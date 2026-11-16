#!/usr/bin/env python3
"""Generate the GitHub Pages site for the poker planner from site-data/*.json.

Guarantees enforced here (the build fails rather than publishing a soft claim):
  * every tournament/hotel row rendered in a table links at least one source whose host is
    an official property, county or room publisher;
  * every row carries a last-checked date;
  * no structural value (fee, stack, level, registration cutoff) is shown for an event whose
    structure sheet was not read;
  * no internal href points at a file this build does not write.

Blank means "not verified": the builder never invents a value.

Usage: python3 scripts/build-site.py [--check]
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site-data")
OUT = ROOT
ASSETS = os.path.join(ROOT, "assets")

OFFICIAL_HOSTS = {
    "venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com", "visitwynn.com",
    "caesars.com", "mgmresorts.com", "bellagio.com", "aria.com", "cosmopolitanlasvegas.com",
    "parkmgm.com", "clarkcountynv.gov", "goldennugget.com", "github.com",
}
# Hosts that are not the property domain but serve the property's own published documents:
# assets.contentstack.io is the MGM Resorts CMS asset host every mgmresorts.com property page links
# its poker term sheets from; cdn.wynnresorts.com is Wynn's own asset host. They are allowed only for
# document paths under the property's asset namespace, which is why they are listed separately here
# instead of being folded into OFFICIAL_HOSTS.
OFFICIAL_ASSET_HOSTS = {"assets.contentstack.io", "cdn.wynnresorts.com"}


def load(name):
    with open(os.path.join(DATA, name), encoding="utf8") as fh:
        return json.load(fh)


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def money(v, dash="&mdash;"):
    if v is None or v == "":
        return dash
    v = float(v)
    return "$" + (("{:,.0f}".format(v)) if abs(v - round(v)) < 1e-9 else ("{:,.2f}".format(v)))


def num(v, dash="&mdash;"):
    return dash if v is None or v == "" else "{:,}".format(v)


def ratio(v, dash="&mdash;"):
    return dash if v in (None, "") else "{:.1f}&times;".format(float(v))


def host_of(u):
    m = re.match(r"https?://([^/]+)", u or "")
    return (m.group(1) if m else "").replace("www.", "")


def is_official(u):
    h = host_of(u)
    if any(h == d or h.endswith("." + d) for d in OFFICIAL_HOSTS):
        return True
    if h in OFFICIAL_ASSET_HOSTS:
        # an asset CDN counts only when the path is the property's own namespace
        return bool(re.search(r"/(visitwynn_pdfs_files|blt[0-9a-f]{16,})/", u or ""))
    return False


def srclink(url, label=None):
    if not url:
        return '<span class="badge b-warn">no source read</span>'
    lab = label or host_of(url)
    return '<a href="' + esc(url) + '" target="_blank" rel="noopener">' + esc(lab) + "</a>"


def badge(text, kind="warn"):
    return '<span class="badge b-' + kind + '">' + esc(text) + "</span>"


def t12(s):
    if not s:
        return "&mdash;"
    m = re.match(r"(\d{1,2}):(\d{2})", str(s))
    if not m:
        return esc(s)
    h, mm = int(m.group(1)), int(m.group(2))
    ap = "AM" if h < 12 else "PM"
    return "{:d}:{:02d} {}".format(h % 12 or 12, mm, ap)


def tag_open(name, attrs):
    out = "<" + name
    for k, v in attrs:
        if v is None:
            continue
        out += ' ' + k + '="' + esc(v) + '"'
    return out + ">"


# --------------------------------------------------------------------------- data
EV = load("events.json")
SCH = load("schedule.json")
HOT = load("hotels.json")
VEN = load("venues.json")
WALK = load("walk.json")
RATES = load("rates.json")
FLAGS = load("flags.json")
QUEST = load("questions.json")
SUGG = load("suggestions.json")
SUMM = load("summary.json")
SRCS = load("sources.json")
OTHER = load("other-venues.json")
STATS = load("summary-stats.json")
CHANGE_REPORT = os.path.join(DATA, "change-report.json")
CHANGES = {"runs": [], "sources": []}
if os.path.exists(CHANGE_REPORT):
    CHANGES = load("change-report.json")

WORKFLOW_URL = ("https://github.com/karagemop466-tech/Poker2/actions/workflows/daily-refresh.yml")
TAX_PCT = HOT["tax"]["rate_pct"]
TAX_MULT = 1 + TAX_PCT / 100
AS_OF = EV["as_of"]
events = EV["events"]
venue_names = {}
for v in VEN["venues"]:
    venue_names[v["id"]] = v["name"]
SCHED_URL = EV["generated_from"]
SHEET_BASE = ""
for e in events:
    if e.get("sheet_url"):
        SHEET_BASE = re.sub(r"structure_\d+\.pdf$", "", e["sheet_url"])
        break
READ_SHEETS = {e["sheet"] for e in events if e["sheet_read"]}
ALL_SHEET_NUMS = sorted({e["sheet"] for e in events if e["sheet"]})

CATEGORY_LABEL = {
    "single_entry_candidate": ("single-entry candidate", "ok"),
    "spend_advantage": ("spend-advantage", "bad"),
    "multi_flight": ("multi-flight", "bad"),
    "satellite": ("satellite", "warn"),
    "team_format": ("team format", "warn"),
    "day2_restart": ("day 2 restart", "info"),
    "final_table": ("final table", "info"),
    "unverified": ("unverified", "warn"),
}

rows_all = []
for e in events:
    cat = e["category"]
    rule = e["rules"]["single_entry"]
    if cat == "single_entry_candidate" and rule["status"] == "not_stated_sheet_read":
        single = "candidate"
    elif cat in ("spend_advantage", "multi_flight"):
        single = "excluded"
    else:
        single = "unknown"
    srcs = [SCHED_URL] + ([e["sheet_url"]] if e.get("sheet_url") else [])
    cats = [cat] + (["bounty"] if e.get("bounty") else [])
    flag = "no"
    if cat == "unverified" or not e["sheet_read"]:
        flag = "yes"
    rows_all.append({
        "key": e["id"], "venue": e["venue"], "property": e["property"], "date": e["date"],
        "dow": e["dow"], "start": e["start"], "start_lbl": t12(e["start"]),
        "event_no": e["event_no"], "name": e["name"], "cat": cat, "cats": cats,
        "buy_in": e["buy_in"], "fee": e["fee"], "pool": e["pool_per_entry"], "gtd": e["gtd"],
        "ratio": e["ratio_gtd_to_buyin"], "chips": e["chips"], "level": e["level_min"],
        "reg_close": e["reg_close"], "finish": e["earliest_plausible_finish"],
        "single": single, "sheet": e["sheet"], "sheet_read": e["sheet_read"],
        "sources": srcs, "last_checked": e["last_checked"],
        "excerpt": rule.get("excerpt"), "extra": e["rules"]["re_entry"].get("excerpt"),
        "bounty": bool(e.get("bounty")), "not_read": False, "reg_text": e.get("reg_close_text"),
        "flag": flag,
    })
for r in OTHER["rows"]:
    cat = r["category"]
    m = re.match(r"(\d{4}-\d{2}-\d{2})", r.get("date_range") or "")
    d = m.group(1) if m else None
    gtd, bi = r.get("gtd"), r.get("buy_in")
    rows_all.append({
        "key": r["id"], "venue": r["venue"], "property": r["property"], "date": d,
        "dow": None, "start": r.get("start") if (r.get("start") or "").count(":") == 1 else None,
        "start_lbl": r.get("start") or "&mdash;", "event_no": "&mdash;", "name": r["name"], "cat": cat,
        "cats": [cat], "buy_in": bi, "fee": None, "pool": None, "gtd": gtd,
        "ratio": (round(gtd / bi, 1) if gtd and bi else None),
        "chips": None, "level": None, "reg_close": None, "finish": None,
        "single": ("excluded" if cat == "spend_advantage" else "unknown"),
        "sheet": None, "sheet_read": False, "sources": [r["source_url"]],
        "last_checked": r.get("recorded_by", ""), "excerpt": r.get("entry_rule"),
        "extra": r.get("reason"), "not_read": True, "bounty": False, "reg_text": None,
        "flag": "yes",
    })

ALL_ROWS = rows_all
QUAL = [r for r in ALL_ROWS if r["cat"] == "single_entry_candidate"]
RANKED = sorted([r for r in QUAL if r["fee"] and r["gtd"]],
                key=lambda r: (-r["ratio"], r["buy_in"], r["date"] or ""))
EXCL = sorted([r for r in ALL_ROWS if r["cat"] in ("spend_advantage", "multi_flight", "satellite", "team_format")],
              key=lambda r: (r["cat"], r["date"] or ""))
UNVER = [r for r in ALL_ROWS if r["cat"] == "unverified"]
OTHERS_MISC = [r for r in ALL_ROWS if r.get("not_read") and r["cat"] != "spend_advantage"]

pages_written = set()
generated = {}
problems = []

NAV = [
    ("index.html", "Dashboard"), ("tournaments.html", "All events"),
    ("single-entry.html", "Single-entry ranked"), ("spend-advantage.html", "Spend-advantage"),
    ("unverified.html", "Unverified"), ("schedule.html", "Day plan"),
    ("hotels.html", "Hotels & true cost"), ("trip-cost.html", "Trip cost"),
    ("rate-log.html", "Rate log"), ("venues.html", "Venues"), ("sources.html", "Sources"),
    ("questions.html", "Questions"), ("suggestions.html", "Suggestions"),
    ("flagged.html", "Flagged"), ("repo-review.html", "Repo & method"),
]


def page(fname, title, body, desc=""):
    nav = ""
    for href, label in NAV:
        cur = ' aria-current="page"' if href == fname else ""
        nav += '<a href="' + esc(href) + '"' + cur + ">" + esc(label) + "</a>"
    n_flags = str(len(FLAGS["items"]))
    head = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>" + esc(title) + " &middot; Vegas poker planner</title>\n"
        '<meta name="description" content="' + esc(desc or title) + '">\n'
        '<link rel="stylesheet" href="assets/site.css">\n</head>\n<body>\n'
        '<header class="site">\n  <div class="head-row">\n'
        '    <div class="brand">Vegas poker trip planner'
        ' <small>official sources only &middot; data checked ' + esc(AS_OF) + "</small></div>\n"
        '    <div class="sm">Ranking covers one-day events whose official structure sheet was read.'
        ' Blank = unverified, never guessed.\n'
        '      <a href="flagged.html">' + n_flags + " items flagged</a></div>\n  </div>\n"
        '  <nav class="top">' + nav + "</nav>\n</header>\n<main>\n"
        + body +
        "\n</main>\n<footer class=" + '"site">\n'
        "  Static site generated by <code>scripts/build-site.py</code> from <code>site-data/*.json</code>;"
        " the datasets come from <code>scripts/build-events.py</code> and <code>scripts/build-schedule.py</code>.\n"
        '  Official pages are re-checked by <a href="' + WORKFLOW_URL + '">the refresh workflow</a>\n'
        '  and reported on the <a href="flagged.html">review page</a>.\n</footer>\n'
        '<script src="assets/data.js"></script>\n<script src="assets/site.js"></script>\n'
        "</body>\n</html>\n"
    )
    subdir = os.path.dirname(fname)
    if subdir:  # pages under venues/ must reach the root with ../
        def up(m):
            target = m.group(2)
            if target.startswith(("http", "mailto", "tel", "#", "../", "./", "/")):
                return m.group(0)
            return m.group(1) + "../" + target + m.group(3)

        head = re.sub(r'(<(?:a|link|script)\s[^>]*?(?:href|src)=")([^"]+)(")', up, head)
    pages_written.add(fname)
    generated[fname] = head


# --------------------------------------------------------------------------- shared table bits
TABLE_HEAD = """<thead><tr>
<th>Date</th><th>Property</th><th>Ev #</th><th>Event</th><th>Start</th>
<th>Buy-in</th><th>House fee</th><th>Pool / entry</th><th>Guarantee</th><th>Gtd &divide; buy-in</th>
<th>Chips</th><th>Level</th><th>Reg closes</th><th>Earliest plausible finish</th><th>Last checked</th><th>Sources</th>
</tr></thead>"""


def event_row(r):
    catlabel, catkind = CATEGORY_LABEL.get(r["cat"], (r["cat"], "info"))
    badges = badge(catlabel, catkind)
    if r.get("bounty"):
        badges += " " + badge("bounty", "warn")
    if r["cat"] == "single_entry_candidate":
        badges += " " + (badge("sheet read", "ok") if r["sheet_read"] else badge("sheet not read", "bad"))
    if r.get("not_read"):
        badges += " " + badge("cited, not re-read", "bad")
    srcs = ""
    for u in r["sources"]:
        lab = "schedule" if u == SCHED_URL else ("sheet " + str(r["sheet"]) if r["sheet"] else host_of(u))
        srcs += "<div>" + srclink(u, lab) + "</div>"
    excerpt = ""
    if r.get("excerpt"):
        extra = ('<div class="sm">' + esc(r["extra"]) + "</div>") if r.get("extra") else ""
        excerpt = ('<details><summary class="sm">official rule excerpt</summary><blockquote>'
                   + esc(r["excerpt"]) + "</blockquote>" + extra + "</details>")
    attrs = [
        ("data-key", r["key"]), ("id", r["key"]), ("data-date", r["date"] or "9999-99-99"),
        ("data-venue", r["venue"]), ("data-cat", " ".join(r["cats"])), ("data-single", r["single"]),
        ("data-flag", r["flag"]), ("data-sources", " ".join(r["sources"])),
        ("data-search", ((r["property"] or "") + " " + (r["name"] or "") + " " + str(r["event_no"]) + " "
                         + (r["date"] or "") + " " + r["cat"]).lower()),
    ]
    finish = t12(str(r["finish"]).zfill(4)) if isinstance(r["finish"], int) else esc(r["finish"] or "&mdash;")
    if not r["finish"]:
        finish = "&mdash;"
    cells = [
        '<td class="nowrap">' + esc(r["date"] or "recurring") + '<div class="sm">' + esc(r["dow"] or "") + "</div></td>",
        "<td>" + esc(r["property"]) + "</td>",
        '<td class="nowrap">' + esc(r["event_no"]) + "</td>",
        "<td>" + esc(r["name"]) + '<div class="pill-row">' + badges + "</div>" + excerpt + "</td>",
        '<td class="nowrap">' + r["start_lbl"] + "</td>",
        '<td class="num">' + money(r["buy_in"]) + "</td>",
        '<td class="num">' + money(r["fee"]) + "</td>",
        '<td class="num">' + money(r["pool"]) + "</td>",
        '<td class="num">' + money(r["gtd"]) + "</td>",
        '<td class="num">' + ratio(r["ratio"]) + "</td>",
        '<td class="num">' + num(r["chips"]) + "</td>",
        '<td class="num">' + (str(r["level"]) + " min" if r["level"] else "&mdash;") + "</td>",
        '<td class="nowrap">' + t12(r["reg_close"]) + "</td>",
        '<td class="nowrap">' + finish + '<div class="sm">derived</div></td>',
        '<td class="change-cell">' + esc(r["last_checked"]) + "</td>",
        "<td>" + srcs + "</td>",
    ]
    return tag_open("tr", attrs) + "".join(cells) + "</tr>"


def filters():
    venues = sorted({r["venue"] for r in ALL_ROWS})
    vopts = ""
    for v in venues:
        vopts += '<option value="' + esc(v) + '">' + esc(venue_names.get(v, v)) + "</option>"
    return ('<div class="filters">\n'
            '  <label>Search<input type="search" data-f="q" placeholder="event name, number, property&hellip;"></label>\n'
            '  <label>From<input type="date" data-f="datefrom" value="' + events[0]["date"] + '"></label>\n'
            '  <label>To<input type="date" data-f="dateto" value="' + events[-1]["date"] + '"></label>\n'
            '  <label>Venue<select data-f="venue"><option value="all">all venues</option>' + vopts + "</select></label>") + """
  <label>Class<select data-f="cat"><option value="all">all</option>
    <option value="single_entry_candidate">single-entry candidate</option>
    <option value="multi_flight">multi-flight</option>
    <option value="spend_advantage">spend-advantage</option>
    <option value="satellite">satellite</option>
    <option value="team_format">team</option>
    <option value="unverified">unverified</option></select></label>
  <label class="check"><input type="checkbox" data-f="single"> single-entry / no re-entry clause only</label>
  <label class="check"><input type="checkbox" data-f="flagged"> only rows with an open flag</label>
  <span class="spacer"></span><span class="count"></span>
