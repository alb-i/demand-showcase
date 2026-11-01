# E7b common ties: quantiles of 4-week sums (full set, tuning origins from 2011-03-28)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 4.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-summed | full | 0.510 | 0.457 | 0.721 | -2.3% | 0.269 | 0.231 | 91.8% | 98.4% | 84.4% | 96.4% |
| lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths | full | 0.510 | 0.457 | 0.721 | -2.3% | 0.264 | 0.216 | 85.6% | 92.1% | 63.4% | 86.3% |
| lgbm-total-q-p1.8-sum-paths-ct-full-r1 | lgbm-total-q-p1.8-sum-paths-ct | full | 0.510 | 0.457 | 0.721 | -2.3% | 0.265 | 0.216 | 88.8% | 96.6% | 75.8% | 92.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.006 [-0.008, -0.003] * |
| lgbm-total-q-p1.8-sum-paths-ct-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.005 [-0.008, -0.003] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths-ct-full-r1 |
|---|---|---|---|---|
| A-erratic | 448 | 0.455 | 0.455 | 0.455 |
| A-intermittent | 26 | 0.494 | 0.494 | 0.494 |
| A-lumpy | 114 | 0.244 | 0.244 | 0.244 |
| A-smooth | 364 | 0.429 | 0.429 | 0.429 |
| B-erratic | 434 | 0.400 | 0.400 | 0.400 |
| B-intermittent | 61 | 0.327 | 0.327 | 0.327 |
| B-lumpy | 530 | 0.450 | 0.450 | 0.450 |
| B-smooth | 120 | 0.482 | 0.482 | 0.482 |
| C-erratic | 122 | 0.267 | 0.267 | 0.267 |
| C-intermittent | 605 | 0.761 | 0.761 | 0.761 |
| C-lumpy | 1188 | 0.613 | 0.613 | 0.613 |
| C-smooth | 132 | 0.318 | 0.318 | 0.318 |
| unclassified | 140 | 0.170 | 0.170 | 0.170 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths-ct-full-r1 |
|---|---|---|---|
| 0.025 | 0.015 / 44.2% / 2.0% | 0.015 / 44.6% / 10.9% | 0.015 / 44.3% / 4.7% |
| 0.05 | 0.029 / 44.2% / 3.9% | 0.028 / 45.2% / 17.1% | 0.028 / 44.6% / 9.0% |
| 0.1 | 0.057 / 44.3% / 7.9% | 0.054 / 46.8% / 29.8% | 0.054 / 46.0% / 17.5% |
| 0.2 | 0.107 / 45.1% / 15.9% | 0.101 / 51.4% / 46.7% | 0.101 / 50.3% / 33.3% |
| 0.5 | 0.220 / 57.0% / 47.2% | 0.212 / 69.1% / 68.5% | 0.212 / 69.5% / 68.5% |
| 0.8 | 0.256 / 82.9% / 82.7% | 0.253 / 87.1% / 87.1% | 0.254 / 87.4% / 87.4% |
| 0.9 | 0.230 / 92.2% / 92.2% | 0.225 / 93.3% / 93.3% | 0.225 / 93.3% / 93.3% |
| 0.95 | 0.186 / 96.7% / 96.7% | 0.185 / 96.0% / 96.0% | 0.184 / 96.0% / 96.0% |
| 0.975 | 0.145 / 98.4% / 98.4% | 0.145 / 97.2% / 97.2% | 0.145 / 97.2% / 97.2% |
| 0.99 | 0.101 / 99.4% / 99.4% | 0.103 / 98.0% / 98.0% | 0.105 / 98.1% / 98.1% |
