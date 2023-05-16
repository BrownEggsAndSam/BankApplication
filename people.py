import pandas as pd

def create_sql_table_from_excel(excel_file, sheet_name, table_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    create_table_query = f'CREATE TABLE {table_name} (\n'

    for column in df.columns:
        # Check if the first row of data is numeric or not
        if pd.api.types.is_numeric_dtype(df[column]):
            sql_type = 'INT'
        else:
            sql_type = 'VARCHAR(255)'

        create_table_query += f'  {column} {sql_type},\n'

    create_table_query = create_table_query.rstrip(',\n') + '\n);'

    return create_table_query

# Usage
excel_file = 'your_file.xlsx'
sheet_name = 'Sheet1' # Change this to your sheet name
table_name = 'your_table' # Change this to your desired table name

print(create_sql_table_from_excel(excel_file, sheet_name, table_name))
