# Research and verification log

**As-of date:** 2026-11-16 (UTC, per task context)  
**Repository at start:** one minimal README and no application files; initial commit `058cd5412575dad64023c3d0d0f7e15d6815016a`.  
**Evidence standard:** Official property / tournament organizer sources only for facts shown as confirmed. No third-party tournament calendars used to establish event facts. Blank cells are intentional.

## Repository audit

- Initial tree contained only an 8-byte `README.md`; no code, data model, tests, page layout, or deployment workflow existed.
- Created a no-dependency static site with separate category pages and GitHub Pages workflow.
- Built-in link checker verifies every local page and asset reference and verifies external hrefs are HTTPS. It does not assert that each remote server will continue serving its URL; direct official pages/PDFs were fetched during research.

## Official sources reviewed

### Venetian Resort

1. [DeepStack Extravaganza IV event page](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html) — reviewed dates, event names, buy-ins, guarantees, and links to structure sheets for the Nov 16–Dec 23, 2026 series.
2. [Official full schedule PDF](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf) — checked schedule rows for event dates/times, registration-close times, guarantees, starting stacks and levels. The schedule has multiple flights for several events; it does not itself state whether a player may enter more than one flight.
3. [Official $300 NLH one-day structure](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf) — checked $300 buy-in, $58 withheld for house fees, $242 prize-pool contribution, 11:10 a.m. start, 30-minute levels and registration closure. It does not specify a freezeout or re-entry rule.
4. [Official $200 NLH one-day structure](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_29.pdf) — checked $200 entry, $40 withheld, $160 prize-pool contribution, 11:10 a.m. start and structure. It does not specify entry restrictions.
5. [Official $400 NLH one-day structure](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_6.pdf) and [official $600 NLH structure](https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf) — checked level lengths / timing. Entry limits are not stated in the reviewed structures.
6. [Venetian Poker Room page](https://www.venetianlasvegas.com/resort/casino/poker.html) — confirms the room is at The Palazzo, Level 2, Grand Canal Shoppes; open 24 hours; property features and room location.
7. [2026 Poker Suite Rate page](https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html) — confirms rates start “as low as $119 and $209” for Venetian/Palazzo suites; rate/property mapping is not given on the page; rates depend on availability and qualifying play; $55 resort fee per night; requires six hours active live cash play or buy-in to a $300+ tournament per night.
8. [Hotel terms](https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html) — confirms 13.38% Clark County room tax (subject to change), $55 nightly standard resort fee plus applicable tax, and $150 per-night incidental deposit for non-Signature Suites.
9. [General Venetian Poker Room page](https://www.venetianlasvegas.com/resort/casino/poker.html) describes WPT Fall Festival ending Nov 15 as the “Current Series”; the [DeepStack series detail page](https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html) lists DeepStack Extravaganza IV starting Nov 16. The page-module inconsistency is flagged; event-specific schedule is used for event facts.

### Wynn / World Poker Tour

1. [Wynn Poker Room official page](https://www.wynnlasvegas.com/casino/poker) — confirms the Nov 27–Dec 21, 2026 WPT series, event schedule link, $400 Super Gold Million Mystery Bounty with $3 million guarantee, and daily tournament availability outside series periods.
2. [WPT World Championship official schedule PDF](https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf) — checked scheduled event dates, start times, buy-ins and guarantees, including $600/$400K, $800/$1M, WPT Prime $1,100/$5M, and $400 Mystery Bounty/$3M. The 10:00 a.m. start found on Dec 10 is later than the initial WPT series dates but earlier than the Venetian schedule's 10:10 a.m. starts.
3. [WPT official structure / event terms PDF](https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf) — checked event-specific entry rules. The $600 $400K event allows **unlimited re-entry per starting flight until Level 9**; the $800 $1M event does the same; the $1,100 WPT Prime allows **one entry plus one re-entry per starting flight** through Level 10. Each therefore fails the strict one-entry screen. The Prime terms prohibit a player who advances to Day 2 from entering a later flight. This is event-specific, not necessarily applicable to every series event.
4. [Wynn room and suite page](https://www.wynnlasvegas.com/rooms-and-suites) — official room category / booking information; no exact rate applied to dates because no travel dates were supplied.
5. [Wynn resort information](https://www.wynnlasvegas.com/about-us/resort-information) — current official page states $55 plus tax per room night for the standard resort fee and lists included amenities.
6. [Wynn 2026 awards statement](https://www.wynnlasvegas.com/stories/wynn-resorts-culinary-hospitality-awards) — states Wynn Tower Suites received a 20th consecutive Forbes Travel Guide Five-Star rating. This is not generalized to standard Wynn/Encore rooms.

### MGM Grand

1. [Official MGM Grand poker page](https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html) — lists daily Texas Hold'em tournaments at 11 a.m., 7 p.m. and 11 p.m.; it links to an official weekly schedule, full structure list and tournament promotions.
2. [Linked MGM schedule PDF](https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf) — titled “MGM Grand August Tournament Schedule” with no year; lists $120 NLH at 11:10 a.m., 7:10 p.m. and 11:10 p.m. every day, Saturday $150 NLH / $2,000 guarantee, and a Sunday-Friday five-entry promotion. Because the schedule is labeled August and no year is stated, it is not treated as a verified November schedule.
3. [Linked $120 NLH structure PDF](https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf) — states $120 initial entry with $92 prize pool, $13 house fee, $4 promotions and a voluntary $11 staff gratuity that gives 10,000 additional chips; 25,000 chips total; registration until Level 8. This ties a voluntary payment to more chips, so it is excluded from strict-cost recommendations pending clarification; the text does not say whether the $11 is additional to the $120 or an optional portion of the stated $120 allocation. Entry/re-entry policy is not stated in the reviewed text.
4. [Official MGM Grand hotel terms](https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html) — $50 nightly resort fee plus applicable tax; fee-waiver eligibility for certain MGM Rewards Gold+ members; $100/day incidental authorization; exact all-in totals require a reservation.
5. [Official MGM Grand FAQ](https://mgmgrand.mgmresorts.com/en/faq.html) — confirms check-in/out, extra-occupant fees and incidental terms.

## Verification outcomes

- **Strict single-entry-qualified events:** 0. No event in the reviewed material was both a good candidate and explicitly confirmed as a one-entry-only/no-add-on event by an official event-specific source.
- **Confirmed multiple-entry exclusions:** Wynn $600 / $400K NLH, Wynn $800 / $1M NLH, and Wynn $1,100 / $5M WPT Prime. Their re-entry policies are linked and stated in the site.
- **Unverified entry format:** Venetian single-day NLH candidates and Venetian multi-flight events. These are not classified as freezeouts; they remain held out of the verified table.
- **Hotel total:** exact nightly and stay totals cannot be computed without dates, guests and a live quote. Resort fees and known tax terms are stated separately; total cells remain blank.
- **Walk distance:** exact hotel-room-to-registration walking times were not found in official property pages; numeric walking values are not invented.
- **MGM promotion:** the official linked $120 NLH structure describes an optional $11 gratuity for 10,000 additional chips. It fails the strict “no more money for an advantage” screen. The linked schedule is titled August (year not stated), so its future/current $120 and Saturday $150/$2,000 terms need confirmation.
- **Schedule target:** no 8:00 a.m. event start was found in reviewed official event schedules. Earliest specific start found was 10:00 a.m. on Wynn's Dec 10 Mystery Bounty event; this is not a single-entry-qualified event.
- **Scope:** curated shortlist for useful near-term events and the official schedule source links. Not an exhaustive transcription of every Strip poker room's event calendar. Other casinos' third-party listings were not used as official evidence.

## Irregularities and open confirmations

- Venetian general room page's “Current Series” text is dated through Nov 15 while the detailed series page lists the next series starting Nov 16.
- The reviewed Venetian schedule/structures don't establish re-entry / add-on policies for listed candidates.
- MGM Grand's current poker page links to a schedule explicitly titled August with no year; it differs by ten minutes from the current page's round-hour start times. The linked $120 structure allows an optional $11 gratuity for 10,000 more chips, and the tournament's re-entry limit is not stated.
- Wynn's WPT event structures show unlimited/limited re-entry for several high-guarantee events, which materially changes maximum spend and is easy to miss from a schedule-only view.
- All hotel room totals and off-property walk times remain unverified/blank.

All flags and suggestions are published at the [Flagged for Review](../pages/review.html) and [Questions & Suggestions](../pages/decisions.html) pages.
