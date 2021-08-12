import sqlite3
from optparse import OptionParser
import os
import re

def get_simulations_rowids(database, table, failed=False):
    """Prints the rowids of simulations registered in the database.

    Parameters
    ----------
    database : str
        The path to the sqlite database.

    table : str
        The name of the database table to read from

    failed : bool
        If instead of successful simulations, only failed simulations should be retrieved.
    Raises
    ------
    NotImplementedError
        If the incorrect table name is passed as parameter.
    """
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    # Check that table is properly named
    if table == "quetzal_EGG_1" :
        if failed :
            cursor.execute("SELECT rowid, * FROM quetzal_EGG_1 WHERE newicks = '';")
        else :
            cursor.execute("SELECT rowid, * FROM quetzal_EGG_1 WHERE newicks <> '';")
    else :
        NotImplementedError("Error when setting option table: should be quetzal_EGG_n, where n = 1.")
    # Build the rowids list
    records = cursor.fetchall()
    rowids = list()
    for row in records:
        rowids.append(row[0])
    conn.close()
    # return the result
    return rowids

def main(argv):
    parser = OptionParser()
    parser.add_option("--database", type="str", dest="database", help="path to SQLite database")
    parser.add_option("--table", type="str", dest="table", help="what quetzal-EGG was used (eg: quetzal_EGG_1)")
    parser.add_option("--failed", type="bool", dest="failed", default=False, help="only retrieve failed simulations")
    (options, args) = parser.parse_args(argv)
    return get_simulations_rowids(options.database, options.table, options.failed)

if __name__ == '__main__':
    main(sys.argv[1:])
