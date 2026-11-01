import importlib.util

import numpy as np
import pandas as pd
import pytest
import yaml
from conftest import W0, panel

from retail.io import REPO_DIR
from retail.segments import (
    abc,
    bulk_lines,
    class_table,
    customer_concentration,
    customer_order_mix,
    demand_stats,
    history,
    segment_table,
    syntetos_boylan,
    without_large_orders,
    xyz,
)


def test_history_drops_closed_and_later_weeks():
    p = panel({"A": [1, 2, 3, 4]}, closed=[1])
    h = history(p, W0 + pd.Timedelta(weeks=3))
    assert h["units"].tolist() == [1.0, 3.0]


def test_abc_cumulative_share():
    rev = pd.Series({"a": 70.0, "b": 15.0, "c": 10.0, "d": 5.0})
    # a: 0 before -> A; b: 70 % before -> A (crosses 80 %); c: 85 % -> B; d: 95 % -> C
    assert abc(rev, 0.8, 0.95).tolist() == ["A", "A", "B", "C"]


def test_xyz_cut_offs():
    cv = pd.Series([0.5, 0.51, 1.0, 1.2, np.nan])
    out = xyz(cv, 0.5, 1.0)
    assert out.iloc[:4].tolist() == ["X", "Y", "Y", "Z"] and pd.isna(out.iloc[4])


def test_demand_stats_adi_cv2():
    s = demand_stats(panel({"A": [4, 0, 4, 0], "B": [2, 6, 2, 6]}))
    assert s.loc["A", "adi"] == 2.0 and s.loc["A", "cv2"] == 0.0
    assert s.loc["B", "adi"] == 1.0 and s.loc["B", "cv2"] == pytest.approx(0.25)
    assert s.loc["A", "active_weeks"] == 4 and s.loc["A", "nonzero_weeks"] == 2
    assert s.loc["A", "cv"] == pytest.approx(1.0)  # mean 2, sd 2
    assert s.loc["A", "cv_nonzero"] == 0.0 and s.loc["B", "cv_nonzero"] == pytest.approx(0.5)


def test_syntetos_boylan_quadrants():
    adi = pd.Series([1.0, 1.0, 2.0, 2.0, 1.32, np.nan])
    cv2 = pd.Series([0.1, 0.49, 0.1, 1.0, 0.1, 0.1])
    out = syntetos_boylan(adi, cv2, 1.32, 0.49)
    assert out.iloc[:5].tolist() == ["smooth", "erratic", "intermittent", "lumpy", "intermittent"]
    assert pd.isna(out.iloc[5])


def test_customer_concentration_counts_anonymous_in_total():
    sales = pd.DataFrame(
        {
            "stock_code": ["A", "A", "A", "B"],
            "customer_id": pd.array([1, 2, None, None], dtype="Int64"),
            "quantity": [6, 2, 2, 5],
            "invoice_date": pd.to_datetime(["2011-01-03"] * 3 + ["2011-01-04"]),
        }
    )
    c = customer_concentration(sales, "2012-01-01")
    assert c.loc["A", "top_customer"] == 1
    assert c.loc["A", "top_customer_share"] == pytest.approx(0.6)
    assert c.loc["A", "n_customers"] == 2
    assert c.loc["B", "top_customer_share"] == 0.0 and c.loc["B", "n_customers"] == 0
    assert customer_concentration(sales, "2011-01-01").empty


CFG = {
    "before": "2011-01-31",  # weeks 0..3 of W0
    "abc": {"a": 0.8, "b": 0.95},
    "xyz": {"x": 0.5, "y": 1.0},
    "syntetos_boylan": {"adi": 1.32, "cv2": 0.49},
    "focus": {"classes": ["A", "B"], "min_active_weeks": 3},
}


def test_segment_table_focus_and_no_look_ahead():
    p = panel(
        {
            "big": [100, 100, 100, 100, 0, 0],
            "new": [0, 0, 0, 0, 1000, 1000],  # sells only after `before`
            "short": [0, 0, 0, 0],
        }
    )
    # "short" first sells in week 2: 2 active weeks < 3 -> not in focus despite class A/B
    p = pd.concat([p, panel({"late": [0, 0, 50, 50]})], ignore_index=True)
    p = p[~((p["stock_code"].isin(["new", "short"])) & (p["units"] == 0))]
    p = p[~((p["stock_code"] == "late") & (p["week"] < W0 + pd.Timedelta(weeks=2)))]
    sales = pd.DataFrame(
        {
            "stock_code": ["big", "late"],
            "customer_id": pd.array([1, 2], dtype="Int64"),
            "quantity": [400, 100],
            "invoice_date": pd.to_datetime(["2011-01-04", "2011-01-18"]),
        }
    )
    seg = segment_table(p, sales, CFG).set_index("stock_code")
    assert set(seg.index) == {"big", "late"}  # "new" has no demand before the cut
    assert seg.loc["big", "focus"] and not seg.loc["late", "focus"]
    assert seg.loc["late", "active_weeks"] == 2
    assert seg["revenue_share"].sum() == pytest.approx(1.0)


def test_class_table_shares():
    seg = pd.DataFrame(
        {"abc": ["A", "A", "B"], "revenue": [60.0, 30.0, 10.0], "focus": [True, False, True]}
    )
    t = class_table(seg, "abc")
    assert t.loc["A", "products"] == 2 and t.loc["A", "revenue_share"] == pytest.approx(0.9)
    assert t.loc["A", "focus_products"] == 1
    assert t.loc["B", "focus_revenue_share"] == pytest.approx(0.1)


