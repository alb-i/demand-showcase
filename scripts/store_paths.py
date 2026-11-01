"""Store the sample paths of the P-quantile policy for the workbench what-if.

    micromamba run -n demand-showcase python scripts/store_paths.py [--origins tuning test] \
        [--k 2 3 4 5]

The weekly path values of the selected model (configs/costs.yaml policies.quantile: source,
n_paths, min_pool, seed; common ties) on the focus set, generated exactly as by
scripts/simulate_policies.py: the tuning origins from the tuning rows only, the test origins
from tuning + test rows (pool rolling over both). So the tau-quantile of a stored K-week
sum equals the order-up-to level of the P5 simulation with L = K - R.
Writes $DATA_DIR/paths/<model>-focus/K<k>/<origin>.npz (codes, values: float32 products x
n_paths x K) for the simulated weeks (tuning from simulation.tuning_from, all test origins) and
index.json (source runs, settings, origins).
"""

import argparse
import json
import time

import numpy as np
import pandas as pd
import yaml
from simulate_policies import source_rows  # scripts/simulate_policies.py

from retail.inventory.costs import load_costs
from retail.io import REPO_DIR, data_dir
from retail.paths import horizon_sums


class Writer:
    """Collects the per-label path blocks of one (origin, K) and writes them as one file."""

    def __init__(self, root, keep):
        self.root, self.keep, self.key, self.parts, self.written = root, keep, None, [], []

    def __call__(self, origin, k, codes, values):
        if not self.keep(origin):
            return
        if (origin, k) != self.key:
            self.flush()
            self.key = (origin, k)
        self.parts.append((np.asarray(codes, dtype=str), values.astype(np.float32)))

    def flush(self):
        if self.key is None:
            return
        origin, k = self.key
        codes = np.concatenate([c for c, _ in self.parts])
        values = np.concatenate([v for _, v in self.parts])
        order = np.argsort(codes)
        d = self.root / f"K{k}"
        d.mkdir(parents=True, exist_ok=True)
        np.savez(d / f"{origin.date()}.npz", codes=codes[order], values=values[order])
        self.written.append((str(origin.date()), k, len(codes)))
        self.key, self.parts = None, []


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--origins", nargs="+", choices=["tuning", "test"], default=["tuning", "test"])
    p.add_argument("--k", type=int, nargs="+", default=[2, 3, 4, 5])
    a = p.parse_args()
    _, cfg = load_costs()
    qcfg, sim = cfg["policies"]["quantile"], cfg["simulation"]
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    seg = pd.read_parquet(data_dir() / "processed" / "segments.parquet").set_index("stock_code")
    labels = seg["abc"] + "-" + seg["sb_class"]
    root = data_dir() / "paths" / f"{qcfg['source']}-focus"
    index = {"model": qcfg["source"], "set": "focus", "ties": "common",
             "n_paths": qcfg["n_paths"], "min_pool": qcfg["min_pool"], "seed": qcfg["seed"],
             "k": a.k, "origins": {}, "source_runs": {}}  # fmt: skip
    if (root / "index.json").exists():
        index = json.loads((root / "index.json").read_text()) | {"k": a.k}
    for origins in a.origins:
        t0 = time.time()
        rows, ids, _ = source_rows(qcfg["source"], origins)
        first = pd.Timestamp(sim[f"{origins}_from"])
        last = pd.Timestamp(bt["origins"][origins]["to"])
        writer = Writer(root, lambda o, f=first, la=last: f <= o <= la)
        horizon_sums(rows, bt["quantiles"], ks=tuple(a.k), labels=labels, n_paths=qcfg["n_paths"],
                     min_pool=qcfg["min_pool"], seed=qcfg["seed"], common_ties=True,
                     sampled=("paths",), on_paths=writer)  # fmt: skip
        writer.flush()
        index["origins"][origins] = sorted({o for o, _, _ in writer.written})
        index["source_runs"][origins] = ids
        print(f"{origins}: {len(writer.written)} files (K {a.k}), "
              f"{time.time() - t0:.0f} s", flush=True)  # fmt: skip
    (root / "index.json").write_text(json.dumps(index, indent=1))
    print(root)


if __name__ == "__main__":
    main()
