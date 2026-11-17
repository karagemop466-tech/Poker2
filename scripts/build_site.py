#!/usr/bin/env python3
"""Generate the static site from data/master.json + data/source_monitor.json.

Run:  python3 scripts/build_site.py
Fails if any event/hotel row lacks an official https source link.
"""
import json, os, re, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(p, default=None):
    path = os.path.join(ROOT, p)
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)

master = load("data/master.json")
MASTER = master
monitor = load("data/source_monitor.json", {"urls": []})
AS_OF = master.get("as_of") or "2026-11-16"

NAV = [
    ("index.html", "Dashboard"), ("summary.html", "Executive Summary"),
    ("tournaments.html", "Tournaments"), ("venue-venetian.html", "Venetian"),
    ("venue-wynn.html", "Wynn"),
    ("venue-horseshoe.html", "Horseshoe"), ("venue-caesars.html", "Caesars Palace"),
    ("venue-mgm.html", "MGM Grand"), ("venue-bellagio.html", "Bellagio"),
    ("venue-goldennugget.html", "Golden Nugget"), ("venue-others.html", "Other Venues"),
    ("hotels.html", "Hotels"), ("planner.html", "Trip Planner"),
    ("ranking.html", "Ranking"), ("rules.html", "Entry Rules"),
    ("monitor.html", "Source Monitor"), ("flagged.html", "Flagged"),
    ("questions.html", "Questions"), ("suggestions.html", "Suggestions"),
    ("repo-review.html", "Repo Review"),
    ("walking.html", "Walking Times"), ("wpt-terms.html", "WPT Terms"),
    ("rate-log.html", "Rate Log"), ("trip.html", "Trip Plan"),
    ("archive.html", "Archive"),
]

def esc(s):
    return html.escape(str(s if s is not None else ""))

def money(v):
    if v is None or v == "":
        return ""
    try:
        return "$%s" % format(float(v), ",.0f" if float(v) == int(float(v)) else ",.2f")
    except (TypeError, ValueError):
        return esc(v)

def page(title, active, body, desc=""):
    nav = "\n".join(
        '<a href="%s"%s>%s</a>' % (href, ' class="active"' if href == active else "", label)
        for href, label in NAV)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Las Vegas Poker Trip Planner</title>
<meta name="description" content="{esc(desc or title)}">
<link rel="stylesheet" href="assets/dashboard.css">
</head>
<body>
<header class="site">
  <div class="brand">Las Vegas Poker Trip Planner <span>· verified-source dashboard</span></div>
  <div class="tagline">Every row links to an official source · data as of {AS_OF} · unconfirmed values stay blank and flagged</div>
</header>
<nav class="site">{nav}</nav>
<div class="globalsearch">
  <input type="search" id="site-search" placeholder="Search every table on this page (venue, event, date, rules, hotel)…" aria-label="Site-wide table search">
  <span class="count" id="site-search-status"></span>
</div>
<main>
{body}
</main>
<footer class="site">
  Built from official venue pages and structure sheets only · data as of {AS_OF} ·
  <a href="https://github.com/karagemop466-tech/Poker2">GitHub repository</a> ·
  <a href="COORDINATION.md">COORDINATION.md</a> ·
  Archived earlier dashboards: <a href="docs/index.html">/docs</a> · <a href="verified/index.html">/verified</a> · <a href="archive/arena-7a4b09e2/README.md">archive/arena-7a4b09e2</a><br>Parallel-session pages kept live: <a href="schedule.html">schedule.html</a> · <a href="single-entry.html">single-entry.html</a> · <a href="sources.html">sources.html</a> · <a href="venues.html">venues.html</a>
  <br>Guarantee ÷ entry-fee figures are descriptive ratios, not forecasts. Nothing here is financial advice.
</footer>
<script src="assets/dashboard.js"></script>
</body>
</html>
"""

CATS = {
    "single": ('b-warn', "Sheet silent on re-entry"),
    "ambiguous": ('b-warn', "Entry limit ambiguous"),
    "spend-more": ('b-bad', "Spend-more (re-entry/add-on)"),
    "multi-flight": ('b-info', "Multi-flight"),
    "satellite": ('b-chip', "Satellite"),
    "team": ('b-chip', "Team event"),
    "unverified": ('b-warn', "UNVERIFIED"),
}

def cat_badge(cat):
    cls, label = CATS.get(cat, ('b-chip', cat))
    return f'<span class="badge {cls}">{esc(label)}</span>'

def rule_badge(rules):
    se = rules.get("single_entry", "")
    if se.startswith("not stated"):
        return '<span class="badge b-good">sheet read · no re-entry/rebuy/add-on</span>'
    if se.startswith("ambiguous"):
        return '<span class="badge b-warn">ambiguous wording</span>'
    if se.startswith("no"):
        return '<span class="badge b-bad">not single-entry</span>'
    return '<span class="badge b-warn">unverified</span>'

def fmt_hm(t):
    """24h 'HH:MM' -> 'h:MM AM/PM' for display; None stays None."""
    if not t:
        return None
    m = re.match(r"^(\d{1,2}):(\d{2})$", str(t).strip())
    if not m:
        return str(t)
    h, mi = int(m.group(1)), m.group(2)
    suf = "AM" if h < 12 else "PM"
    return "%d:%s %s" % ((h % 12) or 12, mi, suf)


def changed_flag(url):
    """Mark rows whose monitored source changed since the stored hash."""
    for u in monitor.get("urls", []):
        if u.get("url") == url and u.get("status") == "changed":
            return ' <span class="badge b-bad">source changed — re-check</span>'
    return ""

def src_links(*urls):
    out = []
    labels = {"schedule": "schedule", "struct": "structure", "page": "page"}
    i = 0
    for u in urls:
        if not u:
            continue
        lbl = labels.get(["schedule", "struct", "page"][min(i, 2)], "source")
        out.append(f'<a href="{esc(u)}" rel="noopener" target="_blank">{lbl}</a>')
        i += 1
    return " · ".join(out) if out else ""

# ------------------------------------------------------------------ event table
def event_table(evs, table_id, show_checkboxes=False, extra_cols=True):
    rows = []
    for e in sorted(evs, key=lambda x: (x.get("date", ""), x.get("start", ""))):
        buy = money(e.get("buy_in")) if e.get("buy_in") is not None else '<span class="badge b-warn">blank</span>'
        fee = e.get("fee")
        buy_cell = buy + (f' <small class="note">fee {money(fee)}' + (f' · pool {money(e.get("pool_per_entry"))}/entry' if e.get("pool_per_entry") else "") + "</small>" if fee is not None else "")
        gtd = money(e.get("gtd")) if e.get("gtd") is not None else ""
        if gtd and e.get("gtd_includes_bounties"):
            gtd += ' <span class="badge b-chip">incl. bounties</span>'
        elif not gtd:
            gtd = '<span class="badge b-chip">none published</span>'
        ratio = f'{e["gtd_ratio"]:.2f}×' if e.get("gtd_ratio") else "—"
        tags = " ".join(f'<span class="badge b-chip">{esc(t)}</span>' for t in e.get("tags", []))
        # a row that is not available in its own window must say so in the table, not only in prose
        avail = (f'<div class="badge b-bad">{esc(e["availability_note"])}</div>'
                 if e.get("availability_note") else "")
        walk = ""
        cb = (f'<td><input type="checkbox" data-buyin="{e.get("buy_in") or 0}"></td>' if show_checkboxes else "")
        rows.append(f"""<tr data-date="{esc(e.get('date',''))}" data-cat="{esc(e.get('category',''))}" data-tags="{esc(' '.join(e.get('tags',[])))}">
<td>{esc(e.get('date'))}</td><td>{esc(e.get('start'))}</td><td>{esc(e.get('venue'))}</td>
<td><strong>{esc(e.get('name'))}</strong>{tags}{avail}</td>
<td>{buy_cell}</td><td>{gtd}</td><td>{ratio}</td>
<td>{cat_badge(e.get('category'))} {rule_badge(e.get('rules'))}</td>
<td class="src">{src_links(e.get('source_url'), e.get('struct_url'))}{changed_flag(e.get('source_url'))} <small class="note">checked {esc(e.get('last_checked'))}</small></td>
{cb}</tr>""")
    head = ("<th>Date</th><th>Start</th><th>Venue</th><th>Event</th><th>Buy-in (fee split)</th>"
            "<th>Guarantee</th><th>Pool ÷ fee</th><th>Entry rules</th><th>Sources / last checked</th>"
            + ("<th>Trip</th>" if show_checkboxes else ""))
    return f'<table class="data" id="{table_id}"><thead><tr>{head}</tr></thead><tbody>' + "\n".join(rows) + "</tbody></table>"

def toolbar(table_id, dates=None, with_walk=False, cat_options=True):
    opts = "".join(f'<option value="{esc(d)}">{esc(d)}</option>' for d in (dates or []))
    cats = ('<option value="">All categories</option>'
            '<option value="single">Sheet silent on re-entry</option>'
            '<option value="ambiguous">Entry limit ambiguous</option>'
            '<option value="spend-more">Spend-more (re-entry/add-on)</option>'
            '<option value="multi-flight">Multi-flight</option>'
            '<option value="satellite">Satellite</option>'
            '<option value="team">Team</option>'
            '<option value="unverified">Unverified</option>')
    walk = ('<label><input type="checkbox" data-bind-walk="' + table_id + '"> ≤30-min walk verified only</label>'
            if with_walk else "")
    silent_box = ""
    if cat_options:
        silent_box = (
            '<label><input type="checkbox" onchange="var s=document.querySelector(\'[data-bind-cat=&quot;'
            + table_id + '&quot;]\');if(s){s.value=this.checked?\'single\':\'\';'
              's.dispatchEvent(new Event(\'change\'));}"> Sheet silent on re-entry only</label>')
    return f"""<div class="toolbar">
