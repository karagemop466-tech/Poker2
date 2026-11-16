#!/usr/bin/env python3
"""Build the unified dashboard site at the repo root from data/site/*.json.

Usage: python3 scripts/build_site.py
Outputs: index.html, tournaments.html, schedule.html, hotels.html, walking.html,
trip.html, questions.html, suggestions.html, flagged.html, sources.html,
monitor.html, archive.html, venues/*.html, assets/js/data.js
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "site")
def load(n):
    return json.load(open(os.path.join(D, n)))
events = load("events.json"); hotels = load("hotels.json"); walking = load("walking.json")
trip = load("trip.json"); questions = load("questions.json"); suggestions = load("suggestions.json")
flags = load("flags.json"); summary = load("summary.json"); sources = load("sources.json")
monitor = load("monitor.json")

AS_OF = events["as_of"]
EV = events["events"]
def esc(s):
    return html.escape(str(s)) if s is not None else ""

def src_link(sid):
    s = sources.get(sid)
    if not s: return esc(sid)
    return f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(sid)}</a>'

NAV = [("index.html","Summary"),("tournaments.html","Tournaments"),("schedule.html","Day plan"),
       ("trip.html","Trip calculator"),("hotels.html","Hotels & rates"),("walking.html","Walking times"),
       ("venues/venetian.html","Venetian"),("venues/wynn.html","Wynn"),("venues/others.html","Other venues"),
       ("questions.html","Questions"),("suggestions.html","Suggestions"),("flagged.html","Flagged"),
       ("sources.html","Sources"),("monitor.html","Monitor"),("archive.html","Archive")]

def page(title, body, depth=0):
    p = "../" * depth
    nav = "".join(f'<a href="{p}{u}">{esc(t)}</a>' for u, t in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Vegas Poker Trip Planner</title>
<link rel="stylesheet" href="{p}assets/css/site.css"></head>
<body>
<header><div class="wrap"><h1><a href="{p}index.html">Vegas Poker Trip Planner</a></h1>
<div class="sub">Verified single-entry tournaments · hotels · walking times · trip cost — data as of {AS_OF}</div></div></header>
<nav><div class="wrap navrow">{nav}</div></nav>
<main class="wrap">{body}</main>
<footer><div class="wrap">Compiled from official sources only, retrieved {AS_OF}. Unconfirmed values are left blank and flagged.
Follow-up sessions: see <a href="{p}flagged.html">Flagged for Review</a>. Sources are re-checked automatically — see <a href="{p}monitor.html">Monitor</a>.</div></footer>
<script src="{p}assets/js/data.js"></script><script src="{p}assets/js/site.js"></script>
</body></html>"""

def write(rel, title, body, depth=0):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(page(title, body, depth))

# ---------- data.js (embedded data for client-side filters) ----------
datajs = "window.SITE=" + json.dumps({"events": EV, "hotels": hotels, "walking": walking["rows"],
    "trip": trip, "monitor": monitor, "sources": sources, "flags": flags["items"]}) + ";"
open(os.path.join(ROOT, "assets/js/data.js"), "w").write(datajs)

# ---------- index.html ----------
headline = "".join(f'<div class="card"><div class="kpi">{esc(h["value"])}</div><div class="lbl">{esc(h["label"])}</div><div class="note">{esc(h["note"])}</div></div>' for h in summary["headline"])
findings = "".join(f'<div class="finding"><h3>{esc(f["title"])}</h3><p>{esc(f["text"])}</p></div>' for f in summary["findings"])
B = f"""
<section class="hero"><h2>{esc(summary["title"])}</h2><p>{esc(summary["scope"])}</p>
<p class="pill">Trip window (fixed by rule): <b>{esc(trip["trip_dates"]["play_days"][0])} → {esc(trip["trip_dates"]["play_days"][-1])}</b> ·
nightly true-cost target <b>${trip["budget_quality_floor"]["nightly_true_cost_target_usd"]}</b> ·
quality floor <b>{esc(trip["budget_quality_floor"]["quality_floor"])}</b> · walk limit <b>{walking["limit_min"]} min</b></p></section>
<section class="kpis">{headline}</section>
<section><h2>Findings</h2>{findings}</section>
<section><h2>How to use this planner</h2>
<ol class="steps">
<li><b>Fix dates & budget</b> — already set above (adjustable in the <a href="trip.html">trip calculator</a>).</li>
<li><b>Filter to single-entry events</b> — <a href="tournaments.html">Tournaments</a> → toggle “Confirmed single-entry only”. Events with any spend-more mechanic sit in their own section.</li>
<li><b>Compare</b> — guarantee ÷ entry-fee ratio (descriptive, not a forecast), stack, level length and day fit. Bounty/flight events are labeled.</li>
<li><b>Hotels</b> — <a href="hotels.html">Hotels & rates</a> for the dated rate log and true cost/night formula; <a href="walking.html">Walking times</a> for the ≤30-minute test with Google Maps confirmation links.</li>
<li><b>Day plan</b> — <a href="schedule.html">Day plan</a> gives each day a primary event and a conditional evening fallback with overlap flags.</li>
<li><b>Reconfirm before paying</b> — the <a href="monitor.html">Monitor</a> re-checks every official URL daily and flags changed sources; re-verify schedules and rates before any nonrefundable payment.</li>
</ol></section>
"""
write("index.html", "Summary", B)

