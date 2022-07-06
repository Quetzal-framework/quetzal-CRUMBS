#!/usr/bin/python


def main(argv=None):
    """
    The main routine
    """

    from pathlib import Path

    from ..rotate_and_rescale import rotate_and_rescale
    from .rotate_and_rescale_options import get_parser

    print("- Quetzal-CRUMBS Rotation - GIS utility for landscape preparation")

    parser = get_parser()

    (options, args) = parser.parse_args(argv)

    return rotate_and_rescale(
        args[0], options.angle, options.factor, Path(options.output)
    )


if __name__ == "__main__":
    import sys

    sys.exit(main())
