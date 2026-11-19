#!/usr/bin/env python3
"""Fail if any file GitHub Pages publishes contains an unresolved merge-conflict marker.

Why this exists: PR #100 (601f62f) committed a stray ``<<<<<<< HEAD`` into index.html and
was merged even though its own `verify` check failed; the marker was live on
https://karagemop466-tech.github.io/Poker2/ until 7edf1b7 repaired main. The generator
drift check alone does not catch this class of defect (a hand-edited page can still match
a generator run that happens afterwards), so it gets its own cheap gate.

Line-anchored on purpose: prose may legitimately quote the marker (COORDINATION.md does),
and only lines that *begin* with a marker are unresolved-conflict syntax.

Usage: python3 scripts/check_conflict_markers.py
"""
import subprocess
import sys

GLOBS = [
    "*.html", "2026/*.html", "2026/venues/*.html", "plan/*.html", "plan/venues/*.html",
    "venues/*.html", "docs/*.html", "verified/**/*.html", "archive/**/*.html",
    "assets/*.js", "assets/*.css", "2026/assets/*.js", "2026/assets/*.css",
    "plan/assets/*.js", "site-data/*.json",
]
MARKERS = ("<<<<<<< ", ">>>>>>> ", "^=======$")

bad = []
files = subprocess.run(
    ["git", "ls-files"] + GLOBS, capture_output=True, text=True, check=True
).stdout.split()
for path in files:
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, 1):
                if line.startswith("<<<<<<< ") or line.startswith(">>>>>>> ") \
                        or line.rstrip("\n") == "=======":
                    bad.append("%s:%d: %s" % (path, i, line.rstrip()[:60]))
    except OSError as ex:
        bad.append("%s: unreadable (%s)" % (path, ex))

if bad:
    print("::error::Unresolved merge-conflict markers found in published files:")
    for b in bad:
        print("  " + b)
    sys.exit(1)
print("conflict-marker check ok: %d published files clean" % len(files))
