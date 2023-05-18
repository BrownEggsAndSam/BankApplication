# import pandas as pd

file_path = './Big NLP Tool/PDD+DSET/'

# # Read the Excel files
# pdd_df = pd.read_excel(file_path + 'PDD.xlsx')
# dset_df = pd.read_excel(file_path + 'DSET.xlsx')

# # Concatenate DataFrames
# combined_df = pd.concat([pdd_df, dset_df], ignore_index=True)
# print(combined_df)

# # Filter rows based on Attribute ID pattern
# valid_pattern = r'^ATTR\d{5}$'
# valid_rows = combined_df['Attribute ID'].str.match(valid_pattern)
# valid_df = combined_df[valid_rows]
# invalid_df = combined_df[~valid_rows]

# # Count occurrences of unique groupings of Physical Name and Attribute ID
# grouped_df = valid_df.groupby(['Physical Name', 'Attribute ID']).size().reset_index(name='Count of Groupings')

# # Save the result to a new Excel file
# grouped_df.to_excel(file_path + 'Occurances.xlsx', index=False)
# invalid_df.to_excel(file_path + 'Invalid_Attribute_IDs.xlsx', index=False)


import pandas as pd
import re

# Read the Excel files
pdd = pd.read_excel(file_path + "PDD.xlsx")
dset = pd.read_excel(file_path + "DSET.xlsx")

# Merge the PDD and DSET DataFrames
pdd["PDD+DSETID"] = pdd["PDD ID"]
dset["PDD+DSETID"] = dset["DSET ID"]
merged = pd.concat([pdd, dset], ignore_index=True).drop(columns=["PDD ID", "DSET ID"])
print(merged)

# Filter rows based on the Attribute ID pattern
attr_pattern = re.compile(r"ATTR\d{5}$")
valid_rows = merged[merged["Attribute ID"].apply(lambda x: bool(attr_pattern.match(x)))]
invalid_rows = merged[merged["Attribute ID"].apply(lambda x: not bool(attr_pattern.match(x)))]

# Count unique groupings and save the result to an Excel file
grouped = valid_rows.groupby(["Physical Name", "Attribute ID"]).size().reset_index(name="Count of Groupings")
grouped.to_excel(file_path + "Occurances.xlsx", index=False)

# Save invalid rows to an Excel file
invalid_rows.to_excel(file_path + "Invalid_Attribute_IDs.xlsx", index=False)    