#!/usr/bin/env python3
"""Build the f0816fab-contributor pages from data/site/*-f0816fab.json plus the
shared walking.json / trip.json datasets.

Contributor-owned outputs (kept separate from the integration dashboard that
scripts/build_site.py generates, per COORDINATION.md file ownership):
  walking.html, trip.html, wpt-terms.html, rate-log.html, archive.html
Every displayed value carries its source id and retrieval date.
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "site")
def load(n):
    return json.load(open(os.path.join(D, n)))

events = load("events-f0816fab.json")
hotels = load("hotels-f0816fab.json")
flags = load("flags-f0816fab.json")
walking = load("walking.json")
trip = load("trip.json")
sources = load("sources.json")
EV = events["events"]
AS_OF = events["as_of"]

def esc(s):
    return html.escape(str(s)) if s is not None else ""

NAV = [("index.html","Dashboard"),("tournaments.html","Tournaments"),("single-entry.html","Single-entry"),
       ("schedule.html","Schedule"),("planner.html","Trip planner"),("hotels.html","Hotels"),
       ("venues.html","Venues"),("ranking.html","Ranking"),("rules.html","Rules"),
       ("walking.html","Walking times (f0816fab)"),("wpt-terms.html","WPT terms (f0816fab)"),
       ("rate-log.html","Rate log (f0816fab)"),("trip.html","Trip plan (f0816fab)"),
       ("questions.html","Questions"),("suggestions.html","Suggestions"),("flagged.html","Flagged"),
       ("sources.html","Sources"),("monitor.html","Monitor"),("archive.html","Archive")]

def page(title, body):
    nav = "".join(f'<a href="{u}">{esc(t)}</a>' for u, t in NAV)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Vegas Poker Trip Planner (f0816fab)</title>
<link rel="stylesheet" href="assets/css/site.css"></head>
<body>
<header><div class="wrap"><h1><a href="index.html">Vegas Poker Trip Planner</a></h1>
<div class="sub">Contributor pages (arena/f0816fab-poker2) — data as of {AS_OF}</div></div></header>
<nav><div class="wrap navrow">{nav}</div></nav>
<main class="wrap">{body}</main>
<footer><div class="wrap">Compiled from official sources only, retrieved {AS_OF}. Unconfirmed values are blank and flagged on the <a href="flagged.html">Flagged</a> page. Sources re-checked by the repository's scheduled monitor.</div></footer>
<script src="assets/js/site.js"></script>
</body></html>"""

def write(rel, title, body):
    open(os.path.join(ROOT, rel), "w").write(page(title, body))

def src(sid):
    s = sources.get(sid)
    return f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(sid)}</a>' if s else esc(sid)

def srcs(ids):
    return " ".join(src(s) for s in (ids or []))

# ---------------- walking.html ----------------
rows = ""
for r in walking["rows"]:
    rows += (f'<tr class="walkrow" data-ok="{"yes" if r["within_30_min"] else "no"}">'
             f'<td>{esc(r["hotel"])}<div class="tiny">{esc(r["hotel_address"])}</div></td>'
             f'<td>{esc(r["venue"])}</td><td>{r["walk_min"]}</td>'
             f'<td>{"✅ ≤30 min" if r["within_30_min"] else "❌ over 30 min"}</td>'
             f'<td><a href="{esc(r["gmaps_link"])}" target="_blank" rel="noopener">Verify on Google Maps</a></td>'
             f'<td>{esc(r.get("as_of") or walking.get("as_of"))}</td></tr>')
write("walking.html", "Walking times", f"""
<h2>Walking times — hotel → venue poker room (f0816fab)</h2>
<p>{esc(walking["method"])}</p>
<div class="filters"><input id="q" class="search" placeholder="Search hotel or venue…">
<label><input type="checkbox" id="only30"> ≤ 30-minute limit only</label></div>
<table class="data" id="walktbl"><thead><tr><th>Hotel</th><th>Venue poker room</th><th>Walk (min, routed estimate)</th><th>30-min rule</th><th>Confirmation</th><th>Last checked</th></tr></thead>
<tbody>{rows}</tbody></table>
<h3>Flagged (this dataset)</h3>
""" + "".join(f'<div class="qitem flag"><h3>[{esc(x["id"])}] {esc(x["item"])} <span class="pill">{esc(x["severity"])}</span></h3><p class="tiny">{esc(x["where"])}</p><p>{esc(x["detail"])}</p></div>'
              for x in flags["items"] if x["id"] in ("F01","F02","F03","F09","F15","F16")))

