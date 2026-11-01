# E4 global LightGBM (full set, tuning origins, smooth + erratic)

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r5`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: smooth, erratic.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r5 | split-ma4-bulk-ma52 | full | 0.637 | 0.717 | 0.932 | -13.8% | 0.309 | 0.329 | 89.2% | 97.2% |
| lgbm-item-bulk-ma52-full-r1 | lgbm-item-bulk-ma52 | full | 0.633 | 0.717 | 0.916 | -14.4% | 0.302 | 0.325 | 84.4% | 95.9% |
| lgbm-total-full-r1 | lgbm-total | full | 0.624 | 0.687 | 0.932 | -5.0% | 0.307 | 0.332 | 84.2% | 95.9% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.662 | 0.760 | 0.928 | -20.5% | 0.307 | 0.335 | 89.4% | 97.3% |
| ets-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10 | full | 0.674 | 0.753 | 0.957 | -21.0% | 0.343 | 0.338 | 88.1% | 96.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-item-bulk-ma52-full-r1 | -0.009 [-0.013, -0.004] * | +0.000 [-0.005, +0.007] | -0.004 [-0.007, -0.001] * |
| lgbm-total-full-r1 | -0.007 [-0.016, +0.003] | -0.029 [-0.039, -0.019] * | +0.007 [+0.001, +0.014] * |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | +0.020 [+0.016, +0.025] * | +0.041 [+0.032, +0.051] * | -0.002 [-0.004, -0.000] * |
| ets-bulk-ma52-r10-full-r1 | +0.039 [+0.035, +0.044] * | +0.036 [+0.030, +0.041] * | +0.028 [+0.021, +0.035] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r5 | lgbm-item-bulk-ma52-full-r1 | lgbm-total-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | ets-bulk-ma52-r10-full-r1 |
|---|---|---|---|---|---|---|
| A-erratic | 448 | 0.675 | 0.682 | 0.640 | 0.728 | 0.715 |
| A-smooth | 364 | 0.695 | 0.690 | 0.676 | 0.712 | 0.729 |
| B-erratic | 434 | 0.662 | 0.643 | 0.653 | 0.675 | 0.704 |
| B-smooth | 120 | 0.725 | 0.709 | 0.715 | 0.731 | 0.764 |
| C-erratic | 122 | 0.362 | 0.360 | 0.402 | 0.362 | 0.385 |
| C-smooth | 132 | 0.335 | 0.349 | 0.362 | 0.339 | 0.354 |
