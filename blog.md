# 2026 First Half CVE Data Review

<!-- Featured image suggestion: graphs/00_scorecard.png (mid-year stat card) or graphs/01_cves_by_year.png (2026 towers over every prior H1) -->

We are halfway through 2026, so it is time for the mid-year CVE check-in. The short version: the volume curve has gone vertical while exploitation has not. This review covers everything published in the first half of 2026 (Jan 1 - Jun 30, 2026), the volume, the severity, what is actually being exploited, and who is driving the numbers, all measured against the same elapsed window a year ago so a partial half is never compared to a full one.

## TL;DR

**The first half of 2026 produced 34,601 CVEs, more in six months than any full year before 2024 (all of 2023 finished at 28,817).** That works out to one new CVE every **7.4 minutes**, an increase of **48.8%** over the same window in 2025 (23,252). And yet only **84 of them, 0.24%, are known to be exploited.** That gap is the story of 2026 so far: we are minting CVEs faster than ever while real-world exploitation stays flat, so the hard problem is signal-to-noise, not patch volume.

At this pace the year projects to roughly **71,352 to 72,046**, and the all-time catalog has now passed **343,497 CVEs** since 1999. Numbers run through Jun 26; the window closes June 30, so treat them as a floor.

> **Note**: All statistics in this report exclude rejected CVEs to provide an accurate count of active vulnerabilities.

### Key Statistics at a Glance

| Metric | Value |
|--------|-------|
| **Total CVEs (H1 2026)** | **34,601** |
| CVEs per Day | 195.5 |
| Change vs same window 2025 | +48.8% |
| Projected Full Year | 71,352 - 72,046 |
| Critical Severity | 3,446 |
| High Severity | 13,378 |
| Average CVSS Score | 6.88 |
| CVSS Coverage | 93.4% |
| CWE Coverage | 95.3% |
| Active CNAs | 338 |
| Rejected CVEs (H1 2026) | 1,258 |
| Already Known-Exploited (KEV) | 84 |

---

## H1-over-H1: Three Years Side by Side

To keep the comparison honest while 2026 is still in progress, each year is measured over the identical window (January 1 through Jun 26).

| Window | CVEs | Per Day | Avg CVSS |
|--------|------|---------|----------|
| Jan 1 - Jun 26, 2024 | 20,137 | 113.8 | 6.65 |
| Jan 1 - Jun 26, 2025 | 23,252 | 131.4 | 6.57 |
| Jan 1 - Jun 26, 2026 *(partial)* | 34,601 | 195.5 | 6.88 |

---

## Forecast Scorecard: Are We On Pace?

