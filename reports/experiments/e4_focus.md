# E4 global LightGBM (focus set, tuning origins)

Reference for the bootstrap: `split-ma4-bulk-ma52-focus-r5`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-focus-r5 | split-ma4-bulk-ma52 | focus | 0.732 | 0.737 | 2.728 | -12.8% | 0.364 | 0.340 | 89.7% | 97.8% |
| lgbm-item-bulk-ma52-focus-r1 | lgbm-item-bulk-ma52 | focus | 0.730 | 0.736 | 2.724 | -12.6% | 0.353 | 0.333 | 85.4% | 96.2% |
| lgbm-total-focus-r1 | lgbm-total | focus | 0.692 | 0.685 | 2.727 | 2.1% | 0.357 | 0.338 | 85.0% | 96.3% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 0.786 | 0.798 | 2.731 | -20.4% | 0.372 | 0.353 | 88.9% | 97.7% |
| ets-bulk-ma52-r10-focus-r1 | ets-bulk-ma52-r10 | focus | 0.769 | 0.768 | 2.732 | -20.0% | 0.370 | 0.343 | 86.4% | 96.9% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| lgbm-item-bulk-ma52-focus-r1 | -0.002 [-0.008, +0.003] | -0.001 [-0.007, +0.007] | -0.011 [-0.016, -0.006] * |
| lgbm-total-focus-r1 | -0.040 [-0.051, -0.030] * | -0.052 [-0.073, -0.034] * | -0.007 [-0.012, -0.002] * |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | +0.054 [+0.045, +0.063] * | +0.060 [+0.046, +0.076] * | +0.008 [+0.004, +0.011] * |
| ets-bulk-ma52-r10-focus-r1 | +0.037 [+0.031, +0.043] * | +0.030 [+0.022, +0.038] * | +0.005 [+0.002, +0.009] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-focus-r5 | lgbm-item-bulk-ma52-focus-r1 | lgbm-total-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | ets-bulk-ma52-r10-focus-r1 |
|---|---|---|---|---|---|---|
| A-erratic | 373 | 0.699 | 0.700 | 0.666 | 0.751 | 0.741 |
| A-intermittent | 16 | 0.866 | 0.860 | 0.821 | 0.856 | 0.896 |
| A-lumpy | 66 | 1.064 | 1.046 | 0.874 | 1.301 | 1.071 |
| A-smooth | 293 | 0.691 | 0.689 | 0.676 | 0.711 | 0.729 |

## MASE / CRPS per product category

| category | series | split-ma4-bulk-ma52-focus-r5 | lgbm-item-bulk-ma52-focus-r1 | lgbm-total-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r3 | ets-bulk-ma52-r10-focus-r1 |
|---|---|---|---|---|---|---|
| kitchen_tableware | 169 | 0.693 / 0.330 | 0.691 / 0.317 | 0.681 / 0.321 | 0.708 / 0.323 | 0.730 / 0.331 |
| bags | 67 | 0.693 / 0.323 | 0.706 / 0.334 | 0.685 / 0.340 | 0.721 / 0.328 | 0.734 / 0.338 |
| stationery_craft | 66 | 0.688 / 0.303 | 0.688 / 0.290 | 0.657 / 0.303 | 0.736 / 0.306 | 0.737 / 0.317 |
| candles_lights | 64 | 0.615 / 0.272 | 0.614 / 0.259 | 0.568 / 0.263 | 0.682 / 0.283 | 0.672 / 0.292 |
| wall_decor | 61 | 0.656 / 0.296 | 0.668 / 0.293 | 0.637 / 0.297 | 0.686 / 0.297 | 0.694 / 0.295 |
| party_giftwrap | 55 | 0.745 / 0.351 | 0.747 / 0.356 | 0.755 / 0.365 | 0.769 / 0.356 | 0.771 / 0.352 |
| storage | 43 | 0.798 / 0.373 | 0.795 / 0.379 | 0.751 / 0.386 | 0.838 / 0.374 | 0.842 / 0.379 |
| toys_games | 43 | 0.653 / 0.333 | 0.665 / 0.321 | 0.628 / 0.322 | 0.710 / 0.338 | 0.720 / 0.345 |
| textiles_cushions | 38 | 0.756 / 0.401 | 0.735 / 0.349 | 0.624 / 0.347 | 0.940 / 0.460 | 0.741 / 0.389 |
| garden_outdoor | 34 | 0.783 / 0.439 | 0.781 / 0.446 | 0.763 / 0.441 | 0.796 / 0.438 | 0.820 / 0.438 |
| decorations | 33 | 0.620 / 0.268 | 0.629 / 0.242 | 0.545 / 0.240 | 0.737 / 0.289 | 0.656 / 0.290 |
| accessories | 20 | 0.559 / 0.273 | 0.567 / 0.253 | 0.529 / 0.260 | 0.621 / 0.283 | 0.622 / 0.268 |
| christmas | 17 | 0.864 / 0.438 | 0.824 / 0.399 | 0.561 / 0.392 | 1.257 / 0.548 | 0.816 / 0.424 |
| furniture | 16 | 0.739 / 0.347 | 0.718 / 0.332 | 0.655 / 0.334 | 0.737 / 0.337 | 0.751 / 0.339 |
| easter | 11 | 1.123 / 0.527 | 0.940 / 0.462 | 0.948 / 0.476 | 1.232 / 0.547 | 1.090 / 0.494 |
| bath_beauty | 9 | 0.833 / 0.343 | 0.847 / 0.306 | 0.724 / 0.298 | 0.913 / 0.341 | 0.935 / 0.382 |
| other | 2 | 11.201 / 11.880 | 11.193 / 11.843 | 11.016 / 11.837 | 11.241 / 11.873 | 11.190 / 11.941 |
