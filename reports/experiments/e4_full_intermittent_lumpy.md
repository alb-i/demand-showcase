# E4 global LightGBM (full set, tuning origins, intermittent + lumpy)

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r5`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r5 | split-ma4-bulk-ma52 | full | 0.765 | 0.732 | 1.961 | -87.4% | 0.489 | 0.347 | 88.8% | 96.8% |
| lgbm-item-bulk-ma52-full-r1 | lgbm-item-bulk-ma52 | full | 0.787 | 0.732 | 1.950 | -84.9% | 0.468 | 0.299 | 85.3% | 95.5% |
| lgbm-total-full-r1 | lgbm-total | full | 0.779 | 0.556 | 1.967 | -9.7% | 0.481 | 0.293 | 85.5% | 95.8% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.807 | 0.886 | 1.954 | -113.5% | 0.466 | 0.366 | 90.2% | 97.5% |
| ets-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10 | full | 0.850 | 0.758 | 1.980 | -102.7% | 0.534 | 0.379 | 92.6% | 96.3% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-item-bulk-ma52-full-r1 | +0.022 [+0.015, +0.029] * | +0.000 [-0.009, +0.010] | -0.020 [-0.024, -0.016] * |
| lgbm-total-full-r1 | +0.017 [+0.004, +0.030] * | -0.170 [-0.232, -0.113] * | -0.005 [-0.011, +0.001] |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | +0.043 [+0.037, +0.049] * | +0.153 [+0.119, +0.189] * | -0.022 [-0.026, -0.019] * |
| ets-bulk-ma52-r10-full-r1 | +0.084 [+0.076, +0.092] * | +0.026 [+0.008, +0.042] * | +0.045 [+0.039, +0.051] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r5 | lgbm-item-bulk-ma52-full-r1 | lgbm-total-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | ets-bulk-ma52-r10-full-r1 |
|---|---|---|---|---|---|---|
| A-intermittent | 26 | 0.795 | 0.793 | 0.716 | 0.829 | 0.812 |
| A-lumpy | 114 | 0.814 | 0.817 | 0.614 | 1.029 | 0.822 |
| B-intermittent | 61 | 0.584 | 0.603 | 0.570 | 0.615 | 0.629 |
| B-lumpy | 530 | 0.783 | 0.760 | 0.694 | 0.851 | 0.842 |
| C-intermittent | 605 | 0.760 | 0.845 | 0.865 | 0.792 | 0.869 |
| C-lumpy | 1188 | 0.763 | 0.776 | 0.803 | 0.784 | 0.859 |
