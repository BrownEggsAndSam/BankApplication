import pandas as pd
import os

# Backend
package_backend_path = './__glossaryDifferenceScript/backend/backend.xlsx'

# Define file paths
package_input_path = './__glossaryDifferenceScript/input/'
package_output_path = './__glossaryDifferenceScript/output/'
edgDataDictionaryReference = package_input_path + 'EDG_Ref.xlsx'
edgDataDictionaryCurrent = package_input_path + 'EDG_Current.xlsx'
output_file = package_output_path + 'EDG_Difference.xlsx'
output_text_file = package_output_path + 'EDG_Difference_Report.txt'

# Ensure output directory exists
os.makedirs(package_output_path, exist_ok=True)

print("Loading reference and current EDG files...")
df_ref = pd.read_excel(edgDataDictionaryReference)
df_current = pd.read_excel(edgDataDictionaryCurrent)
df_backend = pd.read_excel(package_backend_path, sheet_name='Rename', header=None, names=['Old', 'New'])

# Rename columns based on backend mapping
rename_dict = dict(zip(df_backend['Old'], df_backend['New']))
df_ref.rename(columns=rename_dict, inplace=True)
df_current.rename(columns=rename_dict, inplace=True)

key_col = rename_dict.get('Attribute Registry ID', 'Attribute Registry ID')

print("Merging datasets to identify differences...")
df_merged = df_ref.merge(df_current, on=key_col, how='outer', suffixes=('_Ref', '_Current'), indicator=True)

def generate_tool_comment(row):
    changes = []
    for col in df_ref.columns:
        if col == key_col:
            continue
        ref_value, cur_value = row.get(f'{col}_Ref'), row.get(f'{col}_Current')
        if pd.isna(ref_value) and not pd.isna(cur_value):
            changes.append(f"New: {col} set to {cur_value}")
        elif not pd.isna(ref_value) and pd.isna(cur_value):
            changes.append(f"Removed: {col} was {ref_value}")
        elif ref_value != cur_value:
            changes.append(f"Updated: {col} changed from {ref_value} to {cur_value}")
    return '; '.join(changes) if changes else 'No Changes'

df_merged['Tool Comments'] = df_merged.apply(generate_tool_comment, axis=1)

# Categorize changes
df_merged['Change Type'] = df_merged['_merge'].map({
    'left_only': 'Deleted Attribute',
    'right_only': 'New Attribute',
    'both': 'Modified Attribute'
})
df_merged.drop(columns=['_merge'], inplace=True)

print("Saving differences to output Excel file...")
df_merged.to_excel(output_file, index=False)

# Save summary report to text file
print("Generating text report...")
report_lines = ["EDG Data Dictionary Difference Report", "===================================\n"]
for change_type, group in df_merged.groupby('Change Type'):
    report_lines.append(f"{change_type} ({len(group)} records):")
    report_lines.extend([f"- {row[key_col]}: {row['Tool Comments']}" for _, row in group.iterrows()])
    report_lines.append("\n")

with open(output_text_file, 'w') as f:
    f.write('\n'.join(report_lines))

print("Comparison complete. Results saved to output folder.")