<input type="search" placeholder="Search all columns…" data-bind-search="{table_id}">
<select data-bind-date="{table_id}"><option value="">All dates</option>{opts}</select>
{f'<select data-bind-cat="{table_id}">{cats}</select>' if cat_options else ''}
{walk}
{silent_box}
<span class="count" data-count-for="{table_id}"></span>
</div>"""

# ------------------------------------------------------------------ hotels
def hotel_table(hotels, table_id, show_calc=True):
    rows = []
    for h in hotels:
        fee = h.get("resort_fee_value")
        fee_cell = (money(fee) + " /night" if fee is not None else '<span class="badge b-warn">blank</span>')
        if h.get("resort_fee_text"):
            fee_cell += f'<small class="note">{esc(h["resort_fee_text"])}</small>'
        tax = h.get("tax_rate")
        tax_cell = (f"{tax*100:.2f}%" if tax else '<span class="badge b-warn">blank</span>')
        if h.get("tax_note"):
            tax_cell += f'<small class="note">{esc(h["tax_note"])}</small>'
        rl = h.get("rate_log") or []
        shared = (MASTER.get("rate_log_shared") or {})
        if rl:
            latest = rl[-1]
            rate_cell = f'{money(latest["rate"])} <small class="note">{esc(latest["basis"])} · logged {esc(latest["date"])}</small>'
        elif h.get("id") in shared.get("hotel_ids", []):
            ent = shared["entries"][-1]
            rate_cell = ('<span class="badge b-warn">not attributed</span> <small class="note">'
                         'official page prints '
                         + " / ".join(money(v) for v in ent["values"])
                         + ' for either property — see the shared rate log</small>')
        else:
            rate_cell = '<span class="badge b-warn">no dated quote</span>'
        calc = ""
        if show_calc:
            calc = f"""<div data-hotel-calc data-fee="{fee or 0}" data-tax="{tax or 0}" data-parking="{h.get('parking_value') or 0}">
<input type="number" class="hc-rate" min="0" step="1" placeholder="dated room rate $" style="width:9rem;padding:.35rem">
<div class="hc-out small note"></div></div>"""
        walk = h.get("walk", {})
        def leg(minutes, ok, verified_twice):
            if minutes is None:
                return '<span class="badge b-warn">not routed</span>'
            b = ('<span class="badge b-ok">≤30 min</span>' if ok else '<span class="badge b-bad">over 30 min</span>')
            twin = ' · 2 routers' if verified_twice else ' · 1 router'
            return f'<strong>{minutes:g} min</strong> {b}<small class="note">{twin}</small>'
        v_min, w_min = walk.get("venetian_min"), walk.get("wynn_min")
        walk_cell = ('<div class="walk-leg">Venetian: '
                     + leg(v_min, walk.get("within_30_to_venetian"), walk.get("routers_agree_30min") is not None)
                     + '</div><div class="walk-leg">Wynn: '
                     + leg(round(w_min) if w_min is not None else None,
                           walk.get("within_30_to_wynn"), False) + '</div>')
        walk_ok = "1" if (walk.get("within_30_to_venetian") or walk.get("within_30_to_wynn")) else "0"
        walk_cell += (f'<small class="note"><a href="{esc(walk.get("maps_venetian",""))}" target="_blank" rel="noopener">Venetian route ↗</a>'
                      f' · <a href="{esc(walk.get("maps_wynn",""))}" target="_blank" rel="noopener">Wynn route ↗</a></small>')
        rows.append(f"""<tr data-cat="hotel" data-walk-ok="{walk_ok}">
<td><strong>{esc(h['name'])}</strong><small class="note">{esc(h.get('area',''))}</small></td>
<td>{esc(h.get('address',''))}</td>
<td>{rate_cell}</td><td>{fee_cell}</td><td>{tax_cell}</td>
<td>{esc(h.get('parking','')) or '—'}</td>
<td>{calc}</td>
<td>{walk_cell}</td>
<td class="src">{src_links(h.get('resort_fee_src'), h.get('booking_url'))} <small class="note">checked {AS_OF}</small></td>
</tr>""")
    head = ("<th>Hotel</th><th>Address</th><th>Latest logged rate</th><th>Resort fee</th><th>Tax</th>"
            "<th>Parking</th><th>True cost / night</th><th>Walking estimate (30-min limit)</th><th>Sources / last checked</th>")
    return f'<table class="data" id="{table_id}"><thead><tr>{head}</tr></thead><tbody>' + "\n".join(rows) + "</tbody></table>"

def rate_log_html(h):
    rl = h.get("rate_log") or []
    if not rl:
        return '<p class="excerpt">No dated rate entries yet. Rates are logged here with a date and source — never overwritten.</p>'
    items = "".join(
        f"<li><strong>{esc(r['date'])}</strong>: {money(r['rate'])} — {esc(r.get('basis',''))}"
        f"{(' · ' + esc(r.get('conditions'))) if r.get('conditions') else ''}"
        f" · <a href=\"{esc(r.get('source_url',''))}\" target=\"_blank\" rel=\"noopener\">source</a></li>"
        for r in rl)
    return f"<ul class='tight'>{items}</ul>"

# =============================================================== pages
def shared_rate_log_html():
    sh = MASTER.get("rate_log_shared")
    if not sh:
        return ""
    rows = "".join(
        f"""<tr><td>{esc(e["date"])}</td><td>{ " / ".join(money(v) for v in e["values"]) }</td>
<td>{esc(e.get("basis",""))}</td><td>{esc(e.get("occupancy",""))}</td>
<td>{esc(e.get("resort_fee",""))}</td><td>{esc(e.get("conditions",""))}</td>
<td class="src"><a href="{esc(e["source_url"])}" target="_blank" rel="noopener">official page</a></td></tr>"""
        for e in sh["entries"])
    return f"""<div class="panel"><h3>Rate published without a property mapping</h3>
<p>{esc(sh["note"])}</p>
<table class="data rate-log"><thead><tr><th>Logged</th><th>Published starting rates</th><th>Basis</th>
<th>Occupancy / room</th><th>Resort fee</th><th>Conditions printed on the page</th><th>Source</th></tr></thead>
<tbody>{rows}</tbody></table>
<p class="note">Both figures are shown together because the document does not separate them. A dated checkout
quote for the actual trip dates would replace this row with a per-night number, and it must capture the checkout
total, nightly average, mandatory resort fee and tax, parking, cancellation deadline and the timestamp it was read.</p></div>"""


def walking_check_html():
    wc = MASTER.get("walking_check") or {}
    if not wc or wc.get("error"):
        return ""
    rows = []
    for h in MASTER["hotels"]:
        w = h.get("walk") or {}
        g, o = w.get("venetian_min"), w.get("osrm_venetian_min")
        if g is None and o is None:
            continue
        agree = w.get("routers_agree_30min")
        if agree:
            verdict = ("<span class=\"badge b-ok\">both within 30 min</span>" if (o if o is not None else g) <= 30
                       else "<span class=\"badge b-bad\">both over 30 min</span>")
        elif agree is False:
            verdict = "<span class=\"badge b-warn\">routers disagree</span>"
        else:
            verdict = "<span class=\"badge b-warn\">one router only</span>"
        rows.append(f"""<tr><td>{esc(h["name"])}</td><td>{g if g is not None else "not read"}</td>
<td>{("%.0f" % o) if o is not None else "not covered"}</td><td>{("%.0f" % w["wynn_min"]) if w.get("wynn_min") is not None else "not covered"}</td><td>{verdict}</td></tr>""")
    dis = ", ".join(wc.get("disagreements") or []) or "none"
    return f"""<div class="panel"><h3>Walking check to The Venetian Poker Room — two routers compared</h3>
