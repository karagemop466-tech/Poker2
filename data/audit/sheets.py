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
        "sheet": 4,
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
        "single_entry": "explicit_no",
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
        "sheet": 10,
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
        "single_entry": "explicit_no",
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
        "sheet": 12,
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
        "single_entry": "explicit_no",
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
        "sheet": 21,
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
        "single_entry": "explicit_no",
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
]

# Sheets the official schedule page links to that have NOT been read in this pass.
# Listed so the gap is countable and citable rather than invisible.
UNREAD_SHEETS = [2, 3, 6, 8, 9, 13, 14, 17, 19, 20, 22, 23, 24, 25, 26, 27, 28,
                 29, 30, 31, 32, 33, 35, 36, 37]


def sheet_url(n):
    return SHEET_URL % n


def by_number():
    return {s["sheet"]: s for s in SHEETS}


if __name__ == "__main__":
    n_events = sum(len(s["event_numbers"]) for s in SHEETS)
    print("sheets read      :", len(SHEETS))
    print("event numbers    :", n_events, "(distinct rows differ: flights repeat a number)")
    print("sheets not read  :", len(UNREAD_SHEETS), UNREAD_SHEETS)
