#!/usr/bin/python
from optparse import OptionParser
import rasterio
from affine import Affine  # For easly manipulation of affine matrix

def get_center(dataset):
    """This function return the pixel coordinates of the raster center
    """
    # We get the size (in pixels) of the raster using gdal
    #width, height = raster.RasterXSize, raster.RasterYSize
    width, height = dataset.width, dataset.height
    # We calculate the middle of raster
    xmed = width // 2
    ymed = height // 2
    return (xmed, ymed)

def rotate(inputRaster, angle, outputRaster=None):
    outputRaster = 'rotated.tif' if outputRaster is None else outputRaster
    src_dataset = rasterio.open(inputRaster)
    assert src_dataset.crs == 'EPSG:4326', "Raster must have CRS=EPSG:4326, that is unprojected lon/lat (degree) relative to WGS84 datum"
    # Display information
    print("\nSource dataset:\n")
    print(" - crs: ", src_dataset.crs, "\n")
    print(" - transform:\n")
    print(src_dataset.transform, "\n")
    print(" - ", src_dataset.bounds, "\n")
    pxsz, pysz = src_dataset.res
    print(" - pixel size X: ", pxsz, "unit:", src_dataset.crs.linear_units)
    print(" - pixel size Y: ", pysz, "unit:", src_dataset.crs.linear_units)
    # this is a 3D numpy array, with dimensions [band, row, col]
    Z = src_dataset.read()
    center_x, center_y = get_center(src_dataset)
    src_affine = src_dataset.transform
    new_affine = Affine.translation(center_x, center_y) * Affine.rotation(angle) * Affine.scale(pxsz, pysz)
    new_dataset = rasterio.open(
        outputRaster,
        'w',
        driver='GTiff',
        height=src_dataset.height,
        width=src_dataset.width,
        count=src_dataset.count,
        crs=src_dataset.crs,
        dtype=Z.dtype,
        transform=new_affine
    )
    # Display information
    print("\nNew rotated dataset:\n")
    print(" - transform:\n")
    print(new_dataset.transform, "\n")
    print(" - ", new_dataset.bounds, "\n")
    pxsz, pysz = new_dataset.res
    print(" - pixel size X: \t", pxsz, new_dataset.crs.linear_units)
    print(" - pixel size Y: \t", pysz, new_dataset.crs.linear_units)
    # Write dataset
    new_dataset.write(Z)
    # Close datasets
    src_dataset.close()
    new_dataset.close()
    return

def main(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="Rotated output raster name")
    (options, args) = parser.parse_args(argv)
    return rotate(args[0], float(args[1]), options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
