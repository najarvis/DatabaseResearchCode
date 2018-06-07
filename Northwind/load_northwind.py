"""Loads and exports the northwind data into csv files"""

import sqlite3
import csv
from py2neo import Graph, authenticate, DBMS

authenticate('localhost:7474', 'neo4j', 'password')

my_dbms = DBMS()
import_dir = my_dbms.config["dbms.directories.import"]
print("Saving files to:", import_dir)

conn = sqlite3.connect('northwind.db')
sql_cursor = conn.cursor()

def execute_sql_file(filename):
    with open(filename) as sql_file:
        full_text = sql_file.read()
    lines = full_text.split(';')
    for line in lines:
        sql_cursor.execute(line + ';')
        conn.commit()

def export_csv(curs, name):
    headers = [desc[0] for desc in curs.description]
    with open('{}/{}.csv'.format(import_dir, name), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(list(curs))

def get_data_for_export():
    curs = sql_cursor.execute("SELECT * FROM orders " \
        "LEFT OUTER JOIN 'Order Details' ON 'Order Details'.OrderID = orders.OrderID")
    export_csv(curs, 'orders')
    tables = ['customers', 'suppliers', 'products', 'employees', 'categories']
    for table in tables:
        curs = sql_cursor.execute("SELECT * FROM {}".format(table))
        export_csv(curs, table)

def load_csv_to_neo():
    g = Graph(password='password')
    with open("load_relations.cypher") as f:
        file_string = f.read()
    queries = file_string.split(';')

    for query in queries:
        print("Running:\n", repr(query))
        g.run(query)

execute_sql_file('Northwind.Sqlite3.sql')
get_data_for_export()
load_csv_to_neo()

conn.close()
