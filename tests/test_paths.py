import numpy as np
import pandas as pd
import pytest

from retail.paths import (
    horizon_sums,
    knots,
    overstatement,
    pit,
    pit_vectors,
    quantile_fn,
    ranks,
    sample_sums,
)

Q = [0.025, 0.05, 0.1, 0.2, 0.5, 0.8, 0.9, 0.95, 0.975, 0.99]
Z = np.array([-1.96, -1.645, -1.2816, -0.8416, 0.0, 0.8416, 1.2816, 1.645, 1.96, 2.3263])
O0 = pd.Timestamp("2011-01-03")


def test_knots_and_quantile_fn():
    t, v = knots(np.array([[0.0, 1, 2, 3, 4, 5, 6, 7, 8, 9.5]]), Q)
    assert t[0] == 0 and t[-1] == 1 and len(t) == 12
    assert v[0, 0] == 0 and v[0, -1] == pytest.approx(9.5 + 1.5 / 0.015 * 0.01)
    u = np.array([[0.025, 0.35, 0.99, 1.0]])
    assert quantile_fn(t, v, u)[0] == pytest.approx([0.0, 3.5, 9.5, v[0, -1]])  # 3 + 0.15 / 0.3


def test_pit_inverts_and_randomises_ties():
    rng = np.random.default_rng(0)
    q = np.tile([0.0, 0.0, 0.0, 1, 2, 3, 4, 5, 6, 7], (3, 1)).astype(float)
    t, v = knots(q, Q)
    u = pit(np.array([2.5, 0.0, 100.0]), t, v, rng)
    assert u[0] == pytest.approx(0.65)  # halfway between q0.5 = 2 and q0.8 = 3
    assert 0.0 <= u[1] <= 0.1  # y = 0 equals the knots at 0, 0.025, 0.05, 0.1
    assert u[2] == 1.0
    many = pit(np.zeros(2000), *knots(np.tile(q[0], (2000, 1)), Q), rng)
    assert many.mean() == pytest.approx(0.05, abs=0.005)  # uniform on [0, 0.1]
    # round trip: Q(F(y)) = y away from ties
    y = np.array([0.5, 4.2, 6.9])
    tt, vv = knots(q, Q)
    assert quantile_fn(tt, vv, pit(y, tt, vv, rng)[:, None])[:, 0] == pytest.approx(y)


def test_ranks_uniform():
    u = np.array([[0.2, 0.0], [0.9, 0.0], [0.5, 0.0], [0.1, 0.0]])
    r = ranks(u, np.random.default_rng(0))
    assert r[:, 0].tolist() == [0.375, 0.875, 0.625, 0.125]
    assert sorted(r[:, 1]) == [0.125, 0.375, 0.625, 0.875]  # ties broken at random


def normal_curve(m, mu=10.0, sd=1.0):
    return knots(np.tile(mu + sd * Z, (m, 1)), Q)


def test_sample_sums_dependence():
    rng = np.random.default_rng(1)
    curves = [normal_curve(1), normal_curve(1)]
    u = rng.uniform(size=5000)
    comonotone = ranks(np.column_stack([u, u]), rng)
    indep = ranks(rng.uniform(size=(5000, 2)), rng)
    s_co = sample_sums(curves, comonotone, 20000, rng)[0]
    s_ind = sample_sums(curves, indep, 20000, rng)[0]
    s_draw = sample_sums(curves, comonotone, 20000, rng, dependent=False)[0]
    q95 = 10 + 1.645
    # comonotone: the quantile of the sum = the sum of the quantiles
    assert np.quantile(s_co, 0.95) == pytest.approx(2 * q95, abs=0.08)
    # independent: sd sqrt(2), quantile 20 + 1.645 sqrt(2) < summed
    for s in (s_ind, s_draw):
        assert np.quantile(s, 0.95) == pytest.approx(20 + 1.645 * np.sqrt(2), abs=0.08)


