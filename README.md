# Las Vegas Poker Trip Planner

<<<<<<< HEAD
A source-audited research site for planning a Las Vegas Strip poker vacation. Every published
value links to the official page or PDF it came from. Anything an organiser does not publish is
left **blank** and listed on the **Flagged for review** page — never estimated, never inferred.

**Live site:** <https://karagemop466-tech.github.io/Poker2/>

## What this build verified (retrieved 2026-11-16)

| Area | Status |
|---|---|
| Venetian DeepStack Extravaganza IV schedule (Nov 16 – Dec 23, 2026) | Read in full from the official schedule **PDF**: date, event number, start, registration close, guarantee, starting chips, level length |
| All 37 official Venetian structure sheets | Read individually: buy-in split, late-registration close, stack, level length, payout share |
| Wynn WPT World Championship schedule + terms | Read: $600/$400K, TORSE, PLO $400, Mixed Triple Draw entry rules |
| Wynn daily tournaments | Read: Mon–Thu, Fri rebuy/add-on, Sat–Sun, plus the poster |
| Bellagio Friday $600, Caesars Palace dailies, MGM Grand $120, Horseshoe | Read to the extent each organiser publishes |
| Hotel fees and taxes | Venetian $55 resort fee + 13.38% room tax; Wynn/Bellagio $55, MGM Grand $50 resort fee (tax % not published) |
| Confirmed single-entry events | **0** — no organiser publishes an explicit one-entry-only rule |
| Dated hotel totals | **0** — needs a live dated quote |
| Walking times | **0** — no official source publishes one |

## Structure

```
index.html            Dashboard: search, filters, trip-cost calculator
tournaments.html      Every verified event, filterable by date / buy-in / entry type
schedule.html         Day plan: one primary event + one conditional fallback per day, plus overlap checks
hotels.html           Resort fees, taxes, parking, dated rate log, true-cost calculator
venues.html           One page per venue (detail pages under venues/)
single-entry.html     The entry-rule evidence, quoted, in three groups
summary.html          Executive summary
questions.html        What must be answered before a decision
suggestions.html      Options with the decision each one needs from you
flagged.html          F-01…F-14: every unverified value and irregularity, with sources
sources.html          Source register + scheduled change monitoring
repo-review.html      Line-by-line review of what the repo contains
data/site/*.json      Generated dataset (do not hand-edit)
scripts/dataset.py    Single source of truth — every verified value
scripts/build.py      Generates all pages from dataset.py
scripts/check_links.py  Fails on broken internal links or non-official external hosts
scripts/recheck_sources.py  Scheduled re-fetch + content hashing of every official URL
```

## Build / check

```bash
python3 scripts/build.py          # regenerate every page + data/site/*.json
python3 scripts/check_links.py    # 18 pages, ~1,100 links, must print OK
python3 -m http.server 8000       # preview at http://localhost:8000
```

The build refuses to publish a row whose source is not an official host.

## Monitoring

`.github/workflows/recheck.yml` runs daily at 06:00 UTC: it re-fetches every official URL, hashes
the normalised text, appends the run to `data/site/checks.json`, rebuilds the site and commits.
A changed hash means a cited value may have moved — the site reports it rather than guessing.

## Legacy pages

Earlier sessions published three overlapping dashboards (`docs/`, `verified/`, `pages/`,
`planning.html`). They are retained so no existing link breaks, but they are superseded by the
pages listed above. Consolidation is offered as suggestion **S-09** for your decision.

## Rules this repo follows

1. Official sources only. No aggregator, no mapping app, no retrieved-by-memory values.
2. Blank beats guessed. A blank cell is listed on the Flagged page with the reason.
3. A guarantee is a floor, not a forecast. GTD ÷ buy-in is labelled descriptive only.
4. Bounty, multi-flight, satellite and team events are shown separately, never mixed into a
   like-for-like comparison.
5. Re-check the official pages before any non-refundable payment.
=======
A verified-source dashboard for planning a live tournament poker trip on and near the Las Vegas Strip.
Live site: **https://karagemop466-tech.github.io/Poker2/**

## What it does

- **Tournaments table** — every row links to an official venue page/PDF, with a `last checked` date,
  a search box, a date filter, and a **“Freezeout confirmed only”** toggle (single-entry / no re-entry / no rebuy / no add-on).
- **Venue pages** — one page each for [The Venetian](venue-venetian.html), [Wynn](venue-wynn.html) and
  [other venues](venue-others.html) (Caesars Palace, Horseshoe, MGM Grand, Golden Nugget), each with its events and hotels.
- **Hotels** — resort fees, tax, parking, cancellation notes from official terms pages; **rates kept as a dated log**;
  a true-cost/night calculator (room rate + resort fee + tax + parking); walking-direction links per hotel–venue pair
  with a ≤30-minute filter (walk minutes stay blank until verified).
- **Trip planner** — estimated trip cost = entries × buy-ins + nights × true hotel cost, plus a day-by-day plan
  (primary event + conditional fallback) with overlap flags based on start times, late-registration cutoffs and
  plausible durations.
- **Ranking** — guaranteed pool ÷ total entry fee shown only where both figures are official. It is a **descriptive
  ratio, not a forecast**. Bounty and multi-flight events are labeled and ranked separately.
- **Entry rules** — single-entry, re-entry, add-on and fee values stored as separate fields per event, each with its
  source excerpt and retrieval date.
- **Source monitor** — a scheduled GitHub Actions job re-checks every official URL daily
  (`.github/workflows/source-monitor.yml` + `scripts/monitor.py`), stores daily snapshots under `data/snapshots/`,
  and marks rows whose source **changed**.
