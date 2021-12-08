# Quetzal-CRUMBS <img align="right" width="200" src="https://github.com/Becheler/Becheler.github.io/raw/master/draw/logos/quetzal_crumbs.png">

[![Becheler](https://circleci.com/gh/Becheler/quetzal-CRUMBS.svg?style=shield)](https://app.circleci.com/pipelines/github/Becheler)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Website becheler.github.io](https://img.shields.io/website-up-down-green-red/https/becheler.github.io.svg)](https://becheler.github.io/pages/quetzal_crumbs/home)
[![PyPI version](https://badge.fury.io/py/quetzal-crumbs.svg)](https://badge.fury.io/py/quetzal-crumbs)

General utility scripts for the Quetzal framework projects

## Usage in bash

At the present moment the python interfaces are not very stable, and are not really
meant to be used directly. I prefer to use Quetzal-CRUMBS in bash scripts
when I'm doing ABC-inference or when I'm calibrating my simulations.

### Sampling parameters in prior distribution

* Sampling integers (*e.g.*, population size): `N=$(python3 -m crumbs.sample "uniform_integer" 10 1000)`
* Sampling double (*e.g.*, probability): `p=$(python3 -m crumbs.sample "uniform_real" 0.0001 0.1)`
* Sampling a coordinate uniformly at random in a geotiff file:
    * `latlon=($(python3 -m crumbs.sample "uniform_latlon" "file.tif" | tr -d '[],'))`
    * get latitude with `${latlon[0]}`
    * get longitude with `${latlon[1]}`

### Visualizing demographic history:

* If you chose to log the demographic history from Quetzal-EGGS programs (option `log-history=history.tif` in the EGG configuration file), then you can convert it into an animation using CRUMBS.
It is quite handy to check the impact of parameters or suitability on the simulation. The `animate`
function can be called with the following:
    * **Default settings** (generates an `animation.gif`):
    `python3 animate.py --input "animation.tif"`
    * **Change the output format** (detects the mp4 extension and converts accordingly):
    `python3 animate.py --input "animation.tif" --output "animation.mp4"`
    * **Change the colorbar cap value** (if none is given then the max value is inferred from the multiband raster).
    `python3 animate.py --input "animation.tif" --vmax 100`
    * **Combination of the previous:** `python3 animate.py --input "animation.tif" --output "animation.mp4" --vmax 100`

# Updating the package (tip note for the dev)

* Create a `feature` branch, make updates to it.
* Test the feature
* Bump the version in `setup.cfg`
* Bump the version of the `whl` file in `.circleci/config.yml`
* Update the ChangeLog
* Push to GitHub

When you have a successful build on https://app.circleci.com/pipelines/github/Becheler/quetzal-CRUMBS:
* create a Pull Request (PR) to the develop branch
* Merge the PR if it looks good.
* When that build succeeds, create a PR to the main branch, review it, and merge.
* Go get a beer and bless this new version with some luuuv.

Workflow from https://circleci.com/blog/publishing-a-python-package/.
