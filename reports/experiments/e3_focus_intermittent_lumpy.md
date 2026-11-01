# E3 ETS / ARIMA (focus set, tuning origins, intermittent + lumpy)

Reference for the bootstrap: `split-ma4-bulk-ma52-focus-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-focus-r3 | split-ma4-bulk-ma52 | focus | 1.025 | 0.843 | 7.873 | -42.1% | 0.665 | 0.393 | 90.7% | 98.5% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 1.214 | 1.102 | 7.877 | -66.2% | 0.708 | 0.462 | 89.1% | 98.4% |
| ets-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10 | focus | 1.037 | 0.817 | 7.871 | -41.7% | 0.668 | 0.378 | 91.6% | 97.1% |
| arima-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10 | focus | 1.088 | 0.907 | 7.872 | -47.1% | 0.671 | 0.388 | 92.4% | 97.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | +0.189 [+0.137, +0.242] * | +0.258 [+0.156, +0.354] * | +0.042 [+0.027, +0.059] * |
| ets-bulk-ma52-r10-focus-r1 | +0.012 [-0.013, +0.038] | -0.027 [-0.072, +0.024] | +0.002 [-0.015, +0.020] |
| arima-bulk-ma52-r10-focus-r1 | +0.063 [+0.024, +0.106] * | +0.063 [-0.003, +0.132] | +0.005 [-0.015, +0.025] |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-focus-r3 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | ets-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10-focus-r1 |
|---|---|---|---|---|---|
| A-intermittent | 16 | 0.866 | 0.856 | 0.896 | 0.892 |
| A-lumpy | 66 | 1.064 | 1.301 | 1.071 | 1.136 |
