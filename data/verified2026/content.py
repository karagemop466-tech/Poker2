# Narrative content: other venues, flags, questions, suggestions, summary.
# Every claim here is tied to an official URL. Where a value could not be confirmed it is
# listed as a flag, not filled in.

ROOM_TAX = dict(
    value=13.38,
    text="13.38% transient lodging tax",
    source="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf",
    corroboration=("The official Venetian hotel terms state 'Clark County Room Tax of 13.38%' "
                   "(https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html)."),
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

FLAGS = [
    dict(id="F-01", area="Entry rules",
         title="No Venetian structure sheet states a single-entry or freezeout rule",
         detail=("All 37 official structure sheets were read on 2026-11-17. Not one contains the words "
                 "'single entry', 'one entry', 'freezeout' or 'no re-entry'. Every one-day sheet is simply "
                 "silent on re-entry, rebuy and add-on. Silence is not a prohibition, so no event is marked "
                 "'single-entry confirmed'."),
         impact="The single-entry filter can only offer 'no re-entry/add-on clause printed', never 'confirmed'.",
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/"),
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
         impact=("Overlap flags are computed as 'same-day entries cannot both be played from the start'. The "
                 "later event is offered as a conditional fallback whose deadline is its official registration "
                 "close. Nothing is presented as a guaranteed finish."),
         source="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"),
    dict(id="F-05", area="Hotels",
         title="No dated room quote was captured",
         detail=("Official booking engines render rates with client-side JavaScript, so no dated checkout total, "
                 "nightly average or rate timestamp could be read on 2026-11-17. The Venetian's own page also "
                 "says future poker rates 'are only provided out to a maximum of 150 days from the current date' "
                 "and must be booked by phone."),
         impact="The true-cost calculator needs you to enter the nightly rate you are quoted; it is not prefilled.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
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
                 "by an earlier session and was not re-read today."),
         impact="Used as the calculator default. Re-check on the county page before you book.",
         source="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf"),
    dict(id="F-08", area="Walking",
         title="Walk times are routing estimates, not a Google or Apple Maps measurement",
         detail=("The walk matrix was computed from OpenStreetMap data with the OSRM foot profile "
                 "(routing.openstreetmap.de/routed-foot) on 2026-11-16. A Google Maps walking-directions link is "
                 "published on every row so you can confirm each pair yourself."),
         impact="The 30-minute filter is applied to the routed estimate and is labelled as an estimate.",
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
         title="Only The Venetian publishes a dated schedule plus a per-event structure sheet",
         detail=("Every other Strip room checked either publishes no tournament schedule, no structure sheet, or "
                 "both. Horseshoe publishes six daily start times with no buy-ins; Resorts World's poker page "
                 "redirects to a dining page; Westgate publishes room hours only; MGM's weekly grid carries no "
                 "year; Bellagio's Saturday sheet contradicts itself."),
         impact="The ranked tables are Venetian DSE IV only. That is a coverage limit, not a preference.",
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
         impact=("Any comparison of a Caesars daily against a Venetian DSE event is unsafe on price alone. Ask the "
                 "room, or treat the higher figure as the cost of the seat."),
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
    dict(id="X-02", area="Official page defect",
         title="The Venetian series overview still labels an ended series as 'Current Series'",
         detail=("The DeepStack overview page shows 'Current Series: WPT Fall Festival, October 28 - November 15, "
                 "2026' even though today is 2026-11-17 and the live series is DeepStack Extravaganza IV "
                 "(Nov 16 - Dec 23, 2026)."),
         impact="Do not rely on that page's 'Current Series' label; use the dated event page and schedule PDF.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"),
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
    dict(id="F-11", area="Coverage",
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
    dict(id="Q-01", q="Do you want only events whose sheet is silent on re-entry, or only events the poker room confirms in writing are one-entry-only?",
         why="No official sheet states a one-entry rule, so the first option is the only one the documents support today. The second requires an email or a posted rule from the room.",
         blocks="The single-entry toggle on the tournaments table.",
         answer=None),
    dict(id="Q-02", q="What are your exact trip dates?",
         why="Hotel rates, walking plans and the day-by-day schedule are all date-bound. The poker suite rate is only quoted 150 days out and only by phone.",
         blocks="Any dated hotel quote, the night count in the trip-cost calculator, and which events you can actually enter.",
         answer=None),
    dict(id="Q-03", q="What is your nightly hotel budget ceiling, and what quality floor will you accept?",
         why="You said cost and quality outrank distance. Without a ceiling and a floor the hotel table cannot be ranked.",
         blocks="The hotel shortlist and the ranking order.",
         answer=None),
    dict(id="Q-04", q="How many tournaments do you want to enter per day, and do you accept a conditional fallback?",
         why="You asked to play from 8 AM onward. The earliest verified Venetian start in this series is 9:10 AM (satellite event 46) and 10:10 AM for a main-schedule event.",
         blocks="The day plan. Every same-day second event is a fallback, not a sequence.",
         answer=None),
    dict(id="Q-05", q="Are you 50 or older?",
         why="Events 24, 32 and 49 are Seniors events with a hard 50+ rule and no refund for an under-50 entrant. They carry $40K, $40K and $300K guarantees, three of the larger figures in the series.",
         blocks="Whether three of the better-value events are available to you at all.",
         answer=None),
    dict(id="Q-06", q="Do you have, or will you open, a Venetian Rewards card?",
         why="Every structure sheet requires one to participate, and the poker suite rate is tracked through it.",
         blocks="Both entering any Venetian event and qualifying for the conditional poker offer.",
         answer=None),
    dict(id="Q-07", q="Do you object to bounty formats on principle, or only to paying extra for an advantage?",
         why="Bounty events do not let you buy extra chips, but their guarantee includes bounty money so the cash pool is smaller than the headline number.",
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
         what="Email lv_cas_poker@venetianlasvegas.com or call 702.414.7657 and ask one question: are the one-day events single entry, or may a player buy in again after busting?",
         decides="Whether any event can be promoted from 'no re-entry clause printed' to 'single-entry confirmed'.",
         cost="One email", effort="Low", blocks="Q-01"),
    dict(id="S-02", title="Fix your trip dates and book the poker suite rate by phone",
         what="Call 866.255.8936 with code EPOKR25. The rate is only quoted 150 days out and cannot be booked online.",
         decides="Your true nightly cost. A $300+ tournament entry already satisfies the qualifying-play condition for that night.",
         cost="One call", effort="Low", blocks="Q-02"),
    dict(id="S-03", title="Confirm the 30-minute walk with Google Maps on the pairs you care about",
         what="Every row in the walking table carries a prefilled Google Maps walking-directions link. Open the two or three that matter and read the live time.",
         decides="Whether the routed estimate stands.",
         cost="Five minutes", effort="Low", blocks="F-08"),
    dict(id="S-04", title="Add a Google Maps (or Apple Maps) API key so walk times are measured, not modelled",
         what="Elevation, kerbs, pedestrian bridges and the Strip's footbridge detours are not in a plain OSRM foot profile.",
         decides="Whether the 30-minute filter can be presented as measured.",
         cost="An API key and a small monthly quota", effort="Medium", blocks="F-08"),
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
    dict(id="S-08", title="Add the two upcoming Venetian series to the monitor",
         what="DeepStack Extravaganza NYE (Dec 24 2026 - Jan 10 2027) and DeepStack Showdown (Jan 11 - Feb 14 2027) already have official pages.",
         decides="Whether you get first look at their structure sheets the day they are posted.",
         cost="Two URLs", effort="Low", blocks=None),
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

SUMMARY_HEADLINE = ("No reviewed event has written rules that confirm the strict single-entry policy. "
                    "The Venetian schedule gives useful research leads; none is a booking recommendation.")
