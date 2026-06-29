"""Tests for the reporting-window logic in period_config.

These guard the date-boundary handling that every "current period" figure in
the pipeline depends on. They run without any downloaded data.
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))


def _df(dates):
    return pd.DataFrame({"published": pd.to_datetime(dates, utc=True)})


def test_period_mask_includes_window_and_excludes_after():
    from period_config import period_mask

    df = _df(
        [
            "2026-01-01T00:00:00Z",  # first instant - in
            "2026-06-30T23:59:59Z",  # last instant of Jun 30 - in
            "2026-07-01T00:00:00Z",  # first instant of Jul 1 - out
            "2025-12-31T23:59:59Z",  # prior year - out
        ]
    )
    mask = period_mask(df)
    assert list(mask) == [True, True, False, False]


def test_period_mask_handles_naive_dates():
    """Naive (tz-less) timestamps should still bin correctly (coerced to UTC)."""
    from period_config import period_mask

    df = pd.DataFrame({"published": pd.to_datetime(["2026-03-15", "2025-03-15"])})
    assert list(period_mask(df)) == [True, False]


def test_prior_period_mask_selects_prior_year_same_window():
    from period_config import prior_period_mask

    df = _df(["2025-03-15T00:00:00Z", "2026-03-15T00:00:00Z", "2025-07-01T00:00:00Z"])
    assert list(prior_period_mask(df)) == [True, False, False]


def test_same_elapsed_mask_respects_asof_day():
    from period_config import same_elapsed_mask

    asof = pd.Timestamp("2026-06-26", tz="UTC")
    df = _df(
        [
            "2025-06-26T12:00:00Z",  # on the as-of day - in
            "2025-06-27T00:00:00Z",  # day after as-of - out
            "2025-01-01T00:00:00Z",  # start - in
        ]
    )
    assert list(same_elapsed_mask(df, 2025, asof)) == [True, False, True]


def test_period_days_is_full_first_half():
    from period_config import PERIOD_DAYS

    # Jan 1 -> Jul 1 (exclusive) in a non-leap year is 181 days.
    assert PERIOD_DAYS == 181
