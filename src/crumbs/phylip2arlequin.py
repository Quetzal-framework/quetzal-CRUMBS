from optparse import OptionParser
import csv
import os
from collections import defaultdict

def phylip2arlequin(input, imap, output):
    """Converts a PHYLIP alignement to ALREQUIN format using population mapping

    Parameters
    ----------
    input : str
        The path to the phylip sequence file - space delimited csv

    imap : str
        The path to the imap file mapping sequences ids to population - space delimited csv

    output : str
        The path of the arlequin file to write the result
    """
    assert os.stat(input).st_size > 0, "Phylip input file is empty"
    assert os.stat(imap).st_size > 0, "Imap input file is empty"
    # mapping imap sequences ids to their population id.
    id_to_pop = {}
    # defining the set of populations defined in imap
    pop_set = set()
    with open(imap, newline='') as csvfile:
        # TODO: IMAP is space delimiter based !!!
        reader = csv.reader(csvfile, delimiter=' ')
        for row in reader:
            # TODO: check for empty lines: IMAP last line can not be empty!
            assert len(row) == 2, "row (%s) in IMAP file has more than 2 columns." % row
            # assign seq id to pop in dico
            id_to_pop[row[0]]=row[1]
            pop_set.add(row[1])
    #reading sequences
    id_to_seq = {}
    with open(input, newline='') as csvfile:
        # TODO: PHYLIP files is space delimiter based !!!
        reader = csv.reader(csvfile, delimiter=' ')
        next(reader)
        for row in reader:
            # TODO: check for empty lines: PHYLIP last line can not be empty!
            assert len(row) == 2, "row (%s) in MHYLIP file has more than 2 columns." % row
            caret_ID = row[0]
            ID = caret_ID[1:]
            id_to_seq[ID] = row[1]
    pop_to_ids = defaultdict(list)
    pop_to_seqs = defaultdict(list)
    for id, pop in id_to_pop.items():
        pop_to_ids[pop].append(id)
        pop_to_seqs[pop].append(id_to_seq[id])
    seq_to_ids = defaultdict(list)
    for id, seq in id_to_seq.items():
        seq_to_ids[seq].append(id)
    seq_to_arl_ID = {}
    i = 0
    for s in seq_to_ids:
        seq_to_arl_ID[s] = i;
        i += 1
    nb_samples = len(pop_set)
    buffer = (
    "[Profile]\n\t" +
    '''Title="Simulated DNA sequence data"''' + "\n"
    "\tNbSamples=" + str(nb_samples) + "\n" +
    "\tGenotypicData=0\n" +
    "\tDataType=DNA\n" +
    "\tLocusSeparator=NONE\n" +
    "[Data]\n" +
    "\t[[Samples]]")
    for pop in pop_set:
        sample_size = len(pop_to_ids[pop])
        buffer = (buffer +
        "\n\t\tSampleName=" + '''"'''+ pop + '''"''' + "\n" +
        "\t\tSampleSize=" + str(sample_size) + "\n" +
        "\t\tSampleData={\n")
        for id in pop_to_ids[pop]:
            seq = id_to_seq[id]
            arl_id = seq_to_arl_ID[seq]
            count = pop_to_seqs[pop].count(seq)
            buffer = (buffer +
            str(arl_id) + "\t" + str(count) + "\t" + seq + "\n")
        buffer = buffer + "}\t"
    buffer = ( buffer +
    "\n\t[[Structure]]\n\n\t\t" +
    '''StructureName="A group of simulated populations"''' + "\n"
    "\t\tNbGroups=1\n\n" +
    "\t\tGroup={\n")
    for pop in pop_set:
        buffer = buffer+ "\t\t\t" + '''"''' + pop + '''"''' + "\n"
    buffer = buffer + "\t\t}"
    outfile = open(output,'w')
    outfile.write(buffer)
    outfile.close()

def main(argv):
    parser = OptionParser()
    parser.add_option("--input", type="str", dest="input", help="phylip input file")
    parser.add_option("--imap", type="str", dest="imap", help="mapping individuals to populations")
    parser.add_option("--output", type="str", dest="output", help="arlequin output file")
    (options, args) = parser.parse_args(argv)
    return phylip2arlequin(options.input, options.imap, options.output)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
