# E3b bulk threshold 10x vs 20x (focus set, tuning origins, intermittent + lumpy)

> Record of the 20x vs 10x comparison; run before 10x became the only threshold: segments and the "products with bulk lines" here are still the 20x ones.

Reference for the bootstrap: `split-ma4-bulk-ma52-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-focus-r1 | split-ma4-bulk-ma52 | focus | 0.978 | 0.755 | 7.921 | -32.8% | 0.668 | 0.385 | 90.5% | 98.6% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 1.197 | 1.079 | 7.925 | -63.3% | 0.715 | 0.471 | 88.9% | 98.2% |
| ets-bulk-ma52-focus-r1 | ets-bulk-ma52 | focus | 0.999 | 0.730 | 7.919 | -33.4% | 0.681 | 0.384 | 92.3% | 97.3% |
| arima-bulk-ma52-focus-r1 | arima-bulk-ma52 | focus | 1.069 | 0.813 | 7.920 | -37.5% | 0.689 | 0.392 | 92.8% | 97.5% |
| split-ma4-bulk-ma52-r10-focus-r1 | split-ma4-bulk-ma52-r10 | focus | 1.034 | 0.851 | 7.921 | -42.0% | 0.671 | 0.395 | 90.7% | 98.5% |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10 | focus | 1.224 | 1.112 | 7.925 | -66.1% | 0.714 | 0.465 | 89.1% | 98.4% |
| ets-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10 | focus | 1.045 | 0.823 | 7.919 | -41.6% | 0.674 | 0.381 | 91.5% | 97.1% |
| arima-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10 | focus | 1.095 | 0.913 | 7.920 | -46.9% | 0.677 | 0.391 | 92.3% | 97.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r1 | +0.219 [+0.162, +0.282] * | +0.322 [+0.181, +0.470] * | +0.047 [+0.029, +0.067] * |
| ets-bulk-ma52-focus-r1 | +0.021 [-0.008, +0.052] | -0.026 [-0.086, +0.038] | +0.013 [-0.005, +0.031] |
| arima-bulk-ma52-focus-r1 | +0.091 [+0.037, +0.150] * | +0.058 [-0.009, +0.139] | +0.021 [-0.007, +0.048] |
| split-ma4-bulk-ma52-r10-focus-r1 | +0.056 [+0.032, +0.082] * | +0.095 [+0.040, +0.161] * | +0.003 [-0.004, +0.010] |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-focus-r1 | +0.246 [+0.178, +0.319] * | +0.355 [+0.200, +0.519] * | +0.046 [+0.028, +0.066] * |
| ets-bulk-ma52-r10-focus-r1 | +0.067 [+0.035, +0.099] * | +0.067 [+0.020, +0.108] * | +0.006 [-0.014, +0.026] |
| arima-bulk-ma52-r10-focus-r1 | +0.118 [+0.068, +0.166] * | +0.156 [+0.059, +0.253] * | +0.009 [-0.015, +0.032] |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r1 | ets-bulk-ma52-focus-r1 | arima-bulk-ma52-focus-r1 | split-ma4-bulk-ma52-r10-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10-focus-r1 |
|---|---|---|---|---|---|---|---|---|---|
| A-intermittent | 12 | 0.991 | 0.971 | 1.010 | 0.993 | 0.978 | 0.965 | 1.002 | 0.989 |
| A-lumpy | 69 | 0.975 | 1.236 | 0.997 | 1.082 | 1.043 | 1.269 | 1.052 | 1.114 |
