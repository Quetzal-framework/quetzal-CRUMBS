"""
Defines parsing options from command line
"""

def get_times_args(option, opt, value, parser, type='float'):
    setattr(parser.values, option.dest, [int(s) for s in value.split(',')])


def get_parser():
    """
    Returns parsed options from command line
    """

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("-t", "--timesID",
                        dest="generations",
                        type='str',
                        action='callback',
                        callback=get_times_args,
                        help="Comma separated sequence mapping band layers to years before present. Example for a 3 band raster: 0,500,1000.")

    parser.add_option("-o", "--output",
                        type="str",
                        dest="output",
                        help="Cliped output raster name")

    return parser
