"""
Single source of truth for the consolidated Las Vegas poker dashboard.

Every value in this module was read from an official property page, PDF or
structure sheet on 2026-11-16 (UTC). If a value could not be read from an
official source it is left as None and is shown blank + flagged on the site.

Run `python3 scripts/poker_data.py` to (re)write data/poker/*.json.
"""

import json
import os

RETRIEVED = "2026-11-16"

# ---------------------------------------------------------------------------
# SOURCES
# kind: official | official-editorial | third-party | routing
# ---------------------------------------------------------------------------
SOURCES = {
    # ---- The Venetian Resort ------------------------------------------------
    "V_SCHED_TABLE": dict(
        kind="official",
        publisher="The Venetian Resort Las Vegas",
        title="DeepStack Extravaganza IV — November 16 – December 23, 2026 (event schedule table)",
        url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
        used_for="Every date, start time, event number, event name, structure-PDF link and published guarantee in the Venetian rows.",
    ),
    "V_SCHED_PDF": dict(
        kind="official",
        publisher="The Venetian Resort Las Vegas",
        title="DSE IV 2026 printed schedule PDF (reg-closes, chips, level minutes)",
        url="https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf",
        used_for="Registration-close times, starting chips and level durations per Venetian event.",
    ),
    "V_SERIES": dict(
        kind="official",
        publisher="The Venetian Resort Las Vegas",
        title="DeepStack Poker Series overview (series dates and headline guarantees)",
        url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
        used_for="Series window (Nov 16 – Dec 23, 2026) and headline guarantee events.",
    ),
    "V_POKER": dict(
        kind="official",
        publisher="The Venetian Resort Las Vegas",
        title="Poker at The Venetian Resort (room location, hours, venue description)",
        url="https://www.venetianlasvegas.com/resort/casino/poker.html",
        used_for="Poker room is at The Palazzo, level 2, Grand Canal Shoppes; open 24 hours; 50 tables / 14,000 sq ft.",
    ),
    "V_RESORT_FEE": dict(
        kind="official",
        publisher="The Venetian Resort Las Vegas",
        title="Resort Fee",
        url="https://www.venetianlasvegas.com/resort/resort-fee.html",
        used_for="Daily resort fee of $55 plus tax per night and its inclusions.",
    ),
    "V_HOTEL_TC": dict(
        kind="official",
        publisher="The Venetian Resort Las Vegas",
        title="Hotel Terms and Conditions",
        url="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
        used_for="Clark County room tax of 13.38%, resort fee, parking fees, check-in/out times, deposit and cancellation terms.",
    ),
    "V_SUITE_RATES": dict(
        kind="official",
        publisher="The Venetian Resort Las Vegas",
        title="2026 Special Suite Rates — Poker Suite Rate Information Guide",
        url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
        used_for="Published poker starting rates ($119 and $209), $55 resort fee, qualifying-play requirement, 150-day booking window, EPOKR25 code.",
    ),
    # ---- Wynn / Encore ------------------------------------------------------
    "W_POKER": dict(
        kind="official",
        publisher="Wynn Las Vegas",
        title="Wynn Las Vegas Poker Room (series pages and daily tournament links)",
        url="https://www.wynnlasvegas.com/casino/poker",
        used_for="WPT World Championship dates (Nov 27 – Dec 21), daily-tournament description, and the official schedule/structure PDF links.",
    ),
    "W_WPT_SCHED": dict(
        kind="official",
        publisher="Wynn Las Vegas",
        title="WPT World Championship 2026 schedule PDF",
        url="https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf",
        used_for="Every Wynn WPT row: date, start time, event name, buy-in, guarantee, starting chips, level minutes.",
    ),
    "W_WPT_STRUCT": dict(
        kind="official",
        publisher="Wynn Las Vegas",
        title="WPT World Championship 2026 structures and event terms PDF",
        url="https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf",
        used_for="Per-event entry-fee breakdown and re-entry wording (e.g. $600 NLH '$510 prize pool + $65 tournament fee + $25 staff service charge', 'Unlimited re-entry ... until the start of level 9').",
    ),
    "W_DAILY_POSTER": dict(
        kind="official",
        publisher="Wynn Las Vegas",
        title="Wynn daily poker tournament poster PDF",
        url="https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf",
        used_for="Daily tournament grid: Mon–Thu $200 NLH 12pm $10K GTD, Fri $240 NLH Rebuy 12pm $40K GTD, Sat/Sun $200 NLH 12pm $25K GTD, nightly $160 NLH 6pm $10K GTD.",
    ),
    "W_DAILY_STRUCT": dict(
        kind="official",
        publisher="Wynn Las Vegas",
        title="Wynn daily poker tournament structures PDF",
        url="https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf",
        used_for="Daily event terms: fee splits, re-entry wording, rebuy/add-on mechanics, registration close levels.",
    ),
    "W_RESORT_INFO": dict(
        kind="official",
        publisher="Wynn Las Vegas",
        title="Resort Policies & Information",
        url="https://www.wynnlasvegas.com/about-us/resort-information",
        used_for="Daily resort fee of $55 plus tax; check-in 3 p.m. / check-out 12 p.m.; one night deposit.",
    ),
    # ---- Caesars Palace -----------------------------------------------------
    "C_DAILY_PDF": dict(
        kind="official",
        publisher="Caesars Palace Las Vegas",
        title="Daily No-Limit Texas Hold'em Tournament Schedule (2026 flyer)",
        url="https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf",
        used_for="Caesars Palace daily start times, buy-ins, $50 add-on, starting chips, level times, $1,000 guarantees, fee splits and re-entry rule.",
    ),
    "C_POKER": dict(
        kind="official",
        publisher="Caesars Palace",
        title="Caesars Palace casino / poker room page",
        url="https://www.caesars.com/caesars-palace/casino",
        used_for="Poker room open 24/7 with cash games and daily tournaments; link to the official daily flyer.",
    ),
    "C_STRIP_ARTICLE": dict(
        kind="official-editorial",
        publisher="Caesars Entertainment",
        title="Poker Tournaments in Las Vegas — Caesars Palace & Horseshoe (editorial article, 17 Jul 2026)",
        url="https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip",
        used_for="Horseshoe daily start times (9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m., 11 p.m.) and the 16-table Caesars Palace / 20-table Horseshoe room descriptions. Editorial page, not the room's own tournament flyer — flagged.",
    ),
    "H_POKER": dict(
        kind="official",
        publisher="Horseshoe Las Vegas",
        title="Horseshoe Las Vegas casino / Hall of Fame Poker Room",
        url="https://www.caesars.com/horseshoe-las-vegas/casino",
        used_for="Hall of Fame Poker Room: 20 tables, '6 exciting tournament times daily'. No buy-in, guarantee or entry rule published on the page.",
    ),
    # ---- Bellagio -----------------------------------------------------------
    "B_POKER": dict(
        kind="official",
        publisher="Bellagio Las Vegas",
        title="Bellagio Poker Room",
        url="https://bellagio.mgmresorts.com/en/casino/poker.html",
        used_for="Room location (north side of casino, next to sportsbook), weekly tournament links, nightly 6 PM PLO Double Bomb Pot, host phone 702.693.7291.",
    ),
    "B_FRI_PDF": dict(
        kind="official",
        publisher="Bellagio Las Vegas",
        title="Fridays | $600 NLH tournament structure",
        url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt9cf95b0e60ec253e/6af491a3a9851d75c40be840/mgm-bellagio-poker-fridays-$600-nlh.pdf",
        used_for="Friday 11:00 a.m. $600 NLH: 30,000 chips, 30-minute levels, fee split, re-entry through level 8, optional $40 staff gratuity for +15,000 chips.",
    ),
    "B_SAT_PDF": dict(
        kind="official",
        publisher="Bellagio Las Vegas",
        title="Saturdays | $1,000 NLH tournament structure",
        url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt6d47974bf5a7d9b6/6af491a391a6e8e4230c9e07/mgm-bellagio-poker-saturdays-$1000-nlh.pdf",
        used_for="Saturday 11:00 a.m. NLH multi-flight event, 30-minute levels, registration to level 10, optional $40 gratuity for +20,000 chips. PDF title says $1,100 while its rules text says '$600 Buy-in' — flagged.",
    ),
    "B_TC": dict(
        kind="official",
        publisher="Bellagio Las Vegas",
        title="Hotel Reservation Terms and Conditions",
        url="https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
        used_for="Daily resort fee of $55 plus applicable tax; extra-occupant charge $50 plus tax; 72-hour cancellation; $150/day incidental authorisation.",
    ),
    # ---- MGM Grand ----------------------------------------------------------
    "M_POKER": dict(
        kind="official",
        publisher="MGM Grand Las Vegas",
        title="Poker at MGM Grand",
        url="https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html",
        used_for="Poker room open 24 hours; daily tournaments at 11:00am, 7:00pm and 11:00pm; links to the official weekly schedule and structure PDFs.",
    ),
    "M_SCHED_PDF": dict(
        kind="official",
        publisher="MGM Grand Las Vegas",
        title="MGM Grand weekly tournament schedule PDF (labelled 'August Tournament Schedule')",
        url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf",
        used_for="Daily 11:10am / 7:10pm / 11:10pm $120 NLH with 25K chips and 15-minute levels; Saturday 11:10am $150 NLH $2,000 guarantee with 20-minute levels. Month label is stale — flagged.",
    ),
    "M_STRUCT_PDF": dict(
        kind="official",
        publisher="MGM Grand Las Vegas",
        title="MGM Grand $120 NLH tournament structure and rules",
        url="https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/bltb2a45da7e8ee5621/mgm-grand-casino-poker-120_nlh.pdf",
        used_for="$120 fee split ($92 prize pool / $13 house fee / $11 voluntary gratuity / $4 promotions), 25,000 chips including the gratuity chips, registration open until level 8, '1 in 7 entries in the money'.",
    ),
    "M_TC": dict(
        kind="official",
        publisher="MGM Grand Las Vegas",
        title="Hotel Reservation Terms and Conditions",
        url="https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
        used_for="Daily resort fee of $50 plus applicable tax; extra-occupant charge $40 plus tax; 72-hour cancellation; $100/day incidental authorisation.",
    ),
    # ---- routing ------------------------------------------------------------
    "G_WALK": dict(
        kind="routing",
        publisher="Google Maps",
        title="Google Maps walking directions (travelmode=walking)",
        url="https://www.google.com/maps/dir/?api=1&travelmode=walking",
        used_for="Point-to-point walking minutes and distance used in the walking matrix. This is a routing service, not a casino or hotel policy page.",
    ),
}


def VEN(event_no, date, time, name, buy_in, gtd, s_pdf, reg_close, chips, level_min,
        fee=None, pool=None, rule="not_stated", rule_excerpt=None, etype="1day",
        notes="", ordinal_ok=True):
    """Build a Venetian event row."""
    return dict(
        venue="venetian",
        date=date, time=time, event_no=str(event_no), name=name,
        buy_in=buy_in, fee=fee, pool_per_entry=pool, gtd=gtd,
        reg_close=reg_close, chips=chips, level_min=level_min,
        structure_pdf=f"https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{s_pdf}.pdf",
        entry_rule=rule, entry_rule_excerpt=rule_excerpt, type=etype, notes=notes,
        sources=["V_SCHED_TABLE", "V_SCHED_PDF", f"S_V{s_pdf}"],
    )


# Structure-sheet registry (each PDF was opened and read on 2026-11-16).
STRUCT_SHEETS = {
    1: "s1", 2: "s2", 3: "s3", 4: "s4", 5: "s5", 6: "s6", 7: "s7", 8: "s8",
    9: "s9", 10: "s10", 11: "s11", 12: "s12", 13: "s13", 14: "s14", 15: "s15",
    16: "s16", 17: "s17", 18: "s18", 19: "s19", 20: "s20", 21: "s21", 22: "s22",
    23: "s23", 24: "s24", 25: "s25", 26: "s26", 27: "s27", 28: "s28", 29: "s29",
    30: "s30", 31: "s31", 32: "s32", 33: "s33", 34: "s34", 35: "s35", 36: "s36",
    37: "s37",
}
STRUCT_READ = {1, 2, 4, 5, 6, 7, 11, 12, 15, 18, 20, 21, 29, 34}
for n in STRUCT_SHEETS:
    SOURCES[f"S_V{n}"] = dict(
        kind="official",
        publisher="The Venetian Resort Las Vegas",
        title=f"DSE IV 2026 structure sheet {n}",
        url=f"https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{n}.pdf",
        used_for=("Read in full on 2026-11-16: levels, late-registration close, buy-in fee split, re-entry wording."
                  if n in STRUCT_READ else
                  "Linked from the official schedule. Not opened in this session — any value that would come from it is left blank, not inferred."),
    )

