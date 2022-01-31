#!/usr/bin/python
from optparse import OptionParser
import io
import rasterio.plot
from rasterio.plot import show_hist

from matplotlib import pyplot
import imageio
from tqdm import tqdm
import numpy

def plot(fig):
    with io.BytesIO() as buff:
        fig.savefig(buff, format='raw')
        buff.seek(0)
        data = numpy.frombuffer(buff.getvalue(), dtype=numpy.uint8)
    w, h = fig.canvas.get_width_height()
    im = data.reshape((int(h), int(w), -1))
    return(im)


def animate(inputRaster, vmin=None, vmax=None, output=None, gbif=None, DDD=False):
    output = 'animation.gif' if output is None else output

    with rasterio.open(inputRaster) as source:
        source_data = source.read(masked=True)

        if vmax is None: vmax = source_data.max()
        if vmin is None: vmin = source_data.min()

        with imageio.get_writer(output, mode='I') as writer:

            for bandID in tqdm(range(1, source.count + 1)):

                if DDD is not True:
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
                    writer.append_data(plot(fig))

                if DDD is True:
                    # Create the data
                    Z = source_data[bandID-1].astype(float)
                    if isinstance(Z, numpy.ma.MaskedArray):
                        Z = Z.filled(numpy.nan)  # Set masked values to nan
                    nrows, ncols = Z.shape
                    x = numpy.linspace(source.bounds[0], source.bounds[2], ncols)
                    y = numpy.linspace(source.bounds[1], source.bounds[3], nrows)
                    X, Y = numpy.meshgrid(x, y)
                    # Visualization
                    from mayavi import mlab
                    mlab.surf(Z, colormap='viridis', warp_scale=0.1)
                    plot(mlab.figure)

def get_band(Z, i):
    """ Return the ith band of the (possibly masked) Z 3D array: if masked, fills masked values with nan.
    """
    z = Z[i].astype(float)
    if isinstance(z, numpy.ma.MaskedArray):
        z = z.filled(numpy.nan)  # Set masked values to nan
    return z

from mayavi import mlab

def save_to_buffer(fig):
    with io.BytesIO() as buff:
        fig.savefig(buff, format='raw')
        buff.seek(0)
        data = numpy.frombuffer(buff.getvalue(), dtype=numpy.uint8)
    w, h = fig.canvas.get_width_height()
    im = data.reshape((int(h), int(w), -1))
    return(im)

@mlab.animate(delay=10, ui=False)
def update_animation(Z, surface, writer, vmin, vmax):
    f = mlab.gcf()
    t = 2.0
    while t <= Z.shape[0]:
        # get the current lut manager
        lut_manager = mlab.colorbar(orientation='vertical')
        surface.module_manager.scalar_lut_manager.use_default_range = False
        surface.module_manager.scalar_lut_manager.data_range = numpy.array([vmin, vmax])
        surface.update_pipeline()
        f.scene.camera.azimuth(1)
        f.scene.render()
        surface.mlab_source.scalars = get_band(Z, int(t)-1)
        t += 0.1
        writer.append_data(mlab.screenshot())
        yield

def animate2(inputRaster, vmin=None, vmax=None, output=None, gbif=None, DDD=False, warp_scale=1.0):
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
            elif(DDD is True):
                surface = mlab.surf(get_band(Z, 0), colormap='viridis', warp_scale=0.1)

            # Sets nan pixels to white
            surface.module_manager.scalar_lut_manager.lut.nan_color = 0, 0, 0, 0

            a = update_animation(Z, surface, writer, vmin, vmax)

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
    return animate2(args[0],
     vmin=options.min,
     vmax=options.max,
     output=options.output,
     gbif=options.gbif,
     DDD=options.DDD,
     warp_scale=options.warp_scale)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
