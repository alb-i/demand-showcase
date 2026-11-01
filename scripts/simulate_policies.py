"""Inventory simulation of the periodic-review policies.

    micromamba run -n demand-showcase python scripts/simulate_policies.py \
        [--origins tuning|test --final] [--lead-time 1 2 4] [--backorders]

For each lead time L (review period R from configs/costs.yaml, K = L + R) one run
sim-L<L>-focus[-test]: every policy and grid value of configs/costs.yaml (P-naive buffers,
P-normal alphas, P-quantile taus) is simulated week by week over the simulated weeks (tuning:
from simulation.tuning_from to the last tuning origin; test: the test origins), demand = the
cleaned weekly units of the focus set, start stock = S of the first week. P-quantile reads the
tau-quantile of the K-week sum of 1000 sample paths (E7b, common ties) of the selected model's
forecasts at origin t; the PIT pool uses earlier origins only (tuning: tuning runs; test: tuning
+ earlier test origins).
Run folder: config.yaml (costs, grids, sources), metrics.jsonl (one line per policy, value and
cost scenario margin x holding rate: totals; write_down_full = value of the seasonal stock left
at the end, the write-down is share x that), simulation/<policy>-<value>.parquet (weekly per
product: demand, arrival, order, stock, served, short, level) and simulation/kpis.parquet (per
product, base costs). Prices: median weekly price before the first simulated week.
"""

import argparse
import itertools
import json

import pandas as pd
import yaml

from retail.backtest import wide_units
from retail.compare import load_run
from retail.inventory.costs import COSTS, critical_ratio, load_costs, unit_economics, unit_prices
from retail.inventory.policies import naive_levels, normal_levels, quantile_levels
from retail.inventory.simulate import kpis, simulate, totals
from retail.io import REPO_DIR, data_dir
from retail.paths import horizon_sums
from retail.runlog import RunLogger


def source_rows(model: str, origins: str) -> tuple[pd.DataFrame, list[str], str]:
    """Evaluated rows of the model's newest focus runs: tuning; for test tuning + test (the
    PIT pool rolls over both)."""
    names = [f"{model}-focus"] + ([f"{model}-focus-test"] if origins == "test" else [])
    rows, ids, version = [], [], None
    for n in names:
        run_id, path, cfg = load_run(f"latest:{n}")
        if cfg.get("origins", "tuning") != ("test" if n.endswith("-test") else "tuning"):
            raise SystemExit(f"{run_id}: unexpected origins {cfg.get('origins')}")
        rows.append(pd.read_parquet(path / "rows.parquet"))
        ids.append(run_id)
        version = json.loads((path / "meta.json").read_text())["dataset_version"]
    return pd.concat(rows, ignore_index=True), ids, version


