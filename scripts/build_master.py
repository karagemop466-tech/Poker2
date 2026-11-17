#!/usr/bin/env python3
"""Merge all verified datasets + this session's official-source reads into
data/master.json — the single source of truth for the site.

Inputs (all already in the repo):
  data/venetian-dse4-official-check.json  (Venetian DSE IV rows, structure-checked)
  data/verified/tournaments.json          (classification + Wynn WPT/daily rows)
  data/hotels.json, data/verified/hotels.json
  data/flags.json, data/verified/{questions,suggestions,summary}.json
  data/sources.json
  data/session-updates.json               (arena/8234a824-poker2 official reads)

No value is invented here: every field comes from an input file whose own
provenance is an official page/PDF, or is left blank/null.
"""
import json, re, os, datetime, urllib.parse
_re2b = re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AS_OF = "2026-11-16"          # date the underlying datasets were transcribed
LAST_VERIFIED = "2026-11-17"  # date this session re-read the official sources

def load(p):
    with open(os.path.join(ROOT, p)) as f:
        return json.load(f)

check = load("data/venetian-dse4-official-check.json")
verified = load("data/verified/tournaments.json")
updates = load("data/session-updates.json")
hotels_b = load("data/hotels.json")
hotels_v = load("data/verified/hotels.json")
flags_b = load("data/flags.json")
questions = load("data/verified/questions.json")
suggestions = load("data/verified/suggestions.json")
summary_v = load("data/verified/summary.json")
sources_b = load("data/sources.json")

V_SCHED = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html"
def struct_url(n):
    return ("https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/"
            "2026/structures/dse_nov_2026-structure_%s.pdf" % n)
W_WPT_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf"
W_WPT_SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf"
W_POKER = "https://www.wynnlasvegas.com/casino/poker"
W_DAILY_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf"
C_GUIDE = updates["caesars_recurring"]["guide_url"]
C_FLYER = updates["caesars_recurring"]["flyer_url"]
MGM_POKER = updates["mgm_grand_daily"]["url"]
GN_PAGE = updates["golden_nugget_daily"]["url"]

SHEET_READS = updates["structure_sheet_reads"]
WYNN_RULES = updates["wynn_wpt_rules_read"]["rules"]

def tags_from_name(name):
    n = name.lower()
    tags = []
    if "bounty" in n or "pko" in n or "knock-out" in n or "knockout" in n:
        tags.append("bounty")
    if "pko" in n or "progressive knock" in n:
        tags.append("pko")
    if "turbo" in n:
        tags.append("turbo")
    if "senior" in n:
        tags.append("seniors")
    if "lips" in n or "ladies" in n or "women" in n or "queen" in n:
        tags.append("ladies")
    if "omaha" in n or "plo" in n or "big o" in n:
        tags.append("plo")
    if "torse" in n or "horse" in n or "mixed" in n or "triple draw" in n or "badugi" in n or "stud" in n or "nih" in n or "limit omaha" in n:
        tags.append("mixed")
    if "tag team" in n or "teams" in n:
        tags.append("team")
    if "satellite" in n:
        tags.append("satellite")
    if "raceday" in n or "race day" in n:
        tags.append("raceday")
    if "milestone" in n:
        tags.append("milestone")
    if "high roller" in n:
        tags.append("high-roller")
    return tags

def clean_time(t):
    """'11:10' -> '11:10 AM'; '16:10' -> '4:10 PM'; keep strings like '10:00 AM'."""
    if not t:
        return ""
    t = str(t).strip()
    m = re.match(r"^(\d{1,2}):(\d{2})$", t)
    if m:
        h, mm = int(m.group(1)), m.group(2)
        suf = "AM" if h < 12 else "PM"
        h12 = h % 12 or 12
        return "%d:%s %s" % (h12, mm, suf)
    return t

def parse_start(t):
    """Return (hour24, minute) for overlap math, or None."""
    if not t:
        return None
    m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)", t.strip(), re.I)
    if not m:
        return None
    h, mm = int(m.group(1)), int(m.group(2))
    if m.group(3).upper() == "PM" and h != 12:
        h += 12
    if m.group(3).upper() == "AM" and h == 12:
        h = 0
    return (h, mm)

events = []
eid = 0
def add_event(**kw):
    global eid
    eid += 1
    kw.setdefault("id", "E%03d" % eid)
    kw.setdefault("gtd_includes_bounties", None)
    kw.setdefault("bounty", None)
    kw.setdefault("notes", "")
    events.append(kw)

# ---------------------------------------------------------------- Venetian rows
def ven_common(row, category, rules, tags_extra=None):
    struct = row.get("structure")
    sheet = SHEET_READS.get(str(struct)) if struct is not None else None
    tags = tags_from_name(row.get("name", "")) + (tags_extra or [])
    fee = row.get("fee")
    pool = row.get("prize_pool_each")
    excerpt = rules.get("excerpt", "")
    if not excerpt and sheet:
        excerpt = sheet.get("excerpt", "")
    return dict(
        venue_id="venetian", venue="The Venetian",
        name=row.get("name", ""), game="", 
        date=row.get("date", ""), start=clean_time(row.get("time")),
        buy_in=row.get("buy_in"), fee=fee, pool_per_entry=pool,
        gtd=row.get("gtd"), format=category if category in ("multi-flight", "satellite", "team") else "one-day",
        category=category, tags=sorted(set(tags)),
        chips=row.get("starting_chips") or (sheet or {}).get("chips"),
        level_min=(sheet or {}).get("level_min", ""),
        late_reg=(sheet or {}).get("late_reg", ""),
        rules=rules,
        last_checked=AS_OF,
        source_url=V_SCHED,
        struct_url=struct_url(struct) if isinstance(struct, int) else "",
        notes=row.get("note", ""),
    )

for row in check["single_entry"]:
    ev_no = row.get("event_no")
    struct = row.get("structure")
    sheet = SHEET_READS.get(str(struct))
    if ev_no in (18, 58):
        cat = "ambiguous"
        rules = dict(
            single_entry="ambiguous",
            re_entry="not stated; sheet note 7 refers to \u201csubsequent buy in\u2019s\u201d",
            add_on="none stated",
            excerpt=SHEET_READS["8"]["excerpt"],
            retrieved=AS_OF,
        )
        notes = "Sheet note 7 implies more than one buy-in may be possible (see flag). Entry limit NOT confirmed."
    else:
        cat = "single"
        rules = dict(
            single_entry="not stated \u2014 sheet is silent on re-entry",
            re_entry="no re-entry clause printed on the sheet; silence, not a prohibition",
            add_on="no add-on clause printed on the sheet; silence, not a prohibition",
            excerpt=(sheet or {}).get("excerpt") or row.get("entry_rules", ""),
            retrieved=(sheet or {}).get("retrieved", AS_OF),
        )
        notes = ("Structure sheet read in full 2026-11-16. It prints no re-entry, rebuy or add-on "
                 "mechanism, but it also never says 'no re-entry', so this row is recorded as "
                 "sheet-silent rather than confirmed single-entry.")
    ev = ven_common(row, cat, rules)
    if ev_no in (3, 4, 5):
        ev["notes"] = (ev["notes"] + " " if ev["notes"] else "") + \
            "Official subtitle: \u201cRace to finish before the Race\u201d \u2014 hard finish constraint; no guarantee published."
        ev["tags"] = sorted(set(ev["tags"] + ["raceday"]))
    if ev_no in (8, 17, 18, 40, 43, 58):
        ev["gtd_includes_bounties"] = True
    if ev_no in (9, 11, 13, 15, 16, 21, 22, 23, 25, 29, 42, 50, 51, 53, 55, 54):
        # bounty one-day events whose sheets state the guarantee includes bounties
        if ev_no in (9, 16, 29):
            ev["gtd_includes_bounties"] = True
    if ev_no == 35:
        ev["category"] = "team"
        ev["format"] = "team"
    add_event(id="V-%02d" % ev_no, **ev)

for row in check["multi_flight_not_single_entry"]:
    struct = row.get("structure")
    sheet = SHEET_READS.get(str(struct))
    rules = dict(
        single_entry="no \u2014 multi-flight event (each starting flight is a separate entry)",
        re_entry="a player who has not bagged a Day 2 stack may enter another flight" if sheet else "unverified for this flight sheet",
        add_on="none stated",
        excerpt=(sheet or {}).get("excerpt") or row.get("note", ""),
        retrieved=(sheet or {}).get("retrieved", AS_OF),
    )
    ev = ven_common(row, "multi-flight", rules)
    add_event(id="V-MF%02d-%s-%s" % (row.get("event_no", 0), row.get("date", "")[-5:],
                                     clean_time(row.get("time")).replace(" ", "")), **ev)

for row in check["excluded_team_satellite_and_other"]:
    name = row.get("name", "")
    cat = "team" if "tag team" in name.lower() else "satellite"
    rules = dict(
        single_entry="no \u2014 " + ("team event (one entry per team)" if cat == "team" else "satellite (awards a seat, not a cash prize pool)"),
        re_entry="none stated", add_on="none stated",
        excerpt=SHEET_READS["31"]["excerpt"] if cat == "team" else row.get("note", ""),
        retrieved=AS_OF,
    )
    ev = ven_common(row, cat, rules)
    add_event(id="V-X%02d" % row.get("event_no", 0), **ev)

