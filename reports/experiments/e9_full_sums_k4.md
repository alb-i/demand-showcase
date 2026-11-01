# E9 quantiles of 4-week sums (full set, test origins)

Reference for the bootstrap: `best-crps-sum-summed-full-test-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-06-06 on.

Only h = 4.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best-crps-sum-summed-full-test-r1 | best-crps-sum-summed | full | 0.623 | 0.601 | 1.027 | 0.1% | 0.358 | 0.312 | 89.3% | 97.1% | 82.3% | 95.3% |
| best-crps-sum-paths-ct-full-test-r1 | best-crps-sum-paths-ct | full | 0.623 | 0.601 | 1.027 | 0.1% | 0.349 | 0.285 | 87.1% | 95.3% | 74.8% | 91.6% |
| best-crps-sum-indep-ct-full-test-r1 | best-crps-sum-indep-ct | full | 0.623 | 0.601 | 1.027 | 0.1% | 0.355 | 0.284 | 47.6% | 88.8% | 46.0% | 77.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| best-crps-sum-paths-ct-full-test-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.007 [-0.009, -0.005] * |
| best-crps-sum-indep-ct-full-test-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.001 [-0.002, +0.004] |

## MASE per segment

| segment | series | best-crps-sum-summed-full-test-r1 | best-crps-sum-paths-ct-full-test-r1 | best-crps-sum-indep-ct-full-test-r1 |
|---|---|---|---|---|
| A-erratic | 448 | 0.437 | 0.437 | 0.437 |
| A-intermittent | 26 | 0.535 | 0.535 | 0.535 |
| A-lumpy | 114 | 0.614 | 0.614 | 0.614 |
| A-smooth | 364 | 0.487 | 0.487 | 0.487 |
| B-erratic | 434 | 0.432 | 0.432 | 0.432 |
| B-intermittent | 61 | 0.408 | 0.408 | 0.408 |
| B-lumpy | 530 | 0.630 | 0.630 | 0.630 |
| B-smooth | 120 | 0.475 | 0.475 | 0.475 |
| C-erratic | 122 | 0.324 | 0.324 | 0.324 |
| C-intermittent | 605 | 0.827 | 0.827 | 0.827 |
| C-lumpy | 1188 | 0.612 | 0.612 | 0.612 |
| C-smooth | 132 | 0.451 | 0.451 | 0.451 |
| unclassified | 543 | 1.226 | 1.226 | 1.226 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | best-crps-sum-summed-full-test-r1 | best-crps-sum-paths-ct-full-test-r1 | best-crps-sum-indep-ct-full-test-r1 |
|---|---|---|---|
| 0.025 | 0.028 / 42.7% / 2.4% | 0.028 / 43.0% / 4.8% | 0.030 / 45.0% / 18.4% |
| 0.05 | 0.050 / 43.1% / 4.5% | 0.049 / 43.5% / 8.9% | 0.049 / 46.4% / 31.0% |
| 0.1 | 0.090 / 43.7% / 8.6% | 0.085 / 45.0% / 17.0% | 0.085 / 49.4% / 45.0% |
| 0.2 | 0.154 / 44.6% / 16.2% | 0.143 / 49.2% / 32.1% | 0.145 / 55.0% / 51.9% |
| 0.5 | 0.287 / 55.7% / 45.7% | 0.272 / 68.0% / 66.4% | 0.276 / 69.6% / 68.8% |
| 0.8 | 0.319 / 81.8% / 81.3% | 0.317 / 85.7% / 85.5% | 0.316 / 85.1% / 84.9% |
| 0.9 | 0.283 / 91.0% / 90.9% | 0.281 / 91.8% / 91.7% | 0.281 / 91.0% / 90.9% |
| 0.95 | 0.234 / 95.7% / 95.6% | 0.234 / 94.9% / 94.9% | 0.237 / 94.0% / 94.0% |
| 0.975 | 0.192 / 97.6% / 97.6% | 0.190 / 96.4% / 96.4% | 0.196 / 95.4% / 95.3% |
| 0.99 | 0.151 / 98.8% / 98.8% | 0.146 / 97.6% / 97.6% | 0.160 / 96.3% / 96.3% |
