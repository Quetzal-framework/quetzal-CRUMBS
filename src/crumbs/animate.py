#!/usr/bin/python
from mayavi import mlab

def plot_to_buffer(fig):
    """ Save figure to a virtual file. Used to append data to gif or mp4 in animate 2D functions.
    """
    import io
    import numpy as np
    with io.BytesIO() as buff:
        fig.savefig(buff, format='raw')
        buff.seek(0)
        data = np.frombuffer(buff.getvalue(), dtype=np.uint8)
    w, h = fig.canvas.get_width_height()
    im = data.reshape((int(h), int(w), -1))
    return(im)

def summary(dataset):
    """ Print most important informations of a geoTiff file.
    """
    print(" - no data value: \t", dataset.nodata )
    print(" - crs:\t", dataset.crs)
    print(" - ", dataset.bounds)
    pxsz, pysz = dataset.res
    print(" - pixel size X: \t", pxsz, "unit:", dataset.crs.linear_units)
    print(" - pixel size Y: \t", pysz, "unit:", dataset.crs.linear_units)
    print(" - width: \t", dataset.width)
    print(" - height: \t", dataset.height)
    return

def get_band(Z, i):
    """ Return the ith band of the (possibly masked) Z 3D array: if masked, fills masked values with nan.
    """
    import numpy as np
    z = Z[i].astype(float)
    if isinstance(z, np.ma.MaskedArray):
        z = z.filled(np.nan)  # Set masked values to nan
    return z

def get_points(shapefile):
    """ Read Point features in a shapefile with a 'Year' property, returning a tuple of lists (lons, lats, years)
    """
    from shapely.geometry import shape
    import fiona
    lons, lats, years = ([] for i in range(3))
    with fiona.open(shapefile, mode='r') as source:
        print(source.crs)
        for feature in source:
            try:
                g = feature["geometry"]
                assert g["type"] == "Point"
                lon, lat = g["coordinates"]
                year = feature['properties']['Year']
                lons.append(float(lon))
                lats.append(float(lat))
                years.append(int(year))
            except IOError:
                logging.exception("Error processing feature %s:", feature["id"])
    return lons, lats, years

def make_X_Y_Z(raster_src, fill):
    import numpy as np
    Z = raster_src.read(masked=True)
    if not np.isnan(fill):
        Z=Z.filled(fill)
    nrows, ncols = Z[0].shape
    # the value returned by bounds is a tuple: (lower left x, lower left y, upper right x, upper right y)
    x = np.linspace(raster_src.bounds[0], raster_src.bounds[2], ncols)
    y = np.linspace(raster_src.bounds[1], raster_src.bounds[3], nrows)
    X, Y = np.meshgrid(x, y)
    return X, Y, Z

def plot_axes():
    import numpy as np
    xx = yy = zz = np.arange(start = 0.0, stop = 1300, step = 1)
    xy = xz = yx = yz = zx = zy = np.zeros_like(xx)
    lensoffset = 0
    mlab.plot3d(yx, yy + lensoffset, yz, line_width=10, tube_radius=10)
    mlab.plot3d(zx, zy + lensoffset, zz, line_width=10, tube_radius=10)
    mlab.plot3d(xx, xy + lensoffset, xz, line_width=10, tube_radius=10)

def decorate(surface, vmin, vmax):
    import numpy as np
    # Custom axes because mayavi defaults suck
    plot_axes()
    # Vertical colorbar
    mlab.colorbar(orientation='vertical')
    # Sets nan pixels to white
    surface.module_manager.scalar_lut_manager.lut.nan_color = 0, 0, 0, 0
    # Fix colorbar to global max/min
    surface.module_manager.scalar_lut_manager.use_default_range = False
    surface.module_manager.scalar_lut_manager.data_range = np.array([vmin, vmax])
    surface.update_pipeline()

def feature_scaling(x, xmin, xmax):
    return (x - xmin) / (xmax -xmin)

