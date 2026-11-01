"""Raw lines -> cleaned lines -> weekly SKU panel, with cleaning report.

    micromamba run -n demand-showcase python scripts/build_panel.py [configs/cleaning.yaml]

Variant `main` writes $DATA_DIR/processed/{panel_weekly,sales_clean}.parquet and the
committed reports/{cleaning_report.md,descriptions.csv,bulk_review.csv}; any other variant
writes all of these to $DATA_DIR/processed/variants/<variant>/.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from retail.cleaning import (
    book,
    bulk_candidates,
    clean,
    data_version,
    git_commit,
    is_cancellation,
    load_config,
    r1_overlap,
    reconcile,
    totals,
)
from retail.io import REPO_DIR, data_dir
from retail.panel import (
    build_panel,
    canonical_descriptions,
    drop_last_week,
    panel_totals,
    trading_weeks,
)
from retail.review import merge_decisions, read_review


def bulk_review(sales: pd.DataFrame, cancels: pd.DataFrame, k: float, top: int) -> pd.DataFrame:
    """Top bulk candidates with the median quantity of the product and the first cancellation
    of the same product by the same customer within 30 days (any quantity)."""
    cand = bulk_candidates(sales, k).head(top)
    med = sales.groupby("stock_code")["quantity"].median()
    rows = []
    for r in cand.itertuples():
        c = cancels[
            (cancels["customer_id"] == r.customer_id)
            & (cancels["stock_code"] == r.stock_code)
            & (cancels["invoice_date"] >= r.invoice_date)
            & (cancels["invoice_date"] <= r.invoice_date + pd.Timedelta(days=30))
        ]
        first = c.sort_values("invoice_date").head(1)
        rows.append(
            {
                "invoice": r.invoice,
                "stock_code": r.stock_code,
                "description": r.description,
                "quantity": r.quantity,
                "price": r.price,
                "revenue": round(r.quantity * r.price, 2),
                "date": r.invoice_date.date().isoformat(),
                "customer_id": r.customer_id,
                "country": r.country,
                "product_median_qty": med[r.stock_code],
                "z": round(r.z, 1) if np.isfinite(r.z) else "inf",
                "cancelled_qty_30d": int(-c["quantity"].sum()) if len(c) else 0,
                "first_cancel_days": (first["invoice_date"].iloc[0] - r.invoice_date).days
                if len(first)
                else None,
                "decision": "",
            }
        )
    return pd.DataFrame(rows)


def fmt(x: float) -> str:
    return f"{x:,.0f}".replace(",", " ")


def cancellation_table(raw: pd.DataFrame, fate: pd.Series) -> list[str]:
    """Where the cancellation lines went: lines and revenue per rule / return."""
    c = is_cancellation(raw)
    rev = (raw["quantity"] * raw["price"])[c]
    g = pd.DataFrame({"fate": fate[c], "rev": rev}).groupby("fate")["rev"].agg(["size", "sum"])
    out = ["| Cancellations (C...) went to | Lines | Revenue (£) |", "|---|---:|---:|"]
    for name, r in g.sort_values("sum").iterrows():
        out.append(f"| {name} | {fmt(r['size'])} | {fmt(r['sum'])} |")
    out.append(f"| all | {fmt(c.sum())} | {fmt(rev.sum())} |")
    return out


def report(
    cfg, version, commit, raw_tot, removed, kept, ret, panel, weeks, desc, last, canc
) -> str:
    rows = [raw_tot] + removed + [kept, ret]
    ok = reconcile(raw_tot, removed + [kept, ret])
    pt = panel_totals(panel)
    lines = [
        f"# Cleaning report — variant `{cfg['variant']}`",
        "",
        f"Data version `{version}` (cleaning config + commit `{commit}`).",
        "",
        "| Step | Lines | Units | Revenue (£) |",
        "|---|---:|---:|---:|",
    ]
    names = {"total": "Raw (both sheets)"}
    for r in rows:
        name = names.get(r["rule"], r["rule"])
        lines.append(f"| {name} | {fmt(r['lines'])} | {fmt(r['units'])} | {fmt(r['revenue'])} |")
    lines += [
        "",
        f"Reconciliation (raw = removals + demand + returns, lines, units and revenue): "
        f"**{'OK' if ok else 'FAILED'}**.",
        "",
        f"- Demand in the panel: {fmt(pt['units'])} units, £{fmt(pt['revenue'])}"
        f" (lines: {fmt(kept['units'])} units, £{fmt(kept['revenue'])}).",
        f"- Returns in the panel (`returned_units`): {fmt(pt['returned_units'])} units,"
        f" £{fmt(-ret['revenue'])} = {(-ret['revenue']) / kept['revenue']:.1%} of demand revenue.",
        f"- Panel: {panel['stock_code'].nunique()} SKUs, {weeks['week'].min().date()} to "
        f"{weeks['week'].max().date()} ({len(weeks)} weeks), {len(panel)} rows "
        f"({int(panel['closed'].sum())} in closed weeks)"
        + (f"; dropped incomplete week {last.date()}." if last is not None else "."),
        f"- Closed weeks: {', '.join(str(w.date()) for w in weeks.loc[weeks['closed'], 'week'])}.",
        f"- Stock codes with more than one description: {int((desc['n_descriptions'] > 1).sum())}"
        f" of {len(desc)} (canonical = most frequent, reports/descriptions.csv).",
        "",
        *canc,
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    cfg_path = Path(sys.argv[1] if len(sys.argv) > 1 else REPO_DIR / "configs" / "cleaning.yaml")
    cfg = load_config(cfg_path)
    commit = git_commit(REPO_DIR)
    version = data_version(cfg, commit)
    processed = data_dir() / "processed"
    raw = pd.read_parquet(processed / "raw.parquet")

    out_dir = processed if cfg["variant"] == "main" else processed / "variants" / cfg["variant"]
    rep_dir = REPO_DIR / "reports" if cfg["variant"] == "main" else out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    rep_dir.mkdir(parents=True, exist_ok=True)

    cleaned = clean(raw, cfg)
    removed = cleaned.removed.to_dict("records")
    weeks = trading_weeks(raw[~r1_overlap(raw, cfg)])
    sales, returns = cleaned.sales, cleaned.returns
    last = None
    if cfg["panel"]["drop_last_week"]:
        sales, returns, gone, last = drop_last_week(sales, returns)
        removed.append(book("R8 incomplete last week", gone))
        cleaned.fate[gone.index] = "R8 incomplete last week"
        weeks = weeks[weeks["week"] < last]
    panel, outside = build_panel(sales, returns, weeks)
    removed.append(book("R9 returns outside the active window", outside))
    cleaned.fate[outside.index] = "R9 returns outside the active window"
    returns = returns.drop(outside.index)

    desc = canonical_descriptions(sales)
    panel = panel.merge(desc[["stock_code", "description"]], on="stock_code", how="left")
    cancels = raw[is_cancellation(raw)].assign(stock_code=lambda d: d["stock_code"].str.upper())
    review = bulk_review(sales, cancels, cfg["bulk"]["k"], cfg["bulk"]["review_top"])

    kept = book("Demand (panel units)", sales)
    ret = book("Returns (panel returned_units)", returns)
    canc = cancellation_table(raw, cleaned.fate)
    text = report(
        cfg, version, commit, totals(raw), removed, kept, ret, panel, weeks, desc, last, canc
    )

    panel.to_parquet(out_dir / "panel_weekly.parquet", index=False)
    sales.to_parquet(out_dir / "sales_clean.parquet", index=False)
    meta = {"variant": cfg["variant"], "data_version": version, "git_commit": commit, "config": cfg}
    (out_dir / "panel_meta.json").write_text(json.dumps(meta, indent=2, default=str) + "\n")
    (rep_dir / "cleaning_report.md").write_text(text)
    desc.to_csv(rep_dir / "descriptions.csv", index=False)
    review_csv = rep_dir / "bulk_review.csv"
    if review_csv.exists():  # keep the decisions made so far (scripts/review_bulk.py)
        review = merge_decisions(review, read_review(review_csv))
    review.to_csv(review_csv, index=False)
    print(text)
    print(f"-> {out_dir}, reports in {rep_dir}")


if __name__ == "__main__":
    main()
