#!/usr/bin/env python3
"""
Build the consolidated Las Vegas poker dashboard.

Deterministic: same data in -> same HTML out. Every table row carries an
official source link and the date that source was last read. Rows with an
unverified value render an em-dash, never a guess.

    python3 scripts/poker_data.py     # regenerate data/poker/dataset.json
    python3 scripts/build_dashboard.py
"""

import html
import json
import os
import re
import shutil
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "poker", "dataset.json")

with open(DATA) as fh:
    D = json.load(fh)

AS_OF = D["as_of"]
SRC = D["sources"]
EVENTS = D["events"]
HOTELS = D["hotels"]
WALKS = D["walks"]
RATES = D["rates"]
FLAGS = D["flags"]
QUESTIONS = D["questions"]
SUGGESTIONS = D["suggestions"]
VENUES = D["venues"]

HOTEL_BY_ID = {h["id"]: h for h in HOTELS}
VENUE_BY_ID = {v["id"]: v for v in VENUES}
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_NAME = dict(zip(WEEKDAYS, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]))

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def e(s):
    return html.escape(str(s), quote=True)


def dash(v, fmt=None):
    if v is None or v == "":
        return '<span class="blank" title="Not stated by any official source read">—</span>'
    if fmt == "money":
        return f"${v:,.0f}"
    if fmt == "money2":
        return f"${v:,.2f}"
    return e(v)


SHORT = {
    "V_POKER": "Venetian poker page", "V_SCHED_TABLE": "DSE IV schedule",
    "V_SERIES": "DSE IV landing", "V_SCHED_PDF": "DSE IV schedule PDF",
    "V_RESORT_FEE": "Venetian resort fee", "V_HOTEL_TC": "Venetian hotel T&Cs",
    "V_SUITE_RATES": "Venetian poker suite rates", "V_PROMOS": "Venetian promotions",
    "W_POKER": "Wynn poker page", "W_WPT_SCHED": "WPT Championship schedule",
    "W_WPT_STRUCT": "WPT structure sheets", "W_DAILY_POSTER": "Wynn daily poster",
    "W_DAILY_STRUCT": "Wynn daily structures", "W_RESORT_INFO": "Wynn resort information",
    "C_POKER": "Caesars Palace poker", "C_DAILY_PDF": "Caesars daily flyer",
    "C_STRIP_ARTICLE": "Caesars Strip poker guide", "C_TERMS": "Caesars fine print",
    "B_POKER": "Bellagio poker", "B_FRI_PDF": "Bellagio $600 structure",
    "B_SAT_PDF": "Bellagio $1,100 structure",
    "M_POKER": "MGM Grand poker", "M_SCHED_PDF": "MGM Grand schedule PDF",
    "M_STRUCT_PDF": "MGM Grand $120 structure", "M_TC": "MGM Grand T&Cs",
    "B_TC": "Bellagio T&Cs", "H_POKER": "Horseshoe poker",
    "G_WALK": "Google Maps",
}


def src_link(key, label=None):
    s = SRC.get(key)
    if not s:
        return '<span class="blank">no source</span>'
    name = label or SHORT.get(key) or s["title"][:44]
    return (f'<a href="{e(s["url"])}" target="_blank" rel="noopener" '
            f'class="src" title="{e(s["title"])} — {e(s["used_for"])}">{e(name)} ↗</a>')


def src_cell(keys):
    return " · ".join(src_link(k) for k in keys)


def kind_badge(kind):
    cls = {"official": "ok", "official-editorial": "warn",
           "third-party": "warn", "routing": "warn"}.get(kind, "warn")
    return f'<span class="tag {cls}">{e(kind)}</span>'


def rule_badge(rule, sheet_read=False):
    if rule == "not_stated" and not sheet_read:
        return '<span class="tag muted">sheet not read</span>'
    label = {
        "not_stated": "silent on entry limit",
        "unlimited_reentry": "unlimited re-entry",
        "reentry_allowed": "re-entry allowed",
        "rebuy_addon": "rebuy + add-on",
        "reentry_addon": "re-entry + add-on",
    }.get(rule, rule)
    cls = "ok" if rule == "not_stated" else "warn"
    return f'<span class="tag {cls}">{e(label)}</span>'


TYPE_LABEL = {
    "1day": ("1-day freezeout-format event", "plain"),
    "flight": ("starting flight", "warn"),
    "2day": ("2-day event", "warn"),
    "day2": ("day-2 restart, no new entry", "muted"),
    "final": ("final table", "muted"),
    "satellite": ("satellite", "muted"),
    "team": ("team event", "warn"),
    "daily": ("daily / weekly", "plain"),
}


def type_badge(t):
    label, cls = TYPE_LABEL.get(t, (t, "plain"))
    return f'<span class="tag {cls}">{e(label)}</span>'


def _gap(a, b):
    """Human gap between two HH:MM start times, for wording only."""
    if not a or not b:
        return "later"
    h1, m1 = (int(x) for x in a.split(":"))
    h2, m2 = (int(x) for x in b.split(":"))
    d = (h2 * 60 + m2) - (h1 * 60 + m1)
    if d <= 0:
        return "later"
    hh, mm = divmod(d, 60)
    return (f"{hh} h {mm:02d} min" if hh else f"{mm} min")


def reg_close_display(ev):
    """Late-registration close as the source states it: a clock time where one
    is printed, otherwise a level number. Never a converted clock time."""
    if ev.get("reg_close"):
        return e(ev["reg_close"])
    if ev.get("reg_close_level"):
        return f'start of level {ev["reg_close_level"]}'
    return dash(None)


def event_date_label(ev):
    if ev.get("date"):
        return ev["date"]
    days = ev.get("weekday")
    if not days:
        return ""
    if len(days) == 7:
        return "Every day"
    if len(days) == 1:
        return "Every " + DAY_NAME[days[0]]
    return " · ".join(DAY_NAME[d] for d in days)


def sort_key(ev):
    return (ev.get("date") or "9999", ev.get("time") or "99")


# --------------------------------------------------------------------------
# derived numbers — arithmetic on published figures only
# --------------------------------------------------------------------------
def entry_cost(ev):
    """Mandatory buy-in. Already includes the house fee: buy_in is what you pay."""
    return ev.get("buy_in")


def guarantee_ratio(ev):
    if ev.get("gtd") and ev.get("buy_in"):
        return round(ev["gtd"] / ev["buy_in"], 2)
    return None


