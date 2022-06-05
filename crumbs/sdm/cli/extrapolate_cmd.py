#!/usr/bin/python

def main(argv=None):
    """
    The main routine
    """

    import sys

    from . options import get_parser
    from .. sdm import SDM

    print("- Quetzal-CRUMBS - Species Distribution Models for iDDC modeling")
    print("Not implemented yet!")

    parser = get_parser()
    (options, args) = parser.parse_args(argv)

if __name__ == '__main__':
    import sys
    sys.exit(main())
