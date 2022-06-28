#!/usr/bin/python

def main(argv=None):
    """
    The main routine
    """

    from . interpolate_options import get_parser
    from .. interpolate import interpolate

    print("- Quetzal-CRUMBS Interpolate - Temporal interpolation for missing layers")

    parser = get_parser()

    (options, args) = parser.parse_args(argv)

    return temporal_interpolation(
        inputFile = args[0],
        band_to_yearBP = options.generations,
        outputFile = options.output)

if __name__ == '__main__':
    import sys
    sys.exit(main())
