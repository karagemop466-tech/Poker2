#!/usr/bin/env python3
"""Assemble data/site/*.json from the 2026-11-16 first-hand verification pass.

Every event row records structured rule fields (single-entry / re-entry / rebuy /
add-on / house fee) with a source excerpt and retrieval date. Venetian values
come from structure sheets read in full this session (all sheets 1-37). Wynn WPT
values come from the official WPT World Championship structures PDF read in full
this session (8 chunks) plus the official schedule PDF rows. Nothing is inferred:
where an official source is silent the value is null / "not stated".
"""
import json, os

RETRIEVED = "2026-11-16"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "site")
os.makedirs(OUT, exist_ok=True)

V_SCHED = "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"
V_PAGE = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
def V_STRUCT(n):
    return f"https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{n}.pdf"
W_SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
W_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"
W_DAILY = "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"
W_POSTER = "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"
W_POKER = "https://www.wynnlasvegas.com/casino/poker"
CAESARS = "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"
CAESARS_FLIER = "https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf"
MGM_POKER = "https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html"
V_HOTEL_TC = "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"
V_RESORT_FEE = "https://www.venetianlasvegas.com/resort/resort-fee.html"
V_SUITE_RATES = "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"
V_POKER = "https://www.venetianlasvegas.com/resort/casino/poker.html"
W_RESORT_INFO = "https://www.wynnlasvegas.com/about-us/resort-information"
MGM_TC = "https://www.mgmresorts.com/en/hotel/terms-and-conditions.html"

SOURCES = {
  "V_PAGE": {"label": "Venetian DSE IV event page (Nov 16 – Dec 23, 2026)", "url": V_PAGE, "publisher": "The Venetian Las Vegas (official)", "type": "Official schedule page"},
  "V_SCHED": {"label": "Venetian DSE IV schedule PDF", "url": V_SCHED, "publisher": "The Venetian Las Vegas (official)", "type": "Official schedule PDF"},
  "W_SCHED": {"label": "Wynn WPT World Championship schedule PDF (Nov 27 – Dec 21, 2026)", "url": W_SCHED, "publisher": "Wynn Las Vegas (official)", "type": "Official schedule PDF"},
  "W_STRUCT": {"label": "Wynn WPT World Championship terms & structures PDF", "url": W_STRUCT, "publisher": "Wynn Las Vegas (official)", "type": "Official terms PDF"},
  "W_DAILY": {"label": "Wynn daily tournament structures PDF", "url": W_DAILY, "publisher": "Wynn Las Vegas (official)", "type": "Official structure PDF"},
  "W_POKER": {"label": "Wynn poker room page", "url": W_POKER, "publisher": "Wynn Las Vegas (official)", "type": "Official poker room page"},
  "CAESARS": {"label": "Caesars Las Vegas poker tournaments guide", "url": CAESARS, "publisher": "Caesars Entertainment (official)", "type": "Official guide page"},
  "CAESARS_FLIER": {"label": "Caesars Palace daily NLH tournament flier PDF", "url": CAESARS_FLIER, "publisher": "Caesars Entertainment (official)", "type": "Official flier PDF"},
  "MGM_POKER": {"label": "MGM Grand poker tables page", "url": MGM_POKER, "publisher": "MGM Grand (official)", "type": "Official poker room page"},
  "V_HOTEL_TC": {"label": "Venetian hotel terms & conditions (13.38% room tax, parking, deposit)", "url": V_HOTEL_TC, "publisher": "The Venetian Las Vegas (official)", "type": "Official terms"},
  "V_RESORT_FEE": {"label": "Venetian resort fee page ($55 plus tax)", "url": V_RESORT_FEE, "publisher": "The Venetian Las Vegas (official)", "type": "Official fee page"},
  "V_SUITE_RATES": {"label": "Venetian poker suite/player rates page", "url": V_SUITE_RATES, "publisher": "The Venetian Las Vegas (official)", "type": "Official rate page"},
  "V_POKER": {"label": "Venetian poker room page (location, parking)", "url": V_POKER, "publisher": "The Venetian Las Vegas (official)", "type": "Official poker room page"},
  "W_RESORT_INFO": {"label": "Wynn resort information (resort fee $55 plus tax)", "url": W_RESORT_INFO, "publisher": "Wynn Las Vegas (official)", "type": "Official fee page"},
  "MGM_TC": {"label": "MGM Resorts hotel terms & conditions (resort fees)", "url": MGM_TC, "publisher": "MGM Resorts International (official)", "type": "Official terms"},
}
for n in range(1, 38):
    SOURCES[f"V_S{n}"] = {"label": f"Venetian DSE IV structure sheet {n} (PDF)", "url": V_STRUCT(n), "publisher": "The Venetian Las Vegas (official)", "type": "Official structure PDF"}

def rules_from_sheet(sheet_id, fee_text, extra=None, silent_note=True):
    """Standard structured rule fields from a Venetian sheet read in full."""
    base = {
        "single_entry": {
            "value": "freezeout (no re-entry / rebuy / add-on clause on official sheet)",
            "excerpt": (extra or {}).get("single_excerpt", "Sheet contains no re-entry, re-buy or add-on clause. " + fee_text),
            "source": sheet_id, "retrieved": RETRIEVED},
        "re_entry": {"value": "not offered (no clause found)", "excerpt": "No re-entry language appears anywhere on the sheet.", "source": sheet_id, "retrieved": RETRIEVED},
        "rebuy": {"value": "not offered (no clause found)", "excerpt": "No re-buy language appears anywhere on the sheet.", "source": sheet_id, "retrieved": RETRIEVED},
        "addon": {"value": "not offered (no clause found)", "excerpt": "No add-on language appears anywhere on the sheet.", "source": sheet_id, "retrieved": RETRIEVED},
        "house_fee": {"value": fee_text, "excerpt": fee_text, "source": sheet_id, "retrieved": RETRIEVED},
    }
    if extra:
        for k, v in extra.items():
            if k != "single_excerpt":
                base[k] = v
    return base

E = []  # events

def ev(**kw):
    kw.setdefault("retrieved", RETRIEVED)
    kw.setdefault("last_checked", RETRIEVED)
    E.append(kw)

# ---------------------------------------------------------------------------
# Venetian DSE IV — CONFIRMED SINGLE-ENTRY (freezeout) one-day events.
# Each: sheet read in full on 2026-11-16; no re-entry/rebuy/add-on clause.
# ---------------------------------------------------------------------------
NO_RE = "Sheet read in full: no re-entry, re-buy or add-on clause appears."

