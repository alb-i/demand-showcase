# E3 ETS / ARIMA (focus set, tuning origins)

Reference for the bootstrap: `split-ma4-bulk-ma52-focus-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-focus-r3 | split-ma4-bulk-ma52 | focus | 0.732 | 0.737 | 2.728 | -12.8% | 0.364 | 0.340 | 89.7% | 97.8% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 0.786 | 0.798 | 2.731 | -20.4% | 0.372 | 0.353 | 88.9% | 97.7% |
| ets-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10 | focus | 0.769 | 0.768 | 2.732 | -20.0% | 0.370 | 0.343 | 86.4% | 96.9% |
| arima-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10 | focus | 0.808 | 0.814 | 2.733 | -27.2% | 0.374 | 0.352 | 85.9% | 97.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | +0.054 [+0.045, +0.063] * | +0.060 [+0.046, +0.076] * | +0.008 [+0.004, +0.011] * |
| ets-bulk-ma52-r10-focus-r1 | +0.037 [+0.031, +0.043] * | +0.030 [+0.022, +0.038] * | +0.005 [+0.002, +0.009] * |
| arima-bulk-ma52-r10-focus-r1 | +0.076 [+0.067, +0.084] * | +0.076 [+0.064, +0.089] * | +0.009 [+0.006, +0.013] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-focus-r3 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | ets-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10-focus-r1 |
|---|---|---|---|---|---|
| A-erratic | 373 | 0.699 | 0.751 | 0.741 | 0.781 |
| A-intermittent | 16 | 0.866 | 0.856 | 0.896 | 0.892 |
| A-lumpy | 66 | 1.064 | 1.301 | 1.071 | 1.136 |
| A-smooth | 293 | 0.691 | 0.711 | 0.729 | 0.763 |
