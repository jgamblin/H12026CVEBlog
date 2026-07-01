# 2026 First Half CVE Data Review: Launch Campaign

> **FINAL — numbers locked to the July 1 run; live URL inserted.**
> Post URL: **https://jerrygamblin.com/2026/07/01/3528/**
> House style: no em dashes. Confirm handles (@rogolabs, infosec.exchange, Bluesky) before posting.

## The thesis (use everywhere)

We are manufacturing CVEs faster than ever, but confirmed exploitation has not kept pace. Volume up, confirmed exploitation rare, signal-to-noise collapsing. The big number alarms; the 0.24% reframes it as a prioritization problem, not a panic. (0.24% is a CISA KEV floor that rises as the cohort ages, not a final exploitation rate.)

## Hero assets

- `00_scorecard.png` - the stat card (best single launch image)
- `01_cves_by_year.png` - 2026 towers over every prior first half
- Each drip post pairs with its own chart (named below)

## Hero stats (final)

- **35,364 CVEs** in H1 2026, more than any full year before 2024 (all of 2023 = 28,817)
- More CVEs in six months than the program's entire first decade combined (1999-2008 = 33,411, a far smaller, hand-curated era)
- **One new CVE every 7.4 minutes** (195.4/day)
- **+49.5%** over the same window in 2025
- **85 of 35,364 (0.24%)** on CISA's KEV list so far, a floor that rises as the cohort ages; 146 KEV additions this half (incl. older CVEs), 17 ransomware-linked
- Projected full year ~71-72K (run-rate), vs CVEForecast's 90,831 (my call: model is high; CVEForecast is my own RogoLabs tool)
- Top CVE issuer: GitHub Security Advisories (6,801); VulnCheck climbed to #3 (VulDB is #2)
- OpenClaw, the viral AI agent, is now a top-reported product and embraced the CVE lifecycle
- All-time catalog has passed 344,258 CVEs since 1999

## Strategy: one post, milked for a week

Launch with the thesis + hero image, then drip one finding per day, each with its own chart. ~6 days of content from one post, and the link keeps recirculating. Launch Tue-Thu, mid-morning US Eastern. Pin the launch post/thread for the week. End each post with a question to drive comments.

---

## Launch day (TODAY - post all four)

### LinkedIn
> Halfway through 2026, and the CVE numbers are not subtle.
>
> The first six months produced 35,364 CVEs. That is more than any full year on record before 2024. One new CVE every 7.4 minutes, up 49.5% over the same window last year.
>
> But here is the number that should actually shape your patching strategy: of those 35,364, only 85 are on CISA's KEV list so far. That is 0.24% (a floor that climbs as the cohort ages, not a final rate).
>
> The takeaway for security teams has not changed, it has just gotten louder. You cannot patch everything at once, so chasing raw volume is the wrong goal. Lead on exploitability, weight by what is actually exposed, and schedule the rest. Prioritize is not the same as ignore.
>
> Full mid-year review, with the data and the code behind every chart: https://jerrygamblin.com/2026/07/01/3528/
>
> How is your team triaging at 195 CVEs a day?
>
> #vulnerabilitymanagement #cybersecurity #CVE

### Twitter / X (thread)
> 1/ The first half of 2026 produced more CVEs than any full year before 2024.
>
> 35,364 in six months. One every 7.4 minutes. Up 49.5% over H1 2025.
>
> But only 85 are on CISA's KEV list. Mid-year CVE review 🧵 [attach 00_scorecard.png]
>
> 2/ For scale: H1 2026 alone is bigger than the CVE program's entire first decade combined (1999-2008). The curve isn't bending, it's accelerating. [attach 01_cves_by_year.png]
>
> 3/ The number that matters more than volume: 85 of 35,364 (0.24%) are on CISA's KEV list so far (a lagging floor that rises as the cohort ages). The overwhelming majority of CVEs are not confirmed-exploited. Volume is a triage problem, not a patch-everything problem.
>
> 4/ Who's publishing all this? The CNA mix flipped. GitHub Security Advisories leads at 6,801; VulnCheck climbed to #3 (VulDB is #2). Platforms, ecosystems, and research CNAs now drive the numbers. High counts reflect scope, not padding. [attach 08_top_cnas.png]
>
> 5/ CVEForecast (one of my own RogoLabs tools) projects 90,831 for the year. My call: we land closer to 72k. The model's gap rests entirely on a second-half surge that still has to show up.
>
> 6/ Everything here is reproducible. Data, code, and every chart: https://jerrygamblin.com/2026/07/01/3528/
> Built on the free tools at @rogolabs: cve.icu, cveforecast.org, cnascorecard.org

