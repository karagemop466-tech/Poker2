#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build data/audit/hotels.json - what each hotel's own official terms publish.

Only values printed on the property's own terms/conditions page (or the Clark County
licensing guide for the room-tax rate) are filled in. A field the property does not
publish is None and the reason is in `missing`.

`resort_fee` is the nightly fee only. The page-level total is built by the round-trip
calculator, which composes: rate x nights, resort fee x nights, occupancy surcharge,
then applies tax, then adds parking. The composition rule itself is flagged because
the properties publish "plus applicable tax" without printing the arithmetic.
"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "audit", "hotels.json")
RETRIEVED = "2026-11-17"
TAX = 0.1338
COUNTY_TAX_URL = ("https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:"
                  "689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/"
                  "genl-info-guide-for-tles-july-2021.pdf")

HOTELS = [
    dict(id="HT-01", name="The Venetian Resort Las Vegas",
         address="3355 S Las Vegas Blvd, Las Vegas, NV 89109",
         resort_fee=55.0, resort_fee_text="The Venetian Resort has a standard Las Vegas Resort Fee of $55 plus applicable tax per night, payable upon check-in.",
         fee_url="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
         tax_text="Daily rates do not include the applicable Clark County Room Tax of 13.38%.",
         tax_source="property", occupancy_extra=50.0,
         occupancy_text="For reservations with more than 2 guests per suite, a charge of $50 is added to the daily rate for each additional guest 13 years of age or older.",
         parking=20.0, parking_text="The daily fee for registered hotel guests is $20/day, seven days a week.",
         cancellation="Deposit equal to the first night's stay or prepayment of the entire stay, depending on the offer.",
         checkin="3:00 p.m.", checkout="11:00 a.m.",
         missing=["Dated room rate for the trip window: the official booking engine renders prices only in JavaScript and no checkout total was captured."],
         notes="Also publishes a conditional poker suite rate (see rates.json, R-VEN-POKER)."),
    dict(id="HT-02", name="The Palazzo at The Venetian",
         address="3325 S Las Vegas Blvd, Las Vegas, NV 89109",
         resort_fee=55.0, resort_fee_text="Same Venetian Resort terms page: a standard Las Vegas Resort Fee of $55 plus applicable tax per night.",
         fee_url="https://www.venetianlasvegas.com/legal/hotel-terms-and-conditions.html",
         tax_text="Clark County Room Tax of 13.38% (same Venetian terms page).",
         tax_source="property", occupancy_extra=50.0,
         occupancy_text="Same Venetian terms page: $50 per additional guest 13+ above 2 per suite.",
         parking=20.0, parking_text="Same Venetian terms page: $20/day for registered hotel guests.",
         cancellation="Same Venetian terms page.", checkin="3:00 p.m.", checkout="11:00 a.m.",
         missing=["Dated room rate for the trip window: no checkout total captured."],
         notes="Palazzo is operated under The Venetian's hotel terms; the poker suite page quotes from-$209 for Palazzo."),
    dict(id="HT-03", name="Wynn Las Vegas",
         address="3131 S Las Vegas Blvd, Las Vegas, NV 89109",
         resort_fee=55.0, resort_fee_text="A daily resort fee of $55 plus tax will be added to your room account for each room night.",
         fee_url="https://www.wynnlasvegas.com/terms-and-conditions/850257",
         tax_text="The Wynn terms page says 'plus tax' and prints no rate. The Clark County licensing guide lists Wynn/Encore (account 2000013.RES-001) at 13.38%.",
         tax_source="county", occupancy_extra=50.0,
         occupancy_text="A $50 surcharge per night shall be added for each guest exceeding the two or four guests in a room, as applicable.",
         parking=None, parking_text="Complimentary self-parking for up to two vehicles is included in the resort fee; no separate published price.",
         cancellation="A full deposit of all room nights and tax will be charged at the time of booking. Reservations are non-cancellable, non-refundable, and non-changeable.",
         checkin="", checkout="",
         missing=["Dated room rate for the trip window: no checkout total captured.",
                  "Check-in / check-out times not printed on the terms page that was read."],
         notes="The terms page read is an offer-specific terms page; the $55 fee and the $50 occupancy surcharge are stated on it."),
    dict(id="HT-04", name="Bellagio",
         address="3600 S Las Vegas Blvd, Las Vegas, NV 89109",
         resort_fee=55.0, resort_fee_text="A daily resort fee of $55.00 plus applicable tax will be applied to all reservations.",
         fee_url="https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
         tax_text="The Bellagio terms page says 'plus applicable tax' and prints no rate. Clark County licensing guide: 13.38%.",
         tax_source="county", occupancy_extra=50.0,
         occupancy_text="There is an additional charge of $50 plus tax per occupant, per night, above 2 occupants per room.",
         parking=None, parking_text="",
         cancellation="The first night's deposit is fully refundable provided a timely notice of cancellation is received at least 72 hours prior to the arrival date.",
         checkin="", checkout="",
         missing=["Dated room rate for the trip window: no checkout total captured.",
                  "Parking fee not published on the terms page that was read."],
         notes="Resort fee waived for MGM Rewards Gold+ members on eligible reservations."),
    dict(id="HT-05", name="Caesars Palace",
         address="3570 S Las Vegas Blvd, Las Vegas, NV 89109",
         resort_fee=None, resort_fee_text="", fee_url="", tax_text="Clark County licensing guide: 13.38%.",
         tax_source="county", occupancy_extra=None, occupancy_text="", parking=None, parking_text="",
         cancellation="", checkin="", checkout="",
         missing=["Resort fee: www.caesars.com/caesars-palace/hotel-policy redirected to the Caesars Palace home page, which prints no fee.",
                  "Dated room rate for the trip window: no checkout total captured.",
                  "Occupancy surcharge, parking, cancellation deadline: no official page read."],
         notes="NOT VERIFIED for fees. The site deliberately shows blanks rather than a remembered figure."),
    dict(id="HT-06", name="Horseshoe Las Vegas",
         address="3645 S Las Vegas Blvd, Las Vegas, NV 89109",
         resort_fee=None, resort_fee_text="", fee_url="", tax_text="Clark County licensing guide: 13.38%.",
         tax_source="county", occupancy_extra=None, occupancy_text="", parking=None, parking_text="",
         cancellation="", checkin="", checkout="",
         missing=["Resort fee: no official Horseshoe terms page was read.",
                  "Dated room rate for the trip window: no checkout total captured.",
                  "Occupancy surcharge, parking, cancellation deadline: no official page read."],
         notes="NOT VERIFIED for fees."),
    dict(id="HT-07", name="The Cosmopolitan of Las Vegas",
         address="3708 S Las Vegas Blvd, Las Vegas, NV 89109",
         resort_fee=None, resort_fee_text="", fee_url="", tax_text="Clark County licensing guide: 13.38%.",
         tax_source="county", occupancy_extra=None, occupancy_text="", parking=None, parking_text="",
         cancellation="", checkin="", checkout="",
         missing=["Resort fee: no official Cosmopolitan terms page was read in this pass.",
                  "Dated room rate for the trip window: no checkout total captured."],
         notes="NOT VERIFIED for fees."),
    dict(id="HT-08", name="ARIA Resort & Casino",
         address="3730 S Las Vegas Blvd, Las Vegas, NV 89158",
         resort_fee=55.0, resort_fee_text="A daily resort fee of $55.00 plus applicable tax will be applied to all reservations.",
         fee_url="https://aria.mgmresorts.com/en/terms-and-conditions.html",
         tax_text="The ARIA terms page says 'plus applicable tax' and prints no rate. Clark County licensing guide: 13.38%.",
         tax_source="county", occupancy_extra=50.0,
         occupancy_text="There is an additional charge of $50 plus tax per occupant, per night, above 2 occupants per room.",
         parking=None, parking_text="",
         cancellation="The first night's deposit is fully refundable provided a timely notice of cancellation is received at least 72 hours prior to the arrival date.",
         checkin="3:00 pm", checkout="11:00 am",
         missing=["Dated room rate for the trip window: no checkout total captured.",
                  "Parking fee not published on the terms page that was read."],
         notes="Fails the 30-minute walking rule to the Venetian (42 min)."),
    dict(id="HT-09", name="MGM Grand",
         address="3799 S Las Vegas Blvd, Las Vegas, NV 89109",
         resort_fee=50.0, resort_fee_text="A daily resort fee of $50.00 plus applicable tax will be applied to all reservations.",
         fee_url="https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
         tax_text="The MGM Grand terms page says 'plus applicable tax' and prints no rate. Clark County licensing guide: 13.38%.",
         tax_source="county", occupancy_extra=40.0,
         occupancy_text="There is an additional charge of $40 plus tax per occupant, per night, above 2 occupants per room.",
         parking=None, parking_text="",
         cancellation="The first night's deposit is fully refundable provided a timely notice of cancellation is received at least 72 hours prior to the arrival date.",
         checkin="3:00 pm", checkout="11:00 am",
         missing=["Dated room rate for the trip window: no checkout total captured.",
                  "Parking fee not published on the terms page that was read."],
         notes="Fails the 30-minute walking rule to the Venetian (45 min)."),
    dict(id="HT-10", name="Westgate Las Vegas Resort & Casino",
         address="3000 Paradise Rd, Las Vegas, NV 89109",
         resort_fee=None, resort_fee_text="", fee_url="", tax_text="Clark County licensing guide: 13.38%.",
         tax_source="county", occupancy_extra=None, occupancy_text="", parking=None, parking_text="",
         cancellation="", checkin="", checkout="",
         missing=["Resort fee: no official Westgate terms page was read in this pass.",
                  "Dated room rate for the trip window: no checkout total captured."],
         notes="Fails the 30-minute walking rule to the Venetian (34 min)."),
    dict(id="HT-11", name="South Point Hotel, Casino & Spa",
         address="9777 S Las Vegas Blvd, Las Vegas, NV 89183",
         resort_fee=None, resort_fee_text="", fee_url="", tax_text="Clark County licensing guide: 13.38%.",
         tax_source="county", occupancy_extra=None, occupancy_text="", parking=0.0,
         parking_text="Self-parking is free (stated on the property's poker page, per an earlier session's note; not re-read in this pass).",
         cancellation="", checkin="", checkout="",
         missing=["Resort fee: no official South Point terms page was read in this pass.",
                  "Dated room rate for the trip window: no checkout total captured."],
         notes="9 miles / about 3 hours on foot from the Venetian: outside the walking corridor entirely."),
]


