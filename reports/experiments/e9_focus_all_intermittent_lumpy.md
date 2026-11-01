# E9 test origins (focus set, all models, intermittent + lumpy)

Reference for the bootstrap: `best-crps-focus-test-r1`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better. rcov = coverage under the randomised PIT (ties y = q fractional).

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 | rcov 80 | rcov 95 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| best-crps-focus-test-r1 | best-crps | focus | 0.842 | 1.165 | 0.870 | 17.2% | 0.406 | 0.575 | 87.6% | 97.2% | 78.0% | 93.9% |
| naive-focus-test-r1 | naive | focus | 0.890 | 1.357 | 1.015 | 27.2% | 0.561 | 0.811 | 84.8% | 96.4% | 76.0% | 93.8% |
| snaive-focus-test-r1 | snaive | focus | 1.808 | 1.997 | 1.530 | -50.5% | 1.041 | 1.115 | 75.1% | 93.5% | 64.2% | 88.5% |
| ma4-focus-test-r1 | ma4 | focus | 0.826 | 1.281 | 0.942 | 32.7% | 0.520 | 0.770 | 86.8% | 97.0% | 77.0% | 94.2% |
| ma8-focus-test-r1 | ma8 | focus | 0.853 | 1.346 | 0.978 | 37.3% | 0.540 | 0.814 | 88.3% | 97.0% | 78.6% | 94.4% |
| ma13-focus-test-r1 | ma13 | focus | 0.902 | 1.434 | 1.024 | 41.0% | 0.569 | 0.865 | 88.9% | 97.2% | 79.5% | 94.7% |
| croston-a0.1-focus-test-r1 | croston-a0.1 | focus | 1.408 | 1.769 | 1.134 | 12.5% | 0.674 | 0.957 | 85.2% | 96.8% | 74.1% | 92.3% |
| croston-a0.2-focus-test-r1 | croston-a0.2 | focus | 1.297 | 1.625 | 1.131 | 17.1% | 0.659 | 0.895 | 86.0% | 96.2% | 75.1% | 92.5% |
| sba-a0.1-focus-test-r1 | sba-a0.1 | focus | 1.377 | 1.756 | 1.129 | 16.9% | 0.673 | 0.959 | 85.3% | 96.7% | 74.1% | 92.2% |
| sba-a0.2-focus-test-r1 | sba-a0.2 | focus | 1.248 | 1.613 | 1.117 | 25.4% | 0.656 | 0.903 | 86.0% | 96.2% | 74.9% | 92.5% |
| tsb-a0.1-b0.1-focus-test-r1 | tsb-a0.1-b0.1 | focus | 0.965 | 1.464 | 1.007 | 28.9% | 0.568 | 0.873 | 88.4% | 97.1% | 80.0% | 94.8% |
| tsb-a0.2-b0.2-focus-test-r1 | tsb-a0.2-b0.2 | focus | 0.866 | 1.336 | 0.966 | 33.8% | 0.537 | 0.812 | 88.0% | 96.9% | 78.9% | 94.5% |
| split-ma4-bulk-0-focus-test-r1 | split-ma4-bulk-0 | focus | 0.801 | 1.331 | 0.981 | 66.1% | 0.529 | 0.814 | 87.3% | 96.8% | 76.7% | 94.0% |
| split-ma4-bulk-ma52-focus-test-r1 | split-ma4-bulk-ma52 | focus | 0.890 | 1.326 | 0.931 | 14.3% | 0.517 | 0.768 | 87.9% | 97.0% | 78.2% | 94.3% |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-test-r1 | split-ma4-bulk-tsb-a0.1-b0.1 | focus | 0.884 | 1.277 | 0.937 | 18.7% | 0.525 | 0.773 | 88.4% | 97.0% | 79.5% | 94.5% |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-test-r1 | split-tsb-a0.2-b0.2-bulk-ma52 | focus | 0.949 | 1.407 | 0.969 | 15.6% | 0.545 | 0.815 | 88.6% | 97.0% | 79.4% | 94.6% |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-test-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1 | focus | 0.935 | 1.351 | 0.970 | 19.9% | 0.550 | 0.819 | 88.6% | 97.0% | 79.9% | 94.6% |
| split-ma4-bulk-ma52-poolcat-focus-test-r1 | split-ma4-bulk-ma52-poolcat | focus | 0.890 | 1.326 | 0.931 | 14.3% | 0.488 | 0.740 | 86.7% | 95.6% | 77.2% | 92.7% |
| topdown-ma4-bulk-ma52-focus-test-r1 | topdown-ma4-bulk-ma52 | focus | 1.171 | 1.508 | 0.972 | -4.0% | 0.578 | 0.781 | 84.6% | 96.3% | 73.4% | 92.3% |
| topdown-ma13-bulk-ma52-focus-test-r1 | topdown-ma13-bulk-ma52 | focus | 1.165 | 1.580 | 1.023 | 5.7% | 0.596 | 0.855 | 88.1% | 97.1% | 76.9% | 93.8% |
| ets-bulk-ma52-focus-test-r1 | ets-bulk-ma52 | focus | 0.877 | 1.279 | 0.902 | 9.3% | 0.471 | 0.648 | 91.0% | 96.4% | 78.9% | 93.2% |
| arima-bulk-ma52-focus-test-r1 | arima-bulk-ma52 | focus | 1.042 | 1.484 | 0.971 | 4.6% | 0.525 | 0.734 | 90.3% | 95.9% | 77.7% | 92.5% |
| lgbm-item-bulk-ma52-focus-test-r1 | lgbm-item-bulk-ma52 | focus | 0.919 | 1.273 | 0.861 | -3.1% | 0.510 | 0.739 | 75.0% | 90.6% | 65.5% | 87.2% |
| lgbm-total-focus-test-r1 | lgbm-total | focus | 0.873 | 1.204 | 0.884 | 14.9% | 0.554 | 0.768 | 71.5% | 89.2% | 62.1% | 85.5% |
| lgbm-total-p1.8-focus-test-r1 | lgbm-total-p1.8 | focus | 0.842 | 1.165 | 0.870 | 17.2% | 0.539 | 0.746 | 70.9% | 88.9% | 61.4% | 85.0% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| naive-focus-test-r1 | +0.049 [-0.029, +0.123] | +0.192 [+0.081, +0.292] * | +0.155 [+0.102, +0.222] * |
| snaive-focus-test-r1 | +0.966 [+0.674, +1.276] * | +0.884 [+0.397, +1.420] * | +0.635 [+0.438, +0.847] * |
| ma4-focus-test-r1 | -0.016 [-0.091, +0.054] | +0.113 [-0.014, +0.243] | +0.114 [+0.060, +0.184] * |
| ma8-focus-test-r1 | +0.011 [-0.076, +0.100] | +0.176 [-0.005, +0.393] | +0.134 [+0.066, +0.224] * |
| ma13-focus-test-r1 | +0.060 [-0.043, +0.170] | +0.263 [+0.026, +0.545] * | +0.162 [+0.082, +0.269] * |
| croston-a0.1-focus-test-r1 | +0.566 [+0.342, +0.807] * | +0.591 [+0.316, +0.882] * | +0.268 [+0.162, +0.398] * |
| croston-a0.2-focus-test-r1 | +0.455 [+0.219, +0.726] * | +0.449 [+0.226, +0.689] * | +0.253 [+0.145, +0.384] * |
| sba-a0.1-focus-test-r1 | +0.536 [+0.319, +0.769] * | +0.578 [+0.300, +0.874] * | +0.267 [+0.160, +0.399] * |
| sba-a0.2-focus-test-r1 | +0.406 [+0.189, +0.654] * | +0.438 [+0.207, +0.683] * | +0.250 [+0.144, +0.379] * |
| tsb-a0.1-b0.1-focus-test-r1 | +0.123 [+0.024, +0.230] * | +0.292 [+0.064, +0.563] * | +0.162 [+0.079, +0.272] * |
| tsb-a0.2-b0.2-focus-test-r1 | +0.024 [-0.059, +0.108] | +0.169 [-0.005, +0.375] | +0.131 [+0.064, +0.219] * |
| split-ma4-bulk-0-focus-test-r1 | -0.041 [-0.130, +0.053] | +0.165 [-0.061, +0.415] | +0.123 [+0.057, +0.209] * |
| split-ma4-bulk-ma52-focus-test-r1 | +0.048 [-0.038, +0.128] | +0.154 [+0.007, +0.301] * | +0.111 [+0.050, +0.192] * |
| split-ma4-bulk-tsb-a0.1-b0.1-focus-test-r1 | +0.042 [-0.061, +0.169] | +0.108 [-0.027, +0.248] | +0.118 [+0.055, +0.202] * |
| split-tsb-a0.2-b0.2-bulk-ma52-focus-test-r1 | +0.107 [+0.011, +0.202] * | +0.233 [+0.055, +0.425] * | +0.139 [+0.066, +0.235] * |
| split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-test-r1 | +0.094 [-0.016, +0.226] | +0.180 [+0.010, +0.367] * | +0.143 [+0.068, +0.242] * |
| split-ma4-bulk-ma52-poolcat-focus-test-r1 | +0.048 [-0.038, +0.128] | +0.154 [+0.007, +0.301] * | +0.082 [+0.032, +0.145] * |
| topdown-ma4-bulk-ma52-focus-test-r1 | +0.330 [+0.221, +0.444] * | +0.338 [+0.216, +0.458] * | +0.172 [+0.109, +0.253] * |
| topdown-ma13-bulk-ma52-focus-test-r1 | +0.323 [+0.202, +0.446] * | +0.402 [+0.215, +0.597] * | +0.189 [+0.109, +0.298] * |
| ets-bulk-ma52-focus-test-r1 | +0.036 [-0.046, +0.106] | +0.108 [-0.006, +0.215] | +0.065 [+0.028, +0.101] * |
| arima-bulk-ma52-focus-test-r1 | +0.200 [+0.085, +0.328] * | +0.306 [+0.111, +0.509] * | +0.119 [+0.061, +0.190] * |
| lgbm-item-bulk-ma52-focus-test-r1 | +0.078 [+0.031, +0.124] * | +0.101 [+0.038, +0.160] * | +0.104 [+0.053, +0.165] * |
| lgbm-total-focus-test-r1 | +0.032 [+0.010, +0.064] * | +0.038 [+0.019, +0.057] * | +0.148 [+0.078, +0.229] * |
| lgbm-total-p1.8-focus-test-r1 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] | +0.133 [+0.074, +0.205] * |

