import math

import numpy as np
import pandas as pd
import pytest
from conftest import lines

from retail.cleaning import (
    bulk_candidates,
    classify_codes,
    clean,
    data_version,
    load_config,
    match_corrections,
    r1_overlap,
    r2_duplicates,
    r4_non_product,
    r5_adjustments,
    r6_corrections,
    r7_bulk,
    reconcile,
    totals,
    upper_case_codes,
)


def test_load_config_merges_base(tmp_path):
    (tmp_path / "a.yaml").write_text("x: 1\nnested: {a: 1, b: 2}\n")
    (tmp_path / "b.yaml").write_text("base: a.yaml\nnested: {b: 3}\ny: 2\n")
    assert load_config(tmp_path / "b.yaml") == {"x": 1, "nested": {"a": 1, "b": 3}, "y": 2}


def test_dedup_variant_differs_only_in_duplicates(cfg):
    from conftest import CONFIG

    dedup = load_config(CONFIG.parent / "cleaning-dedup.yaml")
    assert {k for k in cfg if cfg[k] != dedup[k]} == {"variant", "duplicates"}


def test_data_version_depends_on_config_and_commit(cfg):
    v = data_version(cfg, "abc1234")
    assert len(v) == 8
    assert v == data_version(dict(cfg), "abc1234")
    assert v != data_version(cfg, "abc1235")
    assert v != data_version({**cfg, "duplicates": "drop"}, "abc1234")


def test_r1_overlap_drops_copy_in_first_sheet(cfg):
    first = lines(
        ("1", "10001", 1, "2010-11-30 10:00", 1.0, 1),
        ("2", "10001", 1, "2010-12-01 09:00", 1.0, 1),
        sheet="Year 2009-2010",
    )
    second = lines(("2", "10001", 1, "2010-12-01 09:00", 1.0, 1))
    df = pd.concat([first, second], ignore_index=True)
    assert list(r1_overlap(df, cfg)) == [False, True, False]


def test_r2_duplicates_keep_and_drop(cfg):
    df = lines(
        ("1", "10001", 1, "2011-01-03 10:00", 1.0, 1),
        ("1", "10002", 1, "2011-01-03 10:00", 1.0, 1),
        ("1", "10001", 1, "2011-01-03 10:00", 1.0, 1),
        ("1", "10001", 2, "2011-01-03 10:00", 1.0, 1),
    )
    assert not r2_duplicates(df, cfg).any()
    assert list(r2_duplicates(df, {**cfg, "duplicates": "drop"})) == [False, False, True, False]
    with pytest.raises(ValueError):
        r2_duplicates(df, {**cfg, "duplicates": "maybe"})


def test_upper_case_codes(cfg):
    df = lines(("1", "85123a", 1, "2011-01-03", 1.0, 1), ("1", "85123A", 1, "2011-01-03", 1.0, 1))
    assert list(upper_case_codes(df, cfg)["stock_code"]) == ["85123A", "85123A"]
    assert list(upper_case_codes(df, {**cfg, "upper_case_codes": False})["stock_code"]) == [
        "85123a",
        "85123A",
    ]


def test_classify_codes(cfg):
    codes = pd.Series(
        ["85123A", "22423", "DCGS0058", "SP1002", "POST", "GIFT_0001_20", "ADJUST2", "WHAT"],
        dtype="string",
    )
    kinds = classify_codes(codes, cfg)
    assert list(kinds[:7]) == ["product"] * 4 + ["non_product"] * 3
    assert pd.isna(kinds.iloc[7])


def test_r4_non_product_removes_services_and_fails_on_unknown(cfg):
    df = upper_case_codes(
        lines(
            ("1", "22423", 1, "2011-01-03", 12.75, 1),
            ("1", "POST", 1, "2011-01-03", 18.0, 1),
            ("C2", "AMAZONFEE", -1, "2011-01-03", 5000.0, None),
            ("1", "gift_0001_20", 1, "2011-01-03", 17.0, 1),
        ),
        cfg,
    )
    assert list(r4_non_product(df, cfg)) == [False, True, True, True]
    with pytest.raises(ValueError, match="XYZ"):
        r4_non_product(lines(("1", "XYZ", 1, "2011-01-03", 1.0, 1)), cfg)


def test_r5_adjustments(cfg):
    df = lines(
        ("1", "22423", 3, "2011-01-03", 12.75, 1),  # sale
        ("2", "22423", -10, "2011-01-03", 0.0, None, "damaged"),  # stock adjustment
        ("3", "22423", 5, "2011-01-03", 0.0, None, "found"),  # price 0
        ("C4", "22423", -1, "2011-01-04", 12.75, 1),  # cancellation
        ("C5", "22423", 1, "2011-01-04", 12.75, 1),  # C with positive quantity
    )
    assert list(r5_adjustments(df, cfg)) == [False, True, True, False, True]


