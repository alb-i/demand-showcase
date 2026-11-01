# E2b bulk/item split vs combined (focus set, tuning origins, intermittent + lumpy)

Reference for the bootstrap: `ma4-focus-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-focus-r3 | ma4 | focus | 0.944 | 0.621 | 7.876 | -15.4% | 0.695 | 0.401 | 89.7% | 97.8% |
| tsb-a0.2-b0.2-focus-r2 | tsb-a0.2-b0.2 | focus | 1.172 | 1.001 | 7.879 | -54.8% | 0.727 | 0.487 | 87.8% | 98.1% |
| split-ma4-bulk-0-focus-r1 | split-ma4-bulk-0 | focus | 0.826 | 0.491 | 7.872 | 43.9% | 0.662 | 0.361 | 88.9% | 98.3% |
| split-ma4-bulk-ma52-focus-r2 | split-ma4-bulk-ma52 | focus | 1.025 | 0.843 | 7.873 | -42.1% | 0.665 | 0.393 | 90.7% | 98.5% |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-r1 | split-ma4-bulk-tsb-a0.1-b0.1 | focus | 1.367 | 1.075 | 7.891 | -123.0% | 0.810 | 0.477 | 90.2% | 98.1% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r2 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 1.214 | 1.102 | 7.877 | -66.2% | 0.708 | 0.462 | 89.1% | 98.4% |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1 | focus | 1.555 | 1.334 | 7.898 | -147.1% | 0.852 | 0.538 | 89.4% | 98.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| tsb-a0.2-b0.2-focus-r2 | +0.227 [+0.146, +0.310] * | +0.380 [+0.192, +0.554] * | +0.032 [-0.006, +0.066] |
| split-ma4-bulk-0-focus-r1 | -0.118 [-0.196, -0.054] * | -0.122 [-0.207, -0.061] * | -0.033 [-0.079, +0.002] |
| split-ma4-bulk-ma52-focus-r2 | +0.081 [+0.007, +0.149] * | +0.225 [+0.050, +0.375] * | -0.030 [-0.073, +0.003] |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-r1 | +0.422 [+0.206, +0.746] * | +0.429 [+0.223, +0.629] * | +0.115 [-0.009, +0.329] |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-r2 | +0.270 [+0.160, +0.376] * | +0.483 [+0.241, +0.700] * | +0.013 [-0.034, +0.052] |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-r1 | +0.611 [+0.371, +0.947] * | +0.687 [+0.420, +0.954] * | +0.157 [+0.028, +0.373] * |

## MASE per segment

| segment | series | ma4-focus-r3 | tsb-a0.2-b0.2-focus-r2 | split-ma4-bulk-0-focus-r1 | split-ma4-bulk-ma52-focus-r2 | split-ma4-bulk-tsb-a0.1-b0.1-focus-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-r2 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-r1 |
|---|---|---|---|---|---|---|---|---|
| A-intermittent | 16 | 0.922 | 0.845 | 0.771 | 0.866 | 0.952 | 0.856 | 0.951 |
| A-lumpy | 66 | 0.950 | 1.251 | 0.839 | 1.064 | 1.467 | 1.301 | 1.701 |
