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


Query 4: CMDB and Interface JOIN QUERY

producer_bus_catg_type
producer_sox_cd
producer_BHS_type
producer_tech_ownr
producer_bus_owner
producer_asset_type
consumer_bus_catg_type
consumer_sox_cd
consumer_BHS_type
consumer_tech_ownr
consumer_bus_owner
consumer_asset_type
Query 5: Load Dataflow_Details Table

producer_bus_catg_type
producer_sox_cd
producer_BHS_type
producer_tech_ownr
producer_bus_owner
producer_asset_type
consumer_bus_catg_type
consumer_sox_cd
consumer_BHS_type
consumer_tech_ownr
consumer_bus_owner
consumer_asset_type
Query 6: Load DEComplianceResults2 Table

producer_BHS_type
Producer_DGR_Rating
Consumer_DG_Rating
INTERFACE_EXMP_COMMENTS
DATAFLOW_EXP_COMMENTS
INTERFACE_REMEDIATION_COMMENTS
DATAFLOW_REMEDIATION_COMMENTS
INTERFACE_COMPLIANCE_FINAL
DATAFLOW_COMPLIANCE_FINAL
LinkToInterfaceDatasetFinal
ConsumerSTTMLocationFinal
CompletenessCheckPerformedFinal
InterfaceDesignPatternFinal
InterfaceDataFormatFinal
InterfaceDeliveryMechanismFinal
ControlMechanismTypeFinal
InterfaceResult
DataflowResult