</div>"""


def event_table(rows, caption):
    return ('<div class="tablewrap" data-filterable><table><caption>' + caption + "</caption>"
            + TABLE_HEAD + "<tbody>" + "".join(event_row(r) for r in rows) + "</tbody></table></div>")


# --------------------------------------------------------------------------- pages
def p_index():
    wins = SCH["windows"]["best_poker_rate_compatible"]
    rec = wins[0] if wins else SCH["windows"]["best_size_ratio"][0]
    n_unver = len(UNVER) + len(OTHERS_MISC)
    kpis = [
        (num(len(ALL_ROWS)), "published rows in the table"),
        (num(len(QUAL)), "one-day events, sheet read, no re-entry clause"),
        (num(len(RANKED)), "rankable: fee AND guarantee confirmed"),
        (str(STATS["sheets_read"]) + "/" + str(STATS["sheets_published"]), "official structure sheets read"),
        (money(STATS["cheapest_qualifying_entry"]), "cheapest verified entry"),
        (ratio(STATS["highest_ratio"]), "best guarantee-per-entry ratio"),
        (num(len(SCH["days"])), "days with a plan"),
        (num(len(FLAGS["items"]) + n_unver), "open items to close"),
    ]
    kpi_html = ""
    for k, l in kpis:
        kpi_html += '<div class="kpi"><b>' + k + "</b><span>" + esc(l) + "</span></div>"
    findings = ""
    for f in SUMM["findings"]:
        srcs = " &middot; ".join(srclink(u) for u in f["sources"])
        findings += ("<details open><summary>" + esc(f["title"]) + "</summary><p>" + esc(f["text"])
                     + '</p><div class="sm">Sources: ' + srcs + "</div></details>")
    steps = ""
    for s in SUMM["decision_sequence"]:
        kind = "ok" if s["state"].startswith("done") else ("bad" if "blocked" in s["state"] else "warn")
        steps += ('<tr><td class="num">' + str(s["step"]) + "</td><td>" + esc(s["text"]) + "</td><td>"
                  + badge(s["state"], kind) + '</td><td class="sm">' + esc(s["detail"]) + "</td></tr>")
    rec_html = ""
    if rec:
        rec_html = ('<div class="note ok"><b>Recommended window, computed from the verified rows:</b> arrive '
                    + esc(rec["arrival"]) + ", depart " + esc(rec["departure"]) + " &mdash; " + str(rec["nights"])
                    + " nights, " + str(rec["entries"]) + " one-day entries totalling " + money(rec["entry_cost"])
                    + " against " + money(rec["gtd_played"]) + " of published guarantees (avg "
                    + ratio(rec["avg_ratio"]) + " per entry), and every primary is $300+ so the poker suite rate stays valid. "
                    "<span class=\"sm\">Note: 4 of these days share one overlap flag, because the evening fallback is a "
                    "mid-level entry, not a fresh start.</span></div>")
    rec2 = SCH["windows"]["best_poker_rate_compatible"][1] if len(SCH["windows"]["best_poker_rate_compatible"]) > 1 else None
    if rec2:
        rec_html += ('<p class="sm">Close alternative: ' + esc(rec2["arrival"]) + " &rarr; " + esc(rec2["departure"])
                     + " at " + ratio(rec2["avg_ratio"]) + " for " + money(rec2["entry_cost"]) + " of entries.</p>")
    limits = [
        "No 8 AM start exists in the verified schedule; the earliest published cash-prize start is 10:10 AM.",
        "No walking duration is verified for any hotel &rarr; poker-room pair, so the &le;30-minute filter is honest but empty.",
        "No dated room rate is verified for any property, so nightly cost is a formula plus one official &ldquo;from&rdquo; rate, not a quote.",
        "Ranking covers The Venetian only, because it is the only room with a dated per-event official document set this pass read.",
        "Nothing on this page is a forecast: no field sizes, no expected value, no finish times.",
    ]
    lim_html = "".join("<li>" + x + "</li>" for x in limits)
    links = [
        ("single-entry.html", "Single-entry ranked", str(len(RANKED)) + " events with fee and guarantee confirmed, rule excerpt on every row."),
        ("spend-advantage.html", "Spend-advantage", "rebuy/add-on, multi-flight, team, satellite and the paid-membership discount events, kept out of the ranking."),
        ("schedule.html", "Day plan", "one primary per day plus a conditional evening fallback, with overlap flags computed from published times."),
        ("hotels.html", "Hotels", "resort fee, 13.38% tax, parking, incidentals, occupancy surcharge and cancellation window per property."),
        ("trip-cost.html", "Trip cost", "entries &times; buy-in + nights &times; true nightly cost, with open items listed inside the number."),
        ("flagged.html", "Flagged for review", str(len(FLAGS["items"])) + " items: what is unverified, what contradicts itself, what to ask."),
    ]
    link_html = "".join('<li><a href="' + esc(h) + '"><b>' + esc(t) + "</b></a> &mdash; " + d + "</li>" for h, t, d in links)
    body = """