### Mastodon (infosec.exchange; 500 chars, substance over hashtags)
> Mid-year CVE check-in: the first half of 2026 produced 35,364 CVEs. More than any full year before 2024, and more than the program's entire first decade (1999-2008) combined. One every 7.4 minutes.
>
> The counterweight: only 85 of them (0.24%) are on CISA's KEV list. Volume keeps climbing; confirmed exploitation stays rare. The signal-to-noise problem is the story.
>
> Full writeup + reproducible code: https://jerrygamblin.com/2026/07/01/3528/

### Bluesky (300 chars)
> H1 2026: 35,364 CVEs. More than any full year before 2024. One every 7.4 minutes, +49.5% YoY.
>
> But only 85 (0.24%) are on CISA's KEV list so far. We're drowning in CVEs while confirmed exploitation stays rare. That gap is the whole game.
>
> Mid-year review + code: https://jerrygamblin.com/2026/07/01/3528/

---

## The drip (days 1-5, one finding/day, starting tomorrow)

**Day 1 - Exploitation rarity** (chart: KEV examples / 00_scorecard crop)
> 0.24%. That's how many H1 2026 CVEs are on CISA's KEV list so far: 85 of 35,364 (a floor that rises as they age). CISA added 146 to KEV this half, 17 tied to ransomware. The lesson every defender knows but every dashboard forgets: exploitability is the first filter, not volume. How much of your queue is driven by raw count today? https://jerrygamblin.com/2026/07/01/3528/

**Day 2 - The CNA flip** (chart: 08_top_cnas.png)
> GitHub Security Advisories is now the #1 CVE issuer (6,801). VulnCheck climbed to #3 (VulDB sits #2). The people assigning CVEs changed in 2026: platforms, ecosystems, and research CNAs now set the pace. High counts reflect scope, not padding. What that means for data quality 👇 https://jerrygamblin.com/2026/07/01/3528/

**Day 3 - The OpenClaw story** (chart: 18_top_products.png)
> ~500 of OpenClaw's 537 CVEs this half came from VulnCheck alone, disclosed steadily across the half. OpenClaw, the viral local AI agent (Peter Steinberger on Lex Fridman #491), is now a top-reported product of 2026, but that count tracks researcher attention, not bad code. The project also runs coordinated disclosure through GitHub. Is concentrated outside research a red flag or exactly what you'd want on a hot new target? I track it: github.com/jgamblin/OpenClawCVEs — https://jerrygamblin.com/2026/07/01/3528/

**Day 4 - Forecast scorecard** (chart: 01_cves_by_year.png)
> Are we on pace? Two straight-line methods say ~72k for 2026. CVEForecast (one of my own RogoLabs tools) says 90,831. I think the model is high: its gap rests on a second-half surge that hasn't shown up. Planting a flag now, settling it in December. Where do you think 2026 lands? https://jerrygamblin.com/2026/07/01/3528/

**Day 5 - Patch Tuesday myth + recap** (chart: 16_day_of_week.png)
> Everyone says Patch Tuesday. The 2026 data says Wednesday (7,943 vs 7,216). The midweek bulge is driven less by Microsoft than by high-volume CNAs batch-publishing. What does your patch cadence actually look like? Full mid-year review, every chart: https://jerrygamblin.com/2026/07/01/3528/

---

## Mechanics checklist

- [x] Refresh all numbers from the July 1 run
- [x] Insert the published URL in every link
- [ ] Confirm handles: @rogolabs, infosec.exchange instance, Bluesky handle
- [ ] Attach the right chart to each post (filenames above)
- [ ] Launch all four platforms within an hour; pin launch post/thread
- [ ] Reply-chain / quote drip posts back to the launch so the link resurfaces
- [ ] Engage in comments for the first 2 hours (algorithm window)
