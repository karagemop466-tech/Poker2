#!/usr/bin/env python3
"""Static checks for the built site: source coverage, rule provenance,
classification validity, and internal link integrity."""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "site")
errors = []

def load(n):
    return json.load(open(os.path.join(D, n)))

sources = load("sources.json")
events = load("events.json")["events"]
ALLOWED = {"single_entry_confirmed", "flagged_ambiguous", "excluded", "unverified"}

for e in events:
    eid = e.get("id", "?")
    if e.get("classification") not in ALLOWED:
        errors.append(f"{eid}: bad classification {e.get('classification')}")
    if not e.get("sources"):
        errors.append(f"{eid}: no sources[]")
    for s in e.get("sources", []):
        if s not in sources:
            errors.append(f"{eid}: unknown source id {s}")
    for k, v in (e.get("rules") or {}).items():
        if not isinstance(v, dict) or "source" not in v or "retrieved" not in v:
            errors.append(f"{eid}: rule '{k}' missing source/retrieved")
        elif v["source"] not in sources:
            errors.append(f"{eid}: rule '{k}' unknown source {v['source']}")
    if e.get("classification") == "single_entry_confirmed":
        for k in ("single_entry", "re_entry", "rebuy", "addon"):
            v = (e.get("rules") or {}).get(k) or {}
            if not v.get("excerpt"):
                errors.append(f"{eid}: confirmed row missing rule excerpt for {k}")

# hotel rate log provenance
for r in load("hotels.json")["rate_log"]:
    if r.get("source") not in sources:
        errors.append(f"rate_log {r.get('hotel_id')}: unknown source {r.get('source')}")

# internal link integrity over generated HTML
pages = ["index.html", "tournaments.html", "schedule.html", "trip.html", "hotels.html",
         "walking.html", "questions.html", "suggestions.html", "flagged.html",
         "sources.html", "monitor.html", "archive.html",
         "venues/venetian.html", "venues/wynn.html", "venues/others.html"]
for pg in pages:
    p = os.path.join(ROOT, pg)
    if not os.path.exists(p):
        errors.append(f"missing page {pg}")
        continue
    base = os.path.dirname(p)
    body = open(p).read()
    for href in re.findall(r'href="([^"]+)"', body):
        if href.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target = os.path.normpath(os.path.join(base, href.split("#")[0]))
        if not os.path.exists(target):
            errors.append(f"{pg}: broken internal link {href}")
    for src in re.findall(r'src="([^"]+)"', body):
        if src.startswith(("http://", "https://")):
            continue
        target = os.path.normpath(os.path.join(base, src))
        if not os.path.exists(target):
            errors.append(f"{pg}: missing script/asset {src}")

# monitor seed covers every unique source URL
mon = load("monitor.json")
urls_data = {s["url"] for s in sources.values()}
urls_mon = {r["url"] for r in mon["rows"]}
if urls_data != urls_mon:
    errors.append(f"monitor rows out of sync with sources: data-only={urls_data-urls_mon} mon-only={urls_mon-urls_data}")

if errors:
    print("FAIL:", len(errors))
    for x in errors[:60]:
        print(" -", x)
    sys.exit(1)
print(f"PASS: {len(events)} events, {len(sources)} sources, {len(pages)} pages — provenance and links OK")
