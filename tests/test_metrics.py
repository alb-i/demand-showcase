import math

import numpy as np
import pandas as pd
import pytest

from retail.metrics import aggregate, interval, naive_scale, paired_bootstrap, pinball, row_errors

Q = [0.1, 0.5, 0.9]


def rows():
    # hand-computed values in the comments below
    return pd.DataFrame(
        {
            "y": [3.0, 0.0],
            "mean": [1.0, 2.0],
            "q0.1": [0.0, 0.0],
            "q0.5": [1.0, 1.0],
            "q0.9": [2.0, 3.0],
            "scale": [2.0, 1.0],
            "scale2": [4.0, 1.0],
            "weight": [3.0, 1.0],
        }
    )


def test_naive_scale_skips_closed_weeks():
    units = pd.DataFrame([[1, np.nan, 3, 0], [np.nan, np.nan, np.nan, 5]], index=["a", "b"])
    s = naive_scale(units)
    assert s.loc["a", "scale"] == 2.5  # |3-1|, |0-3|
    assert s.loc["a", "scale2"] == 6.5  # 4, 9
    assert np.isnan(s.loc["b", "scale"])


def test_pinball():
    assert pinball(3, 0, 0.1) == pytest.approx(0.3)
    assert pinball(0, 3, 0.9) == pytest.approx(0.3)
    assert pinball(2, 2, 0.5) == 0


def test_interval():
    assert interval(0.8) == (0.1, 0.9)
    assert interval(0.95) == (0.025, 0.975)


def test_row_errors_by_hand():
    e = row_errors(rows(), Q, [0.8])
    assert e["e"].tolist() == [2.0, -2.0]
    assert e["abs_scaled"].tolist() == [1.0, 2.0]
    assert e["sq_scaled"].tolist() == [1.0, 4.0]
    # pinball/scale: row 1: 0.3/2, 1.0/2, 0.9/2; row 2: 0, 0.5, 0.3
    assert e["pinball_0.1"].tolist() == pytest.approx([0.15, 0.0])
    assert e["pinball_0.5"].tolist() == pytest.approx([0.5, 0.5])
    assert e["pinball_0.9"].tolist() == pytest.approx([0.45, 0.3])
    assert e["crps"].tolist() == pytest.approx([2 * 1.1 / 3, 2 * 0.8 / 3])
    assert e["cover_0.8"].tolist() == [0.0, 1.0]


def test_aggregate_unweighted_and_weighted():
    r = rows()
    e = row_errors(r, Q, [0.8])
    u = aggregate(r, e, weighted=False)
    assert u["mase"] == pytest.approx(1.5)
    assert u["rmsse"] == pytest.approx(math.sqrt(2.5))
    assert u["bias"] == 0.0
    assert u["crps"] == pytest.approx((2.2 + 1.6) / 6)
    assert u["cover_0.8"] == 0.5
    w = aggregate(r, e, weighted=True)
    assert w["mase"] == pytest.approx((3 * 1 + 1 * 2) / 4)
    assert w["bias"] == pytest.approx((3 * 2 - 1 * 2) / (3 * 3 + 0))
    assert w["cover_0.8"] == pytest.approx(0.25)


def test_unscaled_series_left_out():
    r = rows().assign(scale=[2.0, 0.0], scale2=[4.0, np.nan])
    e = row_errors(r, Q, [0.8])
    assert np.isnan(e.loc[1, "abs_scaled"]) and np.isnan(e.loc[1, "crps"])
    assert aggregate(r, e, weighted=False)["mase"] == 1.0


def test_paired_bootstrap_detects_a_real_difference():
    rng = np.random.default_rng(1)
    b = pd.Series(rng.gamma(2, 1, 300))
    a = b + 0.5 + rng.normal(0, 0.3, 300)
    res = paired_bootstrap(a, b, n=1000)
    assert res["significant"] and res["lo"] < 0.5 < res["hi"]
    assert res["diff"] == pytest.approx((a - b).mean())


def test_paired_bootstrap_no_difference():
    rng = np.random.default_rng(2)
    b = pd.Series(rng.gamma(2, 1, 300))
    a = b + rng.normal(0, 0.3, 300)
    a -= (a - b).mean()  # mean difference exactly 0
    res = paired_bootstrap(a, b, n=1000)
    assert not res["significant"] and res["lo"] < 0 < res["hi"]


def test_paired_bootstrap_weights_and_alignment():
    a = pd.Series({"x": 1.0, "y": 5.0, "z": 9.0})
    b = pd.Series({"x": 0.0, "y": 0.0})  # z missing in b: dropped
    res = paired_bootstrap(a, b, weights=pd.Series({"x": 1.0, "y": 0.0}), n=200)
    assert res["n_series"] == 2 and res["diff"] == 1.0
