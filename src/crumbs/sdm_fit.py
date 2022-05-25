#!/usr/bin/python

from typing import List, Set, Dict, Tuple, Optional

def fit_models(train_xs, train_y, target_xs, raster_info, outdir, persist=True):
    """ Models fitting and spatial range prediction
    """
    from . import sdm_utils

    import warnings
    with warnings.catch_warnings():

        warnings.filterwarnings("ignore", category=UserWarning)
        warnings.filterwarnings("ignore", category=FutureWarning)

        from pyimpute import impute
        from sklearn import model_selection
        from pathlib import Path

        class_map = sdm_utils.get_ML_classifiers()
        imputed_images = []

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

            if persist is True:
                filename = 'persist' + model_name + '.joblib'
                print('        - trained model will be saved to', filename)
                from joblib import dump
                dump(model, filename)

        return imputed_images, class_map


def fit_species_distribution_model(
    presence_shp: str,
    variables: List[str],
    timeID: float = 20,
    persist: bool = False,
    cleanup: bool = True,
    crop_dir: str = None,
    background_points: str = None,
    margin: float = 0.0,
    output: str = 'suitability.tif') -> None:

    # Inspire by Daniel Furman, https://daniel-furman.github.io/Python-species-distribution-modeling/
    from . import get_chelsa
    from . import sample
    from . import sdm_utils

    import rasterio
    import geopandas as gpd
    import pandas as pd
    import glob
    import os

    from pyimpute import impute
    from pathlib import Path

    import numpy as np

    output = os.path.splitext(output)[0]

    current_dir = str(Path().resolve())

    world_dir      = 'CHELSA_world'
    in_dir         = 'sdm_inputs'
    out_dir        = 'sdm_outputs'
    average_dir    = 'averaged'
    stack_dir      = in_dir + '/' + 'CHELSA_multiband'

    if crop_dir is None:
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

    get_chelsa.get_chelsa(
        inputFile=None,
        variables=variables,
        timesID=[timeID],
        points=presence_shp,
        margin=margin,
        chelsa_dir=world_dir,
        clip_dir=crop_dir,
        geotiff=stack_dir + '/' + 'multiband.tif',
        cleanup=cleanup)

    current_elevation_file =  crop_dir + '/' + 'CHELSA_TraCE21k_dem_20_V1.0.tif'

    # Presence data
    print('    ... reading occurrence:')
    presence = sdm_utils.to_geopanda_dataframe(presence_shp)
    sdm_utils.present_geopanda(presence)

    print('    ... after removing duplicated occurrences:')
    presence.drop_duplicates(subset='geometry', inplace=True)
    sdm_utils.present_geopanda(presence)

    print('    ... after removing occurrences falling in ocean cells (NA, -inf, +inf):')
    presence = sdm_utils.drop_ocean_cells(presence, current_elevation_file)
    sdm_utils.present_geopanda(presence)

    # Generate pseudo-absence
    pseudo_absence = sdm_utils.sample_background(current_elevation_file, background_points)

    # Presence-absence
    pa = pd.concat([presence, pseudo_absence],  axis=0, ignore_index=True, join="inner")
    print('    ... building presence/absence dataset:')
    sdm_utils.present_geopanda(pa)
    pa = pa.reset_index()
    sdm_utils.plot(pa)

    explanatory_rasters = sorted(glob.glob(crop_dir + '/*_20_*.tif'))
    print('    ... there are', len(explanatory_rasters), 'explanatory rasters features')

    print('    ... masking ocean cells to dem nodata value for all explanatory rasters')
    sdm_utils.ocean_cells_to_nodata(current_elevation_file, explanatory_rasters)

    from pyimpute import load_training_vector
    from pyimpute import load_targets

    print('    ... loading training vector')
    train_xs, train_y = load_training_vector(pa, explanatory_rasters, response_field='CLASS')

    print('    ... loading explanatory rasters')
    target_xs, raster_info = load_targets(explanatory_rasters)

    # check shape, does it match the size above of the observations?
    assert train_xs.shape[0] == train_y.shape[0]

    print('    ... fittin models on training data')
    proba_rasters, models_map = fit_models(train_xs, train_y, target_xs, raster_info, out_dir, persist)

    print('    ... projection to current climate (timeID=', timeID, ')')

    print('    ... projection to time ' + str(timeID))
    new_explanatory_rasters = sorted(glob.glob(crop_dir + '/*_' + str(timeID) +'_*.tif'))
    new_elevation_file =  crop_dir + '/' + 'CHELSA_TraCE21k_dem_' + str(timeID) + '_V1.0.tif'

    print('        - loading target explanatory raster data')
    target_xs, raster_info = load_targets(new_explanatory_rasters)

    imputed_images = []

    for model_name, (model) in models_map.items():
        print("        - Classifier", model_name)
        dir = out_dir + '/' + model_name + '/' + str(timeID)
        imputed = dir  +'/' + 'probability_1.tif'
        impute(target_xs, model, raster_info, outdir=dir, linechunk=400, class_prob=True, certainty=True)
        imputed_images.append(imputed)

    print('    ... masking ocean cells to dem no data value for all probability_1 rasters')
    sdm_utils.ocean_cells_to_nodata(new_elevation_file, imputed_images)

    print('    ... averaging models for climate conditions at CHELSA time', timeID)
    imgs = [ rasterio.open(r).read(1, masked=True) for r in imputed_images]
    import numpy.ma as ma
    averaged = ma.array(imgs).mean(axis=0)

    dst_raster = out_dir + '/' + average_dir + '/' + output + '_' + str(timeID) + '.tif'

    with rasterio.open(imputed_images[0]) as mask:
        meta = mask.meta.copy()
        with rasterio.open(dst_raster, "w", **meta) as dst:
            dst.write(averaged.filled(fill_value=mask.nodata), 1)


