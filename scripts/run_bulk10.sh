#!/usr/bin/env bash
# Bulk threshold 10x everywhere (it was 20x before E3b). Reruns E1, E2, E2b and E3 on the 10x segments and the 10x
# bulk/item split (segments.parquet, demand_split_r10 and the exploration figures are regenerated
# beforehand by segment.py / split_demand.py / explore.py); E3 reuses the ETS / ARIMA 10x runs
# of E3b (run_e3.sh --reuse-stats). Overwrites the e1-e3 reports; the e3b reports stay as the
# 20x-vs-10x record. Runtime roughly 15-20 min with 6 jobs.
#   bash scripts/run_d29.sh 2>&1 | tee d29.log
set -euo pipefail
cd "$(dirname "$0")"
bash run_e1.sh
bash run_e2.sh
bash run_e2b.sh
bash run_e3.sh --reuse-stats