- **Flagged / Questions / Suggestions** — irregularities for review, the questions that must be answered before any
  decision, and suggestion options to choose from before implementing changes.

## Data policy

Every value comes from an official source (venue sites and their PDFs) or is left **blank and flagged**.
Nothing is inferred. “Freezeout confirmed” means the official structure sheet was fully read and contains no
re-entry, rebuy or add-on mechanism — see the caveat on the Flagged page (IR-8234-02).

## Repo layout

| Path | Purpose |
|---|---|
| `data/master.json` | Unified dataset (events, hotels, rate logs, rule fields, flags) |
| `data/session-updates.json` | Session-level official-source excerpts and retrieval dates |
| `data/source_monitor.json` | URL/hash registry for scheduled change monitoring |
| `scripts/build_master.py` | Merge verified inputs into `data/master.json` |
| `scripts/build_site.py` | Generate all pages (fails if a row lacks an official source link) |
| `scripts/monitor.py` | Scheduled URL re-check + snapshots (runs in Actions) |
| `docs/`, `verified/` | Earlier session dashboards, kept as archives |
| `COORDINATION.md` | Shared task board for parallel sessions |

## Rebuilding

```bash
python3 scripts/build_master.py   # regenerate data/master.json
python3 scripts/build_site.py     # regenerate pages (row-source check included)
python3 scripts/monitor.py        # optional locally; runs daily in Actions
```
>>>>>>> e151b14 (Automation + docs: scheduled official-URL re-check with change flagging and daily snapshots)

---

# Parallel session build — arena/7a4b09e2-poker2 (preserved)

The following README is the documentation of the parallel session whose root pages are archived under `archive/arena-7a4b09e2/`. Its non-conflicting outputs (`venues/*.html`, `schedule.html`, `single-entry.html`, `sources.html`, `data/site/*.json`, `scripts/{dataset,build,audit,recheck_sources}.py`) remain in the repo and on the live site.

# Vegas Poker Planner

A source-audited research site for planning a Las Vegas Strip poker vacation. Every published
value links to the official page or PDF it came from. Anything an organiser does not publish is
left **blank** and listed on the **Flagged for review** page — never estimated, never inferred.

**Live site:** <https://karagemop466-tech.github.io/Poker2/>

## What this build verified (retrieved 2026-11-16)

| Area | Status |
|---|---|
| Venetian DeepStack Extravaganza IV schedule (Nov 16 – Dec 23, 2026) | Read in full from the official schedule **PDF**: date, event number, start, registration close, guarantee, starting chips, level length |
| All 37 official Venetian structure sheets | Read individually: buy-in split, late-registration close, stack, level length, payout share |
| Wynn WPT World Championship schedule + terms | Read: $600/$400K, TORSE, PLO $400, Mixed Triple Draw entry rules |
| Wynn daily tournaments | Read: Mon–Thu, Fri rebuy/add-on, Sat–Sun, plus the poster |
| Bellagio Friday $600, Caesars Palace dailies, MGM Grand $120, Horseshoe | Read to the extent each organiser publishes |
| Hotel fees and taxes | Venetian $55 resort fee + 13.38% room tax; Wynn/Bellagio $55, MGM Grand $50 resort fee (tax % not published) |
| Confirmed single-entry events | **0** — no organiser publishes an explicit one-entry-only rule |
| Dated hotel totals | **0** — needs a live dated quote |
| Walking times | **0** — no official source publishes one |

## Structure

```
index.html            Dashboard: search, filters, trip-cost calculator
tournaments.html      Every verified event, filterable by date / buy-in / entry type
schedule.html         Day plan: one primary event + one conditional fallback per day, plus overlap checks
hotels.html           Resort fees, taxes, parking, dated rate log, true-cost calculator
venues.html           One page per venue (detail pages under venues/)
single-entry.html     The entry-rule evidence, quoted, in three groups
summary.html          Executive summary
questions.html        What must be answered before a decision
suggestions.html      Options with the decision each one needs from you
flagged.html          F-01…F-14: every unverified value and irregularity, with sources
sources.html          Source register + scheduled change monitoring
repo-review.html      Line-by-line review of what the repo contains
data/site/*.json      Generated dataset (do not hand-edit)
scripts/dataset.py    Single source of truth — every verified value
scripts/build.py      Generates all pages from dataset.py
scripts/check_links.py  Fails on broken internal links or non-official external hosts
scripts/recheck_sources.py  Scheduled re-fetch + content hashing of every official URL
```

## Build / check

```bash
python3 scripts/build.py          # regenerate every page + data/site/*.json
python3 scripts/check_links.py    # 18 pages, ~1,100 links, must print OK
python3 -m http.server 8000       # preview at http://localhost:8000
```

The build refuses to publish a row whose source is not an official host.

## Monitoring

`.github/workflows/recheck.yml` runs daily at 06:00 UTC: it re-fetches every official URL, hashes
the normalised text, appends the run to `data/site/checks.json`, rebuilds the site and commits.
A changed hash means a cited value may have moved — the site reports it rather than guessing.

## Legacy pages

Earlier sessions published three overlapping dashboards (`docs/`, `verified/`, `pages/`,
`planning.html`). They are retained so no existing link breaks, but they are superseded by the
pages listed above. Consolidation is offered as suggestion **S-09** for your decision.

## Rules this repo follows

1. Official sources only. No aggregator, no mapping app, no retrieved-by-memory values.
2. Blank beats guessed. A blank cell is listed on the Flagged page with the reason.
3. A guarantee is a floor, not a forecast. GTD ÷ buy-in is labelled descriptive only.
4. Bounty, multi-flight, satellite and team events are shown separately, never mixed into a
   like-for-like comparison.
5. Re-check the official pages before any non-refundable payment.
