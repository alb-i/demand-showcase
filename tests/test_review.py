import ipaddress

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from retail.review import (
    allowed,
    create_app,
    join_decision,
    merge_decisions,
    read_review,
    split_decision,
    write_review,
)


@pytest.fixture
def csv(tmp_path):
    path = tmp_path / "bulk_review.csv"
    pd.DataFrame(
        {
            "invoice": ["495194", "501534"],
            "stock_code": ["20991", "85123A"],
            "quantity": ["6768", "5364"],
            "first_cancel_days": ["", "3"],
            "decision": ["", ""],
        }
    ).to_csv(path, index=False)
    return path


def client(csv, host="127.0.0.1"):
    return TestClient(create_app(csv, ["127.0.0.1/32", "192.168.0.0/24"]), client=(host, 5000))


def test_decision_format():
    assert split_decision("exclude; wholesale lot") == ("exclude", "wholesale lot")
    assert split_decision("keep") == ("keep", "")
    assert join_decision("exclude", " a;b ") == "exclude; a,b"
    assert join_decision("", "note without decision") == ""


def test_allowed_networks():
    nets = [ipaddress.ip_network("192.168.0.0/24"), ipaddress.ip_network("127.0.0.1/32")]
    assert allowed("192.168.0.23", nets)
    assert allowed("127.0.0.1", nets)
    assert not allowed("192.168.1.23", nets)
    assert not allowed("10.0.0.5", nets)
    assert not allowed("testclient", nets)
    assert not allowed(None, nets)


def test_other_networks_get_403(csv):
    assert client(csv, "192.168.0.23").get("/api/rows").status_code == 200
    assert client(csv, "192.168.1.23").get("/api/rows").status_code == 403
    assert client(csv, "8.8.8.8").get("/").status_code == 403


def test_put_writes_only_the_decision(csv):
    before = read_review(csv)
    c = client(csv)
    r = c.put("/api/rows/501534/85123A", json={"decision": "exclude", "note": "lot"})
    assert r.status_code == 200
    after = read_review(csv)
    assert after.loc[1, "decision"] == "exclude; lot"
    assert after.drop(columns="decision").equals(before.drop(columns="decision"))
    rows = c.get("/api/rows").json()
    assert rows[1]["decision"] == "exclude" and rows[1]["note"] == "lot"
    assert rows[0]["decision"] == "" and rows[0]["row"] == 1
    assert c.put("/api/rows/501534/85123A", json={"decision": ""}).status_code == 200
    assert read_review(csv).loc[1, "decision"] == ""


def test_put_rejects_bad_input(csv):
    c = client(csv)
    assert c.put("/api/rows/501534/85123A", json={"decision": "maybe"}).status_code == 422
    assert c.put("/api/rows/999999/85123A", json={"decision": "keep"}).status_code == 404


def test_page_is_served(csv):
    r = client(csv).get("/")
    assert r.status_code == 200 and "Bulk review" in r.text


def test_merge_decisions_keeps_old_review():
    old = pd.DataFrame(
        {"invoice": ["1", "2"], "stock_code": ["A", "B"], "decision": ["keep", "exclude; x"]}
    )
    new = pd.DataFrame({"invoice": ["2", "3"], "stock_code": ["B", "C"], "decision": ["", ""]})
    assert merge_decisions(new, old)["decision"].tolist() == ["exclude; x", ""]


def test_write_review_round_trip(tmp_path):
    df = pd.DataFrame({"invoice": ["C0012"], "stock_code": ["00123"], "decision": [""]})
    write_review(df, tmp_path / "r.csv")
    assert read_review(tmp_path / "r.csv").equals(df)
    assert [p.name for p in tmp_path.iterdir()] == ["r.csv"]
