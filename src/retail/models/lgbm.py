"""Global LightGBM model (experiment E4).

One model over all products of the history, refitted at every origin t (expanding window).
A training row is (product i, past origin j, horizon h) with a known target week j+h-1 < t; its
features use only the weeks < j, so the same code builds the rows of the forecast (j = t).
Rows of all horizons h = 1..H are stacked, h is a feature.

Target (`target`):
  item   item demand (units - units_bulk); a bulk part per product (default MA(52),
         as in the split model) is added to the point forecast
  total  total demand directly (no bulk part; the bulk features stay)
Scaling: target and demand features are divided by the series' mean target demand of
the last `scale_weeks` known weeks before j (fallback: mean of all known weeks before j, then
1); the prediction is multiplied back. Point objective: Tweedie (DEFAULT_PARAMS).

Features at origin j (FEATURES): lags 1-8 and 52; rolling mean / std / share of zero weeks;
weeks since launch and known weeks; week of year and weeks to Christmas of the target week
(distance to the Christmas closure); relative price = last known weekly median price / the
product's median price before j; segment recomputed at j (ABC by revenue of the 52 weeks
before j, Syntetos-Boylan class of the target demand of those weeks; fixed segments
would look ahead at tuning origins); bulk history; product category.

Intervals (pooled): a second model is fitted with cut-off c = t - `oos_weeks` (only
targets < c) and forecasts from the origins c..t-1; its errors on the known weeks < t are
genuine out-of-sample h-step errors. They are scaled by the series' naive scale and pooled per
segment label and h; quantile = point + pooled quantile x scale, clipped at 0.

Quantile models (`quantile_models: true`; experiment E5; total target only, since item and
bulk quantiles would not add up): instead of the pooled errors, one LightGBM model per level tau
with the pinball (quantile) objective on the same scaled rows and features; the predictions are
multiplied back by the scale, clipped at 0 and sorted per row so that the quantiles do not cross.
The mean stays the Tweedie model's forecast. No second (out-of-sample) fit.
"""

import numpy as np
import pandas as pd

from retail.backtest import History
from retail.categories import OTHER
from retail.metrics import qcol
from retail.models.baselines import Baseline
from retail.models.split import bulk_units, part_model

TARGETS = ("item", "total")
LAGS = (1, 2, 3, 4, 5, 6, 7, 8, 52)
SB = {"smooth": 0, "erratic": 1, "intermittent": 2, "lumpy": 3}
DEFAULT_PARAMS = {
    "objective": "tweedie",
    "tweedie_variance_power": 1.5,
    "num_leaves": 31,
    "learning_rate": 0.05,
    "min_data_in_leaf": 50,
    "feature_fraction": 0.8,
    "bagging_fraction": 0.8,
    "bagging_freq": 1,
    "lambda_l2": 1.0,
    "seed": 0,
    "deterministic": True,
    "force_col_wise": True,
    "num_threads": 1,  # one per worker process (--jobs)
    "verbose": -1,
}
CATEGORICAL = ("category", "abc", "sb_class")
FEATURES = (
    "h",
    *[f"lag{k}" for k in LAGS],
    "mean4", "mean26", "mean52", "std13", "std52", "zero13", "zero52",
    "log_scale", "age", "known",
    "woy", "to_xmas", "rel_price",
    "abc", "sb_class", "adi52", "cv2_52",
    "bulk_share52", "bulk_weeks52", "since_bulk", "bulk_mean52",
    "category",
)  # fmt: skip


def past(m: np.ndarray, window: int | None, how: str, min_periods: int = 1) -> np.ndarray:
    """Column j = the rolling (window None: expanding) statistic of the columns < j; NaN cells
    are skipped (pandas rolling)."""
    df = pd.DataFrame(m.T)
    r = df.expanding(min_periods) if window is None else df.rolling(window, min_periods)
    return getattr(r, how)().shift(1).to_numpy().T


