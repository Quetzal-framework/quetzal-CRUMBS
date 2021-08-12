import sqlite3
from optparse import OptionParser
import evolve

# options
parser = OptionParser()
parser.add_option("--database", type="str", dest="database", help="path to database - must contain a pods table")
parser.add_option("--rowid", type="str", dest="rowid", help="what row in the database table")
parser.add_option("--sequence_size", type="int", dest="sequence_size", help="sequence_size")
parser.add_option("--scale_tree", type="float", dest="scale_tree", help="scale tree branch length")
parser.add_option("--output", type="str", dest="filename", help="output file name")

(options, args) = parser.parse_args()
conn = sqlite3.connect(options.database)

try:
    conn.execute("ALTER TABLE pods ADD COLUMN scale_tree DOUBLE")
except Exception:
    pass

try:
    conn.execute("ALTER TABLE pods ADD COLUMN sequence_size INTEGER")
except Exception:
    pass

cursor = conn.cursor()

t = (options.rowid,)
cursor.execute('SELECT newicks FROM pods WHERE rowid=?', t)
record = cursor.fetchone()
trees = record[0].split("\n\n")
evolve(trees, options.sequence_size, options.scale_tree, options.filename)

cursor.execute('''UPDATE core4_pods SET scale_tree = ? WHERE rowid = ?''', (options.scale_tree, options.rowid))
cursor.execute('''UPDATE core4_pods SET sequence_size = ? WHERE rowid = ?''', (options.sequence_size, options.rowid))
conn.commit()