# ---------- tournaments.html ----------
B = f"""
<h2>Tournaments — all venues</h2>
<p>Every row links to its official source. Classification:
<b>single-entry confirmed</b> = official structure sheet read in full, no re-entry/rebuy/add-on clause;
<b>flagged</b> = sheet read but entry wording unsettled; <b>excluded</b> = spend-more/multi-flight/satellite/team confirmed;
<b>unverified</b> = entry rules not published in official sources (values left blank).</p>
<div class="filters">
<input id="q" class="search" placeholder="Search all tables…" aria-label="Search">
<label>From <input type="date" id="dfrom"></label>
<label>To <input type="date" id="dto"></label>
<label><input type="checkbox" id="seOnly" checked> Confirmed single-entry / freezeout only</label>
<label><input type="checkbox" id="hideGated"> Hide age/gender-gated events</label>
<label>Sort <select id="sort"><option value="date">Date</option><option value="ratio">Guarantee ÷ buy-in</option><option value="buyin">Buy-in (low→high)</option></select></label>
<span id="count" class="pill"></span>
</div>
<h3 id="sec-se">Confirmed single-entry events (incl. bounty / PKO — labeled)</h3>
<div id="tbl-se"></div>
<h3 id="sec-flag">Flagged — ambiguous entry wording</h3>
<div id="tbl-flag"></div>
<h3 id="sec-excl">Excluded — re-entry / rebuy / add-on / multi-flight / satellite / team (spend-more section)</h3>
<div id="tbl-excl"></div>
<h3 id="sec-unv">Unverified — entry terms not published (blank fields flagged)</h3>
<div id="tbl-unv"></div>
<h3>Structured rule fields</h3>
<p>Each event stores single-entry, re-entry, re-buy, add-on and house-fee values separately, with the source excerpt and retrieval date. Expand any row’s “rules” link to see them.</p>
<div id="rulebox"></div>
"""
write("tournaments.html", "Tournaments", B)

# ---------- schedule.html ----------
days_html = ""
for d in trip["day_plan"]:
    p = d["primary"]; f = d["fallback"]
    flags_html = "".join(f'<div class="flagline">⚑ {esc(x)}</div>' for x in d["overlap_flags"])
    ph = (f'<div class="primary"><b>Primary</b> {esc(p["start"])} — {esc(p["name"])} (${p["buy_in"]}) <span class="elig">{esc(p["eligibility"])}</span></div>' if p else '<div class="primary muted">No confirmed event this day.</div>')
    fh = (f'<div class="fallback"><b>Conditional fallback</b> {esc(f["start"])} — {esc(f["name"])} (${f["buy_in"]}) — {esc(f["condition"])}</div>' if f else "")
    days_html += f'<div class="daycard"><div class="date">{esc(d["date"])}</div>{ph}{fh}{flags_html}</div>'
B = f"""
<h2>Day-by-day plan — {esc(trip["trip_dates"]["play_days"][0])} → {esc(trip["trip_dates"]["play_days"][-1])}</h2>
<p>{esc(trip["trip_dates"]["rule"])} {esc(trip["overlap_method"])}</p>
<div class="days">{days_html}</div>
<h3>Full calendar of confirmed events</h3>
<div id="cal"></div>
"""
write("schedule.html", "Day plan", B)

