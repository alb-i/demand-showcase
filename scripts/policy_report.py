"""Operating points and reports of the inventory simulation.

    micromamba run -n demand-showcase python scripts/policy_report.py select [--lead-time 1 2 4]
    micromamba run -n demand-showcase python scripts/policy_report.py report \
        --origins tuning|test [--lead-time 1 2 4]

select (tuning runs sim-L<L>-focus): per L and reference P-naive (buffers
policies.naive.reference_buffers: 0 and 1.0), for P-quantile and P-normal the smallest
grid value whose tuning fill rate is >= the reference's;
written to configs/operating_point.yaml (commit it before the test simulation).
report: per L the grid at base costs (fill rate, cycle service level, stock-out weeks, average
stock value, costs), the operating points of configs/operating_point.yaml against P-naive
(paired bootstrap over products), the stock value at the reference's fill rate interpolated
along each frontier, the sensitivity (margin x holding rate, lead time, write-down share) and
the frontier figure -> reports/experiments/p5_<origins>.md, reports/figures/
p5_frontier_<origins>.pdf/.png.
"""

import argparse
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402
from explore import INK2, MUTED, SERIES  # noqa: E402  (style and palette)

from retail.compare import load_run  # noqa: E402
from retail.inventory.costs import load_costs  # noqa: E402
from retail.inventory.frontier import at_fill_rate, bootstrap_totals, match  # noqa: E402
from retail.io import REPO_DIR  # noqa: E402

OP = REPO_DIR / "configs" / "operating_point.yaml"
NAMES = {"naive": "P-naive", "normal": "P-normal", "quantile": "P-quantile"}
PARAM = {"naive": "buffer", "normal": "alpha", "quantile": "tau"}


def sim_run(lead: int, origins: str) -> tuple[str, pd.DataFrame, object]:
    name = f"latest:sim-L{lead}-focus{'-test' if origins == 'test' else ''}"
    run_id, path, cfg = load_run(name)
    if cfg.get("origins") != origins or cfg.get("lead_time") != lead:
        raise SystemExit(f"{run_id}: not a {origins} simulation with L = {lead}")
    lines = [json.loads(x) for x in (path / "metrics.jsonl").read_text().splitlines()]
    return run_id, pd.DataFrame(lines), path


def base_grid(m: pd.DataFrame, costs) -> pd.DataFrame:
    g = m[(m["margin"] == costs.margin) & (m["holding_rate"] == costs.holding_rate)].copy()
    g["write_down"] = costs.write_down_share * g["write_down_full"]
    g["total_cost_wd"] = g["total_cost"] + g["write_down"]
    return g


def select(leads, costs, cfg) -> None:
    refs = cfg["policies"]["naive"]["reference_buffers"]
    out = {
        "decision": "per lead time and reference P-naive buffer (0 and 1.0), "
        "P-quantile and P-normal at the smallest grid value whose tuning fill rate reaches "
        "the reference's",
        "lead_time": {},
    }
    for lead in leads:
        run_id, m, _ = sim_run(lead, "tuning")
        g = base_grid(m, costs)
        points = []
        for buf in refs:
            ref = g[(g["policy"] == "naive") & (g["value"] == buf)].iloc[0]
            rec = {"naive": {"buffer": float(buf),
                             "fill_rate": round(float(ref["fill_rate"]), 4)}}  # fmt: skip
            for pol in ("quantile", "normal"):
                row = match(g[g["policy"] == pol], ref["fill_rate"])
                if row is None:
                    raise SystemExit(f"L = {lead}: no {pol} value reaches {ref['fill_rate']:.3f}")
                rec[pol] = {
                    PARAM[pol]: float(row["value"]),
                    "fill_rate": round(float(row["fill_rate"]), 4),
                }
            points.append(rec)
            print(f"L = {lead}, buffer {buf:g}: {rec}")
        out["lead_time"][lead] = {"source_run": run_id, "points": points}
    OP.write_text(yaml.safe_dump(out, sort_keys=False, width=100))
    print(f"wrote {OP.relative_to(REPO_DIR)}")


def money(x: float) -> str:
    return f"£{x:,.0f}"


