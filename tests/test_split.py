import json

import numpy as np
import pandas as pd
import pytest
import yaml
from conftest import W0, panel

from retail.backtest import History, evaluate_origin, wide_units
from retail.compare import common_target, relabel, select_codes
from retail.io import REPO_DIR
from retail.models.baselines import Baseline
from retail.models.split import Split, bulk_units, part_model
from retail.segments import bulk_thresholds, demand_split, split_files

Q = [0.1, 0.5, 0.9]


def week(i):
    return W0 + pd.Timedelta(weeks=i)


def test_bulk_thresholds_and_demand_split():
    sales = pd.DataFrame(
        {
            "stock_code": ["a", "a", "a", "a", "a", "b", "c"],
            "invoice_date": [week(0), week(0), week(1), week(2), week(9), week(1), week(9)],
            "quantity": [2, 3, 100, 2, 500, 7, 1000],
        }
    )
    t = bulk_thresholds(sales, before=week(5), ratio=20)
    assert t.to_dict() == {"a": 20 * 2.5, "b": 20 * 7}  # median over lines before week 5
    split = demand_split(sales, t)
    assert split.to_dict("records") == [
        {"stock_code": "a", "week": week(1), "units_bulk": 100},
        {"stock_code": "a", "week": week(9), "units_bulk": 500},  # threshold fixed
    ]  # c has no line before the cut-off: never bulk


def bulk_panel(series: dict, bulk: dict, closed=()) -> pd.DataFrame:
    p = panel(series, closed=closed)
    b = [(c, week(i), float(v)) for c, vals in bulk.items() for i, v in enumerate(vals)]
    b = pd.DataFrame(b, columns=["stock_code", "week", "units_bulk"])
    p = p.merge(b, on=["stock_code", "week"], how="left")
    return p.assign(units_bulk=p["units_bulk"].fillna(0.0))


def test_split_point_is_item_plus_bulk():
    series = {"x": [10, 2, 3, 50, 2, 1, 3, 2]}
    bulk = {"x": [8, 0, 0, 48, 0, 0, 0, 0]}  # item = 2, 2, 3, 2, 2, 1, 3, 2
    p = bulk_panel(series, bulk)
    h = History(p, wide_units(p), week(8))
    skus = pd.Index(["x"])
    fc = Split({"method": "ma", "window": 4}, {"method": "ma", "window": 8}, min_pool=1)
    out = fc.predict(h, skus, [1, 2], Q).set_index("h")
    assert out.loc[1, "mean"] == pytest.approx(np.mean([2, 1, 3, 2]) + np.mean(bulk["x"]))
    assert out.loc[2, "mean"] == out.loc[1, "mean"]
    item_only = Split({"method": "ma", "window": 4}, None, min_pool=1)
    assert item_only.predict(h, skus, [1], Q)["mean"].iloc[0] == pytest.approx(2.0)
    assert item_only.name == "split-ma4-bulk-0" and "ma4" in item_only.description


def test_split_without_bulk_equals_combined_model():
    rng = np.random.default_rng(0)
    series = {f"s{i}": rng.poisson(5, 30).tolist() for i in range(15)}
    p = bulk_panel(series, {})
    wide = wide_units(p)
    skus = pd.Index(sorted(series))
    a, _ = evaluate_origin(Split({"method": "ma", "window": 4}, None, min_pool=10), p, wide,
                           week(25), skus, [1, 3], Q)  # fmt: skip
    b, _ = evaluate_origin(Baseline("ma", 4, min_pool=10), p, wide, week(25), skus, [1, 3], Q)
    pd.testing.assert_frame_equal(a, b)


def test_split_quantiles_valid_and_no_look_ahead():
    rng = np.random.default_rng(1)
    series, bulk = {}, {}
    for i in range(12):
        item = rng.poisson(3, 30)
        b = np.where(rng.random(30) < 0.1, 200, 0)
        series[f"s{i}"], bulk[f"s{i}"] = (item + b).tolist(), b.tolist()
    p = bulk_panel(series, bulk, closed=(7,))
    skus = pd.Index(sorted(series))
    model = Split({"method": "tsb", "alpha": 0.2}, {"method": "tsb", "alpha": 0.1}, min_pool=5)
    f1, _ = evaluate_origin(model, p, wide_units(p), week(20), skus, [1, 4], Q)  # checks it
    assert (f1[["mean", *(f"q{q:g}" for q in Q)]].to_numpy() >= 0).all()
    p2 = p.copy()
    late = p2["week"] >= week(20)
    p2.loc[late, "units"] *= 50
    p2.loc[late, "units_bulk"] = p2.loc[late, "units"]
    f2, _ = evaluate_origin(model, p2, wide_units(p2), week(20), skus, [1, 4], Q)
    pd.testing.assert_frame_equal(f1, f2)


