# E2 intermittent methods (focus set, intermittent + lumpy, tuning origins)

Reference for the bootstrap: `ma4-focus-r2`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-focus-r2 | ma4 | focus | 0.944 | 0.621 | 7.876 | -15.4% | 0.695 | 0.401 | 89.7% | 97.8% |
| croston-a0.1-focus-r1 | croston-a0.1 | focus | 1.677 | 1.570 | 7.893 | -109.3% | 0.795 | 0.537 | 89.4% | 98.8% |
| croston-a0.2-focus-r1 | croston-a0.2 | focus | 1.580 | 1.339 | 7.897 | -88.0% | 0.812 | 0.527 | 86.3% | 97.5% |
| sba-a0.1-focus-r1 | sba-a0.1 | focus | 1.624 | 1.505 | 7.891 | -98.8% | 0.789 | 0.529 | 89.4% | 98.8% |
| sba-a0.2-focus-r1 | sba-a0.2 | focus | 1.483 | 1.231 | 7.892 | -69.2% | 0.799 | 0.512 | 86.3% | 97.6% |
| tsb-a0.1-b0.1-focus-r1 | tsb-a0.1-b0.1 | focus | 1.377 | 1.337 | 7.882 | -87.3% | 0.744 | 0.530 | 88.3% | 98.4% |
| tsb-a0.2-b0.2-focus-r1 | tsb-a0.2-b0.2 | focus | 1.172 | 1.001 | 7.879 | -54.8% | 0.727 | 0.487 | 87.8% | 98.1% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| croston-a0.1-focus-r1 | +0.732 [+0.509, +0.961] * | +0.950 [+0.614, +1.269] * | +0.100 [+0.027, +0.173] * |
| croston-a0.2-focus-r1 | +0.636 [+0.418, +0.870] * | +0.718 [+0.478, +0.955] * | +0.117 [+0.038, +0.210] * |
| sba-a0.1-focus-r1 | +0.680 [+0.467, +0.898] * | +0.885 [+0.565, +1.188] * | +0.094 [+0.023, +0.165] * |
| sba-a0.2-focus-r1 | +0.539 [+0.339, +0.750] * | +0.612 [+0.395, +0.827] * | +0.103 [+0.029, +0.189] * |
| tsb-a0.1-b0.1-focus-r1 | +0.432 [+0.293, +0.574] * | +0.717 [+0.398, +1.011] * | +0.049 [-0.003, +0.095] |
| tsb-a0.2-b0.2-focus-r1 | +0.227 [+0.146, +0.310] * | +0.380 [+0.192, +0.554] * | +0.032 [-0.006, +0.066] |

## MASE per segment

| segment | series | ma4-focus-r2 | croston-a0.1-focus-r1 | croston-a0.2-focus-r1 | sba-a0.1-focus-r1 | sba-a0.2-focus-r1 | tsb-a0.1-b0.1-focus-r1 | tsb-a0.2-b0.2-focus-r1 |
|---|---|---|---|---|---|---|---|---|
| A-intermittent | 16 | 0.922 | 0.986 | 1.008 | 0.970 | 0.969 | 0.869 | 0.845 |
| A-lumpy | 66 | 0.950 | 1.844 | 1.719 | 1.782 | 1.608 | 1.500 | 1.251 |
