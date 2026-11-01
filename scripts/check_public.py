"""Check a public working tree before it is committed: no timestamps, no private traces.

    micromamba run -n demand-showcase python scripts/check_public.py <tree> [--manifest M]

Fails (exit 1, one line per finding) on
- day-level dates (YYYY-MM-DD, YYYYMMDD, DD.MM.YYYY) outside the allowed ranges of the
  manifest (check.allowed_dates: the data period and the placeholder date of test fixtures);
- clock times (HH:MM:SS, or THH:MM of an ISO timestamp) that are not part of an allowed date;
- PDF creation / modification dates other than the 1st of a month;
- dates in image and video metadata (PNG tIME and text chunks, JPEG EXIF, GIF comments,
  container tags of videos);
- zip-based files (zip, xlsx, docx, pptx, odt, ods, jar, ...) and notebooks;
- absolute home paths, this machine's host name (and check.hosts), a file named .env, and the
  marker of the private repositories.
"""

import argparse
import datetime as dt
import json
import re
import socket
import struct
import subprocess
import sys
from pathlib import Path

import yaml

PRIVATE = "-" + "private"  # split so that this file passes its own check
ABS_PATHS = re.compile(
    "|".join(["/" + "home/", "/" + "Users/", "/" + "root/", r"[A-Z]:\\" + "Users"])
)
ZIP_EXT = {".zip", ".xlsx", ".xlsm", ".docx", ".pptx", ".odt", ".ods", ".odp", ".jar", ".whl",
           ".epub", ".7z", ".gz", ".tgz", ".bz2", ".xz", ".rar"}  # fmt: skip
NOTEBOOK_EXT = {".ipynb"}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"}
TEXT_LIMIT = 50_000_000
MIDNIGHT = ":".join(["00"] * 3)  # built, so that this file passes its own check

DATE_ISO = re.compile(r"(?<![\d.])(\d{4})-(\d{2})-(\d{2})(?!\d)")
DATE_COMPACT = re.compile(r"(?<!\d)(?<!\d\.)(\d{4})(\d{2})(\d{2})(?!\d)(?!\.\d)")
DATE_DOTTED = re.compile(r"(?<!\d)(?<!\d\.)(\d{2})\.(\d{2})\.(\d{4})(?!\d)(?!\.\d)")
CLOCK = re.compile(r"(?<![\d:])([01]\d|2[0-3]):([0-5]\d):([0-5]\d)(?![\d:])")
ISO_TIME = re.compile(r"(?<=\d)T([01]\d|2[0-3]):([0-5]\d)")
# a date immediately followed by a time: the time belongs to that date
STAMP = re.compile(r"(\d{4}-\d{2}-\d{2}|\d{8})[T _-]?(?:[01]\d|2[0-3]):?[0-5]\d(?::?[0-5]\d)?")


def parse_ranges(ranges) -> list[tuple[dt.date, dt.date]]:
    """[[from, to], ...] (dates or ISO strings) -> list of date pairs."""
    out = []
    for lo, hi in ranges or []:
        lo = lo if isinstance(lo, dt.date) else dt.date.fromisoformat(str(lo))
        hi = hi if isinstance(hi, dt.date) else dt.date.fromisoformat(str(hi))
        out.append((lo, hi))
    return out


def as_date(y: str, m: str, d: str) -> dt.date | None:
    """A valid calendar date between 1900 and 2099, else None (most 8-digit numbers are not)."""
    try:
        date = dt.date(int(y), int(m), int(d))
    except ValueError:
        return None
    return date if 1900 <= date.year <= 2099 else None


def allowed(date: dt.date, ranges) -> bool:
    return any(lo <= date <= hi for lo, hi in ranges)


def find_dates(text: str) -> list[tuple[int, str, dt.date]]:
    """(position, matched text, date) of every day-level date in the text."""
    out = []
    for rx, order in ((DATE_ISO, (1, 2, 3)), (DATE_COMPACT, (1, 2, 3)), (DATE_DOTTED, (3, 2, 1))):
        for m in rx.finditer(text):
            date = as_date(*(m.group(i) for i in order))
            if date is not None:
                out.append((m.start(), m.group(0), date))
    return out


def check_text(text: str, ranges, hosts=()) -> list[str]:
    """Findings in one text: dates outside the ranges, clock times outside allowed stamps,
    home paths, host names and the private marker."""
    found = []
    for _, s, date in find_dates(text):
        if not allowed(date, ranges):
            found.append(f"date {s}")
    covered = []  # spans of timestamps whose date is allowed
    for m in STAMP.finditer(text):
        dates = find_dates(m.group(1))
        if dates and allowed(dates[0][2], ranges):
            covered.append((m.start(), m.end()))
    for rx in (CLOCK, ISO_TIME):
        for m in rx.finditer(text):
            if not any(a <= m.start() < b for a, b in covered):
                found.append(f"clock time {m.group(0)}")
    if PRIVATE in text:
        found.append(f"marker {PRIVATE}")
    for m in ABS_PATHS.finditer(text):
        found.append(f"absolute path {m.group(0)}")
    for h in hosts:
        if re.search(rf"(?<![\w-]){re.escape(h)}(?![\w-])", text, re.I):
            found.append(f"host name {h}")
    return sorted(set(found))


