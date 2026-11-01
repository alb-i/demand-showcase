#!/usr/bin/env bash
# E4: global LightGBM point forecast, refitted at every origin on
# all products, two targets: item demand + bulk MA(52) and total demand directly;
# intervals from out-of-sample errors (second fit 13 weeks earlier). References: split
# MA(4) + bulk MA(52) (rerun), split TSB(0.2) + bulk MA(52) and ETS (newest runs). Tuning
# origins, focus and full set (the model is trained on all products either way; the set only
# chooses the evaluated products). Runtime roughly 50-60 min with 6 jobs (one LightGBM origin
# ~2.5-3.5 min per core, 4 rounds of 6 origins per run, 4 LightGBM runs).
#   bash scripts/run_e4.sh 2>&1 | tee e4.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
$PY scripts/split_demand.py
$PY scripts/categorize.py > /dev/null
run() { local out; out=$($PY scripts/backtest.py "$@" | tee /dev/stderr); basename "$(head -1 <<<"$out")"; }
for set in focus full; do
  ids=()
  for m in split_ma4_bulkma52 lgbm_item lgbm_total; do
    ids+=("$(run configs/models/$m.yaml --set $set)")
  done
  ids+=(latest:split-tsb-a0.2-b0.2-bulk-ma52-$set latest:ets-bulk-ma52-r10-$set)
  title="E4 global LightGBM ($set set, tuning origins"
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --by-category \
    --title "$title)" --out reports/experiments/e4_$set.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --sb-classes smooth erratic \
    --title "$title, smooth + erratic)" --out reports/experiments/e4_${set}_smooth_erratic.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --sb-classes intermittent lumpy \
    --title "$title, intermittent + lumpy)" \
    --out reports/experiments/e4_${set}_intermittent_lumpy.md
done
