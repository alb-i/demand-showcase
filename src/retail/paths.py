"""Sample paths and quantiles of horizon sums (experiment E7).

Quantiles do not add up: the tau-quantile of D_1 + ... + D_K is not the sum of the per-week
tau-quantiles (unless demand is perfectly correlated over the weeks). The order-up-to level
needs the quantile of the sum, so it is taken from sample paths.

Paths keep the per-week forecast distributions (the quantile curves of the model) and take the
dependence between the weeks from past forecast errors (an empirical copula, a block bootstrap
in rank space):

1. Quantile curve per (series, origin, h): piecewise linear through (tau, q_tau), extended by
   (0, 0) and (1, q_top) with q_top = q_0.99 + (q_0.99 - q_0.975) x 0.01 / 0.015 (the slope of
   the last segment).
2. Realised PIT u_h = F(y_h) of earlier origins under that curve; where y lies on a flat part
   (y = q for several levels, mostly y = q = 0), u is uniform on that part (randomised PIT).
3. Pool at origin t: the PIT vectors (u_1..u_K) of earlier origins o whose last target week
   o + (K-1) weeks is before t (no look-ahead), per segment label (fewer than `min_pool`
   vectors: all labels). Per h the pool's u are replaced by their ranks, (rank - 0.5) / n
   (ties broken at random), so every week keeps a uniform marginal and the forecast's own
   quantiles exactly; only the joint ranks (the dependence) come from the past.
4. Path j of a series: draw one pool vector, D_h = Q_h(u_h). "indep" draws u_h independently
   per week (the no-dependence extreme); "summed" adds the per-week quantiles (the shortcut).

The quantiles of the path sums are written in the backtest row format with h = K, scale
K x scale and scale2 K^2 x scale2, so the usual metrics and reports apply.
"""

import zlib

import numpy as np
import pandas as pd

from retail.metrics import qcol

METHODS = ("summed", "paths", "indep")


def knots(q: np.ndarray, taus) -> tuple[np.ndarray, np.ndarray]:
    """Knot levels (L + 2) and values (rows x L + 2) of the piecewise linear quantile curves of
    the sorted, non-negative quantiles q (rows x L)."""
    taus = np.asarray(taus, dtype=float)
    q = np.sort(np.clip(np.asarray(q, dtype=float), 0, None), axis=1)
    slope = (q[:, -1] - q[:, -2]) / (taus[-1] - taus[-2])
    top = q[:, -1] + slope * (1 - taus[-1])
    t = np.concatenate([[0.0], taus, [1.0]])
    v = np.column_stack([np.zeros(len(q)), q, top])
    return t, v


