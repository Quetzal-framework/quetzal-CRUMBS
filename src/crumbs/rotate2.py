#!/usr/bin/python
from optparse import OptionParser
import rasterio
from affine import Affine  # For easly manipulation of affine matrix
from rasterio.warp import reproject, Resampling
import numpy as np

def summary(dataset):
    print(" - no data value:", dataset.nodata )
    print(" - transform:\n")
    print(dataset.transform, "\n")
    print(" - ", dataset.bounds, "\n")
    pxsz, pysz = dataset.res
    print(" - pixel size X: \t", pxsz, "unit:", dataset.crs.linear_units)
    print(" - pixel size Y: \t", pysz, "unit:", dataset.crs.linear_units)
    return

def get_center(dataset):
    """This function return the pixel coordinates of the raster center
    """
    width, height = dataset.width, dataset.height
    # We calculate the middle of raster
    x_pixel_med = width // 2
    y_pixel_med = height // 2
    # The convention for the transform array as used by GDAL (T0) is to reference the pixel corner
    T0 = dataset.transform
    # We want to instead reference the pixel centre, so it needs to be translated by 50%:
    T1 = T0 * Affine.translation(0.5, 0.5)
    # to transform from pixel coordinates to world coordinates, multiply the coordinates with the matrix
    rc2xy = lambda r, c: T1 * (c, r)
    # get the coordinates for a raster in the first row, second column (index [0, 1]):
    return rc2xy(y_pixel_med, x_pixel_med)

def rotate(inputRaster, angle, scale=1, outputRaster=None):
    outputRaster = 'rotated.tif' if outputRaster is None else outputRaster

    ### Read input
    source = rasterio.open(inputRaster)
    assert source.crs == 'EPSG:4326', "Raster must have CRS=EPSG:4326, that is unprojected lon/lat (degree) relative to WGS84 datum"

    # Display information
    print("\nSource dataset:\n")
    summary(source)

    ### Rotate the affine
    pivot = get_center(source)
    print("\nPivot coordinates:", pivot)
    new_transform = source.transform * Affine.rotation(angle, pivot) * Affine.scale(scale)

    # this is a 3D numpy array, with dimensions [band, row, col]
    data = source.read(masked=True)
    kwargs = source.meta
    kwargs['transform'] = new_transform

    with rasterio.open(outputRaster, 'w', **kwargs) as dst:
        for i in range(1, source.count + 1):
            reproject(
                source=rasterio.band(source, i),
                destination=rasterio.band(dst, i),
                src_transform=source.transform,
                src_crs=source.crs,
                dst_transform=new_transform,
                dst_crs=dst.crs,
                resampling=Resampling.average)

        # Display information
        print("\nNew rotated dataset:\n")
        summary(dst)

    return

def main(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="Rotated output raster name")
    (options, args) = parser.parse_args(argv)
    return rotate(args[0], float(args[1]), float(args[2]), options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
