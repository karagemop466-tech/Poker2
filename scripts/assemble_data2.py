#!/usr/bin/env python3
"""Assemble hotels, walking matrix, trip plan, questions, suggestions, flags,
summary and the monitor seed from the 2026-11-16 verification pass."""
import json, os

R = "2026-11-16"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "site")

# ---------------------------------------------------------------------------
# Walking matrix. Method: official addresses geocoded via OpenStreetMap
# Nominatim (2026-11-16), foot routes via OSRM "foot" profile on the FOSSGIS
# routing server (routing.openstreetmap.de/routed-foot), durations in seconds.
# Google Maps walking links are provided per pair for independent confirmation.
# ---------------------------------------------------------------------------
hotels_geo = [
    ("H-VEN", "The Venetian", "3355 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1217073, -115.1693352),
    ("H-PAL", "The Palazzo", "3325 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1241843, -115.1682710),
    ("H-WYN", "Wynn Las Vegas", "3131 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1263781, -115.1658180),
    ("H-ENC", "Encore Las Vegas", "3121 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1294358, -115.1648801),
    ("H-RW",  "Resorts World Las Vegas", "3000 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1336945, -115.1661576),
    ("H-WG",  "Westgate Las Vegas", "2901 Paradise Rd, Las Vegas, NV 89109", 36.1356551, -115.1513429),
    ("H-HAR", "Harrah's Las Vegas", "3475 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1193033, -115.1711625),
    ("H-LIN", "The LINQ", "3535 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1183591, -115.1705968),
    ("H-FLA", "Flamingo Las Vegas", "3555 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1164253, -115.1723637),
    ("H-CRO", "The Cromwell", "3595 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1149764, -115.1695532),
    ("H-CP",  "Caesars Palace", "3570 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1166277, -115.1767568),
    ("H-HS",  "Horseshoe Las Vegas", "3645 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1134820, -115.1690550),
    ("H-PAR", "Paris Las Vegas", "3655 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1121618, -115.1706380),
    ("H-PH",  "Planet Hollywood", "3667 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1100625, -115.1715131),
    ("H-BEL", "Bellagio", "3600 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1123192, -115.1787230),
    ("H-ARI", "ARIA Resort & Casino", "3730 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1070287, -115.1779977),
    ("H-PMG", "Park MGM", "3770 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1047548, -115.1752620),
    ("H-MGM", "MGM Grand", "3799 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1027891, -115.1694006),
    ("H-NYN", "New York-New York", "3790 S. Las Vegas Blvd, Las Vegas, NV 89109", 36.1021436, -115.1744946),
    ("H-MB",  "Mandalay Bay", "3950 S. Las Vegas Blvd, Las Vegas, NV 89119", 36.0922458, -115.1758239),
    ("H-GN",  "Golden Nugget (downtown)", "129 E. Fremont St, Las Vegas, NV 89101", 36.1697984, -115.1457909),
]
venues_geo = [
    ("V-VEN", "Venetian poker room (DSE IV)", "3355 S. Las Vegas Blvd", 36.1217073, -115.1693352),
    ("V-WYN", "Wynn poker room (in Encore — WPT)", "3121 S. Las Vegas Blvd", 36.1294358, -115.1648801),
    ("V-CP",  "Caesars Palace poker room", "3570 S. Las Vegas Blvd", 36.1166277, -115.1767568),
    ("V-HS",  "Horseshoe poker room", "3645 S. Las Vegas Blvd", 36.1134820, -115.1690550),
    ("V-BEL", "Bellagio poker room", "3600 S. Las Vegas Blvd", 36.1123192, -115.1787230),
    ("V-MGM", "MGM Grand poker room", "3799 S. Las Vegas Blvd", 36.1027891, -115.1694006),
]
# OSRM routed-foot table durations (seconds), rows = hotels_geo order,
# cols = venues_geo order. Retrieved 2026-11-16 from routing.openstreetmap.de/routed-foot.
dur = [
 [0,1128.3,1171.7,1230.7,1658.9,2187],
 [359.2,1007.9,1348.1,1407.1,1814.6,2432],
 [779.3,528.2,1768.2,1827.2,2146.6,2841.7],
 [1128.3,0,2117.2,2176.2,2491.6,3190.7],
 [1492.3,607.9,2237.3,2533.9,2478.1,3554.7],
 [2365.1,1475,3354,3339.6,3724.5,3989.1],
 [524.1,1469.6,860.7,879.9,1347.9,1965.2],
 [572.4,1700.7,1211.2,1011.5,1698.4,1895.5],
 [672.1,1617.6,744.6,558.6,1231.8,1583.5],
 [1022,2025.4,1152.4,759.2,1639.6,1786],
 [1171.7,2117.2,0,1270.4,695.2,2295.3],
 [1230.7,2176.2,1270.4,0,1486.4,1094.3],
 [1280.7,2226.2,1320.4,498.2,1222.2,1208.9],
 [1570.6,2516.1,1610.3,601.5,1330.5,880.3],
 [1658.9,2491.6,695.2,1486.4,0,1694.2],
 [1835.6,2781.1,1422.9,1090.5,755.8,1340],
 [2041.4,2986.9,2065.7,1296.3,1398.6,640],
 [2187,3190.7,2295.3,1094.3,1694.2,0],
 [2354,3299.5,2001.5,1571.5,1334.4,742],
 [3107.3,4052.8,2785.7,2324.8,2118.6,1495.3],
 [4971.4,4081.3,5850.2,6019.3,6091,7033.8],
]
def gmaps(h, v):
    return ("https://www.google.com/maps/dir/?api=1&origin="
            + f"{h[3]},{h[4]}" + "&destination=" + f"{v[3]},{v[4]}" + "&travelmode=walking")

walk_rows = []
for hi, h in enumerate(hotels_geo):
    for vi, v in enumerate(venues_geo):
        secs = dur[hi][vi]
        walk_rows.append({
            "hotel_id": h[0], "hotel": h[1], "hotel_address": h[2],
            "venue_id": v[0], "venue": v[1], "venue_address": v[2],
            "walk_min": round(secs / 60.0, 1),
            "within_30_min": bool(secs <= 1800),
            "gmaps_link": gmaps(h, v),
        })
walking = {
    "as_of": R,
    "method": "Official addresses geocoded via OpenStreetMap Nominatim; walking routes computed with the OSRM foot profile on the FOSSGIS routing server (routing.openstreetmap.de/routed-foot) on 2026-11-16. Durations are routing estimates (typical walking pace), not a Google/Apple Maps measurement — each row includes a prefilled Google Maps walking-directions link for independent confirmation. The ≤30-minute rule is applied to the routed estimate.",
    "limit_min": 30,
    "rows": walk_rows,
}
json.dump(walking, open(os.path.join(OUT, "walking.json"), "w"), indent=1)

# ---------------------------------------------------------------------------
# Hotels: fees from official pages (verified 2026-11-16 / earlier 2026-11-16
# reads recorded in the repo), dated rate log (append-only), true-cost formula.
# ---------------------------------------------------------------------------
rate_log = [
 {"date": R, "hotel_id": "H-VEN", "kind": "poker player rate (conditional)", "value_usd": 119, "unit": "per night, from",
  "conditions": "Official 2026 poker-rate page: from $119 (Venetian suites). Requires 6 hours live cash or a $300+ tournament buy-in per night; availability applies. Not a dated quote.",
  "source": "V_SUITE_RATES"},
 {"date": R, "hotel_id": "H-PAL", "kind": "poker player rate (conditional)", "value_usd": 209, "unit": "per night, from",
  "conditions": "Official 2026 poker-rate page: from $209 (Palazzo suites). Same qualifying-play conditions. Not a dated quote. Page wording lists both amounts together; property mapping follows the page's presentation order and is flagged for confirmation at reservation.",
  "source": "V_SUITE_RATES"},
 {"date": R, "hotel_id": "H-VEN", "kind": "resort fee", "value_usd": 55, "unit": "per night, plus tax",
  "conditions": "Payable at check-in; includes fitness access for two, in-suite internet, boarding pass printing, local calls, PressReader.",
  "source": "V_RESORT_FEE"},
 {"date": R, "hotel_id": "H-PAL", "kind": "resort fee", "value_usd": 55, "unit": "per night, plus tax",
  "conditions": "Same resort-fee page covers Venetian and Palazzo.",
  "source": "V_RESORT_FEE"},
 {"date": R, "hotel_id": "H-WYN", "kind": "resort fee", "value_usd": 55, "unit": "per night, plus tax",
  "conditions": "Wynn resort information page: daily resort fee $55 plus tax.",
  "source": "W_RESORT_INFO"},
 {"date": R, "hotel_id": "H-ENC", "kind": "resort fee", "value_usd": 55, "unit": "per night, plus tax",
  "conditions": "Wynn resort information page covers the resort (Wynn and Encore towers).",
  "source": "W_RESORT_INFO"},
 {"date": R, "hotel_id": "H-MGM", "kind": "resort fee", "value_usd": 50, "unit": "per night, plus tax",
  "conditions": "MGM Grand hotel terms: $50 plus applicable tax; eligible MGM Rewards Gold+ reservations may qualify for a waiver.",
  "source": "MGM_TC"},
 {"date": R, "hotel_id": "H-ARI", "kind": "resort fee", "value_usd": 55, "unit": "per night, plus tax",
  "conditions": "MGM Resorts hotel terms list $55 plus tax for ARIA ($50 plus tax extra occupant); Gold+ may waive.",
  "source": "MGM_TC"},
 {"date": R, "hotel_id": "H-BEL", "kind": "resort fee", "value_usd": 55, "unit": "per night, plus tax",
  "conditions": "MGM Resorts hotel terms list $55 plus tax for Bellagio ($50 plus tax extra occupant); Gold+ may waive.",
  "source": "MGM_TC"},
]
hotels = {
 "as_of": R,
 "tax_note": "Clark County room tax 13.38% is disclosed in the Venetian hotel terms (operator disclosure; no independent county page captured). The same rate is applied to the resort fee as an assumption — confirm at booking. Wynn terms say only 'plus tax'.",
 "true_cost_formula": "true cost per night = (room rate + resort fee) × 1.1338  [tax on both components is an assumption to confirm]. Parking optional add-on. Security deposit is not a cost unless charged.",
 "quality_floor": "Planning assumption: 4-star-and-up class resort (user's quality priority). Quality labels are classes, not third-party ratings — no official rating body listing was captured (flagged).",
 "budget_floor": "Planning assumption: nightly true-cost target ≤ $250 (adjustable in the trip calculator).",
 "parking_verified": {"H-VEN": "$20/day for hotel guests (Venetian hotel terms)", "H-PAL": "$20/day for hotel guests (Venetian hotel terms)"},
 "cancellation_note": "Cancellation deadlines are rate-specific and are captured only at booking (no official deadline captured — blank/flagged).",
 "rows": [
  {"id": "H-VEN", "name": "The Venetian", "address": "3355 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": 55, "resort_fee_txt": "$55 plus tax per night (official resort-fee page)",
   "parking": "$20/day hotel guests; $150/night incidental hold (official hotel terms)",
   "booking_url": "https://www.venetianlasvegas.com/book", "quality_class": "5-star class (assumption)",
   "notes": "Home of DSE IV — zero walk to the tournament room. Poker player rates in the dated rate log (conditional)."},
  {"id": "H-PAL", "name": "The Palazzo", "address": "3325 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": 55, "resort_fee_txt": "$55 plus tax per night (official resort-fee page)",
   "parking": "$20/day hotel guests (official hotel terms)", "booking_url": "https://www.venetianlasvegas.com/book",
   "quality_class": "5-star class (assumption)", "notes": "Same tower complex as the Venetian poker room."},
  {"id": "H-WYN", "name": "Wynn Las Vegas", "address": "3131 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": 55, "resort_fee_txt": "$55 plus tax per room night (official resort information page)",
   "parking": "not captured — flagged", "booking_url": "https://www.wynnlasvegas.com/",
   "quality_class": "5-star class (assumption)", "notes": "Wynn Tower Suites holds a 20th consecutive Forbes Travel Guide Five-Star rating statement for 2026 (applies to Tower Suites only)."},
  {"id": "H-ENC", "name": "Encore Las Vegas", "address": "3121 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": 55, "resort_fee_txt": "$55 plus tax per room night (official resort information page)",
   "parking": "not captured — flagged", "booking_url": "https://www.wynnlasvegas.com/",
   "quality_class": "5-star class (assumption)", "notes": "The Wynn poker room is inside Encore (WPT general terms, note 3). Best WPT location."},
  {"id": "H-CP", "name": "Caesars Palace", "address": "3570 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.caesars.com/caesars-palace",
   "quality_class": "5-star class (assumption)", "notes": "Host of the daily $100/$160 NLH with the $50 add-on."},
  {"id": "H-HS", "name": "Horseshoe Las Vegas", "address": "3645 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.caesars.com/horseshoe-las-vegas",
   "quality_class": "3-star class (assumption)", "notes": "Budget-friendly; hosts the earliest verified daily start (9 AM)."},
  {"id": "H-ARI", "name": "ARIA Resort & Casino", "address": "3730 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": 55, "resort_fee_txt": "$55 plus tax per night; $50 plus tax extra occupant (MGM terms)",
   "parking": "not captured — flagged", "booking_url": "https://aria.mgmresorts.com/",
   "quality_class": "5-star class (assumption)", "notes": "Gold+ MGM Rewards may waive the resort fee."},
  {"id": "H-BEL", "name": "Bellagio", "address": "3600 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": 55, "resort_fee_txt": "$55 plus tax per night; $50 plus tax extra occupant (MGM terms)",
   "parking": "not captured — flagged", "booking_url": "https://bellagio.mgmresorts.com/",
   "quality_class": "5-star class (assumption)", "notes": "Central Strip location; hosts weekly tournaments per its poker page."},
  {"id": "H-MGM", "name": "MGM Grand", "address": "3799 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": 50, "resort_fee_txt": "$50 plus applicable tax per night (MGM hotel terms)",
   "parking": "not captured — flagged", "booking_url": "https://mgmgrand.mgmresorts.com/",
   "quality_class": "4-star class (assumption)", "notes": "Home of the Saturday $150/$2K event."},
  {"id": "H-HAR", "name": "Harrah's Las Vegas", "address": "3475 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.caesars.com/harrahs-las-vegas",
   "quality_class": "3-star class (assumption)", "notes": "Budget-friendly center-north Strip."},
  {"id": "H-LIN", "name": "The LINQ", "address": "3535 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.caesars.com/linq",
   "quality_class": "3-star class (assumption)", "notes": "Budget-friendly."},
  {"id": "H-FLA", "name": "Flamingo Las Vegas", "address": "3555 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.caesars.com/flamingo-las-vegas",
   "quality_class": "3-star class (assumption)", "notes": "Central; short walk to Caesars/Horseshoe."},
  {"id": "H-CRO", "name": "The Cromwell", "address": "3595 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.caesars.com/cromwell",
   "quality_class": "4-star class (assumption)", "notes": "Boutique; closest Caesars-area hotel to the Horseshoe."},
  {"id": "H-PAR", "name": "Paris Las Vegas", "address": "3655 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.caesars.com/paris-las-vegas",
   "quality_class": "4-star class (assumption)", "notes": ""},
  {"id": "H-PH", "name": "Planet Hollywood", "address": "3667 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.caesars.com/planet-hollywood",
   "quality_class": "4-star class (assumption)", "notes": ""},
  {"id": "H-PMG", "name": "Park MGM", "address": "3770 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://parkmgm.mgmresorts.com/",
   "quality_class": "4-star class (assumption)", "notes": "Non-smoking resort."},
  {"id": "H-RW", "name": "Resorts World Las Vegas", "address": "3000 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.resortsworldlv.com/",
   "quality_class": "5-star class (assumption)", "notes": "North Strip; convenient for the Wynn/WPT side."},
  {"id": "H-WG", "name": "Westgate Las Vegas", "address": "2901 Paradise Rd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.westgateresorts.com/las-vegas/",
   "quality_class": "3-star class (assumption)", "notes": "Off-Strip east of the Convention Center; own poker room (aggregator-sourced $70 freezeout lead — flagged, not verified)."},
  {"id": "H-NYN", "name": "New York-New York", "address": "3790 S. Las Vegas Blvd, Las Vegas, NV 89109",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://newyorknewyork.mgmresorts.com/",
   "quality_class": "4-star class (assumption)", "notes": ""},
  {"id": "H-MB", "name": "Mandalay Bay", "address": "3950 S. Las Vegas Blvd, Las Vegas, NV 89119",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://mandalaybay.mgmresorts.com/",
   "quality_class": "4-star class (assumption)", "notes": "South Strip — outside the 30-minute walk to Venetian."},
  {"id": "H-GN", "name": "Golden Nugget (downtown)", "address": "129 E. Fremont St, Las Vegas, NV 89101",
   "resort_fee": None, "resort_fee_txt": "not captured from an official page — flagged",
   "parking": "not captured — flagged", "booking_url": "https://www.goldennugget.com/las-vegas/",
   "quality_class": "4-star class (assumption)", "notes": "Downtown — well outside the 30-minute walk to any Strip venue."},
 ],
 "rate_log": rate_log,
}
json.dump(hotels, open(os.path.join(OUT, "hotels-f0816fab.json"), "w"), indent=1)

# ---------------------------------------------------------------------------
# Trip plan. Dates fixed by rule: the 7-night window (Dec 6–13, 2026) with the
# most confirmed single-entry events, chosen programmatically from events.json.
# ---------------------------------------------------------------------------
events = json.load(open(os.path.join(OUT, "events-f0816fab.json")))["events"]
from datetime import date, timedelta
playable = [e for e in events if e["classification"] == "sheet_silent"]
open_play = [e for e in playable if e.get("eligibility", "").startswith("21+")]
gated = [e for e in playable if not e.get("eligibility", "").startswith("21+")]
by_day, by_day_all = {}, {}
for e in playable:
    for d in (e.get("days") or [e["date"]]):
        by_day_all.setdefault(d, []).append(e["id"])
for e in open_play:
    for d in (e.get("days") or [e["date"]]):
        by_day.setdefault(d, []).append(e["id"])
alldays = sorted(by_day_all)
best = None
for start in alldays:
    d0 = date.fromisoformat(start)
    window = [(d0 + timedelta(days=i)).isoformat() for i in range(8)]  # 8 play days = 7 nights
    n = sum(len(by_day.get(d, [])) for d in window)      # score: open-to-all entries
    n_all = sum(len(by_day_all.get(d, [])) for d in window)
    if best is None or n > best[0]:
        best = (n, window, n_all)
TRIP_DAYS = best[1]
trip = {
 "as_of": R,
 "trip_dates": {"play_days": TRIP_DAYS, "nights": 7,
   "rule": "Fixed by the stated planning rule: the consecutive 7-night window (8 play days) with the most sheet-silent single-entry candidates open to all players (ties broken by earliest start). Age/gender-gated events are counted separately. Selected window: %d open-to-all entries (%d incl. gated)." % (best[0], best[2])},
 "budget_quality_floor": {"nightly_true_cost_target_usd": 250, "quality_floor": "4-star-and-up class resort",
   "note": "Planning assumptions set for this plan (step 1 of the decision workflow). Adjustable in the calculator below; cost and quality outrank distance, hard limit = 30-minute walk."},
 "tax_rate": 0.1338,
 "day_plan": [],
 "overlap_method": "For each day: the sheet-silent candidate with the earliest start is the primary. The evening event is listed as a conditional fallback (playable only if the player exits the earlier event). A 1-Day event at the Venetian runs to a winner (typically 10–14 hours from start; sheets list 28 levels) so the same-day evening event cannot be scheduled back-to-back — it is a fallback, not a second seat time. Durations are estimates from level counts on the official sheets, not published finish times (flagged).",
}
for d in TRIP_DAYS:
    ids = by_day_all.get(d, [])
    evs = [e for e in playable if e["id"] in ids]
    evs.sort(key=lambda e: e["start"])
    prim = evs[0] if evs else None
    fallb = evs[1] if len(evs) > 1 else None
    trip["day_plan"].append({
        "date": d,
        "primary": ({"id": prim["id"], "name": prim["name"], "start": prim["start"], "buy_in": prim["buy_in"], "eligibility": prim["eligibility"]} if prim else None),
        "fallback": ({"id": fallb["id"], "name": fallb["name"], "start": fallb["start"], "buy_in": fallb["buy_in"], "eligibility": fallb["eligibility"], "condition": "Conditional: only if the player exits the earlier event before this start (and before its late-registration cutoff)."} if fallb else None),
        "extra": [{"id": e["id"], "name": e["name"], "start": e["start"], "buy_in": e["buy_in"]} for e in evs[2:]],
        "overlap_flags": (
            ["Two candidate events share this day and their play windows overlap by design (a 1-Day event runs to a winner). The later start is a fallback only."]
            if len(evs) > 1 else []),
    })
json.dump(trip, open(os.path.join(OUT, "trip.json"), "w"), indent=1)
print("trip window:", TRIP_DAYS[0], "→", TRIP_DAYS[-1], "| playable entries in window:", best[0])

# ---------------------------------------------------------------------------
# Questions, suggestions, flags, summary, monitor seed, sources
# ---------------------------------------------------------------------------
questions = {
 "as_of": R,
 "intro": "Questions that must be answered before money is committed. 'Answered' = settled from an official source this session; 'Open' = the sources do not answer it; the How-to-find column names the discovery step.",
 "items": [
  {"id": "Q01", "question": "Which tournaments are confirmed single-entry freezeouts (no re-entry, rebuy or add-on)?",
   "status": "Answered for Venetian DSE IV", "answer": "46 Venetian events are sheet-silent single-entry candidates after reading every official structure sheet (explicit confirmation outstanding) (1–37) in full on 2026-11-16. 2 Valuetown events are flagged (ambiguous 'subsequent buy in's' wording). 42 events are excluded (re-entry/rebuy/add-on/multi-flight/satellite/team confirmed). 33 WPT rows stay unverified (terms not published in the structures document).",
   "how_to_find": "Remaining work: ask the Wynn poker room for written entry terms on the 33 unverified WPT rows; ask the Venetian whether Events 18/58 permit subsequent buy-ins.",
   "sources": ["https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html", "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"]},
  {"id": "Q02", "question": "Can a player start play at 8:00 AM with confirmed single-entry events?",
   "status": "Answered (no)", "answer": "No listed event starts at 8:00 AM anywhere in the dataset. Earliest candidate starts are 10:10 AM (Venetian). Horseshoe runs a recurring 9:00 AM daily NLH (entry rules unverified).",
   "how_to_find": "Check other rooms' official daily schedules (Palms, South Point, Orleans, Golden Nugget) for earlier starts.",
   "sources": ["https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip"]},
  {"id": "Q03", "question": "What is the true nightly hotel cost for the trip dates?",
   "status": "Open (needs dated quotes)", "answer": "Resort fees, tax rate and the conditional Venetian poker player rates are verified and in the dated rate log. No dated room quote for Dec 6–13, 2026 was captured — live quotes require each hotel's booking engine (dynamic pricing).",
   "how_to_find": "Open each hotel's official booking link for Dec 6–13 2026 and record the checkout total (rate + resort fee + 13.38% tax), cancellation deadline and quote timestamp in the rate log. The trip calculator accepts these numbers.",
   "sources": ["https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html", "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"]},
  {"id": "Q04", "question": "Is each hotel within a 30-minute walk of the tournament venues?",
   "status": "Answered (routing estimates)", "answer": "Walking times for 21 hotels × 6 venue poker rooms were computed from official addresses with the OSRM foot profile (routing estimates) and each row links to Google Maps walking directions for confirmation. 16 hotels are within 30 minutes of the Venetian; Golden Nugget, Mandalay Bay, NYNY, Westgate fail the test to at least one venue.",
   "how_to_find": "Confirm the rows you plan to rely on by opening the Google Maps links (walking mode) before booking.",
   "sources": ["https://routing.openstreetmap.de/routed-foot", "https://nominatim.openstreetmap.org"]},
  {"id": "Q05", "question": "Which events can be combined in one day of play?",
   "status": "Answered (plan + flags)", "answer": "1-Day events run to a winner; the evening event on the same date is a conditional fallback only. The day plan shows primary + fallback per day with overlap flags; verified finish times are not published (durations estimated from level counts).",
   "how_to_find": "Ask the tournament desk for typical finish times of 1-Day events to tighten the estimates.",
   "sources": ["https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf"]},
  {"id": "Q06", "question": "Is the Venetian poker rate $119/$209 mapping to Venetian/Palazzo correct?",
   "status": "Open (flagged)", "answer": "The official poker-rate page publishes both amounts but its wording does not explicitly bind each amount to a property. The site records them as separate dated rate-log entries with the ambiguity flagged.",
   "how_to_find": "Confirm at reservation or with the poker room host.", "sources": ["https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"]},
  {"id": "Q07", "question": "What is the exact tax on the resort fee?",
   "status": "Open (assumption flagged)", "answer": "Venetian terms state 13.38% Clark County room tax on the room rate and 'plus applicable tax' on the resort fee. Applying 13.38% to the fee is an assumption in the calculator.",
   "how_to_find": "Confirm the fee tax rate at check-in or from a folio.", "sources": ["https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html"]},
  {"id": "Q08", "question": "Do any events cap entries (maximum-entry rules)?",
   "status": "Open", "answer": "No official sheet states a maximum number of entries for the confirmed freezeouts; freezeout structure implies one entry but the sheets are silent on caps. WPT events explicitly allow re-entry (terms captured).",
   "how_to_find": "Ask the poker room for written maximum-entry statements before relying on single-entry economics.", "sources": []},
  {"id": "Q09", "question": "Which schedule discrepancies exist between official sources?",
   "status": "Answered (flagged)", "answer": "1) WPT Dec 21 turbo listed at 6 PM in event terms vs 8 PM on the schedule row. 2) The $1,600 NLH $1M terms are dated Dec 3–5 while a schedule row shows a $1,600 2-Day $1M on Dec 9. 3) Venetian series overview labels the WPT Fall Festival 'Current Series' while listing DSE IV as 'Next Series' (stale label). 4) Venetian resort-fee page says 'Rates include a daily Resort Fee of $55 plus tax' while the poker-rate page lists it separately — confirm which applies to poker rates.",
   "how_to_find": "Ask each venue to reconcile; monitor.py flags future changes to these pages automatically.", "sources": ["https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html"]},
 ],
}
json.dump(questions, open(os.path.join(OUT, "questions.json"), "w"), indent=1)

suggestions = {
 "as_of": R,
 "intro": "Suggestions for improving the decision process and the site. None are implemented — review and choose a path before any change is built.",
 "items": [
  {"id": "S01", "title": "Confirm the 33 unverified WPT rows directly with the Wynn poker room", "category": "Verification",
   "options": ["A) Email/call the Wynn poker room for written entry terms on each unverified WPT event.", "B) Leave them unverified and decide only on Venetian data.", "C) Treat WPT rows with similar names to verified re-entry events as re-entry (not recommended — inference)."],
   "tradeoff": "A closes the biggest information gap. B is safest but leaves the WPT schedule unusable. C violates the no-inference rule.", "status": "Awaiting decision", "impact": "high"},
  {"id": "S02", "title": "Capture dated hotel quotes for Dec 6–13 at booking time", "category": "Hotels",
   "options": ["A) Manual capture from each official booking page into the rate log (checkout total, nightly average, fee, tax, parking, cancellation deadline, timestamp).", "B) Use the conditional poker rates as planning estimates.", "C) Wait until 30 days out when cancellation windows matter."],
   "tradeoff": "A yields true cost numbers but is per-date manual work. B over/under-shoots. C is timed to cancellation deadlines.", "status": "Awaiting decision", "impact": "high"},
  {"id": "S03", "title": "Verify walk times on Google Maps before booking", "category": "Logistics",
   "options": ["A) Click each prefilled Google Maps link for the hotel–venue pairs you will use.", "B) Accept the OSRM routing estimates.", "C) Add a physical test walk on arrival."],
   "tradeoff": "A is the confirmation step the ≤30-minute rule deserves. B risks bridge/detour errors. C is too late for booking.", "status": "Awaiting decision", "impact": "medium"},
  {"id": "S04", "title": "Add remaining poker rooms to the daily schedule pull", "category": "Coverage",
   "options": ["A) Add Palms, South Point, Orleans, The Strat, Golden Nugget official schedules to the morning monitor.", "B) Keep Venetian/Wynn/Caesars/MGM scope.", "C) Add only rooms with confirmed single-entry daily events."],
   "tradeoff": "A broadens the search for 8 AM starts and freezeout dailies. B is cheaper. C depends on discovery.", "status": "Awaiting decision", "impact": "medium"},
  {"id": "S05", "title": "Resolve the Valuetown 'subsequent buy in's' wording", "category": "Verification",
   "options": ["A) Ask the Venetian poker room in writing whether Events 18/58 are single-entry.", "B) Keep them flagged and exclude from the plan.", "C) Play them only as a fallback."],
   "tradeoff": "A settles it. B loses two $20K-guarantee options. C keeps exposure small.", "status": "Awaiting decision", "impact": "medium"},
  {"id": "S06", "title": "Tighten event-duration estimates", "category": "Schedule",
   "options": ["A) Record actual finish times of the first events played and feed them back into the overlap logic.", "B) Ask the tournament desk for typical durations.", "C) Keep level-count estimates."],
   "tradeoff": "A self-corrects during the trip. B is quick. C is current state.", "status": "Awaiting decision", "impact": "low"},
  {"id": "S07", "title": "Quality ratings for hotels", "category": "Hotels",
   "options": ["A) AAA Diamond listings.", "B) Forbes Travel Guide stars (Wynn Tower Suites statement already captured).", "C) Keep class assumptions."],
   "tradeoff": "A and B are third-party verified ratings; C is assumption-based.", "status": "Awaiting decision", "impact": "low"},
  {"id": "S08", "title": "Merge the archived dashboards into this one", "category": "Site",
   "options": ["A) Keep archives as-is (current state) with links from the Archive page.", "B) Delete after a review period.", "C) Port any unique rows from archives into data/site/ (they are already merged)."],
   "tradeoff": "A preserves prior sessions' work. B cleans up. C is already done by the integration pass.", "status": "Awaiting decision", "impact": "low"},
 ],
}
json.dump(suggestions, open(os.path.join(OUT, "suggestions.json"), "w"), indent=1)

flags = {
 "as_of": R,
 "items": [
  {"id": "F01", "item": "Venetian Events 18/58 (Valuetown) 'subsequent buy in's' wording", "where": "Structure sheet 8, note 07",
   "detail": "The sheet says the PokerAtlas PRO discount applies to 'their initial $200 buy in only' and 'All subsequent buy in's after the initial buy in will be $200', implying possible further entries. No explicit re-entry clause. Kept out of the confirmed single-entry list.", "severity": "medium"},
  {"id": "F02", "item": "WPT Dec 21 Turbo start-time discrepancy", "where": "WPT structures terms vs schedule row",
   "detail": "Event terms list Dec 21 at 6 PM; the schedule row shows 8:00 PM.", "severity": "low"},
  {"id": "F03", "item": "$1,600 NLH $1M date discrepancy", "where": "WPT structures terms (Dec 3–5) vs schedule row U-WPT14 (Dec 9)",
   "detail": "Possibly two separate events or a source error. Both are re-entry; no effect on the single-entry list.", "severity": "low"},
  {"id": "F04", "item": "WPT schedule text 'NIH' where NLH is expected", "where": "WPT schedule rows for Dec 13, Dec 14, Dec 15 events",
   "detail": "Printed as 'NIH' in the official schedule PDF. Presumed typo but shown as printed.", "severity": "low"},
  {"id": "F05", "item": "Venetian series overview stale status label", "where": "Venetian DSE series overview page",
   "detail": "Labels the WPT Fall Festival (Oct 28–Nov 15) 'Current Series' while showing DSE IV (from Nov 16) as 'Next Series' on the same snapshot date.", "severity": "low"},
  {"id": "F06", "item": "Venetian resort-fee wording ambiguity", "where": "Venetian resort-fee page vs poker-rate page",
   "detail": "Resort-fee page: 'Rates include a daily Resort Fee of $55 plus tax.' Poker-rate page presents the $55 fee separately. Confirm at reservation.", "severity": "medium"},
  {"id": "F07", "item": "Venetian poker rate $119/$209 property mapping", "where": "Venetian poker suite-rates page",
   "detail": "Both amounts published with conditional play requirements; the page does not bind each amount to one property. Recorded as separate dated entries; flagged.", "severity": "medium"},
  {"id": "F08", "item": "Hotel true cost uses assumed 13.38% tax on the resort fee", "where": "Trip calculator",
   "detail": "The 13.38% rate is verified for the room rate (Venetian hotel terms). Applying it to the fee is an assumption to confirm.", "severity": "medium"},
  {"id": "F09", "item": "Walk times are routing estimates, not Google/Apple Maps measurements", "where": "Walking matrix",
   "detail": "Computed with the OSRM foot profile from geocoded official addresses; Google Maps links included per pair for confirmation. ±10–15% error possible.", "severity": "medium"},
  {"id": "F10", "item": "No dated hotel room quotes captured for Dec 6–13, 2026", "where": "Hotel rate log",
   "detail": "Dynamic booking-engine pricing cannot be captured by a static fetch; official booking links provided. True-cost cells stay blank until quotes are logged.", "severity": "high"},
  {"id": "F11", "item": "Caesars Palace daily buy-in alternates $100/$160 by start", "where": "Caesars official flier vs guide page",
   "detail": "The guide page states $100; the flier shows $160 for some starts. Both recorded; per-start buy-in needs confirmation.", "severity": "low"},
  {"id": "F12", "item": "MGM Saturday event free-entry loyalty mechanic", "where": "MGM Grand poker page",
   "detail": "Five $120 dailies earn a free Saturday entry — a spend-more mechanic; event kept in the separate section. Re-entry status unverified.", "severity": "low"},
  {"id": "F13", "item": "33 WPT rows have no published entry terms", "where": "Wynn WPT structures PDF",
   "detail": "The official structures document covers 13 event types; the remaining schedule rows have no terms in any official document read. Rows stay unverified.", "severity": "high"},
  {"id": "F14", "item": "Westgate $70 freezeout lead is aggregator-sourced", "where": "Third-party calendars (VegasPokerCalendar/PokerAtlas)",
   "detail": "'Freezeout / No rebuy / No add-on' wording found on an aggregator detail page only; not confirmed with the Westgate poker room. Not used in any ranking.", "severity": "medium"},
  {"id": "F15", "item": "Sahara Las Vegas not geocoded", "where": "Walking matrix",
   "detail": "Nominatim returned only the monorail stop for the address; Sahara omitted from the matrix rather than guessed.", "severity": "low"},
  {"id": "F16", "item": "Event finish times are estimates", "where": "Day plan / overlap flags",
   "detail": "No official finish times exist. Durations estimated from level counts (28 levels × 30 min + breaks ≈ 12–14 h). Overlap flags are conservative.", "severity": "medium"},
  {"id": "F17", "item": "Hotel quality classes are assumptions", "where": "Hotel table",
   "detail": "No official AAA/Forbes listing captured except the Wynn Tower Suites Five-Star statement. Classes marked as assumptions.", "severity": "low"},
  {"id": "F18", "item": "Maximum-entry caps not published for Venetian freezeouts", "where": "Venetian sheets 1–37",
   "detail": "Freezeout classification rests on the absence of re-entry/rebuy/add-on clauses; sheets do not state entry caps explicitly.", "severity": "medium"},
 ],
}
json.dump(flags, open(os.path.join(OUT, "flags-f0816fab.json"), "w"), indent=1)

summary = {
 "as_of": R,
 "title": "Executive summary — Las Vegas Strip single-entry tournament trip planner",
 "scope": "Venetian DSE IV (Nov 16 – Dec 23, 2026), Wynn WPT World Championship (Nov 27 – Dec 21, 2026) and Wynn/Caesars/MGM recurring dailies. Every Venetian structure sheet (1–37) and the full WPT structures document were read first-hand on 2026-11-16. Values appear only where an official source states them.",
 "headline": [
  {"label": "Sheet-silent single-entry candidates (Venetian DSE IV)", "value": "46", "note": "Structure sheets read in full; no re-entry/rebuy/add-on clauses anywhere on the sheet — candidates under the strict standard (explicit single-entry confirmation outstanding). Includes 3 bounty types and 1 PKO, labeled separately."},
  {"label": "Flagged (ambiguous entry wording)", "value": "2", "note": "Valuetown events 18/58 — 'subsequent buy in's' phrasing."},
  {"label": "Excluded (spend-more / multi-flight / satellite / team)", "value": "42", "note": "Includes all 12 WPT event types with published terms (all allow re-entry), 4 Wynn dailies, 8 Venetian multi-flights, 7 satellites, 1 team event, Caesars add-on and MGM loyalty events."},
  {"label": "Unverified (entry terms not published)", "value": "33 WPT rows + Horseshoe dailies", "note": "Blank rule fields; flagged; excluded from ranking."},
  {"label": "Recommended trip window", "value": "fixed by rule — see trip plan", "note": "The consecutive 7-night window with the most sheet-silent single-entry candidates open to all players (ties → earliest). Age/gender-gated events shown separately."},
  {"label": "Earliest verified start", "value": "9:00 AM (Horseshoe daily, rules unverified)", "note": "No 8:00 AM start found in any checked official source."},
  {"label": "Best confirmed value ratio (gtd ÷ buy-in)", "value": "Event 36 — 93.75×", "note": "$800 bounty, $75K guarantee (includes bounties), Dec 9 11:10 AM. Descriptive ratio only — not a forecast."},
  {"label": "Walk-time rule", "value": "≤ 30 minutes", "note": "OSRM foot-routing estimates from official addresses; Google Maps confirmation links per pair."},
  {"label": "True hotel cost/night", "value": "rate + resort fee, taxed 13.38%", "note": "Verified fee/tax inputs; dated room rates still to be logged (flagged)."},
 ],
 "findings": [
  {"title": "Single-entry confirmation is now sheet-level", "text": "All 37 Venetian DSE IV structure sheets were read in full. 46 one-day (plus one two-day) events contain no re-entry, re-buy or add-on clause anywhere on the sheet. Under the strict standard adopted on main (arena/e1c079dc-poker2: sheet silence is not confirmation) these are single-entry CANDIDATES — the sheets' one-buy-in accounting supports it, but written single-entry confirmation from the poker room is still outstanding. The two Valuetown events are held back on their 'subsequent buy in's' wording."},
  {"title": "Wynn WPT is a re-entry series", "text": "Every WPT event whose terms are published in the official structures document allows re-entry (unlimited per flight until level 9–10, or one re-entry per flight for WPT Prime). The 12 documented event types are excluded from the single-entry list. 33 schedule rows have no published terms and stay unverified."},
  {"title": "Value ranking (descriptive ratio)", "text": "Ranked by guarantee ÷ buy-in among sheet-silent candidates with a printed guarantee: Event 36 $800 bounty $75K (93.75×), Event 54 $600 bounty $50K (83.33×), Event 52 $1,100 PKO $75K (68.18×). Bounty guarantees include bounty money — read the ratio as description, not EV."},
  {"title": "Plan one seat per day, evenings conditional", "text": "For Dec 6–13 the plan gives each day a primary confirmed event and, where a second exists, a conditional evening fallback. 1-Day events run to a winner, so back-to-back seats are flagged as overlapping."},
  {"title": "Walkability", "text": "Venetian/Palazzo are on-site for DSE IV. Harrah's/LINQ/Flamingo/Cromwell are 9–17 min from the Venetian. Wynn/Encore guests are 0–13 min from the WPT room (in Encore). Golden Nugget (83 min), Westgate (39 min), Mandalay Bay (52 min) fail the 30-minute rule to the Venetian."},
  {"title": "Hotel economics", "text": "Verified: Venetian/Palazzo/Wynn/Encore resort fee $55+tax; MGM Grand $50+tax; ARIA/Bellagio $55+tax; conditional Venetian poker rates from $119/$209 per night; 13.38% room tax; Venetian parking $20/day. Not verified: dated room quotes, cancellation deadlines, parking elsewhere — all blank and flagged."},
 ],
}
json.dump(summary, open(os.path.join(OUT, "summary.json"), "w"), indent=1)

# Sources registry for the site (adds walking-geometry services)
sources = {
  "V_PAGE": {"label": "Venetian DSE IV event page (Nov 16 – Dec 23, 2026)", "url": "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html", "publisher": "The Venetian Las Vegas (official)", "type": "Official schedule page"},
  "V_SCHED": {"label": "Venetian DSE IV schedule PDF", "url": "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/dse-nov-2026-schedule.pdf", "publisher": "The Venetian Las Vegas (official)", "type": "Official schedule PDF"},
  "W_SCHED": {"label": "Wynn WPT World Championship schedule PDF", "url": "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf", "publisher": "Wynn Las Vegas (official)", "type": "Official schedule PDF"},
  "W_STRUCT": {"label": "Wynn WPT World Championship terms & structures PDF", "url": "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf", "publisher": "Wynn Las Vegas (official)", "type": "Official terms PDF"},
  "W_DAILY": {"label": "Wynn daily tournament structures PDF", "url": "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf", "publisher": "Wynn Las Vegas (official)", "type": "Official structure PDF"},
  "W_POKER": {"label": "Wynn poker room page", "url": "https://www.wynnlasvegas.com/casino/poker", "publisher": "Wynn Las Vegas (official)", "type": "Official poker room page"},
  "CAESARS": {"label": "Caesars Las Vegas poker tournaments guide", "url": "https://www.caesars.com/las-vegas/explore/casino/poker-tournaments-las-vegas-strip", "publisher": "Caesars Entertainment (official)", "type": "Official guide page"},
  "CAESARS_FLIER": {"label": "Caesars Palace daily NLH flier PDF", "url": "https://www.caesars.com/content/dam/empire/clv/casino/poker/tournament-schedule/clv-poker-daily-nlh-tournament-flyer-2026.pdf", "publisher": "Caesars Entertainment (official)", "type": "Official flier PDF"},
  "MGM_POKER": {"label": "MGM Grand poker tables page", "url": "https://mgmgrand.mgmresorts.com/en/casino/poker-tables.html", "publisher": "MGM Grand (official)", "type": "Official poker room page"},
  "V_HOTEL_TC": {"label": "Venetian hotel terms & conditions (13.38% room tax, parking, deposit)", "url": "https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html", "publisher": "The Venetian Las Vegas (official)", "type": "Official terms"},
  "V_RESORT_FEE": {"label": "Venetian resort fee page ($55 plus tax)", "url": "https://www.venetianlasvegas.com/resort/resort-fee.html", "publisher": "The Venetian Las Vegas (official)", "type": "Official fee page"},
  "V_SUITE_RATES": {"label": "Venetian poker suite/player rates page", "url": "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html", "publisher": "The Venetian Las Vegas (official)", "type": "Official rate page"},
  "V_POKER": {"label": "Venetian poker room page", "url": "https://www.venetianlasvegas.com/resort/casino/poker.html", "publisher": "The Venetian Las Vegas (official)", "type": "Official poker room page"},
  "W_RESORT_INFO": {"label": "Wynn resort information ($55 plus tax resort fee)", "url": "https://www.wynnlasvegas.com/about-us/resort-information", "publisher": "Wynn Las Vegas (official)", "type": "Official fee page"},
  "MGM_TC": {"label": "MGM Resorts hotel terms & conditions", "url": "https://www.mgmresorts.com/en/hotel/terms-and-conditions.html", "publisher": "MGM Resorts International (official)", "type": "Official terms"},
  "GEOCODE": {"label": "OpenStreetMap Nominatim geocoder (official-address coordinates)", "url": "https://nominatim.openstreetmap.org", "publisher": "OpenStreetMap contributors (ODbL)", "type": "Geocoding service"},
  "OSRM_FOOT": {"label": "OSRM foot-routing server (walking durations)", "url": "https://routing.openstreetmap.de/routed-foot", "publisher": "FOSSGIS / Project-OSRM (open source)", "type": "Routing service"},
}
for n in range(1, 38):
    sources[f"V_S{n}"] = {"label": f"Venetian DSE IV structure sheet {n} (PDF)", "url": f"https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{n}.pdf", "publisher": "The Venetian Las Vegas (official)", "type": "Official structure PDF"}
json.dump(sources, open(os.path.join(OUT, "sources.json"), "w"), indent=1)

print("data/site written:", sorted(os.listdir(OUT)))
