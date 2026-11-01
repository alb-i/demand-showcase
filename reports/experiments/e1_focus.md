# E1 baselines (focus set, tuning origins)

Reference for the bootstrap: `naive-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| naive-focus-r1 | naive | focus | 0.814 | 0.836 | 2.782 | 0.6% | 0.442 | 0.425 | 86.9% | 97.1% |
| snaive-focus-r1 | snaive | focus | 1.064 | 1.027 | 2.826 | -35.0% | 0.536 | 0.483 | 81.7% | 95.8% |
| ma4-focus-r1 | ma4 | focus | 0.720 | 0.735 | 2.741 | 0.3% | 0.390 | 0.372 | 88.2% | 97.2% |
| ma8-focus-r1 | ma8 | focus | 0.754 | 0.784 | 2.743 | -7.2% | 0.397 | 0.389 | 87.6% | 96.9% |
| ma13-focus-r1 | ma13 | focus | 0.822 | 0.859 | 2.749 | -17.3% | 0.414 | 0.410 | 86.1% | 96.2% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| snaive-focus-r1 | +0.249 [+0.214, +0.283] * | +0.190 [+0.152, +0.228] * | +0.094 [+0.072, +0.113] * |
| ma4-focus-r1 | -0.094 [-0.104, -0.085] * | -0.099 [-0.113, -0.085] * | -0.052 [-0.060, -0.045] * |
| ma8-focus-r1 | -0.060 [-0.079, -0.042] * | -0.050 [-0.082, -0.017] * | -0.045 [-0.058, -0.033] * |
| ma13-focus-r1 | +0.007 [-0.020, +0.034] | +0.025 [-0.023, +0.076] | -0.028 [-0.045, -0.013] * |

## MASE per segment

| segment | series | naive-focus-r1 | snaive-focus-r1 | ma4-focus-r1 | ma8-focus-r1 | ma13-focus-r1 |
|---|---|---|---|---|---|---|
| A-erratic | 373 | 0.760 | 1.012 | 0.681 | 0.717 | 0.783 |
| A-intermittent | 16 | 1.102 | 1.385 | 0.922 | 0.890 | 0.890 |
| A-lumpy | 66 | 0.934 | 1.086 | 0.950 | 1.149 | 1.432 |
| A-smooth | 293 | 0.841 | 1.107 | 0.708 | 0.705 | 0.730 |
