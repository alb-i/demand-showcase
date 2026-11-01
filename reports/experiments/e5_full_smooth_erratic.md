# E5 LightGBM quantile models (full set, tuning origins, smooth + erratic)

Reference for the bootstrap: `lgbm-total-p1.8-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: smooth, erratic.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-p1.8-full-r1 | lgbm-total-p1.8 | full | 0.619 | 0.683 | 0.927 | -5.5% | 0.305 | 0.329 | 84.3% | 96.0% |
| lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8 | full | 0.619 | 0.683 | 0.927 | -5.5% | 0.278 | 0.316 | 85.8% | 98.0% |
| split-ma4-bulk-ma52-full-r6 | split-ma4-bulk-ma52 | full | 0.637 | 0.717 | 0.932 | -13.8% | 0.309 | 0.329 | 89.2% | 97.2% |
| lgbm-total-full-r1 | lgbm-total | full | 0.624 | 0.687 | 0.932 | -5.0% | 0.307 | 0.332 | 84.2% | 95.9% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.046 [-0.056, -0.037] * |
| split-ma4-bulk-ma52-full-r6 | +0.015 [+0.005, +0.024] * | +0.034 [+0.024, +0.044] * | -0.003 [-0.009, +0.002] |
| lgbm-total-full-r1 | +0.008 [+0.006, +0.011] * | +0.005 [+0.002, +0.007] * | +0.004 [+0.002, +0.006] * |

## MASE per segment

| segment | series | lgbm-total-p1.8-full-r1 | lgbm-total-q-p1.8-full-r1 | split-ma4-bulk-ma52-full-r6 | lgbm-total-full-r1 |
|---|---|---|---|---|---|
| A-erratic | 448 | 0.634 | 0.634 | 0.675 | 0.640 |
| A-smooth | 364 | 0.678 | 0.678 | 0.695 | 0.676 |
| B-erratic | 434 | 0.646 | 0.646 | 0.662 | 0.653 |
| B-smooth | 120 | 0.711 | 0.711 | 0.725 | 0.715 |
| C-erratic | 122 | 0.388 | 0.388 | 0.362 | 0.402 |
| C-smooth | 132 | 0.347 | 0.347 | 0.335 | 0.362 |

## Per quantile level: scaled pinball / share of y <= q (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated.

| tau | lgbm-total-p1.8-full-r1 | lgbm-total-q-p1.8-full-r1 | split-ma4-bulk-ma52-full-r6 | lgbm-total-full-r1 |
|---|---|---|---|---|
| 0.025 | 0.027 / 28.9% | 0.018 / 28.0% | 0.026 / 28.6% | 0.028 / 28.9% |
| 0.05 | 0.049 / 29.8% | 0.036 / 28.0% | 0.048 / 29.1% | 0.051 / 29.8% |
| 0.1 | 0.091 / 32.0% | 0.070 / 29.0% | 0.086 / 30.5% | 0.092 / 32.0% |
| 0.2 | 0.161 / 37.4% | 0.130 / 34.5% | 0.152 / 34.8% | 0.163 / 37.2% |
| 0.5 | 0.282 / 58.7% | 0.259 / 59.1% | 0.278 / 59.3% | 0.285 / 57.7% |
| 0.8 | 0.277 / 80.3% | 0.273 / 85.2% | 0.292 / 85.1% | 0.280 / 79.8% |
| 0.9 | 0.233 / 89.8% | 0.221 / 92.4% | 0.245 / 92.6% | 0.233 / 89.6% |
| 0.95 | 0.181 / 94.7% | 0.170 / 96.1% | 0.189 / 96.2% | 0.181 / 94.6% |
| 0.975 | 0.135 / 97.2% | 0.126 / 98.0% | 0.139 / 97.9% | 0.135 / 97.1% |
| 0.99 | 0.088 / 98.6% | 0.088 / 99.1% | 0.088 / 99.0% | 0.088 / 98.6% |
