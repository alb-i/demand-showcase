import numpy as np
import pandas as pd

from retail.selection import compose, segment_table, winners

Q = [0.1, 0.5, 0.9]
O0 = pd.Timestamp("2011-01-03")


def rows(width, codes=("a1", "a2", "b1", "b2", "new"), extra=()):
    """y = 10; quantiles 10 -/+ width (wider = worse CRPS)."""
    out = []
    for c in codes:
        w = width[c[0]] if isinstance(width, dict) else width
        out.append(
            {
                "stock_code": c,
                "origin": O0,
                "h": 1,
                "y": 10.0,
                "mean": 10.0,
                "scale": 1.0,
                "scale2": 1.0,
                "weight": 1.0,
                "q0.1": 10 - w,
                "q0.5": 10.0,
                "q0.9": 10 + w,
            }
        )
    return pd.DataFrame(out)


LABELS = pd.Series({"a1": "A", "a2": "A", "b1": "B", "b2": "B"})


def test_segment_table_and_winners_per_segment():
    runs = {"m1": rows({"a": 1.0, "b": 3.0, "n": 2.0}), "m2": rows({"a": 2.0, "b": 1.0, "n": 1.0})}
    t = segment_table(runs, Q, [0.8], LABELS)
    assert set(t.index) == {"A", "B", "unclassified"} and list(t.columns) == ["m1", "m2"]
    assert winners(t).to_dict() == {"A": "m1", "B": "m2", "unclassified": "m2"}
    # only rows all candidates evaluated count
    t2 = segment_table({"m1": runs["m1"], "m2": runs["m2"].iloc[:2]}, Q, [0.8], LABELS)
    assert list(t2.index) == ["A"]


def test_winners_tie_first_column():
    t = pd.DataFrame({"x": [1.0], "y": [1.0]}, index=["A"])
    assert winners(t)["A"] == "x"


def test_compose_takes_whole_rows_of_the_winner():
    r1, r2 = rows(1.0), rows(5.0).assign(mean=99.0)
    out = compose({"m1": r1, "m2": r2}, pd.Series({"A": "m1", "B": "m2"}), LABELS, fallback="m1")
    by = out.set_index("stock_code")
    assert by.loc[["a1", "a2"], "source"].tolist() == ["m1", "m1"]
    assert by.loc[["b1", "b2"], "source"].tolist() == ["m2", "m2"]
    assert by.loc["b1", "mean"] == 99.0 and by.loc["b1", "q0.9"] == 15.0  # mean + quantiles
    assert by.loc["new", "source"] == "m1"  # no winner for unclassified -> fallback
    assert len(out) == 5 and not out.duplicated(["stock_code", "origin", "h"]).any()
    assert np.isclose(by.loc["a1", "q0.9"], 11.0)
