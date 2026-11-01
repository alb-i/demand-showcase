# E7b common ties: quantiles of 4-week sums (focus set, tuning origins from 2011-03-28)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 4.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-summed | focus | 0.447 | 0.474 | 0.489 | 3.0% | 0.223 | 0.246 | 91.8% | 98.7% | 89.9% | 97.8% |
| lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths | focus | 0.447 | 0.474 | 0.489 | 3.0% | 0.210 | 0.229 | 80.9% | 92.6% | 78.2% | 91.4% |
| lgbm-total-q-p1.8-sum-paths-ct-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct | focus | 0.447 | 0.474 | 0.489 | 3.0% | 0.209 | 0.229 | 81.2% | 93.5% | 79.0% | 92.1% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-focus-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.013 [-0.017, -0.009] * |
| lgbm-total-q-p1.8-sum-paths-ct-focus-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.013 [-0.017, -0.009] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct-focus-r1 |
|---|---|---|---|---|
| A-erratic | 373 | 0.482 | 0.482 | 0.482 |
| A-intermittent | 16 | 0.626 | 0.626 | 0.626 |
| A-lumpy | 66 | 0.305 | 0.305 | 0.305 |
| A-smooth | 293 | 0.424 | 0.424 | 0.424 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct-focus-r1 |
|---|---|---|---|
| 0.025 | 0.021 / 8.5% / 0.9% | 0.020 / 9.3% / 5.1% | 0.020 / 9.2% / 4.3% |
| 0.05 | 0.041 / 8.5% / 1.6% | 0.037 / 11.0% / 7.8% | 0.037 / 10.7% / 6.9% |
| 0.1 | 0.079 / 8.9% / 3.2% | 0.066 / 15.1% / 13.2% | 0.066 / 14.9% / 12.4% |
| 0.2 | 0.133 / 10.9% / 6.8% | 0.114 / 25.0% / 24.6% | 0.114 / 25.1% / 24.0% |
| 0.5 | 0.212 / 39.0% / 37.8% | 0.204 / 56.3% / 56.2% | 0.204 / 56.4% / 56.3% |
| 0.8 | 0.198 / 82.4% / 82.4% | 0.197 / 82.7% / 82.7% | 0.197 / 82.7% / 82.7% |
| 0.9 | 0.160 / 93.1% / 93.1% | 0.156 / 91.4% / 91.4% | 0.155 / 91.5% / 91.5% |
| 0.95 | 0.122 / 97.2% / 97.2% | 0.116 / 94.7% / 94.7% | 0.116 / 94.8% / 94.8% |
| 0.975 | 0.091 / 98.7% / 98.7% | 0.083 / 96.6% / 96.6% | 0.083 / 96.5% / 96.5% |
| 0.99 | 0.056 / 99.5% / 99.5% | 0.055 / 97.8% / 97.8% | 0.054 / 97.7% / 97.7% |
