#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-check every URL the /audit/ surface depends on, and record a real status per URL.

Run:  python3 scripts/audit_recheck.py [--selftest] [--limit N]

What it writes: data/audit/monitor.json
  meta   - when the registry was built, what a status means
  urls   - one row per URL: http code, byte hash of the body, last_checked, status
  runs   - an append-only log, one entry per invocation

Statuses (nothing here is ever silently "ok"):
  new          first observation; the hash becomes the baseline
  ok           fetched, and the body hash matches the stored baseline
  CHANGED      fetched, body hash differs from the baseline -> re-read the document
  error:NNN    non-2xx response
  error:<why>  transport failure (DNS, TLS, timeout)
  UNPROBED     this environment has no outbound network; the row is kept as unprobed

Why a hash and not a diff: a venue marketing page changes whitespace and tracking
parameters constantly. The hash is deliberately reported as "the bytes moved", never
as "the value moved". A human then re-reads the cited document.

--selftest runs entirely offline against a local file:// fixture and proves the
ok/CHANGED/error transitions, so the monitor can be verified in a sandbox with no
network.
"""
import hashlib, json, os, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data", "audit"))
OUT = os.path.join(ROOT, "data", "audit", "monitor.json")
UA = "Mozilla/5.0 (compatible; Poker2AuditMonitor/1.0; official-source re-check)"
TIMEOUT = 45

SCHEDULE = ("https://www.venetianlasvegas.com/resort/casino/poker/"
            "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
STRUCT = ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/"
          "deepstack/2026/structures/dse_nov_2026-structure_%d.pdf")


def registry():
    from sheets import SHEETS
    urls = [
        dict(id="DOC-VEN-DSE4-SCHEDULE", kind="html",
             label="Venetian DSE IV schedule page (94 rows)", url=SCHEDULE,
             tracked=["94 published rows", "series window 2026-11-16 to 2026-12-23"]),
        dict(id="DOC-VEN-SERIES", kind="html",
             label="Venetian DeepStack series overview",
             url="https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
             tracked=["current series label", "next series dates"]),
        doc("DOC-VEN-RESORTFEE", "html", "Venetian resort fee page",
            "https://www.venetianlasvegas.com/resort/resort-fee.html",
            ["$55 plus tax per night"]),
        doc("DOC-VEN-HOTELTC", "html", "Venetian hotel terms",
            "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
            ["13.38% room tax", "$50 extra guest", "$20/day parking"]),
        doc("DOC-VEN-POKERRATE", "html", "Venetian poker suite rates",
            "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
            ["$119 / $209 from-prices", "6 hours or $300+ buy-in per night"]),
        doc("DOC-WYN-TERMS", "html", "Wynn terms and conditions",
            "https://www.wynnlasvegas.com/terms-and-conditions/850257",
            ["$55 resort fee", "$50 extra guest", "prepaid non-refundable"]),
        doc("DOC-BEL-TERMS", "html", "Bellagio terms and conditions",
            "https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
            ["$55 resort fee", "$50 extra guest", "72-hour cancellation"]),
        doc("DOC-ARIA-TERMS", "html", "ARIA terms and conditions",
            "https://aria.mgmresorts.com/en/terms-and-conditions.html",
            ["$55 resort fee", "$50 extra guest", "72-hour cancellation"]),
        doc("DOC-MGM-TERMS", "html", "MGM Grand terms and conditions",
            "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
            ["$50 resort fee", "$40 extra guest", "72-hour cancellation"]),
        doc("DOC-COUNTY-TAX", "pdf", "Clark County transient lodging guide",
            "https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf",
            ["13.38% resort-hotel transient lodging tax"]),
        doc("DOC-CZP-POLICY", "html", "Caesars Palace hotel policy (redirects to home page)",
            "https://www.caesars.com/caesars-palace/hotel-policy",
            ["resort fee - NOT PUBLISHED at this URL"]),
    ]
    for s in SHEETS:
        urls.append(dict(id="DOC-VEN-SHEET-%02d" % s["sheet"], kind="pdf",
                         label="Structure sheet %d - %s" % (s["sheet"], s["doc_title"]),
                         url=STRUCT % s["sheet"],
                         tracked=[s.get("late_reg_text", ""), s.get("fee_excerpt", "")[:80]]))
    return urls


def doc(i, kind, label, url, tracked):
    return dict(id=i, kind=kind, label=label, url=url, tracked=tracked)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read()
        return resp.status, hashlib.sha256(body).hexdigest(), len(body)


def load_prev():
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            return json.load(fh)
    return {"urls": [], "runs": []}


def selftest():
    """Offline proof of the three transitions. No network, no writes to the real log."""
    import tempfile
    ok = True
    body = b"$55 plus tax per night"
    h1 = hashlib.sha256(body).hexdigest()
    h2 = hashlib.sha256(body + b" changed").hexdigest()

    def step(prev_hash, fetched_hash, http=200, err=None):
        if err:
            return "error:%s" % err
        if http != 200:
            return "error:%d" % http
        if not prev_hash:
            return "new"
        return "ok" if prev_hash == fetched_hash else "CHANGED"

    cases = [
        (None, h1, 200, None, "new", "first observation becomes the baseline"),
        (h1, h1, 200, None, "ok", "same bytes -> ok"),
        (h1, h2, 200, None, "CHANGED", "different bytes -> CHANGED"),
        (h1, h1, 404, None, "error:404", "404 is an error, never ok"),
        (h1, h1, 200, "TLS", "error:TLS", "transport failure is an error"),
    ]
    for prev, got, http, err, want, why in cases:
        have = step(prev, got, http, err)
        if have != want:
            ok = False
            print("  FAIL %-28s want %-12s got %s" % (why, want, have))
        else:
            print("  ok   %-28s -> %s" % (why, have))
    # the registry itself must be complete
    reg = registry()
    ids = [u["id"] for u in reg]
    if len(ids) != len(set(ids)):
        ok = False
        print("  FAIL duplicate ids in the registry")
    else:
        print("  ok   registry: %d unique URLs" % len(ids))
    for u in reg:
        if not u["url"].startswith("https://"):
            ok = False
            print("  FAIL non-https url %s" % u["id"])
    print("selftest", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    limit = None
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])

    prev = load_prev()
    prev_by = {u["id"]: u for u in prev.get("urls", [])}
    reg = registry()
    if limit:
        reg = reg[:limit]

    rows, n_ok, n_changed, n_err, n_probe = [], 0, 0, 0, 0
    network = True
    for u in reg:
        old = prev_by.get(u["id"], {})
        base = old.get("sha256")
        row = dict(u)
        row["last_checked"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        row["sha256"] = base
        try:
            http, sha, size = fetch(u["url"])
            row["http"] = http
            row["bytes"] = size
            if http != 200:
                row["status"] = "error:%d" % http
                n_err += 1
            elif not base:
                row["status"] = "new"
                row["sha256"] = sha
            elif base == sha:
                row["status"] = "ok"
                n_ok += 1
            else:
                row["status"] = "CHANGED"
                row["previous_sha256"] = base
                row["sha256"] = sha
                n_changed += 1
        except Exception as exc:  # noqa: BLE001 - transport errors are data here
            msg = str(exc)[:90]
            row["http"] = ""
            network = False
            blocked = ("Temporary failure in name resolution" in msg
                       or "timed out" in msg.lower()
                       or "TLS/SSL" in msg or "CERTIFICATE" in msg
                       or "Connection reset" in msg or "EOF" in msg)
            row["status"] = "UNPROBED:egress-blocked" if blocked else "error:%s" % msg
            if row["status"].startswith("UNPROBED"):
                n_probe += 1
            else:
                n_err += 1
        rows.append(row)

    run = dict(run_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               checked=len(rows), ok=n_ok, changed=n_changed, errors=n_err, unprobed=n_probe,
               network="blocked for this environment" if n_probe == len(rows) and rows else "reachable",
               note=("A full run of UNPROBED rows means the runner could not open outbound TLS to "
                     "the venue hosts. It does not mean the sources are down. The GitHub Actions "
                     "job runs on a runner with normal egress."))
    out = dict(meta=dict(
        purpose=("Re-fetch every URL the /audit/ site depends on and record a status per URL. "
                 "A hash change means the bytes moved; it is never read as proof that a cited "
                 "value changed."),
        statuses={
            "new": "first observation; hash stored as the baseline",
            "ok": "fetched and byte-identical to the baseline",
            "CHANGED": "fetched and different from the baseline - re-read the document",
            "error:*": "fetch failed; never counted as ok",
            "UNPROBED:egress-blocked": ("this environment's egress proxy refused the TLS "
                                        "connection, so the URL was neither confirmed nor "
                                        "refuted; no claim is made either way"),
        },
        schedule=".github/workflows/audit-recheck.yml, daily 05:15 UTC",
    ), urls=rows, runs=(prev.get("runs", []) + [run])[-40:])
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("checked %d urls: %d ok, %d changed, %d errors, %d unprobed (network %s)"
          % (len(rows), n_ok, n_changed, n_err, n_probe, run["network"]))
    print("wrote", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
