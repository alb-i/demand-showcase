import importlib.util
import json
import sys

import pytest
import yaml

from retail.io import REPO_DIR


@pytest.fixture(scope="module")
def rb():
    sys.path.insert(0, str(REPO_DIR / "scripts"))
    spec = importlib.util.spec_from_file_location("rb", REPO_DIR / "scripts" / "run_batch.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_run(root, rid, status="finished", origins="tuning", minutes=10, extra=None):
    d = root / rid
    d.mkdir()
    meta = {"status": status, "start_time": "2000-01-01T10:00:00+01:00"}
    if status == "finished":
        meta["end_time"] = f"2000-01-01T10:{minutes:02d}:00+01:00"
    (d / "meta.json").write_text(json.dumps(meta))
    (d / "config.yaml").write_text(yaml.safe_dump({"origins": origins} | (extra or {})))


def test_finished_runs_newest_finished_per_name_and_origins(tmp_path, rb):
    make_run(tmp_path, "20000101-100000-ma4-focus", minutes=10)
    make_run(tmp_path, "20000101-110000-ma4-focus", minutes=20)  # newer wins
    make_run(tmp_path, "20000101-120000-ma4-focus-test", status="crashed", origins="test")
    make_run(tmp_path, "20000101-130000-x-sum-paths-focus", extra={"horizon_sums": {}})
    make_run(tmp_path, "20000101-140000-best-focus", extra={"derived_from": "a"})
    (tmp_path / "notarun").mkdir()
    done = rb.finished_runs(tmp_path)
    assert done == {("ma4-focus", "tuning"): 1200.0}  # crashed / derived runs do not count


def test_per_origin_cost(rb):
    assert rb.per_origin_cost(None, 22) == rb.DEFAULT_SECONDS
    assert rb.per_origin_cost(220.0, 22) == pytest.approx(60.0)  # 6 workers, 22 origins
    assert rb.per_origin_cost(100.0, 3) == pytest.approx(100.0)  # fewer origins than workers


def test_batch_refuses_test_origins_without_final(tmp_path):
    import subprocess

    b = tmp_path / "b.yaml"
    b.write_text("runs: []\n")
    r = subprocess.run([sys.executable, str(REPO_DIR / "scripts" / "run_batch.py"), str(b),
                        "--origins", "test"], capture_output=True, text=True)  # fmt: skip
    assert r.returncode == 2 and "--final" in r.stderr
