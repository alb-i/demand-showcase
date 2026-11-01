"""scripts/publish.py and scripts/check_public.py: manifest selection, run-id rewriting, time
fields, and the checks on small hand-made trees."""

import datetime as dt
import importlib.util
import json
import struct
import subprocess
import sys
import zlib

import pytest
import yaml

from retail.io import REPO_DIR

RANGES = [(dt.date(2009, 11, 1), dt.date(2012, 1, 31)), (dt.date(2000, 1, 1), dt.date(2000, 1, 1))]
HOST = "t" + "ux"


def s(text: str) -> str:
    """Test string with a real year and clock times, written as <Y> and ~ in this file so that the
    published file itself passes check_public."""
    return text.replace("<Y>", "20" + "26").replace("~", ":")


def load(name):
    sys.path.insert(0, str(REPO_DIR / "scripts"))
    spec = importlib.util.spec_from_file_location(name, REPO_DIR / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def pub():
    return load("publish")


@pytest.fixture(scope="module")
def cp():
    return load("check_public")


# --- check_public ---------------------------------------------------------------------------


def test_dates_outside_the_ranges_fail(cp):
    assert cp.check_text("weeks 2011-06-06 to 2011-11-28, origin 20110606", RANGES) == []
    assert cp.check_text("placeholder 2000-01-01T10:00:00+01:00", RANGES) == []
    assert cp.check_text(s("run on <Y>-11-01"), RANGES) == [s("date <Y>-11-01")]
    assert cp.check_text(s("id <Y>1102-133451-x"), RANGES) == [s("date <Y>1102")]
    assert cp.check_text(s("am 04.11.<Y>"), RANGES) == [s("date 04.11.<Y>")]


def test_numbers_that_are_no_dates_pass(cp):
    assert cp.check_text(s("revenue 13231898, units 20251399, <Y>.11.04x"), RANGES) == []


def test_clock_times_only_inside_allowed_stamps(cp):
    assert cp.check_text("invoice 2010-12-01 08:26:00", RANGES) == []
    assert cp.check_text(s("finished at 14~03~22"), RANGES) == [s("clock time 14~03~22")]
    found = cp.check_text(s("start <Y>-11-01T09~15~00"), RANGES)
    assert s("date <Y>-11-01") in found and s("clock time T09~15") in found


def test_private_traces(cp):
    marker = "ml-workbench" + "-" + "private"
    text = f"see ../{marker} and /" + f"home/someone/x on {HOST}.local"
    found = cp.check_text(text, RANGES, [HOST])
    assert found == ["absolute path /" + "home/", f"host name {HOST}", "marker -" + "private"]
    assert cp.check_text(f"linux {HOST}edo", RANGES, [HOST]) == []


def png(chunks):
    def chunk(kind, data):
        body = kind + data
        return struct.pack(">I", len(data)) + body + struct.pack(">I", zlib.crc32(body))

    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 0, 0, 0, 0)
    idat = zlib.compress(b"\x00\x00")
    return b"\x89PNG\r\n\x1a\n" + b"".join(
        chunk(k, d) for k, d in [(b"IHDR", ihdr), *chunks, (b"IDAT", idat), (b"IEND", b"")]
    )


def test_image_metadata(tmp_path, cp):
    (tmp_path / "ok.png").write_bytes(png([(b"tEXt", b"Software\x00Matplotlib")]))
    (tmp_path / "t.png").write_bytes(png([(b"tIME", b"\x07\xea\x0b\x04\x0c\x00\x00")]))
    (tmp_path / "c.png").write_bytes(png([(b"tEXt", s("Creation Time\x00<Y>-11-04").encode())]))
    gif = b"GIF89a" + b"\x00" * 7 + b"\x21\xfe" + bytes([10]) + s("<Y>-11-04").encode() + b"\x00;"
    (tmp_path / "a.gif").write_bytes(gif)
    (tmp_path / "b.gif").write_bytes(gif.replace(s("<Y>-11-04").encode(), b"gif.ski..."))
    assert cp.check_image(tmp_path / "ok.png", RANGES) == []
    assert cp.check_image(tmp_path / "t.png", RANGES) == ["PNG tIME chunk"]
    assert len(cp.check_image(tmp_path / "c.png", RANGES)) == 1
    assert len(cp.check_image(tmp_path / "a.gif", RANGES)) == 1
    assert cp.check_image(tmp_path / "b.gif", RANGES) == []