def animate_raster_2D(inputRaster, vmin=None, vmax=None, output=None):
    """ Animate a multi-band geotiff raster into a gif or mp4, where every band is a frame.
    """
    import rasterio.plot
    import imageio
    from tqdm import tqdm
    import numpy as np
    from matplotlib import pyplot

    output = 'animation.gif' if output is None else output

    with rasterio.open(inputRaster) as source:
        source_data = source.read(masked=True)

        # Fix value extent across time dimension
        if vmax is None: vmax = np.amax(source_data)
        if vmin is None: vmin = np.amin(source_data)

        with imageio.get_writer(output, mode='I') as writer:

            for bandID in tqdm(range(1, source.count + 1)):
                fig, ax = pyplot.subplots()
                # to get longitude/latitude axis
                extent = np.asarray(source.bounds)[[0,2,1,3]]
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

                writer.append_data(plot_to_buffer(fig))
                pyplot.close()

def animate_gbif_2D(inputRaster, gbif_occurrences, vmin=None, vmax=None, output=None):
    """ Animates spatio-temporal dynamics of GBIF observations on top of the last band of a multi-band raster.
    """
    import rasterio.plot
    import imageio
    from tqdm import tqdm
    import numpy as np
    from matplotlib import pyplot

    output = 'animation.gif' if output is None else output

    with rasterio.open(inputRaster) as source:

        # Retrieve GBIF occurrences to plot, transform to pixel coordinates
        lons, lats, years = get_points(gbif_occurrences)

        sorted_years = sorted(set(years))
        zipped = zip(lons, lats, years)
        sorted_tuples = sorted(zipped, key=lambda x: x[2])

        Z = source.read(masked=True)

        # Fix value extent across time dimension
        if vmax is None: vmax = np.amax(Z)
        if vmin is None: vmin = np.amin(Z)

        # initialize data source at the last time (layer)
        array_2d = get_band(Z, Z.shape[0] - 1)

        with imageio.get_writer(output, mode='I') as writer:
            for year in tqdm(sorted_years):
                fig, ax = pyplot.subplots()
                # to get longitude/latitude axis
                extent = np.asarray(source.bounds)[[0,2,1,3]]
                # use imshow so that we have something to map the colorbar to
                image_hidden = ax.imshow(array_2d,
                                         extent=extent,
                                         cmap='viridis',
                                         vmin=vmin,
                                         vmax=vmax,
                                         zorder=1)
                image_hidden.set_visible(False)
                # plot on the same axis with rio.plot.show
                image = rasterio.plot.show(array_2d,
                                      transform=source.transform,
                                      ax=ax,
                                      cmap='viridis',
                                      vmin=vmin,
                                      vmax=vmax,
                                      zorder=2)

                # add colorbar using the now hidden image
                fig.colorbar(image_hidden, ax=ax)
                pyplot.title(str(year), color=(0,0,0), line_width=1, size=0.5)

                # Plot the occurrences while rotating
                for i in sorted_tuples:
                    if i[2] == year:
                        # Add latitude/longitude points
                        pyplot.scatter(i[0], i[1], c='r', s=40, zorder=3)
                        writer.append_data(plot_to_buffer(fig))
                pyplot.close()

@mlab.animate(delay=10, ui=False)
def update_raster_3D_animation(Z, surface, writer):
    from tqdm import tqdm
    import numpy as np
    figure = mlab.gcf()
    t = 2.0
    increment = 0.1

    sequence = np.arange(t, float(Z.shape[0]), increment)

    for i in tqdm(range(len(sequence))):

        figure.scene.camera.azimuth(1)
        figure.scene.render()

        t += increment
        surface.mlab_source.scalars = get_band(Z, int(t)-1)
        writer.append_data(mlab.screenshot())
        yield

