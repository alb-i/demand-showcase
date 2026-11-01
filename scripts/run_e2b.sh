#!/usr/bin/env bash
# E2 extension: separate models for item and bulk demand (bulk = lines above max_order_ratio
# (10x) x the product's median line quantity before 2011-06-06), forecast = item + bulk, against the
# combined models MA(4) and TSB(0.2) on total demand; plus MA(4) and TSB(0.2) scored on item
# demand alone. Tuning origins, focus and full set.
#   bash scripts/run_e2b.sh 2>&1 | tee e2b.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
$PY scripts/split_demand.py
run() { local out; out=$($PY scripts/backtest.py "$@" | tee /dev/stderr); basename "$(head -1 <<<"$out")"; }
for set in focus full; do
  ids=()
  for m in ma4 tsb_a02 split_ma4_bulk0 split_ma4_bulkma52 split_ma4_bulktsb \
      split_tsb02_bulkma52 split_tsb02_bulktsb; do
    ids+=("$(run configs/models/$m.yaml --set $set)")
  done
  title="E2b bulk/item split vs combined ($set set, tuning origins"
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" \
    --title "$title)" --out reports/experiments/e2b_$set.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --with-bulk \
    --title "$title, products with bulk lines)" --out reports/experiments/e2b_${set}_with_bulk.md
  $PY scripts/compare_runs.py "${ids[@]}" --ref "${ids[0]}" --sb-classes intermittent lumpy \
    --title "$title, intermittent + lumpy)" \
    --out reports/experiments/e2b_${set}_intermittent_lumpy.md
  item=("$(run configs/models/ma4.yaml --set $set --target item)"
        "$(run configs/models/tsb_a02.yaml --set $set --target item)")
  $PY scripts/compare_runs.py "${item[@]}" --ref "${item[0]}" \
    --title "E2b item demand only ($set set, tuning origins)" \
    --out reports/experiments/e2b_${set}_item.md
done
