#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verified structure-sheet values — The Venetian Resort Las Vegas, DeepStack
Extravaganza IV (Nov 16 - Dec 23, 2026).

HOW THIS FILE IS BUILT
  One entry per official structure-sheet PDF that was opened and read in full on
  2026-11-17. Every field is a verbatim transcription of something printed on that
  PDF. Nothing is inferred, and a field that the PDF does not print is `None`.

  `single_entry` records ONLY what the sheet prints:
    "explicit_no"      the sheet prints a rule that forbids entering a second time
    "explicit_yes"     the sheet prints a mechanism for a second entry / rebuy / add-on
    "not_stated"       the sheet was read in full and prints no entry-limit clause
  `not_stated` is silence. It is NOT a published no-re-entry rule, and this file
  never upgrades silence to "single entry". See flag FD-03.

  URL pattern: theschedule page links each row to
  https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_<n>.pdf
"""

RETRIEVED = "2026-11-17"
SHEET_URL = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/"
             "deepstack/2026/structures/dse_nov_2026-structure_%d.pdf")
SCHEDULE_URL = ("https://www.venetianlasvegas.com/resort/casino/poker/"
                "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")

SHEETS = [
    {
        "sheet": 1,
        "doc_title": "$200 No Limit Hold'em Bounty (1Day)",
        "event_numbers": ["09", "11", "13", "15", "21", "22", "23", "25", "60", "61", "62", "64"],
        "start_time": "5:10 PM",
        "chips": 25000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + Break (9:40 PM)",
        "late_reg_time": "21:40",
        "guarantee_text": "Guarantee: $8,000 (prize pool + total bounties)",
        "guarantee_basis": "prize pool + total bounties",
        "fee_excerpt": "$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $160 of every $200 Buy In.",
        "fee": 40, "pool_per_entry": 160,
        "pays_pct": "12.5",
        "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "Players receive $50 bounty for each player they eliminate from the tournament.",
        "bounty_amount": 50,
        "single_entry": "not_stated",
        "re_entry": "not_stated",
        "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "",
    },
    {
        "sheet": 4,  # CORRECTED 2026-11-17: see notes
        "doc_title": "$600 No Limit Hold'em (Event 59)",
        "event_numbers": ["59"],
        "start_time": "11:10 AM",
        "chips": 40000,
        "level_min": "40",
        "late_reg_text": "Late Registration: 9 levels + Break (5:55 PM)",
        "late_reg_time": "17:55",
        "guarantee_text": "Guarantee: $150,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$95 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $505 of every $600 Buy In.",
        "fee": 95, "pool_per_entry": 505,
        "pays_pct": None,
        "pays_excerpt": "",
        "bounty_excerpt": "",
        "bounty_amount": None,
        "single_entry": "not_stated",
        "re_entry": "explicit_yes",
        "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Rake discount: $20 off house fees on Day 1A if registered before 11:10 a.m. "
                 "($580 total instead of $600). Flight days: A+B+C at 11:10 AM, Day 2 at 11:00 AM.",
    },
    {
        "sheet": 5,
        "doc_title": "$300 No Limit Hold'em (1Day)",
        "event_numbers": ["02", "12"],
        "start_time": "11:10 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 10 levels + Break (~ 4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $10,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$58 of the $300 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $242 of every $300 Buy In.",
        "fee": 58, "pool_per_entry": 242,
        "pays_pct": "12.5",
        "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "",
    },
    {
        "sheet": 7,
        "doc_title": "$600 No Limit Hold'em (1Day)",
        "event_numbers": ["14", "28", "63"],
        "start_time": "11:10 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 10 levels + Break (~ 4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $30,000 for Event #14 and #63; $40,000 for Event #28",
        "guarantee_basis": "prize pool",
        "per_event_guarantee": {"14": 30000, "28": 40000, "63": 30000},
        "fee_excerpt": "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $510 of every $600 Buy In.",
        "fee": 90, "pool_per_entry": 510,
        "pays_pct": "12.5",
        "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "",
    },
    {
        "sheet": 10,  # CORRECTED 2026-11-17: see notes
        "doc_title": "$300 No Limit Hold'em (Event 01)",
        "event_numbers": ["01"],
        "start_time": "11:10 AM",
        "chips": 30000,
        "level_min": "40",
        "late_reg_text": "Late Registration: 6 levels + Break (~ 3:40 PM)",
        "late_reg_time": "15:40",
        "guarantee_text": "Guarantee: $75,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$60 of the $300 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $240 of every $300 Buy In.",
        "fee": 60, "pool_per_entry": 240,
        "pays_pct": None,
        "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated",
        "re_entry": "explicit_yes",
        "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Flight days: A and C at 11:10 AM (this sheet), B and D at 5:10 PM (sheet 9). "
                 "Day 2 resumes at 12:00 PM.",
    },
    {
        "sheet": 11,
        "doc_title": "$600 No Limit Hold'em Bounty (1Day)",
        "event_numbers": ["16", "30", "54"],
        "start_time": "11:10 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 10 levels + Break (4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $30,000 (prize pool + total bounties) Event #16; "
                          "$40,000 Event #30; $50,000 Event #54",
        "guarantee_basis": "prize pool + total bounties",
        "per_event_guarantee": {"16": 30000, "30": 40000, "54": 50000},
        "fee_excerpt": "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $510 of every $600 Buy In.",
        "fee": 90, "pool_per_entry": 510,
        "pays_pct": "12.5",
        "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "Players receive $200 Bounty for each player they eliminate from the "
                          "tournament. Once we reach the money (posted payouts) - players receive a "
                          "$500 Bounty for each player they eliminate from the tournament.",
        "bounty_amount": 200,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "",
    },
    {
        "sheet": 12,  # CORRECTED 2026-11-17: see notes
        "doc_title": "$800 No Limit Hold'em (Event 26, flights A/C/E)",
        "event_numbers": ["26"],
        "start_time": "11:10 AM",
        "chips": 40000,
        "level_min": "40",
        "late_reg_text": "Late Registration: 6 levels + Break (~ 3:40 PM)",
        "late_reg_time": "15:40",
        "guarantee_text": "Guarantee: $500,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$110 of the $800 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $690 of every $800 Buy In.",
        "fee": 110, "pool_per_entry": 690,
        "pays_pct": None,
        "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated",
        "re_entry": "explicit_yes",
        "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Six flights A-F; this sheet covers A, C, E (11:10 AM). Flights B, D, F (5:10 PM) "
                 "use sheets 13/14. Day 2 resumes at 12:00 PM.",
    },
    {
        "sheet": 15,
        "doc_title": "$300 No Limit Hold'em Bounty (1Day)",
        "event_numbers": ["29", "31", "34", "38", "42", "50", "51", "53", "55"],
        "start_time": "5:10 PM",
        "chips": 25000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + Break (9:40 PM)",
        "late_reg_time": "21:40",
        "guarantee_text": "Guarantee: $15,000 (prize pool + total bounties)",
        "guarantee_basis": "prize pool + total bounties",
        "fee_excerpt": "$50 of the $300 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $250 of every $300 Buy In.",
        "fee": 50, "pool_per_entry": 250,
        "pays_pct": "12.5",
        "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "Players receive $100 bounty for each player they eliminate from the tournament.",
        "bounty_amount": 100,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Rule 10: the $15,000 guarantee 'consists of the actual prize pool plus the total "
                 "amount of $100 bounties that are awarded'.",
    },
    {
        "sheet": 16,
        "doc_title": "$800 No Limit Hold'em Bounty (1Day)",
        "event_numbers": ["36"],
        "start_time": "11:10 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 10 levels + Break (4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $75,000 (prize pool + total bounties)",
        "guarantee_basis": "prize pool + total bounties",
        "fee_excerpt": "$100 of the $800 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $700 of every $800 Buy In.",
        "fee": 100, "pool_per_entry": 700,
        "pays_pct": "12.5",
        "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "Players receive $200 Bounty for each player they eliminate from the "
                          "tournament. Once we reach the money (posted payouts) - players receive a "
                          "$500 Bounty for each player they eliminate from the tournament.",
        "bounty_amount": 200,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "",
    },
    {
        "sheet": 18,
        "doc_title": "$200 No Limit Hold'em (1Day) RaceDay Stack",
        "event_numbers": ["03", "04", "05"],
        "start_time": "10:10 AM",
        "chips": 30000,
        "level_min": "20/15",
        "late_reg_text": "Late Registration: 6 levels + Break (~ 12:25 PM)",
        "late_reg_time": "12:25",
        "guarantee_text": "",
        "guarantee_basis": "no guarantee printed",
        "fee_excerpt": "$35 of the $200 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $165 of every $200 Buy In.",
        "fee": 35, "pool_per_entry": 165,
        "pays_pct": "12.5",
        "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Levels 1-6 are 20 minutes and levels 7-28 are 15 minutes. No guaranteed prize "
                 "pool is printed on this sheet; the official schedule page prints none either.",
    },
    {
        "sheet": 21,  # CORRECTED 2026-11-17: see notes
        "doc_title": "$2,200 No Limit Hold'em PokerAtlas Championship Title Event (Event 47)",
        "event_numbers": ["47"],
        "start_time": "10:10 AM",
        "chips": 40000,
        "level_min": "40",
        "late_reg_text": "Late Registration: 9 levels + Break (~ 4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $1,000,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$225 of the $2,200 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $1,975 of every $2,200 Buy In.",
        "fee": 225, "pool_per_entry": 1975,
        "pays_pct": None,
        "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated",
        "re_entry": "explicit_yes",
        "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Day 1A at 10:10 AM (this sheet); Day 1B at 6:10 PM (sheet 37). Day 2 at 1:00 PM, "
                 "Day 3 at 11:00 AM.",
    },
    {
        "sheet": 34,
        "doc_title": "$1,100 No Limit Hold'em (1Day) Progressive Knock-Out Bounty",
        "event_numbers": ["52"],
        "start_time": "11:10 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 10 levels + Break (4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $75,000 (prize pool + total bounties)",
        "guarantee_basis": "prize pool + total bounties",
        "fee_excerpt": "$130 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $970 of every $1,100 Buy In.",
        "fee": 130, "pool_per_entry": 970,
        "pays_pct": "12.5",
        "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "Players start the event as a $200 bounty. For each player they eliminate "
                          "from the tournament, they will receive 1/2 of the other players bounty to "
                          "keep as prize money...",
        "bounty_amount": 200,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Progressive knockout: half of each bounty is kept, half is added to the winner's own bounty.",
    },

    # ---------------------------------------------------------------- 2026-11-17 evening pass
    # The 25 sheets below were read after the first 12. They are transcribed the same way.
    {
        "sheet": 2,
        "doc_title": "$400 No Limit Hold'em",
        "event_numbers": ["07"],
        "start_time": "11:10 AM (Day A+B) with Day 2 @ 11:00 AM",
        "chips": 40000,
        "level_min": "40",
        "late_reg_text": "Late Registration: 9 levels + Break (5:55 PM)",
        "late_reg_time": "17:55",
        "guarantee_text": "Guarantee: $75,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$70 of the $400 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $330 of every $400 Buy In.",
        "fee": 70, "pool_per_entry": 330,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "explicit_no", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Two starting flights on one sheet (1A and 1B). Day 2 at 11:00 AM. No payout "
                 "percentage line is printed; the sheet's 12.5% figure is the flight stop rule, "
                 "not a payout rule, so pays_pct is left blank.",
    },
    {
        "sheet": 3,
        "doc_title": "$400 No Limit Hold'em",
        "event_numbers": ["19"],
        "start_time": "11:10 AM (Day A+B+C) with Day 2 @ 11:00 AM",
        "chips": 40000,
        "level_min": "40",
        "late_reg_text": "Late Registration: 9 levels + Break (5:55 PM)",
        "late_reg_time": "17:55",
        "guarantee_text": "Guarantee: $75,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$70 of the $400 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $330 of every $400 Buy In.",
        "fee": 70, "pool_per_entry": 330,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "explicit_no", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Three starting flights on one sheet (1A, 1B, 1C). Day 2 at 11:00 AM. No payout "
                 "percentage line printed.",
    },
    {
        "sheet": 6,
        "doc_title": "$400 No Limit Hold'em (1Day)",
        "event_numbers": ["10"],
        "start_time": "11:10 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 10 levels + Break (~ 4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $15,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$65 of the $400 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $335 of every $400 Buy In.",
        "fee": 65, "pool_per_entry": 335,
        "pays_pct": "12.5", "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "",
    },
    {
        "sheet": 8,
        "doc_title": "$200 No Limit Hold'em Valuetown Bounty (1Day)",
        "event_numbers": ["18", "58"],
        "start_time": "5:10 PM",
        "chips": 25000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + Break (9:40 PM)",
        "late_reg_time": "21:40",
        "guarantee_text": "Guarantee: $20,000 (prize pool + total bounties)",
        "guarantee_basis": "prize pool + total bounties",
        "fee_excerpt": "$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $160 of every $200 Buy In.",
        "fee": 40, "pool_per_entry": 160,
        "pays_pct": "12.5", "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "Players receive $50 bounty for each player they eliminate from the "
                          "tournament. If two or more players eliminate another player with the "
                          "exact same hand, the $50 bounty will be split equally amongst all "
                          "winning hands.",
        "bounty_amount": 50,
        "single_entry": "not_stated", "re_entry": "explicit_yes", "add_on": "not_stated",
        "entry_excerpt": "PokerAtlas PRO players will receive a twenty ($20) rake discount on their "
                         "initial $200 buy in only, for a total buy in of $180 instead of $200. "
                         "... All subsequent buy in's after the initial buy in will be $200.",
        "notes": "Rule 7 contemplates more than one buy-in for this event ('initial buy in only', "
                 "'all subsequent buy in's'), so this is NOT a single-entry event. Rule 11 states "
                 "the $20,000 is 'the actual prize pool plus the total amount of $50 bounties'. "
                 "The PokerAtlas PRO discount makes the first entry $180, but only if the discount "
                 "is claimed in the PokerAtlas app at the cage.",
    },
    {
        "sheet": 9,
        "doc_title": "$300 No Limit Hold'em",
        "event_numbers": ["01"],
        "start_time": "5:10 PM (Day B+D) with Day 2 @ 12:00 PM",
        "chips": 30000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 6 levels + Break (~ 8:40 PM)",
        "late_reg_time": "20:40",
        "guarantee_text": "Guarantee: $75,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$60 of the $300 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $240 of every $300 Buy In.",
        "fee": 60, "pool_per_entry": 240,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "explicit_no", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Days B and D only. Sheet 10 carries the same event's Days A and C at 11:10 AM. "
                 "The two sheets print the same $75,000 guarantee for the same event, so the "
                 "guarantee is series-wide across flights, not four separate guarantees.",
    },
    {
        "sheet": 13,
        "doc_title": "$800 No Limit Hold'em",
        "event_numbers": ["26"],
        "start_time": "5:10 PM (Day B+D) with Day 2 @ 12:00 PM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 6 levels + Break (~ 8:40 PM)",
        "late_reg_time": "20:40",
        "guarantee_text": "Guarantee: $500,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$110 of the $800 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $690 of every $800 Buy In.",
        "fee": 110, "pool_per_entry": 690,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "explicit_no", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Days B and D only. THIS FLIGHT SET HAS A 30-MINUTE LEVEL, while sheet 12 covers "
                 "the same event's Days A, C and E at 40 minutes and sheet 14 covers Day F at 20 "
                 "minutes. Buying the 5:10 PM flight gets a faster structure than the 11:10 AM one "
                 "for the same $800. See flag FD-16.",
    },
    {
        "sheet": 14,
        "doc_title": "$800 No Limit Hold'em (Turbo)",
        "event_numbers": ["26"],
        "start_time": "5:10 PM (Day F, Turbo) with Day 2 @ 12:00 PM",
        "chips": 40000,
        "level_min": "20",
        "late_reg_text": "Late Registration: 6 levels + Break (~ 7:25 PM)",
        "late_reg_time": "19:25",
        "guarantee_text": "Guarantee: $500,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$110 of the $800 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $690 of every $800 Buy In.",
        "fee": 110, "pool_per_entry": 690,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "explicit_no", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Day F only, labelled Turbo on the sheet and on the schedule page. 20-minute "
                 "levels. Same $800 buy-in and same $500,000 guarantee as the other flights.",
    },
    {
        "sheet": 17,
        "doc_title": "$600 No Limit Hold'em Seniors (1Day)",
        "event_numbers": ["24", "32"],
        "start_time": "10:10 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 10 levels + Break (~ 3:55 PM)",
        "late_reg_time": "15:55",
        "guarantee_text": "Guarantee: $40,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $510 of every $600 Buy In.",
        "fee": 90, "pool_per_entry": 510,
        "pays_pct": "15", "pays_excerpt": "This event pays 15% of the field",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Age-restricted: must be 50+. The sheet prints the consequence of ignoring that: "
                 "'Any player who buys into this event that is not 50+ years of age will not be "
                 "entitled to any prize money or a refund of their buy in.' Pays 15%, not the 12.5% "
                 "used almost everywhere else in this series, so it is not payout-comparable.",
    },
    {
        "sheet": 19,
        "doc_title": "$100 NLH LIPS Ladies (1Day)",
        "event_numbers": ["33", "37"],
        "start_time": "4:10 PM",
        "chips": 20000,
        "level_min": "20",
        "late_reg_text": "Late Registration: 6 levels + Break (~6:25 PM)",
        "late_reg_time": "18:25",
        "guarantee_text": "Guarantee: 2 Seats",
        "guarantee_basis": "seats (satellite)",
        "fee_excerpt": "$20 of the $100 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $80 of every $100 Buy In.",
        "fee": 20, "pool_per_entry": 80,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "SATELITTE, not a cash event. The guarantee is '2 Seats', and rule 8 says all "
                 "prizes are direct entry into the $800 LIPS Ladies Event #39 with odd monies as "
                 "one additional payout. Open to female players 21+. There is no dollar prize pool "
                 "to divide, so this row can never carry a GTD-per-entry ratio.",
    },
    {
        "sheet": 20,
        "doc_title": "$1,100 No Limit Hold'em Seniors",
        "event_numbers": ["49"],
        "start_time": "10:10 AM (Day A+B) with Day 2 @ 10:00 AM",
        "chips": 40000,
        "level_min": "40",
        "late_reg_text": "Late Registration: 9 levels + Break (~ 4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $300,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$140 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $960 of every $1,100 Buy In.",
        "fee": 140, "pool_per_entry": 960,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "explicit_no", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Age-restricted: must be 50+. Two flights (1A, 1B), Day 2 at 10:00 AM. Rule 3 "
                 "says each flight stops at 'approximately 15% of the field remaining', but no "
                 "payout percentage line is printed, so pays_pct is blank rather than copied from "
                 "that flight-stop figure.",
    },
    {
        "sheet": 22,
        "doc_title": "$300 Pot Limit Omaha Double Board Bomb Pot (1Day)",
        "event_numbers": ["20"],
        "start_time": "12:10 PM",
        "chips": 30000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + break (~ 4:40 PM)",
        "late_reg_time": "16:40",
        "guarantee_text": "Guarantee: $10,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$58 of the $300 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $242 of every $300 Buy In.",
        "fee": 58, "pool_per_entry": 242,
        "pays_pct": "12.5", "pays_excerpt": "This event will play eight (8) handed and pay 12.5% "
                                            "of the field.",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Different game entirely: Pot Limit Omaha, double board bomb pot, eight-handed. "
                 "Every player antes every hand and action starts on the flop; the top and bottom "
                 "board split the pot. Not Hold'em and not comparable with the NLH rows.",
    },
    {
        "sheet": 23,
        "doc_title": "$600 Pot Limit Omaha Double Board Bomb Pot (1Day)",
        "event_numbers": ["57"],
        "start_time": "12:10 PM",
        "chips": 30000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + break (~ 4:40 PM)",
        "late_reg_time": "16:40",
        "guarantee_text": "Guarantee: $25,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $510 of every $600 Buy In.",
        "fee": 90, "pool_per_entry": 510,
        "pays_pct": "12.5", "pays_excerpt": "This event will play eight (8) handed and pay 12.5% "
                                            "of the field.",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Pot Limit Omaha double board bomb pot, eight-handed. Same game as sheet 22 at "
                 "twice the buy-in.",
    },
    {
        "sheet": 24,
        "doc_title": "$260 No Limit Hold'em (1Day) Milestone Satellite",
        "event_numbers": ["41", "44"],
        "start_time": "4:10 PM",
        "chips": 20000,
        "level_min": "20",
        "late_reg_text": "Late Registration: 6 levels + Break (~6:25 PM)",
        "late_reg_time": "18:25",
        "guarantee_text": "Guarantee: 2 Seats",
        "guarantee_basis": "seats (satellite)",
        "fee_excerpt": "$40 of the $260 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $220 of every $260 Buy In.",
        "fee": 40, "pool_per_entry": 220,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "SATELITTE. Prizes are direct entry into the $2,200 PokerAtlas Championship "
                 "Title Event #47, plus odd monies as one payout. A player reaching 200,000 chips "
                 "('The Milestone') is paid immediately and removed from play. No dollar prize "
                 "pool, so no GTD-per-entry ratio.",
    },
    {
        "sheet": 25,
        "doc_title": "$260 No Limit Hold'em Turbo (1Day) Milestone Satellite",
        "event_numbers": ["45", "46", "48"],
        "start_time": "8:10 PM (45), 9:10 AM (46), 12:10 PM (48)",
        "chips": 20000,
        "level_min": "15",
        "late_reg_text": "Late Registration: 6 levels",
        "late_reg_time": None,
        "guarantee_text": "Guarantee: 2 Seats",
        "guarantee_basis": "seats (satellite)",
        "fee_excerpt": "$35 of the $260 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $225 of every $260 Buy In.",
        "fee": 35, "pool_per_entry": 225,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "SATELITTE. Three different events on one sheet, each with its own start time: "
                 "#45 at 8:10 PM, #46 at 9:10 AM, #48 at 12:10 PM. 15-minute levels. This sheet "
                 "prints no late-registration clock time, only '6 levels', so the close time is "
                 "left blank rather than calculated.",
    },
    {
        "sheet": 26,
        "doc_title": "$400 Pot Limit Omaha Bounty (1Day)",
        "event_numbers": ["17"],
        "start_time": "12:10 PM",
        "chips": 30000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + break (~ 4:40 PM)",
        "late_reg_time": "16:40",
        "guarantee_text": "Guarantee: $15,000 (prize pool + total bounties)",
        "guarantee_basis": "prize pool + total bounties",
        "fee_excerpt": "$60 of the $400 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $340 of every $400 Buy In.",
        "fee": 60, "pool_per_entry": 340,
        "pays_pct": "12.5", "pays_excerpt": "This event will play eight (8) handed and pay 12.5% "
                                            "of the field",
        "bounty_excerpt": "Players receive a $100 Bounty for each player they eliminate from the "
                          "tournament. ... The winner of the event will keep their own bounty chip.",
        "bounty_amount": 100,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Pot Limit Omaha, eight-handed, with a $100 per-elimination bounty. Rule 10: the "
                 "$15,000 consists of the actual prize money plus the total amount of $100 "
                 "bounties awarded. Bounty-inclusive, so no GTD ratio. This sheet has its own "
                 "ante rule: the ante is not part of the pre-flop calculation but counts toward "
                 "the pot post-flop, and the blind is posted before the ante.",
    },
    {
        "sheet": 27,
        "doc_title": "$600 Pot Limit Omaha Bounty (1Day)",
        "event_numbers": ["40"],
        "start_time": "12:10 PM",
        "chips": 30000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + break (~ 4:40 PM)",
        "late_reg_time": "16:40",
        "guarantee_text": "Guarantee: $25,000 (prize pool + total bounties)",
        "guarantee_basis": "prize pool + total bounties",
        "fee_excerpt": "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $510 of every $600 Buy In.",
        "fee": 90, "pool_per_entry": 510,
        "pays_pct": "12.5", "pays_excerpt": "This event will play eight (8) handed and pay 12.5% "
                                            "of the field",
        "bounty_excerpt": "Players receive a $200 Bounty for each player they eliminate from the "
                          "tournament. ... The winner of the event will keep their own bounty chip.",
        "bounty_amount": 200,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Pot Limit Omaha bounty, eight-handed. $25,000 includes total bounties awarded, "
                 "so no GTD ratio.",
    },
    {
        "sheet": 28,
        "doc_title": "$600 BIG O (1Day)",
        "event_numbers": ["27"],
        "start_time": "12:10 PM",
        "chips": 30000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + break (~ 4:40 PM)",
        "late_reg_time": "16:40",
        "guarantee_text": "Guarantee: $25,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                       "Prize pool consists of $510 of every $600 Buy In.",
        "fee": 90, "pool_per_entry": 510,
        "pays_pct": "12.5", "pays_excerpt": "This event will play eight (8) handed and pay 12.5% "
                                            "of the field",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "BIG O (five-card Omaha hi-lo), eight-handed. The only sheet in the series whose "
                 "title is not a Hold'em or four-card PLO event.",
    },
    {
        "sheet": 29,
        "doc_title": "$200 No Limit Hold'em (1Day)",
        "event_numbers": ["06"],
        "start_time": "11:10 AM",
        "chips": 30000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + Break (~ 3:40 PM)",
        "late_reg_time": "15:40",
        "guarantee_text": "no guarantee line is printed on this sheet",
        "guarantee_basis": "no guarantee printed",
        "fee_excerpt": "$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $160 of every $200 Buy In.",
        "fee": 40, "pool_per_entry": 160,
        "pays_pct": "12.5", "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "NOTABLE: this sheet carries no Guarantee line at all, unlike the other 36. The "
                 "event therefore has a published buy-in and a published fee but no published "
                 "guarantee, and it is the only such row in the series.",
    },
    {
        "sheet": 30,
        "doc_title": "$200 No Limit Hold'em Progressive Knock-Out Bounty (1Day)",
        "event_numbers": ["08"],
        "start_time": "5:10 PM",
        "chips": 25000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + Break (9:40 PM)",
        "late_reg_time": "21:40",
        "guarantee_text": "Guarantee: $8,000 (prize pool + total bounties)",
        "guarantee_basis": "prize pool + total bounties",
        "fee_excerpt": "$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $160 of every $200 Buy In.",
        "fee": 40, "pool_per_entry": 160,
        "pays_pct": "12.5", "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "Players start the event as a $50 bounty. For each player they eliminate "
                          "from the tournament, they will receive half of the other players bounty "
                          "to keep as prize money, and the other half of the bounty will then be "
                          "calculated into their own bounty elimination prize amount.",
        "bounty_amount": 50,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Progressive knockout: half of an eliminated player's bounty is kept, half is "
                 "added to the eliminator's own bounty. $8,000 includes total bounty prize money.",
    },
    {
        "sheet": 31,
        "doc_title": "$600 No Limit Hold'em LIPS Poker Jingle Tag Team Event (1Day)",
        "event_numbers": ["35"],
        "start_time": "10:10 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 8 levels + Break (~ 2:40 PM)",
        "late_reg_time": "14:40",
        "guarantee_text": "Guarantee: $10,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$80 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                       "$10 of the $600 Buy In will be withheld as a flat fee for Vegas Connected, "
                       "INC, DBA Ladies International Poker Series (LIPS). Prize pool consists of "
                       "$510 of every $600 Buy In.",
        "fee": 90, "pool_per_entry": 510,
        "pays_pct": "12.5", "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "TAG TEAM event: teams rotate players every level and a team that fails to switch "
                 "is disqualified. $600 buys a team, not a seat. Teams must be female/female or "
                 "female/male. IMPORTANT: fee is recorded as $90 because $80 is house fees and a "
                 "further $10 is a flat fee for a third party (LIPS/Vegas Connected); $80 + $10 + "
                 "$510 prize pool = $600. See flag FD-17.",
    },
    {
        "sheet": 32,
        "doc_title": "$800 NLH LIPS Ladies (2Day)",
        "event_numbers": ["39"],
        "start_time": "10:10 AM Dec 10, with Day 2 Dec 11 @ 10:00 AM",
        "chips": 40000,
        "level_min": "40",
        "late_reg_text": "Late Registration: 9 levels + Break (~ 4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $40,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$90 of the $800 Buy-In is withheld for house fees (Rake + Staff). "
                       "$20 of the $800 Buy In will be withheld as a flat fee for Vegas Connected, "
                       "INC, DBA Ladies International Poker Series (LIPS). Prize pool consists of "
                       "$690 of every $800 Buy In.",
        "fee": 110, "pool_per_entry": 690,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "LIPS Women in Poker main event, open to female players 21+. One starting day "
                 "(Dec 10) and Day 2 (Dec 11). The final table of seven is played at approximately "
                 "7:00 PM on Dec 11 and streamed by PokerGO, which is why the schedule carries a "
                 "third Dec 11 row at 7:00 PM. Fee is $110: $90 house plus a $20 third-party LIPS "
                 "fee. No payout percentage line is printed.",
    },
    {
        "sheet": 33,
        "doc_title": "$600 No Limit Hold'em LIPS Kings and Queens Bounty (1Day)",
        "event_numbers": ["43"],
        "start_time": "11:10 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 10 levels + Break (4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $30,000 (prize pool + total bounties)",
        "guarantee_basis": "prize pool + total bounties",
        "fee_excerpt": "$80 of the $600 Buy-In is withheld for house fees (Rake + Staff). "
                       "$10 of the $600 Buy In will be withheld as a flat fee for Vegas Connected, "
                       "INC, DBA Ladies International Poker Series (LIPS). Prize pool consists of "
                       "$510 of every $600 Buy In.",
        "fee": 90, "pool_per_entry": 510,
        "pays_pct": "12.5", "pays_excerpt": "This event pays 12.5% of the field",
        "bounty_excerpt": "Players receive $200 Bounty for each player they eliminate from the "
                          "tournament. The player who wins the event will keep their own bounty.",
        "bounty_amount": 200,
        "single_entry": "not_stated", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Read in full: no re-entry, rebuy, add-on or entry-limit clause is printed.",
        "notes": "Open to all players, but trophies go to the last King (male) and last Queen "
                 "(female) standing. $200 bounty, and the $30,000 includes total bounties awarded. "
                 "Fee is $90: $80 house plus a $10 third-party LIPS fee.",
    },
    {
        "sheet": 35,
        "doc_title": "$1,100 No Limit Hold'em",
        "event_numbers": ["56"],
        "start_time": "10:10 AM (Day A+C+E) with Day 2 @ 11:00 AM",
        "chips": 40000,
        "level_min": "40",
        "late_reg_text": "Late Registration: 9 levels + Break (~ 4:55 PM)",
        "late_reg_time": "16:55",
        "guarantee_text": "Guarantee: $500,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$140 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). The "
                       "prize pool consists of $960 of every $1,100 Buy In. On Day 1A, players who "
                       "register before the start of the event (10:10 a.m.) will receive a forty "
                       "($40) discount on house fees for a total buy in of $1,060 instead of "
                       "$1,100. $40 discounts will no longer be applied once the event has "
                       "started and played one hand.",
        "fee": 140, "pool_per_entry": 960,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "explicit_no", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Days A, C and E at 40-minute levels. Day 1A pre-registration discount: $40 off "
                 "house fees, $1,060 total, only before 10:10 a.m. and only until one hand has "
                 "been played. A $1,100 entry is therefore $1,060 or $1,100 depending on when and "
                 "how you register. See flag FD-18.",
    },
    {
        "sheet": 36,
        "doc_title": "$1,100 No Limit Hold'em",
        "event_numbers": ["56"],
        "start_time": "6:10 PM (Day B+D) with Day 2 @ 11:00 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 9 levels + Break (~ 11:10 PM)",
        "late_reg_time": "23:10",
        "guarantee_text": "Guarantee: $500,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$140 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). The "
                       "prize pool consists of $960 of every $1,100 Buy In. On Day 1B, players who "
                       "register before the start of the event (6:10 PM.) will receive a forty "
                       "($40) discount on house fees for a total buy in of $1,060 instead of "
                       "$1,100.",
        "fee": 140, "pool_per_entry": 960,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "explicit_no", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Days B and D at 6:10 PM with 30-MINUTE levels, while sheet 35 gives the same "
                 "event's Days A, C and E 40-minute levels. Same $1,100 buy-in, materially faster "
                 "structure, and late registration runs to about 11:10 PM. Day 1B pre-registration "
                 "discount: $40 off, $1,060 total. See flags FD-16 and FD-18.",
    },
    {
        "sheet": 37,
        "doc_title": "$2,200 No Limit Hold'em PokerAtlas Championship Title Event",
        "event_numbers": ["47"],
        "start_time": "6:10 PM (Day 1B) with Day 2 @ 1:00 PM and Day 3 @ 11:00 AM",
        "chips": 40000,
        "level_min": "30",
        "late_reg_text": "Late Registration: 9 levels + Break (~ 11:10 PM)",
        "late_reg_time": "23:10",
        "guarantee_text": "Guarantee: $1,000,000",
        "guarantee_basis": "prize pool",
        "fee_excerpt": "$225 of the $2,200 Buy-In is withheld for house fees (Rake + Staff). "
                       "The prize pool consists of $1,975 of every $2,200 Buy In.",
        "fee": 225, "pool_per_entry": 1975,
        "pays_pct": None, "pays_excerpt": "",
        "bounty_excerpt": "", "bounty_amount": None,
        "single_entry": "explicit_no", "re_entry": "not_stated", "add_on": "not_stated",
        "entry_excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.",
        "notes": "Day 1B at 6:10 PM with 30-minute levels; sheet 21 covers Day 1A at 10:10 AM with "
                 "40-minute levels. This is the only three-day event in the series: Day 2 at "
                 "1:00 PM, Day 3 at 11:00 AM for a PokerGO-streamed final table. No payout "
                 "percentage line is printed.",
    },
]

UNREAD_SHEETS = []   # all 37 sheets have now been read in full


def sheet_url(n):
    return SHEET_URL % n


def by_number():
    return {s["sheet"]: s for s in SHEETS}


if __name__ == "__main__":
    n_events = sum(len(s["event_numbers"]) for s in SHEETS)
    print("sheets read      :", len(SHEETS))
    print("event numbers    :", n_events, "(distinct rows differ: flights repeat a number)")
    print("sheets not read  :", len(UNREAD_SHEETS), UNREAD_SHEETS)
