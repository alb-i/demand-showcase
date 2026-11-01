# E2b item demand only (focus set, tuning origins)

Reference for the bootstrap: `ma4-item-focus-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-item-focus-r1 | ma4 | focus | 0.732 | 0.758 | 0.790 | 1.3% | 0.338 | 0.345 | 89.2% | 97.7% |
| tsb-a0.2-b0.2-item-focus-r1 | tsb-a0.2-b0.2 | focus | 0.792 | 0.835 | 0.793 | -10.3% | 0.350 | 0.366 | 88.5% | 97.5% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| tsb-a0.2-b0.2-item-focus-r1 | +0.060 [+0.046, +0.076] * | +0.076 [+0.048, +0.111] * | +0.012 [+0.007, +0.018] * |

## MASE per segment

| segment | series | ma4-item-focus-r1 | tsb-a0.2-b0.2-item-focus-r1 |
|---|---|---|---|
| A-erratic | 373 | 0.750 | 0.804 |
| A-intermittent | 16 | 0.906 | 0.916 |
| A-lumpy | 66 | 0.676 | 1.037 |
| A-smooth | 293 | 0.713 | 0.715 |
