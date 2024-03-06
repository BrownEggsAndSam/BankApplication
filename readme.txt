import pandas as pd

# Read the attribute counts and Consolidated EDG files
attribute_counts_df = pd.read_excel('Attribute_Registry_Counts.xlsx')
consolidated_df = pd.read_excel('Consolidated_EDG.xlsx')

# Merge the attribute counts with the Consolidated EDG data based on 'Attribute Registry ID'
merged_df = pd.merge(attribute_counts_df, consolidated_df, on='Attribute Registry ID', how='left')

# Save the merged DataFrame to a new Excel file
merged_df.to_excel('Merged_Attribute_Registry.xlsx', index=False)
