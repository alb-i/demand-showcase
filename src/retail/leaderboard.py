"""Leaderboard: model x segment metrics with paired bootstrap intervals.

For every model (its evaluated rows) and segment ("all" and every ABC x SB segment of the rows):
the pooled metrics of retail.compare.summary (MASE, CRPS, pinball per level, coverage, rcov,
bias; unweighted and revenue weighted) and, against a reference model, the paired bootstrap of
the per-series mean MASE and CRPS differences on the rows both evaluated. The workbench shows
the table (time-series adapter, get_leaderboard); the metric definitions stay in
retail.metrics.
"""

import numpy as np
import pandas as pd

from retail.compare import KEY, summary
from retail.metrics import paired_bootstrap, row_errors

METRICS = ("abs_scaled", "crps")  # per-series means for the bootstrap (MASE, CRPS)


def _per_series(rows: pd.DataFrame, err: pd.DataFrame) -> pd.DataFrame:
    df = pd.DataFrame({"stock_code": rows["stock_code"].to_numpy(),
                       "segment": rows["segment"].to_numpy()})  # fmt: skip
    for m in METRICS:
        df[m] = err[m].to_numpy()
    return df.groupby("stock_code").agg(segment=("segment", "first"),
                                        **{m: (m, "mean") for m in METRICS})  # fmt: skip


def leaderboard(runs: dict[str, pd.DataFrame], reference: str, quantiles, levels,
                n: int = 2000, seed: int = 0) -> pd.DataFrame:  # fmt: skip
    """One row per (model, segment): n_series, the summary metrics, and diff/lo/hi/sig of MASE
    and CRPS against `reference` (per-series means on the common rows; NaN for the reference
    itself). runs: model -> evaluated rows (with a `segment` column)."""
    if reference not in runs:
        raise ValueError(f"reference {reference} not among the runs")
    ref_rows = runs[reference]
    out = []
    for model, rows in runs.items():
        segs = summary(rows, quantiles, levels, by="segment")
        segs.loc["all"] = summary(rows, quantiles, levels).iloc[0]
        if model != reference:
            common = rows[KEY].merge(ref_rows[KEY], on=KEY)
            a, b = rows.merge(common, on=KEY), ref_rows.merge(common, on=KEY)
            pa = _per_series(a, row_errors(a, quantiles, []))
            pb = _per_series(b, row_errors(b, quantiles, []))
        for seg, rec in segs.iterrows():
            r = {"model": model, "segment": seg, **rec.to_dict()}
            for m, name in zip(METRICS, ("mase", "crps"), strict=True):
                if model == reference:
                    r |= {f"{name}_diff": np.nan, f"{name}_lo": np.nan, f"{name}_hi": np.nan,
                          f"{name}_sig": False}  # fmt: skip
                    continue
                sel = pa.index if seg == "all" else pa.index[pa["segment"] == seg]
                b_ = paired_bootstrap(pa.loc[sel, m], pb[m], n=n, seed=seed)
                r |= {f"{name}_diff": b_["diff"], f"{name}_lo": b_["lo"], f"{name}_hi": b_["hi"],
                      f"{name}_sig": b_["significant"]}  # fmt: skip
            out.append(r)
    return pd.DataFrame(out)
