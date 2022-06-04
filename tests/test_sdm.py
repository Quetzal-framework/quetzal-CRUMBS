# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys

from . context import crumbs

from . utils import delete_folder

class TestSDM(unittest.TestCase):

    def setUp(self):
        self.sampling_points = "tests/data/test_points/test_points.shp"
        self.occurrences_filename = "occurrences"

    @unittest.skip("Too slow on circle CI")
    def test_fit_and_extrapolate(self):

        from crumbs.sdm.sdm import SDM
        from crumbs.get_gbif import search_gbif
        import pickle

        search_gbif(scientific_name='Heteronotia binoei',
                             points=self.sampling_points,
                             margin=1.0,
                             all=False,
                             limit=50,
                             year='1950,2022',
                             csv_file= self.occurrences_filename + ".csv",
                             shapefile= self.occurrences_filename + ".shp")

        my_sdm = SDM(
            scientific_name='Heteronotia binoei',
            presence_shapefile = self.occurrences_filename + ".shp",
            nb_background_points = 30,
            variables = ['dem','bio01'],
            chelsa_time_IDs = [20],
            buffer = 1.0
            )

        my_sdm.fit_on_present_data()

        with open("my_sdm.bin","wb") as f:
            pickle.dump(my_sdm, f)

        with open("my_sdm.bin","rb") as f:
            my_saved_sdm = pickle.load(f)
            my_saved_sdm.load_classifiers_and_extrapolate(20)

    def tearDown(self):
        from pathlib import Path
        import glob

        # Removing all occurrences files generated
        for p in Path(".").glob( self.occurrences_filename + ".*"):
            p.unlink()

        # Removing sdm pickled
        Path("my_sdm.bin").unlink()

        # Removing SDM input and outputs folder
        delete_folder(Path("chelsa-landscape"))
        delete_folder(Path("model-persistence"))
        delete_folder(Path("model-averaging"))
        delete_folder(Path("model-imputation"))

if __name__=="__main__":
    unittest.main()
