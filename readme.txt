import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.scrolledtext as st

# --------------------------
# Backend file paths
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
package_backend_path = os.path.join(BASE_DIR, '__glossaryDifferenceScript', 'backend', 'backend.xlsx')
package_input_path = os.path.join(BASE_DIR, '__glossaryDifferenceScript', 'input')
package_output_path = os.path.join(BASE_DIR, '__glossaryDifferenceScript', 'output')
output_file = os.path.join(package_output_path, 'EDG_Difference.xlsx')

# --------------------------
# Helper Functions
# --------------------------
def load_rename_mapping():
    """
    Load the rename mapping from the backend.xlsx file.
    Expected to have two columns: Column A (original) and Column B (new name).
    """
    if not os.path.exists(package_backend_path):
        print(f"Warning: Rename mapping file not found at {package_backend_path}. Continuing without renaming.")
        return {}
    try:
        rename_df = pd.read_excel(package_backend_path, sheet_name='Rename')
        mapping = dict(zip(rename_df.iloc[:, 0], rename_df.iloc[:, 1]))
        return mapping
    except Exception as e:
        print("Error loading rename mapping:", e)
        return {}

def read_edg_file(filepath):
    """
    Reads an EDG Excel file and returns a standardized DataFrame.
    Checks if a 'Data Glossary' sheet exists. If not, uses alternative expected columns.
    Consolidates duplicate Attribute Registry IDs if needed.
    """
    try:
        xls = pd.ExcelFile(filepath)
        if 'Data Glossary' in xls.sheet_names:
            df = pd.read_excel(xls, 'Data Glossary')
            required_cols = ['Attribute Name', 'Attribute Registry ID', 'Definition', 'Status', 
                             'Business Segment', 'KDE', 'Privacy Designation', 'Authoritative Source', 'Domain']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing columns in 'Data Glossary' sheet: {', '.join(missing_cols)}")
            df = df[required_cols]
        else:
            df = pd.read_excel(xls, xls.sheet_names[0])
            alt_cols = ['Attribute Registry ID', 'Name', 'Definition', 
                        '[Asset] is classified by [Business Dimension] > Name', 
                        '[Business Term] system of record [Technology Asset] > Name',
                        'KDE', 'Privacy Designation', 'Authoritative Source', 'Status']
            if 'Attribute Registry ID' not in df.columns:
                raise ValueError("EDG file missing key column 'Attribute Registry ID'")
            for col in alt_cols:
                if col not in df.columns:
                    df[col] = None
            df = df[alt_cols]
            # Consolidate duplicate records based on 'Attribute Registry ID'
            df = df.groupby('Attribute Registry ID', as_index=False).agg({
                'Name': 'first',
                'Definition': 'first',
                '[Asset] is classified by [Business Dimension] > Name': lambda x: ', '.join(sorted(set(str(i) for i in x if pd.notnull(i)))),
                '[Business Term] system of record [Technology Asset] > Name': lambda x: ', '.join(sorted(set(str(i) for i in x if pd.notnull(i)))),
                'KDE': 'first',
                'Privacy Designation': 'first',
                'Authoritative Source': 'first',
                'Status': 'first'
            })
        mapping = load_rename_mapping()
        if mapping:
            df.rename(columns=mapping, inplace=True)
        return df
    except Exception as e:
        raise ValueError(f"Error reading EDG file {filepath}: {e}")

def compare_edg_data(ref_df, curr_df, full_comparison=True):
    """
    Compare two EDG DataFrames using 'Attribute Registry ID' as the key.
    - For full comparison: performs an outer merge to report new attributes and deletions.
    - Otherwise: only records in EDG_Current (left merge) are considered.
    Creates a 'Tool Comments' column with a summary of changes.
    """
    if full_comparison:
        merged_df = pd.merge(ref_df, curr_df, on='Attribute Registry ID', how='outer', 
                             suffixes=('_ref', '_curr'), indicator=True)
    else:
        merged_df = pd.merge(curr_df, ref_df, on='Attribute Registry ID', how='left', 
                             suffixes=('_curr', '_ref'), indicator=True)
    tool_comments = []
    for idx, row in merged_df.iterrows():
        comments = []
        # Mark new or deleted attributes based on merge indicator
        if full_comparison:
            if row['_merge'] == 'left_only':
                comments.append("Attribute deleted")
            elif row['_merge'] == 'right_only':
                comments.append("New attribute added")
        else:
            if row['_merge'] == 'left_only':
                comments.append("New attribute added")
        # For records present in both, compare column values
        if row['_merge'] == 'both':
            for col in ref_df.columns:
                if col == 'Attribute Registry ID':
                    continue
                col_ref = f"{col}_ref"
                col_curr = f"{col}_curr"
                if col_ref in merged_df.columns and col_curr in merged_df.columns:
                    val_ref = row[col_ref]
                    val_curr = row[col_curr]
                    if pd.isnull(val_ref) and pd.isnull(val_curr):
                        continue
                    if val_ref != val_curr:
                        comments.append(f"Difference in {col}: '{val_ref}' -> '{val_curr}'")
        tool_comments.append("; ".join(comments))
    merged_df['Tool Comments'] = tool_comments
    # If not full comparison, only keep records with changes (from EDG_Current)
    if not full_comparison:
        merged_df = merged_df[merged_df['Tool Comments'] != ""]
    return merged_df

