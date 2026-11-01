"""Rolling-origin backtester with a leakage guard.

At origin t (a Monday) a model sees only a `History` of the weeks < t and forecasts the weeks
t, t+1w, ..., t+(H-1)w (horizon h = 1 is the week starting at the origin). Any request through
the History for a week >= t raises LeakageError, and the History holds no row of such a week.

Evaluated rows: every product of the evaluation set with a first sale before the origin,
all horizons; weeks after a product's last sale count as 0 demand, closed weeks and weeks after
the data end are not evaluated. Revenue weights: the product's revenue in the 52 weeks before
the origin.

run_origins evaluates the origins one after another or, with jobs > 1, in worker processes
(spawned, each gets the panel once; default 6); the results come back in origin order
either way.
"""

import multiprocessing as mp
import os
import time
from collections.abc import Callable, Iterator
from concurrent.futures import ProcessPoolExecutor
from typing import Protocol

import numpy as np
import pandas as pd

from retail.metrics import aggregate, naive_scale, qcol, row_errors


class LeakageError(RuntimeError):
    """A model asked for data of a week at or after its forecast origin."""


def wide_units(panel: pd.DataFrame) -> pd.DataFrame:
    """sku x week matrix of units over all weeks of the panel: NaN before the first sale and in
    closed weeks, 0 for open weeks after the last sale (the product simply did not sell)."""
    weeks = pd.Index(sorted(panel["week"].unique()), name="week")
    wide = panel.pivot(index="stock_code", columns="week", values="units").reindex(columns=weeks)
    closed = panel.groupby("week")["closed"].first().reindex(weeks).fillna(False).to_numpy(bool)
    started = wide.notna().cumsum(axis=1).to_numpy() > 0
    fill = started & ~closed[None, :]
    return wide.mask(fill & wide.isna().to_numpy(), 0.0)


class History:
    """What a model may know at `origin`: panel rows and the units matrix of the weeks < origin."""

    def __init__(self, panel: pd.DataFrame, wide: pd.DataFrame, origin: pd.Timestamp):
        self.origin = pd.Timestamp(origin)
        self._rows = panel[panel["week"] < self.origin].copy()
        self._units = wide.loc[:, wide.columns < self.origin].copy()

    def _check(self, week) -> pd.Timestamp:
        week = pd.Timestamp(week)
        if week >= self.origin:
            raise LeakageError(f"week {week.date()} requested at origin {self.origin.date()}")
        return week

    @property
    def units(self) -> pd.DataFrame:
        """sku x week units before the origin (see wide_units); a copy."""
        return self._units.copy()

    @property
    def rows(self) -> pd.DataFrame:
        """Panel rows (all columns) of the weeks before the origin; a copy."""
        return self._rows.copy()

    def week(self, week) -> pd.DataFrame:
        """Panel rows of one week; LeakageError for weeks >= origin."""
        week = self._check(week)
        return self._rows[self._rows["week"] == week].copy()

    def series(self, sku: str, until=None) -> pd.Series:
        """Units of one product before the origin (or before `until`, which must be <= it)."""
        s = self._units.loc[sku]
        if until is not None:
            if pd.Timestamp(until) > self.origin:
                self._check(until)
            s = s[s.index < pd.Timestamp(until)]
        return s.copy()


class Model(Protocol):
    name: str

    def predict(
        self, history: History, skus: pd.Index, horizons: list[int], quantiles: list[float]
    ) -> pd.DataFrame:
        """Rows (stock_code, h) for every sku x horizon with columns mean and q<tau>."""
        ...


def origin_weeks(spec: dict) -> list[pd.Timestamp]:
    """Mondays from spec['from'] to spec['to'] inclusive."""
    return list(pd.date_range(spec["from"], spec["to"], freq="W-MON"))


def target_weeks(origin: pd.Timestamp, horizons: list[int]) -> dict[int, pd.Timestamp]:
    return {h: origin + pd.Timedelta(weeks=h - 1) for h in horizons}


def check_forecast(
    fc: pd.DataFrame, skus: pd.Index, horizons: list[int], quantiles: list[float]
) -> pd.DataFrame:
    """Complete, finite, non-crossing forecasts; returned indexed by (stock_code, h)."""
    cols = ["mean", *[qcol(t) for t in quantiles]]
    missing = [c for c in ["stock_code", "h", *cols] if c not in fc.columns]
    if missing:
        raise ValueError(f"forecast lacks columns {missing}")
    fc = fc.set_index(["stock_code", "h"])[cols]
    want = pd.MultiIndex.from_product([skus, horizons], names=["stock_code", "h"])
    if fc.index.has_duplicates or len(fc.index.intersection(want)) != len(want):
        raise ValueError("forecast must have exactly one row per sku and horizon")
    fc = fc.loc[want]
    v = fc.to_numpy(float)
    if not np.isfinite(v).all():
        raise ValueError("forecast has missing or infinite values")
    if (np.diff(v[:, 1:], axis=1) < -1e-9).any():
        raise ValueError("forecast quantiles cross")
    return fc


