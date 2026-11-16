#!/usr/bin/env python3
"""Build data JSON and the static GitHub Pages site for the Las Vegas Strip poker research.

Rules enforced here:
- Every row must cite at least one official source key from data/sources.json.
- Any value not in the verified notes is left blank and flagged (never inferred).
- Single-entry = 1-day event whose official structure sheet was read and contains no
  re-entry/rebuy language. Anything else (flighted, re-entry, unread sheet) is kept out of
  the single-entry list.
"""
import html
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = json.load(open(os.path.join(ROOT, "data", "sources.json")))
TODAY = "2026-11-16"

def esc(s):
    return html.escape("" if s is None else str(s))

def money(v):
    return "" if v is None else f"${v:,.0f}"

# ---------------------------------------------------------------- Venetian (DSE IV)
V = "Venetian / Palazzo (DSE IV)"
V_NOTE_STRUCT_READ = "Structure sheet read; no re-entry or rebuy language found."

def vrow(ev, day, time, name, buy, gtd, fee, reg, chips, level, struct, notes="", extra_src=()):
    srcs = ["V_EVENT", "V_SCHED"] + ([struct] if struct else []) + list(extra_src)
    return dict(venue=V, event=ev, date=day, time=time, name=name, buy_in=buy, gtd=gtd,
                fee=fee, reg_closes=reg, chips=chips, level=level, notes=notes, src=srcs)

# Single-entry candidates (1-day events whose structure sheet was read; no re-entry language)
SINGLE = [
    vrow(14, "2026-11-27 (Fri)", "11:10 AM", "$600 No-Limit Hold'em (1Day)", 600, 30000, 90, "4:55 PM", 40000, "30", "S_V7", V_NOTE_STRUCT_READ),
    vrow(16, "2026-11-28 (Sat)", "11:10 AM", "$600 NLH Bounty (1Day) — $200 bounties from start, $500 once in the money", 600, 30000, 90, "4:55 PM", 40000, "30", "S_V11", "Bounty values change at the money; see sheet."),
    vrow(24, "2026-12-02 (Wed)", "10:10 AM", "$600 NLH Seniors (1Day) — must be 50+", 600, 40000, 90, "3:55 PM", 40000, "30", "S_V17", "Age 50+ required."),
    vrow(28, "2026-12-06 (Sun)", "11:10 AM", "$600 No-Limit Hold'em (1Day)", 600, 40000, 90, "4:55 PM", 40000, "30", "S_V7", V_NOTE_STRUCT_READ),
    vrow(30, "2026-12-07 (Mon)", "11:10 AM", "$600 NLH Bounty (1Day) — $200 to start, $500 in the money", 600, 40000, 90, "4:55 PM", 40000, "30", "S_V11", "Bounty values change at the money; see sheet."),
    vrow(32, "2026-12-08 (Tue)", "10:10 AM", "$600 NLH Seniors (1Day) — must be 50+", 600, 40000, 90, "3:55 PM", 40000, "30", "S_V17", "Age 50+ required."),
    vrow(54, "2026-12-16 (Wed)", "11:10 AM", "$600 NLH Bounty (1Day) — $200 to start, $500 in the money", 600, 50000, 90, "4:55 PM", 40000, "30", "S_V11", "Bounty values change at the money; see sheet."),
    vrow(63, "2026-12-23 (Wed)", "11:10 AM", "$600 No-Limit Hold'em (1Day)", 600, 30000, 90, "4:55 PM", 40000, "30", "S_V7", V_NOTE_STRUCT_READ),
    vrow(52, "2026-12-15 (Tue)", "11:10 AM", "$1,100 NLH Progressive Knock-Out Bounty (1Day)", 1100, 75000, 130, "4:55 PM", 40000, "30", "S_V34", "PKO: bounty money counts toward guarantee per sheet."),
    vrow(10, "2026-11-25 (Wed)", "11:10 AM", "$400 No-Limit Hold'em (1Day)", 400, 15000, 65, "4:55 PM", 40000, "30", "S_V6", V_NOTE_STRUCT_READ),
    vrow(8, "2026-11-23 (Mon)", "5:10 PM", "$200 NLH Progressive Knock-Out Bounty (1Day)", 200, 8000, 40, "9:40 PM", 25000, "30", "S_V30", "PKO."),
    vrow(6, "2026-11-22 (Sun)", "11:10 AM", "$200 No-Limit Hold'em (1Day)", 200, None, 40, "3:40 PM", 30000, "30", "S_V29", "No guarantee on schedule or sheet (blank)."),
    vrow(18, "2026-11-28 (Sat)", "5:10 PM", "$200 NLH PokerAtlas Valuetown Bounty (1Day)", 200, 20000, 40, "9:40 PM", 25000, "30", "S_V8", "PokerAtlas PRO: $20 rake discount (applies to PRO members)."),
    vrow(58, "2026-12-19 (Sat)", "5:10 PM", "$200 NLH PokerAtlas Valuetown Bounty (1Day)", 200, 20000, 40, "9:40 PM", 25000, "30", "S_V8", "PokerAtlas PRO: $20 rake discount (applies to PRO members)."),
]
# Remove the placeholder row for event 2 — it is reclassified to review below.

