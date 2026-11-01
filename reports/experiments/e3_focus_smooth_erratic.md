# E3 ETS / ARIMA (focus set, tuning origins, smooth + erratic)

Reference for the bootstrap: `split-ma4-bulk-ma52-focus-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: smooth, erratic.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-focus-r3 | split-ma4-bulk-ma52 | focus | 0.696 | 0.728 | 0.853 | -11.5% | 0.327 | 0.336 | 89.6% | 97.7% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 0.733 | 0.773 | 0.857 | -18.4% | 0.331 | 0.344 | 88.9% | 97.6% |
| ets-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10 | focus | 0.735 | 0.764 | 0.870 | -19.0% | 0.333 | 0.340 | 85.7% | 96.9% |
| arima-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10 | focus | 0.773 | 0.806 | 0.872 | -26.3% | 0.337 | 0.349 | 85.1% | 97.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | +0.037 [+0.031, +0.045] * | +0.043 [+0.033, +0.056] * | +0.003 [+0.001, +0.007] * |
| ets-bulk-ma52-r10-focus-r1 | +0.040 [+0.034, +0.045] * | +0.035 [+0.028, +0.041] * | +0.006 [+0.003, +0.009] * |
| arima-bulk-ma52-r10-focus-r1 | +0.077 [+0.069, +0.086] * | +0.078 [+0.066, +0.090] * | +0.010 [+0.007, +0.013] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-focus-r3 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | ets-bulk-ma52-r10-focus-r1 | arima-bulk-ma52-r10-focus-r1 |
|---|---|---|---|---|---|
| A-erratic | 373 | 0.699 | 0.751 | 0.741 | 0.781 |
| A-smooth | 293 | 0.691 | 0.711 | 0.729 | 0.763 |
