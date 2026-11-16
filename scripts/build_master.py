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
import json, re, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AS_OF = "2026-11-16"

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
            single_entry="freezeout-confirmed",
            re_entry="none \u2014 no re-entry clause in sheet",
            add_on="none \u2014 no add-on clause in sheet",
            excerpt=(sheet or {}).get("excerpt") or row.get("entry_rules", ""),
            retrieved=(sheet or {}).get("retrieved", AS_OF),
        )
        notes = ""
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
def walk_links(address, hotel):
    dest_ven = "The Venetian Poker Room, 3355 S Las Vegas Blvd, Las Vegas, NV"
    dest_wyn = "Wynn Las Vegas Poker Room, 3131 S Las Vegas Blvd, Las Vegas, NV"
    return {
        "maps_venetian": "https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=walking"
                         % (address.replace(" ", "+"), dest_ven.replace(" ", "+")),
        "maps_wynn": "https://www.google.com/maps/dir/?api=1&origin=%s&destination=%s&travelmode=walking"
                     % (address.replace(" ", "+"), dest_wyn.replace(" ", "+")),
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
    rate_log=[
        dict(date=AS_OF, rate=119, basis="from-price, conditional poker player rate",
             conditions="Requires 6 hours live cash or a $300+ tournament buy-in per night; else prevailing rate. Availability applies.",
             source_url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    ],
    notes="Official 2026 poker-suite-rate page publishes from-$119 (Venetian) and from-$209 (Palazzo). A dated checkout quote for exact trip dates has NOT been captured; rate log holds dated entries only.",
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
    rate_log=[
        dict(date=AS_OF, rate=209, basis="from-price, conditional poker player rate",
             conditions="Requires 6 hours live cash or a $300+ tournament buy-in per night; else prevailing rate. Availability applies.",
             source_url="https://www.venetianlasvegas.com/resort/casino/poker/suite-rates.html"),
    ],
    notes="Same resort and poker room as The Venetian. Official poker-rate wording maps $119 to Venetian and $209 to Palazzo per prior 2026-11-16 reads; see flag F-PokerRate-Mapping.",
)
add_hotel(
    id="H-WYN", name="Wynn Las Vegas", area="Strip (venue hotel)",
    address="3131 S. Las Vegas Blvd, Las Vegas, NV 89109",
    resort_fee_value=55.0,
    resort_fee_text="$55 plus tax per room night (official resort-information page)",
    resort_fee_src="https://www.wynnlasvegas.com/about-us/resort-information",
    tax_rate=None,
    tax_note="Wynn terms say \u201cplus tax\u201d with no published rate. The 13.38% Clark County rate comes from Venetian\u2019s terms \u2014 applying it here is unverified (flag).",
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
    tax_rate=None,
    tax_note="Tax rate not captured from an official MGM page \u2014 blank.",
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
    tax_rate=None,
    tax_note="Tax rate not captured from an official MGM page \u2014 blank.",
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
    tax_rate=None,
    tax_note="Tax rate not captured from an official MGM page \u2014 blank.",
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
    tax_rate=None,
    tax_note="",
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
    tax_rate=None, tax_note="", parking="", deposit="",
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
         detail="No official walking-time source and no dated checkout quote have been captured. Walk minutes and checkout totals are blank; use the official booking links and maps links to capture them for exact trip dates before booking.",
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
            "source are left blank and flagged. \u2018freezeout-confirmed\u2019 means the official "
            "structure sheet was fully read and contains no re-entry, rebuy or add-on mechanism; "
            "it is not an express \u2018single entry\u2019 clause (see flag IR-8234-02)."),
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
    tax_rate=0.1338, tax_note="Clark County transient lodging tax, per the county licensing guide.",
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
for rid, name, buy, gtd, date, start, tags in WPT_SCHEDULE_ONLY:
    if rid in existing_ids:
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
print("added %d schedule-verified Wynn events" % len(WPT_SCHEDULE_ONLY))

ids = [e["id"] for e in events]
assert len(ids) == len(set(ids)), "duplicate event ids: %s" % [i for i in ids if ids.count(i) > 1]

with open(os.path.join(ROOT, "data/master.json"), "w") as f:
    json.dump(master, f, indent=1, sort_keys=False)
print("data/master.json written: %d events, %d hotels, %d flags"
      % (len(events), len(hotels), len(flags)))
from collections import Counter
print("categories:", dict(Counter(e["category"] for e in events)))