def png_chunks(data: bytes):
    """(type, payload) of the chunks of a PNG file."""
    pos = 8
    while pos + 8 <= len(data):
        n, kind = struct.unpack(">I4s", data[pos : pos + 8])
        yield kind.decode("latin-1"), data[pos + 8 : pos + 8 + n]
        pos += 12 + n


def gif_comments(data: bytes) -> list[str]:
    """Comment extensions (0x21 0xFE) of a GIF file."""
    out, pos = [], 0
    while (pos := data.find(b"\x21\xfe", pos)) != -1:
        pos += 2
        text = b""
        while pos < len(data) and data[pos] != 0:
            n = data[pos]
            text += data[pos + 1 : pos + 1 + n]
            pos += 1 + n
        out.append(text.decode("latin-1"))
    return out


def check_image(path: Path, ranges) -> list[str]:
    """Dates in image metadata."""
    data = path.read_bytes()
    found = []
    if data.startswith(b"\x89PNG"):
        for kind, payload in png_chunks(data):
            if kind == "tIME":
                found.append("PNG tIME chunk")
            elif kind in ("tEXt", "iTXt", "zTXt", "eXIf"):
                text = payload.decode("latin-1")
                if find_dates(text) or "date" in text.lower() or "time" in text.lower():
                    found.append(f"PNG {kind} chunk with a date: {text[:60]!r}")
    elif data.startswith(b"GIF8"):
        for c in gif_comments(data):
            if find_dates(c) or CLOCK.search(c):
                found.append(f"GIF comment with a date: {c[:60]!r}")
    elif data.startswith(b"\xff\xd8"):
        from PIL import Image

        exif = Image.open(path).getexif()
        if any(k in exif for k in (306, 36867, 36868)):  # DateTime, DateTimeOriginal, ...Digitized
            found.append("JPEG EXIF date")
    return found


def pdf_dates(path: Path) -> list[str]:
    """CreationDate / ModDate lines of pdfinfo."""
    out = subprocess.run(["pdfinfo", "-isodates", str(path)], capture_output=True, text=True)
    return [
        line for line in out.stdout.splitlines() if line.startswith(("CreationDate", "ModDate"))
    ]


def check_pdf(path: Path, hosts=()) -> list[str]:
    """PDF dates other than the 1st of a month at 00:00; private traces in the text."""
    found = []
    for line in pdf_dates(path):
        value = line.split(":", 1)[1].strip()
        if not re.match(r"\d{4}-\d{2}-01T" + MIDNIGHT, value):
            found.append(f"PDF {line.split(':')[0]} {value}")
    text = subprocess.run(["pdftotext", str(path), "-"], capture_output=True, text=True).stdout
    found += [f for f in check_text(text, [(dt.date.min, dt.date.max)], hosts)]
    return found


def check_video(path: Path) -> list[str]:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format_tags:stream_tags",
                          "-of", "json", str(path)], capture_output=True, text=True)  # fmt: skip
    tags = json.dumps(json.loads(out.stdout or "{}"))
    return ["video metadata with a date"] if "creation_time" in tags or find_dates(tags) else []


def is_zip(path: Path) -> bool:
    if path.suffix.lower() in ZIP_EXT:
        return True
    with path.open("rb") as f:
        return f.read(4) == b"PK\x03\x04"


def check_tree(root: Path, ranges, hosts=()) -> dict[str, list[str]]:
    """Findings per file (relative path) of every file below root except .git."""
    findings = {}
    for path in sorted(
        p for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts
    ):
        rel = str(path.relative_to(root))
        found = []
        if path.name == ".env":
            found.append("file .env")
        if path.suffix.lower() in NOTEBOOK_EXT:
            found.append("notebook")
        if is_zip(path):
            found.append("zip-based file")
        elif path.suffix.lower() == ".pdf":
            found += check_pdf(path, hosts)
        elif path.suffix.lower() in VIDEO_EXT:
            found += check_video(path)
        elif path.suffix.lower() in {".png", ".gif", ".jpg", ".jpeg"}:
            found += check_image(path, ranges)
        else:
            data = path.read_bytes()[:TEXT_LIMIT]
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                found.append("unknown binary file")
            else:
                found += check_text(text, ranges, hosts)
        found += check_text(rel, ranges, hosts)  # the file name itself
        if found:
            findings[rel] = sorted(set(found))
    return findings


def load_check_config(manifest: Path) -> tuple[list, list[str]]:
    cfg = (yaml.safe_load(manifest.read_text()) or {}).get("check", {})
    hosts = [socket.gethostname().split(".")[0], *cfg.get("hosts", [])]
    return parse_ranges(cfg.get("allowed_dates")), [h for h in hosts if h]


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("tree", type=Path)
    p.add_argument(
        "--manifest", type=Path, default=Path(__file__).resolve().parents[1] / "publish.yaml"
    )
    a = p.parse_args(argv)
    ranges, hosts = load_check_config(a.manifest)
    findings = check_tree(a.tree, ranges, hosts)
    for rel, found in findings.items():
        for f in found:
            print(f"{rel}: {f}")
    print(
        f"check_public: {len(findings)} files with findings" if findings else "check_public: clean"
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
