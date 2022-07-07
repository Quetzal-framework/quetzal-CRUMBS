Install Quetzal-crumbs on your local system
######################

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

.. note::

    |:bulb:| If you are outside of this configuration, you may have some problems,
    but `ask me on Github <https://github.com/Becheler/quetzal-CRUMBS/issues>`_ if we can find a fix!

.. note::

    |:ambulance:| I tried my best to come with a repeatable local installation procedure,
    but if you have any problem, again `see you on Github <https://github.com/Becheler/quetzal-CRUMBS/issues>`_!

macOS 12 Monterey
**********

First install GDAL:

.. code-block:: bash

    brew install gdal

Then install XQuartz to allow cross-platform applications using X11 for the GUI to run on macOS:

.. code-block:: bash

    brew install --cask xquartz
    # https://docs.github.com/en/actions/learn-github-actions/workflow-commands-for-github-actions#adding-a-system-path
    echo "/opt/X11/bin" >> $GITHUB_PATH
    # https://github.com/ponty/PyVirtualDisplay/issues/42
    mkdir /tmp/.X11-unix
    sudo chmod 1777 /tmp/.X11-unix
    sudo chown root /tmp/.X11-unix

Then install quetzal-crumbs in a virtual environment:

.. code-block:: bash

    python3 -m pip install quetzal-crumbs


Ubuntu 20.04 LTS (Focal Fossa)
**********

Things get a bit trickier with Linux distributions |:see_no_evil:|

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

Then in your virtual environment install the Visualization Toolkit (VTK), an
open source software for manipulating and displaying scientific data:

.. code-block:: bash

    python3 -m pip install vtk

And finally install quetzal-crumbs in your virtual environment:

.. code-block:: bash

    python3 -m pip install quetzal-crumbs


Ubuntu 22.04 LTS (Jammy Jellyfish)
**********

Install GDAL:

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install gdal-bin
    sudo apt-get install libgdal-dev
    python3 -m pip install --global-option=build_ext --global-option="-I/usr/include/gdal" GDAL==`gdal-config --version`

Then install Linux packages for Qt5 support: the `qt5-default` package has been removed
(see `here <https://askubuntu.com/questions/1404263/how-do-you-install-qt-on-ubuntu22-04>`_)
and you now need to install directly its dependencies:

.. code-block:: bash

    sudo apt-get update
    sudo apt install -y qtcreator qtbase5-dev qt5-qmake cmake
    sudo apt-get install libxcb-xinerama0
    sudo apt-get install -y tigervnc-standalone-server xserver-xephyr gnumeric x11-utils

Then (in a virtual environment) install python packages for Mayavi support:

.. code-block:: bash

    python3 -m pip install https://github.com/pyvista/pyvista-wheels/raw/main/vtk-9.1.0.dev0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

.. note::

    |:bulb:| Until Kitware releases official VTK wheels for Python 3.10, we will need this weird dependency...

And finally install CRUMBS (in a virtual environment)

.. code-block:: bash

    python3 -m pip install quetzal-crumbs
