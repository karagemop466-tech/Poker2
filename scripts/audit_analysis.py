#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build data/audit/{rates,flags,questions,suggestions,sources}.json.

These are the parts of the site that are judgement rather than transcription, so each
one is written to be falsifiable: a flag names the document that shows the problem, a
question names what would close it, and a suggestion names the decision it needs.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "audit")
RETRIEVED = "2026-11-17"
SCHED = ("https://www.venetianlasvegas.com/resort/casino/poker/"
         "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
POKER_RATE_PAGE = "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"
VENUE_TC = "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"
RESORT_FEE = "https://www.venetianlasvegas.com/resort/resort-fee.html"
COUNTY = ("https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:"
          "689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf")


def sheet(n):
    return ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/"
            "deepstack/2026/structures/dse_nov_2026-structure_%d.pdf" % n)


# --------------------------------------------------------------------------- rates
RATES = {
    "meta": {
        "as_of": RETRIEVED,
        "rule": ("A rate is a dated observation with a source URL, never a single standing value. "
                 "Every row below is one observation made on the date shown. A row with no price is "
                 "kept, not deleted, so the next observation can be compared against it."),
        "what_a_complete_row_requires": [
            "arrival_date", "departure_date", "nights", "occupancy", "room_type", "rate_plan",
            "nightly_rate", "resort_fee", "tax", "parking", "total_at_checkout",
            "cancellation_deadline", "source_url", "captured_at",
        ],
        "blocking_reason": ("Every official booking engine found (venetianlasvegas.com/book, "
                            "wynnlasvegas.com/book, the MGM property sites, caesars.com) renders "
                            "date-specific prices only inside JavaScript. A static site cannot read "
                            "them, and no request from this workspace returned a price. No dated "
                            "total is therefore claimed. This is the single largest gap on the site."),
    },
    "rates": [
        dict(id="R-01", hotel="The Venetian Resort Las Vegas", hotel_id="HT-01",
             captured=RETRIEVED, basis="published from-price, conditional",
             room_type="Luxury King Suite", occupancy="single/double",
             nightly_rate=119.0, currency="USD",
             conditions=("Poker suite rate. Must book by phone (866.255.8936, code EPOKR25) and play "
                         "6 hours of live cash poker or buy in to a $300+ tournament for each night "
                         "stayed; otherwise the nightly rate reverts to the prevailing rate."),
             includes_fee=False, includes_tax=False,
             excerpt="These rates will start as low as $119 and $209 and can be higher.",
             source_url=POKER_RATE_PAGE, verified=True,
             is_not_a_quote="A floor, not a quote. It is not tied to a date and it is not an "
                            "itemised checkout total."),
        dict(id="R-02", hotel="The Palazzo at The Venetian", hotel_id="HT-02",
             captured=RETRIEVED, basis="published from-price, conditional",
             room_type="Luxury King Suite", occupancy="single/double",
             nightly_rate=209.0, currency="USD",
             conditions="Same poker suite rate terms and qualifying-play requirement as R-01.",
             includes_fee=False, includes_tax=False,
             excerpt="These rates will start as low as $119 and $209 and can be higher.",
             source_url=POKER_RATE_PAGE, verified=True,
             is_not_a_quote="The page prints the two numbers together in the order Venetian, Palazzo, "
                            "without labelling each; the pairing is the site's reading, not a label "
                            "on the page. See flag FD-06.",
             caveat=True),
        dict(id="R-03", hotel="The Venetian / The Palazzo", hotel_id="HT-01",
             captured=RETRIEVED, basis="published resort fee",
             nightly_rate=None, resort_fee=55.0, includes_fee=True, includes_tax=False,
             excerpt="The Venetian Resort has a standard Las Vegas Resort Fee of $55 plus applicable "
                     "tax per night, payable upon check-in.",
             source_url=VENUE_TC, verified=True,
             is_not_a_quote="A fee component, not a room rate."),
        dict(id="R-04", hotel="All properties in the dataset", hotel_id="all",
             captured=RETRIEVED, basis="room tax rate",
             nightly_rate=None, tax_rate=0.1338,
             excerpt="Clark County Room Tax of 13.38% (The Venetian's hotel terms); the Clark County "
                     "licensing guide lists resort-hotel accounts at 13.38%.",
             source_url=VENUE_TC, secondary_url=COUNTY, verified=True,
             is_not_a_quote="A tax rate, not a room rate."),
        dict(id="R-05", hotel="Any property, trip window", hotel_id="all",
             captured=RETRIEVED, basis="dated checkout quote",
             nightly_rate=None, verified=False,
             excerpt="Not captured. The booking engine requires JavaScript.",
             source_url="https://www.venetianlasvegas.com/book",
             is_not_a_quote="The missing row. It stays in the log with a null price so the gap is "
                            "counted instead of hidden."),
    ],
}