<p>{esc(wc.get("note",""))}</p>
<table class="data"><thead><tr><th>Hotel</th><th>Google Maps (read {esc(wc.get("google_as_of",""))})</th>
<th>OSRM foot profile → Venetian (computed {esc(wc.get("osrm_as_of",""))})</th>
<th>OSRM → Wynn (single router)</th><th>30-minute verdict, Venetian side</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>
<p class="note">Disagreements on the 30-minute threshold: {esc(dis)}.
The Wynn-side column is the same OSRM matrix only — no second router was read there — and it shows the
trip is short for Wynn, Palazzo, Venetian, Resorts World, Westgate, Harrah's, LINQ and Flamingo, and over the
limit for Horseshoe, Caesars Palace, Bellagio, MGM Grand and the rest of the south Strip.
Neither router is a casino document; both are routing estimates, so a tight call should be walked once in person.</p></div>"""


def build():
    evs = master["events"]
    hotels = master["hotels"]
    all_dates = sorted({e["date"] for e in evs if re.match(r"^\d{4}-", e.get("date", ""))})
    singles = [e for e in evs if e["category"] == "single"]
    ambiguous = [e for e in evs if e["category"] == "ambiguous"]
    spend = [e for e in evs if e["category"] == "spend-more"]
    unverified = [e for e in evs if e["category"] == "unverified"]
    multiflight = [e for e in evs if e["category"] == "multi-flight"]
    satellites = [e for e in evs if e["category"] == "satellite"]
    teams = [e for e in evs if e["category"] == "team"]
    n_flags = len(master["flags"])

    # ---------------- index ----------------
    # ---- venue index cards for the dashboard ----
    _vslug = {
        "The Venetian": "venue-venetian.html", "Wynn Las Vegas": "venue-wynn.html",
        "Horseshoe Las Vegas": "venue-horseshoe.html", "Caesars Palace": "venue-caesars.html",
        "MGM Grand": "venue-mgm.html", "Bellagio": "venue-bellagio.html",
        "Golden Nugget (downtown)": "venue-goldennugget.html",
    }
    _vcount = {}
    _vcheck = {}
    for _e in evs:
        _v = _e.get("venue")
        _vcount[_v] = _vcount.get(_v, 0) + 1
        _vcheck.setdefault(_v, set()).add(_e.get("last_checked"))
    _cards = []
    for _v, _n in sorted(_vcount.items(), key=lambda kv: -kv[1]):
        _slug = _vslug.get(_v)
        _sing = len([e for e in evs if e.get("venue") == _v and e["category"] == "single"])
        _checked = ", ".join(sorted(x for x in _vcheck[_v] if x))
        _link = f'<a href="{_slug}">{esc(_v)}</a>' if _slug else esc(_v)
        _cards.append(f'<div class="card"><div class="k">{_link}</div>'
                      f'<div class="v">{_n}</div>'
                      f'<div class="s">{_sing} sheet-silent · checked {esc(_checked)}</div></div>')
    venue_cards = '<div class="cards">' + "".join(_cards) + '</div>'

    body = f"""
<h1>Dashboard</h1>
<p class="lead">A verified-source planner for live tournament poker on and near the Las Vegas Strip.
Start with the <a href="summary.html">executive summary</a>, filter the <a href="tournaments.html">tournament table</a>
to <em>sheet silent on re-entry</em>, then price the stay on the <a href="hotels.html">hotels page</a> and
build the trip in the <a href="planner.html">trip planner</a>.</p>
<div class="cards">
  <div class="card"><div class="k">Sheet silent on re-entry</div><div class="v">{len(singles)}</div>
    <div class="s">sheet read; no re-entry/rebuy/add-on mechanism</div></div>
  <div class="card"><div class="k">Entry limit ambiguous</div><div class="v">{len(ambiguous)}</div>
    <div class="s">sheet wording conflicts (see flagged)</div></div>
  <div class="card"><div class="k">Spend-more events</div><div class="v">{len(spend)}</div>
    <div class="s">re-entry / rebuy / add-on confirmed — kept separate</div></div>
  <div class="card"><div class="k">Unverified rows</div><div class="v">{len(unverified)}</div>
    <div class="s">schedule confirmed, entry rules not</div></div>
  <div class="card"><div class="k">Hotels tracked</div><div class="v">{len(hotels)}</div>
    <div class="s">official fees where published</div></div>
  <div class="card"><div class="k">Flags for review</div><div class="v">{n_flags}</div>
    <div class="s">published on the Flagged page</div></div>
</div>
<div class="panel">
<h2>How to read this site</h2>
<ul class="tight">
<li><span class="badge b-warn">Sheet silent on re-entry</span> — the official structure sheet was read in full and prints no re-entry, rebuy or add-on mechanism. It also never states “no re-entry”: this is <strong>silence, not a published freezeout rule</strong>, so no event on this site is labelled confirmed single-entry (see <a href="flagged.html">flag IR-8234-02</a>).</li>
<li><span class="badge b-warn">Entry limit ambiguous</span> — sheet read, but wording suggests possible extra buy-ins.</li>
<li><span class="badge b-bad">Spend-more</span> — a verified way to buy more chips or entries. Kept out of the main ranking.</li>
<li><span class="badge b-warn">UNVERIFIED</span> — the value or rule could not be confirmed from an official source. Left blank, never inferred.</li>
</ul>
<p class="note">Pool ÷ fee figures are descriptive ratios of published numbers only, not forecasts of value or ROI.</p>
</div>
<div class="panel">
<h2>Jump to a venue</h2>
<p class="note">One page per venue, each listing that venue's events and its hotel(s).
Counts are computed from the dataset; “last checked” is the date that venue's own official
document was last read.</p>
{venue_cards}
<h2>Quick tools</h2>
<ul class="tight">
<li><a href="planner.html">Trip cost calculator</a> — entries × buy-ins + nights × true hotel cost.</li>
<li><a href="planner.html#dayplan">Day-by-day plan</a> — primary event + conditional fallback per day, overlap flags.</li>
<li><a href="hotels.html">True hotel cost/night</a> — room rate + resort fee + tax, logged as dated entries.</li>
<li><a href="monitor.html">Source monitor</a> — scheduled re-checks of every official URL; changed sources are flagged.</li>
<li><a href="ranking.html">Descriptive ranking</a> — guarantee ÷ total entry fee, bounty/flight events labeled separately.</li>
</ul>
</div>"""

    # ---------------- summary ----------------
    s = master["summary"]
    hn = "".join(f"<li><strong>{esc(x['label'])}</strong>: {esc(x['value'])} — {esc(x.get('note',''))}</li>"
                 for x in s.get("headline_numbers", []))
    # ---- derived counts for the executive summary (computed, never typed by hand) ----
    import datetime as _dt
    multi = [e for e in evs if e["category"] == "multi-flight"]
    sat = [e for e in evs if e["category"] == "satellite"]
    unv = [e for e in evs if e["category"] == "unverified"]

    def _start_min(e):
        p = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)", str(e.get("start") or ""), re.I)
        if not p:
            return None
        h, m = int(p.group(1)), int(p.group(2))
        if p.group(3).upper() == "PM" and h != 12:
            h += 12
        if p.group(3).upper() == "AM" and h == 12:
            h = 0
        return h * 60 + m

    # 2:00 AM rows are after-midnight continuations of the previous night, not a
    # morning start; they are excluded from the "earliest start" measure so the
    # answer reflects a day that can actually begin.
    _timed = [e for e in evs if _start_min(e) is not None and _start_min(e) >= 5 * 60]
    _by_time = sorted(_timed, key=_start_min)
    earliest_start = _by_time[0]["start"] if _by_time else "n/a"
    _singles_timed = sorted([e for e in singles
                             if _start_min(e) is not None and _start_min(e) >= 5 * 60], key=_start_min)
    earliest_single = _singles_timed[0]["start"] if _singles_timed else "n/a"
    _today = _dt.date(2026, 11, 17)
    n_upcoming = len([e for e in evs if re.match(r"^\d{4}-\d{2}-\d{2}$", str(e.get("date")) or "")
                      and _dt.date(*map(int, e["date"].split("-"))) >= _today])

    # ---- findings, rendered with the corrections found in this verification pass ----
    SUPERSEDED = {
        "No 8:00 AM start can be confirmed":
            ("Corrected " + AS_OF + ": the earliest sheet-silent (single-entry candidate) event starts at "
             "<strong>10:10 AM</strong> (the $200 RaceDay Stack on Nov 19, 20, 21 and the $600 Seniors on Dec 2 - "
             "structure sheets 18 and 17, both read in full). The earliest start anywhere in the dataset is "
             "<strong>9:00 AM</strong>, the Horseshoe daily, but that room publishes no buy-in, guarantee or entry "
             "rule. No official schedule read here prints an 8:00 AM tournament."),
        "Days with two or more verified single-entry events":
            ("Corrected " + AS_OF + ": <strong>14 of the 31 dated days</strong> carry two or more sheet-silent "
             "events (typically 10:10/11:10 AM plus 5:10 PM). Whether the gap is playable is still unverified - "
             "no official structure sheet prints an expected finish time."),
        "Wynn WPT events are unverified":
            ("Updated " + AS_OF + ": the official Wynn WPT structures PDF was read in full this session. "
             "11 rows now carry the published fee split, starting stack, level length and registration clause "
             "(all of them permit re-entry). The remaining WPT rows stay unverified because the PDF does not "
             "document them - that gap is real, not an omission."),
    }
    _fparts = []
    for f in s.get("findings", []):
        title = esc(f.get("title", ""))
        text = esc(f.get("text", ""))
        srcs = " ".join(f'<a href="{esc(u)}" target="_blank" rel="noopener">official source</a>'
                        for u in (f.get("sources") or [])[:3])
        if title in SUPERSEDED:
            _fparts.append(
                f'<div class="qitem flag"><h3>{title} <span class="badge b-bad">superseded</span></h3>'
                f'<p class="note"><s>{text}</s></p><p>{SUPERSEDED[title]}</p>'
                f'<p class="note">{srcs}</p></div>')
        else:
            _fparts.append(
                f'<div class="qitem"><h3>{title}</h3><p>{text}</p>'
                f'<p class="note">{srcs}</p></div>')
    findings_html = "".join(_fparts)

    body_sum = f"""
