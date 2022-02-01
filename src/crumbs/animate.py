#!/usr/bin/python
from optparse import OptionParser
import io
import rasterio.plot
from rasterio.plot import show_hist

import imageio
from tqdm import tqdm
import numpy

def get_band(Z, i):
    """ Return the ith band of the (possibly masked) Z 3D array: if masked, fills masked values with nan.
    """
    z = Z[i].astype(float)
    if isinstance(z, numpy.ma.MaskedArray):
        z = z.filled(numpy.nan)  # Set masked values to nan
    return z

from mayavi import mlab

@mlab.animate(delay=10, ui=False)
def update_animation(Z, surface, writer, vmin, vmax, DDD=False):
    f = mlab.gcf()
    t = 2.0
    increment = 0.1 if DDD is True else 1.0
    sequence = numpy.arange(2.0, float(Z.shape[0]), increment)
    for i in tqdm(range(len(sequence))):
        # get the current lut manager
        lut_manager = mlab.colorbar(orientation='vertical')
        surface.module_manager.scalar_lut_manager.use_default_range = False
        surface.module_manager.scalar_lut_manager.data_range = numpy.array([vmin, vmax])
        surface.update_pipeline()
        if(DDD is True):
            f.scene.camera.azimuth(1)
            f.scene.render()
        t += increment

        surface.mlab_source.scalars = get_band(Z, int(t)-1)
        writer.append_data(mlab.screenshot())
        yield

def animate(inputRaster, vmin=None, vmax=None, output=None, gbif=None, DDD=False, warp_scale=1.0):
    output = 'animation.gif' if output is None else output

    with rasterio.open(inputRaster) as source:

        Z = source.read(masked=True)

        nrows, ncols = Z[0].shape
        x = numpy.linspace(source.bounds[0], source.bounds[2], ncols)
        y = numpy.linspace(source.bounds[1], source.bounds[3], nrows)
        X, Y = numpy.meshgrid(x, y)

        if vmax is None: vmax = numpy.amax(Z)
        if vmin is None: vmin = numpy.amin(Z)

        with imageio.get_writer(output, mode='I') as writer:

            if(DDD is False):
                surface = mlab.imshow(get_band(Z, 0), colormap='viridis')
                # view along z axis
                mlab.view(0,0)
            elif(DDD is True):
                surface = mlab.surf(get_band(Z, 0), colormap='viridis', warp_scale=warp_scale)

            # Sets nan pixels to white
            surface.module_manager.scalar_lut_manager.lut.nan_color = 0, 0, 0, 0

            a = update_animation(Z, surface, writer, vmin, vmax, DDD)

            mlab.show()

def main(argv):
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="output animation name")
    parser.add_option("-m", "--min", type="float", default=None, dest="min", help="min value in color scale")
    parser.add_option("-M", "--max", type="float", default=None, dest="max", help="max value in color scale")
    parser.add_option("-g", "--gbif", type="string", default=None, dest="gbif", help="Occurence file gotten from get_gbif")
    parser.add_option("-w", "--warp-scale", type="float", default=1.0, dest="warp_scale", help="Warp scale for the vertical axis.")
    parser.add_option("--DDD", dest="DDD", default = False, action = 'store_true', help="Plot a 3 dimensional version of the data")
    parser.add_option("--no-DDD", dest="DDD", action = 'store_false', help="Normal 2 dimension plot.")
    (options, args) = parser.parse_args(argv)
    return animate(args[0],
     vmin=options.min,
     vmax=options.max,
     output=options.output,
     gbif=options.gbif,
     DDD=options.DDD,
     warp_scale=options.warp_scale)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
