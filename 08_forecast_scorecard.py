#!/usr/bin/env python3
"""
Forecast Scorecard input for the 2026 First Half CVE Data Review.

Pulls the published CVEForecast feed (cveforecast.org) and writes a small
normalized ``processed/forecast.json`` that 04_generate_blog.py reads to render
the "Are We On Pace?" section. This is the mid-year angle the annual review
can't tell: H1 actuals graded against the full-year forecast.

The blog step runs fine without this file (it prints a TODO placeholder), so
this script is optional but recommended before publishing.
"""

import json
from pathlib import Path

import requests

OUTPUT_DIR = Path("processed")
OUTPUT_DIR.mkdir(exist_ok=True)

# Live site first, then the raw GitHub copy as a fallback.
DATA_URLS = [
    "https://www.cveforecast.org/data.json",
    "https://raw.githubusercontent.com/RogoLabs/CVEForecast/main/web/data.json",
]
SITE_URL = "https://www.cveforecast.org"
TARGET_YEAR = "2026"


def fetch_data():
    """Return the parsed CVEForecast data.json, trying each URL in turn."""
    last_err = None
    for url in DATA_URLS:
        try:
            print(f"Fetching forecast data from {url} ...")
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:  # noqa: BLE001 - report and try the next source
            print(f"  could not fetch {url}: {e}")
            last_err = e
    raise SystemExit(f"Unable to fetch CVEForecast data: {last_err}")


def normalize(data):
    """Extract the handful of fields the blog scorecard needs."""
    totals = data.get("yearly_forecast_totals", {}).get(TARGET_YEAR, {})
    # The ensemble ("all_models") is the headline full-year projection.
    full_year = totals.get("all_models")

    rankings = data.get("model_rankings", [])
    best = rankings[0] if rankings else {}

    summary = data.get("summary", {})

    return {
        "source": "CVEForecast",
        "url": SITE_URL,
        "as_of": data.get("generated_at"),
        "full_year_forecast": full_year,
        "model": best.get("model_name"),
        "model_mape": best.get("mape"),
        "per_model_totals": totals,
        "prior_year_total": summary.get("previous_year_total"),
        "cumulative_actual_2026": summary.get("cumulative_cves_2026"),
    }


def main():
    print("=" * 60)
    print("CVEForecast Scorecard - 2026 First Half Review")
    print("=" * 60)

    data = fetch_data()
    forecast = normalize(data)

    out = OUTPUT_DIR / "forecast.json"
    with open(out, "w") as f:
        json.dump(forecast, f, indent=2)

    print(f"\n✓ Wrote {out}")
    print(f"  Full-year 2026 forecast (ensemble): {forecast['full_year_forecast']:,}")
    print(f"  Best model: {forecast['model']} (MAPE {forecast['model_mape']})")
    print(f"  Prior full year (2025): {forecast['prior_year_total']:,}")
    print(f"  H1 2026 actual (cumulative): {forecast['cumulative_actual_2026']:,}")
    print("\nThe blog step (04_generate_blog.py) will pick this up automatically.")


if __name__ == "__main__":
    main()