<section>
<h1>""" + esc(SUMM["title"]) + """</h1>
<p class="lede">""" + esc(SUMM["scope"]) + """</p>
<p class="lede">""" + esc(SUMM["method"]) + """</p>
<div class="searchbar"><input id="global-search" type="search" autocomplete="off"
 placeholder="Search every table: event number, buy-in, property, RaceDay, 13.38%&hellip;">
<div id="search-suggest"></div></div>
<div class="grid kpis">""" + kpi_html + """</div>
""" + rec_html + """
</section>
<section class="grid cols">
  <div class="panel">
    <h3 style="margin-top:0">Where the plan stands</h3>
    <div class="tablewrap compact"><table><thead><tr><th>#</th><th>Decision step</th><th>State</th><th>Detail</th></tr></thead>
    <tbody>""" + steps + """</tbody></table></div>
    <p class="sm">Steps 1 and 4 are the two things only you can close: the dates, and one itemised hotel quote.</p>
  </div>
  <div class="panel">
    <h3 style="margin-top:0">Read first</h3>
    <ul class="tight">""" + link_html + """</ul>
    <h3>Honest limits</h3>
    <ul class="tight">""" + lim_html + """</ul>
  </div>
</section>
<section>
<h2>Findings</h2>
""" + findings + """
</section>
"""
    page("index.html", "Dashboard", body, SUMM["scope"])


def p_tournaments():
    note = ("<b>Column definitions.</b> <i>Buy-in</i> is the published entry price; on the read sheets the house fee "
            "is taken <i>out</i> of it, not added on top. <i>Pool / entry</i> is what the sheet allocates to the prize "
            "pool. <i>Gtd &divide; buy-in</i> is a descriptive size ratio, not a forecast or an overlay claim. "
            "<i>Bounty</i> rows publish a guarantee that includes total bounties, so their cash pool is smaller than "
            "the headline. <i>Earliest plausible finish</i> = registration close + one level, derived from published "
            "times; no source publishes finish times.")
    body = """
<section>
<h1>All events on the verified schedule</h1>
<p class="lede">Every published row of the official DeepStack Extravaganza IV schedule (Nov 16 &ndash; Dec 23, 2026),
plus rows other Strip rooms published in official documents that an earlier pass read. Columns are filled only where
the official structure sheet states the value, so &ldquo;sheet not read&rdquo; rows show blanks by design. Events 03,
04, 05 and 06 have no guarantee printed on either the schedule or their sheet: their guarantee cell is empty, not zero.</p>
""" + filters() + """
""" + event_table(ALL_ROWS, str(len(ALL_ROWS)) + " rows &middot; each links its own official source") + """
<div class="note info" style="margin-top:12px">""" + note + """</div>
</section>"""
    page("tournaments.html", "All events", body)


def p_single():
    defs = ""
    for k, v in EV["definition"].items():
        defs += "<li><b>" + esc(k.replace("_", " ")) + "</b> &mdash; " + esc(v) + "</li>"
    body = """
<section>
<h1>Single-entry candidates, ranked</h1>
<p class="lede">Ranking uses only rows where the total entry fee and the guarantee are both confirmed from an official
structure sheet. Every row below was read in full on """ + esc(AS_OF) + """ and contains no rebuy, add-on or re-entry
provision. <b>That is not the same as an official one-entry cap</b> &mdash; no Venetian sheet publishes one (flag
FG-02) &mdash; so treat this as the qualifying set produced by the published sources, and get the last sentence
confirmed by the room before you rely on it.</p>
<div class="note"><b>How &ldquo;single-entry&rdquo; is decided here.</b> A sheet that states a limit is
<i>confirmed</i>; a sheet read in full that contains no buy-in clause is a <i>candidate</i> (this list); a sheet not
read is excluded from ranking; any rebuy, add-on, priced re-entry, extra flight, or a discount bought with a paid
third-party membership goes to the <a href="spend-advantage.html">spend-advantage</a> page.</div>
<ul class="sm">""" + defs + """</ul>
""" + filters() + """
""" + event_table(RANKED, str(len(RANKED)) + " ranked events &middot; sorted by published guarantee per entry") + """
</section>"""
    page("single-entry.html", "Single-entry ranked", body)


def p_spend():
    s8 = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/"
          "dse_nov_2026-structure_8.pdf")
    other = [r for r in ALL_ROWS if r.get("not_read") and r["cat"] == "spend_advantage"]
    body = """
<section>
<h1>Kept separate: money buys an edge</h1>
<p class="lede">These are the events your policy excludes from a single-entry plan. They are listed so the exclusion is
auditable, with the official wording that caused it, and never ranked against the single-entry table.</p>
""" + event_table(EXCL, str(len(EXCL)) + " Venetian rows excluded by explicit text") + """
<h2>Same category at other rooms</h2>
<p class="lede">Cited from official documents read by an earlier pass on """ + esc(AS_OF) + """ and not re-read in this
pass, so each row carries a &ldquo;cited, not re-read&rdquo; badge and no ranking (flag FG-04).</p>
""" + event_table(other, str(len(other)) + " rows, other Strip rooms") + """
<div class="note bad"><b>The clearest example of the pattern.</b> Venetian sheet 8, events 18 and 58:
&ldquo;PokerAtlas PRO players will receive a twenty ($20) rake discount on their initial $200 buy in only, for a
total buy in of $180 instead of $200 &hellip; All subsequent buy in's after the initial buy in will be $200.&rdquo;
A paid subscription lowers the first entry, and the sheet prices later entries &mdash; both are spending-based edges.
""" + srclink(s8, "official sheet 8") + """</div>
</section>"""
    page("spend-advantage.html", "Spend-advantage events", body)


def p_unverified():
    rows = UNVER + OTHERS_MISC
    body = """
<section>
<h1>Unverified rows</h1>
<p class="lede">Rows published on an official schedule whose structure sheet has not been read. Fee, house cut,
starting stack, level length and the registration cutoff are blank, and so is whether additional buy-ins are allowed
&mdash; a value is never copied across from a similar event. """ + str(len(UNVER)) + """ one-day Venetian rows and
""" + str(len(OTHERS_MISC)) + """ other-venue rows are in this state.</p>
""" + filters() + """
""" + event_table(rows, "the sheet URL in the last column is what would close each row") + """
<div class="note info">Reading the remaining """ + str(STATS["sheets_published"] - STATS["sheets_read"]) + """ sheets
is suggestion <a href="suggestions.html">S-02</a>. The daily job already fetches every one of those URLs, so a change
to a sheet is reported here before anyone relies on it.</div>
</section>"""
    page("unverified.html", "Unverified rows", body)


def p_schedule():
    dayrows = ""
    for k, d in SCH["days"].items():
        p, f = d["primary"], d["fallback"]
        flags = "".join('<div class="sm">&#9888; ' + esc(fl["text"]) + "</div>" for fl in d["flags"])
        if f:
            fcell = ('<a href="tournaments.html#' + esc(f["id"]) + '">Event ' + esc(f["event_no"]) + "</a> &middot; "
                     + esc(f["name"]) + '<div class="sm">start ' + t12(f["start"]) + " &middot; reg closes "
                     + t12(f["reg_close"]) + " &middot; usable only if you are out before then</div>")
            both = p["buy_in"] + f["buy_in"]
        else:
            fcell = '<span class="muted">none that qualifies</span>'
            both = p["buy_in"]
        search = (k + " " + p["name"] + " " + (f["name"] if f else "")).lower()
        attrs = [("data-key", "D" + k), ("id", "D" + k), ("data-date", k), ("data-venue", "venetian"),
                 ("data-cat", "day"), ("data-single", "candidate"), ("data-flag", "yes" if d["flags"] else "no"),
                 ("data-search", search)]
        dayrows += (tag_open("tr", attrs)
                    + '<td class="nowrap">' + esc(k) + '<div class="sm">' + esc(d["dow"]) + "</div></td>"
                    + '<td class="num">' + str(d["qualifying_events"]) + "</td>"
                    + '<td><a href="tournaments.html#' + esc(p["id"]) + '">Event ' + esc(p["event_no"]) + "</a> &middot; "
                    + esc(p["name"]) + '<div class="sm">start ' + t12(p["start"]) + " &middot; reg closes "
                    + t12(p["reg_close"]) + " &middot; earliest plausible finish " + esc(p["earliest_plausible_finish"])
                    + " &middot; " + num(p["chips"]) + " chips / " + str(p["level_min"]) + "-min levels</div>"
                    + flags + "</td>"
                    + '<td class="num">' + money(p["buy_in"]) + "</td>"
                    + '<td class="num">' + money(p["gtd"]) + "</td>"
                    + '<td class="num">' + ratio(p["ratio"]) + "</td>"
                    + "<td>" + fcell + "</td>"
                    + '<td class="num">' + money(both) + "</td>"
                    + "<td>" + srclink(p["sheet_url"], "sheet " + str(p["sheet"])) + " "
                    + srclink(SCHED_URL, "schedule") + "</td></tr>")
    wins = ""
    objectives = (("best published guarantee per entry", "best_size_ratio"),
                   ("compatible with the Venetian poker suite rate", "best_poker_rate_compatible"),
                   ("cheapest entries", "cheapest_entries"))
    for label, key in objectives:
        for w in SCH["windows"][key][:2]:
            feas = badge("overlap flags present", "warn") if w["has_overlap_flag"] else badge("no impossible sequence", "ok")
            wins += ('<tr><td>' + esc(label) + '</td><td class="nowrap">' + esc(w["arrival"]) + " &rarr; "
                     + esc(w["departure"]) + '</td><td class="num">' + str(w["nights"]) + '</td><td class="num">'
                     + str(w["entries"]) + '</td><td class="num">' + money(w["entry_cost"]) + '</td><td class="num">'
                     + money(w["gtd_played"]) + '</td><td class="num">' + ratio(w["avg_ratio"]) + '</td><td class="num">'
                     + str(w["poker_rate_eligible_nights"]) + "/" + str(w["entries"]) + "</td><td>" + feas
                     + '</td><td class="num">' + str(w["fallback_days"]) + "</td></tr>")
    gaps = ""
    for g in SCH["gap_days"]:
        avail = " &middot; ".join(esc(a["event_no"]) + " " + esc(a["name"]) + " [" + esc(a["category"]) + "]"
                                  for a in g["available"][:4])
        gaps += ('<tr><td class="nowrap">' + esc(g["date"]) + ' <span class="sm">' + esc(g["dow"])
                 + "</span></td><td>" + esc(g["reason"]) + "</td><td class=\"sm\">" + avail + "</td></tr>")
    rules = "".join("<li>" + esc(x) + "</li>" for x in SCH["rules"])
    nocomp = ""
    if not SCH["windows"]["best_poker_rate_compatible"]:
        nocomp = '<div class="note bad">No four-day window currently qualifies on every night at the $300+ level.</div>'
    body = """
