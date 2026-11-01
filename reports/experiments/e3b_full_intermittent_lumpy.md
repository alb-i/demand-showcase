# E3b bulk threshold 10x vs 20x (full set, tuning origins, intermittent + lumpy)

> Record of the 20x vs 10x comparison; run before 10x became the only threshold: segments and the "products with bulk lines" here are still the 20x ones.

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r1 | split-ma4-bulk-ma52 | full | 0.753 | 0.664 | 1.972 | -76.4% | 0.499 | 0.347 | 88.4% | 96.7% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.795 | 0.844 | 1.962 | -107.0% | 0.470 | 0.366 | 89.7% | 97.4% |
| ets-bulk-ma52-full-r1 | ets-bulk-ma52 | full | 0.854 | 0.704 | 1.997 | -98.2% | 0.555 | 0.387 | 93.1% | 96.2% |
| arima-bulk-ma52-full-r1 | arima-bulk-ma52 | full | 0.856 | 0.755 | 1.998 | -102.8% | 0.555 | 0.391 | 93.7% | 96.5% |
| split-ma4-bulk-ma52-r10-full-r1 | split-ma4-bulk-ma52-r10 | full | 0.767 | 0.731 | 1.969 | -89.0% | 0.490 | 0.346 | 88.9% | 96.8% |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10 | full | 0.810 | 0.887 | 1.963 | -115.6% | 0.468 | 0.366 | 90.2% | 97.5% |
| ets-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10 | full | 0.852 | 0.757 | 1.988 | -104.4% | 0.537 | 0.379 | 92.6% | 96.3% |
| arima-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10 | full | 0.855 | 0.805 | 1.985 | -108.6% | 0.536 | 0.381 | 93.1% | 96.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-full-r1 | +0.043 [+0.037, +0.050] * | +0.179 [+0.135, +0.232] * | -0.029 [-0.033, -0.025] * |
| ets-bulk-ma52-full-r1 | +0.100 [+0.090, +0.110] * | +0.039 [+0.018, +0.059] * | +0.056 [+0.049, +0.063] * |
| arima-bulk-ma52-full-r1 | +0.102 [+0.090, +0.114] * | +0.090 [+0.066, +0.119] * | +0.056 [+0.045, +0.070] * |
| split-ma4-bulk-ma52-r10-full-r1 | +0.014 [+0.010, +0.018] * | +0.066 [+0.046, +0.090] * | -0.009 [-0.011, -0.007] * |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-full-r1 | +0.057 [+0.049, +0.065] * | +0.221 [+0.171, +0.280] * | -0.031 [-0.035, -0.026] * |
| ets-bulk-ma52-r10-full-r1 | +0.099 [+0.090, +0.108] * | +0.091 [+0.075, +0.108] * | +0.037 [+0.031, +0.044] * |
| arima-bulk-ma52-r10-full-r1 | +0.102 [+0.090, +0.113] * | +0.139 [+0.112, +0.171] * | +0.037 [+0.027, +0.050] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-full-r1 | ets-bulk-ma52-full-r1 | arima-bulk-ma52-full-r1 | split-ma4-bulk-ma52-r10-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10-full-r1 |
|---|---|---|---|---|---|---|---|---|---|
| A-intermittent | 20 | 0.858 | 0.889 | 0.871 | 0.873 | 0.879 | 0.912 | 0.891 | 0.888 |
| A-lumpy | 119 | 0.720 | 0.956 | 0.738 | 0.825 | 0.803 | 1.010 | 0.812 | 0.873 |
| B-intermittent | 31 | 0.581 | 0.615 | 0.625 | 0.646 | 0.583 | 0.618 | 0.631 | 0.649 |
| B-lumpy | 548 | 0.747 | 0.813 | 0.833 | 0.856 | 0.768 | 0.835 | 0.826 | 0.857 |
| C-intermittent | 525 | 0.688 | 0.722 | 0.803 | 0.792 | 0.689 | 0.723 | 0.804 | 0.793 |
| C-lumpy | 1252 | 0.787 | 0.806 | 0.900 | 0.890 | 0.798 | 0.818 | 0.892 | 0.883 |
