#!/usr/bin/env python3
"""Root-surface invariants for scripts/build_site.py output (M3 regression gate)."""
import pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
def read(n): return (ROOT/n).read_text(errors="ignore")
errs=[]
hotels=read("hotels.html"); planner=read("planner.html"); tourn=read("tournaments.html"); ranking=read("ranking.html")
if 'data-rate="None"' in planner or 'data-rate="None"' in hotels: errs.append("data-rate=None rendered")
if 'data-fee="0"' in hotels and 'blank' in hotels:
    # fee=0 is only legitimate where dataset fee is actually 0; build_site now emits "" for unverified
    pass
# unverified hotels (Horseshoe/Caesars/South Point in dataset) must not emit fee/parking 0 in calc/preset
import json
m=json.load(open(ROOT/"data/master.json"))
for h in m["hotels"]:
    if h.get("resort_fee_value") is None and f'data-fee="0"' in planner: errs.append("planner coerces unverified fee to 0")
    if h.get("id")=="H-PAL" and 'data-rate="209"' in planner: errs.append("Palazzo $209 starting price prefilled as quote rate")
# tournaments filters present
for attr in ("data-bind-from","data-bind-to","data-bind-upcoming","data-bind-freezeout"):
    if attr not in tourn: errs.append(f"tournaments missing {attr}")
if "Confirmed single-entry / freezeout only" not in tourn: errs.append("freezeout toggle label missing")
# planner past dates in dayplan: dates before 2026-11-19 must not appear as primary rows
for d in ("2026-11-16","2026-11-17","2026-11-18"):
    if f"<tr><td>{d}</td>" in planner: errs.append(f"planner dayplan includes past date {d}")
# ranking NLH section must not contain PLO/BIG O rows
sec = ranking.split("NLH events whose sheet is silent",1)[-1].split("<h2>",1)[0] if "NLH events" in ranking else ""
if "BIG O" in sec or "Pot Limit Omaha" in sec: errs.append("ranking NLH section contains PLO/BIG O")
# hotels walk filter is Venetian/Wynn based: MGM/Golden Nugget rows must be walk-ok 0 if their ven/wynn legs >30
# (checked structurally: no data-walk-ok=1 row may simultaneously show both legs as over 30)
for row in re.findall(r"<tr[^>]*data-walk-ok=\"1\".*?</tr>", hotels, re.S):
    if row.count("over 30 min")>=2: errs.append("hotel row marked walk-ok=1 despite both headline legs over 30 min")
if errs:
    print("check_root_surface FAILED:"); [print(" -",e) for e in errs]; sys.exit(1)
print("check_root_surface: root invariants ok")
