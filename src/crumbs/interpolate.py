#!/usr/bin/python
from optparse import OptionParser
import rasterio
import numpy as np
from scipy.interpolate import RegularGridInterpolator

def pad(data):
    good = np.isfinite(data)
    interpolated = np.interp(np.arange(data.shape[0]),
                             np.flatnonzero(good),
                             data[good])
    return interpolated

def temporal_interpolation(inputFile, band_to_generation, outputFile=None):
    assert band_to_generation[0] == 0, "band_to_generation mapping should begin with 0, mapping the first layer to present generation 0"
    outputFile = 'interpolated.tif' if outputFile is None else outputFile

    with rasterio.open(inputFile) as source:
        assert source.count > 1, "Need at least 2 bands in raster to interpolate."
        # this is a 3D numpy array, with dimensions [band, row, col]
        src_data = source.read(masked=True)
        src_shape = src_data.shape
        last_generation = band_to_generation[-1]
        print(last_generation)
        # Build a nan 3D array
        dst_shape = (last_generation + 1, src_shape[1], src_shape[2])
        dst_data = np.empty(dst_shape)
        dst_data[:] = np.nan

        assert source.count == len(band_to_generation), "Raster should have as many bands as band_to_generation parameter"

        # Filling the data shape
        i = 0
        for input_value in band_to_generation: # g = 0, 9
            dst_data[input_value] = src_data[i]
            print(inputFile,  " - Interpolation : band ", i, "assigned to generation ", input_value)
            i = i + 1

        new = np.apply_along_axis(pad, 0, dst_data)
        out_meta = source.meta
        out_meta.update(count=last_generation+1)

        with rasterio.open(outputFile, "w", **out_meta) as dest:
            dest.write(new)

    return


def main(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="Cliped output raster name")
    (options, args) = parser.parse_args(argv)
    return temporal_interpolation(args[0], [int(x) for x in args[1:]], options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