def test_write_focus_keeps_the_config_head(tmp_path):
    spec = importlib.util.spec_from_file_location("segment", REPO_DIR / "scripts" / "segment.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    path = tmp_path / "backtest.yaml"
    path.write_text(f"a: 1  # comment\n{mod.MARKER} ---\nold: stuff\n")
    for _ in range(2):  # idempotent
        mod.write_focus(path, ["00123", "85123A"], {"n": 2})
    text = path.read_text()
    assert text.startswith("a: 1  # comment\n") and "old" not in text
    assert yaml.safe_load(text)["focus_set"]["stock_codes"] == ["00123", "85123A"]


def test_committed_focus_set_matches_config():
    cfg = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    fs = cfg["focus_set"]
    assert fs["n"] == len(fs["stock_codes"]) == len(set(fs["stock_codes"]))
    assert fs["before"] == cfg["segments"]["before"] == cfg["origins"]["test"]["from"]
    assert all(isinstance(c, str) for c in fs["stock_codes"])


def test_without_large_orders_turns_weeks_to_zero():
    p = panel({"A": [10, 2, 3]})
    sales = pd.DataFrame(
        {
            "stock_code": ["A"] * 5,
            "quantity": [2, 2, 100, 2, 3],  # median 2: 100 > 20 x 2 is dropped
            "invoice_date": pd.to_datetime(
                ["2011-01-03", "2011-01-04", "2011-01-05", "2011-01-10", "2011-01-17"]
            ),
            "customer_id": pd.array([1] * 5, dtype="Int64"),
        }
    )
    trimmed, large = without_large_orders(p, sales, "2012-01-01", 20)
    assert trimmed["units"].tolist() == [4.0, 2.0, 3.0]
    assert large["quantity"].tolist() == [100]
    only_big = pd.DataFrame(  # week 0 has only a large order -> zero week
        {
            "stock_code": ["A"] * 4,
            "quantity": [100, 1, 1, 1],
            "invoice_date": pd.to_datetime(
                ["2011-01-03", "2011-01-10", "2011-01-17", "2011-01-18"]
            ),
        }
    )
    trimmed, _ = without_large_orders(p, only_big, "2012-01-01", 20)
    assert trimmed["units"].tolist() == [0.0, 1.0, 2.0]


def test_segment_table_sb_without_large_orders():
    p = panel({"A": [4, 4, 4, 4]})
    sales = pd.DataFrame(
        {
            "stock_code": ["A"] * 5,
            "quantity": [1, 1, 1, 1, 1000],
            "invoice_date": pd.to_datetime(
                ["2011-01-03", "2011-01-10", "2011-01-17", "2011-01-24", "2011-01-25"]
            ),
            "customer_id": pd.array([1] * 5, dtype="Int64"),
        }
    )
    p.loc[3, ["units", "revenue"]] = 1001.0
    cfg = CFG | {"syntetos_boylan": {"adi": 1.32, "cv2": 0.49, "max_order_ratio": 20}}
    seg = segment_table(p, sales, cfg).set_index("stock_code")
    assert seg.loc["A", "sb_class_all"] == "erratic" and seg.loc["A", "sb_class"] == "smooth"
    assert seg.loc["A", "cv2"] == 0.0 and seg.loc["A", "adi"] == 1.0


def test_bulk_lines_and_customer_order_mix():
    sales = pd.DataFrame(
        {
            "stock_code": ["A", "A", "A", "A", "B", "B"],
            "quantity": [1, 1, 50, 2, 3, 3],  # A: median 1.5 -> 50 > 30 is bulk
            "invoice_date": pd.to_datetime(["2011-01-03"] * 5 + ["2011-07-01"]),
            "customer_id": pd.array([1, 2, 2, None, 2, 1], dtype="Int64"),
        }
    )
    bulk = bulk_lines(sales, "2011-06-06", 20)
    assert bulk.tolist() == [False, False, True, False, False]  # last line after `before`
    mix = customer_order_mix(sales, "2011-06-06", 20)
    assert mix.loc[1].tolist()[:4] == [1, 0, 1, 0]
    assert mix.loc[2, "item_lines"] == 2 and mix.loc[2, "bulk_lines"] == 1
    assert mix.loc[2, "bulk_unit_share"] == pytest.approx(50 / 54)
    assert len(mix) == 2  # the line without customer is left out


def test_segment_table_xyz_zero_weeks():
    p = panel({"A": [4, 0, 4, 0], "B": [1, 2, 1, 2]})
    sales = pd.DataFrame(
        {"stock_code": ["A"], "quantity": [8], "invoice_date": pd.to_datetime(["2011-01-03"])}
    ).assign(customer_id=pd.array([1], dtype="Int64"))
    with_zeros = segment_table(p, sales, CFG).set_index("stock_code")
    assert with_zeros.loc["A", "xyz"] == "Y"  # cv 1.0 with the zero weeks
    cfg = CFG | {"xyz": {"x": 0.5, "y": 1.0, "zero_weeks": False}}
    seg = segment_table(p, sales, cfg).set_index("stock_code")
    assert seg.loc["A", "xyz"] == "X" and seg.loc["B", "xyz"] == "X"  # cv 0 and 1/3


def test_segment_table_min_demand_weeks():
    p = panel({"A": [4, 0, 4, 0], "once": [7]})
    sales = pd.DataFrame(
        {"stock_code": ["A"], "quantity": [8], "invoice_date": pd.to_datetime(["2011-01-03"])}
    ).assign(customer_id=pd.array([1], dtype="Int64"))
    assert set(segment_table(p, sales, CFG)["stock_code"]) == {"A", "once"}
    seg = segment_table(p, sales, CFG | {"min_demand_weeks": 2})
    assert seg["stock_code"].tolist() == ["A"] and seg["revenue_share"].sum() == 1.0
