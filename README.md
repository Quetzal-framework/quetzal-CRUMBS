# Quetzal-CRUMBS <img align="right" width="200" src="https://github.com/Becheler/Becheler.github.io/blob/master/draw/logos/quetzal_crumbs.png">

[![Becheler](https://circleci.com/gh/Becheler/quetzal-CRUMBS.svg?style=shield)](https://app.circleci.com/pipelines/github/Becheler)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Website becheler.github.io](https://img.shields.io/website-up-down-green-red/https/becheler.github.io.svg)](https://becheler.github.io/pages/quetzal_crumbs/home)

General utility scripts for the Quetzal framework projects

# Usage in bash

## Sampling parameters in prior distribution:

Sampling integers (eg population size): `N=$(python3 -m crumbs.sample "uniform_integer" 10 1000)`
-------------------------------------------
Sampling double (eg probability): `p=$(python3 -m crumbs.sample "uniform_real" 0.0001 0.1)`
---------------------------------------------------------
Sampling coordinate in a landscape (geotiff): `latlon=($(python3 -m crumbs.sample "uniform_latlon" "suitability.tif" | tr -d '[],'))`
* get latitude with `${latlon[0]}`
* get longitude with `${latlon[1]}`
--------------------------------------------------------
## To visualize the parameter space:

What parameters lead to simulation that failed?

```
ids=$(python3 -m crumbs.get_simulations_ID "output.db", "quetzal_EGG_1", failed=True)
```
What parameters lead to successful simulations?
```
ids=$(python3 -m crumbs.get_simulations_ID "output.db", "quetzal_EGG_1", failed=False)
```
```
for i in ids
do
  s=$(python3 -m crumbs.sample "uniform_real" 0.00025 0.0000025)

  python3 -m crumbs.simulate_sequences \
  --database "output.db" \
  --table "quetzal_EGG_1" \
  --rowid $i\
  --sequence_size 1041  \
  --scale_tree $s \
  --output "pods/phylip/EGG1_pod_"$i".phyl"

  python3 -m crumbs.phylip2arlequin \
  --input "pods/phylip/EGG1_pod_"$i".phyl" \
  --imap "imap.txt" \
  --output "pods/arlequin/EGG1_pod_"$i".arp"

  if [ $i -eq 1 ]; then
      ./arlsumstat3522_64bit "pods/arlequin/EGG1_pod_"$i".arp" outSS 0 1 run_silent
   else
      ./arlsumstat3522_64bit "pods/arlequin/EGG1_pod_"$i".arp" outSS 1 0 run_silent
   fi
   rm "pods/arlequin/EGG1_pod_"$i".res" -r
```
# Updating the package

From https://circleci.com/blog/publishing-a-python-package/ :

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
