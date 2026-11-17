#!/usr/bin/env python3
"""Build site-data/schedule.json and site-data/summary-stats.json.

Rules, all derived from published data (nothing is estimated):
  1. A day's PRIMARY event is chosen only from rows classified single_entry_candidate
     (one-day event whose official structure sheet was read and contains no rebuy,
     add-on or re-entry clause) and whose fee AND guarantee are both confirmed,
     and whose official sheet states no entry restriction. Rows whose sheet restricts
     entry (50+, female-only, tag-team) are listed with the restriction instead of
     being scheduled, because the plan must be playable by a general visitor.
  2. Among that day's qualifying events, the primary is the one with the highest
     guarantee/buy-in size ratio that starts before 12:00; if none starts before noon,
     the highest-ratio event of the day becomes the primary.
  3. An evening event is added only as a CONDITIONAL FALLBACK: it is listed only if its
     late-registration cutoff is later than the primary's cutoff, i.e. you can still enter
     it after busting out of the primary. It is never counted as a second full day.
  4. IMPOSSIBLE-SEQUENCE flag: raised when the later event's start is not after the earlier
     event's earliest plausible finish (earliest plausible finish = its own registration
     close + one level, because no payout can be posted while registration is open).
  5. Night-qualification flag for the Venetian poker suite rate: the night qualifies only
     with a $300-or-higher tournament buy-in (or six hours of live cash) per the official
     poker-rate page.
Usage: python3 scripts/build-schedule.py [--check]
"""
import json
import os
import sys
from collections import defaultdict
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EV = os.path.join(ROOT, "site-data", "events.json")
OUT = os.path.join(ROOT, "site-data", "schedule.json")
STATS = os.path.join(ROOT, "site-data", "summary-stats.json")
QUALIFY_MIN = 300


def mins(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)


def fmt(m):
    if m is None:
        return None
    h, mm = divmod(m, 60)
    ap = "AM" if h < 12 else "PM"
    hh = h % 12 or 12
    return f"{hh}:{mm:02d} {ap}"


def demographic_restriction(e):
    """Return the gate text when it actually restricts who can play (age 50+, female-only,
    team composition). The venue-wide "21+, with a Venetian Rewards card" gate is the standard
    requirement for anyone playing at the property and does not restrict an open-to-all trip."""
    el = e.get("eligibility")
    if not el:
        return None
    v = el.get("value") or ""
    if "50+" in v or "emale" in v or v.startswith("Teams"):
        return v
    return None


