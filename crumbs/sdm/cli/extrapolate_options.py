"""
Defines parsing options from command line
"""

def get_parser():
    """
    Returns parsed options from command line
    """

    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option("-f", "--sdm-file",
                        dest="sdm_file",
                        type='str',
                        default="my-sdm.bin",
                        help="The binary representation of the SDM")

    parser.add_option("-t", "--timeID",
                        dest="timeID",
                        type='int',
                        help="CHELSA_TraCE21k time ID to perform the extrapolation: 20 (present) to -200 (LGM)")

    return parser
