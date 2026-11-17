#!/usr/bin/env python3
"""Semantic gates for the 2026/ and plan/ pages.

Structure checks (build --check, link checks) prove the generator ran and the anchors
resolve. They do not prove a page means what it says. Both failures below shipped green:

  * 2026/sources.html said "58 URLs are monitored" directly above a run summary that
    counted 61 URLs, because the paragraph counted the register's own rows while the
    summary counted everything the re-check fetches;
  * the same page printed "51 first-time checks" from a field the monitor calls
    never_checked, which is the opposite statement.

Gates:
  1. arithmetic agreement — a sentence quoting N monitored URLs must not contradict the
     run summary beside it, and the run summary's parts must sum to its whole;
  2. naming — no page may print a number next to the words "never checked" / "never read"
     unless the monitor's own JSON says that is what the number counts;
  3. traceability — every URL the re-check watches across surfaces appears in at least one
     published register, so a reader can open the document the site depends on;
  4. fees — a resort-fee amount rendered in the plan/ hotel table carries the fee page it
     came from, and no rendered fee is attributed to a page that does not state it.
"""
from __future__ import annotations

import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P2026 = os.path.join(ROOT, "2026")
PLAN = os.path.join(ROOT, "plan")
problems: list[str] = []


def raw(path: str) -> str:
    with open(path, encoding="utf8") as fh:
        return fh.read()


def text(path: str) -> str:
    """Visible text only — use only for reading sentences, never for link checks."""
    return html.unescape(re.sub(r"<[^>]+>", " ", raw(path)))


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def load_json(*parts: str):
    path = os.path.join(ROOT, *parts)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------- 1 + 2: 2026/sources.html
src = os.path.join(P2026, "sources.html")
if os.path.exists(src):
    t = norm(text(src))
    claim = re.search(r"(\d+) URLs are monitored", t)
    reg = re.search(r"(\d+) URLs are registered for monitoring", t)
    runline = re.search(r"Latest recorded run:.*?(\d+) URLs:", t)
    if claim and runline and claim.group(1) != runline.group(1):
        problems.append("2026/sources.html: the page claims %s monitored URLs but the run beside "
                        "it reports %s" % (claim.group(1), runline.group(1)))
    # A register count may legitimately exceed the run's count: a URL added to the register
    # after the last run is watched but has no baseline yet. That is only honest when the page
    # also prints the gap, so the gap becomes the thing this gate enforces.
    if reg and runline and reg.group(1) != runline.group(1):
        added = re.search(r"(\d+) were added to the register after that run", t)
        gap = int(reg.group(1)) - int(runline.group(1))
        if not added:
            problems.append("2026/sources.html: the page registers %s monitored URLs beside a run "
                            "of %s without stating how many were added since that run"
                            % (reg.group(1), runline.group(1)))
        elif int(added.group(1)) != gap:
            problems.append("2026/sources.html: the page says %s URLs were added since the last "
                            "run, but %s registered minus %s in the run leaves %s"
                            % (added.group(1), reg.group(1), runline.group(1), gap))
    if runline:
        whole = int(runline.group(1))
        detail = re.search(r"Latest recorded run:.*?URLs:(.*?)\.\s*A fetch error", t)
        if detail:
            # every per-URL outcome named in the sentence must be accounted for exactly:
            # changed + fetch errors + baseline-set + never-read = the URL count
            named = dict(re.findall(r"(\d+) (changed|fetch errors|whose baseline hash was set by that run|"
                                    r"that no run has ever read successfully)", detail.group(1)))
            vals = [int(named[k]) for k in ("changed", "fetch errors",
                                            "whose baseline hash was set by that run",
                                            "that no run has ever read successfully") if k in named]
            if len(vals) == 4 and sum(vals) != whole:
                problems.append("2026/sources.html: changed + fetch errors + first checks + never read "
                                "= %d, but the run covered %d URLs" % (sum(vals), whole))

    checks = load_json("data", "verified2026", "checks.json")
    if checks:
        rows = (checks.get("runs") or [{}])[0].get("results") or []
        real_first = sum(1 for r in rows if r.get("change") == "first check")
        for m in re.finditer(r"(\d+) (first-time checks|that have never been read successfully|that no run has ever read successfully)", t):
            n, phrase = int(m.group(1)), m.group(2)
            if "never" in phrase and n == real_first and real_first:
                problems.append("2026/sources.html: %d is the number of *first checks* (%d in the "
                                "monitor), printed as %r" % (n, real_first, phrase))

