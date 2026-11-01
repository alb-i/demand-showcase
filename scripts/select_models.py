"""Model per segment on the tuning origins, and the composite run (E9).

    micromamba run -n demand-showcase python scripts/select_models.py select \
        [--batch configs/batches/e9.yaml] [--set full] [--metric crps] \
        [--out configs/selection.yaml]
    micromamba run -n demand-showcase python scripts/select_models.py compose \
        --set focus|full [--origins tuning|test] [--selection configs/selection.yaml]

select: the candidates are the models of the batch file; for each, the newest finished tuning
run on --set; per ABC x SB segment the lowest mean --metric wins (retail.selection). Writes the
winners, the table and the source run ids to --out (to commit before the test runs).
names: the model names of the batch on --set (one per line).
compose: the run best-<metric>-<set>[-test] whose rows per product come from the winner of the
product's segment (newest finished run of that model on the set and origins).
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml
from backtest import prepare  # scripts/backtest.py

from retail.backtest import group_metrics
from retail.compare import load_run
from retail.io import REPO_DIR, data_dir
from retail.runlog import RunLogger
from retail.selection import compose, segment_table, winners


def labels() -> pd.Series:
    seg = pd.read_parquet(data_dir() / "processed" / "segments.parquet").set_index("stock_code")
    return seg["abc"] + "-" + seg["sb_class"]


def model_names(batch: Path, set_: str) -> list[str]:
    """Model names (run name without the set) of the batch's runs on set_, in batch order."""
    cache: dict = {}
    out = []
    for r in yaml.safe_load(batch.read_text())["runs"]:
        if r["set"] != set_ or r.get("target", "total") != "total":
            continue
        name = prepare(REPO_DIR / r["config"], set_, "tuning", cache=cache).config["model_name"]
        if name not in out:
            out.append(name)
    return out


def latest(name: str, set_: str, origins: str) -> tuple[str, Path, dict]:
    return load_run(f"latest:{name}-{set_}{'-test' if origins == 'test' else ''}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["select", "compose", "names"])
    p.add_argument("--batch", default="configs/batches/e9.yaml")
    p.add_argument("--set", default="full", choices=["focus", "full"])
    p.add_argument("--origins", default="tuning", choices=["tuning", "test"])
    p.add_argument("--metric", default="crps")
    p.add_argument("--selection", default="configs/selection.yaml")
    p.add_argument("--out", default="configs/selection.yaml")
    a = p.parse_args()
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    q, lv = bt["quantiles"], bt["intervals"]
    lab = labels()

    if a.mode == "names":  # the batch's model names on --set, one per line (run_e9.sh)
        print("\n".join(model_names(REPO_DIR / a.batch, a.set)))
        return
    if a.mode == "select":
        names = model_names(REPO_DIR / a.batch, a.set)
        runs, ids = {}, {}
        for n in names:
            ids[n], path, cfg = latest(n, a.set, "tuning")
            runs[n] = pd.read_parquet(path / "rows.parquet")
            if cfg.get("origins", "tuning") != "tuning":
                sys.exit(f"{ids[n]} is not a tuning run")
        table = segment_table(runs, q, lv, lab, a.metric)
        win = winners(table)
        out = {
            "decision": "model per ABC x SB segment by the lowest mean tuning "
            f"{a.metric} on the {a.set} set (E9)",
            "metric": a.metric,
            "set": a.set,
            "winners": {str(k): str(v) for k, v in win.items()},
            "fallback": str(win.value_counts().idxmax()),
            "source_runs": ids,
            "table": {
                str(s): {m: round(float(v), 4) for m, v in r.items()} for s, r in table.iterrows()
            },  # fmt: skip
        }
        (REPO_DIR / a.out).write_text(yaml.safe_dump(out, sort_keys=False, width=100))
        print(table.round(3).to_string())
        for s, m in win.items():
            print(f"{s}: {m}")
        return

    sel = yaml.safe_load((REPO_DIR / a.selection).read_text())
    win = pd.Series(sel["winners"])
    runs, fcs, ids = {}, {}, {}
    data_version = None
    for n in sorted(set(win) | {sel["fallback"]}):
        ids[n], path, cfg = latest(n, a.set, a.origins)
        if cfg.get("origins", "tuning") != a.origins:
            sys.exit(f"{ids[n]}: origins {cfg.get('origins')} != {a.origins}")
        runs[n] = pd.read_parquet(path / "rows.parquet")
        fcs[n] = pd.read_parquet(path / "forecasts.parquet")
        data_version = json.loads((path / "meta.json").read_text())["dataset_version"]
    rows = compose(runs, win, lab, sel["fallback"])
    forecasts = compose(fcs, win, lab, sel["fallback"])
    model_name = f"best-{sel['metric']}"
    config = {
        "model_name": model_name,
        "model_description": f"Composite (E9): per ABC x SB segment the model with the "
        f"lowest tuning {sel['metric']}: " + ", ".join(f"{s} {m}" for s, m in win.items()),
        "selection": sel | {"composed_from": ids},
        "target": "total",
        "level": "product",
        "set": a.set,
        "origins": a.origins,
        "n_origins": int(rows["origin"].nunique()),
    }
    name = f"{model_name}-{a.set}{'-test' if a.origins == 'test' else ''}"

    def segment_of(codes: pd.Series) -> pd.Series:
        return codes.map(lab).fillna("unclassified")

    with RunLogger(config, name=name, data_version=data_version) as run:
        print(run.dir)
        for origin, g in rows.groupby("origin"):
            for rec in group_metrics(g, q, lv, segment_of):
                run.log(origin=str(origin.date()), model=model_name, **rec)
        for rec in group_metrics(rows, q, lv, segment_of):
            run.log(origin="all", model=model_name, **rec)
        run.write_parquet("forecasts", forecasts)
        run.write_parquet("rows", rows.assign(segment=segment_of(rows["stock_code"])))
    print(rows["source"].value_counts().to_string())


if __name__ == "__main__":
    main()
