"""
Module declaring the base class for Species Distribution Modeling.
"""

class SDM:
    """
    Species Distribution Model: use presence points (from GBIF) to infer pseudo-absences
    and fit classifiers, saving fitted models for later extrapolations to past time periods
    with dHTC.
    """

    from typing import List, Set, Dict, Tuple, Optional

    def __init__(
    self,
    scientific_name: str,
    presence_shapefile: str,
    nb_background_points: float = 30,
    variables = ['bio'],
    buffer: float = 0.0,
    cleanup: bool = True
    ):
        """
        Species Distribution Model constuctor
        """

        self.scientific_name    = scientific_name
        self.presence_shapefile = presence_shapefile
        self.nb_background_points  = nb_background_points
        self.variables          = variables
        self.buffer             = buffer
        self.cleanup            = cleanup

        # File system
        self.world_dir          = 'chelsa-world'
        self.landscape_dir      = 'chelsa-landscape'
        self.joblib_dir         = 'model-persistence'
        self.impute_dir         = 'model-imputation'
        self.model_average_dir  = 'model-averaging'
        self.present_time_DEM =  self.landscape_dir + '/' + 'CHELSA_TraCE21k_dem_20_V1.0.tif'

        # We need to download Digital Elevation Model for marine/terrestial filter
        v = set(self.variables)
        v.add('dem')
        self.variables = list(v)

    def _get_ML_classifiers(self):
        """
        Imports a bunch of machine learning classifiers
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

    def _train_and_save_classifiers(self,train_xs, train_y, target_xs, raster_info):
        """
        Fitting classifiers from target data
        """

        from sklearn import model_selection
        from joblib import dump
        from pathlib import Path

        import warnings
        with warnings.catch_warnings():

            warnings.filterwarnings("ignore", category=UserWarning)
            warnings.filterwarnings("ignore", category=FutureWarning)

            class_map = self._get_ML_classifiers()

            for model_name, (model) in class_map.items():
                print('    ...', 'Classifier', model_name)

                print('        - k-fold cross validation for accuracy scores (displayed as a percentage)')

                k = 5
                kfold = model_selection.KFold(n_splits=k)
                accuracy_scores = model_selection.cross_val_score(model, train_xs, train_y, cv=kfold, scoring='accuracy')

                print('        - ' +
                model_name + " %d-fold Cross Validation Accuracy: %0.2f (+/- %0.2f)"
                % (k, accuracy_scores.mean() * 100, accuracy_scores.std() * 200)
                )

                print('        - fitting model')
                model.fit(train_xs, train_y)

                print('        - trained model will be saved to', self.joblib_dir + '/' + model_name + '.joblib')
                path = Path(self.joblib_dir + '/')
                path.mkdir(parents=True, exist_ok=True)
                dump(model, self.joblib_dir + '/' + model_name + '.joblib')

        return None

    def _random_sample_from_masked_array(self, masked, nb_sample):
        """
        Sample indices uniformely at random in a masked array, ignoring masked values.
        Returns a tuple (idx,idy)
        """
        import numpy as np

        #Assign False = 0, True = 1
        weights =~ masked.mask + 0
        normalized = weights.ravel()/float(weights.sum())
        index = np.random.choice(masked.size, size=nb_sample, replace=False, p=normalized)
        idy, idx = np.unravel_index(index, masked.shape)

        return idx, idy

    def _present_geopanda(self, gdf) -> None :
        print("        - number of duplicates: ", gdf.duplicated(subset='geometry', keep='first').sum())
        print("        - number of NA's: ", gdf['geometry'].isna().sum())
        print("        - coordinate reference system: {}".format(gdf.crs))
        print("        - {} observations with {} columns".format(*gdf.shape))
        return None

    def _to_geopanda_dataframe(self, shapefile) :
        """ Read presence points from a shapefile and adds a CLASS = 1 for observation status (1 for observed, 0 for absent)
        """
        import geopandas as gpd
        gdf = gpd.GeoDataFrame.from_file(shapefile)
        gdf.insert(0, 'CLASS', 1, True)
        return gdf

    def _sample_background(self, demRaster, nb_sample=30):
        """
        If presence-only data are given (e.g., from GBIF) then some form of absence points is needed.
        Random background points are sampled uniformely at random from contemporary DEM band.
        Returns a geopandas dataframe, with a CLASS column filled with 0 values (absence)
        """

        import rasterio
        import geopandas

        with rasterio.open(demRaster) as src:

            Z = src.read(1, masked=True)

            cols, rows = self._random_sample_from_masked_array(Z, nb_sample)

            xs, ys = rasterio.transform.xy(src.transform, rows, cols)

            geometry=geopandas.points_from_xy(xs, ys, crs=src.crs)

            d = {'CLASS': [0]*len(xs), 'geometry': geometry}

            gdf = geopandas.GeoDataFrame(d, crs = src.crs)

        return gdf

    def _download_chelsa_variables_at_time(self, timeID) -> None :
        """
        Download chelsa datasets in order to fit and extrapolate classifiers
        """

        from crumbs.chelsa.utils import request

        request(
        inputFile   =   None,
        variables   =   self.variables,
        timesID     =   [timeID],
        points      =   self.presence_shapefile,
        margin      =   self.buffer,
        chelsa_dir  =   self.world_dir,
        clip_dir    =   self.landscape_dir,
        geotiff     =   None,
        cleanup     =   self.cleanup )

        return None

    def _spatial_plot(self, x, title, timeID, cmap="Blues") -> None:
        from pylab import plt
        plt.imshow(x, cmap=cmap)
        plt.colorbar()
        plt.title(title + ', ' + str(timeID), fontweight = 'bold')
        plt.savefig('averaged-species-range' + str(timeID) + '.png')
        return None

    def _drop_ocean_cells(self, gdf, rasterFile):
        """
        Drop coordinates of a geopandadataframe that happen to fall in the ocean cells
        of a digital elevation model.
        """
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

    def _read_and_clean_presence_dataset(self):
        """
        Read a presence dataset, drop duplicates and remove points falling in ocean cells
        """
        print('    ... reading presence shapefile datatsets:')
        presences = self._to_geopanda_dataframe(self.presence_shapefile)
        self._present_geopanda(presences)

        print('    ... after removing duplicated occurrences:')
        presences.drop_duplicates(subset='geometry', inplace=True)
        self._present_geopanda(presences)

        print('    ... after removing occurrences falling in ocean cells (NA, -inf, +inf):')
        presences = self._drop_ocean_cells(presences, self.present_time_DEM)
        self._present_geopanda(presences)

        return presences

    def _plot(self, pa, filename : str = "presences-pseudo-absences.png") -> None:
        """
        Plot presences and absences on top of each others.
        """
        import matplotlib.pyplot as plt

        fig = plt.figure()
        ax = fig.gca()

        pa[pa.CLASS == 1].plot(marker='*', color='green', markersize=8, ax=ax)
        pa[pa.CLASS == 0].plot(marker='+', color='black', markersize=2, ax=ax)
        plt.savefig(filename)

        return None

    def _build_presence_absence(self, presence, pseudo_absence, plot=False):
        """
        Concatenate presence and pseudo-absence geopanda dataframes
        """
        import pandas

        pa = pandas.concat([presence, pseudo_absence],  axis=0, ignore_index=True, join="inner")

        print('    ... building presence/absence dataset:')
        self._present_geopanda(pa)

        pa = pa.reset_index()

        if plot is True:
            self._plot(pa)

        return pa

    def _ocean_cells_to_nodata(self, demRaster, rasters) -> None :
        """
        Transfer the notdata values from a Digital Elevation Model raster to a list
        of rasters of similar metadata
        """
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

                    # Avoid WARNING:CPLE_NotSupported in driver GTiff does not support creation option FILL_VALUE
                    # meta.update(fill_value = dem.nodata)
                    meta.update({'nodata' : dem.nodata})

                    with rasterio.open(raster, "w", **meta) as dst:
                        dst.nodata = dem.nodata
                        dst.write(masked_img.filled(fill_value=dem.nodata), 1)

        return None

    def _get_paths_of_explanatory_rasters_at_time(self, timeID):
        """
        Returns paths to all expplanatory rasters and mask their ocean cells using DEM
        """
        from glob import glob
        explanatory_rasters = sorted(glob(self.landscape_dir + '/*_' + str(timeID) +'_*.tif'))
        print('    ... there are', len(explanatory_rasters), 'explanatory rasters features')
        return explanatory_rasters

    def _mask_ocean_cells(self, explanatory_rasters: List[str]) -> None:
        """"
        Mask ocean cells of raster using DEM
        """
        print('    ... masking ocean cells to DEM nodata value for all explanatory rasters')
        self._ocean_cells_to_nodata(self.present_time_DEM, explanatory_rasters)

        return explanatory_rasters

    def _find_digital_elevation_raster(self, timeID):
        return self.landscape_dir + '/' + 'CHELSA_TraCE21k_dem_' + str(timeID) + '_V1.0.tif'

    def _load_classifiers_and_impute(self, timeID, target_xs, raster_info):
        import joblib
        import pyimpute
        class_map = self._get_ML_classifiers()

        imputed_images = []

        for model_name in class_map.keys():

            print("        - loading persisted classifier", model_name)

            model = joblib.load(self.joblib_dir + '/' + model_name + '.joblib')

            outdir = self.impute_dir + '/' + model_name + '/' + str(timeID)

            pyimpute.impute(target_xs, model, raster_info, outdir=outdir, linechunk=400, class_prob=True, certainty=True)

            imputed_images.append(outdir  +'/' + 'probability_1.tif')

        return imputed_images

    def _average_and_save_imputed_rasters(self, timeID, imputed_images) -> None:
        """
        Opens raster images imputed by different classifiers and average
        them, saving the averaged raster.
        """
        import numpy.ma as ma
        import rasterio
        from pathlib import Path

        rasters = [ rasterio.open(r).read(1, masked=True) for r in imputed_images]

        averaged = ma.array(rasters).mean(axis=0)

        path = Path(self.model_average_dir + '/')
        path.mkdir(parents=True, exist_ok=True)

        dst_raster = self.model_average_dir + '/suitability_' + str(timeID) + '.tif'

        with rasterio.open(imputed_images[0]) as mask:

            meta = mask.meta.copy()

            with rasterio.open(dst_raster, "w", **meta) as dst:

                dst.write(averaged.filled(fill_value = mask.nodata), 1)

        return None

    def load_classifiers_and_extrapolate(self, timeID) -> None:
        """
        Load the classifiers from joblib files and project them to present
        and past climates.
        """
        from pyimpute import load_targets

        print("- Quetzal-CRUMBS - Species Distribution Modeling for iDDC modeling")
        print('    ... projection to time ' + str(timeID))

        self._download_chelsa_variables_at_time(timeID)
        explanatory_rasters = self._get_paths_of_explanatory_rasters_at_time(timeID)

        print('        - loading target explanatory raster data')
        target_xs, raster_info = load_targets(explanatory_rasters)

        print('        - loading persisted classifiers and imputing')
        imputed_images = self._load_classifiers_and_impute(timeID, target_xs, raster_info)

        print('    ... masking ocean cells to dem no data value for all probability_1 rasters')
        elevation_file = self._find_digital_elevation_raster(timeID)

        self._ocean_cells_to_nodata(elevation_file, imputed_images)

        print('    ... averaging imputed rasters for climate conditions at CHELSA time', timeID)
        self._average_and_save_imputed_rasters(timeID, imputed_images)

        return None

    def fit_on_present_data(self) -> None:
        """
        Use presences and modern DEM to generate pseudo-absence, then fit the classifiers
        and generate joblib files for model persistence.
        """
        from pyimpute import (
            load_training_vector,
            load_targets
        )

        self._download_chelsa_variables_at_time(timeID=20)

        presence = self._read_and_clean_presence_dataset()

        absence = self._sample_background(self.present_time_DEM, self.nb_background_points)

        presence_absence = self._build_presence_absence(presence, absence, plot=False)

        explanatory_rasters = self._get_paths_of_explanatory_rasters_at_time(timeID=20)

        print('    ... loading training vector')
        train_xs, train_y = load_training_vector(presence_absence, explanatory_rasters, response_field='CLASS')

        print('    ... loading explanatory rasters')
        target_xs, raster_info = load_targets(explanatory_rasters)

        # check shape, does it match the size above of the observations?
        assert train_xs.shape[0] == train_y.shape[0]

        print('    ... fitting classifiers on training data')
        self._train_and_save_classifiers(train_xs, train_y, target_xs, raster_info)

        return None

    # def build_virtual_suitability():
    #     VRT = get_chelsa.to_vrt(get_chelsa.sort_nicely(raster_list), out_dir + '/' + output + ".vrt"  )
    #     get_chelsa.to_geotiff(VRT,  out_dir + '/' + output + ".tif")
