#!/usr/bin/python
from optparse import OptionParser

def convert_size(size_bytes):
    import math
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])

def fast_interp(z):
    # see https://stackoverflow.com/a/52699059/10360134
    # fast interpolator that use the regular grid structure (x and y are 1D arrays)
    z = z_masked.filled(np.nan)
    from scipy.interpolate import RegularGridInterpolator
    zinterp = RegularGridInterpolator((x, y), z.T)

    # new grid to interpolate on
    X2, Y2 = np.meshgrid(x2, y2)
    newpoints = np.array((X2, Y2)).T

    # actual interpolation
    z2 = zinterp(newpoints)
    z2_masked = np.ma.array(z2, mask=np.isnan(z2))


def pad(data):
    import numpy as np
    good = np.isfinite(data)
    interpolated = np.interp(x = np.arange(data.shape[0]),
                             xp = np.flatnonzero(good),
                             fp = data[good])
    return interpolated


def masked_interpolation(data, x, xp, propagate_mask=True):
    import math
    import numpy as np
    import numpy.ma as ma

    # The x-coordinates (missing times) at which to evaluate the interpolated values.
    #x = np.where(data.mask == False)[0]
    assert len(x) >= 1

    # The x-coordinates (existing times) of the data points (where returns a tuple because each element of the tuple refers to a dimension.)
    #xp = np.where(data.mask == True)[0]
    assert len(xp) >= 2

    # The y-coordinates (value at existing times) of the data points, that is the valid entries
    fp = np.take(data, xp)
    assert len(fp) >= 2

    # Returns the one-dimensional piecewise linear interpolant to a function with given discrete data points (xp, fp), evaluated at x.
    new_y = np.interp(x, xp, fp.filled(np.nan))

    # interpolate mask & apply to interpolated data
    if propagate_mask:
        new_mask = data.mask[:]
        new_mask[new_mask]  = 1
        new_mask[~new_mask] = 0
        # the mask y values at existing times
        new_fp = np.take(new_mask, xp)
        new_mask = np.interp(x, xp, new_fp)
        new_y = np.ma.masked_array(new_y, new_mask > 0.5)

    return new_y

def temporal_interpolation(inputFile, band_to_yearBP, outputFile=None):
    import numpy as np
    import numpy.ma as ma

    outputFile = 'interpolated.tif' if outputFile is None else outputFile

    import rasterio
    with rasterio.open(inputFile) as source:
        print('    ... reading multiband raster ' + inputFile)
        print('        - number of existing bands is', source.count)
        assert source.count > 1, "Need at least 2 bands in raster to interpolate."
        print('        - bands will be macthed against (in years BP):', band_to_yearBP)
        assert source.count==len(band_to_yearBP), 'incorrect number of existing bands, or incorrect mapping {band number -> year BP}.'

        sum = 0
        for i in range(len(band_to_yearBP) - 1):
            left = band_to_yearBP[i]
            right = band_to_yearBP[i+1]
            sum += right - left - 1

        print('        - number of missing bands is', sum)

        # this is a 3D numpy array, with dimensions [band, row, col]
        src_data = source.read(masked=True)
        src_shape = src_data.shape
        last_yearBP = band_to_yearBP[-1]

        print('    ... creating new array')

        # Building a fully masked 3D array
        dst_shape = (last_yearBP + 1, src_shape[1], src_shape[2])
        dst_data = ma.zeros(dst_shape)
        #dst_data = np.full(dst_shape, np.nan)
        size_bytes = dst_data.size * dst_data.itemsize
        print('        - memory allocation needed is ', convert_size(size_bytes))

        # Filling the data shape with existing bands
        i = 0
        for yearBP in band_to_yearBP:
            dst_data[yearBP] = src_data[i]
            print("        - band ", i, "assigned to year BP ", yearBP)
            i += 1

        # Interpolating the missing bands
        start = band_to_yearBP[0]
        end = band_to_yearBP[-1] + 1
        step = 1
        known_years = set(band_to_yearBP)
        all_years = set(range(start, end, step))
        missing_years = all_years - known_years
        new = ma.apply_along_axis(func1d=masked_interpolation, axis=0, arr=dst_data, x=list(missing_years), xp=list(known_years))

        # Writing the new raster
        meta = source.meta
        meta.update({'count' : dst_shape[0] })
        meta.update({'nodata' : source.nodata})
        meta.update(fill_value = source.nodata)
        print(new.shape)
        print(meta)
        assert new.shape == (meta['count'],meta['height'],meta['width'])
        with rasterio.open(outputFile, "w", **meta) as dst:
            dst.write(new.filled(fill_value=source.nodata))

    return

def get_times_args(option, opt, value, parser, type='float'):
    setattr(parser.values, option.dest, [int(s) for s in value.split(',')])

def main(argv):
    parser = OptionParser()

    print("- Quetzal-CRUMBS - Temporal interpolation for missing layers")

    parser.add_option("-t", "--timesID",
                        dest="generations",
                        type='str',
                        action='callback',
                        callback=get_times_args,
                        help="Comma separated sequence mapping band layers to years before present. Example for a 3 band raster: 0,500,1000.")

    parser.add_option("-o", "--output", type="str", dest="output", help="Cliped output raster name")

    (options, args) = parser.parse_args(argv)

    return temporal_interpolation(
        inputFile = args[0],
        band_to_yearBP = options.generations,
        outputFile = options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
