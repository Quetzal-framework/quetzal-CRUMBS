from osgeo import gdal
import numpy as np
from optparse import OptionParser
import random

parser = OptionParser()
parser.add_option("--raster", type="str", dest="raster", help="path to raster file")
(options, args) = parser.parse_args()

raster = gdal.Open(options.raster, gdal.GA_ReadOnly)
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
print(lonlat)
