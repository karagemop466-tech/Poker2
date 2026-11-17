#!/usr/bin/env python3
"""Build data/structure-sheets.json — the verified transcription of the 37 official
Venetian DeepStack Extravaganza IV structure sheets.

Every value in this file was read off the official PDF whose URL is in the row on
2026-11-17 (fetch of the live PDF). `reg_close` is the clock time the sheet itself
prints next to "Late Registration"; when the sheet prints only a level count and no
clock time the field is left empty (null) rather than computed.

Event numbers are attached from the official DSE IV schedule page, not invented:
the schedule row links each event to its structure sheet.

Run:  python3 scripts/build_structure_registry.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/"
        "2026/structures/dse_nov_2026-structure_%d.pdf")
SCHEDULE = ("https://www.venetianlasvegas.com/resort/casino/poker/"
            "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
READ_ON = "2026-11-17"

# sheet -> transcript
#   title      : the heading printed on the sheet
#   start      : start time printed on the sheet (None = sheet prints none)
#   chips      : starting chips printed
#   level_min  : level duration printed (string, may cover several flights)
#   late_reg   : the "Late Registration:" line, verbatim
#   reg_close  : clock time printed next to the late-registration line, else None
#   fee, pool  : "$X of the $Y Buy-In is withheld ... pool consists of $Z"
#   gtd        : guarantee printed on the sheet, else None
#   has_flight_note : sheet prints the "may not play a subsequent flight" rule
#   entry_rule : verbatim wording, if the sheet prints any entry/re-entry mechanism
SHEETS = {
    1: dict(title="$200 No Limit Hold'em Bounty (1Day)", start="5:10 PM", chips=25000,
            level_min="30", late_reg="8 levels + Break (9:40 PM)", reg_close="21:40",
            fee=40, pool=160, gtd=8000, has_flight_note=False, entry_rule=None),
    2: dict(title="$400 No Limit Hold'em — Day A+B @ 11:10 AM with Day 2 @ 11:00 AM",
            start="11:10 AM", chips=40000, level_min="40",
            late_reg="9 levels + Break (5:55 PM)", reg_close="17:55",
            fee=70, pool=330, gtd=75000, has_flight_note=True,
            entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
    3: dict(title="$400 No Limit Hold'em — Day A+B+C @ 11:10 AM with Day 2 @ 11:00 AM",
            start="11:10 AM", chips=40000, level_min="40",
            late_reg="9 levels + Break (5:55 PM)", reg_close="17:55",
            fee=70, pool=330, gtd=75000, has_flight_note=True,
            entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
    4: dict(title="$600 No Limit Hold'em — Day A+B+C @ 11:10 AM with Day 2 @ 11:00 AM",
            start="11:10 AM", chips=40000, level_min="40",
            late_reg="9 levels + Break (5:55 PM)", reg_close="17:55",
            fee=95, pool=505, gtd=150000, has_flight_note=True,
            entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
    5: dict(title="$300 No Limit Hold'em (1Day)", start="11:10 AM", chips=40000,
            level_min="30", late_reg="10 levels + Break (~ 4:55 PM)", reg_close="16:55",
            fee=58, pool=242, gtd=10000, has_flight_note=False, entry_rule=None),
    6: dict(title="$400 No Limit Hold'em (1Day)", start="11:10 AM", chips=40000,
            level_min="30", late_reg="10 levels + Break (~ 4:55 PM)", reg_close="16:55",
            fee=65, pool=335, gtd=15000, has_flight_note=False, entry_rule=None),
    7: dict(title="$600 No Limit Hold'em (1Day)", start="11:10 AM", chips=40000,
            level_min="30", late_reg="10 levels + Break (~ 4:55 PM)", reg_close="16:55",
            fee=90, pool=510, gtd=None, has_flight_note=False, entry_rule=None,
            gtd_note="Sheet prints $30,000 for Events #14 and #63 and $40,000 for Event #28."),
    8: dict(title="$200 No Limit Hold'em Valuetown(TM) Bounty (1Day) — PokerAtlas PRO Member $20 Rake Discount",
            start="5:10 PM", chips=25000, level_min="30",
            late_reg="8 levels + Break (9:40 PM)", reg_close="21:40",
            fee=40, pool=160, gtd=20000, has_flight_note=False,
            entry_rule=("PokerAtlas PRO players will receive a twenty ($20) rake discount on their "
                        "initial $200 buy in only ... All subsequent buy in's after the initial buy in "
                        "will be $200.")),
    9: dict(title="$300 No Limit Hold'em — Day B+D @ 5:10 PM with Day 2 @ 12:00 PM",
            start="5:10 PM", chips=30000, level_min="30",
            late_reg="6 levels + Break (~ 8:40 PM)", reg_close="20:40",
            fee=60, pool=240, gtd=75000, has_flight_note=True,
            entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
    10: dict(title="$300 No Limit Hold'em — Day A+C @ 11:10 AM with Day 2 @ 12:00 PM",
             start="11:10 AM", chips=30000, level_min="40",
             late_reg="6 levels + Break (~ 3:40 PM)", reg_close="15:40",
             fee=60, pool=240, gtd=75000, has_flight_note=True,
             entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
    11: dict(title="$600 No Limit Hold'em Bounty (1Day)", start="11:10 AM", chips=40000,
             level_min="30", late_reg="10 levels + Break (4:55 PM)", reg_close="16:55",
             fee=90, pool=510, gtd=None, has_flight_note=False, entry_rule=None,
             gtd_note="Sheet prints $30,000 for Event #16, $40,000 for #30 and $50,000 for #54."),
    12: dict(title="$800 No Limit Hold'em — Day A+C+E @ 11:10 AM with Day 2 @ 12:00 PM",
             start="11:10 AM", chips=40000, level_min="40",
             late_reg="6 levels + Break (~ 3:40 PM)", reg_close="15:40",
             fee=110, pool=690, gtd=500000, has_flight_note=True,
             entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
    13: dict(title="$800 No Limit Hold'em — Day B+D @ 5:10 PM with Day 2 @ 12:00 PM",
             start="5:10 PM", chips=40000, level_min="30",
             late_reg="6 levels + Break (~ 8:40 PM)", reg_close="20:40",
             fee=110, pool=690, gtd=500000, has_flight_note=True,
             entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
    14: dict(title="$800 No Limit Hold'em — Day F (Turbo) @ 5:10 PM with Day 2 @ 12:00 PM",
             start="5:10 PM", chips=40000, level_min="20",
             late_reg="6 levels + Break (~ 7:25 PM)", reg_close="19:25",
             fee=110, pool=690, gtd=500000, has_flight_note=True,
             entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
    15: dict(title="$300 No Limit Hold'em Bounty (1Day)", start="5:10 PM", chips=25000,
             level_min="30", late_reg="8 levels + Break (9:40 PM)", reg_close="21:40",
             fee=50, pool=250, gtd=15000, has_flight_note=False, entry_rule=None),
    16: dict(title="$800 No Limit Hold'em Bounty (1Day)", start="11:10 AM", chips=40000,
             level_min="30", late_reg="10 levels + Break (4:55 PM)", reg_close="16:55",
             fee=100, pool=700, gtd=75000, has_flight_note=False, entry_rule=None),
    17: dict(title="$600 No Limit Hold'em Seniors (1Day) — must be 50+", start="10:10 AM",
             chips=40000, level_min="30", late_reg="10 levels + Break (~ 3:55 PM)",
             reg_close="15:55", fee=90, pool=510, gtd=40000, has_flight_note=False,
             entry_rule=None,
             eligibility="Must be 50+ years of age with a Venetian Rewards card; "
                         "a player who buys in under 50 forfeits prize money and the buy-in."),
    18: dict(title="$200 No Limit Hold'em (1Day) — RaceDay Stack", start="10:10 AM",
             chips=30000, level_min="20/15",
             late_reg="6 levels + Break (~ 12:25 PM)", reg_close="12:25",
             fee=35, pool=165, gtd=None, has_flight_note=False, entry_rule=None,
             gtd_note="Sheet prints no guarantee; the schedule calls it a satellite awarding 2 seats."),
    19: dict(title="$100 NLH LIPS Ladies (1Day) — Milestone Satellite to Event #39",
             start="4:10 PM", chips=20000, level_min="20",
             late_reg="6 levels + Break (~6:25 PM)", reg_close="18:25",
             fee=20, pool=80, gtd=None, has_flight_note=False,
             entry_rule=None, gtd_note="Guarantee: 2 seats (direct entry to Event #39).",
             eligibility="Open to female players, 21+, with a Venetian Rewards card."),
    20: dict(title="$1,100 No Limit Hold'em Seniors — Day A+B @ 10:10 AM with Day 2 @ 10:00 AM",
             start="10:10 AM", chips=40000, level_min="40",
             late_reg="9 levels + Break (~ 4:55 PM)", reg_close="16:55",
             fee=140, pool=960, gtd=300000, has_flight_note=True,
             entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight.",
             eligibility="Must be 50+ years of age; under-50 buy-ins forfeit prize money and the buy-in."),
    21: dict(title="$2,200 No Limit Hold'em PokerAtlas Championship Title Event — Day 1A @ 10:10 AM",
             start="10:10 AM", chips=40000, level_min="40",
             late_reg="9 levels + Break (~ 4:55 PM)", reg_close="16:55",
             fee=225, pool=1975, gtd=1000000, has_flight_note=True,
             entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
    22: dict(title="$300 Pot Limit Omaha Double Board Bomb Pot (1Day)", start="12:10 PM",
             chips=30000, level_min="30", late_reg="8 levels + break (~ 4:40 PM)",
             reg_close="16:40", fee=58, pool=242, gtd=10000, has_flight_note=False,
             entry_rule=None),
    23: dict(title="$600 Pot Limit Omaha Double Board Bomb Pot (1Day)", start="12:10 PM",
             chips=30000, level_min="30", late_reg="8 levels + break (~ 4:40 PM)",
             reg_close="16:40", fee=90, pool=510, gtd=25000, has_flight_note=False,
             entry_rule=None),
    24: dict(title="$260 No Limit Hold'em (1Day) — Milestone Satellite to Event #47",
             start="4:10 PM", chips=20000, level_min="20",
             late_reg="6 levels + Break (~6:25 PM)", reg_close="18:25",
             fee=40, pool=220, gtd=None, has_flight_note=False, entry_rule=None,
             gtd_note="Guarantee: 2 seats (direct entry to Event #47)."),
    25: dict(title="$260 No Limit Hold'em Turbo (1Day) — Milestone Satellite to Event #47",
             start="8:10 PM / 9:10 AM / 12:10 PM (Events 45 / 46 / 48)", chips=20000,
             level_min="15", late_reg="6 levels", reg_close=None,
             fee=35, pool=225, gtd=None, has_flight_note=False, entry_rule=None,
             gtd_note="Guarantee: 2 seats. Sheet prints no clock time for the close of registration."),
    26: dict(title="$400 Pot Limit Omaha Bounty (1Day)", start="12:10 PM", chips=30000,
             level_min="30", late_reg="8 levels + break (~ 4:40 PM)", reg_close="16:40",
             fee=60, pool=340, gtd=15000, has_flight_note=False, entry_rule=None),
    27: dict(title="$600 Pot Limit Omaha Bounty (1Day)", start="12:10 PM", chips=30000,
             level_min="30", late_reg="8 levels + break (~ 4:40 PM)", reg_close="16:40",
             fee=90, pool=510, gtd=25000, has_flight_note=False, entry_rule=None),
    28: dict(title="$600 BIG O (1Day)", start="12:10 PM", chips=30000, level_min="30",
             late_reg="8 levels + break (~ 4:40 PM)", reg_close="16:40",
             fee=90, pool=510, gtd=25000, has_flight_note=False, entry_rule=None),
    29: dict(title="$200 No Limit Hold'em (1Day)", start="11:10 AM", chips=30000,
             level_min="30", late_reg="8 levels + Break (~ 3:40 PM)", reg_close="15:40",
             fee=40, pool=160, gtd=None, has_flight_note=False, entry_rule=None,
             gtd_note="Sheet prints no guarantee (schedule: no guarantee stated)."),
    30: dict(title="$200 No Limit Hold'em (1Day) — Progressive Knock-Out Bounty (PKO)",
             start="5:10 PM", chips=25000, level_min="30",
             late_reg="8 levels + Break (9:40 PM)", reg_close="21:40",
             fee=40, pool=160, gtd=8000, has_flight_note=False, entry_rule=None),
    31: dict(title="$600 No Limit Hold'em (1Day) — LIPS Poker Jingle Tag Team",
             start="10:10 AM", chips=40000, level_min="30",
             late_reg="8 levels + Break (~ 2:40 PM)", reg_close="14:40",
             fee=90, pool=510, gtd=10000, has_flight_note=False, entry_rule=None,
             eligibility="Teams of female/female or female/male, 21+, with Venetian Rewards cards. "
                         "$10 of the $600 buy-in is withheld as a flat LIPS fee, so the sheet's own "
                         "figures are $80 house + $10 LIPS + $510 pool."),
    32: dict(title="$800 NLH LIPS Ladies (2Day) — Women in Poker Main Event",
             start="10:10 AM", chips=40000, level_min="40",
             late_reg="9 levels + Break (~ 4:55 PM)", reg_close="16:55",
             fee=110, pool=690, gtd=40000, has_flight_note=False, entry_rule=None,
             eligibility="Female, 21+, with a Venetian Rewards card. $20 of the $800 buy-in is "
                         "withheld as a flat LIPS fee, so the sheet's figures are $90 house + "
                         "$20 LIPS + $690 pool."),
    33: dict(title="$600 No Limit Hold'em LIPS (1Day) — Kings and Queens Bounty, open to all",
             start="11:10 AM", chips=40000, level_min="30",
             late_reg="10 levels + Break (4:55 PM)", reg_close="16:55",
             fee=90, pool=510, gtd=30000, has_flight_note=False, entry_rule=None,
             eligibility="$80 house + $10 LIPS flat fee + $510 pool on the sheet's own figures."),
    34: dict(title="$1,100 No Limit Hold'em (1Day) — Progressive Knock-Out Bounty (PKO)",
             start="11:10 AM", chips=40000, level_min="30",
             late_reg="10 levels + Break (4:55 PM)", reg_close="16:55",
             fee=130, pool=970, gtd=75000, has_flight_note=False, entry_rule=None),
    35: dict(title="$1,100 No Limit Hold'em — Day A+C+E @ 10:10 AM with Day 2 @ 11:00 AM",
             start="10:10 AM", chips=40000, level_min="40",
             late_reg="9 levels + Break (~ 4:55 PM)", reg_close="16:55",
             fee=140, pool=960, gtd=500000, has_flight_note=True,
             entry_rule=("Any player who bags chips for Day 2 may not play a subsequent flight. "
                         "On Day 1A, players who register before 10:10 a.m. pay $1,060 instead of "
                         "$1,100 (a $40 house-fee discount).")),
    36: dict(title="$1,100 No Limit Hold'em — Day B+D @ 6:10 PM with Day 2 @ 11:00 AM",
             start="6:10 PM", chips=40000, level_min="30",
             late_reg="9 levels + Break (~ 11:10 PM)", reg_close="23:10",
             fee=140, pool=960, gtd=500000, has_flight_note=True,
             entry_rule=("Any player who bags chips for Day 2 may not play a subsequent flight. "
                         "On Day 1B, players who register before 6:10 p.m. pay $1,060 instead of "
                         "$1,100 (a $40 house-fee discount).")),
    37: dict(title="$2,200 No Limit Hold'em PokerAtlas Championship Title Event — Day 1B @ 6:10 PM",
             start="6:10 PM", chips=40000, level_min="30",
             late_reg="9 levels + Break (~ 11:10 PM)", reg_close="23:10",
             fee=225, pool=1975, gtd=1000000, has_flight_note=True,
             entry_rule="Any player who bags chips for Day 2 may not play a subsequent flight."),
}


# sheet -> event numbers, taken from the official schedule page, which links each
# schedule row to its structure sheet. Verified 2026-11-17 against the live page.
EVENT_NUMBERS = {
    1: [9, 11, 13, 15, 21, 22, 23, 25, 60, 61, 62, 64], 2: [7], 3: [19], 4: [59],
    5: [2, 12], 6: [10], 7: [14, 28, 63], 8: [18, 58], 9: [1], 10: [1],
    11: [16, 30, 54], 12: [26], 13: [26], 14: [26],
    15: [29, 31, 34, 38, 42, 50, 51, 53, 55], 16: [36], 17: [24, 32], 18: [3, 4, 5],
    19: [33, 37], 20: [49], 21: [47], 22: [20], 23: [57], 24: [41, 44],
    25: [45, 46, 48], 26: [17], 27: [40], 28: [27], 29: [6], 30: [8], 31: [35],
    32: [39], 33: [43], 34: [52], 35: [56], 36: [56], 37: [47],
}


def main():
    # event numbers come from the official schedule page (sheet <- event mapping)
    path = os.path.join(ROOT, "data", "structure-sheets.json")
    events_by_sheet = dict(EVENT_NUMBERS)

    out = []
    for n in sorted(SHEETS):
        t = SHEETS[n]
        row = dict(sheet=n, url=BASE % n, retrieved=READ_ON)
        row.update({k: v for k, v in t.items()})
        row["events"] = events_by_sheet.get(n, [])
        # The sheet is "silent on re-entry" when it prints no re-entry/rebuy/add-on
        # mechanism at all and no multi-flight prohibition. Recorded as a fact about
        # the document, NOT as a published freezeout rule.
        row["prints_reentry_mechanism"] = bool(row.get("has_flight_note")) or bool(
            row.get("entry_rule") and "re-entry" in str(row.get("entry_rule")).lower())
        row["silent_on_reentry"] = not row["prints_reentry_mechanism"] and not row.get("has_flight_note")
        out.append(row)

    doc = dict(
        as_of=READ_ON,
        generated_by="scripts/build_structure_registry.py",
        coverage="All 37 structure sheets linked from the official DSE IV schedule page.",
        source=SCHEDULE,
        method=("Each PDF was fetched and read in full on 2026-11-17. Values below are copied "
                "from the sheet. reg_close is the clock time the sheet prints beside 'Late "
                "Registration'; where the sheet prints only a level count, reg_close is null "
                "and is never computed here."),
        sheets=out,
    )
    with open(path, "w") as f:
        json.dump(doc, f, indent=1, sort_keys=False)
    print("wrote %s with %d sheets" % (path, len(out)))


if __name__ == "__main__":
    main()
