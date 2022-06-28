#!/usr/bin/python

def main(argv=None):
    """
    The main routine
    """

    from . rotate_and_rescale_options import get_parser
    from .. rotate_and_rescale import rotate_and_rescale

    print("- Quetzal-CRUMBS Rotation - GIS utility for landscape preparation")

    parser = get_parser()

    (options, args) = parser.parse_args(argv)

    return rotate_and_rescale(args[0], float(args[1]), float(args[2]), options.output)

if __name__ == '__main__':
    import sys
    sys.exit(main())
