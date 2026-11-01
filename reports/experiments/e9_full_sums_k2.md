# E9 quantiles of 2-week sums (full set, test origins)

Reference for the bootstrap: `best-crps-sum-summed-full-test-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-06-06 on.

Only h = 2.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best-crps-sum-summed-full-test-r1 | best-crps-sum-summed | full | 0.675 | 0.690 | 1.241 | -0.6% | 0.372 | 0.339 | 89.4% | 97.2% | 81.0% | 94.8% |
| best-crps-sum-paths-ct-full-test-r1 | best-crps-sum-paths-ct | full | 0.675 | 0.690 | 1.241 | -0.6% | 0.370 | 0.327 | 88.0% | 96.2% | 73.6% | 91.9% |
| best-crps-sum-indep-ct-full-test-r1 | best-crps-sum-indep-ct | full | 0.675 | 0.690 | 1.241 | -0.6% | 0.370 | 0.322 | 81.1% | 94.1% | 70.0% | 87.8% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| best-crps-sum-paths-ct-full-test-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.002 [-0.002, -0.001] * |
| best-crps-sum-indep-ct-full-test-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.002 [-0.003, -0.000] * |

## MASE per segment

| segment | series | best-crps-sum-summed-full-test-r1 | best-crps-sum-paths-ct-full-test-r1 | best-crps-sum-indep-ct-full-test-r1 |
|---|---|---|---|---|
| A-erratic | 448 | 0.500 | 0.500 | 0.500 |
| A-intermittent | 26 | 0.575 | 0.575 | 0.575 |
| A-lumpy | 114 | 0.666 | 0.666 | 0.666 |
| A-smooth | 364 | 0.575 | 0.575 | 0.575 |
| B-erratic | 434 | 0.499 | 0.499 | 0.499 |
| B-intermittent | 61 | 0.458 | 0.458 | 0.458 |
| B-lumpy | 530 | 0.656 | 0.656 | 0.656 |
| B-smooth | 120 | 0.531 | 0.531 | 0.531 |
| C-erratic | 122 | 0.361 | 0.361 | 0.361 |
| C-intermittent | 605 | 0.878 | 0.878 | 0.878 |
| C-lumpy | 1188 | 0.658 | 0.658 | 0.658 |
| C-smooth | 132 | 0.503 | 0.503 | 0.503 |
| unclassified | 560 | 1.232 | 1.232 | 1.232 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | best-crps-sum-summed-full-test-r1 | best-crps-sum-paths-ct-full-test-r1 | best-crps-sum-indep-ct-full-test-r1 |
|---|---|---|---|
| 0.025 | 0.030 / 48.8% / 2.9% | 0.029 / 48.9% / 5.4% | 0.029 / 49.6% / 9.2% |
| 0.05 | 0.052 / 49.2% / 5.6% | 0.052 / 49.5% / 10.0% | 0.051 / 50.3% / 14.5% |
| 0.1 | 0.092 / 49.9% / 10.6% | 0.090 / 50.7% / 18.7% | 0.087 / 52.2% / 21.9% |
| 0.2 | 0.157 / 51.6% / 20.2% | 0.151 / 54.2% / 34.8% | 0.149 / 56.0% / 36.7% |
| 0.5 | 0.292 / 63.5% / 52.9% | 0.287 / 70.2% / 68.4% | 0.288 / 71.0% / 69.3% |
| 0.8 | 0.333 / 84.2% / 83.7% | 0.333 / 86.2% / 86.0% | 0.333 / 85.8% / 85.6% |
| 0.9 | 0.297 / 91.7% / 91.6% | 0.298 / 92.3% / 92.3% | 0.297 / 92.0% / 91.9% |
| 0.95 | 0.248 / 95.8% / 95.7% | 0.250 / 95.6% / 95.6% | 0.250 / 95.3% / 95.3% |
| 0.975 | 0.203 / 97.8% / 97.8% | 0.206 / 97.2% / 97.2% | 0.207 / 97.0% / 97.0% |
| 0.99 | 0.159 / 98.9% / 98.9% | 0.156 / 98.1% / 98.1% | 0.159 / 97.8% / 97.8% |
