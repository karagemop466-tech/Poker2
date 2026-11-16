#!/usr/bin/env python3
"""Render one cautious venue page per property represented in the official-source data."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVENTS = json.loads((ROOT / 'data/tournaments.json').read_text())
SOURCES = json.loads((ROOT / 'data/sources.json').read_text())
HOTELS = json.loads((ROOT / 'data/hotels.json').read_text()).get('hotels', [])
VENUES = [
    ('the-venetian', 'The Venetian Resort', ('Venetian / Palazzo',), ('The Venetian', 'The Palazzo'), 'V_EVENT'),
    ('wynn', 'Wynn Las Vegas', ('Wynn Las Vegas',), ('Wynn Las Vegas',), 'W_POKER'),
    ('bellagio', 'Bellagio', ('Bellagio',), ('Bellagio',), 'B_POKER'),
    ('mgm-grand', 'MGM Grand', ('MGM Grand',), ('MGM Grand',), 'MGM_POKER'),
    ('aria', 'ARIA Resort & Casino', ('ARIA',), ('ARIA Resort & Casino',), 'A_POKER'),
]

def esc(value):
    return html.escape('' if value is None else str(value), quote=True)

def fmt_money(value):
    return '' if value in (None, '') else '$' + format(float(value), ',.2f').rstrip('0').rstrip('.')

def date_attrs(value):
    dates=re.findall(r'\d{4}-\d{2}-\d{2}', str(value or ''))
    if not dates: return ''
    start,end=dates[0],dates[-1]
    return f' data-date-start="{esc(start)}" data-date-end="{esc(end)}"'

def urls_for(row):
    refs = row.get('src', [])
    if isinstance(refs, str): refs = [refs]
    return list(dict.fromkeys(SOURCES[ref]['url'] for ref in refs if ref in SOURCES))

def page(slug, title, aliases, hotel_names, poker_key):
    event_rows=[]
    for category, records in EVENTS.items():
        if not isinstance(records, list): continue
        for event in records:
            venue=event.get('venue','')
            if not any(alias.lower() in venue.lower() for alias in aliases): continue
            date=event.get('date') or ''
            start=event.get('time') or ''
            name=event.get('name') or ''
            buyin=fmt_money(event.get('buy_in'))
            gtd=fmt_money(event.get('gtd'))
            evidence=event.get('rule_evidence',{})
            rules='Unverified'
            if any(evidence.get(field,{}).get('value') is not None for field in ('single_entry','re_entry','add_on')):
                rules='See cited rule evidence; not independently re-confirmed'
            row_sources=urls_for(event)
            links=' · '.join(f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">Official source {i+1}</a>' for i,url in enumerate(row_sources))
            if not links:
                link=SOURCES.get(poker_key,{}).get('url','')
                links=f'<a href="{esc(link)}">Official venue page</a>' if link else ''
            event_rows.append(f'<tr{date_attrs(date)}><td>{esc(date)}</td><td>{esc(start)}</td><td>{esc(name)}</td><td>{esc(buyin)}</td><td>{esc(gtd)}</td><td>{esc(rules)}</td><td>{esc(event.get("last_checked", EVENTS.get("as_of", "")))}</td><td>{links}</td></tr>')
    if not event_rows:
        event_rows.append('<tr><td colspan="8">No dated event facts were verified in the current official-source dataset for this venue. Open the official poker link below; no event has been inferred.</td></tr>')

    hotel_rows=[]
    for hotel in HOTELS:
        if not any(name.lower() in hotel.get('name','').lower() for name in hotel_names): continue
        sources=[]
        for ref in hotel.get('src',[]):
            if ref in SOURCES: sources.append(SOURCES[ref]['url'])
        links=' · '.join(f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">Official hotel source {i+1}</a>' for i,url in enumerate(dict.fromkeys(sources)))
        hotel_rows.append(f'<tr data-walk-minutes=""><td>{esc(hotel.get("name"))}</td><td>{esc(hotel.get("rate") or "")}</td><td>{esc(hotel.get("resort_fee") or "")}</td><td>{esc(hotel.get("walk") or "")}</td><td>{esc(hotel.get("last_checked", HOTELS[0].get("last_checked", "") if HOTELS else ""))}</td><td>{links}</td></tr>')
    if not hotel_rows: hotel_rows.append('<tr><td colspan="6">No hotel rate, mandatory cost total, or walking duration verified for this property. See official source links.</td></tr>')

    poker_url=SOURCES.get(poker_key,{}).get('url','')
    nav=' <a href="../index.html">Overview</a> <a href="../tournaments.html">All tournaments</a> <a href="../hotels.html">Hotel comparison</a> <a href="../trip-cost.html">Trip cost</a> <a href="../source-monitor.html">Source monitor</a> <a href="../flagged.html">Flagged for Review</a>'
    html_doc=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Vegas Poker Planner</title><link rel="stylesheet" href="../style.css"></head><body><header class="top"><div class="shell topbar"><a class="brand" href="../index.html"><i></i>VEGAS POKER PLANNER</a><nav class="nav">{nav}</nav></div></header><main class="shell"><div class="eyebrow">Venue profile · sourced schedule + lodging context</div><h1>{esc(title)}</h1><p class="lead">This profile brings together available event leads and hotel information for this property. Empty values are intentionally blank when an official source did not establish them. Historical retrieval date is shown per row; use the <a href="../source-monitor.html">official-source monitor</a> and re-open venue links before relying on a schedule.</p><p><a href="{esc(poker_url)}" target="_blank" rel="noopener noreferrer">Official poker-room page ↗</a></p><section class="panel"><h2>Events and tournament leads</h2><p>Buy-in and guarantee cells reflect the cited official-source dataset where present. Rule status is not treated as confirmed single-entry unless evidence is explicitly stored; ratio rankings are withheld here.</p><div class="tablewrap"><table class="event-table"><thead><tr><th>Date</th><th>Start</th><th>Event</th><th>Published buy-in</th><th>Published guarantee</th><th>Entry-rule status</th><th>Last checked</th><th>Official sources</th></tr></thead><tbody>{''.join(event_rows)}</tbody></table></div></section><section class="panel"><h2>Hotels for this venue</h2><p>Rates and walk times remain blank unless sourced for the exact stay. A resort-fee line is not an all-in rate. Walking-time eligibility is not assigned without verified route timing.</p><div class="tablewrap"><table class="hotel-table"><thead><tr><th>Property</th><th>Nightly room rate</th><th>Resort fee</th><th>Walk to poker room</th><th>Last checked</th><th>Official sources</th></tr></thead><tbody>{''.join(hotel_rows)}</tbody></table></div></section><p class="small">Source snapshot: {esc(EVENTS.get('as_of',''))}. Dates, published schedule values, fees and policies may change. No value is inferred from a missing cell.</p></main><footer class="footer"><div class="shell">Venue-specific view. Check Flagged for Review before making a travel or payment decision.</div></footer><script src="../site-tools.js"></script></body></html>'''
    path=ROOT/'venues'/f'{slug}.html';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(html_doc,encoding='utf-8')

for config in VENUES: page(*config)
# Small venue directory; every property row links to its official poker-room page.
directory_rows=[]
for slug,title,aliases,hotel_names,poker_key in VENUES:
    source=SOURCES.get(poker_key,{})
    directory_rows.append(f'<tr><td><a href="{slug}.html">{esc(title)}</a></td><td><a href="{esc(source.get("url",""))}">Official poker-room page</a></td><td><a href="{slug}.html">Events and hotel costs</a></td></tr>')
index='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Venue pages | Vegas Poker Planner</title><link rel="stylesheet" href="../style.css"></head><body><header class="top"><div class="shell topbar"><a class="brand" href="../index.html"><i></i>VEGAS POKER PLANNER</a><nav class="nav"><a href="../index.html">Overview</a><a href="../tournaments.html">Tournaments</a><a href="../hotels.html">Hotels</a><a href="../trip-cost.html">Trip cost</a><a href="../source-monitor.html">Source monitor</a><a href="../flagged.html">Flagged for Review</a></nav></div></header><main class="shell"><div class="eyebrow">Venue-specific information</div><h1>Venues</h1><p class="lead">Each profile groups available event facts and hotel-cost context for that venue. Missing schedule data and hotel values remain blank rather than inferred.</p><div class="tablewrap"><table><thead><tr><th>Venue</th><th>Official poker source</th><th>Profile</th></tr></thead><tbody>''' + ''.join(directory_rows) + '''</tbody></table></div></main><footer class="footer"><div class="shell">Source snapshot dated ''' + esc(EVENTS.get('as_of','')) + '''.</div></footer><script src="../site-tools.js"></script></body></html>'''
(ROOT/'venues'/'index.html').write_text(index,encoding='utf-8')
print(f'Built {len(VENUES)} venue pages and a directory under venues/.')
