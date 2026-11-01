# E5 LightGBM quantile models (focus set, tuning origins)

Reference for the bootstrap: `lgbm-total-p1.8-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| lgbm-total-p1.8-focus-r1 | lgbm-total-p1.8 | focus | 0.686 | 0.678 | 2.726 | 1.5% | 0.354 | 0.334 | 85.2% | 96.3% |
| lgbm-total-q-p1.8-focus-r1 | lgbm-total-q-p1.8 | focus | 0.686 | 0.678 | 2.726 | 1.5% | 0.339 | 0.321 | 83.2% | 97.4% |
| split-ma4-bulk-ma52-focus-r6 | split-ma4-bulk-ma52 | focus | 0.732 | 0.737 | 2.728 | -12.8% | 0.364 | 0.340 | 89.7% | 97.8% |
| lgbm-total-focus-r1 | lgbm-total | focus | 0.692 | 0.685 | 2.727 | 2.1% | 0.357 | 0.338 | 85.0% | 96.3% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-total-q-p1.8-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | -0.016 [-0.020, -0.012] * |
| split-ma4-bulk-ma52-focus-r6 | +0.046 [+0.035, +0.057] * | +0.058 [+0.038, +0.081] * | +0.010 [+0.005, +0.015] * |
| lgbm-total-focus-r1 | +0.006 [+0.004, +0.008] * | +0.006 [+0.003, +0.009] * | +0.003 [+0.002, +0.004] * |

## MASE per segment

| segment | series | lgbm-total-p1.8-focus-r1 | lgbm-total-q-p1.8-focus-r1 | split-ma4-bulk-ma52-focus-r6 | lgbm-total-focus-r1 |
|---|---|---|---|---|---|
| A-erratic | 373 | 0.660 | 0.660 | 0.699 | 0.666 |
| A-intermittent | 16 | 0.800 | 0.800 | 0.866 | 0.821 |
| A-lumpy | 66 | 0.832 | 0.832 | 1.064 | 0.874 |
| A-smooth | 293 | 0.680 | 0.680 | 0.691 | 0.676 |

## MASE / CRPS per product category

| category | series | lgbm-total-p1.8-focus-r1 | lgbm-total-q-p1.8-focus-r1 | split-ma4-bulk-ma52-focus-r6 | lgbm-total-focus-r1 |
|---|---|---|---|---|---|
| kitchen_tableware | 169 | 0.685 / 0.319 | 0.685 / 0.302 | 0.693 / 0.330 | 0.681 / 0.321 |
| bags | 67 | 0.681 / 0.337 | 0.681 / 0.326 | 0.693 / 0.323 | 0.685 / 0.340 |
| stationery_craft | 66 | 0.658 / 0.298 | 0.658 / 0.286 | 0.688 / 0.303 | 0.657 / 0.303 |
| candles_lights | 64 | 0.561 / 0.262 | 0.561 / 0.250 | 0.615 / 0.272 | 0.568 / 0.263 |
| wall_decor | 61 | 0.631 / 0.295 | 0.631 / 0.289 | 0.656 / 0.296 | 0.637 / 0.297 |
| party_giftwrap | 55 | 0.755 / 0.358 | 0.755 / 0.326 | 0.745 / 0.351 | 0.755 / 0.365 |
| storage | 43 | 0.748 / 0.384 | 0.748 / 0.353 | 0.798 / 0.373 | 0.751 / 0.386 |
| toys_games | 43 | 0.637 / 0.321 | 0.637 / 0.311 | 0.653 / 0.333 | 0.628 / 0.322 |
| textiles_cushions | 38 | 0.590 / 0.342 | 0.590 / 0.334 | 0.756 / 0.401 | 0.624 / 0.347 |
| garden_outdoor | 34 | 0.750 / 0.439 | 0.750 / 0.406 | 0.783 / 0.439 | 0.763 / 0.441 |
| decorations | 33 | 0.522 / 0.237 | 0.522 / 0.237 | 0.620 / 0.268 | 0.545 / 0.240 |
| accessories | 20 | 0.523 / 0.259 | 0.523 / 0.245 | 0.559 / 0.273 | 0.529 / 0.260 |
| christmas | 17 | 0.522 / 0.386 | 0.522 / 0.337 | 0.864 / 0.438 | 0.561 / 0.392 |
| furniture | 16 | 0.636 / 0.331 | 0.636 / 0.319 | 0.739 / 0.347 | 0.655 / 0.334 |
| easter | 11 | 0.887 / 0.457 | 0.887 / 0.442 | 1.123 / 0.527 | 0.948 / 0.476 |
| bath_beauty | 9 | 0.721 / 0.298 | 0.721 / 0.291 | 0.833 / 0.343 | 0.724 / 0.298 |
| other | 2 | 10.977 / 11.832 | 10.977 / 11.885 | 11.201 / 11.880 | 11.016 / 11.837 |

## Per quantile level: scaled pinball / share of y <= q (ideal: tau)

Demand is discrete with many zero weeks: y = q = 0 counts as y <= q, so the low levels hit more often than tau even when calibrated.

| tau | lgbm-total-p1.8-focus-r1 | lgbm-total-q-p1.8-focus-r1 | split-ma4-bulk-ma52-focus-r6 | lgbm-total-focus-r1 |
|---|---|---|---|---|
| 0.025 | 0.026 / 16.3% | 0.021 / 15.6% | 0.028 / 16.2% | 0.027 / 16.3% |
| 0.05 | 0.049 / 17.1% | 0.043 / 15.6% | 0.053 / 16.8% | 0.050 / 17.1% |
| 0.1 | 0.093 / 19.0% | 0.083 / 17.1% | 0.098 / 18.5% | 0.094 / 19.0% |
| 0.2 | 0.170 / 24.2% | 0.153 / 24.1% | 0.174 / 23.8% | 0.171 / 24.0% |
| 0.5 | 0.318 / 46.8% | 0.302 / 52.0% | 0.321 / 54.6% | 0.323 / 45.3% |
| 0.8 | 0.331 / 78.4% | 0.325 / 82.2% | 0.342 / 85.4% | 0.334 / 77.7% |
| 0.9 | 0.280 / 89.9% | 0.270 / 90.5% | 0.290 / 93.5% | 0.282 / 89.5% |
| 0.95 | 0.221 / 94.9% | 0.214 / 95.0% | 0.228 / 97.1% | 0.222 / 94.8% |
| 0.975 | 0.168 / 97.3% | 0.163 / 97.4% | 0.172 / 98.6% | 0.168 / 97.3% |
| 0.99 | 0.117 / 98.8% | 0.118 / 98.8% | 0.116 / 99.4% | 0.117 / 98.8% |