for ev, day, gtd in [(9, "2026-11-24 (Tue)", 8000), (11, "2026-11-25 (Wed)", 8000), (13, "2026-11-26 (Thu)", 8000),
                     (15, "2026-11-27 (Fri)", 8000), (21, "2026-11-29 (Sun)", 8000), (22, "2026-11-30 (Mon)", 8000),
                     (23, "2026-12-01 (Tue)", 8000), (25, "2026-12-02 (Wed)", 8000), (60, "2026-12-20 (Sun)", 8000),
                     (61, "2026-12-21 (Mon)", 8000), (62, "2026-12-22 (Tue)", 8000), (64, "2026-12-23 (Wed)", 8000)]:
    SINGLE.append(vrow(ev, day, "5:10 PM", "$200 NLH Bounty (1Day)", 200, gtd, 40, "9:40 PM", 25000, "30", "S_V1", "$50 bounty per elimination per sheet."))

for ev, day in [(29, "2026-12-06 (Sun)"), (31, "2026-12-07 (Mon)"), (34, "2026-12-08 (Tue)"), (38, "2026-12-09 (Wed)"),
                (42, "2026-12-10 (Thu)"), (50, "2026-12-13 (Sun)"), (51, "2026-12-14 (Mon)"), (53, "2026-12-15 (Tue)"),
                (55, "2026-12-16 (Wed)")]:
    SINGLE.append(vrow(ev, day, "5:10 PM", "$300 NLH Bounty (1Day)", 300, 15000, 50, "9:40 PM", 25000, "30", "S_V15", "Bounty per sheet."))

for ev, day in [(3, "2026-11-19 (Thu)"), (4, "2026-11-20 (Fri)"), (5, "2026-11-21 (Sat)")]:
    SINGLE.append(vrow(ev, day, "10:10 AM", "$200 NLH RaceDay Stack (1Day) — race to finish before the race", 200, None, 35, "12:25 PM", 30000, "20/15", "S_V18", "No guarantee listed on schedule or sheet (blank)."))

SINGLE.sort(key=lambda r: (-(r["buy_in"] or 0), -(r["gtd"] or 0), r["date"]))

# Flighted / multi-day Venetian events — re-entry status not established (separate section)
FLIGHTED = [
    vrow(1, "2026-11-16 to 2026-11-18", "11:10 AM / 5:10 PM (flights 1A–1D)", "$300 No-Limit Hold'em (Flights 1A–1D; Day 2 restart Nov 18)", 300, 75000, None, "3:40 PM / 8:40 PM", 30000, "40/30", "S_V10", "Multi-flight; re-entry not confirmed. Structure sheet not read in verified notes."),
    vrow(7, "2026-11-23 to 2026-11-25", "11:10 AM (1A/1B)", "$400 No-Limit Hold'em (Flights 1A/1B; Day 2 restart Nov 25)", 400, 75000, 70, "5:55 PM", 40000, "40", "S_V2", "Multi-flight; re-entry status not stated in sheet read."),
    vrow(19, "2026-11-29 to 2026-12-02", "11:10 AM (1A–1C)", "$400 No-Limit Hold'em (Flights 1A–1C; Day 2 restart Dec 2)", 400, 75000, 70, "5:55 PM", 40000, "40", "S_V3", "Multi-flight; sheet 3 read for GTD only; fee not in verified notes."),
    vrow(26, "2026-12-03 to 2026-12-06", "11:10 AM (1A–1F)", "$800 No-Limit Hold'em (Flights 1A–1F; Day 2 restart Dec 6)", 800, 500000, 110, "3:40 PM / 8:40 PM", 40000, "40/30/20", "S_V12", "Six flights; re-entry status not stated in sheet read."),
    vrow(39, "2026-12-10 to 2026-12-11", "10:10 AM (2-day)", "$800 No-Limit Hold'em LIPS Ladies (2Day) — Women in Poker Main Event", 800, 40000, None, "4:55 PM", 40000, "40", "S_V32", "Two-day event; structure sheet not read — flagged."),
    vrow(47, "2026-12-12 to 2026-12-14", "10:10 AM (1A) / 6:10 PM (1B)", "$2,200 No-Limit Hold'em PokerAtlas Championship Title Event", 2200, 1000000, 225, "4:55 PM / 11:10 PM", 40000, "40/30", "S_V21", "Flights 1A/1B; re-entry status not stated in sheet read."),
    vrow(49, "2026-12-12 to 2026-12-15", "10:10 AM (Seniors 1A/1B)", "$1,100 No-Limit Hold'em Seniors (50+; Flights 1A/1B)", 1100, 300000, 140, "4:55 PM", 40000, "40", "S_V20", "50+ required; flights; re-entry not stated in sheet read."),
    vrow(56, "2026-12-17 to 2026-12-20", "10:10 AM (1A/1C/1E) / 6:10 PM (1B/1D)", "$1,100 No-Limit Hold'em (Flights 1A–1E; Day 2 restart Dec 20)", 1100, 500000, 140, "4:55 PM / 11:10 PM", 40000, "40/30", "S_V35", "$40 rake discount on some entries per schedule; re-entry not stated in sheet read."),
    vrow(59, "2026-12-20 to 2026-12-23", "11:10 AM (1A–1C)", "$600 No-Limit Hold'em (Flights 1A–1C; Day 2 restart Dec 23)", 600, 150000, 95, "5:55 PM", 40000, "40", "S_V4", "$20 rake discount on early entry per schedule; re-entry not stated in sheet read."),
]

