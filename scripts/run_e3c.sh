#!/usr/bin/env bash
# E3c: product categories. (1) Category level: the weekly demand of each category (sum of
# its products) forecast directly with naive, MA(4), MA(13), split MA(4) + bulk MA(52), TSB,
# ETS and ARIMA; and the bottom-up sum of the product forecasts (split ma4 + bulk ma52, full
# set) against them. (2) Product level: the split reference against the same model with
# intervals pooled per category and two top-down models (category item demand by MA(4) /
# MA(13), split by the products' shares; bulk per product by MA(52)); per-category tables.
# Tuning origins. Runtime roughly 15-20 min with 6 jobs (~50 s per category-level run, 1-2 min
# per product-level run).
#   bash scripts/run_e3c.sh 2>&1 | tee e3c.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
$PY scripts/split_demand.py
$PY scripts/categorize.py > /dev/null
run() { local out; out=$($PY scripts/backtest.py "$@" | tee /dev/stderr); basename "$(head -1 <<<"$out")"; }

cat_ids=()
for m in split_ma4_bulkma52 naive ma4 ma13 tsb_a02 ets arima; do
  cat_ids+=("$(run configs/models/$m.yaml --level category)")
done
$PY scripts/compare_runs.py "${cat_ids[@]}" --ref "${cat_ids[0]}" \
  --title "E3c category level (category totals, tuning origins)" \
  --out reports/experiments/e3c_category_level.md

for set in focus full; do
  ids=()
  for m in split_ma4_bulkma52 split_ma4_bulkma52_poolcat topdown_ma4_bulkma52 \
      topdown_ma13_bulkma52; do
    ids+=("$(run configs/models/$m.yaml --set $set)")
  done
  title="E3c pooling by category and top-down ($set set, tuning origins"
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --by-category \
    --title "$title)" --out reports/experiments/e3c_$set.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --sb-classes intermittent lumpy \
    --title "$title, intermittent + lumpy)" --out reports/experiments/e3c_${set}_intermittent_lumpy.md
  [[ $set == full ]] && full_ref=${ids[0]}
done
$PY scripts/bottom_up.py --products "$full_ref" --category "${cat_ids[@]}" \
  --title "E3c bottom-up (split ma4 + bulk ma52, full set) vs. direct category forecasts" \
  --out reports/experiments/e3c_bottom_up.md
