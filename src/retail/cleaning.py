"""Cleaning rules R1-R7 for Online Retail II, each a pure function of the raw lines.

Every removal rule returns a boolean mask over the lines it is given (True = remove); `clean`
applies them in order and books rows, units and revenue per rule, so that
raw totals = kept sales + returns + removals (checked by `reconcile`).
Decisions behind the rules: configs/cleaning.yaml and the step log.
"""

import fnmatch
import hashlib
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

KEY = ["invoice", "stock_code", "description", "quantity", "invoice_date", "price", "customer_id"]


def load_config(path: Path) -> dict:
    """YAML config; `base: other.yaml` (relative to the file) is loaded first and overridden
    key by key (nested dicts merged)."""
    path = Path(path)
    cfg = yaml.safe_load(path.read_text())
    base = cfg.pop("base", None)
    return merge(load_config(path.parent / base), cfg) if base else cfg


def merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in b.items():
        out[k] = merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def data_version(cfg: dict, commit: str) -> str:
    """sha256 of the resolved cleaning config and the code commit, first 8 hex digits."""
    text = json.dumps(cfg, sort_keys=True) + "\n" + commit
    return hashlib.sha256(text.encode()).hexdigest()[:8]


def git_commit(repo: Path) -> str:
    """HEAD commit, with "-dirty" if tracked files differ from it."""
    run = lambda *a: subprocess.run(  # noqa: E731
        ["git", *a], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()
    return run("rev-parse", "--short", "HEAD") + (
        "-dirty" if run("status", "--porcelain", "-uno") else ""
    )


def is_cancellation(df: pd.DataFrame) -> pd.Series:
    return df["invoice"].str.startswith("C")


# --- rules ------------------------------------------------------------------------------------


def r1_overlap(df: pd.DataFrame, cfg: dict) -> pd.Series:
    """Lines of the overlap sheet from `from_date` on (copied in the next sheet)."""
    o = cfg["overlap"]
    return (df["sheet"] == o["sheet"]) & (df["invoice_date"] >= pd.Timestamp(o["from_date"]))


def r2_duplicates(df: pd.DataFrame, cfg: dict) -> pd.Series:
    """`duplicates: drop`: every exact copy of an earlier line; `keep`: nothing."""
    if cfg["duplicates"] == "keep":
        return pd.Series(False, index=df.index)
    if cfg["duplicates"] != "drop":
        raise ValueError(f"duplicates must be keep or drop, not {cfg['duplicates']!r}")
    return df.duplicated(KEY, keep="first")


def upper_case_codes(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """R3 (transform, no removal): 85123a -> 85123A."""
    if not cfg["upper_case_codes"]:
        return df
    return df.assign(stock_code=df["stock_code"].str.upper())


def classify_codes(codes: pd.Series, cfg: dict) -> pd.Series:
    """ "product", "non_product" or <NA> (in neither list) per code."""
    pattern = re.compile(cfg["product_pattern"])

    def one(code: str):
        if pattern.fullmatch(code) or any(
            fnmatch.fnmatchcase(code, p) for p in cfg["products_extra"]
        ):
            return "product"
        if any(fnmatch.fnmatchcase(code, p) for p in cfg["non_product"]):
            return "non_product"
        return None

    uniq = pd.Series(codes.unique())
    kind = dict(zip(uniq, uniq.map(one), strict=True))
    return codes.map(kind).astype("string")


def r4_non_product(df: pd.DataFrame, cfg: dict) -> pd.Series:
    kind = classify_codes(df["stock_code"], cfg)
    unknown = sorted(df.loc[kind.isna(), "stock_code"].unique())
    if unknown:
        raise ValueError(f"stock codes in neither products nor non_product: {unknown}")
    return kind == "non_product"


def r5_adjustments(df: pd.DataFrame, cfg: dict) -> pd.Series:
    """Not a sale and not a cancellation: price <= 0 or quantity <= 0 outside C invoices,
    and C lines with price <= 0 or quantity >= 0."""
    c = is_cancellation(df)
    bad_sale = ~c & ((df["price"] <= 0) | (df["quantity"] <= 0))
    bad_cancel = c & ((df["price"] <= 0) | (df["quantity"] >= 0))
    return bad_sale | bad_cancel


def match_corrections(df: pd.DataFrame, days: float) -> tuple[pd.Index, pd.Index]:
    """Order corrections: (sale index, cancellation index) pairs with the same customer,
    stock code and quantity, the cancellation 0..`days` days after the sale. Cancellations
    in time order; each takes the latest unmatched earlier sale; each sale is used once."""
    c = is_cancellation(df)
    has_cust = df["customer_id"].notna()
    sales = df[~c & has_cust]
    cancels = df[c & has_cust].sort_values("invoice_date", kind="stable")
    by_key: dict[tuple, list] = {}
    for idx, (cust, code, q, t) in zip(
        sales.index,
        sales[["customer_id", "stock_code", "quantity", "invoice_date"]].itertuples(index=False),
        strict=True,
    ):
        by_key.setdefault((cust, code, q), []).append((t, idx))
    for v in by_key.values():
        v.sort()
    window = pd.Timedelta(days=days)
    sale_idx, cancel_idx = [], []
    for idx, (cust, code, q, t) in zip(
        cancels.index,
        cancels[["customer_id", "stock_code", "quantity", "invoice_date"]].itertuples(index=False),
        strict=True,
    ):
        cands = by_key.get((cust, code, -q))
        if not cands:
            continue
        for i in range(len(cands) - 1, -1, -1):
            ts, s = cands[i]
            if ts <= t:
                if t - ts <= window:
                    sale_idx.append(s)
                    cancel_idx.append(idx)
                    del cands[i]
                break
    return pd.Index(sale_idx), pd.Index(cancel_idx)


def r6_corrections(df: pd.DataFrame, cfg: dict) -> pd.Series:
    """Both lines of every order correction (see match_corrections)."""
    sale_idx, cancel_idx = match_corrections(df, cfg["cancellations"]["correction_days"])
    return df.index.isin(sale_idx.append(cancel_idx))


def bulk_candidates(sales: pd.DataFrame, k: float) -> pd.DataFrame:
    """Sales lines with log(quantity) > median + k * MAD of the product's log quantities
    (for a product with MAD 0 every line above its median is a candidate, z = inf), with
    column z, largest quantity first."""
    lq = np.log(sales["quantity"].astype(float))
    g = lq.groupby(sales["stock_code"])
    med = g.transform("median")
    mad = (lq - med).abs().groupby(sales["stock_code"]).transform("median")
    z = ((lq - med) / mad.where(mad > 0)).where(mad > 0, np.where(lq > med, np.inf, 0.0))
    out = sales.assign(z=z)[z > k]
    return out.sort_values("quantity", ascending=False, kind="stable")


def r7_bulk(df: pd.DataFrame, cfg: dict) -> pd.Series:
    """Lines listed in bulk.exclude as {invoice, stock_code} after the review by hand."""
    ex = {(str(e["invoice"]), str(e["stock_code"])) for e in cfg["bulk"]["exclude"]}
    pairs = zip(df["invoice"], df["stock_code"], strict=True)
    return pd.Series([p in ex for p in pairs], index=df.index)


RULES = [
    ("R1 sheet overlap", r1_overlap),
    ("R2 duplicate lines", r2_duplicates),
    ("R4 non-product codes", r4_non_product),
    ("R5 adjustments (price/quantity)", r5_adjustments),
    ("R6 order corrections", r6_corrections),
    ("R7 bulk orders (reviewed)", r7_bulk),
]


@dataclass
class Cleaned:
    sales: pd.DataFrame  # demand lines
    returns: pd.DataFrame  # cancellations that are returns (negative quantities)
    removed: pd.DataFrame  # one row per rule: rule, lines, units, revenue
    fate: pd.Series  # per raw line: the rule that removed it, "demand" or "return"


def book(rule: str, lines: pd.DataFrame) -> dict:
    return {
        "rule": rule,
        "lines": len(lines),
        "units": int(lines["quantity"].sum()),
        "revenue": float((lines["quantity"] * lines["price"]).sum()),
    }


def clean(raw: pd.DataFrame, cfg: dict) -> Cleaned:
    df = raw
    rows = []
    fate = pd.Series("", index=raw.index, dtype="string")
    for i, (name, rule) in enumerate(RULES):
        if i == 2:  # R3 transform before the code-based rules
            df = upper_case_codes(df, cfg)
        mask = np.asarray(rule(df, cfg), dtype=bool)
        rows.append(book(name, df[mask]))
        fate[df.index[mask]] = name
        df = df[~mask]
    c = is_cancellation(df)
    fate[df.index[~c]] = "demand"
    fate[df.index[c]] = "return"
    return Cleaned(sales=df[~c], returns=df[c], removed=pd.DataFrame(rows), fate=fate)


def totals(df: pd.DataFrame) -> dict:
    return book("", df) | {"rule": "total"}


def reconcile(raw: dict, parts: list[dict], tol: float = 0.01) -> bool:
    """raw lines/units/revenue == sum over parts (revenue within tol)."""
    s = {k: sum(p[k] for p in parts) for k in ("lines", "units", "revenue")}
    return (
        s["lines"] == raw["lines"]
        and s["units"] == raw["units"]
        and abs(s["revenue"] - raw["revenue"]) <= tol
    )
