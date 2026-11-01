# E2b bulk/item split vs combined (full set, tuning origins)

Reference for the bootstrap: `ma4-full-r3`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-full-r3 | ma4 | full | 0.666 | 0.688 | 1.658 | -3.1% | 0.435 | 0.359 | 87.7% | 96.7% |
| tsb-a0.2-b0.2-full-r2 | tsb-a0.2-b0.2 | full | 0.698 | 0.747 | 1.643 | -18.3% | 0.408 | 0.356 | 88.8% | 97.2% |
| split-ma4-bulk-0-full-r1 | split-ma4-bulk-0 | full | 0.601 | 0.596 | 1.646 | 29.3% | 0.419 | 0.332 | 87.4% | 96.6% |
| split-ma4-bulk-ma52-full-r2 | split-ma4-bulk-ma52 | full | 0.699 | 0.720 | 1.647 | -24.3% | 0.414 | 0.333 | 89.3% | 97.0% |
| split-ma4-bulk-tsb-a0.1-b0.1-full-r1 | split-ma4-bulk-tsb-a0.1-b0.1 | full | 0.839 | 0.783 | 1.697 | -40.8% | 0.457 | 0.353 | 89.6% | 97.3% |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r2 | split-tsb-a0.2-b0.2-bulk-ma52 | full | 0.736 | 0.784 | 1.641 | -33.8% | 0.400 | 0.341 | 90.2% | 97.5% |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-full-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1 | full | 0.876 | 0.849 | 1.691 | -50.3% | 0.449 | 0.361 | 90.2% | 97.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| tsb-a0.2-b0.2-full-r2 | +0.032 [+0.027, +0.038] * | +0.059 [+0.041, +0.079] * | -0.028 [-0.031, -0.025] * |
| split-ma4-bulk-0-full-r1 | -0.065 [-0.070, -0.059] * | -0.087 [-0.105, -0.071] * | -0.016 [-0.019, -0.012] * |
| split-ma4-bulk-ma52-full-r2 | +0.033 [+0.027, +0.039] * | +0.033 [+0.013, +0.053] * | -0.024 [-0.027, -0.021] * |
| split-ma4-bulk-tsb-a0.1-b0.1-full-r1 | +0.173 [+0.155, +0.191] * | +0.094 [+0.073, +0.118] * | +0.019 [+0.010, +0.028] * |
| split-tsb-a0.2-b0.2-bulk-ma52-full-r2 | +0.069 [+0.061, +0.077] * | +0.096 [+0.068, +0.124] * | -0.038 [-0.042, -0.034] * |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-full-r1 | +0.209 [+0.191, +0.228] * | +0.159 [+0.130, +0.189] * | +0.011 [+0.002, +0.020] * |

## MASE per segment

| segment | series | ma4-full-r3 | tsb-a0.2-b0.2-full-r2 | split-ma4-bulk-0-full-r1 | split-ma4-bulk-ma52-full-r2 | split-ma4-bulk-tsb-a0.1-b0.1-full-r1 | split-tsb-a0.2-b0.2-bulk-ma52-full-r2 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-full-r1 |
|---|---|---|---|---|---|---|---|---|
| A-erratic | 448 | 0.645 | 0.685 | 0.550 | 0.675 | 0.738 | 0.728 | 0.794 |
| A-intermittent | 26 | 0.681 | 0.717 | 0.584 | 0.795 | 0.859 | 0.829 | 0.895 |
| A-lumpy | 114 | 0.624 | 0.900 | 0.554 | 0.814 | 1.049 | 1.029 | 1.262 |
| A-smooth | 364 | 0.703 | 0.696 | 0.631 | 0.695 | 0.724 | 0.712 | 0.743 |
| B-erratic | 434 | 0.648 | 0.640 | 0.567 | 0.662 | 0.758 | 0.675 | 0.774 |
| B-intermittent | 61 | 0.513 | 0.543 | 0.465 | 0.584 | 0.676 | 0.615 | 0.706 |
| B-lumpy | 530 | 0.716 | 0.785 | 0.631 | 0.783 | 1.005 | 0.851 | 1.071 |
| B-smooth | 120 | 0.692 | 0.688 | 0.624 | 0.725 | 0.839 | 0.731 | 0.846 |
| C-erratic | 122 | 0.357 | 0.346 | 0.322 | 0.362 | 0.436 | 0.362 | 0.437 |
| C-intermittent | 605 | 0.729 | 0.768 | 0.710 | 0.760 | 0.838 | 0.792 | 0.870 |
| C-lumpy | 1188 | 0.734 | 0.751 | 0.663 | 0.763 | 1.002 | 0.784 | 1.021 |
| C-smooth | 132 | 0.311 | 0.311 | 0.295 | 0.335 | 0.368 | 0.339 | 0.373 |
| unclassified | 140 | 0.175 | 0.251 | 0.175 | 0.175 | 0.175 | 0.251 | 0.251 |
