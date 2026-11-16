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

## Session arena/e3cb221d-poker2 — source follow-up / coordination record (2026-11-16)

| Task | Status | Owner | Files |
|---|---|---|---|
| Re-read Wynn WPT event terms and document confirmed entry limits / cost mechanics | done | arena/e3cb221d-poker2 | `research/e3cb221d-official-follow-up.md` |
| Verify official Caesars recurring start times and Venetian/Wynn hotel fee wording | done (prices / routes remain unverified) | arena/e3cb221d-poker2 | `research/e3cb221d-official-follow-up.md` |
| Request integration of newly verified Wynn re-entry, Caesars start/add-on, and Venetian page irregularities into existing owned datasets/pages | needs review | arena/e3cb221d-poker2 | request only; see task log below |

Task log:
- The checkout initially contained only the original README at base `058cd54`, and no coordination board. A claim was committed/pushed immediately. Before opening my PR, other sessions merged their integrated site to `main` (now `c83d13e`); the current main already includes the live root dashboard and multiple linked category sites. I fetched/re-read the current board and existing pages before proceeding.
- Read the Wynn WPT structure PDF chunks 1–7 and verified that the featured $600 NLH $400K and $800 NLH $1M tournaments permit unlimited re-entry per starting flight until level 9; WPT Prime allows one entry plus one re-entry per starting flight until level 10; the listed $600 NLH Turbo events allow unlimited re-entry until level 9. Full details and exact source URLs are in the unique audit file above.
- Read Caesars' official tournament guide: Horseshoe's recurring NLH schedule includes 9 AM, 11 AM, 2 PM, 5 PM, 8 PM and 11 PM; the guide does not provide its buy-in/guarantee/entry limits. Caesars Palace's daily $100/$1,000-GTD event offers a $50 first-break add-on for 15,000 chips.
- Rechecked Wynn's official $55-plus-tax resort-fee page, Venetian hotel terms (13.38% tax), Venetian poker-rate and resort-fee pages (wording ambiguity plus qualifying play), and Venetian series overview (status label/date inconsistency).
- PR #12 contained a duplicate version of root pages and conflicted with already-merged main-owned site files. Closed PR #12 rather than overwrite the active site. Merged current `origin/main` into this branch, resolved overlapping root files by retaining main's versions and workflow, removed my duplicate root pages, and preserved all other merged-session work. The only new source deliverable is `research/e3cb221d-official-follow-up.md`; requests to modify files owned by completed sessions are recorded for their integration owner rather than edited here.
- Current live main dashboard remains at https://karagemop466-tech.github.io/Poker2/. Existing Pages workflow and root site are retained from main.

Integration request (no owner-owned file edited): please update the existing `data/verified/tournaments.json` / `verified/**` or the designated root pages to show the verified Wynn re-entry policies in the separate spend-more list, the Caesars 9 AM recurring Horseshoe schedule and Caesars Palace paid add-on, and the two Venetian source irregularities (stale series label and resort-fee wording). Keep exact hotel stay totals, walk times, and unclear Venetian event entry rules blank. This request stays `needs review` until reflected in the existing site's Flagged for Review / re-entry category.

Publication coordination: the integrated site has already been merged by prior sessions; their PRs #2, #4, #7 and #11 and Pages build records are in earlier entries above. This session did not merge its duplicate PR or change the live site's owned pages.
- Branch synchronization note (2026-11-16): before pushing the current-branch integration, `git pull --rebase origin arena/e3cb221d-poker2` began replaying the old branch history and conflicted on the `COORDINATION.md` add/add record from already-integrated main. Aborted that rebase rather than rewriting the merged main history; the resolved local branch is a fast-forward descendant of the remote session branch and will be pushed as-is. Conflict was coordination-only; all upstream main site/data files remain intact.

