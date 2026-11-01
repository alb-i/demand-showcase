"""Table of backtest runs and bootstrap comparisons against a reference run.

    micromamba run -n demand-showcase python scripts/compare_runs.py RUN [RUN ...] \
        --ref RUN [--title E1] [--out reports/experiments/e1.md] [--sb-classes lumpy ...]

RUN = run id (folder in $RUNS_DIR), path, or latest:<name> (the newest run of that name).
Per run: MASE, RMSSE, bias, CRPS, coverage over all evaluated rows (unweighted and revenue
weighted), MASE per segment, and the paired bootstrap of the per-series MASE and CRPS difference
to the reference (negative = better than the reference). --sb-classes restricts everything to
the series of those Syntetos-Boylan classes, --with-bulk to the products with bulk lines
(default threshold max_order_ratio, 10x median) before the segment cut-off.
Segments are taken from the current segments.parquet, not from the labels stored in the
runs, so runs made before a segment change are compared on today's classes; runs at
category level (backtest.py --level category) keep the category as their segment.
--by-category adds MASE and CRPS per product category (categories.parquet).
"""

import argparse

import numpy as np
import pandas as pd
import yaml

from retail.categories import load_categories
from retail.compare import (  # noqa: F401  (resolve: used by the tests)
    common_target,
    compare,
    relabel,
    resolve,
    select_codes,
    select_sb,
    summary,
)
from retail.io import REPO_DIR, data_dir
from retail.runlog import runs_dir
from retail.segments import split_files


def load(run: str) -> tuple[str, pd.DataFrame, dict]:
    path = resolve(run, runs_dir())
    cfg = yaml.safe_load((path / "config.yaml").read_text())
    return path.name, pd.read_parquet(path / "rows.parquet"), cfg


def bulk_products(before, ratio: float) -> set[str]:
    """Products with bulk lines (threshold `ratio`) in the weeks before the segment cut-off."""
    path, _ = split_files(data_dir() / "processed", ratio)
    split = pd.read_parquet(path)
    return set(split.loc[split["week"] < pd.Timestamp(before), "stock_code"])


def model_label(cfg: dict) -> str:
    return cfg.get("model_name") or cfg["model"].get("method", cfg["model"]["name"])


def fmt(v, pct=False) -> str:
    return "-" if pd.isna(v) else (f"{v:.1%}" if pct else f"{v:.3f}")


def ci(res: dict) -> str:
    star = " *" if res["significant"] else ""
    return f"{res['diff']:+.3f} [{res['lo']:+.3f}, {res['hi']:+.3f}]{star}"


def category_table(runs, quantiles, levels, categories: pd.Series) -> pd.DataFrame:
    """MASE and CRPS per product category (rows) and run (columns run|metric)."""
    out = {}
    for run_id, rows, _ in runs:
        r = rows.assign(category=rows["stock_code"].map(categories).fillna("other").to_numpy())
        s = summary(r, quantiles, levels, by="category")
        out[(run_id, "series")] = s["series"]
        out[(run_id, "mase")] = s["mase"]
        out[(run_id, "crps")] = s["crps"]
    return pd.DataFrame(out)


def by_category(runs, quantiles, levels) -> list[str]:
    meta = yaml.safe_load((data_dir() / "processed" / "panel_meta.json").read_text())
    categories = load_categories(data_dir() / "processed", meta["data_version"])
    table = category_table(runs, quantiles, levels, categories)
    ids = [i for i, _, _ in runs]
    lines = ["", "## MASE / CRPS per product category", "",
             "| category | series | " + " | ".join(ids) + " |",
             "|" + "---|" * (len(ids) + 2)]  # fmt: skip
    for cat, r in table.sort_values((ids[0], "series"), ascending=False).iterrows():
        cells = [f"{fmt(r[(i, 'mase')])} / {fmt(r[(i, 'crps')])}" for i in ids]
        lines.append(f"| {cat} | {r[(ids[0], 'series')]:.0f} | " + " | ".join(cells) + " |")
    return lines


