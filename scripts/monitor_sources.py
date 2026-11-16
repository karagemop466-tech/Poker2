#!/usr/bin/env python3
"""Fetch official URLs in data/sources.json and record content-hash changes.

First successful observation establishes a baseline. Network/HTTP failures are
reported as unavailable, never misclassified as a changed official source.
"""
from __future__ import annotations

import concurrent.futures
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE_FILE = ROOT / "data" / "sources.json"
STATE_FILE = ROOT / "data" / "source-monitor.json"
MAX_BYTES = 25 * 1024 * 1024
TIMEOUT = 35


def read_json(path: pathlib.Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def check_one(item, previous, timestamp):
    key, entry = item
    url = entry.get("url", "")
    row = {"id": key, "label": entry.get("label", key), "url": url,
           "publisher": entry.get("publisher", ""), "last_checked": timestamp}
    prior_hash = previous.get("sha256") if previous else None
    if prior_hash:
        row["sha256"] = prior_hash
    if not url.startswith("https://"):
        row.update(status="skipped", detail="The source registry entry is not HTTPS; no request was made.")
        return row
    request = urllib.request.Request(url, headers={
        "User-Agent": "Poker2-SourceMonitor/1.0 (GitHub Actions; official-source change detection)",
        "Accept": "text/html,application/pdf,application/octet-stream,*/*",
    })
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            status_code = response.status
            digest = hashlib.sha256()
            size = 0
            while True:
                chunk = response.read(256 * 1024)
                if not chunk:
                    break
                size += len(chunk)
                if size > MAX_BYTES:
                    row.update(status="unavailable", http_status=status_code,
                               detail=f"Response exceeded {MAX_BYTES // (1024 * 1024)} MB safety limit; no comparison made.")
                    return row
                digest.update(chunk)
            new_hash = digest.hexdigest()
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        row.update(status="unavailable", detail=f"Fetch failed; previous value retained. {str(reason)[:240]}")
        return row

    row.update(http_status=status_code, sha256=new_hash, bytes=size)
    old_hash = previous.get("sha256") if previous else None
    row["sha256"] = new_hash
    if not old_hash:
        row.update(status="baseline", detail="First successful check; this hash becomes the comparison baseline.")
    elif old_hash == new_hash:
        row.update(status="unchanged", detail="Content hash matches the previous successful check.")
    else:
        row.update(status="changed", previous_sha256=old_hash,
                   detail="Official response content differs from the previous successful check; review the source before updating values.")
    return row


def main():
    sources = read_json(SOURCE_FILE, {})
    previous_doc = read_json(STATE_FILE, {})
    previous_rows = {row.get("id"): row for row in previous_doc.get("sources", [])}
    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    items = list(sources.items())
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(lambda item: check_one(item, previous_rows.get(item[0]), timestamp), items))
    rows.sort(key=lambda row: row["id"])
    changed = [row["id"] for row in rows if row["status"] == "changed"]
    unavailable = [row["id"] for row in rows if row["status"] == "unavailable"]
    result = {
        "last_checked": timestamp,
        "schedule": "Daily GitHub Actions check (07:00 UTC; may be delayed by GitHub Actions)",
        "comparison": "SHA-256 of the successful HTTP response body; a difference is a review flag, not proof that a tournament value changed.",
        "first_run_note": "First successful check per URL establishes a baseline. Changes are flagged on later successful checks.",
        "changed_count": len(changed),
        "unavailable_count": len(unavailable),
        "sources": rows,
    }
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Checked {len(rows)} registered official sources; changed={len(changed)}, unavailable={len(unavailable)}.")
    if changed:
        print("Changed sources: " + ", ".join(changed))
    if unavailable:
        print("Unavailable sources: " + ", ".join(unavailable))
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            output.write(f"changed_count={len(changed)}\n")
            output.write("changed_sources=" + json.dumps(changed, ensure_ascii=False) + "\n")
    # Keep failures visible in the workflow log without turning transient official-site
    # outages into a false changed-data assertion.
    return 0


if __name__ == "__main__":
    sys.exit(main())
