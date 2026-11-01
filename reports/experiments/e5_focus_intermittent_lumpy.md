# E5 LightGBM quantile models (focus set, tuning origins, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-p1.8-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-p1.8-focus-r1 | lgbm-total-p1.8 | focus | 0.826 | 0.502 | 7.867 | 30.1% | 0.602 | 0.291 | 87.8% | 96.6% |
| lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8 | focus | 0.826 | 0.502 | 7.867 | 30.1% | 0.583 | 0.271 | 84.8% | 97.1% |
| split-ma4-bulk-ma52-focus-r6 | split-ma4-bulk-ma52 | focus | 1.025 | 0.843 | 7.873 | -42.1% | 0.665 | 0.393 | 90.7% | 98.5% |
| lgbm-total-focus-r1 | lgbm-total | focus | 0.864 | 0.542 | 7.867 | 22.9% | 0.606 | 0.294 | 88.0% | 96.6% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.019 [-0.032, -0.007] * |
| split-ma4-bulk-ma52-focus-r6 | +0.200 [+0.154, +0.250] * | +0.339 [+0.182, +0.487] * | +0.063 [+0.037, +0.087] * |
| lgbm-total-focus-r1 | +0.038 [+0.030, +0.047] * | +0.038 [+0.030, +0.047] * | +0.003 [+0.001, +0.006] * |

## MASE per segment

| segment | series | lgbm-total-p1.8-focus-r1 | lgbm-total-q-p1.8-focus-r1 | split-ma4-bulk-ma52-focus-r6 | lgbm-total-focus-r1 |
|---|---|---|---|---|---|
| A-intermittent | 16 | 0.800 | 0.800 | 0.866 | 0.821 |
| A-lumpy | 66 | 0.832 | 0.832 | 1.064 | 0.874 |

## Per quantile level: scaled pinball / share of y <= q (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated.

| tau | lgbm-total-p1.8-focus-r1 | lgbm-total-q-p1.8-focus-r1 | split-ma4-bulk-ma52-focus-r6 | lgbm-total-focus-r1 |
|---|---|---|---|---|
| 0.025 | 0.024 / 51.0% | 0.022 / 50.5% | 0.025 / 50.8% | 0.024 / 50.9% |
| 0.05 | 0.047 / 51.5% | 0.043 / 50.5% | 0.054 / 51.5% | 0.047 / 51.4% |
| 0.1 | 0.093 / 52.8% | 0.087 / 50.9% | 0.117 / 53.4% | 0.093 / 52.4% |
| 0.2 | 0.182 / 55.7% | 0.173 / 52.6% | 0.219 / 57.9% | 0.182 / 55.1% |
| 0.5 | 0.391 / 65.3% | 0.391 / 62.4% | 0.443 / 74.2% | 0.394 / 64.1% |
| 0.8 | 0.504 / 81.2% | 0.499 / 82.9% | 0.560 / 88.4% | 0.510 / 81.2% |
| 0.9 | 0.513 / 91.6% | 0.484 / 90.6% | 0.563 / 95.3% | 0.517 / 91.2% |
| 0.95 | 0.479 / 95.6% | 0.448 / 95.1% | 0.519 / 98.1% | 0.481 / 95.4% |
| 0.975 | 0.421 / 97.5% | 0.406 / 97.1% | 0.455 / 99.0% | 0.422 / 97.3% |
| 0.99 | 0.357 / 98.9% | 0.362 / 98.4% | 0.372 / 99.6% | 0.358 / 98.8% |
