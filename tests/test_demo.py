"""Static demo: product pick, re-priceable aggregates, data files, operating point."""

import importlib.util
import json

import numpy as np
import pandas as pd
import pytest
from workbench.inventory import Costs, price, simulate, summarize

from retail.demo import aggregate, grid, js_data, pick_products, reprice, rounded
from retail.io import REPO_DIR


def test_grid_adds_extra_values_sorted_unique():
    assert grid(0.5, 0.6, 0.05) == [0.5, 0.55, 0.6]
    assert grid(0.5, 0.6, 0.05, [0.525, 0.55]) == [0.5, 0.525, 0.55, 0.6]
    assert grid(0.0, 2.0, 0.05)[-1] == 2.0 and len(grid(0.0, 2.0, 0.05)) == 41


def table(n_smooth=40, n_erratic=50, n_lumpy=6, n_int=2, n_xmas=5):
    rows = []
    for cls, n, cat in [("smooth", n_smooth, "bags"), ("erratic", n_erratic, "bags"),
                        ("lumpy", n_lumpy, "toys"), ("intermittent", n_int, "toys"),
                        ("lumpy", n_xmas, "christmas")]:  # fmt: skip
        for i in range(n):
            rows.append({"series_id": f"{cls[:2]}{cat[:2]}{i}", "revenue": 1000.0 - i,
                         "sb_class": cls, "category": cat})  # fmt: skip
    return pd.DataFrame(rows)


def test_pick_products_stratified_and_deterministic():
    t = table()
    ids = pick_products(t, n=30, n_seasonal=4, min_class=3)
    assert len(ids) == 30 and len(set(ids)) == 30
    picked = t.set_index("series_id").loc[ids]
    assert (picked["category"] == "christmas").sum() == 4
    rest = picked[picked["category"] != "christmas"]["sb_class"].value_counts()
    assert rest["intermittent"] == 2  # all there are (fewer than min_class)
    assert rest["lumpy"] == 3 and rest["erratic"] > rest["smooth"] > 3
    assert "smba0" in ids and "smba39" in ids  # top and bottom of the revenue ranks
    assert pick_products(t.sample(frac=1, random_state=1), n=30) == ids


def test_aggregate_repriced_equals_the_workbench_totals():
    rng = np.random.default_rng(0)
    n, m = 12, 20
    demand = rng.poisson(3, (n, m)).astype(float)
    demand[0, :5] = np.nan
    levels = rng.uniform(2, 12, (n, m))
    levels[1, -3:] = np.nan
    p = rng.uniform(1, 9, n)
    seasonal = (np.arange(n) % 3 == 0).astype(float)
    summary = summarize(simulate(demand, levels, 2))
    agg = aggregate(summary, p, seasonal)
    json.dumps(agg)  # plain numbers only
    for margin, hold, wd in [(0.4, 0.25, 0.0), (0.25, 0.4, 0.5), (0.6, 0.15, 1.0)]:
        want = price(summary, p, Costs(margin=margin, holding_rate=hold, write_down=wd), seasonal)
        got = reprice(agg, margin, hold, wd)
        assert got.keys() == want.keys()
        for k in want:
            assert got[k] == pytest.approx(want[k], rel=1e-12), k


def test_rounded_and_js_data():
    assert rounded([1.23456, np.nan, np.inf, 2]) == [1.23, None, None, 2.0]
    js = js_data("fc-85099B", {"a": rounded([np.nan, 1.5])})
    assert js == '(window.DEMO=window.DEMO||{})["fc-85099B"]={"a":[null,1.5]};\n'
    with pytest.raises(ValueError):
        js_data("x", {"a": float("nan")})


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, REPO_DIR / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_operating_point_per_lead_time(tmp_path):
    mod = load_script("export_static")
    f = tmp_path / "op.yaml"
    pts = [
        "{naive: {buffer: 0.0}, normal: {alpha: 0.5}, quantile: {tau: 0.7}}",
        "{naive: {buffer: 1.0}, normal: {alpha: 0.9}, quantile: {tau: 0.925}}",
    ]
    f.write_text("lead_time:\n  1:\n    points:\n" + "".join(f"    - {p}\n" for p in pts))
    assert mod.operating_point(f) == {"1": {"naive": 1.0, "normal": 0.9, "quantile": 0.925}}
    for policy, values in mod.GRIDS.items():  # every operating point value is on its grid
        assert values == sorted(set(values)), policy
    op = mod.operating_point(REPO_DIR / "configs" / "operating_point.yaml")
    for point in op.values():
        for policy, v in point.items():
            assert v in mod.GRIDS[policy]


def test_demo_pages_load_their_scripts():
    demo = REPO_DIR / "demo"
    for page in ("index", "forecast", "policy", "decision"):
        html = (demo / f"{page}.html").read_text()
        assert '<script src="demo.js">' in html and 'href="style.css"' in html
        assert "fetch(" not in html  # file:// blocks fetch; data come as script files
        assert "data/meta.js" in html
