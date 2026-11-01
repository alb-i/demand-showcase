"""Generate the public working tree of a repository from its publish manifest.

    micromamba run -n demand-showcase python scripts/publish.py --target ../public/demand-showcase
    micromamba run -n demand-showcase python scripts/publish.py --source <workbench repo> \
        --target ../public/ml-workbench

1. Copies exactly the files the manifest (<source>/publish.yaml) allows into the target; everything
   in the target except .git is replaced. `files` globs select tracked files (git ls-files),
   `generated` globs select build outputs in the working tree (each must match a file);
   `exclude` globs win over both. Lines of .gitignore that ignore a generated path are dropped.
2. Rewrites run ids (YYYYMMDD-HHMM[SS]-name) in text files to neutral ids
   (<experiment>-<name>-r<n>); the mapping is kept in <source>/publish-runids.yaml (private).
3. Drops time fields (TIME_KEYS) from published JSON, JSONL and Parquet files and reduces
   timestamps in published .log files to month and year.
4. Runs check_public.py on the target and fails if it finds anything.

The source must be clean (tracked files committed) unless --allow-dirty.
"""

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_public  # noqa: E402

RUN_ID = re.compile(r"(?<![\w.-])(\d{8})-(\d{4}|\d{6})-([A-Za-z][\w.+-]*[\w+])")
TIME_KEYS = {"ts", "time", "timestamp", "start_time", "end_time", "generated_at", "created_at",
             "updated_at", "heartbeat", "mtime", "date_run"}  # fmt: skip
LOG_STAMP = re.compile(
    r"\b(\d{4})-(\d{2})-\d{2}(?:[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?)?"
)
MAP_FILE = "publish-runids.yaml"