# ---------- trip.html ----------
B = f"""
<h2>Estimated trip cost calculator</h2>
<p class="formula">estimated cost of a trip = <b>entries × buy-ins</b> + <b>nights × true hotel cost/night</b><br>
true hotel cost/night = (room rate + resort fee) × (1 + 13.38% tax) · tax on the fee is an assumption (<a href="flagged.html">F08</a>).</p>
<div class="calc">
<label>Entries planned <input type="number" id="cEntries" value="8" min="0"></label>
<label>Average buy-in ($) <input type="number" id="cBuyin" value="400" min="0" step="10"></label>
<label>Nights <input type="number" id="cNights" value="7" min="1"></label>
<label>Hotel
<select id="cHotel"><option value="">— choose —</option></select>
</label>
<label>Room rate ($/night, before fee & tax) <input type="number" id="cRate" placeholder="log a dated quote" step="1"></label>
<label>Resort fee ($/night) <input type="number" id="cFee" step="1"></label>
<label><input type="checkbox" id="cParking"> Add parking ($20/day at Venetian/Palazzo; elsewhere blank/flagged)</label>
<div id="cOut" class="calcOut"></div>
</div>
<h3>Planning assumptions (fixed for this plan)</h3>
<ul>
<li>Trip dates: <b>{esc(", ".join(trip["trip_dates"]["play_days"]))}</b> — {esc(trip["trip_dates"]["rule"])}</li>
<li>Nightly true-cost target: <b>${trip["budget_quality_floor"]["nightly_true_cost_target_usd"]}</b>; quality floor: <b>{esc(trip["budget_quality_floor"]["quality_floor"])}</b>. {esc(trip["budget_quality_floor"]["note"])}</li>
<li>Dated room rates are not captured (dynamic booking engines) — enter a logged rate above; the dated log is on the <a href="hotels.html">Hotels & rates</a> page.</li>
</ul>
"""
write("trip.html", "Trip calculator", B)

# ---------- hotels.html ----------
rows = ""
for h in hotels["rows"]:
    fee = h["resort_fee"] if h["resort_fee"] is not None else ""
    rows += (f'<tr data-id="{esc(h["id"])}"><td><b>{esc(h["name"])}</b><div class="tiny">{esc(h["address"])}</div></td>'
             f'<td>{esc(h["quality_class"])}</td>'
             f'<td>{esc(h["resort_fee_txt"])}</td>'
             f'<td>{esc(h["parking"])}</td>'
             f'<td><a href="{esc(h["booking_url"])}" target="_blank" rel="noopener">Official booking</a></td>'
             f'<td class="tiny">{esc(h["notes"])}</td></tr>')
logrows = ""
for r in hotels["rate_log"]:
    logrows += (f'<tr><td>{esc(r["date"])}</td><td>{esc(r["hotel_id"])}</td><td>{esc(r["kind"])}</td>'
                f'<td>{"$"+str(r["value_usd"]) if r["value_usd"] is not None else ""}</td><td>{esc(r["unit"])}</td>'
                f'<td class="tiny">{esc(r["conditions"])} [{src_link(r["source"])}]</td></tr>')
B = f"""
<h2>Hotels & rates</h2>
<p><b>True cost/night = rate + resort fee + 13.38% tax</b> — computed in the <a href="trip.html">trip calculator</a>. {esc(hotels["tax_note"])}</p>
<p>{esc(hotels["true_cost_formula"])} {esc(hotels["cancellation_note"])}</p>
<h3>Hotel table</h3>
<div class="filters"><input id="q" class="search" placeholder="Search hotels…"></div>
<table class="data" id="hoteltbl"><thead><tr><th>Hotel</th><th>Quality class</th><th>Resort fee (official)</th><th>Parking</th><th>Booking</th><th>Notes</th></tr></thead>
<tbody>{rows}</tbody></table>
<h3>Dated rate log (append-only — one row per observation)</h3>
<p>Rates are kept as a dated log, not a single value. New observations are appended with their retrieval date and conditions.</p>
<table class="data"><thead><tr><th>Date checked</th><th>Hotel</th><th>Kind</th><th>Value</th><th>Unit</th><th>Conditions & source</th></tr></thead>
<tbody>{logrows}</tbody></table>
<h3>What is still blank (and why)</h3>
<ul>
<li>Dated room rates for {esc(trip["trip_dates"]["play_days"][0])}–{esc(trip["trip_dates"]["play_days"][-1])} — booking engines price dynamically; capture at booking into the rate log with checkout total, nightly average, fee, tax, parking, cancellation deadline and timestamp (compare like-for-like).</li>
<li>Caesars/Horseshoe/Flamingo/LINQ/Cromwell/Paris/PH/Park MGM/Resorts World/Westgate/NYNY/Mandalay/Golden Nugget resort fees — not captured from official pages in this pass (flagged).</li>
<li>Cancellation deadlines — rate-specific; captured only at booking.</li>
</ul>
"""
write("hotels.html", "Hotels & rates", B)

