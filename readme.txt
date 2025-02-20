from ui import start_ui  # Import UI startup function

if __name__ == "__main__":
    start_ui()  # Runs the program



#ui.py

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from processor import process_file  # Import processing function

# ---------------------- FUNCTION TO HANDLE FILE SELECTION ----------------------
def select_file():
    global file_path
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel Files", "*.xlsx;*.xls")]
    )
    if file_path:
        file_label.config(text=f"📂 Selected: {os.path.basename(file_path)}")

# ---------------------- FUNCTION TO RUN PROCESSING ----------------------
def run_processing():
    global file_path  
    if not file_path:
        messagebox.showerror("Error", "No file selected. Please select an Excel file first.")
        return

    threshold = threshold_slider.get()  # Get threshold from slider
    result = process_file(file_path, threshold)  # Call processing function

    if "Error" in result:
        messagebox.showerror("Processing Failed", result)
    else:
        messagebox.showinfo("Success", f"✅ Processing complete!\nResults saved at: {result}")

# ---------------------- FUNCTION TO UPDATE SLIDER LABEL ----------------------
def update_threshold_label(value):
    threshold_label.config(text=f"Threshold: {float(value):.2f}")  # Update label with slider value

# ---------------------- CREATE UI ----------------------
root = tk.Tk()
root.title("Privacy Data Processor")
root.geometry("400x300")

# Heading
tk.Label(root, text="Privacy Data Processor", font=("Arial", 14, "bold")).pack(pady=10)

# Select File Button
file_path = ""
select_button = tk.Button(root, text="Select Input File", command=select_file, font=("Arial", 12))
select_button.pack(pady=5)

# File label
file_label = tk.Label(root, text="No file selected", font=("Arial", 10), fg="red")
file_label.pack()

# Threshold selection
threshold_label = tk.Label(root, text="Threshold: 0.60", font=("Arial", 10))
threshold_label.pack()

threshold_slider = tk.Scale(root, from_=0.1, to=1.0, resolution=0.05, orient="horizontal", length=300, command=update_threshold_label)
threshold_slider.set(0.6)  # Default value
threshold_slider.pack()

# Start Button
start_button = tk.Button(root, text="Start Processing", command=run_processing, font=("Arial", 12), bg="green", fg="white")
start_button.pack(pady=20)

# Run the UI
root.mainloop()

#processor.py
import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------- FUNCTION TO PROCESS FILE ----------------------
def process_file(file_path, threshold):
    """Processes the Excel file and applies fuzzy matching based on the given threshold."""
    try:
        df = pd.read_excel(file_path)

        # Keep only relevant columns and ensure unique values
        key = df[['Attribute Registry ID', 'Name', 'Definition', 'Privacy Designation', 'CreatedOn']].drop_duplicates()

        # ------------------- JACCARD SIMILARITY FUNCTION -------------------
        def jaccard_similarity(str1, str2):
            set1, set2 = set(str1.lower().split()), set(str2.lower().split())
            return len(set1 & set2) / len(set1 | set2) if (set1 | set2) else 0

        # Group similar definitions based on threshold
        grouped_dict = {}
        group_counter = 0

        for idx, row in key.iterrows():
            definition = row['Definition']
            matched_group = None

            for group, definitions in grouped_dict.items():
                if any(jaccard_similarity(definition, existing_def) >= threshold for existing_def in definitions):
                    matched_group = group
                    break

            if matched_group:
                grouped_dict[matched_group].append(definition)
            else:
                grouped_dict[f"group_{group_counter}"] = [definition]
                group_counter += 1

        # Map definitions to grouped strings
        definition_to_group = {definition: group for group, definitions in grouped_dict.items() for definition in definitions}
        key['grouped_str'] = key['Definition'].map(definition_to_group)

        # Standardize grouped string values
        key['grouped_str'] = key['grouped_str'].str.lower().str.strip()

        # ------------------- CREATE SUMMARY TABLE -------------------
        key_summary = key.groupby(['grouped_str', 'Privacy Designation']).size().unstack(fill_value=0)
        key_summary.reset_index(inplace=True)

        # Identify discrepancies
        key_summary['potential_discrepancy'] = (
            (key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI', 0) > 0) |
            (key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI In Combination - Personally Identifiable', 0) > 0) |
            (key_summary.get('Not NPI', 0) > 0) & (key_summary.get('NPI In Combination - Not Publicly Available', 0) > 0)
        )

        # Filter discrepancies
        potential_observation = key_summary[key_summary['potential_discrepancy']]
        potential_observation_ids = pd.merge(potential_observation, key, on="grouped_str", how="left")

        # Save results
        output_file = os.path.join(os.path.dirname(file_path), "NPI_example.xlsx")
        potential_observation_ids.to_excel(output_file, index=False)

        return output_file  # Return the saved file path

    except Exception as e:
        return f"Error: {str(e)}"
