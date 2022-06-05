#!/usr/bin/python

def main(argv=None):
    """
    The main routine.
    """

    import sys
    from . options import get_parser
    from .. request import request

    if argv is None:
        argv = sys.argv[1:]

    parser = get_parser()
    (options, args) = parser.parse_args(argv)

    return request(
        scientific_name = options.scientific_name,
        points = options.points,
        buffer = options.buffer,
        limit = options.limit,
        all = options.all,
        year = options.year,
        csv_file = options.output + ".csv",
        shapefile = options.output + ".shp"
        )

if __name__ == '__main__':
    import sys
    sys.exit(main())
