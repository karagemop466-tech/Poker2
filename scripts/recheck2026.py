#!/usr/bin/env python3
"""Re-check every official URL this site cites, and record content changes as a dated log.

Runs on a schedule (see .github/workflows/recheck.yml). For each URL it:
  * fetches it with a browser-like User-Agent and a timeout;
  * hashes the normalised visible text for HTML and the raw bytes for PDFs;
  * compares the hash with the previous run and records CHANGED / unchanged / first check.

Output: data/verified2026/checks.json  (append-only history, newest run first)

A changed hash means the official document moved, so the value transcribed from it must be
re-read before it is relied on. The job reports that; it never guesses at the new value and
never rewrites a table row.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data", "sheets"))
sys.path.insert(0, os.path.join(ROOT, "data", "verified2026"))

import part1, part2, part3, part4, part5, part6          # noqa: E402
import schedule as sched                                  # noqa: E402
import hotels as hotelsmod                                # noqa: E402
import content as contentmod                              # noqa: E402

OUT = os.path.join(ROOT, "data", "verified2026", "checks.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")


def sources():
    """Every URL the site cites, keyed for diffing. Built from the data, so it cannot drift."""
    out = {}
    out["VSERIES"] = ("Venetian DeepStack series overview page", sched.SERIES_URL)
    out["VEVENT"] = ("Venetian DSE IV event page (schedule table)", sched.SCHEDULE_URL)
    out["VSCHED"] = ("Venetian DSE IV schedule PDF", sched.SCHEDULE_PDF)
    out["VPOKER"] = ("Venetian poker room page", sched.POKER_ROOM_URL)
    for n in sorted(part1.SHEETS):
        s = part1.SHEETS[n]
        out["VSTRUCT%02d" % n] = ("Venetian DSE IV structure sheet %d" % n, s["url"])
    out["VFEE"] = ("Venetian resort fee page",
                   "https://www.venetianlasvegas.com/resort/resort-fee.html")
    out["VRATES"] = ("Venetian poker suite rates page",
                     "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html")
    out["VTC"] = ("Venetian hotel terms and conditions",
                  "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html")
    out["CCTAX"] = ("Clark County transient lodging tax guide", contentmod.ROOM_TAX["source"])
    for h in hotelsmod.HOTELS:
        if h.get("resort_fee_src"):
            out["HFEE_" + h["id"].upper().replace("-", "")] = (
                "%s resort fee source" % h["name"], h["resort_fee_src"])
        if h.get("parking_src"):
            out["HPARK_" + h["id"].upper().replace("-", "")] = (
                "%s parking source" % h["name"], h["parking_src"])
    for v in contentmod.OTHER_VENUES:
        key = re.sub(r"[^A-Z0-9]", "", v["name"].upper())[:12]
        out["VEN_" + key] = ("%s official page" % v["name"], v["url"])
        for i, f in enumerate(v["earlier_findings"]):
            out["VEN_%s_%d" % (key, i + 1)] = ("%s official document" % v["name"], f["url"])
    # collapse duplicates so one URL is fetched once, keeping the first label
    seen, deduped = {}, {}
    for k in sorted(out):
        label, url = out[k]
        if url in seen:
            continue
        seen[url] = k
        deduped[k] = (label, url)
    return deduped


def normalise(raw):
    text = raw.decode("utf-8", "ignore")
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def content_hash(url, raw):
    if urlsplit(url).path.lower().endswith(".pdf"):
        return hashlib.sha256(raw).hexdigest()[:16], "raw PDF bytes"
    return hashlib.sha256(normalise(raw).encode("utf-8")).hexdigest()[:16], "normalised HTML text"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.getcode(), r.read()


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    history = []
    if os.path.exists(OUT):
        try:
            history = json.load(open(OUT, encoding="utf-8")).get("runs", [])
        except Exception:
            history = []
    previous = {}
    if history:
        for row in history[0].get("results", []):
            previous[row["key"]] = row.get("hash")

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = []
    for key, (label, url) in sorted(sources().items()):
        row = dict(key=key, label=label, url=url)
        try:
            code, raw = fetch(url)
            row["status"] = code
            row["hash"], row["hash_method"] = content_hash(url, raw)
            row["bytes"] = len(raw)
            old = previous.get(key)
            if old is None:
                row["change"] = "first check"
            elif old != row["hash"]:
                row["change"] = "CHANGED"
            else:
                row["change"] = "unchanged"
        except urllib.error.HTTPError as e:
            row.update(status=e.code, hash=None, change="fetch error", error="HTTP %s" % e.code)
        except Exception as e:  # noqa: BLE001
            row.update(status=None, hash=None, change="fetch error", error=str(e)[:180])
        results.append(row)
        print("%-10s %-12s %s" % (row.get("status"), row["change"], key))

    history.insert(0, dict(checked=now, results=results))
    history = history[:90]
    changed = [r for r in results if r["change"] == "CHANGED"]
    payload = dict(
        last_run=now,
        monitored=len(results),
        changed_this_run=len(changed),
        # "first check" is the opposite of "never checked": it means the baseline hash was
        # just established. This field used to count it under never_checked, so the site
        # reported "51 first-time checks" from a value documented as never_checked. Both
        # counts are now published, each under the name that says what it is.
        first_check=sum(1 for r in results if r["change"] == "first check"),
        never_checked=sum(1 for r in results
                          if r["change"] not in ("first check", "unchanged", "CHANGED", "fetch error")),
        errors=sum(1 for r in results if r["change"] == "fetch error"),
        note=("HTML is hashed from normalised visible text; PDFs are hashed as raw response bytes. "
              "A CHANGED row means the official document moved, so every value transcribed from it "
              "must be re-read before it is relied on. This job reports; it never rewrites a value."),
        runs=history,
    )
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
    print("\n%d URLs monitored, %d changed, %d errors. Wrote %s"
          % (len(results), len(changed), payload["errors"], OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
