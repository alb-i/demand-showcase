"""Leaderboard file for the workbench.

    micromamba run -n demand-showcase python scripts/leaderboard.py --set focus|full \
        [--origins tuning|test] [--reference snaive]

Models: the newest finished backtest run of every model on the set and origins (total target;
no calibration, horizon-sum or simulation runs; composites such as best-crps included).
Segments relabelled from the current segments.parquet (as compare_runs). Writes
$DATA_DIR/processed/leaderboard_<set>_<origins>.parquet: one row per model and segment with the
metrics of retail.compare.summary, the paired bootstrap of MASE and CRPS against --reference
and the run id; the workbench reads it (time-series adapter).
"""

import argparse
import json
import re
import time

import pandas as pd
import yaml

from retail.compare import relabel
from retail.io import REPO_DIR, data_dir
from retail.leaderboard import leaderboard
from retail.runlog import runs_dir

SKIP = {"calibration", "horizon_sums", "simulation"}


def newest_runs(set_: str, origins: str) -> dict[str, tuple[str, dict]]:
    """model name -> (run id, config) of the newest finished backtest run on set_ / origins."""
    suffix = "-test" if origins == "test" else ""
    out = {}
    for d in sorted(runs_dir().iterdir()):
        if not re.fullmatch(rf"\d{{8}}-\d{{6}}-.+-{set_}{suffix}", d.name):
            continue
        if not (d / "meta.json").exists() or not (d / "rows.parquet").exists():
            continue
        if json.loads((d / "meta.json").read_text()).get("status") != "finished":
            continue
        cfg = yaml.safe_load((d / "config.yaml").read_text()) or {}
        if SKIP & set(cfg) or "n_origins" not in cfg or cfg.get("set") != set_:
            continue
        if cfg.get("origins", "tuning") != origins or cfg.get("target", "total") != "total":
            continue
        name = d.name.removesuffix(f"-{set_}{suffix}").split("-", 2)[2]
        if cfg.get("model_name", name) != name:
            continue  # e.g. focus cut of a full run under another name
        out[name] = (d.name, cfg)  # sorted by id: the newest wins
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--set", choices=["focus", "full"], default="focus")
    p.add_argument("--origins", choices=["tuning", "test"], default="test")
    p.add_argument("--reference", default="snaive")
    p.add_argument("--n", type=int, default=2000)
    a = p.parse_args()
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    q, lv = bt["quantiles"], bt["intervals"]
    seg = pd.read_parquet(data_dir() / "processed" / "segments.parquet").set_index("stock_code")
    labels = seg["abc"] + "-" + seg["sb_class"]
    found = newest_runs(a.set, a.origins)
    if a.reference not in found:
        raise SystemExit(f"no {a.origins} run of the reference {a.reference} on {a.set}")
    t0 = time.time()
    runs = {m: relabel(pd.read_parquet(runs_dir() / rid / "rows.parquet"), labels)
            for m, (rid, _) in found.items()}  # fmt: skip
    lb = leaderboard(runs, a.reference, q, lv, n=a.n)
    lb["run_id"] = lb["model"].map({m: rid for m, (rid, _) in found.items()})
    lb["description"] = lb["model"].map(
        {m: (cfg.get("model_description") or "") for m, (_, cfg) in found.items()})  # fmt: skip
    lb = lb.assign(set=a.set, origins=a.origins, reference=a.reference)
    out = data_dir() / "processed" / f"leaderboard_{a.set}_{a.origins}.parquet"
    lb.to_parquet(out)
    allrows = lb[lb["segment"] == "all"].sort_values("crps")
    print(allrows[["model", "mase", "crps", "rcover_0.8", "rcover_0.95", "crps_diff", "crps_sig"]]
          .round(3).to_string(index=False))  # fmt: skip
    print(f"{len(found)} models, {lb['segment'].nunique()} segments -> {out} "
          f"({time.time() - t0:.0f} s)")  # fmt: skip


if __name__ == "__main__":
    main()
