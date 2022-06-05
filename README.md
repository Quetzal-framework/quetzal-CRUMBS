# Quetzal-CRUMBS <img align="right" width="200" src="https://github.com/Becheler/quetzal-CRUMBS/blob/media/quetzal-crumbs.png?raw=True">

[![Website becheler.github.io](https://img.shields.io/website-up-down-green-red/https/becheler.github.io.svg)](https://becheler.github.io/quetzal-CRUMBS/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/quetzal-crumbs.svg)](https://badge.fury.io/py/quetzal-crumbs)
![Lines of code](https://img.shields.io/tokei/lines/github/Becheler/quetzal-CRUMBS)
[![Becheler](https://circleci.com/gh/Becheler/quetzal-CRUMBS.svg?style=shield)](https://app.circleci.com/pipelines/github/Becheler)

This python library is meant to be used along other software from the Quetzal
framework to perform iDDC modeling and inference.

iDDC modeling (Integrated Distributional, Demographic, Coalescent modeling) is a
methodology for statistical phylogeography. It relies heavily on spatial models
and methods to explain how past processes (sea level change, glaciers dynamics,
climate modifications) shaped the present spatial distribution of genetic lineages.

:rocket: The project website lives [here](https://becheler.github.io/quetzal-CRUMBS/).

In short:

1. Access the high resolution paleoclimatic database CHELSA to download world files
2. Fit a Species Distribution model and save (persist) the fitted model
3. Distribute the fitted model on cluster nodes and reconstruct landscape habitability dynamics across millennia.
4. Assemble the layers and prepare the dynamic landscape for simulation-based inference
5. If using Quetzal-EGGS spatial simulators, retrieve parameters and simulated data
6. Use Decrypt to perform robustness analysis of species delimitation methods.


## What problem does this library solve?

iDDC modeling is quite a complex workflow and Quetzal-CRUMBS allows to simplify things quite a lot.

For example, to estimate the current habitat of a species using CHELSA-Trace21k model and reconstruct its high-resolution dynamics along the last 21.000 years (averaged across 4 different ML classifiers), with nice visualizations and GIS operations at the end, you can just do the following:

```bash
# Pull the docker image with all the dependencies
docker pull arnaudbecheler/quetzal-nest:latest

# Run the docker image synchronizing you working directory
docker run --user $(id -u):$(id -g) --rm=true -it \
  -v $(pwd):/srv -w /srv \
  becheler/quetzal-nest:latest /bin/bash
```

This will start your docker container. Once inside, copy/paste the following code in a `script.sh` file,
and then run it with `chmod u+x script.sh && ./script.sh`.

```bash
#!/bin/bash

# your DNA sampling points (shapefile)
sample='sampling-points/sampling-points.shp'

# for present to LGM analysis (but much longer computations) use instead:
# chelsaTimes=$(seq -s ',' -200 1 20)
chelsaTimes=20,0,-50

# spatial buffer around sampling points (in degree)
buffer=2.0

# for proper SDM (but much longer computations) use instead:
# biovars=dem,bio
biovars=dem,bio01

crumbs-get-gbif \
      --species "Heteronotia binoei" \
      --points $sample \
      --limit 30 \
      --year "1950,2022" \
      --buffer $buffer \
      --output occurrences

mkdir -p occurrences
mv occurrences.* occurrences/

crumbs-fit-sdm \
      --presences occurrences/occurrences.shp \
      --variables $biovars \
      --nb-background 100 \
      --buffer $margin \
      --cleanup \
      --sdm-file 'my-fitted-sdm.bin'

# This part can be massively parallelized on dHTC grids
crumbs-extrapolate-sdm \
     --sdm-file 'my-fitted-sdm.bin' \
     --timeID 20

crumbs-extrapolate-sdm \
    --sdm-file 'my-fitted-sdm.bin' \
    --timeID 19
```

What is nice is that you can leverage these long computations for publication
analyses using dHTC (distributed Hight Throughput Computing)
and distribute this load on a cluster grid: check out
[quetzal_on_OSG](https://github.com/Becheler/quetzal_on_OSG)!

# Contact and troubleshooting

:boom: A problem? A bug? *Outrageous!* :scream_cat: Please let me know by opening
an issue or sending me an email so I can fix this! :rescue_worker_helmet:

:bellhop_bell: In need of assistance about this project? Just want to chat?
Let me know and let's have a zoom meeting!

--------------------------------------------------------------------------------
# :rocket: Updating the package (tip note for the dev)

* Create a `feature` branch, make updates to it.
* Test the feature
* Bump the version in `setup.cfg`
* Bump the version of the `whl` file in `.circleci/config.yml`
* Update the ChangeLog
* Push to GitHub

:rainbow: When you have a successful build on https://app.circleci.com/pipelines/github/Becheler/quetzal-CRUMBS:
* create a Pull Request (PR) to the develop branch
* Merge the PR if it looks good.
* When that build succeeds, create a PR to the main branch, review it, and merge.
* Go get a beer and bless this new version with some luuuv :beer: :revolving_hearts:

Workflow from https://circleci.com/blog/publishing-a-python-package/.

---------------------------------------------------
# :books: References

* Karger, Dirk Nikolaus; Nobis, M., Normand, Signe; Graham, Catherine H., Zimmermann,
N.E. (2021). CHELSA-TraCE21k: Downscaled transient temperature and precipitation data
since the last glacial maximum. Geoscientific Model Development - Discussions

* Version 1.0
Karger, Dirk Nikolaus; Nobis, M., Normand, Signe; Graham, Catherine H., Zimmermann, N.E.
(2021). CHELSA-TraCE21k: Downscaled transient temperature and precipitation data since
the last glacial maximum. EnviDat.

* Bocedi, G., Pe’er, G., Heikkinen, R. K., Matsinos, Y., & Travis, J. M. (2012). Projecting species’ range expansion dynamics: sources of systematic biases when scaling up patterns and processes. Methods in Ecology and Evolution, 3(6), 1008-1018.

* Baird, S. J., & Santos, F. (2010). Monte Carlo integration over stepping stone models for spatial genetic inference using approximate Bayesian computation. Molecular ecology resources, 10(5), 873-885.

* Estoup, A., Baird, S. J., Ray, N., Currat, M., CORNUET, J. M., Santos, F., ... & Excoffier, L. (2010). Combining genetic, historical and geographical data to reconstruct the dynamics of bioinvasions: application to the cane toad Bufo marinus. Molecular ecology resources, 10(5), 886-901.
