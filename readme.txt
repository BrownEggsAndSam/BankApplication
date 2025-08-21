import pandas as pd
from pathlib import Path
from datetime import datetime

# -------- Paths --------
input_path = "./_pddReuploadScript/input/"
output_path = "./_pddReuploadScript/output/"
Path(output_path).mkdir(parents=True, exist_ok=True)

# Timestamped run folder + relationships subfolder
run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
run_root = f"{output_path}{run_stamp}/"
rels_dir = f"{run_root}relationships/"
Path(rels_dir).mkdir(parents=True, exist_ok=True)

# -------- Helpers --------
def trim_all_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace from all string cells (no applymap)."""
    return df.map(lambda x: x.strip() if isinstance(x, str) else x)

def require_columns(df: pd.DataFrame, cols: list[str], file_name: str):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"{file_name}: missing required columns: {missing}")

def ensure_no_conflicting_table_ids(tables: pd.DataFrame, file_name: str):
    grp = tables.groupby("Full Name")["Asset Id"].nunique(dropna=True)
    conflicts = grp[grp > 1]
    if not conflicts.empty:
        bad = conflicts.index.tolist()
        raise ValueError(
            f"{file_name}: conflicting Asset Ids found for Table Full Name(s): {bad}"
        )

def derive_table_full_name(full_name: str, file_name: str, row_idx: int) -> str:
    if not isinstance(full_name, str):
        raise ValueError(f"{file_name}: Row {row_idx}: Full Name is not a string for a Column asset.")
    if "." not in full_name:
        raise ValueError(f"{file_name}: Row {row_idx}: Column Full Name must contain at least one '.' → '{full_name}'")
    return full_name.rsplit(".", 1)[0]

# -------- Core Processing --------
def process_file(file: Path):
    print(f"\n--- Processing: {file.name} ---")
    df = pd.read_excel(file, dtype=object)
    df = trim_all_columns(df)

    required = ["Asset Type", "Full Name", "Asset Id"]
    require_columns(df, required, file.name)

    atype_norm = df["Asset Type"].map(lambda x: str(x).strip().casefold() if isinstance(x, str) else x)
    tables = df[atype_norm == "table"].copy()
    columns = df[atype_norm == "column"].copy()

    ensure_no_conflicting_table_ids(tables, file.name)

    table_map = (
        tables[["Full Name", "Asset Id"]]
        .dropna(subset=["Full Name"])
        .drop_duplicates(subset=["Full Name"])
        .set_index("Full Name")["Asset Id"]
        .to_dict()
    )

    # Build the mapping without persisting derived name to output
    rel_asset_ids = []
    for idx, val in columns["Full Name"].items():
        derived_table_name = derive_table_full_name(val, file.name, idx)
        rel_asset_ids.append(table_map.get(derived_table_name, None))

    out = columns.copy()
    out["[Column] is part of [Table] > Asset Id"] = rel_asset_ids

    # Drop all-empty columns
    out = out.loc[:, out.notna().any(axis=0)]

    # Save per-file output
    base = file.stem
    out_path = f"{rels_dir}{base}_relationships_by_assetid.xlsx"
    out.to_excel(out_path, index=False)

    total_cols = len(out)
    populated = out["[Column] is part of [Table] > Asset Id"].notna().sum()
    print(f"  → Relationships file: {Path(out_path).name}")
    print(f"    Rows (Column assets only): {total_cols}")
    print(f"    '[Column] is part of [Table] > Asset Id' populated: {populated}/{total_cols}")

def main():
    excel_files = list(Path(input_path).glob("*.xls*"))
    if not excel_files:
        print("No Excel files found in ./_pddReuploadScript/input/")
        return
    print(f"Found {len(excel_files)} file(s). Run folder: {run_root}")

    for file in excel_files:
        process_file(file)

if __name__ == "__main__":
    main()
