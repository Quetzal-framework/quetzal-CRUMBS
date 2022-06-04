Starting the Quetzal-NEST Docker container
==========================================

Quetzal-NEST is the Docker container where the Quetzal framework lives, and it
can be deployed on clusters for scalable, massively parallel, reproducible science.
The container is published on `DockerHub <https://hub.docker.com/r/arnaudbecheler/quetzal-nest>`_ and publicly available for local and remote use.

Why do we need a Docker container?
-----------------------------------

iDDC modeling is quite a complex workflow and requires many system dependencies
and tricky configurations (in the present state, it's more than 65 dependencies
that have to coexist peacefully!).

Using Docker containers allows to simplify and stabilize things quite a lot,
as these containers allow to *freeze* and *distribute* entire systems.

How do I deploy quetzal-NEST on clusters?
-----------------------------

You can use Singularity to deploy Docker images on clusters to run iDDC worflows:
no need to ask your favorite cluster maintenance guy to manually install every dependency!

On the Open Science Grid:
^^^^^^^^^^^^^^^^^^^^^^

Quetzal-NEST has been submitted to the Open Science Grid CVMFS image repository
where it is available for distributed High Throughput Computing.

To make it available to your computation, just add these two lines to your ``.condor`` project file:

.. code-block::

   Requirements           = HAS_SINGULARITY == TRUE
   +SingularityImage      = "/cvmfs/singularity.opensciencegrid.org/arnaudbecheler/quetzal-nest:latest"


On the NASA Pleiades
^^^^^^^^^^^^^^^^^^^^^^

To deploy it on the NASA Pleiades:

.. code-block:: bash
   pfe$ module load singularity
   pfe% singularity pull lolcow.sif docker://arnaudbecheler/quetzal-nest
   # or
   pfe$ singularity build --sandbox lolcow docker://arnaudbecheler/quetzal-nest


How do I use it locally?
----------------------

First you will need to `install Docker <https://docs.docker.com/get-docker/>`_ on your system. It's very quick, I promise!

Then, you can type this on a terminal

.. code-block:: bash

   # Pull the docker image with all the dependencies
   docker pull arnaudbecheler/quetzal-nest:latest
   # Run the docker image synchronizing with your working directory
   docker run --user $(id -u):$(id -g) --rm=true -it \
   -v $(pwd):/srv -w /srv \
   becheler/quetzal-nest:latest /bin/bash

This will start your docker container, where the Quetzal tools are ready to be used.
