..
   Note: Items in this toctree form the top-level navigation. See `api.rst` for the `autosummary` directive, and for why `api.rst` isn't called directly.

.. toctree::
   :hidden:

   Home page <self>
   API reference <_autosummary/crumbs>

Welcome to Quetzal-crumbs documentation
=====================================================

This python library is meant to be used along other software from the Quetzal
framework to perform iDDC modeling and inference.

iDDC modeling (Integrated Distributional, Demographic, Coalescent modeling) is a
methodology for statistical phylogeography. It relies heavily on spatial models
and methods to explain how past processes (sea level change, glaciers dynamics,
climate modifications) shaped the present spatial distribution of genetic lineages.

For a quick tour of iDDC, have a look at `my blog post <https://becheler.github.io/who-am-i/>`_

Short list of features:
-----------------------

1. Access the Global Biodiversity Information Facility to retrieve presence points
2. Access the high resolution paleoclimatic database CHELSA to download world files
3. Fit a Species Distribution model and save (persist) the fitted models
4. Distribute the fitted models on cluster nodes and
    * reconstruct landscape habitability dynamics across millennia
    * perform model averaging
    * fetch and assemble the layers
5. Prepare the dynamic landscape for simulation-based inference (virtual layers, resolution...)
6. If using Quetzal-EGGS spatial simulators, retrieve parameters and simulated data from the output database
7. Use Decrypt to perform robustness analysis of species delimitation methods.
