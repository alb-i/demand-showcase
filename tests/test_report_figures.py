"""scripts/report_figures.py: cost at the operating points (README figure)."""

import importlib.util
import sys
import types

import pandas as pd

from retail.io import REPO_DIR


def load(monkeypatch):
    monkeypatch.syspath_prepend(str(REPO_DIR / "scripts"))
    spec = importlib.util.spec_from_file_location("rf", REPO_DIR / "scripts" / "report_figures.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_operating_costs_picks_the_operating_points(monkeypatch, tmp_path):
    mod = load(monkeypatch)
    rows = []
    for lead in (1, 2):
        for pol, values in (("naive", [0.0, 1.0]), ("normal", [0.5, 0.9]),
                            ("quantile", [0.7, 0.925])):  # fmt: skip
            for v in values:
                for margin in (0.4, 0.25):
                    rows.append({"lead": lead, "policy": pol, "value": v, "margin": margin,
                                 "holding_rate": 0.25, "holding_cost": 10 * v + lead,
                                 "lost_margin": 100 - 50 * v, "total_cost": 110 - 40 * v + lead,
                                 "fill_rate": 0.7 + 0.2 * v, "write_down_full": 1.0})  # fmt: skip
    m = pd.DataFrame(rows)
    fake = types.ModuleType("policy_report")
    fake.sim_run = lambda lead, origins: ("run", m[m["lead"] == lead], None)
    fake.base_grid = importlib.import_module("policy_report").base_grid  # the real one
    monkeypatch.setitem(sys.modules, "policy_report", fake)
    op = tmp_path / "configs"
    op.mkdir()
    pts = "[{naive: {buffer: 0.0}, normal: {alpha: 0.5}, quantile: {tau: 0.7}}, " \
          "{naive: {buffer: 1.0}, normal: {alpha: 0.9}, quantile: {tau: 0.925}}]"  # fmt: skip
    (op / "operating_point.yaml").write_text(
        f"lead_time:\n  1:\n    points: {pts}\n  2:\n    points: {pts}\n")  # fmt: skip
    monkeypatch.setattr(mod, "REPO_DIR", tmp_path)
    t = mod.operating_costs(leads=(1, 2), reference=1.0).set_index(["L", "policy"])
    assert len(t) == 6
    assert t.loc[(1, "quantile"), "value"] == 0.925 and t.loc[(2, "normal"), "value"] == 0.9
    assert t.loc[(2, "naive"), "total"] == 110 - 40 + 2  # base margin 0.4 rows only
    assert t.loc[(1, "quantile"), "holding"] == 10 * 0.925 + 1
    monkeypatch.setattr(mod, "FIG", tmp_path)
    mod.fig_costs(t.reset_index())
    mod.fig_costs_client(t.reset_index())
    for name in ("costs_test", "costs_client"):
        assert (tmp_path / f"{name}.png").exists() and (tmp_path / f"{name}.pdf").exists()
