import importlib.util
import json

import numpy as np
import pandas as pd
import pytest
import yaml
from conftest import W0, panel

from retail.backtest import History, evaluate_origin, wide_units
from retail.categories import category_panel, load_categories
from retail.io import REPO_DIR
from retail.models.split import Split
from retail.models.topdown import TopDown

Q = [0.1, 0.5, 0.9]


def week(i):
    return W0 + pd.Timedelta(weeks=i)


def script(name):
    spec = importlib.util.spec_from_file_location(name, REPO_DIR / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def bulk_panel(series: dict, bulk: dict, closed=()) -> pd.DataFrame:
    p = panel(series, closed=closed)
    b = [(c, week(i), float(v)) for c, vals in bulk.items() for i, v in enumerate(vals)]
    b = pd.DataFrame(b, columns=["stock_code", "week", "units_bulk"])
    p = p.merge(b, on=["stock_code", "week"], how="left")
    return p.assign(units_bulk=p["units_bulk"].fillna(0.0))


def test_category_panel_sums_and_keeps_closed_weeks():
    p = bulk_panel({"a": [1, 2, 3], "b": [10, 20, 30], "c": [5, 5, 5], "x": [7, 7, 7]},
                   {"b": [0, 15, 0]}, closed=(1,))  # fmt: skip
    cats = pd.Series({"a": "bags", "b": "bags", "c": "non_product"})
    out = category_panel(p, cats).set_index(["stock_code", "week"])
    assert sorted(out.index.get_level_values(0).unique()) == ["bags", "other"]  # x: other
    assert out.loc[("bags", week(0)), "units"] == 11 and out.loc[("bags", week(2)), "units"] == 33
    assert np.isnan(out.loc[("bags", week(1)), "units"]) and out.loc[("bags", week(1)), "closed"]
    assert out["units_bulk"].sum() == 15


def test_topdown_points_are_category_forecast_times_share():
    series = {"a": [2, 2, 2, 2, 2, 2], "b": [6, 6, 6, 46, 6, 6], "c": [9, 9, 9, 9, 9, 9]}
    bulk = {"b": [0, 0, 0, 40, 0, 0]}
    p = bulk_panel(series, bulk)
    h = History(p, wide_units(p), week(6))
    cats = pd.Series({"a": "bags", "b": "bags", "c": "toys"})
    td = TopDown({"method": "ma", "window": 4}, {"method": "ma", "window": 52}, share_weeks=52,
                 min_pool=1, categories=cats)  # fmt: skip
    out = td.predict(h, pd.Index(["a", "b", "c"]), [1], Q).set_index("stock_code")
    # bags item demand 8 per week; shares 2/8 and 6/8; b's bulk mean 40 / 6
    assert out.loc["a", "mean"] == pytest.approx(8 * 0.25)
    assert out.loc["b", "mean"] == pytest.approx(8 * 0.75 + 40 / 6)
    assert out.loc["c", "mean"] == pytest.approx(9)
    alone = td.predict(h, pd.Index(["a"]), [1], Q)  # category from all products, not only skus
    assert alone["mean"].iloc[0] == pytest.approx(out.loc["a", "mean"])
    assert td.name == "topdown-ma4-bulk-ma52" and "category" in td.description


def test_topdown_single_product_categories_equal_split():
    rng = np.random.default_rng(3)
    series = {f"s{i}": rng.poisson(4, 30).tolist() for i in range(8)}
    p = bulk_panel(series, {})
    cats = pd.Series({c: c for c in series})  # one product per category, share 1
    skus = pd.Index(sorted(series))
    a, _ = evaluate_origin(TopDown({"method": "ma", "window": 4}, None, min_pool=10,
                                   categories=cats), p, wide_units(p), week(25), skus, [1, 3],
                           Q)  # fmt: skip
    b, _ = evaluate_origin(Split({"method": "ma", "window": 4}, None, min_pool=10), p,
                           wide_units(p), week(25), skus, [1, 3], Q)  # fmt: skip
    pd.testing.assert_frame_equal(a, b)


def test_topdown_no_look_ahead():
    rng = np.random.default_rng(4)
    series, bulk = {}, {}
    for i in range(10):
        item = rng.poisson(3, 30)
        b = np.where(rng.random(30) < 0.1, 100, 0)
        series[f"s{i}"], bulk[f"s{i}"] = (item + b).tolist(), b.tolist()
    p = bulk_panel(series, bulk, closed=(6,))
    cats = pd.Series({c: "a" if int(c[1:]) < 5 else "b" for c in series})
    skus = pd.Index(sorted(series))
    m = TopDown({"method": "tsb", "alpha": 0.2}, {"method": "ma", "window": 52}, min_pool=5,
                categories=cats)  # fmt: skip
    f1, _ = evaluate_origin(m, p, wide_units(p), week(20), skus, [1, 4], Q)
    p2 = p.copy()
    late = p2["week"] >= week(20)
    p2.loc[late, ["units", "units_bulk"]] *= 50
    f2, _ = evaluate_origin(m, p2, wide_units(p2), week(20), skus, [1, 4], Q)
    pd.testing.assert_frame_equal(f1, f2)


def test_load_model_pool_labels_and_configs():
    bt = script("backtest")
    seg, cats = pd.Series({"a": "A-smooth"}), pd.Series({"a": "bags"})
    assert bt.pool_labels("segment", seg, cats) is seg
    assert bt.pool_labels("category", seg, cats) is cats
    with pytest.raises(ValueError):
        bt.pool_labels("abc", seg, cats)
    cfg = yaml.safe_load((REPO_DIR / "configs/models/topdown_ma4_bulkma52.yaml").read_text())
    with pytest.raises(ValueError):
        bt.load_model(cfg, seg)  # needs the categories
    assert isinstance(bt.load_model(cfg, seg, cats), TopDown)
    pool = yaml.safe_load((REPO_DIR / "configs/models/split_ma4_bulkma52_poolcat.yaml").read_text())
    model = bt.load_model(pool, cats)  # pool_by is not a model parameter
    assert pool["pool_by"] == "category" and model.segments is cats


def test_load_categories_checks_version(tmp_path):
    pd.DataFrame({"stock_code": ["a"], "category": ["bags"]}).to_parquet(
        tmp_path / "categories.parquet"
    )
    with pytest.raises(SystemExit):
        load_categories(tmp_path, "v1")  # no json
    (tmp_path / "categories.json").write_text(json.dumps({"data_version": "v1"}))
    assert load_categories(tmp_path, "v1").to_dict() == {"a": "bags"}
    with pytest.raises(SystemExit):
        load_categories(tmp_path, "v2")


def test_bottom_up_sum_and_score():
    bu_mod = script("bottom_up")
    fc = pd.DataFrame({"stock_code": ["a", "b", "c"], "origin": [week(5)] * 3, "h": [1] * 3,
                       "mean": [1.0, 2.0, 4.0]})  # fmt: skip
    bu = bu_mod.bottom_up(fc, pd.Series({"a": "bags", "b": "bags", "c": "toys"}))
    assert bu.set_index("category")["mean"].to_dict() == {"bags": 3.0, "toys": 4.0}
    rows = pd.DataFrame({"stock_code": ["bags", "toys", "easter"], "origin": [week(5)] * 3,
                         "h": [1] * 3, "y": [5.0, 4.0, 2.0], "mean": [4.0, 6.0, 1.0],
                         "scale": [2.0, 1.0, 1.0]})  # fmt: skip
    s = bu_mod.score(rows, bu)
    assert s.loc["bags"].tolist() == [0.5, 1.0] and s.loc["toys"].tolist() == [2.0, 0.0]
    assert s.loc["easter"].tolist() == [1.0, 2.0]  # no product forecast: bottom-up 0


def test_category_table():
    cr = script("compare_runs")
    rows = pd.DataFrame({"stock_code": ["a", "b"], "origin": [week(5)] * 2, "h": [1, 1],
                         "y": [2.0, 4.0], "mean": [1.0, 4.0], "scale": [1.0, 2.0],
                         "scale2": [1.0, 4.0], "weight": [1.0, 1.0], "q0.1": [0.0, 3.0],
                         "q0.5": [1.0, 4.0], "q0.9": [2.0, 5.0],
                         "segment": ["x", "x"]})  # fmt: skip
    t = cr.category_table([("r1", rows, {})], Q, [0.8], pd.Series({"a": "bags"}))
    assert t.loc["bags", ("r1", "mase")] == pytest.approx(1.0)
    assert t.loc["other", ("r1", "mase")] == pytest.approx(0.0)
