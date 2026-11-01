import pandas as pd
import pytest

from retail.report import FAMILIES, family, hit_curve


def test_family_covers_the_e9_models():
    names = ["naive", "snaive", "ma4", "ma13", "croston-a0.1", "sba-a0.2", "tsb-a0.2-b0.2",
             "split-ma4-bulk-ma52", "topdown-ma4-bulk-ma52", "ets-bulk-ma52", "arima-bulk-ma52",
             "lgbm-item-bulk-ma52", "lgbm-total-q-p1.8", "best-crps"]  # fmt: skip
    got = [family(n) for n in names]
    assert set(got) == set(FAMILIES)
    assert got[:4] == ["Simple baselines"] * 4 and got[-1] == "LightGBM"
    with pytest.raises(ValueError):
        family("prophet")


def test_hit_curve_plain_vs_randomised_on_zero_ties():
    # q = (0, 0, 2) at tau (0.1, 0.5, 0.9); y = 0 ties the two lower levels
    rows = pd.DataFrame({"y": [0.0, 1.0, 3.0, 0.0], "q0.1": 0.0, "q0.5": 0.0, "q0.9": 2.0,
                         "mean": 1.0, "scale": 1.0, "scale2": 1.0, "weight": 1.0})  # fmt: skip
    h = hit_curve(rows, [0.1, 0.5, 0.9]).set_index("tau")
    assert h.loc[0.1, "hit"] == 0.5 and h.loc[0.9, "hit"] == 0.75  # y <= q counts the ties
    assert h.loc[0.1, "rhit"] < h.loc[0.1, "hit"]  # randomised PIT spreads them
    assert h["rhit"].between(0, 1).all() and h["rhit"].is_monotonic_increasing
