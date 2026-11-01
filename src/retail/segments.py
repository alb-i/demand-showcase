"""Product segments on the weekly panel: ABC by revenue, XYZ by the CV of weekly
demand, Syntetos-Boylan classes, customer concentration and the focus set.

Everything is computed on the open weeks before `before` (the first test origin), so the
test period never decides which products are evaluated where.
"""

import numpy as np
import pandas as pd

from retail.panel import week_start

SB_CLASSES = ["smooth", "erratic", "intermittent", "lumpy"]


def history(panel: pd.DataFrame, before) -> pd.DataFrame:
    """Open panel rows (closed weeks dropped) of the weeks < before."""
    return panel[(panel["week"] < pd.Timestamp(before)) & ~panel["closed"]]


def abc(revenue: pd.Series, a: float, b: float) -> pd.Series:
    """A for the products that make up the top `a` of revenue (a product is A if the revenue of
    all larger products is below a * total), B up to `b`, C for the rest."""
    r = revenue.sort_values(ascending=False, kind="stable")
    before = (r.cumsum() - r) / r.sum()
    out = pd.Series(np.where(before < a, "A", np.where(before < b, "B", "C")), index=r.index)
    return out.reindex(revenue.index)


def xyz(cv: pd.Series, x: float, y: float) -> pd.Series:
    out = np.where(cv <= x, "X", np.where(cv <= y, "Y", "Z"))
    return pd.Series(out, index=cv.index).where(cv.notna())


def demand_stats(hist: pd.DataFrame) -> pd.DataFrame:
    """Per product over its open weeks: active_weeks, units, revenue, nonzero_weeks, cv (of weekly
    units, zeros included, population sd), adi (active weeks / weeks with demand), cv_nonzero (CV
    of the non-zero weekly units; 0 for a single demand) and cv2 = cv_nonzero ** 2."""
    g = hist.groupby("stock_code")
    out = pd.DataFrame(
        {
            "first_week": g["week"].min(),
            "active_weeks": g.size(),
            "units": g["units"].sum(),
            "revenue": g["revenue"].sum(),
            "nonzero_weeks": g["units"].agg(lambda u: int((u > 0).sum())),
            "cv": g["units"].std(ddof=0) / g["units"].mean(),
        }
    )
    nz = hist[hist["units"] > 0].groupby("stock_code")["units"]
    out["adi"] = out["active_weeks"] / out["nonzero_weeks"].where(out["nonzero_weeks"] > 0)
    out["cv_nonzero"] = nz.std(ddof=0) / nz.mean()
    out["cv2"] = out["cv_nonzero"] ** 2
    return out


def bulk_lines(sales: pd.DataFrame, before, ratio: float) -> pd.Series:
    """Sales lines before `before` -> True for a bulk sale (quantity > `ratio` x the product's
    median line quantity in that period), False for an item sale; index = those lines."""
    s = sales[sales["invoice_date"] < pd.Timestamp(before)]
    return s["quantity"] > ratio * s.groupby("stock_code")["quantity"].transform("median")


def bulk_thresholds(sales: pd.DataFrame, before, ratio: float) -> pd.Series:
    """Per product: `ratio` x its median line quantity over the lines before `before` (the bulk
    rule of bulk_lines; fixed over the whole panel)."""
    s = sales[sales["invoice_date"] < pd.Timestamp(before)]
    return ratio * s.groupby("stock_code")["quantity"].median()


def demand_split(sales: pd.DataFrame, thresholds: pd.Series) -> pd.DataFrame:
    """Weekly bulk units per product (all weeks): the sum over its lines above the product's
    threshold; products without a threshold (no line before the cut-off) have none. Columns
    stock_code, week, units_bulk (rows only where it is > 0); item units = units - units_bulk."""
    limit = sales["stock_code"].map(thresholds)
    bulk = sales[sales["quantity"] > limit]  # NaN limit: never bulk
    out = bulk.assign(week=week_start(bulk["invoice_date"]))
    out = out.groupby(["stock_code", "week"], as_index=False)["quantity"].sum()
    return out.rename(columns={"quantity": "units_bulk"})


def split_files(processed, ratio: float):
    """Paths of the demand split for one bulk threshold: demand_split_r<ratio>.{parquet,json}."""
    from pathlib import Path

    stem = Path(processed) / f"demand_split_r{ratio:g}"
    return stem.with_suffix(".parquet"), stem.with_suffix(".json")


def customer_order_mix(sales: pd.DataFrame, before, ratio: float) -> pd.DataFrame:
    """Per customer (lines with a customer id): item_lines, bulk_lines, item_units, bulk_units
    and bulk_line_share, bulk_unit_share."""
    bulk = bulk_lines(sales, before, ratio)
    s = sales.loc[bulk.index].assign(bulk=bulk).dropna(subset=["customer_id"])
    g = s.groupby(["customer_id", "bulk"])["quantity"]
    lines = g.size().unstack(fill_value=0).reindex(columns=[False, True], fill_value=0)
    units = g.sum().unstack(fill_value=0).reindex(columns=[False, True], fill_value=0)
    out = pd.DataFrame(
        {
            "item_lines": lines[False],
            "bulk_lines": lines[True],
            "item_units": units[False],
            "bulk_units": units[True],
        }
    )
    out["bulk_line_share"] = out["bulk_lines"] / (out["item_lines"] + out["bulk_lines"])
    out["bulk_unit_share"] = out["bulk_units"] / (out["item_units"] + out["bulk_units"])
    out.columns.name = None
    return out


