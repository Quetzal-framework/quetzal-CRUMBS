def paginated_search(max_limit, *args, **kwargs):
    """
    In its current version, pygbif can not search more than 300 occurrences at
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
    """
    Convert the given points into a polygon, adding a margin.
    """
    from shapely.geometry import Polygon
    return Polygon([[long0 - margin , lat0 - margin],
                    [long1 + margin , lat0 - margin],
                    [long1 + margin , lat1 + margin],
                    [long0 - margin , lat1 + margin]])

def bounds_to_polygon(shapefile, margin):
    """
    Convert the given shapefiles points into a polygon, adding a margin.
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
    """
    Outputs the results in a CSV file.
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
