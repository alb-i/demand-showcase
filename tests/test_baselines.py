import numpy as np
import pandas as pd
import pytest
from conftest import W0, panel

from retail.backtest import History, check_forecast, evaluate_origin, wide_units
from retail.compare import compare, summary
from retail.models.baselines import Baseline, point_matrix

Q = [0.1, 0.5, 0.9]


def week(i):
    return W0 + pd.Timedelta(weeks=i)


def test_point_matrix_by_hand():
    u = pd.DataFrame([[1.0, np.nan, 3.0, 5.0, np.nan]], columns=range(5))
    naive = point_matrix(u, "naive", 0, 1).iloc[0].tolist()
    assert naive[1:] == [1.0, 1.0, 3.0, 5.0]  # forecast at origin j = last known before j
    ma2 = point_matrix(u, "ma", 2, 1).iloc[0].tolist()
    assert ma2[1:] == [1.0, 1.0, 3.0, 4.0]  # known weeks among the last 2
    assert np.isnan(naive[0]) and np.isnan(ma2[0])


def test_point_matrix_seasonal_naive():
    u = pd.DataFrame([np.arange(60, dtype=float)], columns=range(60))
    s = point_matrix(u, "snaive", 0, 2)  # target week j+1, 52 weeks earlier: j+1-52
    assert s.iloc[0, 55] == 4.0
    assert s.iloc[0, 10] == 9.0  # no value 52 weeks earlier: naive


def history(series, origin_week, closed=()):
    p = panel(series, closed=closed)
    return p, wide_units(p), History(p, wide_units(p), week(origin_week))


def test_baseline_points_and_monotone_quantiles():
    rng = np.random.default_rng(0)
    series = {f"s{i}": rng.poisson(5, 30).tolist() for i in range(20)}
    _, _, h = history(series, 30)
    skus = pd.Index(sorted(series))
    for method, window in [("naive", 1), ("ma", 4), ("snaive", 1)]:
        fc = Baseline(method, window, min_pool=10).predict(h, skus, [1, 2], Q)
        fc = check_forecast(fc, skus, [1, 2], Q)  # complete, finite, not crossing
        assert (fc.to_numpy() >= 0).all()
    fc = Baseline("naive", min_pool=10).predict(h, skus, [1], Q).set_index("stock_code")
    assert fc.loc["s0", "mean"] == series["s0"][-1]
    fc = Baseline("ma", 4, min_pool=10).predict(h, skus, [1], Q).set_index("stock_code")
    assert fc.loc["s3", "mean"] == pytest.approx(np.mean(series["s3"][-4:]))


def test_baseline_intervals_scale_with_the_series():
    rng = np.random.default_rng(1)
    small = {f"a{i}": rng.poisson(2, 40).tolist() for i in range(10)}
    big = {f"b{i}": (100 * np.array(small[f"a{i}"])).tolist() for i in range(10)}
    _, _, h = history(small | big, 40)
    skus = pd.Index(sorted(small | big))
    seg = pd.Series("A-smooth", index=skus)
    fc = Baseline("naive", segments=seg, min_pool=10).predict(h, skus, [1], Q)
    fc = fc.set_index("stock_code")
    width = fc["q0.9"] - fc["q0.1"]
    assert width["b0"] > 20 * width["a0"]  # same pooled quantiles x 100 x larger scale


def test_baseline_small_pool_falls_back_to_all():
    series = {"x": [1, 2, 1, 2, 1, 2], "y": [5, 0, 5, 0, 5, 0]}
    _, _, h = history(series, 6)
    skus = pd.Index(["x", "y"])
    seg = pd.Series({"x": "A-smooth", "y": "C-lumpy"})
    a = Baseline("naive", segments=seg, min_pool=1000).predict(h, skus, [1], Q)
    b = Baseline("naive", segments=None, min_pool=1000).predict(h, skus, [1], Q)
    pd.testing.assert_frame_equal(a, b)


def test_baseline_has_no_look_ahead():
    rng = np.random.default_rng(2)
    series = {f"s{i}": rng.poisson(4, 20).tolist() for i in range(8)}
    p, wide, _ = history(series, 12)
    p2 = p.copy()
    p2.loc[p2["week"] >= week(12), "units"] *= 50
    skus = pd.Index(sorted(series))
    for method in ["naive", "snaive", "ma"]:
        m = Baseline(method, 4, min_pool=5)
        f1, _ = evaluate_origin(m, p, wide, week(12), skus, [1, 3], Q)
        f2, _ = evaluate_origin(m, p2, wide_units(p2), week(12), skus, [1, 3], Q)
        pd.testing.assert_frame_equal(f1, f2)


def test_unknown_method():
    with pytest.raises(ValueError):
        Baseline("croston")


def rows(mean_offset: float, n_series: int = 30) -> pd.DataFrame:
    rng = np.random.default_rng(3)
    recs = []
    for i in range(n_series):
        for h in (1, 2):
            y = float(rng.poisson(5))
            m = y + mean_offset + rng.normal(0, 0.5)
            recs.append(
                {"stock_code": f"s{i}", "origin": W0, "h": h, "y": y, "mean": m,
                 "q0.1": m - 2, "q0.5": m, "q0.9": m + 2, "scale": 1.0, "scale2": 1.0,
                 "weight": 1.0 + i, "segment": "A-smooth" if i % 2 else "B-lumpy"}
            )  # fmt: skip
    return pd.DataFrame(recs)


def test_summary_and_compare():
    good, bad = rows(0.0), rows(3.0)
    s = summary(good, Q, [0.8])
    assert s.loc["all", "n"] == 60 and s.loc["all", "series"] == 30
    assert set(summary(good, Q, [0.8], by="segment").index) == {"A-smooth", "B-lumpy"}
    res = compare(bad, good, Q, [0.8], n=500)
    assert res["significant"] and res["diff"] > 2
    res_w = compare(bad, good, Q, [0.8], weighted=True, n=500)
    assert res_w["n_series"] == 30


def test_compare_uses_common_rows_only():
    a, b = rows(0.0), rows(0.0).iloc[:10]
    assert compare(a, b, Q, [0.8], n=100)["n_series"] == 5
