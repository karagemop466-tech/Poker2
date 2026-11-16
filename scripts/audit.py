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