# Venetian events on the schedule that could not be verified against a structure sheet
REVIEW_VENETIAN = [
    vrow(2, "2026-11-18 (Wed)", "11:10 AM", "$300 No-Limit Hold'em (1Day)", 300, 10000, None, "4:55 PM", 40000, "30", None, "Structure sheet 5 not read; fee and re-entry unverified."),
    vrow(12, "2026-11-26 (Thu)", "11:10 AM", "$300 No-Limit Hold'em (1Day)", 300, 10000, None, "4:55 PM", 40000, "30", None, "Structure sheet 5 not read; fee and re-entry unverified."),
    vrow(17, "2026-11-28 (Sat)", "12:10 PM", "$400 Pot Limit Omaha Bounty (1Day)", 400, 15000, None, "4:40 PM", 30000, "30", None, "Structure sheet not read."),
    vrow(20, "2026-11-29 (Sun)", "12:10 PM", "$300 Pot Limit Omaha Double Board Bomb Pot (1Day)", 300, 10000, None, "4:40 PM", 30000, "30", None, "Structure sheet not read."),
    vrow(27, "2026-12-03 (Thu)", "12:10 PM", "$600 BIG O (1Day)", 600, 25000, None, "4:40 PM", 30000, "30", None, "Structure sheet not read."),
    vrow(36, "2026-12-09 (Wed)", "11:10 AM", "$800 NLH Bounty (1Day) — $200 to start, $500 in the money", 800, 75000, None, "4:55 PM", 40000, "30", None, "Structure sheet not read."),
    vrow(40, "2026-12-10 (Thu)", "12:10 PM", "$600 Pot Limit Omaha Bounty (1Day)", 600, 25000, None, "4:40 PM", 30000, "30", None, "Structure sheet not read."),
    vrow(43, "2026-12-11 (Fri)", "11:10 AM", "$600 NLH Kings and Queens Bounty (1Day) — open to all", 600, 30000, None, "4:55 PM", 40000, "30", None, "Structure sheet not read."),
    vrow(57, "2026-12-17 (Thu)", "12:10 PM", "$600 Pot Limit Omaha Double Board Bomb Pot (1Day)", 600, 25000, None, "4:40 PM", 30000, "30", None, "Structure sheet not read."),
    vrow(35, "2026-12-08 (Tue)", "10:10 AM", "$600 NLH LIPS Jingle Tag Team (1Day) — team entry", 600, 10000, None, "2:40 PM", 40000, "30", None, "Team format (female/female or female/male). Structure not read."),
]

def satrow(ev, day, time, name, buy, prize, reg, chips, level):
    return dict(venue=V, event=ev, date=day, time=time, name=name, buy_in=buy, gtd=None, fee=None,
                reg_closes=reg, chips=chips, level=level, notes=f"Satellite — prize: {prize}. Re-entry not confirmed.",
                src=["V_EVENT", "V_SCHED"])

SATELLITES = [
    satrow(33, "2026-12-08 (Tue)", "4:10 PM", "$100 NLH LIPS Ladies Milestone Satellite (1Day)", 100, "2 seats to Event 39", "6:25 PM", 20000, "20"),
    satrow(37, "2026-12-09 (Wed)", "4:10 PM", "$100 NLH LIPS Ladies Milestone Satellite (1Day)", 100, "2 seats to Event 39", "6:25 PM", 20000, "20"),
    satrow(41, "2026-12-10 (Thu)", "4:10 PM", "$260 NLH Milestone Satellite (1Day)", 260, "2 seats to Event 47", "6:25 PM", 20000, "20"),
    satrow(44, "2026-12-11 (Fri)", "4:10 PM", "$260 NLH Milestone Satellite (1Day)", 260, "2 seats to Event 47", "6:25 PM", 20000, "20"),
    satrow(45, "2026-12-11 (Fri)", "8:10 PM", "$260 NLH Turbo Milestone Satellite (1Day)", 260, "2 seats to Event 47", "9:55 PM", 20000, "15"),
    satrow(46, "2026-12-12 (Sat)", "9:10 AM", "$260 NLH Turbo Milestone Satellite (1Day)", 260, "2 seats to Event 47", "10:55 AM", 20000, "15"),
    satrow(48, "2026-12-12 (Sat)", "12:10 PM", "$260 NLH Turbo Milestone Satellite (1Day)", 260, "2 seats to Event 47", "1:55 PM", 20000, "15"),
]

