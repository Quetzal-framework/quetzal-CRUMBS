#!/usr/bin/python
from optparse import OptionParser
import rasterio
from matplotlib import pyplot

def show_raster(inputRaster):

    source = rasterio.open(inputRaster)
    pyplot.imshow(source.read(1), cmap='viridis')
    pyplot.show()

def main(argv):
    parser = OptionParser()
    (options, args) = parser.parse_args(argv)
    return show_raster(args[0])

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
