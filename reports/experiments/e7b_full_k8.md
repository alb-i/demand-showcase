# E7b common ties: quantiles of 8-week sums (full set, tuning origins from 2011-03-28)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 8.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-summed | full | 0.495 | 0.406 | 0.669 | -2.4% | 0.282 | 0.216 | 90.5% | 98.3% | 84.3% | 96.7% |
| lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths | full | 0.495 | 0.406 | 0.669 | -2.4% | 0.270 | 0.192 | 66.4% | 93.1% | 58.3% | 83.9% |
| lgbm-total-q-p1.8-sum-paths-ct-full-r1 | lgbm-total-q-p1.8-sum-paths-ct | full | 0.495 | 0.406 | 0.669 | -2.4% | 0.270 | 0.192 | 86.8% | 96.0% | 74.7% | 91.7% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.012 [-0.016, -0.009] * |
| lgbm-total-q-p1.8-sum-paths-ct-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.013 [-0.016, -0.010] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths-ct-full-r1 |
|---|---|---|---|---|
| A-erratic | 448 | 0.400 | 0.400 | 0.400 |
| A-intermittent | 26 | 0.450 | 0.450 | 0.450 |
| A-lumpy | 114 | 0.239 | 0.239 | 0.239 |
| A-smooth | 364 | 0.371 | 0.371 | 0.371 |
| B-erratic | 434 | 0.362 | 0.362 | 0.362 |
| B-intermittent | 61 | 0.322 | 0.322 | 0.322 |
| B-lumpy | 530 | 0.426 | 0.426 | 0.426 |
| B-smooth | 120 | 0.418 | 0.418 | 0.418 |
| C-erratic | 122 | 0.239 | 0.239 | 0.239 |
| C-intermittent | 605 | 0.804 | 0.804 | 0.804 |
| C-lumpy | 1188 | 0.575 | 0.575 | 0.575 |
| C-smooth | 132 | 0.295 | 0.295 | 0.295 |
| unclassified | 140 | 0.502 | 0.502 | 0.502 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths-ct-full-r1 |
|---|---|---|---|
| 0.025 | 0.015 / 37.6% / 1.6% | 0.015 / 38.2% / 12.6% | 0.015 / 37.7% / 4.8% |
| 0.05 | 0.030 / 37.6% / 3.2% | 0.029 / 38.8% / 21.9% | 0.029 / 38.1% / 9.2% |
| 0.1 | 0.060 / 37.7% / 6.4% | 0.055 / 40.5% / 33.7% | 0.056 / 39.6% / 17.5% |
| 0.2 | 0.112 / 38.2% / 12.9% | 0.104 / 46.8% / 44.6% | 0.103 / 44.8% / 32.6% |
| 0.5 | 0.229 / 48.9% / 40.3% | 0.216 / 66.7% / 66.6% | 0.216 / 66.7% / 66.4% |
| 0.8 | 0.266 / 79.4% / 79.2% | 0.255 / 86.4% / 86.4% | 0.256 / 86.7% / 86.7% |
| 0.9 | 0.239 / 90.8% / 90.8% | 0.227 / 92.1% / 92.1% | 0.227 / 92.2% / 92.2% |
| 0.95 | 0.195 / 96.3% / 96.3% | 0.187 / 94.9% / 94.9% | 0.186 / 95.0% / 95.0% |
| 0.975 | 0.156 / 98.3% / 98.3% | 0.150 / 96.4% / 96.4% | 0.150 / 96.5% / 96.5% |
| 0.99 | 0.110 / 99.3% / 99.3% | 0.113 / 97.6% / 97.6% | 0.111 / 97.6% / 97.6% |