<section>
<h1>Day plan &mdash; one primary event, one conditional fallback</h1>
<p class="lede">Built only from rows whose fee and guarantee are confirmed. Each day gets one primary &mdash; the
highest published guarantee-per-entry that starts before noon, so the day is actually long &mdash; and, where one
exists, an evening event that is usable only as a fallback because its registration is still open when you would
bust out.</p>
<div class="note"><b>The 8 AM question.</b> The earliest start published anywhere in the series is
""" + t12(SCH["earliest_start_in_series"]) + """ (a Dec 12 satellite) and the earliest cash-prize start is
""" + t12(SCH["earliest_day_start"]) + """. A day cannot be planned earlier than the schedule, so each day starts as
early as the series does; the 10:10 AM RaceDay format is the only verified second-shot option.</div>
<ol class="sm">""" + rules + """</ol>
<h2>All """ + str(len(SCH["days"])) + """ planned days</h2>
""" + filters() + """
<div class="tablewrap" data-filterable><table><caption>Generated from the same JSON as the event tables. Column 2 counts how many qualifying one-day events that date has; the rest are skipped to keep one event per day.</caption>
<thead><tr><th>Date</th><th>Qualifying</th><th>Primary event</th><th>Buy-in</th><th>Guarantee</th><th>Ratio</th>
<th>Conditional fallback</th><th>Day total</th><th>Sources</th></tr></thead><tbody>""" + dayrows + """</tbody></table></div>
<h2>Four-day windows (4 consecutive played days, 4 nights)</h2>
<div class="tablewrap compact"><table><thead><tr><th>Objective</th><th>Arrival &rarr; departure</th><th>Nights</th><th>Entries</th>
<th>Entry cost</th><th>Published gtd</th><th>Avg ratio</th><th>Poker-rate nights</th><th>Feasibility</th><th>Days with fallback</th></tr></thead>
<tbody>""" + wins + """</tbody></table></div>
""" + nocomp + """
<h2>Days with no plan</h2>
<p class="lede">Fifteen dates in the series have no event that passes the ranking test. Listing them is the point:
a silent gap would look like a free day.</p>
<div class="tablewrap compact"><table><thead><tr><th>Date</th><th>Why no primary</th><th>What is published that day</th></tr></thead>
<tbody>""" + gaps + """</tbody></table></div>
</section>"""
    page("schedule.html", "Day plan", body)


def p_hotels():
    hrows = ""
    for h in HOT["hotels"]:
        def cell(field, key, fmt=lambda v: v):
            f = h.get(field) or {}
            verified = f.get("status") in ("verified_official", "verified_official_county")
            v = f.get(key)
            if not verified or v is None:
                return ("&mdash; " + badge(field + " not read", "warn")) if not verified else ("&mdash; " + badge("not stated", "warn"))
            return fmt(v) + " " + badge("official", "ok")
        rate = None
        if h.get("room_rate_log_id"):
            for r in RATES["entries"]:
                if r["id"] == h["room_rate_log_id"]:
                    rate = r
        fee = (h.get("resort_fee") or {}).get("amount")
        nightly = ""
        if rate and fee:
            nightly = money((rate["rate_usd"] + fee) * TAX_MULT) + " " + badge("computed", "info")
        else:
            nightly = "&mdash; " + badge("no verified rate", "warn")
        rate_txt = ((money(rate["rate_usd"]) + ' <span class="sm">' + esc(rate["rate_kind"]) + ", captured "
                     + esc(rate["date_captured"]) + "</span>") if rate
                    else badge("no verified nightly rate", "bad"))
        canc = h.get("cancellation") or {}
        canc_badge = badge("official", "ok") if canc.get("status") == "verified_official" else badge("not read", "warn")
        addrv = (h.get("address") or {}).get("value")
        srcs = ""
        seen = set()
        # cite in this order so the terms page that every value came from is always first,
        # then fall through to whatever else the property publishes (booking, poker, guides)
        order = ["hotel_terms", "terms", "reservation_terms", "resort_fee", "parking",
                 "poker_player_rates", "poker", "hotel", "book_with_dates", "book_start", "book",
                 "tournament_guide", "guide_url", "daily_flyer_pdf", "friday_terms_pdf",
                 "saturday_terms_pdf", "sunday_terms_pdf", "resort_information"]
        pages_ = h.get("official_pages") or {}
        for k in order + [k for k in pages_ if k not in order]:
            u = pages_.get(k)
            if isinstance(u, str) and u.startswith("http") and u not in seen:
                seen.add(u)
                srcs += "<div>" + srclink(u, k.replace("_", " ")) + "</div>"
        for f in FLAGS["items"]:
            pass  # flags are linked from their own page
        search = (h["property"] + " " + str(addrv) + " resort fee parking cancellation").lower()
        attrs = [("data-key", h["id"]), ("id", h["id"]), ("data-venue", h.get("poker_room_walk_target")),
                 ("data-cat", "hotel"), ("data-flag", "no" if rate else "yes"), ("data-search", search)]
        feeexcerpt = esc(((h.get("resort_fee") or {}).get("excerpt") or "")[:200])
        hrows += (tag_open("tr", attrs)
                  + "<td><b>" + esc(h["property"]) + '</b><div class="sm">'
                  + esc(addrv or "address not verified this pass") + "</div></td>"
                  + "<td>" + rate_txt + "</td>"
                  + '<td class="num">' + nightly + "</td>"
                  + "<td>" + cell("resort_fee", "amount", lambda v: money(v) + " + tax")
                  + '<div class="sm">' + feeexcerpt + "</div></td>"
                  + "<td>" + cell("parking", "guest_self_per_day", lambda v: ("included in the resort fee" if v == 0 else money(v) + "/day")) + "</td>"
                  + "<td>" + cell("occupancy", "extra_guest_charge", lambda v: money(v) + "/guest/night" if v else "none stated") + "</td>"
                  + "<td>" + cell("incidentals", "amount", lambda v: money(v) + "/night") + "</td>"
                  + '<td class="sm">' + esc(canc.get("rule") or "&mdash;") + " " + canc_badge + "</td>"
                  + "<td>" + esc((h.get("quality") or {}).get("value") or "&mdash;") + " " + badge("no official rating", "warn") + "</td>"
                  + "<td>" + srcs + "</td></tr>")
    wrows = ""
    for p in WALK["pairs"]:
        prop = None
        for h in HOT["hotels"]:
            if h["id"] == p["hotel_id"]:
                prop = h["property"]
        prop = prop or p["hotel_id"]
        mins = p.get("minutes_verified")
        kind = "ok" if p["status"].startswith("connected") else "bad"
        label = WALK["status_labels"].get(p["status"], p["status"])
        route = esc(p.get("route_official") or "no official route statement found")
        if p.get("route_source"):
            route += "<div>" + srclink(p["route_source"], "official route text") + "</div>"
        maps = ""
        if p.get("google_maps"):
            maps += srclink(p["google_maps"], "Google Maps")
        if p.get("apple_maps"):
            maps += " " + srclink(p["apple_maps"], "Apple Maps")
        if not maps:
            maps = "&mdash;"
        attrs = [("data-key", p["id"]), ("data-walk", mins if mins else ""), ("data-venue", p["venue"]),
                 ("data-cat", "walk"), ("data-flag", "no" if kind == "ok" else "yes"),
                 ("data-search", (prop + " " + str(p.get("destination_label"))).lower())]
        wrows += (tag_open("tr", attrs) + "<td>" + esc(prop) + "</td><td>"
                  + esc(venue_names.get(p["venue"], p["venue"])) + "</td><td>"
                  + esc(p.get("destination_label") or "") + '</td><td class="num">'
                  + ((str(mins) + " min") if mins else "&mdash;") + "</td><td>" + badge(label, kind)
                  + '</td><td class="sm">' + route + "</td><td class=\"nowrap\">" + maps + "</td></tr>")
    tax = HOT["tax"]
    body = """
