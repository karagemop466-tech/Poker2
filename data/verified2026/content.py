# Narrative content: other venues, flags, questions, suggestions, summary.
# Every claim here is tied to an official URL. Where a value could not be confirmed it is
# listed as a flag, not filled in.

ROOM_TAX = dict(
    value=13.38,
    text="13.38% transient lodging tax",
    source="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf",
    corroboration=("The official Venetian hotel terms state 'Clark County Room Tax of 13.38%' "
                   "(https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html)."),
    retrieved="2026-11-16",
    note="Read by an earlier session from the county's own published guide. Not re-read in this session.",
)

# Other Strip-area poker rooms. `status_this_session` records what happened when this session
# tried to reach the official page on 2026-11-17.
OTHER_VENUES = [
    dict(
        name="Wynn / Encore",
        poker_room="Wynn Poker Room (WPT World Championship host room)",
        status_this_session=("The official Wynn poker-room URL returned 'IT SEEMS THIS PAGE HAS CHECKED OUT' "
                             "(a not-found page) when requested on 2026-11-17. No dated schedule could be read."),
        url="https://www.wynnlasvegas.com/casino/poker-room",
        earlier_findings=[
            dict(text="Wynn's official WPT World Championship structures PDF prints 'Unlimited re-entry until the start of level 9' for the $600 Turbo, the $600 mixed-game events, and the $400 / $1,100 PLO events.",
                 url="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf",
                 retrieved="2026-11-16"),
            dict(text="The same PDF prints the buy-in splits, e.g. $600 NLH $400K GTD is $510 prize pool + $65 house fee + $25 staff gratuity.",
                 url="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf",
                 retrieved="2026-11-16"),
        ],
        verdict="Excluded from the single-entry ranking: the official structure sheet states unlimited re-entry.",
        provenance="cited from an earlier session's reading, not re-read on 2026-11-17 (the page is currently unavailable)",
    ),
    dict(
        name="Horseshoe Las Vegas",
        poker_room="Hall of Fame Poker Room",
        status_this_session=("The official poker sub-page redirects to the general casino page. That page confirms a "
                             "poker room with 20 tables and '6 exciting tournament times daily' but publishes no "
                             "buy-ins, guarantees, dates or structure sheet."),
        url="https://www.caesars.com/horseshoe-las-vegas/casino",
        earlier_findings=[
            dict(text="Caesars' own editorial page publishes the six daily start times: 9:00 AM, 11:00 AM, 2:00 PM, 5:00 PM, 8:00 PM and 11:00 PM.",
                 url="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
                 retrieved="2026-11-16"),
        ],
        verdict="Start times only. No buy-in, guarantee, structure or entry rule is officially published, so no row can be ranked.",
        provenance="times cited from an earlier session's reading; the page was re-requested this session and the poker sub-page no longer resolves",
    ),
    dict(
        name="Caesars Palace",
        poker_room="Caesars Palace Poker Room",
        status_this_session="Not re-read in this session.",
        url="https://www.caesars.com/caesars-palace/casino",
        earlier_findings=[
            dict(text="Caesars' corporate disclaimer publishes only a resort-fee range: 'a daily resort fee between $45-$50 plus applicable tax. Resort fees are waived for Diamond and Seven Stars.' No single property value is published.",
                 url="https://www.caesars.com/corporate/disclaimer",
                 retrieved="2026-11-16"),
        ],
        verdict="No tournament schedule or structure sheet published on the official page.",
        provenance="cited from an earlier session's reading",
    ),
    dict(
        name="Bellagio",
        poker_room="Bellagio Poker Room",
        status_this_session="Not re-read in this session.",
        url="https://bellagio.mgmresorts.com/en/casino/poker.html",
        earlier_findings=[
            dict(text="The official Sunday $400 H.O.R.S.E. structure sheet states: 'Players may buy-in and re-enter through the end of level 8 (Including Break)' and that a voluntary $25 staff gratuity at registration grants an additional 15,000 starting chips.",
                 url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/mgm-bellagio-poker-sundays-$400-horse.pdf",
                 retrieved="2026-11-16"),
            dict(text="The official Saturday NLH structure sheet contradicts itself ($1,100 heading vs $1,000 link label vs $600 rule text) and no value from it is used.",
                 url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf",
                 retrieved="2026-11-16"),
        ],
        verdict="Excluded from the single-entry ranking: re-entry plus a paid extra-chip gratuity on the verified sheet.",
        provenance="cited from an earlier session's reading",
    ),
    dict(
        name="MGM Grand",
        poker_room="MGM Grand Poker Room",
        status_this_session="Not re-read in this session.",
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
         title="Wynn's poker page is currently unavailable",
         detail=("https://www.wynnlasvegas.com/casino/poker-room returned a not-found page on 2026-11-17. Wynn "
                 "findings on this site are carried from an earlier session's reading of the official WPT "
                 "structures PDF on 2026-11-16 and are labelled as such."),
         impact="Wynn rows are marked 'cited, not re-read' and are not presented as current.",
         source="https://www.wynnlasvegas.com/casino/poker-room"),
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
    dict(id="X-02", area="Official page defect",
         title="The Venetian series overview still labels an ended series as 'Current Series'",
         detail=("The DeepStack overview page shows 'Current Series: WPT Fall Festival, October 28 - November 15, "
                 "2026' even though today is 2026-11-17 and the live series is DeepStack Extravaganza IV "
                 "(Nov 16 - Dec 23, 2026)."),
         impact="Do not rely on that page's 'Current Series' label; use the dated event page and schedule PDF.",
         source="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"),
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
         blocks="Both entering any Venetian event and holding the $119 poker rate.",
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

SUMMARY_HEADLINE = ("No Strip poker room publishes a single-entry rule. The Venetian is the only room "
                   "that publishes enough to rank line by line. Silence on re-entry is recorded as "
                   "silence, never as a promise.")
