# Live official-source verification — 2026-11-19

Session: arena/9e862af8-poker2 (branch `arena/9e862af8-poker2`, from `main` `7ab07592`).
Method: every document below was re-read live via the agent page-fetch tool today (bash egress to
casino/county hosts is TLS-blocked in this sandbox; `gh workflow run` returns HTTP 403, so no CI was
dispatched). Values already in the dataset were confirmed or contradicted against the live text;
nothing was inferred. Where two official documents disagree, both are cited and the conflict is
flagged — no value was silently rewritten.

## 1. Venetian DeepStack Extravaganza IV schedule

Official page (read live, all 4 chunks):
https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html

- Series window: November 16 – December 23, 2026 ("More than $3.6 Million in guaranteed tournament prize pools").
- Transcribed all 94 printed rows (date, time, event #, name, structure-sheet URL) to
  `research/live-schedule-venetian-2026-11-19.tsv`.
- Comparison against `data/master.json` (83 published Venetian rows; 11 Day-2 Restart / Final Table
  rows are deliberately excluded from the published set, per prior session decision):
  - master-only pairs: 0
  - live-only pairs: 11 — all are Day-2 Restart / Final Table rows (Nov 18 Event 1 restart; Nov 25
    Event 7 restart; Dec 2 Event 19 restart; Dec 6 Event 26 restart; Dec 11 Event 39 restart +
    final table; Dec 13 Event 47 Day 2; Dec 14 Event 47 Day 3; Dec 15 Event 49 Day 2 restart;
    Dec 20 Event 56 Day 2 restart; Dec 23 Event 59 Day 2 restart). Excluded by design, not missing.
  - URL mismatches on shared (date, start) keys: 0. Every published row's structure-sheet URL matches
    the live page.
- All 83 Venetian rows carry `struct_checked` in {2026-11-17, 2026-11-19}; refreshed to 2026-11-19
  where this pass re-read them.

Transcript saved: `research/live-schedule-venetian-2026-11-19.tsv`.

## 2. Venetian hotel / poker official pages

Resort fee — https://www.venetianlasvegas.com/resort/resort-fee.html (read live 2026-11-19)
- "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in." — matches stored
  value ($55 + tax/night, Venetian & Palazzo). Unchanged.

Poker suite rates — https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html (read live 2026-11-19)
- "start as low as $119 and $209 ... for either The Venetian or The Palazzo" (no per-property mapping);
  code EPOKR25; phone 866.255.8936; qualify with six hours live cash or a $300+ tournament buy-in per
  night, met before 2 a.m. the last night; $55 resort fee; not combinable with promotional rates;
  quotes only 150 days ahead. — matches stored conditional starting rates; no dated quote exists and
  none was invented (F-05 stays open).

## 3. Caesars Palace daily NLH — official sources disagree; rows reconciled to the flyer

Official daily flyer (read live 2026-11-19):
https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf

| Time | Buy-in | Add-on | Chips | Levels | Guarantee |
|------|--------|--------|-------|--------|-----------|
| 10 AM | $100 | $50 (15,000 chips, first break only) | 20,000 | 20 min | $1,000 |
| 2 PM | $160 | same | 20,000 | 20 min | $1,000 |
| 6 PM | $100 | same | 20,000 | 20 min | $1,000 |
| 9 PM | $160 | same | 20,000 | 20 min | $1,000 |

Flyer terms: re-entry by paying the entry fee upon elimination within the first break; registration
closes at the start of level seven; $100 = $70 prize pool / $30 fee; $160 = $115 pool / $45 fee;
$50 add-on = $45 pool / $5 fee; minimum 6 players; 21+.

Official poker guide page (re-confirmed live 2026-11-19):
https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip
- "four No-Limit Hold'em tournaments each day at 10 a.m., 2 p.m., 6 p.m. and 9 p.m. Every event
  carries a $100 buy-in ... $1,000 guaranteed ... $50 add-on at the first break ... 15,000 chips."
- Horseshoe: six daily NLH at 9, 11, 2, 5, 8, 11 PM; no buy-ins/guarantees published on the page.

Change made to `data/master.json` (rows CZP-1000AM/200PM/600PM/900PM, `last_checked` 2026-11-19):
- buy-in now per flyer per time slot: 100 / 160 / 100 / 160; `fee` 30 / 45 / 30 / 45;
  `pool_per_entry` 70 / 115 / 70 / 115; `gtd_ratio` 10.00 / 6.25 / 10.00 / 6.25 (guarantee ÷ total
  entry fee — descriptive ratio only, not a forecast).
- `rules` re-written from the flyer: re-entry confirmed within first break; paid add-on confirmed;
  registration closes at start of level seven; both official excerpts quoted with retrieval date;
  secondary_source records the guide's conflicting "$100 for all four" claim.
- `event name` for the 2 PM and 9 PM rows now reads "$160 buy-in" (was "$100 buy-in").
- Flag VR-028 ("Caesars Palace daily buy-ins — official sources disagree") updated with the 2026-11-19
  flyer reading; conflict remains flagged, not resolved by guesswork. Not single-entry: the flyer
  confirms paid re-entry and a paid add-on.

Site regenerated with `scripts/build_site.py` (20 pages, 166 events, 10 hotels, all rows cited).

## 4. Wynn poker room — https://www.wynnlasvegas.com/casino/poker (read live 2026-11-19)

- WPT World Championship: November 27 – December 21, 2026; Super Gold Million $400 buy-in / $3,000,000
  guarantee. Matches stored data.
- Daily tournaments: $200,000 weekly GTD; Friday $40,000 rebuy; $10,000 guaranteed every evening at 6 PM.
- Suspension clause: "the Daily Tournament schedule will be suspended during each Wynn Signature, Wynn
  Millions, and Classic tournament series." Note: the live page does NOT name the WPT series, so a
  WPT-window suspension is NOT supported by this page; Wynn daily rows during Nov 27–Dec 21 stay
  "unavailable, not confirmed either way" (pre-existing flagged position, unchanged).
- Wynn resort information page ($55 + tax, self-parking for two, one night at booking) previously
  confirmed; unchanged.

## 5. Clark County transient lodging tax

https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf (read live 2026-11-19)
- Appendix III carries the combined transient lodging tax rates and components; the 13.38% Primary
  Gaming Corridor rate attribution for Strip properties rests on this county document plus the
  Venetian/Cosmopolitan terms pages stating 13.38% verbatim. South Point sits outside the PGC at 13.00%
  (prior county-schedule reading). Stored values unchanged; no re-attribution.

## 6. Spot checks consistent with prior live reads

- Venetian structure sheets 5/02/12 were re-read 2026-11-19 by the preceding integration session with
  exact match; this pass re-confirmed the stored Event 2 structure sheet URL and fee split
  ($58 withheld / $242 pool / $10,000 GTD) against the live schedule page's sheet links.
- check_sheet_readings.py: 37 sheets, 481 comparisons, 0 mismatches; 0 sheets print a single-entry /
  freezeout / no-re-entry clause → confirmed single-entry events remain 0 (FG-02 open).
- Wynn WPT structures PDF (general terms, Nov 27 – Dec 21, 2026) matches the stored transcript
  (all 8 chunks read 2026-11-16 by arena/e3cb221d-poker2).

## Result

No published value contradicted by today's reads except the Caesars 2 PM/9 PM buy-in, which was
reconciled to the official flyer with the flyer–guide conflict flagged (VR-028). Everything else read
today matches the dataset. `last_checked` on the four Caesars rows and the Venetian series card is now
2026-11-19.

Open and unchanged (flagged, not guessed): no dated room quote (F-05), no finish times (F-04), no
official walking time (F-08/F-13), zero confirmed single-entry events (F-01/FG-02), Caesars/Horseshoe
resort fee (VR-32a4-02), Wynn WPT re-entry details for individual events (VR-009).
