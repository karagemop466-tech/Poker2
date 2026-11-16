#!/usr/bin/env python3
"""Re-check every official source URL and record content changes as a dated log.

Runs on a schedule (see .github/workflows/recheck.yml). For each URL:
  * fetch it with a browser-like User-Agent and a timeout;
  * strip HTML tags / normalise whitespace for HTML; hash PDFs as raw bytes;
  * store a SHA-256 short hash plus the HTTP status;
  * compare with the previous run and append a change record when the hash moves.

Output: data/site/checks.json  (append-only history, newest run first)
Exit code is always 0 for content changes; a hard error only if the file cannot
be written. Content drift is data, not a build failure.
"""
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
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import dataset as D  # noqa: E402

OUT = os.path.join(ROOT, "data", "site", "checks.json")
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0 Safari/537.36")


def normalise(raw):
    text = raw.decode("utf-8", "ignore")
    text = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = text.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"\s+", " ", text).strip()


def content_hash(url, raw):
    """Return a short SHA-256 and method; preserve all PDF bytes, normalise HTML text."""
    if urlsplit(url).path.lower().endswith(".pdf"):
        body = raw
        method = "raw PDF bytes"
    else:
        body = normalise(raw).encode("utf-8")
        method = "normalised HTML text"
    return hashlib.sha256(body).hexdigest()[:16], method


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
    for key, (label, url) in sorted(D.SOURCES.items()):
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
        print("%-10s %-8s %s" % (row.get("status"), row["change"], key))

    history.insert(0, dict(checked=now, results=results))
    history = history[:60]
    changed = [r for r in results if r["change"] == "CHANGED"]
    payload = dict(
        last_run=now,
        monitored=len(results),
        changed_this_run=len(changed),
        never_checked=sum(1 for r in results if r["change"] == "first check"),
        errors=sum(1 for r in results if r["change"] == "fetch error"),
        note=("HTML is hashed from normalised visible text; PDFs are hashed as raw response bytes. "
              "A 'CHANGED' row means the official response moved; the corresponding site "
              "value must be re-read before it is relied on."),
        runs=history,
    )
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
    print("\n%d URLs monitored, %d changed, %d errors. Wrote %s"
          % (len(results), len(changed), payload["errors"], OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
