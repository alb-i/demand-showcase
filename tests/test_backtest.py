import json
import os

import numpy as np
import pandas as pd
import pytest
from conftest import W0, panel

from retail.backtest import (
    check_forecast,
    evaluate_origin,
    group_metrics,
    origin_weeks,
    revenue_weights,
    target_weeks,
    wide_units,
)
from retail.models.trivial import Trivial
from retail.runlog import RunLogger

Q = [0.1, 0.5, 0.9]


def week(i):
    return W0 + pd.Timedelta(weeks=i)


def test_wide_units_zero_after_last_sale_nan_before_first_and_closed():
    p = panel({"A": [5, 2, 0, 0], "B": [1, 0, 0, 0]}, closed=[2])
    p = p[~((p["stock_code"] == "A") & (p["week"] == week(0)))]  # A starts in week 1
    p = p[~((p["stock_code"] == "B") & (p["week"] > week(0)))]  # B's last sale is week 0
    w = wide_units(p)
    assert np.isnan(w.loc["A", week(0)]) and w.loc["A", week(1)] == 2
    assert np.isnan(w.loc["A", week(2)]) and np.isnan(w.loc["B", week(2)])  # closed
    assert w.loc["B", week(1)] == 0 and w.loc["B", week(3)] == 0  # after the last sale


def test_origin_and_target_weeks():
    o = origin_weeks({"from": "2011-01-03", "to": "2011-01-24"})
    assert [d.day for d in o] == [3, 10, 17, 24] and all(d.day_of_week == 0 for d in o)
    assert target_weeks(o[0], [1, 2]) == {1: o[0], 2: o[1]}


def test_check_forecast():
    skus = pd.Index(["A"])
    fc = pd.DataFrame(
        {"stock_code": ["A", "A"], "h": [1, 2], "mean": [1.0, 1.0],
         "q0.1": [0.0, 0.0], "q0.5": [1.0, 1.0], "q0.9": [2.0, 2.0]}
    )  # fmt: skip
    assert len(check_forecast(fc, skus, [1, 2], Q)) == 2
    with pytest.raises(ValueError, match="exactly one row"):
        check_forecast(fc.iloc[:1], skus, [1, 2], Q)
    with pytest.raises(ValueError, match="cross"):
        check_forecast(fc.assign(**{"q0.9": [0.5, 2.0]}), skus, [1, 2], Q)
    with pytest.raises(ValueError, match="missing"):
        check_forecast(fc.assign(mean=[np.nan, 1.0]), skus, [1, 2], Q)
    with pytest.raises(ValueError, match="lacks"):
        check_forecast(fc.drop(columns="q0.5"), skus, [1, 2], Q)


def test_revenue_weights_window():
    p = panel({"A": [1, 2, 3, 4]})
    w = revenue_weights(p, week(3), weeks=2)
    assert w["A"] == 2 + 3


def test_evaluate_origin_rows():
    p = panel({"A": [2, 2, 2, 2, 4], "B": [0, 0, 0, 0, 0]}, closed=[3])
    p = p[~((p["stock_code"] == "B") & (p["week"] < week(4)))]  # B first sold at the origin
    wide = wide_units(p)
    fc, rows = evaluate_origin(
        Trivial(window=52), p, wide, week(4), pd.Index(["A", "B", "C"]), [1, 2], Q
    )
    assert fc["stock_code"].unique().tolist() == ["A"]  # B, C: no sale before the origin
    r = rows.set_index("h")
    assert r.index.tolist() == [1]  # h=2 is after the data end: not evaluated
    assert r.loc[1, "y"] == 4 and r.loc[1, "mean"] == 2
    assert r.loc[1, "scale"] == 0  # constant history: no scale
    assert r.loc[1, "weight"] == 6  # revenue weeks 0-2 (week 3 closed)


