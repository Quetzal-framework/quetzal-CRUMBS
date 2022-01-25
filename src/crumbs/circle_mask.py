#!/usr/bin/python
from optparse import OptionParser
import rasterio
import math
import rasterio.mask

from functools import partial
import pyproj
from shapely.ops import transform
from shapely.geometry import Point, Polygon

proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')

from math import cos, sin, asin, sqrt, radians

def calc_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6371 * c
    return km

def geodesic_point_buffer(lat, lon, km):
    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres
    return transform(project, buf).exterior.coords[:]


def circle_mask(inputFile, outputFile=None):
    outputFile = 'disk.tif' if outputFile is None else outputFile

    with rasterio.open(inputFile) as source:
        c = source.width // 2
        r = source.height // 2
        rc2xy = lambda r, c: source.transform * (c, r)
        x, y = rc2xy(r,c)
        min(source.width*source.res[0], source.height*source.res[1])
        bounds = source.bounds
        d_width = calc_distance(bounds.bottom, bounds.left, bounds.bottom, bounds.right)
        d_height = calc_distance(bounds.bottom, bounds.left, bounds.top, bounds.left)
        print(d_width, d_height)
        b = geodesic_point_buffer(y, x, km=min(d_width, d_height)/2)
        out_image, out_transform = rasterio.mask.mask(source, [Polygon(b)], crop=True)
        out_meta = source.meta

    with rasterio.open(outputFile, "w", **out_meta) as dest:
        dest.write(out_image)

    return


def main(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="Cliped output raster name")
    (options, args) = parser.parse_args(argv)
    return circle_mask(args[0], options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
