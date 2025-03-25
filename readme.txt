name_col = rename_dict.get('Name', 'Name')

for change_type, group in df_merged.groupby('Change Type'):
    report_lines.append(f"{change_type} ({len(group)} records):")
    if change_type == 'New Attribute':
        report_lines.extend([f"- {row[key_col]}: {row[name_col]}" for _, row in group.iterrows()])
    elif change_type == 'Modified Attribute':
        modified_records = [f"- {row[key_col]}: {row['Tool Comments']}" for _, row in group.iterrows() if row['Tool Comments']]
        report_lines.extend(modified_records)
    else:
        report_lines.extend([f"- {row[key_col]}" for _, row in group.iterrows()])
    report_lines.append("\n")
