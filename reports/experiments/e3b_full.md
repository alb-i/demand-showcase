# E3b bulk threshold 10x vs 20x (full set, tuning origins)

> Record of the 20x vs 10x comparison; run before 10x became the only threshold: segments and the "products with bulk lines" here are still the 20x ones.

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r1 | split-ma4-bulk-ma52 | full | 0.688 | 0.702 | 1.650 | -19.9% | 0.421 | 0.338 | 88.8% | 96.8% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.724 | 0.769 | 1.641 | -30.5% | 0.402 | 0.345 | 89.7% | 97.3% |
| ets-bulk-ma52-full-r1 | ets-bulk-ma52 | full | 0.767 | 0.743 | 1.674 | -30.9% | 0.506 | 0.356 | 91.8% | 96.3% |
| arima-bulk-ma52-full-r1 | arima-bulk-ma52 | full | 0.779 | 0.786 | 1.673 | -37.9% | 0.495 | 0.358 | 92.2% | 96.5% |
| split-ma4-bulk-ma52-r10-full-r1 | split-ma4-bulk-ma52-r10 | full | 0.699 | 0.720 | 1.647 | -24.3% | 0.413 | 0.333 | 89.3% | 97.0% |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10 | full | 0.736 | 0.784 | 1.641 | -33.8% | 0.400 | 0.342 | 90.2% | 97.5% |
| ets-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10 | full | 0.766 | 0.754 | 1.665 | -32.7% | 0.491 | 0.346 | 91.2% | 96.4% |
| arima-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10 | full | 0.776 | 0.793 | 1.661 | -39.1% | 0.479 | 0.353 | 91.3% | 96.6% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-full-r1 | +0.035 [+0.030, +0.039] * | +0.065 [+0.051, +0.081] * | -0.019 [-0.022, -0.017] * |
| ets-bulk-ma52-full-r1 | +0.078 [+0.072, +0.084] * | +0.041 [+0.034, +0.049] * | +0.080 [+0.072, +0.088] * |
| arima-bulk-ma52-full-r1 | +0.088 [+0.080, +0.098] * | +0.083 [+0.071, +0.095] * | +0.071 [+0.061, +0.081] * |
| split-ma4-bulk-ma52-r10-full-r1 | +0.011 [+0.008, +0.013] * | +0.017 [+0.011, +0.024] * | -0.008 [-0.010, -0.007] * |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-full-r1 | +0.047 [+0.041, +0.052] * | +0.080 [+0.064, +0.098] * | -0.022 [-0.025, -0.019] * |
| ets-bulk-ma52-r10-full-r1 | +0.077 [+0.072, +0.083] * | +0.051 [+0.043, +0.059] * | +0.064 [+0.057, +0.072] * |
| arima-bulk-ma52-r10-full-r1 | +0.086 [+0.078, +0.093] * | +0.090 [+0.078, +0.102] * | +0.056 [+0.047, +0.065] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-full-r1 | ets-bulk-ma52-full-r1 | arima-bulk-ma52-full-r1 | split-ma4-bulk-ma52-r10-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10-full-r1 |
|---|---|---|---|---|---|---|---|---|---|
| A-erratic | 539 | 0.661 | 0.706 | 0.709 | 0.749 | 0.670 | 0.718 | 0.710 | 0.744 |
| A-intermittent | 20 | 0.858 | 0.889 | 0.871 | 0.873 | 0.879 | 0.912 | 0.891 | 0.888 |
| A-lumpy | 119 | 0.720 | 0.956 | 0.738 | 0.825 | 0.803 | 1.010 | 0.812 | 0.873 |
| A-smooth | 274 | 0.712 | 0.723 | 0.747 | 0.779 | 0.710 | 0.728 | 0.744 | 0.778 |
| B-erratic | 474 | 0.663 | 0.671 | 0.710 | 0.728 | 0.672 | 0.685 | 0.715 | 0.728 |
| B-intermittent | 31 | 0.581 | 0.615 | 0.625 | 0.646 | 0.583 | 0.618 | 0.631 | 0.649 |
| B-lumpy | 548 | 0.747 | 0.813 | 0.833 | 0.856 | 0.768 | 0.835 | 0.826 | 0.857 |
| B-smooth | 92 | 0.735 | 0.736 | 0.777 | 0.790 | 0.737 | 0.741 | 0.776 | 0.788 |
| C-erratic | 148 | 0.348 | 0.347 | 0.373 | 0.499 | 0.361 | 0.362 | 0.385 | 0.428 |
| C-intermittent | 525 | 0.688 | 0.722 | 0.803 | 0.792 | 0.689 | 0.723 | 0.804 | 0.793 |
| C-lumpy | 1252 | 0.787 | 0.806 | 0.900 | 0.890 | 0.798 | 0.818 | 0.892 | 0.883 |
| C-smooth | 122 | 0.329 | 0.332 | 0.348 | 0.385 | 0.331 | 0.335 | 0.350 | 0.381 |
| unclassified | 140 | 0.175 | 0.251 | 0.247 | 0.173 | 0.175 | 0.251 | 0.247 | 0.173 |
