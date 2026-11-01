"""Top-down item forecast by category (experiment E3c), with the bulk part per product as in
the split model.

At every (past) origin j: the item demand of each category (sum over ALL its products in the
history, not only the evaluated ones) is forecast with the category method (baselines or
croston); a product gets category forecast x its share of the category's item units over the
last `share_weeks` weeks before j (0 if the category sold nothing then). The bulk part is
forecast per product (as in Split); forecast = item + bulk. Intervals as for the baselines, pooled
scaled residuals of these point forecasts.
"""

import numpy as np
import pandas as pd

from retail.categories import OTHER
from retail.models.split import Split, bulk_units


class TopDown(Split):
    def __init__(
        self,
        item: dict,
        bulk: dict | None = None,
        share_weeks: int = 52,
        residual_weeks: int = 52,
        min_pool: int = 100,
        segments: pd.Series | None = None,
        categories: pd.Series | None = None,
    ):
        super().__init__(item, bulk, residual_weeks, min_pool, segments)
        self.share_weeks = share_weeks
        self.categories = categories if categories is not None else pd.Series(dtype=str)
        bulk_name = self.bulk.name if self.bulk else "0"
        self.name = f"topdown-{self.item.name}-bulk-{bulk_name}"
        self.description = (
            f"Top-down by category: category item demand by {self.item.name}, split by the "
            f"products' item shares of the last {share_weeks} weeks; bulk demand per product by "
            f"{bulk_name}; forecast = item + bulk."
        )

    def item_points(self, units: pd.DataFrame, h: int) -> pd.DataFrame:
        """Top-down item point matrix for the rows of `units` (columns as in `units`)."""
        everything = self._history.units.reindex(columns=units.columns)
        item = everything - bulk_units(self._history, everything)
        cat = self.categories.reindex(item.index).fillna(OTHER).to_numpy()
        cat_points = self.item.points(item.groupby(cat).sum(min_count=1), h)
        recent = item.T.rolling(self.share_weeks, min_periods=1).sum().T.shift(1, axis=1)
        total = recent.groupby(cat).transform("sum")
        with np.errstate(invalid="ignore", divide="ignore"):
            share = (recent / total).where(total > 0, 0.0)
        top = cat_points.reindex(cat).set_axis(item.index) * share
        return top.reindex(units.index)

    def points(self, units: pd.DataFrame, h: int) -> pd.DataFrame:
        out = self.item_points(units, h).fillna(0.0)
        if self.bulk is not None:
            out = out + self.bulk.points(bulk_units(self._history, units), h).fillna(0.0)
        started = units.notna().cumsum(axis=1).shift(1, axis=1, fill_value=0) > 0
        return out.where(started)
