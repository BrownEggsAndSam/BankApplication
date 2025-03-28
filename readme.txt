import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import tkinter.scrolledtext as st
from datetime import datetime

# --------------------------
# Updated Backend File Paths
# --------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
package_backend_path = os.path.join(BASE_DIR, 'backend', 'backend.xlsx')
package_input_path = os.path.join(BASE_DIR, 'input')
package_output_path = os.path.join(BASE_DIR, 'output')

def get_output_filenames():
    """
    Returns dynamic output filenames based on current timestamp.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_excel = os.path.join(package_output_path, f"EDG_Difference_{timestamp}.xlsx")
    output_txt = os.path.join(package_output_path, f"EDG_Difference_{timestamp}.txt")
    return output_excel, output_txt

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

def compare_edg_data(ref_df, curr_df):
    """
    Compare EDG_Current (curr_df) to EDG_Reference (ref_df) using 'Attribute Registry ID' as the key.
    
    Performs a left merge so that only records present in the current file are considered.
    For each record:
      - If no matching record is found in the reference, mark as a new attribute.
      - If a match exists, compare each field (except 'Attribute Registry ID').
    A dictionary 'diff_details' is created for each row:
      - If the record is new, diff_details['new'] is set to True.
      - For common records, keys for each field with differences are added as a tuple (old, new).
    """
    merged_df = pd.merge(curr_df, ref_df, on='Attribute Registry ID', how='left', 
                           suffixes=('_curr', '_ref'), indicator=True)
    diff_details_list = []
    for idx, row in merged_df.iterrows():
        diff_details = {}
        if row['_merge'] == 'left_only':
            diff_details['new'] = True
        else:
            for col in curr_df.columns:
                if col == 'Attribute Registry ID':
                    continue
                col_curr = f"{col}_curr"
                col_ref = f"{col}_ref"
                if col_curr in merged_df.columns and col_ref in merged_df.columns:
                    val_curr = row[col_curr]
                    val_ref = row[col_ref]
                    # Skip if both are missing or equal
                    if pd.isnull(val_ref) and pd.isnull(val_curr):
                        continue
                    if val_ref != val_curr:
                        diff_details[col] = (val_ref, val_curr)
        diff_details_list.append(diff_details)
    merged_df['diff_details'] = diff_details_list
    # Build a simple Tool Comments string for the Excel report
    tool_comments = []
    for details in diff_details_list:
        comments = []
        if details.get('new'):
            comments.append("New attribute added")
        for key, diff in details.items():
            if key == 'new':
                continue
            comments.append(f"Difference in {key}: '{diff[0]}' -> '{diff[1]}'")
        tool_comments.append("; ".join(comments))
    merged_df['Tool Comments'] = tool_comments
    # Only keep rows with differences
    merged_df = merged_df[merged_df['Tool Comments'] != ""]
    return merged_df

def save_reports(merged_df, ref_file_name, curr_file_name):
    """
    Saves an Excel report and a grouped text report.
    
    The text report is organized into sections:
      - New Attributes:
          Lists each new attribute with "Attribute Registry ID - Attribute Name".
      - For each field with differences, a section is created with header:
          "Difference IN <Field>"
        Under each header, each line is:
          "Attr Registry ID - Changed from 'old' to 'new'"
    """
    try:
        output_excel, output_txt = get_output_filenames()
        # Save the Excel report (all records are saved)
        merged_df.to_excel(output_excel, index=False)
        
        # Prepare groups for the text report
        new_attributes = []
        differences_by_field = {}  # key: field name, value: list of difference lines
        
        for idx, row in merged_df.iterrows():
            diff = row['diff_details']
            attr_id = row['Attribute Registry ID']
            # Determine attribute name: prefer "Attribute Name" over "Name"
            attr_name = row.get('Attribute Name', row.get('Name', ''))
            if diff.get('new'):
                new_attributes.append(f"{attr_id} - {attr_name}")
            for key in diff:
                if key == 'new':
                    continue
                # Create a line for this field
                old_val, new_val = diff[key]
                line = f"{attr_id} - Changed from '{old_val}' to '{new_val}'"
                if key not in differences_by_field:
                    differences_by_field[key] = []
                differences_by_field[key].append(line)
        
        report_lines = []
        header = f"EDG Comparison Report\nInput Files: {ref_file_name} | {curr_file_name}\n{'='*40}\n"
        report_lines.append(header)
        
        if new_attributes:
            report_lines.append("New Attributes:")
            for item in new_attributes:
                report_lines.append("  " + item)
            report_lines.append("")
        
        for field, lines in differences_by_field.items():
            report_lines.append(f"Difference IN {field}:")
            for line in lines:
                report_lines.append("  " + line)
            report_lines.append("")
        
        with open(output_txt, 'w') as f:
            f.write("\n".join(report_lines))
        return output_excel, output_txt
    except Exception as e:
        raise ValueError("Error saving reports: " + str(e))

# --------------------------
# Tkinter GUI
# --------------------------
class EDGComparisonApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EDG Comparison Tool")
        self.geometry("750x600")  # Updated window size
        
        self.ref_file = None
        self.curr_file = None
        
        # File selection widgets
        tk.Label(self, text="EDG Reference File:").pack(pady=5)
        self.ref_entry = tk.Entry(self, width=80)
        self.ref_entry.pack(pady=5)
        tk.Button(self, text="Browse", command=self.browse_ref_file).pack(pady=5)
        
        tk.Label(self, text="EDG Current File:").pack(pady=5)
        self.curr_entry = tk.Entry(self, width=80)
        self.curr_entry.pack(pady=5)
        tk.Button(self, text="Browse", command=self.browse_curr_file).pack(pady=5)
        
        # Status label and detailed status text area
        self.status_label = tk.Label(self, text="Status: Waiting for input")
        self.status_label.pack(pady=5)
        self.status_text = st.ScrolledText(self, height=10, width=90)
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
            merged_df = compare_edg_data(ref_df, curr_df)
            self.log_status(f"Comparison complete. Records with differences: {len(merged_df)}")
            
            self.log_status("Saving reports...")
            output_excel, output_txt = save_reports(merged_df, ref_file_name, curr_file_name)
            self.log_status(f"Reports saved successfully:\nExcel: {output_excel}\nText: {output_txt}")
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
