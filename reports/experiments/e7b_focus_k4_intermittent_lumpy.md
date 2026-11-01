# E7b common ties: quantiles of 4-week sums (focus set, tuning origins from 2011-03-28, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 4.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-summed | focus | 0.367 | 0.311 | 0.331 | 29.6% | 0.200 | 0.174 | 88.5% | 98.2% | 82.3% | 96.2% |
| lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths | focus | 0.367 | 0.311 | 0.331 | 29.6% | 0.195 | 0.172 | 79.3% | 88.3% | 67.3% | 84.0% |
| lgbm-total-q-p1.8-sum-paths-ct-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct | focus | 0.367 | 0.311 | 0.331 | 29.6% | 0.193 | 0.170 | 80.1% | 95.5% | 73.8% | 90.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-focus-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.005 [-0.014, +0.007] |
| lgbm-total-q-p1.8-sum-paths-ct-focus-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.007 [-0.016, +0.002] |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct-focus-r1 |
|---|---|---|---|---|
| A-intermittent | 16 | 0.626 | 0.626 | 0.626 |
| A-lumpy | 66 | 0.305 | 0.305 | 0.305 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths-ct-focus-r1 |
|---|---|---|---|
| 0.025 | 0.014 / 31.0% / 1.9% | 0.014 / 31.3% / 12.5% | 0.014 / 31.1% / 6.1% |
| 0.05 | 0.028 / 31.0% / 3.8% | 0.028 / 32.4% / 17.2% | 0.028 / 31.5% / 11.0% |
| 0.1 | 0.055 / 31.0% / 7.1% | 0.053 / 34.0% / 24.9% | 0.053 / 32.9% / 18.2% |
| 0.2 | 0.102 / 32.0% / 13.8% | 0.095 / 39.0% / 36.2% | 0.093 / 38.2% / 29.1% |
| 0.5 | 0.191 / 43.0% / 37.5% | 0.180 / 59.4% / 58.6% | 0.180 / 59.4% / 58.6% |
| 0.8 | 0.196 / 75.4% / 75.1% | 0.191 / 82.0% / 81.9% | 0.191 / 81.5% / 81.5% |
| 0.9 | 0.158 / 89.5% / 89.5% | 0.156 / 92.2% / 92.2% | 0.154 / 92.0% / 92.0% |
| 0.95 | 0.121 / 95.1% / 95.1% | 0.121 / 94.5% / 94.5% | 0.118 / 94.5% / 94.5% |
| 0.975 | 0.084 / 98.2% / 98.2% | 0.086 / 96.5% / 96.5% | 0.084 / 96.6% / 96.6% |
| 0.99 | 0.051 / 99.4% / 99.4% | 0.053 / 98.0% / 98.0% | 0.050 / 98.0% / 98.0% |
