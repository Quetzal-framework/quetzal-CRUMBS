import pytest

from . context import crumbs
from crumbs import bpp


def test_nb_species_posterior_probabilities():

    from pathlib import Path
    import math

    string = Path('data/bpp_output.txt').read_text()
    posterior = bpp.nb_species_posterior_probabilities(string)

    assert math.isclose(posterior[1], 0.0)
    assert math.isclose(posterior[2], 0.985)
