#!/usr/bin/env bash
# Leaderboards for the workbench: focus and full set, tuning and test origins
# -> $DATA_DIR/processed/leaderboard_<set>_<origins>.parquet (scripts/leaderboard.py).
# Rerun after new backtest runs. Runtime: focus ~20 s each, full set a few minutes each.
#   bash scripts/build_leaderboards.sh 2>&1 | tee -a leaderboard.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
for set in focus full; do
  for origins in test tuning; do
    $PY scripts/leaderboard.py --set "$set" --origins "$origins"
  done
done