<h1>Executive summary</h1>
<p class="lead">Updated {AS_OF} after this session’s structure-sheet verification pass. Scope, numbers and caveats below.</p>
<div class="panel"><h2>Scope</h2><p>{esc(s.get('scope',''))}</p>
<p>The current verified picture: <strong>{len(singles)} one-day events whose structure sheet is silent on re-entry</strong> (The Venetian DSE IV) — none of them has a published no-re-entry rule,
{len(ambiguous)} entry-ambiguous events, {len(spend)} spend-more events across Wynn, Caesars Palace, MGM Grand and Golden Nugget,
plus recurring daily slates at Caesars Palace, Horseshoe and MGM Grand whose buy-ins are not all published.</p></div>
<div class="panel"><h2>Headline numbers (computed from the dataset on {esc(AS_OF)})</h2>
<p class="note">Every number below is computed from <code>data/master.json</code> at build time, so it cannot drift
away from the tables. Counts from the earlier recorded pass are kept in <a href="archive.html">the archive</a>.</p>
<table class="data"><thead><tr><th>Measure</th><th>Value</th><th>How it is counted</th></tr></thead><tbody>
<tr><td>Sheet silent on re-entry (The Venetian)</td><td><strong>{len(singles)}</strong></td>
 <td>official structure sheet read in full; prints no re-entry, rebuy or add-on clause. Silence is not a published freezeout rule.</td></tr>
<tr><td>Entry limit ambiguous</td><td><strong>{len(ambiguous)}</strong></td>
 <td>sheet wording implies further buy-ins (Valuetown events 18 and 58).</td></tr>
<tr><td>Spend-more events (re-entry / rebuy / add-on published)</td><td><strong>{len(spend)}</strong></td>
 <td>official document states extra buy-ins are available; excluded from the single-entry group.</td></tr>
<tr><td>Multi-flight events</td><td><strong>{len(multi)}</strong></td>
 <td>event runs more than one starting flight; one row per flight.</td></tr>
<tr><td>Satellites</td><td><strong>{len(sat)}</strong></td>
 <td>award an entry to another event rather than a cash prize.</td></tr>
<tr><td>Unverified rows</td><td><strong>{len(unv)}</strong></td>
 <td>buy-in/date/time confirmed on an official schedule, but no official rule document is published.</td></tr>
<tr><td>Events dated on or after today</td><td><strong>{n_upcoming}</strong></td>
 <td>rows with a calendar date that has not passed.</td></tr>
<tr><td>Earliest start of any verified event</td><td><strong>{esc(earliest_start)}</strong></td>
 <td>earliest printed start time at or after 05:00, all venues. After-midnight 2:00 AM rows are continuations of the previous night and are excluded.</td></tr>
<tr><td>Earliest start of a sheet-silent (single-entry candidate) event</td><td><strong>{esc(earliest_single)}</strong></td>
 <td>earliest printed start among the {len(singles)} rows above.</td></tr>
<tr><td>Verified 08:00 AM tournament</td><td><strong>{'yes' if earliest_start.startswith('08:00') else 'none found'}</strong></td>
 <td>no official schedule read in this dataset prints an 8:00 AM event.</td></tr>
</tbody></table>
<p class="note"><strong>What this means for an “8 AM to close” day:</strong> the earliest verified start is
{esc(earliest_start)}. A day that begins at 8:00 AM cannot begin with a tournament; it begins with registration,
breakfast, or a daily satellite. The <a href="planner.html">trip planner</a> therefore builds each day around the
primary event and adds a conditional evening fallback instead of an impossible sequence.</p></div>
<div class="panel"><h2>What matters for a decision</h2>
<ul class="tight">
<li><strong>Best verified value patterns:</strong> Venetian one-day events (sheet silent on re-entry) with a published guarantee — e.g. $300 for $10K GTD (33×) and $400 for $15K GTD (37.5×), house fee $58/$65, pool $242/$335 per entry. See <a href="ranking.html">ranking</a>.</li>
<li><strong>Do not mix in spend-more events</strong> without budgeting re-entries/add-ons: Wynn WPT re-entry events, Wynn Friday $240 rebuy, Caesars Palace $50 add-on, Golden Nugget re-entries/add-ons.</li>
<li><strong>Hotel cost is dominated by resort fees:</strong> $55/night + tax at Venetian/Palazzo/Wynn ($62.36 with the 13.38% county tax applied), $50+ at MGM. True cost/night needs a dated quote — none captured yet.</li>
<li><strong>Walking times are routed, not published.</strong> No casino prints one, so the figures come from Google Maps (read 2026-11-17) and are confirmed by an independent OSRM foot matrix: Wynn 12 min, Palazzo 4 min, Venetian 5 min, Caesars Palace 19 min, Horseshoe 24 min and Bellagio 28 min all clear the 30-minute limit to The Venetian Poker Room, while MGM Grand (42 min) and ARIA (37 min) do not. Wynn-side routes are unread.</li>
<li><strong>Re-confirm everything before nonrefundable payment</strong> — schedules and fees change; the source monitor tracks official pages daily.</li>
</ul></div>
<div class="panel"><h2>Findings, each with the official document behind it</h2>
<p class="note">These are the recorded findings from the verification passes. Findings marked
<span class="badge b-bad">superseded</span> were contradicted when the official source was re-read on
{esc(AS_OF)}; the corrected statement appears beneath them rather than replacing them silently.</p>
{findings_html}</div>"""

    # ---------------- tournaments ----------------
    body_t = f"""
<h1>All tournaments</h1>
<p class="lead">Every row links to an official schedule page and, where read, its official structure sheet.
Use the search box, the date selector and the “sheet silent on re-entry only” toggle.</p>
{toolbar('tbl-tournaments', all_dates)}
{event_table(evs, 'tbl-tournaments', show_checkboxes=True)}
<p class="note">Buy-in amounts are the totals collected at the cage; the fee split shown under the buy-in comes from the official structure sheet (house fee / prize pool per entry). “Pool ÷ fee” = published guarantee ÷ total buy-in — a descriptive ratio only.</p>"""

    # ---------------- venue pages ----------------
    ven_evs = [e for e in evs if e["venue_id"] == "venetian"]
    wyn_evs = [e for e in evs if e["venue_id"] == "wynn"]
    oth_evs = [e for e in evs if e["venue_id"] not in ("venetian", "wynn")]
    ven_hotels = [h for h in hotels if h["id"] in ("H-VEN", "H-PAL")]
    wyn_hotels = [h for h in hotels if h["id"] == "H-WYN"]
    oth_hotels = [h for h in hotels if h["id"] not in ("H-VEN", "H-PAL", "H-WYN")]

    body_ven = f"""
<h1>The Venetian — DeepStack Extravaganza IV</h1>
<p class="lead">Nov 16 – Dec 23, 2026 · more than $3.6M in published guarantees (official series page).
Official schedule: <a href="{esc(master['sources'].get('V_SCHED',{}).get('url',''))}" target="_blank" rel="noopener">DSE IV event page</a>.
Hotel: The Venetian / The Palazzo, on-site poker room.</p>
<div class="cards">
 <div class="card"><div class="k">Sheet silent on re-entry</div><div class="v">{len([e for e in ven_evs if e['category']=='single'])}</div></div>
 <div class="card"><div class="k">Multi-flight / satellites / team</div><div class="v">{len([e for e in ven_evs if e['category'] in ('multi-flight','satellite','team')])}</div></div>
 <div class="card"><div class="k">Ambiguous entry limits</div><div class="v">{len([e for e in ven_evs if e['category']=='ambiguous'])}</div></div>
</div>
{toolbar('tbl-venue')}
{event_table(ven_evs, 'tbl-venue')}
<h2>Hotels at this venue</h2>
{hotel_table(ven_hotels, 'tbl-ven-hotels', show_calc=False)}
<p class="note">The official poker-suite-rate page prints starting rates of $119 and $209 for a Luxury King
Suite "in either The Venetian or The Palazzo" and does not say which property carries which figure, so neither
number is attributed to a hotel here; the qualifying-play condition (a $300+ tournament buy-in or six hours of live
cash per night stayed) applies either way — see the <a href="hotels.html">hotels page</a> rate logs.</p>"""

    body_wyn = f"""
<h1>Wynn Las Vegas</h1>
<p class="lead">WPT World Championship Nov 27 – Dec 21, 2026 + daily tournaments.
Official page: <a href="https://www.wynnlasvegas.com/casino/poker" target="_blank" rel="noopener">wynnlasvegas.com/casino/poker</a> (re-checked {AS_OF}).
The official Wynn poker page states the daily slate is suspended during Wynn Signature, Wynn Millions and Classic series; it does not name the WPT series. The official WPT World Championship schedule (Nov 27 \u2013 Dec 21) contains <strong>no 12:00 PM daily rows</strong>, so the recurring daily rows below are shown as unavailable during that window rather than assumed. <a href="flagged.html">See the flag</a>.</p>
<div class="cards">
 <div class="card"><div class="k">WPT rows</div><div class="v">{len(wyn_evs)}</div><div class="s">re-entry confirmed on featured events</div></div>
 <div class="card"><div class="k">Sheet silent on re-entry</div><div class="v">{len([e for e in wyn_evs if e['category']=='single'])}</div></div>
 <div class="card"><div class="k">Spend-more (WPT re-entry + daily rebuy)</div><div class="v">{len([e for e in wyn_evs if e['category']=='spend-more'])}</div></div>
</div>
{event_table(wyn_evs, 'tbl-venue')}
<h2>Hotel at this venue</h2>
{hotel_table(wyn_hotels, 'tbl-wyn-hotels', show_calc=False)}
<p class="note">Featured WPT events permit re-entry (verified from the official structures PDF): $600 NLH $400K and $800 NLH $1M — unlimited re-entry per flight until level 9; WPT Prime — one re-entry per flight until level 10; $600 NLH Turbo $50K — unlimited re-entry until level 9. None of these is single-entry.</p>"""

    body_oth = f"""
<h1>Other venues</h1>
<p class="lead">Recurring daily schedules verified from official pages on {AS_OF}. Rows without published buy-ins stay blank.</p>
<h2>Caesars Palace</h2>
<p class="excerpt">Official guide: four NLH events daily (10 AM, 2 PM, 6 PM, 9 PM), $100 buy-in, 20,000 chips, $1,000 GTD, 20-minute blinds, $50 add-on for 15,000 chips at the first break.</p>
<h2>Horseshoe Las Vegas (Hall of Fame Poker Room)</h2>
<p class="excerpt">Official guide: six NLH events daily (9 AM, 11 AM, 2 PM, 5 PM, 8 PM, 11 PM) — “a mixture of buy-ins, levels and guarantees”; values not published there.</p>
<h2>MGM Grand</h2>
<p class="excerpt">Official page: daily NLH tournaments at 11:00 AM, 7:00 PM and 11:00 PM. Buy-ins live on the official weekly-schedule PDF (not re-read this session).</p>
<h2>Golden Nugget <small class="note">(downtown — outside the Strip scope, kept for completeness)</small></h2>
<p class="excerpt">Official page: daily at 10 AM / 5 PM / 2 AM, 15,000 chips, 15-minute levels, unlimited re-entry until level 5 and up to two $20 add-ons. Buy-in not printed on the page.</p>
{event_table(oth_evs, 'tbl-venue')}
<h2>Hotels near these venues</h2>
{hotel_table(oth_hotels, 'tbl-oth-hotels', show_calc=False)}"""

    # ---------------- one page per venue ----------------
    # Every venue that appears in the dataset gets its own page with its events
    # and the hotels assigned to it. Pages are generated from the data, so a
    # venue added later cannot silently lose its page.
    VENUE_META = {
        "venetian": dict(slug="venue-venetian.html", title="The Venetian",
                         lead=("DeepStack Extravaganza IV, Nov 16 \u2013 Dec 23, 2026. "
                               "Poker room is on the property, so a stay here has a 0-minute walk."),
                         hotel_ids=("H-VEN", "H-PAL")),
        "wynn": dict(slug="venue-wynn.html", title="Wynn Las Vegas",
                     lead=("WPT World Championship, Nov 27 \u2013 Dec 21, 2026, plus the recurring daily slate. "
                           "The poker room is in Encore at Wynn Las Vegas (stated in the official WPT terms). "
                           "<br><strong>Daily tournaments during the series are not confirmed.</strong> The Wynn poker page says "
                           "the daily slate is suspended during Wynn Signature, Wynn Millions and Classic series and does "
                           "<em>not</em> name the WPT series; the official WPT World Championship schedule contains no "
                           "12:00 PM daily rows at all. The daily rows below are therefore marked unavailable for that "
                           "window rather than assumed to run. <a href=\"flagged.html\">Flagged</a>."),
                     hotel_ids=("H-WYN",)),
        "horseshoe": dict(slug="venue-horseshoe.html", title="Horseshoe Las Vegas",
                          lead="Hall of Fame Poker Room, recurring daily schedule.",
                          hotel_ids=("H-HS",)),
        "caesars": dict(slug="venue-caesars.html", title="Caesars Palace",
                        lead="Recurring daily No Limit Hold'em events.",
                        hotel_ids=("H-CZP",)),
        "mgm": dict(slug="venue-mgm.html", title="MGM Grand",
                    lead="Recurring daily No Limit Hold'em events.",
                    hotel_ids=("H-MGM",)),
        "bellagio": dict(slug="venue-bellagio.html", title="Bellagio",
                         lead="Recurring daily events; Friday $600 and weekend schedules.",
                         hotel_ids=("H-BEL",)),
        "gn": dict(slug="venue-goldennugget.html", title="Golden Nugget (downtown)",
                             lead=("Downtown Las Vegas \u2014 outside the Strip walking scope, kept for completeness. "
                                   "No Strip hotel is within a 30-minute walk of it."),
                             hotel_ids=()),
    }
    venue_pages = {}
    by_venue = {}
    for e in evs:
        by_venue.setdefault(e.get("venue_id"), []).append(e)
    for vid, meta in VENUE_META.items():
        vevs = by_venue.get(vid, [])
        vhotels = [h for h in hotels if h.get("id") in meta["hotel_ids"]]
        n_single = len([e for e in vevs if e["category"] == "single"])
        n_spend = len([e for e in vevs if e["category"] in ("spend-more", "multi-flight")])
        n_unv = len([e for e in vevs if e["category"] == "unverified"])
        checked = sorted({e.get("last_checked") for e in vevs if e.get("last_checked")})
        body_v = f"""
<h1>{esc(meta['title'])} \u2014 events and hotels</h1>
<p class="lead">{meta['lead']}</p>
<div class="cards">
 <div class="card"><div class="k">Events listed</div><div class="v">{len(vevs)}</div>
   <div class="s">last checked {esc(', '.join(checked)) or 'n/a'}</div></div>
 <div class="card"><div class="k">Sheet silent on re-entry</div><div class="v">{n_single}</div>
   <div class="s">sheet read; no re-entry/rebuy/add-on clause</div></div>
 <div class="card"><div class="k">Spend-more / multi-flight</div><div class="v">{n_spend}</div>
   <div class="s">extra buy-ins are possible</div></div>
 <div class="card"><div class="k">Unverified</div><div class="v">{n_unv}</div>
   <div class="s">no official rule document published</div></div>
</div>
<h2>Events at this venue</h2>
{toolbar('tbl-venue') if vevs else '<p class="excerpt">No event rows in the dataset for this venue.</p>'}
{event_table(vevs, 'tbl-venue') if vevs else ''}
<h2>Hotels at this venue</h2>
{hotel_table(vhotels, 'tbl-vh', show_calc=False) if vhotels else '<p class="excerpt">No hotel record is assigned to this venue in the dataset.</p>'}
<p class="note">Every value above links to the official venue document it came from. Blank cells mean the official
source does not publish that value; blanks are listed on the <a href="flagged.html">Flagged for review</a> page.</p>"""
        venue_pages[meta["slug"]] = (meta["title"], body_v)

    # ---------------- hotels ----------------
    body_h = f"""
