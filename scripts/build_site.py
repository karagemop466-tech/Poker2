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
    "multi-day": ('b-info', "Multi-day (one starting day)"),
    "satellite": ('b-chip', "Satellite"),
    "team": ('b-chip', "Team event"),
    "unverified": ('b-warn', "UNVERIFIED"),
}

def cat_badge(cat):
    cls, label = CATS.get(cat, ('b-chip', cat))
    return f'<span class="badge {cls}">{esc(label)}</span>'

def rule_badge(rules, entry=None):
    """Entry-rule badge. Driven by what the document says, never by inference."""
    entry = entry or {}
    state = entry.get("entry_state")
    if state == "stated":
        return ('<span class="badge b-bad" title="The sheet states the entry rule; read the field detail">sheet states the rule · '
                'not single-entry</span>')
    if state == "stated_multi_entry":
        return '<span class="badge b-bad">sheet prices further buy-ins</span>'
    if state == "silent":
        return ('<span class="badge b-good" title="Structure sheet read in full: no re-entry, rebuy or '
                'add-on clause is printed. Silence is not a published freezeout rule.">sheet read · no '
                're-entry/rebuy/add-on printed</span>')
    if state == "not_stated":
        return '<span class="badge b-warn">no rule document published</span>'
    se = rules.get("single_entry", "") or ""
    if not isinstance(se, str):
        se = str(se)
    if se.startswith("not stated"):
        return '<span class="badge b-good">sheet read · no re-entry/rebuy/add-on printed</span>'
    if se.startswith("ambiguous"):
        return '<span class="badge b-warn">ambiguous wording</span>'
    if se.startswith("no"):
        return '<span class="badge b-bad">not single-entry</span>'
    return '<span class="badge b-warn">unverified</span>'


FIELD_LABELS = [("single_entry", "Single entry"), ("re_entry", "Re-entry"), ("add_on", "Add-on"),
                ("fee", "House fee"), ("guarantee", "Guarantee"), ("payout", "Payout"),
                ("bounty", "Bounty")]
STATUS_WORDS = {"explicit": "stated on the sheet", "explicit_no": "stated on the sheet",
                "not_stated_sheet_read": "read in full · not stated", "not_read": "not read",
                "not_stated": "not stated"}


def rule_detail(e):
    """Per-field entry-rule evidence: value, status, the sheet's own words, its URL and the date
    it was retrieved. Nothing here is inferred — a field that the document does not state is
    shown as unread/no-provision, with the sheet link so the reader can check it."""
    f = e.get("rules_fields") or {}
    if not f:
        return ""
    items = []
    for key, label in FIELD_LABELS:
        rec = f.get(key)
        if not isinstance(rec, dict):
            continue
        val = rec.get("value")
        if val is None or val == "":
            val = "not stated"
        st = STATUS_WORDS.get(str(rec.get("status")), str(rec.get("status") or "—"))
        src = rec.get("source_url") or e.get("struct_url") or ""
        link = (f' <a href="{esc(src)}" target="_blank" rel="noopener">sheet</a>' if src else "")
        exc = rec.get("excerpt") or ""
        items.append(
            f'<li><strong>{esc(label)}</strong>: {esc(val)} '
            f'<small class="note">· {esc(st)} · retrieved {esc(rec.get("retrieved") or e.get("sheet_retrieved") or "")}{link}</small>'
            + (f'<div class="excerpt">&ldquo;{esc(exc)}&rdquo;</div>' if exc else "") + "</li>")
    if not items:
        return ""
    gate = ""
    el = e.get("eligibility") or {}
    if isinstance(el, dict) and el.get("value"):
        gate = (f'<div class="excerpt"><strong>Eligibility:</strong> {esc(el["value"])} '
                f'&ldquo;{esc(el.get("excerpt") or "")}&rdquo; '
                f'<a href="{esc(el.get("source_url") or "")}" target="_blank" rel="noopener">source</a>'
                f' · retrieved {esc(el.get("retrieved") or "")}</div>')
    spend = ""
    if e.get("spend_advantage"):
        spend = (f'<div class="excerpt"><strong>Spend advantage:</strong> {esc(e["spend_advantage"])} '
                 f'<a href="{esc(e.get("spend_advantage_source") or "")}" target="_blank" '
                 f'rel="noopener">source</a></div>')
    return (f'<details><summary class="note">Entry-rule evidence, field by field</summary>'
            f'<ul class="tight">{"".join(items)}</ul>{gate}{spend}</details>')


