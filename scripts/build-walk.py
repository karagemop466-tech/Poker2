#!/usr/bin/env python3
"""Regenerate site-data/walk.json: hotel -> poker-room walking pairs with routed minutes.

Two inputs, both already committed and both traceable:

  1. data/site/walking.json - the routed matrix built by an earlier session. Official hotel
     and poker-room addresses were geocoded with OpenStreetMap Nominatim and routed with the
     OSRM foot profile (routing.openstreetmap.de/routed-foot). It gives, for each
     hotel x poker-room pair, `walk_min` (a routed walking estimate), the pair of addresses
     used, and a prefilled Google Maps directions link.
  2. site-data/walk.json - this surface's own pair list, which additionally carries the
     verbatim OFFICIAL interior-route descriptions (Venetian -> Palazzo level 2, Bellagio ->
     Cosmopolitan bridge) that no router can produce.

This script merges them. It never invents a duration: a pair with no routed row keeps
minutes = null and stays out of the <= 30 minute filter, which is the honest outcome.

Usage: python3 scripts/build-walk.py [--check]
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTED = os.path.join(ROOT, "data", "site", "walking.json")
HOTELS = os.path.join(ROOT, "site-data", "hotels.json")
VENUES = os.path.join(ROOT, "site-data", "venues.json")
OUT = os.path.join(ROOT, "site-data", "walk.json")
AS_OF = "2026-11-17"
ROUTE_TEXT_DATE = "2026-11-16"   # when the official interior-route wording was captured
LIMIT_MIN = 30

# site-data hotel id -> id used in the routed matrix
HOTEL_MAP = {
    "H-VEN": "H-VEN", "H-PAL": "H-PAL", "H-WYN": "H-WYN", "H-PMGM": "H-PMG",
    "H-ARIA": "H-ARI", "H-BEL": "H-BEL", "H-CAES": "H-CP", "H-PARIS": "H-PAR",
    "H-HORSE": "H-HS",
    # H-COSMO has no row in the routed matrix - it keeps minutes = null.
}
# site-data venue id -> id used in the routed matrix.
# `aria` and `goldennugget` have no routed destination, so they stay null.
VENUE_MAP = {
    "venetian": "V-VEN", "wynn": "V-WYN", "caesars": "V-CP",
    "mgm": "V-MGM", "bellagio": "V-BEL",
}
# Human label for each venue, used in the Google/Apple confirmation links.
VENUE_LABEL = {
    "venetian": "The Venetian Poker Room", "wynn": "Wynn Las Vegas Poker Room",
    "caesars": "Caesars Palace Poker Room", "mgm": "MGM Grand Poker Room",
    "bellagio": "Bellagio Poker Room", "aria": "ARIA Poker Room",
    "goldennugget": "Golden Nugget Poker Room",
}
ROUTE_METHOD = (
    "Official hotel and poker-room addresses were geocoded with OpenStreetMap Nominatim and "
    "routed with the OSRM foot profile (routing.openstreetmap.de/routed-foot) on 2026-11-16, "
    "by the session that produced data/site/walking.json. A routed duration is an estimate at "
    "a typical walking pace - it is NOT a Google or Apple Maps measurement, and it does not "
    "include time spent inside a casino, at crossings, or waiting for a lift. Every row carries "
    "a prefilled Google Maps and Apple Maps directions link so you can confirm the pair "
    "yourself in one tap."
)

STATUS_LABELS = {
    "connected_indoor_same_building": "Poker room is in this building (official route description)",
    "connected_indoor_same_resort": "Indoor route inside the same resort (official route description)",
    "connected_indoor": "Published interior walkway between the two properties",
    "same_property_no_duration": "Same property; minutes not published",
    "routed_estimate": "Routed walking estimate, not a measured duration - confirm with the map link",
    "no_verified_duration": "No duration available from an official or map-provider source",
}


def gmaps(origin, dest):
    return ("https://www.google.com/maps/dir/?api=1&travelmode=walking&origin="
            + origin.replace(" ", "+") + "&destination=" + dest.replace(" ", "+"))


def amaps(origin, dest):
    return ("https://maps.apple.com/?dirflg=w&saddr=" + origin.replace(" ", "+")
            + "&daddr=" + dest.replace(" ", "+"))


def main():
    routed = json.load(open(ROUTED, encoding="utf8"))
    hotels = json.load(open(HOTELS, encoding="utf8"))["hotels"]
    venues = json.load(open(VENUES, encoding="utf8"))["venues"]
    by_pair = {}
    for r in routed["rows"]:
        by_pair[(r["hotel_id"], r["venue_id"])] = r

    # official interior-route text already captured on this surface, keyed hotel+venue
    official = {}
    if os.path.exists(OUT):
        for p in json.load(open(OUT, encoding="utf8")).get("pairs", []):
            if p.get("route_official"):
                official[(p["hotel_id"], p["venue"])] = p
            if p.get("hotel_address_official"):
                official.setdefault(("addr", p["hotel_id"]), p["hotel_address_official"])

    pairs = []
    n = 0
    for h in hotels:
        hid = h["id"]
        rh = HOTEL_MAP.get(hid)
        for v in venues:
            vid = v["id"]
            rv = VENUE_MAP.get(vid)
            row = by_pair.get((rh, rv)) if (rh and rv) else None
            n += 1
            prev = official.get((hid, vid))
            label = v["name"]
            dest = VENUE_LABEL.get(vid, label)
            mins = row["walk_min"] if row else None
            if row and mins is not None:
                status = "routed_estimate"
            elif prev and prev.get("status", "").startswith("connected"):
                status = prev["status"]
            elif prev and prev.get("status") == "same_property_no_duration":
                status = "same_property_no_duration"
            else:
                status = "no_verified_duration"
            p = {
                "id": "W-%d" % n,
                "hotel_id": hid,
                "hotel": h["property"],
                "venue": vid,
                "venue_label": label,
                "destination_label": dest,
                "minutes_verified": None if mins is None else round(float(mins), 1),
                "minutes_kind": ("routed_estimate" if mins is not None else None),
                "distance_verified": None,
                "within_30_min": (round(float(mins), 1) <= LIMIT_MIN) if mins is not None else None,
                "hotel_address_official": (prev.get("hotel_address_official") if prev else None)
                                          or (row["hotel_address"] if row else None),
                "venue_address_official": (row["venue_address"] if row else None),
                "route_official": prev.get("route_official") if prev else None,
                "route_source": prev.get("route_source") if prev else None,
                "route_retrieved": (prev.get("route_retrieved") if prev else None) or ROUTE_TEXT_DATE,
                "status": status,
                "google_maps": (row["gmaps_link"] if row and row.get("gmaps_link")
                                else gmaps(h["property"], dest)),
                "apple_maps": amaps(h["property"], dest),
                "routed_source": ("data/site/walking.json" if row else None),
                "retrieved": AS_OF if row else None,
            }
            pairs.append(p)

    payload = {
        "as_of": AS_OF,
        "rule": ("A pair passes the 30-minute test only when a duration exists for it. "
                 "Durations are routed estimates (see `method`), so the filter is a "
                 "shortlist, not a guarantee."),
        "method": ROUTE_METHOD,
        "limit_min": LIMIT_MIN,
        "counts": {
            "pairs": len(pairs),
            "with_routed_minutes": sum(1 for p in pairs if p["minutes_verified"] is not None),
            "within_30_min": sum(1 for p in pairs if p["within_30_min"]),
            "no_duration": sum(1 for p in pairs if p["minutes_verified"] is None),
        },
        "pairs": pairs,
        "status_labels": STATUS_LABELS,
    }

    txt = json.dumps(payload, indent=1, ensure_ascii=False)
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf8").read() if os.path.exists(OUT) else ""
        if cur.strip() != txt.strip():
            raise SystemExit("site-data/walk.json is stale; run python3 scripts/build-walk.py")
        print("walk.json up to date (%d pairs, %d with routed minutes)"
              % (len(pairs), payload["counts"]["with_routed_minutes"]))
        return
    with open(OUT, "w", encoding="utf8") as fh:
        fh.write(txt + "\n")
    print("wrote %d pairs -> site-data/walk.json (%d with routed minutes, %d within %d min)"
          % (len(pairs), payload["counts"]["with_routed_minutes"],
             payload["counts"]["within_30_min"], LIMIT_MIN))


if __name__ == "__main__":
    main()
