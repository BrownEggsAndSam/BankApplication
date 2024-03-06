# Read the dropped EDL file
edl_dropped_df = pd.read_excel('EDL_Dropped.xlsx')

# Filter records where both Attribute Registry ID and Assigned Attribute Registry ID are filled
both_filled_df = edl_dropped_df.dropna(subset=['Attribute Registry ID', 'Assigned Attribute Registry ID'], how='any')

# Add a column to check if Attribute Registry ID and Assigned Attribute Registry ID are the same
both_filled_df['Same ID'] = both_filled_df['Attribute Registry ID'] == both_filled_df['Assigned Attribute Registry ID']

# Count how many records have the same or different IDs
same_count = both_filled_df['Same ID'].sum()
different_count = len(both_filled_df) - same_count

# Create a separate sheet with the filtered records
with pd.ExcelWriter('EDL_Filtered.xlsx') as writer:
    both_filled_df.to_excel(writer, sheet_name='Filtered Data', index=False)

# Print the counts
print("Total records:", len(both_filled_df))
print("Records with same ID:", same_count)
print("Records with different ID:", different_count)
