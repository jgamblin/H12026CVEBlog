#!/bin/bash
#
# 2026 First Half CVE Data Review - Full Pipeline
# Runs all scripts in sequence to generate the complete blog
#

set -e  # Exit on any error

echo "============================================================"
echo "2026 First Half CVE Data Review - Full Pipeline"
echo "============================================================"
echo ""

# Check for required environment variable
if [ -z "$GEMINI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: No GEMINI_API_KEY or GOOGLE_API_KEY set"
    echo "   AI enrichment (step 7) will be skipped"
    echo ""
fi

# Step 1: Download Data
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1/6] Downloading CVE Data..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 01_download_data.py
echo ""

# Step 2: Process Data
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[2/6] Processing CVE Data..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 02_process_data.py
echo ""

# Step 3: Generate Graphs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[3/6] Generating Graphs..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 03_generate_graphs.py
echo ""

# Step 4: Fetch Forecast Scorecard (CVEForecast) - optional, non-fatal
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[4/7] Fetching CVEForecast Scorecard..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 08_forecast_scorecard.py || echo "  (forecast fetch failed - blog will render a placeholder)"
echo ""

# Step 5: KEV (known-exploited) analysis - optional, non-fatal
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[5/7] Analyzing CISA KEV (known-exploited)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 09_kev_analysis.py || echo "  (KEV fetch failed - blog will skip the KEV section)"
echo ""

# Step 6: Generate Blog
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[6/7] Generating Blog..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python3 04_generate_blog.py
echo ""

# Step 7: Enrich with AI (optional - requires API key)
if [ -n "$GEMINI_API_KEY" ] || [ -n "$GOOGLE_API_KEY" ]; then
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[7/7] Enriching Blog with AI..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    python3 05_enrich_blog.py
    echo ""
else
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "[7/7] Skipping AI Enrichment (no API key)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# Summary
echo "============================================================"
echo "✅ PIPELINE COMPLETE!"
echo "============================================================"
echo ""
echo "Generated files:"
echo "  📄 blog.md           - Main blog post"
if [ -f "blog_enriched.md" ]; then
    echo "  📄 blog_enriched.md  - AI-enhanced version"
fi
echo "  📊 graphs/           - All visualizations"
echo ""
echo "Graph count: $(ls -1 graphs/*.png 2>/dev/null | wc -l | tr -d ' ') images"
echo ""
