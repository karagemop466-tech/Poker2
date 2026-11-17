#!/usr/bin/env python3
"""Guard: a multi-event structure sheet must not give every one of its events the same figure.

The failure this catches actually happened. Sheet 11 prints
    "$30,000 (#16), $40,000 (#30), $50,000 (#54) - prize pool + total bounties"
and sheet 7 prints
    "$30,000 for Event #14 and #63; $40,000 for Event #28"
A previous version of scripts/build2026.py took the first dollar figure on the sheet, so events
30, 54 and 28 were published with the wrong guarantee and the wrong guarantee-to-entry ratio. A
wrong number that renders cleanly is the worst failure this site can have, so it is now a build
gate rather than something a reader has to notice.

    python3 scripts/check_guarantees.py
"""
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data", "sheets"))
sys.path.insert(0, os.path.join(ROOT, "data", "verified2026"))

spec = importlib.util.spec_from_file_location("b26", os.path.join(ROOT, "scripts", "build2026.py"))
b26 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b26)

problems = []
checked = 0

for n, sheet in sorted(b26.SHEETS.items()):
    events = sheet.get("events") or []
    text = sheet.get("guarantee") or ""
    values = {}
    for ev in events:
        val, note = b26.guarantee_for_event(sheet, ev)
        values[ev] = val
        checked += 1
    # a sheet that prints several dollar figures must not hand the same one to every event
    printed = set(re.findall(r"\$([\d,]+)\s*(K|Million|Mill)?", text, re.I))
    if len(printed) > 1 and len(events) > 1:
        distinct = {v for v in values.values() if v is not None}
        if len(distinct) == 1:
            problems.append("sheet %d prints %d different guarantees but every event resolved to %s"
                            % (n, len(printed), distinct))
        for ev, v in values.items():
            if v is None:
                problems.append("sheet %d: event #%d got no guarantee from a sheet that prints several"
                                % (n, ev))
    # a sheet that names a single event number in the guarantee text must not be shared blindly
    named = {int(x) for x in re.findall(r"#\s*(\d+)", text)}
    if named and len(events) > 1 and not named.issuperset(events):
        for ev in events:
            if ev not in named and values.get(ev) is not None:
                problems.append("sheet %d: event #%d has a guarantee but is not named in the sheet text %r"
                                % (n, ev, text[:80]))

for p in problems:
    print("FAIL " + p)
print("%s: %d event(s) resolved across %d sheet(s)"
      % ("FAILED" if problems else "OK", checked, len(b26.SHEETS)))

# --------------------------------------------------------------------------------------
# day-plan rule: a restricted or satellite event must not be the primary of a day that has an
# unrestricted event available. This is the bug that made a $260 satellite the main event of
# 12 December instead of the $2,200 $1M-guarantee title event.
# --------------------------------------------------------------------------------------
day_problems = []
days = b26.build_days(b26.build_events())
for d in days:
    p = d["primary"]
    if p is None:
        continue
    if p.get("eligibility"):
        day_problems.append("%s: primary #%s is entry-restricted (%s)"
                            % (d["date"], p["event_no"], p["eligibility"][:60]))
    alternatives = [x for x in d["entries"]
                    if not x.get("eligibility") and x["group"] != "satellite"
                    and not (x["event_no"] == p["event_no"] and x["start"] == p["start"])]
    if p["group"] == "satellite" and alternatives:
        day_problems.append("%s: primary #%s is a satellite but %d open event(s) run that day"
                            % (d["date"], p["event_no"], len(alternatives)))
for q in day_problems:
    print("FAIL " + q)
print("%s: %d day(s) checked for a playable primary"
      % ("FAILED" if day_problems else "OK", len([d for d in days if d["primary"]])))
sys.exit(1 if (problems or day_problems) else 0)
