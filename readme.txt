import pandas as pd

# Read the excel files
consolidated_df = pd.read_excel("Consolidated_EDG.xlsx")
edl_df = pd.read_excel("EDL.xlsx")

# Drop records where Attribute Registry ID or Assigned Attribute Registry ID is empty
edl_df = edl_df.dropna(subset=['Attribute Registry ID', 'Assigned Attribute Registry ID'], how='all')

# Merge information from Consolidated_EDG.xlsx to add Attribute Name and Domain
edl_merged_df = edl_df.merge(consolidated_df, how='left', left_on='Attribute Registry ID', right_on='Attribute ID')
edl_merged_df.rename(columns={'Attribute Name': 'Attribute Name (Registry ID)', 'Domain': 'Domain (Registry ID)'}, inplace=True)

edl_merged_df = edl_merged_df.merge(consolidated_df, how='left', left_on='Assigned Attribute Registry ID', right_on='Attribute ID')
edl_merged_df.rename(columns={'Attribute Name': 'Attribute Name (Assigned Registry ID)', 'Domain': 'Domain (Assigned Registry ID)'}, inplace=True)

# Drop the redundant columns
edl_merged_df.drop(columns=['Attribute ID_x', 'Attribute ID_y'], inplace=True)

# Create separate sheets for count of occurrences of each attribute ID
attribute_registry_counts = edl_merged_df['Attribute Registry ID'].value_counts().reset_index()
attribute_registry_counts.columns = ['Attribute Registry ID', 'Count']
attribute_registry_counts = attribute_registry_counts.merge(consolidated_df, how='left', left_on='Attribute Registry ID', right_on='Attribute ID')
attribute_registry_counts.rename(columns={'Attribute Name': 'Attribute Name (Registry ID)', 'Domain': 'Domain (Registry ID)'}, inplace=True)

assigned_attribute_registry_counts = edl_merged_df['Assigned Attribute Registry ID'].value_counts().reset_index()
assigned_attribute_registry_counts.columns = ['Assigned Attribute Registry ID', 'Count']
assigned_attribute_registry_counts = assigned_attribute_registry_counts.merge(consolidated_df, how='left', left_on='Assigned Attribute Registry ID', right_on='Attribute ID')
assigned_attribute_registry_counts.rename(columns={'Attribute Name': 'Attribute Name (Assigned Registry ID)', 'Domain': 'Domain (Assigned Registry ID)'}, inplace=True)

# Write to Excel file with two separate sheets
with pd.ExcelWriter('Report.xlsx') as writer:
    edl_merged_df.to_excel(writer, index=False, sheet_name='Merged Data')
    attribute_registry_counts.to_excel(writer, index=False, sheet_name='Attribute Registry ID Counts')
    assigned_attribute_registry_counts.to_excel(writer, index=False, sheet_name='Assigned Attribute Registry ID Counts')
