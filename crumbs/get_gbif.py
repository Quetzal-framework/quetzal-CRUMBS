#!/usr/bin/python

def paginated_search(max_limit, *args, **kwargs):
    """ In its current version, pygbif can not search more than 300 occurrences at
        once: this solves a bit of the problem.
    """
    MAX_LIMIT = max_limit
    PER_PAGE = 100
    results = []

    from pygbif import occurrences

    if(MAX_LIMIT <= PER_PAGE):
        resp = occurrences.search(*args, **kwargs, limit=MAX_LIMIT)
        results = resp['results']
    else :
        from tqdm import tqdm
        progress_bar = tqdm(total=MAX_LIMIT, unit='B', unit_scale=True, unit_divisor=1024)
        offset = 0
        while offset < MAX_LIMIT:
            resp = occurrences.search(*args, **kwargs, limit=PER_PAGE, offset=offset)
            results = results + resp['results']
            progress_bar.update(len(resp['results']))
            if resp['endOfRecords']:
                progress_bar.close()
                break
            else:
                offset = offset + PER_PAGE
        progress_bar.close()
    return results # list of dicts

def to_polygon(long0, lat0, long1, lat1, margin=0.0, csv_file='occurrences.csv'):
    """ Convert the given points into a polygon, adding a margin.
    """
    from shapely.geometry import Polygon
    return Polygon([[long0 - margin , lat0 - margin],
                    [long1 + margin , lat0 - margin],
                    [long1 + margin , lat1 + margin],
                    [long0 - margin , lat1 + margin]])

def bounds_to_polygon(shapefile, margin):
    """ Convert the given shapefiles points into a polygon, adding a margin.
    """
    from shapely.geometry import shape
    import fiona
    with fiona.open(shapefile) as shapes:
        bbox = to_polygon(*shapes.bounds, margin)
    return bbox

def preprocess(gbif_results):

    # Make sure that the query returned the right keys
    keys_all = set().union(*(dico.keys() for dico in gbif_results))
    keys= ['decimalLatitude','decimalLongitude','year']
    assert set(keys).issubset(keys_all), "Problem in fetching results: the required keys are not a subset of the results key. Contact the developer."

    processed = []

    for big_dict in gbif_results:
        small_dict = dict( (key, big_dict[key]) for key in keys)
        processed.append(small_dict)

    return processed, keys

