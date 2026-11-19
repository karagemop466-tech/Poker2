#!/usr/bin/env python3
"""Build the Las Vegas single-entry poker trip site from verified official sources.

Every value rendered by this script comes from an official document that was read and
transcribed by hand. A value the organiser does not publish is rendered as an empty cell and
is listed on flagged.html. The build fails if a rendered row would carry no official source.

    python3 scripts/build2026.py            # regenerate every page and JSON file
    python3 scripts/build2026.py --check    # regenerate to a temp dir and diff (CI)
"""
from __future__ import annotations

from itertools import combinations

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
import decision as decisions
import review_20261119 as fresh
import content as contentmod                              # noqa: E402
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


def event_sources(event):
    return (sched.SCHEDULE_URL, sched.SCHEDULE_PDF, *event["sheet_urls"])


def source_state():
    import recheck2026
    runs = (CHECKS_META or {}).get("runs", [])
    state = recheck2026.source_state(runs, (CHECKS_META or {}).get("source_state"), recheck2026.reviewed_hashes())
    return ({u: row.get("changed_at") or "date unknown" for u, row in state.items() if row.get("review_required")},
            {u: row.get("last_success") for u, row in state.items()})


PENDING, LAST_FETCH = source_state()
SITE = "2026"  # the consolidated surface lives under /2026/ so it never clobbers
              # the root dashboard owned by another session (see COORDINATION.md, S-11)
ASSETS = os.path.join(ROOT, SITE, "assets")

OFFICIAL_HOSTS = {
    "www.venetianlasvegas.com": "The Venetian Resort Las Vegas (official)",
    "reservations.wynnlasvegas.com": "Wynn official booking engine",
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


def sheet_retrieved(sheet):
    return decisions.READ if sheet["sheet"] in decisions.VENETIAN_SHEETS_REREAD else sheet["retrieved"]


def confirmed_freezeout(sheet):
    """Require positive, attributed whole-event evidence; silence never passes."""
    if not sheet or not sheet.get("url") or not sheet.get("retrieved"):
        return False
    policy = sheet.get("entry_policy") or {}
    cap = policy.get("max_entries")
    return (type(cap) is int and cap == 1 and policy.get("scope") == "whole event"
            and all(policy.get(field) is False for field in ("reentry", "rebuy", "addon", "paid_advantage"))
            and bool((policy.get("quote") or "").strip()))


def rule_evidence(sheet):
    if not sheet:
        return {}
    evidence = {}
    for field in ("single_entry", "reentry", "rebuy", "addon", "fee"):
        status = sheet.get(field)
        if field == "single_entry":
            value = True if confirmed_freezeout(sheet) else None
        else:
            value = None if isinstance(status, str) and status.startswith("silent") else status
        excerpt = sheet.get(field + "_quote")
        if field == "single_entry" and value:
            excerpt = sheet["entry_policy"]["quote"]
        if field == "reentry" and not excerpt:
            excerpt = sheet.get("flight_rule")
        evidence[field] = dict(value=value, excerpt=excerpt, source=sheet["url"],
                               retrieved=sheet_retrieved(sheet))
    return evidence


def flight_letter(row):
    """The flight letter in an official row title such as \"... 1A\", else None."""
    fm = re.search(r"\b1([A-Z])\b", row[8])
    return fm.group(1) if fm else None


def per_flight(entry_rows, value_of):
    """One value for the event when every flight agrees; otherwise each distinct value with the
    flights that print it. A multi-flight event can have different late-registration closes and
    level lengths per flight (e.g. Event 1: flights A and C close at ~3:40 PM on 40-minute levels,
    flights B and D at ~8:40 PM on 30-minute levels). Each value comes from the structure sheet the
    official schedule links for that row, never from a single representative sheet."""
    groups = {}
    for r in entry_rows:
        v = value_of(r)
        if v in (None, ""):
            continue
        groups.setdefault(v, []).append(flight_letter(r))
    if not groups:
        return None
    if len(groups) == 1:
        return next(iter(groups))
    parts = []
    for v, letters in groups.items():
        named = sorted({x for x in letters if x})
        tag = ("flight%s %s" % ("s" if len(named) > 1 else "", ", ".join(named))) if named else "some entries"
        parts.append("%s: %s" % (tag, v))
    return "; ".join(parts)


def build_events():
    by_event = {}
    for r in sched.ROWS:
        by_event.setdefault(r[2], []).append(r)
    events = []
    for ev_no in sorted(by_event):
        rows = sorted(by_event[ev_no], key=lambda r: (r[0], tminutes(r[3]) or 0))
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
            single_entry_confirmed=confirmed_freezeout(sheet) and group != "spend",
            reason=reason,
            dates=sorted({r[0] for r in entry_rows}),
            all_dates=[r[0] for r in rows],
            starts=starts,
            entry_slots=[(r[0], r[3]) for r in entry_rows],
            sheet_urls=sorted({SHEETS[r[9]]["url"] for r in rows}),
            schedule_url=sched.SCHEDULE_URL,
            first_date=entry_rows[0][0] if entry_rows else rows[0][0],
            reg_close=(per_flight(entry_rows, lambda r: r[4]) or ""),
            chips=entry_rows[0][6] if entry_rows else None,
            level=(per_flight(entry_rows, lambda r: r[7]) or ""),
            buy_in=buy_in,
            fee=sheet.get("fee") if sheet else None,
            pool_per_entry=sheet.get("pool_per_entry") if sheet else None,
            fee_quote=(sheet.get("fee_quote") if sheet else None),
            gtd=gtd,
            gtd_note=(gtd_note or None),
            gtd_text=(sheet.get("guarantee") if sheet else (gtds[0] if len(gtds) == 1 else None)),
            ratio=round(gtd / buy_in, 1) if (gtd and buy_in and sheet.get("fee") is not None
                                             and group not in ("satellite", "team")
                                             and not demographic_gate(sheet)) else None,
            bounty=(sheet.get("bounty") if sheet else None),
            bounty_flag=None,
            reentry=(sheet.get("reentry") if sheet else "not read"),
            addon=(sheet.get("addon") if sheet else "not read"),
            rebuy=(sheet.get("rebuy") if sheet else "not read"),
            flight_rule=(sheet.get("flight_rule") if sheet else None),
            eligibility=(sheet.get("eligibility") if sheet else None),
            late_reg=(per_flight(entry_rows, lambda r: (SHEETS.get(r[9]) or {}).get("late_reg"))
                      or (sheet.get("late_reg") if sheet else None)),
            payout_pct=(sheet.get("payout_pct") if sheet else None),
            verified_on=sheet_retrieved(sheet) if sheet else None,
            last_checked=sheet_retrieved(sheet) if sheet else None,
            schedule_verified_on=sched.RETRIEVED,
            rule_evidence=rule_evidence(sheet),
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


def choose_primary(entries):
    """Only written-policy matches that need no assumed demographic eligibility."""
    eligible = [x for x in entries if x["single_entry_confirmed"] and not demographic_gate(x)]
    return min(eligible, default=None, key=lambda x: (x["start_m"], x["event_no"]))


def sequence(first, second):
    """Compare in start order. Minutes may extend beyond midnight for a verified finish."""
    start, cutoff = first["start_m"], second["reg_close_m"]
    finish = first.get("finish_m")
    if cutoff is None:
        return "unknown", "No official registration cutoff for the later entry."
    if cutoff <= start or (finish is not None and finish >= cutoff):
        return "cannot be sequenced", "The later entry closes before the first can be completed."
    if finish is not None and finish < second["start_m"]:
        return "no published overlap", "The first is scheduled to finish before the second starts."
    return ("conditional fallback", "Only enter the later event if out of the earlier one and able to "
            "register before %s. A registration window is not a finish time." % second["reg_close"])


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
                buy_in=ev["buy_in"], gtd=ev["gtd"], sheet_url=ev["sheet_url"],
                eligibility=ev.get("eligibility"),
                single_entry_confirmed=ev["single_entry_confirmed"],
                schedule_sheet_url=SHEETS[r[9]]["url"],
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
                buy_in=None, gtd=None, sheet_url=ev["sheet_url"],
                date=r[0], dow=r[1], restart=True,
            ))
    out = []
    for d in sorted(days):
        entries = sorted([x for x in days[d] if not x.get("restart")], key=lambda x: x["start_m"] or 0)
        restarts = sorted([x for x in days[d] if x.get("restart")], key=lambda x: x["start_m"] or 0)
        primary = choose_primary(entries)
        pairs = []
        for first, second in combinations(entries, 2):
            if first["event_no"] == second["event_no"]:
                verdict, note = "same event", "A second flight is not a separate tournament."
            else:
                verdict, note = sequence(first, second)
            pairs.append(dict(first=first, second=second, note=note, verdict=verdict))
        fallbacks = [dict(item=p["second"], note=p["note"], verdict=p["verdict"])
                     for p in pairs if p["first"] is primary and p["second"]["single_entry_confirmed"]
                     and not demographic_gate(p["second"]) and p["verdict"] == "conditional fallback"][:1]
        # Events a player who meets the condition could play, which are never promoted to primary
        # because they are restricted. Shown explicitly so an age-restricted morning event is not
        # silently dropped from the day.
        restricted_alts = [x for x in entries if demographic_gate(x)
                           and (primary is None or x["event_no"] != primary["event_no"])]
        out.append(dict(date=d, dow=entries[0]["dow"] if entries else (restarts[0]["dow"] if restarts else ""),
                        entries=entries, restarts=restarts, primary=primary, fallbacks=fallbacks,
                        restricted_alternatives=restricted_alts, pairs=pairs,
                        overlap=any(p["verdict"] != "no published overlap" for p in pairs)))
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
    ("latest-review.html", "Latest evidence"),
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
tr.hidden,.slot[hidden]{display:none}
.slot{display:block}
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
empty and listed on <a href="flagged.html">Flagged for review</a>. Routing and cost estimates are
labeled separately. Core structure-sheet audit: %s.</p>
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
    changed = [PENDING[u] for u in urls if u in PENDING]
    differences = [h["schedule_diff"] for h in hits if (h.get("schedule_diff") or {}).get("state") == "rows differ"]
    if changed or differences:
        suffix = " since " + max(changed)[:10] if changed else ""
        return "<span class='tag t-bad' title='Change awaits verification against the official source%s'>source changed</span>" % esc(suffix)
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
    if any((h.get("schedule_diff") or {}).get("state") == "unreadable schedule table" for h in hits):
        return "<span class='tag t-warn'>official schedule table unreadable</span>"
    if any(u not in CHECKS for u in urls):
        return "<span class='tag t-info'>partial monitor coverage</span>"
    if all(h.get("change") == "first check" for h in hits):
        return "<span class='tag t-info'>baseline set</span>"
    return "<span class='tag t-ok'>unchanged</span>"


def row_changed(*urls):
    """True when any source behind a row still needs review."""
    return any(u in PENDING or (CHECKS.get(u, {}).get("schedule_diff") or {}).get("state") == "rows differ"
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
        ("Structure sheets read", len(SHEETS), "all 37 transcribed on %s; 9 candidate sheets re-read on %s" % (RETRIEVED, decisions.READ)),
        ("Confirmed single-entry", 0, "no audited sheet states a one-entry rule &mdash; see F-01"),
        ("Best candidates", len(cands), "%d open to players 21+ with a Venetian Rewards card (printed rule 2), %d restricted by the sheet (age or gender); one-day, "
         "no bounty, no re-entry/add-on clause printed" % (len(cands_open), len(restricted))),
        ("Comparable hotel quotes", 0, "no verified total for the same stay &mdash; see hotels"),
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
<p class="lede">Compare Las Vegas poker schedules and hotel costs using linked official sources.
Keep a clear distinction between written entry rules, route estimates and unverified prices.</p>
<p class="lede"><strong>No reviewed event meets the strict freezeout policy.</strong> All 37 official
Venetian DeepStack IV structure sheets were transcribed on %(ret)s, and the nine sheets behind the research candidates were re-read on %(reread)s and still match. A sheet that is silent on re-entry,
rebuy and add-on is a research lead, not a booking recommendation.</p>
</div>
<div class="cards">%(cards)s</div>

<div class="banner info"><strong>Start here.</strong>
<a href="tournaments.html">Tournaments</a> starts with confirmed freezeouts only.
<a href="entry-rules.html">Entry rules</a> shows the exact wording each classification rests on.
<a href="schedule.html">Day plan</a> shows published starts and possible conflicts, but no policy-qualified entries.
<a href="hotels.html">Hotels</a> separates quoted rates from estimates.
<a href="sources.html#room-feed">Morning schedule watch</a> links to official schedules and coverage gaps.
<a href="questions.html">Questions</a> lists what still has to be answered before a decision.</div>

<div class="grid2">
<div class="panel"><h2>Research shortlist by published ratio</h2>
<p class="note">Entry dates on or after Nov 19, 2026. Open to players aged 21+ who hold a Venetian Rewards card, as printed on each sheet (rule 2); the card's cost and enrolment terms are not on the sheet. %(nres)d candidate event(s) are restricted by the
official sheet (age 50+ or women-only) and are listed at the foot of this page rather than ranked
against unrestricted research leads.</p>
<p class="note">Guarantee &divide; total entry fee, shown only where both figures are printed on the
official documents. This is a <strong>descriptive ratio, not a forecast</strong> &mdash; a guarantee is
a floor the room commits to, not a predicted pool. Bounty, multi-flight, satellite and team events are
excluded from this table on purpose: their guarantees are not like-for-like.</p>
<div class="tbl-scroll"><table><thead><tr>
<th>#</th><th>Event</th><th class="num">Entry</th><th class="num">Guarantee</th>
<th class="num">House fee</th><th class="num">GTD&divide;entry</th><th>Dates</th>
</tr></thead><tbody>%(top)s</tbody></table></div>
<p class="note"><a href="tournaments.html">Tournament filters &rarr;</a></p>
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
<li><a href="schedule.html">Day plan</a> &mdash; confirmed entries only for recommendations; overlap checks also cover research events.</li>
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
""" % dict(ret=RETRIEVED, reread=decisions.READ, cards=cardhtml, top=top, cheap=cheap, n=len(events),
                  nres=len(restricted), restricted_html=restricted_html)
    return page("Dashboard", body, "index.html")


def p_tournaments(events):
    dates = sorted({d for e in events for d in e["dates"]})
    rowshtml = []
    for e in events:
        gtdcell = gtd_cell(e)
        rowshtml.append(
            '<tr id="ev%(no)d" data-group="%(g)s" data-dates="%(dates)s" '
            'data-buyin="%(biv)s" data-confirmed="%(confirmed)s" data-gtd="%(gtdv)s" data-changed="%(chg)s" data-search="%(search)s">'
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
                dates=" ".join(e["dates"]), confirmed=int(e["single_entry_confirmed"]), biv=e["buy_in"] or "",
                datesc="".join("<span class='note slot' data-slot-date='%s'>%s</span>" % (d, d) for d, _ in e["entry_slots"]),
                starts="".join("<span class='note slot' data-slot-date='%s'>%s</span>" % (d, esc(start))
                               for d, start in e["entry_slots"]),
                bi=format(e["buy_in"], ",") if e["buy_in"] else "&mdash;",
                fee="$" + format(e["fee"], ",") if e["fee"] else "&mdash;",
                pool="$" + format(e["pool_per_entry"], ",") if e["pool_per_entry"] else "&mdash;",
                gtd=gtdcell, gtdv=e["gtd"] or 0,
                ratio="%.1f&times;" % e["ratio"] if e["ratio"] else "&mdash;",
                sheet="<br>".join(srclink(u, "sheet " + u.rsplit("_", 1)[-1].removesuffix(".pdf"))
                                   for u in event_sources(e)[2:])
                      + "<br>" + srclink(sched.SCHEDULE_URL, "DSE IV schedule"),
                checked=e["verified_on"],
                recheck=check_badge(*event_sources(e)),
                chg="1" if row_changed(*event_sources(e)) else "0",
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
the date selector and the confirmed-freezeout toggle. <strong>No event in this series has a verified whole-event
freezeout rule.</strong> Candidate events remain in the research table only; silence on re-entry,
rebuy and add-on does not qualify.</p></div>

<div class="panel">
<div class="controls">
<label>Search tournaments<input type="search" id="q" placeholder="event name, number, buy-in, date&hellip;"></label>
<label>From (Las Vegas)<input type="date" id="datef"></label>
<label>Through (inclusive)<input type="date" id="date-to"></label>
<label>Entry fee max<select id="maxbi">
<option value="">Any</option><option value="200">$200 and under</option>
<option value="300">$300 and under</option><option value="400">$400 and under</option>
<option value="600">$600 and under</option><option value="1100">$1,100 and under</option>
</select></label>
<label class="chk"><input type="checkbox" id="sef" checked> Single-entry / freezeout confirmed only</label>
<label class="chk"><input type="checkbox" id="include-past"> Include past entry dates</label>
<label class="chk"><input type="checkbox" id="nogtd"> Has a published guarantee</label>
<button class="btn" id="reset">Reset</button>
</div>
<div class="pill-row">%(pills)s</div>
<p class="note" id="count"></p>
<p class="note"><strong>Source re-check</strong> is the scheduled monitor's verdict on the structure
sheet and schedule documents behind this row: <em>unchanged</em>, <em>source changed</em> (the official document
changed and is awaiting review), <em>fetch error</em>, or
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
                "<td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                % (e["event_no"], esc(e["name"][:60]),
                   format(e["buy_in"], ",") if e["buy_in"] else "&mdash;",
                   ("Confirmed<div class='quote'>%s</div>" % esc(e["rule_evidence"]["single_entry"]["excerpt"]))
                   if e["single_entry_confirmed"] else "<span class='blank'>Unverified</span>",
                   esc(e["reentry"]), esc(e["addon"]), esc(e["rebuy"]),
                   ("<div class='quote'>%s</div>" % esc(e["fee_quote"])) if e["fee_quote"] else "&mdash;",
                   srclink(e["sheet_url"], "sheet %s" % e["sheet_no"]), esc(e["verified_on"])))
        return ("<div class='panel'><h2>%s <span class='tag t-%s'>%d</span></h2><p class='note'>%s</p>"
                "<div class='tbl-scroll'><table><thead><tr><th class='num'>#</th><th>Event</th>"
                "<th class='num'>Entry</th><th>Whole-event single entry</th><th>Re-entry clause</th><th>Add-on clause</th>"
                "<th>Rebuy clause</th><th>Official fee wording</th><th>Sheet</th><th>Last checked</th></tr></thead>"
                "<tbody>%s</tbody></table></div></div>"
                % (esc(title), group, len(items), esc(blurb), "".join(rows)))

    body = """
<div class="hero"><h1>Entry rules, quoted</h1>
<p class="lede">Single-entry, re-entry, add-on and fee values are stored as separate fields for every
event, each with the sentence it was taken from and the date it was read. Nothing here is a summary of
what a sheet probably means. Where a sheet says nothing, that is recorded as silence &mdash; and
silence is not a prohibition.</p></div>

<div class="banner"><strong>The one thing to understand.</strong> All 37 official structure sheets were
transcribed on %(ret)s (nine candidate sheets re-read %(reread)s). Not one contains a one-entry-only rule. Where a restriction is absent, it stays unverified even when the fee, starting stack and schedule are confirmed. Flag <a href="flagged.html#F-01">F-01</a>.</div>
""" % dict(ret=RETRIEVED, reread=decisions.READ)

    body += block("Group A \u2014 best single-entry candidates", "candidate",
                  "Events with one starting day, no bounty, no satellite seat, no team format, and "
                  "no re-entry, rebuy or add-on clause printed anywhere on the official structure sheet.")
    body += block("Group B \u2014 bounty and progressive knock-out", "bounty",
                  "These are not confirmed freezeouts; their published guarantee includes bounty money, so "
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
                 "<p class='note'>Example of a bagged-stack restriction, not a whole-event entry cap.</p>"
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
                "<div class='day'><h3>Primary &mdash; #%d %s%s</h3>"
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
            lines.append("<div class='day'><h3>No confirmed primary or fallback</h3><p class='note'>No eligible event has a written single-entry, no-rebuy and no-add-on rule.</p></div>")
        for fb in d["fallbacks"]:
            it = fb["item"]
            cls = "t-bad" if fb["verdict"] == "cannot be sequenced" else "t-warn"
            lines.append(
                "<div class='day'><h3>Fallback &mdash; #%d %s <span class='tag %s'>%s</span></h3>"
                "<div class='meta'>Start %s &middot; registration closes %s &middot; entry %s</div>"
                "<p class='note'>%s</p></div>"
                % (it["event_no"], esc(entry_title(it)[:70]), cls, esc(fb["verdict"]), esc(it["start"]),
                   esc(it["reg_close"] or "not published"),
                   ("$" + format(it["buy_in"], ",")) if it["buy_in"] else "not published",
                   esc(fb["note"])))
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
        entries = "".join(
            "<tr><td>#%d %s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (x["event_no"], esc(entry_title(x)), esc(x["start"]), esc(x["reg_close"]),
               esc(GROUP_LABEL[x["group"]]), srclink(x["schedule_sheet_url"], "official structure"),
               esc(decisions.READ))
            for x in d["entries"])
        pair_rows = "".join(
            "<li>#%d %s → #%d %s: <strong>%s</strong>. %s</li>"
            % (p["first"]["event_no"], esc(p["first"]["start"]), p["second"]["event_no"],
               esc(p["second"]["start"]), esc(p["verdict"]), esc(p["note"]))
            for p in d["pairs"])
        blocks.append(
            "<div class='panel' data-date='%s' data-overlap='%d'><h2>%s</h2>%s"
            "<div class='grid2'>%s</div><details><summary>Published starts and overlap review (research only)</summary>"
            "<div class='tbl-scroll'><table><thead><tr><th>Event</th><th>Start</th><th>Late registration</th>"
            "<th>Format</th><th>Source</th><th>Last checked</th></tr></thead><tbody>%s</tbody></table></div><ul>%s</ul></details></div>"
            % (d["date"], d["overlap"], esc(head), srclink(sched.SCHEDULE_PDF, "official schedule"),
               "".join(lines), entries, pair_rows))

    opts = "".join('<option value="%s">%s</option>' % (d["date"], d["date"]) for d in days)
    return page("Day plan", """
<div class="hero"><h1>Day plan</h1>
<p class="lede">No entry-qualified trip can be scheduled from this evidence. The plan only chooses
confirmed freezeouts without unverified eligibility. The Venetian research schedule is available by day below.
No finish time is published, so the late-registration cutoff can rule out a sequence or make it conditional,
but cannot prove one will work. All times are Las Vegas local.</p></div>

<div class="banner"><strong>No 8 AM start in this Venetian series.</strong> The earliest is 9:10 AM for
satellite #46; the earliest non-satellite start is 10:10 AM. Do not book two entries in advance based on these
windows. A continuation takes priority if you advance.</div>

<div class="panel">
<div class="controls">
<label>Date<select id="df"><option value="">All dates</option>%(opts)s</select></label>
<label class="chk"><input type="checkbox" id="ov"> Only days with possible overlap</label>
<label class="chk"><input type="checkbox" id="past"> Include past dates</label>
</div>
<p class="note" id="c"></p>
</div>
%(blocks)s
""" % dict(opts=opts, blocks="".join(blocks)), "schedule.html")


def all_quotes():
    prior = [dict(hotel=q["property"], check_in=q["arrival"], check_out=q["departure"], adults=q["adults"],
                  children=0, rooms=q["rooms"], retrieved=q["checked"], source=q["url"], note=q["status"],
                  checkout_total=q["total"], nightly_average=q["nightly"], resort_fee=q["fee"], tax=q["tax"],
                  parking=q["parking"], cancellation=q["cancel"], rate_timestamp=q["rate_timestamp"])
             for q in decisions.QUOTE_LOG]
    return prior + hotelsmod.QUOTE_LOG


def quote_log():
    keys = ("hotel", "check_in", "check_out", "adults", "children", "rooms", "room", "offer", "checkout_total",
            "nightly_average", "resort_fee", "tax", "parking", "cancellation", "rate_timestamp", "retrieved", "note")
    headers = ("Hotel", "Check-in", "Check-out", "Adults", "Children", "Rooms", "Room", "Offer", "Checkout total",
               "Nightly average", "Resort fee", "Tax", "Parking", "Cancellation deadline / term",
               "Rate timestamp", "Retrieved", "Audit note", "Official booking")
    rows = "".join("<tr>" + "".join("<td>%s</td>" % esc(q.get(key)) for key in keys)
                   + "<td>%s</td></tr>" % srclink(q["source"], "Official booking") for q in all_quotes())
    return ("<div class='panel' id='checkout-log'><h2>Exact-stay lookup log</h2>"
            "<p><strong>Research baseline:</strong> Dec 1–4, 2026, one adult, one room; $200 per night all-in ($600 for three nights). "
            "Screen for a private nonsmoking room with ensuite bath and a refundable rate with a written deadline. These are comparison "
            "criteria, not verified hotel features. The earlier two-adult Nov 25–28 lookup is not comparable. Compare the same dates, "
            "occupancy, room class, cancellation terms and parking needs. No comparable itemized checkout "
            "total is verified; blanks mean unverified, not zero.</p><div class='tbl-scroll'><table><thead><tr>"
            + "".join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>" + rows + "</tbody></table></div></div>")


def hotel_estimator(prefix):
    hotel_options = "".join(
        '<option value="%s" data-fee="%s" data-tax="%s" data-book="%s">%s</option>'
        % (esc(h["id"]), esc(h["resort_fee"]), esc(h.get("tax_pct")), esc(h["book"]), esc(h["name"]))
        for h in hotelsmod.HOTELS)
    checkout = """
<label>Final checkout total for the stay ($)<input type="number" id="t-checkout" min="0" step="0.01"></label>
<p class="note">Use the exact-stay checkout total (include mandatory fees, tax and applicable parking once).
A valid checkout total overrides the component estimate below. Leave it blank only for a what-if estimate.
Enter zero nights for entries only.</p>""" if prefix == "t" else ""
    return """
<div class="panel" data-estimator="{p}"><h2>Estimate lodging cost</h2>
<p class="note">This is not a quote. Provide the average base room rate <em>before</em> resort fee and tax.
The model applies tax to room rate + resort fee, then adds parking at the all-in amount. This is a
scenario, not confirmation of how every property itemizes tax. No dated price is prefilled.</p>
{checkout}
<div class="calc">
<label>Hotel<select id="{p}-hotel"><option data-fee="" data-tax="" data-book="">Choose a hotel</option>{opts}</select></label>
<label>Nightly base rate ($)<input type="number" id="{p}-rate" min="0" step="0.01"></label>
<label>Resort fee / night ($)<input type="number" id="{p}-fee" min="0" step="0.01"></label>
<label>Room tax (%)<input type="number" id="{p}-tax" min="0" step="0.01" placeholder="13.38 if applicable"></label>
<label>All-in parking / night ($)<input type="number" id="{p}-park" value="{parking}" min="0" step="0.01"></label>
<label>Nights<input type="number" id="{p}-nights" value="3" min="0" step="1"></label>
</div>
<p class="note">{parking_note} Choosing a property preloads only known
fee/tax values. Enter 0 explicitly when a charge is confirmed absent. <a id="{p}-book" href="hotels.html#checkout-log">Official booking links and lookup log</a>.</p>
<div class="calc" aria-live="polite">
<div class="out"><div class="k">Estimated nightly cost</div><div class="v" id="{night_id}">&mdash;</div></div>
<div class="out"><div class="k">Estimated stay total</div><div class="v" id="{total_id}">&mdash;</div></div>
</div></div>
""".format(p=prefix, opts=hotel_options, checkout=checkout, parking="0" if prefix == "t" else "",
           parking_note="Trip scenario defaults to no car ($0 parking)." if prefix == "t" else "Enter parking cost, or 0 for no car.",
           night_id="tot-night" if prefix == "t" else "h-night",
           total_id="tot-hotel" if prefix == "t" else "h-total")


def p_hotels():
    rows = []
    for h in hotelsmod.HOTELS:
        fee = ("$%d" % h["resort_fee"]) if h["resort_fee"] is not None else '<span class="blank">not published</span>'
        pr = ("from $%d" % h["poker_rate"]) if h["poker_rate"] else '<span class="blank">none published</span>'
        canc = ('<span class="blank">not published</span>' if not h.get("cancel")
                else esc(h["cancel"]) + "<div class='note'>%s</div>" % esc(h.get("cancel_type") or "")
                + ("<div class='note'>%s</div>" % srclink(h["cancel_src"]) if h.get("cancel_src") else ""))
        rows.append(
            "<tr><td><strong>%s</strong><div class='note'>%s</div></td>"
            "<td>%s<div class='note'>%s</div></td>"
            "<td class='num'>%s</td><td class='num'>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
            % (esc(h["name"]), esc(h["addr"]),
               fee, esc(h["resort_fee_note"] or ""),
               pr,
               '<span class="blank">not published</span>' if h.get("tax_pct") is None
               else ("%.2f%%" % h["tax_pct"] + ("<div class='note'>%s</div>" % srclink(h["tax_src"]) if h.get("tax_src") else "")),
               ((esc(h["parking"]) if h["parking"] else '<span class="blank">not published</span>')
                # The parking value must show the page that prints it. Venetian/Palazzo were re-cited
                # 2026-11-19 (flag P-01): their old source, the poker room page, prints no parking fee.
                + (("<div class='note'>%s</div>" % (srclink(h["parking_src"], "Parking fee, official page")
                       + ((" · " + srclink(h["parking_src_2"], "Verified independently here"))
                          if h.get("parking_src_2") else "")))
                   if h.get("parking_src") else "")),
               canc,
               ('<span class="blank">not published</span>' if not h["dated_total"] else esc(h["dated_total"])),
               srclink(h["resort_fee_src"], "Official fee source") + " · " + srclink(h["book"], "Official booking")
               + "<div class='note'>Fee read %s</div>" % esc(h.get("resort_fee_checked")),
               check_badge(*(h[f] for f in ("resort_fee_src", "parking_src", "cancel_src", "tax_src", "book") if h.get(f)))))

    # Occupancy and early-departure charges, which change the true cost per night and are usually
    # missed by a per-night comparison. Rendered only where the property publishes a figure.
    extra = []
    for h in hotelsmod.HOTELS:
        if not (h.get("extra_guest_fee") or h.get("early_checkout_fee")):
            continue
        extra.append(
            "<tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>"
            % (esc(h["name"]),
               esc(h["extra_guest_fee"]) if h.get("extra_guest_fee") else '<span class="blank">not published</span>',
               esc(h["early_checkout_fee"]) if h.get("early_checkout_fee") else '<span class="blank">not published</span>'))
    extra_html = ("<div class='panel'><h2>Occupancy and early-departure charges</h2>"
                  "<p class='note'>These are the charges that make a per-night rate quote not equal the "
                  "bill. Both are taken verbatim from the property's own terms; a blank means the page "
                  "read does not publish the figure.</p>"
                  "<div class='tbl-scroll'><table><thead><tr><th>Hotel</th>"
                  "<th>Extra occupant above double occupancy</th><th>Early check-out</th>"
                  "</tr></thead><tbody>%s</tbody></table></div>"
                  "<p class='note'>Sources: the Venetian/Palazzo, Bellagio and MGM Grand hotel terms "
                  "linked in the table above.</p></div>") % "".join(extra)
    log = "".join(
        "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td class='note'>%s</td></tr>"
        % (esc(d), esc(hid), esc(field), esc(value),
           srclink(url) if url else '<span class="blank">no page</span>', esc(note))
        for d, hid, field, value, url, note in hotelsmod.RATE_LOG)

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
requirement must be met before 2&nbsp;a.m. on the last night. <strong>$119 and $209 are advertised starting
rates, not quoted rates for any specific night.</strong> Terms, blackout dates, availability and qualifying
play all matter. This trip cannot assume that any entry earns the discount.
Source: %(srcrates)s</div>

<div class="panel"><h2>Hotel comparison</h2>
<div class="tbl-scroll"><table><thead><tr>
<th>Hotel</th><th>Resort fee / night</th><th class="num">Fee</th><th class="num">Room tax</th>
<th>Parking</th><th>Cancellation deadline</th><th>Dated checkout total</th><th>Sources / retrieval</th><th>Source re-check</th>
</tr></thead><tbody>%(rows)s</tbody></table></div>
<p class="note">The Venetian and Palazzo terms print 13.38%%. Do not apply it to another property without
checking its quote and the applicable jurisdiction. See flag <a href="flagged.html#F-07">F-07</a>.</p>
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
""" % dict(rows="".join(rows), log=log, calc=hotel_estimator("h"), quotes=quote_log(), ret=decisions.READ, extra=extra_html,
           srcrates=srclink("https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"))
    return page("Hotels & true cost", body, "hotels.html")


def maps_lookup_panel():
    ids = {"H-VEN": "venetian", "H-PAL": "palazzo", "H-WYN": "wynn", "H-ENC": "encore", "H-BEL": "bellagio",
           "H-MGM": "mgm-grand", "H-CP": "caesars-palace", "H-HS": "horseshoe"}
    hotels = {h["id"]: h for h in hotelsmod.HOTELS}
    rows = []
    for hid, (origin, minutes) in sorted(hotelsmod.MAPS_TO_VENETIAN.items(), key=lambda row: row[1][1]):
        hotel = hotels[ids[hid]]
        query = urlencode(dict(api=1, origin=origin, destination="The Venetian Poker Room, Grand Canal Shoppes",
                               travelmode="walking"))
        rows.append('<tr data-google-min="%s"><td>%s</td><td>%s</td><td>%d min</td>'
                    '<td>%s</td><td>2026-11-19</td><td>%s · %s</td></tr>' % (
                        minutes, esc(hotel["name"]), esc(origin), minutes, "Within limit" if minutes <= 30 else "Over limit",
                        srclink("https://www.google.com/maps/dir/?" + query, "Google walking route"),
                        srclink(hotel["book"], "Official property")))
    return ("<div class='panel' id='google-routes'><h2>Google Maps checks to the Venetian poker room</h2>"
            "<p>All eight hotels in the hotel comparison were checked. Durations are estimates, not "
            "door-to-seat measurements. The official indoor directions are below.</p>"
            "<label class='chk'><input type='checkbox' id='google30'> 30 minutes or less (Google routes)</label>"
            "<div class='tbl-scroll'><table><thead><tr><th>Hotel</th><th>Route origin</th><th>Estimated walk</th>"
            "<th>30-minute test</th><th>Checked</th><th>Sources</th></tr></thead><tbody>" + "".join(rows) +
            "</tbody></table></div></div>")


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
    evidence = {h["id"]: (w["venetian_min"], w["maps_venetian"], "Google Maps route estimate", date, True)
            for h in previous["hotels"] if (w := h.get("walk")) and w.get("routers_agree_30min") is not None
            and date and w.get("venetian_min") is not None and w.get("maps_venetian", "").startswith("https://www.google.com/")}

    for hid, (origin, minutes) in hotelsmod.MAPS_TO_VENETIAN.items():
        query = urlencode(dict(api=1, origin=origin, destination="The Venetian Poker Room, Grand Canal Shoppes",
                               travelmode="walking"))
        evidence[hid] = (minutes, "https://www.google.com/maps/dir/?" + query, "Google Maps route estimate",
                         decisions.READ, True)
    return evidence


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
    wj = json.load(open(os.path.join(ROOT, "data", "site", "walking.json")))
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

<div class="banner"><strong>Read this before you trust a number.</strong> These durations are
<em>routing estimates</em>, not measurements. They were computed from OpenStreetMap data with the OSRM
foot profile on 2026-11-16 &mdash; a straight-line-plus-path model that does not know about the Strip's
footbridges, kerb ramps, crowds or the fact that the Venetian poker room is on level 2 of the Grand
Canal Shoppes, reached by escalator. They can screen candidate routes, but do not establish that a hotel is best or that a tight connection is possible. Flag <a href="flagged.html#F-08">F-08</a>.</div>

%s
<h2>Earlier multi-venue routing model</h2>
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
""" % (maps_lookup_panel(), controls, "".join(out), srclink(sched.POKER_ROOM_URL), decisions.READ), "walking.html")


def p_trip(events):
    events = sorted((e for e in events if e["buy_in"] and e["group"] == "candidate" and not demographic_gate(e)),
                    key=lambda e: (e["buy_in"], e["event_no"]))
    opts = "".join(
        '<option value="%d" data-buyin="%d" data-confirmed="%d">#%d &mdash; %s ($%s) · %s</option>'
        % (e["event_no"], e["buy_in"], e["single_entry_confirmed"], e["event_no"],
           esc(e["name"][:58]), format(e["buy_in"], ","), esc(e["group_label"]))
        for e in events)
    return page("Trip cost", """
<div class="hero"><h1>Trip cost estimator</h1>
<p class="lede">Estimated trip cost = sum of entries × total buy-in + nights × estimated hotel cost.
Entry prices come from official structure sheets; lodging inputs are scenario amounts, not a checkout quote.
No tournament currently qualifies for the confirmed single-entry itinerary.</p></div>
<div class="panel"><h2>Entries</h2>
<p class="note">Use at most one buy-in per research candidate for a what-if budget. Known spending formats are excluded. The calculator does not confirm eligibility,
registration, or schedule fit. It does not count potential winnings or a conditional poker-room discount.</p>
<div class="controls">
<label class="chk"><input type="checkbox" id="research-entries"> Allow research events in estimate only</label>
<label>Event<select id="pick"><option value="">Choose a confirmed entry</option>%s</select></label>
<button class="btn" id="add" type="button" disabled>Add</button>
</div>
<div class="tbl-scroll"><table id="cart"><thead><tr><th>Event and official sources</th><th>Entries</th><th>Entry subtotal</th><th></th></tr></thead><tbody></tbody></table></div>
</div>
%s
<div class="panel"><h2>Trip totals</h2><div class="calc" aria-live="polite">
<div class="out"><div class="k">Entry fees</div><div class="v" id="tot-buyin">$0.00</div></div>
<div class="out"><div class="k">Estimated trip cost</div><div class="v" id="tot-all">&mdash;</div></div>
</div><p class="note">Excludes flights, food, cash-game bankroll and other trip costs.</p></div>
""" % (opts, hotel_estimator("t")), "trip.html")



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
            pub = "64 events, 94 scheduled rows, all 37 structure sheets read. No written freezeout confirmed."
        else:
            v = contentmod.OTHER_VENUES_BY_ID.get(key) or next(v for v in contentmod.OTHER_VENUES if v["name"] == meta["title"])
            pub = esc(v["verdict"])
        cards.append(
            "<div class='panel'><h2><a href='%s'>%s</a></h2>"
            "<p class='note'><strong>Room:</strong> %s</p>"
            "<p class='note'><strong>Hotels:</strong> %s%s</p>"
            "<p>%s</p><p><a href='%s'>Open the %s page &rarr;</a></p></div>"
            % (meta["page"], esc(meta["title"]), esc(meta["room"]),
               esc(stat), (" &middot; nearest: " + esc(nearest)) if nearest else "",
               pub, meta["page"], esc(meta["title"])))

    return page("Venues", """
<div class="hero"><h1>Venues</h1>
<p class="lede">One page per poker room, each listing that room's events and the hotels within walking
distance of it when evidence is available. The Venetian series is the only full event-by-event audit in this dashboard. Other official schedules appear in the <a href="sources.html#room-feed">morning schedule watch</a> and venue evidence sections.</p></div>

<div class="banner info"><strong>How to read a room page.</strong> The events table holds only rows
transcribed from that room's own official document. Where the room publishes no dated event, the table
is empty and the reason is quoted underneath with the page that was checked. The hotels table applies
the 30-minute walking limit to routed estimates, with a Maps link on every row.</div>

<div class="grid2">%s</div>
""" % "".join(cards), "venues.html", subnav=SUBNAV["venues.html"])


def p_venue_venetian(events, days):
    rows = "".join(
        "<tr><td class='num'>%d</td><td>%s</td><td class='num'>$%s</td><td>%s</td><td>%s</td><td>%s · %s</td></tr>"
        % (e["event_no"], esc(e["name"][:70]),
           format(e["buy_in"], ",") if e["buy_in"] else "&mdash;",
           ", ".join("<span class='note'>%s</span>" % d[5:] for d in e["dates"]),
           "<span class='tag t-%s'>%s</span>" % (e["group"], esc(e["group_label"].split(" (")[0])),
           srclink(e["sheet_url"], "Official structure sheet"), esc(e["verified_on"]))
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
<dt>Structure sheets</dt><dd>37 PDFs; transcribed %(ret)s; nine candidate sheets re-read %(reread)s</dd>
<dt>Next series</dt><dd>DeepStack Extravaganza NYE, Dec 24 2026 &ndash; Jan 10 2027</dd>
<dt>Then</dt><dd>DeepStack Showdown, Jan 11 &ndash; Feb 14 2027</dd>
</dl>
<p class="note">Source: %(series)s</p>
</div>
</div>

<div class="panel"><h2>Every event in the series</h2>
<div class="tbl-scroll"><table><thead><tr>
<th class="num">#</th><th>Event</th><th class="num">Entry</th><th>Dates</th><th>Classification</th><th>Source / retrieval</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>

<div class="panel"><h2>Nearby stays</h2><p>See the <a href="walking.html#google-routes">eight address-based Google Maps estimates</a> and <a href="hotels.html">official booking links and charges</a>. No comparable checkout quote was confirmed.</p></div>
<div class="banner"><strong>Irregularity X-02.</strong> Resolved Nov 19: the series overview now labels DeepStack IV as current. Check the dated source for each start and the <a href="../flagged.html#X-09">NYE discrepancies</a> before planning later dates.
%(series)s</div>
""" % dict(n=len(events), rows=rows, ret=RETRIEVED, reread=decisions.READ,
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
        desc="Host room for the WPT World Championship (Nov 27 - Dec 21) and a recurring daily slate. "
             "All four daily structures were read November 19: each permits extra spending and is excluded. "
             "Daily availability during series is unverified.",
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
        desc="A historical structure sheet is archived; no current slate was confirmed.",
        page="venues/mgm-grand.html",
    ),
    "resorts-world": dict(walk_key=None, title="Resorts World Las Vegas", room="Resorts World poker room",
                         desc="No current dated tournament schedule verified.", page="venues/resorts-world.html"),
    "westgate": dict(walk_key=None, title="Westgate Las Vegas", room="Westgate poker room",
                     desc="No current dated tournament schedule verified.", page="venues/westgate.html"),
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
    if not rows:
        return ("<div class='panel'><h2>Hotels</h2><p>No hotel-to-room walk has been verified for this venue. "
                "See <a href='hotels.html'>the dated hotel log</a> for booking and comparison criteria.</p></div>")
    gmaps = google_routes()
    trs = "".join(walk_table_row(r, gmaps, wj["as_of"]) for r in rows)
    ok = sum(1 for r in rows if (minutes := route_evidence(r, gmaps, wj["as_of"])[0]) is not None and minutes <= 30)
    return ("""
<div class="panel"><h2>Hotels within walking distance of %(room)s</h2>
<p class="note">%(ok)d of %(n)d hotels are inside the 30-minute limit. These are route estimates (Google Maps where recorded, otherwise OSRM). Unverified times stay blank. Leave extra time for indoor access. Flag <a href="flagged.html#F-08">F-08</a>.</p>
<div class="chk-row"><label class="chk"><input type="checkbox" id="w30" data-walk-room="%(key)s">
Within 30 minutes only</label><span class="note" id="wc"></span></div>
<div class="tbl-scroll"><table id="wt-%(key)s"><thead><tr><th>Hotel</th>
<th class="num">Walking estimate</th><th>30-minute rule</th><th>Route / last checked</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>
""" % dict(room=esc(room), ok=ok, n=len(rows), asof=esc(wj["as_of"]), key=walk_key,
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
                "<th class='num'>Levels</th><th class='num'>Guarantee</th><th>Last checked</th></tr>")
        rows = "".join(
            "<tr><td>%s</td><td class='num'>$%s</td><td class='num'>$%s</td>"
            "<td class='num'>$%s</td><td>$%d add-on &middot; %s chips at the first break</td>"
            "<td class='num'>%s</td><td class='num'>%d min</td><td class='num'>%s</td><td>%s</td></tr>"
            % (esc(r["start"]), format(r["buy_in"], ","), format(r["house_fee"], ","),
               format(r["to_pool"], ","), r["add_on"], format(r["add_on_chips"], ","),
               format(r["chips"], ","), r["level_min"],
               "$" + format(r["guarantee"], ",") if r["guarantee"] else "&mdash;",
               esc(sched_data["retrieved"]))
            for r in sched_data["rows"])
        doc_link = srclink(sched_data["source"], "official daily tournament flyer (PDF)")
    elif key == "bellagio":
        sched_data = othermod.BELLAGIO_SCHEDULE
        head = ("<tr><th>Day</th><th>Start</th><th>Event</th><th class='num'>Buy-in</th>"
                "<th class='num'>House fee</th><th>Gratuity buys chips</th>"
                "<th class='num'>Starting chips</th><th class='num'>Levels</th>"
                "<th class='num'>Guarantee</th><th>Structure sheet</th><th>Last checked</th></tr>")
        rows = ""
        for r in sched_data["events"]:
            buy = ("$" + format(r["buy_in"], ",")) if r["buy_in"] else (
                "<span class='blank-cell'>conflict &mdash; see X-04</span>")
            rows += (
                "<tr><td>%s</td><td>%s</td><td>%s</td><td class='num'>%s</td>"
                "<td class='num'>$%s</td><td>$%d &rarr; +%s chips</td>"
                "<td class='num'>%s without &middot; %s with</td><td class='num'>%d min</td>"
                "<td class='num'>%s</td><td>%s</td><td>%s</td></tr>"
                % (esc(r["day"]), esc(r["start"]), esc(r["name"]), buy,
                   format(r["house_fee"], ","), r["gratuity"],
                   format(r["gratuity_chips"], ","),
                   format(r["chips_without_gratuity"], ","),
                   format(r["chips_with_gratuity"], ","), r["level_min"],
                   ("$" + format(r["guarantee"], ",")) if r["guarantee"] else "&mdash;",
                   srclink(r["source"], "PDF"), esc(sched_data["retrieved"])))
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
    own = next((v for v in contentmod.OTHER_VENUES if v["name"] == meta["title"]),
               contentmod.OTHER_VENUES_BY_ID.get(key))
    # events and hotels for this room
    if key == "venetian":
        ev_html = ("<p>64 events across 38 playable days, all 37 structure sheets read. "
                   "<a href='../tournaments.html'>Open the full event table</a> or "
                   "<a href='../schedule.html'>the day plan</a>.</p>")
        hotel_count = 21
    else:
        ev_html = ('<p class="blank-cell">No date-specific event row was verified for this room, so this table is intentionally empty. The reason is recorded below '
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
                    srclink(decisions.WYNN_JAN_RULES, "January structures (placeholder)"))) + wynn_daily_table()
    matching = [(label, evidence, document) for label, local, evidence, _, document in contentmod.SCHEDULE_FEED
                if local == meta["page"] and document]
    if matching:
        ev_html += "<ul>" + "".join("<li>%s: %s</li>" % (srclink(doc, label), esc(note))
                                    for label, note, doc in matching) + "</ul>"
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
""" % dict(room=esc(own["poker_room"]), desc=esc(meta["desc"]), ret=esc(own.get("checked") or "not confirmed"),
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
<p class="lede">Historical findings from seven nearby poker rooms. See each room page and the
<a href="../sources.html#room-feed">morning schedule watch</a> for dated official evidence.
None of the events reviewed here passes the strict freezeout filter.</p></div>

<div class="banner"><strong>Research coverage, not a citywide negative.</strong> The 64-event dataset
covers Venetian DeepStack IV. The room pages link to current published documents where available and
keep the audited Caesars and Bellagio spending formats separate. A missing row means the schedule or
rules have not been verified for this dataset, not that the room has no tournament.</div>

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

<div class="cards">
<div class="card"><div class="k">Series covered</div><div class="v">DSE IV</div>
<div class="s">Nov 16 &ndash; Dec 23, 2026 &middot; %(n)s events</div></div>
<div class="card"><div class="k">Official documents read</div><div class="v">39</div>
<div class="s">37 structure sheets + schedule page + schedule PDF</div></div>
<div class="card"><div class="k">Confirmed single-entry</div><div class="v">0</div>
<div class="s">no audited sheet states a one-entry rule</div></div>
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
suite-rate page, both re-read on Nov 19.</li>
<li><strong>Other room schedules:</strong> official Wynn, Caesars Palace and Bellagio documents are linked from the <a href="sources.html#room-feed">morning watch</a>. The Wynn WPT opener allows re-entry, and the audited Caesars and Bellagio slates allow re-entry or paid add-ons.</li>
</ul></div>

<div class="panel"><h2>What could not be verified</h2>
<ul class="tight">
<li><strong>Any single-entry guarantee.</strong> Not one official document says an event is one entry
only. The strongest available statement is the absence of a re-entry clause. <a href="flagged.html#F-01">F-01</a></li>
<li><strong>Any finish time.</strong> No event has a published end time, so no two events can be
promised as a sequence. <a href="flagged.html#F-04">F-04</a></li>
<li><strong>A comparable checkout quote.</strong> Partial or dynamically loaded rates are not a stay total.
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
<p>The first half cannot be completed from the documents alone. <strong>No audited sheet states a
one-entry rule.</strong> The research candidates have one scheduled starting day and carry no re-entry, rebuy
or add-on clause at all &mdash; which is still silence rather than a promise. Written confirmation from the poker room would resolve that gap.
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
        "<td>%s</td><td>%s</td></tr>"
        % (esc(q["id"]), esc(q["id"]), esc(q["q"]), esc(q["why"]), esc(q["blocks"]), esc(q["answer"] or "Open"))
        for q in contentmod.QUESTIONS)
    body = """
<div class="hero"><h1>Questions that must be answered first</h1>
<p class="lede">What we know, what we do not know, and what has to be settled before any decision here
is reasonable. The strict entry policy is settled. Other decisions still need a documented answer.</p></div>

<div class="banner"><strong>No booking recommendation.</strong> The research budget and quality screen are defined, but written event rules and equivalent checkout totals are missing. The hotel log uses a Dec 1–4 research window, not a trip commitment. See <a href="suggestions.html">suggestions</a> for ways to close these gaps.</div>

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
<li>Whether any audited candidate enforces a written whole-event one-entry limit.</li>
<li>Finish times, or any basis for deriving one. No field sizes are published in advance.</li>
<li>A comparable itemized checkout total for the same stay, occupancy and booking conditions.</li>
<li>A cancellation deadline tied to a future bookable quote.</li>
<li>An official quality rating for any property.</li>
<li>A measured walking time. The matrix is modelled, not measured.</li>
<li>Complete written rules for every event listed in the <a href="sources.html#room-feed">official schedule watch</a>.</li>
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
own priority. Google Maps and OSRM both estimate a route; neither measures time from the room door to the table. <a href="#S-04">S-04</a></li>
<li><strong>Turn the monitor from page hashes into value changes.</strong> A hash change tells you a
page moved. Tracking the specific sentence each row was transcribed from tells you the buy-in changed.
<a href="#S-07">S-07</a></li>
<li><strong>Pick one quality authority.</strong> Cost and quality outrank distance in the brief, but
quality has no official source, so it is currently a blank column. <a href="#S-06">S-06</a></li>
<li><strong>Consolidate.</strong> Three scheduled monitor jobs and four overlapping dashboards are
still in the repository. <a href="#S-09">S-09</a>, <a href="#S-10">S-10</a></li>
</ol></div>
""" % dict(rows=rows), "suggestions.html")


def wynn_daily_table():
    rows = []
    for r in fresh.WYNN_DAILY:
        rules = []
        for name in ('reentry', 'rebuy', 'addon'):
            f = r[name]
            value = 'Not allowed' if f['value'] is False else ('$%s' % f['value'] if f['value'] is not None else '')
            rules.append('<td>%s<div class="note">%s</div></td>' % (value, esc(f['excerpt'])))
        rows.append('<tr><td>%s<br>%s<br>%s</td><td>$%s</td><td>$%s</td><td>%s</td><td>%s / %s min</td><td>%s</td>%s<td>%s<br>%s</td></tr>' % (
            esc(r['name']), esc(r['days']), esc(r['start']), r['entry'], format(r['guarantee'], ','),
            'House $%s + staff $%s; pool $%s' % (r['house_fee'], r['staff_fee'], r['pool']),
            format(r['chips'], ','), r['level_minutes'], esc(r['late_registration']), ''.join(rules),
            srclink(r['source'], 'Official rules'), r['last_checked']))
    return '''<p><strong>Separate extra-spend section — excluded from strict single-entry recommendations.</strong>
    All four daily formats were read from the official Wynn structures on November 19. These are recurring
    templates, not verified occurrences for specific trip dates. Each sheet allows suspension during series.
    A Friday “no re-entry” rule still permits rebuys and an add-on. Blank rule values mean not stated, not prohibited.</p>
    <div class="tbl-scroll"><table><thead><tr><th>Format / days / start</th><th>Total entry</th><th>Guarantee</th>
    <th>Initial entry split</th><th>Stack / levels</th><th>Late registration</th><th>Re-entry</th><th>Rebuy</th>
    <th>Add-on</th><th>Official source / last checked</th></tr></thead><tbody>''' + ''.join(rows) + '''</tbody></table></div>
    <p class="note">Finish times and exact-date availability are unverified. Friday rebuy accounting conflicts
    inside rule 3; see N-02 on Flagged for review. No descriptive ratio is used to recommend these excluded formats.</p>'''


def p_latest_review():
    facts = [
        ('Venetian dated schedule', 'All four HTML chunks read, November 16–December 23 series still listed. Schedule-only re-read does not reverify structure terms.', fresh.SCHEDULE),
        ('Wynn daily rules', 'All three extracted chunks read. Four recurring formats all permit re-entry, rebuys or paid add-ons; excluded.', fresh.WYNN_RULES),
        ('Wynn upcoming series', 'Official page lists WPT World Championship November 27–December 21; daily formats may be suspended during series. No daily occurrence inferred.', fresh.WYNN_PAGE),
        ('Venetian resort fee', 'Official page still states $55 plus tax per night. This is not a room quote or a checkout total.', fresh.FEE),
    ]
    rows = ''.join('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' %
                   (esc(a), esc(b), fresh.CHECKED, srclink(c)) for a,b,c in facts)
    return page('Latest evidence and decision readiness', '''
    <div class="hero"><h1>Latest evidence &amp; decision readiness</h1>
    <p class="lede">November 19, 2026 · No manual input was needed to perform this audit.
    Personal travel constraints were not invented. No booking or payment was made.</p></div>
    <div class="banner"><strong>Recommendation: do not make a nonrefundable poker-trip booking from this dataset yet.</strong>
    No tournament currently has written confirmation of the complete one-entry / no-rebuy / no-add-on policy.
    No comparable exact-stay checkout total is available. Dated Google Maps walks are estimates, not indoor measurements.</div>
    <div class="panel"><h2>Fresh official reads, precisely scoped</h2>
    <table><thead><tr><th>Source</th><th>Finding</th><th>Last checked</th><th>Official link</th></tr></thead><tbody>''' + rows + '''</tbody></table>
    <p>The original 37-sheet transcription is dated November 17. Concurrent integration re-read sheets 5, 6 and 7 on November 19; those event rows retain the newer date. The saved transcription consistency
    test itself is not a new live read. Reading the schedule today does not justify removing an unverified entry-rule label.</p></div>
    <div class="panel"><h2>Wynn daily structures: separate extra-spend events</h2>''' + wynn_daily_table() + '''</div>
    <div class="panel"><h2>Questions, known answers and next evidence needed</h2>
    <table><thead><tr><th>Decision question</th><th>Known answer / missing information</th><th>Next step / source</th></tr></thead><tbody>
    <tr><td>Which event meets the strict policy?</td><td>None confirmed in reviewed documents. Rules-silent is not eligible.</td><td>Obtain written maximum-entry, no-rebuy and no-add-on confirmation from the <a href="https://www.venetianlasvegas.com/resort/casino/poker.html">official room</a>.</td></tr>
    <tr><td>Can play start at 8 a.m.?</td><td>No reviewed schedule establishes an 8 a.m. eligible tournament. Registration opening is not a start time.</td><td>Check the <a href="https://www.wynnlasvegas.com/casino/poker">official schedules</a>; do not insert invented morning events.</td></tr>
    <tr><td>Can an evening event follow a daytime event?</td><td>No verified finish time. Late-registration cutoff is not the preceding event’s finish.</td><td>Use the <a href="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html">official start schedule</a>; switch only if the earlier event is skipped or has finished for you and you can register in time.</td></tr>
    <tr><td>Which hotel is best value?</td><td>Dec 1–4 is the comparison window: one adult and $200/night all-in for a private nonsmoking ensuite room with a refundable rate. No comparable checkout price confirmed.</td><td>Compare the same stay and room/refund terms via <a href="https://www.venetianlasvegas.com/book">official booking</a>. Capture room subtotal, mandatory fees, tax, parking, total, nightly average, cancellation deadline and timestamp as a new rate-log entry.</td></tr>
    <tr><td>Is the walk ≤30 minutes?</td><td>Seven of eight dated Google routes to the Venetian poker room are estimated at 30 minutes or less. Indoor walking was not timed.</td><td>Verify the route to the actual poker-room entrance using the <a href="https://www.venetianlasvegas.com/resort/casino/poker.html">official destination</a>, including pedestrian bridges and indoor access; retain route timestamp.</td></tr>
    </tbody></table></div>
    <div class="panel"><h2>Suggested next paths — not silently implemented</h2>
    <ol><li><strong>Keep strict policy:</strong> prioritize written room confirmation; no relaxed-event recommendation.</li>
    <li><strong>Improve rate capture:</strong> an authorized booking integration needs exact dates and occupancy before collecting comparable quotes. No arbitrary defaults.</li>
    <li><strong>Consolidate legacy surfaces:</strong> retain old links, but make the current evidence dashboard the eventual sole source of truth. Review this separately before retiring old workflows.</li></ol>
    <p><a href="suggestions.html">Full suggestions register</a> · <a href="flagged.html">Flagged for review</a> · <a href="sources.html">Scheduled source checks</a></p></div>
    ''', 'latest-review.html')


def p_flagged(events):
    live_flags = [dict(id="MON-%d" % i, area="Source changed", title="Document needs re-review",
                       detail="An unchanged re-fetch does not reverify the stored facts.",
                       impact="Re-read before relying on affected rows.", source=url)
                  for i, url in enumerate(sorted(PENDING), 1)]
    rows = "".join(
        "<tr id='%s'><td class='num'>%s</td><td>%s</td>"
        "<td><strong>%s</strong><div class='note'>%s</div></td>"
        "<td>%s</td><td>%s</td></tr>"
        % (esc(f["id"]), esc(f["id"]), esc(f["area"]), esc(f["title"]), esc(f["detail"]),
           esc(f["impact"]), srclink(f["source"]))
        for f in contentmod.FLAGS + fresh.FLAGS + live_flags)
    nh = len(hotelsmod.HOTELS)
    body = """
<div class="hero"><h1>Flagged for review</h1>
<p class="lede">Every value that could not be confirmed from an official source, and every irregularity
found in an official document. Nothing here blocks the site &mdash; it is the list of things you should
look at yourself, with the link to do it.</p></div>

<div class="banner"><strong>Latest issues to check:</strong> <a href="#X-09">Venetian NYE price and dates</a>,
<a href="#X-10">Wynn WPT date labels</a>, and <a href="sources.html#room-feed">scheduled-source status</a>.</div>

<div class="panel"><div class="tbl-scroll"><table><thead><tr>
<th class="num">ID</th><th>Area</th><th>Issue</th><th>Why it matters</th><th>Source to check</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>

<div class="panel"><h2>Blank cells on this site, in one list</h2>
<ul class="tight">
<li><strong>Single-entry confirmation</strong> &mdash; 0 of %(n)s audited events. No audited sheet states one.
<a href="#F-01">F-01</a></li>
<li><strong>Finish times</strong> &mdash; 0 of %(n)s events. <a href="#F-04">F-04</a></li>
<li><strong>Comparable checkout quotes</strong> &mdash; 0 of %(nh)s hotels. <a href="#F-05">F-05</a></li>
<li><strong>Cancellation deadlines</strong> &mdash; 0 of %(nh)s hotels. <a href="#F-06">F-06</a></li>
<li><strong>Official quality ratings</strong> &mdash; 0 of %(nh)s hotels.</li>
<li><strong>Measured walk times</strong> &mdash; 0 pairs. All are routing estimates.
<a href="#F-08">F-08</a></li>
<li><strong>Caesars Palace and Horseshoe resort fees</strong> &mdash; only a $45&ndash;$50 corporate
range is published, so no single value is entered.</li>
<li><strong>Room tax per property</strong> &mdash; only prefilled where a property's official terms establish it.</li>
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


def room_feed():
    rows = []
    for label, local, evidence, page_url, document in contentmod.SCHEDULE_FEED:
        target = document or page_url
        rows.append('<tr><td><a href="%s">%s</a></td><td>%s</td><td>%s</td><td>%s</td>'
                    '<td>%s</td><td>%s</td></tr>' % (esc(local), esc(label), esc(evidence),
                    srclink(page_url, "Official page"), srclink(document, "Published schedule / rules") if document else "",
                    esc(LAST_FETCH.get(target) or ""), check_badge(*dict.fromkeys([page_url, target]))))
    diff = (CHECKS.get(sched.SCHEDULE_URL) or {}).get("schedule_diff")
    summary = "Awaiting first run of the structured DeepStack IV check."
    details = ""
    if diff:
        summary = "DeepStack IV row comparison: " + diff["state"]
        if diff.get("count") is not None:
            summary += " (%d source rows; %d added, %d removed)" % (diff["count"], len(diff["added"]), len(diff["removed"]))
        changes = [(state, *r) for state in ("added", "removed") for r in diff[state]]
        if changes:
            details = "<details><summary>Review changed schedule rows</summary><ul>" + "".join(
                "<li>%s: %s %s · event #%s · sheet %s</li>" % tuple(map(esc, r)) for r in changes) + "</ul></details>"
    return ('<div class="panel" id="room-feed"><h2>Morning official schedule watch</h2>'
            '<p>Known Strip-area room sources, not a complete inventory of every room or event. The job fetches official '
            'pages and posted documents daily at 15:00 UTC (7 a.m. PST / 8 a.m. PDT). Only the Venetian DeepStack IV '
            'table has structured automatic row comparison (event number, date, start and sheet reference). '
            'Other PDFs/pages are tracked for document changes. Nothing is promoted into confirmed results by this job.</p>'
            '<p>%s</p>%s<div class="tbl-scroll"><table><thead><tr><th>Venue / slate</th><th>Evidence scope</th>'
            '<th>Operator</th><th>Schedule</th><th>Last successful fetch (UTC)</th><th>Monitor state</th>'
            '</tr></thead><tbody>%s</tbody></table></div></div>' % (esc(summary), details, "".join(rows)))


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
                         url=s["url"], date=sheet_retrieved(s),
                         use="Events %s. Buy-in split, late registration, stack, level length, payout share, "
                             "and the re-entry / add-on / rebuy finding."
                             % ", ".join("#%d" % e for e in s["events"])))
    srcs.append(dict(kind="Series", name="DeepStack Poker Series overview", url=sched.SERIES_URL,
                     date="2026-11-19", use="Series dates and the NYE / Showdown series that follow. See X-09."))
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
        for field, url in (("resort fee", h.get("resort_fee_src")), ("parking", h.get("parking_src"))):
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
    import recheck2026
    listed = {row["url"] for row in srcs}
    for label, url in recheck2026.sources().values():
        if url not in listed:
            srcs.append(dict(kind="Monitor", name=label, url=url, date="",
                             use="Scheduled source. A successful automated fetch is not a human verification date."))
    import recheck2026
    srcs.append(dict(kind="Structure rules", name="Wynn daily structures (four formats)",
                     url=fresh.WYNN_RULES, date=fresh.CHECKED, use="Four audited daily formats; all excluded for extra spend."))
    present = {row["url"] for row in srcs}
    for label, url in recheck2026.sources().values():
        if url not in present:
            srcs.append(dict(kind="Monitored reference", name=label, url=url, date="",
                             use="Change watch only; no new human-verified value implied."))
            present.add(url)
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
this page each Las Vegas morning, fingerprints the source, and appends the run to
<code>data/verified2026/checks.json</code>. A changed hash is reported rather than guessed at &mdash;
the Tournaments table then marks that row's <em>Source re-check</em> cell as <em>source changed</em> so
you know which cited value may have moved. %(monitored_sentence)s A <em>fetch error</em> means the job
could not read the document &mdash; often a bot wall (HTTP 403) or a 302 redirect on a property that
restricts scripts &mdash; and it proves nothing either way; those rows keep their previous hash and
their old read date.</p>
%(monitor)s
<p class="note">A detected change stays flagged until the source is reviewed, even if the next fetch is unchanged or fails.
Most sources are compared by document fingerprint; extracting more individual values is <a href="suggestions.html#S-07">S-07</a>.</p>
</div>

%(feed)s
%(cov)s
<div class="panel"><div class="tbl-scroll"><table><thead><tr>
<th>Kind</th><th>Document</th><th>URL</th><th class="num">Retrieved</th><th>What it is used for</th>
</tr></thead><tbody>%(rows)s</tbody></table></div></div>
""" % dict(rows=rows, n=len(srcs), ndocs=len({x["url"] for x in srcs if x["url"]}),
           monitored_sentence=monitored_sentence(monitored_n, run_n), monitor=monitor,
           cov=cov, feed=room_feed()), "sources.html")


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
    if(/^#ev\d+$/.test(location.hash)){ past.checked=true; sef.checked=false; } // A source link can cite research.
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
      cnt.textContent=shown+' of '+rows.length+' events shown.'+(sef.checked&&!shown?' No confirmed freezeout matches. Turn off the filter to see research only.':'');
    }
    [q,df,until,past,mbi,sef,ng].forEach(function(el){ el.addEventListener('input',run); el.addEventListener('change',run); });
    pills.forEach(function(p){p.addEventListener('click',function(){
      var g=p.getAttribute('data-g');
      if(activeGroups[g]) delete activeGroups[g]; else activeGroups[g]=1;
      p.classList.toggle('on'); run();
    });});
    $('#reset').addEventListener('click',function(){
      q.value=''; df.value=''; until.value=''; past.checked=false; mbi.value=''; sef.checked=true; ng.checked=false;
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
    var df2=$('#df'), ov=$('#ov'), past=$('#past'), c2=$('#c'), panels=$$('.panel[data-date]');
    var today=vegasDate();
    function run2(){
      var d=df2.value, shown=0;
      panels.forEach(function(p){
        var ok=true;
        if(d && p.getAttribute('data-date')!==d) ok=false;
        if(ok && !past.checked && !d && p.getAttribute('data-date')<today) ok=false;
        if(ok && ov.checked && p.getAttribute('data-overlap')!=='1') ok=false;
        p.style.display=ok?'':'none';
        if(ok) shown++;
      });
      c2.textContent=shown+' of '+panels.length+' days shown.';
    }
    df2.addEventListener('change',run2); ov.addEventListener('change',run2); past.addEventListener('change',run2); run2();
  }

  var google30=$('#google30');
  if(google30)google30.addEventListener('change',function(){
    $$('tr[data-google-min]').forEach(function(tr){tr.hidden=google30.checked && Number(tr.dataset.googleMin)>30;});
  });

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
        if(ok && maps.checked && tr.getAttribute('data-maps')!=='1')ok=false;
        tr.classList.toggle('hidden',!ok);
        if(ok) shown++;
      });
      wc.textContent=shown+' of '+all.length+' hotel\u2013room pairs shown ('+shownp+' rooms).';
    }
    [v,w30,w15,maps].forEach(function(el){el.addEventListener('change',run3)});
    run3();
  }

  function fmt(n){return n===null ? 'Not available' : n.toLocaleString('en-US',{style:'currency',currency:'USD'});}
  function number(input){return input.value!=='' && input.validity.valid && Number.isFinite(input.valueAsNumber)
    ? input.valueAsNumber : null;}

  function setupLodging(p, onTotal){
    var hotel=$('#'+p+'-hotel'), book=$('#'+p+'-book'), checkout=$('#'+p+'-checkout');
    var fields=['rate','fee','tax','park','nights'].map(function(key){return $('#'+p+'-'+key);});
    function update(){
      var v=fields.map(number);
      var nightly=v.slice(0,4).includes(null) ? null : Math.round(((v[0]+v[1])*(1+v[2]/100)+v[3])*100)/100;
      var n=v[4], total=nightly===null || n===null ? null : nightly*n;
      if(checkout && (checkout.value!=='' || checkout.validity.badInput)){
        total=number(checkout);
        nightly=n>0 && total!==null ? total/n : null;
      }
      if(n===0){total=0; nightly=null;}
      else if(n===null){total=null; nightly=null;}
      $(p==='t'?'#tot-night':'#h-night').textContent=fmt(nightly);
      $(p==='t'?'#tot-hotel':'#h-total').textContent=fmt(total);
      if(onTotal)onTotal(total);
    }
    hotel.addEventListener('change',function(){
      var opt=hotel.options[hotel.selectedIndex];
      fields[0].value=''; fields[1].value=opt.dataset.fee; fields[2].value=opt.dataset.tax;
      fields[3].value=p==='t'?'0':'';
      if(checkout)checkout.value='';
      book.href=opt.dataset.book || 'hotels.html#checkout-log';
      book.textContent=opt.dataset.book ? 'Official booking for '+opt.textContent : 'Official booking links and lookup log';
      update();
    });
    if(checkout)checkout.addEventListener('input',update);
    fields.forEach(function(f){f.addEventListener('input',update);}); update();
  }
  if($('#h-rate'))setupLodging('h');

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
    var pick=$('#pick'), body=$('#cart').tBodies[0], add=$('#add');
    var research=$('#research-entries'), hotelTotal=null;
    function alreadyPicked(){return pick.value && Array.from(body.rows).some(function(tr){return tr.dataset.event===pick.value;});}
    function recalc(){
      var buyin=$$('#cart tbody tr').reduce(function(sum,tr){return sum+Number(tr.dataset.subtotal);},0);
      $('#tot-buyin').textContent=fmt(buyin);
      $('#tot-all').textContent=fmt(hotelTotal===null ? null : buyin+hotelTotal);
      add.disabled=!pick.value || alreadyPicked();
    }
    function filterCart(){
      var choice=pick.value;
      Array.from(pick.options).forEach(function(o){if(o.value)o.hidden=o.disabled=!research.checked && o.dataset.confirmed!=='1';});
      if(!research.checked){
        $$('#cart tbody tr[data-research="true"]').forEach(function(tr){tr.remove();});
      }
      if(choice && (!pick.options[pick.selectedIndex] || pick.options[pick.selectedIndex].disabled))pick.value='';
      recalc();
    }
    add.addEventListener('click',function(){
      var o=pick.options[pick.selectedIndex];
      if(!o || !o.value || o.disabled || alreadyPicked())return;
      var tr=body.insertRow(), cost=Number(o.dataset.buyin);
      tr.dataset.event=o.value;
      tr.dataset.subtotal=cost;
      tr.dataset.research=o.dataset.confirmed!=='1';
      var link=document.createElement('a'); link.href='tournaments.html#ev'+o.value; link.textContent=o.textContent;
      tr.insertCell().appendChild(link); tr.insertCell().textContent=1; tr.insertCell().textContent=fmt(cost);
      var del=document.createElement('button'); del.type='button'; del.className='btn'; del.textContent='Remove';
      tr.insertCell().appendChild(del); del.addEventListener('click',function(){tr.remove();recalc();}); recalc();
    });
    pick.addEventListener('change',recalc);
    research.addEventListener('change',filterCart); setupLodging('t',function(total){hotelTotal=total;recalc();}); filterCart();
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
        "venues/resorts-world.html": p_venue_room("resorts-world", events),
        "venues/westgate.html": p_venue_room("westgate", events),
        "summary.html": p_summary(events, days),
        "latest-review.html": p_latest_review(),
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
            room_tax_pct=contentmod.ROOM_TAX["value"],
            events=[{k: v for k, v in e.items() if k != "rows"} for e in events],
            days=[{k: (v if k not in ("primary", "fallbacks", "restricted_alternatives") else
                       (v if k == "primary" else
                        [dict(note=f["note"], verdict=f["verdict"], **f["item"]) for f in v]
                        if k == "fallbacks" else v))
                   for k, v in d.items()} for d in days],
            hotels=hotelsmod.HOTELS,
            research_stay=decisions.STAY,
            quote_log=all_quotes(),
            schedule_feed=contentmod.SCHEDULE_FEED,
            google_routes_to_venetian=hotelsmod.MAPS_TO_VENETIAN,
            rate_log=[dict(date=a, property=b, field=c, value=d, source=e, note=f)
                      for a, b, c, d, e, f in hotelsmod.RATE_LOG],
            flags=contentmod.FLAGS + fresh.FLAGS,
            wynn_daily=fresh.WYNN_DAILY,
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
