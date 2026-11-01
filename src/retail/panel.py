"""Weekly demand panel per SKU from the cleaned lines.

Row = (stock_code, week) for every week from the product's first to its last sale (no zeros
before launch or after the last sale). Weeks without any trading day of the shop are closed:
kept as rows with closed = True and missing demand, not zero.
"""

import numpy as np
import pandas as pd


def week_start(ts: pd.Series) -> pd.Series:
    """Monday 00:00 of the ISO week."""
    days = ts.dt.normalize()
    return days - pd.to_timedelta(days.dt.day_of_week, unit="D")


def trading_weeks(lines: pd.DataFrame) -> pd.DataFrame:
    """Every week from the first to the last line, with the number of days with any invoice
    line (all lines, including non-products and cancellations) and closed = (no such day)."""
    days = lines["invoice_date"].dt.normalize().drop_duplicates()
    per_week = days.groupby(week_start(days)).size()
    weeks = pd.date_range(per_week.index.min(), per_week.index.max(), freq="7D")
    out = pd.DataFrame({"week": weeks})
    out["trading_days"] = out["week"].map(per_week).fillna(0).astype("int64")
    out["closed"] = out["trading_days"] == 0
    return out


def canonical_descriptions(sales: pd.DataFrame) -> pd.DataFrame:
    """Most frequent description per stock code (ties: alphabetically first), with the
    number of distinct descriptions and of lines."""
    counts = sales.groupby(["stock_code", "description"]).size().rename("n").reset_index()
    counts = counts.sort_values(["stock_code", "n", "description"], ascending=[True, False, True])
    out = counts.groupby("stock_code").agg(
        description=("description", "first"),
        n_descriptions=("description", "size"),
        lines=("n", "sum"),
    )
    return out.reset_index()


def drop_last_week(sales: pd.DataFrame, returns: pd.DataFrame):
    """Remove lines in the week of the last line (incomplete). Returns sales, returns, the
    removed lines and that week."""
    last = week_start(pd.concat([sales["invoice_date"], returns["invoice_date"]])).max()
    s_out = week_start(sales["invoice_date"]) == last
    r_out = week_start(returns["invoice_date"]) == last
    removed = pd.concat([sales[s_out], returns[r_out]])
    return sales[~s_out], returns[~r_out], removed, last


def build_panel(sales: pd.DataFrame, returns: pd.DataFrame, weeks: pd.DataFrame):
    """Panel and the return lines outside every product's active window (not in the panel)."""
    s = sales.assign(
        week=week_start(sales["invoice_date"]), revenue=sales["quantity"] * sales["price"]
    )
    keys = ["stock_code", "week"]
    agg = s.groupby(keys).agg(
        units=("quantity", "sum"),
        revenue=("revenue", "sum"),
        n_invoices=("invoice", "nunique"),
        n_customers=("customer_id", "nunique"),
        median_price=("price", "median"),
    )
    top = s.groupby([*keys, "customer_id"])["quantity"].sum().groupby(level=[0, 1]).max()
    agg["top_customer_share"] = (top / agg["units"]).reindex(agg.index)

    span = s.groupby("stock_code")["week"].agg(["min", "max"])
    week_list = weeks["week"].to_numpy()
    grid = pd.concat(
        [
            pd.DataFrame(
                {"stock_code": code, "week": week_list[(week_list >= lo) & (week_list <= hi)]}
            )
            for code, lo, hi in span.itertuples()
        ],
        ignore_index=True,
    )
    panel = grid.merge(agg.reset_index(), on=keys, how="left").merge(weeks, on="week", how="left")

    r = returns.assign(week=week_start(returns["invoice_date"]))
    ret = (-r.groupby(keys)["quantity"].sum()).rename("returned_units").reset_index()
    inside = ret.merge(grid, on=keys, how="inner")
    panel = panel.merge(inside, on=keys, how="left")
    r_keys = pd.MultiIndex.from_frame(r[keys])
    outside = r[~r_keys.isin(pd.MultiIndex.from_frame(grid))]

    open_ = ~panel["closed"]
    for col in ["units", "revenue", "n_invoices", "n_customers", "returned_units"]:
        panel[col] = panel[col].where(~open_ | panel[col].notna(), 0).astype("float64")
        panel.loc[~open_, col] = np.nan
    return panel.sort_values(keys, ignore_index=True), outside


def panel_totals(panel: pd.DataFrame) -> dict:
    return {
        "units": int(panel["units"].sum()),
        "revenue": float(panel["revenue"].sum()),
        "returned_units": int(panel["returned_units"].sum()),
    }
