import sqlite3
from optparse import OptionParser
import os
import re

# options
parser = OptionParser()
parser.add_option("--database", type="str", dest="database", help="path to database")
parser.add_option("--table", type="str", dest="table", help="what simulation core table to use")
parser.add_option("--output", type="str", dest="output", help="output file name")

(options, args) = parser.parse_args()
conn = sqlite3.connect(options.database)

cursor = conn.cursor()
print(options.output)
outfile = open(options.output,'w')
outfile.write("N K r m g p s\n")

cursor.execute("SELECT N_0, K_suit, r, emigrant_rate, duration, p_K, scale_tree FROM core4_pods")
for row in cursor:
    # do_stuff_with_row
    row = [str(i) for i in row]
    outfile.write(" ".join(row))
    outfile.write("\n")

outfile.close()
conn.close()
