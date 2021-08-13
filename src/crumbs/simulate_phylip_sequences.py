import sqlite3
from optparse import OptionParser
import pyvolve
from crumbs.sequence import fasta_to_phylip

def newick_list_to_phylip_simulation(newicks, sequence_size, scale_tree, output):
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
        sequence.fasta_to_phylip(fasta_seqfile, phylip_seqfile)
        os.remove(fasta_seqfile)
    phyl_output = "temp_seq.phyl"
    with open(phyl_output, 'w') as outfile:
        for fname in phy_files:
            with open(fname) as infile:
                outfile.write(infile.read())
                outfile.write("\n")
            os.remove(fname)
    return phyl_output

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

def simulate_phylip_sequences(database, table, rowid, sequence_size, scale_tree, output_file):
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
    newick_list_to_phylip_simulation(trees, sequence_size, scale_tree, output_file)
    record_parameters(conn, )
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
    parser.add_option("--output", type="str", dest="filename", help="output file name")
    (options, args) = parser.parse_args(argv)
    return simulate_phylip_sequences(options.database, options.table, options.rowid, options.sequence_size, options.scale_tree, options.output_file)

if __name__ == '__main__':
    main(sys.argv[1:])
