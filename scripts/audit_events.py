#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build data/audit/events.json.

Two transcription inputs, both dated 2026-11-17:
  1. verify/official-venetian-dse4-2026-11-17.tsv  - one row per table row on the
     official DSE IV schedule page (94 rows: date, time, event no, name, sheet no).
  2. data/audit/sheets.py                          - the values printed on each
     structure-sheet PDF that was opened and read in full.

The join key is the structure-sheet number, because that is the only document
identity the official page actually publishes. An event whose sheet was not read
keeps every structural field null and is marked "structure_not_read".

Nothing is filled in. If a field is not on a document that was read, it is None.
"""
import csv, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data", "audit"))
from sheets import SHEETS, UNREAD_SHEETS, RETRIEVED, SCHEDULE_URL, sheet_url, by_number

TSV = os.path.join(ROOT, "verify", "official-venetian-dse4-2026-11-17.tsv")
OUT = os.path.join(ROOT, "data", "audit", "events.json")

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def iso_to_dow(iso):
    import datetime
    y, m, d = (int(x) for x in iso.split("-"))
    return DAY_NAMES[datetime.date(y, m, d).weekday()]


def hhmm(twelve):
    m = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM)", twelve.strip().upper())
    h = int(m.group(1)) % 12 + (12 if m.group(3) == "PM" else 0)
    return "%02d:%s" % (h, m.group(2))


def money_from_name(name):
    m = re.search(r"\$([\d,]+)", name)
    return int(m.group(1).replace(",", "")) if m else None


def gtd_from_name(name):
    m = re.search(r"\$([\d,.]+)\s*([KM])\s*GTD", name)
    if not m:
        return None
    v = float(m.group(1).replace(",", ""))
    return int(v * (1_000_000 if m.group(2) == "M" else 1_000))


def classify(name, sheet_no, sheet):
    """Category decides which section of the site a row belongs in.

    multi_flight : the official page says the row is one flight (1A..1F / Day 2).
    satellite    : the name says satellite / milestone satellite.
    team         : the name says tag team.
    single       : a one-day row. Its entry-rule certainty is a separate field.
    """
    n = name.lower()
    if "satellite" in n:
        return "satellite"
    if "tag team" in n:
        return "team"
    if re.search(r"\b1[a-f]\b", name) or "day 2" in n or "day 3" in n or "final table" in n:
        return "multi_flight"
    if "2day" in n or "(2day)" in n:
        return "multi_flight"
    return "single"


def main():
    rows = []
    with open(TSV, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            date, time12, evno, name, sheet = line.rstrip("\n").split("\t")
            rows.append(dict(date=date, time12=time12, evno=evno, name=name, sheet=int(sheet)))

    sheets = by_number()
    out = []
    for i, r in enumerate(rows, start=1):
        s = sheets.get(r["sheet"])
        start = hhmm(r["time12"])
        cat = classify(r["name"], r["sheet"], s)

        # Event number the sheet assigns to this row, where the sheet lists several.
        # The schedule page number is authoritative for the row; this only records
        # whether the sheet agrees with it.
        sheet_no_match = None
        if s:
            nums = [x.lstrip("0") for x in s["event_numbers"]]
            sheet_no_match = (r["evno"] in nums) or (str(r["sheet"]) in
                                                     [str(x) for x in s["event_numbers"]])
        rec = {
            "id": "EV-%02d" % i,
            "date": r["date"],
            "dow": iso_to_dow(r["date"]),
            "start": start,
            "start_text": r["time12"],
            "event_no": r["evno"],
            "name": r["name"],
            "category": cat,
            "buy_in_nominal": money_from_name(r["name"]),
            "gtd_from_name": gtd_from_name(r["name"]),
            "sheet": r["sheet"],
            "sheet_url": sheet_url(r["sheet"]),
            "schedule_url": SCHEDULE_URL,
            "schedule_retrieved": RETRIEVED,
            "structure_read": bool(s),
            "last_checked": RETRIEVED,
            # ---- values that exist only when the structure sheet was read ----
            "fee": None, "pool_per_entry": None, "chips": None,
            "level_min": None, "late_reg_time": None, "late_reg_text": None,
            "gtd": None, "gtd_basis": None, "pays_pct": None,
            "bounty_amount": None, "single_entry": None, "re_entry": None, "add_on": None,
            "eligibility": None, "game": None,
            "entry_excerpt": None, "fee_excerpt": None, "source_url": None,
            "unverified": [], "notes": "",
        }
        if s:
            gtd = s.get("per_event_guarantee", {}).get(r["evno"]) if s.get("per_event_guarantee") else None
            if gtd is None and s.get("guarantee_basis") != "no guarantee printed":
                gtd = gtd_from_name(r["name"])
            rec.update({
                "fee": s["fee"],
                "pool_per_entry": s["pool_per_entry"],
                "chips": s["chips"],
                "level_min": s["level_min"],
                "late_reg_time": s["late_reg_time"],
                "late_reg_text": s["late_reg_text"],
                "gtd": gtd,
                "gtd_basis": s["guarantee_basis"],
                "pays_pct": s["pays_pct"],
                "bounty_amount": s["bounty_amount"],
                "eligibility": s.get("eligibility"),
                "single_entry": s["single_entry"],
                "re_entry": s["re_entry"],
                "add_on": s["add_on"],
                "entry_excerpt": s["entry_excerpt"],
                "fee_excerpt": s["fee_excerpt"],
                "source_url": sheet_url(r["sheet"]),
                "notes": s["notes"],
            })
            if not sheet_no_match:
                rec["unverified"].append(
                    "schedule page event #%s is not among the event numbers printed on sheet %d (%s)"
                    % (r["evno"], r["sheet"], ", ".join(s["event_numbers"])))
        else:
            for f in ("fee", "pool_per_entry", "chips", "level_min", "late_reg_time",
                      "late_reg_text", "gtd", "gtd_basis", "pays_pct", "single_entry",
                      "re_entry", "add_on"):
                rec["unverified"].append("%s: structure sheet %d not read in this pass" % (f, r["sheet"]))
            rec["source_url"] = SCHEDULE_URL

        # A published buy-in and a published fee are two numbers from two documents.
        if rec["fee"] is not None and rec["buy_in_nominal"] is not None:
            rec["total_entry_fee"] = rec["buy_in_nominal"]
            rec["fee_plus_pool_matches_buyin"] = (rec["fee"] + rec["pool_per_entry"]
                                                 == rec["buy_in_nominal"])
        else:
            rec["total_entry_fee"] = None
            rec["fee_plus_pool_matches_buyin"] = None

        # Descriptive ratio only, and only when the guarantee is pure prize pool.
        # A bounty-inclusive guarantee (sheet 1/11/15/16) counts money that is paid back
        # as bounties, so dividing it by the entry fee would flatter the event. Those rows
        # keep gtd but get no ratio; the page shows why. See FD-07.
        if (rec["gtd"] and rec["total_entry_fee"]
                and (rec["gtd_basis"] or "").strip().lower() == "prize pool"):
            rec["gtd_ratio_descriptive"] = round(rec["gtd"] / rec["total_entry_fee"], 2)
        else:
            rec["gtd_ratio_descriptive"] = None
        out.append(rec)

    meta = {
        "as_of": RETRIEVED,
        "schedule_url": SCHEDULE_URL,
        "schedule_rows_transcribed": len(out),
        "sheets_read": len(SHEETS),
        "sheets_not_read": UNREAD_SHEETS,
        "series": "DeepStack Extravaganza IV, The Venetian Resort Las Vegas, 2026-11-16 to 2026-12-23",
        "note": ("Every row is one <tr> of the official schedule page, in page order. "
                 "Structural fields are transcribed from the structure sheet the page links "
                 "to and are null when that sheet was not read. 'single_entry: not_stated' "
                 "means the sheet was read and prints no entry-limit clause - it is silence, "
                 "not a published freezeout rule."),
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"meta": meta, "events": out}, fh, indent=1, ensure_ascii=False)
        fh.write("\n")

    read = sum(1 for e in out if e["structure_read"])
    print("rows          : %d" % len(out))
    print("sheet read    : %d rows (from %d of %d sheets)" % (read, len(SHEETS), len(SHEETS) + len(UNREAD_SHEETS)))
    print("sheet not read: %d rows" % (len(out) - read))
    bad = [e["id"] for e in out if e["fee"] is not None and e["fee_plus_pool_matches_buyin"] is False]
    print("fee+pool != buy-in rows: %d %s" % (len(bad), bad))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
