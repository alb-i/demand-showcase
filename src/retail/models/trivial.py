"""Trivial model for the pipeline check: the same forecast for every horizon, the mean
and the empirical quantiles of the last `window` known weeks of each product (not one of the
baselines)."""

import numpy as np
import pandas as pd

from retail.backtest import History
from retail.metrics import qcol


class Trivial:
    name = "trivial"

    def __init__(self, window: int = 52):
        self.window = window

    def predict(
        self, history: History, skus: pd.Index, horizons: list[int], quantiles: list[float]
    ) -> pd.DataFrame:
        v = history.units.loc[skus].to_numpy(float)
        last = np.full((len(skus), self.window), np.nan)
        for i, row in enumerate(v):
            known = row[~np.isnan(row)][-self.window :]
            last[i, : len(known)] = known
        base = pd.DataFrame({"stock_code": skus, "mean": np.nanmean(last, axis=1)})
        qs = np.nanquantile(last, quantiles, axis=1)
        for tau, q in zip(quantiles, qs, strict=True):
            base[qcol(tau)] = q
        return pd.concat([base.assign(h=h) for h in horizons], ignore_index=True)
