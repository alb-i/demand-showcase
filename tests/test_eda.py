import numpy as np
import pandas as pd
import pytest
from conftest import W0, panel

from retail.eda import (
    life_cycle,
    new_product_share,
    season_profile,
    weekday_shares,
    weekly_totals,
)


def test_weekly_totals_closed_weeks_missing():
    t = weekly_totals(panel({"A": [1, 2, 0], "B": [0, 3, 4]}, closed=[1]))
    assert t["units"].tolist()[0] == 1 and np.isnan(t["units"].iloc[1])
    assert t["active_skus"].iloc[0] == 1 and pd.isna(t["active_skus"].iloc[1])
    assert t["active_skus"].iloc[2] == 1


def test_weekday_shares():
    sales = pd.DataFrame(
        {
            "invoice_date": pd.to_datetime(["2011-01-03", "2011-01-03", "2011-01-06"]),  # Mon, Thu
            "quantity": [1, 1, 2],
            "price": [1.0, 1.0, 3.0],
        }
    )
    s = weekday_shares(sales)
    assert list(s.index) == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    assert s.loc["Mon", "lines"] == pytest.approx(2 / 3)
    assert s.loc["Thu", "revenue"] == pytest.approx(6 / 8)
    assert s.loc["Sat"].sum() == 0 and s.sum().tolist() == pytest.approx([1, 1, 1])


def test_season_profile_iso_weeks():
    weeks = pd.to_datetime(["2010-01-04", "2010-12-27", "2011-01-03"])
    t = pd.DataFrame({"units": [1.0, np.nan, 3.0]}, index=weeks)
    p = season_profile(t)
    assert p.loc[1, 2010] == 1 and p.loc[1, 2011] == 3
    assert np.isnan(p.loc[52, 2010])  # closed stays missing


def test_life_cycle_and_new_product_share():
    p = panel({"old": [2, 2, 2, 2], "new": [0, 0, 1, 3]})
    lc = life_cycle(p)
    assert lc.loc["new", "first_week"] == W0 + pd.Timedelta(weeks=2)
    assert lc.loc["old", "last_week"] == W0 + pd.Timedelta(weeks=3)
    share = new_product_share(p, burn_in_weeks=1)
    assert share.tolist() == pytest.approx([0, 0, 1 / 3, 3 / 5])
