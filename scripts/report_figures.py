"""Result figures of the technical report (reports/report.tex), from the E9 test runs.

    micromamba run -n demand-showcase python scripts/report_figures.py \
        [fan sums calibration models costs]

Reads the newest finished test runs in $RUNS_DIR (E9, P5 simulations) and the panel; writes
vector PDFs (no date) and PNGs (README) to reports/figures/: models_test, calibration_test,
horizon_sums_test, fan_chart, costs_test (total cost at the operating points, README),
costs_client (the same for the one-pager).
The EDA figures (weekly_totals, syntetos_boylan, ...) come from scripts/explore.py.
"""

import json
import re
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402
from explore import AXIS, INK2, MUTED, SERIES  # noqa: E402  (style and palette, rcParams)

from retail.compare import load_run, summary  # noqa: E402
from retail.io import REPO_DIR, data_dir  # noqa: E402
from retail.metrics import qcol  # noqa: E402
from retail.paths import overstatement  # noqa: E402
from retail.report import FAMILIES, family, hit_curve  # noqa: E402
from retail.runlog import runs_dir  # noqa: E402

FIG = REPO_DIR / "reports" / "figures"
COLORS = SERIES + ["#e87ba4"]  # categorical slots 1-5 in fixed order (one per family)
MARKERS = ["o", "s", "^", "D", "P"]
# labelled points: run name -> (label, offset in points on the focus / full panel)
LABELS = {"snaive": ("seasonal naive", (-30, 6), (-30, 6)), "naive": ("naive", (6, 0), (6, 0)),
          "ma4": ("MA(4)", (6, 4), (-34, -2)), "ets-bulk-ma52": ("ETS", (-22, -10), (4, 4)),
          "split-ma4-bulk-ma52": ("MA(4) item + MA(52) bulk", (6, -2), (8, -6)),
          "lgbm-total-q-p1.8": ("LightGBM quantiles", (6, -4), (6, -4))}  # fmt: skip
LIMITS = {"focus": None, "full": ((0.6, 1.3), (0.4, 0.8))}  # full: Croston/SBA off scale
FAN_ORIGIN = pd.Timestamp("2011-09-05")


def save(fig, name: str) -> None:
    fig.savefig(FIG / f"{name}.pdf", metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(FIG / f"{name}.png")
    plt.close(fig)


def models_with_test_runs(set_: str) -> list[str]:
    """Model names with a finished plain test run on set_ (no composites, sums, calibration)."""
    names = set()
    for d in runs_dir().iterdir():
        m = re.fullmatch(rf"\d{{8}}-\d{{6}}-(.+)-{set_}-test", d.name)
        if not m or not (d / "meta.json").exists():
            continue
        if json.loads((d / "meta.json").read_text()).get("status") != "finished":
            continue
        cfg = yaml.safe_load((d / "config.yaml").read_text()) or {}
        if {"calibration", "horizon_sums", "selection", "simulation"} & set(cfg):
            continue
        names.add(m.group(1))
    return sorted(names)


def rows_of(name: str) -> pd.DataFrame:
    _, path, _ = load_run(f"latest:{name}")
    return pd.read_parquet(path / "rows.parquet")


def fig_models(q, lv):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for ax, set_ in zip(axes, ["focus", "full"], strict=True):
        pts = []
        for n in models_with_test_runs(set_):
            s = summary(rows_of(f"{n}-{set_}-test"), q, lv).iloc[0]
            pts.append((n, s["mase"], s["crps"]))
            print(f"{set_} {n}: MASE {s['mase']:.3f} CRPS {s['crps']:.3f}")
        for i, fam in enumerate(FAMILIES):
            p = [x for x in pts if family(x[0]) == fam]
            ax.scatter([x[1] for x in p], [x[2] for x in p], s=44, color=COLORS[i],
                       marker=MARKERS[i], edgecolor="white", lw=0.8, label=fam,
                       zorder=3)  # fmt: skip
        for n, x, y in pts:
            if n in LABELS:
                text, *offs = LABELS[n]
                ax.annotate(text, (x, y), xytext=offs[set_ == "full"],
                            textcoords="offset points", fontsize=7.5, color=INK2)  # fmt: skip
        if LIMITS[set_]:
            (x0, x1), (y0, y1) = LIMITS[set_]
            out = [x for x in pts if not (x0 <= x[1] <= x1 and y0 <= x[2] <= y1)]
            ax.set_xlim(x0, x1)
            ax.set_ylim(y0, y1)
            if out:
                ax.text(0.02, 0.97, f"off scale: {len(out)} Croston / SBA models\n(MASE "
                        f"{min(x[1] for x in out):.1f}-{max(x[1] for x in out):.1f}, CRPS "
                        f"{min(x[2] for x in out):.2f}-{max(x[2] for x in out):.2f})",
                        transform=ax.transAxes, va="top", fontsize=7.5, color=MUTED)  # fmt: skip
        ax.set_title(f"{set_} set ({len(pts)} models)")
        ax.set_xlabel("MASE (lower is better)")
        ax.set_ylabel("CRPS (scaled, lower is better)")
    axes[1].legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), fontsize=8)
    fig.tight_layout()
    save(fig, "models_test")


