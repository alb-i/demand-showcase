# E6 conformal calibration of the E5 quantile models (full set, tuning origins from 2011-03-28)

Reference for the bootstrap: `lgbm-total-q-p1.8-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only origins from 2011-03-28 on.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8 | full | 0.693 | 0.660 | 1.365 | -2.4% | 0.378 | 0.314 | 89.6% | 97.8% | 78.1% | 93.7% |
| lgbm-total-q-p1.8-cqr13-full-r1 | lgbm-total-q-p1.8-cqr13 | full | 0.693 | 0.660 | 1.365 | -2.4% | 0.378 | 0.315 | 89.4% | 97.9% | 78.0% | 93.9% |
| lgbm-total-q-p1.8-cqr13-all-full-r1 | lgbm-total-q-p1.8-cqr13-all | full | 0.693 | 0.660 | 1.365 | -2.4% | 0.378 | 0.314 | 89.5% | 97.8% | 78.2% | 93.8% |
| lgbm-total-q-p1.8-cqr26-full-r1 | lgbm-total-q-p1.8-cqr26 | full | 0.693 | 0.660 | 1.365 | -2.4% | 0.378 | 0.314 | 89.3% | 97.8% | 78.0% | 93.8% |
| lgbm-total-q-p1.8-cqr26-all-full-r1 | lgbm-total-q-p1.8-cqr26-all | full | 0.693 | 0.660 | 1.365 | -2.4% | 0.378 | 0.314 | 89.5% | 97.8% | 78.3% | 93.8% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-cqr13-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [-0.000, +0.001] |
| lgbm-total-q-p1.8-cqr13-all-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, +0.000] |
| lgbm-total-q-p1.8-cqr26-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, +0.000] |
| lgbm-total-q-p1.8-cqr26-all-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, -0.000] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8-cqr13-full-r1 | lgbm-total-q-p1.8-cqr13-all-full-r1 | lgbm-total-q-p1.8-cqr26-full-r1 | lgbm-total-q-p1.8-cqr26-all-full-r1 |
|---|---|---|---|---|---|---|
| A-erratic | 448 | 0.614 | 0.614 | 0.614 | 0.614 | 0.614 |
| A-intermittent | 26 | 0.676 | 0.676 | 0.676 | 0.676 | 0.676 |
| A-lumpy | 114 | 0.318 | 0.318 | 0.318 | 0.318 | 0.318 |
| A-smooth | 364 | 0.669 | 0.669 | 0.669 | 0.669 | 0.669 |
| B-erratic | 434 | 0.577 | 0.577 | 0.577 | 0.577 | 0.577 |
| B-intermittent | 61 | 0.480 | 0.480 | 0.480 | 0.480 | 0.480 |
| B-lumpy | 530 | 0.605 | 0.605 | 0.605 | 0.605 | 0.605 |
| B-smooth | 120 | 0.726 | 0.726 | 0.726 | 0.726 | 0.726 |
| C-erratic | 122 | 0.391 | 0.391 | 0.391 | 0.391 | 0.391 |
| C-intermittent | 605 | 0.990 | 0.990 | 0.990 | 0.990 | 0.990 |
| C-lumpy | 1188 | 0.774 | 0.774 | 0.774 | 0.774 | 0.774 |
| C-smooth | 132 | 0.458 | 0.458 | 0.458 | 0.458 | 0.458 |
| unclassified | 140 | 0.524 | 0.524 | 0.524 | 0.524 | 0.524 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8-cqr13-full-r1 | lgbm-total-q-p1.8-cqr13-all-full-r1 | lgbm-total-q-p1.8-cqr26-full-r1 | lgbm-total-q-p1.8-cqr26-all-full-r1 |
|---|---|---|---|---|---|
| 0.025 | 0.015 / 60.8% / 4.1% | 0.015 / 60.8% / 4.0% | 0.015 / 60.8% / 4.0% | 0.015 / 60.8% / 4.0% | 0.015 / 60.8% / 3.9% |
| 0.05 | 0.030 / 60.8% / 7.8% | 0.030 / 60.8% / 7.7% | 0.030 / 60.8% / 7.7% | 0.030 / 60.8% / 7.6% | 0.030 / 60.8% / 7.5% |
| 0.1 | 0.060 / 61.1% / 14.5% | 0.060 / 61.2% / 14.3% | 0.060 / 61.1% / 14.1% | 0.060 / 61.2% / 14.1% | 0.060 / 61.1% / 13.8% |
| 0.2 | 0.117 / 63.4% / 27.3% | 0.117 / 63.7% / 27.0% | 0.117 / 63.4% / 26.6% | 0.117 / 63.8% / 26.6% | 0.117 / 63.4% / 26.1% |
| 0.5 | 0.268 / 73.5% / 62.1% | 0.268 / 73.6% / 60.4% | 0.268 / 73.5% / 60.4% | 0.268 / 73.7% / 59.2% | 0.268 / 73.5% / 59.0% |
| 0.8 | 0.351 / 87.1% / 86.8% | 0.351 / 87.1% / 85.6% | 0.351 / 87.1% / 85.7% | 0.351 / 87.0% / 84.9% | 0.351 / 87.1% / 85.0% |
| 0.9 | 0.333 / 92.6% / 92.6% | 0.333 / 92.6% / 92.3% | 0.333 / 92.6% / 92.3% | 0.333 / 92.6% / 92.1% | 0.333 / 92.6% / 92.2% |
| 0.95 | 0.290 / 96.0% / 96.0% | 0.290 / 96.0% / 96.0% | 0.290 / 96.0% / 95.9% | 0.290 / 95.9% / 95.8% | 0.290 / 96.0% / 95.9% |
| 0.975 | 0.242 / 97.8% / 97.8% | 0.242 / 97.9% / 97.9% | 0.242 / 97.8% / 97.8% | 0.242 / 97.8% / 97.7% | 0.242 / 97.8% / 97.8% |
| 0.99 | 0.182 / 98.9% / 98.9% | 0.183 / 99.0% / 99.0% | 0.182 / 99.0% / 99.0% | 0.182 / 98.9% / 98.9% | 0.182 / 98.9% / 98.9% |
