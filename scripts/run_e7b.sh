#!/usr/bin/env bash
# E7b: as E7, but the tied weeks of a past PIT vector (mostly
# y = q = 0) share one uniform and one tie-break order (--ties common), so runs of zero weeks
# stay together in the paths. Compared per K = 2, 4, 8 from 2011-03-28 on with the E7 runs
# (summed quantiles and the E7 paths, newest lgbm-total-q-p1.8-sum-{summed,paths}-<set>). Question:
# does the lower tail of the path sums on sparse series get calibrated? No refits.
#   bash scripts/run_e7b.sh 2>&1 | tee e7b.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
for set in focus full; do
  out=$($PY scripts/horizon_sums.py latest:lgbm-total-q-p1.8-$set --ties common --methods paths \
    --from 2011-03-28 --out reports/experiments/e7b_${set}_ratio.md | tee /dev/stderr)
  ct=$(grep -E '^/' <<<"$out" | head -1 | xargs basename)
  ids=(latest:lgbm-total-q-p1.8-sum-summed-$set latest:lgbm-total-q-p1.8-sum-paths-$set "$ct")
  for k in 2 4 8; do
    title="E7b common ties: quantiles of $k-week sums ($set set, tuning origins from 2011-03-28"
    $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --from 2011-03-28 \
      --h $k --title "$title)" --out reports/experiments/e7b_${set}_k$k.md
    $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --from 2011-03-28 \
      --h $k --sb-classes intermittent lumpy --title "$title, intermittent + lumpy)" \
      --out reports/experiments/e7b_${set}_k${k}_intermittent_lumpy.md
  done
done
