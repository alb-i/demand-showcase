# E3c pooling by category and top-down (focus set, tuning origins, intermittent + lumpy)

Reference for the bootstrap: `split-ma4-bulk-ma52-focus-r4`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-focus-r4 | split-ma4-bulk-ma52 | focus | 1.025 | 0.843 | 7.873 | -42.1% | 0.665 | 0.393 | 90.7% | 98.5% |
| split-ma4-bulk-ma52-poolcat-focus-r1 | split-ma4-bulk-ma52-poolcat | focus | 1.025 | 0.843 | 7.873 | -42.1% | 0.675 | 0.417 | 86.4% | 95.9% |
| topdown-ma4-bulk-ma52-focus-r1 | topdown-ma4-bulk-ma52 | focus | 1.217 | 1.012 | 7.880 | -51.1% | 0.694 | 0.408 | 92.3% | 98.8% |
| topdown-ma13-bulk-ma52-focus-r1 | topdown-ma13-bulk-ma52 | focus | 1.366 | 1.227 | 7.883 | -72.6% | 0.743 | 0.489 | 90.0% | 98.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-ma4-bulk-ma52-poolcat-focus-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.009 [-0.008, +0.030] |
| topdown-ma4-bulk-ma52-focus-r1 | +0.192 [+0.125, +0.262] * | +0.168 [+0.100, +0.260] * | +0.029 [+0.011, +0.046] * |
| topdown-ma13-bulk-ma52-focus-r1 | +0.340 [+0.252, +0.430] * | +0.381 [+0.264, +0.497] * | +0.078 [+0.053, +0.104] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-focus-r4 | split-ma4-bulk-ma52-poolcat-focus-r1 | topdown-ma4-bulk-ma52-focus-r1 | topdown-ma13-bulk-ma52-focus-r1 |
|---|---|---|---|---|---|
| A-intermittent | 16 | 0.866 | 0.866 | 0.960 | 0.943 |
| A-lumpy | 66 | 1.064 | 1.064 | 1.279 | 1.468 |
