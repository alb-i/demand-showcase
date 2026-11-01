# Segments

Data version `ae898752`; weeks before 2011-06-06 (first test origin). 4144 products with demand in at least 2 weeks of that period, 13,231,898 GBP; left out: 162 products with demand in a single week, 10,166 GBP (0.08%).

**Focus set**: 748 products (A with >= 52 active weeks), 68.8% of revenue. Listed in configs/backtest.yaml (`focus_set`).

## ABC (revenue)

| ABC | products | revenue_share | focus_products | focus_revenue_share |
|---|---|---|---|---|
| A | 952 | 80.0% | 748 | 68.8% |
| B | 1145 | 15.0% | 0 | 0.0% |
| C | 2047 | 5.0% | 0 | 0.0% |

## ABC x XYZ (revenue share; products in brackets)

| ABC | X | Y | Z |
|---|---|---|---|
| A | 22.9% (171) | 44.6% (583) | 12.5% (198) |
| B | 1.5% (110) | 8.7% (651) | 4.8% (384) |
| C | 0.9% (658) | 2.6% (979) | 1.5% (410) |

## Syntetos-Boylan classes (ADI 1.32, CV^2 0.49)

ADI and CV^2 ignore 20,569 lines with more than 10x the product's median line quantity (36.7% of the units, 2741 products). The class on all lines is `sb_class_all` in segments.csv.

Products per class, all lines (rows) vs. without large orders (columns):

| all lines \ without large | smooth | erratic | intermittent | lumpy |
|---|---|---|---|---|
| smooth | 280 | 4 | 0 | 1 |
| erratic | 336 | 1000 | 9 | 41 |
| intermittent | 0 | 0 | 487 | 2 |
| lumpy | 0 | 0 | 196 | 1788 |

On all lines:

| Syntetos-Boylan (all lines) | products | revenue_share | focus_products | focus_revenue_share |
|---|---|---|---|---|
| smooth | 285 | 19.6% | 88 | 16.3% |
| erratic | 1386 | 61.6% | 581 | 47.5% |
| intermittent | 489 | 1.3% | 5 | 0.4% |
| lumpy | 1984 | 17.5% | 74 | 4.6% |

Without large orders:

| Syntetos-Boylan | products | revenue_share | focus_products | focus_revenue_share |
|---|---|---|---|---|
| smooth | 616 | 45.5% | 293 | 39.0% |
| erratic | 1004 | 35.1% | 373 | 24.6% |
| intermittent | 692 | 3.1% | 16 | 1.2% |
| lumpy | 1832 | 16.3% | 66 | 4.0% |

## Customer concentration

- One customer buys > 50 % of the units of 463 products (11.2%; focus set: 30), > 80 % of 134.
- Median top-customer share by Syntetos-Boylan class: smooth 13%, erratic 13%, intermittent 25%, lumpy 21%.
