# E9 quantiles of 8-week sums (focus set, test origins)

Reference for the bootstrap: `best-crps-sum-summed-focus-test-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-06-06 on.

Only h = 8.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best-crps-sum-summed-focus-test-r1 | best-crps-sum-summed | focus | 0.433 | 0.485 | 0.414 | -1.6% | 0.226 | 0.269 | 92.8% | 99.3% | 91.1% | 98.7% |
| best-crps-sum-paths-ct-focus-test-r1 | best-crps-sum-paths-ct | focus | 0.433 | 0.485 | 0.414 | -1.6% | 0.194 | 0.217 | 77.1% | 94.7% | 75.7% | 92.3% |
| best-crps-sum-indep-ct-focus-test-r1 | best-crps-sum-indep-ct | focus | 0.433 | 0.485 | 0.414 | -1.6% | 0.203 | 0.222 | 60.9% | 76.8% | 60.5% | 76.7% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| best-crps-sum-paths-ct-focus-test-r1 | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | -0.032 [-0.037, -0.028] * |
| best-crps-sum-indep-ct-focus-test-r1 | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | -0.023 [-0.029, -0.016] * |

## MASE per segment

| segment | series | best-crps-sum-summed-focus-test-r1 | best-crps-sum-paths-ct-focus-test-r1 | best-crps-sum-indep-ct-focus-test-r1 |
|---|---|---|---|---|
| A-erratic | 373 | 0.402 | 0.402 | 0.402 |
| A-intermittent | 16 | 0.516 | 0.516 | 0.516 |
| A-lumpy | 66 | 0.600 | 0.600 | 0.600 |
| A-smooth | 293 | 0.429 | 0.429 | 0.429 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | best-crps-sum-summed-focus-test-r1 | best-crps-sum-paths-ct-focus-test-r1 | best-crps-sum-indep-ct-focus-test-r1 |
|---|---|---|---|
| 0.025 | 0.023 / 9.2% / 0.6% | 0.022 / 9.8% / 4.2% | 0.026 / 17.7% / 17.2% |
| 0.05 | 0.046 / 9.2% / 1.1% | 0.039 / 11.5% / 8.1% | 0.044 / 21.4% / 21.0% |
| 0.1 | 0.088 / 9.4% / 2.3% | 0.068 / 16.1% / 15.0% | 0.074 / 27.0% / 26.9% |
| 0.2 | 0.149 / 10.8% / 5.1% | 0.116 / 26.2% / 26.0% | 0.122 / 36.4% / 36.4% |
| 0.5 | 0.224 / 33.1% / 31.2% | 0.202 / 55.8% / 55.8% | 0.204 / 58.3% / 58.3% |
| 0.8 | 0.191 / 82.0% / 81.9% | 0.184 / 82.2% / 82.2% | 0.185 / 79.5% / 79.5% |
| 0.9 | 0.152 / 93.4% / 93.4% | 0.138 / 90.7% / 90.7% | 0.141 / 87.4% / 87.4% |
| 0.95 | 0.116 / 97.5% / 97.5% | 0.097 / 94.5% / 94.5% | 0.101 / 91.3% / 91.3% |
| 0.975 | 0.084 / 99.3% / 99.3% | 0.065 / 96.5% / 96.5% | 0.072 / 93.8% / 93.8% |
| 0.99 | 0.057 / 99.8% / 99.8% | 0.039 / 98.0% / 98.0% | 0.049 / 95.6% / 95.6% |
