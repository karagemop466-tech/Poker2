# Official-source re-check, 2026-11-17 — session `arena/7be88b38-poker2`

Every document below was opened and read in full or in the cited part by this session on
2026-11-17 (UTC) through the browser-side page fetcher. The sandbox has no outbound access to
venue hosts (`curl` to `venetianlasvegas.com` returns nothing), so nothing here was read from a
terminal, and no value was carried over from memory: each line records what the fetched page
actually printed. Where the site's stored value matched, it is confirmed; where it did not, the
site was corrected in the same commit; where the page does not answer the question, the cell stays
blank and the gap is on the Flagged page.

## 1. Venetian DeepStack Extravaganza IV — official schedule page

<https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html>

* Series header on the page: **November 16 – December 23, 2026**, "More than $3.6 Million in
  guaranteed tournament prize pools".
* Rows read on this pass cover Nov 16 → Nov 28, with date, weekday, time, event number, event name,
  structure-sheet link and results column. Examples as printed:
  * Wed Nov 18, 11:10 AM, **Event 2** — `$300 No LImit Hold'em $10K GTD (1Day)` →
    `dse_nov_2026-structure_5.pdf`
  * Wed Nov 18, 12:00 PM, **Event 1** — `$300 No Limit Hold'em Day 2 Restart` → `structure_10.pdf`
  * Thu Nov 19 / Fri Nov 20 / Sat Nov 21, 10:10 AM, **Events 3/4/5** —
    `$200 NLH RaceDay Stack (1Day) - Race to finish before the Race` → `structure_18.pdf`
  * Mon Nov 23 11:10 AM **7A** / Tue Nov 24 11:10 AM **7B** / Wed Nov 25 11:00 AM **Day 2 Restart** —
    all three link `structure_2.pdf` (one sheet, three schedule rows)
  * Fri Nov 27, 11:10 AM, **Event 14** — `$600 No Limit Hold'em $30K GTD (1Day)` → `structure_7.pdf`
  * Sat Nov 28, 11:10 AM, **Event 16** — `$600 No Limit Hold'em Bounty $30K GTD (1Day) - $200 bounties
    to start & $500 bounties in the money` → `structure_11.pdf`
  * Sat Nov 28, 12:10 PM, **Event 17** — `$400 Pot Limit Omaha Bounty $15K GTD (1Day)` → `structure_26.pdf`
* The page prints `No LImit` (capital I) in several event names. Preserved as printed, as elsewhere
  on this site.
* **Result:** every date, time, event number, buy-in and sheet link read on this pass matches
  `data/verified2026/schedule.py` and the published rows. Nothing changed, so no row value moved.
  The full 94-row reconciliation was recorded by `arena/1655b450-poker2` on the same day in
  [`venetian-dse4-live-2026-11-17.csv`](venetian-dse4-live-2026-11-17.csv)
  (`python3 scripts/recheck_schedule_live.py`).

## 2. Venetian structure sheet 5 (events 02 and 12)

<https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf>

Read in full, one page. As printed: title `$300 No Limit Hold'em (1Day)`; `Event Numbers: 02 and 12`;
`Start Time: 11:10 AM`; `Starting Chips: 40,000`; `Level Duration: 30 minutes`;
`Late Registration: 10 levels + Break (~ 4:55 PM)`; `Guarantee: $10,000`;
clause 6 `$58 of the $300 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of
$242 of every $300 Buy In.`; clause 7 `This event pays 12.5% of the field`; clause 2 `Must be 21+ years
of age and have a Venetian Rewards card to participate`; levels 1–28 with 15-minute breaks, the
registration-closing break after level 10.

* **Confirmed against the site:** buy-in, house fee, per-entry prize pool, guarantee, stack, level
  length, late-registration close, payout share and the 21+ / rewards-card gate all agree with the
  published row for events 2 and 12.