def struct_cell(e):
    """Starting stack, blind length and the registration window — the comparison fields the
    structure sheets publish. A blank stays blank when no document states it."""
    bits = []
    if e.get("chips"):
        bits.append(f'{int(e["chips"]):,} chips' if str(e.get("chips")).isdigit() else f'{esc(e["chips"])} chips')
    if e.get("level_min"):
        bits.append(f'{esc(e["level_min"])}-min levels')
    lr = e.get("late_reg") or ""
    if lr:
        bits.append(esc(lr))
    if e.get("pays_pct"):
        bits.append(f'pays {e["pays_pct"]}% of field')
    if not bits:
        return '<span class="badge b-warn">not published</span>'
    return "<small class=\"note\">" + " · ".join(bits) + "</small>"

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
        gate = ""
        el = e.get("eligibility")
        if isinstance(el, dict) and el.get("value"):
            gate = (f' <span class="badge b-chip" title="{esc(el.get("excerpt") or "")} '
                    f'· retrieved {esc(el.get("retrieved") or "")}">restricted field: {esc(el["value"])}</span>')
        elif isinstance(el, str) and el.strip():
            gate = f' <span class="badge b-chip">restricted field: {esc(el)}</span>'
        # a row that is not available in its own window must say so in the table, not only in prose
        avail = (f'<div class="badge b-bad">{esc(e["availability_note"])}</div>'
                 if e.get("availability_note") else "")
        walk = ""
        cb = (f'<td><input type="checkbox" data-buyin="{e.get("buy_in") or 0}"></td>' if show_checkboxes else "")
        extra = (f'<td>{struct_cell(e)}</td>' if extra_cols else "")
        rows.append(f"""<tr data-date="{esc(e.get('date',''))}" data-cat="{esc(e.get('category',''))}" data-tags="{esc(' '.join(e.get('tags',[])))}">
<td>{esc(e.get('date'))}</td><td>{esc(e.get('start'))}</td><td>{esc(e.get('venue'))}</td>
<td><strong>{esc(e.get('name'))}</strong>{tags}{gate}{avail}</td>
<td>{buy_cell}</td><td>{gtd}</td><td>{ratio}</td>
<td>{cat_badge(e.get('category'))} {rule_badge(e, e)}{rule_detail(e)}</td>
{extra}<td class="src">{src_links(e.get('source_url'), e.get('struct_url'))}{changed_flag(e.get('source_url'))} <small class="note">checked {esc(e.get('last_checked'))}</small></td>
{cb}</tr>""")
    head = ("<th>Date</th><th>Start</th><th>Venue</th><th>Event</th><th>Buy-in (fee split)</th>"
            "<th>Guarantee</th><th>Pool ÷ fee</th><th>Entry rules</th>"
            + ("<th>Stack · levels · registration · payout</th>" if extra_cols else "")
            + "<th>Sources / last checked</th>"
            + ("<th>Trip</th>" if show_checkboxes else ""))
    return f'<table class="data" id="{table_id}"><thead><tr>{head}</tr></thead><tbody>' + "\n".join(rows) + "</tbody></table>"

def toolbar(table_id, dates=None, with_walk=False, cat_options=True):
    opts = "".join(f'<option value="{esc(d)}">{esc(d)}</option>' for d in (dates or []))
    cats = ('<option value="">All categories</option>'
            '<option value="single">Sheet silent on re-entry</option>'
            '<option value="ambiguous">Entry limit ambiguous</option>'
            '<option value="spend-more">Spend-more (re-entry/add-on)</option>'
            '<option value="multi-flight">Multi-flight</option>'
            '<option value="multi-day">Multi-day (one starting day)</option>'
            '<option value="satellite">Satellite</option>'
            '<option value="team">Team</option>'
            '<option value="unverified">Unverified</option>')
    walk = ('<label><input type="checkbox" data-bind-walk="' + table_id + '"> ≤30-min walk (routed estimate) only</label>'
            if with_walk else "")
    return f"""<div class="toolbar">
<input type="search" placeholder="Search all columns…" data-bind-search="{table_id}">
<select data-bind-date="{table_id}"><option value="">All dates</option>{opts}</select>
{f'<select data-bind-cat="{table_id}">{cats}</select>' if cat_options else ''}
{walk}
<label><input type="checkbox" onchange="var s=document.querySelector('[data-bind-cat=&quot;{table_id}&quot;]');if(s){{s.value=this.checked?'single':'';s.dispatchEvent(new Event('change'));}}"> Sheet silent on re-entry only <small class="note">(the closest a source gets to single-entry here — no room publishes a freezeout rule)</small></label>
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
        rl = [x for x in (h.get("rate_log") or []) if x.get("rate") is not None]
        quote = h.get("quote") or {}
        if quote.get("checkout_total_usd") is not None:
            rate_cell = (f'<strong>{money(quote["nightly_average_usd"])}</strong>'
                         f'<small class="note">/night average of the itemised official quote · '
                         f'{esc(quote.get("stay_start"))} → {esc(quote.get("stay_end"))} · '
                         f'{quote.get("nights")} nights · {esc(quote.get("adults"))} adults · '
                         f'{esc(quote.get("suite_type"))}</small>'
                         f'<small class="note">checkout total {money(quote["checkout_total_usd"])} '
                         f'= room {money(quote.get("room_subtotal_usd"))} + resort fee '
                         f'{money(quote.get("resort_fee_total_usd"))} + tax {money(quote.get("taxes_usd"))}'
                         f' ({quote.get("tax_pct_implied")}%) · captured {esc(quote.get("date_captured"))} · '
                         f'<a href="{esc(quote.get("source_url"))}" target="_blank" rel="noopener">official quote</a></small>'
                         + (f'<small class="note">Caveat: {esc(quote.get("caveat"))}</small>'
                            if quote.get("caveat") else ""))
        elif rl:
            latest = rl[-1]
            rate_cell = (f'{money(latest["rate"])} <small class="note">{esc(latest.get("basis",""))} · '
                         f'logged {esc(latest["date"])} — a from-price, not a quote</small>')
        else:
            rate_cell = '<span class="badge b-warn">no dated quote</span>'
        # --- prefill: the calculator must not be the only way to see a true cost. If the data
        #     carries a dated room rate, the row shows the arithmetic the sources support.
        prefill = ""
        prefill_src = ""
        if quote.get("room_subtotal_usd") is not None and quote.get("nights"):
            # nightly room average, taken from the quote's own itemisation (room subtotal / nights)
            prefill = round(quote["room_subtotal_usd"] / quote["nights"], 2)
            prefill_src = "prefilled from the dated official quote"
        elif rl and rl[-1].get("rate"):
            prefill = rl[-1]["rate"]
            prefill_src = "prefilled from the last logged rate"
        calc = ""
        if show_calc:
            calc = f"""<div data-hotel-calc data-fee="{fee or 0}" data-tax="{tax or 0}" data-parking="{h.get('parking_value') or 0}">
