#!/usr/bin/env python3
"""Re-check every official source URL on a daily schedule.

For each URL in data/site/sources.json: fetch it, store a SHA-256 snapshot,
append a dated row to data/site/monitor.json, and mark rows whose content
changed since the previous run. Changes are flagged on the monitor page and on
any table whose source row changed. Trigger manually via workflow_dispatch
until the branch merges to main (the cron schedule activates on GitHub Pages
once the workflow file is on the default branch).
"""
import hashlib, json, os, sys, urllib.request, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "data", "site")
TODAY = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "PokerTripMonitor/1.0 (+GitHub Actions)"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read()

def main():
    sources = json.load(open(os.path.join(SITE, "sources.json")))
    mon = json.load(open(os.path.join(SITE, "monitor.json")))
    by_url = {r["url"]: r for r in mon["rows"]}
    log_path = os.path.join(SITE, "monitor-log.json")
    log = json.load(open(log_path)) if os.path.exists(log_path) else []
    changed_urls = []
    for sid, s in sorted(sources.items()):
        url = s["url"]
        row = by_url.setdefault(url, {"source_id": sid, "url": url, "label": s["label"],
                                      "last_checked": None, "last_changed": None,
                                      "status": "not yet checked", "sha256": None, "changed": False})
        try:
            body = fetch(url)
            digest = hashlib.sha256(body).hexdigest()
            changed = row["sha256"] is not None and row["sha256"] != digest
            row["changed"] = changed
            if changed:
                row["last_changed"] = TODAY
                changed_urls.append(url)
            row["sha256"] = digest
            row["last_checked"] = TODAY
            row["status"] = "ok (%d KB)" % (len(body) // 1024)
        except Exception as exc:  # keep the previous snapshot; surface the error
            row["changed"] = True
            row["status"] = "fetch error: %s" % exc
        log.append({"date": TODAY, "source_id": sid, "url": url,
                    "status": row["status"], "changed": row["changed"]})
    mon["rows"] = sorted(mon["rows"], key=lambda r: (r["label"] or ""))
    mon["last_run"] = TODAY
    mon["changed_this_run"] = sorted(set(changed_urls))
    json.dump(mon, open(os.path.join(SITE, "monitor.json"), "w"), indent=1)
    json.dump(log, open(log_path, "w"), indent=1)
    print("checked", len(mon["rows"]), "urls; changed:", len(set(changed_urls)))
    if changed_urls:
        print("CHANGED:")
        for u in sorted(set(changed_urls)):
            print(" -", u)

if __name__ == "__main__":
    main()
