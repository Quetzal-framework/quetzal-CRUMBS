#!/usr/bin/python

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
    plt.imshow(x, cmap=cmap)
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
        'xgb': (XGBClassifier(verbosity = 0)),
        'lgbm': (LGBMClassifier())
        }
    return class_map

def fit_models(train_xs, train_y, target_xs, raster_info, outdir):
    """ Models fitting and spatial range prediction
    """
    import warnings
    with warnings.catch_warnings():

        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)

        from pyimpute import impute
        from sklearn import model_selection
        from pathlib import Path

        class_map = get_ML_classifiers()
        output_images = []

        for model_name, (model) in class_map.items():
            print('    ...', 'Classifier', model_name)

            print('        - k-fold cross validation for accuracy scores (displayed as a percentage)')
            k = 5
            kf = model_selection.KFold(n_splits=k)
            accuracy_scores = model_selection.cross_val_score(model, train_xs, train_y, cv=kf, scoring='accuracy')
            print('        - ' +
                model_name + " %d-fold Cross Validation Accuracy: %0.2f (+/- %0.2f)"
                % (k, accuracy_scores.mean() * 100, accuracy_scores.std() * 200)
                )

            print('        - fitting model ... ')
            model.fit(train_xs, train_y)

        return output_images, class_map

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

def ocean_cells_to_nodata(demRaster, rasters):
    import rasterio
    import numpy as np
    from matplotlib import pyplot

    with rasterio.open(demRaster) as dem:
        Z_dem = dem.read(1, masked=True)

        for raster in rasters:
            meta = None

            with rasterio.open(raster, 'r') as src:
                Z = src.read(1)
                meta = src.meta.copy()

            masked_img = np.ma.masked_where(np.ma.getmask(Z_dem), Z)

            meta.update(fill_value = dem.nodata)
            meta.update({'nodata' : dem.nodata})
            with rasterio.open(raster, "w", **meta) as dst:
                dst.nodata = dem.nodata
                dst.write(masked_img.filled(fill_value=dem.nodata), 1)

