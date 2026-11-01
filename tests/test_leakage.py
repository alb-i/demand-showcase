"""No look-ahead: a model at origin t must not see week t or later."""

import pandas as pd
import pytest
from conftest import W0, panel

from retail.backtest import History, LeakageError, evaluate_origin, wide_units
from retail.models.trivial import Trivial

QUANTILES = [0.1, 0.5, 0.9]
ORIGIN = W0 + pd.Timedelta(weeks=4)


def data():
    p = panel({"A": [1, 2, 3, 4, 5, 6, 7, 8], "B": [0, 1, 0, 1, 0, 1, 0, 1]})
    return p, wide_units(p)


class Cheater:
    """Reads the actuals of the week it is supposed to forecast."""

    name = "cheater"

    def predict(self, history, skus, horizons, quantiles):
        actual = history.week(history.origin)
        raise AssertionError(f"leak not caught: {len(actual)} rows")


def test_cheating_model_raises():
    p, wide = data()
    with pytest.raises(LeakageError):
        evaluate_origin(Cheater(), p, wide, ORIGIN, pd.Index(["A", "B"]), [1, 2], QUANTILES)


def test_history_guards_every_access():
    p, wide = data()
    h = History(p, wide, ORIGIN)
    with pytest.raises(LeakageError):
        h.week(ORIGIN + pd.Timedelta(weeks=1))
    with pytest.raises(LeakageError):
        h.series("A", until=ORIGIN + pd.Timedelta(weeks=1))
    assert len(h.week(ORIGIN - pd.Timedelta(weeks=1))) == 2
    assert h.units.columns.max() < ORIGIN and h.rows["week"].max() < ORIGIN
    assert h.series("A").tolist() == [1, 2, 3, 4]


def test_history_copies_cannot_leak_back():
    p, wide = data()
    h = History(p, wide, ORIGIN)
    u = h.units
    u.loc["A"] = 999
    assert h.units.loc["A"].max() == 4


def test_forecasts_do_not_depend_on_the_future():
    p, wide = data()
    future = p["week"] >= ORIGIN
    p2 = p.copy()
    p2.loc[future, ["units", "revenue"]] *= 100
    skus = pd.Index(["A", "B"])
    fc1, _ = evaluate_origin(Trivial(window=3), p, wide, ORIGIN, skus, [1, 2], QUANTILES)
    fc2, rows2 = evaluate_origin(
        Trivial(window=3), p2, wide_units(p2), ORIGIN, skus, [1, 2], QUANTILES
    )
    pd.testing.assert_frame_equal(fc1, fc2)
    assert rows2.set_index(["stock_code", "h"]).loc[("A", 1), "y"] == 500  # targets do change