# ---------------------------------------------------------------- Spending advantage / re-entry (separate section)
def srow(venue, day, time, name, buy, gtd, fee, rule, src, notes=""):
    return dict(venue=venue, event="", date=day, time=time, name=name, buy_in=buy, gtd=gtd, fee=fee,
                reg_closes="", chips="", level="", notes=(rule + (" " + notes if notes else "")), src=src)

W = "Wynn Las Vegas (WPT World Championship)"
B = "Bellagio"
WD = "Wynn Las Vegas (Daily)"
SPENDING = [
    srow(W, "2026-11-27", "1:00 PM", "Pot Limit Omaha", 400, 0, "$45 fee + $18 staff charge (prize pool $337)", "Unlimited re-entry until start of Level 9 per notes.", ["W_POKER", "W_WPT_SCHED", "W_WPT_STRUCT"], "30K chips. Schedule PDF re-fetch failed (HTTP 500); values from earlier read of the PDF."),
    srow(W, "2026-11-30 to 2026-12-04", "11:00 AM (Day 1A)", "No-Limit Hold'em $800", 800, 1000000, "$72 fee + $33 staff charge (prize pool $695)", "Unlimited re-entry per flight until start of Level 9.", ["W_POKER", "W_WPT_SCHED", "W_WPT_STRUCT"]),
    srow(W, "2026-12-03 to 2026-12-05", "11:00 AM (Day 1A)", "No-Limit Hold'em $1,600", 1600, 1000000, "$120 + $50 (prize pool $1,430)", "Unlimited re-entry per flight until start of Level 10.", ["W_POKER", "W_WPT_SCHED", "W_WPT_STRUCT"]),
    srow(W, "2026-12-05 to 2026-12-12", "11:00 AM (Day 1A)", "WPT Prime Championship $1,100 (5-day NLH)", 1100, 5000000, "$90 + $40 (prize pool $970)", "One entry plus one re-entry per flight until start of Level 10.", ["W_POKER", "W_WPT_SCHED", "W_WPT_STRUCT"], "Not single-entry."),
    srow(W, "2026-12-06 to 2026-12-07", "11:00 AM (Day 1A)", "PLO Mystery Bounty $1,600", 1600, 500000, "$120 + $50 plus $500 bounty pool (prize pool $930)", "Unlimited re-entry per flight until start of Level 10.", ["W_POKER", "W_WPT_SCHED", "W_WPT_STRUCT"]),
    srow(W, "2026-12-05 to 2026-12-21", "9:00 PM (select dates)", "NLH Turbo $600", 600, 50000, "$60 + $25 (prize pool $515)", "Unlimited re-entry until start of Level 9.", ["W_POKER", "W_WPT_SCHED", "W_WPT_STRUCT"], "Time as recorded in notes; verify."),
    srow(W, "Dec 13, 2026", "", "WPT World Championship $10,400 ($1M added)", 10400, None, None, "Entry rules NOT verified.", ["W_POKER"], "Flagged: buy-in and rules must be checked on the official structures sheet."),
    srow(W, "Nov 27 – Dec 21, 2026", "", "Super Gold Million $400 ($3,000,000 GTD)", 400, 3000000, None, "Re-entry and dates NOT verified.", ["W_POKER"], "Named on Wynn poker page; details not in verified notes."),
    srow(WD, "Fri (poster)", "12:00 PM", "NLH Rebuy $240", 240, 40000, None, "Rebuy event; re-entry by rebuy per Wynn poker page.", ["W_POKER", "W_DAILY"], "Guarantee from Wynn poker page ($40,000 guaranteed NLH Rebuy on Friday)."),
    srow(WD, "Mon–Thu, Sat, Sun (poster)", "12:00 PM", "NLH $200", 200, None, None, "Re-entry NOT verified.", ["W_DAILY"], "Guarantee not captured in verified notes."),
    srow(WD, "Nightly (poster)", "6:00 PM", "NLH $160", 160, 10000, None, "Re-entry NOT verified.", ["W_POKER", "W_DAILY"], "$10,000 guaranteed each evening at 6 p.m. per Wynn poker page."),
    srow(B, "Every Friday (dates per PDF; not captured)", "11:00 AM", "NLH $600", 600, None, "$50 house fee; $40 optional gratuity (prize pool $510)", "Buy-in and re-enter through end of Level 8.", ["B_FRI"]),
    srow(B, "Every Sunday (dates per PDF; not captured)", "11:00 AM", "H.O.R.S.E. $400", 400, None, "$35 house fee; $25 optional gratuity (prize pool $340)", "Buy-in and re-enter through end of Level 8.", ["B_SUN"]),
    srow(B, "Every Saturday (dates per PDF; not captured)", "11:00 AM", "NLH $1,100 (PDF heading) — page link says $1,000", 1100, 50000, "$50 admin; $40 optional gratuity (prize pool $510)", "Re-entry NOT verified (flagged).", ["B_SAT"], "Conflicting title ($1,100 vs $1,000) and a level 3 blind typo in the sheet. Flagged."),
]

