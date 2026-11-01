"""EDA figures and notes.

    micromamba run -n demand-showcase python scripts/explore.py

Run scripts/segment.py first (segments.parquet). Writes reports/figures/*.png, the same as
*.pdf for reports/report.tex, and reports/eda.md.
The aggregate figures show the whole period with the test origins shaded; the segment figures
use the weeks before the first test origin only.
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from retail.eda import (  # noqa: E402
    life_cycle,
    new_product_share,
    season_profile,
    weekday_shares,
    weekly_totals,
)
from retail.io import REPO_DIR, data_dir  # noqa: E402
from retail.segments import SB_CLASSES, customer_order_mix  # noqa: E402

FIG = REPO_DIR / "reports" / "figures"
BURN_IN_WEEKS = 13  # products first sold in the first quarter count as "existing at the start"

# Reference palette (dataviz skill, light mode): categorical slots in fixed order
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, SURFACE, BAND = "#e1e0d9", "#c3c2b7", "#fcfcfb", "#f0efec"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "axes.edgecolor": AXIS,
        "axes.labelcolor": INK2,
        "axes.titlecolor": INK,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlelocation": "left",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 0.6,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK2,
        "ytick.labelcolor": INK2,
        "font.size": 10,
        "lines.linewidth": 1.6,
        "legend.frameon": False,
        "legend.labelcolor": INK2,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
    }
)


def save(fig, name: str) -> None:
    """PNG for the markdown reports and the README, PDF (vector, no date) for report.tex."""
    fig.savefig(FIG / f"{name}.png")
    fig.savefig(FIG / f"{name}.pdf", metadata={"CreationDate": None, "ModDate": None})


def shade(ax, test, closed_weeks):
    ax.axvspan(*test, color=BAND, zorder=0, lw=0)
    for w in closed_weeks:
        ax.axvline(w + pd.Timedelta(days=3), color=AXIS, lw=0.8, ls=":", zorder=1)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))


def thousands(ax, unit=""):
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{unit}{v / 1e3:,.0f}k"))


def fig_weekly(tot, test, closed):
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    for ax, col, title, unit in [
        (axes[0], "units", "Weekly demand (units)", ""),
        (axes[1], "revenue", "Weekly revenue (GBP)", "£"),
    ]:
        ax.plot(tot.index, tot[col], color=SERIES[0])
        ax.set_title(title)
        thousands(ax, unit)
        ax.set_ylim(bottom=0)
        shade(ax, test, closed)
    axes[0].text(test[0], axes[0].get_ylim()[1], " test origins", va="top", color=MUTED)
    axes[1].text(closed[0], axes[1].get_ylim()[1], " closed (Christmas)", color=MUTED, va="top")
    save(fig, "weekly_totals")
    plt.close(fig)


def fig_season(prof):
    fig, ax = plt.subplots(figsize=(10, 4))
    for i, year in enumerate([2010, 2011]):
        ax.plot(prof.index, prof[year], color=SERIES[i], label=str(year))
        last = prof[year].dropna()
        ax.text(last.index[-1] + 0.5, last.iloc[-1], str(year), color=INK2, va="center")
    ax.set_title("Weekly units by ISO week of year")
    ax.set_xlabel("ISO week")
    thousands(ax)
    ax.set_ylim(bottom=0)
    ax.legend(loc="upper left")
    save(fig, "seasonality")
    plt.close(fig)


def fig_weekday(wd):
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(wd.index, wd["revenue"], color=SERIES[0], width=0.6)
    ax.set_title("Share of revenue by weekday")
    ax.yaxis.set_major_locator(plt.MultipleLocator(0.05))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.grid(axis="x", visible=False)
    for x, v in zip(wd.index, wd["revenue"], strict=True):
        ax.text(x, v, f"{v:.0%}", ha="center", va="bottom", color=INK2, fontsize=9)
    save(fig, "weekday")
    plt.close(fig)


def fig_life_cycle(tot, lc, share, test, closed):
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    axes[0].plot(tot.index, tot["active_skus"], color=SERIES[0])
    axes[0].set_title("Products with demand in the week")
    launches = lc["first_week"].value_counts().sort_index()
    start = tot.index.min() + pd.Timedelta(weeks=BURN_IN_WEEKS)
    launches = launches[launches.index >= start]  # before: first seen, not launched
    axes[1].bar(launches.index, launches.to_numpy(), width=5, color=SERIES[0])
    axes[1].set_title(f"Products sold for the first time (after the first {BURN_IN_WEEKS} weeks)")
    axes[2].plot(share.index, share, color=SERIES[0])
    axes[2].set_title(f"Revenue share of products introduced after the first {BURN_IN_WEEKS} weeks")
    axes[2].yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    for ax in axes:
        ax.set_ylim(bottom=0)
        shade(ax, test, closed)
    save(fig, "life_cycle")
    plt.close(fig)


def fig_sb(seg, cfg):
    sb = cfg["syntetos_boylan"]
    fig, ax = plt.subplots(figsize=(7, 5))
    s = seg.dropna(subset=["sb_class"])
    for i, c in enumerate(SB_CLASSES):
        d = s[s["sb_class"] == c]
        ax.scatter(
            d["adi"], d["cv2"].clip(lower=1e-3), s=10, color=SERIES[i], alpha=0.6, lw=0,
            label=f"{c} ({len(d)})",
        )  # fmt: skip
    ax.axvline(sb["adi"], color=MUTED, lw=1)
    ax.axhline(sb["cv2"], color=MUTED, lw=1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("ADI (active weeks / weeks with demand)")
    ax.set_ylabel("CV² of non-zero weekly units")
    title = f"Syntetos-Boylan classes (weeks before {cfg['before']})"
    if sb.get("max_order_ratio"):
        title += f"\nwithout lines > {sb['max_order_ratio']}x the product's median quantity"
    ax.set_title(title)
    ax.text(1.01, 1e-3, "CV² = 0", color=MUTED, va="center", transform=ax.get_yaxis_transform())
    ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), markerscale=2)
    save(fig, "syntetos_boylan")
    plt.close(fig)


def fig_concentration(seg):
    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.linspace(0, 1, 21)
    ax.hist(seg["top_customer_share"], bins=bins, color=SERIES[0], rwidth=0.9)
    ax.set_title("Share of units bought by the largest customer, per product")
    ax.set_xlabel("top-customer share of units (weeks before the first test origin)")
    ax.set_ylabel("products")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.grid(axis="x", visible=False)
    save(fig, "customer_concentration")
    plt.close(fig)


def fig_customer_mix(mix, ratio, before):
    """Item vs bulk lines per customer (log axes; 0 drawn on its own strip, jittered), and the
    bulk share of each customer's units."""
    rng = np.random.default_rng(0)
    bulky = mix["bulk_unit_share"] > 0.5

    def pos(n):  # 0 -> 0.5 on the log axis, small jitter so integer counts do not stack
        return np.where(n > 0, n, 0.5) * np.exp(rng.uniform(-0.12, 0.12, len(n)))

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [3, 2]})
    ax = axes[0]
    for i, (mask, label) in enumerate(
        [(~bulky, "mostly item sales"), (bulky, "mostly bulk sales (> 50 % of units)")]
    ):
        d = mix[mask]
        ax.scatter(
            pos(d["item_lines"]), pos(d["bulk_lines"]), s=9, lw=0, alpha=0.55,
            color=SERIES[i], label=f"{label} ({len(d):,})",
        )  # fmt: skip
    ax.set_xscale("log")
    ax.set_yscale("log")
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_locator(plt.FixedLocator([0.5, 1, 10, 100, 1000, 10000]))
        axis.set_major_formatter(plt.FixedFormatter(["0", "1", "10", "100", "1k", "10k"]))
    ax.axhline(0.75, color=AXIS, lw=0.8)
    ax.axvline(0.75, color=AXIS, lw=0.8)
    ax.set_xlabel(
        f"item sales (lines)\nbulk = quantity > {ratio}x the product's median line quantity"
    )
    ax.set_ylabel("bulk sales (lines)")
    ax.set_title(f"Bulk vs item sales per customer (lines before {before})")
    ax.legend(loc="upper left", markerscale=2)

    ax = axes[1]
    has_bulk = mix[mix["bulk_lines"] > 0]
    ax.hist(has_bulk["bulk_unit_share"], bins=np.linspace(0, 1, 21), color=SERIES[0], rwidth=0.9)
    ax.set_title("Bulk share of the units, per customer")
    ax.set_xlabel(
        f"customers with any bulk sale ({len(has_bulk):,}; {len(mix) - len(has_bulk):,} have none)"
    )
    ax.set_ylabel("customers")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.grid(axis="x", visible=False)
    save(fig, "customer_bulk_vs_item")
    plt.close(fig)


