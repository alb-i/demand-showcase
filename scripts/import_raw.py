"""Import both xlsx sheets into $DATA_DIR/processed/raw.parquet with explicit dtypes (~3 min).
micromamba run -n demand-showcase python scripts/import_raw.py
"""

from retail.io import XLSX_NAME, data_dir, read_xlsx


def main() -> None:
    root = data_dir()
    df = read_xlsx(root / "raw" / XLSX_NAME)
    out = root / "processed" / "raw.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"{len(df)} rows -> {out}")
    print(df.groupby("sheet").size().to_string())
    print(df.dtypes.to_string())


if __name__ == "__main__":
    main()
