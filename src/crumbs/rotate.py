#!/usr/bin/python
from optparse import OptionParser
from osgeo import gdal, osr  # For read and manipulate rasters
from affine import Affine  # For easly manipulation of affine matrix
import numpy as np
import scipy.ndimage
from matplotlib import pyplot

def get_center(raster):
    """This function return the pixel coordinates of the raster center
    """
    # We get the size (in pixels) of the raster using gdal
    width, height = raster.RasterXSize, raster.RasterYSize
    # We calculate the middle of raster
    xmed = width / 2
    ymed = height / 2
    return (xmed, ymed)


def rotate_geotransform(affine_matrix, angle, pivot):
    """This function generate a rotated affine matrix
    """
    affine_src = Affine.from_gdal(*affine_matrix)
    affine_dst = affine_src * affine_src.rotation(angle, pivot)
    # Return the rotated matrix in gdal format
    return affine_dst.to_gdal()


def rotate(inputRaster, angle, outputRaster=None):
    outputRaster = 'rotated.TIF' if outputRaster is None else outputRaster

    dataset_src = gdal.Open(inputRaster)
    src_arr = dataset_src.GetRasterBand(1).ReadAsArray()

    rotated_arr = scipy.ndimage.rotate(src_arr, angle, order=1, reshape=True)
    rotated_arr = scipy.ndimage.rotate(src_arr, angle, order=1, reshape=True)
    pyplot.imshow(rotated_arr)
    pyplot.show()
    dst_arr = rotated_arr.reshape(src_arr.shape)
    pyplot.imshow(dst_arr)
    pyplot.show()

    driver = gdal.GetDriverByName("GTiff")
    dataset_dst = driver.CreateCopy(outputRaster, dataset_src, strict=0)
    # First step, get the affine tranformation matrix of the initial file
    old_affine_matrix = dataset_src.GetGeoTransform()
    pivot = get_center(dataset_src)
    # Rotate the raster by setting a new affine matrix made by the "rotate_gt" function.
    new_affine_matrix = rotate_geotransform(old_affine_matrix, angle, pivot)
    dataset_dst.SetGeoTransform(new_affine_matrix)
    # setting spatial reference of output raster
    prj = dataset_src.GetProjection()
    srs = osr.SpatialReference(wkt = prj)
    dataset_dst.SetProjection( srs.ExportToWkt() )

    dst_band = dataset_dst.GetRasterBand(1)
    dst_band.WriteArray(rotated_arr)
    dataset_dst.FlushCache() ##saves to disk!!

def main(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="Rotated output raster name")
    (options, args) = parser.parse_args(argv)
    return rotate(args[0], float(args[1]), options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
