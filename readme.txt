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
        "Definition": df.get("Column Definition", ""),
        "Table Logical Name": df.get("Table Logical Name", ""),
        "Sub Model Name": df.get("Sub Model Name", ""),
        "Glossary Attribute ID provided in model": df.get("Glossary Attribute ID", ""),
        "Primary Key Indicator": df.get("Primary Key Indicator", ""),
        "Data Dic Data Type": df.get("Data Type", "").map(normalize_dtype),
        "Maximum Text Length": df.get("Length", ""),
        "Data Dic Scale": df.get("Scale", ""),
        "Null-able Indicator": df.get("Null", ""),
        "Logical Column Name": df.get("Column Logical Name", ""),
        "Column Sequence Number": df.get("Column Sequence Number", ""),
        "Name": col_col,
    })
    col_df["[Column] is part of [Table] > Full Name"] = (
        col_df["CMDB Asset ID"].astype(str) + "." + col_df["Container Type"].astype(str) + "." + table_col.astype(str)
    )
    col_df["Community"] = col_df["CMDB Asset ID"]
    col_df["Domain"] = col_df["CMDB Asset ID"].astype(str) + "." + col_df["Container Type"].astype(str)
    col_df["Full Name"] = col_df["[Column] is part of [Table] > Full Name"] + "." + col_df["Name"].astype(str)

    # -------- Save --------
    base = Path(file).stem
    table_out = f"{output_path}{base}_table.xlsx"
    col_out = f"{output_path}{base}_column.xlsx"

    table_df.to_excel(table_out, index=False)
    col_df.to_excel(col_out, index=False)

    print(f"  → Table file:   {Path(table_out).name} ({len(table_df)} rows)")
    print(f"  → Column file:  {Path(col_out).name} ({len(col_df)} rows)")
    print("Done.")

def main():
    excel_files = list(Path(input_path).glob("*.xls*"))
    if not excel_files:
        print("No Excel files found in ./input/")
        return
    print(f"Found {len(excel_files)} file(s) to process.")
    for file in excel_files:
        process_file(file)

if __name__ == "__main__":
    main()
