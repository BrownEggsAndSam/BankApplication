import pyodbc
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML

# Function to extract table names from SQL query
def extract_tables(sql):
    tables = []
    parsed = sqlparse.parse(sql)

    for item in parsed:
        for token in item.tokens:
            if isinstance(token, IdentifierList):
                for identifier in token.get_identifiers():
                    tables.append(str(identifier))
            elif isinstance(token, Identifier):
                tables.append(str(token))
            elif token.ttype == Keyword and token.value.upper() == "FROM":
                tables.append(str(token))

    return tables

# Connect to AccessDB
conn_str = (
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    r"DBQ=path\to\your\database.accdb;"
)
conn = pyodbc.connect(conn_str)

# Pick a query (replace 'your_query_name' with the actual query name)
query_name = "your_query_name"
sql = ""

cursor = conn.cursor()
for row in cursor.tables(tableType="VIEW"):
    if row.table_name == query_name:
        cursor2 = conn.cursor()
        cursor2.execute(f"SELECT * FROM {query_name}")
        sql = cursor2.getdescription()

# Show the table's data lineage
if sql:
    tables = extract_tables(sql)
    print("Data lineage (tables):", tables)
else:
    print(f"No query found with the name '{query_name}'")

cursor.close()
conn.close()
