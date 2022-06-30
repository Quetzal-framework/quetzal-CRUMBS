# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import pytest

from . context import crumbs
from crumbs.chelsa.request import request

@pytest.mark.slow
def test_get_chelsa_with_input_file(tmp_path):

    d1 = tmp_path / 'chelsa-world'
    d1.mkdir()

    d2 = tmp_path / "chelsa-landscape"
    d2.mkdir()

    d3 = tmp_path / "chelsa-stacked"
    d3.mkdir()

    geotiff = d3 / "stacked.tif"

    request(inputFile = "tests/data/chelsa_url_test.txt",
            points = "tests/data/test_points/test_points.shp",
            world_dir=d1,
            landscape_dir=d2,
            geotiff=geotiff
            )

@pytest.mark.slow
def test_get_chelsa_with_no_input_file(tmp_path):

    d1 = tmp_path / 'chelsa-world'
    d1.mkdir()

    d2 = tmp_path / "chelsa-landscape"
    d2.mkdir()

    d3 = tmp_path / "chelsa-stacked"
    d3.mkdir()

    geotiff = d3 / "stacked.tif"

    request(points = "tests/data/test_points/test_points.shp",
            variables = ['dem'],
            timesID = [20],
            world_dir=d1,
            landscape_dir=d2,
            geotiff=geotiff
            )

@pytest.mark.slow
def test_get_chelsa_with_time_range(tmp_path):

    d1 = tmp_path / 'chelsa-world'
    d1.mkdir()

    d2 = tmp_path / "chelsa-landscape"
    d2.mkdir()

    d3 = tmp_path / "chelsa-stacked"
    d3.mkdir()

    geotiff = d3 / "stacked.tif"

    request(points = "tests/data/test_points/test_points.shp",
            variables = ['bio01'],
            timesID = [0, -1],
            world_dir=d1,
            landscape_dir=d2,
            geotiff=geotiff
            )
