# E6 conformal calibration of the E5 quantile models (focus set, tuning origins from 2011-03-28, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-q-p1.8-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8 | focus | 0.494 | 0.446 | 0.583 | 25.7% | 0.266 | 0.240 | 85.7% | 97.8% | 73.0% | 93.1% |
| lgbm-total-q-p1.8-cqr13-focus-r1 | lgbm-total-q-p1.8-cqr13 | focus | 0.494 | 0.446 | 0.583 | 25.7% | 0.269 | 0.243 | 86.4% | 98.2% | 73.7% | 93.6% |
| lgbm-total-q-p1.8-cqr13-all-focus-r1 | lgbm-total-q-p1.8-cqr13-all | focus | 0.494 | 0.446 | 0.583 | 25.7% | 0.267 | 0.240 | 86.0% | 97.9% | 71.9% | 93.0% |
| lgbm-total-q-p1.8-cqr26-focus-r1 | lgbm-total-q-p1.8-cqr26 | focus | 0.494 | 0.446 | 0.583 | 25.7% | 0.269 | 0.243 | 86.1% | 98.1% | 73.5% | 93.5% |
| lgbm-total-q-p1.8-cqr26-all-focus-r1 | lgbm-total-q-p1.8-cqr26-all | focus | 0.494 | 0.446 | 0.583 | 25.7% | 0.267 | 0.240 | 84.9% | 97.8% | 71.3% | 93.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-cqr13-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.002 [-0.004, +0.008] |
| lgbm-total-q-p1.8-cqr13-all-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [-0.001, +0.001] |
| lgbm-total-q-p1.8-cqr26-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.002 [-0.002, +0.006] |
| lgbm-total-q-p1.8-cqr26-all-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.001] |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8-cqr13-focus-r1 | lgbm-total-q-p1.8-cqr13-all-focus-r1 | lgbm-total-q-p1.8-cqr26-focus-r1 | lgbm-total-q-p1.8-cqr26-all-focus-r1 |
|---|---|---|---|---|---|---|
| A-intermittent | 16 | 0.885 | 0.885 | 0.885 | 0.885 | 0.885 |
| A-lumpy | 66 | 0.400 | 0.400 | 0.400 | 0.400 | 0.400 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8-cqr13-focus-r1 | lgbm-total-q-p1.8-cqr13-all-focus-r1 | lgbm-total-q-p1.8-cqr26-focus-r1 | lgbm-total-q-p1.8-cqr26-all-focus-r1 |
|---|---|---|---|---|---|
| 0.025 | 0.014 / 54.5% / 4.7% | 0.014 / 54.5% / 4.6% | 0.014 / 54.5% / 5.0% | 0.014 / 54.5% / 4.5% | 0.014 / 54.5% / 4.8% |
| 0.05 | 0.028 / 54.5% / 9.2% | 0.028 / 54.5% / 9.0% | 0.028 / 54.5% / 9.8% | 0.028 / 54.5% / 8.9% | 0.028 / 54.5% / 9.5% |
| 0.1 | 0.055 / 54.5% / 16.8% | 0.055 / 54.5% / 16.4% | 0.055 / 54.5% / 17.9% | 0.055 / 54.5% / 16.2% | 0.055 / 54.5% / 17.4% |
| 0.2 | 0.107 / 55.9% / 29.0% | 0.107 / 55.9% / 28.5% | 0.107 / 56.0% / 30.8% | 0.107 / 55.9% / 28.3% | 0.107 / 56.0% / 29.7% |
| 0.5 | 0.227 / 64.4% / 57.0% | 0.227 / 65.8% / 57.1% | 0.227 / 64.6% / 57.3% | 0.226 / 65.8% / 56.8% | 0.227 / 64.4% / 55.1% |
| 0.8 | 0.265 / 82.0% / 81.7% | 0.263 / 83.0% / 81.9% | 0.265 / 81.5% / 80.6% | 0.263 / 82.7% / 81.4% | 0.266 / 80.7% / 79.3% |
| 0.9 | 0.230 / 89.7% / 89.7% | 0.229 / 90.2% / 90.0% | 0.230 / 89.9% / 89.8% | 0.230 / 89.9% / 89.7% | 0.230 / 88.8% / 88.7% |
| 0.95 | 0.180 / 95.2% / 95.2% | 0.181 / 95.6% / 95.6% | 0.181 / 95.5% / 95.5% | 0.182 / 95.4% / 95.4% | 0.180 / 94.9% / 94.9% |
| 0.975 | 0.134 / 97.8% / 97.8% | 0.138 / 98.2% / 98.2% | 0.134 / 97.9% / 97.9% | 0.138 / 98.1% / 98.1% | 0.134 / 97.8% / 97.8% |
| 0.99 | 0.094 / 98.7% / 98.7% | 0.103 / 99.4% / 99.4% | 0.094 / 99.0% / 99.0% | 0.103 / 99.3% / 99.3% | 0.093 / 98.9% / 98.9% |
