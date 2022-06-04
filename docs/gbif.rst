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
* presence points (*retrieved from the Global Biodiversity Information Facility*)
* pseudo-absence points (*generated from the presence points and the CHELSA Digital Elevation Model*).

To integrate GBIF occurrence records in an IDDC workflow, you need to:

1. download the observational data
2. restrict them to your area of interest (a bounding box around your genetic sample +/- an offset in km)
3. remove duplicated points
4. download the CHELSA-TraCE21k Digital Elevation Model for the present century
5. filter out the data points that falls in the ocean cells
6. export the remaining points to a shapefile

But To facilitate the
