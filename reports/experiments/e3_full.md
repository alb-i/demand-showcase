# E3 ETS / ARIMA (full set, tuning origins)

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r3 | split-ma4-bulk-ma52 | full | 0.699 | 0.720 | 1.647 | -24.3% | 0.414 | 0.333 | 89.3% | 97.0% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.736 | 0.784 | 1.641 | -33.8% | 0.400 | 0.341 | 90.2% | 97.5% |
| ets-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10 | full | 0.766 | 0.754 | 1.665 | -32.7% | 0.491 | 0.346 | 91.2% | 96.4% |
| arima-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10 | full | 0.776 | 0.793 | 1.661 | -39.1% | 0.479 | 0.353 | 91.3% | 96.6% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | +0.036 [+0.032, +0.040] * | +0.063 [+0.052, +0.075] * | -0.014 [-0.016, -0.012] * |
| ets-bulk-ma52-r10-full-r1 | +0.067 [+0.061, +0.072] * | +0.034 [+0.028, +0.040] * | +0.073 [+0.065, +0.081] * |
| arima-bulk-ma52-r10-full-r1 | +0.075 [+0.068, +0.081] * | +0.073 [+0.064, +0.081] * | +0.064 [+0.056, +0.073] * |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r3 | split-tsb-a0.2-b0.2-bulk-ma52-full-r3 | ets-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10-full-r1 |
|---|---|---|---|---|---|
| A-erratic | 448 | 0.675 | 0.728 | 0.715 | 0.752 |
| A-intermittent | 26 | 0.795 | 0.829 | 0.812 | 0.825 |
| A-lumpy | 114 | 0.814 | 1.029 | 0.822 | 0.883 |
| A-smooth | 364 | 0.695 | 0.712 | 0.729 | 0.760 |
| B-erratic | 434 | 0.662 | 0.675 | 0.704 | 0.716 |
| B-intermittent | 61 | 0.584 | 0.615 | 0.629 | 0.645 |
| B-lumpy | 530 | 0.783 | 0.851 | 0.842 | 0.875 |
| B-smooth | 120 | 0.725 | 0.731 | 0.764 | 0.782 |
| C-erratic | 122 | 0.362 | 0.362 | 0.385 | 0.437 |
| C-intermittent | 605 | 0.760 | 0.792 | 0.869 | 0.855 |
| C-lumpy | 1188 | 0.763 | 0.784 | 0.859 | 0.851 |
| C-smooth | 132 | 0.335 | 0.339 | 0.354 | 0.382 |
| unclassified | 140 | 0.175 | 0.251 | 0.247 | 0.173 |
