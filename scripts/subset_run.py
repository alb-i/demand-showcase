"""A run of the focus set cut out of a full-set run (E9).

    micromamba run -n demand-showcase python scripts/subset_run.py RUN [--set focus]

Only for models whose forecasts of a product do not depend on the evaluated set: the global
LightGBM quantile models (trained on all products, no intervals pooled over the set; the
tuning runs of lgbm-total-q-p1.8 on focus and full agree to 0.0). Writes <model>-focus[-test]
with the focus rows and forecasts and their metrics; config: the source config with set: focus
and derived_from.
"""

import argparse
import json
import sys

import pandas as pd
import yaml

from retail.backtest import group_metrics
from retail.compare import load_run
from retail.io import REPO_DIR, data_dir
from retail.runlog import RunLogger

ALLOWED = ("lgbm-total-q",)  # model name prefixes whose forecasts do not depend on the set


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("run")
    p.add_argument("--set", default="focus", choices=["focus"])
    a = p.parse_args()
    run_id, path, cfg = load_run(a.run)
    if cfg["set"] != "full" or not cfg["model_name"].startswith(ALLOWED):
        sys.exit(f"{run_id}: only full-set runs of {ALLOWED} can be cut to the focus set")
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    q, lv = bt["quantiles"], bt["intervals"]
    codes = set(bt["focus_set"]["stock_codes"])
    seg = pd.read_parquet(data_dir() / "processed" / "segments.parquet").set_index("stock_code")
    lab = seg["abc"] + "-" + seg["sb_class"]
    rows = pd.read_parquet(path / "rows.parquet")
    rows = rows[rows["stock_code"].isin(codes)]
    fc = pd.read_parquet(path / "forecasts.parquet")
    fc = fc[fc["stock_code"].isin(codes)]
    meta = json.loads((path / "meta.json").read_text())
    config = cfg | {"set": a.set, "derived_from": run_id}
    name = f"{cfg['model_name']}-{a.set}{'-test' if cfg.get('origins') == 'test' else ''}"

    def segment_of(c: pd.Series) -> pd.Series:
        return c.map(lab).fillna("unclassified")

    with RunLogger(config, name=name, data_version=meta["dataset_version"]) as run:
        print(run.dir)
        for origin, g in rows.groupby("origin"):
            for rec in group_metrics(g, q, lv, segment_of):
                run.log(origin=str(origin.date()), model=cfg["model_name"], **rec)
        for rec in group_metrics(rows, q, lv, segment_of):
            run.log(origin="all", model=cfg["model_name"], **rec)
        run.write_parquet("forecasts", fc)
        run.write_parquet("rows", rows)


if __name__ == "__main__":
    main()
