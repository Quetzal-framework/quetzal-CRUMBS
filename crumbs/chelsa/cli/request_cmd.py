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

    try:

        return request(
            inputFile = options.input,
            variables = options.variables,
            timesID = options.timesID,
            points = options.points,
            buffer = options.buffer,
            world_dir = options.world_dir,
            landscape_dir = options.landscape_dir,
            cleanup = options.cleanup)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    import sys
    sys.exit(main())
