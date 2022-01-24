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

def get_center_pixel(dataset):
    """This function return the pixel coordinates of the raster center
    """
    width, height = dataset.width, dataset.height
    # We calculate the middle of raster
    x_pixel_med = width // 2
    y_pixel_med = height // 2
    return (x_pixel_med, y_pixel_med)

def rotate_and_rescale(inputRaster, angle, scale=1, outputRaster=None):
    outputRaster = 'rotated.tif' if outputRaster is None else outputRaster

    ### Read input
    with rasterio.open(inputRaster) as source:
        assert source.crs == 'EPSG:4326', "Raster must have CRS=EPSG:4326, that is unprojected lon/lat (degree) relative to WGS84 datum"

        # Display information
        print("- Source dataset:")
        summary(source)

        ### Rotate the affine about a pivot and rescale
        pivot = get_center_pixel(source)
        print("\nPivot coordinates:", source.transform * pivot)

        # Apply transformation
        new_transform = source.transform*Affine.rotation(angle, pivot) * Affine.scale(scale)

        # this is a 3D numpy array, with dimensions [band, row, col]
        data = source.read(masked=True)
        kwargs = source.meta.copy()
        kwargs.update({
            'crs': source.crs,
            'transform': new_transform,
            'width': int(source.width // scale),
            'height': int(source.height // scale)
            })

        with rasterio.open(outputRaster, 'w', **kwargs) as dst:
            for i in range(1, source.count + 1):
                reproject(
                    source=rasterio.band(source, i),
                    destination=rasterio.band(dst, i),
                    src_transform=source.transform,
                    src_crs=source.crs,
                    dst_transform=new_transform,
                    dst_crs=dst.crs,
                    resampling=Resampling.average
                    )

        # Display information
        print("- New rotated dataset:")
        summary(dst)

    return

def main(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="Rotated output raster name")
    (options, args) = parser.parse_args(argv)
    return rotate_and_rescale(args[0], float(args[1]), float(args[2]), options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
