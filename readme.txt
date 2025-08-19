import os
import pandas as pd
from pathlib import Path

# Folders
input_path = "./input/"
output_path = "./output/"
Path(output_path).mkdir(parents=True, exist_ok=True)

def normalize_dtype(val):
    if pd.isna(val): 
        return val
    s = str(val).strip().upper()
    if s == "DOUBLE PRECISION": return "DOUBLE"
    if s == "FLOATA": return "FLOAT"
    if s == "TIMESTAMPTZ": return "TIMESTAMP"
    return s

def trim_all_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace from all string cells."""
    return df.map(lambda x: x.strip() if isinstance(x, str) else x)

def process_file(file):
    print(f"\n--- Processing: {Path(file).name} ---")
    df = pd.read_excel(file)
    df = trim_all_columns(df)

    # Fallbacks for table/column names
    table_col = df["Container (Table) Name"] if "Container (Table) Name" in df else df.get("Table", "")
    col_col   = df["Data Element Name"] if "Data Element Name" in df else df.get("Column", "")

    # -------- Table template --------
    table_df = pd.DataFrame({
        "Asset Type": "Table",
        "Domain Type": "Physical Data Dictionary",
        "Physical Model Name": "Physical",
        "Model File Name": df.get("Diagram Name", ""),
        "Load File Name": Path(file).name,
        "CMDB Asset ID": df.get("CMDB Asset ID", ""),
        "CMDB Asset Name": df.get("CMDB Asset Name", ""),
        "Container Type": df.get("Container Type", ""),
        "Name": table_col,
        "Table Logical Name": df.get("Table Logical Name", ""),
        "Sub Model Name": df.get("Sub Model Name", ""),
        "Definition": df.get("Table/View Definition", ""),
    })
    table_df["Community"] = table_df["CMDB Asset ID"]
    table_df["Domain"] = table_df["CMDB Asset ID"].astype(str) + "." + table_df["Container Type"].astype(str)
    table_df["Full Name"] = table_df["Domain"] + "." + table_df["Name"].astype(str)
    table_df = table_df.drop_duplicates(subset=["Full Name"]).reset_index(drop=True)

    # -------- Column template --------
    col_df = pd.DataFrame({
        "Asset Type": "Column",
        "Domain Type": "Physical Data Dictionary",
        "Physical Model Name": "Physical",
        "CMDB Asset ID": df.get("CMDB Asset ID", ""),
        "CMDB Asset Name": df.get("CMDB Asset Name", ""),
        "Container Type": df.get("Container Type", ""),
