import numpy as np
import pandas as pd
import pytest
from conftest import W0, panel

from retail.backtest import History, check_forecast, evaluate_origin, wide_units
from retail.compare import select_sb
from retail.models.croston import Intermittent, intermittent_matrix

Q = [0.1, 0.5, 0.9]
NAN = np.nan


def week(i):
    return W0 + pd.Timedelta(weeks=i)


def row(values) -> pd.DataFrame:
    return pd.DataFrame([values], columns=range(len(values)), dtype=float)


def test_croston_by_hand():
    # demands 4 (interval 1), 6 (interval 2), 2 (interval 3); alpha 0.5
    f = intermittent_matrix(row([4, 0, 6, 0, 0, 2, 0]), "croston", 0.5).iloc[0].tolist()
    assert np.isnan(f[0])  # nothing known yet
    assert f[1] == f[2] == 4.0  # z = 4, p = 1
    z, p = 5.0, 1.5  # after the 6: z = 4 + 0.5 (6 - 4), p = 1 + 0.5 (2 - 1)
    assert f[3] == f[4] == f[5] == pytest.approx(z / p)
    z, p = 3.5, 2.25  # after the 2: z = 5 + 0.5 (2 - 5), p = 1.5 + 0.5 (3 - 1.5)
    assert f[6] == pytest.approx(z / p)


def test_sba_is_croston_times_correction():
    u = row([0, 3, 0, 0, 5, 1, 0, 0, 0, 4])
    c = intermittent_matrix(u, "croston", 0.2)
    s = intermittent_matrix(u, "sba", 0.2)
    pd.testing.assert_frame_equal(s, c * 0.9)


def test_tsb_by_hand_decays_without_sales():
    f = intermittent_matrix(row([4, 0, 0, 8]), "tsb", 0.5, 0.5).iloc[0].tolist()
    assert f[1] == 4.0  # p = 1, z = 4
    assert f[2] == pytest.approx(0.5 * 4)  # no sale: p = 0.5
    assert f[3] == pytest.approx(0.25 * 4)
    g = intermittent_matrix(row([4, 0, 0, 8, 0]), "tsb", 0.5, 0.5).iloc[0].tolist()
    assert g[4] == pytest.approx((0.25 + 0.5 * 0.75) * (4 + 0.5 * 4))  # p 0.625, z 6


def test_closed_weeks_and_weeks_before_launch_are_skipped():
    with_gaps = row([NAN, NAN, 4, 0, NAN, 6, 0])
    without = row([4, 0, 6, 0])
    for method in ("croston", "sba", "tsb"):
        a = intermittent_matrix(with_gaps, method, 0.3).iloc[0].to_numpy()
        b = intermittent_matrix(without, method, 0.3).iloc[0].to_numpy()
        assert np.isnan(a[:3]).all()  # 0 is filled in by predict
        assert a[3] == b[1] and a[4] == a[5] == b[2] and a[6] == b[3]


def test_unknown_method():
    with pytest.raises(ValueError):
        intermittent_matrix(row([1.0]), "ses", 0.1)
    with pytest.raises(ValueError):
        Intermittent("ma")


def history(series, origin_week):
    p = panel(series)
    return p, wide_units(p), History(p, wide_units(p), week(origin_week))


def test_predict_flat_point_and_valid_quantiles():
    rng = np.random.default_rng(0)
    series = {f"s{i}": (rng.poisson(3, 40) * (rng.random(40) < 0.3)).tolist() for i in range(20)}
    _, _, h = history(series, 40)
    skus = pd.Index(sorted(series))
    for method in ("croston", "sba", "tsb"):
        m = Intermittent(method, 0.1, min_pool=10)
        fc = m.predict(h, skus, [1, 2, 4], Q)
        checked = check_forecast(fc, skus, [1, 2, 4], Q)
        assert (checked.to_numpy() >= 0).all()
        means = fc.pivot(index="stock_code", columns="h", values="mean")
        assert (means.nunique(axis=1) == 1).all()  # same point forecast for every horizon
        known = h.units.loc[skus]
        known = known.assign(origin=np.nan)  # one more column: the forecast after all weeks
        expected = intermittent_matrix(known, method, 0.1).iloc[:, -1].fillna(0.0)
        h1 = fc[fc["h"] == 1].set_index("stock_code")["mean"]
        pd.testing.assert_series_equal(h1, expected, check_names=False)
    assert Intermittent("tsb", 0.2, 0.1).name == "tsb-a0.2-b0.1"
    assert Intermittent("sba", 0.1).name == "sba-a0.1"


def test_intermittent_has_no_look_ahead():
    rng = np.random.default_rng(2)
    series = {f"s{i}": (rng.poisson(4, 24) * (rng.random(24) < 0.4)).tolist() for i in range(8)}
    p, wide, _ = history(series, 14)
    p2 = p.copy()
    p2.loc[p2["week"] >= week(14), "units"] *= 50
    skus = pd.Index(sorted(series))
    for method in ("croston", "sba", "tsb"):
        m = Intermittent(method, 0.2, min_pool=5)
        f1, _ = evaluate_origin(m, p, wide, week(14), skus, [1, 3], Q)
        f2, _ = evaluate_origin(m, p2, wide_units(p2), week(14), skus, [1, 3], Q)
        pd.testing.assert_frame_equal(f1, f2)


def test_select_sb():
    rows = pd.DataFrame({"segment": ["A-lumpy", "B-smooth", "C-intermittent", "unclassified"]})
    assert select_sb(rows, ["lumpy", "intermittent"])["segment"].tolist() == [
        "A-lumpy",
        "C-intermittent",
    ]


def script(name):
    import importlib.util

    from retail.io import REPO_DIR

    spec = importlib.util.spec_from_file_location(name, REPO_DIR / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_e2_configs_load_and_label():
    import yaml

    from retail.io import REPO_DIR

    bt = script("backtest")
    seg = pd.Series({"x": "A-lumpy"})
    names = set()
    for m in ("croston", "sba", "tsb"):
        for a in ("01", "02"):
            cfg = yaml.safe_load((REPO_DIR / "configs" / "models" / f"{m}_a{a}.yaml").read_text())
            model = bt.load_model(cfg, seg)
            assert isinstance(model, Intermittent) and model.segments is seg
            names.add(model.name)
    assert len(names) == 6
    label = script("compare_runs").model_label
    assert label({"model_name": "ma4", "model": {"name": "baseline", "method": "ma"}}) == "ma4"
    assert label({"model": {"name": "baseline", "method": "ma"}}) == "ma"  # runs before E1 fix
