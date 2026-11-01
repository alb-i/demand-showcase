"""Static demo: data for the Forecast, Decision and Policy pages of demo/.

    micromamba run -n demand-showcase python scripts/export_static.py [--out demo] \
        [--n 30] [--lead-times 1 2 3 4]

Reads $DATA_DIR/processed (panel, segments, leaderboards), the forecast runs of the models
shown and the stored sample paths ($DATA_DIR/paths/<model>-focus). The simulation code is
the workbench's (workbench.inventory.Lab), so the demo shows the same numbers as the Policy
and Decision pages there, for the test weeks.

Writes demo/data/ (JavaScript files, so the pages also open from file://):
  meta.js         weeks, grids, cost defaults (configs/costs.yaml), operating point, products
  aggregates.js   per L, policy and grid value the cost-free sums over all focus products
                  (re-priced in the page for any margin / holding rate / write-down)
  sim.js          for the demo products: test-week demand, 4-week mean and MA(4) error (P-naive,
                  P-normal) and price; the page simulates them itself
  levels-L<L>.js  for the demo products the P-quantile order-up-to levels per week and tau
  fc/<code>.js    history and the forecasts of the shown models (tuning + test origins)
  selftest.js     reference results of the Python simulator for policy.html?selftest
and copies chart.umd.min.js and style.css from the workbench. The pages themselves (html, js)
are in demo/ and written by hand.
"""

import argparse
import shutil
import time
from pathlib import Path

import numpy as np
import pandas as pd
import workbench
import yaml
from workbench.app import FAN
from workbench.inventory import FRONTIER, Costs, Lab
from workbench.timeseries import PanelAdapter

from retail.demo import aggregate, grid, js_data, pick_products, reprice, rounded
from retail.inventory.costs import load_costs
from retail.io import REPO_DIR, data_dir
from retail.runlog import runs_dir

MODELS = ["lgbm-total-q-p1.8", "snaive"]  # the selected model and the reference
GRIDS = {
    "quantile": grid(0.5, 0.99, 0.01, FRONTIER["quantile"]),
    "normal": grid(0.5, 0.99, 0.01, FRONTIER["normal"]),
    "naive": grid(0.0, 2.0, 0.05, FRONTIER["naive"]),
}


def write(path: Path, key: str, obj) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = js_data(key, obj)
    path.write_text(text)
    return len(text)


def operating_point(path: Path) -> dict:
    """Headline values per L (reference buffer 1.0), as in configs/operating_point.yaml."""
    op = yaml.safe_load(path.read_text())
    out = {}
    for lead, entry in op["lead_time"].items():
        pts = [p for p in entry["points"] if p["naive"]["buffer"] == 1.0]
        if pts:
            p = pts[0]
            out[str(lead)] = {"naive": p["naive"]["buffer"], "normal": p["normal"]["alpha"],
                              "quantile": p["quantile"]["tau"]}  # fmt: skip
    return out


