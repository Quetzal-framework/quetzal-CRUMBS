
from . utils import (
    bounds_to_polygon,
    expand_bio,
    generate_urls,
    read_urls,
    retrieve_variable_names_from,
    get_filename,
    clip,
    sort_nicely,
    to_vrt,
    to_geotiff
)

from typing import List, Set, Tuple, Dict
from pathlib import Path

def request(
        inputFile: Path=None,
        variables: List[str]=None,
        timesID: List[int]=None,
        points: Path=None,
        buffer: float=0.0,
        landscape_dir: Path=Path('chelsa-landscape'),
        geotiff: Path=Path('chelsa-stacked.tif')
    ):
    """
    Downloads bio and orog variables from CHELSA-TraCE21k. 1km climate timeseries since the LGM
    and crop the world files to the spatial extent of given points. Possiblly converts the output into a geotiff file
    """

    print("- Quetzal-CRUMBS - CHELSA-TraCE21k data access for iDDC modeling")

    bounding_box = bounds_to_polygon(points, buffer)
    print('    ... rasters will be cropped to bounding box infered from points:', bounding_box)

    landscape_dir.mkdir(parents=True, exist_ok=True)

    if inputFile is None:
        variables = expand_bio(variables)
        urls = generate_urls(variables, timesID)
    else:
        urls = read_urls(inputFile)
        variables = retrieve_variable_names_from(urls)

    assert len(urls) != 0 , "no URL generated or read in file."

    landscapes = []

    for url in urls:

        file = landscape_dir / get_filename(url)
        landscapes.append(str(file))
        if not file.exists(): clip(url, bounding_box, file)

    if geotiff is not None:

        for variable in variables:
            matching = [s for s in landscapes if variable in s]
            filename = str(geotiff).rsplit('.', 1)[-2]  + "_" + variable
            VRT = to_vrt(sort_nicely(matching), filename + ".vrt"  )
            TIFF = to_geotiff(VRT,  filename + ".tif")

    return landscapes
