#!/usr/bin/env python3
"""
Generate 2026 First Half CVE Data Review Blog Post
Creates a publishable Markdown blog with all visualizations

This script imports graph generation functions from 03_generate_graphs.py
to avoid code duplication and ensure consistent styling.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import warnings
import importlib.util

import json
import re
from urllib.parse import quote_plus

from style_config import CWE_NAMES, prettify_name
from period_config import (
    period_mask,
    same_elapsed_mask,
    half1_mask,
    current_asof,
    PERIOD_START,
    PERIOD_DAYS,
    PERIOD_TITLE,
    PERIOD_RANGE,
    TARGET_YEAR,
    PRIOR_YEAR,
    HIST_MIN_YEAR,
)

warnings.filterwarnings("ignore")

# Directories
OUTPUT_DIR = Path("processed")
GRAPHS_DIR = Path("graphs")
GRAPHS_DIR.mkdir(exist_ok=True)

# Import graph generation functions - using importlib for numeric filename
spec = importlib.util.spec_from_file_location(
    "generate_graphs", "03_generate_graphs.py"
)
if spec is None or spec.loader is None:
    raise ImportError("Could not load 03_generate_graphs.py")
graphs_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(graphs_module)

# Re-export functions from graphs module for use in this script
graph_cves_by_year = graphs_module.graph_cves_by_year
graph_yoy_growth = graphs_module.graph_yoy_growth
graph_cumulative_growth = graphs_module.graph_cumulative_growth
graph_period_monthly = graphs_module.graph_period_monthly
graph_cvss_distribution = graphs_module.graph_cvss_distribution
graph_severity_breakdown = graphs_module.graph_severity_breakdown
graph_top_cwes = graphs_module.graph_top_cwes
graph_top_cnas = graphs_module.graph_top_cnas
graph_data_quality = graphs_module.graph_data_quality
graph_rejected_cves = graphs_module.graph_rejected_cves
graph_cvss_by_year = graphs_module.graph_cvss_by_year
graph_top_vendors = graphs_module.graph_top_vendors
graph_day_of_week = graphs_module.graph_day_of_week
graph_top_days = graphs_module.graph_top_days
graph_top_products = graphs_module.graph_top_products
graph_scorecard = graphs_module.graph_scorecard
normalize_data = graphs_module.normalize_data


# =============================================================================
# DATA LOADING
# =============================================================================
def load_data():
    """Load processed data, returning both filtered and full datasets"""
    print("Loading processed data...")

    nvd_df = None
    cvelist_df = None

    if (OUTPUT_DIR / "nvd_cves.parquet").exists():
        nvd_df = pd.read_parquet(OUTPUT_DIR / "nvd_cves.parquet")
        print(f"  ✓ Loaded NVD data: {len(nvd_df):,} CVEs")
    elif (OUTPUT_DIR / "nvd_cves.csv").exists():
        nvd_df = pd.read_csv(
            OUTPUT_DIR / "nvd_cves.csv", parse_dates=["published", "modified"]
        )
        print(f"  ✓ Loaded NVD data: {len(nvd_df):,} CVEs")

    if (OUTPUT_DIR / "cvelist_v5.parquet").exists():
        cvelist_df = pd.read_parquet(OUTPUT_DIR / "cvelist_v5.parquet")
        print(f"  ✓ Loaded CVE List V5 data: {len(cvelist_df):,} CVEs")
    elif (OUTPUT_DIR / "cvelist_v5.csv").exists():
        cvelist_df = pd.read_csv(
            OUTPUT_DIR / "cvelist_v5.csv",
            parse_dates=["date_reserved", "date_published"],
        )
        print(f"  ✓ Loaded CVE List V5 data: {len(cvelist_df):,} CVEs")

    # Keep full datasets for rejection analysis
    full_nvd_df = nvd_df.copy() if nvd_df is not None else None
    full_cvelist_df = cvelist_df.copy() if cvelist_df is not None else None

    # Filter out rejected CVEs for the main analysis
    if nvd_df is not None and "is_rejected" in nvd_df.columns:
        rejected_count = nvd_df["is_rejected"].sum()
        print(f"  → Filtering out {rejected_count:,} rejected CVEs from NVD data")
        nvd_df = nvd_df[~nvd_df["is_rejected"]].copy()

    if cvelist_df is not None and "is_rejected" in cvelist_df.columns:
        rejected_count = cvelist_df["is_rejected"].sum()
        print(f"  → Filtering out {rejected_count:,} rejected CVEs from CVE List V5")
        cvelist_df = cvelist_df[~cvelist_df["is_rejected"]].copy()

    # STRICT CUTOFF: exclude any data published after the target year so a
    # re-run on a later date never pulls future-dated CVEs into the totals.
    if nvd_df is not None and "year" in nvd_df.columns:
        future_count = (nvd_df["year"] > TARGET_YEAR).sum()
        if future_count > 0:
            print(
                f"  → Excluding {future_count:,} CVEs from after {TARGET_YEAR} (strict cutoff)"
            )
            nvd_df = nvd_df[nvd_df["year"] <= TARGET_YEAR].copy()

    if cvelist_df is not None and "year" in cvelist_df.columns:
        future_count = (cvelist_df["year"] > TARGET_YEAR).sum()
        if future_count > 0:
            print(
                f"  → Excluding {future_count:,} CVEs from after {TARGET_YEAR} (strict cutoff)"
            )
            cvelist_df = cvelist_df[cvelist_df["year"] <= TARGET_YEAR].copy()

    # Also apply cutoff to full datasets used for rejection analysis
    if full_nvd_df is not None and "year" in full_nvd_df.columns:
        full_nvd_df = full_nvd_df[full_nvd_df["year"] <= TARGET_YEAR].copy()

    if full_cvelist_df is not None and "year" in full_cvelist_df.columns:
        full_cvelist_df = full_cvelist_df[full_cvelist_df["year"] <= TARGET_YEAR].copy()

    # Return both filtered (active) and full datasets
    return nvd_df, cvelist_df, full_nvd_df, full_cvelist_df


# =============================================================================
# HELPERS
# =============================================================================
def _movers(cur_counts, prior_counts, topn=5):
    """Rank the top ``topn`` of ``cur_counts`` and tag movement vs prior period."""
    prior_rank = {name: i + 1 for i, name in enumerate(prior_counts.index)}
    out = []
    for i, (name, cnt) in enumerate(cur_counts.head(topn).items()):
        pr = prior_rank.get(name)
        cur_rank = i + 1
        if pr is None:
            status = "new"
        elif pr > cur_rank:
            status = "up"
        elif pr < cur_rank:
            status = "down"
        else:
            status = "flat"
        out.append(
            {"name": name, "count": int(cnt), "prior_rank": pr, "status": status}
        )
    return out


def cwe_link(cwe):
    """Markdown link from a CWE id to its MITRE definition page."""
    num = cwe.split("-")[1] if "-" in cwe else cwe
    return f"[{cwe}](https://cwe.mitre.org/data/definitions/{num}.html)"


def pretty(name):
    """Human-friendly display of a normalized vendor/product slug."""
    return prettify_name(name)


def vendor_link(vendor):
    """Markdown link from a vendor to its NVD advanced-search results."""
    slug = quote_plus(str(vendor).lower().strip())
    base = (
        "https://nvd.nist.gov/vuln/search/results?form_type=Advanced"
        "&results_type=overview&search_type=all&isCpeNameSearch=false&cpe_vendor="
    )
    return f"[{pretty(vendor)}]({base}{slug})"


# Known first-party sub-CNAs: CNA short name -> parent vendor it assigns for.
_FIRST_PARTY_CNA = {
    "chrome": "google",
    "android": "google",
    "github_m": "github",
}


def _is_self_assigned(cna, name):
    """True when the dominant CNA looks like the vendor/product itself."""
    a = re.sub(r"[^a-z0-9]", "", str(cna).lower())
    b = re.sub(r"[^a-z0-9]", "", str(name).lower())
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    parent = _FIRST_PARTY_CNA.get(str(cna).lower())
    return bool(parent and re.sub(r"[^a-z0-9]", "", parent) in b)


def cna_concentration(cvelist_df, asof, top_n=15, threshold=0.6, fields=("vendor",)):
    """Flag report callouts dominated by a single THIRD-PARTY CNA.

    When one CNA that is not the vendor itself assigns most of a vendor's CVEs
    (as VulnCheck did for OpenClaw), a "top vendor" callout can reflect one
    researcher group's disclosure push rather than broad activity. Self-assigned
    dominance (the Linux CNA for Linux, Chrome for Google, etc.) is expected and
    skipped. Defaults to vendors only; product names rarely match their owning
    CNA textually, so checking them is noisy. Returns the flagged items.
    """
    flagged = []
    if cvelist_df is None or "assigner_short_name" not in cvelist_df.columns:
        return flagged

    cur = cvelist_df[same_elapsed_mask(cvelist_df, TARGET_YEAR, asof)]
    exclude = {"n/a", "unknown", "none", "na", "n_a", "*", ""}
    for field in fields:
        if field not in cur.columns:
            continue
        sub = cur[cur[field].notna()].copy()
        sub["_key"] = sub[field].astype(str).str.lower().str.strip()
        sub = sub[~sub["_key"].isin(exclude)]
        for name, total in sub["_key"].value_counts().head(top_n).items():
            ac = sub[sub["_key"] == name]["assigner_short_name"].value_counts()
            if ac.empty:
                continue
            top_cna, top_ct = str(ac.index[0]), int(ac.iloc[0])
            share = top_ct / total
            if share >= threshold and not _is_self_assigned(top_cna, name):
                flagged.append(
                    {
                        "type": field,
                        "name": name,
                        "total": int(total),
                        "top_cna": top_cna,
                        "top_cna_count": top_ct,
                        "share": round(share * 100, 1),
                    }
                )

    if flagged:
        print("\n" + "!" * 64)
        print("CNA CONCENTRATION WARNING: callouts dominated by one third-party CNA")
        print("!" * 64)
        for f in sorted(flagged, key=lambda x: -x["share"]):
            print(
                f"  {f['type']:7} {f['name'][:26]:26} {f['total']:>5} CVEs  "
                f"{f['share']:>5.1f}% from {f['top_cna']}"
            )
        print(
            "Review before publishing: a spotlight on any of these reflects one "
            "group's disclosure push, not broad activity.\n"
        )
    return flagged


# =============================================================================
# STATISTICS CALCULATION
# =============================================================================
def calculate_stats(df, cvelist_df, full_nvd_df=None, full_cvelist_df=None):
    """Calculate all statistics for the blog"""
    stats = {}

    df_2025 = df[period_mask(df)].copy()  # current period: H1 2026 (to as-of date)

    # As-of date = latest publish date in the current window. Year-over-year
    # comparisons use the SAME elapsed window in prior years, so a partial half
    # is never measured against a full one. Once the window closes (Jun 30) the
    # same-elapsed window equals the full first half.
    pubs = pd.to_datetime(df_2025["published"], utc=True, errors="coerce").dropna()
    asof = pubs.max() if len(pubs) else PERIOD_START
    stats["asof"] = asof
    stats["asof_label"] = f"{asof:%b} {asof.day}"
    stats["window_complete"] = (asof.month, asof.day) >= (6, 30)

    df_2024 = df[same_elapsed_mask(df, PRIOR_YEAR, asof)]  # same window, prior year

    stats["total_2025"] = len(df_2025)
    stats["total_2024"] = len(df_2024)
    stats["total_all_time"] = len(df)
    stats["yoy_change"] = (
        ((stats["total_2025"] - stats["total_2024"]) / stats["total_2024"] * 100)
        if stats["total_2024"] > 0
        else 0
    )

    # Per-day pace + two independent full-year projections.
    span_days = max((asof - PERIOD_START).days + 1, 1)
    stats["days_elapsed"] = span_days
    stats["cves_per_day"] = len(df_2025) / span_days if span_days else 0
    stats["projected_runrate"] = round(stats["cves_per_day"] * 365)
    # Seasonality-adjusted: scale the estimated full H1 by the prior year's H1
    # share of its full-year total (CVE publishing is not evenly spread).
    full_prior = int((df["year"] == PRIOR_YEAR).sum())
    h1_prior_full = int(half1_mask(df, PRIOR_YEAR).sum())
    h1_share = (h1_prior_full / full_prior) if full_prior else 0.5
    stats["h1_share_prior"] = h1_share * 100
    est_full_h1 = stats["cves_per_day"] * PERIOD_DAYS
    stats["projected_seasonal"] = round(est_full_h1 / h1_share) if h1_share else 0
    stats["projected_full_year"] = stats["projected_runrate"]  # back-compat

    # Human-scale framings for the lead.
    stats["minutes_between"] = (1440 / stats["cves_per_day"]) if stats["cves_per_day"] else 0
    # Most recent full year whose total is still below this half's count.
    fy = df.groupby("year").size()
    h1_total = stats["total_2025"]
    exceeds = [
        y for y in range(TARGET_YEAR - 1, 1998, -1) if int(fy.get(y, 0)) < h1_total
    ]
    stats["h1_exceeds_year"] = exceeds[0] if exceeds else None
    stats["h1_exceeds_year_total"] = int(fy.get(exceeds[0], 0)) if exceeds else 0

    # H1-over-H1 comparison across three years, identical elapsed window each.
    cvss_col0 = "cvss_v3" if "cvss_v3" in df.columns else "cvss_v4"
    compare = []
    for y in (TARGET_YEAR - 2, TARGET_YEAR - 1, TARGET_YEAR):
        d = df[same_elapsed_mask(df, y, asof)]
        compare.append(
            {
                "year": y,
                "total": len(d),
                "per_day": len(d) / span_days if span_days else 0,
                "avg_cvss": d[cvss_col0].mean()
                if cvss_col0 in d.columns and len(d)
                else 0,
            }
        )
    stats["h1_compare"] = compare

    # Rejected CVE statistics (from full datasets)
    stats["rejected_2025"] = 0
    stats["rejected_all_time"] = 0
    if full_nvd_df is not None and "is_rejected" in full_nvd_df.columns:
        stats["rejected_all_time"] = full_nvd_df["is_rejected"].sum()
        stats["rejected_2025"] = full_nvd_df[
            (period_mask(full_nvd_df)) & (full_nvd_df["is_rejected"])
        ].shape[0]
    elif full_cvelist_df is not None and "is_rejected" in full_cvelist_df.columns:
        stats["rejected_all_time"] = full_cvelist_df["is_rejected"].sum()
        stats["rejected_2025"] = full_cvelist_df[
            (period_mask(full_cvelist_df)) & (full_cvelist_df["is_rejected"])
        ].shape[0]

    # Calculate rejection rate
    total_with_rejected_2025 = stats["total_2025"] + stats["rejected_2025"]
    stats["rejection_rate_2025"] = (
        (stats["rejected_2025"] / total_with_rejected_2025 * 100)
        if total_with_rejected_2025 > 0
        else 0
    )

    # Severity
    if "severity" in df_2025.columns:
        severity_counts = df_2025["severity"].str.upper().value_counts()
        stats["critical"] = severity_counts.get("CRITICAL", 0)
        stats["high"] = severity_counts.get("HIGH", 0)
        stats["medium"] = severity_counts.get("MEDIUM", 0)
        stats["low"] = severity_counts.get("LOW", 0)
    else:
        stats["critical"] = stats["high"] = stats["medium"] = stats["low"] = 0

    # CVSS
    cvss_col = "cvss_v3" if "cvss_v3" in df.columns else "cvss_v4"
    if cvss_col in df_2025.columns:
        stats["avg_cvss"] = df_2025[cvss_col].mean()
        stats["median_cvss"] = df_2025[cvss_col].median()
        stats["cvss_coverage"] = df_2025[cvss_col].notna().sum() / len(df_2025) * 100
    else:
        stats["avg_cvss"] = stats["median_cvss"] = stats["cvss_coverage"] = 0

    # CWE
    if "cwe" in df_2025.columns:
        stats["cwe_coverage"] = df_2025["cwe"].notna().sum() / len(df_2025) * 100
        stats["top_cwe"] = (
            df_2025["cwe"].value_counts().index[0]
            if df_2025["cwe"].notna().any()
            else "N/A"
        )
        stats["top_cwe_count"] = (
            df_2025["cwe"].value_counts().iloc[0] if df_2025["cwe"].notna().any() else 0
        )
    else:
        stats["cwe_coverage"] = 0
        stats["top_cwe"] = "N/A"
        stats["top_cwe_count"] = 0

    # CPE
    if "has_cpe" in df_2025.columns:
        stats["cpe_coverage"] = df_2025["has_cpe"].sum() / len(df_2025) * 100
    else:
        stats["cpe_coverage"] = 0

    # Yearly data
    yearly = df.groupby("year").size().reset_index(name="count")
    yearly = yearly[
        (yearly["year"] >= HIST_MIN_YEAR) & (yearly["year"] <= TARGET_YEAR)
    ]
    stats["yearly"] = yearly

    # CVE List V5 specific stats
    if cvelist_df is not None:
        cv_2025 = cvelist_df[period_mask(cvelist_df)]

        if "assigner_short_name" in cv_2025.columns:
            stats["unique_cnas"] = cv_2025["assigner_short_name"].nunique()
            cna_counts = cv_2025["assigner_short_name"].value_counts()
            stats["top_cna"] = cna_counts.index[0] if len(cna_counts) > 0 else "N/A"
            stats["top_cna_count"] = cna_counts.iloc[0] if len(cna_counts) > 0 else 0

        if "state" in cv_2025.columns:
            state_counts = cv_2025["state"].value_counts()
            stats["published"] = state_counts.get("PUBLISHED", 0)
            stats["rejected"] = state_counts.get("REJECTED", 0)
            stats["reserved"] = state_counts.get("RESERVED", 0)

        if "vendor" in cv_2025.columns:
            stats["unique_vendors"] = cv_2025["vendor"].nunique()

    # ----- "What changed" movers vs the same window a year ago -----------------
    asof = stats["asof"]

    if cvelist_df is not None and "assigner_short_name" in cvelist_df.columns:
        cur = cvelist_df[same_elapsed_mask(cvelist_df, TARGET_YEAR, asof)][
            "assigner_short_name"
        ].value_counts()
        pri = cvelist_df[same_elapsed_mask(cvelist_df, PRIOR_YEAR, asof)][
            "assigner_short_name"
        ].value_counts()
        stats["cna_movers"] = _movers(cur, pri, 5)

    if "product" in df.columns:
        cur_p = df[same_elapsed_mask(df, TARGET_YEAR, asof) & df["product"].notna()][
            "product"
        ].value_counts().head(8)
        pri_p = set(
            df[same_elapsed_mask(df, PRIOR_YEAR, asof) & df["product"].notna()][
                "product"
            ].value_counts().head(8).index
        )
        stats["new_products"] = [p for p in cur_p.index if p not in pri_p][:4]

    if "cwe" in df.columns:
        cur_c = df[same_elapsed_mask(df, TARGET_YEAR, asof) & df["cwe"].notna()][
            "cwe"
        ].value_counts()
        pri_c = df[same_elapsed_mask(df, PRIOR_YEAR, asof) & df["cwe"].notna()][
            "cwe"
        ].value_counts()
        stats["cwe_movers"] = _movers(cur_c, pri_c, 5)

    # OpenClaw assigner breakdown: who actually issued these CVEs (third-party
    # researchers vs the project itself). This is the story behind the count.
    if cvelist_df is not None and "vendor" in cvelist_df.columns:
        ocv = cvelist_df[same_elapsed_mask(cvelist_df, TARGET_YEAR, asof)]
        ocv = ocv[ocv["vendor"].astype(str).str.lower().str.strip() == "openclaw"]
        if len(ocv) and "assigner_short_name" in ocv.columns:
            ac = ocv["assigner_short_name"].value_counts()
            stats["openclaw"] = {
                "total": int(len(ocv)),
                "top_assigner": str(ac.index[0]),
                "top_assigner_count": int(ac.iloc[0]),
            }

    return stats


# =============================================================================
# BLOG GENERATION
# =============================================================================
def generate_blog(
    stats,
    top_cwes,
    top_cnas,
    top_vendors,
    peak_month,
    peak_count,
    cumulative_total,
    rejected_stats=None,
    day_stats=None,
    top_days=None,
    top_products=None,
    forecast=None,
    kev=None,
):
    """Generate the Markdown blog post"""

    # Dynamic date - use current date
    current_date = datetime.now().strftime("%B %d, %Y")

    # Precomputed framing helpers
    kev = kev or {}
    asof_label = stats.get("asof_label", "Jun 30")
    complete = stats.get("window_complete", False)
    window_note = (
        ""
        if complete
        else f" Numbers run through {asof_label}; the window closes June 30, so treat them as a floor."
    )
    proj_lo = min(stats["projected_runrate"], stats["projected_seasonal"])
    proj_hi = max(stats["projected_runrate"], stats["projected_seasonal"])
    direction = "an increase" if stats["yoy_change"] > 0 else "a decrease"
    # Lead-framing helpers
    kev_in = kev.get("h1_published_in_kev")
    kev_pct = (kev_in / max(stats["total_2025"], 1) * 100) if kev_in is not None else None
    exceeds_year = stats.get("h1_exceeds_year")
    scale_clause = (
        f", more in six months than any full year before {exceeds_year + 1} "
        f"(all of {exceeds_year} finished at {stats['h1_exceeds_year_total']:,})"
        if exceeds_year
        else ""
    )
    if kev_pct is not None:
        exploit_line = (
            f" And yet only **{kev_in} of them, {kev_pct:.2f}%, are known to be exploited.** "
            "That gap is the story of 2026 so far: we are minting CVEs faster than ever while "
            "real-world exploitation stays flat, so the hard problem is signal-to-noise, not patch volume."
        )
    else:
        exploit_line = ""

    # Severity percentages, guarded against an empty current period so a
    # bad/partial data load degrades to 0% instead of a ZeroDivisionError.
    _tot = max(stats["total_2025"], 1)
    sev_pct = {
        k: stats[k] / _tot * 100 for k in ("critical", "high", "medium", "low")
    }
    crit_high_pct = (stats["critical"] + stats["high"]) / _tot * 100

    blog = f"""# {PERIOD_TITLE} CVE Data Review

