"""
Defines parsing options from command line
"""

def get_parser():
    """
    Returns parsed options from command line
    """

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("-o", "--output",
                        type="str",
                        dest="output",
                        help="Resampled raster name")
    return parser
