# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys
sys.path.append("..")

def delete_folder(pth) :
    import pathlib

    for sub in pth.iterdir() :
        if sub.is_dir() :
            delete_folder(sub)
        else :
            sub.unlink()
    pth.rmdir() # if you just want to delete the dir content but not the dir itself, remove this line


class TestSDM(unittest.TestCase):

    def setUp(self):

        from src.crumbs.sdm import SDM
        from src.crumbs.get_gbif import search_gbif

        self.sampling_points = "data/test_points/test_points.shp"
        self.occurrences_filename = "occurrences"

        search_gbif(scientific_name='Heteronotia binoei',
                             points=self.sampling_points,
                             margin=1.0,
                             all=False,
                             limit=50,
                             year='1950,2022',
                             csv_file= self.occurrences_filename + ".csv",
                             shapefile= self.occurrences_filename + ".shp")


        self.sdm = SDM(
            scientific_name='Heteronotia binoei',
            presence_shapefile = self.occurrences_filename + ".shp",
            nb_background_points = 30,
            variables = ['dem','bio01'],
            chelsa_time_IDs = [20,19],
            buffer = 1.0
            )

    def test_fit_sdm(self):
        self.sdm.fit_on_present_data()

    def test_extrapolate(self):
        self.sdm.load_classifiers_and_extrapolate(20)
        self.sdm.load_classifiers_and_extrapolate(19)

    def tearDown(self):
        from pathlib import Path
        import glob

        # Removing all occurrences files generated
        for p in Path(".").glob( self.occurrences_filename + ".*"):
            p.unlink()

        # Removing all persistence files generated
        for p in Path(".").glob( "persist-" + "*.joblib"):
            p.unlink()

        # Removing SDM input and outputs folder
        # delete_folder(Path("sdm_inputs"))
        # delete_folder(Path("sdm_outputs"))
        # delete_folder(Path(self.cropped_file_dir))

if __name__=="__main__":
    unittest.main()