@mlab.animate(delay=10, ui=False)
def update_gbif_3D_animation(output, xs, ys, zs, years, vmin, vmax, warp_scale):
    from tqdm import tqdm
    import imageio

    sorted_years = sorted(set(years))
    zipped = zip(xs, ys, zs, years)
    sorted_tuples = sorted(zipped, key=lambda x: x[3])

    figure = mlab.gcf()
    title = mlab.title(str(sorted_years[0]), color=(0,0,0), line_width=1, size=0.5)
    azimuth = 0.0
    tubes_dict = dict.fromkeys(sorted_years, [])

    with imageio.get_writer(output, mode='I') as writer:

        for year in tqdm(sorted_years):
            # Update title
            title.remove()
            title = mlab.title(str(year), color=(0,0,0), line_width=1, size= 0.5, height=0.9)

            # Fade others tubes a bit more
            for time, tubes in tubes_dict.items():
                for tube in tubes:
                    tube.actor.property.opacity = max(0, tube.actor.property.opacity - 0.1)

            # Plot the occurrences while rotating
            for i in sorted_tuples:

                if i[3] == year:
                    xx = [i[0], i[0]]
                    yy = [i[1], i[1]]
                    zz = [vmin, vmax*warp_scale]
                    # Update current year observations with max opacity
                    new_tube = mlab.plot3d(xx, yy, zz, line_width=5, tube_radius=5, opacity=1)
                    # rotate the figure for each new tube
                    figure.scene.camera.azimuth(1)
                    azimuth += 1.0
                    figure.scene.render()
                    tubes_dict[year].append(new_tube)
                    writer.append_data(mlab.screenshot())
                    yield

        # Finish figure by continuing rotating
        while azimuth < 360.0:
            figure.scene.camera.azimuth(1)
            azimuth += 1.0
            figure.scene.render()
            writer.append_data(mlab.screenshot())
            yield

def animate_gbif_3D(demRaster, gbif_occurrences, output=None, warp_scale=1.0, nb_triangles=None):
    """ Plot the observation points for each year recorded, possibly performs a Delaunay 2D triangulation of the elevation surface.
    """
    import numpy as np
    import rasterio
    output = 'animation_occurrence.gif' if output is None else output

    with rasterio.open(demRaster) as source:
        print("- Elevation source dataset:", demRaster)
        summary(source)

        # Triangulation is impossible with nan or masked values
        fill = 0.0 if nb_triangles is not None else np.nan
        X, Y, Z = make_X_Y_Z(source, fill=fill)

        vmax = np.amax(Z)
        vmin = np.amin(Z)
        extent = [0, Z.shape[2] - 1, 0, Z.shape[1] - 1, vmin, vmax]

        # Retrieve GBIF occurrences to plot, transform to pixel coordinates
        lons, lats, years = get_points(gbif_occurrences)
        points_ys, points_xs = rasterio.transform.rowcol(transform=source.transform, xs=lons, ys=lats)

        # initialize data source at the last time (layer)
        array_2d = get_band(Z, Z.shape[0] - 1)

        # tubes Z coordinates
        points_zs = [ array_2d[points_ys[i], points_xs[i]] for i in range(len(points_xs)) ]

        # initialize the figure
        fig = mlab.figure(1, bgcolor=(1, 1, 1), size=(600,600))

        if nb_triangles is None:
            surface = mlab.surf(array_2d, colormap='viridis', extent = extent)
            surface.actor.actor.scale = [1, 1, warp_scale]

        elif nb_triangles is not None:
            print("heyo")
            # initialize data source
            data = mlab.pipeline.array2d_source(array_2d)
            # Use a greedy_terrain_decimation to created a decimated mesh
            terrain = mlab.pipeline.greedy_terrain_decimation(data)
            terrain.filter.error_measure = 'number_of_triangles'
            terrain.filter.number_of_triangles = nb_triangles
            terrain.filter.compute_normals = True
            # Plot it black the lines of the mesh
            lines = mlab.pipeline.surface(terrain, color=(0, 0, 0), representation='wireframe', extent=extent)
            # The terrain decimator has done the warping. We control the warping scale via the actor's scale.
            lines.actor.actor.scale = [1, 1, warp_scale]
            # Display the surface itself.
            surface = mlab.pipeline.surface(terrain, colormap='viridis', extent=extent)
            surface.actor.actor.scale = [1, 1, warp_scale]
            # Get current_scene
            s = mlab.get_engine().current_scene
            # Set the scene to an isometric view.
            s.scene.isometric_view()

        a = update_gbif_3D_animation(output, points_xs, points_ys, points_zs, years, vmin, vmax, warp_scale)
        mlab.show()

