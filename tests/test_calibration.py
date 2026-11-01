import numpy as np
import pandas as pd
import pytest

from retail.calibration import (
    apply_offsets,
    calibrate,
    conformal_quantile,
    offsets,
    target_week,
)
from retail.metrics import pit_hits, row_errors

Q = [0.1, 0.5, 0.9]
O0 = pd.Timestamp("2011-01-03")


def test_pit_hits_without_and_with_ties():
    q = np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [0.0, 0.0, 4.0], [0.0, 0.0, 0.0]])
    y = np.array([2.5, 0.0, 0.0, 0.0])
    h = pit_hits(y, q, Q)
    assert h[0].tolist() == [0.0, 0.0, 1.0]  # = y <= q
    assert h[1].tolist() == [1.0, 1.0, 1.0]
    # tie at 0 for 0.1 and 0.5: U uniform on [0, (0.5 + 0.9) / 2 = 0.7]
    assert h[2] == pytest.approx([0.1 / 0.7, 0.5 / 0.7, 1.0])
    assert h[3] == pytest.approx([0.1 / 0.95, 0.5 / 0.95, 0.9 / 0.95])  # hi = (0.9 + 1) / 2
    r = pd.DataFrame({"y": y, "mean": 1.0, "scale": 1.0, "scale2": 1.0,
                      "q0.1": q[:, 0], "q0.5": q[:, 1], "q0.9": q[:, 2]})  # fmt: skip
    e = row_errors(r, Q, [0.8])
    assert e["rcover_0.8"].tolist() == pytest.approx([1.0, 0.0, 1 - 0.1 / 0.7, 0.8 / 0.95])
    assert e["cover_0.8"].tolist() == [1.0, 0.0, 1.0, 1.0]


def test_conformal_quantile():
    s = np.arange(1.0, 10.0)  # 9 scores
    assert conformal_quantile(s, 0.5) == 5.0  # ceil(10 * 0.5) = 5th
    assert conformal_quantile(s, 0.9) == 9.0 and conformal_quantile(s, 0.01) == 1.0
    assert conformal_quantile(np.array([np.nan]), 0.5) == 0.0


def rows_for(origins, n=60, bias=0.0, seed=0):
    """Rows of a forecast whose quantiles are the N(0, 1) ones shifted by -bias (too low)."""
    rng = np.random.default_rng(seed)
    z = {0.1: -1.2816, 0.5: 0.0, 0.9: 1.2816}
    out = []
    for o in origins:
        for h in (1, 2):
            y = rng.normal(10, 1, n)
            df = pd.DataFrame({"stock_code": [f"s{i}" for i in range(n)], "origin": o, "h": h,
                               "y": y, "scale": 1.0})  # fmt: skip
            for t in Q:
                df[f"q{t:g}"] = 10 + z[t] - bias
            out.append(df)
    return pd.concat(out, ignore_index=True)


def test_offsets_pool_fallback_and_apply():
    cal = rows_for([O0], n=30).assign(label=lambda d: np.where(d.index % 2, "a", "b"))
    off = offsets(cal, Q, min_pool=20)
    assert ("*", 1) in off.index
    big = offsets(cal, Q, min_pool=1)
    small = offsets(cal, Q, min_pool=100)  # labels too small: the overall pool
    assert small.loc[("a", 1)].tolist() == small.loc[("*", 1)].tolist()
    assert big.loc[("a", 1)].tolist() != big.loc[("*", 1)].tolist()
    r = pd.DataFrame({"label": ["zz"], "h": [1], "scale": [2.0], "q0.1": [5.0], "q0.5": [5.0],
                      "q0.9": [1.0]})  # fmt: skip
    out = apply_offsets(r, big, Q)  # unknown label: the overall offsets; sorted
    expect = np.sort(np.clip(np.array([5.0, 5.0, 1.0]) + 2 * big.loc[("*", 1)].to_numpy(), 0, None))
    assert out[["q0.1", "q0.5", "q0.9"]].to_numpy()[0] == pytest.approx(expect)


def test_calibrate_fixes_a_biased_forecast_without_look_ahead():
    origins = list(pd.date_range(O0, periods=12, freq="W-MON"))
    rows = rows_for(origins, bias=1.0)
    cal, info = calibrate(rows, Q, window_weeks=13, min_pool=10)
    first = cal["origin"] == origins[0]
    pd.testing.assert_frame_equal(cal[first], rows[first])  # nothing known yet
    assert info["n_cal"].iloc[0] == 0 and info["n_cal"].iloc[1] == 60  # only h = 1 known
    late = cal["origin"] >= origins[4]
    before = (rows.loc[late, "y"] <= rows.loc[late, "q0.5"]).mean()
    after = (cal.loc[late, "y"] <= cal.loc[late, "q0.5"]).mean()
    assert before < 0.25 and abs(after - 0.5) < 0.1  # quantiles too low -> few hits
    # no look-ahead: actuals of target weeks >= the origin do not matter
    t = origins[6]
    changed = rows.copy()
    changed.loc[target_week(changed) >= t, "y"] += 100
    cal2, _ = calibrate(changed, Q, window_weeks=13, min_pool=10)
    at = cal["origin"] == t
    pd.testing.assert_frame_equal(cal.loc[at, ["q0.1", "q0.5", "q0.9"]],
                                  cal2.loc[at, ["q0.1", "q0.5", "q0.9"]])  # fmt: skip


def test_calibrate_forecasts_take_the_scale_from_the_rows():
    origins = list(pd.date_range(O0, periods=4, freq="W-MON"))
    rows = rows_for(origins, bias=1.0)
    fc = rows.drop(columns=["y", "scale"])
    cal_fc, _ = calibrate(rows, Q, window_weeks=13, min_pool=10, targets=fc)
    cal_rows, _ = calibrate(rows, Q, window_weeks=13, min_pool=10)
    assert "scale" not in cal_fc and list(cal_fc.columns) == list(fc.columns)
    np.testing.assert_allclose(cal_fc["q0.5"], cal_rows["q0.5"])
    labels = pd.Series("x", index=[f"s{i}" for i in range(60)])
    by_label, _ = calibrate(rows, Q, labels, window_weeks=13, min_pool=10)
    np.testing.assert_allclose(by_label["q0.5"], cal_rows["q0.5"])  # one label = one pool