At **195.5 CVEs/day**, two independent methods converge on the full-year number: the run-rate extrapolates to **71,352**, and a seasonality-adjusted estimate (using 2025's 49% first-half share) to **72,046**.

[CVEForecast](https://www.cveforecast.org) projects **82,878 CVEs** for full-year 2026 (LinearRegression, MAPE 14.35). That is **10,832 above** the top of the straight-line range, and here is where I will plant a flag: **I think the model is high.** Two independent methods both land near 72,046, and the forecast's entire gap to them rests on a heavy second-half surge that still has to show up. **My call is the year closes nearer 72,046 than 82,878.** I will happily eat those words in the December review if H2 accelerates the way the model expects, but the burden of proof is on the surge.

---

## What Changed in H1 2026

**GitHub_M** is the busiest CNA at **6,730** assignments. New to the most-affected product list this year: **Chrome, OpenClaw**. Among weakness types, [CWE-862](https://cwe.mitre.org/data/definitions/862.html) (Missing Authorization) climbed to #2 in the top five.

**Spotlight: OpenClaw.** The standout newcomer is OpenClaw, Peter Steinberger's viral local AI agent and one of the fastest-growing open-source projects of the cycle (he told the story on [Lex Fridman Podcast #491](https://lexfridman.com/peter-steinberger/), which includes a segment on its security). A project that barely existed a year ago is already among the most-reported products of the half. What stands out is the response: instead of quietly patching, the OpenClaw project embraced the CVE lifecycle and began issuing CVEs for its advisories as the reports came in, a textbook case of a fast-moving open-source project adopting coordinated disclosure under pressure. I track it at [OpenClawCVEs](https://github.com/jgamblin/OpenClawCVEs).

---

## Historical CVE Growth

To compare like with like, this chart counts only the first half of every year (January 1 through Jun 26). On that basis 2026 already stands taller than any prior first half: more CVEs in six months than the same window has ever produced.

![First-Half CVEs by Year](graphs/01_cves_by_year.png)

First-half growth has been relentless, and 2026 is **+48.8%** on the first half of 2025.

![First-Half Year-over-Year Growth](graphs/02_yoy_growth.png)

Counting full years, the cumulative catalog has now passed **343,497 CVEs**.

![Cumulative Growth](graphs/03_cumulative_growth.png)

---

## Monthly Distribution (H1 2026)

CVE publications varied across the first half of 2026, with **May** being the peak month at **6,939 CVEs**.

![Monthly Distribution](graphs/04_h1_monthly.png)

---

## Publication Patterns by Day of Week

Publishing clusters midweek. **Wednesday** is the busiest day at **7,943 CVEs**, with Tuesday close behind at **7,081**. Patch Tuesday is part of the story, but the midweek bulge owes as much to the high-volume CNAs (GitHub, Linux, the WordPress plugin crowd) that batch-publish midweek.

![CVEs by Day of Week](graphs/16_day_of_week.png)

Weekdays average **6,379** CVEs against just **1,352** on weekends.

---

## Busiest Days of H1 2026

Some days saw massive spikes in CVE publications:

![Top Days](graphs/17_top_days.png)

### Top 5 Busiest Days

| Rank | Date | CVE Count |
|------|------|----------|
| 1 | 2026-06-09 | 747 |
| 2 | 2026-06-17 | 732 |
| 3 | 2026-05-27 | 716 |
| 4 | 2026-03-25 | 606 |
| 5 | 2026-05-12 | 554 |

---

## CVSS Score Analysis

The Common Vulnerability Scoring System (CVSS) helps standardize severity assessments. Here's how H1 2026 CVEs were distributed across the scoring range.

![CVSS Distribution](graphs/05_cvss_distribution.png)

The **average CVSS score for H1 2026 was 6.88**, with a **median of 7.10**.

### Severity Breakdown

| Severity | Count | Percentage |
|----------|-------|------------|
| Critical | 3,446 | 10.0% |
| High | 13,378 | 38.7% |
| Medium | 14,162 | 40.9% |
| Low | 2,974 | 8.6% |

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
| 1 | [CWE-79](https://cwe.mitre.org/data/definitions/79.html) | XSS | 3,710 |
| 2 | [CWE-862](https://cwe.mitre.org/data/definitions/862.html) | Missing Authorization | 1,639 |
| 3 | [CWE-89](https://cwe.mitre.org/data/definitions/89.html) | SQL Injection | 1,404 |
| 4 | [CWE-22](https://cwe.mitre.org/data/definitions/22.html) | Path Traversal | 1,224 |
| 5 | [CWE-416](https://cwe.mitre.org/data/definitions/416.html) | Use After Free | 1,010 |

---

## CVE Numbering Authorities (CNAs)

The CNA mix keeps tilting toward platform security teams and third-party aggregators rather than the original product vendors. The most active assigners this year:

![Top CNAs](graphs/08_top_cnas.png)

### Top 5 CNAs in H1 2026

| Rank | CNA | CVEs Assigned |
|------|-----|---------------|
| 1 | GitHub_M | 6,730 |
| 2 | VulDB | 3,218 |
| 3 | VulnCheck | 3,162 |
| 4 | Patchstack | 2,685 |
| 5 | Linux | 2,516 |

In total, **338 unique CNAs** assigned CVEs in H1 2026.

---

## Top Vendors

The vendors with the most CVEs attributed to their products this year (each links to its NVD search):

![Top Vendors](graphs/14_top_vendors.png)

### Top 5 Vendors in H1 2026

| Rank | Vendor | CVE Count |
|------|--------|-----------|
| 1 | [Linux](https://nvd.nist.gov/vuln/search/results?form_type=Advanced&results_type=overview&search_type=all&isCpeNameSearch=false&cpe_vendor=linux) | 2,516 |
| 2 | [Google](https://nvd.nist.gov/vuln/search/results?form_type=Advanced&results_type=overview&search_type=all&isCpeNameSearch=false&cpe_vendor=google) | 1,418 |
| 3 | [Microsoft](https://nvd.nist.gov/vuln/search/results?form_type=Advanced&results_type=overview&search_type=all&isCpeNameSearch=false&cpe_vendor=microsoft) | 863 |
| 4 | [OpenClaw](https://nvd.nist.gov/vuln/search/results?form_type=Advanced&results_type=overview&search_type=all&isCpeNameSearch=false&cpe_vendor=openclaw) | 537 |
| 5 | [Oracle Corporation](https://nvd.nist.gov/vuln/search/results?form_type=Advanced&results_type=overview&search_type=all&isCpeNameSearch=false&cpe_vendor=oracle+corporation) | 445 |

---

## Most Vulnerable Products

Drilling past vendors to specific products, the H1 2026 leaders:

![Top Products](graphs/18_top_products.png)

### Top 5 Products

| Rank | Product | CVE Count |
|------|---------|----------|
| 1 | Linux Kernel | 1,915 |
| 2 | Chrome | 1,200 |
| 3 | OpenClaw | 534 |
| 4 | Windows 10 | 372 |
| 5 | Android | 303 |

---

## Known-Exploited Vulnerabilities (CISA KEV)

Volume is the headline, but exploitation is what should actually drive patching. Of the **34,601** CVEs published in H1 2026, only **84** (0.24%) have shown up in the [CISA KEV catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) so far. That gap is the prioritization signal: the overwhelming majority of CVEs are not known to be exploited, so triaging on exploitability beats chasing raw counts.

CISA added **145** entries to KEV during the first half (more than the **132** added in the same window of 2025), and **16** of those are tied to known ransomware campaigns.

### H1 2026 CVEs Already in KEV

| CVE | Vendor | Product | Added | Ransomware |
|-----|--------|---------|-------|------------|
| CVE-2026-20805 | Microsoft | Windows | 2026-01-13 |  |
| CVE-2026-20045 | Cisco | Unified Communications Manager | 2026-01-21 |  |
| CVE-2026-24061 | Gnu | InetUtils | 2026-01-26 |  |
| CVE-2026-21509 | Microsoft | Office | 2026-01-26 |  |
| CVE-2026-23760 | Smartertools | SmarterMail | 2026-01-26 | Yes |

---

## Data Quality

Not all CVEs have complete metadata. Here's how data quality has evolved over the years:

![Data Quality](graphs/09_data_quality.png)

### H1 2026 Data Quality Metrics

| Metric | Coverage |
|--------|----------|
| CVSS Score | 93.4% |
| CWE Classification | 95.3% |
| CPE Identifiers | 58.5% |

---

## Rejected CVEs

Not all CVE IDs stay active. Some are rejected for duplicates, disputes, or invalid submissions, and the rejection rate is a useful read on the ecosystem's quality control.

![Rejected CVEs](graphs/10_rejected_cves.png)

### H1 2026 Rejection Statistics

| Metric | Value |
|--------|-------|
| Rejected CVEs in H1 2026 | 1,258 |
| H1 2026 Rejection Rate | 3.51% |
| Total Rejected (All Time) | 17,639 |

CVE rejections occur for several reasons:
- **Duplicates**: The same vulnerability assigned multiple CVE IDs
- **Disputes**: Vendor disagreement that the issue is a vulnerability
- **Invalid**: Not a security vulnerability or insufficient information
- **Withdrawn**: CVE withdrawn by the assigning CNA

---

## Conclusions

### Key Takeaways from the First Half of 2026

1. **Volume keeps climbing**: 34,601 CVEs in roughly six months, up 48.8% on the same window last year, with the full year projecting to 71,352-72,046.

2. **Severity stays heavy**: 16,824 CVEs (48.6%) are Critical or High.

3. **Web and access-control flaws lead**: XSS, Missing Authorization, SQL Injection, Path Traversal headline the CWE list. Memory-safety issues barely register in the top tier this half.

4. **The CNA mix is shifting**: platform teams and aggregators, not the original vendors, now top the assigner list, and the lineup reshuffled from a year ago.

5. **Coverage gaps persist**: CVSS and CWE are well covered, but CPE sits at 58.5%, which still hampers automated matching.

6. **Exploitation stays rare**: just 84 of 34,601 H1 CVEs (0.24%) are in CISA KEV. Volume is a triage problem, not a patch-everything problem.

### What this means for you

- **If you defend a network:** ignore the headline count. With only **0.24%** of H1 CVEs known-exploited, exploitability is your filter, not volume. Wire CISA KEV and EPSS into triage and let the long tail wait.
- **If you run a CNA:** the center of gravity has shifted to platforms and aggregators. Throughput and data quality, CPE coverage especially, are the differentiators now.
- **If you consume NVD data:** enrichment is the bottleneck. CPE at 58.5% means nearly half of new CVEs cannot be auto-matched to a product, and volume only widens that gap.

### What I'm watching in H2

My call from the scorecard stands: 2026 closes nearer **72,046** than the **82,878** forecast. Two things would change my mind: a December disclosure surge bigger than 2025's, or another OpenClaw-style project flooding the catalog. The year-end review settles it.

---

## Methodology and Reproducibility

Two primary data sources, plus two enrichment feeds:

1. **NVD JSON** - National Vulnerability Database export from [nvd.handsonhacking.org](https://nvd.handsonhacking.org/nvd.json)
2. **CVE List V5** - Official CVE records from [CVEProject/cvelistV5](https://github.com/CVEProject/cvelistV5)
3. **Forecast** - [CVEForecast](https://www.cveforecast.org) full-year projection
4. **Exploitation** - [CISA KEV catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)

Everything here is reproducible. The full pipeline (Python, pandas, matplotlib) is on GitHub at [jgamblin/H12026CVEBlog](https://github.com/jgamblin/H12026CVEBlog), and it leans on the free CVE tooling I build at [RogoLabs](https://rogolabs.net): [cve.icu](https://cve.icu), [cnascorecard.org](https://cnascorecard.org), and [cveforecast.org](https://www.cveforecast.org).

*Data collected and analyzed on June 27, 2026.*