# ---------- walking.html ----------
wrows = ""
for r in walking["rows"]:
    ok = "yes" if r["within_30_min"] else "no"
    wrows += (f'<tr class="walkrow" data-ok="{ok}" data-hotel="{esc(r["hotel"])}" data-venue="{esc(r["venue"])}">'
              f'<td>{esc(r["hotel"])}<div class="tiny">{esc(r["hotel_address"])}</div></td>'
              f'<td>{esc(r["venue"])}</td><td>{r["walk_min"]}</td>'
              f'<td>{"✅ ≤30 min" if r["within_30_min"] else "❌ over 30 min"}</td>'
              f'<td><a href="{esc(r["gmaps_link"])}" target="_blank" rel="noopener">Verify on Google Maps</a></td></tr>')
B = f"""
<h2>Walking times — hotel → venue poker room</h2>
<p>{esc(walking["method"])}</p>
<div class="filters"><input id="q" class="search" placeholder="Search hotel or venue…">
<label><input type="checkbox" id="only30"> ≤ 30-minute limit only</label></div>
<table class="data" id="walktbl"><thead><tr><th>Hotel</th><th>Venue poker room</th><th>Walk (min, routed estimate)</th><th>30-min rule</th><th>Confirmation</th></tr></thead>
<tbody>{wrows}</tbody></table>
"""
write("walking.html", "Walking times", B)

# ---------- venues ----------
def ev_rows(items):
    out = ""
    for e in items:
        ratio = f'{e["gtd"]/e["buy_in"]:.1f}×' if (e.get("gtd") and e.get("buy_in")) else ""
        out += (f'<tr><td>{esc(e["date"])} {esc(e["start"])}</td><td>{esc(e["name"])}</td>'
                f'<td>{e["buy_in"] or ""}</td><td>{e.get("house_fee") or ""}</td><td>{e.get("gtd") or ""}</td>'
                f'<td>{ratio}</td><td>{esc(e["classification"])}</td>'
                f'<td>{" ".join(src_link(s) for s in e.get("sources", []))}</td>'
                f'<td class="tiny">{esc(e.get("note") or "")}</td></tr>')
    return out

for slug, vname, filt in [("venetian","The Venetian", lambda e: e["venue"] == "The Venetian"),
                          ("wynn","Wynn Las Vegas", lambda e: e["venue"].startswith("Wynn")),
                          ("others","Other venues (Caesars, MGM)", lambda e: not e["venue"].startswith("Wynn") and e["venue"] != "The Venetian")]:
    items = [e for e in EV if filt(e)]
    hot = ""
    if slug == "venetian":
        hot = '<h3>Hotels on site / closest</h3><p>The Venetian and The Palazzo are the tournament venue itself (0 min). See <a href="../walking.html">Walking times</a> for all pairs.</p>'
    elif slug == "wynn":
        hot = '<h3>Hotels on site / closest</h3><p>The Wynn poker room is inside Encore (official WPT terms). Wynn and Encore are on site; Resorts World is ~10 min north. See <a href="../walking.html">Walking times</a>.</p>'
    else:
        hot = '<h3>Hotels nearby</h3><p>See <a href="../walking.html">Walking times</a> for hotel–venue pairs and the 30-minute rule.</p>'
    B = f"""<h2>{esc(vname)} — events & hotels</h2>
<div class="filters"><input id="q" class="search" placeholder="Search events…"></div>
<table class="data"><thead><tr><th>Date / start</th><th>Event</th><th>Buy-in</th><th>House fee</th><th>Guarantee</th><th>Gtd ÷ buy-in</th><th>Class</th><th>Sources</th><th>Notes</th></tr></thead>
<tbody>{ev_rows(items)}</tbody></table>{hot}"""
    write(f"venues/{slug}.html", vname, B, depth=1)

# ---------- questions / suggestions / flagged / sources / monitor / archive ----------
def _qlinks(lst):
    return " ".join('<a href="%s" target="_blank">source</a>' % esc(s) for s in lst)
