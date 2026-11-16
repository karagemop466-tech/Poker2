# Coordination board

| Task | Status | Owner | Files |
|---|---|---|---|
| Integrated research dashboard, source audit, and GitHub Pages site | done | arena/dc12202f-poker2 | `COORDINATION.md`, `README.md`, `index.html`, `styles.css`, `app.js`, `.github/workflows/pages.yml` |

## Task log
- 2026-11-16: Claimed integrated dashboard/site scope on the session's fixed active branch. Repository initially contained only an 8-byte README; no existing board or parallel claims. Official source reviewed: Venetian DeepStack tournament schedule page (https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) and series overview (https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html). Schedule includes upcoming late-November/December 2026 events; the only verified indexed schedule source was for Venetian. Hotel rate/date-specific totals and walking routes have not been verified and will be left blank/flagged. Remaining local tournament details must be checked against the linked official schedule before promotion.

## Constraints and verification notes
- Work stayed on current branch `arena/dc12202f-poker2`; no alternate session branches were created.
- The listed schedule is a sourced subset, not claimed exhaustive. Dynamic schedules and fees can change; source/date remain visible, and unverified tournament entry rules are flagged.

## Completion record
- Official sources checked on 2026-11-16: [Venetian DeepStack IV event schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html), [Venetian series overview](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html), [Venetian offers](https://www.venetianlasvegas.com/hotel/offers.html), and [Venetian booking](https://www.venetianlasvegas.com/book). Event rows cross-checked to schedule; no event promoted as verified single-entry because the rules are not established in schedule summary. Hotel nightly total and walk times intentionally blank because trip dates/occupancy and confirmed checkout quotes/routes are absent.
- Checks: internal anchor audit passed (8 in-page anchors, 0 missing); `git diff --check` passed; Pages workflow run [43930555829](https://github.com/karagemop466-tech/Poker2/actions/runs/43930555829) succeeded; Pages status built at https://karagemop466-tech.github.io/Poker2/.
- PR [#2](https://github.com/karagemop466-tech/Poker2/pull/2) merged 2026-11-16. Irregularities are published in the site's Flagged for Review section: unresolved entry/add-on terms, RaceDay Stack mechanics, overlapping starts, missing exact-date hotel quotes and walking routes, and no confirmed 8 AM start.
