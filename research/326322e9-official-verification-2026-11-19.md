# Official-source verification — 2026-11-19 (session arena/326322e9-poker2)

Every line below is a page that was **opened on 2026-11-19 in this session** and read. Nothing here is
carried over from an earlier session's reading, and nothing is inferred. Where a value could not be
read, the row says so instead of guessing. Each URL is given so a person can re-open it.

Method: the pages were fetched in full (Venetian DSE IV is a four-chunk page; all four chunks were
read), and every stored value in `data/verified2026/` was compared against what the page printed.
A fetch is not a transcription: a successful fetch proves the page answered, not that a stored value
is right. The comparison against the stored value is recorded in the right-hand column.

## 1. Venetian DeepStack Extravaganza IV — schedule page

**URL:** https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html
**Result:** HTTP 200, all four chunks read. Title: *DeepStack Extravaganza IV*, **November 16 – December 23, 2026**,
"More than $3.6 Million in guaranteed tournament prize pools".

| Check | Result |
|---|---|
| Row count | 94 scheduled rows, matching `data/verified2026/schedule.py` line for line |
| Event numbers | 1–64 present; restart rows carry the parent event number |
| Dates | every stored date matches the printed weekday + date |
| Start times | every stored start matches |
| Structure-sheet link | every stored `sheet_no` matches the `structure_NN.pdf` in the row's own link cell |
| Guarantees printed in the table | match where the page prints one; the page leaves some cells empty, and so does the dataset |

Spot rows quoted verbatim from the page, for manual review:

- `Thursday, November 19, 2026 | 10:10 AM | 3 | $200 NLH RaceDay Stack (1Day) - Race to finish before the Race` → structure_18.pdf
- `Wednesday, December 2, 2026 | 10:10 AM | 24 | $600 No Limit Hold'em Seniors $40K GTD (1Day) - Must be 50+ years of age to participate` → structure_17.pdf
- `Saturday, December 12, 2026 | 9:10 AM | 46 | $260 NLH Turbo Milestone Satellite (1Day) - Awards Direct Entry to Event # 47` → structure_25.pdf
- `Saturday, December 12, 2026 | 10:10 AM | 47 | $2,200 No Limit Hold'em 1A $1 Mill GTD - PokerAtlas Championship Title Event` → structure_21.pdf
- `Wednesday, December 23, 2026 | 11:10 AM | 63 | $600 No Limit Hold'em $30K GTD (1Day)` → structure_7.pdf
- `Wednesday, December 23, 2026 | 5:10 PM | 64 | $200 No Limit Hold'em Bounty $8K GTD (1Day)` → structure_1.pdf

The 09:10 start on 2026-12-12 is the earliest start anywhere in the series. Every main-schedule event
starts at 10:10 AM or later. **This is why an 8 a.m. all-day plan is recorded as blocked (R-10, N-06).**

## 2. Venetian structure sheet 5 — used as the fee/rule verification sample

**URL:** https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf
**Result:** read in full. Headline `$300 No Limit Hold'em (1Day)`, **Event Numbers: 02 and 12**,
Start 11:10 AM, Starting Chips 40,000, Level Duration 30 minutes, Late Registration "10 levels + Break
(~ 4:55 PM)", Guarantee $10,000.

Stored values that match: buy-in $300; house fee $58; prize-pool contribution $242; 40,000 chips;
30-minute levels; late registration to 4:55 PM; guarantee $10,000.

The sheet prints, verbatim:

- "6. $58 of the $300 Buy-In is withheld for house fees (Rake - Staff). The prize pool consists of $242 of every $300 Buy In."
- "2. Must be 21+ years of age and have a Venetian Rewards card to participate."
- "7. This event pays 12.5% of the field"

**The sheet does not state a one-entry limit, and does not mention re-entry, rebuys or add-ons.** It is
silent, which is not the same as prohibiting them, so event 2/12 stays a research candidate and is not
marked single-entry confirmed (flag F-01 stands).

## 3. Venetian resort fee

**URL:** https://www.venetianlasvegas.com/resort/resort-fee.html
**Result:** "Rates include a daily Resort Fee of **$55 plus tax per night**, payable upon check-in."
Matches the stored $55. Inclusions printed: Canyon Ranch fitness for two, in-suite internet, boarding-pass
printing, unlimited local/toll-free calls, PressReader.

This is a fee, not a room rate. It is not a checkout total and is not used as one.

## 4. Venetian hotel terms and conditions — tax, parking, cancellation

**URL:** https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html (two chunks, both read)
**Result:** prints, verbatim:

