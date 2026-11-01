# E3 ETS / ARIMA (full set, tuning origins, intermittent + lumpy)

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r3 | split-ma4-bulk-ma52 | full | 0.765 | 0.732 | 1.961 | -87.4% | 0.489 | 0.347 | 88.8% | 96.8% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.807 | 0.886 | 1.954 | -113.5% | 0.466 | 0.366 | 90.2% | 97.5% |
| ets-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10 | full | 0.850 | 0.758 | 1.980 | -102.7% | 0.534 | 0.379 | 92.6% | 96.3% |
| arima-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10 | full | 0.853 | 0.806 | 1.976 | -106.8% | 0.534 | 0.382 | 93.1% | 96.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | +0.043 [+0.037, +0.049] * | +0.153 [+0.119, +0.189] * | -0.022 [-0.026, -0.019] * |
| ets-bulk-ma52-r10-full-r1 | +0.084 [+0.076, +0.092] * | +0.026 [+0.008, +0.042] * | +0.045 [+0.039, +0.051] * |
| arima-bulk-ma52-r10-full-r1 | +0.087 [+0.077, +0.097] * | +0.074 [+0.053, +0.096] * | +0.045 [+0.036, +0.058] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r3 | split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | ets-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10-full-r1 |
|---|---|---|---|---|---|
| A-intermittent | 26 | 0.795 | 0.829 | 0.812 | 0.825 |
| A-lumpy | 114 | 0.814 | 1.029 | 0.822 | 0.883 |
| B-intermittent | 61 | 0.584 | 0.615 | 0.629 | 0.645 |
| B-lumpy | 530 | 0.783 | 0.851 | 0.842 | 0.875 |
| C-intermittent | 605 | 0.760 | 0.792 | 0.869 | 0.855 |
| C-lumpy | 1188 | 0.763 | 0.784 | 0.859 | 0.851 |
