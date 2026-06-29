#!/usr/bin/env python3
"""
WordPress export for the 2026 First Half CVE Data Review.

Turns the generated ``blog.md`` into a Gutenberg-ready ``blog_wordpress.html`` that
pastes cleanly into the WordPress block editor's *Code editor* (Options menu, or
Cmd/Ctrl+Shift+Alt+M), then switch back to Visual. This removes the two things that
break a naive copy-paste of the Markdown:

1. Raw Markdown does not render in Gutenberg (you would publish literal ``**``, ``#``
   and ``|`` characters). We convert to HTML so headings, the blockquote, links, and
   all the pipe tables land as real blocks.
2. The in-body H1 and the featured-image HTML comment are stripped (WordPress renders
   the post Title as the page's only H1; a second one is an SEO/accessibility defect).

It also enriches chart alt text (data-forward, better for SEO/accessibility) and prints
a publish checklist: title, slug, meta description, and the ordered image-upload list.

Images: by default the ``graphs/<file>.png`` paths are left as-is (they must be uploaded
to the Media Library and re-pointed in WordPress). Pass ``--media-base-url`` to rewrite
them to a predictable uploads URL if you upload with the original filenames, e.g.::

    python3 10_wordpress_export.py --media-base-url https://jerrygamblin.com/wp-content/uploads/2026/07

Requires pandoc (https://pandoc.org). On macOS: ``brew install pandoc``.
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from period_config import PERIOD_TITLE, PERIOD_RANGE

INPUT_FILE = Path("blog.md")
OUTPUT_FILE = Path("blog_wordpress.html")

POST_TITLE = f"{PERIOD_TITLE} CVE Data Review"
POST_SLUG = "2026-first-half-cve-data-review"
META_DESCRIPTION = (
    "H1 2026 produced 34,601 CVEs, up nearly 49% YoY, yet only 0.24% are known-exploited. "
    "The mid-year data review on volume, severity, and what's actually exploited."
)

# Data-forward alt text by image filename (better for SEO/accessibility than the bare
# chart title). Kept free of specific figures so it stays correct across re-runs.
ALT_TEXT = {
    "00_scorecard.png": "Mid-year scorecard card summarizing the headline H1 2026 CVE statistics",
    "01_cves_by_year.png": "Bar chart of first-half CVE counts by year, with 2026 the tallest on record",
    "02_yoy_growth.png": "Year-over-year growth in first-half CVE counts",
    "03_cumulative_growth.png": "Cumulative all-time CVE catalog growth since 1999",
    "04_h1_monthly.png": "Monthly distribution of CVEs published across the first half of 2026",
    "05_cvss_distribution.png": "Distribution of H1 2026 CVEs across the CVSS score range",
    "06_severity_breakdown.png": "H1 2026 CVE severity breakdown across Critical, High, Medium, and Low",
    "07_top_cwes.png": "Most common weakness types (CWE) among H1 2026 CVEs",
    "08_top_cnas.png": "Most active CVE Numbering Authorities in H1 2026",
    "09_data_quality.png": "CVE metadata completeness (CVSS, CWE, CPE coverage) over time",
    "10_rejected_cves.png": "Rejected CVE counts and rejection rate by year",
    "13_cvss_by_year.png": "Average and median CVSS score trend by year",
    "14_top_vendors.png": "Vendors with the most CVEs attributed in H1 2026",
    "16_day_of_week.png": "CVE publication volume by day of week, peaking midweek",
    "17_top_days.png": "Busiest single days for CVE publication in H1 2026",
    "18_top_products.png": "Products with the most CVEs in H1 2026",
}


def strip_for_wordpress(md: str) -> str:
    """Remove the in-body H1 and HTML comments so WordPress owns the page H1."""
    # Drop HTML comments (e.g. the featured-image suggestion on line 3).
    md = re.sub(r"<!--.*?-->", "", md, flags=re.DOTALL)
    # Drop the first top-level H1 only (the post title; WP renders it from the Title).
    lines = md.splitlines()
    out, dropped_h1 = [], False
    for line in lines:
        if not dropped_h1 and line.startswith("# "):
            dropped_h1 = True
            continue
        out.append(line)
    return "\n".join(out).strip() + "\n"


def enrich_alt_text(md: str) -> str:
    """Replace each image's alt text with a data-forward description by filename."""

    def repl(m):
        src = m.group(2)
        name = src.rsplit("/", 1)[-1]
        alt = ALT_TEXT.get(name, m.group(1))
        return f"![{alt}]({src})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", repl, md)


def rewrite_image_paths(md: str, base_url: str) -> str:
    """Re-point ``graphs/<file>`` image sources at an uploads base URL."""
    base = base_url.rstrip("/")
    return re.sub(
        r"(!\[[^\]]*\]\()graphs/([^)]+)(\))",
        lambda m: f"{m.group(1)}{base}/{m.group(2)}{m.group(3)}",
        md,
    )


def list_images(md: str):
    return sorted(set(re.findall(r"!\[[^\]]*\]\((?:.*?/)?([^)/]+\.png)\)", md)))


def to_html(md: str) -> str:
    if not shutil.which("pandoc"):
        sys.exit(
            "ERROR: pandoc not found. Install it (macOS: brew install pandoc) and re-run."
        )
    # gfm keeps the pipe tables; no '+smart' so ASCII hyphens are not turned into
    # en/em dashes (house style bans em dashes).
    proc = subprocess.run(
        ["pandoc", "--from", "gfm", "--to", "html", "--wrap=none"],
        input=md,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        sys.exit(f"ERROR: pandoc failed: {proc.stderr}")
    return proc.stdout


def main():
    parser = argparse.ArgumentParser(description="Export blog.md to WordPress-ready HTML")
    parser.add_argument(
        "--media-base-url",
        help="If set, rewrite graphs/*.png image src to <base>/<file> "
        "(only safe if you upload with the original filenames).",
    )
    args = parser.parse_args()

    if not INPUT_FILE.exists():
        sys.exit(f"ERROR: {INPUT_FILE} not found. Run 04_generate_blog.py first.")

    md = INPUT_FILE.read_text()
    images = list_images(md)

    md = strip_for_wordpress(md)
    md = enrich_alt_text(md)
    if args.media_base_url:
        md = rewrite_image_paths(md, args.media_base_url)

    OUTPUT_FILE.write_text(to_html(md))

    print("=" * 60)
    print("WordPress export complete")
    print("=" * 60)
    print(f"\n  Wrote {OUTPUT_FILE} (paste into the Gutenberg *Code editor*, then switch to Visual)\n")
    print(f"  Post Title : {POST_TITLE}")
    print(f"  Slug       : {POST_SLUG}")
    print(f"  Window     : {PERIOD_RANGE}")
    print(f"  Meta desc  : {META_DESCRIPTION}\n")
    if args.media_base_url:
        print(f"  Image src rewritten to: {args.media_base_url.rstrip('/')}/<file>\n")
    else:
        print("  Images: paths left as graphs/<file>. Upload these to the Media Library")
        print("  and re-point each (or re-run with --media-base-url):")
    print("  Featured image (set in Document panel, not body): 00_scorecard.png")
    for img in images:
        print(f"    - {img}")
    print("\n  Then: confirm one H1 (the title), no literal ** / # / |, no broken images.")


if __name__ == "__main__":
    main()