## MASE per segment

| segment | series | best-crps-focus-test-r1 | naive-focus-test-r1 | snaive-focus-test-r1 | ma4-focus-test-r1 | ma8-focus-test-r1 | ma13-focus-test-r1 | croston-a0.1-focus-test-r1 | croston-a0.2-focus-test-r1 | sba-a0.1-focus-test-r1 | sba-a0.2-focus-test-r1 | tsb-a0.1-b0.1-focus-test-r1 | tsb-a0.2-b0.2-focus-test-r1 | split-ma4-bulk-0-focus-test-r1 | split-ma4-bulk-ma52-focus-test-r1 | split-ma4-bulk-tsb-a0.1-b0.1-focus-test-r1 | split-tsb-a0.2-b0.2-bulk-ma52-focus-test-r1 | split-tsb-a0.2-b0.2-bulk-tsb-a0.1-b0.1-focus-test-r1 | split-ma4-bulk-ma52-poolcat-focus-test-r1 | topdown-ma4-bulk-ma52-focus-test-r1 | topdown-ma13-bulk-ma52-focus-test-r1 | ets-bulk-ma52-focus-test-r1 | arima-bulk-ma52-focus-test-r1 | lgbm-item-bulk-ma52-focus-test-r1 | lgbm-total-focus-test-r1 | lgbm-total-p1.8-focus-test-r1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-intermittent | 16 | 0.784 | 0.947 | 1.467 | 0.807 | 0.776 | 0.767 | 0.923 | 0.911 | 0.902 | 0.871 | 0.754 | 0.757 | 0.729 | 0.820 | 0.770 | 0.808 | 0.755 | 0.820 | 0.943 | 0.896 | 0.816 | 0.841 | 0.814 | 0.776 | 0.784 |
| A-lumpy | 66 | 0.856 | 0.877 | 1.890 | 0.830 | 0.871 | 0.935 | 1.526 | 1.390 | 1.493 | 1.339 | 1.016 | 0.892 | 0.819 | 0.907 | 0.912 | 0.983 | 0.979 | 0.907 | 1.227 | 1.230 | 0.892 | 1.090 | 0.945 | 0.897 | 0.856 |