def _abc(revenue52: np.ndarray, a: float = 0.80, b: float = 0.95) -> np.ndarray:
    """ABC code per cell from each column's revenue: 0 = A (top `a` of the cumulative share),
    1 = B (next up to `b`), 2 = C; columns without revenue: NaN."""
    out = np.full(revenue52.shape, np.nan)
    r = np.nan_to_num(revenue52, nan=0.0)
    for j in range(r.shape[1]):
        total = r[:, j].sum()
        if total <= 0:
            continue
        order = np.argsort(-r[:, j], kind="stable")
        before = (np.cumsum(r[order, j]) - r[order, j]) / total  # share before this product
        code = np.where(before < a, 0.0, np.where(before < b, 1.0, 2.0))
        code[r[order, j] <= 0] = 2.0
        out[order, j] = code
    return out


def _sb_class(y: np.ndarray, window: int = 52, adi_cut=1.32, cv2_cut=0.49):
    """ADI, CV^2 of the non-zero sizes and the Syntetos-Boylan code over the `window` weeks
    before each column (NaN without demand)."""
    known = past(np.isfinite(y).astype(float), window, "sum")
    pos = np.where(np.isfinite(y), y > 0, np.nan).astype(float)
    nz = past(pos, window, "sum")
    s1 = past(np.where(y > 0, y, 0.0), window, "sum")
    s2 = past(np.where(y > 0, y**2, 0.0), window, "sum")
    with np.errstate(invalid="ignore", divide="ignore"):
        adi = np.where(nz > 0, known / nz, np.nan)
        mean = s1 / nz
        var = np.maximum(s2 / nz - mean**2, 0.0)
        cv2 = np.where(nz > 0, var / mean**2, np.nan)
    code = np.where(adi < adi_cut, np.where(cv2 < cv2_cut, 0.0, 1.0),
                    np.where(cv2 < cv2_cut, 2.0, 3.0))  # fmt: skip
    return adi, cv2, np.where(np.isnan(adi), np.nan, code)


def origin_features(
    y: np.ndarray,
    units: np.ndarray,
    bulk: np.ndarray,
    revenue: np.ndarray | None,
    price: np.ndarray | None,
    category: np.ndarray,
    scale_weeks: int = 13,
) -> dict[str, np.ndarray]:
    """Per-origin features (products x origins; origin column j uses the columns < j only).
    The inputs have one column per week before the forecast origin plus one empty (NaN)
    column for it. Also returns 'scale' and 'started' (a known week before j)."""
    f: dict[str, np.ndarray] = {}
    p, c = y.shape
    known = past(np.isfinite(y).astype(float), None, "sum")
    known = np.nan_to_num(known, nan=0.0)
    started = known > 0
    recent = past(y, scale_weeks, "mean")
    overall = past(y, None, "mean")
    scale = np.where(recent > 0, recent, np.where(overall > 0, overall, 1.0))
    f["scale"], f["started"] = scale, started
    for k in LAGS:
        lag = np.full_like(y, np.nan)
        if k < c:
            lag[:, k:] = y[:, :-k]
        f[f"lag{k}"] = lag / scale
    for w in (4, 26, 52):
        f[f"mean{w}"] = past(y, w, "mean") / scale
    for w in (13, 52):
        f[f"std{w}"] = past(y, w, "std", 2) / scale
        zero = np.where(np.isfinite(y), y == 0, np.nan).astype(float)
        f[f"zero{w}"] = past(zero, w, "mean")
    f["log_scale"] = np.log1p(scale)
    first = np.where(np.isfinite(y).any(axis=1), np.argmax(np.isfinite(y), axis=1), c)
    f["age"] = np.where(started, np.arange(c)[None, :] - first[:, None], np.nan)
    f["known"] = known
    if price is not None:
        last = pd.DataFrame(price).ffill(axis=1).shift(1, axis=1).to_numpy()
        med = past(price, None, "median")
        with np.errstate(invalid="ignore", divide="ignore"):
            f["rel_price"] = np.where(med > 0, last / med, np.nan)
    else:
        f["rel_price"] = np.full_like(y, np.nan)
    f["abc"] = _abc(past(revenue, 52, "sum")) if revenue is not None else np.full_like(y, np.nan)
    f["adi52"], f["cv2_52"], f["sb_class"] = _sb_class(y)
    b52, u52 = past(bulk, 52, "sum"), past(units, 52, "sum")
    with np.errstate(invalid="ignore", divide="ignore"):
        f["bulk_share52"] = np.where(u52 > 0, b52 / u52, np.nan)
    f["bulk_weeks52"] = past(np.where(np.isfinite(bulk), bulk > 0, np.nan).astype(float), 52,
                             "sum")  # fmt: skip
    hit = np.where(np.nan_to_num(bulk) > 0, np.arange(c)[None, :].astype(float), np.nan)
    last_hit = pd.DataFrame(hit).ffill(axis=1).shift(1, axis=1).to_numpy()
    f["since_bulk"] = np.arange(c)[None, :] - last_hit
    f["bulk_mean52"] = past(bulk, 52, "mean") / scale
    f["category"] = np.broadcast_to(category[:, None].astype(float), (p, c))
    return f