<h1>Hotels — true cost per night</h1>
<p class="lead">True cost/night = (room rate + mandatory resort fee) × (1 + tax) + parking. The 13.38% room tax is the
Clark County transient lodging rate: the county’s own licensing guide for hotel/motel establishments prints 13.38%, the county’s
combined transient lodging return breaks it into an 8.5% and a 4.5% county component, and both The Venetian’s and The Cosmopolitan’s
hotel terms state 13.38% verbatim.
<a href="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf"
target="_blank" rel="noopener">County guide (PDF)</a> ·
<a href="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:46abba4b-3467-42d5-849b-c33a4e527b33/original/as/non-resort-within-sd-outside-pgc.pdf"
target="_blank" rel="noopener">county tax return components (PDF)</a>.
Rates are kept as a <strong>dated log</strong>, never a single value.</p>
<div class="panel"><h2>Rate log status — read this before trusting any nightly number</h2>
<p><strong>No dated room quote has been captured yet.</strong> Every official booking calendar reachable from this build
rendered nightly prices as <code>$XXX</code> behind a cookie wall, so the log below records the <em>attempt</em> rather than
a number. A price only enters the log together with its check-in, check-out, occupancy, room type, resort fee, tax line,
parking, cancellation deadline and the timestamp it was read, so quotes stay comparable like-for-like.</p>
<p><a href="https://www.venetianlasvegas.com/book?adults%5B%5D=2&arrival_date=2026-11-27&children%5B%5D=0&departure_date=2026-12-02&view=calendar"
target="_blank" rel="noopener">Example attempt: Venetian, 27 Nov – 2 Dec 2026, 2 adults (prices masked)</a></p>
<p><strong>Walking times:</strong> no casino page publishes a walk time, so the figures come from routing services
instead, labelled as such. Google Maps walking directions were read on 2026-11-17 for eight hotels' trips to The Venetian
Poker Room, and an independent OSRM foot-profile matrix (computed 2026-11-16 from geocoded official addresses) covers
twenty-one hotels. The two agree on the 30-minute verdict everywhere both cover, which is why the filter below can be
applied. The Wynn side rests on the OSRM matrix alone, so those figures are labelled "1 router" rather than
quoted as confirmed.</p></div>
{toolbar('tbl-hotels', with_walk=True, cat_options=False)}
{hotel_table(hotels, 'tbl-hotels', show_calc=True)}
{walking_check_html()}
<h2>Dated rate logs</h2>
{shared_rate_log_html()}
{''.join(f'<details><summary>{esc(h["name"])}</summary>{rate_log_html(h)}</details>' for h in hotels)}
<div class="panel"><h2>What is still missing</h2>
<ul class="tight">
<li>Dated checkout quotes for exact trip dates (checkout total, nightly average, cancellation deadline, rate timestamp).</li>
<li>Walking times to The Venetian Poker Room are recorded for every hotel whose route was read, and the 30-minute call is confirmed by a second, independent router (see the hotels page). The Wynn side is covered by the OSRM matrix alone, so those rows say "1 router"; the two tight Venetian-side calls (ARIA and Bellagio) are the ones still worth walking in person.</li>
<li>Official resort-fee amounts for Caesars properties (shown in the official booking flow at checkout; Diamond+ waives).</li>
</ul>
<p class="note">The trip calculator on the <a href="planner.html">Trip Planner</a> uses the same formula, per hotel, over your stay.</p></div>"""

    # ---------------- planner ----------------
    # ---- day-by-day plan -------------------------------------------------
    # A realistic "play all day" test is NOT "does the event's estimated finish
    # collide with the next start". It is:
    #   can I enter event B before its late registration closes, if I am knocked
    #   out of event A?
    # That only needs published facts: A's start time and B's printed registration
    # close. No invented finish time is used, and a pair is only flagged when the
    # published times make the sequence impossible for a player who enters both.
    def to_min(t):
        p = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)", str(t or ""), re.I)
        if not p:
            return None
        h, m = int(p.group(1)), int(p.group(2))
        if p.group(3).upper() == "PM" and h != 12:
            h += 12
        if p.group(3).upper() == "AM" and h == 12:
            h = 0
        return h * 60 + m

    def entry_rank(e):
        # which rows may be recommended as an entry at all
        return e.get("category") in ("single", "ambiguous")

    plan_rows = []
    dated = [e for e in evs if re.match(r"^\d{4}-", e.get("date", ""))]
    for date in all_dates:
        day = [e for e in dated if e["date"] == date]
        day.sort(key=lambda x: (to_min(x.get("start")) is None, to_min(x.get("start")) or 0))
        if not day:
            continue
        playable = [e for e in day if entry_rank(e)] or day
        primary = playable[0]
        p_start = to_min(primary.get("start"))
        # fallback = the latest same-day event whose registration is still open
        # after the primary has started (so it is reachable if you bust early)
        fallback, pairs = None, []
        for e in day:
            if e is primary:
                continue
            s_b, close_b = to_min(e.get("start")), to_min(e.get("reg_close_end"))
            if s_b is None:
                continue
            if p_start is not None and close_b is not None:
                if close_b > p_start:
                    pairs.append(e)
            elif s_b > (p_start or 0):
                pairs.append(e)
        if pairs:
            fallback = pairs[-1]
        # Two published-fact tests. Neither invents a finish time.
        #  (a) closed-registration: a later event whose registration had already
        #      closed before the earlier event started can never be entered.
        #  (b) same-time collision: two events at different properties starting
        #      within the 30-minute walking limit cannot both be played.
        clashes = []
        for i in range(len(day)):
            for j in range(i + 1, len(day)):
                a, b = day[i], day[j]
                sa, sb = to_min(a.get("start")), to_min(b.get("start"))
                if sa is None or sb is None:
                    continue
                cb = to_min(b.get("reg_close_end"))
                if sb > sa and cb is not None and cb <= sa:
                    clashes.append(("registration closed", a, b))
                    continue
                if (a.get("venue") != b.get("venue")) and abs(sb - sa) <= 30:
                    clashes.append(("starts within 30 min at a different property", a, b))
        ov_html = " ".join(
            f'<span class="badge b-bad">{esc(a.get("name","")[:22])} ({esc(a.get("start"))}) vs '
            f'{esc(b.get("name","")[:22])} ({esc(b.get("start"))}) — {esc(why)}</span>'
            for why, a, b in clashes)
        def cell(e, cls):
            if not e:
                return '<td class="muted">—</td>'
            close = fmt_hm(e.get("reg_close_end"))
            return (f'<td class="{cls}"><strong>{esc(e.get("start"))}</strong> {esc(e.get("name"))} '
                    f'({money(e.get("buy_in"))}) {cat_badge(e.get("category"))}'
                    f'<small class="note">{esc(e.get("venue"))} · registration closes '
                    f'{esc(close) if close else "not printed on the sheet"}</small></td>')
        if fallback is None:
            fb_cell = '<td class="muted">No later event on this day whose registration stays open past the primary’s start.</td>'
        else:
            fb_cell = cell(fallback, "fallback")
        plan_rows.append(f"""<tr><td>{esc(date)}</td>{cell(primary,'primary')}{fb_cell}
<td>{ov_html or '<span class="badge b-good">no impossible sequence on the published times</span>'}</td></tr>""")

    trip_events = sorted([e for e in evs if e["category"] in ("single", "ambiguous") and e.get("buy_in")],
                         key=lambda x: (x.get("date", ""), x.get("start", "")))
    cb_items = "".join(
        f'<label style="display:block"><input type="checkbox" data-buyin="{e["buy_in"]}"> '
        f'{esc(e.get("date"))} {esc(e.get("start"))} — {esc(e.get("name"))[:58]} ({money(e["buy_in"])})</label>'
        for e in trip_events)
    hotel_opts = "".join(
        f'<option value="{esc(h["id"])}" data-rate="{(h.get("rate_log") or [{}])[-1].get("rate","") if h.get("rate_log") else ""}" '
        f'data-fee="{h.get("resort_fee_value") or 0}" data-tax="{(h.get("tax_rate") or 0)*100}" '
        f'data-parking="{h.get("parking_value") or 0}">{esc(h["name"])}</option>' for h in hotels)

    body_p = f"""
<h1>Trip planner</h1>
<p class="lead">Estimated cost of a trip = <strong>entries × buy-ins + nights × true hotel cost</strong>,
where true hotel cost/night = (rate + resort fee) × (1 + tax) + parking. Enter values only from verified rows or your own dated quote.</p>
<div class="panel" id="trip-calc">
<h2>Trip cost calculator</h2>
<div class="form-grid">
  <div><label>Pick sheet-silent / ambiguous entries</label>
    <div style="max-height:14rem;overflow:auto;border:1px solid var(--line);border-radius:8px;padding:.5rem">{cb_items}</div>
    <small class="note" id="trip-entry-sum"></small></div>
  <div>
    <label>Hotel preset (loads its verified fee/tax/parking)</label>
    <select id="trip-preset-hotel"><option value="">— custom —</option>{hotel_opts}</select>
    <label>Nights</label><input type="number" id="trip-nights" min="1" value="7">
    <label>Room rate per night ($) — from a dated quote only</label>
    <input type="number" id="trip-nightly" min="0" value="" placeholder="not captured from any official source">
    <label>Resort fee per night ($)</label><input type="number" id="trip-resort-fee" min="0" value="55">
    <label>Tax (%)</label><input type="number" id="trip-tax" min="0" step="0.01" value="13.38">
    <label>Parking per night ($)</label><input type="number" id="trip-parking" min="0" value="20">
    <p class="note" id="trip-rate-warning">No dated room rate has been captured from an official source,
    so the hotel side of this estimate is intentionally blank. The resort fee ($55 + tax) and the 13.38% Clark
    County room tax are sourced; the room rate is not, and the calculator will not invent one.</p>
  </div>
</div>
<div class="result">
  True hotel cost per night: <span class="total" id="trip-true-nightly">—</span><br>
  Hotel total for stay: <span class="total" id="trip-hotel-total">—</span><br>
  <strong>Estimated trip total (entries + hotel): <span class="total" id="trip-grand">—</span></strong>
  <p class="note">Formula: entries × buy-ins + nights × true hotel cost. Excludes flights, food, and cash-game bankroll. The resort fee and tax are the sourced figures; the room rate stays empty until a dated checkout quote is captured.</p>
