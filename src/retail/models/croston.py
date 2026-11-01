"""Intermittent-demand methods (experiment E2): Croston, SBA, TSB.

All three smooth over the known weeks of a series (NaN = before the first sale or a closed week,
skipped) and give a flat forecast for every horizon:
  croston  z = demand size, p = interval in open weeks between demands, both updated only in
           weeks with demand (smoothing alpha); forecast z / p
  sba      Syntetos-Boylan approximation: croston x (1 - alpha / 2) (removes Croston's bias)
  tsb      Teunter-Syntetos-Babai: z updated in weeks with demand (alpha), the demand
           probability p updated every known week towards 1 (demand) or 0 (none) (beta);
           forecast p x z, so the forecast decays while a product does not sell
Initialisation at the first demand: z = its size, p = its interval (croston, sba; 1 when the
series starts with a sale) or 1 (tsb). Before the first demand the forecast is 0.
Intervals as for the baselines: pooled scaled h-step residuals per segment.
"""

import numpy as np
import pandas as pd

from retail.models.baselines import Baseline

METHODS = ("croston", "sba", "tsb")


def intermittent_matrix(
    units: pd.DataFrame, method: str, alpha: float, beta: float | None = None
) -> pd.DataFrame:
    """Column j = the forecast made at origin j from the columns < j (flat over horizons)."""
    if method not in METHODS:
        raise ValueError(f"method must be one of {METHODS}")
    beta = alpha if beta is None else beta
    v = units.to_numpy(dtype=float)
    n, t = v.shape
    z = np.full(n, np.nan)  # smoothed demand size
    p = np.full(n, np.nan)  # croston/sba: smoothed interval; tsb: demand probability
    q = np.zeros(n)  # open weeks since the last demand (croston/sba)
    out = np.full((n, t), np.nan)
    for j in range(t):
        if method == "tsb":
            out[:, j] = p * z
        else:
            out[:, j] = z / p * ((1 - alpha / 2) if method == "sba" else 1.0)
        y = v[:, j]
        known = ~np.isnan(y)
        demand = known & (y > 0)
        first = demand & np.isnan(z)
        later = demand & ~first
        if method == "tsb":
            started = known & ~np.isnan(z) & ~first
            p[started] += beta * (demand[started] - p[started])
            p[first] = 1.0
        else:
            q[known] += 1
            p[first] = q[first]
            p[later] += alpha * (q[later] - p[later])
            q[demand] = 0
        z[later] += alpha * (y[later] - z[later])
        z[first] = y[first]
    return pd.DataFrame(out, index=units.index, columns=units.columns)


class Intermittent(Baseline):
    def __init__(
        self,
        method: str,
        alpha: float = 0.1,
        beta: float | None = None,
        residual_weeks: int = 52,
        min_pool: int = 100,
        segments: pd.Series | None = None,
    ):
        if method not in METHODS:
            raise ValueError(f"method must be one of {METHODS}")
        super().__init__("naive", 1, residual_weeks, min_pool, segments)
        self.method, self.alpha = method, alpha
        self.beta = alpha if beta is None else beta
        self.name = f"{method}-a{alpha:g}" + (f"-b{self.beta:g}" if method == "tsb" else "")

    def points(self, units: pd.DataFrame, h: int) -> pd.DataFrame:
        return intermittent_matrix(units, self.method, self.alpha, self.beta)
