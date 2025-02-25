import pandas as pd
import os
from fuzzywuzzy import process, fuzz
from tqdm import tqdm

def trim_all_columns(df):
    trim_strings = lambda x: x.strip() if isinstance(x, str) else x
    return df.applymap(trim_strings)

# Define input and output paths
package_input_path = './__rationalizationTool/input/'
package_output_path = './__rationalizationTool/output/'
edgDataDictionary = 'EDG.xlsx'
requestFile = 'Request.xlsx'
output_file = 'Results.xlsx'

# Read and clean data
print("Loading EDG data...")
edg_df = trim_all_columns(pd.read_excel(os.path.join(package_input_path, edgDataDictionary)))
print("Loading Request data...")
request_df = trim_all_columns(pd.read_excel(os.path.join(package_input_path, requestFile)))

# Extract relevant columns
edg_df = edg_df[['Attribute ID', 'Attribute Name', 'Attribute Definition']]
request_df = request_df[['Attribute ID', 'Physical Name', 'Logical Name', 'Definition']]

# Perform fuzzy matching
print("Performing fuzzy matching...")
matched_results = []

for _, req_row in tqdm(request_df.iterrows(), total=len(request_df)):
    req_def = req_row['Definition']
    matches = process.extract(req_def, edg_df['Attribute Definition'], scorer=fuzz.token_sort_ratio, limit=5)
    
    for match in matches:
        matched_results.append({
            'Request Attribute ID': req_row['Attribute ID'],
            'Physical Name': req_row['Physical Name'],
            'Logical Name': req_row['Logical Name'],
            'Request Definition': req_def,
            'Matched Attribute ID': edg_df.loc[edg_df['Attribute Definition'] == match[0], 'Attribute ID'].values[0],
            'Matched Attribute Name': edg_df.loc[edg_df['Attribute Definition'] == match[0], 'Attribute Name'].values[0],
            'Matched Definition': match[0],
            'Similarity Score': match[1]
        })

# Convert results to DataFrame
result_df = pd.DataFrame(matched_results)

# Save to Excel
output_path = os.path.join(package_output_path, output_file)
print(f"Saving results to {output_path}...")
result_df.to_excel(output_path, index=False)

print("Processing complete!")

