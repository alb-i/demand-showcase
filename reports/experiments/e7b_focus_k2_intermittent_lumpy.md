# E7b common ties: quantiles of 2-week sums (focus set, tuning origins from 2011-03-28, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 2.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-summed | focus | 0.421 | 0.372 | 0.418 | 30.3% | 0.222 | 0.199 | 86.8% | 97.8% | 77.7% | 94.8% |
| lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths | focus | 0.421 | 0.372 | 0.418 | 30.3% | 0.221 | 0.197 | 74.0% | 94.4% | 67.2% | 87.8% |
| lgbm-total-q-p1.8-sum-paths-ct-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct | focus | 0.421 | 0.372 | 0.418 | 30.3% | 0.222 | 0.198 | 85.1% | 97.3% | 70.6% | 91.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-focus-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.001 [-0.006, +0.005] |
| lgbm-total-q-p1.8-sum-paths-ct-focus-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.000 [-0.005, +0.005] |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct-focus-r1 |
|---|---|---|---|---|
| A-intermittent | 16 | 0.749 | 0.749 | 0.749 |
| A-lumpy | 66 | 0.342 | 0.342 | 0.342 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct-focus-r1 |
|---|---|---|---|
| 0.025 | 0.014 / 42.2% / 3.0% | 0.014 / 42.2% / 9.9% | 0.014 / 42.2% / 6.2% |
| 0.05 | 0.028 / 42.2% / 5.9% | 0.028 / 42.3% / 16.1% | 0.028 / 42.3% / 11.5% |
| 0.1 | 0.056 / 42.3% / 11.2% | 0.055 / 43.3% / 24.4% | 0.055 / 43.0% / 20.4% |
| 0.2 | 0.104 / 43.5% / 20.5% | 0.100 / 46.5% / 34.4% | 0.100 / 46.5% / 34.4% |
| 0.5 | 0.202 / 53.2% / 46.5% | 0.197 / 62.2% / 61.1% | 0.197 / 62.6% / 61.5% |
| 0.8 | 0.215 / 79.3% / 79.0% | 0.214 / 81.1% / 81.1% | 0.215 / 81.7% / 81.7% |
| 0.9 | 0.177 / 88.9% / 88.9% | 0.176 / 91.6% / 91.6% | 0.178 / 91.0% / 91.0% |
| 0.95 | 0.143 / 96.1% / 96.1% | 0.142 / 96.5% / 96.5% | 0.143 / 96.3% / 96.3% |
| 0.975 | 0.105 / 97.8% / 97.8% | 0.110 / 97.7% / 97.7% | 0.110 / 97.7% / 97.7% |
| 0.99 | 0.068 / 99.1% / 99.1% | 0.071 / 98.3% / 98.3% | 0.070 / 98.2% / 98.2% |
