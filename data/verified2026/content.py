# Narrative content: other venues, flags, questions, suggestions, summary.
# Every claim here is tied to an official URL. Where a value could not be confirmed it is
# listed as a flag, not filled in.

ROOM_TAX = dict(
    value=13.38,
    text="13.38% transient lodging tax",
    source="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf",
    corroboration=("The official Venetian hotel terms state 'Clark County Room Tax of 13.38%' "
                   "(https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html). "
                   "Clark County Department of Business License letter dated 2016-11-15 (adopted rate; "
                   "Primary Gaming Corridor = 13.38%, effective 2017): "
                   "https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:7436500e-cac4-420a-b23a-02d3fec69900/original/as/room-tax-increase-transient-lodging-letter-111616.pdf "
                   "(re-read 2026-11-19; a 2016 notice, so the current county rate has not been re-checked against a live county table)."),
    retrieved="2026-11-17",
    note=("Re-read first-hand on 2026-11-17 from the county guide's own licence register, which lists "
          "'Venetian Resort Hotel Casino / Palazzo Resort Hotel Casino, 3325 Las Vegas Blvd S - Licensed - "
          "13.38% - RES - Transient Lodging Tax - Resort Hotel (PGC)'. Irregularity: the PDF the county "
          "serves at a '...july-2021.pdf' slug carries the internal title 'Genl Info Guide for TLEs Sept "
          "2018', so the document's own date and its URL disagree (flag F-15); the rate is also printed in "
          "the Venetian's own hotel terms, which is the corroboration the hotel rows cite."),
)

# Other Strip-area poker rooms. `status_this_session` records what happened when this session
# tried to reach the official page on 2026-11-17.
OTHER_VENUES = [
    dict(
        name="Wynn / Encore",
        poker_room="Wynn Poker Room (WPT World Championship host room)",
        status_this_session=("Read first-hand on 2026-11-17 at https://www.wynnlasvegas.com/casino/poker. "
                             "The room publishes three tournament documents - WPT World Championship (Nov 27 - "
                             "Dec 21), the Wynn Signature Series (January 11-24, 2027) and a daily-tournament "
                             "poster - and the page states the daily slate runs 'twice a day during non-event "
                             "timeframes' with '$200,000 in guaranteed prize pools weekly'. No start time is "
                             "printed on the page except the evening event ('a $10,000 guaranteed event every "
                             "evening at 6 p.m.'), and no buy-in is printed for any daily event. The older URL "
                             "this site used to cite, /casino/poker-room, returns Wynn's not-found page and is "
                             "the reason the scheduled re-check logged HTTP 404 for this venue."),
        url="https://www.wynnlasvegas.com/casino/poker",
        checked="2026-11-17",
        earlier_findings=[
            dict(text="Wynn's official WPT World Championship structures PDF prints 'Unlimited re-entry until the start of level 9' for the $600 Turbo, the $600 mixed-game events, and the $400 / $1,100 PLO events.",
                 url="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf",
                 retrieved="2026-11-16"),
            dict(text="The same PDF prints the buy-in splits, e.g. $600 NLH $400K GTD is $510 prize pool + $65 house fee + $25 staff gratuity.",
                 url="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf",
                 retrieved="2026-11-16"),
        ],
        verdict=("Excluded from the single-entry ranking. Two independent official statements support the "
                 "exclusion: the WPT structures PDF prints unlimited re-entry on named events, and the room's "
                 "own page advertises the Friday daily as a '$40,000 guaranteed NLH Rebuy' - a rebuy is a second "
                 "buy-in, so the event cannot enter a single-entry table on either reading."),
        provenance=("page itself read first-hand 2026-11-17; the WPT structures PDF lines are cited from an "
                    "earlier session's reading on 2026-11-16 and are labelled as such"),
    ),
    dict(
        name="Horseshoe Las Vegas",
        poker_room="Hall of Fame Poker Room",
        status_this_session=("The official poker sub-page redirects to the general casino page. That page confirms a "
                             "poker room with 20 tables and '6 exciting tournament times daily' but publishes no "
                             "buy-ins, guarantees, dates or structure sheet."),
        url="https://www.caesars.com/horseshoe-las-vegas/casino",
        checked="2026-11-17",
        earlier_findings=[
            dict(text="Caesars' own editorial page publishes the six daily start times: 9:00 AM, 11:00 AM, 2:00 PM, 5:00 PM, 8:00 PM and 11:00 PM.",
                 url="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
                 retrieved="2026-11-16"),
        ],
        verdict="Start times only. No buy-in, guarantee, structure or entry rule is officially published, so no row can be ranked.",
        provenance=("the six times were read first-hand on 2026-11-17 on Caesars' own poker-tournaments page "
                    "('9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m. and 11 p.m.'); the property's poker sub-page still "
                    "publishes no schedule and no structure sheet"),
    ),
    dict(
        name="Caesars Palace",
        poker_room="Caesars Palace Poker Room",
        status_this_session=("Read first-hand on 2026-11-17 on Caesars' own poker page. It does publish a daily "
                             "tournament slate for Caesars Palace: 'four No-Limit Hold'em tournaments each day at "
                             "10 a.m., 2 p.m., 6 p.m. and 9 p.m. Every event carries a $100 buy-in, starts you with "
                             "20,000 chips, and features a $1,000 guaranteed prize pool. Blinds increase every 20 "
                             "minutes ... and a $50 add-on at the first break gives you an extra 15,000 chips'. That "
                             "is the first time this site has an official buy-in, stack, guarantee and level length "
                             "for a Caesars daily; it is still not a structure sheet, and the add-on is decisive. The "
                             "property's own daily flyer PDF, read the same day (session arena/7cc9ee65-poker2), gives "
                             "the same four start times and the same $1,000 guarantee but prices them $100 / $160 / "
                             "$100 / $160 - see F-14."),
        url="https://www.caesars.com/caesars-palace/casino",
        checked="2026-11-17",
        earlier_findings=[
            dict(text="Caesars' corporate disclaimer publishes only a resort-fee range: 'a daily resort fee between $45-$50 plus applicable tax. Resort fees are waived for Diamond and Seven Stars.' No single property value is published.",
                 url="https://www.caesars.com/corporate/disclaimer",
                 retrieved="2026-11-16"),
            dict(text="Read live 2026-11-17 from the official daily flyer: 'All Tournaments feature a $50 add-on for 15,000 tournament chips that can only be taken at the first break. Registration will close at the start of level seven.'",
                 url="https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf",
                 retrieved="2026-11-17"),
            dict(text="Read live 2026-11-17: '3. Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.'",
                 url="https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf",
                 retrieved="2026-11-17"),
            dict(text="Read live 2026-11-17: '6. Of the $100 buy in, $70 goes to the prize pool and $30 is held by Caesars Palace as a maintenance fee.' and '7. Of the $160 buy in, $115 goes to the prize pool and $45 is held by Caesars Palace as a maintenance fee.'",
                 url="https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf",
                 retrieved="2026-11-17"),
        ],
        verdict=("Excluded from the single-entry table on the operator's own words: the published $50 add-on is a "
                 "second purchase of chips, which is exactly the money-buys-an-advantage case the brief puts in a "
                 "separate section. It can be listed and priced, but not compared like-for-like with the sheet-silent "
                 "Venetian candidates, and the buy-in conflicts between Caesars' own page ($100 for all four) and "
                 "its own daily flyer ($160 at 2 p.m. and 9 p.m.) - see F-14. The four rows are transcribed on the "
                 "Caesars Palace venue page."),
        provenance="read first-hand 2026-11-17 on the operator's own page and in its daily flyer PDF (session arena/7cc9ee65-poker2); the flyer conflict is carried from 2026-11-16",
    ),
    dict(
        name="Bellagio",
        poker_room="Bellagio Poker Room",
        status_this_session=("Re-read live on 2026-11-17 (session arena/7cc9ee65-poker2). The poker page now "
                             "links three official weekly structure sheets - Friday $600 NLH, Saturday NLH and "
                             "Sunday $400 H.O.R.S.E., all at 11:00 AM - each of which was read in full."),
        url="https://bellagio.mgmresorts.com/en/casino/poker.html",
        earlier_findings=[
            dict(text="The official Sunday $400 H.O.R.S.E. structure sheet states: 'Players may buy-in and re-enter through the end of level 8 (Including Break)' and that a voluntary $25 staff gratuity at registration grants an additional 15,000 starting chips.",
                 url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf",
                 retrieved="2026-11-16"),
            dict(text="The official Saturday NLH structure sheet contradicts itself ($1,100 heading vs $1,000 link label vs $600 rule text) and no value from it is used.",
                 url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf",
                 retrieved="2026-11-16"),
        ],
        verdict=("Publishes three weekly events with official structure sheets. Excluded from the single-entry "
                 "ranking: every sheet prints re-entry through level 8 and a gratuity that buys 15,000-20,000 "
                 "extra starting chips. Rows are published on the Bellagio venue page."),
        provenance="re-read live on 2026-11-17 by arena/7cc9ee65-poker2; the Saturday sheet still contradicts itself (X-04)",
    ),
    dict(
        name="MGM Grand",
        poker_room="MGM Grand Poker Room",
        status_this_session=("Re-requested live on 2026-11-17 (session arena/7cc9ee65-poker2): the poker page "
                             "now returns 'Oops! We can't find that page', so the earlier $120-sheet reading "
                             "can no longer be re-verified against a live official page. Irregularity X-06."),
        url="https://mgmgrand.mgmresorts.com/en/casino/poker.html",
        earlier_findings=[
            dict(text="The official $120 daily structure sheet prints: '$92 to Prize Pool, $13 House Fee and a once-time, voluntary gratuity of $11 which grants players an extra 10,000 chips. $4 will fund Tournament Promotions.'",
                 url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8e5621/mgm-grand-casino-poker-120_nlh.pdf",
                 retrieved="2026-11-16"),
            dict(text="The linked weekly grid is titled 'MGM Grand August Tournament Schedule' with no year stated: Mon-Fri 11:10 AM $120, Sat 11:10 AM $150 with a $2,000 guarantee, plus 7:10 PM and 11:10 PM $120 daily.",
                 url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8e5621/mgm-grand-casino-poker-120_nlh.pdf",
                 retrieved="2026-11-16"),
        ],
        verdict="Excluded from the single-entry ranking: the $11 gratuity buys 10,000 extra chips, a pay-for-advantage mechanic. The grid also has no year printed.",
        provenance="cited from an earlier session's reading",
    ),
    dict(
        name="Resorts World Las Vegas",
        poker_room="Resorts World Poker Room",
        status_this_session=("The official poker-room URL redirects to a poker-room *dining* page. No schedule, "
                             "buy-in, guarantee or structure sheet is published."),
        url="https://www.rwlasvegas.com/gaming/poker-room/",
        earlier_findings=[],
        verdict="No tournament data published on the official page.",
        provenance="checked this session",
    ),
    dict(
        name="Westgate Las Vegas",
        poker_room="Westgate Poker Room",
        status_this_session="Not re-read in this session.",
        url="https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/casino/poker/",
        earlier_findings=[
            dict(text="The official page publishes room hours (Mon-Fri 12:00 PM, Sat-Sun 10:00 AM), 7 nine-handed tables and a phone number. It publishes no tournament times, buy-ins or structures.",
                 url="https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/casino/poker/",
                 retrieved="2026-11-16"),
        ],
        verdict="No tournament schedule published. Third-party listings are not used.",
        provenance="cited from an earlier session's reading",
    ),
]

