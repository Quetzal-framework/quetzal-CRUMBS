
def get_parser():

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

    parser.add_option("-m", "--buffer",
                        type="float",
                        dest="buffer",
                        default=0.0,
                        help="Buffer to add around the bounding box, in degrees.")

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

    return parser
