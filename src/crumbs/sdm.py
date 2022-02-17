#!/usr/bin/python

def present_geopanda(gdf):
    print("        - number of duplicates: ", gdf.duplicated(subset='geometry', keep='first').sum())
    print("        - number of NA's: ", gdf['geometry'].isna().sum())
    print("        - coordinate reference system: {}".format(gdf.crs))
    print("        - {} observations with {} columns".format(*gdf.shape))


def to_geopanda_dataframe(shapefile):
    """ Read presence points from a shapefile and adds a CLASS = 1 for observation status (1 for observed, 0 for absent)
    """
    import geopandas as gpd
    gdf = gpd.GeoDataFrame.from_file(shapefile)
    gdf.insert(0, 'CLASS', 1, True)
    return gdf


def random_sample_from_masked_array(masked, nb_sample):
    """ Sample indices uniformely at random in a masked array, ignoring masked values.
        Returns a tuple (idx,idy)
    """
    import numpy as np
     #Assign False = 0, True = 1
    weights =~ masked.mask + 0
    normalized = weights.ravel()/float(weights.sum())
    index = np.random.choice(
        masked.size,
        size=nb_sample,
        replace=False,
        p=normalized
    )
    idy, idx = np.unravel_index(index, masked.shape)
    return idx, idy


def sample_background(demRaster, nb_sample=30):
    """ If presence-only data are given (e.g., from GBIF) then some form of absence points is needed.
        Random background points are sampled uniformely at random from contemporary DEM band.
        Returns a geopandas dataframe, with a CLASS column filled with 0 values (absence)
    """
    import rasterio
    import geopandas
    with rasterio.open(demRaster) as src:
        Z = src.read(1, masked=True)
        cols, rows = random_sample_from_masked_array(Z, nb_sample)
        xs, ys = rasterio.transform.xy(src.transform, rows, cols)
        geometry=geopandas.points_from_xy(xs, ys, crs=src.crs)
        d = {'CLASS': [0]*len(xs), 'geometry': geometry}
        gdf = geopandas.GeoDataFrame(d, crs=src.crs)
        return gdf


def plot(pa):
    """ Plot presences and absences on top of each others.
    """
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.gca()
    pa[pa.CLASS == 1].plot(marker='*', color='green', markersize=8, ax=ax)
    pa[pa.CLASS == 0].plot(marker='+', color='black', markersize=2, ax=ax)
    plt.show()


def spatial_plot(x, title, cmap="Blues"):
    from pylab import plt
    plt.imshow(x, cmap=cmap, interpolation='nearest')
    plt.colorbar()
    plt.title(title, fontweight = 'bold')
    plt.show()

def get_ML_classifiers():
    """ Imports a bunch of machine learning classifiers
    """
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.ensemble import ExtraTreesClassifier
    from xgboost import XGBClassifier
    from lightgbm import LGBMClassifier
    class_map = {
        'rf': (RandomForestClassifier()),
        'et': (ExtraTreesClassifier()),
        'xgb': (XGBClassifier()),
        'lgbm': (LGBMClassifier())
        }
    return class_map

def fit_models(train_xs, train_y, target_xs, raster_info):

    from pyimpute import impute
    from sklearn import model_selection

    import os
    os.mkdir("outputs")
    # import classifiers
    class_map = get_ML_classifiers()

    # model fitting and spatial range prediction
    for model_name, (model) in class_map.items():

        # k-fold cross validation for accuracy scores (displayed as a percentage)
        k = 5
        kf = model_selection.KFold(n_splits=k)
        accuracy_scores = model_selection.cross_val_score(model, train_xs, train_y, cv=kf, scoring='accuracy', error_score='raise')
        print(
            model_name + " %d-fold Cross Validation Accuracy: %0.2f (+/- %0.2f)"
            % (k, accuracy_scores.mean() * 100, accuracy_scores.std() * 200)
            )

        # spatial prediction
        model.fit(train_xs, train_y)
        os.mkdir('outputs/' + model_name + '-images')
        impute(target_xs, model, raster_info, outdir='outputs/' + model_name + '-images', class_prob=True, certainty=True)


def drop_ocean_cells(gdf, rasterFile):
    import rasterio
    import numpy as np
    with rasterio.open(rasterFile) as src:
        coord_list = [(x,y) for x,y in zip(gdf['geometry'].x , gdf['geometry'].y)]
        gdf['value'] = [x for x in src.sample(coord_list)]
        gdf.dropna(inplace=True, axis=0)
        #gdf = gdf[np.isfinite(gdf.value)]
        gdf = gdf.loc[gdf['value'] >= 0.0].copy()
        gdf.drop(labels='value', axis=1, inplace=True)
        gdf.reset_index(inplace=True)
    return gdf

