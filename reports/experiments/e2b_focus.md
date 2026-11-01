# E2b bulk/item split vs combined (focus set, tuning origins)

Reference for the bootstrap: `ma4-focus-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-focus-r3 | ma4 | focus | 0.720 | 0.735 | 2.741 | 0.3% | 0.390 | 0.372 | 88.2% | 97.2% |
| tsb-a0.2-b0.2-focus-r2 | tsb-a0.2-b0.2 | focus | 0.761 | 0.786 | 2.736 | -11.5% | 0.386 | 0.374 | 87.8% | 97.2% |
| split-ma4-bulk-0-focus-r1 | split-ma4-bulk-0 | focus | 0.629 | 0.637 | 2.732 | 34.9% | 0.366 | 0.339 | 87.9% | 97.4% |
| split-ma4-bulk-ma52-focus-r2 | split-ma4-bulk-ma52 | focus | 0.732 | 0.737 | 2.728 | -12.8% | 0.364 | 0.340 | 89.7% | 97.8% |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-r1 | split-ma4-bulk-tsb-a0.1-b0.1 | focus | 0.791 | 0.768 | 2.741 | -17.5% | 0.388 | 0.352 | 90.1% | 97.9% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r2 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 0.786 | 0.798 | 2.731 | -20.4% | 0.372 | 0.353 | 88.9% | 97.7% |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1 | focus | 0.846 | 0.829 | 2.745 | -25.2% | 0.395 | 0.362 | 90.1% | 98.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| tsb-a0.2-b0.2-focus-r2 | +0.041 [+0.027, +0.054] * | +0.051 [+0.027, +0.078] * | -0.004 [-0.011, +0.002] |
| split-ma4-bulk-0-focus-r1 | -0.091 [-0.107, -0.078] * | -0.093 [-0.119, -0.070] * | -0.024 [-0.033, -0.016] * |
| split-ma4-bulk-ma52-focus-r2 | +0.012 [-0.004, +0.026] | +0.004 [-0.021, +0.030] | -0.025 [-0.034, -0.018] * |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-r1 | +0.071 [+0.040, +0.109] * | +0.032 [+0.006, +0.062] * | -0.002 [-0.019, +0.024] |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r2 | +0.066 [+0.045, +0.085] * | +0.064 [+0.030, +0.101] * | -0.018 [-0.027, -0.009] * |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-r1 | +0.125 [+0.090, +0.166] * | +0.092 [+0.057, +0.133] * | +0.005 [-0.013, +0.031] |

## MASE per segment

| segment | series | ma4-focus-r3 | tsb-a0.2-b0.2-focus-r2 | split-ma4-bulk-0-focus-r1 | split-ma4-bulk-ma52-focus-r2 | split-ma4-bulk-tsb-a0.1-b0.1-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r2 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-r1 |
|---|---|---|---|---|---|---|---|---|
| A-erratic | 373 | 0.681 | 0.719 | 0.582 | 0.699 | 0.740 | 0.751 | 0.792 |
| A-intermittent | 16 | 0.922 | 0.845 | 0.771 | 0.866 | 0.952 | 0.856 | 0.951 |
| A-lumpy | 66 | 0.950 | 1.251 | 0.839 | 1.064 | 1.467 | 1.301 | 1.701 |
| A-smooth | 293 | 0.708 | 0.699 | 0.634 | 0.691 | 0.696 | 0.711 | 0.715 |