def glob_regex(pattern: str) -> re.Pattern:
    """Glob with ** (any depth), * and ? (within one path segment) -> compiled regex."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile(out + r"\Z")


def matches(path: str, patterns) -> bool:
    return any(glob_regex(p).match(path) for p in patterns)


def git(source: Path, *args) -> str:
    return subprocess.run(
        ["git", *args], cwd=source, capture_output=True, text=True, check=True
    ).stdout


def working_tree(source: Path) -> list[str]:
    """Relative paths of all files of the working tree except .git."""
    return [str(p.relative_to(source)) for p in source.rglob("*")
            if p.is_file() and ".git" not in p.relative_to(source).parts]  # fmt: skip


def select_files(source: Path, manifest: dict, tracked: list[str]) -> list[str]:
    """Published files (relative paths): tracked files matching `files` plus working-tree files
    matching `generated`, minus `exclude`. A generated glob that matches nothing is an error."""
    exclude = manifest.get("exclude", [])
    out = {f for f in tracked if matches(f, manifest.get("files", []))}
    for g in manifest.get("generated", []):
        found = [f for f in working_tree(source) if matches(f, [g])]
        if not found:
            raise SystemExit(f"generated file(s) missing: {g} (build them first)")
        out.update(found)
    return sorted(f for f in out if not matches(f, exclude))


def drop_ignored_generated(gitignore: str, generated) -> str:
    """.gitignore without the lines that would ignore a published generated path."""
    stems = {g.removesuffix("/**").removesuffix("/*").rstrip("/") for g in generated}
    keep = [line for line in gitignore.splitlines() if line.strip().rstrip("/") not in stems]
    return "\n".join(keep) + "\n"


def neutral_id(run_id: str, mapping: dict, runs_dir: Path | None) -> str:
    """Neutral id of a run (added to mapping): <experiment>-<name>-r<n>, n counting the runs of
    the same experiment and name in the order they are first seen."""
    if run_id in mapping:
        return mapping[run_id]
    name = RUN_ID.match(run_id).group(3)
    exp = None
    cfg = runs_dir / run_id / "config.yaml" if runs_dir else None
    if cfg is not None and cfg.exists():
        exp = (yaml.safe_load(cfg.read_text()) or {}).get("experiment")
    stem = f"{exp}-{name}" if exp else name
    n = 1 + sum(1 for v in mapping.values() if v.rsplit("-r", 1)[0] == stem)
    mapping[run_id] = f"{stem}-r{n}"
    return mapping[run_id]


def rewrite_run_ids(text: str, mapping: dict, runs_dir: Path | None, ranges) -> str:
    """Replace every run id whose date is not an allowed (content or placeholder) date."""

    def sub(m: re.Match) -> str:
        d = m.group(1)
        date = check_public.as_date(d[:4], d[4:6], d[6:])
        if date is None or check_public.allowed(date, ranges):
            return m.group(0)
        return neutral_id(m.group(0), mapping, runs_dir)

    return RUN_ID.sub(sub, text)


def collect_run_ids(source: Path, files, ranges) -> set[str]:
    """Run ids (with a date that is not allowed) in the published text files."""
    ids = set()
    for rel in files:
        try:
            text = (source / rel).read_text()
        except UnicodeDecodeError:
            continue
        for m in RUN_ID.finditer(text):
            d = m.group(1)
            date = check_public.as_date(d[:4], d[4:6], d[6:])
            if date is not None and not check_public.allowed(date, ranges):
                ids.add(m.group(0))
    return ids


def drop_time_fields(obj):
    """JSON-like object without TIME_KEYS (recursively)."""
    if isinstance(obj, dict):
        return {k: drop_time_fields(v) for k, v in obj.items() if k not in TIME_KEYS}
    if isinstance(obj, list):
        return [drop_time_fields(v) for v in obj]
    return obj


def month_year(text: str) -> str:
    """Timestamps in a log reduced to month and year (e.g. 'November 2026')."""
    return LOG_STAMP.sub(
        lambda m: dt.date(int(m.group(1)), int(m.group(2)), 1).strftime("%B %Y"), text
    )


def transform(rel: str, data: bytes, ctx: dict) -> bytes:
    """Published bytes of one file."""
    suffix = Path(rel).suffix.lower()
    if suffix == ".parquet":
        import io

        import pandas as pd

        df = pd.read_parquet(io.BytesIO(data))
        buf = io.BytesIO()
        df.drop(columns=[c for c in df.columns if c in TIME_KEYS]).to_parquet(buf, index=False)
        return buf.getvalue()
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    if rel == ".gitignore":
        text = drop_ignored_generated(text, ctx["generated"])
    if suffix == ".json":
        text = json.dumps(drop_time_fields(json.loads(text)), indent=1, ensure_ascii=False) + "\n"
    elif suffix == ".jsonl":
        text = "".join(json.dumps(drop_time_fields(json.loads(line))) + "\n"
                       for line in text.splitlines() if line.strip())  # fmt: skip
    elif suffix == ".log":
        text = month_year(text)
    text = rewrite_run_ids(text, ctx["mapping"], ctx["runs_dir"], ctx["ranges"])
    return text.encode("utf-8")


def ignored_files(target: Path, files) -> list[str]:
    """Published files that git would not add in the target (ignored by its .gitignore)."""
    if not (target / ".git").exists():
        return []
    out = subprocess.run(["git", "check-ignore", "--no-index", "--stdin"], cwd=target, text=True,
                         input="\n".join(files), capture_output=True)  # fmt: skip
    return out.stdout.split()


def clear_target(target: Path, source: Path) -> None:
    """Delete everything in target except .git; refuses a target that is not a git working tree
    (or empty), or that lies inside the source."""
    target = target.resolve()
    if target == source or source in target.parents:
        raise SystemExit("target must not be inside the source repository")
    if target.exists() and any(target.iterdir()) and not (target / ".git").exists():
        raise SystemExit(f"{target} is neither empty nor a git working tree")
    target.mkdir(parents=True, exist_ok=True)
    for p in target.iterdir():
        if p.name != ".git":
            shutil.rmtree(p) if p.is_dir() and not p.is_symlink() else p.unlink()


def publish(source: Path, target: Path, runs_dir: Path | None, allow_dirty=False) -> list[str]:
    source = source.resolve()
    manifest = yaml.safe_load((source / "publish.yaml").read_text())
    if not allow_dirty and git(source, "status", "--porcelain", "-uno").strip():
        raise SystemExit(f"{source} has uncommitted changes (commit them or --allow-dirty)")
    files = select_files(source, manifest, git(source, "ls-files").splitlines())
    map_path = source / MAP_FILE
    mapping = (yaml.safe_load(map_path.read_text()) or {}) if map_path.exists() else {}
    ranges = check_public.parse_ranges(manifest.get("check", {}).get("allowed_dates"))
    ctx = {"mapping": mapping, "runs_dir": runs_dir, "ranges": ranges,
           "generated": manifest.get("generated", [])}  # fmt: skip
    for run_id in sorted(collect_run_ids(source, files, ranges)):  # numbers in time order
        neutral_id(run_id, mapping, runs_dir)
    clear_target(target, source)
    for rel in files:
        out = target / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(transform(rel, (source / rel).read_bytes(), ctx))
        shutil.copymode(source / rel, out)
    ignored = ignored_files(target, files)
    if ignored:
        raise SystemExit(f"published files ignored by the target's .gitignore: {ignored[:5]}")
    if mapping:
        map_path.write_text("# run id -> public id (scripts/publish.py); private, not published\n"
                            + yaml.safe_dump(mapping, sort_keys=True))  # fmt: skip
    return files


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--target", type=Path, required=True)
    p.add_argument(
        "--runs-dir", type=Path, default=None, help="default: $RUNS_DIR of the source's .env"
    )
    p.add_argument("--allow-dirty", action="store_true")
    a = p.parse_args(argv)
    runs_dir = a.runs_dir
    if runs_dir is None:
        from dotenv import dotenv_values

        env = dotenv_values(a.source / ".env")
        runs_dir = Path(env["RUNS_DIR"]) if env.get("RUNS_DIR") else None
    files = publish(a.source, a.target, runs_dir, a.allow_dirty)
    print(f"published {len(files)} files to {a.target}")
    return check_public.main([str(a.target), "--manifest", str(a.source / "publish.yaml")])


if __name__ == "__main__":
    sys.exit(main())