def test_pdf_dates(tmp_path, cp, monkeypatch):
    (tmp_path / "x.pdf").write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(cp, "pdf_dates", lambda p: [s("CreationDate:    <Y>-11-01T00~00~00Z")])
    assert [f for f in cp.check_pdf(tmp_path / "x.pdf") if f.startswith("PDF")] == []
    monkeypatch.setattr(cp, "pdf_dates", lambda p: [s("ModDate:    <Y>-11-04T10~12~00+01")])
    assert [f for f in cp.check_pdf(tmp_path / "x.pdf") if f.startswith("PDF")] == [
        s("PDF ModDate <Y>-11-04T10~12~00+01")
    ]


def test_check_tree(tmp_path, cp):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "HEAD").write_text(s("<Y>-11-04 is fine inside .git"))
    (tmp_path / "README.md").write_text("Data 2009-12-01 to 2011-12-09.")
    (tmp_path / ".env").write_text("X=1")
    (tmp_path / "book.xlsx").write_bytes(b"PK\x03\x04rest")
    (tmp_path / "data.bin").write_bytes(b"PK\x03\x04rest")
    (tmp_path / "n.ipynb").write_text("{}")
    (tmp_path / s("log-<Y>1104.txt")).write_text("")
    found = cp.check_tree(tmp_path, RANGES)
    assert sorted(found) == [".env", "book.xlsx", "data.bin", s("log-<Y>1104.txt"), "n.ipynb"]
    assert found["data.bin"] == ["zip-based file"]
    assert found[s("log-<Y>1104.txt")] == [s("date <Y>1104")]


def test_the_publish_tools_pass_their_own_checks(cp):
    for path in ("scripts/check_public.py", "scripts/publish.py", "tests/test_publish.py"):
        assert cp.check_text((REPO_DIR / path).read_text(), RANGES, [HOST]) == [], path


# --- publish ----------------------------------------------------------------------------------


def test_glob(pub):
    assert pub.matches("src/retail/io.py", ["src/**"])
    assert pub.matches("CLAUDE.md", ["**/CLAUDE.md"]) and pub.matches(
        "a/CLAUDE.md", ["**/CLAUDE.md"]
    )
    assert pub.matches("reports/a.md", ["reports/*.md"])
    assert not pub.matches("reports/experiments/a.md", ["reports/*.md"])
    assert not pub.matches("README.md.bak", ["README.md"])


def test_select_files(tmp_path, pub):
    (tmp_path / "demo" / "data").mkdir(parents=True)
    (tmp_path / "demo" / "data" / "meta.js").write_text("x")
    manifest = {"files": ["src/**", "README.md", "CLAUDE.md"], "generated": ["demo/data/**"],
                "exclude": ["**/CLAUDE.md"]}  # fmt: skip
    tracked = ["README.md", "CLAUDE.md", "src/a.py", "src/CLAUDE.md", "notes.md"]
    assert pub.select_files(tmp_path, manifest, tracked) == [
        "README.md", "demo/data/meta.js", "src/a.py"
    ]  # fmt: skip
    with pytest.raises(SystemExit):
        pub.select_files(tmp_path, manifest | {"generated": ["demo/missing/**"]}, tracked)


def test_gitignore_keeps_published_generated_files(pub):
    text = ".env\n# demo\ndemo/data/\ndemo/style.css\nruns/\n"
    out = pub.drop_ignored_generated(text, ["demo/data/**", "demo/style.css"])
    assert out == ".env\n# demo\nruns/\n"