def main():
    walk = json.load(open(os.path.join(ROOT, "data", "audit", "walking.json")))["hotels"]
    walk_by = {w["hotel_id"]: w for w in walk}
    rows = []
    for h in HOTELS:
        w = walk_by.get(h["id"], {})
        r = dict(h)
        r["tax_rate"] = TAX
        r["tax_source_url"] = COUNTY_TAX_URL
        r["walk_minutes"] = w.get("walk_minutes")
        r["walk_within_30"] = w.get("within_30_min")
        r["walk_source_url"] = w.get("source_url")
        r["walk_basis"] = w.get("basis")
        r["fee_verified"] = h["resort_fee"] is not None
        r["booking_url"] = {
            "HT-01": "https://www.venetianlasvegas.com/book",
            "HT-02": "https://www.venetianlasvegas.com/book",
            "HT-03": "https://www.wynnlasvegas.com/book",
            "HT-04": "https://bellagio.mgmresorts.com/en/hotel.html",
            "HT-05": "https://www.caesars.com/caesars-palace",
            "HT-06": "https://www.caesars.com/horseshoe-las-vegas",
            "HT-07": "https://www.cosmopolitanlasvegas.com/",
            "HT-08": "https://aria.mgmresorts.com/en/hotel.html",
            "HT-09": "https://mgmgrand.mgmresorts.com/en/hotel.html",
            "HT-10": "https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/",
            "HT-11": "https://southpointcasino.com/hotel",
        }[h["id"]]
        r["retrieved"] = RETRIEVED
        rows.append(r)

    meta = {
        "as_of": RETRIEVED,
        "room_tax": TAX,
        "room_tax_note": ("13.38% is the Clark County transient lodging tax for resort hotels. It is the "
                          "figure printed in the county's licensing guide and on The Venetian's own hotel "
                          "terms. The county PDF's internal title reads 'Sept 2018' even though its URL "
                          "contains 'july-2021', so the document's revision date is not certain - flagged."),
        "county_tax_source": COUNTY_TAX_URL,
        "fee_verified_count": sum(1 for r in rows if r["fee_verified"]),
        "rates_verified_count": 0,
        "note": ("resort_fee is the nightly fee the property itself publishes. No dated room rate was "
                 "captured for any property: every official booking engine renders prices only inside "
                 "JavaScript. The trip-cost calculator therefore reports a hotel total that excludes "
                 "the room rate and says so."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "hotels": rows}, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print("hotels:", len(rows), "| fee verified:", meta["fee_verified_count"])
    for r in rows:
        print("  %-6s %-44s fee=%-6s walk=%-4s %s" % (r["id"], r["name"][:44], r["resort_fee"],
                                                       r["walk_minutes"],
                                                       "IN" if r["walk_within_30"] else "OUT"))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
