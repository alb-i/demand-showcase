# E7 quantiles of 8-week sums (full set, tuning origins from 2011-03-28, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 8.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-summed | full | 0.575 | 0.355 | 0.745 | 13.5% | 0.338 | 0.183 | 87.3% | 97.7% | 79.8% | 95.8% |
| lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-paths | full | 0.575 | 0.355 | 0.745 | 13.5% | 0.329 | 0.175 | 58.1% | 91.4% | 50.2% | 79.6% |
| lgbm-total-q-p1.8-sum-indep-full-r1 | lgbm-total-q-p1.8-sum-indep | full | 0.575 | 0.355 | 0.745 | 13.5% | 0.349 | 0.189 | 39.8% | 49.7% | 37.1% | 48.3% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.009 [-0.014, -0.004] * |
| lgbm-total-q-p1.8-sum-indep-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.011 [+0.005, +0.019] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-indep-full-r1 |
|---|---|---|---|---|
| A-intermittent | 26 | 0.450 | 0.450 | 0.450 |
| A-lumpy | 114 | 0.239 | 0.239 | 0.239 |
| B-intermittent | 61 | 0.322 | 0.322 | 0.322 |
| B-lumpy | 530 | 0.426 | 0.426 | 0.426 |
| C-intermittent | 605 | 0.804 | 0.804 | 0.804 |
| C-lumpy | 1188 | 0.575 | 0.575 | 0.575 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-full-r1 | lgbm-total-q-p1.8-sum-paths-full-r1 | lgbm-total-q-p1.8-sum-indep-full-r1 |
|---|---|---|---|
| 0.025 | 0.014 / 45.3% / 1.9% | 0.015 / 46.0% / 16.2% | 0.021 / 49.5% / 45.2% |
| 0.05 | 0.028 / 45.3% / 3.8% | 0.029 / 46.4% / 27.6% | 0.038 / 51.4% / 48.2% |
| 0.1 | 0.056 / 45.3% / 7.5% | 0.057 / 47.3% / 40.6% | 0.068 / 54.2% / 52.6% |
| 0.2 | 0.112 / 45.5% / 15.0% | 0.112 / 52.0% / 49.9% | 0.124 / 58.9% / 58.7% |
| 0.5 | 0.266 / 49.2% / 38.9% | 0.251 / 66.2% / 66.1% | 0.260 / 71.5% / 71.5% |
| 0.8 | 0.332 / 73.4% / 73.1% | 0.314 / 84.7% / 84.7% | 0.315 / 85.1% / 85.1% |
| 0.9 | 0.303 / 87.4% / 87.4% | 0.284 / 90.8% / 90.8% | 0.287 / 89.7% / 89.7% |
| 0.95 | 0.245 / 95.1% / 95.1% | 0.237 / 94.1% / 94.1% | 0.245 / 92.0% / 92.0% |
| 0.975 | 0.196 / 97.7% / 97.7% | 0.195 / 95.9% / 95.9% | 0.211 / 93.5% / 93.5% |
| 0.99 | 0.137 / 99.0% / 99.0% | 0.150 / 97.1% / 97.1% | 0.177 / 94.9% / 94.9% |
