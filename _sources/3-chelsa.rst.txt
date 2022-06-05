Accessing the CHELSA-TraCE21k 1km climate timeseries with Quetzal-CRUMBS
================================================

`CHELSA-TraCE21k <https://chelsa-climate.org/chelsa-trace21k/>`_ provides
monthly climate data for temperature and precipitation at 30 arcsec spatial
resolution in 100-yeartime steps for the last 21,000 years.
Based on the reconstructed paleo orography, mean annual
temperature and precipitation was downscaled using the CHELSA V1.2 algorithm ([Karger2021]_).

Why do we need CHELSA?
-------------------------------

At phylogeographic scales, climatic variations cause changes in sea-levels and orography,
and as a result have an important impact on the biodiversity, affecting species migration
patterns and ecology. Database with high spatial resolution are a necessity when
processes happening at a small spatial scale (*e.g., two masses of land that get disconnected
by a single small strait*) impact a species ecology (*e.g., isolation of population*)
and have a snowball effect on the downstream levels of biodiversity
at higher spatial scales (*e.g., emergence of two distinct species*).

.. figure:: DEM_dynamic_2D.gif
   :alt: Digital Elevation Model
   :class: with-shadow
   :width: 400px
   :align: center

   Effect of sea-level changes on islands biogeography

Models that can link these scales have to rely on high-resolution landscape data.
iDDC can integrate such data by fitting models of species distribution
on present climate and elevation, extrapolating them to past climates conditions and elevations
to reconstruct dynamic habitability landscapes.

Usage
-------

Quetzal-CRUMBS SDM utilities will automatically download the CHELSA bioclimatic
and elevation files when they need to make them available to the classifiers:
you should not have to download them yourself when you are building
your iDDC workflow.

However, if you happen to download some CHELSA files for your own needs,
here is how to do so.

Context
^^^^^^^^^^

You need a shapefile to define the longitude/latitude points to define the area
of the world of interest.
In iDDC wokflows, the points of interest would normally be the coordinates of your
DNA samples, but if you want to reproduce our example then just download our test
data points from Github:

1. Go to the `Download Directory <https://download-directory.github.io/>`_ utility
2. Enter this url: ``https://github.com/Becheler/quetzal-CRUMBS/tree/main/tests/data/test_points``
3. Press enter to start the download
4. Extract the archive in your working directory
5. You should find 3 files: move them to your Docker working directory

   * ``test_points.shp``
   * ``test_points.shx``
   * ``test_points.dbf``

.. warning::
  CHELSA-TraCE21k uses times identifiers that range from 20 (present century) to -200 (LGM).
  Have a look `at their technical notice <https://chelsa-climate.org/chelsa-trace21k/>`_

Command
^^^^^^^^

.. code-block:: bash

   sample='test_points/test_points.shp'
   buffer=2.0                #in degrees
   biovars=dem,bio01         #or bio01,bio02,bio10,bio12, or simply dem,bio for all
   chelsaTimes=20,0,-20

   crumbs-get-chelsa \
        --variables $biovars \
        --timesID $chelsaTimes \
        --points $sample \
        --buffer $buffer \
        --cleanup

Behavior
^^^^^^^^^^

1. A world file is downloaded for the variable and time of interest in the ``chelsa-world`` folder
2. The file is cropped to the bounding box of the given geographic points (+/- a buffer in degrees)
3. The resulting landscape file is stored in a ``chelsa-landscape`` folder
4. The world file deleted if ``--cleanup``, or kept if  ``--no-cleanup``.

.. warning::
   These world files are heavy, and there are many many of them, so if you don't need them, use ``--cleanup``.

Output
^^^^^^^^^^

.. code-block:: text

    - Quetzal-CRUMBS - CHELSA-TraCE21k data access for iDDC modeling
        ... rasters will be cropped to bounding box infered from points: POLYGON ((128.8515 -18.2625, 139.0335 -18.2625, 139.0335 -9.0333, 128.8515 -9.0333, 128.8515 -18.2625))
    https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/orog/CHELSA_TraCE21k_dem_19_V1.0.tif
        ... World file does not exist, starting download from scratch.
    100% 252M/252M [00:17<00:00, 14.7MiB/s]
    https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/bio/CHELSA_TraCE21k_bio01_19_V1.0.tif
        ... World file does not exist, starting download from scratch.
    100% 533M/533M [00:36<00:00, 14.5MiB/s]
        ... Converting bands to VRT file: chelsa-stacked_dem.vrt
        ... Converting chelsa-stacked_dem.vrt to GeoTiff file: chelsa-stacked_dem.tif
        ... Converting bands to VRT file: chelsa-stacked_bio01.vrt
        ... Converting chelsa-stacked_bio01.vrt to GeoTiff file: chelsa-stacked_bio01.tif

References
------------

.. [Karger2021] Karger, D. N., Nobis, M. P., Normand, S., Graham, C. H., & Zimmermann, N. E. (2021): CHELSA-TraCE21k v1. 0. Downscaled transient temperature and precipitation data since the last glacial maximum. Climate of the Past Discussions, 1-27.
