"""Bulk review app (reports/bulk_review.csv): keep / exclude each candidate line by hand.

The CSV stays the single source of the decisions; the app only rewrites its `decision` column
(format "keep", "exclude" or "<decision>; <note>"). Requests from addresses outside `allow`
are refused (403), so the app can listen on the LAN without being open to everyone else.
"""

import ipaddress
import os
import tempfile
from pathlib import Path

import pandas as pd
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse

KEY = ["invoice", "stock_code"]
DECISIONS = {"", "keep", "exclude"}
PAGE = Path(__file__).with_name("review_page.html")


def read_review(path: Path) -> pd.DataFrame:
    """All columns as strings, empty cells as "" (nothing is reformatted on the way back)."""
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def write_review(df: pd.DataFrame, path: Path) -> None:
    """Atomic: a crash while writing never leaves a half-written CSV."""
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    with os.fdopen(fd, "w", newline="") as f:
        df.to_csv(f, index=False)
    os.replace(tmp, path)


def split_decision(cell: str) -> tuple[str, str]:
    """ "exclude; wholesale lot" -> ("exclude", "wholesale lot")."""
    decision, _, note = cell.partition(";")
    return decision.strip(), note.strip()


def join_decision(decision: str, note: str) -> str:
    note = " ".join(note.replace(";", ",").split())
    return f"{decision}; {note}" if decision and note else decision


def merge_decisions(new: pd.DataFrame, old: pd.DataFrame) -> pd.DataFrame:
    """Decisions of an earlier review copied to the same (invoice, stock_code) lines of a new
    one (build_panel would otherwise overwrite the review); lines no longer listed are lost."""
    old = old.astype({k: str for k in KEY}).set_index(KEY)["decision"]
    keys = pd.MultiIndex.from_frame(new[KEY].astype(str))
    return new.assign(decision=old.reindex(keys).fillna("").to_numpy())


def allowed(host: str | None, networks: list) -> bool:
    if host is None:
        return False
    try:
        addr = ipaddress.ip_address(host)
    except ValueError:
        return False
    return any(addr in n for n in networks)


def create_app(path: Path, allow: list[str]) -> FastAPI:
    path = Path(path)
    networks = [ipaddress.ip_network(a, strict=False) for a in allow]
    app = FastAPI(title="Bulk review", docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def only_allowed(request: Request, call_next):
        if not allowed(request.client.host if request.client else None, networks):
            return JSONResponse({"detail": "forbidden"}, status_code=403)
        return await call_next(request)

    @app.get("/", response_class=HTMLResponse)
    def page() -> str:
        return PAGE.read_text()

    @app.get("/api/rows")
    def rows() -> list[dict]:
        df = read_review(path)
        out = []
        for i, r in enumerate(df.to_dict("records")):
            decision, note = split_decision(r["decision"])
            out.append(r | {"row": i + 1, "decision": decision, "note": note})
        return out

    @app.put("/api/rows/{invoice}/{stock_code}")
    def decide(invoice: str, stock_code: str, body: dict = Body(...)) -> dict:  # noqa: B008
        decision = str(body.get("decision", ""))
        if decision not in DECISIONS:
            raise HTTPException(422, f"decision must be keep, exclude or empty, not {decision!r}")
        df = read_review(path)
        hit = (df["invoice"] == invoice) & (df["stock_code"] == stock_code)
        if not hit.any():
            raise HTTPException(404, f"no line {invoice} / {stock_code}")
        df.loc[hit, "decision"] = join_decision(decision, str(body.get("note", "")))
        write_review(df, path)
        return {"invoice": invoice, "stock_code": stock_code, "decision": decision}

    return app
