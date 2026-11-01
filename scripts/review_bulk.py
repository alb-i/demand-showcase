"""Review app for reports/bulk_review.csv (keep / exclude per line), for the iPad on the LAN.

    micromamba run -n demand-showcase python scripts/review_bulk.py [--port 8765]

Listens on all interfaces but answers only 127.0.0.1 and the networks in --allow (default
192.168.0.0/24); everyone else gets 403. Then open http://<this machine>:8765/ on the iPad.
Decisions are written straight into the CSV (column `decision`).
"""

import argparse

import uvicorn

from retail.io import REPO_DIR
from retail.review import create_app


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--csv", default=REPO_DIR / "reports" / "bulk_review.csv")
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--allow", nargs="+", default=["192.168.0.0/24"])
    a = p.parse_args()
    app = create_app(a.csv, ["127.0.0.1/32", *a.allow])
    uvicorn.run(app, host=a.host, port=a.port)


if __name__ == "__main__":
    main()
