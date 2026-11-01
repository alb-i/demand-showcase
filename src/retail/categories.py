"""Product categories from the descriptions: ordered keyword rules in
configs/categories.yaml (the first matching rule wins; `none` phrases veto a rule), per-product
overrides, "other" when nothing matches."""

import re
from dataclasses import dataclass

import pandas as pd
import yaml

from retail.io import REPO_DIR

CONFIG = REPO_DIR / "configs" / "categories.yaml"
OTHER = "other"


def _pattern(phrases) -> re.Pattern | None:
    """Whole-word match of any phrase (any run of spaces between its words)."""
    if not phrases:
        return None
    alt = "|".join(r"\s+".join(map(re.escape, p.split())) for p in phrases)
    return re.compile(rf"(?<![A-Z0-9'])(?:{alt})(?![A-Z'])")


@dataclass
class Rule:
    name: str
    label: str
    any: re.Pattern
    none: re.Pattern | None

    def matches(self, text: str) -> bool:
        return bool(self.any.search(text)) and not (self.none and self.none.search(text))


def load_rules(cfg: dict | None = None) -> tuple[list[Rule], dict[str, str]]:
    """Rules (in order) and overrides from the config dict (default: configs/categories.yaml)."""
    cfg = cfg if cfg is not None else yaml.safe_load(CONFIG.read_text())
    names = [r["name"] for r in cfg["rules"]]
    if len(set(names)) != len(names) or OTHER in names:
        raise ValueError("category names must be unique and not 'other'")
    rules = [Rule(r["name"], r.get("label", r["name"]), _pattern(r["any"]),
                  _pattern(r.get("none"))) for r in cfg["rules"]]  # fmt: skip
    overrides = {str(k): v for k, v in (cfg.get("overrides") or {}).items()}
    unknown = set(overrides.values()) - set(names) - {OTHER}
    if unknown:
        raise ValueError(f"overrides name unknown categories: {sorted(unknown)}")
    return rules, overrides


def classify(description: str, rules: list[Rule]) -> str:
    text = str(description).upper()
    return next((r.name for r in rules if r.matches(text)), OTHER)


def categorize(descriptions: pd.Series, cfg: dict | None = None) -> pd.Series:
    """stock_code-indexed descriptions -> category per product."""
    rules, overrides = load_rules(cfg)
    out = descriptions.map(lambda d: classify(d, rules))
    hit = out.index.isin(list(overrides))
    out[hit] = [overrides[c] for c in out.index[hit]]
    return out.rename("category")


def labels(cfg: dict | None = None) -> dict[str, str]:
    rules, _ = load_rules(cfg)
    return {r.name: r.label for r in rules} | {OTHER: "Other"}


def category_panel(panel: pd.DataFrame, categories: pd.Series, drop=("non_product",)):
    """Weekly panel per category (stock_code = category name): units, revenue and units_bulk
    (if present) summed over its products, NaN in closed weeks; categories in `drop` left out;
    products without a category count as other."""
    p = panel.assign(stock_code=panel["stock_code"].map(categories).fillna(OTHER).to_numpy())
    p = p[~p["stock_code"].isin(list(drop))]
    cols = [c for c in ("units", "revenue", "units_bulk") if c in p]
    g = p.groupby(["stock_code", "week"])
    out = g[cols].sum(min_count=1)
    out["closed"] = g["closed"].any()
    return out.reset_index()


def load_categories(processed, data_version: str) -> pd.Series:
    """stock_code -> category from scripts/categorize.py, checked against the data version."""
    import json
    from pathlib import Path

    path, info = Path(processed) / "categories.parquet", Path(processed) / "categories.json"
    if not path.exists() or not info.exists():
        raise SystemExit("no categories.parquet: run scripts/categorize.py")
    if json.loads(info.read_text())["data_version"] != data_version:
        raise SystemExit("categories were built on another data version: rerun categorize.py")
    return pd.read_parquet(path).set_index("stock_code")["category"]
