"""Rolling-origin backtest of one model.

    micromamba run -n demand-showcase python scripts/backtest.py configs/models/trivial.yaml \
        [--set focus|full] [--origins tuning|test --final] [--jobs N]

Writes $RUNS_DIR/<run-id>/: meta.json, config.yaml, heartbeat, metrics.jsonl (one line per
origin x segment x horizon, plus origin "all"), forecasts.parquet and rows.parquet (evaluated
rows: y, scale, weight, forecast). Test origins are used once at the end: they need --final.
--jobs: origins evaluated in parallel worker processes (default 6); same results.
--target item: models see and are scored on item demand only (units - units_bulk).
--level category: the products are summed per category (categories.parquet) and the
models forecast those category series (all categories but non_product; --set is ignored).
The model config may set pool_by: category (intervals pooled per product category instead of
the segment; name suffix -poolcat).
name: lgbm = the global LightGBM model (E4); it is trained on all products of the panel
whatever --set is (the set only chooses the evaluated products).
The panel gets the column units_bulk from demand_split_r<ratio>.parquet (split_demand.py);
the model config may set bulk_ratio (default: segments max_order_ratio, 10), a ratio
other than the default is appended to the model name (e.g. ets-bulk-ma52-r10).
Runs on the test origins get the name suffix -test (e.g. ma4-focus-test). prepare() is
also used by scripts/run_batch.py (many runs in one worker pool).
"""

import argparse
import json

import pandas as pd
import yaml

from retail.backtest import default_jobs, origin_weeks, wide_units
from retail.categories import category_panel, load_categories
from retail.io import REPO_DIR, data_dir
from retail.models.baselines import Baseline
from retail.models.croston import Intermittent
from retail.models.lgbm import GlobalLGBM
from retail.models.split import Split
from retail.models.stats import StatsModel
from retail.models.topdown import TopDown
from retail.models.trivial import Trivial
from retail.runlog import RunLogger
from retail.runner import Prepared, finish, log_origin, schedule
from retail.segments import split_files

MODELS = {
    "trivial": Trivial,
    "baseline": Baseline,
    "intermittent": Intermittent,
    "split": Split,
    "stats": StatsModel,
    "topdown": TopDown,
    "lgbm": GlobalLGBM,
}
NOT_PARAMS = ("name", "experiment", "bulk_ratio", "pool_by")


def load_model(cfg: dict, segments: pd.Series, categories: pd.Series | None = None):
    """Model from its config; models that pool get the pool labels (`segments`), top-down
    models the product categories."""
    params = {k: v for k, v in cfg.items() if k not in NOT_PARAMS}
    cls = MODELS[cfg["name"]]
    args = cls.__init__.__code__.co_varnames
    if "segments" in args:
        params["segments"] = segments
    if "categories" in args:
        if categories is None:
            raise ValueError(f"model {cfg['name']} needs the product categories")
        params["categories"] = categories
    return cls(**params)


def pool_labels(pool_by: str, segments: pd.Series, categories: pd.Series) -> pd.Series:
    """Labels the intervals are pooled by: the segment (default) or the category."""
    if pool_by == "segment":
        return segments
    if pool_by == "category":
        return categories
    raise ValueError(f"pool_by must be segment or category, not {pool_by!r}")


def with_bulk(panel: pd.DataFrame, processed, data_version: str, ratio: float) -> pd.DataFrame:
    """Panel plus units_bulk for the bulk threshold `ratio` (0 where a week has no bulk lines)."""
    path, info_path = split_files(processed, ratio)
    if not path.exists():
        raise SystemExit(f"no {path.name}: run scripts/split_demand.py --ratio {ratio:g}")
    info = json.loads(info_path.read_text())
    if info["data_version"] != data_version:
        raise SystemExit("demand split was built on another data version: rerun split_demand.py")
    split = pd.read_parquet(path)
    out = panel.merge(split, on=["stock_code", "week"], how="left")
    return out.assign(units_bulk=out["units_bulk"].fillna(0.0))


def apply_ratio(model, ratio: float, default_ratio: float) -> str | None:
    """Mark a non-default bulk threshold in the model name (suffix -r<ratio>); returns the
    model description with the threshold (None for models without a description)."""
    if ratio != default_ratio:
        model.name = f"{model.name}-r{ratio:g}"
    description = getattr(model, "description", None)
    if description:
        description += f" Bulk line: quantity > {ratio:g}x the product's median line quantity."
    return description


def load_panel(processed, meta: dict, ratio: float, target: str) -> pd.DataFrame:
    panel = pd.read_parquet(processed / "panel_weekly.parquet")
    panel = with_bulk(panel, processed, meta["data_version"], ratio)
    if target == "item":
        panel = panel.assign(units=panel["units"] - panel["units_bulk"])
    return panel


