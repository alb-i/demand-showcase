#!/usr/bin/env bash
# E2: Croston, SBA, TSB (alpha 0.1 and 0.2) against MA(4), the best E1
# baseline, on the tuning origins, focus set and full set. Reports per set: all series and only
# the intermittent + lumpy series (the question of E2). Reference: MA(4).
#   bash scripts/run_e2.sh 2>&1 | tee e2.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
for set in focus full; do
  ids=()
  for m in ma4 croston_a01 croston_a02 sba_a01 sba_a02 tsb_a01 tsb_a02; do
    out=$($PY scripts/backtest.py configs/models/$m.yaml --set $set | tee /dev/stderr)
    ids+=("$(basename "$(head -1 <<<"$out")")")
  done
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" \
    --title "E2 intermittent methods ($set set, tuning origins)" --out reports/experiments/e2_$set.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --sb-classes intermittent lumpy \
    --title "E2 intermittent methods ($set set, intermittent + lumpy, tuning origins)" \
    --out reports/experiments/e2_${set}_intermittent_lumpy.md
done