<!-- Featured image suggestion: graphs/00_scorecard.png (mid-year stat card) or graphs/01_cves_by_year.png (2026 towers over every prior H1) -->

We are halfway through 2026, so it is time for the mid-year CVE check-in. The short version: the volume curve has gone vertical while exploitation has not. This review covers everything published in the first half of 2026 ({PERIOD_RANGE}), the volume, the severity, what is actually being exploited, and who is driving the numbers, all measured against the same elapsed window a year ago so a partial half is never compared to a full one.

## TL;DR

**The first half of 2026 produced {stats["total_2025"]:,} CVEs{scale_clause}.** That works out to one new CVE every **{stats["minutes_between"]:.1f} minutes**, {direction} of **{abs(stats["yoy_change"]):.1f}%** over the same window in {PRIOR_YEAR} ({stats["total_2024"]:,}).{exploit_line}

At this pace the year projects to roughly **{proj_lo:,} to {proj_hi:,}**, and the all-time catalog has now passed **{stats["total_all_time"]:,} CVEs** since 1999.{window_note}

> **Note**: All statistics in this report exclude rejected CVEs to provide an accurate count of active vulnerabilities.

### Key Statistics at a Glance

| Metric | Value |
|--------|-------|
| **Total CVEs (H1 2026)** | **{stats["total_2025"]:,}** |
| CVEs per Day | {stats["cves_per_day"]:.1f} |
| Change vs same window {PRIOR_YEAR} | {stats["yoy_change"]:+.1f}% |
| Projected Full Year | {proj_lo:,} - {proj_hi:,} |
| Critical Severity | {stats["critical"]:,} |
| High Severity | {stats["high"]:,} |
| Average CVSS Score | {stats["avg_cvss"]:.2f} |
| CVSS Coverage | {stats["cvss_coverage"]:.1f}% |
| CWE Coverage | {stats["cwe_coverage"]:.1f}% |
"""

    if "unique_cnas" in stats:
        blog += f"| Active CNAs | {stats['unique_cnas']:,} |\n"

    if stats.get("rejected_2025", 0) > 0:
        blog += f"| Rejected CVEs (H1 2026) | {stats['rejected_2025']:,} |\n"

    if kev.get("h1_published_in_kev") is not None:
        blog += f"| Already Known-Exploited (KEV) | {kev['h1_published_in_kev']} |\n"

    # H1-over-H1 comparison table, identical elapsed window each year.
    cmp_rows = ""
    for c in stats.get("h1_compare", []):
        tag = " *(partial)*" if c["year"] == TARGET_YEAR and not complete else ""
        cmp_rows += (
            f"| Jan 1 - {asof_label}, {c['year']}{tag} | {c['total']:,} | "
            f"{c['per_day']:.1f} | {c['avg_cvss']:.2f} |\n"
        )

    # Forecast scorecard, reframed: straight-line projections vs the model call.
    if forecast and forecast.get("full_year_forecast"):
        fc = forecast["full_year_forecast"]
        model = forecast.get("model")
        mape = forecast.get("model_mape")
        model_note = f" ({model}, MAPE {mape})" if model else ""
        url = forecast.get("url", "https://www.cveforecast.org")
        gap = fc - proj_hi
        if gap > 0:
            interp = (
                f"That is **{gap:,} above** the top of the straight-line range, and here is where I "
                f"will plant a flag: **I think the model is high.** Two independent methods both land "
                f"near {proj_hi:,}, and the forecast's entire gap to them rests on a heavy second-half "
                f"surge that still has to show up. **My call is the year closes nearer {proj_hi:,} than "
                f"{fc:,}.** I will happily eat those words in the December review if H2 accelerates the "
                f"way the model expects, but the burden of proof is on the surge."
            )
        else:
            interp = "That sits inside the straight-line range, so 2026 is tracking the model."
        forecast_block = (
            f"[CVEForecast]({url}) projects **{fc:,} CVEs** for full-year 2026{model_note}. {interp}"
        )
    else:
        forecast_block = (
            "_Forecast comparison pending: run `08_forecast_scorecard.py` to pull the latest "
            "number from [cveforecast.org](https://www.cveforecast.org)._"
        )

    # "What changed" callouts vs the same window a year ago.
    changed_bits = []
    movers = stats.get("cna_movers", [])
    if movers:
        leader = movers[0]
        new_cnas = [m["name"] for m in movers if m["status"] == "new"]
        lead_txt = (
            f"**{leader['name']}** is the busiest CNA at **{leader['count']:,}** assignments"
        )
        if new_cnas:
            joined = ", ".join(new_cnas)
            verb = "is" if len(new_cnas) == 1 else "are"
            lead_txt += f", and {joined} {verb} new to the top five"
        changed_bits.append(lead_txt + ".")
    if stats.get("new_products"):
        nps = ", ".join(pretty(p) for p in stats["new_products"])
        changed_bits.append(f"New to the most-affected product list this year: **{nps}**.")
    for idx, m in enumerate(stats.get("cwe_movers", [])):
        if m["status"] in ("new", "up"):
            nm = CWE_NAMES.get(m["name"], m["name"])
            verb = "is new to" if m["status"] == "new" else f"climbed to #{idx + 1} in"
            changed_bits.append(
                f"Among weakness types, {cwe_link(m['name'])} ({nm}) {verb} the top five."
            )
            break
    # Editorial spotlight: OpenClaw, where most CVEs come from third-party
    # researchers (VulnCheck) rather than the project itself.
    openclaw_spotlight = ""
    oc = stats.get("openclaw")
    if oc and oc.get("total"):
        share = oc["top_assigner_count"] / max(oc["total"], 1) * 100
        openclaw_spotlight = (
            "\n\n**Spotlight: OpenClaw.** A project that barely existed a year ago, OpenClaw "
            "(Peter Steinberger's viral local AI agent, the subject of "
            "[Lex Fridman Podcast #491](https://lexfridman.com/peter-steinberger/)) is already one "
            f"of the most-reported products of the half with **{oc['total']:,} CVEs**. The striking "
            f"part is who is doing the reporting: **{oc['top_assigner']} alone assigned "
            f"{oc['top_assigner_count']:,}** of them ({share:.0f}%), disclosed steadily across the "
            "half rather than in a single dump. That is what a research magnet looks like, an outside "
            "team systematically working a hot new target. To its credit the project also embraced "
            "the CVE lifecycle itself, issuing advisories through GitHub as reports came in. I track "
            "its CVEs at [OpenClawCVEs](https://github.com/jgamblin/OpenClawCVEs)."
        )

    if changed_bits or openclaw_spotlight:
        changed_section = (
            "## What Changed in H1 2026\n\n"
            + " ".join(changed_bits)
            + openclaw_spotlight
            + "\n\n---\n\n"
        )
    else:
        changed_section = ""

    blog += f"""
