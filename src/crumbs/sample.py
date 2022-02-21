#!/usr/bin/python
import os.path
import sys
import random

def uniform_integer(min, max):
    print(random.randint(int(min), int(max)))

def uniform_real(min, max):
    print(random.uniform(float(min), float(max)))

from osgeo import gdal
import numpy as np

def uniform_latlon_above_minimum(raster_path):
    from os.path import exists
    assert exists(path_to_file), 'File doest not exists:' + raster_path

    raster = gdal.Open(raster_path, gdal.GA_ReadOnly)
    band = raster.GetRasterBand(1)
    array = band.ReadAsArray().astype(float)
    (y_index, x_index) = np.nonzero(array >= band.GetMinimum())
    (upper_left_x, x_size, x_rotation, upper_left_y, y_rotation, y_size) = raster.GetGeoTransform()
    x_coords = x_index * x_size + upper_left_x + (x_size / 2) #add half the cell size
    y_coords = y_index * y_size + upper_left_y + (y_size / 2) #to centre the point
    assert (x_coords.size == y_coords.size)
    i = random.randint(0, x_coords.size -1)
    latlon = list()
    latlon.append(y_coords[i])
    latlon.append(x_coords[i])
    return latlon

def uniform_latlon(raster_path):
    print(uniform_latlon_above_minimum(raster_path))

commands = {
    'uniform_integer': uniform_integer,
    'uniform_real': uniform_real,
    'uniform_latlon': uniform_latlon
}

if __name__ == '__main__':
    import sys
    command = os.path.basename(sys.argv[1])
    if command in commands:
        commands[command](*sys.argv[2:])
