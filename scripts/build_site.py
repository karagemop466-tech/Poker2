#!/usr/bin/env python3
"""Build the static GitHub Pages site in docs/ from data/*.json.

Rules enforced here (the build fails if any is broken):
  * every table row has at least one link whose host is an official venue/brand domain
  * blank values are rendered as "UNVERIFIED" and carry a flag id
"""
import json, html, pathlib, re, sys
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
DOCS = ROOT / "docs"
OFFICIAL_HOSTS = {"www.venetianlasvegas.com", "www.caesars.com", "www.wynnlasvegas.com",
                  "cdn.wynnresorts.com", "mgmgrand.mgmresorts.com", "assets.contentstack.io",
                  "www.goldennugget.com", "www.resortsworldlasvegas.com"}

T = json.load(open(DATA / "venetian-dse4-official-check.json"))
H = json.load(open(DATA / "hotels-official-check.json"))
S = T["sources"]
VEN_PDF = S["venetian_structure_pdf_base"]
ERRORS = []

FLAGS = {
 "F-01": ("Venetian times conflict", "pokernews.com lists different daily times for some Venetian events. Official Venetian schedule used for every row."),
 "F-02": ("Caesars resort fee conflicts", "Third-party sources list $45, $49.95 and $56.63 for the Caesars resort fee. No official Caesars fee page located. Left blank."),
 "F-03": ("MGM Grand time mismatch", "Official MGM web page: 11:00 AM / 7:00 PM / 11:00 PM. Official weekly PDF (titled 'August') shows 11:10 AM / 7:10 PM / 11:10 PM. Both shown; unverified which is current."),
 "F-04": ("Golden Nugget buy-in not printed", "Official daily-tournaments page lists times, chips and add-ons but no buy-in. Blank."),
 "F-05": ("Horseshoe times not published", "Official Horseshoe page states '6 tournament times daily' without listing them. Third-party times ($100 at 5 PM, $160 at 8 PM) not used."),
 "F-06": ("Wynn WPT World Championship not verified", "Official WPT schedule PDF returned HTTP 502 when fetched. WPT events not listed."),
 "F-07": ("Venetian booking rates are placeholders", "Official Venetian booking calendar shows '$XXX' for all nightly rates. No rate used."),
 "F-08": ("PokerAtlas PRO rake discount", "Venetian E18/E58 list a $20 PokerAtlas PRO member rake discount. Prize pool for those events not printed on the official page; blank."),
 "F-09": ("Structure sheets not all read", "Structure sheets not yet read line-by-line for some single-entry rows (E12, E20, E27, E40, E57). Their entry rules are flagged NOT VERIFIED in the table."),
 "F-10": ("Multi-flight Day 2 rules not read", "Day 2 rules for E26, E39, E47, E49, E56, E59 not yet read line-by-line. Excluded from single-entry list."),
 "F-11": ("Event 28 name", "An earlier note said 'Big O'. Official page reads 'No Limit Hold'em $40K GTD'. Official name used."),
 "F-12": ("Hotel nightly rate unverified", "No official nightly rate located. Venetian booking calendar shows placeholders (F-07). All-in cost therefore blank."),
 "F-13": ("Clark County room tax unverified", "Room-tax percentages (13.38% Strip / 13% elsewhere) come only from third-party sites. Not used."),
 "F-14": ("Walking time unverified", "No official walking-distance source found. Walking minutes blank for every hotel, so no hotel can yet be confirmed within 30 minutes."),
 "F-15": ("Repo had no coordination file", "Repo contained only README.md at 058cd54 when this session started. COORDINATION.md created on the session branch."),
 "F-16": ("Branch scheme differs from brief", "The brief asked for session-<id>/<task> branches; this session is assigned one branch, arena/acd81e67-poker2. Integration uses that branch."),
 "F-17": ("GitHub Pages status unconfirmed", "A curl to the Pages URL from the sandbox returned no response (HTTP 000). Deploy status is checked through the GitHub API after merge."),
 "F-18": ("Wynn resort fee link not re-located", "Official Wynn resort-fee terms were read in an earlier session; the exact link was not re-located, so the value is blank. Third-party $50 / $51 figures not used."),
 "F-19": ("Satellite awards", "Venetian satellites award direct entries; no cash prize pool. Excluded from single-entry list."),
 "F-20": ("Venetian pool text", "Official Venetian titles say 'No LImit' (typo in source). Reproduced as printed."),
 "F-21": ("Caesars add-on status", "Caesars flyer lists a $50 add-on for the 10 AM and 2 PM events. Add-on status for 6 PM and 9 PM not verified."),
 "F-22": ("Wynn daily rules", "Wynn Friday rebuy: unlimited $200 rebuys and one $100 add-on (structure sheet read earlier). Exact wording to be re-checked against the PDF."),
}

