import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from data_cleaner_ui import DataCleanerUI
from data_cleaner import DataCleaner
from report_maker import ReportMaker

class StewardshipTool:
    def __init__(self, master):
        self.master = master
        self.master.title("The Stewardship Tool")

        self.header_names = ["Data Cleaning", "Report making"]
        self.button_names = [
            ["Strip Whitespace", "Convert to Lowercase", "Replace Empty Strings",
             "Remove Duplicates", "Remove Columns", "Fill Missing Values"],
            ["EDL Delta Hydration"]
        ]

        self.buttons = []

        for i, header_name in enumerate(self.header_names):
            header = ttk.Label(self.master, text=header_name, font=("Helvetica", 14, "bold"))
            header.grid(row=i*2, column=0, pady=10, sticky="w")

            button_frame = tk.Frame(self.master)
            button_frame.grid(row=i*2+1, column=0, sticky="w")

            button_row = []
            for j, button_name in enumerate(self.button_names[i]):
                btn = tk.Button(button_frame, text=button_name, command=lambda i=i, j=j: self.show_popup(i, j),
                                bg="#ADD8E6", relief="solid", bd=2, highlightthickness=0)
                btn.pack(side="left", padx=5, pady=5)
                btn.configure(highlightbackground=btn.cget("background"), highlightcolor=btn.cget("background"))

                button_row.append(btn)
            self.buttons.append(button_row)

    def show_popup(self, header_index, button_index):
        button_name = self.button_names[header_index][button_index]

        if header_index == 0:
            data_cleaner = DataCleaner()
            DataCleanerUI(self.master, data_cleaner, button_name,
                        "Instructions for this cleaning procedure...", self)
        elif button_name == "EDL Delta Hydration":
            self.select_input_file()

    def select_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")])
        if file_path:
            report_maker = ReportMaker(file_path)
            report_maker.edl_delta_hydration()

    def close_popup(self, popup):
        popup.destroy()
        self.set_buttons_state("normal")

    def set_buttons_state(self, state):
        for button_row in self.buttons:
            for button in button_row:
                button.configure(state=state)

if __name__ == "__main__":
    root = tk.Tk()
    app = StewardshipTool(root)
    root.mainloop()

import os
import pandas as pd
from datetime import datetime
from data_cleaner import DataCleaner


class ReportMaker:
    def __init__(self, input_file):
        self.input_file_name = os.path.basename(input_file).split('.')[0]
        self.input_data = pd.read_excel(input_file) if input_file.endswith(".xlsx") else pd.read_csv(input_file)
        self.output_folder = 'output'

    def edl_delta_hydration(self):
        print("Starting EDL Delta Hydration report...")

        # Create a copy of the input data
        reimport_data = self.input_data.copy()

        # Strip whitespace
        reimport_data = DataCleaner.strip_whitespace(reimport_data)

        # Initialize variables for the log file
        total_records = len(reimport_data)
        valid_records = 0
        invalid_records = 0
        exact_matches = 0
        duplicate_matches = 0
        blank_records = 0

        # Initialize dataframes for invalid and duplicate records
        invalid_df = pd.DataFrame(columns=reimport_data.columns)
        dupes_df = pd.DataFrame(columns=reimport_data.columns)

        # Implement the report logic
        for index, row in reimport_data.iterrows():
            attr_id = row['Attribute Registry ID']
            name = row['Name']

            if pd.isnull(attr_id):
                # Look up by name
                matches = DataCleaner.dset_pdd_occurences[DataCleaner.dset_pdd_occurences['Physical_Name'] == name]

                if len(matches) == 1:
                    exact_matches += 1
                    attr_id = matches['Attribute ID'].iloc[0]
                elif len(matches) > 1:
                    duplicate_matches += 1
                    dupes_df = dupes_df.append(row)
                    reimport_data.loc[index, 'Attribute Registry ID'] = 'Check duplicate records sheet'
                    continue

            if not pd.isnull(attr_id) and (str(attr_id).startswith('ATTR') and str(attr_id)[4:].isdigit() and len(str(attr_id)) == 9 or str(attr_id).isdigit() and len(str(attr_id)) == 5):
                # Check for a match in consolidated_EDG
                match = DataCleaner.consolidated_EDG[DataCleaner.consolidated_EDG['Full Name'] == attr_id]

                if len(match) == 1:
                    valid_records += 1
                    # Fill in the information for the columns from consolidated_EDG to the 'reimport' sheet
                    for col in ['Attribute Registry ID', 'represents Business Term [Business Term] > Name', 'represents Business Term [Business Term] > Full Name', 'represents Business Term [Business Term] > Asset Type', 'represents Business Term [Business Term] > Community', 'represents Business Term [Business Term] > Domain Type', 'represents Business Term [Business Term] > Domain']:
                        reimport_data.loc[index, col] = match[col].iloc[0]
                else:
                    invalid_records += 1
                    invalid_df = invalid_df.append(row)
            else:
                invalid_records += 1
                invalid_df = invalid_df.append(row)

        blank_records = len(reimport_data[pd.isnull(reimport_data['Attribute Registry ID'])])

        # Save the output file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name = f"{self.input_file_name}_{timestamp}.xlsx"
        output_file_path = os.path.join(self.output_folder, output_file_name)

        with pd.ExcelWriter(output_file_path) as writer:
            self.input_data.to_excel(writer, sheet_name="Original", index=False)
            reimport_data.to_excel(writer, sheet_name="Reimport", index=False)
            invalid_df.to_excel(writer, sheet_name="Invalid Records", index=False)
            dupes_df.to_excel(writer, sheet_name="Dupes", index=False)


        # def consolidated_edg_report(self):
        #     # Your implementation for the consolidated_edg_report method
        #     # ...

        #     # Update output_file_path for consolidated_edg_report folder
        #     consolidated_edg_folder = os.path.join(self.output_folder, 'consolidated_edg_report')
        #     os.makedirs(consolidated_edg_folder, exist_ok=True)
        #     output_file_path = os.path.join(consolidated_edg_folder, output_file_name)

        #     # Save the output file for this report
        #     # ...


