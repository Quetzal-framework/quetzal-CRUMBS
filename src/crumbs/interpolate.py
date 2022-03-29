#!/usr/bin/python
from optparse import OptionParser

def unpacking_apply_along_axis(all_args):
    """
    Like numpy.apply_along_axis(), but with arguments in a tuple
    instead.

    This function is useful with multiprocessing.Pool().map(): (1)
    map() only handles functions that take a single argument, and (2)
    this function can generally be imported from a module, as required
    by map().
    """
    (func1d, axis, arr, args, kwargs) = all_args
    return func1d, axis, arr, args, kwargs


def parallel_apply_along_axis(func1d, axis, arr, *args, **kwargs):
    """
    Like numpy.apply_along_axis(), but takes advantage of multiple
    cores.
    """
    import multiprocessing
    import numpy as np
    import numpy.ma as ma
    # Effective axis where apply_along_axis() will be applied by each
    # worker (any non-zero axis number would work, so as to allow the use
    # of `np.array_split()`, which is only done on axis 0):
    effective_axis = 1 if axis == 0 else axis
    if effective_axis != axis:
        arr = arr.swapaxes(axis, effective_axis)

    print('        -', multiprocessing.cpu_count(), 'CPUS available, using', multiprocessing.cpu_count()-1)

    # Chunks for the mapping (only a few chunks):
    chunks = [(func1d, effective_axis, sub_arr, args, kwargs)
              for sub_arr in np.array_split(arr, multiprocessing.cpu_count()-1)]

    print(chunks)
    pool = multiprocessing.Pool()
    individual_results = pool.map(unpacking_apply_along_axis, chunks)
    print(individual_results)
    # Freeing the workers:
    pool.close()
    pool.join()
    print(individual_results)

    return ma.concatenate(individual_results)

def convert_size(size_bytes):
    import math
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def masked_interpolation(data, x, xp, *args, **kwargs):
    import math
    import numpy as np
    import dask
    import dask.array as da
    # The x-coordinates (missing times) at which to evaluate the interpolated values.
    assert len(x) >= 1
    print('x',x)
    # The x-coordinates (existing times) of the data points (where returns a tuple because each element of the tuple refers to a dimension.)
    assert len(xp) >= 2
    assert np.all(np.diff(xp) > 0) , 'Sequence of yearsBP must be increasing'
    print('xp',xp)
    # The y-coordinates (value at existing times) of the data points, that is the valid entrie
    print('data',data)
    fp = np.take(data, xp)
    assert len(fp) >= 2
    print('fp',fp)

    # Returns the one-dimensional piecewise linear interpolant to a function with given discrete data points (xp, fp), evaluated at x.
    new_y = np.interp(x, xp, fp.filled(np.nan))
    np.nan_to_num(new_y, copy=False)

    # interpolate mask & apply to interpolated data
    new_mask = data.mask[:]
    new_mask[new_mask]  = 1
    new_mask[~new_mask] = 0
    # the mask y values at existing times
    new_fp = np.take(new_mask, xp)
    new_mask = np.interp(x, xp, new_fp)
    new_y = da.ma.masked_array(new_y, new_mask > 0.5)

    data[x] = new_y
    return data


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


def make_dash_array(shape, known_array, band_to_yearBP):
    import dask
    import dask.array as da
    import numpy as np
    chunk_shape = (8, shape[1], shape[2])
    new_array = np.zeros(shape)
    # Filling the data shape with existing bands
    i = 0
    for yearBP in band_to_yearBP:
        new_array[yearBP,:,:] = known_array[i]
        print("        - band ", i, "assigned to year BP ", yearBP)
        i += 1
    return da.from_array(new_array, chunks=chunk_shape)


def temporal_interpolation(inputFile, band_to_yearBP, outputFile=None):
    import numpy as np
    import dask
    import dask.array as da
    from dask.dataframe.utils import make_meta
    from dask_rasterio import read_raster, write_raster

    outputFile = 'interpolated.tif' if outputFile is None else outputFile

    import rasterio
    with rasterio.open(inputFile) as source:

        print('    ... reading multiband raster', source.name )
        print('        - number of existing bands is', source.count)
        assert source.count > 1, "Need at least 2 bands in raster to interpolate."
        print('        - bands will be macthed against (in years BP):', band_to_yearBP)
        assert source.count==len(band_to_yearBP), 'Incorrect number of existing bands, or incorrect mapping {band number -> year BP}.'
        assert np.all(np.diff(band_to_yearBP) > 0) , 'Incorrect mapping: sequence of yearsBP must be strictly increasing.'
        print('        - number of missing bands is', number_of_missing_bands(band_to_yearBP))

        # this is a 3D numpy array, with dimensions [band, row, col]
        src_array = source.read(masked=True)
        new_shape = (band_to_yearBP[-1]+1, src_array.shape[1], src_array.shape[2])

        # Predicting requested memory
        size_bytes = new_shape[0]*new_shape[1]*new_shape[2] * src_array.itemsize
        print('        - memory allocation request would be: ', convert_size(size_bytes))

        print('    ... creating dash array')
        big_array = make_dash_array(new_shape, src_array, band_to_yearBP)
        print(big_array)
        big_array.visualize()

        print('    ... interpolating missing bands')
        missing_years, known_years = missing_years_known_years(band_to_yearBP)
        interpolated = da.apply_along_axis(func1d=masked_interpolation,
                                           axis=0,
                                           arr=big_array,
                                           shape=make_meta(big_array).shape,
                                           dtype=make_meta(big_array).dtype,
                                           x=missing_years, xp=known_years)

        # Writing the new raster
        new_meta = source.meta
        new_meta.update({'count' : new_shape[0], 'nodata' : source.nodata  })

        assert interpolated.dtype == src_array.dtype
        assert interpolated.shape == (new_meta['count'], new_meta['height'], new_meta['width'])

        # with rasterio.open(outputFile, "w", **new_meta) as dst:
        #     dst.write(interpolated.filled(fill_value=source.nodata))

        filled = interpolated.filled(fill_value=source.nodata)
        write_raster('processed_image.tif', filled, **new_meta)
        filled.visualize()
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
