#!/usr/bin/env python3
"""Gate the /plan/ surface on its *published* inputs only.

Why this exists
---------------
`plan-verify.yml` (and the daily refresh's post-fetch step) used to gate on
`git diff --cached --quiet -- plan site-data`. That compared **everything** under
`site-data/`, including `change-report.json` and `snapshots/**`, which are not inputs:
they are the output of the scheduled re-check itself. Two consequences, both observed:

  * the daily `Plan: daily official-source refresh` job could not succeed on any day it
    actually wrote a re-check result — its own post-fetch `build-site.py --check` failed
    with "regenerated output differs from the committed page: flagged.html" because
    `plan/flagged.html` renders `change-report.json` (run 44124782058, main `b832ae2`);
  * the committed tree has never carried a re-check report at all (`git log --all --
    site-data/change-report.json` is empty), so in CI the pages are always rendered from
    the "no monitor run yet" branch and any real report makes that page differ.

This checker separates the two kinds of file:

  published output   plan/** and the dataset files in site-data/** that the generators
                     read (everything except the run artefacts below). These must be
                     reproduced exactly from the dataset — that is the drift gate.
  run artefacts      site-data/change-report.json, site-data/schedule-diff.json and
                     site-data/snapshots/**. They are inputs to the *renderer* (the
                     "source changed" column and the live-schedule diff table) and are
                     allowed to change on a scheduled run; they are still validated for
                     shape, so a malformed report cannot be committed either.

Usage:
  python3 scripts/check_plan_fresh.py            # snapshot-aware check (used after a run)
  python3 scripts/check_plan_fresh.py --strict    # also require plan/** to match the
                                                  # committed datasets byte for byte
Exit status is non-zero on any drift or malformed artefact.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "site-data")

ARTEFACTS = [
    "site-data/change-report.json",
    "site-data/schedule-diff.json",
]
ARTEFACT_DIRS = ["site-data/snapshots"]


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True).stdout


def changed(paths: list[str]) -> list[str]:
    """Tracked-file modifications + untracked files, restricted to `paths`."""
    out = git("status", "--porcelain", "--", *paths)
    rows = []
    for line in out.splitlines():
        if not line.strip():
            continue
        rows.append(line[3:].strip())
    return rows


def check_reports() -> list[str]:
    problems: list[str] = []

    rep = os.path.join(DATA, "change-report.json")
    if os.path.exists(rep):
        try:
            d = json.load(open(rep, encoding="utf8"))
        except Exception as exc:  # noqa: BLE001 - a broken report must fail loudly
            return ["site-data/change-report.json is not valid JSON: %s" % exc]
        if not isinstance(d, dict):
            problems.append("change-report.json: expected an object")
        else:
            if not d.get("last_run"):
                problems.append("change-report.json: no last_run timestamp")
            for s in d.get("sources") or []:
                if not s.get("url", "").startswith("https://"):
                    problems.append("change-report.json: source without an https URL: %r" % s.get("id"))
                if s.get("state") in ("changed", "error", "error-new", "pattern-missing") \
                        and not (s.get("value_diffs") or s.get("error")):
                    problems.append("change-report.json: %s is %r with no diff and no error"
                                    % (s.get("id"), s.get("state")))

    dif = os.path.join(DATA, "schedule-diff.json")
    if os.path.exists(dif):
        try:
            d = json.load(open(dif, encoding="utf8"))
        except Exception as exc:  # noqa: BLE001
            return problems + ["site-data/schedule-diff.json is not valid JSON: %s" % exc]
        if not d.get("checked"):
            problems.append("schedule-diff.json: no checked timestamp")
        if d.get("state") not in (None, "ok", "changed", "parse_failed", "fetch_failed"):
            problems.append("schedule-diff.json: unknown state %r" % d.get("state"))
    return problems


def main() -> int:
    strict = "--strict" in sys.argv
    problems: list[str] = []

    # 1. Every plan page must reproduce from the datasets (the real drift gate).
    rc = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "build-site.py"), "--check"],
                        cwd=ROOT, capture_output=True, text=True)
    if rc.returncode != 0:
        problems.append("plan/** is not reproducible from site-data/*.json:\n" + rc.stdout.strip())

    # 2. The committed *published* inputs must not have moved without a rebuild.
    allowed = set(ARTEFACTS)
    tracked_inputs = [
        os.path.join("site-data", f) for f in sorted(os.listdir(DATA))
        if os.path.isfile(os.path.join(DATA, f)) and os.path.join("site-data", f) not in allowed
    ]
    moved = [p for p in changed(tracked_inputs) if p not in allowed]
    if moved:
        problems.append("published dataset files changed but the pages were not rebuilt: "
                        + ", ".join(moved))

    if strict:
        pages = [p for p in changed(["plan"]) if not p.endswith("/")]
        if pages:
            problems.append("plan/** differs from the committed output: " + ", ".join(pages))

    # 3. Run artefacts are allowed to move, but never to be malformed.
    problems.extend(check_reports())

    if problems:
        print("PLAN FRESHNESS CHECK FAILED")
        for p in problems:
            print("  - " + p)
        return 1

    n_art = len([p for p in changed(ARTEFACTS + ARTEFACT_DIRS)])
    print("plan freshness: pages reproduce from the datasets; %d run artefact file(s) present "
          "(allowed to move on a scheduled run)" % n_art)
    return 0


if __name__ == "__main__":
    sys.exit(main())
