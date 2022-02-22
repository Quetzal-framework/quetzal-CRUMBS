import unittest

class TestSequence(unittest.TestCase):
    def SetUp(self):
        pass

    def test_new(self):
        from crumbs import sequence
        s = sequence.Sequence(">HEADER","--ACGT")
        self.assertEqual(s.header,"HEADER")
        self.assertEqual(s.sequence,"--ACGT")

    def test_parse(self):
        from crumbs import sequence
        generator = sequence.fasta_parse("tests/data/sequences.fasta")
        sequences = list(generator)
        self.assertEqual(sequences[0].header, "QWER1")
        self.assertEqual(sequences[0].sequence, "GGCAGATTCCCCCTA")
        self.assertEqual(sequences[1].header, "AZER2")
        self.assertEqual(sequences[1].sequence, "---CTGCACTCACCG")

class TestBPP(unittest.TestCase):
    def SetUp(self):
        pass

    def test_nb_species_posterior_probabilities(self):
        from crumbs import bpp
        from pathlib import Path
        import math
        string = Path('tests/data/bpp_output.txt').read_text()
        posterior = bpp.nb_species_posterior_probabilities(string)
        assert math.isclose(posterior[1], 0.0)
        assert math.isclose(posterior[2], 0.985)

class TestTiff(unittest.TestCase):
    def SetUp(self):
        pass

    def test_rasterIO(self):
        from osgeo import gdal
        import numpy as np
        # Open the file:
        raster = gdal.Open(r'tests/data/suitability.tif')
        # Check type of the variable 'raster'
        type(raster)
        # Projection
        raster.GetProjection()
        # Dimensions
        self.assertEqual(raster.RasterXSize, 216)
        self.assertEqual(raster.RasterYSize, 144)
        # Number of bands
        self.assertEqual(raster.RasterCount, 1)
        # Read the raster band as separate variable
        band = raster.GetRasterBand(1)
        # Compute statistics if needed
        if band.GetMinimum() is None or band.GetMaximum()is None:
            band.ComputeStatistics(0)
        # Fetch metadata for the band
        band.GetMetadata()
        # Print only selected metadata:
        self.assertEqual(band.GetNoDataValue(), -3.4e+38)
        np.testing.assert_almost_equal(band.GetMinimum(), 0.1104118, 6)
        np.testing.assert_almost_equal(band.GetMaximum(), 0.7852693, 6)

    def test_sample_latlon(self):
        from crumbs import sample
        latlon = sample.uniform_latlon("tests/data/suitability.tif", 0)

class TestGetSimulation(unittest.TestCase):
    def SetUp(self):
        pass

    def test_database_IDS(self):
        from crumbs import get_successful_simulations_rowids, get_failed_simulations_rowids
        # Open the file:
        success_rowids = get_successful_simulations_rowids("tests/data/database_with_newicks.db", "quetzal_EGG_1")
        self.assertEqual(success_rowids, list(range(1,31)))
        print(success_rowids)
        failed_rowids = get_failed_simulations_rowids("tests/data/database_failed_newicks.db", "quetzal_EGG_1")
        self.assertEqual(failed_rowids, list(range(1,31)))

    def test_simulate_phylip(self):
        from crumbs import get_successful_simulations_rowids, retrieve_parameters, simulate_phylip_sequences
        rowids = get_successful_simulations_rowids("tests/data/database_with_newicks.db", "quetzal_EGG_1")
        sequence_size = 100
        scale_tree = 0.000025
        print(rowids[0])
        simulate_phylip_sequences("tests/data/database_with_newicks.db", "quetzal_EGG_1", rowids[0], sequence_size, scale_tree, "sim_test.phyl", "sim_test_temp")
        a = retrieve_parameters("tests/data/database_with_newicks.db", "quetzal_EGG_1", rowids[0])
        b = retrieve_parameters("tests/data/database_with_newicks.db", "quetzal_EGG_1", rowids[0], True)
        c = retrieve_parameters("tests/data/database_with_newicks.db", "quetzal_EGG_1", rowids[0], False)
        self.assertEqual(a,b)
        print("With header:\n", a)
        print("No header:\n", c)

class TestConvertPhylipToArlequin(unittest.TestCase):
    def SetUp(self):
        pass

    def test_phylip_to_alequin(self):
        from crumbs import phylip2arlequin
        output = "test.arlequin"
        phylip2arlequin("tests/data/seq.phyl", "tests/data/imap.txt", output)
        with open('test.arlequin', 'r') as f:
            print(f.read())

class TestAnimate(unittest.TestCase):
    def SetUp(self):
        pass

    def test_animate(self):
        from crumbs import animate

        demographic_tiff = "tests/data/EGG2_short_history.tif"
        elevation_tiff = "tests/data/DEM_5_bands.tif"
        gbif_files = "tests/data/occurrences.shp"

        # 2D demographic animation
        animate.chose_method(inputRaster=demographic_tiff)
        animate.chose_method(inputRaster=demographic_tiff, vmax=500)
        animate.chose_method(inputRaster=demographic_tiff, vmax=500, output="animation.mp4")

        # 3D elevation defaults
        animate.chose_method(inputRaster=elevation_tiff, vmin=None, vmax=None, output=None, gbif_occurrences=None, DDD=True, warp_scale=1.0, nb_triangles=None)
        # 3D elevation z rescaled
        animate.chose_method(inputRaster=elevation_tiff, vmin=None, vmax=None, output=None, gbif_occurrences=None, DDD=True, warp_scale=0.1, nb_triangles=None)
        # 3D elevation rescaled & triangulated
        animate.chose_method(inputRaster=elevation_tiff, vmin=None, vmax=None, output=None, gbif_occurrences=None, DDD=True, warp_scale=0.1, nb_triangles=1000)
        # 3D elevation rescaled & triangulated & Gbif
        animate.chose_method(inputRaster=elevation_tiff, vmin=None, vmax=None, output=None, gbif_occurrences=gbif_files, DDD=True, warp_scale=0.1, nb_triangles=1000)


class TestGetChelsa(unittest.TestCase):
    def SetUp(self):
        pass

    def test_get_chelsa(self):
        from crumbs import get_chelsa
        get_chelsa.get_chelsa(inputFile = "tests/data/chelsa_url_test.txt", points = "tests/data/test_points/test_points.shp")
        get_chelsa.get_chelsa(points = "tests/data/test_points/test_points.shp", variables = ['bio01'], timesID = [20, -199])
        get_chelsa.get_chelsa(points = "tests/data/test_points/test_points.shp", variables = ['dem'], timesID = [20])

from crumbs import get_gbif

class TestGetGbif(unittest.TestCase):
    def SetUp(self):
        pass

    def test_get_bif(self):
        get_gbif.search_gbif(scientific_name='Heteronotia binoei', points="tests/data/test_points/test_points.shp", margin=1.0, limit=50, csv_file="occurrences.csv", shapefile="occurrences.shp", all=False, year=None, output=None)
        get_gbif.search_gbif(scientific_name='Heteronotia binoei', points="tests/data/test_points/test_points.shp", margin=1.0, limit=50, csv_file="occurrences.csv", shapefile="occurrences.shp", all=False, year='1950,2022', output=None)


if __name__=="__main__":
    unittest.main()
