# Las Vegas Single-Entry Poker Trip Planner

A source-audited research site for planning a live tournament poker trip on and near the Las Vegas
Strip. The brief was specific: **single-entry tournaments only**, ranked by cost to enter and prize
pool, with anything that lets money buy an advantage kept in a separate section — plus hotels within
a reasonable walk, priced at their **true** nightly cost.

**Live surface: <https://karagemop466-tech.github.io/Poker2/2026/>**

The repository root serves an older multi-venue dashboard built by earlier parallel sessions from a
different generator. This site is deliberately published **under `/2026/`** so the two surfaces do
not overwrite each other; every page links back to the root dashboard.

## The headline finding

> No event in the reviewed dataset is confirmed to meet the strict single-entry policy.

All **37** official Venetian DeepStack Extravaganza IV structure sheets were read individually. Not
one contains a one-entry-only, freezeout or no-re-entry clause. That is not a gap in the reading —
it is what the organiser publishes. So the site does the next best thing and says so plainly: it
separates the events whose sheet is **silent** on re-entry, rebuy and add-on from the ones that
expressly price a second buy-in, run multiple flights, pay bounties, or award seats.

**Confirmed single-entry events: 0.** That number is a finding, not a failure.

## What is verified (retrieved 2026-11-17)

| Area | Status |
|---|---|
| Venetian DeepStack Extravaganza IV, Nov 16 – Dec 23 2026 | Read in full, from **both** the HTML event page and the official schedule PDF: 94 rows, 64 event numbers |
| All 37 official structure sheets | Read one by one. Buy-in split, late-registration close, stack, level length, payout share, bounty mechanic, and the re-entry / rebuy / add-on finding for each |
| Entry-rule classification | 15 best candidates (13 open to any player, 2 restricted to 50+) · 30 bounty/PKO · 9 multi-day/multi-flight · 7 satellites · 1 team · 2 that price a second buy-in |
| Resort fees | Venetian/Palazzo $55, Wynn/Encore $55, Bellagio $55, MGM Grand $50 — each with its official page |
| Poker suite rate | Shared offer lists starting prices of $119 and $209 without assigning them to towers; phone code `EPOKR25`, subject to availability and qualifying play |
| Room tax | 13.38%, from Clark County's own transient lodging guide |
| Seven other poker rooms | Checked. **Two do publish official schedules** — Caesars Palace (four daily NLH events) and Bellagio (three weekly events), both read live on 2026-11-17 and published on their venue pages. Every one of those events prints re-entry or a paid add-on, so none is single-entry |

## What is not verified, and is left blank

| Gap | Why |
|---|---|
| Any single-entry confirmation | No official document states one. Flag **F-01** |
| Any finish time | No event publishes an end time, so no two events can be promised as a sequence. **F-04** |
| Any dated hotel quote | Official booking engines render rates with JavaScript. **F-05** |
| Any cancellation deadline | Not published on the pages read. **F-06** |
| Any official quality rating | No hotel publishes a star or diamond rating for standard rooms |
| Any measured walk time | The walking page differentiates dated Google Maps route readings from OSRM estimates. Neither verifies the indoor portion. **F-08** |
| Ten monitored URLs | The 2026-11-17 scheduled run read 51 of 61. The other ten returned 403/404/302/422 or timed out, so they are reported as *not read*, never as unchanged. **F-14** |

Every one of these is on the **Flagged for review** page with the source to check. Scenario inputs and routing estimates are labelled separately from official evidence.

## Irregularities found in the official documents

- **X-01** — The official schedule PDF prints a sponsor banner (`@PokerAtlas PRO`) or a series logo
  where the date should be on **12 rows**. Every affected date was recovered from the official HTML
  schedule page and is marked `date_from_html` in the data.
- **X-02** — The official series overview still labels the **WPT Fall Festival** (Oct 28 – Nov 15
  2026) as its "Current Series", even though that series has ended.
- **F-02** — Events **18 and 58** price a *subsequent* buy-in at $200 on the official sheet, so more
  than one buy-in per player is contemplated. They are moved out of the candidate group.
- **F-03** — Bounty guarantees include bounty money, so they are not like-for-like with cash
  guarantees. Bounty events are ranked in their own group.

## Site structure

