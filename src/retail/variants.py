"""Compare data variants (cleaning configs that differ in one decision) on the panel."""

import pandas as pd


def summary(panel: pd.DataFrame) -> dict:
    open_ = panel[~panel["closed"]]
    return {
        "skus": panel["stock_code"].nunique(),
        "rows": len(panel),
        "units": float(open_["units"].sum()),
        "revenue": float(open_["revenue"].sum()),
        "zero_weeks": float((open_["units"] == 0).mean()),
    }


def sku_changes(base: pd.DataFrame, other: pd.DataFrame) -> pd.DataFrame:
    """Per SKU: total units in both panels and the relative change (other / base - 1), SKUs
    missing in one panel count as 0 there; largest absolute relative change first."""
    a = base.groupby("stock_code")["units"].sum().rename("units_base")
    b = other.groupby("stock_code")["units"].sum().rename("units_other")
    out = pd.concat([a, b], axis=1).fillna(0.0)
    out["rel_change"] = out["units_other"] / out["units_base"].where(out["units_base"] > 0) - 1
    order = out["rel_change"].abs().fillna(float("inf")).sort_values(ascending=False).index
    return out.loc[order]


def weekly_changes(base: pd.DataFrame, other: pd.DataFrame) -> pd.DataFrame:
    """Total units per week in both panels and the relative change."""
    a = base.groupby("week")["units"].sum(min_count=1).rename("units_base")
    b = other.groupby("week")["units"].sum(min_count=1).rename("units_other")
    out = pd.concat([a, b], axis=1)
    out["rel_change"] = out["units_other"] / out["units_base"] - 1
    return out
