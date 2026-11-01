"""Rolling conformal calibration of quantile forecasts (experiment E6).

Per quantile level (CQR per level): at origin t, the calibration set holds the evaluated rows of
earlier origins o (within the last `window_weeks` weeks) whose target week o + (h-1) weeks is
before t, so their actuals were known at t (no look-ahead). Score s = (y - q_tau) / scale
(scale: the row's naive scale). The offset of (label, h, tau) is the conformal tau-quantile of
its scores, the ceil((n+1) tau)-th smallest; a pool with fewer than `min_pool` scores uses all
labels of that h, no score at all: offset 0. Calibrated q_tau = q_tau + offset x scale, then
clipped at 0 and sorted per row (no crossing). The offsets always come from the uncalibrated
quantiles of the earlier origins.
"""

import math

import numpy as np
import pandas as pd

from retail.metrics import qcol


def target_week(rows: pd.DataFrame) -> pd.Series:
    return rows["origin"] + pd.to_timedelta((rows["h"] - 1) * 7, unit="D")


def conformal_quantile(scores: np.ndarray, tau: float) -> float:
    """The ceil((n+1) tau)-th smallest score (clamped to 1..n); 0 without scores."""
    s = np.sort(scores[np.isfinite(scores)])
    if len(s) == 0:
        return 0.0
    k = min(max(math.ceil((len(s) + 1) * tau), 1), len(s))
    return float(s[k - 1])


def offsets(cal: pd.DataFrame, quantiles, min_pool: int = 100) -> pd.DataFrame:
    """Offsets (scaled units) per (label, h) x tau from calibration rows with columns label, h,
    y, scale, q<tau>; pools below min_pool fall back to all labels of the same h (index label
    '*')."""
    ok = cal[cal["scale"] > 0]
    out = {}
    for h, g in ok.groupby("h"):
        everything = {t: conformal_quantile(((g["y"] - g[qcol(t)]) / g["scale"]).to_numpy(), t)
                      for t in quantiles}  # fmt: skip
        out[("*", h)] = everything
        for label, gl in g.groupby("label"):
            if len(gl) < min_pool:
                out[(label, h)] = everything
                continue
            s = {t: ((gl["y"] - gl[qcol(t)]) / gl["scale"]).to_numpy() for t in quantiles}
            out[(label, h)] = {t: conformal_quantile(s[t], t) for t in quantiles}
    idx = pd.MultiIndex.from_tuples(list(out), names=["label", "h"])
    return pd.DataFrame(list(out.values()), index=idx, columns=list(quantiles))


def apply_offsets(rows: pd.DataFrame, off: pd.DataFrame, quantiles) -> pd.DataFrame:
    """Rows (label, h, scale, q<tau>) with q_tau + offset x scale, clipped at 0, sorted; rows
    whose (label, h) has no offset use (*, h), none at all: unchanged."""
    cols = [qcol(t) for t in quantiles]
    out = rows.copy()
    if off.empty:
        return out
    key = pd.MultiIndex.from_arrays([out["label"], out["h"]])
    d = off.reindex(key).to_numpy(float)
    fallback = off.reindex(pd.MultiIndex.from_arrays([["*"] * len(out), out["h"]])).to_numpy()
    d = np.where(np.isnan(d), fallback, d)
    d = np.nan_to_num(d, nan=0.0)
    scale = out["scale"].where(out["scale"] > 0, 0.0).fillna(0.0).to_numpy(float)[:, None]
    q = out[cols].to_numpy(float) + d * scale
    out[cols] = np.sort(np.clip(q, 0, None), axis=1)
    return out


def calibrate(
    rows: pd.DataFrame,
    quantiles,
    labels: pd.Series | None = None,
    window_weeks: int = 13,
    min_pool: int = 100,
    targets: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Calibrated copy of `targets` (default: `rows`), origin by origin, from the evaluated
    `rows` (stock_code, origin, h, y, scale, q<tau>) of earlier origins. labels: stock_code ->
    pool label (None: one pool). `targets` may be the forecasts (stock_code, origin, h, q...;
    their scale comes from the rows of the same stock_code and origin). Returns the calibrated
    frame and per origin the number of calibration rows."""

    def label(df):
        if labels is None:
            return pd.Series("all", index=df.index)
        return df["stock_code"].map(labels).fillna("unclassified")

    src = rows.assign(label=label(rows), target=target_week(rows))
    tgt = rows if targets is None else targets
    if "scale" not in tgt:
        sc = rows.groupby(["stock_code", "origin"])["scale"].first().rename("scale")
        tgt = tgt.join(sc, on=["stock_code", "origin"])
    tgt = tgt.assign(label=label(tgt))
    parts, info = [], []
    for origin, part in tgt.groupby("origin", sort=True):
        start = origin - pd.Timedelta(weeks=window_weeks)
        cal = src[(src["origin"] >= start) & (src["origin"] < origin) & (src["target"] < origin)]
        off = offsets(cal, quantiles, min_pool) if len(cal) else pd.DataFrame()
        parts.append(apply_offsets(part, off, quantiles))
        info.append({"origin": origin, "n_cal": len(cal)})
    out = pd.concat(parts).loc[tgt.index].drop(columns="label")
    if targets is not None and "scale" not in targets:
        out = out.drop(columns="scale")
    return out, pd.DataFrame(info)
