# arena/799d66c1-poker2 — final integration verification (2026-11-19)

**Session:** `arena/799d66c1-poker2` (final integration). **Base at start:** `a63a9c3` (PR #98 merge).
**End state:** rebased onto repaired `main` (`f0afe1b`), all checks green, site live.

## What this session did

1. Read `COORDINATION.md` and checked open PRs before starting.
2. Rebased the session branch onto the latest `main`. While the branch was open, other sessions
   completed and merged the remaining work: PR #102 (F-07 tax-flag correction + COORDINATION record,
   merged `d5d22ea`), PR #103 (`8ec92de`), PR #104 (`f0afe1b`), and two **"Repair main"** commits
   (`7edf1b7`, `e0be8ca`) that regenerated the root surface from its generators and removed a stray
   conflict marker. Those repairs resolved the root-surface drift that had appeared after #100/#101.
3. Confirmed the repaired root surface now **reproduces exactly** from `scripts/build_master.py` +
   `scripts/build_site.py` (no drift).
4. Ran the **full local verification suite** across both surfaces (root and `/2026/`). All checks
   exit 0. Results are recorded in `COORDINATION.md`.
5. Performed an **independent first-hand re-verification** of five official sources against the
   stored data, recorded below. No value changed.
6. Incorporated the last open completion-record PR (#99, doc-only) into this integration branch and
   closed it (its content is now on `main` via this PR).

## First-hand official-source verification (2026-11-19, UTC)

Every value below was read from the official document on 2026-11-19 and compared to the stored
dataset. **No discrepancies were found.** Links are for manual review.

| # | Claim verified | Official source (read 2026-11-19) | Result |
|---|---|---|---|
| 1 | Venetian DeepStack Extravaganza IV runs **Nov 16 – Dec 23, 2026**; schedule rows, event numbers, start times and structure-sheet links match the stored dataset (94 rows). | [Venetian DSE IV schedule](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) | Match. Row-for-row reconciliation also passes via `recheck_schedule_live.py` (94/94). |
| 2 | Venetian/Palazzo **resort fee = $55 plus tax per night**, payable at check-in. | [Venetian resort-fee page](https://www.venetianlasvegas.com/resort/resort-fee.html) | Match. |
| 3 | Venetian structure sheet 7 (Events 14, 28, 63): **$600 buy-in**, **$90 house fee**, **$510 to prize pool**, **40,000 starting chips**, **30-min levels**, late registration **10 levels + Break (~4:55 PM)**, guarantee **$30,000 (#14/#63)** and **$40,000 (#28)**, pays 12.5% of field, and prints **"Must be 21+ years of age and have a Venetian Rewards card to participate."** The sheet is **silent on re-entry / rebuy / add-on** — it states no single-entry rule. | [Sheet 7 PDF](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf) | Match. Silence confirmed; event stays **unconfirmed** single-entry (consistent with `check_sheet_readings.py`: 0 sheets print a one-entry clause). |
| 4 | Wynn: **WPT World Championship Nov 27 – Dec 21, 2026**; **Wynn Signature Series Jan 11–24, 2027**; daily tournaments **suspended during series**; **$40,000 GTD NLH Rebuy on Friday** and a **$10,000 GTD evening event at 6 p.m.**; weekly guarantees total $200,000. | [Wynn poker page](https://www.wynnlasvegas.com/casino/poker) | Match. |
| 5 | Clark County **transient lodging tax = 13.38%** for Primary Gaming Corridor (PGC) resort hotels (Bellagio, Caesars Palace, Excalibur, Flamingo, Harrah's, Gold Coast, etc.) — the calculator's default rate. | [Clark County TLE guide, Appendix III](https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf) | Match. The 13.38% PGC rate is published in the county's own rate table. **Caveat retained (flag F-07):** this is the county guide's rate table; the *current* county rate table has not been separately re-checked, so the site keeps the re-check caveat rather than asserting a fresh 2026 table read. |

## Verification suite (all exit 0, run locally on the repaired main)

Root surface: `audit.py`, `build.py`, `test_monitor.py`, `build_master.py`, `build_site.py`
(drift check clean), `check_root_surface.py`, `check_links.py`, `check_plan_fresh.py --strict`.

`/2026/` surface: `build2026.py --check`, `recheck_schedule_live.py` (94/94),
`check_sheet_readings.py` (37 sheets / 481 fields), `check_guarantees.py`, `check2026.py`
(24 pages, 1631 links, no broken links, no non-official hosts), `check_decisions2026.mjs`,
`test_recheck2026.py`, `check_monitor_badge.py`, `check_refresh2026.py`, `check_semantics.py`,
`check_decisions.mjs`, `check_search.mjs`, `check_trip.mjs`, `check_labels.py` + self-test.

## Irregularities / findings

- **Root-surface drift was real and is now fixed.** After PRs #100/#101, the committed root pages did
  not reproduce from `build_master.py`/`build_site.py` (a `json.dump` unicode-escaping mismatch plus
  stale regenerated content). The "Repair main" commits `7edf1b7`/`e0be8ca` regenerated the root
  surface from the generators and removed a stray conflict marker. This session confirmed the repair
  is complete: the root surface now reproduces with no drift. No further change was needed.
- **PR #99** (doc-only completion record) could not be merged cleanly because it was based on an
  older `main` and conflicted in the append-only `COORDINATION.md`. Its content was incorporated
  into this integration branch and the PR closed; nothing was discarded.
- **No new data defects were found** in the five official sources re-read this session.

## Still blocked / not claimed (unchanged, published on the Flagged page)

These are **not** implemented or claimed complete; they are blocked on sources that do not publish
the needed data, and are listed on the site's Flagged for Review and Suggestions pages:

- **No confirmed single-entry / freezeout event.** No Venetian structure sheet (all 37 read) states
  a one-entry, no-rebuy or no-add-on rule. Silence is not a prohibition. Confirmed-only count = 0.
- **No verified finish times.** Official schedules publish start time and registration close, not end
  time; no field size is published in advance. No all-day sequence is claimed as guaranteed.
- **No itemized checkout totals for an exact stay.** The official booking engine loads a shell without
  a price; no comparable dated quote was captured. Hotel totals remain blank/flagged, not zero.
- **Walking times are route estimates**, not measured door-to-seat durations (OSRM foot routing +
  dated Google Maps checks). No entrance-to-room measurement is claimed.
- **Live hotel quote feed and complete Strip-wide scraping** are not implemented; the monitor
  re-checks the 77 registered official URLs on a schedule and flags changes, which is not the same as
  a live booking-price feed.
