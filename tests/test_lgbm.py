import importlib.util

import numpy as np
import pandas as pd
import pytest
import yaml
from conftest import W0, panel

from retail.backtest import History, evaluate_origin, wide_units
from retail.io import REPO_DIR
from retail.models.lgbm import (
    FEATURES,
    GlobalLGBM,
    _abc,
    _sb_class,
    origin_features,
    past,
    target_calendar,
)

Q = [0.1, 0.5, 0.9]
SMALL = {"min_data_in_leaf": 5, "num_leaves": 4, "bagging_fraction": 1.0, "bagging_freq": 0}


def week(i):
    return W0 + pd.Timedelta(weeks=i)


def data(n_products=12, weeks=40, seed=0, closed=(10,)):
    rng = np.random.default_rng(seed)
    series, bulk = {}, {}
    for i in range(n_products):
        item = rng.poisson(2 + i % 4, weeks).astype(float)
        b = np.where(rng.random(weeks) < 0.08, 30.0, 0.0)
        series[f"s{i:02d}"], bulk[f"s{i:02d}"] = (item + b).tolist(), b
    p = panel(series, closed=closed)
    bdf = pd.DataFrame([(c, week(k), v) for c, vals in bulk.items() for k, v in enumerate(vals)],
                       columns=["stock_code", "week", "units_bulk"])  # fmt: skip
    p = p.merge(bdf, on=["stock_code", "week"], how="left")
    p.loc[p["closed"], "units_bulk"] = np.nan
    p["units_bulk"] = p["units_bulk"].fillna(0.0)
    p["median_price"] = np.where(p["units"] > 0, 1.0 + 0.1 * (p["week"] > week(20)), np.nan)
    return p


def model(**kw):
    return GlobalLGBM(params=SMALL, rounds=20, oos_weeks=6, min_pool=5, **kw)


def test_past_uses_only_earlier_columns():
    m = np.array([[1.0, 2.0, np.nan, 4.0, 5.0]])
    assert np.isnan(past(m, 2, "mean")[0, 0])
    assert past(m, 2, "mean")[0].tolist()[1:] == [1.0, 1.5, 2.0, 4.0]  # NaN skipped
    assert past(m, None, "sum")[0].tolist()[1:] == [1.0, 3.0, 3.0, 7.0]


def test_origin_features_lags_scale_and_bulk():
    y = np.array([[np.nan, 2.0, 4.0, 0.0, 6.0, np.nan]])  # last column = the origin
    units = y + np.array([[np.nan, 0.0, 10.0, 0.0, 0.0, np.nan]])
    bulk = units - y
    f = origin_features(y, units, bulk, None, None, np.array([3]), scale_weeks=2)
    assert f["started"][0].tolist() == [False, False, True, True, True, True]
    assert f["scale"][0, 5] == pytest.approx(3.0)  # mean of 0 and 6
    assert f["scale"][0, 4] == pytest.approx(2.0)  # mean of 4 and 0
    assert f["lag1"][0, 5] == pytest.approx(6 / 3) and f["lag2"][0, 5] == 0.0
    assert f["lag52"][0, 5] != f["lag52"][0, 5]  # NaN
    assert f["age"][0, 5] == 4 and f["known"][0, 5] == 4
    assert f["since_bulk"][0, 5] == 3 and f["bulk_weeks52"][0, 5] == 1
    assert f["bulk_share52"][0, 5] == pytest.approx(10 / 22)
    assert f["category"][0, 0] == 3
    # all-zero history: scale 1
    z = origin_features(np.array([[0.0, 0.0, np.nan]]), np.zeros((1, 3)), np.zeros((1, 3)),
                        None, None, np.array([0]))  # fmt: skip
    assert z["scale"][0, 2] == 1.0


def test_abc_and_sb_class():
    rev = np.array([[80.0], [15.0], [5.0], [0.0]])
    assert _abc(rev)[:, 0].tolist() == [0.0, 1.0, 2.0, 2.0]
    y = np.array([[1.0, 1.0, 1.0, 1.0, np.nan], [0.0, 5.0, 0.0, 1.0, np.nan],
                  [0.0, 0.0, 0.0, 0.0, np.nan]])  # fmt: skip
    adi, cv2, code = _sb_class(y)
    assert adi[0, 4] == 1.0 and cv2[0, 4] == 0.0 and code[0, 4] == 0  # smooth
    assert adi[1, 4] == 2.0 and cv2[1, 4] == pytest.approx(4 / 9) and code[1, 4] == 2
    assert np.isnan(code[2, 4])


def test_target_calendar():
    d = pd.DatetimeIndex(["2011-12-19", "2011-12-26", "2011-01-03"])
    woy, xmas = target_calendar(d)
    assert woy.tolist() == [51, 52, 1]
    assert xmas.tolist() == [0, 52, 50]


def test_train_cells_respect_the_cutoff():
    p = data()
    h = History(p, wide_units(p), week(30))
    m = model()
    d = m._prepare(h, [1, 3])
    for hh in (1, 3):
        i, j = m.train_cells(d, hh, 20)
        assert (j + hh - 1 <= 19).all() and np.isfinite(d["y"][i, j + hh - 1]).all()
        assert d["feats"]["started"][i, j].all()
        assert 10 not in set(j + hh - 1)  # closed week: no target
    x = m.design(d, i, j, 3)
    assert list(x.columns) == list(FEATURES) and (x["h"] == 3).all()


