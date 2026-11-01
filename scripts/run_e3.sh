#!/usr/bin/env bash
# E3: ETS and auto-ARIMA per series (statsforecast) on item demand plus
# the bulk part, own intervals, against the E2b split models (reference: ma4 + bulk
# ma52). Tuning origins, focus and full set, origins in parallel (--jobs default 6).
# Runtime roughly 90-110 min, most of it ARIMA on the full set (~15-20 min per origin and core).
# --reuse-stats: no new ETS / ARIMA runs, the newest 10x runs of E3b instead (ets-bulk-ma52-r10,
# arima-bulk-ma52-r10; their forecasts do not depend on the segments), ~3 min.
#   bash scripts/run_e3.sh 2>&1 | tee e3.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
$PY scripts/split_demand.py
for set in focus full; do
  ids=()
  models=(split_ma4_bulkma52 split_tsb02_bulkma52 ets arima)
  [[ "${1:-}" == "--reuse-stats" ]] && models=("${models[@]:0:2}")
  for m in "${models[@]}"; do
    out=$($PY scripts/backtest.py configs/models/$m.yaml --set $set | tee /dev/stderr)
    ids+=("$(basename "$(head -1 <<<"$out")")")
  done
  [[ "${1:-}" == "--reuse-stats" ]] && ids+=(latest:ets-bulk-ma52-r10-$set latest:arima-bulk-ma52-r10-$set)
  title="E3 ETS / ARIMA ($set set, tuning origins"
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" \
    --title "$title)" --out reports/experiments/e3_$set.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --sb-classes smooth erratic \
    --title "$title, smooth + erratic)" --out reports/experiments/e3_${set}_smooth_erratic.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --sb-classes intermittent lumpy \
    --title "$title, intermittent + lumpy)" \
    --out reports/experiments/e3_${set}_intermittent_lumpy.md
done
