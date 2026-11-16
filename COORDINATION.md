# Coordination board

| Task | Status | Owner | Files |
|---|---|---|---|
| Integrated research dashboard, source audit, and GitHub Pages site | done | arena/dc12202f-poker2 | `COORDINATION.md`, `README.md`, `index.html`, `styles.css`, `app.js`, `.github/workflows/pages.yml` |
| Official structure-level event analysis, Venetian resort-fee/player-rate detail, organized subpages and source verification integration | done | arena/b9936cd9-poker2 | `COORDINATION.md`, `index.html`, `tournaments.html`, `hotels.html`, `planning.html`, `flagged.html`, `style.css` |

## Task log
- 2026-11-16: Claimed integrated dashboard/site scope on the session's fixed active branch. Repository initially contained only an 8-byte README; no existing board or parallel claims. Official source reviewed: Venetian DeepStack tournament schedule page (https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) and series overview (https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html). Schedule includes upcoming late-November/December 2026 events; the only verified indexed schedule source was for Venetian. Hotel rate/date-specific totals and walking routes have not been verified and will be left blank/flagged. Remaining local tournament details must be checked against the linked official schedule before promotion.

## Constraints and verification notes
- Work stayed on current branch `arena/dc12202f-poker2`; no alternate session branches were created.
- The listed schedule is a sourced subset, not claimed exhaustive. Dynamic schedules and fees can change; source/date remain visible, and unverified tournament entry rules are flagged.

