import sqlite3, pyvolve, os
from optparse import OptionParser

from . import sequence

def newick_list_to_phylip_simulation(newicks, sequence_size, scale_tree, output, temporary_prefix):
    temporaries = []
    my_model = pyvolve.Model("nucleotide")
    partition = pyvolve.Partition(models = my_model, size = sequence_size)
    for i in range(0, len(newicks)):
        # creating a evolver object
        newick = newicks[i]
        tree = pyvolve.read_tree(tree = newick, scale_tree = scale_tree)
        my_evolver = pyvolve.Evolver(tree = tree, partitions = partition)
        # creating temporaries
        fasta_seqfile = temporary_prefix + str(i) + ".fasta"
        phylip_seqfile = temporary_prefix + str(i) + ".phyl"
        temporaries.append(temporary_prefix + str(i))
        # simulating
        my_evolver(seqfile=fasta_seqfile, seqfmt = "fasta", ratefile = None, infofile = None)
        # converting
        sequence.fasta_to_phylip(fasta_seqfile, phylip_seqfile)
    # concatening all sequences into a bigger file
    with open(output, 'w') as outfile:
        for fname in temporaries:
            with open(fname + ".phyl") as infile:
                outfile.write(infile.read())
                outfile.write("\n")
            # cleaning
            os.remove(fname + ".phyl")
            os.remove(fname + ".fasta")
    return output

def maybe_alter_table_to_add_2_columns(database, table):
    conn = sqlite3.connect(database)
    # Check that table is properly named
    if table == "quetzal_EGG_1" :
        try:
            conn.execute("ALTER TABLE quetzal_EGG_1 ADD COLUMN scale_tree DOUBLE")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE quetzal_EGG_1 ADD COLUMN sequence_size INTEGER")
        except Exception:
            pass
    else :
        raise NotImplementedError("Error with option table" + table + "in database " + database + ": should be quetzal_EGG_n, where n = 1.")
    conn.commit()
    return conn

def simulate_phylip_sequences(database, table, rowid, sequence_size, scale_tree, output_file, temporary_prefix):
    """Add sequencReads newicks in database and simulate  the rowids of simulations registered in the database.

    Parameters
    ----------
    database : str
        The path to the sqlite database.

    table : str
        The name of the database table to read from

    rowid : int
        The simulation row to read from

    sequence_size : int
        The sequence length (in bp) to be simulated

    scale_tree : double
        The scaling factor along branches (see Pyvolve manual)

    output : str
        The name of the output file where to store the result
    Raises
    ------
    NotImplementedError
        If the incorrect table name is passed as parameter.
    """
    conn = maybe_alter_table_to_add_2_columns(database, table)
    cursor = conn.cursor()
    cursor.execute('SELECT newicks FROM quetzal_EGG_1 WHERE rowid=?', (rowid,))
    # fetch one row, returns a tuple of size 1 but can return none if wrong rowid
    record = cursor.fetchone()
    if record is None :
        raise Runtime("Error when fetching row with rowid " + rowid + ". Make sure that row is defined in table using crumbs.get_simulations_rowids.")
    # newick formulas are separated by 2 Newline characters
    trees = record[0].split("\n\n")
    newick_list_to_phylip_simulation(trees, sequence_size, scale_tree, output_file, temporary_prefix)
    cursor.execute('''UPDATE quetzal_EGG_1 SET scale_tree = ? WHERE rowid = ?''', (scale_tree, rowid))
    cursor.execute('''UPDATE quetzal_EGG_1 SET sequence_size = ? WHERE rowid = ?''', (sequence_size, rowid))
    conn.commit()
    conn.close()

def main(argv):
    parser = OptionParser()
    parser.add_option("--database", type="str", dest="database", help="path to database")
    parser.add_option("--table", type="str", dest="table", help="what quetzal-EGG was used (eg: quetzal_EGG_1)")
    parser.add_option("--rowid", type="str", dest="rowid", help="what row in the database table")
    parser.add_option("--sequence_size", type="int", dest="sequence_size", help="sequence_size")
    parser.add_option("--scale_tree", type="float", dest="scale_tree", help="scale tree branch length")
    parser.add_option("--output", type="str", dest="output", help="output file name")
    (options, args) = parser.parse_args(argv)
    return simulate_phylip_sequences(options.database, options.table, options.rowid, options.sequence_size, options.scale_tree, options.output, options.output + "_temp")

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
