#!/usr/bin/python

def main(argv=None):
    """
    The main routine
    """

    from . resample_options import get_parser
    from .. resample import resample

    print("- Quetzal-CRUMBS Resample - GIS utility for landscape preparation")

    parser = get_parser()

    (options, args) = parser.parse_args(argv)

    return resample(args[0], float(args[1]), options.output)

if __name__ == '__main__':
    import sys
    sys.exit(main())
