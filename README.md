# Quetzal-CRUMBS <img align="right" width="200" src="https://github.com/Becheler/quetzal-CRUMBS/blob/media/quetzal-crumbs.png">

[![Becheler](https://circleci.com/gh/Becheler/quetzal-CRUMBS.svg?style=shield)](https://app.circleci.com/pipelines/github/Becheler)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Website becheler.github.io](https://img.shields.io/website-up-down-green-red/https/becheler.github.io.svg)](https://becheler.github.io/pages/quetzal_crumbs/home)
[![PyPI version](https://badge.fury.io/py/quetzal-crumbs.svg)](https://badge.fury.io/py/quetzal-crumbs)

General utility scripts for the Quetzal framework projects and iDDC modeling (Integrated Distributional, Demographic, Coalescent models).

## Usage in bash

:warning: At the present moment the python interfaces are not very stable, and are not really
meant to be used directly. I prefer to use Quetzal-CRUMBS in bash scripts
when I'm doing ABC-inference or when I'm calibrating my simulations.

-------------------------------------------------------------------------------
### :game_die: Sampling model parameters in a prior distribution


* Sampling integers (*e.g.*, population size): `N=$(python3 -m crumbs.sample "uniform_integer" 10 1000)`
* Sampling double (*e.g.*, probability): `p=$(python3 -m crumbs.sample "uniform_real" 0.0001 0.1)`
* Sampling a coordinate uniformly at random in a geotiff file:
    * `latlon=($(python3 -m crumbs.sample "uniform_latlon" "file.tif" | tr -d '[],'))`
    * get latitude with `${latlon[0]}`
    * get longitude with `${latlon[1]}`

-------------------------------------------------------------------------------
### :clapper: Visualizing a dynamic landscape:

This `animate` function facilitates visual checks of the impact of landscape features or other parameters on the simulation:
- If you have a multi-band raster representing a dynamic landscape (*e.g.,* using `crumbs.interpolate`),
you can easily perform a visual check of the landscape dynamics before to run the simulations
- If you chose to log the demographic history from Quetzal-EGGS programs (option `log-history=history.tif` in the EGG configuration file), then you can convert it into an animation using CRUMBS.

- The `animate` function can be called with the following:
    * **Default settings:** generates an animated gif    
    `python3 animate.py input.tif`
    * **Change the output format:** detects the mp4 extension and converts accordingly    
    `python3 animate.py  input.tif -o "output.mp4"`
    * **Change the colorbar cap value:** if none is given then the max value is inferred from the multiband raster):  
    `python3 animate.py input.tif" --vmax 100`
    * **Combination of the previous:**  
    `python3 animate.py input.tif -o output.mp4 --vmax 100`

The quetzal-EGG program you are using is responsible for logging the parameter values in the SQLite database. They can be retrieved later.

--------------------

### :scissors: Cutting a circular landscape

> :bulb: When you begin to rotate and rescale landscapes, you can end up with quite counter-intuitive orientations that are not very convenient.  
To facilitate landscape manipulation and analysis, we implemented a function that fits and cuts a circle with maximal radius around the landscape center:

* **Default settings:** generates a `disk.tif` file    
`python3 -m crumbs.circle_mask input.tif`
* **Change the output name:**  
`python3 -m crumbs.circle_mask input.tif -o masked_output.tif`

--------------------------------------------------------------------------------
### :globe_with_meridians: Sampling spatial grid parameters

> :bulb: In spatial dynamic models, resolution of the landscape is an issue (see e.g. [Bocedi et al. 2012](https://besjournals.onlinelibrary.wiley.com/doi/full/10.1111/j.2041-210X.2012.00235.x)).  
> * If the resolution is too low, biological processes may be misrepresented and important biases may plague the results.  
> * If the resolution is too high, computational
costs make ABC methodology impossible.  
> * The same goes with the grid orientation, that is arbitrary but is a necessary model parameter.  
>
> Choices have to be made and their
impact on inference should be carefully assessed: one way to do so is to include
the spatial resolution and grid orientation as parameters to be sampled and estimated by ABC inference
(see e.g., [Baird and Santos 2010](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1755-0998.2010.02865.x?casa_token=LDz1BGeg5lgAAAAA:_cCFdutvABU0kUsKxQApztP_tU9Yulej32wRRM8vb8Q3pQxlysu7LITGpxlweX81QKhm0tfaiyzWBAE),
[Estoup et al. 2010](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1755-0998.2010.02882.x?casa_token=R0ybkgcrDIAAAAAA:Et4XddaPhgFee8XEAJP_QS1G1O-Ocxw6dVZeAEra7ye91rLcxZ0QqZrr67smVkhns4TsTnf9134DDVs)).

#### :arrows_counterclockwise: Adjusting the grid orientation

* Sample a rotation angle about the center in a prior distribution:  
  `angle=$(python3 -m crumbs.sample "uniform_real" 0.0 360.0)`
* Then you can call the `rotate_and_rescale` function:  
    * **Default:** generates a `rotated.tif` file with no resolution change (scale=1)   
    `python3 -m crumbs.rotate_and_rescale input.tif $angle`
    * **Change the output name:**  
    `python3 -m crumbs.resample input.tif $angle $factor -o out.tif`

#### :mag_right: Adjusting the grid resolution:

* Sample a rescaling factor in a prior distribution:  
`scale=$(python3 -m crumbs.sample "uniform_real" 0.5 2)`
* Perform the rescaling with no rotation (angle=0):  
 `python3 -m crumbs.rotate_and_rescale input.tif 0.0 $scale`
* Perform the rescaling with a rotation:
`python3 -m crumbs.rotate_and_rescale input.tif $angle $scale`

>  :open_book:   
>*Upsampling*: converting to higher resolution/smaller cells (scale > 1)  
    *Downsampling*: converting to lower resolution/larger cell (scale < 1)  

--------------------------------------------

### :hourglass_flowing_sand: Temporal interpolation

> :bulb: You typically don't have a raster whose number of bands (*i.e.*, layers) that conveniently matches the number
of generations of the simulation. Instead, iDDC studies have focused on using a limited number of bands to represent the landscape temporal variance, mapping them to classes of events in a quite cumbersome way.
>
>*e.g.*, using 3 bands: *present*, *past*, *distant_past* :black_large_square: :black_medium_square: :black_small_square: and mapping them to time periods
>
> :gift: But because Quetzal-CoaTL embeds the GDAL library, it allows much more granularity in
the way to represent the landscape. With the `interpolate` function, you can:  
- assignexisting bands to the generations of your choice:
    - the first band must be assigned to 0
    - the last band is assigned to the integer *n* of you choice, *n* being the number of generations of the simulation
- The crumbs will interpolate the missing layers
- When it's done, you can simply pass the output to a Quetzal-EGG simulator: no painful mapping required!

* To generate a `interpolated.tif` file with 10 bands (*i.e.*, 10 generations) from a raster with only 2 bands:   
`python3 -m crumbs.interpolate input_with_2_bands.tif 0 9`
* To generate a `interpolated.tif` file with 100 bands (*i.e.*, 100 generations) fom a raster with only 3 bands (the middle band being assigned to generation 42):  
`python3 -m crumbs.interpolate input_with_3_bands.tif 0 42 99`
* General mapping form, also changing the output name:
`python3 -m crumbs.circle_mask input_n_band.tif <0 ... n-2 other values ... X> -o output_with_X_bands.tif`

--------------------------------------------------------------------------------
### :rocket: Updating the package (tip note for the dev)


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
# References

* Bocedi, G., Pe’er, G., Heikkinen, R. K., Matsinos, Y., & Travis, J. M. (2012). Projecting species’ range expansion dynamics: sources of systematic biases when scaling up patterns and processes. Methods in Ecology and Evolution, 3(6), 1008-1018.

* Baird, S. J., & Santos, F. (2010). Monte Carlo integration over stepping stone models for spatial genetic inference using approximate Bayesian computation. Molecular ecology resources, 10(5), 873-885.

* Estoup, A., Baird, S. J., Ray, N., Currat, M., CORNUET, J. M., Santos, F., ... & Excoffier, L. (2010). Combining genetic, historical and geographical data to reconstruct the dynamics of bioinvasions: application to the cane toad Bufo marinus. Molecular ecology resources, 10(5), 886-901.
