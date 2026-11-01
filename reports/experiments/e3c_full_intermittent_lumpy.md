# E3c pooling by category and top-down (full set, tuning origins, intermittent + lumpy)

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r4`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r4 | split-ma4-bulk-ma52 | full | 0.765 | 0.732 | 1.961 | -87.4% | 0.489 | 0.347 | 88.8% | 96.8% |
| split-ma4-bulk-ma52-poolcat-full-r1 | split-ma4-bulk-ma52-poolcat | full | 0.765 | 0.732 | 1.961 | -87.4% | 0.496 | 0.354 | 88.4% | 96.1% |
| topdown-ma4-bulk-ma52-full-r1 | topdown-ma4-bulk-ma52 | full | 0.808 | 0.841 | 1.955 | -90.6% | 0.453 | 0.345 | 92.5% | 97.9% |
| topdown-ma13-bulk-ma52-full-r1 | topdown-ma13-bulk-ma52 | full | 0.879 | 0.994 | 1.962 | -121.9% | 0.466 | 0.392 | 91.9% | 97.8% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-ma4-bulk-ma52-poolcat-full-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.007 [+0.006, +0.009] * |
| topdown-ma4-bulk-ma52-full-r1 | +0.040 [+0.028, +0.051] * | +0.106 [+0.080, +0.135] * | -0.036 [-0.041, -0.030] * |
| topdown-ma13-bulk-ma52-full-r1 | +0.111 [+0.098, +0.123] * | +0.253 [+0.212, +0.292] * | -0.023 [-0.029, -0.017] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r4 | split-ma4-bulk-ma52-poolcat-full-r1 | topdown-ma4-bulk-ma52-full-r1 | topdown-ma13-bulk-ma52-full-r1 |
|---|---|---|---|---|---|
| A-intermittent | 26 | 0.795 | 0.795 | 0.904 | 0.935 |
| A-lumpy | 114 | 0.814 | 0.814 | 1.003 | 1.189 |
| B-intermittent | 61 | 0.584 | 0.584 | 0.706 | 0.749 |
| B-lumpy | 530 | 0.783 | 0.783 | 0.828 | 0.920 |
| C-intermittent | 605 | 0.760 | 0.760 | 0.801 | 0.859 |
| C-lumpy | 1188 | 0.763 | 0.763 | 0.786 | 0.846 |
