#!/usr/bin/python
from optparse import OptionParser
import rasterio
from rasterio import Affine, MemoryFile
from rasterio.enums import Resampling

def resample_raster(raster, scale, outputRaster):
    t = raster.transform

    # rescale the metadata
    transform = Affine(t.a / scale, t.b, t.c, t.d, t.e / scale, t.f)
    height = int(raster.height * scale)
    width = int(raster.width * scale)

    profile = raster.profile
    profile.update(transform=transform, driver='GTiff', height=height, width=width)

    data = raster.read( # Note changed order of indexes, arrays are band, row, col order not row, col, band
            out_shape=(raster.count, height, width),
            resampling=Resampling.bilinear,
        )

    with rasterio.open(outputRaster, 'w', **profile) as dest_dataset:
        dest_dataset.write(data)

    return dest_dataset


def resample(inputRaster, resample_factor, outputRaster=None):
    """This function changes the resolution of the raster.
       Upsampling refers to cases where we are converting to
       higher resolution/smaller cells (resample_factor >1). Downsampling is resampling to lower
       resolution/larger cellsizes (resample_factor <1).
    """
    outputRaster = 'resampled.tif' if outputRaster is None else outputRaster

    with rasterio.open(inputRaster) as src_dataset:
        resampled_dataset = resample_raster(src_dataset, resample_factor, outputRaster)
        print('Orig dims: {}, New dims: {}'.format(src_dataset.shape, resampled_dataset.shape))

    return
