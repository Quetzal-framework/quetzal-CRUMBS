#!/usr/bin/python

def main(argv=None):
    """
    The main routine
    """

    from . animate_options import get_parser
    from .. animate import animate

    print("- Quetzal-CRUMBS Animate - GIS utility for landscape preparation")

    parser = get_parser()

    (options, args) = parser.parse_args(argv)

    return chose_method(args[0],
     vmin=options.min,
     vmax=options.max,
     output=options.output,
     gbif_occurrences=options.gbif,
     DDD=options.DDD,
     warp_scale=options.warp_scale,
     nb_triangles=options.nb_triangles
     )

if __name__ == '__main__':
    import sys
    sys.exit(main())