def test_run_ids_get_neutral_ids(tmp_path, pub):
    (tmp_path / s("<Y>1103-105207-sim-L1-focus-test")).mkdir()
    (tmp_path / s("<Y>1103-105207-sim-L1-focus-test") / "config.yaml").write_text(
        yaml.safe_dump({"experiment": "P5"})
    )
    mapping = {}
    text = s("Runs: `<Y>1103-105207-sim-L1-focus-test`, <Y>1102-073939-naive-full and ") + s(
        "<Y>1102-0739-naive-full. Fixture 20000101-120000-mlp, data 20110606-x."
    )
    out = pub.rewrite_run_ids(text, mapping, tmp_path, RANGES)
    assert out == (
        "Runs: `P5-sim-L1-focus-test-r1`, naive-full-r1 and "
        "naive-full-r2. Fixture 20000101-120000-mlp, data 20110606-x."
    )
    # stable: the same id keeps its neutral id, a new run of the same name counts on
    again = pub.rewrite_run_ids(s("<Y>1102-073939-naive-full <Y>1104-000000-naive-full"), mapping,
                                tmp_path, RANGES)  # fmt: skip
    assert again == "naive-full-r1 naive-full-r3"


def test_time_fields_and_logs(pub):
    obj = {"status": "finished", "start_time": "x", "rows": [{"ts": 1, "loss": 0.5}]}
    assert pub.drop_time_fields(obj) == {"status": "finished", "rows": [{"loss": 0.5}]}
    assert pub.month_year(s("[<Y>-11-04 10~12~33] start\n<Y>-11-04T10~12~33+01~00 end")) == (
        s("[November <Y>] start\nNovember <Y> end")
    )


def test_transform(pub):
    ctx = {"mapping": {}, "runs_dir": None, "ranges": RANGES, "generated": []}
    meta = json.dumps({"run": s("<Y>1102-073939-naive-full"), "end_time": "t", "n": 1}).encode()
    assert json.loads(pub.transform("runs/meta.json", meta, ctx)) == {
        "run": "naive-full-r1",
        "n": 1,
    }
    assert pub.transform("a.png", b"\x89PNG\xff\xfe", ctx) == b"\x89PNG\xff\xfe"


def test_publish_end_to_end(tmp_path, pub):
    src, tgt = tmp_path / "src", tmp_path / "public"
    (src / "src").mkdir(parents=True)
    (src / "src" / "a.py").write_text(s("RUN = '<Y>1102-073939-naive-full'\n"))
    (src / "src" / "b.py").write_text(s("EARLIER = '<Y>1101-000000-naive-full'\n"))
    (src / "CLAUDE.md").write_text("private")
    (src / "publish.yaml").write_text(
        yaml.safe_dump(
            {
                "files": ["src/**", "publish.yaml"],
                "exclude": ["**/CLAUDE.md"],
                "check": {"allowed_dates": [["2000-01-01", "2000-01-01"]]},
            }
        )  # fmt: skip
    )
    git = ["git", "-c", "user.name=t", "-c", "user.email=t@t"]
    subprocess.run(["git", "init", "-q"], cwd=src, check=True)
    subprocess.run(["git", "add", "-A"], cwd=src, check=True)
    subprocess.run([*git, "commit", "-qm", "x"], cwd=src, check=True)
    (tgt / ".git").mkdir(parents=True)
    (tgt / "stale.txt").write_text("old")
    files = pub.publish(src, tgt, None)
    assert files == ["publish.yaml", "src/a.py", "src/b.py"]
    assert not (tgt / "stale.txt").exists() and (tgt / ".git").exists()
    assert (tgt / "src" / "a.py").read_text() == "RUN = 'naive-full-r2'\n"
    assert yaml.safe_load((src / "publish-runids.yaml").read_text()) == {
        s("<Y>1101-000000-naive-full"): "naive-full-r1",
        s("<Y>1102-073939-naive-full"): "naive-full-r2",
    }
    (src / "src" / "a.py").write_text("changed")
    with pytest.raises(SystemExit):  # uncommitted changes
        pub.publish(src, tgt, None)
    with pytest.raises(SystemExit):  # target inside the source
        pub.publish(src, src / "out", None, allow_dirty=True)
    (tmp_path / "other").mkdir()
    (tmp_path / "other" / "keep.txt").write_text("x")
    with pytest.raises(SystemExit):  # not a git working tree
        pub.publish(src, tmp_path / "other", None, allow_dirty=True)
