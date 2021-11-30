#!/usr/bin/python
from optparse import OptionParser

import rasterio.plot
from rasterio.plot import show_hist

from matplotlib import pyplot
import imageio
from tqdm import tqdm
import numpy

def get_global_max(source):

    array = source.read()
    # mask off no data values
    m = (array != source.nodata)
    return array[m].max()


def animate(inputRaster, vmax, output='animation.gif'):

    source = rasterio.open(inputRaster)

    if vmax is None:
        vmax = get_global_max(source)

    with imageio.get_writer(output, mode='I') as writer:

        for bandId in tqdm(range(source.count)):

            bandId = bandId+1
            band = source.read(bandId, masked=True)

            fig, ax = pyplot.subplots()

            # to get longitude/latitude axis
            extent = numpy.asarray(source.bounds)[[0,2,1,3]]

            # use imshow so that we have something to map the colorbar to
            image_hidden = ax.imshow(band,
                                     extent=extent,
                                     cmap='viridis',
                                     vmin=0,
                                     vmax=vmax)

            # plot on the same axis with rio.plot.show
            image = rasterio.plot.show(band,
                                  transform=source.transform,
                                  ax=ax,
                                  cmap='viridis',
                                  vmin=0,
                                  vmax=vmax)

            # add colorbar using the now hidden image
            fig.colorbar(image_hidden, ax=ax)

            pyplot.savefig("layer.png", bbox_inches='tight')
            pyplot.close()

            image = imageio.imread('layer.png')
            writer.append_data(image)

def main(argv):
    parser = OptionParser()
    parser.add_option("-i", "--input", type="str", dest="input", help="Geotiff multiband file")
    parser.add_option("-o", "--output", type="str", dest="output", help="output animation name")
    parser.add_option("-m", "--vmax", type="int", dest="vmax", help="max value in color scale")
    (options, args) = parser.parse_args(argv)
    return animate(options.input, options.vmax, options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
