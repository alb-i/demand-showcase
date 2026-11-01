# E2b bulk/item split vs combined (focus set, tuning origins, products with bulk lines)

Reference for the bootstrap: `ma4-focus-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only products with bulk lines (> 10x median) before 2011-06-06.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-focus-r3 | ma4 | focus | 0.721 | 0.736 | 2.785 | 0.3% | 0.392 | 0.373 | 88.2% | 97.2% |
| tsb-a0.2-b0.2-focus-r2 | tsb-a0.2-b0.2 | focus | 0.761 | 0.786 | 2.779 | -11.4% | 0.388 | 0.375 | 87.8% | 97.2% |
| split-ma4-bulk-0-focus-r1 | split-ma4-bulk-0 | focus | 0.626 | 0.637 | 2.775 | 35.3% | 0.366 | 0.339 | 88.2% | 97.5% |
| split-ma4-bulk-ma52-focus-r2 | split-ma4-bulk-ma52 | focus | 0.733 | 0.738 | 2.771 | -13.0% | 0.366 | 0.341 | 89.8% | 97.8% |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-r1 | split-ma4-bulk-tsb-a0.1-b0.1 | focus | 0.794 | 0.769 | 2.785 | -17.8% | 0.390 | 0.352 | 90.2% | 97.9% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r2 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 0.787 | 0.798 | 2.774 | -20.4% | 0.373 | 0.353 | 89.0% | 97.7% |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1 | focus | 0.848 | 0.830 | 2.789 | -25.3% | 0.397 | 0.362 | 90.1% | 98.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| tsb-a0.2-b0.2-focus-r2 | +0.040 [+0.027, +0.054] * | +0.050 [+0.028, +0.078] * | -0.004 [-0.010, +0.002] |
| split-ma4-bulk-0-focus-r1 | -0.094 [-0.110, -0.081] * | -0.094 [-0.121, -0.071] * | -0.026 [-0.035, -0.018] * |
| split-ma4-bulk-ma52-focus-r2 | +0.012 [-0.004, +0.026] | +0.004 [-0.019, +0.030] | -0.026 [-0.035, -0.019] * |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-r1 | +0.074 [+0.043, +0.117] * | +0.032 [+0.007, +0.063] * | -0.002 [-0.020, +0.027] |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r2 | +0.066 [+0.046, +0.085] * | +0.064 [+0.032, +0.101] * | -0.019 [-0.028, -0.010] * |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-r1 | +0.128 [+0.092, +0.172] * | +0.092 [+0.059, +0.134] * | +0.005 [-0.013, +0.034] |

## MASE per segment

| segment | series | ma4-focus-r3 | tsb-a0.2-b0.2-focus-r2 | split-ma4-bulk-0-focus-r1 | split-ma4-bulk-ma52-focus-r2 | split-ma4-bulk-tsb-a0.1-b0.1-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r2 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-r1 |
|---|---|---|---|---|---|---|---|---|
| A-erratic | 361 | 0.679 | 0.718 | 0.577 | 0.699 | 0.741 | 0.751 | 0.794 |
| A-intermittent | 14 | 0.905 | 0.827 | 0.733 | 0.842 | 0.940 | 0.840 | 0.948 |
| A-lumpy | 60 | 0.988 | 1.296 | 0.866 | 1.114 | 1.557 | 1.351 | 1.791 |
| A-smooth | 288 | 0.708 | 0.699 | 0.633 | 0.691 | 0.696 | 0.711 | 0.715 |
