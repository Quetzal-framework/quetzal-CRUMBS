Install the CRUMBS and their dependencies
==========================================

iDDC modeling is quite a complex workflow and geospatial manipulations,
C++ simulations and visualization require some system dependencies.

Using Docker containers allows to simplify this a lot (see next section), especially
if you want to deploy the framework on clusters.

If you want/need a local installation, you can try the following steps, that have
been tested with

* macOS 12 Monterey
* Ubuntu 20.04 LTS
* Ubuntu 22.04 LTS
* for Python 3.6 to 3.10.

|:bulb:| If you are outside of this configuration, you may have some problems,
but `ask me on Github <https://github.com/Becheler/quetzal-CRUMBS/issues>`_ if we can find a fix!

|:ambulance:| I tried my best to come with a repeatable local installation procedure,
but if you have any problem, again `see you on Github <https://github.com/Becheler/quetzal-CRUMBS/issues>`_!

macOS
---

First install GDAL:

.. code-block:: bash

    brew install gdal

Then install the Python package:

.. code-block:: bash

    python3 -m pip install quetzal-crumbs


Ubuntu
---

Things get a bit trickier with Linux distributions |:see_no_evil:|

Ubuntu 20.04 LTS (Focal Fossa)
^^^

Install GDAL:

.. code-block:: bash

    sudo apt-get update
    sudo add-apt-repository ppa:ubuntugis/ppa && sudo apt-get update
    sudo apt-get install gdal-bin
    sudo apt-get install libgdal-dev
    python3 -m pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==`gdal-config --version`



Then install Linux packages for Qt5 support:

.. code-block:: bash

    sudo apt-get install qt5-default
    sudo apt-get install libxkbcommon-x11-0
    sudo apt-get install libxcb-icccm4
    sudo apt-get install libxcb-image0
    sudo apt-get install libxcb-keysyms1
    sudo apt-get install libxcb-randr0
    sudo apt-get install libxcb-render-util0
    sudo apt-get install libxcb-xinerama0

Then (in your virtual environment) install python packages for Mayavi support:

.. code-block:: bash

    python3 -m pip install pyqt5
    python3 -m pip install numpy
    python3 -m pip install vtk
    python3 -m pip install pillow

And finally install CRUMBS (in your virtual environment)

.. code-block:: bash
    python3 -m pip install quetzal-crumbs



Ubuntu 22.04 LTS (Jammy Jellyfish)
^^^

Install GDAL:

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install gdal-bin
    sudo apt-get install libgdal-dev
    python3 -m pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==`gdal-config --version`

Then install Linux packages for Qt5 support:

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install libxcb-xinerama0

Then (in your virtual environment) install python packages for Mayavi support:

.. code-block:: bash

    python3 -m pip install numpy
    python3 -m pip install https://github.com/pyvista/pyvista-wheels/raw/main/vtk-9.1.0.dev0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
    python3 -m pip install pillow

|:bulb:| Until Kitware releases official VTK wheels for Python 3.10, we will need this weird dependency...

And finally install CRUMBS (in your virtual environment)

.. code-block:: bash

    python3 -m pip install quetzal-crumbs
