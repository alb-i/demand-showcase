"""Baselines (experiment E1): naive, seasonal naive (lag 52 where
available, else naive), moving average of the last k weeks.

Point forecast at origin t for week t+h-1:
  naive     last known week before t
  snaive    the week 52 weeks before the target if known, else naive
  ma        mean of the known weeks among the last k weeks before t (closed weeks skipped)
Intervals: the method's h-step errors on the last `residual_weeks` weeks before t (as if
it had forecast from each of those weeks), divided by the series' naive scale and pooled over
all products of the same segment and horizon; quantile = point + pooled quantile x scale,
clipped at 0. A pool with fewer than `min_pool` residuals uses all products of that horizon.
"""

import numpy as np
import pandas as pd

from retail.backtest import History
from retail.metrics import naive_scale, qcol

METHODS = ("naive", "snaive", "ma")


def point_matrix(units: pd.DataFrame, method: str, window: int, h: int) -> pd.DataFrame:
    """Column j = the forecast for week j+h-1 made at origin j from the columns < j (the frame
    may have extra NaN columns at the end for the origin and the target weeks)."""
    naive = units.ffill(axis=1).shift(1, axis=1)
    if method == "naive":
        return naive
    if method == "ma":
        return units.T.rolling(window, min_periods=1).mean().T.shift(1, axis=1)
    if method == "snaive":
        return units.shift(52 - (h - 1), axis=1).fillna(naive)
    raise ValueError(f"unknown method {method!r}")


class Baseline:
    def __init__(
        self,
        method: str,
        window: int = 4,
        residual_weeks: int = 52,
        min_pool: int = 100,
        segments: pd.Series | None = None,
    ):
        if method not in METHODS:
            raise ValueError(f"method must be one of {METHODS}")
        self.method, self.window = method, window
        self.residual_weeks, self.min_pool = residual_weeks, min_pool
        self.segments = segments if segments is not None else pd.Series(dtype=str)
        self.name = f"ma{window}" if method == "ma" else method

    def predict(
        self, history: History, skus: pd.Index, horizons: list[int], quantiles: list[float]
    ) -> pd.DataFrame:
        known = history.units.loc[skus]
        n = known.shape[1]
        future = pd.date_range(history.origin, periods=max(horizons), freq="7D")
        units = known.reindex(columns=known.columns.append(future))  # NaN from the origin on
        scale = naive_scale(known)["scale"]
        fallback = known.mean(axis=1).where(lambda m: m > 0, 1.0)
        scale = scale.where(scale > 0, fallback)
        seg = self.segments.reindex(skus).fillna("unclassified").to_numpy()
        out = []
        for h in horizons:
            pred = self.points(units, h)
            actual = units.shift(-(h - 1), axis=1)  # column j = the week j+h-1
            cols = slice(max(0, n - self.residual_weeks), n)  # past origins, targets < t
            res = (actual - pred).iloc[:, cols].to_numpy(float) / scale.to_numpy()[:, None]
            qs = self._pooled_quantiles(res, seg, quantiles)
            point = pred.iloc[:, n].to_numpy(float)
            point = np.where(np.isnan(point), 0.0, point)
            q = np.clip(point[:, None] + qs * scale.to_numpy()[:, None], 0, None)
            frame = pd.DataFrame(q, columns=[qcol(t) for t in quantiles])
            frame.insert(0, "mean", point)
            frame.insert(0, "h", h)
            frame.insert(0, "stock_code", skus)
            out.append(frame)
        return pd.concat(out, ignore_index=True)

    def points(self, units: pd.DataFrame, h: int) -> pd.DataFrame:
        """Point matrix as in point_matrix (subclasses replace the method)."""
        return point_matrix(units, self.method, self.window, h)

    def _pooled_quantiles(self, res: np.ndarray, seg: np.ndarray, quantiles) -> np.ndarray:
        """Per series the quantiles of its segment's pooled residuals (rows x quantiles)."""
        everything = res[~np.isnan(res)]
        overall = (
            np.quantile(everything, quantiles) if len(everything) else np.zeros(len(quantiles))
        )
        out = np.empty((len(seg), len(quantiles)))
        for s in np.unique(seg):
            mask = seg == s
            pool = res[mask]
            pool = pool[~np.isnan(pool)]
            out[mask] = np.quantile(pool, quantiles) if len(pool) >= self.min_pool else overall
        return out