def test_group_metrics_segments():
    rows = pd.DataFrame(
        {"stock_code": ["A", "B"], "h": [1, 1], "y": [3.0, 0.0], "mean": [1.0, 2.0],
         "q0.1": [0.0, 0.0], "q0.5": [1.0, 1.0], "q0.9": [2.0, 3.0],
         "scale": [2.0, 1.0], "scale2": [4.0, 1.0], "weight": [3.0, 1.0]}
    )  # fmt: skip
    recs = group_metrics(rows, Q, [0.8], lambda c: c.map({"A": "A-smooth"}))
    by = {r["segment"]: r for r in recs}
    assert set(by) == {"all", "A-smooth"}
    assert by["all"]["n"] == 2 and by["all"]["mase"] == pytest.approx(1.5)
    assert by["all"]["mase_w"] == pytest.approx(1.25)
    assert by["A-smooth"]["mase"] == 1.0


def test_runlog(tmp_path):
    with RunLogger({"model": {"name": "t"}}, name="t", data_version="v1", root=tmp_path) as run:
        run.log(origin="2011-01-03", mase=float("nan"))
        run.write_parquet("forecasts", pd.DataFrame({"a": [1]}))
    meta = json.loads((run.dir / "meta.json").read_text())
    assert meta["status"] == "finished" and meta["dataset_version"] == "v1"
    rec = json.loads((run.dir / "metrics.jsonl").read_text().splitlines()[0])
    assert rec["mase"] is None and "ts" in rec
    assert (run.dir / "forecasts.parquet").exists() and (run.dir / "heartbeat").exists()
    with pytest.raises(ZeroDivisionError):
        with RunLogger({}, name="c", data_version="v1", root=tmp_path) as crashed:
            raise ZeroDivisionError("boom")
    assert json.loads((crashed.dir / "meta.json").read_text())["status"] == "crashed"


def test_trivial_model_uses_the_last_window():
    from retail.backtest import History

    p = panel({"A": [100, 1, 2, 3]})
    h = History(p, wide_units(p), week(4))
    fc = Trivial(window=3).predict(h, pd.Index(["A"]), [1, 2], Q).set_index("h")
    assert fc.loc[1, "mean"] == 2 and fc.loc[2, "q0.5"] == 2  # 100 is outside the window
    assert fc.loc[1, "q0.1"] == pytest.approx(1.2) and fc.loc[1, "q0.9"] == pytest.approx(2.8)


def test_script_refuses_test_origins_without_final():
    import subprocess
    import sys

    from retail.io import REPO_DIR

    r = subprocess.run(
        [sys.executable, str(REPO_DIR / "scripts" / "backtest.py"), "x.yaml", "--origins", "test"],
        capture_output=True,
        text=True,
    )
    assert r.returncode == 2 and "--final" in r.stderr


def test_run_origins_parallel_equals_sequential():
    from retail.backtest import default_jobs, run_origins, wide_units
    from retail.models.croston import Intermittent

    rng = np.random.default_rng(5)
    series = {f"s{i}": (rng.poisson(4, 30) * (rng.random(30) < 0.6)).tolist() for i in range(12)}
    p = panel(series)
    wide = wide_units(p)
    skus = pd.Index(sorted(series))
    origins = [W0 + pd.Timedelta(weeks=w) for w in (10, 14, 18, 22, 26)]
    model = Intermittent("tsb", 0.2, min_pool=5)
    seq = list(run_origins(model, p, wide, origins, skus, [1, 2], [0.1, 0.5, 0.9], 8, jobs=1))
    par = list(run_origins(model, p, wide, origins, skus, [1, 2], [0.1, 0.5, 0.9], 8, jobs=3))
    assert [r[0] for r in par] == origins  # origin order kept
    for (_, fc1, rows1, _), (_, fc2, rows2, _) in zip(seq, par, strict=True):
        pd.testing.assert_frame_equal(fc1, fc2)
        pd.testing.assert_frame_equal(rows1, rows2)
    assert default_jobs() == min(6, len(os.sched_getaffinity(0)))
