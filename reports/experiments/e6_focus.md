# E6 conformal calibration of the E5 quantile models (focus set, tuning origins)

Reference for the bootstrap: `lgbm-total-q-p1.8-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8 | focus | 0.686 | 0.678 | 2.726 | 1.5% | 0.339 | 0.321 | 83.2% | 97.4% | 80.0% | 93.7% |
| lgbm-total-q-p1.8-cqr13-focus-r1 | lgbm-total-q-p1.8-cqr13 | focus | 0.686 | 0.678 | 2.726 | 1.5% | 0.343 | 0.324 | 80.6% | 97.1% | 77.5% | 93.3% |
| lgbm-total-q-p1.8-cqr13-all-focus-r1 | lgbm-total-q-p1.8-cqr13-all | focus | 0.686 | 0.678 | 2.726 | 1.5% | 0.340 | 0.322 | 82.4% | 97.2% | 78.9% | 93.5% |
| lgbm-total-q-p1.8-cqr26-focus-r1 | lgbm-total-q-p1.8-cqr26 | focus | 0.686 | 0.678 | 2.726 | 1.5% | 0.343 | 0.324 | 80.3% | 97.0% | 77.2% | 93.2% |
| lgbm-total-q-p1.8-cqr26-all-focus-r1 | lgbm-total-q-p1.8-cqr26-all | focus | 0.686 | 0.678 | 2.726 | 1.5% | 0.340 | 0.322 | 82.2% | 97.1% | 78.8% | 93.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-cqr13-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.004 [+0.003, +0.005] * |
| lgbm-total-q-p1.8-cqr13-all-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.001 [+0.001, +0.002] * |
| lgbm-total-q-p1.8-cqr26-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.004 [+0.003, +0.005] * |
| lgbm-total-q-p1.8-cqr26-all-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.001 [+0.001, +0.002] * |

## MASE per segment

| segment | series | lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8-cqr13-focus-r1 | lgbm-total-q-p1.8-cqr13-all-focus-r1 | lgbm-total-q-p1.8-cqr26-focus-r1 | lgbm-total-q-p1.8-cqr26-all-focus-r1 |
|---|---|---|---|---|---|---|
| A-erratic | 373 | 0.660 | 0.660 | 0.660 | 0.660 | 0.660 |
| A-intermittent | 16 | 0.800 | 0.800 | 0.800 | 0.800 | 0.800 |
| A-lumpy | 66 | 0.832 | 0.832 | 0.832 | 0.832 | 0.832 |
| A-smooth | 293 | 0.680 | 0.680 | 0.680 | 0.680 | 0.680 |

## Per quantile level: scaled pinball / share of y <= q / randomised PIT (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated; the randomised PIT counts such ties fractionally.

| tau | lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8-cqr13-focus-r1 | lgbm-total-q-p1.8-cqr13-all-focus-r1 | lgbm-total-q-p1.8-cqr26-focus-r1 | lgbm-total-q-p1.8-cqr26-all-focus-r1 |
|---|---|---|---|---|---|
| 0.025 | 0.021 / 15.6% / 3.6% | 0.021 / 15.6% / 3.9% | 0.021 / 15.6% / 3.7% | 0.021 / 15.6% / 3.8% | 0.021 / 15.6% / 3.7% |
| 0.05 | 0.043 / 15.6% / 6.4% | 0.043 / 15.7% / 6.8% | 0.043 / 15.6% / 6.5% | 0.043 / 15.7% / 6.7% | 0.043 / 15.6% / 6.4% |
| 0.1 | 0.083 / 17.1% / 10.5% | 0.083 / 18.2% / 12.0% | 0.083 / 17.1% / 10.7% | 0.083 / 18.4% / 12.0% | 0.083 / 17.1% / 10.6% |
| 0.2 | 0.153 / 24.1% / 20.0% | 0.153 / 26.4% / 22.4% | 0.153 / 24.5% / 20.5% | 0.153 / 26.7% / 22.6% | 0.153 / 24.5% / 20.4% |
| 0.5 | 0.302 / 52.0% / 51.0% | 0.302 / 52.7% / 51.6% | 0.302 / 52.1% / 51.0% | 0.302 / 52.7% / 51.5% | 0.302 / 52.1% / 50.7% |
| 0.8 | 0.325 / 82.2% / 82.2% | 0.326 / 80.2% / 80.0% | 0.326 / 80.5% / 80.4% | 0.326 / 79.9% / 79.7% | 0.325 / 80.3% / 80.1% |
| 0.9 | 0.270 / 90.5% / 90.5% | 0.272 / 89.5% / 89.5% | 0.272 / 89.7% / 89.6% | 0.272 / 89.3% / 89.3% | 0.272 / 89.4% / 89.4% |
| 0.95 | 0.214 / 95.0% / 95.0% | 0.217 / 94.3% / 94.3% | 0.216 / 94.4% / 94.4% | 0.217 / 94.1% / 94.1% | 0.216 / 94.2% / 94.2% |
| 0.975 | 0.163 / 97.4% / 97.4% | 0.166 / 97.1% / 97.1% | 0.165 / 97.2% / 97.2% | 0.165 / 97.0% / 97.0% | 0.165 / 97.1% / 97.1% |
| 0.99 | 0.118 / 98.8% / 98.8% | 0.131 / 98.8% / 98.8% | 0.119 / 98.8% / 98.8% | 0.131 / 98.7% / 98.7% | 0.119 / 98.7% / 98.7% |