q = "".join('<div class="qitem"><h3>[%s] %s</h3>' % (esc(x["id"]), esc(x["question"])) +
            '<p><b>Status:</b> %s</p><p>%s</p>' % (esc(x["status"]), esc(x["answer"])) +
            '<p><b>How to find the missing part:</b> %s</p>' % esc(x["how_to_find"]) +
            '<p class="tiny">%s</p></div>' % _qlinks(x.get("sources", []))
            for x in questions["items"])
write("questions.html", "Questions", f"<h2>Questions, information and answers</h2><p>{esc(questions['intro'])}</p>{q}")

s = "".join(f'<div class="qitem"><h3>[{esc(x["id"])}] {esc(x["title"])} <span class="pill">{esc(x["category"])} · impact: {esc(x["impact"])}</span></h3>'
            f'<ul>{"".join(f"<li>{esc(o)}</li>" for o in x["options"])}</ul>'
            f'<p><b>Trade-off:</b> {esc(x["tradeoff"])}</p><p class="pill">{esc(x["status"])}</p></div>'
            for x in suggestions["items"])
write("suggestions.html", "Suggestions", f"<h2>Suggestions — review before implementing</h2><p>{esc(suggestions['intro'])}</p>{s}")

f = "".join(f'<div class="qitem flag"><h3>[{esc(x["id"])}] {esc(x["item"])} <span class="pill">{esc(x["severity"])}</span></h3>'
            f'<p class="tiny">Where: {esc(x["where"])}</p><p>{esc(x["detail"])}</p></div>' for x in flags["items"])
write("flagged.html", "Flagged for Review", f"<h2>Flagged for Review</h2><p>Irregularities and unverified items published for post-launch review. These do not block the site; each names the discovery step in the <a href='questions.html'>Questions</a> or <a href='suggestions.html'>Suggestions</a> pages.</p>{f}")

srows = "".join(f'<tr><td>{esc(k)}</td><td><a href="{esc(v["url"])}" target="_blank" rel="noopener">{esc(v["label"])}</a></td><td>{esc(v["publisher"])}</td><td>{esc(v["type"])}</td></tr>' for k, v in sorted(sources.items()))
write("sources.html", "Sources", f"<h2>Source registry</h2><p>Every displayed value links here. Official sources first; routing/geocoding services used for walking times are labeled as such.</p><table class='data'><thead><tr><th>ID</th><th>Source</th><th>Publisher</th><th>Type</th></tr></thead><tbody>{srows}</tbody></table>")

mrows = "".join(f'<tr><td>{esc(r["label"])}</td><td class="tiny"><a href="{esc(r["url"])}" target="_blank" rel="noopener">{esc(r["url"])[:70]}…</a></td>'
                f'<td>{esc(r["last_checked"] or "pending first scheduled run")}</td><td>{esc(r["status"])}</td><td>{"CHANGED" if r["changed"] else ""}</td></tr>' for r in monitor["rows"])
write("monitor.html", "Source monitor", f"""<h2>Automatic source re-check</h2>
<p>{esc(monitor["schedule"])}. {esc(monitor["note"])} Rows whose source content changed since the previous run are marked <b>CHANGED</b> here and on the affected tables.</p>
<table class="data"><thead><tr><th>Source</th><th>URL</th><th>Last checked</th><th>Status</th><th>Change</th></tr></thead><tbody>{mrows}</tbody></table>""")

write("archive.html", "Archive", """<h2>Archived dashboards (prior sessions)</h2>
<p>Earlier parallel sessions built separate dashboards. They are preserved here unchanged and superseded by this unified site (data merged and re-verified line by line).</p>
<ul>
<li><a href="archive/index.html">Root dashboard as of 2026-11-16 (pre-integration)</a> — with its <a href="archive/tournaments.html">tournaments</a>, <a href="archive/hotels.html">hotels</a>, <a href="archive/planning.html">planning</a>, <a href="archive/flagged.html">flagged</a> pages.</li>
<li><a href="pages/summary.html">pages/ dashboard (session f743ae5a)</a> — category pages under /pages/.</li>
<li><a href="docs/index.html">docs/ dashboard (session acd81e67)</a> — served under /docs/.</li>
<li><a href="verified/index.html">verified/ dashboard (session a22d577b)</a> — served under /verified/.</li>
</ul>""")
print("site built")