def save_reports(merged_df, output_excel_path, output_txt_path, ref_file_name, curr_file_name, full_comparison=True):
    """
    Saves an Excel report and a grouped text report.
    In the text report, only records with changes are included and grouped by type:
    New, Modified, and Deleted Attributes.
    """
    try:
        # Excel report:
        # For full comparison, save all records; for current-only, save only changed records.
        excel_df = merged_df.copy() if full_comparison else merged_df.copy()
        excel_df.to_excel(output_excel_path, index=False)
        
        # Build the text report by grouping changes
        new_attrs = []
        modified_attrs = []
        deleted_attrs = []
        report_rows = merged_df[merged_df['Tool Comments'] != ""]
        for idx, row in report_rows.iterrows():
            comment = row['Tool Comments']
            if "New attribute added" in comment:
                new_attrs.append(row)
            elif "Attribute deleted" in comment:
                deleted_attrs.append(row)
            elif "Difference in" in comment:
                modified_attrs.append(row)
        
        report_text = []
        header = f"EDG Comparison Report\nInput Files: {ref_file_name} | {curr_file_name}\n{'='*40}\n"
        report_text.append(header)
        
        if new_attrs:
            report_text.append("New Attributes:")
            for row in new_attrs:
                report_text.append(f"  Attribute Registry ID: {row['Attribute Registry ID']}")
                report_text.append(f"    Comments: {row['Tool Comments']}")
            report_text.append("")
        if modified_attrs:
            report_text.append("Modified Attributes:")
            for row in modified_attrs:
                report_text.append(f"  Attribute Registry ID: {row['Attribute Registry ID']}")
                report_text.append(f"    Comments: {row['Tool Comments']}")
            report_text.append("")
        if full_comparison and deleted_attrs:
            report_text.append("Deleted Attributes:")
            for row in deleted_attrs:
                report_text.append(f"  Attribute Registry ID: {row['Attribute Registry ID']}")
                report_text.append(f"    Comments: {row['Tool Comments']}")
            report_text.append("")
        
        with open(output_txt_path, 'w') as f:
            f.write("\n".join(report_text))
    except Exception as e:
        raise ValueError("Error saving reports: " + str(e))

# --------------------------
# Tkinter GUI
# --------------------------
class EDGComparisonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EDG Comparison Tool")
        self.geometry("700x400")
        
        self.ref_file = None
        self.curr_file = None
        
        # File selection widgets
        tk.Label(self, text="EDG Reference File:").pack(pady=5)
        self.ref_entry = tk.Entry(self, width=70)
        self.ref_entry.pack(pady=5)
        tk.Button(self, text="Browse", command=self.browse_ref_file).pack(pady=5)
        
        tk.Label(self, text="EDG Current File:").pack(pady=5)
        self.curr_entry = tk.Entry(self, width=70)
        self.curr_entry.pack(pady=5)
        tk.Button(self, text="Browse", command=self.browse_curr_file).pack(pady=5)
        
        # Full comparison option
        self.full_compare_var = tk.BooleanVar()
        tk.Checkbutton(self, text="Full EDG Comparison", variable=self.full_compare_var).pack(pady=5)
        
        # Status label and detailed status text area
        self.status_label = tk.Label(self, text="Status: Waiting for input")
        self.status_label.pack(pady=5)
        self.status_text = st.ScrolledText(self, height=10, width=80)
        self.status_text.pack(pady=5)
        
        tk.Button(self, text="Run Comparison", command=self.run_comparison).pack(pady=10)
    
    def log_status(self, message):
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.update_idletasks()
    
    def browse_ref_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=package_input_path,
            title="Select EDG Reference File",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if file_path:
            self.ref_file = file_path
            self.ref_entry.delete(0, tk.END)
            self.ref_entry.insert(0, file_path)
    
    def browse_curr_file(self):
        file_path = filedialog.askopenfilename(
            initialdir=package_input_path,
            title="Select EDG Current File",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if file_path:
            self.curr_file = file_path
            self.curr_entry.delete(0, tk.END)
            self.curr_entry.insert(0, file_path)
    
    def run_comparison(self):
        if not self.ref_file or not self.curr_file:
            messagebox.showerror("Input Error", "Please select both EDG Reference and Current files.")
            return
        try:
            self.status_label.config(text="Status: Starting processing...")
            self.log_status("Starting EDG comparison process.")
            
            ref_file_name = os.path.basename(self.ref_file)
            curr_file_name = os.path.basename(self.curr_file)
            
            self.log_status("Reading EDG Reference file...")
            ref_df = read_edg_file(self.ref_file)
            self.log_status(f"EDG Reference file read successfully. Records: {len(ref_df)}")
            
            self.log_status("Reading EDG Current file...")
            curr_df = read_edg_file(self.curr_file)
            self.log_status(f"EDG Current file read successfully. Records: {len(curr_df)}")
            
            self.log_status("Comparing files...")
            merged_df = compare_edg_data(ref_df, curr_df, full_comparison=self.full_compare_var.get())
            self.log_status(f"Comparison complete. Records in result: {len(merged_df)}")
            
            output_excel = os.path.join(package_output_path, "EDG_Difference.xlsx")
            output_txt = os.path.join(package_output_path, "EDG_Difference.txt")
            
            self.log_status("Saving reports...")
            save_reports(merged_df, output_excel, output_txt, ref_file_name, curr_file_name,
                         full_comparison=self.full_compare_var.get())
            self.log_status("Reports saved successfully.")
            self.status_label.config(text=f"Status: Completed. Output saved to {output_excel}")
            messagebox.showinfo("Success", "Comparison completed successfully!")
        except Exception as e:
            self.status_label.config(text="Status: Error encountered.")
            self.log_status("Error: " + str(e))
            messagebox.showerror("Error", str(e))

# --------------------------
# Main execution
# --------------------------
if __name__ == '__main__':
    app = EDGComparisonApp()
    app.mainloop()
