"""Writes meta.json, config.yaml, heartbeat and metrics.jsonl into a run folder (same format as
Showcase 01, so the workbench can read it).

    with RunLogger(config, name="trivial") as run:
        run.log(origin="2011-01-03", model="trivial", segment="A-smooth", h=2, mase=0.84)
        run.write_parquet("forecasts", df)

Run folder $RUNS_DIR/<run-id>/. meta.json gets "status" running -> finished, or crashed if the
block exits with an exception; a killed process just stops touching the heartbeat.
"""

import json
import os
import socket
import threading
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv

from retail.cleaning import git_commit
from retail.io import REPO_DIR

HEARTBEAT_SECONDS = 10


def runs_dir() -> Path:
    load_dotenv(REPO_DIR / ".env")
    return Path(os.environ["RUNS_DIR"])


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class RunLogger:
    def __init__(
        self,
        config: dict,
        name: str,
        data_version: str,
        root: Path | None = None,
        heartbeat_seconds: float = HEARTBEAT_SECONDS,
    ):
        self.run_id = f"{datetime.now():%Y%m%d-%H%M%S}-{name}"
        self.dir = (root or runs_dir()) / self.run_id
        self.dir.mkdir(parents=True)
        self.meta = {
            "run_id": self.run_id,
            "git_commit": git_commit(REPO_DIR),
            "dataset_version": data_version,
            "start_time": now_iso(),
            "host": socket.gethostname(),
            "status": "running",
        }
        self._write_meta()
        (self.dir / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
        self._metrics = open(self.dir / "metrics.jsonl", "a")
        self._stop = threading.Event()
        self._heartbeat_seconds = heartbeat_seconds
        self._touch()
        self._thread = threading.Thread(target=self._beat, daemon=True)
        self._thread.start()

    def _write_meta(self) -> None:
        tmp = self.dir / "meta.json.tmp"
        tmp.write_text(json.dumps(self.meta, indent=2) + "\n")
        tmp.replace(self.dir / "meta.json")

    def _touch(self) -> None:
        (self.dir / "heartbeat").write_text(now_iso() + "\n")

    def _beat(self) -> None:
        while not self._stop.wait(self._heartbeat_seconds):
            self._touch()

    def log(self, **fields) -> None:
        """Append one JSON line (NaN written as null)."""
        record = {
            k: (None if isinstance(v, float) and v != v else v) for k, v in fields.items()
        } | {"ts": round(time.time(), 3)}
        self._metrics.write(json.dumps(record) + "\n")
        self._metrics.flush()

    def write_parquet(self, name: str, df: pd.DataFrame) -> Path:
        path = self.dir / f"{name}.parquet"
        df.to_parquet(path, index=False)
        return path

    def close(self, status: str = "finished") -> None:
        self._stop.set()
        self._thread.join()
        self._metrics.close()
        self._touch()
        self.meta.update(status=status, end_time=now_iso())
        self._write_meta()

    def __enter__(self) -> "RunLogger":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close("finished" if exc_type is None else "crashed")