def species_distribution_model(presence_shp, variables, timesID, cleanup, background_points=1000, margin=0.0, output='suitability.tif'):
    # Inspire by Daniel Furman, https://daniel-furman.github.io/Python-species-distribution-modeling/
    from . import get_chelsa
    from . import sample
    import rasterio
    import geopandas as gpd
    import pandas as pd
    from pathlib import Path
    import glob
    import os

    output = os.path.splitext(output)[0]

    current_dir = str(Path().resolve())

    world_dir  = 'CHELSA_world'
    in_dir     = 'sdm_inputs'
    out_dir    = 'sdm_outputs'
    average_dir    = 'averaged'
    stack_dir = in_dir + '/' + 'CHELSA_multiband'
    crop_dir   = in_dir + '/' + 'CHELSA_cropped'

    Path(current_dir + '/' + world_dir).mkdir(parents=True, exist_ok=True)
    Path(current_dir + '/' + in_dir).mkdir(parents=True, exist_ok=True)
    Path(current_dir + '/' + out_dir).mkdir(parents=True, exist_ok=True)
    Path(current_dir + '/' + stack_dir).mkdir(parents=True, exist_ok=True)
    Path(current_dir + '/' + crop_dir).mkdir(parents=True, exist_ok=True)
    Path(current_dir + '/' + out_dir + '/' + average_dir).mkdir(parents=True, exist_ok=True)

    print('    - CHELSA raw world files will be saved to  ' , current_dir + '/' + world_dir)
    print('    - CHELSA cropped files will be saved to    ' , current_dir + '/' + crop_dir)
    print('    - CHELSA multibands files will be saved to ' , current_dir + '/' + stack_dir)
    print('    - SDM inputs will be saved to              ' , current_dir + '/' + in_dir)
    print('    - SDM output will be saved to              ' , current_dir + '/' + out_dir)

    # We need DEM for marine/terrestial filter
    v = set(variables); v.add('dem')
    variables = list(v)
    t = set(timesID); t.add('20')
    timesID = list(t)

    get_chelsa.get_chelsa(
        inputFile=None,
        variables=variables,
        timesID=timesID,
        points=presence_shp,
        margin=margin,
        chelsa_dir=world_dir,
        clip_dir=crop_dir,
        geotiff=stack_dir + '/' + 'multiband.tif',
        cleanup=cleanup)

    current_elevation_file =  crop_dir + '/' + 'CHELSA_TraCE21k_dem_20_V1.0.tif'

    # Presence data
    print('    ... reading occurrence:')
    presence = to_geopanda_dataframe(presence_shp)
    present_geopanda(presence)

    print('    ... after removing duplicated occurrences:')
    presence.drop_duplicates(subset='geometry', inplace=True)
    present_geopanda(presence)

    print('    ... after removing occurrences falling in ocean cells (NA, -inf, +inf):')
    presence = drop_ocean_cells(presence, current_elevation_file)
    present_geopanda(presence)

    # Generate pseudo-absence
    pseudo_absence = sample_background(current_elevation_file, background_points)

    # Presence-absence
    pa = pd.concat([presence, pseudo_absence],  axis=0, ignore_index=True, join="inner")
    print('    ... building presence/absence dataset:')
    present_geopanda(pa)
    pa = pa.reset_index()
    plot(pa)

    explanatory_rasters = sorted(glob.glob(crop_dir + '/*_20_*.tif'))
    print('    ... there are', len(explanatory_rasters), 'explanatory rasters features')

    print('    ... masking ocean cells to dem nodata value for all explanatory rasters')
    ocean_cells_to_nodata(current_elevation_file, explanatory_rasters)

    from pyimpute import load_training_vector
    from pyimpute import load_targets

    print('    ... loading training vector')
    train_xs, train_y = load_training_vector(pa, explanatory_rasters, response_field='CLASS')

    print('    ... loading explanatory rasters')
    target_xs, raster_info = load_targets(explanatory_rasters)

    # check shape, does it match the size above of the observations?
    assert train_xs.shape[0] == train_y.shape[0]

    proba_rasters, models_map = fit_models(train_xs, train_y, target_xs, raster_info, out_dir)

    print('    ... projection to current and past climates')
    raster_list = []
    for t in timesID:
        print('    ... projection to time ' + str(t))
        new_explanatory_rasters = sorted(glob.glob(crop_dir + '/*_' + str(t) +'_*.tif'))
        new_elevation_file =  crop_dir + '/' + 'CHELSA_TraCE21k_dem_' + str(t) + '_V1.0.tif'

        print('        - loading target explanatory raster data')
        target_xs, raster_info = load_targets(new_explanatory_rasters)

        output_images = []
        for model_name, (model) in models_map.items():
            print("        - Classifier", model_name)
            from pyimpute import impute
            out = out_dir + '/' + model_name + '/' + str(t)
            impute(target_xs, model, raster_info, outdir=out, linechunk=400, class_prob=True, certainty=True)
            img = out  +'/' + 'probability_1.tif'
            output_images.append(img)

        print('    ... masking ocean cells to dem no data value for all probability_1 rasters')
        ocean_cells_to_nodata(new_elevation_file, output_images)

        print('    ... averaging models for climate conditions at CHELSA time', t)
        imgs = [ rasterio.open(r).read(1, masked=True) for r in output_images]
        averaged_img = sum(imgs)/len(imgs)
        spatial_plot(averaged_img, "Species range, averaged", cmap='viridis')
        dst_raster = out_dir + '/' + average_dir + '/' + output + '_' + str(t) + '.tif'
        raster_list.append(dst_raster)
        with rasterio.open(output_images[0]) as mask:
            meta = mask.meta.copy()
            with rasterio.open(dst_raster, "w", **meta) as dst:
                dst.write(averaged_img, 1)

    VRT = get_chelsa.to_vrt(get_chelsa.sort_nicely(raster_list), out_dir + '/' + output + ".vrt"  )
    get_chelsa.to_geotiff(VRT,  out_dir + '/' + output + ".tif")

def main(argv):
    from optparse import OptionParser
    from . import get_chelsa
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

    parser.add_option("-t", "--timesID",
                        dest="timesID",
                        type='str',
                        action='callback',
                        callback=get_chelsa.get_timesID_args,
                        help="CHELSA_TraCE21k_ times IDs to download for projection to past climates. Default: 20 (present) to -200 (LGM)")
    parser.add_option("-m", "--margin", type="float", dest="margin", default=0.0, help="Margin to add around the bounding box, in degrees.")
    parser.add_option("--cleanup", dest="cleanup", default = False, action = 'store_true', help="Remove downloaded CHELSA world files, but keep clipped files.")
    parser.add_option("--no-cleanup", dest="cleanup", action = 'store_false', help="Keep downloaded CHELSA files on disk.")
    parser.add_option("-o", "--output", type="str", dest="output", help="Output suitability geotiff name.")
    (options, args) = parser.parse_args(argv)
    return species_distribution_model(
        presence_shp = options.presence_points,
        variables = options.variables,
        timesID = options.timesID,
        background_points = options.background_points,
        margin = options.margin,
        cleanup = options.cleanup
        )

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
