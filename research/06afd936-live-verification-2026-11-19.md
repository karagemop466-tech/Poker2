# Live official-source re-read — arena/06afd936-poker2 (2026-11-19 UTC)

Scope: task V1 on the coordination board. Read-only re-check of decisive official pages with the agent page-fetch tool (the sandbox cannot reach casino hosts with curl). Each comparison below was made by reading the fetched text and checking it against the stored dataset in `data/verified2026/`. Nothing in this file is a booking quote, a checkout total, or a certification that an event is single-entry.

## What was read (all on 2026-11-19)

| Official URL | What was read | Result against stored data |
|---|---|---|
| [Venetian DeepStack Extravaganza IV schedule (HTML)](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) | All four chunks | All 94 rows (83 entry rows and 11 Day 2/3 restarts, including the Dec 11 7:00 PM streamed final table) match on date, start time, event number, title, buy-in, guarantee and structure-sheet link. No row-level value differs. The only discrepancy is in the event-level late-registration text for multi-flight events (flag M-01, below). |
| [Structure sheet 7](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf) — $600 NLH 1-Day | Full text | Events 14, 28 and 63. Guarantee $30,000 (#14, #63) and $40,000 (#28); $90 house fee, $510 to pool; 30-minute levels; 40,000 chips; registration closes about 4:55 PM. **No single-entry, re-entry or add-on clause.** Matches stored data. |
| [Structure sheet 9](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_9.pdf) — $300 NLH, Day B+D @ 5:10 PM | Full text | Event 1, flights B and D. 30-minute levels; late registration about 8:40 PM; $60 house fee, $240 to pool; 30,000 chips; $75,000 guarantee. Clause 8: a player who bags chips for Day 2 may not play a later flight. **No single-entry, re-entry or add-on clause.** |
| [Structure sheet 10](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_10.pdf) — $300 NLH, Day A+C @ 11:10 AM | Full text | Event 1, flights A and C. **40-minute levels; late registration about 3:40 PM.** Same fee, guarantee and chips as sheet 9. **No single-entry, re-entry or add-on clause.** |
| [Structure sheet 14](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_14.pdf) — $800 NLH, Day F (Turbo) @ 5:10 PM | Full text | Event 26, flight F. 20-minute levels; late registration about 7:25 PM; $110 house fee, $690 to pool; $500,000 guarantee; 40,000 chips. Clause 8 is the same flight rule as sheet 9. **No single-entry, re-entry or add-on clause.** |
| [Venetian resort fee](https://www.venetianlasvegas.com/resort/resort-fee.html) | Full text | "$55 plus tax per night, payable upon check-in." Matches. |
| [Venetian 2026 poker suite rates](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html) | Full text | "As low as $119 and $209." Code EPOKR25 by phone. Requires six hours of live cash play or a buy-in to a $300-or-higher tournament for each night stayed, completed before 2 a.m. on the last night; otherwise the night is re-rated. $55 resort fee. Matches the stored conditions. |
| [Venetian hotel terms and conditions](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) | Both chunks | "Daily rates do not include the applicable Clark County Room Tax of 13.38%." $55 resort fee plus tax. Parking: $20/day for registered guests, $20 Mon–Thu or $25 Fri–Sun for others, $40/day valet. Early check-out costs $100 plus tax. Prepaid offers are non-refundable unless the offer says otherwise. Matches. |

## Irregularity found and corrected (flag M-01)

- **Event 1 (and three other multi-flight events) showed one flight's late-registration close for every flight.** The event-level row used a single structure sheet (sheet 9). The official schedule links flights A and C to sheet 10, which closes about 3:40 PM on 40-minute levels. Flights B and D close about 8:40 PM on 30-minute levels. The per-flight entry rows were already correct. The event-level text ("~8:40 PM") was wrong for flights A and C.
- Same pattern on Event 26 (flights A/C/E at 3:40 PM, B/D at 8:40 PM, F at 7:25 PM), Event 47 (A at 4:55 PM, B at 11:10 PM) and Event 56 (A/C/E at 4:55 PM, B/D at 11:10 PM).
- **Fix (generator only, `scripts/build2026.py`):** each flight's late-registration close, level length and close time now comes from the sheet its own official schedule row links. Where flights differ, the event row lists each value with its flights. Single-sheet events are unchanged. The build diff touches only these four events.
- **Checked against the sheets:** sheets 9, 10 and 14 were read in full today and match the corrected values. Sheets 12, 13, 21, 35, 36 and 37 were not re-read today. Their late-registration values come from the earlier 2026-11-17 transcription.

## Last-checked dates

- Day-plan schedule rows are now dated 2026-11-19, the date of the row-level schedule comparison above.
- Sheets 9, 10 and 14 are now dated 2026-11-19 in the shared re-read set, next to sheets 5, 6 and 7.
- Caesars Palace and Bellagio schedule tables show the retrieval date already recorded for their data (2026-11-17). They were not re-read this session.
- Entry-rules "Verified on" column is renamed "Last checked".

## Not re-read in this session (still carry earlier dates)

- Structure sheets other than 7, 9, 10 and 14 (see the sheets page for each sheet's date).
- Wynn daily structures, WPT series page, Caesars and Bellagio documents, Resorts World, Westgate, Golden Nugget, MGM.
- The Venetian booking engine. The Nov 25–28 and Dec 1–4 lookups were not re-run here.
- No single-entry, re-entry or add-on clause was found in the sheets read today, so no event is promoted. The confirmed single-entry count stays **0**.

## Checks run on the corrected tree

`build2026.py` and `--check`, `check2026.py`, `check_labels.py`, `check_sheet_readings.py` (37 sheets, 481 fields), `check_guarantees.py`, `recheck_schedule_live.py` (94/94), `check_semantics.py`, `check_search.mjs`, `check_trip.mjs`, `check_decisions.mjs`, `check_monitor_badge.py`, `check_refresh2026.py`, `test_recheck2026.py`. All exited 0.

## Links for manual review

- Venetian schedule: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
- Sheet 7: https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf
- Sheet 9: https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_9.pdf
- Sheet 10: https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_10.pdf
- Sheet 14: https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_14.pdf
- Resort fee: https://www.venetianlasvegas.com/resort/resort-fee.html
- Suite rates: https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html
- Hotel terms (13.38% room tax): https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html
