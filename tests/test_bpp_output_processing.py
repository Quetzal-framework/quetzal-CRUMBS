import pytest

from . context import crumbs
from crumbs import bpp

class TestBPP():
    def setup_method(self, test_method):
        pass

    def test_nb_species_posterior_probabilities(self):

        from pathlib import Path
        import math

        string = Path('tests/data/bpp_output.txt').read_text()
        posterior = bpp.nb_species_posterior_probabilities(string)

        assert math.isclose(posterior[1], 0.0)
        assert math.isclose(posterior[2], 0.985)