def fig_calibration(q):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    for ax, set_ in zip(axes, ["focus", "full"], strict=True):
        ax.plot([0, 1], [0, 1], color=AXIS, lw=1, zorder=1)
        for name, col, ls, label in [
            ("lgbm-total-q-p1.8", "rhit", "-", "LightGBM quantiles, randomised PIT"),
            ("lgbm-total-q-p1.8", "hit", "--", "LightGBM quantiles, share y ≤ q"),
            ("ma4", "rhit", "-", "MA(4) + empirical residuals, randomised PIT"),
        ]:  # fmt: skip
            h = hit_curve(rows_of(f"{name}-{set_}-test"), q)
            color = SERIES[0] if name.startswith("lgbm") else SERIES[1]
            ax.plot(h["tau"], h[col], ls=ls, color=color, marker="o", ms=4, label=label)
        ax.set_title(f"{set_} set, test origins")
        ax.set_xlabel("quantile level τ")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("share of outcomes below the τ-quantile")
    axes[1].legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    save(fig, "calibration_test")


def fig_horizon_sums(q):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.0), sharey=True)
    for ax, set_ in zip(axes, ["focus", "full"], strict=True):
        s = rows_of(f"best-crps-sum-summed-{set_}-test")
        p = rows_of(f"best-crps-sum-paths-ct-{set_}-test")
        r = overstatement(s, p, q)
        r = r[r["tau"] >= 0.5]
        ax.axhline(1, color=AXIS, lw=1)
        for i, (k, g) in enumerate(r.groupby("K")):
            ax.plot(g["tau"], g["weighted_ratio"], color=SERIES[i], marker="o", ms=4,
                    label=f"K = {k} weeks")  # fmt: skip
            ax.text(g["tau"].iloc[-1] + 0.006, g["weighted_ratio"].iloc[-1], f"K = {k}",
                    color=INK2, va="center", fontsize=8)  # fmt: skip
        ax.set_title(f"{set_} set, test origins")
        ax.set_xlabel("quantile level τ")
        ax.set_xlim(0.48, 1.04)
    axes[0].set_ylabel("Σ weekly quantiles / quantile of the sum")
    axes[0].legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    save(fig, "horizon_sums_test")


def fig_fan(codes: list[str]):
    panel = pd.read_parquet(data_dir() / "processed" / "panel_weekly.parquet")
    _, path, _ = load_run("latest:lgbm-total-q-p1.8-focus-test")
    fc = pd.read_parquet(path / "forecasts.parquet")
    fig, axes = plt.subplots(len(codes), 1, figsize=(10, 3.0 * len(codes)))
    for ax, code in zip(axes, codes, strict=True):
        hist = panel[(panel["stock_code"] == code) & (panel["week"] >= "2011-01-03")]
        hist = hist.set_index("week").sort_index()
        f = fc[(fc["stock_code"] == code) & (fc["origin"] == FAN_ORIGIN)].sort_values("h")
        weeks = FAN_ORIGIN + pd.to_timedelta((f["h"] - 1) * 7, unit="D")
        ax.fill_between(weeks, f[qcol(0.025)], f[qcol(0.975)], color=SERIES[0], alpha=0.15,
                        lw=0, label="95 % interval")  # fmt: skip
        ax.fill_between(weeks, f[qcol(0.1)], f[qcol(0.9)], color=SERIES[0], alpha=0.3, lw=0,
                        label="80 % interval")  # fmt: skip
        ax.plot(weeks, f[qcol(0.5)], color=SERIES[0], label="median forecast")
        ax.plot(hist.index, hist["units"], color=INK2, lw=1.2, marker="o", ms=2.5,
                label="weekly demand")  # fmt: skip
        ax.axvline(FAN_ORIGIN - pd.Timedelta(days=3.5), color=MUTED, lw=0.8, ls=":")
        ax.set_title(f"{code} {hist['description'].iloc[0].title()}")
        ax.set_ylabel("units")
        ax.set_ylim(bottom=0)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    axes[0].legend(loc="upper left", fontsize=8, ncol=4)
    fig.tight_layout()
    save(fig, "fan_chart")


