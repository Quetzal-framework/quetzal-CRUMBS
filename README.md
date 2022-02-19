# Quetzal-CRUMBS <img align="right" width="200" src="https://github.com/Becheler/quetzal-CRUMBS/blob/media/quetzal-crumbs.png?raw=True">

[![Becheler](https://circleci.com/gh/Becheler/quetzal-CRUMBS.svg?style=shield)](https://app.circleci.com/pipelines/github/Becheler)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Website becheler.github.io](https://img.shields.io/website-up-down-green-red/https/becheler.github.io.svg)](https://becheler.github.io/pages/quetzal_crumbs/home)
[![PyPI version](https://badge.fury.io/py/quetzal-crumbs.svg)](https://badge.fury.io/py/quetzal-crumbs)

This python library is meant to be used along other softwares from the Quetzal
framework to perform iDDC modeling and inference.

iDDC modeling (Integrated Distributional, Demographic, Coalescent modeling) is a
methodology for statistical phylogeography. It heavily relies on spatial models
and methods to explain how past processes (sea level change, glaciers dynamics, climate modifications)
shaped the present spatial distribution of genetic lineages.

> :books: **What is iDDC, and what is Quetzal?**
> - For an informal introduction to iDDC modeling and the resources I develop, see [my research post](https://becheler.github.io/who-am-i/).
>
> - For a more formal presentation of the field, see this excellent review by [Dennis J. Larsson, Da Pan and Gerald M. Schneeweiss.](https://www.annualreviews.org/doi/abs/10.1146/annurev.ecolsys.38.091206.095702?journalCode=ecolsys)


:boom: A problem? A bug? *Outrageous!* :scream_cat: Please let me know by opening an issue or sending me an email so I can fix this! :rescue_worker_helmet:

:bellhop_bell: In need of assistance about this project? Just want to chat? Let me know and let's have a zoom meeting!

## What problem does this library solve?

iDDC modeling is quite a complex workflow and Quetzal-CRUMBS allows to simplify things a lot.

For example, to estimate the current habitat of a species and reconstruct its high-resolution dynamics along the last 21.000 years (averaged across 4 different ML classifiers), with a nice visualization at the end, you can simply use these 3 bash commands:

```bash
python3 -m crumbs.get_gbif \
      --species "Heteronotia binoei" \
      --points test_points/test_points.shp \
      --all \
      --year "1950,2022" \
      --margin 2.0

python3 -m crumbs.sdm \
      --points occurrences.shp \
      --variables bio \
      --background 1000 \
      --times $(seq -s ',' -50 1 20)

python3 -m crumbs.animate sdm_outputs/suitability.tiff
```
-------------------------------------------------------------------------------
# :game_die: Sampling model parameters in a prior distribution


* Sampling integers (*e.g.*, population size): `N=$(python3 -m crumbs.sample "uniform_integer" 10 1000)`
* Sampling double (*e.g.*, probability): `p=$(python3 -m crumbs.sample "uniform_real" 0.0001 0.1)`
* Sampling a coordinate uniformly at random in a geotiff file:
    * `latlon=($(python3 -m crumbs.sample "uniform_latlon" "file.tif" | tr -d '[],'))`
    * get latitude with `${latlon[0]}`
    * get longitude with `${latlon[1]}`

-------------------------------------------------------------------------------
# :inbox_tray: Get CHELSA-Trace21k: 1km climate time series since the LGM

High resolution, downscaled climate model data are central to iDDC modeling. [The CHELSA-TraCE21k downscaling algorithm](https://chelsa-climate.org/chelsa-trace21k/) is particularly relevant to the iDDC modeling field, as it provides:

- global monthly climatologies for temperature and precipitation at 30 arcsec spatial resolution in 100 year time steps for the last 21,000 years.
- paleo orography at high spatial resolution for each timestep

Quetzal-CRUMBS allows to download Geotiff files from this database, selecting the variables and time-steps of interest, possibly clipping the (heavy) worldwide data to the spatial extent of your choice to reduce disk usage, and assemble them into multi-band GeoTiff files than can be processed by other *crumbs* or by *Quetzal-EGGS* simulators :egg::egg::egg:

## :spiral_notepad: Get times series using URL files

> :bulb: If manual selection of the data of interest is cumbersome (too many variables, too many timesteps), you may want to refer to further sections for downloading entire variables for large time sequences

Go to the [CHELSA-Trace21k website](https://envicloud.wsl.ch/#/?prefix=chelsa%2Fchelsa_V1%2Fchelsa_trace%2F), select multiple files via the check-boxes, download the URL file `envidatS3paths.txt`. This file contains a list of URLs that point to the GeoTiff files you want to download. You could use `wget` bash tool, or if you want to use *crumbs* utilities, you can do the following:

  - :globe_with_meridians: **Get worlwide data**: \
  `python3 -m crumbs.get_chelsa.py --input envidatS3paths.txt`
  - :scissors: **Crop the data using the bounding box of your sampling points:** \
  `python3 -m crumbs.get_chelsa.py -i envidatS3paths.txt --points points.shp`
  - :framed_picture: **Same, but adds a buffer of 1 degree (111km) around the bounding box:** \
  `python3 -m crumbs.get_chelsa.py -i envidatS3paths.txt -p points.shp --margin 1.0`
  - :wastebasket: **Same, but erases intermediary worlwide files to save disk space** \
  `python3 -m crumbs.get_chelsa.py -i envidatS3paths.txt -p points.shp -m 1.0 --cleanup`

>:bulb: You can specify the directory where to save raw CHELSA datasets with the option `-d` or `--dir`. Default is `CHELSA`.
>
>:bulb: You can specify the directory where to save clipped CHELSA datasets with the option `-c` or `--clip_dir`. Default is `CHELSA_clipped`.
>
>:bulb: By default, the `get_chelsa` function produces `stacked.tif` multi-band GeoTiff files for each variable selected, ranked from the past (first band) to the present (last band). You can rename them using the `-o` or `--geotiff` option.

## :mountain: Get Digital Elevation Model ('dem')

Digital Elevation Models allow to incorporate sea level variations in the landscape simulation, allowing for better explanation of the population dynamics and patterns of genetic variations near coastlines and islands systems:

- **Download present time (timeID=20) and LGM (timeID=-199) data:**\
`python3 -m crumbs.get_chelsa.py -p my_sampling_points.shp --variables dem -timesID 20,-199`
- **Download a sequence of timesteps:**\
`python3 -m crumbs.get_chelsa.py -p my_sampling_points.shp -v dem -t $(seq -s ',' -50 1 20)`

| Example | Output       |
| --------------| --------------------|
| Sea level rising on the North coast of Australia from -5000 to 1990. <pre> python3 -m crumbs.get_chelsa.py    \ <br> &emsp;        -p my_sampling_points.shp \ <br> &emsp;        -v dem                    \ <br> &emsp;        -t $(seq -s ',' -50 1 20) \ <br> &emsp;        --geotiff my_elevation.tif <br> python3 -m crumbs.animate my_elevation.tif -o my_dem.gif <br> </pre> | <img src="https://github.com/Becheler/quetzal-CRUMBS/blob/media/dem_dynamic.gif?raw=True" width="250" height="250"/> |


## :mountain_snow: Get Glacier Elevation ('glz')

When studying let's say alpine plants, embedding glacier dynamics into the simulation can provide important insights
on the species past dynamics.

- **Add glacier elevation to the list of variables:**\
`python3 -m crumbs.get_chelsa.py -p my_sampling_points.shp ---v dem,glz -t $(seq -s ',' -50 1 20)`

## :sun_behind_rain_cloud: Get Bioclimatic variables ('bio')

Bioclimatic variables are of fundamental importance for species distribution modeling, an important step of the iDDC method. You can use the present bioclimatic variables to model the niche of the species based on present distributional data, and then project the model on past bioclimatic values to get a sense of the probable suitable areas for the species.

- **Add bio01 to the list of variables:**\
`python3 -m crumbs.get_chelsa.py -p my_sampling_points.shp ---v dem,glz,bio01 -t $(seq -s ',' -50 1 20)`

- **Add all bioclimatic variables to the list:**\
`python3 -m crumbs.get_chelsa.py -p my_sampling_points.shp ---v dem,glz,bio -t $(seq -s ',' -50 1 20)`

-------------------------------------------------------------------------------
# :art: Landscape manipulation

## :scissors: Cutting a circular landscape

> :bulb: When you begin to rotate and rescale landscapes, you can end up with quite counter-intuitive orientations that are not very convenient.  
To facilitate landscape manipulation and analysis, we implemented a function that fits and cuts a circle with maximal radius around the landscape center:

* **Default settings:** generates a `disk.tif` file    
`python3 -m crumbs.circle_mask input.tif`
* **Change the output name:**  
`python3 -m crumbs.circle_mask input.tif -o masked_output.tif`

| Example | Output       |
| --------------| --------------------|
| Sea level rising on the North coast of Australia from -5000 to 1990. <pre>python3 -m crumbs.get_chelsa.py    \ <br> &emsp;        -p my_sampling_points.shp \ <br> &emsp;        -v dem                    \ <br> &emsp;        -t $(seq -s ',' -50 1 20) \ <br> &emsp;        --geotiff my_dem.tif  <br>python3 -m crumbs.circle_mask my_dem.tif -o my_circle.tif <br>python3 -m crumbs.animate my_circle.tif -o my_anim.gif <br> </pre> | <img src="https://github.com/Becheler/quetzal-CRUMBS/blob/media/my_circular_landscape.gif?raw=True" width="250" height="250"/> |

## :globe_with_meridians: Sampling spatial grid parameters

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

### :arrows_counterclockwise: Rotating the spatial grid

* Sample a rotation angle about the center in a prior distribution:  
  `angle=$(python3 -m crumbs.sample "uniform_real" 0.0 360.0)`
* Then you can call the `rotate_and_rescale` function:  
    * **Default:** generates a `rotated.tif` file with no resolution change (scale=1)   
    `python3 -m crumbs.rotate_and_rescale input.tif $angle`
    * **Change the output name:**  
    `python3 -m crumbs.resample input.tif $angle $factor -o out.tif`

### :mag_right: Rescaling the grid resolution

* Sample a rescaling factor in a prior distribution:  
`scale=$(python3 -m crumbs.sample "uniform_real" 0.5 2)`
* Perform the rescaling with no rotation (angle=0):  
 `python3 -m crumbs.rotate_and_rescale input.tif 0.0 $scale`
* Perform the rescaling with a rotation:
`python3 -m crumbs.rotate_and_rescale input.tif $angle $scale`

>  :open_book:   
>*Upsampling*: converting to higher resolution/smaller cells (scale > 1)  
    *Downsampling*: converting to lower resolution/larger cell (scale < 1)  

## :hourglass_flowing_sand: Temporal interpolation

> :bulb: You typically don't have a raster whose number of bands (*i.e.*, layers) that conveniently matches the number
of generations of the simulation. Instead, iDDC studies have focused on using a limited number of bands to represent the landscape temporal variance, mapping them to classes of events in a quite cumbersome way.
>
>*e.g.*, using 3 bands: *present*, *past*, *distant_past* :black_large_square: :black_medium_square: :black_small_square: and mapping them to time periods
>
> :gift: But because Quetzal-CoaTL embeds the GDAL library, it allows much more granularity in
the way to represent the landscape. With the `interpolate` function, you can:  
- assign existing bands to the generations of your choice:
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
# :desert: Species Distribution Modeling

> :bulb: Species Distribution Modeling (SDM, also known as ENM: Environmental Niche Modeling)
> is an important step of iDDC modeling. In its correlative version, these models
> use presence locations of a species to draw correlations between these coordinates
> and the value of environmental variables (climate, soil type, vegetation type)
> at these positions. The end result generally consists of some prediction of
> the habitat suitability over the landscape.

The main steps are generally the following:
1. Retrieve observational (presence) data (longitude/latitude)
2. Sample environmental variables at the presence coordinates.
3. Use a statistical model (e.g., SK-Learn classifiers) to build a mathematical relationship between the species and its environment preferences
4. Map the species–environment relationship across the study area (interpolation).
5. Project to past climates (extrapolation)

## :earth_africa: Get presence data with GBIF

> :bulb: Obtaining observational data are the first step of any SDM/ENM. For conveniency, the crumbs
> `get_gbif` function can be used to fetch observations that fall in the area of your choice (generally specified by the extent
> of your sampling points plus a margin), in time period of your choice.

* Look for for occurrences that falls in the bounding box defined by spatial points (plus a margin of 2 degrees), but don't fetch anything:\
`python3 -m crumbs.get_gbif --species "Heteronotia binoei" --points sampling_points.shp --margin 2`
* Fetch all occurrences that falls in the bounding box and save the data of interest (longitude, latitude, year) in a `occurrences.csv` file (for human reading) and in a `occurences.shp` shapefile (for further geospatial processing):\
`python3 -m crumbs.get_gbif -s "Heteronotia binoei" -p sampling_points.shp -m 2 --all`
* Fetch a max of 50 occurrences that falls in the bounding box:\
`python3 -m crumbs.get_gbif -s "Heteronotia binoei" -p sampling_points.shp -m 2 --limit 50`
* Fetch a max of 50 occurrences that falls in the bounding box in the time range specified:\
`python3 -m crumbs.get_gbif -s "Heteronotia binoei" -p sampling_points.shp -m 2 -l 50 --year "1950,2022"`
* Fetch all occurrences between 1950 and 2022:\
`python3 -m crumbs.get_gbif -s "Heteronotia binoei" -p spatial_points.shp -m 2 --year "1950,2022" --all`

<div align="center">

| <img src="https://github.com/Becheler/quetzal-CRUMBS/blob/media/animation_dem_gbif_3D.gif?raw=True" width="350" height="350"/> |
|:--:|
| [*Animation generated with quetzal-CRUMBS animate*](#animating-gbif-data) |

</div>

## :checkered_flag: Perform full SDM analysis

For example, to :
1. Estimate the current habitat of a species
2. Reconstruct the high-resolution habitat dynamics along the last 21.000 years
3. Average the results across 4 different ML classifiers
4. Get a nice visualization at the end,
you can simply use this bash commands:

```bash
python3 -m crumbs.sdm \
      --points occurrences.shp \
      --variables bio \
      --background 1000 \
      --times $(seq -s ',' -199 1 20)
```

-------------------------------------------------------------------------------
# :film_strip: Visualizations

## 2D rendering

>:bulb: The `animate` function facilitates visual checks of the impact of landscape features or other parameters on the simulation:
> - If you have a multi-band raster representing a dynamic landscape (*e.g.,* using `get_chelsa` or `crumbs.interpolate`),
> you can easily perform a visual check of the landscape dynamics before to run the simulations
> - If you chose to log the demographic history from Quetzal-EGGS programs (option `log-history=history.tif` in the EGG configuration
> file), then you can convert it into an animation using CRUMBS.

- The `animate` function can be called with the following:
    * **Default settings:** generates an animated gif    
    `python3 animate.py input.tif`
    * **Change the output format:** detects the mp4 extension and converts accordingly    
    `python3 animate.py  input.tif -o "output.mp4"`
    * **Change the colorbar cap value:** if none is given then the max value is inferred from the multiband raster):  
    `python3 animate.py input.tif" --vmax 100`
    * **Combination of the previous:**  
    `python3 animate.py input.tif -o output.mp4 --vmax 100`


## 3D rendering with Digital Elevation model

>:bulb: There is nothing better than a 3D animation to get a better sense of the
landscape you are simulating! The `--DDD` options allows you to produce high-quality
graphic that are automatically converted to a gif or a mp4.
Because usually the elevation values (in meter) along the z axis are much higher than
the values along the longitudinal and latitudinal axis (in degree), you may want
to rescale the z axis by a factor using the `--warp-scale` option (shorter `-w`).

 `python3 animate.py input.tif -o output.mp4 --DDD --warp_factor 0.3`


## Animating GBIF data

> :bulb: For presentation, blogging, tweeting or broader communication purposes, it's always nice to give to your audience an
> intuition of the observations dynamics over space and time. We implemented some
> utilities for this purpose!  
> The `animate` function can be called with an **elevation file** (see `crumbs.get_chelsa`, DEM) and an **occurrences file** (see `crumbs.get_gbif`) with the option `--gbif` (short option `-g`). Since relevant GBIF data are
most of the time modern, the elevation is considered constant during the animation, and only the last
CHELSA layer (ie, modern times) of the tiff file is used to display the obsevations.

* **2D rendering:**  
  * **Defaults:** plot observations through time on a 2D landscape, older observations fading over time:\
 `python3 -m crumbs.animate dem.tif -g occurrences.shp`
  * **Change the output format:** detects the mp4 extension and converts accordingly:\
 `python3 animate.py  crumbs.animate dem.tif -g occurrences.shp -o "output.mp4"`
* **3D rendering:**  
  * Plot the raw elevation data and displays the GBIF observations on top of it:\
  `python3 -m crumbs.animate dem.tif -g occurrences.shp --DDD`
  * The elevation values can be rescaled with `--warp_scale`, `-w`:\
  `python3 -m crumbs.animate dem.tif -g occurrences.shp --DDD --warp_scale 0.1`
  * Performs a triangulation of the elevation surface using n triangles given by the `--triangles`, `-t` options for a smoother surface:\
  `python3 -m crumbs.animate dem.tif -g occurrences.shp --DDD --triangles 5000`
  * **Combination of the previous:** \
  `python3 animate.py dem.tif -g occurences.shp -o output.mp4 --DDD -w 0.1 -t 5000`

  | Examples | Output       |
  | --------------| --------------------|
  | Elevation and GBIF occurrences over time<pre>crumbs.animate dem.tif -g occurences.shp <br> </pre> | <img src="https://github.com/Becheler/quetzal-CRUMBS/blob/media/animation_dem_gbif_2D.gif?raw=True" width="250" height="250"/> |
  | Same, but 3D and rescaled<pre>crumbs.animate dem.tif -g occ.shp --DDD -w 0.1 <br> </pre> | <img src="https://github.com/Becheler/quetzal-CRUMBS/blob/media/animation_dem_gbif_3D_no_triangle.gif?raw=True" width="250" height="250"/> |
  | Same, but triangulated<pre>crumbs.animate dem.tif -g occ.shp --DDD -w 0.1 -t 5000 <br> </pre> | <img src="https://github.com/Becheler/quetzal-CRUMBS/blob/media/animation_dem_gbif_3D.gif?raw=True" width="250" height="250"/> |

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