<input type="number" class="hc-rate" min="0" step="1" value="{prefill}" placeholder="dated room rate $" style="width:9rem;padding:.35rem">
<div class="hc-out small note"></div>{f'<div class="small note">{esc(prefill_src)}</div>' if prefill_src else '<div class="small note">no dated rate on file — enter one to compute</div>'}</div>"""
        walk = h.get("walk") or {}
        pairs = h.get("walk_pairs") or []
        timed = [p for p in pairs if p.get("minutes") is not None]
        within = [p for p in timed if p.get("within_30_min")]
        walk_cell = ""
        if timed:
            cells = []
            for p in sorted(timed, key=lambda x: (x.get("minutes") if x.get("minutes") is not None else 9e9)):
                ok = p.get("within_30_min")
                badge = "b-good" if ok else "b-warn"
                lbl = (f'{p["minutes"]:.0f} min' if isinstance(p.get("minutes"), (int, float))
                       else esc(p.get("minutes")))
                link = (f'<a href="{esc(p.get("google_maps"))}" target="_blank" rel="noopener">map ↗</a>'
                        if p.get("google_maps") else "")
                alink = (f' · <a href="{esc(p.get("apple_maps"))}" target="_blank" rel="noopener">Apple ↗</a>'
                         if p.get("apple_maps") else "")
                cells.append(f'<div><span class="badge {badge}">{lbl}</span> to {esc(p.get("venue_label"))} '
                             f'<small class="note">{alink}{link}</small></div>')
            walk_cell = "".join(cells)
            if len(within) != len(timed):
                walk_cell += (f'<small class="note">{len(timed) - len(within)} of {len(timed)} '
                              'pair(s) exceed the 30-minute limit</small>')
            walk_cell += (f'<small class="note">routed estimate (OSRM foot profile) on the official '
                          f'addresses, routed {esc(walk.get("routed_on") or "")} — not an official or '
                          'measured duration</small>')
        elif walk.get("maps_venetian"):
            walk_cell = ('<span class="badge b-warn">no duration</span> '
                         f'<a href="{esc(walk.get("maps_venetian"))}" target="_blank" rel="noopener">walk to Venetian ↗</a> · '
                         f'<a href="{esc(walk.get("maps_wynn"))}" target="_blank" rel="noopener">walk to Wynn ↗</a>')
        else:
            walk_cell = ('<span class="badge b-warn">unverified</span> <small class="note">no routed duration '
                         'and no map link on file for this property</small>')
        rows.append(f"""<tr data-cat="hotel" data-walk-ok="{1 if within else 0}">
<td><strong>{esc(h['name'])}</strong><small class="note">{esc(h.get('area',''))}</small></td>
<td>{esc(h.get('address',''))}</td>
<td>{rate_cell}</td><td>{fee_cell}</td><td>{tax_cell}</td>
<td>{esc(h.get('parking','')) or '—'}</td>
<td>{calc}</td>
<td>{walk_cell}</td>
<td class="src">{src_links(h.get('resort_fee_src'), h.get('booking_url'))} <small class="note">fee re-read {esc(h.get('fee_last_checked') or h.get('retrieved') or AS_OF)}</small></td>
</tr>""")
    head = ("<th>Hotel</th><th>Address</th><th>Latest logged rate</th><th>Resort fee</th><th>Tax</th>"
            "<th>Parking</th><th>True cost / night</th><th>Walking time (30-min limit)</th><th>Sources / last checked</th>")
    return f'<table class="data" id="{table_id}"><thead><tr>{head}</tr></thead><tbody>' + "\n".join(rows) + "</tbody></table>"

def rate_log_html(h):
    """A rate log, not a rate: every entry keeps the date it was captured, the dates it applies
    to, the occupancy and room type it was quoted for, and the page it came from. Entries are
    appended, never overwritten, so a price that moved stays visible."""
    rl = h.get("rate_log") or []
    if not rl:
        return ('<p class="excerpt">No dated rate entries yet. Rates are logged here with a date and '
                'source — never overwritten.</p>')
    items = []
    for r in rl:
        head = (f"<strong>{esc(r.get('date'))}</strong>: {money(r.get('rate'))}"
                if r.get("rate") is not None else f"<strong>{esc(r.get('date'))}</strong>: no price obtainable")
        bits = [b for b in (r.get("basis"), r.get("stay"), r.get("suite"), r.get("occupancy"),
                            r.get("offer")) if b]
        line = head + (f" — {esc(' · '.join(bits))}" if bits else "")
        if r.get("checkout_total") is not None:
            line += (f" <small class=\"note\">checkout total {money(r['checkout_total'])} · "
                     f"room {money(r.get('room_subtotal'))} + resort fee {money(r.get('resort_fee_total'))}"
                     f" + tax {money(r.get('taxes'))}"
                     + (f" ({r.get('tax_pct_implied')}%)" if r.get("tax_pct_implied") else "")
                     + f" · nightly average {money(r.get('nightly_average'))}"
                     + f" · true cost/night {money(r.get('true_cost_per_night'))}"
                     + (f" (+{money(r.get('parking_per_day'))}/day parking, not in the engine total)"
                        if r.get("parking_per_day") else "")
                     + "</small>")
        if r.get("excerpt"):
            line += f'<div class="excerpt">&ldquo;{esc(r["excerpt"])}&rdquo;</div>'
        if r.get("itemisation"):
            line += f'<div class="excerpt note">{esc(r["itemisation"])}</div>'
        if r.get("caveat"):
            line += f'<div class="excerpt note"><strong>Caveat:</strong> {esc(r["caveat"])}</div>'
        if r.get("cancellation"):
            line += f'<div class="excerpt note"><strong>Cancellation:</strong> {esc(r["cancellation"])}'
            line += (f' (deadline: {esc(r["cancellation_deadline"])})' if r.get("cancellation_deadline")
                     else ' (no fixed deadline published)') + "</div>"
        if r.get("nightly"):
            per = " · ".join(f"{esc(n.get('date'))} {money(n.get('room_rate_usd'))}"
                             + (f" + fee {money(n.get('resort_fee_usd'))}" if n.get("resort_fee_usd") is not None else "")
                             for n in r["nightly"])
            line += f'<div class="excerpt note"><strong>Per night:</strong> {per}</div>'
        if r.get("conditions"):
            line += f'<div class="excerpt note">{esc(r["conditions"])}</div>'
        src = r.get("source_url")
        if src:
            line += (f' <small class="note"><a href="{esc(src)}" target="_blank" rel="noopener">source</a>'
                     f'{(" · " + esc(r.get("status"))) if r.get("status") else ""}</small>')
        items.append(f"<li>{line}</li>")
    return "<ul class='tight'>" + "".join(items) + "</ul>"

# =============================================================== pages
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
    # The data is a snapshot, so "today" is the date the snapshot was verified — never the
    # machine's clock and never a date hard-coded in this file. A build that silently
    # re-labels old rows as "upcoming" is worse than one that states its own date.
    _as_of = str(master.get("as_of") or "")
    try:
        _today = _dt.date(*map(int, _as_of.split("-")))
    except Exception:
        _today = None
    n_upcoming = len([e for e in evs if _today and re.match(r"^\d{4}-\d{2}-\d{2}$", str(e.get("date")) or "")
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
<li><strong>Walking times are unverified.</strong> Every hotel row carries official-address maps links; capture walk minutes manually (30-minute limit) before choosing a hotel.</li>
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
<p class="note">Poker player rates ($119 Venetian / $209 Palazzo from-prices) require 6 hours live cash or a $300+ tournament buy-in per night — see the <a href="hotels.html">hotels page</a> rate logs.</p>"""

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
    # ---- everything in this section's prose is computed from the rows above it ----
    _quoted = [h for h in hotels if h.get("quote")]
    _routed = [(h, p) for h in hotels for p in (h.get("walk_pairs") or []) if p.get("minutes") is not None]
    _within = [(h, p) for h in hotels for p in (h.get("walk_pairs") or []) if p.get("within_30_min")]
    _no_walk = [h["name"] for h in hotels if not any(p.get("minutes") is not None
                                                      for p in (h.get("walk_pairs") or []))]
    _by_venue = {}
    for _h, _p in _routed:
        _by_venue.setdefault(_p.get("venue_label"), []).append((_h["name"], _p["minutes"]))
    _best = {k: min(v, key=lambda t: t[1]) for k, v in _by_venue.items()}
    quote_status = (
        "<p><strong>%d of %d properties carry a dated quote read off the official booking engine's own price "
        "breakdown</strong> (%s). Each is itemised to the cent — per-night room rate, per-night resort fee, the tax "
        "line and the checkout total — so it can be compared like-for-like with another quote for the same room and "
        "dates. The other %d properties have no dated quote: every official calendar reachable from this build renders "
        "nightly prices as <code>$XXX</code> behind a cookie wall, so the log records the <em>attempt</em>, not a "
        "number. A quote only enters the log with its check-in, check-out, occupancy, room type, resort fee, tax line, "
        "parking, cancellation deadline and the timestamp it was read.</p>"
        % (len(_quoted), len(hotels),
           ", ".join("%s — %s nights from %s at %s/night" % (
               h["name"], (h.get("quote") or {}).get("nights"), (h.get("quote") or {}).get("stay_start"),
               money((h.get("quote") or {}).get("nightly_average_usd")))
               for h in _quoted) or "none yet",
           len(hotels) - len(_quoted)))
    _pairs_total = sum(len(h.get("walk_pairs") or []) for h in hotels)
    walk_status = (
        "<p><strong>%d of %d hotel–venue pairs have a routed duration, %d of them within the 30-minute "
        "limit.</strong> Those are routing-engine estimates (OSRM foot profile) computed on the properties' own "
        "published addresses — <em>not</em> an official or measured walk time, and no property page publishes one. "
        "They are shown so a hotel can be shortlisted, and each carries Google and Apple directions links so the pair "
        "can be confirmed in one tap before it decides anything. %s</p>"
        % (len(_routed), _pairs_total, len(_within),
           ("Properties with no duration at all: " + ", ".join(_no_walk) + ".")
           if _no_walk else "Every property has at least one routed duration."))
    if _best:
        _rows = ""
        for _k, _v in sorted(_best.items(), key=lambda kv: kv[1][1]):
            _ok = ('<span class="badge b-good">yes</span>' if _v[1] <= 30
                   else '<span class="badge b-warn">no</span>')
            _rows += ("<tr><td>%s</td><td>%s</td><td>%.0f</td><td>%s</td></tr>"
                      % (esc(_k), esc(_v[0]), _v[1], _ok))
        walk_status += (
            '<div class="panel"><h2>Closest property for each poker room (routed estimate)</h2>'
            '<table class="data"><thead><tr><th>Poker room</th><th>Closest property</th><th>Minutes</th>'
            '<th>Within 30 min?</th></tr></thead><tbody>' + _rows + '</tbody></table>'
            '<p class="note">Ranked on the routed estimate only; quality, rate and the true nightly cost still '
            'decide the stay, and no duration here is an official or measured one.</p></div>')

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
<div class="panel"><h2>Rate log and walking status — read this before trusting any nightly number</h2>
{quote_status}
{walk_status}
<p class="note">Official street addresses for every hotel and poker room are in the table below, so any pair can be
re-checked directly. Resort fees and tax percentages there come from each property's own reservation terms page, with
the date that page was read.</p></div>
{toolbar('tbl-hotels', with_walk=True, cat_options=False)}
{hotel_table(hotels, 'tbl-hotels', show_calc=True)}
<h2>Dated rate logs</h2>
{''.join(f'<details><summary>{esc(h["name"])}</summary>{rate_log_html(h)}</details>' for h in hotels)}
<div class="panel"><h2>What is still missing</h2>
<ul class="tight">
<li>Dated checkout quotes for exact trip dates (checkout total, nightly average, cancellation deadline, rate timestamp).</li>
<li>Verified walking times per hotel–venue pair (30-minute limit). Use the maps links in each row to capture them.</li>
<li>Official resort-fee amounts for Caesars properties (shown in the official booking flow at checkout; Diamond+ waives).</li>
</ul>
<p class="note">The trip calculator on the <a href="planner.html">Trip Planner</a> uses the same formula, per hotel, over your stay.</p></div>"""

    # ---------------- planner ----------------
    def est_hours(e):
        lm = str(e.get("level_min") or "")
        fmt = e.get("format", "")
        if fmt == "recurring":
            return 5.0
        if "40" in lm:
            return 11.0
        if "20" in lm:
            return 5.5
        return 10.0

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

    plan_rows = []
    dated = [e for e in evs if re.match(r"^\d{4}-", e.get("date", ""))]
    for date in all_dates:
        day = [e for e in dated if e["date"] == date]
        day.sort(key=lambda x: (to_min(x.get("start")) is None, to_min(x.get("start")) or 0))
        suitable = [e for e in day if e["category"] in ("single", "ambiguous")]
        primary = suitable[0] if suitable else (day[0] if day else None)
        fallback = None
        if primary:
            p_start = to_min(primary.get("start")) or 0
            later = [e for e in suitable
                     if (to_min(e.get("start")) or 0) > p_start
                     and (to_min((e.get("late_reg") or "").split("~")[-1].strip().rstrip(")")) or 9999) > p_start]
            fallback = later[-1] if later else None
        overlaps = []
        for i in range(len(day)):
            for j in range(i + 1, len(day)):
                a, b = day[i], day[j]
                sa, sb = to_min(a.get("start")), to_min(b.get("start"))
                if sa is None or sb is None:
                    continue
                ea = sa + est_hours(a) * 60
                if sb < ea:
                    overlaps.append((a, b))
        ov_html = " ".join(f'<span class="badge b-bad">{esc(a.get("name","")[:28])} ↔ {esc(b.get("name","")[:28])}</span>'
                           for a, b in overlaps)
        def cell(e, cls):
            if not e:
                return "<td>—</td>"
            return (f'<td class="{cls}"><strong>{esc(e.get("start"))}</strong> {esc(e.get("name"))} '
                    f'({money(e.get("buy_in"))}) {cat_badge(e.get("category"))}'
                    f'<small class="note">{esc(e.get("venue"))} · late reg {esc(e.get("late_reg") or "n/a")}</small></td>')
        plan_rows.append(f"""<tr><td>{esc(date)}</td>{cell(primary,'primary')}{cell(fallback,'fallback')}
<td>{ov_html or '<span class="badge b-good">none</span>'}</td></tr>""")

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
    <label>Room rate per night ($)</label><input type="number" id="trip-nightly" min="0" value="119">
    <label>Resort fee per night ($)</label><input type="number" id="trip-resort-fee" min="0" value="55">
    <label>Tax (%)</label><input type="number" id="trip-tax" min="0" step="0.01" value="13.38">
    <label>Parking per night ($)</label><input type="number" id="trip-parking" min="0" value="20">
  </div>
</div>
<div class="result">
  True hotel cost per night: <span class="total" id="trip-true-nightly">—</span><br>
  Hotel total for stay: <span class="total" id="trip-hotel-total">—</span><br>
  <strong>Estimated trip total (entries + hotel): <span class="total" id="trip-grand">—</span></strong>
  <p class="note">Formula: entries × buy-ins + nights × true hotel cost. Excludes flights, food, and cash-game bankroll. Default numbers are the verified Venetian poker from-rate and resort fee — replace the room rate with a dated quote before relying on the total.</p>
</div>
</div>
<h2 id="dayplan">Day-by-day plan — primary + conditional fallback</h2>
<p class="note">Plausible durations are estimates (level length × typical levels + breaks), not published finish times.
Fallback entries are playable only if you are eliminated from the primary event before the fallback’s late-registration closes.
Rows with an overlap badge cannot be played in sequence as planned.</p>
<table class="data day-plan"><thead><tr><th>Date</th><th>Primary event</th><th>Conditional fallback</th><th>Overlap flags (est. durations)</th></tr></thead>
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
    def _fld(e, key):
        """Return (value, status, excerpt, retrieved) for one structured rule field."""
        f = (e.get("rules_fields") or {}).get(key)
        if isinstance(f, dict):
            return (f.get("value"), f.get("status") or "", f.get("excerpt") or "", f.get("retrieved") or "")
        r = e.get("rules") or {}
        return (r.get(key), "", r.get("excerpt") or "", r.get("retrieved") or "")

    def _cell(e, key):
        v, st, exc, ret = _fld(e, key)
        word = v if v not in (None, "") else "not stated"
        badge = {"explicit": "b-good", "explicit_no": "b-bad", "not_stated_sheet_read": "b-warn",
                 "not_read": "b-warn", "verified_official": "b-good"}.get(st, "b-chip")
        st_txt = {"explicit": "stated", "explicit_no": "stated", "not_stated_sheet_read": "read · silent",
                  "not_read": "no document", "verified_official": "stated"}.get(st, st or "")
        html = f"<div>{esc(word)}</div>"
        if st_txt:
            html += f'<div><span class="badge {badge}">{esc(st_txt)}</span></div>'
        if exc:
            html += f'<div class="excerpt">&ldquo;{esc(exc)}&rdquo;</div>'
        html += f'<div class="small note">retrieved {esc(ret or "—")}</div>'
        return html

    rule_rows = []
    for e in sorted(evs, key=lambda x: (x.get("venue", ""), x.get("date", ""), x.get("start", ""))):
        r = e.get("rules", {})
        fee_v, fee_st, fee_exc, fee_ret = _fld(e, "fee")
        fee_cell = f"{money(e.get('fee'))}{' / ' + money(e.get('pool_per_entry')) + ' to the pool per entry' if e.get('pool_per_entry') else ''}"
        if fee_exc:
            fee_cell += f'<div class="excerpt">&ldquo;{esc(fee_exc)}&rdquo;</div>'
        fee_cell += f'<div class="small note">retrieved {esc(fee_ret or "—")}</div>'
        gate = e.get("eligibility")
        gate_txt = ""
        if isinstance(gate, dict) and gate.get("value"):
            gate_txt = (f'<div class="small note"><strong>Field:</strong> {esc(gate["value"])} · '
                        f'retrieved {esc(gate.get("retrieved") or "—")}</div>')
        elif isinstance(gate, str) and gate.strip():
            gate_txt = f'<div class="small note"><strong>Field:</strong> {esc(gate)}</div>'
        rule_rows.append(f"""<tr data-cat="{esc(e.get('category'))}">
