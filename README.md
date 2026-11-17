# Las Vegas Poker Trip Planner

A source-audited static research dashboard for planning live poker tournament trips on and near the Las Vegas Strip.

**Published site:** <https://karagemop466-tech.github.io/Poker2/>

The project distinguishes confirmed facts from unknowns. Tournament, hotel, and policy values are linked to the official source used; values that cannot be established from that source are left blank and documented on **Flagged for Review**. Schedules, policies, room rates, fees, and availability can change, so check the linked official source before booking or entering an event.

## Start here

- [Dashboard](index.html) — current overview and trip-planning tools.
- [Executive summary](summary.html) — what is known and the limits of the available evidence.
- [Tournament table](tournaments.html) — search and filter the sourced event rows.
- [Venue pages](venues.html) — venue directory, with individual pages under `venues/`.
- [Hotels](hotels.html) and [rate log](rate-log.html) — published fees, dated rate records, and missing quote details.
- [Trip planner](planner.html) and [schedule](schedule.html) — trip-cost and day-plan views; feasibility flags are not a guarantee that a full event can be completed before another starts.
- [Entry rules](rules.html) and [single-entry evidence](single-entry.html) — per-event rule evidence and separate spend-advantage cases.
- [Walking information](walking.html) — hotel/venue routes and the 30-minute threshold; unverified durations remain blank.
- [Flagged for Review](flagged.html), [open questions](questions.html), and [suggestions](suggestions.html) — unresolved evidence and decision-support improvements.
- [Source monitor](monitor.html) — latest recorded checks and any detected source changes.

## Evidence and ranking policy

- A source's silence is **not** confirmation that re-entry, rebuy, or add-ons are prohibited. An event is not described as confirmed single-entry unless the source establishes that policy.
- Guaranteed-pool ÷ total entry fee is a descriptive ratio, not a forecast or expected return. Events with bounties, flights, satellites, or other different mechanics are labeled separately rather than compared as if identical.
- Hotel quote totals are date-, occupancy-, and room-specific. Starting rates and resort fees are not a checkout total. The nightly-cost calculation only uses values supported by the recorded rate and fee evidence; missing components stay blank rather than being inferred.
- Schedule overlap flags are planning aids based on sourced start/registration information and explicitly identified duration assumptions. A day plan is not proof that an event can be completed before entering another.
- Every event and hotel row should retain its official source and a last-checked date. Review the linked page or PDF again before a non-refundable purchase.

## Repository layout and generated surfaces

This repository currently publishes more than one historical dashboard surface; do not assume that similarly named pages share a generator or dataset.

| Surface / files | Role | Generator / data |
|---|---|---|
| Root pages (`index.html`, `tournaments.html`, `hotels.html`, `venue-*.html`, and other root pages) | Primary dashboard | `scripts/build_master.py` builds `data/master.json`; `scripts/build_site.py` renders the root pages from it. Inputs and provenance are recorded in `data/` and `data/verified/`. |
| `walking.html`, `wpt-terms.html`, `rate-log.html`, `trip.html`, `archive.html` | Additional research pages linked from the root dashboard | `scripts/build_f0816fab.py` and the `data/site/*-f0816fab.json` / related data files. |
| `/plan/` | Separate generated planning surface | `scripts/build-events.py`, `scripts/build-schedule.py`, and `scripts/build-site.py`, using `site-data/*.json`. |
| `docs/`, `verified/`, `pages/`, and `archive/` | Earlier or retained pages/data for history and compatibility | Not the generator for the primary root dashboard. |
| `COORDINATION.md` | Shared task board, ownership notes, verification records, and integration history | Read before editing shared/generated outputs. |

Generated HTML should be changed through its corresponding generator and source data, not by hand. Consult `COORDINATION.md` for current file ownership; the root dashboard and `/plan/` have separate generators and checks.

## Local checks

From the repository root:

```sh
python3 scripts/audit.py
python3 scripts/build_master.py
python3 scripts/build_site.py
python3 scripts/check_links.py

# Separate /plan/ surface
python3 scripts/build-events.py
python3 scripts/build-schedule.py
python3 scripts/build-site.py
node scripts/check_site.mjs
```

The root audit cross-checks transcribed rows against their cited documents; the root link checker checks internal links and approved external hosts. The `/plan/` generators and checker validate that surface separately. Rebuilding one surface can rewrite overlapping root filenames, so follow the ownership notes and CI workflow comments before running generators that touch shared outputs.

## Scheduled monitoring

This checkout contains more than one scheduled source-check workflow. The root dashboard uses `.github/workflows/source-monitor.yml` and `scripts/monitor.py`; the separate `/plan/` surface uses `.github/workflows/plan-refresh.yml` with `scripts/check_sources.mjs` and `scripts/scrape-schedule.mjs`. There is also `.github/workflows/recheck.yml` for the earlier dataset. These workflows have different source registries and outputs; see [COORDINATION.md](COORDINATION.md) and [the source monitor page](monitor.html) before treating a check as comprehensive. A failed fetch is a monitoring error, not proof that the source did not change.

## Current verification caveats

The latest local checks recorded for this README repair were: `scripts/audit.py` passed (83 Venetian rows, 13 other-venue rows, 8 hotels, 60 sources); `scripts/check_links.py` passed (24 pages, 1,749 links). A manual `scripts/monitor.py` invocation reported **22 URLs and 22 fetch errors** in this sandbox. That run does not establish whether the scheduled GitHub Actions monitor can reach those sources; consult its latest report and rerun it in an environment with working outbound access. No rate, schedule, or policy value should be changed based on failed fetches alone.