# ---------------------------------------------------------------- Hotels
HOTELS = [
    dict(name="The Venetian", address="3355 S. Las Vegas Blvd (Strip)", resort_fee="$55 plus tax per night", rate="from $119 (poker suite, conditional; before fee and tax)",
         walk=None, src=["V_RESORT_FEE", "V_POKER_RATES", "V_HOTEL_TC"], notes="Poker suite rate is conditional on qualifying play each night and on availability; blackout dates may apply. Dated quote not captured. Walking time not verified."),
    dict(name="The Palazzo", address="3325 S. Las Vegas Blvd (Strip)", resort_fee="$55 plus tax per night", rate="from $209 (poker suite, conditional; before fee and tax)",
         walk=None, src=["V_RESORT_FEE", "V_POKER_RATES"], notes="Same poker-suite conditions as the Venetian. Dated quote not captured. Walking time not verified."),
    dict(name="Wynn Las Vegas", address="3131 S. Las Vegas Blvd (Strip)", resort_fee="$55 plus tax per room night", rate=None,
         walk=None, src=["W_TC"], notes="Fee from search snippet of official terms; full page not fetched. Rate and walk time blank."),
    dict(name="ARIA Resort & Casino", address="3730 S. Las Vegas Blvd (Strip)", resort_fee="$55 plus tax per night; $50 plus tax extra occupant", rate=None,
         walk=None, src=["A_TC"], notes="Gold+ waives the fee. Incidental $150–$500/day by room type."),
    dict(name="Bellagio", address="3600 S. Las Vegas Blvd (Strip)", resort_fee="$55 plus tax per night; $50 plus tax extra occupant", rate=None,
         walk=None, src=["B_TC"], notes="Gold+ waives the fee. $150/day incidental."),
]

# ---------------------------------------------------------------- Flagged-for-review rows (unverified or unstated)
FLAGS = [
    ("Venetian: Re-entry/add-on rules", "All Venetian events", "Structure sheets read contain no re-entry language. Absence is not verification. Confirm with the official Venetian poker room before paying."),
    ("Venetian: Structure sheets not read", "Events 2, 12, 17, 20, 27, 36, 39, 40, 43, 57, 35 and satellites", "Fee and rules left blank."),
    ("Venetian: Event 19 fee", "Event 19", "Only GTD confirmed; fee not in verified notes."),
    ("Venetian: RaceDay Stack guarantee", "Events 3, 4, 5", "No guarantee printed on schedule or sheet."),
    ("Venetian: Event 6 guarantee", "Event 6", "No guarantee printed."),
    ("Bellagio: Saturday re-entry", "Saturday $1,100 NLH", "Title says $1,100 in PDF heading and $1,000 in link; level 3 blind typo in sheet."),
    ("Bellagio: Dates", "Friday, Saturday, Sunday", "Dates not captured from PDFs. Recurring schedule only."),
    ("Wynn: WPT World Championship $10,400", "Dec 13", "Entry rules unverified."),
    ("Wynn: Super Gold Million $400", "Named on Wynn poker page", "$3M guarantee shown. Dates, buy-in breakdown and re-entry not verified."),
    ("Wynn: Schedule PDF", "WPT schedule", "Re-fetch returned HTTP 500 on 2026-11-16. Retry before relying on a re-read."),
    ("Wynn daily 12pm $200 NLH", "Mon–Thu, Sat, Sun", "Guarantee and re-entry not verified."),
    ("Hotels: nightly rates", "All hotels", "Official rate data not captured. Cost ranking not possible."),
    ("Hotels: walking distances", "All hotels", "No official walking distances captured. 30-minute test not verified."),
    ("Hotels: Encore and others", "Encore, others", "Resort fee not verified; not listed."),
    ("Clark County transient lodging tax", "All hotels", "Secondary sources conflict (13.38% vs 10.5%–13.38%). No official county source found. Left blank."),
    ("Golden Nugget Grand Poker Series", "Downtown; June 2026", "Excluded: not on Strip and dates passed."),
    ("Aria poker schedule", "ARIA", "Official schedule not captured in verified notes. Not listed."),
]

