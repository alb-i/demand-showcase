"""Cost model, policies and simulator on small hand-computed scenarios (constant demand, a
single spike, zero demand)."""

import numpy as np
import pandas as pd
import pytest

from retail.inventory.costs import Costs, critical_ratio, load_costs, unit_economics, unit_prices
from retail.inventory.policies import (
    last_mean,
    ma_errors,
    naive_levels,
    normal_levels,
    quantile_levels,
)
from retail.inventory.simulate import kpis, simulate, totals

W = pd.date_range("2011-06-06", periods=5, freq="W-MON")


def frame(rows: dict, weeks=W) -> pd.DataFrame:
    return pd.DataFrame(rows, index=list(weeks)).T.rename_axis("stock_code")


def run(d, s, lead=1, review=1, lost=True):
    sim = simulate(frame({"a": d}, W[: len(d)]), frame({"a": s}, W[: len(s)]), lead, review, lost)
    return sim.set_index("week")


def test_constant_demand_steady_state():
    sim = run([10] * 5, [20] * 5)
    assert sim["order"].tolist() == [0, 10, 10, 10, 10]
    assert sim["arrival"].tolist() == [0, 0, 10, 10, 10]
    assert sim["on_hand_end"].tolist() == [10, 0, 0, 0, 0]
    assert sim["avg_on_hand"].tolist() == [15, 5, 5, 5, 5]
    assert sim["short"].sum() == 0


def test_single_spike_lost_sales():
    sim = run([0, 0, 30, 0, 0], [20] * 5)
    assert sim["served"].tolist() == [0, 0, 20, 0, 0]
    assert sim["short"].tolist() == [0, 0, 10, 0, 0]
    assert sim["order"].tolist() == [0, 0, 0, 20, 0]  # position 0 in week 3, arrives week 4
    assert sim["on_hand_end"].tolist() == [20, 20, 0, 0, 20]


def test_single_spike_backorders():
    sim = run([0, 0, 30, 0, 0], [20] * 5, lost=False)
    assert sim["served"].tolist() == [0, 0, 20, 0, 0]  # served in the week of the demand
    assert sim["on_hand_end"].tolist() == [20, 20, -10, -10, 20]
    assert sim["order"].tolist() == [0, 0, 0, 30, 0]
    assert sim["avg_on_hand"].iloc[2] == 10  # (20 + max(-10, 0)) / 2


def test_zero_demand_keeps_the_start_stock():
    sim = run([0] * 5, [8] * 5)
    assert (sim["on_hand_end"] == 8).all() and (sim["order"] == 0).all()


def test_lead_time_zero_and_review_period_two():
    sim = run([10] * 5, [10] * 5, lead=0)
    assert sim["short"].sum() == 0 and sim["order"].tolist() == [0, 10, 10, 10, 10]
    sim = run([10] * 5, [30] * 5, lead=1, review=2)
    assert sim["order"].tolist() == [0, 0, 20, 0, 20]  # reviews in weeks 0, 2, 4
    assert sim["short"].tolist() == [0, 0, 0, 0, 0]


def test_level_nan_means_no_order():
    sim = run([10] * 3, [10, np.nan, 10])
    assert sim["order"].tolist() == [0, 0, 10]


def test_kpis_money_by_hand():
    costs = Costs(margin=0.4, holding_rate=0.26, weeks_per_year=52, write_down_share=0.5)
    econ = unit_economics(pd.Series({"a": 10.0, "b": 10.0}), costs)
    assert econ.loc["a", "unit_cost"] == 6 and econ.loc["a", "lost_margin"] == 4
    assert econ.loc["a", "holding_week"] == pytest.approx(0.03)  # 0.26 x 6 / 52
    d = frame({"a": [0, 0, 30, 0, 0], "b": [0] * 5})
    sim = simulate(d, frame({"a": [20] * 5, "b": [8] * 5}), 1)
    k = kpis(sim, econ, costs, seasonal=["b"])
    a, b = k.loc["a"], k.loc["b"]
    assert a["fill_rate"] == pytest.approx(2 / 3) and a["stockout_weeks"] == 1
    assert a["cycle_service"] == pytest.approx(0.8)
    assert a["lost_margin"] == pytest.approx(40)  # 10 units x 4
    # average stock: 20, 20, (20 + 0) / 2, 0, 20 -> 14 units, value 84; 70 unit-weeks x 0.03
    assert a["avg_stock"] == pytest.approx(14) and a["avg_stock_value"] == pytest.approx(84)
    assert a["holding_cost"] == pytest.approx(2.1)
    assert a["write_down"] == 0 and np.isnan(b["fill_rate"])
    assert b["write_down"] == pytest.approx(0.5 * 8 * 6)  # seasonal leftover
    assert b["total_cost_wd"] == pytest.approx(b["total_cost"] + 24)
    t = totals(k)
    assert t["fill_rate"] == pytest.approx(2 / 3) and t["lost_margin"] == pytest.approx(40)
    assert t["avg_stock_value"] == pytest.approx(84 + 48)


