#!/usr/bin/python


def main(argv=None):
    """
    The main routine.
    """

    import sys
    from pathlib import Path

    from ..request import request
    from .options import get_parser

    if argv is None:
        argv = sys.argv[1:]

    parser = get_parser()
    (options, args) = parser.parse_args(argv)

    try:

        return request(
            inputFile=options.input,
            variables=options.variables,
            timesID=options.timesID,
            points=options.points,
            buffer=options.buffer,
            landscape_dir=Path(options.landscape_dir),
            geotiff=Path(options.geotiff),
        )

    except Exception as e:
        print(e)


if __name__ == "__main__":
    import sys

    sys.exit(main())
