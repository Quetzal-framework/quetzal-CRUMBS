import pytest

from .context import crumbs
from .utils import delete_folder


@pytest.mark.slow
def test_fit_and_extrapolate(tmp_path):

    import pickle

    from crumbs.gbif.request import request
    from crumbs.sdm.sdm import SDM

    # Input
    sampling_points = "data/test_points/test_points.shp"
    # Outputs
    csv = tmp_path / "occurrences.csv"
    shp = tmp_path / "occurrences.shp"
    pickled = tmp_path / "my_sdm.bin"

    request(
        scientific_name="Heteronotia binoei",
        points=sampling_points,
        buffer=1.0,
        all=False,
        limit=50,
        year="1950,2022",
        csv_file=csv,
        shapefile=shp,
    )

    my_sdm = SDM(
        scientific_name="Heteronotia binoei",
        presence_shapefile=shp,
        nb_background_points=30,
        variables=["dem", "bio01"],
        buffer=1.0,
        outdir=tmp_path / "SDM/",
    )

    my_sdm.fit_on_present_data()

    with open(pickled, "wb") as f:
        pickle.dump(my_sdm, f)

    with open(pickled, "rb") as f:
        my_saved_sdm = pickle.load(f)
        my_saved_sdm.load_classifiers_and_extrapolate(20)
