import pandas as pd

# Read the dropped EDL file and the Consolidated EDG file
edl_dropped_df = pd.read_excel('EDL_Dropped.xlsx')
consolidated_df = pd.read_excel('Consolidated_EDG.xlsx')

# Merge the dataframes on 'Attribute Registry ID' and 'Assigned Attribute Registry ID'
merged_df = pd.merge(edl_dropped_df, consolidated_df, left_on='Attribute Registry ID', right_on='Attribute ID', suffixes=('_left', '_right'))
merged_df = pd.merge(merged_df, consolidated_df, left_on='Assigned Attribute Registry ID', right_on='Attribute ID', suffixes=('_left', '_right'))

# Drop unnecessary columns
merged_df.drop(['Attribute ID_left', 'Attribute ID_right'], axis=1, inplace=True)

# Save the merged DataFrame to a new Excel file
merged_df.to_excel('EDL_Merged.xlsx', index=False)
