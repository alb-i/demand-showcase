# E7 quantiles of 2-week sums (full set, tuning origins from 2011-03-28)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 2.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-summed | full | 0.557 | 0.536 | 0.885 | -1.8% | 0.281 | 0.256 | 91.8% | 98.4% | 82.5% | 95.7% |
| lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths | full | 0.557 | 0.536 | 0.885 | -1.8% | 0.281 | 0.249 | 82.3% | 96.2% | 70.8% | 90.0% |
| lgbm-total-q-p1.8-sum-indep-full-r1 | lgbm-total-q-p1.8-sum-indep | full | 0.557 | 0.536 | 0.885 | -1.8% | 0.282 | 0.248 | 80.7% | 95.5% | 69.1% | 87.8% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.001 [-0.002, +0.000] |
| lgbm-total-q-p1.8-sum-indep-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.002, +0.002] |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-indep-full-r1 |
|---|---|---|---|---|
| A-erratic | 448 | 0.517 | 0.517 | 0.517 |
| A-intermittent | 26 | 0.574 | 0.574 | 0.574 |
| A-lumpy | 114 | 0.263 | 0.263 | 0.263 |
| A-smooth | 364 | 0.540 | 0.540 | 0.540 |
| B-erratic | 434 | 0.476 | 0.476 | 0.476 |
| B-intermittent | 61 | 0.391 | 0.391 | 0.391 |
| B-lumpy | 530 | 0.488 | 0.488 | 0.488 |
| B-smooth | 120 | 0.598 | 0.598 | 0.598 |
| C-erratic | 122 | 0.320 | 0.320 | 0.320 |
| C-intermittent | 605 | 0.752 | 0.752 | 0.752 |
| C-lumpy | 1188 | 0.657 | 0.657 | 0.657 |
| C-smooth | 132 | 0.390 | 0.390 | 0.390 |
| unclassified | 140 | 0.140 | 0.140 | 0.140 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-indep-full-r1 |
|---|---|---|---|
| 0.025 | 0.014 / 52.1% / 2.6% | 0.014 / 52.2% / 8.0% | 0.014 / 52.5% / 10.1% |
| 0.05 | 0.029 / 52.1% / 5.2% | 0.028 / 52.5% / 13.8% | 0.028 / 53.2% / 16.2% |
| 0.1 | 0.057 / 52.3% / 10.3% | 0.055 / 53.7% / 22.6% | 0.055 / 55.1% / 24.0% |
| 0.2 | 0.106 / 53.8% / 20.7% | 0.104 / 57.3% / 37.7% | 0.104 / 58.7% / 39.1% |
| 0.5 | 0.226 / 65.5% / 54.8% | 0.224 / 72.0% / 70.8% | 0.224 / 72.8% / 71.6% |
| 0.8 | 0.268 / 85.4% / 85.1% | 0.269 / 87.1% / 87.1% | 0.270 / 87.1% / 87.1% |
| 0.9 | 0.242 / 92.7% / 92.7% | 0.243 / 93.3% / 93.3% | 0.243 / 93.1% / 93.1% |
| 0.95 | 0.200 / 96.8% / 96.8% | 0.200 / 96.6% / 96.6% | 0.201 / 96.3% / 96.3% |
| 0.975 | 0.157 / 98.4% / 98.4% | 0.158 / 98.0% / 98.0% | 0.159 / 97.9% / 97.9% |
| 0.99 | 0.107 / 99.3% / 99.3% | 0.109 / 98.6% / 98.6% | 0.111 / 98.4% / 98.4% |
