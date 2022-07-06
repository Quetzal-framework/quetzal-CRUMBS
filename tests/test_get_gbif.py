import pytest

from crumbs.gbif.request import request

from .context import crumbs


class TestGetGbif:
    output_filename = "occurrences"

    def setup_method(self, test_method):
        pass

    def test_request_gbif(self):

        request(
            scientific_name="Heteronotia binoei",
            points="data/test_points/test_points.shp",
            buffer=1.0,
            all=False,
            limit=50,
            year="1950,2022",
            csv_file=self.output_filename + ".csv",
            shapefile=self.output_filename + ".shp",
        )

        request(
            scientific_name="Heteronotia binoei",
            points="data/test_points/test_points.shp",
            buffer=1.0,
            all=False,
            year="1950,2022",
            limit=50,
            csv_file=self.output_filename + ".csv",
            shapefile=self.output_filename + ".shp",
        )

    def teardown_method(self, test_method):
        import glob
        from pathlib import Path

        # Removing all occurrences files generated
        for p in Path(".").glob(self.output_filename + ".*"):
            p.unlink()
