import pandas as pd
from rapidfuzz import fuzz
from itertools import combinations
import os

def group_similar_definitions(definitions, threshold=60, status_callback=None):
    """
    Group similar definitions using fuzzy matching.

    :param definitions: List of definition strings.
    :param threshold: Similarity threshold (0-100) for grouping definitions.
    :param status_callback: Optional callback function to update status.
    :return: List of grouped definition strings.
    """
    groups = {}
    n = len(definitions)
    if status_callback:
        status_callback(f"Processing {n} definitions for grouping...")

    # Compare every pair of definitions
    for d1, d2 in combinations(definitions, 2):
        score = fuzz.token_sort_ratio(d1, d2)
        if score >= threshold:
            if d1 in groups:
                groups[d2] = groups[d1]
            elif d2 in groups:
                groups[d1] = groups[d2]
            else:
                groups[d1] = d1
                groups[d2] = d1

    # Preserve original order by mapping each definition to its group representative
    grouped_list = [groups.get(d, d) for d in definitions]
    return grouped_list

def process_privacy_file(input_path, output_path, threshold=60, status_callback=None):
    """
    Process the EDG Data Dictionary to identify discrepancies in privacy designations.

    :param input_path: Path to the input Excel file.
    :param output_path: Path for saving the output Excel file.
    :param threshold: Similarity threshold for fuzzy matching (0-100).
    :param status_callback: Callback function to report status messages.
    """
    try:
        if status_callback:
            status_callback("Loading Excel file...")
        # Load the Excel file
        df = pd.read_excel(input_path)
        
        # Select relevant columns and drop duplicates
        if status_callback:
            status_callback("Selecting columns and removing duplicate records...")
        key = df[['Attribute Registry ID', 'Name', 'Definition', 'Privacy Designation', 'CreatedOn']].drop_duplicates()
        
        # Group similar definitions using fuzzy matching
        if status_callback:
            status_callback("Grouping similar definitions...")
        definitions = key['Definition'].tolist()
        grouped_definitions = group_similar_definitions(definitions, threshold=threshold, status_callback=status_callback)
        key['grouped_str'] = grouped_definitions
        key['grouped_str'] = key['grouped_str'].str.lower().str.strip()
        
        # Count occurrences of each privacy designation per grouped string
        if status_callback:
            status_callback("Tabulating privacy designations per grouped definition...")
        key_summary = key.groupby(['grouped_str', 'Privacy Designation']).size().unstack(fill_value=0)
        
        # Identify discrepancies where attributes have conflicting privacy designations
        if status_callback:
            status_callback("Identifying potential discrepancies...")
        key_summary['potential_discrepancy'] = (
            ((key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI', 0) > 0)) |
            ((key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI In Combination - Personally Identifiable', 0) > 0)) |
            ((key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI In Combination - Not Publicly Available', 0) > 0))
        )
        
        # Filter rows with discrepancies
        potential_observation = key_summary[key_summary['potential_discrepancy']]
        
        # Merge discrepancy summary with the original attribute details
        if status_callback:
            status_callback("Merging discrepancy details with attribute data...")
        potential_observation_ids = potential_observation.merge(key, on='grouped_str', how='left')
        
        # Reorder columns for better readability
        columns = ['Attribute Registry ID', 'Name', 'Definition', 'Privacy Designation', 'CreatedOn', 'grouped_str',
                   'Not NPI', 'NPI In Combination - Personally Identifiable', 'NPI In Combination - Not Publicly Available', 'NPI', 'potential_discrepancy']
        potential_observation_ids = potential_observation_ids.reindex(columns=columns, fill_value=0)
        
        # Save the results to an Excel file
        if status_callback:
            status_callback("Saving results to Excel...")
        potential_observation_ids.to_excel(output_path, index=False)
        if status_callback:
            status_callback(f"Process completed successfully. Output saved to: {output_path}")
    except Exception as e:
        if status_callback:
            status_callback(f"Error occurred: {str(e)}")
        else:
            print(f"Error occurred: {str(e)}")


import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from privacy_audit import process_privacy_file

class PrivacyAuditApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NPI Privacy Designation Audit")
        self.geometry("600x500")
        # Input and output file paths
        self.input_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.threshold_value = tk.IntVar(value=60)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Input file selection
        input_frame = tk.Frame(self)
        input_frame.pack(pady=5, fill='x')
        tk.Label(input_frame, text="Select EDG Data Dictionary Excel File:").pack(side="left", padx=5)
        tk.Entry(input_frame, textvariable=self.input_file_path, width=40).pack(side="left", padx=5)
        tk.Button(input_frame, text="Browse", command=self.browse_input).pack(side="left", padx=5)
        
        # Output file selection
        output_frame = tk.Frame(self)
        output_frame.pack(pady=5, fill='x')
        tk.Label(output_frame, text="Output Excel File:").pack(side="left", padx=5)
        tk.Entry(output_frame, textvariable=self.output_file_path, width=40).pack(side="left", padx=5)
        tk.Button(output_frame, text="Save As", command=self.browse_output).pack(side="left", padx=5)
        
        # Fuzzy matching threshold setting
        threshold_frame = tk.Frame(self)
        threshold_frame.pack(pady=5, fill='x')
        tk.Label(threshold_frame, text="Fuzzy Matching Threshold (0-100):").pack(side="left", padx=5)
        self.threshold_spinbox = tk.Spinbox(threshold_frame, from_=0, to=100, textvariable=self.threshold_value, width=5)
        self.threshold_spinbox.pack(side="left", padx=5)
        
        # Run and Exit buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5, fill='x')
        tk.Button(button_frame, text="Run", command=self.run_process).pack(side="left", padx=10)
        tk.Button(button_frame, text="Exit", command=self.quit).pack(side="left", padx=10)
        
        # Status display area
        status_frame = tk.Frame(self)
        status_frame.pack(pady=10, fill='both', expand=True)
        tk.Label(status_frame, text="Status:").pack(anchor="w", padx=5)
        self.status_text = tk.Text(status_frame, wrap="word", state="disabled")
        self.status_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def browse_input(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        if file_path:
            self.input_file_path.set(file_path)
    
    def browse_output(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])
        if file_path:
            self.output_file_path.set(file_path)
    
    def append_status(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert("end", message + "\n")
        self.status_text.see("end")
        self.status_text.config(state="disabled")
    
    def run_process(self):
        input_file = self.input_file_path.get()
        output_file = self.output_file_path.get()
        threshold = self.threshold_value.get()
        
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Error", "Please select a valid input Excel file.")
            return
        
        if not output_file:
            messagebox.showerror("Error", "Please select a valid output file path.")
            return
        
        # Clear previous status messages
        self.status_text.config(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.config(state="disabled")
        
        self.append_status("Starting processing...")
        # Run the process in a separate thread to keep the UI responsive
        threading.Thread(target=self.process_file_thread, args=(input_file, output_file, threshold)).start()
    
    def process_file_thread(self, input_file, output_file, threshold):
        def status_callback(message):
            # Schedule status updates on the main thread
            self.status_text.after(0, self.append_status, message)
        
        process_privacy_file(input_file, output_file, threshold=threshold, status_callback=status_callback)
    
if __name__ == "__main__":
    app = PrivacyAuditApp()
    app.mainloop()


HOW TO: Running the NPI Privacy Designation Audit Script with Tkinter UI

Prerequisites:
- Python 3.7+ installed.
- Required Python libraries: pandas, rapidfuzz, openpyxl.
  (Tkinter is included with Python. Install additional libraries via: pip install pandas rapidfuzz openpyxl)
- Ensure your input Excel file (EDG Data Dictionary) is available and correctly formatted with the following columns:
  "Attribute Registry ID", "Name", "Definition", "Privacy Designation", "CreatedOn".

Steps:
1. Place both "privacy_audit.py" and "privacy_ui.py" in the same directory.
2. Open a terminal or command prompt in that directory.
3. Run the UI script by executing:
     python privacy_ui.py
4. In the UI window:
   - Click "Browse" to select the input Excel file.
   - Click "Save As" to specify the output Excel file path.
   - Adjust the fuzzy matching threshold using the spinbox (default is 60).
5. Click the "Run" button to start processing.
6. Monitor the status updates in the status box.
7. Once complete, review the output Excel file generated at the specified path.

Troubleshooting:
- If the script cannot load the Excel file, verify that the file path is correct and the file is properly formatted.
- Check the status messages in the UI for any errors.
- Ensure all required libraries are installed.
- For additional issues, review the terminal output for debugging information.


# NPI Privacy Designation Audit Script FAQ

## Overview
The NPI Privacy Designation Audit Script automates the auditing of an Enterprise Data Glossary by grouping similar definitions using fuzzy matching and identifying discrepancies in privacy designations. A new graphical user interface (GUI) built with Tkinter allows users to easily select input files, adjust matching parameters, and view status updates in real time.

## Table of Contents
- Overview
- Key Features
- Detailed Process
- Frequently Asked Questions (FAQ)
- Troubleshooting
- Additional Resources

## Key Features
- **User-Friendly Interface:**
  - Select the input Excel file (EDG Data Dictionary) using a file browser.
  - Specify the output Excel file path.
  - Adjust the fuzzy matching threshold using a spinbox.
  - View real-time status updates during processing.
- **Robust Processing:**
  - Data extraction, cleaning, and deduplication.
  - Efficient fuzzy grouping using RapidFuzz.
  - Automated identification of conflicting privacy designations.
- **Clear Output:**
  - Final results are exported to an Excel file with flagged discrepancies for further review.

## Detailed Process
1. **Data Loading:**
   - The tool loads the input Excel file and selects key columns: "Attribute Registry ID", "Name", "Definition", "Privacy Designation", and "CreatedOn".
   - Duplicate records are removed to ensure a clean dataset.
2. **Fuzzy Grouping:**
   - Definitions are compared pairwise using RapidFuzz's token sort ratio.
   - Definitions exceeding the user-defined threshold are grouped together, reducing noise from minor textual differences.
3. **Discrepancy Identification:**
   - The grouped data is pivoted to count occurrences of each privacy designation.
   - Discrepancies are flagged when conflicting designations (e.g., "Not NPI" vs. "NPI") occur for the same grouped definition.
4. **Output Generation:**
   - The discrepancy summary is merged with the original data.
   - The final report is saved as an Excel file at the user-specified location.

## Frequently Asked Questions (FAQ)
**Q1: What is the purpose of this script?**  
A: It automates the auditing process for enterprise data dictionaries by identifying conflicting privacy designations using fuzzy matching.

**Q2: How do I run the tool?**  
A: Run the `privacy_ui.py` file. The Tkinter-based GUI will guide you to select your input file, choose an output path, set the matching threshold, and monitor the process.

**Q3: How can I adjust the fuzzy matching sensitivity?**  
A: Use the spinbox in the UI to set a threshold value between 0 and 100. A higher threshold applies stricter matching criteria.

**Q4: What should I do if an error occurs during processing?**  
A: Check the status box in the UI for detailed error messages. Verify that the input file exists, is in the correct format, and that all required libraries are installed.

**Q5: What are the required libraries for this tool?**  
A: The script requires pandas, rapidfuzz, tkinter (included with Python), and openpyxl.

## Troubleshooting
- **Input File Issues:** Ensure that your input Excel file contains the required columns and is not corrupted.
- **Library Installation:** If you encounter module import errors, reinstall the required libraries using pip.
- **UI Issues:** If the GUI does not launch, run the script from a terminal to view error messages.
- **Performance Concerns:** For very large datasets, consider adjusting the threshold or optimizing system resources.

## Additional Resources
- [Python Documentation](https://docs.python.org/)
- [RapidFuzz Documentation](https://maxbachmann.github.io/RapidFuzz/)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- Contact your system administrator for further support.
