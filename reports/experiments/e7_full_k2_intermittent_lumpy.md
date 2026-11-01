# E7 quantiles of 2-week sums (full set, tuning origins from 2011-03-28, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 2.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-summed | full | 0.619 | 0.411 | 1.006 | 6.4% | 0.328 | 0.196 | 91.7% | 98.0% | 79.4% | 94.8% |
| lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths | full | 0.619 | 0.411 | 1.006 | 6.4% | 0.329 | 0.196 | 79.8% | 96.3% | 65.0% | 87.6% |
| lgbm-total-q-p1.8-sum-indep-full-r1 | lgbm-total-q-p1.8-sum-indep | full | 0.619 | 0.411 | 1.006 | 6.4% | 0.331 | 0.197 | 79.4% | 96.1% | 64.6% | 84.8% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.001 [-0.001, +0.004] |
| lgbm-total-q-p1.8-sum-indep-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.003 [+0.000, +0.007] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-indep-full-r1 |
|---|---|---|---|---|
| A-intermittent | 26 | 0.574 | 0.574 | 0.574 |
| A-lumpy | 114 | 0.263 | 0.263 | 0.263 |
| B-intermittent | 61 | 0.391 | 0.391 | 0.391 |
| B-lumpy | 530 | 0.488 | 0.488 | 0.488 |
| C-intermittent | 605 | 0.752 | 0.752 | 0.752 |
| C-lumpy | 1188 | 0.657 | 0.657 | 0.657 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-indep-full-r1 |
|---|---|---|---|
| 0.025 | 0.013 / 67.9% / 3.2% | 0.013 / 67.9% / 10.2% | 0.013 / 67.9% / 12.9% |
| 0.05 | 0.025 / 67.9% / 6.4% | 0.025 / 67.9% / 17.9% | 0.026 / 68.0% / 20.5% |
| 0.1 | 0.051 / 67.9% / 12.6% | 0.051 / 68.2% / 28.3% | 0.052 / 68.6% / 28.6% |
| 0.2 | 0.101 / 68.0% / 24.7% | 0.101 / 69.1% / 44.0% | 0.102 / 69.5% / 44.4% |
| 0.5 | 0.241 / 71.1% / 57.2% | 0.241 / 76.5% / 74.9% | 0.241 / 77.3% / 75.7% |
| 0.8 | 0.316 / 85.0% / 84.5% | 0.317 / 87.5% / 87.5% | 0.318 / 87.8% / 87.8% |
| 0.9 | 0.300 / 92.0% / 92.0% | 0.300 / 93.3% / 93.3% | 0.300 / 93.2% / 93.2% |
| 0.95 | 0.255 / 96.3% / 96.3% | 0.253 / 96.4% / 96.4% | 0.255 / 96.1% / 96.1% |
| 0.975 | 0.201 / 98.0% / 98.0% | 0.202 / 97.8% / 97.8% | 0.204 / 97.7% / 97.7% |
| 0.99 | 0.136 / 99.1% / 99.1% | 0.143 / 98.4% / 98.4% | 0.147 / 98.2% / 98.2% |
