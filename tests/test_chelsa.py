# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import pytest

from . context import crumbs
from crumbs.chelsa.request import request

from pathlib import Path
import glob

class TestGetChelsa():

    def setup_method(self, test_method):
        pass

    @pytest.fixture
    def output_filename():
        # before test - create resource
        output_filename = "chelsa-stacked"
        file_path = pathlib.Path(output_filename)
        yield file_path
        # after test - Remove all chelsa stacked files generated
        for p in Path(".").glob( output_filename + "*.*"):
            p.unlink()

    @pytest.fixture
    def world_file_dir():
        # before test - create resource
        world_file_dir = "chelsa-world"
        file_path = pathlib.Path(world_file_dir)
        yield file_path
        # Remove all chelsa world files generated
        for p in Path(world_file_dir).glob("*.tif"):
            p.unlink()

        Path(world_file_dir).rmdir()

    @pytest.fixture
    def cropped_file_dir():
        # before test - create resource
        cropped_file_dir = "chelsa-cropped"
        file_path = pathlib.Path(cropped_file_dir)
        yield file_path
        # Remove all chelsa cropped files generated
        for p in Path(cropped_file_dir).glob("*.tif"):
            p.unlink()

        Path(cropped_file_dir).rmdir()

    @pytest.mark.slow
    def test_get_chelsa_with_input_file(self, output_filename):
        request(inputFile = "tests/data/chelsa_url_test.txt",
                              points = "tests/data/test_points/test_points.shp")

    @pytest.mark.slow
    def test_get_chelsa_with_no_input_file(self, world_file_dir):
        request(points = "tests/data/test_points/test_points.shp",
                              variables = ['dem'],
                              timesID = [20])

    @pytest.mark.slow
    def test_get_chelsa_with_time_range(self, cropped_file_dir):
        request(points = "tests/data/test_points/test_points.shp",
                              variables = ['bio01'],
                              timesID = [0, -1])
