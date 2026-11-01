"""Bottom-up vs. direct forecasts of the category totals (experiment E3c).

    micromamba run -n demand-showcase python scripts/bottom_up.py --products RUN \
        --category RUN [RUN ...] [--title ...] [--out reports/experiments/e3c_bottom_up.md]

--products: a product-level run on the full set (total demand); its mean forecasts are summed
per category, origin and horizon (bottom-up). --category: runs at category level (backtest.py
--level category) with the same origins; their mean forecasts are the direct ones. Both are
scored on the category runs' actuals and naive scales (MASE; only point forecasts: quantiles do
not add up, so the bottom-up sum has no quantiles). Products launched after an origin have no
product forecast; their demand is in the category actuals.
"""

import argparse

import pandas as pd
import yaml

from retail.categories import load_categories
from retail.compare import common_target, load_run
from retail.io import REPO_DIR, data_dir


def bottom_up(forecasts: pd.DataFrame, categories: pd.Series) -> pd.DataFrame:
    """Mean forecasts summed per (category, origin, h)."""
    f = forecasts.assign(category=forecasts["stock_code"].map(categories).fillna("other"))
    return f.groupby(["category", "origin", "h"], as_index=False)["mean"].sum()


def scaled_errors(rows: pd.DataFrame, mean: pd.Series) -> pd.Series:
    """|y - mean| / scale per category row (rows of a category-level run)."""
    return (rows["y"] - mean).abs() / rows["scale"]


def score(cat_rows: pd.DataFrame, bu: pd.DataFrame) -> pd.DataFrame:
    """Per category: MASE of the direct forecast (the run's mean) and of the bottom-up sum."""
    r = cat_rows.merge(bu.rename(columns={"category": "stock_code", "mean": "bottom_up"}),
                       on=["stock_code", "origin", "h"], how="left")  # fmt: skip
    r["bottom_up"] = r["bottom_up"].fillna(0.0)
    r["direct_err"] = scaled_errors(r, r["mean"])
    r["bu_err"] = scaled_errors(r, r["bottom_up"])
    g = r.groupby("stock_code")
    return pd.DataFrame({"direct": g["direct_err"].mean(), "bottom_up": g["bu_err"].mean()})


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--products", required=True)
    p.add_argument("--category", nargs="+", required=True)
    p.add_argument("--title", default="Bottom-up vs. direct category forecasts")
    p.add_argument("--out")
    a = p.parse_args()
    prod_id, prod_dir, prod_cfg = load_run(a.products)
    if prod_cfg.get("level", "product") != "product" or prod_cfg["set"] != "full":
        p.error("--products must be a product-level run on the full set")
    meta = yaml.safe_load((data_dir() / "processed" / "panel_meta.json").read_text())
    cats = load_categories(data_dir() / "processed", meta["data_version"])
    bu = bottom_up(pd.read_parquet(prod_dir / "forecasts.parquet"), cats)
    lines = [f"# {a.title}", "",
             f"Bottom-up = the summed mean forecasts of `{prod_id}`. MASE on the category "
             "totals (scale: naive error of each category series); lower = better.",
             ""]  # fmt: skip
    tables = {}
    for run in a.category:
        run_id, run_dir, cfg = load_run(run)
        if cfg.get("level") != "category":
            p.error(f"{run_id} is not a category-level run")
        common_target([prod_cfg, cfg])
        rows = pd.read_parquet(run_dir / "rows.parquet")
        if set(rows["origin"].unique()) - set(bu["origin"].unique()):
            p.error(f"{run_id} has origins the product run does not have")
        tables[run_id] = score(rows, bu)
    first = next(iter(tables.values()))
    lines += ["| run (direct) | MASE direct | MASE bottom-up | categories direct better |",
              "|---|---|---|---|"]  # fmt: skip
    for run_id, t in tables.items():
        lines.append(f"| {run_id} | {t['direct'].mean():.3f} | {t['bottom_up'].mean():.3f} | "
                     f"{(t['direct'] < t['bottom_up']).sum()} of {len(t)} |")  # fmt: skip
    lines += ["", "## MASE per category", "",
              "| category | bottom-up | " + " | ".join(tables) + " |",
              "|" + "---|" * (len(tables) + 2)]  # fmt: skip
    for cat in first.sort_values("bottom_up").index:
        cells = [f"{t.loc[cat, 'direct']:.3f}" for t in tables.values()]
        lines.append(f"| {cat} | {first.loc[cat, 'bottom_up']:.3f} | " + " | ".join(cells) + " |")
    text = "\n".join(lines) + "\n"
    print(text)
    if a.out:
        out = REPO_DIR / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)


if __name__ == "__main__":
    main()
