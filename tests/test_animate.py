# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys
sys.path.append("..")

from src.crumbs import animate

class TestAnimate(unittest.TestCase):

    demographic_tiff = "data/EGG2_short_history.tif"
    elevation_tiff = "data/DEM_5_bands.tif"
    gbif_files = "data/occurrences.shp"

    output_filename = "animation"

    def SetUp(self):
        pass

    def test_2D_animation_on_demographic_file(self):
        animate.chose_method(inputRaster=self.demographic_tiff)
        animate.chose_method(inputRaster=self.demographic_tiff, vmax=500)
        animate.chose_method(inputRaster=self.demographic_tiff, vmax=500, output=self.output_filename+".mp4")

    def test_3D_default_on_elevation_file(self):
        animate.chose_method(inputRaster=self.elevation_tiff,
                            vmin=None,
                            vmax=None,
                            output=None,
                            gbif_occurrences=None,
                            DDD=True,
                            warp_scale=1.0,
                            nb_triangles=None)

    def test_3D_with_elevation_rescaled(self):
        animate.chose_method(inputRaster=self.elevation_tiff,
                            vmin=None,
                            vmax=None,
                            output=None,
                            gbif_occurrences=None,
                            DDD=True,
                            warp_scale=0.1,
                            nb_triangles=None)

    def test_3D_with_elevation_rescaled_and_triangulated(self):
        animate.chose_method(inputRaster=self.elevation_tiff,
                            vmin=None,
                            vmax=None,
                            output=None,
                            gbif_occurrences=None,
                            DDD=True,
                            warp_scale=0.1,
                            nb_triangles=1000)


    def test_3D_with_elevation_rescaled_and_triangulated_and_bif_data_display(self):
        animate.chose_method(inputRaster=self.elevation_tiff,
                            vmin=None,
                            vmax=None,
                            output=None,
                            gbif_occurrences=self.gbif_files,
                            DDD=True,
                            warp_scale=0.1,
                            nb_triangles=1000)

    def tearDown(self):
        from pathlib import Path
        import glob
        # Removing all occurrences files generated
        for p in Path(".").glob( self.output_filename + ".*"):
            p.unlink()

if __name__=="__main__":
    unittest.main()
