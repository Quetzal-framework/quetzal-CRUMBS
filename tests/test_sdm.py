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

    sampling_points = "data/test_points/test_points.shp"
    occurrences_filename = "occurrences"
    output_filename = "chelsa-stacked"
    world_file_dir = "chelsa-world"
    cropped_file_dir = "chelsa-cropped"

    def SetUp(self):
        pass

    def test_fitting_classifiers(self):

        from src.crumbs import sdm_fit
        from src.crumbs import get_gbif

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

    def test_extrapolating_trained_classifiers_to_past():
        from src.crumbs import sdm

        # sdm.extrapolate_model(joblib, ...)
        sdm.extrapolate_model_to_past_climates(
            model_files=self.model_files,
            timesID = [20,19,18]
            variables = ["dem","bio01"],
            margin = 1.0,
            output = "suitability.tif",
            )

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
        delete_folder(Path("sdm_inputs"))
        delete_folder(Path("sdm_outputs"))
        delete_folder(Path(self.cropped_file_dir))

if __name__=="__main__":
    unittest.main()
