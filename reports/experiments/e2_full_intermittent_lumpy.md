# E2 intermittent methods (full set, intermittent + lumpy, tuning origins)

Reference for the bootstrap: `ma4-full-r2`. Differences: mean over series of (run - reference), 95 % CI; * = significant; negative = better.

Only series of the Syntetos-Boylan classes: intermittent, lumpy.

| run | model | set | MASE | MASE w | RMSSE | bias | CRPS | CRPS w | cov 80 | cov 95 |
|---|---|---|---|---|---|---|---|---|---|---|
| ma4-full-r2 | ma4 | full | 0.718 | 0.545 | 1.969 | -11.3% | 0.510 | 0.355 | 87.6% | 96.7% |
| croston-a0.1-full-r1 | croston-a0.1 | full | 2.069 | 1.393 | 2.112 | -274.9% | 0.822 | 0.456 | 86.5% | 96.6% |
| croston-a0.2-full-r1 | croston-a0.2 | full | 1.781 | 1.202 | 2.056 | -242.3% | 0.732 | 0.443 | 86.0% | 96.7% |
| sba-a0.1-full-r1 | sba-a0.1 | full | 1.988 | 1.336 | 2.095 | -256.1% | 0.803 | 0.451 | 86.5% | 96.6% |
| sba-a0.2-full-r1 | sba-a0.2 | full | 1.647 | 1.108 | 2.034 | -208.0% | 0.704 | 0.433 | 86.0% | 96.7% |
| tsb-a0.1-b0.1-full-r1 | tsb-a0.1-b0.1 | full | 0.850 | 0.997 | 1.957 | -105.0% | 0.466 | 0.395 | 90.6% | 97.9% |
| tsb-a0.2-b0.2-full-r1 | tsb-a0.2-b0.2 | full | 0.763 | 0.755 | 1.955 | -59.1% | 0.474 | 0.372 | 88.9% | 97.2% |

## Paired bootstrap vs. the reference

| run | MASE diff | MASE w diff | CRPS diff |
|---|---|---|---|
| croston-a0.1-full-r1 | +1.343 [+1.219, +1.467] * | +0.857 [+0.733, +0.979] * | +0.308 [+0.240, +0.382] * |
| croston-a0.2-full-r1 | +1.057 [+0.962, +1.154] * | +0.664 [+0.569, +0.761] * | +0.220 [+0.170, +0.272] * |
| sba-a0.1-full-r1 | +1.261 [+1.144, +1.380] * | +0.800 [+0.681, +0.916] * | +0.290 [+0.225, +0.360] * |
| sba-a0.2-full-r1 | +0.923 [+0.837, +1.011] * | +0.570 [+0.483, +0.656] * | +0.191 [+0.147, +0.239] * |
| tsb-a0.1-b0.1-full-r1 | +0.132 [+0.117, +0.146] * | +0.453 [+0.352, +0.560] * | -0.043 [-0.051, -0.036] * |
| tsb-a0.2-b0.2-full-r1 | +0.046 [+0.037, +0.054] * | +0.211 [+0.152, +0.277] * | -0.036 [-0.041, -0.031] * |

## MASE per segment

| segment | series | ma4-full-r2 | croston-a0.1-full-r1 | croston-a0.2-full-r1 | sba-a0.1-full-r1 | sba-a0.2-full-r1 | tsb-a0.1-b0.1-full-r1 | tsb-a0.2-b0.2-full-r1 |
|---|---|---|---|---|---|---|---|---|
| A-intermittent | 26 | 0.681 | 1.430 | 1.267 | 1.378 | 1.179 | 0.902 | 0.717 |
| A-lumpy | 114 | 0.624 | 1.806 | 1.573 | 1.735 | 1.455 | 1.205 | 0.900 |
| B-intermittent | 61 | 0.513 | 1.051 | 0.945 | 1.013 | 0.879 | 0.615 | 0.543 |
| B-lumpy | 530 | 0.716 | 1.215 | 1.142 | 1.175 | 1.068 | 0.888 | 0.785 |
| C-intermittent | 605 | 0.729 | 3.418 | 2.856 | 3.272 | 2.620 | 0.843 | 0.768 |
| C-lumpy | 1188 | 0.734 | 1.870 | 1.604 | 1.798 | 1.488 | 0.813 | 0.751 |
