"""Summaries of backtest runs and paired comparisons between them.

A run's rows.parquet holds one row per evaluated (stock_code, origin, h). Summaries pool all
rows of a run; comparisons first average a metric per series (over origins and horizons) and
then bootstrap the difference over series (paired: only series present in both runs).
"""

import re
from pathlib import Path

import pandas as pd
import yaml

from retail.metrics import aggregate, paired_bootstrap, row_errors

KEY = ["stock_code", "origin", "h"]


def select_sb(rows: pd.DataFrame, classes) -> pd.DataFrame:
    """Rows whose segment (e.g. "A-lumpy") has one of the Syntetos-Boylan classes."""
    sb = rows["segment"].str.split("-", n=1).str[1]
    return rows[sb.isin(list(classes))]


def common_target(configs) -> str:
    """The target all runs were scored on (total unless a run says item); ValueError if
    they differ, since their errors are not comparable."""
    targets = {cfg.get("target", "total") for cfg in configs}
    if len(targets) > 1:
        raise ValueError(f"runs scored on different targets ({', '.join(sorted(targets))})")
    return targets.pop()


def relabel(rows: pd.DataFrame, labels: pd.Series) -> pd.DataFrame:
    """Rows with the segment (stock_code -> label, e.g. "A-lumpy") of `labels`; products
    without a label are "unclassified" (as in the backtest)."""
    return rows.assign(segment=rows["stock_code"].map(labels).fillna("unclassified").to_numpy())


def select_codes(rows: pd.DataFrame, codes) -> pd.DataFrame:
    """Rows of the given products."""
    return rows[rows["stock_code"].isin(list(codes))]


def summary(rows: pd.DataFrame, quantiles, levels, by: str | None = None) -> pd.DataFrame:
    """Unweighted and revenue weighted metrics over all rows, or per value of `by`."""
    err = row_errors(rows, quantiles, levels)
    groups = [("all", rows.index)] if by is None else list(rows.groupby(by).groups.items())
    out = {}
    for name, idx in groups:
        r, e = rows.loc[idx], err.loc[idx]
        rec = {"n": len(r), "series": r["stock_code"].nunique()}
        rec |= aggregate(r, e, weighted=False)
        rec |= {f"{k}_w": v for k, v in aggregate(r, e, weighted=True).items()}
        out[name] = rec
    return pd.DataFrame.from_dict(out, orient="index")


def per_series(rows: pd.DataFrame, quantiles, levels, metric: str) -> pd.DataFrame:
    """Mean of a row-level metric (abs_scaled, crps, ...) per series, and the series' mean
    revenue weight."""
    err = row_errors(rows, quantiles, levels)
    df = pd.DataFrame(
        {"stock_code": rows["stock_code"], "value": err[metric], "weight": rows["weight"]}
    )
    return df.groupby("stock_code").agg(value=("value", "mean"), weight=("weight", "mean"))


def compare(
    rows_a: pd.DataFrame,
    rows_b: pd.DataFrame,
    quantiles,
    levels,
    metric: str = "abs_scaled",
    weighted: bool = False,
    n: int = 2000,
    level: float = 0.95,
) -> dict:
    """Bootstrap CI of mean(metric of a - metric of b) over series, on the rows both runs
    evaluated (same stock_code, origin, h)."""
    common = rows_a[KEY].merge(rows_b[KEY], on=KEY)
    a = rows_a.merge(common, on=KEY)
    b = rows_b.merge(common, on=KEY)
    sa = per_series(a, quantiles, levels, metric)
    sb = per_series(b, quantiles, levels, metric)
    w = sa["weight"] if weighted else None
    return paired_bootstrap(sa["value"], sb["value"], weights=w, n=n, level=level)


def resolve(run: str, root: Path) -> Path:
    """Run folder from a path, a run id, or latest:<name> (the newest run whose id is
    <date>-<time>-<name>)."""
    if run.startswith("latest:"):
        name = run.removeprefix("latest:")
        pattern = re.compile(rf"\d{{8}}-\d{{6}}-{re.escape(name)}")
        hits = sorted(d for d in root.iterdir() if d.is_dir() and pattern.fullmatch(d.name))
        if not hits:
            raise SystemExit(f"no run named {name} in {root}")
        return hits[-1]
    return Path(run) if Path(run).is_dir() else root / run


def load_run(run: str, root: Path | None = None) -> tuple[str, Path, dict]:
    """Run id, folder and config.yaml of a run (path, id or latest:<name>; root: $RUNS_DIR)."""
    if root is None:
        from retail.runlog import runs_dir

        root = runs_dir()
    path = resolve(run, root)
    return path.name, path, yaml.safe_load((path / "config.yaml").read_text())