# # Usage example
# report_maker = ReportMaker("path/to/your/input_data/input_file.csv")
# report_maker.edl_delta_hydration()
# report_maker.consolidated_edg_report()
import os
import pandas as pd
import numpy as np
from datetime import datetime

class DataCleaner:
    def __init__(self, input_file=None):
        self.input_file = input_file
        self.data = None
        self.log_file = "data_cleaning_log_{}.txt".format(datetime.now().strftime("%Y%m%d_%H%M%S"))

    def set_input_file(self, file_path):
        self.input_file = file_path
        self.data = pd.read_excel(file_path) if file_path.endswith(".xlsx") else pd.read_csv(file_path)

    def log(self, message):
        with open(self.log_file, "a") as f:
            f.write(message + "\n")

    @classmethod
    def strip_whitespace(cls, data):
        before = data.shape
        data = data.applymap(lambda x: x.strip() if isinstance(x, str) else x)
        after = data.shape
        print(f"Whitespace stripped from data. Before: {before}, After: {after}")
        return data

    def convert_to_lowercase(self):
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                self.data[col] = self.data[col].str.lower()
        self.log("Converted string columns to lowercase")

    def replace_empty_strings(self):
        before = self.data.isnull().sum().sum()
        self.data.replace("", np.nan, inplace=True)
        after = self.data.isnull().sum().sum()
        self.log(f"Replaced empty strings with NaN: Before={before}, After={after}")

    def remove_duplicates(self):
        before = self.data.shape
        self.data.drop_duplicates(inplace=True)
        after = self.data.shape
        self.log(f"Removed duplicates: Before={before}, After={after}")

    def remove_columns(self, columns_to_remove):
        before = self.data.shape
        self.data.drop(columns=columns_to_remove, inplace=True)
        after = self.data.shape
        self.log(f"Removed columns {columns_to_remove}: Before={before}, After={after}")

    def fill_missing_values(self, strategy="mean"):
        if strategy not in ["mean", "median", "mode"]:
            raise ValueError("Invalid strategy, choose from 'mean', 'median', or 'mode'")

        before = self.data.isnull().sum().sum()
        if strategy == "mean":
            self.data.fillna(self.data.mean(), inplace=True)
        elif strategy == "median":
            self.data.fillna(self.data.median(), inplace=True)
        else:
            self.data.fillna(self.data.mode().iloc[0], inplace=True)
        after = self.data.isnull().sum().sum()
        self.log(f"Filled missing values using {strategy}: Before={before}, After={after}")

    def consolidate_edg(self):
        files = ['EDG.xlsx', 'NewSF.xlsx', 'NC.xlsx', 'InA.xlsx']
        input_folder = os.path.join('input_data', 'Consolidated_EDG')

        data_frames = []

        for file in files:
            file_path = os.path.join(input_folder, file)
            df = pd.read_excel(file_path)
            data_frames.append(df)

        self.consolidated_EDG = pd.concat(data_frames, ignore_index=True)

    def dset_pdd_occurences(self):
        input_folder = os.path.join('input_data', 'DSET_PDD')

        # Read files
        dset_path = os.path.join(input_folder, 'DSET.xlsx')
        pdd_path = os.path.join(input_folder, 'PDD.xlsx')
        dset = pd.read_excel(dset_path)
        pdd = pd.read_excel(pdd_path)

        # Merge files
        merged = dset.merge(pdd, left_on='Name', right_on='Name', suffixes=('', '_pdd'))
        merged = merged[['Name', 'represented by [Business Term] > Full Name']]

        # Rename columns
        merged.columns = ['Physical_Name', 'Attribute_ID']

        # Calculate occurrence count
        merged['Occurrence_Count'] = merged.groupby(['Physical_Name', 'Attribute_ID'])['Physical_Name'].transform('count')

        # Drop duplicate rows
        self.DSET_PDD_Occurences = merged.drop_duplicates()

