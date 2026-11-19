#!/usr/bin/env python3
"""Re-check every official URL this site cites, and record content changes as a dated log.

Runs on a schedule (see .github/workflows/recheck.yml). For each URL it:
  * fetches it with a browser-like User-Agent, a cookie jar (so a redirect that sets a session
    cookie is followed instead of being written up as a 3xx) and a timeout;
  * hashes the normalised visible text for HTML and the raw bytes for PDFs;
  * compares the hash with the previous run and records CHANGED / unchanged / first check;
  * when the fetch fails, records *why* it failed. A property that refuses a datacenter runner and
    a page that has actually moved are different facts, and the site must not print them the same
    way: "not read today" is never evidence of "not changed".

Output: data/verified2026/checks.json  (append-only history, newest run first)

A changed hash means the official document moved, so the value transcribed from it must be
re-read before it is relied on. The job reports that; it never guesses at the new value and
never rewrites a table row.
"""
from __future__ import annotations

import http.cookiejar
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
import decision as decisions
import other_rooms as othermod                            # noqa: E402

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
    # Rooms whose official schedules are transcribed onto their venue pages (added 2026-11-17).
    for key, label, url in othermod.MONITOR_URLS:
        out["ROOM_" + key] = (label, url)
    for i, (label, url) in enumerate(decisions.WATCH, 1):
        out["FOLLOWUP_%02d" % i] = (label, url)
    for h in hotelsmod.HOTELS:
        for field in ("book", "tax_src", "cancel_src", "poker_rate_src"):
            if h.get(field):
                out["HOTEL_%s_%s" % (h["id"], field)] = (h["name"] + " · " + field, h[field])
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


_OPENER = None

# What each failure mode means for the reader. Printed verbatim on the Sources page, so a red row in
# the monitor log can never be read as "the source is unchanged".
MEANING = {
    "blocked": "the property's bot protection refused the runner; the page is live for a person, "
               "so this value has to be re-read by hand",
    "redirect-loop": "the host keeps redirecting without serving content (a cookie or region wall). "
                     "Not evidence that the page moved",
    "not found": "the official URL no longer serves a document - the citation itself needs correcting",
    "server error": "the official host returned 5xx. Retry before concluding anything",
    "timeout": "the request timed out; nothing about the document is proven",
    "dns": "the host did not resolve from the runner",
    "tls": "the TLS handshake failed from the runner",
    "unreachable": "the request failed; nothing about the document is proven",
}


def error_kind(code, message):
    m = str(message or "").lower()
    if code in (401, 403, 429):
        return "blocked"
    if code in (301, 302, 303, 307, 308):
        return "redirect-loop"
    if code in (404, 410, 451):
        return "not found"
    if code and int(code) >= 500:
        return "server error"
    if "timed out" in m or "timeout" in m:
        return "timeout"
    if "resolve" in m or "nodename" in m or "network is unreachable" in m:
        return "dns"
    if "certificate" in m or "ssl" in m or "tls" in m:
        return "tls"
    return "unreachable"


def opener():
    global _OPENER
    if _OPENER is None:
        _OPENER = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
            urllib.request.HTTPRedirectHandler())
    return _OPENER


def fetch(url):
    """One fetch. Returns (status, bytes, final url) or raises; the final url is what a citation
    actually resolves to, which is how a moved page is told apart from a blocked one."""
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })
    with opener().open(req, timeout=60) as r:
        return r.getcode(), r.read(), r.geturl()


def prior_observations(history):
    """Keep the latest readable baseline by URL across errors and registry-key renames."""
    baselines, changes = {}, {}
    for run in history:
        for row in run.get("results", []):
            url = row["url"]
            if row.get("hash"):
                baselines.setdefault(url, row["hash"])
            changed = row.get("last_changed") or (run.get("checked") if row.get("change") == "CHANGED" else None)
            if changed:
                changes.setdefault(url, changed)
    return baselines, changes


def main():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    history = []
    if os.path.exists(OUT):
        try:
            history = json.load(open(OUT, encoding="utf-8")).get("runs", [])
        except Exception:
            history = []
    previous, changes = prior_observations(history)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    results = []
    for key, (label, url) in sorted(sources().items()):
        row = dict(key=key, label=label, url=url)
        try:
            code, raw, final = fetch(url)
            row["status"] = code
            row["hash"], row["hash_method"] = content_hash(url, raw)
            row["bytes"] = len(raw)
            if final and final.rstrip("/") != url.rstrip("/"):
                # kept, because a citation that resolves somewhere else is a citation to fix
                row["resolved_to"] = final
            old = previous.get(url)
            if old is None:
                row["change"] = "first check"
            elif old != row["hash"]:
                row["change"] = "CHANGED"
                changes[url] = now
            else:
                row["change"] = "unchanged"
        except urllib.error.HTTPError as e:
            kind = error_kind(e.code, e.reason)
            row.update(status=e.code, hash=None, change="fetch error", error="HTTP %s" % e.code,
                       error_kind=kind, reason=MEANING[kind])
        except Exception as e:  # noqa: BLE001
            kind = error_kind(None, str(e))
            row.update(status=None, hash=None, change="fetch error", error=str(e)[:180],
                       error_kind=kind, reason=MEANING[kind])
        if url in changes:
            row["last_changed"] = changes[url]
        results.append(row)
        print("%-10s %-12s %s" % (row.get("status"), row["change"], key))

    kinds = {}
    for r in results:
        if r["change"] == "fetch error":
            k = r.get("error_kind") or "unreachable"
            kinds[k] = kinds.get(k, 0) + 1

    readable_rows = [r for r in results if r.get("hash")]
    if not readable_rows and "--allow-no-network" not in sys.argv:
        # A run where nothing could be fetched proves nothing about the sources, and recording it
        # would (a) replace the site's last real coverage number with "0 of 61 read" and (b) strip
        # every row's badge, making the tables look less checked than they are. This has happened:
        # a run inside a sandbox with no outbound access produced exactly this state.
        print("ABORT: 0 of %d URLs were readable. Nothing is written and no run is recorded, "
              "because \"every fetch failed\" describes the network this command ran on, not the "
              "official documents. Pass --allow-no-network to record it deliberately." % len(results))
        return 1

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
        readable=sum(1 for r in results if r.get("hash")),
        # Coverage, stated as a number the reader can hold the job to: URLs whose fetch failed are not
        # "checked and unchanged", and a first-time check is not "unchanged" either.
        by_error_kind=kinds,
        coverage="%d of %d URLs could be read by this run" % (sum(1 for r in results if r.get("hash")),
                                                              len(results)),
        note=("HTML is hashed from normalised visible text; PDFs are hashed as raw response bytes. "
              "A CHANGED row means the official document moved, so every value transcribed from it "
              "must be re-read before it is relied on. A fetch error is a monitoring failure, not a "
              "verdict: the value it covers keeps its own last human-verified date. "
              "This job reports; it never rewrites a value."),
        runs=history,
    )
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
    print("\n%d URLs monitored, %d changed, %d errors. Wrote %s"
          % (len(results), len(changed), payload["errors"], OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