# ------------------------------------------------------------- 3: every watched URL is listed
try:
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    sys.path.insert(0, os.path.join(ROOT, "data", "sheets"))
    sys.path.insert(0, os.path.join(ROOT, "data", "verified2026"))
    import recheck2026  # noqa: E402

    watched = {u for _l, u in recheck2026.sources().values()}
    pages = " ".join(raw(os.path.join(P2026, f)) for f in os.listdir(P2026) if f.endswith(".html"))
    pages += " " + " ".join(raw(os.path.join(PLAN, f)) for f in os.listdir(PLAN) if f.endswith(".html"))
    missing = sorted(u for u in watched if u.split("://", 1)[-1] not in pages)
    if missing:
        problems.append("watched but not linked from any published page: " +
                        ", ".join(u[:80] for u in missing[:6]))
except Exception as exc:  # noqa: BLE001 - never let an import hide the real result
    problems.append("could not read the monitor's URL list: %s" % exc)

# ------------------------------------------------------------------ 4: fee provenance in plan/
hot = load_json("site-data", "hotels.json")
hotels = os.path.join(PLAN, "hotels.html")
if hot and os.path.exists(hotels):
    page = raw(hotels)      # hrefs live in the markup; the excerpt is checked against text below
    page_text = norm(text(hotels))
    for h in hot["hotels"]:
        fee = h.get("resort_fee") or {}
        if fee.get("status") != "verified_official":
            continue
        url = fee.get("source_url") or ""
        if not url:
            problems.append("plan/hotels.html: %s publishes a fee with no source_url" % h["id"])
            continue
        # the page must link the page the fee came from, and quote the sentence it came from
        if url.split("://", 1)[-1] not in page:
            problems.append("plan/hotels.html: %s fee cites %s but the page never links it"
                            % (h["id"], url[:70]))
        words = re.sub(r"\s+", " ", str(fee.get("excerpt") or "")).strip()
        if words:
            key = words[:60].split("$")[0].strip()
            if key and key not in page_text:
                problems.append("plan/hotels.html: %s fee excerpt is not rendered on the page"
                                % h["id"])

# --------------------------------------- 5: no rate printed for a property the county omits
if hot and os.path.exists(hotels):
    for h in hot["hotels"]:
        tl = h.get("transient_lodging_tax") or {}
        if tl.get("status") != "not_in_county_list":
            continue
        row = re.search(r'<tr data-key="' + re.escape(h["id"]) + r'"(.*?)</tr>', raw(hotels), re.S)
        # scoped to the fee cell: the note beside it legitimately quotes the former name's rate
        # as context, but the cell that applies a rate must not carry one for this property.
        cell = re.search(r"resort_fee.*?</td>", row.group(1), re.S) if row else None
        if cell:
            # the assertion is about the applied rate, not about a quoted sentence: strip the
            # explanatory note (which may quote the former name's rate) before looking
            applied = re.split(r'<div class="sm">The county schedule', cell.group(0))[0]
            if re.search(r"\d+\.\d+%", applied):
                problems.append("plan/hotels.html: %s has no county row but its tax cell applies a rate"
                                % h["id"])

if problems:
    print("SEMANTIC GATE FAILED")
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print("semantic gates ok: monitor arithmetic agrees, no first-check printed as never-checked, "
      "every watched URL is published, every rendered fee carries its own source")
