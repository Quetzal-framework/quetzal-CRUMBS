#!/usr/bin/python

def main(argv=None):
    """
    The main routine
    """

    import sys
    import pickle

    from . fit_options import get_parser
    from .. sdm import SDM

    print("- Quetzal-CRUMBS - Fitting Species Distribution Models for iDDC modeling")

    parser = get_parser()
    (options, args) = parser.parse_args(argv)

    my_sdm = SDM(
        scientific_name=options.scientific_name,
        presence_shapefile = options.presence_shapefile,
        nb_background_points = options.nb_background_points,
        variables = options.variables,
        buffer = options.buffer,
        cleanup = options.cleanup
    )

    my_sdm.fit_on_present_data()

    with open("my_sdm.bin","wb") as f:
        pickle.dump(my_sdm, f)

if __name__ == '__main__':
    import sys
    sys.exit(main())
