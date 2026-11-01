# E9 quantiles of 4-week sums (focus set, test origins)

Reference for the bootstrap: `best-crps-sum-summed-focus-test-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-06-06 on.

Only h = 4.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best-crps-sum-summed-focus-test-r1 | best-crps-sum-summed | focus | 0.476 | 0.543 | 0.495 | -0.4% | 0.239 | 0.282 | 91.9% | 98.6% | 89.8% | 97.9% |
| best-crps-sum-paths-ct-focus-test-r1 | best-crps-sum-paths-ct | focus | 0.476 | 0.543 | 0.495 | -0.4% | 0.219 | 0.249 | 83.1% | 95.5% | 78.5% | 93.4% |
| best-crps-sum-indep-ct-focus-test-r1 | best-crps-sum-indep-ct | focus | 0.476 | 0.543 | 0.495 | -0.4% | 0.220 | 0.247 | 67.7% | 89.4% | 67.5% | 86.7% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| best-crps-sum-paths-ct-focus-test-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.019 [-0.022, -0.016] * |
| best-crps-sum-indep-ct-focus-test-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.019 [-0.022, -0.015] * |

## MASE per segment

| segment | series | best-crps-sum-summed-focus-test-r1 | best-crps-sum-paths-ct-focus-test-r1 | best-crps-sum-indep-ct-focus-test-r1 |
|---|---|---|---|---|
| A-erratic | 373 | 0.439 | 0.439 | 0.439 |
| A-intermittent | 16 | 0.554 | 0.554 | 0.554 |
| A-lumpy | 66 | 0.601 | 0.601 | 0.601 |
| A-smooth | 293 | 0.490 | 0.490 | 0.490 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | best-crps-sum-summed-focus-test-r1 | best-crps-sum-paths-ct-focus-test-r1 | best-crps-sum-indep-ct-focus-test-r1 |
|---|---|---|---|
| 0.025 | 0.023 / 11.0% / 0.7% | 0.023 / 11.3% / 3.3% | 0.021 / 14.8% / 9.2% |
| 0.05 | 0.047 / 11.0% / 1.4% | 0.041 / 12.5% / 6.2% | 0.039 / 17.5% / 14.5% |
| 0.1 | 0.089 / 11.2% / 2.9% | 0.072 / 16.4% / 12.6% | 0.071 / 22.8% / 22.3% |
| 0.2 | 0.149 / 13.1% / 6.7% | 0.124 / 26.0% / 24.8% | 0.124 / 32.6% / 32.3% |
| 0.5 | 0.230 / 39.2% / 37.1% | 0.219 / 56.9% / 56.8% | 0.221 / 57.9% / 57.9% |
| 0.8 | 0.210 / 82.6% / 82.6% | 0.208 / 83.0% / 83.0% | 0.209 / 81.4% / 81.4% |
| 0.9 | 0.167 / 92.7% / 92.7% | 0.160 / 91.1% / 91.1% | 0.161 / 89.7% / 89.7% |
| 0.95 | 0.127 / 97.1% / 97.1% | 0.117 / 95.0% / 95.0% | 0.116 / 93.9% / 93.9% |
| 0.975 | 0.092 / 98.6% / 98.6% | 0.082 / 96.8% / 96.8% | 0.083 / 95.8% / 95.8% |
| 0.99 | 0.059 / 99.6% / 99.6% | 0.051 / 98.0% / 98.0% | 0.055 / 97.0% / 97.0% |
