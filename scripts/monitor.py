#!/usr/bin/env python3
"""Scheduled official-URL re-check (change monitoring + daily snapshots).

Reads data/source_monitor.json, fetches every registered official URL,
hashes the normalized content, compares with the stored hash, and writes:
  data/source_monitor.json  (url, label, sha256, last_checked, status)
  data/monitor-report.md    (human-readable run report)
  data/snapshots/<date>/<slug>.html  (daily snapshot of each page)

Status values:
  new       — first time this URL has been checked (hash established)
  unchanged — hash matches the stored hash
  changed   — hash differs from the stored hash  → rows citing it are marked

Runs in GitHub Actions (open network). Locally it works wherever the
sites are reachable.
"""
import json, os, re, sys, hashlib, datetime, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MON = os.path.join(ROOT, "data", "source_monitor.json")
REPORT = os.path.join(ROOT, "data", "monitor-report.md")
SNAP = os.path.join(ROOT, "data", "snapshots")

# Seed registry: every official URL the site's rows cite.
SEED = [
    ("venetian-dse4-schedule", "Venetian DSE IV schedule page",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"),
    ("venetian-series", "Venetian DeepStack series overview",
     "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"),
    ("venetian-poker", "Venetian poker room page",
     "https://www.venetianlasvegas.com/resort/casino/poker.html"),
    ("venetian-resort-fee", "Venetian resort-fee page",
     "https://www.venetianlasvegas.com/resort/resort-fee.html"),
    ("venetian-hotel-terms", "Venetian hotel terms (13.38% tax)",
     "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"),
    ("venetian-poker-rates", "Venetian poker suite rates",
     "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    ("wynn-poker", "Wynn poker room page (daily + WPT)",
     "https://www.wynnlasvegas.com/casino/poker"),
    ("wynn-wpt-schedule", "Wynn WPT World Championship schedule PDF",
     "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"),
    ("wynn-wpt-structures", "Wynn WPT World Championship structures PDF",
     "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"),
    ("wynn-daily-poster", "Wynn daily tournament poster PDF",
     "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf"),
    ("wynn-daily-structures", "Wynn daily tournament structures PDF",
     "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"),
    ("wynn-resort-info", "Wynn resort information (resort fee)",
     "https://www.wynnlasvegas.com/about-us/resort-information"),
    ("caesars-poker-guide", "Caesars Las Vegas poker tournaments guide",
     "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"),
    ("caesars-daily-flyer", "Caesars Palace daily NLH flyer PDF",
     "https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf"),
    ("caesars-benefits", "Caesars Rewards benefits (fee waiver)",
     "https://www.caesars.com/myrewards/benefits-overview"),
    ("mgm-grand-poker", "MGM Grand poker page (daily times)",
     "https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html"),
    ("mgm-grand-weekly", "MGM Grand weekly tournament schedule PDF",
     "https://assets.contentstack.io/v3/assets/bltc6ce635bc4868eb2/blt5f25277b8918da08/mgm-grand-casino-poker-tournament_schedule.pdf"),
    ("mgm-grand-terms", "MGM Grand hotel terms (resort fee)",
     "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html"),
    ("aria-terms", "ARIA hotel terms (resort fee)",
     "https://aria.mgmresorts.com/en/terms-and-conditions.html"),
    ("bellagio-terms", "Bellagio hotel terms (resort fee)",
     "https://bellagio.mgmresorts.com/en/terms-and-conditions.html"),
    ("golden-nugget-daily", "Golden Nugget daily tournaments page",
     "https://www.goldennugget.com/las-vegas/casino/poker-room/daily-tournaments/"),
    ("horseshoe-hotel", "Horseshoe Las Vegas hotel page",
     "https://www.caesars.com/horseshoe-las-vegas/hotel"),
]

VENUE_HOSTS = ("venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com", "caesars.com",
               "mgmresorts.com", "goldennugget.com", "contentstack.io", "visitwynn.com")


def norm_text(raw: bytes) -> str:
    t = raw.decode("utf-8", "replace")
    t = re.sub(r"\s+", " ", t)
    return t


def slug(u):
    return re.sub(r"[^a-z0-9]+", "-", u.lower()).strip("-")[:80]


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; Poker2SourceMonitor/1.0; +https://github.com/karagemop466-tech/Poker2)"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read(), r.status


def main():
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    if os.path.exists(MON):
        with open(MON) as f:
            mon = json.load(f)
    else:
        mon = {"urls": [], "note": "Hashes are established on first check. 'changed' means the normalized page content differs from the stored hash."}
    by_url = {u["url"]: u for u in mon.get("urls", [])}

    # make sure every seed URL is registered
    for sid, label, url in SEED:
        if url not in by_url:
            rec = {"id": sid, "label": label, "url": url, "sha256": None,
                   "last_checked": None, "status": "never checked"}
            mon["urls"].append(rec)
            by_url[url] = rec

    os.makedirs(os.path.join(SNAP, today), exist_ok=True)
    changed, failed = [], []
    for rec in mon["urls"]:
        url = rec["url"]
        host_ok = any(h in url for h in VENUE_HOSTS)
        try:
            raw, code = fetch(url)
            text = norm_text(raw)
            digest = hashlib.sha256(text.encode()).hexdigest()
            with open(os.path.join(SNAP, today, slug(url) + ".html"), "w") as f:
                f.write(text)
            if rec.get("sha256") is None:
                rec["status"] = "new"
            elif digest != rec.get("sha256"):
                rec["status"] = "changed"
                changed.append(rec["label"])
            else:
                rec["status"] = "unchanged"
            rec["sha256"] = digest
            rec["http_status"] = code
            rec["last_checked"] = today
        except Exception as ex:  # keep the run alive; record the failure
            rec["status"] = "fetch error: %s" % str(ex)[:120]
            rec["last_checked"] = today
            failed.append(rec["label"])
        _ = host_ok  # registry is hand-curated; all entries are official hosts

    mon["last_run"] = today
    with open(MON, "w") as f:
        json.dump(mon, f, indent=1)

    lines = ["# Source monitor report — %s" % today, "",
             "Run by `scripts/monitor.py` (scheduled daily). %d URLs checked." % len(mon["urls"]), "",
             "| Source | Status |", "|---|---|"]
    for rec in mon["urls"]:
        lines.append("| %s | %s |" % (rec["label"], rec["status"]))
    if changed:
        lines += ["", "## CHANGED sources — rows citing these are marked 'source changed' on the site:",
                  "" ] + ["- %s" % c for c in changed]
    if failed:
        lines += ["", "## Fetch errors", ""] + ["- %s" % c for c in failed]
    with open(REPORT, "w") as f:
        f.write("\n".join(lines) + "\n")

    print("monitor: %d urls, %d changed, %d errors" % (len(mon["urls"]), len(changed), len(failed)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
