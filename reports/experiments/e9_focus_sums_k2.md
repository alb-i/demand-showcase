# E9 quantiles of 2-week sums (focus set, test origins)

Reference for the bootstrap: `best-crps-sum-summed-focus-test-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-06-06 on.

Only h = 2.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best-crps-sum-summed-focus-test-r1 | best-crps-sum-summed | focus | 0.550 | 0.638 | 0.623 | -0.0% | 0.265 | 0.311 | 90.3% | 98.4% | 87.6% | 97.2% |
| best-crps-sum-paths-ct-focus-test-r1 | best-crps-sum-paths-ct | focus | 0.550 | 0.638 | 0.623 | -0.0% | 0.257 | 0.296 | 84.6% | 96.2% | 81.5% | 94.3% |
| best-crps-sum-indep-ct-focus-test-r1 | best-crps-sum-indep-ct | focus | 0.550 | 0.638 | 0.623 | -0.0% | 0.255 | 0.292 | 80.1% | 94.1% | 77.6% | 92.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| best-crps-sum-paths-ct-focus-test-r1 | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | -0.008 [-0.009, -0.006] * |
| best-crps-sum-indep-ct-focus-test-r1 | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | -0.010 [-0.012, -0.008] * |

## MASE per segment

| segment | series | best-crps-sum-summed-focus-test-r1 | best-crps-sum-paths-ct-focus-test-r1 | best-crps-sum-indep-ct-focus-test-r1 |
|---|---|---|---|---|
| A-erratic | 373 | 0.506 | 0.506 | 0.506 |
| A-intermittent | 16 | 0.618 | 0.618 | 0.618 |
| A-lumpy | 66 | 0.635 | 0.635 | 0.635 |
| A-smooth | 293 | 0.583 | 0.583 | 0.583 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | best-crps-sum-summed-focus-test-r1 | best-crps-sum-paths-ct-focus-test-r1 | best-crps-sum-indep-ct-focus-test-r1 |
|---|---|---|---|
| 0.025 | 0.024 / 13.7% / 1.2% | 0.023 / 13.9% / 3.3% | 0.022 / 14.6% / 5.4% |
| 0.05 | 0.047 / 13.7% / 2.4% | 0.044 / 14.4% / 5.5% | 0.042 / 16.0% / 8.2% |
| 0.1 | 0.089 / 14.2% / 4.5% | 0.080 / 17.0% / 10.1% | 0.077 / 19.8% / 13.3% |
| 0.2 | 0.151 / 18.0% / 10.7% | 0.137 / 25.6% / 21.5% | 0.136 / 28.3% / 24.2% |
| 0.5 | 0.250 / 47.0% / 44.8% | 0.248 / 57.6% / 57.4% | 0.249 / 58.0% / 57.8% |
| 0.8 | 0.245 / 82.9% / 82.8% | 0.246 / 83.6% / 83.5% | 0.245 / 82.7% / 82.7% |
| 0.9 | 0.195 / 92.1% / 92.1% | 0.194 / 91.7% / 91.7% | 0.194 / 90.9% / 90.9% |
| 0.95 | 0.146 / 96.3% / 96.3% | 0.143 / 95.6% / 95.6% | 0.143 / 95.2% / 95.2% |
| 0.975 | 0.106 / 98.4% / 98.4% | 0.103 / 97.6% / 97.6% | 0.102 / 97.4% / 97.4% |
| 0.99 | 0.069 / 99.3% / 99.3% | 0.065 / 98.4% / 98.4% | 0.065 / 98.2% / 98.2% |