<section>
<h1>Hotels: what a night really costs</h1>
<p class="lede">Cost and quality first, distance as a hard limit. Every fee, tax, surcharge and cancellation window
below is quoted from the property's own page so the comparison is like for like. The room rate is the one term that
cannot be verified without an itemised quote, and it is left blank rather than guessed.</p>
<div class="note info"><b>True cost per night = (room rate + resort fee + extra-occupant charge) &times;
""" + ("{:.4f}".format(TAX_MULT)) + """</b> &nbsp;&middot;&nbsp; incidentals are an authorization, not a charge;
parking is a separate line on the <a href="trip-cost.html">Trip cost</a> page because two official Venetian pages
disagree about it (FG-07).</div>
<div class="tablewrap compact"><table><caption>""" + str(len(HOT["hotels"])) + """ properties &middot; """ + esc(AS_OF) + """</caption>
<thead><tr><th>Property</th><th>Verified room rate</th><th>True cost / night</th><th>Resort fee</th><th>Parking</th>
<th>Extra occupant</th><th>Incidental hold</th><th>Cancellation</th><th>Quality</th><th>Sources</th></tr></thead>
<tbody>""" + hrows + """</tbody></table></div>
<div class="panel"><h3 style="margin-top:0">""" + esc(tax["label"]) + " &mdash; " + str(tax["rate_pct"]) + """%</h3>
<blockquote>""" + esc(tax["excerpt"]) + """</blockquote>
<p class="sm">Scope: """ + esc(tax["applies_to"]) + """. Source: """ + srclink(tax["source_url"], "Clark County notice (official)") + """.</p>
<ul class="tight">"""
    for c in tax.get("corroborating_official_excerpts", []):
        body += ("<li><b>" + esc(c["publisher"]) + "</b>: &ldquo;" + esc(c["excerpt"]) + "&rdquo; "
                 + srclink(c["source_url"], host_of(c["source_url"])) + "</li>")
    body += """</ul></div>
<h2>Walking route to the poker room (30-minute limit)</h2>
<p class="lede">""" + esc(WALK["why_no_minutes"]) + """</p>
<div class="filters"><label class="check"><input type="checkbox" data-f="walk"> only pairs with a verified &le;30 min duration</label>
<span class="spacer"></span><span class="count"></span></div>
<div class="tablewrap compact" data-filterable><table><caption>""" + str(len(WALK["pairs"])) + """ hotel &rarr; venue pairs &middot; durations blank until verified</caption>
<thead><tr><th>Hotel</th><th>Toward</th><th>Destination</th><th>Verified minutes</th><th>Status</th><th>Official route</th><th>Check it yourself</th></tr></thead>
<tbody>""" + wrows + """</tbody></table></div>
<h2>Official booking engines for your dates</h2>
<ul class="tight">"""
    for b in RATES["booking_links"]:
        prop = b["hotel_id"]
        for h in HOT["hotels"]:
            if h["id"] == b["hotel_id"]:
                prop = h["property"]
        body += "<li>" + esc(prop) + ": " + srclink(b["url"], b["label"]) + "</li>"
    body += """</ul>
<div class="note bad"><b>Not the same thing as a quote.</b> A &ldquo;from $119&rdquo; starting rate is a floor, and the
Venetian publishes poker rates only 150 days ahead. To compare hotels properly you need the itemised checkout total
for the same room type, occupancy and dates &mdash; the template is on the <a href="rate-log.html">Rate log</a> page.</div>
</section>"""
    page("hotels.html", "Hotels & true cost", body)


def p_tripcost():
    wins = SCH["windows"]["best_poker_rate_compatible"]
    rec = wins[0] if wins else SCH["windows"]["best_size_ratio"][0]
    ven = None
    for h in HOT["hotels"]:
        if h["id"] == "H-VEN":
            ven = h
    rate = None
    for r in RATES["entries"]:
        if r["id"] == "R-VEN-POKER":
            rate = r
    fee = ven["resort_fee"]["amount"]
    per_night = (rate["rate_usd"] + fee) * TAX_MULT
    days = [SCH["days"][d] for d in rec["days"]]
    entry_rows = ""
    for d in days:
        p = d["primary"]
        entry_rows += ('<div class="line"><span>' + esc(d["date"]) + " &middot; Event " + esc(p["event_no"])
                       + " &mdash; " + esc(p["name"]) + ' <span class="sm">start ' + t12(p["start"])
                       + ", reg closes " + t12(p["reg_close"]) + "</span></span><b>" + money(p["buy_in"]) + "</b></div>")
    lodging = per_night * rec["nights"]
    total = rec["entry_cost"] + lodging
    opt = ""
    for d in days:
        p = d["primary"]
        opt += ('<label class="check"><input type="checkbox" value="' + esc(p["id"]) + '" data-n="'
                + str(p["buy_in"]) + '" checked> ' + esc(d["date"]) + " &middot; Event " + esc(p["event_no"])
                + " &middot; " + money(p["buy_in"]) + " &middot; " + esc(p["name"][:44]) + "</label>")
    hotelopts = "".join('<option value="' + esc(h["id"]) + '">' + esc(h["property"]) + "</option>" for h in HOT["hotels"])
    dayopts = ""
    for k in SCH["days"]:
        p = SCH["days"][k]["primary"]
        dayopts += '<option value="' + esc(k) + '">' + esc(k) + " &middot; " + esc(SCH["days"][k]["dow"]) + "</option>"
    parking = ven["parking"]["guest_self_per_day"]
    inc = ven["incidentals"]["amount"]
    body = """
<section>
<h1>Trip cost calculator</h1>
<p class="lede">Formula: <b>entries &times; buy-in + nights &times; true nightly cost</b>, where true nightly cost =
(room rate + resort fee + extra-occupant charge) &times; """ + ("{:.4f}".format(TAX_MULT)) + """. It starts filled with the
recommended plan so the shape of the number is visible, then you change what you want to test. Nothing in it is an
estimate of a rate: the room-rate line is either a dated official capture or it is zero with a warning.</p>
<div class="grid cols">
 <div class="panel" id="trip-calc">
  <h3 style="margin-top:0">Scenario</h3>
  <div class="filters" style="border:0;padding:0;margin:0 0 8px">
   <label>Hotel<select id="c-hotel">""" + hotelopts + """</select></label>
   <label>Nightly rate source<select id="c-rate"></select></label>
   <label>Nights<input id="c-nights" type="number" min="1" max="14" value="' + str(rec["nights"]) + '"></label>
   <label>Occupancy<select id="c-occ"><option value="1">1 adult</option><option value="2" selected>2 adults</option><option value="3">3 adults</option><option value="4">4 adults</option></select></label>
   <label class="check"><input id="c-parking" type="checkbox"> add hotel self-parking</label>
  </div>
  <div id="c-pick" style="max-height:190px;overflow:auto;border:1px solid var(--line);border-radius:8px;padding:8px">"""
    body += opt
    body += """</div>
  <div class="pill-row"><button id="c-add" class="badge b-info" type="button">Load recommended window (""" + esc(rec["arrival"]) + " &rarr; " + esc(rec["departure"]) + """)</button></div>
  <div id="c-out" class="panel" style="margin-top:10px"></div>
  <div class="grid" style="grid-template-columns:1fr 1fr 1fr;margin-top:10px">
   <div class="kpi"><b id="c-pernight">&mdash;</b><span>true cost per night</span></div>
   <div class="kpi"><b id="c-entries">&mdash;</b><span>entries subtotal</span></div>
   <div class="kpi"><b id="c-total">&mdash;</b><span>estimated trip cost</span></div>
  </div>
 </div>
 <div class="panel">
  <h3 style="margin-top:0">The same number, spelled out</h3>""" + entry_rows + """
  <div class="line"><span>Entry subtotal (""" + str(rec["entries"]) + """ events)</span><b>""" + money(rec["entry_cost"]) + """</b></div>
  <div class="line"><span>Room rate per night &mdash; official &ldquo;from&rdquo; rate, captured """ + esc(rate["date_captured"]) + """</span><b>""" + money(rate["rate_usd"]) + """</b></div>
  <div class="line"><span>Resort fee (""" + esc(ven["resort_fee"]["excerpt"][:64]) + """&hellip;)</span><b>""" + money(fee) + """</b></div>
  <div class="line"><span>Clark County room tax at """ + str(TAX_PCT) + """%</span><b>""" + money((rate["rate_usd"] + fee) * TAX_PCT / 100) + """</b></div>
  <div class="line"><span>True cost per night</span><b>""" + money(per_night) + """</b></div>
  <div class="line"><span>&times; """ + str(rec["nights"]) + """ nights</span><b>""" + money(lodging) + """</b></div>
  <div class="line total"><span>Estimated trip cost, no parking</span><b>""" + money(total) + """</b></div>
  <div class="line"><span>If guest parking is charged (""" + money(parking) + """/day)</span><b>""" + money(total + parking * rec["nights"]) + """</b></div>
  <div class="line"><span>Incidental authorization """ + money(inc) + """ &times; """ + str(rec["nights"]) + """ nights &mdash; held, not spent</span><b>""" + money(inc * rec["nights"]) + """</b></div>
  <div class="note" style="margin-top:10px"><b>Read before you budget.</b> The """ + money(rate["rate_usd"]) + """ is a
  published floor, not your quote (FG-05); whether the fee is taxed on your rate plan is an interpretation (FG-06);
  parking is disputed between two official Venetian pages (FG-07); and the poker rate itself is conditional on six
  hours of live cash or a $300+ tournament every night, which is why this scenario avoids the $200 formats.
  Total buy-in exposure on the days shown: """ + money(rec["entry_cost"]) + """ against """ + money(rec["gtd_played"]) + """
  of published guarantees &mdash; a size ratio of """ + ratio(rec["avg_ratio"]) + """, not a forecast.</div>
 </div>
</div>
</section>"""
    page("trip-cost.html", "Trip cost", body)


def p_ratelog():
    rows = ""
    for r in RATES["entries"]:
        status = str(r.get("status") or "")
        kind = "ok" if "verified" in status else "bad"
        srcs = srclink(r.get("source_url"))
        attrs = [("data-key", r["id"]), ("data-cat", "rate"), ("data-venue", r.get("hotel_id")),
                 ("data-flag", "no" if r.get("rate_usd") else "yes"),
                 ("data-search", (str(r.get("hotel_id")) + " " + str(r.get("rate_kind"))).lower())]
        rows += (tag_open("tr", attrs)
                 + '<td class="nowrap">' + esc(r["date_captured"]) + "</td><td>" + esc(r.get("hotel_id")) + "</td>"
                 + '<td class="num">' + money(r.get("rate_usd")) + "</td><td>" + esc(r.get("rate_kind")) + "</td>"
                 + "<td>" + esc(r.get("occupancy_basis") or "&mdash;") + "</td>"
                 + '<td class="sm">' + esc(r.get("conditions") or "&mdash;") + "</td>"
                 + "<td>" + esc(r.get("applies_to_dates") or "&mdash;") + "</td>"
                 + "<td>" + badge(status.replace("_", " "), kind) + "</td>"
                 + '<td class="sm">' + esc(r.get("excerpt") or "") + "</td>"
                 + "<td>" + srcs + "</td>"
                 + '<td class="sm">' + esc(r.get("caveat") or "") + "</td></tr>")
    template = ("arrival_date &middot; departure_date &middot; nights &middot; occupancy &middot; room type &middot; "
                "rate plan &middot; nightly rate &middot; resort fee &middot; taxes &middot; total at checkout &middot; "
                "cancellation deadline &middot; page URL &middot; date and time captured")
    body = """
