"""Quantiles of horizon sums: summed quantiles vs. sample paths (E7).

    micromamba run -n demand-showcase python scripts/horizon_sums.py RUN [RUN ...] \
        [--k 2 4 8] [--paths 1000] [--min-pool 100] [--seed 0] [--ties independent|common] \
        [--methods summed paths indep] [--out REPORT.md]

RUN [RUN ...]: run folders, ids or latest:<name> of one quantile model and set (several:
pooled, e.g. the tuning and the test run, so the paths of the test origins learn from the
tuning origins too; a test run among them gives the name suffix -test), e.g. the E5 model
lgbm-total-q-p1.8 or the E9 composite best-crps. Writes three runs <model>-sum-<method>-<set>
(method: summed, paths, indep; retail.paths) whose rows are the
K-week sums at h = K, so compare_runs.py --h K reports them like a backtest. Paths come only
from realised PIT vectors of earlier origins (pool per segment label); the summed shortcut
exists at every origin. --out: a Markdown table of how much the summed quantiles overstate
(or understate) the path quantiles. Paths are not stored (seeded, reproducible).
--ties common (E7b; the default): tied weeks of a PIT vector share one uniform; the
path runs are named <model>-sum-<method>-ct-<set>. --methods: which runs to write.
"""

import argparse
import json

import pandas as pd
import yaml

from retail.backtest import group_metrics
from retail.compare import load_run
from retail.io import REPO_DIR, data_dir
from retail.paths import METHODS, horizon_sums, overstatement
from retail.runlog import RunLogger


def ratio_table(ratios: pd.DataFrame) -> list[str]:
    lines = ["| K | tau | rows | median summed / path | weighted summed / path |",
             "|---|---|---|---|---|"]  # fmt: skip
    for _, r in ratios.iterrows():
        lines.append(f"| {r['K']:.0f} | {r['tau']:g} | {r['n']:.0f} | {r['median_ratio']:.3f} "
                     f"| {r['weighted_ratio']:.3f} |")  # fmt: skip
    return lines


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("runs", nargs="+", help="runs of one model and set, e.g. tuning + test")
    p.add_argument("--k", type=int, nargs="+", default=[2, 4, 8])
    p.add_argument("--paths", type=int, default=1000)
    p.add_argument("--min-pool", type=int, default=100)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--ties",
        choices=["independent", "common"],
        default="common",
        help="common (default): one uniform per PIT vector for tied weeks (E7b); "
        "independent: as in E7",
    )
    p.add_argument("--methods", nargs="+", choices=METHODS, default=list(METHODS))
    p.add_argument("--from", dest="start", help="ratio table only from this origin on")
    p.add_argument("--out")
    a = p.parse_args()

    loaded = [load_run(r) for r in a.runs]
    if len({(c["model_name"], c["set"]) for _, _, c in loaded}) > 1:
        p.error("runs of different models or sets")
    ids = [i for i, _, _ in loaded]
    run_id, folder, cfg = loaded[-1]
    test = any(c.get("origins") == "test" for _, _, c in loaded)
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    q, lv = bt["quantiles"], bt["intervals"]
    rows = pd.concat([pd.read_parquet(f / "rows.parquet") for _, f, _ in loaded],
                     ignore_index=True)  # fmt: skip
    if rows.duplicated(["stock_code", "origin", "h"]).any():
        p.error("the runs share origins")
    seg = pd.read_parquet(data_dir() / "processed" / "segments.parquet").set_index("stock_code")
    labels = seg["abc"] + "-" + seg["sb_class"]
    frames, info = horizon_sums(rows, q, a.k, labels, a.paths, a.min_pool, a.seed,
                                common_ties=a.ties == "common")  # fmt: skip
    suffix = "-ct" if a.ties == "common" else ""
    meta_version = json.loads((folder / "meta.json").read_text())["dataset_version"]

    def segment_of(codes: pd.Series) -> pd.Series:
        return codes.map(labels).fillna("unclassified")

    for method in a.methods:
        r = frames[method]
        model_name = f"{cfg['model_name']}-sum-{method}{suffix if method != 'summed' else ''}"
        config = cfg | {
            "model_name": model_name,
            "model_description": (cfg.get("model_description") or "")
            + f" Quantiles of K-week sums (h = K), method {method} (E7).",
            "horizon_sums": {"source_runs": ids, "method": method, "k": a.k,
                             "n_paths": a.paths, "min_pool": a.min_pool, "seed": a.seed,
                             "ties": a.ties},
            "horizons": a.k,
            "n_origins": int(r["origin"].nunique()),
            "origins": "test" if test else cfg.get("origins", "tuning"),
        }  # fmt: skip
        with RunLogger(config, name=f"{model_name}-{cfg['set']}{'-test' if test else ''}",
                       data_version=meta_version) as run:  # fmt: skip
            print(run.dir)
            for origin, g in r.groupby("origin"):
                for rec in group_metrics(g, q, lv, segment_of):
                    run.log(origin=str(origin.date()), model=model_name, **rec)
            for rec in group_metrics(r, q, lv, segment_of):
                run.log(origin="all", model=model_name, **rec)
            run.write_parquet("forecasts", r.drop(columns=["y"]))
            run.write_parquet("rows", r.assign(segment=segment_of(r["stock_code"])))
    print(info.pivot(index="origin", columns="k", values="n_pool").to_string())
    if a.out:
        s, pth = frames["summed"], frames["paths"]
        if a.start:
            s, pth = (f[f["origin"] >= pd.Timestamp(a.start)] for f in (s, pth))
        text = "\n".join([
            f"# Summed quantiles vs. path quantiles ({cfg['model_name']}, {cfg['set']} set"
            + (f", origins from {a.start}" if a.start else "") + ")", "",
            f"Source runs {', '.join(f'`{i}`' for i in ids)}; {a.paths} paths per series and "
            "origin. Ratio > 1: the sum of the per-week quantiles is above the quantile of the "
            "sum (paths).", "",
            *ratio_table(overstatement(s, pth, q)), ""])  # fmt: skip
        out = REPO_DIR / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(text)


if __name__ == "__main__":
    main()
