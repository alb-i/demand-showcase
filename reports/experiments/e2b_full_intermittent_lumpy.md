# E2b bulk/item split vs combined (full set, tuning origins, intermittent + lumpy)

Reference for the bootstrap: `ma4-full-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-full-r3 | ma4 | full | 0.718 | 0.545 | 1.969 | -11.3% | 0.510 | 0.355 | 87.6% | 96.7% |
| tsb-a0.2-b0.2-full-r2 | tsb-a0.2-b0.2 | full | 0.763 | 0.755 | 1.955 | -59.1% | 0.474 | 0.372 | 88.9% | 97.2% |
| split-ma4-bulk-0-full-r1 | split-ma4-bulk-0 | full | 0.657 | 0.462 | 1.960 | 26.1% | 0.494 | 0.337 | 87.2% | 96.5% |
| split-ma4-bulk-ma52-full-r2 | split-ma4-bulk-ma52 | full | 0.765 | 0.732 | 1.961 | -87.4% | 0.489 | 0.347 | 88.8% | 96.8% |
| split-ma4-bulk-tsb-a0.1-b0.1-full-r1 | split-ma4-bulk-tsb-a0.1-b0.1 | full | 0.957 | 0.911 | 2.015 | -144.2% | 0.548 | 0.405 | 89.6% | 97.3% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r2 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.807 | 0.886 | 1.954 | -113.5% | 0.466 | 0.366 | 90.2% | 97.5% |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-full-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1 | full | 0.998 | 1.066 | 2.007 | -170.2% | 0.536 | 0.426 | 90.3% | 97.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| tsb-a0.2-b0.2-full-r2 | +0.046 [+0.037, +0.054] * | +0.211 [+0.152, +0.277] * | -0.036 [-0.041, -0.031] * |
| split-ma4-bulk-0-full-r1 | -0.061 [-0.069, -0.053] * | -0.077 [-0.101, -0.058] * | -0.016 [-0.020, -0.011] * |
| split-ma4-bulk-ma52-full-r2 | +0.047 [+0.038, +0.056] * | +0.185 [+0.132, +0.238] * | -0.021 [-0.026, -0.017] * |
| split-ma4-bulk-tsb-a0.1-b0.1-full-r1 | +0.238 [+0.209, +0.266] * | +0.355 [+0.289, +0.421] * | +0.038 [+0.023, +0.053] * |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r2 | +0.090 [+0.078, +0.101] * | +0.339 [+0.260, +0.420] * | -0.044 [-0.050, -0.037] * |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-full-r1 | +0.280 [+0.249, +0.309] * | +0.507 [+0.425, +0.597] * | +0.026 [+0.010, +0.041] * |

## MASE per segment

| segment | series | ma4-full-r3 | tsb-a0.2-b0.2-full-r2 | split-ma4-bulk-0-full-r1 | split-ma4-bulk-ma52-full-r2 | split-ma4-bulk-tsb-a0.1-b0.1-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-full-r2 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-full-r1 |
|---|---|---|---|---|---|---|---|---|
| A-intermittent | 26 | 0.681 | 0.717 | 0.584 | 0.795 | 0.859 | 0.829 | 0.895 |
| A-lumpy | 114 | 0.624 | 0.900 | 0.554 | 0.814 | 1.049 | 1.029 | 1.262 |
| B-intermittent | 61 | 0.513 | 0.543 | 0.465 | 0.584 | 0.676 | 0.615 | 0.706 |
| B-lumpy | 530 | 0.716 | 0.785 | 0.631 | 0.783 | 1.005 | 0.851 | 1.071 |
| C-intermittent | 605 | 0.729 | 0.768 | 0.710 | 0.760 | 0.838 | 0.792 | 0.870 |
| C-lumpy | 1188 | 0.734 | 0.751 | 0.663 | 0.763 | 1.002 | 0.784 | 1.021 |
