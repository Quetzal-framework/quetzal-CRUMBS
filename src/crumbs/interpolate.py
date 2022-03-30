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


def test_preconditions(data, x, xp):
    import numpy as np
    # The x-coordinates (missing times) at which to evaluate the interpolated values.
    assert len(x) >= 1
    # The x-coordinates (existing times) of the data points (where returns a tuple because each element of the tuple refers to a dimension.)
    assert len(xp) >= 2
    assert np.all(np.diff(xp) > 0) , 'Sequence of yearsBP must be increasing'


def unmasked_interpolation(data, x, xp):
    import numpy as np

    test_preconditions(data, x, xp)

    fp = np.take(data, xp)
    assert len(fp) >= 2

    # Returns the one-dimensional piecewise linear interpolant to a function with given discrete data points (xp, fp), evaluated at x.
    new_y = np.interp(x, xp, fp)
    np.nan_to_num(new_y, copy=False)
    data[x] = new_y

    return data


def mask_interpolation(mask, x, xp):
    import numpy as np

    test_preconditions(mask, x, xp)
    mask[mask]  = 1
    mask[~mask] = 0

    # the mask y values at existing times
    fp = np.take(mask, xp)
    assert len(fp) >= 2

    new_y = np.interp(x, xp, fp)
    mask[x] = new_y
    return mask > 0.5


def missing_years_known_years(band_to_yearBP):
    assert all(band_to_yearBP[i] <= band_to_yearBP[i+1] for i in range(len(band_to_yearBP) - 1))
    start = band_to_yearBP[0]
    end = band_to_yearBP[-1] + 1
    step = 1
    known_years = set(band_to_yearBP)
    all_years = set(range(start, end, step))
    missing_years = all_years - known_years
    return sorted(missing_years), sorted(known_years)


def number_of_missing_bands(band_to_yearBP):
    assert all(band_to_yearBP[i] <= band_to_yearBP[i+1] for i in range(len(band_to_yearBP) - 1))
    sum = 0
    for i in range(len(band_to_yearBP) - 1):
        left = band_to_yearBP[i]
        right = band_to_yearBP[i+1]
        sum += right - left - 1
    return sum


def make_masked_array(shape, known_ma_array, band_to_yearBP):
    import numpy as np
    import numpy.ma as ma
    ma_array = ma.zeros(shape, dtype=known_ma_array.dtype)
    #Filling the data shape with existing bands
    i = 0
    for yearBP in band_to_yearBP:
        ma_array[yearBP,:,:] = known_ma_array[i]
        print("        - band ", i, "assigned to year BP ", yearBP)
        i += 1
    return ma_array


def temporal_interpolation(inputFile, band_to_yearBP, outputFile=None):
    import numpy as np
    import dask
    import dask.array as da
    import rasterio
    from dask.diagnostics import ProgressBar
    import xarray as xr
    import rioxarray
    import threading

    outputFile = 'interpolated.tif' if outputFile is None else outputFile

    with rasterio.open(inputFile) as source:
        print('    ... reading multiband raster', source.name )
        print('        - number of existing bands is', source.count)
        assert source.count > 1, "Need at least 2 bands in raster to interpolate."
        print('        - bands will be macthed against (in years BP):', band_to_yearBP)
        assert source.count==len(band_to_yearBP), 'Incorrect number of existing bands, or incorrect mapping {band number -> year BP}.'
        assert np.all(np.diff(band_to_yearBP) > 0) , 'Incorrect mapping: sequence of yearsBP must be strictly increasing.'
        print('        - number of missing bands is', number_of_missing_bands(band_to_yearBP))

        # chaunks is provided & lock is False: ensure that reading and operating on your data happen in parallel.
        x_array = rioxarray.open_rasterio(inputFile, masked=True, chunks = (1,'auto','auto'), lock=False)
        # Create a view
        src_array = x_array.to_masked_array(copy=False)
        # src_array = source.read(masked=True)
        new_shape = (band_to_yearBP[-1]+1, src_array.shape[1], src_array.shape[2])

        # Predicting requested memory
        # size_bytes = new_shape[0]*new_shape[1]*new_shape[2] * src_array.itemsize
        # print('        - memory allocation request would be: ', convert_size(size_bytes))

        print('    ... creating new array')
        ma_arr = make_masked_array(new_shape, src_array, band_to_yearBP)

        print('    ... interpolating missing bands')
        missing_years, known_years = missing_years_known_years(band_to_yearBP)

        da_ma_arr = da.from_array(ma_arr, chunks=(1,10000,10000))

        arr_interpolated = da.apply_along_axis(func1d=unmasked_interpolation,
                                           axis=0,
                                           arr=da.ma.filled(da_ma_arr, np.nan),
                                           shape=(da_ma_arr.shape[0],),
                                           dtype=da_ma_arr.dtype,
                                           x=missing_years,
                                           xp=known_years)

        mask_interpolated = da.apply_along_axis(func1d=mask_interpolation,
                                           axis=0,
                                           arr=ma_arr.mask,
                                           shape=(da_ma_arr.shape[0],),
                                           dtype=da_ma_arr.dtype,
                                           x=missing_years,
                                           xp=known_years)

        interpolated = da.ma.masked_array(arr_interpolated, mask_interpolated)
        filled = da.ma.filled(interpolated, fill_value=source.nodata)

        # Writing the new raster
        new_meta = source.meta
        new_meta.update({'count' : new_shape[0], 'nodata' : source.nodata  })

        assert filled.dtype == src_array.dtype
        assert filled.shape == (new_meta['count'], new_meta['height'], new_meta['width'])

        ProgressBar().register()
        result = xr.DataArray(filled, dims=["band", "y", "x"])
        result.rio.write_crs(x_array.rio.crs, inplace=True)
        result.rio.write_nodata(source.nodata, inplace=True, encoded=True)
        result.rio.to_raster(outputFile, lock=threading.Lock())

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
