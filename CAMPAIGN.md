# 2026 First Half CVE Data Review: Launch Campaign

> Draft copy uses numbers through Jun 26. **Refresh every figure after the final post-Jul-1 run.**
> No em dashes (house style). Swap in real handles and the published URL before posting.
>
> **`[LINK]` = the published post URL on JerryGamblin.com** (10 occurrences). It does
> not exist until you publish. Expected format, matching the series permalink pattern:
> `https://jerrygamblin.com/2026/07/<DD>/2026-first-half-cve-data-review/`. Replace all
> 10 once live.

## The thesis (use everywhere)

We are manufacturing CVEs faster than ever, but exploitation has not kept pace. Volume up, exploitation flat, signal-to-noise collapsing. The big number alarms; the 0.24% reframes it as a prioritization problem, not a panic.

## Hero assets

- `graphs/00_scorecard.png` - the stat card (best single launch image)
- `graphs/01_cves_by_year.png` - 2026 towers over every prior first half
- Each drip post pairs with its own chart (named below)

## Verified hero stats

- **34,601 CVEs** in H1 2026, more than any full year before 2024 (all of 2023 = 28,817)
- More CVEs in six months than the program's entire first decade combined (1999-2008 = 33,411)
- **One new CVE every 7.4 minutes** (195.5/day)
- **+48.8%** over the same window in 2025
- **84 of 34,601 (0.24%)** already known-exploited (CISA KEV); 145 KEV additions this half, 16 ransomware-linked
- Projected full year ~71-72K (run-rate), vs CVEForecast's 82,878 (my call: model is high)
- Top CVE issuer: GitHub; VulnCheck surged into the top 3
- OpenClaw, the viral AI agent, is now a top-reported product and embraced the CVE lifecycle

## Strategy: one post, milked for a week

Launch with the thesis + hero image, then drip one finding per day, each with its own chart. ~6 days of content from one post, and the link keeps recirculating. Launch Tue-Thu, mid-morning US Eastern. Pin the launch post/thread for the week. End each post with a question to drive comments.

---

## Launch day

### LinkedIn
> Halfway through 2026, and the CVE numbers are not subtle.
>
> The first six months produced 34,601 CVEs. That is more than any full year on record before 2024. One new CVE every 7.4 minutes, up nearly 49% over the same window last year.
>
> But here is the number that should actually shape your patching strategy: of those 34,601, only 84 are known to be exploited. That is 0.24%.
>
> The takeaway for security teams has not changed, it has just gotten louder. You cannot patch everything, and you do not need to. Volume is a triage problem. Prioritize on exploitability and automate the rest.
>
> Full mid-year review, with the data and the code behind every chart: [LINK]
>
> How is your team triaging at 195 CVEs a day?
>
> #vulnerabilitymanagement #cybersecurity #CVE #infosec

### Twitter / X (thread)
> 1/ The first half of 2026 produced more CVEs than any full year before 2024.
>
> 34,601 in six months. One every 7.4 minutes. Up 49% over H1 2025.
>
> But only 84 are known-exploited. Mid-year CVE review 🧵 [attach 00_scorecard.png]
>
> 2/ For scale: H1 2026 alone is bigger than the CVE program's entire first decade combined (1999-2008). The curve isn't bending, it's accelerating. [attach 01_cves_by_year.png]
>
> 3/ The number that matters more than volume: 84 of 34,601 (0.24%) are in CISA KEV. The overwhelming majority of CVEs are not known to be exploited. Volume is a triage problem, not a patch-everything problem.
>
> 4/ Who's publishing all this? The CNA mix flipped. GitHub leads at 6,730, VulnCheck surged into the top 3. Platforms and aggregators now drive the numbers, not the original vendors. [attach 08_top_cnas.png]
>
> 5/ CVEForecast projects 82,878 for the year. My call: we land closer to 72k. The model's gap rests entirely on a second-half surge that still has to show up.
>
> 6/ Everything here is reproducible. Data, code, and all 16 charts: [LINK]
> Built on the free tools at @rogolabs: cve.icu, cveforecast.org, cnascorecard.org

### Mastodon (infosec.exchange; 500 chars, substance over hashtags)
> Mid-year CVE check-in: the first half of 2026 produced 34,601 CVEs. More than any full year before 2024, and more than the program's entire first decade (1999-2008) combined. One every 7.4 minutes.
>
> The counterweight: only 84 of them (0.24%) are known-exploited. Volume keeps climbing; exploitation stays rare. The signal-to-noise problem is the story.
>
> Full writeup + reproducible code: [LINK]

### Bluesky (300 chars)
> H1 2026: 34,601 CVEs. More than any full year before 2024. One every 7.4 minutes, +49% YoY.
>
> But only 84 (0.24%) are known-exploited. We're drowning in CVEs while exploitation stays flat. That gap is the whole game.
>
> Mid-year review + code: [LINK]

---

## The drip (days 1-5, one finding/day)

**Day 1 - Exploitation rarity** (chart: KEV examples / 00_scorecard crop)
> 0.24%. That's how many H1 2026 CVEs are known to be exploited: 84 of 34,601. CISA added 145 to KEV this half, 16 tied to ransomware. The lesson every defender already knows but every dashboard forgets: exploitability is the filter, not volume. [LINK]

**Day 2 - The CNA flip** (chart: 08_top_cnas.png)
> GitHub is now the #1 CVE issuer (6,730). VulnCheck came out of nowhere into the top 3. The people assigning CVEs changed in 2026: platforms and aggregators now set the pace, not the original vendors. What that means for data quality 👇 [LINK]

**Day 3 - The OpenClaw story** (chart: 18_top_products.png)
> A project that barely existed a year ago is already one of the most-reported products of 2026: OpenClaw, the viral local AI agent (Peter Steinberger on Lex Fridman #491). 537 CVEs this half, and ~500 came from VulnCheck alone, disclosed steadily over four months. That is what a research magnet looks like. The project also runs its own coordinated disclosure through GitHub. I track it: github.com/jgamblin/OpenClawCVEs [LINK]

**Day 4 - Forecast scorecard** (chart: 01_cves_by_year.png)
> Are we on pace? Two straight-line methods say ~72k for 2026. CVEForecast says 82,878. I think the model is high: its gap rests on a second-half surge that hasn't shown up. Planting a flag now, settling it in December. [LINK]

**Day 5 - Patch Tuesday myth + recap** (chart: 16_day_of_week.png)
> Everyone says Patch Tuesday. The 2026 data says Wednesday (7,943 vs 7,081). The midweek bulge is driven less by Microsoft than by high-volume CNAs batch-publishing. Full mid-year review, all 16 charts: [LINK]

---

## Mechanics checklist

- [ ] Refresh all numbers from the post-Jul-1 run
- [ ] Insert the published JerryGamblin.com URL in every [LINK]
- [ ] Confirm handles: @rogolabs, infosec.exchange instance, Bluesky handle
- [ ] Attach the right chart to each post (filenames above)
- [ ] Launch all four platforms within an hour; pin launch post/thread
- [ ] Reply-chain / quote drip posts back to the launch so the link resurfaces
- [ ] Engage in comments for the first 2 hours (algorithm window)