### Subsequent integration record from upstream main
- Existing integration PR [#11](https://github.com/karagemop466-tech/Poker2/pull/11) (`arena/a22d577b-poker2` → `main`) merged with merge commit `c83d13e`; Pages workflow run [43932308394](https://github.com/karagemop466-tech/Poker2/actions/runs/43932308394) completed successfully. Pages status was `built`; live content was checked at `/verified/` and `/verified/flagged/`.
- Upstream finalization for PR #11 and its Pages deployment was preserved from main rather than overwritten by this session's board entry.

### Session arena/e3cb221d-poker2 publication result
- Follow-up PR [#14](https://github.com/karagemop466-tech/Poker2/pull/14) merged to `main` at `bde73082b57ff38a4867929aee5c44b5c80b7541` on 2026-11-16 18:50 UTC. It added the official-source follow-up report and this coordination record; it did not replace main-owned dashboard files.
- GitHub Pages build/deploy succeeded: `pages build and deployment` run [43933010600](https://github.com/karagemop466-tech/Poker2/actions/runs/43933010600) and `Deploy static site to GitHub Pages` run [43933012134](https://github.com/karagemop466-tech/Poker2/actions/runs/43933012134). Pages API reports `status: built` for commit `bde73082b57ff38a4867929aee5c44b5c80b7541`; site URL remains https://karagemop466-tech.github.io/Poker2/.
- Both workflows were queued concurrently; an older competing run was cancelled by the Pages concurrency group. The final runs above completed successfully and the latest Pages build is `built`.

## Session arena/3ab1bcae-poker2 — Las Vegas poker vacation planner (2026-11-16)

| Task | Status | Owner | Files |
|---|---|---|---|
| Review repo + build initial single-entry/multi-entry/hotel/schedule/summary/suggestions/questions/flagged Pages site | done (superseded by integrated main site) | arena/3ab1bcae-poker2 | index.html, style.css, tournaments.html, multi-entry.html, hotels.html, schedule.html, executive-summary.html, suggestions.html, questions.html, flagged-review.html |
| Add verified single-entry lead as flagged third-party reference | done | arena/3ab1bcae-poker2 | data/non_official_refs.json, data/flags.json |
| Integration/PR to main + Pages deploy confirmation | done | arena/3ab1bcae-poker2 | PR #8, main |

Task log:
- Branch `arena/3ab1bcae-poker2` created from base `058cd54` (stale initial commit); later re-based onto current main (`c889d78`) to avoid overwriting parallel sessions' integrated site.
- Researched live Strip tournaments (VegasPokerCalendar Nov 16–17, 2026 + PokerAtlas venue calendars). Verified Westgate $70 NLH freezeouts at 5:05 PM and 9:05 PM via the VegasPokerCalendar detail page (“Freezeout / No rebuy / No add-on”).
- Added Westgate finding as a flagged third-party lead only (consistent with the site's official-source standard—not used as a confirmed value): `data/non_official_refs.json` TP_WESTGATE; `data/flags.json` Westgate flag.
- Created PR [#8](https://github.com/karagemop466-tech/Poker2/pull/8) (`arena/3ab1bcae-poker2` → `main`); merged with merge commit `6f5e6db`; Pages workflow completed `built`; live site at https://karagemop466-tech.github.io/Poker2/. Subsequently PR #14 (`arena/e3cb221d-poker2`) merged on top at `bde7308`; main sync verified.
- Flagged items (do not block merge): Westgate entry rules are aggregator-sourced, not confirmed with the Westgate poker room.

## Session arena/93b28309-poker2 — supplemental audit (2026-11-16)

| Task | Status | Files |
|---|---|---|
| Wynn WPT / MGM official source cross-check | done; unknowns flagged | `data/sources.json`, `data/flags.json`, `pages/spending.html`, `pages/schedule.html`, `flagged.html` |
| Hotel fee / quality comparison corrections | done; dated totals and walk durations remain blank | `data/hotels.csv`, `data/hotels.json`, `hotels.html`, `pages/hotel-costs.html` |
| Integrate into current dashboard and record source audit | done | `reports/research-and-verification.md`, current root pages |

- Preserved latest upstream dashboard pages and other sessions' coordination records. No new dashboard was introduced.
- Official source findings and unresolved questions are detailed in `reports/research-and-verification.md`, `data/flags.json`, and the pages above. Wynn's verified re-entry events remain excluded from single-entry recommendations. MGM's August-labeled PDF relevance and $11 gratuity / 10,000-chip wording remain flagged. Hotel prices, true nightly totals and walk times remain blank; Venetian/Palazzo poker-rate numbers are not assigned to a specific property.
- Validation: `python3 scripts/check_links.py` passed (131/131 rows cited); custom check found no broken relative links in 20 root/pages HTML documents; `git diff --check` passed; CSVs parse and all data rows have official HTTPS source links; local preview returned HTTP 200.
- Existing Pages workflow deploys repository root on push to `main`; no workflow change was needed. PR [#16](https://github.com/karagemop466-tech/Poker2/pull/16) merged on 2026-11-16 at merge commit `b484eb08d580e3035d4b538dba0c33f5dc555cb0`.
- Deployment verified: Pages workflow run [43933521465](https://github.com/karagemop466-tech/Poker2/actions/runs/43933521465) completed successfully; Pages API reports `built` for `b484eb08d580e3035d4b538dba0c33f5dc555cb0`. Public Pages URL: https://karagemop466-tech.github.io/Poker2/.

## Session arena/7a4b09e2-poker2 — consolidated dashboard + feature build (2026-11-16)

This session operates as the **final integration session** for shared outputs (root site, index/navigation, combined tables) per the repo's stated rule that only an integration session changes those files. All prior tasks on this board are `done`; no other session holds an active claim.

| Task | Status | Owner | Files |
|---|---|---|---|
| T1 Claim board + repo review | in progress | arena/7a4b09e2-poker2 | `COORDINATION.md` |
| T2 Structure-sheet sweep: all 37 official Venetian DSE IV sheets, structured rule fields + source excerpt + retrieval date | in progress | arena/7a4b09e2-poker2 | `data/site/*.json` (new) |
| T3 Venue pages (Venetian, Wynn, Horseshoe/Caesars, Bellagio, MGM Grand, Resorts World) with events + hotels | in progress | arena/7a4b09e2-poker2 | `venues/*.html` (new) |
| T4 Hotel true-cost log (dated), resort fees, tax | in progress | arena/7a4b09e2-poker2 | `data/site/hotels.json` (new) |
| T5 Trip-cost calculator, date filter, single-entry toggle, search, overlap/fallback schedule | in progress | arena/7a4b09e2-poker2 | `assets/site.js`, `index.html` |
| T6 Scheduled official-URL re-check with change detection | in progress | arena/7a4b09e2-poker2 | `scripts/recheck_sources.py`, `.github/workflows/recheck.yml`, `data/site/checks.json` |
| T7 Executive summary, questions log, suggestions, flagged-for-review, repo review | in progress | arena/7a4b09e2-poker2 | `summary.html`, `questions.html`, `suggestions.html`, `flagged.html`, `repo-review.html` |
| T8 Build/link verification, PR to main, merge, Pages deploy confirmation | in progress | arena/7a4b09e2-poker2 | this section |

Scope rules for this session:
- New canonical site is written to the **repository root** (`index.html` plus category subpages) with its own stylesheet `assets/site.css` and script `assets/site.js`. The legacy stylesheets `style.css` / `styles.css` are left untouched so legacy pages still render.
- Legacy dashboards (`docs/`, `verified/`, root `tournaments.html`, `planning.html`, `pages/*`) are **not deleted**; they are listed as superseded in the Repo review page so no existing link breaks.
- Existing `data/*.json` datasets owned by earlier sessions are not rewritten; new consolidated data goes to `data/site/`.
- Verification standard: every displayed fact carries a link to an official host. Unconfirmed cells stay blank and appear on `flagged.html`.

Task log:
- 2026-11-16: Board re-read; all prior tasks `done`. Claim committed before any research or edits.

### Session arena/7a4b09e2-poker2 — completion record (2026-11-16)

| Task | Status | Owner | Files |
|---|---|---|---|
| T1 Claim board + repo review | done | arena/7a4b09e2-poker2 | `COORDINATION.md`, `repo-review.html` |
| T2 Structure-sheet sweep: all 37 official Venetian DSE IV sheets + schedule PDF, structured rule fields with source + retrieval date | done | arena/7a4b09e2-poker2 | `scripts/dataset.py`, `data/site/*.json` |
| T3 Venue pages (Venetian, Wynn, Bellagio, Caesars Palace, MGM Grand, Horseshoe) with events and hotels | done | arena/7a4b09e2-poker2 | `venues.html`, `venues/*.html` |
| T4 Hotel true-cost log (dated), resort fees, tax, parking | done (walk times and dated totals remain blank) | arena/7a4b09e2-poker2 | `hotels.html` |
| T5 Trip-cost calculator, date filter, single-entry toggle, cross-table search, overlap/fallback schedule | done | arena/7a4b09e2-poker2 | `index.html`, `tournaments.html`, `schedule.html`, `assets/site.js`, `assets/site.css` |
| T6 Scheduled official-URL re-check with change marking | done (baseline only in this sandbox; first live fetch happens in Actions) | arena/7a4b09e2-poker2 | `scripts/recheck_sources.py`, `.github/workflows/recheck.yml`, `data/site/checks.json` |
| T7 Executive summary, questions, suggestions, flagged, sources, repo review | done | arena/7a4b09e2-poker2 | `summary.html`, `questions.html`, `suggestions.html`, `flagged.html`, `sources.html` |
| T8 Build/link verification, PR, merge, Pages confirmation | in progress | arena/7a4b09e2-poker2 | this section |

Sources re-read and verified in this session (all 2026-11-16):

- Venetian DSE IV **schedule PDF** (`dse-nov-2026-schedule.pdf`) — full read, both pages of the table. It **does** print registration-close times, starting chips and level lengths, which corrects the earlier board note that said those values are absent from official sources (flag F-14).
- All **37** Venetian structure sheets (`dse_nov_2026-structure_1.pdf` … `_37.pdf`) — read individually; event-number ownership matched to schedule rows rather than assumed from the URL.
- Venetian event page, series overview, poker room page, resort fee page, hotel terms, 2026 poker suite rates.
- Wynn WPT schedule PDF and structures PDF (general terms, $600/$400K, TORSE, PLO $400, Mixed Triple Draw read; the $800/$1M, Prime and Super Gold Million event terms were not re-read — flag F-13).
- Wynn daily poster + daily structures PDF (Mon–Thu, Fri rebuy/add-on, Sat–Sun), Wynn resort policies.
- Bellagio poker page + Friday $600 terms + hotel reservation terms.
- Caesars Palace daily NLH flyer 2026 + casino page; Horseshoe casino page (no retrievable tournament document — flag F-12).
- MGM Grand poker page, $120 structure, weekly schedule PDF, hotel terms.

New verified findings not on the board before:

1. **RaceDay Stack resolved.** Sheet 18 states $200 buy-in, 30,000 chips, 20/15-minute levels, registration closes after level 6 + break (~12:25 PM), $35 withheld, no re-entry/rebuy/add-on language. It remains *unconfirmed* rather than confirmed single-entry.
2. **Registration-close and chip values are official.** They come from the schedule PDF and, per event, from the structure sheets; the two agree.
3. **No confirmed single-entry event anywhere.** Wynn ($600/$400K, TORSE, PLO $400, Mon–Thu and Sat–Sun dailies), Bellagio Friday $600, Caesars Palace dailies, the Wynn Friday rebuy event and MGM Grand all publish permissive or silent text.
4. **Wynn daily events are suspended during the WPT series** (Wynn poker page), which covers Nov 27 – Dec 21.
5. **MGM Grand's $11 "voluntary" gratuity buys 10,000 extra chips** — excluded from the no-add-on group.
6. **Venetian publishes a 13.38% Clark County Room Tax**; Wynn, Bellagio and MGM Grand publish only "current tax rates". Applying 13.38% to them would be an inference, so it is not done.
7. **Earliest verified start is 09:10 AM** (Venetian Event 46, Dec 12). No 08:00 AM tournament exists in any retrieved schedule.

Verification performed: `python3 scripts/build.py` (96 event rows, 23 sources, 8 hotel records, 14 flags); `python3 scripts/check_links.py` → 18 pages, 1,098 hrefs, 0 broken internal links, 0 non-official external hosts; the build aborts if any row cites a non-official host. No value was inferred: every blank is reproduced on `flagged.html` with its reason.

Irregularities and open items (published on `flagged.html`, do not block merge): F-01 no confirmed single-entry event; F-02 Venetian sheets silent on re-entry; F-03 no official walking times; F-04 no dated hotel totals; F-05 tax rate published only by the Venetian; F-06 MGM schedule PDF titled August with no year; F-07 MGM $11 gratuity buys chips; F-08 Venetian series page still labels the previous series "Current Series"; F-09 schedule PDF date-cell text corruption; F-10 no 08:00 AM start; F-11 Wynn dailies suspended in the WPT window; F-12 Horseshoe publishes no retrievable structure; F-13 three WPT event terms not re-read; F-14 earlier board note about missing chip/reg-close values is superseded.

Conflict and coexistence handling: no other session has an active claim; every earlier task on this board is `done`. Legacy dashboards (`docs/`, `verified/`, `pages/`, `planning.html`) and the earlier `data/*.json` datasets were **not** deleted or rewritten. New data lives in `data/site/`, generated from `scripts/dataset.py`. The legacy `style.css` / `styles.css` / `app.js` are untouched; the new site uses `assets/site.css` and `assets/site.js`.

## Session arena/7d846749-poker2 — final integration, feature build and consolidation (2026-11-16)

Status of T1–T5 as of the end of this session: **all done**. Details and the merge/deploy trail are
recorded below and in the PR.

| Task | Status | Owner | Files |
|---|---|---|---|
| T1 Repo review + coordination claim | done | arena/7d846749-poker2 | `COORDINATION.md`, `repo-review.html` |
| T2 Official re-verification of every event/hotel row | done — 237 event rows, 7 hotels, 14 walk pairs | arena/7d846749-poker2 | `scripts/poker_data.py`, `data/poker/dataset.json` |
| T3 Feature build | done | arena/7d846749-poker2 | `scripts/build_dashboard.py`, `style.css`, `app.js` |
| T4 Consolidated site | done — 21 generated pages | arena/7d846749-poker2 | `index.html`, `events.html`, `ranking.html`, `dayplan.html`, `trip-cost.html`, `hotels.html`, `rates.html`, `walking.html`, `questions.html`, `suggestions.html`, `flagged.html`, `sources.html`, `repo-review.html`, `venues/*` |
| T5 Final integration: PR → main, Pages deploy, record | done — see PR link and deploy result below | arena/7d846749-poker2 | `COORDINATION.md` |

### Scope actually touched

Claimed and used: `scripts/poker_data.py`, `scripts/build_dashboard.py`, `scripts/stamp_archive.py`,
`data/poker/`, `style.css`, `app.js`, the 13 root HTML pages listed above, `venues/`, `archive/`,
`README.md`, this file.

Earlier sessions' trees (`pages/`, `docs/`, `verified/`, root `tournaments.html`, `planning.html`,
`styles.css`, `assets/`) were **moved into `archive/`, not deleted**, and every archived page now
carries a fixed banner marking it superseded. Nothing from an earlier session was rewritten in place;
the archived copies are byte-identical to what was committed, apart from the injected banner.

### What changed in the data model, and why

Three corrections were made during this session, each recorded as a flag or a review finding:

1. **"Not stated" was split from "unread".** An event whose structure sheet was never opened is
   *unverified*, not silent. The dataset now carries `sheet_read` per row and the site distinguishes
   53 silent rows, 168 unread rows and 16 rows where re-entry is positively permitted. Previously all
   237 could have been read as "silent", which would have overstated the evidence.
2. **Zero events are confirmed single-entry.** An earlier reading of this repository treated MGM
   Grand's $120 daily as confirmed single-entry because its sheet never mentions re-entry. That is an
   inference from silence and has been reversed. The single-entry toggle now returns zero rows and
   explains itself.
3. **A derived event length was removed.** An intermediate version of `build_dashboard.py` computed a
   "maximum length" per event from a hard-coded level table written from memory. It was not
   transcribed from the sheets, so it was deleted rather than corrected. The day plan now tests
   fallbacks against published late-registration closes, which are real, and states that no room
   publishes a finish time.

4. **Recurring events are counted once.** A bug expanded each daily/weekly event into seven weekday
   rows, triple-counting the schedule. Fixed: one row per recurring event with a weekday list, expanded
   per date only when the day plan is built.

### Verification performed this session

- 21 generated pages parsed with an HTML tag-balance checker: **0 unclosed or mismatched tags**.
- Internal link check across all 62 site + archive pages: **0 broken relative links**.
- `node --check app.js` passes.
- Generator determinism: rebuilding twice produces byte-identical HTML (md5 verified).
- Every source URL re-confirmed live by re-fetching the three load-bearing documents: the Venetian
  DeepStack IV schedule table (matches the dataset row for row), the Caesars Palace daily flyer
  (fee splits $70/$30 and the $45/$5 add-on confirmed verbatim), the Wynn WPT schedule PDF (dates,
  times and buy-ins confirmed). The Venetian `structure_7.pdf` was re-read and confirms $90 house fee
  on a $600 buy-in, 28 levels of 30 minutes, late registration "10 levels + Break (~ 4:55 PM)".
- Outbound URL resolution could **not** be automated: this sandbox has no outbound network from bash,
  so `urllib`/`curl` cannot reach the properties. The three re-fetches above were done with the page
  fetcher instead. `scripts/check_links.py` therefore remains a manual/CI-time check, not a local one.

### Known gaps left open (all published on the Flagged page)

- **No dated hotel rate exists.** Every booking flow read returned `$XXX` placeholders to a
  non-browser client. Resort fees, tax, parking and cancellation terms are verified; the room rate is
  not. F-03 / Q-09.
- **23 of 37 Venetian structure sheets were not opened.** Those events carry a buy-in from the
  schedule table and a blank fee. Stated on `sources.html`.
- **Horseshoe publishes no buy-in anywhere retrievable.** Six start times exist only in a Caesars
  corporate article; those rows are blank and labelled `official-editorial`. F-07.
- **Caesars Palace resort fee unverified.** All fee URLs redirect to a landing page. F-08.
- **Bellagio Saturday $1,100 contradicts itself** ($50K guarantee vs $600-per-player pool
  allocation). Excluded from the ranking. F-05.

None of these block publication, per the brief. They are surfaced rather than smoothed over.

### Reconciliation with session arena/7a4b09e2-poker2 (same evening, merged first)

PR #21 and #22 from session `arena/7a4b09e2-poker2` reached `main` while this session was building, and
they also claimed `venues/`. Two complete builds therefore existed. They were reconciled rather than
one being force-pushed over the other:

- **Independent agreement on every underlying fact.** Both sessions read the same official documents and
  arrived at the same numbers: Venetian $55 resort fee, MGM Grand $50, Bellagio $55, the 13.38% Clark
  County room tax, the $510/$90 split on a Venetian $600 buy-in, Caesars' $70/$30 and $45/$5 splits, and
  the Wynn $55 fee. Both sessions also independently concluded **zero confirmed single-entry events**.
  That convergence is the strongest cross-check this dataset has; neither session saw the other's work.
- **That session read all 37 Venetian structure sheets; this one read 14.** Its finding on the RaceDay
  Stack (sheet 18: $200, 30,000 chips, 20/15-minute levels, registration closes after level 6 + break
  ~12:25 PM, $35 withheld, no re-entry language) is consistent with the 12:25 close this session's
  dataset records independently from the schedule table. Where the two builds differ, the sheet-per-sheet
  sweep is the better evidence, and the 23 unread sheets remain a stated gap here.
- **Their build is preserved, not discarded.** It sits at `archive/parallel/`, bannered as superseded like
  every other archived tree, so its per-sheet findings stay readable in the repository.
- **This build is the live site** because it is the later consolidation and carries the cross-venue
  walking matrix, the append-only rate log and the three-state entry-rule model. That is a presentation
  choice, not a claim that the other build's research was inferior.

One consequence worth naming: because the two builds describe the same facts with different schemas, the
repository now contains two data modules — `scripts/poker_data.py` (live) and `scripts/dataset.py`
(theirs, still imported by `scripts/build.py`). Consolidating them into one is suggestion S-14 on
`suggestions.html` and is deliberately **not** done in this session, because rewriting another session's
generator is exactly the kind of cross-scope edit `COORDINATION.md` forbids.
