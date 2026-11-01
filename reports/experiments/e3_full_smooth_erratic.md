# E3 ETS / ARIMA (full set, tuning origins, smooth + erratic)

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: smooth, erratic.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r3 | split-ma4-bulk-ma52 | full | 0.637 | 0.717 | 0.932 | -13.8% | 0.309 | 0.329 | 89.2% | 97.2% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.662 | 0.760 | 0.928 | -20.5% | 0.307 | 0.335 | 89.4% | 97.3% |
| ets-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10 | full | 0.674 | 0.753 | 0.957 | -21.0% | 0.343 | 0.338 | 88.1% | 96.4% |
| arima-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10 | full | 0.702 | 0.790 | 0.946 | -27.8% | 0.359 | 0.345 | 87.5% | 96.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | +0.020 [+0.016, +0.025] * | +0.041 [+0.032, +0.051] * | -0.002 [-0.004, -0.000] * |
| ets-bulk-ma52-r10-full-r1 | +0.039 [+0.035, +0.044] * | +0.036 [+0.030, +0.041] * | +0.028 [+0.021, +0.035] * |
| arima-bulk-ma52-r10-full-r1 | +0.063 [+0.056, +0.069] * | +0.072 [+0.063, +0.083] * | +0.048 [+0.037, +0.062] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r3 | split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | ets-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10-full-r1 |
|---|---|---|---|---|---|
| A-erratic | 448 | 0.675 | 0.728 | 0.715 | 0.752 |
| A-smooth | 364 | 0.695 | 0.712 | 0.729 | 0.760 |
| B-erratic | 434 | 0.662 | 0.675 | 0.704 | 0.716 |
| B-smooth | 120 | 0.725 | 0.731 | 0.764 | 0.782 |
| C-erratic | 122 | 0.362 | 0.362 | 0.385 | 0.437 |
| C-smooth | 132 | 0.335 | 0.339 | 0.354 | 0.382 |
