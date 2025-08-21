import pandas as pd
from pathlib import Path
from datetime import datetime

# -------- Paths --------
input_path = Path("./input")
# Output root folder with timestamp per run
run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_root = Path("./output") / run_stamp
tables_dir = output_root / "tables"
columns_dir = output_root / "columns"
rels_dir = output_root / "relationships"
for d in [tables_dir, columns_dir, rels_dir]:
    d.mkdir(parents=True, exist_ok=True)

# -------- Helpers --------
def normalize_dtype(val):
    if pd.isna(val):
        return val
    s = str(val).strip().upper()
    if s == "DOUBLE PRECISION": return "DOUBLE"
    if s == "FLOATA": return "FLOAT"
    if s == "TIMESTAMPTZ": return "TIMESTAMP"
    return s

def trim_all_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace from all string cells (no applymap deprecation)."""
    return df.map(lambda x: x.strip() if isinstance(x, str) else x)

def get_series(df: pd.DataFrame, name: str, fallback: str | None = None) -> pd.Series:
    """Safe column fetch; returns a Series of len(df) even if missing."""
    if name in df.columns:
        return df[name]
    if fallback and fallback in df.columns:
        return df[fallback]
    return pd.Series([""] * len(df), index=df.index, dtype=object)

def with_fallback(df: pd.DataFrame, primary: str, fallbacks: list[str]) -> pd.Series:
    """Try primary then each fallback; return blank Series if none found."""
    if primary in df.columns:
        return df[primary]
    for fb in fallbacks:
        if fb in df.columns:
            return df[fb]
    return pd.Series([""] * len(df), index=df.index, dtype=object)

# -------- Processing --------
def process_file(path: Path):
    print(f"\n--- Processing: {path.name} ---")
    df = pd.read_excel(path)
    df = trim_all_columns(df)

    # Common columns (with short-name fallbacks for Table/Column)
    table_name = with_fallback(df, "Container (Table) Name", ["Table", "TABLE_NAME", "Container"])
    data_element = with_fallback(df, "Data Element Name", ["Column", "COLUMN_NAME", "Data Element"])

    diagram_name = with_fallback(df, "Diagram Name", ["Model File Name", "Diagram"])
    cmdb_id = get_series(df, "CMDB Asset ID")
    cmdb_name = get_series(df, "CMDB Asset Name")
    container_type = get_series(df, "Container Type")
    table_logical = with_fallback(df, "Table Logical Name", ["Logical Table Name"])
    sub_model = get_series(df, "Sub Model Name")

    # ========= TABLE TEMPLATE =========
    table_df = pd.DataFrame({
        "Asset Type": "Table",
        "Domain Type": "Physical Data Dictionary",
        "Physical Model Name": "Physical",
        "Model File Name": diagram_name,
        "Load File Name": path.name,
        "CMDB Asset ID": cmdb_id,
        "CMDB Asset Name": cmdb_name,
        "Container Type": container_type,
        "Name": table_name,
        "Table Logical Name": table_logical,
        "Sub Model Name": sub_model,
        "Definition": with_fallback(df, "Table/View Definition", ["Table Definition", "Definition (Table)"]),
    })
    table_df["Community"] = table_df["CMDB Asset ID"]
    table_df["Domain"] = table_df["CMDB Asset ID"].astype(str) + "." + table_df["Container Type"].astype(str)
    table_df["Full Name"] = table_df["Domain"] + "." + table_df["Name"].astype(str)
    # 1 row per unique table
    table_df = table_df.drop_duplicates(subset=["Full Name"]).reset_index(drop=True)

    # ========= COLUMN TEMPLATE =========
    col_df = pd.DataFrame({
        "Asset Type": "Column",
        "Domain Type": "Physical Data Dictionary",
        "Physical Model Name": "Physical",
        "Model File Name": diagram_name,        # added
        "Load File Name": path.name,            # added
        "CMDB Asset ID": cmdb_id,
        "CMDB Asset Name": cmdb_name,
        "Container Type": container_type,
        "Definition": with_fallback(df, "Column Definition", ["Definition (Column)", "Col Definition"]),
        "Table Logical Name": table_logical,
        "Sub Model Name": sub_model,
        "Glossary Attribute ID provided in model": with_fallback(df, "Glossary Attribute ID", ["Glossary Attribute ID provided in model"]),
        "Primary Key Indicator": get_series(df, "Primary Key Indicator"),
        "Data Dic Data Type": with_fallback(df, "Data Type", ["Data Dic Data Type"]).map(normalize_dtype),
        "Maximum Text Length": with_fallback(df, "Length", ["Maximum Text Length"]),
        "Data Dic Scale": with_fallback(df, "Scale", ["Data Dic Scale"]),
        "Null-able Indicator": with_fallback(df, "Null", ["Null-able Indicator"]),
        "Logical Column Name": with_fallback(df, "Column Logical Name", ["Logical Column Name"]),
        "Column Sequence Number": get_series(df, "Column Sequence Number"),
        "Name": data_element,  # Data Element Name
    })
    # Compose names used for relationships and full column identity
    part_of_full_name = (
        cmdb_id.astype(str) + "." + container_type.astype(str) + "." + table_name.astype(str)
    )
    col_df["Community"] = cmdb_id.astype(str)
    col_df["Domain"] = cmdb_id.astype(str) + "." + container_type.astype(str)
    col_df["Full Name"] = part_of_full_name + "." + data_element.astype(str)

    # ========= RELATIONSHIP FILE =========
    rel_df = pd.DataFrame({
        "Full Name": col_df["Full Name"],
        "[Column] is part of [Table] > Full Name": part_of_full_name
    })

    # ========= SAVE =========
    base = path.stem
    table_out = tables_dir / f"{base}_table.xlsx"
    col_out = columns_dir / f"{base}_column.xlsx"
    rel_out = rels_dir / f"{base}_relationships.xlsx"

    table_df.to_excel(table_out, index=False)
    col_df.to_excel(col_out, index=False)
    rel_df.to_excel(rel_out, index=False)

    print(f"  → Tables:        {table_out.name} ({len(table_df)} rows)")
    print(f"  → Columns:       {col_out.name} ({len(col_df)} rows)")
    print(f"  → Relationships: {rel_out.name} ({len(rel_df)} rows)")
    print("Done.")

def main():
    excel_files = sorted(input_path.glob("*.xls*"))
    if not excel_files:
        print("No Excel files found in ./input/")
        print(f"Output run folder created: {output_root}")
        return

    print(f"Run folder: {output_root}")
    print(f"Found {len(excel_files)} file(s) to process.")
    for f in excel_files:
        process_file(f)

if __name__ == "__main__":
    main()
