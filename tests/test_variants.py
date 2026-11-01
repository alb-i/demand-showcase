import numpy as np
import pandas as pd
import pytest

from retail.variants import sku_changes, summary, weekly_changes


def panel(rows):
    df = pd.DataFrame(rows, columns=["stock_code", "week", "units", "closed"])
    df["week"] = pd.to_datetime(df["week"])
    df["revenue"] = df["units"] * 2.0
    return df


BASE = panel(
    [
        ("A", "2011-01-03", 10.0, False),
        ("A", "2011-01-10", 0.0, False),
        ("A", "2011-01-17", np.nan, True),
        ("B", "2011-01-03", 4.0, False),
    ]
)
OTHER = panel(
    [
        ("A", "2011-01-03", 8.0, False),
        ("A", "2011-01-10", 0.0, False),
        ("C", "2011-01-10", 1.0, False),
    ]
)


def test_summary():
    s = summary(BASE)
    assert s == {
        "skus": 2,
        "rows": 4,
        "units": 14.0,
        "revenue": 28.0,
        "zero_weeks": pytest.approx(1 / 3),
    }


def test_sku_changes_orders_by_absolute_change_and_handles_missing():
    ch = sku_changes(BASE, OTHER)
    assert list(ch.index) == ["C", "B", "A"]  # C new (inf), B gone (-100 %), A -20 %
    assert ch.loc["A", "rel_change"] == pytest.approx(-0.2)
    assert ch.loc["B", "rel_change"] == -1.0 and np.isnan(ch.loc["C", "rel_change"])


def test_weekly_changes():
    w = weekly_changes(BASE, OTHER)
    assert w.loc["2011-01-03", "rel_change"] == pytest.approx(8 / 14 - 1)
    assert np.isnan(w.loc["2011-01-17", "units_base"])
