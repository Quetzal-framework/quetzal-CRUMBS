# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys

from . context import crumbs
from crumbs import bpp

class TestBPP(unittest.TestCase):
    def SetUp(self):
        pass

    def test_nb_species_posterior_probabilities(self):

        from pathlib import Path
        import math

        string = Path('tests/data/bpp_output.txt').read_text()
        posterior = bpp.nb_species_posterior_probabilities(string)

        assert math.isclose(posterior[1], 0.0)
        assert math.isclose(posterior[2], 0.985)

if __name__=="__main__":
    unittest.main()