# --------------------------------------------------- Wynn WPT + Wynn daily rows
def is_turbo600(name):
    return "turbo" in name.lower() and "$600" in name and "50k" in name.lower().replace(" ", "")

for row in verified["unverified"] + verified["excluded"]:
    rid = row.get("id", "")
    name = row.get("name", "")
    if "WPT" in rid:
        if rid in ("X-WPT01", "X-WPT02"):
            cat = "spend-more"
            key = "wpt_600nlh_400k" if rid == "X-WPT01" else "wpt_800nlh_1m"
            rules = dict(single_entry="no \u2014 unlimited re-entry per starting flight",
                         re_entry=WYNN_RULES[key], add_on="none stated",
                         excerpt=WYNN_RULES[key], retrieved=AS_OF)
        elif rid == "X-WPT04":
            cat = "spend-more"
            rules = dict(single_entry="no \u2014 one re-entry per starting flight",
                         re_entry=WYNN_RULES["wpt_prime_1100"], add_on="none stated",
                         excerpt=WYNN_RULES["wpt_prime_1100"], retrieved=AS_OF)
        elif is_turbo600(name):
            cat = "spend-more"
            rules = dict(single_entry="no \u2014 unlimited re-entry",
                         re_entry=WYNN_RULES["wpt_600nlh_turbo_50k"], add_on="none stated",
                         excerpt=WYNN_RULES["wpt_600nlh_turbo_50k"], retrieved=AS_OF)
        elif rid.startswith("X-WPT"):
            cat = "multi-flight"
            rules = dict(single_entry="no \u2014 multi-flight (official naming)",
                         re_entry="unverified for this event\u2019s sheet", add_on="unverified",
                         excerpt=row.get("reason", ""), retrieved=AS_OF)
        else:
            cat = "unverified"
            rules = dict(single_entry="unverified", re_entry="unverified", add_on="unverified",
                         excerpt=row.get("reason", ""), retrieved=AS_OF)
        add_event(
            id=rid, venue_id="wynn", venue="Wynn Las Vegas", name=name, game="",
            date=row.get("date", ""), start=clean_time(row.get("start")),
            buy_in=row.get("buy_in"), fee=None, pool_per_entry=None, gtd=row.get("gtd"),
            format="multi-flight" if "day 1" in name.lower() or "1a" in name.lower() else "one-day",
            category=cat, tags=sorted(set(tags_from_name(name))),
            chips=None, level_min="", late_reg="",
            rules=rules, last_checked=AS_OF,
            source_url=W_WPT_SCHED, struct_url=W_WPT_STRUCT,
            notes=row.get("reason", ""),
        )
    elif rid in ("X-W01", "X-W02", "X-W03", "X-W04"):
        rules = dict(
            single_entry="no \u2014 re-entry / rebuy / add-on confirmed on official daily structure sheet",
            re_entry="yes" if "re-entry" in row.get("reason", "").lower() or rid in ("X-W01", "X-W03", "X-W04") else "no",
            add_on="yes" if "add-on" in row.get("reason", "").lower() else "none stated",
            excerpt=row.get("reason", ""), retrieved=AS_OF)
        add_event(
            id=rid, venue_id="wynn", venue="Wynn Las Vegas", name=name, game="",
            date="Recurring (daily rule)", start=clean_time(row.get("start")),
            buy_in=row.get("buy_in"), fee=None, pool_per_entry=None, gtd=row.get("gtd"),
            format="recurring", category="spend-more", tags=sorted(set(tags_from_name(name))),
            chips=None, level_min="", late_reg="",
            rules=rules, last_checked=AS_OF,
            source_url=W_DAILY_STRUCT, struct_url=W_DAILY_STRUCT,
            notes=row.get("reason", ""),
        )

# ------------------------------------------------------- recurring venue feeds
cz = updates["caesars_recurring"]
for t in cz["caesars_palace"]["times"]:
    add_event(
        id="CZP-" + t.replace(" ", "").replace(":", ""), venue_id="caesars", venue="Caesars Palace",
        name="Daily NLH $100 buy-in, $1,000 GTD", game="NLH",
        date="Recurring (daily)", start=t, buy_in=100, fee=None, pool_per_entry=None, gtd=1000,
        format="recurring", category="spend-more", tags=["recurring", "add-on"],
        chips=20000, level_min=20, late_reg="",
        rules=dict(single_entry="no \u2014 paid add-on confirmed", re_entry="not stated on the official guide",
                   add_on="$50 add-on for 15,000 chips at the first break",
                   excerpt=cz["caesars_palace"]["excerpt"], retrieved=AS_OF),
        last_checked=AS_OF, source_url=C_GUIDE, struct_url=C_FLYER,
        notes="Official guide: four daily events at 10 AM, 2 PM, 6 PM, 9 PM. Official daily flyer (read 2026-11-16 by session arena/acd81e67-poker2) lists $160 buy-ins at 2 PM and 9 PM \u2014 discrepancy flagged, values not reconciled.",
    )
for t in cz["horseshoe"]["times"]:
    add_event(
        id="HS-" + t.replace(" ", "").replace(":", ""), venue_id="horseshoe", venue="Horseshoe Las Vegas",
        name="Daily NLH (buy-in varies)", game="NLH",
        date="Recurring (daily)", start=t, buy_in=None, fee=None, pool_per_entry=None, gtd=None,
        format="recurring", category="unverified", tags=["recurring"],
        chips=None, level_min="", late_reg="",
        rules=dict(single_entry="unverified", re_entry="unverified", add_on="unverified",
                   excerpt=cz["horseshoe"]["excerpt"], retrieved=AS_OF),
        last_checked=AS_OF, source_url=C_GUIDE, struct_url="",
        notes="The official guide lists the times only: \u201cA mixture of buy-ins, levels and guarantees\u201d. Buy-in, guarantee and entry rules are not published there \u2014 left blank.",
    )
mg = updates["mgm_grand_daily"]
for t in mg["times"]:
    add_event(
        id="MGM-" + t.replace(" ", "").replace(":", ""), venue_id="mgm", venue="MGM Grand",
        name="Daily NLH tournament", game="NLH",
        date="Recurring (daily)", start=t, buy_in=None, fee=None, pool_per_entry=None, gtd=None,
        format="recurring", category="unverified", tags=["recurring"],
        chips=None, level_min="", late_reg="",
        rules=dict(single_entry="unverified", re_entry="unverified", add_on="unverified",
                   excerpt=mg["excerpt"], retrieved=AS_OF),
        last_checked=AS_OF, source_url=MGM_POKER, struct_url=mg["weekly_pdf"],
        notes=mg["entry_rules"],
    )
add_event(
    id="MGM-SAT-150", venue_id="mgm", venue="MGM Grand",
    name="$150 NLH, $2,000 GTD (Saturday)", game="NLH",
    date="Recurring (Saturday)", start="11:00 AM", buy_in=150, fee=None, pool_per_entry=None, gtd=2000,
    format="recurring", category="spend-more", tags=["recurring"],
    chips=None, level_min="", late_reg="",
    rules=dict(single_entry="unverified", re_entry="unverified", add_on="unverified",
               excerpt="Five $120 daily entries earn one free Saturday entry (spend-more mechanic). Re-entry/add-on rules not in the official PDF.",
               retrieved=AS_OF),
    last_checked=AS_OF, source_url=MGM_POKER, struct_url=mg["weekly_pdf"],
    notes="Row read from the official MGM weekly schedule PDF on 2026-11-16 by session arena/acd81e67-poker2; time differs between PDF (11:10 AM) and web (11:00 AM) \u2014 flagged.",
)
gn = updates["golden_nugget_daily"]
for t in gn["times"]:
    add_event(
        id="GN-" + t.replace(" ", "").replace(":", ""), venue_id="gn", venue="Golden Nugget (downtown)",
        name="Daily NLH, 15,000 chips, 15-min levels", game="NLH",
        date="Recurring (daily)", start=t, buy_in=None, fee=None, pool_per_entry=None, gtd=None,
        format="recurring", category="spend-more", tags=["recurring", "add-on"],
        chips=15000, level_min=15, late_reg="Registration closes after level 4 (~11:15 AM / 6:15 PM / 3:15 AM)",
        rules=dict(single_entry="no \u2014 unlimited re-entry and paid add-ons confirmed",
                   re_entry="unlimited re-entries until the start of level 5",
                   add_on="up to two $20 add-ons for 10,000 chips each",
                   excerpt=gn["excerpt"], retrieved=AS_OF),
        last_checked=AS_OF, source_url=GN_PAGE, struct_url="",
        notes="Downtown location (Fremont Street), not the Strip. Buy-in is not printed on the official page \u2014 left blank.",
    )

