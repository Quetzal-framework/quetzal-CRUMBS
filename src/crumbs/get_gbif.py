#!/usr/bin/python

def paginated_search(max_limit, *args, **kwargs):
    """ In its current version, pygbif can not search more than 300 occurrences at once: this solves a bit of the problem
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

def search_gbif(scientific_name, points, margin, limit=None, csv_file="occurrences.csv", shapefile="occurrences.shp", all=False, year=None, output=None):
    import os
    if output is not None:
        filename = os.path.splitext(output)[0]
        csv_file = filename + '.csv'
        shapefile = filename + 'shp'

    from pygbif import species as species
    from pygbif import occurrences
    assert points is not None
    print("    ... Looking in GBIF database for", scientific_name)
    if points is not None: bounding_box = bounds_to_polygon(points, margin)
    print("    ... Search in the bounding box provided by", points, "with margin", margin, "degrees")
    print("    ... Bounding box used:", bounding_box)
    taxonKey = species.name_suggest(q=scientific_name)[0]['key']
    print("    ... For", scientific_name, "GBIF suggested the taxon key:", taxonKey)

    LIMIT = limit

    if LIMIT is None:
        # Just printing information
        out = occurrences.search(taxonKey=taxonKey, geometry=bounding_box, hasCoordinate=True, year=year)
        print("    ... We identified", out['count'], "records with coordinates (use option --all to fetch all, or --limit <i> t fetch only i records.).")
        if all is True:
            LIMIT = int(out['count'])
            print("    ... Fetching limit set at", LIMIT)
        else:
            return

    try:
        LIMIT += 1; LIMIT -= 1
    except TypeError:
        print("Something got wrong, LIMIT is", LIMIT)

    results = paginated_search(taxonKey=taxonKey, geometry=bounding_box, hasCoordinate=True, max_limit=LIMIT, year=year)
    print("    ...", len(results), "records retrieved")

    keys_all = set().union(*(dico.keys() for dico in results))
    keys= ['decimalLatitude','decimalLongitude','year']
    assert set(keys).issubset(keys_all), "Problem in fetching results: the required keys are not a subset of the results key."
    to_csv = []
    for big_dict in results:
        small_dict = dict( (key, big_dict[key]) for key in keys)
        to_csv.append(small_dict)

    try:
        import csv
        with open(csv_file, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(to_csv)
    except IOError:
        print("I/O error in writing occurrence to", csv_file)

    try:
        import fiona
        # define schema
        schema = {
            'geometry':'Point',
            'properties':[('Year','int')]
        }
        #open a fiona object
        pointShp = fiona.open(shapefile, mode='w', driver='ESRI Shapefile', schema = schema, crs = "EPSG:4326")

        #iterate over each row in the dataframe and save record
        for small_dic in to_csv:
            rowDict = {
                'geometry' : {'type':'Point',
                             'coordinates': (small_dic[keys[1]], small_dic[keys[0]])},
                'properties': {'Year' : small_dic[keys[2]]},
            }
            pointShp.write(rowDict)
        #close fiona object
        pointShp.close()
    except IOError:
        print("I/O error in writing occurrence to", shape_file)
    return

def main(argv):
    from optparse import OptionParser

    print(" - Quetzal-CRUMBS - Global Biodiversity Information Facility (GBIF) wrapper for iDDC models")
    parser = OptionParser()
    parser.add_option("-s", "--species", type="str", dest="scientific_name", help="Species name for the SDM.")
    parser.add_option("-p", "--points", type="str", dest="points", default=None, help="Shapefile of spatial points around which a bounding box will be drawn to perform SDM. Example: all DNA samples coordinates, or 4 coordinates defining a bounding box.")
    parser.add_option("-m", "--margin", type="float", dest="margin", default=0.0, help="Margin to add around the bounding box, in degrees.")
    parser.add_option("-l", "--limit", type="int", dest="limit", default=None, help="Maximum number of records to retrieve.")
    parser.add_option("-o", "--output", type="str", dest="output", help="Output shapefile name. A csv file with same name will also be generated for human readibility.")
    parser.add_option("-y", "--year", type="str", dest="year", default=None, help="Year (eg. 1990) or range (e.g. 1900,2022) of the occurrences to be retrieved")
    parser.add_option("--all", dest="all", default = False, action = 'store_true', help="Download all available occurrences.")
    parser.add_option("--no-all", dest="all", action = 'store_false', help="Only download a limited number of occurrences.")
    (options, args) = parser.parse_args(argv)
    return search_gbif(
        scientific_name = options.scientific_name,
        points = options.points,
        margin = options.margin,
        limit = options.limit,
        all = options.all,
        year = options.year,
        output = options.output
        )

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
