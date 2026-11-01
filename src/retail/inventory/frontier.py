"""Operating points and trade-off frontiers of the policy grids."""

import numpy as np
import pandas as pd


def match(grid: pd.DataFrame, fill_rate: float) -> pd.Series | None:
    """The grid row (columns value, fill_rate, ...) with the smallest value whose fill rate is
    >= fill_rate; None if no value reaches it."""
    ok = grid[grid["fill_rate"] >= fill_rate - 1e-12].sort_values("value")
    return ok.iloc[0] if len(ok) else None


def at_fill_rate(grid: pd.DataFrame, fill_rate: float, column: str) -> float:
    """`column` linearly interpolated along the frontier (grid sorted by fill rate) at
    fill_rate; NaN outside the range of the grid."""
    g = grid.sort_values("fill_rate")
    x, y = g["fill_rate"].to_numpy(float), g[column].to_numpy(float)
    if len(x) == 0 or fill_rate < x[0] or fill_rate > x[-1]:
        return float("nan")
    return float(np.interp(fill_rate, x, y))


def bootstrap_totals(a: pd.DataFrame, b: pd.DataFrame, n: int = 2000, level: float = 0.95,
                     seed: int = 0) -> dict:  # fmt: skip
    """Paired bootstrap over products of the differences a - b of the totals: fill rate
    (sum served / sum demand), average stock value and total cost (sums). a, b: per-product KPIs
    (retail.inventory.simulate.kpis) of two policies on the same products. Per KPI: the
    difference on all products and the percentile interval."""
    idx = a.index.intersection(b.index)
    a, b = a.loc[idx], b.loc[idx]
    rng = np.random.default_rng(seed)
    draw = rng.integers(0, len(idx), size=(n, len(idx)))

    def stats(x: pd.DataFrame, rows) -> dict:
        served, dem = x["served"].to_numpy()[rows], x["demand"].to_numpy()[rows]
        return {"fill_rate": served.sum(axis=-1) / dem.sum(axis=-1),
                "avg_stock_value": x["avg_stock_value"].to_numpy()[rows].sum(axis=-1),
                "total_cost": x["total_cost"].to_numpy()[rows].sum(axis=-1)}  # fmt: skip

    full = np.arange(len(idx))
    sa, sb = stats(a, full), stats(b, full)
    ba, bb = stats(a, draw), stats(b, draw)
    out = {}
    for k in sa:
        d = ba[k] - bb[k]
        lo, hi = np.quantile(d, [(1 - level) / 2, 1 - (1 - level) / 2])
        out[k] = {"diff": float(sa[k] - sb[k]), "lo": float(lo), "hi": float(hi),
                  "significant": bool(lo > 0 or hi < 0)}  # fmt: skip
    return out
