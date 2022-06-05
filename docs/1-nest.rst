Enter the Quetzal-NEST Docker container
==========================================

Quetzal-NEST is the Docker container where the Quetzal framework lives, and it
can be deployed on clusters for scalable, massively parallel, reproducible science.
The container is published on `DockerHub <https://hub.docker.com/r/arnaudbecheler/quetzal-nest>`_
and publicly available for local and remote use.

Why do we need a Docker container?
-----------------------------------

To encapsulate the chaos of iDDC analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

iDDC modeling is quite a complex workflow and requires many system dependencies
and tricky configurations: in its current version, the Quetzal framework needs
more than 65 dependencies that have to coexist peacefully on the same system.

Using Docker containers allows to simplify and stabilize things quite a lot,
as these containers allow to *freeze* entire systems and *distribute* them to the users.

To provide the benefits of virtual machines  with extra bonus
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Containers are enabled by isolation and virtualization capabilities built into
the Linux kernel. These capabilities makes it possible for multiple application components
to coexist on an host operating system and share its resources.

It is quite similar to the way that multiple virtual machines (VMs) can share the CPU and memory
of a same hardware, and containers and VMs actually share a number of benefits:

* application isolation: *you don't need to mess up your system to use the app*
* disposability: *download, use when needed, delete whenever, repeat*

But containers come with some extras:

* Lighter weight: *containers don't have to pack an entire OS like VMs do, they just embed what is strictly necessary to interface with the hos OS.*
* Improved productivity: *containers are faster and easier to deploy than VMs, making them great for distributed computing.*

How do I use Quetzal-NEST locally?
----------------------

Get started
^^^^^^^^^^^^^^^^^^^^^^

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
All files present in you folder at the moment you start the container will be available
to the computations, and all files generated in the container will also be available to
your system.

List of basic docker commands
^^^^^^^^^^^^^^^^^^^^^^

+-------------------------------------------------+-------------------------------------------------+
| Bash command                                    | Effect                                          |
+========================+========================+=================================================+
|``docker -version``                              | will give the version of Docker is installed.   |
+-------------------------------------------------+-------------------------------------------------+
|``docker pull <image_name>``                     | will download the image from dockerhub.         |
+-------------------------------------------------+-------------------------------------------------+
|``docker run  <image_name>``                     | | will run the image pulled from dockerhub to   |
|                                                 | | create a container. If you don’t have a local |
|                                                 | | copy of the image, the run command will pull  |
|                                                 | | and then run the image to create a container. |
+-------------------------------------------------+-------------------------------------------------+
|``docker ps``                                    | | process status of containers. If no container |
|                                                 | | is running, you get a blank line.             |
+-------------------------------------------------+-------------------------------------------------+
|``docker ps -a``                                 | process status of all containers.               |
+-------------------------------------------------+-------------------------------------------------+
|``docker exec -it <container_id> bash``          | | allows you to run a command in the docker     |
|                                                 | | container. The -it flag provides an           |
|                                                 | | interactive tty (shell) within the container. |
+-------------------------------------------------+-------------------------------------------------+
|``docker stop <container_id>``                   | shuts down a container.                         |
+-------------------------------------------------+-------------------------------------------------+
|``docker build <path_to_docker_file>``           | builds an image from the specified docker file  |
+-------------------------------------------------+-------------------------------------------------+
|``docker push <docker_hub_username/image_name>`` | pushes an image to the docker hub repository.   |
+-------------------------------------------------+-------------------------------------------------+


How do I deploy quetzal-NEST on clusters?
-----------------------------

You can use Singularity to deploy Docker images on clusters to run iDDC worflows:
no need to ask your favorite cluster maintenance guy to manually install every dependency!

On the Open Science Grid:
^^^^^^^^^^^^^^^^^^^^^^

The `Open Science Grid <https://opensciencegrid.org/>`_ is a consortium of research collaborations,
campuses, national laboratories, and software providers dedicated
to the advancement of all open science via the practice of distributed High Throughput Computing (dHTC).
It provides a capability to run independent computations at massive scales, what is
pretty clutch for iDDC, and `supports the use of Docker/Singularity images <https://support.opensciencegrid.org/support/solutions/articles/12000024676-docker-and-singularity-containers>`_

Quetzal-NEST has been submitted to the Open Science Grid CVMFS image repository
where it is available for distributed High Throughput Computing.
To make it available to your computation, just add these two lines to your ``.condor`` project file:

.. code-block::

   Requirements           = HAS_SINGULARITY == TRUE
   +SingularityImage      = "/cvmfs/singularity.opensciencegrid.org/arnaudbecheler/quetzal-nest:latest"


On the NASA Pleiades
^^^^^^^^^^^^^^^^^^^^^^

Docker containers present some security risks and have to be first `converted to Singularity <https://www.nas.nasa.gov/hecc/support/kb/converting-docker-images-to-singularity-for-use-on-pleiades_643.html>`_
to be deployed on the NASA Pleiades:

.. code-block::

   pfe$ module load singularity
   pfe% singularity pull lolcow.sif docker://arnaudbecheler/quetzal-nest
   # or
   pfe$ singularity build --sandbox lolcow docker://arnaudbecheler/quetzal-nest


On JetStream2
^^^^^^^^^^^^^^

Jetstream2 `supports Docker and Apptainer/Singularity. <https://docs.jetstream-cloud.org/general/docker/>`_
Apptainer (previously known as Singularity) is installed as part of the Jetstream Software Collection.
You can access Apptainer from any Jetstream Featured Image by doing:

.. code-block::

   module load apptainer
