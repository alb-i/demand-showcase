# E4 LightGBM grid (focus set, tuning origins)

Reference for the bootstrap: `lgbm-item-bulk-ma52-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-item-bulk-ma52-focus-r1 | lgbm-item-bulk-ma52 | focus | 0.730 | 0.736 | 2.724 | -12.6% | 0.353 | 0.333 | 85.4% | 96.2% |
| split-ma4-bulk-ma52-focus-r5 | split-ma4-bulk-ma52 | focus | 0.732 | 0.737 | 2.728 | -12.8% | 0.364 | 0.340 | 89.7% | 97.8% |
| lgbm-item-bulk-ma52-p1.2-focus-r1 | lgbm-item-bulk-ma52-p1.2 | focus | 0.736 | 0.742 | 2.725 | -12.4% | 0.355 | 0.335 | 85.4% | 96.2% |
| lgbm-item-bulk-ma52-p1.8-focus-r1 | lgbm-item-bulk-ma52-p1.8 | focus | 0.725 | 0.731 | 2.723 | -12.7% | 0.352 | 0.331 | 85.4% | 96.3% |
| lgbm-item-bulk-ma52-l15-focus-r1 | lgbm-item-bulk-ma52-l15 | focus | 0.729 | 0.735 | 2.724 | -11.4% | 0.354 | 0.334 | 85.2% | 96.2% |
| lgbm-item-bulk-ma52-l63-focus-r1 | lgbm-item-bulk-ma52-l63 | focus | 0.728 | 0.734 | 2.724 | -13.3% | 0.353 | 0.331 | 85.4% | 96.3% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-ma4-bulk-ma52-focus-r5 | +0.002 [-0.003, +0.008] | +0.001 [-0.007, +0.007] | +0.011 [+0.006, +0.016] * |
| lgbm-item-bulk-ma52-p1.2-focus-r1 | +0.007 [+0.005, +0.008] * | +0.006 [+0.003, +0.009] * | +0.002 [+0.001, +0.002] * |
| lgbm-item-bulk-ma52-p1.8-focus-r1 | -0.005 [-0.006, -0.003] * | -0.004 [-0.006, -0.003] * | -0.002 [-0.002, -0.001] * |
| lgbm-item-bulk-ma52-l15-focus-r1 | -0.001 [-0.002, +0.000] | -0.000 [-0.003, +0.002] | +0.001 [+0.000, +0.001] * |
| lgbm-item-bulk-ma52-l63-focus-r1 | -0.001 [-0.002, -0.000] * | -0.002 [-0.004, +0.000] | -0.001 [-0.001, -0.000] * |

## MASE per segment

| segment | series | lgbm-item-bulk-ma52-focus-r1 | split-ma4-bulk-ma52-focus-r5 | lgbm-item-bulk-ma52-p1.2-focus-r1 | lgbm-item-bulk-ma52-p1.8-focus-r1 | lgbm-item-bulk-ma52-l15-focus-r1 | lgbm-item-bulk-ma52-l63-focus-r1 |
|---|---|---|---|---|---|---|---|
| A-erratic | 373 | 0.700 | 0.699 | 0.707 | 0.696 | 0.698 | 0.699 |
| A-intermittent | 16 | 0.860 | 0.866 | 0.864 | 0.861 | 0.862 | 0.863 |
| A-lumpy | 66 | 1.046 | 1.064 | 1.087 | 1.013 | 1.065 | 1.027 |
| A-smooth | 293 | 0.689 | 0.691 | 0.688 | 0.689 | 0.684 | 0.691 |