# --------------------------------------------------------------------------------------
# Requirements traceability (session arena/326322e9-poker2, 2026-11-19)
# --------------------------------------------------------------------------------------
# One row per discrete requirement in the standing brief, in the order the brief states it.
# `status` is only ever MET when this session checked the implementation AND the underlying
# evidence on 2026-11-19. PARTIAL means the page exists but the official evidence behind it is
# still missing; BLOCKED means no official source publishes what would be needed; NOT DONE is a
# real gap. Nothing here is upgraded by a build: the page is generated from this table.
#
# Fields: id, area, requirement (the brief's own words, trimmed), status, where (the page),
# evidence (what was actually checked), gap (what is still missing), source (official URL).

REQ_READ = "2026-11-19"

REQUIREMENTS = [
    dict(id="R-01", area="Schedule data",
         requirement="Find live upcoming poker tournaments near the Las Vegas Strip, focused on the Strip area.",
         status="PARTIAL",
         where="tournaments.html (64 event numbers, 94 scheduled rows) and the per-room pages",
         evidence=("Every row was re-read against the official Venetian DSE IV schedule on "
                   "2026-11-19 (all four HTML chunks, 94 rows: dates, start times, event numbers, "
                   "names, guarantees and structure-sheet links all match). Wynn, Caesars, Bellagio, "
                   "Horseshoe, MGM Grand, Resorts World, Westgate and Golden Nugget are covered on "
                   "their own pages, each with what that room does and does not publish."),
         gap=("Only one room publishes a full dated schedule for the trip window (Venetian). The "
              "other rooms are covered at the level of what they publish, not as a complete "
              "Strip-wide event feed."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="R-02", area="Eligibility",
         requirement="Focus on single-entry tournaments only: no double buy-in and no add-ons.",
         status="PARTIAL",
         where="tournaments.html (strict confirmed-only filter, rules-silent group), entry-rules.html",
         evidence=("All 37 official structure sheets were read. Zero of the 64 audited event numbers "
                   "print a whole-event one-entry / no-re-entry / no-rebuy / no-add-on clause, so the "
                   "confirmed-only filter correctly returns zero rows. Entry-rule fields are stored "
                   "separately per event with the quoted excerpt and retrieval date."),
         gap=("No event can be promoted to 'single-entry confirmed' until a room states it in "
              "writing. Sheet silence is not treated as a freezeout (flag F-01)."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf"),
    dict(id="R-03", area="Eligibility",
         requirement="Keep tournaments where money buys an advantage in a separate section.",
         status="MET",
         where="entry-rules.html (extra-spend group), venues/wynn.html (daily formats), tournaments.html group filter",
         evidence=("Events whose sheet prints re-entry, a rebuy, an add-on, a gratuity that buys "
                   "chips, or a priced subsequent buy-in are grouped out of the single-entry table "
                   "with the quoted clause. Wynn's four daily formats and Bellagio's weekly "
                   "structures were re-read on 2026-11-19 and all remain in that separate group."),
         gap="",
         source="https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"),
    dict(id="R-04", area="Ranking",
         requirement="Rank tournaments on cost to enter and prize pool, only after confirming total entry fee and guarantee.",
         status="PARTIAL",
         where="index.html top table, tournaments.html (Entry fee, House fee, To prize pool, Guarantee, GTD÷entry)",
         evidence=("Guarantee ÷ total entry fee is displayed as a descriptive ratio and labelled as "
                   "not a forecast. Bounty and flight events are labelled separately, because their "
                   "guarantee includes bounty money and is not like-for-like."),
         gap=("No ranking is presented as a recommendation, because no event has confirmed "
              "single-entry eligibility. Blank fees stay blank, so a ratio is only shown where both "
              "numbers are published."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf"),
    dict(id="R-05", area="Hotel",
         requirement="Find the best hotels within 30 minutes' walk of the tournaments; cost and quality matter more than distance.",
         status="PARTIAL",
         where="hotels.html, walking.html, venues/*.html (hotel table per room)",
         evidence=("Eight hotels are compared on published resort fee, tax, parking and cancellation "
                   "terms, each cell citing the official page that prints it. Address-based Google "
                   "Maps walking estimates to the Venetian poker room were recorded: seven of eight "
                   "are under 30 minutes (MGM Grand 42 min is over)."),
         gap=("No official star or diamond quality rating is published by any of these properties, so "
              "the quality half of this requirement has no verified source and stays blank (Q-03, "
              "S-06). Walking times are estimates and do not include the indoor route."),
         source="https://www.venetianlasvegas.com/resort/resort-fee.html"),
    dict(id="R-06", area="Hotel",
         requirement="Calculate the true cost per night: rate + mandatory resort fee + tax, with resort fees and parking included.",
         status="PARTIAL",
         where="hotels.html (Estimate lodging cost), trip.html (Trip totals), hotels.html#checkout-log",
         evidence=("The calculator applies (room + mandatory resort fee) × (1 + applicable tax rate) + "
                   "tax-inclusive parking, and 13.38% is only preloaded for the two properties whose "
                   "official terms print it. Parking is now cited to the pages that print the fee "
                   "(flag P-01, fixed 2026-11-19)."),
         gap=("No dated room rate exists for any hotel: the booking engine returned only a loading "
              "shell for the research dates, so every 'true cost' input is blank rather than assumed. "
              "13.38% is a Venetian/Palazzo figure, not a Strip-wide one."),
         source="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"),
    dict(id="R-07", area="Hotel",
         requirement="Capture checkout total, nightly average, mandatory resort fee and tax, parking, cancellation deadline and rate timestamp; compare like-for-like.",
         status="PARTIAL",
         where="hotels.html#checkout-log (each column is a separate field, plus retrieved date and audit note)",
         evidence=("The log schema carries every one of those fields per attempt, and one immutable "
                   "observation is written per lookup (2026-11-19: two Venetian/Palazzo attempts, one "
                   "historical Wynn attempt). Incomparable stays are kept separate rather than merged."),
         gap=("Zero comparable itemised checkout totals exist for the research window. The booking "
              "engines do not expose a total without an interactive session."),
         source="https://www.venetianlasvegas.com/book"),
    dict(id="R-08", area="Hotel",
         requirement="Keep rates as a dated log, not a single value.",
         status="MET",
         where="hotels.html (Dated rate log), every rate cell carries its own retrieval date",
         evidence=("Each hotel row carries a per-field read date, and the rate log keeps one dated "
                   "entry per lookup instead of overwriting a single number. The poker suite rate is "
                   "recorded as a conditional starting price, never as a quote."),
         gap="",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="R-09", area="Schedule",
         requirement="Use start time, late-registration cutoff and plausible duration to flag overlapping entries; one primary event per day plus a conditional fallback.",
         status="PARTIAL",
         where="schedule.html (day plan, overlap verdicts), tournaments.html (Starts)",
         evidence=("Start times and late-registration cut-offs are published on every structure sheet "
                   "and are used to decide whether two events can be played in sequence. An event "
                   "that is merely a second flight of the same tournament is labelled as such and is "
                   "not offered as a second entry."),
         gap=("No official sheet publishes a finish time, so no sequence is certified as playable. The "
              "day plan therefore shows one primary per day and no fallback, rather than an "
              "impossible sequence (flag F-04)."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_6.pdf"),
    dict(id="R-10", area="Schedule",
         requirement="Build a schedule where the player can play all day starting at 8 a.m.",
         status="BLOCKED",
         where="schedule.html, questions.html Q-04, flagged.html N-06",
         evidence=("Checked 2026-11-19: the earliest start printed anywhere in the Venetian series is "
                   "9:10 AM (event 46, Saturday 2026-12-12, a $260 turbo milestone satellite). Every "
                   "main-schedule event starts at 10:10 AM or later. The Wynn page states daily "
                   "tournaments are suspended during its series, and the WPT Championship it lists "
                   "runs 2026-11-27 to 2026-12-21."),
         gap=("No official page read publishes an eligible 8 a.m. start. An 8 a.m.-to-evening day "
              "cannot be built from verified events (flag N-06)."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="R-11", area="Trip cost",
         requirement="Add an estimated trip cost calculator: entries × buy-ins + nights × true hotel cost.",
         status="MET",
         where="trip.html, and the same estimator embedded on hotels.html",
         evidence=("The calculator totals selected entry fees and adds the lodging total, computes the "
                   "nightly average as checkout total ÷ nights, and refuses to print a combined total "
                   "while lodging is unknown. Selecting events does not imply they meet the entry "
                   "policy; the page says so."),
         gap="",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    dict(id="R-12", area="Data model",
         requirement="Store single-entry, re-entry, add-on and fee values separately for each event, each with its source excerpt and retrieval date.",
         status="MET",
         where="entry-rules.html (per-field readings with quoted clause, sheet link and read date), tournaments.html",
         evidence=("Each event carries its own entry-fee split (house fee and prize-pool contribution "
                   "separately), buy-in, late-registration cutoff, chip count and level length, each "
                   "with the quoted sentence from its own sheet and the date that sheet was read."),
         gap="",
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_18.pdf"),
    dict(id="R-13", area="Venues",
         requirement="One page per venue (Venetian, Wynn, others), each with its events and hotels.",
         status="MET",
         where="venues.html plus nine room pages (Venetian, Wynn, Horseshoe, Caesars Palace, Bellagio, MGM Grand, Resorts World, Westgate, other rooms)",
         evidence=("Each room page carries that room's events (or the documented reason it has no "
                   "verified dated row), its official address walking table with a 30-minute filter, "
                   "and its hotel/cost links. Rooms that publish no tournament schedule say so "
                   "instead of showing an empty table."),
         gap="",
         source="https://www.venetianlasvegas.com/resort/casino/poker.html"),
    dict(id="R-14", area="Navigation",
         requirement="Add a search box across all tables.",
         status="MET",
         where="every page (one site-wide index over every rendered table row)",
         evidence=("One committed index covers every rendered table row on all 24 pages of this "
                   "surface and is searched from a box in the header of each page; a no-match result "
                   "reports zero rather than going blank."),
         gap=("The repository root is a separate surface with its own generator. Its rate-log, "
              "schedule, single-entry, sources, walking and WPT-terms pages render tables with no "
              "search box. Reported to the owning session on the coordination board, not edited here."),
         source="index.html"),
    dict(id="R-15", area="Schedule data",
         requirement="Add a date filter that shows only events on the chosen days.",
         status="MET",
         where="tournaments.html (single date, inclusive range, today/upcoming in America/Los_Angeles)",
         evidence=("Date filtering is applied to the entry date of each event, and a restart is not "
                   "counted as a new entry. The upcoming filter compares against 2026-11-19 in Las "
                   "Vegas local time, not the viewer's time zone."),
         gap="",
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="R-16", area="Eligibility",
         requirement="Add a 'single-entry / freezeout confirmed' toggle filter on the tournaments table.",
         status="MET",
         where="tournaments.html",
         evidence=("The toggle exists and is separate from the 'rules silent' group filter; it is "
                   "honest about returning zero rows, because zero events are confirmed."),
         gap="",
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf"),
    dict(id="R-17", area="Schedule",
         requirement="Flag any two events that cannot be played in sequence (schedule overlap check).",
         status="PARTIAL",
         where="schedule.html (every pair on every day, with a verdict)",
         evidence=("Every pair of distinct events on a day is compared using published start times and "
                   "late-registration cut-offs; a same-event second flight is identified as such."),
         gap=("Without published finish times, a pair can only be cleared as 'no published overlap', "
              "never as definitely playable (flag F-04)."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-schedule.pdf"),
    dict(id="R-18", area="Walking",
         requirement="Add official-address walking times for each hotel–venue pair with the 30-minute limit applied.",
         status="PARTIAL",
         where="walking.html (all pairs, filter, Maps link per row), venues/*.html",
         evidence=("Every hotel × room pair has a row with the official street address as the origin, "
                   "the walking estimate, the 30-minute verdict and a prefilled Google Maps walking "
                   "link so the reader can confirm it. Address-based Google estimates to the Venetian "
                   "poker room were recorded on 2026-11-19 for all eight hotels."),
         gap=("The durations are routing estimates (OSRM from OpenStreetMap), not measurements, and "
              "none times the indoor route to the poker room on level 2. A 'verified ≤30 minutes' "
              "claim is not made (flag F-08)."),
         source="https://www.google.com/maps/dir/?api=1&origin=3355+S.+Las+Vegas+Blvd%2C+Las+Vegas%2C+NV+89109&destination=The+Venetian+poker+room&travelmode=walking"),
    dict(id="R-19", area="Monitoring",
         requirement="Re-check each official URL on a schedule and flag rows whose source changed.",
         status="MET",
         where="sources.html, flagged.html (source-changed badges), the row 'Source re-check' column",
         evidence=("A scheduled job re-fetches every official URL the site cites, hashes the content "
                   "and records a dated observation. A changed document is flagged against the rows "
                   "that depend on it and stays flagged until a person records a review. Earlier "
                   "runs that fetched a bot-challenge page as if it were a PDF were repaired, and "
                   "empty or non-PDF responses are now rejected."),
         gap="",
         source="sources.html"),
    dict(id="R-20", area="Monitoring",
         requirement="Add a 'last checked' date to each row.",
         status="MET",
         where="every table (a date per row, from that row's own source reading)",
         evidence=("Each row prints the date its own official document was read, not the build date. "
                   "A rebuild never refreshes a retrieval date."),
         gap="",
         source="https://www.venetianlasvegas.com/resort/resort-fee.html"),
    dict(id="R-21", area="Process",
         requirement="Use one shared COORDINATION.md on main before parallel sessions start.",
         status="MET",
         where="COORDINATION.md in the repository root",
         evidence=("The board is on main, lists each task with status, owning session and file scope, "
                   "and is updated by claim and by completion. This session claimed its scope before "
                   "editing anything and logged a request for the file it does not own."),
         gap="",
         source="../COORDINATION.md"),
    dict(id="R-22", area="Process",
         requirement="Review the repo line by line against official sources and flag irregularities.",
         status="MET",
         where="repo-review.html, flagged.html, research/326322e9-official-verification-2026-11-19.md",
         evidence=("This session re-read the primary sources the site depends on and recorded the "
                   "result row by row. Two new irregularities were found and published: P-01 (a "
                   "parking fee cited to a page that does not print it) and N-05 (a stale 'resume "
                   "26 July' notice on the Bellagio page). A third, N-06, records the schedule horizon."),
         gap="",
         source="../research/326322e9-official-verification-2026-11-19.md"),
    dict(id="R-23", area="Process",
         requirement="Publish a site with a clean landing page and subpages by category, tables and analysis included.",
         status="MET",
         where="the /2026/ surface: 25 generated pages behind one dashboard",
         evidence=("Each page is generated from the verified data by one generator, every internal "
                   "link is checked and every external citation is restricted to an official host."),
         gap="",
         source="index.html"),
    dict(id="R-24", area="Process",
         requirement="Write an executive summary and a dedicated suggestions section to review before any change.",
         status="MET",
         where="summary.html, latest-review.html, suggestions.html",
         evidence=("The summary states the conclusion and what blocks it. Suggestions are listed "
                   "unaplied, each with what it involves, what it decides, its cost and effort, and "
                   "which question it unblocks."),
         gap="",
         source="summary.html"),
    dict(id="R-25", area="Process",
         requirement="Provide a clear list of the questions, known and missing information, and answers needed before a decision.",
         status="MET",
         where="questions.html (Q-01 to Q-04 answered, Q-05 to Q-14 open), flagged.html (blank-cell inventory)",
         evidence=("Each question states why it matters, what decision it blocks, and whether it is "
                   "answered, open, or needs a person (for example age 50+ eligibility for the "
                   "Seniors events). The flagged page lists every category of blank in one place."),
         gap="",
         source="questions.html"),
    dict(id="R-26", area="Process",
         requirement="Improve decision-making with suggestions, and reveal missing information rather than inferring it.",
         status="MET",
         where="suggestions.html, flagged.html, latest-review.html",
         evidence=("Every blank cell is explained with the page that would have to publish it, so the "
                   "next step is a known action (call the room, run a quote, walk the route) rather "
                   "than a guess."),
         gap="",
         source="flagged.html"),
]

REQ_STATUS_NOTE = {
    "MET": "The page exists and this session checked the evidence behind it on 2026-11-19.",
    "PARTIAL": "The page exists, but official evidence for part of the requirement is still missing.",
    "BLOCKED": "No official source read publishes what this requirement needs. Right now that is "
               "the 8 a.m. all-day start.",
}

FLAGS = [
    dict(id="P-01", area="Source citation",
         title="The Venetian parking row cited a poker page that does not print the parking fees",
         detail=("Re-read 2026-11-19: the poker room page "
                 "(https://www.venetianlasvegas.com/resort/casino/poker.html) describes the room, its "
                 "location, hours, promotions and the poker suite rate. It does not print any parking "
                 "price. The published parking row was nonetheless attributed to it. The fees it quotes "
                 "($20/day registered guests; $20 Mon-Thu and $25 Fri-Sun for non-guests; $40/day valet) "
                 "and the 'three hours of play' self-parking benefit are printed verbatim on two other "
                 "official Venetian pages, both re-read 2026-11-19: the hotel terms and conditions "
                 "(Parking Fees section) and the poker-room self-parking page. The row is re-cited to "
                 "those two pages; the values themselves did not change."),
         impact=("No value on the site changed. What changed is that the citation now points at the page "
                 "that actually prints the number, so a reader who opens it sees the fee instead of a "
                 "page that never mentions it. A regression gate fails the build if the poker page is "
                 "used as the parking source again."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/player-parking.html"),
    dict(id="N-05", area="Official page defect",
         title="The Bellagio poker page still advertises tournament play as resuming on 26 July",
         detail=("Re-read 2026-11-19: the official Bellagio poker page still prints 'Tournament play will "
                 "resume on Saturday, July 26, beginning with the $300 PLO Double Board Bomb Pot "
                 "Tournament at 2 PM PT.' That date has long passed, so the notice is stale rather than a "
                 "livestream of the current schedule. The same page still links the three weekly "
                 "structure PDFs the site transcribes, and those PDFs were re-read 2026-11-19 and are "
                 "unchanged (see the verification record). The Saturday sheet also still prints a "
                 "Combined Final Day 2 of 9/13/26, already recorded as X-05."),
         impact=("The Bellagio rows stay published because their own structure PDFs were re-read and "
                 "match, but the room page itself cannot be used to prove the events are currently being "
                 "run. Confirmed by the room before travelling. The rows remain outside the single-entry "
                 "ranking."),
         source="https://bellagio.mgmresorts.com/en/casino/poker.html"),
    dict(id="N-06", area="Seed limits",
         title="Official schedules seen this session stop at 23 December 2026; no 8 a.m. eligible start exists in them",
         detail=("All four HTML chunks of the Venetian DSE IV page were re-read 2026-11-19: the series runs "
                 "November 16 to December 23, 2026. Read on the same day, the Wynn poker page lists the WPT "
                 "World Championship (November 27 to December 21) and the Wynn Signature Series (January 11 "
                 "to 24, 2027), and warns that daily tournaments are suspended during series. No official "
                 "page read this session publishes a date-specific tournament in January 2027 or later, "
                 "and the earliest start printed anywhere in the Venetian series is 9:10 AM (event 46, "
                 "December 12) - every main-schedule event starts at 10:10 AM or later."),
         impact=("A trip after 23 December 2026, or one that wants an 8 a.m. start, has no verified "
                 "schedule on this site yet. The dates remain a research window (Dec 1-4 2026) and the "
                 "day plan stays empty rather than inventing an 8 a.m. event."),
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    dict(id="F-01", area="Entry rules",
         title="No Venetian structure sheet states a single-entry or freezeout rule",
         detail=("All 37 official structure sheets were read on 2026-11-17. Not one contains the words "
                 "'single entry', 'one entry', 'freezeout' or 'no re-entry'. Every one-day sheet is simply "
                 "silent on re-entry, rebuy and add-on. Silence is not a prohibition, so no event is marked "
                 "'single-entry confirmed'."),
         impact="The strict filter returns zero rows. Events with silent rules remain research candidates only.",
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_7.pdf"),
    dict(id="F-02", area="Entry rules",
         title="Two events price a second buy-in on the official sheet",
         detail=("Events 18 and 58 ($200 Valuetown Bounty) print: 'PokerAtlas PRO players will receive a twenty "
                 "($20) rake discount on their initial $200 buy in only ... All subsequent buy in's after the "
                 "initial buy in will be $200.' Pricing a subsequent buy-in means more than one buy-in per "
                 "player is contemplated."),
         impact="Events 18 and 58 are moved out of the single-entry candidate group.",
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_8.pdf"),
    dict(id="X-01", area="Official document defect",
         title="The official schedule PDF has a garbled date column on 12 rows",
         detail=("In dse-nov-2026-schedule.pdf the DATE cell on 12 rows prints a sponsor banner "
                 "('@PokerAtlas PRO', '@PokerAtlas* TOUR') or a series logo ('LIPS CHAMPIONSHIP ...') instead of "
                 "the date. Those rows are events 17, 18, 32, 33, 35, 36, 39, 40, 46, 47 (1A), 49 (1A and 1B) "
                 "and 58."),
         impact=("Every affected date was recovered from the official HTML schedule page and is marked "
                 "'date from HTML' in the row detail. The PDF alone is not sufficient to place those events."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"),
    dict(id="F-03", area="Prize pools",
         title="Bounty guarantees include bounty money, so they are not like-for-like",
         detail=("Bounty and PKO sheets state the guarantee 'consists of the actual prize pool plus the total "
                 "amount of bounties that are awarded'. A $8,000 bounty guarantee is therefore a smaller cash "
                 "prize pool than a $8,000 non-bounty guarantee."),
         impact="Bounty events are shown in a separate group and are never mixed into the like-for-like ranking.",
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_1.pdf"),
    dict(id="F-04", area="Schedule",
         title="No official finish time is published for any event",
         detail=("The schedule gives start time, registration close, chips and level length, but no end time. "
                 "A finish time cannot be derived without a field size, which the organiser does not publish "
                 "in advance."),
         impact=("The day plan compares start order with the later registration deadline. A later event is conditional, not a guaranteed sequence; no unconfirmed event becomes a primary."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"),
    dict(id="F-05", area="Hotels",
         title="No like-for-like checkout totals were confirmed",
         detail=("A Venetian Dec 1–4 lookup for one adult loaded an official booking shell without a price. "
                 "Wynn showed partial Nov 18–19 rates for a different stay, which cannot be compared. "
                 "Neither supplied a verified itemized total or rate timestamp for the research stay."),
         impact="Do not rank hotels by the partial rates or assume availability. See the exact-stay hotel log.",
         source="https://www.venetianlasvegas.com/book?adults%5B%5D=1&arrival_date=2026-12-01&children%5B%5D=0&departure_date=2026-12-04&view=calendar"),
    dict(id="F-06", area="Hotels",
         title="Cancellation deadlines are partial: two properties publish 72 hours, the rest do not",
         detail=("Partly resolved on 2026-11-17 by reading each property's own terms page first-hand. "
                 "Bellagio and MGM Grand both publish a 72-hour window: the first night's deposit is "
                 "fully refundable if Room Reservations is told at least 72 hours before arrival, and a "
                 "late cancellation or no-show forfeits it. Caesars Palace and Horseshoe advertise "
                 "'FREE 48-Hour Cancellation*' with an asterisk whose condition is not printed on the "
                 "page read. The Venetian and Palazzo publish no poker-rate deadline, but do publish "
                 "that prepaid offers are non-cancellable and non-refundable unless the offer says "
                 "otherwise, and that checking out early costs $100 plus tax. Wynn publishes deposit "
                 "terms only (one night charged at booking) and no refund window."),
         impact=("For a Bellagio or MGM Grand stay you can plan a refundable hold until 72 hours out. "
                 "For the Venetian poker rate, which is the rate this plan depends on, the deadline is "
                 "still not established, so treat the deposit as committed."),
         source="https://bellagio.mgmresorts.com/en/terms-and-conditions.html"),
    dict(id="F-07", area="Taxes",
         title="Room tax: the hotel's own terms are re-read, the county levy is not",
         detail=("13.38% comes from Clark County's own 'General Information Guide for Transient Lodging "
                 "Establishments' and is corroborated by the Venetian's hotel terms. It was read on 2026-11-16 "
                 "by an earlier session. On 2026-11-19 the 2016 Clark County notice adopting the 13.38% "
                 "Primary Gaming Corridor rate was re-read (see the ROOM_TAX note). The current county rate "
                 "table has not been re-checked."),
         impact="Used as the calculator default. Re-check on the county page before you book.",
         source="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf"),
    dict(id="F-08", area="Walking",
         title="Walking times are route estimates, not measured door-to-seat durations",
         detail=("The walk matrix was computed from OpenStreetMap data with the OSRM foot profile "
                 "(routing.openstreetmap.de/routed-foot) on 2026-11-16. Eight hotel-to-Venetian routes were also checked in Google Maps on 2026-11-19; neither source measures an actual walk."),
         impact="Use the Maps-checked filter for a shortlist and leave a buffer for indoor elevators, crowds and venue access.",
         source="https://www.openstreetmap.org/"),
    dict(id="F-09", area="Other venues",
         title="The Wynn poker citation on this site pointed at a page that no longer exists",
         detail=("https://www.wynnlasvegas.com/casino/poker-room returns Wynn's 'IT SEEMS THIS PAGE HAS CHECKED "
                 "OUT' not-found page, which is why the scheduled re-check logged HTTP 404 for the Wynn row on "
                 "2026-11-17. The room's live page is https://www.wynnlasvegas.com/casino/poker, read there "
                 "first-hand on 2026-11-17, and every Wynn citation on this site now points at it. What that "
                 "page does *not* publish: a buy-in for any daily event, any one-entry or re-entry limit for "
                 "the daily slate, or a start time other than the 6 p.m. evening guarantee. The WPT structures "
                 "PDF lines still come from the 2026-11-16 reading and stay labelled as such."),
         impact=("Until the room states an entry limit, no Wynn event can leave the 'not single-entry confirmed' "
                 "group - the page was reachable, the missing values are genuinely unpublished, not unfetched."),
         source="https://www.wynnlasvegas.com/casino/poker"),
    dict(id="F-10", area="Other venues",
         title="Entry rules and date coverage vary by poker room",
         detail=("The complete row-by-row audit covers DSE IV only. The morning watch links the other official "
                 "documents available, including Wynn, Caesars Palace and Bellagio. Missing or contradictory "
                 "terms are not evidence of a freezeout."),
         impact="No events outside the audited rules are promoted into the recommendation.",
         source="https://www.caesars.com/horseshoe-las-vegas/casino"),
    dict(id="F-11", area="Hotels",
         title="A per-night rate is not the bill: occupancy and early-departure charges",
         detail=("The properties charge more than the nightly rate and resort fee in two ways a rate "
                 "comparison misses. The Venetian and Palazzo add $50 per night for each additional "
                 "guest 13 or older above double occupancy, and $100 plus tax for checking out before "
                 "the scheduled departure date. Bellagio adds $50 plus tax per occupant per night above "
                 "two. MGM Grand adds $40 plus tax per occupant per night above two. Caesars Palace and "
                 "Horseshoe do not publish an occupancy charge on the page read."),
         impact=("As a pair, the published rates and the calculator are right. With a third adult in "
                 "the room the nightly cost rises by $50 (Venetian) or $40 (MGM Grand) plus tax, which "
                 "can exceed the difference between two hotels."),
         source="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"),
    dict(id="F-12", area="Hotels",
         title="Caesars Palace and Horseshoe do not publish a resort fee on the page read",
         detail=("Both properties' official pages were read on 2026-11-17: the resort-hotel page, the "
                 "casino page and the hotel page. None prints a resort-fee amount; only a 48-hour "
                 "cancellation headline and 'valet and self-parking available' appear. Figures of "
                 "$54.95 and $49.95 are widely repeated by aggregator sites and are deliberately not "
                 "used here."),
         impact=("Those two properties cannot be costed on this site, so they cannot win a cost "
                 "comparison. They stay in the walking tables because distance is published."),
         source="https://www.caesars.com/horseshoe-las-vegas/hotel"),
    dict(id="F-13", area="Monitoring",
         title="The scheduled re-check had never run, and this sandbox cannot reach the venue sites",
         detail=("GitHub Actions had recorded no run of .github/workflows/recheck.yml, so no baseline "
                 "hash existed for any official URL. Two consequences were visible in the site text: it "
                 "pointed at data/site/checks.json, which the scheduled job does not write (it writes "
                 "data/verified2026/checks.json), and nothing read that file to mark rows. Both are fixed "
                 "- every tournament row now carries a Source re-check cell driven by the real file, and "
                 "scripts/check_monitor_badge.py fails the build if the badge stops marking changed rows. "
                 "This sandbox has no outbound access to the venue hosts (curl returns "
                 "SSL_ERROR_SYSCALL; the workflow-dispatch API is not permitted), so the first baseline "
                 "can only be set by the 06:00 UTC job running on main."),
         impact=("Until that job runs, every row reads 'not yet checked'. That is the honest state and "
                 "is deliberately not rendered as 'unchanged'."),
         source=".github/workflows/recheck.yml (repository file, not an external citation)"),
    dict(id="F-14", area="Other venues",
         title="Two official Caesars documents print different daily buy-ins for the same room",
         detail=("Caesars' poker-tournaments page, re-read first-hand on 2026-11-17, prints '$100 buy-in ... "
                 "$1,000 guaranteed prize pool' for the four daily Caesars Palace events. The property's own "
                 "daily NLH flyer, read 2026-11-16, prints $160 for the 2 p.m. and 9 p.m. starts. Both are "
                 "official; neither corrects the other. Nothing on this site picks a winner: the room is listed "
                 "with both citations and is excluded from the ranking regardless, because the page also prints "
                 "a $50 add-on."),
         impact="Do not use a disputed buy-in as a verified price. The official flyer independently excludes these events from the strict itinerary.",
         source="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    dict(id="F-15", area="Taxes",
         title="The county tax guide's own title and its URL disagree by three years",
         detail=("The Clark County transient-lodging guide the room-tax figure is cited from is served at a slug "
                 "ending 'july-2021.pdf' while the document's internal title reads 'Genl Info Guide for TLEs Sept "
                 "2018'. The rate itself was confirmed first-hand on 2026-11-17 from the licence register inside "
                 "that document, which lists the Venetian / Palazzo at 13.38% under 'Transient Lodging Tax - "
                 "Resort Hotel (PGC)', and the same 13.38% is printed in the Venetian's own hotel terms."),
         impact=("The 13.38% used by the calculators is corroborated by two documents, but the county copy is not "
                 "fresh-dated. Re-check the current rate with the room's checkout itemisation before you treat a "
                 "true-cost figure as final."),
         source="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf"),
    dict(id="F-16", area="Monitoring",
         title="Ten of the cited documents could not be read by the scheduled monitor",
         detail=("The 2026-11-17 run of .github/workflows/recheck.yml fetched 61 URLs: 51 answered, 10 did not "
                 "(Caesars and Horseshoe pages returned 403 or redirect loops behind bot protection, the MGM "
                 "Resorts and Bellagio terms pages timed out, one MGM asset returned 422, and the old Wynn "
                 "poker-room URL 404s). Recheck2026.py now classifies each failure and the Sources page lists "
                 "them, because 'could not read' and 'read, unchanged' are different statements - and the monitor "
                 "refuses to record a run in which nothing at all was readable, so a sandbox with no outbound "
                 "access cannot overwrite real coverage with zeroes."),
         impact=("Those rows carry no fresh machine assurance; their values keep their own last human-verified "
                 "date. Read the linked page by hand before a non-refundable payment."),
         source=".github/workflows/recheck.yml and data/verified2026/checks.json (repository files, not external citations)"),
    dict(id="X-02", area="Official page (resolved)",
         title="The Venetian overview now labels DeepStack IV as current",
         detail="A Nov 19 re-read confirmed that the Nov 17 stale WPT Fall Festival label was corrected.",
         impact="Use the dated schedule for each specific event.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"),
    dict(id="X-09", area="Venetian NYE schedule",
         title="Official NYE sources disagree on Ante Up entry price; some dates print 2025",
         detail=("The Nov 19 overview advertises the Dec 27–31 Ante Up Championship at $2,200. "
                 "The dated schedule and linked event #8 structure sheet say $1,100 with a $300,000 guarantee. "
                 "The HTML schedule also lists three Dec 26 starts as 2025 while the series header says 2026–27."),
         impact="Do not rank these rows or resolve the date or price by inference.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    dict(id="X-10", area="Wynn WPT schedule",
         title="Wynn schedule's extracted Dec 18 Wednesday label needs confirmation",
         detail=("The second page of the Nov 27–Dec 21 official PDF was reviewed Nov 19. The readable table "
                 "contains a 'Dec. 18 Wednesday' block and a separate 'Dec. 18 Friday' block. "
                 "The Wednesday rows could be a PDF extraction issue. Their date is not resolved by inference."),
         impact="Open the source PDF and confirm the date against the applicable official structure sheet before planning.",
         source="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"),
    dict(id="X-03", area="Official page defect",
         title="Bellagio's poker page gives a resume date whose weekday does not exist",
         detail=("The official page says 'Tournament play will resume on Saturday, July 26, beginning with the "
                 "$300 PLO Double Board Bomb Pot Tournament at 2 PM PT.' 26 July 2026 is a Sunday, so the "
                 "weekday and the date on the page disagree. The three weekly structure sheets are treated as "
                 "the operative schedule instead."),
         impact="Do not plan around that resume date; confirm the day with the room.",
         source="https://bellagio.mgmresorts.com/en/casino/poker.html"),
    dict(id="X-04", area="Official document defect",
         title="Bellagio's Saturday sheet prints two different buy-ins",
         detail=("The sheet is headlined 'NLH $1100 BUY-IN' while its own rule 7 splits '[t]he $600 Buy-in' into "
                 "$510 prize pool, $50 admin fees and $40 optional staff gratuity. Read 2026-11-17. No buy-in is "
                 "published for that event: the two figures are shown side by side and left blank."),
         impact="The Saturday event cannot be costed or ranked until the room says which figure is current.",
         source="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"),
    dict(id="X-05", area="Official document defect",
         title="Bellagio's Saturday sheet names a final-day date that has already passed",
         detail=("The same sheet prints 'Combined Final Day 2 (9/13/26) will begin at 12pm at Bellagio'. That "
                 "date was already past when the sheet was read on 2026-11-17, so the document may be a stale "
                 "series sheet rather than the current weekly event."),
         impact="Treat the Saturday event as unconfirmed until the room republishes the sheet.",
         source="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf"),
    dict(id="X-06", area="Official page unavailable",
         title="MGM Grand's poker page no longer resolves",
         detail=("https://mgmgrand.mgmresorts.com/en/casino/poker.html returned 'Oops! We can't find that page' "
                 "when requested live on 2026-11-17. An earlier session had read a $120 daily structure sheet "
                 "from this room, with a $11 gratuity that buys 10,000 extra chips."),
         impact=("The MGM Grand finding is published as historical provenance only. It cannot be re-verified "
                 "against a live official page, so it is not used as a current citation."),
         source="https://mgmgrand.mgmresorts.com/en/casino/poker.html"),
    dict(id="X-07", area="Official page unavailable",
         title="The Wynn URL this site used to cite returns a not-found page",
         detail=("https://www.wynnlasvegas.com/casino/poker-room returned 'IT SEEMS THIS PAGE HAS CHECKED OUT' "
                 "when requested live on 2026-11-17, which is why the scheduled re-check logged HTTP 404 for "
                 "this venue. The room's live page is https://www.wynnlasvegas.com/casino/poker, read the same "
                 "day by another session: it publishes three tournament documents and states a $10,000 "
                 "guaranteed event every evening at 6 p.m., but prints no buy-in for any daily event."),
         impact=("The 404 is a dead citation, not a dead room. Use /casino/poker for Wynn; anything cited "
                 "from /casino/poker-room is historical provenance."),
         source="https://www.wynnlasvegas.com/casino/poker-room"),
    dict(id="X-08", area="Monitoring gap",
         title="The scheduled re-check reports fetch errors for pages that do load in a browser",
         detail=("The 2026-11-17T15:49Z run of recheck.yml fetched 61 official URLs: 51 set a baseline and 10 "
                 "returned a fetch error. The ten are all Caesars, Bellagio and MGM Grand HTML pages. Three of "
                 "them - the Bellagio poker page and the Caesars Palace and Horseshoe casino pages - were then "
                 "fetched successfully by hand on 2026-11-17 and are quoted elsewhere on this site, so those "
                 "pages are live and the error is the job's request being refused, not a missing page."),
         impact=("A 'monitor could not fetch' badge is a gap in monitoring, not a change to the source. Do not "
                 "read it as the page having moved, and re-check those pages by hand before paying."),
         source="data/verified2026/checks.json (committed by .github/workflows/recheck.yml)"),
    dict(id="C-01", area="Coverage",
         title="Two rooms publish schedules that are not in the ranked tables",
         detail=("Caesars Palace (four daily NLH events) and Bellagio (three weekly events) both publish "
                 "official schedule documents, read live on 2026-11-17. Every one of those events is a "
                 "re-entry or add-on event on the face of its own sheet, so none of them can enter the "
                 "single-entry ranking; they are published on their venue pages instead."),
         impact=("The ranked table stays Venetian-only not because other rooms publish nothing, but because "
                 "the rooms that do publish are not single-entry. That is a finding, not a coverage gap."),
         source="https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf"),
]

# Look-up used by the per-room venue pages. Keys match ROOM_META in scripts/build2026.py.
OTHER_VENUES_BY_ID = {
    "wynn": next(v for v in OTHER_VENUES if "Wynn" in v["name"]),
    "horseshoe": next(v for v in OTHER_VENUES if "Horseshoe" in v["name"]),
    "caesars-palace": next(v for v in OTHER_VENUES if "Caesars Palace" in v["name"]),
    "bellagio": next(v for v in OTHER_VENUES if "Bellagio" in v["name"]),
    "mgm-grand": next(v for v in OTHER_VENUES if "MGM Grand" in v["name"]),
}

QUESTIONS = [
    dict(id="Q-01", q="What entry rule qualifies an event?",
         why="Only a written whole-event cap of one entry, with no paid rebuy or add-on, satisfies this trip's policy.",
         blocks="A bookable poker itinerary until an organizer supplies those written terms.",
         answer="Answered: strict freezeout only."),
    dict(id="Q-02", q="Which dates should be tested before booking?",
         why="Hotel rates, walking plans and the day-by-day schedule are all date-bound. The poker suite rate is only quoted 150 days out and only by phone.",
         blocks="A real itinerary and comparable checkout totals.",
         answer="Research only: Dec 1–4, 2026 (three nights, one adult, one room). Do not book on this evidence."),
    dict(id="Q-03", q="Which budget and quality screen should the first hotel pass use?",
         why="Compare like-for-like checkout totals after checking the room amenities and walking eligibility.",
         blocks="The hotel shortlist and ranking until checkout and room features are verified.",
         answer="Research screen, not a preference claim: $200/night all-in, private nonsmoking room with ensuite bath, and a refundable booking with a published deadline."),
    dict(id="Q-04", q="Can a primary and conditional fallback fit without assuming an early exit?",
         why="You asked to play from 8 AM onward. The earliest verified Venetian start in this series is 9:10 AM (satellite event 46) and 10:10 AM for a main-schedule event.",
         blocks="A full 8 AM-to-evening day plan.",
         answer="One qualified primary per day; switch only if it is skipped or the player is free in time. No qualified primary or fallback verified."),
    dict(id="Q-05", q="Are you 50 or older?",
         why="Events 24, 32 and 49 are Seniors events with a hard 50+ rule and no refund for an under-50 entrant. They carry $40K, $40K and $300K guarantees, three of the larger figures in the series.",
         blocks="Whether three of the better-value events are available to you at all.",
         answer=None),
    dict(id="Q-06", q="Do you have, or will you open, a Venetian Rewards card?",
         why="Every structure sheet requires one to participate, and the poker suite rate is tracked through it.",
         blocks="Both entering any Venetian event and qualifying for any quoted poker suite rate.",
         answer=None),
    dict(id="Q-07", q="Do you object to bounty formats on principle, or only to paying extra for an advantage?",
         why="A bounty does not establish whether extra spending is allowed. Its guarantee can include bounty money and is not like-for-like with a cash-only guarantee.",
         blocks="Whether the 30 bounty and PKO events belong in your plan.",
         answer=None),
    dict(id="Q-08", q="Is a paid PokerAtlas PRO membership acceptable?",
         why="It buys a $20 rake discount on Valuetown events 18 and 58 and on the first buy-in only. That is a spend-to-advantage element.",
         blocks="Events 18 and 58.",
         answer=None),
    dict(id="Q-09", q="Will you have a car?",
         why="Parking adds $20-$40 a day at the Venetian unless you qualify for free self-parking through play or tier status. It changes the true nightly cost.",
         blocks="The parking line in the true-cost calculator.",
         answer=None),
    dict(id="Q-10", q="Do you want the Day 2 restarts counted as playable days?",
         why="Twelve rows in the schedule are Day 2 / Day 3 / final-table restarts. They cost nothing extra but occupy a morning or afternoon.",
         blocks="The day plan for 12 of the 38 series days.",
         answer=None),
    dict(id="Q-11", q="Should satellites be in the plan?",
         why="Events 33, 37, 41, 44, 45, 46 and 48 award seats, not cash. They are cheap ways into Event 39 or 47 but they are not prize-money events.",
         blocks="Seven events and three of the earliest start times in the series.",
         answer=None),
    dict(id="Q-12", q="How much variance do you accept on the guarantee-to-buy-in ratio?",
         why="The ratio is descriptive, not a forecast. A $500K guarantee on an $800 buy-in is a floor set by the room; the actual pool depends on entries.",
         blocks="How the ranking column should be read.",
         answer=None),
    dict(id="Q-13", q="Will you travel with more than two adults in the room?",
         why=("The Venetian, Palazzo, Bellagio and MGM Grand all surcharge a third adult, from $40 to "
              "$50 plus tax per night, which changes the cheapest-hotel answer."),
         blocks="The hotel half of the trip cost and the cost comparison between properties.",
         answer=None),
    dict(id="Q-14", q="Do you accept a booking with no published cancellation deadline?",
         why=("The Venetian poker rate, which the whole plan leans on, publishes no cancellation "
              "deadline. Bellagio and MGM Grand publish 72 hours. Booking the Venetian means treating "
              "the deposit as committed."),
         blocks="Whether the Venetian poker rate can be used for a trip whose dates are not yet fixed.",
         answer=None),
]

SUGGESTIONS = [
    dict(id="S-01", title="Get the entry rule in writing from the Venetian poker room",
         what="Email lv_cas_poker@venetianlasvegas.com or call 702.414.7657 and request written confirmation of one total entry across all flights, no re-entry or rebuys, no add-ons and no optional payment for a competitive advantage.",
         decides="Whether any event can be promoted from 'no re-entry clause printed' to 'single-entry confirmed'.",
         cost="One email", effort="Low", blocks="Q-01"),
    dict(id="S-02", title="Request an itemized poker suite quote by phone",
         what="Call 866.255.8936 with code EPOKR25. The rate is only quoted 150 days out and cannot be booked online.",
         decides="Your true nightly cost. Confirm property, dates, availability, cancellation and how play is applied to each night before booking.",
         cost="One call", effort="Low", blocks="Q-02"),
    dict(id="S-03", title="Confirm the 30-minute walk with Google Maps on the pairs you care about",
         what="Every row in the walking table carries a prefilled Google Maps walking-directions link. Open the two or three that matter and read the live time.",
         decides="Whether the routed estimate stands.",
         cost="Five minutes", effort="Low", blocks="F-08"),
    dict(id="S-04", title="Time the complete walk, including the casino interior",
         what="A route estimate does not capture the hotel exit, footbridge detours, elevators, or the poker-room entrance. Check the official indoor directions and time the entire route.",
         decides="Whether borderline routes still fit the 30-minute limit.",
         cost="One walk per shortlisted route", effort="Medium", blocks="F-08"),
    dict(id="S-05", title="Capture a real dated checkout total",
         what="Run the official booking flow for your dates and paste the itemised total (rate, resort fee, tax, parking) into the rate log.",
         decides="The nightly-average and checkout-total columns, which are blank today.",
         cost="Ten minutes at booking time", effort="Low", blocks="F-05"),
    dict(id="S-06", title="Add an official quality rating source",
         what="Nothing on any official hotel page states a star or diamond rating. Pick one authority (Forbes, AAA) and cite it, or leave quality as your own judgement.",
         decides="The quality column, which is blank today.",
         cost="A subscription or a decision", effort="Medium", blocks="Q-03"),
    dict(id="S-07", title="Have the daily monitor alert on value changes, not just page hashes",
         what="Today's scheduled job hashes the whole page. Extend it to track the specific sentences each row is transcribed from, so a changed buy-in is reported as a buy-in change.",
         decides="Whether a source change is actionable or just noise.",
         cost="Small script change", effort="Medium", blocks=None),
    dict(id="S-08", title="Audit the two upcoming Venetian series event by event",
         what="The NYE and Showdown documents are already watched. Read each official structure sheet and reconcile it with the dated schedule before adding individual rows.",
         decides="Whether any additional dated event meets the policy.",
         cost="Read and cross-check each sheet", effort="Medium", blocks=None),
    dict(id="S-09", title="Decide whether the archived dashboards should be deleted",
         why="Three earlier sessions published overlapping dashboards (docs/, verified/, pages/, plan/). They are still served but are superseded.",
         decides="Repo cleanliness versus keeping the audit trail.",
         cost="One decision", effort="Low", blocks=None),
    dict(id="S-10", title="Consolidate the three scheduled monitor jobs into one",
         what="recheck.yml, source-monitor.yml, plan-refresh.yml and plan-verify.yml all re-check overlapping URLs on different cron schedules.",
         decides="Whether you get one daily digest or three.",
         cost="Small workflow edit", effort="Low", blocks=None),
    dict(id="S-11", title="Show a per-row source-change badge, and keep the monitor honest",
         what=("Done on 2026-11-17. Every tournament row now carries a Source re-check cell "
               "(unchanged / source changed / fetch error / baseline set) generated from "
               "data/verified2026/checks.json, and scripts/check_monitor_badge.py fails the build if the "
               "badge stops marking changed rows."),
         decides="Whether a row you are about to act on has moved under you since it was transcribed.",
         cost="Already implemented", effort="Done", blocks="F-13"),
    dict(id="S-12", title="Turn the page-hash monitor into a per-sentence diff",
         what=("The monitor hashes a whole page, so a change tells you the document moved, not which "
               "value moved. Tracking the sentence each row was transcribed from would tell you the "
               "buy-in changed. This is the remaining half of S-07."),
         decides="Whether a changed source needs one row re-read or all of them.",
         cost="About a day; the per-row excerpts already exist", effort="Medium", blocks="F-13"),
]

# Read from data/verified2026/checks.json (the run of 2026-11-17T15:49:57Z) rather than typed by
# hand, so the ten URLs named here are exactly the ten the monitor could not read.
def _unread_flags():
    import json, os
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        d = json.load(open(os.path.join(here, "checks.json"), encoding="utf8"))
    except (OSError, ValueError):
        return []
    run = (d.get("runs") or [{}])[0]
    bad = [r for r in run.get("results", []) if r.get("status") != 200]
    if not bad:
        return []
    rows = "".join(
        "<li><code>%s</code> &mdash; %s (%s)</li>"
        % (r.get("url"), r.get("status") if r.get("status") else "no response",
           (r.get("error") or "no error text recorded").split(":")[0][:60])
        for r in bad)
    return [dict(id="F-14", area="Monitoring",
                 title="Ten of the 61 monitored official URLs could not be read on the last scheduled run",
                 detail=("The scheduled re-check ran on %s and read 51 of 61 URLs successfully. The ten "
                         "below returned an HTTP error, a redirect or a timeout, so the site can say only "
                         "that they were not read - not that they are unchanged. None of the ten is cited "
                         "by a tournament row; six are hotel fee or cancellation citations.<ul>%s</ul>"
                         % (run.get("checked") or "the last run", rows)),
                 impact=("A hotel fee or cancellation term sourced from one of these pages rests on the "
                         "reading date shown on that hotel's row, not on the latest check. Re-open the "
                         "link before you rely on the term."),
                 source=(bad[0].get("url") if bad else ""))]


FLAGS = FLAGS + _unread_flags()

SUMMARY_HEADLINE = ("Do not book this trip on the current evidence. No event in the reviewed dataset "
                    "meets the written whole-event freezeout policy, and no comparable hotel checkout totals were verified.")

# label, site page, evidence note, official landing page, official schedule (if known)
SCHEDULE_FEED = [
    ("Venetian · DeepStack IV", "venues/venetian.html", "Nov 16–Dec 23, 2026 · audited structure sheets",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    ("Venetian · NYE", "venues/venetian.html", "Dec 24, 2026–Jan 10, 2027 · rules not yet audited",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html"),
    ("Venetian · January Showdown", "venues/venetian.html", "Jan 11–Feb 14, 2027 · rules not yet audited",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dss-jan-2027.html"),
    ("Wynn · WPT World Championship", "venues/wynn.html", "Nov 27–Dec 21, 2026 · see date discrepancy and entry-rule coverage",
     "https://www.wynnlasvegas.com/casino/poker",
     "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"),
    ("Wynn · Daily tournaments", "venues/wynn.html", "Daily during non-event timeframes; not guaranteed on any trip date",
     "https://www.wynnlasvegas.com/casino/poker",
     "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"),
    ("Venetian · Ante Up Championship", "venues/venetian.html", "NYE entry price discrepancy; not ranked",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-dec-2026.html",
     "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_dec_2026-structure_6.pdf"),
    ("Wynn · Signature Series", "venues/wynn.html", "Jan 11–24, 2027 · rules not yet audited",
     "https://www.wynnlasvegas.com/casino/poker",
     "https://cdn.wynnresorts.com/image/upload/v1753296112/visitwynn_pdfs_files/Poker/Wynn%20Signature%20Series/Wynn_Signature_Series_Schedule.pdf"),
    ("Caesars Palace", "venues/caesars-palace.html", "Daily flyer; paid add-on and re-entry",
     "https://www.caesars.com/caesars-palace/casino",
     "https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf"),
    ("Bellagio", "venues/bellagio.html", "Weekly sheets; paid add-on and re-entry",
     "https://bellagio.mgmresorts.com/en/casino/poker.html", None),
    ("Horseshoe", "venues/horseshoe.html", "Official editorial start times only; no dated schedule",
     "https://www.caesars.com/horseshoe-las-vegas/casino",
     "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    ("MGM Grand", "venues/mgm-grand.html", "No current schedule confirmed",
     "https://mgmgrand.mgmresorts.com/en/casino/poker.html", None),
    ("Resorts World", "venues/resorts-world.html", "No current schedule confirmed",
     "https://www.rwlasvegas.com/gaming/poker-room/", None),
    ("Westgate", "venues/westgate.html", "No current schedule confirmed",
     "https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/casino/poker/", None),
]

# New scoped evidence supplements, rather than redates, earlier findings.
for venue in OTHER_VENUES:
    if "Wynn" in venue["name"]:
        venue.update(checked="2026-11-19",
            status_this_session="The official room page and all three extracted chunks of the daily structures were read November 19. Four recurring daily formats publish entry fees and guarantees; all permit extra spending. Exact-date availability during series remains unverified.",
            provenance="Daily page and structures read first-hand 2026-11-19; earlier WPT readings retain their original dates.")
        venue["earlier_findings"].append(dict(
            text="Daily structures: $200 Monday–Thursday noon, $240 Friday noon rebuy/add-on, $200 weekend noon, $160 nightly 6 p.m. Friday prohibits re-entry but allows rebuys and an add-on; the other three allow re-entry.",
            url="https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf",
            retrieved="2026-11-19"))
for flag in FLAGS:
    if flag["id"] == "F-01":
        flag["impact"] = "The confirmed-only toggle returns zero rows. Rules-silent candidates have a separate group filter and remain unconfirmed."

for flag in FLAGS:
    if flag["id"] == "F-09":
        flag["detail"] += " Update November 19: the linked daily structures have now been read in full and do publish buy-ins and entry rules for all four daily formats."
        flag["impact"] = "All four daily formats permit extra spending and are excluded. Exact-date availability during series remains unverified."
    if flag["id"] == "C-01":
        flag["title"] = "Other rooms publish schedules outside the ranked table"
        flag["detail"] += " Wynn daily structures were read November 19 and are also in a separate excluded table."
        flag["impact"] = "Reviewed extra-spend events are excluded. Neither these exclusions nor incomplete coverage prove that no freezeout exists elsewhere."