def to_csv(gbif_results, csv_file, keys) -> None :
    """ Outputs the results in a CSV file.
    """
    try:

        import csv

        with open(csv_file, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(gbif_results)

    except IOError:

        print("I/O error in writing occurrence to", csv_file)

    return None


def to_shapefile(gbif_results, shapefile, keys) -> None:
    import fiona

    # Define schema
    schema = {
        'geometry':'Point',
        'properties':[('Year','int')]
    }

    try:
        # Open the fiona object
        pointShp = fiona.open(shapefile, mode='w', driver='ESRI Shapefile', schema = schema, crs = "EPSG:4326")

        #iterate over each row in the dataframe and save the record
        for small_dic in gbif_results:

            rowDict = {
                'geometry' : {'type':'Point',
                             'coordinates': (small_dic[keys[1]], small_dic[keys[0]])},
                'properties': {'Year' : small_dic[keys[2]]},
            }

            pointShp.write(rowDict)

        # Close the fiona object
        pointShp.close()

    except IOError:
        print("I/O error in writing occurrence to", shapefile)

    return None


def search_gbif(scientific_name: str,
                points: str,
                margin: float = 0.0,
                all: bool = False,
                limit: int = 30,
                year = None,
                csv_file: str = "occurrences.csv",
                shapefile: str = "occurrences.shp",
                ) -> None :
    """
    Args:
        scientific_name: The scientific name of the species of interest (e.g., "Heteronotia binoei").
        points:          The path to a shapefile with spatial points to infer a spatial extent (e.g., "data/test_points/test_points.shp").
        margin:          A margin in decimal degrees to add around the bounding box (defaults to 0).
        all:             If True, retrieve all occurrences available. If False, retrieve a number of occurrence defined by argument limit.
        limit:           The maximal number of occurence records to retrieve from gbif if all=False. Default is 30.
        year:            Year (eg. 1990) or range (e.g. 1900,2022) of the occurrences to be retrieved.
        csv_file:        Write in a .csv file the occurrences in a Comma-Separated Values format (a human readable table).
        shapefile:       Write the occurrences in a Shapefile format (compatible with other programs).
    Returns:
        The return value. True for success, False otherwise.
    """
    import os

    from pygbif import species as species
    from pygbif import occurrences

    print(" - Quetzal-CRUMBS - Global Biodiversity Information Facility (GBIF) wrapper for iDDC models")

    # Retrieve the taxon key
    taxonKey = species.name_suggest(q=scientific_name)[0]['key']

    # Infer the bounding box from spatial points and margin
    bounding_box = bounds_to_polygon(points, margin)

    # Report
    print("    ... Looking in GBIF database for", scientific_name)
    print("    ... Search in the bounding box provided by", points, "with margin", margin, "degrees")
    print("    ... Bounding box used:", bounding_box)
    print("    ... For", scientific_name, "GBIF suggested the taxon key:", taxonKey)

    # Just fetching some information
    out = occurrences.search(taxonKey=taxonKey, geometry=bounding_box, hasCoordinate=True, year=year)
    print("    ... We identified", out['count'], "available records in the bounding box.")

    LIMIT=0
    if all is True:
        LIMIT = int(out['count'])
        print("    ... Option all is True. Retrieving all", LIMIT, "records available.")
    else:
        LIMIT = limit
        print("    ... Option all is False, using the limit option to retrieve only the first", LIMIT, "available records.")

    # Retrieving all results along years
    raw_results = paginated_search(taxonKey=taxonKey, geometry=bounding_box, hasCoordinate=True, max_limit=LIMIT, year=year)
    print("    ...", len(raw_results), "records retrieved.")

    results, keys = preprocess(raw_results)
    to_csv(results, csv_file, keys)
    to_shapefile(results, shapefile, keys)

    return None


def main(argv=None):
    """The main routine."""
    import sys
    if argv is None:
        argv = sys.argv[1:]

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("-s", "--species",
                        type="str",
                        dest="scientific_name",
                        help="Species name for the SDM.")

    parser.add_option("-p", "--points",
                        type="str",
                        dest="points",
                        default=None,
                        help="Shapefile of spatial points around which a bounding box will be drawn to perform SDM. Example: all DNA samples coordinates, or 4 coordinates defining a bounding box.")

    parser.add_option("-m", "--margin",
                        type="float",
                        dest="margin",
                        default=0.0,
                        help="Margin to add around the bounding box, in degrees.")

    parser.add_option("--all",
                        dest="all",
                        default = False,
                        action = 'store_true',
                        help="Download all available occurrences in the area, whatever the year.")

    parser.add_option("--no-all",
                        dest="all",
                        action = 'store_false',
                        help="Only download a limited number of occurrences.")

    parser.add_option("-l", "--limit",
                        type="int",
                        dest="limit",
                        default=None,
                        help="Maximum number of records to retrieve.")

    parser.add_option("-y", "--year",
                        type="str",
                        dest="year",
                        default=None,
                        help="Year (eg. 1990) or range (e.g. 1900,2022) of the occurrences to be retrieved")

    parser.add_option("-o", "--output",
                        type="str",
                        dest="output",
                        default="occurrences",
                        help="Output file name for the shapeflles. A csv file will also be generated for human readibility.")

    (options, args) = parser.parse_args(argv)

    return search_gbif(
        scientific_name = options.scientific_name,
        points = options.points,
        margin = options.margin,
        limit = options.limit,
        all = options.all,
        year = options.year,
        csv_file = options.output + ".csv",
        shapefile = options.output + ".shp"
        )

if __name__ == '__main__':
    import sys
    sys.exit(main())
