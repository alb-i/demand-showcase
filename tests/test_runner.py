import numpy as np
import pandas as pd
import pytest
from conftest import W0, panel

from retail.backtest import run_origins, wide_units
from retail.models.croston import Intermittent
from retail.models.trivial import Trivial
from retail.runlog import RunLogger
from retail.runner import Prepared, finish, log_origin, origin_metrics, schedule

Q = [0.1, 0.5, 0.9]


def prep(name, model, origins, seed=5):
    rng = np.random.default_rng(seed)
    series = {f"s{i}": (rng.poisson(4, 30) * (rng.random(30) < 0.6)).tolist() for i in range(12)}
    p = panel(series)
    labels = pd.Series({f"s{i}": "A-x" if i < 6 else "B-y" for i in range(12)})
    return Prepared(name=name, model=model, panel=p, wide=wide_units(p),
                    skus=pd.Index(sorted(series)), origins=origins, horizons=[1, 2], quantiles=Q,
                    levels=[0.8], weight_weeks=8, labels=labels)  # fmt: skip


ORIGINS = [W0 + pd.Timedelta(weeks=w) for w in (10, 14, 18, 22, 26)]


class Boom(Trivial):
    """Fails at one origin."""

    def predict(self, history, skus, horizons, quantiles):
        if history.origin == ORIGINS[2]:
            raise ValueError("boom")
        return super().predict(history, skus, horizons, quantiles)


@pytest.mark.parametrize("jobs", [1, 3])
def test_schedule_equals_run_origins_per_run_in_origin_order(jobs):
    a = prep("tsb", Intermittent("tsb", 0.2, min_pool=5), ORIGINS)
    b = prep("triv", Trivial(), ORIGINS[:3], seed=7)
    out = list(schedule({"tsb": a, "triv": b}, jobs=jobs))
    assert len(out) == 8
    for key, p in (("tsb", a), ("triv", b)):
        got = [x for x in out if x[0] == key]
        assert [x[1] for x in got] == p.origins  # origin order within a run
        ref = list(run_origins(p.model, p.panel, p.wide, p.origins, p.skus, p.horizons, Q, 8))
        for (_, _, fc, rows, _, recs), (_, fc2, rows2, _) in zip(got, ref, strict=True):
            pd.testing.assert_frame_equal(fc, fc2)
            pd.testing.assert_frame_equal(rows, rows2)
            assert recs == origin_metrics(p, rows2)  # metrics from the worker


def test_schedule_order_run_by_run_most_expensive_first():
    a = prep("cheap", Trivial(), ORIGINS)
    b = prep("dear", Trivial(), ORIGINS)
    cost = {"cheap": 1.0, "dear": 10.0}
    out = list(schedule({"cheap": a, "dear": b}, lambda k, o: cost[k], jobs=1))
    assert [x[0] for x in out] == ["dear"] * 5 + ["cheap"] * 5


@pytest.mark.parametrize("jobs", [1, 2])
def test_schedule_failure_stops_only_that_run(jobs):
    bad = prep("bad", Boom(), ORIGINS)
    good = prep("good", Trivial(), ORIGINS)
    out = list(schedule({"bad": bad, "good": good}, jobs=jobs))
    b = [x for x in out if x[0] == "bad"]
    assert b[-1][2] is None and "boom" in b[-1][4] and b[-1][1] == ORIGINS[2]
    assert all(x[2] is not None for x in b[:-1]) and len(b) <= 3
    assert [x[1] for x in out if x[0] == "good"] == ORIGINS


def test_log_origin_and_finish(tmp_path):
    p = prep("triv", Trivial(), ORIGINS[:2])
    with RunLogger({"x": 1}, name="triv", data_version="v", root=tmp_path) as run:
        fcs, rows = [], []
        for _, origin, fc, r, _, recs in schedule({"triv": p}, jobs=1):
            log_origin(run, p, origin, recs)
            fcs.append(fc)
            rows.append(r)
        overall = finish(run, p, fcs, rows)
    assert {r["h"] for r in overall} == {1, 2} and all(r["segment"] == "all" for r in overall)
    saved = pd.read_parquet(run.dir / "rows.parquet")
    assert set(saved["segment"]) == {"A-x", "B-y"} and len(saved) == sum(map(len, rows))
    lines = (run.dir / "metrics.jsonl").read_text().splitlines()
    assert any('"origin": "all"' in x for x in lines)