# ---------------- wpt-terms.html ----------------
wpt_rows = ""
for e in EV:
    if not e["venue"].startswith("Wynn"): continue
    r = e.get("rules") or {}
    re_row = r.get("re_entry") or {}
    if e["classification"] == "excluded":
        badge = '<span class="badge b-excl">excluded</span>'
    else:
        badge = '<span class="badge b-unv">unverified</span>'
    wpt_rows += (f'<tr><td>{esc(e["date"])}<div class="tiny">{esc(e["start"])}</div></td><td>{esc(e["name"])}</td>'
                 f'<td>{"$"+str(e["buy_in"]) if e.get("buy_in") else ""}</td>'
                 f'<td>{"$"+str(e["gtd"]) if e.get("gtd") else ""}</td>'
                 f'<td class="tiny">re-entry: {esc(re_row.get("value"))}<div class="tiny">“{esc(re_row.get("excerpt"))}” [{src(re_row.get("source"))} · retrieved {esc(re_row.get("retrieved"))}]</div></td>'
                 f'<td>{badge}</td>'
                 f'<td class="tiny">{srcs(e.get("sources"))}</td></tr>')
write("wpt-terms.html", "WPT terms audit", f"""
<h2>Wynn WPT World Championship — entry-terms audit (f0816fab)</h2>
<p>The complete WPT structures PDF (8 chunks) was read in full on {AS_OF}. Every event type with published terms allows re-entry (unlimited per flight until level 9–10, or one re-entry per flight for WPT Prime) and is <b>excluded</b> from the single-entry list. Schedule rows whose terms are not published in the official document are <b>unverified</b> (blank rule fields) — 33 rows. Contributor: arena/f0816fab-poker2; retrieval dates on every excerpt.</p>
<div class="filters"><input id="q" class="search" placeholder="Search WPT events…"></div>
<table class="data" id="wpttbl"><thead><tr><th>Date / start</th><th>Event</th><th>Buy-in</th><th>Guarantee</th><th>Entry rules (verbatim excerpt)</th><th>Class</th><th>Sources</th></tr></thead>
<tbody>{wpt_rows}</tbody></table>
<h3>Source discrepancies flagged</h3>
<ul><li>F02: WPT Dec 21 turbo listed at 6 PM in event terms vs 8 PM on the schedule row.</li>
<li>F03: $1,600 NLH $1M terms dated Dec 3–5 vs a schedule row showing $1,600 2-Day $1M on Dec 9.</li>
<li>F04: schedule text 'NIH' where NLH is expected (Dec 13/14/15 rows).</li></ul>""")

# ---------------- rate-log.html ----------------
logrows = ""
for r in hotels["rate_log"]:
    logrows += (f'<tr><td>{esc(r["date"])}</td><td>{esc(r["hotel_id"])}</td><td>{esc(r["kind"])}</td>'
                f'<td>{"$"+str(r["value_usd"]) if r["value_usd"] is not None else ""}</td><td>{esc(r["unit"])}</td>'
                f'<td class="tiny">{esc(r["conditions"])} [{src(r["source"])}]</td></tr>')
