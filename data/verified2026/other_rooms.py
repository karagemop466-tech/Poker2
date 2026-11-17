# Official tournament schedules published by two further Strip poker rooms.
#
# Everything here was read directly from the room's own official document on 2026-11-17 by
# session arena/7cc9ee65-poker2. Nothing is inferred and nothing is carried over from a
# third-party listing. Where a figure is not printed on the official document it stays None
# and is listed on the Flagged for review page.
#
# These rows are deliberately NOT merged into the Venetian event table and NOT ranked against
# it: every event below is a re-entry or add-on event on the face of its own sheet, which is
# exactly the class the brief asks to keep in a separate section.

RETRIEVED = "2026-11-17"

CAESARS_SCHEDULE = dict(
    room="Caesars Palace",
    room_page="https://www.caesars.com/caesars-palace/casino",
    source=("https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/"
            "clv-poker-daily-nlh-tournament-flyer-2026.pdf"),
    title="Daily No-Limit Texas Hold'em Tournament Schedule",
    retrieved=RETRIEVED,
    cadence="Daily (every day of the week)",
    # (start, buy_in, add_on, add_on_chips, chips, level_minutes, guarantee,
    #  to_prize_pool, house_fee)
    rows=[
        dict(start="10:00 AM", buy_in=100, add_on=50, add_on_chips=15000, chips=20000,
             level_min=20, guarantee=1000, to_pool=70, house_fee=30),
        dict(start="2:00 PM", buy_in=160, add_on=50, add_on_chips=15000, chips=20000,
             level_min=20, guarantee=1000, to_pool=115, house_fee=45),
        dict(start="6:00 PM", buy_in=100, add_on=50, add_on_chips=15000, chips=20000,
             level_min=20, guarantee=1000, to_pool=70, house_fee=30),
        dict(start="9:00 PM", buy_in=160, add_on=50, add_on_chips=15000, chips=20000,
             level_min=20, guarantee=1000, to_pool=115, house_fee=45),
    ],
    quotes=[
        ("Add-on",
         "\u201cAll Tournaments feature a $50 add-on for 15,000 tournament chips that can only be "
         "taken at the first break. Registration will close at the start of level seven. All "
         "tournaments will have a 10-minute break every six levels.\u201d"),
        ("Re-entry",
         "\u201c3. Participants may only register themselves, but may re-enter, by paying the entry "
         "fee, upon elimination within the first break of play.\u201d"),
        ("Registration",
         "\u201c1. Sign-ups start one hour before the scheduled start of the event. 2. Registration "
         "is open until the start of level seven.\u201d"),
        ("Buy-in split ($100)",
         "\u201c6. Of the $100 buy in, $70 goes to the prize pool and $30 is held by Caesars Palace "
         "as a maintenance fee.\u201d"),
        ("Buy-in split ($160)",
         "\u201c7. Of the $160 buy in, $115 goes to the prize pool and $45 is held by Caesars "
         "Palace as a maintenance fee.\u201d"),
        ("Add-on split",
         "\u201c8. Of the $50 add-on, $45 goes to the prize pool and $5 is held by Caesars Palace "
         "as a maintenance fee.\u201d"),
        ("Minimum field",
         "\u201c26. Must have at least 6 players to start a tournament. If a tournament does not "
         "have at least 6 players at the scheduled start time the tournament will be canceled, "
         "and refunds will be issued\u201d"),
        ("Chops",
         "\u201c27. Prize pool may not be chopped until the end of registration.\u201d"),
    ],
    # What the official document does NOT print.
    gaps=[
        "No end time is printed for any of the four events, so no sequence can be promised.",
        "No single-entry, freezeout or no-re-entry clause is printed; rule 3 expressly allows re-entry.",
        "The guarantee is printed as a flat $1,000 for all four events with no field-size condition.",
        "The flyer is titled for 2026 but prints no series dates, so it is read as a standing daily "
        "schedule rather than a dated calendar.",
    ],
    verdict=("Not single-entry. The official flyer prints a $50 add-on and expressly permits "
             "re-entry, so these events sit in the spending-more-money section, not the "
             "single-entry ranking."),
    notes=[
        ("Two official Caesars documents disagree on the buy-in. This table transcribes the daily "
         "flyer PDF ($100 at 10 AM and 6 PM, $160 at 2 PM and 9 PM). Caesars' own poker page, read "
         "the same day, says every one of the four events carries a $100 buy-in. The conflict is "
         "flag F-14 and no figure is presented as settled."),
    ],
)

