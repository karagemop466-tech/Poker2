#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build data/audit/walking.json - the hotel -> venue walking matrix.

SOURCE PROFILE (this is a published routing service, not an official venue page)
  Every minute figure below was read from a Google Maps walking-directions result
  rendered for these two addresses on 2026-11-17, and the exact URL is stored with
  the row so it can be re-opened and compared. Google publishes no fixed timetable,
  so the figure is a point-in-time estimate from a third-party routing model, not an
  official venue statement. Every row is therefore labelled `third_party_routing` and
  the site never presents it as an official value. See flag FD-08.

  Route requests were made address-to-address, not door-to-door, so the real walk
  inside a large resort (Venetian's poker room is deep inside the property) may be
  longer than the street number. Walking times were NOT adjusted for that.

WHAT WAS DELIBERATELY NOT DONE
  The off-diagonal pairs (e.g. Wynn -> Bellagio) were not queried, so they are absent
  rather than derived by adding two measured legs together. Summing legs would be an
  inference, and this file does not infer.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "audit", "walking.json")
RETRIEVED = "2026-11-17"

VENUE = {
    "id": "VEN-POKER",
    "name": "The Venetian Poker Room",
    "address": "3355 S Las Vegas Blvd, Las Vegas, NV 89109",
    "official_page": "https://www.venetianlasvegas.com/resort/casino/poker.html",
}

HOTELS = {
    "HT-01": dict(name="The Venetian Resort Las Vegas", address="3355 S Las Vegas Blvd, Las Vegas, NV 89109", area="same property"),
    "HT-02": dict(name="The Palazzo at The Venetian", address="3325 S Las Vegas Blvd, Las Vegas, NV 89109", area="same complex"),
    "HT-03": dict(name="Wynn Las Vegas", address="3131 S Las Vegas Blvd, Las Vegas, NV 89109", area="across Sands Ave"),
    "HT-04": dict(name="Bellagio", address="3600 S Las Vegas Blvd, Las Vegas, NV 89109", area="south of Venetian"),
    "HT-05": dict(name="Caesars Palace", address="3570 S Las Vegas Blvd, Las Vegas, NV 89109", area="across the Blvd"),
    "HT-06": dict(name="Horseshoe Las Vegas", address="3645 S Las Vegas Blvd, Las Vegas, NV 89109", area="across the Blvd"),
    "HT-07": dict(name="The Cosmopolitan of Las Vegas", address="3708 S Las Vegas Blvd, Las Vegas, NV 89109", area="further south"),
    "HT-08": dict(name="ARIA Resort & Casino", address="3730 S Las Vegas Blvd, Las Vegas, NV 89158", area="CityCenter"),
    "HT-09": dict(name="MGM Grand", address="3799 S Las Vegas Blvd, Las Vegas, NV 89109", area="Tropicana corner"),
    "HT-10": dict(name="Westgate Las Vegas Resort & Casino", address="3000 Paradise Rd, Las Vegas, NV 89109", area="Convention Center"),
    "HT-11": dict(name="South Point Hotel, Casino & Spa", address="9777 S Las Vegas Blvd, Las Vegas, NV 89183", area="9 miles south"),
}

# minutes, metres, route name exactly as the result panel printed it. None = not queried.
# "google.com/maps/..." URLs are the exact request built for the reading below.
MAPS = "https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=walking"
DEST_Q = "3355+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109"

ROWS = [
    # id, origin_query, minutes, distance_text, route_label
    ("HT-01", "3355+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109", 0, "0", "same address - not routed"),
    ("HT-02", "3325+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109", 7, "0.2 mile", "via unnamed roads"),
    ("HT-03", "3131+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109", 26, "1.1 miles", "via Encore Resort Blvd"),
    ("HT-04", "3600+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109", 26, "1.1 miles", "via Las Vegas Blvd S"),
    ("HT-05", "3570+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109", 25, "1.0 mile", "via Mystere Dreams Ave"),
    ("HT-06", "3645+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109", 24, "1.0 mile", "via Las Vegas Blvd S"),
    ("HT-07", "3708+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109", 33, "1.4 miles", "via Las Vegas Blvd S"),
    ("HT-08", "3730+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109", 42, "1.8 miles", "via Las Vegas Blvd S"),
    ("HT-09", "3799+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89109", 45, "2.0 miles", "via Las Vegas Blvd S"),
    ("HT-10", "3000+Paradise+Rd,+Las+Vegas,+NV+89109", 34, "1.4 miles", "via Convention Center Dr"),
    ("HT-11", "9777+S+Las+Vegas+Blvd,+Las+Vegas,+NV+89183", 185, "8.2 miles", "via Las Vegas Blvd S"),
]


def main():
    rows = []
    for hid, q, mins, dist, route in ROWS:
        h = HOTELS[hid]
        within = None if mins is None else (mins <= 30)
        rows.append({
            "id": "WK-%s" % hid.split("-")[1],
            "hotel_id": hid,
            "hotel": h["name"],
            "hotel_address": h["address"],
            "hotel_area": h["area"],
            "venue_id": VENUE["id"],
            "venue": VENUE["name"],
            "venue_address": VENUE["address"],
            "walk_minutes": mins,
            "distance_text": dist,
            "route_label": route,
            "within_30_min": within,
            "basis": "third_party_routing",
            "source_name": "Google Maps walking directions",
            "source_url": MAPS % (q, DEST_Q) if mins else VENUE["official_page"],
            "retrieved": RETRIEVED,
            "caveat": ("Point-in-time third-party routing estimate between the two street "
                       "addresses; not an official venue statement and not adjusted for the "
                       "distance inside the resort between the street entrance and the poker room."),
        })
    pass_ = [r for r in rows if r["within_30_min"]]
    fail_ = [r for r in rows if r["within_30_min"] is False]
    meta = {
        "as_of": RETRIEVED,
        "venue": VENUE,
        "rule": "A hotel passes only if the published walking time is 30 minutes or less.",
        "method": ("Each pair was requested from maps.google.com as a walking route between the "
                   "two addresses and the minutes figure on the result panel was transcribed. "
                   "The request URL is stored per row."),
        "not_done": ("Off-diagonal hotel-to-hotel pairs were not queried; they are absent rather "
                     "than summed from other legs."),
        "counts": {"queried": len(rows), "within_30": len(pass_), "over_30": len(fail_)},
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "hotels": rows}, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("walk rows:", len(rows), "| within 30 min:", len(pass_), "| over:", len(fail_))
    for r in rows:
        print("  %-6s %-42s %4s min  %-11s %s" % (r["id"], r["hotel"][:42], r["walk_minutes"],
                                                  r["distance_text"], "PASS" if r["within_30_min"] else "FAIL"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