def test_bulk_units_shape_and_missing_column():
    p = bulk_panel({"x": [5, 1, 2]}, {"x": [4, 0, 0]}, closed=(1,))
    h = History(p, wide_units(p), week(3))
    like = h.units.assign(extra=np.nan)
    b = bulk_units(h, like).iloc[0].tolist()
    assert b[0] == 4.0 and np.isnan(b[1]) and b[2] == 0.0 and np.isnan(b[3])
    with pytest.raises(ValueError):
        bulk_units(History(panel({"x": [1]}), wide_units(panel({"x": [1]})), week(1)), like)
    with pytest.raises(ValueError):
        part_model({"method": "arima"})


def test_split_configs_load():
    import importlib.util

    spec = importlib.util.spec_from_file_location("bt", REPO_DIR / "scripts" / "backtest.py")
    bt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bt)
    names = set()
    for f in sorted((REPO_DIR / "configs" / "models").glob("split_*.yaml")):
        model = bt.load_model(yaml.safe_load(f.read_text()), pd.Series(dtype=str))
        assert isinstance(model, Split)
        names.add(model.name)
    assert len(names) == 5


def test_with_bulk_merges_and_checks_version(tmp_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("bt", REPO_DIR / "scripts" / "backtest.py")
    bt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bt)
    p = panel({"x": [5, 1]})
    split = pd.DataFrame({"stock_code": ["x"], "week": [week(0)], "units_bulk": [4]})
    parquet, info = split_files(tmp_path, 10)
    assert parquet.name == "demand_split_r10.parquet" and info.name == "demand_split_r10.json"
    split.to_parquet(parquet)
    info.write_text(json.dumps({"data_version": "v1"}))
    assert bt.with_bulk(p, tmp_path, "v1", 10)["units_bulk"].tolist() == [4.0, 0.0]
    with pytest.raises(SystemExit):
        bt.with_bulk(p, tmp_path, "v2", 10)  # other data version
    with pytest.raises(SystemExit):
        bt.with_bulk(p, tmp_path, "v1", 20)  # no split file for this threshold


def test_compare_helpers():
    assert common_target([{}, {"target": "total"}]) == "total"
    with pytest.raises(ValueError):
        common_target([{}, {"target": "item"}])
    rows = pd.DataFrame({"stock_code": ["a", "b", "c"]})
    assert select_codes(rows, {"a", "c"})["stock_code"].tolist() == ["a", "c"]
    old = rows.assign(segment=["A-lumpy", "B-smooth", "C-erratic"], y=[1, 2, 3])
    new = relabel(old, pd.Series({"a": "A-smooth", "b": "B-smooth"}))
    assert new["segment"].tolist() == ["A-smooth", "B-smooth", "unclassified"]
    assert new["y"].tolist() == [1, 2, 3] and old["segment"].iloc[0] == "A-lumpy"


def test_bulk_ratio_in_name_and_description():
    import importlib.util

    spec = importlib.util.spec_from_file_location("bt", REPO_DIR / "scripts" / "backtest.py")
    bt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bt)
    cfg = yaml.safe_load(
        (REPO_DIR / "configs" / "models" / "split_ma4_bulkma52.yaml").read_text()
    ) | {"bulk_ratio": 10}
    model = bt.load_model(cfg, pd.Series(dtype=str))  # bulk_ratio is not a model parameter
    text = bt.apply_ratio(model, 10, 20)  # a threshold other than the default
    assert model.name == "split-ma4-bulk-ma52-r10" and "> 10x the product's median" in text
    bt_cfg = yaml.safe_load((REPO_DIR / "configs" / "backtest.yaml").read_text())
    assert bt_cfg["segments"]["syntetos_boylan"]["max_order_ratio"] == 10
    same = Split({"method": "ma", "window": 4}, None)
    assert "> 20x" in bt.apply_ratio(same, 20, 20) and same.name == "split-ma4-bulk-0"
    assert bt.apply_ratio(Baseline("naive"), 10, 20) is None


def test_resolve_latest_run(tmp_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("cr", REPO_DIR / "scripts" / "compare_runs.py")
    cr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cr)
    for run in [
        "20000101-100000-ets-bulk-ma52-focus",
        "20000101-110000-ets-bulk-ma52-focus",
        "20000101-120000-ets-bulk-ma52-r10-focus",
        "20000101-130000-x-ets-bulk-ma52-focus",
    ]:
        (tmp_path / run).mkdir()  # fmt: skip
    assert cr.resolve("latest:ets-bulk-ma52-focus", tmp_path).name == (
        "20000101-110000-ets-bulk-ma52-focus"
    )
    assert cr.resolve("20000101-100000-ets-bulk-ma52-focus", tmp_path).parent == tmp_path
    with pytest.raises(SystemExit):
        cr.resolve("latest:arima-focus", tmp_path)
