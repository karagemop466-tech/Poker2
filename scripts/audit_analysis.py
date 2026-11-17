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
         title="Silence on a structure sheet is not a single-entry rule",
         finding=("None of the 12 Venetian structure sheets read in this pass prints an entry limit "
                  "for a one-day event. Each prints its fee split, level time, late-registration "
                  "close and payout percentage, and none prints 'no re-entry', 'no rebuy' or "
                  "'no add-on'. Six sheets print a flight restriction instead: 'Any player who bags "
                  "chips for Day 2 may not play a subsequent flight'."),
         why_it_matters=("A row labelled 'single entry' on that basis would be an inference. The "
                         "honest label is 'sheet silent', and the decision to treat silence as a "
                         "freezeout has to be made explicitly, in writing, by the player or by the "
                         "venue."),
         evidence="sheets 1, 5, 7, 11, 15, 16, 18, 34 read in full; none prints an entry-limit clause.",
         source_url=sheet(5),
         action="Every row carries single_entry = not_stated / explicit_no / explicit_yes, and the site never upgrades silence."),
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
]

# ----------------------------------------------------------------------- questions
QUESTIONS = [
    dict(id="IQ-01", question="What is printed on the 25 structure sheets that were not read?",
         why=("46 of 94 published rows have no fee, stack, level time or late-registration close. "
              "Without them those rows cannot be compared with the 48 that do."),
         how_to_close="Open each sheet URL and transcribe the same fields into data/audit/sheets.py.",
         can_be_closed_here="yes - it is 25 more documents, not a missing source",
         source_url=SCHED, status="open", blocks="Like-for-like comparison of 46 rows"),
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
         why=("Twelve sheets were read in full and none prints an entry limit. 'Single entry' is "
              "currently an assumption about silence."),
         how_to_close="Ask the poker room in writing (lv_cas_poker@venetianlasvegas.com, 702.414.7657) whether a one-day event permits a second entry.",
         can_be_closed_here="no - needs the venue to answer",
         source_url=POKER_RATE_PAGE, status="open", blocks="Labelling any event 'single entry'"),
    dict(id="IQ-04", question="Is the resort fee taxed at 13.38%, and is parking taxed?",
         why=("The properties say 'plus applicable tax' without printing the arithmetic. The "
              "calculator applies the room tax to the resort fee; that is a computation, not a "
              "quotation."),
         how_to_close="Read the tax lines on a real checkout confirmation for one night.",
         can_be_closed_here="no - needs a checkout confirmation",
         source_url=VENUE_TC, status="open", blocks="Exact fees-only nightly figure"),
    dict(id="IQ-05", question="Which guarantee figures include bounties?",
         why="Guarantee-per-entry is only comparable across rows when the guarantee is pure prize pool.",
         how_to_close="Already answered for the 12 sheets read (gtd_basis column); the remaining 25 sheets need the same line checked.",
         can_be_closed_here="yes for the read set",
         source_url=sheet(15), status="partly answered", blocks="Cross-row ratio comparison"),
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
