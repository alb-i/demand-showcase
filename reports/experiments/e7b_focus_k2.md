# E7b common ties: quantiles of 2-week sums (focus set, tuning origins from 2011-03-28)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 2.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-summed | focus | 0.524 | 0.556 | 0.615 | 3.2% | 0.249 | 0.271 | 88.9% | 98.5% | 86.3% | 97.1% |
| lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths | focus | 0.524 | 0.556 | 0.615 | 3.2% | 0.244 | 0.263 | 80.2% | 95.0% | 78.8% | 93.0% |
| lgbm-total-q-p1.8-sum-paths-ct-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct | focus | 0.524 | 0.556 | 0.615 | 3.2% | 0.244 | 0.262 | 81.5% | 95.7% | 79.3% | 93.6% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-focus-r1 | +0.000 [+0.000, +0.000] * | +0.000 [+0.000, +0.000] * | -0.005 [-0.007, -0.003] * |
| lgbm-total-q-p1.8-sum-paths-ct-focus-r1 | +0.000 [+0.000, +0.000] * | +0.000 [+0.000, +0.000] * | -0.005 [-0.007, -0.003] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct-focus-r1 |
|---|---|---|---|---|
| A-erratic | 373 | 0.546 | 0.546 | 0.546 |
| A-intermittent | 16 | 0.749 | 0.749 | 0.749 |
| A-lumpy | 66 | 0.342 | 0.342 | 0.342 |
| A-smooth | 293 | 0.525 | 0.525 | 0.525 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct-focus-r1 |
|---|---|---|---|
| 0.025 | 0.021 / 11.4% / 1.5% | 0.021 / 11.6% / 4.6% | 0.021 / 11.6% / 4.0% |
| 0.05 | 0.042 / 11.4% / 2.7% | 0.039 / 12.6% / 7.2% | 0.039 / 12.6% / 6.7% |
| 0.1 | 0.080 / 12.0% / 5.0% | 0.072 / 16.1% / 12.3% | 0.072 / 16.0% / 11.8% |
| 0.2 | 0.136 / 16.8% / 12.0% | 0.128 / 25.3% / 22.9% | 0.128 / 25.5% / 23.1% |
| 0.5 | 0.239 / 46.1% / 44.7% | 0.236 / 56.2% / 56.1% | 0.236 / 56.3% / 56.1% |
| 0.8 | 0.233 / 81.5% / 81.5% | 0.234 / 81.9% / 81.9% | 0.234 / 81.9% / 81.9% |
| 0.9 | 0.184 / 91.3% / 91.3% | 0.184 / 91.1% / 91.1% | 0.184 / 91.0% / 91.0% |
| 0.95 | 0.139 / 96.5% / 96.5% | 0.139 / 95.7% / 95.7% | 0.138 / 95.7% / 95.7% |
| 0.975 | 0.104 / 98.5% / 98.5% | 0.102 / 97.6% / 97.6% | 0.101 / 97.6% / 97.6% |
| 0.99 | 0.068 / 99.3% / 99.3% | 0.065 / 98.3% / 98.3% | 0.065 / 98.4% / 98.4% |
