import pandas as pd
from fuzzywuzzy import fuzz, process
from itertools import combinations

# Load the Excel file
df = pd.read_excel("Audit_Projects/C&E/Privacy Programs/CF0SDIAD-2684/Enterprise Data Glossary.xlsx")

# Select relevant columns and drop duplicates
key = df[['Attribute Registry ID', 'Name', 'Definition', 'Privacy Designation', 'CreatedOn']].drop_duplicates()

# Function to group similar definitions using fuzzy matching
def group_similar_definitions(definitions, threshold=60):
    groups = {}
    for d1, d2 in combinations(definitions, 2):
        if fuzz.token_sort_ratio(d1, d2) >= threshold:
            if d1 in groups:
                groups[d2] = groups[d1]
            elif d2 in groups:
                groups[d1] = groups[d2]
            else:
                groups[d1] = d1
                groups[d2] = d1
    return [groups.get(d, d) for d in definitions]

# Apply fuzzy grouping
key['grouped_str'] = group_similar_definitions(key['Definition'].tolist())
key['grouped_str'] = key['grouped_str'].str.lower().str.strip()

# Count occurrences of each privacy designation per grouped string
key_summary = key.groupby(['grouped_str', 'Privacy Designation']).size().unstack(fill_value=0)

# Identify discrepancies where an attribute appears under conflicting privacy designations
key_summary['potential_discrepancy'] = (
    (key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI', 0) > 0) |
    (key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI In Combination - Personally Identifiable', 0) > 0) |
    (key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI In Combination - Not Publicly Available', 0) > 0)
)

# Filter out discrepancies
potential_observation = key_summary[key_summary['potential_discrepancy']]

# Merge with original key to get attribute details
potential_observation_ids = potential_observation.merge(key, on='grouped_str', how='left')

# Reorder columns
columns = ['Attribute Registry ID', 'Name', 'Definition', 'Privacy Designation', 'CreatedOn', 'grouped_str',
           'Not NPI', 'NPI In Combination - Personally Identifiable', 'NPI In Combination - Not Publicly Available', 'NPI', 'potential_discrepancy']
potential_observation_ids = potential_observation_ids.reindex(columns=columns, fill_value=0)

# Save to Excel
potential_observation_ids.to_excel("Audit_Projects/C&E/Privacy Programs/CF0SDIAD-2684/NPI_example.xlsx", index=False)
