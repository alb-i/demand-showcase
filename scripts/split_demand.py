"""Weekly bulk / item split of the demand (E2 extension).

    micromamba run -n demand-showcase python scripts/split_demand.py [--ratio 10]

A sales line is bulk when its quantity is above max_order_ratio (configs/backtest.yaml,
segments.syntetos_boylan) x the product's median line quantity over the weeks before
segments.before (the bulk rule of the segments, fixed for all weeks); --ratio
sets another factor. Writes $DATA_DIR/processed/demand_split_r<ratio>.parquet
(stock_code, week, units_bulk; only weeks with bulk units) and .json (data version, threshold,
totals).
"""

import argparse
import json

import pandas as pd
import yaml

from retail.io import REPO_DIR, data_dir
from retail.segments import bulk_thresholds, demand_split, split_files


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ratio", type=float, help="bulk factor (default: max_order_ratio)")
    a = p.parse_args()
    cfg = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())["segments"]
    processed = data_dir() / "processed"
    panel = pd.read_parquet(processed / "panel_weekly.parquet")
    sales = pd.read_parquet(processed / "sales_clean.parquet")
    meta = json.loads((processed / "panel_meta.json").read_text())
    ratio = a.ratio or cfg["syntetos_boylan"]["max_order_ratio"]
    split = demand_split(sales, bulk_thresholds(sales, cfg["before"], ratio))
    check = panel.merge(split, on=["stock_code", "week"], how="inner")
    if len(check) != len(split) or (check["units_bulk"] > check["units"]).any():
        raise SystemExit("bulk units outside the panel or above the weekly units")
    parquet, info_path = split_files(processed, ratio)
    split.to_parquet(parquet, index=False)
    info = {
        "data_version": meta["data_version"],
        "before": str(cfg["before"]),
        "max_order_ratio": ratio,
        "bulk_units": int(split["units_bulk"].sum()),
        "units": int(panel["units"].sum()),
        "products_with_bulk": int(split["stock_code"].nunique()),
        "weeks_with_bulk": len(split),
    }
    info_path.write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