ROOM_NOTE = "Hotel rates and walking distances are not published on official pages and were not verified. The 30-minute walk test and cost ranking are therefore left blank."

# ---------------------------------------------------------------- Write data
os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
json.dump(dict(as_of=TODAY, single_entry=SINGLE, flighted_or_reentry_unverified=FLIGHTED,
               review_unverified_venetian=REVIEW_VENETIAN, satellites=SATELLITES,
               spending_advantage_or_reentry=SPENDING),
          open(os.path.join(ROOT, "data", "tournaments.json"), "w"), indent=2, ensure_ascii=False)
json.dump(dict(as_of=TODAY, hotels=HOTELS, note=ROOM_NOTE), open(os.path.join(ROOT, "data", "hotels.json"), "w"), indent=2, ensure_ascii=False)
json.dump(dict(flags=[dict(item=a, where=b, detail=c) for a, b, c in FLAGS]), open(os.path.join(ROOT, "data", "flags.json"), "w"), indent=2, ensure_ascii=False)

# ---------------------------------------------------------------- HTML helpers
CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1d1d1f;background:#fafafa;line-height:1.5}
header{background:#14532d;color:#fff;padding:14px 24px}
header a{color:#d1fae5;margin-right:14px;text-decoration:none}
header .brand{font-weight:700;color:#fff;margin-right:24px}
main{max-width:1200px;margin:0 auto;padding:20px 24px 60px}
h1{margin-top:8px} h2{margin-top:32px;border-bottom:1px solid #e5e7eb;padding-bottom:4px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin:18px 0}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:16px}
.card .n{font-size:28px;font-weight:700;color:#14532d}
table{border-collapse:collapse;width:100%;background:#fff;font-size:14px;margin:10px 0}
th,td{border-bottom:1px solid #e5e7eb;padding:7px 8px;text-align:left;vertical-align:top}
th{background:#f0fdf4}
td.blank{background:#fef9c3}
.flag{color:#b45309;font-weight:600}
.note{background:#fff7ed;border-left:4px solid #f97316;padding:10px 14px;margin:14px 0}
.ok{background:#f0fdf4;border-left:4px solid #16a34a;padding:10px 14px;margin:14px 0}
a{color:#166534}
.small{font-size:12px;color:#555}
"""

NAV = [("index.html", "Main dashboard"), ("tournaments.html", "Full event table"), ("hotels.html", "Hotel comparison"),
       ("flagged.html", "Evidence review"), ("pages/single-entry.html", "Single-entry candidates"),
       ("pages/spending.html", "Re-entry / spending"), ("pages/schedule.html", "8 AM schedule"),
       ("pages/hotel-costs.html", "Hotel cost detail"), ("pages/summary.html", "Summary"),
       ("pages/flagged-rows.html", "Flagged rows"), ("pages/improvements.html", "Site improvements"),
       ("pages/questions.html", "Questions"), ("pages/repo-review.html", "Repo review")]

def page(path, title, body):
    depth = path.count("/")
    prefix = "../" * depth
    nav = "".join(f'<a href="{prefix}{href}">{label}</a>' for href, label in NAV)
    out = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · Strip Poker Research</title>
<style>{CSS}</style></head><body>
<header><span class="brand">Strip Poker</span>{nav}</header>
<main><h1>{esc(title)}</h1>{body}
<p class="small">Data as of {TODAY}. Every row cites an official source. Blank cells are unverified and are listed on the Flagged page.</p>
</main></body></html>"""
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(out)

def link(key, prefix=""):
    if key not in SRC:
        return ""
    v = SRC[key]
    return f'<a href="{esc(v["url"])}" target="_blank" rel="noopener">{esc(v["label"])}</a>'

def srcs(keys):
    return " · ".join(link(k) for k in keys if k in SRC)

def cell(v, fmt=None):
    if v is None or v == "":
        return '<td class="blank flag">⚑ unverified</td>'
    return f"<td>{esc(fmt(v) if fmt else v)}</td>"

def tourney_table(rows, cols):
    head = "".join(f"<th>{esc(c[0])}</th>" for c in cols) + "<th>Official source</th>"
    body = ""
    for r in rows:
        cs = []
        for name, key, fmt in cols:
            cs.append(cell(r.get(key), fmt))
        body += "<tr>" + "".join(cs) + f"<td>{srcs(r['src'])}</td></tr>"
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"

COLS = [("Date", "date", None), ("Time", "time", None), ("Event", "name", None), ("Event #", "event", None),
        ("Buy-in", "buy_in", money), ("Guarantee", "gtd", money), ("Fee", "fee", money),
        ("Reg. closes", "reg_closes", None), ("Chips", "chips", lambda v: f"{v:,}" if isinstance(v, int) else v),
        ("Level", "level", None), ("Notes", "notes", None)]

# ---------------------------------------------------------------- Pages
n_single = len(SINGLE)
n_flag = len(FLAGS) + len(REVIEW_VENETIAN)
resort_verified = sum(1 for h in HOTELS if h["resort_fee"])

cards = f"""<div class="cards">
<div class="card"><div class="n">{n_single}</div>Single-entry Venetian 1-day events (verified structure sheets)</div>
<div class="card"><div class="n">{len(FLIGHTED)+len(SPENDING)+len(SATELLITES)}</div>Re-entry, flighted, or satellite rows (separate sections)</div>
<div class="card"><div class="n">{n_flag}</div>Flagged or unverified items</div>
<div class="card"><div class="n">{resort_verified}</div>Hotels with a verified resort fee</div></div>"""


# Single-entry
page("pages/single-entry.html", "Single-entry candidates (not confirmed)",
     '<div class="note"><b>Candidates only — none is confirmed single-entry.</b> Each row is a 1-day Venetian event whose official structure sheet was read, and that sheet contains no re-entry or rebuy language. Absence of language is not confirmation. Confirm the rules with the poker room before you register.</div>'
     + tourney_table(SINGLE, COLS))

# Spending/re-entry
page("pages/spending.html", "Re-entry and spending-advantage events (separate)",
     '<div class="note">These events allow re-entry, rebuys or unverified rules. They are not single-entry and are kept separate on purpose.</div>'
     + tourney_table(SPENDING, [("Date", "date", None), ("Time", "time", None), ("Event", "name", None), ("Buy-in", "buy_in", money),
                                ("Guarantee", "gtd", money), ("Fee", "fee", None), ("Re-entry / rules", "notes", None)]))

# Flighted + review + satellites are shown on Flagged page and a spending-adjacent note.
page("pages/flagged-rows.html", "Flagged for Review — row detail",
     '<div class="note">Flagged items do not block merge. They are unverified and must be checked before use.</div>'
     + '<h2>Flighted events (re-entry not confirmed)</h2>' + tourney_table(FLIGHTED, COLS)
     + '<h2>Events with unread structure sheets</h2>' + tourney_table(REVIEW_VENETIAN, COLS)
     + '<h2>Satellites (prize is a seat, not cash)</h2>' + tourney_table(SATELLITES, COLS)
     + '<h2>Unverified items</h2><table><thead><tr><th>Item</th><th>Where</th><th>Detail</th></tr></thead><tbody>'
     + "".join(f"<tr><td>{esc(a)}</td><td>{esc(b)}</td><td>{esc(c)}</td></tr>" for a, b, c in FLAGS)
     + '</tbody></table>')

# Schedule
days = {}
for r in SINGLE + REVIEW_VENETIAN[:0]:
    days.setdefault(r["date"][:10], []).append(r)
sched_rows = ""
for d in sorted(days):
    evs = sorted(days[d], key=lambda r: (r["time"]))
    items = "<br>".join(f'{esc(r["time"])} — #{r["event"]} {esc(r["name"])} (buy-in {money(r["buy_in"])}, reg. closes {esc(r["reg_closes"])})' for r in evs)
    sched_rows += f"<tr><td>{esc(d)}</td><td>{items}</td></tr>"
sched_body = f"""<div class="note"><b>Plan from 8 AM.</b> Events are listed by start time. Official pages give no durations, so overlap between events cannot be verified. The table shows official start and registration deadlines only. No single-entry events begin before 10:10 AM, so the 8 AM start is for travel and registration. Check the time of each registration close before you plan the day.</div>
<table><thead><tr><th>Date</th><th>Single-entry events (start order)</th></tr></thead><tbody>{sched_rows}</tbody></table>
<p class="small">Sources: {srcs(['V_SCHED','V_EVENT'])}</p>"""
page("pages/schedule.html", "8 AM all-day schedule (single-entry)", sched_body)

# Hotels
hotel_rows = ""
for h in HOTELS:
    hotel_rows += f"<tr><td>{esc(h['name'])}</td><td>{esc(h['address'])}</td><td>{esc(h['resort_fee'])}</td>" \
                  f"<td class='blank flag'>⚑ unverified</td><td class='blank flag'>⚑ unverified</td><td>{esc(h['notes'])}</td><td>{srcs(h['src'])}</td></tr>"
hotel_body = f"""<div class="note">{esc(ROOM_NOTE)} Resort fees are shown as the official terms state them. Clark County lodging tax is unverified and left blank.</div>
<table><thead><tr><th>Hotel</th><th>Address</th><th>Resort fee</th><th>Nightly rate</th><th>Walk to poker (30 min?)</th><th>Notes</th><th>Official source</th></tr></thead><tbody>{hotel_rows}</tbody></table>"""
page("pages/hotel-costs.html", "Hotel cost detail", hotel_body)

# Summary
summary = f"""<h2>Executive summary</h2>
<ul>
<li><b>No event is confirmed single-entry.</b> {n_single} Venetian 1-day events (Nov 18–Dec 23, 2026) have a structure sheet read with no re-entry language. They are candidates only, consistent with the main site.</li>
<li><b>Largest guarantee among candidates:</b> the $1,100 PKO (Event 52, Dec 15, $75,000 GTD, official schedule).</li>
<li><b>Wynn WPT and most Bellagio events allow re-entry</b> (Wynn: unlimited per flight, Prime: one re-entry). They are kept in the separate spending section.</li>
<li><b>Hotel ranking is partial.</b> Official resort fees are $55 plus tax per night at the Venetian, Palazzo, Wynn, ARIA and Bellagio. The Venetian and Palazzo publish poker suite rates from $119 and $209 per night, before the $55 fee and tax. Those rates require qualifying play each night (six hours of cash, or a $300+ tournament buy-in). Walking distances and dated quotes are not verified.</li>
<li><b>Clark County tax is unverified</b> and left blank.</li>
</ul>
<h2>Analysis</h2>
<ul>
<li>Candidate events are concentrated at The Venetian / Palazzo. The cheapest candidates are $200 events at 5:10 PM.</li>
<li>The poker suite rate requires a $300+ tournament buy-in each night (or six hours of cash). Candidate $300+ events therefore also satisfy that requirement, subject to the rate terms.</li>
<li>For the 8 AM plan, 11:10 AM events (reg closes 4:55 PM) and 5:10 PM events (reg closes 9:40 PM) do not overlap on start time. Event length is unpublished, so overlap cannot be ruled out.</li>
<li>Re-entry events carry an advantage for players who can spend more. They are excluded from the candidate list.</li>
</ul>
<h2>Method</h2>
<p>Schedule data from the official Venetian DSE IV PDF (fetched 2026-11-16). Structure sheets were used for fees and re-entry language. Wynn values come from its official PDFs read earlier; the Wynn schedule PDF failed on re-fetch. Bellagio values come from its dated PDFs. Aggregator sites were not used.</p>"""
page("pages/summary.html", "Executive summary and analysis", summary)

# Improvements (no changes until approved)
imp = """<div class="note">These are suggestions only. No changes are made to the site until you choose an option.</div>
<ol>
<li>Add a per-row "last checked" date and link to the exact PDF page.</li>
<li>Add a filter by buy-in band and by start time.</li>
<li>Add a hotel tab once a rate source is found (e.g. an official rate feed or a booking-page check).</li>
<li>Add a re-check job that re-fetches each official PDF and flags changes.</li>
<li>Add the Aria schedule once an official source is captured.</li>
</ol>"""
page("pages/improvements.html", "Site-improvement suggestions (awaiting your choice)", imp)

# Questions
qs = """<ol>
<li>Venetian re-entry rules for each event: confirm with the poker room (no re-entry language found in the sheets read).</li>
<li>Venetian structure sheets not read: 2, 5, 10, 17, 20, 27, 32, 33, 36, 40, 43, 57, 35 and satellites.</li>
<li>Wynn schedule PDF (HTTP 500 on re-fetch): retry and re-verify all WPT values.</li>
<li>Wynn $10,400 WPT World Championship entry rules (Dec 13).</li>
<li>Bellagio Saturday re-entry rule and the $1,100 vs $1,000 title conflict.</li>
<li>Official nightly rates for each hotel (rate source or booking-page check).</li>
<li>Official walking distances from each hotel to each poker room.</li>
<li>Official Clark County lodging tax rate (search the county's tax pages).</li>
<li>Encore and Aria resort-fee and poker schedule details.</li>
</ol>"""
page("pages/questions.html", "Questions and missing information", qs)

# Repo review
rr = """<h2>Repo review</h2>
<table><thead><tr><th>File / item</th><th>Finding</th><th>Official link</th></tr></thead><tbody>
<tr><td>README.md</td><td class="flag">Only "# Poker2" — no project description.</td><td>n/a</td></tr>
<tr><td>data/sources.json</td><td>Alias keys were removed. Non-official entries were moved to data/non_official_refs.json.</td><td>n/a</td></tr>
<tr><td>scripts/build.py</td><td>Generates all data and HTML. Blank cells are used for unverified values.</td><td>n/a</td></tr>
<tr><td>GitHub Pages</td><td>Deploys from main / (root). Site is at repo root.</td><td><a href="https://karagemop466-tech.github.io/Poker2/">Pages</a></td></tr>
</tbody></table>
<div class="note"><b>Irregularities:</b> no license file; no tests; Wynn schedule PDF returned HTTP 500 on re-fetch; Aria URL in earlier notes was wrong (www.ariaresortcasino.com failed; aria.mgmresorts.com is correct).</div>"""
page("pages/repo-review.html", "Repo review", rr)
print("built", n_single, len(FLIGHTED), len(SPENDING), len(SATELLITES), n_flag)
