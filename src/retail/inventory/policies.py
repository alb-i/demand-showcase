"""Order-up-to levels S_t of the periodic-review policies.

Every function returns a product x review-week frame of S_t that uses only the weeks before the
review week t (the units matrix is cut at t, the quantile policy reads the forecasts of origin
t). K = L + R is the number of weeks an order has to cover.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm

from retail.metrics import qcol


def _known(wide: pd.DataFrame, t: pd.Timestamp) -> np.ndarray:
    """Units of the open weeks before t (NaN = closed or before the first sale)."""
    return wide.loc[:, wide.columns < t].to_numpy(float)


def last_mean(values: np.ndarray, window: int) -> np.ndarray:
    """Per row: mean of the last `window` non-NaN values (NaN if there are none)."""
    out = np.full(len(values), np.nan)
    for i, row in enumerate(values):
        v = row[~np.isnan(row)][-window:]
        if len(v):
            out[i] = v.mean()
    return out


def ma_errors(values: np.ndarray, window: int, last: int) -> np.ndarray:
    """Per row: RMS of the one-step errors y_u - mean(previous `window` open weeks) over the
    last `last` open weeks that have a full window before them (NaN if none)."""
    out = np.full(len(values), np.nan)
    for i, row in enumerate(values):
        v = row[~np.isnan(row)]
        if len(v) <= window:
            continue
        csum = np.concatenate([[0.0], np.cumsum(v)])
        ma = (csum[window:-1] - csum[: -window - 1]) / window  # mean of v[u-window:u], u >= window
        e = (v[window:] - ma)[-last:]
        out[i] = np.sqrt(np.mean(e**2))
    return out


def naive_levels(wide: pd.DataFrame, weeks, k: int, buffer: float, window: int = 4) -> pd.DataFrame:
    """P-naive, the spreadsheet rule: S_t = K x mean of the last `window` weeks x (1 + buffer)."""
    cols = {t: k * last_mean(_known(wide, t), window) * (1 + buffer) for t in weeks}
    return pd.DataFrame(cols, index=wide.index).fillna(0.0)


def normal_levels(wide: pd.DataFrame, weeks, k: int, alpha: float, window: int = 4,
                  sigma_weeks: int = 52) -> pd.DataFrame:  # fmt: skip
    """P-normal: S_t = K mu + z_alpha sigma sqrt(K), mu = MA(window), sigma = RMS of its one-step
    errors over the last `sigma_weeks` open weeks (independent normal weeks), clipped at 0."""
    z = norm.ppf(alpha)
    cols = {}
    for t in weeks:
        v = _known(wide, t)
        mu = last_mean(v, window)
        sigma = np.nan_to_num(ma_errors(v, window, sigma_weeks))
        cols[t] = np.maximum(k * mu + z * sigma * np.sqrt(k), 0.0)
    return pd.DataFrame(cols, index=wide.index).fillna(0.0)


def quantile_levels(path_rows: pd.DataFrame, codes, weeks, k: int, tau: float) -> pd.DataFrame:
    """P-quantile: S_t = tau-quantile of the K-week path sum of origin t (rows of
    retail.paths.horizon_sums, method paths, h = K). Missing (product, week): NaN."""
    r = path_rows[path_rows["h"] == k]
    s = r.pivot_table(index="stock_code", columns="origin", values=qcol(tau), aggfunc="first")
    return s.reindex(index=pd.Index(codes, name="stock_code"), columns=list(weeks))
