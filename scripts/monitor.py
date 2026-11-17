#!/usr/bin/env python3
"""Scheduled official-URL re-check (change monitoring + snapshots).

Reads data/source_monitor.json, fetches every registered official URL, hashes the
normalized content, compares with the stored hash, and writes:
  data/source_monitor.json  (url, label, sha256, last_checked, last_attempt, status, snapshot)
  data/monitor-report.md    (human-readable run report)
  data/snapshots/<date>/<slug>.html   (only when the content is new or has changed)
  data/snapshots/latest/<slug>.html   (the copy the current hash was taken from)

Status vocabulary — each one says exactly what the run proved:
  never checked — the URL is registered, no fetch has ever succeeded
  new           — first successful fetch; the baseline hash is established here
  unchanged     — fetched, hash matches the stored hash (this is NOT a re-reading of the
                  values: a matching page can still carry a value the site transcribed wrong)
  changed       — fetched, hash differs → every row citing this URL is badged on the site
  unreachable   — the fetch failed (DNS/TLS/403/500/timeout). Nothing is proven; the row's
                  verification date is deliberately NOT advanced

Two rules this tool exists to keep:
  * a failed fetch never advances a date and never clears a previous status;
  * a snapshot is only written when its bytes differ, so a daily job cannot fill the
    repository with 80 identical copies of the same page.

`--dry-run` fetches and reports without touching any file, so a run can be checked in an
environment that has no outbound access (where every URL reports unreachable — which is a
statement about the sandbox, not about the sources).

Runs in GitHub Actions (.github/workflows/source-monitor.yml).
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
    """One fetch, one truth. Returns (text, status); raises on any failure."""
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; Poker2SourceMonitor/1.0; "
                      "+https://github.com/karagemop466-tech/Poker2)"})
    with urllib.request.urlopen(req, timeout=45) as r:
        return r.read(), r.status


def write_snapshot(rel, text):
    full = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(text)


def main(dry=False):
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    if os.path.exists(MON):
        with open(MON) as f:
            mon = json.load(f)
    else:
        mon = {"urls": [], "note": "Hashes are established on first successful check. "
                                   "'changed' means the normalized page content differs from the stored hash."}
    by_url = {u["url"]: u for u in mon.get("urls", [])}

    # make sure every seed URL is registered
    for sid, label, url in SEED:
        if url not in by_url:
            rec = {"id": sid, "label": label, "url": url, "sha256": None,
                   "last_checked": None, "last_attempt": None, "status": "never checked",
                   "http_status": None, "snapshot": None, "consecutive_failures": 0}
            mon["urls"].append(rec)
            by_url[url] = rec

    changed, failed, first_baseline = [], [], []
    for rec in mon["urls"]:
        url = rec["url"]
        try:
            raw, code = fetch(url)
        except Exception as ex:
            # Nothing is proven by a failed fetch: keep the old hash, keep the old
            # verification date, and say which failure it was.
            rec["last_attempt"] = today
            rec["consecutive_failures"] = int(rec.get("consecutive_failures") or 0) + 1
            kind = "unreachable"
            detail = str(ex)[:140]
            m = re.search(r"HTTP Error (\d{3})", detail)
            if m:
                rec["http_status"] = int(m.group(1))
                kind = "blocked (HTTP %s)" % m.group(1) if m.group(1) in ("401", "403", "429") else "http %s" % m.group(1)
            elif "timed out" in detail.lower():
                kind = "timeout"
            elif "Temporary failure in name resolution" in detail or "getaddrinfo" in detail:
                kind = "no network route from this runner"
            rec["status"] = "unreachable — %s" % kind
            failed.append((rec["label"], kind, rec["consecutive_failures"]))
            continue

        text = norm_text(raw)
        digest = hashlib.sha256(text.encode()).hexdigest()
        had_baseline = rec.get("sha256") is not None
        rec["last_attempt"] = today
        rec["last_checked"] = today          # a successful fetch is the only thing that earns a date
        rec["http_status"] = code
        rec["consecutive_failures"] = 0
        # snapshot only when the bytes differ from what is already on disk
        rel_latest = os.path.join("data", "snapshots", "latest", slug(url) + ".html")
        prev_path = rec.get("snapshot")
        differs = True
        if prev_path and os.path.exists(os.path.join(ROOT, prev_path)):
            try:
                with open(os.path.join(ROOT, prev_path), encoding="utf-8") as f:
                    differs = f.read() != text
            except Exception:
                differs = True
        if differs and not had_baseline:
            differs = True
        if differs and not dry:
            write_snapshot(os.path.join("data", "snapshots", today, slug(url) + ".html"), text)
            write_snapshot(rel_latest, text)
            rec["snapshot"] = rel_latest
            rec["snapshot_date"] = today
        if not had_baseline:
            rec["status"] = "new"
            rec["sha256"] = digest
            first_baseline.append(rec["label"])
        elif digest != rec.get("sha256"):
            rec["status"] = "changed"
            rec["previous_sha256"] = rec.get("sha256")
            rec["sha256"] = digest
            rec["changed_on"] = today
            changed.append(rec["label"])
        else:
            rec["status"] = "unchanged"

    mon["last_run"] = today
    mon["last_run_summary"] = {
        "urls": len(mon["urls"]), "changed": len(changed), "unreachable": len(failed),
        "baselines_established": len(first_baseline),
        "note": ("A run that establishes a baseline proves the page is reachable, not that the "
                 "site's transcription of it is right. Rows keep their own verification date; the "
                 "monitor adds a separate 'source re-checked' marker, never a new 'verified' claim."),
    }
    if not dry:
        with open(MON, "w") as f:
            json.dump(mon, f, indent=1)

    lines = ["# Source monitor report — %s" % today, "",
             "Run by `scripts/monitor.py` (scheduled daily). %d URLs registered · %d reachable · "
             "%d changed · %d unreachable." % (len(mon["urls"]), len(mon["urls"]) - len(failed),
                                                len(changed), len(failed)),
             "",
             "| Source | Status | Last successful check | Consecutive failures |",
             "|---|---|---|---|"]
    for rec in mon["urls"]:
        lines.append("| %s | %s | %s | %s |" % (rec["label"], rec.get("status") or "—",
                                                 rec.get("last_checked") or "never",
                                                 rec.get("consecutive_failures") or 0))
    if first_baseline:
        lines += ["", "## Baselines established this run", "",
                  "These URLs had never been fetched before, so this run only records what they look like "
                  "now. It does not confirm that the values the site cites from them were transcribed "
                  "correctly — that is what a manual re-read does.",
                  ""] + ["- %s" % c for c in first_baseline]
    if changed:
        lines += ["", "## CHANGED sources — rows citing these are marked 'source changed — re-check' on the site:",
                  ""] + ["- %s" % c for c in changed]
    if failed:
        lines += ["", "## Unreachable (no date advanced, no status cleared)", ""]
        lines += ["- %s — %s (after %d consecutive failed attempts)" % f for f in failed]
    if not dry:
        with open(REPORT, "w") as f:
            f.write("\n".join(lines) + "\n")

    print("monitor: %d urls, %d changed, %d unreachable, %d baselines established%s"
          % (len(mon["urls"]), len(changed), len(failed), len(first_baseline), " (dry run)" if dry else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(dry=("--dry-run" in sys.argv)))
