"""Model selection per segment and the composite forecast (E9).

The winner of a segment is the candidate with the lowest mean of a row metric (default the
CRPS, unweighted) over that segment's rows of the tuning origins; candidates are compared on
the rows all of them evaluated. The composite takes, per product, every row of the winner of
the product's segment, so its mean and quantiles always come from one model.
"""

import pandas as pd

from retail.compare import KEY
from retail.metrics import row_errors


def segment_table(runs: dict[str, pd.DataFrame], quantiles, levels, labels: pd.Series,
                  metric: str = "crps") -> pd.DataFrame:  # fmt: skip
    """Mean metric per segment (rows) x candidate (columns) on the common rows."""
    common = None
    for rows in runs.values():
        k = rows[KEY]
        common = k if common is None else common.merge(k, on=KEY)
    out = {}
    for name, rows in runs.items():
        r = rows.merge(common, on=KEY)
        err = row_errors(r, quantiles, levels)[metric]
        seg = r["stock_code"].map(labels).fillna("unclassified")
        out[name] = err.groupby(seg.to_numpy()).mean()
    return pd.DataFrame(out)


def winners(table: pd.DataFrame) -> pd.Series:
    """Segment -> candidate with the lowest value (ties: the first candidate column)."""
    return table.idxmin(axis=1)


def compose(runs: dict[str, pd.DataFrame], win: pd.Series, labels: pd.Series,
            fallback: str) -> pd.DataFrame:  # fmt: skip
    """Rows of the winner of each product's segment (segments without a winner: fallback),
    with the column `source` = the model used."""
    parts = []
    for name, rows in runs.items():
        seg = rows["stock_code"].map(labels).fillna("unclassified")
        model = seg.map(win).fillna(fallback)
        part = rows[(model == name).to_numpy()]
        parts.append(part.assign(source=name))
    out = pd.concat(parts, ignore_index=True)
    return out.sort_values(["origin", "stock_code", "h"], ignore_index=True)
