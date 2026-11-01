import numpy as np
import pandas as pd
from conftest import lines

from retail.panel import (
    build_panel,
    canonical_descriptions,
    drop_last_week,
    panel_totals,
    trading_weeks,
    week_start,
)


def test_week_start_is_iso_monday():
    ts = pd.Series(pd.to_datetime(["2011-01-03 09:00", "2011-01-09 23:59", "2011-01-10 00:00"]))
    assert list(week_start(ts)) == list(pd.to_datetime(["2011-01-03", "2011-01-03", "2011-01-10"]))


def test_trading_weeks_marks_weeks_without_trading_days_closed():
    df = lines(
        ("1", "A", 1, "2010-12-20 10:00", 1.0, 1),
        ("2", "A", 1, "2010-12-23 10:00", 1.0, 1),
        ("C3", "A", -1, "2011-01-04 10:00", 1.0, 1),  # a cancellation counts as trading
    )
    w = trading_weeks(df)
    assert list(w["week"]) == list(pd.to_datetime(["2010-12-20", "2010-12-27", "2011-01-03"]))
    assert list(w["trading_days"]) == [2, 0, 1]
    assert list(w["closed"]) == [False, True, False]


def test_drop_last_week():
    sales = lines(("1", "A", 1, "2011-11-28", 1.0, 1), ("2", "A", 2, "2011-12-09", 1.0, 1))
    returns = lines(("C3", "A", -1, "2011-12-05", 1.0, 1))
    s, r, gone, last = drop_last_week(sales, returns)
    assert last == pd.Timestamp("2011-12-05")
    assert list(s["invoice"]) == ["1"] and len(r) == 0 and sorted(gone["invoice"]) == ["2", "C3"]


def panel_case():
    sales = lines(
        ("1", "A", 10, "2010-12-20 10:00", 1.0, 1),
        ("1", "A", 2, "2010-12-20 10:00", 1.5, 2),
        ("2", "A", 4, "2010-12-21 10:00", 1.0, 2),
        ("3", "A", 5, "2011-01-10 10:00", 2.0, None),
        ("4", "B", 7, "2011-01-03 10:00", 3.0, 3),
    )
    returns = lines(
        ("C5", "A", -3, "2011-01-04 10:00", 1.0, 1),  # inside A's window
        ("C6", "B", -1, "2010-12-21 10:00", 3.0, 3),  # before B's first sale: outside
    )
    weeks = trading_weeks(pd.concat([sales, returns]))
    return sales, returns, weeks


def test_build_panel_window_zero_fill_closed_and_aggregates():
    sales, returns, weeks = panel_case()
    panel, outside = build_panel(sales, returns, weeks)
    a = panel[panel["stock_code"] == "A"].set_index("week")
    assert list(a.index) == list(
        pd.to_datetime(["2010-12-20", "2010-12-27", "2011-01-03", "2011-01-10"])
    )
    w = a.loc["2010-12-20"]
    assert (w["units"], w["revenue"], w["n_invoices"], w["n_customers"]) == (16, 17.0, 2, 2)
    assert w["median_price"] == 1.0
    assert w["top_customer_share"] == 10 / 16  # customer 1: 10 of 16 units
    assert a.loc["2010-12-27", "closed"] and np.isnan(a.loc["2010-12-27", "units"])
    assert a.loc["2011-01-03", "units"] == 0 and a.loc["2011-01-03", "returned_units"] == 3
    assert pd.isna(a.loc["2011-01-10", "top_customer_share"])  # only a line without customer
    b = panel[panel["stock_code"] == "B"]
    assert list(b["week"]) == [pd.Timestamp("2011-01-03")]  # no rows before launch
    assert list(outside["invoice"]) == ["C6"]
    assert panel_totals(panel) == {"units": 28, "revenue": 48.0, "returned_units": 3}


def test_canonical_descriptions_most_frequent_then_alphabetical():
    df = lines(
        ("1", "A", 1, "2011-01-03", 1.0, 1, "MUG RED"),
        ("2", "A", 1, "2011-01-03", 1.0, 1, "MUG  RED"),
        ("3", "A", 1, "2011-01-03", 1.0, 1, "MUG RED"),
        ("4", "B", 1, "2011-01-03", 1.0, 1, "ZEBRA"),
        ("5", "B", 1, "2011-01-03", 1.0, 1, "APE"),
    )
    d = canonical_descriptions(df).set_index("stock_code")
    assert d.loc["A", "description"] == "MUG RED" and d.loc["A", "n_descriptions"] == 2
    assert d.loc["B", "description"] == "APE" and d.loc["B", "lines"] == 2
