"""Statistical models per series (experiment E3): ETS and auto-ARIMA via
statsforecast, on item demand with a separate bulk part.

Item part: the model is fitted per series to its known item weeks (units - units_bulk; weeks
before the first sale and closed weeks dropped, so a closed week does not count as a step),
non-seasonal (season_length 1: at most ~1.5 years of history before the tuning origins, too
little for a 52-week season). Series the model cannot fit fall back to statsforecast's Naive;
explosive fits (mean or sigma not finite or above 100 x the largest known week) to the mean /
std of the known weeks.
Its own prediction interval gives a Gaussian per horizon: mean mu_h, sigma_h = (hi95 - mu_h) /
1.96.
Bulk part: the empirical distribution of the series' last `bulk_weeks` known weeks of bulk
units (its mean is the MA(52) bulk rate of E2b); bulk_weeks 0 = no bulk part.
Forecast: mean = max(mu_h, 0) + mean bulk; quantiles of item + bulk (independent) from the
mixture CDF F(s) = mean_k Phi((s - mu_h - b_k) / sigma_h), clipped at 0. Quantiles do not add
up, so they are not summed.
"""

import warnings

import numpy as np
import pandas as pd
from scipy.special import ndtr, ndtri

from retail.backtest import History
from retail.metrics import qcol
from retail.models.split import bulk_units

MODELS = ("ets", "arima")
Z95 = float(ndtri(0.975))


def mixture_quantiles(
    mu: np.ndarray, sigma: np.ndarray, bulk: np.ndarray, taus, iterations: int = 60
) -> np.ndarray:
    """Quantiles (n x H x T) of N(mu, sigma^2) + B, B uniform over the non-NaN values of each
    row of bulk (n x W); rows without bulk values or only zeros: plain normal quantiles."""
    taus = np.asarray(taus, dtype=float)
    z = ndtri(taus)
    n, horizons = mu.shape
    sigma = np.maximum(sigma, 1e-9 * (1 + np.abs(mu)))
    out = mu[:, :, None] + sigma[:, :, None] * z[None, None, :]
    has = np.nan_to_num(bulk, nan=0.0).any(axis=1)
    if not has.any():
        return out
    b = bulk[has]
    m, s = mu[has][:, :, None, None], sigma[has][:, :, None, None]
    bb = b[:, None, None, :]
    valid = ~np.isnan(bb)
    count = valid.sum(axis=-1)
    lo = (mu[has] + np.nanmin(b, axis=1)[:, None])[:, :, None] - 8 * sigma[has][:, :, None]
    hi = (mu[has] + np.nanmax(b, axis=1)[:, None])[:, :, None] + 8 * sigma[has][:, :, None]
    lo = np.broadcast_to(lo, (len(b), horizons, len(taus))).copy()
    hi = np.broadcast_to(hi, (len(b), horizons, len(taus))).copy()
    for _ in range(iterations):
        mid = (lo + hi) / 2
        cdf = np.where(valid, ndtr((mid[..., None] - m - bb) / s), 0.0).sum(axis=-1) / count
        below = cdf < taus[None, None, :]
        lo = np.where(below, mid, lo)
        hi = np.where(below, hi, mid)
    out[has] = (lo + hi) / 2
    return out


