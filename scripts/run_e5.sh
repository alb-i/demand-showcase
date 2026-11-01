#!/usr/bin/env bash
# E5: LightGBM quantile models on total demand (one pinball model
# per quantile level, sorted per row; mean from the Tweedie model, power 1.8), before any
# calibration (E6). Reference: lgbm_total_p18 (same mean, out-of-sample pooled intervals as in
# E4), so the CRPS / pinball / coverage differences come from the quantile models alone; also
# the split reference (rerun) and lgbm_total of E4 (power 1.5, newest run). Tuning origins,
# focus and full set; per-tau pinball and hit rates (--quantiles). Runtime roughly 2.5 h with
# 6 jobs (one quantile-model origin ~15-19 min per core: 11 fits of ~1.7 min).
#   bash scripts/run_e5.sh 2>&1 | tee e5.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
$PY scripts/split_demand.py
$PY scripts/categorize.py > /dev/null
run() { local out; out=$($PY scripts/backtest.py "$@" | tee /dev/stderr); basename "$(head -1 <<<"$out")"; }
for set in focus full; do
  ids=()
  for m in lgbm_total_p18 lgbm_total_q split_ma4_bulkma52; do
    ids+=("$(run configs/models/$m.yaml --set $set)")
  done
  ids+=(latest:lgbm-total-$set)
  title="E5 LightGBM quantile models ($set set, tuning origins"
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --by-category \
    --title "$title)" --out reports/experiments/e5_$set.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --sb-classes smooth erratic \
    --title "$title, smooth + erratic)" --out reports/experiments/e5_${set}_smooth_erratic.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --sb-classes intermittent lumpy \
    --title "$title, intermittent + lumpy)" \
    --out reports/experiments/e5_${set}_intermittent_lumpy.md
done
