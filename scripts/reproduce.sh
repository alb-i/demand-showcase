#!/usr/bin/env bash
# Reproduce the headline results (README "Reproduce in 3 commands"): data pipeline, the selected
# model (LightGBM quantile models on total demand, Tweedie power 1.8) on the focus set for the 22
# tuning and the 26 test origins, and the test simulation of the three order policies at the
# committed operating points (configs/operating_point.yaml, fixed on the tuning weeks).
# Writes run folders to $RUNS_DIR and reports/experiments/p5_test.md, reports/figures/
# p5_frontier_test.*. Runtime ~3.5 h on 12 cores (LightGBM dominates); each start makes new
# run folders, so rerun only the stage that failed (tmux).
#   bash scripts/reproduce.sh [data|forecasts|policies ...]   (default: all three stages)
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
stages=("$@")
[ ${#stages[@]} -eq 0 ] && stages=(data forecasts policies)
for stage in "${stages[@]}"; do
  case $stage in
    data)       # raw download (checksums), xlsx -> parquet, cleaning, weekly panel, segments,
                # categories, bulk/item split (the model's units_bulk feature)
      $PY scripts/download_data.py
      $PY scripts/import_raw.py
      $PY scripts/build_panel.py
      $PY scripts/segment.py
      $PY scripts/categorize.py
      $PY scripts/split_demand.py ;;
    forecasts)  # the model trains on all products; --set focus only selects the evaluated rows
      $PY scripts/backtest.py configs/models/lgbm_total_q.yaml --set focus --origins tuning
      $PY scripts/backtest.py configs/models/lgbm_total_q.yaml --set focus --origins test --final ;;
    policies)   # P-naive, P-normal, P-quantile on the test weeks, L = 1, 2, 4
      $PY scripts/simulate_policies.py --origins test --final --lead-time 1 2 4
      $PY scripts/policy_report.py report --origins test --lead-time 1 2 4 ;;
    *) echo "unknown stage $stage (data, forecasts, policies)" >&2; exit 2 ;;
  esac
done
