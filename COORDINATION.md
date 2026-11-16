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

| Dashboard in `docs/` (official-source tables, schedule, hotels, flagged, repo review) | done (flags published) | arena/acd81e67-poker2 | `docs/*`, `data/*.json`, `scripts/build_site.py`, `scripts/check_links.py`, `COORDINATION.md` |

## Session arena/acd81e67-poker2 — task log
Site: [docs/index.html](docs/index.html) (served at `/Poker2/docs/`). The root site above is untouched.

- Source of truth: official Venetian schedule page (`dse-nov-2026.html`), read in full; every Venetian row is taken from that table. Structure PDF numbers come from the same table.
- Earlier drafts contained registration-close times, a few structure numbers and two URLs that had not been read in this session. Those were removed; they are not in the published data.
- Rows left blank and flagged: Caesars resort fee and address, Wynn resort-fee link, all hotel nightly rates, Clark County room tax, walking times, Golden Nugget buy-in, Horseshoe times, Wynn WPT schedule (HTTP 502), MGM time mismatch (flag F-03).
- Hotels: no hotel is fully verified. Only resort fees are official (Venetian $55 + tax; Wynn $55 + tax, link pending).
- Irregularities: see `docs/flagged.html` (F-01 … F-22).

### Integration result (T7)
- PR: (to be recorded after creation)
- Merge result: (to be recorded)
- Pages deploy: (to be recorded)