# --------------------------------------------------------------------------- flags
FLAGS = [
    dict(id="FD-01", severity="high", area="repo",
         title="A claim of automatic change monitoring that has never run",
         finding=("Four workflows register a schedule (recheck.yml 06:00 UTC, plan-refresh.yml "
                  "06:30 UTC, source-monitor.yml 15:00 UTC, url-check.yml). The Actions API "
                  "returns no scheduled run for any of them, and the two files that would hold "
                  "the results are still placeholders: data/site/checks.json has last_run: null "
                  "and data/source_monitor.json has sha256: null for all 60 URLs."),
         why_it_matters=("On main, 'the site is re-checked daily' describes a configuration, not "
                         "an observation. A reader cannot tell whether any cited value has changed "
                         "since 2026-11-16."),
         evidence="gh run list --workflow=recheck.yml and --workflow=source-monitor.yml return no runs.",
         source_url="https://github.com/karagemop466-tech/Poker2/actions",
         action="This session adds a monitor that records a per-URL status and fails loudly instead of reporting a pass it did not earn."),
    dict(id="FD-02", severity="high", area="repo",
         title="No scheduled workflow can be started from this environment",
         finding=("gh workflow run returns HTTP 403 'Resource not accessible by integration' for "
                  "this repository, so a session cannot dispatch, retry or prove any workflow. "
                  "Only runs triggered by a push are observable."),
         why_it_matters="Any 'we tested the schedule' claim would be unverifiable. None is made here.",
         evidence="gh workflow run plan-refresh.yml --ref main -> HTTP 403.",
         source_url="https://docs.github.com/en/rest/actions/workflows",
         action="Recorded as an environment limitation. The monitor added here is verified by running the same script locally against the real URLs."),
    dict(id="FD-03", severity="high", area="rules",
         title="Nothing in this series is a confirmed single-entry event",
         finding=("All 37 structure sheets have now been read in full. Not one of them prints "
                  "'no re-entry', 'no rebuy' or 'no add-on' for any event. The only entry limit "
                  "any sheet prints is the multi-flight rule: 'Any player who bags chips for Day 2 "
                  "may not play a subsequent flight.' That rule appears on 22 of the 94 rows and it "
                  "restricts a player who has already SURVIVED a flight from buying a second one. "
                  "It is silent on the ordinary case, a player who busts on Day 1A and wants to "
                  "enter Day 1B, which is exactly what a multi-flight event exists to allow. Four "
                  "sheets (4, 10, 12, 21) therefore contradicted themselves in the earlier build: "
                  "the same row was labelled 'explicit: no 2nd entry' and 're-entry allowed'. Those "
                  "four are now recorded as sheet-silent with re-entry allowed."),
         why_it_matters=("The travel brief asks for single-entry tournaments as the main section, so "
                         "this is the load-bearing question of the whole site. The answer is that the "
                         "filter cannot be satisfied from official documents: 72 rows are silent and "
                         "22 rows print only the flight rule. Zero events can be confirmed as "
                         "freezeout. A site that printed 'single entry' on 22 rows would be "
                         "overstating what the sheets say by exactly the amount that matters."),
         evidence=("data/audit/events.json, single_entry and re_entry columns. single_entry is "
                   "'explicit_yes' on 0 rows, 'explicit_no' on 22, 'not_stated' on 72. Every one of "
                   "the 22 explicit_no excerpts quotes the flight rule and no other prohibition. "
                   "No sheet prints an entry-limit clause of any other kind."),
         source_url=sheet(4),
         action=("The site does not label any row single-entry. The tournament page separates rows by "
                 "how strong the evidence is, names the flight rule for what it is, and keeps "
                 "'sheet silent' distinct from 'one entry only'. The toggle the brief asks for is "
                 "present but it filters on published evidence, so it returns nothing rather than "
                 "returning a guess."),
         resolution=("Corrected 2026-11-17 after all 37 sheets were read. Four sheets whose only "
                     "printed limit was the flight rule had been marked explicit_no while also "
                     "carrying re_entry=explicit_yes; they are now not_stated. The claim 'no sheet "
                     "prints an entry limit' is now verified against all 37 rather than 12.")),
    dict(id="FD-04", severity="medium", area="events",
         title="25 of 37 structure sheets were not read, so 46 of 94 rows have no structure data",
         finding=("The official schedule page links 37 distinct structure PDFs. This pass read 12 of "
                  "them, covering 48 of the 94 published rows. The remaining 46 rows carry the "
                  "schedule's date, time, event number, name and sheet link, and nothing else."),
         why_it_matters="Fee, stack, level time and late-registration close for those rows are unknown, so they cannot be compared like-for-like.",
         evidence="data/audit/events.json: structure_read = false on 46 rows; unread sheet numbers listed in meta.sheets_not_read.",
         source_url=SCHED,
         action="Rows stay in the table with blank structural fields and a per-row unverified list. Reading the remaining sheets is question IQ-01."),
    dict(id="FD-05", severity="high", area="hotels",
         title="No dated room rate exists on the site, so 'true cost per night' has no room-rate term",
         finding=("Every official booking engine renders prices only in JavaScript. No request "
                  "returned a checkout total for any property on any date. The only price published "
                  "as text is the Venetian poker-suite 'from' rate ($119 Venetian / $209 Palazzo), "
                  "which is conditional on 6 hours of cash play or a $300+ tournament buy-in per "
                  "night and is not tied to a date."),
         why_it_matters=("A trip total without a room rate is not a trip total. Any figure that "
                         "looked complete would be an estimate, and this site does not publish "
                         "estimates as if they were observations."),
         evidence="data/audit/rates.json R-05; booking URLs render no price server-side.",
         source_url="https://www.venetianlasvegas.com/book",
         action="The calculator computes entries x buy-in exactly, and states the hotel side as a fees-only figure with the room rate explicitly missing."),
    dict(id="FD-06", severity="medium", area="hotels",
         title="The poker-suite page prints two prices without labelling which property each is",
         finding=("The page reads 'These rates will start as low as $119 and $209 and can be higher.' "
                  "It names The Venetian and The Palazzo earlier in the paragraph but does not put "
                  "a number next to a name."),
         why_it_matters="Reading $119 as Venetian and $209 as Palazzo is an ordering assumption, not a quotation.",
         evidence="suite-rates.html, paragraph 1.",
         source_url=POKER_RATE_PAGE,
         action="Recorded as the site's reading in R-02 and marked; the raw sentence is shown next to it."),
    dict(id="FD-07", severity="medium", area="events",
         title="A published guarantee is not always prize money",
         finding=("Six of the twelve sheets read define the guarantee to include bounties: sheet 1 "
                  "($8,000 'prize pool + total bounties'), sheet 11 ($30,000 / $40,000 / $50,000), "
                  "sheet 15 ($15,000), sheet 16 ($75,000) and sheet 34 ($75,000). Sheet 15 rule 10 "
                  "says the $15,000 'consists of the actual prize pool plus the total amount of "
                  "$100 bounties that are awarded'."),
         why_it_matters=("Dividing a bounty-inclusive guarantee by the buy-in produces a bigger "
                         "number than dividing a pure prize-pool guarantee by it. On a single ranked "
                         "list the two would look comparable and would not be."),
         evidence="data/audit/events.json gtd_basis column.",
         source_url=sheet(15),
         action=("Guarantee-per-entry is computed only for rows whose guarantee is pure prize pool; "
                 "bounty-inclusive rows are labelled and kept in a separate section."),
         resolution=("Fixed 2026-11-17. The generator used to compute gtd_ratio_descriptive for "
                     "every row with a guarantee, so 26 bounty-inclusive rows carried a ratio and "
                     "the raw JSON contradicted this flag even though the page's ranking did not. "
                     "The ratio is now emitted only when gtd_basis is exactly 'prize pool': 13 rows "
                     "have a ratio, 26 keep the guarantee with no ratio, and the table prints "
                     "'n/a - bounty GTD' with the reason on hover. verify/verify_events.py fails if "
                     "a ratio ever reappears on a bounty-inclusive guarantee.")),
    dict(id="FD-08", severity="medium", area="walking",
         title="Walking times come from a routing service, not from an official venue page",
         finding=("No casino or poker room publishes a walking time between properties. The matrix "
                  "here was read from Google Maps walking directions on 2026-11-17, address to "
                  "address."),
         why_it_matters=("It is a third-party model's estimate at a point in time, and it measures "
                         "street address to street address: the Venetian poker room is deep inside "
                         "the property, so the real walk from the front door is longer."),
         evidence="data/audit/walking.json basis = third_party_routing on every row.",
         source_url="https://www.google.com/maps/dir/?api=1&travelmode=walking",
         action="Every walking row is labelled third_party_routing with its request URL, and the site does not call it official."),
    dict(id="FD-09", severity="medium", area="hotels",
         title="Four of eleven hotels publish no resort fee on any page that could be read",
         finding=("Caesars Palace (www.caesars.com/caesars-palace/hotel-policy redirects to the "
                  "property home page), Horseshoe, The Cosmopolitan and Westgate have no verified "
                  "resort fee, because no official terms page printing one was reached."),
         why_it_matters="Their true cost per night cannot be compared with the properties whose fee is published.",
         evidence="data/audit/hotels.json fee_verified = false on HT-05, HT-06, HT-07, HT-10.",
         source_url="https://www.caesars.com/caesars-palace",
         action="Fee field left blank with the redirect recorded; the calculator refuses to total those hotels."),
    dict(id="FD-10", severity="low", area="tax",
         title="The county tax document's revision date does not match its URL",
         finding=("The Clark County guide URL contains 'july-2021' but the document's own title line "
                  "reads 'Genl Info Guide for TLEs Sept 2018'. The 13.38% rate is repeated in the "
                  "guide's account listing (e.g. Wynn/Encore 2000013.RES-001) and in The Venetian's "
                  "hotel terms."),
         why_it_matters="The current rate is corroborated twice over, but the county document's age is not what its URL implies.",
         evidence="PDF page 12 account table; title metadata.",
         source_url=COUNTY,
         action="Rate used with the age of the source disclosed."),
    dict(id="FD-11", severity="medium", area="schedule",
         title="There is no 8 AM tournament, so a full day cannot start at 8 AM",
         finding=("The earliest start on the DSE IV schedule is 9:10 AM (a $260 turbo milestone "
                  "satellite on 2026-12-12). The earliest one-day event start is 10:10 AM (the $200 "
                  "RaceDay Stack on 11/19, 11/20, 11/21 and the $600 Seniors events). Most days "
                  "start at 11:10 AM."),
         why_it_matters="A plan built around an 8 AM start describes a schedule that does not exist.",
         evidence="94 transcribed schedule rows; minimum start time 09:10.",
         source_url=SCHED,
         action="The day plan is built from the real start times, and the 8 AM target is answered directly in the questions page."),
    dict(id="FD-12", severity="medium", area="schedule",
         title="Two events on the same day can overlap even when their start times do not",
         finding=("Late registration on the $300 one-day event closes at 4:55 PM and on the $300 "
                  "bounty at 9:40 PM. A player still in the afternoon event cannot enter the 5:10 "
                  "PM event, because registering on time requires being out of the first one."),
         why_it_matters="Start times alone would say 11:10 AM and 5:10 PM do not clash. They can.",
         evidence="sheet 5 late registration; sheet 15 late registration.",
         source_url=sheet(5),
         action="The day plan treats a later event as conditional on the earlier one being exited before the later one's late-registration close."),
    dict(id="FD-13", severity="medium", area="repo",
         title="README.md ships unresolved merge-conflict markers",
         finding="README.md still contains <<<<<<<, ======= and >>>>>>> lines from an unresolved merge.",
         why_it_matters="It is the first file a reader opens, and it presents two contradictory descriptions of the site as if both were current.",
         evidence="grep -n '<<<<<<<' README.md",
         source_url="https://github.com/karagemop466-tech/Poker2/blob/main/README.md",
         action="Left alone here because open PR #43 already owns the file; this session does not edit another session's claimed file."),
    dict(id="FD-14", severity="low", area="hotels",
         title="Wynn states resort fee and occupancy surcharge on an offer-specific terms page",
         finding=("The Wynn page read is titled 'Concours Sip and Savor Experience and Accommodation "
                  "Package 2026'. It states the $55 daily resort fee, the $50 occupancy surcharge, "
                  "the $150/night incidental hold and the prepaid, non-cancellable terms."),
         why_it_matters="Those terms may be package-specific rather than the property default.",
         evidence="wynnlasvegas.com/terms-and-conditions/850257.",
         source_url="https://www.wynnlasvegas.com/terms-and-conditions/850257",
         action="Values used and the page's context disclosed on the hotels page."),
    dict(id="FD-15", severity="high", area="repo",
         title="Three dashboards publish different numbers for the same questions",
         finding=("The repository root, /plan/ and the frozen /docs/, /verified/ and /pages/ trees "
                  "are separate generated sites. The root dashboard says 45 rows are 'sheet silent "
                  "on re-entry'; /plan/ says 30 events are rankable and 10 of 37 sheets were read. "
                  "Both are generated from different datasets."),
         why_it_matters="A reader who lands on the wrong page gets a different answer to 'how many events qualify'.",
         evidence="index.html vs plan/index.html KPI blocks.",
         source_url="https://karagemop466-tech.github.io/Poker2/",
         action="/audit/ states its own numbers from its own dataset and links the other surfaces rather than silently disagreeing with them. Choosing one surface is suggestion SG-01."),
    dict(id="FD-16", severity="high", area="events",
         title="Flights of the same event are not the same tournament",
         finding=("Three events sell several starting flights at different times of day, and the "
                  "flights do not share a structure. Event 26 ($800, $500,000 GTD): sheet 12 gives "
                  "Days A, C and E 40-minute levels, sheet 13 gives Days B and D 30-minute levels, "
                  "and sheet 14 gives Day F 20-minute levels as an explicit Turbo. Event 56 "
                  "($1,100, $500,000 GTD): sheet 35 gives Days A, C and E 40-minute levels, sheet "
                  "36 gives Days B and D 30-minute levels, with late registration running to about "
                  "11:10 PM instead of about 4:55 PM. Event 47 ($2,200, $1,000,000 GTD): sheet 21 "
                  "gives Day 1A 40-minute levels at 10:10 AM, sheet 37 gives Day 1B 30-minute "
                  "levels at 6:10 PM."),
         why_it_matters=("A player comparing these events by buy-in and guarantee is comparing "
                         "numbers that sit on top of different structures. The 5:10 PM flight of "
                         "event 26 costs the same $800 as the 11:10 AM flight and buys 25% less "
                         "time per level. Any ranking or 'value' reading that treats the flights as "
                         "one homogeneous event is wrong in the direction of flattering the evening "
                         "flights. It is also a practical trap: a player planning an 8 AM start "
                         "cannot simply join the same event later at the same structure."),
         evidence=("Level Duration line on sheets 12/13/14, 35/36 and 21/37, all read 2026-11-17. "
                   "Every row of events.json carries the sheet number it came from, so each flight "
                   "shows its own level_min rather than an event-level average."),
         source_url=sheet(13),
         action=("The events table prints the level time per row and never aggregates a multi-flight "
                 "event into one line. The schedule page treats each flight as its own option, so a "
                 "day is planned around the flight that is actually being played."),
         resolution="Recorded 2026-11-17 when the remaining 25 sheets were read."),
    dict(id="FD-17", severity="medium", area="events",
         title="Three events charge a third-party fee that is not a house fee",
         finding=("Sheets 31, 32 and 33 (the LIPS events) print two separate withholdings. Sheet 31 "
                  "and 33: '$80 of the $600 Buy-In is withheld for house fees (Rake + Staff). $10 of "
                  "the $600 Buy In will be withheld as a flat fee for Vegas Connected, INC, DBA "
                  "Ladies International Poker Series (LIPS).' Sheet 32: '$90 ... house fees ... $20 "
                  "... flat fee for Vegas Connected'. The remaining prize pool is $510 of $600 in "
                  "all three cases."),
         why_it_matters=("The site's fee column is defined as money withheld from the buy-in. On "
                         "these three sheets that money goes to two different recipients, and one of "
                         "them is a third-party series operator rather than the house. Reporting "
                         "$80 or $90 alone would understate what is withheld from the prize pool. "
                         "Anyone modelling cost per entry has to compare like with like, and the "
                         "LIPS events cost $90 or $110 to enter in practice."),
         evidence=("Rule 6 on sheets 31, 32 and 33. $80 + $10 + $510 = $600; $90 + $20 + $690 = $800."),
         source_url=sheet(31),
         action=("The fee column records the full amount withheld - $90 on sheets 31 and 33, $110 on "
                 "sheet 32 - and the notes column names the split, so the number is not understated."),
         resolution="Recorded 2026-11-17 when the remaining 25 sheets were read."),
    dict(id="FD-18", severity="medium", area="events",
         title="Three events cost less if you register early, so the buy-in is not one number",
         finding=("Sheets 4, 8, 35 and 36 print a conditional discount. Sheet 4: '$20 off house fees "
                  "on Day 1A if registered before 11:10 a.m. ($580 total instead of $600)'. Sheet 8: "
                  "'PokerAtlas PRO players will receive a twenty ($20) rake discount on their "
                  "initial $200 buy in only, for a total buy in of $180 instead of $200', and 'all "
                  "subsequent buy in's after the initial buy in will be $200'. Sheet 35: '$40 "
                  "discount on house fees for a total buy in of $1,060 instead of $1,100 ... will no "
                  "longer be applied once the event has started and played one hand.' Sheet 36 "
                  "prints the same $40 discount for Day 1B."),
         why_it_matters=("The published buy-in is a maximum, not a price. On event 56 the difference "
                         "is $40, on event 59 $20, and the PokerAtlas discount additionally depends "
                         "on holding a membership and claiming an offer in a phone app at the cage. "
                         "A trip budget built on nominal buy-ins overstates cost, and a cost-per-"
                         "entry ranking built on them understates the discount events' value."),
         evidence="Note 7 on sheet 4; rule 7 on sheet 8; rule 7 on sheets 35 and 36.",
         source_url=sheet(35),
         action=("Buy-in is recorded as the nominal printed figure, which is the upper bound, and "
                 "the discount is stated in the row notes rather than baked into the arithmetic. "
                 "The cost calculator uses the nominal figure and says so."),
         resolution="Recorded 2026-11-17 when the remaining 25 sheets were read."),
    dict(id="FD-19", severity="medium", area="events",
         title="Seven rows guarantee seats, not money, and cannot be costed like the rest",
         finding=("Sheets 19, 24 and 25 cover seven events - 33, 37, 41, 44, 45, 46 and 48 - whose "
                  "prize is direct entry to a named event rather than a cash pool. Sheets 19 and 24 "
                  "print 'Guarantee: 2 Seats'; sheet 25 prints 'Guarantee: 2 Seats' across three "
                  "separate events. Sheet 19's prizes are seats to the $800 LIPS Ladies event 39, "
                  "and sheets 24 and 25's are seats to the $2,200 PokerAtlas Title event 47. All "
                  "three are 'Milestone' satellites: a player who reaches 200,000 chips is paid "
                  "immediately and removed from play."),
         why_it_matters=("These rows have a buy-in and a fee like any other, so a naive sort by "
                         "'guarantee divided by entry fee' would try to divide a seat count by "
                         "dollars. The prize is also conditional on the target event running and "
                         "on the satellite filling its seat allocation, neither of which the sheet "
                         "promises."),
         evidence="Guarantee line and prize rules on sheets 19, 24 and 25.",
         source_url=sheet(19),
         action=("These seven rows are categorised as satellites, excluded from every guarantee-to-"
                 "fee comparison, and shown in their own section with the seat prize named. A seat "
                 "guarantee is never expressed as a dollar figure."),
         resolution="Recorded 2026-11-17 when the remaining 25 sheets were read."),
    dict(id="FD-20", severity="medium", area="events",
         title="Four events are not Hold'em, and two are not one player per seat",
         finding=("Event 20 and event 57 ($300 and $600) are Pot Limit Omaha double-board bomb pots "
                  "played eight-handed, where every player antes every hand and action starts on the "
                  "flop. Event 27 ($600) is BIG O, five-card Omaha hi-lo, also eight-handed. Event "
                  "35 ($600) is a tag-team event where a team rotates players at the start of every "
                  "level and a team that fails to switch is disqualified. Event 24 and event 32 are "
                  "Seniors events, 50+ only. Event 39 is open to female players only, and events 19, "
                  "24 and 25's satellites are restricted to female or to 50+ players."),
         why_it_matters=("The brief asks for tournaments to play, and a Hold'em cash-game specialist "
                         "may not want a bomb pot or a five-card split game at all. Two of these "
                         "rows are not even buyable by a solo player, and four are not buyable at all "
                         "by a player who does not meet an age or gender condition. Sorting the whole "
                         "schedule by price puts events a reader cannot enter next to ones they can."),
         evidence=("Game description and rules 2, 7, 8 and 10 on sheets 22 and 23; sheet 28; rule 8 "
                   "on sheet 31; rules 2 on sheets 17, 20, 32 and 33; rule 2 on items 19, 24 and 25."),
         source_url=sheet(22),
         action=("Every row carries its game and any eligibility condition on the tournament page, "
                 "and the non-Hold'em and team rows are kept out of the like-for-like comparison. "
                 "Eligibility is quoted, not paraphrased."),
         resolution="Recorded 2026-11-17 when the remaining 25 sheets were read."),
    dict(id="FD-21", severity="medium", area="events",
         title="Payout percentage is not uniform, and a figure that looks like one is not one",
         finding=("Most sheets print 'pays 12.5% of the field', but sheet 17 (Seniors, $600) prints "
                  "15% and sheet 20 (Seniors, $1,100) prints nothing. Separately, on the flight "
                  "sheets the 12.5% figure in the rules text is the FLIGHT-STOP rule - 'each starting "
                  "flight will play until we are down to approximately 12.5% of the field remaining' "
                  "- not a payout rule. Sheets 2, 3, 4, 12, 13, 20, 21, 35, 36, 37 and 32 print the "
                  "stop rule and no payout percentage at all."),
         why_it_matters=("Reading the stop rule as a payout rule would publish a 12.5% payout figure "
                         "for 11 sheets that never printed one. The distinction also changes the "
                         "comparison: a 15% event pays more places than a 12.5% event at the same "
                         "field size, which is a real difference in variance for a player deciding "
                         "what to enter."),
         evidence=("pays_pct is 12.5 on 46 rows, 15 on 2 rows and blank on 46 rows. The 46 blanks "
                   "are sheets that either print no percentage or print only the flight-stop rule."),
         source_url=sheet(17),
         action=("pays_pct is filled only where a sheet prints a payout percentage. The 46 blank "
                 "rows say so, and the flight-stop rule is quoted in the row notes where it exists "
                 "instead of being promoted into the payout column."),
         resolution="Recorded 2026-11-17 when the remaining 25 sheets were read."),
]

