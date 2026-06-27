# 2026 First Half CVE Data Review

[![CI](https://github.com/jgamblin/H12026CVEBlog/actions/workflows/ci.yml/badge.svg)](https://github.com/jgamblin/H12026CVEBlog/actions/workflows/ci.yml)

Mid-year review of CVE (Common Vulnerabilities and Exposures) data for the first
half of 2026 (Jan 1 - Jun 30). This project downloads, processes, and visualizes
CVE data from multiple authoritative sources to produce a publication-ready blog
post with professional graphs.

It is a re-scope of the annual [2025CVEBlog](https://github.com/jgamblin/2025CVEBlog)
pipeline to a half-year date window, with two mid-year additions:

- **A real date window** instead of a year equality. All "current period" filters
  route through `period_config.py` (Jan 1 - Jun 30, 2026).
- **A Forecast Scorecard.** `08_forecast_scorecard.py` pulls the published
  [CVEForecast](https://www.cveforecast.org) feed so the post can grade H1 actuals
  against the full-year projection.
- **A Known-Exploited (KEV) section.** `09_kev_analysis.py` cross-references the
  CISA KEV catalog against the H1 CVE set, so the post leads with exploitation, not
  just volume.
- **Apples-to-apples comparisons.** Every year-over-year figure uses the same
  *elapsed* window (Jan 1 through the as-of date), so a partial half is never measured
  against a full one. The current year is shown as a partial bar and excluded from the
  year-over-year chart.

## Data Sources

1. **NVD JSON** - National Vulnerability Database export from https://nvd.handsonhacking.org/nvd.json
2. **CVE List V5** - Official CVE records from https://github.com/CVEProject/cvelistV5
3. **CVEForecast** - Full-year projection feed from https://www.cveforecast.org
4. **CISA KEV** - Known Exploited Vulnerabilities catalog from https://www.cisa.gov/known-exploited-vulnerabilities-catalog

## Requirements

- Python 3.11+
- Dependencies listed in `requirements.txt`
- (Optional) `GEMINI_API_KEY` or `GOOGLE_API_KEY` for AI blog enrichment

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the full pipeline (download, process, graph, forecast, blog, enrich)
./run_all.sh

# Or run individual steps:
python 01_download_data.py        # Download data (~1GB+ NVD JSON)
python 02_process_data.py         # Parse into analysis-ready DataFrames
python 03_generate_graphs.py      # Generate visualizations (standalone)
python 08_forecast_scorecard.py   # Fetch CVEForecast -> processed/forecast.json
python 09_kev_analysis.py         # Cross-reference CISA KEV -> processed/kev.json
python 04_generate_blog.py        # Generate blog.md with all graphs + scorecard + KEV
python 05_enrich_blog.py          # AI-enhanced blog (requires API key)
```

## Reporting Period

The reporting window is configured in one place, `period_config.py`:

| Setting | Value |
|---------|-------|
| Window | Jan 1 - Jun 30, 2026 |
| Prior comparison | Jan 1 - Jun 30, 2025 (H1-over-H1) |
| Historical charts | 1999 - 2026 (2026 = partial) |

To re-target a future period, edit `period_config.py` only.

## Output

- `blog.md` - the generated post
- `blog_enriched.md` - AI-enhanced version (if an API key is set)
- `graphs/` - all PNG charts and animated GIFs referenced by the post
- `processed/forecast.json` - the CVEForecast scorecard input (regenerated, gitignored)

## RogoLabs

This review is built on free CVE tooling from [RogoLabs](https://rogolabs.net):
[cve.icu](https://cve.icu), [cnascorecard.org](https://cnascorecard.org), and
[cveforecast.org](https://www.cveforecast.org).
