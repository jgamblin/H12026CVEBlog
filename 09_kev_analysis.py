#!/usr/bin/env python3
"""
Known-Exploited (CISA KEV) analysis for the 2026 First Half CVE Data Review.

Mid-year readers care most about what is actually being exploited, not just raw
volume. This step downloads the CISA KEV catalog and cross-references it against
the H1 2026 CVE set (from processed/), then writes processed/kev.json for the
blog's "Known-Exploited Vulnerabilities" section.

Runs after 02_process_data.py (needs processed/nvd_cves.parquet). The blog step
renders a placeholder if this file is absent, so it is optional but recommended.
"""

import json
import time
from pathlib import Path

import pandas as pd
import requests

from period_config import period_mask, half1_mask, PERIOD_LABEL, PRIOR_YEAR, TARGET_YEAR

OUTPUT_DIR = Path("processed")
OUTPUT_DIR.mkdir(exist_ok=True)

KEV_URLS = [
    "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
    "https://raw.githubusercontent.com/cisagov/kev-data/main/known_exploited_vulnerabilities.json",
]


def fetch_kev(retries=3):
    """Fetch the CISA KEV catalog, retrying each source with backoff."""
    last = None
    for url in KEV_URLS:
        for attempt in range(1, retries + 1):
            try:
                print(f"Fetching CISA KEV from {url} (attempt {attempt}/{retries}) ...")
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                return r.json()
            except Exception as e:  # noqa: BLE001 - report, back off, then retry/fall through
                print(f"  could not fetch {url}: {e}")
                last = e
                if attempt < retries:
                    time.sleep(3 * attempt)
    raise SystemExit(f"Unable to fetch CISA KEV: {last}")


def is_ransomware(value):
    """Normalize the KEV ``knownRansomwareCampaignUse`` field to a bool.

    CISA publishes the string ``"Known"`` today, but tolerate boolean and other
    truthy spellings so a feed format tweak does not silently zero the count.
    """
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("known", "true", "yes")


def load_h1_cve_ids():
    """CVE IDs published in the H1 2026 window (active, non-rejected)."""
    pq = OUTPUT_DIR / "nvd_cves.parquet"
    if not pq.exists():
        return set()
    df = pd.read_parquet(pq)
    if "is_rejected" in df.columns:
        df = df[~df["is_rejected"]]
    return set(df[period_mask(df)]["cve_id"])


def main():
    print("=" * 60)
    print("CISA KEV Analysis - 2026 First Half Review")
    print("=" * 60)

    kev = fetch_kev()
    vulns = kev.get("vulnerabilities", [])
    if not vulns:
        raise SystemExit("CISA KEV response had no 'vulnerabilities' entries; aborting.")
    kev_df = pd.DataFrame(vulns)

    # Validate the schema before relying on it: a renamed/missing field should
    # fail loudly rather than silently produce a zero exploited-count headline.
    for required in ("cveID", "dateAdded"):
        if required not in kev_df.columns:
            raise SystemExit(
                f"CISA KEV schema changed: expected column '{required}' not found. "
                f"Got: {sorted(kev_df.columns)}"
            )

    kev_df["dateAdded"] = pd.to_datetime(
        kev_df["dateAdded"], utc=True, errors="coerce"
    )
    bad_dates = int(kev_df["dateAdded"].isna().sum())
    if bad_dates:
        print(f"  WARNING: {bad_dates} KEV entries have an unparseable dateAdded")

    # KEV entries newly catalogued during H1 2026 vs the same window in 2025.
    added_h1 = kev_df[half1_mask(kev_df.assign(published=kev_df["dateAdded"]), TARGET_YEAR)]
    added_h1_prior = kev_df[
        half1_mask(kev_df.assign(published=kev_df["dateAdded"]), PRIOR_YEAR)
    ]

    # How many CVEs *published* in H1 2026 are already known-exploited.
    h1_ids = load_h1_cve_ids()
    kev_ids = set(kev_df["cveID"])
    h1_in_kev = sorted(h1_ids & kev_ids)

    if "knownRansomwareCampaignUse" in added_h1.columns:
        ransomware_h1 = added_h1[
            added_h1["knownRansomwareCampaignUse"].apply(is_ransomware)
        ]
    else:
        ransomware_h1 = added_h1.iloc[0:0]

    # Notable examples: H1-2026-published CVEs that are already in KEV,
    # most recent additions first (the blog shows the latest few).
    examples = []
    if h1_in_kev:
        ex_df = kev_df[kev_df["cveID"].isin(h1_in_kev)].sort_values(
            "dateAdded", ascending=False
        )
        for _, row in ex_df.head(8).iterrows():
            examples.append(
                {
                    "cve": row["cveID"],
                    "vendor": row.get("vendorProject"),
                    "product": row.get("product"),
                    "name": row.get("vulnerabilityName"),
                    "date_added": str(row["dateAdded"].date())
                    if pd.notna(row["dateAdded"])
                    else None,
                    "ransomware": is_ransomware(row.get("knownRansomwareCampaignUse")),
                }
            )

    out = {
        "source": "CISA KEV",
        "url": "https://www.cisa.gov/known-exploited-vulnerabilities-catalog",
        "catalog_total": len(kev_df),
        "catalog_version": kev.get("catalogVersion"),
        "period_label": PERIOD_LABEL,
        "added_h1": int(len(added_h1)),
        "added_h1_prior": int(len(added_h1_prior)),
        "ransomware_h1": int(len(ransomware_h1)),
        "h1_published_in_kev": len(h1_in_kev),
        "h1_published_total": len(h1_ids),
        "examples": examples,
    }

    with open(OUTPUT_DIR / "kev.json", "w") as f:
        json.dump(out, f, indent=2)

    print(f"\n✓ Wrote {OUTPUT_DIR / 'kev.json'}")
    print(f"  KEV catalog total: {out['catalog_total']:,}")
    print(f"  Added in {PERIOD_LABEL}: {out['added_h1']:,} (vs {out['added_h1_prior']:,} in H1 {PRIOR_YEAR})")
    print(f"  Ransomware-linked additions: {out['ransomware_h1']:,}")
    print(
        f"  H1 2026-published CVEs already in KEV: {out['h1_published_in_kev']:,}"
        f" of {out['h1_published_total']:,}"
    )


if __name__ == "__main__":
    main()