def target_calendar(dates: pd.DatetimeIndex) -> tuple[np.ndarray, np.ndarray]:
    """ISO week of year and whole weeks to the next Christmas Day (on or after the date)."""
    woy = dates.isocalendar().week.to_numpy(float)
    xmas = pd.to_datetime([f"{y}-12-25" for y in dates.year])
    xmas = xmas.where(xmas >= dates, pd.to_datetime([f"{y + 1}-12-25" for y in dates.year]))
    return woy, ((xmas - dates).days // 7).to_numpy(float)


class GlobalLGBM(Baseline):
    def __init__(
        self,
        target: str = "item",
        bulk: dict | None = None,
        params: dict | None = None,
        rounds: int = 400,
        scale_weeks: int = 13,
        oos_weeks: int = 13,
        min_pool: int = 100,
        tag: str = "",
        quantile_models: bool = False,
        segments: pd.Series | None = None,
        categories: pd.Series | None = None,
    ):
        super().__init__("naive", 1, oos_weeks, min_pool, segments)
        if target not in TARGETS:
            raise ValueError(f"target must be one of {TARGETS}")
        self.target = target
        self.bulk = part_model(bulk if bulk is not None else {"method": "ma", "window": 52})
        if target == "total":
            self.bulk = None
        if quantile_models and target != "total":
            raise ValueError("quantile models need target total (quantiles do not add up)")
        self.quantile_models = quantile_models
        self.params = DEFAULT_PARAMS | (params or {})
        self.rounds, self.scale_weeks, self.oos_weeks = rounds, scale_weeks, oos_weeks
        self.categories = categories if categories is not None else pd.Series(dtype=str)
        bulk_name = f"-bulk-{self.bulk.name}" if self.bulk else ""
        self.name = f"lgbm-{target}{bulk_name}{'-q' if quantile_models else ''}{tag}"
        what = "item demand" if target == "item" else "total demand"
        self.description = (
            f"Global LightGBM on {what} (Tweedie power "
            f"{self.params.get('tweedie_variance_power')}, {self.params['num_leaves']} leaves, "
            f"{rounds} rounds, learning rate {self.params['learning_rate']}), refitted per "
            f"origin, target scaled by the {scale_weeks}-week mean"
            + (f"; bulk demand by {self.bulk.name}" if self.bulk else "")
            + (
                "; quantiles from one pinball-loss LightGBM per level, sorted per row."
                if quantile_models
                else f"; intervals from out-of-sample errors of the last {oos_weeks} origins."
            )
        )
        self.last_importance: pd.Series | None = None

    # -- design matrix -------------------------------------------------------------------
    def _prepare(self, history: History, horizons: list[int]) -> dict:
        units_df = history.units
        n = units_df.shape[1]
        cols = units_df.columns.append(pd.DatetimeIndex([history.origin]))
        units_df = units_df.reindex(columns=cols)  # empty column for the origin itself
        bulk_df = bulk_units(history, units_df)
        units = units_df.to_numpy(float)
        bulk = bulk_df.to_numpy(float)
        y = units - bulk if self.target == "item" else units
        rows = history.rows

        def wide(col):
            if col not in rows:
                return None
            w = rows.pivot(index="stock_code", columns="week", values=col)
            return w.reindex(index=units_df.index, columns=cols).to_numpy(float)

        revenue = wide("revenue")
        price = wide("median_price")
        if price is not None:
            price = np.where(units > 0, price, np.nan)
        cat = self.categories.reindex(units_df.index).fillna(OTHER)
        codes = pd.Categorical(cat, categories=sorted(set(cat) | {OTHER})).codes
        feats = origin_features(y, units, bulk, revenue, price, codes, self.scale_weeks)
        future = pd.date_range(history.origin, periods=max(horizons) + 1, freq="7D")[1:]
        dates = cols.append(future)
        woy, to_xmas = target_calendar(pd.DatetimeIndex(dates))
        bulk_pts = None
        if self.bulk is not None:
            ext = bulk_df.reindex(columns=dates)
            bulk_pts = np.nan_to_num(self.bulk.points(ext, 1).to_numpy(float)[:, : n + 1])
        return dict(index=units_df.index, n=n, y=y, units=units, feats=feats, woy=woy,
                    to_xmas=to_xmas, bulk_pts=bulk_pts)  # fmt: skip

    @staticmethod
    def design(d: dict, i: np.ndarray, j: np.ndarray, h: int) -> pd.DataFrame:
        """Feature rows for products i at origins j (column indices) and horizon h."""
        f = d["feats"]
        out = {}
        for name in FEATURES:
            if name == "h":
                out[name] = np.full(len(i), float(h))
            elif name == "woy":
                out[name] = d["woy"][j + h - 1]
            elif name == "to_xmas":
                out[name] = d["to_xmas"][j + h - 1]
            else:
                out[name] = f[name][i, j]
        frame = pd.DataFrame(out)
        for c in CATEGORICAL:
            frame[c] = frame[c].astype("float32")
        return frame

    @staticmethod
    def train_cells(d: dict, h: int, cutoff: int) -> tuple[np.ndarray, np.ndarray]:
        """(i, j) of the training rows of horizon h whose target week j+h-1 lies before the
        column `cutoff` (and is known), with a known week before j."""
        y, started = d["y"], d["feats"]["started"]
        last_origin = cutoff - h  # j + h - 1 <= cutoff - 1
        if last_origin < 0:
            return np.array([], int), np.array([], int)
        js = np.arange(last_origin + 1)
        tgt = y[:, js + h - 1]
        ok = started[:, js] & np.isfinite(tgt)
        i, jj = np.nonzero(ok)
        return i, js[jj]

    def fit(self, d: dict, horizons: list[int], cutoff: int, params: dict | None = None):
        """LightGBM on the training rows with targets before `cutoff`; `params` override
        self.params (e.g. the quantile objective)."""
        import lightgbm as lgb

        xs, ts = [], []
        for h in horizons:
            i, j = self.train_cells(d, h, cutoff)
            if len(i) == 0:
                continue
            xs.append(self.design(d, i, j, h))
            ts.append(np.maximum(d["y"][i, j + h - 1], 0) / d["feats"]["scale"][i, j])
        if not xs:
            return None
        x = pd.concat(xs, ignore_index=True)
        data = lgb.Dataset(x, np.concatenate(ts), categorical_feature=list(CATEGORICAL),
                           free_raw_data=True)  # fmt: skip
        return lgb.train(self.params | (params or {}), data, num_boost_round=self.rounds)

    def point(self, booster, d: dict, i: np.ndarray, j: np.ndarray, h: int) -> np.ndarray:
        """Point forecast (units of the evaluation target: total demand) for cells (i, j)."""
        if booster is None:
            pred = np.zeros(len(i))
        else:
            pred = booster.predict(self.design(d, i, j, h), num_threads=self.params["num_threads"])
        pred = np.maximum(pred, 0) * d["feats"]["scale"][i, j]
        if d["bulk_pts"] is not None:
            pred = pred + d["bulk_pts"][i, j]
        return pred

    # -- Model protocol ------------------------------------------------------------------
    def predict(
        self, history: History, skus: pd.Index, horizons: list[int], quantiles: list[float]
    ) -> pd.DataFrame:
        d = self._prepare(history, horizons)
        n = d["n"]
        rows = d["index"].get_indexer(skus)
        if (rows < 0).any():
            raise ValueError("skus not in the history")
        main = self.fit(d, horizons, n)
        if main is not None:
            self.last_importance = pd.Series(
                main.feature_importance("gain"), index=main.feature_name()
            )
        if self.quantile_models:
            return self._predict_quantiles(d, main, rows, skus, horizons, quantiles)
        cut = max(n - self.oos_weeks, 1)
        oos = self.fit(d, horizons, cut)
        known = history.units.loc[skus]
        scale = self._series_scale(known)
        seg = self.segments.reindex(skus).fillna("unclassified").to_numpy()
        out = []
        for h in horizons:
            point = self.point(main, d, rows, np.full(len(rows), n), h)
            res = np.full((len(rows), self.oos_weeks), np.nan)
            for k, j in enumerate(range(cut, n - h + 1)):
                if k >= res.shape[1]:
                    break
                jj = np.full(len(rows), j)
                ok = d["feats"]["started"][rows, j] & np.isfinite(d["units"][rows, j + h - 1])
                if not ok.any():
                    continue
                pred = self.point(oos, d, rows[ok], jj[ok], h)
                res[ok, k] = (d["units"][rows[ok], j + h - 1] - pred) / scale[ok]
            qs = self._pooled_quantiles(res, seg, quantiles)
            q = np.clip(point[:, None] + qs * scale[:, None], 0, None)
            frame = pd.DataFrame(q, columns=[qcol(t) for t in quantiles])
            frame.insert(0, "mean", point)
            frame.insert(0, "h", h)
            frame.insert(0, "stock_code", skus)
            out.append(frame)
        return pd.concat(out, ignore_index=True)

    def _predict_quantiles(self, d, main, rows, skus, horizons, quantiles) -> pd.DataFrame:
        """Mean from the Tweedie model, quantiles from one pinball model per level."""
        n = d["n"]
        j = np.full(len(rows), n)
        boosters = [self.fit(d, horizons, n, {"objective": "quantile", "alpha": float(tau)})
                    for tau in quantiles]  # fmt: skip
        out = []
        for h in horizons:
            point = self.point(main, d, rows, j, h)
            q = np.column_stack([self.raw(b, d, rows, j, h) for b in boosters])
            q = np.sort(np.clip(q, 0, None), axis=1)  # no crossing
            frame = pd.DataFrame(q, columns=[qcol(t) for t in quantiles])
            frame.insert(0, "mean", point)
            frame.insert(0, "h", h)
            frame.insert(0, "stock_code", skus)
            out.append(frame)
        return pd.concat(out, ignore_index=True)

    def raw(self, booster, d: dict, i: np.ndarray, j: np.ndarray, h: int) -> np.ndarray:
        """Model output x the series scale (no clipping, no bulk part); 0 without a model."""
        if booster is None:
            return np.zeros(len(i))
        x = self.design(d, i, j, h)
        return (
            booster.predict(x, num_threads=self.params["num_threads"]) * d["feats"]["scale"][i, j]
        )

    @staticmethod
    def _series_scale(known: pd.DataFrame) -> np.ndarray:
        """Naive scale per series as for the baselines (fallback: mean of the known weeks, 1)."""
        from retail.metrics import naive_scale

        scale = naive_scale(known)["scale"]
        fallback = known.mean(axis=1).where(lambda m: m > 0, 1.0)
        return scale.where(scale > 0, fallback).to_numpy(float)