def without_large_orders(hist: pd.DataFrame, sales: pd.DataFrame, before, ratio: float):
    """`hist` with weekly units recomputed from the sales lines before `before` whose quantity
    is at most `ratio` x the product's median line quantity (same period); weeks whose only
    lines were large orders become zero weeks. Also returns the dropped lines."""
    large = bulk_lines(sales, before, ratio)
    s = sales.loc[large.index]
    units = s[~large].groupby(["stock_code", week_start(s[~large]["invoice_date"])])["quantity"]
    units = units.sum().astype("float64")
    keys = pd.MultiIndex.from_frame(hist[["stock_code", "week"]])
    return hist.assign(units=units.reindex(keys, fill_value=0.0).to_numpy()), s[large]


def syntetos_boylan(adi: pd.Series, cv2: pd.Series, adi_cut: float, cv2_cut: float) -> pd.Series:
    """smooth (ADI < cut, CV^2 < cut), erratic (CV^2 >=), intermittent (ADI >=), lumpy (both)."""
    hi_adi, hi_cv2 = adi >= adi_cut, cv2 >= cv2_cut
    out = np.select(
        [~hi_adi & ~hi_cv2, ~hi_adi & hi_cv2, hi_adi & ~hi_cv2], SB_CLASSES[:3], SB_CLASSES[3]
    )
    return pd.Series(out, index=adi.index).where(adi.notna() & cv2.notna())


def customer_concentration(sales: pd.DataFrame, before) -> pd.DataFrame:
    """Per product, sales lines before `before`: top_customer, its share of all units (lines
    without customer count in the total, never as the top customer) and n_customers."""
    s = sales[sales["invoice_date"] < pd.Timestamp(before)]
    total = s.groupby("stock_code")["quantity"].sum()
    by_cust = s.dropna(subset=["customer_id"]).groupby(["stock_code", "customer_id"])["quantity"]
    by_cust = (
        by_cust.sum()
        .reset_index()
        .sort_values(["stock_code", "quantity", "customer_id"], ascending=[True, False, True])
    )
    top = by_cust.groupby("stock_code").first()
    out = pd.DataFrame(index=total.index)
    out["top_customer"] = top["customer_id"].astype("Int64")
    out["top_customer_share"] = top["quantity"] / total
    out["n_customers"] = by_cust.groupby("stock_code").size()
    return out.fillna({"top_customer_share": 0.0, "n_customers": 0})


def segment_table(panel: pd.DataFrame, sales: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """One row per product with at least cfg['min_demand_weeks'] (default 1) weeks with demand
    before cfg['before']; `focus` marks the focus set."""
    hist = history(panel, cfg["before"])
    stats = demand_stats(hist)
    # products with fewer than min_demand_weeks weeks with demand are left out entirely
    stats = stats[stats["nonzero_weeks"] >= cfg.get("min_demand_weeks", 1)]
    stats["revenue_share"] = stats["revenue"] / stats["revenue"].sum()
    stats["abc"] = abc(stats["revenue"], **cfg["abc"])
    x = dict(cfg["xyz"])
    cv = stats["cv" if x.pop("zero_weeks", True) else "cv_nonzero"]  # without zero weeks
    stats["xyz"] = xyz(cv, **x)
    sb = cfg["syntetos_boylan"]
    if sb.get("max_order_ratio"):  # classes without the product's very large orders
        stats = stats.rename(columns={"adi": "adi_all", "cv2": "cv2_all"})
        stats["sb_class_all"] = syntetos_boylan(
            stats["adi_all"], stats["cv2_all"], sb["adi"], sb["cv2"]
        )
        trimmed, _ = without_large_orders(hist, sales, cfg["before"], sb["max_order_ratio"])
        stats = stats.join(demand_stats(trimmed)[["adi", "cv2"]])
    stats["sb_class"] = syntetos_boylan(stats["adi"], stats["cv2"], sb["adi"], sb["cv2"])
    stats = stats.join(customer_concentration(sales, cfg["before"]))
    f = cfg["focus"]
    stats["focus"] = stats["abc"].isin(f["classes"]) & (
        stats["active_weeks"] >= f["min_active_weeks"]
    )
    return stats.sort_values("revenue", ascending=False).reset_index()


def class_table(seg: pd.DataFrame, by: str) -> pd.DataFrame:
    """Products and revenue share per class (rows) for the full and the focus set."""
    g = seg.groupby(by)
    out = pd.DataFrame({"products": g.size(), "revenue_share": g["revenue"].sum()})
    out["revenue_share"] /= seg["revenue"].sum()
    f = seg[seg["focus"]].groupby(by)
    out["focus_products"] = f.size().reindex(out.index).fillna(0).astype(int)
    out["focus_revenue_share"] = (f["revenue"].sum() / seg["revenue"].sum()).reindex(out.index)
    return out.fillna({"focus_revenue_share": 0.0})