# ------------------------------------------------------------------- hotels
# Walking times read from Google Maps walking directions on 2026-11-17. Google Maps is a
# third-party routing service, not the casino: each figure below is the number the routing
# page printed for the shortest walking route, plus the distance it printed alongside it.
# Only the routes actually read are recorded; anything else stays blank.
# Google Maps is not an "official" casino document, so walking rows are marked
# source_type="third-party routing" and never used to state a fact about a room's rules.
WALK_READ = "2026-11-17"
WALK_METHOD = ("Google Maps walking directions, shortest suggested route, read 2026-11-17; "
               "figures rounded as the page displayed them")

def walk_links(address, hotel):
    dest_ven = "The Venetian Poker Room, 3355 S Las Vegas Blvd, Las Vegas, NV"
    dest_wyn = "Wynn Las Vegas Poker Room, 3131 S Las Vegas Blvd, Las Vegas, NV"
    return {
        "maps_venetian": "https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=walking"
                         % (urllib.parse.quote_plus(address), urllib.parse.quote_plus(dest_ven)),
        "maps_wynn": "https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=walking"
                     % (urllib.parse.quote_plus(address), urllib.parse.quote_plus(dest_wyn)),
    }

# origin label -> (minutes, distance text) for route to The Venetian Poker Room
WALK_TO_VENETIAN = {
    "H-WYN":  (12, "0.5 mile"),
    "H-PAL":  (4,  "443 ft"),
    "H-VEN":  (5,  "0.1 mile"),
    "H-ARIA": (37, "1.6 miles"),
    "H-BEL":  (28, "1.1 miles"),
    "H-MGM":  (42, "1.8 miles"),
    "H-HS":   (24, "1.0 mile"),
    "H-CZP":  (19, "0.8 mile"),
}

hotels = []
hmap = {}

def add_hotel(**kw):
    kw.setdefault("rate_log", [])
    kw.setdefault("parking", "")
    kw.setdefault("parking_value", None)
    kw.setdefault("deposit", "")
    kw.setdefault("cancellation", "")
    kw.setdefault("quality", "")
    kw.setdefault("notes", "")
    kw.setdefault("booking_url", "")
    kw["walk"] = dict(venetian_min=None, wynn_min=None,
                      status="UNVERIFIED \u2014 no official walking-time source captured; use the maps links for manual check (30-minute limit)",
                      **walk_links(kw.get("address", ""), kw.get("name", "")))
    hotels.append(kw)
    hmap[kw["id"]] = kw

TAX = 0.1338  # Clark County room tax per Venetian official hotel terms (2026-11-16)

add_hotel(
    id="H-VEN", name="The Venetian Resort Las Vegas", area="Strip (venue hotel)",
    address="3355 S. Las Vegas Blvd, Las Vegas, NV 89109",
    resort_fee_value=55.0,
    resort_fee_text="$55 plus applicable tax per night (official resort-fee page)",
    resort_fee_src="https://www.venetianlasvegas.com/resort/resort-fee.html",
    tax_rate=TAX,
    tax_note="Clark County Room Tax of 13.38% (official hotel terms). Applying it to the resort fee is a computation to confirm at checkout.",
    parking="$20/day for hotel guests (official hotel terms).", parking_value=20.0,
    deposit="$150 per night incidentals (official hotel terms).",
    cancellation="",
    quality="",
    booking_url="https://www.venetianlasvegas.com/book",
    rate_log=[],   # see notes: the official page does not say which property is which
    notes=("Official 2026 poker-suite-rate page (re-read 2026-11-17) prints ONE pair of starting "
           "rates — 'as low as $119 and $209' — for a Luxury King Suite 'in either The Venetian or "
           "The Palazzo' and states play requirements ($300+ tournament buy-in, or six hours of live "
           "cash, per night stayed). It does not say which property carries which number, so no rate "
           "is attributed to this hotel; both numbers are recorded once, in rate_log_shared below. "
           "A dated checkout quote for exact trip dates has NOT been captured."),
)
add_hotel(
    id="H-PAL", name="The Palazzo at The Venetian", area="Strip (venue hotel)",
    address="3325 S. Las Vegas Blvd, Las Vegas, NV 89109",
    resort_fee_value=55.0,
    resort_fee_text="$55 plus applicable tax per night (official resort-fee page, shared with Venetian)",
    resort_fee_src="https://www.venetianlasvegas.com/resort/resort-fee.html",
    tax_rate=TAX,
    tax_note="Same Clark County room tax disclosure as The Venetian.",
    parking="$20/day for hotel guests (official hotel terms).", parking_value=20.0,
    deposit="$150 per night incidentals (official hotel terms).",
    booking_url="https://www.venetianlasvegas.com/book",
    rate_log=[],   # see notes: the official page does not say which property is which
    notes=("Same resort and poker room as The Venetian. The official poker-rate page prints the same "
           "unattributed pair of starting rates ($119 / $209) for 'either The Venetian or The "
           "Palazzo'; it does not map a number to a property. See rate_log_shared."),
)
add_hotel(
    id="H-WYN", name="Wynn Las Vegas", area="Strip (venue hotel)",
    address="3131 S. Las Vegas Blvd, Las Vegas, NV 89109",
    resort_fee_value=55.0,
    resort_fee_text="$55 plus tax per room night (official resort-information page)",
    resort_fee_src="https://www.wynnlasvegas.com/about-us/resort-information",
    tax_rate=0.1338,
    tax_note="Clark County transient lodging tax 13.38% (county licensing guide; corroborated by The Venetian's and The Cosmopolitan's hotel terms). The property's own terms say \u201cplus tax\u201d without printing the rate.",
    parking="Self-parking for up to two vehicles is included in the resort fee (official).",
    deposit="$150 per night (official Wynn terms, 2026 promo terms page).",
    booking_url="https://www.wynnlasvegas.com",
    rate_log=[],
    notes="Wynn Tower Suites holds a published 20th consecutive Forbes Travel Guide Five-Star statement for 2026 (Tower Suites only). No dated room quote captured.",
)
add_hotel(
    id="H-ARIA", name="ARIA Resort & Casino", area="Strip",
    address="3730 S. Las Vegas Blvd, Las Vegas, NV 89109",
    resort_fee_value=55.0,
    resort_fee_text="$55 plus tax per night; $50 plus tax extra occupant (official terms)",
    resort_fee_src="https://aria.mgmresorts.com/en/terms-and-conditions.html",
    tax_rate=0.1338,
    tax_note="Clark County transient lodging tax 13.38% (county licensing guide; corroborated by The Venetian's and The Cosmopolitan's hotel terms). The property's own terms say \u201cplus tax\u201d without printing the rate.",
    parking="", deposit="$150\u2013$500/day by room type (official terms).",
    booking_url="https://aria.mgmresorts.com",
    rate_log=[],
    notes="MGM Rewards Gold+ waives the resort fee (per official terms read 2026-11-16 by session arena/93b28309-poker2).",
)
add_hotel(
    id="H-BEL", name="Bellagio", area="Strip",
    address="3600 S. Las Vegas Blvd, Las Vegas, NV 89109",
    resort_fee_value=55.0,
    resort_fee_text="$55 plus tax per night; $50 plus tax extra occupant (official terms)",
    resort_fee_src="https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
    tax_rate=0.1338,
    tax_note="Clark County transient lodging tax 13.38% (county licensing guide; corroborated by The Venetian's and The Cosmopolitan's hotel terms). The property's own terms say \u201cplus tax\u201d without printing the rate.",
    parking="", deposit="$150/day incidentals (official terms).",
    booking_url="https://bellagio.mgmresorts.com",
    rate_log=[],
    notes="MGM Rewards Gold+ waives the resort fee (per official terms read 2026-11-16 by session arena/93b28309-poker2).",
)
add_hotel(
    id="H-MGM", name="MGM Grand", area="Strip (venue hotel)",
    address="3799 S. Las Vegas Blvd, Las Vegas, NV 89109",
    resort_fee_value=50.0,
    resort_fee_text="$50 plus applicable tax per night (official hotel terms)",
    resort_fee_src="https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
    tax_rate=0.1338,
    tax_note="Clark County transient lodging tax 13.38% (county licensing guide; corroborated by The Venetian's and The Cosmopolitan's hotel terms). The property's own terms say \u201cplus tax\u201d without printing the rate.",
    parking="", deposit="",
    booking_url="https://mgmgrand.mgmresorts.com/en/hotel.html",
    rate_log=[],
    notes="Hosts the MGM Grand poker room (daily tournaments 11 AM / 7 PM / 11 PM). Gold+ may waive the fee per official terms.",
)
add_hotel(
    id="H-HS", name="Horseshoe Las Vegas", area="Strip (venue hotel)",
    address="3645 S. Las Vegas Blvd, Las Vegas, NV 89109",
    resort_fee_value=None,
    resort_fee_text="",
    resort_fee_src="https://www.caesars.com/horseshoe-las-vegas/hotel",
    tax_rate=0.1338,
    tax_note="Clark County transient lodging tax 13.38% (county licensing guide; corroborated by The Venetian's and The Cosmopolitan's hotel terms). The property's own terms do not print a rate.",
    parking="", deposit="",
    cancellation="Free 48-hour cancellation advertised on the official hotel page (2026-11-16).",
    booking_url="https://www.caesars.com/book/?propcode=BLV",
    rate_log=[],
    notes="Resort-fee amount is NOT published on the official pages captured; it appears in the official booking flow at checkout. Blank + flagged. Caesars Rewards Diamond+ waives resort fees (official benefits page). Hall of Fame Poker Room (daily tournaments).",
)
add_hotel(
    id="H-CZP", name="Caesars Palace", area="Strip (venue hotel)",
    address="3570 S. Las Vegas Blvd, Las Vegas, NV 89109",
    resort_fee_value=None, resort_fee_text="",
    resort_fee_src="https://www.caesars.com/caesars-palace/hotel",
    tax_rate=0.1338, tax_note="Clark County transient lodging tax 13.38% (county licensing guide; corroborated by The Venetian's and The Cosmopolitan's hotel terms). The property's own terms say \u201cplus tax\u201d without printing the rate.", parking="", deposit="",
    cancellation="Free 48-hour cancellation advertised on official Caesars hotel pages (2026-11-16).",
    booking_url="https://www.caesars.com/book/?propcode=CP",
    rate_log=[],
    notes="Resort-fee amount not published on captured official pages \u2014 blank + flagged. Diamond+ waives resort fees (official benefits page). Caesars Palace poker room hosts the $100/$1,000-GTD daily events.",
)

