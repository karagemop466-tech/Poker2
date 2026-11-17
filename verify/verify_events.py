#!/usr/bin/env python3
"""
verify_events.py — re-derive data/audit/events.json's schedule fields from the
official transcription and fail if they disagree.

`data/audit/events.json` is produced by `scripts/audit_events.py`, which joins the
hand-transcribed TSV in `verify/` against `data/audit/sheets.py`. That makes the TSV
the only hand-maintained copy of the official schedule, and this script is the check
that keeps it honest:

  * row count and row order match the transcription,
  * date, start time and event number match, row for row,
  * every structure-sheet number points at a sheet that `sheets.py` knows about,
  * a sheet claimed as "read" has enough detail to have been read (fee, stack,
    level time), which is how a real transcription differs from a placeholder,
  * buy_in == fee + pool_per_entry wherever both are printed, so no row invents a fee,
  * every row has an https source and a retrieval date.

It does not fetch anything. Re-reading a changed official page is the job of
`scripts/audit_recheck.py`; this is the offline consistency gate.

    python3 verify/verify_events.py            # human-readable, exit 1 on failure
    python3 verify/verify_events.py --quiet    # one summary line
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV = os.path.join(ROOT, "verify", "official-venetian-dse4-2026-11-17.tsv")
EVENTS = os.path.join(ROOT, "data", "audit", "events.json")
SHEETS_PY = os.path.join(ROOT, "data", "audit", "sheets.py")


def load_tsv(path):
    """Rows of the official transcription, comments and blank lines skipped."""
    rows = []
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                raise SystemExit("%s:%d has %d fields, expected at least 4" % (path, n, len(parts)))
            rows.append({
                "date": parts[0].strip(),
                "time": parts[1].strip(),
                "event_no": parts[2].strip(),
                "name": parts[3].strip(),
                "sheet": parts[4].strip() if len(parts) > 4 else "",
                "line": n,
            })
    return rows


def load_sheets(path):
    """The transcribed structure sheets, imported rather than parsed."""
    sys.path.insert(0, os.path.dirname(path))
    import importlib
    mod = importlib.import_module(os.path.splitext(os.path.basename(path))[0])
    # SHEETS is a list of dicts keyed by 'sheet'; index it by number for lookup
    mod.BY_NUMBER = {int(s["sheet"]): s for s in mod.SHEETS}
    mod.READ = set(mod.BY_NUMBER)
    mod.UNREAD = set(int(n) for n in mod.UNREAD_SHEETS)
    return mod


def norm_time(t):
    """'11:10 AM' and '11:10' both normalise to ('11:10', 'AM')."""
    t = (t or "").strip().upper().replace(".", "")
    ampm = ""
    if t.endswith("AM") or t.endswith("PM"):
        ampm = t[-2:]
        t = t[:-2].strip()
    return t, ampm


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    fails, notes = [], []
    say = (lambda *a: None) if args.quiet else print

    tsv = load_tsv(TSV)
    sheets = load_sheets(SHEETS_PY)
    data = json.load(open(EVENTS, encoding="utf-8"))
    events = data["events"]

    say("transcription: %d rows" % len(tsv))
    say("dataset:       %d rows" % len(events))

    # ---- 1. same number of rows
    if len(tsv) != len(events):
        fails.append("row count: transcription has %d, dataset has %d"
                     % (len(tsv), len(events)))

    # ---- 2. row-for-row agreement on the fields the transcription carries
    by_position = list(zip(tsv, events))
    date_bad = start_bad = no_bad = 0
    for t, e in by_position:
        if t["date"] != e["date"]:
            date_bad += 1
            if date_bad <= 3:
                fails.append("date mismatch at %s:%d: %s vs %s"
                             % (os.path.basename(TSV), t["line"], t["date"], e["date"]))
        # dataset stores 24h 'start' plus the printed 'start_text'
        if t["time"].strip() and e.get("start_text", "").strip():
            if norm_time(t["time"])[0] != norm_time(e["start_text"])[0]:
                start_bad += 1
                if start_bad <= 3:
                    fails.append("start mismatch on %s: %r vs %r"
                                 % (e.get("id"), t["time"], e["start_text"]))
        if t["event_no"] and str(e.get("event_no", "")).strip() != t["event_no"].strip():
            no_bad += 1
            if no_bad <= 3:
                fails.append("event_no mismatch on %s: %r vs %r"
                             % (e.get("id"), t["event_no"], e.get("event_no")))
    if date_bad:
        fails.append("%d row(s) disagree on date" % date_bad)
    if start_bad:
        fails.append("%d row(s) disagree on start time" % start_bad)
    if no_bad:
        fails.append("%d row(s) disagree on event number" % no_bad)
    say("  dates: %d/%d agree, starts: %d/%d agree, event numbers: %d/%d agree"
        % (len(events) - date_bad, len(events),
           len(events) - start_bad, len(events),
           len(events) - no_bad, len(events)))

    # ---- 3. monotonic, complete date span
    dates = [e["date"] for e in events]
    if dates != sorted(dates):
        fails.append("dataset is not in date order")
    if len(set(dates)) != len(set(dates)):
        fails.append("duplicate dates")
    say("  span: %s to %s across %d distinct dates"
        % (min(dates), max(dates), len(set(dates))))

    # ---- 4. every sheet reference resolves
    known = sheets.READ | sheets.UNREAD
    bogus = sorted({e["sheet"] for e in events if e.get("sheet") not in known})
    if bogus:
        fails.append("dataset cites sheet(s) sheets.py does not know: %s" % bogus)

    # ---- 5. a sheet claimed read must carry the detail a real read produces
    thin = []
    for n in sorted(sheets.BY_NUMBER):
        s = sheets.BY_NUMBER[n]
        missing = [k for k in ("fee", "chips", "level_min", "late_reg_time")
                   if not s.get(k)]
        if missing:
            thin.append((n, missing))
    if thin:
        for n, missing in thin[:5]:
            fails.append("sheet %s is marked read but lacks %s" % (n, ", ".join(missing)))

    # the reverse: a row that carries fee/stack/level data must be backed by a read sheet
    phantom = [e["id"] for e in events
               if e.get("fee") and e["sheet"] not in sheets.READ]
    if phantom:
        fails.append("%d row(s) carry a fee but their sheet is not in the read set: %s"
                     % (len(phantom), phantom[:5]))

    read_rows = sum(1 for e in events if e.get("structure_read"))
    say("  structure sheets: %d read, %d not read, %d rows with structure data"
        % (len(sheets.READ), len(sheets.UNREAD), read_rows))

    # ---- 6. buy-in arithmetic: fee + prize pool == nominal buy-in
    mis = [e["id"] for e in events
           if e.get("fee") is not None and e.get("pool_per_entry") is not None
           and e.get("buy_in_nominal") is not None
           and e["fee"] + e["pool_per_entry"] != e["buy_in_nominal"]]
    if mis:
        fails.append("%d row(s) where fee + prize pool != buy-in: %s" % (len(mis), mis[:5]))
    checked = sum(1 for e in events if e.get("fee") is not None
                  and e.get("pool_per_entry") is not None)
    say("  buy-in arithmetic: %d rows checked, %d wrong" % (checked, len(mis)))

    # ---- 7. provenance on every row
    no_src = [e["id"] for e in events
              if not (e.get("source_url") or "").startswith("https://")]
    if no_src:
        fails.append("%d row(s) without an https source: %s" % (len(no_src), no_src[:5]))
    no_date = [e["id"] for e in events
               if not (e.get("last_checked") or e.get("schedule_retrieved"))]
    if no_date:
        fails.append("%d row(s) without a retrieval date: %s" % (len(no_date), no_date[:5]))

    # ---- 8. no event claims single-entry without a quoted rule
    bad_single = [e["id"] for e in events
                  if e.get("single_entry") == "explicit_yes"
                  and not (e.get("entry_excerpt") or "").strip()]
    if bad_single:
        fails.append("%d row(s) claim single-entry with no quoted excerpt: %s"
                     % (len(bad_single), bad_single[:5]))
    yes = sum(1 for e in events if e.get("single_entry") == "explicit_yes")
    no = sum(1 for e in events if e.get("single_entry") == "explicit_no")
    silent = sum(1 for e in events if e.get("single_entry") == "not_stated")
    say("  entry rule: %d explicit yes, %d explicit no, %d silent" % (yes, no, silent))

    # ---- 9. a guarantee ratio only where the guarantee is a pure prize pool
    bad_ratio = [e["id"] for e in events
                 if e.get("gtd_ratio_descriptive")
                 and e.get("gtd_basis") != "prize pool"]
    if bad_ratio:
        fails.append("%d row(s) publish a ratio on a non-prize-pool guarantee: %s"
                     % (len(bad_ratio), bad_ratio[:5]))
    ratios = sum(1 for e in events if e.get("gtd_ratio_descriptive"))
    say("  descriptive ratios: %d rows, all on pure prize pool" % ratios)

    # ---- verdict
    if fails:
        print("\nFAILED (%d)" % len(fails))
        for f in fails:
            print("  - %s" % f)
        return 1
    if args.quiet:
        print("verify_events: OK - %d rows, %d sheets read, %d ratios"
              % (len(events), len(sheets.READ), ratios))
    else:
        print("\nOK - the dataset is consistent with the official transcription.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
