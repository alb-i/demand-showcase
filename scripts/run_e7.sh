#!/usr/bin/env bash
# E7: quantiles of K-week demand sums (K = 2 = L + R, 4, 8) from the
# E5 quantile models (newest lgbm-total-q-p1.8 runs, uncalibrated): the summed per-week
# quantiles (shortcut) vs. sample paths (empirical copula of realised PIT vectors of earlier
# origins, retail.paths) vs. independent paths. Reports per K from 2011-03-28 on (every K has
# a pool of at least 5 earlier origins from then), with per-tau pinball / hit rates and the
# ratio summed / path quantile. Question: how wrong is the shortcut? No refits.
#   bash scripts/run_e7.sh 2>&1 | tee e7.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
for set in focus full; do
  out=$($PY scripts/horizon_sums.py latest:lgbm-total-q-p1.8-$set --ties independent --from 2011-03-28 \
    --out reports/experiments/e7_${set}_ratio.md | tee /dev/stderr)
  mapfile -t ids < <(grep -E '^/' <<<"$out" | xargs -n1 basename)  # summed, paths, indep
  for k in 2 4 8; do
    title="E7 quantiles of $k-week sums ($set set, tuning origins from 2011-03-28"
    $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --from 2011-03-28 \
      --h $k --title "$title)" --out reports/experiments/e7_${set}_k$k.md
    $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --from 2011-03-28 \
      --h $k --sb-classes intermittent lumpy --title "$title, intermittent + lumpy)" \
      --out reports/experiments/e7_${set}_k${k}_intermittent_lumpy.md
  done
done
