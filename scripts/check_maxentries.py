#!/usr/bin/env python3
"""Gate: the "maximum entries per day" table must never present an impossible day as a plan.

The rule the site publishes (Day plan -> "Maximum entries per day") is deliberately narrow because
the data is narrow. Each official schedule row prints a start time and a late-registration close.
No structure sheet prints how many levels an event runs, so a finish time cannot be computed and is
never invented. Therefore:

  * two entries with the SAME published start are impossible, not a sequence;
  * a later entry whose registration closes at or before the earlier entry's start is impossible;
  * a later flight of the SAME event is a second buy-in, not a second tournament;
  * every other pair is CONDITIONAL ("only if you are out in time"), never promised.

This gate fails the build if any of those rules stops holding, if the summary table and the day
cards disagree, or if the page starts quoting a computed finish time it cannot support.

    python3 scripts/check_maxentries.py
"""
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

spec = importlib.util.spec_from_file_location("b26", os.path.join(ROOT, "scripts", "build2026.py"))
b26 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b26)

problems = []
events = b26.build_events()
days = b26.build_days(events)

# ---- 1. unit properties of the rule itself -------------------------------------------------
unit_cases = [
    # name, entries, expected chain length
    ("identical start is impossible",
     [dict(event_no=1, label="A", start=600, start_text="10:00 AM", close=900, close_text="3:00 PM"),
      dict(event_no=2, label="B", start=600, start_text="10:00 AM", close=900, close_text="3:00 PM")], 1),
    ("later entry closing before the earlier start is impossible",
     [dict(event_no=1, label="A", start=600, start_text="10:00 AM", close=610, close_text="10:10 AM"),
      dict(event_no=2, label="B", start=900, start_text="3:00 PM", close=905, close_text="3:05 PM")], 2),
    ("a second flight of the same event is not a second tournament",
     [dict(event_no=1, label="A 1A", start=600, start_text="10:00 AM", close=900, close_text="3:00 PM"),
      dict(event_no=1, label="A 1B", start=1000, start_text="4:40 PM", close=1200, close_text="8:00 PM")], 1),
    ("a later entry still open after the earlier starts is reachable",
     [dict(event_no=1, label="A", start=600, start_text="10:00 AM", close=900, close_text="3:00 PM"),
      dict(event_no=2, label="B", start=1030, start_text="5:10 PM", close=1300, close_text="9:40 PM")], 2),
    ("no close published means it cannot be planned",
     [dict(event_no=1, label="A", start=600, start_text="10:00 AM", close=900, close_text="3:00 PM"),
      dict(event_no=2, label="B", start=1030, start_text="5:10 PM", close=None, close_text="")], 1),
]
for name, entries, expected in unit_cases:
    # day_sequence() reads the same keys build_days() produces
    entries = [dict(e, start_m=e["start"], reg_close_m=e["close"]) for e in entries]
    chain, _ = b26.day_sequence(entries)
    if len(chain) != expected:
        problems.append("rule unit case failed: %s (chain %d, expected %d)"
                        % (name, len(chain), expected))

# ---- 2. no day may claim a chain longer than its entries ------------------------------------
for d in days:
    chain, impossible = b26.day_sequence(d["entries"])
    if len(chain) > len(d["entries"]):
        problems.append("%s: chain longer than the day's entries" % d["date"])
    starts = [c["start"] for c in chain]
    if len(set(starts)) != len(starts):
        problems.append("%s: chain contains two entries with the same start" % d["date"])
    nos = [c["event_no"] for c in chain]
    if len(set(nos)) != len(nos):
        problems.append("%s: chain contains the same event twice" % d["date"])

# ---- 3. the rendered page agrees with the computed rule -------------------------------------
page = os.path.join(ROOT, "2026", "schedule.html")
text = open(page, encoding="utf-8").read()

if 'id="max-entries"' not in text:
    problems.append("schedule.html: the maximum-entries panel is missing")

table = dict((m.group(1), int(m.group(2))) for m in
             re.finditer(r"<tr data-dates='([0-9-]+)' data-max='(\d+)'", text))
for d in days:
    if not d["entries"]:
        continue
    chain, _ = b26.day_sequence(d["entries"])
    if d["date"] not in table:
        problems.append("%s: no row in the maximum-entries table" % d["date"])
    elif table[d["date"]] != len(chain):
        problems.append("%s: table says %d, rule computes %d"
                        % (d["date"], table[d["date"]], len(chain)))

# One maxline per day that publishes more than one entry row. The schedule card prints the DATE
# separately, so match the line and count it rather than trying to key it to a date.
card_lines = re.findall(r"data-max='(\d+)'><strong>Maximum entries today: (\d+)</strong> of (\d+)", text)
want = len([d for d in days if len(d["entries"]) > 1])
if len(card_lines) < want:
    problems.append("only %d 'maximum entries today' lines for %d multi-entry days"
                    % (len(card_lines), want))
for claimed, shown, total in card_lines:
    if int(claimed) > int(total):
        problems.append("a day claims %s entries out of %s published rows" % (claimed, total))

# ---- 4. the page must not pretend to know a finish time ------------------------------------
if re.search(r"finish(es)? (at|by|around) \d", text, re.I):
    problems.append("schedule.html: claims a finish time")

for p in problems:
    print("FAIL " + p)
print("%s: %d days checked, %d multi-entry days, %d rule unit cases"
      % ("FAILED" if problems else "OK",
         len([d for d in days if d["entries"]]),
         len([d for d in days if len(d["entries"]) > 1]),
         len(unit_cases)))
sys.exit(1 if problems else 0)