def clean_dataset(df):
    import geopandas as gpd
    import numpy as np
    assert isinstance(df, gpd.GeoDataFrame), "df needs to be a gpd.GeoDataFrame"
    df.dropna(inplace=True)
    indices_to_keep = ~df.isin([np.nan, np.inf, -np.inf]).any(1)
    return df[indices_to_keep].astype(np.float64)

# def check_transform(rasters):
#     import rasterio
#     transform = None
#     previous_raster = None
#     previous_transform = None
#     for raster in rasters:
#         with rasterio.open(raster) as src:
#             # First iteration, fransform is None
#             if transform is None:
#                 transform = src.transform
#             else:
#                 if transform != src.transform:
#                     if transform.almost_equals(src.transform):
#                         meta = src.meta.copy()
#                         meta.update({'transform' : src.transform})
#                     print(raster + ' and ' + previous + 'have different transforms: ')
#                     print(previous, ':\n', transform)
#                     print(raster, ':\n', src.transform)
#         previous_raster = raster
#         previous_transform = transform

def species_distribution_model(presence_shp, variables, background_points=1000):
    # Inspire by Daniel Furman, https://daniel-furman.github.io/Python-species-distribution-modeling/
    import get_chelsa
    import sample
    import rasterio
    import geopandas as gpd
    import pandas as pd

    from pathlib import Path
    current_dir = str(Path().resolve())
    Path(current_dir + '/' + 'sdm_inputs').mkdir(parents=True, exist_ok=True)
    Path(current_dir + '/' + 'sdm_outputs').mkdir(parents=True, exist_ok=True)

    # We need DEM for marine/terrestial filter
    s = set(variables); s.add('dem')
    variables = list(s)

    get_chelsa.get_chelsa(
        inputFile=None,
        variables=variables,
        timesID=[20],
        points=presence_shp,
        margin=0.0,
        chelsa_dir='CHELSA_world',
        clip_dir='CHELSA_cropped',
        geotiff=current_dir + '/' + 'sdm_inputs/chelsa_20.tif',
        cleanup=False)

    elevation_file =  current_dir + '/' + "sdm_inputs/chelsa_20_dem.tif"

    # Presence data
    print('    ... reading occurrence:')
    presence = to_geopanda_dataframe(presence_shp)
    present_geopanda(presence)

    print('    ... after removing duplicates:')
    presence.drop_duplicates(subset='geometry', inplace=True)
    present_geopanda(presence)

    print('    ... after removing ocean (NA, -inf, +inf) cells:')
    presence = drop_ocean_cells(presence, elevation_file)
    present_geopanda(presence)

    # Generate pseudo-absence
    pseudo_absence = sample_background(elevation_file, background_points)

    # Presence-absence
    pa = pd.concat([presence, pseudo_absence],  axis=0, ignore_index=True, join="inner")
    print('    ... building presence/absence dataset:')
    present_geopanda(pa)
    pa = pa.reset_index()
    plot(pa)
    #pa = clean_dataset(pa)

    import glob
    explanatory_rasters = sorted(glob.glob('sdm_inputs/*.tif'))
    print('    ... there are', len(explanatory_rasters), 'raster features:')
    #check_transform(explanatory_rasters)

    from pyimpute import load_training_vector
    from pyimpute import load_targets

    response_data = pa
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        train_xs, train_y = load_training_vector(response_data, explanatory_rasters, response_field='CLASS')
        target_xs, raster_info = load_targets(explanatory_rasters)

    print(train_xs.shape, train_y.shape) # check shape, does it match the size above of the observations?

    fit_models(train_xs, train_y, target_xs, raster_info)

    distr_rf = rasterio.open("outputs/rf-images/probability_1.tif").read(1)
    distr_et = rasterio.open("outputs/et-images/probability_1.tif").read(1)
    distr_xgb =  rasterio.open("outputs/xgb-images/probability_1.tif").read(1)
    distr_lgbm =  rasterio.open("outputs/lgbm-images/probability_1.tif").read(1)
    distr_averaged = (distr_rf + distr_et + distr_xgb + distr_lgbm)/4
    spatial_plot(distr_averaged, "Heteronotia binoei range, averaged", cmap='viridis')

def main(argv):
    from optparse import OptionParser
    import get_chelsa
    print("- Quetzal-CRUMBS - Species Distribution Models for iDDC modeling")
    parser = OptionParser()

    parser.add_option("-p", "--presence", type="str", dest="presence_points", help="Presence points shapefile.")

    parser.add_option("-b", "--background", type="int", default=1000, dest="background_points", help="Number of backgound points.")

    parser.add_option("-v", "--variables",
                        dest="variables",
                        type='str',
                        action='callback',
                        callback=get_chelsa.get_variables_args,
                        help="Comma-separated list of explanatory variables from CHELSA. Possible options: dem, glz, bio01 to bio19 or bio for all.")

    (options, args) = parser.parse_args(argv)
    return species_distribution_model(
        presence_shp = options.presence_points,
        variables = options.variables,
        background_points = options.background_points
        )

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