write("rate-log.html", "Dated rate log", f"""
<h2>Dated hotel rate log (f0816fab)</h2>
<p>Append-only: one row per observation with retrieval date and conditions. {esc(hotels["tax_note"])}</p>
<p class="formula">{esc(hotels["true_cost_formula"])} {esc(hotels["cancellation_note"])}</p>
<table class="data"><thead><tr><th>Date checked</th><th>Hotel</th><th>Kind</th><th>Value</th><th>Unit</th><th>Conditions & source</th></tr></thead>
<tbody>{logrows}</tbody></table>
<h3>Still blank (flagged)</h3>
<ul><li>Dated room quotes for {"–".join([trip["trip_dates"]["play_days"][0], trip["trip_dates"]["play_days"][-1]])} — dynamic booking engines; capture at booking with checkout total, nightly average, fee, tax, parking, cancellation deadline and timestamp (compare like-for-like; ground truth wins).</li>
<li>Resort fees for Caesars-venue and other non-MGM/Wynn/Venetian hotels — not captured this pass.</li></ul>""")

# ---------------- trip.html ----------------
days_html = ""
for d in trip["day_plan"]:
    p, f = d["primary"], d["fallback"]
    fl = "".join(f'<div class="flagline">⚑ {esc(x)}</div>' for x in d["overlap_flags"])
    ph = (f'<div class="primary"><b>Primary</b> {esc(p["start"])} — {esc(p["name"])} (${p["buy_in"]}) <span class="elig">{esc(p["eligibility"])}</span></div>'
          if p else '<div class="primary muted">No confirmed event this day.</div>')
    fh = (f'<div class="fallback"><b>Conditional fallback</b> {esc(f["start"])} — {esc(f["name"])} (${f["buy_in"]}) — {esc(f["condition"])}</div>' if f else "")
    days_html += f'<div class="daycard"><div class="date">{esc(d["date"])}</div>{ph}{fh}{fl}</div>'
write("trip.html", "Trip plan (f0816fab)", f"""
<h2>Trip plan — fixed by rule (f0816fab)</h2>
<p class="formula">estimated cost of a trip = <b>entries × buy-ins</b> + <b>nights × true hotel cost/night</b><br>
true hotel cost/night = (rate + resort fee) × (1 + 13.38% tax) · tax on the fee is an assumption (F08).</p>
<p><b>Window:</b> {esc(", ".join(trip["trip_dates"]["play_days"]))} — {esc(trip["trip_dates"]["rule"])}</p>
<p>{esc(trip["overlap_method"])}</p>
<div class="days">{days_html}</div>
<h3>Planning assumptions</h3>
<ul><li>Nightly true-cost target <b>${trip["budget_quality_floor"]["nightly_true_cost_target_usd"]}</b>; quality floor <b>{esc(trip["budget_quality_floor"]["quality_floor"])}</b>. {esc(trip["budget_quality_floor"]["note"])}</li>
<li>Dated room rates: none captured (flagged F10) — log them on the <a href="rate-log.html">rate log</a>; the trip planner's calculator accepts them.</li></ul>""")

# ---------------- archive.html ----------------
write("archive.html", "Archive", f"""
<h2>Archived dashboards & contributor pages</h2>
<p>Superseded dashboards preserved unchanged as references (retrieved/compiled {AS_OF} for this contributor's integration pass).</p>
<ul>
<li><a href="archive/index.html">Root dashboard snapshot (pre-integration)</a> — with its <a href="archive/tournaments.html">tournaments</a>, <a href="archive/hotels.html">hotels</a>, <a href="archive/planning.html">planning</a>, <a href="archive/flagged.html">flagged</a> pages.</li>
<li><a href="archive/arena-7a4b09e2/README.md">arena/7a4b09e2-poker2 archives</a></li>
<li><a href="pages/summary.html">pages/ dashboard (session f743ae5a)</a> · <a href="docs/index.html">docs/ dashboard (acd81e67)</a> · <a href="verified/index.html">verified/ dashboard (a22d577b)</a></li>
</ul>
<h3>Contributor note</h3>
<p>Walking/rate-log/WPT-terms/trip-plan pages and <code>data/site/*-f0816fab.json</code>, <code>data/site/walking.json</code>, <code>data/site/trip.json</code> are the arena/f0816fab-poker2 contribution; the main dashboard pages are generated by <code>scripts/build_site.py</code>. Both contributions keep their own source excerpts and retrieval dates.</p>""")
print("f0816fab pages built")
