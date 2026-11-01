# E5 LightGBM quantile models (full set, tuning origins, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-p1.8-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-p1.8-full-r1 | lgbm-total-p1.8 | full | 0.742 | 0.524 | 1.962 | -1.9% | 0.479 | 0.291 | 85.4% | 95.9% |
| lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8 | full | 0.742 | 0.524 | 1.962 | -1.9% | 0.411 | 0.255 | 92.0% | 97.8% |
| split-ma4-bulk-ma52-full-r6 | split-ma4-bulk-ma52 | full | 0.765 | 0.732 | 1.961 | -87.4% | 0.489 | 0.347 | 88.8% | 96.8% |
| lgbm-total-full-r1 | lgbm-total | full | 0.779 | 0.556 | 1.967 | -9.7% | 0.481 | 0.293 | 85.5% | 95.8% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.070 [-0.079, -0.062] * |
| split-ma4-bulk-ma52-full-r6 | +0.020 [+0.007, +0.032] * | +0.202 [+0.145, +0.262] * | +0.007 [+0.001, +0.013] * |
| lgbm-total-full-r1 | +0.037 [+0.034, +0.041] * | +0.031 [+0.026, +0.037] * | +0.002 [+0.000, +0.004] * |

## MASE per segment

| segment | series | lgbm-total-p1.8-full-r1 | lgbm-total-q-p1.8-full-r1 | split-ma4-bulk-ma52-full-r6 | lgbm-total-full-r1 |
|---|---|---|---|---|---|
| A-intermittent | 26 | 0.673 | 0.673 | 0.795 | 0.716 |
| A-lumpy | 114 | 0.578 | 0.578 | 0.814 | 0.614 |
| B-intermittent | 61 | 0.553 | 0.553 | 0.584 | 0.570 |
| B-lumpy | 530 | 0.673 | 0.673 | 0.783 | 0.694 |
| C-intermittent | 605 | 0.801 | 0.801 | 0.760 | 0.865 |
| C-lumpy | 1188 | 0.771 | 0.771 | 0.763 | 0.803 |

## Per quantile level: scaled pinball / share of y <= q (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated.

| tau | lgbm-total-p1.8-full-r1 | lgbm-total-q-p1.8-full-r1 | split-ma4-bulk-ma52-full-r6 | lgbm-total-full-r1 |
|---|---|---|---|---|
| 0.025 | 0.038 / 77.3% | 0.013 / 77.0% | 0.034 / 77.3% | 0.041 / 77.3% |
| 0.05 | 0.063 / 77.5% | 0.026 / 77.0% | 0.061 / 77.5% | 0.066 / 77.5% |
| 0.1 | 0.106 / 78.1% | 0.052 / 77.0% | 0.105 / 78.0% | 0.109 / 78.0% |
| 0.2 | 0.179 / 79.3% | 0.105 / 77.2% | 0.174 / 78.9% | 0.180 / 79.1% |
| 0.5 | 0.333 / 83.7% | 0.263 / 79.7% | 0.341 / 84.1% | 0.329 / 83.0% |
| 0.8 | 0.384 / 87.0% | 0.379 / 88.4% | 0.399 / 88.5% | 0.388 / 87.0% |
| 0.9 | 0.386 / 91.3% | 0.374 / 93.2% | 0.407 / 93.5% | 0.387 / 91.0% |
| 0.95 | 0.359 / 95.3% | 0.336 / 96.2% | 0.374 / 96.6% | 0.359 / 95.2% |
| 0.975 | 0.308 / 97.4% | 0.284 / 97.8% | 0.314 / 98.1% | 0.309 / 97.3% |
| 0.99 | 0.238 / 98.6% | 0.225 / 98.9% | 0.235 / 99.0% | 0.238 / 98.6% |