def test_features_do_not_depend_on_later_weeks():
    p = data()
    wide = wide_units(p)
    m = model()
    short = m._prepare(History(p, wide, week(25)), [1])
    long = m._prepare(History(p, wide, week(35)), [1])
    for name in FEATURES:
        if name in ("h", "woy", "to_xmas"):
            continue
        a, b = short["feats"][name], long["feats"][name][:, : short["n"] + 1]
        np.testing.assert_array_equal(a, b, err_msg=name)


def test_predict_no_look_ahead_and_valid_output():
    p = data()
    skus = pd.Index(sorted(p["stock_code"].unique()))
    m = model(segments=pd.Series("x", index=skus))
    f1, _ = evaluate_origin(m, p, wide_units(p), week(30), skus, [1, 4], Q)
    p2 = p.copy()
    late = p2["week"] >= week(30)
    p2.loc[late, ["units", "units_bulk"]] *= 50
    f2, _ = evaluate_origin(m, p2, wide_units(p2), week(30), skus, [1, 4], Q)
    pd.testing.assert_frame_equal(f1, f2)  # also: deterministic
    assert (f1["mean"] >= 0).all() and (f1["q0.1"] <= f1["q0.9"]).all()
    assert m.last_importance is not None and set(m.last_importance.index) == set(FEATURES)
    assert m.name == "lgbm-item-bulk-ma52" and "out-of-sample" in m.description


def test_item_adds_bulk_and_total_has_none():
    p = data()
    h = History(p, wide_units(p), week(30))
    item, total = model(), model(target="total", tag="-x")
    assert total.bulk is None and total.name == "lgbm-total-x"
    d = item._prepare(h, [1])
    j = np.full(1, d["n"])
    no_model = item.point(None, d, np.array([0]), j, 1)  # booster None: bulk part only
    r = h.rows.query("stock_code == 's00' and not closed")
    bulk_hist = r["units_bulk"].tail(52)  # the MA skips the closed week
    assert no_model[0] == pytest.approx(bulk_hist.mean())
    with pytest.raises(ValueError):
        GlobalLGBM(target="both")


def test_lgbm_configs_load():
    spec = importlib.util.spec_from_file_location("bt", REPO_DIR / "scripts" / "backtest.py")
    bt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bt)
    seg, cats = pd.Series({"a": "A-smooth"}), pd.Series({"a": "bags"})
    names = set()
    for path in sorted((REPO_DIR / "configs" / "models").glob("lgbm*.yaml")):
        m = bt.load_model(yaml.safe_load(path.read_text()), seg, cats)
        assert isinstance(m, GlobalLGBM) and m.categories is cats
        names.add(m.name)
    assert {"lgbm-item-bulk-ma52", "lgbm-total", "lgbm-item-bulk-ma52-p1.2"} <= names
    assert {"lgbm-total-p1.8", "lgbm-total-q-p1.8"} <= names and len(names) == 8


def test_quantile_models():
    p = data()
    skus = pd.Index(sorted(p["stock_code"].unique()))
    taus = [0.1, 0.5, 0.9]
    m = model(target="total", quantile_models=True)
    assert m.name == "lgbm-total-q" and "pinball" in m.description
    f1, rows = evaluate_origin(m, p, wide_units(p), week(30), skus, [1, 4], taus)
    q = f1[["q0.1", "q0.5", "q0.9"]].to_numpy()
    assert (np.diff(q, axis=1) >= 0).all() and (q >= 0).all()
    assert (f1["q0.9"] > f1["q0.1"]).mean() > 0.5  # real spread, not a point mass
    point = model(target="total")
    f2, _ = evaluate_origin(point, p, wide_units(p), week(30), skus, [1, 4], taus)
    np.testing.assert_allclose(f1["mean"], f2["mean"])  # same Tweedie mean
    p2 = p.copy()
    p2.loc[p2["week"] >= week(30), ["units", "units_bulk"]] *= 50
    f3, _ = evaluate_origin(m, p2, wide_units(p2), week(30), skus, [1, 4], taus)
    pd.testing.assert_frame_equal(f1, f3)  # no look-ahead
    with pytest.raises(ValueError):
        GlobalLGBM(target="item", quantile_models=True)


def test_quantile_table():
    spec = importlib.util.spec_from_file_location("cr", REPO_DIR / "scripts" / "compare_runs.py")
    cr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cr)
    rows = pd.DataFrame({"stock_code": ["a", "b"], "origin": [week(5)] * 2, "h": [1, 1],
                         "y": [2.0, 4.0], "mean": [1.0, 4.0], "scale": [1.0, 2.0],
                         "scale2": [1.0, 4.0], "weight": [1.0, 1.0], "q0.1": [0.0, 3.0],
                         "q0.5": [1.0, 4.0], "q0.9": [2.0, 5.0]})  # fmt: skip
    t = cr.quantile_table([("r", rows, {})], Q, [0.8])
    assert t.loc[0.1, ("r", "hit")] == 0.0 and t.loc[0.5, ("r", "hit")] == 0.5
    assert t.loc[0.9, ("r", "hit")] == 1.0
    # pinball at 0.5: a: 0.5 * |2 - 1| / 1 = 0.5; b: 0 -> mean 0.25
    assert t.loc[0.5, ("r", "pinball")] == pytest.approx(0.25)
    assert any("share of y <= q" in line for line in cr.by_quantile([("r", rows, {})], Q, [0.8]))
