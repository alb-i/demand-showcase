# E6 conformal calibration of the E5 quantile models (full set, tuning origins)

Reference for the bootstrap: `lgbm-total-q-p1.8-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8 | full | 0.683 | 0.651 | 1.646 | -5.0% | 0.357 | 0.303 | 90.0% | 97.9% | 77.5% | 93.6% |
| lgbm-total-q-p1.8-cqr13-full-r1 | lgbm-total-q-p1.8-cqr13 | full | 0.683 | 0.651 | 1.646 | -5.0% | 0.358 | 0.304 | 89.7% | 97.9% | 77.4% | 93.6% |
| lgbm-total-q-p1.8-cqr13-all-full-r1 | lgbm-total-q-p1.8-cqr13-all | full | 0.683 | 0.651 | 1.646 | -5.0% | 0.357 | 0.303 | 89.9% | 97.9% | 77.6% | 93.7% |
| lgbm-total-q-p1.8-cqr26-full-r1 | lgbm-total-q-p1.8-cqr26 | full | 0.683 | 0.651 | 1.646 | -5.0% | 0.357 | 0.304 | 89.6% | 97.8% | 77.4% | 93.6% |
| lgbm-total-q-p1.8-cqr26-all-full-r1 | lgbm-total-q-p1.8-cqr26-all | full | 0.683 | 0.651 | 1.646 | -5.0% | 0.357 | 0.303 | 89.9% | 97.8% | 77.7% | 93.7% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-cqr13-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.001] * |
| lgbm-total-q-p1.8-cqr13-all-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, +0.000] |
| lgbm-total-q-p1.8-cqr26-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] * |
| lgbm-total-q-p1.8-cqr26-all-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.000 [-0.000, -0.000] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8-cqr13-full-r1 | lgbm-total-q-p1.8-cqr13-all-full-r1 | lgbm-total-q-p1.8-cqr26-full-r1 | lgbm-total-q-p1.8-cqr26-all-full-r1 |
|---|---|---|---|---|---|---|
| A-erratic | 448 | 0.634 | 0.634 | 0.634 | 0.634 | 0.634 |
| A-intermittent | 26 | 0.673 | 0.673 | 0.673 | 0.673 | 0.673 |
| A-lumpy | 114 | 0.578 | 0.578 | 0.578 | 0.578 | 0.578 |
| A-smooth | 364 | 0.678 | 0.678 | 0.678 | 0.678 | 0.678 |
| B-erratic | 434 | 0.646 | 0.646 | 0.646 | 0.646 | 0.646 |
| B-intermittent | 61 | 0.553 | 0.553 | 0.553 | 0.553 | 0.553 |
| B-lumpy | 530 | 0.673 | 0.673 | 0.673 | 0.673 | 0.673 |
| B-smooth | 120 | 0.711 | 0.711 | 0.711 | 0.711 | 0.711 |
| C-erratic | 122 | 0.388 | 0.388 | 0.388 | 0.388 | 0.388 |
| C-intermittent | 605 | 0.801 | 0.801 | 0.801 | 0.801 | 0.801 |
| C-lumpy | 1188 | 0.771 | 0.771 | 0.771 | 0.771 | 0.771 |
| C-smooth | 132 | 0.347 | 0.347 | 0.347 | 0.347 | 0.347 |
| unclassified | 140 | 0.309 | 0.309 | 0.309 | 0.309 | 0.309 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-full-r1 | lgbm-total-q-p1.8-cqr13-full-r1 | lgbm-total-q-p1.8-cqr13-all-full-r1 | lgbm-total-q-p1.8-cqr26-full-r1 | lgbm-total-q-p1.8-cqr26-all-full-r1 |
|---|---|---|---|---|---|
| 0.025 | 0.015 / 59.9% / 4.3% | 0.015 / 59.9% / 4.2% | 0.015 / 59.9% / 4.2% | 0.015 / 59.9% / 4.2% | 0.015 / 59.9% / 4.1% |
| 0.05 | 0.029 / 59.9% / 8.3% | 0.029 / 59.9% / 8.1% | 0.029 / 59.9% / 8.0% | 0.029 / 59.9% / 8.0% | 0.029 / 59.9% / 8.0% |
| 0.1 | 0.058 / 60.3% / 15.5% | 0.058 / 60.4% / 15.1% | 0.058 / 60.3% / 14.9% | 0.058 / 60.4% / 15.0% | 0.058 / 60.3% / 14.8% |
| 0.2 | 0.112 / 62.4% / 28.9% | 0.112 / 62.7% / 28.1% | 0.112 / 62.4% / 27.7% | 0.112 / 62.7% / 27.9% | 0.112 / 62.4% / 27.4% |
| 0.5 | 0.256 / 72.8% / 63.0% | 0.256 / 72.9% / 60.6% | 0.256 / 72.8% / 60.5% | 0.256 / 72.9% / 60.0% | 0.256 / 72.8% / 59.8% |
| 0.8 | 0.333 / 87.6% / 87.2% | 0.333 / 87.3% / 85.5% | 0.333 / 87.5% / 85.7% | 0.333 / 87.3% / 85.2% | 0.333 / 87.5% / 85.4% |
| 0.9 | 0.311 / 93.1% / 93.1% | 0.311 / 92.9% / 92.5% | 0.311 / 93.0% / 92.6% | 0.311 / 92.9% / 92.4% | 0.311 / 93.0% / 92.5% |
| 0.95 | 0.271 / 96.3% / 96.3% | 0.271 / 96.1% / 96.0% | 0.271 / 96.2% / 96.1% | 0.271 / 96.0% / 95.9% | 0.271 / 96.2% / 96.1% |
| 0.975 | 0.225 / 97.9% / 97.9% | 0.226 / 97.9% / 97.8% | 0.225 / 97.9% / 97.8% | 0.225 / 97.8% / 97.8% | 0.225 / 97.8% / 97.8% |
| 0.99 | 0.177 / 99.0% / 99.0% | 0.178 / 99.0% / 99.0% | 0.177 / 98.9% / 98.9% | 0.178 / 98.9% / 98.9% | 0.177 / 98.9% / 98.9% |
