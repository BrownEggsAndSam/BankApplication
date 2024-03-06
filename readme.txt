import pandas as pd

# Read the dropped EDL file
edl_dropped_df = pd.read_excel('EDL_Dropped.xlsx')

# Count occurrences of each unique 'Attribute Registry ID'
attribute_registry_counts = edl_dropped_df['Attribute Registry ID'].value_counts().reset_index()
attribute_registry_counts.columns = ['Attribute Registry ID', 'Count']

# Save the counts to a new Excel workbook
with pd.ExcelWriter('Attribute_Registry_Counts.xlsx') as writer:
    attribute_registry_counts.to_excel(writer, index=False)
