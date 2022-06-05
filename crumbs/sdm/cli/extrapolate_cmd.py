#!/usr/bin/python

def main(argv=None):
    """
    The main routine
    """

    import sys

    from . extrapolate_options import get_parser
    from .. sdm import SDM

    print("- Quetzal-CRUMBS - Species Distribution Models for iDDC modeling")
    print("Not implemented yet!")

    parser = get_parser()
    (options, args) = parser.parse_args(argv)

    with open(options.sdm_file,"rb") as f:
        my_saved_sdm = pickle.load(f)
        my_saved_sdm.load_classifiers_and_extrapolate(options.timeID)

if __name__ == '__main__':
    import sys
    sys.exit(main())
