# E7 quantiles of 8-week sums (focus set, tuning origins from 2011-03-28, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-q-p1.8-sum-summed-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only h = 8.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-summed | focus | 0.347 | 0.291 | 0.322 | 25.7% | 0.189 | 0.160 | 87.2% | 98.7% | 83.0% | 97.5% |
| lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-paths | focus | 0.347 | 0.291 | 0.322 | 25.7% | 0.182 | 0.152 | 72.6% | 89.4% | 67.3% | 85.6% |
| lgbm-total-q-p1.8-sum-indep-focus-r1 | lgbm-total-q-p1.8-sum-indep | focus | 0.347 | 0.291 | 0.322 | 25.7% | 0.205 | 0.163 | 50.5% | 63.3% | 48.7% | 62.6% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-sum-paths-focus-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | -0.006 [-0.018, +0.008] |
| lgbm-total-q-p1.8-sum-indep-focus-r1 | +0.000 [-0.000, +0.000] | +0.000 [-0.000, +0.000] | +0.016 [-0.008, +0.047] |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-indep-focus-r1 |
|---|---|---|---|---|
| A-intermittent | 16 | 0.557 | 0.557 | 0.557 |
| A-lumpy | 66 | 0.296 | 0.296 | 0.296 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-sum-summed-focus-r1 | lgbm-total-q-p1.8-sum-paths-focus-r1 | lgbm-total-q-p1.8-sum-indep-focus-r1 |
|---|---|---|---|
| 0.025 | 0.014 / 22.1% / 1.2% | 0.014 / 23.3% / 9.8% | 0.022 / 31.6% / 28.7% |
| 0.05 | 0.028 / 22.1% / 2.4% | 0.028 / 24.4% / 14.7% | 0.036 / 34.8% / 32.5% |
| 0.1 | 0.055 / 22.2% / 4.8% | 0.052 / 26.6% / 21.9% | 0.061 / 37.9% / 36.7% |
| 0.2 | 0.102 / 23.0% / 9.5% | 0.091 / 33.2% / 31.6% | 0.101 / 45.6% / 45.4% |
| 0.5 | 0.191 / 33.2% / 28.7% | 0.173 / 55.4% / 55.3% | 0.182 / 65.7% / 65.7% |
| 0.8 | 0.189 / 72.9% / 72.7% | 0.184 / 80.4% / 80.4% | 0.190 / 79.6% / 79.6% |
| 0.9 | 0.144 / 87.8% / 87.8% | 0.143 / 89.3% / 89.3% | 0.155 / 85.4% / 85.4% |
| 0.95 | 0.104 / 96.1% / 96.1% | 0.108 / 93.7% / 93.7% | 0.120 / 89.0% / 89.0% |
| 0.975 | 0.069 / 98.7% / 98.7% | 0.077 / 95.5% / 95.5% | 0.091 / 91.3% / 91.3% |
| 0.99 | 0.048 / 99.8% / 99.8% | 0.042 / 97.8% / 97.8% | 0.066 / 93.9% / 93.9% |