def forecasts(adapter: PanelAdapter, runs: Path, code: str) -> dict:
    """Forecasts of MODELS for one product: the runs of the focus leaderboards (tuning + test)."""
    out = {}
    cols = ["mean", "q0.5"] + [f"q{t:g}" for pair in FAN for t in pair]
    for model in MODELS:
        frames = []
        for origins in ("tuning", "test"):
            lb = adapter.get_leaderboard("focus", origins)
            hit = lb[(lb["model"] == model) & (lb["segment"] == "all")]
            rid = hit["run_id"].iloc[0]
            frames.append(adapter.get_forecasts(runs / rid, code))
        fc = pd.concat(frames, ignore_index=True)
        out[model] = {str(pd.Timestamp(o).date()): {c: rounded(g.sort_values("h")[c], 2)
                                                    for c in cols}
                      for o, g in fc.groupby("origin")}  # fmt: skip
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--out", type=Path, default=REPO_DIR / "demo")
    p.add_argument("--n", type=int, default=30)
    p.add_argument("--lead-times", type=int, nargs="+", default=[1, 2, 3, 4])
    a = p.parse_args()
    runs = runs_dir()
    t0 = time.time()
    costs, cfg = load_costs()
    source = cfg["policies"]["quantile"]["source"]
    adapter = PanelAdapter(data_dir() / "processed")
    lab = Lab(adapter, data_dir() / "paths" / f"{source}-focus", "test",
              seasonal_categories=costs.write_down_categories)  # fmt: skip
    table = adapter.list_series()
    focus = table[table["focus"]]
    codes = pick_products(focus, n=a.n)
    rows = [lab.codes.index(c) for c in codes]
    info = focus.set_index("series_id").loc[codes]
    out = a.out / "data"
    sizes = {}

    # aggregates over all focus products (cost-free sums, re-priced in the page)
    aggs = {}
    for lead in a.lead_times:
        aggs[str(lead)] = {pol: [aggregate(lab.summary(pol, v, lead), lab.price, lab.seasonal)
                                 for v in vals] for pol, vals in GRIDS.items()}  # fmt: skip
        print(f"aggregates L{lead}: {time.time() - t0:.0f} s", flush=True)
    sizes["aggregates.js"] = write(out / "aggregates.js", "aggregates", aggs)

    # demo products: inputs of the page's own simulation
    hist = lab.history
    sims = {}
    for c, i in zip(codes, rows, strict=True):
        sims[c] = {"demand": rounded(lab.demand[i], 2), "mu": rounded(hist.mu[i], 4),
                   "sigma": rounded(hist.sigma[i], 4), "price": round(float(lab.price[i]), 4),
                   "seasonal": bool(lab.seasonal[i])}  # fmt: skip
    sizes["sim.js"] = write(out / "sim.js", "sim", sims)
    for lead in a.lead_times:
        sums = lab.sums(lead + 1)
        levels = np.stack([sums.quantile(t)[rows] for t in GRIDS["quantile"]], axis=2)
        obj = {c: [rounded(levels[k, j], 2) for j in range(len(lab.weeks))]
               for k, c in enumerate(codes)}  # fmt: skip
        sizes[f"levels-L{lead}.js"] = write(out / f"levels-L{lead}.js", f"levels-L{lead}", obj)
    print(f"levels: {time.time() - t0:.0f} s", flush=True)

    # forecasts and history per product (loaded when the product is opened)
    for c in codes:
        s = adapter.get_series(c)
        obj = {"weeks": [str(w.date()) for w in s["week"]], "units": rounded(s["units"], 2),
               "closed": [bool(x) for x in s["closed"]],
               "forecasts": forecasts(adapter, runs, c)}  # fmt: skip
        sizes[f"fc/{c}.js"] = write(out / "fc" / f"{c}.js", f"fc-{c}", obj)

    # reference results of the Python simulator for the page's self-test
    op = operating_point(REPO_DIR / "configs" / "operating_point.yaml")
    base = Costs(margin=costs.margin, holding_rate=costs.holding_rate, write_down=0.0,
                 weeks_per_year=costs.weeks_per_year)  # fmt: skip
    cases = []
    for lead, policy, value in [(1, "quantile", 0.925), (2, "normal", 0.9), (4, "naive", 1.0),
                                (3, "quantile", 0.6)]:  # fmt: skip
        if lead not in a.lead_times:
            continue
        sim, _ = lab.run(policy, value, lead, base)
        for i in rows[:3]:
            cases.append({"product": lab.codes[i], "L": lead, "policy": policy, "value": value,
                          "end": rounded(sim["end"][i], 3),
                          "order": rounded(sim["order"][i], 3)})  # fmt: skip
    k = GRIDS["quantile"].index(0.925)
    agg = aggs[str(a.lead_times[0])]["quantile"][k]
    want = reprice(agg, 0.25, 0.4, 0.5, costs.weeks_per_year)
    checks = {"cases": cases, "reprice": {"L": a.lead_times[0], "policy": "quantile", "index": k,
              "margin": 0.25, "holding": 0.4, "writedown": 0.5, "want": want}}  # fmt: skip
    sizes["selftest.js"] = write(out / "selftest.js", "selftest", checks)

    meta = {
        "weeks": lab.weeks, "model": lab.model, "models": MODELS, "grids": GRIDS,
        "lead_times": a.lead_times, "data_end": str(adapter.weeks[-1].date()),
        "costs": {"margin": costs.margin, "holding": costs.holding_rate,
                  "writedown": 0.0, "writedown_scenario": costs.write_down_share,
                  "weeks_per_year": costs.weeks_per_year},
        "operating_point": op, "n_focus": len(lab.codes), "fan": [list(f) for f in FAN],
        "test_from": str(cfg["simulation"]["test_from"]),
        "products": [{"id": c, "description": info.loc[c, "description"],
                      "segment": info.loc[c, "segment"], "category": info.loc[c, "category"],
                      "revenue": round(float(info.loc[c, "revenue"]), 0)} for c in codes],
    }  # fmt: skip
    sizes["meta.js"] = write(out / "meta.js", "meta", meta)

    static = Path(workbench.__file__).parent / "static"
    for name in ("chart.umd.min.js", "style.css"):
        shutil.copyfile(static / name, a.out / name)
    total = sum(sizes.values())
    big = sorted(sizes.items(), key=lambda kv: -kv[1])[:4]
    print(f"{len(codes)} products, {len(sizes)} data files, {total / 1e6:.2f} MB "
          f"(largest: {', '.join(f'{k} {v / 1e3:.0f} kB' for k, v in big)}), "
          f"{time.time() - t0:.0f} s -> {a.out}")  # fmt: skip


if __name__ == "__main__":
    main()
