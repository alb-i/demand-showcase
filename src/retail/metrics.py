"""Forecast metrics: MASE, RMSSE, bias, scaled pinball, CRPS approximation,
interval coverage, and the paired bootstrap over series.

Scaled metrics divide by the in-sample naive (lag 1) error of each series on the open weeks
before the origin; a series without such a scale (fewer than 2 weeks of history or a
constant history) is left out of the scaled metrics and counted in `n_unscaled`.
"""

import numpy as np
import pandas as pd


def naive_scale(units: pd.DataFrame) -> pd.DataFrame:
    """Per row (series) of a wide sku x week matrix (NaN = no history / closed week): mean
    absolute and mean squared difference of consecutive known weeks (closed weeks skipped)."""
    v = units.to_numpy(dtype=float)
    mae = np.full(len(v), np.nan)
    mse = np.full(len(v), np.nan)
    for i, row in enumerate(v):
        d = np.diff(row[~np.isnan(row)])
        if len(d):
            mae[i], mse[i] = np.abs(d).mean(), (d**2).mean()
    return pd.DataFrame({"scale": mae, "scale2": mse}, index=units.index)


def pinball(y, q, tau: float):
    """Pinball (quantile) loss of quantile forecast q at level tau."""
    diff = np.asarray(y, dtype=float) - np.asarray(q, dtype=float)
    return np.maximum(tau * diff, (tau - 1) * diff)


def qcol(tau: float) -> str:
    return f"q{tau:g}"


def interval(level: float) -> tuple[float, float]:
    """Central interval: 0.8 -> (0.1, 0.9)."""
    a = round((1 - level) / 2, 6)
    return a, round(1 - a, 6)


def pit_hits(y: np.ndarray, q: np.ndarray, taus) -> np.ndarray:
    """Randomised-PIT hit rates: per row and level tau, P(U <= tau) for the randomised
    PIT U of y under the forecast given by the sorted quantiles q (rows x levels). Without a
    tie it is 1 if y <= q_tau else 0 (as y <= q). Where y equals some quantiles (discrete
    demand, mostly y = q = 0), U is uniform on [lo, hi]: lo = the highest level whose quantile
    is < y (0 if none), hi = halfway between the highest tied level and the next level (1 if
    none), so a tied level counts as a fractional hit."""
    taus = np.asarray(taus, dtype=float)
    y = np.asarray(y, dtype=float)[:, None]
    q = np.asarray(q, dtype=float)
    t = np.broadcast_to(taus, q.shape)
    below, tie, above = q < y, q == y, q > y
    lo = np.where(below, t, 0.0).max(axis=1)
    nxt = np.where(above, t, 1.0).min(axis=1)
    top_tie = np.where(tie, t, -1.0).max(axis=1)
    hi = np.where(top_tie >= 0, (top_tie + nxt) / 2, nxt)
    return np.clip((taus[None, :] - lo[:, None]) / (hi - lo)[:, None], 0.0, 1.0)


def row_errors(rows: pd.DataFrame, quantiles: list[float], levels: list[float]) -> pd.DataFrame:
    """Per evaluated row (columns y, mean, q..., scale, scale2): e, abs_scaled, sq_scaled,
    pinball_<tau> (scaled), crps (2 x mean scaled pinball over the levels, an approximation
    of the CRPS), cover_<level> (1 if y lies in the central interval), rhit_<tau> and
    rcover_<level> (randomised PIT, pit_hits)."""
    out = pd.DataFrame(index=rows.index)
    y = rows["y"].to_numpy(float)
    scale = rows["scale"].where(rows["scale"] > 0).to_numpy(float)
    scale2 = rows["scale2"].where(rows["scale2"] > 0).to_numpy(float)
    e = y - rows["mean"].to_numpy(float)
    out["e"] = e
    out["abs_scaled"] = np.abs(e) / scale
    out["sq_scaled"] = e**2 / scale2
    for tau in quantiles:
        out[f"pinball_{tau:g}"] = pinball(y, rows[qcol(tau)], tau) / scale
    out["crps"] = 2 * out[[f"pinball_{tau:g}" for tau in quantiles]].mean(axis=1, skipna=False)
    for level in levels:
        lo, hi = interval(level)
        inside = (rows[qcol(lo)].to_numpy(float) <= y) & (y <= rows[qcol(hi)].to_numpy(float))
        out[f"cover_{level:g}"] = inside.astype(float)
    hits = pit_hits(y, rows[[qcol(t) for t in quantiles]].to_numpy(float), quantiles)
    for k, tau in enumerate(quantiles):
        out[f"rhit_{tau:g}"] = hits[:, k]
    for level in levels:
        lo, hi = interval(level)
        if lo in quantiles and hi in quantiles:
            k_lo, k_hi = list(quantiles).index(lo), list(quantiles).index(hi)
            out[f"rcover_{level:g}"] = hits[:, k_hi] - hits[:, k_lo]
    return out


def _wmean(x: pd.Series, w: pd.Series) -> float:
    ok = x.notna() & w.notna()
    if not ok.any() or w[ok].sum() <= 0:
        return float("nan")
    return float(np.average(x[ok], weights=w[ok]))


def aggregate(rows: pd.DataFrame, err: pd.DataFrame, weighted: bool) -> dict:
    """Metrics over the rows of one group; weighted = by the `weight` column of rows (revenue).
    MASE = mean |e|/scale, RMSSE = sqrt(mean e^2/scale2), bias = sum(e)/sum(y)."""
    w = rows["weight"] if weighted else pd.Series(1.0, index=rows.index)
    y = rows["y"]
    out = {
        "mase": _wmean(err["abs_scaled"], w),
        "rmsse": float(np.sqrt(_wmean(err["sq_scaled"], w))),
        "bias": float((w * err["e"]).sum() / (w * y).sum()) if (w * y).sum() > 0 else float("nan"),
        "crps": _wmean(err["crps"], w),
    }
    for col in err.columns:
        if col.startswith(("pinball_", "cover_", "rhit_", "rcover_")):
            out[col] = _wmean(err[col], w)
    return out


def paired_bootstrap(
    a: pd.Series,
    b: pd.Series,
    weights: pd.Series | None = None,
    n: int = 2000,
    level: float = 0.95,
    seed: int = 0,
) -> dict:
    """CI of the (weighted) mean of a - b over series, resampling series with replacement.
    a, b, weights: one value per series, aligned on the index; series missing in either are
    dropped. significant = the interval excludes 0."""
    d = pd.concat({"a": a, "b": b}, axis=1).dropna()
    w = np.ones(len(d)) if weights is None else weights.reindex(d.index).fillna(0).to_numpy(float)
    diff = (d["a"] - d["b"]).to_numpy(float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(d), size=(n, len(d)))
    ws = w[idx]
    with np.errstate(invalid="ignore", divide="ignore"):
        boot = (diff[idx] * ws).sum(axis=1) / ws.sum(axis=1)
    lo, hi = np.nanquantile(boot, [(1 - level) / 2, 1 - (1 - level) / 2])
    mean = float(np.average(diff, weights=w)) if w.sum() > 0 else float("nan")
    return {
        "diff": mean,
        "lo": float(lo),
        "hi": float(hi),
        "n_series": len(d),
        "significant": bool(lo > 0 or hi < 0),
    }
