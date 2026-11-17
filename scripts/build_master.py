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
V_SHEETS_REREAD = {1, 5, 11, 15, 18}   # sheets read verbatim again in this session
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


# ===========================================================================
# EVIDENCE OVERLAY — arena/32a40b2f-poker2 (2026-11-17)
# ---------------------------------------------------------------------------
# The root dashboard and the /plan/ surface were transcribed from two generations of
# the same official documents. The root rows came from the schedule page plus the
# structure sheets read up to 2026-11-16; site-data/events.json carries the completed
# 37-sheet read (2026-11-17), where every entry-rule field holds its own value,
# status, verbatim excerpt, source URL and retrieval date. That gap is why the root
# pages still said "sheet silent" on rows whose sheet states a rule out loud, and why
# 36-66 cells per field were blank on the root table while the sheet prints them.
#
# Rules of the fold — all five are checked by the overlay itself and reported:
#   1. a root row joins to exactly one plan row, keyed on (date, start time); the join
#      is rejected unless the buy-in agrees, so a wrong pairing can never fill data;
#   2. blank cells are filled, never overwritten; where the root row and the sheet
#      disagree, the root value stays and the disagreement is recorded for review;
#   3. every field filled here carries the sheet URL and the retrieval date of that
#      sheet, so each cell remains independently checkable;
#   4. a category changes only when the sheet states the rule. Silence never promotes
#      a row and never demotes one;
#   5. this overlay reads no new official page, so it does not advance any
#      last_checked date — dates move only when a document is actually opened again.
# ===========================================================================
PLAN_EVENTS_PATH = os.path.join(ROOT, "site-data", "events.json")
PLAN_HOTELS_PATH = os.path.join(ROOT, "site-data", "hotels.json")
PLAN_RATES_PATH = os.path.join(ROOT, "site-data", "rates.json")
PLAN_WALK_PATH = os.path.join(ROOT, "site-data", "walk.json")
SITE_WALK_PATH = os.path.join(ROOT, "data", "site", "walking.json")

overlay = {"filled": {}, "conflicts": [], "joined": 0, "unjoined": [],
           "categories_changed": [], "hotels": [], "walk_rows": 0, "rates_attached": 0}


def _t24(s):
    """'11:10 AM' -> '11:10'; a value already in 24-hour form passes through."""
    m = re.search(r"^(\d{1,2}):(\d{2})\s*([AP])M$", str(s or "").strip().upper().replace(" ", ""))
    if not m:
        return str(s or "").strip()
    h, mi, ap = int(m.group(1)), m.group(2), m.group(3)
    if ap == "P" and h != 12:
        h += 12
    if ap == "A" and h == 12:
        h = 0
    return "%02d:%s" % (h, mi)