def grid_table(g: pd.DataFrame) -> list[str]:
    lines = ["| policy | value | fill rate | cycle service | stock-out weeks | avg stock value "
             "| holding | lost margin | total cost | + write-down |", "|---|---|---|---|---|---|"
             "---|---|---|---|"]  # fmt: skip
    for _, r in g.sort_values(["policy", "value"]).iterrows():
        lines.append(f"| {NAMES[r['policy']]} | {PARAM[r['policy']]} {r['value']:g} | "
                     f"{r['fill_rate']:.1%} | {r['cycle_service']:.1%} | {r['stockout_weeks']} | "
                     f"{money(r['avg_stock_value'])} | {money(r['holding_cost'])} | "
                     f"{money(r['lost_margin'])} | {money(r['total_cost'])} | "
                     f"{money(r['total_cost_wd'])} |")  # fmt: skip
    return lines


def frontier_fig(grids: dict, origins: str, lead: int, refs) -> None:
    g = grids[lead]
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    for i, pol in enumerate(["naive", "normal", "quantile"]):
        p = g[g["policy"] == pol].sort_values("fill_rate")
        ax.plot(p["fill_rate"], p["avg_stock_value"] / 1e3, color=SERIES[i], marker="o", ms=4,
                label=NAMES[pol])  # fmt: skip
        last = p.iloc[-1]
        ax.text(last["fill_rate"] + 0.003, last["avg_stock_value"] / 1e3, NAMES[pol],
                color=INK2, va="center", fontsize=8)  # fmt: skip
    for buf in refs:
        ref = g[(g["policy"] == "naive") & (g["value"] == buf)].iloc[0]
        ax.axvline(ref["fill_rate"], color=MUTED, lw=0.8, ls=":")
    ax.set_xlabel("fill rate (units served / demand)")
    ax.set_ylabel("average stock value (£ thousand, at cost)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    ax.set_title(f"Trade-off frontier, focus set, {origins} weeks, L = {lead}")
    ax.legend(loc="upper left", fontsize=8)
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(
            REPO_DIR / "reports" / "figures" / f"p5_frontier_{origins}.{ext}",
            metadata={"CreationDate": None, "ModDate": None} if ext == "pdf" else None,
        )
    plt.close(fig)


def report(leads, origins: str, costs, cfg) -> None:
    op = yaml.safe_load(OP.read_text()) if OP.exists() else None
    grids, runs, lines = {}, {}, []
    sens = cfg["sensitivity"]
    for lead in leads:
        run_id, m, path = sim_run(lead, origins)
        grids[lead], runs[lead] = base_grid(m, costs), (run_id, m, path)
    title = f"# Inventory simulation ({origins} weeks, focus set)"
    run_cfg = load_run(runs[leads[0]][0])[2]
    lines += [title, "", f"Runs: {', '.join(f'`{r[0]}`' for r in runs.values())}. Weeks "
              f"{run_cfg['weeks'][0]} to {run_cfg['weeks'][1]} ({run_cfg['n_weeks']}), "
              f"{run_cfg['products']} products; review period R = {costs.review_period} week; "
              f"lost sales. Base costs: margin {costs.margin:.0%}, holding {costs.holding_rate:.0%}"
              f" of the unit cost per year; critical ratio {run_cfg['critical_ratio']}. Write-down"
              f" (last column): {costs.write_down_share:.0%} of the unit cost of the stock left "
              f"at the end, {run_cfg['seasonal_products']} seasonal products "
              f"({', '.join(costs.write_down_categories)}).", ""]  # fmt: skip
    pct = lambda x: f"{x * 100:+.1f} pp"  # noqa: E731
    eur = lambda x: f"{x:+,.0f} £"  # noqa: E731
    for lead in leads:
        g = grids[lead]
        lines += [f"## L = {lead} (K = L + R = {lead + costs.review_period} weeks)", ""]
        points = op["lead_time"][lead]["points"] if op and lead in op["lead_time"] else []
        if points:
            kp = pd.read_parquet(runs[lead][2] / "simulation" / "kpis.parquet")
            kp = kp.set_index("stock_code")
            lines += [
                "Operating points fixed on the tuning weeks (configs/operating_point.yaml) vs. "
                "their P-naive reference; differences of the totals, paired bootstrap over "
                "products, 95 % CI, * = significant:",
                "",
                "| reference | policy | fill rate | avg stock value | total cost |",
                "|---|---|---|---|---|",
            ]
            for pt in points:
                buf = pt["naive"]["buffer"]
                naive = kp[(kp["policy"] == "naive") & (kp["value"] == buf)]
                for pol in ("quantile", "normal"):
                    v = pt[pol][PARAM[pol]]
                    b = bootstrap_totals(kp[(kp["policy"] == pol) & (kp["value"] == v)], naive)

                    def cell(k, fmt, b=b):
                        x = b[k]
                        star = " *" if x["significant"] else ""
                        return f"{fmt(x['diff'])} [{fmt(x['lo'])}, {fmt(x['hi'])}]{star}"

                    lines.append(
                        f"| P-naive buffer {buf:g} | {NAMES[pol]} {PARAM[pol]} {v:g} | "
                        f"{cell('fill_rate', pct)} | {cell('avg_stock_value', eur)} | "
                        f"{cell('total_cost', eur)} |"
                    )
            lines.append("")
        for buf in cfg["policies"]["naive"]["reference_buffers"]:
            ref = g[(g["policy"] == "naive") & (g["value"] == buf)].iloc[0]
            vals = ", ".join(
                f"{NAMES[p]} "
                + money(at_fill_rate(g[g["policy"] == p], ref["fill_rate"], "avg_stock_value"))
                for p in ("naive", "normal", "quantile")
            )
            lines.append(
                f"Average stock value at the fill rate of P-naive buffer {buf:g} "
                f"({ref['fill_rate']:.1%}), interpolated along each frontier: {vals}."
            )
        lines += [""] + grid_table(g) + [""]
    # sensitivity: operating points, total cost (no write-down) per margin x holding rate
    if op:
        lines += ["## Sensitivity (operating points; total cost = holding + lost margin)", ""]
        lines += ["| L | reference | margin | holding | P-naive | P-normal | P-quantile | "
                  "P-quantile vs. P-naive |", "|---|---|---|---|---|---|---|---|"]  # fmt: skip
        for lead in leads:
            if lead not in op["lead_time"]:
                continue
            m = runs[lead][1]
            for pt in op["lead_time"][lead]["points"]:
                buf = pt["naive"]["buffer"]
                for mg in sens["margin"]:
                    for h in sens["holding_rate"]:
                        s = m[(m["margin"] == mg) & (m["holding_rate"] == h)]

                        def cost(pol, v, s=s):
                            return float(s[(s["policy"] == pol) & (s["value"] == v)]
                                         ["total_cost"].iloc[0])  # fmt: skip

                        n = cost("naive", buf)
                        nm = cost("normal", pt["normal"]["alpha"])
                        q = cost("quantile", pt["quantile"]["tau"])
                        lines.append(
                            f"| {lead} | buffer {buf:g} | {mg:.0%} | {h:.0%} | {money(n)} | "
                            f"{money(nm)} | {money(q)} | {q - n:+,.0f} £ ({q / n - 1:+.1%}) |"
                        )
        lines += [
            "",
            "Write-down share of the seasonal stock left at the end (base costs, "
            "operating points): total cost incl. write-down",
            "",
            "| L | reference | share | P-naive | P-normal | P-quantile |",
            "|---|---|---|---|---|---|",
        ]
        for lead in leads:
            if lead not in op["lead_time"]:
                continue
            g = grids[lead]
            for pt in op["lead_time"][lead]["points"]:
                buf = pt["naive"]["buffer"]
                for share in sens["write_down_share"]:
                    vals = []
                    for pol, v in (
                        ("naive", buf),
                        ("normal", pt["normal"]["alpha"]),
                        ("quantile", pt["quantile"]["tau"]),
                    ):
                        r = g[(g["policy"] == pol) & (g["value"] == v)].iloc[0]
                        vals.append(money(r["total_cost"] + share * r["write_down_full"]))
                    lines.append(f"| {lead} | buffer {buf:g} | {share:.0%} | {' | '.join(vals)} |")
        lines.append("")
    frontier_fig(grids, origins, leads[0], cfg["policies"]["naive"]["reference_buffers"])
    out = REPO_DIR / "reports" / "experiments" / f"p5_{origins}.md"
    out.write_text("\n".join(lines))
    print("\n".join(lines))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["select", "report"])
    p.add_argument("--origins", choices=["tuning", "test"], default="tuning")
    p.add_argument("--lead-time", type=int, nargs="+", default=None)
    a = p.parse_args()
    costs, cfg = load_costs()
    leads = a.lead_time or cfg["sensitivity"]["lead_time"]
    if a.mode == "select":
        select(leads, costs, cfg)
    else:
        report(leads, a.origins, costs, cfg)


if __name__ == "__main__":
    main()
