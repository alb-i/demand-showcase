"""Cost model of the inventory simulation. All parameters come from
configs/costs.yaml."""

from dataclasses import dataclass, field, replace
from pathlib import Path

import pandas as pd
import yaml

from retail.io import REPO_DIR

COSTS = REPO_DIR / "configs" / "costs.yaml"


@dataclass(frozen=True)
class Costs:
    margin: float = 0.40
    holding_rate: float = 0.25
    lead_time: int = 1
    review_period: int = 1
    order_cost: float = 0.0
    lost_sales: bool = True
    weeks_per_year: int = 52
    write_down_share: float = 0.5
    write_down_categories: tuple[str, ...] = field(default_factory=tuple)

    @property
    def horizon(self) -> int:
        """K = L + R: the weeks an order has to cover."""
        return self.lead_time + self.review_period

    def with_(self, **kw) -> "Costs":
        return replace(self, **kw)


def load_costs(path: Path = COSTS) -> tuple[Costs, dict]:
    """The base Costs and the whole config (grids, sensitivity, simulation weeks)."""
    cfg = yaml.safe_load(Path(path).read_text())
    wd = cfg.get("write_down") or {}
    costs = Costs(
        margin=float(cfg["margin"]),
        holding_rate=float(cfg["holding_rate"]),
        lead_time=int(cfg["lead_time"]),
        review_period=int(cfg["review_period"]),
        order_cost=float(cfg.get("order_cost", 0.0)),
        lost_sales=bool(cfg.get("lost_sales", True)),
        weeks_per_year=int(cfg.get("weeks_per_year", 52)),
        write_down_share=float(wd.get("share", 0.0)),
        write_down_categories=tuple(wd.get("categories", [])),
    )
    return costs, cfg


def unit_prices(panel: pd.DataFrame, before: pd.Timestamp) -> pd.Series:
    """Price p per product: median of the weekly median prices over the weeks with sales before
    `before` (no look-ahead)."""
    p = panel[(panel["week"] < before) & (panel["units"] > 0)]
    return p.groupby("stock_code")["median_price"].median()


def unit_economics(price: pd.Series, costs: Costs) -> pd.DataFrame:
    """Per product: price p, unit cost c = (1 - m) p, lost margin per unit not sold c_u = m p,
    holding cost per unit and week h = holding_rate x c / weeks_per_year."""
    c = (1 - costs.margin) * price
    return pd.DataFrame({
        "price": price,
        "unit_cost": c,
        "lost_margin": costs.margin * price,
        "holding_week": costs.holding_rate * c / costs.weeks_per_year,
    })  # fmt: skip


def critical_ratio(costs: Costs) -> float:
    """Newsvendor level tau* = c_u / (c_u + c_o) for one review period: c_u = m p (lost
    margin), c_o = holding over R weeks = holding_rate (1 - m) p R / weeks_per_year; p cancels."""
    c_u = costs.margin
    c_o = costs.holding_rate * (1 - costs.margin) * costs.review_period / costs.weeks_per_year
    return c_u / (c_u + c_o)
