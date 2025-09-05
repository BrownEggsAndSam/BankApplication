#!/usr/bin/env python3
"""
Excel ➜ SQL INSERT generator

Purpose
-------
Read an Excel file and emit batched INSERT statements to load an existing table
(default: glossary_history_table). Dialect-aware identifier quoting. Sensible
NULL / string escaping. Optionally wrap in a transaction.

Quick start
-----------
1) Put your Excel file in: ./__excelToSQL/input/
2) Run:
   python excel_to_sql_glossary_history_table.py \
     --excel "MyData.xlsx" \
     --sheet "Sheet1" \
     --table "glossary_history_table" \
     --dialect postgres
3) The .sql file will be written to: ./__excelToSQL/output/

Defaults
--------
- Dialect: postgres (identifier quotes with ")
- Table: glossary_history_table
- One sheet: first sheet if --sheet not provided
- Batch size: 1000 rows per INSERT
- Trim strings, convert empty strings to NULL
- Values are escaped using doubled single quotes
- Wrap in a single transaction (BEGIN/COMMIT)

Change these via CLI flags below or by editing the DEFAULTS section.
"""

from __future__ import annotations
import argparse
import os
from pathlib import Path
from typing import Iterable, List
from datetime import date, datetime
from decimal import Decimal

import numpy as np
import pandas as pd

# -------------------------
# DEFAULTS (can be overridden via CLI)
# -------------------------
PROJECT_NAME = "__excelToSQL"
package_input_path = f"./{PROJECT_NAME}/input/"
package_output_path = f"./{PROJECT_NAME}/output/"

DEFAULT_TABLE = "glossary_history_table"
DEFAULT_DIALECT = "postgres"  # one of: postgres | sqlserver | mysql | snowflake | oracle | sqlite | none
DEFAULT_BATCH_SIZE = 1000
DEFAULT_WRAP_IN_TX = True
TRIM_STRINGS = True
EMPTY_STRING_AS_NULL = True

# -------------------------
# Helpers
# -------------------------

