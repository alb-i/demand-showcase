# E3c pooling by category and top-down (focus set, tuning origins)

Reference for the bootstrap: `split-ma4-bulk-ma52-focus-r4`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-focus-r4 | split-ma4-bulk-ma52 | focus | 0.732 | 0.737 | 2.728 | -12.8% | 0.364 | 0.340 | 89.7% | 97.8% |
| split-ma4-bulk-ma52-poolcat-focus-r1 | split-ma4-bulk-ma52-poolcat | focus | 0.732 | 0.737 | 2.728 | -12.8% | 0.367 | 0.342 | 89.1% | 97.6% |
| topdown-ma4-bulk-ma52-focus-r1 | topdown-ma4-bulk-ma52 | focus | 0.821 | 0.819 | 2.735 | -21.7% | 0.375 | 0.353 | 90.2% | 98.1% |
| topdown-ma13-bulk-ma52-focus-r1 | topdown-ma13-bulk-ma52 | focus | 0.885 | 0.894 | 2.742 | -31.1% | 0.393 | 0.378 | 87.2% | 97.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-ma4-bulk-ma52-poolcat-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.003 [-0.000, +0.006] |
| topdown-ma4-bulk-ma52-focus-r1 | +0.089 [+0.074, +0.104] * | +0.084 [+0.065, +0.102] * | +0.011 [+0.005, +0.016] * |
| topdown-ma13-bulk-ma52-focus-r1 | +0.153 [+0.134, +0.171] * | +0.155 [+0.131, +0.180] * | +0.029 [+0.022, +0.035] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-focus-r4 | split-ma4-bulk-ma52-poolcat-focus-r1 | topdown-ma4-bulk-ma52-focus-r1 | topdown-ma13-bulk-ma52-focus-r1 |
|---|---|---|---|---|---|
| A-erratic | 373 | 0.699 | 0.699 | 0.783 | 0.841 |
| A-intermittent | 16 | 0.866 | 0.866 | 0.960 | 0.943 |
| A-lumpy | 66 | 1.064 | 1.064 | 1.279 | 1.468 |
| A-smooth | 293 | 0.691 | 0.691 | 0.758 | 0.806 |

## MASE / CRPS per product category

| category | series | split-ma4-bulk-ma52-focus-r4 | split-ma4-bulk-ma52-poolcat-focus-r1 | topdown-ma4-bulk-ma52-focus-r1 | topdown-ma13-bulk-ma52-focus-r1 |
|---|---|---|---|---|---|
| kitchen_tableware | 169 | 0.693 / 0.330 | 0.693 / 0.328 | 0.796 / 0.333 | 0.812 / 0.336 |
| bags | 67 | 0.693 / 0.323 | 0.693 / 0.322 | 0.785 / 0.336 | 0.775 / 0.336 |
| stationery_craft | 66 | 0.688 / 0.303 | 0.688 / 0.307 | 0.729 / 0.304 | 0.809 / 0.325 |
| candles_lights | 64 | 0.615 / 0.272 | 0.615 / 0.270 | 0.699 / 0.289 | 0.762 / 0.303 |
| wall_decor | 61 | 0.656 / 0.296 | 0.656 / 0.291 | 0.785 / 0.320 | 0.829 / 0.331 |
| party_giftwrap | 55 | 0.745 / 0.351 | 0.745 / 0.352 | 0.825 / 0.360 | 0.849 / 0.365 |
| storage | 43 | 0.798 / 0.373 | 0.798 / 0.384 | 0.855 / 0.375 | 0.919 / 0.391 |
| toys_games | 43 | 0.653 / 0.333 | 0.653 / 0.335 | 0.677 / 0.337 | 0.782 / 0.357 |
| textiles_cushions | 38 | 0.756 / 0.401 | 0.756 / 0.399 | 0.874 / 0.405 | 1.082 / 0.478 |
| garden_outdoor | 34 | 0.783 / 0.439 | 0.783 / 0.446 | 0.876 / 0.455 | 0.894 / 0.462 |
| decorations | 33 | 0.620 / 0.268 | 0.620 / 0.279 | 0.762 / 0.293 | 0.876 / 0.321 |
| accessories | 20 | 0.559 / 0.273 | 0.559 / 0.251 | 0.584 / 0.283 | 0.750 / 0.325 |
| christmas | 17 | 0.864 / 0.438 | 0.864 / 0.466 | 0.917 / 0.450 | 1.420 / 0.650 |
| furniture | 16 | 0.739 / 0.347 | 0.739 / 0.349 | 0.832 / 0.353 | 0.858 / 0.357 |
| easter | 11 | 1.123 / 0.527 | 1.123 / 0.597 | 1.373 / 0.632 | 1.458 / 0.628 |
| bath_beauty | 9 | 0.833 / 0.343 | 0.833 / 0.412 | 0.941 / 0.341 | 0.956 / 0.340 |
| other | 2 | 11.201 / 11.880 | 11.201 / 11.933 | 11.236 / 11.876 | 11.275 / 11.875 |