def operating_costs(leads=(1, 2, 4), reference: float = 1.0) -> pd.DataFrame:
    """Per L the test-week totals at base costs of P-naive (reference buffer) and of P-normal and
    P-quantile at their operating points (configs/operating_point.yaml)."""
    from policy_report import base_grid, sim_run  # scripts/policy_report.py

    from retail.inventory.costs import load_costs

    costs, _ = load_costs()
    op = yaml.safe_load((REPO_DIR / "configs" / "operating_point.yaml").read_text())
    out = []
    for lead in leads:
        _, m, _ = sim_run(lead, "test")
        g = base_grid(m, costs)
        point = next(p for p in op["lead_time"][lead]["points"]
                     if p["naive"]["buffer"] == reference)  # fmt: skip
        for pol, key in (("naive", "buffer"), ("normal", "alpha"), ("quantile", "tau")):
            r = g[(g["policy"] == pol) & (g["value"] == point[pol][key])].iloc[0]
            out.append({"L": lead, "policy": pol, "value": point[pol][key],
                        "holding": r["holding_cost"], "lost": r["lost_margin"],
                        "total": r["total_cost"], "fill_rate": r["fill_rate"]})  # fmt: skip
    return pd.DataFrame(out)


def fig_costs(t: pd.DataFrame):
    names = {"naive": "P-naive (4-week mean + 100 %)", "normal": "P-normal",
             "quantile": "P-quantile (forecast paths)"}  # fmt: skip
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    leads = sorted(t["L"].unique())
    width = 0.26
    for i, pol in enumerate(["naive", "normal", "quantile"]):
        p = t[t["policy"] == pol].set_index("L").loc[leads]
        x = [k + (i - 1) * width for k in range(len(leads))]
        ax.bar(x, p["lost"] / 1e3, width - 0.03, color=SERIES[i], label=names[pol])
        ax.bar(x, p["holding"] / 1e3, width - 0.03, bottom=p["lost"] / 1e3, color=SERIES[i],
               alpha=0.4)  # fmt: skip
        for xi, (_, r) in zip(x, p.iterrows(), strict=True):
            ax.text(xi, r["total"] / 1e3 * 1.015, f"£{r['total'] / 1e3:.0f}k\n{r['fill_rate']:.0%}",
                    ha="center", va="bottom", fontsize=7, color=INK2)  # fmt: skip
    ax.set_xticks(range(len(leads)), [f"lead time {k} week{'s' if k > 1 else ''}" for k in leads])
    ax.set_ylabel("total cost, 26 test weeks (£ thousand)")
    ax.set_ylim(0, t["total"].max() / 1e3 * 1.25)
    ax.set_title("Cost at the pre-fixed operating points (label: total, fill rate)\n"
                 "dark: lost margin, light: holding cost", fontsize=10)  # fmt: skip
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=3, fontsize=8, frameon=False)
    fig.tight_layout()
    save(fig, "costs_test")


def fig_costs_client(t: pd.DataFrame):
    """The one-pager version (no formulas): rule of thumb vs. forecast-based, total only."""
    names = {"naive": "rule of thumb: 4-week average + 100 %",
             "quantile": "forecast-based ordering"}  # fmt: skip
    fig, ax = plt.subplots(figsize=(4.6, 3.3))
    leads = sorted(t["L"].unique())
    width = 0.38
    for i, pol in enumerate(["naive", "quantile"]):
        p = t[t["policy"] == pol].set_index("L").loc[leads]
        x = [k + (i - 0.5) * width for k in range(len(leads))]
        ax.bar(x, p["total"] / 1e3, width - 0.04, color=SERIES[0 if pol == "naive" else 2],
               label=names[pol])  # fmt: skip
        for xi, (_, r) in zip(x, p.iterrows(), strict=True):
            ax.text(xi, r["total"] / 1e3 * 1.015, f"£{r['total'] / 1e3:.0f}k",
                    ha="center", va="bottom", fontsize=8, color=INK2)  # fmt: skip
    ax.set_xticks(range(len(leads)), [f"{k} week{'s' if k > 1 else ''}" for k in leads])
    ax.set_xlabel("delivery time")
    ax.set_ylabel("cost over six months (£ thousand)")
    ax.set_ylim(0, t["total"].max() / 1e3 * 1.3)
    ax.set_title("Missed margin + holding cost, 748 products", fontsize=9)
    ax.legend(loc="upper left", fontsize=7.5, frameon=False)
    fig.tight_layout()
    save(fig, "costs_client")


def main() -> None:
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    q, lv = bt["quantiles"], bt["intervals"]
    FIG.mkdir(parents=True, exist_ok=True)
    seg = pd.read_parquet(data_dir() / "processed" / "segments.parquet")
    focus = seg[seg["focus"]].sort_values("revenue", ascending=False)
    smooth = focus[focus["sb_class"] == "smooth"]["stock_code"].iloc[0]
    lumpy = focus[focus["sb_class"] == "lumpy"]["stock_code"].iloc[0]
    figs = sys.argv[1:] or ["fan", "sums", "calibration", "models", "costs"]
    if "fan" in figs:
        fig_fan([smooth, lumpy])
    if "sums" in figs:
        fig_horizon_sums(q)
    if "calibration" in figs:
        fig_calibration(q)
    if "models" in figs:
        fig_models(q, lv)
    if "costs" in figs:
        t = operating_costs()
        fig_costs(t)
        fig_costs_client(t)


if __name__ == "__main__":
    main()