def prepare(
    model_config,
    set_: str = "focus",
    origins: str = "tuning",
    target: str = "total",
    level: str = "product",
    cache: dict | None = None,
) -> Prepared:
    """The run of one model config on a set and origin kind (cache: shares panels and wide
    matrices between runs with the same bulk ratio, target and level)."""
    cache = {} if cache is None else cache
    bt = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    mcfg = yaml.safe_load(open(model_config))
    processed = data_dir() / "processed"
    meta = json.loads((processed / "panel_meta.json").read_text())
    default_ratio = bt["segments"]["syntetos_boylan"]["max_order_ratio"]
    ratio = mcfg.get("bulk_ratio", default_ratio)
    seg = pd.read_parquet(processed / "segments.parquet").set_index("stock_code")
    label = seg["abc"] + "-" + seg["sb_class"]
    categories = load_categories(processed, meta["data_version"])
    pool_by = mcfg.get("pool_by", "segment")
    key = (ratio, target, level)
    if key not in cache:
        panel = load_panel(processed, meta, ratio, target)
        if level == "category":
            panel = category_panel(panel, categories)
        cache[key] = (panel, wide_units(panel))
    panel, wide = cache[key]
    if level == "category":
        if mcfg["name"] == "topdown" or pool_by != "segment":
            raise SystemExit("--level category forecasts the categories themselves: no topdown "
                             "/ pool_by")  # fmt: skip
        label = pd.Series(panel["stock_code"].unique(), index=panel["stock_code"].unique())
        set_ = "category"
    model = load_model(mcfg, pool_labels(pool_by, label, categories), categories)
    description = apply_ratio(model, ratio, default_ratio)
    if pool_by == "category":
        model.name += "-poolcat"
        description = (description or "") + " Intervals pooled per product category."
    if set_ == "focus":
        skus = pd.Index(bt["focus_set"]["stock_codes"])
        if bt["focus_set"]["data_version"] != meta["data_version"]:
            raise SystemExit("focus set was built on another data version: rerun segment.py")
    else:
        skus = pd.Index(sorted(panel["stock_code"].unique()))
    weeks = origin_weeks(bt["origins"][origins])
    config = {
        "model": mcfg,
        "model_name": model.name,
        "model_description": description,
        "bulk_ratio": ratio,
        "target": target,
        "level": level,
        "pool_by": pool_by,
        "set": set_,
        "origins": origins,
        "n_origins": len(weeks),
        "backtest": {k: v for k, v in bt.items() if k not in ("focus_set", "segments")},
    }
    name = f"{model.name}{'-item' if target == 'item' else ''}-{set_}"  # set: category
    if origins == "test":
        name += "-test"
    return Prepared(name=name, model=model, panel=panel, wide=wide, skus=skus, origins=weeks,
                    horizons=bt["horizons"], quantiles=bt["quantiles"], levels=bt["intervals"],
                    weight_weeks=bt["revenue_weight_weeks"], labels=label, config=config,
                    data_version=meta["data_version"])  # fmt: skip


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("model_config")
    p.add_argument("--set", choices=["focus", "full"], default="focus")
    p.add_argument("--origins", choices=["tuning", "test"], default="tuning")
    p.add_argument("--final", action="store_true", help="required for the test origins")
    p.add_argument("--target", choices=["total", "item"], default="total")
    p.add_argument("--level", choices=["product", "category"], default="product")
    p.add_argument("--jobs", type=int, default=default_jobs(), help="worker processes")
    a = p.parse_args()
    if a.origins == "test" and not a.final:
        p.error("test origins are used once, at the end: add --final")

    prep = prepare(a.model_config, a.set, a.origins, a.target, a.level)
    fcs, rows = [], []
    with RunLogger(prep.config, name=prep.name, data_version=prep.data_version) as run:
        print(run.dir)
        for _, origin, fc, r, seconds, recs in schedule({prep.name: prep}, jobs=a.jobs):
            if fc is None:
                raise RuntimeError(f"{origin.date()} failed:\n{seconds}")
            log_origin(run, prep, origin, recs)
            fcs.append(fc)
            rows.append(r)
            print(f"{origin.date()}: {fc['stock_code'].nunique()} products, "
                  f"{len(r)} rows, {seconds:.1f} s")  # fmt: skip
        for r in finish(run, prep, fcs, rows):
            print(f"h={r['h']}: MASE {r['mase']:.3f} (w {r['mase_w']:.3f}), "
                  f"CRPS {r['crps']:.3f}, cover80 {r['cover_0.8']:.2f}, "
                  f"cover95 {r['cover_0.95']:.2f}")  # fmt: skip


if __name__ == "__main__":
    main()
