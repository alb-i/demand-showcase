# E3b bulk threshold 10x vs 20x (full set, tuning origins, products with bulk lines)

> Record of the 20x vs 10x comparison; run before 10x became the only threshold: segments and the "products with bulk lines" here are still the 20x ones.

Reference for the bootstrap: `split-ma4-bulk-ma52-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only products with bulk lines (> 20x median) before 2011-06-06.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-full-r1 | split-ma4-bulk-ma52 | full | 0.711 | 0.711 | 1.952 | -24.6% | 0.390 | 0.337 | 90.3% | 97.3% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.747 | 0.780 | 1.949 | -35.2% | 0.380 | 0.347 | 90.4% | 97.6% |
| ets-bulk-ma52-full-r1 | ets-bulk-ma52 | full | 0.760 | 0.746 | 1.966 | -34.6% | 0.402 | 0.347 | 90.0% | 96.5% |
| arima-bulk-ma52-full-r1 | arima-bulk-ma52 | full | 0.777 | 0.788 | 1.964 | -41.7% | 0.398 | 0.351 | 90.4% | 96.7% |
| split-ma4-bulk-ma52-r10-full-r1 | split-ma4-bulk-ma52-r10 | full | 0.724 | 0.729 | 1.949 | -29.1% | 0.382 | 0.332 | 90.9% | 97.5% |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10 | full | 0.760 | 0.794 | 1.949 | -38.4% | 0.378 | 0.343 | 91.0% | 97.8% |
| ets-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10 | full | 0.761 | 0.756 | 1.958 | -36.6% | 0.388 | 0.338 | 89.2% | 96.7% |
| arima-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10 | full | 0.778 | 0.798 | 1.961 | -43.2% | 0.388 | 0.348 | 89.2% | 96.8% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| split-tsb-a0.2-b0.2-bulk-ma52-full-r1 | +0.035 [+0.030, +0.041] * | +0.068 [+0.052, +0.087] * | -0.010 [-0.013, -0.007] * |
| ets-bulk-ma52-full-r1 | +0.049 [+0.044, +0.055] * | +0.035 [+0.027, +0.043] * | +0.011 [+0.007, +0.015] * |
| arima-bulk-ma52-full-r1 | +0.065 [+0.059, +0.072] * | +0.077 [+0.063, +0.091] * | +0.008 [+0.004, +0.012] * |
| split-ma4-bulk-ma52-r10-full-r1 | +0.013 [+0.009, +0.017] * | +0.018 [+0.010, +0.027] * | -0.008 [-0.011, -0.007] * |
| split-tsb-a0.2-b0.2-bulk-ma52-r10-full-r1 | +0.048 [+0.041, +0.055] * | +0.082 [+0.063, +0.103] * | -0.013 [-0.016, -0.010] * |
| ets-bulk-ma52-r10-full-r1 | +0.051 [+0.045, +0.056] * | +0.045 [+0.036, +0.054] * | -0.002 [-0.006, +0.001] |
| arima-bulk-ma52-r10-full-r1 | +0.066 [+0.059, +0.073] * | +0.087 [+0.072, +0.102] * | -0.002 [-0.006, +0.002] |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-full-r1 | ets-bulk-ma52-full-r1 | arima-bulk-ma52-full-r1 | split-ma4-bulk-ma52-r10-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-r10-full-r1 | ets-bulk-ma52-r10-full-r1 | arima-bulk-ma52-r10-full-r1 |
|---|---|---|---|---|---|---|---|---|---|
| A-erratic | 440 | 0.665 | 0.713 | 0.710 | 0.751 | 0.677 | 0.725 | 0.711 | 0.748 |
| A-intermittent | 13 | 0.865 | 0.909 | 0.895 | 0.875 | 0.885 | 0.932 | 0.914 | 0.891 |
| A-lumpy | 88 | 0.877 | 1.094 | 0.884 | 0.947 | 0.959 | 1.144 | 0.956 | 1.008 |
| A-smooth | 226 | 0.707 | 0.721 | 0.744 | 0.774 | 0.707 | 0.726 | 0.738 | 0.772 |
| B-erratic | 293 | 0.642 | 0.660 | 0.683 | 0.711 | 0.656 | 0.677 | 0.694 | 0.717 |
| B-intermittent | 16 | 0.561 | 0.580 | 0.553 | 0.567 | 0.565 | 0.587 | 0.565 | 0.572 |
| B-lumpy | 327 | 0.751 | 0.804 | 0.817 | 0.825 | 0.770 | 0.819 | 0.812 | 0.825 |
| B-smooth | 39 | 0.714 | 0.716 | 0.767 | 0.763 | 0.722 | 0.729 | 0.766 | 0.759 |
| C-erratic | 56 | 0.517 | 0.508 | 0.554 | 0.545 | 0.520 | 0.516 | 0.552 | 0.528 |
| C-intermittent | 64 | 0.935 | 0.940 | 0.988 | 0.960 | 0.936 | 0.941 | 0.989 | 0.961 |
| C-lumpy | 424 | 0.742 | 0.754 | 0.805 | 0.793 | 0.750 | 0.762 | 0.795 | 0.788 |
| C-smooth | 24 | 0.573 | 0.579 | 0.602 | 0.611 | 0.577 | 0.584 | 0.604 | 0.616 |
| unclassified | 1 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |
