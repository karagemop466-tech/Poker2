#!/usr/bin/env python3
"""Build the Las Vegas single-entry poker trip site from verified official sources.

Every value rendered by this script comes from an official document that was read and
transcribed by hand. A value the organiser does not publish is rendered as an empty cell and
is listed on flagged.html. The build fails if a rendered row would carry no official source.

    python3 scripts/build2026.py            # regenerate every page and JSON file
    python3 scripts/build2026.py --check    # regenerate to a temp dir and diff (CI)
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import shutil
import sys
import tempfile
from urllib.parse import urlencode

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data", "sheets"))
sys.path.insert(0, os.path.join(ROOT, "data", "verified2026"))

import part1, part2, part3, part4, part5, part6          # noqa: E402  (registers SHEETS)
import schedule as sched                                  # noqa: E402
import hotels as hotelsmod                                # noqa: E402
import content as contentmod                              # noqa: E402
import decision as decisions
import other_rooms as othermod                            # noqa: E402  (other Strip rooms)

SHEETS = part1.SHEETS
BASE = part1.BASE
RETRIEVED = "2026-11-17"
TAX = contentmod.ROOM_TAX["value"] / 100.0

OUT_DATA = os.path.join(ROOT, "data", "verified2026")
CHECKS_PATH = os.path.join(OUT_DATA, "checks.json")


def load_checks():
    """Latest scheduled re-check, keyed by URL. Absent file = the monitor has not run yet."""
    if not os.path.exists(CHECKS_PATH):
        return None, {}
    try:
        with open(CHECKS_PATH, encoding="utf-8") as f:
            d = json.load(f)
    except (OSError, ValueError):
        return None, {}
    runs = d.get("runs") or []
    latest = runs[0] if runs else {}
    return d, {r.get("url"): r for r in latest.get("results", []) if r.get("url")}


CHECKS_META, CHECKS = load_checks()
SITE = "2026"  # the consolidated surface lives under /2026/ so it never clobbers
              # the root dashboard owned by another session (see COORDINATION.md, S-11)
ASSETS = os.path.join(ROOT, SITE, "assets")

OFFICIAL_HOSTS = {
    "www.venetianlasvegas.com": "The Venetian Resort Las Vegas (official)",
    "www.wynnlasvegas.com": "Wynn Las Vegas (official)",
    "cdn.wynnresorts.com": "Wynn Resorts official document CDN",
    "www.caesars.com": "Caesars Entertainment (official)",
    "bellagio.mgmresorts.com": "Bellagio (official)",
    "mgmgrand.mgmresorts.com": "MGM Grand (official)",
    "assets.contentstack.io": "MGM Resorts official document CDN",
    "www.rwlasvegas.com": "Resorts World Las Vegas (official)",
    "www.westgateresorts.com": "Westgate Resorts (official)",
    "www.clarkcountynv.gov": "Clark County, Nevada (official)",
}

# --------------------------------------------------------------------------------------
# model
# --------------------------------------------------------------------------------------

def money(v):
    if v is None:
        return "<span class='blank' title='Not published on any official page read'>not published</span>"
    v = str(v).replace("$", "").replace(",", "").strip().upper()
    m = re.match(r"^([\d.]+)\s*(K|MILLION|M)?$", v)
    if not m:
        return html.escape(str(v))
    n = float(m.group(1))
    unit = m.group(2)
    if unit == "K":
        n *= 1_000
    elif unit in ("MILLION", "M"):
        n *= 1_000_000
    return "$%s" % format(int(n), ",")


def gtd_value(v):
    if not v:
        return None
    s = str(v).replace("$", "").replace(",", "").strip().upper()
    m = re.match(r"^([\d.]+)\s*(K|MILLION)?$", s)
    if not m:
        return None
    n = float(m.group(1))
    if m.group(2) == "K":
        n *= 1_000
    elif m.group(2) == "MILLION":
        n *= 1_000_000
    return int(n)


def tminutes(t):
    """'11:10 AM' -> minutes since midnight."""
    m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)$", t.strip().upper())
    if not m:
        return None
    h = int(m.group(1)) % 12
    if m.group(3) == "PM":
        h += 12
    return h * 60 + int(m.group(2))


def guarantee_for_event(sheet, ev_no):
    """The guarantee that belongs to THIS event, from a sheet that may serve several.

    Some official sheets print one guarantee per event number, e.g. sheet 11 reads
    "$30,000 (#16), $40,000 (#30), $50,000 (#54) - prize pool + total bounties". Taking the first
    dollar figure on that sheet would give every event $30,000. Returns (value, note) where note
    explains anything the reader needs to know about the number, or (None, reason) when the sheet
    does not print a dollar guarantee at all (e.g. satellites that guarantee seats).
    """
    if not sheet:
        return None, "no structure sheet"
    g = sheet.get("guarantee") or ""
    if not g.strip():
        return None, "sheet prints no guarantee"
    # two phrasings appear on the official sheets:
    #   "$30,000 (#16), $40,000 (#30), $50,000 (#54)"
    #   "$30,000 for Event #14 and #63; $40,000 for Event #28"
    per = re.findall(r"\$([\d,]+(?:\.\d+)?)\s*(K|MILLION|MILL)?\s*\(\s*#\s*(\d+)\s*\)", g, re.I)
    # an "A for Event #14 and #63; B for Event #28" style block: split on ";" first so a value
    # carries across the "and #n" numbers inside its own clause.
    for chunk in re.split(r"\s*;\s*", g):
        money = re.search(r"\$([\d,]+(?:\.\d+)?)\s*(K|MILLION|MILL)?", chunk, re.I)
        if not money:
            continue
        for n in re.findall(r"#\s*(\d+)", chunk):
            tup = (money.group(1), money.group(2) or "", n)
            if not any(x[0] == tup[0] and x[2] == tup[2] for x in per):
                per.append(tup)
    note_parts = []
    if per:
        hit = [p for p in per if int(p[2]) == ev_no]
        if not hit:
            return None, "sheet lists guarantees only for other event numbers"
        raw, unit, _ = hit[0]
        n = float(raw.replace(",", ""))
        u = (unit or "").upper()
        if u.startswith("K"):
            n *= 1_000
        elif u.startswith("M"):
            n *= 1_000_000
        if re.search(r"bount", g, re.I):
            note_parts.append("printed guarantee includes bounty money")
        return int(n), "; ".join(note_parts)
    # single-guarantee sheet
    if "SEATS" in g.upper() or "SEAT" in g.upper() and not re.search(r"\$", g):
        return None, "guarantee is seats, not dollars: " + g
    m = re.search(r"\$([\d,]+(?:\.\d+)?)\s*(K|MILLION|MILL)?", g, re.I)
    if not m:
        return None, "no dollar guarantee printed"
    n = float(m.group(1).replace(",", ""))
    u = (m.group(2) or "").upper()
    if u.startswith("K"):
        n *= 1_000
    elif u.startswith("M"):
        n *= 1_000_000
    if re.search(r"bount", g, re.I):
        note_parts.append("printed guarantee includes bounty money")
    if len(sheet.get("events", [])) > 1 and not per:
        note_parts.append("sheet serves %d events and prints one guarantee for them"
                          % len(sheet.get("events", [])))
    return int(n), "; ".join(note_parts)


def sheet_for_event(ev_no):
    for n, s in SHEETS.items():
        if ev_no in s.get("events", []):
            return s
    return None


def classify(ev_no, rows, sheet):
    """Return (group, reason). Groups:
       candidate   - one-day, no bounty, no satellite, no team, no re-entry clause
       bounty      - bounty or PKO
       satellite   - prize is a seat
       team        - tag team
       multiflight - more than one starting flight
       spend       - the sheet prices a subsequent buy-in
    """
    flights = [r for r in rows if "flight" in (r[10] or "")]
    flags = sheet.get("flags", []) if sheet else []
    reentry = (sheet.get("reentry") or "") if sheet else ""
    if any("RE-ENTRY INDICATED" in f for f in flags) or reentry.upper().startswith("IMPLIED"):
        return "spend", ("The official structure sheet prices a second buy-in, so more than one buy-in "
                         "per player is contemplated.")
    if len(flights) > 1 or (sheet and sheet.get("multi_flight")):
        return "multiflight", ("The event runs %d starting flights. Entering more than one flight is a second "
                               "buy-in; the sheet only bars a player who has bagged chips for Day 2 from playing "
                               "a later flight." % max(len(flights), 2))
    if any("SATELLITE" in f for f in flags):
        return "satellite", "The prize is direct entry into another event, not prize money."
    if any("TAG TEAM" in f for f in flags):
        return "team", "Two players share one entry and must alternate every level."
    if sheet and sheet.get("bounty"):
        return "bounty", ("Bounty format. The published guarantee includes bounty money, so the cash prize pool "
                          "is smaller than the headline number.")
    # A multi-day event is not a same-day single entry. `$800 ... (2DAY) ... MAIN EVENT` reaches this
    # line because the sheet prices no second buy-in and prints no bounty, and an earlier version
    # returned "candidate" here with the reason "One-day event" - a factual claim contradicted by the
    # event's own name. multi_flight is the group that already means "second day = second buy-in", so
    # a two-day event belongs there and its reason says why.
    sheet_start = str((sheet or {}).get("start") or "")
    name = " ".join((r[8] or "") for r in rows).upper()
    two_day = ("Day 2" in sheet_start or "Day 3" in sheet_start
               or any("Day 2" in f for f in flags)
               or any(t in name for t in ("(2DAY)", "(3DAY)", "2 DAY", "3 DAY")))
    if two_day:
        return "multiflight", ("The official structure sheet schedules Day 1 and Day 2 as separate days"
                               + (" (%s)" % sheet_start if sheet_start else "")
                               + ", so this is not a one-day event and cannot be played as a same-day "
                                 "single entry. Returning on Day 2 is a continuation of the same entry, "
                                 "not a second buy-in, but the trip does not get a free day back.")
    return "candidate", ("One-day event with a single starting day. The official structure sheet contains no "
                         "re-entry, rebuy or add-on clause.")


def demographic_gate(e):
    """The restriction text when the official sheet limits WHO may play (age 50+, women only,
    teams), else None.

    The standard property-wide "21+ with a Venetian Rewards card" requirement is not a
    restriction on an adult trip, so it is not a gate. This mirrors the test the root surface
    applies in scripts/build-schedule.py, so both surfaces answer "can I enter this?" the same way.
    """
    el = e.get("eligibility") or ""
    if "50+" in el or "female" in el.lower() or el.startswith("Teams"):
        return el
    return None


GROUP_LABEL = {
    "candidate": "Best single-entry candidates",
    "bounty": "Bounty / PKO (separate group)",
    "satellite": "Satellites (prize is a seat)",
    "team": "Team events",
    "multiflight": "Multi-flight (second flight = second buy-in)",
    "spend": "Spend-to-advantage (sheet prices a second buy-in)",
}


def build_events():
    by_event = {}
    for r in sched.ROWS:
        by_event.setdefault(r[2], []).append(r)
    events = []
    for ev_no in sorted(by_event):
        rows = sorted(by_event[ev_no], key=lambda r: tminutes(r[3]) or 0)
        sheet = sheet_for_event(ev_no)
        group, reason = classify(ev_no, rows, sheet)
        entry_rows = [r for r in rows if "restart" not in (r[10] or "")]
        starts = sorted({r[3] for r in entry_rows})
        # A multi-flight event prints one schedule row per flight, each titled "... 1A", "... 1B".
        # The tournament table shows one row per event, so the flight suffix is stripped from the
        # displayed title and the flight list is carried separately.
        flights = []
        for r in entry_rows:
            fm = re.search(r"\b1([A-Z])\b", r[8])
            if fm:
                flights.append(fm.group(1))
        base = entry_rows[0][8] if entry_rows else rows[0][8]
        if len(flights) > 1:
            # strip the flight token wherever it sits in the official title
            base = re.sub(r"\s+", " ", re.sub(r"\s+1[A-Z](?=\s|$)", " ", base)).strip() or base
            flights = sorted(flights)
        gtds = sorted({r[5] for r in entry_rows if r[5]})
        # per-event guarantee: resolved against the event number the sheet prints
        gtd, gtd_note = guarantee_for_event(sheet, ev_no)
        if gtd is None and len(gtds) == 1:
            gtd = gtd_value(gtds[0])
            if gtd is not None:
                gtd_note = "from the schedule row, not the structure sheet"
        buy_in = sheet.get("buy_in") if sheet else None
        events.append(dict(
            event_no=ev_no,
            name=base,
            flights=flights,
            official_name=rows[0][8],
            group=group,
            group_label=GROUP_LABEL[group],
            reason=reason,
            dates=sorted({r[0] for r in entry_rows}),
            all_dates=[r[0] for r in rows],
            starts=starts,
            first_date=min(r[0] for r in (entry_rows or rows)),
            single_entry_confirmed=False,  # No reviewed DSE IV rule expressly meets the policy.
            sheet_urls=sorted({SHEETS[r[9]]["url"] for r in rows if r[9] in SHEETS}),
            sheet_retrieved=(decisions.READ if sheet and sheet["sheet"] in decisions.VENETIAN_SHEETS_REREAD
                             else sheet.get("retrieved", RETRIEVED) if sheet else None),
            schedule_url=sched.SCHEDULE_URL,
            entry_slots=[(r[0], r[3]) for r in sorted(entry_rows, key=lambda r: (r[0], tminutes(r[3]) or 0))],
            reg_close=entry_rows[0][4] if entry_rows and entry_rows[0][4] else "",
            chips=entry_rows[0][6] if entry_rows else None,
            level=entry_rows[0][7] if entry_rows else "",
            buy_in=buy_in,
            fee=sheet.get("fee") if sheet else None,
            pool_per_entry=sheet.get("pool_per_entry") if sheet else None,
            fee_quote=(sheet.get("fee_quote") if sheet else None),
            gtd=gtd,
            gtd_note=(gtd_note or None),
            gtd_text=(sheet.get("guarantee") if sheet else (gtds[0] if len(gtds) == 1 else None)),
            ratio=round(gtd / buy_in, 1) if (gtd and buy_in and not demographic_gate(dict(eligibility=sheet.get("eligibility"))) and group not in ("satellite", "team") and sheet.get("fee") is not None) else None,
            bounty=(sheet.get("bounty") if sheet else None),
            bounty_flag=None,
            reentry=(sheet.get("reentry") if sheet else "not read"),
            addon=(sheet.get("addon") if sheet else "not read"),
            rebuy=(sheet.get("rebuy") if sheet else "not read"),
            flight_rule=(sheet.get("flight_rule") if sheet else None),
            eligibility=(sheet.get("eligibility") if sheet else None),
            late_reg=(sheet.get("late_reg") if sheet else None),
            payout_pct=(sheet.get("payout_pct") if sheet else None),
            sheet_no=(sheet.get("sheet") if sheet else None),
            sheet_url=(sheet.get("url") if sheet else None),
            sheet_title=(sheet.get("title") if sheet else None),
            sheet_notes=(sheet.get("notes") if sheet else None),
            sheet_flags=(sheet.get("flags") if sheet else []),
            rows=rows,
            entry_row_count=len(entry_rows),
            restart_count=len(rows) - len(entry_rows),
        ))
    return events


# Groups that a "primary event of the day" must not come from when anything else is running.
# A satellite's prize is a seat, not money; a tag team needs two players; a multi-flight row is
# one starting flight of a longer event and its guarantee belongs to the whole event.
NOT_A_PRIMARY = ("satellite", "team", "multiflight")

# How desirable a group is as the day's main event. Lower is better.
GROUP_TIER = {"candidate": 0, "bounty": 1, "multiflight": 2, "spend": 3, "satellite": 4, "team": 5}


def _selection_rank(x):
    """Order candidate primaries: unrestricted first, then by group, then by money at stake."""
    restricted = 1 if demographic_gate(x) else 0
    tier = GROUP_TIER.get(x["group"], 3)
    # earlier start breaks a tie within a tier, then the bigger guarantee, then the event number
    return (restricted, tier, x["start_m"] or 0, -(x.get("gtd") or 0), x["event_no"])


def choose_primary(entries):
    """Pick the day's main event: the best event a player can actually buy into.

    The previous rule simply took the earliest start, which made a $260 satellite the primary
    event of 12 December instead of the $2,200 $1M-guarantee PokerAtlas title event starting 17
    minutes later. Eligibility-restricted events (Seniors, Ladies) are never promoted, and
    satellites / tag teams / multi-flight rows only become the primary when nothing else runs.
    """
    if not entries:
        return None
    open_to_all = [x for x in entries if not demographic_gate(x)]
    pool = open_to_all or entries
    ranked = sorted(pool, key=_selection_rank)
    # prefer a start the player can reach first, but never at the cost of the tier
    best = ranked[0]
    if best["group"] in NOT_A_PRIMARY:
        better = [x for x in pool if x["group"] not in NOT_A_PRIMARY]
        if better:
            best = sorted(better, key=_selection_rank)[0]
    return best


def build_days(events):
    """One entry per day: primary + conditional fallback, with overlap flags."""
    days = {}
    for ev in events:
        for r in ev["rows"]:
            if "restart" in (r[10] or ""):
                continue
            d = r[0]
            days.setdefault(d, []).append(dict(
                event_no=ev["event_no"], name=ev["name"], group=ev["group"],
                # the official schedule prints one row per flight, and the flight letter lives in
                # the row title ("$300 NO LIMIT HOLD'EM 1A"). Collapsing to the event name would
                # print the same flight twice on a day that runs 1A and 1B.
                label=r[8], flight=r[10] or "", row_gtd=r[5] or "",
                start=r[3], start_m=tminutes(r[3]), reg_close=r[4],
                reg_close_m=tminutes(r[4]) if r[4] else None,
                buy_in=ev["buy_in"], gtd=ev["gtd"], sheet_url=SHEETS[r[9]]["url"] if r[9] in SHEETS else ev["sheet_url"],
                eligibility=ev.get("eligibility"),
                date=d, dow=r[1],
            ))
            # restarts occupy the same day too
        for r in ev["rows"]:
            if "restart" not in (r[10] or ""):
                continue
            days.setdefault(r[0], []).append(dict(
                event_no=ev["event_no"], name=ev["name"], group=ev["group"],
                label=r[8], flight=r[10] or "", row_gtd="",
                start=r[3], start_m=tminutes(r[3]), reg_close="", reg_close_m=None,
                buy_in=None, gtd=None, sheet_url=SHEETS[r[9]]["url"] if r[9] in SHEETS else ev["sheet_url"],
                date=r[0], dow=r[1], restart=True,
            ))
    out = []
    for d in sorted(days):
        entries = sorted([x for x in days[d] if not x.get("restart")], key=lambda x: x["start_m"] or 0)
        restarts = sorted([x for x in days[d] if x.get("restart")], key=lambda x: x["start_m"] or 0)
        primary = choose_primary(entries)
        fallbacks = []
        for f in entries:
            if primary is not None and f is primary:
                continue
            if primary is not None and f["event_no"] == primary["event_no"] and f["start"] == primary["start"]:
                continue
            if primary and f["event_no"] == primary["event_no"]:
                note = "Another flight of the same event; not a single-entry fallback."
                verdict = "excluded: second flight"
            elif demographic_gate(f) or f["group"] != "candidate":
                note = "Separate format or eligibility restriction; not an option on a strict itinerary."
                verdict = "separate / restricted"
            elif primary and f["reg_close_m"] and f["reg_close_m"] > primary["start_m"]:
                note = ("Conditional: only if you are out of #%d %s before #%d %s's registration "
                        "closes at %s (official)."
                        % (primary["event_no"], entry_title(primary),
                           f["event_no"], entry_title(f), f["reg_close"]))
                verdict = "conditional fallback"
            elif primary and f["reg_close_m"]:
                note = ("Registration for #%d %s closes at %s, before #%d %s even starts at %s. "
                        "You cannot start both."
                        % (f["event_no"], entry_title(f), f["reg_close"],
                           primary["event_no"], entry_title(primary), primary["start"]))
                verdict = "cannot be sequenced"
            else:
                note = "No official registration close published for #%d %s." % (
                    f["event_no"], entry_title(f))
                verdict = "unknown"
            fallbacks.append(dict(item=f, note=note, verdict=verdict))
        # Events a player who meets the condition could play, which are never promoted to primary
        # because they are restricted. Shown explicitly so an age-restricted morning event is not
        # silently dropped from the day.
        restricted_alts = [x for x in entries if demographic_gate(x)
                           and (primary is None or x["event_no"] != primary["event_no"])]
        out.append(dict(date=d, dow=entries[0]["dow"] if entries else (restarts[0]["dow"] if restarts else ""),
                        entries=entries, restarts=restarts, primary=primary, fallbacks=fallbacks,
                        restricted_alternatives=restricted_alts,
                        overlap=len(entries) > 1))
    return out


# --------------------------------------------------------------------------------------
# html helpers
# --------------------------------------------------------------------------------------

NAV = [
    ("index.html", "Dashboard"),
    ("tournaments.html", "Tournaments"),
    ("entry-rules.html", "Entry rules"),
    ("schedule.html", "Day plan"),
    ("hotels.html", "Hotels \u0026amp; true cost"),
    ("walking.html", "Walking times"),
    ("trip.html", "Trip cost"),
    ("venues.html", "Venues"),
    ("summary.html", "Executive summary"),
    ("questions.html", "Questions"),
    ("suggestions.html", "Suggestions"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources"),
    ("repo-review.html", "Repo review"),
]

SUBNAV = {
    "venues.html": [("venues/venetian.html", "The Venetian"), ("venues/other.html", "Other rooms")],
}

# Sub-navigation for pages that live in 2026/venues/. Authored relative to that directory.
VENUE_SUBNAV = [("venetian.html", "The Venetian"), ("wynn.html", "Wynn / Encore"),
                ("horseshoe.html", "Horseshoe"), ("caesars-palace.html", "Caesars Palace"),
                ("bellagio.html", "Bellagio"), ("mgm-grand.html", "MGM Grand"),
                ("other.html", "Other rooms")]

# Human labels for the site-wide search results, keyed by page path.
PAGE_LABEL = dict(NAV)
PAGE_LABEL.update({
    "venues/venetian.html": "The Venetian \u2014 events",
    "venues/other.html": "Other rooms",
})

CSS = """
:root{--bg:#0f1115;--panel:#161a22;--panel2:#1c2230;--line:#2a3242;--fg:#e7ecf3;--dim:#9aa7bb;
--accent:#5eead4;--warn:#fbbf24;--bad:#fb7185;--good:#4ade80;--link:#7dd3fc;}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--link)}
a:visited{color:#a5b4fc}
h1,h2,h3{line-height:1.25;margin:0 0 .5rem}
h1{font-size:1.7rem}h2{font-size:1.25rem;margin-top:0}h3{font-size:1.05rem}
p{margin:.5rem 0}
code,.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:.85em}
.wrap{max-width:1400px;margin:0 auto;padding:0 18px}
header.top{background:linear-gradient(180deg,#141a26,#0f1115);border-bottom:1px solid var(--line);
position:sticky;top:0;z-index:50}
header.top .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:14px;padding-top:10px;padding-bottom:10px}
.brand{font-weight:700;font-size:1.05rem;color:var(--fg);text-decoration:none;white-space:nowrap}
.brand span{color:var(--accent)}
nav.main{display:flex;flex-wrap:wrap;gap:2px;margin-left:auto}
nav.main a{color:var(--dim);text-decoration:none;padding:5px 9px;border-radius:6px;font-size:.86rem}
nav.main a:hover{background:var(--panel2);color:var(--fg)}
nav.main a.on{background:var(--panel2);color:var(--accent)}
main{padding:22px 0 60px}
.hero{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:18px}
.hero h1{margin-bottom:.35rem}
.lede{color:var(--dim);max-width:95ch}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:16px 0 22px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:13px 15px}
.card .k{font-size:.78rem;color:var(--dim);text-transform:uppercase;letter-spacing:.04em}
.card .v{font-size:1.65rem;font-weight:700;margin-top:2px}
.card .s{font-size:.8rem;color:var(--dim);margin-top:2px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin-bottom:18px}
.panel>h2{margin-bottom:.7rem}
table{width:100%;border-collapse:collapse;font-size:.86rem}
th,td{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}
th{background:var(--panel2);position:sticky;top:46px;z-index:10;font-size:.78rem;text-transform:uppercase;
letter-spacing:.03em;color:var(--dim);cursor:pointer;user-select:none;white-space:nowrap}
th:hover{color:var(--fg)}
td.num,th.num{text-align:right;white-space:nowrap}
tbody tr:hover{background:#141a24}
.slot{display:block}.slot[hidden]{display:none}
.tbl-scroll{overflow:auto;max-height:76vh;border:1px solid var(--line);border-radius:10px}
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin-bottom:12px}
.controls label{display:flex;flex-direction:column;gap:3px;font-size:.76rem;color:var(--dim);
text-transform:uppercase;letter-spacing:.03em}
.controls input,.controls select{background:var(--panel2);color:var(--fg);border:1px solid var(--line);
border-radius:7px;padding:7px 9px;font:inherit;font-size:.9rem;min-width:120px}
.controls input[type=text]{min-width:230px}
.controls .chk{flex-direction:row;align-items:center;gap:7px;text-transform:none;font-size:.88rem;
color:var(--fg);letter-spacing:0}
.controls .chk input{width:16px;height:16px;min-width:0}
button.btn{background:var(--panel2);color:var(--fg);border:1px solid var(--line);border-radius:7px;
padding:8px 13px;font:inherit;font-size:.88rem;cursor:pointer}
button.btn:hover{border-color:var(--accent);color:var(--accent)}
.tag{display:inline-block;padding:1px 7px;border-radius:99px;font-size:.72rem;font-weight:600;
border:1px solid transparent;white-space:nowrap}
.t-candidate{background:rgba(74,222,128,.14);color:#86efac;border-color:rgba(74,222,128,.35)}
.t-bounty{background:rgba(251,191,36,.14);color:#fcd34d;border-color:rgba(251,191,36,.35)}
.t-satellite{background:rgba(125,211,252,.14);color:#7dd3fc;border-color:rgba(125,211,252,.35)}
.t-team{background:rgba(196,181,253,.14);color:#c4b5fd;border-color:rgba(196,181,253,.35)}
.t-multiflight{background:rgba(251,113,133,.14);color:#fda4af;border-color:rgba(251,113,133,.35)}
.t-spend{background:rgba(251,113,133,.22);color:#fecdd3;border-color:rgba(251,113,133,.5)}
.t-ok{background:rgba(74,222,128,.14);color:#86efac;border-color:rgba(74,222,128,.35)}
.t-warn{background:rgba(251,191,36,.14);color:#fcd34d;border-color:rgba(251,191,36,.35)}
.t-bad{background:rgba(251,113,133,.14);color:#fda4af;border-color:rgba(251,113,133,.35)}
.t-info{background:rgba(148,163,184,.14);color:#cbd5e1;border-color:rgba(148,163,184,.35)}
.blank{color:#6b7280;font-style:italic;font-size:.84rem}
.yes{color:var(--good);font-weight:600}
.no{color:var(--bad);font-weight:600}
.note{font-size:.82rem;color:var(--dim)}
.quote{border-left:3px solid var(--accent);padding:6px 12px;margin:8px 0;color:#cbd5e1;
background:#131924;border-radius:0 6px 6px 0;font-size:.86rem}
ul.tight{margin:.4rem 0;padding-left:1.1rem}
ul.tight li{margin:.2rem 0}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px}
.day{border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:var(--panel)}
.day h3{margin-bottom:.4rem}
.day .meta{font-size:.8rem;color:var(--dim);margin-bottom:.5rem}
.kv{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;font-size:.86rem}
.kv dt{color:var(--dim)}
.kv dd{margin:0}
footer{border-top:1px solid var(--line);padding:18px 0 40px;color:var(--dim);font-size:.82rem}
.pill-row{display:flex;flex-wrap:wrap;gap:6px;margin:.4rem 0}
.pill{border:1px solid var(--line);border-radius:99px;padding:3px 11px;font-size:.8rem;
background:var(--panel2);cursor:pointer;user-select:none}
.pill.on{background:var(--accent);color:#06231d;border-color:var(--accent);font-weight:600}
.calc{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;align-items:end}
.calc .out{background:#0b1018;border:1px solid var(--line);border-radius:8px;padding:11px 13px}
.calc .out .k{font-size:.74rem;color:var(--dim);text-transform:uppercase;letter-spacing:.04em}
.calc .out .v{font-size:1.35rem;font-weight:700;color:var(--accent)}
.small{font-size:.8rem;color:var(--dim)}
.src{font-size:.74rem;color:var(--dim);word-break:break-all}
tr.hidden{display:none}
.banner{border:1px solid var(--warn);background:rgba(251,191,36,.08);border-radius:10px;
padding:12px 15px;margin-bottom:16px;font-size:.9rem}
.banner.info{border-color:var(--link);background:rgba(125,211,252,.07)}
.chk-row{display:flex;gap:14px;align-items:center;margin:6px 0 10px;flex-wrap:wrap}
.gsbar{border-bottom:1px solid var(--line);background:var(--panel);padding:10px 0}
.gsbar .wrap2{max-width:1180px;margin:0 auto;padding:0 18px;display:grid;gap:6px;
grid-template-columns:auto 1fr auto}
.gs-label{font-size:.8rem;color:var(--dim);text-transform:uppercase;letter-spacing:.06em;align-self:center}
.gsbar input{padding:7px 10px;border-radius:8px;border:1px solid var(--line);background:var(--bg);color:var(--fg);
font:inherit;min-width:0}
.gsbar .note{margin:0;grid-column:1/-1}
#gs-res{grid-column:1/-1}
#gs-res:empty{display:none}
.gs-group{margin:8px 0 12px}
.gs-group h3{margin:0 0 4px}
.gs-group .note{display:block;margin:2px 0 0;font-size:.8rem}
@media(max-width:720px){th{position:static}.tbl-scroll{max-height:none}
.gsbar .wrap2{grid-template-columns:1fr auto}.gs-label{display:none}}
"""


def relink(text):
    """Prefix root-relative links with ../ so sub-directory pages resolve."""
    return re.sub(r'(href|src)="(?!https?:|#|mailto:|tel:|\.\./)([^"]+)"',
                  lambda m: '%s="../%s"' % (m.group(1), m.group(2)), text)


def page(title, body, active, extra_head="", subnav=None):
    nav = "".join(
        '<a href="%s"%s>%s</a>' % (h, ' class="on"' if h == active else "", lab)
        for h, lab in NAV)
    sub = ""
    if subnav:
        sub = '<div class="pill-row" style="margin-bottom:12px">' + "".join(
            '<a class="pill" href="%s">%s</a>' % (h, lab) for h, lab in subnav) + "</div>"
    title = html.escape(title).replace("&amp;#", "&#")
    out = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s &middot; Las Vegas Single-Entry Poker Trip Planner</title>
<link rel="stylesheet" href="%sassets/site2026.css">
<script src="%sassets/search-index.js" defer></script>
<script src="%sassets/site2026.js" defer></script>
%s
</head><body>
<header class="top"><div class="wrap">
<a class="brand" href="index.html">Vegas <span>Single-Entry</span> Poker Planner</a>
<nav class="main">%s<a class="xlink" href="../index.html">Root dashboard</a></nav>
<div class="gsbar"><div class="wrap2">
<label class="gs-label" for="gs">Search every table</label>
<input type="text" id="gs" autocomplete="off" placeholder="event, hotel, price, rule, question&hellip;">
<button class="btn" id="gs-clear" type="button">Clear</button>
<p class="note" id="gs-status">Loading the site-wide index&hellip;</p>
<div id="gs-res"></div>
</div></div>
</div></header>
<main class="wrap">
%s
%s
</main>
<footer><div class="wrap">
<p><strong>Data policy.</strong> Every value on this site is transcribed from an official venue
document that was read and is linked on every row. A value the organiser does not publish is left
empty and listed on <a href="flagged.html">Flagged for review</a>. Nothing is inferred, estimated or
filled in from memory. Sources retrieved %s.</p>
<p class="small">This is a research tool, not a booking service. Re-confirm every official page
before you pay anything non-refundable. This <code>/2026/</code> surface is generated by
<code>scripts/build2026.py</code>; the site root hosts the older multi-venue dashboard, and the two
do not share a generator.</p>
</div></footer>
</body></html>
""" % (title, "", "", "", extra_head, nav, sub, body, RETRIEVED)
    if depth_prefix(active):
        # subnav links are already written relative to the venue directory; protect them from the
        # root-relative prefixing pass by marking them before it runs.
        if sub:
            out = out.replace(sub, "@@SUBNAV@@")
        out = relink(out)
        if sub:
            out = out.replace("@@SUBNAV@@", sub)

    return out


def depth_prefix(active):
    return "../" if active.startswith("venues/") else ""


def entry_title(x):
    """Official schedule row title, de-duplicated against the collapsed event name."""
    return (x.get("label") or x["name"]).strip()


def gtd_cell(e):
    """Guarantee as printed, but never the wording of a sheet that covers several events.

    Some structure sheets serve more than one event number and print the guarantee as
    '30000 FOR EVENT #14 AND #63; 40000 FOR EVENT #28'. That wording belongs to the sheet, not
    to this row, so the row shows the guarantee parsed for this event number instead.
    """
    t = (e.get("gtd_text") or "").strip()
    if t:
        # '30000 (#16) 40000 (#30) 50000 (#54) - PRIZE POOL + TOTAL BOUNTIES': one sheet, three
        # events. Show the figure printed against this event number, never all three.
        per_event = re.findall(r"([\d,]{3,})\s*\(#(\d+)\)", t)
        if per_event:
            for val, no in per_event:
                if int(no) == e["event_no"]:
                    return "$" + format(int(val.replace(",", "")), ",")
            return '<span class="blank">see sheet</span>'
        if "EVENT #" in t.upper():
            t = ""      # sheet-wide wording, not this row's figure
        else:
            m = re.match(r"^\$?([\d,]+)\s*\((.+)\)$", t)
            if m:
                return ("$" + format(int(m.group(1).replace(",", "")), ",")
                        + " <span class='note'>(%s)</span>" % esc(m.group(2).lower()))
            return money(t)
    if e.get("gtd"):
        cell = "$" + format(e["gtd"], ",")
        if e.get("gtd_note"):
            cell += " <span class='note'>%s</span>" % esc(e["gtd_note"])
        return cell
    if e.get("gtd_note"):
        return '<span class="blank">none published</span> <span class="note">%s</span>' % esc(e["gtd_note"])
    return '<span class="blank">none published</span>'


def esc(s):
    return html.escape(str(s)) if s is not None else ""


def check_badge(*urls):
    """Inline status of the scheduled re-check for the document(s) a row rests on.

    The monitor never rewrites a value: it reports that the official document moved, so the
    row is marked and a human re-reads it. A row whose document could not be fetched is marked
    differently from a row whose document is unchanged.
    """
    if CHECKS_META is None:
        return "<span class='note' title='The scheduled re-check has not run against this checkout yet'>not yet checked</span>"
    hits = [CHECKS[u] for u in urls if u in CHECKS]
    if not hits:
        return "<span class='note'>document not in the monitor</span>"
    if row_changed(*urls):
        return "<span class='tag t-bad' title='A cited document changed since transcription; compare published fields before relying on it'>source changed · re-read</span>"
    errs = [h for h in hits if h.get("change") == "fetch error"]
    if errs:
        # Say which kind of failure it was: a property that refuses a datacenter runner is not a
        # source that moved, and neither of them is a source that has been checked. Several of
        # these pages load normally in a browser, so a fetch error is a gap in the monitor, not
        # evidence the document changed. Flag X-08.
        kinds = sorted({h.get("error_kind") for h in errs if h.get("error_kind")})
        lab = ("monitor could not read it: " + ", ".join(kinds)) if kinds else "fetch error"
        return ("<span class='tag t-warn' title='The scheduled re-check could not open this document, "
                "so nothing about it is proven for this run. That is a gap in the monitor, not "
                "evidence the page changed - several of these pages load normally in a browser. See "
                "flag X-08. The value keeps its own last verified date.'>%s</span>" % esc(lab))
    if any(h.get("change") == "first check" for h in hits):
        baselined = all(h.get("change") == "first check" for h in hits)
        return "<span class='tag t-info'>%s</span>" % ("baseline set" if baselined else "some baselines new")
    if any(u and u not in CHECKS for u in urls):
        return "<span class='tag t-warn'>some sources not checked in latest run</span>"
    return "<span class='tag t-ok'>unchanged</span>"


def row_changed(*urls):
    """Keep a change visible when a subsequent run merely sees the same new bytes."""
    return any(CHECKS.get(u, {}).get("change") == "CHANGED"
               or (CHECKS.get(u, {}).get("last_changed") or "")[:10] >= RETRIEVED
               for u in urls)


def srclink(url, label=None):
    if not url:
        return '<span class="blank">no source</span>'
    # a repository-relative citation (no scheme) is shown as code, never as a link
    if not url.startswith(("http://", "https://")):
        return '<code>%s</code>' % esc(url)
    host = re.sub(r"^https?://", "", url).split("/")[0]
    ok = host in OFFICIAL_HOSTS
    lab = label or (host + ("&#8203;" if len(host) > 24 else ""))
    return ('<a class="src" href="%s" target="_blank" rel="noopener"%s>%s</a>'
            % (url, "" if ok else ' style="color:#fb7185"', lab))


def num(v, dash=True):
    if v is None:
        return '<span class="blank">&mdash;</span>' if dash else ""
    if isinstance(v, (int, float)) and abs(v) >= 1000:
        return format(int(v), ",")
    return str(v)


# --------------------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------------------

def p_index(events, days):
    cands = [e for e in events if e["group"] == "candidate"]
    # Only events anyone on the trip can enter are ranked. A 50+ or women-only event is a real
    # event with a real guarantee, but ranking it first for a traveller who cannot enter it is
    # not decision support - it is a wrong answer with a source link. They are listed separately.
    restricted = [e for e in cands if demographic_gate(e)]
    cands_open = [e for e in cands if not demographic_gate(e)]
    upcoming = [e for e in cands_open if any(day >= decisions.READ for day in e["dates"])]
    ranked = [e for e in upcoming if e["ratio"]]
    ranked.sort(key=lambda e: -e["ratio"])
    cheapest = sorted([e for e in upcoming if e["buy_in"]], key=lambda e: e["buy_in"])[:5]
    cards = [
        ("Events in the series", len(events), "Venetian DeepStack Extravaganza IV, Nov 16 &ndash; Dec 23 2026"),
        ("Scheduled rows", len(sched.ROWS), "including 12 Day&nbsp;2 / Day&nbsp;3 restarts"),
        ("Structure sheets read", len(SHEETS), "all 37, every one read on %s" % RETRIEVED),
        ("Confirmed single-entry", 0, "no official sheet states a one-entry rule &mdash; see F-01"),
        ("Best candidates", len(cands), "%d open to any player, %d restricted by age/field; one-day, "
         "no bounty, no re-entry/add-on clause printed" % (len(cands_open), len(restricted))),
        ("Poker suite rate", "from&nbsp;$119", "code EPOKR25, phone only &mdash; see hotels"),
    ]
    cardhtml = "".join(
        '<div class="card"><div class="k">%s</div><div class="v">%s</div><div class="s">%s</div></div>'
        % (k, v, s) for k, v, s in cards)

    if restricted:
        rrows = "".join(
            "<tr><td class='num'>%d</td><td><a href='tournaments.html#ev%d'>%s</a><br>%s</td>"
            "<td class='num'>$%s</td><td class='num'>%s</td><td>%s</td></tr>"
            % (i + 1, e["event_no"], esc(e["name"][:64]), srclink(e["sheet_url"], "Structure sheet"), format(e["buy_in"], ","),
               esc(e.get("gtd_text") or ("$%s" % format(e["gtd"], ",") if e.get("gtd") else "&mdash;")),
               esc(demographic_gate(e)))
            for i, e in enumerate(sorted(restricted, key=lambda x: -(x["ratio"] or 0))))
        restricted_html = (
            "<div class=\"panel\"><h2>Restricted research leads &mdash; events you may not be "
            "able to play</h2>\n<p class=\"note\">These events are not confirmed freezeouts, and the "
            "official structure sheet restricts who may enter. They are listed here, with the sheet's own "
            "wording, instead of being ranked against open events.</p><div class=\"tbl-scroll\"><table>"
            "<thead><tr><th class=\"num\">#</th><th>Event</th><th class=\"num\">Entry</th>"
            "<th class=\"num\">Guarantee</th><th>Restriction (official sheet)</th></tr></thead><tbody>"
            + rrows + "</tbody></table></div></div>")
    else:
        restricted_html = ""
    top = "".join(
        "<tr><td class='num'>%d</td><td><a href='tournaments.html#ev%d'>%s</a><br>%s</td>"
        "<td class='num'>$%s</td><td class='num'>%s</td><td class='num'>%s</td>"
        "<td class='num'>%s</td><td>%s</td></tr>"
        % (i + 1, e["event_no"], esc(e["name"][:64]), srclink(e["sheet_url"], "Structure sheet"), format(e["buy_in"], ","),
           gtd_cell(e),
           "$" + format(e["fee"], ",") if e["fee"] else "&mdash;",
           "%.1f&times;" % e["ratio"] if e["ratio"] else "&mdash;",
           ", ".join("<span class='note'>%s</span>" % d[5:] for d in e["dates"]))
        for i, e in enumerate(ranked[:12]))

    cheap = "".join(
        "<tr><td class='num'>%d</td><td><a href='tournaments.html#ev%d'>%s</a><br>%s</td>"
        "<td class='num'>$%s</td><td>%s</td></tr>"
        % (i + 1, e["event_no"], esc(e["name"][:64]), srclink(e["sheet_url"], "Structure sheet"), format(e["buy_in"], ","),
           ", ".join("<span class='note'>%s</span>" % d[5:] for d in e["dates"]))
        for i, e in enumerate(cheapest))

    body = """
<div class="hero">
<h1>Las Vegas single-entry poker trip planner</h1>
<p class="lede">Event and hotel findings cite the venue or regulator. Walks are separately labelled route estimates,
and a blank checkout field means no verified quote.</p>
<p class="lede"><strong>No reviewed Venetian event is confirmed as single-entry.</strong>
All 37 official Venetian DeepStack Extravaganza IV structure sheets were read on %(ret)s. Not one
contains a one-entry-only clause. What they do let you do is separate the events whose sheet is silent
on re-entry, rebuy and add-on from the ones that expressly price a second buy-in, run multiple
flights, award bounties, or pay out in seats.</p>
</div>
<div class="cards">%(cards)s</div>

<div class="banner"><strong>Booking verdict: hold.</strong> No confirmed freezeout, no comparable hotel checkout
quote, and no verified 8 AM start. <a href="summary.html">Executive summary</a> &middot;
<a href="flagged.html">Flagged for review</a>.</div>
<div class="banner info"><strong>Start here.</strong>
<a href="tournaments.html">Tournaments</a> ranks the events.
<a href="entry-rules.html">Entry rules</a> shows the exact wording each classification rests on.
<a href="schedule.html">Day plan</a> gives every day one primary event plus a conditional fallback.
<a href="hotels.html">Hotels</a> computes the true nightly cost.
<a href="questions.html">Questions</a> lists what still has to be answered before a decision.</div>

<div class="grid2">
<div class="panel"><h2>Research shortlist by published ratio</h2>
<p class="note">Entry dates on or after Nov 19, 2026. Open to any player aged 21+ only. %(nres)d candidate event(s) are restricted by the
official sheet (age 50+ or women-only) and are listed at the foot of this page rather than ranked
against events you can actually enter.</p>
<p class="note">Guarantee &divide; total entry fee, shown only where both figures are printed on the
official documents. This is a <strong>descriptive ratio, not a forecast</strong> &mdash; a guarantee is
a floor the room commits to, not a predicted pool. Bounty, multi-flight, satellite and team events are
excluded from this table on purpose: their guarantees are not like-for-like.</p>
<div class="tbl-scroll"><table><thead><tr>
<th>#</th><th>Event</th><th class="num">Entry</th><th class="num">Guarantee</th>
<th class="num">House fee</th><th class="num">GTD&divide;entry</th><th>Dates</th>
</tr></thead><tbody>%(top)s</tbody></table></div>
<p class="note"><a href="tournaments.html">Browse event evidence &rarr;</a></p>
</div>

<div class="panel"><h2>Lowest entry prices among research leads</h2>
<p class="note">Lowest total entry fee among research leads with entry dates on or after Nov 19, 2026. Cheap is not the same as good value
&mdash; read it next to the guarantee column on the left.</p>
<div class="tbl-scroll"><table><thead><tr>
<th>#</th><th>Event</th><th class="num">Entry</th><th>Dates</th>
</tr></thead><tbody>%(cheap)s</tbody></table></div>
<p class="note"><a href="trip.html">Estimate the cost of a whole trip &rarr;</a></p>
</div>
</div>
%(restricted_html)s

<div class="panel"><h2>What is on this site</h2>
<div class="grid2">
<div>
<h3>Tournaments</h3>
<ul class="tight">
<li><a href="tournaments.html">Tournaments</a> &mdash; all %(n)s events, searchable, with a date filter
and a single-entry toggle.</li>
<li><a href="entry-rules.html">Entry rules</a> &mdash; single-entry, re-entry, add-on and fee fields
stored separately, each with its source excerpt and retrieval date.</li>
<li><a href="schedule.html">Day plan</a> &mdash; one primary event per day plus a conditional fallback,
with overlap flags built from official start times and registration closes.</li>
</ul>
</div>
<div>
<h3>Stay and cost</h3>
<ul class="tight">
<li><a href="hotels.html">Hotels</a> &mdash; resort fees, tax, parking and a dated rate log, plus a
true-cost-per-night calculator.</li>
<li><a href="walking.html">Walking times</a> &mdash; every hotel &times; poker-room pair with a
30-minute filter and a Google Maps link per row.</li>
<li><a href="trip.html">Trip cost</a> &mdash; entries &times; buy-ins + nights &times; true nightly cost.</li>
</ul>
</div>
<div>
<h3>Decide</h3>
<ul class="tight">
<li><a href="summary.html">Executive summary</a> &mdash; the important details on one page.</li>
<li><a href="questions.html">Questions</a> &mdash; what must be answered before any decision.</li>
<li><a href="suggestions.html">Suggestions</a> &mdash; options to choose between before anything changes.</li>
</ul>
</div>
<div>
<h3>Verify</h3>
<ul class="tight">
<li><a href="flagged.html">Flagged for review</a> &mdash; every unverified value and irregularity.</li>
<li><a href="sources.html">Sources</a> &mdash; the source register and the scheduled re-check.</li>
<li><a href="repo-review.html">Repo review</a> &mdash; what the repository contains, line by line.</li>
</ul>
</div>
</div></div>
""" % dict(ret=RETRIEVED, cards=cardhtml, top=top, cheap=cheap, n=len(events),
                  nres=len(restricted), restricted_html=restricted_html)
    return page("Dashboard", body, "index.html")


def p_tournaments(events):
    dates = sorted({d for e in events for d in e["dates"]})
    rowshtml = []
    for e in events:
        gtdcell = gtd_cell(e)
        rowshtml.append(
            '<tr id="ev%(no)d" data-group="%(g)s" data-dates="%(dates)s" '
            'data-confirmed="%(confirmed)s" data-buyin="%(raw_bi)s" data-gtd="%(gtdv)s" data-changed="%(chg)s" data-search="%(search)s">'
            "<td class='num'>%(no)d</td>"
            "<td><span class='tag t-%(g)s'>%(gl)s</span></td>"
            "<td><strong>%(name)s</strong><div class='note'>%(meta)s</div></td>"
            "<td>%(datesc)s</td>"
            "<td>%(starts)s</td>"
            "<td class='num'>$%(bi)s</td>"
            "<td class='num'>%(fee)s</td>"
            "<td class='num'>%(pool)s</td>"
            "<td class='num'>%(gtd)s</td>"
            "<td class='num'>%(ratio)s</td>"
            "<td>%(sheet)s</td>"
            "<td class='num'>%(checked)s</td>"
            "<td>%(recheck)s</td>"
            "</tr>" % dict(
                no=e["event_no"], g=e["group"],
                gl=esc(e["group_label"].split(" (")[0]),
                dates=" ".join(e["dates"]),
                datesc="".join("<span class='note slot' data-slot-date='%s'>%s</span>" % (d, d) for d, _ in e["entry_slots"]),
                starts="".join("<span class='note slot' data-slot-date='%s'>%s</span>" % (d, esc(start)) for d, start in e["entry_slots"]),
                confirmed=int(e["single_entry_confirmed"]), raw_bi=e["buy_in"] or "",
                bi=format(e["buy_in"], ",") if e["buy_in"] else "&mdash;",
                fee="$" + format(e["fee"], ",") if e["fee"] else "&mdash;",
                pool="$" + format(e["pool_per_entry"], ",") if e["pool_per_entry"] else "&mdash;",
                gtd=gtdcell, gtdv=e["gtd"] or 0,
                ratio="%.1f&times;" % e["ratio"] if e["ratio"] else "&mdash;",
                sheet=" · ".join(srclink(url, "sheet " + url.rsplit("_", 1)[-1].split(".")[0]) for url in e["sheet_urls"])
                + "<br>" + srclink(sched.SCHEDULE_URL, "DSE IV schedule"),
                checked=e["sheet_retrieved"],
                recheck=check_badge(*e["sheet_urls"], sched.SCHEDULE_URL, sched.SCHEDULE_PDF),
                chg="1" if row_changed(*e["sheet_urls"], sched.SCHEDULE_URL, sched.SCHEDULE_PDF) else "0",
                name=esc(e["name"][:90]),
                meta=(("<span class='tag t-warn'>flights %s</span> " % ",".join(e["flights"]))
                      if e.get("flights") else "") + esc("; ".join(x for x in [
                    e["payout_pct"],
                    e["late_reg"] and ("late reg: " + e["late_reg"]),
                    (("21+ with a Venetian Rewards card (property rule) -- " + e["eligibility"])
                     if e["eligibility"] else None),
                ] if x)),
                search=esc((" ".join([e["name"], e["official_name"], str(e["event_no"]),
                                      e["group_label"]] + e.get("flights", []))).lower()),
            ))
    opts = "".join('<option value="%s">%s</option>' % (d, d) for d in dates)
    pills = "".join('<span class="pill" data-g="%s">%s</span>' % (k, esc(v.split(" (")[0]))
                    for k, v in GROUP_LABEL.items())
    return page("Tournaments", """
<div class="hero"><h1>Tournaments</h1>
<p class="lede">All %(n)s events in the Venetian DeepStack Extravaganza IV series (Nov 16 &ndash;
Dec 23, 2026), classified by what each official structure sheet actually says. Use the search box,
a range of Las Vegas dates, or the strict freezeout filter. <strong>No reviewed event currently
passes that filter.</strong> Use the candidates group to browse research leads, not confirmed freezeouts.</p></div>

<div class="panel">
<div class="controls">
<label>Search tournaments<input type="search" id="q" placeholder="event name, number, buy-in, date&hellip;"></label>
<label>From (Las Vegas)<input type="date" id="datef"></label>
<label>Through (inclusive)<input type="date" id="date-to"></label>
<label class="chk"><input type="checkbox" id="include-past"> Include past entry dates</label>
<label>Entry fee max<select id="maxbi">
<option value="">Any</option><option value="200">$200 and under</option>
<option value="300">$300 and under</option><option value="400">$400 and under</option>
<option value="600">$600 and under</option><option value="1100">$1,100 and under</option>
</select></label>
<label class="chk"><input type="checkbox" id="sef"> Single-entry / freezeout confirmed</label>
<label class="chk"><input type="checkbox" id="nogtd"> Has a published guarantee</label>
<button class="btn" id="reset">Reset</button>
</div>
<div class="pill-row">%(pills)s</div>
<p class="note" id="count"></p>
<p class="note"><strong>Source re-check</strong> is the scheduled monitor's verdict on the structure
sheet or series schedules cited for the row: <em>unchanged</em>, <em>source changed</em> (the official document
moved after transcription &mdash; re-read it before relying on the row), <em>fetch error</em>, or
<em>baseline set</em> on the monitor's first run. The monitor reports; it never rewrites a value.</p>
<div class="tbl-scroll"><table id="t"><thead><tr>
<th class="num">#</th><th>Group</th><th>Event</th><th>Dates</th><th>Starts</th>
<th class="num">Entry fee</th><th class="num">House fee</th><th class="num">To prize pool</th>
<th class="num">Guarantee</th><th class="num">GTD&divide;entry</th><th>Structure sheet</th>
<th class="num">Last checked</th><th>Source re-check</th>
</tr></thead><tbody>%(rows)s</tbody></table></div>
</div>

<div class="banner"><strong>How to read the ranking.</strong> Guarantee &divide; entry fee is shown
only where both numbers are printed on the official documents, and it is a descriptive ratio, not a
forecast: a guarantee is a floor the room commits to, not a predicted pool. Bounty and PKO events are
in their own group because their published guarantee includes bounty money, so the cash prize pool is
smaller than the headline figure. Multi-flight events are separate because entering a second flight is
a second buy-in. Satellites pay in seats, not cash.</div>
""" % dict(n=len(events), opts=opts, rows="".join(rowshtml), pills=pills), "tournaments.html")


def p_rules(events):
    def block(title, group, blurb):
        items = [e for e in events if e["group"] == group]
        if not items:
            return ""
        rows = []
        for e in sorted(items, key=lambda x: (x["buy_in"] or 0, x["event_no"])):
            rows.append(
                "<tr><td class='num'>%d</td><td>%s</td><td class='num'>$%s</td>"
                "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (e["event_no"], esc(e["name"][:60]),
                   format(e["buy_in"], ",") if e["buy_in"] else "&mdash;",
                   esc(e["reentry"]), esc(e["addon"]), esc(e["rebuy"]),
                   ("<div class='quote'>%s</div>" % esc(e["fee_quote"])) if e["fee_quote"] else "&mdash;",
                   srclink(e["sheet_url"], "sheet %s" % e["sheet_no"])))
        return ("<div class='panel'><h2>%s <span class='tag t-%s'>%d</span></h2><p class='note'>%s</p>"
                "<div class='tbl-scroll'><table><thead><tr><th class='num'>#</th><th>Event</th>"
                "<th class='num'>Entry</th><th>Re-entry clause</th><th>Add-on clause</th>"
                "<th>Rebuy clause</th><th>Official fee wording</th><th>Sheet</th></tr></thead>"
                "<tbody>%s</tbody></table></div></div>"
                % (esc(title), group, len(items), esc(blurb), "".join(rows)))

    body = """
<div class="hero"><h1>Entry rules, quoted</h1>
<p class="lede">Single-entry, re-entry, add-on and fee values are stored as separate fields for every
event, each with the sentence it was taken from and the date it was read. Nothing here is a summary of
what a sheet probably means. Where a sheet says nothing, that is recorded as silence &mdash; and
silence is not a prohibition.</p></div>

<div class="banner"><strong>The one thing to understand.</strong> All 37 official structure sheets were
read on %(ret)s. Not one contains a one-entry-only rule. So the best available evidence is a
<em>negative</em>: the sheet lists every mechanism the event uses, and re-entry, rebuy and add-on are
not among them. That is strong for a one-day event, and it is still not the same as the room promising
you cannot buy in twice. Flag <a href="flagged.html#F-01">F-01</a>.</div>
""" % dict(ret=RETRIEVED)

    body += block("Group A \u2014 best single-entry candidates", "candidate",
                  "Events with one starting day, no bounty, no satellite seat, no team format, and "
                  "no re-entry, rebuy or add-on clause printed anywhere on the official structure sheet.")
    body += block("Group B \u2014 bounty and progressive knock-out", "bounty",
                  "These do not let you buy extra chips, but the published guarantee includes bounty money, so "
                  "the cash prize pool is smaller than the headline number. Ranked separately on purpose.")
    body += block("Group C \u2014 multi-flight events", "multiflight",
                  "More than one starting flight. Entering a second flight costs a second buy-in. Every one of "
                  "these sheets carries the same sentence: any player who bags chips for Day 2 may not play a "
                  "subsequent flight. That blocks a player who has advanced \u2014 it does not block a player "
                  "who busted in flight A from buying into flight B.")
    body += block("Group D \u2014 satellites", "satellite",
                  "The prize is direct entry into another event, not prize money. Not comparable to a cash event.")
    body += block("Group E \u2014 team events", "team",
                  "Two players share one entry and must alternate every level, so a single player cannot play "
                  "the event alone.")
    body += block("Group F \u2014 spend-to-advantage", "spend",
                  "The official sheet prices a second buy-in, so more than one buy-in per player is "
                  "contemplated. These are the events the brief asks to keep in a separate section.")

    extras = [e for e in events if e["flight_rule"]]
    if extras:
        body += ("<div class='panel'><h2>The flight rule, verbatim</h2>"
                 "<p class='note'>Printed identically on every multi-flight sheet.</p>"
                 "<div class='quote'>%s</div>"
                 "<p class='note'>Source: %s</p></div>"
                 % (esc(extras[0]["flight_rule"]), srclink(extras[0]["sheet_url"])))
    return page("Entry rules", body, "entry-rules.html")


def p_schedule(days, events):
    blocks = []
    for d in days:
        dt_ = dt.date.fromisoformat(d["date"])
        head = dt_.strftime("%a %d %b %Y")
        prim = d["primary"]
        lines = []
        if prim:
            gtd = prim["gtd"] or prim.get("row_gtd") or ""
            gtd = ("$" + format(gtd, ",")) if isinstance(gtd, int) else gtd
            lines.append(
                "<div class='day'><h3>Research lead &mdash; #%d %s%s</h3>"
                "<div class='meta'>Start %s &middot; registration closes %s &middot; entry %s &middot; guarantee %s</div>"
                "<p class='note'>%s</p>%s</div>"
                % (prim["event_no"], esc(entry_title(prim)[:70]),
                   (" <span class='tag t-warn'>%s</span>" % esc(prim["flight"])) if prim["flight"] else "",
                   esc(prim["start"]),
                   esc(prim["reg_close"] or "not published"),
                   ("$" + format(prim["buy_in"], ",")) if prim["buy_in"] else "not published",
                   esc(gtd) if gtd else "none published",
                   esc(next(e["reason"] for e in events if e["event_no"] == prim["event_no"])),
                   srclink(prim["sheet_url"], "structure sheet")))
        else:
            lines.append("<div class='day'><h3>No new entries this day</h3></div>")
        for fb in d["fallbacks"]:
            it = fb["item"]
            cls = "t-bad" if fb["verdict"] == "cannot be sequenced" else "t-warn"
            lines.append(
                "<div class='day'><h3>Other scheduled entry &mdash; #%d %s <span class='tag %s'>%s</span></h3>"
                "<div class='meta'>Start %s &middot; registration closes %s &middot; entry %s</div>"
                "<p class='note'>%s %s</p></div>"
                % (it["event_no"], esc(entry_title(it)[:70]), cls, esc(fb["verdict"]), esc(it["start"]),
                   esc(it["reg_close"] or "not published"),
                   ("$" + format(it["buy_in"], ",")) if it["buy_in"] else "not published",
                   esc(fb["note"]), srclink(it["sheet_url"], "structure sheet")))
        if d.get("restricted_alternatives"):
            ra = "".join(
                "<p class='note'>#%d %s &mdash; starts %s, entry %s. <span class='tag t-warn'>not the "
                "primary</span> %s</p>"
                % (x["event_no"], esc(entry_title(x)[:64]), esc(x["start"]),
                   ("$" + format(x["buy_in"], ",")) if x["buy_in"] else "not published",
                   esc(demographic_gate(x) or ""))
                for x in d["restricted_alternatives"])
            lines.append("<div class='day'><h3>Also running &mdash; entry restricted</h3>%s"
                         "<p class='small'>Listed so the day is complete. It is never made the primary "
                         "because not every player can buy in.</p></div>" % ra)
        if d["restarts"]:
            rs = ", ".join("#%d %s &mdash; %s" % (x["event_no"], esc(entry_title(x)[:44]), x["start"])
                           for x in d["restarts"])
            lines.append("<div class='day'><h3>Continuations</h3><p class='note'>%s<br>"
                         "<span class='small'>A Day 2 / Day 3 restart costs nothing extra but occupies the "
                         "day. If you bagged chips, this is where you must be.</span></p></div>" % rs)
        flag = ('<span class="tag t-bad">%d starts &mdash; check timing</span>'
                % len(d["entries"])) if d["overlap"] else '<span class="tag t-ok">one scheduled start</span>'
        blocks.append(
            "<div class='panel' data-date='%s' data-multiple='%d'><h2>%s %s</h2>"
            "<div class='grid2'>%s</div></div>"
            % (d["date"], int(d["overlap"]), esc(head), flag, "".join(lines)))

    opts = "".join('<option value="%s">%s</option>' % (d["date"], d["date"]) for d in days)
    return page("Day plan", """
<div class="hero"><h1>Day plan</h1>
<p class="lede"><strong>No strict single-entry itinerary is confirmed.</strong> The research view shows one lead per day and
other starts separately. A conditional fallback is not a booking recommendation. The view never
claims you can play two events in sequence, because <strong>no official document publishes a finish
time</strong>. What is published is each event's start time and its registration close &mdash; and the
registration close is the real deadline: it is the latest moment you can still take your seat in the
later event.</p></div>

<div class="banner"><strong>How the primary is chosen.</strong> The primary is the day's best event
that <em>any</em> player can buy into, ranked: unrestricted one-day events first, then bounty events,
then multi-flight rows (which carry the day's biggest guarantees, such as the $1&nbsp;Million PokerAtlas
title event on 12 December), then rake-discount rows, and only then satellites and tag teams. Earlier
start breaks a tie, then the larger guarantee. Age- or gender-restricted events are never promoted, but
they are listed under <em>Also running</em> so an eligible player still sees them. Other entries are not planned buy-ins. A different unrestricted candidate can only be a fallback
if you are out before its registration closes and both entry rules have been confirmed;
where a fallback's registration closes before the primary starts, the pair is flagged <em>cannot be
sequenced</em>. Twelve rows in the official schedule are Day 2, Day 3 or streamed final tables; they are
listed as continuations, because you cannot buy into them.</div>

<div class="panel">
<div class="controls">
<label>Date<select id="df"><option value="">All dates</option>%(opts)s</select></label>
<label class="chk"><input type="checkbox" id="ov"> Only days with more than one entry</label>
</div>
<p class="note" id="c"></p>
</div>
%(blocks)s
""" % dict(opts=opts, blocks="".join(blocks)), "schedule.html")


def quote_panel():
    rows = []
    for q in decisions.QUOTE_LOG:
        cells = "".join("<td>%s</td>" % esc(q[field]) for field in
                        ("total", "nightly", "fee", "tax", "parking", "cancel", "rate_timestamp"))
        rows.append("<tr><th scope='row'>%s</th>%s<td>%s<br>%s<br>%s</td></tr>" % (
            esc(q["property"]), cells, esc(q["checked"]), esc(q["status"]), srclink(q["url"], "Open dates at hotel")))
    return """
<div class="panel" id="checkout-log"><h2>Same-stay checkout log</h2>
<p><strong>Comparison scenario, not a booking:</strong> November 25–28, 2026, one room, two adults, three nights.
Screen against a $200 all-in nightly cap and a private room with an en-suite bathroom. These are planning
assumptions, not confirmed preferences. No property can be ranked against the cap without comparable quotes.</p>
<div class="tbl-scroll"><table><thead><tr><th>Property</th><th>Checkout total</th><th>Nightly average</th>
<th>Mandatory resort fee</th><th>Tax</th><th>Parking</th><th>Cancellation deadline</th><th>Quote timestamp</th>
<th>Last checked / official lookup</th></tr></thead><tbody>%s</tbody></table></div>
</div>""" % "".join(rows)


def p_hotels():
    rows = []
    for h in hotelsmod.HOTELS:
        fee = ("$%d" % h["resort_fee"]) if h["resort_fee"] is not None else '<span class="blank">not published</span>'
        pr = ("from $%d" % h["poker_rate"]) if h["poker_rate"] else '<span class="blank">none published</span>'
        canc = ('<span class="blank">not published</span>' if not h.get("cancel")
                else esc(h["cancel"]) + "<div class='note'>%s</div>" % esc(h.get("cancel_type") or "")
                + ("<div class='note'>%s</div>" % (srclink(h["cancel_src"]) + " · " + esc(h.get("cancel_checked"))) if h.get("cancel_src") else ""))
        rows.append(
            "<tr><td><strong>%s</strong><div class='note'>%s</div></td>"
            "<td>%s<div class='note'>%s</div></td>"
            "<td class='num'>%s</td><td class='num'>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(h["name"]), esc(h["addr"]),
               fee, esc(h["resort_fee_note"] or ""),
               pr,
               '<span class="blank">not published</span>' if h.get("tax_pct") is None
               else ("%.2f%%" % h["tax_pct"] + ("<div class='note'>%s</div>" % srclink(h["tax_src"]) if h.get("tax_src") else "")),
               (esc(h["parking"]) + "<br>" + srclink(h["parking_src"], "Parking source") if h["parking"] else '<span class="blank">not published</span>'),
               canc,
               ('<span class="blank">not published</span>' if not h["dated_total"] else esc(h["dated_total"])),
               srclink(h["resort_fee_src"], "Fee source") + " · " + esc(h["resort_fee_checked"])
               + "<br>" + srclink(h["book"], "Official booking page") + "<br>"
               + check_badge(h["resort_fee_src"], h.get("tax_src"), h.get("parking_src"), h.get("cancel_src"))))

    # Occupancy and early-departure charges, which change the true cost per night and are usually
    # missed by a per-night comparison. Rendered only where the property publishes a figure.
    extra = []
    for h in hotelsmod.HOTELS:
        if not (h.get("extra_guest_fee") or h.get("early_checkout_fee")):
            continue
        extra.append(
            "<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td><td>%s · %s</td></tr>"
            % (esc(h["name"]),
               esc(h["extra_guest_fee"]) if h.get("extra_guest_fee") else '<span class="blank">not published</span>',
               esc(h["early_checkout_fee"]) if h.get("early_checkout_fee") else '<span class="blank">not published</span>',
               srclink(h["cancel_src"], "Hotel terms"), esc(h["cancel_checked"])))
    extra_html = ("<div class='panel'><h2>Occupancy and early-departure charges</h2>"
                  "<p class='note'>These are the charges that make a per-night rate quote not equal the "
                  "bill. Both are taken verbatim from the property's own terms; a blank means the page "
                  "read does not publish the figure.</p>"
                  "<div class='tbl-scroll'><table><thead><tr><th>Hotel</th>"
                  "<th>Extra occupant above double occupancy</th><th>Early check-out</th><th>Source / last checked</th>"
                  "</tr></thead><tbody>%s</tbody></table></div>"
                  "<p class='note'>Sources: the Venetian/Palazzo, Bellagio and MGM Grand hotel terms "
                  "linked in the table above.</p></div>") % "".join(extra)
    log = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class='note'>%s</td></tr>"
        % (esc(d), esc(hid), esc(field), esc(value),
           srclink(url) if url else '<span class="blank">no page</span>', esc(note))
        for d, hid, field, value, url, note in hotelsmod.RATE_LOG)

    calc = """
<div class="panel"><h2>True cost per night</h2>
<p class="note">Scenario estimate, not a checkout total. The official Venetian page says &ldquo;a daily Resort Fee of $55
<strong>plus tax</strong> per night&rdquo;, so tax is applied to room rate + resort fee. The tax rate
defaults to %(tax).2f%% for the Venetian scenario (%(taxsrc)s). Nightly rate is
deliberately <strong>not</strong> prefilled &mdash; no dated quote could be read from an official
booking engine, because they render prices with JavaScript (flag <a href="flagged.html#F-05">F-05</a>).</p>
<div class="calc">
<label>Nightly room rate ($)<input type="number" id="h-rate" placeholder="No verified quote" min="0" step="0.01"></label>
<label>Resort fee / night ($)<input type="number" id="h-fee" value="55" min="0" step="0.01"></label>
<label>Room tax (%%)<input type="number" id="h-tax" value="%(tax)s" min="0" step="0.01"></label>
<label>Parking / night ($)<input type="number" id="h-park" value="0" min="0" step="0.01"></label>
<label>Nights<input type="number" id="h-nights" value="3" min="1" step="1"></label>
</div>
<div class="calc" style="margin-top:14px">
<div class="out"><div class="k">Room + resort fee</div><div class="v" id="o-sub">&mdash;</div></div>
<div class="out"><div class="k">Tax</div><div class="v" id="o-tax">&mdash;</div></div>
<div class="out"><div class="k">True cost per night</div><div class="v" id="o-night">&mdash;</div></div>
<div class="out"><div class="k">Total for the stay</div><div class="v" id="o-total">&mdash;</div></div>
</div>
<p class="note" id="h-note"></p>
</div>
""" % dict(tax=TAX * 100, taxsrc=srclink(decisions.HOTEL_TERMS, "official Venetian terms"))

    body = """
<div class="hero"><h1>Hotels &amp; true cost per night</h1>
<p class="lede">Resort fee, tax, parking and cancellation are each shown with the official page they
were read from and the date. Rates are kept as a <strong>dated log</strong>, not a single value, so you
can see what was true when. A cell the property does not publish stays empty and is flagged.</p></div>

%(quotes)s
%(calc)s

<div class="banner info"><strong>The finding that changes the maths.</strong> The official Venetian
poker suite-rate page says you must &ldquo;play six hours of active live cash gameplay <em>or</em> buy
in to a $300 or higher tournament for each night stayed&rdquo; to keep the rate, and that the
requirement must be met before 2&nbsp;a.m. on the last night. The published $119 and $209 are conditional starting prices; the source does not explicitly assign a
price to each tower or promise either price for these dates. Do not add an event to qualify for an
unconfirmed discount. Nights that fail the play requirement are re-rated.
Source: %(srcrates)s</div>

<div class="panel"><h2>Hotel comparison</h2>
<div class="tbl-scroll"><table><thead><tr>
<th>Hotel</th><th>Resort fee / night</th><th class="num">Fee</th><th class="num">Room tax</th>
<th>Parking</th><th>Cancellation deadline</th><th>Dated checkout total</th><th>Fee source</th>
</tr></thead><tbody>%(rows)s</tbody></table></div>
<p class="note">The Venetian terms print 13.38%%. Do not apply it to another property without checking its
location and checkout tax treatment. See flag <a href="flagged.html#F-07">F-07</a>.</p>
</div>

%(extra)s

<div class="panel"><h2>Dated rate log</h2>
<p class="note">One line per reading, newest first. This is the point of keeping rates as a log: a rate
without a date and a source is not data.</p>
<div class="tbl-scroll"><table><thead><tr>
<th>Date read</th><th>Property</th><th>Field</th><th>Value</th><th>Source</th><th>Note</th>
</tr></thead><tbody>%(log)s</tbody></table></div>
</div>

<div class="panel"><h2>The poker suite rate, verbatim</h2>
<div class="quote">We offer suite rates for poker players who are interested in staying in either The
Venetian or The Palazzo. These rates will start as low as $119 and $209 and can be higher. Future rates
are only provided out to a maximum of 150 days from the current date. Rates are subject to qualifying
poker play and availability based on hotel occupancy. Blackout dates may apply. &hellip; There is a $55
resort fee per night stayed.</div>
<div class="quote">During your stay, you will be required to play six hours of active live cash gameplay
or buy in to a $300 or higher tournament for each night stayed. &hellip; These requirements must be met
prior to 2 a.m. the last night stayed. For any nights you fail to complete these requirements, your
nightly suite rate will be adjusted to the prevailing rate, and you will not receive the poker suite
rate discount.</div>
<div class="quote">In order to qualify for these rates, the first step is to book your suite through The
Venetian Resort Las Vegas by calling 866.255.8936 and mentioning code EPOKR25.</div>
<p class="note">Source: %(srcrates)s, retrieved %(ret)s. The poker rate cannot be combined with any
other promotional rate, and the page does not state a cancellation deadline.</p>
</div>
""" % dict(rows="".join(rows), log=log, calc=calc, ret=decisions.READ, extra=extra_html, quotes=quote_panel(),
           srcrates=srclink("https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
           )
    return page("Hotels & true cost", body, "hotels.html")


def route_evidence(row, google, computed):
    saved = google.get(row["hotel_id"]) if row["venue_id"] == "V-VEN" else None
    if saved:
        return saved
    # Prefer named poker-room directions over sending the visitor to a street geocode.
    destination = ("The Venetian Poker Room, The Palazzo, " if row["venue_id"] == "V-VEN" else row["venue"] + ", ") + row["venue_address"]
    url = "https://www.google.com/maps/dir/?" + urlencode(dict(api=1, origin=row["hotel_address"], destination=destination, travelmode="walking"))
    # A 0-minute route shares an outdoor endpoint, not the actual indoor poker room.
    mins = row["walk_min"] or None
    return mins, url, "OSRM estimate", computed, False


def google_routes():
    with open(os.path.join(ROOT, "data", "master.json"), encoding="utf-8") as f:
        previous = json.load(f)
    date = previous.get("walking_check", {}).get("google_as_of")
    return {h["id"]: (w["venetian_min"], w["maps_venetian"], "Google Maps route estimate", date, True)
            for h in previous["hotels"] if (w := h.get("walk")) and w.get("routers_agree_30min") is not None
            and date and w.get("venetian_min") is not None and w.get("maps_venetian", "").startswith("https://www.google.com/")}


def walk_table_row(row, google, computed):
    mins, url, kind, checked, is_google = route_evidence(row, google, computed)
    verdict = "unverified" if mins is None else ("estimated ≤30 min" if mins <= 30 else "estimated >30 min")
    official = sched.POKER_ROOM_URL if row["venue_id"] == "V-VEN" else None
    return ("<tr data-min='%s' data-maps='%d'><td>%s<div class='note'>%s</div></td><td class='num'>%s</td>"
            "<td>%s</td><td>%s · %s<br><a class='src' href=\"%s\" target='_blank' rel='noopener'>Google Maps walking directions</a>%s</td></tr>" %
            ("" if mins is None else mins, is_google, esc(row["hotel"]), esc(row["hotel_address"]),
             "" if mins is None else "%.1f min" % mins, verdict, esc(kind), esc(checked), esc(url),
             "<br>" + srclink(official, "Official poker room address / indoor directions") if official else ""))


def p_walking():
    with open(os.path.join(ROOT, "data", "site", "walking.json"), encoding="utf-8") as f:
        wj = json.load(f)
    rows = wj["rows"]
    google = google_routes()
    venues = sorted({(r["venue_id"], r["venue"]) for r in rows})
    out = []
    for vid, vname in venues:
        sub = sorted([r for r in rows if r["venue_id"] == vid], key=lambda r: r["walk_min"])
        trs = "".join(walk_table_row(r, google, wj["as_of"]) for r in sub)
        out.append(
            "<div class='panel' data-venue='%s'><h2>%s</h2><p class='note'>%s</p>"
            "<div class='tbl-scroll'><table><thead><tr><th>Hotel / origin address</th>"
            "<th class='num'>Walking estimate</th><th>30-minute rule</th><th>Route / last checked</th>"
            "</tr></thead><tbody>%s</tbody></table></div></div>"
            % (esc(vid), esc(vname), esc("Destination: %s (%s)" % (vname, sub[0]["venue_address"])), trs))
    controls = """
<div class="panel"><div class="controls">
<label>Poker room<select id="v"><option value="">All rooms</option>%s</select></label>
<label class="chk"><input type="checkbox" id="w30"> Within 30 minutes only</label>
<label class="chk"><input type="checkbox" id="w15"> Within 15 minutes only</label>
<label class="chk"><input type="checkbox" id="maps-evidence"> Dated Google Maps evidence only</label>
</div><p class="note" id="wc"></p></div>
""" % "".join('<option value="%s">%s</option>' % (esc(v), esc(n)) for v, n in venues)
    return page("Walking times", """
<div class="hero"><h1>Walking times</h1>
<p class="lede">Every hotel &times; poker-room pair, with a 30-minute filter and a Google Maps link on
each row so you can confirm the number yourself.</p></div>

<div class="banner"><strong>Routes, not stopwatch measurements.</strong> Where the earlier audit saved a
Google Maps reading, it is labelled with the retrieval date. Other numbers come from OSRM/OpenStreetMap.
A link by itself does not prove a duration. Neither router verifies the casino's interior route, and
an estimate near 30 minutes should be treated as uncertain. <a href="flagged.html#F-08">F-08</a>.</div>

%s
%s
<div class="panel"><h2>Indoor route to the Venetian poker room, from the official page</h2>
<p class="note">The Venetian publishes walking <em>routes</em> but no times. Worth knowing anyway: the
poker room is indoors, on level 2.</p>
<div class="quote"><strong>From The Venetian Lobby:</strong> Proceed across The Venetian casino floor,
to Restaurant Row. Enter the Waterfall Atrium. Look for the escalator by the Waterfall Atrium. Take the
escalator up to level 2, Grand Canal Shoppes. Make a u-turn and take the hallway to the right. Turn
right at EJ Pretty and The Poker Room will be on your right.</div>
<div class="quote"><strong>From The Palazzo Lobby:</strong> Proceed across The Palazzo Casino Floor to
the self-parking elevators. Take the elevator up to level 2, Grand Canal Shoppes. Enter Grand Canal
Shoppes and take a left at Liam&rsquo;s Den and Bubble Bar. The Poker Room will be straight ahead.</div>
<p class="note">Source: %s, retrieved %s.</p></div>
""" % (controls, "".join(out), srclink(sched.POKER_ROOM_URL), decisions.READ), "walking.html")


def p_trip(events):
    cands = [e for e in events if e["group"] == "candidate" and e["buy_in"] and not demographic_gate(e)]
    cands.sort(key=lambda e: (e["buy_in"], e["event_no"]))
    opts = "".join(
        '<option value="%d" data-buyin="%d" data-pool="%s">#%d &mdash; %s ($%s)</option>'
        % (e["event_no"], e["buy_in"], e["pool_per_entry"] or 0, e["event_no"],
           esc(e["name"][:58]), format(e["buy_in"], ","))
        for e in cands)
    return page("Trip cost", """
<div class="hero"><h1>Trip cost estimator</h1>
<p class="lede">Estimated cost of a trip = entries &times; buy-ins + nights &times; true hotel cost
per night. Use the calculator for scenarios only; there is no verified stay quote and no confirmed
freezeout to add to an itinerary.</p></div>

<div class="panel"><h2>Entries</h2>
<p class="note">Compare at most one buy-in per research candidate. The shortlist excludes known spending formats
and restricted entries. A candidate is not a confirmed freezeout.</p>
<div class="controls">
<label>Add an event<select id="pick"><option value="">Choose a research lead</option>%s</select></label>
<button class="btn" id="add">Add</button>
</div>
<table id="cart"><thead><tr><th class="num">#</th><th>Event</th><th class="num">Entry fee</th>
<th class="num">To prize pool</th><th></th></tr></thead><tbody></tbody>
<tfoot><tr><th colspan="2">Total entry fees</th><th class="num" id="sum-buyin">$0</th>
<th class="num" id="sum-pool">$0</th><th></th></tr></tfoot></table>
</div>

<div class="panel"><h2>Hotel</h2>
<div class="calc">
<label>Hotel checkout total for the stay ($)<input type="number" id="t-checkout" min="0" step="0.01"></label>
<label>Nights<input type="number" id="t-nights" min="0" step="1"></label>
</div>
<p class="note">Use the final checkout total for the same dates and occupancy, including mandatory fees
and taxes. Include applicable parking once. Leave the quote blank if unavailable, or enter zero nights
for an entries-only trip. <a href="hotels.html">Hotel sources and rate log</a>.</p>
</div>

<div class="panel"><h2>Total</h2>
<div class="calc">
<div class="out"><div class="k">Entry fees</div><div class="v" id="tot-buyin">$0</div></div>
<div class="out"><div class="k">True cost per night</div><div class="v" id="tot-night">Not available</div></div>
<div class="out"><div class="k">Hotel for the stay</div><div class="v" id="tot-hotel">Not available</div></div>
<div class="out"><div class="k">Estimated trip cost</div><div class="v" id="tot-all">Not available</div></div>
</div>
<p class="note">Excludes flights, food and cash-game bankroll. No promotional room rate is assumed.</p>
</div>
""" % opts, "trip.html")


def p_venues(events):
    cards = []
    for key, meta in ROOM_META.items():
        wj, rows = _walk_rows_for(meta["walk_key"])
        if rows:
            ok = sum(1 for r in rows if r["within_30_min"])
            stat = "%d of %d hotels within 30 min" % (ok, len(rows))
            nearest = rows[0]["hotel"] if rows else ""
        else:
            stat, nearest = "walking data not in this checkout", ""
        if key == "venetian":
            pub = ("64 events, 94 scheduled rows, all 37 structure sheets read. The only room that "
                   "publishes a dated schedule <em>and</em> a per-event structure sheet.")
        else:
            v = contentmod.OTHER_VENUES_BY_ID[key]
            pub = esc(v["verdict"])
        cards.append(
            "<div class='panel'><h2><a href='%s'>%s</a></h2>"
            "<p class='note'><strong>Room:</strong> %s</p>"
            "<p class='note'><strong>Hotels:</strong> %s%s</p>"
            "<p>%s</p><p><a href='%s'>Open the %s page &rarr;</a></p></div>"
            % (meta["page"], esc(meta["title"]), esc(meta["room"]),
               esc(stat), (" &middot; nearest: " + esc(nearest)) if nearest else "",
               pub, meta["page"], esc(meta["title"])))
    cards.append(
        "<div class='panel'><h2><a href='venues/other.html'>Resorts World &amp; Westgate</a></h2>"
        "<p class='note'>Two further rooms were checked and publish no tournament data on the pages "
        "read, so they have no page of their own beyond the other-rooms record.</p>"
        "<p><a href='venues/other.html'>Open the other rooms page &rarr;</a></p></div>")
    return page("Venues", """
<div class="hero"><h1>Venues</h1>
<p class="lede">One page per poker room, each listing that room's events and the hotels within walking
distance of it. The Venetian is the only Strip room that publishes a dated tournament schedule
<em>and</em> a per-event official structure sheet, so it is the only room that can be ranked line by
line. Every other room gets the same page structure, with the gap documented rather than filled.</p></div>

<div class="banner info"><strong>How to read a room page.</strong> The events table holds only rows
transcribed from that room's own official document. Where the room publishes no dated event, the table
is empty and the reason is quoted underneath with the page that was checked. The hotels table applies
the 30-minute walking limit to routed estimates, with a Maps link on every row.</div>

<div class="grid2">%s</div>
""" % "".join(cards), "venues.html", subnav=SUBNAV["venues.html"])


def p_venue_venetian(events, days):
    rows = "".join(
        "<tr><td class='num'>%d</td><td>%s</td><td class='num'>$%s</td><td>%s</td><td>%s</td></tr>"
        % (e["event_no"], esc(e["name"][:70]),
           format(e["buy_in"], ",") if e["buy_in"] else "&mdash;",
           ", ".join("<span class='note'>%s</span>" % d[5:] for d in e["dates"]),
           "<span class='tag t-%s'>%s</span>" % (e["group"], esc(e["group_label"].split(" (")[0])))
        for e in events)
    return page("The Venetian", """
<div class="hero"><h1>The Venetian Resort &mdash; DeepStack Extravaganza IV</h1>
<p class="lede">November 16 &ndash; December 23, 2026. More than $3.6 million in guaranteed prize pools
across %(n)s events. This is the only Strip room whose official documents support a line-by-line
comparison.</p></div>

<div class="grid2">
<div class="panel"><h2>The room</h2>
<dl class="kv">
<dt>Location</dt><dd>The Palazzo, level 2, Grand Canal Shoppes</dd>
<dt>Hours</dt><dd>Open 24 hours, seven days</dd>
<dt>Size</dt><dd>50 tables across 14,000 sq ft &mdash; the largest room on the Strip</dd>
<dt>Entry requirement</dt><dd>Must be 21+ and hold a Venetian Rewards card</dd>
<dt>Parking</dt><dd>Registered guests $20/day. Non-registered guests who play 3+ hours get free self-parking</dd>
<dt>Phone</dt><dd>702.414.7657</dd>
<dt>Email</dt><dd>lv_cas_poker@venetianlasvegas.com</dd>
</dl>
<p class="note">Source: %(room)s, retrieved %(ret)s.</p>
</div>

<div class="panel"><h2>Series dates and documents</h2>
<dl class="kv">
<dt>Series</dt><dd>DeepStack Extravaganza IV, Nov 16 &ndash; Dec 23 2026</dd>
<dt>Schedule page</dt><dd>%(sched)s</dd>
<dt>Schedule PDF</dt><dd>%(pdf)s</dd>
<dt>Structure sheets</dt><dd>37 PDFs, all read on %(ret)s</dd>
<dt>Next series</dt><dd>DeepStack Extravaganza NYE, Dec 24 2026 &ndash; Jan 10 2027</dd>
<dt>Then</dt><dd>DeepStack Showdown, Jan 11 &ndash; Feb 14 2027</dd>
</dl>
<p class="note">Source: %(series)s</p>
</div>
</div>

<div class="panel"><h2>Every event in the series</h2>
<div class="tbl-scroll"><table><thead><tr>
<th class="num">#</th><th>Event</th><th class="num">Entry</th><th>Dates</th><th>Classification</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>

<div class="banner"><strong>Irregularity X-02.</strong> The official series overview page still labels
its &ldquo;Current Series&rdquo; as the WPT Fall Festival (Oct 28 &ndash; Nov 15, 2026) even though
that series has ended and DSE IV is live. Do not rely on that label &mdash; use the dated event page.
%(series)s</div>
""" % dict(n=len(events), rows=rows, ret=RETRIEVED,
           room=srclink(sched.POKER_ROOM_URL),
           sched=srclink(sched.SCHEDULE_URL, "dse-nov-2026.html"),
           pdf=srclink(sched.SCHEDULE_PDF, "dse-nov-2026-schedule.pdf"),
           series=srclink(sched.SERIES_URL, "series overview")),
                        "venues/venetian.html", subnav=VENUE_SUBNAV)



# --------------------------------------------------------------------------------------
# one page per poker room
# --------------------------------------------------------------------------------------

# Room -> the official venue label used in data/site/walking.json, plus what the room is.
ROOM_META = {
    "venetian": dict(
        walk_key="V-VEN",
        title="The Venetian Resort",
        room="The Venetian poker room",
        desc=("The poker room is indoors on level 2 of the Grand Canal Shoppes, reached by escalator "
              "from the Waterfall Atrium. Requires a Venetian Rewards card."),
        page="venues/venetian.html",
    ),
    "wynn": dict(
        walk_key="V-WYN",
        title="Wynn / Encore",
        room="Wynn poker room",
        desc="Host room for the WPT World Championship (Nov 27 - Dec 21) and the daily slate. Its page states "
             "the Friday daily is a '$40,000 guaranteed NLH Rebuy' and prints no buy-in or entry limit for any "
             "daily event, so no Wynn event can enter the single-entry table.",
        page="venues/wynn.html",
    ),
    "horseshoe": dict(
        walk_key="V-HS",
        title="Horseshoe Las Vegas",
        room="Hall of Fame poker room",
        desc="20 tables, six tournament times a day advertised; no buy-in, guarantee or entry rule published.",
        page="venues/horseshoe.html",
    ),
    "caesars-palace": dict(
        walk_key="V-CP",
        title="Caesars Palace",
        room="Caesars Palace poker room",
        desc=("Four daily NLH events at 10 AM, 2 PM, 6 PM and 9 PM, published as an official "
              "daily flyer PDF. Re-entry and a $50 add-on are printed on it, so none of them is "
              "single-entry. Read 2026-11-17."),
        page="venues/caesars-palace.html",
    ),
    "bellagio": dict(
        walk_key="V-BEL",
        title="Bellagio",
        room="Bellagio poker room",
        desc=("Three weekly events with official structure sheets: Friday $600 NLH, Saturday NLH "
              "and Sunday $400 H.O.R.S.E., all at 11:00 AM. Each sheet prints re-entry and a "
              "gratuity that buys extra chips. Read 2026-11-17."),
        page="venues/bellagio.html",
    ),
    "mgm-grand": dict(
        walk_key="V-MGM",
        title="MGM Grand",
        room="MGM Grand poker room",
        desc="Publishes a weekly tournament-schedule PDF and hotel terms; no per-event entry rule read.",
        page="venues/mgm-grand.html",
    ),
}


def _walk_rows_for(walk_key):
    """Routed walking estimate from every hotel to one poker room, shortest first."""
    path = os.path.join(ROOT, "data", "site", "walking.json")
    if not os.path.exists(path):
        return None, None
    with open(path, encoding="utf-8") as f:
        wj = json.load(f)
    rows = [r for r in wj["rows"] if r["venue_id"] == walk_key]
    rows.sort(key=lambda r: r["walk_min"])
    return wj, rows


def _walk_panel(walk_key, room):
    wj, rows = _walk_rows_for(walk_key)
    if wj is None:
        return ("<div class='panel'><h2>Hotels within walking distance</h2><p class='note'>The walking "
                "dataset is not present in this checkout, so no distance is shown.</p></div>")
    google = google_routes()
    trs = "".join(walk_table_row(r, google, wj["as_of"]) for r in rows)
    return ("""
<div class="panel"><h2>Hotel routes to %(room)s</h2>
<p class="note">Routing estimates use dated Google Maps readings where held; otherwise the OSRM foot-profile matrix.
No published interior duration is assumed. Every row has a route link. Flag <a href="flagged.html#F-08">F-08</a>.</p>
<div class="chk-row"><label class="chk"><input type="checkbox" id="w30" data-walk-room="%(key)s">
Within 30 minutes only</label><span class="note" id="wc"></span></div>
<div class="tbl-scroll"><table id="wt-%(key)s"><thead><tr><th>Hotel</th>
<th class="num">Walking estimate</th><th>30-minute rule</th><th>Verify</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>
""" % dict(room=esc(room), key=walk_key,
           rows=trs))


def other_room_schedule(key):
    """Official schedule table for a non-Venetian room that publishes one.

    Added 2026-11-17 by session arena/7cc9ee65-poker2: Caesars Palace and Bellagio both
    publish official tournament documents, so their rows are rendered here instead of the
    room page saying the room publishes nothing. Every row cites the room's own PDF and is
    kept out of the single-entry ranking, because every one of these events is a re-entry or
    add-on event on the face of its own sheet.
    """
    if key == "caesars-palace":
        sched_data = othermod.CAESARS_SCHEDULE
        head = ("<tr><th>Start</th><th class='num'>Buy-in</th><th class='num'>House fee</th>"
                "<th class='num'>To prize pool</th><th>Add-on</th><th class='num'>Chips</th>"
                "<th class='num'>Levels</th><th class='num'>Guarantee</th></tr>")
        rows = "".join(
            "<tr><td>%s</td><td class='num'>$%s</td><td class='num'>$%s</td>"
            "<td class='num'>$%s</td><td>$%d add-on &middot; %s chips at the first break</td>"
            "<td class='num'>%s</td><td class='num'>%d min</td><td class='num'>%s</td></tr>"
            % (esc(r["start"]), format(r["buy_in"], ","), format(r["house_fee"], ","),
               format(r["to_pool"], ","), r["add_on"], format(r["add_on_chips"], ","),
               format(r["chips"], ","), r["level_min"],
               "$" + format(r["guarantee"], ",") if r["guarantee"] else "&mdash;")
            for r in sched_data["rows"])
        doc_link = srclink(sched_data["source"], "official daily tournament flyer (PDF)")
    elif key == "bellagio":
        sched_data = othermod.BELLAGIO_SCHEDULE
        head = ("<tr><th>Day</th><th>Start</th><th>Event</th><th class='num'>Buy-in</th>"
                "<th class='num'>House fee</th><th>Gratuity buys chips</th>"
                "<th class='num'>Starting chips</th><th class='num'>Levels</th>"
                "<th class='num'>Guarantee</th><th>Structure sheet</th></tr>")
        rows = ""
        for r in sched_data["events"]:
            buy = ("$" + format(r["buy_in"], ",")) if r["buy_in"] else (
                "<span class='blank-cell'>conflict &mdash; see X-04</span>")
            rows += (
                "<tr><td>%s</td><td>%s</td><td>%s</td><td class='num'>%s</td>"
                "<td class='num'>$%s</td><td>$%d &rarr; +%s chips</td>"
                "<td class='num'>%s without &middot; %s with</td><td class='num'>%d min</td>"
                "<td class='num'>%s</td><td>%s</td></tr>"
                % (esc(r["day"]), esc(r["start"]), esc(r["name"]), buy,
                   format(r["house_fee"], ","), r["gratuity"],
                   format(r["gratuity_chips"], ","),
                   format(r["chips_without_gratuity"], ","),
                   format(r["chips_with_gratuity"], ","), r["level_min"],
                   ("$" + format(r["guarantee"], ",")) if r["guarantee"] else "&mdash;",
                   srclink(r["source"], "PDF")))
        doc_link = srclink(sched_data["room_page"], "official Bellagio poker page")
    else:
        return ""

    quotes = "".join(
        '<div class="quote"><strong>%s.</strong> %s</div>' % (esc(t), esc(q))
        for t, q in (sched_data.get("quotes") or []))
    if key == "bellagio":
        quotes = "".join(
            '<div class="panel"><h3>%s &mdash; %s</h3>%s<div class="note">%s</div>'
            '<ul class="tight">%s</ul></div>'
            % (esc(r["day"]), esc(r["name"]),
               "".join('<div class="quote"><strong>%s.</strong> %s</div>' % (esc(t), esc(q))
                       for t, q in r["quotes"]),
               srclink(r["source"], "official structure sheet (PDF)"),
               "".join("<li>%s</li>" % esc(g) for g in r["gaps"]))
            for r in sched_data["events"])

    gaps = "".join("<li>%s</li>" % esc(g) for g in sched_data.get("gaps") or [])
    if gaps:
        gaps = ("<div class='panel'><h3>What the official document does not print</h3>"
                "<ul class='tight'>%s</ul></div>" % gaps)
    notes = "".join("<li>%s</li>" % esc(n) for n in sched_data.get("notes") or [])
    if notes:
        notes = ("<ul class='tight'>%s</ul>" % notes)

    irr = [i for i in othermod.IRREGULARITIES if i["room"] == sched_data["room"]]
    irr_html = ""
    if irr:
        irr_html = ("<div class='panel'><h3>Irregularities in the official document</h3>"
                    "<table><thead><tr><th class='num'>ID</th><th>What the document says</th>"
                    "<th>Why it matters</th><th>Source</th></tr></thead><tbody>%s</tbody></table>"
                    "</div>" % "".join(
                        "<tr id='%s'><td class='num'>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                        % (esc(i["id"]), esc(i["id"]), esc(i["what"]), esc(i["why_it_matters"]),
                           srclink(i["source"], "official page"))
                        for i in irr))

    return """
<div class="panel"><h2>Official tournament schedule</h2>
<p>Transcribed line by line from the room's own document, read %s. These rows are
<strong>not</strong> in the single-entry ranking: the sheet for each one prints re-entry or a
paid add-on, which is the class of event the brief asks to keep separate. The Venetian table
stays the only ranked table, because it is the only room that publishes a dated schedule
<em>and</em> a per-event structure sheet.</p>
<p class="note">Source: %s &middot; cadence: %s</p>
<div class="tbl-scroll"><table><thead>%s</thead><tbody>%s</tbody></table></div>
<p><strong>Verdict.</strong> %s</p>
%s
</div>
%s
<div class="panel"><h3>What the official document says, in its own words</h3>%s</div>
%s
""" % (esc(sched_data["retrieved"]), doc_link, esc(sched_data["cadence"]), head, rows,
       esc(sched_data["verdict"]), notes, gaps, quotes, irr_html)


def p_venue_room(key, events):
    meta = ROOM_META[key]
    own = contentmod.OTHER_VENUES_BY_ID.get(key)
    # events and hotels for this room
    if key == "venetian":
        ev_html = ("<p>64 events across 38 playable days, all 37 structure sheets read. "
                   "<a href='../tournaments.html'>Open the full event table</a> or "
                   "<a href='../schedule.html'>the day plan</a>.</p>")
        hotel_count = 21
    else:
        ev_html = ('<p class="blank-cell">No dated event row is published by this room that could be '
                   'transcribed, so this table is intentionally empty. The reason is recorded below '
                   'with the source that was checked.</p>')
        hotel_count = None
    if key in ("caesars-palace", "bellagio"):
        # These two rooms do publish an official schedule document; render it instead of the
        # empty-state paragraph. Read 2026-11-17, session arena/7cc9ee65-poker2.
        ev_html = other_room_schedule(key)
    if key == "wynn":
        entries = "".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s · %s</td></tr>" %
                          (esc(name), esc(dates), esc(finding), srclink(url, label), decisions.READ)
                          for name, dates, finding, url, label in decisions.FINDINGS)
        ev_html = ("<p>%s · %s</p><table><thead><tr><th>Series</th><th>Dates</th><th>Entry rule finding</th>"
                   "<th>Source / last checked</th></tr></thead><tbody>%s</tbody></table><p>%s</p>" %
                   (srclink(decisions.WYNN, "Official Wynn poker room"), decisions.READ, entries,
                    srclink(decisions.WYNN_JAN_RULES, "January structures (placeholder)")))
    whats = ""
    if own:
        finds = "".join(
            '<div class="quote">%s<div class="note">%s, retrieved %s</div></div>'
            % (esc(f["text"]), srclink(f["url"]), esc(f["retrieved"]))
            for f in own["earlier_findings"])
        whats = ("""
<div class="panel"><h2>What this room publishes</h2>
<p><strong>Poker room:</strong> %(room)s. %(desc)s</p>
<p><strong>Checked %(ret)s:</strong> %(status)s</p>
%(finds)s
<p><strong>Verdict:</strong> %(verdict)s</p>
<p class="note">Official page: %(url)s &middot; provenance: %(prov)s</p></div>
""" % dict(room=esc(own["poker_room"]), desc=esc(meta["desc"]), ret=RETRIEVED,
           status=esc(own["status_this_session"]), finds=finds,
           verdict=esc(own["verdict"]), url=srclink(own["url"]),
           prov=esc(own["provenance"])))
    body = """
<div class="hero"><h1>%(title)s &mdash; %(room)s</h1>
<p class="lede">%(desc)s</p></div>

<div class="panel"><h2>Events</h2>%(ev)s</div>
%(whats)s
%(walk)s

<div class="panel"><h2>Getting there</h2>
<p class="note">The distances above are to the poker room as a destination. Re-check the room's own
page for entrances, hours and any access requirement before you travel.</p></div>
""" % dict(title=esc(meta["title"]), room=esc(meta["room"]), desc=esc(meta["desc"]),
           ev=ev_html, whats=whats, walk=_walk_panel(meta["walk_key"], meta["room"]))
    return page(meta["title"], body, meta["page"], subnav=VENUE_SUBNAV)



def p_venue_other():
    blocks = []
    for v in contentmod.OTHER_VENUES:
        # The date printed next to "Checked" must be the date recorded on *that* venue's own reading,
        # never the build date: an earlier pass hardcoded 2026-11-17 here while five of the seven rooms
        # say "Not re-read in this session". A checked-date that is really a build-date is how a page
        # certifies evidence nobody looked at.
        _read = max([f["retrieved"] for f in v["earlier_findings"] if f.get("retrieved")] or [RETRIEVED])
        if v.get("checked"):
            _when = "Checked %s:" % v["checked"]
        else:
            _when = "Not re-read in this pass (last read %s):" % _read
        finds = "".join(
            '<div class="quote">%s<div class="note">%s, retrieved %s</div></div>'
            % (esc(f["text"]), srclink(f["url"]), esc(f["retrieved"]))
            for f in v["earlier_findings"])
        blocks.append(
            "<div class='panel'><h2>%s</h2>"
            "<p class='note'><strong>Poker room:</strong> %s</p>"
            "<p><strong>%s</strong> %s</p>"
            "%s"
            "<p><strong>Verdict:</strong> %s</p>"
            "<p class='note'>Provenance: %s. Official page: %s</p></div>"
            % (esc(v["name"]), esc(v["poker_room"]), esc(_when), esc(v["status_this_session"]), finds,
               esc(v["verdict"]), esc(v["provenance"]), srclink(v["url"])))
    return page("Other rooms", """
<div class="hero"><h1>Other Strip poker rooms</h1>
<p class="lede">Seven other rooms in and around the Strip area were checked. Two of them &mdash;
Caesars Palace and Bellagio &mdash; do publish official tournament documents, read live on
%(ret)s, and their rows are on their own venue pages. None of the seven publishes a
<em>single-entry</em> event, so none of them can enter the ranked table. This page records
exactly what each one publishes, so the gap is documented rather than filled.</p></div>

<div class="banner"><strong>Why the ranked tables are Venetian-only.</strong> This is a finding, not
a coverage limit. To rank an event on entry fee and prize pool you need a buy-in, a guarantee and an
entry rule, each from the room itself. Only The Venetian publishes all three for a dated schedule
<em>and</em> stays silent on re-entry. Caesars Palace publishes four daily events and Bellagio three
weekly ones, but every sheet prints re-entry or a paid add-on, so they sit in the
spending-more-money section instead. Horseshoe publishes six start times and nothing else.
Resorts World's poker page redirects to a dining page. Westgate publishes room hours. Wynn's live
page states a $10,000 guaranteed event every evening at 6 p.m. and prints no buy-in for any daily
event. MGM Grand's poker page returned a not-found page on %(ret)s
(<a href="flagged.html#X-06">X-06</a>); the URL this site used to cite for Wynn does too
(<a href="flagged.html#X-07">X-07</a>). Flag
<a href="flagged.html#F-10">F-10</a>, <a href="flagged.html#F-11">F-11</a>.</div>

%(blocks)s
""" % dict(blocks="".join(blocks), ret=RETRIEVED), "venues/other.html", subnav=VENUE_SUBNAV)


def p_summary(events, days):
    cands = [e for e in events if e["group"] == "candidate"]
    ranked = sorted([e for e in cands if e["ratio"] and any(day >= decisions.READ for day in e["dates"])], key=lambda e: -e["ratio"])
    cheapest = sorted([e for e in cands if e["buy_in"]], key=lambda e: e["buy_in"])
    earliest = sorted([e for e in events if e["starts"]], key=lambda e: tminutes(e["starts"][0]))
    top = "".join(
        "<tr><td class='num'>%d</td><td>#%d %s<br>%s</td><td class='num'>$%s</td><td class='num'>%s</td>"
        "<td class='num'>%s</td><td>%s</td></tr>"
        % (i + 1, e["event_no"], esc(e["name"][:56]), srclink(e["sheet_url"], "Structure sheet"), format(e["buy_in"], ","),
           ("$" + format(e["gtd"], ",")) if e["gtd"] else "&mdash;",
           "%.1f&times;" % e["ratio"] if e["ratio"] else "&mdash;",
           ", ".join("<span class='note'>%s</span>" % d[5:] for d in e["dates"]))
        for i, e in enumerate(ranked[:8]))
    counts = {}
    for e in events:
        counts[e["group"]] = counts.get(e["group"], 0) + 1
    dist = "".join("<tr><td><span class='tag t-%s'>%s</span></td><td class='num'>%d</td>"
                   "<td class='note'>%s</td></tr>"
                   % (k, esc(GROUP_LABEL[k].split(" (")[0]), counts.get(k, 0), why)
                   for k, why in [
                       ("candidate", "Not confirmed: one-day, one starting day, no "
                                     "re-entry, rebuy or add-on clause on the official sheet."),
                       ("bounty", "Bounty or PKO. The guarantee includes bounty "
                                  "money so the cash pool is smaller."),
                       ("multiflight", "Multi-flight or multi-day. Buying into another flight differs from a continuation."),
                       ("satellite", "Prize is a seat in another event, not cash."),
                       ("spend", "The official sheet prices a subsequent buy-in."),
                       ("team", "Two players share one entry."),
                   ] if counts.get(k))
    return page("Executive summary", """
<div class="hero"><h1>Executive summary</h1>
<p class="lede">%(headline)s</p></div>
<div class="panel"><h2>Decision for the November 25–28 scenario</h2>
<p><strong>Do not make a nonrefundable booking on this evidence.</strong> Venetian events
<a href="tournaments.html#ev10">#10</a>, <a href="tournaments.html#ev12">#12</a> and
<a href="tournaments.html#ev14">#14</a> offer one 11:10 AM research lead per day on November 25, 26
and 27, respectively. No lead is a confirmed freezeout and no evening entry is assumed. The first
start precedes standard hotel check-in. <a href="hotels.html#checkout-log">The exact-date lookup</a>
produced no checkout quote. The Venetian and Palazzo are the indoor-route shortlist, not price winners.</p>
<p><a href="venues/wynn.html">Wynn</a> lists WPT and the January Signature Series; the WPT opener expressly
allows re-entry and the January rules were still a placeholder when checked.</p></div>

<div class="cards">
<div class="card"><div class="k">Series covered</div><div class="v">DSE IV</div>
<div class="s">Nov 16 &ndash; Dec 23, 2026 &middot; %(n)s events</div></div>
<div class="card"><div class="k">Official documents read</div><div class="v">39</div>
<div class="s">37 structure sheets + schedule page + schedule PDF</div></div>
<div class="card"><div class="k">Confirmed single-entry</div><div class="v">0</div>
<div class="s">no official sheet states a one-entry rule</div></div>
<div class="card"><div class="k">Best candidates</div><div class="v">%(nc)d</div>
<div class="s">sheet silent on re-entry, rebuy and add-on</div></div>
<div class="card"><div class="k">Cheapest entry</div><div class="v">$%(cheap)s</div>
<div class="s">%(cheapname)s</div></div>
<div class="card"><div class="k">Earliest start</div><div class="v">%(early)s</div>
<div class="s">%(earlywhat)s</div></div>
</div>

<div class="panel"><h2>What was verified</h2>
<ul class="tight">
<li><strong>All 37 official Venetian structure sheets</strong> were read individually on %(ret)s,
covering all 64 event numbers in the series. Each was transcribed field by field: buy-in split,
late-registration close, starting stack, level length, payout share, bounty mechanic, and whether any
re-entry, rebuy or add-on clause appears.</li>
<li><strong>The official schedule</strong> was read twice, from the HTML event page and from the
schedule PDF, which prints registration-close times, chip counts and level lengths the HTML page does
not. The two agree on every row.</li>
<li><strong>The hotel numbers</strong> come from the official resort-fee page and the official poker
suite-rate page, both read on %(ret)s.</li>
<li><strong>Seven other poker rooms</strong> were checked. Two of them &mdash; Caesars Palace and
Bellagio &mdash; publish official schedules, read live on %(ret)s, but every event on those sheets
prints re-entry or a paid add-on (<a href="flagged.html#X-03">X-03</a>&ndash;<a
href="flagged.html#X-05">X-05</a>, <a href="flagged.html#F-11">F-11</a>). No event from these reads meets the strict single-entry policy. The table below is research only.</li>
</ul></div>

<div class="panel"><h2>What could not be verified</h2>
<ul class="tight">
<li><strong>Any single-entry guarantee.</strong> Not one official document says an event is one entry
only. The strongest available statement is the absence of a re-entry clause. <a href="flagged.html#F-01">F-01</a></li>
<li><strong>Any finish time.</strong> No event has a published end time, so no two events can be
promised as a sequence. <a href="flagged.html#F-04">F-04</a></li>
<li><strong>Any dated hotel quote.</strong> Official booking engines render prices with JavaScript.
<a href="flagged.html#F-05">F-05</a></li>
<li><strong>Any official quality rating.</strong> No hotel page publishes a star or diamond rating.
<a href="suggestions.html#S-06">S-06</a></li>
<li><strong>Any measured walking time.</strong> The matrix is a routing estimate with a Google Maps
link on every row. <a href="flagged.html#F-08">F-08</a></li>
</ul></div>

<div class="panel"><h2>How the %(nv)s events split</h2>
<div class="tbl-scroll"><table><thead><tr><th>Group</th><th class="num">Events</th><th>What it means</th>
</tr></thead><tbody>%(dist)s</tbody></table></div></div>

<div class="panel"><h2>Research shortlist by published ratio</h2>
<p class="note">Entry dates on or after Nov 19, 2026. Guarantee &divide; total entry fee, shown only where both numbers are printed on the
official documents. <strong>Descriptive, not a forecast</strong> &mdash; a guarantee is a floor the room
commits to, not a predicted pool.</p>
<div class="tbl-scroll"><table><thead><tr><th class="num">#</th><th>Event</th>
<th class="num">Entry</th><th class="num">Guarantee</th><th class="num">GTD&divide;entry</th>
<th>Dates</th></tr></thead><tbody>%(top)s</tbody></table></div>
</div>

<div class="panel"><h2>The decision this all rests on</h2>
<p>You asked for single-entry tournaments only, and for anything where money buys an advantage to be
kept in a separate section. The documents let us do the second half cleanly: multi-flight events,
satellites, team events, bounty formats and the two Valuetown events that price a second buy-in are all
in their own groups.</p>
<p>The first half cannot be completed from the documents alone. <strong>No official sheet states a
one-entry rule.</strong> The research candidates have one scheduled starting day and carry no re-entry, rebuy
or add-on clause at all &mdash; which is the strongest evidence available, and is still silence rather
than a promise. Written confirmation from the poker room would resolve that gap.
See <a href="suggestions.html#S-01">S-01</a> and <a href="questions.html#Q-01">Q-01</a>.</p>
</div>
""" % dict(headline=esc(contentmod.SUMMARY_HEADLINE), n=len(events), nv=len(events), nc=len(cands),
           dist=dist, top=top, ret=RETRIEVED,
           cheap=format(cheapest[0]["buy_in"], ",") if cheapest else "&mdash;",
           cheapname=esc(cheapest[0]["name"][:40]) if cheapest else "",
           early=esc(earliest[0]["starts"][0]) if earliest else "&mdash;",
           earlywhat=("event #%d" % earliest[0]["event_no"]) if earliest else ""),
                        "summary.html")


def p_questions():
    rows = "".join(
        "<tr id='%s'><td class='num'>%s</td><td><strong>%s</strong></td><td>%s</td>"
        "<td>%s</td><td><span class='tag t-bad'>open</span></td></tr>"
        % (esc(q["id"]), esc(q["id"]), esc(q["q"]), esc(q["why"]), esc(q["blocks"]))
        for q in contentmod.QUESTIONS)
    body = """
<div class="hero"><h1>Questions that must be answered first</h1>
<p class="lede">What we know, what we do not know, and what has to be settled before any decision here
is reasonable. Every question below is open &mdash; none can be answered from the official documents,
because the organiser does not publish the answer.</p></div>

<div class="banner"><strong>Two questions block everything else.</strong>
<a href="#Q-02">Q-02</a> (your exact dates) blocks any hotel quote, the night count, and which events
you can enter at all. <a href="#Q-01">Q-01</a> (do you accept silence on re-entry, or do you need the
room to confirm it in writing) decides whether the candidate events are usable now or only after one
email.</div>

<div class="panel"><div class="tbl-scroll"><table><thead><tr>
<th class="num">ID</th><th>Question</th><th>Why it matters</th><th>What it blocks</th><th>Status</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>

<div class="panel"><h2>Information we have</h2>
<ul class="tight">
<li>Dates, start times, registration closes, chip counts and level lengths for all %(nrows)s scheduled
rows &mdash; official.</li>
<li>Buy-in splits (house fee vs prize pool) for every event &mdash; official, from the structure sheets.</li>
<li>Which events are multi-flight, bounty, PKO, satellite or team &mdash; official, from the sheets.</li>
<li>Two events whose sheet prices a second buy-in &mdash; official, quoted.</li>
<li>Resort fees for six properties, and the Venetian poker suite rate with its qualifying-play
condition &mdash; official.</li>
<li>Indoor walking routes to the Venetian poker room, from the official poker page.</li>
</ul></div>

<div class="panel"><h2>Information we do not have</h2>
<ul class="tight">
<li>Whether any event is single entry. Not published anywhere.</li>
<li>Finish times, or any basis for deriving one. No field sizes are published in advance.</li>
<li>A dated hotel rate for any property, from any official source.</li>
<li>A cancellation deadline for any property.</li>
<li>An official quality rating for any property.</li>
<li>A measured walking time. The matrix is modelled, not measured.</li>
<li>Any tournament schedule at all for six of the seven other rooms checked.</li>
</ul>
<p class="note">Each of these is logged with the attempt that produced it on
<a href="flagged.html">Flagged for review</a>, and each has a suggestion for how to close it on
<a href="suggestions.html">Suggestions</a>.</p></div>
""" % dict(rows=rows, nrows=len(sched.ROWS))
    return page("Questions", body, "questions.html")


def p_suggestions():
    rows = "".join(
        "<tr id='%s'><td class='num'>%s</td><td><strong>%s</strong></td><td>%s</td><td>%s</td>"
        "<td>%s</td><td>%s</td><td>%s</td></tr>"
        % (esc(s["id"]), esc(s["id"]), esc(s["title"]),
           esc(s.get("what") or s.get("why") or ""),
           esc(s["decides"]), esc(s["cost"]), esc(s["effort"]),
           (('<a href="%s#%s">%s</a>' % ("questions.html" if s["blocks"].startswith("Q")
                                         else "flagged.html", s["blocks"], s["blocks"]))
            if s["blocks"] else "&mdash;"))
        for s in contentmod.SUGGESTIONS)
    return page("Suggestions", """
<div class="hero"><h1>Suggestions &mdash; choose before anything changes</h1>
<p class="lede">Nothing here has been applied. Each row is an option with the decision it needs from
you, what it costs, and how much work it is. Review them, pick the ones you want, and only then do they
get implemented.</p></div>

<div class="panel"><div class="tbl-scroll"><table><thead><tr>
<th class="num">ID</th><th>Suggestion</th><th>What it involves</th><th>What it decides</th>
<th>Cost</th><th>Effort</th><th>Unblocks</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>

<div class="panel"><h2>How to improve decision-making on this site</h2>
<ol class="tight">
<li><strong>Close the single-entry gap first.</strong> Everything else is refined guesswork until the
room states its re-entry policy in writing. One email. <a href="#S-01">S-01</a></li>
<li><strong>Replace modelled walk times with measured ones.</strong> The 30-minute rule is the user's
own priority, and right now it rests on an OpenStreetMap routing estimate. A Google Maps API key makes
it a measurement. <a href="#S-04">S-04</a></li>
<li><strong>Turn the monitor from page hashes into value changes.</strong> A hash change tells you a
page moved. Tracking the specific sentence each row was transcribed from tells you the buy-in changed.
<a href="#S-07">S-07</a></li>
<li><strong>Pick one quality authority.</strong> Cost and quality outrank distance in the brief, but
quality has no official source, so it is currently a blank column. <a href="#S-06">S-06</a></li>
<li><strong>Consolidate.</strong> Three scheduled monitor jobs and four overlapping dashboards are
still in the repository. <a href="#S-09">S-09</a>, <a href="#S-10">S-10</a></li>
</ol></div>
""" % dict(rows=rows), "suggestions.html")


def p_flagged(events):
    rows = "".join(
        "<tr id='%s'><td class='num'>%s</td><td>%s</td>"
        "<td><strong>%s</strong><div class='note'>%s</div></td>"
        "<td>%s</td><td>%s</td></tr>"
        % (esc(f["id"]), esc(f["id"]), esc(f["area"]), esc(f["title"]), esc(f["detail"]),
           esc(f["impact"]), srclink(f["source"]))
        for f in contentmod.FLAGS)
    rows += ("<tr id='F-QUOTE'><td>F-QUOTE</td><td>Hotels</td><td>Exact-date lookup returned a loading shell on %s.</td>"
             "<td>Checkout fields and quote timestamp are blank; no hotel can be ranked on this stay.</td><td>%s</td></tr>"
             "<tr id='F-WYNN'><td>F-WYNN</td><td>Wynn</td><td>January 2027 structures were a placeholder on %s.</td>"
             "<td>Schedule is published; no event promoted without written entry rules.</td><td>%s</td></tr>" %
             (decisions.READ, srclink(decisions.BOOKING, "Exact-date booking"), decisions.READ,
              srclink(decisions.WYNN_JAN_RULES, "January structures")))
    nh = len(hotelsmod.HOTELS)
    body = """
<div class="hero"><h1>Flagged for review</h1>
<p class="lede">Every value that could not be confirmed from an official source, and every irregularity
found in an official document. Nothing here blocks the site &mdash; it is the list of things you should
look at yourself, with the link to do it.</p></div>

<div class="banner"><strong>Two of these are defects in the official documents, not gaps in our
reading.</strong> <a href="#X-01">X-01</a>: the official schedule PDF prints a sponsor banner where the
date should be on twelve rows. <a href="#X-02">X-02</a>: the official series overview still calls an
ended series its &ldquo;Current Series&rdquo;.</div>

<div class="panel"><div class="tbl-scroll"><table><thead><tr>
<th class="num">ID</th><th>Area</th><th>Issue</th><th>Why it matters</th><th>Source to check</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>

<div class="panel"><h2>Blank cells on this site, in one list</h2>
<ul class="tight">
<li><strong>Single-entry confirmation</strong> &mdash; 0 of %(n)s events. No official sheet states one.
<a href="#F-01">F-01</a></li>
<li><strong>Finish times</strong> &mdash; 0 of %(n)s events. <a href="#F-04">F-04</a></li>
<li><strong>Dated hotel quotes</strong> &mdash; 0 of %(nh)s hotels. <a href="#F-05">F-05</a></li>
<li><strong>Cancellation deadlines</strong> &mdash; 0 of %(nh)s hotels. <a href="#F-06">F-06</a></li>
<li><strong>Official quality ratings</strong> &mdash; 0 of %(nh)s hotels.</li>
<li><strong>Measured walk times</strong> &mdash; 0 pairs. All are routing estimates.
<a href="#F-08">F-08</a></li>
<li><strong>Caesars Palace and Horseshoe resort fees</strong> &mdash; only a $45&ndash;$50 corporate
range is published, so no single value is entered.</li>
<li><strong>Room tax per property</strong> &mdash; the county rate is used, not a per-hotel figure.</li>
</ul></div>
""" % dict(rows=rows, n=len(events), nh=nh)
    return page("Flagged for review", body, "flagged.html")


def _monitored_urls():
    """Every URL scripts/recheck2026.py actually fetches, read from its source builder.

    Imported lazily: recheck2026 imports the same data modules build2026 does, so a
    top-level import would be circular. Falling back to an empty set keeps the page
    buildable if the monitor module is absent, and the sentence then describes only the
    register's own URLs.
    """
    try:
        import recheck2026
        return {url for _label, url in recheck2026.sources().values()}
    except Exception:  # noqa: BLE001 - a missing monitor must not stop the site building
        return set()


def monitored_sentence(registered, run_n):
    """The 'N URLs are monitored' sentence, reconciled with the run printed beside it.

    The register and the scheduled run can legitimately disagree: a URL added to the register
    after the last run is watched but has no baseline yet. Quoting one number beside the other
    without saying so made the page contradict itself (58 vs 61, then 63 vs 61). The sentence
    now either quotes a single agreed number, or states both and the gap between them.
    """
    if not run_n or registered == run_n:
        return ("%d URLs are monitored, including all 37 structure-sheet URLs." % registered)
    gap = registered - run_n
    if gap > 0:
        return ("%d URLs are registered for monitoring, including all 37 structure-sheet URLs. "
                "The latest run below fetched %d of them: %d were added to the register after "
                "that run and will be baselined by the next one."
                % (registered, run_n, gap))
    return ("%d URLs are registered for monitoring, including all 37 structure-sheet URLs. The "
            "latest run below fetched %d, which is %d more than this register lists."
            % (registered, run_n, -gap))


def p_sources(events):
    srcs = [dict(kind="Follow-up", name=label, url=url, date=decisions.READ,
                 use="Dated decision follow-up; see venue or checkout log.") for label, url in decisions.WATCH]
    srcs.append(dict(kind="Schedule", name="Venetian DSE IV schedule page",
                     url=sched.SCHEDULE_URL, date=RETRIEVED,
                     use="Dates, event numbers, event names, start times, structure-sheet links for all %d rows."
                         % len(sched.ROWS)))
    srcs.append(dict(kind="Schedule", name="Venetian DSE IV schedule PDF",
                     url=sched.SCHEDULE_PDF, date=RETRIEVED,
                     use="Registration-close times, chip counts, level lengths, guarantees and trophy tiers. "
                         "Note irregularity X-01."))
    for n in sorted(SHEETS):
        s = SHEETS[n]
        srcs.append(dict(kind="Structure sheet", name="Sheet %d \u2014 %s" % (n, s["title"]),
                         url=s["url"], date=decisions.READ if n in decisions.VENETIAN_SHEETS_REREAD else s.get("retrieved", RETRIEVED),
                         use="Events %s. Buy-in split, late registration, stack, level length, payout share, "
                             "and the re-entry / add-on / rebuy finding."
                             % ", ".join("#%d" % e for e in s["events"])))
    srcs.append(dict(kind="Series", name="DeepStack Poker Series overview", url=sched.SERIES_URL,
                     date=RETRIEVED, use="Series dates and the NYE / Showdown series that follow. "
                                         "Note irregularity X-02."))
    srcs.append(dict(kind="Venue", name="Venetian poker room", url=sched.POKER_ROOM_URL, date=RETRIEVED,
                     use="Room location, hours, table count, indoor walking routes, parking, contact details."))
    srcs.append(dict(kind="Hotel", name="Venetian resort fee", url="https://www.venetianlasvegas.com/resort/resort-fee.html",
                     date=RETRIEVED, use="$55 per night plus tax, and what it includes."))
    srcs.append(dict(kind="Hotel", name="Venetian poker suite rates",
                     url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html", date=RETRIEVED,
                     use="From $119 / $209, code EPOKR25, and the qualifying-play condition."))
    srcs.append(dict(kind="Hotel", name="Venetian hotel terms",
                     url="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
                     date="2026-11-16", use="Clark County room tax of 13.38%."))
    srcs.append(dict(kind="Tax", name="Clark County transient lodging tax guide",
                     url=contentmod.ROOM_TAX["source"], date="2026-11-16",
                     use="13.38% from the county's own published guide."))
    # The scheduled re-check watches every hotel fee/parking page the hotels dataset cites,
    # so those pages belong in this register too. Before this list existed the page said
    # "58 URLs are monitored" while the run summary on the same page said 61: the three
    # hotel fee pages below were watched but never listed, so a reader could not open them.
    for h in hotelsmod.HOTELS:
        for field, url in (("resort fee", h.get("resort_fee_src")), ("parking", h.get("parking_src")),
                           ("booking", h.get("book")), ("room tax", h.get("tax_src")),
                           ("cancellation", h.get("cancel_src")), ("poker offer", h.get("poker_rate_src"))):
            if url:
                srcs.append(dict(kind="Hotel", name="%s %s source" % (h["name"], field),
                                 url=url, date=str(h.get("retrieved") or ""),
                                 use="The %s this site publishes for %s." % (field, h["name"])))
    for v in contentmod.OTHER_VENUES:
        # the date is the one recorded on that venue's own reading; an unread room must not be
        # dated with this build's date just because its provenance text happens to say "session"
        _vdate = v.get("checked") or max([f["retrieved"] for f in v["earlier_findings"]
                                          if f.get("retrieved")] or ["2026-11-16"])
        srcs.append(dict(kind="Other venue", name=v["name"], url=v["url"],
                         date=_vdate, use=v["verdict"]))
        for f in v["earlier_findings"]:
            srcs.append(dict(kind="Other venue", name="%s \u2014 %s" % (v["name"], f["url"].rsplit("/", 1)[-1][:44]),
                             url=f["url"], date=f["retrieved"], use=f["text"]))
    rows = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td class='num'>%s</td><td class='note'>%s</td></tr>"
        % (esc(s["kind"]), esc(s["name"]), srclink(s["url"]), esc(s["date"]), esc(s["use"]))
        for s in srcs)
    urls = sorted({s["url"] for s in srcs if s["url"]})
    # The paragraph below sits directly above the run summary, so it must count the same thing
    # that summary counts. The re-check watches each hotel fee/parking page the hotels dataset
    # cites (some of those pages are not rows on this register); quoting only this register's
    # count beside a run that fetched more made the page contradict itself (58 vs 61 on the
    # 2026-11-17 run). The register rows above are the documents, one row per document used.
    monitored_n = len({u for u in _monitored_urls()} | set(urls))
    run_n = 0
    if CHECKS_META is None:
        monitor = ('<p class="note">This checkout carries no completed re-check run yet, so every row '
                   'shows <em>not yet checked</em> rather than an assumed-clean status. The first '
                   'scheduled run sets the baseline hash.</p>')
    else:
        run = (CHECKS_META.get("runs") or [{}])[0]
        # Count from the run's own per-URL results rather than from the summary fields.
        # The summary in a committed checks.json can predate a change in how it is computed
        # (the 2026-11-17 file recorded "never_checked: 51", which counted pages whose
        # baseline had *just* been established). The results list is the evidence.
        rows_ = run.get("results") or []
        first_check = sum(1 for r in rows_ if r.get("change") == "first check")
        changed_n = sum(1 for r in rows_ if r.get("change") == "CHANGED")
        err_n = sum(1 for r in rows_ if r.get("change") == "fetch error")
        ever = set()
        for past in CHECKS_META.get("runs") or []:
            for r in past.get("results") or []:
                if r.get("hash"):
                    ever.add(r.get("key"))
        never_read = sum(1 for r in rows_ if not r.get("hash") and r.get("key") not in ever)
        run_n = len(rows_)
        monitor = ('<p class="note">Latest recorded run: <strong>%s</strong> &mdash; %d URLs: '
                   '<strong>%d changed</strong>, %d fetch errors, %d whose baseline hash was set by that '
                   'run, %d that no run has ever read successfully. A fetch error is a monitoring '
                   'failure, not evidence that the document did not change.</p>'
                   % (esc(CHECKS_META.get("last_run") or run.get("checked") or "unknown"),
                      len(rows_) or CHECKS_META.get("monitored", 0), changed_n, err_n,
                      first_check, never_read))
    cov = ""
    if CHECKS_META:
        _run = (CHECKS_META.get("runs") or [{}])[0]
        _bad = [r for r in _run.get("results", []) if r.get("change") == "fetch error"]
        # An older checks.json (written before the fetch classified its failures) still has to be
        # read truthfully, so derive the kind from the status code rather than calling a documented
        # 403 "unreachable".
        _KIND = {401: "blocked", 403: "blocked", 429: "blocked", 301: "redirect-loop",
                 302: "redirect-loop", 303: "redirect-loop", 307: "redirect-loop",
                 404: "not found", 410: "not found", 451: "not found"}
        _MEAN = {"blocked": "the property's bot protection refused the runner; the page is live for a "
                            "person, so this value has to be re-read by hand",
                 "redirect-loop": "the host keeps redirecting without serving content (a cookie or "
                                  "region wall). Not evidence that the page moved",
                 "not found": "the official URL no longer serves a document - the citation itself "
                              "needs correcting",
                 "unreachable": "the fetch failed; nothing about the document is proven"}
        _rows = ""
        for r in _bad:
            kind = r.get("error_kind") or _KIND.get(r.get("status")) or "unreachable"
            note = r.get("reason") or _MEAN.get(kind) or _MEAN["unreachable"]
            if r.get("status") and int(r["status"]) >= 500:
                kind = "server error"
                note = "the official host returned 5xx. Retry before concluding anything"
            _rows += ("<tr><td>%s</td><td class='num'>%s</td><td>%s</td><td class='note'>%s</td></tr>"
                      % (srclink(r.get("url")), esc(r.get("status") or "no response"),
                         esc(kind), esc(note)))
        if _bad:
            cov = ('<div class="panel"><h2>What the scheduled monitor could not read</h2>'
                   '<p class="note">%d of %d cited documents could not be fetched in the latest run. '
                   'Those rows carry <em>no</em> fresh assurance: a source the runner cannot open is '
                   'not a source that has not changed. The value on the row keeps its own last '
                   'human-verified date, and the badge on the table says so. Open the link and read '
                   'it, or re-read it before any non-refundable payment.</p>'
                   '<table><thead><tr><th>Document</th><th class="num">HTTP</th><th>Failure kind</th>'
                   "<th>What that means</th></tr></thead><tbody>%s</tbody></table></div>"
                   % (len(_bad), CHECKS_META.get("monitored", len(_run.get("results", []))), _rows))
        else:
            cov = ('<div class="panel"><h2>What the scheduled monitor could not read</h2><p class="note">'
                   'Nothing: every cited document was fetched in the latest recorded run. That proves '
                   'reachability and a hash comparison, not that any transcription is correct.</p></div>')
    return page("Sources", """
<div class="hero"><h1>Source register</h1>
<p class="lede">Every document this site is built from, with the date it was read and what it was used
for. <strong>%(ndocs)s distinct document(s)</strong> behind %(n)s register rows. All of them are official
venue, operator or government pages &mdash; no
aggregator, no forum, no mapping service.</p></div>

<div class="panel"><h2>Scheduled re-check</h2>
<p>A GitHub Actions job (<code>.github/workflows/recheck.yml</code>) re-fetches every official URL on
this page every morning at 06:00 UTC, hashes the normalised text, and appends the run to
<code>data/verified2026/checks.json</code>. A changed hash is reported rather than guessed at &mdash;
the Tournaments table then marks that row's <em>Source re-check</em> cell as <em>source changed</em> so
you know which cited value may have moved. %(monitored_sentence)s A <em>fetch error</em> means the job
could not read the document &mdash; often a bot wall (HTTP 403) or a 302 redirect on a property that
restricts scripts &mdash; and it proves nothing either way; those rows keep their previous hash and
their old read date.</p>
%(monitor)s
<p class="note">The monitor currently detects that a page changed, not which value changed. Turning it
into per-sentence tracking is <a href="suggestions.html#S-07">S-07</a>.</p>
</div>

%(cov)s
<div class="panel"><div class="tbl-scroll"><table><thead><tr>
<th>Kind</th><th>Document</th><th>URL</th><th class="num">Retrieved</th><th>What it is used for</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>
""" % dict(rows=rows, n=len(srcs), ndocs=len({x["url"] for x in srcs if x["url"]}),
           monitored_sentence=monitored_sentence(monitored_n, run_n), monitor=monitor,
           cov=cov), "sources.html")


def p_repo_review(events):
    return page("Repo review", """
<div class="hero"><h1>Repo review, line by line</h1>
<p class="lede">What the repository contains today, what this session changed, and what is still lying
around from earlier sessions.</p></div>

<div class="panel"><h2>What this session did</h2>
<ol class="tight">
<li>Read the coordination board. Every prior task is marked <code>done</code>; no other session holds
an active claim.</li>
<li><strong>Read all 37 official Venetian structure sheets</strong>, one by one, covering all 64 event
numbers. This closes the gap that several earlier sessions logged as open (FG-03 / S-02: 27 sheets
unread).</li>
<li>Read the official schedule from both the HTML event page and the schedule PDF, and reconciled them
row by row. The PDF prints registration closes, chip counts and level lengths the HTML page does not.
Found irregularity <a href="flagged.html#X-01">X-01</a>.</li>
<li>Re-read the official poker-room page, resort-fee page and poker suite-rate page.</li>
<li>Checked seven other poker rooms and recorded what each publishes.</li>
<li>Rebuilt the site from that data.</li>
</ol></div>

<div class="panel"><h2>Files this session owns</h2>
<div class="tbl-scroll"><table><thead><tr><th>Path</th><th>What it is</th></tr></thead><tbody>
<tr><td class="mono">data/sheets/part1&ndash;6.py</td>
<td>Verified readings of all 37 official structure sheets. Every clause quoted, every sheet dated.</td></tr>
<tr><td class="mono">data/verified2026/schedule.py</td>
<td>All %(nrows)s official schedule rows, transcribed from the PDF and cross-checked against the HTML page.</td></tr>
<tr><td class="mono">data/verified2026/hotels.py</td>
<td>Hotel fields plus the dated rate log.</td></tr>
<tr><td class="mono">data/verified2026/content.py</td>
<td>Other venues, flags, questions, suggestions.</td></tr>
<tr><td class="mono">scripts/build2026.py</td>
<td>The generator. Every page and JSON file on this site comes from it, and nothing else writes them.</td></tr>
<tr><td class="mono">2026/assets/site2026.css, 2026/assets/site2026.js</td>
<td>The stylesheet and the search / filter / calculator logic.</td></tr>
</tbody></table></div></div>

<div class="panel"><h2>The site root is a separate, live surface</h2>
<p>The repository root serves an older multi-venue dashboard that another session is still
maintaining and regenerating from its own dataset (<code>data/master.json</code>) with its own
generator (<code>scripts/build_site.py</code>). It is <strong>not</strong> legacy: it is simply a
different surface with a different generator. This site lives under <code>/2026/</code> so the two
never overwrite each other, and every page here links back to the root. Nothing in
<code>/2026/</code> is derived from the root dashboard, and nothing on the root was edited to make
this site.</p></div>

<div class="panel"><h2>Legacy surfaces, still in the repository</h2>
<p>Four earlier sessions published overlapping dashboards inside their own directories. They are
still served so no existing link breaks, but they are superseded and are not maintained.</p>
<div class="tbl-scroll"><table><thead><tr><th>Path</th><th>Origin</th><th>Status</th></tr></thead><tbody>
<tr><td class="mono">docs/</td><td>arena/acd81e67-poker2</td><td>Superseded. Frozen.</td></tr>
<tr><td class="mono">verified/</td><td>earlier integration session</td><td>Superseded. Frozen.</td></tr>
<tr><td class="mono">pages/</td><td>arena/f743ae5a-poker2</td><td>Superseded. Frozen.</td></tr>
<tr><td class="mono">plan/</td><td>arena/72ca3e9d-poker2</td><td>Superseded. Frozen.</td></tr>
<tr><td class="mono">archive/</td><td>multiple</td><td>Archives of earlier session trees.</td></tr>
<tr><td class="mono">data/*.json, data/site/*.json, site-data/*.json</td>
<td>multiple earlier sessions</td><td>Retained for audit. Not used by this site.</td></tr>
</tbody></table></div>
<p class="note">Whether to delete these is your call: <a href="suggestions.html#S-09">S-09</a>.</p></div>

<div class="panel"><h2>Irregularities found in the repository</h2>
<ul class="tight">
<li><strong>Three overlapping scheduled monitor jobs</strong> &mdash; <code>recheck.yml</code>,
<code>source-monitor.yml</code> and the <code>plan-*.yml</code> jobs all re-check the same official URLs
on different cron schedules. <a href="suggestions.html#S-10">S-10</a></li>
<li><strong>Three overlapping generators</strong> for superseded surfaces &mdash;
<code>scripts/build.py</code>, <code>scripts/build_site.py</code> and
<code>scripts/build-site.py</code>. Only <code>build2026.py</code> writes the live pages.</li>
<li><strong>Stale claims on the board.</strong> Earlier records say &ldquo;no Venetian sheet prints a
re-entry clause.&rdquo; That is now known to be wrong for sheet 8, which prices subsequent buy-ins, and
incomplete for the multi-flight sheets, which print a flight rule. Per-sheet silence is not
series-wide silence.</li>
<li><strong>The &ldquo;earliest verified start&rdquo; claim.</strong> Earlier records say 10:10 AM.
That is right for main-schedule events, but satellite event 46 starts at 9:10 AM. Neither is 8 AM.</li>
</ul></div>
""" % dict(nrows=len(sched.ROWS)), "repo-review.html")


JS = r"""
(function(){
  'use strict';
  var $=function(s){return document.querySelector(s)};
  var $$=function(s){return Array.prototype.slice.call(document.querySelectorAll(s))};

  function text(tr){return (tr.getAttribute('data-search')||'')+' '+tr.textContent.toLowerCase();}

  function vegasDate(){
    var parts=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
    var date={}; parts.forEach(function(part){date[part.type]=part.value;});
    return date.year+'-'+date.month+'-'+date.day;
  }

  // ---- tournaments table -------------------------------------------------
  var t=$('#t');
  if(t){
    var q=$('#q'), df=$('#datef'), mbi=$('#maxbi'), sef=$('#sef'), ng=$('#nogtd'), cnt=$('#count');
    var pills=$$('.pill[data-g]'), until=$('#date-to'), past=$('#include-past');
    var today=vegasDate();
    if(/^#ev\d+$/.test(location.hash)) past.checked=true;  // Index links can cite historical rows.
    var activeGroups={};
    function run(){
      var s=(q.value||'').toLowerCase().trim();
      var d=df.value, mb=mbi.value?parseInt(mbi.value,10):null;
      var rows=$$('#t tbody tr'), shown=0;
      rows.forEach(function(tr){
        var ok=true;
        if(s && text(tr).indexOf(s)===-1) ok=false;
        function matches(date){return (!d||date>=d)&&(!until.value||date<=until.value)&&(past.checked||date>=today);}
        if(!(tr.getAttribute('data-dates')||'').split(' ').some(matches)) ok=false;
        tr.querySelectorAll('.slot').forEach(function(slot){slot.hidden=!matches(slot.getAttribute('data-slot-date'));});
        if(ok && mb!==null){var b=parseInt(tr.getAttribute('data-buyin')||'0',10); if(!b||b>mb) ok=false;}
        if(ok && sef.checked && tr.getAttribute('data-confirmed')!=='1') ok=false;
        if(ok && ng.checked && !(parseInt(tr.getAttribute('data-gtd')||'0',10)>0)) ok=false;
        if(ok && Object.keys(activeGroups).length && !activeGroups[tr.getAttribute('data-group')]) ok=false;
        tr.classList.toggle('hidden',!ok);
        if(ok) shown++;
      });
      cnt.textContent=shown+' of '+rows.length+' events shown.'+(sef.checked&&!shown?' No events meet the confirmed freezeout filter.':'');
    }
    [q,df,until,past,mbi,sef,ng].forEach(function(el){ el.addEventListener('input',run); el.addEventListener('change',run); });
    pills.forEach(function(p){p.addEventListener('click',function(){
      var g=p.getAttribute('data-g');
      if(activeGroups[g]) delete activeGroups[g]; else activeGroups[g]=1;
      p.classList.toggle('on'); run();
    });});
    $('#reset').addEventListener('click',function(){
      q.value=''; df.value=''; until.value=''; past.checked=false; mbi.value=''; sef.checked=false; ng.checked=false;
      activeGroups={}; pills.forEach(function(p){p.classList.remove('on')}); run();
    });
    $$('#t th').forEach(function(th,i){
      th.addEventListener('click',function(){
        var body=t.tBodies[0], rows=$$('#t tbody tr');
        var num=th.classList.contains('num');
        rows.sort(function(a,b){
          var x=a.cells[i].textContent.trim(), y=b.cells[i].textContent.trim();
          if(num){x=parseFloat(x.replace(/[^0-9.\-]/g,''))||0;y=parseFloat(y.replace(/[^0-9.\-]/g,''))||0;
                  return x-y;}
          return x.localeCompare(y);
        });
        if(th.getAttribute('data-desc')==='1'){rows.reverse(); th.setAttribute('data-desc','0');}
        else th.setAttribute('data-desc','1');
        rows.forEach(function(r){body.appendChild(r)});
      });
    });
    run();
  }

  // ---- schedule page -----------------------------------------------------
  if($('#df')){
    var df2=$('#df'), ov=$('#ov'), c2=$('#c'), panels=$$('.panel[data-date]');
    function run2(){
      var d=df2.value, shown=0;
      panels.forEach(function(p){
        var ok=true;
        if(d && p.getAttribute('data-date')!==d) ok=false;
        if(ok && ov.checked && p.getAttribute('data-multiple')!=='1') ok=false;
        p.style.display=ok?'':'none';
        if(ok) shown++;
      });
      c2.textContent=shown+' of '+panels.length+' days shown.';
    }
    df2.addEventListener('change',run2); ov.addEventListener('change',run2); run2();
  }

  // ---- walking page ------------------------------------------------------
  if($('#v')){
    var v=$('#v'), w30=$('#w30'), w15=$('#w15'), wc=$('#wc'), maps=$('#maps-evidence');
    var prs=$$('.panel[data-venue]'), all=$$('.panel[data-venue] tbody tr');
    function run3(){
      var vv=v.value, shown=0, shownp=0;
      prs.forEach(function(p){
        var pok=(!vv||p.getAttribute('data-venue')===vv);
        p.style.display=pok?'':'none';
        if(pok) shownp++;
      });
      all.forEach(function(tr){
        var m=parseFloat(tr.getAttribute('data-min'));
        var ok=(!vv||tr.closest('.panel').getAttribute('data-venue')===vv);
        if(ok && w30.checked && !(m<=30)) ok=false;
        if(ok && w15.checked && !(m<=15)) ok=false;
        if(ok && maps.checked && tr.getAttribute('data-maps')!=='1') ok=false;
        tr.classList.toggle('hidden',!ok);
        if(ok) shown++;
      });
      wc.textContent=shown+' of '+all.length+' hotel\u2013room pairs shown ('+shownp+' rooms).';
    }
    [v,w30,w15,maps].forEach(function(el){el.addEventListener('change',run3)});
    run3();
  }

  function fmt(n){return n==null?'\u2014':n.toLocaleString('en-US',{style:'currency',currency:'USD'});}
  function hotelCost(H){
    function read(el){return el.value!==''&&el.validity.valid ? Number(el.value) : null;}
    var r=read(H.r), f=read(H.f), t=read(H.t), p=read(H.p), n=read(H.n);
    var sub=r!=null&&f!=null?r+f:null;
    var tax=sub!=null&&t!=null?sub*t/100:null;
    var night=tax!=null&&p!=null?sub+tax+p:null;
    return {sub:sub,tax:tax,night:night,total:n===0?0:night!=null&&n!=null?night*n:null};
  }

  // ---- hotels calculator -------------------------------------------------
  if($('#h-rate')){
    var H={r:$('#h-rate'),f:$('#h-fee'),t:$('#h-tax'),p:$('#h-park'),n:$('#h-nights')};
    var o={s:$('#o-sub'),x:$('#o-tax'),nn:$('#o-night'),tt:$('#o-total')};
    var note=$('#h-note');
    function run4(){
      var est=hotelCost(H);
      o.s.textContent=fmt(est.sub); o.x.textContent=fmt(est.tax);
      o.nn.textContent=fmt(est.night); o.tt.textContent=fmt(est.total);
      note.textContent=est.total==null?'No total until all inputs, including the nightly room rate, are known.':'Illustrative estimate only, not a checkout quote.';
    }
    Object.keys(H).forEach(function(k){H[k].addEventListener('input',run4)});
    run4();
  }

  // ---- single-room walking table (venue pages) --------------------------
  var rw=$('#w30[data-walk-room]');
  if(rw){
    var rt=document.getElementById('wt-'+rw.getAttribute('data-walk-room'));
    var rwc=document.getElementById('wc');
    function runRoom(){
      var rows=rt.tBodies[0].rows, n=0;
      Array.prototype.forEach.call(rows,function(tr){
        var m=parseFloat(tr.getAttribute('data-min'));
        var ok=!rw.checked||(m<=30);
        tr.classList.toggle('hidden',!ok); if(ok)n++;
      });
      rwc.textContent=n+' of '+rows.length+' hotels shown.';
    }
    rw.addEventListener('change',runRoom); runRoom();
  }

  // ---- site-wide search across every table on every page ----------------
  function pagePrefix(){
    // venues/*.html sits one level down
    return location.pathname.indexOf('/venues/') !== -1 ? '../' : '';
  }
  var box=$('#gs'), res=$('#gs-res'), stat=$('#gs-status');
  if(box && window.SEARCH_INDEX){
    var IDX=window.SEARCH_INDEX, LIMIT=40;
    function esc(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML;}
    function runSearch(){
      var q=(box.value||'').toLowerCase().trim();
      if(!q){res.innerHTML='';stat.textContent=IDX.length+' rows indexed across every table on the site.';return;}
      var terms=q.split(/\s+/), hits=[];
      for(var i=0;i<IDX.length;i++){
        // search the table label, the row heading and every cell, not just the caption
        var r=IDX[i], hay=(r.t+' '+r.h+' '+(r.x||'')).toLowerCase(), ok=true;
        for(var j=0;j<terms.length;j++){ if(hay.indexOf(terms[j])===-1){ok=false;break;} }
        if(ok) hits.push(r);
      }
      var byPage={};
      hits.forEach(function(h){ (byPage[h.p]=byPage[h.p]||[]).push(h); });
      var html='';
      Object.keys(byPage).forEach(function(pg){
        html+='<div class="gs-group"><h3><a href="'+pagePrefix()+pg+'">'+esc(byPage[pg][0].pl)+'</a>'
             +' <span class="note">'+byPage[pg].length+' match'+(byPage[pg].length===1?'':'es')+'</span></h3><ul class="tight">';
        byPage[pg].slice(0,LIMIT).forEach(function(h){
          html+='<li><a href="'+pagePrefix()+pg+(h.a?'#'+h.a:'')+'">'+esc(h.h)+'</a>'
               +' <span class="note">'+esc(h.t.slice(0,180))+'</span></li>';
        });
        if(byPage[pg].length>LIMIT) html+='<li class="note">&hellip; '+(byPage[pg].length-LIMIT)+' more in this table</li>';
        html+='</ul></div>';
      });
      res.innerHTML=html;
      stat.textContent=hits.length+' row'+(hits.length===1?'':'s')+' match \u201c'+box.value.trim()+'\u201d'
        +' in '+Object.keys(byPage).length+' table'+(Object.keys(byPage).length===1?'':'s')+'.';
    }
    box.addEventListener('input',runSearch);
    var clr=$('#gs-clear');
    if(clr) clr.addEventListener('click',function(){box.value='';runSearch();box.focus();});
    runSearch();
  }

  // ---- trip calculator ---------------------------------------------------
  if($('#pick')){
    var pick=$('#pick'), body=$('#cart').tBodies[0];
    var checkout=$('#t-checkout'), nights=$('#t-nights');
    function setCost(selector, amount){
      $(selector).textContent=amount===null?'Not available':amount.toLocaleString('en-US',{style:'currency',currency:'USD'});
    }
    function recalc(){
      var buyin=0,pool=0;
      $$('#cart tbody tr').forEach(function(tr){
        buyin+=parseFloat(tr.getAttribute('data-buyin'))||0;
        pool+=parseFloat(tr.getAttribute('data-pool'))||0;
      });
      var n=nights.valueAsNumber, quote=checkout.valueAsNumber;
      var valid=Number.isInteger(n)&&n>0&&Number.isFinite(quote)&&quote>=0&&checkout.validity.valid;
      var hotel=n===0?0:valid?quote:null;
      setCost('#sum-buyin',buyin);
      setCost('#sum-pool',pool);
      setCost('#tot-buyin',buyin);
      setCost('#tot-night',valid?quote/n:null);
      setCost('#tot-hotel',hotel);
      setCost('#tot-all',hotel===null?null:buyin+hotel);
    }
    $('#add').addEventListener('click',function(){
      var o=pick.options[pick.selectedIndex]; if(!o||!o.value) return;
      if(body.querySelector('[data-event="'+o.value+'"]')) return;
      var tr=document.createElement('tr');
      tr.setAttribute('data-event',o.value);
      tr.setAttribute('data-buyin',o.getAttribute('data-buyin'));
      tr.setAttribute('data-pool',o.getAttribute('data-pool')||'0');
      tr.innerHTML='<td class="num">'+o.value+'</td><td>'+o.textContent+'</td>'
        +'<td class="num">'+fmt(+o.getAttribute('data-buyin'))+'</td>'
        +'<td class="num">'+(o.getAttribute('data-pool')?fmt(+o.getAttribute('data-pool')):'\u2014')+'</td>'
        +'<td><button class="btn del">remove</button></td>';
      tr.querySelector('.del').addEventListener('click',function(){tr.remove();recalc()});
      body.appendChild(tr); recalc();
    });
    [checkout,nights].forEach(function(input){input.addEventListener('input',recalc)});
    recalc();
  }
})();
"""


# --------------------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------------------

SEARCH_INDEX = []


def _strip_tags(t):
    t = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def _row_label(raw_cells):
    """Pick the cell that identifies a row for the search results.

    Skips cells that carry only a status tag ("Multi-flight") or only a source link
    ("confirm on Google Maps") - they are not a name a reader can usefully click - and takes the
    first remaining cell with real text.
    """
    vals = []
    for raw in raw_cells:
        inner = re.sub(r"(?is)<span[^>]*class=[\"'][^\"']*\btag\b[^>]*>.*?</span>", " ", raw)
        txt = _strip_tags(inner)
        if re.fullmatch(r"(confirm on google maps|sheet \d+|county source|no sheet)", txt.strip(), re.I):
            continue
        vals.append(txt)
    for v in vals:
        if len(v) > 3 and not re.fullmatch(r"[\d\s.,%$\u00d7-]+", v):
            return v[:120]
    return (vals[0] if vals else "")[:120]


def build_search_index(pages):
    """One entry per table row, per table, per page - so the search box covers every table."""
    idx = []
    for path, text in pages.items():
        for tm in re.finditer(r"(?is)<table([^>]*)>(.*?)</table>", text):
            attrs, table = tm.group(1), tm.group(2)
            tid = re.search(r"id=[\"']([^\"']+)", attrs)
            tid = tid.group(1) if tid else ""
            cap = re.search(r"(?is)<caption>(.*?)</caption>", table)
            heads = [_strip_tags(h) for h in re.findall(r"(?is)<th[^>]*>(.*?)</th>", table)]
            for tr in re.findall(r"(?is)<tr([^>]*)>(.*?)</tr>", table):
                row_attrs, cells = tr
                tds = re.findall(r"(?is)<td[^>]*>(.*?)</td>", cells)
                if not tds:
                    continue
                vals = [_strip_tags(c) for c in tds]
                label = path.replace(".html", "")
                idx.append(dict(
                    p=path,
                    pl=PAGE_LABEL.get(path, label),
                    t=tid,
                    a=(re.search(r"id=[\"']([^\"']+)", row_attrs) or [None, ""])[1]
                      if re.search(r"id=[\"']([^\"']+)", row_attrs) else "",
                    # heading = the first cell that carries enough text to identify the row;
                    # a leading row-number cell ("1") is not a useful label to click on.
                    h=_row_label(tds),
                    x=" | ".join(vals)[:400],
                ))
                idx[-1]["t"] = " ".join([tid, cap and _strip_tags(cap.group(1)) or "",
                                         " ".join(heads[:4])]).strip()
    return idx


def write(path, text):
    full = os.path.join(ROOT, SITE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    check = "--check" in sys.argv
    dest = ROOT
    tmp = None
    if check:
        tmp = tempfile.mkdtemp(prefix="build2026-")
        dest = tmp

    events = build_events()
    days = build_days(events)

    # fail the build if any rendered row lacks an official source
    for e in events:
        if not e["sheet_url"]:
            raise SystemExit("event #%d has no structure sheet URL" % e["event_no"])
        host = re.sub(r"^https?://", "", e["sheet_url"]).split("/")[0]
        if host not in OFFICIAL_HOSTS:
            raise SystemExit("event #%d cites a non-official host: %s" % (e["event_no"], host))
    covered = sorted({e for s in SHEETS.values() for e in s["events"]})
    uncovered = [e["event_no"] for e in events if e["event_no"] not in covered]
    if uncovered:
        raise SystemExit("events with no structure sheet read: %s" % uncovered)

    pages = {
        "index.html": p_index(events, days),
        "tournaments.html": p_tournaments(events),
        "entry-rules.html": p_rules(events),
        "schedule.html": p_schedule(days, events),
        "hotels.html": p_hotels(),
        "walking.html": p_walking(),
        "trip.html": p_trip(events),
        "venues.html": p_venues(events),
        "venues/venetian.html": p_venue_venetian(events, days),
        "venues/other.html": p_venue_other(),
        "venues/wynn.html": p_venue_room("wynn", events),
        "venues/horseshoe.html": p_venue_room("horseshoe", events),
        "venues/caesars-palace.html": p_venue_room("caesars-palace", events),
        "venues/bellagio.html": p_venue_room("bellagio", events),
        "venues/mgm-grand.html": p_venue_room("mgm-grand", events),
        "summary.html": p_summary(events, days),
        "questions.html": p_questions(),
        "suggestions.html": p_suggestions(),
        "flagged.html": p_flagged(events),
        "sources.html": p_sources(events),
        "repo-review.html": p_repo_review(events),
    }

    # ---- site-wide search index: every row of every table we just rendered ----
    global SEARCH_INDEX
    SEARCH_INDEX = build_search_index(pages)

    if not check:
        os.makedirs(ASSETS, exist_ok=True)
        with open(os.path.join(ASSETS, "site2026.css"), "w", encoding="utf-8") as f:
            f.write(CSS)
        with open(os.path.join(ASSETS, "site2026.js"), "w", encoding="utf-8") as f:
            f.write(JS)
        # The search index is a committed artefact so the page needs no fetch: it ships with the
        # site and is regenerated only by this build, which CI then diff-checks.
        with open(os.path.join(ASSETS, "search-index.js"), "w", encoding="utf-8") as f:
            f.write("window.SEARCH_INDEX = "
                    + json.dumps(SEARCH_INDEX, ensure_ascii=False, separators=(",", ":"))
                    + ";\n")
        os.makedirs(OUT_DATA, exist_ok=True)
        with open(os.path.join(OUT_DATA, "search-index.json"), "w", encoding="utf-8") as f:
            json.dump(SEARCH_INDEX, f, indent=1)
        for p, text in pages.items():
            write(p, text)
        # machine-readable dataset
        dump = dict(
            as_of=RETRIEVED,
            generated_by="scripts/build2026.py",
            series=dict(name="DeepStack Extravaganza IV",
                        dates="2026-11-16 to 2026-12-23",
                        schedule_url=sched.SCHEDULE_URL,
                        schedule_pdf=sched.SCHEDULE_PDF,
                        series_url=sched.SERIES_URL,
                        poker_room_url=sched.POKER_ROOM_URL),
            counts=dict(events=len(events), schedule_rows=len(sched.ROWS),
                        sheets_read=len(SHEETS), days=len(days),
                        confirmed_single_entry=sum(e["single_entry_confirmed"] for e in events)),
            quote_log=decisions.QUOTE_LOG,
            room_tax_pct=contentmod.ROOM_TAX["value"],
            events=[{k: v for k, v in e.items() if k != "rows"} for e in events],
            days=[{k: (v if k not in ("primary", "fallbacks", "restricted_alternatives") else
                       (v if k == "primary" else
                        [dict(note=f["note"], verdict=f["verdict"], **f["item"]) for f in v]
                        if k == "fallbacks" else v))
                   for k, v in d.items()} for d in days],
            hotels=hotelsmod.HOTELS,
            rate_log=[dict(date=a, property=b, field=c, value=d, source=e, note=f)
                      for a, b, c, d, e, f in hotelsmod.RATE_LOG],
            flags=contentmod.FLAGS,
            questions=contentmod.QUESTIONS,
            suggestions=contentmod.SUGGESTIONS,
            other_venues=contentmod.OTHER_VENUES,
            sheets=[{k: v for k, v in SHEETS[n].items()} for n in sorted(SHEETS)],
        )
        os.makedirs(OUT_DATA, exist_ok=True)
        with open(os.path.join(OUT_DATA, "dataset.json"), "w", encoding="utf-8") as f:
            json.dump(dump, f, indent=1, sort_keys=False)
        print("wrote %d pages, %d events, %d days, %d sheets"
              % (len(pages), len(events), len(days), len(SHEETS)))
    else:
        # check mode: compare generated text against what is committed
        bad = []
        for p, text in pages.items():
            full = os.path.join(ROOT, SITE, p)
            if not os.path.exists(full):
                bad.append(p + " (missing)")
                continue
            with open(full, encoding="utf-8") as f:
                if f.read() != text:
                    bad.append(p)
        if bad:
            raise SystemExit("committed pages differ from the data: " + ", ".join(bad))
        print("OK: every page matches the verified data")

    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