def animate_raster_3D(inputRaster, vmin=None, vmax=None, output=None, warp_scale=1.0):
    """ Animate an elevational raster with values changing over time
    """
    import numpy as np
    import imageio

    with rasterio.open(inputRaster) as source:
        print("- Source dataset:", inputRaster)
        summary(source)

        # Elevation surface
        X, Y, Z = make_X_Y_Z(source, fill=np.nan)

        # Fix value extent across time dimension
        if vmax is None: vmax = np.amax(Z)
        if vmin is None: vmin = np.amin(Z)

        extent = [0, Z.shape[2] - 1, 0, Z.shape[1] - 1, vmin, vmax]

        # initialize the figure
        fig = mlab.figure(1, bgcolor=(1, 1, 1), size=(600,600))

        writer = imageio.get_writer(output, mode='I')

        surface = mlab.surf(get_band(Z, 0), colormap='viridis', extent = extent)
        surface.actor.actor.scale = [1, 1, warp_scale]
        s = mlab.get_engine().current_scene
        s.scene.isometric_view()

        a = update_raster_3D_animation(Z, surface, writer, DDD)
        mlab.show()

def chose_method(inputRaster, vmin=None, vmax=None, output=None, gbif_occurrences=None, DDD=False, warp_scale=1.0, nb_triangles=None):
    output = 'animation.gif' if output is None else output

    if gbif_occurrences is not None:
        if DDD is True:
            animate_gbif_3D(demRaster=inputRaster, gbif_occurrences=gbif_occurrences, output=output, warp_scale=warp_scale, nb_triangles=nb_triangles)
        elif DDD is False:
            animate_gbif_2D(inputRaster, gbif_occurrences=gbif_occurrences, output=output)
    else :
        if DDD is True:
            animate_raster_3D(inputRaster, vmin=vmin, vmax=vmax, output=output, warp_scale=warp_scale)
        elif DDD is False:
            animate_raster_2D(inputRaster, vmin=vmin, vmax=vmax, output=output)

def main(argv):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-o", "--output", type="str", dest="output", help="output animation name")
    parser.add_option("-m", "--min", type="float", default=None, dest="min", help="min value in color scale")
    parser.add_option("-M", "--max", type="float", default=None, dest="max", help="max value in color scale")
    parser.add_option("-g", "--gbif", type="string", default=None, dest="gbif", help="Occurence file gotten from get_gbif")
    parser.add_option("-w", "--warp-scale", type="float", default=1.0, dest="warp_scale", help="Warp scale for the vertical axis.")
    parser.add_option("-t", "--triangles", type="int", default=None, dest="nb_triangles", help="Number of triangles for the delaunay tiangulation if -g is defined")
    parser.add_option("--DDD", dest="DDD", default = False, action = 'store_true', help="Plot a 3 dimensional version of the data")
    parser.add_option("--no-DDD", dest="DDD", action = 'store_false', help="Normal 2 dimension plot.")
    (options, args) = parser.parse_args(argv)
    return chose_method(args[0],
     vmin=options.min,
     vmax=options.max,
     output=options.output,
     gbif_occurrences=options.gbif,
     DDD=options.DDD,
     warp_scale=options.warp_scale,
     nb_triangles=options.nb_triangles
     )

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
