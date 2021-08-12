import pyvolve

def evolve(newicks, sequence_size, scale_tree):
    temp = "temporary_sequences.fasta"
    phy_files = []
    my_model = pyvolve.Model("nucleotide")
    partition = pyvolve.Partition(models = my_model, size = sequence_size)
    for i in range(0, len(newicks)):

        newick = newicks[i]
        tree = pyvolve.read_tree(tree = newick, scale_tree = scale_tree)
        my_evolver = pyvolve.Evolver(tree = tree, partitions = partition)
        fasta_seqfile = "temp" + str(i) + ".fasta"
        phylip_seqfile = "temp" + str(i) + ".phyl"
        phy_files.append(phylip_seqfile)

        my_evolver(seqfile=fasta_seqfile, seqfmt = "fasta", ratefile = None, infofile = None)
        fasta_to_phyl(fasta_seqfile, phylip_seqfile)

        os.remove(fasta_seqfile)

    phyl_output = "temp_seq.phyl"

    with open(phyl_output, 'w') as outfile:
        for fname in phy_files:
            with open(fname) as infile:
                outfile.write(infile.read())
                outfile.write("\n")
            os.remove(fname)

    return phyl_output