def revenue_weights(panel: pd.DataFrame, origin: pd.Timestamp, weeks: int = 52) -> pd.Series:
    start = origin - pd.Timedelta(weeks=weeks)
    p = panel[(panel["week"] >= start) & (panel["week"] < origin)]
    return p.groupby("stock_code")["revenue"].sum()


def evaluate_origin(
    model: Model,
    panel: pd.DataFrame,
    wide: pd.DataFrame,
    origin: pd.Timestamp,
    skus: pd.Index,
    horizons: list[int],
    quantiles: list[float],
    weight_weeks: int = 52,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Forecasts of one origin and the evaluated rows (y, scale, weight, forecast columns)."""
    history = History(panel, wide, origin)
    known = history.units.loc[history.units.index.intersection(skus)]
    active = known.index[known.notna().any(axis=1)]  # first sale before the origin
    fc = model.predict(history, active, horizons, quantiles)
    fc = check_forecast(fc, active, horizons, quantiles)
    tw = target_weeks(origin, horizons)
    y = wide.reindex(index=active, columns=list(tw.values()))
    y.columns = list(tw)
    y = y.stack(future_stack=True).rename("y")
    y.index.names = ["stock_code", "h"]
    scale = naive_scale(known.loc[active])
    rows = fc.join(y).join(scale, on="stock_code")
    rows["weight"] = (
        revenue_weights(panel, origin, weight_weeks)
        .reindex(rows.index.get_level_values(0))
        .fillna(0)
        .to_numpy()
    )
    rows = rows.reset_index().assign(origin=origin)
    forecasts = fc.reset_index().assign(origin=origin)
    return forecasts, rows[rows["y"].notna()]


DEFAULT_JOBS = 6  # the physical cores of the laptop; more workers only share them


def default_jobs() -> int:
    """DEFAULT_JOBS, at most the usable cores."""
    return max(1, min(DEFAULT_JOBS, len(os.sched_getaffinity(0))))


_JOB: dict = {}  # what the worker processes need for evaluate_origin


def _init_job(job: dict) -> None:
    _JOB.clear()
    _JOB.update(job)


def _evaluate_job(origin: pd.Timestamp) -> tuple[pd.DataFrame, pd.DataFrame, float]:
    t0 = time.time()
    j = _JOB
    fc, rows = evaluate_origin(j["model"], j["panel"], j["wide"], origin, j["skus"],
                               j["horizons"], j["quantiles"], j["weight_weeks"])  # fmt: skip
    return fc, rows, time.time() - t0


def run_origins(
    model: Model,
    panel: pd.DataFrame,
    wide: pd.DataFrame,
    origins,
    skus: pd.Index,
    horizons: list[int],
    quantiles: list[float],
    weight_weeks: int = 52,
    jobs: int = 1,
) -> Iterator[tuple[pd.Timestamp, pd.DataFrame, pd.DataFrame, float]]:
    """(origin, forecasts, rows, seconds) per origin, in origin order; jobs > 1 uses that many
    worker processes (at most one per origin). Results do not depend on jobs."""
    job = dict(model=model, panel=panel, wide=wide, skus=skus, horizons=horizons,
               quantiles=quantiles, weight_weeks=weight_weeks)  # fmt: skip
    origins = list(origins)
    jobs = min(jobs, len(origins))
    if jobs <= 1:
        _init_job(job)
        try:
            for origin in origins:
                yield origin, *_evaluate_job(origin)
        finally:
            _JOB.clear()
        return
    ctx = mp.get_context("spawn")  # no fork: the run logger has a heartbeat thread
    with ProcessPoolExecutor(jobs, mp_context=ctx, initializer=_init_job, initargs=(job,)) as ex:
        for origin, res in zip(origins, ex.map(_evaluate_job, origins), strict=True):
            yield origin, *res


def group_metrics(
    rows: pd.DataFrame,
    quantiles: list[float],
    levels: list[float],
    segment_of: Callable[[pd.Series], pd.Series],
) -> list[dict]:
    """One record per (segment, h), segments = "all" plus segment_of(stock_code) values; scaled
    metrics unweighted and revenue weighted (suffix _w)."""
    err = row_errors(rows, quantiles, levels)
    seg = segment_of(rows["stock_code"])
    out = []
    for name, mask in [("all", pd.Series(True, index=rows.index))] + [
        (s, seg == s) for s in sorted(seg.dropna().unique())
    ]:
        for h, idx in rows[mask].groupby("h").groups.items():
            r, e = rows.loc[idx], err.loc[idx]
            rec = {"segment": name, "h": int(h), "n": len(r)}
            rec["n_unscaled"] = int(e["abs_scaled"].isna().sum())
            rec |= aggregate(r, e, weighted=False)
            rec |= {f"{k}_w": v for k, v in aggregate(r, e, weighted=True).items()}
            out.append(rec)
    return out
