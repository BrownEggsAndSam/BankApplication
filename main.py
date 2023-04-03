import os
import sqlparse
from collections import defaultdict
from sqlparse.sql import IdentifierList, Identifier, Function, Parenthesis
from sqlparse.tokens import Keyword, DML, Name

def extract_tables_and_columns(parsed):
    tables_columns = defaultdict(set)

    for token in parsed.tokens:
        if isinstance(token, IdentifierList):
            for identifier in token.get_identifiers():
                if isinstance(identifier, Identifier):
                    column = str(identifier)
                    table, _, _ = column.partition(".")
                    tables_columns[table].add(column)
        elif isinstance(token, Identifier):
            column = str(token)
            table, _, _ = column.partition(".")
            tables_columns[table].add(column)

    return tables_columns

def extract_join(parsed):
    join_type = None
    join_condition = None
    join_found = False

    for token in parsed.tokens:
        if token.ttype == Keyword and token.value.upper() in ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"]:
            join_type = token.value
            join_found = True
        elif join_found and token.ttype == Keyword and token.value.upper() == "ON":
            for sibling in token.parent.tokens[token.parent.token_index(token):]:
                if sibling.ttype not in [Keyword, Name]:
                    join_condition = str(sibling)
                    break
            break

    return join_type, join_condition

def read_sql_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()

# Read SQL script from input.txt
input_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input", "input.txt")
sql = read_sql_file(input_file)

# Parse SQL script and extract tables, columns, and join information
parsed = sqlparse.parse(sql)[0]
tables_columns = extract_tables_and_columns(parsed)
join_type, join_condition = extract_join(parsed)

# Print in-depth analysis
print("Tables used:", ', '.join(tables_columns.keys()))
print("Columns used from each table:")
for table, columns in tables_columns.items():
    print(f"{table}: {', '.join(columns)}")

if join_type and join_condition:
    print("Join operation:")
    print(f"  - Type: {join_type}")
    print(f"  - Join condition: {join_condition}")

# If the SQL script has an ORDER BY clause
if parsed.token_first(skip_ws=True, skip_cm=True).value.upper() == "SELECT":
    orderby_found = False
    for token in parsed.tokens:
        if token.ttype == Keyword and token.value.upper() == "ORDER":
            orderby_found = True
        elif orderby_found and token.ttype == Keyword and token.value.upper() == "BY":
            order_columns = [str(t) for t in token.parent.tokens[token.parent.token_index(token) + 1:][0].get_identifiers()]
            print("Ordering:")
            print(f"  - Columns: {', '.join(order_columns)}")
            break
