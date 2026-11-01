import numpy as np
import pandas as pd
import pytest

from retail.compare import compare, summary
from retail.leaderboard import leaderboard

Q = [0.1, 0.5, 0.9]
ORIGIN = pd.Timestamp("2011-06-06")


def rows(shift: float, n: int = 30, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    codes = [f"s{i}" for i in range(n)]
    recs = []
    for i, c in enumerate(codes):
        for h in (1, 2):
            y = float(rng.poisson(5))
            m = 5.0 + shift
            recs.append({"stock_code": c, "origin": ORIGIN, "h": h, "y": y, "mean": m,
                         "q0.1": m - 2, "q0.5": m, "q0.9": m + 2, "scale": 1.0,
                         "scale2": 1.0, "weight": 1.0,
                         "segment": "A-smooth" if i < n // 2 else "B-lumpy"})  # fmt: skip
    return pd.DataFrame(recs)


def test_leaderboard_metrics_and_intervals():
    runs = {"ref": rows(3.0), "good": rows(0.0), "same": rows(3.0)}
    lb = leaderboard(runs, "ref", Q, [0.8], n=300).set_index(["model", "segment"])
    assert set(lb.index.get_level_values("segment")) == {"all", "A-smooth", "B-lumpy"}
    assert np.isnan(lb.loc[("ref", "all"), "mase_diff"])
    g = lb.loc[("good", "all")]
    assert g["mase"] == pytest.approx(summary(runs["good"], Q, [0.8]).iloc[0]["mase"])
    want = compare(runs["good"], runs["ref"], Q, [0.8], "abs_scaled", n=300)
    assert g["mase_diff"] == pytest.approx(want["diff"]) and g["mase_sig"]
    assert g["mase_lo"] <= g["mase_diff"] <= g["mase_hi"]
    assert lb.loc[("same", "B-lumpy"), "crps_diff"] == pytest.approx(0)
    assert not lb.loc[("same", "B-lumpy"), "crps_sig"]
    assert lb.loc[("good", "A-smooth"), "series"] == 15


def test_leaderboard_needs_the_reference():
    with pytest.raises(ValueError):
        leaderboard({"a": rows(0.0)}, "ref", Q, [0.8])
