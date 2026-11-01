# E3c category level (category totals, tuning origins)

Reference for the bootstrap: `split-ma4-bulk-ma52-category-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| split-ma4-bulk-ma52-category-r1 | split-ma4-bulk-ma52 | category | 0.782 | 0.657 | 0.804 | -11.6% | 0.373 | 0.315 | 89.1% | 97.8% |
| naive-category-r1 | naive | category | 0.848 | 0.728 | 0.940 | 4.3% | 0.417 | 0.349 | 88.6% | 98.5% |
| ma4-category-r1 | ma4 | category | 0.759 | 0.619 | 0.830 | 3.9% | 0.386 | 0.320 | 87.9% | 98.1% |
| ma13-category-r1 | ma13 | category | 1.028 | 0.870 | 1.018 | -12.5% | 0.511 | 0.445 | 79.7% | 95.5% |
| tsb-a0.2-b0.2-category-r1 | tsb-a0.2-b0.2 | category | 0.867 | 0.723 | 0.879 | -7.1% | 0.423 | 0.362 | 84.3% | 97.1% |
| ets-bulk-ma52-category-r1 | ets-bulk-ma52 | category | 0.767 | 0.655 | 0.789 | -12.2% | 0.328 | 0.271 | 83.5% | 97.4% |
| arima-bulk-ma52-category-r1 | arima-bulk-ma52 | category | 0.823 | 0.711 | 0.806 | -15.7% | 0.352 | 0.297 | 81.6% | 97.2% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| naive-category-r1 | +0.066 [-0.072, +0.173] | +0.073 [-0.084, +0.174] | +0.043 [-0.005, +0.096] |
| ma4-category-r1 | -0.023 [-0.122, +0.060] | -0.038 [-0.154, +0.028] | +0.013 [-0.012, +0.038] |
| ma13-category-r1 | +0.246 [+0.143, +0.362] * | +0.209 [+0.120, +0.339] * | +0.138 [+0.070, +0.237] * |
| tsb-a0.2-b0.2-category-r1 | +0.085 [+0.039, +0.133] * | +0.064 [+0.035, +0.101] * | +0.050 [+0.026, +0.085] * |
| ets-bulk-ma52-category-r1 | -0.015 [-0.047, +0.014] | -0.001 [-0.030, +0.017] | -0.045 [-0.070, -0.027] * |
| arima-bulk-ma52-category-r1 | +0.041 [-0.029, +0.111] | +0.054 [-0.007, +0.125] | -0.021 [-0.057, +0.009] |

## MASE per segment

| segment | series | split-ma4-bulk-ma52-category-r1 | naive-category-r1 | ma4-category-r1 | ma13-category-r1 | tsb-a0.2-b0.2-category-r1 | ets-bulk-ma52-category-r1 | arima-bulk-ma52-category-r1 |
|---|---|---|---|---|---|---|---|---|
| accessories | 1 | 0.707 | 0.787 | 0.694 | 1.233 | 0.905 | 0.686 | 0.728 |
| bags | 1 | 0.663 | 0.962 | 0.765 | 0.824 | 0.742 | 0.685 | 0.727 |
| bath_beauty | 1 | 0.773 | 0.813 | 0.810 | 0.684 | 0.699 | 0.757 | 0.794 |
| candles_lights | 1 | 0.642 | 0.610 | 0.514 | 0.845 | 0.669 | 0.671 | 0.973 |
| christmas | 1 | 0.994 | 0.195 | 0.317 | 1.795 | 1.159 | 0.863 | 0.835 |
| decorations | 1 | 0.575 | 0.730 | 0.536 | 0.917 | 0.690 | 0.597 | 0.801 |
| easter | 1 | 1.979 | 1.699 | 1.914 | 2.650 | 2.208 | 1.780 | 1.663 |
| furniture | 1 | 0.981 | 1.256 | 1.034 | 0.919 | 0.938 | 0.894 | 0.891 |
| garden_outdoor | 1 | 0.760 | 1.055 | 0.838 | 0.820 | 0.801 | 0.778 | 0.746 |
| jewellery | 1 | 0.694 | 0.616 | 0.573 | 0.891 | 0.724 | 0.786 | 1.006 |
| kitchen_tableware | 1 | 0.499 | 0.644 | 0.523 | 0.558 | 0.528 | 0.524 | 0.510 |
| other | 1 | 0.909 | 1.374 | 1.308 | 1.197 | 1.238 | 0.908 | 0.977 |
| party_giftwrap | 1 | 0.362 | 0.433 | 0.365 | 0.335 | 0.322 | 0.374 | 0.419 |
| stationery_craft | 1 | 0.409 | 0.457 | 0.370 | 0.539 | 0.423 | 0.419 | 0.444 |
| storage | 1 | 0.769 | 0.929 | 0.714 | 0.993 | 0.830 | 0.777 | 0.780 |
| textiles_cushions | 1 | 1.081 | 1.039 | 1.066 | 1.499 | 1.268 | 1.024 | 1.246 |
| toys_games | 1 | 0.739 | 0.960 | 0.732 | 1.079 | 0.852 | 0.727 | 0.741 |
| wall_decor | 1 | 0.539 | 0.703 | 0.595 | 0.724 | 0.615 | 0.554 | 0.528 |
