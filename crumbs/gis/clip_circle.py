#!/usr/bin/python

import rasterio
import rasterio.mask

from math import cos, sin, asin, sqrt, radians

from shapely.ops import transform
from shapely.geometry import Point, Polygon

import pyproj
from functools import partial


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
    """
    Draws a circle (buffer) around the center coordinates
    """
    # Azimuthal equidistant projection
    aeqd_proj = '+proj=aeqd +lat_0={lat} +lon_0={lon} +x_0=0 +y_0=0'
    proj_wgs84 = pyproj.Proj('+proj=longlat +datum=WGS84')
    project = partial(
        pyproj.transform,
        pyproj.Proj(aeqd_proj.format(lat=lat, lon=lon)),
        proj_wgs84)
    buf = Point(0, 0).buffer(km * 1000)  # distance in metres
    return transform(project, buf).exterior.coords[:]


def clip_circle(inputFile, outputFile=None):
    """
    Writes an output raster file after clipping a circle on the input raster.
    """
    outputFile = 'disk.tif' if outputFile is None else outputFile

    with rasterio.open(inputFile) as source:

        # Center in pixel coordinates
        c = source.width // 2
        r = source.height // 2

        # Center in real world coordinates
        rc2xy = lambda r, c: source.transform * (c, r)
        x, y = rc2xy(r,c)

        # Getting minimal distance border to fit the circle
        bounds = source.bounds
        d_width = calc_distance(bounds.bottom, bounds.left, bounds.bottom, bounds.right)
        d_height = calc_distance(bounds.bottom, bounds.left, bounds.top, bounds.left)

        # Draw a circle (buffer) around the center coordinates
        b = geodesic_point_buffer(y, x, km=min(d_width, d_height)/2)
        out_image, out_transform = rasterio.mask.mask(source, [Polygon(b)], crop=True, pad=True)
        out_meta = source.meta

    with rasterio.open(outputFile, "w", **out_meta) as dest:
        dest.write(out_image)

    return
