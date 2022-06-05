
def request(scientific_name: str,
                points: str,
                buffer: float = 0.0,
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
        buffer:          A buffer in decimal degrees to add around the bounding box (defaults to 0).
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

    from . utils import(
        bounds_to_polygon,
        paginated_search,
        preprocess,
        to_csv,
        to_shapefile
    )

    print(" - Quetzal-CRUMBS - Global Biodiversity Information Facility (GBIF) wrapper for iDDC models")

    # Retrieve the taxon key
    taxonKey = species.name_suggest(q=scientific_name)[0]['key']

    # Infer the bounding box from spatial points and buffer
    bounding_box = bounds_to_polygon(points, buffer)

    # Report
    print("    ... Looking in GBIF database for", scientific_name)
    print("    ... Search in the bounding box provided by", points, "with buffer", buffer, "degrees")
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
