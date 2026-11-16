#!/usr/bin/env python3
"""Build the verified Vegas poker planner site from scripts/dataset.py.

Design rules enforced by this build:
  * every table row links to an official host;
  * anything not read from an official source is rendered as blank + flagged;
  * the build fails if a row would be published without an official source.
"""
import json
import os
import re
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as D  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DATA = os.path.join(ROOT, "data", "site")
OFFICIAL_HOSTS = (
    "venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com",
    "mgmresorts.com", "contentstack.io", "caesars.com",
)
SITE = "Vegas Poker Planner"

# ---------------------------------------------------------------- helpers ----
def esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def money(v):
    if v in (None, ""):
        return ""
    return "${:,}".format(int(v))


def dur_minutes(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def pretty_time(t):
    if not t or ":" not in t:
        return t or ""
    h, m = t.split(":")
    h = int(h)
    ap = "AM" if h < 12 else "PM"
    hh = h % 12 or 12
    return "%d:%s %s" % (hh, m, ap)


def pretty_date(iso):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", iso or ""):
        return iso or ""
    d = datetime.strptime(iso, "%Y-%m-%d")
    return d.strftime("%a %b %-d, %Y")


def src_link(key, text=None):
    label, url = D.SOURCES[key]
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (
        esc(url), esc(text or label))


def src_count():
    return len(D.SOURCES)


# ------------------------------------------------------------- normalise ----
def build_events():
    events = []
    for i, e in enumerate(D.VENETIAN_EVENTS):
        ev = dict(e)
        ev["id"] = "V%s%s" % (e["ev"], "-" + e["flight"] if e.get("flight") else "")
        ev["venue"] = "The Venetian"
        ev["name"] = D.NAMES.get(e["ev"], "Event " + e["ev"])
        ev["view"] = "The Venetian"
        if e.get("flight"):
            ev["name"] = ev["name"] + " [" + e["flight"] + "]"
        ev["pool"] = (e["buy_in"] - e["fee"]) if e.get("fee") is not None else None
        ev["sheet_url"] = D.vsheet(e["sheet"])
        ev["sources"] = [D.SOURCES["VEVENT"][1], ev["sheet_url"]]
        ev["kind"] = e["kind"]
        ev["bounty"] = bool(e.get("bounty"))
        ev["re_entry"] = e.get("re_entry", "Not stated on the official structure sheet")
        ev["rebuy"] = e.get("rebuy", "None stated")
        ev["add_on"] = e.get("add_on", "None stated")
        # Entry-rule verdict, strictly from official text.
        if ev["kind"] == "multi-flight":
            ev["entry_class"] = "Multi-flight"
            ev["single_confirmed"] = False
            ev["rule_note"] = ("Separate starting flights; official note 8 bars a player who bags "
                               "chips from entering a later flight, so a busted flight can be "
                               "followed by another buy-in. No maximum entry count is stated.")
        elif ev["kind"] == "satellite":
            ev["entry_class"] = "Satellite"
            ev["single_confirmed"] = False
            ev["rule_note"] = "Awards direct tournament seats, not a cash prize pool."
        elif ev["kind"] == "multi-day":
            ev["entry_class"] = "Multi-day"
            ev["single_confirmed"] = False
            ev["rule_note"] = "Single Day 1, single re-entry policy not stated."
        else:
            ev["entry_class"] = "Bounty" if ev["bounty"] else "One-day NLH/PLO"
            ev["single_confirmed"] = False
            ev["rule_note"] = ("Structure sheet states no re-entry, rebuy or add-on rule. Absence of a "
                               "prohibition is not confirmation of single entry.")
        if ev["bounty"]:
            ev["entry_class"] = "Bounty"
        if ev.get("restriction"):
            ev["rule_note"] = ev["restriction"] + ". " + ev["rule_note"]
        # Descriptive guarantee ratio (never a forecast).
        if ev.get("gtd") and ev.get("buy_in"):
            ev["ratio"] = round(ev["gtd"] / float(ev["buy_in"]), 2)
            ev["entries_needed"] = -(-ev["gtd"] // ev["pool"]) if ev.get("pool") else None
        else:
            ev["ratio"] = None
            ev["entries_needed"] = None
        events.append(ev)
    for e in D.OTHER_EVENTS:
        ev = dict(e)
        ev["id"] = e["ev"]
        ev["venue"] = e["venue"]
        ev["view"] = e["venue"]
        ev["sheet_url"] = D.SOURCES[e["src"]][1]
        ev["sources"] = [ev["sheet_url"]]
        ev["bounty"] = "bounty" in (e.get("name", "").lower()) or "Bounty" in (e.get("name") or "")
        ev["single_confirmed"] = False
        ev["entry_class"] = {
            "multi-entry confirmed": "Re-entry permitted",
            "spend-advantage confirmed": "Rebuy / add-on / paid chips",
            "unverified": "Unverified",
        }[e["verdict"]]
        ev["re_entry"] = e.get("rule", "")
        ev["rebuy"] = ev.get("rule", "") if "rebuy" in (e.get("rule") or "").lower() else "None stated"
        ev["add_on"] = e.get("rule", "") if ("add-on" in (e.get("rule") or "").lower()
                                             or "add on" in (e.get("rule") or "").lower()) else "None stated"
        ev["rule_note"] = e.get("rule_short", "")
        if e.get("gtd") and e.get("buy_in"):
            ev["ratio"] = round(e["gtd"] / float(e["buy_in"]), 2)
            ev["entries_needed"] = -(-e["gtd"] // e["pool"]) if e.get("pool") else None
        else:
            ev["ratio"] = None
            ev["entries_needed"] = None
        events.append(ev)
    # source check
    for ev in events:
        for u in ev["sources"]:
            if not any(h in u for h in OFFICIAL_HOSTS):
                raise SystemExit("Refusing to publish non-official source: " + u)
    # stable chronological order: date, then start time, then venue, then event/flight,
    # so weekday names can never shuffle the table (Nov 26 must follow Nov 25).
    events.sort(key=lambda e: (
        e.get("date") or "9999-99-99",
        re.match(r"^\d", str(e.get("start") or "")) and "%05d" % (int(str(e["start"]).split(":")[0]) * 60
                                                                   + int(str(e["start"]).split(":")[1])) or "99999",
        e["venue"], str(e.get("ev")), str(e.get("flight") or "")))
    return events


EVENTS = build_events()
BY_DATE = {}
for ev in EVENTS:
    if re.match(r"^\d{4}-\d{2}-\d{2}$", ev.get("date") or ""):
        BY_DATE.setdefault(ev["date"], []).append(ev)

CONFLICT_WINDOW = 60  # minutes of slack for walking/registration between entries

def day_plan(date):
    """Primary event + conditional fallback for one date, with overlap flags."""
    evs = [e for e in BY_DATE.get(date, []) if e["venue"] == "The Venetian"]
    playable = [e for e in evs if e["kind"] in ("1day", "multi-day")]
    notes = []
    primary = None
    if playable:
        # Daytime first (a day is built around the earlier event), then the largest
        # advertised guarantee, then the earliest start.
        primary = sorted(
            playable,
            key=lambda e: (0 if dur_minutes(e["start"]) < 15 * 60 else 1,
                           -(e.get("gtd") or 0),
                           dur_minutes(e["start"])))[0]
        if dur_minutes(primary["start"]) >= 15 * 60:
            notes.append(
                "No daytime one-day event starts on this date: the only playable events begin at "
                "%s or later. The daytime slot on this date belongs to a multi-flight, satellite, "
                "restricted or restart event, which is not treated as a fresh day's main entry."
                % pretty_time(primary["start"]))
    fallback = None
    restarts = [r for r in D.VENETIAN_RESTARTS if r[0] == date]
    for r in restarts:
        notes.append("Day 2/3 restart of Event %s at %s cannot be combined with a fresh event "
                     "started the same day." % (r[2], pretty_time(r[1])))
    if primary:
        later = [e for e in playable if e is not primary
                 and dur_minutes(e["start"]) > dur_minutes(primary["start"])]
        later = sorted(later, key=lambda e: dur_minutes(e["start"]))
        for cand in later:
            gap = dur_minutes(cand["start"]) - dur_minutes(primary["start"])
            if cand.get("reg_close") and dur_minutes(cand["reg_close"]) > dur_minutes(primary["start"]) + 60:
                fallback = cand
                notes.append(
                    "%s starts %d min after the primary event. You can only take it if you are "
                    "eliminated from the primary before the fallback's late-registration close at %s "
                    "and can reach the cage %d min later. No official finish time is published, so "
                    "this stays conditional."
                    % (pretty_time(cand["start"]), gap, pretty_time(cand["reg_close"]), CONFLICT_WINDOW))
                break
            else:
                notes.append(
                    "%s starts %d min after the primary event and its registration closes at %s, "
                    "before a realistic exit, so the two cannot be played as a sequence."
                    % (pretty_time(cand["start"]), gap, pretty_time(cand.get("reg_close") or "?")))
    if len(playable) > 2:
        for e in playable:
            if e is not primary and e is not fallback:
                if dur_minutes(e["start"]) >= dur_minutes(primary["start"]):
                    notes.append("%s at %s is a further same-day option, not additive."
                                 % (e["name"], pretty_time(e["start"])))
    return dict(date=date, primary=primary, fallback=fallback, notes=notes, all=evs)


def all_overlaps():
    """Flag every pair on the same date that cannot be played in sequence."""
    out = []
    for date, evs in sorted(BY_DATE.items()):
        ven = [e for e in evs if e["venue"] == "The Venetian" and e["kind"] in ("1day", "multi-day")]
        for i in range(len(ven)):
            for j in range(i + 1, len(ven)):
                a, b = ven[i], ven[j]
                if dur_minutes(a["start"]) > dur_minutes(b["start"]):
                    a, b = b, a
                if dur_minutes(a["start"]) == dur_minutes(b["start"]):
                    out.append(dict(date=date, a=a, b=b, kind="simultaneous",
                                    detail="Both start at the same time."))
                    continue
                close = a.get("reg_close")
                if close and dur_minutes(close) <= dur_minutes(b["start"]):
                    out.append(dict(date=date, a=a, b=b, kind="sequence-blocked",
                                    detail=("A's registration closes at %s, before B starts at %s, so A "
                                            "cannot be abandoned for B after the fact. Playing both requires "
                                            "busting A before B's %s close."
                                            % (pretty_time(close), pretty_time(b["start"]),
                                               pretty_time(b.get("reg_close") or "?")))))
                else:
                    out.append(dict(date=date, a=a, b=b, kind="conditional",
                                    detail=("A and B overlap in time; a same-day sequence depends on busting "
                                            "A before B's late-registration close at %s."
                                            % pretty_time(b.get("reg_close") or "?"))))
    return out


# ------------------------------------------------------------------- pages ---
NAV = [
    ("index.html", "Dashboard"),
    ("tournaments.html", "All events"),
    ("schedule.html", "Day plan"),
    ("hotels.html", "Hotels &amp; true cost"),
    ("venues.html", "Venues"),
    ("single-entry.html", "Entry rules"),
    ("summary.html", "Executive summary"),
    ("questions.html", "Questions"),
    ("suggestions.html", "Suggestions"),
    ("flagged.html", "Flagged for review"),
    ("sources.html", "Sources &amp; monitoring"),
    ("repo-review.html", "Repo review"),
]


def head(title, desc, active, depth=0):
    up = "../" * depth
    links = "\n".join(
        '<a href="%s%s"%s>%s</a>' % (up, f, ' class="on"' if f == active else "", t)
        for f, t in NAV)
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s · %s</title>
<meta name="description" content="%s">
<link rel="stylesheet" href="%sassets/site.css">
</head><body>
<header class="top"><a class="brand" href="%sindex.html">♠ VEGAS POKER PLANNER</a>
<span class="stamp">Every value sourced · retrieved %s</span>
<button class="menu-btn" onclick="document.body.classList.toggle('nav-open')">Menu</button></header>
<div class="shell">
<nav class="side">
<p class="lbl">SECTIONS</p>
%s
<p class="lbl">NOTE</p>
<p class="mini">Blank cells are unverified, not zero. Nothing here is an offer.</p>
</nav>
<main>
""" % (esc(title), SITE, esc(desc), up, up, D.RETRIEVED, links)


def foot(depth=0):
    up = "../" * depth
    return """
<footer><p>Independent research dashboard. Official linked pages are authoritative and can change.
Sources were retrieved on %s. Verify again before paying for anything non-refundable.</p>
<p><a href="%sflagged.html">Flagged for review</a> · <a href="%ssources.html">Source register</a></p></footer>
</main></div>
<script src="%sassets/site.js"></script>
</body></html>
""" % (D.RETRIEVED, up, up, up)


def badge(text, cls="warn"):
    return '<span class="badge %s">%s</span>' % (cls, esc(text))


def write(path, html):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full) or ROOT, exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html)


# ----------------------------------------------------------- page: index -----
def page_index():
    ven = [e for e in EVENTS if e["venue"] == "The Venetian"]
    one_day = [e for e in ven if e["kind"] == "1day"]
    dates = sorted(BY_DATE)
    min_start = min(dur_minutes(e["start"]) for e in EVENTS if ":" in (e.get("start") or ""))
    earliest = [e for e in EVENTS if ":" in (e.get("start") or "")
                and dur_minutes(e["start"]) == min_start]
    h = head("Dashboard", "Source-audited Las Vegas Strip poker tournament and hotel research.", "index.html")
    h += """
<section class="hero">
<div class="eyebrow">SOURCE-AUDITED · LAS VEGAS STRIP</div>
<h1>Every tournament, every fee,<br>traced to an official page.</h1>
<p class="lede">%d events across %d venues, %d structure sheets read in full, %d official sources.
Where an organiser does not publish a value, the cell stays blank and appears on the
<a href="flagged.html">Flagged for review</a> page. Nothing here is estimated.</p>
<div class="hero-actions">
<a class="btn" href="tournaments.html">Open the event table</a>
<a class="btn ghost" href="summary.html">Read the executive summary</a>
</div>
</section>

<section class="cards">
<article class="card"><span class="k">Verified single-entry events</span><strong>0</strong>
<p>No organiser publishes an explicit one-entry-only rule. See <a href="single-entry.html">Entry rules</a>.
%s</p></article>
<article class="card"><span class="k">Official sources read</span><strong>%d</strong>
<p>Pages and PDFs retrieved on %s, listed with links in the <a href="sources.html">source register</a>.</p></article>
<article class="card"><span class="k">Earliest official start</span><strong>%s</strong>
<p>%s. There is no 08:00 AM tournament anywhere in the retrieved schedules.</p></article>
<article class="card"><span class="k">Dated hotel totals verified</span><strong>0</strong>
<p>Resort fees and one tax rate are published; no dated checkout total is. Use the
<a href="hotels.html">true-cost calculator</a> with a live quote.</p></article>
</section>

<section class="block">
<div class="head"><h2>Search everything</h2><p>Filter the full event table by text, date, buy-in and entry type.</p></div>
<div class="toolbar">
<input id="q" class="search" type="search" placeholder="Search venue, event, buy-in, rule…" aria-label="Search all tables">
<select id="f-date"><option value="">Any date</option>%s</select>
<select id="f-class"><option value="">Any entry type</option>%s</select>
<select id="f-max"><option value="">Any buy-in</option><option value="200">≤ $200</option><option value="400">≤ $400</option><option value="600">≤ $600</option><option value="1100">≤ $1,100</option></select>
<label class="chk"><input type="checkbox" id="f-single"> Single entry confirmed only</label>
</div>
<p class="hint" id="tcount"></p>
<div class="tw"><table class="t" id="evtable">
<thead><tr><th>Date</th><th>Start</th><th>Venue</th><th>Event</th><th class="num">Buy-in</th>
<th class="num">Fee withheld</th><th class="num">GTD</th><th>Entry type</th><th>Official source</th></tr></thead>
<tbody>%s</tbody></table></div>
</section>

<section class="block">
<div class="head"><h2>Trip cost calculator</h2>
<p>Entries × buy-in, plus nights × true hotel cost per night. Hotel figures must come from a dated
quote you can see; the site will not invent one.</p></div>
<div class="calc" id="calc">
<fieldset><legend>Tournament entries</legend>
<label>Number of entries <input type="number" id="c-entries" value="4" min="0" max="40"></label>
<label>Average buy-in ($) <input type="number" id="c-buyin" value="600" min="0" step="50"></label>
</fieldset>
<fieldset><legend>Hotel</legend>
<label>Nights <input type="number" id="c-nights" value="5" min="0" max="60"></label>
<label>Nightly room rate ($) <input type="number" id="c-rate" value="" placeholder="from a live official quote"></label>
<label>Resort fee per night ($) <input type="number" id="c-fee" value="55" min="0"></label>
<label>Room tax (%%) <input type="number" id="c-tax" value="13.38" step="0.01" min="0"></label>
<label>Parking per day ($) <input type="number" id="c-park" value="0" min="0"></label>
<label>Other per-night fees ($) <input type="number" id="c-other" value="0" min="0"></label>
</fieldset>
<div class="out" id="c-out"></div>
</div>
<p class="hint">Why this defaults to $55 and 13.38%%: both are printed on official Venetian pages
(%s and %s). Other properties publish a resort fee but not a tax percentage, so do not copy the
Venetian rate onto them — see <a href="flagged.html">F-05</a>.</p>
</section>

<section class="block">
<div class="head"><h2>What this build actually verified</h2></div>
<div class="two">
<div><h3>Read in full</h3><ul class="tick">
<li>Official DSE IV schedule <b>PDF</b> — every row: date, event number, time, registration close, guarantee, chips, level length.</li>
<li>All <b>37</b> official Venetian structure sheets — buy-in split, late-registration close, starting stack, level length, payout share.</li>
<li>Official DSE IV event page, series overview, poker room page, resort fee page, hotel terms, poker suite rates.</li>
<li>Wynn WPT schedule PDF and the structures PDF sections for general terms, $600/$400K, TORSE, PLO $400 and Mixed Triple Draw.</li>
<li>Wynn daily structures PDF (Mon–Thu, Fri rebuy, Sat–Sun) and the daily poster.</li>
<li>Bellagio Friday $600 terms; Caesars Palace daily flyer; MGM Grand $120 structure and terms; Horseshoe property page.</li>
</ul></div>
<div><h3>Deliberately blank</h3><ul class="cross">
<li>Every walking time between a hotel and a poker room.</li>
<li>Every dated room rate and checkout total.</li>
<li>Re-entry status for one-day Venetian events.</li>
<li>Room-tax percentage for Wynn, Bellagio, MGM Grand and Caesars properties.</li>
<li>Any 08:00 AM tournament.</li>
</ul>
<p class="mini">Blank means "not on an official source we could read", not "free" and not "no".</p></div>
</div>
</section>
""" % (len(EVENTS), len(set(e["venue"] for e in EVENTS)), 37, src_count(),
       badge("Blocked", "block"), src_count(), D.RETRIEVED,
       pretty_time(earliest[0]["start"]) if earliest else "",
       esc(earliest[0]["name"] + " — " + earliest[0]["venue"]) if earliest else "",
       "".join('<option value="%s">%s</option>' % (d, pretty_date(d)) for d in dates),
       "".join('<option value="%s">%s</option>' % (c, c) for c in sorted(
           set(e["entry_class"] for e in EVENTS))),
       rows_events(EVENTS, limit=None),
       src_link("VFEE", "resort fee page"), src_link("VTC", "hotel terms"))
    h += foot()
    write("index.html", h)


def rows_events(events, limit=None):
    out = []
    for e in events[:limit] if limit else events:
        srcs = " ".join('<a href="%s" target="_blank" rel="noopener">%s</a>' % (
            esc(u), "schedule" if "dse-nov-2026.html" in u else
            ("structure %s" % e["sheet"] if (u == e.get("sheet_url") and e.get("sheet")) else "official"))
            for u in e["sources"])
        cls = {"Re-entry permitted": "nav", "Rebuy / add-on / paid chips": "warn",
               "Multi-flight": "warn", "Unverified": "rev",
               "Satellite": "rev"}.get(e["entry_class"], "")
        date_cell = pretty_date(e["date"]) if re.match(r"^\d{4}", str(e["date"])) else esc(e["date"])
        out.append(
            '<tr data-date="%s" data-class="%s" data-buyin="%s" data-single="%s">'
            '<td class="nowrap">%s</td><td class="nowrap">%s</td><td>%s</td><td>%s</td>'
            '<td class="num">%s</td><td class="num">%s%s</td><td class="num">%s</td>'
            '<td><span class="badge %s">%s</span></td><td class="src">%s</td></tr>' % (
                esc(e.get("date")), esc(e["entry_class"]), esc(e.get("buy_in") or ""),
                "yes" if e["single_confirmed"] else "no",
                date_cell, esc(pretty_time(e["start"]) if re.match(r"^\d", str(e["start"])) else e["start"]),
                esc(e["venue"]), esc(e["name"]),
                money(e.get("buy_in")),
                money(e.get("fee")),
                ('<br><span class="mini">%s</span>' % esc(e["fee_note"])) if e.get("fee_note") else "",
                money(e.get("gtd")) or "—",
                cls, esc(e["entry_class"]), srcs))
    return "\n".join(out)


# ------------------------------------------------------- page: tournaments ----
def page_tournaments():
    h = head("All events", "Every verified event with fee split, guarantee and entry-rule verdict.",
             "tournaments.html")
    h += """
<section class="hero small"><div class="eyebrow">FULL TABLE</div>
<h1>All verified events</h1>
<p class="lede">%d rows. Each row links to the official schedule and, where one exists, the
official structure sheet the fee and rule text came from.</p></section>

<div class="toolbar">
<input id="q" class="search" type="search" placeholder="Search venue, event, buy-in, rule…">
<select id="f-date"><option value="">Any date</option>%s</select>
<select id="f-class"><option value="">Any entry type</option>%s</select>
<select id="f-max"><option value="">Any buy-in</option><option value="200">≤ $200</option><option value="400">≤ $400</option><option value="600">≤ $600</option><option value="1100">≤ $1,100</option></select>
<label class="chk"><input type="checkbox" id="f-single"> Single entry confirmed only</label>
</div>
<p class="hint" id="tcount"></p>
<div class="tw"><table class="t" id="evtable">
<thead><tr><th>Date</th><th>Start</th><th>Venue</th><th>Event</th><th class="num">Buy-in</th>
<th class="num">Fee withheld</th><th class="num">GTD</th><th>Entry type</th><th>Official source</th></tr></thead>
<tbody>%s</tbody></table></div>
<p class="note"><b>Fee withheld</b> is the total the official structure sheet says is deducted from the
buy-in, i.e. buy-in minus the amount allocated to the prize pool, so the column reconciles exactly with
the published pool money. Where an organiser's own breakdown includes a third-party series fee or an
optional gratuity inside that total, the breakdown is printed under the figure (LIPS events, Bellagio,
MGM Grand). Wynn rows combine the tournament fee and the poker staff service charge for the same reason.</p>
""" % (len(EVENTS),
       "".join('<option value="%s">%s</option>' % (d, pretty_date(d)) for d in sorted(BY_DATE)),
       "".join('<option value="%s">%s</option>' % (c, c) for c in sorted(set(e["entry_class"] for e in EVENTS))),
       rows_events(EVENTS))
    h += foot()
    write("tournaments.html", h)


# ---------------------------------------------------------- page: schedule ----
def page_schedule():
    days = [day_plan(d) for d in sorted(BY_DATE)]
    rows = []
    for d in days:
        p = d["primary"]
        f = d["fallback"]
        if not p and not f:
            continue
        rows.append(
            '<tr><td class="nowrap">%s</td><td>%s</td><td>%s</td><td class="mini">%s</td></tr>' % (
                pretty_date(d["date"]),
                ('<b>%s</b><br><span class="mini">%s · %s · %s</span>' % (
                    esc(p["name"]), esc(pretty_time(p["start"])), money(p["buy_in"]),
                    ("GTD " + money(p["gtd"])) if p.get("gtd") else "no guarantee listed"))
                if p else '<span class="blank">No fresh event</span>',
                ('%s<br><span class="mini">%s · %s · late reg closes %s</span>' % (
                    esc(f["name"]), esc(pretty_time(f["start"])), money(f["buy_in"]),
                    esc(pretty_time(f.get("reg_close") or "?")))
                 if f else '<span class="blank">None available</span>'),
                "<br>".join(esc(n) for n in d["notes"]) if d["notes"] else ""))
    ov = all_overlaps()
    orows = []
    for o in ov:
        orows.append('<tr><td class="nowrap">%s</td><td>%s</td><td>%s</td><td>%s</td><td class="mini">%s</td></tr>' % (
            pretty_date(o["date"]), esc(o["a"]["name"]), esc(o["b"]["name"]),
            badge({"simultaneous": "Same start", "sequence-blocked": "Cannot sequence",
                   "conditional": "Conditional"}[o["kind"]],
                  {"simultaneous": "rev", "sequence-blocked": "warn", "conditional": "block"}[o["kind"]]),
            esc(o["detail"])))
    h = head("Day plan", "Primary event plus conditional fallback for every festival date.",
             "schedule.html")
    h += """
<section class="hero small"><div class="eyebrow">DAY BY DAY</div>
<h1>One primary event per day,<br>one conditional fallback.</h1>
<p class="lede">Built from official start times, official late-registration close times and the
official level structure. Because no organiser publishes an expected finish time, a second event on
the same day is always conditional, never a plan.</p></section>

<section class="block">
<div class="head"><h2>The planner</h2>
<p><b>Primary</b> = a one-day event that starts before 3:00 PM, so the day is used from the morning;
among those, the largest advertised guarantee wins and ties break earlier. If a date has no daytime
one-day event, the primary becomes the largest-guarantee event of any start time and the row says so —
presenting an evening-only day as a full day would be misleading. Multi-flight, satellite, restricted
and restart events are excluded from the primary slot because they cannot be freely swapped once a
flight has been played. <b>Fallback</b> = a later one-day event whose late-registration close still
leaves a realistic chance of entering after a bust, so it is usable if the primary sells out at the
cage.</p></div>
<div class="tw"><table class="t"><thead><tr><th>Date</th><th>Primary event</th>
<th>Conditional fallback</th><th>Overlap / sequencing note</th></tr></thead><tbody>
%s</tbody></table></div>
</section>

<section class="block">
<div class="head"><h2>Overlap check</h2>
<p>Every same-day pair of one-day Venetian events, tested against the official registration close.
A pair is <em>sequence-blocked</em> when the earlier event's registration shuts before the later one
starts — you then cannot be in the later event unless you busted out of the earlier one in time.</p></div>
<div class="tw"><table class="t"><thead><tr><th>Date</th><th>Event A</th><th>Event B</th>
<th>Verdict</th><th>Why</th></tr></thead><tbody>
%s</tbody></table></div>
</section>

<section class="block">
<div class="head"><h2>Why the day cannot start at 08:00</h2></div>
<p>No official schedule retrieved in this build lists an 08:00 AM tournament. The earliest verified
starts are:</p>
<div class="tw"><table class="t"><thead><tr><th>Time</th><th>Event</th><th>Venue</th><th>Source</th></tr></thead>
<tbody>
<tr><td>9:10 AM</td><td>$260 NLH Turbo Milestone Satellite (Event 46, Dec 12)</td><td>The Venetian</td><td>%s</td></tr>
<tr><td>10:00 AM</td><td>Super Gold Million Mystery Bounty Day 1A (Dec 10-11)</td><td>Wynn</td><td>%s</td></tr>
<tr><td>10:00 AM</td><td>Daily $100 NLH $1,000 GTD</td><td>Caesars Palace</td><td>%s</td></tr>
<tr><td>10:10 AM</td><td>RaceDay Stack, Seniors, $1,100 NLH flights</td><td>The Venetian</td><td>%s</td></tr>
</tbody></table></div>
<p class="note">Flagged as <a href="flagged.html">F-10</a>.</p>
</section>
""" % ("".join(rows), "".join(orows),
       src_link("VEVENT", "official schedule"), src_link("WPSCHED", "WPT schedule PDF"),
       src_link("CPCAL", "Caesars Palace flyer"), src_link("VSCHED", "official schedule PDF"))
    h += foot()
    write("schedule.html", h)


# ------------------------------------------------------------ page: hotels ----
def page_hotels():
    rows = []
    for x in D.HOTELS:
        fee = money(x["resort_fee"]) if x["resort_fee"] is not None else '<span class="blank">blank</span>'
        tax = ("%.2f%%" % x["tax_rate"]) if x["tax_rate"] else '<span class="blank">blank</span>'
        rate = ("from %s" % money(x["poker_rate"])) if x["poker_rate"] else '<span class="blank">blank</span>'
        walk = money(x["walk_min"]) if x.get("walk_min") else '<span class="blank">blank</span>'
        rows.append(
            '<tr><td><b>%s</b><br><span class="mini">%s</span></td><td class="mini">%s</td>'
            '<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
            '<td class="mini">%s</td><td class="num">%s</td><td class="src">%s</td></tr>' % (
                esc(x["name"]), esc(x["tower"]), esc(x["poker_room"]), fee, tax, rate,
                esc(x["poker_rate_note"]) if x["poker_rate"] else '<span class="blank">No published poker rate</span>',
                walk, " ".join(src_link(k, "official") for k in x["srcs"])))
    logrows = []
    for x in D.HOTELS:
        for r in x["rate_log"]:
            logrows.append(
                '<tr><td class="nowrap">%s</td><td>%s</td><td>%s</td><td class="num">%s</td>'
                '<td class="mini">%s</td><td class="src">%s</td></tr>' % (
                    esc(r["checked"]), esc(x["name"]), esc(r["field"]),
                    esc(r["value"]) if r["value"] else '<span class="blank">blank</span>',
                    esc(r["note"] or ""),
                    ('<a href="%s" target="_blank" rel="noopener">official</a>' % esc(r["source"]))
                    if r["source"] else '<span class="blank">no source</span>'))
    h = head("Hotels & true cost", "Resort fees, published room-tax rate, parking and a dated rate log.",
             "hotels.html")
    h += """
<section class="hero small"><div class="eyebrow">LODGING</div>
<h1>What a night really costs</h1>
<p class="lede">A nightly rate is not the cost. The comparable figure is
<code>(room rate + mandatory resort fee + taxes + parking) ÷ nights</code>, taken from a dated quote
for the exact stay. Only the components printed on official pages are filled in here; the rest is blank.</p></section>

<section class="block">
<div class="head"><h2>Hotel components</h2>
<p>Fees, taxes and parking exactly as published. Walking time is blank for every property because no
official source states one.</p></div>
<div class="tw"><table class="t"><thead><tr><th>Property</th><th>Poker room location</th>
<th class="num">Resort fee / night</th><th class="num">Room tax</th><th class="num">Poker rate</th>
<th>Rate conditions</th><th class="num">Walk (min)</th><th>Official source</th></tr></thead>
<tbody>%s</tbody></table></div>
<p class="note">Venetian poker room is on Palazzo level 2 in the Grand Canal Shoppes; Wynn's poker room
is inside Encore. That is a description of the location, not a walking time.</p>
</section>

<section class="block">
<div class="head"><h2>Dated rate log</h2>
<p>Rates are stored as observations with a date and a source, never as a single remembered value.
A new check appends a row; nothing is silently overwritten.</p></div>
<div class="tw"><table class="t"><thead><tr><th>Checked</th><th>Property</th><th>Field</th>
<th class="num">Value</th><th>Note</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div>
</section>

<section class="block">
<div class="head"><h2>True cost per night calculator</h2>
<p>Enter a nightly rate copied from the property's own booking page for your exact dates. The
calculator applies the fees and tax that the official pages publish for the property you name.</p></div>
<div class="calc">
<fieldset><legend>Stay</legend>
<label>Nights <input type="number" id="c-nights" value="5" min="0" max="60"></label>
<label>Nightly room rate ($) <input type="number" id="c-rate" placeholder="from a live official quote"></label>
<label>Resort fee / night ($) <input type="number" id="c-fee" value="55" min="0"></label>
<label>Room tax (%%) <input type="number" id="c-tax" value="13.38" step="0.01" min="0"></label>
<label>Parking / day ($) <input type="number" id="c-park" value="0" min="0"></label>
<label>Other per-night fees ($) <input type="number" id="c-other" value="0" min="0"></label>
</fieldset>
<div class="out" id="c-out"></div>
</div>
<h3>What tax rate to use</h3>
<div class="tw"><table class="t"><thead><tr><th>Property</th><th>Room tax published?</th><th>Source</th></tr></thead><tbody>
<tr><td>The Venetian / Palazzo</td><td>Yes — 13.38%% Clark County Room Tax</td><td>%s</td></tr>
<tr><td>Wynn / Encore</td><td><span class="blank">No percentage printed</span></td><td>%s</td></tr>
<tr><td>Bellagio</td><td><span class="blank">No percentage printed</span></td><td>%s</td></tr>
<tr><td>MGM Grand</td><td><span class="blank">No percentage printed</span></td><td>%s</td></tr>
<tr><td>Caesars Palace / Horseshoe</td><td><span class="blank">No official page retrieved</span></td><td>—</td></tr>
</tbody></table></div>
<p class="note">Applying 13.38%% to a non-Venetian property would be an inference. It is flagged as
<a href="flagged.html">F-05</a>.</p>

<h3>Parking as published (Venetian)</h3>
<ul class="tick">
<li>Registered hotel guests: $20/day, seven days a week.</li>
<li>Non-hotel guests: $20 Monday–Thursday, $25 Friday–Sunday.</li>
<li>Valet: $40/day.</li>
<li>Venetian Rewards Sapphire and above: complimentary self-parking; Ruby and above: complimentary valet.</li>
<li>Non-registered guests who play three hours or more in tournaments or cash games: complimentary self-parking (poker room page).</li>
<li>Incidental hold: $150 per night for non-Signature Suites.</li>
</ul>
<p class="mini">Source: %s · %s</p>
</section>
""" % ("".join(rows), "".join(logrows),
       src_link("VTC"), src_link("WINFO"), src_link("BTC"), src_link("MGMTC"),
       src_link("VTC"), src_link("VPOKER"))
    h += foot()
    write("hotels.html", h)


# ----------------------------------------------------- page: single-entry ----
def page_single_entry():
    conf = [e for e in EVENTS if e["single_confirmed"]]
    reentry = [e for e in EVENTS if e["entry_class"] == "Re-entry permitted"]
    spend = [e for e in EVENTS if e["entry_class"].startswith("Rebuy")]
    unknown = [e for e in EVENTS if e["venue"] == "The Venetian"
               and e["kind"] == "1day"]
    rows = []
    for e in sorted(EVENTS, key=lambda x: (x["venue"], str(x["date"]))):
        rows.append(
            '<tr><td><b>%s</b><br><span class="mini">%s · %s</span></td><td>%s</td>'
            '<td class="mini">%s</td><td class="num">%s</td><td class="mini">%s</td>'
            '<td class="src">%s</td></tr>' % (
                esc(e["venue"]), esc(pretty_date(e["date"]) if re.match(r"^\d{4}", str(e["date"])) else e["date"]),
                esc(e["name"]), badge(e["entry_class"],
                                      {"Re-entry permitted": "nav", "Rebuy / add-on / paid chips": "warn",
                                       "Unverified": "rev"}.get(e["entry_class"], "block")),
                esc(e["re_entry"] if e["venue"] != "The Venetian"
                    else ("Not stated — " + e["rule_note"])),
                money(e.get("buy_in")),
                esc(e.get("rule_short") or e.get("restriction") or ""),
                e["sources"][0] and '<a href="%s" target="_blank" rel="noopener">official</a>' % esc(e["sources"][-1])))
    h = head("Entry rules", "Which events are genuinely single-entry — and why none can be confirmed yet.",
             "single-entry.html")
    h += """
<section class="hero small"><div class="eyebrow">THE CORE QUESTION</div>
<h1>Confirmed single-entry events: <span class="big-num">%d</span></h1>
<p class="lede">A single-entry screen means the organiser states, in writing, that you get one entry,
no rebuy and no add-on. Not one official document retrieved in this build says that. Every organiser
that does publish a rule publishes a <em>permissive</em> one.</p></section>

<section class="block">
<div class="head"><h2>What the official text actually says</h2>
<p>Rows below quote or summarise the organiser's own words. Where the official text is silent, the row
says silent — it does not say "single entry".</p></div>
<div class="tw"><table class="t"><thead><tr><th>Venue / event</th><th>Entry verdict</th>
<th>Official rule text</th><th class="num">Buy-in</th><th>Short form</th><th>Source</th></tr></thead>
<tbody>%s</tbody></table></div>
</section>

<section class="block">
<div class="head"><h2>Three groups</h2></div>
<div class="three">
<article class="card"><span class="k">Group A · unconfirmed</span><strong>%d</strong>
<p>Venetian one-day events. The structure sheet states the fee split, stack, level length and
late-registration close, and says nothing about re-entry. <b>Silent is not the same as banned.</b></p></article>
<article class="card"><span class="k">Group B · re-entry permitted</span><strong>%d</strong>
<p>Wynn $600/$400K and PLO, Wynn Mon–Thu and Sat–Sun dailies, Bellagio Friday $600. Official text
permits a second entry, so max spend is unbounded or bounded only by the stated window.</p></article>
<article class="card"><span class="k">Group C · money buys chips</span><strong>%d</strong>
<p>Wynn Friday rebuy + add-on, Caesars Palace $50 add-on for 15,000 chips, Bellagio's $40 voluntary
gratuity for 15,000 chips, MGM Grand's $11 voluntary gratuity for 10,000 chips, and every Venetian
PokerAtlas/Valuetown rake discount that changes the effective price by entry status.</p></article>
</div>
<p class="note">Toggle on the <a href="tournaments.html">event table</a>: "Single entry confirmed only"
returns %d rows today. It will start returning rows the moment an official rule is confirmed.</p>
</section>

<section class="block">
<div class="head"><h2>The unresolved Venetian family</h2>
<p>These are the events that would qualify if the room confirms a one-entry rule. They are shown
individually rather than as a recommendation, because the rule is unconfirmed.</p></div>
<div class="tw"><table class="t"><thead><tr><th>Date</th><th>Start</th><th>Event</th>
<th class="num">Buy-in</th><th class="num">To prize pool</th><th class="num">GTD</th>
<th class="num">GTD ÷ buy-in</th><th>Late reg closes</th><th class="num">Stack</th>
<th class="num">Level (min)</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div>
<p class="note">GTD ÷ buy-in is a description of the advertised floor, not an expectation of return and
not a forecast. The last column set also answers a factual question: at the per-entry prize-pool
allocation printed on the sheet, the event needs roughly <b>%s</b> entries before the advertised
guarantee is covered by entry money alone. Above that number the guarantee is funded by the field;
below it, by the organiser.</p>
</section>
""" % (len(conf), "".join(rows), len(unknown), len(reentry), len(spend), len(conf),
       "".join(
           '<tr><td class="nowrap">%s</td><td class="nowrap">%s</td><td>%s</td>'
           '<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
           '<td class="num">%s</td><td class="nowrap">%s</td><td class="num">%s</td>'
           '<td class="num">%s</td><td class="src"><a href="%s" target="_blank" rel="noopener">sheet %s</a></td></tr>' % (
               pretty_date(e["date"]), esc(pretty_time(e["start"])), esc(e["name"]),
               money(e["buy_in"]), money(e["pool"]), money(e["gtd"]) or "—",
               ("%.1f×" % e["ratio"]) if e["ratio"] else "—",
               esc(pretty_time(e.get("reg_close") or "?")), "{:,}".format(e["chips"]),
               esc(str(e["level"])), esc(e["sheet_url"]), e["sheet"])
           for e in sorted(unknown, key=lambda x: (x["date"], x["start"]))),
       ", ".join("{:,}".format(e["entries_needed"]) for e in
                 sorted([x for x in unknown if x.get("entries_needed")],
                        key=lambda x: x["date"])[:3]))
    h += foot()
    write("single-entry.html", h)


# ------------------------------------------------------------- page: venues ---
VENUE_PAGES = ["The Venetian", "Wynn", "Bellagio", "Caesars Palace", "MGM Grand", "Horseshoe Las Vegas"]
SLUG = {"The Venetian": "venetian", "Wynn": "wynn", "Bellagio": "bellagio",
        "Caesars Palace": "caesars-palace", "MGM Grand": "mgm-grand",
        "Horseshoe Las Vegas": "horseshoe"}
HOTEL_FOR = {"The Venetian": ["venetian", "palazzo"], "Wynn": ["wynn", "encore"],
             "Bellagio": ["bellagio"], "Caesars Palace": ["caesars-palace"],
             "MGM Grand": ["mgm-grand"], "Horseshoe Las Vegas": ["horseshoe"]}


def page_venues():
    cards = []
    for v in VENUE_PAGES:
        evs = [e for e in EVENTS if e["venue"] == v]
        cards.append('<a class="venue-card" href="venues/%s.html"><h3>%s</h3>'
                     '<p class="mini">%s</p><span class="k">%d event rows</span>'
                     '<span class="k">%d hotel(s)</span></a>' % (
                         SLUG[v], esc(v),
                         esc(", ".join(sorted(set(e["entry_class"] for e in evs)))),
                         len(evs), len(HOTEL_FOR[v])))
    h = head("Venues", "One page per venue with its events and hotels.", "venues.html")
    h += """
<section class="hero small"><div class="eyebrow">BY VENUE</div>
<h1>One page per venue</h1>
<p class="lede">Each venue page carries that property's verified events, its published fees, and the
hotels on the same footprint. Nothing is merged across properties, because fee and tax rules differ.</p></section>
<section class="block"><div class="venues">%s</div></section>
""" % ("".join(cards))
    h += foot()
    write("venues.html", h)

    for v in VENUE_PAGES:
        evs = sorted([e for e in EVENTS if e["venue"] == v],
                     key=lambda e: (str(e["date"]), str(e["start"])))
        hotels = [x for x in D.HOTELS if x["id"] in HOTEL_FOR[v]]
        hrows = "".join(
            '<tr><td><b>%s</b><br><span class="mini">%s</span></td><td class="num">%s</td>'
            '<td class="num">%s</td><td class="num">%s</td><td class="mini">%s</td>'
            '<td class="num">%s</td><td class="src">%s</td></tr>' % (
                esc(x["name"]), esc(x["poker_room"]),
                money(x["resort_fee"]) if x["resort_fee"] is not None else '<span class="blank">blank</span>',
                ("%.2f%%" % x["tax_rate"]) if x["tax_rate"] else '<span class="blank">blank</span>',
                ("from %s" % money(x["poker_rate"])) if x["poker_rate"] else '<span class="blank">blank</span>',
                esc(x["cancel"]),
                '<span class="blank">blank</span>',
                " ".join(src_link(k, "official") for k in x["srcs"]))
            for x in hotels)
        h = head(v, "%s events and hotels, sourced to official pages." % v, "venues.html", depth=1)
        h += """
<section class="hero small"><div class="eyebrow">VENUE</div><h1>%s</h1>
<p class="lede">%d verified event rows and %d hotel records on the same footprint.</p></section>

<section class="block"><div class="head"><h2>Events</h2></div>
<div class="tw"><table class="t"><thead><tr><th>Date</th><th>Start</th><th>Event</th>
<th class="num">Buy-in</th><th class="num">Fee</th><th class="num">GTD</th><th>Entry type</th>
<th>Last checked</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div></section>

<section class="block"><div class="head"><h2>Hotels at this venue</h2>
<p>Walk time is blank: no official source publishes one.</p></div>
<div class="tw"><table class="t"><thead><tr><th>Property</th><th class="num">Resort fee</th>
<th class="num">Room tax</th><th class="num">Poker rate</th><th>Cancellation</th>
<th class="num">Walk (min)</th><th>Source</th></tr></thead><tbody>%s</tbody></table></div></section>

<p class="note">Last checked: %s. Re-check the official pages before paying.</p>
""" % (esc(v), len(evs), len(hotels),
       "".join('<tr><td class="nowrap">%s</td><td class="nowrap">%s</td><td>%s</td>'
               '<td class="num">%s</td><td class="num">%s</td><td class="num">%s</td>'
               '<td>%s</td><td class="nowrap">%s</td><td class="src">%s</td></tr>' % (
                   esc(pretty_date(e["date"]) if re.match(r"^\d{4}", str(e["date"])) else e["date"]),
                   esc(pretty_time(e["start"]) if re.match(r"^\d", str(e["start"])) else e["start"]),
                   esc(e["name"]), money(e.get("buy_in")), money(e.get("fee")),
                   money(e.get("gtd")) or "—",
                   badge(e["entry_class"], {"Re-entry permitted": "nav",
                                            "Rebuy / add-on / paid chips": "warn",
                                            "Unverified": "rev"}.get(e["entry_class"], "block")),
                   D.RETRIEVED,
                   '<a href="%s" target="_blank" rel="noopener">official</a>' % esc(e["sources"][-1]))
               for e in evs) or '<tr><td colspan="9" class="blank">No event rows verified for this venue.</td></tr>',
       hrows or '<tr><td colspan="7" class="blank">No hotel record.</td></tr>',
       D.RETRIEVED)
        h += foot(depth=1)
        write("venues/%s.html" % SLUG[v], h)


# ------------------------------------------------------------ page: summary ---
def page_summary():
    best_pool = sorted([e for e in EVENTS if e.get("gtd")], key=lambda e: -e["gtd"])[:5]
    best_ratio = sorted([e for e in EVENTS if e.get("ratio")], key=lambda e: -e["ratio"])[:5]
    h = head("Executive summary", "What is verified, what it means, and what is still missing.",
             "summary.html")
    h += """
<section class="hero small"><div class="eyebrow">EXECUTIVE SUMMARY</div>
<h1>What the evidence supports</h1>
<p class="lede">Snapshot %s. %d official sources read. %d event rows. Nothing estimated.</p></section>

<section class="block">
<h2>1. The bottom line</h2>
<div class="callout">
<p><b>A fully optimised, bookable itinerary cannot be produced from official sources today.</b>
Not because the schedules are unknown — they are known in detail — but because three pieces a
booking decision needs are published by nobody: a confirmed one-entry rule, a dated hotel total, and
a walking time.</p>
<p>What <em>can</em> be done, and is done on this site, is narrower and still useful: every official
start time, buy-in, fee split, guarantee, starting stack, level length and late-registration close for
the Venetian DeepStack Extravaganza IV festival (Nov 16 – Dec 23, 2026) is transcribed and linked, plus
the rules of the competing Wynn, Bellagio, Caesars Palace and MGM Grand events.</p>
</div>
</section>

<section class="block">
<h2>2. What is genuinely verified</h2>
<div class="two">
<div><ul class="tick">
<li><b>__VEV__ Venetian event rows</b> for the festival, from the official schedule PDF and all 37 official structure sheets.</li>
<li><b>Fee split per buy-in</b> — e.g. $58 of every $300, $90 of every $600, $130 of every $1,100, $225 of every $2,200 — straight from the sheets.</li>
<li><b>Registration close times</b> per event, printed on both the schedule PDF and each structure sheet, and they agree.</li>
<li><b>Guarantees</b> per event, including the cases where the guarantee includes bounties.</li>
<li><b>Entry rules for four competing venues</b>, quoted, including the permissive ones.</li>
<li><b>Venetian hotel economics</b>: $55 resort fee plus tax, 13.38%% Clark County room tax, $20/day guest parking, $150/night incidental hold, 3 PM check-in / 11 AM check-out.</li>
<li><b>Poker suite rate</b>: from $119 (Venetian) / $209 (Palazzo), conditional on six hours of live cash play or a $300+ tournament entry per night.</li>
</ul></div>
<div><ul class="cross">
<li><b>No</b> confirmed single-entry event, anywhere.</li>
<li><b>No</b> dated room rate or checkout total.</li>
<li><b>No</b> walking time between any hotel and any poker room.</li>
<li><b>No</b> published expected finish time for any event.</li>
<li><b>No</b> 08:00 AM start anywhere.</li>
<li><b>No</b> room-tax percentage for Wynn, Bellagio, MGM Grand or the Caesars properties.</li>
<li><b>No</b> expected field size, so no basis for an expected return.</li>
</ul></div>
</div>
</section>

<section class="block">
<h2>3. Largest advertised guarantees (descriptive only)</h2>
<div class="tw"><table class="t"><thead><tr><th>Event</th><th>Venue</th><th>Date</th>
<th class="num">GTD</th><th class="num">Buy-in</th><th class="num">GTD ÷ buy-in</th><th>Entry type</th><th>Source</th></tr></thead><tbody>
%s</tbody></table></div>
<p class="note">A guarantee is a floor the organiser must pay, not a forecast of your return. The ratio
is shown because it is arithmetic on two published numbers, not because it predicts anything.</p>
</section>

<section class="block">
<h2>4. Highest advertised guarantee per dollar of buy-in</h2>
<div class="tw"><table class="t"><thead><tr><th>Event</th><th>Venue</th><th>Date</th>
<th class="num">GTD</th><th class="num">Buy-in</th><th class="num">Ratio</th><th>Entry type</th></tr></thead><tbody>
%s</tbody></table></div>
<p class="note">The top of this list is dominated by bounty events, whose guarantee includes bounty
money paid out hand by hand. They are labelled, not hidden, and they are not comparable line-for-line
with a plain prize-pool guarantee.</p>
</section>

<section class="block">
<h2>5. Hotel position</h2>
<p>On the published components, the Venetian/Palazzo is the only property where the poker room is in
the same building complex as the rooms, and it is the only property that publishes both a room-tax rate
(13.38%%) and a poker-specific rate (from $119/$209, conditional). Wynn, Bellagio and MGM Grand each
publish a $55 or $50 resort fee plus tax but no percentage; Caesars Palace and Horseshoe publish no
resort-fee figure we could retrieve.</p>
<p>That is a component comparison across five properties, and a component comparison alone cannot rank
them. A ranked hotel list needs a dated quote for the identical nights, which does not exist in this
snapshot — see <a href="hotels.html">Hotels &amp; true cost</a> and
<a href="flagged.html#F-04">F-04</a>.</p>
</section>

<section class="block">
<h2>6. The honest recommendation</h2>
<div class="callout">
<p><b>Objective that the evidence supports:</b> maximise verified entries per day inside the Venetian
festival window, using one-day events, and treat any second event on a day as a conditional fallback.</p>
<ol class="steps">
<li>Choose the week. The festival runs Nov 16 – Dec 23, 2026; the Wynn WPT series overlaps Nov 27 – Dec 21, which is also when Wynn suspends its daily events.</li>
<li>Get the one-entry answer in writing from the Venetian poker room (702.414.7657) for the one-day events you care about. Until then, budget as if a second entry is possible.</li>
<li>Price one dated week at the Venetian with the poker rate (866.255.8936, code EPOKR25) and one at the public rate, then compare like-for-like in the calculator.</li>
<li>Sequence from the <a href="schedule.html">day plan</a>: one primary event per day, evening event only as a conditional fallback.</li>
<li>Re-check the official pages, the policies and the rates immediately before any non-refundable payment.</li>
</ol>
</div>
</section>
""" % (D.RETRIEVED, src_count(), len(EVENTS),
       "".join('<tr><td>%s</td><td>%s</td><td class="nowrap">%s</td><td class="num">%s</td>'
               '<td class="num">%s</td><td class="num">%s</td><td>%s</td><td class="src">%s</td></tr>' % (
                   esc(e["name"]), esc(e["venue"]),
                   esc(pretty_date(e["date"]) if re.match(r"^\d{4}", str(e["date"])) else e["date"]),
                   money(e["gtd"]), money(e.get("buy_in")),
                   ("%.1f×" % e["ratio"]) if e.get("ratio") else "—",
                   esc(e["entry_class"]),
                   '<a href="%s" target="_blank" rel="noopener">official</a>' % esc(e["sources"][0]))
               for e in best_pool),
       "".join('<tr><td>%s</td><td>%s</td><td class="nowrap">%s</td><td class="num">%s</td>'
               '<td class="num">%s</td><td class="num">%s</td><td>%s</td></tr>' % (
                   esc(e["name"]), esc(e["venue"]),
                   esc(pretty_date(e["date"]) if re.match(r"^\d{4}", str(e["date"])) else e["date"]),
                   money(e["gtd"]), money(e.get("buy_in")), "%.1f×" % e["ratio"],
                   esc(e["entry_class"]))
               for e in best_ratio))
    h = h.replace("__VEV__", str(len([x for x in EVENTS if x["venue"] == "The Venetian"])))
    h += foot()
    write("summary.html", h)


# ---------------------------------------------------------- page: questions ---
def page_questions():
    rows = "".join(
        '<tr id="%s"><td><b>%s</b></td><td class="mini">%s</td><td class="mini">%s</td>'
        '<td class="mini">%s</td><td>%s</td></tr>' % (
            q["id"], esc(q["q"]), esc(q["known"]), esc(q["missing"]), esc(q["how"]),
            badge(q["blocks"], "warn" if "Nothing" not in q["blocks"] else "block"))
        for q in D.QUESTIONS)
    h = head("Questions", "What must be answered before a decision is reasonable.", "questions.html")
    h += """
<section class="hero small"><div class="eyebrow">DECISION GATE</div>
<h1>Questions that block a decision</h1>
<p class="lede">Each row is a question, what we already know with a source, what we do not know, how to
close the gap, and what it blocks. Nothing should be booked while a high-impact row is open.</p></section>
<section class="block"><div class="tw"><table class="t"><thead><tr><th>Question</th>
<th>Known now (sourced)</th><th>Missing</th><th>How to close it</th><th>Blocks</th></tr></thead>
<tbody>%s</tbody></table></div></section>

<section class="block">
<h2>How to discover the missing information</h2>
<div class="two">
<div><h3>Ask a person</h3><ul class="tick">
<li><b>Venetian poker room</b>, 702.414.7657 or lv_cas_poker@venetianlasvegas.com — written re-entry, rebuy and add-on rules for one-day DSE events; typical field size; typical finish time.</li>
<li><b>Venetian reservations</b>, 866.255.8936, code EPOKR25 — dated poker-rate quote, prevailing-rate quote for the same nights, and the cancellation deadline in writing.</li>
<li><b>Wynn poker room</b>, 702.770.7654 — whether daily events run during the WPT series.</li>
<li><b>Horseshoe poker room</b> — the six daily tournament times, buy-ins and guarantees.</li>
</ul></div>
<div><h3>Measure on foot</h3><ul class="tick">
<li>Palazzo self-parking elevator to the level-2 poker room.</li>
<li>Venetian lobby to the Palazzo poker room.</li>
<li>Venetian property to Wynn poker room (Encore).</li>
<li>Record the time of day and whether you walked through the casino or outdoors; that is the only way a 30-minute rule becomes checkable.</li>
</ul></div>
</div>
</section>
""" % ("".join(rows))
    h += foot()
    write("questions.html", h)


# -------------------------------------------------------- page: suggestions ---
def page_suggestions():
    rows = "".join(
        '<tr id="%s"><td><b>%s</b></td><td class="mini">%s</td><td>%s</td><td>%s</td>'
        '<td class="mini">%s</td><td>%s</td></tr>' % (
            s["id"], esc(s["title"]), esc(s["why"]), badge(s["effort"], "block"),
            badge(s["impact"], "warn"), esc(s["decision"]),
            badge(s["status"], "ok" if s["status"].startswith("Implemented") else "rev"))
        for s in D.SUGGESTIONS)
    h = head("Suggestions", "Review options and choose a path before anything changes.", "suggestions.html")
    h += """
<section class="hero small"><div class="eyebrow">REVIEW BEFORE IMPLEMENTING</div>
<h1>Suggestions, with a decision attached</h1>
<p class="lede">This page exists so you can choose a direction instead of receiving changes you did not
ask for. Each row states the problem, the effort, the impact and the exact decision it needs from you.
Rows already marked <em>Implemented in this build</em> are ones the build did because they were
unambiguous requests; everything else waits.</p></section>
<section class="block"><div class="tw"><table class="t"><thead><tr><th>Suggestion</th>
<th>Why it matters</th><th>Effort</th><th>Impact</th><th>Decision needed</th><th>Status</th></tr></thead>
<tbody>%s</tbody></table></div></section>

<section class="block">
<h2>What was implemented, and how it maps to the request</h2>
<div class="tw"><table class="t"><thead><tr><th>Requested capability</th><th>Where it lives</th><th>Status</th></tr></thead><tbody>
<tr><td>Trip cost calculator: entries × buy-ins + nights × true hotel cost</td><td><a href="index.html#calc">Dashboard</a>, <a href="hotels.html">Hotels</a></td><td>%s</td></tr>
<tr><td>Date filter showing only events on chosen days</td><td><a href="tournaments.html">All events</a></td><td>%s</td></tr>
<tr><td>Search box across all tables</td><td>Every table page</td><td>%s</td></tr>
<tr><td>Single-entry / freezeout confirmed toggle</td><td><a href="tournaments.html">All events</a></td><td>%s (0 rows, by evidence)</td></tr>
<tr><td>Structured rule fields: single-entry, re-entry, add-on, fee, each with source and retrieval date</td><td><a href="single-entry.html">Entry rules</a></td><td>%s</td></tr>
<tr><td>Schedule overlap check with primary + conditional fallback</td><td><a href="schedule.html">Day plan</a></td><td>%s</td></tr>
<tr><td>Last-checked date on each row</td><td>Every table</td><td>%s</td></tr>
<tr><td>Rates as a dated log, not one value</td><td><a href="hotels.html">Hotels</a></td><td>%s</td></tr>
<tr><td>One page per venue with its events and hotels</td><td><a href="venues.html">Venues</a></td><td>%s</td></tr>
<tr><td>Scheduled re-check of each official URL with change marking</td><td><a href="sources.html">Sources &amp; monitoring</a></td><td>%s</td></tr>
<tr><td>Walking-time verification with a 30-minute filter</td><td><a href="hotels.html">Hotels</a></td><td>%s — no official figure exists</td></tr>
<tr><td>Live hotel rate lookup</td><td><a href="hotels.html">Hotels</a></td><td>%s — needs a dated quote from you</td></tr>
<tr><td>Live-data scraper of each room's daily schedule</td><td><a href="sources.html">Sources &amp; monitoring</a></td><td>%s — change detection runs on a schedule; a full per-room scraper needs sites that expose machines-readable schedules</td></tr>
</tbody></table></div>
</section>
""" % ("".join(rows), *[badge("Done", "ok")] * 10 + [badge("Blocked", "block")] * 3)
    h += foot()
    write("suggestions.html", h)


# ------------------------------------------------------------ page: flagged ---
def page_flagged():
    rows = []
    for f in D.FLAGS:
        rows.append(
            '<tr id="%s"><td><b>%s</b></td><td>%s</td><td>%s</td><td class="mini">%s</td>'
            '<td class="src">%s</td></tr>' % (
                f["id"], esc(f["id"]), badge(f["sev"],
                                             {"high": "rev", "medium": "warn", "low": "block"}[f["sev"]]),
                esc(f["title"]), esc(f["detail"]),
                " ".join(src_link(k, "official") for k in f["srcs"])))
    h = head("Flagged for review", "Unverified values and irregularities, with sources.", "flagged.html")
    h += """
<section class="hero small"><div class="eyebrow">FLAGGED FOR REVIEW</div>
<h1>What is unverified, and why</h1>
<p class="lede">%d items. Every one has a source link. A flag does not mean the value is wrong —
it means no official source retrieved in this build establishes it. These do not block publishing the
site; they block relying on the corresponding cells.</p></section>
<section class="block"><div class="tw"><table class="t"><thead><tr><th>ID</th><th>Severity</th>
<th>Issue</th><th>Detail</th><th>Sources</th></tr></thead><tbody>%s</tbody></table></div></section>
<section class="block">
<h2>Blank cells you will see, and what each one means</h2>
<div class="tw"><table class="t"><thead><tr><th>Blank cell</th><th>Meaning</th><th>Flag</th></tr></thead><tbody>
<tr><td>Walking time (every hotel)</td><td>No official walking time exists on any property page read.</td><td>F-03</td></tr>
<tr><td>Dated room rate / checkout total</td><td>Needs a live dated quote; not a published number.</td><td>F-04</td></tr>
<tr><td>Room tax %% (Wynn, Bellagio, MGM Grand, Caesars)</td><td>Terms say "current tax rates" without printing a percentage.</td><td>F-05</td></tr>
<tr><td>Resort fee (Caesars Palace, Horseshoe)</td><td>No official fee page could be retrieved.</td><td>F-12</td></tr>
<tr><td>Re-entry / rebuy / add-on (Venetian one-day)</td><td>The structure sheet does not state a rule.</td><td>F-02</td></tr>
<tr><td>Guarantee (some Venetian events)</td><td>The official schedule prints no guarantee for that row.</td><td>—</td></tr>
<tr><td>Entry limit (Wynn $800/$1M, Prime, Super Gold Million)</td><td>Event-specific terms were not re-read in this build.</td><td>F-13</td></tr>
</tbody></table></div>
</section>
""" % (len(D.FLAGS), "".join(rows))
    h += foot()
    write("flagged.html", h)


# ------------------------------------------------------------ page: sources ---
def page_sources():
    rows = "".join(
        '<tr><td><code>%s</code></td><td>%s</td><td class="src"><a href="%s" target="_blank" rel="noopener">%s</a></td>'
        '<td class="nowrap">%s</td><td class="src"><a href="%s" target="_blank" rel="noopener">manual check</a></td></tr>' % (
            esc(k), esc(label), esc(url), esc(url), D.RETRIEVED, esc(url))
        for k, (label, url) in sorted(D.SOURCES.items()))
    sheet_rows = "".join(
        '<tr><td class="num">%d</td><td class="src"><a href="%s" target="_blank" rel="noopener">structure PDF %d</a></td>'
        '<td class="nowrap">%s</td></tr>' % (n, esc(D.vsheet(n)), n, D.RETRIEVED)
        for n in range(1, 38))
    h = head("Sources & monitoring", "Official source register, retrieval dates, and change monitoring.",
             "sources.html")
    h += """
<section class="hero small"><div class="eyebrow">PROVENANCE</div>
<h1>Source register</h1>
<p class="lede">%d sources, all retrieved on %s. Each has a link you can open to check the value
yourself. The "manual check" column is the same URL — nothing here is a cached copy.</p></section>

<section class="block"><div class="tw"><table class="t"><thead><tr><th>Key</th><th>Source</th>
<th>URL</th><th>Retrieved</th><th>Verify</th></tr></thead><tbody>%s</tbody></table></div></section>

<section class="block">
<h2>Venetian structure sheets</h2>
<p>All 37 were read. Sheet numbers match the numbers printed in the "Structures" column of the
official event page.</p>
<div class="tw"><table class="t"><thead><tr><th>Sheet</th><th>Official PDF</th><th>Retrieved</th></tr></thead>
<tbody>%s</tbody></table></div>
</section>

<section class="block">
<h2>Automated change monitoring</h2>
%s
<p>A GitHub Actions workflow runs <code>scripts/recheck_sources.py</code> on a schedule, fetches every
official URL above, hashes the normalised text of each page, and appends any change to
<code>data/site/checks.json</code>. The workflow fails nothing on a content change: a change is
recorded, not guessed at.</p>
<div class="tw"><table class="t"><thead><tr><th>What is monitored</th><th>How a change is surfaced</th></tr></thead><tbody>
<tr><td>Every URL in the register above</td><td>Text hash comparison per run; changed rows are listed in <code>data/site/checks.json</code> with the old and new hash and a timestamp.</td></tr>
<tr><td>HTTP failures (404 / 500 / timeouts)</td><td>Recorded as a fetch error, which is itself a flag: a moved page can invalidate a cited value.</td></tr>
<tr><td>Schedule cadence</td><td>Daily at 06:00 UTC, plus manual dispatch from the Actions tab.</td></tr>
</tbody></table></div>
<p class="note">Why monitoring rather than a scraper per room: the Venetian, Wynn and Caesars PDFs are
directly fetchable and are what this dataset is built on; Horseshoe publishes no retrievable
tournament document at all, so no scraper can invent one.</p>
</section>
""" % (src_count(), D.RETRIEVED, rows, sheet_rows, monitoring_block())
    h += foot()
    write("sources.html", h)


def monitoring_block():
    path = os.path.join(ROOT, "data", "site", "checks.json")
    if not os.path.exists(path):
        return ('<p class="note">No monitoring run recorded yet. The workflow writes its first '
                'result to <code>data/site/checks.json</code> on the next scheduled run.</p>')
    import json as _json
    d = _json.load(open(path, encoding="utf-8"))
    if not d.get("runs"):
        return ('<p class="note"><b>Monitoring baseline: nothing checked yet.</b> The scheduled '
                'workflow (<code>.github/workflows/recheck.yml</code>, daily at 06:00 UTC) performs '
                'the first live fetch of all %d URLs and writes the result to '
                '<code>data/site/checks.json</code>. The sandbox that generated this page has no '
                'outbound network access to those hosts, so inventing a status here would be a '
                'fabrication. Every URL below is listed with a direct link so you can check it '
                'yourself right now.</p>'
                '<div class="tw"><table class="t"><thead><tr><th>Source</th><th>URL</th>'
                '<th>Monitoring status</th></tr></thead><tbody>%s</tbody></table></div>'
                % (d.get("monitored", 0), "".join(
                    '<tr><td>%s</td><td class="src"><a href="%s" target="_blank" rel="noopener">%s</a></td>'
                    '<td>%s</td></tr>' % (esc(k), esc(D.SOURCES[k][1]), esc(D.SOURCES[k][1]),
                                          badge("awaiting first run", "nav"))
                    for k in sorted(D.SOURCES))))
    run = d["runs"][0]
    changed = [r for r in run["results"] if r.get("change") == "CHANGED"]
    errs = [r for r in run["results"] if r.get("change") == "fetch error"]
    out = ['<p class="hint">Last run <b>%s</b> · %d URLs monitored · %d changed · %d fetch errors.</p>'
           % (esc(run["checked"]), len(run["results"]), len(changed), len(errs))]
    out.append('<div class="tw"><table class="t"><thead><tr><th>Source</th><th>Status</th>'
               '<th>Change</th><th>Hash</th><th>Official URL</th></tr></thead><tbody>')
    for r in run["results"]:
        cls = {"CHANGED": "warn", "unchanged": "ok", "first check": "nav",
               "fetch error": "rev"}.get(r.get("change"), "block")
        out.append('<tr><td>%s</td><td class="num">%s</td><td>%s</td><td class="mini">%s</td>'
                   '<td class="src"><a href="%s" target="_blank" rel="noopener">check</a></td></tr>'
                   % (esc(r["key"]), esc(r.get("status")), badge(r.get("change") or "?", cls),
                      esc(r.get("hash") or "—"), esc(r["url"])))
    out.append('</tbody></table></div>')
    return "".join(out)


# ------------------------------------------------------- page: repo review ----
def page_repo_review():
    h = head("Repo review", "Line-by-line review of what the repository contains.", "repo-review.html")
    h += """
<section class="hero small"><div class="eyebrow">REPO REVIEW</div>
<h1>What the repository actually contains</h1>
<p class="lede">Earlier sessions built four overlapping dashboards and reached different conclusions
about the same pages. This build adds one consolidated site and records the irregularities rather than
silently overwriting prior work.</p></section>

<section class="block">
<h2>Inventory</h2>
<div class="tw"><table class="t"><thead><tr><th>Path</th><th>What it is</th><th>Status after this build</th></tr></thead><tbody>
<tr><td><code>index.html</code>, <code>tournaments.html</code>, <code>hotels.html</code>, <code>venues.html</code>, <code>schedule.html</code>, <code>single-entry.html</code>, <code>summary.html</code>, <code>questions.html</code>, <code>suggestions.html</code>, <code>flagged.html</code>, <code>sources.html</code>, <code>repo-review.html</code>, <code>venues/*.html</code></td><td>This build's consolidated dashboard</td><td><b>Live</b> at the repository root</td></tr>
<tr><td><code>data/site/*.json</code></td><td>Canonical verified dataset, exported from <code>scripts/dataset.py</code></td><td>Live</td></tr>
<tr><td><code>docs/</code></td><td>Earlier session's dashboard subsite (12 pages)</td><td>Retained, unlinked from the new nav, superseded</td></tr>
<tr><td><code>verified/</code></td><td>Earlier session's dashboard subsite (11 pages)</td><td>Retained, superseded</td></tr>
<tr><td><code>pages/</code></td><td>Earlier session's category pages (15 pages)</td><td>Retained, superseded</td></tr>
<tr><td><code>planning.html</code>, <code>flagged.html</code> (old), <code>style.css</code>, <code>styles.css</code>, <code>app.js</code></td><td>Earlier root-site assets</td><td><code>flagged.html</code> replaced by this build's version; the legacy stylesheets are left in place</td></tr>
<tr><td><code>data/*.json</code>, <code>data/*.csv</code></td><td>Earlier sessions' datasets</td><td>Left untouched; superseded by <code>data/site/</code></td></tr>
<tr><td><code>research/</code>, <code>reports/</code></td><td>Earlier verification logs</td><td>Retained as evidence</td></tr>
</tbody></table></div>
</section>

<section class="block">
<h2>Irregularities found while reviewing the repository</h2>
<div class="tw"><table class="t"><thead><tr><th>#</th><th>Finding</th><th>Handling</th></tr></thead><tbody>
<tr><td>1</td><td>Three complete dashboards published from three different sessions, with different conclusions on the same evidence.</td><td>Not deleted. Consolidation is offered as <a href="suggestions.html#S-09">S-09</a> for your decision.</td></tr>
<tr><td>2</td><td>The old root <code>index.html</code> marked every event "Unverified" for entry rules while a later session had already read several structure sheets.</td><td>Superseded: all 37 sheets are now read and quoted.</td></tr>
<tr><td>3</td><td><code>COORDINATION.md</code> records that "chip counts and registration close times are not on the official schedule page".</td><td>Correct for the HTML page, wrong for the schedule <b>PDF</b>, which prints both. Values are now sourced to the PDF. Logged as <a href="flagged.html#F-14">F-14</a>.</td></tr>
<tr><td>4</td><td>An earlier dataset assigned <code>reg_closes</code>, <code>chips</code> and <code>level</code> values that its own session said it could not reproduce.</td><td>Independently re-derived here from the official schedule PDF and confirmed per event against each structure sheet.</td></tr>
<tr><td>5</td><td>Two stylesheets (<code>style.css</code>, <code>styles.css</code>) and two script files exist for different generations of the same site.</td><td>New build uses <code>assets/site.css</code> and <code>assets/site.js</code>; legacy files untouched.</td></tr>
<tr><td>6</td><td>Branch naming in earlier sessions deviated from the documented <code>session-&lt;id&gt;/&lt;task&gt;</code> convention.</td><td>Recorded; this session uses its fixed branch <code>arena/7a4b09e2-poker2</code> as required.</td></tr>
<tr><td>7</td><td>The old <code>flagged.html</code> and the <code>docs/flag</code> page listed non-overlapping flag sets (F-01…F-22 vs a different list).</td><td>Replaced by a single F-01…%d list with source links per flag.</td></tr>
</tbody></table></div>
</section>

<section class="block">
<h2>Verification performed by this build</h2>
<ul class="tick">
<li>Every event value traced to the official schedule PDF; fee split cross-checked against the individual structure sheet for that event number.</li>
<li>Structure-sheet ownership verified: each sheet lists its own event numbers, and those numbers were matched to schedule rows rather than assumed from the URL.</li>
<li>Build fails if any published row references a non-official host (<code>scripts/build.py</code>).</li>
<li>Link checker (<code>scripts/check_links.py</code>) run over every generated page; no broken internal link and no non-official external host.</li>
<li>No value inferred: where a source was silent the cell is empty and the item appears in <a href="flagged.html">Flagged for review</a>.</li>
</ul>
</section>

<section class="block">
<h2>Known-good vs known-missing, at a glance</h2>
<div class="two">
<div><h3>Good</h3><ul class="tick">
<li>Event identity, dates, start times, registration close, buy-in, guarantee, stack, level length</li>
<li>Fee allocation per buy-in</li>
<li>Competing venues' written entry rules</li>
<li>Resort fees, one room-tax rate, parking</li>
</ul></div>
<div><h3>Missing</h3><ul class="cross">
<li>One-entry confirmation</li>
<li>Dated room totals</li>
<li>Walking times</li>
<li>Expected finish times and field sizes</li>
<li>Caesars property fees</li>
</ul></div>
</div>
</section>
""" % len(D.FLAGS)
    h += foot()
    write("repo-review.html", h)


# ------------------------------------------------------------- data export ---
def export_data():
    os.makedirs(OUT_DATA, exist_ok=True)
    payload = dict(
        retrieved=D.RETRIEVED,
        sources={k: dict(label=v[0], url=v[1]) for k, v in D.SOURCES.items()},
        events=EVENTS,
        hotels=D.HOTELS,
        flags=D.FLAGS,
        questions=D.QUESTIONS,
        suggestions=D.SUGGESTIONS,
        restarts=[dict(date=a, time=b, ev=c, label=d) for a, b, c, d in D.VENETIAN_RESTARTS],
        counts=dict(events=len(EVENTS), sources=len(D.SOURCES),
                    sheets=37, single_confirmed=sum(1 for e in EVENTS if e["single_confirmed"])),
    )
    with open(os.path.join(OUT_DATA, "dataset.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, sort_keys=True, default=str)
    with open(os.path.join(OUT_DATA, "events.json"), "w", encoding="utf-8") as f:
        json.dump(EVENTS, f, indent=1, sort_keys=True, default=str)
    with open(os.path.join(OUT_DATA, "hotels.json"), "w", encoding="utf-8") as f:
        json.dump(D.HOTELS, f, indent=1, sort_keys=True, default=str)
    with open(os.path.join(OUT_DATA, "flags.json"), "w", encoding="utf-8") as f:
        json.dump(D.FLAGS, f, indent=1, sort_keys=True, default=str)


def main():
    page_index()
    page_tournaments()
    page_schedule()
    page_hotels()
    page_single_entry()
    page_venues()
    page_summary()
    page_questions()
    page_suggestions()
    page_flagged()
    page_sources()
    page_repo_review()
    export_data()
    print("built %d events, %d sources, %d hotels, %d flags"
          % (len(EVENTS), len(D.SOURCES), len(D.HOTELS), len(D.FLAGS)))


if __name__ == "__main__":
    main()
