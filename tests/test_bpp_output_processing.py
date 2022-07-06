import pytest

from crumbs import bpp

from .context import crumbs


def test_nb_species_posterior_probabilities():

    import math
    from pathlib import Path

    string = Path("data/bpp_output.txt").read_text()
    posterior = bpp.nb_species_posterior_probabilities(string)

    assert math.isclose(posterior[1], 0.0)
    assert math.isclose(posterior[2], 0.985)
