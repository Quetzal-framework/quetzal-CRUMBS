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

-------------------------------------------------------------------------------
### Sampling parameters in prior distribution


* Sampling integers (*e.g.*, population size): `N=$(python3 -m crumbs.sample "uniform_integer" 10 1000)`
* Sampling double (*e.g.*, probability): `p=$(python3 -m crumbs.sample "uniform_real" 0.0001 0.1)`
* Sampling a coordinate uniformly at random in a geotiff file:
    * `latlon=($(python3 -m crumbs.sample "uniform_latlon" "file.tif" | tr -d '[],'))`
    * get latitude with `${latlon[0]}`
    * get longitude with `${latlon[1]}`

-------------------------------------------------------------------------------
### Visualizing demographic history:


* If you chose to log the demographic history from Quetzal-EGGS programs (option `log-history=history.tif` in the EGG configuration file), then you can convert it into an animation using CRUMBS.
It is quite handy to check the impact of parameters or suitability on the simulation. The `animate`
function can be called with the following:
    * **Default settings** (generates an animated gif):  
    `python3 animate.py --input "animation.tif"`
    * **Change the output format** (detects the mp4 extension and converts accordingly):  
    `python3 animate.py --input "animation.tif" --output "animation.mp4"`
    * **Change the colorbar cap value** (if none is given then the max value is inferred from the multiband raster):  
    `python3 animate.py --input "animation.tif" --vmax 100`
    * **Combination of the previous:**  
    `python3 animate.py --input "animation.tif" --output "animation.mp4" --vmax 100`

--------------------------------------------------------------------------------
### Automate spatial resolution selection

In spatial dynamic models, resolution of the landscape is an issue (see e.g. [Bocedi et al. 2012](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/j.2041-210X.2012.00235.x)). If the resolution is too low, biological processes may be misrepresented
and important biases may plague the results. If the resolution is too high, computational
costs make ABC methodology impossible. Choices have to be made and their
impact on inference should be carefully assessed: one way to do so is to include
the spatial resolution and grid orientation as parameters to be estimated
(see e.g., [Baird and Santos 2010](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1755-0998.2010.02865.x?casa_token=LDz1BGeg5lgAAAAA:_cCFdutvABU0kUsKxQApztP_tU9Yulej32wRRM8vb8Q3pQxlysu7LITGpxlweX81QKhm0tfaiyzWBAE),
[Estoup et al. 2010](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1755-0998.2010.02882.x?casa_token=R0ybkgcrDIAAAAAA:Et4XddaPhgFee8XEAJP_QS1G1O-Ocxw6dVZeAEra7ye91rLcxZ0QqZrr67smVkhns4TsTnf9134DDVs)).

* You can sample a resolution with quetzal-CRUMBS.  
  `factor=$(python3 -m crumbs.sample "uniform_real" 0.5 2)`
* Then you can call the resampling function:  
  *Upsampling* refers to cases where we are converting to higher resolution/smaller cells (factor > 1)  
  *Downsampling* is resampling to lower resolution/larger cellsizes (factor <1)  
    * **Default settings** (generates a `resampled.tif` file):  
    `python3 -m crumbs.sample "resample" --input "suitability.tif" --factor $factor)`
    * **Change the output name**:  
    `python3 -m crumbs.sample "resample" -i "suitability.tif" -f $factor -o "myfile.tif")`


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

# References

* Bocedi, G., Pe’er, G., Heikkinen, R. K., Matsinos, Y., & Travis, J. M. (2012). Projecting species’ range expansion dynamics: sources of systematic biases when scaling up patterns and processes. Methods in Ecology and Evolution, 3(6), 1008-1018.

* Baird, S. J., & Santos, F. (2010). Monte Carlo integration over stepping stone models for spatial genetic inference using approximate Bayesian computation. Molecular ecology resources, 10(5), 873-885.

* Estoup, A., Baird, S. J., Ray, N., Currat, M., CORNUET, J. M., Santos, F., ... & Excoffier, L. (2010). Combining genetic, historical and geographical data to reconstruct the dynamics of bioinvasions: application to the cane toad Bufo marinus. Molecular ecology resources, 10(5), 886-901.
