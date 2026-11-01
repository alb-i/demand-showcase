"""Product categories from the descriptions.

    micromamba run -n demand-showcase python scripts/categorize.py

Classifies every product of the panel by its canonical description with the rules in
configs/categories.yaml. Writes $DATA_DIR/processed/categories.parquet (stock_code, category)
and .json (data version), reports/categories.csv (stock_code, description, category) and
reports/categories.md (products, units and revenue per category over the weeks before the
segment cut-off, focus products, examples).
"""

import json

import pandas as pd
import yaml

from retail.categories import OTHER, categorize, labels
from retail.io import REPO_DIR, data_dir


def summary(cat: pd.DataFrame, seg: pd.DataFrame) -> pd.DataFrame:
    """Per category: products, products in the segment table, focus products, unit / revenue
    share (segment table, weeks before the cut-off)."""
    s = seg.merge(cat, on="stock_code", how="left")
    g = s.groupby("category")
    out = pd.DataFrame({
        "products": cat.groupby("category").size(),
        "segmented": g.size(),
        "focus": g["focus"].sum(),
        "units_share": g["units"].sum() / s["units"].sum(),
        "revenue_share": g["revenue"].sum() / s["revenue"].sum(),
    })  # fmt: skip
    return out.fillna(0).sort_values("revenue_share", ascending=False)


def main() -> None:
    processed = data_dir() / "processed"
    panel = pd.read_parquet(processed / "panel_weekly.parquet")
    meta = json.loads((processed / "panel_meta.json").read_text())
    seg = pd.read_parquet(processed / "segments.parquet")
    desc = panel.drop_duplicates("stock_code").set_index("stock_code")["description"]
    cat = categorize(desc).rename_axis("stock_code").reset_index()
    cat.to_parquet(processed / "categories.parquet", index=False)
    info = {"data_version": meta["data_version"], "products": len(cat),
            "categories": int(cat["category"].nunique())}  # fmt: skip
    (processed / "categories.json").write_text(json.dumps(info, indent=2) + "\n")
    cat.insert(1, "description", cat["stock_code"].map(desc))
    cat.to_csv(REPO_DIR / "reports" / "categories.csv", index=False)

    names = labels()
    table = summary(cat[["stock_code", "category"]], seg)
    before = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())["segments"]
    lines = ["# Product categories", "",
             f"{len(cat):,} products (data version {meta['data_version']}) classified by their "
             "canonical description with the ordered keyword rules of configs/categories.yaml "
             f"(first match wins). Units and revenue: segment table, weeks before "
             f"{before['before']}.", "",
             "| category | label | products | segmented | focus | units | revenue |",
             "|---|---|---|---|---|---|---|"]  # fmt: skip
    for name, r in table.iterrows():
        lines.append(
            f"| {name} | {names.get(name, name)} | {r['products']:.0f} | {r['segmented']:.0f} | "
            f"{r['focus']:.0f} | {r['units_share']:.1%} | {r['revenue_share']:.1%} |"
        )
    lines += ["", "## Examples (largest products by revenue)", ""]
    s = seg.merge(cat[["stock_code", "category"]], on="stock_code")
    for name in table.index:
        top = s[s["category"] == name].nlargest(6, "revenue")["description"].tolist()
        if name == OTHER and not top:
            continue
        lines.append(f"- **{name}**: " + "; ".join(top))
    text = "\n".join(lines) + "\n"
    (REPO_DIR / "reports" / "categories.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
