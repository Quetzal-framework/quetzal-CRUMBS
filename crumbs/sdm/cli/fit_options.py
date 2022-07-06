"""
Defines parsing options from command line
"""


def get_variables_args(option, opt, value, parser):
    """
    Helper function
    """
    setattr(parser.values, option.dest, value.split(","))


def get_parser():
    """
    Returns parsed options from command line
    """

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option(
        "-s",
        "--species",
        type="str",
        dest="scientific_name",
        help="Species name for the SDM.",
    )

    parser.add_option(
        "-p",
        "--presences",
        type="str",
        dest="presence_shapefile",
        default=None,
        help="Shapefile of presence spatial points around which a bounding box will be drawn to clip the CHELSA tif. Example: all DNA samples coordinates, or 4 coordinates defining a bounding box.",
    )

    parser.add_option(
        "-n",
        "--nb-backround",
        dest="nb_background_points",
        type="int",
        help="Number of backround points for pseudo-absence generation.",
    )

    parser.add_option(
        "-v",
        "--variables",
        dest="variables",
        type="str",
        action="callback",
        callback=get_variables_args,
        help="Comma-separated list of explanatory variables from CHELSA. Possible options: dem, glz, bio01 to bio19 or bio for all.",
    )

    parser.add_option(
        "-b",
        "--buffer",
        type="float",
        dest="buffer",
        default=0.0,
        help="Buffer to add around the bounding box, in degrees.",
    )

    parser.add_option(
        "-f",
        "--sdm-file",
        dest="sdm_file",
        type="str",
        default="my-sdm.bin",
        help="The binary representation of the SDM",
    )

    parser.add_option(
        "-j",
        "--joblib",
        type="str",
        dest="joblib",
        help="joblib files containin the persisted classifiers fitted from a previous step.",
    )

    parser.add_option(
        "-o",
        "--outdir",
        type="str",
        dest="outdir",
        default="SDM/",
        help="Output directory for clipped CHELSA files.",
    )

    return parser
