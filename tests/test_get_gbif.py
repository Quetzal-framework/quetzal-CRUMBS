# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys
sys.path.append("..")
# from src.crumbs import my_module

from src.crumbs import get_gbif

class TestGetGbif(unittest.TestCase):
    output_filename = "occurrences"

    def SetUp(self):
        pass

    def test_get_gbif(self):

        get_gbif.search_gbif(scientific_name='Heteronotia binoei',
                             points="data/test_points/test_points.shp",
                             margin=1.0,
                             all=False,
                             limit=50,
                             year='1950,2022',
                             csv_file= self.output_filename + ".csv",
                             shapefile= self.output_filename + ".shp")

        get_gbif.search_gbif(scientific_name='Heteronotia binoei',
                             points="data/test_points/test_points.shp",
                             margin=1.0,
                             all=False,
                             year='1950,2022',
                             limit=50,
                             csv_file= self.output_filename + ".csv",
                             shapefile= self.output_filename + ".shp")

    def tearDown(self):
        from pathlib import Path
        import glob
        # Removing all occurrences files generated
        for p in Path(".").glob( self.output_filename + ".*"):
            p.unlink()

if __name__=="__main__":
    unittest.main()
