#!/usr/bin/python

def main(argv):

    from optparse import OptionParser
    from . import get_chelsa
    from . import sdm_utils

    print("- Quetzal-CRUMBS - Species Distribution Models for iDDC modeling")
    parser = OptionParser()

    parser.add_option("-j", "--joblib",
                        type="str",
                        dest="joblib",
                        help="joblib files containin the persisted classifiers fitted from a previous step.")

    parser.add_option("-v", "--variables",
                        dest="variables",
                        type='str',
                        action='callback',
                        callback=get_chelsa.get_variables_args,
                        help="Comma-separated list of explanatory variables from CHELSA. Possible options: dem, glz, bio01 to bio19 or bio for all.")

    parser.add_option("-t", "--timeID"
                        dest="timeID",
                        type=float,
                        help="CHELSA_TraCE21k_ time ID to download for projection to past climates: 20 (present) to -200 (LGM)")

    parser.add_option("-c", "--clip_dir",
                        type="str",
                        dest="clip_dir",
                        default = "CHELSA_cropped",
                        help="Output directory for clipped CHELSA files. Default: CHELSA_cropped.")

    parser.add_option("-m", "--margin",
                        type="float",
                        dest="margin",
                        default=0.0,
                        help="Margin to add around the bounding box, in degrees.")

    parser.add_option("--cleanup", dest="cleanup",
                        default = False,
                        action = 'store_true',
                        help="Remove downloaded CHELSA world files, but keep clipped files.")

    parser.add_option("--no-cleanup", dest="cleanup",
                        action = 'store_false',
                        help="Keep downloaded CHELSA files on disk.")

    parser.add_option("-o", "--output",
                        type="str",
                        dest="output",
                        help="Output suitability geotiff name.")

    parser.add_option("-o", "--output",
                        type="str",
                        dest="output",
                        help="Output suitability geotiff name.")

    (options, args) = parser.parse_args(argv)

    return species_distribution_model(
        joblib_files = options.joblib,
        variables = options.variables,
        timeID = options.timeID,
        margin = options.margin,
        cleanup = options.cleanup,
        clip_dir = options.clip_dir,
        output = options.output,
        model_files = options.model_files
        )

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