def policy_levels(cfg, wide, codes, weeks, k, paths) -> dict[tuple[str, float], pd.DataFrame]:
    pol = cfg["policies"]
    w = wide.loc[codes]
    out = {}
    for b in pol["naive"]["buffer"]:
        out[("naive", b)] = naive_levels(w, weeks, k, b, pol["naive"]["window"])
    for a in pol["normal"]["alpha"]:
        out[("normal", a)] = normal_levels(w, weeks, k, a, pol["normal"]["window"],
                                           pol["normal"]["sigma_weeks"])  # fmt: skip
    for t in pol["quantile"]["tau"]:
        out[("quantile", t)] = quantile_levels(paths, codes, weeks, k, t)
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--origins", choices=["tuning", "test"], default="tuning")
    p.add_argument("--final", action="store_true", help="required for the test origins")
    p.add_argument("--lead-time", type=int, nargs="+", default=None)
    p.add_argument("--backorders", action="store_true")
    p.add_argument("--costs", default=str(COSTS))
    a = p.parse_args()
    if a.origins == "test" and not a.final:
        p.error("the test simulation is run once per policy: add --final")

    base, cfg = load_costs(a.costs)
    base = base.with_(lost_sales=not a.backorders and base.lost_sales)
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    sim_cfg, qcfg = cfg["simulation"], cfg["policies"]["quantile"]
    codes = sorted(bt["focus_set"]["stock_codes"])
    processed = data_dir() / "processed"
    panel = pd.read_parquet(processed / "panel_weekly.parquet")
    wide = wide_units(panel)
    first = pd.Timestamp(sim_cfg[f"{a.origins}_from"])
    last = pd.Timestamp(bt["origins"][a.origins]["to"])
    weeks = [w for w in wide.columns if first <= w <= last]
    demand = wide.loc[codes, weeks]
    econ0 = unit_prices(panel, first).reindex(codes)
    if econ0.isna().any():
        raise SystemExit(f"no price before {first.date()}: {list(econ0[econ0.isna()].index)}")
    cats = pd.read_parquet(processed / "categories.parquet").set_index("stock_code")["category"]
    seasonal = [c for c in codes if cats.get(c) in base.write_down_categories]
    seg = pd.read_parquet(processed / "segments.parquet").set_index("stock_code")
    labels = seg["abc"] + "-" + seg["sb_class"]
    rows, source_ids, version = source_rows(qcfg["source"], a.origins)
    sens = cfg["sensitivity"]
    scenarios = list(itertools.product(sens["margin"], sens["holding_rate"]))

    for lead in a.lead_time or sens["lead_time"]:
        costs = base.with_(lead_time=lead)
        k = costs.horizon
        frames, info = horizon_sums(rows, bt["quantiles"], ks=(k,), labels=labels,
                                    n_paths=qcfg["n_paths"], min_pool=qcfg["min_pool"],
                                    seed=qcfg["seed"], common_ties=True,
                                    out_quantiles=qcfg["tau"], sampled=("paths",))  # fmt: skip
        paths = frames["paths"]
        levels = policy_levels(cfg, wide, codes, weeks, k, paths)
        # orders placed in the last L weeks arrive after the end: their levels may be missing
        need = weeks[: len(weeks) - lead] if lead else weeks
        for key, s in levels.items():
            gaps = s[need].isna().to_numpy().sum()
            if gaps:
                raise SystemExit(f"L = {lead}, {key}: {gaps} missing order-up-to levels")
        config = {
            "experiment": "P5", "set": sim_cfg["set"], "origins": a.origins,
            "lead_time": lead, "review_period": costs.review_period, "horizon_k": k,
            "lost_sales": costs.lost_sales, "weeks": [str(weeks[0].date()), str(weeks[-1].date())],
            "n_weeks": len(weeks), "products": len(codes), "seasonal_products": len(seasonal),
            "critical_ratio": round(critical_ratio(costs), 4), "simulation": True,
            "path_source_runs": source_ids, "costs": cfg,
        }  # fmt: skip
        mode = "" if costs.lost_sales else "-backorders"
        name = f"sim-L{lead}{mode}-{sim_cfg['set']}{'-test' if a.origins == 'test' else ''}"
        with RunLogger(config, name=name, data_version=version) as run:
            print(run.dir, flush=True)
            (run.dir / "simulation").mkdir()
            base_kpis = []
            for (policy, value), s in levels.items():
                sim = simulate(demand, s, lead, costs.review_period, costs.lost_sales)
                sim.to_parquet(run.dir / "simulation" / f"{policy}-{value:g}.parquet")
                for m, h in scenarios:
                    c = costs.with_(margin=m, holding_rate=h, write_down_share=1.0)
                    per = kpis(sim, unit_economics(econ0, c), c, seasonal, costs.review_period)
                    t = totals(per)
                    t["write_down_full"] = t.pop("write_down")
                    t.pop("total_cost_wd")
                    run.log(policy=policy, value=value, margin=m, holding_rate=h, **t)
                    if m == base.margin and h == base.holding_rate:
                        base_kpis.append(per.assign(policy=policy, value=value))
                        print(f"L={lead} {policy:8} {value:<5g} fill {t['fill_rate']:.3f} "
                              f"stock £{t['avg_stock_value']:,.0f} cost £{t['total_cost']:,.0f}",
                              flush=True)  # fmt: skip
            pd.concat(base_kpis).reset_index().to_parquet(run.dir / "simulation" / "kpis.parquet")
            info.to_csv(run.dir / "simulation" / "path_pool.csv", index=False)
        print(f"L = {lead}: K = {k}, {len(weeks)} weeks, {len(codes)} products, "
              f"pool min {info['n_pool'].min()} (origins {info['origin'].min().date()}..)",
              flush=True)  # fmt: skip


if __name__ == "__main__":
    main()