def main(argv):

    from optparse import OptionParser
    from . import get_chelsa

    print("- Quetzal-CRUMBS - Species Distribution Models for iDDC modeling")

    parser = OptionParser()

    parser.add_option("-p", "--presence",
                        type="str",
                        dest="presence_points",
                        help="Presence points shapefile.")

    parser.add_option("-b", "--background",
                        type="int",
                        default=None,
                        dest="background_points",
                        help="Number of backgound points to sample for pseudo-absences generation")

    parser.add_option("-t", "--timeID",
                        dest="timeID",
                        type='float',
                        default=20,
                        help="CHELSA_TraCE21k_ time ID to download present covariates. Default: 20 (present)")

    parser.add_option("-v", "--variables",
                        dest="variables",
                        type='str',
                        action='callback',
                        callback=get_chelsa.get_variables_args,
                        help="Comma-separated list of explanatory variables from CHELSA. Possible options: dem, glz, bio01 to bio19 or bio for all.")

    parser.add_option("-m", "--margin",
                        type="float",
                        dest="margin",
                        default=0.0,
                        help="Margin to add around the bounding box, in degrees.")

    parser.add_option("-o", "--output",
                        type="str",
                        dest="output",
                        default="suitability.tif",
                        help="Output suitability geotiff name.")

    parser.add_option("--persist",
                        dest="persist",
                        default = True,
                        action = 'store_true',
                        help="After training a scikit-learn model, persist the model for future use without having to retrain.")

    parser.add_option("--no-persist",
                        dest="persist",
                        action = 'store_false',
                        help="After training a scikit-learn model, the model is lost.")

    parser.add_option("--cleanup",
                        dest="cleanup",
                        default = True,
                        action = 'store_true',
                        help="Remove downloaded CHELSA world files, but keep clipped files.")

    parser.add_option("--no-cleanup",
                        dest="cleanup",
                        action = 'store_false',
                        help="Keep downloaded CHELSA world files on disk.")

    parser.add_option("-c", "--clip_dir",
                        type="str",
                        dest="clip_dir",
                        default = "CHELSA_cropped",
                        help="Output directory for clipped CHELSA files. Default: CHELSA_cropped.")

    (options, args) = parser.parse_args(argv)

    return fit_species_distribution_model(
        presence_shp = options.presence_points,
        background_points = options.background_points,
        timeID = options.timeID,
        variables = options.variables,
        margin = options.margin,
        output = options.output,
        persist = options.persist,
        cleanup = options.cleanup,
        clip_dir = options.clip_dir
        )

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
