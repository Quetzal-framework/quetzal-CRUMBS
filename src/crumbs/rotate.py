#!/usr/bin/python
from optparse import OptionParser
from osgeo import gdal  # For read and manipulate rasters
from affine import Affine  # For easly manipulation of affine matrix
import numpy as np
import matplotlib.pyplot as plot

def raster_center(raster):
    """This function return the pixel coordinates of the raster center
    """

    # We get the size (in pixels) of the raster using gdal
    width, height = raster.RasterXSize, raster.RasterYSize

    # We calculate the middle of raster
    xmed = width / 2
    ymed = height / 2

    return (xmed, ymed)


def rotate_gt(affine_matrix, angle, pivot=None):
    """This function generate a rotated affine matrix
    """
    affine_src = Affine.from_gdal(*affine_matrix)

    affine_dst = affine_src * affine_src.rotation(angle, pivot)

    # Return the rotated matrix in gdal format
    return affine_dst.to_gdal()


def rotate(inputRaster, angle, outputRaster=None):

    outputRaster = 'rotated.tif' if outputRaster is None else outputRaster

    dataset_src = gdal.Open(inputRaster)

    driver = gdal.GetDriverByName("GTiff")

    dataset_dst = driver.CreateCopy(outputRaster, dataset_src, strict=0)

    # First step, get the affine tranformation matrix of the initial file
    gt_affine = dataset_src.GetGeoTransform()

    # Second get the center of the raster to set the rotation center
    # Be carefull, the center is in pixel number, not in projected coordinates
    center = raster_center(dataset_src)

    # Third we rotate the destination raster, datase_dst, with setting a new
    # affine matrix made by the "rotate_gt" function.
    dataset_dst.SetGeoTransform(rotate_gt(gt_affine, angle, center))
    array = dataset_dst.GetRasterBand(1).ReadAsAray()
    plt.imshow(array)
    plt.colorbar()
    plt.show()


def main(argv):
    parser = OptionParser()
    parser.add_option("-i", "--input", type="str", dest="input", help="Geotiff multiband file")
    parser.add_option("-o", "--output", type="str", dest="output", help="Rotated output raster name")
    parser.add_option("-a", "--angle", type="float", dest="angle", help="rotation angle between 0 and 360")
    (options, args) = parser.parse_args(argv)
    return rotate(options.input, options.angle, options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
