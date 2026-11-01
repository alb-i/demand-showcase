"""Static demo: product pick, re-priceable aggregates and the data files of demo/.

The demo opens from local files (file://), where browsers block fetch() of JSON, so the data
are JavaScript files that assign to window.DEMO (js_data) and are loaded with <script> tags.

The policy what-if of the demo covers all focus products through aggregates that the page
re-prices for any margin, holding rate and write-down share (aggregate / reprice): every cost of
retail's cost model is linear in a price-weighted sum of the simulation.
"""

import json
import math

import numpy as np
import pandas as pd

SEASONAL = ("christmas", "easter")


def grid(lo: float, hi: float, step: float, extra=()) -> list[float]:
    """Values lo, lo + step, ..., hi plus `extra`, rounded to 4 decimals, sorted, unique."""
    n = int(round((hi - lo) / step))
    vals = {round(lo + i * step, 4) for i in range(n + 1)} | {round(float(v), 4) for v in extra}
    return sorted(vals)


def pick_products(table: pd.DataFrame, n: int = 30, n_seasonal: int = 4,
                  min_class: int = 3) -> list[str]:  # fmt: skip
    """About n representative products of a table (series_id, revenue, sb_class, category):
    n_seasonal seasonal ones, the rest per Syntetos-Boylan class in proportion to its size (at
    least min_class each, if available); within a group evenly spaced over the revenue ranks,
    so big and small sellers both appear. Deterministic."""
    t = table.sort_values(["revenue", "series_id"], ascending=[False, True])

    def spread(frame: pd.DataFrame, k: int) -> list[str]:
        ids = frame["series_id"].tolist()
        if k >= len(ids):
            return ids
        pos = np.linspace(0, len(ids) - 1, k).round().astype(int)
        return [ids[i] for i in pos]

    seasonal = t["category"].isin(SEASONAL)
    out = spread(t[seasonal], n_seasonal)
    rest = t[~t["series_id"].isin(out)]
    sizes = rest["sb_class"].value_counts()
    left = n - len(out)
    want = {c: min(int(s), max(min_class, math.floor(left * s / sizes.sum()))) for c, s in
            sizes.items()}  # fmt: skip
    # largest classes give up or take the difference so that the total is n
    order = sizes.index.tolist()
    i = 0
    while sum(want.values()) != left and i < 10 * len(order):
        c = order[i % len(order)]
        if sum(want.values()) > left and want[c] > min_class:
            want[c] -= 1
        elif sum(want.values()) < left and want[c] < sizes[c]:
            want[c] += 1
        i += 1
    for c in order:
        out += spread(rest[rest["sb_class"] == c], want[c])
    return out


def aggregate(summary: dict, price: np.ndarray, seasonal: np.ndarray) -> dict:
    """The cost-free sums of a simulation summary (workbench.inventory.summarize) over all
    products: served and short units, stock-out and product weeks, and the price-weighted sums
    of mean stock (A), stock-weeks (H), lost units (S) and seasonal leftovers (E)."""
    return {
        "served": float(summary["served"].sum()),
        "short": float(summary["short"].sum()),
        "stockouts": int(summary["stockouts"].sum()),
        "weeks": int(summary["weeks"].sum()),
        "A": float((summary["avg_mean"] * price).sum()),
        "H": float((summary["avg_sum"] * price).sum()),
        "S": float((summary["short"] * price).sum()),
        "E": float((summary["end"] * price * seasonal).sum()),
    }


def reprice(agg: dict, margin: float, holding_rate: float, write_down: float,
            weeks_per_year: int = 52) -> dict:  # fmt: skip
    """Totals of an aggregate at these costs (the same numbers as workbench.inventory.price; the
    demo's JavaScript does the same)."""
    dem = agg["served"] + agg["short"]
    out = {
        "fill_rate": agg["served"] / dem if dem > 0 else float("nan"),
        "cycle_service": 1 - agg["stockouts"] / agg["weeks"],
        "stockout_weeks": agg["stockouts"],
        "avg_stock_value": (1 - margin) * agg["A"],
        "holding_cost": holding_rate * (1 - margin) / weeks_per_year * agg["H"],
        "lost_margin": margin * agg["S"],
        "write_down": write_down * (1 - margin) * agg["E"],
    }
    out["total_cost"] = out["holding_cost"] + out["lost_margin"] + out["write_down"]
    return out


def rounded(values, digits: int = 2) -> list:
    """List of floats rounded to `digits`, NaN -> None (JSON null)."""
    out = []
    for v in np.asarray(values, dtype=float).ravel():
        out.append(None if not np.isfinite(v) else round(float(v), digits))
    return out


def js_data(key: str, obj) -> str:
    """JavaScript that stores obj under window.DEMO[key] (compact JSON, no NaN)."""
    body = json.dumps(obj, separators=(",", ":"), allow_nan=False)
    return f"(window.DEMO=window.DEMO||{{}})[{json.dumps(key)}]={body};\n"
