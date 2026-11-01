# E9 test origins (focus set, all models)

Reference for the bootstrap: `best-crps-focus-test-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best-crps-focus-test-r1 | best-crps | focus | 0.711 | 0.829 | 0.887 | 0.7% | 0.336 | 0.391 | 85.1% | 97.5% | 81.4% | 94.5% |
| naive-focus-test-r1 | naive | focus | 0.822 | 0.993 | 1.054 | 8.5% | 0.448 | 0.520 | 84.4% | 95.8% | 80.5% | 94.6% |
| snaive-focus-test-r1 | snaive | focus | 1.273 | 1.304 | 1.284 | -41.2% | 0.611 | 0.609 | 80.1% | 95.0% | 75.0% | 92.4% |
| ma4-focus-test-r1 | ma4 | focus | 0.715 | 0.862 | 0.922 | 9.0% | 0.385 | 0.444 | 85.5% | 96.5% | 81.4% | 95.2% |
| ma8-focus-test-r1 | ma8 | focus | 0.704 | 0.850 | 0.915 | 10.2% | 0.378 | 0.438 | 86.9% | 96.8% | 82.8% | 95.6% |
| ma13-focus-test-r1 | ma13 | focus | 0.719 | 0.867 | 0.927 | 10.9% | 0.385 | 0.448 | 87.4% | 96.9% | 83.3% | 95.7% |
| croston-a0.1-focus-test-r1 | croston-a0.1 | focus | 0.842 | 0.919 | 0.949 | 4.2% | 0.411 | 0.462 | 85.6% | 96.3% | 80.6% | 94.2% |
| croston-a0.2-focus-test-r1 | croston-a0.2 | focus | 0.811 | 0.897 | 0.948 | 5.9% | 0.408 | 0.455 | 85.3% | 96.2% | 80.4% | 94.3% |
| sba-a0.1-focus-test-r1 | sba-a0.1 | focus | 0.826 | 0.907 | 0.949 | 9.0% | 0.411 | 0.462 | 85.6% | 96.3% | 80.5% | 94.1% |
| sba-a0.2-focus-test-r1 | sba-a0.2 | focus | 0.785 | 0.877 | 0.947 | 15.3% | 0.407 | 0.454 | 85.4% | 96.2% | 80.2% | 94.2% |
| tsb-a0.1-b0.1-focus-test-r1 | tsb-a0.1-b0.1 | focus | 0.730 | 0.864 | 0.916 | 8.3% | 0.382 | 0.444 | 87.4% | 96.9% | 83.4% | 95.7% |
| tsb-a0.2-b0.2-focus-test-r1 | tsb-a0.2-b0.2 | focus | 0.701 | 0.841 | 0.909 | 9.8% | 0.376 | 0.435 | 86.7% | 96.7% | 82.7% | 95.5% |
| split-ma4-bulk-0-focus-test-r1 | split-ma4-bulk-0 | focus | 0.655 | 0.807 | 0.930 | 40.2% | 0.371 | 0.427 | 86.1% | 96.8% | 81.4% | 95.3% |
| split-ma4-bulk-ma52-focus-test-r1 | split-ma4-bulk-ma52 | focus | 0.709 | 0.824 | 0.895 | 2.9% | 0.366 | 0.415 | 87.1% | 96.9% | 83.0% | 95.7% |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-test-r1 | split-ma4-bulk-tsb-a0.1-b0.1 | focus | 0.705 | 0.816 | 0.910 | 5.8% | 0.373 | 0.422 | 87.3% | 96.9% | 83.5% | 95.8% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-test-r1 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 0.723 | 0.841 | 0.902 | 3.4% | 0.372 | 0.425 | 87.7% | 97.1% | 83.6% | 95.8% |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-test-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1 | focus | 0.717 | 0.831 | 0.916 | 6.3% | 0.379 | 0.432 | 87.5% | 96.9% | 83.7% | 95.8% |
| split-ma4-bulk-ma52-poolcat-focus-test-r1 | split-ma4-bulk-ma52-poolcat | focus | 0.709 | 0.824 | 0.895 | 2.9% | 0.362 | 0.410 | 87.2% | 96.9% | 83.1% | 95.7% |
| topdown-ma4-bulk-ma52-focus-test-r1 | topdown-ma4-bulk-ma52 | focus | 0.871 | 0.956 | 0.923 | -14.5% | 0.388 | 0.434 | 86.2% | 96.9% | 81.0% | 94.7% |
| topdown-ma13-bulk-ma52-focus-test-r1 | topdown-ma13-bulk-ma52 | focus | 0.848 | 0.938 | 0.926 | -8.5% | 0.391 | 0.441 | 87.8% | 97.3% | 82.6% | 95.3% |
| ets-bulk-ma52-focus-test-r1 | ets-bulk-ma52 | focus | 0.715 | 0.824 | 0.892 | 2.3% | 0.355 | 0.394 | 87.9% | 96.6% | 82.5% | 94.9% |
| arima-bulk-ma52-focus-test-r1 | arima-bulk-ma52 | focus | 0.754 | 0.858 | 0.901 | -0.2% | 0.364 | 0.405 | 88.3% | 96.7% | 82.5% | 94.9% |
| lgbm-item-bulk-ma52-focus-test-r1 | lgbm-item-bulk-ma52 | focus | 0.724 | 0.835 | 0.878 | -3.0% | 0.362 | 0.417 | 79.0% | 93.3% | 74.7% | 91.6% |
| lgbm-total-focus-test-r1 | lgbm-total | focus | 0.717 | 0.833 | 0.888 | 1.1% | 0.381 | 0.439 | 76.4% | 92.2% | 72.4% | 90.5% |
| lgbm-total-p1.8-focus-test-r1 | lgbm-total-p1.8 | focus | 0.711 | 0.829 | 0.887 | 0.7% | 0.378 | 0.436 | 76.5% | 92.2% | 72.5% | 90.4% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| naive-focus-test-r1 | +0.111 [+0.094, +0.129] * | +0.162 [+0.140, +0.184] * | +0.112 [+0.100, +0.124] * |
| snaive-focus-test-r1 | +0.562 [+0.512, +0.611] * | +0.481 [+0.414, +0.544] * | +0.275 [+0.246, +0.305] * |
| ma4-focus-test-r1 | +0.004 [-0.008, +0.016] | +0.033 [+0.013, +0.053] * | +0.049 [+0.041, +0.059] * |
| ma8-focus-test-r1 | -0.007 [-0.020, +0.005] | +0.020 [+0.000, +0.047] * | +0.043 [+0.033, +0.053] * |
| ma13-focus-test-r1 | +0.008 [-0.007, +0.024] | +0.037 [+0.011, +0.074] * | +0.049 [+0.038, +0.062] * |
| croston-a0.1-focus-test-r1 | +0.131 [+0.095, +0.168] * | +0.090 [+0.054, +0.136] * | +0.075 [+0.059, +0.093] * |
| croston-a0.2-focus-test-r1 | +0.100 [+0.065, +0.137] * | +0.068 [+0.038, +0.104] * | +0.072 [+0.056, +0.091] * |
| sba-a0.1-focus-test-r1 | +0.115 [+0.081, +0.151] * | +0.078 [+0.042, +0.123] * | +0.075 [+0.059, +0.093] * |
| sba-a0.2-focus-test-r1 | +0.074 [+0.042, +0.108] * | +0.049 [+0.017, +0.087] * | +0.071 [+0.055, +0.089] * |
| tsb-a0.1-b0.1-focus-test-r1 | +0.019 [+0.004, +0.034] * | +0.034 [+0.009, +0.069] * | +0.046 [+0.035, +0.059] * |
| tsb-a0.2-b0.2-focus-test-r1 | -0.011 [-0.023, +0.001] | +0.012 [-0.007, +0.037] | +0.040 [+0.031, +0.051] * |
| split-ma4-bulk-0-focus-test-r1 | -0.056 [-0.070, -0.042] * | -0.018 [-0.054, +0.019] | +0.036 [+0.027, +0.046] * |
| split-ma4-bulk-ma52-focus-test-r1 | -0.002 [-0.015, +0.010] | -0.006 [-0.026, +0.016] | +0.030 [+0.022, +0.040] * |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-test-r1 | -0.006 [-0.021, +0.010] | -0.012 [-0.028, +0.007] | +0.037 [+0.028, +0.047] * |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-test-r1 | +0.012 [-0.002, +0.026] | +0.011 [-0.012, +0.037] | +0.036 [+0.027, +0.048] * |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-test-r1 | +0.005 [-0.011, +0.023] | +0.003 [-0.016, +0.027] | +0.043 [+0.032, +0.055] * |
| split-ma4-bulk-ma52-poolcat-focus-test-r1 | -0.002 [-0.015, +0.010] | -0.006 [-0.026, +0.016] | +0.027 [+0.020, +0.034] * |
| topdown-ma4-bulk-ma52-focus-test-r1 | +0.160 [+0.139, +0.182] * | +0.126 [+0.095, +0.159] * | +0.053 [+0.043, +0.064] * |
| topdown-ma13-bulk-ma52-focus-test-r1 | +0.136 [+0.115, +0.159] * | +0.106 [+0.072, +0.140] * | +0.055 [+0.043, +0.069] * |
| ets-bulk-ma52-focus-test-r1 | +0.003 [-0.010, +0.015] | -0.005 [-0.024, +0.013] | +0.019 [+0.014, +0.025] * |
| arima-bulk-ma52-focus-test-r1 | +0.043 [+0.025, +0.059] * | +0.027 [+0.000, +0.055] * | +0.029 [+0.021, +0.037] * |
| lgbm-item-bulk-ma52-focus-test-r1 | +0.013 [+0.004, +0.022] * | +0.005 [-0.009, +0.018] | +0.027 [+0.019, +0.035] * |
| lgbm-total-focus-test-r1 | +0.006 [+0.002, +0.009] * | +0.004 [+0.000, +0.008] * | +0.045 [+0.036, +0.057] * |
| lgbm-total-p1.8-focus-test-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.042 [+0.034, +0.052] * |

## MASE per segment

| segment | series | best-crps-focus-test-r1 | naive-focus-test-r1 | snaive-focus-test-r1 | ma4-focus-test-r1 | ma8-focus-test-r1 | ma13-focus-test-r1 | croston-a0.1-focus-test-r1 | croston-a0.2-focus-test-r1 | sba-a0.1-focus-test-r1 | sba-a0.2-focus-test-r1 | tsb-a0.1-b0.1-focus-test-r1 | tsb-a0.2-b0.2-focus-test-r1 | split-ma4-bulk-0-focus-test-r1 | split-ma4-bulk-ma52-focus-test-r1 | split-ma4-bulk-tsb-a0.1-b0.1-focus-test-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-test-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-test-r1 | split-ma4-bulk-ma52-poolcat-focus-test-r1 | topdown-ma4-bulk-ma52-focus-test-r1 | topdown-ma13-bulk-ma52-focus-test-r1 | ets-bulk-ma52-focus-test-r1 | arima-bulk-ma52-focus-test-r1 | lgbm-item-bulk-ma52-focus-test-r1 | lgbm-total-focus-test-r1 | lgbm-total-p1.8-focus-test-r1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-erratic | 373 | 0.654 | 0.733 | 1.191 | 0.644 | 0.642 | 0.666 | 0.761 | 0.727 | 0.746 | 0.704 | 0.675 | 0.638 | 0.591 | 0.658 | 0.655 | 0.674 | 0.670 | 0.658 | 0.822 | 0.805 | 0.670 | 0.705 | 0.672 | 0.659 | 0.654 |
| A-intermittent | 16 | 0.784 | 0.947 | 1.467 | 0.807 | 0.776 | 0.767 | 0.923 | 0.911 | 0.902 | 0.871 | 0.754 | 0.757 | 0.729 | 0.820 | 0.770 | 0.808 | 0.755 | 0.820 | 0.943 | 0.896 | 0.816 | 0.841 | 0.814 | 0.776 | 0.784 |
| A-lumpy | 66 | 0.856 | 0.877 | 1.890 | 0.830 | 0.871 | 0.935 | 1.526 | 1.390 | 1.493 | 1.339 | 1.016 | 0.892 | 0.819 | 0.907 | 0.912 | 0.983 | 0.979 | 0.907 | 1.227 | 1.230 | 0.892 | 1.090 | 0.945 | 0.897 | 0.856 |
| A-smooth | 293 | 0.748 | 0.917 | 1.228 | 0.775 | 0.742 | 0.736 | 0.787 | 0.781 | 0.774 | 0.759 | 0.734 | 0.734 | 0.696 | 0.724 | 0.719 | 0.722 | 0.715 | 0.724 | 0.849 | 0.813 | 0.726 | 0.736 | 0.736 | 0.747 | 0.748 |
