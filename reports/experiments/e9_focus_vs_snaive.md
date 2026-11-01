# E9 test origins (focus set, vs. seasonal naive)

Reference for the bootstrap: `snaive-focus-test-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best-crps-focus-test-r1 | best-crps | focus | 0.711 | 0.829 | 0.887 | 0.7% | 0.336 | 0.391 | 85.1% | 97.5% | 81.4% | 94.5% |
| lgbm-total-q-p1.8-focus-test-r1 | lgbm-total-q-p1.8 | focus | 0.711 | 0.829 | 0.887 | 0.7% | 0.336 | 0.391 | 85.1% | 97.5% | 81.4% | 94.5% |
| ma4-focus-test-r1 | ma4 | focus | 0.715 | 0.862 | 0.922 | 9.0% | 0.385 | 0.444 | 85.5% | 96.5% | 81.4% | 95.2% |
| naive-focus-test-r1 | naive | focus | 0.822 | 0.993 | 1.054 | 8.5% | 0.448 | 0.520 | 84.4% | 95.8% | 80.5% | 94.6% |
| snaive-focus-test-r1 | snaive | focus | 1.273 | 1.304 | 1.284 | -41.2% | 0.611 | 0.609 | 80.1% | 95.0% | 75.0% | 92.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| best-crps-focus-test-r1 | -0.562 [-0.611, -0.512] * | -0.481 [-0.544, -0.414] * | -0.275 [-0.305, -0.246] * |
| lgbm-total-q-p1.8-focus-test-r1 | -0.562 [-0.611, -0.512] * | -0.481 [-0.544, -0.414] * | -0.275 [-0.305, -0.246] * |
| ma4-focus-test-r1 | -0.558 [-0.611, -0.503] * | -0.449 [-0.521, -0.371] * | -0.226 [-0.257, -0.197] * |
| naive-focus-test-r1 | -0.450 [-0.507, -0.394] * | -0.319 [-0.389, -0.246] * | -0.163 [-0.196, -0.132] * |

## MASE per segment

| segment | series | best-crps-focus-test-r1 | lgbm-total-q-p1.8-focus-test-r1 | ma4-focus-test-r1 | naive-focus-test-r1 | snaive-focus-test-r1 |
|---|---|---|---|---|---|---|
| A-erratic | 373 | 0.654 | 0.654 | 0.644 | 0.733 | 1.191 |
| A-intermittent | 16 | 0.784 | 0.784 | 0.807 | 0.947 | 1.467 |
| A-lumpy | 66 | 0.856 | 0.856 | 0.830 | 0.877 | 1.890 |
| A-smooth | 293 | 0.748 | 0.748 | 0.775 | 0.917 | 1.228 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | best-crps-focus-test-r1 | lgbm-total-q-p1.8-focus-test-r1 | ma4-focus-test-r1 | naive-focus-test-r1 | snaive-focus-test-r1 |
|---|---|---|---|---|---|
| 0.025 | 0.024 / 18.9% / 3.0% | 0.024 / 18.9% / 3.0% | 0.032 / 19.7% / 2.2% | 0.065 / 20.4% / 2.8% | 0.114 / 20.8% / 5.5% |
| 0.05 | 0.049 / 18.9% / 5.4% | 0.049 / 18.9% / 5.4% | 0.061 / 20.8% / 4.4% | 0.109 / 21.7% / 5.2% | 0.199 / 23.1% / 10.0% |
| 0.1 | 0.094 / 19.9% / 9.1% | 0.094 / 19.9% / 9.1% | 0.117 / 23.3% / 9.2% | 0.181 / 24.8% / 10.4% | 0.329 / 27.5% / 17.5% |
| 0.2 | 0.168 / 26.5% / 18.6% | 0.168 / 26.5% / 18.6% | 0.210 / 29.7% / 19.2% | 0.288 / 31.5% / 20.6% | 0.489 / 36.2% / 30.1% |
| 0.5 | 0.317 / 53.2% / 50.9% | 0.317 / 53.2% / 50.9% | 0.355 / 52.8% / 50.1% | 0.411 / 55.0% / 51.2% | 0.610 / 60.9% / 59.9% |
| 0.8 | 0.326 / 82.1% / 82.0% | 0.326 / 82.1% / 82.0% | 0.361 / 80.5% / 80.5% | 0.385 / 81.3% / 81.3% | 0.457 / 84.8% / 84.8% |
| 0.9 | 0.265 / 90.4% / 90.4% | 0.265 / 90.4% / 90.4% | 0.299 / 90.6% / 90.6% | 0.309 / 90.9% / 90.9% | 0.341 / 92.6% / 92.6% |
| 0.95 | 0.200 / 94.9% / 94.9% | 0.200 / 94.9% / 94.9% | 0.227 / 95.2% / 95.2% | 0.230 / 95.3% / 95.3% | 0.244 / 96.1% / 96.1% |
| 0.975 | 0.143 / 97.5% / 97.5% | 0.143 / 97.5% / 97.5% | 0.163 / 97.4% / 97.4% | 0.163 / 97.5% / 97.5% | 0.169 / 97.9% / 97.9% |
| 0.99 | 0.093 / 98.9% / 98.9% | 0.093 / 98.9% / 98.9% | 0.098 / 98.8% / 98.8% | 0.098 / 98.8% / 98.8% | 0.100 / 99.0% / 99.0% |
