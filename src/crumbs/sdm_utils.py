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
    plt.savefig('presences-pseudo-absences.png')


def spatial_plot(x, title, timeID, cmap="Blues"):
    from pylab import plt
    plt.imshow(x, cmap=cmap)
    plt.colorbar()
    plt.title(title + ', ' + str(timeID), fontweight = 'bold')
    plt.savefig('averaged-species-range' + str(timeID) + '.png')


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
