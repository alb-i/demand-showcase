# E9 quantiles of 8-week sums (full set, test origins)

Reference for the bootstrap: `best-crps-sum-summed-full-test-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-06-06 on.

Only h = 8.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best-crps-sum-summed-full-test-r1 | best-crps-sum-summed | full | 0.614 | 0.549 | 1.009 | -0.2% | 0.370 | 0.307 | 88.8% | 96.6% | 82.8% | 95.1% |
| best-crps-sum-paths-ct-full-test-r1 | best-crps-sum-paths-ct | full | 0.614 | 0.549 | 1.009 | -0.2% | 0.354 | 0.264 | 85.2% | 94.6% | 73.0% | 90.5% |
| best-crps-sum-indep-ct-full-test-r1 | best-crps-sum-indep-ct | full | 0.614 | 0.549 | 1.009 | -0.2% | 0.371 | 0.271 | 44.6% | 55.3% | 42.8% | 54.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| best-crps-sum-paths-ct-full-test-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.014 [-0.016, -0.010] * |
| best-crps-sum-indep-ct-full-test-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.005 [+0.000, +0.010] * |

## MASE per segment

| segment | series | best-crps-sum-summed-full-test-r1 | best-crps-sum-paths-ct-full-test-r1 | best-crps-sum-indep-ct-full-test-r1 |
|---|---|---|---|---|
| A-erratic | 448 | 0.403 | 0.403 | 0.403 |
| A-intermittent | 26 | 0.486 | 0.486 | 0.486 |
| A-lumpy | 114 | 0.617 | 0.617 | 0.617 |
| A-smooth | 364 | 0.432 | 0.432 | 0.432 |
| B-erratic | 434 | 0.402 | 0.402 | 0.402 |
| B-intermittent | 61 | 0.391 | 0.391 | 0.391 |
| B-lumpy | 530 | 0.635 | 0.635 | 0.635 |
| B-smooth | 120 | 0.453 | 0.453 | 0.453 |
| C-erratic | 122 | 0.304 | 0.304 | 0.304 |
| C-intermittent | 605 | 0.805 | 0.805 | 0.805 |
| C-lumpy | 1188 | 0.620 | 0.620 | 0.620 |
| C-smooth | 132 | 0.437 | 0.437 | 0.437 |
| unclassified | 469 | 1.363 | 1.363 | 1.363 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | best-crps-sum-summed-full-test-r1 | best-crps-sum-paths-ct-full-test-r1 | best-crps-sum-indep-ct-full-test-r1 |
|---|---|---|---|
| 0.025 | 0.028 / 38.2% / 2.2% | 0.028 / 38.4% / 5.2% | 0.036 / 43.7% / 38.9% |
| 0.05 | 0.050 / 38.5% / 4.1% | 0.049 / 39.0% / 9.7% | 0.055 / 45.9% / 41.9% |
| 0.1 | 0.090 / 38.9% / 7.4% | 0.084 / 40.5% / 18.0% | 0.089 / 49.6% / 46.5% |
| 0.2 | 0.156 / 39.3% / 13.7% | 0.141 / 45.2% / 32.3% | 0.149 / 55.4% / 53.5% |
| 0.5 | 0.296 / 49.1% / 39.9% | 0.272 / 66.5% / 65.2% | 0.280 / 69.9% / 69.2% |
| 0.8 | 0.327 / 79.4% / 78.9% | 0.319 / 85.5% / 85.2% | 0.319 / 84.4% / 84.2% |
| 0.9 | 0.292 / 90.3% / 90.2% | 0.287 / 91.1% / 91.0% | 0.288 / 89.4% / 89.3% |
| 0.95 | 0.247 / 95.2% / 95.2% | 0.240 / 94.0% / 93.9% | 0.247 / 91.9% / 91.9% |
| 0.975 | 0.204 / 97.3% / 97.3% | 0.198 / 95.7% / 95.7% | 0.213 / 93.4% / 93.4% |
| 0.99 | 0.157 / 98.5% / 98.5% | 0.152 / 97.1% / 97.1% | 0.180 / 94.8% / 94.8% |
