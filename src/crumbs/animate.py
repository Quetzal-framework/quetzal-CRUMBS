#!/usr/bin/python
from optparse import OptionParser
import rasterio.plot
from rasterio.plot import show_hist
from matplotlib import pyplot
import imageio
from tqdm import tqdm

def animate(inputRaster, output='animation.gif'):

    source = rasterio.open(inputRaster)

    with imageio.get_writer(output, mode='I') as writer:

        for bandId in tqdm(range(source.count)):
            bandId = bandId+1
            band = source.read(bandId, masked=True)

            fig, ax = pyplot.subplots()
            img = rasterio.plot.show(band, cmap='viridis', ax=ax)
            pyplot.savefig("layer.png", bbox_inches='tight')
            pyplot.close()

            image = imageio.imread('layer.png')
            writer.append_data(image)

def main(argv):
    parser = OptionParser()
    parser.add_option("--input", type="str", dest="input", help="Geotiff multiband file")
    parser.add_option("--output", type="str", dest="output", help="output animation name")
    (options, args) = parser.parse_args(argv)
    return animate(options.input, options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