def test_critical_ratio_and_config():
    costs, cfg = load_costs()
    assert critical_ratio(costs) == pytest.approx(0.4 / (0.4 + 0.25 * 0.6 / 52))
    assert critical_ratio(costs) > 0.99  # around 0.99
    assert costs.horizon == 2 and costs.write_down_categories
    assert set(cfg["policies"]) == {"naive", "normal", "quantile"}


def test_unit_prices_only_before():
    panel = pd.DataFrame({
        "stock_code": ["a"] * 4, "week": list(W[:4]), "units": [1, 0, 1, 1],
        "median_price": [2.0, 9.0, 4.0, 100.0],
    })  # fmt: skip
    assert unit_prices(panel, W[3])["a"] == 3.0  # weeks with sales before W[3]: 2, 4


def test_last_mean_and_ma_errors():
    v = np.array([[1, 2, np.nan, 3, 4, 5, 6.0], [np.nan] * 7])
    np.testing.assert_allclose(last_mean(v, 2), [5.5, np.nan])
    # window 2 on 1..6: means 1.5 .. 4.5, every error 1.5
    np.testing.assert_allclose(ma_errors(v, 2, 52), [1.5, np.nan])
    np.testing.assert_allclose(ma_errors(v, 2, 1), [1.5, np.nan])


def test_naive_and_normal_levels_without_look_ahead():
    wide = frame({"a": [4, 8, 12, 16, 20]})
    s = naive_levels(wide, W[2:], k=2, buffer=0.5, window=2)
    assert s.loc["a", W[2]] == 2 * 6 * 1.5 and s.loc["a", W[4]] == 2 * 14 * 1.5
    later = wide.copy()
    later.loc["a", W[3]] = 1000
    assert naive_levels(later, [W[3]], 2, 0.5, 2).loc["a", W[3]] == s.loc["a", W[3]]
    n = normal_levels(wide, [W[4]], k=2, alpha=0.5, window=2)
    assert n.loc["a", W[4]] == pytest.approx(2 * 14)  # z_0.5 = 0
    hi = normal_levels(wide, [W[4]], k=2, alpha=0.95, window=2)
    assert hi.loc["a", W[4]] == pytest.approx(28 + 1.6449 * 6 * np.sqrt(2), rel=1e-4)


def test_quantile_levels_from_path_rows():
    rows = pd.DataFrame({"stock_code": ["a", "a", "b"], "origin": [W[0], W[1], W[0]],
                         "h": 2, "q0.9": [5.0, 6.0, 7.0]})  # fmt: skip
    s = quantile_levels(rows, ["a", "b", "c"], W[:2], k=2, tau=0.9)
    assert s.loc["a", W[1]] == 6 and s.loc["b", W[0]] == 7
    assert np.isnan(s.loc["b", W[1]]) and s.loc["c"].isna().all()


def test_match_and_interpolate_frontier():
    from retail.inventory.frontier import at_fill_rate, match

    g = pd.DataFrame({"value": [0.5, 0.8, 0.9], "fill_rate": [0.6, 0.8, 0.9],
                      "avg_stock_value": [10.0, 20.0, 40.0]})  # fmt: skip
    assert match(g, 0.7)["value"] == 0.8 and match(g, 0.8)["value"] == 0.8
    assert match(g, 0.95) is None
    assert at_fill_rate(g, 0.85, "avg_stock_value") == pytest.approx(30)
    assert np.isnan(at_fill_rate(g, 0.95, "avg_stock_value"))


def test_bootstrap_totals_paired():
    from retail.inventory.frontier import bootstrap_totals

    rng = np.random.default_rng(1)
    idx = [f"p{i}" for i in range(200)]
    dem = pd.Series(rng.integers(10, 100, 200).astype(float), index=idx)
    a = pd.DataFrame({"demand": dem, "served": dem * 0.9, "avg_stock_value": 100.0,
                      "total_cost": 50.0})  # fmt: skip
    b = a.assign(served=dem * 0.9, avg_stock_value=a["avg_stock_value"] + rng.normal(5, 1, 200))
    r = bootstrap_totals(a, b, n=500)
    assert r["fill_rate"]["diff"] == pytest.approx(0) and not r["fill_rate"]["significant"]
    s = r["avg_stock_value"]
    assert s["diff"] < 0 and s["significant"] and s["lo"] < s["diff"] < s["hi"]
    assert s["diff"] == pytest.approx(-(b["avg_stock_value"] - 100).sum())
