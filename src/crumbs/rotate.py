#!/usr/bin/python
from optparse import OptionParser
import rasterio
from affine import Affine  # For easly manipulation of affine matrix
import scipy.ndimage
from rasterio.plot import reshape_as_raster, reshape_as_image
import numpy as np
from matplotlib import pyplot


def get_center(dataset):
    """This function return the pixel coordinates of the raster center
    """
    # The convention for the transform array as used by GDAL (T0) is to reference the pixel corner
    T0 = dataset.affine
    # We want to instead reference the pixel centre, so it needs to be translated by 50%:
    T1 = T0 * Affine.translation(0.5, 0.5)
    # to transform from pixel coordinates to world coordinates, multiply the coordinates with the matrix
    rc2xy = lambda r, c: T1 * (c, r)
    return rc2xy(0, 1)


def rotate_geotransform(affine_matrix, angle, pivot):
    """This function generate a rotated affine matrix
    """
    affine_dst = affine_matrix * affine_matrix.rotation(angle, pivot)
    return(affine_dst)


def rotate(inputRaster, angle, outputRaster=None):
    outputRaster = 'rotated.TIF' if outputRaster is None else outputRaster

    src_dataset = rasterio.open(inputRaster)
    # this is a 3D numpy array, with dimensions [band, row, col]
    Z = src_dataset.read()

    # raster rotation
    old_affine_matrix = src_dataset.transform
    pivot = get_center(src_dataset)
    new_affine_matrix = rotate_geotransform(old_affine_matrix, angle, pivot)

    # array rotation
    rotated_Z = scipy.ndimage.rotate(Z, angle, order=1, reshape=False, axes=(1,2), cval=np.nan)
    print(Z.shape)
    pyplot.imshow(reshape_as_image(Z))
    pyplot.show()
    gt = src_dataset.transform
    print(gt)
    pixelSizeX = gt[0]
    pixelSizeY =-gt[4]
    print(pixelSizeX)
    print(pixelSizeY)

    print(rotated_Z.shape)
    pyplot.imshow(reshape_as_image(rotated_Z))
    pyplot.show()

    new_dataset = rasterio.open(
        outputRaster,
        'w',
        driver='GTiff',
        height=rotated_Z.shape[1],
        width=rotated_Z.shape[2],
        count=rotated_Z.shape[0],
        dtype=Z.dtype,
        crs=src_dataset.crs,
        transform=new_affine_matrix
    )
    gt = new_dataset.transform
    print(gt)
    pixelSizeX = gt[0]
    pixelSizeY =-gt[4]
    print(pixelSizeX)
    print(pixelSizeY)
    new_dataset.write(rotated_Z)
    new_dataset.close()


def main(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="Rotated output raster name")
    (options, args) = parser.parse_args(argv)
    return rotate(args[0], float(args[1]), options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
