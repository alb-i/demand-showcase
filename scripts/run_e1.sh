#!/usr/bin/env bash
# E1: naive, seasonal naive, moving averages 4/8/13 on the tuning
# origins, focus set and full set; then the comparison tables (reference: naive).
#   bash scripts/run_e1.sh 2>&1 | tee e1.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
for set in focus full; do
  ids=()
  for m in naive snaive ma4 ma8 ma13; do
    out=$($PY scripts/backtest.py configs/models/$m.yaml --set $set | tee /dev/stderr)
    ids+=("$(basename "$(head -1 <<<"$out")")")
  done
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" \
    --title "E1 baselines ($set set, tuning origins)" --out reports/experiments/e1_$set.md
done