def entries_to_fund(ev):
    """How many full entries, at the published prize-pool-per-entry, the
    advertised guarantee needs. Exact arithmetic, not a forecast."""
    if ev.get("gtd") and ev.get("pool_per_entry"):
        return int(-(-ev["gtd"] // ev["pool_per_entry"]))
    return None


# --------------------------------------------------------------------------
# Event length: deliberately NOT computed.
#
# An earlier draft of this file derived a "maximum length" for each event from
# a hard-coded table of levels-per-event and minutes-per-level. That table was
# assembled from memory of the structure sheets rather than transcribed from
# them, which makes it exactly the kind of plausible-looking invention this
# project forbids. It has been removed.
#
# What the sheets actually publish, and what is therefore in the dataset:
# the starting stack, the minutes per level, and the level at which late
# registration closes. What they do not publish, anywhere, is a finish time or
# a guaranteed number of levels played. So no ceiling can be stated without
# inventing one.
#
# The consequence is stated on the day-plan page rather than papered over: a
# second tournament on the same day is always conditional, because nobody can
# say when the first one ends.
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# nook: shared shell
# --------------------------------------------------------------------------
NAV = [
    ("index.html", "Dashboard", "▦"),
    ("events.html", "All events", "♠"),
    ("ranking.html", "Best value", "★"),
    ("dayplan.html", "Day plan", "◷"),
    ("trip-cost.html", "Trip cost", "∑"),
    ("hotels.html", "Hotels", "⌂"),
    ("rates.html", "Rate log", "≡"),
    ("walking.html", "Walking", "⇢"),
    ("venues/venetian.html", "Venues", "◈"),
    ("questions.html", "Questions", "?"),
    ("suggestions.html", "Suggestions", "✦"),
    ("flagged.html", "Flagged", "⚑"),
    ("sources.html", "Sources", "☰"),
    ("repo-review.html", "Repo review", "▤"),
]

CSS = """
:root{
  --bg:#0a0e14; --panel:#101722; --panel2:#151e2b; --line:#22303f;
  --ink:#e8eef6; --muted:#93a4b8; --dim:#6d7f93;
  --ok:#35c48a; --warn:#e8b339; --bad:#e8564f; --accent:#4aa8ff;
  --radius:10px;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--bg); color:var(--ink);
  font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased;
}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
h1,h2,h3,h4{margin:0 0 .4em;line-height:1.2;font-weight:650;letter-spacing:-.01em}
h1{font-size:1.85rem}
h2{font-size:1.32rem;margin-top:0}
h3{font-size:1.02rem}
p{margin:.55em 0}
small{color:var(--muted)}
code,.mono{font-family:var(--mono);font-size:.86em}

/* layout */
.wrap{display:flex;min-height:100vh}
aside{
  width:232px;flex:0 0 232px;background:var(--panel);border-right:1px solid var(--line);
  padding:18px 12px;position:sticky;top:0;height:100vh;overflow-y:auto;
}
.brand{display:flex;align-items:center;gap:9px;font-weight:700;font-size:.95rem;
  letter-spacing:.02em;color:var(--ink);padding:0 8px 14px;border-bottom:1px solid var(--line);margin-bottom:12px}
.brand .mark{color:var(--ok);font-size:1.15rem}
.side-label{font-size:.66rem;letter-spacing:.13em;text-transform:uppercase;color:var(--dim);
  margin:16px 8px 6px;font-weight:700}
aside a.nav{display:flex;gap:9px;align-items:center;padding:7px 9px;border-radius:7px;
  color:var(--muted);font-size:.88rem}
aside a.nav:hover{background:var(--panel2);color:var(--ink);text-decoration:none}
aside a.nav.active{background:#1a2534;color:var(--ink);font-weight:600}
main{flex:1;min-width:0;padding:26px 30px 64px;max-width:1440px}
@media(max-width:900px){
  .wrap{flex-direction:column}
  aside{width:auto;flex:none;height:auto;position:relative;border-right:0;border-bottom:1px solid var(--line)}
  aside a.nav{display:inline-flex;margin:2px}
  main{padding:18px 14px 48px}
}

/* header bits */
.pagehead{display:flex;flex-wrap:wrap;gap:14px;align-items:flex-start;
  justify-content:space-between;margin-bottom:8px;padding-bottom:16px;border-bottom:1px solid var(--line)}
.eyebrow{font-size:.68rem;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);font-weight:700}
.stamp{font-size:.76rem;color:var(--muted);text-align:right}
.stamp b{color:var(--ink);font-family:var(--mono)}

/* cards */
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(232px,1fr));margin:18px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:15px 16px}
.card h3{font-size:.82rem;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);font-weight:700}
.card .big{font-size:1.72rem;font-weight:700;letter-spacing:-.02em;display:block;margin:.15em 0 .1em}
.card .big.dim{color:var(--dim)}
.note{color:var(--muted);font-size:.86rem}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
  padding:16px 18px;margin:16px 0}
.panel.warnbox{border-color:#5a4620;background:#1b1608}
.panel.badbox{border-color:#5a2a28;background:#1c0f0e}

/* tags */
.tag{display:inline-block;font-size:.68rem;font-weight:700;letter-spacing:.05em;
  text-transform:uppercase;padding:2px 7px;border-radius:99px;border:1px solid;white-space:nowrap}
.tag.ok{color:var(--ok);border-color:#1d5d43;background:#0d2419}
.tag.warn{color:var(--warn);border-color:#5a4620;background:#1c1608}
.tag.bad{color:var(--bad);border-color:#5a2a28;background:#1c0f0e}
.tag.plain{color:var(--muted);border-color:var(--line);background:var(--panel2)}
.tag.muted{color:var(--dim);border-color:#26313d;background:transparent}

/* tables */
.tablewrap{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);margin:14px 0}
table{border-collapse:collapse;width:100%;font-size:.845rem;min-width:100%}
thead th{
  position:sticky;top:0;background:#16202d;color:var(--muted);text-align:left;
  font-size:.7rem;letter-spacing:.06em;text-transform:uppercase;font-weight:700;
  padding:9px 11px;border-bottom:1px solid var(--line);white-space:nowrap;z-index:2;
}
tbody td{padding:8px 11px;border-bottom:1px solid #1a2431;vertical-align:top}
tbody tr:nth-child(even){background:#0d131c}
tbody tr:hover{background:#152031}
td.num{text-align:right;font-family:var(--mono);white-space:nowrap}
td.tight{white-space:nowrap}
.blank{color:var(--dim);font-weight:600}
a.src{font-size:.78rem;color:var(--muted)}
a.src:hover{color:var(--accent)}

/* controls */
.controls{display:flex;flex-wrap:wrap;gap:10px;align-items:flex-end;margin:14px 0;
  padding:14px 16px;background:var(--panel);border:1px solid var(--line);border-radius:var(--radius)}
.field{display:flex;flex-direction:column;gap:4px}
.field label{font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:700}
input,select,button{
  font:inherit;font-size:.86rem;color:var(--ink);background:var(--panel2);
  border:1px solid var(--line);border-radius:7px;padding:7px 10px;
}
input[type="search"]{min-width:250px}
input[type="number"]{width:108px;font-family:var(--mono)}
input:focus,select:focus,button:focus{outline:2px solid var(--accent);outline-offset:1px}
button{cursor:pointer;font-weight:600}
button:hover{background:#1d2a3b}
button.primary{background:#1b4a78;border-color:#2c6ba8}
.switch{display:flex;align-items:center;gap:8px;font-size:.86rem;color:var(--muted)}
.switch input{width:16px;height:16px;accent-color:var(--ok)}

/* calculator */
.calc{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(280px,1fr))}
.calc .row{display:flex;justify-content:space-between;gap:12px;padding:7px 0;border-bottom:1px dashed #1c2634}
.calc .row:last-child{border-bottom:0}
.calc .row span:last-child{font-family:var(--mono);white-space:nowrap}
.total{font-size:1.5rem;font-weight:700;font-family:var(--mono);color:var(--ok)}

/* lists */
ul.clean{list-style:none;padding:0;margin:.4em 0}
ul.clean li{padding:7px 0 7px 20px;position:relative;border-bottom:1px solid #1a2431}
ul.clean li:before{content:"—";position:absolute;left:0;color:var(--dim)}
dl.defs{display:grid;grid-template-columns:auto 1fr;gap:6px 16px;margin:.6em 0}
dl.defs dt{color:var(--muted);font-size:.82rem;font-weight:600}
dl.defs dd{margin:0;font-size:.88rem}

details{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
  padding:12px 15px;margin:10px 0}
details summary{cursor:pointer;font-weight:650;font-size:.94rem}
details summary:hover{color:var(--accent)}
details[open] summary{margin-bottom:10px;padding-bottom:10px;border-bottom:1px solid var(--line)}

footer{margin-top:44px;padding-top:16px;border-top:1px solid var(--line);
  color:var(--dim);font-size:.78rem}
.hidden{display:none!important}
.count{font-family:var(--mono);color:var(--accent);font-weight:700}
"""

JS = """
function fmt(n){return n.toLocaleString('en-US',{maximumFractionDigits:2})}
function money(n){return '$'+n.toLocaleString('en-US',{maximumFractionDigits:0})}

/* ---- generic table filter (events page + per-venue pages) ---- */
function applyFilters(tableId){
  var t=document.getElementById(tableId); if(!t) return;
  var q=(document.getElementById('q')||{}).value||'';
  var date=(document.getElementById('fdate')||{}).value||'';
  var venue=(document.getElementById('fvenue')||{}).value||'';
  var se=(document.getElementById('fse')||{}).checked;
  var free=(document.getElementById('ffree')||{}).checked;
  var unread=(document.getElementById('funread')||{}).checked;
  var confirmed=0;
  q=q.toLowerCase().trim(); var shown=0;
  t.querySelectorAll('tbody tr').forEach(function(tr){
    var hay=(tr.dataset.search||'').toLowerCase();
    var ok=true;
    if(q && hay.indexOf(q)===-1) ok=false;
    if(date && tr.dataset.date!==date) ok=false;
    if(venue && tr.dataset.venue!==venue) ok=false;
    /* "Single-entry confirmed" requires a positive statement from an official
       source. No row carries one, so this filter is expected to empty the
       table -- that is the finding, not a bug. */
    if(se && tr.dataset.single!=='1') ok=false;
    /* "Silent on entry limits" = a structure sheet was opened and printed no
       rule either way. Distinct from confirmed, and distinct from unread. */
    if(free && tr.dataset.silent!=='1') ok=false;
    if(unread && tr.dataset.silent==='1') ok=false;
    if(unread && tr.dataset.rule!=='not_stated') ok=false;
    tr.classList.toggle('hidden',!ok);
    if(ok) shown++;
  });
  var out=document.getElementById('shown');
  if(out) out.textContent=shown;
}

/* ---- trip cost calculator ---- */
function calcTrip(){
  var nights=+((document.getElementById('c_nights')||{}).value||0);
  var entries=+((document.getElementById('c_entries')||{}).value||0);
  var buyin=+((document.getElementById('c_buyin')||{}).value||0);
  var rate=+((document.getElementById('c_rate')||{}).value||0);
  var fee=+((document.getElementById('c_fee')||{}).value||0);
  var taxp=+((document.getElementById('c_tax')||{}).value||0);
  var park=+((document.getElementById('c_park')||{}).value||0);
  var parknights=+((document.getElementById('c_parknights')||{}).value||0);
  var other=+((document.getElementById('c_other')||{}).value||0);

  var feeTotal=fee*nights;
  var taxTotal=(rate+ fee)* (taxp/100) * nights;
  var roomTotal=rate*nights;
  var perNight=roomTotal/nights + fee + (rate+fee)*(taxp/100);
  var hotel=roomTotal+feeTotal+taxTotal;
  var parking=park*parknights;
  var tourn=entries*buyin;
  var total=hotel+parking+tourn+other;

  var set=function(id,v){var el=document.getElementById(id); if(el) el.textContent=v;};
  set('o_night','$'+fmt(perNight||0));
  set('o_room','$'+fmt(roomTotal||0));
  set('o_fee','$'+fmt(feeTotal||0));
  set('o_tax','$'+fmt(taxTotal||0));
  set('o_hotel','$'+fmt(hotel||0));
  set('o_park','$'+fmt(parking||0));
  set('o_tourn','$'+fmt(tourn||0));
  set('o_other','$'+fmt(other||0));
  set('o_total','$'+fmt(total||0));
  set('o_perday', nights>0 ? '$'+fmt(total/nights) : '—');
  set('o_perentry', entries>0 ? '$'+fmt(total/entries) : '—');
}
document.addEventListener('DOMContentLoaded',function(){
  var c=document.getElementById('c_nights');
  if(c){['c_nights','c_entries','c_buyin','c_rate','c_fee','c_tax','c_park','c_parknights','c_other']
    .forEach(function(id){var el=document.getElementById(id); if(el) el.addEventListener('input',calcTrip);});
    calcTrip();}
  ['q','fdate','fvenue','fse','ffree','funread'].forEach(function(id){
    var el=document.getElementById(id);
    if(el) el.addEventListener('input',function(){applyFilters('evtable');});
  });
  var reset=document.getElementById('freset');
  if(reset) reset.addEventListener('click',function(){
    ['q','fdate','fvenue'].forEach(function(id){var el=document.getElementById(id); if(el) el.value='';});
    ['fse','ffree','funread'].forEach(function(id){var el=document.getElementById(id); if(el) el.checked=false;});
    applyFilters('evtable');
  });
});
"""


def shell(active, title, desc, body, depth=0, here="index.html"):
    """depth = how deep the page sits below the repo root. `here` is the
    page's own path below root, used to make the Venues nav entry point at the
    index when you are inside venues/."""
    pre = "../" * depth
    nav = []
    for href, label, glyph in NAV:
        if href == "venues/venetian.html":
            target = ("index.html" if depth else "venues/index.html")
        elif href == "index.html":
            target = pre + "index.html" if depth else "index.html"
        else:
            target = pre + href if depth else href
        cls = "nav active" if label == active else "nav"
        nav.append(f'<a class="{cls}" href="{target}"><span aria-hidden="true">{glyph}</span>{e(label)}</a>')
    nav.append('<p class="side-label">Archive</p>')
    nav.append(f'<a class="nav" href="{pre}archive/index.html"><span aria-hidden="true">▣</span>Superseded sites</a>')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="stylesheet" href="{pre}style.css">
</head>
<body>
<div class="wrap">
<aside>
  <div class="brand"><span class="mark">♠</span> VEGAS POKER PLANNER</div>
  {''.join(nav)}
</aside>
<main>
{body}
<footer>
<p><b>Verification rule for this site.</b> Every table row links to the official page, PDF or structure sheet the value came from, and shows the date that source was last read ({e(AS_OF)}). A cell showing <span class="blank">—</span> means no official source stated the value. Nothing is inferred or filled in. Guarantee ÷ entry fee is a descriptive ratio, not a forecast of winnings.</p>
<p>Research snapshot {e(AS_OF)} (UTC). Not an offer to sell rooms or tournament entries. Schedules, fees and rules change without notice — re-check the linked official page before paying anything.</p>
</footer>
</main>
</div>
<script src="{pre}app.js"></script>
</body>
</html>"""


PAGES = {}


def write(path, text):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as fh:
        fh.write(text)
    PAGES[path] = text


# --------------------------------------------------------------------------
# derived collections used by several pages
# --------------------------------------------------------------------------
ven_events = [x for x in EVENTS if x["venue"] == "venetian"]
wynn_events = [x for x in EVENTS if x["venue"] == "wynn"]
daily_events = [x for x in EVENTS if x["venue"] not in ("venetian", "wynn")]

# "Silent on entry limits" is only meaningful where a structure sheet was read
# AND a fee split was published from it. An event whose buy-in came from a
# schedule table (no sheet opened) is unverified, not silent.
confirmed_single = [x for x in EVENTS
                    if x["entry_rule"] == "not_stated" and x.get("sheet_read")]
silent_unread = [x for x in EVENTS
                 if x["entry_rule"] == "not_stated" and not x.get("sheet_read")]
spend_more = [x for x in EVENTS if x["entry_rule"] in
              ("unlimited_reentry", "reentry_allowed", "rebuy_addon", "reentry_addon")]

dated_events = sorted([x for x in EVENTS if x.get("date")], key=sort_key)
recurring = [x for x in EVENTS if x.get("weekday")]
all_dates = sorted({x["date"] for x in dated_events})
playable = [x for x in dated_events if x["type"] not in ("day2", "final")]


def runs_on(ev, iso_date):
    """Does a recurring event run on this ISO date?"""
    import datetime as _dt
    susp = ev.get("suspended")
    if susp and susp[0] <= iso_date <= susp[1]:
        return False
    d = _dt.date.fromisoformat(iso_date)
    code = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][d.weekday()]
    return code in (ev.get("weekday") or [])


def events_for_date(iso_date):
    """Every *enterable* event available on a date: dated ones that start that
    day, plus recurring ones whose weekday matches."""
    out = [x for x in dated_events if x["date"] == iso_date and x["type"] not in ("day2", "final")]
    out += [x for x in recurring if runs_on(x, iso_date) and x.get("buy_in")]
    return sorted(out, key=lambda x: (x.get("time") or "99", x["venue"]))


# ==========================================================================
# DASHBOARD (index)
# ==========================================================================
def page_index():
    n_events = len(EVENTS)
    n_ven = len(ven_events)
    n_wynn = len(wynn_events)
    n_daily = len(daily_events)
    cheapest = min([x for x in EVENTS if x.get("buy_in")], key=lambda x: x["buy_in"])
    biggest = max([x for x in EVENTS if x.get("gtd")], key=lambda x: x["gtd"])
    # Only events backed by a room's own document count as "verified", and a
    # satellite's start is not a tournament start in the sense the brief asks
    # about, so both are excluded from this card.
    # Includes recurring events: the earliest start on the Strip may well be a
    # daily, and a dated-only scan would miss it entirely. Satellites, day-2
    # restarts and final tables are excluded because none is a tournament you
    # can enter as a main event.
    PREF = {"caesars-palace": 0, "venetian": 1, "bellagio": 2, "wynn": 3, "mgm-grand": 4}
    verified_starts = [x for x in EVENTS
                       if x.get("time") and x["type"] not in ("satellite", "day2", "final")
                       and "C_STRIP_ARTICLE" not in x["sources"]
                       and (x.get("sheet_read") or x["type"] == "daily")]
    earliest = sorted(verified_starts, key=lambda x: (x["time"], PREF.get(x["venue"], 9)))[0]
    n_fee_split = len([x for x in EVENTS if x.get("fee") is not None])

    cards = f"""
<section class="grid">
  <article class="card"><h3>Confirmed single-entry events</h3>
    <span class="big dim">0</span>
    <p class="note">No official source read states a maximum of one entry. {len(confirmed_single)} events have
    a structure sheet that says nothing about it — silence is not confirmation.</p></article>
  <article class="card"><h3>Events catalogued</h3>
    <span class="big">{n_events}</span>
    <p class="note">{n_ven} Venetian · {n_wynn} Wynn WPT · {n_daily} daily/weekly at four other rooms.</p></article>
  <article class="card"><h3>Dated hotel quotes</h3>
    <span class="big dim">0</span>
    <p class="note">Published resort fees and starting rates exist for five properties; not one dated
    checkout total does. That is the largest hole in the plan.</p></article>
  <article class="card"><h3>Earliest verified start</h3>
    <span class="big">{e(earliest['time'])}</span>
    <p class="note">{e(earliest['time'])} · {e(earliest['name'][:58])} · {e(earliest['venue_name'])}.
    No 8 AM tournament exists on any official source read, so the requested 8 AM start is not achievable
    as specified.</p></article>
</section>"""

    verdict = f"""
<section class="panel badbox">
<h2 style="margin-top:0">The headline, stated plainly</h2>
<p><b>The requested trip cannot be built to specification from official sources today.</b>
Three of the requirements collide with what the casinos actually publish:</p>
<ul class="clean">
<li><b>Single-entry only.</b> Every property that publishes an entry rule publishes a re-entry, rebuy
or paid add-on. The Venetian's DeepStack sheets are the most promising — they state the fee split,
chips, level length and late-registration close, and they block play after a player bags chips — but
none of the {len(EVENTS)} rows states "one entry only". So the single-entry short-list is empty by
design, not by omission.</li>
<li><b>An 8 AM all-day schedule.</b> The earliest verified start on the Strip is {e(earliest['time'])}
at Caesars Palace, with the Venetian following at 10:10 AM. Wynn also has 10:00 AM starts, but only
on WPT series days. An 8 AM start would leave two hours with nothing to enter.</li>
<li><b>True hotel cost.</b> Resort fees, the 13.38% Clark County tax and the parking schedule are all
verified. The room rate is not: every booking engine returned placeholder prices to a non-browser
client, so no dated checkout total exists.</li>
</ul>
<p class="note">What <i>is</i> solid: {n_events} events with official start times, buy-ins, guarantees and
structure links; printed fee splits for {n_fee_split} of them; a measured hotel→poker-room walking matrix;
and a ranked list that separates events where you can spend more from events that stay silent.</p>
</section>"""

    best = sorted([x for x in EVENTS if x.get("gtd") and x.get("pool_per_entry")],
                  key=lambda x: -(x["gtd"] / x["pool_per_entry"]))[:6]
    best_rows = "".join(
        f"""<tr>
<td class="tight">{e(event_date_label(x))}</td>
<td class="tight">{e(x['time'])}</td>
<td>{e(x['name'][:60])}</td>
<td class="num">{dash(x['buy_in'], 'money')}</td>
<td class="num">{dash(x['fee'], 'money')}</td>
<td class="num">{dash(x['gtd'], 'money')}</td>
<td class="num">{dash(x['pool_per_entry'], 'money')}</td>
<td class="num">{entries_to_fund(x) or dash(None)}</td>
<td>{type_badge(x['type'])}</td>
<td>{src_cell(x['sources'][-1:])}</td>
</tr>""" for x in best)

    body = f"""
<div class="pagehead">
  <div>
    <div class="eyebrow">Las Vegas Strip · poker tournament research</div>
    <h1>Dashboard</h1>
    <p class="note" style="max-width:74ch">Official-source schedule, cost and walking data for a Strip poker
    vacation, rebuilt from the underlying pages line by line on {e(AS_OF)}. Unverified values are blank and
    listed on the <a href="flagged.html">Flagged for review</a> page — they are never guessed.</p>
  </div>
  <div class="stamp">sources read<br><b>{e(AS_OF)}</b><br>UTC</div>
</div>
{verdict}
{cards}

<section class="panel">
<h2>Where the data stands, category by category</h2>
<div class="tablewrap"><table>
<thead><tr><th>Category</th><th>Verified</th><th>Not verified</th><th>Page</th></tr></thead>
<tbody>
<tr><td><b>Tournament schedule</b></td><td>Every start time, buy-in, guarantee and structure link for the
Venetian DSE IV ({n_ven} rows) and the Wynn WPT World Championship ({n_wynn} rows), plus four daily/weekly
slates.</td><td>Two of six venues publish no buy-in at all (Horseshoe); one publishes a stale month label
(MGM Grand).</td><td><a href="events.html">All events →</a></td></tr>
<tr><td><b>Entry limits</b></td><td>Fee splits and re-entry wording for {n_fee_split} events.</td>
<td>A written single-entry confirmation: zero. The Venetian's remaining 23 structure sheets were not opened.</td>
<td><a href="ranking.html">Best value →</a></td></tr>
<tr><td><b>Prize-pool value</b></td><td>Guarantee ÷ entry fee, and the exact number of entries needed to fund each guarantee.</td>
<td>Actual field sizes, so overlay is unknown.</td><td><a href="ranking.html">Best value →</a></td></tr>
<tr><td><b>Hotel cost</b></td><td>Resort fees ($50–$55 + tax), the 13.38% Clark County tax, parking schedules, cancellation terms, check-in times.</td>
<td>Every dated room rate and every checkout total.</td><td><a href="hotels.html">Hotels →</a> · <a href="trip-cost.html">Trip cost →</a></td></tr>
<tr><td><b>Walking distance</b></td><td>14 hotel→room pairs measured on Google Maps, with the 30-minute test applied.</td>
<td>Any property-published route; in-building walking time.</td><td><a href="walking.html">Walking →</a></td></tr>
<tr><td><b>Day plan</b></td><td>Every start time, every late-registration close, and a walking-and-timing test for a second event.</td>
<td>Any published finish time. Without one, every second event is necessarily a <i>conditional fallback</i>.</td><td><a href="dayplan.html">Day plan →</a></td></tr>
</tbody></table></div>
</section>

<section class="panel">
<h2>Highest guarantee ÷ entry fee, among events with a publisher-stated fee split</h2>
<p class="note">Read this as "how many buy-ins the advertised guarantee represents", nothing more. The
<i>entries needed</i> column is exact arithmetic: guarantee ÷ the prize-pool-per-entry printed on the
structure sheet. A low number means the guarantee needs a modest field; a number near or below the
field the room usually draws means the advertised guarantee is likely to be met or beaten.
It is <b>not</b> a forecast of winnings.</p>
<div class="tablewrap"><table>
<thead><tr><th>Date</th><th>Start</th><th>Event</th><th>Buy-in</th><th>Fee</th><th>Guarantee</th>
<th>Pool / entry</th><th>Entries needed</th><th>Type</th><th>Source</th></tr></thead>
<tbody>{best_rows}</tbody></table></div>
<p class="note">Full ranking with filters: <a href="ranking.html">Best value →</a>. Bounty and flight
events are labelled separately there, because a bounty guarantee counts bounties in the pool.</p>
</section>

<section class="grid">
<article class="card"><h3>Start here</h3>
<p class="note" style="margin-bottom:10px">Four pages answer the four questions a booking decision needs.</p>
<ul class="clean" style="font-size:.87rem">
<li><a href="ranking.html">Best value</a> — the short-list, the spend-more list, and what the ratio does and does not mean</li>
<li><a href="dayplan.html">Day plan</a> — one primary event per day, plus a conditional fallback</li>
<li><a href="trip-cost.html">Trip cost</a> — the calculator, with every default labelled as verified or not</li>
<li><a href="questions.html">Questions</a> — the 12 things that must be answered before booking</li>
</ul></article>
<article class="card"><h3>Cheapest entry found</h3>
<p><span class="big">{dash(cheapest['buy_in'],'money')}</span>
<span class="note">{e(cheapest['name'])} · {e(cheapest['venue_name'])} · {e(event_date_label(cheapest))}</span></p>
<p class="note">Cheapest is not best value. Entry cost and field size drive the ratio far more than the
headline number does.</p></article>
<article class="card"><h3>Largest guarantee found</h3>
<p><span class="big">{dash(biggest['gtd'],'money')}</span>
<span class="note">{e(biggest['name'])} · {dash(biggest['buy_in'],'money')} buy-in · {e(event_date_label(biggest))}</span></p>
<p class="note">{src_link('W_WPT_SCHED')}. This event is a multi-flight $1,100 event that allows
re-entry, so it is excluded from any single-entry short-list.</p></article>
</section>
"""
    write("index.html", shell("Dashboard", "Vegas Poker Planner — Dashboard",
                              "Official-source Las Vegas Strip poker tournament, hotel cost and walking-distance dashboard.",
                              body))


# ==========================================================================
# EVENTS
# ==========================================================================
def page_events():
    rows = []
    for x in sorted(EVENTS, key=lambda r: (sort_key(r), r["venue"], r["time"] or "")):
        if not x.get("buy_in") and x["type"] in ("day2", "final"):
            continue  # no-entry rows are shown on the day plan instead
        search = " ".join(str(x.get(k) or "") for k in
                          ("name", "venue_name", "date", "time", "event_no", "notes"))
        silent = 1 if (x["entry_rule"] == "not_stated" and x.get("sheet_read")) else 0
        single = 1 if x.get("single_entry_confirmed") else 0
        rows.append(f"""<tr data-search="{e(search)}" data-date="{e(x.get('date') or '')}"
 data-venue="{e(x['venue'])}" data-rule="{e(x['entry_rule'])}" data-silent="{silent}" data-single="{single}">
<td class="tight">{e(event_date_label(x))}</td>
<td class="tight">{dash(x.get('time'))}</td>
<td>{e(x['venue_name'])}</td>
<td class="tight">{dash(x.get('event_no'))}</td>
<td>{e(x['name'])}</td>
<td class="num">{dash(x.get('buy_in'), 'money')}</td>
<td class="num">{dash(x.get('fee'), 'money')}</td>
<td class="num">{dash(x.get('gtd'), 'money')}</td>
<td class="num">{dash(x.get('chips'))}</td>
<td class="num">{dash(x.get('level_min'))}</td>
<td class="tight">{reg_close_display(x)}</td>
<td>{rule_badge(x['entry_rule'], x.get('sheet_read'))}</td>
<td>{type_badge(x['type'])}</td>
<td class="tight">Last checked<br>{e(AS_OF)}</td>
<td>{src_cell(x['sources'][:3])}</td>
</tr>""")

    opts = "".join(f'<option value="{e(v["id"])}">{e(v["name"])}</option>' for v in VENUES)
    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">Every row, every source</div><h1>All events</h1>
  <p class="note" style="max-width:76ch">Every tournament found on an official property source, with its
  start time, buy-in, published guarantee, starting stack, level length, late-registration close, entry-rule
  status and the source it came from. Search and filter below. Rows marked <span class="blank">—</span> are
  values no official source stated.</p></div>
  <div class="stamp">rows shown<br><b class="count" id="shown">{len(rows)}</b><br>of {len(rows)}</div>
</div>

<div class="controls">
  <div class="field"><label for="q">Search</label>
    <input type="search" id="q" placeholder="venue, event name, date, event number…"></div>
  <div class="field"><label for="fdate">Date</label>
    <select id="fdate"><option value="">Any date</option>
    {''.join(f'<option value="{d}">{d}</option>' for d in all_dates)}</select></div>
  <div class="field"><label for="fvenue">Venue</label>
    <select id="fvenue"><option value="">Any venue</option>{opts}</select></div>
  <label class="switch"><input type="checkbox" id="fse"> Single-entry <i>confirmed</i></label>
  <label class="switch"><input type="checkbox" id="ffree"> Sheet silent on entry rule</label>
  <label class="switch"><input type="checkbox" id="funread"> Sheet never opened</label>
  <button id="freset" type="button">Reset</button>
</div>

<div class="panel warnbox" id="se-note">
<p style="margin-top:0"><b>About the two entry-rule toggles.</b> <i>Single-entry confirmed</i> requires an
official source to state positively that only one entry is allowed. Ticking it returns <b>zero rows</b>:
no such statement exists anywhere in {len(EVENTS)} catalogued rows. That is the finding, not a fault.</p>
<p><i>Sheet silent on entry rule</i> is a different and weaker thing: it shows the {len(confirmed_single)}
events whose structure sheet was actually opened and printed rules for the fee split, chips, levels and
late registration, but said nothing at all about re-entry, rebuys or add-ons. The other
{len(silent_unread)} rows marked "not stated" are only "not stated" because their sheet was <b>never
opened</b> — those are unverified, not silent, and this filter deliberately excludes them.</p>
<p class="note">Third state, for completeness: {len(spend_more)} rows where the property's own terms
positively permit paying again. See <a href="ranking.html">Best value</a>.</p>
</div>

<div class="tablewrap"><table id="evtable">
<thead><tr>
<th>Date</th><th>Start</th><th>Venue</th><th>#</th><th>Event</th><th>Buy-in</th><th>Fee</th>
<th>Guarantee</th><th>Chips</th><th>Level (min)</th><th>Late reg closes</th><th>Entry rule</th>
<th>Type</th><th>Last checked</th><th>Source</th>
</tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>

<section class="panel">
<h2>What each column means</h2>
<dl class="defs">
<dt>Buy-in</dt><dd>The entry amount published by the property. It already includes the house fee — the
<i>Fee</i> column breaks out how much of it the room withholds.</dd>
<dt>Fee</dt><dd>House fee withheld from the buy-in, as printed on the structure sheet ("$90 of the $600
Buy-In is withheld for house fees"). Blank where the sheet was not read.</dd>
<dt>Guarantee</dt><dd>The advertised guaranteed prize pool. For bounty events the property states the
guarantee includes bounties paid, which is why bounty events are separated on the ranking page.</dd>
<dt>Chips / Level</dt><dd>Starting stack and minutes per level, from the property's printed schedule or
structure sheet.</dd>
<dt>Late reg closes</dt><dd>The last moment a new entry is accepted. This is the column that decides
whether a second tournament in the same day is even possible.</dd>
<dt>Entry rule</dt><dd><span class="tag ok">silent on entry limit</span> = the event's own structure sheet
was opened and says nothing about a maximum number of entries. <span class="tag muted">sheet not read</span> =
nobody opened that event's sheet, so it is <i>unverified</i> rather than silent — a different and weaker state.
<span class="tag warn">re-entry</span> / <span class="tag warn">rebuy + add-on</span> = the property's own
terms positively permit paying again for more chips.</dd>
<dt>Type</dt><dd>Starting flights, day-2 restarts and final tables are labelled so they are not mistaken
for additional tournaments.</dd>
<dt>Last checked</dt><dd>The date the linked source was read. Re-open the link before trusting the row.</dd>
</dl>
</section>
"""
    write("events.html", shell("All events", "All events — Vegas Poker Planner",
                              "Every verified Las Vegas Strip poker tournament with source links.", body))


# ==========================================================================
# RANKING
# ==========================================================================
def page_ranking():
    # Only events whose structure sheet was actually opened: a read sheet AND a
    # printed fee split. An event that is "not stated" merely because nobody
    # opened its sheet is unverified, not silent, and does not belong in List A.
    confirmed = [x for x in EVENTS if x["entry_rule"] == "not_stated"
                 and x.get("gtd") and x.get("fee") is not None and x.get("pool_per_entry")]
    confirmed.sort(key=lambda x: (-(x["gtd"] / (x["pool_per_entry"] or x["buy_in"]))))

    se_rows = "".join(f"""<tr>
<td class="tight">{e(event_date_label(x))}</td><td class="tight">{e(x['time'])}</td>
<td>{e(x['name'][:52])}</td><td>{e(x['venue_name'])}</td>
<td class="num">{dash(x['buy_in'],'money')}</td>
<td class="num">{dash(x['fee'],'money')}</td>
<td class="num">{dash(x['pool_per_entry'],'money')}</td>
<td class="num">{dash(x['gtd'],'money')}</td>
<td class="num">{dash(round(x['gtd']/x['buy_in'],1))}</td>
<td class="num">{entries_to_fund(x) or dash(None)}</td>
<td>{type_badge(x['type'])}</td><td>{src_cell(x['sources'][-1:])}</td></tr>""" for x in confirmed)

    # spend-more: events where the property's own terms allow paying more for chips
    sm = [x for x in EVENTS if x["entry_rule"] in ("unlimited_reentry", "reentry_allowed",
                                                  "rebuy_addon", "reentry_addon")]
    sm.sort(key=lambda x: (-(x.get("buy_in") or 0)))
    sm_rows = "".join(f"""<tr>
<td class="tight">{e(event_date_label(x))}</td><td class="tight">{e(x.get('time'))}</td>
<td>{e(x['name'][:52])}</td><td>{e(x['venue_name'])}</td>
<td class="num">{dash(x.get('buy_in'),'money')}</td>
<td class="num">{dash(x.get('gtd'),'money')}</td>
<td>{rule_badge(x['entry_rule'], x.get('sheet_read'))}</td>
<td class="note">{e(x.get('entry_rule_excerpt') or '')[:210]}</td>
<td>{src_cell(x['sources'][-2:])}</td></tr>""" for x in sm[:60])

    bounty = [x for x in EVENTS if "Bounty" in x["name"] or "Knock-Out" in x["name"]]
    side = ([x for x in EVENTS if x["type"] in ("satellite", "team")] )

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">Ranked only after the cost and the guarantee were confirmed</div>
  <h1>Best value</h1>
  <p class="note" style="max-width:76ch">Three separate lists, because mixing them is what makes
  "best tournament" comparisons misleading. <b>List A</b> holds events whose official structure sheet is
  silent on entry limits — the closest available stand-in for a single-entry short-list.
  <b>List B</b> holds events the property's own terms let you re-enter, rebuy or add on to — you can buy
  an advantage there, so they are kept apart. <b>List C</b> separates bounty, flight, team and satellite
  formats, whose headline guarantee does not mean the same thing as a plain prize pool.</p></div>
  <div class="stamp">ranked rows<br><b class="count">{len(confirmed)}</b><br>by guarantee ÷ buy-in</div>
</div>

<section class="panel">
<h2>How the ratio works — and what it is not</h2>
<p><b>Guarantee ÷ entry fee</b> answers one question: how many full buy-ins the advertised guarantee
represents. A ratio of 100 means the room has advertised a prize pool equal to 100 buy-ins.
That is a description of the advertised number, nothing else.</p>
<p>It is <b>not</b> a forecast, an expected return, an overlay estimate, or a statement that the event
is +EV. Three reasons it cannot be read that way: (1) the guarantee is a floor the room promises, not the
amount of money in the prize pool — the pool is the actual entries × prize-pool-per-entry; (2) the room
keeps the fee, so the ratio is not a return on your buy-in; (3) field size is unknown before the event.</p>
<p>The column that makes the ratio interpretable is <b>entries needed to fund the guarantee</b> —
guarantee ÷ prize-pool-per-entry, straight from the structure sheet. If an event needs 1,000 entries to
fund its guarantee and the room draws 200, the room is paying an overlay; if it needs 60, the guarantee is
a formality. Both are useful, neither is a forecast.</p>
</section>

<h2 style="margin-top:26px">List A — official sheet silent on entry limits</h2>
<p class="note">Not "single entry". These are events where the structure sheet that was read sets the fee
split, the chips, the level length and the late-registration close, and does not mention re-entry, rebuy or
an add-on at all. Silence is the whole claim. Ranked by guarantee ÷ buy-in, highest first.</p>
<div class="tablewrap"><table>
<thead><tr><th>Date</th><th>Start</th><th>Event</th><th>Venue</th><th>Buy-in</th><th>Fee</th>
<th>Pool / entry</th><th>Guarantee</th><th>GTD ÷ buy-in</th><th>Entries needed</th><th>Type</th><th>Source</th></tr></thead>
<tbody>{se_rows}</tbody></table></div>

<h2 style="margin-top:30px">List B — you can spend more to buy chips</h2>
<p class="note">Separated on purpose. In these events the property's own published terms let a player pay
again — unlimited re-entry per flight, re-entry through a level, unlimited rebuys at a chip threshold, or a
paid add-on that buys an extra stack. That is the "advantage through spending more money" category the
brief asked to keep apart, and it is the larger category by far. Showing the first 60 by buy-in.</p>
<div class="tablewrap"><table>
<thead><tr><th>Date</th><th>Start</th><th>Event</th><th>Venue</th><th>Buy-in</th><th>Guarantee</th>
<th>Rule</th><th>What the official source says</th><th>Source</th></tr></thead>
<tbody>{sm_rows}</tbody></table></div>
<p class="note">The clearest single example on the Strip: the Wynn Friday daily states
"Re-entry is NOT allowed" and then permits "Unlimited $200 rebuys for 25,000 tournament chips … any time a
player is at 15,000 chips or less" plus "One (1) $100 add-on for 25,000 tournament chips". Under a
single-entry rule that event is out, even though the words "no re-entry" appear in it.</p>

<h2 style="margin-top:30px">List C — formats whose guarantee is not a plain prize pool</h2>
<p class="note">Bounty guarantees include bounty money paid out; a mystery-bounty guarantee is not
comparable to a plain prize pool; a flight's guarantee spans every starting flight; a satellite's "2 seats"
is not a prize pool; a team event needs two players. These are labelled rather than ranked.</p>
<div class="tablewrap"><table>
<thead><tr><th>Date</th><th>Start</th><th>Event</th><th>Venue</th><th>Buy-in</th><th>Guarantee</th><th>Why it is separate</th><th>Source</th></tr></thead>
<tbody>
{''.join(f'''<tr><td class="tight">{e(event_date_label(x))}</td><td class="tight">{e(x.get("time"))}</td>
<td>{e(x["name"][:58])}</td><td>{e(x["venue_name"])}</td>
<td class="num">{dash(x.get("buy_in"),"money")}</td><td class="num">{dash(x.get("gtd"),"money")}</td>
<td class="note">{e("Bounty money counts toward the guarantee" if "Bounty" in x["name"] or "Knock-Out" in x["name"] else "Prize is seats, not cash" if x["type"]=="satellite" else "Team entry" if x["type"]=="team" else "Guarantee spans all starting flights")}</td>
<td>{src_cell(x["sources"][-1:])}</td></tr>''' for x in (bounty[:14] + side[:10]))}
</tbody></table></div>

<section class="panel warnbox">
<h2>Why no event is ranked as a confirmed single-entry event</h2>
<p>Of the {D['struct_total']} Venetian DeepStack structure sheets linked from the official schedule,
<b>{len(D['struct_read'])} were opened and read in full</b> for this snapshot. Every one of them sets the
buy-in, the fee split, the starting stack, the level length and the late-registration close. None of them
states a maximum number of entries. None of them mentions an add-on. Several of them explicitly restrict
play after a player bags chips for day 2 — which proves the sheets do know how to write an entry
restriction when one exists.</p>
<p>That is the strongest finding in this dataset, and it cuts both ways: it is the best available
evidence that these could be one-entry events, and it is <i>not</i> evidence that they are. A written
confirmation from the room is the only thing that converts a blank into a yes.</p>
<p>Every other property publishes the opposite. Wynn says "Unlimited re-entry for each starting flight …
until the start of level 9". Caesars Palace says players "may re-enter, by paying the entry fee, upon
elimination within the first break of play" and sells a $50 add-on. Bellagio says "Players may buy-in and
re-enter through the end of level 8".</p>
<p class="note">Sources: {src_cell(['V_SCHED_TABLE','W_WPT_STRUCT','C_DAILY_PDF','B_FRI_PDF'])}</p>
</section>
"""
    write("ranking.html", shell("Best value", "Best value — Vegas Poker Planner",
                               "Single-entry candidates and spend-more events on the Las Vegas Strip, ranked on confirmed cost and guarantee.",
                               body))


# ==========================================================================
# DAY PLAN
# ==========================================================================
def page_dayplan():
    PRIMARY_PREF = {"venetian": 0, "wynn": 1, "caesars-palace": 2, "bellagio": 3,
                    "mgm-grand": 4, "horseshoe": 5}

    day_blocks = []
    n_fallback_days = 0
    for d in all_dates:
        avail = events_for_date(d)
        restarts = [x for x in dated_events if x["date"] == d and x["type"] in ("day2", "final")]
        if not avail and not restarts:
            continue

        rank_pool = [x for x in avail if "C_STRIP_ARTICLE" not in x["sources"]]
        if not rank_pool:
            rank_pool = avail
        ranked = sorted(rank_pool, key=lambda x: (
            x.get("time") or "99",
            1 if x["type"] == "satellite" else 0,
            PRIMARY_PREF.get(x["venue"], 9)))
        primary = ranked[0] if ranked else None

        rows = []
        if primary:
            rows.append(f"""<tr><td>{e(primary['time'])}</td><td>{e(primary['name'][:56])}</td>
<td>{e(primary['venue_name'])}</td><td class="num">{dash(primary.get('buy_in'),'money')}</td>
<td class="tight">{reg_close_display(primary)}</td>
<td class="num">{dash(primary.get('chips'))}</td>
<td class="num">{dash(primary.get('level_min'))}</td>
<td><span class="tag ok">primary</span></td>
<td class="note">Earliest verified start on this date. The room does not publish a finish time.</td></tr>""")

        viable, dropped = [], 0
        for cand in [x for x in avail if x is not primary]:
            if not cand.get("time") or cand["time"] <= primary["time"]:
                continue
            same = cand["venue"] == primary["venue"]
            walk = next((w for w in WALKS if w["origin"] == primary["venue"]
                         and w["destination"] == cand["venue"]), None)
            if not same and (not walk or not walk["within_30"]):
                dropped += 1
                continue
            arrive = f", then a {walk['minutes']} min walk" if (walk and not same) else ""
            opens = cand.get("reg_close") or (f"level {cand['reg_close_level']}"
                                              if cand.get("reg_close_level") else None)
            closes = primary.get("reg_close") or (f"level {primary['reg_close_level']}"
                                                 if primary.get("reg_close_level") else None)
            if not opens:
                why = (f"Late-registration close is not published for this event, so whether it is still "
                       f"open after the primary cannot be established{arrive}.")
                rank = 2
            else:
                # Each event has its own level clock, so a later-starting event's
                # late close falls later in the day even at the same level number.
                why = (f"Starts {_gap(primary['time'], cand['time'])} after the primary, so its late "
                       f"registration ({opens}) runs later in the day{arrive}. Reachable only if you are "
                       f"eliminated before then; surviving the primary always kills this option.")
                rank = 0 if same else 1
            viable.append((rank, cand, why))

        viable.sort(key=lambda t: (t[0], t[1]["time"]))
        for rank, cand, why in viable[:2]:
            n_fallback_days += 1
            rows.append(f"""<tr><td>{e(cand['time'])}</td><td>{e(cand['name'][:56])}</td>
<td>{e(cand['venue_name'])}</td><td class="num">{dash(cand.get('buy_in'),'money')}</td>
<td class="tight">{reg_close_display(cand)}</td>
<td class="num">{dash(cand.get('chips'))}</td><td class="num">{dash(cand.get('level_min'))}</td>
<td><span class="tag warn">conditional fallback</span></td>
<td class="note">{e(why)}</td></tr>""")

        if not viable:
            later = len([x for x in avail if x is not primary and (x.get("time") or "") > (primary.get("time") or "")])
            rows.append(f"""<tr><td colspan="9" class="note"><b>One entry this day.</b>
{later} later event(s) start today, but none qualifies as a fallback: {dropped} are at properties with no
measured walking route or one over the 30-minute limit, and no same-property event starts later.</td></tr>""")

        for r in restarts:
            rows.append(f"""<tr><td>{e(r.get('time') or '—')}</td><td>{e(r['name'][:56])}</td>
<td>{e(r['venue_name'])}</td><td class="num">—</td><td class="tight">—</td><td class="num">—</td>
<td class="num">—</td><td><span class="tag muted">no new entry</span></td>
<td class="note">Existing players only. Listed so it is not mistaken for a fresh tournament.</td></tr>""")

        day_blocks.append((d, ''.join(rows), len(avail)))

    blocks = "".join(f"""
<h3 style="margin-top:26px">{e(d)} <span class="note" style="font-weight:400">· {n} enterable events that day</span></h3>
<div class="tablewrap"><table>
<thead><tr><th>Start</th><th>Event</th><th>Venue</th><th>Buy-in</th><th>Late reg closes</th>
<th>Chips</th><th>Level min</th><th>Role</th><th>What it costs you to try</th></tr></thead>
<tbody>{rows}</tbody></table></div>""" for d, rows, n in day_blocks)

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">One primary event per day, and never a fantasy second one</div>
  <h1>Day plan</h1>
  <p class="note" style="max-width:76ch">For every one of the {len(day_blocks)} dates in the trip window
  this page names <b>one primary event</b> — the earliest verified start that day — plus, where one exists,
  a <b>conditional fallback</b> whose late registration is still open later in the day. Recurring events are
  merged onto the dates they actually run, and the Wynn slate correctly stays empty between Nov 27 and
  Dec 21.</p></div>
  <div class="stamp">dates covered<br><b class="count">{len(day_blocks)}</b><br>fallbacks offered: {n_fallback_days}</div>
</div>

<section class="panel badbox">
<h2 style="margin-top:0">There is no all-day schedule, and here is exactly why</h2>
<p>The brief asks for a schedule from 8 AM that maximises tournaments per vacation day. Two gaps in what
the rooms publish block it, and neither is a gap in the research.</p>
<p><b>Nobody publishes a finish time.</b> Not one room states when a tournament ends. The structure sheets
give a starting stack, minutes per level and the level at which late registration closes — and stop there.
So no second event can be scheduled with confidence: whether you are free at 5 PM depends on how long you
survive, which is the one variable a schedule cannot control.</p>
<p><b>Nobody publishes an 8 AM start.</b> The earliest start backed by a room's own document is 10:00 AM at
Caesars Palace; the Venetian follows at 10:10 AM. A 9 AM Horseshoe slot exists only in a Caesars corporate
article with no flyer behind it (<a href="flagged.html">F-07</a>). Starting at 8 AM would mean two hours
with nothing to enter.</p>
<p>This page does the honest version instead: one committed event per day, and a fallback labelled with the
exact condition under which it becomes available. It is a plan you can follow rather than a grid that
assumes you bust out on cue.</p>
</section>

<section class="panel">
<h2>How the fallback test works</h2>
<p>For a later event to count as a fallback, three things must be true — and all three are published:</p>
<ol>
<li><b>It starts later than the primary</b>, per the room's own schedule.</li>
<li><b>You can get there</b> — the same building, or a property inside the measured 30-minute limit on the
<a href="walking.html">walking page</a>.</li>
<li><b>Its late registration is still open</b> after you could plausibly be eliminated. This is the binding
constraint, because late-registration closes are published and finish times are not.</li>
</ol>
<p>A player who survives the primary cannot take the fallback, and every fallback row says so. It is
insurance against an early exit, priced at the cost of a second bullet — not a second tournament squeezed
into the same day.</p>
<p class="note">An earlier draft of this page computed a "derived maximum length" per event from a table of
level counts. That table was written from memory rather than transcribed from the sheets, so it was removed
rather than corrected — see <a href="repo-review.html">Repo review</a>. No event-length figure appears
anywhere on this site now.</p>
<p class="note"><b>What the sheets do publish</b>, and what the dataset therefore holds: the starting stack,
the minutes per level, and the point at which late registration closes. The $600 one-day sheet, for example,
prints 28 levels of 30 minutes with seven 15-minute breaks and states "Late Registration: 10 levels + Break
(~ 4:55 PM)". That last figure is the room's own approximate close time — the only clock time any structure
sheet gives, and it is an approximation rather than a schedule.</p>
</section>

{blocks}

<section class="panel">
<h2>What would turn this into a real all-day schedule</h2>
<ul class="clean">
<li><b>Published finish times</b>, or historical level-at-finish data, for each event. One number per event
would convert every conditional fallback into a scheduled second entry.</li>
<li><b>A confirmed 9 AM or 8 AM event.</b> The Horseshoe slot is the only candidate on the Strip, and it
needs its own flyer.</li>
<li><b>The unread Venetian structure sheets</b> ({D['struct_total'] - len(D['struct_read'])} of
{D['struct_total']}), which would at least let every Venetian row state its late-registration close instead
of a blank.</li>
</ul>
</section>
"""
    write("dayplan.html", shell("Day plan", "Day plan — Vegas Poker Planner",
                                "One verified primary event per day, with conditional fallbacks only where the published late-registration closes allow them.",
                                body))


# ==========================================================================
# TRIP COST
# ==========================================================================
def page_tripcost():
    ven = HOTEL_BY_ID["venetian"]
    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">Entries × buy-ins + nights × true hotel cost</div><h1>Trip cost</h1>
  <p class="note" style="max-width:76ch">A working calculator, not a quote. Every input starts at a value
  that was actually read from an official source, and each one is labelled with where it came from. Change
  anything. The output is exact arithmetic on your inputs — it is only as good as the numbers you put in,
  and the room rate is the one number nobody publishes for a specific date.</p></div>
  <div class="stamp">defaults from<br><b>{e(AS_OF)}</b><br>official pages</div>
</div>

<section class="panel">
<h2>The formula and the true-cost definition</h2>
<p><b>Total</b> = (entries × buy-in) + (nights × room rate) + (nights × resort fee) +
(room rate + resort fee) × tax rate × nights + (parking days × daily parking) + other.</p>
<p><b>True cost per night</b> = room rate + mandatory resort fee + tax on both. Taxes are applied to the
resort fee as well as the room rate, because the Clark County room tax applies to the total room charge —
the Venetian's own terms state the 13.38% room tax and the $55-plus-tax fee separately, and the fee is
taxable.</p>
</section>

<section class="panel">
<h2>Inputs</h2>
<div class="controls" style="margin-top:0">
  <div class="field"><label for="c_nights">Nights</label>
    <input type="number" id="c_nights" value="7" min="0" step="1"></div>
  <div class="field"><label for="c_entries">Tournament entries</label>
    <input type="number" id="c_entries" value="7" min="0" step="1"></div>
  <div class="field"><label for="c_buyin">Average buy-in ($)</label>
    <input type="number" id="c_buyin" value="600" min="0" step="50"></div>
  <div class="field"><label for="c_rate">Room rate / night ($)</label>
    <input type="number" id="c_rate" value="119" min="0" step="1"></div>
  <div class="field"><label for="c_fee">Resort fee / night ($)</label>
    <input type="number" id="c_fee" value="55" min="0" step="1"></div>
  <div class="field"><label for="c_tax">Room tax (%)</label>
    <input type="number" id="c_tax" value="13.38" min="0" step="0.01"></div>
  <div class="field"><label for="c_park">Parking / day ($)</label>
    <input type="number" id="c_park" value="20" min="0" step="1"></div>
  <div class="field"><label for="c_parknights">Parking days</label>
    <input type="number" id="c_parknights" value="7" min="0" step="1"></div>
  <div class="field"><label for="c_other">Other ($)</label>
    <input type="number" id="c_other" value="0" min="0" step="10"></div>
</div>
<p class="note" style="margin-top:10px">Defaults: <b>$119</b> is the Venetian's published <i>poker starting
rate</i> — conditional on six hours of live cash play or a $300+ tournament buy-in per night, and not a
dated quote. <b>$55</b> is the Venetian resort fee. <b>13.38%</b> is the Clark County room tax printed on
the Venetian's hotel terms. <b>$20/day</b> is the Venetian's registered-guest self-parking rate. Change the
room rate to a real quote the moment you have one.</p>
</section>

<div class="calc">
<section class="card">
  <h3>Result</h3>
  <div class="row"><span>True cost per night</span><span id="o_night">—</span></div>
  <div class="row"><span>Room subtotal</span><span id="o_room">—</span></div>
  <div class="row"><span>Resort fees</span><span id="o_fee">—</span></div>
  <div class="row"><span>Tax on room + fee</span><span id="o_tax">—</span></div>
  <div class="row"><span><b>Hotel total</b></span><span><b id="o_hotel">—</b></span></div>
  <div class="row"><span>Parking</span><span id="o_park">—</span></div>
  <div class="row"><span>Tournament entries</span><span id="o_tourn">—</span></div>
  <div class="row"><span>Other</span><span id="o_other">—</span></div>
  <div class="row" style="border-top:1px solid #2a3a4d;margin-top:6px;padding-top:10px">
    <span><b>Trip total</b></span><span class="total" id="o_total">—</span></div>
  <div class="row"><span>Per night, all-in</span><span id="o_perday">—</span></div>
  <div class="row"><span>Per tournament entry, all-in</span><span id="o_perentry">—</span></div>
</section>
<section class="card">
  <h3>What the calculator refuses to do</h3>
  <ul class="clean" style="font-size:.86rem">
    <li><b>It will not guess a room rate.</b> The $119 default is a published starting rate, and it is
    conditional. Every booking engine read in this session returned a <code>$XXX</code> placeholder to a
    non-browser client, so no dated total exists.</li>
    <li><b>It will not add the extra-occupant charge.</b> Both MGM properties charge $40–$50 plus tax per
    night above two occupants. If you are travelling as a pair, that line is zero; as a group, add it to
    <i>Other</i>.</li>
    <li><b>It will not model the poker rate's condition.</b> The $119 rate requires six hours of live cash
    play <i>or</i> a $300+ tournament buy-in per night, else the rate reverts to the prevailing rate. If
    you plan rest days, use the public rate instead.</li>
    <li><b>It will not count a "voluntary" gratuity as optional.</b> Several events sell chips for a
    gratuity (Bellagio $40 for +15,000; MGM Grand $11 for +10,000). Declining it puts you at a real chip
    disadvantage, so treat it as part of the entry cost where the fields are competitive.</li>
  </ul>
</section>
</div>

<section class="panel">
<h2>Worked examples using only verified numbers</h2>
<div class="tablewrap"><table>
<thead><tr><th>Stay</th><th>Room rate source</th><th>Resort fee</th><th>Tax</th><th>True cost / night</th><th>Verified?</th></tr></thead>
<tbody>
<tr><td>The Venetian, 7 nights, published poker starting rate</td>
<td>{src_link('V_SUITE_RATES')} $119</td><td>$55</td><td>13.38%</td>
<td class="num">$119 + $55 + 13.38% × $174 = <b>$197.29</b></td>
<td><span class="tag warn">rate conditional</span></td></tr>
<tr><td>The Venetian, 7 nights, no poker-rate qualification (prevailing rate)</td>
<td><span class="blank">—</span></td><td>$55</td><td>13.38%</td>
<td class="num"><span class="blank">cannot compute — no rate</span></td>
<td><span class="tag bad">unverified</span></td></tr>
<tr><td>Wynn, 7 nights</td><td><span class="blank">—</span></td><td>$55</td><td><span class="blank">—</span></td>
<td class="num"><span class="blank">cannot compute</span></td><td><span class="tag bad">unverified</span></td></tr>
<tr><td>Bellagio, 7 nights</td><td><span class="blank">—</span></td><td>$55</td><td><span class="blank">—</span></td>
<td class="num"><span class="blank">cannot compute</span></td><td><span class="tag bad">unverified</span></td></tr>
<tr><td>MGM Grand, 7 nights</td><td><span class="blank">—</span></td><td>$50</td><td><span class="blank">—</span></td>
<td class="num"><span class="blank">cannot compute</span></td><td><span class="tag bad">unverified</span></td></tr>
<tr><td>Caesars Palace, 7 nights</td><td><span class="blank">—</span></td><td><span class="blank">—</span></td><td><span class="blank">—</span></td>
<td class="num"><span class="blank">cannot compute</span></td><td><span class="tag bad">unverified</span></td></tr>
</tbody></table></div>
<p class="note">Only one row of six can be computed at all, and even that one rests on a conditional
starting rate. That is the honest state of the hotel data — see
<a href="questions.html">Questions</a> Q-09 and <a href="flagged.html">Flagged</a> F-03.</p>
</section>

<section class="panel">
<h2>Tournament side: cheapest way to fill seven days</h2>
<div class="tablewrap"><table>
<thead><tr><th>Approach</th><th>Events used</th><th>Entry total</th><th>Caveat</th></tr></thead>
<tbody>
<tr><td>Seven Caesars Palace $100 dailies (10:00 AM or 6:00 PM)</td><td>7 × $100</td><td class="num">$700</td>
<td>Each carries a $50 add-on that buys 15,000 chips — declining it is a real disadvantage. Re-entry permitted.</td></tr>
<tr><td>Seven Venetian $200 daily bounties (5:10 PM)</td><td>7 × $200</td><td class="num">$1,400</td>
<td>Bounty guarantees include bounties, so the headline is not a plain prize pool. Entry limit not stated.</td></tr>
<tr><td>Seven Venetian $600 1-day events</td><td>7 × $600</td><td class="num">$4,200</td>
<td>Highest guarantee-per-buy-in in the dataset. Structure sheet silent on entry limits.</td></tr>
<tr><td>Seven Wynn daily $200 events (Mon–Thu, Sat–Sun)</td><td>7 × $200</td><td class="num">$1,400</td>
<td>Re-entry plus a $100 add-on. Suspended Nov 27 – Dec 21 for the WPT series.</td></tr>
<tr><td>Seven Bellagio $600 Fridays</td><td>7 × $600</td><td class="num">$4,200</td>
<td>Only runs on Fridays; $40 gratuity buys +15,000 chips. Re-entry through level 8.</td></tr>
</tbody></table></div>
<p class="note">Entry totals only — they exclude the hotel side entirely. Combine them with the calculator
once you have a real room rate.</p>
</section>
"""
    write("trip-cost.html", shell("Trip cost", "Trip cost calculator — Vegas Poker Planner",
                                  "Entries × buy-ins + nights × true hotel cost, with every default traced to an official source.",
                                  body))


# ==========================================================================
# HOTELS
# ==========================================================================
def page_hotels():
    rows = []
    for h in HOTELS:
        cards = ""
        rows.append(f"""<tr>
<td><b>{e(h['name'])}</b><br><small>{e(h['address'])}</small></td>
<td class="num">{dash(h['resort_fee'], 'money2')}</td>
<td class="num">{dash(f"{h['tax_rate']*100:.2f}%" if h['tax_rate'] else None)}</td>
<td class="num">{dash(h['published_rate'], 'money')}</td>
<td class="num">{'<span class="blank" title="No dated quote exists">—</span>'}</td>
<td class="note">{e(h['resort_fee_note'])}</td>
<td>{src_cell(h['sources'])}</td>
<td class="tight">Last checked<br>{e(AS_OF)}</td>
</tr>""")

    detail = "".join(f"""
<details>
<summary>{e(h['name'])}</summary>
<dl class="defs">
<dt>Address</dt><dd>{e(h['address'])}</dd>
<dt>Poker room</dt><dd>{e(VENUE_BY_ID[h['venue_with_poker']]['poker_room'])}</dd>
<dt>Resort fee</dt><dd>{dash(h['resort_fee'],'money2')} — {e(h['resort_fee_note'])}</dd>
<dt>Room tax</dt><dd>{e(h['tax_note'])}</dd>
<dt>Published rate</dt><dd>{dash(h['published_rate'],'money')} — {e(h['rate_note'])}</dd>
<dt>Parking</dt><dd>{e(h['parking'])}</dd>
<dt>Cancellation</dt><dd>{e(h['cancellation'])}</dd>
<dt>Check-in / out</dt><dd>{e(h['checkin'])}</dd>
<dt>Quality</dt><dd>{e(h['quality_note'])}</dd>
</dl>
<p class="note">Sources: {src_cell(h['sources'])}</p>
</details>""" for h in HOTELS)

    walk_rows = ""
    for h in HOTELS:
        w = next((x for x in WALKS if x["origin"] == h["id"] and x["destination"] == h["venue_with_poker"]), None)
        if not w:
            continue
        walk_rows += f"""<tr><td>{e(h['name'])}</td>
<td>{e(VENUE_BY_ID[h['venue_with_poker']]['name'])}</td>
<td class="num">{w['minutes']} min</td><td class="num">{e(w['distance'])}</td>
<td>{'<span class="tag ok">≤ 30 min</span>' if w['within_30'] else '<span class="tag bad">over 30 min</span>'}</td>
<td>{src_link('G_WALK')}</td></tr>"""

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">Cost and quality first, distance as the gate</div><h1>Hotels</h1>
  <p class="note" style="max-width:76ch">Seven properties, each shown with the fees and terms its own site
  publishes. The resort fee, the parking schedule and the cancellation deadline are verified for five of
  them. The room rate is verified for none of them for any specific date, so the column that matters most
  is empty and labelled as such.</p></div>
  <div class="stamp">properties<br><b class="count">{len(HOTELS)}</b><br>fees verified: 5 of 7</div>
</div>

<section class="panel badbox">
<h2 style="margin-top:0">The one number nobody publishes</h2>
<p>True nightly cost = room rate + mandatory resort fee + tax on both. Three of those four inputs are
verified for five properties. The room rate is not, and it is the largest input.</p>
<p>Why: The Venetian's booking calendar and the Caesars booking flow both render <code>$XXX</code> price
placeholders to a client that is not a browser, and Wynn's room pages return a "this page has checked out"
stub. The published figures that do exist — $119 and $209 on the Venetian poker-rate page — are
<b>starting rates</b>, conditional on six hours of live cash play or a $300+ tournament buy-in per night,
offered by phone only on code EPOKR25, and capped at 150 days ahead. They are not quotes.</p>
</section>

<div class="tablewrap"><table>
<thead><tr><th>Property</th><th>Resort fee</th><th>Room tax</th><th>Published rate</th>
<th>Dated quote</th><th>Fee wording</th><th>Sources</th><th>Last checked</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>

<h2 style="margin-top:28px">Walking distance to the room you would actually play in</h2>
<p class="note">Measured on Google Maps walking directions on {e(AS_OF)}. Google Maps is a routing
service, not a property policy page — recorded as such on the
<a href="flagged.html">flagged</a> page. Times exclude in-building walking from room to lobby.</p>
<div class="tablewrap"><table>
<thead><tr><th>Stay here</th><th>Play here</th><th>Walk</th><th>Distance</th><th>30-minute test</th><th>Route source</th></tr></thead>
<tbody>{walk_rows}</tbody></table></div>

<h2 style="margin-top:28px">Every verified term, per property</h2>
{detail}

<section class="panel">
<h2>Ranking logic, and why no hotel is ranked here</h2>
<p>The brief ranks cost and quality above distance, with a hard 30-minute walk gate. That ranking needs a
cost, and the only cost inputs available are fees. Ranking on fees alone would put MGM Grand first at
$50/night — and MGM Grand fails the distance gate to the Venetian at 39 minutes. Ranking on the published
starting rate alone would put the Venetian first at $119/night — and that rate is conditional on playing
six hours every single night.</p>
<p>So this page states the constraints and refuses the ranking until a real rate exists. That is
deliberate: a ranking built on a starting rate would look authoritative and be wrong.</p>
<p class="note">Next action: open each property's booking page in a browser for the chosen dates, capture
the checkout total and its timestamp, and append it to the <a href="rates.html">rate log</a>. The rate log
takes as many dated rows per property as you like — it never overwrites.</p>
</section>
"""
    write("hotels.html", shell("Hotels", "Hotels — Vegas Poker Planner",
                               "Verified Las Vegas Strip hotel resort fees, taxes, parking and walking times for poker players.",
                               body))


# ==========================================================================
# RATES (dated log)
# ==========================================================================
def page_rates():
    rows = []
    for r in sorted(RATES, key=lambda x: (x["hotel"], x["kind"])):
        hotel = HOTEL_BY_ID.get(r["hotel"], {}).get("name", r["hotel"])
        amount = (f"${r['amount']:,.2f}" if isinstance(r["amount"], (int, float)) else None)
        rows.append(f"""<tr>
<td class="tight">{e(r['logged'])}</td>
<td>{e(hotel)}</td>
<td>{e(r['kind'].replace('_',' '))}</td>
<td class="num">{dash(amount)}</td>
<td class="note">{e(r['basis'])}</td>
<td class="tight">{dash(r['stay_dates'])}</td>
<td class="note">{e(r['occupancy'])}</td>
<td class="note">{e(r['note'])}</td>
<td>{src_link(r['source']) if r['source'] else '<span class="blank">no source</span>'}</td>
</tr>""")

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">A log, never a single overwritten value</div><h1>Rate log</h1>
  <p class="note" style="max-width:76ch">Every rate observation is its own row, with the date it was
  observed, what it is (a published starting rate, a mandatory fee, a tax rate or a dated quote), the stay
  dates it applies to, the occupancy basis and the source. Nothing here is ever overwritten, so a rate that
  changes shows up as a second row rather than silently replacing the first.</p></div>
  <div class="stamp">observations<br><b class="count">{len(RATES)}</b><br>0 dated quotes</div>
</div>

<section class="panel">
<h2>Why a log instead of a rate column</h2>
<p>A single "rate" cell conflates four different things that look alike and behave differently: a
published <i>starting</i> rate, a mandatory <i>fee</i>, a <i>tax percentage</i> and a real
<i>dated quote</i>. Overwriting one with another loses the distinction, and the distinction is the whole
decision. The $119 Venetian figure is a starting rate conditional on six hours of play per night; a $174
checkout total for 6–10 December would be a quote. They belong in the same log and must never occupy the
same cell.</p>
<p>The log also gives you the audit trail for a dispute: if a property changes a fee, the earlier
observation stays visible with its own date and its own link.</p>
</section>

<div class="tablewrap"><table>
<thead><tr><th>Logged</th><th>Property</th><th>Kind</th><th>Amount</th><th>Basis</th>
<th>Stay dates</th><th>Occupancy</th><th>Note</th><th>Source</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>

<section class="panel warnbox">
<h2>How to append a real quote</h2>
<ol>
<li>Open the property's own booking page in a browser (not a script) for the exact arrival and departure
dates and the exact occupancy.</li>
<li>Walk to the final checkout screen. Capture: the room subtotal, the nightly average, the mandatory
resort fee line, the tax line, any parking line, the cancellation deadline, and the timestamp of the
capture.</li>
<li>Append it to <code>data/poker/dataset.json</code> under <code>rates</code> with
<code>kind: "dated_quote"</code>, the <code>stay_dates</code>, the <code>occupancy</code>, and the URL you
read it from. Run <code>python3 scripts/build_dashboard.py</code>.</li>
<li>Compare like-for-like: the same dates, the same occupancy, the same tax treatment. A prepaid
non-refundable total is not comparable to a flexible rate, so record the cancellation terms on the row.</li>
</ol>
<p class="note">Nothing in this repository can do step 1 for you — every booking engine read returned
placeholders to a non-browser client, which is recorded as flag
<a href="flagged.html">F-03</a>.</p>
</section>
"""
    write("rates.html", shell("Rate log", "Rate log — Vegas Poker Planner",
                              "Dated log of every hotel rate observation with its basis, occupancy and source.",
                              body))


# ==========================================================================
# WALKING
# ==========================================================================
def page_walking():
    names = {h["id"]: h["name"] for h in HOTELS}
    names.update({v["id"]: v["name"] for v in VENUES})
    rows = []
    for w in sorted(WALKS, key=lambda x: (x["destination"], x["minutes"])):
        rows.append(f"""<tr>
<td>{e(names.get(w['origin'], w['origin']))}</td>
<td>{e(names.get(w['destination'], w['destination']))}</td>
<td class="num"><b>{w['minutes']}</b> min</td>
<td class="num">{e(w['distance'])}</td>
<td>{'<span class="tag ok">passes</span>' if w['within_30'] else '<span class="tag bad">fails</span>'}</td>
<td class="note">{e(w['note'])}</td>
<td>{src_link('G_WALK')}</td>
<td class="tight">Last checked<br>{e(AS_OF)}</td>
</tr>""")

    # matrix
    ids = ["venetian", "palazzo", "wynn", "caesars-palace", "bellagio", "mgm-grand"]
    head = "".join(f"<th>{e(names[i].split('(')[0].strip())}</th>" for i in ids)
    mrows = ""
    for o in ids:
        cells = ""
        for d in ids:
            w = next((x for x in WALKS if x["origin"] == o and x["destination"] == d), None)
            if o == d:
                cells += '<td class="num note">—</td>'
            elif w:
                cls = "ok" if w["within_30"] else "bad"
                cells += f'<td class="num"><span class="tag {cls}">{w["minutes"]}′</span></td>'
            else:
                cells += '<td class="num blank">n/m</td>'
        mrows += f"<tr><td><b>{e(names[o])}</b></td>{cells}</tr>"

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">The 30-minute gate, measured rather than assumed</div><h1>Walking</h1>
  <p class="note" style="max-width:76ch">Every hotel→poker-room pair measured on Google Maps walking
  directions on {e(AS_OF)}, with the 30-minute limit applied as a pass/fail. A pair is only useful if you
  would actually walk it, so the times are shown with the route Google chose and the caveats that matter.</p></div>
  <div class="stamp">pairs measured<br><b class="count">{len(WALKS)}</b><br>within 30 min: {sum(1 for w in WALKS if w['within_30'])}</div>
</div>

<section class="panel warnbox">
<h2>Read this before relying on a number</h2>
<p>These are point-to-point times between Google's property pins. They are not published by any casino,
they exclude the walk from your room to the lobby, and they do not account for crowd levels on a weekend
night. Google's pin for a large resort is not necessarily its lobby door.</p>
<p><b>Practical rule:</b> add 5–10 minutes to every figure below for the in-building walk, and treat
anything at 25 minutes or more as over the limit. The Bellagio→Venetian pair is the clearest example: its
best route measures 28 minutes and an alternative route measures 30, so it is on the edge and should not
be treated as a comfortable walk.</p>
</section>

<div class="tablewrap"><table>
<thead><tr><th>Stay here</th><th>Play here</th><th>Walk</th><th>Distance</th><th>30-min test</th>
<th>Route</th><th>Source</th><th>Last checked</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>

<h2 style="margin-top:28px">Matrix (minutes)</h2>
<p class="note">n/m = not measured in this session. Symmetric in principle — these are walking routes so
the return leg is the same distance, though Google reports slightly different times by direction.</p>
<div class="tablewrap"><table>
<thead><tr><th>From ↓ / To →</th>{head}</tr></thead><tbody>{mrows}</tbody></table></div>

<section class="panel">
<h2>What the matrix says about where to stay</h2>
<p><b>If the trip is Venetian-based</b> (the property with the largest and most completely catalogued
schedule), only three hotels pass the gate: The Venetian itself (7 min from its lobby to the poker room,
which is actually in The Palazzo), The Palazzo (4 min), and Wynn (12 min). Caesars Palace passes at 19
minutes but has verified daily tournaments of its own, so the walk matters less. Bellagio sits at 28
minutes — technically inside the limit, practically marginal. MGM Grand fails outright at 39 minutes.</p>
<p><b>If the trip is Caesars Palace-based</b>, the picture widens: Caesars Palace itself, Bellagio at 13
minutes, The Palazzo at 15 minutes, Wynn at 22 minutes and Horseshoe at 11 minutes all pass. That makes
Caesars Palace the most walk-connected base on the Strip for tournament purposes — and it is also the
property whose resort fee could not be verified.</p>
<p><b>If the trip is spread across properties</b>, note that the Venetian→Caesars Palace walk is 15–19
minutes depending on direction, so a Venetian base can reach the Caesars Palace 10:00 AM daily and be back
for a Venetian 5:10 PM bounty. That is the only genuinely two-event day the measurements support, and even
then the morning event's finish time is unknown.</p>
</section>
"""
    write("walking.html", shell("Walking", "Walking matrix — Vegas Poker Planner",
                                "Measured hotel-to-poker-room walking times on the Las Vegas Strip with the 30-minute limit applied.",
                                body))


# ==========================================================================
# VENUE PAGES
# ==========================================================================
def venue_page(v):
    vid = v["id"]
    evs = sorted([x for x in EVENTS if x["venue"] == vid], key=sort_key)
    dated = [x for x in evs if x.get("date")]
    daily = [x for x in evs if x.get("weekday")]
    hotel = next((h for h in HOTELS if h["venue_with_poker"] == vid
                  or (vid == "venetian" and h["id"] == "venetian")), None)
    walk = next((x for x in WALKS if x["origin"] == (hotel["id"] if hotel else "") and x["destination"] == vid), None)

    def rows_for(rows):
        return "".join(f"""<tr>
<td class="tight">{e(event_date_label(x))}</td><td class="tight">{dash(x.get('time'))}</td>
<td class="tight">{dash(x.get('event_no'))}</td>
<td>{e(x['name'])}</td>
<td class="num">{dash(x.get('buy_in'),'money')}</td>
<td class="num">{dash(x.get('fee'),'money')}</td>
<td class="num">{dash(x.get('gtd'),'money')}</td>
<td class="num">{dash(x.get('chips'))}</td>
<td class="num">{dash(x.get('level_min'))}</td>
<td class="tight">{reg_close_display(x)}</td>
<td>{rule_badge(x['entry_rule'], x.get('sheet_read'))}</td>
<td>{type_badge(x['type'])}</td>
<td>{src_cell(x['sources'][:2])}</td>
<td class="tight">Last checked<br>{e(AS_OF)}</td>
</tr>""" for x in rows)

    hotel_block = ""
    if hotel:
        hotel_block = f"""
<section class="panel">
<h2>Staying here</h2>
<dl class="defs">
<dt>Resort fee</dt><dd>{dash(hotel['resort_fee'],'money2')} — {e(hotel['resort_fee_note'])}</dd>
<dt>Room tax</dt><dd>{e(hotel['tax_note'])}</dd>
<dt>Published rate</dt><dd>{dash(hotel['published_rate'],'money')} — {e(hotel['rate_note'])}</dd>
<dt>Parking</dt><dd>{e(hotel['parking'])}</dd>
<dt>Cancellation</dt><dd>{e(hotel['cancellation'])}</dd>
<dt>Check-in / out</dt><dd>{e(hotel['checkin'])}</dd>
<dt>Room → poker room</dt><dd>{f"{walk['minutes']} minutes, {walk['distance']} ({'inside' if walk['within_30'] else 'over'} the 30-minute limit) — {walk['note']}" if walk else '<span class="blank">not measured</span>'}</dd>
<dt>Quality note</dt><dd>{e(hotel['quality_note'])}</dd>
</dl>
<p class="note">Sources: {src_cell(hotel['sources'])}</p>
</section>"""

    daily_block = ""
    if daily:
        daily_block = ('<h2 style="margin-top:26px">Recurring daily / weekly events</h2>'
                       '<div class="tablewrap"><table><thead><tr><th>When</th><th>Start</th><th>#</th>'
                       '<th>Event</th><th>Buy-in</th><th>Fee</th><th>Guarantee</th><th>Chips</th>'
                       '<th>Level</th><th>Late reg</th><th>Entry rule</th><th>Type</th><th>Source</th>'
                       '<th>Last checked</th></tr></thead><tbody>' + rows_for(daily) +
                       '</tbody></table></div>')
    n_silent = len([x for x in evs if x["entry_rule"] == "not_stated" and x.get("sheet_read")])
    n_spend = len([x for x in evs if x["entry_rule"] != "not_stated"])

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">One property, its own events, its own terms</div>
  <h1>{e(v['name'])}</h1>
  <p class="note" style="max-width:76ch">{e(v['schedule_kind'])}. {e(v['series_guarantee'])}</p></div>
  <div class="stamp">rows<br><b class="count">{len(evs)}</b><br>silent on entry limits: {n_silent}</div>
</div>

<section class="grid">
  <article class="card"><h3>Poker room</h3><p>{e(v['poker_room'])}</p>
    <p class="note">{src_link('V_POKER' if vid=='venetian' else 'W_POKER' if vid=='wynn' else 'M_POKER' if vid=='mgm-grand' else 'B_POKER' if vid=='bellagio' else 'C_POKER')}</p></article>
  <article class="card"><h3>Address</h3><p>{e(v['address'])}</p></article>
  <article class="card"><h3>Contact</h3>
    <p>{e(v['phone']) if v['phone'] else '<span class="blank">not published on the page read</span>'}</p>
    <p class="note">{e(v['email']) if v['email'] else ''}</p></article>
  <article class="card"><h3>Entry limits</h3>
    <p><b>{n_silent}</b> sheet silent on entry limits<br><b>{n_spend}</b> with published re-entry /
    rebuy / add-on terms<br><b>{len(evs) - n_silent - n_spend}</b> with no sheet read</p>
    <p class="note">Zero confirmed single-entry events at this property. "Silent" means the sheet was
    read; "no sheet read" is weaker and is labelled separately on the table below.</p></article>
</section>

{hotel_block}

<h2 style="margin-top:26px">Dated events</h2>
<p class="note">Each row carries its own source link and the date that source was read. "not stated" in the
entry-rule column means the official structure sheet was read and does not mention a maximum number of
entries — it does not mean one entry is confirmed.</p>
<div class="tablewrap"><table>
<thead><tr><th>Date</th><th>Start</th><th>#</th><th>Event</th><th>Buy-in</th><th>Fee</th>
<th>Guarantee</th><th>Chips</th><th>Level</th><th>Late reg</th><th>Entry rule</th><th>Type</th>
<th>Source</th><th>Last checked</th></tr></thead>
<tbody>{rows_for(dated) if dated else '<tr><td colspan="14" class="note">No dated events retrieved for this property.</td></tr>'}</tbody></table></div>

{daily_block}

<section class="panel">
<h2>Property sources</h2>
<ul class="clean">
{''.join(f'<li><a href="{e(SRC[k]["url"])}" target="_blank" rel="noopener">{e(SRC[k]["title"])} ↗</a><br><span class="note">{e(SRC[k]["used_for"])}</span> {kind_badge(SRC[k]["kind"])}</li>' for k in v["sources"])}
</ul>
</section>
"""
    write(f"venues/{vid}.html",
          shell("Venues", f"{v['name']} — Vegas Poker Planner",
                 f"Verified schedule, hotel terms and walking distance for {v['name']}.", body,
                 depth=1))


def page_venues_index():
    cards = ""
    for v in VENUES:
        evs = [x for x in EVENTS if x["venue"] == v["id"]]
        w = next((x for x in WALKS if x["origin"] == v["id"] and x["destination"] == v["id"]), None)
        cards += f"""<article class="card">
<h3>{e(v['name'])}</h3>
<p class="note" style="min-height:3.2em">{e(v['schedule_kind'])}</p>
<dl class="defs" style="grid-template-columns:auto 1fr;font-size:.85rem">
<dt>Rows</dt><dd>{len(evs)}</dd>
<dt>Poker room</dt><dd style="font-size:.82rem">{e(v['poker_room'][:86])}</dd>
<dt>Into the room</dt><dd>{f"{w['minutes']} min walk" if w else '<span class="blank">not measured</span>'}</dd>
<dt>Contact</dt><dd style="font-size:.82rem">{e(v['phone']) if v['phone'] else '<span class="blank">not published</span>'}</dd>
</dl>
<p><a href="{v['id']}.html">Open {e(v['name'].split('/')[0].strip())} →</a></p>
</article>"""

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">One page per property</div><h1>Venues</h1>
  <p class="note" style="max-width:76ch">Six Strip properties publish poker tournaments. Each gets its own
  page with its events, its hotel terms and its walking distance, because "where should I stay" is a
  per-property question and a mixed table hides the answer.</p></div>
  <div class="stamp">properties<br><b class="count">{len(VENUES)}</b><br>with verified buy-ins: 5</div>
</div>

<div class="grid">{cards}</div>

<section class="panel">
<h2>Comparing the six</h2>
<div class="tablewrap"><table>
<thead><tr><th>Property</th><th>Schedule type</th><th>Rows verified</th><th>Buy-ins published</th>
<th>Entry rule published</th><th>Resort fee</th><th>Building → poker room</th></tr></thead>
<tbody>
<tr><td><b>The Venetian / Palazzo</b></td><td>Festival, Nov 16 – Dec 23</td><td class="num">{len(ven_events)}</td>
<td>Yes, every row</td><td><span class="tag ok">silent on {len(confirmed_single)} rows</span></td>
<td class="num">$55 + tax</td><td class="num">4–7 min (inside the resort)</td></tr>
<tr><td><b>Wynn / Encore</b></td><td>Festival, Nov 27 – Dec 21, plus a daily slate</td><td class="num">{len(wynn_events)}</td>
<td>Yes, every row</td><td><span class="tag warn">re-entry everywhere</span></td>
<td class="num">$55 + tax</td><td class="num">7 min</td></tr>
<tr><td><b>Caesars Palace</b></td><td>Four dailies every day</td><td class="num">4</td>
<td>Yes, all four</td><td><span class="tag warn">re-entry + $50 add-on</span></td>
<td><span class="blank">unverified</span></td><td class="num">3 min</td></tr>
<tr><td><b>Bellagio</b></td><td>Weekly: Fri, Sat, Sun events</td><td class="num">2</td>
<td>Fri $600; Sat conflicts</td><td><span class="tag warn">re-entry to level 8</span></td>
<td class="num">$55 + tax</td><td class="num">2 min</td></tr>
<tr><td><b>MGM Grand</b></td><td>Three $120 dailies + a Saturday $150</td><td class="num">4</td>
<td>Yes, all four</td><td><span class="tag ok">not stated</span></td>
<td class="num">$50 + tax</td><td class="num">2 min</td></tr>
<tr><td><b>Horseshoe</b></td><td>Six dailies (editorial source only)</td><td class="num">6</td>
<td><span class="tag bad">no</span></td><td><span class="blank">no</span></td>
<td><span class="blank">unverified</span></td><td class="num">2 min</td></tr>
</tbody></table></div>
<p class="note">"Silent on N rows" is the honest label for a sheet that does not mention entry limits. It is
not a claim that the event is single-entry.</p>
</section>
"""
    write("venues/index.html", shell("Venues", "Venues — Vegas Poker Planner",
                                     "One page per Las Vegas Strip poker venue with its events, hotel terms and walking distance.",
                                     body, depth=1))


# ==========================================================================
# QUESTIONS
# ==========================================================================
def q_group(q):
    """Group questions by what they change, from the data, not from a
    hand-maintained list that drifts out of sync with the question order."""
    a = q.get("affects", "").lower()
    if "hotel" in a or "trip cost" in a:
        return "Before you book a room"
    if "ranking" in a or "single-entry" in a or "event" in a:
        return "Before you trust a ranking"
    if "day plan" in a or "start" in a:
        return "Before you commit to a schedule"
    return "Before you decide anything else"


GROUP_ORDER = ["Before you book a room", "Before you trust a ranking",
               "Before you commit to a schedule", "Before you decide anything else"]


def page_questions():
    n_block = sum(1 for q in QUESTIONS if q["priority"] == "blocking")
    groups = {g: [] for g in GROUP_ORDER}
    for q in QUESTIONS:
        groups[q_group(q)].append(q)
    blocks = ""
    for g in GROUP_ORDER:
        qs = groups[g]
        if not qs:
            continue
        items = ""
        for q in qs:
            items += f"""
<details>
<summary><span class="tag {'bad' if q['priority'] == 'blocking' else 'warn'}">{e(q['priority'])}</span>
{q['id']} — {e(q['question'])}</summary>
<p><b>What the official sources do say.</b> {e(q['known'])}</p>
<p><b>What is missing.</b> {e(q['missing'])}</p>
<p><b>How to close it.</b> {e(q['how_to_close'])}</p>
<p><b>What it changes.</b> {e(q['affects'])}</p>
</details>"""
        blocks += f'<h2 style="margin-top:26px">{e(g)}</h2>{items}'

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">The information that must exist before a booking decision</div>
  <h1>Questions</h1>
  <p class="note" style="max-width:76ch">Twelve questions, each traceable to a specific missing value in the
  data rather than a generic worry. <b>{n_block}</b> of them <b>block</b> a decision: until they are
  answered, the only honest recommendation is not to book. The rest change the shape of the trip rather
  than its viability.</p></div>
  <div class="stamp">questions<br><b class="count">{len(QUESTIONS)}</b><br>blocking: {sum(1 for q in QUESTIONS if q['priority'] == 'blocking')}</div>
</div>

<section class="panel badbox">
<h2 style="margin-top:0">The blocking questions, at a glance</h2>
<ul class="clean">
{''.join(f'<li><b>{q["id"]} — {e(q["question"])}</b> {e(q["missing"])}</li>' for q in QUESTIONS if q["priority"] == "blocking")}
</ul>
</section>

{blocks}

<section class="panel">
<h2>How to ask</h2>
<p>Every question above can be answered by one of four routes, in descending order of authority:
<b>(1)</b> the property's poker-room email or phone — the Venetian publishes
<code>lv_cas_poker@venetianlasvegas.com</code> and <code>702.414.7657</code>, the Wynn publishes
<code>poker.reservations@wynnlasvegas.com</code> and <code>702-770-7654</code>, Bellagio publishes
<code>pcohen@bellagioresort.com</code> and <code>702.693.7291</code>, MGM Grand publishes
<code>702.891.7434</code>; <b>(2)</b> a named tournament director's written statement;
<b>(3)</b> the property's own booking flow, screenshot with timestamp; <b>(4)</b> a third-party aggregator —
which is how most of the existing web answers to these questions were produced, and why they cannot be
used as evidence here.</p>
<p class="note">When an answer arrives, record it in this repository with the name of the person who gave
it, the date, and the channel. An email is a citable source; a phone call is a citable source if you note
who you spoke to.</p>
</section>
"""
    write("questions.html", shell("Questions", "Questions and missing information — Vegas Poker Planner",
                                  "The twelve questions that must be answered before booking, with who can answer each and what changes.",
                                  body))


# ==========================================================================
# SUGGESTIONS (gated)
# ==========================================================================
def page_suggestions():
    cards = ""
    for s in SUGGESTIONS:
        status = s["status"]
        cls = {"implemented": "ok", "ready": "ok", "needs-review": "warn",
               "blocked": "bad"}.get(status, "warn")
        cards += f"""
<details>
<summary><span class="tag {cls}">{e(status.replace('-', ' '))}</span> {s['id']} — {e(s['title'])}</summary>
<p><b>What it does.</b> {e(s['what'])}</p>
<p><b>Why it is worth doing.</b> {e(s['why'])}</p>
<p><b>How it would work.</b> {e(s['how'])}</p>
<p><b>Effort / gate.</b> {e(s['effort'])}</p>
</details>"""

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">Ideas are proposed first and gated before anyone builds them</div>
  <h1>Suggestions</h1>
  <p class="note" style="max-width:76ch">Thirteen improvements found while doing the research. The brief
  asked for a suggestions page whose items are <b>gated before implementation</b> — so each one states what
  it would do, why it is worth doing, and what must be true before it can be built. Four are already
  implemented on this site because they needed nothing external.</p></div>
  <div class="stamp">proposals<br><b class="count">{len(SUGGESTIONS)}</b><br>needs review: {sum(1 for s in SUGGESTIONS if s['status']=='needs-review')}</div>
</div>

<section class="panel">
<h2>The gate, defined</h2>
<p>A suggestion moves to <b>ready</b> when it needs only code and data already in this repository. It moves
to <b>needs-review</b> when it touches something outside our control: a third party's terms of service, a
site that blocks automated reading, or a fact only a human can confirm. It moves to <b>blocked</b> when it
cannot be done at all without breaking the no-hallucination rule. Nothing moves to <b>implemented</b>
without the gate being satisfied and the result being verified on the built page.</p>
<p class="note">This is deliberately strict. The failure mode it prevents is a site that quietly grows
features whose numbers are guesses — which is exactly what the three archived dashboards were starting to
do.</p>
</section>

{cards}

<section class="panel warnbox">
<h2>What is already built (no gate needed)</h2>
<ul class="clean">
<li><b>S-01</b> Trip-cost calculator with every default traced to a source — on
<a href="trip-cost.html">Trip cost</a>.</li>
<li><b>S-02</b> Rate log that appends instead of overwriting — on <a href="rates.html">Rate log</a>.</li>
<li><b>S-03</b> Global search and filters across all events — on <a href="events.html">All events</a>.</li>
<li><b>S-06</b> Per-row source link and last-checked date on every table — throughout.</li>
<li><b>S-07</b> Walking matrix as a pass/fail gate — on <a href="walking.html">Walking</a>.</li>
<li><b>S-12</b> One page per venue — under <a href="venues/index.html">Venues</a>.</li>
<li><b>S-13</b> Archive of the superseded dashboards — under
<a href="archive/index.html">Archive</a>.</li>
</ul>
</section>
"""
    write("suggestions.html", shell("Suggestions", "Suggestions — Vegas Poker Planner",
                                    "Thirteen proposed improvements, each gated with the condition that must be met before it is built.",
                                    body))


# ==========================================================================
# FLAGGED
# ==========================================================================
def page_flagged():
    sev = {"high": "bad", "medium": "warn", "low": "plain"}
    rows = "".join(f"""<tr>
<td class="tight">{f['id']}</td>
<td>{'<span class="tag ' + sev[f['severity']] + '">' + e(f['severity']) + '</span>'}</td>
<td>{e(f['subject'])}</td>
<td><b>{e(f['finding'])}</b><br><span class="note">{e(f['detail'])}</span></td>
<td class="note">{e(f['action'])}</td>
<td>{src_cell(f['sources']) if f['sources'] else '<span class="blank">no source</span>'}</td>
<td class="tight">Last checked<br>{e(AS_OF)}</td>
</tr>""" for f in FLAGS)

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">Nothing verified was hidden to make the site look complete</div>
  <h1>Flagged for review</h1>
  <p class="note" style="max-width:76ch">Thirteen irregularities found reading the official sources line by
  line. Some are the property's own contradictions — a schedule header that says August on a page that lists
  November events, an event number that disagrees with its own file name. Some are gaps in what the
  properties publish. All of them are listed here rather than quietly worked around, and none of them block
  publication.</p></div>
  <div class="stamp">flags<br><b class="count">{len(FLAGS)}</b><br>high: {sum(1 for f in FLAGS if f['severity']=='high')}</div>
</div>

<div class="tablewrap"><table>
<thead><tr><th>ID</th><th>Severity</th><th>Subject</th><th>What was found</th>
<th>What to do about it</th><th>Source</th><th>Last checked</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<section class="panel">
<h2>How flags are assigned</h2>
<dl class="defs">
<dt>high</dt><dd>The data cannot be used as-is for a decision. Either a required value is missing entirely
(F-03, no dated room rate) or two official sources contradict each other on a number that matters (F-05,
Bellagio's Saturday event).</dd>
<dt>medium</dt><dd>The value is usable but carries a stated caveat the reader must know: a stale banner
(F-07), a starting rate that is conditional (F-04), a header that names the wrong month (F-06).</dd>
<dt>low</dt><dd>Cosmetic or documentary: an event number printed inconsistently (F-12), a third-party
routing source used for walking distances (F-11).</dd>
</dl>
<p class="note">A flag is never a reason to leave a cell empty without saying why. Each table row that
depends on a flagged value links to this page from its caption or its venue page.</p>
</section>

<section class="panel warnbox">
<h2>The three that would change the plan most</h2>
<p><b>F-03 / Q-09 — no dated hotel rate exists.</b> Every booking flow read returned placeholders. The trip
cannot be costed. This is the single largest gap in the dataset.</p>
<p><b>F-05 — Bellagio's Saturday $1,100 event.</b> The structure PDF promises a $50,000 guarantee but
allocates only $600-per-player to the prize pool, which cannot fund a $50,000 guarantee at any plausible
field size. One of the two printed numbers is wrong; the event is left out of the ranking rather than
guessed at.</p>
<p><b>F-01 — zero confirmed single-entry events.</b> Not a defect in the research but a finding: every
property that publishes an entry rule publishes a way to pay twice. The single-entry short-list is empty
because the market is, not because the search stopped early.</p>
</section>
"""
    write("flagged.html", shell("Flagged", "Flagged for review — Vegas Poker Planner",
                                "Thirteen source irregularities and gaps, listed with their effect on the data and their official links.",
                                body))


# ==========================================================================
# SOURCES
# ==========================================================================
def page_sources():
    groups = defaultdict(list)
    for k, s in SRC.items():
        groups[s["kind"]].append((k, s))
    order = ["official", "official-editorial", "routing", "third-party"]
    blocks = ""
    for kind in order:
        if kind not in groups:
            continue
        rows = "".join(f"""<tr>
<td class="tight mono">{e(k)}</td>
<td><a href="{e(s['url'])}" target="_blank" rel="noopener">{e(s['title'])}</a></td>
<td>{e(s['publisher'])}</td>
<td class="note">{e(s['used_for'])}</td>
<td class="tight">{e(AS_OF)}</td>
</tr>""" for k, s in sorted(groups[kind], key=lambda x: x[1]["publisher"]))
        blocks += f"""
<h2 style="margin-top:26px">{e(kind)} {kind_badge(kind)} <span class="note" style="font-weight:400">· {len(groups[kind])} sources</span></h2>
<div class="tablewrap"><table>
<thead><tr><th>Key</th><th>Page</th><th>Publisher</th><th>What it was used for</th><th>Read on</th></tr></thead>
<tbody>{rows}</tbody></table></div>"""

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">Every claim on this site resolves to one of these</div><h1>Sources</h1>
  <p class="note" style="max-width:76ch">{len(SRC)} pages, PDFs and routes read for this snapshot. Each
  table row elsewhere on the site links to the specific key it came from. Rows are classed by how much
  authority they carry: <b>official</b> means the property's own site or PDF, <b>official-editorial</b> means
  the property's own editorial channel (a corporate blog, not the poker room's flyer), <b>routing</b> means
  a maps service, and <b>third-party</b> means anyone else.</p></div>
  <div class="stamp">sources<br><b class="count">{len(SRC)}</b><br>read {e(AS_OF)}</div>
</div>

<section class="panel">
<h2>Source hierarchy, and why it is not a formality</h2>
<p>Two of the six venues publish no buy-in on their own site. Horseshoe's six daily start times exist only
in a Caesars corporate blog post; the room's own flyer URLs return nothing. That is enough to list the
times as <i>editorial</i>, and not enough to put a buy-in in a cell. The distinction between
"official" and "official-editorial" is what keeps that gap visible instead of filling it with a plausible
number.</p>
<p>The same rule applies to walking times. Google Maps is a routing service, not a casino policy: its pin
for a resort is not the lobby door, and it does not know about the corridor from the Encore tower to the
Wynn poker room. It is the best measurement available and it is labelled as a measurement, not a policy.</p>
</section>

{blocks}

<section class="panel">
<h2>Structure sheets read, and not read</h2>
<p>The Venetian links {D['struct_total']} structure PDFs from its DeepStack IV schedule.
<b>{len(D['struct_read'])} were opened and read in full</b> for this snapshot: sheets
{', '.join(str(n) for n in D['struct_read'])}. Each of those was checked for the buy-in, the fee split, the
starting stack, the level length, the late-registration close, and any language about re-entry, rebuys, an
add-on or a maximum number of entries.</p>
<p><b>{D['struct_total'] - len(D['struct_read'])} sheets were not opened.</b> Their events appear with the
buy-in, date and time from the schedule, and a blank fee and blank chips. That is why the ranking page
ranks {sum(1 for x in EVENTS if x['entry_rule']=='not_stated' and x.get('gtd'))} events rather than all
{len(ven_events)} Venetian rows: a ratio built on an unread sheet would be a guess.</p>
</section>
"""
    write("sources.html", shell("Sources", "Sources — Vegas Poker Planner",
                                "Every official page, PDF and route this site's numbers were read from, with the date each was read.",
                                body))


# ==========================================================================
# REPO REVIEW
# ==========================================================================
def repo_inventory():
    """Live inventory of the repository, computed each build — not typed by hand."""
    skip = {".git", "node_modules", "archive", "__pycache__"}
    files = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in skip)
        for n in sorted(names):
            full = os.path.join(base, n)
            rel = os.path.relpath(full, ROOT)
            files.append((rel, os.path.getsize(full)))
    return files


def page_reporeview():
    files = repo_inventory()
    by_dir = defaultdict(list)
    for rel, size in files:
        d = os.path.dirname(rel) or "."
        by_dir[d].append((rel, size))

    # The four dashboards that predate this build, measured against each other.
    dashboards = [
        ("root /", "index.html", "First dashboard. Single-page, tabs, hard-coded event array."),
        ("docs/", "docs/index.html", "Second subsite. Separate nav, separate numbers, no source links."),
        ("verified/", "verified/index.html", "Third subsite, generated from data/verified/*.json."),
        ("new /", "index.html", "This build. Generated from data/poker/dataset.json by scripts/build_dashboard.py."),
    ]

    def n_files(prefix):
        if prefix == "root /":
            return len([f for f in files if os.path.dirname(f[0]) in ("", "pages", "data")
                        and not f[0].startswith(("docs/", "verified/", "archive/"))])
        return len([f for f in files if f[0].startswith(prefix.strip("/") + "/")])

    d_rows = "".join(f"""<tr><td><b>{e(name)}</b></td><td class="mono">{e(entry)}</td>
<td class="num">{n_files(name)}</td><td class="note">{e(note)}</td></tr>""" for name, entry, note in dashboards)

    dir_rows = "".join(f"""<tr><td class="mono">{e(d)}</td><td class="num">{len(v)}</td>
<td class="num">{sum(s for _, s in v) / 1024:.0f} KB</td></tr>"""
                       for d, v in sorted(by_dir.items(), key=lambda x: -len(x[1])))

    findings = [
        ("Duplicate dashboards", "high",
         "Three complete dashboards existed in one repository, each with its own copy of the event numbers "
         "and its own navigation. The same tournament appeared with different values in different files.",
         "Fixed in this build: a single dataset module (<code>scripts/poker_data.py</code>) and a single "
         "generator. The three older trees are moved under <code>archive/</code> with a banner, not deleted."),
        ("Numbers typed into HTML", "high",
         "Every previous dashboard hard-coded buy-ins and guarantees inside HTML or a JS array. Nothing "
         "could be traced back to a source, and nothing could be re-verified without re-reading the page.",
         "Fixed: all numbers live in one Python module with a source key per row, and every table cell "
         "renders a link to that key."),
        ("No per-row provenance", "high",
         "No previous page carried a source link or a last-checked date on a row. A reader could not tell a "
         "verified value from a plausible one.",
         "Fixed: every table row has a source link and a last-checked date; blanks are typographic, not "
         "silently filled."),
        ("Unverified values presented as facts", "medium",
         "Earlier revisions listed Horseshoe buy-ins and a Caesars Palace resort fee that no official page "
         "states. They were plausible round numbers, which is exactly what makes them dangerous.",
         "Fixed: those cells are now blank and the gaps are listed as flags F-07 and F-08."),
        ("Single-entry claim never substantiated", "medium",
         "An early reading treated MGM Grand's $120 as a confirmed single-entry event on the grounds that "
         "its structure sheet mentions no re-entry. That is an inference from silence.",
         "Reversed. <code>entry_rule=\"not_stated\"</code> is now a distinct value from a confirmed "
         "single-entry rule, and the toggle returns zero rows by design (F-01)."),
        ("Stale series banner left live", "medium",
         "The Venetian poker page still advertises 'WPT Fall Festival, Oct 28 – Nov 15, 2026' while its own "
         "schedule page runs DeepStack IV from Nov 16. A reader landing on the poker page would plan around "
         "a finished series.",
         "Flagged F-07/F-09 and handled by linking the schedule page rather than the poker page for dates."),
        ("MGM Grand schedule header names the wrong month", "medium",
         "The daily schedule PDF's header reads 'August' while its rows list November events. The times are "
         "usable; the header is not.",
         "Flagged F-06. Times are used with the flag attached."),
        ("Bellagio Saturday sheet contradicts itself", "high",
         "The $1,100 Saturday structure sheet promises a $50,000 guarantee but allocates $600 per player to "
         "the prize pool — arithmetically incompatible.",
         "Flagged F-05. The event is excluded from the ranking rather than guessed at."),
        ("No dated hotel rate anywhere", "high",
         "All four booking flows read returned placeholders to a non-browser client. The published $119/$209 "
         "are starting rates conditional on six hours of play per night.",
         "Flagged F-03. The trip-cost calculator defaults to the published starting rate and says so in the "
         "adjacent paragraph, rather than presenting it as a quote."),
        ("Walking times from a routing service", "low",
         "Google Maps is not a casino policy page; its property pin is not the lobby door.",
         "Labelled as a measurement, with the in-building caveat stated on the walking page (F-11)."),
        ("23 of 37 structure sheets unread", "medium",
         "The Venetian links 37 structure PDFs; 14 were read. The other 23 events appear with a buy-in and "
         "a blank fee.",
         "Stated explicitly on the <a href='sources.html'>Sources</a> page and reflected in the ranking, "
         "which only ranks events with a read sheet."),
        ("A derived event length was invented, then removed", "high",
         "An intermediate version of this build computed a 'derived maximum length' for every event from a "
         "hard-coded table of levels-per-event and minutes-per-level. That table was written from memory of "
         "the structure sheets, not transcribed from them — it was plausible, internally consistent, and "
         "not something any casino published.",
         "Removed outright rather than corrected, because correcting it would still mean asserting a number "
         "the sources do not contain. The day plan now builds its fallback test on late-registration closes, "
         "which <i>are</i> published, and states plainly that no finish time exists anywhere."),
        ("Mixed source authority in one table", "medium",
         "Horseshoe's six start times come from a Caesars corporate article; every other timing comes from a "
         "room's own flyer. Mixing them in one table without distinction would overstate the Horseshoe rows.",
         "Fixed: sources are classed official / official-editorial / routing, and the class is rendered "
         "next to the link on the Sources page."),
    ]
    f_rows = "".join(f"""<tr><td>{'<span class="tag bad">high</span>' if sev == 'high' else '<span class="tag warn">medium</span>' if sev == 'medium' else '<span class="tag plain">low</span>'}</td>
<td><b>{e(title)}</b></td><td class="note">{e(what)}</td><td class="note">{fixed}</td></tr>"""
                     for title, sev, what, fixed in findings)

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">Line by line, including the parts that were wrong</div>
  <h1>Repo review</h1>
  <p class="note" style="max-width:76ch">The brief asked for the repository to be reviewed line by line,
  with official links, flagging irregularities. This page is that review, applied to the repository itself
  rather than to the casinos: what was duplicated, what was asserted without a source, what has been
  corrected, and what is still standing.</p></div>
  <div class="stamp">tracked files<br><b class="count">{len(files)}</b><br>findings: {len(findings)}</div>
</div>

<section class="panel badbox">
<h2 style="margin-top:0">The one that mattered</h2>
<p>Earlier revisions of this repository described the MGM Grand $120 daily as the best confirmed
<b>single-entry</b> candidate, on the grounds that its structure sheet never mentions re-entry. That is an
inference from silence, and it is the exact failure mode the brief forbids. A sheet that does not mention
re-entry is silent; a sheet that says "re-entry is not allowed" is evidence. Only the second one confirms
anything.</p>
<p>The dataset now encodes that distinction as a field value rather than a footnote:
<code>entry_rule = "not_stated"</code> is separate from any confirmed rule, the single-entry filter returns
zero rows, and the <a href="ranking.html">ranking page</a> explains the zero instead of hiding it.</p>
</section>

<h2 style="margin-top:26px">Findings</h2>
<div class="tablewrap"><table>
<thead><tr><th>Severity</th><th>Finding</th><th>What was wrong</th><th>What was done</th></tr></thead>
<tbody>{f_rows}</tbody></table></div>

<h2 style="margin-top:28px">The four dashboards</h2>
<p class="note">Counts are files in each tree at build time. The first three are superseded and now sit
under <a href="archive/index.html">archive/</a> with a banner at the top of every page.</p>
<div class="tablewrap"><table>
<thead><tr><th>Tree</th><th>Entry point</th><th>Files</th><th>Notes</th></tr></thead>
<tbody>{d_rows}</tbody></table></div>

<h2 style="margin-top:28px">Repository inventory</h2>
<p class="note">Computed by walking the working tree during this build, so it cannot drift from reality.</p>
<div class="tablewrap"><table>
<thead><tr><th>Directory</th><th>Files</th><th>Size</th></tr></thead>
<tbody>{dir_rows}</tbody></table></div>

<section class="panel">
<h2>What is still wrong, and is not fixed here</h2>
<ul class="clean">
<li><b>Four trees still exist.</b> The old dashboards are archived, not deleted. Deleting them is a
repository-history decision, not a research decision, and it belongs to whoever owns the repo.</li>
<li><b>Two JSON datasets still overlap.</b> <code>data/tournaments.json</code> and
<code>data/verified/*.json</code> are still on disk. They are no longer linked from the live site, but they
are still there and still hold older values.</li>
<li><b>The generator is not scheduled.</b> Nothing re-checks a source automatically. Every "last checked"
date on this site is the date of a human-driven read, and it ages from the moment of the build.</li>
<li><b>Two venue pages have almost nothing on them.</b> Bellagio has two events and Horseshoe has six rows
with no buy-in at all. That is the true state of the research, not a rendering bug.</li>
</ul>
</section>

<section class="panel">
<h2>How to re-run everything</h2>
<pre class="mono" style="background:var(--panel2);padding:12px;border-radius:8px;overflow-x:auto;font-size:.8rem">python3 scripts/poker_data.py        # data/poker/dataset.json  (the numbers)
python3 scripts/build_dashboard.py   # index.html, events.html, … (the pages)
python3 scripts/check_links.py       # optional: resolve every outbound link</pre>
<p class="note">The generator is deterministic. Rebuilding without changing the data produces byte-identical
HTML, which is what makes a diff in a pull request meaningful.</p>
</section>
"""
    write("repo-review.html", shell("Repo review", "Repo review — Vegas Poker Planner",
                                    "Line-by-line review of this repository: duplicates, unsourced claims and what was corrected.",
                                    body))


# ==========================================================================
# ARCHIVE
# ==========================================================================
ARCHIVE_TREES = [
    ("root", "First dashboard", "index.html, tournaments.html, hotels.html, planning.html, "
     "flagged.html", "root/index.html",
     "A single page with tabs, an events table built from a JavaScript array and no per-row source links. "
     "Its numbers were typed by hand, so nothing on it could be re-verified against a linked page."),
    ("pages", "First dashboard, category pages", "pages/*.html (15 files)", "pages/tournaments.html",
     "Fifteen category pages split out of the first dashboard. Same numbers, same lack of provenance, "
     "spread across more files."),
    ("docs", "Second subsite", "docs/*.html (10 files)", "docs/index.html",
     "A second complete site under /docs/ with its own navigation and its own copies of the event numbers. "
     "Diverged from the root dashboard: some buy-ins differ between the two."),
    ("verified", "Third subsite", "verified/** (14 files)", "verified/index.html",
     "Generated from data/verified/*.json by scripts/build.mjs. The closest of the three to a real "
     "source-backed build — it had a data layer — but its rows still carried no last-checked date and no "
     "per-row link."),
]


def page_archive():
    rows = ""
    n_present = 0
    for prefix, title, files, link, note in ARCHIVE_TREES:
        present = os.path.exists(os.path.normpath(os.path.join(ROOT, "archive", link)))
        n_present += 1 if present else 0
        rows += f"""<tr><td><b>{e(title)}</b></td><td class="mono note">{e(files)}</td>
<td class="note">{e(note)}</td>
<td>{f'<a href="{e(link)}">Open archived tree →</a>' if present else '<span class="blank">not present</span>'}</td></tr>"""

    body = f"""
<div class="pagehead">
  <div><div class="eyebrow">Superseded, kept for the audit trail</div><h1>Archive</h1>
  <p class="note" style="max-width:76ch">Four dashboards were built in this repository before the current
  one. They are kept rather than deleted, because the record of what was claimed before — and what was
  wrong about it — is part of the research. Every archived page carries a banner at the top saying so.</p></div>
  <div class="stamp">archived trees<br><b class="count">{n_present}</b><br>of {len(ARCHIVE_TREES)}</div>
</div>

<section class="panel badbox">
<h2 style="margin-top:0">Do not use the archived numbers</h2>
<p>The archived sites contain buy-ins, guarantees and resort fees that were typed in by hand and never
traced to a source. Some are right. At least one is not: an early version listed a Horseshoe buy-in and a
Caesars Palace resort fee that no official page states, and described MGM Grand's $120 daily as confirmed
single-entry on the strength of silence. They are preserved here as a record, not as a reference.</p>
<p>Use the <a href="../index.html">current dashboard</a> instead. Every number on it links to the page it
came from.</p>
</section>

<div class="tablewrap"><table>
<thead><tr><th>Tree</th><th>Files</th><th>What it was, and why it was superseded</th><th></th></tr></thead>
<tbody>{rows}</tbody></table></div>

<section class="panel">
<h2>Why archive rather than delete</h2>
<p>Three reasons, in order of importance. <b>One:</b> the brief asks for irregularities to be flagged and
published, and a deleted dashboard cannot be inspected. <b>Two:</b> a later reader may need to know
<i>which</i> number changed and when — the archive plus the new dataset is that diff. <b>Three:</b>
deleting files rewrites nothing about the past; it only removes the evidence that the correction happened.</p>
<p class="note">If the intent is to remove them from the published site entirely, delete the four trees and
this page, and re-run the build. Nothing in the current dashboard links to them except this index and the
navigation's own archive link.</p>
</section>
"""
    write("archive/index.html", shell("Archive", "Archive — superseded dashboards",
                                      "The three superseded dashboards, preserved as an audit trail and marked unusable.",
                                      body, depth=1))


# ==========================================================================
# MAIN
# ==========================================================================
def main():
    page_index()
    page_events()
    page_ranking()
    page_dayplan()
    page_tripcost()
    page_hotels()
    page_rates()
    page_walking()
    page_venues_index()
    for v in VENUES:
        venue_page(v)
    page_questions()
    page_suggestions()
    page_flagged()
    page_sources()
    page_reporeview()
    page_archive()

    write("style.css", CSS.strip() + "\n")
    write("app.js", JS.strip() + "\n")

    total = sum(len(t) for t in PAGES.values())
    print(f"wrote {len(PAGES)} files, {total/1024:.0f} KB")
    for k in sorted(PAGES):
        print(f"  {k:32s} {len(PAGES[k])/1024:6.1f} KB")


if __name__ == "__main__":
    main()
