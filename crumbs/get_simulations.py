import sqlite3
from optparse import OptionParser
import os
import re

def get_simulations(database, table, failed_only=False):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    if table == "quetzal_EGG_1" :
        if failed_only :
            cursor.execute("SELECT rowid, * FROM quetzal_EGG_1 WHERE newicks = '';")
        else :
            cursor.execute("SELECT rowid, * FROM quetzal_EGG_1 WHERE newicks <> '';")
    else :
        Exception("Error when setting option table: should be quetzal_EGG_n, where n = 1.")

    records = cursor.fetchall()
    rowids = list()
    for row in records:
        ids.append(row[0])
    conn.close()
    return rowids

def main(argv):
    parser = OptionParser()
    parser.add_option("--database", type="str", dest="database", help="path to SQLite database")
    parser.add_option("--table", type="str", dest="table", help="what quetzal-EGG was used (eg: quetzal_EGG_1)")
    parser.add_option("--failed-only", type="bool", dest="failed_only", default=False, help="Only failed simulations")
    (options, args) = parser.parse_args(argv)
    return get_simulations(options.database, options.table, options.failed_only)

if __name__ == '__main__':
    main(sys.argv[1:])
