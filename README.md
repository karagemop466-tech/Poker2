# Las Vegas single-entry poker trip planner

**Current dashboard:** https://karagemop466-tech.github.io/Poker2/2026/
**Latest evidence / decision readiness:** https://karagemop466-tech.github.io/Poker2/2026/latest-review.html

A static, source-linked research dashboard for tournaments and nearby hotels. It is not a booking
service. The root and older `/plan/`, `/verified/`, and `/pages/` surfaces remain available for audit;
`/2026/` is the current consolidated surface. Their generators and monitors are independent.

## Executive conclusion

**No strict single-entry / no-rebuy / no-add-on event is confirmed in the reviewed evidence.**
That is not proof that none exists anywhere on the Strip. A sheet silent on re-entry is not a freezeout
confirmation. The confirmed-only tournament filter returns no rows; rules-silent candidates have a
separate group filter. Bounty, multiple-flight, satellite, team and extra-spend formats remain separate.

There is no defensible hotel winner or bookable all-day itinerary yet. The comparison is Dec 1–4
(three nights, one adult), $200 per night all-in, with a private nonsmoking ensuite room and a refundable
rate with a written deadline. These are research assumptions, not a booked stay. No comparable
checkout was exposed. Seven of eight newly checked Google routes to Venetian Poker Room are estimated
at ≤30 minutes; none measures indoor time. Missing prices remain unavailable, not zero. No 8 a.m. eligible start
or verified tournament finish time has been established.

### Evidence, with honest dates