VENETIAN = [
    VEN(1, "2026-11-16", "11:10", "$300 No Limit Hold'em 1A — $75K GTD", 300, 75000, 10, "15:40", 30000, 40, etype="flight"),
    VEN(1, "2026-11-16", "17:10", "$300 No Limit Hold'em 1B — $75K GTD", 300, 75000, 9, "20:40", 30000, 30, etype="flight"),
    VEN(1, "2026-11-17", "11:10", "$300 No Limit Hold'em 1C — $75K GTD", 300, 75000, 10, "15:40", 30000, 40, etype="flight"),
    VEN(1, "2026-11-17", "17:10", "$300 No Limit Hold'em 1D — $75K GTD", 300, 75000, 9, "20:40", 30000, 30, etype="flight"),
    VEN(2, "2026-11-18", "11:10", "$300 No Limit Hold'em (1 Day)", 300, 10000, 5, "16:55", 40000, 30,
        fee=58, pool=242,
        rule_excerpt="Late Registration: 10 levels + Break (~ 4:55 PM) — the sheet sets no maximum number of entries, no re-entry limit and no add-on."),
    VEN(1, "2026-11-18", "12:00", "Event 1 Day 2 Restart (no new entries)", None, None, 10, None, None, 40, etype="day2",
        notes="Day-2 restart. Not a fresh entry; listed so the day plan does not treat it as another tournament."),
    VEN(3, "2026-11-19", "10:10", "$200 NLH RaceDay Stack (1 Day)", 200, None, 18, "12:25", 30000, 20,
        fee=35, pool=165, rule_excerpt="Late Registration: 6 levels + Break (~ 12:25 PM). No entry cap stated on the sheet."),
    VEN(4, "2026-11-20", "10:10", "$200 NLH RaceDay Stack (1 Day)", 200, None, 18, "12:25", 30000, 20, fee=35, pool=165),
    VEN(5, "2026-11-21", "10:10", "$200 NLH RaceDay Stack (1 Day)", 200, None, 18, "12:25", 30000, 20, fee=35, pool=165),
    VEN(6, "2026-11-22", "11:10", "$200 No Limit Hold'em (1 Day)", 200, None, 29, "15:40", 30000, 30, fee=40, pool=160),
    VEN(7, "2026-11-23", "11:10", "$400 No Limit Hold'em 1A — $75K GTD", 400, 75000, 2, "17:55", 40000, 40,
        fee=70, pool=330, etype="flight",
        rule_excerpt="'Any player who bags chips for Day 2 may not play a subsequent flight.' The sheet restricts play after bagging but states no cap on entries before bagging."),
    VEN(8, "2026-11-23", "17:10", "$200 NLH Progressive Knock-Out Bounty (1 Day) — $8K GTD", 200, 8000, 30, "21:40", 25000, 30),
    VEN(7, "2026-11-24", "11:10", "$400 No Limit Hold'em 1B — $75K GTD", 400, 75000, 2, "17:55", 40000, 40, fee=70, pool=330, etype="flight"),
    VEN(9, "2026-11-24", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30,
        fee=40, pool=160,
        rule_excerpt="$40 of the $200 Buy-In is withheld for house fees. Late Registration: 8 levels + Break (9:40 PM). No entry cap or add-on is stated."),
    VEN(7, "2026-11-25", "11:00", "Event 7 Day 2 Restart (no new entries)", None, None, 2, None, None, 40, etype="day2"),
    VEN(10, "2026-11-25", "11:10", "$400 No Limit Hold'em (1 Day) — $15K GTD", 400, 15000, 6, "16:55", 40000, 30,
        fee=65, pool=335,
        rule_excerpt="$65 of the $400 Buy-In is withheld for house fees. Late Registration: 10 levels + Break (~ 4:55 PM). No entry cap or add-on is stated."),
    VEN(11, "2026-11-25", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(12, "2026-11-26", "11:10", "$300 No Limit Hold'em (1 Day) — $10K GTD", 300, 10000, 5, "16:55", 40000, 30, fee=58, pool=242),
    VEN(13, "2026-11-26", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(14, "2026-11-27", "11:10", "$600 No Limit Hold'em (1 Day) — $30K GTD", 600, 30000, 7, "16:55", 40000, 30,
        fee=90, pool=510,
        rule_excerpt="$90 of the $600 Buy-In is withheld for house fees. Late Registration: 10 levels + Break (~ 4:55 PM). The sheet states no entry cap, no re-entry limit and no add-on."),
    VEN(15, "2026-11-27", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(16, "2026-11-28", "11:10", "$600 NLH Bounty (1 Day) — $30K GTD ($200 bounties to start, $500 in the money)", 600, 30000, 11, "16:55", 40000, 30,
        fee=90, pool=510,
        rule_excerpt="$90 of the $600 Buy-In is withheld for house fees. Late Registration: 10 levels + Break (4:55 PM). Bounty structure set out in rule 07; no entry cap or add-on stated."),
    VEN(17, "2026-11-28", "12:10", "$400 Pot Limit Omaha Bounty (1 Day) — $15K GTD", 400, 15000, 26, "16:40", 30000, 30),
    VEN(18, "2026-11-28", "17:10", "$200 NLH PokerAtlas Valuetown Bounty (1 Day) — $20K GTD", 200, 20000, 8, "21:40", 25000, 30),
    VEN(19, "2026-11-29", "11:10", "$400 No Limit Hold'em 1A — $75K GTD", 400, 75000, 3, "17:55", 40000, 40),
    VEN(20, "2026-11-29", "12:10", "$300 Pot Limit Omaha Double Board Bomb Pot (1 Day) — $10K GTD", 300, 10000, 22, "16:40", 30000, 30),
    VEN(21, "2026-11-29", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(19, "2026-11-30", "11:10", "$400 No Limit Hold'em 1B — $75K GTD", 400, 75000, 3, "17:55", 40000, 40, etype="flight"),
    VEN(22, "2026-11-30", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(19, "2026-12-01", "11:10", "$400 No Limit Hold'em 1C — $75K GTD", 400, 75000, 3, "17:55", 40000, 40, etype="flight"),
    VEN(23, "2026-12-01", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(24, "2026-12-02", "10:10", "$600 No Limit Hold'em Seniors (1 Day) — $40K GTD — must be 50+", 600, 40000, 17, "15:55", 40000, 30),
    VEN(19, "2026-12-02", "11:00", "Event 19 Day 2 Restart (no new entries)", None, None, 3, None, None, 40, etype="day2"),
    VEN(25, "2026-12-02", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(26, "2026-12-03", "11:10", "$800 No Limit Hold'em 1A — $500K GTD", 800, 500000, 12, "15:40", 40000, 40,
        fee=110, pool=690, etype="flight",
        rule_excerpt="$110 of the $800 Buy-In is withheld for house fees. Late Registration: 6 levels + Break (~ 3:40 PM). 'Any player who bags chips for Day 2 may not play a subsequent flight.'"),
    VEN(27, "2026-12-03", "12:10", "$600 BIG O (1 Day) — $25K GTD", 600, 25000, 28, "16:40", 30000, 30),
    VEN(26, "2026-12-03", "17:10", "$800 No Limit Hold'em 1B — $500K GTD", 800, 500000, 13, "20:40", 40000, 30, fee=110, pool=690, etype="flight"),
    VEN(26, "2026-12-04", "11:10", "$800 No Limit Hold'em 1C — $500K GTD", 800, 500000, 12, "15:40", 40000, 40, fee=110, pool=690, etype="flight"),
    VEN(26, "2026-12-04", "17:10", "$800 No Limit Hold'em 1D — $500K GTD", 800, 500000, 13, "20:40", 40000, 30, fee=110, pool=690, etype="flight"),
    VEN(26, "2026-12-05", "11:10", "$800 No Limit Hold'em 1E — $500K GTD", 800, 500000, 12, "15:40", 40000, 40, fee=110, pool=690, etype="flight"),
    VEN(26, "2026-12-05", "17:10", "$800 No Limit Hold'em 1F (Turbo) — $500K GTD", 800, 500000, 14, "19:25", 40000, 20, etype="flight"),
    VEN(28, "2026-12-06", "11:10", "$600 No Limit Hold'em (1 Day) — $40K GTD", 600, 40000, 7, "16:55", 40000, 30,
        fee=90, pool=510,
        rule_excerpt="$90 of the $600 Buy-In is withheld for house fees. Late Registration: 10 levels + Break (~ 4:55 PM). The sheet states no entry cap, no re-entry limit and no add-on."),
    VEN(26, "2026-12-06", "12:00", "Event 26 Day 2 Restart (no new entries)", None, None, 12, None, None, 40, etype="day2"),
    VEN(29, "2026-12-06", "17:10", "$300 NLH Bounty (1 Day) — $15K GTD", 300, 15000, 15, "21:40", 25000, 30,
        fee=50, pool=250,
        rule_excerpt="$50 of the $300 Buy-In is withheld for house fees. $100 bounty per elimination. Late Registration: 8 levels + Break (9:40 PM). No entry cap or add-on stated."),
    VEN(30, "2026-12-07", "11:10", "$600 NLH Bounty (1 Day) — $40K GTD", 600, 40000, 11, "16:55", 40000, 30, fee=90, pool=510),
    VEN(31, "2026-12-07", "17:10", "$300 NLH Bounty (1 Day) — $15K GTD", 300, 15000, 15, "21:40", 25000, 30, fee=50, pool=250),
    VEN(32, "2026-12-08", "10:10", "$600 No Limit Hold'em Seniors (1 Day) — $40K GTD — must be 50+", 600, 40000, 17, "15:55", 40000, 30),
    VEN(33, "2026-12-08", "16:10", "$100 NLH LIPS Ladies Milestone Satellite (1 Day) — 2 seats to Event #39", 100, None, 19, "18:25", 20000, 20, etype="satellite"),
    VEN(34, "2026-12-08", "17:10", "$300 NLH Bounty (1 Day) — $15K GTD", 300, 15000, 15, "21:40", 25000, 30, fee=50, pool=250),
    VEN(35, "2026-12-09", "10:10", "$600 NLH LIPS Poker Jingle Tag Team (1 Day) — $10K GTD", 600, 10000, 31, "14:40", 40000, 30, etype="team"),
    VEN(36, "2026-12-09", "11:10", "$800 NLH Bounty (1 Day) — $75K GTD", 800, 75000, 16, "16:55", 40000, 30),
    VEN(37, "2026-12-09", "16:10", "$100 NLH LIPS Ladies Milestone Satellite (1 Day) — 2 seats to Event #39", 100, None, 19, "18:25", 20000, 20, etype="satellite"),
    VEN(38, "2026-12-09", "17:10", "$300 NLH Bounty (1 Day) — $15K GTD", 300, 15000, 15, "21:40", 25000, 30, fee=50, pool=250),
    VEN(39, "2026-12-10", "10:10", "$800 NLH LIPS Ladies (2 Day) — $40K GTD", 800, 40000, 32, "16:55", 40000, 40, etype="2day"),
    VEN(40, "2026-12-10", "12:10", "$600 Pot Limit Omaha Bounty (1 Day) — $25K GTD", 600, 25000, 27, "16:40", 30000, 30),
    VEN(41, "2026-12-10", "16:10", "$260 NLH Milestone Satellite (1 Day) — direct entry to Event #47", 260, None, 24, "18:25", 20000, 20, etype="satellite"),
    VEN(42, "2026-12-10", "17:10", "$300 NLH Bounty (1 Day) — $15K GTD", 300, 15000, 15, "21:40", 25000, 30, fee=50, pool=250),
    VEN(39, "2026-12-11", "10:00", "Event 39 Day 2 Restart (no new entries)", None, None, 32, None, None, 40, etype="day2"),
    VEN(43, "2026-12-11", "11:10", "$600 NLH LIPS (1 Day) — $30K GTD — Kings & Queens bounty, open to all", 600, 30000, 33, "16:55", 40000, 30),
    VEN(44, "2026-12-11", "16:10", "$260 NLH Milestone Satellite (1 Day) — direct entry to Event #47", 260, None, 24, "18:25", 20000, 20, etype="satellite"),
    VEN(39, "2026-12-11", "19:00", "Event 39 Final Table (streamed, PokerGO)", None, None, 32, None, None, 40, etype="final"),
    VEN(45, "2026-12-11", "20:10", "$260 NLH Turbo Milestone Satellite (1 Day) — direct entry to Event #47", 260, None, 25, "22:25", 20000, 15, etype="satellite"),
    VEN(46, "2026-12-12", "09:10", "$260 NLH Turbo Milestone Satellite (1 Day) — direct entry to Event #47", 260, None, 25, "11:25", 20000, 15, etype="satellite"),
    VEN(47, "2026-12-12", "10:10", "$2,200 No Limit Hold'em 1A — $1,000,000 GTD — PokerAtlas Championship", 2200, 1000000, 21, "16:55", 40000, 40,
        fee=225, pool=1975, etype="flight",
        rule_excerpt="$225 of the $2,200 Buy-In is withheld for house fees. 'Any player who bags chips for Day 2 may not play a subsequent flight.'"),
    VEN(48, "2026-12-12", "12:10", "$260 NLH Turbo Milestone Satellite (1 Day) — direct entry to Event #47", 260, None, 25, "14:25", 20000, 15, etype="satellite"),
    VEN(47, "2026-12-12", "18:10", "$2,200 No Limit Hold'em 1B — $1,000,000 GTD", 2200, 1000000, 37, "23:25", 40000, 30, fee=225, pool=1975, etype="flight"),
    VEN(49, "2026-12-13", "10:10", "$1,100 NLH Seniors 1A — $300K GTD — must be 50+", 1100, 300000, 20, "16:55", 40000, 40,
        fee=140, pool=960, etype="flight",
        rule_excerpt="$140 of the $1,100 Buy-In is withheld for house fees. 'Any player who bags chips for Day 2 may not play a subsequent flight.'"),
    VEN(47, "2026-12-13", "13:00", "Event 47 Day 2 Restart (no new entries)", None, None, 21, None, None, 40, etype="day2"),
    VEN(50, "2026-12-13", "17:10", "$300 NLH Bounty (1 Day) — $15K GTD", 300, 15000, 15, "21:40", 25000, 30, fee=50, pool=250),
    VEN(49, "2026-12-14", "10:10", "$1,100 NLH Seniors 1B — $300K GTD — must be 50+", 1100, 300000, 20, "16:55", 40000, 40, fee=140, pool=960, etype="flight"),
    VEN(47, "2026-12-14", "11:00", "Event 47 Day 3 Restart (streamed final table)", None, None, 21, None, None, 40, etype="final"),
    VEN(51, "2026-12-14", "17:10", "$300 NLH Bounty (1 Day) — $15K GTD", 300, 15000, 15, "21:40", 25000, 30, fee=50, pool=250),
    VEN(49, "2026-12-15", "10:00", "Event 49 Day 2 Restart (no new entries)", None, None, 20, None, None, 40, etype="day2"),
    VEN(52, "2026-12-15", "11:10", "$1,100 No Limit Hold'em (1 Day) — $75K GTD — Progressive Knock-Out Bounty", 1100, 75000, 34, "16:55", 40000, 30,
        fee=130, pool=970,
        rule_excerpt="$130 of the $1,100 Buy-In is withheld for house fees. Late Registration: 10 levels + Break (4:55 PM). No entry cap or add-on stated."),
    VEN(53, "2026-12-15", "17:10", "$300 NLH Bounty (1 Day) — $15K GTD", 300, 15000, 15, "21:40", 25000, 30, fee=50, pool=250),
    VEN(54, "2026-12-16", "11:10", "$600 NLH Bounty (1 Day) — $50K GTD", 600, 50000, 11, "16:55", 40000, 30, fee=90, pool=510),
    VEN(55, "2026-12-16", "17:10", "$300 NLH Bounty (1 Day) — $15K GTD", 300, 15000, 15, "21:40", 25000, 30, fee=50, pool=250),
    VEN(56, "2026-12-17", "10:10", "$1,100 No Limit Hold'em 1A — $500K GTD — $40 rake discount before 10:10 a.m.", 1100, 500000, 35, "16:55", 40000, 40, etype="flight"),
    VEN(57, "2026-12-17", "12:10", "$600 Pot Limit Omaha (1 Day) — $25K GTD — Double Board Bomb Pot", 600, 25000, 23, "16:40", 30000, 30),
    VEN(56, "2026-12-17", "18:10", "$1,100 No Limit Hold'em 1B — $500K GTD — $40 rake discount before 6:10 p.m.", 1100, 500000, 36, "23:25", 40000, 30, etype="flight"),
    VEN(56, "2026-12-18", "10:10", "$1,100 No Limit Hold'em 1C — $500K GTD", 1100, 500000, 35, "16:55", 40000, 40, etype="flight"),
    VEN(56, "2026-12-18", "18:10", "$1,100 No Limit Hold'em 1D — $500K GTD", 1100, 500000, 36, "23:25", 40000, 30, etype="flight"),
    VEN(56, "2026-12-19", "10:10", "$1,100 No Limit Hold'em 1E — $500K GTD", 1100, 500000, 35, "16:55", 40000, 40, etype="flight"),
    VEN(58, "2026-12-19", "17:10", "$200 NLH PokerAtlas Valuetown Bounty (1 Day) — $20K GTD", 200, 20000, 8, "21:40", 25000, 30),
    VEN(56, "2026-12-20", "11:00", "Event 56 Day 2 Restart (no new entries)", None, None, 35, None, None, 40, etype="day2"),
    VEN(59, "2026-12-20", "11:10", "$600 No Limit Hold'em 1A — $150K GTD — $20 rake discount before 11:10 a.m.", 600, 150000, 4, "17:55", 40000, 40,
        fee=95, pool=505, etype="flight",
        rule_excerpt="$95 of the $600 Buy-In is withheld for house fees; on Day 1A a $20 discount applies pre-registration ($580 total). Late Registration: 9 levels + Break (5:55 PM)."),
    VEN(60, "2026-12-20", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(59, "2026-12-21", "11:10", "$600 No Limit Hold'em 1B — $150K GTD", 600, 150000, 4, "17:55", 40000, 40, fee=95, pool=505, etype="flight"),
    VEN(61, "2026-12-21", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(59, "2026-12-22", "11:10", "$600 No Limit Hold'em 1C — $150K GTD", 600, 150000, 4, "17:55", 40000, 40, fee=95, pool=505, etype="flight"),
    VEN(62, "2026-12-22", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
    VEN(59, "2026-12-23", "11:00", "Event 59 Day 2 Restart (no new entries)", None, None, 4, None, None, 40, etype="day2"),
    VEN(63, "2026-12-23", "11:10", "$600 No Limit Hold'em (1 Day) — $30K GTD", 600, 30000, 7, "16:55", 40000, 30, fee=90, pool=510),
    VEN(64, "2026-12-23", "17:10", "$200 NLH Bounty (1 Day) — $8K GTD", 200, 8000, 1, "21:40", 25000, 30, fee=40, pool=160),
]
for i, e in enumerate(VENETIAN):
    e["id"] = f"VEN-{i+1:03d}"
    e["venue_name"] = "The Venetian / The Palazzo"
    e["game"] = ("NLH" if "No Limit Hold'em" in e["name"] or "NLH" in e["name"]
                 else "PLO" if "Omaha" in e["name"] else "Mixed")

# ---------------------------------------------------------------------------
# WYNN — WPT World Championship (full schedule PDF)
# (date, time, event, buy_in, guarantee, chips, levels)
# ---------------------------------------------------------------------------
WPT_ROWS = [
    ("2026-11-27", "11:00", "No Limit Hold'em Day 1A", 600, 400000, 40000, "30/40"),
    ("2026-11-27", "12:00", "TORSE", 600, None, 35000, "30"),
    ("2026-11-27", "13:00", "PLO", 400, None, 30000, "30"),
    ("2026-11-27", "17:00", "No Limit Hold'em Day 1B", 600, 400000, 40000, "30/40"),
    ("2026-11-28", "11:00", "No Limit Hold'em Day 1C", 600, 400000, 40000, "30/40"),
    ("2026-11-28", "12:00", "Mixed Triple Draw (A-5, 2-7, Badugi)", 600, None, 35000, "30"),
    ("2026-11-28", "17:00", "No Limit Hold'em Day 1D", 600, 400000, 40000, "30/40"),
    ("2026-11-29", "11:00", "No Limit Hold'em Day 1E", 600, 400000, 40000, "30/40"),
    ("2026-11-29", "18:00", "No Limit Hold'em Day 1F", 600, 400000, 40000, "20/40"),
    ("2026-11-30", "11:00", "No Limit Hold'em Day 1A", 800, 1000000, 40000, "30/40"),
    ("2026-11-30", "12:00", "Limit Omaha 8", 600, None, 35000, "30"),
    ("2026-11-30", "13:00", "No Limit Hold'em Day 2 (of $600)", None, 400000, 40000, "30/40"),
    ("2026-11-30", "17:00", "No Limit Hold'em Day 1B", 800, 1000000, 40000, "30/40"),
    ("2026-12-01", "11:00", "No Limit Hold'em Day 1C", 800, 1000000, 40000, "30/40"),
    ("2026-12-01", "12:00", "Limit Omaha 8/5/Stud 8", 600, None, 35000, "30"),
    ("2026-12-01", "13:00", "PLO", 1100, None, 30000, "30"),
    ("2026-12-01", "17:00", "No Limit Hold'em Day 1D", 800, 1000000, 40000, "30/40"),
    ("2026-12-02", "11:00", "No Limit Hold'em Day 1E", 800, 1000000, 40000, "30/40"),
    ("2026-12-02", "18:00", "No Limit Hold'em Day 1F", 800, 1000000, 40000, "20/40"),
    ("2026-12-03", "11:00", "No Limit Hold'em Day 1A", 1600, 1000000, 40000, "40"),
    ("2026-12-03", "13:00", "No Limit Hold'em Day 2 (of $800)", None, 1000000, 40000, "40"),
    ("2026-12-03", "19:00", "Double Play Milestone Satellite (2 x $1,100 ticket)", 400, None, 20000, "20"),
    ("2026-12-04", "11:00", "No Limit Hold'em Day 1B", 1600, 1000000, 40000, "40"),
    ("2026-12-04", "12:00", "HORSE", 600, None, 35000, "30"),
    ("2026-12-04", "13:00", "No Limit Hold'em Final Table (of $800)", None, 1000000, 40000, "40"),
    ("2026-12-04", "19:00", "Double Play Milestone Satellite (2 x $1,100 ticket)", 400, None, 20000, "20"),
    ("2026-12-05", "11:00", "WPT Prime Championship Day 1A", 1100, 5000000, 40000, "40/60"),
    ("2026-12-05", "21:00", "NLH Turbo", 600, 50000, 30000, "20"),
    ("2026-12-06", "11:00", "WPT Prime Championship Day 1B", 1100, 5000000, 40000, "40/60"),
    ("2026-12-06", "11:00", "PLO Mystery Bounty Day 1A", 1600, 500000, 40000, "40"),
    ("2026-12-06", "12:00", "Milestone Satellite to $1,100 Prime Championship", 200, None, 20000, "20"),
    ("2026-12-06", "18:00", "PLO Mystery Bounty Day 1B", 1600, 500000, 40000, "20/40"),
    ("2026-12-06", "19:00", "Double Play Milestone Satellite (2 x $1,100 ticket)", 400, None, 20000, "20"),
    ("2026-12-06", "21:00", "NLH Turbo", 600, 50000, 30000, "20"),
    ("2026-12-07", "11:00", "WPT Prime Championship Day 1C", 1100, 5000000, 40000, "40/60"),
    ("2026-12-07", "11:00", "HORSE (2 Day)", 1100, None, 40000, "40"),
    ("2026-12-07", "12:00", "PLO Mystery Bounty Day 2", None, 500000, 40000, "20/40"),
    ("2026-12-07", "13:00", "PLO $500 Bounty", 1600, 100000, 30000, "30"),
    ("2026-12-07", "19:00", "Milestone Satellite Package to Prime and World Championship", 1600, None, 20000, "25"),
    ("2026-12-07", "21:00", "NLH Turbo", 600, 50000, 30000, "20"),
    ("2026-12-08", "11:00", "WPT Prime Championship Day 1D", 1100, 5000000, 40000, "40/60"),
    ("2026-12-08", "19:00", "Milestone Satellite to $10,400 World Championship", 1100, None, 20000, "25"),
    ("2026-12-08", "21:00", "NLH Turbo", 600, 50000, 30000, "20"),
    ("2026-12-09", "11:00", "No Limit Hold'em (2 Day)", 1600, 1000000, 40000, "40"),
    ("2026-12-09", "12:00", "WPT Prime Championship Day 2", None, 5000000, 40000, "40/60"),
    ("2026-12-09", "13:00", "PLO $1,000 Bounty", 3000, 250000, 30000, "30"),
    ("2026-12-09", "13:00", "Limit Omaha 8", 800, None, 35000, "30"),
    ("2026-12-09", "14:00", "Milestone Satellite to $10,400 World Championship", 1100, None, 20000, "25"),
    ("2026-12-09", "19:00", "Milestone Satellite to $10,400 World Championship", 1100, None, 20000, "25"),
    ("2026-12-09", "21:00", "NLH Turbo", 600, 50000, 30000, "20"),
    ("2026-12-10", "10:00", "Super Gold Million Mystery Bounty Day 1A", 400, 3000000, 30000, "30/40"),
    ("2026-12-10", "12:00", "WPT Prime Championship Day 3", None, 5000000, 40000, "40/60"),
    ("2026-12-10", "18:00", "Super Gold Million Mystery Bounty Day 1B", 400, 3000000, 30000, "20/40"),
    ("2026-12-11", "10:00", "Super Gold Million Mystery Bounty Day 1C", 400, 3000000, 30000, "30/40"),
    ("2026-12-11", "12:00", "WPT Prime Championship Day 4", None, 5000000, 40000, "40/60"),
    ("2026-12-11", "18:00", "Super Gold Million Mystery Bounty Day 1D", 400, 3000000, 30000, "20/40"),
    ("2026-12-12", "10:00", "No Limit Hold'em", 800, 100000, 30000, "30"),
    ("2026-12-12", "13:00", "PLO", 3000, 250000, 30000, "30"),
    ("2026-12-12", "14:00", "WPT Prime Championship Final Table", None, 5000000, 40000, "40/60"),
    ("2026-12-12", "14:00", "Super Gold Million Mystery Bounty Day 2", None, 3000000, 30000, "40"),
    ("2026-12-12", "16:00", "Milestone Satellite to $10,400 Ladies NLH Championship", 200, None, 20000, "20"),
    ("2026-12-12", "19:00", "Milestone Satellite to $10,400 World Championship", 1100, None, 20000, "25"),
    ("2026-12-12", "21:00", "NLH Turbo", 600, 50000, 30000, "20"),
    ("2026-12-13", "11:00", "WPT World Championship Day 1A ($1,000,000 added)", 10400, None, 100000, "60/90"),
    ("2026-12-13", "11:00", "Ladies NLH Championship (2 Day)", 1100, 250000, 40000, "40"),
    ("2026-12-13", "11:00", "TORSE (2 Day)", 1100, None, 40000, "40"),
    ("2026-12-13", "11:00", "No Limit Hold'em Day 1A", 800, 500000, 40000, "40"),
    ("2026-12-13", "12:00", "PLO Day 1A", 1600, 1000000, 40000, "40"),
    ("2026-12-13", "13:00", "Super Gold Million Mystery Bounty Day 3", None, 3000000, 30000, "40"),
    ("2026-12-14", "11:00", "WPT World Championship Day 1B ($1,000,000 added)", 10400, None, 100000, "60/90"),
    ("2026-12-14", "11:00", "No Limit Hold'em Day 1B", 800, 500000, 40000, "40"),
    ("2026-12-14", "12:00", "PLO Day 1B", 1600, 1000000, 40000, "40"),
    ("2026-12-14", "12:00", "Mixed Triple Draw (A-5, 2-7, Badugi) (2 Day)", 1100, None, 40000, "40"),
    ("2026-12-14", "14:00", "Super Gold Million Mystery Bounty Final Table", None, 3000000, 30000, "40"),
    ("2026-12-14", "19:00", "PLO Turbo", 1100, 100000, 30000, "20"),
    ("2026-12-14", "21:00", "NLH Turbo", 600, 50000, 30000, "20"),
    ("2026-12-15", "11:00", "WPT World Championship Day 1C ($1,000,000 added)", 10400, None, 100000, "60/90"),
    ("2026-12-15", "11:00", "No Limit Hold'em Day 2 (of $800)", None, 500000, 40000, "40"),
    ("2026-12-15", "12:00", "PLO Day 2", None, 1000000, 40000, "40"),
    ("2026-12-15", "12:00", "Big O", 1100, None, 30000, "30"),
    ("2026-12-15", "13:00", "PLO Progressive Bounty (PKO)", 3000, 250000, 30000, "30"),
    ("2026-12-15", "19:00", "NLH $500 Bounty Turbo", 1600, 100000, 30000, "20"),
    ("2026-12-17", "11:00", "Seniors NLH Championship (3 Day)", 1100, 500000, 40000, "40"),
    ("2026-12-17", "11:00", "Wynn Mixed Championship (2 Day)", 1600, None, 40000, "40/60"),
    ("2026-12-17", "12:00", "WPT World Championship Day 3", None, None, 100000, "60/90"),
    ("2026-12-17", "12:00", "No Limit Hold'em Day 1A", 3000, 2000000, 40000, "40"),
    ("2026-12-17", "13:00", "NLH High Roller (2 Day)", 25800, None, 200000, "40/60"),
    ("2026-12-17", "14:00", "Milestone Satellite to $3,000 NLH", 400, None, 20000, "20"),
    ("2026-12-17", "19:00", "Milestone Satellite to $3,000 NLH", 400, None, 20000, "20"),
    ("2026-12-18", "10:00", "Milestone Satellite to $3,000 NLH", 400, None, 20000, "15"),
    ("2026-12-18", "11:00", "No Limit Hold'em Day 1A", 1100, 1000000, 40000, "40"),
    ("2026-12-18", "12:00", "WPT World Championship Day 4", None, None, 100000, "60/90"),
    ("2026-12-18", "12:00", "No Limit Hold'em Day 1B (of $3,000)", 3000, 2000000, 40000, "40"),
    ("2026-12-18", "12:00", "Limit Omaha 8 Championship (2 Day)", 1600, None, 40000, "40/60"),
    ("2026-12-18", "12:00", "No Limit Hold'em", 600, 100000, 30000, "30"),
    ("2026-12-18", "13:00", "NLH 6-Max", 10500, None, 100000, "30/40"),
    ("2026-12-18", "13:00", "PLO 6-Max", 10500, None, 100000, "30/40"),
    ("2026-12-18", "13:00", "HORSE", 800, None, 35000, "30"),
    ("2026-12-18", "14:00", "Milestone Satellite to $5,000 Seniors High Roller", 600, None, 20000, "20"),
    ("2026-12-18", "18:00", "NLH Turbo", 1100, 100000, 30000, "20"),
    ("2026-12-18", "18:00", "Milestone Satellite to $3,000 NLH", 400, None, 20000, "20"),
    ("2026-12-18", "19:00", "No Limit Hold'em Day 1B (of $1,100)", 1100, 1000000, 40000, "20/40"),
    ("2026-12-19", "11:00", "Seniors High Roller (3 Day)", 5000, 250000, 50000, "60"),
    ("2026-12-19", "11:00", "NLH Mystery Bounty Day 1A", 1600, 1000000, 40000, "40"),
    ("2026-12-19", "12:00", "WPT World Championship Day 5", None, None, 100000, "60/90"),
    ("2026-12-19", "12:00", "Milestone Satellite to $1,600 Mystery Bounty", 300, None, 20000, "20"),
    ("2026-12-19", "13:00", "PLO", 10500, None, 100000, "30/40"),
    ("2026-12-19", "13:00", "NLH 6-Max", 3000, 500000, 30000, "30"),
    ("2026-12-19", "13:00", "TORSE Championship (2 Day)", 1600, None, 40000, "40/60"),
    ("2026-12-19", "17:00", "Milestone Satellite to $1,600 Mystery Bounty", 300, None, 20000, "20"),
    ("2026-12-19", "18:00", "NLH 6-Max Turbo", 600, 50000, 30000, "20"),
    ("2026-12-19", "19:00", "NLH Mystery Bounty Day 1B", 1600, 1000000, 40000, "20/40"),
    ("2026-12-20", "11:00", "NLH Mystery Bounty Day 1C", 1600, 1000000, 40000, "40"),
    ("2026-12-20", "12:00", "No Limit Hold'em Final Table (of $1,100)", None, 1000000, 40000, "40"),
    ("2026-12-20", "12:00", "No Limit Hold'em", 600, 50000, 30000, "30"),
    ("2026-12-20", "13:00", "NLH 8-Max", 10500, None, 100000, "30/40"),
    ("2026-12-20", "13:00", "Mixed Triple Draw (A-5, 2-7, Badugi)", 600, None, 35000, "30"),
    ("2026-12-20", "14:00", "WPT World Championship Final Table", None, None, 100000, "60/90"),
    ("2026-12-20", "18:00", "5-Card PLO Turbo", 600, 50000, 30000, "20"),
    ("2026-12-20", "19:00", "NLH Mystery Bounty Day 1D", 1600, 1000000, 40000, "20/40"),
    ("2026-12-21", "12:00", "No Limit Hold'em", 1100, 100000, 30000, "30"),
    ("2026-12-21", "13:00", "NLH Mystery Bounty Day 2", None, 1000000, 40000, "40"),
    ("2026-12-21", "20:00", "NLH Turbo", 600, 50000, 30000, "20"),
]

WYNN = []
for i, (d, t, name, bi, gtd, chips, lv) in enumerate(WPT_ROWS):
    WYNN.append(dict(
        id=f"WPT-{i+1:03d}", venue="wynn", venue_name="Wynn / Encore Las Vegas",
        date=d, time=t, event_no="", name=name, buy_in=bi, fee=None,
        pool_per_entry=None, gtd=gtd, reg_close=None, chips=chips,
        level_min=None, structure_pdf=None,
        # Per-event entry rule. Only the events whose own structure sheet was
        # opened can carry a rule; the rest were not opened, and labelling all
        # 127 rows "unlimited re-entry" off a handful of read sheets would be an
        # inference dressed up as a fact. See WYNN_ENTRY below.
        entry_rule="not_stated", entry_rule_excerpt=None,
        type=("final" if "Final Table" in name else "day2" if " Day 2" in name or " Day 3" in name
              or " Day 4" in name else "satellite" if "Satellite" in name else "flight" if "Day 1" in name else "1day"),
        sources=["W_WPT_SCHED"], game=("NLH" if "Hold'em" in name or "NLH" in name else "Mixed/other"),
        notes="",
    ))

# Verified fee splits from the WPT structures PDF (only the events actually read).
WYNN_FEES = {
    ("2026-11-27", "11:00", "No Limit Hold'em Day 1A"): (600, 65 + 25, 510),
    ("2026-11-27", "12:00", "TORSE"): (600, 65 + 25, 510),
    ("2026-11-27", "13:00", "PLO"): (400, 45 + 18, 337),
    ("2026-11-28", "12:00", "Mixed Triple Draw (A-5, 2-7, Badugi)"): (600, 65 + 25, 510),
    ("2026-11-30", "11:00", "No Limit Hold'em Day 1A"): (800, 72 + 33, 695),
    ("2026-11-30", "12:00", "Limit Omaha 8"): (600, 65 + 25, 510),
}
# A "not stated" row only counts as SILENT (i.e. a candidate) when its own
# structure sheet was actually opened. Everything else is UNREAD and must be
# labelled that way. This flag is the difference between evidence and absence.
for e in WYNN:
    e["sheet_read"] = False
for e in VENETIAN:
    e["sheet_read"] = e.get("fee") is not None
for e in WYNN:
    k = (e["date"], e["time"], e["name"])
    if k in WYNN_FEES:
        e["sheet_read"] = True
        _, fee, pool = WYNN_FEES[k]
        e["fee"] = fee
        e["pool_per_entry"] = pool
        e["sources"] = ["W_WPT_SCHED", "W_WPT_STRUCT"]
        e["entry_rule"] = "unlimited_reentry"
        e["entry_rule_excerpt"] = ("Structure sheet opened for this event: 'Unlimited re-entry for each "
                                   "starting flight ... until the start of level 9.'")

# ---------------------------------------------------------------------------
# Daily / weekly tournaments at other Strip rooms
# ---------------------------------------------------------------------------
def DAILY(venue, venue_name, weekday, time, name, buy_in, gtd, chips, level_min,
          fee, pool, rule, excerpt, sources, notes="", extra=None):
    """ONE row per recurring event. `weekday` is "*" for every day, a single day
    code, or a list of day codes; the dashboard expands it per date when it
    builds the day plan, so an event that runs seven days a week is counted once
    rather than seven times."""
    if weekday == "*":
        days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    elif isinstance(weekday, str):
        days = [weekday]
    else:
        days = list(weekday)
    r = dict(venue=venue, venue_name=venue_name, date=None, weekday=days, time=time,
             event_no="", name=name, buy_in=buy_in, fee=fee, pool_per_entry=pool,
             gtd=gtd, reg_close=None, chips=chips, level_min=level_min,
             structure_pdf=None, entry_rule=rule, entry_rule_excerpt=excerpt,
             type="daily", sources=list(sources), game="NLH",
             notes=notes)
    if extra:
        r.update(extra)
    return [r]


DAILY_ROWS = []
# Caesars Palace — official daily flyer
DAILY_ROWS += DAILY(
    "caesars-palace", "Caesars Palace", "*", "10:00", "$100 NLH Daily", 100, 1000, 20000, 20,
    30, 70, "reentry_allowed",
    "Sign-ups start one hour before the scheduled start. 'Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.' 'Of the $100 buy in, $70 goes to the prize pool and $30 is held by Caesars Palace as a maintenance fee.'",
    ["C_DAILY_PDF"], notes="Optional $50 add-on for 15,000 chips at the first break (add-on: $45 to pool / $5 fee). Registration closes at the start of level 7.")
DAILY_ROWS += DAILY(
    "caesars-palace", "Caesars Palace", "*", "14:00", "$160 NLH Daily", 160, 1000, 20000, 20,
    45, 115, "reentry_allowed",
    "'Participants may only register themselves, but may re-enter, by paying the entry fee, upon elimination within the first break of play.' 'Of the $160 buy in, $115 goes to the prize pool and $45 is held by Caesars Palace as a maintenance fee.'",
    ["C_DAILY_PDF"], notes="Optional $50 add-on for 15,000 chips at the first break. Registration closes at the start of level 7.")
DAILY_ROWS += DAILY(
    "caesars-palace", "Caesars Palace", "*", "18:00", "$100 NLH Daily", 100, 1000, 20000, 20,
    30, 70, "reentry_allowed", "Same daily flyer rules as the 10 AM $100 event.", ["C_DAILY_PDF"],
    notes="Optional $50 add-on for 15,000 chips at the first break.")
DAILY_ROWS += DAILY(
    "caesars-palace", "Caesars Palace", "*", "21:00", "$160 NLH Daily", 160, 1000, 20000, 20,
    45, 115, "reentry_allowed", "Same daily flyer rules as the 2 PM $160 event.", ["C_DAILY_PDF"],
    notes="Optional $50 add-on for 15,000 chips at the first break.")

# Wynn daily tournaments
DAILY_ROWS += DAILY(
    "wynn", "Wynn Las Vegas", ["mon", "tue", "wed", "thu"], "12:00", "$200 NLH Daily — $10K GTD", 200, 10000,
    25000, 30, 38, 162, "reentry_allowed",
    "'The Tournament entry fee, as well as the re-entry fee, is $200.' '$26 for the Tournament fee, $12 for the poker staff service charge, and $162 for the Tournament prize pool.' 'Registration and re-entries will be available until the start of level 9 (approximately 4:30 p.m.).'",
    ["W_DAILY_POSTER", "W_DAILY_STRUCT"], notes="Suspended during WPT World Championship (Nov 27 – Dec 21).")
DAILY_ROWS += DAILY(
    "wynn", "Wynn Las Vegas", "fri", "12:00", "$240 NLH Rebuy & Add-On — $40K GTD", 240, 40000,
    25000, 30, 50, 190, "rebuy_addon",
    "'Registration, rebuys and add-ons will be available until the start of level 9 ... Re-entry is NOT allowed.' 'Unlimited $200 rebuys for 25,000 tournament chips are available any time a player is at 15,000 chips or less. One (1) $100 add-on for 15,000 tournament chips is available any time until the end of registration.'",
    ["W_DAILY_POSTER", "W_DAILY_STRUCT"],
    notes="No re-entry, but unlimited rebuys plus a paid add-on — an explicit spend-more structure.")
DAILY_ROWS += DAILY(
    "wynn", "Wynn Las Vegas", ["sat", "sun"], "12:00", "$200 NLH Daily — $25K GTD", 200, 25000,
    25000, 30, 38, 162, "reentry_allowed",
    "'Registration, re-entries, and one (1) add-on per entry will be available until the start of level 11 (approximately 5:30 p.m.).' 'One (1) $100 add-on for 25,000 tournament chips.'",
    ["W_DAILY_POSTER", "W_DAILY_STRUCT"])
DAILY_ROWS += DAILY(
    "wynn", "Wynn Las Vegas", "*", "18:00", "$160 NLH Nightly — $10K GTD", 160, 10000,
    25000, 20, 30, 130, "reentry_addon",
    "'The Tournament entry fee, as well as the re-entry fee, is $160.' 'Registration, re-entries, and one (1) add-on per entry will be available until the start of level 9 (approximately 9:00 p.m.).'",
    ["W_DAILY_POSTER", "W_DAILY_STRUCT"])

# MGM Grand
DAILY_ROWS += DAILY(
    "mgm-grand", "MGM Grand Las Vegas", "*", "11:10", "$120 NLH Daily", 120, None,
    25000, 15, 28, 92, "not_stated",
    "'Each initial $120 buy-in is allocated as follows: $92 to Prize Pool, $13 House Fee and a onetime, voluntary gratuity of $11 which grants players an extra 10,000 chips. $4 will fund Tournament Promotions.' 'Registration is open until Level 8.' No maximum-entry or re-entry limit is stated on the structure sheet.",
    ["M_POKER", "M_SCHED_PDF", "M_STRUCT_PDF"],
    notes="Paid 'voluntary' $11 gratuity buys +10,000 chips — a spend-more mechanic even though re-entry is not stated.")
DAILY_ROWS += DAILY(
    "mgm-grand", "MGM Grand Las Vegas", "*", "19:10", "$120 NLH Daily", 120, None,
    25000, 15, 28, 92, "not_stated", "Same structure sheet as the 11:10 a.m. $120 event.",
    ["M_POKER", "M_SCHED_PDF", "M_STRUCT_PDF"])
DAILY_ROWS += DAILY(
    "mgm-grand", "MGM Grand Las Vegas", "*", "23:10", "$120 NLH Daily", 120, None,
    25000, 15, 28, 92, "not_stated", "Same structure sheet as the 11:10 a.m. $120 event.",
    ["M_POKER", "M_SCHED_PDF", "M_STRUCT_PDF"])
DAILY_ROWS += DAILY(
    "mgm-grand", "MGM Grand Las Vegas", "sat", "11:10", "$150 NLH — $2,000 GTD", 150, 2000,
    25000, 20, None, None, "not_stated",
    "Saturday 11:10 a.m. $150 NLH, 25K chips, 20-minute levels, $2,000 guarantee (schedule PDF). No structure sheet read for the $150.",
    ["M_POKER", "M_SCHED_PDF"])

# Bellagio
DAILY_ROWS += DAILY(
    "bellagio", "Bellagio", "fri", "11:00", "$600 NLH Friday", 600, None, 30000, 30,
    90, 510, "reentry_allowed",
    "'Players may buy-in and re-enter through the end of level 8 (Including Break).' 'The $600 Buy-In is allocated as follows: $510 to Prize Pool; $50 House Fee; $40 Voluntary Staff Gratuity.' 'The voluntary staff gratuity will grant players an extra 15,000 chips.'",
    ["B_POKER", "B_FRI_PDF"],
    notes="Re-entry plus an optional $40 gratuity that buys +15,000 chips.")
DAILY_ROWS += DAILY(
    "bellagio", "Bellagio", "sat", "11:00", "$1,100 NLH Saturday (multi-flight)", 1100, 50000, 40000, 30,
    None, None, "reentry_allowed",
    "'Registration will be open until the start of Level 10.' 'The voluntary staff gratuity will grant players an extra 20,000 chips.' The PDF is titled '$1100 BUY-IN' but its own rules text refers to 'the $600 Buy-in' — the two statements conflict.",
    ["B_POKER", "B_SAT_PDF"],
    notes="Conflicting buy-in stated inside the official PDF; treat the $1,100 headline as unverified.")

# Horseshoe (editorial source only)
DAILY_ROWS += DAILY(
    "horseshoe", "Horseshoe Las Vegas", "*", "09:00", "Horseshoe Daily NLH (9 AM slot)", None, None,
    None, None, None, None, "not_stated",
    "Caesars' own Las Vegas guide lists six daily Horseshoe tournaments at '9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m. and 11 p.m.' with '$100 or $160 buy-in'. No Horseshoe poker-room flyer, structure sheet or entry rule could be retrieved.",
    ["C_STRIP_ARTICLE", "H_POKER"],
    notes="Buy-in, guarantee and entry rules unverified — editorial page only.")
for t in ["11:00", "14:00", "17:00", "20:00", "23:00"]:
    DAILY_ROWS += DAILY(
        "horseshoe", "Horseshoe Las Vegas", "*", t, f"Horseshoe Daily NLH ({t} slot)", None, None,
        None, None, None, None, "not_stated",
        "Caesars' own Las Vegas guide lists six daily Horseshoe tournaments at 9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m. and 11 p.m. No flyer or structure sheet retrieved.",
        ["C_STRIP_ARTICLE", "H_POKER"],
        notes="Buy-in, guarantee and entry rules unverified — editorial page only.")

# Late registration closes by LEVEL for four venues, stated in their own words.
# We record the level, not a clock time: converting a level to a time would need
# the break schedule, and the Wynn's own sheet shows that shortcut is wrong (it
# publishes "start of level 9 (approximately 4:30 p.m.)" for a level that plain
# arithmetic puts at 4:00 p.m.). A level is a published fact; a derived clock
# time is not.
REG_CLOSE_LEVEL = {
    "caesars-palace": 7,
    "mgm-grand": 8,
    "wynn": 9,
    "bellagio": 8,
}
for _r in DAILY_ROWS:
    _r["sheet_read"] = _r["venue"] != "horseshoe"
for _r in DAILY_ROWS:
    if _r["venue"] in REG_CLOSE_LEVEL:
        _r["reg_close_level"] = REG_CLOSE_LEVEL[_r["venue"]]
        _r["reg_close_level_note"] = {
            "caesars-palace": "Flyer: registration closes at the start of level 7.",
            "mgm-grand": "Structure sheet: 'Registration is open until Level 8.'",
            "wynn": "Poster: registration and re-entries available until the start of level 9 "
                    "(the poster itself says 'approximately 4:30 p.m.' for the noon event).",
            "bellagio": "Structure sheet: buy-in and re-entry through the end of level 8 (including break).",
        }[_r["venue"]]

# The Wynn suspends its entire daily slate for the WPT World Championship.
for _r in DAILY_ROWS:
    if _r["venue"] == "wynn":
        _r["suspended"] = ["2026-11-27", "2026-12-21"]

for i, e in enumerate(DAILY_ROWS):
    e["id"] = f"D-{i+1:03d}"

EVENTS = VENETIAN + WYNN + DAILY_ROWS

# ---------------------------------------------------------------------------
# HOTELS — every number read from the property's own page
# ---------------------------------------------------------------------------
HOTELS = [
    dict(
        id="venetian", name="The Venetian Resort", venue_with_poker="venetian",
        address="3355 S Las Vegas Blvd, Las Vegas, NV 89109",
        resort_fee=55.00, resort_fee_note="$55 plus tax per night, payable upon check-in.",
        tax_rate=0.1338, tax_note="Clark County Room Tax of 13.38% (stated on the Venetian hotel terms page).",
        published_rate=119.00,
        rate_note="Published poker starting rate 'as low as $119' (Venetian) — a starting rate, not a dated quote. Booked by phone only, code EPOKR25, maximum 150 days ahead.",
        parking="Registered hotel guests $20/day; non-hotel guests $20 Mon–Thu, $25 Fri–Sun; valet $40/day. Sapphire+ members park free.",
        cancellation="Deposit of one night (suite + fee + tax) at booking; prepaid offers are non-cancellable and non-refundable.",
        checkin="Check-in 3:00 p.m. – 11:59 p.m.; check-out 11:00 a.m.",
        quality_note="50-table / 14,000 sq ft poker room on level 2 of the Grand Canal Shoppes at The Palazzo — the largest poker room on the Strip by table count per the property's own page.",
        sources=["V_RESORT_FEE", "V_HOTEL_TC", "V_SUITE_RATES", "V_POKER"],
    ),
    dict(
        id="palazzo", name="The Palazzo (same resort as The Venetian)", venue_with_poker="venetian",
        address="3325 S Las Vegas Blvd, Las Vegas, NV 89109",
        resort_fee=55.00, resort_fee_note="$55 plus tax per night — the resort-fee page covers The Venetian and The Palazzo.",
        tax_rate=0.1338, tax_note="Clark County Room Tax of 13.38% (Venetian hotel terms).",
        published_rate=209.00,
        rate_note="Published poker starting rate 'as low as $209' — the same page gives $119 and $209 without explicitly mapping each figure to a property. Flagged as an unmapped pair.",
        parking="Same resort parking schedule as The Venetian.",
        cancellation="Same resort terms as The Venetian.",
        checkin="Check-in 3:00 p.m.; check-out 11:00 a.m.",
        quality_note="Shares the same 50-table poker room as The Venetian.",
        sources=["V_RESORT_FEE", "V_HOTEL_TC", "V_SUITE_RATES"],
    ),
    dict(
        id="wynn", name="Wynn Las Vegas", venue_with_poker="wynn",
        address="3131 S Las Vegas Blvd, Las Vegas, NV 89109",
        resort_fee=55.00, resort_fee_note="$55 plus tax per room night; includes self-parking for up to two vehicles.",
        tax_rate=None, tax_note="Wynn's page does not print the percentage; it says '$55 plus tax'. The 13.38% Clark County rate appears on the Venetian page, not Wynn's.",
        published_rate=None,
        rate_note="No published starting rate, no dated quote. Wynn offers a mail-in poker reservation address (poker.reservations@wynnlasvegas.com) but publishes no price.",
        parking="Complimentary self-parking for up to two vehicles is included in the resort fee.",
        cancellation="One night's room rate and tax charged at booking.",
        checkin="Check-in 3:00 p.m.; check-out 12:00 p.m.",
        quality_note="Wynn Tower Suites holds a Forbes Travel Guide Five-Star rating (Tower Suites only, not the whole hotel). Poker room is inside Encore at Wynn Las Vegas per the tournament terms.",
        sources=["W_RESORT_INFO", "W_POKER", "W_WPT_STRUCT"],
    ),
    dict(
        id="bellagio", name="Bellagio", venue_with_poker="bellagio",
        address="3600 S Las Vegas Blvd, Las Vegas, NV 89109",
        resort_fee=55.00, resort_fee_note="$55 plus applicable tax; waived for MGM Rewards Gold+ on eligible reservations.",
        tax_rate=None, tax_note="Bellagio's terms say 'plus applicable tax' without a percentage.",
        published_rate=None, rate_note="No published rate and no dated quote retrieved.",
        parking="Not stated on the terms page read.",
        cancellation="First night refundable if cancelled at least 72 hours before arrival.",
        checkin="Not stated on the page read; terms reference a $150/day incidental authorisation.",
        quality_note="Poker room on the north side of the casino next to the sportsbook; the property advertises the only medium/high-limit Limit Hold'em on the Strip.",
        sources=["B_TC", "B_POKER"],
    ),
    dict(
        id="mgm-grand", name="MGM Grand Las Vegas", venue_with_poker="mgm-grand",
        address="3799 S Las Vegas Blvd, Las Vegas, NV 89109",
        resort_fee=50.00, resort_fee_note="$50 plus applicable tax; waived for MGM Rewards Gold+ on eligible reservations.",
        tax_rate=None, tax_note="Terms say 'plus applicable tax' without a percentage.",
        published_rate=None, rate_note="No published rate and no dated quote retrieved.",
        parking="Not stated on the terms page read.",
        cancellation="First night refundable if cancelled at least 72 hours before arrival.",
        checkin="Check-in 3:00 p.m.; check-out 11:00 a.m.",
        quality_note="Non-smoking poker room open 24 hours; advertises the deepest $1–$3 NLH action on the Strip.",
        sources=["M_TC", "M_POKER"],
    ),
    dict(
        id="caesars-palace", name="Caesars Palace", venue_with_poker="caesars-palace",
        address="3570 S Las Vegas Blvd, Las Vegas, NV 89109",
        resort_fee=None, resort_fee_note="Not verified. The Caesars resort-fee URL redirects to the hotel landing page and no fee figure was readable from an official Caesars page in this session. Third-party trackers quote $54.95 + tax; that figure is NOT used here.",
        tax_rate=None, tax_note="Not verified from an official page.",
        published_rate=None, rate_note="No published rate and no dated quote retrieved.",
        parking="Not verified.",
        cancellation="Caesars Palace pages advertise 'FREE 48-Hour Cancellation' with terms marked by an asterisk; the terms text was not retrieved.",
        checkin="Not verified.",
        quality_note="16-table poker room on the Appian Way promenade; open 24/7 with four daily tournaments.",
        sources=["C_POKER", "C_DAILY_PDF", "C_STRIP_ARTICLE"],
    ),
    dict(
        id="horseshoe", name="Horseshoe Las Vegas", venue_with_poker="horseshoe",
        address="3645 S Las Vegas Blvd, Las Vegas, NV 89109",
        resort_fee=None, resort_fee_note="Not verified in this session.",
        tax_rate=None, tax_note="Not verified.",
        published_rate=None, rate_note="No published rate and no dated quote retrieved.",
        parking="Not verified.", cancellation="Not verified.", checkin="Not verified.",
        quality_note="Hall of Fame Poker Room, 20 tables, described by Caesars as adjacent to the resort's front entrance near the Lobby Bar.",
        sources=["H_POKER", "C_STRIP_ARTICLE"],
    ),
]

# ---------------------------------------------------------------------------
# WALKING MATRIX — Google Maps walking routes measured 2026-11-16
# ---------------------------------------------------------------------------
_WALK_RAW = [
    # (origin, dest, minutes, distance, note)
    ("palazzo", "venetian", 4, "443 ft", "Palazzo lobby → poker room (level 2, Grand Canal Shoppes)."),
    ("venetian", "venetian", 7, "0.3 mi", "Venetian lobby → poker room."),
    ("wynn", "venetian", 12, "0.5 mi", "Wynn → Venetian poker room via Wynn Main Gate Dr."),
    ("wynn", "wynn", 7, "0.3 mi", "Wynn → poker room located inside Encore."),
    ("caesars-palace", "venetian", 19, "0.8 mi", "Caesars Palace → Venetian poker room via Las Vegas Blvd S."),
    ("bellagio", "venetian", 28, "1.1 mi", "Bellagio → Venetian poker room; an alternative route measures 30 min / 1.3 mi."),
    ("caesars-palace", "caesars-palace", 3, "—", "Distance only; the poker room is inside the property."),
    ("bellagio", "caesars-palace", 13, "0.6 mi", "Bellagio → Caesars Palace poker room via Las Vegas Blvd Overpass."),
    ("palazzo", "caesars-palace", 15, "0.6 mi", "Palazzo → Caesars Palace poker room."),
    ("wynn", "caesars-palace", 22, "1.0 mi", "Wynn → Caesars Palace poker room."),
    ("caesars-palace", "horseshoe", 11, "0.4 mi", "Caesars Palace → Horseshoe poker room via Las Vegas Blvd Overpass."),
    ("palazzo", "horseshoe", 22, "1.0 mi", "Palazzo → Horseshoe poker room."),
    ("palazzo", "bellagio", 22, "0.9 mi", "Palazzo → Bellagio poker room."),
    ("palazzo", "mgm-grand", 39, "1.7 mi", "Palazzo → MGM Grand — over the 30-minute limit."),
]
WALKS = []
for o, d, mins, dist, note in _WALK_RAW:
    WALKS.append(dict(origin=o, destination=d, minutes=mins, distance=dist,
                      within_30=mins <= 30, note=note, source="G_WALK"))

# ---------------------------------------------------------------------------
# DATED RATE LOG — rates are kept as a log, never as one overwritten value
# ---------------------------------------------------------------------------
RATE_LOG = [
    dict(logged="2026-11-16", hotel="venetian", kind="published_starting_rate",
         amount=119.00, basis="nightly room rate before resort fee and tax",
         stay_dates=None, occupancy="single/double (Luxury King Suite)",
         source="V_SUITE_RATES",
         note="Official page wording: poker suite rates 'will start as low as $119 and $209 and can be higher'. Not a dated quote; requires 6 hours of live cash play or a $300+ tournament buy-in per night."),
    dict(logged="2026-11-16", hotel="venetian", kind="mandatory_resort_fee",
         amount=55.00, basis="per night, plus tax", stay_dates=None, occupancy="per suite",
         source="V_RESORT_FEE", note="Unchanged on both the resort-fee page and the hotel terms page."),
    dict(logged="2026-11-16", hotel="palazzo", kind="published_starting_rate",
         amount=209.00, basis="nightly room rate before resort fee and tax",
         stay_dates=None, occupancy="single/double",
         source="V_SUITE_RATES",
         note="Same page as the $119 figure; the page does not explicitly say which property each number belongs to. Unmapped."),
    dict(logged="2026-11-16", hotel="venetian", kind="room_tax_rate",
         amount=None, basis="13.38% Clark County Room Tax",
         stay_dates=None, occupancy="—", source="V_HOTEL_TC",
         note="Printed as a percentage, so no currency amount is recorded."),
    dict(logged="2026-11-16", hotel="wynn", kind="mandatory_resort_fee",
         amount=55.00, basis="per room night, plus tax", stay_dates=None, occupancy="per room",
         source="W_RESORT_INFO", note="Wynn does not print the tax percentage on this page."),
    dict(logged="2026-11-16", hotel="bellagio", kind="mandatory_resort_fee",
         amount=55.00, basis="per night, plus applicable tax", stay_dates=None, occupancy="per room",
         source="B_TC", note="Waived for MGM Rewards Gold+ on eligible reservations."),
    dict(logged="2026-11-16", hotel="mgm-grand", kind="mandatory_resort_fee",
         amount=50.00, basis="per night, plus applicable tax", stay_dates=None, occupancy="per room",
         source="M_TC", note="Waived for MGM Rewards Gold+ on eligible reservations."),
    dict(logged="2026-11-16", hotel="caesars-palace", kind="dated_room_quote",
         amount=None, basis="—", stay_dates=None, occupancy="—", source=None,
         note="No dated checkout quote could be captured. The Venetian and Caesars booking engines render placeholder '$XXX' prices to a non-browser client, so no room total is recorded for any date."),
]

# ---------------------------------------------------------------------------
# FLAGS — irregularities found while re-reading the sources
# ---------------------------------------------------------------------------
FLAGS = [
    dict(id="F-01", severity="high", subject="Single-entry status",
         finding="Not one Strip event in this dataset has an official source that confirms a single entry / no re-entry limit.",
         detail="The Venetian DSE IV structure sheets that were opened (14 of 37) set the buy-in, fee split, starting chips, level length and late-registration close, and they restrict play after a player bags chips for Day 2 — but none of them states a maximum number of entries, a no-re-entry rule or a no-add-on rule. The remaining 23 Venetian sheets were not opened and are treated as unverified. Wynn, Bellagio and Caesars Palace all state re-entry or rebuy/add-on mechanics in their own terms.",
         action="Do not label any event 'single-entry confirmed'. Ask each poker room, in writing, for the maximum-entry rule per event before booking.",
         sources=["S_V5", "S_V7", "S_V34", "W_WPT_STRUCT", "B_FRI_PDF", "C_DAILY_PDF"]),
    dict(id="F-02", severity="high", subject="8 AM start",
         finding="No verified Strip tournament starts at 8:00 AM, so the requested 8 AM all-day schedule cannot be built from official sources.",
         detail="Earliest verified starts: Caesars Palace 10:00 AM (official flyer), Venetian 10:10 AM (official schedule). Horseshoe is listed at 9:00 AM but only on a Caesars editorial page, not the room's own flyer. Wynn, Bellagio and MGM Grand all start at 11:00–12:00.",
         action="Either accept a 10:00 AM start or verify the Horseshoe 9 AM slot with the room directly.",
         sources=["C_DAILY_PDF", "V_SCHED_TABLE", "C_STRIP_ARTICLE"]),
    dict(id="F-03", severity="high", subject="Dated hotel totals",
         finding="No dated checkout total exists anywhere in this dataset.",
         detail="The Venetian booking calendar and the Caesars booking flow return '$XXX' placeholders to a non-browser client, and the Wynn room pages return a 'page has checked out' stub. The published $119 / $209 figures are starting rates conditional on six hours of play per night, not quotes.",
         action="A human has to open each booking page in a browser, pick the exact dates, and capture the checkout total, the nightly average, the fee and tax lines and the cancellation deadline.",
         sources=["V_SUITE_RATES", "V_HOTEL_TC", "W_RESORT_INFO"]),
    dict(id="F-04", severity="medium", subject="Venetian poker-rate mapping",
         finding="The Venice/Palazzo poker-rate page prints '$119 and $209' without saying which property gets which number.",
         detail="Wording: 'These rates will start as low as $119 and $209 and can be higher.' Both properties are named in the preceding sentence, so the mapping is ambiguous. Earlier dashboards in this repo assigned $119 to the Venetian and $209 to the Palazzo; that assignment is an inference.",
         action="Confirm the mapping by phone (866.255.8936, code EPOKR25) before using either figure.",
         sources=["V_SUITE_RATES"]),
    dict(id="F-05", severity="medium", subject="Bellagio Saturday buy-in",
         finding="The official Saturday Bellagio PDF contradicts itself: titled '$1100 BUY-IN' but its rules say 'Of the $600 Buy-in, $510 goes to the Prize Pool'.",
         detail="Both statements are in the same official document. The $1,100 headline and the $600 fee split cannot both be right.",
         action="Treat the Saturday buy-in as unverified; confirm with the Bellagio poker room (702.693.7291).",
         sources=["B_SAT_PDF"]),
    dict(id="F-06", severity="medium", subject="MGM Grand schedule month label",
         finding="The MGM Grand weekly schedule PDF is headed 'MGM Grand August Tournament Schedule' and is not dated otherwise.",
         detail="The daily times (11:10am / 7:10pm / 11:10pm) match the live MGM Grand poker page, but the PDF itself may be an August edition still being served in November.",
         action="Confirm with the MGM Grand poker room (702.891.7434) that the times are current.",
         sources=["M_SCHED_PDF", "M_POKER"]),
    dict(id="F-07", severity="medium", subject="Horseshoe schedule source",
         finding="Horseshoe's six daily start times appear only on a Caesars editorial article, not the poker room's own flyer.",
         detail="caesars.com/las-vegas/explore/... lists 9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m. and 11 p.m. No Horseshoe buy-in, guarantee, structure or entry rule could be retrieved, and the direct PDF guesses returned empty documents.",
         action="Ask the Horseshoe poker room for its current flyer before relying on any Horseshoe row.",
         sources=["C_STRIP_ARTICLE", "H_POKER"]),
    dict(id="F-08", severity="medium", subject="Caesars Palace resort fee",
         finding="No official Caesars page would render a resort-fee figure.",
         detail="caesars.com/caesars-palace/hotel/resort-fee redirects to the hotel landing page. Third-party trackers quote $54.95 + tax; that number is deliberately NOT entered in the hotel table.",
         action="Read the fee from a live booking confirmation or ask the property.",
         sources=["C_POKER"]),
    dict(id="F-09", severity="low", subject="Wynn poker room building",
         finding="Wynn's own terms say the poker room is 'located in Encore at Wynn Las Vegas', while the room is marketed as 'Wynn Las Vegas Poker Room'.",
         detail="The Encore building is part of the same resort across a pedestrian bridge, but a guest booking 'Wynn' rather than 'Encore' should know the walk.",
         action="None needed; walking time between the two towers is included in the walking table.",
         sources=["W_WPT_STRUCT", "W_POKER"]),
    dict(id="F-10", severity="low", subject="Wynn WPT $160 nightly / $200 daily add-ons",
         finding="Every Wynn daily event carries a paid add-on or re-entries, so none qualifies as single-entry.",
         detail="Mon–Thu $200: re-entry allowed. Fri $240: 'Re-entry is NOT allowed' but unlimited $200 rebuys and one $100 add-on. Sat/Sun $200: re-entries plus one add-on per entry. Nightly $160: re-entries plus one add-on per entry.",
         action="Treat the whole Wynn daily slate as spend-more. It is shown on the spend-more page, not the single-entry page.",
         sources=["W_DAILY_STRUCT"]),
    dict(id="F-11", severity="low", subject="Walking times are point-to-point",
         finding="The walking minutes come from Google Maps' routing between property pins, not from a published casino-floor route.",
         detail="Google Maps is a routing service, not an official property source, and its pin for a property is not necessarily the lobby door. Times also do not include the walk from the hotel room to the lobby.",
         action="Treat every walk time as a floor, not a guaranteed measure, and add 5–10 minutes of building-internal walking.",
         sources=["G_WALK", "V_POKER"]),
    dict(id="F-12", severity="low", subject="Same-day multi-tournament assumption",
         finding="No source publishes a finish time for any event, so a two-tournament day cannot be verified.",
         detail="The schedule publishes start times and late-registration cut-offs only. The 'derived maximum length' used on the Day Plan page is arithmetic on the published structure (levels × level length + breaks), not a published finish time.",
         action="Use the day plan as a primary event plus a conditional fallback, never as a guaranteed double.",
         sources=["V_SCHED_PDF", "S_V7"]),
    dict(id="F-13", severity="low", subject="Repo contains four overlapping dashboards",
         finding="Before this consolidation the repository published four separate dashboards at /, /pages/, /docs/ and /verified/, with overlapping and sometimes conflicting numbers.",
         detail="They were built by earlier parallel sessions. Their files are preserved under archive/ and are no longer linked from the main navigation.",
         action="Review the archived copies if any number looks different from what you remember. This dashboard supersedes them.",
         sources=[]),
]

# ---------------------------------------------------------------------------
# QUESTIONS the decision depends on
# ---------------------------------------------------------------------------
QUESTIONS = [
    dict(id="Q-01", priority="blocking",
         question="What are the exact trip dates and the number of nights?",
         known="The verified Strip calendar runs Nov 16 – Dec 23, 2026 (Venetian DSE IV) and Nov 27 – Dec 21 (Wynn WPT).",
         missing="Nothing in the repo fixes a stay window. Room totals, walk-day routing and event choices are all date-specific.",
         how_to_close="Pick a 7-night window inside Nov 25 – Dec 23, 2026 (the only window where two properties both publish schedules).",
         affects="Hotel cost, trip cost, day plan"),
    dict(id="Q-02", priority="blocking",
         question="Is a maximum of one entry per event actually required, and would the player accept a re-entry event if it were cheap?",
         known="Zero events are confirmed single-entry. Every property that states a rule states re-entry, rebuy or a paid add-on.",
         missing="Whether the user's 'single entry only' rule is hard (never play a re-entry event) or soft (prefer single-entry, accept a capped event).",
         how_to_close="Answer the constraint question. If hard, the dataset yields no bookable event and the trip is not possible on official information.",
         affects="Everything on the ranking page"),
    dict(id="Q-03", priority="blocking",
         question="What is the maximum total buy-in per day and for the trip?",
         known="Verified buy-ins in the window range from $100 (Caesars Palace daily) to $25,800 (Wynn High Roller).",
         missing="No bankroll or per-day cap was supplied, so the ranking cannot apply a cost ceiling.",
         how_to_close="State a per-day and a trip maximum.",
         affects="Ranking, day plan, trip cost"),
    dict(id="Q-04", priority="blocking",
         question="What hotel quality floor is acceptable, and is the poker rate (which requires 6 hours of play per night) acceptable?",
         known="Venetian publishes a poker rate from $119/$209 that requires six hours of live cash play or a $300+ tournament buy-in per night, or the rate reverts to the prevailing rate.",
         missing="Whether the player can meet the six-hour condition on every night, and whether a 4-star or 5-star floor is required.",
         how_to_close="Choose a star floor and decide whether to book the poker rate or the public rate.",
         affects="True nightly cost, hotel ranking"),
    dict(id="Q-05", priority="blocking",
         question="Is a 10:00 AM start acceptable, given that no 8 AM tournament exists?",
         known="Earliest verified start is 10:00 AM (Caesars Palace) / 10:10 AM (Venetian). Horseshoe shows 9:00 AM on an editorial page only.",
         missing="Whether the 8 AM requirement is a hard constraint.",
         how_to_close="Accept 10 AM, or verify Horseshoe's 9 AM slot directly with the room.",
         affects="Day plan feasibility"),
    dict(id="Q-06", priority="high",
         question="Does the Venetian/Venetian-Palazzo poker room publish a maximum-entry rule anywhere not yet read?",
         known="14 of 37 DSE IV structure sheets were read in full and none states an entry cap.",
         missing="23 structure sheets unread; no Venetian tournament-rules page could be found (the /tournament-rules.html path returns 404).",
         how_to_close="Read the remaining 23 sheets, or ask lv_cas_poker@venetianlasvegas.com in writing.",
         affects="Whether any event can ever be marked single-entry"),
    dict(id="Q-07", priority="high",
         question="What is the all-in entry cost per event, including staff gratuities that buy chips?",
         known="Fee splits are verified for 14 Venetian sheets, 6 Wynn WPT events, all four Caesars Palace dailies, all four Wynn dailies and both Bellagio weeklies.",
         missing="Several Bellagio and MGM Grand events attach a *voluntary* gratuity that buys extra chips. Whether to count that as part of the entry cost is an open modelling choice, since not paying it puts you at a chip disadvantage.",
         how_to_close="Decide whether 'entry cost' means the mandatory minimum or the cost of a competitive stack (mandatory + gratuity).",
         affects="True cost per event, ranking ratio"),
    dict(id="Q-08", priority="high",
         question="Is the published guarantee actually reachable in the field sizes these events draw?",
         known="Guaranteed pool and prize-pool-per-entry are both known for most events, so the number of entries needed to fund the guarantee can be computed exactly.",
         missing="Actual field sizes are not published before the event. No historical attendance was retrieved.",
         how_to_close="Use the computed 'entries needed to fund the guarantee' as the comparison, and check the property's published results pages for past field sizes.",
         affects="Guarantee ÷ entry ratio interpretation"),
    dict(id="Q-09", priority="medium",
         question="What does a room actually cost for the chosen dates, all-in?",
         known="Resort fees are $50–$55 plus tax at every property that publishes one; the Clark County room tax is 13.38% on the Venetian page.",
         missing="Every dated room rate. Booking engines return placeholders to a non-browser client.",
         how_to_close="Capture a checkout total in a browser for the chosen dates and occupancy, and record the rate timestamp.",
         affects="True nightly cost, trip cost"),
    dict(id="Q-10", priority="medium",
         question="Do the walk times hold at the actual times of day, and from the actual hotel tower?",
         known="Google Maps walking times were measured for 14 hotel→room pairs on 2026-11-16.",
         missing="Times are point-to-point and measured at one moment; they exclude in-building walking and do not account for crowd levels.",
         how_to_close="Add 5–10 minutes per walk and re-measure on arrival.",
         affects="Hotel shortlist, day plan"),
    dict(id="Q-11", priority="medium",
         question="Which event should be the primary on each day, given that a long 1-day event blocks an evening event?",
         known="Venetian 1-day structures run up to 28 levels at 30 minutes plus seven 15-minute breaks, i.e. a derived ceiling of 15 h 45 min from the 11:10 AM start.",
         missing="Actual finish times and field sizes.",
         how_to_close="Treat the day plan's 'conditional fallback' as contingent on a bust before the fallback's late-registration close, and check the close time on the day.",
         affects="Day plan"),
    dict(id="Q-12", priority="low",
         question="Does the Bellagio and MGM Grand 'voluntary' gratuity change the effective rake?",
         known="Bellagio $40 gratuity buys +15,000 (Fri) or +20,000 (Sat) chips on top of 30,000/40,000. MGM Grand $11 buys +10,000 on top of 15,000.",
         missing="Whether declining the gratuity is realistic in a competitive field.",
         how_to_close="Model entry cost twice: minimum and with-gratuity.",
         affects="Cost per event"),
]

# ---------------------------------------------------------------------------
# SUGGESTIONS — options to review before implementing
# ---------------------------------------------------------------------------
SUGGESTIONS = [
    dict(id="S-01", status="implemented", title="Trip-cost calculator",
         what="A live calculator: (selected entries × buy-ins) + (nights × true nightly hotel cost) + parking days.",
         why="Answers 'what does this trip cost' directly instead of leaving it as a formula in prose.",
         how="trip-cost page; hotel inputs default to the published resort fee + Clark County tax and the published starting poker rate, all labelled as such.",
         effort="Done in this session."),
    dict(id="S-02", status="implemented", title="Dated rate log instead of one rate value",
         what="Every rate observation is a row with its own log date, basis, occupancy and source.",
         why="A single 'rate' field silently overwrites history and hides whether a number is a quote or a starting rate.",
         how="rates page reads data/poker/rates.json; nothing is overwritten.",
         effort="Done in this session."),
    dict(id="S-03", status="implemented", title="'Last checked' on every row",
         what="Every table row shows the date its source was last read.",
         why="A schedule with no date on it is indistinguishable from a current one.",
         how="Every row renders its source-link date (2026-11-16) next to the source link.",
         effort="Done in this session."),
    dict(id="S-04", status="implemented", title="One page per venue",
         what="Venetian, Wynn, Caesars Palace, Bellagio, MGM Grand and Horseshoe each get a page with their events, hotel terms and walk times.",
         why="The decision 'where do I stay' is per-venue, and a mixed table makes it hard to see one property's whole picture.",
         how="venues/*.html generated from the same data.",
         effort="Done in this session."),
    dict(id="S-05", status="implemented", title="Search + date + single-entry toggle",
         what="Free-text search across every table, a date picker, a venue filter and a single-entry-only toggle.",
         why="Requested directly; also the only way to answer 'what can I play on Dec 7' in one action.",
         how="Client-side filter on the events table; the single-entry toggle returns zero rows by design and says why.",
         effort="Done in this session."),
    dict(id="S-06", status="implemented", title="Schedule-overlap flags",
         what="Each day is shown as one primary event plus a conditional fallback, never two 'confirmed' events.",
         why="No source publishes finish times, so a second same-day tournament is never a certainty.",
         how="Derived maximum length from the published structure; a second event is only a fallback if its late-registration close is after the primary's derived ceiling.",
         effort="Done in this session."),
    dict(id="S-07", status="implemented", title="Walking matrix with a 30-minute test",
         what="A hotel→room table with measured minutes, distance, and a pass/fail against 30 minutes.",
         why="Requested directly; also the constraint that removes MGM Grand from a Venetian-based stay.",
         how="14 pairs measured on Google Maps on 2026-11-16 and recorded with that caveat.",
         effort="Done in this session."),
    dict(id="S-08", status="needs-review", title="Automated URL re-check + change diff",
         what="A scheduled job that re-fetches every official URL, hashes the relevant text, and marks rows whose source changed.",
         why="Requested directly. Schedules and fees change without notice.",
         how="Not implemented: it needs a GitHub Actions job with outbound network access, a stored hash per source, and a review queue. The repository's own sandbox has outbound access only to GitHub/npm/PyPI, so the check cannot run here.",
         effort="~1 hour: one workflow file, one hash store, one 'changed' badge on each row."),
    dict(id="S-09", status="needs-review", title="Live hotel-rate lookup",
         what="Query each hotel's booking API for the chosen dates and compute true cost automatically.",
         why="Requested directly, and it is the single biggest hole in the dataset.",
         how="Not implemented: the booking flows are JavaScript apps that return placeholders to non-browser clients, and scraping them is against most of these properties' terms. A compliant option is a manual capture form with a timestamp.",
         effort="Depends entirely on whether the properties offer an approved feed."),
    dict(id="S-10", status="needs-review", title="Live daily-schedule scraper",
         what="Pull each room's official daily schedule every morning.",
         why="Requested directly.",
         how="Not implemented for the same network/terms reason as S-09, and because most Strip dailies are published as PDFs whose layout changes between properties.",
         effort="PDF parsing per venue, plus a human check for layout changes."),
    dict(id="S-11", status="needs-review", title="Written single-entry confirmation per event",
         what="Replace every 'unverified' label with a written room confirmation, quoted verbatim.",
         why="This is the only thing that can make the single-entry filter return rows.",
         how="Send one email per room naming the events and asking for the maximum-entry and add-on rules. Store each reply verbatim with its date.",
         effort="Human action; cannot be automated from this sandbox."),
    dict(id="S-12", status="implemented", title="Rank only on confirmed cost and guarantee",
         what="Guarantee ÷ entry fee is shown as a descriptive ratio, with a separate 'entries needed to fund the guarantee' column.",
         why="A ratio without the entry count hides whether a guarantee is a real overlay or needs a full field.",
         how="Ranking page shows both; bounty and flight events are labelled separately.",
         effort="Done in this session."),
    dict(id="S-13", status="needs-review", title="Consolidate the four dashboards",
         what="One dashboard instead of four.",
         why="Four parallel sites with conflicting numbers is the largest source of confusion in this repository.",
         how="Applied here: the new dashboard replaces them and the old trees are archived under /archive/ with a banner.",
         effort="Done in this session — review the archive before deleting it."),
    dict(
        id="S-14",
        status="needs-review",
        title="Collapse the two surviving data modules into one",
        what="The repository now holds scripts/poker_data.py (this build's dataset, 237 rows) and "
             "scripts/dataset.py (session arena/7a4b09e2-poker2's dataset, 96 rows). Both describe the same "
             "official documents. Merging them into one module would remove the last duplicate source of "
             "truth.",
        why="Two modules can drift. The whole point of this consolidation was that one number should live in "
            "one place; leaving two data layers is the same defect this rebuild was meant to fix, just "
            "smaller.",
        how="Diff the two event lists key by key, prefer the sheet-transcribed value where they disagree, "
            "keep the 37-sheet sweep's per-event findings, then delete the loser and re-point its generator.",
        effort="Needs review, not code: scripts/dataset.py and scripts/build.py belong to another session, "
               "and COORDINATION.md forbids editing another session's files from inside an integration "
               "session. It needs that session's owner, or an explicit hand-off.",
    ),
]


# ---------------------------------------------------------------------------
# VENUES
# ---------------------------------------------------------------------------
VENUES = [
    dict(id="venetian", name="The Venetian / The Palazzo",
         poker_room="The Palazzo, level 2, Grand Canal Shoppes — 50 tables, 14,000 sq ft, open 24 hours",
         address="3355 S Las Vegas Blvd, Las Vegas, NV 89109 (Palazzo: 3325 S Las Vegas Blvd)",
         phone="702.414.7657", email="lv_cas_poker@venetianlasvegas.com",
         schedule_kind="Festival — DeepStack Extravaganza IV, Nov 16 – Dec 23, 2026",
         series_guarantee="More than $3.6 million in guaranteed prize pools (property's own figure)",
         sources=["V_POKER", "V_SCHED_TABLE", "V_SERIES"]),
    dict(id="wynn", name="Wynn / Encore Las Vegas",
         poker_room="Inside Encore at Wynn Las Vegas — open 24 hours; daily tournaments suspended during series",
         address="3131 S Las Vegas Blvd, Las Vegas, NV 89109",
         phone="702-770-7654", email="poker.reservations@wynnlasvegas.com",
         schedule_kind="Festival — WPT World Championship, Nov 27 – Dec 21, 2026, plus a daily slate when no series is running",
         series_guarantee="Headline guarantees: $5,000,000 WPT Prime Championship, $3,000,000 Super Gold Million, $2,000,000 NLH, $1,000,000 WPT World Championship (plus $1,000,000 added by ClubWPT Gold)",
         sources=["W_POKER", "W_WPT_SCHED", "W_WPT_STRUCT", "W_DAILY_POSTER"]),
    dict(id="caesars-palace", name="Caesars Palace",
         poker_room="16 tables, on the Appian Way promenade; open 24/7",
         address="3570 S Las Vegas Blvd, Las Vegas, NV 89109",
         phone=None, email=None,
         schedule_kind="Daily — four No-Limit Hold'em tournaments every day",
         series_guarantee="$1,000 guarantee per daily tournament",
         sources=["C_POKER", "C_DAILY_PDF", "C_STRIP_ARTICLE"]),
    dict(id="bellagio", name="Bellagio",
         poker_room="North side of the casino, next to the sportsbook",
         address="3600 S Las Vegas Blvd, Las Vegas, NV 89109",
         phone="702.693.7291", email="pcohen@bellagioresort.com",
         schedule_kind="Weekly — Friday $600 NLH, Saturday $1,100 NLH, Sunday $400 H.O.R.S.E; nightly 6 PM PLO Double Bomb Pot (cash)",
         series_guarantee="Saturday event guarantees a combined prize pool of at least $50,000",
         sources=["B_POKER", "B_FRI_PDF", "B_SAT_PDF"]),
    dict(id="mgm-grand", name="MGM Grand Las Vegas",
         poker_room="Non-smoking poker room, open 24 hours",
         address="3799 S Las Vegas Blvd, Las Vegas, NV 89109",
         phone="702.891.7434", email=None,
         schedule_kind="Daily — 11:10 a.m., 7:10 p.m., 11:10 p.m. $120 NLH",
         series_guarantee="$2,000 guarantee on the Saturday $150 NLH",
         sources=["M_POKER", "M_SCHED_PDF", "M_STRUCT_PDF"]),
    dict(id="horseshoe", name="Horseshoe Las Vegas",
         poker_room="Hall of Fame Poker Room — 20 tables",
         address="3645 S Las Vegas Blvd, Las Vegas, NV 89109",
         phone=None, email=None,
         schedule_kind="Daily — six start times per Caesars' own guide (9 a.m., 11 a.m., 2 p.m., 5 p.m., 8 p.m., 11 p.m.)",
         series_guarantee="Not published anywhere retrievable",
         sources=["H_POKER", "C_STRIP_ARTICLE"]),
]


def build():
    return dict(
        as_of=RETRIEVED,
        venues=VENUES,
        events=EVENTS,
        hotels=HOTELS,
        walks=WALKS,
        rates=RATE_LOG,
        flags=FLAGS,
        questions=QUESTIONS,
        suggestions=SUGGESTIONS,
        sources=SOURCES,
        struct_read=sorted(STRUCT_READ),
        struct_total=len(STRUCT_SHEETS),
    )


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "data", "poker")
    os.makedirs(out, exist_ok=True)
    payload = build()
    with open(os.path.join(out, "dataset.json"), "w") as fh:
        json.dump(payload, fh, indent=1, sort_keys=False)
    print("events:", len(payload["events"]),
          "hotels:", len(payload["hotels"]),
          "walks:", len(payload["walks"]),
          "rates:", len(payload["rates"]),
          "flags:", len(payload["flags"]),
          "questions:", len(payload["questions"]),
          "suggestions:", len(payload["suggestions"]),
          "sources:", len(payload["sources"]))


if __name__ == "__main__":
    main()
