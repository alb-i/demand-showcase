import pandas as pd

from retail.io import as_code, make_read_only, normalise, verify_checksums, write_checksums


def test_as_code_keeps_strings_and_strips_float_cells():
    col = pd.Series([85123, 85123.0, "85123A", " C489449 ", "00123"], dtype=object)
    assert list(as_code(col)) == ["85123", "85123", "85123A", "C489449", "00123"]


def test_normalise_dtypes_and_line_ids():
    raw = pd.DataFrame(
        {
            "Invoice": [489434, "C489449"],
            "StockCode": [85048, "79323P"],
            "Description": [" LED LIGHT ", None],
            "Quantity": [12, -6],
            "InvoiceDate": ["2009-12-01 07:45:00", "2009-12-01 10:33:00"],
            "Price": [6.95, 2.95],
            "Customer ID": [13085.0, None],
            "Country": ["United Kingdom", "Australia"],
        }
    )
    df = normalise(raw, "Year 2009-2010")
    assert list(df["invoice"]) == ["489434", "C489449"]
    assert list(df["stock_code"]) == ["85048", "79323P"]
    assert df["description"].iloc[0] == "LED LIGHT" and pd.isna(df["description"].iloc[1])
    assert str(df["customer_id"].dtype) == "Int64" and pd.isna(df["customer_id"].iloc[1])
    assert df["quantity"].dtype == "int64" and list(df["line"]) == [0, 1]
    assert (df["sheet"] == "Year 2009-2010").all()


def test_checksums_roundtrip_and_read_only(tmp_path):
    (tmp_path / "a.bin").write_bytes(b"abc")
    (tmp_path / "b.bin").write_bytes(b"def")
    write_checksums(tmp_path, ["a.bin", "b.bin"])
    assert verify_checksums(tmp_path) == []
    (tmp_path / "b.bin").write_bytes(b"changed")
    assert verify_checksums(tmp_path) == ["b.bin"]
    make_read_only(tmp_path)
    try:
        assert not (tmp_path.stat().st_mode & 0o222)
        assert not ((tmp_path / "a.bin").stat().st_mode & 0o222)
    finally:
        tmp_path.chmod(0o755)
        for p in tmp_path.iterdir():
            p.chmod(0o644)
