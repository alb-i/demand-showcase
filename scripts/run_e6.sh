#!/usr/bin/env bash
# E6: rolling conformal calibration per quantile level of the E5
# quantile models (newest lgbm-total-q-p1.8 runs), offsets from earlier origins only (target
# weeks before the origin). Variants: window 13 / 26 weeks, pooled per segment x h or over all
# products x h. Reports on all tuning origins and from 2011-03-28 on (every horizon has at least
# 4 calibration origins from then), with per-tau pinball / hit rates (y <= q and randomised
# PIT). Question: coverage within +-3 pp of nominal? Runtime roughly 10 min (no refits).
#   bash scripts/run_e6.sh 2>&1 | tee e6.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
cal() { local out; out=$($PY scripts/calibrate.py "$@" | tee /dev/stderr); basename "$(head -1 <<<"$out")"; }
for set in focus full; do
  src=latest:lgbm-total-q-p1.8-$set
  ids=("$src")
  for w in 13 26; do
    for pool in segment all; do
      ids+=("$(cal "$src" --window $w --pool $pool)")
    done
  done
  title="E6 conformal calibration of the E5 quantile models ($set set, tuning origins"
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles \
    --title "$title)" --out reports/experiments/e6_$set.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --from 2011-03-28 \
    --title "$title from 2011-03-28)" --out reports/experiments/e6_${set}_from0328.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --from 2011-03-28 \
    --sb-classes intermittent lumpy --title "$title from 2011-03-28, intermittent + lumpy)" \
    --out reports/experiments/e6_${set}_from0328_intermittent_lumpy.md
done