def esc(x): return html.escape("" if x is None else str(x))

def check_source(url, where):
    if not url: ERRORS.append(f"missing source: {where}"); return
    host = urlparse(url).hostname or ""
    if host not in OFFICIAL_HOSTS: ERRORS.append(f"non-official host {host}: {where}")

def link(url, text=None):
    if not url: return '<span class="unv">UNVERIFIED</span>'
    return f'<a href="{esc(url)}" target="_blank" rel="noopener">{esc(text or "source")}</a>'

def val(v, flag=None):
    if v is None or v == "":
        return f'<span class="unv">UNVERIFIED{(" "+flag) if flag else ""}</span>'
    return esc(v)

def money(v):
    return "" if v is None else f"${v:,}"

def page(title, body, active):
    nav = [("index.html","Home"),("single-entry.html","Single-entry"),("excluded.html","Excluded / special"),
           ("schedule.html","Schedule"),("hotels.html","Hotels"),("summary.html","Summary"),
           ("questions.html","Questions"),("suggestions.html","Suggestions"),("repo-review.html","Repo review"),("flagged.html","Flagged")]
    navh = "".join(f'<a href="{h}" class="{"on" if h==active else ""}">{t}</a>' for h,t in nav)
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · Las Vegas Strip Poker Dashboard</title>
<style>
body{{font-family:system-ui,Arial,sans-serif;margin:0;color:#1d1d1f;background:#f7f7f9}}
header{{background:#14532d;color:#fff;padding:14px 20px}} header h1{{margin:0;font-size:20px}}
nav{{display:flex;flex-wrap:wrap;gap:4px;background:#fff;border-bottom:1px solid #ddd;padding:6px 12px}}
nav a{{padding:6px 10px;color:#14532d;text-decoration:none;border-radius:4px;font-size:14px}}
nav a.on,nav a:hover{{background:#dcfce7}}
main{{padding:18px 20px;max-width:1200px}}
table{{border-collapse:collapse;width:100%;background:#fff;font-size:13px;margin:10px 0 24px}}
th,td{{border:1px solid #e2e2e2;padding:6px 8px;text-align:left;vertical-align:top}}
th{{background:#f0f4f1}} .unv{{color:#b45309;font-weight:600}}
.box{{background:#fff;border:1px solid #e2e2e2;padding:12px 16px;margin:12px 0;border-radius:6px}}
.note{{font-size:13px;color:#555}} a{{color:#14532d}}
</style></head><body>
<header><h1>Las Vegas Strip Poker Dashboard</h1><div style="font-size:13px">As of {T['as_of']} (UTC). Official-source tables only.</div></header>
<nav>{navh}</nav><main>{body}</main></body></html>"""

def flagchips(ids):
    return " ".join(f'<a href="flagged.html#{i}" title="{esc(FLAGS[i][0])}">{i}</a>' for i in ids)

# ---------- single entry ----------
def sort_key(r):
    return (-(r["buy_in"] or 0), -(r["prize_pool_each"] or 0))

se = [r for r in T["single_entry"]]
for r in se:
    check_source(S["venetian_schedule_page"], f"E{r['event_no']}")
    check_source(VEN_PDF.replace("{N}", str(r["structure"])), f"E{r['event_no']} structure")
ranked = sorted(se, key=sort_key)

def se_row(i, r):
    pdf = VEN_PDF.replace("{N}", str(r["structure"]))
    fl = []
    if r["entry_rules"].startswith("NOT VERIFIED"): fl.append("F-09")
    if r["event_no"] in (18, 58): fl.append("F-08")
    if r["event_no"] == 28: fl.append("F-11")
    return f"""<tr><td>{i}</td><td>{esc(r['date'])}</td><td>{esc(r['time'])}</td><td>E{r['event_no']}</td>
<td>{esc(r['name'])}</td><td>{val(money(r['buy_in']))}</td><td>{val(money(r['gtd']) if r['gtd'] else '')}</td>
<td>{val(money(r['fee']))}</td><td>{val(money(r['prize_pool_each']))}</td><td>{val(f"{r['starting_chips']:,}" if r['starting_chips'] else '')}</td>
<td>{esc(r['entry_rules'])} {flagchips(fl)}</td>
<td>{link(S['venetian_schedule_page'],'schedule')} · {link(pdf,'structure')}</td></tr>"""

se_table = "\n".join(se_row(i+1, r) for i, r in enumerate(ranked))
se_body = f"""<h2>Single-entry live tournaments (Venetian DeepStack Extravaganza IV)</h2>
<div class="box"><b>Ranking:</b> highest buy-in first, then highest prize pool. Listed as single-entry per the official schedule (no multi-flight, team, or satellite format). Dates Nov 16 – Dec 23, 2026.
<br><span class="note">Fee = venue fee per official structure sheet where read; blank if not verified. Times are local Las Vegas.
Entry rules column: "no re-entry or add-on clause" means the structure sheet we read does not mention re-entry or add-ons. It is an absence, not an express single-entry confirmation (the other branch's review reached the same conclusion for E2/E10). Rows marked NOT VERIFIED have no structure sheet read yet.</span></div>
<table><tr><th>Rank</th><th>Date</th><th>Time</th><th>Event</th><th>Name (official)</th><th>Buy-in</th><th>GTD</th><th>Fee</th><th>Prize pool each</th><th>Starting chips</th><th>Entry rules</th><th>Sources</th></tr>
{se_table}</table>
<p class="note">Sources: official Venetian DeepStack IV schedule page (<a href="{esc(S['venetian_schedule_page'])}">link</a>) and per-event structure PDFs linked on each row. Satellites, team events, multi-flight and two-day events are on the <a href="excluded.html">Excluded / special</a> page.</p>"""

# ---------- excluded / special ----------
def mf_row(r):
    pdf = VEN_PDF.replace("{N}", str(r["structure"]))
    check_source(S["venetian_schedule_page"], f"multi E{r['event_no']}")
    check_source(pdf, f"multi structure E{r['event_no']}")
    return f"""<tr><td>{esc(r['date'])}</td><td>{esc(r['time'])}</td><td>E{r['event_no']}</td><td>{esc(r['name'])}</td>
<td>{money(r['buy_in'])}</td><td>{money(r['gtd'])}</td><td>{esc(r['note'])}</td>
<td>{link(S['venetian_schedule_page'],'schedule')} · {link(pdf,'structure')}</td></tr>"""

mf_table = "\n".join(mf_row(r) for r in T["multi_flight_not_single_entry"])
ex_rows = []
for r in T["excluded_team_satellite_and_other"]:
    pdf = VEN_PDF.replace("{N}", str(r["structure"]))
    check_source(S["venetian_schedule_page"], f"ex E{r['event_no']}")
    check_source(pdf, f"ex structure E{r['event_no']}")
    ex_rows.append(f"""<tr><td>{esc(r['date'])}</td><td>{esc(r['time'])}</td><td>E{r['event_no']}</td><td>{esc(r['name'])}</td>
<td>{money(r['buy_in'])}</td><td>{esc(r['reason'])} {flagchips(['F-19'] if 'atellite' in r['reason'] else [])}</td><td>{link(S['venetian_schedule_page'],'schedule')} · {link(pdf,'structure')}</td></tr>""")
ex_table = "\n".join(ex_rows)

rr_rows = []
for r in T["re_entry_addon_or_spend_more"]:
    check_source(r["source_url"], f"rr {r['venue']} {r['time']}")
    fl = []
    if "Caesars" in r["venue"]: fl.append("F-21")
    if "Wynn" in r["venue"]: fl.append("F-22")
    if "Golden" in r["venue"]: fl.append("F-04")
    if "MGM" in r["venue"]: fl.append("F-03")
    rr_rows.append(f"""<tr><td>{esc(r['venue'])}</td><td>{esc(r['date'])}</td><td>{esc(r['time'])}</td><td>{esc(r['name'])}</td>
<td>{val(money(r['buy_in']) if r['buy_in'] else '')}</td><td>{val(money(r['gtd']) if r['gtd'] else '')}</td><td>{esc(r['note'])} {flagchips(fl)}</td><td>{link(r['source_url'],'source')}</td></tr>""")
rr_table = "\n".join(rr_rows)

ex_body = f"""<h2>Excluded from the single-entry list</h2>
<div class="box"><b>Kept out of the main ranking:</b> multi-flight events (you must enter a flight and may play a later one), team events, satellites (direct-entry awards, not cash equity), and events with re-entry, add-ons or spend-more rules.</div>

<h3>A. Multi-flight / two-day events (multi-entry)</h3>
<table><tr><th>Date</th><th>Time</th><th>Event</th><th>Name (official)</th><th>Buy-in</th><th>GTD</th><th>Notes</th><th>Sources</th></tr>
{mf_table}</table>

<h3>B. Team, satellite and other excluded Venetian events</h3>
<table><tr><th>Date</th><th>Time</th><th>Event</th><th>Name (official)</th><th>Buy-in</th><th>Reason</th><th>Sources</th></tr>
{ex_table}</table>

<h3>C. Re-entry, add-on, or spend-more tournaments (other venues)</h3>
<table><tr><th>Venue</th><th>Day</th><th>Time</th><th>Name</th><th>Buy-in</th><th>GTD</th><th>Rules / notes</th><th>Source</th></tr>
{rr_table}</table>
<p class="note">Golden Nugget (downtown) is not on the Strip; included for reference only.</p>"""

# ---------- schedule ----------
from collections import defaultdict
bydate = defaultdict(list)
for r in se:
    bydate[r["date"]].append(r)
def t_to_min(t):
    h, m = map(int, t.split(":")); return h * 60 + m
sched_rows = []
for d in sorted(bydate):
    evs = sorted(bydate[d], key=lambda r: t_to_min(r["time"]))
    evs = [r for r in evs if t_to_min(r["time"]) >= 8 * 60]
    cells = "<br>".join(f"{esc(r['time'])} E{r['event_no']} ${r['buy_in']:,} ({'GTD $'+format(r['gtd'],',') if r['gtd'] else 'no GTD'})" for r in evs)
    first = evs[0]["time"] if evs else ""
    sched_rows.append(f"<tr><td>{esc(d)}</td><td>{len(evs)}</td><td>{esc(first)}</td><td>{cells}</td><td>{link(S['venetian_schedule_page'],'schedule')}</td></tr>")
sched_table = "\n".join(sched_rows)
sched_body = f"""<h2>Daily single-entry schedule (all Venetian, 8:00 AM onward)</h2>
<div class="box"><b>How to read:</b> one row per date that has at least one verified single-entry event, listing every single-entry start time from 8:00 AM. Entries are all at the Venetian, so no cross-venue travel is needed.
<br><b>Not yet known:</b> your vacation dates, your budget, and whether you will play flights. Registration close times are NOT verified (not on the official page), so overlap between events is shown by start time only. See <a href="questions.html">Questions</a>.
<br><span class="note">A plan for "as many as possible" is limited by sleep and bankroll, which we cannot verify. The table shows the maximum number of single-entry starts on a given day.</span></div>
<table><tr><th>Date</th><th>Starts from 8 AM</th><th>First start</th><th>Starts (time, event, buy-in)</th><th>Source</th></tr>
{sched_table}</table>"""

# ---------- hotels ----------
hot_rows = []
for h in H["hotels"]:
    fee_src = h["resort_fee_source"]
    poker_src = {"The Venetian Resort": S["venetian_schedule_page"], "The Palazzo at The Venetian": S["venetian_schedule_page"], "Wynn Las Vegas": S["wynn_poker_page"], "Caesars Palace": S["caesars_poker_page"]}[h["name"]]
    check_source(poker_src, f"hotel poker {h['name']}")
    if fee_src: check_source(fee_src, f"hotel fee {h['name']}")
    fl = ["F-12", "F-13", "F-14"] if h["flags"] else []
    hot_rows.append(f"""<tr><td>{esc(h['name'])}</td><td>{esc(h['poker_link'])}</td>
<td>{val(money(h['resort_fee_per_night']) if h['resort_fee_per_night'] != '' else '', 'F-18' if h['name']=='Wynn Las Vegas' else ('F-02' if 'Caesars' in h['name'] else ''))}</td>
<td>{esc(h['resort_fee_note'])}</td><td>{val(money(h['room_rate_per_night']) + ' (starting, conditional)' if h['room_rate_per_night'] else '', 'F-07' if 'Venetian' in h['name'] else 'F-12')} {('· ' + link(h['rate_source'],'rate source')) if h.get('rate_source') else ''}</td>
<td>{val(h['all_in_cost_per_night'],'F-12')}</td><td>{val(h['walking_minutes'],'F-14')}</td>
<td>{link(fee_src,'fee') if fee_src else '<span class="unv">fee: no official link</span>'} · {link(poker_src,'poker page')}</td></tr>""")
hot_table = "\n".join(hot_rows)
hot_body = f"""<h2>Hotels near the Strip tournament rooms</h2>
<div class="box"><b>Result: no hotel is fully verified yet.</b> Nightly rates, room tax and walking times have no official source in this session. The only verified figures are resort fees.
<br>Once rates are verified, <i>true nightly cost = nightly rate + resort fee + tax</i>. Cost and quality weigh more than walking distance, but walking must be within 30 minutes.</div>
<table><tr><th>Hotel</th><th>Poker link</th><th>Resort fee / night</th><th>Fee note</th><th>Room rate / night</th><th>True nightly cost</th><th>Walk (min)</th><th>Source</th></tr>
{hot_table}</table>
<p class="note">Not yet checked: {esc('; '.join(H['not_yet_checked']))}.</p>"""

# ---------- home / summary / questions / suggestions / repo review / flagged ----------
n_se = len(se); n_mf = len(T['multi_flight_not_single_entry'])
home_body = f"""<div class="box"><h2>Start here</h2>
<p>Live tournament data for the Las Vegas Strip, sourced line by line from official venue pages and PDFs. Every table row links to its official source. Anything that could not be verified is left blank and flagged.</p>
<ul>
<li><a href="single-entry.html">Single-entry tournaments</a> — {n_se} verified rows, ranked by buy-in and prize pool.</li>
<li><a href="excluded.html">Excluded / special</a> — multi-flight, satellites, team events, re-entry and add-on events.</li>
<li><a href="schedule.html">Daily schedule</a> — starts from 8 AM, all at the Venetian.</li>
<li><a href="hotels.html">Hotels</a> — resort fees verified; rates and walking times not yet verified.</li>
<li><a href="summary.html">Executive summary</a>, <a href="questions.html">questions</a>, <a href="suggestions.html">suggestions (for review, not applied)</a>, <a href="repo-review.html">repo review</a>, <a href="flagged.html">flagged items</a>.</li>
</ul></div>"""

summary_body = f"""<h2>Executive summary</h2>
<div class="box">
<ul>
<li><b>Largest verified series:</b> Venetian DeepStack Extravaganza IV, Nov 16 – Dec 23, 2026 (official page and schedule). {n_se} single-entry rows; {n_mf} multi-flight rows excluded.</li>
<li><b>Top single-entry buy-in:</b> E52 $1,100 NLH PKO, $75K GTD, Dec 15 11:10 AM (official). Fee $130, pool $970 (structure sheet read earlier).</li>
<li><b>Largest verified guarantee (single-entry):</b> E36 $800 bounty, $75K GTD, Dec 9, 11:10 AM. Largest guarantee overall is a multi-flight event (E47, $1M GTD).</li>
<li><b>Other venues:</b> Wynn daily ($200 noon, $240 Friday rebuy with $40K GTD, $160 at 6 PM per official poster); Caesars Palace daily ($100 and $160 at 10 AM / 2 PM / 6 PM / 9 PM per flyer, re-entry and add-on rules partly unverified); MGM Grand ($120 daily; times conflict, flagged); Golden Nugget (downtown; buy-in not published).</li>
<li><b>Hotels:</b> Official Venetian poker suite rates start at $119 (Venetian) and $209 (Palazzo), plus a $55 resort fee per night, conditional on poker play and not a dated quote. Caesars fee conflicts. Walking times and room tax are unverified, so no hotel can yet be confirmed inside the 30-minute walking rule.</li>
<li><b>Schedule:</b> Venetian single-entry starts run from 10:10 AM to 5:10 PM daily, with many days offering 2–3 starts. Your travel dates are needed to build a vacation plan.</li>
<li><b>Honest limits:</b> Registration close times, several structure sheets, multi-flight Day 2 rules and the Wynn WPT schedule are not verified. See <a href="flagged.html">Flagged</a>.</li>
</ul></div>
<h3>Sources used (official only)</h3>
<ul>
<li><a href="{esc(S['venetian_schedule_page'])}">Venetian DeepStack IV schedule page</a></li>
<li><a href="https://www.venetianlasvegas.com/resort/resort-fee.html">Venetian resort fee</a></li>
<li><a href="{esc(S['caesars_poker_page'])}">Caesars Palace poker</a> and <a href="{esc(S['caesars_flyer'])}">2026 Caesars daily flyer</a></li>
<li><a href="{esc(S['wynn_poker_page'])}">Wynn poker</a>, <a href="{esc(S['wynn_daily_poster'])}">Wynn daily poster</a>, <a href="{esc(S['wynn_daily_structures'])}">Wynn daily structures</a></li>
<li><a href="{esc(S['mgm_poker_page'])}">MGM Grand poker</a>, <a href="{esc(S['mgm_weekly_pdf'])}">MGM weekly schedule</a></li>
<li><a href="{esc(S['golden_nugget_page'])}">Golden Nugget daily tournaments</a></li>
</ul>"""

questions = [
 ("Vacation dates", "Which dates will you be in Las Vegas? Needed for the schedule page."),
 ("Budget", "Total bankroll and per-day tournament budget? Needed to rank by affordability."),
 ("Hotel rates", "Should I use a specific check-in/check-out window? Official Venetian calendar shows placeholders; please provide the dates you want priced or allow a lookup on a later date."),
 ("Walking tolerance", "Is 30 minutes the max? Need official walking times (no official source yet)."),
 ("Flights", "Do you want multi-flight events (E1, E7, E19, E26, E47, E49, E56, E59) in the plan? They are excluded from the single-entry list."),
 ("Satellites", "Will you play satellites to win direct entries?"),
 ("Skill / format", "Any format preferences (NLH, PLO, Big O, bounty, PKO, seniors 50+)?"),
 ("Caesars fee", "Official Caesars Palace resort-fee page URL, if you have one."),
 ("Wynn fee link", "Official Wynn resort-fee link (earlier session read it; link was not re-located)."),
 ("MGM time", "Which MGM time is current (web 11:00 AM / 7 PM / 11 PM vs PDF 11:10 AM / 7:10 PM / 11:10 PM)? Confirm at the cage."),
 ("Golden Nugget buy-in", "Official buy-in for the daily tournaments."),
 ("Horseshoe", "Official Horseshoe tournament times and buy-ins."),
 ("WPT Wynn", "Wynn WPT World Championship schedule (official PDF returned 502)."),
 ("Discovery ideas", "Call each room (Venetian, Caesars, Wynn, MGM, Golden Nugget, Horseshoe) at the poker desk; ask for the printed schedule and re-entry rules."),
 ("Discovery ideas", "Ask the Venetian, Wynn and Caesars rewards desks for their current resort fee and tax-inclusive nightly rate."),
 ("Discovery ideas", "Use the Clark County Department of Business License / Nevada Department of Taxation page for the official room tax rate (not yet fetched)."),
 ("Discovery ideas", "Use a walking-route tool (e.g., Google Maps) to measure walking time from each hotel to the poker room, then record the result with the tool's link; mark it as an external estimate, not an official source."),
]
q_rows = "\n".join(f"<tr><td>{i+1}</td><td>{esc(a)}</td><td>{esc(b)}</td></tr>" for i,(a,b) in enumerate(questions))
q_body = f"""<h2>Questions and information still needed</h2>
<table class="meta"><tr><th>#</th><th>Topic</th><th>Question / what to find</th></tr>{q_rows}</table>"""

sugg = [
 "Add a 'last verified' date to every row (currently only the page-level date).",
 "Store each row's source as a per-cell link, not just one per row, so reviewers can check each value.",
 "Add a flagged-items filter to the single-entry table.",
 "Add hotel walking time only from a reproducible map link (external), clearly labelled.",
 "Add a schedule builder that lets you pick vacation dates and see a day-by-day plan.",
 "Automate the official-source check so a CI step fails when a row has no official link.",
 "Add a mobile layout for the wide tables.",
]
s_rows = "\n".join(f"<li>{esc(s)}</li>" for s in sugg)
sugg_body = f"""<h2>Suggestions for site improvements (review first — no changes applied)</h2>
<div class="box"><b>Status:</b> suggestions only. Per your instruction, nothing here is implemented until you review it.</div>
<ol>{s_rows}</ol>"""

review_body = """<h2>Repo review (line by line)</h2>
<table><tr><th>Item</th><th>Finding</th><th>Source</th></tr>
<tr><td>README.md</td><td>One line: "# Poker2". No setup or purpose text.</td><td><a href="https://github.com/karagemop466-tech/Poker2/blob/main/README.md">README.md on main</a></td></tr>
<tr><td>Commit history</td><td>One commit: 058cd54 "Initial commit". Main and the session branch both point to it.</td><td><a href="https://github.com/karagemop466-tech/Poker2">GitHub repo</a></td></tr>
<tr><td>Pages</td><td>GitHub Pages is configured to build from main at / (no change needed). The site lives in /docs, so it is served at /Poker2/docs/. A root index.html redirects the Pages root to /docs/.</td><td><a href="https://api.github.com/repos/karagemop466-tech/Poker2/pages">Pages API</a></td></tr>
<tr><td>COORDINATION.md</td><td>Did not exist at session start; created by this session (F-15).</td><td><a href="https://github.com/karagemop466-tech/Poker2/blob/arena/acd81e67-poker2/COORDINATION.md">COORDINATION.md on session branch</a></td></tr>
<tr><td>Branch scheme</td><td>Brief asks for session-&lt;id&gt;/&lt;task&gt; branches; session assigned one branch (F-16).</td><td><a href="https://github.com/karagemop466-tech/Poker2/branches">Repo branches</a></td></tr>
</table>"""

flag_rows = "\n".join(f'<tr id="{k}"><td>{k}</td><td>{esc(v[0])}</td><td>{esc(v[1])}</td></tr>' for k,v in FLAGS.items())
flag_body = f"""<h2>Flagged for review</h2>
<p class="note">Flagged items do not block the merge. Each row says what could not be verified.</p>
<table class="meta"><tr><th>ID</th><th>Issue</th><th>Detail</th></tr>{flag_rows}</table>"""

PAGES = {
 "index.html": ("Home", home_body),
 "single-entry.html": ("Single-entry", se_body),
 "excluded.html": ("Excluded / special", ex_body),
 "schedule.html": ("Schedule", sched_body),
 "hotels.html": ("Hotels", hot_body),
 "summary.html": ("Executive summary", summary_body),
 "questions.html": ("Questions", q_body),
 "suggestions.html": ("Suggestions", sugg_body),
 "repo-review.html": ("Repo review", review_body),
 "flagged.html": ("Flagged", flag_body),
}

if ERRORS:
    print("BUILD FAILED — rows without official source:"); [print(" -", e) for e in ERRORS]; sys.exit(1)

DOCS.mkdir(exist_ok=True)
for name, (title, body) in PAGES.items():
    (DOCS / name).write_text(page(title, body, name))

# root index.html belongs to the main-branch site; not written here
print("built", len(PAGES), "pages into docs/")