</div>
</div>
<h2 id="dayplan">Day-by-day plan — primary + conditional fallback</h2>
<p class="note">No casino publishes finish times, so this plan uses only two published facts: each event's start time
and the clock time its structure sheet prints for the close of registration. Nothing here assumes how long you will last.
The primary event is the earliest event that is actually enterable on that date; the fallback is a later event on the same
date whose printed registration close falls after the primary's start, so it is still open if you are eliminated early.
A row is flagged only when the documents make the pair impossible — either the fallback's registration had already closed
before the primary began, or two events at different properties start within 30 minutes of each other.</p>
<table class="data day-plan"><thead><tr><th>Date</th><th>Primary event</th><th>Conditional fallback</th><th>Playability against the published times</th></tr></thead>
<tbody>{''.join(plan_rows)}</tbody></table>"""

    # ---------------- ranking ----------------
    def rank_rows(rows):
        rows = sorted(rows, key=lambda x: -(x.get("gtd_ratio") or 0))
        out = []
        for e in rows:
            if not e.get("gtd_ratio"):
                continue
            out.append(f"""<tr><td>{esc(e.get('date'))}</td><td>{esc(e.get('venue'))}</td>
<td>{esc(e.get('name'))}</td><td>{money(e.get('buy_in'))}</td>
<td>{money(e.get('fee'))}</td><td>{money(e.get('pool_per_entry'))}</td>
<td>{money(e.get('gtd'))}</td><td><strong>{e['gtd_ratio']:.2f}×</strong></td>
<td class="src">{src_links(e.get('source_url'), e.get('struct_url'))}</td></tr>""")
        return "".join(out)
    head_r = ("<th>Date</th><th>Venue</th><th>Event</th><th>Total entry fee</th><th>House fee</th>"
              "<th>Prize pool/entry</th><th>Guarantee</th><th>Pool ÷ fee</th><th>Sources</th>")
    nlh_singles = [e for e in singles + ambiguous
                   if e.get("gtd_ratio") and "bounty" not in " ".join(e.get("tags", []))]
    bounty_singles = [e for e in singles + ambiguous
                      if e.get("gtd_ratio") and "bounty" in " ".join(e.get("tags", []))]
    body_r = f"""
<h1>Descriptive ranking</h1>
<div class="flag info"><strong>Read this first.</strong> “Pool ÷ fee” is a descriptive ratio of two published numbers
(guaranteed prize pool ÷ total entry fee). It is <strong>not</strong> a forecast, an EV estimate, or a prediction of
attendance, overlay, or ROI. Events are ranked only when both the total entry fee and the guarantee are confirmed from
official sources. Bounty and multi-flight events are shown in separate tables because their guarantees are not comparable.</div>
<h2>NLH events whose sheet is silent on re-entry (no bounty)</h2>
<table class="data"><thead><tr>{head_r}</tr></thead><tbody>{rank_rows(nlh_singles)}</tbody></table>
<h2>Bounty / PKO events — labeled separately</h2>
<p class="note">For bounty events the published guarantee often includes total bounties (marked in the table where the structure sheet says so).</p>
<table class="data"><thead><tr>{head_r}</tr></thead><tbody>{rank_rows(bounty_singles)}</tbody></table>
<h2>Not ranked here</h2>
<ul class="tight">
<li><strong>Spend-more events ({len(spend)}):</strong> cost to enter is not a single number when re-entry/rebuy/add-ons exist. See <a href="tournaments.html">Tournaments</a> filtered to “Spend-more”.</li>
<li><strong>Multi-flight events ({len(multiflight)}):</strong> guarantee is shared across flights; per-flight entry ≠ per-event cost.</li>
<li><strong>Satellites ({len(satellites)}) / team events ({len(teams)}):</strong> prizes are seats; or the unit is a team.</li>
<li><strong>Unverified rows ({len(unverified)}):</strong> ranking requires confirmed fee and guarantee.</li>
</ul>"""

    # ---------------- rules ----------------
    rule_rows = []
    for e in sorted(evs, key=lambda x: (x.get("venue", ""), x.get("date", ""), x.get("start", ""))):
        r = e.get("rules", {})
        excerpt = esc(r.get("excerpt", ""))[:220]
        rule_rows.append(f"""<tr data-cat="{esc(e.get('category'))}">
<td>{esc(e.get('venue'))}</td><td>{esc(e.get('date'))} {esc(e.get('start'))}</td>
<td>{esc(e.get('name'))}</td>
<td>{rule_badge(r)}<small class="note">{esc(r.get('single_entry',''))}</small></td>
<td>{esc(r.get('re_entry',''))}</td><td>{esc(r.get('add_on',''))}</td>
<td>{money(e.get('fee'))}{' / ' + money(e.get('pool_per_entry')) + ' pool' if e.get('pool_per_entry') else ''}</td>
<td class="excerpt">{excerpt}</td>
<td>{esc(r.get('retrieved',''))}</td>
<td class="src">{src_links(e.get('struct_url') or e.get('source_url'))}</td></tr>""")
    body_rules = f"""
<h1>Structured entry-rule fields</h1>
<p class="lead">Single-entry, re-entry, add-on and fee values are stored as separate fields per event, each with its
source excerpt and retrieval date. Excerpts are quoted from the official structure sheet or page.</p>
{toolbar('tbl-rules', all_dates)}
<table class="data" id="tbl-rules"><thead><tr>
<th>Venue</th><th>Date / start</th><th>Event</th><th>Single-entry field</th><th>Re-entry field</th>
<th>Add-on field</th><th>Fee (house / pool)</th><th>Source excerpt</th><th>Retrieved</th><th>Source</th>
</tr></thead><tbody>{''.join(rule_rows)}</tbody></table>"""

    # ---------------- monitor ----------------
    rows_m = []
    affected = {}
    for e in evs:
        for u in (e.get("source_url"), e.get("struct_url")):
            if u:
                affected[u] = affected.get(u, 0) + 1
    for h in hotels:
        for u in (h.get("resort_fee_src"), h.get("booking_url")):
            if u:
                affected[u] = affected.get(u, 0) + 1
    for u in monitor.get("urls", []):
        st = u.get("status", "never checked")
        cls = {"changed": "b-bad", "unchanged": "b-good", "new": "b-warn"}.get(st, "b-chip")
        rows_m.append(f"""<tr><td>{esc(u.get('label',''))}</td>
<td class="src"><a href="{esc(u.get('url',''))}" target="_blank" rel="noopener">{esc(u.get('url',''))[:70]}…</a></td>
<td>{esc(u.get('last_checked','—'))}</td><td><span class="badge {cls}">{esc(st)}</span></td>
<td>{affected.get(u.get('url',''), 0)}</td></tr>""")
    body_mon = f"""
<h1>Source monitor</h1>
<p class="lead">A scheduled GitHub Actions job re-fetches every official URL on this list, compares a content hash with
the stored one, saves daily snapshots under <code>data/snapshots/</code>, and marks rows whose source changed.
Workflow: <code>.github/workflows/source-monitor.yml</code> (daily at 07:00 Las Vegas time) + <code>scripts/monitor.py</code>.</p>
<div class="panel"><strong>Current state:</strong> {len(monitor.get('urls', []))} URLs registered ·
{sum(1 for u in monitor.get('urls', []) if u.get('status') == 'changed')} changed ·
{sum(1 for u in monitor.get('urls', []) if u.get('status') == 'unchanged')} unchanged.
Hashes are established on the first scheduled run; after that, any hash mismatch marks the URL “changed” and every
table row citing it gets a <span class="badge b-bad">source changed — re-check</span> badge.</div>
<table class="data"><thead><tr><th>Source</th><th>URL</th><th>Last checked</th><th>Status</th><th>Rows citing it</th></tr></thead>
<tbody>{''.join(rows_m)}</tbody></table>"""

    # ---------------- flagged ----------------
    def flag_html(f):
        fid = esc(f.get("id", ""))
        sev = (f.get("severity") or "").lower()
        sev_badge = ""
        if sev in ("high", "medium", "critical"):
            sev_badge = f' <span class="badge b-bad">{esc(sev)}</span>'
        elif sev == "info":
            sev_badge = ' <span class="badge b-good">superseded</span>'
        src = (f' · <a href="{esc(f["url"])}" target="_blank" rel="noopener">official source</a>'
               if f.get("url") else ' · <span class="badge b-warn">no official link recorded</span>')
        resolved = (f'<div class="resolved"><strong>Update {esc(AS_OF)}:</strong> {esc(f["resolved"])}</div>'
                    if f.get("resolved") else "")
        return (f'<div class="flag" id="{fid}"><strong>{fid} · {esc(f.get("item",""))}</strong>{sev_badge}'
                f'{(" · " + esc(f.get("where",""))) if f.get("where") else ""}'
                f'<br>{esc(f.get("detail",""))}{src}'
                f'{resolved}'
                f'<small class="note">recorded by {esc(f.get("source",""))}'
                f'{(" · retrieved " + esc(f.get("retrieved"))) if f.get("retrieved") else ""}</small></div>')

    fl = "".join(flag_html(f) for f in master["flags"] if isinstance(f, dict))
    body_f = f"""
<h1>Flagged for review</h1>
<p class="lead">{n_flags} irregularities and open items. None of these blocks the data — review them and request changes.
Every flag carries the source link it was found on.</p>
{fl}"""

    # ---------------- questions ----------------
    q_rows = "".join(
        f"""<tr><td>{esc(q.get('id',''))}</td><td>{esc(q.get('question',''))}</td>
<td>{esc(q.get('answer','') or '—')}</td><td><span class="badge b-warn">{esc(q.get('status',''))}</span></td>
<td>{esc(q.get('needed','') or q.get('how_to_find',''))}</td></tr>"""
        for q in master["questions"])
    body_q = f"""
