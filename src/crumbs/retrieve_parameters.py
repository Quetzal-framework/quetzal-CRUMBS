import sqlite3
from optparse import OptionParser
import os
import re

def retrieve_parameters(database, table, rowid, header=True):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    # Check that table is properly named
    if table == "quetzal_EGG_1" :
        cursor.execute("SELECT N_0, K_suit, r, emigrant_rate, duration, p_K, scale_tree FROM quetzal_EGG_1 WHERE rowid = ?", rowid)
    else :
        raise NotImplementedError("Error when setting option table: should be quetzal_EGG_n, where n = 1.")
    buffer = ""
    if(header):
        buffer += "N_0 K_suit r emigrant_rate duration p_K scale_tree\n"
    records = row.fetchone()
    records = [str(i) for i in records]
    buffer+=(" ".join(records))
    buffer+="\n"
    conn.close()
    return buffer

def main(argv):
    parser = OptionParser()
    parser.add_option("--database", type="str", dest="database", help="path to database")
    parser.add_option("--table", type="str", dest="table", help="what simulation core table to use")
    parser.add_option("--rowid", type="str", dest="rowid", help="what rowid to retrieve")
    parser.add_option('--header', help='add header of summary statistics', dest = 'header', default = true, action = 'store_true')
    (options, args) = parser.parse_args()
    print(retrieve_parameters(options.database, options.table, options.rowid, options.header))

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
