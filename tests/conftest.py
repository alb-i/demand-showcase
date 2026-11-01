from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from retail.cleaning import load_config

CONFIG = Path(__file__).resolve().parents[1] / "configs" / "cleaning.yaml"


def lines(*rows, sheet="Year 2010-2011") -> pd.DataFrame:
    """Raw lines from tuples (invoice, stock_code, quantity, date, price, customer[, description])
    with the dtypes of retail.io."""
    recs = []
    for r in rows:
        inv, code, q, date, price, cust, *desc = r
        recs.append(
            {
                "invoice": inv,
                "stock_code": code,
                "description": desc[0] if desc else f"ITEM {code}",
                "quantity": q,
                "invoice_date": pd.Timestamp(date),
                "price": price,
                "customer_id": cust,
                "country": "United Kingdom",
                "sheet": sheet,
            }
        )
    df = pd.DataFrame(recs)
    return df.astype(
        {
            "invoice": "string",
            "stock_code": "string",
            "description": "string",
            "quantity": "int64",
            "invoice_date": "datetime64[s]",
            "price": "float64",
            "customer_id": "Int64",
            "country": "string",
            "sheet": "string",
        }
    ).assign(line=range(len(df)))


@pytest.fixture
def cfg():
    return load_config(CONFIG)


W0 = pd.Timestamp("2011-01-03")


def panel(series: dict, closed=()) -> pd.DataFrame:
    """Panel rows from {code: [weekly units ...]} starting at W0 (price 1 per unit)."""
    rows = []
    for code, units in series.items():
        for i, u in enumerate(units):
            week = W0 + pd.Timedelta(weeks=i)
            shut = i in closed
            rows.append(
                {
                    "stock_code": code,
                    "week": week,
                    "units": np.nan if shut else float(u),
                    "revenue": np.nan if shut else float(u),
                    "closed": shut,
                }
            )
    return pd.DataFrame(rows)
