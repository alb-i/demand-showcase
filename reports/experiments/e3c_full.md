# E3c pooling by category and top-down (full set, tuning origins)

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r4`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r4 | split-ma4-bulk-ma52 | full | 0.699 | 0.720 | 1.647 | -24.3% | 0.414 | 0.333 | 89.3% | 97.0% |
| split-ma4-bulk-ma52-poolcat-full-r1 | split-ma4-bulk-ma52-poolcat | full | 0.699 | 0.720 | 1.647 | -24.3% | 0.421 | 0.333 | 88.7% | 96.9% |
| topdown-ma4-bulk-ma52-full-r1 | topdown-ma4-bulk-ma52 | full | 0.758 | 0.802 | 1.654 | -23.1% | 0.399 | 0.345 | 91.9% | 97.8% |
| topdown-ma13-bulk-ma52-full-r1 | topdown-ma13-bulk-ma52 | full | 0.817 | 0.879 | 1.661 | -34.8% | 0.409 | 0.367 | 91.0% | 97.7% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-ma4-bulk-ma52-poolcat-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.006 [+0.004, +0.007] * |
| topdown-ma4-bulk-ma52-full-r1 | +0.055 [+0.046, +0.065] * | +0.083 [+0.069, +0.097] * | -0.010 [-0.015, -0.004] * |
| topdown-ma13-bulk-ma52-full-r1 | +0.113 [+0.103, +0.123] * | +0.155 [+0.135, +0.173] * | +0.001 [-0.004, +0.006] |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r4 | split-ma4-bulk-ma52-poolcat-full-r1 | topdown-ma4-bulk-ma52-full-r1 | topdown-ma13-bulk-ma52-full-r1 |
|---|---|---|---|---|---|
| A-erratic | 448 | 0.675 | 0.675 | 0.763 | 0.819 |
| A-intermittent | 26 | 0.795 | 0.795 | 0.904 | 0.935 |
| A-lumpy | 114 | 0.814 | 0.814 | 1.003 | 1.189 |
| A-smooth | 364 | 0.695 | 0.695 | 0.773 | 0.812 |
| B-erratic | 434 | 0.662 | 0.662 | 0.704 | 0.740 |
| B-intermittent | 61 | 0.584 | 0.584 | 0.706 | 0.749 |
| B-lumpy | 530 | 0.783 | 0.783 | 0.828 | 0.920 |
| B-smooth | 120 | 0.725 | 0.725 | 0.916 | 0.953 |
| C-erratic | 122 | 0.362 | 0.362 | 0.480 | 0.517 |
| C-intermittent | 605 | 0.760 | 0.760 | 0.801 | 0.859 |
| C-lumpy | 1188 | 0.763 | 0.763 | 0.786 | 0.846 |
| C-smooth | 132 | 0.335 | 0.335 | 0.438 | 0.454 |
| unclassified | 140 | 0.175 | 0.175 | 0.274 | 0.308 |

## MASE / CRPS per product category

| category | series | split-ma4-bulk-ma52-full-r4 | split-ma4-bulk-ma52-poolcat-full-r1 | topdown-ma4-bulk-ma52-full-r1 | topdown-ma13-bulk-ma52-full-r1 |
|---|---|---|---|---|---|
| kitchen_tableware | 645 | 0.969 / 0.613 | 0.969 / 0.626 | 1.028 / 0.588 | 1.042 / 0.589 |
| candles_lights | 512 | 0.512 / 0.285 | 0.512 / 0.284 | 0.572 / 0.269 | 0.609 / 0.274 |
| jewellery | 403 | 0.640 / 0.385 | 0.640 / 0.400 | 0.619 / 0.321 | 0.695 / 0.325 |
| stationery_craft | 392 | 0.652 / 0.352 | 0.652 / 0.353 | 0.692 / 0.343 | 0.746 / 0.350 |
| wall_decor | 323 | 0.565 / 0.320 | 0.565 / 0.318 | 0.657 / 0.316 | 0.686 / 0.320 |
| decorations | 246 | 0.653 / 0.354 | 0.653 / 0.361 | 0.715 / 0.337 | 0.782 / 0.345 |
| christmas | 219 | 0.390 / 0.208 | 0.390 / 0.264 | 0.454 / 0.208 | 0.798 / 0.313 |
| bags | 217 | 0.851 / 0.573 | 0.851 / 0.573 | 0.971 / 0.586 | 0.961 / 0.585 |
| textiles_cushions | 209 | 0.772 / 0.497 | 0.772 / 0.492 | 0.820 / 0.472 | 0.931 / 0.493 |
| party_giftwrap | 207 | 0.759 / 0.391 | 0.759 / 0.399 | 0.803 / 0.379 | 0.819 / 0.380 |
| garden_outdoor | 170 | 0.791 / 0.475 | 0.791 / 0.461 | 0.898 / 0.503 | 0.907 / 0.506 |
| storage | 169 | 0.693 / 0.395 | 0.693 / 0.401 | 0.773 / 0.400 | 0.826 / 0.407 |
| toys_games | 155 | 0.573 / 0.296 | 0.573 / 0.299 | 0.599 / 0.283 | 0.682 / 0.294 |
| accessories | 153 | 0.568 / 0.292 | 0.568 / 0.289 | 0.563 / 0.281 | 0.668 / 0.294 |
| furniture | 105 | 0.698 / 0.515 | 0.698 / 0.522 | 0.939 / 0.537 | 0.972 / 0.543 |
| easter | 92 | 1.120 / 0.624 | 1.120 / 0.660 | 1.223 / 0.601 | 1.255 / 0.613 |
| bath_beauty | 46 | 0.692 / 0.334 | 0.692 / 0.359 | 0.791 / 0.317 | 0.807 / 0.317 |
| other | 20 | 1.545 / 1.482 | 1.545 / 1.501 | 1.491 / 1.475 | 1.522 / 1.476 |
| non_product | 1 | - / - | - / - | - / - | - / - |