- "Daily rates do not include the applicable Clark County Room Tax of **13.38%**." → matches the stored tax.
- "For reservations with more than 2 guests per suite, a charge of **$50** is added to the daily rate for each additional guest 13 years of age or older." → matches.
- "The Venetian Resort has a standard Las Vegas Resort Fee of **$55 plus applicable tax per night**, payable upon check-in." → matches.
- "Check-out prior to your scheduled departure date will result in an additional charge of **$100 plus tax**." → matches.
- **Parking Fees section:** "The daily fee for registered hotel guests is **$20/day**, seven days a week. For non-hotel guests, the fee is **$20**, Monday – Thursday, and **$25/day** Friday – Sunday. Valet parking is **$40/day**." → matches the stored parking values.
- Deposit: "A deposit for your stay, including suite, fee, and tax, will be billed upon reservation confirmation… the deposit may be either payment of your first night's stay or prepayment of your entire stay." → matches.

**No cancellation window is printed here.** The page describes deposit mechanics and the early-checkout
charge, not a "cancel by date" rule. The site therefore leaves the poker-rate cancellation deadline blank.

## 5. Venetian poker suite rates

**URL:** https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html
**Result:** "These rates will start as low as **$119 and $209** and can be higher. Future rates are only
provided out to a maximum of **150 days** from the current date. Rates are subject to qualifying poker
play and availability… Rates are based on single/double occupancy in a Luxury King Suite… There is a
**$55 resort fee per night** stayed."

Qualifying condition, verbatim: "During your stay, you will be required to play **six hours of active
live cash gameplay or buy in to a $300 or higher tournament for each night stayed**… These requirements
must be met prior to **2 a.m. the last night stayed**. For any nights you fail to complete these
requirements, your nightly suite rate will be adjusted to the prevailing rate."

Booked only by phone: "calling **866.255.8936** and mentioning code **EPOKR25**".

The page **does not assign $119 to the Venetian and $209 to the Palazzo**; it lists both "as low as" and
says they "can be higher". That is why the site publishes them as an unassigned conditional starting
price and not as either property's rate.

## 6. Venetian poker room page — the page that does NOT print the parking fee

**URL:** https://www.venetianlasvegas.com/resort/casino/poker.html
**Result:** read in full. Prints location ("The Palazzo, level 2, Grand Canal Shoppes"), open 24 hours,
50 tables / 14,000 sq ft, the indoor directions from both lobbies, the poker-suite-rate promotion, and
"Non-registered hotel guests who play for three hours or more in our tournaments or cash games receive
complimentary self-parking."

**It prints no parking price anywhere.** The site's Venetian and Palazzo parking rows were nonetheless
cited to this URL. That is irregularity **P-01**, now fixed: the rows cite the hotel terms (which print
the fees) and the parking page below (which confirms them), and `scripts/check_semantics.py` fails if
this URL is used as a parking source again.

## 7. Venetian poker-room self-parking page

**URL:** https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html
**Result:** prints "The daily fee for registered hotel guests is **$20/day**, seven days a week. For
non-hotel guests, the fee is **$20/day** Monday – Thursday, and **$25/day** Friday – Sunday. Valet
parking is **$40/day**." plus "Players in the poker room who play three hours or more in tournament or
cash games will receive complimentary self-parking for the day. Players must visit a supervisor at the
end of their session to confirm qualifications."

This is the second, independent confirmation of the parking values, and it is now watched by the
scheduled re-check.

## 8. Wynn poker room page

