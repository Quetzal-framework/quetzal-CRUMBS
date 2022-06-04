#!/bin/bash

# exit when any command fails
set -e

sample='data/test_points/test_points.shp'
buffer=2.0
biovars=dem,bio01

crumbs-get-gbif \
      --species "Heteronotia binoei" \
      --points $sample \
      --limit 30 \
      --year "1950,2022" \
      --margin $buffer \
      --output occurrences