* **The finding stands:** the sheet contains no `single entry`, `one entry`, `freezeout`, `no re-entry`,
  `rebuy` or `add-on` clause anywhere. Silence is not a freezeout rule, so **no "unverified" label can
  be removed on the strength of this document** — this is the answer to the brief's request to "read
  every structure sheet and remove the unverified label from each event that is confirmed": all 37 are
  read, and none confirms single-entry. The structural fields the sheet *does* print are labelled
  read; the entry rule is labelled silent.

## 3. Wynn Las Vegas poker room — the live page

<https://www.wynnlasvegas.com/casino/poker>

Read in full. As printed:

* **WPT World Championship — November 27–December 21**; "New for 2026, the Super Gold Million brings a
  $400 buy-in featuring a $3,000,000 guarantee!" with `View Schedule`, `Structures`, `CHIP
  COUNTS/REDRAWS` and `Results` documents on `cdn.wynnresorts.com`.
* **Wynn Signature Series — January 11–24. 2027** (period after "24" as printed), schedule and
  structures PDFs linked.
* **Daily tournaments:** "runs twice a day during non-event timeframes, offering a total of $200,000 in
  guaranteed prize pools weekly. Tournaments include the **$40,000 guaranteed NLH Rebuy** on Friday and
  a **$10,000 guaranteed event every evening at 6 p.m.**"
* "*Please note that the Daily Tournament schedule will be suspended during each Wynn Signature, Wynn
  Millions, and Classic tournament series." — the WPT window is **not** in that suspension list, so the
  page neither confirms nor denies daily dailies during the WPT; the existing flag stays as "not
  confirmed either way" rather than being resolved in either direction.
* No buy-in, no structure sheet and **no entry limit** is printed for any daily event.

* **Result — a defect fixed:** the site's Wynn/Encore venue row cited
  `https://www.wynnlasvegas.com/casino/poker-room`, which serves Wynn's "IT SEEMS THIS PAGE HAS CHECKED
  OUT" not-found page; that is exactly why the scheduled re-check logged **HTTP 404** for the Wynn row.
  Every Wynn citation now points at the live page, the venue row records today's read, and flag `F-09`
  states both the fix and what the page still does not publish.
* **Result — an exclusion strengthened with a first-hand source:** the room's own page advertises the
  Friday daily as a **Rebuy**. A rebuy is a second buy-in, so that event cannot sit in a single-entry
  table on the operator's own description, independently of the WPT structures PDF line cited from
  2026-11-16.

## 4. Caesars — "Poker Tournaments in Las Vegas" page

<https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip>

Read in full (3 parts). As printed:

* **Caesars Palace daily slate:** "four No-Limit Hold'em tournaments each day at **10 a.m., 2 p.m.,
  6 p.m. and 9 p.m.** Every event carries a **$100 buy-in**, starts you with **20,000 chips**, and
  features a **$1,000 guaranteed prize pool**. Blinds increase every 20 minutes ... and a **$50 add-on**
  at the first break gives you an extra 15,000 chips."
* **Horseshoe Las Vegas:** "six daily No-Limit Hold'em games. The times at **9 a.m., 11 a.m., 2 p.m.,
  5 p.m., 8 p.m. and 11 p.m.** ... A mixture of buy-ins, levels and guarantees" — no buy-in, guarantee
  or structure is printed for any of the six.
* **Caesars Palace poker room:** "recently refreshed and relocated, this 16-table sanctuary ... open
  24/7, with cash games running alongside the daily tournament slate." **Horseshoe:** "Hall of Fame
  Poker Room".
* Also printed: "Most sessions finish in four to six hours" — an operator's estimate, not a published
  finish time, so it is *not* used to promise a same-day sequence anywhere on the site.

* **Result:** the six Horseshoe start times previously carried as "cited from an earlier session" are
  now confirmed first-hand (that venue's row is dated 2026-11-17).
* **Result — a claim corrected:** the Caesars Palace row said "no tournament schedule or structure sheet
  published on the official page". The page does publish a dated daily slate with buy-in, stack,
  guarantee and blind length. It is now recorded, together with the **$50 add-on**, which is the reason
  the events stay out of the single-entry table under the brief's own rule (anything where money can buy
  an extra advantage is separated, not ranked).
