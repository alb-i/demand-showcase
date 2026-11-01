"""Data for the figures of the technical report (reports/report.tex)."""

import pandas as pd

from retail.metrics import qcol, row_errors

# Model families in a fixed order (one categorical colour each in the figures)
FAMILIES = ("Simple baselines", "Croston / SBA / TSB", "Item + bulk split", "ETS / ARIMA",
            "LightGBM")  # fmt: skip


def family(model: str) -> str:
    """Family of a model name as used in the run names (naive, ma4, tsb-a0.2-b0.2, ...)."""
    if model.startswith(("lgbm", "best-")):
        return "LightGBM"
    if model.startswith(("ets", "arima")):
        return "ETS / ARIMA"
    if model.startswith(("split", "topdown")):
        return "Item + bulk split"
    if model.startswith(("croston", "sba", "tsb")):
        return "Croston / SBA / TSB"
    if model in ("naive", "snaive") or model.startswith("ma"):
        return "Simple baselines"
    raise ValueError(f"unknown model family: {model}")


def hit_curve(rows: pd.DataFrame, quantiles) -> pd.DataFrame:
    """Per quantile level: share of rows with y <= q_tau (`hit`) and the randomised-PIT hit
    rate (`rhit`, ties y = q counted fractionally). Calibrated: both close to tau, `hit`
    above tau where y = q = 0 ties are frequent."""
    err = row_errors(rows, quantiles, [])
    recs = []
    for t in quantiles:
        recs.append({"tau": t, "hit": float((rows["y"] <= rows[qcol(t)]).mean()),
                     "rhit": float(err[f"rhit_{t:g}"].mean())})  # fmt: skip
    return pd.DataFrame(recs)