BELLAGIO_SCHEDULE = dict(
    room="Bellagio",
    room_page="https://bellagio.mgmresorts.com/en/casino/poker.html",
    retrieved=RETRIEVED,
    cadence="Weekly",
    events=[
        dict(
            day="Fridays", start="11:00 AM", name="NLH $600 buy-in",
            buy_in=600, to_pool=510, house_fee=50, gratuity=40, gratuity_chips=15000,
            chips_without_gratuity=15000, chips_with_gratuity=30000,
            level_min=30, guarantee=None, game="No-Limit Hold'em",
            source=("https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/"
                    "blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/"
                    "mgm-bellagio-poker-fridays-$600-nlh.pdf"),
            quotes=[
                ("Re-entry",
                 "\u201c3. Players may buy-in and re-enter through the end of level 8 (Including "
                 "Break). Tournament Surrender is allowed on Level 8 break.\u201d"),
                ("Split",
                 "\u201c5. The $600 Buy-In is allocated as follows: $510 to Prize Pool; $50 House "
                 "Fee; $40 Voluntary Staff Gratuity.\u201d"),
                ("Gratuity buys chips",
                 "\u201c7. The voluntary staff gratuity will grant players an extra 15,000 chips. "
                 "This optional gratuity is paid to staff and will not be kept by the house.\u201d"),
                ("Starting stack",
                 "\u201c1. Players will start with 30,000 tournament chips, including the optional "
                 "Staff Gratuity. (15,000 + 15,000)\u201d"),
            ],
            gaps=["No guarantee is printed on this sheet.", "No end time is printed."],
        ),
        dict(
            day="Saturdays", start="11:00 AM", name="NLH (sheet headline: $1,100 buy-in)",
            buy_in=None, to_pool=510, house_fee=50, gratuity=40, gratuity_chips=20000,
            chips_without_gratuity=20000, chips_with_gratuity=40000,
            level_min=30, guarantee=50000, game="No-Limit Hold'em",
            source=("https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/"
                    "blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/"
                    "mgm-bellagio-poker-saturdays-$1000-nlh.pdf"),
            buy_in_conflict=True,
            quotes=[
                ("Combined prize pool",
                 "\u201c8. Bellagio guarantees that the total Combined Prize Pool will be at least "
                 "$50,000.\u201d"),
                ("Split (prints $600)",
                 "\u201c7. Of the $600 Buy-in, $510 goes to the Prize Pool, $50 is Admin Fees and "
                 "$40 is optional staff gratuity.\u201d"),
                ("Gratuity buys chips",
                 "\u201c9. \u2026 There is a voluntary staff gratuity of $40, at registration only. "
                 "The voluntary staff gratuity will grant players an extra 20,000 chips.\u201d"),
                ("Registration close",
                 "\u201c3. Registration will be open until the start of Level 10. (Approximately "
                 "5:15pm for Flights 1A, 1B, 4:15pm for 1C and 9:30pm for Flight D).\u201d"),
                ("Fixed date in the sheet",
                 "\u201c4. Combined Final Day 2 (9/13/26) will begin at 12pm at Bellagio.\u201d"),
            ],
            gaps=[
                "The sheet's headline reads \u201cNLH $1100 BUY-IN\u201d while rule 7 splits a $600 "
                "buy-in. The two figures cannot both be right; the buy-in is left blank and flagged "
                "rather than picked from one of the two.",
                "The only final-day date printed is 9/13/26, which is already past on 2026-11-17, "
                "so this sheet may be a stale series document rather than the current weekly event.",
                "No end time is printed.",
            ],
        ),
        dict(
            day="Sundays", start="11:00 AM", name="$400 H.O.R.S.E. Tournament",
            buy_in=400, to_pool=340, house_fee=35, gratuity=25, gratuity_chips=15000,
            chips_without_gratuity=15000, chips_with_gratuity=30000,
            level_min=30, guarantee=None, game="H.O.R.S.E. (mixed)",
            source=("https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/"
                    "blt07fcf1244a6da661/6af491a339e2b4f6b76a86ad/"
                    "mgm-bellagio-poker-sundays-$400-horse.pdf"),
            quotes=[
                ("Re-entry",
                 "\u201c5. Players may buy-in and re-enter through the end of level 8 (Including "
                 "Break). Tournament Surrender is allowed on Level 8 break.\u201d"),
                ("Split",
                 "\u201c1. The $400 Buy-In is allocated as follows: $340 to Prize Pool; $35 House "
                 "Fee; $25 Voluntary Staff Gratuity.\u201d"),
                ("Gratuity buys chips",
                 "\u201c2. \u2026 A voluntarty [sic] Staff gratuity of $25, at registration only, "
                 "will grant players an additional 15,000 in starting chips.\u201d"),
                ("Payouts",
                 "\u201c7. Payout structure based on number of entries and will be approximately "
                 "12.5% of field.\u201d"),
            ],
            gaps=["No guarantee is printed on this sheet.", "No end time is printed."],
        ),
    ],
    verdict=("Not single-entry. Each sheet prints re-entry through level 8 and prices a "
             "\u201cvoluntary\u201d staff gratuity that buys 15,000 extra starting chips, so more "
             "money buys more chips. These events sit in the spending-more-money section."),
)

