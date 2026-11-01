"""Raw data: download checks and xlsx -> raw.parquet with explicit dtypes.

Paths come from $DATA_DIR (.env of the repo); $DATA_DIR/raw is read-only after the download.
"""

import hashlib
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

REPO_DIR = Path(__file__).resolve().parents[2]
URL = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
ZIP_NAME = "online_retail_ii.zip"
XLSX_NAME = "online_retail_II.xlsx"
SHEETS = ["Year 2009-2010", "Year 2010-2011"]

# Column names as in the xlsx -> snake_case names used everywhere else
COLUMNS = {
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
}


def data_dir() -> Path:
    load_dotenv(REPO_DIR / ".env")
    return Path(os.environ["DATA_DIR"])


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_checksums(folder: Path, names: list[str]) -> Path:
    """SHA256SUMS in the format of `sha256sum` (checkable with `sha256sum -c`)."""
    out = folder / "SHA256SUMS"
    out.write_text("".join(f"{sha256_file(folder / n)}  {n}\n" for n in sorted(names)))
    return out


def verify_checksums(folder: Path) -> list[str]:
    """Names whose checksum does not match SHA256SUMS (missing files count as mismatches)."""
    bad = []
    for line in (folder / "SHA256SUMS").read_text().splitlines():
        digest, name = line.split(maxsplit=1)
        path = folder / name.strip()
        if not path.is_file() or sha256_file(path) != digest:
            bad.append(name.strip())
    return bad


def make_read_only(folder: Path) -> None:
    for path in folder.iterdir():
        path.chmod(0o444)
    folder.chmod(0o555)


def normalise(df: pd.DataFrame, sheet: str) -> pd.DataFrame:
    """Raw sheet -> explicit dtypes. Invoice and StockCode stay strings (leading zeros, letter
    suffixes, "C" prefix); numbers that Excel stored as numeric cells become their digits."""
    df = df.rename(columns=COLUMNS)[list(COLUMNS.values())]
    out = pd.DataFrame(
        {
            "invoice": as_code(df["invoice"]),
            "stock_code": as_code(df["stock_code"]),
            "description": df["description"].astype("string").str.strip(),
            "quantity": df["quantity"].astype("int64"),
            "invoice_date": pd.to_datetime(df["invoice_date"]).astype("datetime64[s]"),
            "price": df["price"].astype("float64"),
            "customer_id": pd.to_numeric(df["customer_id"]).astype("Int64"),
            "country": df["country"].astype("string"),
            "sheet": pd.Series(sheet, index=df.index, dtype="string"),
        }
    )
    out["line"] = range(len(out))  # row in the sheet (0-based, without header): stable line id
    return out


def as_code(col: pd.Series) -> pd.Series:
    """Code column -> string; numeric cells (85123 or 85123.0) become "85123"."""

    def one(v):
        if isinstance(v, float) and v.is_integer():
            return str(int(v))
        return str(v).strip()

    return col.map(one).astype("string")


def read_xlsx(path: Path) -> pd.DataFrame:
    """Both sheets, concatenated in sheet order."""
    sheets = pd.read_excel(path, sheet_name=SHEETS, dtype=object, engine="openpyxl")
    return pd.concat([normalise(sheets[s], s) for s in SHEETS], ignore_index=True)
