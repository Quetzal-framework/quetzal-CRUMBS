Species Distribution Modeling with Quetzal-CRUMBS
================================================

Species distribution modelling (SDM), or equivalently environmental niche modelling (ENM),
(or habitat modelling, or predictive habitat distribution modelling or range mapping!)
is a methodoogy that tries to predict the distribution
of a species across geographic space and time.

Within the iDDC approach, the idea is to reconstruct the landscape habitability
to inform various aspects of a species ecology. Although there are many tools
existing for SDM, several reasons motivated us to develop an iDDC-specific resource.

* High-resolution environmental data like CHELSA are new (2021) and to our
  knowledge there is no other way to easily script the access to these layers and their post-treatment
* Developing our own tools for iDDC means more control on scalability:
    * For example we could integrate **dask** [Rocklin2015]_ for parallel computing and larger-than-memory data management
    * We use **jòblib** for model persistence of fitted classifiers
    * Combined with the right command-line interfaces, that makes SDM extrapolation to past climates
      easier to distribute on High-Throughput Computing Grids.

Why do we need CHELSA?
-------------------------------

References
----------

.. [Rocklin2015] Rocklin, M. (2015) Dask: Parallel computation with blocked algorithms and task scheduling. In Proceedings of the 14th python
   in science conference, vol. 130, 136. Citeseer.