# Irregularities found on the official documents read on 2026-11-17.
IRREGULARITIES = [
    dict(
        id="X-03",
        room="Bellagio",
        what=("The official poker page says \u201cTournament play will resume on Saturday, July "
              "26\u201d, but 26 July 2026 is a Sunday."),
        why_it_matters=("The day-of-week on the page disagrees with the calendar, so the resume "
                        "date cannot be taken as printed. The three weekly structure sheets are "
                        "read as the operative schedule instead."),
        source="https://bellagio.mgmresorts.com/en/casino/poker.html",
        retrieved=RETRIEVED,
    ),
    dict(
        id="X-04",
        room="Bellagio",
        what=("The Saturday sheet is headlined \u201cNLH $1100 BUY-IN\u201d while its own rule 7 "
              "splits \u201c[t]he $600 Buy-in\u201d."),
        why_it_matters=("The buy-in is the number the whole ranking rests on, and the official "
                        "document gives two different ones. No figure is published; both are "
                        "shown so the room can be asked which is current."),
        source=BELLAGIO_SCHEDULE["events"][1]["source"],
        retrieved=RETRIEVED,
    ),
    dict(
        id="X-05",
        room="Bellagio",
        what=("The Saturday sheet prints \u201cCombined Final Day 2 (9/13/26)\u201d, a date that "
              "had already passed when the sheet was read on 2026-11-17."),
        why_it_matters=("A sheet naming a past final day may be a stale series document. Treat "
                        "the Saturday event as unconfirmed until the room republishes it."),
        source=BELLAGIO_SCHEDULE["events"][1]["source"],
        retrieved=RETRIEVED,
    ),
    dict(
        id="X-06",
        room="MGM Grand",
        what=("The official poker page https://mgmgrand.mgmresorts.com/en/casino/poker.html now "
              "returns \u201cOops! We can't find that page\u201d (HTTP 200 with a not-found body)."),
        why_it_matters=("An earlier session recorded a $120 daily structure sheet from this room "
                        "with a $11 gratuity that buys 10,000 chips. That reading can no longer "
                        "be re-verified against a live page, so it is published as historical "
                        "provenance rather than a current citation."),
        source="https://mgmgrand.mgmresorts.com/en/casino/poker.html",
        retrieved=RETRIEVED,
    ),
    dict(
        id="X-07",
        room="Wynn / Encore",
        what=("The official poker-room page https://www.wynnlasvegas.com/casino/poker-room "
              "returns \u201cIT SEEMS THIS PAGE HAS CHECKED OUT\u201d (a not-found page)."),
        why_it_matters=("No dated schedule, buy-in or entry rule can be read for the WPT World "
                        "Championship host room. Any Wynn figure on this site is historical "
                        "provenance, not a current citation."),
        source="https://www.wynnlasvegas.com/casino/poker-room",
        retrieved=RETRIEVED,
    ),
]

# Pages the scheduled re-check should hash, so a change in any of them is detected.
MONITOR_URLS = [
    ("BPOKER", "Bellagio poker room page", BELLAGIO_SCHEDULE["room_page"]),
    ("BFRI", "Bellagio Friday $600 NLH structure sheet",
     BELLAGIO_SCHEDULE["events"][0]["source"]),
    ("BSAT", "Bellagio Saturday NLH structure sheet",
     BELLAGIO_SCHEDULE["events"][1]["source"]),
    ("BSUN", "Bellagio Sunday $400 H.O.R.S.E. structure sheet",
     BELLAGIO_SCHEDULE["events"][2]["source"]),
    ("CPCAS", "Caesars Palace casino page (links the daily poker flyer)",
     CAESARS_SCHEDULE["room_page"]),
    ("CPSCHED", "Caesars Palace daily NLH tournament flyer", CAESARS_SCHEDULE["source"]),
]
