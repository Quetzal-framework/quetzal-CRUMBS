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

Fitting a SDM
---------------

Context
^^^^^^^^^^


Command
^^^^^^^^^^

.. code-block:: bash

  species='Heteronotia binoei'
  presences='occurrences.shp'
  buffer=2.0
  biovars=dem,bio01

  crumbs-fit-sdm \
        --species $species \
        --presences $presences \
        --nb-backround 30 \
        --variables $biovars \
        --buffer $buffer \
        --cleanup

Output
^^^^^^^^^^

.. code-block:: text

    - Quetzal-CRUMBS - Fitting Species Distribution Models for iDDC modeling
    - Quetzal-CRUMBS - CHELSA-TraCE21k data access for iDDC modeling
        ... rasters will be cropped to bounding box infered from points: POLYGON ((128.349138 -18.275254, 138.893138 -18.275254, 138.893138 -9.750165, 128.349138 -9.750165, 128.349138 -18.275254))
    https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/orog/CHELSA_TraCE21k_dem_20_V1.0.tif
        ... World file does not exist, starting download from scratch.
    100% 252M/252M [00:16<00:00, 15.5MiB/s]
    https://os.zhdk.cloud.switch.ch/envicloud/chelsa/chelsa_V1/chelsa_trace/bio/CHELSA_TraCE21k_bio01_20_V1.0.tif
        ... World file does not exist, starting download from scratch.
    100% 528M/528M [00:33<00:00, 15.7MiB/s]
        ... reading presence shapefile datatsets:
            - number of duplicates:  4
            - number of NA's:  0
            - coordinate reference system: epsg:4326
            - 30 observations with 3 columns
        ... after removing duplicated occurrences:
            - number of duplicates:  0
            - number of NA's:  0
            - coordinate reference system: epsg:4326
            - 26 observations with 3 columns
        ... after removing occurrences falling in ocean cells (NA, -inf, +inf):
            - number of duplicates:  0
            - number of NA's:  0
            - coordinate reference system: epsg:4326
            - 26 observations with 4 columns
        ... building presence/absence dataset:
            - number of duplicates:  0
            - number of NA's:  0
            - coordinate reference system: epsg:4326
            - 56 observations with 2 columns
        ... there are 2 explanatory rasters features
        ... loading training vector
        ... loading explanatory rasters
        ... fitting classifiers on training data
        ... Classifier rf
            - k-fold cross validation for accuracy scores (displayed as a percentage)
            - rf 5-fold Cross Validation Accuracy: 57.42 (+/- 23.71)
            - fitting model
            - trained model will be saved to model-persistence/rf.joblib
        ... Classifier et
            - k-fold cross validation for accuracy scores (displayed as a percentage)
            - et 5-fold Cross Validation Accuracy: 59.09 (+/- 19.92)
            - fitting model
            - trained model will be saved to model-persistence/et.joblib
        ... Classifier xgb
            - k-fold cross validation for accuracy scores (displayed as a percentage)
            - xgb 5-fold Cross Validation Accuracy: 57.27 (+/- 30.21)
            - fitting model
            - trained model will be saved to model-persistence/xgb.joblib
        ... Classifier lgbm
            - k-fold cross validation for accuracy scores (displayed as a percentage)
            - lgbm 5-fold Cross Validation Accuracy: 38.18 (+/- 38.83)
            - fitting model
            - trained model will be saved to model-persistence/lgbm.joblib


References
----------

.. [Rocklin2015] Rocklin, M. (2015) Dask: Parallel computation with blocked algorithms and task scheduling. In Proceedings of the 14th python
   in science conference, vol. 130, 136. Citeseer.
