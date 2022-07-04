#!/usr/bin/python

def main(argv=None):
    """
    The main routine
    """

    from . clip_circle_options import get_parser
    from .. clip_circle import clip_circle

    print("- Quetzal-CRUMBS Clip Circle - GIS utility for landscape preparation")

    parser = get_parser()

    (options, args) = parser.parse_args(argv)

    return clip_circle(args[0], options.output)

if __name__ == '__main__':
    import sys
    sys.exit(main())