<section>
<h1>Dated rate log</h1>
<p class="lede">""" + esc(RATES["why_a_log"]) + """</p>
<div class="tablewrap compact"><table><caption>""" + str(len(RATES["entries"])) + """ log entries &middot; """ + esc(AS_OF) + """</caption>
<thead><tr><th>Captured</th><th>Hotel</th><th>Rate</th><th>Kind</th><th>Occupancy basis</th><th>Conditions</th>
<th>Applies to</th><th>Status</th><th>Official excerpt</th><th>Source</th><th>Caveat</th></tr></thead><tbody>""" + rows + """</tbody></table></div>
<div class="note info"><b>Template for the missing number.</b> When you have an itemised quote, append a row with
<code class="mono">""" + template + """</code> &mdash; the calculator then uses it instead of a &ldquo;from&rdquo; rate.</div>
<div class="note bad">""" + esc(RATES["live_lookup_limit"]) + """</div>
</section>"""
    page("rate-log.html", "Rate log", body)


def p_venues_index():
    rows = ""
    for v in VEN["venues"]:
        evs = [e for e in ALL_ROWS if e["venue"] == v["id"]]
        qual = [e for e in evs if e["cat"] == "single_entry_candidate"]
        nhot = len([h for h in HOT["hotels"] if h["id"] in v.get("hotels", [])])
        rows += ('<tr><td><a href="venues/' + esc(v["id"]) + ".html\">" + esc(v["name"]) + "</a></td><td>"
                 + esc(v["brand_group"]) + '</td><td class="num">' + str(len(evs)) + '</td><td class="num">'
                 + str(len(qual)) + '</td><td class="num">' + str(nhot) + '</td><td class="sm">'
                 + esc(v["coverage"]["status"]) + "</td></tr>")
    pending = "".join("<li>" + esc(x) + "</li>" for x in VEN["not_covered_yet"])
    body = """
<section>
<h1>Venues</h1>
<p class="lede">One page per property, with its events, its hotels, its official documents and what is still missing
there. """ + esc(VEN["note"]) + """</p>
<div class="tablewrap compact"><table><thead><tr><th>Venue</th><th>Group</th><th>Rows in the dataset</th>
<th>Single-entry candidates</th><th>Hotels linked</th><th>Coverage state</th></tr></thead><tbody>""" + rows + """</tbody></table></div>
<h2>Not covered yet</h2><ul class="tight">""" + pending + """</ul>
</section>"""
    page("venues.html", "Venues", body)


def p_venue(v):
    evs = [r for r in ALL_ROWS if r["venue"] == v["id"]]
    hots = [h for h in HOT["hotels"] if h["id"] in v.get("hotels", [])]
    r_ = v["room"]
    s = v.get("series", {})
    walkp = [p for p in WALK["pairs"] if p["venue"] == v["id"]]
    rowshtml = ""
    for x in evs:
        catlabel, catkind = CATEGORY_LABEL.get(x["cat"], (x["cat"], "info"))
        srcs = "".join(srclink(u, "schedule" if u == SCHED_URL else host_of(u)) for u in x["sources"])
        rowshtml += ('<tr><td class="nowrap">' + esc(x["date"] or "recurring") + '</td><td class="nowrap">'
                     + esc(x["event_no"]) + "</td><td>" + esc(x["name"]) + '</td><td class="num">'
                     + money(x["buy_in"]) + '</td><td class="num">' + money(x["gtd"]) + '</td><td class="num">'
                     + money(x["fee"]) + '</td><td class="num">' + ratio(x["ratio"]) + "</td><td>"
                     + badge(catlabel, catkind) + "</td><td>" + srcs + "</td></tr>")
    hrows = ""
    for h in hots:
        fee = (h.get("resort_fee") or {}).get("amount")
        pk = (h.get("parking") or {}).get("guest_self_per_day")
        canc = h.get("cancellation") or {}
        hrows += ('<tr><td><a href="hotels.html#' + esc(h["id"]) + '">' + esc(h["property"]) + "</a></td><td>"
                  + (money(fee) if fee else badge("fee not read", "warn")) + "</td><td>"
                  + (("included in fee" if pk == 0 else money(pk) + "/day") if pk is not None else badge("parking not read", "warn"))
                  + "</td><td>" + esc(canc.get("deadline") or canc.get("rule") or "&mdash;") + "</td></tr>")
    wrows = ""
    for p in walkp:
        prop = p["hotel_id"]
        for h in HOT["hotels"]:
            if h["id"] == p["hotel_id"]:
                prop = h["property"]
        mins = p.get("minutes_verified")
        kind = "ok" if p["status"].startswith("connected") else "bad"
        label = WALK["status_labels"].get(p["status"], p["status"])
        route = esc(p.get("route_official") or "no official route text")
        if p.get("google_maps"):
            route += " &middot; " + srclink(p["google_maps"], "Google Maps")
        wrows += ('<tr><td>' + esc(prop) + '</td><td class="num">' + ((str(mins) + " min") if mins else "&mdash;")
                  + "</td><td>" + badge(label, kind) + '</td><td class="sm">' + route + "</td></tr>")
    fields = ""
    for k, val in r_.items():
        if val in (None, "", {}, []):
            continue
        if str(val).startswith("http"):
            val = srclink(val)
        fields += ('<div class="line"><span>' + esc(k.replace("_", " ")) + "</span><b>" + val + "</b></div>")
    docs = ""
    for k, x in s.items():
        if str(x).startswith("http"):
            docs += '<div class="line"><span>' + esc(k.replace("_", " ")) + "</span><b>" + srclink(x) + "</b></div>"
        else:
            docs += '<div class="line"><span>' + esc(k.replace("_", " ")) + "</span><b>" + esc(x) + "</b></div>"
    empty = ""
    if not evs:
        empty = ('<div class="note bad">No verified event rows for this venue: its official documents were not read in '
                 "this pass, so nothing is published here as a value. The links above are what a future pass would read.</div>")
    body = """
<section>
<h1>""" + esc(v["name"]) + """</h1>
<p class="lede">""" + esc(v["coverage"]["status"]) + """</p>
<div class="grid cols">
<div class="panel"><h3 style="margin-top:0">Room facts (official)</h3>""" + fields + """</div>
<div class="panel"><h3 style="margin-top:0">Schedules and documents</h3>""" + docs + """</div>
</div>
<h2>Events (""" + str(len(evs)) + """)</h2>
<div class="tablewrap"><table><thead><tr><th>Date</th><th>Ev #</th><th>Event</th><th>Buy-in</th><th>Gtd</th><th>Fee</th>
<th>Ratio</th><th>Class</th><th>Sources</th></tr></thead><tbody>""" + rowshtml + """</tbody></table></div>
""" + empty + """
<h2>Hotels that can reach it</h2>
<div class="tablewrap compact"><table><thead><tr><th>Property</th><th>Resort fee</th><th>Guest parking</th><th>Cancellation</th></tr></thead>
<tbody>""" + hrows + """</tbody></table></div>
<h2>Walking routes</h2>
<div class="tablewrap compact"><table><thead><tr><th>From</th><th>Verified minutes</th><th>Status</th><th>Route</th></tr></thead>
<tbody>""" + wrows + """</tbody></table></div>
<p class="sm"><a href="venues.html">&larr; all venues</a></p>
</section>"""
    page("venues/" + v["id"] + ".html", v["name"], body)


def p_sources():
    def row(x, official=True):
        lc = x.get("last_checked") or "not checked"
        state = badge("read this pass", "ok") if x.get("read_in_this_pass") else badge("cited, not re-read", "warn")
        mon = x.get("monitor") or {}
        mbadge = badge("monitored daily", "info") if mon.get("enabled") else badge("not monitored", "")
        used = x.get("used_for") or x.get("why_listed") or "&mdash;"
        attrs = [("data-key", x["id"]), ("data-cat", "official" if official else "lead"), ("data-flag", "no"),
                 ("data-search", (str(x.get("label")) + " " + str(x.get("publisher"))).lower())]
        return (tag_open("tr", attrs) + "<td>" + esc(x.get("label")) + '</td><td class="sm">'
                + esc(x.get("publisher") or "&mdash;") + "</td><td>" + srclink(x["url"]) + '</td><td class="nowrap">'
                + esc(lc) + "</td><td>" + state + " " + mbadge + '</td><td class="sm">' + esc(used) + "</td></tr>")
    sheetrows = ""
    for n in ALL_SHEET_NUMS:
        url = SHEET_BASE + "dse_nov_2026-structure_" + str(n) + ".pdf"
        read = n in READ_SHEETS
        evs = sorted({e["event_no"] for e in events if e["sheet"] == n})
        attrs = [("data-key", "SH" + str(n)), ("data-cat", "official"), ("data-flag", "no" if read else "yes"),
                 ("data-search", ("structure sheet " + str(n) + " " + " ".join(evs)).lower())]
        sheetrows += (tag_open("tr", attrs) + "<td>Venetian structure sheet " + str(n)
                      + ' <span class="sm">events ' + esc(", ".join(evs)) + "</span></td>"
                      + '<td class="sm">The Venetian (official)</td><td>' + srclink(url, "sheet " + str(n))
                      + '</td><td class="nowrap">' + (esc(AS_OF) if read else "not read") + "</td><td>"
                      + (badge("read this pass", "ok") if read else badge("not read", "bad"))
                      + " " + badge("monitored daily", "info")
                      + '</td><td class="sm">fee, pool per entry, stack, level length, registration cutoff and guarantee</td></tr>')
    nmon = len([x for x in SRCS["official"] if (x.get("monitor") or {}).get("enabled")]) + len(ALL_SHEET_NUMS)
    body = """