# ----------------------------------------------------------------------- questions
QUESTIONS = [
    dict(id="IQ-01", question="What is printed on the 37 structure sheets?",
         answer=("All 37 have now been read in full, 2026-11-17, and every one of the 94 schedule "
                 "rows carries its fee, prize-pool split, starting stack, level time and "
                 "late-registration close. The sheets are consistent on one point worth stating: "
                 "$fee + $prize pool always equals the printed buy-in, on all 94 rows, with no "
                 "exceptions. What they do not contain is any entry limit (FD-03) or any payout "
                 "percentage on 46 rows (FD-21)."),
         status="closed",
         how_to_close="Read each PDF linked from the official schedule page.",
         can_be_closed_here="Closed here: every sheet is a public PDF.",
         blocks="Nothing now. It gated the fee, stack and late-registration columns.",
         source_url=sheet(2),
         resolution="Closed 2026-11-17. This was the largest open gap in the earlier build."),
    dict(id="IQ-02", question="What is the actual checkout total for specific dates?",
         why=("No dated room rate exists. The hotel side of the trip cost is unknown, so total cost "
              "cannot be ranked between properties."),
         how_to_close=("Enter the dates on the official booking engine and record the itemised "
                       "checkout total, or call the poker rate line (866.255.8936, code EPOKR25) "
                       "and ask for the total including resort fee and tax."),
         can_be_closed_here="no - requires a JavaScript booking engine or a phone call",
         source_url="https://www.venetianlasvegas.com/book", status="open",
         blocks="Any statement of true cost per night"),
    dict(id="IQ-03", question="Does any Venetian one-day event actually forbid re-entry?",
         answer=("No. With all 37 sheets read, none prints a freezeout, no-rebuy or no-add-on rule. "
                 "The only entry restriction in the series is the multi-flight rule, which stops a "
                 "player who has already bagged chips from buying a later flight - not the same "
                 "thing, and it does not apply to one-day events at all in the way it applies to "
                 "flights. Four sheets had previously been recorded as forbidding a second entry on "
                 "that basis; they have been corrected to sheet-silent."),
         status="closed",
         how_to_close="Read the 25 remaining structure sheets.",
         can_be_closed_here="Closed here: every sheet is a public PDF.",
         blocks="The single-entry claim the brief asks for. It cannot be satisfied.",
         source_url=sheet(5),
         resolution=("Closed 2026-11-17 with a negative answer. The practical consequence is that "
                     "the site cannot claim any event is single-entry, which is why the tournament "
                     "page separates rows by evidence strength instead.")),
    dict(id="IQ-04", question="Is the resort fee taxed at 13.38%, and is parking taxed?",
         why=("The properties say 'plus applicable tax' without printing the arithmetic. The "
              "calculator applies the room tax to the resort fee; that is a computation, not a "
              "quotation."),
         how_to_close="Read the tax lines on a real checkout confirmation for one night.",
         can_be_closed_here="no - needs a checkout confirmation",
         source_url=VENUE_TC, status="open", blocks="Exact fees-only nightly figure"),
    dict(id="IQ-05", question="Which guarantee figures include bounties?",
         answer=("32 of the 94 rows. The sheets print the basis explicitly: sheets 1, 8, 11, 15, 16, "
                 "26, 27, 30 and 33 define the guarantee as prize pool plus total bounties, and the "
                 "wording on each names the actual composition - for example sheet 15's 'the actual "
                 "prize pool plus the total amount of $100 bounties that are awarded'. The other 51 "
                 "dollar guarantees are pure prize pool, and 7 rows guarantee seats instead of money."),
         status="closed",
         how_to_close="Read the guarantee rules on all 37 sheets and classify each.",
         can_be_closed_here="Closed here: every sheet is a public PDF.",
         blocks="The like-for-like guarantee comparison.",
         source_url=sheet(15),
         resolution=("Closed 2026-11-17. The 32 bounty-inclusive rows carry their guarantee but no "
                     "guarantee-to-fee ratio, and the table prints 'n/a - bounty GTD' in that cell.")),
    dict(id="IQ-06", question="Can the trip actually be filled from 8 AM to night?",
         why=("No event starts before 9:10 AM and the earliest one-day event is 10:10 AM, so part "
              "of the morning is free by construction."),
         how_to_close="Accept a 10:10 AM start, or add a second venue with an earlier daily event and verify its schedule.",
         can_be_closed_here="partly - the Venetian answer is no",
         source_url=SCHED, status="answered: no 8 AM event exists", blocks="An 8 AM itinerary"),
    dict(id="IQ-07", question="What is the real walk from the hotel lobby to the poker room?",
         why="Measured times are street address to street address.",
         how_to_close="Re-route to 'The Venetian Poker Room' as the destination rather than the street address, and compare.",
         can_be_closed_here="yes", source_url="https://www.google.com/maps", status="open",
         blocks="Tight connections between the hotel and a 10:10 AM start"),
    dict(id="IQ-08", question="Does any other Strip room run a daily tournament earlier than 10:10 AM?",
         why=("The full-day goal needs an earlier start, and other rooms run recurring dailies whose "
              "official schedules were not read in this pass."),
         how_to_close="Read the daily schedule pages of the other Strip poker rooms and transcribe them the same way.",
         can_be_closed_here="yes - sources exist, not read yet",
         source_url="https://www.wynnlasvegas.com/casino/poker", status="open",
         blocks="A plan that starts before 10 AM"),
    dict(id="IQ-09", question="What is the cancellation deadline and deposit for each property?",
         why="It decides how long the trip can stay flexible and whether a prepaid rate is safe.",
         how_to_close="Recorded for Bellagio, ARIA, MGM Grand (72 hours) and Wynn (prepaid, non-refundable); missing for Caesars, Horseshoe, Cosmopolitan, Westgate, South Point.",
         can_be_closed_here="partly", source_url=VENUE_TC, status="partly answered",
         blocks="Choosing a refundable vs prepaid rate"),
    dict(id="IQ-10", question="How many players enter each event?",
         why=("Guarantee-per-entry is a descriptive ratio. Whether a guarantee is likely to be met, "
              "and therefore whether the ratio means anything, depends on field size, which no "
              "organiser publishes in advance."),
         how_to_close="Use historical results for the same event in earlier series if the venue publishes them.",
         can_be_closed_here="partly - results pages exist",
         source_url=SCHED, status="open", blocks="Any statement about value"),
    dict(id="IQ-11", question="Is the Venetian poker-suite rate available on the chosen dates?",
         why=("The $119/$209 figures are 'from' prices subject to occupancy and blackout dates; "
              "availability is unknown."),
         how_to_close="Call the poker rate line with the dates.",
         can_be_closed_here="no - needs a phone call", source_url=POKER_RATE_PAGE, status="open",
         blocks="Using the poker rate in the cost model"),
    dict(id="IQ-12", question="Which surface of this repository is the one to keep?",
         why="Root, /plan/ and the frozen trees disagree on headline counts.",
         how_to_close="Choose one surface; the rest are archived. See suggestion SG-01.",
         can_be_closed_here="needs a decision", source_url="https://karagemop466-tech.github.io/Poker2/",
         status="open", blocks="Any single set of published numbers"),
]