def quantile_fn(t: np.ndarray, v: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Q(u) per row: v (rows x knots) at levels u (rows x n) by linear interpolation."""
    k = np.clip(np.searchsorted(t, u, side="right"), 1, len(t) - 1)
    t0, t1 = t[k - 1], t[k]
    v0 = np.take_along_axis(v, k - 1, axis=1)
    v1 = np.take_along_axis(v, k, axis=1)
    return v0 + (u - t0) / (t1 - t0) * (v1 - v0)


def pit(
    y: np.ndarray,
    t: np.ndarray,
    v: np.ndarray,
    rng: np.random.Generator,
    draw: np.ndarray | None = None,
) -> np.ndarray:
    """Randomised PIT of y (rows) under the quantile curves: the u with Q(u) = y, uniform over
    the flat part where several knots equal y; 1 above the top knot. draw: the uniforms for
    the flat parts per row (default: fresh ones from rng)."""
    y = np.asarray(y, dtype=float)[:, None]
    n_lt = (v < y).sum(axis=1)  # knots below y
    n_le = (v <= y).sum(axis=1)  # knots at or below y
    rows = np.arange(len(v))
    out = np.ones(len(v))
    tie = n_le > n_lt
    lo, hi = t[np.minimum(n_lt, len(t) - 1)], t[np.maximum(n_le - 1, 0)]
    d = rng.uniform(size=len(v)) if draw is None else np.asarray(draw, dtype=float)
    out[tie] = lo[tie] + d[tie] * (hi[tie] - lo[tie])
    inner = ~tie & (n_lt > 0) & (n_lt < len(t))
    k = n_lt[inner]
    v0, v1 = v[rows[inner], k - 1], v[rows[inner], k]
    out[inner] = t[k - 1] + (y[inner, 0] - v0) / (v1 - v0) * (t[k] - t[k - 1])
    return out


def wide(rows: pd.DataFrame, k: int, columns) -> pd.DataFrame:
    """Rows of the (stock_code, origin) pairs evaluated at every h = 1..k, as one row each with
    the columns per h (MultiIndex columns: column x h)."""
    r = rows[rows["h"] <= k]
    w = r.pivot_table(index=["stock_code", "origin"], columns="h", values=columns, aggfunc="first")
    return w.dropna()


def pit_vectors(
    rows: pd.DataFrame, quantiles, k: int, seed: int = 0, common_ties: bool = False
) -> pd.DataFrame:
    """PIT vectors u1..uk per (stock_code, origin) evaluated at every h = 1..k. common_ties
    (E7b): one uniform per vector for the flat parts of all weeks, so weeks that tie (mostly
    y = q = 0) keep their joint position; else a fresh uniform per week."""
    cols = [qcol(t) for t in quantiles]
    w = wide(rows, k, ["y", *cols])
    rng = np.random.default_rng([seed, k])
    out = pd.DataFrame(index=w.index)
    shared = rng.uniform(size=len(w)) if common_ties else None
    for h in range(1, k + 1):
        t, v = knots(w[[(c, h) for c in cols]].to_numpy(float), quantiles)
        out[f"u{h}"] = pit(w[("y", h)].to_numpy(float), t, v, rng, shared)
    return out


def ranks(u: np.ndarray, rng: np.random.Generator, common_ties: bool = False) -> np.ndarray:
    """(rank - 0.5) / n per column, ties broken at random (common_ties: by the same random
    order in every column)."""
    n = len(u)
    out = np.empty_like(u, dtype=float)
    shared = rng.uniform(size=n)
    for j in range(u.shape[1]):
        key = shared if common_ties else rng.uniform(size=n)
        order = np.lexsort((key, u[:, j]))
        out[order, j] = (np.arange(n) + 0.5) / n
    return out


def sample_sums(
    curves: list[tuple[np.ndarray, np.ndarray]],
    pool: np.ndarray,
    n_paths: int,
    rng: np.random.Generator,
    dependent: bool = True,
) -> np.ndarray:
    """Path sums (series x n_paths): curves = per h the knots (t, v) of the series, pool = rank
    PIT vectors (n x K). dependent: one pool vector per path; else u_h drawn per week."""
    m, k = len(curves[0][1]), len(curves)
    total = np.zeros((m, n_paths))
    idx = rng.integers(len(pool), size=(m, n_paths))
    for h, (t, v) in enumerate(curves):
        if not dependent:
            idx = rng.integers(len(pool), size=(m, n_paths))
        total += quantile_fn(t, v, pool[idx, h])
    assert k == pool.shape[1]
    return total


def sample_paths(
    curves: list[tuple[np.ndarray, np.ndarray]],
    pool: np.ndarray,
    n_paths: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Weekly path values (series x n_paths x K) of the dependent method, with the same draws
    as sample_sums(..., dependent=True): their sums over K equal its sums up to rounding."""
    m = len(curves[0][1])
    idx = rng.integers(len(pool), size=(m, n_paths))
    out = np.empty((m, n_paths, len(curves)))
    for h, (t, v) in enumerate(curves):
        out[:, :, h] = quantile_fn(t, v, pool[idx, h])
    return out


def _rng(seed: int, origin: pd.Timestamp, k: int, label: str, method: str):
    return np.random.default_rng(
        [seed, origin.toordinal(), k, zlib.crc32(f"{label}|{method}".encode())]
    )


def horizon_sums(
    rows: pd.DataFrame,
    quantiles,
    ks=(2, 4, 8),
    labels: pd.Series | None = None,
    n_paths: int = 1000,
    min_pool: int = 100,
    seed: int = 0,
    common_ties: bool = False,
    out_quantiles=None,
    sampled=("paths", "indep"),
    on_paths=None,
) -> tuple[dict[str, pd.DataFrame], pd.DataFrame]:
    """Rows of the K-week sums (h = K) per method in METHODS from the evaluated backtest rows
    (stock_code, origin, h, y, mean, scale, scale2, weight, q<tau>; segment if present).
    Paths only at origins with a pool; "summed" at every origin. Returns the rows per method
    and per (origin, K) the pool size. common_ties: see pit_vectors and ranks (E7b).
    out_quantiles: levels of the sampled sums (default: `quantiles`; the inventory policies need
    a finer grid);
    sampled: the sampled methods to compute (each has its own seeded stream, so leaving one out
    does not change the other). on_paths(origin, k, codes, paths): called with the weekly path
    values (series x n_paths x K, sample_paths) of the method "paths" per origin and pool label
    (to store them); the sums are then taken from these values."""
    cols = [qcol(t) for t in quantiles]
    out_q = list(quantiles if out_quantiles is None else out_quantiles)
    out_cols = [qcol(t) for t in out_q]
    lab = (lambda c: c.map(labels).fillna("unclassified")) if labels is not None else (
        lambda c: pd.Series("all", index=c.index))  # fmt: skip
    out = {m: [] for m in METHODS}
    info = []
    for k in ks:
        w = wide(rows, k, ["y", "mean", *cols])
        base = rows[rows["h"] == 1].set_index(["stock_code", "origin"])
        extra = [c for c in ("scale", "scale2", "weight", "segment") if c in base]
        head = pd.DataFrame(
            {"y": w["y"].sum(axis=1), "mean": w["mean"].sum(axis=1)}, index=w.index
        ).join(base[extra])
        head["scale"] = head["scale"] * k
        head["scale2"] = head["scale2"] * k**2
        summed = head.copy()
        for c in cols:
            summed[c] = w[c].sum(axis=1)
        summed[cols] = np.sort(summed[cols].to_numpy(float), axis=1)
        out["summed"].append(summed.reset_index().assign(h=k))
        vec = pit_vectors(rows, quantiles, k, seed, common_ties)
        vec_origin = vec.index.get_level_values("origin")
        vec_label = lab(pd.Series(vec.index.get_level_values("stock_code"), index=vec.index))
        last_target = vec_origin + pd.Timedelta(weeks=k - 1)
        for origin, part in w.groupby(level="origin", sort=True):
            ok = np.asarray(last_target < origin)
            info.append({"origin": origin, "k": k, "n_pool": int(ok.sum())})
            if not ok.any():
                continue
            codes = pd.Series(part.index.get_level_values("stock_code"), index=part.index)
            part_label = lab(codes)
            res = {m: [] for m in sampled}
            for label, idx in part.groupby(part_label.to_numpy()).groups.items():
                sel = ok & np.asarray(vec_label == label)
                if sel.sum() < min_pool:
                    sel = ok
                for method in res:
                    rng = _rng(seed, origin, k, label, method)
                    u = vec[sel][[f"u{h}" for h in range(1, k + 1)]].to_numpy()
                    pool = ranks(u, rng, common_ties)
                    g = part.loc[idx]
                    curves = [knots(g[[(c, h) for c in cols]].to_numpy(float), quantiles)
                              for h in range(1, k + 1)]  # fmt: skip
                    if on_paths is not None and method == "paths":
                        vals = sample_paths(curves, pool, n_paths, rng)
                        on_paths(origin, k, g.index.get_level_values("stock_code"), vals)
                        sums = vals.sum(axis=2)
                    else:
                        sums = sample_sums(curves, pool, n_paths, rng, method == "paths")
                    qs = np.quantile(sums, out_q, axis=1).T
                    res[method].append(pd.DataFrame(qs, index=g.index, columns=out_cols))
            for method, frames in res.items():
                q = pd.concat(frames)
                out[method].append(head.loc[q.index].join(q).reset_index().assign(h=k))
    frames = {m: pd.concat(v, ignore_index=True) for m, v in out.items() if v}
    return frames, pd.DataFrame(info)


def overstatement(summed: pd.DataFrame, paths: pd.DataFrame, quantiles) -> pd.DataFrame:
    """Per K and tau: median and revenue-weighted ratio of the summed quantile to the path
    quantile (rows where the path quantile is > 0)."""
    key = ["stock_code", "origin", "h"]
    m = summed.merge(paths, on=key, suffixes=("_s", "_p"))
    recs = []
    for k, g in m.groupby("h"):
        for t in quantiles:
            c = qcol(t)
            pos = g[f"{c}_p"] > 0
            r = g.loc[pos, f"{c}_s"] / g.loc[pos, f"{c}_p"]
            w = g.loc[pos, "weight_s"] if "weight_s" in g else None
            wsum = (g.loc[pos, f"{c}_s"] * w).sum() / (g.loc[pos, f"{c}_p"] * w).sum() if (
                w is not None) else float("nan")  # fmt: skip
            recs.append({"K": int(k), "tau": t, "n": int(pos.sum()),
                         "median_ratio": float(r.median()) if len(r) else float("nan"),
                         "weighted_ratio": float(wsum)})  # fmt: skip
    return pd.DataFrame(recs)