def main():
    check = "--check" in sys.argv
    d = json.load(open(EV, encoding="utf8"))
    events = d["events"]
    qual = [e for e in events if e["category"] == "single_entry_candidate"
            and e["fee"] is not None and e["gtd"] is not None
            and not demographic_restriction(e)]
    restricted = [e for e in events if e["category"] == "single_entry_candidate"
                  and e["fee"] is not None and e["gtd"] is not None
                  and demographic_restriction(e)]
    by_day = defaultdict(list)
    for e in qual:
        by_day[e["date"]].append(e)
    for k in by_day:
        by_day[k].sort(key=lambda e: (mins(e["start"]), -e["ratio_gtd_to_buyin"]))

    days = {}
    for day, evs in sorted(by_day.items()):
        dayev = [e for e in evs if mins(e["start"]) < 12 * 60]
        primary = max(dayev or evs, key=lambda e: e["ratio_gtd_to_buyin"])
        fallback = None
        flags = []
        for e in evs:
            if e is primary:
                continue
            pf, ef = primary["reg_close"], e["reg_close"]
            if ef and pf and ef > pf:
                fallback = e
                break
        pfin = primary.get("earliest_plausible_finish")
        if fallback:
            if mins(fallback["start"]) <= pfin:
                flags.append({
                    "type": "overlap",
                    "text": (f"{fallback['event_no']} starts {fallback['start']} but {primary['event_no']} "
                             f"cannot plausibly finish before {fmt(pfin)} (its registration closes "
                             f"{primary['reg_close']}). You can only join {fallback['event_no']} during its "
                             f"late registration, which closes {fallback['reg_close']}."),
                })
            open_window = mins(primary["reg_close"]) < mins(fallback["reg_close"])
            flags.append({
                "type": "conditional",
                "text": (f"Fallback entry for {fallback['event_no']} stays open until {fallback['reg_close']}, "
                         f"so a bust out of {primary['event_no']} before then still allows it - mid-level, "
                         "at the blinds of that moment, not from a fresh start."
                         if open_window else
                         f"Fallback {fallback['event_no']} closes registration at {fallback['reg_close']}, which is "
                         f"not after the primary's cutoff ({primary['reg_close']}), so it is not a usable second entry."),
            })
        if primary["buy_in"] < QUALIFY_MIN:
            flags.append({
                "type": "poker_rate",
                "text": (f"A ${primary['buy_in']} buy-in does not satisfy the Venetian poker-rate condition "
                         "(six hours of live cash or a $300+ tournament per night)."),
            })
        days[day] = {
            "date": day,
            "dow": primary["dow"],
            "qualifying_events": len(evs),
            "primary": {
                "id": primary["id"], "event_no": primary["event_no"], "name": primary["name"],
                "start": primary["start"], "buy_in": primary["buy_in"], "gtd": primary["gtd"],
                "fee": primary["fee"], "pool_per_entry": primary["pool_per_entry"],
                "ratio": primary["ratio_gtd_to_buyin"], "reg_close": primary["reg_close"],
                "chips": primary["chips"], "level_min": primary["level_min"],
                "earliest_plausible_finish": fmt(pfin),
                "sheet": primary["sheet"], "sheet_url": primary["sheet_url"],
                "last_checked": primary["last_checked"],
            },
            "fallback": None if not fallback else {
                "id": fallback["id"], "event_no": fallback["event_no"], "name": fallback["name"],
                "start": fallback["start"], "buy_in": fallback["buy_in"], "gtd": fallback["gtd"],
                "ratio": fallback["ratio_gtd_to_buyin"], "reg_close": fallback["reg_close"],
                "sheet": fallback["sheet"], "sheet_url": fallback["sheet_url"],
            },
            "skipped_events": [
                {"event_no": e["event_no"], "start": e["start"], "name": e["name"],
                 "buy_in": e["buy_in"], "gtd": e["gtd"], "ratio": e["ratio_gtd_to_buyin"]}
                for e in evs if e is not primary and e is not fallback
            ] + [
                {"event_no": e["event_no"], "start": e["start"], "name": e["name"],
                 "buy_in": e["buy_in"], "gtd": e["gtd"], "ratio": e["ratio_gtd_to_buyin"],
                 "restricted": e["eligibility"]}
                for e in restricted if e["date"] == day
            ],
            "flags": flags,
        }

    # days in the series with no qualifying primary (so a gap is visible, not silent)
    from datetime import timedelta as _td
    all_series_days = sorted({e["date"] for e in events})
    gap_days = []
    for day in all_series_days:
        if day in days:
            continue
        rows = [e for e in events if e["date"] == day]
        gap_days.append({
            "date": day, "dow": rows[0]["dow"],
            "reason": "no one-day event with both fee and guarantee confirmed on this date",
            "available": [{"event_no": e["event_no"], "start": e["start"], "name": e["name"],
                           "category": e["category"], "buy_in": e["buy_in"], "gtd": e["gtd"]} for e in rows],
        })

    # ---- windows: 4 consecutive calendar days played, 4 nights (depart the following morning) ----
    from datetime import timedelta
    d0 = date.fromisoformat(min(e["date"] for e in events))
    d1 = date.fromisoformat(max(e["date"] for e in events))
    windows = []
    cur = d0
    while cur + timedelta(days=3) <= d1:
        play = [(cur + timedelta(days=k)).isoformat() for k in range(4)]
        if all(p in days for p in play):
            rows = [days[p] for p in play]
            cost = sum(r["primary"]["buy_in"] for r in rows)
            gtd = sum(r["primary"]["gtd"] for r in rows)
            windows.append({
                "arrival": play[0], "departure": (cur + timedelta(days=4)).isoformat(),
                "days": play, "nights": 4, "entries": len(rows),
                "entry_cost": cost, "gtd_played": gtd,
                "avg_ratio": round(sum(r["primary"]["ratio"] for r in rows) / len(rows), 1),
                "poker_rate_eligible_nights": sum(1 for r in rows if r["primary"]["buy_in"] >= QUALIFY_MIN),
                "has_overlap_flag": any(any(f["type"] == "overlap" for f in r["flags"]) for r in rows),
                "fallback_days": sum(1 for r in rows if r["fallback"]),
            })
        cur += timedelta(days=1)
    best_ratio = sorted(windows, key=lambda w: (-w["avg_ratio"], w["entry_cost"]))
    # keep the top distinct windows so narrative pages cite canonical numbers instead of ad-hoc math
    top_windows, seen_days = [], set()
    for w in best_ratio:
        key = tuple(w["days"])
        if key in seen_days:
            continue
        seen_days.add(key)
        top_windows.append(w)
        if len(top_windows) == 4:
            break
    best_poker = [w for w in windows if w["poker_rate_eligible_nights"] == w["entries"]]
    cheapest = sorted(windows, key=lambda w: (w["entry_cost"], -w["avg_ratio"]))
    out = {
        "generated_from": "site-data/events.json",
        "as_of": d["as_of"],
        "rules": [
            "Primary events are drawn only from rows whose official structure sheet was read and whose fee and guarantee are both confirmed.",
            "A primary must be open to all players: rows whose sheet restricts entry (50+, female-only, tag-team) are listed with the restriction, never scheduled as the primary.",
            "Highest published guarantee-to-buy-in size ratio that starts before 12:00 is the day's primary.",
            "An evening event is shown only as a conditional fallback, and only when its late-registration cutoff is later than the primary's.",
            "Overlap is flagged when the later event starts at or before the earlier event's earliest plausible finish (registration close + one level).",
            "Night-eligibility uses the official poker-rate condition: $300+ tournament buy-in or six hours of live cash per night.",
            "Finish times are not published anywhere: the 'earliest plausible finish' column is a derived clock value, not a schedule.",
        ],
        "earliest_start_in_series": min(e["start"] for e in events),
        "earliest_day_start": min(e["start"] for e in events if e["kind"] == "DAY"),
        "days": days,
        "gap_days": gap_days,
        "windows": {
            "best_size_ratio": best_ratio[:3],
            "best_poker_rate_compatible": sorted(best_poker, key=lambda w: (-w["avg_ratio"], w["entry_cost"]))[:3],
            "cheapest_entries": cheapest[:3],
        },
    }
    txt = json.dumps(out, indent=1, ensure_ascii=False) + "\n"
    if check:
        cur = open(OUT, encoding="utf8").read() if os.path.exists(OUT) else ""
        if cur.strip() != txt.strip():
            raise SystemExit("site-data/schedule.json is stale; run scripts/build-schedule.py")
    else:
        open(OUT, "w", encoding="utf8").write(txt)

    cats = defaultdict(int)
    for e in events:
        cats[e["category"]] += 1
    stats = {
        "as_of": d["as_of"],
        "rows_total": len(events),
        "days_with_qualifying_event": len(days),
        "categories": dict(cats),
        "sheets_read": len({e["sheet"] for e in events if e["sheet_read"]}),
        "sheets_published": len({e["sheet"] for e in events}),
        "qualifying_rows": len(qual),
        "restricted_single_entry_rows": len(restricted),
        "spend_advantage_rows": cats["spend_advantage"] + len([e for e in events if e["category"] == "multi_flight"]),
        "cheapest_qualifying_entry": min(e["buy_in"] for e in qual),
        "highest_ratio": max(qual, key=lambda e: e["ratio_gtd_to_buyin"])["ratio_gtd_to_buyin"],
        "highest_ratio_event": max(qual, key=lambda e: e["ratio_gtd_to_buyin"])["name"],
        "earliest_day_start": min(e["start"] for e in events if e["kind"] == "DAY"),
        "series_start": min(e["date"] for e in events),
        "series_end": max(e["date"] for e in events),
        "best_poker_window": (sorted(best_poker, key=lambda w: (-w["avg_ratio"], w["entry_cost"])) or [None])[0],
        "best_ratio_window": (best_ratio or [None])[0],
        "cheapest_window": (cheapest or [None])[0],
        "top_windows": top_windows,
    }
    stxt = json.dumps(stats, indent=1, ensure_ascii=False) + "\n"
    if check:
        cur = open(STATS, encoding="utf8").read() if os.path.exists(STATS) else ""
        if cur.strip() != stxt.strip():
            raise SystemExit("site-data/summary-stats.json is stale; run scripts/build-schedule.py")
        print("schedule + stats up to date")
        return
    open(STATS, "w", encoding="utf8").write(stxt)
    print(f"wrote schedule for {len(days)} days; {len(windows)} four-day windows; "
          f"{len(best_poker)} poker-rate-compatible windows")


if __name__ == "__main__":
    main()
