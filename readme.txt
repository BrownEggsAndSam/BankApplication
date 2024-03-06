import pandas as pd

# Read the attribute counts file and the Consolidated EDG file
attribute_counts_df = pd.read_excel('Attribute_Registry_Counts.xlsx')
consolidated_df = pd.read_excel('Consolidated_EDG.xlsx')

# Merge the dataframes on 'Attribute Registry ID'
merged_df = pd.merge(attribute_counts_df, consolidated_df[['Attribute ID', 'Attribute Name', 'Domain']], 
                     left_on='Attribute Registry ID', right_on='Attribute ID', how='left')

# Drop the 'Attribute ID' column as it's redundant
merged_df.drop('Attribute ID', axis=1, inplace=True)

# Save the merged DataFrame to a new Excel file
merged_df.to_excel('Merged_Attribute_Registry_Counts.xlsx', index=False)
