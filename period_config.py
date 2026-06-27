#!/usr/bin/env python3
"""
Central reporting-period configuration for the 2026 First Half CVE Data Review.

The annual pipeline scoped the "current period" with a simple ``df["year"] == 2025``
equality. A mid-year review needs a real date window (Jan 1 - Jun 30) so that a
partial year is never mistaken for a full one. Every current-period filter in the
analysis scripts routes through ``period_mask`` / ``prior_period_mask`` defined here,
so the window is configured in exactly one place.
"""

import pandas as pd

# -----------------------------------------------------------------------------
# Reporting period: first half of 2026 (Jan 1 - Jun 30, inclusive)
# -----------------------------------------------------------------------------
TARGET_YEAR = 2026
PRIOR_YEAR = 2025  # used for H1-over-H1 comparisons

# Half-open interval [START, END): END is the first instant outside the window.
PERIOD_START = pd.Timestamp(f"{TARGET_YEAR}-01-01", tz="UTC")
PERIOD_END = pd.Timestamp(f"{TARGET_YEAR}-07-01", tz="UTC")

# Human-readable labels used in chart titles and prose.
PERIOD_LABEL = "H1 2026"  # short tag for chart titles
PERIOD_TITLE = "2026 First Half"  # post / report title
PERIOD_RANGE = "Jan 1 - Jun 30, 2026"

# Historical charts (CVEs-by-year, growth, data-quality) span this range.
# 2026 is included but is a PARTIAL year and must be labelled as such.
HIST_MIN_YEAR = 1999
HIST_MAX_YEAR = TARGET_YEAR

# Days elapsed in the reporting window (181 in 2026; 2026 is not a leap year).
PERIOD_DAYS = (PERIOD_END - PERIOD_START).days


def _date_column(df):
    """Return the name of the publish-date column present on ``df`` (or None)."""
    for col in ("published", "date_published"):
        if col in df.columns:
            return col
    return None


def period_mask(df, start=PERIOD_START, end=PERIOD_END):
    """Boolean mask selecting rows published within [start, end).

    Falls back to the CVE ``year`` column when no publish-date column exists, so
    the helper is a drop-in replacement for the old ``df["year"] == YEAR`` filters
    regardless of which dataset (NVD or CVE List V5) is passed in.
    """
    col = _date_column(df)
    if col is None:
        if "year" in df.columns:
            return df["year"] == start.year
        raise KeyError("DataFrame has no publish-date or year column")
    dates = pd.to_datetime(df[col], utc=True, errors="coerce")
    return (dates >= start) & (dates < end)


def prior_period_mask(df):
    """Mask for the SAME Jan 1 - Jun 30 window in the prior year (H1-over-H1)."""
    return period_mask(
        df,
        start=PERIOD_START.replace(year=PRIOR_YEAR),
        end=PERIOD_END.replace(year=PRIOR_YEAR),
    )


def filter_period(df):
    """Return a copy of ``df`` restricted to the reporting window."""
    return df[period_mask(df)].copy()


def half1_mask(df, year):
    """Mask for the full Jan 1 - Jun 30 window of any given ``year``."""
    return period_mask(
        df,
        start=pd.Timestamp(f"{year}-01-01", tz="UTC"),
        end=pd.Timestamp(f"{year}-07-01", tz="UTC"),
    )


def current_asof(df):
    """Latest publish date present in the current reporting window.

    Used to measure every prior year over the identical elapsed window. Falls
    back to the day before the window closes if no dated rows are present.
    """
    cur = df[period_mask(df)]
    col = _date_column(cur)
    if col is None or len(cur) == 0:
        return PERIOD_END - pd.Timedelta(days=1)
    dates = pd.to_datetime(cur[col], utc=True, errors="coerce").dropna()
    return dates.max() if len(dates) else (PERIOD_END - pd.Timedelta(days=1))


def same_elapsed_mask(df, year, asof):
    """Mask for Jan 1 of ``year`` through the same month/day as ``asof``.

    Keeps year-over-year comparisons fair while the current period is still in
    progress: every year is measured over the identical number of elapsed days.
    Once the reporting window closes (asof = Jun 30) this equals ``half1_mask``.
    """
    start = pd.Timestamp(f"{year}-01-01", tz="UTC")
    # Include the as-of day itself by ending at the following midnight.
    end = pd.Timestamp(f"{year}-{asof.month:02d}-{asof.day:02d}", tz="UTC") + pd.Timedelta(
        days=1
    )
    return period_mask(df, start=start, end=end)
