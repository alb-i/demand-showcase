# E5 LightGBM quantile models (focus set, tuning origins, smooth + erratic)

Reference for the bootstrap: `lgbm-total-p1.8-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: smooth, erratic.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-p1.8-focus-r1 | lgbm-total-p1.8 | focus | 0.669 | 0.693 | 0.852 | 0.3% | 0.324 | 0.338 | 84.9% | 96.3% |
| lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8 | focus | 0.669 | 0.693 | 0.852 | 0.3% | 0.308 | 0.325 | 83.0% | 97.4% |
| split-ma4-bulk-ma52-focus-r6 | split-ma4-bulk-ma52 | focus | 0.696 | 0.728 | 0.853 | -11.5% | 0.327 | 0.336 | 89.6% | 97.7% |
| lgbm-total-focus-r1 | lgbm-total | focus | 0.671 | 0.697 | 0.854 | 1.2% | 0.327 | 0.342 | 84.6% | 96.2% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.016 [-0.020, -0.011] * |
| split-ma4-bulk-ma52-focus-r6 | +0.027 [+0.017, +0.037] * | +0.034 [+0.022, +0.046] * | +0.003 [-0.001, +0.008] |
| lgbm-total-focus-r1 | +0.002 [-0.000, +0.004] | +0.004 [+0.001, +0.006] * | +0.003 [+0.002, +0.004] * |

## MASE per segment

| segment | series | lgbm-total-p1.8-focus-r1 | lgbm-total-q-p1.8-focus-r1 | split-ma4-bulk-ma52-focus-r6 | lgbm-total-focus-r1 |
|---|---|---|---|---|---|
| A-erratic | 373 | 0.660 | 0.660 | 0.699 | 0.666 |
| A-smooth | 293 | 0.680 | 0.680 | 0.691 | 0.676 |

## Per quantile level: scaled pinball / share of y <= q (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated.

| tau | lgbm-total-p1.8-focus-r1 | lgbm-total-q-p1.8-focus-r1 | split-ma4-bulk-ma52-focus-r6 | lgbm-total-focus-r1 |
|---|---|---|---|---|
| 0.025 | 0.026 / 12.0% | 0.021 / 11.3% | 0.029 / 11.9% | 0.027 / 12.0% |
| 0.05 | 0.049 / 12.8% | 0.042 / 11.3% | 0.052 / 12.5% | 0.050 / 12.8% |
| 0.1 | 0.093 / 14.9% | 0.083 / 12.9% | 0.096 / 14.2% | 0.094 / 14.9% |
| 0.2 | 0.168 / 20.3% | 0.151 / 20.6% | 0.169 / 19.6% | 0.170 / 20.1% |
| 0.5 | 0.309 / 44.6% | 0.291 / 50.7% | 0.305 / 52.2% | 0.314 / 43.0% |
| 0.8 | 0.310 / 78.0% | 0.303 / 82.2% | 0.315 / 85.0% | 0.313 / 77.3% |
| 0.9 | 0.252 / 89.7% | 0.244 / 90.5% | 0.257 / 93.3% | 0.253 / 89.3% |
| 0.95 | 0.189 / 94.8% | 0.185 / 95.0% | 0.192 / 97.0% | 0.190 / 94.7% |
| 0.975 | 0.137 / 97.3% | 0.134 / 97.4% | 0.138 / 98.5% | 0.137 / 97.3% |
| 0.99 | 0.087 / 98.8% | 0.088 / 98.8% | 0.085 / 99.3% | 0.087 / 98.8% |
