# E6 conformal calibration of the E5 quantile models (focus set, tuning origins from 2011-03-28)

Reference for the bootstrap: `lgbm-total-q-p1.8-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8 | focus | 0.639 | 0.692 | 0.819 | 2.7% | 0.304 | 0.335 | 82.8% | 97.4% | 79.0% | 93.5% |
| lgbm-total-q-p1.8-cqr13-focus-r1 | lgbm-total-q-p1.8-cqr13 | focus | 0.639 | 0.692 | 0.819 | 2.7% | 0.305 | 0.336 | 80.7% | 97.6% | 77.1% | 93.4% |
| lgbm-total-q-p1.8-cqr13-all-focus-r1 | lgbm-total-q-p1.8-cqr13-all | focus | 0.639 | 0.692 | 0.819 | 2.7% | 0.305 | 0.335 | 82.8% | 97.6% | 78.8% | 93.7% |
| lgbm-total-q-p1.8-cqr26-focus-r1 | lgbm-total-q-p1.8-cqr26 | focus | 0.639 | 0.692 | 0.819 | 2.7% | 0.305 | 0.336 | 80.2% | 97.4% | 76.5% | 93.3% |
| lgbm-total-q-p1.8-cqr26-all-focus-r1 | lgbm-total-q-p1.8-cqr26-all | focus | 0.639 | 0.692 | 0.819 | 2.7% | 0.304 | 0.335 | 82.4% | 97.5% | 78.4% | 93.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-cqr13-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.001 [+0.001, +0.002] * |
| lgbm-total-q-p1.8-cqr13-all-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.001 [+0.000, +0.001] * |
| lgbm-total-q-p1.8-cqr26-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.001 [+0.000, +0.002] * |
| lgbm-total-q-p1.8-cqr26-all-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8-cqr13-focus-r1 | lgbm-total-q-p1.8-cqr13-all-focus-r1 | lgbm-total-q-p1.8-cqr26-focus-r1 | lgbm-total-q-p1.8-cqr26-all-focus-r1 |
|---|---|---|---|---|---|---|
| A-erratic | 373 | 0.644 | 0.644 | 0.644 | 0.644 | 0.644 |
| A-intermittent | 16 | 0.885 | 0.885 | 0.885 | 0.885 | 0.885 |
| A-lumpy | 66 | 0.400 | 0.400 | 0.400 | 0.400 | 0.400 |
| A-smooth | 293 | 0.672 | 0.672 | 0.672 | 0.672 | 0.672 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8-cqr13-focus-r1 | lgbm-total-q-p1.8-cqr13-all-focus-r1 | lgbm-total-q-p1.8-cqr26-focus-r1 | lgbm-total-q-p1.8-cqr26-all-focus-r1 |
|---|---|---|---|---|---|
| 0.025 | 0.020 / 18.4% / 3.9% | 0.020 / 18.4% / 4.2% | 0.020 / 18.4% / 4.0% | 0.020 / 18.4% / 4.1% | 0.020 / 18.4% / 3.9% |
| 0.05 | 0.041 / 18.4% / 6.9% | 0.041 / 18.4% / 7.5% | 0.041 / 18.4% / 7.0% | 0.041 / 18.4% / 7.2% | 0.041 / 18.4% / 6.9% |
| 0.1 | 0.079 / 19.7% / 11.3% | 0.079 / 20.8% / 13.1% | 0.079 / 19.7% / 11.5% | 0.079 / 21.3% / 13.3% | 0.079 / 19.7% / 11.3% |
| 0.2 | 0.145 / 27.2% / 21.6% | 0.145 / 29.3% / 24.3% | 0.145 / 27.2% / 22.0% | 0.145 / 30.0% / 24.6% | 0.145 / 27.3% / 21.7% |
| 0.5 | 0.282 / 54.1% / 52.7% | 0.283 / 55.3% / 53.8% | 0.282 / 54.3% / 52.9% | 0.283 / 55.3% / 53.6% | 0.282 / 54.3% / 52.3% |
| 0.8 | 0.297 / 82.0% / 81.9% | 0.297 / 81.3% / 81.1% | 0.297 / 81.5% / 81.3% | 0.297 / 80.6% / 80.3% | 0.297 / 81.0% / 80.7% |
| 0.9 | 0.243 / 90.3% / 90.2% | 0.244 / 90.3% / 90.3% | 0.244 / 90.3% / 90.2% | 0.243 / 89.8% / 89.8% | 0.243 / 89.8% / 89.7% |
| 0.95 | 0.186 / 94.9% / 94.9% | 0.188 / 95.2% / 95.2% | 0.187 / 95.2% / 95.2% | 0.187 / 94.8% / 94.8% | 0.186 / 94.7% / 94.7% |
| 0.975 | 0.137 / 97.4% / 97.4% | 0.138 / 97.6% / 97.6% | 0.137 / 97.6% / 97.6% | 0.138 / 97.4% / 97.4% | 0.137 / 97.5% / 97.5% |
| 0.99 | 0.091 / 98.8% / 98.8% | 0.093 / 99.0% / 99.0% | 0.091 / 99.0% / 99.0% | 0.093 / 98.9% / 98.9% | 0.091 / 99.0% / 99.0% |
