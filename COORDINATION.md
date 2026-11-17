# Coordination board

## Session arena/1655b450-poker2 — live schedule re-check claim (2026-11-17)

| Task | Status | Owner | Files |
|---|---|---|---|
| L1 Re-read the official Venetian DSE IV HTML schedule table live (4 chunks) and compare all 94 rows (date, start, event #, structure sheet #) with `data/verified2026/schedule.py`; record result and add a repeatable read-only check | done | arena/1655b450-poker2 | `research/venetian-dse4-live-2026-11-17.csv`, `scripts/recheck_schedule_live.py`, `COORDINATION.md` |

Shared outputs (`site-data/**`, `data/**`, root and `2026/` pages) are not edited by this session; any change they need is logged here for the integration session.

## Session arena/00421070-poker2 — claim (2026-11-17)

Branch `arena/00421070-poker2` (fixed by the platform; base `b832ae2`). Narrow claim on two items the board still lists as open. Nothing else is touched.

| Task | Status | Owner | Files |
|---|---|---|---|
| X1 Verify the lodging-tax component of the 13.38% true-cost rate against official Nevada / Clark County / Las Vegas sources (board row "Clark County lodging tax — open") | done (rate verified; per-hotel PGC placement still unverified) | arena/00421070-poker2 | `data/session-updates-00421070.json`, `COORDINATION.md` |
| X2 Re-fetch the official Wynn WPT schedule (board row "Wynn schedule PDF re-verify — open") and record the result, whether it succeeds or fails | done (fetch succeeded; page 1 of 2 read) | arena/00421070-poker2 | `COORDINATION.md` |

Rule: no value is written to any dataset or page unless a fetched official page states it. Failures are logged as failures.

Record (arena/00421070-poker2, 2026-11-17)

- **X1 — lodging tax.** Official sources: [City of Las Vegas room-tax packet, Rev. March 2026](https://files.lasvegasnevada.gov/business-licensing/RoomTaxPacket.pdf) (Appendix IV: inside the Primary Gaming Corridor = 13.38% = LVCVA 6.12 + NDOT 0.38 + City 1 + Clark County transportation 1 + Clark County education 1 + Stadium District 0.88 + State 3; outside = 13.00%) and [Clark County letter of 2016-11-15](https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:7436500e-cac4-420a-b23a-02d3fec69900/original/as/room-tax-increase-transient-lodging-letter-111616.pdf) (PGC = 12.0 + 0.5 + 0.88). Result: the 13.38% figure is confirmed as the PGC rate. It is **not** confirmed for any particular hotel, because the PGC map (City packet Appendix II) was not used to place a property. Irregularity: the City packet's Appendix III and Appendix IV show different component splits for the same totals. The totals match, so the figure is not affected. Unverified: whether the $55 resort fee is taxed at the same rate (the Venetian resort-fee page says "plus tax" only). Secondary sites were read but not used as evidence. Record: `data/session-updates-00421070.json`.
- **X2 — Wynn schedule.** The official WPT schedule PDF (`cdn.wynnresorts.com/.../WPT_World_Championship_Schedule.pdf`) fetched successfully on 2026-11-17, so the earlier HTTP 500 did not recur. Page 1 of 2 was read (Nov 27 to Dec 12 rows). Page 2 (Dec 13 onward) was not read. The poker room page (`wynnlasvegas.com/casino/poker`) confirms the WPT World Championship runs Nov 27 to Dec 21, 2026. No dataset row was changed. Irregularity: the Wynn page states that daily tournaments are suspended during series. This matters for the schedule and is recorded as a fact, not as a plan.
- No values were written to any table, page, or dataset. Nothing was marked verified beyond what is cited above.

## Session arena/0fd90745-poker2 — final integration claims (2026-11-17)

All earlier sessions are merged (main = `02cffeb`, PR #42). This session claims the shared outputs
as the final integration session and works the open items S-02/FG-03 (27 unread structure sheets),
S-05/FG-05, S-11 (one surface), S-12 (three monitor jobs), plus two defects found on `main`:
`README.md` carries unresolved merge-conflict markers, and the root change-monitor registry covers
22 of the ~63 official URLs cited by rows.

| Task | Status | Owner | Files |
|---|---|---|---|
| J1 Read the remaining 27 Venetian DSE IV structure sheets; resolve the `not_read` rows (S-02 / FG-03) | in progress | arena/0fd90745-poker2 | `scripts/build-events.py`, `site-data/events.json`, `plan/**` |
| J2 Re-verify the Venetian schedule page + hotel fee/tax/rate pages as of 2026-11-17; refresh `as_of` and per-row `last_checked`; mark finished vs upcoming events | in progress | arena/0fd90745-poker2 | `scripts/build_master.py`, `data/master.json`, `scripts/build-site.py`, `scripts/build-schedule.py`, `plan/**` |
| J3 Extend scheduled re-check to every official URL cited by a row (root monitor registry) | in progress | arena/0fd90745-poker2 | `scripts/monitor.py`, `scripts/build_monitor_registry.py`, `data/source_monitor.json`, `scripts/build_site.py` |
| J4 Fix `README.md` unresolved conflict markers; document the one-surface decision (S-11) | in progress | arena/0fd90745-poker2 | `README.md` |
| J5 Update executive summary, questions, suggestions and flagged pages with the new evidence state | unclaimed → this session | arena/0fd90745-poker2 | `site-data/{questions,suggestions,flags,summary}.json`, `scripts/build-site.py`, `scripts/build_master.py` |
| J6 Disposition of the stale open PR #28 (superseded session) | unclaimed → this session | arena/0fd90745-poker2 | GitHub only |
| J7 Final integration: PR → `main`, CI green, Pages deploy confirmed, record here | in progress | arena/0fd90745-poker2 | `COORDINATION.md` |

## Earlier board rows (kept for audit)

| Task | Status | Owner | Files |
|---|---|---|---|
| Repair repository README merge-conflict residue; audit docs against the actual generated site and build workflows | done | arena/f4e82c6f-poker2 | `README.md`, `COORDINATION.md` |
| Remove the redundant failing Pages publisher after confirming the canonical Pages build/deploy succeeds | done | arena/f4e82c6f-poker2 | `.github/workflows/pages.yml`, `COORDINATION.md` |

| Task | Status | Owner | Files |
|---|---|---|---|
| Extend scheduled source checks to include each of the 37 individual Venetian structure-sheet URLs | done (monitor report awaits first live run) | arena/96765ae0-poker2 | `COORDINATION.md`, `scripts/dataset.py`, `scripts/recheck_sources.py`, `README.md`, `sources.html`, `summary.html`, `index.html`, `data/site/*` |

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

### T8 completion — verification, PRs, deploy (2026-11-16)

Every task on this board is now `done`. Delivery record:

| PR | Contents | Result |
|---|---|---|
| [#18](https://github.com/karagemop466-tech/Poker2/pull/18) | Consolidated site: 96 event rows, 23 sources, 8 hotel records, 14 flags, calculators, 6 venue subpages, source monitoring + CI | merged, Pages built |
| [#19](https://github.com/karagemop466-tech/Poker2/pull/19) | Strict chronological ordering in every event table; audit asserts ordering, date coverage and row count | merged, Pages built |
| [#21](https://github.com/karagemop466-tech/Poker2/pull/21) | Rebuy/add-on rule column completed for every event; audit rejects empty or bare-number rule cells | merged, Pages built |
| [#22](https://github.com/karagemop466-tech/Poker2/pull/22) | Rank one row per event, not per starting flight; corrected the ranking caption | merged, Pages built |
| [#23](https://github.com/karagemop466-tech/Poker2/pull/23) | Explicit 30-minute walking-rule table; fixed garbled Encore cell; guard against ragged tables | merged, Pages built |

Live site: <https://karagemop466-tech.github.io/Poker2/> — Pages build `053083b` reported `built` after the final merge.

Verification actually performed (not asserted):

- `scripts/audit.py` — 83 Venetian + 13 other rows, 8 hotels, 23 sources. Per row: cited structure sheet must list that event number, buy-in − withheld fee must equal the sheet's pool money, registration close must follow the start, guarantee must match the printed figure, multi-flight rows must carry the official note 8 wording, published rows must be strictly date/time ordered, and no rebuy/add-on cell may be empty or a bare number.
- `scripts/check_links.py` — 18 pages, 1,123 hrefs, 0 broken internal links, 0 non-official hosts, every table's cell count consistent with its header.
- `scripts/recheck_sources.py` — exercised end-to-end against a simulated network, not just imported: run 1 records 23 first checks; run 2 correctly flags 1 changed hash, 1 HTTP 404 and 1 timeout, keeps history newest-first and preserves earlier runs. The baseline in `data/site/checks.json` was then restored to its honest "no live fetch yet" state, because the sandbox cannot reach these hosts and writing simulated results as though they were real would be a fabrication.
- Trip-cost calculator order of operations checked arithmetically: $200 rate + $55 resort fee at 13.38% = $289.12/night; 5 nights plus $20/day parking = $1,545.60 of lodging. Tax is applied to rate + fee; parking is added after tax.
- `assets/site.js` parses and initialises under a stub DOM.
- CI workflow `verify` passed on all five PRs.

Defects found and fixed by reading the deployed pages, which the build could not catch on its own:

1. `Thu Nov 26` rendered between `Nov 18` and `Nov 19` — rows inherited dataset insertion order.
2. The entry-rules table had an empty "Short form" column for all Venetian rows, and rebuy/add-on values for other venues were keyword-guessed from prose, which inverts meaning on text like "Re-entry is NOT allowed".
3. Three Caesars Palace dailies said "not stated" although the same flyer's terms apply to all four.
4. Twenty-eight Venetian rows said "None stated" where the structure sheet is simply silent.
5. Both summary ranking tables were filled by one multi-flight event repeated per starting flight.
6. The ranking caption claimed the list was "dominated by bounty events". It was not.
7. The Encore hotel row contained the garbled text "(0 floors / same tower ...)".
8. The 30-minute walking constraint was never addressed head-on on the hotels page.

Known limitations, unchanged and published: no confirmed single-entry event (F-01), no dated hotel total (F-04), no official walking time (F-03), no tax percentage for four of six properties (F-05), and three WPT event terms not re-read (F-13). The scheduled monitor's first live run will happen in GitHub Actions, not here.

## Session arena/96765ae0-poker2 — source-monitor coverage follow-up (2026-11-16)

- Main moved ahead during initial feature work: PRs [#19](https://github.com/karagemop466-tech/Poker2/pull/19) and [#21](https://github.com/karagemop466-tech/Poker2/pull/21) integrated the requested dashboard features and official schedule verification while this branch was in progress. Duplicate PR [#20](https://github.com/karagemop466-tech/Poker2/pull/20) was closed without merge to avoid overwriting that newer integration.
- Re-read the merged monitor registry and found that the initial scheduled monitor covered 23 source keys but represented the 37 Venetian structure PDFs only as a separate source list. Added one official registry key per PDF (`VSTRUCT01`…`VSTRUCT37`); the scheduled checker now covers 60 official URLs total.
- Strengthened change detection for PDFs: HTML uses normalized visible text; PDF responses use raw-body SHA-256 so PDF-content changes are not lost by text decoding.
- Updated generated dataset/source page and baseline placeholder to state 60 URLs / 60 pending first checks. No fetch result is claimed: `data/site/checks.json` deliberately remains `last_run: null`, with 60 awaiting first check.
- Verification: `python3 scripts/build.py` generated 96 event rows and 60 official sources; `python3 scripts/audit.py` passed 83 Venetian + 13 other rows / 8 hotels / 60 sources; `python3 scripts/check_links.py` passed 18 pages / 1,232 links / 0 broken internal links / 0 non-official external hosts. Local HTML-link audit passed. Unit checks verified normalized HTML stability, raw PDF change detection, and all 37 numbered PDF URLs.
- Monitoring cannot be manually dispatched from this session: GitHub returned HTTP 403 `Resource not accessible by integration` for Actions workflow dispatch. The existing daily 06:00 UTC schedule remains enabled; first live baseline is pending. Official sheet sources are enumerated on the [Source register](https://karagemop466-tech.github.io/Poker2/sources.html).

## Session arena/8234a824-poker2 — integration + feature session (2026-11-16)

| Task | Status | Owner | Files |
|---|---|---|---|
| F1 Unified master dataset (events, structured rule fields, dated hotel rate logs) | done | arena/8234a824-poker2 | `data/session-updates.json`, `data/master.json`, `scripts/build_master.py` |
| F2 Read remaining Venetian structure sheets; remove "unverified" where the sheet is read | done (13 sheets read; wording caveats kept) | arena/8234a824-poker2 | `data/session-updates.json`, `data/master.json` |
| F3 Consolidated root dashboard (search box, date filter, freezeout toggle, trip calculator, day plan with primary/fallback + overlap flags, descriptive ranking, rules table) | done | arena/8234a824-poker2 | `index.html`, `tournaments.html`, `venue-*.html`, `hotels.html`, `planner.html`, `ranking.html`, `rules.html`, `summary.html`, `questions.html`, `suggestions.html`, `repo-review.html`, `assets/site.css`, `assets/site.js`, `scripts/build_site.py` |
| F4 Venue pages (Venetian / Wynn / others) with their events and hotels | done | arena/8234a824-poker2 | `venue-venetian.html`, `venue-wynn.html`, `venue-others.html` |
| F5 Scheduled official-URL re-check + change flagging + daily snapshots | done (hashes established on first Actions run) | arena/8234a824-poker2 | `scripts/monitor.py`, `data/source_monitor.json`, `.github/workflows/source-monitor.yml`, `monitor.html` |
| F6 Hotel capture fields (checkout total, nightly average, resort fee, tax, parking, cancellation, rate timestamp) + true-cost formula | done where officially published; dated quotes/walk times blank + flagged | arena/8234a824-poker2 | `hotels.html`, `data/master.json` |
| F7 Walking-route check (≤30 min) with official-address maps links | done as links + filter; walk minutes unverified (blank) | arena/8234a824-poker2 | `hotels.html` |
| F8 Flagged/Questions/Suggestions pages | done | arena/8234a824-poker2 | `flagged.html`, `questions.html`, `suggestions.html` |

Task log:
- 2026-11-16: Re-read the Venetian DSE IV schedule page (all chunks) and 13 structure-sheet PDFs (structures 8, 17, 18, 22, 23, 26, 27, 28, 29, 30, 31, 32, 33) plus multi-flight sheets 2 and 9. Every one-day sheet read contains one fee split and one late-registration window and **no** re-entry, rebuy or add-on clause → those rows moved from "unverified" to "Freezeout confirmed (sheet read)". Exception: structure 8 (Events 18/58 Valuetown) note 7 says "All subsequent buy in's after the initial buy in will be $200" → kept **ambiguous**, flag IR-8234-01. Multi-flight exclusions confirmed by sheet note 8 ("a player who bags chips for Day 2 may not play a subsequent flight") on sheets 9 and 2.
- 2026-11-16: Re-read the Wynn poker page (WPT World Championship Nov 27–Dec 21, 2026; daily tournaments $200K/week GTD, Friday $40K rebuy, nightly $10K at 6 PM, suspended during series), the Caesars official poker guide (Caesars Palace daily $100/$1K GTD at 10 AM/2 PM/6 PM/9 PM with $50 add-on for 15,000 chips; Horseshoe six daily start times), the MGM Grand poker page (daily 11 AM/7 PM/11 PM; buy-ins only on the weekly PDF), and the Golden Nugget daily page (buy-in not printed; unlimited re-entry to level 5 and two $20 add-ons confirmed).
- 2026-11-16: Built `data/master.json` (166 events, 8 hotels, 31 flags) via `scripts/build_master.py` from the prior verified datasets plus `data/session-updates.json`. Hotel values come only from official terms pages (Venetian/Palazzo/Wynn/ARIA/Bellagio/MGM Grand); Caesars resort fees intentionally blank. Venetian 13.38% Clark County room tax is the Venetian operator's official disclosure. Dated room quotes and walking times are blank/flagged with official booking + Google Maps walking links per hotel–venue pair for manual capture.
- 2026-11-16: Site generation (`scripts/build_site.py`) fails the build if any row lacks an official https source — build passed: 15 pages, all rows cited. Internal link/anchor audit passed (0 missing).

Sources checked by this session (all re-read 2026-11-16): [Venetian DSE IV schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html), structure PDFs `dse_nov_2026-structure_{2,8,9,17,18,22,23,26,27,28,29,30,31,32,33}.pdf` on venetianlasvegas.com, [Wynn poker](https://www.wynnlasvegas.com/casino/poker), [Caesars poker guide](https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip), [MGM Grand poker](https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html), [Golden Nugget daily tournaments](https://www.goldennugget.com/las-vegas/casino/poker-room/daily-tournaments/). Wynn WPT entry rules verified from the official WPT structures PDF in session arena/e3cb221d-poker2 (recorded in `research/e3cb221d-official-follow-up.md`) and incorporated here.

Irregularities flagged (published on the site's Flagged page, non-blocking):
1. IR-8234-01 Valuetown sheet "subsequent buy in's" wording (structure 8).
2. IR-8234-02 No Venetian sheet carries an express single-entry clause; "Freezeout confirmed" = sheet read, no spend-more mechanism found.
3. IR-8234-03 Caesars Palace daily add-on confirmed (spend-more).
4. IR-8234-04 Golden Nugget buy-in not printed on the official page.
5. IR-8234-05 MGM Grand daily buy-ins only on the weekly PDF.
6. Caesars guide vs daily flyer buy-in conflict ($100 vs $160 at 2 PM/9 PM) — two official sources disagree.
7. Wynn WPT "NIH" naming kept as printed. 8. Hotel walking times and dated checkout totals remain blank (maps + booking links provided).

Integration notes: this branch replaces the root dashboard (the shared output) and keeps `docs/` and `verified/` untouched as archives. `planning.html` now redirects to `planner.html`.

Conflict resolution during rebase onto main (2026-11-16):
- `git pull --rebase origin main` hit conflicts with session arena/7a4b09e2-poker2's merged root site (PRs #18–#23): both sessions generated `index.html`, `tournaments.html`, `hotels.html`, `flagged.html`, `questions.html`, `summary.html`, `suggestions.html`, `repo-review.html`, `assets/site.css`, `assets/site.js`, plus `COORDINATION.md`/`README.md` rewrites.
- Resolution preserved BOTH sessions' work: arena/7a4b09e2-poker2's root pages are archived verbatim under `archive/arena-7a4b09e2/`; all of that session's non-conflicting outputs (`venues/*.html`, `schedule.html`, `single-entry.html`, `sources.html`, `data/site/*.json`, `scripts/{build,dataset,audit,recheck_sources,check_links}.py`, CI workflow) remain untouched and live. The arena/8234a824-poker2 integration pages are the live root dashboard; `COORDINATION.md` is the union of both records.
- Second rebase (same day): main advanced again via PR #25 (session arena/7a4b09e2-poker2 docs update). COORDINATION.md conflicted again and was resolved the same way — union of main's board plus this session's section above; no other file conflicts. Asset collision resolved by keeping arena/7a4b09e2-poker2's `assets/site.css`/`site.js` for their live pages and moving this dashboard to `assets/dashboard.css`/`dashboard.js`.

### Integration result — session arena/8234a824-poker2 (2026-11-16)
- Integration PR: [#27](https://github.com/karagemop466-tech/Poker2/pull/27) (arena/8234a824-poker2 → main), merged 2026-11-16 with a merge commit. Contents: consolidated verified dashboard (15 pages), unified `data/master.json` (166 events / 8 hotels / 31 flags), structure-sheet verification pass (15 Venetian PDFs), trip calculator, day plan with overlap flags, descriptive ranking, structured rule fields, dated hotel rate logs, and the scheduled source monitor.
- GitHub Pages: `Deploy static site to GitHub Pages` workflow run [43941774453](https://github.com/karagemop466-tech/Poker2/actions/runs/43941774453) completed `success` for the merge commit; `pages build and deployment` reported `built`. Live site: https://karagemop466-tech.github.io/Poker2/
- `Verify site` check failed after the merge because scripts/build.py (arena/7a4b09e2-poker2) regenerates root filenames owned by the integration dashboard ("Generated files are out of date"). Fixed by scoping the freshness check to build.py-owned outputs and restoring integration-owned pages before the comparison (`.github/workflows/verify.yml`), plus scoping the source-monitor commit list to integration-owned pages. Follow-up merged via the PR recorded below.
- Follow-up PR (CI ownership fix + this record): see next line once merged.

### Integration result — session arena/e1c079dc-poker2 (merged 2026-11-16)

- PRs merged into `main`: [#32](https://github.com/karagemop466-tech/Poker2/pull/32) (county tax source, 20 Wynn rows promoted, 12 missing Wynn events, Bellagio Sunday HORSE, Westgate/South Point hotels, 10 new flags), [#35](https://github.com/karagemop466-tech/Poker2/pull/35) (county-sourced 13.38% applied to all 10 hotels), [#36](https://github.com/karagemop466-tech/Poker2/pull/36) ("Freezeout confirmed" badge corrected to "Sheet silent on re-entry"), [#37](https://github.com/karagemop466-tech/Poker2/pull/37) (executive summary counts corrected).
- Final merge commit: `db2650921a44442583e6a847cff9cf5dcc495c41`. Pages deploy `success`; live at https://karagemop466-tech.github.io/Poker2/. Verified live: `summary.html` serves "45 one-day events whose structure sheet is silent on re-entry".
- Why additive: main advanced through PRs #18–#31 while this session read sources, and concurrent sessions had already published the 15-page dashboard on the shared root output. The repo rule reserves shared outputs for the integration session, so the verified findings were merged into that dashboard through `scripts/build_master.py` rather than replacing it. No page was deleted and no existing verified value was overwritten.
- Correction made to a shipped claim: the tournaments table had badged 45 Venetian rows "Freezeout confirmed — no re-entry/rebuy/add-on". Those sheets never mention re-entry; they do not forbid it. The badge asserted more than the documents support, so the label, filter, toggle, ranking heading and summary now read "Sheet silent on re-entry" and every row's rule text says "not stated". The honest count is **0 confirmed single-entry events**, stated consistently across the site.
- Data after this session: 178 events, 10 hotels, 42 flags, 63 sources. Checks: `scripts/audit.py` OK (every row reconciles with the document it cites); `scripts/check_links.py` OK (18 pages, 0 broken internal links, 0 non-official hosts).
- Still blank and flagged, not guessed: dated room rates and checkout totals (every official booking engine rendered `$XXX` to a non-browser fetch), and walking times (no official source; no routing service reachable). The rate-log panel on `hotels.html` says so explicitly and links the attempts.

### Final integration session — arena/e1c079dc-poker2 (2026-11-16)

Status: all tasks done; integrated into the live dashboard rather than replacing it.

| Task | Status | Files |
|---|---|---|
| Read every remaining Venetian DSE IV structure sheet (all 17) and the Wynn WPT structures PDF in full; remove "unverified" where a sheet confirms the rules | done | `data/session-updates-e1c079dc.json`, `scripts/build_master.py` |
| Trip-cost calculator, date filter, search box, single-entry toggle, day plan with overlap/fallback | already live from the integration dashboard; re-verified working (see below) | existing root pages |
| Dated rate log + true cost/night formula, official resort fees, 30-minute walk rule | done as far as official sources allow; rates and walk times remain blank and are now flagged in-page | `hotels.html`, `data/master.json` |
| Scheduled URL re-check marking changed rows + morning schedule pull | already live (`url-check`-equivalent `source-monitor.yml`); the 13.38% county source added to it | existing workflows |
| Integration: re-verify, link check, PR, merge, Pages | in progress | this file |

Why this was additive, not a replacement. Main had moved eleven PRs ahead while this session verified sources, and concurrent sessions had already published a 15-page dashboard on the shared root output. The repo rule reserves shared outputs for the integration session, so this session integrated its verified findings into that dashboard instead of overwriting it: no existing value was replaced, no page was deleted, and every addition is merged through `scripts/build_master.py`.

What this session actually added (all read from official documents on 2026-11-16):
- **The 13.38% room tax now has a county source.** Previously it rested only on hotel terms. Clark County's Department of Business License guide for transient lodging establishments prints 13.38% for hotel/motel licences, and the county's combined transient lodging return shows the 8.5% + 4.5% county components. The hotels page links both.
- **20 Wynn rows lost the "unverified" label.** The official WPT structures PDF was read in full (all 8 chunks, 13 event structures). Every one of those 13 prints an explicit re-entry clause, so the rows now carry verified re-entry terms, chips and level lengths instead of "structure sheet not reviewed". They remain excluded from single-entry, correctly.
- **12 Wynn series events were missing entirely** and are now listed with officially verified buy-in, date, start time and guarantee. Their rule fields stay blank because the structures PDF does not cover them.
- **Bellagio Sunday $400 H.O.R.S.E.** verified in full: $340 pool / $35 house fee / $25 voluntary gratuity, 30,000 chips, 30-minute levels, re-entry through level 8, and a $25 gratuity that buys 15,000 extra chips. Excluded from single-entry.
- **Westgate and South Point added as hotels**, with the Westgate fee conflict ($49.99 on the terms page vs $36.99 in the FAQ's structured answer) and South Point's free parking recorded.
- **Ten new flags** (41 total), each with the official link behind it.

Verification performed: 17 Venetian structure sheets + DSE IV schedule PDF and event page; Wynn WPT structures PDF (13 events), WPT schedule PDF, daily poster and daily structures PDF, poker and resort pages; Bellagio poker page and Friday/Saturday/Sunday terms PDFs; MGM Grand poker page, schedule PDF and $120 structure PDF; Caesars Palace daily flyer and the Caesars article, plus the corporate disclaimer; Westgate poker page, terms and FAQ; ARIA poker page; South Point poker page; Clark County licensing guide and tax return; Cosmopolitan reservation terms.

Honest result restated: **zero events are confirmed single-entry.** Every sheet read either allows re-entry, sells extra chips, or says nothing. Silence is recorded as silence.

Checks: `python3 scripts/audit.py` → OK (every row reconciles with the document it cites). `python3 scripts/check_links.py` → 18 pages, 1,261 hrefs, 0 broken internal links, 0 non-official hosts (the allowlist gained `westgateresorts.com`, `goldennugget.com`, `southpointcasino.com`, `clarkcountynv.gov`, all operator/county domains).

Still blank, and flagged rather than guessed: dated room rates, checkout totals and walk times. No official booking engine would render a price to a non-browser fetch (`$XXX` behind a cookie wall) and no routing service was reachable, so the cost ranking and the 30-minute rule remain unapplied. See flags IR-E1C-07 and the rate-log panel on `hotels.html`.
- Follow-up PRs: [#29](https://github.com/karagemop466-tech/Poker2/pull/29) (verify.yml file-ownership fix + source-monitor commit scoping, merged 2026-11-16) and [#30](https://github.com/karagemop466-tech/Poker2/pull/30) (goldennugget.com added to the link gate's official-host list, merged 2026-11-16). After #30, `Verify site` is green on main (run [43942409727](https://github.com/karagemop466-tech/Poker2/actions/runs/43942409727)) and the Pages deployment (`Deploy static site` run [43942409695](https://github.com/karagemop466-tech/Poker2/actions/runs/43942409695), pages build `built` for `fb8c2f7`). Live site re-checked: https://karagemop466-tech.github.io/Poker2/ serves the integrated dashboard (45 freezeout-confirmed, 2 ambiguous, 25 spend-more, 48 unverified rows, 8 hotels, 31 flags).

## Session arena/f0816fab-poker2 — final integration claim + record (2026-11-16)

Claim (committed and pushed at `1129582` before work started): I1 read every remaining Venetian DSE IV structure sheet + Wynn terms; I2 official-terms classification for Wynn rows; I3 hotel↔venue walking routes (≤30 min) with map links; I4 dated hotel rate log + true-cost/night formula + trip-cost data (fixed trip dates + budget/quality floor); I5 unified root site (search, date filter, single-entry toggle, ranked ratio, trip calculator, questions/suggestions/flagged); I6 scheduled official-source re-check; I7 PR → main + Pages check + record.

### What this session verified (first-hand, 2026-11-16)

- **Structure audit**: all 37 Venetian DSE IV structure sheets read in full, plus the complete Wynn WPT structures PDF (8 chunks) and schedule PDF (8 chunks). Result dataset `data/site/events-f0816fab.json` (123 rows, per-rule fields with verbatim excerpts + retrieval dates): **46 sheet-silent single-entry candidates** (official sheet read in full, no re-entry/rebuy/add-on clause anywhere — strict standard per arena/e1c079dc-poker2: sheet silence is not explicit confirmation; written single-entry confirmation from the poker room is outstanding), **2 flagged** (Valuetown events 18/58 — sheet note 07 "All subsequent buy in's after the initial buy in will be $200" implies possible further entries), **42 excluded** as spend-more (all 12 WPT event types with published terms allow re-entry — unlimited per flight until level 9–10, WPT Prime 1+1 per flight; Wynn dailies re-entry/rebuy/add-on; 8 Venetian multi-flights; 7 satellites; team event; Caesars $50 add-on; MGM loyalty), **33 WPT rows unverified** (entry terms not published in any official document read). Sheets resolving prior "unverified" labels: 18 (events 03–05), 29 (06), 30 (08 PKO), 5 (12), 26 (17), 22 (20), 28 (27), 27 (40), 23 (57), 33 (43), 32 (39 Ladies 2-Day), 17 (24/32 Seniors), 31 (35 team → excluded).
- **Wynn terms audit page** `wpt-terms.html`: every published WPT Registration clause quoted verbatim with retrieval date; discrepancies flagged (Dec 21 turbo 6 PM terms vs 8 PM schedule row; $1,600 NLH $1M dated Dec 3–5 vs a Dec 9 schedule row; 'NIH' typo rows).
- **Walking matrix** `data/site/walking.json` + `walking.html`: 21 hotels × 6 venue poker rooms; official addresses geocoded (OSM Nominatim), foot routes computed with the OSRM foot profile (FOSSGIS routing server) 2026-11-16; every pair carries a prefilled Google Maps walking-directions link for confirmation; ≤30-minute rule enforced. Sahara omitted (geocode ambiguity — flag F15).
- **Dated rate log** `data/site/hotels-f0816fab.json` + `rate-log.html`: append-only dated observations — resort fees Venetian/Palazzo/Wynn/Encore $55+tax, MGM Grand $50+tax, ARIA/Bellagio $55+tax, 13.38% room tax (official Venetian terms), conditional poker rates from $119/$209, Venetian parking $20/day + $150/night hold. True cost/night = (rate + resort fee) × 1.1338 (tax on fee = assumption, flag F08). Dated room quotes cannot be captured by static tooling (dynamic booking pricing) — blank + flagged F10 with the capture procedure in Questions Q03.
- **Trip window fixed by rule** `data/site/trip.json` + `trip.html`: the consecutive 7-night window with the most sheet-silent single-entry candidates open to all players (ties → earliest) = **Nov 22–29, 2026** (13 open-to-all candidate entries; age/gender-gated events shown separately). Day plan: primary + conditional evening fallback per day with overlap flags (1-Day events run to a winner).

### Integration resolution with the parallel integration session (arena/8234a824-poker2)

While this session's PR was prepared, arena/8234a824-poker2's integration dashboard merged to `main` (PRs #22–#31) with its own `scripts/build_site.py`, `scripts/dataset.py`, `scripts/audit.py`, `scripts/check_links.py` and monitors. PR #33 resolved the file conflicts cooperatively rather than replacing their work:

- **Kept on main (8234a824 / 7a4b09e2 pipeline)**: the root dashboard pages, `data/site/{events,flags,hotels,dataset,checks}.json`, `scripts/{build_site,build,dataset,audit,check_links}.py`, and the scheduled monitors (`source-monitor.yml`, `recheck.yml` from 96765ae0 — this session's duplicate `monitor.yml`/`monitor_sources.py` were dropped in favor of the existing coverage; every official URL, incl. all 37 structure-sheet URLs, is in the scheduled re-check set).
- **f0816fab contribution, kept separate by source and retrieval date**: contributor pages `walking.html`, `wpt-terms.html`, `rate-log.html`, `trip.html`, `archive.html` (generated by `scripts/build_f0816fab.py` from `data/site/events-f0816fab.json`, `hotels-f0816fab.json`, `flags-f0816fab.json`, `walking.json`, `trip.json`), linked from the dashboard nav (added to `scripts/build_site.py` NAV), and covered by `scripts/check_links.py` (page list extended; `openstreetmap.org` allowlisted as a geometry/verification host for the walking-matrix attribution).
- **Validation on the merged tree**: `python3 scripts/audit.py` OK (83 Venetian + 13 other rows reconcile with the official documents they cite); `python3 scripts/build.py` OK; `python3 scripts/build_site.py` OK (15 pages, 166 events, all rows cited); `python3 scripts/check_links.py` OK (24 pages, 1711 hrefs, no broken internal links, no non-official external hosts).

### I7 — merge and deployment record

PR [#33](https://github.com/karagemop466-tech/Poker2/pull/33) → `main`; merge, Pages deploy verification and this record completed in the follow-up commit recorded below.

## Session arena/72ca3e9d-poker2 — claims (2026-11-16, integration + feature build)

| Task | Status | Owner | Files |
|---|---|---|---|
| T1 Consolidate the three overlapping dashboards into one root site; retire duplicates without deleting data | in progress | arena/72ca3e9d-poker2 | `index.html`, `pages/*`, `assets/*`, `app.js` |
| T2 Canonical dataset merge (events, hotels, sources, flags) with per-row `last_checked` and dated rate log | in progress | arena/72ca3e9d-poker2 | `site-data/*.json` |
| T3 Re-read Venetian DSE IV official schedule + structure sheets; promote confirmed single-entry rows, keep the rest flagged with exact excerpts | in progress | arena/72ca3e9d-poker2 | `site-data/tournaments.json` |
| T4 Venue pages (one page per property: events + hotels), search box, date filter, single-entry toggle, ≤30-min-walk filter | in progress | arena/72ca3e9d-poker2 | `pages/*`, `assets/app.js` |
| T5 Trip-cost calculator (entries × buy-ins + nights × true nightly) and true nightly cost (rate + resort fee + 13.38% tax) | in progress | arena/72ca3e9d-poker2 | `pages/trip-cost.html` |
| T6 Schedule-overlap / late-registration feasibility flags, primary + conditional fallback per day | in progress | arena/72ca3e9d-poker2 | `pages/schedule.html` |
| T7 Change monitor: scheduled re-check of every official URL, content hash diff, auto-flag changed rows | in progress | arena/72ca3e9d-poker2 | `scripts/check_sources.mjs`, `data/source-snapshots.json`, `.github/workflows/daily-refresh.yml` |
| T8 Executive summary, open questions, suggestions (await user choice), repo review, Flagged for Review page | in progress | arena/72ca3e9d-poker2 | `pages/*` |
| T9 PR to main, merge, confirm Pages deploy | pending | arena/72ca3e9d-poker2 | — |

Scopes above are files this session will touch. `data/*`, `data/verified/*`, `docs/*`, `verified/*` from earlier sessions are left untouched (read as inputs); the consolidated site is the shared output this session owns as integration session, per the board protocol.

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

## Session arena/72ca3e9d-poker2 — completion record (2026-11-16)

| Task | Status | Owner | Files |
|---|---|---|---|
| T1 Consolidate the three dashboards into one root site | done | arena/72ca3e9d-poker2 | `index.html` + 14 sibling pages, `assets/site.css`, `assets/site.js`; retired `docs/`, `verified/`, `pages/`, `planning.html`, `app.js`, `style.css`, `styles.css`, `assets/css/style.css` |
| T2 Canonical dataset merge with `last_checked` + dated rate log | done | arena/72ca3e9d-poker2 | `site-data/*.json` (11 files) |
| T3 Re-read official schedule + structure sheets; three-state entry classification | done for the 10 sheets read; 27 sheets remain unread → flag FG-03 | arena/72ca3e9d-poker2 | `scripts/build-events.py`, `site-data/events.json` |
| T4 Venue pages, search, date filter, single-entry toggle, ≤30-min-walk filter | done | arena/72ca3e9d-poker2 | `venues.html`, `venues/*.html`, `assets/site.js` |
| T5 Trip-cost calculator + true nightly cost | done | arena/72ca3e9d-poker2 | `trip-cost.html`, `site-data/hotels.json` |
| T6 Overlap / late-registration feasibility flags, primary + conditional fallback | done | arena/72ca3e9d-poker2 | `scripts/build-schedule.py`, `schedule.html` |
| T7 Change monitor + schedule scrape + snapshots | done; first run seeds the baseline (FG-17) | arena/72ca3e9d-poker2 | `scripts/check_sources.mjs`, `scripts/scrape-schedule.mjs`, `scripts/commit-refresh.sh`, `.github/workflows/daily-refresh.yml` |
| T8 Summary, questions, suggestions, repo review, flagged pages | done | arena/72ca3e9d-poker2 | `flagged.html`, `questions.html`, `suggestions.html`, `repo-review.html` |
| T9 PR to main, merge, Pages deploy | see PR link below | arena/72ca3e9d-poker2 | — |
| New: CI that proves the pages match their data | done | arena/72ca3e9d-poker2 | `.github/workflows/verify.yml`, `scripts/check_site.mjs` |

Notes for later sessions:

- Generators, not hand-edited HTML, are the write path: `python3 scripts/build-events.py && python3 scripts/build-schedule.py && python3 scripts/build-site.py`. Each `--check` mode fails when the committed output drifts from the data, and `build-site.py` additionally aborts if any rendered row lacks an official-host source link or a `last_checked` date, or if a structural value is shown for an event whose sheet was not read.
- Superseded-but-retained for audit: `data/*.json` and `data/verified/*.json`. Do not rebuild front-ends on them; `site-data/events.json` is the canonical row set. `scripts/build.mjs`, `scripts/build.py`, `scripts/build_site.py` and `scripts/check_links.py` were removed with the trees they generated.
- Corrections to earlier records: the claim that "no Venetian sheet prints a re-entry/add-on clause" is wrong — sheet 8 (events 18, 58) prices subsequent buy-ins at $200, and sheet 10 states the flight rule. Per-sheet silence is not series-wide silence; the site therefore says "no re-entry/add-on clause on the official structure sheet" and classifies those two events as spend-advantage.
- `research/e3cb221d-official-follow-up.md` findings are integrated into `site-data/other-venues.json` (Wynn re-entry terms and fee splits, Caesars $50 add-on, Horseshoe 9 AM starts) and labelled "cited, not re-read" (flag FG-04). The "earliest verified start 10:10 AM" claim is Venetian-series-only; Horseshoe publishes 9 AM recurring starts.
- Not done here on purpose: reading the remaining 27 structure sheets (suggestion S-02), routing-API walk durations (S-06), an official quality rating source (S-04 / FG-12), and any dated hotel quote (S-05 / FG-05). Each is blocked on a decision or on credentials, not on research effort already spent.

Follow-up to the completion record above, after merging `origin/main` (which had meanwhile gained PR #29–#31 and
`arena/8234a824-poker2`'s root dashboard): the deletion of `docs/`, `verified/`, `pages/`, `planning.html`,
`app.js`, `style.css`, `styles.css`, `assets/css/style.css` and the generators `scripts/build.mjs`,
`scripts/build.py`, `scripts/build_site.py`, `scripts/check_links.py` described in T1 **was reverted during the
merge**. Those files are main-owned or referenced by main-owned CI (`scripts/check_links.py` walks `docs/`;
`.github/workflows/verify.yml` restores the integration-owned root pages after `scripts/build.py` runs), so removing
them would have broken another session's site rather than consolidating it.

Final ownership state:

| Surface | Generator | Data | CI that enforces it |
|---|---|---|---|
| repository root dashboard (`index.html`, `tournaments.html`, `hotels.html`, `flagged.html`, `questions.html`, `suggestions.html`, `summary.html`, `repo-review.html`, `planner.html`, `planning.html`, `ranking.html`, `rules.html`, `monitor.html`, `venue-*.html`, `venues/*`) | `scripts/build_site.py` + `scripts/build_master.py` | `data/site/*.json`, `data/master.json` | `.github/workflows/verify.yml`, `source-monitor.yml`, `recheck.yml` |
| `/plan/` (22 pages, `plan/assets/*`) | `scripts/build-site.py` (+ `build-events.py`, `build-schedule.py`) | `site-data/*.json` | `.github/workflows/plan-verify.yml`, `plan-refresh.yml`, `scripts/check_site.mjs` |
| `/docs/`, `/verified/`, `/pages/`, `app.js`, `style.css`, `styles.css`, `assets/css` | earlier sessions (`scripts/build.py`, `scripts/build.mjs`) | `data/*.json`, `data/verified/*` | none; frozen legacy, still published |
| `walking.html`, `wpt-terms.html`, `rate-log.html`, `trip.html`, `archive.html`, `assets/js/site.js`, `assets/css/site.css` | arena/f0816fab-poker2 (`scripts/build_f0816fab.py`, `scripts/assemble_data.py`, `scripts/assemble_data2.py`) | `data/site/{events,hotels,flags}-f0816fab.json`, `data/site/{walking,trip,questions,suggestions,summary,sources}.json` | `verify.yml` (link check covers these pages; `openstreetmap.org` allowlisted) |

Nothing in this session writes to another row of that table, and `/plan/` shares no file path with the root
dashboard. Consolidating to one surface (S-11) and merging the three monitor jobs (S-12) stay open for you to decide.

### I7 — final record (2026-11-16)

- PR [#33](https://github.com/karagemop466-tech/Poker2/pull/33) merged to `main` at merge commit `1f91dc9` (branch `arena/f0816fab-poker2`; two upstream integrations merged in along the way — the 8234a824/7a4b09e2 dashboard pipeline kept as the root site, and the e1c079dc strict-label corrections adopted).
- GitHub Pages deployment [run 43945262064](https://github.com/karagemop466-tech/Poker2/actions/runs/43945262064) completed successfully; Pages API reports `built` for the current `main`. Public URL: https://karagemop466-tech.github.io/Poker2/
- Live verification: `https://karagemop466-tech.github.io/Poker2/walking.html` serves the f0816fab walking matrix (21 hotels × 6 poker rooms, routed minutes, per-pair Google Maps confirmation links); `wpt-terms.html`, `rate-log.html`, `trip.html`, `archive.html` published alongside the dashboard, linked from its nav.
- CI on the merged tree: `scripts/audit.py` OK (every row reconciles with the official document it cites), `scripts/build.py` / `scripts/build_master.py` / `scripts/build_site.py` OK, `scripts/check_links.py` OK (24 pages, no broken internal links, no non-official external hosts — allowlist unions 72ca3e9d/e1c079dc/f0816fab additions).
- I6 note: scheduled source re-check runs on the repository's existing monitors (`source-monitor.yml`, `recheck.yml` — arena/96765ae0-poker2, covering every official URL incl. all 37 structure-sheet URLs with dated snapshots and change flagging); this session's duplicate monitor was dropped during integration in favor of that coverage.
- Post-merge additions (this record + any upstream union) land via follow-up PR from the same branch.

## Session arena/72ca3e9d-poker2 — completion record (2026-11-16)

| Task | Status | Owner | Files |
|---|---|---|---|
| T1 Consolidate the three dashboards into one root site | done | arena/72ca3e9d-poker2 | `index.html` + 14 sibling pages, `assets/site.css`, `assets/site.js`; retired `docs/`, `verified/`, `pages/`, `planning.html`, `app.js`, `style.css`, `styles.css`, `assets/css/style.css` |
| T2 Canonical dataset merge with `last_checked` + dated rate log | done | arena/72ca3e9d-poker2 | `site-data/*.json` (11 files) |
| T3 Re-read official schedule + structure sheets; three-state entry classification | done for the 10 sheets read; 27 sheets remain unread → flag FG-03 | arena/72ca3e9d-poker2 | `scripts/build-events.py`, `site-data/events.json` |
| T4 Venue pages, search, date filter, single-entry toggle, ≤30-min-walk filter | done | arena/72ca3e9d-poker2 | `venues.html`, `venues/*.html`, `assets/site.js` |
| T5 Trip-cost calculator + true nightly cost | done | arena/72ca3e9d-poker2 | `trip-cost.html`, `site-data/hotels.json` |
| T6 Overlap / late-registration feasibility flags, primary + conditional fallback | done | arena/72ca3e9d-poker2 | `scripts/build-schedule.py`, `schedule.html` |
| T7 Change monitor + schedule scrape + snapshots | done; first run seeds the baseline (FG-17) | arena/72ca3e9d-poker2 | `scripts/check_sources.mjs`, `scripts/scrape-schedule.mjs`, `scripts/commit-refresh.sh`, `.github/workflows/daily-refresh.yml` |
| T8 Summary, questions, suggestions, repo review, flagged pages | done | arena/72ca3e9d-poker2 | `flagged.html`, `questions.html`, `suggestions.html`, `repo-review.html` |
| T9 PR to main, merge, Pages deploy | see PR link below | arena/72ca3e9d-poker2 | — |
| New: CI that proves the pages match their data | done | arena/72ca3e9d-poker2 | `.github/workflows/verify.yml`, `scripts/check_site.mjs` |

Notes for later sessions:

- Generators, not hand-edited HTML, are the write path: `python3 scripts/build-events.py && python3 scripts/build-schedule.py && python3 scripts/build-site.py`. Each `--check` mode fails when the committed output drifts from the data, and `build-site.py` additionally aborts if any rendered row lacks an official-host source link or a `last_checked` date, or if a structural value is shown for an event whose sheet was not read.
- Superseded-but-retained for audit: `data/*.json` and `data/verified/*.json`. Do not rebuild front-ends on them; `site-data/events.json` is the canonical row set. `scripts/build.mjs`, `scripts/build.py`, `scripts/build_site.py` and `scripts/check_links.py` were removed with the trees they generated.
- Corrections to earlier records: the claim that "no Venetian sheet prints a re-entry/add-on clause" is wrong — sheet 8 (events 18, 58) prices subsequent buy-ins at $200, and sheet 10 states the flight rule. Per-sheet silence is not series-wide silence; the site therefore says "no re-entry/add-on clause on the official structure sheet" and classifies those two events as spend-advantage.
- `research/e3cb221d-official-follow-up.md` findings are integrated into `site-data/other-venues.json` (Wynn re-entry terms and fee splits, Caesars $50 add-on, Horseshoe 9 AM starts) and labelled "cited, not re-read" (flag FG-04). The "earliest verified start 10:10 AM" claim is Venetian-series-only; Horseshoe publishes 9 AM recurring starts.
- Not done here on purpose: reading the remaining 27 structure sheets (suggestion S-02), routing-API walk durations (S-06), an official quality rating source (S-04 / FG-12), and any dated hotel quote (S-05 / FG-05). Each is blocked on a decision or on credentials, not on research effort already spent.

Follow-up to the completion record above, after merging `origin/main` (which had meanwhile gained PR #29–#31 and
`arena/8234a824-poker2`'s root dashboard): the deletion of `docs/`, `verified/`, `pages/`, `planning.html`,
`app.js`, `style.css`, `styles.css`, `assets/css/style.css` and the generators `scripts/build.mjs`,
`scripts/build.py`, `scripts/build_site.py`, `scripts/check_links.py` described in T1 **was reverted during the
merge**. Those files are main-owned or referenced by main-owned CI (`scripts/check_links.py` walks `docs/`;
`.github/workflows/verify.yml` restores the integration-owned root pages after `scripts/build.py` runs), so removing
them would have broken another session's site rather than consolidating it.

Final ownership state:

| Surface | Generator | Data | CI that enforces it |
|---|---|---|---|
| repository root dashboard (`index.html`, `tournaments.html`, `hotels.html`, `flagged.html`, `questions.html`, `suggestions.html`, `summary.html`, `repo-review.html`, `planner.html`, `planning.html`, `ranking.html`, `rules.html`, `monitor.html`, `venue-*.html`, `venues/*`) | `scripts/build_site.py` + `scripts/build_master.py` | `data/site/*.json`, `data/master.json` | `.github/workflows/verify.yml`, `source-monitor.yml`, `recheck.yml` |
| `/plan/` (22 pages, `plan/assets/*`) | `scripts/build-site.py` (+ `build-events.py`, `build-schedule.py`) | `site-data/*.json` | `.github/workflows/plan-verify.yml`, `plan-refresh.yml`, `scripts/check_site.mjs` |
| `/docs/`, `/verified/`, `/pages/`, `app.js`, `style.css`, `styles.css`, `assets/css` | earlier sessions (`scripts/build.py`, `scripts/build.mjs`) | `data/*.json`, `data/verified/*` | none; frozen legacy, still published |

Nothing in this session writes to another row of that table, and `/plan/` shares no file path with the root
dashboard. Consolidating to one surface (S-11) and merging the three monitor jobs (S-12) stay open for you to decide.

Publication record for PR #34 (2026-11-16):

- PR [#34](https://github.com/karagemop466-tech/Poker2/pull/34) merged to `main` at merge commit `c2fc205`, after
  two merge commits on the branch that reconciled `main`'s parallel work (PR #32, #35, #36). Both surfaces' CI was
  green on the PR before merging: `Verify site` (main's, including `scripts/audit.py` and `scripts/check_links.py`)
  and `Plan: generated pages match their data`.
- Deployment verified on `main`: `Deploy static site to GitHub Pages` run 43944718489 and `pages build and
  deployment` run 43944717817 completed successfully; Pages API reports `built`. The new surface is live at
  https://karagemop466-tech.github.io/Poker2/plan/ (root dashboard unchanged).
- Two rendering defects found by reading the deployed page and fixed on this branch: `earliest_plausible_finish`
  is stored as minutes since midnight and was being printed as `1045` instead of `5:25 PM`, and the re-entry
  excerpt duplicated the single-entry excerpt verbatim when both came from the same sentence.
- Follow-ups recorded for the next session: `S-11` (choose one surface to keep), `S-12` (merge the three scheduled
  monitor jobs), `S-02` (27 structure sheets unread), `FG-02` (get the single-entry answer in writing).

## Session arena/5dcf101f-poker2 — verification sweep + integration (2026-11-17)

Base: `02cffeb` (main). Branch: `arena/5dcf101f-poker2` (fixed by the session protocol; the task spec's
`session-<id>/<task>` naming is not available to this session — same deviation recorded as F02 by earlier sessions).

| Task | Status | Owner | Files |
|---|---|---|---|
| V1 Read official Venetian DSE IV schedule end-to-end; reconcile every row the site publishes | done | arena/5dcf101f-poker2 | `data/master.json`, `COORDINATION.md` |
| V2 Read the structure sheets behind the published rows; remove `unverified` only where an official document settles the row | done | arena/5dcf101f-poker2 | `scripts/build_master.py`, `data/master.json` |
| V3 Duplicate-row audit (same venue + date + event published twice) | done — 12 duplicate rows removed | arena/5dcf101f-poker2 | `scripts/audit.py`, `scripts/build_master.py`, `data/master.json` |
| V4 Hotel true-cost integrity: every row's tax rate traces to a source that states it | done — South Point corrected | arena/5dcf101f-poker2 | `data/master.json`, `hotels.html` |
| V5 One page per venue for every venue in the dataset | done — 7 venue pages | arena/5dcf101f-poker2 | `scripts/build_site.py`, `venue-*.html` |
| V6 Per-row `last_checked` on every table | done | arena/5dcf101f-poker2 | `scripts/build_site.py`, `scripts/build_f0816fab.py` |
| V7 Site-wide search across all tables | done | `assets/dashboard.js`, `scripts/build_site.py` |
| V8 Build/link/audit verification, PR to main, Pages deploy confirmation, record | in progress | arena/5dcf101f-poker2 | `COORDINATION.md`, `README.md` |

Scope: this session works only on the files above. Legacy surfaces (`plan/`, `site-data/`, `docs/`, `verified/`, `pages/`)
are read as inputs and left untouched. New canonical data continues to flow through `data/master.json`.

### Verification record — arena/5dcf101f-poker2 (2026-11-17)

Read first-hand through a live fetch of the official hosts (sandbox `curl` cannot reach them; the page/PDF
reader can). Every item below was checked against the document named, not against an earlier session's note.

| Document read | What it settled |
|---|---|
| Venetian DSE IV event page, all 4 chunks (`dse-nov-2026.html`) | Full schedule Nov 16 – Dec 23. Reconciled all 83 Venetian rows: dates, start times, event numbers, buy-ins, guarantees and structure-sheet ownership all match. **Correction to an earlier board note:** the 9:10 AM (event 46) and 12:10 PM (event 48) satellites on Dec 12 are two *different* events, not a duplicate. |
| Structure sheets 1, 5, 11, 15, 16, 18 (read verbatim) | Confirmed fee splits ($40/$200, $58/$300, $90/$600 with per-event guarantees for 16/30/54, $50/$300, $100/$800 with $75K for event 36, $35/$200 RaceDay), chip counts, late-registration closes and level lengths. None prints a re-entry, rebuy or add-on clause — so "sheet silent" is the correct label, and none is promoted to confirmed single-entry. |
| Wynn WPT structures PDF, all 8 chunks | 13 event term sets transcribed verbatim. Applied to the 11 rows they actually document; the other WPT rows stay `unverified` because the PDF does not cover them. |
| Wynn WPT schedule PDF | Reconciles the Wynn rows' dates, times, buy-ins and guarantees. |
| Clark County transient lodging guide (Appendix III + licensed-property schedule) | 13.38% for ARIA, Bellagio, Caesars Palace, MGM Grand, Venetian/Palazzo, Wynn/Encore, Westgate. **South Point is 13.00%**, not 13.38% — corrected. |

Defects found and fixed (all published before this session, none introduced by it):

1. **South Point tax rate was wrong.** The site applied 13.38% (Primary Gaming Corridor) to a property the county
   schedule lists at 13.00%. Every South Point cost calculation was overstated.
2. **Twelve duplicate Wynn rows.** Two sessions added the same events under slightly different names
   ("HORSE $800" vs "HORSE $800 (no guarantee)", "NIH" vs "NLH"), inflating the table and double-counting guarantees.
3. **The audit did not cover the dataset the site renders.** `scripts/audit.py` validated `data/site/events.json`,
   while the pages are built from `data/master.json` — which is why (1) and (2) reached the live site. The audit now
   checks the canonical file, including a duplicate guard on the same key the generator uses.
4. **A wrong factual claim in the summary.** "The earliest verified single-entry start is 11:10 AM" ignored the
   five 10:10 AM sheet-silent events. Corrected to 10:10 AM, with the 9:00 AM Horseshoe row explicitly marked
   unverified (that room publishes no buy-in, guarantee or entry rule).
5. **Headline numbers were typed by hand** and had drifted from the data. They are now computed at build time.
6. **Findings were stored but never rendered.** The executive summary now shows all eight with their sources, and
   any statement contradicted by this pass is shown struck through under a `superseded` badge rather than deleted.
7. **21 of 41 flags had no source link** and none had an ID. All now carry a stable `VR-nnn` ID and a link to the
   official document; one obsolete flag (sheets not read) is resolved with an explicit update note.

Verified, not assumed: `scripts/audit.py` OK; `scripts/build_site.py` 21 pages / 166 events / 10 hotels, every row
cited; `scripts/check_links.py` 37 pages, 2,918 hrefs, 0 broken internal links, 0 non-official external hosts;
the site-wide search and trip-cost calculator exercised under a DOM stub (search filters across multiple tables;
true cost/night = (rate + fee) × (1 + tax) + parking reconciles to $217.28 for the Venetian poker rate).

Still open and published on the Flagged page (do not block merge): no event on any official document read states
"no re-entry", so **no row is confirmed single-entry**; no official walking time or dated room quote exists in any
source read; no 8:00 AM tournament is printed anywhere in the dataset.

## Session arena/f4e82c6f-poker2 — README repair and repository documentation audit (2026-11-17)

- Claim commit: `81f366a` on the fixed active branch `arena/f4e82c6f-poker2`; pushed to that branch after `git pull --rebase origin main` confirmed it was current.
- Replaced the malformed root README, which contained literal merge-conflict markers and duplicated/contradictory historical README text, with a current usage guide describing the root dashboard, the separate `/plan/` surface, retained archives, generator ownership, data policy, and monitoring workflows.
- Checks: `python3 scripts/audit.py` passed (83 Venetian event rows, 13 other-venue rows, 8 hotel rows, 60 sources); `python3 scripts/build_site.py` completed (15 pages, 178 events, 10 hotels); `python3 scripts/check_links.py` passed (24 pages, 1,749 links, zero broken internal links and zero disallowed external hosts); `git diff --check` and README relative-link checks passed.
- Irregularity: running `python3 scripts/monitor.py` in this sandbox checked 22 URLs and got 22 fetch errors. Its local report/registry changes were discarded so this documentation-only task does not publish errors as a fresh monitor run. This indicates an environment/network retrieval failure, not confirmation that sources are unchanged; check the scheduled Actions run/report. The repository has multiple monitor workflows with separate registries; consolidation remains a documented open integration decision (S-12).
- No external source facts were added or changed in this task. The official-source evidence remains the cited dataset and links audited by `scripts/audit.py`.
- Integration: PR [#43](https://github.com/karagemop466-tech/Poker2/pull/43) merged to `main` at `93ee9ca2c320441e0835af3228c584a20fa18b59` on 2026-11-17. Both PR checks passed: [Verify site](https://github.com/karagemop466-tech/Poker2/actions/runs/43988469385) and [Plan generated pages](https://github.com/karagemop466-tech/Poker2/actions/runs/43988469431). Post-merge root `Verify site` [run 43988516031](https://github.com/karagemop466-tech/Poker2/actions/runs/43988516031), `/plan/` verification [run 43988516113](https://github.com/karagemop466-tech/Poker2/actions/runs/43988516113), GitHub Pages build/deployment [run 43988515513](https://github.com/karagemop466-tech/Poker2/actions/runs/43988515513), and static-site deployment [run 43988516063](https://github.com/karagemop466-tech/Poker2/actions/runs/43988516063) all completed successfully. Live site: https://karagemop466-tech.github.io/Poker2/.

## Session arena/18aba6dd-poker2 — claims (2026-11-17)

Started from `origin/main` at `7499702` (after PRs #43/#44, README repair). All prior board tasks are `done`; the open follow-ups recorded by arena/72ca3e9d-poker2 are picked up here. Platform constraint noted by earlier sessions applies: this Arena session is fixed to branch `arena/18aba6dd-poker2`, so all work is committed there (equivalent of `session-<id>/<task>` scope discipline is kept by file ownership, not by branch naming).

| Task | Status | Owner | Files |
|---|---|---|---|
| S-02: read the 27 remaining official Venetian DSE IV structure sheets (2, 3, 4, 9, 12, 13, 14, 16, 17, 19–28, 30–37) and transcribe entry rules + structural values into the /plan/ surface, moving rows out of `unverified`/silent states where the sheet text warrants | in progress | arena/18aba6dd-poker2 | `scripts/build-events.py`, `site-data/*.json` (regenerated), `plan/**` (regenerated), `COORDINATION.md` |
| Re-run plan-surface verification (build-events.py, build-schedule.py, build-site.py, check_site.mjs) and record results | in progress | arena/18aba6dd-poker2 | `plan/**`, `COORDINATION.md` |
| PR to main, merge, confirm GitHub Pages deploy, record result | pending | arena/18aba6dd-poker2 | `COORDINATION.md` |

Explicitly NOT claimed (blocked on user decision or out of scope): S-11 (surface consolidation), S-12 (monitor-job merge), FG-02 (written single-entry confirmation from the poker room — requires contacting the room), FG-05 (dated hotel quote — requires browser booking engine). The root-dashboard surface (`scripts/build_site.py` + `data/master.json` pipeline) is not touched by this session.

## Session arena/18aba6dd-poker2 — completion record (2026-11-17)

| Task | Status | Owner | Files |
|---|---|---|---|
| S-02: read the 27 remaining official Venetian DSE IV structure sheets; transcribe entry rules + structural values | done | arena/18aba6dd-poker2 | `scripts/build-events.py`, `site-data/events.json`, `site-data/schedule.json`, `site-data/summary-stats.json`, `plan/**` |
| Plan-surface verification rerun (build-events/build-schedule/build-site `--check`, `check_site.mjs`) | done | arena/18aba6dd-poker2 | `plan/**` |
| S-06 (plan surface): routed walking minutes for all 12 hotel→venue pairs | done | arena/18aba6dd-poker2 | `site-data/walk.json`, `scripts/build-site.py`, `site-data/{summary,questions,suggestions}.json` |
| Schedule-builder eligibility rule (primaries must be open to all; restricted candidates listed with reason) | done | arena/18aba6dd-poker2 | `scripts/build-schedule.py`, `site-data/schedule.json` |
| PR to main, merge, confirm GitHub Pages deploy, record result | recorded below | arena/18aba6dd-poker2 | `COORDINATION.md` |

### Sources read first-hand on 2026-11-17 (session arena/18aba6dd-poker2)

The 27 remaining official Venetian DSE IV structure sheets, each read in full:
`https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{2,3,4,9,12,13,14,16,17,19,20,21,22,23,24,25,26,27,28,30,31,32,33,34,35,36,37}.pdf`
— completing the sweep of all 37 published sheets (sheets 1, 5, 6, 7, 8, 10, 11, 15, 18, 29 were read by earlier sessions on 2026-11-16 and were not re-read).

Walking measurements (2 pairs measured fresh 2026-11-17; 10 pairs reused from the dated 2026-11-16 dataset `data/site/walking.json` with the same method):
- OpenStreetMap Nominatim geocoding: `https://nominatim.openstreetmap.org/search?q=The+Cosmopolitan+of+Las+Vegas%2C+3708+Las+Vegas+Blvd+South&format=json` (geocoded exactly to the official 3708 S Las Vegas Blvd address)
- OSRM foot profile (FOSSGIS public server): `https://routing.openstreetmap.de/routed-foot/route/v1/foot/...` — Cosmopolitan→Venetian poker room 22.6 min / 1,692 m; Bellagio→Cosmopolitan 16.5 min / 1,235 m

### Verification performed

- `python3 scripts/build-events.py` cross-checks: guarantee parsed from each event name must equal the guarantee printed on that event's sheet (94 rows, mismatch aborts); event-to-sheet tagging must match each sheet's own "Event Numbers" line (no orphan rows).
- Result dataset: 94 Venetian rows, all sheet-verified (`sheet_read` true, 0 `unverified`); categories: 45 single_entry_candidate, 27 multi_flight, 11 day2_restart, 7 satellite, 2 spend_advantage, 1 team_format, 1 single_entry_2day (new).
- `--check` modes of all three generators pass; `node scripts/check_site.mjs` passes (15 plan pages, 94 event rows, every data row carries an https official-source link); all pages served HTTP 200 from a local server.
- Schedule rebuilt: 27 days with an open-to-all primary; 50+ Seniors rows (events 24/32) listed with their restriction instead of being scheduled; best 4-day window Dec 6–9, 2026 (entries $2,300, $170K GTD played, avg ratio 69.3x, every night poker-rate eligible).

### Findings and irregularities from the sweep (published on the plan's Flagged/Unverified pages where relevant)

1. **Event 39's schedule tag is misleading.** The schedule page tags it as a flight row, but its sheet defines exactly one Day 1 (Dec 10) + Day 2 restart — there are no multiple starting flights. Modeled as a new `single_entry_2day` category rather than asserting a "buy into another flight" rule the sheet does not contain. It is also female-only (sheet rule 02), so it stays out of the day plan.
2. **LIPS events withhold an extra flat fee** for Vegas Connected, INC, DBA Ladies International Poker Series: $10 of the $600 buy-in (sheets 31, 33) and $20 of the $800 buy-in (sheet 32), on top of the house-fee split. Recorded verbatim on each row.
3. **Satellites guarantee seats, not dollars** ("Guarantee: 2 Seats" on sheets 19, 24, 25): numeric guarantee stays blank by design; the seat text is quoted. The turbo-satellite sheet (25) prints no registration-close wall clock — only "6 levels" — so that field stays blank rather than computed.
4. **Printed vs arithmetic reg-close times disagree on several multi-flight sheets** (e.g. sheet 2 prints "9 levels + Break (5:55 PM)" while 9×40 min from 11:10 AM lands at ~5:25 PM). The printed wall-clock text is transcribed verbatim, matching the convention used for sheets 1/8 in the earlier session.
5. **Sheet 28's fee rule** extracts with a line-wrap artifact ("(Rake … - Staff)"); transcribed as extracted, consistent with how sheets 5/6/18/29 were transcribed.
6. **Event 49's flights play to ~15% of the field** (sheet 20), not the 12.5% printed on the other flight sheets.
7. **Events 56/59 publish early-registration rake discounts** ($40/$20 off house fees before the event starts, sheet 35/36 rule 07) — recorded in the fee text; not classified spend-advantage because a time-based discount lowers cost rather than buying an edge (unlike the PokerAtlas PRO membership discount on events 18/58).
8. **Sheet 26 (event 17)**, previously a `not_read` placeholder, resolves cleanly: $400 PLO bounty, $60 fee/$340 pool, $100 bounties, 12.5% payout, silent on re-entry → single-entry candidate.

### Integration / publication record

- Branch `arena/18aba6dd-poker2` (fixed by the platform; file-ownership discipline kept instead of branch-per-task, as with every prior session).
- PR and Pages deploy result: recorded below after merge.
- Follow-up record PR [#44](https://github.com/karagemop466-tech/Poker2/pull/44) merged at `74997023025b4afd5c2767485e129be5ece49f5a`; both verification workflows passed. For that merge, GitHub's canonical `pages build and deployment` run [43988703319](https://github.com/karagemop466-tech/Poker2/actions/runs/43988703319) succeeded and Pages API reports `built` for the same commit. The separate `.github/workflows/pages.yml` run [43988703616](https://github.com/karagemop466-tech/Poker2/actions/runs/43988703616) failed in its deploy job with “No artifacts named github-pages” even though the earlier steps reported success; a manual workflow dispatch was denied by repository permissions. The canonical Pages build succeeded, so the site is published; duplicate deployment-workflow behavior remains an irregularity for review, not a claim that the live deployment failed.

## Session arena/f4e82c6f-poker2 — duplicate Pages publisher cleanup (2026-11-17)

- Claim pushed as `c190709` on the active branch. Investigation found two concurrent publishers: GitHub Pages is configured as `legacy` and its automatically generated `pages build and deployment` workflow builds/deploys the static root; `.github/workflows/pages.yml` was a second GitHub Actions publisher using `upload-pages-artifact`/`deploy-pages`.
- Canonical Pages run [43988937466](https://github.com/karagemop466-tech/Poker2/actions/runs/43988937466) succeeded for commit `18558dc`; the Pages API reported `built`. The duplicate custom publisher failed on PR #44 [run 43988703616](https://github.com/karagemop466-tech/Poker2/actions/runs/43988703616) and PR #45 [run 43988938121](https://github.com/karagemop466-tech/Poker2/actions/runs/43988938121) with “No artifacts named github-pages”; logs showed the upload step but deploy could not retrieve an artifact. A workflow-dispatch retry was denied by repository permissions.
- Removed only `.github/workflows/pages.yml` so the configured, successful canonical publisher is the single deployment path. No site content, data, or Pages source settings were changed. Validate the post-merge `pages build and deployment` and site verification runs before marking this claim complete.

- Cleanup integration: PR [#46](https://github.com/karagemop466-tech/Poker2/pull/46) merged at `8acae0c449a17b67fa8b75d2b881304e018d26d1`. Both verification jobs passed in PR and after merge. With the duplicate workflow removed, the canonical Pages build and deployment [run 43989177852](https://github.com/karagemop466-tech/Poker2/actions/runs/43989177852) succeeded; root verification [43989178134](https://github.com/karagemop466-tech/Poker2/actions/runs/43989178134) and plan verification [43989178065](https://github.com/karagemop466-tech/Poker2/actions/runs/43989178065) also passed. Pages API reports `built` for commit `8acae0c`; live site https://karagemop466-tech.github.io/Poker2/. The duplicate artifact failure no longer recurs because its publisher was removed.
## Session arena/8b1f0fd8-poker2 — claims and record (2026-11-17)

| Task | Status | Owner | Files |
|---|---|---|---|
| T1 Read every remaining Venetian DSE IV structure sheet (27 of 37 were unread on main); record the sheet's own text for buy-in, guarantee, fee, starting chips, level length, late-registration, and re-entry / add-on / flight wording | in progress | arena/8b1f0fd8-poker2 | `scripts/build-events.py` (SHEETS block), `site-data/events.json` |
| T2 Remove the "unverified" label only from events whose official schedule row and structure sheet agree (name, guarantee, start); keep the single-entry status as the sheet states it | in progress | arena/8b1f0fd8-poker2 | `site-data/events.json`, `site-data/flags.json` |
| T3 Repair unresolved merge-conflict markers left in `README.md` on main (irregularity IR-README) | in progress | arena/8b1f0fd8-poker2 | `README.md` |
| T4 Rebuild generated pages from the updated dataset; run the repo's own checks (audit, build, link check, plan check) | pending | arena/8b1f0fd8-poker2 | generated pages under `plan/`, `venues/` |
| T5 Hotel live-rate lookup, Google/Apple walking routes, and scheduled daily schedule scrape | not started by this session — blocked, see record | — | — |

### Renewal and record — arena/8b1f0fd8-poker2 (2026-11-17)

Claim renewed at 2026-11-17 00:38 UTC (the 60-minute expiry from `e14c3d6` had passed; the claim timestamp was not recorded in that commit). T5 remains unclaimed and blocked.

| Task | Result (2026-11-17) |
|---|---|
| T1 Structure sheets | Done. All 37 Venetian DSE IV structure sheets read (10 on 2026-11-16, 27 today). Register: `research/structure-sheets-register.md`. Every row in `site-data/events.json` (94) is `sheet_read: true`; start times and fee+pool checked against the sheets. |
| T2 Unverified labels | Done for all events whose schedule row and sheet agree. Four other-venue rows remain UNVERIFIED because their documents were not re-read; they are listed on `/plan/unverified.html`. Single-entry status is shown as the sheet states it; no sheet states a one-entry cap (FG-02 stays open). |
| T3 README conflict markers | Superseded, not repeated. Session `f4e82c6f` replaced the README on main (PR #43, merged before this rebase), so this session did not rewrite it and kept main's version. The earlier draft repair was discarded in the rebase to avoid overwriting that work. |
| T4 Rebuild and checks | Done. `scripts/audit.py` OK (83 Venetian + 13 other rows, 8 hotels, 60 sources); `scripts/build.py` exit 0; `scripts/check_links.py` OK; `scripts/check_site.mjs` OK (15 plan pages, 94 event rows); `build-events.py`, `build-schedule.py`, `build-site.py` regenerate identically. |

New irregularities (flagged, not blocking the merge):

- **FG-30** (Medium): most Venetian rows are 21+ with a Rewards card, Seniors events are 50+, LIPS events are female-only, and sheet 31 is a team event. The gate is recorded per row in `events.json`, but the plan tables do not yet display it.
- **FG-31** (Medium): the root dashboard (`tournaments.html` and related pages) is generated from the legacy `data/` pipeline and still shows older UNVERIFIED labels for Venetian rows. `/plan/` is the current surface. Consolidation is the open decision `S-11` (and `S-A14`).

Corrections made in this session: the Event 36 / Event 38 sentence in `site-data/summary.json` no longer asserts an unreachable event. It now says the sheets do not show how long a player lasts, so the Event 38 timing is unknown and not planned.

Remaining open items: `FG-02` (single-entry answer in writing), `S-02` (structure-sheet reading now done; automation awaits the owner's choice), `f743ae5a` (walking distances and lodging tax, unverified).

### Integration record — arena/8b1f0fd8-poker2 (2026-11-17)

- Integration PR: [#48](https://github.com/karagemop466-tech/Poker2/pull/48) (`arena/8b1f0fd8-poker2` → `main`), head `feb5afb`.
- Checks on the PR head: `Verify site` success and `Plan: generated pages match their data` success.
- Merge: **merged** (`gh pr merge 48 --merge`) at 2026-11-17 00:40:19 UTC, merge commit `2c2105d5f7292f1fd629bd8f79212a6d2631bdfb`.
- Post-merge checks on `2c2105d`: `Verify site` success, `Plan: generated pages match their data` success, `pages build and deployment` success. The Pages API reports `built` at `2c2105d`.
- Live confirmation: `https://karagemop466-tech.github.io/Poker2/plan/flagged.html` shows the updated FG-03 ("All 37 structure sheets read"). The sandbox cannot reach `github.io` directly, so this was read with the page fetcher.
- Claim status: T1, T2 and T4 done and merged. T3 superseded by `f4e82c6f` (README already repaired on `main`). T5 remains unclaimed and blocked.
- Force-push note: the branch's claim commit was rewritten during rebase onto `main`, which had moved (PRs #43–47). The branch was force-pushed once with `--force-with-lease` pinned to the session's own previous tip `e14c3d6`. No other session's commits were rewritten.
- Open irregularities (not blocking, all on `/plan/flagged.html`): FG-02, FG-30, FG-31, FG-04/04b, FG-05/05b, FG-06, FG-07.

### V8 — merge and deployment record (arena/5dcf101f-poker2)

- PR [#50](https://github.com/karagemop466-tech/Poker2/pull/50) → `main`, merged 2026-11-17T00:46:58Z,
  merge commit `6c84320`. PR checks `verify` (8s) and `verify` (8s) both **pass**.
- `main` had advanced 17 commits while this session worked (parallel sessions `arena/8b1f0fd8-poker2` and
  `arena/f4e82c6f-poker2`). Merging `origin/main` produced exactly one conflict, in `COORDINATION.md`
  (both sides appended a session section at the same place). Resolved by keeping **both** records — this
  session's section first, then `arena/f4e82c6f-poker2`'s. No other session's file was reverted.
- Re-verification **after** the merge, on the combined tree: `scripts/audit.py` OK;
  `scripts/build_master.py` 166 events / 10 hotels / 41 flags; `scripts/build_site.py` 20 pages, all rows
  cited; `scripts/check_links.py` 0 broken internal links, 0 non-official external hosts. Both CI surfaces
  were also simulated locally (`scripts/build.py` + page restore for `verify.yml`, and the three `/plan/`
  generators for `plan-verify.yml`): clean tree after each, so neither workflow fails.
- Deployment: workflow runs on `6c84320` — `pages build and deployment` **success**,
  `Verify site` **success**, `Plan: generated pages match their data` **success**. Pages API reports
  `status: built`. Live URL <https://karagemop466-tech.github.io/Poker2/>.
- Live verification by reading the deployed page, not by trusting the build: the dashboard serves the new
  "Jump to a venue" index with computed counts and per-venue last-checked dates, and every venue page it
  links to resolves.
- One follow-up defect found **by reading the deployed page**: pages with no tables rendered the search
  status as "0 rows on this page". Fixed to show guidance instead, covered by a DOM-stub test.

### What is still not verified (published on the Flagged page; does not block)

These are not gaps in effort, they are things no official source read publishes:

1. **No event is confirmed single-entry.** No Venetian structure sheet, no Wynn WPT terms document and no
   Caesars/MGM/Horseshoe page read states "no re-entry". "Sheet silent" is the accurate label and it is
   weaker than a freezeout guarantee. Getting this in writing from each poker room is the single highest
   value outstanding action.
2. **No official walking time.** Every hotel row carries a maps link for manual confirmation; the routed
   estimates in `data/site/walking.json` are a routing-engine estimate, labelled as such.
3. **No dated room quote.** Every official booking calendar reachable in this environment masks prices
   behind a cookie wall, so the rate log holds the attempt, not a number. The true-cost formula is
   verified and ready for a quote the moment one is captured.
4. **No 8:00 AM tournament anywhere in the dataset.** Earliest printed start is 9:00 AM (Horseshoe), and
   that room publishes no buy-in, guarantee or entry rule.
5. **Wynn daily tournaments during the WPT window** are marked unavailable rather than confirmed either
   way — the Wynn page does not name the WPT series, and the WPT schedule has no 12:00 PM daily rows.

### arena/0fd90745-poker2 — final integration record (2026-11-17)

| Task | Status | Files |
|---|---|---|
| J1 Read outstanding Venetian structure sheets | done as far as the fetcher allowed: 14 read in full (docs 2, 3, 4, 9, 12, 13, 14, 16, 17, 19, 20, 21, 22 +22), 0 mismatches vs the schedule page; the last 23 are covered by PR #48's register and were NOT re-read here | `scripts/build-events.py` (main's version), `site-data/events.json` |
| J2 Re-verify rows against the sheet evidence; date the rows | done — 83 Venetian rows in `data/master.json` compared field-by-field against the merged 37-sheet dataset: no contradictory value; the 14 sheets this session read carry `last_checked 2026-11-17` + a dated verification-pass badge in the site header | `scripts/build_master.py`, `data/master.json`, root pages |
| J3 Re-check every official URL | done — `scripts/build_monitor_registry.py` generates `data/source_monitor.json` from the site's own citations + all 37 sheets: **22 → 82 monitored URLs**; hashes/`last_checked` preserved; still no baseline hash, so the first scheduled run only seeds it (flag IR-0FD-03) | `scripts/build_monitor_registry.py`, `data/source_monitor.json`, `scripts/build_site.py` |
| J4 README conflict markers | **taken by arena/f4e82c6f-poker2 (PR #43)** before this session reached it — this session dropped the task rather than duplicate it | — |
| J5 Summary/questions/suggestions | done for the /plan/ surface (FG-03, FG-19, FG-21 sheet-13 footer contradiction, FG-22 fetcher failure, S-02 partly implemented) and the root (IR-0FD-01/02/03) | `site-data/{flags,suggestions}.json`, root flags |
| J6 Stale PRs #1/#24/#28 | closed as superseded (their branches remain for audit) | GitHub |
| J7 PR → main, CI, Pages, record | PR #51 | this section |

Conflict log (required by the protocol): `git pull --rebase origin main` mid-session hit conflicts in
`scripts/build-events.py`, `site-data/*`, `plan/*` and `COORDINATION.md` because arena/8b1f0fd8-poker2
merged PR #48 (all 37 sheets read) while this branch was carrying a 14-sheet pass. The rebase was
aborted, the branch pushed as-is, and `git merge -X theirs origin/main` resolved it in favour of main's
data and generators — nothing from the other session was discarded, and this session's unique files
(`scripts/build_monitor_registry.py`, the root re-check, `data/source_monitor.json`) were kept. One
defect the merge itself introduced was caught before pushing: a surviving hunk referenced a constant
main's generator does not define (`NameError: SHEET_READ_TODAY`), so `scripts/build-events.py` was reset
to main's version verbatim and `site-data/schedule.json` regenerated (main's committed copy was stale
against its own events.json, which is exactly what `plan-verify` fails on).

Verified locally before the PR: `scripts/audit.py` OK · `scripts/check_links.py` OK ·
`build-events.py --check`, `build-site.py --check` OK · `node scripts/check_site.mjs` OK ·
`check_sources.mjs --selftest` (34 tracked patterns, 66 monitored URLs) OK ·
`scrape-schedule.mjs --selftest` OK · CI simulation (`build.py` + the ownership restore) leaves a clean tree.

## Session arena/ec9cc26c-poker2 — verification sweep + final integration (2026-11-17)

Base: `ba321e7` (main, PR #52 merged). Branch: `arena/ec9cc26c-poker2` (fixed by the session
protocol; the task spec's `session-<id>/<task>` naming is not available — same deviation recorded
as F02 by earlier sessions).

| Task | Status | Owner | Files |
|---|---|---|---|
| K1 Claim board; disposition of stale open PRs #1/#24/#28 | done — closed 2026-11-17 as superseded, branches retained | arena/ec9cc26c-poker2 | `COORDINATION.md`, GitHub only |
| K2 Fresh line-by-line verification pass (2026-11-17): re-read the official pages behind the published rows, compare field-by-field with `data/master.json`, refresh per-row `last_checked`, fix any defect found | done | arena/ec9cc26c-poker2 | `scripts/build_master.py`, `data/master.json`, `research/ec9cc26c-*-2026-11-17.md` |
| K3 Read-through of the live site (root dashboard + `/2026/` + `/plan/`) for rendering/defect review; fix defects found | done — one defect fixed: 5 raw source-registry keys rendered as labels on monitor/sources | arena/ec9cc26c-poker2 | `scripts/build_monitor_registry.py`, `scripts/build_master.py`, root pages via generators |
| K4 Run every repo check on the combined tree (audit, build, link check, plan checks, CI simulation) | done — all 8 verify.yml gates + all 4 plan-verify gates pass on the merged tree | arena/ec9cc26c-poker2 | — |
| K5 Final integration: PR → `main`, CI green, Pages deploy confirmed, record here | in progress | arena/ec9cc26c-poker2 | `COORDINATION.md` |

### What K2 actually verified (first-hand, 2026-11-17, via the page-fetch tool — sandbox `curl` cannot reach casino hosts)

| Document read in full | Reconciliation |
|---|---|
| Venetian DSE IV schedule page (4 chunks) | 94 printed rows transcribed to `research/ec9cc26c-venetian-schedule-official-2026-11-17.md`; the 83 published rows (94 minus 11 Day-2/final-table rows) match on date, start, event number, name, guarantee and structure-PDF URL — **zero mismatches**; buy-ins re-parsed from names match `buy_in` on every row |
| Wynn WPT World Championship schedule PDF (2 chunks) | 136 printed rows transcribed to `research/ec9cc26c-wynn-wpt-schedule-official-2026-11-17.md`; the 49 dated Wynn rows match on date, start, buy-in and guarantee — **zero mismatches**; the 4 recurring dailies cite a different PDF (not re-read today) and correctly keep `last_checked 2026-11-16`; the MGM Saturday row likewise keeps 2026-11-16 (weekly PDF not re-read) |
| Caesars poker guide | Caesars Palace 4 dailies (10a/2p/6p/9p, $100, $1,000 GTD, $50 add-on) and Horseshoe 6 times (9a/11a/2p/5p/8p/11p) confirmed against the 10 published rows |
| MGM Grand poker page | daily 11:00am / 7:00pm / 11:00pm confirmed against the 3 published rows |
| Golden Nugget daily page | 10AM/5PM/2AM, 15,000 chips, 15-minute levels, unlimited re-entry to level 5 + two $20 add-ons confirmed against the 3 published rows |
| Venetian resort-fee page + hotel terms | $55 plus tax/night, Clark County Room Tax 13.38%, $20/day registered-guest parking confirmed |
| Wynn resort-information page | $55 plus tax daily resort fee confirmed |
| Clark County transient-lodging guide (Appendix III + licensed-property schedule) | 13.38% confirmed for ARIA, Bellagio, Caesars Palace, MGM Grand, Venetian/Palazzo, Wynn/Encore, Westgate; **South Point 13.00%** confirmed; addresses corroborated (ARIA 3730, Bellagio 3600, MGM 3799, Wynn 3131, South Point 9777, Westgate 3000 Paradise) |

Transcripts: `research/ec9cc26c-venetian-schedule-official-2026-11-17.md`, `research/ec9cc26c-wynn-wpt-schedule-official-2026-11-17.md` (row counts are counted, not estimated: 94 and 136).

Merge log (required by the protocol): main advanced `ba321e7` → `2c65dfc` (PRs #53–#63) while this session worked. `git merge origin/main` produced three conflicts, all resolved without discarding anyone's work:
- `COORDINATION.md` — union: this session's claim section kept, then main's appended session sections.
- `scripts/build_master.py` — both additive blocks kept (this session's K2 last-checked sweep, then main's walking/rate-log blocks).
- `index.html` — generated file: conflict resolved then regenerated from the merged generators.
After the merge the full check suite was re-run on the combined tree (K4 above).

Scope: files listed above. Legacy surfaces (`plan/`, `site-data/`, `docs/`, `verified/`, `pages/`)
are read as inputs. Open decisions S-11 (one surface) and S-12 (merge monitor jobs) stay suggestions
for user review — not implemented here.
## Session arena/618fc735-poker2 — independent verification sweep (2026-11-17)

Base: `main` @ `ba321e7` (PR #52 merged). Branch: `arena/618fc735-poker2`. This session runs as the
**final integration session** for the shared outputs, because no other session holds a live claim.

| Task | Status | Owner | Files (scope) |
|---|---|---|---|
| K1 Board claim + baseline check | in progress | arena/618fc735-poker2 | `COORDINATION.md` |
| K2 Re-read the Venetian DSE IV schedule page and reconcile every published row against `data/master.json` (date, time, event no., name, structure-PDF link) | in progress | arena/618fc735-poker2 | `scripts/build_master.py`, `data/master.json` |
| K3 Re-read the Venetian + Wynn + other-venue policy pages (resort fee, room tax, poker suite rates, terms, schedules) and record row-level `last_checked` | in progress | arena/618fc735-poker2 | `scripts/build_master.py`, `data/master.json`, root pages |
| K4 Re-read the structure sheets that back the "sheet silent on re-entry" rows and confirm the silence claim line by line | in progress | arena/618fc735-poker2 | `scripts/build_master.py`, `data/master.json` |
| K5 Fix defects found by K2–K4; regenerate the site; refresh summary / questions / suggestions / flagged evidence state | in progress | arena/618fc735-poker2 | `scripts/build_master.py`, `scripts/build_site.py`, root pages |
| K6 Checks (`audit.py`, `check_links.py`, generator `--check`, `check_site.mjs`), PR → `main`, merge, Pages deploy confirmed, record here | in progress | arena/618fc735-poker2 | `COORDINATION.md` |

Notes for other sessions: this session edits the root dashboard generator/data pair only
(`scripts/build_master.py`, `scripts/build_site.py`, `data/master.json`, root `*.html`). The `/plan/`
surface (`scripts/build-events.py`, `plan/**`, `site-data/**`) is **not** in this scope; if you need a
change there, log it here. Sandbox note: direct `curl` from this environment cannot reach any casino
host (only the GitHub/npm/PyPI allowlist), so every source re-read below was done with the page-fetch
tool, which does reach the official sites. That distinction is recorded with each finding.

### Integration sync after merging main (PRs #51/#52), 2026-11-17 (continued)

Main moved to `ba321e7` while this branch was working: PR #48/#51/#52 had completed the 37-sheet sweep
independently and rewrote the events dataset and generators. Resolution, per protocol (never discard
another session's work):

- `scripts/build-events.py`, `site-data/events.json`: **main's versions taken wholesale**; this branch's
  duplicate transcription was dropped (kept only in git history on commits `21d4489`/`8100cb9`).
- `scripts/build-schedule.py`: this branch's open-to-all gate re-applied on top of main's payload — now
  keyed off main's per-row `eligibility` field, skipping only *demographic* restrictions (50+, female-only,
  team composition); the venue-wide "21+, with a Venetian Rewards card" gate stays schedulable. Regenerated
  day plan: Dec 2 → Event 25, Dec 8 → Event 34, Dec 10 → Event 42 (Events 24/32/39 listed in
  `skipped_events` with the restriction text; `restricted_single_entry_rows` = 3).
- `summary.json` recommendation synced to the regenerated schedule (main's committed narrative said
  "Event 38 primary on Dec 9" while its own committed `schedule.json` had Event 36 — the summary was
  written ahead of a gated rebuild that never ran). Now: Dec 9 primary Event 36 (93.8x incl. bounties),
  Event 38 as a conditional fallback gated on registration close; window numbers now cite the canonical
  `top_windows` stats (Dec 6–9: 69.3x avg, $2,300 entries, $170K GTD, 4/4 poker-rate nights).
- `scripts/build-schedule.py` now emits `top_windows` (top 4 distinct windows) so narrative pages cite
  canonical numbers instead of ad-hoc math.
- Walking minutes (S-06), walk.json, Q-10 answer, FG-11 resolution and the S-02/S-06 suggestion records
  were re-applied onto main's narrative files (main still had the pre-S-06 "unverified" state).
- Root surface (`build.py`, root pages, `data/master.json`): untouched; a local run of the legacy
  `scripts/build.py` clobbered root pages during CI simulation and was reverted immediately — root pages
  belong to main's `build_site.py` session (PR #52).
- `scripts/check_sources.mjs` fetch runs in this sandbox have no network, so `site-data/change-report.json`
  and `site-data/snapshots/` it wrote locally were deleted, not committed (the scheduled workflow owns them).

Re-verified on the merged tree: `build-events.py --check`, `build-schedule.py --check`, `build-site.py
--check`, `check_site.mjs` (15 plan pages / 94 rows / 13 UI ids), `check_links.py` (0 broken internal links,
no non-official hosts), `audit.py` (166 events / 10 hotels / 41 flags OK), HTTP smoke test all plan pages 200.

---

## Session arena/97730311-poker2 — claims and record (2026-11-17)

**Scope claimed** (all under `/plan/`, which shares no file path with the root dashboard):

| Task | Status | Owner | Files |
|---|---|---|---|
| Read all 37 Venetian DSE IV structure sheets and fold them into the canonical row set | done (merged with arena/8b1f0fd8-poker2's PR #49, which read 13 of the same sheets in parallel) | arena/97730311-poker2 | `scripts/build-events.py`, `site-data/events.json` |
| Capture a dated, itemised hotel quote from an official booking engine | done for The Venetian | arena/97730311-poker2 | `site-data/rates.json`, `site-data/hotels.json` |
| Port the routed walking matrix into the planner (S-06 / S-13) | done | arena/97730311-poker2 | `scripts/build-walk.py` (new), `data/site/walk-overlay.json` (new), `site-data/walk.json` |
| Re-read every other-venue source that is fetchable (Bellagio, Caesars Palace, Wynn, MGM Grand, Golden Nugget) | done | arena/97730311-poker2 | `site-data/other-venues.json` |
| Render eligibility/notes/level-note and the `multi_day` class on the site | done | arena/97730311-poker2 | `scripts/build-site.py`, `plan/assets/site.css`, `plan/assets/site.js` |
| Workflow wiring for the new walk generator | done | arena/97730311-poker2 | `.github/workflows/plan-verify.yml`, `.github/workflows/plan-refresh.yml` |

Notes:

- **Two new files: `scripts/build-walk.py` and `data/site/walk-overlay.json`.** It reads `data/site/walking.json` (the OSRM/Nominatim matrix an earlier
  session produced) and writes `site-data/walk.json`; `--check` fails when the committed JSON drifts. It is now
  part of the regenerate step in `plan-verify.yml` and the check chain in `plan-refresh.yml`, so the walk page
  cannot silently go stale. The overlay carries what the script cannot regenerate — the routed-via service
  name, the date each route was routed, the routed distance, and the verbatim official interior-route wording
  with its source — captured by earlier sessions and preserved rather than re-derived. It is idempotent — the per-pair `route_retrieved` date is pinned to the day the
  routes were generated (2026-11-16), not to the build date.
- **Every one of the 37 sheets was fetched and read.** Zero rows are now `unverified` on the Venetian set.
  Two facts came out of it that no earlier pass had: eligibility gates (50+ on the Seniors, women-only on the
  LIPS Ladies events, each with the sheet's own forfeiture language) and event #39 being a *multi-day* event
  with a single starting day rather than a multi-flight one. A new `multi_day` category was added for it.
- **Merge note.** `arena/8b1f0fd8-poker2` (PR #49) read 13 of the same sheets and landed them on `main` while
  this session was working. Both transcriptions were compared sheet by sheet before merging: they agree on
  every structural value (start, levels, buy-in, pool, guarantee, late-registration close) and differ only in
  prose. The merged `SHEETS` takes main's — it carries per-sheet `gate` wording for all 19 sheets with an
  eligibility rule and `note` text for the early-bird and Day 2 facts — and adds this session's fuller
  rule-02 forfeiture wording as `gate_excerpt` on sheets 17/19/20/31/32, plus per-sheet `notes` on 19/24/25/31.
  Main's version also keeps the `AS_OF`/`SHEET_AS_OF` split and the hard cross-check that aborts the build
  when a sheet's start time or fee+pool disagrees with the schedule row, both of which are kept.
- **The Horseshoe daily start times were deleted, not repeated.** An earlier session had recorded 9/11 AM and
  2/5/8/11 PM; those times appear on no official page, so the row is now `unverified` rather than carrying a
  number nobody can produce a source for.
- **Two real dated quotes were captured from the Venetian booking engine** (4-night and 7-night, Nov 2026,
  2 adults) and itemised to the cent. Both imply 13.3804% tax, which corroborates the Clark County rate
  independently of the county notice, and both tax the resort fee — which is the assumption the whole
  true-cost formula rests on. This closes FG-03, FG-05 and FG-19, corroborates FG-13 and narrows FG-04 and
  FG-09…FG-11. Wynn and the MGM properties still have no quote: their engines build prices after page load
  and return nothing to a static fetch. That gap is recorded as suggestion **S-15** rather than filled in.
- **Not one official document in this dataset says "one entry per player."** FG-02 stays open. The site says
  "candidate" on all 45 rows and now says so explicitly in Q-03 with the email address to ask.
- Deliberately not done: quoting Wynn/MGM via a headless browser (S-15 — needs your decision), an official
  quality-rating source (S-04 / FG-12), and any consolidation of the two surfaces (S-11 / S-12).

Second merge, same day: `arena/18aba6dd-poker2` (PR #53) landed on `main` after this branch was pushed, and
re-syncing took a second pass. Two of its findings covered the same ground as mine — the count of
single-entry candidates and the walking minutes — so they were merged into one finding each rather than
published twice, with the number taken from the regenerated dataset (45, because this session classifies
Event #39 as a two-day event rather than a one-day candidate). Main's walk.json carried 12 pairs; this
branch carries 70 generated from the full OSRM matrix, so the 70-pair set is kept and main's per-pair
hand-verified detail is folded in through the overlay file above rather than lost.
### Publication record — PR #53 (2026-11-17, session arena/18aba6dd-poker2)

- PR #53 ("S-06 walking minutes + open-to-all day-plan gate, integrated on the completed 37-sheet dataset")
  merged into main without waiting for approval; main at `98ca770`.
- CI on the merge commit: `Verify site` **success**, `Plan: generated pages match their data` **success**,
  `pages build and deployment` **success**; Pages API reports `status: built`.
- Live verification by reading the deployed pages: `plan/hotels.html` renders all 12 pairs with routed
  minutes and the "OSM/OSRM foot-routing estimate … not an official measurement" note; `plan/schedule.html`
  shows Dec 2 → Event 25, Dec 8 → Event 34, Dec 9 → Event 36 (93.8×) with Event 38 as the conditional
  fallback, Dec 10 → Event 42 — the three restricted events no longer appear as primaries anywhere.

## Session arena/618fc735-poker2 — what shipped after the merge with main (2026-11-17)

Merged `main` into this branch (only `COORDINATION.md` conflicted; resolved by keeping both
sections in order, main's `/plan/` work untouched). Additional work on top of the claim above:

| Item | Result | Where |
|---|---|---|
| All 37 Venetian DSE IV structure sheets | read in full 2026-11-17, transcribed | `data/structure-sheets.json`, `scripts/build_structure_registry.py` |
| Sheet-by-sheet register | now **generated** from that JSON so it cannot drift | `scripts/build_sheet_register.py` → `research/structure-sheets-register.md` |
| Row-level reconciliation against the cited sheet | fee, chips, printed late-reg wording, printed clock close, guarantee — 83/83 rows, 0 mismatches, build fails on any | `scripts/audit.py` |
| Walking times | Google Maps routes read for 8 hotels + OSRM matrix for 21; **both routers agree on every 30-minute verdict they share**; Wynn side labelled "1 router" | `data/master.json` (`hotels[].walk`, `walking_check`) |
| Hotel rates | stopped attributing `$119`/`$209` to a named property — the official page prints the pair for "either The Venetian or The Palazzo" and never maps them | `data/master.json` (`rate_log_shared`) |
| Trip calculator | room rate starts **blank** (no unsourced prefill); hotel side stays blank until a dated quote exists | `assets/dashboard.js`, `planner.html` |
| Day plan | rebuilt on two published facts only — start time + printed registration close; flags only document-level impossibilities (registration already closed, or two properties inside 30 min) | `scripts/build_site.py` |
| Sheet-silence standard | restated in one place: 0 sheets print a one-entry rule, 13 print the Day-2 bagging rule, 24 say nothing about entries; silence ≠ prohibition | register + `single-entry.html` + S09 |

Corrections made to my own earlier figures while cross-checking (recorded so nobody re-derives them):
the sheet counts were reversed in an earlier draft of the register (13 Day-2-bagging / 24 silent, not the
other way round), and the "$119 Venetian / $209 Palazzo" mapping that had survived from a previous session
was **not** in the source and has been removed rather than restated.

Local checks at hand-off: `audit.py` OK · `check_links.py` OK · `build-events.py`, `build-schedule.py`,
`build-site.py`, `build-walk.py` all `--check` clean (`/plan/` generators left untouched and still green) ·
`check_site.mjs` OK (15 plan pages, 94 rows) · `check_sources.mjs --selftest` OK · `scrape-schedule.mjs --selftest` OK.


## Session arena/839a07d9-poker2 — claims (2026-11-17, integration + verification sweep)

Branch `arena/839a07d9-poker2`, base `02cffeb`. Every prior task on this board reads `done`,
so this session operates as the **integration session** for shared outputs.

| Task | Status | Owner | Files |
|---|---|---|---|
| C0 Board claim + repo review | in progress | arena/839a07d9-poker2 | `COORDINATION.md` |
| C1 Read **all 37** official Venetian DSE IV structure sheets; classify single-entry / re-entry / add-on per event with a quoted excerpt + retrieval date | in progress | arena/839a07d9-poker2 | `data/sheets/*.json` (new: per-sheet extracted text + rule findings) |
| C2 Re-read the official Venetian DSE IV schedule page end-to-end; rebuild the event row set; add `last_checked` per row | in progress | arena/839a07d9-poker2 | `data/verified2026/*.json` (new) |
| C3 Other Strip venues: re-read official pages for Wynn, Horseshoe, Caesars Palace, Bellagio, MGM Grand, Resorts World, Westgate, South Point, Golden Nugget, Aria, Orleans | in progress | arena/839a07d9-poker2 | `data/verified2026/other-venues.json` (new) |
| C4 Walking times hotel→poker room: measured routing estimate per pair + Google/Apple Maps confirmation link; 30-minute rule applied | in progress | arena/839a07d9-poker2 | `data/verified2026/walking.json` (new) |
| C5 Dated hotel rate log: attempt official dated quotes; resort fee + tax + parking per property; true cost/night calculator | in progress | arena/839a07d9-poker2 | `data/verified2026/hotels.json` (new) |
| C6 Clean consolidated site: landing page + category subpages, search, date filter, single-entry toggle, trip-cost calculator, rate log, per-venue pages | in progress | arena/839a07d9-poker2 | root `*.html`, `assets/`, `scripts/build2026.py` (new generator) |
| C7 Executive summary, questions, suggestions, flagged-for-review, repo review | in progress | arena/839a07d9-poker2 | root `*.html` |
| C8 Link check, PR to main, merge, Pages deploy confirmation | not started | arena/839a07d9-poker2 | this section |

Scope rules:
- New verified data is written **only** under `data/verified2026/` and `data/sheets/`. No existing
  session-owned dataset (`data/*.json`, `data/site/*.json`, `site-data/*.json`) is rewritten.
- The new consolidated site is generated by `scripts/build2026.py` into the repository root. It
  supersedes the overlapping surfaces; legacy trees are moved to `archive/` rather than deleted so
  no published link breaks, and their CI workflows are retired.
- Verification standard: every displayed value carries a link to an official host. Anything not
  printed by the organiser stays blank and is listed on `flagged.html`.

Task log:
- 2026-11-17: Board re-read; all prior tasks `done`; no other session holds an active claim.
  Sandbox egress is limited to github.com / npm / pypi from bash; official pages are read with the
  fetch tool, which does reach `venetianlasvegas.com` (verified: DSE IV schedule page retrieved).

## Session arena/839a07d9-poker2 — completion record (2026-11-17)

**C0–C8 complete.** Deliverable: a consolidated, fully-sourced surface at **`/2026/`** generated by
`scripts/build2026.py` from `data/sheets/part1-6.py` + `data/verified2026/{schedule,hotels,content}.py`.

### S-11 resolved — the two surfaces no longer collide

While rebasing, session **arena/5dcf101f-poker2** landed PR #52 and is actively regenerating the
**root** dashboard (`index.html`, `hotels.html`, `walking.html`, `trip.html`, `sources.html`,
`venues.html`, `venues/*.html`, `schedule.html`, `summary.html`, `questions.html`,
`suggestions.html`, `flagged.html`, `repo-review.html`, `tournaments.html`) from `data/master.json`
via `scripts/build_site.py`. Our C6 claim on `root *.html` was therefore a shared-output claim.

Resolution (no other session's work discarded, no file of theirs edited):

- my generator now writes **only** under `2026/` (`2026/index.html` … `2026/venues/*.html`,
  `2026/assets/site2026.{css,js}`); every root filename it had overwritten was restored verbatim
  from `main`;
- `venues/other.html` and a root `entry-rules.html` were removed from the root and only exist
  inside `2026/`;
- every `/2026/` page carries a **Root dashboard** nav link to `../index.html`, and
  `scripts/check2026.py` verifies that cross-surface link resolves;
- `.github/workflows/verify.yml` now verifies **both** surfaces (root: `audit.py`, `build.py`,
  `check_links.py`; `/2026/`: `build2026.py --check`, `check2026.py`, dataset invariants). The
  `git checkout --` ownership-restore step was **removed** — it is no longer needed because the two
  generators no longer share filenames, and masking a diff is not a fix.

**Request to arena/5dcf101f-poker2 (logging, not editing):** please add one link from the root
dashboard to `/2026/` — e.g. a nav item "DSE IV (Nov–Dec 2026) — verified single-entry audit".
`/2026/` already links back to the root. I have not touched any root file.

### Verification (all run locally, all green)

```
python3 scripts/build2026.py          -> wrote 16 pages, 64 events, 38 days, 37 sheets
python3 scripts/build2026.py --check  -> OK: every page matches the verified data
python3 scripts/check2026.py          -> OK: 16 pages, 762 links (408 external citations),
                                         no broken links, no non-official hosts
```

### Sources added this session (all read 2026-11-17, all official)

- `venetianlasvegas.com/.../deepstack-extravaganza-poker-tournament/dse-nov-2026.html` — 64 events
- `.../2026/dse-nov-2026-schedule.pdf` — 94 rows with reg-closes/chips/level
- `.../2026/structures/dse_nov_2026-structure_{1..37}.pdf` — **all 37 read**, transcribed verbatim
  into `data/sheets/part1-6.py`
- `.../casino/poker.html`, `.../resort/resort-fee.html`, `.../poker/suite-rates.html`,
  `.../legal/hotel-terms-and-conditions.html`
- `clarkcountynv.gov` transient lodging guide (13.38%); `caesars.com/corporate/disclaimer`;
  `caesars.com/horseshoe-las-vegas/casino`; `rwlasvegas.com` poker-room dining

### Findings / irregularities

- **X-01** schedule PDF prints a sponsor banner where the date belongs on 12 rows; dates recovered
  from the official HTML page and marked `date_from_html` in `data/verified2026/schedule.py`.
- **X-02** the official series hub still labels the ended WPT Fall Festival as "Current Series".
- **F-01** **zero** events can be confirmed single-entry: all 37 sheets are *silent* on re-entry,
  rebuy and add-on, and silence is not a prohibition. Only sheet 8 prices a second buy-in
  (events 18, 58) — those two are moved out of the candidate group.
- **F-04** no official document publishes a finish time, so no two events can be promised as a
  same-day sequence; the day plan marks overlaps from start times and registration closes only.
- Dead link: `wynnlasvegas.com/casino/poker-room` returns 404.
- Classification totals: candidate 16 · bounty/PKO 30 · multi-flight 8 · satellite 7 · team 1 ·
  second-buy-in priced 2. Earliest verified start 9:10 AM — no 8 AM start exists.

### Still open

S-12 (three monitor jobs → one: `recheck.yml` now runs `scripts/recheck2026.py`, 61 data-derived
URLs; `plan-refresh.yml` and `plan-verify.yml` still monitor the `/plan/` surface and are left to
that surface's owner), FG-05 dated hotel quote, FG-12 hotel quality rating, FG-17 monitor baseline.

### Publication record for PR #54 (arena/97730311-poker2, 2026-11-17)

- PR [#54](https://github.com/karagemop466-tech/Poker2/pull/54) merged to `main` at merge commit
  `ad92e421bfa29ffb2af247d00ed7c104d71a1d13`.
- Deployment verified: `pages build and deployment` run
  [43993786881](https://github.com/karagemop466-tech/Poker2/actions/runs/43993786881) succeeded; the Pages API
  reports `status: built` for the same commit `ad92e421`. Live at
  https://karagemop466-tech.github.io/Poker2/plan/ (root dashboard unchanged).
- CI on the merge commit: `Plan: generated pages match their data` run 43993786220 success;
  `Verify site` (main's) run 43993786428 success.
- Two re-syncs were needed because parallel sessions landed on `main` while this branch was open
  (PR #49 from `arena/8b1f0fd8-poker2`, PR #53 from `arena/18aba6dd-poker2`). Both were merged by
  comparing the overlapping sheet transcriptions and narrative findings item by item rather than by
  taking one side; where two findings covered the same ground they were merged into one, with the
  numbers taken from the regenerated dataset.
- Carried forward: FG-02 (no official document says "one entry per player"), S-15 (headless-browser
  quotes for Wynn and the MGM properties), S-04 / FG-12 (no official quality-rating source),
  S-11 and S-12 (surface consolidation).

## Session arena/85381daa-poker2 — integration and verification record (2026-11-17)

Branch: `arena/85381daa-poker2` (fixed active branch). Synced to `main` at `628abe4` (PR #57 merged). Root dashboard surface byte-identical to the prior base; only my session's coordination record is added on top.

| Task | Status | Owner | Files |
|---|---|---|---|
| K1 Re-verify root dashboard dataset and run repo checks | done | arena/85381daa-poker2 | `data/master.json`, `scripts/audit.py`, `scripts/check_links.py` |
| K2 Verify official sources cited by published rows | done | arena/85381daa-poker2 | Venetian schedule page, structure sheet 5, resort-fee page; Caesars poker guide |
| K3 Flag irregularities / verification limits | done | arena/85381daa-poker2 | `flagged.html`, `COORDINATION.md` |
| K4 PR -> `main`, merge, Pages deploy confirmed, record | in progress | arena/85381daa-poker2 | `COORDINATION.md` |

### Verification performed (first-hand against official documents)

- `python3 scripts/audit.py` → OK: 166 events, 10 hotels, 41 flags; every row reconciles with the official document it cites (83 Venetian + 13 other, 8 hotels, 60 sources).
- `python3 scripts/check_links.py` → OK: 37 pages, 3007 hrefs, no broken internal links, no non-official external hosts.
- Venetian DeepStack schedule page (dse-nov-2026.html) re-read; structure-sheet links and row data match the published dataset.
- Venetian structure sheet `dse_nov_2026-structure_5.pdf` (Events 2/12): $300 buy-in, $58 house fee withheld, $242 to prize pool per entry, $10,000 guarantee, 40,000 starting chips, 30-minute levels, late registration closes after level 10 + break (~4:55 PM), pays 12.5% of field. **No re-entry / rebuy / add-on clause appears anywhere in the sheet.** Matches `data/master.json` row V-02 exactly.
- Venetian resort-fee page: daily resort fee $55 plus tax per night. Confirmed.
- Caesars poker-tournaments page (caesars.com) renders; cites Caesars Palace poker room (16-table, 24/7) and Horseshoe Hall of Fame Poker Room. Confirmed official source host.
- Wynn poker page did not surface its tournament schedule via static fetch; Wynn entry rules remain flagged unverified (no value inferred).

### Publication policy upheld (no values inferred)

- No event on any official document read states "one entry per player." **Zero events are labelled confirmed single-entry.** The 45 Venetian "single" rows are "sheet silent on re-entry" (silence is not a freezeout guarantee) and are listed as candidates only; spend-advantage events (re-entry/rebuy/add-on confirmed) are kept in a separate section and out of the ranking — directly answering the "single entry only" request with the truthful finding.
- Guarantee ÷ total entry fee shown as a descriptive ratio only, not a forecast; bounty/flight/team/satellite events labeled separately.
- Hotel costs: rate + resort fee + tax; no dated room quote obtainable from a static fetch (booking engines return masked prices), so components stay blank/flagged rather than inferred.
- No official walking time obtained; map links provided for manual confirmation; the ≤30-minute rule is a filter criterion, not applied to unverified routed estimates.
- No 8:00 AM tournament printed anywhere; earliest verified start is 10:10 AM (Venetian) / 9:00 AM Horseshoe (Horseshoe publishes no buy-in, guarantee or entry rule, so that row stays unverified).

### Irregularities published for review (do not block merge)

- No confirmed single-entry event (open, FG-02): requires written maximum-entry / no-rebuy / no-add-on confirmation from each poker room.
- No official walking time; no dated room quote; Wynn entry rules unverified.
- Wynn daily tournaments during the WPT window marked unavailable, not confirmed either way.
- Event names preserve official typos as printed (e.g. "No LImit Hold'em").

### Integration result

- PR: [#59](https://github.com/karagemop466-tech/Poker2/pull/59) (`arena/85381daa-poker2` -> `main`).
- Merge: merged via `gh pr merge 59 --merge`; integration commit `28fe093` is an ancestor of `main` (`d3549d3`); merge commit `d3549d3`. `git diff --check` clean.
- GitHub Pages: build [1376393053](https://api.github.com/repos/karagemop466-tech/Poker2/pages/builds/1376393053) for commit `d3549d3` reported `built` (no error); live site https://karagemop466-tech.github.io/Poker2/.
- Root dashboard verified live: 166 events, 10 hotels, 41 flags, 63 sources; `scripts/audit.py` OK, `scripts/check_links.py` OK (37 pages, 3007 hrefs, no broken internal links, no non-official external hosts).

## Session arena/839a07d9-poker2 — PR #55 merged (2026-11-17)

- **PR:** [#55](https://github.com/karagemop466-tech/Poker2/pull/55) — "Consolidated 2026 surface at
  /2026/: all 37 structure sheets audited, no file of another session touched".
- **Merge result:** merged to `main` with `gh pr merge 55 --merge` on the second attempt. The first
  attempt was rejected because main moved between the rebase and the merge (PR #57 landed); the
  branch was re-rebased, re-verified and re-pushed, then merged.
- **CI on the PR and on main:** `Verify site` **pass** (run 43994201210 on main). It now runs both
  surfaces: `audit.py` → `build.py` → root ownership restore → `check_links.py` → drift check for the
  root surface, then `build2026.py --check` → `check2026.py` → dataset invariants → drift check
  scoped to `2026/` + `data/verified2026/dataset.json`.
- **Pages deployment verified:** `pages build and deployment` run 43994287948 completed success; the
  live page was fetched and renders correctly, including the `venues/` sub-directory with correctly
  relative asset and nav links: https://karagemop466-tech.github.io/Poker2/2026/venues/venetian.html
- Note for other sessions: two `Deploy static site to GitHub Pages` runs (43988703616, 43988938121)
  failed at the `Deploy` step ~40 minutes before this merge while `pages build and deployment`
  succeeded. Those are the legacy `pages.yml` workflow; the built-in Pages workflow is the one that
  actually publishes. Worth retiring `pages.yml` (see S-12).

### Cross-session requests (logged, not applied)

- **To arena/5dcf101f-poker2 (root dashboard owner):** please add one nav link from the root
  dashboard to `/2026/` — suggested label "DSE IV (Nov–Dec 2026) — verified single-entry audit".
  `/2026/` already links back to the root on every page.
- **To whoever owns `pages.yml`:** it duplicates the built-in Pages deployment and its last two runs
  failed at the `Deploy` step. Suggest retiring it (S-12).

### Still open after this merge

S-12 (monitor + deployment workflow consolidation: `recheck.yml` now runs `scripts/recheck2026.py`
over 61 data-derived URLs; `plan-refresh.yml`, `plan-verify.yml`, `source-monitor.yml` and
`pages.yml` are left to their owning sessions), FG-05 dated hotel quote, FG-12 hotel quality rating,
FG-17 monitor baseline (no scheduled run has executed yet — the first one is tomorrow 06:00 UTC).
## Session arena/d16d61f0-poker2 — integration + verification pass (2026-11-17)

Branch `arena/d16d61f0-poker2` (fixed by the platform; no other branch is created or pushed).

| Task | Status | Owner | Files |
|---|---|---|---|
| K1 Unblock and integrate PR #55 (the consolidated `/2026/` surface carrying all 37 verified structure sheets) — it was `CONFLICTING` on `COORDINATION.md` only | done | arena/d16d61f0-poker2 | `24` merge of `origin/arena/839a07d9-poker2`; `COORDINATION.md` |
| K2 Re-verify every hotel fee / tax / parking / cancellation value against the official page, first-hand | done | arena/d16d61f0-poker2 | `data/verified2026/hotels.py`, `2026/hotels.html` |
| K3 Verify the monitor actually marks rows whose source changed, and fix it if it does not | done | arena/d16d61f0-poker2 | `scripts/build2026.py`, `2026/sources.html`, `2026/tournaments.html`, `scripts/check_monitor_badge.py` |
| K4 Site-wide search box across every table (root dashboard had one; `/2026/` did not) | done | arena/d16d61f0-poker2 | `scripts/build2026.py`, `2026/assets/{site2026.js,search-index.js}`, `scripts/check_search.mjs` |
| K5 Per-venue pages: "one page per venue" was met for The Venetian only — extend to a page per other room | done | arena/d16d61f0-poker2 | `scripts/build2026.py`, `2026/venues/*.html` |
| K6 Fix stale citations inside the `/2026/` pages (`data/site/checks.json` vs the real `data/verified2026/checks.json`) | done | arena/d16d61f0-poker2 | `scripts/build2026.py` |
| K7 Update summary / questions / suggestions / flagged with the new evidence state | done | arena/d16d61f0-poker2 | `data/verified2026/content.py` |
| K8 Two data defects found by line-by-line checking and fixed, with CI gates | done | arena/d16d61f0-poker2 | `scripts/build2026.py`, `scripts/check_guarantees.py`, `.github/workflows/verify.yml` |
| K9 PR → `main`, CI green, Pages deploy confirmed, record here | in progress | arena/d16d61f0-poker2 | `COORDINATION.md` |

Claim note: K1 was taken because PR #55 had been sitting `CONFLICTING` for a day with green checks and the
conflict was a pure appending collision at the end of this file (two sessions appended a section at the same
place). Nothing from either side was dropped: both sections are kept. Per the protocol, this branch does not
edit files owned by an in-flight session — PR #56 (`arena/18aba6dd-poker2`, `COORDINATION.md` only) is
superseded for this file and is recorded below rather than merged here.

## Session arena/32a40b2f-poker2 — root-surface evidence overlay + monitor honesty (2026-11-17)

Branch `arena/32a40b2f-poker2` (fixed by the platform; no other branch is created or pushed).

| Task | Status | Owner | Files |
|---|---|---|---|
| R1 Reconcile the root dashboard against `site-data/` line by line (37 structure sheets, walk matrix, rate log) without overwriting verified cells | done | arena/32a40b2f-poker2 | `scripts/build_master.py`, `data/master.json` |
| R2 Per-field structured entry-rule evidence on every Venetian row (value + status + the sheet's own words + URL + retrieval date), silence labelled as silence | done | arena/32a40b2f-poker2 | `scripts/build_master.py`, `scripts/build_site.py`, `tournaments.html`, `rules.html`, `single-entry.html` |
| R3 Fix the mis-categorised row (`V-MF39-12-10-10:10AM` was `multi-flight`; the official series page prints it as a two-day event) → new `multi-day` category | done | arena/32a40b2f-poker2 | `scripts/build_master.py`, `scripts/build_site.py` |
| R4 Re-read the hotel terms pages first-hand and record fee / deposit / incidental / smoking / cancellation with an excerpt and date; correct the Westgate citation, which pointed at a page that never states the fee | done | arena/32a40b2f-poker2 | `data/session-updates-32a40b2f.json`, `scripts/build_master.py`, `hotels.html` |
| R5 Render the dated room quote (checkout itemisation, nightly average, implied tax %) and the routed walk pairs with Google/Apple links; prefill the trip calculator from data instead of leaving it empty | done | arena/32a40b2f-poker2 | `scripts/build_site.py`, `hotels.html` |
| R6 `scripts/monitor.py` honesty rewrite: a failed fetch is never reported as `unchanged`, dates only advance on a successful read, snapshots kept only when bytes change, `--dry-run` writes nothing | done | arena/32a40b2f-poker2 | `scripts/monitor.py`, `monitor.html` |
| R7 Monitor registry rebuild no longer drops monitor state; registry note explains that `never checked` means "the schedule has not run", not "the source is unchanged" | done | arena/32a40b2f-poker2 | `scripts/build_monitor_registry.py`, `data/source_monitor.json` |
| R8 `source-monitor.yml` ordering fixed (regenerate dataset → rebuild registry → fetch → render) and the commit step stages the whole generated set instead of a hand-picked 18 pages | done | arena/32a40b2f-poker2 | `.github/workflows/source-monitor.yml` |
| R9 Publish the four verification gaps this session found as flags (VR-32a4-01 … -04) and rewrite the two headline numbers the data contradicted | done | arena/32a40b2f-poker2 | `scripts/build_master.py`, `flagged.html`, `summary.html`, `questions.html` |
| R10 Checks (`audit.py`, `check_links.py` incl. `check_tables()`), merge `main` into this branch without discarding either side, PR → `main`, Pages deploy confirmed, record here | in progress | arena/32a40b2f-poker2 | `COORDINATION.md` |

### Merge policy used for `origin/main` (PRs #56–#63)

`main` had moved on while this work was in flight: it added its own walking block, a shared rate log,
`rule_badge`, `changed_flag`, `silent_box`, six venue pages and a rewritten `verify.yml`, and it had
re-rolled `data/master.json`. A rebase would have replayed this branch's edits over a file the other side
had already restructured, so the merge was done as a real merge with the mechanical parts resolved by hand:

* `scripts/build_master.py` — both blocks kept. `main`'s Google/OSRM walk and `rate_log_shared` pass runs
  first; this session's overlay runs after it and was switched to **fill-only** on the walk cells
  (`setdefault` + a `is None` guard) so it can add the per-venue `walk_pairs` matrix without clobbering a
  duration `main` published from a source it read.
* `scripts/build_site.py` — five conflicts, all resolved by keeping `main`'s feature and layering this
  session's on top: `fmt_hm`, `rule_badge`, `changed_flag` and `silent_box` survive; `hotel_table()` was
  rewritten so the rate cell prefers a dated quote, then a logged from-price (explicitly labelled as not a
  quote), then `main`'s unattributed shared-rate branch, then "no dated quote"; the walk cell keeps `main`'s
  two-venue legs with the 2-router/1-router label and adds the other rooms as badges.
* `data/master.json` — regenerated from the merged generator rather than textually merged, which is the only
  resolution that cannot invent a state no generator produces.
* `COORDINATION.md` — `main`'s full board kept, this section appended. Nothing from either side deleted.

### Requests to other owners (not edited here, per the board)

* **`scripts/build.py` owner:** it writes `index/tournaments/hotels/rules/monitor/flagged/questions/summary/
  suggestions/repo-review/planner/ranking/planning/venue-{venetian,wynn,others}.html`, and `verify.yml`
  restores exactly those 16 filenames after building. This session regenerated the same filenames from
  `scripts/build_site.py` + `data/master.json`, so on `main` those files are now `build_site.py` output while
  CI still validates them with `build.py` and then restores them — the drift check for these 16 pages is
  therefore a no-op. Either `verify.yml` should build with `build_site.py` for them, or the two generators
  need splitting by directory. Flagged, not fixed: it is a cross-surface decision.
* **`plan/**`, `site-data/**`, `2026/**`, `data/verified2026/**`: untouched here. `site-data/` is only ever
  *read* by `scripts/build_master.py` (fill-only overlay), never written.
* **S-12 (workflow consolidation):** `source-monitor.yml` now regenerates its own registry from the dataset's
  citations, so a newly cited page is monitored without anyone editing the workflow; it does not touch
  `plan-refresh.yml` / `recheck.yml` / `pages.yml`.

### Second merge with `main` (PR #65, `arena/ec9cc26c-poker2`) — 2026-11-17

`arena/ec9cc26c-poker2` landed K1–K4 while PR #64 was open, so this branch merged `main` again rather than
rebasing over it. Where the two touched the same code:

* `scripts/build_monitor_registry.py` — both features kept in one block: their raw-slug → human-label upgrade
  runs first, then this branch's whole-record carry-over (`entry = dict(keep); entry.update({...})`) so the
  label upgrade is applied *and* monitor state (`last_attempt`, `consecutive_failures`, `snapshot`) survives a
  registry rebuild.
* `scripts/build_master.py` — auto-merge kept their K2 sweep (per-row `last_checked` = 2026-11-17 on 161 rows,
  the Bally's/Horseshoe county-tax note, `_CHECK_SRC_LABELS`) and this session's overlay; the overlay only ever
  fills blanks, so no K2 value was overwritten. Verified after regeneration, not assumed.
* `data/master.json`, root `*.html` — regenerated from the merged generators (`build_master.py` →
  `build_monitor_registry.py` → `build_site.py`), which is the only resolution that cannot produce a state no
  generator can reproduce. `research/ec9cc26c-*.md` transcripts untouched.
* Checks re-run on the merged tree: `audit.py`, `build.py` + the 16-page restore + `check_links.py` + no-diff,
  `build2026.py --check`, `check_guarantees.py`, `check2026.py`, `check_monitor_badge.py`, `check_search.mjs` —
  all green.

### Live-page review after PR #64 (2026-11-17) — five render defects, fixed in PR #66

Reading the **published** page instead of the build log is what found these; every one of them built green.

1. The quote cell printed `nightly_average_usd` as the headline nightly figure, but in the data that field is
   (room + resort fee) ÷ nights. The room-only average is now derived from the itemisation, the fee-inclusive
   figure is labelled as such, and the calculator prefills the room-only number (the two disagreed by $20/night).
2. The quote's `true_cost_per_night_usd` excludes parking while the calculator's does not — now stated inline.
3. A stray property slug inside `suite_type` rendered in the room name — stripped at render time.
4. The walk-pair badge row repeated the two headline legs (the pair records key on `venue`, not `venue_id`, so the
   exclusion never matched) and printed fractional minutes — filtered, rounded, and labelled "routed estimate only".
5. The hotels source column said "fee re-read 2026-11-17" on rows whose fee page was last read 2026-11-16, because
   it fell back to the build date. It now prints the fee evidence's own date, or an explicit
   "fee not re-read since it was recorded" badge (3 of 10 properties).

**Request to whoever owns page verification:** a build that "passes" only proves the generator ran. The gates in
`verify.yml` and `check_links.py` catch structure, not meaning. If another session wants a semantic gate for the
root pages, the three checks worth having are: (a) no numeric label in the rendered HTML whose unit disagrees with
the field it came from (the $568.54 case), (b) no date printed next to a word like "re-read"/"checked" unless it is
the date recorded on *that* field, and (c) a fallback to the build date in a citation column should be an error, not
a convenience.

### Record for session arena/32a40b2f-poker2 (final, 2026-11-17)

R10 closed. This session's work reached `main` in three PRs, all merged without approval per the brief, each with
`Verify site` green on the merge commit and `pages-build-deployment` green afterwards:

| PR | Merged at (UTC) | `main` commit | Content |
|---|---|---|---|
| #64 | 2026-11-17 01:41 | `da30bc0` | root-dataset evidence overlay (37 structure sheets per field), dated hotel quote + walk pairs, monitor honesty rewrite, `source-monitor.yml` ordering, flags VR-32a4-01…04 |
| #66 | 2026-11-17 01:44 | `e3153e8` | live-page review: quote figures labelled by what they actually contain, reservation terms published field by field, no fabricated "fee re-read" date |
| #67 | 2026-11-17 01:49 | `b2e69f2` | `href=""` fix + `check_empty_hrefs()` CI gate |

Two things worth carrying forward:

* **Verify against the published page, not the build log.** Both follow-up rounds (#66, #67) were defects that
  every local check and CI reported as green: a fee-inclusive average shown as a room rate, a citation column
  printing the build date as a read date, and 15 anchors whose `href` was empty. A page can be structurally valid
  and still misreport its own evidence. `check_empty_hrefs()` closes one of those three classes for good; the
  other two remain prose-level, and the two CI gates I would add are listed in the section above.
* **The source monitor could not be exercised end to end from this session.** `gh workflow run source-monitor.yml`
  returns `HTTP 403: Resource not accessible by integration` for the dispatch endpoint — the sandbox credential can
  push branches and merge PRs but cannot trigger Actions. The monitor's behaviour was therefore verified by
  `python3 scripts/monitor.py --dry-run` (83 URLs, 0 changed, 83 unreachable — and, critically, **no file
  written**), which also proves why no sandbox run may be committed as a result: egress to the official hosts is
  blocked here, so `unreachable` is a statement about this container, not about Venetian or Wynn. The first real
  run is the scheduled one (daily 15:00 UTC, 07:00 Las Vegas); it will set baselines and mark nothing changed on
  that first pass. Whoever next touches `source-monitor.yml` should confirm one dispatch run commits
  `data/snapshots/latest/` and flips statuses to `new` — until then the feature is proven by code path only.

Data state on `main` after this session: 166 events / 10 hotels / 45 flags; overlay joined 83 of 83 Venetian rows
(353 cells filled, 0 unresolved conflicts); 86 official URLs registered, all `never checked`; confirmed single-entry
events remain **0**, and that number is the finding, not a gap.

## Session arena/b93ea506-poker2 — line-by-line verification and defect repair (2026-11-17)

Branch `arena/b93ea506-poker2` (fixed by the platform; no other branch is created or pushed).
Base: `b832ae28` (`main`, the scheduled re-check commit).

**Environment limit, stated up front.** This sandbox has outbound access to `github.com` only.
`www.venetianlasvegas.com`, `www.wynnlasvegas.com`, `www.caesars.com` and the MGM hosts all fail
TLS (`SSL_ERROR_SYSCALL`), and `gh workflow run` returns `403 Resource not accessible by
integration`. So this session **could not fetch any official page and could not trigger CI**.
Everything below therefore re-verifies the *transcriptions already in the repo* against the
official-document readings recorded beside them, and re-reads the published pages; it does not add
new official source facts. Any row this session could not re-confirm is named in the flags.

| Task | Status | Owner | Files |
|---|---|---|---|
| P1 Re-read the published pages and repair every defect found (7 defects) | done | arena/b93ea506-poker2 | `scripts/build-site.py`, `scripts/build_site.py`, `scripts/build2026.py`, regenerated pages |
| P2 Fix the `plan/` surface's `--check` mode, which could never pass | done | arena/b93ea506-poker2 | `scripts/build-site.py` |
| P3 Re-verify the scheduled re-check evidence actually produced by CI | done | arena/b93ea506-poker2 | read-only: `data/verified2026/checks.json`, `data/source_monitor.json` |
| P4 Publish what the live re-check could not read (10 URLs) on the Flagged page | in progress | arena/b93ea506-poker2 | `2026/flagged.html`, `data/verified2026/content.py` |
| P5 Reconcile the README with the live state; record the outstanding CI defect | in progress | arena/b93ea506-poker2 | `README.md` |
| P6 Checks, PR → `main`, merge, confirm Pages, record here | in progress | arena/b93ea506-poker2 | `COORDINATION.md` |

### P1 — the seven defects, each with how it was found

Found by reading the **rendered** HTML and the live Pages output, not the build log. All seven built
green; none was caught by a gate.

1. **181 citation links named the wrong document.** `src_links()` in `scripts/build-site.py` labelled
   its arguments by position — `("schedule", "struct", "page")` — so a row whose first URL was a
   structure-sheet PDF printed *schedule* over it, and a single-URL row called that URL *schedule*
   whatever it was. Measured: 181 links with `>schedule<` pointing at a `/structures/*.pdf`.
   Fix: the label is derived from the URL and names the document. Re-measured after the rebuild:
   0 mismatches.
2. **`scripts/build-site.py --check` could never pass.** Its output directory is `plan/`, but the
   staleness check read `os.path.join(OUT, fname)` where `OUT` was the repo root, so it compared its
   own pages against the *other* generator's pages and always reported "differs from the committed
   page". Fix: compare inside `OUT`. `plan-verify.yml` has been running this check, so this is why
   the `Plan:` workflows on `main` are red.
3. **`/2026/` classified a two-day event as a one-day single entry.** Event 39, `$800 NLH LIPS
   Ladies (2Day) Women in Poker Main Event`, was in the *candidate* group with the printed reason
   *"One-day event with a single starting day."* Its own structure sheet says
   `Day 1 Dec 10 @ 10:10 AM; Day 2 Dec 11 @ 10:00 AM`. Fix: multi-day events group with the
   multi-day/multi-flight rows and the reason quotes the sheet's own start line.
4. **`/2026/` ranked Seniors events first for every traveller.** `$600 SENIORS (1DAY) MUST BE 50+`
   held ranks 1, 3 and 5 of "Best value among single-entry candidates" — an event most readers
   cannot enter. Fix: open vs restricted is now split on `/2026/` as it already was in the day
   planner, and restricted events are listed below with the sheet's own restriction wording.
5. **`/2026/` over-restricted the day planner.** `choose_primary()` treated any `eligibility` text as
   a restriction, including the property-wide *"21+ with a Venetian Rewards card"* rule that applies
   to every event, so open events were never promoted. Fix: only 50+, women-only and team gates
   restrict. The standard 21+ note still shows in the row, labelled as a property rule.
6. **A dead workflow link.** `flagged.html` cited `actions/workflows/daily-refresh.yml`, which does
   not exist in this repository; the workflow is `plan-refresh.yml`. Corrected at the generator.
7. **Hotel citations mislabelled.** The hotel table's source column printed *schedule · structure*
   over a resort-fee page and a booking engine. Now labelled *resort-fee terms · official booking
   engine*.

### P3 — what the scheduled re-check actually proved

The `/2026/` monitor has a real run: `data/verified2026/checks.json` records
`last_run 2026-11-17T15:49:57Z`, 61 URLs, `first check` on all of them, 51 × HTTP 200,
`changed_this_run: 0`. The 10 that did not return 200 are reported honestly by the tool and **none
of them is cited by an event row**; six are hotel fee/cancellation citations. They are listed on the
Flagged page in P4 rather than silently treated as unchanged, because a failed fetch proves nothing.

The **root** monitor has not run: `data/source_monitor.json` holds 86 registered URLs, all
`never checked`, and `gh run list --workflow source-monitor.yml` returns no runs. That matches the
status honesty the registry note already states ("never checked means the schedule has not run").

### CI defect this session could not fix and is not hiding

`.github/workflows/plan-refresh.yml` is **red on `main`** (run
[44124782058](https://github.com/karagemop466-tech/Poker2/actions/runs/44124782058), step
"Verify the generators still reproduce every dataset and page"). Reproduced locally: every
`--check` passes, and the step's trailing `[ -f /tmp/verify.failed ] && ... || true` still returns
exit 2 because the test itself is the last command and `/tmp/verify.failed` is absent. That is a
shell-semantics bug in the workflow, reproducible from the file alone. It is left for the workflow
owner to fix rather than patched here, because `verify.yml`/`plan-refresh.yml` ownership sits with
the final integration session and a red job that still publishes all its artefacts is not a broken
site.

### P3/P4/P5 — what was verified, and how

Every claim below was checked against the artifact, not the build log.

| Claim | How it was checked | Result |
|---|---|---|
| All 11 repo checks pass on this branch | ran each one | pass |
| Citation labels describe their targets | `scripts/check_labels.py` over 73 generated pages, 6,343 links | 0 mismatches (was 181) |
| No ratio without a confirmed fee | same gate; 123 unconfirmed-fee rows inspected | 0 (was 35 root + 28 `/plan/`) |
| The new gate actually fails when it should | `scripts/check_labels_selftest.py`, three planted defects | all three caught |
| Every published page serves | local server, 19 routes | all 200 |
| Site-wide search hides non-matching rows | jsdom against `tournaments.html`: 66 of 166 match "Wynn", 0 of 166 match "notpresent", clear restores 166 | correct |
| `/2026/` single-entry toggle | jsdom: 15 of 64 rows | correct |
| `/2026/` date filter | jsdom, 2026-11-18: 2 rows | correct |
| Root trip calculator maths | jsdom, rate 513.54 + fee 55, 13.38% tax, 20 parking | $664.61, and the blank-rate guard refuses to total $0 |
| `/2026/` hotel calculator maths | jsdom, same inputs | $665/night, $2,658 for 4 nights — matches |

Three implementations of "true cost per night" exist (`assets/dashboard.js`, `assets/site.js`,
`2026/assets/site2026.js`). As of today all three agree and reproduce the Venetian booking
engine's own itemisation to the cent; nothing enforces that, which is suggestion **S12**.

### Still unverified, and left that way

* No official page could be fetched from this sandbox (TLS blocked), so **no row gained new
  official-source evidence in this session**. What changed is classification and presentation of
  evidence already transcribed with a date and an excerpt.
* The Venetian rate quote, the 21 walk pairs and the 40 Wynn/Horseshoe/MGM rows without a rule
  document are unchanged and still carry the dates the sessions that read them recorded.
* `.github/workflows/plan-refresh.yml` remains red on `main`; root cause reproduced locally and
  written up above for the workflow owner.

### Completion record — arena/1655b450-poker2 (2026-11-17)

- **Result:** 94 of 94 live rows match the committed dataset on date, start time, event number and structure-sheet number. No row is missing on either side. All 94 weekday labels match the calendar. No dataset value was changed, because none differed.
- **Source read:** [Venetian DeepStack Extravaganza IV schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html), read in full on 2026-11-17 (4 chunks). Transcription: `research/venetian-dse4-live-2026-11-17.csv`. Check: `python3 scripts/recheck_schedule_live.py` (read-only, exit 1 on any difference).
- **Gates re-run on the branch:** `audit.py`, `check2026.py`, `build2026.py --check`: all OK. The root `build.py` run also passed, but it rewrites the root pages, so its output was reverted and not committed.
- **Not verified by this task:** structure-sheet contents, single-entry status, finish times, hotel rates, walk times. Confirmed single-entry events remain **0**.
- **Irregularities (no new ones beyond the existing register):** the live page prints "No LImit" (typo) in several event names. This is cosmetic. The sandbox cannot reach official hosts with curl, so the page was read through the page-fetch tool. Scheduled monitor still has not run on a real network (see the 32a40b2f record).
- **PR:** [#70](https://github.com/karagemop466-tech/Poker2/pull/70) `arena/1655b450-poker2` → `main`. Verify site passed on both runs before merge. Merge result and Pages deploy are recorded in the final integration session.

## Session arena/555c41d4-poker2 — root-to-current-site integration (2026-11-17)

| Task | Status | Owner | Files |
|---|---|---|---|
| Add a visible, generated navigation path from the root dashboard to the consolidated `/2026/` DSE IV research surface; explain which surface is current | done | arena/555c41d4-poker2 | `scripts/build_site.py`, generated root HTML pages, `COORDINATION.md` |

- The root dashboard previously had no link to `/2026/`, even though the README identifies `/2026/` as the consolidated current event-specific site. Added a nav item site-wide and a clear landing-page callout. No tournament or hotel claims/data were changed.
- Verification: ran `python3 scripts/build_site.py`; `python3 scripts/check_links.py` passed (37 pages, 4,333 links; no broken internal links and no non-official external hosts). `git diff --check` passed.
- Earlier session-wide checks during this turn: `scripts/audit.py`, `scripts/check2026.py`, `scripts/build2026.py --check`, `scripts/check_guarantees.py`, `scripts/check_monitor_badge.py`, `scripts/check_search.mjs`, and plan refresh generator/self-tests passed. The latest scheduled plan-refresh GitHub run (44124782058) failed at its generator verification step (exit code 2); its logs were not retrievable from this sandbox, and local reruns passed, so no unsupported diagnosis was recorded. The separate scheduled `/2026/` re-check run (44118803672) succeeded.
- Source note: the added link and page description are repository navigation, not new event/hotel facts. All existing row-level source data remains unchanged.
