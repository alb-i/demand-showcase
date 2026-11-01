"""Rolling conformal calibration of a run's quantile forecasts (E6).

    micromamba run -n demand-showcase python scripts/calibrate.py RUN [RUN ...] \
        [--window 13] [--min-pool 100] [--pool segment|all]

RUN: run folders, ids or latest:<name> of one model and set (e.g. the tuning and later the
test origins); their rows are pooled, so a later run is calibrated from the earlier one too.
At every origin the offsets come only from rows whose target week is before it
(retail.calibration). Writes a new run <model>-cqr<window>[-all]-<set> with rows.parquet,
forecasts.parquet and metrics.jsonl like a backtest run (config: the source config plus
`calibration`), and prints the calibration rows per origin.
"""

import argparse
import json

import pandas as pd
import yaml

from retail.backtest import group_metrics
from retail.calibration import calibrate
from retail.compare import load_run
from retail.io import REPO_DIR, data_dir
from retail.runlog import RunLogger


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("runs", nargs="+")
    p.add_argument("--window", type=int, default=13, help="weeks of earlier origins")
    p.add_argument("--min-pool", type=int, default=100)
    p.add_argument("--pool", choices=["segment", "all"], default="segment")
    a = p.parse_args()

    loaded = [load_run(r) for r in a.runs]
    cfgs = [cfg for _, _, cfg in loaded]
    names = {(c["model_name"], c["set"], c.get("target", "total")) for c in cfgs}
    if len(names) > 1:
        p.error(f"runs of different models / sets / targets: {sorted(names)}")
    cfg = cfgs[0]
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    q, lv = bt["quantiles"], bt["intervals"]
    rows = pd.concat([pd.read_parquet(d / "rows.parquet") for _, d, _ in loaded],
                     ignore_index=True)  # fmt: skip
    fc = pd.concat([pd.read_parquet(d / "forecasts.parquet") for _, d, _ in loaded],
                   ignore_index=True)  # fmt: skip
    seg = pd.read_parquet(data_dir() / "processed" / "segments.parquet").set_index("stock_code")
    labels = seg["abc"] + "-" + seg["sb_class"]
    pool = labels if a.pool == "segment" else None
    cal_rows, info = calibrate(rows, q, pool, a.window, a.min_pool)
    cal_fc, _ = calibrate(rows, q, pool, a.window, a.min_pool, targets=fc)
    meta = json.loads((loaded[0][1] / "meta.json").read_text())
    suffix = f"-cqr{a.window}{'-all' if a.pool == 'all' else ''}"
    model_name = cfg["model_name"] + suffix
    config = cfg | {
        "model_name": model_name,
        "model_description": (cfg.get("model_description") or "")
        + f" Rolling conformal calibration per quantile level (E6): offsets from the "
        f"last {a.window} weeks of earlier origins, pooled per {a.pool} x h (min "
        f"{a.min_pool}).",
        "calibration": {
            "source_runs": [i for i, _, _ in loaded],
            "window_weeks": a.window,
            "min_pool": a.min_pool,
            "pool": a.pool,
        },  # fmt: skip
        "n_origins": int(rows["origin"].nunique()),
    }

    def segment_of(codes: pd.Series) -> pd.Series:
        return codes.map(labels).fillna("unclassified")

    with RunLogger(config, name=f"{model_name}-{cfg['set']}",
                   data_version=meta["dataset_version"]) as run:  # fmt: skip
        print(run.dir)
        for origin, r in cal_rows.groupby("origin"):
            for rec in group_metrics(r, q, lv, segment_of):
                run.log(origin=str(origin.date()), model=model_name, **rec)
        for rec in group_metrics(cal_rows, q, lv, segment_of):
            run.log(origin="all", model=model_name, **rec)
        run.write_parquet("forecasts", cal_fc)
        run.write_parquet("rows", cal_rows.assign(segment=segment_of(cal_rows["stock_code"])))
    print(info.to_string(index=False))


if __name__ == "__main__":
    main()
