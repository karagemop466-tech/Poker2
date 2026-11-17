#!/usr/bin/env python3
"""Compare the live official Venetian DSE IV schedule table with the committed dataset.

Input : research/venetian-dse4-live-2026-11-17.csv  (one row per table row, transcribed from the
        official HTML page, https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html,
        read in four chunks on 2026-11-17)
Dataset: data/verified2026/schedule.py ROWS (date, dow, event_no, start, ..., sheet_no)
Exit 1 on any difference. Read-only: writes nothing except stdout.
"""
import collections, csv, datetime, importlib.util, sys

LIVE = "research/venetian-dse4-live-2026-11-17.csv"
spec = importlib.util.spec_from_file_location("sch", "data/verified2026/schedule.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

ds = collections.Counter((r[0], r[3], r[2], r[9]) for r in m.ROWS)
live_rows = list(csv.DictReader(open(LIVE)))
live = collections.Counter((r["date"], r["start"], int(r["event_no"]), int(r["sheet_no"])) for r in live_rows)

bad = 0
print(f"dataset rows={sum(ds.values())} live rows={sum(live.values())}")
for k, v in (live - ds).items():
    print("MISSING IN DATASET:", k, v); bad += 1
for k, v in (ds - live).items():
    print("NOT ON LIVE PAGE:", k, v); bad += 1

# weekday labels in the dataset must match the calendar
for r in m.ROWS:
    d = datetime.date.fromisoformat(r[0])
    if d.strftime("%a") != r[1]:
        print("WEEKDAY MISMATCH:", r[0], r[1], d.strftime("%a")); bad += 1

print("OK: live official table matches the dataset row for row." if bad == 0 else f"FAIL: {bad} difference(s)")
sys.exit(1 if bad else 0)
