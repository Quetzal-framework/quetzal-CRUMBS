#!/usr/bin/python

def main(argv):

    from optparse import OptionParser

    from lib import (
        chelsa,
        sdm
    )

    print("- Quetzal-CRUMBS - Species Distribution Models for iDDC modeling")

    parser = OptionParser()

    parser.add_option("-p", "--presence",
                        type="str",
                        dest="presence_points",
                        help="Presence points shapefile.")

    parser.add_option("-b", "--background",
                        type="int",
                        default=None,
                        dest="background_points",
                        help="Number of backgound points to sample for pseudo-absences generation")

    parser.add_option("-t", "--timeID",
                        dest="timeID",
                        type='float',
                        default=20,
                        help="CHELSA_TraCE21k_ time ID to download present covariates. Default: 20 (present)")

    parser.add_option("-v", "--variables",
                        dest="variables",
                        type='str',
                        action='callback',
                        callback=get_chelsa.get_variables_args,
                        help="Comma-separated list of explanatory variables from CHELSA. Possible options: dem, glz, bio01 to bio19 or bio for all.")

    parser.add_option("-m", "--margin",
                        type="float",
                        dest="margin",
                        default=0.0,
                        help="Margin to add around the bounding box, in degrees.")

    parser.add_option("-o", "--output",
                        type="str",
                        dest="output",
                        default="suitability.tif",
                        help="Output suitability geotiff name.")

    parser.add_option("--persist",
                        dest="persist",
                        default = True,
                        action = 'store_true',
                        help="After training a scikit-learn model, persist the model for future use without having to retrain.")

    parser.add_option("--no-persist",
                        dest="persist",
                        action = 'store_false',
                        help="After training a scikit-learn model, the model is lost.")

    parser.add_option("--cleanup",
                        dest="cleanup",
                        default = True,
                        action = 'store_true',
                        help="Remove downloaded CHELSA world files, but keep clipped files.")

    parser.add_option("--no-cleanup",
                        dest="cleanup",
                        action = 'store_false',
                        help="Keep downloaded CHELSA world files on disk.")

    parser.add_option("-c", "--clip_dir",
                        type="str",
                        dest="clip_dir",
                        default = "CHELSA_cropped",
                        help="Output directory for clipped CHELSA files. Default: CHELSA_cropped.")

    (options, args) = parser.parse_args(argv)

    my_sdm = SDM(
        presence_shp = options.presence_points,
        background_points = options.background_points,
        timeID = options.timeID,
        variables = options.variables,
        margin = options.margin,
        output = options.output,
        persist = options.persist,
        cleanup = options.cleanup,
        clip_dir = options.clip_dir
    )

    my_sdm.fit_on_present_data()

    return None

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
