# Verification sweep — session arena/594db405-poker2 (2026-11-17)

Independent line-by-line re-read of the official pages behind the published hotel and event rows.
Every page below was opened **live on 2026-11-17 (UTC)** through the page-fetch tool (sandbox `curl`
cannot reach casino hosts — TLS egress is blocked to everything except github.com / npm / pypi, so
`fetch_page` is the only first-hand channel). Quotes are copied from the fetched page text.
Nothing here is inferred or carried over from an aggregator.

Scope note: the Venetian DSE IV schedule rows were re-verified the same day by session
`arena/1655b450-poker2` (94/94 rows match, PR #70) and the lodging-tax rate + Wynn WPT schedule by
`arena/00421070-poker2` (PR #71). This sweep deliberately covers the pages those passes did not:
hotel fee/terms pages, the poker suite-rate page, the Caesars corporate disclaimer, the Westgate
FAQ, South Point, and two structure sheets.

## Result summary

| # | Official page (read 2026-11-17) | Rows affected | Result |
|---|---|---|---|
| 1 | Venetian [resort-fee](https://www.venetianlasvegas.com/resort/resort-fee.html) | H-VEN, H-PAL | **match** — "Rates include a daily Resort Fee of $55 plus tax per night, payable upon check-in." |
| 2 | Venetian [hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) (both chunks, read end to end) | H-VEN, H-PAL | **match, all fields** — see field list below |
| 3 | Venetian [poker suite rates](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html) | poker-rate page | **match** — $119/$209, code EPOKR25, "$55 resort fee per night stayed", "six hours of active live cash gameplay or buy in to a $300 or higher tournament for each night stayed" |
| 4 | Wynn [resort information](https://www.wynnlasvegas.com/about-us/resort-information) | H-WYN | **match** on fee/parking; **new nuance** on deposit policy (below) |
| 5 | ARIA [terms and conditions](https://aria.mgmresorts.com/en/terms-and-conditions.html) | H-ARIA | **match, word for word** — $55.00 fee, $150/day incidentals, $50 additional occupant, 72-hour refundable first-night deposit |
| 6 | MGM Grand [terms and conditions](https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html) | H-MGM | **match** — $50.00 fee, $100/day incidentals, $40 additional occupant, 72-hour cancellation (877.880.0880) |
| 7 | Westgate [resort-fee FAQ](https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/faq/resort-fee/) | H-WG | **match** — page body: "the resort fee is $49.99 plus tax per night". The $36.99 figure attributed to this page by an earlier note does **not** appear in the page body read today |
| 8 | Caesars [corporate disclaimer](https://www.caesars.com/corporate/disclaimer) (Hotel Disclaimer section) | H-HS, H-CZP, `caesars_resort_fee_range` | **CHANGED** — see change record below |
| 9 | Horseshoe [hotel page](https://www.caesars.com/horseshoe-las-vegas/hotel) | H-HS | **match** — "FREE 48-Hour Cancellation*", "Reserve now. Pay at hotel."; still **no resort-fee amount** published on the property page, so the row stays blank |
| 10 | South Point [poker room](https://southpointcasino.com/casino/poker-room) | H-SP, `south_point` slate | **match** — "parking is always free!"; "tournaments daily … at 10:10 am, 2:10 pm, 6:10 pm and 10:10 pm with buy-ins of $120 and $300" |
| 11 | Structure sheet 5 ([PDF](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf)) | V-02 (and event 12) | **match, word for word** — $300 buy-in, $58 withheld / $242 to pool, $10,000 guarantee, 40,000 chips, 30-min levels, 11:10 AM, "Late Registration: 10 levels + Break (~ 4:55 PM)", "pays 12.5% of the field", no re-entry/rebuy/add-on clause |
| 12 | Structure sheet 6 ([PDF](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_6.pdf)) | V-10 | **match, word for word** — $400 buy-in, $65 withheld / $335 to pool, $15,000 guarantee, same structure values, no entry-mechanism clause |

## Field-by-field confirmation — Venetian hotel terms (page 2 of 2 above)

| Field | Live text (2026-11-17) | Row value | Status |
|---|---|---|---|
| Room tax | "Daily rates do not include the applicable Clark County Room Tax of 13.38%." | 13.38% | match |
| Resort fee | "a standard Las Vegas Resort Fee of $55 plus applicable tax per night, payable upon check-in" | $55 + tax | match |
| Incidentals | "A credit card incidental deposit of $150 per night is required upon check-in … for non-Signature Suites." | $150/night | match |
| Self-parking (guest) | "The daily fee for registered hotel guests is $20/day, seven days a week." | $20/day | match |
| Self-parking (non-guest) | "$20, Monday – Thursday, and $25/day Friday – Sunday" | $20/$25 | match |
| Valet | "Valet parking is $40/day." | $40/day | match |
| Extra guest | "a charge of $50 is added to the daily rate for each additional guest 13 years of age or older" | $50 | match |
| Early departure | "Check-out prior to your scheduled departure date will result in an additional charge of $100 plus tax." | $100 | match |
| Prepaid offers | "bookings made using a prepaid offer are non-cancellable and non-refundable, and cancellation will result in a forfeiture of the deposit" | matches `cancellation_evidence` | match |

## Change record — Caesars corporate disclaimer (the one value that moved)

* **URL:** https://www.caesars.com/corporate/disclaimer → "Hotel Disclaimer" section
* **Read 2026-11-16 (session e1c079dc):** "Room reservations are subject to a daily resort fee between
  **$45-$50** plus applicable tax."
* **Read 2026-11-17 (this session):** "Room reservations are subject to a daily resort fee between
  **$45-$60** plus applicable tax. Resort fees are waived for Diamond and Seven Stars."
* The dataset value is updated to **$45-$60** with the new excerpt and retrieval date, and the change
  is published as a flag. The stale "$45-$50" also still appears in the search engine's cached
  snippet; the live page fetch is treated as authoritative over any cache.
* This is a range only — it still does **not** support a single Caesars Palace or Horseshoe fee
  figure, so both property rows keep their blank fee cells.

## New nuance — Wynn deposit policy (no row value contradicted)

The H-WYN `cancellation_evidence` rule ("A full deposit of all room nights and tax will be charged at
the time of booking") is quoted from three official **offer-terms** pages
([850257](https://www.wynnlasvegas.com/terms-and-conditions/850257),
[848703](https://www.wynnlasvegas.com/terms-and-conditions/848703),
[849723](https://www.wynnlasvegas.com/terms-and-conditions/849723)). The property's general
[resort-information](https://www.wynnlasvegas.com/about-us/resort-information) page states the
standard guarantee policy as "One night's room rate and tax will be charged at time of booking."
Both can hold — standard policy vs. specific offers — but a traveler's deposit exposure depends on
which rate they book, so both readings are now recorded on the row.

## Irregularities found in this pass (all published on the Flagged page)

1. **Caesars disclaimer range moved $45-$50 → $45-$60 in one day** (record above). Any true-cost
   estimate that used the old upper bound understates the worst case by $10/night before tax.
2. **Horseshoe Las Vegas publishes no resort-fee amount** on its hotel page even though its
   [fitness page](https://www.caesars.com/horseshoe-las-vegas/things-to-do/fitness-center) says
   access is "included in the daily resort fee" — a fee exists but its amount is not published on
   the pages reachable without the booking engine. Row stays blank; aggregator figures
   (e.g. $56.63) were **not** used.
3. **South Point's [daily tournament schedule](https://southpointcasino.com/casino/poker-room/daily-tournament-schedule)
   is image-only** (a JPG poster plus JPG rules sheets, "Oct2026" in the file names). Text cannot be
   extracted, so which time carries which buy-in stays unpublished in the dataset. A human with the
   image open can read it in seconds — link kept on the row for manual review.
4. **Westgate's $36.99 figure** appears in third-party notes and search snippets but **not** in the
   page body read 2026-11-17 (which prints $49.99). The row keeps $49.99 and the conflict note.
5. The Venetian resort-fee page and the hotel-terms page word the same $55 fee differently
   ("Rates include a daily Resort Fee…" vs "a standard Las Vegas Resort Fee…"); no numeric conflict.

## Verification performed for this sweep

* Each URL above was fetched live and the quoted sentences were read in the returned text.
* Structure sheets 5 and 6 were compared field-by-field with the transcribed rows in
  `data/master.json` (names, buy-in split, guarantee, chips, level length, start, late-reg wording,
  payout share). Zero mismatches.
* Sandbox `curl` connectivity was tested (`curl -sI https://www.venetianlasvegas.com` → TLS blocked,
  `github.com` → 200), which is why the fetch tool is named as the reading channel in every record.
* Values not read in this pass (Bellagio terms, MGM parking table, Wynn offer-terms pages, the
  county tax PDF) keep their previous retrieval dates and owners: `arena/32a40b2f-poker2` (Bellagio/
  MGM Grand terms re-read 2026-11-17), `arena/00421070-poker2` (tax guide re-read 2026-11-17),
  `arena/e1c079dc-poker2` (Wynn offer terms, 2026-11-16).
