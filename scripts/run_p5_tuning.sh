#!/usr/bin/env bash
# Inventory simulation, step 1: on the tuning weeks
# (2011-03-28..05-30, focus set) for L = 1, 2, 4: P-naive (buffers), P-normal (alphas) and
# P-quantile (taus of the sample-path sums of lgbm-total-q-p1.8) from configs/costs.yaml; then
# the operating points (P-quantile / P-normal at the smallest value whose fill rate reaches
# P-naive buffer 0) -> configs/operating_point.yaml, and the report reports/experiments/
# p5_tuning.md + reports/figures/p5_frontier_tuning.pdf/.png.
# Runtime ~2-3 min. Afterwards: review, commit configs/operating_point.yaml, then run_p5_test.sh.
#   bash scripts/run_p5_tuning.sh 2>&1 | tee -a p5.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
$PY scripts/simulate_policies.py --origins tuning --lead-time 1 2 4
$PY scripts/policy_report.py select --lead-time 1 2 4
$PY scripts/policy_report.py report --origins tuning --lead-time 1 2 4