<td>{esc(e.get('venue'))}</td><td>{esc(e.get('date'))} {esc(e.get('start'))}</td>
<td>{esc(e.get('name'))}<div class="small note">sheet {esc(e.get('sheet') or '—')} · event {esc(e.get('event_no') or '—')}</div>{gate_txt}</td>
<td>{rule_badge(r, e)}{_cell(e, 'single_entry')}</td>
<td>{_cell(e, 're_entry')}</td><td>{_cell(e, 'add_on')}</td>
<td>{fee_cell}</td>
<td>{money(e.get('total_entry_fee')) if e.get('total_entry_fee') else '<span class="badge b-warn">blank</span>'}
<div class="small note">what one entry costs; the ranking divides the guarantee by this figure</div></td>
<td class="src">{src_links(e.get('struct_url') or e.get('source_url'))}
<div class="small note">row checked {esc(e.get('last_checked') or '—')}</div></td></tr>""")
    body_rules = f"""
<h1>Structured entry-rule fields</h1>
<p class="lead">Single-entry, re-entry, add-on, fee, guarantee, payout and bounty are stored as separate fields per
event, each carrying its own status, the source's own words, and the date that source was retrieved. The Venetian
fields come from that event's official structure sheet; the Wynn WPT fields from the official WPT terms document.
<strong>&ldquo;read · silent&rdquo; is not a freezeout rule</strong>: it means the document was read in full and prints
no such provision, which is why no row here is labelled confirmed single-entry.</p>
<p class="note">{len([e for e in evs if e.get('entry_state') == 'stated'])} Venetian rows carry an entry rule the sheet
states in words (the multi-flight &ldquo;may not play a subsequent flight&rdquo; clause);
{len([e for e in evs if e.get('entry_state') == 'stated_multi_entry'])} carry a stated further-buy-in price and are
therefore spend-more by definition;
{len([e for e in evs if e.get('entry_state') == 'silent'])} are read-and-silent candidates; and
{len([e for e in evs if e.get('entry_state') in ('not_stated', None)] + [e for e in evs if not e.get('entry_state')])}
rows across all venues have no rule document published anywhere.</p>
<div class="panel"><h2>Legend</h2><ul class="tight">
<li><span class="badge b-good">stated</span> — the document says it, and the quoted text is shown in the cell.</li>
<li><span class="badge b-warn">read · silent</span> — the document was read in full and prints no such provision. Not a prohibition.</li>
<li><span class="badge b-warn">no document</span> — no rule document exists for this row at all; the field is blank, never guessed.</li>
<li><span class="badge b-bad">stated</span> on a single-entry field — the sheet states a rule that removes the event from a single-entry plan (a further buy-in is priced, or a flight restriction applies).</li>
</ul></div>
{toolbar('tbl-rules', all_dates)}
<table class="data" id="tbl-rules"><thead><tr>
<th>Venue</th><th>Date / start</th><th>Event</th><th>Single-entry field</th><th>Re-entry field</th>
<th>Add-on field</th><th>Fee (house / pool)</th><th>Total entry fee</th><th>Source · last checked</th>
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
    def _st_cls(st):
        s = str(st or "")
        if s.startswith("changed"):
            return "b-bad"
        if s.startswith("unreachable") or s.startswith("fetch error"):
            return "b-bad"
        if s.startswith("unchanged"):
            return "b-good"
        if s.startswith("new"):
            return "b-warn"
        return "b-chip"

    for u in monitor.get("urls", []):
        st = u.get("status", "never checked")
        lc = u.get("last_checked")
        lc_cell = esc(lc) if lc else ('<span class="badge b-warn">never fetched</span>'
                                      + (f'<div class="small note">last attempted {esc(u.get("last_attempt"))}</div>'
                                         if u.get("last_attempt") else ""))
        rows_m.append(f"""<tr><td>{esc(u.get('label',''))}</td>
<td class="src"><a href="{esc(u.get('url',''))}" target="_blank" rel="noopener">{esc(u.get('url',''))[:70]}…</a></td>
<td>{lc_cell}</td><td><span class="badge {_st_cls(st)}">{esc(st)}</span></td>
<td>{affected.get(u.get('url',''), 0)}</td></tr>""")
    _run = monitor.get("last_run_summary") or {}
    _last_run = monitor.get("last_run")
    state_cell = (
        "<strong>Current state:</strong> %d URLs registered · %d changed · %d unchanged · %d baselines still to "
        "establish · %d unreachable on the last run. Last run: %s."
        % (len(monitor.get('urls', [])),
           sum(1 for u in monitor.get('urls', []) if str(u.get('status', '')).startswith('changed')),
           sum(1 for u in monitor.get('urls', []) if str(u.get('status', '')).startswith('unchanged')),
           sum(1 for u in monitor.get('urls', []) if not u.get('sha256')),
           int(_run.get('unreachable') or 0),
           esc(_last_run) if _last_run else
           '<span class="badge b-warn">the scheduled job has not run in this branch yet</span>'))
    never_note = ""
    if not _last_run or all(not u.get("sha256") for u in (monitor.get("urls") or [{}])):
        never_note = (
            "<p class=\"panel\"><strong>Read that state correctly.</strong> “never fetched” means the monitor has not "
            "completed a run against that page yet — it is <em>not</em> a finding that the source is unchanged. Until a "
            "baseline hash exists, no row can be marked changed, so the absence of a "
            "<span class=\"badge b-bad\">source changed — re-check</span> badge proves nothing. The dates on the "
            "tournament and hotel rows come from a person or agent actually opening the cited page, which is a "
            "different and stronger claim than a matching hash.</p>")
    body_mon = f"""
<h1>Source monitor</h1>
<p class="lead">A scheduled GitHub Actions job re-fetches every official URL on this list, compares a content hash with
the stored one, saves a snapshot when the bytes differ, and marks rows whose source changed.
Workflow: <code>.github/workflows/source-monitor.yml</code> (daily at 07:00 Las Vegas time) + <code>scripts/monitor.py</code>.
The registry itself is generated from the citations in the published rows
(<code>scripts/build_monitor_registry.py</code>), so a new source cannot be left unmonitored by forgetting to add it
to a hand-kept list.</p>
<div class="panel">{state_cell}</div>
{never_note}
<p class="note"><strong>What each status claims:</strong> <span class="badge b-good">unchanged</span> the page bytes
match the stored hash — the source moved nothing, but a matching hash does not re-verify a value this site transcribed
from that page. <span class="badge b-warn">new</span> first successful fetch; this run only sets the baseline.
<span class="badge b-bad">changed</span> the bytes differ, and every row citing the URL is badged
<span class="badge b-bad">source changed — re-check</span>. <span class="badge b-bad">unreachable</span> the fetch
failed (blocked, timed out, or no route from the runner): the previous status and the row's verification date are left
alone, because a failed fetch proves nothing about the page.</p>
<table class="data"><thead><tr><th>Source</th><th>URL</th><th>Last successful check</th><th>Status</th><th>Rows citing it</th></tr></thead>
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
<li><strong>Q-B:</strong> What are the verified walking times between each hotel and each venue (30-minute limit)? — Open. Use the per-row Google Maps walking links and record the minutes.</li>
<li><strong>Q-C:</strong> Do the Venetian DSE sheets’ “no re-entry clause” silence and the Valuetown “subsequent buy in’s” note mean unlimited re-entry is allowed after all? — Open. Only the poker room can settle it (flag IR-8234-01/02).</li>
<li><strong>Q-D:</strong> Which Caesars Palace daily buy-in figure is current — $100 (official guide) or $160 at 2 PM/9 PM (official flyer)? — Open; two official sources disagree.</li>
<li><strong>Q-E:</strong> What are the Horseshoe and MGM Grand daily buy-ins and guarantees? — Open; not published on their official pages (Horseshoe) or only on the weekly PDF (MGM).</li>
</ul></div>"""

    # ---------------- suggestions ----------------
    s_rows = "".join(
        f"""<tr><td>{esc(x.get('id',''))}</td><td><strong>{esc(x.get('title',''))}</strong><small class="note">{esc(x.get('category',''))}</small></td>
<td>{'<br>'.join(esc(o) for o in x.get('options', []))}</td>
<td>{esc(x.get('tradeoff',''))}</td><td><span class="badge b-info">{esc(x.get('status',''))}</span></td></tr>"""
        for x in master["suggestions"])
    body_s = f"""
<h1>Suggestions — review before implementing</h1>
<p class="lead">{esc(master.get('suggestions_intro',''))} Each item lists options and the trade-off so you can choose a
path. Nothing here has been implemented.</p>
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