## Completion record
- 2026-11-16 (integration follow-up, `arena/b9936cd9-poker2`): expanded the merged baseline with separate sourced event, hotel, planning, and review subpages. Official Venetian event #2 and #10 structure PDFs checked directly: both specify the $300/$400 buy-ins, guarantee, late-registration timing, fees withheld ($58/$65), and amount allocated per entry to the prize pool ($242/$335); neither structure PDF states a one-entry limit or expressly settles add-ons/re-entry, so both remain unqualified. Official resort-fee page confirms $55 plus tax nightly; official player-rate page gives $119 Venetian/$209 Palazzo starting rates and play conditions (six hours cash or $300+ tournament per night, else prevailing rate). No dated room quote or walk duration verified. Sources: [event schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html), [event #2/#12 structure](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf), [event #10 structure](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_6.pdf), [resort fee](https://www.venetianlasvegas.com/resort/resort-fee.html), [hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html), [player rates](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html). All displayed event facts link to official source; unknowns remain blank / flagged. The first `git pull --rebase origin main` encountered main's already-merged integration (PR #3); rebase was stopped, checked against upstream, and resumed preserving the completed site's owned files and the existing workflow. Added detail pages and navigation as integration follow-up rather than replacing the existing dashboard.
- Official sources checked on 2026-11-16: [Venetian DeepStack IV event schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html), [Venetian series overview](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html), [Venetian offers](https://www.venetianlasvegas.com/hotel/offers.html), and [Venetian booking](https://www.venetianlasvegas.com/book). Event rows cross-checked to schedule; no event promoted as verified single-entry because the rules are not established in schedule summary. Hotel nightly total and walk times intentionally blank because trip dates/occupancy and confirmed checkout quotes/routes are absent.
- Checks: internal anchor audit passed (8 in-page anchors, 0 missing); `git diff --check` passed; Pages workflow run [43930555829](https://github.com/karagemop466-tech/Poker2/actions/runs/43930555829) succeeded; Pages status built at https://karagemop466-tech.github.io/Poker2/.
- PR [#2](https://github.com/karagemop466-tech/Poker2/pull/2) merged 2026-11-16. Irregularities are published in the site's Flagged for Review section: unresolved entry/add-on terms, RaceDay Stack mechanics, overlapping starts, missing exact-date hotel quotes and walking routes, and no confirmed 8 AM start.
- Follow-up was merged as [PR #4](https://github.com/karagemop466-tech/Poker2/pull/4), merge commit `25ae3278495d9ddaf4e0db95761fc12264945410` (2026-11-16). GitHub Pages deployment [run 43930959307](https://github.com/karagemop466-tech/Poker2/actions/runs/43930959307) completed successfully. Live site: https://karagemop466-tech.github.io/Poker2/ with detail pages `/tournaments.html`, `/hotels.html`, `/planning.html`, `/flagged.html`. No PR checks were reported; Pages deploy passed. Local cross-page stylesheet/script/link audit and `git diff --check` passed.

## Session arena/f743ae5a-poker2 — claims and record (2026-11-16)

| Task | Status | Owner | Files |
|---|---|---|---|
| Source registry (official vs. non-official separated; alias keys removed) | done | arena/f743ae5a-poker2 | `data/sources.json`, `data/non_official_refs.json` |
| Venetian DSE IV schedule dataset from official schedule PDF | done | arena/f743ae5a-poker2 | `data/tournaments.json`, `data/flags.json` |
| Category pages: candidates, re-entry/spending, 8 AM schedule, hotel cost detail, summary, flagged rows, improvements, questions, repo review | done | arena/f743ae5a-poker2 | `pages/*.html`, `scripts/build.py` |
| Hotel rows: official resort fees and Venetian/Palazzo poker-suite rates | done (rates conditional; walk times blank) | arena/f743ae5a-poker2 | `data/hotels.json`, `pages/hotel-costs.html` |
| Hotel walking distances (30-minute test) | open — not verified | none | — |
| Clark County lodging tax | open — no official county source found | none | — |
| Wynn schedule PDF re-verify (HTTP 500 on re-fetch 2026-11-16) | open | none | — |

Task log:
- 2026-11-16: Re-read the official Venetian DSE IV schedule PDF. Built the event dataset from it. Fees come only from structure sheets that were read earlier. Rows are candidates for single-entry, not confirmed. No event is marked confirmed single-entry, which matches the main site.
- 2026-11-16: Official Venetian poker-suite rate page read. It states from $119 (Venetian) and $209 (Palazzo), a $55 resort fee per night, and qualifying-play conditions. Those are the only hotel rates added; dated quotes are not captured.
- 2026-11-16: Wynn schedule PDF returned HTTP 500 on re-fetch. Wynn WPT rows rely on earlier verified reads and are flagged.
- Kept the existing root site (`index.html`, `tournaments.html`, `hotels.html`, `planning.html`, `flagged.html`). Added category pages under `pages/` and links from the sidebar.

Integration (this session is the integration session for shared outputs):
- Branch: `arena/f743ae5a-poker2` → PR #6 into `main`.
- Pages deploy and merge result: recorded below after merge.


## Session arena/acd81e67-poker2 — claims and record (2026-11-16)

| Task | Status | Owner | Files |
|---|---|---|---|
| Official-check dataset for Venetian DSE IV (single-entry, multi-flight, team, satellite, re-entry/add-on, other venues) | done (rows re-read from official page) | arena/acd81e67-poker2 | `data/venetian-dse4-official-check.json` |
| Hotel official-check dataset (resort fees; Venetian/Palazzo conditional starting rates) | done; walk times, room tax and Caesars fee blank | arena/acd81e67-poker2 | `data/hotels-official-check.json` |
| Dashboard subsite (schedule, excluded/special, hotels, summary, questions, suggestions, repo review, flagged) | done; served under `/docs/` | arena/acd81e67-poker2 | `docs/*`, `scripts/build_site.py`, `scripts/check_links.py` |
| Integration/PR for this branch | in progress (see below) | arena/acd81e67-poker2 | — |

Notes for integration (2026-11-16):
- Main already contained `data/tournaments.json` and `data/hotels.json` from PR #6 (arena/f743ae5a-poker2). This branch leaves those files unchanged and writes its own data under distinct names so neither dataset is overwritten.
- Values in main's `data/tournaments.json` such as `reg_closes`, `chips` and `level` were NOT reproduced from the official pages read in this session (registration close times and chip counts are not on the official schedule page). They are not used in `docs/`. Flagged for review, not verified here.
- Root site (`index.html`, `tournaments.html`, `hotels.html`, `planning.html`, `flagged.html`, `pages/*`) is untouched by this branch.
- Two dashboards now exist: the root site (main) and `/docs/` (this branch). Consolidating them is a suggestion for user review, not applied.

Task log (this session):
- Re-read the official Venetian DSE IV schedule page in full (4 chunks). Each row's name, date, time, event number and structure PDF number was taken from that table. Earlier drafts had reg-close times and chip counts that were not on the page; removed.
- Read the official poker suite-rate page: from $119 (Venetian) and $209 (Palazzo), $55 resort fee per night, conditional on 6 hours live cash or a $300+ tournament per night. Recorded as conditional starting rates, not dated quotes.
- Verification: 131/131 data rows have an official or repo https source; 0 broken internal links in `docs/`.

Integration result (arena/acd81e67-poker2 → main):
- PR: [#7](https://github.com/karagemop466-tech/Poker2/pull/7) — merge commit `23e5dfe`, merged 2026-11-16 (merge commit, not squash). Mergeable state was CLEAN after main moved twice; the branch was merged with main (not rebased) to keep the other sessions' commits.
- Pages deploy: workflow run [43931916982](https://github.com/karagemop466-tech/Poker2/actions/runs/43931916982) completed `success` on `23e5dfe`; `gh api repos/karagemop466-tech/Poker2/pages/builds/latest` reports `built` for `23e5dfe`.
- Live check: https://karagemop466-tech.github.io/Poker2/docs/single-entry.html fetched and served the merged content. Root site https://karagemop466-tech.github.io/Poker2/ is the other session's page and was not changed.
- Known issue for review: this branch was force-updated once (a broken merge commit was amended before PR #7 was merged); no other session's commits were rewritten.
- Flagged items (do not block merge): see `docs/flagged.html` F-01…F-22, and the notes above on main's `reg_closes`/`chips`/`level` values.

## Session arena/a22d577b-poker2 — claims and record (2026-11-16)

| Task | Status | Owner | Files |
|---|---|---|---|
| T1 Repo review + irregularity log | done | arena/a22d577b-poker2 | `data/verified/flags.json` |
| T2 Single-entry data — The Venetian (DeepStack IV, Nov 18 – Dec 23 2026) | done | arena/a22d577b-poker2 | `data/verified/tournaments.json` |
| T3 Excluded / unverified data — Wynn daily + WPT | done (WPT structure chunks 1–7 unread; rows stay UNVERIFIED) | arena/a22d577b-poker2 | `data/verified/tournaments.json` |
| T4 Hotels: resort-fee verification (Venetian, Wynn) | done (room rates and walk times not verified; blank) | arena/a22d577b-poker2 | `data/verified/hotels.json` |
| T5 Executive summary, questions, suggestions, sources | done | arena/a22d577b-poker2 | `data/verified/{summary,questions,suggestions,sources}.json` |
| T6 Site build (generator with official-source and link checks) | done | arena/a22d577b-poker2 | `scripts/build.mjs`, `verified/**` |
| T7 Integration: merge, Pages check, record | in progress | arena/a22d577b-poker2 | this section |

Coexistence with main (no overwrites):
- Main's `data/*.json` and root pages (`index.html`, `tournaments.html`, `hotels.html`, `planning.html`, `flagged.html`, `pages/*`, `docs/*`) belong to other sessions and were NOT changed.
- This session's data is under `data/verified/` and its site under `verified/` (live at `/Poker2/verified/`). Two overlapping dashboards therefore exist on main plus this one. Consolidating them is a suggestion for the user (see `verified/suggestions/index.html`, S-items), not applied here.
- Branch name deviation: the task spec asks for `session-<id>/<task>`, but this session's branch is `arena/a22d577b-poker2` (fixed for the session). Recorded as flag F02.

Task log (this session):
- 2026-11-16: Claimed T1–T7 on the board. Committed `data/tournaments.json` (32 verified Venetian single-entry rows; Venetian 15 + Wynn 17 excluded; Venetian 17 + Wynn WPT 49 unverified).
- 2026-11-16: Built hotels, flags, questions, suggestions, summary and sources data. Built the site with `scripts/build.mjs` (11 pages). The build fails if any table row lacks an official-host source; internal link check passed.
- 2026-11-16: Corrected drafts. Removed unsupported claims (a Wynn phone number, an Encore location, WPT re-entry text, an unverified Wynn tax rate, aggregator resort-fee figures). Confirmed the Venetian structure URL pattern (sheet 16 resolves and confirms the Event 36 facts).
- 2026-11-16: First merge attempt (PR #11) conflicted with main's new data and root pages. Resolved by moving this session's files to `data/verified/` and `verified/` and merging main, keeping main's COORDINATION.md and appending this section. No other session's files were overwritten.
- Conflicts logged: COORDINATION.md (add/add) — resolved by keeping main's board and appending this section. `data/*.json` and root site names — avoided by relocation.

## Current session and constraints

- **Owner/session identifier:** `arena/704e2a25-poker2` (current Arena branch; no separate session ID was exposed in the checkout).
- **Branch:** `arena/704e2a25-poker2` (the active branch provided for this session).
- **Initial repository review (at fork):** the branch began with only `README.md` (`# Poker2`) and no coordination board. After rebase, `origin/main` contained several merged dashboard implementations and an existing Pages workflow.
- **Concurrency note:** this board was created because none existed. No other claims were visible at claim time. This checkout exposes no mechanism to enumerate other live Arena sessions, so avoid overlapping edits if another contributor appears.
- **Branch constraint:** work stays on the provided branch; do not create or switch branches.

## Task board

| Task | Status | Owner | File scope |
| --- | --- | --- | --- |
| Build an isolated cross-venue evidence dashboard; keep the strict single-entry shortlist empty and avoid changing other sessions’ dashboards | done (pushed; Pages deploy awaits merge) | `arena/704e2a25-poker2` | `COORDINATION.md`, `README.md`, `site/*` |

## Completion log

- 2026-11-16: Implemented the isolated, responsive cross-venue dashboard under `site/` with 25 source-linked event records, 32 official/Forbes Travel Guide sources, an explicitly empty strict single-entry shortlist, a start-time guide, conditional hotel-rate context, and open trip inputs. Existing root/`pages/`/`docs/`/`verified/` dashboards and datasets were left unchanged.
- Verification: JavaScript syntax checks passed; a DOM-mock render check produced all 25 rows, correctly filtered the four Caesars entries and nine extra-spend records, and rendered all three hotel cards and the source registry. HTML anchor/local-link audit and `git diff --check` passed. Preview server returned HTTP 200 for the page, stylesheet, and both scripts.
- Rebase/push: resolved the add/add conflict by preserving the full `origin/main` board and appending this session’s claim/research notes. Rebased commits `1884d44` and `4dd113f` onto `c7deb19`, added site commit `c3921fb`, and pushed the active branch with `--force-with-lease` because the remote pointed to the pre-rebase history. No other branch was touched. The site is not merged or production-deployed; the existing Pages workflow deploys from `main`.

## Sources and verification log

Snapshot date: **2026-11-16**. Research is limited to upcoming Las Vegas Strip events and official hotel terms; any unconfirmed entry policy remains unknown rather than being inferred.

- **Caesars Palace daily NLH:** the official 2026 flyer (`https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf`) verifies 10 a.m. and 6 p.m. at $100; 2 p.m. and 9 p.m. at $160; each has a $1,000 guarantee and 20,000 starting chips. Each has a $50 first-break add-on and re-entry is allowed after elimination within the first break. The 2026 flyer supersedes the linked Caesars marketing article's inaccurate claim that all four buy-ins are $100. These are spend-enabled, not single-entry candidates.
- **Horseshoe daily NLH:** Caesars' current Las Vegas tournament article (`https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip`) lists 9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m., and 11 p.m.; the casino page confirms six daily times but not buy-ins, guarantees, or entry rules. Earliest confirmed recurring start is 9 a.m.; no 8 a.m. start found.
- **Venetian DeepStack Extravaganza IV:** official schedule (`https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html`) runs Nov. 16–Dec. 23, with event-level structures. Reviewed Nov/Dec one-day structures show entry amounts, guarantees (where published), stacks, and registration details but do not expressly establish one-entry-only or re-entry limits. Do not treat omission of re-entry language as proof of single entry.
- **WPT World Championship:** Wynn's official schedule (`https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf`) runs Nov. 27–Dec. 21. The official structure book (`https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf`) explicitly allows unlimited re-entry through a level deadline in the $600 NLH, $800 NLH, $1,600 NLH, $600 HORSE and $1,600 PLO Mystery Bounty; the $1,100 WPT Prime allows one entry plus one re-entry per starting flight. These are not strict single-entry.
- **Hotel quality/cost:** Forbes Travel Guide's 2026 listings rate Wynn, The Venetian, and The Palazzo Four-Star. Official Venetian poker-rate page (`https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html`) advertises starting nightly base rates of $119 (Venetian) and $209 (Palazzo), subject to availability and qualifying poker play; the resort fee is $55 plus tax. Venetian terms specify a 13.38% room tax and $55 plus applicable tax nightly. Wynn's official resort policy (`https://www.wynnlasvegas.com/about-us/resort-information`) confirms $55 plus tax nightly. Neither yields an actual date-specific stay total without trip dates. No reliable current resort-fee amount or date-specific nightly price was established for Caesars Palace or Horseshoe.
- **On-site proximity:** candidate hotels are on-site at the corresponding poker rooms; exact guest-room-to-room walking times are not published here. Use hotel/venue co-location rather than an invented route estimate.

## Irregularities / requests

- Vacation dates, number of nights/guests, and room requirements were not supplied. Exact date-specific hotel totals (including resort fees and taxes) cannot be represented as verified until those inputs or publicly published date-specific rates exist. The site will leave unconfirmed amounts blank and flag the limitation rather than infer prices.
- “Single entry” will be treated as a format explicitly confirmed by an official tournament structure/rules page. Events whose official page does not establish entry/re-entry/add-on rules will be excluded from the primary shortlist and flagged for review.
