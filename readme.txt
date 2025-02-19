import pandas as pd
import itertools
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Read Excel file
df = pd.read_excel("Audit_Projects/C&E/Privacy Programs/CF0SDIAD-2684/Enterprise Data Glossary.xlsx")

# Keep only relevant columns and ensure unique values
key = df[['Attribute Registry ID', 'Name', 'Definition', 'Privacy Designation', 'CreatedOn']].drop_duplicates()

print(f"✅ Loaded {len(key)} unique records from the dataset.")

# ------------------- JACCARD SIMILARITY FUNCTION -------------------
def jaccard_similarity(str1, str2):
    set1, set2 = set(str1.lower().split()), set(str2.lower().split())
    return len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0

# Group similar definitions
threshold = 0.6  # Similarity threshold (adjust if needed)
grouped_dict = {}
group_counter = 0

for idx, row in key.iterrows():
    definition = row['Definition']
    matched_group = None

    # Find an existing group with high similarity
    for group, definitions in grouped_dict.items():
        if any(jaccard_similarity(definition, existing_def) >= threshold for existing_def in definitions):
            matched_group = group
            break

    # Assign to existing group or create a new one
    if matched_group:
        grouped_dict[matched_group].append(definition)
    else:
        grouped_dict[f"group_{group_counter}"] = [definition]
        group_counter += 1

# Create a mapping of definitions to grouped strings
definition_to_group = {definition: group for group, definitions in grouped_dict.items() for definition in definitions}
key['grouped_str'] = key['Definition'].map(definition_to_group)

print(f"✅ Grouped {len(grouped_dict)} unique definition clusters using Jaccard similarity.")

# Standardize grouped string values
key['grouped_str'] = key['grouped_str'].str.lower().str.strip()

# ------------------- CREATE SUMMARY TABLE -------------------
key_summary = key.groupby(['grouped_str', 'Privacy Designation']).size().unstack(fill_value=0)
key_summary.reset_index(inplace=True)

# Identify discrepancies in privacy designation
key_summary['potential_discrepancy'] = (
    (key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI', 0) > 0) |
    (key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI In Combination - Personally Identifiable', 0) > 0) |
    (key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI In Combination - Not Publicly Available', 0) > 0)
)

# Filter for potential discrepancies
potential_observation = key_summary[key_summary['potential_discrepancy']]

print(f"⚠️ Found {len(potential_observation)} potential discrepancies in privacy designation.")

# ------------------- MERGE BACK TO ATTRIBUTE IDs -------------------
potential_observation_ids = pd.merge(potential_observation, key, on="grouped_str", how="left")

# Rearrange columns for better readability
final_columns = [
    'Attribute Registry ID', 'Name', 'Definition', 'Privacy Designation', 'CreatedOn',
    'grouped_str', 'Not NPI', 'NPI In Combination - Personally Identifiable', 
    'NPI In Combination - Not Publicly Available', 'NPI', 'potential_discrepancy'
]
potential_observation_ids = potential_observation_ids[final_columns]

# Save results to an Excel file
output_file = "Audit_Projects/C&E/Privacy Programs/CF0SDIAD-2684/NPI_example.xlsx"
potential_observation_ids.to_excel(output_file, index=False)

print(f"✅ Results saved to {output_file}.")
