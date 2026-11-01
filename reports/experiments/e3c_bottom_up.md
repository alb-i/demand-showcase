# E3c bottom-up (split ma4 + bulk ma52, full set) vs. direct category forecasts

Bottom-up = the summed mean forecasts of `split-ma4-bulk-ma52-full-r4`. MASE on the category totals (scale: naive error of each category series); lower = better.

| run (direct) | MASE direct | MASE bottom-up | categories direct better |
|---|---|---|---|
| split-ma4-bulk-ma52-category-r1 | 0.782 | 0.823 | 15 of 18 |
| naive-category-r1 | 0.848 | 0.823 | 7 of 18 |
| ma4-category-r1 | 0.759 | 0.823 | 12 of 18 |
| ma13-category-r1 | 1.028 | 0.823 | 3 of 18 |
| tsb-a0.2-b0.2-category-r1 | 0.867 | 0.823 | 7 of 18 |
| ets-bulk-ma52-category-r1 | 0.767 | 0.823 | 15 of 18 |
| arima-bulk-ma52-category-r1 | 0.823 | 0.823 | 10 of 18 |

## MASE per category

| category | bottom-up | split-ma4-bulk-ma52-category-r1 | naive-category-r1 | ma4-category-r1 | ma13-category-r1 | tsb-a0.2-b0.2-category-r1 | ets-bulk-ma52-category-r1 | arima-bulk-ma52-category-r1 |
|---|---|---|---|---|---|---|---|---|
| party_giftwrap | 0.386 | 0.362 | 0.433 | 0.365 | 0.335 | 0.322 | 0.374 | 0.419 |
| stationery_craft | 0.438 | 0.409 | 0.457 | 0.370 | 0.539 | 0.423 | 0.419 | 0.444 |
| kitchen_tableware | 0.537 | 0.499 | 0.644 | 0.523 | 0.558 | 0.528 | 0.524 | 0.510 |
| wall_decor | 0.564 | 0.539 | 0.703 | 0.595 | 0.724 | 0.615 | 0.554 | 0.528 |
| decorations | 0.604 | 0.575 | 0.730 | 0.536 | 0.917 | 0.690 | 0.597 | 0.801 |
| bags | 0.669 | 0.663 | 0.962 | 0.765 | 0.824 | 0.742 | 0.685 | 0.727 |
| jewellery | 0.699 | 0.694 | 0.616 | 0.573 | 0.891 | 0.724 | 0.786 | 1.006 |
| candles_lights | 0.704 | 0.642 | 0.610 | 0.514 | 0.845 | 0.669 | 0.671 | 0.973 |
| garden_outdoor | 0.768 | 0.760 | 1.055 | 0.838 | 0.820 | 0.801 | 0.778 | 0.746 |
| toys_games | 0.776 | 0.739 | 0.960 | 0.732 | 1.079 | 0.852 | 0.727 | 0.741 |
| storage | 0.808 | 0.769 | 0.929 | 0.714 | 0.993 | 0.830 | 0.777 | 0.780 |
| bath_beauty | 0.813 | 0.773 | 0.813 | 0.810 | 0.684 | 0.699 | 0.757 | 0.794 |
| accessories | 0.849 | 0.707 | 0.787 | 0.694 | 1.233 | 0.905 | 0.686 | 0.728 |
| other | 0.909 | 0.909 | 1.374 | 1.308 | 1.197 | 1.238 | 0.908 | 0.977 |
| furniture | 0.979 | 0.981 | 1.256 | 1.034 | 0.919 | 0.938 | 0.894 | 0.891 |
| textiles_cushions | 1.105 | 1.081 | 1.039 | 1.066 | 1.499 | 1.268 | 1.024 | 1.246 |
| christmas | 1.297 | 0.994 | 0.195 | 0.317 | 1.795 | 1.159 | 0.863 | 0.835 |
| easter | 1.910 | 1.979 | 1.699 | 1.914 | 2.650 | 2.208 | 1.780 | 1.663 |