| Page | What it does |
|---|---|
| `2026/index.html` | Dashboard: headline counts, best-value and cheapest leaderboards |
| `2026/tournaments.html` | All 64 events. Search box, date selector, entry-fee cap, single-entry toggle, sortable columns, group pills |
| `2026/entry-rules.html` | Single-entry, re-entry, add-on and fee fields, one row per event, each with its source excerpt and retrieval date |
| `2026/schedule.html` | One primary event per day plus a conditional fallback, with overlap flags built from official start times and registration closes |
| `2026/hotels.html` | Resort fees, tax, parking, a **dated rate log**, and a true-cost-per-night calculator |
| `2026/walking.html` | 21 hotels × 6 poker rooms, routed minutes, 30-minute filter, Google Maps link per row |
| `2026/trip.html` | Estimated trip cost = entries × buy-ins + nights × true hotel cost |
| `2026/venues.html` | One page per room |
| `2026/summary.html` | Executive summary |
| `2026/questions.html` | What must be answered before any decision |
| `2026/suggestions.html` | Options to choose between before anything changes |
| `2026/flagged.html` | Every unverified value and irregularity |
| `2026/sources.html` | The source register and the scheduled re-check |
| `2026/repo-review.html` | What the repository contains |

## How the ranking works

Guarantee ÷ total entry fee is shown **only** where both figures are printed on the official
documents, and it is labelled a **descriptive ratio, not a forecast** — a guarantee is a floor the
room commits to, not a predicted pool. Bounty and PKO events are ranked separately because their
published guarantee includes bounty money. Multi-flight events are separate because a second flight
is a second buy-in. Satellites pay in seats, not cash.

## November 19 decision update

The November 25–28 stay is a comparison scenario only. The [official booking engine](https://www.venetianlasvegas.com/book?adults%5B%5D=2&arrival_date=2026-11-25&children%5B%5D=0&departure_date=2026-11-28&view=calendar) exposed no checkout quote. The three Venetian research leads (#10, #12, #14) still do not state a maximum-entry rule. The [Wynn venue page](2026/venues/wynn.html) separates the WPT opener (explicit re-entry) from the January Signature Series (schedule published, structures pending). Neither is ranked as a freezeout.

## Build and check

```bash
python3 scripts/build2026.py          # regenerate 2026/*.html + data/verified2026/dataset.json
python3 scripts/check2026.py          # no broken links, no non-official external hosts
python3 scripts/build2026.py --check  # CI: fail if committed pages differ from the data
python3 scripts/recheck2026.py        # re-fetch every official URL, hash it, log changes
python3 scripts/check_sheet_readings.py  # diff the sheets against a live transcription
python3 -m http.server 8000           # then open /2026/index.html
```

### Independent re-read of all 37 sheets (2026-11-17)

Every structure sheet was read again from `venetianlasvegas.com` and transcribed to
`research/sheet-readings-7cc9ee65.csv`, field by field. `check_sheet_readings.py` diffs that
transcription against what the site ships: **37 sheets, 481 field comparisons, 0 mismatches,
0 sheets containing a single-entry clause.** The check exits 1 on any difference, so the claim
is re-runnable rather than asserted.

`build2026.py` **aborts** rather than publishing a row whose structure sheet was not read, or whose
citation points at a non-official host.

## Data layout

| Path | Purpose |
|---|---|
| `data/sheets/part1–6.py` | Verified readings of all 37 official structure sheets, clause by clause |
| `data/verified2026/schedule.py` | All 94 official schedule rows, with the X-01 date fix noted per row |
| `data/verified2026/hotels.py` | Hotel fields plus the dated rate log |
| `data/verified2026/content.py` | Other venues, flags, questions, suggestions |
| `data/verified2026/dataset.json` | Generated. Do not hand-edit |

## Monitoring

`.github/workflows/recheck.yml` runs daily at 14:15 UTC (06:15–07:15 Las Vegas): it re-fetches the registered official URLs the
site cites, hashes the normalised text (or the raw PDF bytes), appends the run to
`data/verified2026/checks.json`, rebuilds the site and commits. A `CHANGED` row means the official
document moved, so every value transcribed from it must be re-read. The job reports; it never
rewrites a value.

## Rules this repository follows

1. **Official sources only.** No aggregator, no forum, no mapping service as a citation.
2. **Blank beats guessed.** A blank cell is listed on the Flagged page with the reason.
3. **Silence is not a prohibition.** "No re-entry clause printed" is never written as "single entry".
4. **A guarantee is a floor, not a forecast.** GTD ÷ entry is descriptive only.
5. **Bounty, multi-flight, satellite and team events are shown separately**, never mixed into a
   like-for-like comparison.
6. **Re-check the official pages before any non-refundable payment.**

## Legacy surfaces

Several earlier sessions published overlapping dashboards (`docs/`, `verified/`, `pages/`,
`plan/`) plus their own generators. They are still served so no existing link breaks, but they are superseded
and frozen. Their scheduled workflows were retired in favour of the single `recheck.yml`. Deleting
the trees is offered as suggestion **S-09** rather than done unilaterally.

## Coordination

`COORDINATION.md` is the shared task board for parallel sessions. This site was built by session
`arena/839a07d9-poker2` as the integration session; its claim, sources and completion record are
logged there.
