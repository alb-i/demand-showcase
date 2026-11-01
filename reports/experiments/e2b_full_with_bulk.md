# E2b bulk/item split vs combined (full set, tuning origins, products with bulk lines)

Reference for the bootstrap: `ma4-full-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only products with bulk lines (> 10x median) before 2011-06-06.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-full-r3 | ma4 | full | 0.710 | 0.692 | 1.886 | -2.8% | 0.453 | 0.361 | 87.5% | 96.5% |
| tsb-a0.2-b0.2-full-r2 | tsb-a0.2-b0.2 | full | 0.740 | 0.751 | 1.872 | -18.3% | 0.426 | 0.359 | 88.2% | 97.0% |
| split-ma4-bulk-0-full-r1 | split-ma4-bulk-0 | full | 0.611 | 0.595 | 1.870 | 32.1% | 0.421 | 0.332 | 88.1% | 96.8% |
| split-ma4-bulk-ma52-full-r2 | split-ma4-bulk-ma52 | full | 0.762 | 0.726 | 1.870 | -25.8% | 0.423 | 0.334 | 89.8% | 97.2% |
| split-ma4-bulk-tsb-a0.1-b0.1-full-r1 | split-ma4-bulk-tsb-a0.1-b0.1 | full | 0.977 | 0.794 | 1.939 | -43.5% | 0.500 | 0.357 | 88.8% | 97.1% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r2 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.799 | 0.791 | 1.869 | -35.0% | 0.415 | 0.343 | 90.0% | 97.5% |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-full-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1 | full | 1.015 | 0.860 | 1.937 | -52.8% | 0.496 | 0.365 | 89.0% | 97.2% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| tsb-a0.2-b0.2-full-r2 | +0.030 [+0.023, +0.037] * | +0.059 [+0.040, +0.079] * | -0.027 [-0.031, -0.023] * |
| split-ma4-bulk-0-full-r1 | -0.101 [-0.109, -0.092] * | -0.093 [-0.112, -0.075] * | -0.033 [-0.038, -0.028] * |
| split-ma4-bulk-ma52-full-r2 | +0.051 [+0.042, +0.060] * | +0.035 [+0.016, +0.056] * | -0.030 [-0.035, -0.026] * |
| split-ma4-bulk-tsb-a0.1-b0.1-full-r1 | +0.270 [+0.244, +0.298] * | +0.100 [+0.079, +0.127] * | +0.048 [+0.035, +0.063] * |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r2 | +0.087 [+0.076, +0.098] * | +0.098 [+0.072, +0.127] * | -0.038 [-0.044, -0.032] * |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-full-r1 | +0.306 [+0.279, +0.335] * | +0.165 [+0.137, +0.198] * | +0.044 [+0.030, +0.059] * |

## MASE per segment

| segment | series | ma4-full-r3 | tsb-a0.2-b0.2-full-r2 | split-ma4-bulk-0-full-r1 | split-ma4-bulk-ma52-full-r2 | split-ma4-bulk-tsb-a0.1-b0.1-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-full-r2 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-full-r1 |
|---|---|---|---|---|---|---|---|---|
| A-erratic | 430 | 0.649 | 0.690 | 0.550 | 0.680 | 0.745 | 0.735 | 0.803 |
| A-intermittent | 22 | 0.631 | 0.675 | 0.516 | 0.765 | 0.840 | 0.807 | 0.886 |
| A-lumpy | 101 | 0.654 | 0.938 | 0.575 | 0.869 | 1.134 | 1.084 | 1.348 |
| A-smooth | 353 | 0.702 | 0.693 | 0.627 | 0.693 | 0.723 | 0.710 | 0.742 |
| B-erratic | 370 | 0.652 | 0.645 | 0.559 | 0.669 | 0.780 | 0.685 | 0.800 |
| B-intermittent | 46 | 0.483 | 0.506 | 0.420 | 0.578 | 0.701 | 0.603 | 0.724 |
| B-lumpy | 446 | 0.751 | 0.815 | 0.650 | 0.830 | 1.094 | 0.894 | 1.155 |
| B-smooth | 80 | 0.702 | 0.692 | 0.605 | 0.749 | 0.911 | 0.753 | 0.918 |
| C-erratic | 69 | 0.502 | 0.485 | 0.442 | 0.510 | 0.637 | 0.511 | 0.638 |
| C-intermittent | 147 | 0.959 | 0.997 | 0.883 | 1.088 | 1.403 | 1.097 | 1.413 |
| C-lumpy | 636 | 0.769 | 0.781 | 0.638 | 0.824 | 1.268 | 0.842 | 1.284 |
| C-smooth | 41 | 0.425 | 0.421 | 0.384 | 0.484 | 0.567 | 0.490 | 0.575 |
| unclassified | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.083 | 0.000 | 0.083 |
