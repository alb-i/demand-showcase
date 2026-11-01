"""Backtest runs as data, and a batch scheduler that runs the origins of many runs in one worker
pool (E9).

`Prepared` holds everything a run needs (model, panel, evaluation set, origins, config, name);
scripts/backtest.py builds one and runs its origins; scripts/run_batch.py builds many and hands
every (run, origin) pair to one pool of `jobs` worker processes, most expensive first (longest
processing time first, run by run), so the cores stay busy until the last task instead of
idling at the end of each run. The results of a run do not depend on the scheduling: every
origin is evaluated by evaluate_origin exactly as in run_origins, and each run logs its origins
in origin order.
The workers also compute each origin's metric records, so the main process only writes them:
heavy pandas work in the main process starves the pool's feeder thread (GIL) and leaves
workers idle.
"""

import multiprocessing as mp
import time
import traceback
from collections.abc import Callable, Iterator
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import dataclass, field

import pandas as pd

from retail.backtest import evaluate_origin, group_metrics


@dataclass
class Prepared:
    """One backtest run: model, data and settings (picklable; the panel may be shared)."""

    name: str  # run name, e.g. ma4-focus
    model: object
    panel: pd.DataFrame
    wide: pd.DataFrame
    skus: pd.Index
    origins: list[pd.Timestamp]
    horizons: list[int]
    quantiles: list[float]
    levels: list[float]
    weight_weeks: int
    labels: pd.Series  # stock_code -> segment label
    config: dict = field(default_factory=dict)
    data_version: str = ""

    def segment_of(self, codes: pd.Series) -> pd.Series:
        return codes.map(self.labels).fillna("unclassified")

    def evaluate(self, origin: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame, float]:
        t0 = time.time()
        fc, rows = evaluate_origin(self.model, self.panel, self.wide, origin, self.skus,
                                   self.horizons, self.quantiles, self.weight_weeks)  # fmt: skip
        return fc, rows, time.time() - t0


def origin_metrics(prep: Prepared, rows: pd.DataFrame) -> list[dict]:
    """The metric records of one origin (computed in the worker)."""
    return group_metrics(rows, prep.quantiles, prep.levels, prep.segment_of)


def log_origin(run, prep: Prepared, origin, recs: list[dict]) -> None:
    for rec in recs:
        run.log(origin=str(origin.date()), model=prep.model.name, **rec)


def finish(run, prep: Prepared, fcs: list[pd.DataFrame], rows: list[pd.DataFrame]) -> list[dict]:
    """Overall metrics, forecasts.parquet and rows.parquet of a run; returns the overall
    records of segment "all" per h."""
    r = pd.concat(rows, ignore_index=True)
    recs = group_metrics(r, prep.quantiles, prep.levels, prep.segment_of)
    for rec in recs:
        run.log(origin="all", model=prep.model.name, **rec)
    run.write_parquet("forecasts", pd.concat(fcs, ignore_index=True))
    run.write_parquet("rows", r.assign(segment=prep.segment_of(r["stock_code"])))
    return [x for x in recs if x["segment"] == "all"]


_PREPS: dict = {}


def _init(preps: dict) -> None:
    _PREPS.clear()
    _PREPS.update(preps)


def _task(key: str, origin: pd.Timestamp):
    try:
        prep = _PREPS[key]
        fc, rows, seconds = prep.evaluate(origin)
        return key, origin, fc, rows, seconds, origin_metrics(prep, rows)
    except Exception:  # reported to the caller, the other runs go on
        return key, origin, None, None, traceback.format_exc(), None


def schedule(
    preps: dict[str, Prepared],
    cost: Callable[[str, pd.Timestamp], float] | None = None,
    jobs: int = 6,
) -> Iterator[tuple[str, pd.Timestamp, pd.DataFrame, pd.DataFrame, float, list[dict]]]:
    """(key, origin, forecasts, rows, seconds, metric records) for every origin of every run,
    per run in origin order (a result is held back until the earlier origins of its run are
    done). Tasks are submitted run by run, the most expensive run first (sum of cost(key,
    origin)), within a run the most expensive origin first (default cost: later origins first,
    they have more history); the next run's tasks fill the workers while a run finishes, and
    only a few runs are open at a time. jobs = worker processes (1: in this process, in
    submission order). If an origin fails, its run yields once (key, origin, None, None,
    traceback, None) and nothing more; the other runs go on."""
    cost = cost or (lambda key, origin: origin.value)
    run_cost = {k: sum(cost(k, o) for o in p.origins) for k, p in preps.items()}
    tasks = sorted(((k, o) for k, p in preps.items() for o in p.origins),
                   key=lambda t: (run_cost[t[0]], t[0], cost(*t)), reverse=True)  # fmt: skip
    pending = {k: {} for k in preps}
    nxt = {k: 0 for k in preps}
    failed = set()

    def release(key, origin, *res):
        if key in failed:
            return
        if res[0] is None:
            failed.add(key)
            yield key, origin, *res
            return
        pending[key][origin] = res
        p = preps[key]
        while nxt[key] < len(p.origins) and p.origins[nxt[key]] in pending[key]:
            o = p.origins[nxt[key]]
            yield key, o, *pending[key].pop(o)
            nxt[key] += 1

    if jobs <= 1:
        _init(preps)
        try:
            for key, origin in tasks:
                yield from release(*_task(key, origin))
        finally:
            _PREPS.clear()
        return
    ctx = mp.get_context("spawn")  # no fork: run loggers have heartbeat threads
    with ProcessPoolExecutor(jobs, mp_context=ctx, initializer=_init, initargs=(preps,)) as ex:
        futures = {ex.submit(_task, k, o) for k, o in tasks}
        while futures:
            done, futures = wait(futures, return_when=FIRST_COMPLETED)
            for f in done:
                yield from release(*f.result())
