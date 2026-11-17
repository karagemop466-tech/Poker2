#!/usr/bin/env python3
"""Build the scheduled re-check registry (data/source_monitor.json) from the citations
that actually appear in the published data, instead of a hand-maintained seed list.

Every official URL cited by an event row, a hotel row or the source register is added, so
"re-check each official URL on a schedule and mark rows whose source changed" covers the
whole site rather than the 22 URLs scripts/monitor.py used to seed.

Rules
  * official hosts only - a URL on a non-official host is skipped and reported;
  * existing entries keep their sha256 / last_checked / status, so a rebuild never resets
    the change-detection baseline;
  * deterministic output: sorted by id.

Run: python3 scripts/build_monitor_registry.py
"""
import json, os, re, sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MASTER = os.path.join(ROOT, "data", "master.json")
MON = os.path.join(ROOT, "data", "source_monitor.json")

# Hosts that publish the values this site cites (venue operators, their CDN, the county).
OFFICIAL_HOSTS = (
    "venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com", "visitwynn.com",
    "caesars.com", "mgmresorts.com", "contentstack.io", "goldennugget.com",
    "clarkcountynv.gov", "westgateresorts.com", "southpointcasino.com",
    "aria.com", "bellagio.com", "cosmopolitanlasvegas.com",
)

SHEET_URL = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/"
             "2026/structures/dse_nov_2026-structure_{n}.pdf")


def is_official(url):
    host = urlparse(url).netloc.lower()
    return any(host == h or host.endswith("." + h) for h in OFFICIAL_HOSTS)


def slugify(u):
    return re.sub(r"[^a-z0-9]+", "-", u.lower()).strip("-")[:60]


def label_for(url, master, hotel_names):
    """Short human label, reusing the source register when the URL appears in it."""
    for key, v in (master.get("sources") or {}).items():
        if isinstance(v, dict) and v.get("url") == url:
            return v.get("label") or key
    if "structure_" in url:
        n = re.search(r"structure_(\d+)\.pdf", url)
        return "Venetian DSE IV structure sheet %s" % (n.group(1) if n else "?")
    if url in hotel_names:
        return "%s: booking / rate page" % hotel_names[url]
    host = urlparse(url).netloc.lower().replace("www.", "")
    path = (urlparse(url).path.rstrip("/") or "site root").replace("/en/", "")
    return "%s: %s" % (host, path)


def collect(master):
    """All official URLs the published rows cite, keyed by url."""
    found = {}

    def add(url, kind):
        if not isinstance(url, str) or not url.startswith("https://"):
            return
        if not is_official(url):
            found.setdefault("_skipped", set()).add(urlparse(url).netloc)
            return
        found.setdefault(url, kind)

    src = master.get("sources") or {}
    for v in src.values():
        if isinstance(v, dict):
            add(v.get("url"), "source register")
    for e in master.get("events", []):
        add(e.get("source_url"), "event row")
        add(e.get("struct_url"), "structure sheet")
    for h in master.get("hotels", []):
        add(h.get("booking_url"), "hotel booking")
        add(h.get("resort_fee_src"), "hotel fee terms")
        for entry in (h.get("rate_log") or []):
            if isinstance(entry, dict):
                add(entry.get("url") or entry.get("source_url"), "dated rate observation")
    # The 37 Venetian structure sheets are individually cited by rows; make sure a sheet
    # that loses its row is still monitored, because its hash is the change signal.
    for n in range(1, 38):
        add(SHEET_URL.format(n=n), "structure sheet")
    return found


def main():
    master = json.load(open(MASTER, encoding="utf8"))
    hotel_names = {}
    for h in master.get("hotels", []):
        u = h.get("booking_url")
        if isinstance(u, str) and u.startswith("https://") and u not in hotel_names:
            hotel_names[u] = h.get("name") or h.get("id") or "hotel"
    old = {"urls": []}
    if os.path.exists(MON):
        old = json.load(open(MON, encoding="utf8"))
    prev = {u["url"]: u for u in old.get("urls", []) if isinstance(u, dict) and u.get("url")}

    found = collect(master)
    skipped = sorted(found.pop("_skipped", set()))

    urls = []
    for url in sorted(found):
        kind = found[url]
        keep = prev.get(url) or {}
        sid = keep.get("id") or ("%s-%s" % (slugify(urlparse(url).netloc.replace("www.", "")),
                                            slugify(url)[-40:]))
        urls.append({
            "id": sid,
            "label": keep.get("label") or label_for(url, master, hotel_names),
            "url": url,
            "cited_by": kind,
            "sha256": keep.get("sha256"),
            "http_status": keep.get("http_status"),
            "last_checked": keep.get("last_checked"),
            "status": keep.get("status", "never checked"),
        })
    # keep any previously registered URL so a baseline hash is never silently dropped
    for url, keep in prev.items():
        if url not in found and is_official(url):
            entry = dict(keep)
            entry.setdefault("cited_by", "carried over from an earlier register")
            urls.append(entry)
    urls.sort(key=lambda u: u["id"])

    out = {
        "note": ("Scheduled official-URL re-check (change monitoring + daily snapshots). "
                 "Generated by scripts/build_monitor_registry.py from the URLs cited in "
                 "data/master.json plus the full set of Venetian DSE IV structure sheets; "
                 "scripts/monitor.py fetches every entry, hashes it and flags the rows that "
                 "cite a changed URL. Hashes are established on the first scheduled run."),
        "generated_by": "scripts/build_monitor_registry.py",
        "urls": urls,
    }
    if old.get("last_run"):
        out["last_run"] = old["last_run"]
    with open(MON, "w", encoding="utf8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("registry: %d official URLs registered (%d already had a baseline hash)"
          % (len(urls), sum(1 for u in urls if u.get("sha256"))))
    if skipped:
        print("skipped non-official hosts:", ", ".join(skipped))
    return 0


if __name__ == "__main__":
    sys.exit(main())
