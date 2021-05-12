from osgeo import gdal
import numpy as np
import random
import argparse

def random_lonlat(raster_path):
    raster = gdal.Open(raster_path, gdal.GA_ReadOnly)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray().astype(float)
    (y_index, x_index) = np.nonzero(array >= band.GetMinimum())
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = raster.GetGeoTransform()
    x_coords = x_index * x_size + upper_left_x + (x_size / 2) #add half the cell size
    y_coords = y_index * y_size + upper_left_y + (y_size / 2) #to centre the point
    assert (x_coords.size == y_coords.size)
    i = random.randint(0, x_coords.size -1)
    lonlat = list()
    lonlat.append(x_coords[i])
    lonlat.append(y_coords[i])
    return lonlat

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sample value-defined lon/lats cells uniformely at random')
    parser.add_argument('raster_path', help="path to raster file")
    args = parser.parse_args()
    print(random_lonlat(args.raster_path))
