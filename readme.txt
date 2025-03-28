import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

# -------------------------
# Global paths & constants
# -------------------------
package_backend_path = './__glossaryDifferenceScript/backend/backend.xlsx'
package_input_path = './__glossaryDifferenceScript/input/'
package_output_path = './__glossaryDifferenceScript/output/'
output_file = os.path.join(package_output_path, 'EDG_Difference.xlsx')
report_txt_file = os.path.join(package_output_path, 'EDG_Difference_Report.txt')

# -------------------------
# Function: Load Rename Mapping
# -------------------------
def load_rename_mapping():
    try:
        rename_df = pd.read_excel(package_backend_path, sheet_name='Rename')
        # Assume Column A: original field, Column B: new field name
        rename_mapping = dict(zip(rename_df.iloc[:, 0], rename_df.iloc[:, 1]))
        return rename_mapping
    except Exception as e:
        print(f"Error loading rename mapping: {e}")
        return {}

# -------------------------
# Function: Load an EDG Excel file
# -------------------------
def load_edg_file(filepath):
    try:
        xls = pd.ExcelFile(filepath)
        if 'Data Glossary' in xls.sheet_names:
            # For files with a 'Data Glossary' sheet:
            df = pd.read_excel(xls, sheet_name='Data Glossary')
            expected_cols = ['Attribute Name', 'Attribute Registry ID', 'Definition', 'Status', 
                             'Business Segment', 'KDE', 'Privacy Designation', 'Authoritative Source', 'Domain']
            # Select only columns that exist
            df = df[[col for col in expected_cols if col in df.columns]]
        else:
            # For alternative formats, read the first sheet and search for expected fields
            df = pd.read_excel(filepath)
            # Map the expected field names to actual columns found (using case-insensitive search)
            alternative_fields = {
                'Attribute Registry ID': None,
                'Name': None,
                'Definition': None,
                '[Asset] is classified by [Business Dimension] > Name': None,
                '[Business Term] system of record [Technology Asset] > Name': None,
                'KDE': None,
                'Privacy Designation': None,
                'Authoritative Source': None,
                'Status': None
            }
            selected_cols = {}
            for field in alternative_fields.keys():
                for col in df.columns:
                    if field.lower() in col.lower():
                        selected_cols[field] = col
                        break
            if not selected_cols:
                raise ValueError("The file format is not recognized.")
            # Subset and then rename columns to standard names
            df = df[list(selected_cols.values())]
            rename_cols = {v: k for k, v in selected_cols.items()}
            df.rename(columns=rename_cols, inplace=True)
        return df
    except Exception as e:
        raise ValueError(f"Error loading file {filepath}: {e}")

# -------------------------
# Function: Consolidate duplicate records
# -------------------------
def consolidate_duplicates(df):
    # Example consolidation for the two columns that might be duplicated.
    asset_col = '[Asset] is classified by [Business Dimension] > Name'
    tech_col = '[Business Term] system of record [Technology Asset] > Name'
    if asset_col in df.columns and tech_col in df.columns:
        def consolidate_group(group):
            # Consolidate values for the asset/tech columns by combining unique non-null entries
            asset_vals = group[asset_col].dropna().unique().tolist()
            tech_vals = group[tech_col].dropna().unique().tolist()
            combined = list(set(asset_vals + tech_vals))
            consolidated_value = ", ".join(combined)
            # For simplicity, take the first value for other columns
            row = group.iloc[0]
            row[asset_col] = consolidated_value
            row[tech_col] = consolidated_value
            return row
        df = df.groupby('Attribute Registry ID', as_index=False).apply(consolidate_group)
        # After groupby+apply, the index might be non-sequential; reset if needed.
        df.reset_index(drop=True, inplace=True)
    return df

