"""Weekly periodic-review simulation and its KPIs.

Timing within week t: (1) orders due in t arrive; (2) in a review week the order
q_t = max(0, S_t - inventory position) is placed (position = on hand + on order) and arrives at
the start of week t + L (L = 0: at once); (3) the week's demand is served from stock. Unmet
demand is lost (lost_sales) or backordered (stock goes negative and is served later; the fill
rate counts only what was served in the week of the demand). The simulation starts with stock
S at the first week and nothing on order. Average stock of a week = mean of the stock after
the arrivals and at the end of the week (linear depletion), negative stock counts as 0.
"""

import numpy as np
import pandas as pd

from retail.inventory.costs import Costs

COLUMNS = ["demand", "arrival", "order", "on_hand_start", "on_hand_end", "served", "short",
           "avg_on_hand", "level"]  # fmt: skip


def simulate(demand: pd.DataFrame, levels: pd.DataFrame, lead_time: int, review_period: int = 1,
             lost_sales: bool = True) -> pd.DataFrame:  # fmt: skip
    """demand: product x week units (NaN = closed week, no demand); levels: product x week S_t
    (read in the review weeks: the first week and every review_period-th after it; NaN = no
    order). Returns one row per (stock_code, week) with the COLUMNS."""
    weeks = list(demand.columns)
    n, m = demand.shape
    lv = levels.reindex(index=demand.index, columns=weeks).to_numpy(float)
    d = np.nan_to_num(demand.to_numpy(float))
    pipeline = np.zeros((n, m + lead_time + 1))  # arrivals per week index
    on_hand = np.nan_to_num(lv[:, 0]).copy()
    out = {c: np.zeros((n, m)) for c in COLUMNS}
    for i in range(m):
        arrival = pipeline[:, i].copy()
        on_hand = on_hand + arrival
        start = on_hand.copy()
        order = np.zeros(n)
        if i % review_period == 0:
            position = on_hand + pipeline[:, i + 1 :].sum(axis=1)
            s = lv[:, i]
            order = np.where(np.isnan(s), 0.0, np.maximum(s - position, 0.0))
            if lead_time == 0:
                on_hand = on_hand + order
                start = on_hand.copy()
            else:
                pipeline[:, i + lead_time] += order
        served = np.minimum(np.maximum(on_hand, 0.0), d[:, i])
        on_hand = on_hand - served if lost_sales else on_hand - d[:, i]
        for c, v in (
            ("demand", d[:, i]),
            ("arrival", arrival),
            ("order", order),
            ("on_hand_start", start),
            ("on_hand_end", on_hand),
            ("served", served),
            ("short", d[:, i] - served),
            ("level", lv[:, i]),
            ("avg_on_hand", (np.maximum(start, 0) + np.maximum(on_hand, 0)) / 2),
        ):
            out[c][:, i] = v  # fmt: skip
    idx = pd.MultiIndex.from_product([demand.index, weeks], names=["stock_code", "week"])
    return pd.DataFrame({c: v.ravel() for c, v in out.items()}, index=idx).reset_index()


def kpis(sim: pd.DataFrame, econ: pd.DataFrame, costs: Costs, seasonal=(),
         review_period: int = 1) -> pd.DataFrame:  # fmt: skip
    """Per product: demand, served, short, fill rate (served / demand), cycle service level
    (share of review cycles without a shortage), stock-out weeks, average stock (units and
    value at unit cost c), holding cost, lost margin (lost sales only), order cost, write-down
    of the stock left at the end (products in `seasonal`, share x c) and the total cost without
    (total_cost) and with the write-down (total_cost_wd). econ: retail.inventory.costs.
    unit_economics."""
    s = sim.join(econ, on="stock_code")
    pos = s.groupby("stock_code").cumcount()
    s["cycle"] = pos // review_period
    s["hold"] = s["avg_on_hand"] * s["holding_week"]
    s["lost"] = s["short"] * s["lost_margin"] if costs.lost_sales else 0.0
    g = s.groupby("stock_code")
    out = pd.DataFrame({
        "demand": g["demand"].sum(),
        "served": g["served"].sum(),
        "short": g["short"].sum(),
        "stockout_weeks": g["short"].apply(lambda x: int((x > 1e-9).sum())),
        "weeks": g.size(),
        "avg_stock": g["avg_on_hand"].mean(),
        "holding_cost": g["hold"].sum(),
        "lost_margin": g["lost"].sum(),
        "orders": g["order"].apply(lambda x: int((x > 0).sum())),
    })  # fmt: skip
    cyc = s.groupby(["stock_code", "cycle"])["short"].max()
    out["cycle_service"] = (cyc <= 1e-9).groupby(level=0).mean()
    out["fill_rate"] = out["served"] / out["demand"].where(out["demand"] > 0)
    out["avg_stock_value"] = out["avg_stock"] * econ["unit_cost"].reindex(out.index)
    last = s.groupby("stock_code").tail(1).set_index("stock_code")
    left = np.maximum(last["on_hand_end"], 0) * last["unit_cost"]
    out["end_stock_value"] = left
    is_seasonal = out.index.isin(list(seasonal))
    out["write_down"] = np.where(is_seasonal, costs.write_down_share * left, 0.0)
    out["order_cost"] = costs.order_cost * out["orders"]
    out["total_cost"] = out["holding_cost"] + out["lost_margin"] + out["order_cost"]
    out["total_cost_wd"] = out["total_cost"] + out["write_down"]
    return out


def totals(per_product: pd.DataFrame) -> dict:
    """Totals over the products: fill rate = sum served / sum demand, cycle service level and
    stock-out weeks as means/sums, money as sums (average stock value = sum of the products'
    average stock values)."""
    p = per_product
    return {
        "products": len(p),
        "demand": float(p["demand"].sum()),
        "fill_rate": float(p["served"].sum() / p["demand"].sum()),
        "cycle_service": float(p["cycle_service"].mean()),
        "stockout_weeks": int(p["stockout_weeks"].sum()),
        "avg_stock_value": float(p["avg_stock_value"].sum()),
        "end_stock_value": float(p["end_stock_value"].sum()),
        "holding_cost": float(p["holding_cost"].sum()),
        "lost_margin": float(p["lost_margin"].sum()),
        "order_cost": float(p["order_cost"].sum()),
        "write_down": float(p["write_down"].sum()),
        "total_cost": float(p["total_cost"].sum()),
        "total_cost_wd": float(p["total_cost_wd"].sum()),
    }