# --------------------------------------------------------------------- suggestions
SUGGESTIONS = [
    dict(id="SG-01", title="Keep one surface, archive the rest",
         problem="Four generated dashboards publish different counts for the same questions.",
         options="A) keep /audit/ and redirect root, /plan/, /docs/, /verified/, /pages/ · B) keep root and archive /audit/ · C) leave all four and add a banner to each",
         trade_off="A is clearest for a reader and the most work; C is free and keeps the confusion.",
         needs_decision="Yes - this is a product decision, not a data one.", effort="medium",
         recommendation="A"),
    dict(id="SG-02", title="Read the remaining 25 structure sheets",
         problem="46 of 94 rows have no fee, stack or late-registration close.",
         options="A) transcribe all 25 · B) transcribe only the 14 one-day events · C) leave them blank",
         trade_off="Each sheet is one document and about ten numbers; the only cost is time.",
         needs_decision="No - it is mechanical.", effort="2-3 hours",
         recommendation="A"),
    dict(id="SG-03", title="Add a targeted, dated rate capture instead of a general one",
         problem="No booking engine returns a price to a static site.",
         options=("A) a scheduled job against the one official JSON price endpoint, storing only the itemised total · "
                  "B) a monthly manual capture of a single date range into rates.json · "
                  "C) keep rates blank and link the engine"),
         trade_off="A is the only automatic option but depends on an endpoint the property can change without notice; B is honest and slow.",
         needs_decision="Pick A or B; C is the current state.", effort="A: 1 day · B: 15 min/month",
         recommendation="B until A is proven stable"),
    dict(id="SG-04", title="Ask the poker room for a written entry-rule schedule",
         problem="No sheet prints an entry limit, so 'single entry' cannot be published.",
         options="A) email the poker room and paste the reply into the site with its date · B) keep the three-state label · C) treat silence as single entry",
         trade_off="C is the only option that is not honest.",
         needs_decision="Send the email (A) or keep the current label (B).", effort="one email",
         recommendation="A, fall back to B"),
    dict(id="SG-05", title="Score hotels on published facts only, and show the blanks",
         problem="Quality is often scored with star ratings that no official page publishes here.",
         options="A) score on published fee, tax, walk time and cancellation only · B) add a third-party star rating, clearly labelled · C) no score",
         trade_off="B introduces a third-party judgement; A measures what is verifiable.",
         needs_decision="Whether a third-party quality signal is acceptable on an official-source site.",
         effort="low", recommendation="A"),
    dict(id="SG-06", title="Make the change monitor write a real status per URL",
         problem="The existing monitor files are placeholders after a day of scheduled runs.",
         options="A) per-URL status with HTTP code, hash and tracked values, failing loudly · B) hash only · C) none",
         trade_off="A costs one page and answers 'has anything moved since I last looked'.",
         needs_decision="No.", effort="done in this session for /audit/ sources",
         recommendation="A"),
    dict(id="SG-07", title="Show the ratio as a range, not a point",
         problem="Guarantee / entry fee is printed to two decimals, which implies precision that a floor does not have.",
         options="A) print the ratio plus 'guarantee is a floor' inline · B) round to a whole number · C) drop the ratio",
         trade_off="A keeps the signal and removes the false precision.",
         needs_decision="No.", effort="low", recommendation="A"),
    dict(id="SG-08", title="Publish the day plan as a decision tree, not a timetable",
         problem="A timetable implies the player will be free at 5 PM; the first event usually will not be over.",
         options="A) each day: primary + 'if you bust before HH:MM, enter X' · B) fixed timetable · C) list only",
         trade_off="A matches how a tournament day actually works.",
         needs_decision="No.", effort="low", recommendation="A (implemented on the schedule page)"),
    dict(id="SG-09", title="Add a 'what would change my mind' line to every flag",
         problem="A flag that only says 'unverified' does not tell a reader how much it matters.",
         options="A) each flag names the decision it blocks · B) severity only · C) neither",
         trade_off="A is what makes the flag list usable.", needs_decision="No.", effort="low",
         recommendation="A (implemented)"),
    dict(id="SG-10", title="Keep the COORDINATION.md board as the source of truth for ownership",
         problem="Three sessions regenerated the same root files and produced four dashboards.",
         options="A) hard file ownership enforced by CI · B) advisory board only (current) · C) one generator for everything",
         trade_off="A prevents the four-dashboard problem; C is the long-run answer.",
         needs_decision="Yes.", effort="A: 1 hour · C: 1 day", recommendation="A now, C next"),
]


def main():
    os.makedirs(D, exist_ok=True)

    def dump(name, obj):
        with open(os.path.join(D, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1, ensure_ascii=False)
            fh.write("\n")

    dump("rates.json", RATES)
    dump("flags.json", {"meta": {"as_of": RETRIEVED, "count": len(FLAGS)}, "flags": FLAGS})
    dump("questions.json", {"meta": {"as_of": RETRIEVED, "count": len(QUESTIONS)}, "questions": QUESTIONS})
    dump("suggestions.json", {"meta": {"as_of": RETRIEVED, "count": len(SUGGESTIONS)}, "suggestions": SUGGESTIONS})
    print("rates:", len(RATES["rates"]), "| flags:", len(FLAGS),
          "| questions:", len(QUESTIONS), "| suggestions:", len(SUGGESTIONS))


if __name__ == "__main__":
    main()