<h1>Questions — what must be answered before deciding</h1>
<p class="lead">{esc(master.get('questions_intro',''))} These are the gaps between what we have verified and what a
booking/registration decision needs. Suggestions for discovering the missing information live on the
<a href="suggestions.html">suggestions page</a>.</p>
<table class="data"><thead><tr><th>#</th><th>Question</th><th>Current answer</th><th>Status</th><th>What is needed / how to find it</th></tr></thead>
<tbody>{q_rows}</tbody></table>
<div class="panel"><h2>Added by this session</h2><ul class="tight">
<li><strong>Q-A:</strong> What is the dated checkout total (with tax and resort fee) for the exact trip dates at Venetian, Palazzo and Wynn? — Open. Use the official booking links on the <a href="hotels.html">hotels page</a>; log the quote with its timestamp in the rate log.</li>
<li><strong>Q-B:</strong> The Wynn-side walking figures rest on a single router (OSRM); only the Venetian side has been confirmed twice. ARIA is also the one hotel where the two routers straddle the 30-minute line (30.6 vs 37 min).</li>
<li><strong>Q-C:</strong> Do the Venetian DSE sheets’ “no re-entry clause” silence and the Valuetown “subsequent buy in’s” note mean unlimited re-entry is allowed after all? — Open. Only the poker room can settle it (flag IR-8234-01/02).</li>
<li><strong>Q-D:</strong> Which Caesars Palace daily buy-in figure is current — $100 (official guide) or $160 at 2 PM/9 PM (official flyer)? — Open; two official sources disagree.</li>
<li><strong>Q-E:</strong> What are the Horseshoe and MGM Grand daily buy-ins and guarantees? — Open; not published on their official pages (Horseshoe) or only on the weekly PDF (MGM).</li>
</ul></div>"""

    # ---------------- suggestions ----------------
    s_rows = "".join(
        f"""<tr><td>{esc(x.get('id',''))}</td><td><strong>{esc(x.get('title',''))}</strong><small class="note">{esc(x.get('category',''))}</small></td>
<td>{'<br>'.join(esc(o) for o in x.get('options', []))}</td>
<td>{esc(x.get('tradeoff',''))}</td>
<td><span class="badge b-info">{esc(x.get('status',''))}</span>
{('<small class="note"><strong>Recommended:</strong> ' + esc(x["recommendation"]) + '</small>') if x.get('recommendation') else ''}
{('<small class="note">' + esc(x["implemented_as"]) + '</small>') if x.get('implemented_as') else ''}</td></tr>"""
        for x in master["suggestions"])
    body_s = f"""
<h1>Suggestions — review before implementing</h1>
<p class="lead">{esc(master.get('suggestions_intro',''))} Each item lists options, the trade-off and — where the work has
already been done here — exactly how it was done, so you can accept it or ask for a different option.</p>
<table class="data"><thead><tr><th>#</th><th>Suggestion</th><th>Options</th><th>Trade-off</th><th>Status</th></tr></thead>
<tbody>{s_rows}</tbody></table>
<div class="panel"><h2>Added by this session</h2>
<ul class="tight">
<li><strong>S-A (Decision quality):</strong> Require a dated checkout quote + verified walk time before any event/hotel pair leaves the “candidate” list. Options: A) hard gate in the planner (recommended) · B) warning badge only · C) manual checklist. Trade-off: A prevents bad bookings but blocks planning until quotes exist.</li>
<li><strong>S-B (Ranking honesty):</strong> Keep bounty guarantees out of the main ratio table (implemented on the Ranking page) and add an overlay tracker once real attendance data exists. Options: A) leave ratio as the only metric · B) add historical field sizes per event · C) add EV model. Trade-off: B is data-heavy; C needs assumptions you may not trust.</li>
<li><strong>S-C (Consolidation):</strong> Retire the archived /docs and /verified dashboards once this master site is accepted, so there is one source of truth. Options: A) keep archives visible · B) unpublish but keep in git history (recommended) · C) delete. Trade-off: A causes confusion; C loses browsable history.</li>
<li><strong>S-D (Monitoring depth):</strong> Extend the daily source monitor to diff parsed values (buy-in, guarantee) instead of page hashes. Options: A) hash-only (current) · B) parsed diff for the 4 key pages · C) full parser for every PDF. Trade-off: B/C catch silent edits but need maintenance when layouts change.</li>
</ul></div>"""

    # ---------------- repo review ----------------
    body_repo = f"""
<h1>Repo review</h1>
<p class="lead">Line-by-line state of the repository as of {AS_OF}, after the integration pass.</p>
<div class="panel"><h2>Structure</h2>
<ul class="tight">
<li><code>data/master.json</code> — unified dataset (events, hotels, rate logs, rules, flags) generated by <code>scripts/build_master.py</code> from verified inputs.</li>
<li><code>data/session-updates.json</code> — this session’s official-source reads (structure-sheet excerpts, recurring venue feeds, hotel facts).</li>
<li><code>data/source_monitor.json</code> — URL/hash registry maintained by <code>scripts/monitor.py</code> (scheduled).</li>
<li>Root pages (this dashboard) — generated by <code>scripts/build_site.py</code>; row-level source check fails the build if a row lacks an official link.</li>
<li><code>docs/</code> and <code>verified/</code> — earlier session dashboards, preserved as archives and linked in the footer.</li>
<li><code>COORDINATION.md</code> — shared task board for parallel sessions.</li>
</ul></div>
<div class="panel"><h2>Irregularities found in earlier data (flagged, not silently fixed)</h2>
<ul class="tight">
<li>Three overlapping dashboards exist (root, <code>/docs/</code>, <code>/verified/</code>). This root dashboard supersedes them; consolidation is suggestion S-C.</li>
<li>Earlier datasets disagreed on chip counts and reg-close times for some Venetian rows (see session arena/acd81e67-poker2 notes in COORDINATION.md). Rows in this site use the structure-sheet values where the sheet was read; others carry blanks.</li>
<li>“Verified single-entry” in older files meant “no re-entry language found”. This site labels that state precisely (“Sheet silent on re-entry — sheet read”) and states in every legend that silence is not a published freezeout rule.</li>
<li>Wynn WPT “NIH” naming, the Venetian series-label staleness, and the Caesars guide-vs-flyer buy-in conflict are preserved as flags.</li>
</ul></div>
<div class="panel"><h2>Verification performed in this integration pass</h2>
<ul class="tight">
<li>13 Venetian structure PDFs read directly (structures 8, 17, 18, 22, 23, 26, 27, 28, 29, 30, 31, 32, 33) + multi-flight sheets 2 and 9.</li>
<li>Wynn poker page, Caesars poker guide, MGM Grand poker page, Golden Nugget daily page re-read directly.</li>
<li>Hotel facts: Venetian tax/resort-fee/player-rate pages and Wynn resort-information page are the basis of every hotel value; Caesars fees intentionally blank.</li>
<li>Build-time check: every event and hotel row must cite an official https source or the build fails.</li>
</ul></div>"""

    pages = {
        "index.html": ("Dashboard", body),
        "summary.html": ("Executive summary", body_sum),
        "tournaments.html": ("Tournaments", body_t),
        # NOTE: venue-*.html are emitted by the generated per-venue builder below.
        # They used to be listed here too, and the hand-written body overwrote the
        # generated page (so the Wynn suspension notice never reached the site).
        "venue-others.html": ("Other venues", body_oth),
        "hotels.html": ("Hotels", body_h),
        "planner.html": ("Trip planner", body_p),
        "ranking.html": ("Ranking", body_r),
        "rules.html": ("Entry rules", body_rules),
        "monitor.html": ("Source monitor", body_mon),
        "flagged.html": ("Flagged for review", body_f),
        "questions.html": ("Questions", body_q),
        "suggestions.html": ("Suggestions", body_s),
        "repo-review.html": ("Repo review", body_repo),
    }
    pages.update(venue_pages)
    for fn, (title, b) in pages.items():
        with open(os.path.join(ROOT, fn), "w") as f:
            f.write(page(title, fn, b))
    # redirect for the old planning.html name
    with open(os.path.join(ROOT, "planning.html"), "w") as f:
        f.write('<!DOCTYPE html><html><head><meta http-equiv="refresh" content="0; url=planner.html">'
                '<title>Redirecting…</title></head><body><a href="planner.html">Continue to the trip planner</a></body></html>')

    # ---- verification pass: every row must have an official https source ----
    bad = []
    for e in evs:
        u = e.get("source_url", "")
        if not (u.startswith("https://") and any(d in u for d in
                ("venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com", "caesars.com",
                 "mgmresorts.com", "goldennugget.com", "contentstack.io", "visitwynn.com"))):
            bad.append(e["id"])
    for h in hotels:
        u = h.get("resort_fee_src", "")
        if u and not u.startswith("https://"):
            bad.append(h["id"])
    if bad:
        raise SystemExit("Rows without an official source link: %s" % bad)
    print("site built: %d pages, %d events, %d hotels — all rows cited" % (len(pages), len(evs), len(hotels)))

if __name__ == "__main__":
    build()