def trim_all_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Trim whitespace on string-like cells across entire DataFrame."""
    def _trim(x):
        if isinstance(x, str):
            s = x.strip()
            if EMPTY_STRING_AS_NULL and s == "":
                return np.nan
            return s
        return x
    return df.applymap(_trim)


def list_excels_in(path: str) -> List[str]:
    exts = (".xlsx", ".xlsm", ".xltx", ".xls", ".xlsb")
    return [f for f in os.listdir(path) if f.lower().endswith(exts)]


def pick_excel_or_raise(path: str, explicit: str | None) -> str:
    if explicit:
        return explicit
    files = list_excels_in(path)
    if not files:
        raise FileNotFoundError(
            f"No Excel files found in {path}. Provide --excel or add a file there.")
    if len(files) > 1:
        raise ValueError(
            f"Multiple Excel files found in {path}: {files}. Specify one with --excel.")
    return files[0]


def quote_ident(name: str, dialect: str) -> str:
    if dialect == "sqlserver":
        return f"[{name}]"
    if dialect == "mysql":
        return f"`{name}`"
    if dialect in {"postgres", "snowflake", "oracle", "sqlite"}:
        return f'"{name}"'
    # none: no quoting
    return name


def escape_string(val: str) -> str:
    # Double any single quotes for SQL literal safety
    return val.replace("'", "''")


def format_literal(val, dialect: str) -> str:
    """Convert a Python/NumPy/Pandas scalar to a SQL literal string (including quotes/NULL)."""
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "NULL"

    # Pandas NA types
    try:
        import pandas as _pd  # noqa
        if pd.isna(val):
            return "NULL"
    except Exception:
        pass

    # Datetime / Date
    if isinstance(val, (datetime, pd.Timestamp)):
        # Normalize to second precision for tidy SQL
        dt = pd.Timestamp(val).to_pydatetime().replace(tzinfo=None)
        return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
    if isinstance(val, date):
        return f"'{val.strftime('%Y-%m-%d')}'"

    # Boolean
    if isinstance(val, (bool, np.bool_)):
        if dialect in {"sqlserver", "mysql"}:
            return "1" if bool(val) else "0"
        return "TRUE" if bool(val) else "FALSE"

    # Numbers
    if isinstance(val, (int, np.integer)):
        return str(int(val))
    if isinstance(val, (float, np.floating)):
        if np.isfinite(val):
            # Avoid scientific notation for most DBs
            return ("{0:.15g}").format(float(val))
        return "NULL"
    if isinstance(val, Decimal):
        return format(val, 'f')

    # Everything else -> treat as string
    sval = str(val)
    if TRIM_STRINGS:
        sval = sval.strip()
    if EMPTY_STRING_AS_NULL and sval == "":
        return "NULL"
    return f"'{escape_string(sval)}'"


def chunk_iterable(n: int, total: int) -> Iterable[range]:
    start = 0
    while start < total:
        end = min(start + n, total)
        yield range(start, end)
        start = end


def build_insert_sql(table: str, columns: List[str], values_rows: List[List[str]], dialect: str) -> str:
    quoted_cols = ", ".join(quote_ident(c, dialect) for c in columns)
    values_sql = ",\n  ".join("(" + ", ".join(row) + ")" for row in values_rows)
    return f"INSERT INTO {quote_ident(table, dialect)} ({quoted_cols})\nVALUES\n  {values_sql};\n"


# -------------------------
# Main runner
# -------------------------

def main():
    parser = argparse.ArgumentParser(description="Excel ➜ SQL INSERT generator")
    parser.add_argument("--excel", help="Excel filename in input folder (or absolute path)")
    parser.add_argument("--sheet", help="Excel sheet name (default: first sheet)")
    parser.add_argument("--table", default=DEFAULT_TABLE, help="Target table name")
    parser.add_argument("--dialect", default=DEFAULT_DIALECT,
                        choices=["postgres", "sqlserver", "mysql", "snowflake", "oracle", "sqlite", "none"],
                        help="SQL dialect for identifier quoting and boolean formatting")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
                        help="Rows per INSERT batch")
    parser.add_argument("--no-transaction", action="store_true", help="Do not wrap in BEGIN/COMMIT")
    parser.add_argument("--project", default=PROJECT_NAME, help="Project folder name (for input/output roots)")

    args = parser.parse_args()

    # Resolve IO paths
    in_root = Path(f"./{args.project}/input/")
    out_root = Path(f"./{args.project}/output/")
    out_root.mkdir(parents=True, exist_ok=True)

    # Determine Excel path
    if args.excel and os.path.isabs(args.excel):
        excel_path = Path(args.excel)
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel not found: {excel_path}")
    else:
        excel_name = pick_excel_or_raise(str(in_root), args.excel)
        excel_path = in_root / excel_name

    print(f"[INFO] Reading Excel: {excel_path}")
    # Read Excel (sheet=0 means first sheet)
    sheet_to_use = args.sheet if args.sheet else 0
    df = pd.read_excel(excel_path, sheet_name=sheet_to_use)

    # Standardize & clean
    if TRIM_STRINGS:
        df = trim_all_columns(df)

    # Ensure column order is preserved from Excel
    columns = [str(c) for c in df.columns]
    print(f"[INFO] Columns ({len(columns)}): {columns}")
    print(f"[INFO] Rows: {len(df)}")

    # Prepare output file
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_root / f"{args.table}_{ts}.sql"

    wrap_tx = not args.no_transaction

    emitted_rows = 0
    with out_file.open("w", encoding="utf-8") as f:
        if wrap_tx:
            f.write("BEGIN;\n\n")
        # Write batched INSERTs
        total_rows = len(df)
        if total_rows == 0:
            print("[WARN] No data rows found. Emitting empty transaction file.")
        for batch_range in chunk_iterable(args.batch_size, total_rows):
            batch_values: List[List[str]] = []
            for r in batch_range:
                row = df.iloc[r]
                vals = [format_literal(row[c], args.dialect) for c in df.columns]
                batch_values.append(vals)
            sql = build_insert_sql(args.table, columns, batch_values, args.dialect)
            f.write(sql + "\n")
            emitted_rows += len(batch_values)
            print(f"[INFO] Emitted rows: {emitted_rows}/{total_rows}")
        if wrap_tx:
            f.write("COMMIT;\n")

    print(f"[OK] Wrote SQL to: {out_file}")


if __name__ == "__main__":
    main()
