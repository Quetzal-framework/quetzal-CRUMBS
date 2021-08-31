import sqlite3
from optparse import OptionParser
import os, re, sys

def get_successful_simulations_rowids(database, table):
    """Prints the rowids of simulations registered in the database.

    Parameters
    ----------
    database : str
        The path to the sqlite database.

    table : str
        The name of the database table to read from

    Raises
    ------
    NotImplementedError
        If the incorrect table name is passed as parameter.
    """
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    # Check that table is properly named
    if table == "quetzal_EGG_1" :
        cursor.execute("SELECT rowid, * FROM quetzal_EGG_1 WHERE newicks <> '';")
    else :
        raise NotImplementedError("Error when setting option table: should be quetzal_EGG_n, where n = 1.")
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
    (options, args) = parser.parse_args(argv)
    rreturnList = get_successful_simulations_rowids(options.database, options.table)
    returnStr = ''
    for item in returnList:
        returnStr += str(item)+' '
    print(returnStr)

if __name__ == '__main__':
    import sys
    main(sys.argv[1:])
