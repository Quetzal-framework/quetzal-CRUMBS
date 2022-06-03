..
   Note: Items in this toctree form the top-level navigation. See `api.rst` for the `autosummary` directive, and for why `api.rst` isn't called directly.

.. toctree::
   :hidden:

   Home page <self>
   API reference <_autosummary/crumbs>

Welcome to the Quetzal-CRUMBS' documentation
=====================================================

Introduction
------------

This python library is meant to be used along other software from the Quetzal
framework to perform iDDC modeling and inference.

**iDDC modeling** (*integrated Distributional, Demographic, Coalescent modeling*) is a
methodology for statistical phylo-geography. It relies heavily on spatial models
and methods to explain how past processes (sea level change, glaciers dynamics,
climate modifications) shaped the present spatial distribution of genetic lineages.

.. figure:: pipeline_SOFTWARES.svg
   :alt: Quetzal framework
   :class: with-shadow
   :width: 400px

   How Quetzal-CRUMBS fit into other resources for spatial simulations.


* For a quick tour of iDDC, have a look at `my blog post. <https://becheler.github.io/who-am-i/>`_
* For a more formal presentation of the field, see this excellent review by
  `Dennis J. Larsson, Da Pan and Gerald M. Schneeweiss. <https://www.annualreviews.org/doi/abs/10.1146/annurev.ecolsys.38.091206.095702?journalCode=ecolsys>`_

Short list of features:
-----------------------

1. Access the Global Biodiversity Information Facility to retrieve presence points
2. Access the high resolution paleoclimatic database CHELSA to download world files
3. Fit a Species Distribution model and save (persist) the fitted models
4. Distribute the fitted models on cluster nodes and:
    * reconstruct landscape habitability dynamics across millennia
    * perform model averaging
    * fetch and assemble the layers
5. Prepare the dynamic landscape for simulation-based inference
    * adjust the landscape extent and its grid resolution
    * interpolate missing layers if you need to smooth sharp climatic transitions
    * virtualize missing layers if you need to save memory
    * Use the resulting ``landscape.vrt`` file to trick the simulator into believing a layer exists for each generation to simulate
6. Use Quetzal-EGGS spatial simulators, retrieve parameters and simulated genetic data from the output database
7. Use Decrypt to perform robustness analysis of species delimitation methods.

.. figure:: pipeline_CRUMBS.svg
   :alt: Quetzal-CRUMBS main features
   :class: with-shadow
   :width: 400px

   How you can use Quetzal-CRUMBS to inform spatially explicit landscape simulations at phylogeographic scales