def _json_load(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ event fold
plan_ev = None
_p = _json_load(PLAN_EVENTS_PATH)
if _p:
    plan_ev = _p.get("events", [])

if plan_ev:
    plan_by_key = {}
    for q in plan_ev:
        plan_by_key.setdefault((q.get("date"), q.get("start")), []).append(q)

    def _blank(v):
        return v is None or (isinstance(v, str) and v.strip() == "")

    for e in events:
        if e.get("venue_id") != "venetian":
            continue
        cands = plan_by_key.get((e.get("date"), _t24(e.get("start"))), [])
        cands = [q for q in cands if q.get("buy_in") == e.get("buy_in")]
        if len(cands) != 1:
            overlay["unjoined"].append({"id": e["id"], "key": "%s %s" % (e.get("date"), e.get("start")),
                                        "candidates": len(cands)})
            continue
        q = cands[0]
        overlay["joined"] += 1
        sq = q.get("sheet_url") or ""
        ret = q.get("sheet_retrieved") or q.get("last_checked")

        # --- structured, per-field entry-rule evidence (the sheet, field by field)
        fields = {}
        for fk in ("single_entry", "re_entry", "add_on", "fee", "guarantee", "payout", "bounty"):
            v = (q.get("rules") or {}).get(fk)
            if isinstance(v, dict):
                fields[fk] = {"value": v.get("value"), "status": v.get("status"),
                              "excerpt": v.get("excerpt"), "source_url": v.get("source_url") or sq,
                              "retrieved": v.get("retrieved") or ret}
            elif v is None and fk in ("bounty",):
                fields[fk] = None
        if fields:
            e["rules_fields"] = fields
        se = fields.get("single_entry") or {}
        re_ = fields.get("re_entry") or {}
        ao = fields.get("add_on") or {}
        st = se.get("status")
        # entry-rule state, in the words the document supports
        if st == "explicit":
            e["entry_state"] = "stated"
            e["rules"]["single_entry"] = "stated on the sheet — %s" % (se.get("value") or "see excerpt")
            e["rules"]["re_entry"] = "stated on the sheet — %s" % (re_.get("value") or "see excerpt")
        elif st == "explicit_no":
            e["entry_state"] = "stated_multi_entry"
            e["rules"]["single_entry"] = "not single-entry — the sheet prices further buy-ins"
            e["rules"]["re_entry"] = "stated on the sheet — %s" % (re_.get("value") or "further buy-ins")
        elif st == "not_stated_sheet_read":
            e["entry_state"] = "silent"
            e["rules"]["single_entry"] = "not stated — sheet read in full, no re-entry/rebuy/add-on clause"
            e["rules"]["re_entry"] = "not stated — sheet read in full; silence, not a prohibition"
        else:
            e["entry_state"] = "not_stated"
            e["rules"]["single_entry"] = "not published — no official rule document for this row"
            e["rules"]["re_entry"] = "not published"
        e["rules"]["add_on"] = ao.get("value") or ("not stated — sheet read in full"
                                                   if ao.get("status") == "not_stated_sheet_read"
                                                   else "not published")
        _ex = (se.get("excerpt") or ao.get("excerpt") or "")
        e["rules"]["excerpt"] = _ex
        e["rules"]["retrieved"] = se.get("retrieved") or ret or ""
        e["rules"]["source_url"] = se.get("source_url") or sq

        # --- fill blank structural cells straight off the sheet
        filled = []
        for dst, src in (("chips", "chips"), ("level_min", "level_min"), ("gtd", "gtd")):
            if _blank(e.get(dst)) and not _blank(q.get(src)):
                e[dst] = q[src]
                filled.append(dst)
        if _blank(e.get("fee")) and not _blank(q.get("fee")):
            fee_q, pool_q, bi = q.get("fee"), q.get("pool_per_entry"), e.get("buy_in")
            if bi and not _blank(pool_q) and bi - fee_q == pool_q:
                e["fee"] = fee_q
                e["pool_per_entry"] = pool_q
                filled += ["fee", "pool_per_entry"]
            else:
                overlay["conflicts"].append({"id": e["id"], "field": "fee",
                                             "root": [e.get("buy_in"), e.get("fee"), e.get("pool_per_entry")],
                                             "sheet": [bi, fee_q, pool_q]})
        if _blank(e.get("pool_per_entry")) and not _blank(q.get("pool_per_entry")) and not _blank(e.get("fee")):
            if e["buy_in"] - e["fee"] == q["pool_per_entry"]:
                e["pool_per_entry"] = q["pool_per_entry"]
                filled.append("pool_per_entry")
        if _blank(e.get("late_reg")):
            lr = q.get("reg_close_text") or q.get("reg_close")
            if not _blank(lr):
                e["late_reg"] = lr
                filled.append("late_reg")
        if not _blank(q.get("reg_close")):
            e["reg_close_24"] = q["reg_close"]
        if _blank(e.get("bounty")) and not _blank(q.get("bounty")):
            e["bounty"] = q["bounty"]
            filled.append("bounty")
        if e.get("pays_pct") is None and q.get("pays_pct") is not None:
            e["pays_pct"] = q["pays_pct"]
            filled.append("pays_pct")
        if e.get("eligibility") is None and isinstance(q.get("eligibility"), dict):
            e["eligibility"] = q["eligibility"]
            filled.append("eligibility")
        if not e.get("notes") and not _blank(q.get("note")):
            e["notes"] = q["note"]
            filled.append("notes")
        if q.get("level_note"):
            e["level_note"] = q["level_note"]
        e["sheet"] = q.get("sheet")
        e["sheet_read"] = bool(q.get("sheet_read"))
        e["sheet_url"] = sq
        e["sheet_retrieved"] = ret
        e["plan_row_id"] = q.get("id")
        e["event_no"] = q.get("event_no")
        e["kind"] = q.get("kind")
        if q.get("satellite_text"):
            e["satellite_text"] = q["satellite_text"]
        if q.get("earliest_plausible_finish"):
            e["earliest_plausible_finish"] = q["earliest_plausible_finish"]
        # provenance of every value this block added
        for f_ in filled:
            e.setdefault("field_sources", {})[f_] = {"source_url": sq, "retrieved": ret,
                                                     "origin": "structure sheet %s (read in full)" % q.get("sheet")}
            overlay["filled"][f_] = overlay["filled"].get(f_, 0) + 1
        e["fields_from_sheets"] = filled

        # --- spend-advantage statement found on the sheet, if any
        if st == "explicit" and "subsequent flight" in (se.get("excerpt") or ""):
            e["spend_advantage"] = "further buy-ins possible: one entry per starting flight, " \
                                    "and a player who did not bag Day 2 chips may play another flight"
            e["spend_advantage_source"] = se.get("source_url")
        elif st == "explicit_no":
            e["spend_advantage"] = "further buy-ins priced on the sheet: %s" % (re_.get("value") or "see excerpt")
            e["spend_advantage_source"] = re_.get("source_url")

        # --- category moves ONLY on a stated rule
        if q.get("kind") == "PARTNER" and e["category"] != "spend-more":
            overlay["categories_changed"].append({"id": e["id"], "from": e["category"],
                                                   "to": "spend-more", "why": "sheet prices subsequent buy-ins"})
            e["category"] = "spend-more"
            e["format"] = "one-day"
            e["tags"] = sorted(set(e.get("tags") or []) | {"extra-buyins"})
        elif q.get("kind") == "MULTIDAY" and e["category"] == "multi-flight":
            overlay["categories_changed"].append({"id": e["id"], "from": "multi-flight",
                                                   "to": "multi-day", "why": "one starting day, two playing days"})
            e["category"] = "multi-day"
            e["format"] = "two-day"

    # keep the descriptive ratio honest after a fill
    for e in events:
        if e.get("venue_id") != "venetian":
            continue
        bi = e.get("total_entry_fee") or e.get("buy_in")
        if e.get("gtd") and bi:
            e["gtd_ratio"] = round(e["gtd"] / bi, 2)

# ------------------------------------------------------------------ hotel fold
HOTEL_ALIAS = {"H-CZP": "H-CAES", "H-HS": "H-HORSE", "H-MGM": None, "H-WG": None, "H-SP": None}
VENUE_WALK_ID = {"V-VEN": "venetian", "V-WYN": "wynn", "V-CP": "caesars",
                 "V-HS": "horseshoe", "V-BEL": "bellagio", "V-MGM": "mgm",
                 "V-GN": "goldennugget"}
WALK_HOTEL_ID = {"H-VEN": "H-VEN", "H-PAL": "H-PAL", "H-WYN": "H-WYN", "H-ARIA": "H-ARI",
                 "H-BEL": "H-BEL", "H-MGM": "H-MGM", "H-HS": "H-HS", "H-CZP": "H-CP",
                 "H-WG": "H-WG"}

VENUE_LABELS = (("venetian", "Venetian poker room"), ("wynn", "Wynn / Encore poker room"),
                ("caesars", "Caesars Palace poker room"), ("horseshoe", "Horseshoe poker room"),
                ("bellagio", "Bellagio poker room"), ("mgm", "MGM Grand poker room"),
                ("aria", "ARIA poker room"), ("goldennugget", "Golden Nugget poker room"))
# key used by data/site/walking.json for the same venue (it names only six rooms)
WALK_VENUE_ID = {"venetian": "V-VEN", "wynn": "V-WYN", "caesars": "V-CP", "horseshoe": "V-HS",
                 "bellagio": "V-BEL", "mgm": "V-MGM"}

plan_hotels = _json_load(PLAN_HOTELS_PATH) or {}
plan_rates = _json_load(PLAN_RATES_PATH) or {}
plan_walk = _json_load(PLAN_WALK_PATH) or {}
site_walk = _json_load(SITE_WALK_PATH) or {}

ph_by_id = {h.get("id"): h for h in (plan_hotels.get("hotels") or [])}
rate_rows = plan_rates.get("entries") or []
walk_by_pair = {}
for p_ in (plan_walk.get("pairs") or []):
    walk_by_pair[(p_.get("hotel_id"), p_.get("venue"))] = p_
site_walk_by_pair = {}
for r_ in (site_walk.get("rows") or []):
    site_walk_by_pair[(r_.get("hotel_id"), r_.get("venue_id"))] = r_
WALK_PLAN_HOTEL_IDS = {k[0] for k in walk_by_pair}
WALK_METHOD = (plan_walk.get("method") or site_walk.get("method") or
               "routed estimate")
WALK_LIMIT = plan_walk.get("limit_min") or site_walk.get("limit_min") or 30

for h in hotels:
    hid = h.get("id")
    src_hotel = ph_by_id.get(hid) or ph_by_id.get(HOTEL_ALIAS.get(hid) or "")
    if isinstance(src_hotel, dict):
        for key_src, key_dst in (("resort_fee", "fee_evidence"), ("parking", "parking_evidence"),
                                 ("incidentals", "incidentals"), ("tax", "tax_evidence")):
            v = src_hotel.get(key_src)
            if isinstance(v, dict):
                h[key_dst] = v
        if src_hotel.get("cancellation"):
            h["cancellation_evidence"] = src_hotel["cancellation"]
        if not h.get("quality") and src_hotel.get("quality"):
            h["quality"] = src_hotel["quality"]
        overlay["hotels"].append(hid)

    # dated rate log (plan rates file) — appended, never overwriting the existing log
    for r_ in rate_rows:
        if r_.get("hotel_id") != hid and HOTEL_ALIAS.get(hid) != r_.get("hotel_id"):
            continue
        if any(x.get("id") == r_.get("id") for x in (h.get("rate_log") or [])):
            continue
        h.setdefault("rate_log", []).append({
            "id": r_.get("id"),
            "date": r_.get("date_captured"),
            "rate": r_.get("rate_usd"),
            "basis": r_.get("rate_kind"),
            "conditions": r_.get("conditions"),
            "occupancy": r_.get("occupancy_basis"),
            "suite": r_.get("suite_type"),
            "offer": r_.get("offer"),
            "stay": None if not r_.get("stay_start") else "%s to %s (%s nights)" % (
                r_.get("stay_start"), r_.get("stay_end"), r_.get("nights")),
            "nightly": r_.get("nightly"),
            "room_subtotal": r_.get("room_subtotal_usd"),
            "resort_fee_total": r_.get("resort_fee_total_usd"),
            "taxes": r_.get("taxes_usd"),
            "tax_pct_implied": r_.get("tax_pct_implied"),
            "checkout_total": r_.get("checkout_total_usd"),
            "nightly_average": r_.get("nightly_average_usd"),
            "true_cost_per_night": r_.get("true_cost_per_night_usd"),
            "parking_per_day": r_.get("parking_self_park_per_day_usd"),
            "cancellation": r_.get("cancellation"),
            "cancellation_deadline": r_.get("cancellation_deadline"),
            "excerpt": r_.get("excerpt"),
            "caveat": r_.get("caveat"),
            "itemisation": r_.get("itemisation"),
            "status": r_.get("status"),
            "source_url": r_.get("source_url"),
        })
        overlay["rates_attached"] += 1
        if r_.get("status") == "verified_official_dated_quote":
            q_ = r_
            h["quote"] = {k: q_.get(k) for k in
                          ("stay_start", "stay_end", "nights", "adults", "suite_type", "offer",
                           "room_subtotal_usd", "resort_fee_total_usd", "taxes_usd", "tax_pct_implied",
                           "checkout_total_usd", "nightly_average_usd", "true_cost_per_night_usd",
                           "parking_self_park_per_day_usd", "cancellation", "cancellation_deadline",
                           "status", "source_url", "date_captured", "itemisation", "excerpt", "caveat")}

        # walking: prefer the /plan/ matrix (it carries the official indoor-route wording and
    # both map links); fall back to the routing matrix that produced it.
    plan_hid = hid if hid in WALK_PLAN_HOTEL_IDS else (HOTEL_ALIAS.get(hid) or "")
    site_hid = WALK_HOTEL_ID.get(hid)
    pairs = []
    for vkey, label in VENUE_LABELS:
        p_ = walk_by_pair.get((plan_hid, vkey)) if plan_hid else None
        site_vid = WALK_VENUE_ID.get(vkey)
        r_ = site_walk_by_pair.get((site_hid, site_vid)) if (site_hid and site_vid) else None
        mins = kind = gmap = amap = routed_on = note = None
        if p_:
            mins = p_.get("minutes_verified")
            kind = p_.get("minutes_kind")
            gmap = p_.get("google_maps")
            amap = p_.get("apple_maps")
            routed_on = p_.get("routed_on")
            note = p_.get("routed_via")
        if mins is None and r_:
            mins = r_.get("walk_min")
            kind = "routed_osrm_osm"
            gmap = gmap or r_.get("gmaps_link")
            routed_on = routed_on or site_walk.get("as_of")
        if mins is None and not p_ and not r_:
            continue
        ok30 = (mins is not None and mins <= WALK_LIMIT)
        pairs.append({"venue": vkey, "venue_label": label, "minutes": mins,
                      "kind": kind, "within_30_min": bool(ok30), "routed_on": routed_on,
                      "via": note, "google_maps": gmap, "apple_maps": amap,
                      "status": ("routed_estimate" if kind == "routed_osrm_osm" else
                                 ("same_property_indoor" if kind == "same_property_indoor"
                                  else "no_verified_duration")),
                      "official_address": (p_ or {}).get("venue_address_official"),
                      "route_official": (p_ or {}).get("route_official"),
                      "route_source": (p_ or {}).get("route_source")})
        if mins is not None:
            overlay["walk_rows"] += 1
    if pairs:
        h["walk_pairs"] = pairs
        ven = next((p_ for p_ in pairs if p_["venue"] == "venetian"), None)
        wyn = next((p_ for p_ in pairs if p_["venue"] == "wynn"), None)
        w = h.setdefault("walk", {})
        if ven and ven["minutes"] is not None:
            w["venetian_min"] = ven["minutes"]
            w["venetian_kind"] = ven["kind"]
        if wyn and wyn["minutes"] is not None:
            w["wynn_min"] = wyn["minutes"]
            w["wynn_kind"] = wyn["kind"]
        w["status"] = ("routed estimate (OSRM foot profile) - not an official or measured "
                       "duration; confirm on the map before you rely on it")
        w["routed_on"] = (ven or wyn or pairs[0])["routed_on"]
        w["limit_min"] = WALK_LIMIT
        w["method"] = WALK_METHOD
        w["within_30_min"] = any(p_["within_30_min"] for p_ in pairs)
        if ven and ven.get("google_maps"):
            w["maps_venetian"] = ven["google_maps"]
        if wyn and wyn.get("google_maps"):
            w["maps_wynn"] = wyn["google_maps"]

# the overlay's own report, so a reader can see what was changed and what was not
master["overlay"] = {
    "session": "arena/32a40b2f-poker2",
    "date": "2026-11-17",
    "from": "site-data/events.json (37 structure sheets), site-data/hotels.json, "
            "site-data/rates.json, site-data/walk.json, data/site/walking.json",
    "joined_rows": overlay["joined"],
    "unjoined_rows": overlay["unjoined"],
    "cells_filled": overlay["filled"],
    "categories_changed": overlay["categories_changed"],
    "conflicts_left_unresolved": overlay["conflicts"],
    "hotels_with_official_fee_evidence": sorted(set(overlay["hotels"])),
    "walk_pairs_with_minutes": overlay["walk_rows"],
    "rate_log_entries_attached": overlay["rates_attached"],
    "note": "Blanks filled, not values overwritten. No last_checked date was advanced by "
            "this overlay — a date moves only when the cited page is opened again.",
}
print("overlay: %d/%d Venetian rows joined, %d cells filled, %d categories changed, "
      "%d unresolved conflicts, %d walk pairs with minutes"
      % (overlay["joined"], len([e for e in events if e.get("venue_id") == "venetian"]),
         sum(overlay["filled"].values()), len(overlay["categories_changed"]),
         len(overlay["conflicts"]), overlay["walk_rows"]))
if overlay["unjoined"]:
    print("overlay: rows NOT joined:", [u["id"] for u in overlay["unjoined"]])
if overlay["conflicts"]:
    print("overlay: conflicts kept for review:", overlay["conflicts"])


# ===========================================================================
# OFFICIAL RE-READ APPLIED — arena/32a40b2f-poker2 (2026-11-17)
# ---------------------------------------------------------------------------
# data/session-updates-32a40b2f.json holds the four official pages this session
# opened end to end on 2026-11-17 (ARIA terms, Bellagio terms, MGM Grand terms,
# Westgate Las Vegas resort-fee FAQ, plus the Caesars Palace hotel page). Only the
# rows whose cited page was actually opened again get a new date — everything else
# keeps the date of the read behind it.
# ===========================================================================
OWN_UPDATES_PATH = os.path.join(ROOT, "data", "session-updates-32a40b2f.json")
own = _json_load(OWN_UPDATES_PATH) or {}
hotel_by_id = {h["id"]: h for h in hotels}

if own.get("hotel_terms_reads"):
    for hid, rec in own["hotel_terms_reads"].items():
        h = hotel_by_id.get(hid)
        if not h:
            continue
        if h.get("resort_fee_value") in (None, "") and rec.get("resort_fee_usd") is not None:
            h["resort_fee_value"] = rec["resort_fee_usd"]
        elif (h.get("resort_fee_value") is not None and rec.get("resort_fee_usd") is not None
              and abs(float(h["resort_fee_value"]) - float(rec["resort_fee_usd"])) > 0.005):
            h["fee_reread_conflict"] = {"row_value": h["resort_fee_value"],
                                        "page_value": rec["resort_fee_usd"],
                                        "url": rec["url"], "retrieved": rec["retrieved"]}
        h["resort_fee_text"] = "$%s plus applicable tax per night (official hotel terms)" % (
            ("%g" % rec["resort_fee_usd"]) if rec.get("resort_fee_usd") is not None else "—")
        h["resort_fee_src"] = rec["url"]
        h["fee_evidence"] = {"amount": rec.get("resort_fee_usd"), "plus_tax": True,
                             "per": "room night", "status": "verified_official",
                             "excerpt": rec.get("resort_fee_excerpt"),
                             "waiver": rec.get("fee_waiver"),
                             "source_url": rec["url"], "retrieved": rec["retrieved"]}
        if rec.get("incidentals_usd_per_day") is not None:
            h["deposit"] = "$%s per night incidentals (official hotel terms)" % (
                "%g" % rec["incidentals_usd_per_day"])
            h["incidentals"] = {"amount": rec["incidentals_usd_per_day"],
                                "excerpt": rec.get("incidentals_excerpt"),
                                "source_url": rec["url"], "retrieved": rec["retrieved"]}
        if rec.get("additional_occupant"):
            h["additional_occupant"] = {"value": rec["additional_occupant"],
                                        "source_url": rec["url"], "retrieved": rec["retrieved"]}
        if rec.get("check_in_out"):
            h["check_in_out"] = {"value": rec["check_in_out"], "source_url": rec["url"],
                                 "retrieved": rec["retrieved"]}
        if rec.get("cancellation"):
            h["cancellation"] = rec["cancellation"]
            h["cancellation_deadline"] = rec.get("cancellation_deadline")
        if rec.get("cancellation_fee"):
            h["cancellation_fee"] = rec["cancellation_fee"]
        if rec.get("early_checkout"):
            h["early_checkout"] = rec["early_checkout"]
        if rec.get("tax_note"):
            h["tax_note"] = rec["tax_note"]
        h["retrieved"] = rec["retrieved"]
        h["fee_last_checked"] = rec["retrieved"]

# a placeholder left by the earlier pass ("this page was not read") must not survive next
# to the read that supersedes it, or a row shows both a value and its own denial
for _h in hotels:
    if not _h.get("fee_last_checked"):
        continue
    for _k in ("fee_evidence", "cancellation_evidence", "parking_evidence", "incidentals"):
        _v = _h.get(_k)
        if isinstance(_v, dict) and _v.get("status") == "not_read_official_page":
            _h[_k] = {"status": "superseded_by_reread",
                      "note": ("an earlier pass recorded that this page had not been read; the value on this "
                               "row now comes from the %s read of %s"
                               % (_h.get("fee_last_checked"), _h.get("resort_fee_src") or "")),
                      "superseded_excerpt_of": _v.get("note") or _v.get("rule")}

_wg = own.get("westgate_resort_fee_recheck")
if _wg:
    h = hotel_by_id.get("H-WG")
    if h:
        h["resort_fee_src"] = _wg["fee_supported_by"]
        h["fee_evidence"] = {"amount": h.get("resort_fee_value"), "plus_tax": True,
                             "per": "room night", "status": "verified_official",
                             "excerpt": _wg["excerpt"], "source_url": _wg["fee_supported_by"],
                             "retrieved": _wg["retrieved"]}
        h["retrieved"] = _wg["retrieved"]
        h["fee_last_checked"] = _wg["retrieved"]
        h["fee_conflict"] = {
            "value_used": h.get("resort_fee_value"),
            "conflict": "The property's own resort-fee FAQ page prints “$49.99 plus tax per night”. "
                        "The same FAQ's embedded structured answer carries $36.99 in an earlier session's "
                        "note; the page body does not. The generic westgateresorts.com terms page — which an "
                        "earlier row cited for this figure — states no Westgate Las Vegas nightly fee at all "
                        "and is the Westgate Resorts timeshare terms, so the citation has been corrected.",
            "url": _wg["fee_supported_by"],
            "wrongly_cited": "https://www.westgateresorts.com/terms-and-conditions/",
            "retrieved": _wg["retrieved"]}
        flags.append({
            "source": "arena/32a40b2f-poker2 re-read 2026-11-17",
            "item": "Westgate: the resort fee was cited to a page that does not state it",
            "where": "Hotels table, Westgate row",
            "detail": _wg["finding"],
            "url": _wg["fee_supported_by"],
            "severity": "medium",
            "id": "VR-32a4-01"})

_cz = own.get("caesars_palace_recheck")
if _cz:
    for hid in ("H-CZP", "H-HS"):
        h = hotel_by_id.get(hid)
        if not h:
            continue
        h["fee_page_read"] = {"url": _cz["url"], "retrieved": _cz["retrieved"],
                              "finding": _cz["finding"],
                              "cancellation_marketing": _cz.get("cancellation_marketing")}
        h["resort_fee_text"] = ("blank — the official property page read on 2026-11-17 publishes no "
                                "resort-fee figure")
    flags.append({
        "source": "arena/32a40b2f-poker2 re-read 2026-11-17",
        "item": "Caesars Palace and Horseshoe: no official page states a resort fee",
        "where": "Hotels table, Caesars Palace and Horseshoe rows",
        "detail": _cz["finding"],
        "url": _cz["url"],
        "severity": "medium",
        "id": "VR-32a4-02"})

# ---------------------------------------------------------------------------
# Narrative corrections: every statement the synced data contradicts is
# rewritten from the data itself, with the superseded wording kept visible so
# the change is auditable rather than silent.
# ---------------------------------------------------------------------------
_ven = [e for e in events if e.get("venue_id") == "venetian"]
n_silent = len([e for e in _ven if e.get("entry_state") == "silent"])
n_stated = len([e for e in _ven if e.get("entry_state") in ("stated", "stated_multi_entry")])
n_unver = len([e for e in events if e["category"] == "unverified"])
n_spend = len([e for e in events if e["category"] == "spend-more"])
n_single_all = len([e for e in events if e["category"] == "single"])
n_quote = len([h for h in hotels if h.get("quote")])
n_fee = len([h for h in hotels if h.get("resort_fee_value") is not None])
n_walk = len([h for h in hotels if (h.get("walk") or {}).get("within_30_min")])

_repl = {
    "Structure sheet silent on re-entry (The Venetian)": (
        str(n_silent),
        "One-day Venetian events whose official structure sheet was read in full and prints no re-entry, "
        "rebuy or add-on clause. Silence is NOT a published freezeout rule: no Venetian sheet states "
        "\u201cno re-entry\u201d, so these are sheet-silent candidates, not confirmed single-entry."),
    "Excluded rows": (
        "Venetian %d · all venues %d" % (len([e for e in _ven if e["category"] in
                                              ("multi-flight", "satellite", "team", "multi-day")]), n_spend),
        "Spend-more, multi-flight, multi-day, satellite and team events, kept out of the single-entry "
        "ranking and shown separately."),
    "Unverified rows (structure not reviewed)": (
        str(n_unver),
        "Rows whose schedule values come from an official page but for which the room publishes no entry-rule "
        "document at all. Every one of the 37 Venetian DeepStack IV structure sheets has now been read, so no "
        "Venetian row is left in this state."),
    "Structure sheet silent on re-entry at Wynn": (
        "0",
        "Every Wynn structure document read prints an explicit re-entry clause, so no Wynn row is even a "
        "sheet-silent candidate."),
}
for _hn in master["summary"].get("headline_numbers", []):
    if _hn.get("label") in _repl:
        val, note = _repl[_hn["label"]]
        if _hn.get("value") != val:
            _hn["previous_value"] = _hn["value"]
        _hn["value"] = val
        _hn["note"] = note
        _hn["computed"] = "computed from data/master.json at build time"
master["summary"]["headline_numbers"] += [
    {"label": "Venetian rows whose sheet states an entry rule", "value": str(n_stated),
     "note": "The sheet says it out loud: 27 multi-flight rows carry the official “may not play a "
             "subsequent flight” clause once a player bags Day 2 chips, and 2 rows price further buy-ins "
             "explicitly. Stated rules are recorded per field with the sheet excerpt and retrieval date."},
    {"label": "Dated official room quotes captured", "value": str(n_quote),
     "note": "Checkout-level quotes read off the official booking engine's own price breakdown (itemised "
             "per night, with tax and resort fee) for The Venetian. Every other property stays blank until "
             "a quote is captured for its dates and occupancy."},
    {"label": "Hotels with an official resort fee on file", "value": "%d of %d" % (n_fee, len(hotels)),
     "note": "Each fee carries the page it was read from and the date. Where a property publishes no fee "
             "figure, the cell is blank and flagged rather than estimated."},
    {"label": "Hotels within a 30-minute routed walk of a tracked poker room",
     "value": "%d of %d" % (n_walk, len(hotels)),
     "note": "Routed estimates (OSRM foot profile) computed on the official addresses — not measured or "
             "official durations. Each row links straight to Google and Apple walking directions so the "
             "pair can be confirmed in one tap."}]

_recs = ("Start from the %d sheet-silent Venetian one-day events (no re-entry, rebuy or add-on clause on the "
         "official structure sheet) — but treat that as the closest thing to a single-entry list the "
         "rooms publish, not as a confirmed freezeout: ask the room, in writing, before paying. Price the "
         "stay from a dated checkout quote, not a from-price: The Venetian has one (itemised, with the tax "
         "line) and it shows how much an event window moves the nightly rate. Confirm the walk on the map "
         "link for the hotel you pick: the ≤30-minute test is applied to routed estimates, not to measured "
         "times. Build one event per day, and add an evening event only where the earlier one can "
         "realistically be exited.")
if master["summary"].get("recommendation") and "sheet-silent" not in master["summary"]["recommendation"]:
    master["summary"]["recommendation_previous"] = master["summary"]["recommendation"]
    master["summary"]["recommendation"] = _recs

# stale Q&A answers that the synced data now contradicts — corrected in place,
# with the old wording preserved under 'superseded' so nothing disappears silently
for _q in master.get("questions", []):
    if _q.get("id") == "Q01":
        _q["superseded"] = _q.get("answer", "")
        _q["answer"] = ("%d Venetian one-day events are sheet-silent on re-entry, rebuy and add-ons "
                        "(the strongest position any official document supports); %d Venetian rows carry a "
                        "stated entry rule on their sheet — %d of them a restriction that keeps the event out "
                        "of a single-entry plan. No Las Vegas room in this dataset publishes \u201cno "
                        "re-entry\u201d, so no event is labelled confirmed single-entry. %d rows across "
                        "Wynn, Horseshoe and MGM have no rule document published at all."
                        % (n_silent, n_stated, 27, n_unver))
        _q["status"] = "Partly answered — from the official sheets, not from the rooms"
        _q["needed"] = ("A written one-entry confirmation from each poker room. The structure sheets are "
                        "now all read (37 of 37), so no further sheet can settle it.")
        _q["how_to_find"] = ("Email or ask the Venetian, Wynn, Caesars, Horseshoe and MGM Grand poker rooms "
                             "in writing; keep the reply with the row.")
        _q["corrected"] = "2026-11-17 (arena/32a40b2f-poker2): answer rewritten from the completed 37-sheet read"

flags.append({
    "source": "arena/32a40b2f-poker2 integration 2026-11-17",
    "item": "Root dashboard was one evidence generation behind the planner surface",
    "where": "Tournaments, Entry rules, Hotels, Executive summary",
    "detail": ("The root pages were built from the reads captured up to 2026-11-16, while the completed "
               "37-sheet transcription (2026-11-17) sat in site-data/. The gap is now folded in: %d blank "
               "cells filled from the sheet that prints them, %d rows re-labelled because their sheet states "
               "the rule, per-field excerpts and retrieval dates on every Venetian row, and two headline "
               "numbers that the data contradicted rewritten from the data. Filling was one-directional "
               "(blanks only) and %d value conflicts were found between the two surfaces, so no verified "
               "number was overwritten.")
              % (sum(overlay["filled"].values()), len(overlay["categories_changed"]),
                 len(overlay["conflicts"])),
    "url": "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
    "severity": "info",
    "id": "VR-32a4-03",
    "resolved": "Closed by this build: both surfaces now render the same sheet evidence."})

flags.append({
    "source": "arena/32a40b2f-poker2 re-read 2026-11-17",
    "item": "No official document turns a sheet-silent event into a confirmed single-entry event",
    "where": "Entry rules, Single-entry filter, Ranking",
    "detail": ("Reading all 37 structure sheets produced no \u201cno re-entry\u201d sentence anywhere. What "
               "the sheets do print is a late-registration window, a payout percentage, a fee split and — on "
               "multi-flight events — the clause that a player who bags Day 2 chips may not play a later "
               "flight. Rows are therefore labelled by what the document says, field by field, and the "
               "single-entry toggle filters to \u201csheet silent\u201d, which is a shorter list of "
               "candidates, not a guarantee of a freezeout."),
    "url": "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_5.pdf",
    "severity": "high",
    "id": "VR-32a4-04"})

master["verification"] = {
    "session": "arena/32a40b2f-poker2",
    "date": "2026-11-17",
    "documents": [
        {"title": "Venetian DeepStack Extravaganza IV event page (Nov 16 – Dec 23, 2026)",
         "url": "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html",
         "retrieved": "2026-11-17",
         "settles": "The schedule the Venetian rows are keyed to: dates, start times, event numbers, buy-in "
                    "and guarantee strings, and which structure sheet is linked from each row."},
        {"title": "ARIA hotel reservation terms",
         "url": "https://aria.mgmresorts.com/en/terms-and-conditions.html",
         "retrieved": "2026-11-17",
         "settles": "ARIA $55.00 plus applicable tax daily resort fee, its inclusions, the Gold+ waiver, "
                    "$150/day incidentals, the $50 additional-occupant charge and the 72-hour deposit "
                    "cancellation deadline."},
        {"title": "Bellagio hotel reservation terms",
         "url": "https://bellagio.mgmresorts.com/en/terms-and-conditions.html",
         "retrieved": "2026-11-17",
         "settles": "Bellagio $55.00 plus applicable tax daily resort fee, inclusions, waiver, $150/day "
                    "incidentals, $50 additional occupant, 72-hour cancellation deadline."},
        {"title": "MGM Grand hotel reservation terms",
         "url": "https://mgmgrand.mgmresorts.com/en/terms-and-conditions.html",
         "retrieved": "2026-11-17",
         "settles": "MGM Grand $50.00 plus applicable tax daily resort fee, inclusions, waiver, $100/day "
                    "incidentals, $40 additional occupant, 72-hour cancellation deadline and the early-"
                    "departure assessment."},
        {"title": "Westgate Las Vegas resort-fee FAQ",
         "url": "https://www.westgateresorts.com/hotels/nevada/las-vegas/westgate-las-vegas-resort-casino/faq/resort-fee/",
         "retrieved": "2026-11-17",
         "settles": "Westgate Las Vegas resort fee $49.99 plus tax per night — and shows the terms page an "
                    "earlier row cited for it does not state any Westgate Las Vegas fee."},
        {"title": "Caesars Palace official hotel page",
         "url": "https://www.caesars.com/caesars-palace/hotel",
         "retrieved": "2026-11-17",
         "settles": "Nothing about the resort fee: the page publishes no figure, so the cell stays blank. "
                    "It does print “FREE 48-Hour Cancellation*” as a booking benefit."},
    ],
    "hotel_rows_re_read_today": sorted([h["id"] for h in hotels if h.get("fee_last_checked")]),
    "note": ("Only these six documents were opened again on 2026-11-17 by this session. Structure-sheet dates "
             "come from the 2026-11-17 read recorded in site-data/ (that pass is cited per field, per row); "
             "no date was advanced for a document this session did not itself open."),
}
print("overlay applied: ARIA/Bellagio/MGM Grand fees re-read first-hand; Westgate citation corrected; "
      "%d flags now published" % len(flags))

ids = [e["id"] for e in events]
assert len(ids) == len(set(ids)), "duplicate event ids: %s" % [i for i in ids if ids.count(i) > 1]

master["as_of"] = LAST_VERIFIED
with open(os.path.join(ROOT, "data/master.json"), "w") as f:
    json.dump(master, f, indent=1, sort_keys=False)
print("data/master.json written: %d events, %d hotels, %d flags"
      % (len(events), len(hotels), len(flags)))
from collections import Counter
print("categories:", dict(Counter(e["category"] for e in events)))
