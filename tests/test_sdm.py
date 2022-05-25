# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys
sys.path.append("..")

from src.crumbs import sdm_fit
from src.crumbs import get_gbif

class TestSDM(unittest.TestCase):

    sampling_points = "data/test_points/test_points.shp"
    occurrences_filename = "occurrences"
    output_filename = "chelsa-stacked"
    world_file_dir = "chelsa-world"
    cropped_file_dir = "chelsa-cropped"

    def SetUp(self):
        pass

    def test_get_chelsa_with_input_file(self):

        get_gbif.search_gbif(scientific_name='Heteronotia binoei',
                             points=self.sampling_points,
                             margin=1.0,
                             all=False,
                             limit=50,
                             year='1950,2022',
                             csv_file= self.occurrences_filename + ".csv",
                             shapefile= self.occurrences_filename + ".shp")

        sdm_fit.fit_species_distribution_model(
            presence_shp = self.occurrences_filename + ".shp",
            background_points = 30,
            timeID = 20,
            variables = ["dem","bio01"],
            margin = 1.0,
            output = "suitability.tif",
            persist = True,
            cleanup = True,
            crop_dir = self.cropped_file_dir
            )




if __name__=="__main__":
    unittest.main()
