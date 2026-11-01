#!/usr/bin/env bash
# Inventory simulation, step 2: the test simulation, run once (2011-06-06..11-28, focus
# set, L = 1, 2, 4, the whole grid of configs/costs.yaml), with the operating points fixed on
# the tuning weeks (configs/operating_point.yaml, must be committed before this run); P-quantile
# paths pool over tuning + earlier test origins. Report reports/experiments/p5_test.md +
# reports/figures/p5_frontier_test.pdf/.png (operating points vs. P-naive with paired bootstrap,
# frontiers, sensitivity margin x holding x L, write-down 0/50/100 %).
# Runtime ~3-5 min.
#   bash scripts/run_p5_test.sh 2>&1 | tee -a p5.log
set -euo pipefail
cd "$(dirname "$0")/.."
PY="micromamba run -n demand-showcase python"
if ! git ls-files --error-unmatch configs/operating_point.yaml >/dev/null 2>&1 \
   || ! git diff --quiet HEAD -- configs/operating_point.yaml configs/costs.yaml; then
  echo "configs/operating_point.yaml and configs/costs.yaml must be committed first" >&2
  exit 1
fi
$PY scripts/simulate_policies.py --origins test --final --lead-time 1 2 4
$PY scripts/policy_report.py report --origins test --lead-time 1 2 4
