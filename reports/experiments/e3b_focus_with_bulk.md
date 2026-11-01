# E3b bulk threshold 10x vs 20x (focus set, tuning origins, products with bulk lines)

> Record of the 20x vs 10x comparison; run before 10x became the only threshold: segments and the "products with bulk lines" here are still the 20x ones.

Reference for the bootstrap: `split-ma4-bulk-ma52-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only products with bulk lines (> 20x median) before 2011-06-06.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-focus-r1 | split-ma4-bulk-ma52 | focus | 0.734 | 0.728 | 2.963 | -10.8% | 0.380 | 0.347 | 89.7% | 97.6% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 0.788 | 0.794 | 2.964 | -19.4% | 0.386 | 0.360 | 88.9% | 97.4% |
| ets-bulk-ma52-focus-r1 | ets-bulk-ma52 | focus | 0.775 | 0.762 | 2.966 | -20.1% | 0.386 | 0.350 | 87.1% | 96.8% |
| arima-bulk-ma52-focus-r1 | arima-bulk-ma52 | focus | 0.816 | 0.809 | 2.966 | -27.5% | 0.386 | 0.355 | 87.5% | 97.1% |
| split-ma4-bulk-ma52-r10-focus-r1 | split-ma4-bulk-ma52-r10 | focus | 0.744 | 0.740 | 2.961 | -14.1% | 0.375 | 0.341 | 90.1% | 97.8% |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10 | focus | 0.796 | 0.802 | 2.963 | -21.6% | 0.382 | 0.355 | 89.3% | 97.7% |
| ets-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10 | focus | 0.778 | 0.768 | 2.962 | -21.2% | 0.377 | 0.341 | 86.1% | 96.9% |
| arima-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10 | focus | 0.815 | 0.814 | 2.964 | -28.2% | 0.380 | 0.352 | 85.6% | 97.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r1 | +0.053 [+0.043, +0.064] * | +0.065 [+0.045, +0.087] * | +0.006 [+0.002, +0.010] * |
| ets-bulk-ma52-focus-r1 | +0.041 [+0.034, +0.049] * | +0.033 [+0.023, +0.044] * | +0.006 [+0.001, +0.010] * |
| arima-bulk-ma52-focus-r1 | +0.082 [+0.069, +0.094] * | +0.080 [+0.063, +0.098] * | +0.006 [+0.001, +0.011] * |
| split-ma4-bulk-ma52-r10-focus-r1 | +0.010 [+0.005, +0.015] * | +0.012 [+0.003, +0.023] * | -0.006 [-0.008, -0.003] * |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-focus-r1 | +0.062 [+0.050, +0.074] * | +0.073 [+0.050, +0.098] * | +0.002 [-0.002, +0.007] |
| ets-bulk-ma52-r10-focus-r1 | +0.043 [+0.036, +0.052] * | +0.039 [+0.029, +0.050] * | -0.003 [-0.008, +0.002] |
| arima-bulk-ma52-r10-focus-r1 | +0.081 [+0.070, +0.092] * | +0.086 [+0.068, +0.105] * | +0.000 [-0.005, +0.005] |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r1 | ets-bulk-ma52-focus-r1 | arima-bulk-ma52-focus-r1 | split-ma4-bulk-ma52-r10-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10-focus-r1 |
|---|---|---|---|---|---|---|---|---|---|
| A-erratic | 381 | 0.680 | 0.728 | 0.727 | 0.769 | 0.689 | 0.738 | 0.728 | 0.766 |
| A-intermittent | 9 | 0.982 | 0.976 | 1.009 | 0.973 | 0.965 | 0.967 | 0.998 | 0.968 |
| A-lumpy | 51 | 1.198 | 1.435 | 1.207 | 1.284 | 1.258 | 1.459 | 1.253 | 1.312 |
| A-smooth | 187 | 0.708 | 0.723 | 0.745 | 0.776 | 0.706 | 0.727 | 0.739 | 0.774 |