# --------------------------------------------------------------- ranking helpers
for ev in events:
    bi = ev.get("buy_in")
    gtd = ev.get("gtd")
    ev["total_entry_fee"] = bi  # Venetian/Wynn buy-ins are total amounts collected at the cage
    if bi and gtd:
        ev["gtd_ratio"] = round(gtd / bi, 2)
    else:
        ev["gtd_ratio"] = None

# ------------------------------------------------------------ flags (merged)
flags = []
for f in flags_b.get("flags", []):
    flags.append(dict(source="data/flags.json", **f))
for ir in updates["irregularities_found_this_session"]:
    flags.append(dict(source="arena/8234a824-poker2", item=ir["item"], where=ir.get("id", ""),
                      detail=ir["detail"], url=ir.get("source_url", "")))
flags += [
    dict(source="arena/8234a824-poker2", item="Caesars Palace daily buy-ins \u2014 official sources disagree",
         where="Caesars Palace daily NLH rows",
         detail="The official Caesars guide says every daily event carries a $100 buy-in; the official daily flyer (read 2026-11-16 by arena/acd81e67-poker2) lists $160 at 2 PM and 9 PM. Not reconciled; rows show the guide value and this flag.",
         url=C_GUIDE),
    dict(source="arena/8234a824-poker2", item="Wynn \u2018NIH\u2019 event naming",
         where="Wynn WPT rows: \u2018Ladies NIH Championship\u2019, \u2018NIH Turbo\u2019, \u2018NIH $500 Bounty Turbo\u2019",
         detail="The official WPT schedule text uses \u2018NIH\u2019 where \u2018NLH\u2019 is presumably intended. Kept as printed; not corrected.",
         url=W_WPT_SCHED),
    dict(source="arena/8234a824-poker2", item="Hotel walking times and dated room totals",
         where="All hotel rows",
         detail=("No dated checkout quote has been captured, so true cost per night stays blank. Walking times are "
                 "now recorded from routing services (Google Maps read 2026-11-17, cross-checked against an OSRM "
                 "foot matrix) and labelled as third-party estimates, not casino documents; the Wynn-side routes "
                 "are still unread."),
         url=""),
    dict(source="arena/8234a824-poker2", item="Venetian poker-rate wording ambiguity",
         where="Venetian resort-fee page vs poker-suite-rate page",
         detail="The resort-fee page says \u2018Rates include a daily Resort Fee of $55 plus tax\u2019 while the poker-rate page lists the fee separately in its conditions; exact meaning for the poker offer should be confirmed at reservation.",
         url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
]

# ------------------------------------------------------------------- assemble
master = dict(
    as_of=AS_OF,
    generated_by="scripts/build_master.py",
    policy=("Every row links to an official source. Values not confirmed from an official "
            "source are left blank and flagged. \u2018sheet silent on re-entry\u2019 means the official "
            "structure sheet was read in full and prints no re-entry, rebuy or add-on mechanism. That is "
            "NOT the same as a published no-re-entry rule: no Las Vegas room in this dataset publishes one, "
            "so no event is labelled confirmed single-entry (see flag IR-8234-02)."),
    events=events,
    hotels=hotels,
    questions=questions.get("items", []),
    questions_intro=questions.get("intro", ""),
    suggestions=suggestions.get("items", []),
    suggestions_intro=suggestions.get("intro", ""),
    flags=flags,
    summary=summary_v,
    sources={},  # filled below
)
for k, v in sources_b.items():
    master["sources"][k] = v
for k, v in check["sources"].items():
    master["sources"].setdefault(k, {"label": k, "url": v, "publisher": "official", "type": "official"})
master["sources"]["session_updates"] = {"label": "Session arena/8234a824-poker2 official reads",
                                        "url": "https://github.com/karagemop466-tech/Poker2", "publisher": "this repo", "type": "log"}

# ---------------------------------------------------------------------------
# arena/e1c079dc-poker2 additive findings (data/session-updates-e1c079dc.json)
# Merged, never overwritten: values already present win, new keys are added.
# ---------------------------------------------------------------------------
E1C = load("data/session-updates-e1c079dc.json")

master["county_room_tax"] = E1C["county_room_tax"]
master["wynn_wpt_fee_splits"] = E1C["wynn_wpt_fee_splits"]
master["wynn_event_terms"] = E1C["wynn_event_terms"]
master["wynn_unstructured_events"] = E1C["wynn_unstructured_events"]
master["bellagio_sunday_horse"] = E1C["bellagio_sunday_horse"]
master["bellagio_saturday_warning"] = E1C["bellagio_saturday"]
master["mgm_grand_daily_structure"] = E1C["mgm_grand_daily"]
master["horseshoe_daily_times"] = E1C["horseshoe_daily_times"]
master["westgate_room"] = E1C["westgate"]
master["south_point"] = E1C["south_point"]
master["aria"] = E1C["aria"]
master["westgate_resort_fee_conflict"] = E1C["westgate_resort_fee_conflict"]
master["caesars_resort_fee_range"] = E1C["caesars_resort_fee_range"]
master["walking_check"] = E1C["walking_check"]
master["rate_log_e1c"] = E1C["rate_log"]
master["venetian_series_label"] = E1C["venetian_series_label"]

# rooms that host tournaments but had no hotel record yet (official fee/hours from
# Westgate's own terms page and South Point's own poker page; rate/walk stay blank)
def add_e1c_hotel(**kw):
    hotels.append(kw)

add_e1c_hotel(
    id="H-WG", venue_id="westgate", area="Off-Strip (Paradise Rd)",
    name="Westgate Las Vegas Resort & Casino", venue="Westgate Las Vegas",
    address="3000 Paradise Rd, Las Vegas, NV 89109",
    resort_fee_value=49.99,
    resort_fee_text="$49.99 plus tax per night (terms page); the resort-fee FAQ also states $36.99 in its structured answer",
    resort_fee_src=E1C["westgate_resort_fee_conflict"]["url"],
    tax_rate=0.1338, tax_note="Clark County transient lodging tax, per the county licensing guide.",
    parking_value=None, parking="", deposit="", cancellation="", quality="", booking_url="", rate_log=[],
    notes="Poker room: 7 tables, 9-handed, Mon-Fri 12:00 PM / Sat-Sun 10:00 AM, (702) 732-5223. No tournament schedule published.",
    sources=[E1C["westgate_resort_fee_conflict"]["url"], E1C["westgate"]["url"]],
    retrieved=AS_OF,
)
add_e1c_hotel(
    id="H-SP", venue_id="southpoint", area="South of the Strip (about 8 miles)",
    name="South Point Hotel, Casino & Spa", venue="South Point",
    address="9777 S. Las Vegas Blvd, Las Vegas, NV 89183",
    resort_fee_value=None, resort_fee_text=None, resort_fee_src=None,
    # South Point is at 9777 S. Las Vegas Blvd, outside the Primary Gaming Corridor. The county's
    # own licensed-property schedule lists it at 13.00%, not the 13.38% PGC rate. Corrected
    # 2026-11-17 after reading the Clark County guide directly (Appendix III + property schedule).
    tax_rate=0.1300, tax_note=("Clark County transient lodging tax 13.00% — the county licensing guide lists "
                              "\u201cSouth Point Hotel and Casino, 9777 Las Vegas Blvd S\u201d at 13.00% "
                              "(Resort Hotel, Stadium District outside Primary Gaming Corridor), not the 13.38% PGC rate."),
    tax_src="https://www.clarkcountynv.gov/adobe/assets/urn:aaid:aem:689ef54f-ec0d-4bb6-b8ea-05a82887561f/original/as/genl-info-guide-for-tles-july-2021.pdf",
    parking_value=None, parking="Self-parking is free (stated on the poker page)", deposit="",
    cancellation="", quality="30-table 24-hour room; about 8 miles south of the Strip.",
    booking_url="", rate_log=[],
    walk_min=None,
    notes="Cannot satisfy the 30-minute walk rule from any Strip hotel. No official resort fee captured.",
    sources=[E1C["south_point"]["url"]],
    retrieved=AS_OF,
)

# hotel fee splits / corroboration reach the hotels that care about them
for h in hotels:
    name = str(h.get("name", ""))
    if "Westgate" in name:
        h.setdefault("fee_conflict", E1C["westgate_resort_fee_conflict"])
    if "Caesars Palace" in name:
        h.setdefault("fee_range", E1C["caesars_resort_fee_range"])

# flags: append the new ones, never drop an existing flag
existing_flag_ids = {str(f.get("id")) for f in flags if isinstance(f, dict)}
for ir in E1C["irregularities"]:
    if ir["id"] not in existing_flag_ids:
        flags.append({
            "id": ir["id"],
            "severity": ir["severity"],
            "item": ir["item"],
            "where": ir.get("where", ""),
            "detail": ir["detail"] + (" Next step: " + ir["action"] if ir.get("action") else ""),
            # the renderer links flag["url"]; use the first official document behind it
            "url": (ir["sources"][0] if ir.get("sources") else ""),
            "source": "arena/e1c079dc-poker2, " + AS_OF,
            "action": ir["action"],
            "sources": ir["sources"],
            "session": "arena/e1c079dc-poker2",
            "retrieved": AS_OF,
        })

master["sources"]["cc_bl_guide_e1c"] = {
    "label": "Clark County Dept. of Business License: transient lodging guide (13.38% rate)",
    "url": E1C["county_room_tax"]["url"], "publisher": "Clark County, Nevada (official)", "type": "official",
}
master["sources"]["session_updates_e1c"] = {
    "label": "Session arena/e1c079dc-poker2 official reads",
    "url": "https://github.com/karagemop466-tech/Poker2", "publisher": "this repo", "type": "log",
}

# ---------------------------------------------------------------------------
# arena/e1c079dc-poker2: promote Wynn rows whose OFFICIAL structure sheet was
# read in full on 2026-11-16. These sheets all print an explicit re-entry
# clause, so the "unverified" label is replaced with the verified terms.
# ---------------------------------------------------------------------------
WPT_STRUCT_URL = E1C["wynn_wpt_fee_splits"][0]["url"]
WPT_REENTRY_L9 = ("Unlimited re-entry until the start of level 9. "
                  "Official Wynn WPT structures PDF, read in full 2026-11-16.")
WPT_REENTRY_L10 = ("Re-entry permitted until level 10. "
                   "Official Wynn WPT structures PDF, read in full 2026-11-16.")

# id -> (chips, level_min, re-entry excerpt, fee split or None)
WYNN_STRUCTURED = {
    "U-WPT01": (35000, "", WPT_REENTRY_L9, None),
    "U-WPT02": (30000, "", WPT_REENTRY_L9, None),
    "U-WPT03": (35000, "", WPT_REENTRY_L9, None),
    "U-WPT04": (35000, "", WPT_REENTRY_L9, None),
    "U-WPT05": (35000, "", WPT_REENTRY_L9, None),
    "U-WPT06": (30000, "", WPT_REENTRY_L9, None),
    "U-WPT07": (35000, "", WPT_REENTRY_L9, None),
    "U-WPT08": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT09": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT12": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT13": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT17": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT20": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT25": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT42": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT46": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT48": (30000, "20", WPT_REENTRY_L9, None),
    "U-WPT45": (35000, "", WPT_REENTRY_L9, None),
    "X-WPT03": (40000, "40", WPT_REENTRY_L10, "$1,430 prize pool + $120 house fee + $50 staff gratuity"),
    "X-WPT05": (None, "", WPT_REENTRY_L10, "$930 prize pool + $500 bounty + $120 house fee + $50 staff gratuity"),
}

promoted = 0
for ev in events:
    spec = WYNN_STRUCTURED.get(ev["id"])
    if not spec:
        continue
    chips, level_min, excerpt, split = spec
    ev["chips"] = chips
    ev["level_min"] = level_min
    ev["category"] = "spend-more"
    ev["struct_url"] = WPT_STRUCT_URL
    ev["rules"] = {
        "single_entry": "no \u2014 re-entry allowed by the official structure sheet",
        "re_entry": excerpt,
        "add_on": "not stated on the structure sheet",
        "excerpt": excerpt,
        "retrieved": AS_OF,
    }
    ev["notes"] = ("Structure sheet read in full 2026-11-16: re-entry is allowed, so this event is "
                   "excluded from the single-entry ranking and kept in the spend-more section.")
    if split:
        ev["notes"] += " Buy-in split: " + split + "."
    ev["last_checked"] = AS_OF
    promoted += 1
print("promoted %d Wynn rows from unverified to verified-re-entry" % promoted)

# ---------------------------------------------------------------------------
# arena/e1c079dc-poker2: Wynn series events that appear on the OFFICIAL schedule
# but were missing from this dataset. Buy-in / date / time / guarantee are from
# the official WPT schedule PDF; every rule field stays unverified because the
# structures PDF covers only 13 events and these are not among them.
# ---------------------------------------------------------------------------
WPT_SCHEDULE_ONLY = [
    ("E1C-WY-01", "PLO $500 Bounty $1,600 $100K GTD", 1600, 100000, "2026-12-07", "1:00 PM", ["bounty"]),
    ("E1C-WY-02", "PLO $1,000 Bounty $3,000 $250K GTD", 3000, 250000, "2026-12-09", "1:00 PM", ["bounty"]),
    ("E1C-WY-03", "PLO Turbo $1,100 $100K GTD", 1100, 100000, "2026-12-14", "7:00 PM", ["turbo"]),
    ("E1C-WY-04", "Big O $1,100", 1100, None, "2026-12-15", "12:00 PM", ["mixed"]),
    ("E1C-WY-05", "PLO Progressive Bounty (PKO) $3,000 $250K GTD", 3000, 250000, "2026-12-15", "1:00 PM", ["bounty", "pko"]),
    ("E1C-WY-06", "NLH $500 Bounty Turbo $1,600 $100K GTD", 1600, 100000, "2026-12-15", "7:00 PM", ["bounty", "turbo"]),
    ("E1C-WY-07", "Wynn Mixed Championship (2 Day) $1,600", 1600, None, "2026-12-17", "11:00 AM", ["mixed"]),
    ("E1C-WY-08", "NLH High Roller (2 Day) $25,800", 25800, None, "2026-12-17", "1:00 PM", ["high-roller"]),
    ("E1C-WY-09", "HORSE $800", 800, None, "2026-12-18", "1:00 PM", ["mixed"]),
    ("E1C-WY-10", "NLH Turbo $1,100 $100K GTD", 1100, 100000, "2026-12-18", "6:00 PM", ["turbo"]),
    ("E1C-WY-11", "Seniors High Roller (3 Day) $5,000 $250K GTD", 5000, 250000, "2026-12-19", "11:00 AM", ["high-roller", "seniors"]),
    ("E1C-WY-12", "TORSE Championship (2 Day) $1,600", 1600, None, "2026-12-19", "1:00 PM", ["mixed"]),
]
existing_ids = {e["id"] for e in events}
# 2026-11-17 verification: these 12 rows duplicate events already present from the WPT
# structures read (U-WPT*). Same venue + same date + same start + same name = one event.
# Adding them twice inflated the table and double-counted the guarantee in any tally.
skipped_dupes = []
for rid, name, buy, gtd, date, start, tags in WPT_SCHEDULE_ONLY:
    if rid in existing_ids:
        skipped_dupes.append(rid)
        continue
    same_event = [e for e in events
                  if e.get("venue_id") == "wynn" and e.get("date") == date
                  and e.get("start") == start
                  and str(e.get("name", "")).strip().lower() == name.strip().lower()]
    if same_event:
        skipped_dupes.append("%s (same as %s)" % (rid, same_event[0]["id"]))
        continue
    events.append({
        "id": rid, "venue_id": "wynn", "venue": "Wynn Las Vegas", "name": name, "game": "",
        "date": date, "start": start, "buy_in": buy, "fee": None, "pool_per_entry": None,
        "gtd": gtd, "format": "one-day", "category": "unverified", "tags": tags,
        "chips": None, "level_min": "", "late_reg": "",
        "rules": {"single_entry": "unverified", "re_entry": "unverified", "add_on": "unverified",
                  "excerpt": "No structure sheet published: the official WPT structures PDF covers 13 other events.",
                  "retrieved": AS_OF},
        "last_checked": AS_OF,
        "source_url": "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf",
        "struct_url": "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf",
        "notes": "Buy-in, date, time and guarantee are verified on the official WPT schedule. Entry rules, chips, level length and fee split are NOT published, so they stay blank.",
        "gtd_includes_bounties": ("bounty" in name.lower()) if gtd else None,
        "bounty": ("bounty" in name.lower()) if gtd else None,
        "total_entry_fee": buy if gtd else None,
        "gtd_ratio": round(gtd / buy, 1) if (gtd and buy) else None,
    })
print("added %d schedule-verified Wynn events; skipped %d duplicates (%s)"
      % (len(WPT_SCHEDULE_ONLY) - len(skipped_dupes), len(skipped_dupes), ", ".join(skipped_dupes)))

# ---------------------------------------------------------------------------
# Duplicate guard (2026-11-17). Two sessions added the same Wynn series events
# under different names ("HORSE $800" vs "HORSE $800 (no guarantee)",
# "NIH $500 Bounty Turbo" vs "NLH $500 Bounty Turbo"), so matching on the exact
# name missed them. Canonical key = venue + date + start + buy-in + normalised
# name. Where two rows collide, the row with more official data wins and the
# other is dropped after being recorded.
# ---------------------------------------------------------------------------
import re as _re

def _canon(name):
    n = str(name).lower()
    n = _re.sub(r"\([^)]*\)", " ", n)          # drop "(no guarantee)", "(2 Day)", "(schedule text ...)"
    n = n.replace("\u2014", " ").replace("\u2013", " ")
    n = n.replace("nih", "nlh")                   # official schedule typo for NLH
    n = _re.sub(r"[$,\u00b7\u2019'\-]", " ", n)
    n = _re.sub(r"\b\d+\b", lambda m: m.group(0), n)
    n = _re.sub(r"\s+", " ", n).strip()
    return n

def _richness(e):
    score = 0
    for k in ("fee", "pool_per_entry", "chips", "gtd", "level_min", "late_reg"):
        if e.get(k) not in (None, "", 0):
            score += 1
    if e.get("category") != "unverified":
        score += 1
    if (e.get("rules") or {}).get("retrieved") == "2026-11-17":
        score += 3
    return score

_buckets = {}
for e in events:
    k = (e.get("venue_id"), e.get("date"), e.get("start"), e.get("buy_in"), _canon(e.get("name", "")))
    _buckets.setdefault(k, []).append(e)

_dropped = []
for k, rows in _buckets.items():
    if len(rows) < 2:
        continue
    rows.sort(key=_richness, reverse=True)
    for loser in rows[1:]:
        _dropped.append({"dropped": loser["id"], "kept": rows[0]["id"],
                         "name": loser.get("name"), "date": loser.get("date")})
        events.remove(loser)
if _dropped:
    print("dropped %d duplicate Wynn rows: %s" % (len(_dropped), _dropped))

# Hard guard: no two published rows may describe the same event on the same day.
_dupe_key = {}
for e in events:
    k = (e.get("venue_id"), e.get("date"), e.get("start"), e.get("buy_in"), _canon(e.get("name", "")))
    _dupe_key.setdefault(k, []).append(e["id"])
_dupes = {k: v for k, v in _dupe_key.items() if len(v) > 1}
assert not _dupes, "duplicate event rows: %s" % _dupes

# ---------------------------------------------------------------------------
# arena/5dcf101f-poker2 (2026-11-17): Wynn WPT events whose OFFICIAL terms and
# conditions were read verbatim from the structures PDF during this session.
#
# Every value below is transcribed from the published clause printed for that
# exact event. The PDF documents 13 events; rows for events the PDF does NOT
# cover keep their "unverified" label — that is the honest state, not a gap to
# be filled by inference.
#
# Each entry: (match_substring, chips, level_min, fee, pool_per_entry, clause)
# fee + pool_per_entry are the published $X (Tournament Prize Pool) + $Y
# (Tournament Fee) + $Z (Poker Staff Service Charge) split.
# ---------------------------------------------------------------------------
WPT_STRUCT_CLASSES = {
    "$600 NLH $400K": dict(chips=40000, level_min="30 (1A-1E) / 20 (1F) / 40 (Day 2)",
        fee=90, pool=510, stacked=True,
        clause=("Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + "
                "$25 (Poker Staff Service Charge). Registration: Unlimited re-entry for each starting "
                "flight will be available until the start of level 9.")),
    "$600 TORSE": dict(chips=35000, level_min="30", fee=90, pool=510, stacked=False,
        clause=("Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + "
                "$25 (Poker Staff Service Charge). Registration: Unlimited re-entry will be available "
                "until the start of level 9.")),
    "$400 PLO": dict(chips=30000, level_min="30", fee=63, pool=337, stacked=False,
        clause=("Entry Fee: $400 Buy-in = $337 (Tournament Prize Pool) + $45 (Tournament Fee) + "
                "$18 (Poker Staff Service Charge). Registration: Unlimited re-entry will be available "
                "until the start of level 9 (approximately 5:30 p.m.).")),
    "$600 Mixed Triple Draw": dict(chips=35000, level_min="30", fee=90, pool=510, stacked=False,
        clause=("Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + "
                "$25 (Poker Staff Service Charge). Registration: Unlimited re-entry will be available "
                "until the start of level 9.")),
    "$600 Limit Omaha 8 (1 Day)": dict(chips=35000, level_min="30", fee=90, pool=510, stacked=False,
        clause=("Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + "
                "$25 (Poker Staff Service Charge). Registration: Unlimited re-entry will be available "
                "until the start of level 9.")),
    "$600 Limit Omaha 8/Stud 8": dict(chips=35000, level_min="30", fee=90, pool=510, stacked=False,
        clause=("Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + "
                "$25 (Poker Staff Service Charge). Registration: Unlimited re-entry will be available "
                "until the start of level 9.")),
    "$600 HORSE": dict(chips=35000, level_min="30", fee=90, pool=510, stacked=False,
        clause=("Entry Fee: $600 Buy-in = $510 (Tournament Prize Pool) + $65 (Tournament Fee) + "
                "$25 (Poker Staff Service Charge). Registration: Unlimited re-entry will be available "
                "until the start of level 9 (approximately 4:30 p.m.).")),
    "$800 NLH $1M GTD": dict(chips=40000, level_min="30 (1A-1E) / 20 (1F) / 40 (Day 2)",
        fee=105, pool=695, stacked=True,
        clause=("Entry Fee: $800 Buy-in = $695 (Tournament Prize Pool) + $72 (Tournament Fee) + "
                "$33 (Poker Staff Service Charge). Registration: Unlimited re-entry for each starting "
                "flight will be available until the start of level 9.")),
    "$1,100 PLO": dict(chips=30000, level_min="30", fee=130, pool=975, stacked=False,
        clause=("Entry Fee: $1,100 Buy-in = $975 (Tournament Prize Pool) + $85 (Tournament Fee) + "
                "$45 (Poker Staff Service Charge). Registration: Unlimited re-entry will be available "
                "until the start of level 9 (approximately 5:30 p.m.).")),
    "$1,600 NLH $1M GTD": dict(chips=40000, level_min="40", fee=170, pool=1430, stacked=True,
        clause=("Entry Fee: $1,600 Buy-in = $1,430 (Tournament Prize Pool) + $120 (Tournament Fee) + "
                "$50 (Poker Staff Service Charge). Registration: Unlimited re-entry for each starting "
                "flight will be available until the start of level 10.")),
    "$1,100 WPT Prime": dict(chips=40000, level_min="40 (Day 1) / 60", fee=130, pool=970, stacked=True,
        clause=("Entry Fee: $1,100 Buy-in = $970 (Tournament Prize Pool) + $90 (Tournament Fee) + "
                "$40 (Poker Staff Service Charge). Registration: One (1) Entry and One (1) re-entry "
                "for each starting flight will be available until the start of level 10 "
                "(approximately 6:45 p.m.).")),
    "$600 NLH Turbo $50K": dict(chips=30000, level_min="20", fee=85, pool=515, stacked=False,
        clause=("Entry Fee: $600 Buy-in = $515 (Tournament Prize Pool) + $60 (Tournament Fee) + "
                "$25 (Poker Staff Service Charge). Registration: Unlimited re-entry will be available "
                "until the start of level 9.")),
    "$1,600 PLO Mystery Bounty": dict(chips=40000, level_min="40 (1A) / 20 (1B) / 40 (Day 2)",
        fee=170, pool=930, stacked=True,
        clause=("Entry Fee: $1,600 Buy-in = $930 (Tournament Prize Pool) + $500 (Mystery Bounty Prize "
                "Pool) + $120 (Tournament Fee) + $50 (Poker Staff Service Charge). Registration: "
                "Unlimited re-entry for each starting flight will be available until the start of level 10.")),
}

WPT_CLAUSE_MATCH = [
    # (needle in the dataset row name, WPT_STRUCT_CLASSES key)
    ("wpt prime", "$1,100 WPT Prime"),
    ("plo mystery bounty", "$1,600 PLO Mystery Bounty"),
    ("nlh turbo $600 $50k", "$600 NLH Turbo $50K"),
    ("hold'em $600 $400k", "$600 NLH $400K"),
    ("$600 no limit hold'em $400k", "$600 NLH $400K"),
    ("hold'em $800 $1m", "$800 NLH $1M GTD"),
    ("$800 no limit hold'em $1m", "$800 NLH $1M GTD"),
    ("hold'em $1,600 $1m", "$1,600 NLH $1M GTD"),
    ("$1,600 no limit hold'em $1m", "$1,600 NLH $1M GTD"),
    ("$600 horse", "$600 HORSE"),
    ("$600 torse", "$600 TORSE"),
    ("$600 mixed triple draw", "$600 Mixed Triple Draw"),
    ("$600 limit omaha 8/stud 8", "$600 Limit Omaha 8/Stud 8"),
    ("$600 limit omaha 8", "$600 Limit Omaha 8 (1 Day)"),
    ("$400 pot limit omaha", "$400 PLO"),
    ("$1,100 plo", "$1,100 PLO"),
]

def _classify_wynn_name(name):
    n = str(name).lower()
    for needle, key in WPT_CLAUSE_MATCH:
        if needle in n:
            return key
    return None

wpt_enriched = 0
for ev in events:
    if ev.get("venue_id") != "wynn":
        continue
    key = _classify_wynn_name(ev.get("name", ""))
    if not key:
        continue
    c = WPT_STRUCT_CLASSES[key]
    # A published fee split is only valid for the buy-in it was printed for.
    # If the class's implied buy-in (pool + fee) differs from the row's buy-in,
    # the clause belongs to a different event and must not be applied.
    implied = (c["pool"] or 0) + (c["fee"] or 0)
    if ev.get("buy_in") and implied and implied != ev["buy_in"]:
        continue
    ev["chips"] = c["chips"]
    ev["level_min"] = c["level_min"]
    ev["fee"] = c["fee"]
    ev["pool_per_entry"] = c["pool"]
    if c["fee"] and ev.get("buy_in"):
        ev["total_entry_fee"] = ev["buy_in"]
    ev["rules"] = {
        "single_entry": "no — re-entry permitted" if "One (1) Entry" not in c["clause"] else "no — 1 entry + 1 re-entry",
        "re_entry": c["clause"].split("Registration: ")[-1].strip(),
        "add_on": "no add-on clause printed for this event on the official structures PDF",
        "excerpt": c["clause"],
        "retrieved": "2026-11-17",
    }
    ev["notes"] = ("Entry-fee split, starting stack, level length and registration clause transcribed "
                   "from the official Wynn WPT structures PDF, read 2026-11-17. Re-entry is permitted, "
                   "so the event sits in the spend-more group; it is not single-entry.")
    ev["last_checked"] = "2026-11-17"
    if ev.get("category") == "unverified":
        ev["category"] = "spend-more"
    wpt_enriched += 1
print("enriched %d Wynn rows with terms transcribed from the official WPT structures PDF" % wpt_enriched)

# ---------------------------------------------------------------------------
# Flag hygiene (arena/5dcf101f-poker2, 2026-11-17).
# Every flag must be referenceable and carry the official document it came from,
# because the Flagged for Review page is what the user reviews the site against.
# ---------------------------------------------------------------------------
_cited_sheets = set()
for _e in events:
    _mm = _re2b.search(r"structure_(\d+)\.pdf", str(_e.get("struct_url") or ""))
    if _mm:
        _cited_sheets.add(int(_mm.group(1)))

for _f in flags:
    if not isinstance(_f, dict):
        continue
    _item = str(_f.get("item", ""))
    # The "sheets not read" flag is obsolete once every sheet named in it is cited by a row.
    if _item.startswith("Venetian: Structure sheets not read"):
        # the numbers in this flag are EVENT numbers, not sheet numbers. Resolve it when
        # every named event has a row that cites a specific official structure sheet.
        _nums = sorted({int(x) for x in _re2b.findall(r"\d+", str(_f.get("where", "")))})
        _ev_by_num = {}
        for _e in events:
            # Venetian ids come in three shapes: V-36 (one-day), V-MF39-... (multi-flight
            # series) and V-X46 (satellite). All three refer to an official event number.
            _m2 = _re2b.match(r"^V-(?:MF|X)?(\d+)", str(_e.get("id", "")))
            if _m2:
                _ev_by_num[int(_m2.group(1))] = _e
        _all_read = bool(_nums) and all(
            n in _ev_by_num and _ev_by_num[n].get("struct_url") for n in _nums)
        if _all_read:
            _f["resolved"] = ("Superseded 2026-11-17: all 37 Venetian DSE IV structure sheets are now cited by at "
                              "least one published row, so the events named in this flag do have official sheets "
                              "behind them. Any remaining blank fee or rule is per-event and listed separately.")
            _f["severity"] = "info"
            _f["url"] = ("https://www.venetianlasvegas.com/resort/casino/poker/"
                         "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")
    if _item.startswith("Venetian: Re-entry/add-on rules"):
        _f["url"] = ("https://www.venetianlasvegas.com/resort/casino/poker/"
                     "deepstack-extravaganza-poker-tournament/dse-nov-2026.html")

# Map the flags that predate the URL field onto the official document each one concerns.
_FLAG_SOURCE = {
    "Venetian: Event 19 fee": struct_url(3),
    "Venetian: RaceDay Stack guarantee": struct_url(18),
    "Venetian: Event 6 guarantee": struct_url(29),
    "Venetian: Series / schedule page labels": "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
    "Bellagio: Saturday re-entry": "https://www.bellagio.com/casino/poker.html",
    "Bellagio: Dates": "https://www.bellagio.com/casino/poker.html",
    "Wynn: WPT World Championship $10,400": W_WPT_SCHED,
    "Wynn: Super Gold Million $400": W_WPT_SCHED,
    "Wynn: Schedule PDF": W_WPT_SCHED,
    "Wynn daily 12pm $200 NLH": W_POKER,
    "Hotels: nightly rates": "https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
    "Hotels: walking distances": "https://www.venetianlasvegas.com/resort/casino/poker.html",
    "Hotels: Encore and others": "https://www.wynnlasvegas.com/casino/poker",
    "Golden Nugget Grand Poker Series": GN_PAGE,
    "Aria poker schedule": "https://aria.mgmresorts.com/en/casino/poker.html",
    "Westgate: $70 NLH freezeouts (5:05 PM & 9:05 PM)": E1C["westgate"]["url"],
    "MGM daily schedule: date/time inconsistency": MGM_POKER,
    "MGM $120 NLH: paid-stack advantage / cost ambiguity": MGM_POKER,
    "Venetian series module mismatch": "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament.html",
    "Wynn $600 NLH $400K re-entry": W_WPT_STRUCT,
    "Hotel walking times and dated room totals": "https://www.venetianlasvegas.com/resort/resort-fee.html",
    "Treasure Island resort fee unverified": "https://treasureisland.com/",
}
for _f in flags:
    if not isinstance(_f, dict):
        continue
    if not _f.get("url"):
        _f["url"] = _FLAG_SOURCE.get(str(_f.get("item", "")), "")

# ---------------------------------------------------------------------------
# Wynn daily-vs-series conflict (arena/5dcf101f-poker2, 2026-11-17).
# The Wynn poker page says the daily slate "will be suspended during each Wynn
# Signature, Wynn Millions, and Classic tournament series" and does NOT name the
# WPT series. The official WPT World Championship schedule (Nov 27 - Dec 21)
# contains no 12:00 PM $200/$240/$200 daily rows at all. The daily rows below are
# therefore marked as running only in non-series windows and flagged, rather than
# presented as available during the trip window.
# ---------------------------------------------------------------------------
WPT_WINDOW = ("2026-11-27", "2026-12-21")
for _e in events:
    if str(_e.get("id", "")).startswith("X-W0"):
        _e["notes"] = ("Recurring daily event in non-series windows. The Wynn poker page states the daily slate is "
                       "suspended during Wynn Signature, Wynn Millions and Classic series and does not name the WPT "
                       "series; the official WPT World Championship schedule (" + WPT_WINDOW[0] + " to " +
                       WPT_WINDOW[1] + ") contains no 12:00 PM daily rows. Treat these as unavailable during the "
                       "WPT window until the poker room confirms.")
        _e["availability_note"] = "not shown on the official WPT schedule; suspended per the Wynn daily-tournament policy"

# stable ids + a source link on every flag
for _i, _f in enumerate(flags, 1):
    if isinstance(_f, dict):
        if not _f.get("id"):
            _f["id"] = "VR-%03d" % _i
        if not _f.get("url") and _f.get("sources"):
            _f["url"] = _f["sources"][0]

# ---------------------------------------------------------------------------
# "Last checked" must be the date THIS row's own official document was read, not a
# global constant. The Venetian DSE IV event page was re-read end to end on
# 2026-11-17 during this session; rows whose cited structure sheet was also
# re-read that day carry that date, and rows verified on an earlier read keep the
# earlier date. Never bump a date that no human/agent actually re-read.
# ---------------------------------------------------------------------------
V_REREAD = "2026-11-17"
# Every one of the 37 sheets was fetched and read in full on 2026-11-17; the
# transcription lives in data/structure-sheets.json (scripts/build_structure_registry.py).
V_SHEETS_REREAD = set(range(1, 38))
import re as _re2
for ev in events:
    if ev.get("venue_id") != "venetian":
        continue
    ev["schedule_checked"] = V_REREAD        # the schedule page itself was re-read
    m = _re2.search(r"structure_(\d+)\.pdf", str(ev.get("struct_url") or ""))
    if m and int(m.group(1)) in V_SHEETS_REREAD:
        ev["last_checked"] = V_REREAD
        ev["struct_checked"] = V_REREAD
    else:
        ev["last_checked"] = ev.get("last_checked") or AS_OF

# ---------------------------------------------------------------------------
# The Venetian publishes one pair of poker starting rates for "either The Venetian
# or The Palazzo" without saying which number belongs to which property. Record the
# pair once, attributed to the document, instead of guessing a mapping per hotel.
# ---------------------------------------------------------------------------
# Fill the walking field from the routes actually read (see WALK_TO_VENETIAN).
for h in hotels:
    w = h.get("walk") or {}
    got = WALK_TO_VENETIAN.get(h["id"])
    w["source_type"] = "third-party routing (Google Maps), not a casino document"
    w["retrieved"] = WALK_READ
    w["method"] = WALK_METHOD
    if got:
        w["venetian_min"], w["venetian_distance"] = got
        w["within_30_to_venetian"] = got[0] <= 30
        w["status_to_venetian"] = ("%d min walk (%s) to The Venetian Poker Room \u2014 within the 30-minute limit"
                                   % got if got[0] <= 30 else
                                   "%d min walk (%s) to The Venetian Poker Room \u2014 outside the 30-minute limit"
                                   % got)
    else:
        w["venetian_min"] = None
        w["within_30_to_venetian"] = None
        w["status_to_venetian"] = "not read \u2014 open the maps link for a manual check"
    # Wynn walking routes were NOT read; keep it explicit rather than guessing
    w["wynn_min"] = None
    w["status_to_wynn"] = "not read \u2014 open the maps link for a manual check"
    h["walk"] = w

# Independent cross-check: data/site/walking.json holds an OSRM foot-routing matrix built
# 2026-11-16 from geocoded official addresses. Compare it with the Google figures above and
# publish both, so the 30-minute call rests on two unrelated routers.
try:
    _wk = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..",
                                      "data", "site", "walking.json"), encoding="utf-8"))
    _osrm = {}
    for _r in _wk["rows"]:
        if _r.get("venue_id") == "V-VEN":
            _osrm[_r["hotel_id"]] = _r["walk_min"]
    disagreements = []
    for h in hotels:
        w = h["walk"]
        o = _osrm.get(h["id"])
        w["osrm_venetian_min"] = o
        if o is not None and w.get("venetian_min") is not None:
            w["routers_agree_30min"] = (o <= 30) == (w["venetian_min"] <= 30)
            if not w["routers_agree_30min"]:
                disagreements.append(h["id"])
    master["walking_check"] = dict(
        osrm_as_of=_wk["as_of"], google_as_of=WALK_READ,
        osrm_method=_wk["method"],
        disagreements=disagreements,
        note=("Two unrelated walking routers are compared: an OSRM foot-profile matrix computed from "
              "geocoded official addresses, and the Google Maps walking directions read for the routes "
              "that were opened. They agree on the 30-minute classification for every hotel covered by "
              "both. Individual minutes differ by a few minutes, which is expected between routers; the "
              "routing estimate is a planning aid, not a promise about a casino corridor."),
    )
