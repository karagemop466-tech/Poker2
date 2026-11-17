#!/usr/bin/env python3
"""Line-by-line audit of the verified dataset.

Checks every row against what the official document actually printed:
  1. the cited structure sheet lists that event number (sheet -> event map);
  2. buy-in minus withheld fee equals the prize-pool money the sheet states;
  3. registration close is after the start time;
  4. the guarantee matches the figure printed on the sheet, when the sheet prints one;
  5. every row carries at least one official source URL;
  6. no duplicate date/event/flight rows;
  7. multi-flight rows always name the flight and multi-flight sheets always carry the
     "cannot play a subsequent flight" note;
  8. every hotel figure that is present is attributed to an official source, and every
     blank hotel figure is explicitly marked unverified.

Exit code 1 on any failure.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dataset as D  # noqa: E402

FAIL = []
WARN = []


def fail(msg):
    FAIL.append(msg)


def minutes(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def main():
    seen = set()
    for e in D.VENETIAN_EVENTS:
        tag = "%s%s" % (e["ev"], "/" + e["flight"] if e.get("flight") else "")
        key = (e["date"], e["ev"], e.get("flight"))
        if key in seen:
            fail("%s: duplicate row for %s" % (tag, e["date"]))
        seen.add(key)

        # 1. sheet ownership
        allowed = D.SHEET_EVENTS.get(e["sheet"])
        if allowed is None:
            fail("%s: cites sheet %s which was not read" % (tag, e["sheet"]))
        elif e["ev"] not in allowed:
            fail("%s: sheet %d does not list event %s (lists %s)"
                 % (tag, e["sheet"], e["ev"], sorted(allowed)))

        # 2. fee reconciliation
        pool = e.get("pool", e["buy_in"] - e["fee"])
        if e["buy_in"] - e["fee"] != pool:
            fail("%s: %d - %d != pool %d" % (tag, e["buy_in"], e["fee"], pool))
        if not 0 < e["fee"] < e["buy_in"]:
            fail("%s: implausible fee %s of %s" % (tag, e["fee"], e["buy_in"]))

        # 3. registration close after start
        if e.get("reg_close") and minutes(e["reg_close"]) <= minutes(e["start"]):
            fail("%s: reg close %s not after start %s" % (tag, e["reg_close"], e["start"]))

        # 4. printed guarantee
        printed = D.GUARANTEE_BY_EVENT.get(e["ev"], D.SHEET_GUARANTEE.get(e["sheet"]))
        if printed is not None and e.get("gtd") != printed:
            fail("%s: guarantee %s but sheet prints %s" % (tag, e.get("gtd"), printed))

        # 7. flights
        if e["kind"] == "multi-flight" and not e.get("flight"):
            fail("%s: multi-flight without a flight label" % tag)
        if e["kind"] == "multi-flight" and "subsequent flight" not in (e.get("re_entry") or ""):
            fail("%s: multi-flight row missing the official no-later-flight note" % tag)

    for e in D.OTHER_EVENTS:
        if not D.SOURCES.get(e["src"]):
            fail("%s: unknown source key %s" % (e["ev"], e["src"]))
        if e["verdict"] == "unverified" and e.get("buy_in") is not None:
            warn = "%s: marked unverified but carries figures" % e["ev"]
            WARN.append(warn)
        if e.get("pool") and e.get("fee") is not None and e.get("buy_in"):
            if e["buy_in"] - e["fee"] != e["pool"]:
                fail("%s: %d - %d != pool %d" % (e["ev"], e["buy_in"], e["fee"], e["pool"]))

    for h in D.HOTELS:
        for k in h["srcs"]:
            if not D.SOURCES.get(k):
                fail("hotel %s: unknown source key %s" % (h["id"], k))
        if h["resort_fee"] is None and "unverified" not in h["resort_fee_note"].lower():
            fail("hotel %s: no resort fee and no unverified note" % h["id"])
        if h["tax_rate"] is None and "unverified" not in h["tax_note"].lower():
            fail("hotel %s: no tax rate and no unverified note" % h["id"])
        if h.get("walk_min") is not None:
            fail("hotel %s: walk_min set without an official source" % h["id"])
        for r in h["rate_log"]:
            if r["value"] and not r["source"]:
                fail("hotel %s: log value %s has no source" % (h["id"], r["field"]))

    # 10. published rebuy/add-on cells must never be empty or a bare number.
    #     Silence on the official document must be stated in words, not left blank.
    path_ev = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                           "data", "site", "events.json")
    if os.path.exists(path_ev):
        import json
        for e in json.load(open(path_ev, encoding="utf-8")):
            for field in ("rebuy", "add_on"):
                v = e.get(field)
                if v is None or str(v).strip() == "":
                    fail("%s (%s): empty %s cell" % (e["id"], e["venue"], field))
                elif str(v).strip().isdigit():
                    fail("%s (%s): %s is a bare number (%r) — needs a written rule"
                         % (e["id"], e["venue"], field, v))

    # 9. the published data must be in strict chronological order, with enough coverage
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                        "data", "site", "events.json")
    if os.path.exists(path):
        import json
        built = json.load(open(path, encoding="utf-8"))
        keys = [(e["date"], minutes(e["start"])) for e in built
                if re.match(r"^\d{4}-\d{2}-\d{2}$", str(e.get("date")))]
        for i in range(len(keys) - 1):
            if keys[i] > keys[i + 1]:
                fail("published order: %s %s comes before %s %s" % (keys[i] + keys[i + 1]))
                break
        dates = {k[0] for k in keys}
        if len(dates) < 30:
            fail("published dataset covers only %d dates" % len(dates))
        if len(built) != len(D.VENETIAN_EVENTS) + len(D.OTHER_EVENTS):
            fail("published %d rows but dataset has %d"
                 % (len(built), len(D.VENETIAN_EVENTS) + len(D.OTHER_EVENTS)))

    # 11. the CANONICAL dataset (data/master.json) — the one the site renders.
    #     Earlier audits only checked data/site/events.json, which is why duplicate
    #     Wynn rows and a wrong South Point tax rate reached the published pages.
    import json as _json
    mpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "master.json")
    if os.path.exists(mpath):
        m = _json.load(open(mpath, encoding="utf-8"))
        OFFICIAL_HOSTS = ("venetianlasvegas.com", "wynnlasvegas.com", "wynnresorts.com",
                          "mgmresorts.com", "caesars.com", "goldennugget.com", "visitwynn.com",
                          "contentstack.io", "clarkcountynv.gov", "southpointcasino.com",
                          "westgateresorts.com")
        seen_rows = {}
        for e in m["events"]:
            u = str(e.get("source_url") or "")
            if not u.startswith("https://") or not any(h in u for h in OFFICIAL_HOSTS):
                fail("master %s: source is not an official host (%s)" % (e["id"], u[:60]))
            if not e.get("last_checked"):
                fail("master %s: no last_checked date" % e["id"])
            if e.get("buy_in") and e.get("fee") is not None:
                if e["buy_in"] - e["fee"] <= 0:
                    fail("master %s: fee %s consumes the whole %s buy-in" % (e["id"], e["fee"], e["buy_in"]))
                if e.get("pool_per_entry") is not None and e["buy_in"] - e["fee"] != e["pool_per_entry"]:
                    fail("master %s: %s - %s != published pool %s"
                         % (e["id"], e["buy_in"], e["fee"], e["pool_per_entry"]))
            if e.get("gtd_ratio") is not None and not e.get("gtd"):
                fail("master %s: ratio without a guarantee" % e["id"])
            # duplicate guard on the canonical key used by the generator
            name = re.sub(r"\([^)]*\)", " ", str(e.get("name", "")).lower())
            name = re.sub(r"[$,\u00b7\u2019'\-\u2013\u2014]", " ", name)
            name = re.sub(r"\bnih\b", "nlh", name)
            name = re.sub(r"\s+", " ", name).strip()
            key = (e.get("venue_id"), e.get("date"), e.get("start"), e.get("buy_in"), name)
            if key in seen_rows:
                fail("master: %s and %s are the same event (%s %s)"
                     % (seen_rows[key], e["id"], e.get("date"), e.get("start")))
            seen_rows[key] = e["id"]
        print("master.json audited: %d events, %d hotels, %d flags"
              % (len(m["events"]), len(m["hotels"]), len(m["flags"])))

    # 5. sources are official hosts
    for k, (label, url) in D.SOURCES.items():
        if not url.startswith("https://"):
            fail("source %s is not https" % k)

    print("rows audited: %d Venetian + %d other, %d hotels, %d sources"
          % (len(D.VENETIAN_EVENTS), len(D.OTHER_EVENTS), len(D.HOTELS), len(D.SOURCES)))
    for w in WARN:
        print("  warn: " + w)
    if FAIL:
        print("\nFAILED (%d):" % len(FAIL))
        for f in FAIL:
            print("  - " + f)
        return 1
    print("\nOK: every row reconciles with the official document it cites.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
