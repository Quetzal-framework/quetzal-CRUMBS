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
        new_width = int(source.width // scale)
        new_height =  int(source.height // scale)

        # Update metadata
        kwargs = source.meta.copy()
        kwargs.update({
            'count': source.count,
            'width': new_width,
            'height': new_height,
            'transform': new_transform,
            'nodata': source.nodata,
            'crs': source.crs
            })

        # Source data: use normal array because mask won't work with reproject
        src_data = source.read()
        source_type = src_data.dtype;
        src_data=src_data.astype('float64')
        src_data[src_data == source.nodata] = np.nan

        # Array to store destination data
        dst_shape=[source.count, new_height, new_width]
        dst_data = np.empty(dst_shape); dst_data[:] = np.nan

        with rasterio.open(outputRaster, mode='w', **kwargs) as dst:

            for i in range(1, source.count + 1):
                # Reproject from array to array
                reproject(
                    source=src_data[i-1],
                    destination=dst_data[i-1],
                    src_transform=source.transform,
                    src_crs=source.crs,
                    dst_transform=new_transform,
                    dst_crs=dst.crs,
                    resampling=Resampling.average,
                    dst_nodata=np.nan
                    )

            dst_data[np.isnan(dst_data)] = source.nodata
            dst_data=dst_data.astype(source_type)
            # Write to the output file
            dst.write(dst_data, indexes=range(1, source.count + 1))
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
