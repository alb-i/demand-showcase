#!/usr/bin/env bash
# E9: every tuning model once on the 26 test origins (Jun-Nov 2011), the
# per-segment selection fixed beforehand on the tuning origins (configs/selection.yaml, committed
# before this run), the composite best-crps, final numbers with paired-bootstrap CIs, and the
# sample-path sums (K = 2, 4, 8, common ties; pool rolling over tuning + earlier test origins).
# All backtests share one pool of 6 workers (scripts/run_batch.py), so the cores stay busy.
# Restartable: finished test runs are skipped, so after a crash simply start it again.
# Runtime estimate ~7-8 h (quantile LightGBM and ARIMA on the full set dominate): overnight.
#   bash scripts/run_e9.sh 2>&1 | tee -a e9.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
REP=reports/experiments
FROM=2011-06-06   # first test origin
$PY scripts/run_batch.py configs/batches/e9.yaml --origins test --final
# lgbm-total-q-p1.8 ran on the full set only; its focus run is cut out (forecasts do not depend
# on the set)
if ! ls "$($PY -c 'from retail.runlog import runs_dir; print(runs_dir())')" | grep -qE '^[0-9]{8}-[0-9]{6}-lgbm-total-q-p1\.8-focus-test$'; then
  $PY scripts/subset_run.py latest:lgbm-total-q-p1.8-full-test
fi
for set in focus full; do
  $PY scripts/select_models.py compose --set $set --origins tuning
  $PY scripts/select_models.py compose --set $set --origins test
  mapfile -t names < <($PY scripts/select_models.py names --set $set)
  all=(latest:best-crps-$set-test)
  for n in "${names[@]}"; do all+=("latest:$n-$set-test"); done
  short=(latest:best-crps-$set-test latest:lgbm-total-q-p1.8-$set-test latest:ma4-$set-test
         latest:naive-$set-test latest:snaive-$set-test)
  t="E9 test origins ($set set"
  $PY scripts/compare_runs.py "${all[@]}" --ref "${all[0]}" --title "$t, all models)" \
    --out $REP/e9_${set}_all.md
  $PY scripts/compare_runs.py "${all[@]}" --ref "${all[0]}" --sb-classes intermittent lumpy \
    --title "$t, all models, intermittent + lumpy)" --out $REP/e9_${set}_all_intermittent_lumpy.md
  $PY scripts/compare_runs.py "${short[@]}" --ref latest:snaive-$set-test --quantiles \
    --title "$t, vs. seasonal naive)" --out $REP/e9_${set}_vs_snaive.md
  $PY scripts/compare_runs.py "${short[@]}" --ref latest:ma4-$set-test --quantiles \
    --title "$t, vs. MA(4))" --out $REP/e9_${set}_vs_ma4.md
  # horizon sums on the test origins, PIT pool from tuning + earlier test origins
  out=$($PY scripts/horizon_sums.py latest:best-crps-$set latest:best-crps-$set-test \
    --from $FROM --out $REP/e9_${set}_sums_ratio.md | tee /dev/stderr)
  mapfile -t ids < <(grep -E '^/' <<<"$out" | xargs -n1 basename)  # summed, paths, indep
  for k in 2 4 8; do
    $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --quantiles --from $FROM --h $k \
      --title "E9 quantiles of $k-week sums ($set set, test origins)" \
      --out $REP/e9_${set}_sums_k$k.md
  done
done