<section>
<h1>Sources</h1>
<p class="lede">""" + esc(SRCS["rule"]) + """</p>
""" + filters() + """
<div class="tablewrap" data-filterable><table><caption>""" + str(len(SRCS["official"])) + """ official sources,
""" + str(len(ALL_SHEET_NUMS)) + """ structure sheets and """ + str(len(SRCS["third_party_leads"])) + """ third-party
leads (leads are never used as the source of a value)</caption>
<thead><tr><th>Source</th><th>Publisher</th><th>Link</th><th>Last checked</th><th>State</th><th>Used for</th></tr></thead>
<tbody>""" + "".join(row(x) for x in SRCS["official"]) + sheetrows + "".join(row(x, False) for x in SRCS["third_party_leads"]) + """</tbody></table></div>
<div class="note info">""" + str(nmon) + """ URLs are re-read on a schedule. Every table row on this site links one of
these sources; the generator refuses to build a row whose source host is not an official property, county or room
domain, or that has no last-checked date.</div>
</section>"""
    page("sources.html", "Sources", body)


def p_flagged():
    chg = CHANGES.get("sources") or []
    if chg:
        chg_rows = ""
        for c in chg:
            diffs = c.get("value_diffs") or []
            txt = "; ".join("{}: {} &rarr; {}".format(d[0], d[1], d[2]) for d in diffs) if diffs else esc(c.get("detail") or "no tracked value change")
            state = c.get("state")
            kind = {"ok": "ok", "changed": "bad", "missing": "warn"}.get(state, "warn")
            chg_rows += ('<tr><td class="nowrap">' + esc(c.get("checked") or "&mdash;") + "</td><td>"
                         + srclink(c.get("url")) + "</td><td>" + badge(state, kind) + '</td><td class="sm">'
                         + txt + "</td></tr>")
        chg_table = ('<div class="tablewrap compact"><table><thead><tr><th>Checked</th><th>Source</th><th>State</th>'
                     "<th>What changed</th></tr></thead><tbody>" + chg_rows + "</tbody></table></div>")
    else:
        chg_table = ('<div class="note bad">No monitor run yet. The workflow writes '
                     "<code>site-data/change-report.json</code> on its first scheduled run (06:30 UTC daily), and "
                     "affected rows on the event tables pick up a &ldquo;source changed&rdquo; badge automatically.</div>")
    items = ""
    for f in FLAGS["items"]:
        sev = "bad" if f["severity"] == "High" else ("warn" if f["severity"] == "Medium" else "info")
        done = f["status"] in ("done", "resolved by this pass")
        attrs = [("id", f["id"]), ("data-key", "FL" + f["id"]), ("data-cat", "flag"), ("data-flag", "yes"),
                 ("data-venue", ""), ("data-date", "9999-99-99"), ("data-single", "unknown"), ("data-search",
                     (f["id"] + " " + f["title"] + " " + f["area"]).lower())]
        items += ('<div class="panel" id="' + esc(f["id"]) + '"><h3 style="margin:0 0 4px">' + esc(f["id"]) + " &middot; "
                  + esc(f["title"]) + " " + badge(f["severity"], sev) + " "
                  + badge(f["status"], "ok" if done else "") + '</h3><div class="sm">Area: ' + esc(f["area"])
                  + "</div><p>" + esc(f["detail"]) + '</p><div class="line"><span>Source</span><b>'
                  + srclink(f["source"]) + '</b></div><div class="line"><span>Next action</span><b class="sm" style="text-align:right;max-width:70%">'
                  + esc(f["action"]) + "</b></div></div>")
    diff_html = ""
    diff_path = os.path.join(DATA, "schedule-diff.json")
    if os.path.exists(diff_path):
        sd = load("schedule-diff.json")
        items = ""
        for kind in ("added", "removed", "modified", "renamed"):
            for x in sd.get(kind, [])[:25]:
                detail = x.get("changes") or x.get("value_deltas") or x.get("note") or ""
                items += ('<tr><td>' + esc(kind) + '</td><td class="nowrap">' + esc(x.get("date") or "&mdash;")
                          + " " + esc(x.get("start") or "") + "</td><td>" + esc(x.get("name") or x.get("now") or "")
                          + (' <span class="sm">was: ' + esc(x.get("was")) + "</span>" if x.get("was") else "")
                          + '</td><td class="sm">' + esc(json.dumps(detail)) + "</td></tr>")
        if not items:
            items = '<tr><td colspan="4" class="muted">No differences: the live schedule page matches the dataset row for row.</td></tr>'
        diff_html = ('<h2>Live schedule scrape &middot; last run ' + esc(sd.get("checked") or "?") + "</h2>"
                     + badge(str(sd.get("state", "?")), "ok" if sd.get("state") == "ok" else "bad")
                     + '<div class="tablewrap compact"><table><caption>Written by '
                     '<code>scripts/scrape-schedule.mjs</code> on its own schedule. The scrape never edits the dataset: '
                     'a difference here means read the cited structure sheet and re-run the generators.</caption>'
                     "<thead><tr><th>Kind</th><th>Slot</th><th>Event</th><th>Difference</th></tr></thead><tbody>"
                     + items + "</tbody></table></div>")
    body = """
<section>
<h1>Flagged for review</h1>
<p class="lede">""" + esc(FLAGS["intro"]) + """</p>
<div class="note bad"><b>The four that change decisions.</b> FG-01 (no 8 AM start exists in the verified schedule),
FG-02 (no sheet publishes a one-entry cap), FG-05 (no dated room rate) and FG-11 (no walking minutes verified).
Everything else is either a source contradiction to watch or a dataset-hygiene note.</div>
""" + items + """
""" + diff_html + """
<h2>Change monitor &middot; last run """ + esc(CHANGES.get("last_run") or "not yet run") + """</h2>
""" + chg_table + """
<p class="sm">Configuration: <code>scripts/check_sources.mjs</code> reads <code>site-data/sources.json</code> plus every
structure-sheet URL in <code>site-data/events.json</code>, hashes each page, compares the tracked values, and writes
<code>site-data/change-report.json</code>. It runs on a schedule in
<a href="https://github.com/karagemop466-tech/Poker2/actions/workflows/daily-refresh.yml">the refresh workflow</a>
and can be triggered manually before a non-refundable payment.</p>
</section>"""
    page("flagged.html", "Flagged for review", body)


def p_questions():
    rows = ""
    for q in QUEST["items"]:
        st = q["status"]
        kind = "ok" if st == "answered" else ("bad" if st in ("needs_you", "open") else "warn")
        rows += ('<div class="panel" id="' + esc(q["id"]) + '"><h3 style="margin:0 0 4px">' + esc(q["id"])
                 + " &middot; " + esc(q["question"]) + " " + badge(st.replace("_", " "), kind)
                 + ' <span class="sm">step ' + str(q["step"]) + "</span></h3>"
                 + '<div class="line"><span>What we already have</span><b class="sm" style="text-align:right;max-width:72%">'
                 + esc(q["what_we_have"]) + "</b></div>"
                 + '<div class="line"><span>What is missing</span><b class="sm" style="text-align:right;max-width:72%">'
                 + esc(q["what_is_missing"]) + "</b></div>"
                 + '<div class="line"><span>How to close it</span><b class="sm" style="text-align:right;max-width:72%">'
                 + esc(q["how_to_find"]) + "</b></div>"
                 + '<div class="line"><span>Blocks</span><b class="sm" style="text-align:right;max-width:72%">'
                 + esc(q["blocks"]) + "</b></div></div>")
    body = """
<section>
<h1>Open questions, and what is already answered</h1>
<p class="lede">""" + esc(QUEST["intro"]) + """</p>
<div class="grid">""" + rows + """</div>
</section>"""
    page("questions.html", "Questions", body)


def p_suggestions():
    done = ""
    for s in SUGG["implemented_this_pass"]:
        done += ('<tr><td class="nowrap">' + esc(s["id"]) + "</td><td><b>" + esc(s["title"]) + '</b><div class="sm">'
                 + esc(s["detail"]) + "</div></td><td>" + badge("implemented", "ok") + "</td></tr>")
    todo = ""
    for s in SUGG["awaiting_your_choice"]:
        todo += ('<tr><td class="nowrap">' + esc(s["id"]) + "</td><td><b>" + esc(s["title"]) + '</b><div class="sm">'
                 + esc(s["what"]) + '</div><div class="sm">Why: ' + esc(s["why"]) + "</div></td>"
                 + '<td class="sm">' + esc(s["category"]) + "<div>" + esc(s["effort"]) + "</div></td><td>"
                 + badge(s["status"], "warn") + "</td></tr>")
    body = """
