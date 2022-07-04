"""
Defines parsing options from command line
"""

def get_variables_args(option, opt, value, parser):
    """
    Helper function
    """
    setattr(parser.values, option.dest, value.split(','))


def get_timesID_args(option, opt, value, parser, type='int'):
    """
    Helper function
    """
    setattr(parser.values, option.dest, [int(s) for s in value.split(',')])


def get_parser():
    """
    Defines parsing options for command line
    """
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("-i", "--input", type="str", dest="input", help="Input urls file, one url by line")

    parser.add_option("-v", "--variables",
                        dest="variables",
                        type='str',
                        action='callback',
                        callback=get_variables_args,
                        help="If no input given, comma-separated CHELSA TraCE21k variables to download. Possible options: dem, glz, bio01 to bio19 or bio for all")

    parser.add_option("-t", "--timesID",
                        dest="timesID",
                        type='str',
                        action='callback',
                        callback=get_timesID_args,
                        help="CHELSA_TraCE21k_ times IDs to download: 20 (present) to -200 (LGM)")

    parser.add_option("-p", "--points",
                        type="str",
                        dest="points",
                        default=None,
                        help="Shapefile of spatial points around which a bounding box will be drawn to clip the CHELSA tif. Example: all DNA samples coordinates, or 4 coordinates defining a bounding box.")

    parser.add_option("-b", "--buffer",
                        type="float",
                        dest="buffer",
                        default=0.0,
                        help="Buffer to add around the bounding box, in degrees.")

    parser.add_option("-l", "--landscape_dir",
                        type="str",
                        dest="landscape_dir",
                        default='chelsa-landscape/',
                        help="Directory where to store landscape rasters.")

    parser.add_option("-g", "--geotiff",
                        type="str",
                        dest="geotiff",
                        default='stacked.tif',
                        help="Multilayer geotiff for each variable, where each layer is a time step.")

    return parser
