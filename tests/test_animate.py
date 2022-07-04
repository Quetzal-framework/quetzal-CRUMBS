import pytest

from . context import crumbs

from crumbs.gis.animate import chose_method


def test_2D_animation_on_demographic_file(tmp_path):

    demographic_tiff = "data/EGG2_short_history.tif"

    d = tmp_path / "animation"
    d.mkdir()

    filename = d / "demography.mp4"

    chose_method(inputRaster=demographic_tiff, output=filename)
    chose_method(inputRaster=demographic_tiff, vmax=500, output=filename)


def test_3D_default_on_elevation_file(tmp_path):

    elevation_tiff = "data/DEM_5_bands.tif"

    d = tmp_path / "animation"
    d.mkdir()

    filename = d / "elevation.mp4"

    chose_method(inputRaster=elevation_tiff,
                        vmin=None,
                        vmax=None,
                        output=filename,
                        gbif_occurrences=None,
                        DDD=True,
                        warp_scale=1.0,
                        nb_triangles=None)

def test_3D_with_elevation_rescaled(tmp_path):

    elevation_tiff = "data/DEM_5_bands.tif"

    d = tmp_path / "animation"
    d.mkdir()

    filename = d / "elevation_rescaled.mp4"

    chose_method(inputRaster=elevation_tiff,
                        vmin=None,
                        vmax=None,
                        output=filename,
                        gbif_occurrences=None,
                        DDD=True,
                        warp_scale=0.1,
                        nb_triangles=None)

def test_3D_with_elevation_rescaled_and_triangulated(tmp_path):

    elevation_tiff = "data/DEM_5_bands.tif"

    d = tmp_path / "animation"
    d.mkdir()

    filename = d / "elevation_triangulated.mp4"

    chose_method(inputRaster=elevation_tiff,
                        vmin=None,
                        vmax=None,
                        output=filename,
                        gbif_occurrences=None,
                        DDD=True,
                        warp_scale=0.1,
                        nb_triangles=1000)

def test_3D_with_elevation_rescaled_and_triangulated_and_bif_data_display(tmp_path):

    elevation_tiff = "data/DEM_5_bands.tif"
    gbif_files = "data/occurrences.shp"

    d = tmp_path / "animation"
    d.mkdir()

    filename = d / "elevation_gbif.mp4"

    chose_method(inputRaster=elevation_tiff,
                        vmin=None,
                        vmax=None,
                        output=filename,
                        gbif_occurrences=gbif_files,
                        DDD=True,
                        warp_scale=0.1,
                        nb_triangles=1000)