**URL:** https://www.wynnlasvegas.com/casino/poker
**Result:** lists **WPT World Championship, November 27 – December 21** (Wynn's fifth year; "the Super
Gold Million brings a $400 buy-in featuring a $3,000,000 guarantee") and **Wynn Signature Series,
January 11–24, 2027**. Daily tournaments: "twice a day during non-event timeframes… $200,000 in
guaranteed prize pools weekly… include the $40,000 guaranteed NLH Rebuy on Friday and a $10,000
guaranteed event every evening at 6 p.m."

Verbatim caveat: "Please note that the Daily Tournament schedule will be suspended during each Wynn
Signature, Wynn Millions, and Classic tournament series."

The page also names the Friday event a **Rebuy**, which matches the stored finding that all four Wynn
daily formats allow extra spend (flag N-01).

## 9. Bellagio poker page — stale notice found

**URL:** https://bellagio.mgmresorts.com/en/casino/poker.html
**Result:** HTTP 200 and readable **this session** — note that the site's monitor recorded a timeout on
this host. Content: room location ("Northside of Casino, next to Sportsbook"), host phone
702.693.7291, and the three weekly tournament PDFs (Fridays $600 NLH, Saturdays $1,000 NLH, Sundays
$400 H.O.R.S.E.).

**It also still prints:** "Please Note: Tournament play will resume on **Saturday, July 26**, beginning
with the $300 PLO Double Board Bomb Pot Tournament at 2 PM PT." That date has passed, so the notice is
stale. Published as **N-05**. The rows stay because their own PDFs were re-read (below), but the room
page cannot be used to prove the events currently run, and the rows remain outside the single-entry
ranking.

## 10. Bellagio Friday structure PDF

**URL:** https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf
**Result:** read in full, unchanged from the stored transcription. Headline "NLH $600 BUY-IN,
Fridays | 11:00 a.m."

- "01. Players will start with 30,000 tournament chips, including the optional Staff Gratuity. (15,000 + 15,000)"
- "02. Levels will be 30 Minutes in Length with a 12 minute break every 4 levels."
- "03. Players may buy-in and re-enter through the end of level 8 (Including Break)."
- "05. The $600 Buy-In is allocated as follows: $510 to Prize Pool; $50 House Fee; $40 Voluntary Staff Gratuity."
- "07. The voluntary staff gratuity will grant players an extra 15,000 chips."

Re-entry and a gratuity that buys chips are both printed, so this event is excluded from the
single-entry group. No guarantee and no end time are printed.

## 11. Bellagio Saturday structure PDF — the existing X-04 conflict, confirmed

**URL:** https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf
**Result:** the headline reads "**NLH $1100 BUY-IN**, Saturdays | 11:00 a.m.", but rule 07 still reads
"Of the **$600** Buy-in, $510 goes to the Prize Pool, $50 is Admin Fees and $40 is optional staff
gratuity." The sheet contradicts itself on the buy-in, and it also prints "04. Combined Final Day 2
(**9/13/26**)", a date already past when read. Stored as buy-in blank + conflict flag X-04/X-05.

## 12. MGM Grand poker page — dead, as already recorded

**URL:** https://mgmgrand.mgmresorts.com/en/casino/poker.html
**Result:** HTTP 200 with the body "**Oops! We can't find that page**". Confirms flag X-06. The MGM Grand
hotel resort fee and terms are sourced from the property's terms page, not from this poker page.

## 13. Caesars Palace casino page — the poker-room claim

**URL:** https://www.caesars.com/caesars-palace/casino
**Result:** prints "The Poker Room at Caesars Palace is open 24/7 with both live-action cash games and
daily tournaments" and links the official daily flyer
(`clv-poker-daily-nlh-tournament-flyer-2026.pdf`). The page prints **no resort fee and no parking rate**,
which is why the Caesars Palace and Horseshoe fee cells stay blank rather than carrying a number.

## What was NOT re-read this session

These remain on their earlier retrieval dates, and the site shows that date on every row that uses them:

- The 36 Venetian structure sheets other than sheet 5. Their stored readings are offline-reconciled
  against the shipped data (`scripts/check_sheet_readings.py`, 481 field comparisons) but that is **not**
  a fresh read of the source.
- The Venetian schedule PDF (`dse-nov-2026-schedule.pdf`), the source of late-registration cut-offs and
  chip counts.
- Wynn daily structure PDF, Wynn Signature/WPT structure PDFs.
- Bellagio Sunday structure, Caesars flyer, Horseshoe, Resorts World, Westgate, Golden Nugget pages.
- Every hotel booking engine: a checkout total still requires an interactive session, and the Venetian
  date link still returns a loading shell.

## Irregularities raised by this session

| ID | Where | What | Status |
|---|---|---|---|
| **P-01** | Venetian/Palazzo hotel rows | Parking fee was cited to the poker room page, which prints no parking fee. | Fixed: re-cited to the hotel terms + poker-room parking page; gate added. |
| **N-05** | Bellagio poker page | Page still says tournament play "will resume on Saturday, July 26". | Published for review; rows keep their own PDF citations. |
| **N-06** | Schedule horizon | Official schedules read stop at 2026-12-23; earliest start in the series is 09:10 on 2026-12-12, so no 8 a.m. start exists. | Published; R-10 recorded as blocked. |
| **Marker** | Site root `index.html` | The committed landing page contained an unresolved merge-conflict marker (`<<<<<<< HEAD`) and the live Pages site rendered it. | Fixed by regenerating from `scripts/build_site.py`; `scripts/check_root_surface.py` now fails on any conflict marker in any published page. |

## Files changed by this session

- `2026/requirements.html` (new) + `data/verified2026/content.py` (requirements table, flags P-01/N-05/N-06)
- `scripts/build2026.py` (requirements page + nav; parking citation rendered; parking confirmation page watched)
- `scripts/recheck2026.py` (watch the parking confirmation page)
- `data/verified2026/hotels.py` (parking source re-pointed)
- `scripts/check_semantics.py` (parking-citation gate), `scripts/check_root_surface.py` (conflict-marker gate),
  `scripts/check2026.py` (new page in the link check)
- `index.html` (regenerated), `README.md`, `COORDINATION.md`
