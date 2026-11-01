"""Aggregate exploration of the panel and the cleaned lines.

Descriptive only: nothing here feeds a model. Figures: scripts/explore.py.
"""

import pandas as pd

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def weekly_totals(panel: pd.DataFrame) -> pd.DataFrame:
    """Per week: units, revenue, active_skus (units > 0), closed. Closed weeks stay missing."""
    g = panel.groupby("week")
    out = pd.DataFrame(
        {
            "units": g["units"].sum(min_count=1),
            "revenue": g["revenue"].sum(min_count=1),
            "active_skus": g["units"].agg(lambda u: int((u > 0).sum())),
            "closed": g["closed"].first(),
        }
    )
    out.loc[out["closed"], "active_skus"] = pd.NA
    return out


def weekday_shares(sales: pd.DataFrame) -> pd.DataFrame:
    """Share of lines, units and revenue per weekday (Mon..Sun, missing days as 0)."""
    s = sales.assign(
        day=sales["invoice_date"].dt.day_of_week, revenue=sales["quantity"] * sales["price"]
    )
    g = s.groupby("day").agg(lines=("quantity", "size"), units=("quantity", "sum"))
    g["revenue"] = s.groupby("day")["revenue"].sum()
    g = g.reindex(range(7), fill_value=0)
    g = g / g.sum()
    g.index = WEEKDAYS
    return g


def season_profile(totals: pd.DataFrame, col: str = "units") -> pd.DataFrame:
    """Weekly totals as ISO week-of-year (rows) x ISO year (columns); closed weeks stay missing."""
    iso = totals.index.isocalendar()
    return totals.assign(year=iso.year.to_numpy(), woy=iso.week.to_numpy()).pivot(
        index="woy", columns="year", values=col
    )


def life_cycle(panel: pd.DataFrame) -> pd.DataFrame:
    """Per product: first and last week with a sale."""
    s = panel[panel["units"] > 0].groupby("stock_code")["week"]
    return pd.DataFrame({"first_week": s.min(), "last_week": s.max()})


def new_product_share(panel: pd.DataFrame, burn_in_weeks: int) -> pd.Series:
    """Per week: revenue share of products whose first sale is later than the first
    `burn_in_weeks` weeks of the data (introduced during the period, not merely first seen)."""
    start = panel["week"].min() + pd.Timedelta(weeks=burn_in_weeks)
    first = life_cycle(panel)["first_week"]
    new = panel["stock_code"].map(first >= start)
    rev = panel.groupby("week")["revenue"].sum(min_count=1)
    return panel[new].groupby("week")["revenue"].sum().reindex(rev.index, fill_value=0) / rev