def rows_for(origins, n=40, rho=1.0, seed=0):
    """Rows with N(10, 1) quantile forecasts per week and actuals that are perfectly
    correlated over the weeks of an origin (rho = 1) or independent (rho = 0)."""
    rng = np.random.default_rng(seed)
    out = []
    for o in origins:
        common = rng.normal(size=n)
        for h in range(1, 5):
            z = rho * common + np.sqrt(1 - rho**2) * rng.normal(size=n)
            df = pd.DataFrame({"stock_code": [f"s{i}" for i in range(n)], "origin": o, "h": h,
                               "y": 10 + z, "mean": 10.0, "scale": 1.0, "scale2": 1.0,
                               "weight": 1.0})  # fmt: skip
            for t, zz in zip(Q, Z, strict=True):
                df[f"q{t:g}"] = 10 + zz
            out.append(df)
    return pd.concat(out, ignore_index=True)


def test_pit_vectors_complete_only():
    rows = rows_for([O0], n=5)
    rows = rows[~((rows["stock_code"] == "s0") & (rows["h"] == 2))]
    v = pit_vectors(rows, Q, 2)
    assert len(v) == 4 and list(v.columns) == ["u1", "u2"]
    assert len(pit_vectors(rows, Q, 1)) == 5


def test_horizon_sums_learns_dependence_without_look_ahead():
    origins = list(pd.date_range(O0, periods=10, freq="W-MON"))
    rows = rows_for(origins, rho=1.0)
    frames, info = horizon_sums(rows, Q, ks=(2, 4), n_paths=4000, min_pool=10)
    s, p, i = frames["summed"], frames["paths"], frames["indep"]
    assert set(s["h"]) == {2, 4} and s["origin"].nunique() == 10
    # pool at origin t: origins o with o + (K-1) weeks < t
    n2 = info[info["k"] == 2].set_index("origin")["n_pool"]
    assert n2.iloc[0] == 0 and n2.iloc[1] == 0 and n2.iloc[2] == 40
    assert p[p["h"] == 4]["origin"].min() == origins[4]
    want = rows[rows["h"] <= 2].groupby(["stock_code", "origin"])["y"].sum()
    got = s[s["h"] == 2].set_index(["stock_code", "origin"])["y"]
    np.testing.assert_allclose(got.loc[want.index], want)
    late = p[(p["h"] == 4) & (p["origin"] == origins[-1])]
    late_i = i[(i["h"] == 4) & (i["origin"] == origins[-1])]
    late_s = s[(s["h"] == 4) & (s["origin"] == origins[-1])]
    # perfectly correlated weeks: paths ~ summed quantiles, independent ones much narrower
    assert late["q0.95"].mean() == pytest.approx(late_s["q0.95"].mean(), abs=0.3)
    assert late_i["q0.95"].mean() == pytest.approx(40 + 1.645 * 2, abs=0.3)
    assert (late_s["scale"] == 4.0).all() and (late_s["scale2"] == 16.0).all()
    # no look-ahead: actuals of target weeks >= the origin do not change its paths
    t = origins[6]
    changed = rows.copy()
    tw = changed["origin"] + pd.to_timedelta((changed["h"] - 1) * 7, unit="D")
    changed.loc[(tw >= t) & (changed["origin"] < t), "y"] += 100
    p2 = horizon_sums(changed, Q, ks=(2,), n_paths=500, min_pool=10)[0]["paths"]
    p1 = horizon_sums(rows, Q, ks=(2,), n_paths=500, min_pool=10)[0]["paths"]
    cols = [f"q{x:g}" for x in Q]
    pd.testing.assert_frame_equal(p1.loc[p1["origin"] == t, cols], p2.loc[p2["origin"] == t, cols])


def test_independent_actuals_paths_narrower_than_summed_and_ratio():
    origins = list(pd.date_range(O0, periods=10, freq="W-MON"))
    rows = rows_for(origins, n=80, rho=0.0)
    frames, _ = horizon_sums(rows, Q, ks=(4,), n_paths=4000, min_pool=10)
    late = frames["paths"][frames["paths"]["origin"] == origins[-1]]
    assert late["q0.95"].mean() == pytest.approx(40 + 1.645 * 2, abs=0.3)
    r = overstatement(frames["summed"], frames["paths"], Q).set_index("tau")
    assert r.loc[0.95, "median_ratio"] > 1.02 and r.loc[0.05, "median_ratio"] < 0.98
    assert r.loc[0.5, "median_ratio"] == pytest.approx(1.0, abs=0.01)


