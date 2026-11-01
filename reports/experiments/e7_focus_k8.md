# E7 quantiles of 8-week sums (focus set, tuning origins from 2011-03-28)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 8.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-summed | focus | 0.396 | 0.419 | 0.394 | 2.7% | 0.206 | 0.228 | 92.4% | 98.9% | 91.0% | 98.3% |
| lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths | focus | 0.396 | 0.419 | 0.394 | 2.7% | 0.185 | 0.201 | 77.4% | 91.6% | 76.7% | 90.2% |
| lgbm-total-q-p1.8-sum-indep-focus-r1 | lgbm-total-q-p1.8-sum-indep | focus | 0.396 | 0.419 | 0.394 | 2.7% | 0.197 | 0.213 | 60.8% | 76.9% | 60.5% | 76.8% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-focus-r1 | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | -0.021 [-0.026, -0.015] * |
| lgbm-total-q-p1.8-sum-indep-focus-r1 | -0.000 [-0.000, +0.000] | -0.000 [-0.000, +0.000] | -0.009 [-0.017, +0.000] |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-indep-focus-r1 |
|---|---|---|---|---|
| A-erratic | 373 | 0.425 | 0.425 | 0.425 |
| A-intermittent | 16 | 0.557 | 0.557 | 0.557 |
| A-lumpy | 66 | 0.296 | 0.296 | 0.296 |
| A-smooth | 293 | 0.373 | 0.373 | 0.373 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-indep-focus-r1 |
|---|---|---|---|
| 0.025 | 0.020 / 6.7% / 0.6% | 0.019 / 8.0% / 5.2% | 0.025 / 16.2% / 15.7% |
| 0.05 | 0.041 / 6.7% / 1.1% | 0.035 / 9.9% / 8.3% | 0.041 / 20.2% / 19.9% |
| 0.1 | 0.078 / 7.0% / 2.3% | 0.061 / 14.1% / 13.5% | 0.068 / 26.3% / 26.1% |
| 0.2 | 0.132 / 8.2% / 4.8% | 0.104 / 25.1% / 24.9% | 0.111 / 36.2% / 36.2% |
| 0.5 | 0.196 / 32.3% / 31.3% | 0.182 / 55.8% / 55.8% | 0.185 / 58.7% / 58.7% |
| 0.8 | 0.176 / 82.8% / 82.8% | 0.174 / 82.9% / 82.9% | 0.174 / 79.4% / 79.4% |
| 0.9 | 0.145 / 93.3% / 93.3% | 0.135 / 90.2% / 90.2% | 0.138 / 86.6% / 86.6% |
| 0.95 | 0.111 / 97.4% / 97.4% | 0.099 / 93.6% / 93.6% | 0.105 / 90.5% / 90.5% |
| 0.975 | 0.080 / 98.9% / 98.9% | 0.071 / 95.4% / 95.4% | 0.080 / 92.5% / 92.5% |
| 0.99 | 0.049 / 99.7% / 99.7% | 0.045 / 97.1% / 97.1% | 0.058 / 94.5% / 94.5% |
