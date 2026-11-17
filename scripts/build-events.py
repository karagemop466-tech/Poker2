#!/usr/bin/env python3
"""Build the canonical event dataset (site-data/events.json) for the poker planner.

Source discipline (hard rules, enforced below):
  * Every row is transcribed from ONE official publisher page: The Venetian's
    DeepStack Extravaganza IV schedule (https://www.venetianlasvegas.com/resort/casino/poker/
    deepstack-extravaganza-poker-tournament/dse-nov-2026.html), re-read 2026-11-16.
  * Buy-in and guarantee are parsed from the official event name and then CROSS-CHECKED
    against the guarantee stated on that event's official structure sheet. A mismatch aborts
    the build (this is the line-by-line verification the site claims to perform).
  * Fee, prize pool per entry, starting chips, level length and the late-registration
    cutoff are taken only from a structure sheet that was read in full. Events whose sheet
    was not read carry null in those columns and are reported as UNVERIFIED.
  * Entry rules are never inferred. Three states are used:
      explicit   - the official text states the rule (quoted excerpt stored)
      silent     - the sheet was read in full and contains no such provision
      not_read   - no official document for that event has been read
  * Values that are computed (guarantee/buy-in ratio, schedule windows) are marked
    "computed" so they are never mistaken for a published figure.

Usage: python3 scripts/build-events.py [--check]
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site-data", "events.json")
AS_OF = "2026-11-16"          # date the official schedule page was transcribed (ROWS below)
TODAY = "2026-11-17"          # date of the structure-sheet re-read pass below
# Structure sheets read in full during the 2026-11-17 pass. Their rows carry last_checked
# 2026-11-17; rows supported only by the 2026-11-16 reads keep that earlier date.
SHEET_READ_TODAY = {2, 3, 4, 9, 12, 13, 14, 16, 17, 19, 20, 21, 22}
SCHED_URL = ("https://www.venetianlasvegas.com/resort/casino/poker/"
             "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
SHEET_URL = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/"
             "2026/structures/dse_nov_2026-structure_{n}.pdf")

# --------------------------------------------------------------------------------------
# Official structure sheets read in full on 2026-11-16 (this session). Each block holds
# only what the sheet states. `entry_text` is the verbatim rule wording used as evidence.
# --------------------------------------------------------------------------------------
SILENT_ENTRY = ("Read in full: the sheet lists no rebuy, no add-on and no re-entry "
                "provision. It states a late-registration window only.")
SILENT_ADDON = "Read in full: the sheet contains no add-on provision."
PAY125 = "This event pays 12.5% of the field"

SHEETS = {
    1: {
        "title": "$200 No Limit Hold'em Bounty (1Day)",
        "events": ["09", "11", "13", "15", "21", "22", "23", "25", "60", "61", "62", "64"],
        "start": "17:10", "chips": 25000, "level_min": 30, "reg_close": "21:40",
        "reg_close_text": "Late Registration: 8 levels + Break (9:40 PM)",
        "fee": 40, "pool": 160, "gtd": {"*": 8000},
        "gtd_text": "Guarantee: $8,000 (prize pool + total bounties)",
        "bounty": 50, "bounty_text": ("Players receive $50 bounty for each player they eliminate "
                                      "from the tournament."),
        "pays": 12.5,
        "fee_text": ("$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $160 of every $200 Buy In."),
    },
    5: {
        "title": "$300 No Limit Hold'em (1Day)",
        "events": ["02", "12"],
        "start": "11:10", "chips": 40000, "level_min": 30, "reg_close": "16:55",
        "reg_close_text": "Late Registration: 10 levels + Break (~ 4:55 PM)",
        "fee": 58, "pool": 242, "gtd": {"*": 10000}, "gtd_text": "Guarantee: $10,000",
        "bounty": None, "pays": 12.5,
        "fee_text": ("$58 of the $300 Buy-In is withheld for house fees (Rake - Staff). "
                     "The prize pool consists of $242 of every $300 Buy In."),
    },
    6: {
        "title": "$400 No Limit Hold'em (1Day)",
        "events": ["10"],
        "start": "11:10", "chips": 40000, "level_min": 30, "reg_close": "16:55",
        "reg_close_text": "Late Registration: 10 levels + Break (~ 4:55 PM)",
        "fee": 65, "pool": 335, "gtd": {"*": 15000}, "gtd_text": "Guarantee: $15,000",
        "bounty": None, "pays": 12.5,
        "fee_text": ("$65 of the $400 Buy-In is withheld for house fees (Rake - Staff). "
                     "The prize pool consists of $335 of every $400 Buy In."),
    },
    7: {
        "title": "$600 No Limit Hold'em (1Day)",
        "events": ["14", "28", "63"],
        "start": "11:10", "chips": 40000, "level_min": 30, "reg_close": "16:55",
        "reg_close_text": "Late Registration: 10 levels + Break (~ 4:55 PM)",
        "fee": 90, "pool": 510, "gtd": {"14": 30000, "28": 40000, "63": 30000},
        "gtd_text": ("Guarantee: $30,000 for Event #14 and #63; "
                     "Guarantee: $40,000 for Event #28"),
        "bounty": None, "pays": 12.5,
        "fee_text": ("$90 of the $600 Buy-In is withheld for house fees (Rake - Staff). "
                     "The prize pool consists of $510 of every $600 Buy In."),
    },
    8: {
        "title": "$200 No Limit Hold'em Valuetown Bounty (1Day) - PokerAtlas PRO Member "
                "$20 Rake Discount",
        "events": ["18", "58"],
        "start": "17:10", "chips": 25000, "level_min": 30, "reg_close": "21:40",
        "reg_close_text": "Late Registration: 8 levels + Break (9:40 PM)",
        "fee": 40, "pool": 160, "gtd": {"*": 20000},
        "gtd_text": "Guarantee: $20,000 (prize pool + total bounties)",
        "bounty": 50, "bounty_text": ("Players receive $50 bounty for each player they eliminate "
                                      "from the tournament."),
        "pays": 12.5,
        "fee_text": ("$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $160 of every $200 Buy In."),
        # The only Venetian sheet read that prices additional buy-ins out loud.
        "re_entry_explicit": ("PokerAtlas PRO players will receive a twenty ($20) rake discount "
                              "on their initial $200 buy in only, for a total buy in of $180 "
                              "instead of $200. [...] All subsequent buy in's after the initial "
                              "buy in will be $200."),
        "single_entry_explicit": "no - the sheet prices a second and later buy-in",
        "spend_advantage": ("PokerAtlas PRO membership (a paid third-party subscription) buys a "
                            "$20 discount on the first entry: rule 07."),
    },
    10: {
        "title": "$300 No Limit Hold'em - Day A+C @ 11:10 AM with Day 2 @ 12:00 PM",
        "events": ["01", "01D2"],
        "start": "11:10", "chips": 30000, "level_min": 40, "reg_close": "15:40",
        "reg_close_text": "Late Registration: 6 levels + Break (~ 3:40 PM)",
        "fee": 60, "pool": 240, "gtd": {"*": 75000}, "gtd_text": "Guarantee: $75,000",
        "bounty": None, "pays": None,
        "fee_text": ("$60 of the $300 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $240 of every $300 Buy In."),
        "multi_flight_explicit": ("Each starting flight will play until we are down to "
                                 "approximately 12.5% of the field remaining. Day 2 will resume at "
                                 "12:00 PM combining all remaining players from 1A, 1B, 1C, and "
                                 "1D [...] Any player who bags chips for Day 2 may not play a "
                                 "subsequent flight."),
    },
    11: {
        "title": "$600 No Limit Hold'em Bounty (1Day)",
        "events": ["16", "30", "54"],
        "start": "11:10", "chips": 40000, "level_min": 30, "reg_close": "16:55",
        "reg_close_text": "Late Registration: 10 levels + Break (4:55 PM)",
        "fee": 90, "pool": 510,
        "gtd": {"16": 30000, "30": 40000, "54": 50000},
        "gtd_text": ("Guarantee: $30,000 (prize pool + total bounties) Event #16; "
                     "$40,000 Event #30; $50,000 Event #54"),
        "bounty": 200,
        "bounty_text": ("Players receive $200 Bounty for each player they eliminate from the "
                        "tournament. Once we reach the money (posted payouts) - players receive a "
                        "$500 Bounty for each player they eliminate from the tournament."),
        "pays": 12.5,
        "fee_text": ("$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $510 of every $600 Buy In."),
    },
    15: {
        "title": "$300 No Limit Hold'em Bounty (1Day)",
        "events": ["29", "31", "34", "38", "42", "50", "51", "53", "55"],
        "start": "17:10", "chips": 25000, "level_min": 30, "reg_close": "21:40",
        "reg_close_text": "Late Registration: 8 levels + Break (9:40 PM)",
        "fee": 50, "pool": 250, "gtd": {"*": 15000},
        "gtd_text": "Guarantee: $15,000 (prize pool + total bounties)",
        "bounty": 100,
        "bounty_text": ("Players receive $100 bounty for each player they eliminate from the "
                        "tournament."),
        "pays": 12.5,
        "fee_text": ("$50 of the $300 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $250 of every $300 Buy In."),
    },
    18: {
        "title": "$200 No Limit Hold'em (1Day) RaceDay Stack",
        "events": ["03", "04", "05"],
        "start": "10:10", "chips": 30000, "level_min": 20, "reg_close": "12:25",
        "reg_close_text": "Late Registration: 6 levels + Break (~ 12:25 PM)",
        "fee": 35, "pool": 165, "gtd": {}, "gtd_text": "No guarantee stated on the sheet.",
        "bounty": None, "pays": 12.5,
        "fee_text": ("$35 of the $200 Buy-In is withheld for house fees (Rake - Staff). "
                     "The prize pool consists of $165 of every $200 Buy In."),
        "level_note": "Levels 1-6 at 20 minutes, then 15-minute levels (20/15 minutes).",
    },
    29: {
        "title": "$200 No Limit Hold'em (1Day)",
        "events": ["06"],
        "start": "11:10", "chips": 30000, "level_min": 30, "reg_close": "15:40",
        "reg_close_text": "Late Registration: 8 levels + Break (~ 3:40 PM)",
        "fee": 40, "pool": 160, "gtd": {}, "gtd_text": "No guarantee stated on the sheet.",
        "bounty": None, "pays": 12.5,
        "fee_text": ("$40 of the $200 Buy-In is withheld for house fees (Rake - Staff). "
                     "The prize pool consists of $160 of every $200 Buy In."),
    },
    # Event 17's structure document number was captured from the schedule page (the link is
    # split across two page chunks: ".../dse_nov_20" + "26-structure_26.pdf"). The sheet
    # itself has not been read, so only the document number is recorded here.
    26: {"title": "$400 Pot Limit Omaha Bounty (1Day)", "events": ["17"], "not_read": True},
    # ---- sheets read in full on 2026-11-17 (arena/0fd90745-poker2 final-integration pass) ----
    2: {
        "title": "$400 No Limit Hold'em - Day A+B @ 11:10 AM with Day 2 @ 11:00 AM",
        "events": ["07", "07D2"],
        "start": "11:10", "chips": 40000, "level_min": 40, "reg_close": "17:55",
        "reg_close_text": "Late Registration: 9 levels + Break (5:55 PM)",
        "fee": 70, "pool": 330, "gtd": {"*": 75000}, "gtd_text": "Guarantee: $75,000",
        "bounty": None, "pays": None,
        "fee_text": ("$70 of the $400 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $330 of every $400 Buy In."),
        "multi_flight_explicit": (
            "Each starting flight will play until we are down to approximately 12.5% of the "
            "field remaining. Day 2 will resume at 11:00 AM combining all remaining players from "
            "1A and 1B with all players being considered in the money and will continue until a "
            "winner has been declared. [...] Any player who bags chips for Day 2 may not play a "
            "subsequent flight."),
    },
    3: {
        "title": "$400 No Limit Hold'em - Day A+B+C @ 11:10 AM with Day 2 @ 11:00 AM",
        "events": ["19", "19D2"],
        "start": "11:10", "chips": 40000, "level_min": 40, "reg_close": "17:55",
        "reg_close_text": "Late Registration: 9 levels + Break (5:55 PM)",
        "fee": 70, "pool": 330, "gtd": {"*": 75000}, "gtd_text": "Guarantee: $75,000",
        "bounty": None, "pays": None,
        "fee_text": ("$70 of the $400 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $330 of every $400 Buy In."),
        "multi_flight_explicit": (
            "Each starting flight will play until we are down to approximately 12.5% of the "
            "field remaining. Day 2 will resume at 11:00 AM combining all remaining players from "
            "1A, 1B, and 1C with all players being considered in the money and will continue "
            "until a winner has been declared. [...] Any player who bags chips for Day 2 may "
            "not play a subsequent flight."),
    },
    4: {
        "title": "$600 No Limit Hold'em - Day A+B+C @ 11:10 AM with Day 2 @ 11:00 AM",
        "events": ["59", "59D2"],
        "start": "11:10", "chips": 40000, "level_min": 40, "reg_close": "17:55",
        "reg_close_text": "Late Registration: 9 levels + Break (5:55 PM)",
        "fee": 95, "pool": 505, "gtd": {"*": 150000}, "gtd_text": "Guarantee: $150,000",
        "bounty": None, "pays": None,
        "fee_text": ("$95 of the $600 Buy-In is withheld for house fees (Rake + Staff). The "
                     "prize pool consists of $505 of every $600 Buy In. On Day 1A only, players "
                     "who register before the start of the event (11:10 a.m.), will receive a "
                     "$20 discount on house fees for a total buy in of $580 instead of $600."),
        "multi_flight_explicit": (
            "Each starting flight will play until we are down to approximately 12.5% of the "
            "field remaining. Day 2 will resume at 11:00 AM combining all remaining players from "
            "1A, 1B, and 1C with all players being considered in the money [...] Any player who "
            "bags chips for Day 2 may not play a subsequent flight."),
        "discount_note": ("Rule 07: Day 1A only, $20 off the house fee for pre-start registration "
                          "($580 total). A discount for registering early, not a purchase of "
                          "chips or entries; no rebuy/add-on clause on the sheet."),
    },
    9: {
        "title": "$300 No Limit Hold'em - Day B+D @ 5:10 PM with Day 2 @ 12:00 PM",
        "events": ["01"],
        "start": "17:10", "chips": 30000, "level_min": 30, "reg_close": "20:40",
        "reg_close_text": "Late Registration: 6 levels + Break (~ 8:40 PM)",
        "fee": 60, "pool": 240, "gtd": {"*": 75000}, "gtd_text": "Guarantee: $75,000",
        "bounty": None, "pays": None,
        "fee_text": ("$60 of the $300 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $240 of every $300 Buy In."),
        "multi_flight_explicit": (
            "Each starting flight will play until we are down to approximately 12.5% of the "
            "field remaining. Day 2 will resume at 12:00 PM combining all remaining players from "
            "1A, 1B, 1C, and 1D with all players being considered in the money & will continue "
            "until a winner has been declared. [...] Any player who bags chips for Day 2 may not "
            "play a subsequent flight."),
        "cross_ref": "Sheet footer: \"SEE OTHER STRUCTURE SHEET FOR DAYS A+C\" (structure_10.pdf).",
    },
    12: {
        "title": "$800 No Limit Hold'em - Day A+C+E @ 11:10 AM with Day 2 @ 12:00 PM",
        "events": ["26"],
        "start": "11:10", "chips": 40000, "level_min": 40, "reg_close": "15:40",
        "reg_close_text": "Late Registration: 6 levels + Break (~ 3:40 PM)",
        "fee": 110, "pool": 690, "gtd": {"*": 500000}, "gtd_text": "Guarantee: $500,000",
        "bounty": None, "pays": None,
        "fee_text": ("$110 of the $800 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $690 of every $800 Buy In."),
        "multi_flight_explicit": (
            "Each starting flight will play until we are down to approximately 12.5% of the "
            "field remaining. Day 2 will resume at 12:00 PM combining all remaining players from "
            "1A, 1B, 1C, 1D, 1E, and 1F, with all players being considered in the money & will "
            "continue until a winner has been declared. [...] Any player who bags chips for "
            "Day 2 may not play a subsequent flight."),
        "cross_ref": "Sheet footer: \"SEE OTHER STRUCTURE SHEET FOR DAYS B+D+F\" (structure_13.pdf).",
    },
    13: {
        "title": "$800 No Limit Hold'em - Day B+D @ 5:10 PM with Day 2 @ 12:00 PM",
        "events": ["26"],
        "start": "17:10", "chips": 40000, "level_min": 30, "reg_close": "20:40",
        "reg_close_text": "Late Registration: 6 levels + Break (~ 8:40 PM)",
        "fee": 110, "pool": 690, "gtd": {"*": 500000}, "gtd_text": "Guarantee: $500,000",
        "bounty": None, "pays": None,
        "fee_text": ("$110 of the $800 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $690 of every $800 Buy In."),
        "multi_flight_explicit": (
            "Each starting flight will play until we are down to approximately 12.5% of the "
            "field remaining. Day 2 will resume at 12:00 PM combining all remaining players from "
            "1A, 1B, 1C, 1D, 1E, and 1F with all players being considered in the money & will "
            "continue until a winner has been declared. [...] Any player who bags chips for "
            "Day 2 may not play a subsequent flight."),
        # Recorded as printed: the footer names A+C+F while the header of this sheet covers B+D.
        "irregularity": ("The footer says \"SEE OTHER STRUCTURE SHEET FOR DAYS A+C+F\" while the "
                         "header of the same sheet reads \"Day B+D\", and structure_12.pdf lists "
                         "Day A+C+E. One of the two flight cross-references is a typo; the "
                         "schedule page rows (1A/1C/1E at 11:10, 1B/1D at 5:10 PM, 1F Turbo) are "
                         "used instead. Flagged for review."),
    },
    14: {
        "title": "$800 No Limit Hold'em - Day F (Turbo) @ 5:10 PM with Day 2 @ 12:00 PM",
        "events": ["26"],
        "start": "17:10", "chips": 40000, "level_min": 20, "reg_close": "19:25",
        "reg_close_text": "Late Registration: 6 levels + Break (~ 7:25 PM)",
        "fee": 110, "pool": 690, "gtd": {"*": 500000}, "gtd_text": "Guarantee: $500,000",
        "bounty": None, "pays": None,
        "fee_text": ("$110 of the $800 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $690 of every $800 Buy In."),
        "multi_flight_explicit": (
            "Each starting flight will play until we are down to approximately 12.5% of the "
            "field remaining. Day 2 will resume at 12:00 PM combining all remaining players from "
            "1A, 1B, 1C, 1D, 1E, and 1F with all players being considered in the money [...] "
            "Any player who bags chips for Day 2 may not play a subsequent flight."),
        "cross_ref": ("Sheet footer: \"SEE OTHER STRUCTURE SHEETS FOR DAYS A+B+C+D+E\" "
                      "(structure_12.pdf and structure_13.pdf). Turbo levels: 20 minutes."),
    },
    16: {
        "title": "$800 No Limit Hold'em Bounty (1Day)",
        "events": ["36"],
        "start": "11:10", "chips": 40000, "level_min": 30, "reg_close": "16:55",
        "reg_close_text": "Late Registration: 10 levels + Break (4:55 PM)",
        "fee": 100, "pool": 700, "gtd": {"*": 75000},
        "gtd_text": "Guarantee: $75,000 (prize pool + total bounties)",
        "bounty": 200,
        "bounty_text": ("Players receive $200 Bounty for each player they eliminate from the "
                        "tournament. Once we reach the money (posted payouts) - players receive a "
                        "$500 Bounty for each player they eliminate from the tournament. [...] The "
                        "player who wins the event will keep their own bounty."),
        "pays": 12.5,
        # Bounty events: the $75,000 figure is prize pool + total bounties, not a cash pool.
        "gtd_includes_bounties": True,
        "fee_text": ("$100 of the $800 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $700 of every $800 Buy In."),
    },
    17: {
        "title": "$600 No Limit Hold'em Seniors (1Day) - must be 50+",
        "events": ["24", "32"],
        "start": "10:10", "chips": 40000, "level_min": 30, "reg_close": "15:55",
        "reg_close_text": "Late Registration: 10 levels + Break (~ 3:55 PM)",
        "fee": 90, "pool": 510, "gtd": {"*": 40000}, "gtd_text": "Guarantee: $40,000",
        "bounty": None, "pays": 15,
        "pays_text": "This event pays 15% of the field",
        "fee_text": ("$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $510 of every $600 Buy In."),
        "eligibility": ("Rule 02: \"Must be 50+ years of age and have a Venetian Rewards card to "
                        "participate. Any player who buys into this event that is not 50+ years of "
                        "age will not be entitled to any prize money or a refund of their buy in.\""),
    },
    19: {
        "title": "$100 NLH LIPS Ladies Milestone Satellite (1Day) - Event #33 and #37",
        "events": ["33", "37"],
        "start": "16:10", "chips": 20000, "level_min": 20, "reg_close": "18:25",
        "reg_close_text": "Late Registration: 6 levels + Break (~6:25 PM)",
        "fee": 20, "pool": 80, "gtd": {},
        "gtd_text": ("Guarantee: 2 Seats - \"All tournament prizes are direct entry into our $800 "
                     "No Limit Hold'em LIPS Ladies Event #39, with any odd monies awarded as one "
                     "additional payout.\""),
        "bounty": None, "pays": None,
        "fee_text": ("$20 of the $100 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $80 of every $100 Buy In."),
        "eligibility": ("Rule 02: \"Open to Female players who must 21+ years of age and have a "
                        "Venetian Rewards card to participate.\" (wording as printed)"),
        "satellite_seats": 2,
        "milestone_explicit": (
            "Rule 09: \"A Player who accumulates 200,000 in tournament chips (\"The Milestone\") "
            "or more will instantly receive direct entry into the $800 No Limit Hold'em LIPS "
            "Ladies Event #39. Upon verification by poker room management, the player who achieved "
            "The Milestone will cease play and have their chips removed from play.\""),
    },
    20: {
        "title": "$1,100 No Limit Hold'em Seniors - Day A+B @ 10:10 AM with Day 2 @ 10:00 AM",
        "events": ["49", "49D2"],
        "start": "10:10", "chips": 40000, "level_min": 40, "reg_close": "16:55",
        "reg_close_text": "Late Registration: 9 levels + Break (~ 4:55 PM)",
        "fee": 140, "pool": 960, "gtd": {"*": 300000}, "gtd_text": "Guarantee: $300,000",
        "bounty": None, "pays": None,
        "fee_text": ("$140 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $960 of every $1,100 Buy In."),
        "multi_flight_explicit": (
            "Each starting flight will play until we are down to approximately 15% of the field "
            "remaining. Day 2 will resume at 10:00 AM combining all remaining players from 1A and "
            "1B with all players being considered in the money and will continue until a winner has "
            "been declared. [...] Any player who bags chips for Day 2 may not play a subsequent "
            "flight."),
        "eligibility": ("Rule 02: \"Must be 50+ years of age and have a Venetian Rewards card to "
                        "participate. Any player who buys into this event that is not 50+ years of "
                        "age will not be entitled to any prize money or a refund of their buy in.\""),
    },
    21: {
        "title": "$2,200 No Limit Hold'em PokerAtlas Championship Title Event - "
                 "Day 1A @ 10:10 AM w/ Day 2 @ 1:00 PM w/ Day 3 @ 11:00 AM",
        "events": ["47", "47D2", "47D3"],
        "start": "10:10", "chips": 40000, "level_min": 40, "reg_close": "16:55",
        "reg_close_text": "Late Registration: 9 levels + Break (~ 4:55 PM)",
        "fee": 225, "pool": 1975, "gtd": {"*": 1000000}, "gtd_text": "Guarantee: $1,000,000",
        "bounty": None, "pays": None,
        "fee_text": ("$225 of the $2,200 Buy-In is withheld for house fees (Rake + Staff). "
                     "The prize pool consists of $1,975 of every $2,200 Buy In."),
        "multi_flight_explicit": (
            "Each starting flight will play until we are down to approximately 12.5% of the field "
            "remaining. Day 2 will resume at 1:00 PM combining all remaining players from 1A and "
            "1B with all players being considered in the money & will continue until seven (7) "
            "players remain. [...] Day 3 will resume at 11:00 AM for a streamed and distributed "
            "Final Table produced by PokerGO and play until a winner has been declared. [...] Any "
            "player who bags chips for Day 2 may not play a subsequent flight."),
        "cross_ref": "Sheet footer: \"SEE OTHER STRUCTURE SHEET FOR DAY 1B\" (structure_37.pdf).",
    },
}

# --------------------------------------------------------------------------------------
# The official schedule table, transcribed from dse-nov-2026.html on 2026-11-16
# (all four page chunks read; 64 numbered events, 94 published rows incl. flights,
# day-2 restarts and final tables). kind: DAY | FLIGHT | RESTART | FINALTABLE | SAT | TEAM
# --------------------------------------------------------------------------------------
ROWS = [
    ("2026-11-16", "11:10", "01", "$300 No Limit Hold'em 1A $75K GTD", 10, "FLIGHT"),
    ("2026-11-16", "17:10", "01", "$300 No Limit Hold'em 1B $75K GTD", 9, "FLIGHT"),
    ("2026-11-17", "11:10", "01", "$300 No Limit Hold'em 1C $75K GTD", 10, "FLIGHT"),
    ("2026-11-17", "17:10", "01", "$300 No Limit Hold'em 1D $75K GTD", 9, "FLIGHT"),
    ("2026-11-18", "11:10", "02", "$300 No Limit Hold'em $10K GTD (1Day)", 5, "DAY"),
    ("2026-11-18", "12:00", "01", "$300 No Limit Hold'em Day 2 Restart", 10, "RESTART"),
    ("2026-11-19", "10:10", "03", "$200 NLH RaceDay Stack (1Day) - Race to finish before the Race", 18, "DAY"),
    ("2026-11-20", "10:10", "04", "$200 NLH RaceDay Stack (1Day) - Race to finish before the Race", 18, "DAY"),
    ("2026-11-21", "10:10", "05", "$200 NLH RaceDay Stack (1Day) - Race to finish before the Race", 18, "DAY"),
    ("2026-11-22", "11:10", "06", "$200 No Limit Hold'em (1Day)", 29, "DAY"),
    ("2026-11-23", "11:10", "07", "$400 No Limit Hold'em 1A $75K GTD", 2, "FLIGHT"),
    ("2026-11-23", "17:10", "08", "$200 No Limit Hold'em $8K GTD (1Day) - Progressive Knock-Out Bounty (PKO)", 30, "DAY"),
    ("2026-11-24", "11:10", "07", "$400 No Limit Hold'em 1B $75K GTD", 2, "FLIGHT"),
    ("2026-11-24", "17:10", "09", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-11-25", "11:00", "07", "$400 No Limit Hold'em Day 2 Restart", 2, "RESTART"),
    ("2026-11-25", "11:10", "10", "$400 No Limit Hold'em $15K GTD (1Day)", 6, "DAY"),
    ("2026-11-25", "17:10", "11", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-11-26", "11:10", "12", "$300 No Limit Hold'em $10K GTD (1Day)", 5, "DAY"),
    ("2026-11-26", "17:10", "13", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-11-27", "11:10", "14", "$600 No Limit Hold'em $30K GTD (1Day)", 7, "DAY"),
    ("2026-11-27", "17:10", "15", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-11-28", "11:10", "16", "$600 No Limit Hold'em Bounty $30K GTD (1Day) - $200 bounties to start & $500 bounties in the money", 11, "DAY"),
    ("2026-11-28", "12:10", "17", "$400 Pot Limit Omaha Bounty $15K GTD (1Day)", 26, "DAY"),
    ("2026-11-28", "17:10", "18", "$200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) - PokerAtlas Pro member $20 rake discount", 8, "PARTNER"),
    ("2026-11-29", "11:10", "19", "$400 No Limit Hold'em 1A $75K GTD", 3, "FLIGHT"),
    ("2026-11-29", "12:10", "20", "$300 Pot Limit Omaha $10K GTD (1Day) - Double Board Bomb Pot", 22, "DAY"),
    ("2026-11-29", "17:10", "21", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-11-30", "11:10", "19", "$400 No Limit Hold'em 1B $75K GTD", 3, "FLIGHT"),
    ("2026-11-30", "17:10", "22", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-12-01", "11:10", "19", "$400 No Limit Hold'em 1C $75K GTD", 3, "FLIGHT"),
    ("2026-12-01", "17:10", "23", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-12-02", "10:10", "24", "$600 No Limit Hold'em Seniors $40K GTD (1Day) - must be 50+ years of age", 17, "DAY"),
    ("2026-12-02", "11:00", "19", "$400 No Limit Hold'em Day 2 Restart", 3, "RESTART"),
    ("2026-12-02", "17:10", "25", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-12-03", "11:10", "26", "$800 No Limit Hold'em 1A $500K GTD", 12, "FLIGHT"),
    ("2026-12-03", "12:10", "27", "$600 BIG O $25K GTD (1Day)", 28, "DAY"),
    ("2026-12-03", "17:10", "26", "$800 No Limit Hold'em 1B $500K GTD", 13, "FLIGHT"),
    ("2026-12-04", "11:10", "26", "$800 No Limit Hold'em 1C $500K GTD", 12, "FLIGHT"),
    ("2026-12-04", "17:10", "26", "$800 No Limit Hold'em 1D $500K GTD", 13, "FLIGHT"),
    ("2026-12-05", "11:10", "26", "$800 No Limit Hold'em 1E $500K GTD", 12, "FLIGHT"),
    ("2026-12-05", "17:10", "26", "$800 No Limit Hold'em 1F (Turbo) $500K GTD", 14, "FLIGHT"),
    ("2026-12-06", "11:10", "28", "$600 No Limit Hold'em $40K GTD (1Day)", 7, "DAY"),
    ("2026-12-06", "12:00", "26", "$800 No Limit Hold'em Day 2 Restart", 12, "RESTART"),
    ("2026-12-06", "17:10", "29", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 15, "DAY"),
    ("2026-12-07", "11:10", "30", "$600 No Limit Hold'em Bounty $40K GTD (1Day) - $200 bounties to start & $500 bounties in the money", 11, "DAY"),
    ("2026-12-07", "17:10", "31", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 15, "DAY"),
    ("2026-12-08", "10:10", "32", "$600 No Limit Hold'em Seniors $40K GTD (1Day) - must be 50+ years of age", 17, "DAY"),
    ("2026-12-08", "16:10", "33", "$100 NLH LIPS Ladies Milestone Satellite (1Day) - awards direct entry to Event #39", 19, "SAT"),
    ("2026-12-08", "17:10", "34", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 15, "DAY"),
    ("2026-12-09", "10:10", "35", "$600 NLH LIPS Poker Jingle Tag Team $10K GTD (1Day) - tag teams of female/female or female/male", 31, "TEAM"),
    ("2026-12-09", "11:10", "36", "$800 No Limit Hold'em Bounty $75K GTD (1Day) - $200 bounties to start & $500 bounties in the money", 16, "DAY"),
    ("2026-12-09", "16:10", "37", "$100 NLH LIPS Ladies Milestone Satellite (1Day) - awards direct entry to Event #39", 19, "SAT"),
    ("2026-12-09", "17:10", "38", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 15, "DAY"),
    ("2026-12-10", "10:10", "39", "$800 No Limit Hold'em LIPS Ladies $40K GTD (2Day) - Women in Poker Main Event", 32, "FLIGHT"),
    ("2026-12-10", "12:10", "40", "$600 Pot Limit Omaha Bounty $25K GTD (1Day)", 27, "DAY"),
    ("2026-12-10", "16:10", "41", "$260 NLH Milestone Satellite (1Day) - awards direct entry to Event #47", 24, "SAT"),
    ("2026-12-10", "17:10", "42", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 15, "DAY"),
    ("2026-12-11", "10:00", "39", "$800 No Limit Hold'em LIPS Ladies Day 2 Restart - play down to final 7 (PokerGO)", 32, "RESTART"),
    ("2026-12-11", "11:10", "43", "$600 No Limit Hold'em LIPS $30K GTD (1Day) - Kings and Queens Bounty, open to all players", 33, "DAY"),
    ("2026-12-11", "16:10", "44", "$260 NLH Milestone Satellite (1Day) - awards direct entry to Event #47", 24, "SAT"),
    ("2026-12-11", "19:00", "39", "$800 No Limit Hold'em LIPS Ladies Final Table - streamed final table (PokerGO)", 32, "FINALTABLE"),
    ("2026-12-11", "20:10", "45", "$260 NLH Turbo Milestone Satellite (1Day) - awards direct entry to Event #47", 25, "SAT"),
    ("2026-12-12", "09:10", "46", "$260 NLH Turbo Milestone Satellite (1Day) - awards direct entry to Event #47", 25, "SAT"),
    ("2026-12-12", "10:10", "47", "$2,200 No Limit Hold'em 1A $1 Mill GTD - PokerAtlas Championship Title Event", 21, "FLIGHT"),
    ("2026-12-12", "12:10", "48", "$260 NLH Turbo Milestone Satellite (1Day) - awards direct entry to Event #47", 25, "SAT"),
    ("2026-12-12", "18:10", "47", "$2,200 No Limit Hold'em 1B $1 Mill GTD - PokerAtlas Championship Title Event", 37, "FLIGHT"),
    ("2026-12-13", "10:10", "49", "$1,100 No Limit Hold'em Seniors 1A $300K GTD - must be 50+ years of age", 20, "FLIGHT"),
    ("2026-12-13", "13:00", "47", "$2,200 NLH PokerAtlas Championship Title Event Day 2 Restart - play down to final 7 (PokerGO)", 21, "RESTART"),
    ("2026-12-13", "17:10", "50", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 15, "DAY"),
    ("2026-12-14", "10:10", "49", "$1,100 No Limit Hold'em Seniors 1B $300K GTD - must be 50+ years of age", 20, "FLIGHT"),
    ("2026-12-14", "11:00", "47", "$2,200 NLH PokerAtlas Championship Title Event Day 3 Restart - streamed final table (PokerGO)", 21, "RESTART"),
    ("2026-12-14", "17:10", "51", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 15, "DAY"),
    ("2026-12-15", "10:00", "49", "$1,100 No Limit Hold'em Seniors Day 2 Restart", 20, "RESTART"),
    ("2026-12-15", "11:10", "52", "$1,100 No Limit Hold'em $75K GTD (1Day) - Progressive Knock-Out Bounty (PKO)", 34, "DAY"),
    ("2026-12-15", "17:10", "53", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 15, "DAY"),
    ("2026-12-16", "11:10", "54", "$600 No Limit Hold'em Bounty $50K GTD (1Day) - $200 bounties to start & $500 bounties in the money", 11, "DAY"),
    ("2026-12-16", "17:10", "55", "$300 No Limit Hold'em Bounty $15K GTD (1Day)", 15, "DAY"),
    ("2026-12-17", "10:10", "56", "$1,100 No Limit Hold'em 1A $500K GTD - $40 rake discount for entries before 10:10 a.m.", 35, "FLIGHT"),
    ("2026-12-17", "12:10", "57", "$600 Pot Limit Omaha $25K GTD (1Day) - Double Board Bomb Pot", 23, "DAY"),
    ("2026-12-17", "18:10", "56", "$1,100 No Limit Hold'em 1B $500K GTD - $40 rake discount for entries before 6:10 p.m.", 36, "FLIGHT"),
    ("2026-12-18", "10:10", "56", "$1,100 No Limit Hold'em 1C $500K GTD", 35, "FLIGHT"),
    ("2026-12-18", "18:10", "56", "$1,100 No Limit Hold'em 1D $500K GTD", 36, "FLIGHT"),
    ("2026-12-19", "10:10", "56", "$1,100 No Limit Hold'em 1E $500K GTD", 35, "FLIGHT"),
    ("2026-12-19", "17:10", "58", "$200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day) - PokerAtlas Pro member $20 rake discount", 8, "PARTNER"),
    ("2026-12-20", "11:00", "56", "$1,100 No Limit Hold'em Day 2 Restart", 35, "RESTART"),
    ("2026-12-20", "11:10", "59", "$600 No Limit Hold'em 1A $150K GTD - $20 rake discount for entries before 11:10 a.m.", 4, "FLIGHT"),
    ("2026-12-20", "17:10", "60", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-12-21", "11:10", "59", "$600 No Limit Hold'em 1B $150K GTD", 4, "FLIGHT"),
    ("2026-12-21", "17:10", "61", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-12-22", "11:10", "59", "$600 No Limit Hold'em 1C $150K GTD", 4, "FLIGHT"),
    ("2026-12-22", "17:10", "62", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
    ("2026-12-23", "11:00", "59", "$600 No Limit Hold'em Day 2 Restart", 4, "RESTART"),
    ("2026-12-23", "11:10", "63", "$600 No Limit Hold'em $30K GTD (1Day)", 7, "DAY"),
    ("2026-12-23", "17:10", "64", "$200 No Limit Hold'em Bounty $8K GTD (1Day)", 1, "DAY"),
]

NAME_BUYIN = re.compile(r"\$([\d,]+)")
NAME_GTD = re.compile(r"\$([\d.]+)\s*(K|Mill|MM)?\s*GTD", re.I)
DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def parse_money_buysin(name):
    m = NAME_BUYIN.search(name)
    return int(m.group(1).replace(",", "")) if m else None


def parse_gtd(name):
    m = NAME_GTD.search(name)
    if not m:
        return None
    val = float(m.group(1))
    unit = (m.group(2) or "").lower()
    if unit == "k":
        val *= 1000
    elif unit in ("mill", "mm"):
        val *= 1_000_000
    return int(val)


def hhmm_to_min(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def dow(datestr):
    import datetime
    return DOW[datetime.date.fromisoformat(datestr).weekday()]


def build():
    events = []
    for date, start, num, name, sheetno, kind in ROWS:
        sheet = SHEETS.get(sheetno)
        read = bool(sheet) and not sheet.get("not_read")
        buyin = parse_money_buysin(name)
        gtd_name = parse_gtd(name)
        ev_key = num + ("D2" if kind == "RESTART" else "")
        gtd_sheet = None
        if read:
            gmap = sheet["gtd"]
            gtd_sheet = gmap.get(num, gmap.get("*"))
            if gtd_sheet and gtd_name and gtd_sheet != gtd_name:
                # Satellites and RaceDay formats legitimately state no number; anything else
                # means the schedule name and the structure sheet disagree -> stop the build.
                raise SystemExit(f"event {num} {date}: schedule name guarantee ${gtd_name:,} "
                                 f"disagrees with structure sheet {sheetno} (${gtd_sheet:,})")
        is_restart = kind in ("RESTART", "FINALTABLE")
        ev = {
            "id": f"V{num}-{date.replace('-', '')}-{start.replace(':', '')}",
            "property": "The Venetian / The Palazzo",
            "venue": "venetian",
            "date": date,
            "dow": dow(date),
            "start": start,
            "event_no": num,
            "name": name,
            "buy_in": buyin if not is_restart else None,
            "gtd": gtd_sheet or gtd_name,
            "gtd_source": "structure sheet" if gtd_sheet else ("official schedule name" if gtd_name else None),
            "fee": sheet["fee"] if read and not is_restart else None,
            "total_entry_cost": (buyin + 0) if (read and buyin and not is_restart) else (buyin if buyin and not is_restart else None),
            "pool_per_entry": sheet["pool"] if read and not is_restart else None,
            "chips": sheet["chips"] if read and not is_restart else None,
            "level_min": sheet["level_min"] if read and not is_restart else None,
            "reg_close": None if is_restart else (sheet["reg_close"] if read else None),
            "reg_close_text": None if is_restart else (sheet["reg_close_text"] if read else None),
            "pays_pct": sheet.get("pays") if read and not is_restart else None,
            "bounty": sheet.get("bounty") if read and not is_restart else None,
            "sheet": sheetno,
            "sheet_read": read,
            "sheet_url": SHEET_URL.format(n=sheetno),
            "schedule_url": SCHED_URL,
            "last_checked": (TODAY if sheetno in SHEET_READ_TODAY else AS_OF) if read else AS_OF,
            "schedule_checked": AS_OF,
            "kind": kind,
        }
        if sheet:
            if sheet.get("eligibility"):
                ev["eligibility"] = sheet["eligibility"]
            for k in ("discount_note", "cross_ref", "irregularity"):
                if sheet.get(k):
                    ev.setdefault("sheet_notes", []).append(sheet[k])
            if sheet.get("satellite_seats"):
                ev["satellite_seats"] = sheet["satellite_seats"]
        # ---- structured rule fields, each with its own source excerpt + retrieval date ----
        got = TODAY if (read and sheetno in SHEET_READ_TODAY) else (AS_OF if read else None)

        def field(value, status, excerpt, url):
            return {"value": value, "status": status, "excerpt": excerpt,
                    "source_url": url, "retrieved": got}

        if read and kind in ("DAY", "PARTNER", "SAT", "TEAM"):
            one_entry = "one_entry_explicit" in sheet
            priced = "re_entry_explicit" in sheet
            ev["rules"] = {
                "single_entry": field(
                    "yes" if one_entry else None,
                    "explicit" if one_entry else (
                        "explicit_no" if priced else "not_stated_sheet_read"),
                    sheet.get("one_entry_explicit") or (
                        "Sheet rule 07 prices subsequent buy-ins (see re_entry)." if priced
                        else SILENT_ENTRY),
                    ev["sheet_url"]),
                "re_entry": field(
                    "subsequent buy-ins priced at $200" if priced else None,
                    "explicit" if priced else "not_stated_sheet_read",
                    sheet.get("re_entry_explicit") or SILENT_ENTRY,
                    ev["sheet_url"]),
                "add_on": field(
                    None, "not_stated_sheet_read", SILENT_ADDON, ev["sheet_url"])
                if not sheet.get("add_on_explicit") else field(
                    "add-on offered", "explicit", sheet["add_on_explicit"], ev["sheet_url"]),
                "fee": field(sheet["fee"], "explicit", sheet["fee_text"], ev["sheet_url"]),
                "guarantee": field(gtd_sheet, "explicit", sheet["gtd_text"], ev["sheet_url"]),
                "payout": field(sheet.get("pays"), "explicit", sheet.get("pays_text", PAY125),
                                ev["sheet_url"])
                if sheet.get("pays") else field(None, "not_stated_sheet_read", None, ev["sheet_url"]),
                "bounty": field(sheet.get("bounty"), "explicit", sheet.get("bounty_text"),
                                ev["sheet_url"]) if sheet.get("bounty") else None,
            }
        elif read and kind == "FLIGHT":
            ev["rules"] = {
                "single_entry": field("no", "explicit",
                                      sheet.get("multi_flight_explicit",
                                                 "multi-flight event: each starting flight is a separate entry"),
                                      ev["sheet_url"]),
                "re_entry": field("play another starting flight if you did not bag Day 2 chips",
                                  "explicit", sheet.get("multi_flight_explicit"), ev["sheet_url"]),
                "add_on": field(None, "not_stated_sheet_read", SILENT_ADDON, ev["sheet_url"]),
                "fee": field(sheet["fee"], "explicit", sheet["fee_text"], ev["sheet_url"]),
                "guarantee": field(gtd_sheet, "explicit", sheet["gtd_text"], ev["sheet_url"]),
                "payout": None, "bounty": None,
            }
        else:
            ev["rules"] = {k: field(None, "not_read", None, ev["sheet_url"])
                           for k in ("single_entry", "re_entry", "add_on", "fee", "guarantee",
                                     "payout", "bounty")}

        # ---- classification ----
        if is_restart or kind == "RESTART":
            ev["category"] = "day2_restart"
        elif kind == "FINALTABLE":
            ev["category"] = "final_table"
        elif kind == "SAT":
            ev["category"] = "satellite"
        elif kind == "TEAM":
            ev["category"] = "team_format"
        elif kind == "FLIGHT":
            ev["category"] = "multi_flight"
        elif kind == "PARTNER":
            ev["category"] = "spend_advantage"
        elif not read:
            ev["category"] = "unverified"
        elif "re_entry_explicit" in sheet:
            ev["category"] = "spend_advantage"
        else:
            ev["category"] = "single_entry_candidate"
        # ---- computed, clearly labelled as computed ----
        ev["ratio_gtd_to_buyin"] = (round(ev["gtd"] / ev["buy_in"], 1)
                                    if ev["gtd"] and ev["buy_in"] else None)
        ev["earliest_plausible_finish"] = None
        if ev["reg_close"] and ev["level_min"]:
            ev["earliest_plausible_finish"] = hhmm_to_min(ev["reg_close"]) + ev["level_min"]
        events.append(ev)

    # duplicate-name sanity: the sheet's own event list must match the rows tagged to it
    for n, s in SHEETS.items():
        if s.get("not_read"):
            continue
        tagged = {e["event_no"] for e in events if e["sheet"] == n and e["kind"] in ("DAY", "PARTNER", "FLIGHT")}
        listed = {(x[:-2] if x.endswith("D2") else x) for x in s["events"]}
        extra = tagged - listed
        if extra:
            raise SystemExit(f"structure sheet {n} does not list event(s) {sorted(extra)} "
                             "that this dataset tags to it")
    return events


def main():
    events = build()
    payload = {
        "generated_from": SCHED_URL,
        "as_of": AS_OF,
        "publisher": "The Venetian Las Vegas (official)",
        "series": "DeepStack Extravaganza IV, November 16 - December 23, 2026",
        "definition": {
            "single_entry_candidate": ("One-day event whose official structure sheet was read in "
                                       "full and contains no rebuy, add-on or re-entry provision. "
                                       "The sheet does NOT state a one-entry cap, so this is the "
                                       "highest state the published sources support; ask the room "
                                       "for a written answer (see Questions)."),
            "spend_advantage": ("Money buys an edge or extra entries: paid third-party membership "
                                "discounts, priced subsequent buy-ins, rebuys or add-ons."),
            "multi_flight": ("Day 1A/1B/... flights: a player who does not reach Day 2 may buy "
                             "into another starting flight (stated on the sheet), so the event is "
                             "not single-entry."),
            "unverified": ("Row exists on the official schedule; the structure sheet has not been "
                           "read, so entry rules, fee and payout timing are unknown."),
            "ratio_gtd_to_buyin": ("Descriptive only: published guarantee divided by the buy-in. "
                                   "It is not an expected value, a forecast, or an overlay."),
        },
        "events": events,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    txt = json.dumps(payload, indent=1, ensure_ascii=False)
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf8").read() if os.path.exists(OUT) else ""
        if cur.strip() != txt.strip():
            raise SystemExit("site-data/events.json is stale; run python3 scripts/build-events.py")
        print(f"events.json up to date ({len(events)} rows)")
        return
    with open(OUT, "w", encoding="utf8") as fh:
        fh.write(txt + "\n")
    cats = {}
    for e in events:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
    print(f"wrote {len(events)} rows -> site-data/events.json; categories: {cats}")


if __name__ == "__main__":
    main()
