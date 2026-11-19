# Official re-checks and `/2026/` corrections — 2026-11-19 (UTC)

Session `arena/c2a75934-poker2`. Branch `arena/c2a75934-poker2`. Sandbox bash has no route to the
casino/county hosts (TLS reset on `www.venetianlasvegas.com:443`), so every official read below was
made with the agent page-fetch tool. Retrieval date for every item on this page: **2026-11-19**.

No value is written to any dataset or page unless the cited official page states it. Where a page
does not state a value, the cell stays blank and the gap is recorded.

## 1. Venetian DeepStack Extravaganza IV schedule page — confirmed unchanged

Fetched <https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html>
(chunk 1 of 4). Title reads **November 16 – December 23, 2026**, "More than $3.6 Million in
guaranteed tournament prize pools". The printed rows continue to match the shipped schedule file
row for row on the rows inspected (Nov 16 – Nov 28 window): dates, start times, event numbers,
event names and the per-row structure-sheet PDF links.

Spot-checked against `data/verified2026/schedule.py`:

| Printed row | Dataset | Match |
|---|---|---|
| Mon Nov 16 · 11:10 AM · #1 · `$300 No Limit Hold'em 1A $75K GTD` · structure_10 | same | yes |
| Mon Nov 16 · 5:10 PM · #1 · `1B $75K GTD` · structure_9 | same | yes |
| Wed Nov 18 · 12:00 PM · #1 · Day 2 Restart · structure_10 | same (restart row) | yes |
| Thu Nov 19 · 10:10 AM · #3 · `$200 NLH RaceDay Stack (1Day)` · structure_18 | same | yes |
| Sat Nov 28 · 12:10 PM · #17 · `$400 Pot Limit Omaha Bounty $15K GTD` · structure_26 | same | yes |

This read does **not** re-verify the structure sheets behind those rows; their transcription dates
are unchanged.

## 2. Structure sheets — not re-read by this session

37 sheets keep their existing transcription date (2026-11-17) and the twelve re-read dates already
recorded by earlier sessions (`2026-11-19`, sheets 5/6/7/9/10/14/17/18/22/23/28/29). This session
added no new sheet reading and promoted nothing to "confirmed single-entry". The printed
whole-event cap field remains unset on every sheet: **the confirmed count stays 0**.

## 3. Hotel terms — live re-read, fees confirmed

| Property | Page read | What the page prints | Effect on the site |
|---|---|---|---|
| Bellagio | <https://bellagio.mgmresorts.com/en/terms-and-conditions.html> | "A daily resort fee of $55.00 plus applicable tax will be applied to all reservations." Also: additional occupant **$50 plus tax** per occupant per night above 2; first night refundable if cancellation is received "at least 72 hours prior to the arrival date". | `$55` confirmed; new dated rate-log observation added. |
| MGM Grand | <https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html> | "A daily resort fee of $50.00 plus applicable tax" · additional occupant **$40 plus tax** above 2 · 72-hour deposit refund. | `$50` confirmed; new dated rate-log observation added. |
| Wynn / Encore | <https://www.wynnlasvegas.com/about-us/resort-information> | "a daily resort fee of $55 plus tax … entitles you to … Complimentary self-parking for up to two vehicles". Tower Suites carry the same `$55` daily fee. | `$55` and the in-fee parking statement confirmed; new dated rate-log observation added. |
| Caesars Palace | <https://www.caesars.com/caesars-palace/hotel> | No resort-fee amount printed (landing page prints "FREE 48-Hour Cancellation*" without the condition, and describes THE VILLAS' AAA Five Diamond award only). | Fee **stays blank**; recorded as still unprinted. |
| Horseshoe Las Vegas | <https://www.caesars.com/horseshoe-las-vegas/hotel> | No resort-fee amount printed. | Fee **stays blank**; recorded as still unprinted. |

`https://www.caesars.com/faq/resort-fees` was also requested; it redirects to the Caesars corporate
home page (`?originalrequest=%2Ffaq%2Fresort-fees`) and prints no fee table. Recorded as a
dead-end, not as a source.

## 4. Other Strip poker rooms — live re-check

| Room | Page read | What it publishes | Consequence |
|---|---|---|---|
| Westgate Las Vegas | <https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/casino/poker/> | Seven tables, cash-game limits, room hours; "Tournaments are available every day (private tournament available upon request)". **No** start time, buy-in, guarantee, entry rule or structure sheet. | No event row can be written. Venue page copy updated with this exact finding. |
| Westgate Las Vegas | <.../casino/poker/events/> | Poker *promotions* only (Game Starter Special, Instant High Hand, Weekly Loyalty). No dated tournament. | Same. |
| Resorts World Las Vegas | <https://www.rwlasvegas.com/gaming/poker-room/> | Redirects to a **"Poker Room Dining"** page listing restaurants and delivery-to-table service. No tournament document. | No event row can be written. Venue page copy updated. |

## 5. Live checkout quote — attempted, not obtained

Both of these were fetched and both returned the same loading shell ("Your Venice meets Vegas
getaway is loading") with a rewards-tier panel and **no rate block, no resort-fee line, no tax line
and no total**:

- `https://www.venetianlasvegas.com/booking?adults[]=1&arrival_date=2026-12-01&children[]=0&departure_date=2026-12-04&view=calendar` (the Dec 1–4 research window)
- `https://www.venetianlasvegas.com/booking?adults[]=2&arrival_date=2026-11-18&children[]=0&departure_date=2026-11-22&view=calendar` (the stay already quoted on 2026-11-17)

**Flag F-05 stays open.** The two itemized quotes already in `site-data/rates.json` keep their own
2026-11-17 capture dates and are not refreshed, restated or extrapolated.

## 6. Corrections made to the site this session

1. **`2026/venues/venetian.html`** now renders the 21-row hotel-to-poker-room walking table with the
   30-minute filter, matching every other venue page. Previously it showed only a text pointer even
   though the routing data existed.
2. **`2026/tournaments.html`** gained per-row **Single entry / Re-entry / Rebuy / Add-on** cells from
   the structured `rule_evidence` already stored per event. Silence renders as *silent*, never as
   "no". Events 18 and 58 — whose sheet (8) prices "subsequent buy in's" at $200 — now show that
   written re-entry evidence instead of a blank cell.
3. **`2026/schedule.html`** gained a **Maximum entries per day** table and a per-day line. It uses
   only published start times and late-registration closes. Identical starts, a later registration
   closing before the earlier event begins, and a repeat entry in the same event (a later flight) are
   never chained. No finish time is computed, because no sheet prints how many levels an event runs.
4. **`2026/venues/resorts-world.html`** and **`2026/venues/westgate.html`** carry the 2026-11-19
   findings above.
5. **`2026/summary.html`**, **`questions.html`** (new Q-00) and **`suggestions.html`** (new S-00,
   asking each room for the number of levels per event) reflect the new evidence state.
6. **`scripts/check_maxentries.py`** gates the maximum-entries rule in `verify.yml`.

## 7. Irregularities found, none blocking

- Caesars' own FAQ path for resort fees redirects to the corporate home page instead of a fee table.
- Resorts World's poker-room URL serves a dining page under `/gaming/poker-room/`, so the poker-room
  content is not reachable at the URL the site had been citing; the page now says so.
- Westgate advertises daily tournaments without a single published structure, so its events cannot
  be compared, ranked or scheduled on this site.
- The Venetian booking engine would not render a price for either date pair today, which is exactly
  the failure the site already flags rather than guesses around.