import tkinter as tk
from tkinter import ttk, filedialog

class DataCleanerUI(tk.Toplevel):
    def __init__(self, master, data_cleaner, title, instructions, stewardship_tool):
        super().__init__(master)
        self.title(title)
        self.data_cleaner = data_cleaner
        self.instructions = instructions
        self.stewardship_tool = stewardship_tool

        # Disable other buttons in StewardshipTool
        self.stewardship_tool.set_buttons_state(tk.DISABLED)

        # Bind the 'destroy' event to enable buttons when the window is closed
        self.bind('<Destroy>', self.enable_buttons)

        # Display instructions
        self.instructions_label = tk.Label(self, text=self.instructions, wraplength=300)
        self.instructions_label.pack(pady=10)

        # Button to select the input file
        self.select_file_button = tk.Button(self, text="Select Input File", command=self.select_input_file)
        self.select_file_button.pack(pady=5)

        # Label to display the selected file path
        self.file_path_var = tk.StringVar()
        self.file_path_label = tk.Label(self, textvariable=self.file_path_var, bg="white", relief="solid", bd=1,
                                        font=('Helvetica', 9, 'bold'))
        self.file_path_label.pack(pady=5)

        # Confirm button
        self.confirm_button = tk.Button(self, text="Confirm", command=self.confirm)
        self.confirm_button.pack(pady=10)

    def enable_buttons(self, event):
        self.stewardship_tool.set_buttons_state(tk.NORMAL)
        
    def select_input_file(self):
        filetypes = [("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
        file_path = filedialog.askopenfilename(title="Select Input File", filetypes=filetypes)
        if file_path:
            self.file_path_var.set(file_path)
            self.data_cleaner.set_input_file(file_path)

    def run_cleaning_procedure(self):
        # Call the corresponding cleaning procedure from the DataCleaner class with the user's input
        procedure_name = self.label_title.cget("text")

        if procedure_name == "Strip Whitespace":
            self.data_cleaner.strip_whitespace()
        elif procedure_name == "Convert to Lowercase":
            self.data_cleaner.convert_to_lowercase()
        elif procedure_name == "Replace Empty Strings":
            self.data_cleaner.replace_empty_strings()
        elif procedure_name == "Remove Duplicates":
            self.data_cleaner.remove_duplicates()
        elif procedure_name == "Remove Columns":
            columns_to_remove = self.user_input.get().split(',')
            self.data_cleaner.remove_columns(columns_to_remove)
        elif procedure_name == "Fill Missing Values":
            strategy = self.user_input.get()
            self.data_cleaner.fill_missing_values(strategy)

        # Close the popup after executing the procedure
        self.destroy()

