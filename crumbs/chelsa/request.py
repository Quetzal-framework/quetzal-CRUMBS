#!/usr/bin/python

from . helpers import (
    get_variables_args,
    get_timesID_args
)

from . utils import request

def main(argv):

    parser = OptionParser()

    parser.add_option("-i", "--input", type="str", dest="input", help="Input urls file, one url by line")

    parser.add_option("-v", "--variables",
                        dest="variables",
                        type='str',
                        action='callback',
                        callback=get_variables_args,
                        help="If no input given, comma-separated CHELSA TraCE21k variables to download. Possible options: dem, glz, bio01 to bio19 or bio for all")

    parser.add_option("-t", "--timesID",
                        dest="timesID",
                        type='str',
                        action='callback',
                        callback=get_timesID_args,
                        help="CHELSA_TraCE21k_ times IDs to download. Default: 20 (present) to -200 (LGM)")

    parser.add_option("-p", "--points", type="str", dest="points", default=None, help="Shapefile of spatial points around which a bounding box will be drawn to clip the CHELSA tif. Example: all DNA samples coordinates, or 4 coordinates defining a bounding box.")
    parser.add_option("-m", "--margin", type="float", dest="margin", default=0.0, help="Margin to add around the bounding box, in degrees.")
    parser.add_option("-d", "--dir", type="str", dest="chelsa_dir", default = "chelsa-world", help="Output directory for CHELSA files.")
    parser.add_option("-c", "--clip_dir", type="str", dest="clip_dir", default = "chelsa-cropped", help="Output directory for cropped CHELSA files.")
    parser.add_option("-o", "--geotiff", type="str", dest="geotiff", default = "chelsa-stacked.tif", help="Produces a geotiff stackin variables at all times.")
    parser.add_option("--cleanup", dest="cleanup", default = False, action = 'store_true', help="Remove downloaded CHELSA world files, but keep cropped files.")
    parser.add_option("--no-cleanup", dest="cleanup", action = 'store_false', help="Keep downloaded CHELSA files on disk.")
    (options, args) = parser.parse_args(argv)
    try:
        return get_chelsa(
            inputFile = options.input,
            variables = options.variables,
            timesID = options.timesID,
            points = options.points,
            margin = options.margin,
            chelsa_dir = options.chelsa_dir,
            clip_dir = options.clip_dir,
            geotiff = options.geotiff,
            cleanup = options.cleanup)
    except Exception as e:
        print(e)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
