#!/usr/bin/python
from optparse import OptionParser
import io
import rasterio.plot
from rasterio.plot import show_hist

from matplotlib import pyplot
import imageio
from tqdm import tqdm
import numpy

def plot1(fig):
    fig.canvas.draw()
    data = numpy.frombuffer(fig.canvas.tostring_rgb(), dtype=numpy.uint8)
    w, h = fig.canvas.get_width_height()
    im = data.reshape((int(h), int(w), -1))
    return(im)


def plot2(fig):
    with io.BytesIO() as buff:
        fig.savefig(buff, format='png')
        buff.seek(0)
        im = plt.imread(buff)
        return(im)


def plot3(fig):
    with io.BytesIO() as buff:
        fig.savefig(buff, format='raw')
        buff.seek(0)
        data = numpy.frombuffer(buff.getvalue(), dtype=numpy.uint8)
    w, h = fig.canvas.get_width_height()
    im = data.reshape((int(h), int(w), -1))
    return(im)


def animate(inputRaster, vmin=None, vmax=None, output=None):
    output = 'animation.gif' if output is None else output

    with rasterio.open(inputRaster) as source:
        source_data = source.read(masked=True)

        if vmax is None: vmax = source_data.max()
        if vmin is None: vmin = source_data.min()

        with imageio.get_writer(output, mode='I') as writer:

            for bandID in tqdm(range(1, source.count + 1)):
                fig, ax = pyplot.subplots()
                # to get longitude/latitude axis
                extent = numpy.asarray(source.bounds)[[0,2,1,3]]
                # use imshow so that we have something to map the colorbar to
                image_hidden = ax.imshow(source_data[bandID-1],
                                         extent=extent,
                                         cmap='viridis',
                                         vmin=vmin,
                                         vmax=vmax)
                image_hidden.set_visible(False)
                # plot on the same axis with rio.plot.show
                image = rasterio.plot.show(source_data[bandID-1],
                                      transform=source.transform,
                                      ax=ax,
                                      cmap='viridis',
                                      vmin=vmin,
                                      vmax=vmax)

                # add colorbar using the now hidden image
                fig.colorbar(image_hidden, ax=ax)

                writer.append_data(plot3(fig))
                pyplot.close()


def main(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="output animation name")
    parser.add_option("-m", "--min", type="float", dest="min", help="min value in color scale")
    parser.add_option("-M", "--max", type="float", dest="max", help="max value in color scale")
    (options, args) = parser.parse_args(argv)
    return animate(args[0], options.min, options.max, options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
