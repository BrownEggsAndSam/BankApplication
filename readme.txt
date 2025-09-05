import os
import re
import sys
import glob
import pandas as pd
from datetime import datetime

# ── Project paths ──────────────────────────────────────────────────────────────
project_name = "__glossaryHistoryBackfill"
package_input_path = f'./{project_name}/input/'
package_output_path = f'./{project_name}/output/'

os.makedirs(package_input_path, exist_ok=True)
os.makedirs(package_output_path, exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def trim_all_columns(df: pd.DataFrame) -> pd.DataFrame:
    trim_strings = lambda x: x.strip() if isinstance(x, str) else x
    return df.applymap(trim_strings)

def find_excel_file(input_dir: str) -> str:
    # Pick the most recently modified Excel file if multiple are present
    patterns = ("*.xlsx", "*.xls", "*.xlsm")
    files = []
    for p in patterns:
        files.extend(glob.glob(os.path.join(input_dir, p)))
    if not files:
        raise FileNotFoundError(
            f"No Excel files found in {input_dir}. "
            "Place your source workbook there (e.g., data.xlsx)."
        )
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[0]

def to_sql_literal(val):
    """Return a SQL literal string for a value (NULL or 'escaped')."""
    if pd.isna(val) or val == "":
        return "NULL"
    s = str(val)
    # Normalize newlines and escape single quotes
    s = s.replace("\r\n", "\n").replace("\r", "\n").replace("'", "''")
    return f"'{s}'"

def sanitize_quarter(q):
    """Make a safe filename fragment from the Quarter value."""
    if pd.isna(q) or str(q).strip() == "":
        return "Unspecified"
    s = str(q).strip()
    s = re.sub(r"[^\w\-\.\(\) ]+", "_", s)
    s = s.replace(" ", "_")
    return s

# ── Configuration: Excel → Table column mappings ───────────────────────────────
# LEFT = target column in "HAE".glossary_history
# RIGHT = source Excel column name
MAPPING = {
    '"name"': "Attribute Name",
    "full_name": "Attribute Registry ID",            # per your spec
    "attribute_registry_id": "Attribute Registry ID",
    "authoritative_source": "Authoritative Source",
    "subject_area": "Business Segment",
    "definition": "Definition",
    '"domain"': "Domain",
    "historical_approved_date": "Historical Approved Date",
    "kde": "KDE",
    "lastmodifiedon": "Last Modified On",
    "privacy_designation": "Privacy Designation",
    "quarter_indicator": "Quarter",
    "status": "Status",
}

# ── Load Excel ────────────────────────────────────────────────────────────────
src_path = find_excel_file(package_input_path)
print(f"[INFO] Reading workbook: {src_path}")

df = pd.read_excel(src_path)  # reads first sheet; adjust if needed
df = trim_all_columns(df)

# Verify required source columns exist (only those present will be used)
missing = [src for src in MAPPING.values() if src not in df.columns]
if missing:
    print("[WARN] The following columns were not found in the Excel and will be NULL in inserts:")
    for m in missing:
        print(f"       - {m}")

# Build a working frame with only the mapped columns we have
available_pairs = [(tgt, src) for tgt, src in MAPPING.items() if src in df.columns]
if not available_pairs:
    raise ValueError("None of the expected source columns were found. Check your Excel headers.")

work = pd.DataFrame()
for tgt, src in available_pairs:
    work[tgt] = df[src]

# If some mapped targets are missing in Excel, add them as empty (NULL later)
for tgt, src in MAPPING.items():
    if tgt not in work.columns:
        work[tgt] = pd.NA

# Deduplicate on (quarter_indicator, full_name) as per your unique identifier
# Keep the last occurrence (typical for backfills where later rows are latest)
before = len(work)
work = work.drop_duplicates(subset=["quarter_indicator", "full_name"], keep="last")
after = len(work)
print(f"[INFO] Deduplicated on (quarter_indicator, full_name): {before} → {after}")

# ── Group by Quarter and write .sql per quarter ───────────────────────────────
# Prepare a stable INSERT column list consisting of the mapped target columns
# (only the ones you actually map; all other table columns are left NULL by omission)
insert_columns = list(MAPPING.keys())

# Quote identifiers for SQL: already quoted for name/domain; quote the rest safely
def quote_ident(ident: str) -> str:
    # ident may already be quoted (e.g., "name"); honor that
    if ident.startswith('"') and ident.endswith('"'):
        return ident
    return f'"{ident}"'

insert_columns_quoted = [quote_ident(c) for c in insert_columns]

# Output folder with timestamp for traceability
run_folder = os.path.join(package_output_path, datetime.now().strftime("backfill_%Y%m%d_%H%M%S"))
os.makedirs(run_folder, exist_ok=True)

files_written = []

for quarter_value, group in work.groupby("quarter_indicator", dropna=False):
    quarter_tag = sanitize_quarter(quarter_value)
    out_path = os.path.join(run_folder, f'insert_glossary_history_{quarter_tag}.sql')

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("-- Backfill INSERTs for \"HAE\".glossary_history\n")
        f.write(f"-- Source workbook: {os.path.basename(src_path)}\n")
        f.write(f"-- Generated: {datetime.now().isoformat(timespec='seconds')}\n")
        f.write(f"-- Quarter: {quarter_value if pd.notna(quarter_value) else '(NULL/Unspecified)'}\n\n")

        # Optional: one big multi-row INSERT per file (faster), or one row per statement.
        # Here we’ll do one row per statement for simplicity/troubleshooting.
        for _, row in group.iterrows():
            values = [to_sql_literal(row.get(tgt)) for tgt in insert_columns]
            cols_sql = ", ".join(insert_columns_quoted)
            vals_sql = ", ".join(values)
            stmt = f'INSERT INTO "HAE".glossary_history ({cols_sql}) VALUES ({vals_sql});\n'
            f.write(stmt)

    files_written.append(out_path)
    print(f"[INFO] Wrote: {out_path}  (rows: {len(group)})")

print("\n[SUMMARY]")
print(f"Total files: {len(files_written)}")
for p in files_written:
    print(" -", p)

print("\nDone.")
