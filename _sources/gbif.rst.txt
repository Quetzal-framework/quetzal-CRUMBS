Accessing the GBIF database with Quetzal-CRUMBS
=====================================================

The first step in IDDC modeling is to reconstruct a dynamic suitability map to inform every
generation (or year, or century) of the simulation of a meta-population.
This suitability map can be derived from a Species Distribution Model
(aka an Environmental Niche Model).

There are many models available out there, and in CRUMBS we use a model averaging over 4 classifiers:

* Random Forest (RF)
* Extra-Tree (ET)
* Extreme Gradient Boosting (XGB)
* Light Gradient Boosted Machine (LGBM)

These classifiers use spatial predictors (bioclimatic variables from CHELSA) and the following features:

* presence points retrieved from the Global Biodiversity Information Facility
* pseudo-absence points generated from the presence points and the CHELSA Digital Elevation Model.

You could download manually the observational data, restrict them to you area of interest,
discard the data points that are aberrant in regard of the simulated topography etc.
But To facilitate the
