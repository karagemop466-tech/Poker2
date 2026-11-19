# Official verification — 2026-11-19 (arena/027412f0-poker2)

All pages below were fetched live on 2026-11-19 via the page-fetch tool. No value was
inferred; where an official page does not state a value, the dataset keeps it blank and
the row stays on Flagged for Review.

## Venetian
- Structure Sheet 30 / Event 8 — https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_30.pdf
  `$200 NLH (1Day) PKO`, 5:10 PM, 25,000 chips, 30-min levels, late reg 8 levels + break
  (9:40 PM), $8,000 GTD (prize pool + total bounties), $40 house fee + $160 pool, pays
  12.5%. Silent on re-entry/freezeout/add-on. Matches `data/master.json` / sheet register.
  The 2026-11-18 monitor `changed` flag for this PDF was a slug-collision artifact
  (all 37 sheets shared one 80-char snapshot name), not a content change.
- DSE IV schedule — https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
  Nov 16–Dec 23, 2026, >$3.6M GTD; Events 1–17 unchanged. The page header embeds a
  rolling booking widget (`Select Dates Thu, Nov 19 Sun, Nov 22`,
  `arrival_date=2026-11-20&departure_date=2026-11-22`) — this caused daily raw-hash churn.
- Series overview — https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html
  **Genuine upstream update:** stale `WPT Fall Festival (Oct 28–Nov 15, 2026)` banner is
  gone; page now lists `Current Series: DeepStack Extravaganza IV (Nov 16–Dec 23, 2026)`,
  `DeepStack Extravaganza NYE (Dec 24, 2026–Jan 10, 2027, >$1.1M GTD)` and
  `DeepStack Showdown (Jan 11–Feb 14, 2027, >$2.2M GTD)`. Resolves flag X-02's stale label.
- Resort fee / terms / poker rates / poker room —
  https://www.venetianlasvegas.com/resort/resort-fee.html ,
  https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html ,
  https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html ,
  https://www.venetianlasvegas.com/resort/casino/poker.html
  $55 + 13.38% Clark County Room Tax resort fee; check-in 3:00 p.m.–11:59 p.m.,
  check-out 11:00 a.m.; registered-guest self-parking $20/day (non-guest $20 Mon–Thu /
  $25 Fri–Sun, valet $40/day; 3+ hr poker play = complimentary self-parking for
  non-registered guests); poker suite rates starting $119 / $209 (`EPOKR25`,
  866.255.8936, 6 hrs cash or $300+ tournament/night before 2 a.m., $2/hr comps);
  50 tables, Palazzo Level 2, Grand Canal Shoppes, 24/7.

## Wynn
- https://www.wynnlasvegas.com/casino/poker and https://www.wynnlasvegas.com/about-us/resort-information
  WPT World Championship Nov 27–Dec 21 (new $400 Super Gold Million, $3,000,000 GTD);
  Wynn Signature Series Jan 11–24, 2027; daily tournaments suspended during series;
  check-in 3 p.m. / check-out 12 p.m.; $55 + tax daily resort fee incl. self-parking (2 vehicles).

## Caesars
- Daily flyer PDF (live and intact) — https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf
  10 AM $100, 2 PM $160, 6 PM $100, 9 PM $160; $30/$45 maintenance fees; optional $50
  add-on ($45+$5, 15,000 chips at 1st break); 20,000 chips, 20-min levels, $1,000 GTD,
  re-entry through 1st break / start of L7, min 6 players. Therefore Caesars Palace
  dailies are spend-more, not single-entry.
- https://www.caesars.com/corporate/disclaimer — daily resort fee $45–$60 plus tax
  (range only; property fee still blank). Note the Strip guide chunk contradicts the
  flyer ($100 at all four times); the flyer prevails as the tournament document and
  the discrepancy stays flagged.
- https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip —
  16-table 24/7 Caesars Palace room; Horseshoe Hall of Fame Poker Room 24/7.

## Other official pages
- Bellagio https://bellagio.mgmresorts.com/en/casino/poker.html — links Fri $600 NLH,
  Sat $1,000 NLH, Sun $400 H.O.R.S.E. PDFs; $300 PLO Double Board Bomb Pot Sat 2 PM.
- Resorts World https://www.rwlasvegas.com/gaming/poker-room/ redirected to
  `/gaming/poker-room/poker-room-dining/` on 2026-11-19 — no tournament schedule there.
- Westgate https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/faq/resort-fee/
  ($49.99 + tax/night) and .../casino/poker/ (7 tables, Mon–Fri 12:00pm–Last Game,
  Sat–Sun 10:00am–Last Game, (702) 732-5223, daily tournaments with no online structure
  sheet); .../faq/parking/ redirected to the Westgate homepage.
- Clark County https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf
  13.38% Combined Transient Lodging Tax in the Primary Gaming Corridor (e.g. Wynn/Encore,
  3131 Las Vegas Blvd S, RES, District 1).

## Monitor forensics (2026-11-18 run)
1. Caesars served HTTP-200 Imperva `<title>Pardon Our Interruption</title>` HTML for the
   flyer PDF and 3 HTML pages, overwriting good baselines. The real PDF is live/unchanged.
2. `slug(url)[:80]` collided all 37 Venetian structure PDFs onto one snapshot file.
3. Every Venetian HTML page carries the rolling booking-widget dates above, so raw-text
   hashing flagged them daily. Only the series-overview change was genuine.
Repairs are in `scripts/monitor.py` (unique hashed slugs, PDF/bot-challenge/soft-404
validation, raw-byte PDF hashing, visible-text + widget normalization, `review_pending`
preservation), `scripts/test_monitor.py`, and the repaired `data/source_monitor.json`.
