# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import pytest

from . context import crumbs

from crumbs.chelsa.request import request

class TestGetChelsa():

    output_filename = "chelsa-stacked"
    world_file_dir = "chelsa-world"
    cropped_file_dir = "chelsa-cropped"

    def setup_method(self, test_method):
        pass

    def teardown_method(self, test_method):
        from pathlib import Path
        import glob

        # Remove all chelsa stacked files generated
        for p in Path(".").glob( self.output_filename + "*.*"):
            p.unlink()

        # Remove all chelsa world files generated
        for p in Path(self.world_file_dir).glob("*.tif"):
            p.unlink()
        Path(self.world_file_dir).rmdir()

        # Remove all chelsa cropped files generated
        for p in Path(self.cropped_file_dir).glob("*.tif"):
            p.unlink()
        Path(self.cropped_file_dir).rmdir()


    @pytest.mark.slow
    def test_get_chelsa_with_input_file(self):
        request(inputFile = "tests/data/chelsa_url_test.txt",
                              points = "tests/data/test_points/test_points.shp")

    @pytest.mark.slow
    def test_get_chelsa_with_no_input_file(self):
        request(points = "tests/data/test_points/test_points.shp",
                              variables = ['dem'],
                              timesID = [20])

    @pytest.mark.slow
    def test_get_chelsa_with_time_range(self):
        request(points = "tests/data/test_points/test_points.shp",
                              variables = ['bio01'],
                              timesID = [0, -1])
