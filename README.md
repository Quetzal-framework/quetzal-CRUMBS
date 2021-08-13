# quetzal-CRUMBS

General utility scripts for Quetzal projects

# Updating the package

  * create a *feature* branch, make updates to it.
  * Create tests for it
  * Bump the version in setup.py
  * Bump the version of the whl file in the CircleCI config file
  * Update the ChangeLog
  * Push to GitHub

When you have a successful build, create a GitHub Pull Request (PR) to the develop branch. If it looks good, merge it. When that build succeeds, create a PR to the main branch, review it, and merge.
# Usage

## To visualize the parameter space:

What parameters lead to simulation that failed?

```
ids=$(python3 -m crumbs.get_simulations_ID "output.db", "quetzal_EGG_1", failed=True)
```
What parameters lead to successful simulations?
```
ids=$(python3 -m crumbs.get_simulations_ID "output.db", "quetzal_EGG_1", failed=False)
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

## Dependencies

### GDAL/OGR for Python:

- [Ubuntu installation](https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html)
