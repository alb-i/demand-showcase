# E2b item demand only (full set, tuning origins)

Reference for the bootstrap: `ma4-item-full-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-item-full-r1 | ma4 | full | 0.658 | 0.708 | 0.956 | -2.9% | 0.385 | 0.335 | 87.9% | 96.7% |
| tsb-a0.2-b0.2-item-full-r1 | tsb-a0.2-b0.2 | full | 0.701 | 0.792 | 0.931 | -16.7% | 0.366 | 0.349 | 88.9% | 97.2% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| tsb-a0.2-b0.2-item-full-r1 | +0.042 [+0.036, +0.047] * | +0.083 [+0.062, +0.107] * | -0.020 [-0.023, -0.017] * |

## MASE per segment

| segment | series | ma4-item-full-r1 | tsb-a0.2-b0.2-item-full-r1 |
|---|---|---|---|
| A-erratic | 448 | 0.696 | 0.752 |
| A-intermittent | 26 | 0.672 | 0.750 |
| A-lumpy | 114 | 0.472 | 0.806 |
| A-smooth | 364 | 0.698 | 0.701 |
| B-erratic | 434 | 0.660 | 0.664 |
| B-intermittent | 61 | 0.695 | 0.738 |
| B-lumpy | 530 | 0.779 | 0.868 |
| B-smooth | 120 | 0.610 | 0.612 |
| C-erratic | 122 | 0.312 | 0.303 |
| C-intermittent | 605 | 0.618 | 0.656 |
| C-lumpy | 1188 | 0.733 | 0.757 |
| C-smooth | 132 | 0.280 | 0.284 |
| unclassified | 140 | 0.142 | 0.217 |
