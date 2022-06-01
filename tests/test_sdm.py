# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys

from .context import src.crumbs
from .utils import delete_folder

class TestSDM(unittest.TestCase):

    def setUp(self):
        self.sampling_points = "data/test_points/test_points.shp"
        self.occurrences_filename = "occurrences"

    def test_fit_and_extrapolate(self):

        from src.crumbs.sdm import SDM
        from src.crumbs.get_gbif import search_gbif



        search_gbif(scientific_name='Heteronotia binoei',
                             points=self.sampling_points,
                             margin=1.0,
                             all=False,
                             limit=50,
                             year='1950,2022',
                             csv_file= self.occurrences_filename + ".csv",
                             shapefile= self.occurrences_filename + ".shp")


        sdm = SDM(
            scientific_name='Heteronotia binoei',
            presence_shapefile = self.occurrences_filename + ".shp",
            nb_background_points = 30,
            variables = ['dem','bio01'],
            chelsa_time_IDs = [20,19],
            buffer = 1.0
            )

        sdm.fit_on_present_data()
        sdm.load_classifiers_and_extrapolate(20)
        sdm.load_classifiers_and_extrapolate(19)

    def tearDown(self):
        from pathlib import Path
        import glob

        # Removing all occurrences files generated
        for p in Path(".").glob( self.occurrences_filename + ".*"):
            p.unlink()

        # Removing all persistence files generated
        for p in Path(".").glob( "model-persistence" + "*.joblib"):
            p.unlink()

        # Removing all landscape files generated
        for p in Path(".").glob( "chelsa-landscape" + "*.tif"):
            p.unlink()

        # Removing SDM input and outputs folder
        delete_folder(Path("model-averaging"))
        delete_folder(Path("model-imputation"))

if __name__=="__main__":
    unittest.main()
