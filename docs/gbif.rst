Accessing the GBIF database with Quetzal-CRUMBS
=====================================================

The first step in IDDC modeling is to reconstruct a suitability map for every
generation (or year, or century) of a simulation.

This suitability map can be derived from a Species Distribution Model
(aka an Environmental Niche Model).

There are many models available out there, and in CRUMBS we use a model averaging over 4 classifiers:

* Random Forest (RF)
* Extra-Tree (ET)
* Extreme Gradient Boosting (XGB)
* Light Gradient Boosted Machine (LGBM)

These models use spatial predictors (bioclimatic variables from CHELSA) and the following features:

* presence points retrieved from the Global Biodiversity Information Facility
* pseudo-absence points generated from the presence points and the CHELSA Digital Elevation Model.