def test_match_corrections_exact_quantity_within_window_latest_first():
    df = lines(
        ("1", "A1", 10, "2011-01-03 10:00", 1.0, 7),  # older sale, same qty
        ("2", "A1", 10, "2011-01-05 10:00", 1.0, 7),  # latest earlier sale -> matched
        ("C3", "A1", -10, "2011-01-06 10:00", 1.0, 7),
        ("C4", "A1", -10, "2011-01-07 10:00", 1.0, 7),  # takes the remaining sale 1 (4 days)
        ("5", "B1", 4, "2011-01-03 10:00", 1.0, 7),
        ("C6", "B1", -4, "2011-01-11 10:00", 1.0, 7),  # 8 days later: a return
        ("7", "C1", 6, "2011-01-03 10:00", 1.0, 7),
        ("C8", "C1", -5, "2011-01-03 11:00", 1.0, 7),  # other quantity: a return
        ("9", "D1", 6, "2011-01-03 10:00", 1.0, 7),
        ("C10", "D1", -6, "2011-01-03 11:00", 1.0, 8),  # other customer: a return
        ("C11", "E1", -2, "2011-01-03 11:00", 1.0, None),  # no customer: a return
    )
    sale_idx, cancel_idx = match_corrections(df, 7)
    assert dict(zip(cancel_idx, sale_idx, strict=True)) == {2: 1, 3: 0}


def test_match_corrections_never_matches_a_later_sale():
    df = lines(
        ("C1", "A1", -3, "2011-01-03 10:00", 1.0, 7),
        ("2", "A1", 3, "2011-01-04 10:00", 1.0, 7),
    )
    sale_idx, cancel_idx = match_corrections(df, 7)
    assert len(sale_idx) == len(cancel_idx) == 0


def test_r6_corrections_removes_both_lines(cfg):
    df = lines(
        ("1", "23843", 80995, "2011-12-09 09:15", 2.08, 16446),
        ("C2", "23843", -80995, "2011-12-09 09:27", 2.08, 16446),
        ("3", "23843", 1, "2011-12-09 09:30", 2.08, 1),
    )
    assert list(r6_corrections(df, cfg)) == [True, True, False]


def test_bulk_candidates_median_mad_rule():
    q = [1, 2, 2, 3, 4, 500] + [6, 6, 6, 600]
    codes = ["A"] * 6 + ["B"] * 4
    rows = zip(codes, q, strict=True)
    df = lines(*[(str(i), c, n, "2011-01-03", 1.0, 1) for i, (c, n) in enumerate(rows)])
    cand = bulk_candidates(df, k=5)
    # A: log quantities, median log(2.5), MAD > 0, 500 is far out; B: MAD 0 -> z = inf
    assert list(cand["quantity"]) == [600, 500]
    assert math.isinf(cand["z"].iloc[0]) and np.isfinite(cand["z"].iloc[1])
    lq = np.log(np.array([1, 2, 2, 3, 4, 500.0]))
    med = np.median(lq)
    assert cand["z"].iloc[1] == pytest.approx((lq[-1] - med) / np.median(np.abs(lq - med)))


def test_r7_bulk_only_listed_lines(cfg):
    df = lines(("1", "A1", 5000, "2011-01-03", 0.1, 1), ("2", "A1", 5000, "2011-01-03", 0.1, 1))
    assert not r7_bulk(df, cfg).any()
    listed = {**cfg, "bulk": {**cfg["bulk"], "exclude": [{"invoice": 2, "stock_code": "A1"}]}}
    assert list(r7_bulk(df, listed)) == [False, True]


def test_clean_books_every_line_once_and_reconciles(cfg):
    df = pd.concat(
        [
            lines(("0", "10001", 2, "2010-12-01 09:00", 1.0, 1), sheet="Year 2009-2010"),
            lines(
                ("0", "10001", 2, "2010-12-01 09:00", 1.0, 1),  # demand
                ("1", "10001a", 3, "2011-01-03", 2.0, 1),  # demand (code upper-cased)
                ("1", "POST", 1, "2011-01-03", 18.0, 1),  # R4
                ("2", "10001", -5, "2011-01-03", 0.0, None),  # R5
                ("3", "10002", 4, "2011-01-03", 1.5, 2),  # R6
                ("C4", "10002", -4, "2011-01-04", 1.5, 2),  # R6
                ("C5", "10001", -1, "2011-01-20", 1.0, 1),  # return
            ),
        ],
        ignore_index=True,
    )
    out = clean(df, cfg)
    assert list(out.sales["stock_code"]) == ["10001", "10001A"]
    assert list(out.returns["invoice"]) == ["C5"]
    assert list(out.fate) == [
        "R1 sheet overlap",
        "demand",
        "demand",
        "R4 non-product codes",
        "R5 adjustments (price/quantity)",
        "R6 order corrections",
        "R6 order corrections",
        "return",
    ]
    parts = out.removed.to_dict("records") + [totals(out.sales), totals(out.returns)]
    assert reconcile(totals(df), parts)
    assert not reconcile(totals(df), parts[1:])
