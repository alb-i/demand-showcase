# E2 intermittent methods (focus set, tuning origins)

Reference for the bootstrap: `ma4-focus-r2`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-focus-r2 | ma4 | focus | 0.720 | 0.735 | 2.741 | 0.3% | 0.390 | 0.372 | 88.2% | 97.2% |
| croston-a0.1-focus-r1 | croston-a0.1 | focus | 0.887 | 0.895 | 2.744 | -26.4% | 0.398 | 0.382 | 87.3% | 97.5% |
| croston-a0.2-focus-r1 | croston-a0.2 | focus | 0.830 | 0.828 | 2.744 | -14.7% | 0.401 | 0.381 | 87.0% | 97.1% |
| sba-a0.1-focus-r1 | sba-a0.1 | focus | 0.858 | 0.863 | 2.741 | -20.0% | 0.396 | 0.379 | 87.2% | 97.5% |
| sba-a0.2-focus-r1 | sba-a0.2 | focus | 0.784 | 0.782 | 2.739 | -3.3% | 0.397 | 0.376 | 87.0% | 97.0% |
| tsb-a0.1-b0.1-focus-r1 | tsb-a0.1-b0.1 | focus | 0.834 | 0.864 | 2.738 | -23.9% | 0.387 | 0.377 | 87.8% | 97.6% |
| tsb-a0.2-b0.2-focus-r1 | tsb-a0.2-b0.2 | focus | 0.761 | 0.786 | 2.736 | -11.5% | 0.386 | 0.374 | 87.8% | 97.2% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| croston-a0.1-focus-r1 | +0.167 [+0.132, +0.202] * | +0.162 [+0.114, +0.214] * | +0.008 [-0.004, +0.020] |
| croston-a0.2-focus-r1 | +0.109 [+0.079, +0.142] * | +0.093 [+0.060, +0.128] * | +0.011 [+0.001, +0.023] * |
| sba-a0.1-focus-r1 | +0.138 [+0.104, +0.172] * | +0.130 [+0.085, +0.180] * | +0.007 [-0.005, +0.018] |
| sba-a0.2-focus-r1 | +0.064 [+0.036, +0.093] * | +0.048 [+0.019, +0.080] * | +0.007 [-0.003, +0.019] |
| tsb-a0.1-b0.1-focus-r1 | +0.113 [+0.090, +0.137] * | +0.130 [+0.088, +0.177] * | -0.003 [-0.012, +0.006] |
| tsb-a0.2-b0.2-focus-r1 | +0.041 [+0.027, +0.054] * | +0.051 [+0.027, +0.078] * | -0.004 [-0.011, +0.002] |

## MASE per segment

| segment | series | ma4-focus-r2 | croston-a0.1-focus-r1 | croston-a0.2-focus-r1 | sba-a0.1-focus-r1 | sba-a0.2-focus-r1 | tsb-a0.1-b0.1-focus-r1 | tsb-a0.2-b0.2-focus-r1 |
|---|---|---|---|---|---|---|---|---|
| A-erratic | 373 | 0.681 | 0.815 | 0.747 | 0.788 | 0.706 | 0.791 | 0.719 |
| A-intermittent | 16 | 0.922 | 0.986 | 1.008 | 0.970 | 0.969 | 0.869 | 0.845 |
| A-lumpy | 66 | 0.950 | 1.844 | 1.719 | 1.782 | 1.608 | 1.500 | 1.251 |
| A-smooth | 293 | 0.708 | 0.757 | 0.724 | 0.733 | 0.689 | 0.735 | 0.699 |
