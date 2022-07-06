"""
Defines parsing options from command line
"""


def get_parser():
    """
    Returns parsed options from command line
    """

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option(
        "-a", "--angle", type="float", dest="angle", default=0.0, help="Rotation angle"
    )

    parser.add_option(
        "-f",
        "--factor",
        type="float",
        default=1.0,
        dest="factor",
        help="Rescaling factor",
    )

    parser.add_option(
        "-o", "--output", type="str", dest="output", help="Rotated/rescaled raster name"
    )
    return parser