def guard_explosive(
    mu: np.ndarray, sigma: np.ndarray, known: np.ndarray, cap: float = 100.0
) -> tuple[np.ndarray, np.ndarray]:
    """Rows whose mean or sigma is not finite or above `cap` x (the series' largest known week
    + 1) (e.g. a non-stationary ARIMA fit) fall back to the mean and std of the known weeks,
    sigma x sqrt(h); NaN otherwise (no forecast) -> 0."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        limit = cap * (np.nan_to_num(np.nanmax(known, axis=1), nan=0.0) + 1)
        mean = np.nan_to_num(np.nanmean(known, axis=1), nan=0.0)
        std = np.nan_to_num(np.nanstd(known, axis=1), nan=0.0)
    with np.errstate(invalid="ignore"):
        bad = (~np.isfinite(mu) & ~np.isnan(mu)) | (~np.isfinite(sigma) & ~np.isnan(sigma))
        bad |= (np.abs(np.nan_to_num(mu)) > limit[:, None]) | (
            np.nan_to_num(sigma) > limit[:, None]
        )
    rows = bad.any(axis=1)
    mu, sigma = np.nan_to_num(mu, nan=0.0), np.nan_to_num(sigma, nan=0.0)
    steps = np.sqrt(np.arange(1, mu.shape[1] + 1))
    mu[rows] = mean[rows, None]
    sigma[rows] = std[rows, None] * steps[None, :]
    return mu, sigma


class StatsModel:
    def __init__(self, model: str = "ets", bulk_weeks: int = 52, segments=None):
        if model not in MODELS:
            raise ValueError(f"model must be one of {MODELS}")
        self.model, self.bulk_weeks = model, bulk_weeks
        self.name = f"{model}-bulk-ma{bulk_weeks}" if bulk_weeks else model
        label = {"ets": "ETS (AutoETS)", "arima": "auto-ARIMA"}[model]
        self.description = (
            f"{label} per series on item demand, non-seasonal, with its own Gaussian intervals"
            + (
                f"; plus bulk demand = the last {bulk_weeks} weeks' bulk units (mean = their "
                "average); quantiles of the sum"
                if bulk_weeks
                else ""
            )
            + "."
        )

    def _statsforecast(self):
        from statsforecast import StatsForecast
        from statsforecast.models import AutoARIMA, AutoETS, Naive

        m = AutoETS(season_length=1) if self.model == "ets" else AutoARIMA(season_length=1)
        return StatsForecast(models=[m], freq=1, n_jobs=1, fallback_model=Naive())

    def item_forecast(self, item: pd.DataFrame, horizon: int) -> tuple[np.ndarray, np.ndarray]:
        """mu and sigma (series x horizon) of the model fitted to each row's known weeks."""
        long = item.stack(future_stack=True).dropna().rename("y").reset_index()
        long.columns = ["unique_id", "week", "y"]
        long["ds"] = long.groupby("unique_id").cumcount()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fc = self._statsforecast().forecast(df=long[["unique_id", "ds", "y"]], h=horizon,
                                                level=[95])  # fmt: skip
        col = fc.columns[2]
        fc["step"] = fc.groupby("unique_id").cumcount()
        mu = fc.pivot(index="unique_id", columns="step", values=col).reindex(item.index)
        hi = fc.pivot(index="unique_id", columns="step", values=f"{col}-hi-95").reindex(item.index)
        mu, hi = mu.to_numpy(float), hi.to_numpy(float)
        with np.errstate(all="ignore"):
            sigma = ((hi - mu) / Z95).clip(min=0)
        return guard_explosive(mu, sigma, item.to_numpy(float))

    def predict(
        self, history: History, skus: pd.Index, horizons: list[int], quantiles: list[float]
    ) -> pd.DataFrame:
        units = history.units.loc[skus]
        if self.bulk_weeks:
            bulk = bulk_units(history, units)
            recent = np.full((len(units), self.bulk_weeks), np.nan)
            for i, row in enumerate(bulk.to_numpy(float)):
                known = row[~np.isnan(row)][-self.bulk_weeks :]
                recent[i, : len(known)] = known
        else:
            bulk = units * 0.0
            recent = np.full((len(units), 1), np.nan)
        mu, sigma = self.item_forecast(units - bulk, max(horizons))
        q = mixture_quantiles(mu, sigma, recent, quantiles)
        known = ~np.isnan(recent)
        bulk_mean = np.where(known, recent, 0.0).sum(axis=1) / np.maximum(known.sum(axis=1), 1)
        out = []
        for h in horizons:
            frame = pd.DataFrame(np.clip(q[:, h - 1, :], 0, None),
                                 columns=[qcol(t) for t in quantiles])  # fmt: skip
            frame.insert(0, "mean", np.clip(mu[:, h - 1], 0, None) + bulk_mean)
            frame.insert(0, "h", h)
            frame.insert(0, "stock_code", skus)
            out.append(frame)
        return pd.concat(out, ignore_index=True)
