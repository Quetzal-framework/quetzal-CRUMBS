from optparse import OptionParser
import sequence

# options
parser = OptionParser()
parser.add_option("--input", type="str", dest="input", help="phylip input file")
parser.add_option("--output", type="str", dest="output", help="arlequin output file")

(options, args) = parser.parse_args()

fasta_to_phylip(options.input, options.output)
