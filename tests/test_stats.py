import numpy as np
import pandas as pd
import pytest
import yaml
from conftest import W0, panel
from scipy.stats import norm

from retail.backtest import History, evaluate_origin, wide_units
from retail.io import REPO_DIR
from retail.models.stats import StatsModel, guard_explosive, mixture_quantiles

Q = [0.05, 0.25, 0.5, 0.75, 0.95]
NAN = np.nan


def week(i):
    return W0 + pd.Timedelta(weeks=i)


def test_mixture_without_bulk_is_normal():
    mu, sigma = np.array([[10.0, 12.0]]), np.array([[2.0, 3.0]])
    q = mixture_quantiles(mu, sigma, np.array([[NAN, NAN]]), Q)
    assert q[0, 1] == pytest.approx(norm.ppf(Q, 12, 3))
    q0 = mixture_quantiles(mu, sigma, np.array([[0.0, 0.0]]), Q)  # only zeros: same
    assert q0 == pytest.approx(q)


def test_mixture_with_bulk_matches_monte_carlo():
    mu, sigma = np.array([[5.0]]), np.array([[1.5]])
    bulk = np.array([[0.0, 0.0, 0.0, 40.0, NAN]])  # 25 % chance of a 40-unit bulk week
    taus = [0.05, 0.25, 0.5, 0.7, 0.9, 0.95]  # not 0.75: the gap between the modes
    q = mixture_quantiles(mu, sigma, bulk, taus)[0, 0]
    rng = np.random.default_rng(0)
    draws = rng.normal(5, 1.5, 400_000) + rng.choice([0.0, 0.0, 0.0, 40.0], 400_000)
    assert q == pytest.approx(np.quantile(draws, taus), abs=0.05)
    assert q[-1] > 40 and q[0] < 5  # the bulk week shows up in the upper tail only
    shifted = mixture_quantiles(mu, sigma, np.array([[7.0, 7.0]]), Q)[0, 0]
    assert shifted == pytest.approx(norm.ppf(Q, 12, 1.5), abs=1e-6)  # constant bulk: shift


def bulk_panel(series: dict, bulk: dict, closed=()) -> pd.DataFrame:
    p = panel(series, closed=closed)
    b = [(c, week(i), float(v)) for c, vals in bulk.items() for i, v in enumerate(vals)]
    b = pd.DataFrame(b, columns=["stock_code", "week", "units_bulk"])
    p = p.merge(b, on=["stock_code", "week"], how="left")
    return p.assign(units_bulk=p["units_bulk"].fillna(0.0))


def test_constant_item_series_and_bulk_mean():
    series = {"x": [5, 5, 45, 5, 5, 5, 5, 5, 5, 5, 5, 5]}
    bulk = {"x": [0, 0, 40, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
    p = bulk_panel(series, bulk)
    h = History(p, wide_units(p), week(12))
    fc = StatsModel("ets", bulk_weeks=52).predict(h, pd.Index(["x"]), [1, 3], Q)
    assert fc["mean"].tolist() == pytest.approx([5 + 40 / 12] * 2, rel=1e-3)
    no_bulk = StatsModel("ets", bulk_weeks=0).predict(h, pd.Index(["x"]), [1], Q)
    assert 5 <= no_bulk["mean"].iloc[0] < 5 + 40 / 12  # total demand, the spike smoothed away
    assert StatsModel("ets", 0).name == "ets" and StatsModel("arima").name == "arima-bulk-ma52"


def test_closed_weeks_are_not_steps():
    m = StatsModel("ets", 0)
    a = pd.DataFrame([[NAN, 3, 4, NAN, 6, 5, 7, 6, 8]], index=["x"], dtype=float)
    b = pd.DataFrame([[3, 4, 6, 5, 7, 6, 8]], index=["x"], dtype=float)
    mu_a, s_a = m.item_forecast(a, 2)
    mu_b, s_b = m.item_forecast(b, 2)
    assert mu_a == pytest.approx(mu_b) and s_a == pytest.approx(s_b)


@pytest.mark.parametrize("model", ["ets", "arima"])
def test_stats_valid_forecasts_and_no_look_ahead(model):
    rng = np.random.default_rng(1)
    series, bulk = {}, {}
    for i in range(6):
        item = rng.poisson(4, 26)
        b = np.where(rng.random(26) < 0.15, 100, 0)
        series[f"s{i}"], bulk[f"s{i}"] = (item + b).tolist(), b.tolist()
    series["new"], bulk["new"] = [0] * 24 + [3, 2], [0] * 26  # two known weeks only
    p = bulk_panel(series, bulk, closed=(9,))
    p = p[~((p["stock_code"] == "new") & (p["week"] < week(24)))]
    skus = pd.Index(sorted(series))
    m = StatsModel(model, 52)
    f1, _ = evaluate_origin(m, p, wide_units(p), week(20), skus, [1, 4], Q)  # checked inside
    p2 = p.copy()
    late = p2["week"] >= week(20)
    p2.loc[late, ["units", "units_bulk"]] *= 50
    f2, _ = evaluate_origin(m, p2, wide_units(p2), week(20), skus, [1, 4], Q)
    pd.testing.assert_frame_equal(f1, f2)
    f3, _ = evaluate_origin(m, p, wide_units(p), week(26), skus, [1], Q)
    assert "new" in set(f3["stock_code"]) and (f3[[f"q{t:g}" for t in Q]] >= 0).all().all()


def test_stats_configs_and_errors():
    import importlib.util

    with pytest.raises(ValueError):
        StatsModel("theta")
    spec = importlib.util.spec_from_file_location("bt", REPO_DIR / "scripts" / "backtest.py")
    bt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bt)
    for name in ("ets", "arima"):
        cfg = yaml.safe_load((REPO_DIR / "configs" / "models" / f"{name}.yaml").read_text())
        model = bt.load_model(cfg, pd.Series(dtype=str))
        assert isinstance(model, StatsModel) and model.name == f"{name}-bulk-ma52"


def test_guard_explosive_fits():
    known = np.array([[2.0, 4.0, NAN, 6.0], [1.0, 1.0, 1.0, 1.0], [NAN, NAN, NAN, NAN]])
    mu = np.array([[5.0, 5.0], [1.0, 1.0], [NAN, NAN]])
    sigma = np.array([[np.inf, 2.0], [0.5, 0.6], [NAN, NAN]])
    m, s = guard_explosive(mu, sigma, known)
    assert m[0] == pytest.approx([4.0, 4.0]) and s[0] == pytest.approx(
        np.std([2, 4, 6]) * np.sqrt([1, 2])
    )
    assert m[1].tolist() == [1.0, 1.0] and s[1].tolist() == [0.5, 0.6]  # sane rows unchanged
    assert m[2].tolist() == [0.0, 0.0] and s[2].tolist() == [0.0, 0.0]  # no forecast
    huge, _ = guard_explosive(np.array([[1e6, 1.0]]), np.array([[1.0, 1.0]]), known[:1])
    assert huge[0] == pytest.approx([4.0, 4.0])  # mean above 100 x (max + 1)
    q = mixture_quantiles(m, s, np.array([[0.0, 40.0], [NAN, NAN], [NAN, NAN]]), [0.1, 0.9])
    assert np.isfinite(q).all()