def quantile_table(runs, quantiles, levels) -> pd.DataFrame:
    """Per quantile level (rows) and run: scaled pinball loss and the share of actuals at or
    below the quantile forecast (calibration: ideally = tau) and its randomised-PIT version
    (ties y = q fractional). Columns run|pinball, run|hit, run|rhit."""
    out = {}
    for run_id, rows, _ in runs:
        s = summary(rows, quantiles, levels).iloc[0]
        y = rows["y"].to_numpy(float)
        out[(run_id, "pinball")] = pd.Series({t: s[f"pinball_{t:g}"] for t in quantiles})
        out[(run_id, "hit")] = pd.Series(
            {t: float(np.mean(y <= rows[f"q{t:g}"].to_numpy(float))) for t in quantiles}
        )
        out[(run_id, "rhit")] = pd.Series({t: s[f"rhit_{t:g}"] for t in quantiles})
    return pd.DataFrame(out)


def by_quantile(runs, quantiles, levels) -> list[str]:
    table = quantile_table(runs, quantiles, levels)
    ids = [i for i, _, _ in runs]
    lines = ["", "## Per quantile level: scaled pinball / share of y <= q / randomised PIT "
             "(ideal: tau)", "",
             "Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low "
             "levels hit more often than tau even when calibrated; the randomised PIT counts "
             "such ties fractionally.", "",
             "| tau | " + " | ".join(ids) + " |", "|" + "---|" * (len(ids) + 1)]  # fmt: skip
    for tau, r in table.iterrows():
        cells = [f"{r[(i, 'pinball')]:.3f} / {r[(i, 'hit')]:.1%} / {r[(i, 'rhit')]:.1%}"
                 for i in ids]  # fmt: skip
        lines.append(f"| {tau:g} | " + " | ".join(cells) + " |")
    return lines


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("runs", nargs="+")
    p.add_argument("--ref", required=True)
    p.add_argument("--title", default="Backtest runs")
    p.add_argument("--out")
    p.add_argument("--sb-classes", nargs="+", help="only series of these classes (E2)")
    p.add_argument("--with-bulk", action="store_true", help="only products with bulk lines")
    p.add_argument("--by-category", action="store_true", help="metrics per product category")
    p.add_argument("--quantiles", action="store_true", help="pinball and hit rate per tau (E5)")
    p.add_argument("--from", dest="start", help="only origins from this date on (E6)")
    p.add_argument("--h", type=int, nargs="+", help="only these horizons (E7: sum length K)")
    a = p.parse_args()

    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    q, lv, boot = bt["quantiles"], bt["intervals"], bt["bootstrap"]
    seg_cfg = bt["segments"]
    seg = pd.read_parquet(data_dir() / "processed" / "segments.parquet").set_index("stock_code")
    labels = seg["abc"] + "-" + seg["sb_class"]  # today's segments

    def segments(rows: pd.DataFrame, cfg: dict) -> pd.DataFrame:
        if cfg.get("level") == "category":
            return rows.assign(segment=rows["stock_code"])
        return relabel(rows, labels)

    ref_id, ref_rows, ref_cfg = load(a.ref)
    ref_rows = segments(ref_rows, ref_cfg)
    runs = [(i, segments(rows, cfg), cfg) for i, rows, cfg in map(load, a.runs)]
    run_levels = {cfg.get("level", "product") for _, _, cfg in runs}
    if len(run_levels | {ref_cfg.get("level", "product")}) > 1:
        p.error("runs at product and at category level are not comparable")
    try:
        common_target([ref_cfg] + [cfg for _, _, cfg in runs])
    except ValueError as e:
        p.error(str(e))
    if a.start:
        start = pd.Timestamp(a.start)
        ref_rows = ref_rows[ref_rows["origin"] >= start]
        runs = [(i, rows[rows["origin"] >= start], cfg) for i, rows, cfg in runs]
    if a.h:
        ref_rows = ref_rows[ref_rows["h"].isin(a.h)]
        runs = [(i, rows[rows["h"].isin(a.h)], cfg) for i, rows, cfg in runs]
    if a.sb_classes:
        ref_rows = select_sb(ref_rows, a.sb_classes)
        runs = [(i, select_sb(rows, a.sb_classes), cfg) for i, rows, cfg in runs]
    if a.with_bulk:
        codes = bulk_products(
            bt["segments"]["before"], seg_cfg["syntetos_boylan"]["max_order_ratio"]
        )
        ref_rows = select_codes(ref_rows, codes)
        runs = [(i, select_codes(rows, codes), cfg) for i, rows, cfg in runs]

    lines = [f"# {a.title}", "", f"Reference for the bootstrap: `{ref_id}`. "
             "Differences: mean over series of (run - reference), 95 % CI; * = significant; "
             "negative = better. rcov = coverage under the randomised PIT (ties y = q "
             "fractional).", ""]  # fmt: skip
    if a.start:
        lines += [f"Only origins from {a.start} on.", ""]
    if a.h:
        lines += [f"Only h = {', '.join(map(str, a.h))}.", ""]
    if a.sb_classes:
        lines += [f"Only series of the Syntetos-Boylan classes: {', '.join(a.sb_classes)}.", ""]
    if a.with_bulk:
        lines += [
            f"Only products with bulk lines (> {seg_cfg['syntetos_boylan']['max_order_ratio']}x "
            f"median) before {seg_cfg['before']}.",
            "",
        ]
    head = ("| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 "
            "| rcov 80 | rcov 95 |")  # fmt: skip
    lines += [head, "|" + "---|" * 13]
    for run_id, rows, cfg in runs:
        s = summary(rows, q, lv).iloc[0]
        lines.append(
            f"| {run_id} | {model_label(cfg)} | {cfg['set']} | "
            f"{fmt(s['mase'])} | {fmt(s['mase_w'])} | {fmt(s['rmsse'])} | {fmt(s['bias'], True)} | "
            f"{fmt(s['crps'])} | {fmt(s['crps_w'])} | {fmt(s['cover_0.8'], True)} | "
            f"{fmt(s['cover_0.95'], True)} | {fmt(s.get('rcover_0.8'), True)} | "
            f"{fmt(s.get('rcover_0.95'), True)} |"
        )
    lines += ["", "## Paired bootstrap vs. the reference", "",
              "| run | MASE diff | MASE w diff | CRPS diff |", "|---|---|---|---|"]  # fmt: skip
    for run_id, rows, _ in runs:
        if run_id == ref_id:
            continue
        args = dict(quantiles=q, levels=lv, n=boot["n"], level=boot["level"])
        m = compare(rows, ref_rows, metric="abs_scaled", **args)
        mw = compare(rows, ref_rows, metric="abs_scaled", weighted=True, **args)
        c = compare(rows, ref_rows, metric="crps", **args)
        lines.append(f"| {run_id} | {ci(m)} | {ci(mw)} | {ci(c)} |")
    segs = {run_id: summary(rows, q, lv, by="segment")["mase"] for run_id, rows, _ in runs}
    table = pd.DataFrame(segs)
    n = summary(runs[0][1], q, lv, by="segment")["series"]
    lines += ["", "## MASE per segment", "",
              "| segment | series | " + " | ".join(table.columns) + " |",
              "|" + "---|" * (len(table.columns) + 2)]  # fmt: skip
    for segment, r in table.iterrows():
        lines.append(f"| {segment} | {n.get(segment, 0)} | " + " | ".join(fmt(v) for v in r) + " |")
    if a.by_category:
        lines += by_category(runs, q, lv)
    if a.quantiles:
        lines += by_quantile(runs, q, lv)
    text = "\n".join(lines) + "\n"
    print(text)
    if a.out:
        out = REPO_DIR / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)


if __name__ == "__main__":
    main()
