# Launch-Readiness Review: H1 2026 CVE Data Review

Critical pre-launch pass by eight personas (Technical Writer, Technical Editor, CVE
Researcher, CNA Owner, CISO, Vuln Management Professional, Marketing Expert, and an
adversarial "worst critic") on `blog.md` and `CAMPAIGN.md`.

**Verdict: not safe to launch as-is, but nothing fatal.** The data work is sound, the
core arithmetic reconciles across both files, and the thesis is strong. The risks were
in the seams: framing that can be weaponized, a stat that didn't sum to 100%, one
self-contradicting count, and launch hygiene. Most are now fixed; the rest are your
calls or require the July 1 final run.

Status legend: ✅ fixed in code (`04_generate_blog.py` / `style_config.py`, applies on
next pipeline run) · ✅📣 fixed in `CAMPAIGN.md` · ⚖️ your editorial call · 🔎 verify
before posting · 🗓️ resolves on the July 1 re-run.

---

## 🔴 Launch-blockers (consensus across 3+ personas)

1. **KEV "0.24% / exploitation flat / let the long tail wait" chain** (CISO, Vuln Mgmt, CVE Researcher, Marketing, Tech Writer)
   - ✅ `0.24%` now framed as a *lagging floor* (KEV lags disclosure, US-gov scope, rises as the cohort ages) in the TL;DR, KEV section, and conclusion; EPSS named as the forward-looking complement.
   - ✅📣 "exploitation stays flat" → "confirmed exploitation stays **rare**" everywhere (it isn't flat: KEV additions rose 145 vs 132).
   - ✅ Defender advice rewritten: KEV = floor not verdict, weight by asset exposure (internet-facing/sensitive first), compliance SLAs (PCI/FedRAMP) set hard clocks, "lower priority is not never."
   - ✅📣 LinkedIn "you do not need to [patch]" softened to "chasing raw volume is the wrong goal… prioritize is not the same as ignore."

2. **OpenClaw count self-contradiction: 537 vs 534 vs 500/93%** (Tech Editor, Worst Critic, CVE Researcher, Tech Writer, Marketing)
   - ✅ Added a products-table footnote explaining vendor-level vs product-level rollups so the gap reads as intentional.
   - 🔎 **You must reconcile the actual numbers against your OpenClawCVEs data** and re-derive the 93% after the July 1 run (500/537 = 93.1%; shifts if the denominator moves).

3. **Severity percentages summed to 98.2%, not 100%** (Worst Critic, CVE Researcher)
   - ✅ Added an "Unscored" row (the ~6.6% with no CVSS severity) plus a denominator footnote, so the column now sums to 100%.

4. **Jun 26 vs Jun 30 window mismatch** (Tech Editor, CVE Researcher, Worst Critic)
   - 🗓️ Resolves on the July 1 re-run. **Checklist for that run:** every "Jun 26" updates to Jun 30, the "(partial)" table tag and the "treat as a floor" caveat disappear, and month formatting is unified (pick "June 26" prose vs "Jun 26" table and stay consistent).

5. **`[LINK]` placeholders (10×) + unconfirmed handles** (Marketing, Worst Critic, Tech Writer)
   - 🔎 Biggest *embarrassment* risk is a live `[LINK]` in a **drip post (Day 2–5)** after launch-day attention fades. Mint the URL, find-replace all 10 at once, and stage only link-filled copy. Confirm `@rogolabs` and the Bluesky handle (still a TODO).

---

## 🟠 High-priority

- **CNA framing read as a backhanded inflation accusation** (CNA Owner).
  - ✅ CNA-section intro reworked: "platform/ecosystem/research CNAs" instead of "rather than the *original* vendors"; added an explicit "high counts reflect scope, not padding" sentence; "If you run a CNA" no longer implies the volume leaders drag quality (CPE gap reframed as NVD-side).
  - ✅📣 Campaign: "VulnCheck came out of nowhere" → "climbed to #3 (VulDB is #2)."
- **Undisclosed RogoLabs ownership of CVEForecast** (Worst Critic).
  - ✅ / ✅📣 Forecast block and Day-4 drip now disclose CVEForecast is "one of my own RogoLabs tools."
- **`GitHub_M` raw label in reader-facing copy** (CNA Owner, Tech Editor, CVE Researcher, Tech Writer).
  - ✅ Added `cna_display()` mapping `GitHub_M` → `GitHub` in prose and the CNA table.
- **"Two independent methods converge"** (CVE Researcher).
  - ✅ Reworded to "two straight-line methods… a sanity check, not two truly independent signals," and the seasonality step is now described (scale pace across the half, then divide by the prior H1 share). *Note: the figures are computed correctly; the issue was reproducibility/independence, not wrong math.*
- **"Oracle Corporation"** vs other short vendor names → ✅ aliased to "Oracle."
- **Stale committed `summary_stats.json`** (46.26% vs the blog's 48.8%) → ✅ removed; regenerates cleanly on the next run (generator was fixed in the earlier hardening pass).
- **Campaign hook "first decade combined = 33,411" isn't in the blog body** (Tech Writer) → ⚖️ flagged in the campaign; **decide:** add the comparison to the blog TL;DR (so the click-through pays off) or cut it from the campaign.

---

## 🟡 Medium / polish (not yet changed unless noted)

- ⚖️ **OpenClaw "research magnet" spin** — ✅ softened ("tracks researcher attention, not bad code"; VulnCheck's emerging-threat remit stated). Review the voice; revert if it reads too defensive.
- ✅ **KEV examples table** now labeled "a sample (first N of 84)" and renders "No" instead of blank for non-ransomware rows.
- ✅ **145-vs-84 populations** explicitly distinguished (published-in-H1 vs added-to-KEV-in-H1).
- ✅📣 **YoY rounding** — social standardized toward "nearly 49%"; blog stays 48.8%. Keep them from sitting side by side as "49%" vs "48.8%."
- ✅ **CPE "cannot be auto-matched"** softened to "lack a formal CPE, complicating NVD-style automated matching (many CNAs still carry vendor/product strings)."
- ✅📣 **"16 charts"** → "every chart" in the campaign (the post body renders 15; the scorecard is the hero image, not embedded). Alternatively embed `00_scorecard.png` in the body to make 16 literal.
- ⚖️ **Tech Writer prose notes** (not auto-applied): the parenthetical-percentage pattern is fixed in the TL;DR, but consider promoting OpenClaw to its own `## Spotlight` heading, trimming the repeated "volume up / exploitation rare" thesis in the conclusion, and cutting the define-the-acronym opener sentences (CVSS/CWE). Optional, voice-dependent.

---

## 🔎 You must personally verify before publishing

- ✅ **OpenClaw citation — VERIFIED** against the YouTube video (YFjfBk8HI5o). Title: "OpenClaw: The Viral AI Agent that Broke the Internet - Peter Steinberger | Lex Fridman Podcast **#491**." Steinberger is the creator (ex-PSPDFKit, built OpenClaw Nov 2025, later joined OpenAI); "viral," "local AI agent," and "barely existed a year ago" all check out. No misattribution risk on the named person / episode / descriptor.
  - ⚖️ Link target: blog points to `lexfridman.com/peter-steinberger/` (unconfirmed slug); consider swapping to the YouTube URL or confirming the lexfridman.com page resolves.
  - 🔎 Still open: "disclosed steadily across the half" (confirm from your OpenClawCVEs dates).
- 🔎 **OpenClaw counts** — 537 (vendor) vs 534 (product) vs 500 / 93% (VulnCheck share), reconciled against OpenClawCVEs after the July 1 run. (Data-internal; not a fact about Steinberger.)
- **Handles** — `@rogolabs` (X), the infosec.exchange instance, and the Bluesky handle.

---

## 🌐 WordPress paste-readiness (publish day is Wednesday, July 1)

A WordPress-expert pass found two paste-blockers and several hygiene issues. The
mechanical ones are now automated by **`10_wordpress_export.py`** (runs as step 8 of
`run_all.sh`, or standalone), which converts the freshly generated `blog.md` into
`blog_wordpress.html`:

- ✅ **Raw Markdown won't render in Gutenberg** (would publish literal `**`/`#`/`|`). The export runs the post through pandoc to real HTML, so headings, the `> Note` blockquote, links, and all ~11 pipe tables land as proper blocks. Paste path: editor → **Code editor** → paste `blog_wordpress.html` → back to **Visual**.
- ✅ **Duplicate in-body H1** stripped (WordPress renders the post Title as the only H1).
- ✅ **Featured-image HTML comment** stripped; export reminds you to set `00_scorecard.png` as the Document-panel Featured Image.
- ✅ **Weak alt text** — bare chart titles replaced with data-forward descriptions (re-run-safe, no baked-in numbers).
- ✅ **KEV table blank cells** render "No" (fixed in the generator).
- 🔎 **Images still 404 until uploaded** (the one step that needs WordPress access): upload the 16 `graphs/*.png` to the Media Library and re-point. Shortcut: if you upload with original filenames, re-run `python3 10_wordpress_export.py --media-base-url https://jerrygamblin.com/wp-content/uploads/2026/07` to pre-fill the `src`s.
- ⚖️ External-link new-tab behavior and the slug/meta are set in WordPress; the export prints the suggested **slug** (`2026-first-half-cve-data-review`) and **meta description**.

## 🗓️ Pre-publish mechanics (after the July 1 final run)

1. Run the full pipeline so every figure is a true Jun-30 window; the "(partial)" tag and "floor" caveats should drop out automatically.
2. Diff `blog.md` to confirm the code fixes rendered (severity sums to 100%, "GitHub" not "GitHub_M", KEV floor caveat, disclosure clause).
3. Refresh every hard number in `CAMPAIGN.md` (it's hand-written, it does not auto-update).
4. Mint the post URL, find-replace all 10 `[LINK]`s, stage only link-filled drip copy.
5. Confirm handles; attach the right chart per post; pin on X and Mastodon (no edge-ranking to resurface them).