def test_common_ties_keep_zero_runs_together():
    """Dead series (y = 0 in all weeks) under curves with zero regions of different length: with
    one shared uniform per vector the weeks stay together, so the pooled paths put more mass on
    an all-zero sum than with a fresh uniform per week."""
    rng = np.random.default_rng(3)
    n, k = 600, 4
    zero_to = rng.choice([2, 4, 5], size=n)  # number of zero quantiles: up to tau 0.05 / 0.2 / 0.5
    dead = rng.uniform(size=n) < 0.5
    out = []
    for h in range(1, k + 1):
        q = np.tile(np.arange(1.0, 11.0), (n, 1))
        q[np.arange(10)[None, :] < zero_to[:, None]] = 0.0
        y = np.where(dead, 0.0, rng.integers(1, 8, size=n).astype(float))
        df = pd.DataFrame({"stock_code": [f"s{i}" for i in range(n)], "origin": O0, "h": h, "y": y})
        for j, t in enumerate(Q):
            df[f"q{t:g}"] = q[:, j]
        out.append(df)
    rows = pd.concat(out, ignore_index=True)
    common = pit_vectors(rows, Q, k, common_ties=True)
    fresh = pit_vectors(rows, Q, k)
    d = common.loc[[f"s{i}" for i in np.flatnonzero(dead)]].to_numpy()
    assert np.allclose(d, d[:, :1])  # same curves, same shared uniform -> equal u per week
    r = ranks(np.array([[0.0, 0.0], [0.0, 0.0], [0.5, 0.5]]), rng, common_ties=True)
    assert (r[:, 0] == r[:, 1]).all()
    curve = knots(np.tile(np.r_[np.zeros(4), np.arange(5.0, 11.0)], (1, 1)), Q)  # zero to 0.2

    def p_zero(vec, common):
        pool = ranks(vec.to_numpy(), np.random.default_rng(0), common)
        s = sample_sums([curve] * k, pool, 20000, np.random.default_rng(1))
        return (s == 0).mean()

    assert p_zero(common, True) > p_zero(fresh, False) + 0.05


def test_horizon_sums_out_quantiles_and_sampled_subset():
    origins = list(pd.date_range(O0, periods=6, freq="W-MON"))
    rows = rows_for(origins, rho=1.0)
    both, _ = horizon_sums(rows, Q, ks=(2,), n_paths=500, min_pool=10)
    grid = [0.5, 0.85, 0.95]
    only, _ = horizon_sums(rows, Q, ks=(2,), n_paths=500, min_pool=10, out_quantiles=grid,
                           sampled=("paths",))  # fmt: skip
    assert set(only) == {"summed", "paths"}
    p = only["paths"]
    assert {"q0.5", "q0.85", "q0.95"} <= set(p.columns) and "q0.9" not in p.columns
    assert (p["q0.5"] <= p["q0.85"]).all() and (p["q0.85"] <= p["q0.95"]).all()
    # same stream: the shared levels equal those of the default call
    np.testing.assert_allclose(p["q0.95"].to_numpy(), both["paths"]["q0.95"].to_numpy())


def test_sample_paths_match_sums_and_on_paths_callback():
    from retail.paths import sample_paths, sample_sums

    q = np.array([np.linspace(1, 10, len(Q)), np.linspace(0, 20, len(Q))])
    t, v = knots(q, Q)
    pool = np.random.default_rng(3).uniform(size=(50, 2))
    curves = [(t, v), (t, v * 2)]
    s = sample_sums(curves, pool, 200, np.random.default_rng(7), dependent=True)
    p = sample_paths(curves, pool, 200, np.random.default_rng(7))
    assert p.shape == (2, 200, 2)
    np.testing.assert_allclose(p.sum(axis=2), s, rtol=1e-12)
    origins = list(pd.date_range(O0, periods=6, freq="W-MON"))
    rows = rows_for(origins, rho=0.5)
    seen = []
    plain, _ = horizon_sums(rows, Q, ks=(2,), n_paths=300, min_pool=10, sampled=("paths",))

    def keep(o, k, codes, vals):
        seen.append((o, k, len(codes), vals.shape))

    kept, _ = horizon_sums(rows, Q, ks=(2,), n_paths=300, min_pool=10, sampled=("paths",),
                           on_paths=keep)  # fmt: skip
    cols = [f"q{x:g}" for x in Q]
    np.testing.assert_allclose(kept["paths"][cols], plain["paths"][cols], rtol=1e-9)
    assert seen and all(k == 2 and shape[1:] == (300, 2) and shape[0] == n
                        for _, k, n, shape in seen)  # fmt: skip
