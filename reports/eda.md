# Exploration

Data version `ae898752`. Figures in `reports/figures/`; aggregate figures cover all weeks (test origins shaded), segment figures only the weeks before 2011-06-06.

## Totals and seasonality (`weekly_totals.png`, `seasonality.png`)

- Peak week 2010-09-27 with 235,317 units; median open week 97,250 units, £162,973.
- Sep-Dec 2010 bring 43% of the 2010 revenue (strong autumn build-up for giftware, peak in November).
- Closed weeks: 2009-12-28, 2010-12-27 (Christmas); missing, not 0.

## Weekday (`weekday.png`)

- Revenue share: Mon 17.5%, Tue 19.7%, Wed 17.4%, Thu 20.5%, Fri 15.3%, Sat 0.1%, Sun 9.5%. Saturday is (almost) never traded; weekly buckets hide the weekday pattern.

## Life cycle (`life_cycle.png`)

- 4718 products; products with demand per open week: median 1836 (min 1316, max 2383).
- 1373 products first sold after the first 13 weeks bring 32.9% of all revenue; their weekly share rises to 62%.
- 1567 products have no sale in the last 12 weeks (discontinued or dormant).

## Segments and concentration (`syntetos_boylan.png`, `customer_concentration.png`)

See `reports/segments.md` (class tables, focus set).

## Bulk and item customers (`customer_bulk_vs_item.png`)

Sale lines before 2011-06-06; bulk = quantity > 10x the product's median line quantity (the bulk rule of the segments), item otherwise; lines without customer id and products with demand in a single week left out.

- 4,922 customers: 2,880 never buy in bulk, 72 only in bulk; 368 get > 50 % of their units from bulk lines.
- Those 368 customers buy 82% of all bulk units; bulk is 38% of the units of customers with an id.
