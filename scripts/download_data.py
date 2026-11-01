"""Download Online Retail II (UCI 502) into $DATA_DIR/raw, write SHA256SUMS, make it read-only.

Idempotent: if SHA256SUMS exists, only verifies it.
    micromamba run -n demand-showcase python scripts/download_data.py
"""

import sys
import urllib.request
import zipfile

from retail.io import (
    URL,
    XLSX_NAME,
    ZIP_NAME,
    data_dir,
    make_read_only,
    verify_checksums,
    write_checksums,
)


def main() -> int:
    raw = data_dir() / "raw"
    if (raw / "SHA256SUMS").exists():
        bad = verify_checksums(raw)
        print("checksums ok" if not bad else f"checksum mismatch: {bad}")
        return 1 if bad else 0
    raw.mkdir(parents=True, exist_ok=True)
    if not (raw / ZIP_NAME).exists():
        print(f"downloading {URL}")
        urllib.request.urlretrieve(URL, raw / ZIP_NAME)
    with zipfile.ZipFile(raw / ZIP_NAME) as z:
        z.extract(XLSX_NAME, raw)
    print(write_checksums(raw, [ZIP_NAME, XLSX_NAME]).read_text(), end="")
    make_read_only(raw)
    return 0


if __name__ == "__main__":
    sys.exit(main())
