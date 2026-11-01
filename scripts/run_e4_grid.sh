#!/usr/bin/env bash
# E4 grid: lgbm_item with Tweedie power 1.2 / 1.8 and 15 / 63 leaves against the
# default lgbm_item run (newest, from run_e4.sh) and the split reference. Focus set, tuning
# origins. Run after run_e4.sh. Runtime roughly 50-60 min with 6 jobs.
#   bash scripts/run_e4_grid.sh 2>&1 | tee e4_grid.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
run() { local out; out=$($PY scripts/backtest.py "$@" | tee /dev/stderr); basename "$(head -1 <<<"$out")"; }
ids=(latest:lgbm-item-bulk-ma52-focus latest:split-ma4-bulk-ma52-focus)
for m in lgbm_item_p12 lgbm_item_p18 lgbm_item_l15 lgbm_item_l63; do
  ids+=("$(run configs/models/$m.yaml --set focus)")
done
$PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" \
  --title "E4 LightGBM grid (focus set, tuning origins)" --out reports/experiments/e4_grid.md