def main() -> None:
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    cfg = bt["segments"]
    processed = data_dir() / "processed"
    panel = pd.read_parquet(processed / "panel_weekly.parquet")
    sales = pd.read_parquet(processed / "sales_clean.parquet")
    seg = pd.read_parquet(processed / "segments.parquet")
    meta = json.loads((processed / "panel_meta.json").read_text())
    FIG.mkdir(parents=True, exist_ok=True)

    tot = weekly_totals(panel)
    test = (pd.Timestamp(bt["origins"]["test"]["from"]), tot.index.max())
    closed = list(tot.index[tot["closed"]])
    prof = season_profile(tot)
    wd = weekday_shares(sales)
    lc = life_cycle(panel)
    share = new_product_share(panel, BURN_IN_WEEKS)

    fig_weekly(tot, test, closed)
    fig_season(prof)
    fig_weekday(wd)
    fig_life_cycle(tot, lc, share, test, closed)
    fig_sb(seg, cfg)
    fig_concentration(seg)
    ratio = cfg["syntetos_boylan"]["max_order_ratio"]
    in_seg = sales["stock_code"].isin(seg["stock_code"])  # same products as the segments
    mix = customer_order_mix(sales[in_seg], cfg["before"], ratio)
    fig_customer_mix(mix, ratio, cfg["before"])
    bulky, bulk_u = mix["bulk_unit_share"] > 0.5, mix["bulk_units"].sum()

    rev_month = tot["revenue"].groupby(tot.index.to_period("M")).sum()
    y10 = rev_month[rev_month.index.year == 2010]
    q4 = y10[y10.index.month >= 9].sum() / y10.sum()
    peak = tot["units"].idxmax()
    open_tot = tot[~tot["closed"]]
    start = tot.index.min() + pd.Timedelta(weeks=BURN_IN_WEEKS)
    new_rev = panel.loc[panel["stock_code"].map(lc["first_week"] >= start), "revenue"].sum()
    gone = (lc["last_week"] < tot.index.max() - pd.Timedelta(weeks=12)).sum()
    lines = [
        "# Exploration",
        "",
        f"Data version `{meta['data_version']}`. Figures in `reports/figures/`; aggregate "
        "figures cover all weeks (test origins shaded), segment figures only the weeks before "
        f"{cfg['before']}.",
        "",
        "## Totals and seasonality (`weekly_totals.png`, `seasonality.png`)",
        "",
        f"- Peak week {peak.date()} with {tot['units'].max():,.0f} units; median open week "
        f"{open_tot['units'].median():,.0f} units, £{open_tot['revenue'].median():,.0f}.",
        f"- Sep-Dec 2010 bring {q4:.0%} of the 2010 revenue (strong autumn build-up for "
        "giftware, peak in November).",
        f"- Closed weeks: {', '.join(str(w.date()) for w in closed)} (Christmas); missing, not 0.",
        "",
        "## Weekday (`weekday.png`)",
        "",
        "- Revenue share: "
        + ", ".join(f"{d} {v:.1%}" for d, v in wd["revenue"].items())
        + ". Saturday is (almost) never traded; weekly buckets hide the weekday pattern.",
        "",
        "## Life cycle (`life_cycle.png`)",
        "",
        f"- {len(lc)} products; products with demand per open week: median "
        f"{open_tot['active_skus'].median():.0f} (min {open_tot['active_skus'].min():.0f}, "
        f"max {open_tot['active_skus'].max():.0f}).",
        f"- {(lc['first_week'] >= start).sum()} products first sold after the first "
        f"{BURN_IN_WEEKS} weeks bring {new_rev / panel['revenue'].sum():.1%} of all revenue; "
        f"their weekly share rises to {share.max():.0%}.",
        f"- {gone} products have no sale in the last 12 weeks (discontinued or dormant).",
        "",
        "## Segments and concentration (`syntetos_boylan.png`, `customer_concentration.png`)",
        "",
        "See `reports/segments.md` (class tables, focus set).",
        "",
        "## Bulk and item customers (`customer_bulk_vs_item.png`)",
        "",
        f"Sale lines before {cfg['before']}; bulk = quantity > {ratio}x the product's median "
        "line quantity (the bulk rule of the segments), item otherwise; lines without customer id "
        "and products with demand in a single week left out.",
        "",
        f"- {len(mix):,} customers: {(mix['bulk_lines'] == 0).sum():,} never buy in bulk, "
        f"{(mix['item_lines'] == 0).sum()} only in bulk; "
        f"{(mix['bulk_unit_share'] > 0.5).sum()} get > 50 % of their units from bulk lines.",
        f"- Those {bulky.sum()} customers buy {mix.loc[bulky, 'bulk_units'].sum() / bulk_u:.0%} "
        f"of all bulk units; bulk is {bulk_u / (bulk_u + mix['item_units'].sum()):.0%} of the "
        "units of customers with an id.",
        "",
    ]
    (REPO_DIR / "reports" / "eda.md").write_text("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
