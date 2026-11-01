"""Bulk / item split model (E2 extension): one model for the item demand, one for the
bulk demand (lines above bulk_ratio x the product's median line quantity; default
max_order_ratio, 10x; scripts/split_demand.py),
forecast = item forecast + bulk forecast (bulk: none = 0).

The bulk units come from the panel column units_bulk of the History (weeks < origin only);
item units = units - units_bulk. Each part's point matrix comes from its own method
(baselines or croston), a part without a forecast yet counts 0. Intervals as for the
baselines: pooled scaled h-step residuals of the summed forecast against total demand.
"""

import pandas as pd

from retail.backtest import History
from retail.models import baselines, croston
from retail.models.baselines import Baseline
from retail.models.croston import Intermittent


def part_model(cfg: dict | None) -> Baseline | None:
    """Point-forecast model of one part from {method, window | alpha, beta}; None = 0."""
    if cfg is None:
        return None
    if cfg["method"] in baselines.METHODS:
        return Baseline(cfg["method"], cfg.get("window", 4))
    if cfg["method"] in croston.METHODS:
        return Intermittent(cfg["method"], cfg.get("alpha", 0.1), cfg.get("beta"))
    raise ValueError(f"unknown method {cfg['method']!r}")


def bulk_units(history: History, like: pd.DataFrame) -> pd.DataFrame:
    """Bulk units shaped like the units matrix `like`: 0 in known weeks without bulk lines,
    NaN where `like` is NaN (before the first sale, closed weeks, the future)."""
    rows = history.rows
    if "units_bulk" not in rows:
        raise ValueError("panel has no units_bulk column: run scripts/split_demand.py")
    wide = rows.pivot(index="stock_code", columns="week", values="units_bulk")
    wide = wide.reindex(index=like.index, columns=like.columns).fillna(0.0)
    return wide.where(like.notna())


class Split(Baseline):
    def __init__(
        self,
        item: dict,
        bulk: dict | None = None,
        residual_weeks: int = 52,
        min_pool: int = 100,
        segments: pd.Series | None = None,
    ):
        super().__init__("naive", 1, residual_weeks, min_pool, segments)
        self.item, self.bulk = part_model(item), part_model(bulk)
        bulk_name = self.bulk.name if self.bulk else "0"
        self.name = f"split-{self.item.name}-bulk-{bulk_name}"
        self.description = (
            f"Bulk/item split: item demand by {self.item.name}, bulk demand by {bulk_name}; "
            "forecast = item + bulk."
        )
        self._history: History | None = None

    def predict(
        self, history: History, skus: pd.Index, horizons: list[int], quantiles: list[float]
    ) -> pd.DataFrame:
        self._history = history
        try:
            return super().predict(history, skus, horizons, quantiles)
        finally:
            self._history = None

    def points(self, units: pd.DataFrame, h: int) -> pd.DataFrame:
        bulk = bulk_units(self._history, units)
        item = units - bulk
        out = self.item.points(item, h).fillna(0.0)
        if self.bulk is not None:
            out = out + self.bulk.points(bulk, h).fillna(0.0)
        started = units.notna().cumsum(axis=1).shift(1, axis=1, fill_value=0) > 0
        return out.where(started)  # NaN at origins before (and at) the first sale