| Scope | What was checked | Official reference |
|---|---|---|
| Venetian DSE IV | November 16–December 23, 2026 schedule; all four HTML chunks read November 19. Core dataset contains 94 scheduled rows / 64 event numbers. This schedule read does not reverify structure rules. | [Official event page](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) |
| 37 Venetian structure sheets | Original live transcription dated November 17. Nine sheets behind the 15 research candidates (5, 6, 7, 17, 18, 22, 23, 28, 29) were re-read on November 19 and match the stored fees, guarantees, start times and late-registration times (0 of 90 comparisons differ). Those nine print a Venetian Rewards-card condition, now shown on the pages. Offline reconciliation checks 481 stored fields; rerunning it is **not** a fresh source retrieval. No explicit one-entry clause recorded. Details: `research/2c7e846d-official-verification-2026-11-19.md`. | Individual official PDF links in `data/sheets/part1–6.py` and the site's Sources page |
| Wynn daily structures | All three extracted chunks read November 19. Four daily templates: all allow re-entry, rebuys or add-ons. Friday prohibits re-entry but permits unlimited $200 rebuys and a $100 add-on. | [Official structures](https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf) |
| Wynn series | Page read November 19; lists WPT November 27–December 21 and warns daily tournaments can be suspended during series. Recurring templates are not inferred date-specific occurrences. | [Official poker page](https://www.wynnlasvegas.com/casino/poker) |
| Venetian / Palazzo resort fee | Re-read November 19: $55 plus tax per night. Logged as a new dated observation, not a room quote. | [Official resort-fee page](https://www.venetianlasvegas.com/resort/resort-fee.html) |
| Other rooms and hotel terms | Earlier source readings retain their individual retrieval dates. They were not all re-read November 19. | Row-level citations on venue and hotel pages |

The new Wynn Friday flag N-02 records conflicting rebuy accounting inside the official sheet. The
initial $240 split reconciles; the stated $190 rebuy pool contribution conflicts with deductions of
$10 + $5 from a $200 rebuy. The site does not resolve that conflict by guessing.

## Dashboard features

- Tournament table: global/local search, single date and inclusive date range, today/upcoming entry
  dates in **America/Los_Angeles**, fee cap, format groups, strict confirmed-only and separate
  rules-silent group filters. A restart is not a new entry.
- Rule fields and excerpts, official source links, individual retrieval dates and source-change badges.
- Guarantee ÷ total entry fee is a descriptive ratio, **not** expected winnings or a pool forecast.
  It does not establish strict-policy eligibility.
- Day plan: one primary and at most one conditional fallback only when the evidence qualifies; currently none. End times are unverified; no guaranteed
  sequence is claimed. A fallback requires elimination and enough time to arrive before registration closes.
- Venue pages: Venetian, Wynn/Encore, Caesars, Bellagio, Horseshoe, MGM and an other-rooms record.
  Wynn daily formats are explicitly in an excluded extra-spend section.
- Hotel fee/terms table and dated rate log. The optional formula is
  `(room + mandatory resort fee) × (1 + applicable tax rate) + tax-inclusive parking`, under an explicit
  same-tax-rate assumption. 13.38% is not automatically assigned to every hotel.
- Trip calculator: sum of selected total entry fees + known checkout total. Nightly average = checkout
  total / nights. Unknown lodging keeps the combined total unavailable. Selecting events is not proof
  that they meet the policy, do not overlap, or qualify for a promotional rate.
- Walking matrix and ≤30-minute estimate filter with Maps links. Existing OSM routing estimates are
  **not** official venue facts or verified Google/Apple walking durations.
- Executive summary, questions, suggestions awaiting a decision, latest review and **Flagged for Review**.

## Decisions still blocked

1. Obtain written maximum-entry, no-rebuy and no-add-on rules before promoting any event to confirmed.
2. Keep the Nov 25–28 two-adult lookup separate from Dec 1–4; do not use the booking engine’s default dates as quotes.
3. Capture itemized checkout totals for the same dates, occupancy, room type and refund terms. Preserve
   room subtotal, nightly average, mandatory fees/taxes, parking, exact cancellation deadline and timestamp.
4. Verify the actual pedestrian route and poker-room entrance; certify ≤30 minutes only after verification.
5. Reconfirm official schedules, policies and quotes before any nonrefundable payment.

A live hotel quote service, complete Strip-wide event ingestion, indoor walking measurements and verified
finish-time sequencing are **not implemented or claimed as complete**. The evidence page explains
what is missing and how to obtain it. The current monitor fetches official documents and flags changes;
it does not silently replace published event facts with scraped guesses.

## Build and tests

```sh
python3 scripts/build2026.py
python3 scripts/build2026.py --check
python3 scripts/check2026.py
python3 scripts/check_sheet_readings.py  # stored November 17 transcription, not a live fetch
python3 scripts/test_recheck2026.py
python3 scripts/check_monitor_badge.py
python3 scripts/check_semantics.py
python3 scripts/check_guarantees.py
python3 scripts/check_labels.py
node scripts/check_search.mjs
node scripts/check_trip.mjs
npm install --no-save --package-lock=false jsdom@26.1.0
node scripts/check_decisions2026.mjs
python3 -m http.server 8000 --bind 0.0.0.0
```

Generated pages, browser assets and JSON are committed. Edit the generators and evidence inputs,
not generated pages. CI checks the current and legacy surfaces independently. Link validation proves
local targets and permitted citation hosts, **not** that every external page currently returns content.

## Daily source monitoring

`.github/workflows/recheck.yml` runs at **15:00 UTC: 7 a.m. PST / 8 a.m. PDT in Las Vegas**.
The registry currently includes 77 distinct official URLs: all 37 Venetian sheets, official schedules,
Wynn daily rules, field-level hotel sources, booking links and flagged-source references.

- HTML text and PDF bytes are hashed; empty/challenge pages and non-PDF responses at PDF URLs are rejected.
- Baselines are keyed by URL and survive errors and registry-key changes.
- A changed-source warning stays pending across later unchanged/error runs until documented human review.
- `checks.json` retains 90 runs plus durable per-URL state. This is not an unlimited append-only archive;
  older committed snapshots remain in Git history.
- A successful fetch does not update a human retrieval date or certify an individual value.
- All-network-failure runs abort rather than overwriting the last successful evidence. A newly added URL
  is not claimed to have been checked before the next successful run.
- The root `source-monitor.yml` and `/plan/` `plan-refresh.yml` still exist separately. Consolidating them
  is a suggestion, not an action falsely claimed complete.

## Coordination and publication

`COORDINATION.md` is the shared board on main. Session `arena/a29d9f35-poker2` uses its platform-assigned
branch as final integrator. Concurrent trip-calculator PR #80 was incorporated without discarding its
work; the append-only coordination conflict was resolved by retaining both records. Publication uses
GitHub Pages from `main` at `/`; PR and deployment results are recorded on the board.

## Preserved concurrent integration (#81 / #82)

The integration also retains the other session's November 19 re-reads of Venetian sheets 5, 6 and 7,
Wynn WPT/January findings, and an explicitly hypothetical November 25–28 two-adult hotel lookup.
That booking attempt exposed only a loading shell: it is not the user's selected dates and no
checkout quote is recorded. Their dated quote-attempt schema, daily plan safeguards, flight-specific
date filtering, source citations on shortlists, and refresh-artifact preservation remain intact.
Historical Google Maps readings stay distinguished from OSRM estimates; neither is represented
as a fresh entrance-specific walking verification by this session. Current table dates reflect both
sessions' evidence without treating a build as a retrieval.

The consolidated monitor compares Venetian DSE IV event/date/start/sheet keys and tracks other room
documents at source level. Review changes stay pending across failed or unchanged fetches. After a
source re-read, record the verified URL/hash in `data/verified2026/reviewed-hashes.json`. Scheduled
reports remain downloadable even if the guarded push or Pages build request is rejected.