# -------------------------
# Function: Compare the two EDG DataFrames
# -------------------------
def compare_dataframes(df_ref, df_current):
    # Compare on 'Attribute Registry ID'
    common_cols = list(set(df_ref.columns).intersection(set(df_current.columns)))
    if 'Attribute Registry ID' in common_cols:
        common_cols.remove('Attribute Registry ID')
    
    # Merge the two dataframes to detect differences, new, and deleted records
    merged = pd.merge(df_ref, df_current, on='Attribute Registry ID', how='outer',
                      suffixes=('_ref', '_current'), indicator=True)
    
    differences = []
    for _, row in merged.iterrows():
        attr_id = row['Attribute Registry ID']
        diff_comment = []
        if row['_merge'] == 'both':
            for col in common_cols:
                ref_val = row.get(f"{col}_ref")
                curr_val = row.get(f"{col}_current")
                # Compare values (treating NaN as equal)
                if pd.isna(ref_val) and pd.isna(curr_val):
                    continue
                if (pd.isna(ref_val) and not pd.isna(curr_val)) or (not pd.isna(ref_val) and pd.isna(curr_val)) or str(ref_val) != str(curr_val):
                    diff_comment.append(f"{col}: '{ref_val}' -> '{curr_val}'")
            if diff_comment:
                differences.append({
                    'Attribute Registry ID': attr_id,
                    'Tool Comments': "; ".join(diff_comment)
                })
        elif row['_merge'] == 'left_only':
            differences.append({
                'Attribute Registry ID': attr_id,
                'Tool Comments': 'Attribute deleted in current version.'
            })
        elif row['_merge'] == 'right_only':
            differences.append({
                'Attribute Registry ID': attr_id,
                'Tool Comments': 'New attribute added in current version.'
            })
    diff_df = pd.DataFrame(differences)
    return merged, diff_df

# -------------------------
# Main processing function
# -------------------------
def process_files(edg_ref_file, edg_current_file):
    # Load the rename mapping
    rename_mapping = load_rename_mapping()
    
    try:
        df_ref = load_edg_file(edg_ref_file)
        df_current = load_edg_file(edg_current_file)
    except ValueError as e:
        return str(e)
    
    # Apply rename mapping if applicable
    if rename_mapping:
        df_ref.rename(columns=rename_mapping, inplace=True)
        df_current.rename(columns=rename_mapping, inplace=True)
    
    # Consolidate duplicates if necessary
    df_ref = consolidate_duplicates(df_ref)
    df_current = consolidate_duplicates(df_current)
    
    # Compare the two dataframes
    merged_df, diff_df = compare_dataframes(df_ref, df_current)
    
    # Save the Excel difference report and write a text summary report
    try:
        diff_df.to_excel(output_file, index=False)
        with open(report_txt_file, 'w') as f:
            f.write("EDG Difference Report\n")
            f.write(f"Reference file: {edg_ref_file}\n")
            f.write(f"Current file: {edg_current_file}\n")
            f.write(f"Output file: {output_file}\n\n")
            f.write(f"Total differences: {len(diff_df)}\n")
            for _, row in diff_df.iterrows():
                f.write(f"Attribute Registry ID: {row['Attribute Registry ID']} - {row['Tool Comments']}\n")
        return "Processing completed successfully."
    except Exception as e:
        return f"Error saving output: {e}"

# -------------------------
# Tkinter GUI for user interaction
# -------------------------
def run_gui():
    root = tk.Tk()
    root.title("EDG Difference Reporter")
    
    edg_ref_file = tk.StringVar()
    edg_current_file = tk.StringVar()
    status_text = tk.StringVar()
    
    def browse_ref_file():
        filename = filedialog.askopenfilename(
            initialdir=package_input_path,
            title="Select Reference EDG File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        edg_ref_file.set(filename)
    
    def browse_current_file():
        filename = filedialog.askopenfilename(
            initialdir=package_input_path,
            title="Select Current EDG File",
            filetypes=[("Excel Files", "*.xlsx *.xls")]
        )
        edg_current_file.set(filename)
    
    def process():
        ref = edg_ref_file.get()
        curr = edg_current_file.get()
        if not ref or not curr:
            messagebox.showerror("Error", "Please select both the reference and current EDG files.")
            return
        status_text.set("Processing...")
        root.update_idletasks()
        result = process_files(ref, curr)
        status_text.set(result)
        messagebox.showinfo("Processing Result", result)
    
    # Layout the GUI elements
    tk.Label(root, text="Reference EDG File:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
    tk.Entry(root, textvariable=edg_ref_file, width=50).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse", command=browse_ref_file).grid(row=0, column=2, padx=5, pady=5)
    
    tk.Label(root, text="Current EDG File:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
    tk.Entry(root, textvariable=edg_current_file, width=50).grid(row=1, column=1, padx=5, pady=5)
    tk.Button(root, text="Browse", command=browse_current_file).grid(row=1, column=2, padx=5, pady=5)
    
    tk.Button(root, text="Process", command=process).grid(row=2, column=1, pady=10)
    tk.Label(root, textvariable=status_text).grid(row=3, column=0, columnspan=3, pady=5)
    
    root.mainloop()

# -------------------------
# Entry point
# -------------------------
if __name__ == "__main__":
    run_gui()
