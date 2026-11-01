"""Many backtest runs in one worker pool, so the CPU stays busy (E9).

    micromamba run -n demand-showcase python scripts/run_batch.py BATCH.yaml \
        [--origins tuning|test --final] [--jobs 6] [--dry-run]

BATCH.yaml: `runs:` a list of {config: configs/models/<m>.yaml, set: focus|full, target: total
|item (default total)}. Every run is prepared as by scripts/backtest.py (same model, data,
names; test runs get the suffix -test) and all (run, origin) tasks go to one pool of --jobs
worker processes, the most expensive first (the duration of the run's newest finished tuning
run per origin, later origins weighted up as they have more history), so no core waits for the
end of a run. A run's folder is created when its first origin is done; its origins are logged
in origin order; results equal those of scripts/backtest.py.
A run whose name already has a finished run with the same origins in $RUNS_DIR is skipped (the
test origins are used once; after a crash the batch can simply be started again). A run that
fails is marked crashed, the others go on; the exit code is 1 if any failed.
--dry-run: list the runs, the skipped ones and the cost estimate, run nothing.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml
from backtest import prepare  # scripts/backtest.py (sys.path[0] is scripts/)

from retail.backtest import default_jobs
from retail.io import REPO_DIR
from retail.runlog import RunLogger, runs_dir
from retail.runner import finish, log_origin, schedule

DEFAULT_SECONDS = 30.0  # per origin, for runs without a finished tuning run


def finished_runs(root: Path) -> dict[tuple[str, str], float]:
    """(run name, origins) -> duration in seconds of the newest finished run of that name."""
    out = {}
    for d in sorted(root.iterdir()):
        m = re.fullmatch(r"\d{8}-\d{6}-(.+)", d.name)
        if not m or not (d / "meta.json").exists() or not (d / "config.yaml").exists():
            continue
        meta = json.loads((d / "meta.json").read_text())
        if meta.get("status") != "finished" or "end_time" not in meta:
            continue
        cfg = yaml.safe_load((d / "config.yaml").read_text()) or {}
        if "calibration" in cfg or "horizon_sums" in cfg or "derived_from" in cfg:
            continue
        seconds = (datetime.fromisoformat(meta["end_time"])
                   - datetime.fromisoformat(meta["start_time"])).total_seconds()  # fmt: skip
        out[(m.group(1), cfg.get("origins", "tuning"))] = seconds
    return out


def per_origin_cost(tuning_seconds: float | None, n_origins: int, jobs: int = 6) -> float:
    """CPU seconds per origin from a tuning run's wall time (it used up to `jobs` workers)."""
    if tuning_seconds is None:
        return DEFAULT_SECONDS
    return tuning_seconds * min(jobs, n_origins) / n_origins


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("batch")
    p.add_argument("--origins", choices=["tuning", "test"], default="tuning")
    p.add_argument("--final", action="store_true", help="required for the test origins")
    p.add_argument("--jobs", type=int, default=default_jobs())
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    if a.origins == "test" and not a.final:
        p.error("test origins are used once, at the end: add --final")

    spec = yaml.safe_load(Path(a.batch).read_text())
    root = runs_dir()
    done = finished_runs(root)
    cache: dict = {}
    preps, base_cost = {}, {}
    for r in spec["runs"]:
        prep = prepare(REPO_DIR / r["config"], r["set"], a.origins, r.get("target", "total"),
                       r.get("level", "product"), cache)  # fmt: skip
        if (prep.name, a.origins) in done:
            print(f"skip {prep.name}: finished run exists")
            continue
        if prep.name in preps:
            raise SystemExit(f"run {prep.name} twice in {a.batch}")
        tuning_name = prep.name.removesuffix("-test")
        tuning = done.get((tuning_name, "tuning"))
        n_tuning = len(prep.origins) if a.origins == "tuning" else 22
        preps[prep.name] = prep
        base_cost[prep.name] = per_origin_cost(tuning, n_tuning)
    first = min((o for pr in preps.values() for o in pr.origins), default=None)

    def cost(key, origin):  # later origins have more history: up to +50 % at the last
        span = max((pr.origins[-1] - first).days for pr in preps.values()) or 1
        return base_cost[key] * (1 + 0.5 * (origin - first).days / span)

    total = sum(cost(k, o) for k, pr in preps.items() for o in pr.origins)
    print(
        f"{len(preps)} runs, {sum(len(pr.origins) for pr in preps.values())} tasks, "
        f"~{total / 3600:.1f} CPU h, ~{total / 3600 / a.jobs:.1f} h with {a.jobs} workers "
        "(estimate from the tuning runs)"
    )
    for k in sorted(preps, key=lambda k: -base_cost[k]):
        print(f"  {k}: ~{base_cost[k]:.0f} s per origin")
    if a.dry_run or not preps:
        return

    loggers, fcs, rows, failed = {}, {k: [] for k in preps}, {k: [] for k in preps}, []
    left = {k: len(pr.origins) for k, pr in preps.items()}
    try:
        for key, origin, fc, r, seconds, recs in schedule(preps, cost, a.jobs):
            prep = preps[key]
            if key not in loggers:
                loggers[key] = RunLogger(prep.config, name=prep.name,
                                         data_version=prep.data_version)  # fmt: skip
                print(f"{key}: {loggers[key].dir}", flush=True)
            run = loggers[key]
            if fc is None:
                print(f"{key}: FAILED at {origin.date()}\n{seconds}", flush=True)
                run.close("crashed")
                failed.append(key)
                continue
            log_origin(run, prep, origin, recs)
            fcs[key].append(fc)
            rows[key].append(r)
            left[key] -= 1
            print(f"{key} {origin.date()}: {len(r)} rows, {seconds:.1f} s, {left[key]} left",
                  flush=True)  # fmt: skip
            if left[key] == 0:
                finish(run, prep, fcs[key], rows[key])
                run.close("finished")
                fcs[key], rows[key] = [], []
                print(f"{key}: finished", flush=True)
    finally:
        for key, run in loggers.items():
            if left[key] > 0 and key not in failed:
                run.close("crashed")
    if failed:
        print(f"failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
