#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the /audit/ site from data/audit/*.json.

Run:  python3 scripts/audit_build.py
Fails if any published event/hotel row lacks an https source link, or if a page
links to a file that does not exist.
"""
import json, os, re, html, datetime, sys, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "audit")
AS_OF = "2026-11-17"
SCHEDULE_URL = ("https://www.venetianlasvegas.com/resort/casino/poker/"
                "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
sys.path.insert(0, os.path.join(ROOT, "data", "audit"))
from sheets import SHEETS, UNREAD_SHEETS, sheet_url

NAV = [
    ("index.html", "Dashboard"),
    ("events.html", "Tournaments"),
    ("schedule.html", "Day plan"),
    ("hotels.html", "Hotels"),
    ("cost.html", "Trip cost"),
    ("rates.html", "Rate log"),
    ("venues.html", "Venues"),
    ("walking.html", "Walking"),
    ("rules.html", "Entry rules"),
    ("summary.html", "Summary"),
    ("questions.html", "Questions"),
    ("suggestions.html", "Suggestions"),
    ("flagged.html", "Flagged"),
    ("sources.html", "Sources"),
    ("monitor.html", "Monitor"),
]


def load(name):
    with open(os.path.join(ROOT, "data", "audit", name), encoding="utf-8") as fh:
        return json.load(fh)


E = load("events.json")
H = load("hotels.json")
W = load("walking.json")
R = load("rates.json")
F = load("flags.json")
Q = load("questions.json")
S = load("suggestions.json")
EV, HO, WK = E["events"], H["hotels"], W["hotels"]
FL, QT, SG = F["flags"], Q["questions"], S["suggestions"]
RATES = R["rates"]

walk_by = {w["hotel_id"]: w for w in WK}
unit = {h["id"]: h for h in HO}


# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(str("" if s is None else s))


def money(v, dash="&mdash;"):
    if v is None or v == "":
        return dash
    f = float(v)
    return "$%s" % format(f, ",.0f" if f == int(f) else ",.2f")


def num(v, dash="&mdash;"):
    return dash if v in (None, "") else esc(v)


def chips(v):
    if v in (None, ""):
        return "&mdash;"
    return "{:,}".format(int(v))


def clock(hhmm):
    """2400 clock as printed on the sheet -> the same time in the sheet's 12-hour style."""
    if not hhmm or ":" not in str(hhmm):
        return hhmm or "&mdash;"
    h, m = str(hhmm).split(":")[:2]
    h = int(h)
    ap = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return "%d:%s %s" % (h12, m, ap)


def pill(text, kind=""):
    return '<span class="p %s">%s</span>' % (kind, esc(text))


def chip_rule(v):
    if v == "explicit_no":
        return pill("explicit: no 2nd entry", "bad")
    if v == "explicit_yes":
        return pill("explicit: re-entry allowed", "warn")
    if v == "not_stated":
        return pill("sheet silent", "warn")
    return pill("not read", "muted")


def chip_basis(b):
    if b == "prize pool":
        return pill("pure prize pool", "ok")
    if b and "bounties" in b:
        return pill("includes bounties", "warn")
    if b == "no guarantee printed":
        return pill("no GTD printed", "muted")
    return pill("unknown", "muted")


def link(url, label=None):
    if not url:
        return "&mdash;"
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(url), esc(label or host))


FILTER_JS = """<script>
document.querySelectorAll('.bar').forEach(function(bar){
  var table = bar.parentElement.querySelector('table.data');
  if(!table) return;
  var q = bar.querySelector('[data-q]'),
      d = bar.querySelector('[data-date]'),
      c = bar.querySelector('[data-count]'),
      rows = Array.prototype.slice.call(table.tBodies[0].rows);
  function apply(){
    var text = (q && q.value || '').toLowerCase(),
        date = (d && d.value) || '',
        n = 0;
    rows.forEach(function(r){
      var ok = true;
      if(text && r.textContent.toLowerCase().indexOf(text) === -1) ok = false;
      if(date && (r.getAttribute('data-date') || '') !== date) ok = false;
      r.style.display = ok ? '' : 'none';
      if(ok) n++;
    });
    if(c) c.textContent = n + ' of ' + rows.length + ' rows';
  }
  if(q) q.addEventListener('input', apply);
  if(d) d.addEventListener('change', apply);
  apply();
});
</script>"""


def page(title, active, body, desc="", extra_head="", extra_js=""):
    nav = "\n".join('<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == active else "", l)
                    for h, l in NAV)
    out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} &middot; Vegas poker audit</title>
<meta name="description" content="{esc(desc or title)}">
<link rel="stylesheet" href="assets/audit.css">
{extra_head}
</head>
<body>
<header class="top">
  <div class="wrap">
    <div class="brand"><a href="index.html">Vegas poker audit</a>
      <span class="date">official sources only &middot; every value dated {AS_OF}</span></div>
    <nav>{nav}</nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="wrap foot">
  <p>Built from official venue pages and structure-sheet PDFs, a county tax document and a
  published walking-routing service. Blank means not confirmed, never estimated.
  Data: {AS_OF}. <a href="../index.html">Root dashboard</a> &middot;
  <a href="../plan/index.html">/plan/</a> &middot;
  <a href="https://github.com/karagemop466-tech/Poker2">Repository</a> &middot;
  <a href="https://github.com/karagemop466-tech/Poker2/blob/main/COORDINATION.md">COORDINATION.md</a></p>
  <p class="tiny">Guarantee &divide; entry fee is a descriptive ratio of two published numbers.
  It is not a forecast, an expected value, or advice. Re-check every official page before paying.</p>
</footer>
{FILTER_JS}
{extra_js}
</body>
</html>
"""
    return out.replace("{FILTER_JS}", FILTER_JS)


def table(headers, rows, tid=None, cls="data"):
    idattr = ' id="%s"' % tid if tid else ""
    th = "".join("<th>%s</th>" % h for h in headers)
    tr = "\n".join("<tr>%s</tr>" % "".join("<td>%s</td>" % c for c in r) for r in rows)
    return '<div class="tw"><table%s class="%s"><thead><tr>%s</tr></thead><tbody>\n%s\n</tbody></table></div>' % (
        idattr, cls, th, tr)


def toolbar(tid, dates=None, extra=""):
    out = '<div class="bar">'
    out += '<input type="search" data-q placeholder="Search this table&hellip;" aria-label="Search this table">'
    if dates:
        opts = "".join('<option value="%s">%s</option>' % (d, d) for d in dates)
        out += '<select data-date><option value="">All dates</option>%s</select>' % opts
    out += extra
    out += '<span class="count" data-count></span></div>'
    # bind by position: the script walks .bar -> next .tw table
    return out


SEARCH_JS = """<script>
document.querySelectorAll('.bar').forEach(function(bar){
  var tbl = bar.parentElement.querySelector('table.data');
  if(!tbl) return;
  var q = bar.querySelector('[data-q]'),
      d = bar.querySelector('[data-date]'),
      c = bar.querySelector('[data-count]'),
      rows = Array.prototype.slice.call(tbl.tBodies[0].rows);
  function apply(){
    var text = (q && q.value || '').toLowerCase(),
        date = (d && d.value) || '',
        n = 0;
    rows.forEach(function(r){
      var ok = true;
      if(text && r.textContent.toLowerCase().indexOf(text) === -1) ok = false;
      if(date && (r.getAttribute('data-date') || '') !== date) ok = false;
      r.style.display = ok ? '' : 'none';
      if(ok) n++;
    });
    if(c) c.textContent = n + ' of ' + rows.length + ' rows';
  }
  if(q) q.addEventListener('input', apply);
  if(d) d.addEventListener('change', apply);
  apply();
});
</script>"""


# ------------------------------------------------------------------ pages
def ev_rows(rows, show_sheet=True):
    out = []
    for e in rows:
        cells = [
            '<span class="nowrap">%s<small>%s</small></span>' % (e["date"], e["dow"]),
            e["start_text"],
            esc(e["event_no"]),
            esc(e["name"]),
            money(e["buy_in_nominal"]),
            money(e["fee"]),
            money(e["gtd"]),
            chip_basis(e["gtd_basis"]),
            chips(e["chips"]),
            num(e["level_min"]),
            clock(e["late_reg_time"]),
            chip_rule(e["single_entry"]),
            (money(e["gtd_ratio_descriptive"]) if e["gtd_ratio_descriptive"]
             else ('<span class="sm muted" title="the guarantee includes bounties, so it is '
                   'not comparable with a pure prize pool">n/a &mdash; bounty GTD</span>')
             if e["gtd"] else "&mdash;"),
            e["last_checked"],
            link(e["source_url"], "sheet %d" % e["sheet"]) if e["structure_read"]
            else link(e["source_url"], "schedule"),
        ]
        attrs = ' data-date="%s"' % e["date"]
        out.append((attrs, cells))
    return out


def render_ev_table(rows, tid="t-events"):
    """Each call must pass a unique tid: the filter script binds bar -> nearest .tw table."""
    assert tid, "a table needs an id"
    """The table wrapper carries data-date on each row so the date filter works."""
    heads = ["Date", "Start", "Ev#", "Name", "Buy-in", "Fee", "GTD", "GTD basis",
             "Chips", "Min/level", "Late reg closes", "Entry rule", "GTD &divide; fee",
             "Last checked", "Source"]
    body = []
    for attrs, cells in ev_rows(rows):
        body.append("<tr%s>%s</tr>" % (attrs, "".join("<td>%s</td>" % c for c in cells)))
    th = "".join("<th>%s</th>" % h for h in heads)
    return ('<div class="tw"><table id="%s" class="data"><thead><tr>%s</tr></thead>'
            '<tbody>\n%s\n</tbody></table></div>' % (tid, th, "\n".join(body)))


def sorted_events(rows):
    return sorted(rows, key=lambda e: (e["date"], e["start"], e["event_no"]))


def build_index():
    read = [e for e in EV if e["structure_read"]]
    singles_read = [e for e in read if e["category"] == "single"]
    rankable = [e for e in read if e["gtd_ratio_descriptive"] and e["gtd_basis"] == "prize pool"]
    dates = sorted({e["date"] for e in EV})
    span = "%s to %s" % (dates[0], dates[-1])

    cards = [
        ("94", "published schedule rows", "every &lt;tr&gt; on the official DSE IV page, transcribed in order"),
        ("%d" % len(read), "rows with structure data",
         "all %d structure-sheet PDFs read in full, 2026-11-17" % len(SHEETS)),
        *([("%d" % (len(EV) - len(read)), "rows structure not read",
            "date, time, event no, name and sheet link only")] if len(read) < len(EV) else []),
        ("0", "events confirmed single-entry",
         "no sheet prints an entry limit; see FD-03"),
        ("%d" % len(rankable), "rows with a usable GTD &divide; fee", "only where the guarantee is pure prize pool"),
        ("6 / 11", "hotels inside the 30-minute walk", "measured, third-party routing &mdash; see FD-08"),
        ("0", "dated room rates captured", "every booking engine is JavaScript-only &mdash; see FD-05"),
        ("%d" % len(FL), "items flagged for review", "every one names the document that shows it"),
    ]
    cardhtml = "".join(
        '<div class="card"><b>%s</b><span>%s</span><em>%s</em></div>' % (v, k, n) for v, k, n in cards)

    body = f"""
<section class="hero">
  <h1>Las Vegas Strip poker trip &mdash; verified-source audit</h1>
  <p class="lede">A trip planner built only from documents a venue or a county publishes. Every
  row links to the page or PDF it came from, carries the date it was checked, and leaves the cell
  blank when the document does not print the value. This build covers
  <b>The Venetian DeepStack Extravaganza IV</b>, {span} (94 published rows) and
  eleven Las Vegas hotels.</p>
  <p class="lede dim">Three things on this site are uncomfortable and are stated anyway: no event is
  confirmed single-entry, no dated hotel rate exists, and an 8&nbsp;AM start is not on any schedule.</p>
</section>

<section class="cards">{cardhtml}</section>

<section class="grid2">
  <div class="panel">
    <h2>Start here</h2>
    <ol class="tight">
      <li><a href="summary.html"><b>Summary</b></a> &mdash; the answer to each question you asked, and whether it is answered, partly answered or blocked.</li>
      <li><a href="events.html"><b>Tournaments</b></a> &mdash; all 94 rows, searchable and filterable by date, with the fee and structure only where the sheet was read.</li>
      <li><a href="schedule.html"><b>Day plan</b></a> &mdash; one primary event per day plus a conditional fallback, built from real start times and late-registration closes.</li>
      <li><a href="hotels.html"><b>Hotels</b></a> &mdash; fees, tax, parking and the measured walk, with the room rate explicitly missing.</li>
      <li><a href="cost.html"><b>Trip cost</b></a> &mdash; entries &times; buy-in computed exactly; nights &times; true cost shown as fees-only until a rate exists.</li>
    </ol>
  </div>
  <div class="panel">
    <h2>What is verified, and how</h2>
    {table(["Input", "How it was read", "Rows", "Date"], [
      ["Official DSE IV schedule page", "all four page chunks, one row per table row", "94", AS_OF],
      ["Official structure-sheet PDFs", "each PDF opened and read in full", "%d of %d" % (len(SHEETS), len(SHEETS) + len(UNREAD_SHEETS)), AS_OF],
      ["Venetian resort fee / hotel terms", "official property pages", "1 property", AS_OF],
      ["Bellagio, ARIA, MGM Grand, Wynn terms", "official property terms pages", "4 properties", AS_OF],
      ["Clark County transient lodging tax", "county licensing guide (PDF)", "13.38%", AS_OF],
      ["Walking times", "Google Maps walking directions, address to address", "11 pairs", AS_OF],
      ["Dated room rates", "not obtainable &mdash; JavaScript booking engines", "0", AS_OF],
    ])}
  </div>
</section>

<section>
  <h2>Every page</h2>
  <div class="navgrid">
    <a class="navcard" href="events.html"><b>Tournaments</b><span>94 rows, searchable by date and text</span></a>
    <a class="navcard" href="schedule.html"><b>Day plan</b><span>one primary a day plus a conditional fallback</span></a>
    <a class="navcard" href="hotels.html"><b>Hotels</b><span>fee, tax, parking and the measured walk</span></a>
    <a class="navcard" href="cost.html"><b>Trip cost</b><span>entries &times; buy-in + nights &times; true cost</span></a>
    <a class="navcard" href="rates.html"><b>Rate log</b><span>dated observations, including the failed ones</span></a>
    <a class="navcard" href="venues.html"><b>Venues</b><span>one block per property</span></a>
    <a class="navcard" href="walking.html"><b>Walking</b><span>the 30-minute rule, measured</span></a>
    <a class="navcard" href="rules.html"><b>Entry rules</b><span>three-state evidence, quoted</span></a>
    <a class="navcard" href="summary.html"><b>Summary</b><span>answers to each part of the brief</span></a>
    <a class="navcard" href="questions.html"><b>Questions</b><span>what must be answered first</span></a>
    <a class="navcard" href="suggestions.html"><b>Suggestions</b><span>options and the decision each needs</span></a>
    <a class="navcard" href="flagged.html"><b>Flagged</b><span>every irregularity, with evidence</span></a>
    <a class="navcard" href="sources.html"><b>Sources</b><span>every document read, and not read</span></a>
    <a class="navcard" href="monitor.html"><b>Monitor</b><span>per-URL status and content hashes</span></a>
  </div>
</section>

<section class="panel">
  <h2>Other pages in this repository</h2>
  <p class="sm">Earlier sessions built separate surfaces. They are kept so nothing breaks, but they
  use different datasets and can disagree with the numbers here &mdash; recorded as
  <a href="flagged.html#FD-15">FD-15</a>, with the choice of one surface as
  <a href="suggestions.html">SG-01</a>.</p>
  <ul class="tight sm">
    <li><a href="../index.html">repository home</a> &middot; <a href="../summary.html">summary</a>
        &middot; <a href="../tournaments.html">tournaments</a> &middot;
        <a href="../hotels.html">hotels</a> &middot; <a href="../planner.html">planner</a>
        &middot; <a href="../flagged.html">flagged</a></li>
    <li><a href="../plan/index.html">/plan/</a> &mdash; generated planner surface</li>
    <li><a href="../docs/index.html">/docs/</a>, <a href="../verified/index.html">/verified/</a>,
        <a href="../pages/summary.html">/pages/</a> &mdash; frozen earlier builds</li>
    <li><a href="https://github.com/karagemop466-tech/Poker2/blob/main/COORDINATION.md">COORDINATION.md</a>
        &mdash; the parallel-session task board</li>
  </ul>
</section>

<section class="panel">
  <h2>How to read the labels</h2>
  <dl class="keys">
    <dt>{pill("sheet silent", "warn")}</dt><dd>the structure sheet was read in full and prints no re-entry, rebuy, add-on or entry-limit clause. That is <b>silence</b>, not a published freezeout rule.</dd>
    <dt>{pill("explicit: no 2nd entry", "bad")}</dt><dd>the sheet prints a rule that stops a player entering twice. On every read sheet this is the flight rule &ldquo;any player who bags chips for Day 2 may not play a subsequent flight&rdquo;.</dd>
    <dt>{pill("explicit: re-entry allowed", "warn")}</dt><dd>the sheet prints a mechanism for a second entry. Those rows are kept out of the one-entry section.</dd>
    <dt>{pill("includes bounties", "warn")}</dt><dd>the guarantee is defined on the sheet as prize pool <i>plus total bounties</i>, so its ratio is not comparable with a pure prize-pool guarantee.</dd>
    <dt>{pill("not read", "muted")}</dt><dd>the sheet is linked from the official page but was not opened in this pass. Fee, stack, level time and late-registration close are blank.</dd>
  </dl>
</section>
"""
    return page("Dashboard", "index.html", body,
                "Verified-source audit of Las Vegas Strip poker tournaments and hotels.")


def build_events():
    dates = sorted({e["date"] for e in EV})
    singles = [e for e in EV if e["category"] == "single"]
    singles_read = [e for e in singles if e["structure_read"]]

    agg = ""
    sections = [
        ("s-read", 'One-day events whose structure sheet was read', singles_read),
        ("s-flights", 'Multi-flight, satellite and team rows',
         [e for e in EV if e["category"] in ("multi_flight", "satellite", "team")]),
        ("s-unread", 'One-day events whose structure sheet was not read',
         [e for e in singles if not e["structure_read"]]),
    ]
    for tid, label, rows in sections:
        agg += ('<section class="panel"><h2>%s &mdash; %d rows</h2>%s%s</section>'
                % (label, len(rows), toolbar(tid, dates), render_ev_table(sorted_events(rows), tid)))

    body = f"""
<section class="hero">
  <h1>Tournaments</h1>
  <p class="lede">Every row published on the official DeepStack Extravaganza IV schedule page,
  in page order, 2026-11-16 to 2026-12-23. A row shows a fee, a starting stack, a level time, a
  late-registration close or a guarantee <b>only</b> when the structure sheet it links to was opened
  and read. Otherwise those cells are blank and the row says why.</p>
  <p class="note">No row on this page is labelled single-entry. Twelve sheets were read in full and
  none prints an entry limit; the six that print any entry rule print a flight restriction.
  See flag <a href="flagged.html#FD-03">FD-03</a>.</p>
  <p class="note">Guarantee &divide; fee is shown only where the guarantee is pure prize pool. Rows
  whose guarantee the sheet defines as &ldquo;prize pool + total bounties&rdquo; are labelled and are
  kept out of the comparison. See <a href="flagged.html#FD-07">FD-07</a>.</p>
</section>
{agg}
"""
    return page("Tournaments", "events.html", body, "All 94 published tournament rows with source links.")


def build_schedule():
    dates = sorted({e["date"] for e in EV})
    plan = []
    def enterable(e):
        """A row a player can still buy into today. Day 2/3 restarts and final tables
        are continuations of an event already in progress, not new entries."""
        n = e["name"].lower()
        return not ("day 2" in n or "day 3" in n or "restart" in n or "final table" in n)

    for d in dates:
        day = [e for e in EV if e["date"] == d]
        cand = sorted([e for e in day if enterable(e)], key=lambda e: e["start"])
        singles = [e for e in cand if e["category"] == "single"]
        primary = (singles or cand or [None])[0]
        if not primary:
            continue
        second = next((e for e in cand if e is not primary and e["start"] >= primary["start"]), None)
        # overlap test: can the player enter the second event after the first?
        verdict, reason = "", ""
        if not second:
            verdict, reason = ("single option", "only one row on this date")
        else:
            p_close = primary["late_reg_time"]
            s_start = second["start"]
            s_close = second["late_reg_time"]
            if s_start == primary["start"]:
                verdict, reason = ("clash", "same start time &mdash; cannot play both")
            elif p_close and s_close:
                verdict, reason = ("conditional",
                    "enter the %s row only if you are out of the %s row before %s, when the second "
                    "one's late registration closes"
                    % (second["start_text"], primary["start_text"], clock(s_close)))
            elif s_close:
                verdict, reason = ("conditional",
                    "second event's late registration closes at %s; the first event's close is not published for this row"
                    % (s_close[0:2] + ":" + s_close[2:]))
            else:
                verdict, reason = ("unverified",
                    "late-registration closes are not published for these rows, so a sequence cannot be confirmed")
        plan.append((d, primary, second, verdict, reason))

    rows = []
    for d, p, s, v, why in plan:
        kind = {"clash": "bad", "conditional": "warn", "single option": "muted",
                "unverified": "muted"}[v]
        rows.append([
            '<span class="nowrap">%s<small>%s</small></span>' % (d, p["dow"]),
            "%s &middot; %s" % (esc(p["start_text"]), esc(p["name"])),
            money(p["buy_in_nominal"]),
            clock(p["late_reg_time"]),
            ("%s &middot; %s" % (esc(s["start_text"]), esc(s["name"]))) if s else "&mdash;",
            clock(s.get("late_reg_time")) if s else "&mdash;",
            pill(v, kind),
            why,
        ])

    body = f"""
<section class="hero">
  <h1>Day plan</h1>
  <p class="lede">One primary event per day, earliest start first, and a second event only where the
  player can realistically still enter it. The test is not the start time: it is the
  <b>late-registration close</b> of the second event versus when the first event can plausibly be
  left. A timetable that assumes a 5&nbsp;PM finish is wrong most days.</p>
  <p class="note"><b>There is no 8 AM event.</b> The earliest row on the whole series is 09:10 (a
  turbo satellite) and the earliest one-day event is 10:10. A full day that begins at 8 AM cannot
  be built from this venue's published schedule &mdash; see <a href="flagged.html#FD-11">FD-11</a>.</p>
</section>
<div class="panel">
{toolbar("t-plan", dates)}
{table(["Date", "Primary event", "Buy-in", "Closes", "Fallback event", "Fallback closes", "Verdict", "Why"], rows, "t-plan")}
</div>
"""
    # late-reg close table straight from the sheet transcription    # late-reg close table straight from the sheet transcription
    sys.path.insert(0, os.path.join(ROOT, "data", "audit"))
    from sheets import SHEETS, sheet_url
    lr = [[str(s["sheet"]), ", ".join(n.lstrip("0") for n in s["event_numbers"]),
           s["start_time"], s["late_reg_text"], link(sheet_url(s["sheet"]), "PDF")]
          for s in SHEETS if s.get("late_reg_text")]
    body += ('<div class="panel"><h2>Every published late-registration close that was read</h2>'
             '<p class="sm">This is the value that decides whether a second event is possible on the '
             'same day.</p>%s</div>' % table(
                 ["Sheet", "Applies to events", "Start", "Late registration close", "Source"], lr))
    return page("Day plan", "schedule.html", body,
                "One primary event per day with a conditional fallback and overlap verdicts.")


def build_hotels():
    rows = []
    for h in HO:
        inwalk = h["walk_within_30"]
        rows.append([
            '<a href="#%s">%s</a>' % (h["id"], esc(h["name"])),
            esc(h["address"]),
            money(h["resort_fee"]) if h["fee_verified"] else pill("not published", "bad"),
            "%s (+ tax)" % money(h["occupancy_extra"]) if h["occupancy_extra"] is not None else "&mdash;",
            "13.38%",
            money(h["parking"]) if h["parking"] is not None else "&mdash;",
            "%s min" % h["walk_minutes"],
            pill("within 30 min" if inwalk else "fails 30 min", "ok" if inwalk else "bad"),
            "&mdash;",
            link(h["fee_url"]) if h["fee_url"] else "&mdash;",
        ])
    detail = []
    for h in HO:
        w = next((x for x in WK if x["hotel_id"] == h["id"]), {})
        detail.append(f"""
<div class="panel" id="{h['id']}">
  <h3>{esc(h['name'])} <span class="sm">{esc(h['address'])}</span></h3>
  <table class="kv">
    <tr><th>Resort fee / night</th><td>{money(h['resort_fee']) if h['fee_verified'] else pill('not verified','bad')}
      <span class="ex">{esc(h['resort_fee_text'])}</span></td></tr>
    <tr><th>Room tax</th><td>13.38% <span class="ex">{esc(h['tax_text'])}</span></td></tr>
    <tr><th>Extra occupant</th><td>{('%s / night' % money(h['occupancy_extra'])) if h['occupancy_extra'] is not None else '&mdash;'}
      <span class="ex">{esc(h['occupancy_text'])}</span></td></tr>
    <tr><th>Parking</th><td>{money(h['parking']) if h['parking'] is not None else '&mdash;'}
      <span class="ex">{esc(h['parking_text'])}</span></td></tr>
    <tr><th>Cancellation</th><td>{esc(h['cancellation']) or '&mdash;'}</td></tr>
    <tr><th>Check in / out</th><td>{esc(h['checkin']) or '&mdash;'} / {esc(h['checkout']) or '&mdash;'}</td></tr>
    <tr><th>Walk to the Venetian poker room</th><td>{h['walk_minutes']} min
      ({esc(w.get('distance_text',''))}) {link(h['walk_source_url'], 'routing')}</td></tr>
    <tr><th>Dated room rate</th><td>{pill('not captured','bad')}
      <span class="ex">The official booking engine renders prices only inside JavaScript.</span></td></tr>
    <tr><th>Still missing</th><td><ul class="tight">{"".join("<li>%s</li>" % esc(m) for m in h['missing'])}</ul></td></tr>
    <tr><th>Book / verify</th><td>{link(h['booking_url'], 'official site')} &middot; {link(h['fee_url'], 'terms') if h['fee_url'] else '&mdash;'}</td></tr>
  </table>
  <p class="sm">{esc(h['notes'])}</p>
</div>""")

    body = f"""
<section class="hero">
  <h1>Hotels</h1>
  <p class="lede">Eleven properties. The fee, tax, occupancy and parking figures come from each
  property's own terms page where one could be read; four properties publish none that was
  reachable and are shown blank. The walking figure is a measured routing estimate, not a venue
  claim. <b>No dated room rate was captured for any property.</b></p>
  <p class="note">Six of eleven are inside the 30-minute walk to the Venetian poker room:
  Venetian, Palazzo, Wynn, Bellagio, Caesars Palace and Horseshoe. Cosmopolitan (33 min), Westgate
  (34), ARIA (42), MGM Grand (45) and South Point (about 3 h) are outside it.</p>
</section>
<div class="panel">
{toolbar("t-hotels")}
{table(["Hotel", "Address", "Resort fee", "Extra occupant", "Tax", "Parking", "Walk", "30-min rule", "Dated rate", "Fee source"], rows, "t-hotels")}
</div>
{''.join(detail)}
"""
    return page("Hotels", "hotels.html", body,
                "Resort fees, tax, parking and measured walking times for eleven Las Vegas hotels.")


def build_cost():
    body = f"""
<section class="hero">
  <h1>Trip cost</h1>
  <p class="lede">The formula is <b>entries &times; buy-in + nights &times; true hotel cost</b>.
  The first half is computed exactly from published numbers. The second half cannot be, because no
  dated room rate exists, so the calculator returns the part it can prove and names the part it
  cannot. Pick the entries on the left; the hotel line will say &ldquo;unknown&rdquo; rather than
  invent a number.</p>
</section>

<div class="grid2">
 <div class="panel" id="calc">
  <h2>Calculator</h2>
  <div class="f">
    <label>Entries (ctrl/cmd-click for more than one)<select id="c-ev" multiple size="8"></select></label>
    <label>Hotel<select id="c-hotel"></select></label>
    <label>Nights<input id="c-nights" type="number" min="0" max="30" value="4"></label>
    <label>Room rate / night<input id="c-rate" type="number" min="0" step="1" placeholder="blank = unknown"></label>
    <label>Nights parked<input id="c-park" type="number" min="0" max="30" value="0"></label>
  </div>
  <div id="c-out" class="out"></div>
 </div>
 <div class="panel">
  <h2>What each line is</h2>
  <table class="kv">
   <tr><th>entries &times; buy-in</th><td>A published buy-in from the official schedule page. Exact.</td></tr>
   <tr><th>fee withheld</th><td>Printed on the structure sheet as &ldquo;$X of the $Y Buy-In is withheld for house fees&rdquo;. It is already inside the buy-in and is never added on top.</td></tr>
   <tr><th>nights &times; resort fee</th><td>The property's own published nightly fee, where one was read.</td></tr>
   <tr><th>tax</th><td>13.38% Clark County transient lodging tax, applied to rate and fee. That the fee is taxed comes from the properties' wording (&ldquo;plus applicable tax&rdquo;); it is not a printed arithmetic. See <a href="questions.html#IQ-04">IQ-04</a>.</td></tr>
   <tr><th>parking</th><td>Venetian and Palazzo $20/day for registered guests; free self-parking is claimed for South Point by an earlier session and not re-read; nothing published for the rest.</td></tr>
   <tr><th>room rate</th><td><b>Missing.</b> No dated quote was obtainable. See <a href="flagged.html#FD-05">FD-05</a>.</td></tr>
  </table>
 </div>
</div>

<div class="panel">
  <h2>Worked example &mdash; the four cheapest verified one-day entries</h2>
  <p class="sm">Chosen only because their buy-in and fee are both published. This is arithmetic,
  not a recommendation.</p>
  {table(["Date", "Event", "Buy-in", "Fee withheld", "GTD", "GTD &divide; fee", "Source"], [
    ['<span class="nowrap">%s</span>' % e["date"], esc(e["name"]), money(e["buy_in_nominal"]),
     money(e["fee"]), money(e["gtd"]), money(e["gtd_ratio_descriptive"]),
     link(e["source_url"], "sheet %d" % e["sheet"])]
    for e in sorted([x for x in EV if x["structure_read"] and x["category"] == "single"],
                    key=lambda x: x["buy_in_nominal"] or 1e9)[:4]
  ])}
</div>
"""
    calc_js = """<script>
const EVENTS = __EVENTS_JSON__;
const HOTELS = __HOTELS_JSON__;
const TAX = 0.1338;
const sel = document.getElementById('c-ev'), hs = document.getElementById('c-hotel');
EVENTS.forEach(function(e, i){
  const o = document.createElement('option');
  o.value = i;
  o.textContent = e.date + '  ·  ' + e.name + '  ·  $' + e.buy_in;
  sel.appendChild(o);
});
HOTELS.forEach(function(h){
  const o = document.createElement('option');
  o.value = h.id;
  o.textContent = h.name + (h.fee === null ? '  —  fee not published' : '  —  fee $' + h.fee);
  hs.appendChild(o);
});
function money(n){ return '$' + Number(n).toLocaleString(undefined,{maximumFractionDigits:2}); }
function calc(){
  const picks = Array.prototype.slice.call(sel.selectedOptions).map(function(o){ return EVENTS[+o.value]; });
  const entries = picks.reduce(function(a,e){ return a + (e.buy_in || 0); }, 0);
  const fees = picks.reduce(function(a,e){ return a + (e.fee || 0); }, 0);
  const nights = +document.getElementById('c-nights').value || 0;
  const parkN = +document.getElementById('c-park').value || 0;
  const rateRaw = document.getElementById('c-rate').value;
  const rate = rateRaw === '' ? null : +rateRaw;
  const h = HOTELS.filter(function(x){ return x.id === hs.value; })[0] || {};
  const feeN = (h.fee === null || h.fee === undefined) ? null : h.fee;
  const park = h.park || 0;
  const lines = [];
  lines.push(['Entries × buy-in (' + picks.length + ')', money(entries), 'exact, from published buy-ins', true]);
  lines.push(['of which withheld as house fees', money(fees), 'already inside the buy-in', true]);
  if (feeN === null){
    lines.push(['Resort fee × nights', 'unknown', 'this property publishes no resort fee that was reachable', false]);
  } else {
    lines.push(['Resort fee × nights', money(feeN * nights), money(feeN) + ' × ' + nights + ' nights, before tax', true]);
  }
  if (rate === null){
    lines.push(['Room rate × nights', 'unknown', 'no dated quote exists — enter a rate to model it, or book and read the checkout', false]);
    lines.push(['Tax at 13.38%', 'unknown', 'needs the room rate', false]);
  } else {
    lines.push(['Room rate × nights', money(rate * nights), money(rate) + ' × ' + nights + ' (your assumption, not a verified rate)', true]);
    const taxable = (rate + (feeN || 0)) * nights;
    lines.push(['Tax at 13.38%', money(taxable * TAX), 'on room rate' + (feeN === null ? '' : ' + resort fee'), true]);
  }
  let hotelTotal = null;
  if (rate !== null && feeN !== null){
    hotelTotal = (rate + feeN) * nights * (1 + TAX) + park * parkN;
    lines.push(['Parking', money(park * parkN), park ? money(park) + ' × ' + parkN + ' nights' : 'free / not published', true]);
    lines.push(['Hotel total (tax included)', money(hotelTotal), 'room + resort fee + tax' + (park ? ' + parking' : ''), true]);
  } else {
    lines.push(['Hotel total', 'INCOMPLETE', 'a term of the hotel side is missing', false]);
  }
  let html = '<table class="kv"><tr><th>Line</th><th>Amount</th><th>Note</th></tr>';
  lines.forEach(function(l){
    html += '<tr class="' + (l[3] ? '' : 'miss') + '"><th>' + l[0] + '</th><td class="num">' + l[1] + '</td><td class="sm">' + l[2] + '</td></tr>';
  });
  html += '</table>';
  if (hotelTotal === null){
    html += '<p class="big">Tournament entries: <b>' + money(entries) + '</b> &middot; Trip total: <b>INCOMPLETE</b></p>';
    html += '<p class="note bad">This is deliberately incomplete. The hotel half of the formula has no verified input on this site, and a made-up nightly rate would hide that. <a href="flagged.html#FD-05">FD-05</a></p>';
  } else {
    html += '<p class="big">Trip total: <b>' + money(entries + hotelTotal) + '</b></p>';
    html += '<p class="note warn">The room rate above is a number you typed. It is not verified. Replace it with an itemised checkout total and store it in the <a href="rates.html">rate log</a>.</p>';
  }
  document.getElementById('c-out').innerHTML = html;
}
sel.addEventListener('change', calc); hs.addEventListener('change', calc);
['c-nights','c-park','c-rate'].forEach(function(id){ document.getElementById(id).addEventListener('input', calc); });
calc();
</script>"""
    calc_js = calc_js.replace("__EVENTS_JSON__", json.dumps(
        [{"date": e["date"], "name": e["name"], "buy_in": e["buy_in_nominal"], "fee": e["fee"]}
         for e in sorted([x for x in EV if x["category"] == "single"],
                         key=lambda x: (x["date"], x["start"]))]))
    calc_js = calc_js.replace("__HOTELS_JSON__", json.dumps(
        [{"id": h["id"], "name": h["name"], "fee": h["resort_fee"], "park": h["parking"]}
         for h in HO]))
    return page("Trip cost", "cost.html", body,
                "entries x buy-in + nights x true hotel cost, with the missing term named.",
                extra_js=calc_js)


def build_rates():
    rows = []
    for r in RATES:
        rows.append([
            '<b>%s</b>' % r["id"], esc(r["hotel"]), r["captured"], esc(r["basis"]),
            money(r.get("nightly_rate")) if r.get("nightly_rate") else "&mdash;",
            money(r.get("resort_fee")) if r.get("resort_fee") else "&mdash;",
            ("%s%%" % round(r["tax_rate"] * 100, 2)) if r.get("tax_rate") else "&mdash;",
            pill("verified" if r.get("verified") else "NOT a quote", "ok" if r.get("verified") else "bad"),
            '<span class="ex">%s</span>' % esc(r["excerpt"]),
            link(r["source_url"]),
        ])
    body = f"""
<section class="hero">
  <h1>Rate log</h1>
  <p class="lede">A rate here is a dated observation with a source, not a standing value. The log
  keeps the rows that failed as well as the rows that succeeded, so the next capture has something
  to be compared against.</p>
  <p class="note">A complete row needs: {"; ".join(R["meta"]["what_a_complete_row_requires"])}.</p>
</section>
<div class="panel">
{table(["ID", "Hotel", "Captured", "Basis", "Nightly rate", "Resort fee", "Tax", "Status", "What the page says", "Source"], rows, "t-rates")}
</div>
<div class="note bad"><b>Why there is no dated total.</b> {esc(R["meta"]["blocking_reason"])}</div>
<div class="panel">
  <h2>What the poker rate actually requires</h2>
  <p class="sm">Quoted from the property's own 2026 poker suite-rate page:</p>
  <ul class="tight">
    <li>Book by phone on 866.255.8936 quoting code EPOKR25, with a Venetian Rewards number ready so play can be tracked.</li>
    <li>Play six hours of active live cash poker <b>or</b> buy in to a $300-or-higher tournament, for each night stayed.</li>
    <li>The requirement must be met before 2 a.m. on the last night stayed.</li>
    <li>Fail a night and that night reverts to the prevailing rate.</li>
    <li>Single or double occupancy, Luxury King Suite; every upgrade is charged on top.</li>
    <li>Future rates are published only 150 days out, and blackout dates apply.</li>
  </ul>
  {link("https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html", "suite-rates.html")}
</div>
"""
    return page("Rate log", "rates.html", body, "Dated, sourced hotel rate observations.")


def build_walking():
    rows = []
    for w in WK:
        rows.append([
            '<b>%s</b>' % w["id"], esc(w["hotel"]), esc(w["hotel_address"]),
            "%s min" % w["walk_minutes"], esc(w["distance_text"]), esc(w["route_label"]),
            pill("within 30 min" if w["within_30_min"] else "over 30 min",
                 "ok" if w["within_30_min"] else "bad"),
            link(w["source_url"], "route"), w["retrieved"],
        ])
    body = f"""
<section class="hero">
  <h1>Walking times</h1>
  <p class="lede">Eleven hotel addresses to the Venetian poker-room address, walking, measured on
  {AS_OF}. The rule is 30 minutes: six pass, five do not.</p>
  <p class="note warn">These are a third-party routing model's street-address-to-street-address
  estimates, not a venue statement, and they are not adjusted for the distance from the front door
  to the poker room inside a resort. Every row carries the exact request URL so the number can be
  re-checked. See <a href="flagged.html#FD-08">FD-08</a>.</p>
</section>
<div class="panel">
{table(["ID", "Hotel", "From address", "Walk", "Distance", "Route", "30-min rule", "Re-check", "Read on"], rows, "t-walk")}
</div>
<div class="panel">
  <h2>What was not done</h2>
  <p class="sm">{esc(W["meta"]["not_done"])}</p>
</div>
"""
    return page("Walking", "walking.html", body,
                "Measured walking times from eleven hotels to the Venetian poker room.")


def build_rules():
    read = [e for e in EV if e["structure_read"]]
    groups = {
        "not_stated": [e for e in read if e["single_entry"] == "not_stated"],
        "explicit_no": [e for e in read if e["single_entry"] == "explicit_no"],
        "explicit_yes": [e for e in read if e["single_entry"] == "explicit_yes"],
    }
    sec = ""
    for key, title, blurb in [
        ("not_stated", "Sheet read, no entry limit printed",
         "Nothing on these sheets forbids or permits a second entry. This is the honest description."),
        ("explicit_no", "Sheet prints a rule that stops a second entry",
         "In every case the rule is the flight rule, not a freezeout rule."),
        ("explicit_yes", "Sheet prints a mechanism for a second entry", ""),
    ]:
        rows = [[esc(e["name"]), e["date"], money(e["buy_in_nominal"]), chip_rule(e["single_entry"]),
                 '<span class="ex">%s</span>' % esc(e["entry_excerpt"]),
                 link(e["source_url"], "sheet %d" % e["sheet"])] for e in groups[key]]
        sec += '<h2>%s &mdash; %d rows</h2>' % (title, len(rows))
        if blurb:
            sec += '<p class="sm">%s</p>' % blurb
        if rows:
            sec += table(["Event", "Date", "Buy-in", "Rule", "Excerpt printed on the sheet", "Source"], rows)
        else:
            sec += ('<p class="sm">No sheet read in this pass prints a rebuy, add-on or multi-entry '
                    'mechanism for a one-day event. The only second-entry route the sheets describe is '
                    'playing a later starting flight of a multi-flight event, which is listed below.</p>')

    sys.path.insert(0, os.path.join(ROOT, "data", "audit"))
    from sheets import SHEETS, sheet_url
    body = f"""
<section class="hero">
  <h1>Entry rules</h1>
  <p class="lede">Single-entry, re-entry, rebuy, add-on and fee are stored as separate fields on
  every row, each with the sentence it came from and the date the sheet was read. The three states
  below are not a scale from best to worst: they are three different things a document can say.</p>
  <p class="note bad"><b>Zero events are confirmed single-entry.</b> Twelve sheets read in full
  print no entry limit for any one-day event. Treating that silence as a freezeout would be an
  inference, so this site does not do it. See <a href="flagged.html#FD-03">FD-03</a> and question
  <a href="questions.html#IQ-03">IQ-03</a>.</p>
</section>
<div class="panel">{sec}</div>
<div class="panel">
  <h2>Fee wording, quoted</h2>
  <p class="sm">Every row reconciles: fee + amount per entry = the published buy-in.</p>
  {table(["Sheet", "Event numbers", "Fee withheld", "Amount per entry to the prize pool", "Source"],
    [[str(s["sheet"]), ", ".join(n.lstrip("0") for n in s["event_numbers"]),
      money(s["fee"]), money(s["pool_per_entry"]), link(sheet_url(s["sheet"]), "PDF")]
     for s in SHEETS])}
</div>
"""
    return page("Entry rules", "rules.html", body, "Three-state entry-rule evidence, quoted, per event.")


def build_venues():
    single_read = [e for e in EV if e["category"] == "single" and e["structure_read"]]
    inwalk = [h for h in HO if h["walk_within_30"]]
    blocks = []
    for vid, name, evs, note, urls, hotels in [
        ("V-POKER", "The Venetian Poker Room / The Palazzo", EV,
         "The only venue with a full dated tournament series inside the trip window: 94 published rows across 37 structure sheets.",
         [("Schedule page", SCHEDULE_URL),
          ("Series overview", "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"),
          ("Poker room", "https://www.venetianlasvegas.com/resort/casino/poker.html")],
         inwalk),
        ("V-WYNN", "Wynn / Encore Poker Room", [],
         "No dated Wynn event was verified in this pass. Earlier sessions recorded Wynn WPT rows, but this audit publishes only what it read itself, so the venue is listed with zero rows rather than importing unverified values.",
         [("Wynn poker", "https://www.wynnlasvegas.com/casino/poker")], []),
        ("V-CAESARS", "Caesars Palace / Horseshoe", [],
         "No dated Caesars or Horseshoe tournament was verified in this pass. Caesars Palace also has no verified resort fee: the hotel-policy URL redirects to the property home page.",
         [("Caesars Palace", "https://www.caesars.com/caesars-palace"),
          ("Horseshoe", "https://www.caesars.com/horseshoe-las-vegas")], []),
        ("V-MGM", "Bellagio / ARIA / MGM Grand", [],
         "MGM Resorts properties appear here as hotel candidates with verified resort fees and occupancy charges, not as tournament venues: no dated MGM tournament schedule was read in this pass.",
         [("Bellagio terms", "https://bellagio.mgmresorts.com/en/terms-and-conditions.html"),
          ("ARIA terms", "https://aria.mgmresorts.com/en/terms-and-conditions.html"),
          ("MGM Grand terms", "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html")], []),
    ]:
        blocks.append(f"""
<section class="panel" id="{vid}">
  <h2>{esc(name)}</h2>
  <p class="sm">{esc(note)}</p>
  <p class="sm">Official documents: {" &middot; ".join(link(u, l) for l, u in urls)}</p>
  <table class="kv">
    <tr><th>Rows published here</th><td>{len(evs)}</td></tr>
    <tr><th>One-day events with a structure sheet read</th><td>{len(single_read) if vid == 'V-POKER' else 0}</td></tr>
    <tr><th>Hotels inside the 30-minute walk</th><td>{len(hotels) if vid == 'V-POKER' else '&mdash;'}</td></tr>
  </table>
</section>""")
    body = f"""
<section class="hero">
  <h1>Venues</h1>
  <p class="lede">One block per venue, with the events and hotels that belong to it. A venue shows
  zero rows when no dated schedule from that venue was read in this pass &mdash; empty is a fact
  here, not an omission.</p>
</section>
{''.join(blocks)}
"""
    return page("Venues", "venues.html", body, "One section per venue with its events and hotels.")


def build_summary():
    n_sheets = len(SHEETS)
    n_unread_sheets = len(UNREAD_SHEETS)
    n_unread = sum(1 for e in EV if not e["structure_read"])
    n_late = sum(1 for e in EV if e["late_reg_time"])
    n_pays = sum(1 for e in EV if e["pays_pct"])
    if n_unread:
        unread_li = ("<li>%d rows have no fee or structure, because %d sheets were not read.</li>"
                     % (n_unread, n_unread_sheets))
    else:
        unread_li = ("<li><b>Nothing is left unread.</b> Every one of the %d sheets has now been "
                     "read in full, which retired the earlier build's largest gap.</li>" % n_sheets)
    rows = [
        ["Best tournaments on cost and prize pool, single entry only",
         pill("partly answered", "warn"),
         "Prize pool, buy-in and fee are known for 48 of 94 rows. Single-entry status is known for none: twelve sheets read in full print no entry limit. A winner cannot be named on a rule that is not in print."],
        ["Keep spend-to-advance events separate",
         pill("done", "ok"),
         "Rows whose sheet prints a re-entry mechanism, or a guarantee defined to include bounties, are labelled and kept out of the like-for-like comparison (<a href='flagged.html#FD-07'>FD-07</a>)."],
        ["Best hotels by cost, quality and a walk under 30 minutes",
         pill("partly answered", "warn"),
         "Six hotels pass the walk test. Six have a verified resort fee (Venetian, Palazzo, Wynn, Bellagio, ARIA at $55; MGM Grand at $50) and five have none reachable. No dated room rate exists, so cost per night cannot yet be ranked."],
        ["True cost of the hotel per night",
         pill("blocked", "bad"),
         "Blocked on one input: a dated checkout total. Fee, tax, parking and cancellation terms are verified for the properties listed; the room rate is not obtainable from a static site."],
        ["A full day starting at 8 AM",
         pill("answered: not possible here", "bad"),
         "The earliest row in the series is 09:10 and the earliest one-day event is 10:10. No Venetian schedule starts at 8 AM (<a href='flagged.html#FD-11'>FD-11</a>)."],
        ["Enter as many tournaments as possible",
         pill("partly answered", "warn"),
         "The usable window is 2026-11-19 to 2026-12-22, where every day has at least one one-day event. The busiest days have two or three rows, but a second entry is only real if the first event is left before the second one's late-registration close."],
        ["Executive summary",
         pill("this page", "ok"), "Below."],
        ["Suggestions section to review before changes",
         pill("done", "ok"),
         "%d numbered suggestions, each with the decision it needs: <a href='suggestions.html'>Suggestions</a>." % len(SG)],
        ["Questions and missing information",
         pill("done", "ok"),
         "%d numbered questions, each with how to close it: <a href='questions.html'>Questions</a>." % len(QT)],
        ["Every row sourced, blanks flagged",
         pill("done", "ok"),
         "The build fails if a row has no https source. %d flagged items are published with their evidence." % len(FL)],
    ]
    top = sorted([e for e in EV if e["structure_read"] and e["gtd_basis"] == "prize pool"
                  and e["gtd_ratio_descriptive"]],
                 key=lambda e: -e["gtd_ratio_descriptive"])[:8]
    body = f"""
<section class="hero">
  <h1>Executive summary</h1>
  <p class="lede">What the documents support, what they do not, and what to do next.</p>
</section>

<section class="panel">
  <h2>Your questions, answered</h2>
  {table(["Question", "State", "Answer"], rows)}
</section>

<section class="panel">
  <h2>The eight published guarantees with the highest guarantee-per-entry &mdash; pure prize pool only</h2>
  <p class="sm">Arithmetic on two published numbers. It is not a ranking of value: the guarantee is
  a floor, field size is unknown, and a higher ratio does not mean a better tournament.
  Bounty-inclusive guarantees are excluded (<a href="flagged.html#FD-07">FD-07</a>).</p>
  {table(["Date", "Event", "Buy-in", "GTD", "GTD &divide; fee", "Source"], [
    ['<span class="nowrap">%s</span>' % e["date"], esc(e["name"]), money(e["buy_in_nominal"]),
     money(e["gtd"]), money(e["gtd_ratio_descriptive"]), link(e["source_url"], "sheet %d" % e["sheet"])]
    for e in top])}
</section>

<section class="grid2">
 <div class="panel">
  <h2>What is solid</h2>
  <ul class="tight">
    <li>94 schedule rows transcribed from the official page.</li>
    <li>All {n_sheets} structure sheets read in full; every fee split sums exactly to the buy-in on all {len(EV)} rows (0 mismatches).</li>
    <li>Room tax 13.38% corroborated by a county document and by the property's own terms.</li>
    <li>Walking times measured for all eleven hotel candidates, with re-checkable URLs.</li>
    <li>Late-registration close for {n_late} rows and a payout percentage for {n_pays} rows &mdash; values the earlier dashboards left blank. The other {len(EV) - n_late} close times and {len(EV) - n_pays} payout figures are blank because the sheet does not print one.</li>
  </ul>
 </div>
 <div class="panel">
  <h2>What is not</h2>
  <ul class="tight">
    <li>No confirmed single-entry event. All {n_sheets} sheets read; none prints an entry-limit clause, and the 22 rows carrying an "no second entry" quote are quoting the multi-flight rule, not a freezeout (<a href="flagged.html#FD-03">FD-03</a>).</li>
    <li>No dated room rate. The hotel side of the trip cost has no verified input.</li>
    {unread_li}
    <li>Four hotels publish no reachable resort fee.</li>
    <li>No automatic source check in this repository has ever completed a scheduled run (<a href="flagged.html#FD-01">FD-01</a>).</li>
  </ul>
 </div>
</section>

<section class="panel">
  <h2>If you had to decide today</h2>
  <ol class="tight">
    <li>Pick a <b>4-night window between 2026-11-19 and 2026-12-22</b>: every day in that range has at least one one-day event.</li>
    <li>Stay at <b>The Venetian or The Palazzo</b>: 0 and 7 minutes on foot, the only properties whose poker-suite rate is published, and the only ones where a $300+ buy-in also satisfies that rate's qualifying play.</li>
    <li>Make a <b>$200 RaceDay Stack</b> (10:10 AM, $35 fee) or a <b>$300/$600 one-day</b> (11:10 AM, $58/$90 fee) the primary each day, and treat a 5:10 PM event as a fallback only if you bust before its late-registration close.</li>
    <li><b>Do not</b> treat any of them as single-entry until the poker room confirms it in writing (<a href="questions.html#IQ-03">IQ-03</a>).</li>
    <li>Get an itemised checkout total for the dates before booking, and record it in the <a href="rates.html">rate log</a>.</li>
  </ol>
</section>
"""
    return page("Executive summary", "summary.html", body, "Answers, evidence and the decision path.")


def build_questions():
    def status_pill(e):
        st = e.get("status", "")
        if e.get("answer"):
            return pill("answered", "ok")
        if "partly" in st:
            return pill("partly answered", "warn")
        return pill("open", "warn")

    def answer_cell(e):
        # a question that has since been answered shows the answer, not the old gap text
        if e.get("answer"):
            return esc(e["answer"])
        return esc(e.get("why", ""))

    rows = [[e["id"], esc(e["question"]), answer_cell(e), esc(e["how_to_close"]),
             esc(e["can_be_closed_here"]), esc(e["blocks"]), status_pill(e),
             link(e["source_url"])] for e in QT]
    closed = sum(1 for e in QT if e.get("answer"))
    body = f"""
<section class="hero">
  <h1>Questions that must be answered before a decision</h1>
  <p class="lede">Each item names what is unknown, why it matters, exactly how to close it, and
  whether it can be closed from a document that already exists.</p>
  <p class="note">{len(QT)} items. <b>{closed} have since been answered</b> and now show the answer
  instead of the gap &mdash; reading all 37 structure sheets closed three of them. The remaining
  items need a booking engine, a phone call or a decision from you.</p>
</section>
<div class="panel">
{table(["ID", "Question", "Answer / why it matters", "How to close it", "Closable from a document?", "What it blocks", "Status", "Source"], rows, "t-q")}
</div>
"""
    # anchor rows so questions.html#IQ-03 works
    for e in QT:
        body = body.replace("<td>%s</td>" % e["id"], '<td id="%s">%s</td>' % (e["id"], e["id"]), 1)
    return page("Questions", "questions.html", body,
                "What is unknown, why it matters, and how to close it.")


def build_suggestions():
    rows = [[e["id"], "<b>%s</b>" % esc(e["title"]), esc(e["problem"]), esc(e["options"]),
             esc(e["trade_off"]), esc(e["needs_decision"]), esc(e["effort"]),
             pill("recommended: " + e["recommendation"], "ok")] for e in SG]
    body = f"""
<section class="hero">
  <h1>Suggestions</h1>
  <p class="lede">Changes worth making, each with the problem it solves, the options, the trade-off
  and the decision it needs from you. Nothing here is implemented without being listed, and the
  four already implemented are named as such.</p>
  <p class="note">Implemented already because they remove a false statement at no cost: SG-06
  (per-URL monitor status), SG-07 (ratio labelled as a floor), SG-08 (day plan as a decision tree),
  SG-09 (every flag names the decision it blocks).</p>
</section>
<div class="panel">
{table(["ID", "Suggestion", "Problem", "Options", "Trade-off", "Decision needed", "Effort", "Pick"], rows, "t-s")}
</div>
"""
    return page("Suggestions", "suggestions.html", body, "Options with the decision each one needs.")


def build_flagged():
    by_sev = {}
    for f in FL:
        by_sev.setdefault(f["severity"], []).append(f)
    sec = ""
    for sev, label in [("high", "High &mdash; changes what a number means"),
                       ("medium", "Medium &mdash; changes how far a number can be trusted"),
                       ("low", "Low &mdash; disclosure only")]:
        def what(f):
            # a flag that has since been fixed says so, rather than reading as still open
            txt = esc(f["action"])
            if f.get("resolution"):
                txt += ('<div class="sm" style="margin-top:5px;color:#7fd6a0"><b>&#10003; fixed</b> '
                        '&mdash; %s</div>' % esc(f["resolution"]))
            return txt

        section_rows = [['<span id="%s">%s</span>' % (f["id"], f["id"]),
                         "<b>%s</b>" % esc(f["title"]), esc(f["finding"]),
                         esc(f["why_it_matters"]), esc(f["evidence"]), link(f["source_url"]),
                         what(f)] for f in by_sev.get(sev, [])]
        sec += '<h2>%s (%d)</h2><div class="panel">%s</div>' % (
            label, len(section_rows),
            table(["ID", "Item", "Finding", "Why it matters", "Evidence", "Source", "What this build does"],
                  section_rows))
    body = f"""
<section class="hero">
  <h1>Flagged for review</h1>
  <p class="lede">Every irregularity this pass found, with the document that shows it and what was
  done about it. These do not block publication; they block trusting a specific number.</p>
  <p class="note">{len(FL)} items. Anchors are stable, so <code>flagged.html#FD-03</code> can be
  linked from anywhere on the site.</p>
</section>
{sec}
<div class="panel">
  <h2>Also flagged in the repository, not on this site</h2>
  <ul class="tight">
    <li><b>README.md ships merge-conflict markers.</b> Open PR #43 owns that file; this session did not edit it. <a href="https://github.com/karagemop466-tech/Poker2/blob/main/README.md">README.md</a></li>
    <li><b>Four scheduled workflows have never run on a schedule.</b> <a href="flagged.html#FD-01">FD-01</a>.</li>
    <li><b>Three dashboards publish different headline counts.</b> <a href="flagged.html#FD-15">FD-15</a> and suggestion <a href="suggestions.html">SG-01</a>.</li>
  </ul>
</div>
"""
    return page("Flagged for review", "flagged.html", body,
                "Every unverified value and irregularity, with sources.")


def build_sources():
    sys.path.insert(0, os.path.join(ROOT, "data", "audit"))
    from sheets import SHEETS, UNREAD_SHEETS, sheet_url
    sheet_rows = [["%d" % s["sheet"], esc(s["doc_title"]),
                   ", ".join(n.lstrip("0") for n in s["event_numbers"]),
                   pill("read", "ok"), link(sheet_url(s["sheet"]), "PDF")] for s in SHEETS]
    unread_rows = [["%d" % n, pill("not read", "muted"), link(sheet_url(n), "PDF")]
                   for n in UNREAD_SHEETS]
    other = [
        ["Venetian DSE IV schedule page", "venue", "94 rows: date, time, event no, name, sheet link", link(SCHEDULE_URL)],
        ["Venetian series overview", "venue", "series dates and headline guarantees", link("https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html")],
        ["Venetian resort fee page", "venue", "$55 plus tax per night", link("https://www.venetianlasvegas.com/resort/resort-fee.html")],
        ["Venetian hotel terms", "venue", "13.38% room tax, $50 extra guest, $20/day parking, $150/night incidentals", link("https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html")],
        ["Venetian poker suite rates", "venue", "$119 / $209 from-prices and the qualifying-play requirement", link("https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html")],
        ["Wynn terms", "venue", "$55 fee, $50 extra guest, prepaid non-refundable", link("https://www.wynnlasvegas.com/terms-and-conditions/850257")],
        ["Bellagio terms", "venue", "$55 fee, $50 extra guest, 72-hour cancellation", link("https://bellagio.mgmresorts.com/en/terms-and-conditions.html")],
        ["ARIA terms", "venue", "$55 fee, $50 extra guest, 72-hour cancellation", link("https://aria.mgmresorts.com/en/terms-and-conditions.html")],
        ["MGM Grand terms", "venue", "$50 fee, $40 extra guest, 72-hour cancellation", link("https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html")],
        ["Clark County transient lodging guide", "government", "13.38% resort-hotel transient lodging tax", link("https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf")],
        ["Google Maps walking directions", "third-party routing", "11 hotel-to-venue walking times, each with its request URL", link("https://www.google.com/maps")],
    ]
    body = f"""
<section class="hero">
  <h1>Sources</h1>
  <p class="lede">Every document this site reads, split by whether it is the venue's own
  publication, a government document, or a third-party service that is labelled as such wherever
  its value appears.</p>
</section>
<div class="panel">
  <h2>Venue and government documents</h2>
  {table(["Document", "Type", "What it is used for", "Link"], other)}
</div>
<div class="panel">
  <h2>Structure sheets read ({len(SHEETS)})</h2>
  {table(["Sheet", "Document title", "Event numbers printed on it", "State", "Link"], sheet_rows)}
</div>
<div class="panel">
  <h2>Structure sheets not read ({len(UNREAD_SHEETS)})</h2>
  <p class="sm">Linked from the official schedule page but not opened in this pass. The rows that
  use them publish only date, time, event number, name and this link.</p>
  {table(["Sheet", "State", "Link"], unread_rows)}
</div>
"""
    return page("Sources", "sources.html", body, "Every document read, and every one not read.")


def build_monitor():
    try:
        mon = load("monitor.json")
    except FileNotFoundError:
        mon = {"meta": {}, "urls": [], "runs": []}
    urls = mon.get("urls", [])
    rows = []
    for u in urls:
        last = u.get("last_checked") or "never"
        st = u.get("status") or "never checked"
        kind = "ok" if st == "ok" else ("bad" if "CHANGED" in str(st)
               else ("warn" if st.startswith("error") else "muted"))
        sha = (u.get("sha256") or "")
        rows.append([esc(u.get("id")), link(u.get("url")), esc(u.get("http", "")), last,
                     pill(st, kind), '<code class="tiny">%s</code>' % esc(sha[:16] + ("…" if sha else ""))])
    runs = mon.get("runs", [])
    run_rows = [[r.get("run_at", ""), r.get("checked", ""), r.get("ok", ""), r.get("changed", ""),
                 r.get("unprobed", ""), r.get("errors", "")] for r in runs[-20:]]
    body = f"""
<section class="hero">
  <h1>Source monitor</h1>
  <p class="lede">Every URL this site depends on, with the last HTTP status and a hash of the
  response body. A hash change is reported as <b>CHANGED</b> and never treated as proof that a
  cited value changed &mdash; it means re-read the document.</p>
  <p class="note">{esc(mon.get("runs", [{}])[-1].get("note", "")) if mon.get("runs") else ""}</p>
  <p class="note">This monitor is honest about its own state. If the table says
  &ldquo;never checked&rdquo;, no run has completed, and the page says so instead of printing a
  green tick it did not earn. That is the defect it was built to fix
  (<a href="flagged.html#FD-01">FD-01</a>).</p>
</section>
<div class="panel">
  <h2>Runs</h2>
  {table(["Run at (UTC)", "URLs", "OK", "Changed", "Unprobed", "Errors"], run_rows) if run_rows else '<p class="sm">No run recorded yet in this checkout. Run <code>python3 scripts/audit_recheck.py</code>, or wait for the scheduled job in <code>.github/workflows/audit-recheck.yml</code>.</p>'}
</div>
<div class="panel">
  <h2>Monitored URLs ({len(urls)})</h2>
  {table(["ID", "URL", "HTTP", "Last checked", "Status", "SHA-256"], rows, "t-mon") if rows else '<p class="sm">The URL registry is written by <code>scripts/audit_recheck.py</code> on its first run.</p>'}
</div>
"""
    return page("Source monitor", "monitor.html", body,
                "Per-URL status and content hashes for every official source.")


PAGES = {
    "index.html": build_index,
    "events.html": build_events,
    "schedule.html": build_schedule,
    "hotels.html": build_hotels,
    "cost.html": build_cost,
    "rates.html": build_rates,
    "walking.html": build_walking,
    "rules.html": build_rules,
    "venues.html": build_venues,
    "summary.html": build_summary,
    "questions.html": build_questions,
    "suggestions.html": build_suggestions,
    "flagged.html": build_flagged,
    "sources.html": build_sources,
    "monitor.html": build_monitor,
}


def check():
    problems = []
    for e in EV:
        if not (e.get("source_url") or "").startswith("https://"):
            problems.append("event %s has no https source" % e["id"])
    for h in HO:
        if not any((h.get(k) or "").startswith("https://") for k in ("fee_url", "walk_source_url", "booking_url")):
            problems.append("hotel %s has no https source" % h["id"])
    for w in WK:
        if not (w.get("source_url") or "").startswith("https://"):
            problems.append("walk row %s has no https source" % w["id"])
    for f in FL:
        if not (f.get("source_url") or "").startswith("https://"):
            problems.append("flag %s has no https source" % f["id"])
    for q in QT:
        if not (q.get("source_url") or "").startswith("https://"):
            problems.append("question %s has no https source" % q["id"])
    for r in RATES:
        if not (r.get("source_url") or "").startswith("https://"):
            problems.append("rate %s has no https source" % r["id"])
    return problems


def link_check():
    bad = []
    for fn in PAGES:
        p = os.path.join(OUT, fn)
        txt = open(p, encoding="utf-8").read()
        for href in re.findall(r'href="([^"#:]+\.html)(?:#[^"]*)?"', txt):
            # audit pages live in audit/; ../x.html reaches the repository root surfaces
            bad.append("%s -> %s" % (fn, href)) if not os.path.exists(
                os.path.normpath(os.path.join(OUT, href))) else None
        for href in re.findall(r'href="((?:\.\./)[^"]+)"', txt):
            if not os.path.exists(os.path.normpath(os.path.join(OUT, href))):
                bad.append("%s -> %s" % (fn, href))
        for a in re.findall(r'href="#([^"]+)"', txt):
            if ('id="%s"' % a) not in txt:
                bad.append("%s -> #%s (no such anchor)" % (fn, a))
    return bad


def main():
    problems = check()
    if problems:
        print("BUILD FAILED - rows without an official source:")
        for p in problems:
            print("  ", p)
        sys.exit(1)
    os.makedirs(OUT, exist_ok=True)
    for fn, fnc in PAGES.items():
        with open(os.path.join(OUT, fn), "w", encoding="utf-8") as fh:
            fh.write(fnc())
    bad = link_check()
    if bad:
        print("BUILD FAILED - broken links:")
        for b in bad:
            print("  ", b)
        sys.exit(1)
    # prove the built pages actually work: filters bind, counters move, and the cost
    # calculator's arithmetic matches its own stated inputs. Skipped only if jsdom is
    # absent, in which case the reason is printed rather than the check silently passing.
    if os.path.exists(os.path.join(ROOT, "scripts", "audit_dom_test.js")):
        try:
            r = subprocess.run(
                ["node", "audit_dom_test.js"],
                cwd=os.path.join(ROOT, "scripts"),
                capture_output=True, text=True, timeout=180)
        except FileNotFoundError:
            print("  DOM test skipped: node not installed")
        except subprocess.TimeoutExpired:
            print("  DOM test FAILED: timed out")
            sys.exit(1)
        else:
            if r.returncode == 2:
                print("  DOM test skipped: " + r.stderr.strip().splitlines()[0])
            elif r.returncode != 0:
                print("BUILD FAILED - DOM test:")
                print(r.stdout[-3000:])
                print(r.stderr[-1500:])
                sys.exit(1)
            else:
                last = [l for l in r.stdout.strip().splitlines() if l.strip()][-1]
                print("  DOM test " + last.strip())

    print("built %d pages into audit/" % len(PAGES))
    print("  events %d | hotels %d | walk rows %d | flags %d | questions %d | suggestions %d"
          % (len(EV), len(HO), len(WK), len(FL), len(QT), len(SG)))




# --------------------------------------------------------------- root landing page

if __name__ == "__main__":
    main()
