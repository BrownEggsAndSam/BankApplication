import pandas as pd

# Read Excel files
consolidated_df = pd.read_excel('Consolidated_EDG.xlsx')
edl_df = pd.read_excel('EDL.xlsx')

# Drop records where Attribute Registry ID and Assigned Attribute Registry ID are empty
edl_df.dropna(subset=['Attribute Registry ID', 'Assigned Attribute Registry ID'], how='all', inplace=True)

# Save the modified DataFrame to a new Excel file
edl_df.to_excel('EDL_Dropped.xlsx', index=False)