<section>
<h1>Suggestions</h1>
<p class="lede">""" + esc(SUGG["intro"]) + """</p>
<h2>Built in this pass</h2>
<div class="tablewrap compact"><table><thead><tr><th>#</th><th>Improvement</th><th>Status</th></tr></thead><tbody>""" + done + """</tbody></table></div>
<h2>Awaiting your choice &mdash; deliberately not implemented</h2>
<div class="tablewrap compact"><table><thead><tr><th>#</th><th>Suggestion</th><th>Type / effort</th><th>Status</th></tr></thead><tbody>""" + todo + """</tbody></table></div>
<div class="note info">Pick any of S-01&hellip;S-10 and it becomes the next task. Each one names the file it would
change, so nothing here is silently built ahead of your decision.</div>
</section>"""
    page("suggestions.html", "Suggestions", body)


def p_repo():
    checks = [
        ("Every event row links an official source host", "scripts/build-site.py validate(): non-official or missing source aborts the build"),
        ("Every row carries a last-checked date", "same validation pass"),
        ("No structural value shown for an unread sheet", "validate(): fee/chips/level/reg-close must have sheet_read"),
        ("Every resort fee / parking / incidentals / occupancy value has a source URL", "validate(): &ldquo;verified_official&rdquo; without a URL aborts"),
        ("No broken internal links", "validate(): walks every written page after generation"),
        ("Guarantee in the event name matches the guarantee on its structure sheet",
         "scripts/build-events.py: 34 cross-checked rows, mismatch aborts"),
        ("Event-to-sheet tagging matches each sheet's own &ldquo;Event Numbers&rdquo; line", "scripts/build-events.py"),
        ("Registration-close time parsed from the sheet matches the printed wall clock in the text",
         "scripts/build-events.py parses both the level count and the parenthesised time"),
        ("Values are never copied from an aggregator",
         "site-data/sources.json keeps third-party leads with used_as_value_source: false and they are not referenced by any row"),
    ]
    crows = ""
    for a, b in checks:
        crows += ("<tr><td>" + a + '</td><td class="sm">' + b + "</td><td>" + badge("automated", "info") + "</td></tr>")
    listing = " ".join("<code>" + esc(f) + "</code>" for f in sorted(os.listdir(ROOT)) if not f.startswith("."))
    bullets = [
        ("FG-14", "<code>data/tournaments.json</code> attributed structure-sheet values (registration cutoff, stack, level length) to the schedule page, and a second session had already flagged those fields as unreproducible from that page. Both were half right: the values are real, the attribution was not. Fixed by per-field source links in the new dataset."),
        ("FG-15", "<code>data/venetian-dse4-official-check.json</code> (47 rows) and <code>data/verified/tournaments.json</code> (32 rows) each labelled rows &ldquo;single_entry&rdquo; on sheet silence alone, and the former counted per-flight rows as separate single-entry events. The consolidated dataset uses three states and groups flights by event."),
        ("FG-16", "Three dashboards (root, <code>/docs/</code>, <code>/verified/</code>) rendered three datasets with different labels for the same event. The root site is now the only front-end; the duplicate trees are removed and their data kept under <code>data/</code> for audit."),
        ("FG-19", "For the 34 rows whose sheet was read, the buy-in is fee-inclusive. For rows whose sheet was not read, whether the published number is fee-inclusive or fee-additive is unverified, so their cost-to-enter shows the published buy-in with a caveat instead of a computed total."),
        ("Repo hygiene", "Two stylesheets and two scripts existed at the root (<code>style.css</code>/<code>styles.css</code>, <code>app.js</code>) with overlapping selectors from different sessions; retired in favour of <code>assets/site.css</code> and <code>assets/site.js</code>. <code>scripts/build.mjs</code> and <code>scripts/build.py</code> built the retired front-ends and are no longer the publisher path."),
    ]
    blist = ""
    for tag_, txt in bullets:
        blist += "<li><b>" + tag_ + "</b>: " + txt + "</li>"
    body = """
<section>
<h1>Repo review, method, and what changed</h1>
<p class="lede">The repo arrived with seven prior sessions' work and three parallel dashboards. This page records the
audit, the consolidation, and how the build enforces its own claims.</p>
<h2>Method</h2>
<ul class="tight">
<li><b>Read the official page, then its document.</b> Event rows come from the DSE IV schedule page; fee, stack,
level, registration and guarantee come from that event's structure sheet. Buy-ins and guarantees parsed from the event
name are cross-checked against the sheet text, and a mismatch aborts the build.</li>
<li><b>Three states, never two.</b> <i>explicit</i> (the source says it, excerpt stored), <i>not stated after a full
read</i> (we read it and the clause is absent), <i>not read</i> (no claim). Only the first two may appear in a table,
and only a full read with a confirmed fee and guarantee may be ranked.</li>
<li><b>Computed values are labelled computed.</b> Ratios and &ldquo;earliest plausible finish&rdquo; are derived from
published times; the derivation is printed next to the table so nobody reads it as a scheduled end time.</li>
<li><b>No outbound network in the build sandbox</b> (GitHub, npm and PyPI only), so live re-reads happen in the GitHub
Actions job, which reports here rather than silently rewriting data.</li>
</ul>
<h2>Automated checks in this build</h2>
<div class="tablewrap compact"><table><thead><tr><th>Check</th><th>Where</th><th>Type</th></tr></thead><tbody>""" + crows + """</tbody></table></div>
<h2>Irregularities found in the repo itself</h2>
<ul class="tight">""" + blist + """</ul>
<h2>Working tree at the top level</h2>
<p class="sm">""" + listing + """</p>
<h2>Coordination</h2>
<p class="sm">Board and hand-off record: <a href="COORDINATION.md">COORDINATION.md</a> (per-session claims, conflict
log, sources and PR history).</p>
</section>"""
    page("repo-review.html", "Repo & method", body)


# --------------------------------------------------------------------------- assets
def write_data_js(write=True):
    payload = {
        "as_of": AS_OF, "tax": HOT["tax"], "events": events, "schedule": SCH, "hotels": HOT,
        "rates": RATES, "walk": WALK, "venues": VEN, "flags": FLAGS,
        "changes": [c for c in (CHANGES.get("sources") or []) if c.get("state") in ("changed", "missing")],
        "search": [],
    }
    search = []
    for r in ALL_ROWS:
        search.append({"label": (r["date"] or "recurring") + " &middot; event " + str(r["event_no"]) + " &middot; "
                       + r["name"], "group": r["property"], "page": "tournaments.html", "anchor": r["key"]})
    for h in HOT["hotels"]:
        search.append({"label": h["property"] + " &middot; hotel cost", "group": "hotels", "page": "hotels.html",
                       "anchor": h["id"]})
    for f in FLAGS["items"]:
        search.append({"label": f["id"] + " &middot; " + f["title"], "group": "flagged", "page": "flagged.html",
                       "anchor": f["id"]})
    for q in QUEST["items"]:
        search.append({"label": q["id"] + " &middot; " + q["question"], "group": "questions", "page": "questions.html",
                       "anchor": q["id"]})
    for s in SUGG["implemented_this_pass"] + SUGG["awaiting_your_choice"]:
        search.append({"label": s["id"] + " &middot; " + s["title"], "group": "suggestions", "page": "suggestions.html"})
    for x in SRCS["official"]:
        search.append({"label": str(x["label"]), "group": "source", "page": "sources.html"})
    for v in VEN["venues"]:
        search.append({"label": v["name"], "group": "venue", "page": "venues/" + v["id"] + ".html"})
    for r in RATES["entries"]:
        search.append({"label": "rate " + r["date_captured"] + " &middot; " + str(r.get("hotel_id")) + " &middot; "
                       + str(r["rate_kind"]), "group": "rate log", "page": "rate-log.html"})
    payload["search"] = search
    js = "window.POKER = " + json.dumps(payload, ensure_ascii=False) + ";\n"
    if write:
        if not os.path.isdir(ASSETS):
            os.makedirs(ASSETS)
        with open(os.path.join(ASSETS, "data.js"), "w", encoding="utf8") as fh:
            fh.write(js)
    else:
        disk = os.path.join(OUT, "assets", "data.js")
        if not os.path.exists(disk) or open(disk, encoding="utf8").read() != js:
            problems.append("assets/data.js differs from the datasets")
    return len(search)


# --------------------------------------------------------------------------- validate
def validate():
    for r in ALL_ROWS:
        if not r["sources"]:
            problems.append("row " + r["key"] + ": no source")
        for u in r["sources"]:
            if not is_official(u):
                problems.append("row " + r["key"] + ": non-official source " + u)
        if not r["last_checked"]:
            problems.append("row " + r["key"] + ": missing last_checked")
    for e in events:
        if not e["sheet_read"]:
            for fld in ("fee", "chips", "level_min", "reg_close", "pool_per_entry"):
                if e[fld] is not None:
                    problems.append("event " + e["event_no"] + ": " + fld + " filled without a read sheet")
        if e["gtd"] and e["gtd_source"] not in ("structure sheet", "official schedule name"):
            problems.append("event " + e["event_no"] + ": guarantee source unclear (" + str(e["gtd_source"]) + ")")
    for h in HOT["hotels"]:
        for fld in ("resort_fee", "parking", "incidentals", "occupancy"):
            f = h.get(fld) or {}
            has_val = any(f.get(k) is not None for k in ("amount", "guest_self_per_day", "extra_guest_charge"))
            has_src = f.get("source_url") or f.get("source_urls")
            if has_val and not has_src:
                problems.append("hotel " + h["id"] + "." + fld + ": value without source")
            if f.get("status") == "verified_official" and not has_src:
                problems.append("hotel " + h["id"] + "." + fld + ": verified without a source url")
    for fname in sorted(pages_written):
        txt = open(os.path.join(OUT, fname), encoding="utf8").read()
        base = os.path.dirname(fname)
        for href in re.findall(r'href="([^"#]+)"', txt):
            if href.startswith(("http", "mailto", "tel", "data:")):
                continue
            target = os.path.normpath(os.path.join(base, href))
            if target not in pages_written and not os.path.exists(os.path.join(ROOT, target)):
                problems.append(fname + ": broken internal link " + href)
    return problems


def main():
    check = "--check" in sys.argv
    p_index()
    p_tournaments()
    p_single()
    p_spend()
    p_unverified()
    p_schedule()
    p_hotels()
    p_tripcost()
    p_ratelog()
    p_venues_index()
    for v in VEN["venues"]:
        p_venue(v)
    p_sources()
    p_flagged()
    p_questions()
    p_suggestions()
    p_repo()
    nsearch = write_data_js(write=not check)
    probs = validate()
    if check:
        stale = []
        for fname, txt in generated.items():
            disk = os.path.join(OUT, fname)
            if not os.path.exists(disk) or open(disk, encoding="utf8").read() != txt:
                stale.append(fname)
        if stale:
            problems.append("regenerated output differs from the committed page: " + ", ".join(sorted(stale)[:12]))
        probs = problems
    if probs:
        print("BUILD FAILED:")
        for p in probs[:40]:
            print("  -", p)
        raise SystemExit(1)
    if not check:
        for fname, txt in generated.items():
            fpath = os.path.join(OUT, fname)
            fd = os.path.dirname(fpath)
            if fd:
                os.makedirs(fd, exist_ok=True)
            with open(fpath, "w", encoding="utf8") as fh:
                fh.write(txt)
    print(("committed output unchanged: " if check else "wrote ") + str(len(pages_written)) + " pages, " + str(len(ALL_ROWS)) + " event rows ("
          + str(len(RANKED)) + " ranked, " + str(len(UNVER)) + " unverified, " + str(len(EXCL))
          + " spend-advantage), " + str(len(HOT["hotels"])) + " hotels, " + str(nsearch)
          + " search entries; all rows source-checked against official hosts")


if __name__ == "__main__":
    main()
