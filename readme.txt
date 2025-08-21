import pandas as pd
from pathlib import Path
from datetime import datetime

# Folders
input_path = "./_pddReuploadScript/input/"
output_path = "./_pddReuploadScript/output/"
Path(output_path).mkdir(parents=True, exist_ok=True)

# Timestamped run folder + subfolders
run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
run_root = f"{output_path}{run_stamp}/"
tables_dir = f"{run_root}tables/"
columns_dir = f"{run_root}columns/"
rels_dir = f"{run_root}relationships/"
concat_dir = f"{run_root}Concatenated Uploads/"

for d in [tables_dir, columns_dir, rels_dir, concat_dir]:
    Path(d).mkdir(parents=True, exist_ok=True)

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

    # -------- Table template --------
    table_df = pd.DataFrame({
        "Asset Type": "Table",
        "Domain Type": "Physical Data Dictionary",
        "Physical Model Name": "Physical",
        "Model File Name": df["Diagram Name"],
        "Load File Name": df["Excel File Name"],
        "CMDB Asset ID": df["CMDB Asset ID"],
        "CMDB Asset Name": df["CMDB Asset Name"],
        "Container Type": df["Container Type"],
        "Name": df["Container (Table) Name"],
        "Table Logical Name": df["Table Logical Name"],
        "Sub Model Name": df["Sub Model Name"],
        "Definition": df["Table/View Definition"],
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
        "Model File Name": df["Diagram Name"],
        "Load File Name": df["Excel File Name"],
        "CMDB Asset ID": df["CMDB Asset ID"],
        "CMDB Asset Name": df["CMDB Asset Name"],
        "Container Type": df["Container Type"],
        "Definition": df["Column Definition"],
        "Table Logical Name": df["Table Logical Name"],
        "Sub Model Name": df["Sub Model Name"],
        "Glossary Attribute ID provided in model": df["Glossary Attribute ID"],
        "Primary Key Indicator": df["Primary Key Indicator"],
        "Data Dic Data Type": df["Data Type"].map(normalize_dtype),
        "Maximum Text Length": df["Length"],
        "Data Dic Scale": df["Scale"],
        "Null-able Indicator": df["Null"],
        "Logical Column Name": df["Column Logical Name"],
        "Column Sequence Number": df["Column Sequence Number"],
        "Name": df["Data Element Name"],
    })
    part_of_full_name = (
        col_df["CMDB Asset ID"].astype(str)
        + "."
        + col_df["Container Type"].astype(str)
        + "."
        + df["Container (Table) Name"].astype(str)
    )
    col_df["Community"] = col_df["CMDB Asset ID"]
    col_df["Domain"] = col_df["CMDB Asset ID"].astype(str) + "." + col_df["Container Type"].astype(str)
    col_df["Full Name"] = part_of_full_name + "." + col_df["Name"].astype(str)

    # -------- Relationship file --------
    rel_df = pd.DataFrame({
        "Full Name": col_df["Full Name"],
        "[Column] is part of [Table] > Full Name": part_of_full_name
    })

    # -------- Save individual --------
    base = Path(file).stem
    table_out = f"{tables_dir}{base}_table.xlsx"
    col_out = f"{columns_dir}{base}_column.xlsx"
    rel_out = f"{rels_dir}{base}_relationships.xlsx"

    table_df.to_excel(table_out, index=False)
    col_df.to_excel(col_out, index=False)
    rel_df.to_excel(rel_out, index=False)

    print(f"  → Table file:        {Path(table_out).name} ({len(table_df)} rows)")
    print(f"  → Column file:       {Path(col_out).name} ({len(col_df)} rows)")
    print(f"  → Relationship file: {Path(rel_out).name} ({len(rel_df)} rows)")
    print("Done.")

    return table_df, col_df, rel_df

def main():
    excel_files = list(Path(input_path).glob("*.xls*"))
    if not excel_files:
        print("No Excel files found in ./input/")
        return
    print(f"Found {len(excel_files)} file(s) to process.")
    print(f"Run folder: {run_root}")

    all_tables, all_columns, all_rels = [], [], []

    for file in excel_files:
        tdf, cdf, rdf = process_file(file)
        all_tables.append(tdf)
        all_columns.append(cdf)
        all_rels.append(rdf)

    # -------- Concatenated Uploads --------
    if all_tables:
        pd.concat(all_tables, ignore_index=True).to_excel(f"{concat_dir}tables.xlsx", index=False)
        pd.concat(all_columns, ignore_index=True).to_excel(f"{concat_dir}columns.xlsx", index=False)
        pd.concat(all_rels, ignore_index=True).to_excel(f"{concat_dir}relationships.xlsx", index=False)

        print("\nConcatenated Uploads written:")
        print(f"  → tables.xlsx        ({sum(len(t) for t in all_tables)} rows)")
        print(f"  → columns.xlsx       ({sum(len(c) for c in all_columns)} rows)")
        print(f"  → relationships.xlsx ({sum(len(r) for r in all_rels)} rows)")

if __name__ == "__main__":
    main()
