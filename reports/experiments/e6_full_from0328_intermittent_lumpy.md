# E6 conformal calibration of the E5 quantile models (full set, tuning origins from 2011-03-28, intermittent + lumpy)

Reference for the bootstrap: `lgbm-total-q-p1.8-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8 | full | 0.761 | 0.504 | 1.531 | 13.5% | 0.442 | 0.253 | 91.6% | 97.6% | 76.7% | 93.5% |
| lgbm-total-q-p1.8-cqr13-full-r1 | lgbm-total-q-p1.8-cqr13 | full | 0.761 | 0.504 | 1.531 | 13.5% | 0.442 | 0.254 | 91.7% | 97.7% | 76.8% | 93.8% |
| lgbm-total-q-p1.8-cqr13-all-full-r1 | lgbm-total-q-p1.8-cqr13-all | full | 0.761 | 0.504 | 1.531 | 13.5% | 0.442 | 0.253 | 91.6% | 97.6% | 76.8% | 93.7% |
| lgbm-total-q-p1.8-cqr26-full-r1 | lgbm-total-q-p1.8-cqr26 | full | 0.761 | 0.504 | 1.531 | 13.5% | 0.442 | 0.253 | 91.6% | 97.6% | 77.0% | 93.7% |
| lgbm-total-q-p1.8-cqr26-all-full-r1 | lgbm-total-q-p1.8-cqr26-all | full | 0.761 | 0.504 | 1.531 | 13.5% | 0.442 | 0.253 | 91.6% | 97.5% | 77.0% | 93.7% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-cqr13-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.001] |
| lgbm-total-q-p1.8-cqr13-all-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, -0.000] * |
| lgbm-total-q-p1.8-cqr26-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, +0.000] |
| lgbm-total-q-p1.8-cqr26-all-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, +0.000] |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8-cqr13-full-r1 | lgbm-total-q-p1.8-cqr13-all-full-r1 | lgbm-total-q-p1.8-cqr26-full-r1 | lgbm-total-q-p1.8-cqr26-all-full-r1 |
|---|---|---|---|---|---|---|
| A-intermittent | 26 | 0.676 | 0.676 | 0.676 | 0.676 | 0.676 |
| A-lumpy | 114 | 0.318 | 0.318 | 0.318 | 0.318 | 0.318 |
| B-intermittent | 61 | 0.480 | 0.480 | 0.480 | 0.480 | 0.480 |
| B-lumpy | 530 | 0.605 | 0.605 | 0.605 | 0.605 | 0.605 |
| C-intermittent | 605 | 0.990 | 0.990 | 0.990 | 0.990 | 0.990 |
| C-lumpy | 1188 | 0.774 | 0.774 | 0.774 | 0.774 | 0.774 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8-cqr13-full-r1 | lgbm-total-q-p1.8-cqr13-all-full-r1 | lgbm-total-q-p1.8-cqr26-full-r1 | lgbm-total-q-p1.8-cqr26-all-full-r1 |
|---|---|---|---|---|---|
| 0.025 | 0.014 / 77.9% / 4.0% | 0.014 / 77.9% / 3.9% | 0.014 / 77.9% / 3.9% | 0.014 / 77.9% / 3.8% | 0.014 / 77.9% / 3.8% |
| 0.05 | 0.028 / 77.9% / 8.0% | 0.028 / 77.9% / 7.8% | 0.028 / 77.9% / 7.8% | 0.028 / 77.9% / 7.7% | 0.028 / 77.9% / 7.7% |
| 0.1 | 0.056 / 77.9% / 15.7% | 0.056 / 77.9% / 15.3% | 0.056 / 77.9% / 15.3% | 0.056 / 77.9% / 15.0% | 0.056 / 77.9% / 15.0% |
| 0.2 | 0.113 / 78.0% / 30.0% | 0.113 / 78.0% / 29.2% | 0.113 / 78.0% / 29.2% | 0.113 / 78.0% / 28.6% | 0.113 / 78.0% / 28.5% |
| 0.5 | 0.280 / 79.8% / 65.0% | 0.280 / 79.8% / 63.1% | 0.280 / 79.8% / 63.1% | 0.280 / 79.8% / 61.7% | 0.280 / 79.8% / 61.3% |
| 0.8 | 0.405 / 87.6% / 87.1% | 0.405 / 87.6% / 86.0% | 0.405 / 87.6% / 86.0% | 0.405 / 87.6% / 85.3% | 0.405 / 87.6% / 85.1% |
| 0.9 | 0.404 / 92.5% / 92.4% | 0.404 / 92.4% / 92.1% | 0.404 / 92.4% / 92.1% | 0.404 / 92.4% / 92.0% | 0.404 / 92.4% / 92.0% |
| 0.95 | 0.363 / 95.8% / 95.8% | 0.363 / 95.8% / 95.7% | 0.363 / 95.7% / 95.7% | 0.363 / 95.7% / 95.6% | 0.363 / 95.7% / 95.7% |
| 0.975 | 0.309 / 97.6% / 97.6% | 0.309 / 97.7% / 97.7% | 0.309 / 97.6% / 97.6% | 0.309 / 97.6% / 97.6% | 0.309 / 97.5% / 97.5% |
| 0.99 | 0.237 / 98.7% / 98.7% | 0.237 / 98.9% / 98.9% | 0.236 / 98.8% / 98.8% | 0.236 / 98.8% / 98.8% | 0.237 / 98.7% / 98.7% |