---

## H1-over-H1: Three Years Side by Side

To keep the comparison honest while 2026 is still in progress, each year is measured over the identical window (January 1 through {asof_label}).

| Window | CVEs | Per Day | Avg CVSS |
|--------|------|---------|----------|
{cmp_rows}
---

## Forecast Scorecard: Are We On Pace?

At **{stats["cves_per_day"]:.1f} CVEs/day**, two independent methods converge on the full-year number: the run-rate extrapolates to **{stats["projected_runrate"]:,}**, and a seasonality-adjusted estimate (using {PRIOR_YEAR}'s {stats["h1_share_prior"]:.0f}% first-half share) to **{stats["projected_seasonal"]:,}**.

{forecast_block}

---

{changed_section}## Historical CVE Growth

To compare like with like, this chart counts only the first half of every year (January 1 through {asof_label}). On that basis 2026 already stands taller than any prior first half: more CVEs in six months than the same window has ever produced.

![First-Half CVEs by Year](graphs/01_cves_by_year.png)

First-half growth has been relentless, and 2026 is **{stats["yoy_change"]:+.1f}%** on the first half of {PRIOR_YEAR}.

![First-Half Year-over-Year Growth](graphs/02_yoy_growth.png)

Counting full years, the cumulative catalog has now passed **{stats["total_all_time"]:,} CVEs**.

![Cumulative Growth](graphs/03_cumulative_growth.png)

---

## Monthly Distribution (H1 2026)

"""

    if peak_month and peak_count:
        blog += f"""CVE publications varied across the first half of 2026, with **{peak_month}** being the peak month at **{peak_count:,} CVEs**.

![Monthly Distribution](graphs/04_h1_monthly.png)

---
"""

    # Day of Week Analysis - drive the framing from the actual peak day.
    if day_stats:
        _full_day = {
            "Mon": "Monday",
            "Tue": "Tuesday",
            "Wed": "Wednesday",
            "Thu": "Thursday",
            "Fri": "Friday",
            "Sat": "Saturday",
            "Sun": "Sunday",
        }
        peak_day = _full_day.get(day_stats["peak_day"], day_stats["peak_day"])
        peak_dc = day_stats["peak_count"]
        tue = day_stats["tuesday_count"]
        if str(peak_day).lower().startswith("tue"):
            day_line = (
                f"The Patch Tuesday effect is clear: **Tuesday** leads at "
                f"**{peak_dc:,} CVEs**, well above the weekday average."
            )
        else:
            day_line = (
                f"Publishing clusters midweek. **{peak_day}** is the busiest day at "
                f"**{peak_dc:,} CVEs**, with Tuesday close behind at **{tue:,}**. Patch "
                f"Tuesday is part of the story, but the midweek bulge owes as much to the "
                f"high-volume CNAs (GitHub, Linux, the WordPress plugin crowd) that "
                f"batch-publish midweek."
            )
        blog += f"""
## Publication Patterns by Day of Week

{day_line}

![CVEs by Day of Week](graphs/16_day_of_week.png)

Weekdays average **{day_stats["weekday_avg"]:,.0f}** CVEs against just **{day_stats["weekend_avg"]:,.0f}** on weekends.

---
"""

    # Top Days
    if top_days and len(top_days) > 0:
        blog += """
## Busiest Days of H1 2026

Some days saw massive spikes in CVE publications:

![Top Days](graphs/17_top_days.png)

### Top 5 Busiest Days

| Rank | Date | CVE Count |
|------|------|----------|
"""
        for i, (date, count) in enumerate(top_days[:5], 1):
            blog += f"| {i} | {date} | {count:,} |\n"
        blog += "\n---\n"

    blog += f"""
## CVSS Score Analysis

The Common Vulnerability Scoring System (CVSS) helps standardize severity assessments. Here's how H1 2026 CVEs were distributed across the scoring range.

![CVSS Distribution](graphs/05_cvss_distribution.png)

The **average CVSS score for H1 2026 was {stats["avg_cvss"]:.2f}**, with a **median of {stats["median_cvss"]:.2f}**.

### Severity Breakdown

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | {stats["critical"]:,} | {sev_pct["critical"]:.1f}% |
| High | {stats["high"]:,} | {sev_pct["high"]:.1f}% |
| Medium | {stats["medium"]:,} | {sev_pct["medium"]:.1f}% |
| Low | {stats["low"]:,} | {sev_pct["low"]:.1f}% |

![Severity Breakdown](graphs/06_severity_breakdown.png)

### CVSS Trends Over Time

![CVSS by Year](graphs/13_cvss_by_year.png)

---

## Top Weakness Types (CWE)

The Common Weakness Enumeration (CWE) categorizes the types of security weaknesses. Here are the most prevalent weakness types in H1 2026:

![Top CWEs](graphs/07_top_cwes.png)

### Top 5 CWEs in H1 2026

| Rank | CWE | Name | Count |
|------|-----|------|-------|
"""

    for i, (cwe, count) in enumerate(top_cwes, 1):
        name = CWE_NAMES.get(cwe, "")
        blog += f"| {i} | {cwe_link(cwe)} | {name} | {count:,} |\n"

    blog += """
---

## CVE Numbering Authorities (CNAs)

The CNA mix keeps tilting toward platform security teams and third-party aggregators rather than the original product vendors. The most active assigners this year:

![Top CNAs](graphs/08_top_cnas.png)

### Top 5 CNAs in H1 2026

| Rank | CNA | CVEs Assigned |
|------|-----|---------------|
"""

    for i, (cna, count) in enumerate(top_cnas, 1):
        blog += f"| {i} | {cna} | {count:,} |\n"

    if "unique_cnas" in stats:
        blog += f"\nIn total, **{stats['unique_cnas']} unique CNAs** assigned CVEs in H1 2026.\n"

    blog += """
---

## Top Vendors

The vendors with the most CVEs attributed to their products this year (each links to its NVD search):

![Top Vendors](graphs/14_top_vendors.png)

### Top 5 Vendors in H1 2026

| Rank | Vendor | CVE Count |
|------|--------|-----------|
"""

    for i, (vendor, count) in enumerate(top_vendors, 1):
        blog += f"| {i} | {vendor_link(vendor)} | {count:,} |\n"

    # Products (now after vendors, so "drilling past vendors" is accurate)
    if top_products and len(top_products) > 0:
        blog += """
---

## Most Vulnerable Products

Drilling past vendors to specific products, the H1 2026 leaders:

![Top Products](graphs/18_top_products.png)

### Top 5 Products

| Rank | Product | CVE Count |
|------|---------|----------|
"""
        for i, (product, count) in enumerate(top_products[:5], 1):
            blog += f"| {i} | {pretty(product)} | {count:,} |\n"

    # Known-Exploited Vulnerabilities (CISA KEV)
    if kev.get("h1_published_in_kev") is not None:
        total_pub = max(kev.get("h1_published_total", 0), 1)
        in_kev = kev["h1_published_in_kev"]
        pct = in_kev / total_pub * 100
        added = kev.get("added_h1", 0)
        added_prior = kev.get("added_h1_prior", 0)
        added_dir = (
            "more than"
            if added > added_prior
            else ("fewer than" if added < added_prior else "the same as")
        )
        blog += f"""
---

## Known-Exploited Vulnerabilities (CISA KEV)

Volume is the headline, but exploitation is what should actually drive patching. Of the **{kev.get("h1_published_total", 0):,}** CVEs published in H1 2026, only **{in_kev}** ({pct:.2f}%) have shown up in the [CISA KEV catalog]({kev.get("url")}) so far. That gap is the prioritization signal: the overwhelming majority of CVEs are not known to be exploited, so triaging on exploitability beats chasing raw counts.

CISA added **{added}** entries to KEV during the first half ({added_dir} the **{added_prior}** added in the same window of {PRIOR_YEAR}), and **{kev.get("ransomware_h1", 0)}** of those are tied to known ransomware campaigns.
"""
        ex_rows = ""
        for e in kev.get("examples", [])[:5]:
            ex_rows += (
                f"| {e['cve']} | {pretty(e.get('vendor') or '')} | {e.get('product') or ''} | "
                f"{e.get('date_added') or ''} | {'Yes' if e.get('ransomware') else ''} |\n"
            )
        if ex_rows:
            blog += f"""
### H1 2026 CVEs Already in KEV

| CVE | Vendor | Product | Added | Ransomware |
|-----|--------|---------|-------|------------|
{ex_rows}"""

    blog += f"""
---

## Data Quality

Not all CVEs have complete metadata. Here's how data quality has evolved over the years:

![Data Quality](graphs/09_data_quality.png)

### H1 2026 Data Quality Metrics

| Metric | Coverage |
|--------|----------|
| CVSS Score | {stats["cvss_coverage"]:.1f}% |
| CWE Classification | {stats["cwe_coverage"]:.1f}% |
| CPE Identifiers | {stats["cpe_coverage"]:.1f}% |

---

## Rejected CVEs

Not all CVE IDs stay active. Some are rejected for duplicates, disputes, or invalid submissions, and the rejection rate is a useful read on the ecosystem's quality control.

"""

    if rejected_stats:
        blog += f"""![Rejected CVEs](graphs/10_rejected_cves.png)

### H1 2026 Rejection Statistics

| Metric | Value |
|--------|-------|
| Rejected CVEs in H1 2026 | {rejected_stats["rejected_2025"]:,} |
| H1 2026 Rejection Rate | {rejected_stats["rate_2025"]:.2f}% |
| Total Rejected (All Time) | {rejected_stats["total_rejected"]:,} |

CVE rejections occur for several reasons:
- **Duplicates**: The same vulnerability assigned multiple CVE IDs
- **Disputes**: Vendor disagreement that the issue is a vulnerability
- **Invalid**: Not a security vulnerability or insufficient information
- **Withdrawn**: CVE withdrawn by the assigning CNA

"""
    else:
        blog += """*Rejection data analysis unavailable.*

"""

    # Data-driven CWE takeaway (replaces the old "memory safety dominates" line)
    cwe_names_top = ", ".join(CWE_NAMES.get(c, c) for c, _ in (top_cwes or [])[:4])
    kev_takeaway = ""
    if kev.get("h1_published_in_kev") is not None:
        total_pub = max(kev.get("h1_published_total", 0), 1)
        kev_pct = kev["h1_published_in_kev"] / total_pub * 100
        kev_takeaway = (
            f"\n\n6. **Exploitation stays rare**: just {kev['h1_published_in_kev']} of "
            f"{kev.get('h1_published_total', 0):,} H1 CVEs ({kev_pct:.2f}%) are in CISA KEV. "
            f"Volume is a triage problem, not a patch-everything problem."
        )

    # Role-based "what this means" + a forward-looking prediction.
    if kev.get("h1_published_in_kev") is not None:
        _kpct = kev["h1_published_in_kev"] / max(stats["total_2025"], 1) * 100
        defender_line = (
            f"- **If you defend a network:** ignore the headline count. With only **{_kpct:.2f}%** of "
            f"H1 CVEs known-exploited, exploitability is your filter, not volume. Wire CISA KEV and "
            f"EPSS into triage and let the long tail wait."
        )
    else:
        defender_line = (
            "- **If you defend a network:** triage on exploitability, not raw counts. Wire CISA KEV "
            "and EPSS into your pipeline."
        )
    role_section = (
        "### What this means for you\n\n"
        + defender_line
        + "\n- **If you run a CNA:** the center of gravity has shifted to platforms and aggregators. "
        "Throughput and data quality, CPE coverage especially, are the differentiators now.\n"
        + f"- **If you consume NVD data:** enrichment is the bottleneck. CPE at {stats['cpe_coverage']:.1f}% "
        "means nearly half of new CVEs cannot be auto-matched to a product, and volume only widens that gap.\n"
    )
    if forecast and forecast.get("full_year_forecast"):
        watching = (
            f"My call from the scorecard stands: 2026 closes nearer **{proj_hi:,}** than the "
            f"**{forecast['full_year_forecast']:,}** forecast. Two things would change my mind: a "
            f"December disclosure surge bigger than {PRIOR_YEAR}'s, or another OpenClaw-style project "
            "flooding the catalog. The year-end review settles it."
        )
    else:
        watching = (
            f"The straight-line pace points to roughly **{proj_lo:,} to {proj_hi:,}** for the year. "
            "The year-end review settles it."
        )

    blog += f"""---

## Conclusions

### Key Takeaways from the First Half of 2026

1. **Volume keeps climbing**: {stats["total_2025"]:,} CVEs in roughly six months, {"up" if stats["yoy_change"] > 0 else "down"} {abs(stats["yoy_change"]):.1f}% on the same window last year, with the full year projecting to {proj_lo:,}-{proj_hi:,}.

2. **Severity stays heavy**: {stats["critical"] + stats["high"]:,} CVEs ({crit_high_pct:.1f}%) are Critical or High.

3. **Web and access-control flaws lead**: {cwe_names_top} headline the CWE list. Memory-safety issues barely register in the top tier this half.

4. **The CNA mix is shifting**: platform teams and aggregators, not the original vendors, now top the assigner list, and the lineup reshuffled from a year ago.

5. **Coverage gaps persist**: CVSS and CWE are well covered, but CPE sits at {stats["cpe_coverage"]:.1f}%, which still hampers automated matching.{kev_takeaway}

{role_section}
### What I'm watching in H2

{watching}

---

## Methodology and Reproducibility

Two primary data sources, plus two enrichment feeds:

1. **NVD JSON** - National Vulnerability Database export from [nvd.handsonhacking.org](https://nvd.handsonhacking.org/nvd.json)
2. **CVE List V5** - Official CVE records from [CVEProject/cvelistV5](https://github.com/CVEProject/cvelistV5)
3. **Forecast** - [CVEForecast](https://www.cveforecast.org) full-year projection
4. **Exploitation** - [CISA KEV catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)

Everything here is reproducible. The full pipeline (Python, pandas, matplotlib) is on GitHub at [jgamblin/H12026CVEBlog](https://github.com/jgamblin/H12026CVEBlog), and it leans on the free CVE tooling I build at [RogoLabs](https://rogolabs.net): [cve.icu](https://cve.icu), [cnascorecard.org](https://cnascorecard.org), and [cveforecast.org](https://www.cveforecast.org).

*Data collected and analyzed on {current_date}.*
"""

    return blog


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 60)
    print(f"{PERIOD_TITLE} CVE Data Review - Blog Generator")
    print("=" * 60)

    # Optional forecast scorecard input (written by 08_forecast_scorecard.py)
    forecast = None
    forecast_path = OUTPUT_DIR / "forecast.json"
    if forecast_path.exists():
        with open(forecast_path) as f:
            forecast = json.load(f)
        print(f"  ✓ Loaded forecast: {forecast.get('full_year_forecast')}")

    # Optional KEV input (written by 09_kev_analysis.py)
    kev = None
    kev_path = OUTPUT_DIR / "kev.json"
    if kev_path.exists():
        with open(kev_path) as f:
            kev = json.load(f)
        print(f"  ✓ Loaded KEV: {kev.get('h1_published_in_kev')} H1 CVEs already exploited")

    # Load data (returns both filtered and full datasets)
    nvd_df, cvelist_df, full_nvd_df, full_cvelist_df = load_data()

    if nvd_df is None and cvelist_df is None:
        print("\nERROR: No data found. Run these scripts first:")
        print("  1. python 01_download_data.py")
        print("  2. python 02_process_data.py")
        return

    # NORMALIZE DATA - Clean and deduplicate before analysis
    nvd_df = normalize_data(nvd_df)
    cvelist_df = normalize_data(cvelist_df)

    # Use NVD as primary, CVE List V5 as secondary
    df = nvd_df if nvd_df is not None else cvelist_df
    full_df = full_nvd_df if full_nvd_df is not None else full_cvelist_df

    if df is None:
        print("\nERROR: No valid data loaded.")
        return

    print(f"\nUsing primary dataset: {len(df):,} active CVEs (excluded rejected)")

    # Calculate statistics
    print("\nCalculating statistics...")
    stats = calculate_stats(df, cvelist_df, full_nvd_df, full_cvelist_df)

    # Sanity check: warn when a top product/vendor is dominated by one outside CNA
    # (the OpenClaw/VulnCheck pattern) so an inflated callout never ships silently.
    concentration = cna_concentration(cvelist_df, stats["asof"])
    if concentration:
        with open(OUTPUT_DIR / "cna_concentration.json", "w") as f:
            json.dump(concentration, f, indent=2)

    # Generate all graphs using imported functions from 03_generate_graphs.py
    print("\nGenerating graphs...")

    # First-Half CVEs by Year - returns (fig, h1_yearly) for the YoY chart
    asof = current_asof(df)
    _, h1_yearly = graph_cves_by_year(
        df, asof, save_path=GRAPHS_DIR / "01_cves_by_year.png"
    )

    # First-Half YoY Growth (derived from the H1 series)
    graph_yoy_growth(h1_yearly, save_path=GRAPHS_DIR / "02_yoy_growth.png")

    # Cumulative Growth uses the TRUE full-year totals (all-time catalog size)
    yearly_full = df.groupby("year").size().reset_index(name="count")
    yearly_full = yearly_full[
        (yearly_full["year"] >= HIST_MIN_YEAR) & (yearly_full["year"] <= TARGET_YEAR)
    ]
    _, cumulative_total = graph_cumulative_growth(
        yearly_full, save_path=GRAPHS_DIR / "03_cumulative_growth.png"
    )

    # H1 Monthly - returns (fig, peak_month, peak_count)
    _, peak_month, peak_count = graph_period_monthly(
        df, save_path=GRAPHS_DIR / "04_h1_monthly.png"
    )

    # CVSS Distribution
    graph_cvss_distribution(df, save_path=GRAPHS_DIR / "05_cvss_distribution.png")

    # Severity Breakdown
    graph_severity_breakdown(df, save_path=GRAPHS_DIR / "06_severity_breakdown.png")

    # Top CWEs - returns (fig, top_cwes_list)
    _, top_cwes = graph_top_cwes(df, save_path=GRAPHS_DIR / "07_top_cwes.png")
    if top_cwes is None:
        top_cwes = []

    # Data Quality
    graph_data_quality(df, save_path=GRAPHS_DIR / "09_data_quality.png")

    # CVSS by Year
    graph_cvss_by_year(df, save_path=GRAPHS_DIR / "13_cvss_by_year.png")

    # Rejected CVE analysis (uses full dataset) - returns (fig, rejected_stats)
    rejected_stats = None
    if full_df is not None:
        result = graph_rejected_cves(
            full_df, save_path=GRAPHS_DIR / "10_rejected_cves.png"
        )
        if result is not None:
            _, rejected_stats = result

    # CVE List V5 specific graphs
    cna_df = cvelist_df if cvelist_df is not None else df

    # Top CNAs - returns (fig, top_cnas_list)
    _, top_cnas = graph_top_cnas(cna_df, save_path=GRAPHS_DIR / "08_top_cnas.png")
    if top_cnas is None:
        top_cnas = []

    # Top Vendors - returns (fig, top_vendors_list)
    _, top_vendors = graph_top_vendors(
        cna_df, save_path=GRAPHS_DIR / "14_top_vendors.png"
    )
    if top_vendors is None:
        top_vendors = []

    # Day of Week Analysis - returns (fig, day_stats_dict)
    _, day_stats = graph_day_of_week(df, save_path=GRAPHS_DIR / "16_day_of_week.png")

    # Top Days Analysis - returns (fig, top_days_list)
    _, top_days = graph_top_days(df, save_path=GRAPHS_DIR / "17_top_days.png")
    if top_days is None:
        top_days = []

    # Top Products Analysis - returns (fig, top_products_list)
    _, top_products = graph_top_products(
        df, save_path=GRAPHS_DIR / "18_top_products.png"
    )
    if top_products is None:
        top_products = []

    # Social scorecard (shareable launch image)
    proj_lo = min(stats["projected_runrate"], stats["projected_seasonal"])
    proj_hi = max(stats["projected_runrate"], stats["projected_seasonal"])
    kev_txt = (
        f"{kev['h1_published_in_kev']}"
        if kev and kev.get("h1_published_in_kev") is not None
        else "n/a"
    )
    scorecard_tiles = [
        (f"{stats['total_2025']:,}", "CVEs in H1 2026", True),
        (f"{stats['cves_per_day']:.0f}/day", f"1 every {stats['minutes_between']:.0f} min", False),
        (f"+{stats['yoy_change']:.0f}%", f"vs H1 {PRIOR_YEAR} (same window)", False),
        (kev_txt, "known-exploited (CISA KEV)", True),
        (f"{round(proj_lo / 1000)}-{round(proj_hi / 1000)}K", "projected full year", False),
        (str(stats.get("top_cna", "n/a")).split("_")[0], "top CVE issuer", False),
    ]
    graph_scorecard(
        scorecard_tiles,
        "2026 First Half CVE Data: Mid-Year Scorecard",
        subtitle=f"January 1 - {stats['asof_label']}, 2026",
        save_path=GRAPHS_DIR / "00_scorecard.png",
    )

    # Generate blog
    print("\nGenerating blog.md...")
    blog_content = generate_blog(
        stats,
        top_cwes,
        top_cnas,
        top_vendors,
        peak_month,
        peak_count,
        cumulative_total,
        rejected_stats,
        day_stats,
        top_days,
        top_products,
        forecast,
        kev,
    )

    with open("blog.md", "w") as f:
        f.write(blog_content)

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print("\n✓ Blog saved to: blog.md")
    print(f"✓ Graphs saved to: {GRAPHS_DIR}/")
    print(f"\nGenerated {len(list(GRAPHS_DIR.glob('*.png')))} graphs")
    print("\nYou can now publish blog.md!")


if __name__ == "__main__":
    main()