* **Irregularity kept, not resolved:** the $100 on this page disagrees with the $160 at 2 p.m./9 p.m. on
  the property's own daily flyer (read 2026-11-16). Two official documents, one room. Recorded as flag
  **F-14**; no figure is chosen for the tables.

## 5. Venetian resort fee

<https://www.venetianlasvegas.com/resort/resort-fee.html>

Read in full: "Rates include a daily Resort Fee of **$55 plus tax per night, payable upon check-in**",
with the inclusions (fitness at Canyon Ranch for two, in-suite internet, boarding-pass printing,
unlimited local/toll-free calls, PressReader while on guest WiFi) and "questions ... inquire with the
Front Desk Agent upon check-in".

* **Confirmed.** Added as a dated line in the rate log, which is what the log is for: the fee is a
  value with an evidence date, not a constant.

## 6. Clark County transient-lodging tax

<https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf>

Read: table of contents, the transient-lodging definition and licence sections, and the licence
register containing the rate per property. The register prints, among others:
`1000389.RES-001 | Venetian Resort Hotel Casino / Palazzo Resort Hotel Casino | 3325 Las Vegas Blvd S |
Las Vegas | NV | Licensed | 13.38% | RES | 1 | Transient Lodging Tax - Resort Hotel (PGC)`, and the same
13.38% for Cosmopolitan, The LINQ, Treasure Island, Vdara, Virgin Hotels, Westgate Las Vegas and
Waldorf Astoria, with 13.00% inside the unincorporated strip district and 12.50% outside the service
district.

* **Confirmed:** 13.38% for a Paradise Commercial Zone resort hotel, i.e. the Venetian/Palazzo rate the
  calculators use. The room-tax record's date advanced to 2026-11-17.
* **Irregularity found:** the document the county serves at a `...july-2021.pdf` slug carries the
  internal title `Microsoft Word - Genl Info Guide for TLEs Sept 2018`. The rate is corroborated by the
  property's own hotel terms, but the county copy is not fresh-dated → flag **F-15**.

## What this pass could NOT verify, and did not invent

| Question | State after this pass |
|---|---|
| A dated checkout total for the trip nights (room + fee + tax + parking) | Not obtainable from the property pages. The Venetian booking widget returns only its default calendar window (`Thu, Nov 19 – Sun, Nov 22`, "Check Rates"), no price, and `.../book` is a JS engine that answers with no rate at all. No quote is published anywhere on this site, so the calculator keeps an empty rate field rather than a made-up one. **F-05 open.** |
| Cancellation deadline per rate plan | Not printed on any page read. **F-06 open.** |
| Any hotel quality tier from an official source | No property publishes a star or diamond rating for standard rooms; the field stays blank. **F-12 open.** |
| An official walking time from any hotel to the Venetian poker room | None published. The matrix stays a labelled OpenStreetMap/OSRM routing estimate with a Google and an Apple link per pair so a person can confirm each one. **F-08 open.** |
| A confirmed single-entry event anywhere on the Strip | Still **0**. One sheet read in full today repeats the pattern: the fields a freezeout needs are printed, the entry rule is not. |
| An 8:00 AM start | Nothing printed. The earliest start this site has from an official document is 9:00 AM (Horseshoe, no buy-in published); the Venetian's earliest is 10:10 AM. |
| Whether MGM Grand / Bellagio / Aria terms changed | Their pages time out for the monitor and could not be read on this pass either; the values carry their previous dates and are listed under "What the scheduled monitor could not read". **F-16.** |

## Effect on the site

* No event value, hotel fee value or tax value moved, so no row was rewritten.
* One dead citation was fixed (Wynn), two venue rows gained first-hand evidence dates, one venue
  verdict gained an official reason for its exclusion, three flags were added (F-14 buy-in conflict,
  F-15 county document date, F-16 monitor coverage), and two dated lines were appended to the rate log.
* Generator-level honesty changes are described in the commit that carries this file.