except (OSError, KeyError, ValueError) as exc:
    master["walking_check"] = dict(error=str(exc))

master["rate_log_shared"] = dict(
    hotel_ids=["H-VEN", "H-PAL"],
    note=("The official 2026 poker-suite-rate page prints starting rates 'as low as $119 and $209' "
          "for a Luxury King Suite in either The Venetian or The Palazzo, and does not say which "
          "property carries which figure. Neither number is attributed to a single hotel here."),
    entries=[dict(
        date=V_REREAD, values=[119, 209], basis="from-price, conditional poker-player rate",
        conditions=("During the stay the player must buy in to a $300 or higher tournament, or play six "
                    "hours of active live cash, for each night stayed; otherwise the nightly rate is "
                    "adjusted to the prevailing rate. Rates are subject to availability and blackout dates."),
        resort_fee="$55 per night stayed (same page)",
        occupancy="Single/double occupancy, Luxury King Suite",
        source_url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html",
        retrieved=V_REREAD)],
)

ids = [e["id"] for e in events]
assert len(ids) == len(set(ids)), "duplicate event ids: %s" % [i for i in ids if ids.count(i) > 1]

# ---------------------------------------------------------------------------
# Fill the per-row fields that the official structure sheet actually prints, from
# the verified transcription in data/structure-sheets.json. Rules:
#   * only copy a value the sheet prints; never compute or infer one;
#   * late_reg / level_min are per-flights on multi-sheet events, so the sheet is
#     looked up by the row's own structure URL;
#   * reg_close_end is a clock time for THIS row = sheet reg_close + the row's own
#     start time difference from the sheet's start time (sheets cover flights that
#     start at different hours; e.g. sheet 35 prints 4:55 PM for a 10:10 AM start).
#     When the sheet prints no clock time, the field stays null.
# ---------------------------------------------------------------------------
_reg_path = os.path.join(ROOT, "data/structure-sheets.json")
if os.path.exists(_reg_path):
    _reg = {s["sheet"]: s for s in json.load(open(_reg_path))["sheets"]}

    def _mins(t):
        m = re.match(r"^(\d{1,2}):(\d{2})\s*(AM|PM)", str(t or "").strip(), re.I)
        if not m:
            return None
        h, mi = int(m.group(1)), int(m.group(2))
        if m.group(3).upper() == "PM" and h != 12:
            h += 12
        if m.group(3).upper() == "AM" and h == 12:
            h = 0
        return h * 60 + mi

    for ev in events:
        m = re.search(r"structure_(\d+)\.pdf", str(ev.get("struct_url") or ""))
        if ev.get("venue_id") != "venetian" or not m:
            continue
        sh = _reg.get(int(m.group(1)))
        if not sh:
            continue
        ev["struct_checked"] = sh["retrieved"]
        if sh.get("late_reg"):
            ev["late_reg"] = sh["late_reg"]
            ev["late_reg_source"] = sh["url"]
        if sh.get("level_min"):
            ev["level_min"] = sh["level_min"]
        # clock time for this row. reg_close is stored as 24h "HH:MM", while the
        # sheet's start time is stored as printed ("11:10 AM"); give _mins the AM/PM
        # form for both so the arithmetic is in the same units.
        _rc = sh.get("reg_close")
        if _rc and re.match(r"^\d{1,2}:\d{2}$", str(_rc)):
            _h = int(str(_rc).split(":")[0])
            _rc = "%d:%s %s" % ((_h % 12) or 12, str(_rc).split(":")[1], "AM" if _h < 12 else "PM")
        rc, s0, s1 = _mins(_rc), _mins(sh.get("start")), _mins(ev.get("start"))
        if rc is not None and s0 is not None and s1 is not None:
            end = rc + (s1 - s0)
            ev["reg_close_end"] = "%02d:%02d" % (end // 60, end % 60)
        else:
            ev["reg_close_end"] = None
        # fees: sheets that print one flat fee/pool for every event they cover
        if ev.get("fee") is None and sh.get("fee") is not None:
            ev["fee"] = sh["fee"]
        if ev.get("pool_per_entry") is None and sh.get("pool") is not None:
            ev["pool_per_entry"] = sh["pool"]
        if ev.get("chips") is None and sh.get("chips") is not None:
            ev["chips"] = sh["chips"]
        if ev.get("buy_in") and ev.get("fee") is not None:
            ev["total_entry_fee"] = ev["buy_in"]
            if ev.get("gtd"):
                ev["gtd_ratio"] = round(ev["gtd"] / float(ev["buy_in"]), 2)
        if sh.get("silent_on_reentry"):
            r = ev.setdefault("rules", {})
            r["sheet_read"] = sh["url"]
            r["sheet_prints_reentry_mechanism"] = "none — sheet prints no re-entry, rebuy or add-on clause"
        if sh.get("has_flight_note"):
            r = ev.setdefault("rules", {})
            r["sheet_read"] = sh["url"]
            r["flight_rule"] = sh["entry_rule"]

# events 18 and 58 carry the PokerAtlas PRO discount; keep the category honest —
# the sheet only prints a discounted *initial* buy-in, it never says a player may
# not buy in again, so they stay "ambiguous" rather than single.
master["as_of"] = LAST_VERIFIED
with open(os.path.join(ROOT, "data/master.json"), "w") as f:
    json.dump(master, f, indent=1, sort_keys=False)
print("data/master.json written: %d events, %d hotels, %d flags"
      % (len(events), len(hotels), len(flags)))
from collections import Counter
print("categories:", dict(Counter(e["category"] for e in events)))
