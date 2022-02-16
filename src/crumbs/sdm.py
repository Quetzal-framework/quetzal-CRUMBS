# Daniel Furman, https://daniel-furman.github.io/Python-species-distribution-modeling/

def present_geopanda(pa):
    print("- number of duplicates: ", pa.duplicated(subset='geometry', keep='first').sum())
    print("- number of NA's: ", pa['geometry'].isna().sum())
    print("- coordinate reference system: {}".format(pa.crs))
    print("- {} observations with {} columns".format(*pa.shape))

def to_geopanda_dataframe(shapefile):
    """ Read presence points from a shapefile and adds a CLASS = 1 for observation status (1 for observed, 0 for absent)
    """
    import geopandas as gpd
    gdf = gpd.GeoDataFrame.from_file(shapefile)
    gdf.insert(0, 'CLASS', 1, True )
    return gdf


def spatial_plot(x, title, cmap="Blues"):
    from pylab import plt
    plt.imshow(x, cmap=cmap, interpolation='nearest')
    plt.colorbar()
    plt.title(title, fontweight = 'bold')

def read_spatial_features():
    import shutil
    import glob
    # grab climate features - cropped to joshua tree study area
    for f in sorted(glob.glob('data/bioclim/bclim*.asc')):
        shutil.copy(f,'inputs/')
    raster_features = sorted(glob.glob('inputs/bclim*.asc'))
    # check number of features
    print('\nThere are', len(raster_features), 'raster features.')
    from pyimpute import load_training_vector
    from pyimpute import load_targets
    train_xs, train_y = load_training_vector(pa, raster_features, response_field='CLASS')
    target_xs, raster_info = load_targets(raster_features)
    train_xs.shape, train_y.shape # check shape, does it match the size above of the observations?

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

def fit_models(train_xs, train_y):
    from pyimpute import impute
    from sklearn import model_selection
    class_map = get_ML_classifiers()
    # model fitting and spatial range prediction
    for model_name, (model) in class_map.items():

        # k-fold cross validation for accuracy scores (displayed as a percentage)
        k = 5
        kf = model_selection.KFold(n_splits=k)
        accuracy_scores = model_selection.cross_val_score(model, train_xs, train_y, cv=kf, scoring='accuracy')
        print(
            model_name + " %d-fold Cross Validation Accuracy: %0.2f (+/- %0.2f)"
            % (k, accuracy_scores.mean() * 100, accuracy_scores.std() * 200)
            )

        # spatial prediction
        model.fit(train_xs, train_y)
        os.mkdir('outputs/' + model_name + '-images')
        impute(target_xs, model, raster_info, outdir='outputs/' + model_name + '-images', class_prob=True, certainty=True)

def plot_model_average():
    import rasterio
    distr_rf = rasterio.open("outputs/rf-images/probability_1.0.tif").read(1)
    distr_et = rasterio.open("outputs/et-images/probability_1.0.tif").read(1)
    distr_xgb =  rasterio.open("outputs/xgb-images/probability_1.0.tif").read(1)
    distr_lgbm =  rasterio.open("outputs/lgbm-images/probability_1.0.tif").read(1)
    distr_averaged = (distr_rf + distr_et + distr_xgb + distr_lgbm)/4
    spatial_plot(distr_averaged, "Joshua Tree Range, averaged", cmap="Greens")

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

def species_distribution_model(presence_shp, variables):
    import get_chelsa
    import sample
    import rasterio
    import matplotlib.pyplot as plt
    import geopandas
    import pandas

    # Presence data
    presence = to_geopanda_dataframe(presence_shp)

    # Generate pseudo-absence
    get_chelsa.get_chelsa(variables = variables, timesID = [20], points = presence_shp)
    pseudo_absence = sample_background("stacked_dem.tif", 3000)
    print(pseudo_absence.sample(5))

    # Presence-absence
    pa = pandas.concat([presence, pseudo_absence],  axis=0, ignore_index=True, join="inner")
    present_geopanda(pa)
    print(pa.sample(10))

    fig = plt.figure()
    ax = fig.gca()
    pa[pa.CLASS == 1].plot(marker='*', color='green', markersize=8, ax=ax)
    pa[pa.CLASS == 0].plot(marker='+', color='black', markersize=4, ax=ax)
    plt.show()
    # Define the known data points or "training" data
    # explanatory_fields = fields.split()
    # explanatory_rasters = [os.path.join(TRAINING_DIR, "current_" + r + ".img") for r in explanatory_fields]
    # response_shapes = os.path.join(TRAINING_DIR, "DF.shp")

def main(argv):
    from optparse import OptionParser
    import get_chelsa
    print("- Quetzal-CRUMBS - Species Distribution Models for iDDC modeling")
    parser = OptionParser()

    parser.add_option("-p", "--presence", type="str", dest="presence_points", help="Presence points shapefile.")

    parser.add_option("-v", "--variables",
                        dest="variables",
                        type='str',
                        action='callback',
                        callback=get_chelsa.get_variables_args,
                        help="Comma-separated list of explanatory variables from CHELSA. Possible options: dem, glz, bio01 to bio19 or bio for all.")

    (options, args) = parser.parse_args(argv)
    return species_distribution_model(
        presence_shp = options.presence_points,
        variables = options.variables
        )

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
