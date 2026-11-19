# Official-source verification — arena/a9f5847f-poker2 (2026-11-19)

Live re-reads via page-fetch tool on 2026-11-19. No values inferred; every
field below was read first-hand today. Retrieval date for all rows: **2026-11-19**.

## 1. Venetian DSE IV schedule page (all 94 printed rows, 4 chunks)

Source: https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html

- Series header unchanged: "DeepStack Extravaganza IV, November 16 – December 23, 2026, More than $3.6 Million in guaranteed tournament prize pools."
- All 94 printed rows read end to end (Nov 16 – Dec 23). No event added,
  removed, retimed, or renamed vs the stored dataset: every date, start time,
  event number, event name, guarantee and structure-sheet URL matches the
  stored rows (83 published non-restart rows + 11 Day 2 restarts).
- Spot checks against stored rows: Event 1 flights (Nov 16–17, structure_9/10),
  Event 47 $2,200 1A Dec 12 10:10 AM / 1B 6:10 PM $1M GTD (structure_21/37),
  Event 56 $1,100 1A–1E with $40 rake discount (structure_35/36),
  Event 63 Dec 23 11:10 AM $600 $30K GTD (structure_7). All match.
- Result: `schedule_checked` and `last_checked` for all Venetian rows → 2026-11-19.

## 2. Venetian structure sheet 7 (Events 14, 28, 63) — full read

Source: https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf

- $600 No Limit Hold'em (1Day), Events 14/28/63, start 11:10 AM, 40,000 starting
  chips, 30-minute levels, late registration 10 levels + break (~4:55 PM).
- Guarantee: $30,000 for Events 14 and 63; $40,000 for Event 28.
- $90 of the $600 buy-in withheld (rake + staff); $510 to the prize pool.
  Event pays 12.5% of the field. TDA rules; 21+; Venetian Rewards card required.
- **No re-entry, rebuy, or add-on clause anywhere on the sheet** — the sheet
  states a late-registration window only. These rows remain rules-silent
  ("not stated"), NOT confirmed single-entry. Silence is not a prohibition.
- All stored fields for V-14, V-28, V-63 match exactly.
- Result: `struct_checked` → 2026-11-19 for V-14, V-28, V-63.

## 3. Venetian structure sheet 30 (Event 8) — full read (confirm prior re-read)

Source: https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_30.pdf

- $200 NLH (1Day) Progressive Knock-Out Bounty, Event 8, start 5:10 PM,
  25,000 chips, 30-minute levels, late registration 8 levels + break (9:40 PM).
- Guarantee $8,000 (prize pool + total bounties). $40 withheld, $160 to pool.
  Players start with a $50 bounty; pays 12.5% of the field.
- No re-entry/rebuy/add-on clause — rules-silent, unchanged.
- Matches stored V-08 exactly. (Already dated 2026-11-19 by the prior session's
  re-read; this read confirms no change since.)

## 4. Wynn poker page — full read

Source: https://www.wynnlasvegas.com/casino/poker

- WPT World Championship November 27 – December 21 (fifth year at Wynn).
  "New for 2026, the Super Gold Million brings a $400 buy-in featuring a
  $3,000,000 guarantee!" — already stored as X-WPT06 ($400, $3M GTD, multi-flight
  Day 1A–1D, mystery bounty). No change.
- Wynn Signature Series January 11–24, 2027 (schedule + structures PDFs linked).
- Daily tournaments run twice a day outside series; daily schedule suspended
  during Wynn Signature / Wynn Millions / Classic series. $40,000 guaranteed
  NLH Rebuy Friday; $10,000 guaranteed every evening at 6 PM.
- The WPT schedule PDF itself was NOT re-read today, so Wynn rows keep their
  2026-11-17 `last_checked`. No value changed.

## 5. Venetian resort fee page — full read

Source: https://www.venetianlasvegas.com/resort/resort-fee.html

- "Rates include a daily Resort Fee of $55 plus tax per night, payable upon
  check-in." Unchanged vs stored H-VEN. No new dated rate observation.

## 6. Bellagio poker page — full read

Source: https://bellagio.mgmresorts.com/en/casino/poker.html

- Weekly tournament PDFs linked with the same URLs as stored:
  Fridays $600 NLH, Saturdays $1,000 NLH, Sundays $400 H.O.R.S.E.
- Page note: "Tournament play will resume on Saturday, July 26, beginning with
  the $300 PLO Double Board Bomb Pot Tournament at 2 PM PT." (stale July note;
  the three weekly PDFs remain the current linked terms.)
- The three weekly PDFs were not re-read today; no Bellagio row dates changed.

## 7. MGM Grand poker page — full read

Source: https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html

- "Daily Texas Hold'em Tournaments: 11:00am, 7:00pm and 11:00pm" — matches
  stored MGM-1100AM / MGM-700PM / MGM-1100PM.
- Weekly Schedule and Full Structure List PDFs linked with the same URLs as stored.
- Result: `last_checked` → 2026-11-19 for the three MGM daily rows.
  MGM-SAT-150 NOT bumped (its buy-in/guarantee come from the weekly PDF,
  not re-read today).

## 8. Caesars Palace poker room + Caesars/Horseshoe guide — read

Sources:
- https://www.caesars.com/caesars-palace/casino/poker (redirects to the casino
  page; poker room section: "open 24/7 with both live-action cash games and
  daily tournaments", schedule flyer PDF link unchanged)
- https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip
  (marketing guide; Caesars Palace and Horseshoe rooms described; no schedule
  table on the page)

- The daily schedule data comes from the flyer PDF
  (clv-poker-daily-nlh-tournament-flyer-2026.pdf), which was NOT re-read today.
  Caesars/Horseshoe rows keep their 2026-11-17 `last_checked`.
- Note: https://www.caesars.com/casino/poker redirects to the Caesars homepage
  (no poker content); the stored source URLs were already the correct ones.

## 9. Golden Nugget daily tournaments page — full read

Source: https://www.goldennugget.com/las-vegas/casino/poker-room/daily-tournaments/

- Daily at 10AM, 5PM, 2AM; 15,000 starting chips; 15-minute levels.
- "unlimited Re-Entries are available until the start of Level 5"; two $20
  add-ons (first to dealer appreciation, second to prize pool).
- Matches stored GN rows exactly; extra-spend classification confirmed.
- Result: `last_checked` → 2026-11-19 for GN-1000AM, GN-500PM, GN-200AM.

## 10. Monitor state (read-only)

`data/verified2026/checks.json`: last run 2026-11-18T15:29:01Z, 4 changed
sources, 5 fetch errors. A changed source means the document moved and its
transcribed values must be re-read before reliance; a fetch error is a
monitoring failure, not a verdict. The two Venetian sheets re-read today
(7 and 30) match the stored transcriptions, so no value changes result.
The remaining changed/errored URLs were not re-read in this session and keep
their existing dates and flags.

## Conclusion

- Zero values changed. Zero events added/removed. Zero rows promoted to
  confirmed single-entry: every Venetian 1-day sheet remains silent on
  re-entry, and silence is not a freezeout confirmation.
- Confirmed single-entry/freezeout count remains **0** (unchanged).
- Dates advanced only where the row's own official document was actually
  re-read today: Venetian schedule rows, V-14/V-28/V-63 (sheet 7),
  MGM daily rows, Golden Nugget rows.
- Irregularities: none new. The stale Bellagio "July 26" note and the
  Caesars /casino/poker redirect are recorded above; neither affects data.
