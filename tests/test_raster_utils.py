# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys

from . context import crumbs

class TestTiff(unittest.TestCase):

    def SetUp(self):
        pass

    def test_rasterIO(self):

        from osgeo import gdal
        import numpy as np

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

if __name__=="__main__":
    unittest.main()
