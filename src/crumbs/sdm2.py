from optparse import OptionParser

import os
import sklearn # machine learning
import pyimpute     # spatial classification
import rasterio     # reads and writes geospatial rasters
import geopandas    # for spatial operations
from dotenv import load_dotenv   #for python-dotenv method


def paginated_search(my_limit, *args, **kwargs):
    # https://gist.github.com/niconoe/b9dcb6c468b996b6f77e18f51516e840#file-example_paginate_nameusage-py-L2
    from pygbif import occurrences
    from tqdm import tqdm

    PER_PAGE = 100
    progress_bar = tqdm(total=my_limit, unit='iB', unit_scale=True)

    results = []
    offset = 0

    while offset <= my_limit:
        #resp = occurrences.name_usage(*args, **kwargs, limit=PER_PAGE, offset=offset)
        resp = occurrences.search(*args, **kwargs, limit=PER_PAGE, offset=offset)
        results = results + resp['results']
        progress_bar.update(len(resp['results']))
        if resp['endOfRecords']:
            break
        else:
            offset = offset + PER_PAGE
    progress_bar.close()
    return results

def to_polygon(long0, lat0, long1, lat1, margin=0.0):
    """ Convert the given points into a polygon, adding a margin.
    """
    from shapely.geometry import Polygon
    return Polygon([[long0 - margin , lat0 - margin],
                    [long1 + margin , lat0 - margin],
                    [long1 + margin , lat1 + margin],
                    [long0 - margin , lat1 + margin]])

def bounds_to_polygon(shapefile, margin):
    from shapely.geometry import shape
    import fiona
    with fiona.open(shapefile) as shapes:
        bbox = to_polygon(*shapes.bounds, margin)
        return bbox

def create_folders_if_dont_exist(dir1, dir2):
    import os
    if not os.path.exists(dir1):
        os.makedirs(dir1)
    if not os.path.exists(dir2):
        os.makedirs(dir2)
    return

def inspect_gbif(scientific_name, points, margin, limit=None):
    from pygbif import species as species
    from pygbif import occurrences

    print("    - Looking in GBIF database for", scientific_name)
    if points is not None: bounding_box = bounds_to_polygon(points, margin)
    print("    - Search in the bounding box provided by", points, "with margin", margin, "degrees")
    print("    - Bounding box used:", bounding_box)
    key = species.name_suggest(q=scientific_name)[0]['key']
    print("    - Name", scientific_name, "suggested GBIF taxon key", key)
    if limit is None:
        out = occurrences.search(taxonKey=key, geometry=bounding_box, hasCoordinate=True,limit=300)
        print("    -", out['count'], "records identified with usable coordinates")
        return
    else:
        results = paginated_search(taxonKey=key, geometry=bounding_box, hasCoordinate=True, my_limit=limit)
        print("    -", len(results), "records retrieved")
        print("\tLatitude\tLongitude\tYear")
        for key in results:
            print("\t", key['decimalLatitude'], "\t", key['decimalLongitude'], "\t", key['year'])
    return

def download_gbif(scientific_name, points, margin):
    print("    - Looking in GBIF database for", scientific_name)
    if points is not None: bounding_box = bounds_to_polygon(points, margin)
    print("    - Search in the bounding box provided by", points, "with margin", margin, "degrees")
    print("    - Bounding box used:", bounding_box)
    key = species.name_suggest(q=scientific_name)[0]['key']
    print("    - Name", scientific_name, "suggested GBIF taxon key", key)
    from pathlib import Path  # python3 only
    env_path = Path('.') / '.env'
    load_dotenv(dotenv_path=env_path)
    print("    - Beginning download")
    print("      - GBIF user name:", os.environ.get('GBIF_USER'))
    print("      - GBIF user email:", os.environ.get('GBIF_EMAIL'))
    print("      - GBIF user password:", "*"*len(os.environ.get('GBIF_PWD')))
    res = occurrences.download(['taxonKey = ' + str(key), 'hasCoordinate = TRUE', 'geometry = '+ str(bounding_box)])
    download_key = res[0]
    occurrences.download_get(download_key)

def main(argv):
    print(" - Quetzal-CRUMBS - Species Distribution Modeling for iDDC models")
    parser = OptionParser()
    parser.add_option("-s", "--species", type="str", dest="scientific_name", help="Species name for the SDM.")
    parser.add_option("-p", "--points", type="str", dest="points", default=None, help="Shapefile of spatial points around which a bounding box will be drawn to perform SDM. Example: all DNA samples coordinates, or 4 coordinates defining a bounding box.")
    parser.add_option("-m", "--margin", type="float", dest="margin", default=0.0, help="Margin to add around the bounding box, in degrees.")
    parser.add_option("-l", "--limit", type="float", dest="limit", default=None, help="Maximum number of records to retrieve.")
    parser.add_option("--download", dest="download", default = False, action = 'store_true', help="Download data using GBIF user information.")
    parser.add_option("--no-download", dest="download", action = 'store_false', help="Inspect the GBIF database, with limitied output.")
    (options, args) = parser.parse_args(argv)
    try:
        if options.download is not True:
            return inspect_gbif(
                scientific_name = options.scientific_name,
                points = options.points,
                margin = options.margin,
                limit = options.limit
                )
        else :
            return download_gbif(
                scientific_name = options.scientific_name,
                points = options.points,
                margin = options.margin
                )
    except Exception as e:
        print(e)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
