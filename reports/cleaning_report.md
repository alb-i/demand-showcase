# Cleaning report — variant `main`

Data version `ae898752` (cleaning config + commit `f02aec0`).

| Step | Lines | Units | Revenue (£) |
|---|---:|---:|---:|
| Raw (both sheets) | 1 067 371 | 10 608 492 | 19 287 251 |
| R1 sheet overlap | 22 523 | 166 648 | 377 488 |
| R2 duplicate lines | 0 | 0 | 0 |
| R4 non-product codes | 5 832 | 10 438 | -71 536 |
| R5 adjustments (price/quantity) | 5 972 | -320 653 | 0 |
| R6 order corrections | 5 130 | 0 | 38 350 |
| R7 bulk orders (reviewed) | 0 | 0 | 0 |
| R8 incomplete last week | 17 585 | 162 288 | 311 735 |
| R9 returns outside the active window | 293 | -2 450 | -8 727 |
| Demand (panel units) | 995 125 | 10 805 429 | 18 932 649 |
| Returns (panel returned_units) | 14 911 | -213 208 | -292 709 |

Reconciliation (raw = removals + demand + returns, lines, units and revenue): **OK**.

- Demand in the panel: 10 805 429 units, £18 932 649 (lines: 10 805 429 units, £18 932 649).
- Returns in the panel (`returned_units`): 213 208 units, £292 709 = 1.5% of demand revenue.
- Panel: 4718 SKUs, 2009-11-30 to 2011-11-28 (105 weeks), 319964 rows (5952 in closed weeks); dropped incomplete week 2011-12-05.
- Closed weeks: 2009-12-28, 2010-12-27.
- Stock codes with more than one description: 598 of 4718 (canonical = most frequent, reports/descriptions.csv).

| Cancellations (C...) went to | Lines | Revenue (£) |
|---|---:|---:|
| R4 non-product codes | 1 192 | -745 647 |
| R6 order corrections | 2 565 | -414 464 |
| return | 14 911 | -292 709 |
| R1 sheet overlap | 329 | -61 364 |
| R9 returns outside the active window | 293 | -8 727 |
| R8 incomplete last week | 204 | -3 757 |
| all | 19 494 | -1 526 668 |
