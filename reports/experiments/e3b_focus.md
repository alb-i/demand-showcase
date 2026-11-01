# E3b bulk threshold 10x vs 20x (focus set, tuning origins)

> Record of the 20x vs 10x comparison; run before 10x became the only threshold: segments and the "products with bulk lines" here are still the 20x ones.

Reference for the bootstrap: `split-ma4-bulk-ma52-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-focus-r1 | split-ma4-bulk-ma52 | focus | 0.723 | 0.727 | 2.731 | -9.5% | 0.370 | 0.346 | 89.2% | 97.6% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 0.777 | 0.790 | 2.732 | -18.1% | 0.376 | 0.358 | 88.6% | 97.4% |
| ets-bulk-ma52-focus-r1 | ets-bulk-ma52 | focus | 0.764 | 0.762 | 2.735 | -18.7% | 0.378 | 0.352 | 87.6% | 96.7% |
| arima-bulk-ma52-focus-r1 | arima-bulk-ma52 | focus | 0.808 | 0.810 | 2.735 | -26.5% | 0.380 | 0.356 | 88.0% | 97.1% |
| split-ma4-bulk-ma52-r10-focus-r1 | split-ma4-bulk-ma52-r10 | focus | 0.732 | 0.737 | 2.728 | -12.8% | 0.365 | 0.340 | 89.7% | 97.7% |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10 | focus | 0.786 | 0.798 | 2.731 | -20.4% | 0.372 | 0.353 | 89.0% | 97.7% |
| ets-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10 | focus | 0.769 | 0.768 | 2.732 | -20.0% | 0.370 | 0.343 | 86.4% | 96.9% |
| arima-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10 | focus | 0.808 | 0.814 | 2.733 | -27.2% | 0.374 | 0.352 | 85.9% | 97.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r1 | +0.054 [+0.043, +0.065] * | +0.062 [+0.044, +0.083] * | +0.006 [+0.002, +0.010] * |
| ets-bulk-ma52-focus-r1 | +0.042 [+0.034, +0.049] * | +0.034 [+0.024, +0.043] * | +0.008 [+0.003, +0.012] * |
| arima-bulk-ma52-focus-r1 | +0.085 [+0.074, +0.097] * | +0.083 [+0.066, +0.099] * | +0.010 [+0.005, +0.014] * |
| split-ma4-bulk-ma52-r10-focus-r1 | +0.009 [+0.004, +0.014] * | +0.011 [+0.002, +0.020] * | -0.006 [-0.008, -0.003] * |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-focus-r1 | +0.063 [+0.051, +0.076] * | +0.071 [+0.050, +0.094] * | +0.002 [-0.003, +0.006] |
| ets-bulk-ma52-r10-focus-r1 | +0.046 [+0.038, +0.054] * | +0.041 [+0.031, +0.051] * | -0.000 [-0.005, +0.004] |
| arima-bulk-ma52-r10-focus-r1 | +0.085 [+0.073, +0.096] * | +0.087 [+0.070, +0.104] * | +0.003 [-0.001, +0.008] |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r1 | ets-bulk-ma52-focus-r1 | arima-bulk-ma52-focus-r1 | split-ma4-bulk-ma52-r10-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10-focus-r1 |
|---|---|---|---|---|---|---|---|---|---|
| A-erratic | 452 | 0.682 | 0.726 | 0.731 | 0.774 | 0.689 | 0.735 | 0.731 | 0.769 |
| A-intermittent | 12 | 0.991 | 0.971 | 1.010 | 0.993 | 0.978 | 0.965 | 1.002 | 0.989 |
| A-lumpy | 69 | 0.975 | 1.236 | 0.997 | 1.082 | 1.043 | 1.269 | 1.052 | 1.114 |
| A-smooth | 215 | 0.712 | 0.724 | 0.746 | 0.783 | 0.709 | 0.728 | 0.744 | 0.781 |
