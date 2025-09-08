import os
import re
import csv
import unicodedata
import pandas as pd
from io import StringIO

# =========================
# Paths & filenames
# =========================
package_input_path = './_csvCleaner/input/'
package_output_path = './_csvCleaner/output/'
input_file  = 'input.csv'
output_file = 'output_cleaned.csv'

# Ensure output folder exists
os.makedirs(package_output_path, exist_ok=True)

# =========================
# Config
# =========================
# If True, remove ALL newlines from within cells (prevents CSV import quote errors)
STRIP_INNER_NEWLINES = True

# Remove other control characters inside cells (recommended)
STRIP_CONTROL_CHARS = True

# =========================
# Helpers
# =========================
CONTROL_CHARS_PATTERN = re.compile(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]')
NBSP = '\xa0'

SMART_PUNCT_TRANS = str.maketrans({
    '“': '"', '”': '"', '„': '"', '‟': '"',
    '‘': "'", '’': "'", '‚': "'", '‛': "'",
    '—': '-', '–': '-', '−': '-', '•': '*',
    NBSP: ' '
})

def normalize_text(s: str) -> str:
    """Unicode normalize, fix smart punctuation, strip control chars/newlines/tabs, and trim."""
    if s is None:
        return s
    # Ensure string
    s = str(s)

    # Normalize unicode (compatibility form)
    s = unicodedata.normalize('NFKC', s)

    # Replace smart punctuation + NBSP
    s = s.translate(SMART_PUNCT_TRANS)

    # Optionally strip control characters (except standard comma, quotes handled by CSV writer)
    if STRIP_CONTROL_CHARS:
        s = CONTROL_CHARS_PATTERN.sub('', s)

    # Collapse inner newlines/tabs to spaces if requested
    if STRIP_INNER_NEWLINES:
        s = s.replace('\r\n', ' ').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')

    # Final trim
    s = s.strip()
    return s

def nullify(s: str) -> str:
    """Convert blanks and 'null' (any case) to literal 'NULL'."""
    if s is None:
        return 'NULL'
    txt = s.strip()
    if txt == "" or txt.lower() == "null":
        return 'NULL'
    return s

def try_read_text(path: str) -> str:
    """Try multiple encodings and return decoded text."""
    encodings = ["utf-8-sig", "utf-8", "cp1252", "latin1"]
    last_err = None
    with open(path, "rb") as f:
        raw = f.read()
    for enc in encodings:
        try:
            return raw.decode(enc)
        except UnicodeDecodeError as e:
            last_err = e
            continue
    # Fallback: replace undecodable bytes so we can still clean
    return raw.decode("utf-8", errors="replace")

def read_csv_resilient(csv_text: str) -> pd.DataFrame:
    """
    Read CSV via pandas with the python engine (more tolerant),
    without inferring dtypes (keep as strings).
    """
    return pd.read_csv(
        StringIO(csv_text),
        engine="python",
        dtype=str,
        keep_default_na=False,  # don't auto-convert to NaN
        na_values=[],           # treat nothing as NaN; we handle nulls ourselves
        quoting=csv.QUOTE_MINIMAL
    )

# =========================
# Main
# =========================
def main():
    # 1) Read raw text with resilient decoding
    raw_text = try_read_text(os.path.join(package_input_path, input_file))

    # 2) Normalize the entire file text to reduce catastrophic parse issues
    #    (fix BOM handled by utf-8-sig; here we ensure line endings are consistent)
    raw_text = raw_text.replace('\r\n', '\n').replace('\r', '\n')

    # 3) Parse with pandas (tolerant engine)
    df = read_csv_resilient(raw_text)

    # 4) Cell-wise cleanup
    #    - unicode normalize + smart quotes -> ascii-ish
    #    - strip control chars/newlines/tabs
    #    - trim
    df = df.applymap(lambda x: normalize_text(x) if x is not None else x)

    # 5) Standardize nulls
    df = df.applymap(nullify)

    # 6) Optional: strip surrounding quotes literally present in text (rare legacy case)
    #    If your inputs sometimes contain embedded literal double-quotes wrapping the whole value,
    #    uncomment the next line to remove a single pair of surrounding quotes.
    # df = df.applymap(lambda x: x[1:-1] if isinstance(x, str) and len(x) >= 2 and x[0] == '"' and x[-1] == '"' else x)

    # 7) Save cleaned CSV (UTF-8 without BOM)
    out_path = os.path.join(package_output_path, output_file)
    df.to_csv(out_path, index=False, encoding="utf-8", quoting=csv.QUOTE_MINIMAL)

if __name__ == "__main__":
    main()
