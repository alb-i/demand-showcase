# E7 quantiles of 4-week sums (full set, tuning origins from 2011-03-28, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 4.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-summed | full | 0.589 | 0.372 | 0.832 | 8.8% | 0.325 | 0.185 | 90.1% | 97.9% | 80.5% | 95.4% |
| lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths | full | 0.589 | 0.372 | 0.832 | 8.8% | 0.324 | 0.182 | 84.1% | 89.4% | 55.5% | 82.1% |
| lgbm-total-q-p1.8-sum-indep-full-r1 | lgbm-total-q-p1.8-sum-indep | full | 0.589 | 0.372 | 0.832 | 8.8% | 0.332 | 0.187 | 39.9% | 87.8% | 37.6% | 72.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.001 [-0.005, +0.002] |
| lgbm-total-q-p1.8-sum-indep-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.007 [+0.003, +0.012] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-indep-full-r1 |
|---|---|---|---|---|
| A-intermittent | 26 | 0.494 | 0.494 | 0.494 |
| A-lumpy | 114 | 0.244 | 0.244 | 0.244 |
| B-intermittent | 61 | 0.327 | 0.327 | 0.327 |
| B-lumpy | 530 | 0.450 | 0.450 | 0.450 |
| C-intermittent | 605 | 0.761 | 0.761 | 0.761 |
| C-lumpy | 1188 | 0.613 | 0.613 | 0.613 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-indep-full-r1 |
|---|---|---|---|
| 0.025 | 0.013 / 56.0% / 2.4% | 0.014 / 56.3% / 14.6% | 0.015 / 57.0% / 23.4% |
| 0.05 | 0.026 / 56.0% / 4.9% | 0.027 / 56.7% / 22.3% | 0.029 / 57.6% / 38.6% |
| 0.1 | 0.053 / 56.0% / 9.7% | 0.054 / 57.3% / 37.3% | 0.058 / 59.6% / 54.8% |
| 0.2 | 0.106 / 56.1% / 19.2% | 0.106 / 59.8% / 55.1% | 0.112 / 63.7% / 60.9% |
| 0.5 | 0.250 / 60.1% / 47.8% | 0.242 / 71.0% / 70.1% | 0.247 / 73.6% / 73.5% |
| 0.8 | 0.318 / 80.0% / 79.7% | 0.313 / 86.4% / 86.4% | 0.314 / 86.9% / 86.9% |
| 0.9 | 0.296 / 90.3% / 90.3% | 0.287 / 92.7% / 92.7% | 0.288 / 92.3% / 92.3% |
| 0.95 | 0.243 / 95.7% / 95.7% | 0.241 / 95.5% / 95.5% | 0.244 / 95.1% / 95.1% |
| 0.975 | 0.189 / 97.9% / 97.9% | 0.193 / 96.7% / 96.7% | 0.199 / 95.9% / 95.9% |
| 0.99 | 0.131 / 99.1% / 99.1% | 0.142 / 97.6% / 97.6% | 0.158 / 96.7% / 96.7% |
