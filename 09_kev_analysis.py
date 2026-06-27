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


def fetch_kev():
    last = None
    for url in KEV_URLS:
        try:
            print(f"Fetching CISA KEV from {url} ...")
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:  # noqa: BLE001
            print(f"  could not fetch {url}: {e}")
            last = e
    raise SystemExit(f"Unable to fetch CISA KEV: {last}")


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
    kev_df = pd.DataFrame(vulns)
    kev_df["dateAdded"] = pd.to_datetime(
        kev_df["dateAdded"], utc=True, errors="coerce"
    )

    # KEV entries newly catalogued during H1 2026 vs the same window in 2025.
    added_h1 = kev_df[half1_mask(kev_df.assign(published=kev_df["dateAdded"]), TARGET_YEAR)]
    added_h1_prior = kev_df[
        half1_mask(kev_df.assign(published=kev_df["dateAdded"]), PRIOR_YEAR)
    ]

    # How many CVEs *published* in H1 2026 are already known-exploited.
    h1_ids = load_h1_cve_ids()
    kev_ids = set(kev_df["cveID"])
    h1_in_kev = sorted(h1_ids & kev_ids)

    ransomware_h1 = added_h1[
        added_h1.get("knownRansomwareCampaignUse", pd.Series(dtype=str)) == "Known"
    ]

    # Notable examples: H1-2026-published CVEs that are already in KEV.
    examples = []
    if h1_in_kev:
        ex_df = kev_df[kev_df["cveID"].isin(h1_in_kev)].sort_values("dateAdded")
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
                    "ransomware": row.get("knownRansomwareCampaignUse") == "Known",
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
