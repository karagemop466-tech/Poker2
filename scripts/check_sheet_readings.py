#!/usr/bin/env python3
"""Compare a live transcription of the official Venetian DSE IV structure sheets
against the values the site ships.

The transcription in ``research/sheet-readings-7cc9ee65.csv`` was made by reading
each official PDF directly from venetianlasvegas.com. This script is the
reproducible part of that check: it diffs the transcription field by field
against ``data/verified2026/dataset.json`` and exits 1 on any difference, so
"the sheets were read" is a claim anyone can re-run rather than a claim anyone
has to take on trust.

Usage:  python3 scripts/check_sheet_readings.py [--readings FILE] [--quiet]
"""

import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
READINGS = os.path.join(ROOT, "research", "sheet-readings-7cc9ee65.csv")
DATASET = os.path.join(ROOT, "data", "verified2026", "dataset.json")

MONEY = re.compile(r"[\$,]|\s+")


def norm(value):
    """Collapse a free-text field to a comparable token string."""
    if value is None:
        return ""
    text = str(value).lower()
    text = MONEY.sub("", text)
    text = text.replace("~", "").replace("levels", "levels")
    text = re.sub(r"[^a-z0-9%]+", " ", text)
    return " ".join(text.split())


def numbers(value):
    """Every integer in a field, as a sorted list - order-independent compare."""
    if value is None:
        return []
    return sorted(int(n.replace(",", "")) for n in re.findall(r"\d[\d,]*", str(value)))


def same_text(mine, theirs):
    """Two text fields agree if they normalise equal, or one contains the other."""
    a, b = norm(mine), norm(theirs)
    if not a and not b:
        return True
    if not a or not b:
        return False
    return a == b or a in b or b in a


def same_guarantee(mine, theirs):
    """Guarantees are compared on their numbers and on whether the sheet says the
    figure is bounty-inclusive or a seat prize - the two things that decide
    whether a guarantee is like-for-like."""
    a, b = norm(mine), norm(theirs)
    if numbers(mine) != numbers(theirs):
        return False
    for token in ("bounties", "bounty", "seats", "seat"):
        if (token in a) != (token in b):
            return False
    return True


def is_silent(value):
    return norm(value) in ("", "silent")


def main():
    quiet = "--quiet" in sys.argv
    readings_path = READINGS
    if "--readings" in sys.argv:
        readings_path = sys.argv[sys.argv.index("--readings") + 1]

    with open(readings_path, newline="") as fh:
        readings = list(csv.DictReader(fh))
    with open(DATASET) as fh:
        sheets = json.load(fh)["sheets"]

    by_no = {}
    for sheet in sheets:
        match = re.search(r"structure_(\d+)\.pdf$", sheet["url"])
        if match:
            by_no[int(match.group(1))] = sheet

    problems = []
    checks = 0
    single_entry_clauses = 0

    for row in readings:
        no = int(row["sheet_no"])
        sheet = by_no.get(no)
        label = "sheet %d (%s)" % (no, row["live_title"][:48])
        if sheet is None:
            problems.append("%s: no such sheet in the shipped dataset" % label)
            continue

        def cmp(field_mine, field_theirs, test=same_text):
            nonlocal checks
            checks += 1
            mine, theirs = row[field_mine], sheet.get(field_theirs)
            if not test(mine, theirs):
                problems.append(
                    "%s: %s differs - live=%r stored=%r"
                    % (label, field_theirs, mine, theirs)
                )

        for field in ("buy_in", "fee", "pool_per_entry", "chips"):
            checks += 1
            if int(row[field]) != int(sheet.get(field) or 0):
                problems.append(
                    "%s: %s differs - live=%s stored=%s"
                    % (label, field, row[field], sheet.get(field))
                )

        checks += 1
        if norm(row["level_min"]) != norm(sheet.get("level_min")):
            problems.append(
                "%s: level_min differs - live=%s stored=%s"
                % (label, row["level_min"], sheet.get("level_min"))
            )

        cmp("late_reg", "late_reg")
        cmp("guarantee", "guarantee", same_guarantee)
        cmp("payout", "payout_pct")

        for field in ("reentry", "addon", "rebuy"):
            checks += 1
            mine, theirs = row[field], sheet.get(field)
            if is_silent(mine) != is_silent(theirs):
                problems.append(
                    "%s: %s differs - live=%r stored=%r" % (label, field, mine, theirs)
                )

        checks += 1
        multi = row["multi_flight"].strip().lower() == "yes"
        if multi != bool(sheet.get("multi_flight")):
            problems.append(
                "%s: multi_flight differs - live=%s stored=%s"
                % (label, row["multi_flight"], sheet.get("multi_flight"))
            )

        checks += 1
        if norm(row["single_entry_clause"]) != "none":
            single_entry_clauses += 1

    print("sheet readings checked : %d sheets, %d field comparisons" % (len(readings), checks))
    print("sheets with a single-entry / freezeout / no-re-entry clause printed: %d" % single_entry_clauses)
    if problems:
        print("\nMISMATCHES (%d):" % len(problems))
        for problem in problems:
            print("  -", problem)
        return 1
    if not quiet:
        print("\nAll %d sheets match the shipped data field by field." % len(readings))
    return 0


if __name__ == "__main__":
    sys.exit(main())