# Sheet 1: $200 NLH Bounty events (Evening 5:10 PM)
S1_FEE = "$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $160 of every $200 Buy In."
for eid, date, day, name in [
    ("V-E09", "2026-11-24", "Tue", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E11", "2026-11-25", "Wed", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E13", "2026-11-26", "Thu", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E15", "2026-11-27", "Fri", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E21", "2026-11-29", "Sun", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E22", "2026-11-30", "Mon", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E23", "2026-12-01", "Tue", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E25", "2026-12-02", "Wed", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E60", "2026-12-20", "Sun", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E61", "2026-12-21", "Mon", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E62", "2026-12-22", "Tue", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
    ("V-E64", "2026-12-23", "Wed", "$200 No Limit Hold'em Bounty $8K GTD (1Day)"),
]:
    ev(id=eid, venue="The Venetian", series="DSE IV", date=date, day=day, start="5:10 PM",
       event_no=eid.split("E")[-1].lstrip("0") or "0", name=name, game="NLH", format="bounty",
       buy_in=200, house_fee=40, prize_pool=160, gtd=8000, gtd_includes_bounties=True,
       bounty_note="$50 bounty per elimination (sheet note 09)", chips=25000, level_min=30,
       late_reg="8 levels + break (9:40 PM)", eligibility="21+ with Venetian Rewards card",
       classification="single_entry_confirmed", struct_sheet=1,
       rules=rules_from_sheet("V_S1", S1_FEE),
       note="Guarantee is prize pool + total bounties (sheet note 10). Pays 12.5% of field.",
       sources=["V_PAGE", "V_SCHED", "V_S1"])

# Sheet 5: events 02 and 12 ($300 NLH 1Day)
S5_FEE = "$58 of the $300 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $242 of every $300 Buy In."
for eid, date, day in [("V-E02", "2026-11-18", "Wed"), ("V-E12", "2026-11-26", "Thu")]:
    ev(id=eid, venue="The Venetian", series="DSE IV", date=date, day=day, start="11:10 AM",
       event_no=eid.split("E")[-1].lstrip("0"), name="$300 No Limit Hold'em $10K GTD (1Day)", game="NLH", format="freezeout",
       buy_in=300, house_fee=58, prize_pool=242, gtd=10000, gtd_includes_bounties=False,
       chips=40000, level_min=30, late_reg="10 levels + break (~4:55 PM)",
       eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=5,
       rules=rules_from_sheet("V_S5", S5_FEE),
       note="Sheet 5 covers Event Numbers 02 and 12. Pays 12.5% of field.",
       sources=["V_PAGE", "V_SCHED", "V_S5"])

# Sheet 6: event 10
ev(id="V-E10", venue="The Venetian", series="DSE IV", date="2026-11-25", day="Wed", start="11:10 AM",
   event_no="10", name="$400 No Limit Hold'em $15K GTD (1Day)", game="NLH", format="freezeout",
   buy_in=400, house_fee=65, prize_pool=335, gtd=15000, gtd_includes_bounties=False,
   chips=40000, level_min=30, late_reg="10 levels + break (~4:55 PM)",
   eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=6,
   rules=rules_from_sheet("V_S6", "$65 of the $400 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $335 of every $400 Buy In."),
   note="Pays 12.5% of field.", sources=["V_PAGE", "V_SCHED", "V_S6"])

# Sheet 7: events 14, 28, 63 ($600 NLH 1Day)
S7_FEE = "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $510 of every $600 Buy In."
for eid, date, day, gtd in [("V-E14", "2026-11-27", "Fri", 30000), ("V-E28", "2026-12-06", "Sun", 40000), ("V-E63", "2026-12-23", "Wed", 30000)]:
    ev(id=eid, venue="The Venetian", series="DSE IV", date=date, day=day, start="11:10 AM",
       event_no=eid.split("E")[-1].lstrip("0"), name=f"$600 No Limit Hold'em ${gtd//1000}K GTD (1Day)", game="NLH", format="freezeout",
       buy_in=600, house_fee=90, prize_pool=510, gtd=gtd, gtd_includes_bounties=False,
       chips=40000, level_min=30, late_reg="10 levels + break (~4:55 PM)",
       eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=7,
       rules=rules_from_sheet("V_S7", S7_FEE),
       note="Sheet 7 covers Event Numbers 14, 28 and 63 (guarantees $30K/$40K/$30K).",
       sources=["V_PAGE", "V_SCHED", "V_S7"])

# Sheet 11: events 16, 30, 54 ($600 Bounty, escalating $200→$500)
S11_FEE = "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $510 of every $600 Buy In."
for eid, date, day, gtd in [("V-E16", "2026-11-28", "Sat", 30000), ("V-E30", "2026-12-07", "Mon", 40000), ("V-E54", "2026-12-16", "Wed", 50000)]:
    ev(id=eid, venue="The Venetian", series="DSE IV", date=date, day=day, start="11:10 AM",
       event_no=eid.split("E")[-1].lstrip("0"), name=f"$600 No Limit Hold'em Bounty ${gtd//1000}K GTD (1Day)", game="NLH", format="bounty",
       buy_in=600, house_fee=90, prize_pool=510, gtd=gtd, gtd_includes_bounties=True,
       bounty_note="$200 bounty per elimination; $500 per elimination after the money (sheet note 07)",
       chips=40000, level_min=30, late_reg="10 levels + break (4:55 PM)",
       eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=11,
       rules=rules_from_sheet("V_S11", S11_FEE),
       note="Guarantee is prize pool + total bounties. Sheet 11 covers Events 16, 30, 54.",
       sources=["V_PAGE", "V_SCHED", "V_S11"])

# Sheet 15: events 29,31,34,38,42,50,51,53,55 ($300 Bounty evening)
S15_FEE = "$50 of the $300 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $250 of every $300 Buy In."
for eid, date, day in [("V-E29", "2026-12-06", "Sun"), ("V-E31", "2026-12-07", "Mon"), ("V-E34", "2026-12-08", "Tue"),
                       ("V-E38", "2026-12-09", "Wed"), ("V-E42", "2026-12-10", "Thu"), ("V-E50", "2026-12-13", "Sun"),
                       ("V-E51", "2026-12-14", "Mon"), ("V-E53", "2026-12-15", "Tue"), ("V-E55", "2026-12-16", "Wed")]:
    ev(id=eid, venue="The Venetian", series="DSE IV", date=date, day=day, start="5:10 PM",
       event_no=eid.split("E")[-1].lstrip("0"), name="$300 No Limit Hold'em Bounty $15K GTD (1Day)", game="NLH", format="bounty",
       buy_in=300, house_fee=50, prize_pool=250, gtd=15000, gtd_includes_bounties=True,
       bounty_note="$100 bounty per elimination (sheet note 09)", chips=25000, level_min=30,
       late_reg="8 levels + break (9:40 PM)", eligibility="21+ with Venetian Rewards card",
       classification="single_entry_confirmed", struct_sheet=15,
       rules=rules_from_sheet("V_S15", S15_FEE),
       note="Guarantee is prize pool + total bounties. Sheet 15 covers Events 29–55 listed above.",
       sources=["V_PAGE", "V_SCHED", "V_S15"])

# Sheet 16: event 36 ($800 Bounty)
ev(id="V-E36", venue="The Venetian", series="DSE IV", date="2026-12-09", day="Wed", start="11:10 AM",
   event_no="36", name="$800 No Limit Hold'em Bounty $75K GTD (1Day)", game="NLH", format="bounty",
   buy_in=800, house_fee=100, prize_pool=700, gtd=75000, gtd_includes_bounties=True,
   bounty_note="$200 bounty per elimination; $500 per elimination after the money (sheet note 07)",
   chips=40000, level_min=30, late_reg="10 levels + break (4:55 PM)",
   eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=16,
   rules=rules_from_sheet("V_S16", "$100 of the $800 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $700 of every $800 Buy In."),
   note="Guarantee is prize pool + total bounties.", sources=["V_PAGE", "V_SCHED", "V_S16"])

# Sheet 34: event 52 ($1,100 PKO)
ev(id="V-E52", venue="The Venetian", series="DSE IV", date="2026-12-15", day="Tue", start="11:10 AM",
   event_no="52", name="$1,100 No Limit Hold'em Progressive Knock-Out $75K GTD (1Day)", game="NLH", format="pko",
   buy_in=1100, house_fee=130, prize_pool=970, gtd=75000, gtd_includes_bounties=True,
   bounty_note="PKO: players start as a $200 bounty; half the eliminated bounty is kept, half is added to the eliminator's bounty (sheet note 09)",
   chips=40000, level_min=30, late_reg="10 levels + break (4:55 PM)",
   eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=34,
   rules=rules_from_sheet("V_S34", "$130 of the $1,100 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $970 of every $1,100 Buy In."),
   note="Guarantee is prize pool + total bounty prize money (sheet note 10).",
   sources=["V_PAGE", "V_SCHED", "V_S34"])

# ---- Sheets read this session that resolve previously UNVERIFIED rows ----

# Sheet 18: events 03, 04, 05 (RaceDay Stack)
S18_FEE = "$35 of the $200 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $165 of every $200 Buy In."
for eid, date, day in [("V-E03", "2026-11-19", "Thu"), ("V-E04", "2026-11-20", "Fri"), ("V-E05", "2026-11-21", "Sat")]:
    ev(id=eid, venue="The Venetian", series="DSE IV", date=date, day=day, start="10:10 AM",
       event_no=eid.split("E")[-1].lstrip("0"), name="$200 NLH RaceDay Stack (1Day)", game="NLH", format="freezeout",
       buy_in=200, house_fee=35, prize_pool=165, gtd=None, gtd_includes_bounties=False,
       chips=30000, level_min=20, late_reg="6 levels + break (~12:25 PM)",
       eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=18,
       rules=rules_from_sheet("V_S18", S18_FEE),
       note="No guarantee printed on sheet or schedule. 20-min levels then 15-min. Pay jump: 12.5%.",
       sources=["V_PAGE", "V_SCHED", "V_S18"])

# Sheet 29: event 06
ev(id="V-E06", venue="The Venetian", series="DSE IV", date="2026-11-22", day="Sun", start="11:10 AM",
   event_no="06", name="$200 No Limit Hold'em (1Day)", game="NLH", format="freezeout",
   buy_in=200, house_fee=40, prize_pool=160, gtd=None, gtd_includes_bounties=False,
   chips=30000, level_min=30, late_reg="8 levels + break (~3:40 PM)",
   eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=29,
   rules=rules_from_sheet("V_S29", S1_FEE),
   note="No guarantee printed on sheet or schedule.", sources=["V_PAGE", "V_SCHED", "V_S29"])

# Sheet 30: event 08 (PKO)
ev(id="V-E08", venue="The Venetian", series="DSE IV", date="2026-11-23", day="Mon", start="5:10 PM",
   event_no="08", name="$200 No Limit Hold'em PKO Bounty $8K GTD (1Day)", game="NLH", format="pko",
   buy_in=200, house_fee=40, prize_pool=160, gtd=8000, gtd_includes_bounties=True,
   bounty_note="PKO: players start as a $50 bounty (sheet note 09)", chips=25000, level_min=30,
   late_reg="8 levels + break (9:40 PM)", eligibility="21+ with Venetian Rewards card",
   classification="single_entry_confirmed", struct_sheet=30,
   rules=rules_from_sheet("V_S30", S1_FEE),
   note="Guarantee is prize pool + total bounty prize money (sheet note 10).",
   sources=["V_PAGE", "V_SCHED", "V_S30"])

# Sheet 17: events 24, 32 (Seniors)
S17_FEE = "$90 of the $600 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $510 of every $600 Buy In."
for eid, date, day in [("V-E24", "2026-12-02", "Wed"), ("V-E32", "2026-12-08", "Tue")]:
    ev(id=eid, venue="The Venetian", series="DSE IV", date=date, day=day, start="10:10 AM",
       event_no=eid.split("E")[-1].lstrip("0"), name="$600 No Limit Hold'em Seniors $40K GTD (1Day)", game="NLH", format="freezeout",
       buy_in=600, house_fee=90, prize_pool=510, gtd=40000, gtd_includes_bounties=False,
       chips=40000, level_min=30, late_reg="10 levels + break (~3:55 PM)",
       eligibility="Must be 50+ years of age (sheet note 02; under-50 buyers forfeit prize money and buy-in)",
       classification="single_entry_confirmed", struct_sheet=17,
       rules=rules_from_sheet("V_S17", S17_FEE),
       note="Age-gated 50+.", sources=["V_PAGE", "V_SCHED", "V_S17"])

# Sheet 26: event 17 ($400 PLO Bounty)
ev(id="V-E17", venue="The Venetian", series="DSE IV", date="2026-11-28", day="Sat", start="12:10 PM",
   event_no="17", name="$400 Pot Limit Omaha Bounty $15K GTD (1Day)", game="PLO", format="bounty",
   buy_in=400, house_fee=60, prize_pool=340, gtd=15000, gtd_includes_bounties=True,
   bounty_note="$100 bounty per elimination (sheet note 08); winner keeps own bounty",
   chips=30000, level_min=30, late_reg="8 levels + break (~4:40 PM)",
   eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=26,
   rules=rules_from_sheet("V_S26", "$60 of the $400 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $340 of every $400 Buy In."),
   note="Guarantee is prize pool + total bounties (sheet note 10). Plays 8-handed.",
   sources=["V_PAGE", "V_SCHED", "V_S26"])

# Sheet 8: events 18 and 58 (Valuetown) — FLAGGED: "subsequent buy in's" wording
S8_FEE = "$40 of the $200 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $160 of every $200 Buy In."
for eid, date, day in [("V-E18", "2026-11-28", "Sat"), ("V-E58", "2026-12-19", "Sat")]:
    ev(id=eid, venue="The Venetian", series="DSE IV", date=date, day=day, start="5:10 PM",
       event_no=eid.split("E")[-1].lstrip("0"), name="$200 NLH PokerAtlas Valuetown Bounty $20K GTD (1Day)", game="NLH", format="bounty",
       buy_in=200, house_fee=40, prize_pool=160, gtd=20000, gtd_includes_bounties=True,
       bounty_note="$50 bounty per elimination (sheet note 10)", chips=25000, level_min=30,
       late_reg="8 levels + break (9:40 PM)", eligibility="21+ with Venetian Rewards card",
       classification="flagged_ambiguous", struct_sheet=8,
       rules={
         "single_entry": {"value": "AMBIGUOUS — sheet refers to 'subsequent buy in's'", "excerpt": "Note 07: 'PokerAtlas PRO players will receive a twenty ($20) rake discount on their initial $200 buy in only... All subsequent buy in's after the initial buy in will be $200.' The sheet has no re-entry/rebuy/add-on clause, but the phrase 'subsequent buy in's' implies more than one buy-in may be possible.", "source": "V_S8", "retrieved": RETRIEVED},
         "re_entry": {"value": "not stated (ambiguous wording above)", "excerpt": "No explicit re-entry clause; 'subsequent buy in's' wording unresolved.", "source": "V_S8", "retrieved": RETRIEVED},
         "rebuy": {"value": "not offered (no clause found)", "excerpt": "No re-buy language.", "source": "V_S8", "retrieved": RETRIEVED},
         "addon": {"value": "not offered (no clause found)", "excerpt": "No add-on language.", "source": "V_S8", "retrieved": RETRIEVED},
         "house_fee": {"value": S8_FEE, "excerpt": S8_FEE, "source": "V_S8", "retrieved": RETRIEVED},
       },
       note="FLAGGED: PokerAtlas PRO $20 discount applies to the initial buy-in only; 'All subsequent buy in's after the initial buy in will be $200' suggests possible further entries. Confirm with the poker room before treating as single-entry. Guarantee is prize pool + total bounties (note 11).",
       sources=["V_PAGE", "V_SCHED", "V_S8"])

# Sheet 22: event 20 ($300 PLO Double Board Bomb Pot)
ev(id="V-E20", venue="The Venetian", series="DSE IV", date="2026-11-29", day="Sun", start="12:10 PM",
   event_no="20", name="$300 Pot Limit Omaha $10K GTD (1Day) — Double Board Bomb Pot", game="PLO", format="freezeout",
   buy_in=300, house_fee=58, prize_pool=242, gtd=10000, gtd_includes_bounties=False,
   chips=30000, level_min=30, late_reg="8 levels + break (~4:40 PM)",
   eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=22,
   rules=rules_from_sheet("V_S22", "$58 of the $300 Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of $242 of every $300 Buy In."),
   note="Double-board bomb-pot PLO; plays 8-handed; pays 12.5%.",
   sources=["V_PAGE", "V_SCHED", "V_S22"])

# Sheet 28: event 27 ($600 BIG O)
ev(id="V-E27", venue="The Venetian", series="DSE IV", date="2026-12-03", day="Thu", start="12:10 PM",
   event_no="27", name="$600 BIG O $25K GTD (1Day)", game="BIG O", format="freezeout",
   buy_in=600, house_fee=90, prize_pool=510, gtd=25000, gtd_includes_bounties=False,
   chips=30000, level_min=30, late_reg="8 levels + break (~4:40 PM)",
   eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=28,
   rules=rules_from_sheet("V_S28", S7_FEE),
   note="5-card PLO8 (BIG O). Plays 8-handed; pays 12.5%.", sources=["V_PAGE", "V_SCHED", "V_S28"])

# Sheet 27: event 40 ($600 PLO Bounty)
ev(id="V-E40", venue="The Venetian", series="DSE IV", date="2026-12-10", day="Thu", start="12:10 PM",
   event_no="40", name="$600 Pot Limit Omaha Bounty $25K GTD (1Day)", game="PLO", format="bounty",
   buy_in=600, house_fee=90, prize_pool=510, gtd=25000, gtd_includes_bounties=True,
   bounty_note="$200 bounty per elimination (sheet note 08); winner keeps own bounty",
   chips=30000, level_min=30, late_reg="8 levels + break (~4:40 PM)",
   eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=27,
   rules=rules_from_sheet("V_S27", S7_FEE),
   note="Guarantee is prize pool + total bounties (sheet note 10). Plays 8-handed.",
   sources=["V_PAGE", "V_SCHED", "V_S27"])

# Sheet 23: event 57 ($600 PLO Double Board Bomb Pot)
ev(id="V-E57", venue="The Venetian", series="DSE IV", date="2026-12-17", day="Thu", start="12:10 PM",
   event_no="57", name="$600 Pot Limit Omaha $25K GTD (1Day) — Double Board Bomb Pot", game="PLO", format="freezeout",
   buy_in=600, house_fee=90, prize_pool=510, gtd=25000, gtd_includes_bounties=False,
   chips=30000, level_min=30, late_reg="8 levels + break (~4:40 PM)",
   eligibility="21+ with Venetian Rewards card", classification="single_entry_confirmed", struct_sheet=23,
   rules=rules_from_sheet("V_S23", S7_FEE),
   note="Double-board bomb-pot PLO; plays 8-handed; pays 12.5%.",
   sources=["V_PAGE", "V_SCHED", "V_S23"])

# Sheet 33: event 43 (LIPS Kings and Queens bounty, open to all)
ev(id="V-E43", venue="The Venetian", series="DSE IV", date="2026-12-11", day="Fri", start="11:10 AM",
   event_no="43", name="$600 NLH LIPS $30K GTD (1Day) — Kings and Queens bounty, open to all", game="NLH", format="bounty",
   buy_in=600, house_fee=80, extra_fee=10, extra_fee_note="$10 flat fee for Vegas Connected, Inc. (LIPS) (sheet note 06)", prize_pool=510,
   gtd=30000, gtd_includes_bounties=True,
   bounty_note="$200 bounty per elimination (sheet note 07); winner keeps own bounty",
   chips=40000, level_min=30, late_reg="10 levels + break (4:55 PM)",
   eligibility="Open to all players 21+ (trophy to last King and last Queen standing)",
   classification="single_entry_confirmed", struct_sheet=33,
   rules=rules_from_sheet("V_S33", "$80 of the $600 Buy-In is withheld for house fees (Rake + Staff). $10 of the $600 Buy In will be withheld as a flat fee for Vegas Connected, INC, DBA Ladies International Poker Series (LIPS). Prize pool consists of $510 of every $600 Buy In."),
   note="Guarantee is prize pool + total bounties.", sources=["V_PAGE", "V_SCHED", "V_S33"])

# Sheet 32: event 39 (LIPS Ladies 2-Day, women only) — single-entry confirmed but 2-day + eligibility
ev(id="V-E39", venue="The Venetian", series="DSE IV", date="2026-12-10", day="Thu", start="10:10 AM",
   event_no="39", name="$800 NLH LIPS Ladies $40K GTD (2Day) — Women in Poker Main Event", game="NLH", format="freezeout",
   buy_in=800, house_fee=90, extra_fee=20, extra_fee_note="$20 flat fee for Vegas Connected, Inc. (LIPS) (sheet note 07)", prize_pool=690,
   gtd=40000, gtd_includes_bounties=False,
   chips=40000, level_min=40, late_reg="9 levels + break (~4:55 PM)",
   eligibility="Female players 21+ only (sheet note 02)",
   classification="single_entry_confirmed", struct_sheet=32,
   rules=rules_from_sheet("V_S32", "$90 of the $800 Buy-In is withheld for house fees (Rake + Staff). $20 of the $800 Buy In will be withheld as a flat fee for Vegas Connected, INC, DBA Ladies International Poker Series (LIPS). Prize pool consists of $690 of every $800 Buy In."),
   note="TWO-DAY: Day 2 resumes Dec 11 at 10:00 AM, streamed final table by PokerGO ~7:00 PM (sheet note 03). Playing Day 2 commits most of Dec 11.",
   days=["2026-12-10", "2026-12-11"], sources=["V_PAGE", "V_SCHED", "V_S32"])

# Sheet 31: event 35 — TEAM event (excluded from single-entry)
ev(id="X-V35", venue="The Venetian", series="DSE IV", date="2026-12-09", day="Wed", start="10:10 AM",
   event_no="35", name="$600 NLH LIPS Poker Jingle Tag Team $10K GTD (1Day)", game="NLH", format="team",
   buy_in=600, house_fee=80, extra_fee=10, extra_fee_note="$10 flat fee for Vegas Connected, Inc. (LIPS)", prize_pool=510,
   gtd=10000, gtd_includes_bounties=False, chips=40000, level_min=30,
   late_reg="8 levels + break (~2:40 PM)", eligibility="Teams of two: Female/Female or Female/Male (sheet)",
   classification="excluded", exclude_reason="Team format — not an individual single-entry event (players rotate each level)",
   struct_sheet=31,
   rules=rules_from_sheet("V_S31", "$80 of the $600 Buy-In is withheld for house fees (Rake + Staff). $10 of the $600 Buy In will be withheld as a flat fee for Vegas Connected, INC, DBA LIPS."),
   sources=["V_PAGE", "V_SCHED", "V_S31"])

# ---------------------------------------------------------------------------
# Venetian multi-flight events (excluded — each flight is a separate entry)
# ---------------------------------------------------------------------------
MF_NOTE = "Multi-flight: each starting flight is a separate buy-in. Sheet note 08: 'Any player who bags chips for Day 2 may not play a subsequent flight.' The sheet states no other re-entry terms; a non-bagging player may take another flight (multi-entry by design)."
def multi(no, name, date_desc, flights_desc, buy_in, fee, pool, gtd, chips, lvl, late, sheet, extra_note=""):
    ev(id=f"X-V{no}", venue="The Venetian", series="DSE IV", date=date_desc, day="", start=flights_desc,
       event_no=str(no), name=name, game="NLH", format="multi-flight",
       buy_in=buy_in, house_fee=fee, prize_pool=pool, gtd=gtd, gtd_includes_bounties=False,
       chips=chips, level_min=lvl, late_reg=late, eligibility="21+ with Venetian Rewards card",
       classification="excluded", exclude_reason=MF_NOTE + (" " + extra_note if extra_note else ""),
       struct_sheet=sheet,
       rules={
         "single_entry": {"value": "NO — multi-flight event", "excerpt": MF_NOTE, "source": f"V_S{sheet}", "retrieved": RETRIEVED},
         "re_entry": {"value": "flights are separate entries; bagged players barred from later flights", "excerpt": "Any player who bags chips for Day 2 may not play a subsequent flight.", "source": f"V_S{sheet}", "retrieved": RETRIEVED},
         "rebuy": {"value": "not offered (no clause found)", "excerpt": "No re-buy language on sheet.", "source": f"V_S{sheet}", "retrieved": RETRIEVED},
         "addon": {"value": "not offered (no clause found)", "excerpt": "No add-on language on sheet.", "source": f"V_S{sheet}", "retrieved": RETRIEVED},
         "house_fee": {"value": f"${fee} of the ${buy_in} Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of ${pool} of every ${buy_in} Buy In.", "excerpt": f"${fee} of the ${buy_in} Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of ${pool} of every ${buy_in} Buy In.", "source": f"V_S{sheet}", "retrieved": RETRIEVED},
       },
       sources=["V_PAGE", "V_SCHED", f"V_S{sheet}"])

multi(1, "$300 No Limit Hold'em 1A–1D $75K GTD", "Nov 16 – Nov 18, 2026 (Day 2 Nov 18 12:00 PM)", "Flights 11:10 AM / 5:10 PM", 300, 60, 240, 75000, 30000, 30, "6 levels + break (1A/C ~3:40 PM; 1B/D ~8:40 PM)", 9, "Sheets 10 (1A/1C) and 9 (1B/1D) read: $60 house fee / $240 to prize pool.")
multi(7, "$400 No Limit Hold'em 1A–1B $75K GTD", "Nov 23 – Nov 25, 2026 (Day 2 Nov 25 11:00 AM)", "Flights 11:10 AM", 400, 70, 330, 75000, 40000, 40, "9 levels + break (~5:55 PM)", 2, "")
multi(19, "$400 No Limit Hold'em 1A–1C $75K GTD", "Nov 29 – Dec 2, 2026 (Day 2 Dec 2 11:00 AM)", "Flights 11:10 AM", 400, 70, 330, 75000, 40000, 40, "9 levels + break (~5:55 PM)", 3, "")
multi(26, "$800 No Limit Hold'em 1A–1F $500K GTD", "Dec 3 – Dec 6, 2026 (Day 2 Dec 6 12:00 PM)", "Flights 11:10 AM / 5:10 PM (1F Turbo 5:10 PM)", 800, 110, 690, 500000, 40000, 40, "6 levels + break (A/C/E ~3:40 PM; B/D ~8:40 PM; F ~7:25 PM)", 12, "Sheets 12 (A/C/E, 40-min), 13 (B/D, 30-min) and 14 (F Turbo, 20-min) read.")
multi(47, "$2,200 No Limit Hold'em 1A–1B $1M GTD (PokerAtlas Championship Title Event)", "Dec 12 – Dec 14, 2026 (Day 2 Dec 13 1:00 PM; Day 3 FT Dec 14 11:00 AM, PokerGO stream)", "Flights 1A 10:10 AM / 1B 6:10 PM", 2200, 225, 1975, 1000000, 40000, 40, "9 levels + break (1A ~4:55 PM; 1B ~11:10 PM)", 21, "Sheets 21 (1A, 40-min) and 37 (1B, 30-min) read. Day 3 streamed final table by PokerGO.")
multi(49, "$1,100 No Limit Hold'em Seniors 1A–1B $300K GTD (50+)", "Dec 13 – Dec 15, 2026 (Day 2 Dec 15 10:00 AM)", "Flights 10:10 AM", 1100, 140, 960, 300000, 40000, 40, "9 levels + break (~4:55 PM)", 20, "Must be 50+ (sheet note 02). Flights play to ~15% remaining.")
multi(56, "$1,100 No Limit Hold'em 1A–1E $500K GTD", "Dec 17 – Dec 20, 2026 (Day 2 Dec 20 11:00 AM)", "Flights 10:10 AM / 6:10 PM", 1100, 140, 960, 500000, 40000, 40, "9 levels + break (A/C/E ~4:55 PM; B/D ~11:10 PM)", 35, "Sheets 35 (A/C/E, 40-min) and 36 (B/D, 30-min) read. $40 house-fee discount for on-time registration on Days 1A and 1B ($1,060 buy-in).")
multi(59, "$600 No Limit Hold'em 1A–1C $150K GTD", "Dec 20 – Dec 23, 2026 (Day 2 Dec 23 11:00 AM)", "Flights 11:10 AM", 600, 95, 505, 150000, 40000, 40, "9 levels + break (5:55 PM)", 4, "$20 house-fee discount for on-time registration on Day 1A ($580 buy-in).")

# ---------------------------------------------------------------------------
# Venetian satellites (excluded — award seats, not cash)
# ---------------------------------------------------------------------------
def sat(no, name, date, start, buy_in, fee, pool, sheet, target, late, chips=20000, lvl=20):
    ev(id=f"X-V{no}", venue="The Venetian", series="DSE IV", date=date, day="", start=start,
       event_no=str(no), name=name, game="NLH", format="satellite",
       buy_in=buy_in, house_fee=fee, prize_pool=pool, gtd=None, gtd_includes_bounties=False,
       chips=chips, level_min=lvl, late_reg=late,
       eligibility="See sheet (LIPS satellites open to female players 21+)",
       classification="excluded",
       exclude_reason=f"Satellite: prizes are direct entry seats to {target} (sheet note 04/08) — not a cash-prize freezeout.",
       struct_sheet=sheet,
       rules=rules_from_sheet(f"V_S{sheet}", f"${fee} of the ${buy_in} Buy-In is withheld for house fees (Rake + Staff). The prize pool consists of ${pool} of every ${buy_in} Buy In."),
       sources=["V_PAGE", "V_SCHED", f"V_S{sheet}"])

sat(33, "$100 NLH LIPS Ladies Milestone Satellite → Event 39", "2026-12-08", "4:10 PM", 100, 20, 80, 19, "Event #39 ($800 LIPS Ladies)", "6 levels + break (~6:25 PM)")
sat(37, "$100 NLH LIPS Ladies Milestone Satellite → Event 39", "2026-12-09", "4:10 PM", 100, 20, 80, 19, "Event #39 ($800 LIPS Ladies)", "6 levels + break (~6:25 PM)")
sat(41, "$260 NLH Milestone Satellite → Event 47", "2026-12-10", "4:10 PM", 260, 40, 220, 24, "Event #47 ($2,200 PokerAtlas Championship)", "6 levels + break (~6:25 PM)")
sat(44, "$260 NLH Milestone Satellite → Event 47", "2026-12-11", "4:10 PM", 260, 40, 220, 24, "Event #47 ($2,200 PokerAtlas Championship)", "6 levels + break (~6:25 PM)")
sat(45, "$260 NLH Turbo Milestone Satellite → Event 47", "2026-12-11", "8:10 PM", 260, 35, 225, 25, "Event #47 ($2,200 PokerAtlas Championship)", "6 levels (no break listed)")
sat(46, "$260 NLH Turbo Milestone Satellite → Event 47", "2026-12-12", "9:10 AM", 260, 35, 225, 25, "Event #47 ($2,200 PokerAtlas Championship)", "6 levels (no break listed)")
sat(48, "$260 NLH Turbo Milestone Satellite → Event 47", "2026-12-12", "12:10 PM", 260, 35, 225, 25, "Event #47 ($2,200 PokerAtlas Championship)", "6 levels (no break listed)")

# ---------------------------------------------------------------------------
# Wynn daily tournaments (excluded — re-entry / rebuy / add-on confirmed)
# ---------------------------------------------------------------------------
W_DAILY_RULES = {
  "single_entry": {"value": "NO — re-entry/rebuy/add-on confirmed on official daily structures", "excerpt": "See per-row excerpt.", "source": "W_DAILY", "retrieved": RETRIEVED},
}
def wynn_daily(id_, dow, start, name, buy_in, gtd, excerpt):
    ev(id=id_, venue="Wynn Las Vegas", series="Daily", date=f"{dow} (recurring)", day=dow, start=start,
       event_no="", name=name, game="NLH", format="re-entry/add-on",
       buy_in=buy_in, house_fee=None, prize_pool=None, gtd=gtd, gtd_includes_bounties=False,
       chips=None, level_min=None, late_reg=None, eligibility="21+; Wynn Rewards membership required",
       classification="excluded", exclude_reason=excerpt,
       rules={
         "single_entry": {"value": "NO", "excerpt": excerpt, "source": "W_DAILY", "retrieved": RETRIEVED},
         "re_entry": {"value": "confirmed (see excerpt)", "excerpt": excerpt, "source": "W_DAILY", "retrieved": RETRIEVED},
         "rebuy": {"value": "see excerpt", "excerpt": excerpt, "source": "W_DAILY", "retrieved": RETRIEVED},
         "addon": {"value": "see excerpt", "excerpt": excerpt, "source": "W_DAILY", "retrieved": RETRIEVED},
         "house_fee": {"value": None, "excerpt": "Fee split not verified in this pass.", "source": "W_DAILY", "retrieved": RETRIEVED},
       },
       sources=["W_POKER", "W_DAILY"])

wynn_daily("X-W01", "Mon–Thu", "12:00 PM", "$200 No Limit Hold'em $10K GTD", 200, 10000,
           "Official daily structure sheet: entry fee and re-entry fee are both listed — re-entry allowed (spend-more).")
wynn_daily("X-W02", "Fri", "12:00 PM", "$240 No Limit Hold'em Rebuy & Add-on $40K GTD", 240, 40000,
           "Official daily structure sheet: unlimited $200 rebuys and one $100 add-on per player (spend-more).")
wynn_daily("X-W03", "Sat & Sun", "12:00 PM", "$200 No Limit Hold'em $25K GTD", 200, 25000,
           "Official daily structure sheet: re-entries allowed and one $100 add-on per player (spend-more).")
wynn_daily("X-W04", "Mon–Sun (nightly)", "7:00 PM", "$160 No Limit Hold'em $10K GTD", 160, 10000,
           "Official daily structure sheet: re-entries allowed and one $100 add-on per player (spend-more).")

# ---------------------------------------------------------------------------
# Wynn WPT World Championship — excluded (re-entry confirmed on official terms)
# ---------------------------------------------------------------------------
WPT_REG_UNLIMITED = "Unlimited re-entry will be available until the start of level 9"
def wpt(id_, date, start, name, buy_in, gtd, fee_split, reg_excerpt, daysofplay=None, extra=None):
    ev(id=id_, venue="Wynn Las Vegas (Encore poker room)", series="WPT World Championship", date=date, day="", start=start,
       event_no="", name=name, game=(extra or {}).get("game", "NLH"), format=(extra or {}).get("format", "re-entry"),
       buy_in=buy_in, house_fee=None, prize_pool=None, gtd=gtd, gtd_includes_bounties=(extra or {}).get("gtd_bounty", False),
       chips=(extra or {}).get("chips"), level_min=(extra or {}).get("lvl"), late_reg=(extra or {}).get("late"),
       eligibility="21+; Wynn Rewards membership required (WPT general terms 18)",
       classification="excluded", exclude_reason=reg_excerpt,
       rules={
         "single_entry": {"value": "NO — re-entry allowed", "excerpt": reg_excerpt, "source": "W_STRUCT", "retrieved": RETRIEVED},
         "re_entry": {"value": reg_excerpt.split(".")[0], "excerpt": reg_excerpt, "source": "W_STRUCT", "retrieved": RETRIEVED},
         "rebuy": {"value": "not offered (no clause found)", "excerpt": "No re-buy language in event terms.", "source": "W_STRUCT", "retrieved": RETRIEVED},
         "addon": {"value": "not offered (no clause found)", "excerpt": "No add-on language in event terms.", "source": "W_STRUCT", "retrieved": RETRIEVED},
         "house_fee": {"value": fee_split, "excerpt": fee_split, "source": "W_STRUCT", "retrieved": RETRIEVED},
       },
       note=(extra or {}).get("note", ""), sources=["W_SCHED", "W_STRUCT"])

wpt("X-WPT01", "Nov 27 – Nov 30, 2026 (Day 2 Nov 30)", "Flights 11:00 AM / 5:00 PM (1F 6:00 PM)",
    "$600 NLH $400K GTD (Day 1A–1F)", 600, 400000,
    "$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
    "Unlimited re-entry for each starting flight will be available until the start of level 9.",
    extra={"chips": 40000, "lvl": 30, "late": "until start of level 9", "note": "Day 1F plays 20-min levels."})
wpt("X-WPT02", "Nov 30 – Dec 4, 2026 (Day 2 Dec 3; FT Dec 4)", "Flights 11:00 AM / 5:00 PM (1F 6:00 PM)",
    "$800 NLH $1M GTD (Day 1A–1F)", 800, 1000000,
    "$800 Buy-in = $695 (Tournament Prize Pool) + $72 (Tournament Fee) + $33 (Poker Staff Service Charge)",
    "Unlimited re-entry for each starting flight will be available until the start of level 9.",
    extra={"chips": 40000, "lvl": 30, "late": "until start of level 9", "note": "Day 1F plays 20-min levels."})
wpt("X-WPT03", "Dec 5 – Dec 12, 2026 (FT Dec 12 2:00 PM)", "Flights 11:00 AM",
    "$1,100 WPT Prime Championship $5M GTD (Day 1A–1D)", 1100, 5000000,
    "$1,100 Buy-in = $970 (Tournament Prize Pool) + $90 (Tournament Fee) + $40 (Poker Staff Service Charge)",
    "One (1) Entry and One (1) re-entry for each starting flight will be available until the start of level 10 (approximately 6:45 p.m.).",
    extra={"chips": 40000, "lvl": 40, "late": "until start of level 10 (~6:45 PM)", "note": "First place also receives a $10,400 entry to the Dec 2027 WPT World Championship (withheld from prize pool)."})
for tid, d, s in [("X-WPT08", "2026-12-05", "9:00 PM"), ("X-WPT09", "2026-12-06", "9:00 PM"), ("X-WPT12", "2026-12-07", "9:00 PM"),
                  ("X-WPT13", "2026-12-08", "9:00 PM"), ("X-WPT17", "2026-12-09", "9:00 PM"), ("X-WPT20", "2026-12-12", "9:00 PM"),
                  ("X-WPT25", "2026-12-14", "9:00 PM"), ("X-WPT48", "2026-12-21", "6:00 PM (schedule row lists 8:00 PM — time discrepancy flagged)")]:
    wpt(tid, d, s, "$600 NLH Turbo $50K GTD (1Day)", 600, 50000,
        "$600 Buy-in = $515 (Tournament Prize Pool) + $60 (Tournament Fee) + $25 (Poker Staff Service Charge)",
        WPT_REG_UNLIMITED + " (approximately 4:30 p.m. for 9 PM starts).",
        extra={"chips": 30000, "lvl": 20, "late": "until start of level 9",
               "note": "Official terms list these start dates: Dec 5, 6, 7, 8, 9, 12, 14 at 9 PM and Dec 21 at 6 PM. The schedule row for Dec 21 shows 8:00 PM — flagged as a source discrepancy." if tid == "X-WPT48" else ""})
for tid, d, s in [("X-WPT01b", "2026-11-27", "12:00 PM")]:
    pass  # placeholder removed
wpt("X-WPT-TORSE600", "2026-11-27", "12:00 PM", "$600 TORSE (1Day)", 600, None,
    "$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
    WPT_REG_UNLIMITED, extra={"game": "Mixed (TORSE)", "chips": 35000, "lvl": 30, "late": "until start of level 9"})
wpt("X-WPT-PLO400", "2026-11-27", "1:00 PM", "$400 PLO (1Day)", 400, None,
    "$400 Buy-in = $337 (Tournament Prize Pool) + $45 (Tournament Fee) + $18 (Poker Staff Service Charge)",
    WPT_REG_UNLIMITED + " (approximately 5:30 p.m.).", extra={"game": "PLO", "chips": 30000, "lvl": 30, "late": "until start of level 9 (~5:30 PM)"})
wpt("X-WPT-MTD600", "2026-11-28 and 2026-12-20", "12:00 PM / 1:00 PM", "$600 Mixed Triple Draw (A-5, 2-7, Badugi) (1Day)", 600, None,
    "$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
    WPT_REG_UNLIMITED, extra={"game": "Mixed (Triple Draw)", "chips": 35000, "lvl": 30, "late": "until start of level 9"})
wpt("X-WPT-O8-600", "2026-11-30", "12:00 PM", "$600 Limit Omaha 8 (1Day)", 600, None,
    "$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
    WPT_REG_UNLIMITED, extra={"game": "Limit O8", "chips": 35000, "lvl": 30, "late": "until start of level 9"})
wpt("X-WPT-O8S8-600", "2026-12-01", "12:00 PM", "$600 Limit Omaha 8/Stud 8 (1Day)", 600, None,
    "$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
    WPT_REG_UNLIMITED, extra={"game": "Mixed (O8/Stud8)", "chips": 35000, "lvl": 30, "late": "until start of level 9"})
wpt("X-WPT-PLO1100", "2026-12-01", "1:00 PM", "$1,100 PLO (1Day)", 1100, None,
    "$1,100 Buy-in = $975 (Tournament Prize Pool) + $85 (Tournament Fee) + $45 (Poker Staff Service Charge)",
    WPT_REG_UNLIMITED + " (approximately 5:30 p.m.).", extra={"game": "PLO", "chips": 30000, "lvl": 30, "late": "until start of level 9 (~5:30 PM)"})
wpt("X-WPT-NLH1600", "Dec 3 – Dec 5, 2026 (Day 2 Dec 5)", "Flights 11:00 AM", "$1,600 NLH $1M GTD (Day 1A–1B, 2Day)", 1600, 1000000,
    "$1,600 Buy-in = $1,430 (Tournament Prize Pool) + $120 (Tournament Fee) + $50 (Poker Staff Service Charge)",
    "Unlimited re-entry for each starting flight will be available until the start of level 10.",
    extra={"chips": 40000, "lvl": 40, "late": "until start of level 10", "note": "Official terms date this event Dec 3–5. The schedule row U-WPT14 lists an apparently separate $1,600 NLH 2-Day $1M on Dec 9 — flagged as a source discrepancy to confirm."})
wpt("X-WPT-HORSE600", "2026-12-04", "12:00 PM", "$600 HORSE (1Day)", 600, None,
    "$600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + $25 (Poker Staff Service Charge)",
    WPT_REG_UNLIMITED + " (approximately 4:30 p.m.).", extra={"game": "Mixed (HORSE)", "chips": 35000, "lvl": 30, "late": "until start of level 9 (~4:30 PM)"})
wpt("X-WPT-PLOMB1600", "Dec 6 – Dec 7, 2026 (Day 2 Dec 7)", "Flights 11:00 AM / 6:00 PM", "$1,600 PLO Mystery Bounty $500K GTD (2Day)", 1600, 500000,
    "$1,600 Buy-in = $930 (Tournament Prize Pool) + $500 (Mystery Bounty Prize Pool) + $120 (Tournament Fee) + $50 (Poker Staff Service Charge)",
    "Unlimited re-entry for each starting flight will be available until the start of level 10.",
    extra={"game": "PLO", "chips": 40000, "lvl": 40, "late": "until start of level 10", "gtd_bounty": True,
           "note": "Mystery bounty prizes $1,000–$100,000 drawn on Day 2; guarantee covers tournament + bounty prizes."})

# ---------------------------------------------------------------------------
# WPT rows whose entry terms are NOT in the official structures PDF — stay UNVERIFIED
# ---------------------------------------------------------------------------
def wpt_unverified(id_, date, start, name, buy_in, gtd, note=""):
    ev(id=id_, venue="Wynn Las Vegas (Encore poker room)", series="WPT World Championship", date=date, day="", start=start,
       event_no="", name=name, game="", format="unverified",
       buy_in=buy_in, house_fee=None, prize_pool=None, gtd=gtd, gtd_includes_bounties=False,
       chips=None, level_min=None, late_reg=None, eligibility="21+; Wynn Rewards membership required",
       classification="unverified",
       exclude_reason="UNVERIFIED — this event's terms are not included in the official WPT structures PDF reviewed on 2026-11-16 (8 chunks read in full). Entry rules unknown; not eligible for the single-entry list.",
       rules={
         "single_entry": {"value": None, "excerpt": "Not published in the structures document read.", "source": "W_STRUCT", "retrieved": RETRIEVED},
         "re_entry": {"value": None, "excerpt": "Not published in the structures document read.", "source": "W_STRUCT", "retrieved": RETRIEVED},
         "rebuy": {"value": None, "excerpt": "Not published in the structures document read.", "source": "W_STRUCT", "retrieved": RETRIEVED},
         "addon": {"value": None, "excerpt": "Not published in the structures document read.", "source": "W_STRUCT", "retrieved": RETRIEVED},
         "house_fee": {"value": None, "excerpt": "Not published in the structures document read.", "source": "W_STRUCT", "retrieved": RETRIEVED},
       },
       note=note, sources=["W_SCHED", "W_STRUCT"])

for row in [
 ("U-WPT10", "2026-12-07", "11:00 AM", "HORSE (2 Day) $1,100", 1100, None, ""),
 ("U-WPT11", "2026-12-07", "1:00 PM", "PLO $500 Bounty $1,600 $100K GTD", 1600, 100000, "Bounty event — labeled separately from freezeouts."),
 ("U-WPT14", "2026-12-09", "11:00 AM", "NLH (2 Day) $1,600 $1M GTD", 1600, 1000000, "See source discrepancy note on X-WPT-NLH1600."),
 ("U-WPT15", "2026-12-09", "1:00 PM", "PLO $1,000 Bounty $3,000 $250K GTD", 3000, 250000, "Bounty event."),
 ("U-WPT16", "2026-12-09", "1:00 PM", "Limit Omaha 8 $800", 800, None, ""),
 ("U-WPT18", "2026-12-12", "10:00 AM", "NLH $800 $100K GTD", 800, 100000, ""),
 ("U-WPT19", "2026-12-12", "1:00 PM", "PLO $3,000 $250K GTD", 3000, 250000, ""),
 ("U-WPT21", "2026-12-13", "11:00 AM", "Ladies NLH Championship (2 Day) $1,100 $250K GTD", 1100, 250000, "Schedule PDF text reads 'NIH' — taken as printed; flagged."),
 ("U-WPT22", "2026-12-13", "11:00 AM", "TORSE (2 Day) $1,100", 1100, None, ""),
 ("U-WPT23", "2026-12-14", "12:00 PM", "Mixed Triple Draw (2 Day) $1,100", 1100, None, ""),
 ("U-WPT24", "2026-12-14", "7:00 PM", "PLO Turbo $1,100 $100K GTD", 1100, 100000, ""),
 ("U-WPT26", "2026-12-15", "12:00 PM", "Big O $1,100", 1100, None, ""),
 ("U-WPT27", "2026-12-15", "1:00 PM", "PLO Progressive Bounty (PKO) $3,000 $250K GTD", 3000, 250000, "Bounty event."),
 ("U-WPT28", "2026-12-15", "7:00 PM", "NLH $500 Bounty Turbo $1,600 $100K GTD", 1600, 100000, "Schedule PDF text reads 'NIH' — flagged. Bounty event."),
 ("U-WPT29", "2026-12-17", "11:00 AM", "Seniors NLH Championship (3 Day) $1,100 $500K GTD", 1100, 500000, "Age eligibility not stated in reviewed sources."),
 ("U-WPT30", "2026-12-17", "11:00 AM", "Wynn Mixed Championship (2 Day) $1,600", 1600, None, ""),
 ("U-WPT31", "2026-12-17", "1:00 PM", "NLH High Roller (2 Day) $25,800", 25800, None, ""),
 ("U-WPT32", "2026-12-18", "12:00 PM", "PLO Double Board Bomb Pot $800", 800, None, ""),
 ("U-WPT33", "2026-12-18", "12:00 PM", "Limit Omaha 8 Championship (2 Day) $1,600", 1600, None, ""),
 ("U-WPT34", "2026-12-18", "12:00 PM", "NLH $600 $100K GTD", 600, 100000, ""),
 ("U-WPT35", "2026-12-18", "1:00 PM", "NLH 6-Max $10,500", 10500, None, ""),
 ("U-WPT36", "2026-12-18", "1:00 PM", "HORSE $800", 800, None, ""),
 ("U-WPT37", "2026-12-18", "6:00 PM", "NLH Turbo $1,100 $100K GTD", 1100, 100000, ""),
 ("U-WPT38", "2026-12-19", "11:00 AM", "Seniors High Roller (3 Day) $5,000 $250K GTD", 5000, 250000, ""),
 ("U-WPT39", "2026-12-19", "1:00 PM", "PLO $10,500", 10500, None, ""),
 ("U-WPT40", "2026-12-19", "1:00 PM", "NLH 6-Max $3,000 $500K GTD", 3000, 500000, ""),
 ("U-WPT41", "2026-12-19", "1:00 PM", "TORSE Championship (2 Day) $1,600", 1600, None, ""),
 ("U-WPT42", "2026-12-19", "6:00 PM", "NLH 6-Max Turbo $600 $50K GTD", 600, 50000, ""),
 ("U-WPT43", "2026-12-20", "12:00 PM", "NLH $600 $50K GTD", 600, 50000, ""),
 ("U-WPT44", "2026-12-20", "1:00 PM", "NLH 8-Max $10,500", 10500, None, ""),
 ("U-WPT46", "2026-12-20", "6:00 PM", "5-Card PLO Turbo $600 $50K GTD", 600, 50000, ""),
 ("U-WPT47", "2026-12-21", "12:00 PM", "NLH $1,100 $100K GTD", 1100, 100000, ""),
]:
    wpt_unverified(*row)

# ---------------------------------------------------------------------------
# Caesars / MGM — recurring daily events (from official pages; separate section)
# ---------------------------------------------------------------------------
ev(id="C-CP-100", venue="Caesars Palace", series="Daily (recurring)", date="Daily", day="", start="10:00 AM / 2:00 PM / 6:00 PM / 9:00 PM",
   event_no="", name="Daily NLH $100–$160, $1,000 GTD", game="NLH", format="add-on",
   buy_in=100, house_fee=None, prize_pool=None, gtd=1000, gtd_includes_bounties=False,
   chips=None, level_min=None, late_reg=None, eligibility="21+ (Caesars Rewards)",
   classification="excluded",
   exclude_reason="$50 add-on for 15,000 chips at the first break (official tournament guide) — spend-more mechanic. Recurring schedule, not a dated calendar. Re-entry status NOT verified.",
   rules={
     "single_entry": {"value": "NO — paid add-on confirmed", "excerpt": "The page describes a $50 add-on for 15,000 chips at the first break.", "source": "CAESARS", "retrieved": RETRIEVED},
     "re_entry": {"value": None, "excerpt": "Re-entry status not stated on the official page.", "source": "CAESARS", "retrieved": RETRIEVED},
     "rebuy": {"value": None, "excerpt": "Not stated.", "source": "CAESARS", "retrieved": RETRIEVED},
     "addon": {"value": "YES — $50 for 15,000 chips at first break", "excerpt": "$50 add-on for 15,000 chips at the first break.", "source": "CAESARS", "retrieved": RETRIEVED},
     "house_fee": {"value": None, "excerpt": "Fee split not published on the page.", "source": "CAESARS", "retrieved": RETRIEVED},
   },
   note="Official flier lists $50 add-on at the 10 AM and 2 PM entries; 6 PM/9 PM add-on status not verified. Buy-in alternates $100/$160 by start per the official flier (2 PM and 9 PM are $160).",
   sources=["CAESARS", "CAESARS_FLIER"])

ev(id="C-HS-9AM", venue="Horseshoe Las Vegas", series="Daily (recurring)", date="Daily", day="", start="9:00 AM / 11:00 AM / 2:00 PM / 5:00 PM / 8:00 PM / 11:00 PM",
   event_no="", name="Daily NLH (buy-in and guarantee not published on the guide page)", game="NLH", format="unverified",
   buy_in=None, house_fee=None, prize_pool=None, gtd=None, gtd_includes_bounties=False,
   chips=None, level_min=None, late_reg=None, eligibility="21+ (Caesars Rewards)",
   classification="unverified",
   exclude_reason="UNVERIFIED — the official Caesars guide lists recurring start times (including a 9:00 AM start, the earliest verified anywhere in this dataset) but does not publish buy-in, guarantee, or entry rules for Horseshoe events.",
   rules={
     "single_entry": {"value": None, "excerpt": "Entry rules not published on the official guide page.", "source": "CAESARS", "retrieved": RETRIEVED},
     "re_entry": {"value": None, "excerpt": "Not stated.", "source": "CAESARS", "retrieved": RETRIEVED},
     "rebuy": {"value": None, "excerpt": "Not stated.", "source": "CAESARS", "retrieved": RETRIEVED},
     "addon": {"value": None, "excerpt": "Not stated.", "source": "CAESARS", "retrieved": RETRIEVED},
     "house_fee": {"value": None, "excerpt": "Not stated.", "source": "CAESARS", "retrieved": RETRIEVED},
   },
   note="A 9:00 AM daily start exists (earliest verified start across checked sources). No event verified at 8:00 AM anywhere.",
   sources=["CAESARS"])

ev(id="M-MGM-SAT", venue="MGM Grand", series="Weekly (recurring)", date="Saturday", day="Sat", start="11:10 AM (PDF) / 11:00 AM (web)",
   event_no="", name="$150 NLH $2,000 GTD (Saturday)", game="NLH", format="loyalty",
   buy_in=150, house_fee=None, prize_pool=None, gtd=2000, gtd_includes_bounties=False,
   chips=None, level_min=None, late_reg=None, eligibility="21+ (MGM Rewards)",
   classification="excluded",
   exclude_reason="Spend-more loyalty mechanic: five $120 daily entries earn one free Saturday entry (official page). Re-entry/add-on rules not published in the official PDF — unverified.",
   rules={
     "single_entry": {"value": "NO — loyalty spend-more mechanic", "excerpt": "Five $120 daily entries earn one free Saturday entry.", "source": "MGM_POKER", "retrieved": RETRIEVED},
     "re_entry": {"value": None, "excerpt": "Not stated on official sources read.", "source": "MGM_POKER", "retrieved": RETRIEVED},
     "rebuy": {"value": None, "excerpt": "Not stated.", "source": "MGM_POKER", "retrieved": RETRIEVED},
     "addon": {"value": None, "excerpt": "Not stated.", "source": "MGM_POKER", "retrieved": RETRIEVED},
     "house_fee": {"value": None, "excerpt": "Not stated.", "source": "MGM_POKER", "retrieved": RETRIEVED},
   },
   sources=["MGM_POKER"])

events = {
  "as_of": RETRIEVED,
  "verification_method": "Every Venetian structure sheet (1-37) and the complete Wynn WPT structures PDF (8 chunks) were read in full on 2026-11-16. Classification: 'single_entry_confirmed' = official sheet read in full, no re-entry/rebuy/add-on clause; 'flagged_ambiguous' = sheet read but wording leaves entry count unsettled; 'excluded' = re-entry/rebuy/add-on/multi-flight/satellite/team/spend-more confirmed or event type not a cash freezeout; 'unverified' = entry terms not published in the sources read. Values are copied from official sources only; null = not stated on the source.",
  "events": E,
}
with open(os.path.join(OUT, "events-f0816fab.json"), "w") as f:
    json.dump(events, f, indent=1)
print("events:", len(E))
from collections import Counter
print(Counter(e["classification"] for e in E))
