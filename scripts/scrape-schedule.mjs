#!/usr/bin/env node
/* Morning scrape of the official Venetian schedule page.

   What it does: parses every published schedule row (date, time, event name, structure-sheet
   number), compares the parsed set against site-data/events.json using the canonical key
   `event_no + flight/section + date`, and writes:
     site-data/snapshots/schedule-live.json  - the parse, for audit
     site-data/schedule-diff.json            - added / removed / modified rows, or a clean state

   What it deliberately does not do: it never edits site-data/events.json. A structural parse of
   a marketing page is not strong enough to rewrite transcribed values on its own; a diff here
   means "read the cited sheet and re-run the generators".

   Usage: node scripts/scrape-schedule.mjs [--selftest] [--html <file>]
*/
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DATA = path.join(ROOT, "site-data");
const URL_SCHEDULE = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html";
const MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December";
const now = new Date().toISOString();

const clean = (s) =>
  String(s || "")
    .replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&#39;|&rsquo;|&rsquo/g, "'")
    .replace(/&quot;|&#8220;|&#8221;/g, '"').replace(/&ndash;|&mdash;/g, "-")
    .replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();

/** Parse schedule rows out of the official page HTML. Tolerant on purpose: a row is any table
 *  row that contains a long-form date, a clock time and a buy-in. */
export function parseRows(html) {
  const rows = [];
  const chunks = html.split(/<tr[^>]*>/i).slice(1);
  for (const chunk of chunks) {
    const body = chunk.split(/<\/tr>/i)[0];
    const text = clean(body);
    const dm = text.match(new RegExp("(" + MONTHS + ")\\s+(\\d{1,2}),?\\s+(20\\d\\d)", "i"));
    const tm = text.match(/\b(\d{1,2}):(\d{2})\s*([ap])\.?\s*m\.?/i);
    const sheet = body.match(/structure_(\d+)\.pdf/i);
    const links = [...body.matchAll(/<a[^>]*href="([^"]+)"[^>]*>([\s\S]*?)<\/a>/gi)].map((m) => ({
      href: m[1].startsWith("http") ? m[1] : new URL(m[1], URL_SCHEDULE).href, label: clean(m[2]),
    }));
    if (!dm || !tm) continue;
    const buy = text.match(/\$\s?(\d[\d,]*)/);
    // event name: the segment after the time cell up to the next date/link noise
    const afterTime = text.slice(text.indexOf(tm[0]) + tm[0].length);
    const name = afterTime.replace(new RegExp("(" + MONTHS + "\\s+\\d{1,2},?\\s*20\\d\\d)\\b.*$", "i"), "")
      .replace(/Structure Sheet|Read More|Details|PDF/i, "").replace(/[\s|·-]+$/, "").trim();
    if (!name) continue;
    const y = Number(dm[3]), mo = ["january","february","march","april","may","june","july","august","september","october","november","december"]
      .indexOf(dm[1].toLowerCase()) + 1;
    const iso = [String(y), String(mo).padStart(2, "0"), String(Number(dm[2])).padStart(2, "0")].join("-");
    const h24 = ((Number(tm[1]) % 12) + (tm[3].toLowerCase() === "p" ? 12 : 0));
    const flight = (name.match(/\b(1[A-Z])\b/) || name.match(/\bDay\s*([A-D])\b/i) || [])[0] || null;
    const eventNo = (name.match(/Event\s*#?\s*(\d{1,2})/i) || [])[1] || null;
    rows.push({
      date: iso, start: String(h24).padStart(2, "0") + ":" + tm[2], raw_time: tm[0],
      name, buy_in: buy ? Number(buy[1].replace(/,/g, "")) : null,
      sheet: sheet ? Number(sheet[1]) : null, flight, event_no_in_name: eventNo,
      links, key: (eventNo || "NA") + "|" + (flight || "-") + "|" + iso, text,
    });
  }
  return rows;
}

const parseGtd = (name) => {
  const m = String(name || "").match(/\$([\d,]+)\s*([Kk])?\s*GTD/i);
  if (!m) return null;
  return Number(m[1].replace(/,/g, "")) * (m[2] ? 1000 : 1);
};
const parseBuyin = (name) => {
  const m = String(name || "").match(/^\s*\$\s?([\d,]+)/);
  return m ? Number(m[1].replace(/,/g, "")) : null;
};

const norm = (s) => String(s || "").toLowerCase().replace(/\u2019/g, "'").replace(/[^a-z0-9$]+/g, " ").trim();
const keyOf = (date, start, name) => [date, start, norm(name)].join("|");

/** Compare against the dataset on `date + start + published name` - the three fields the schedule
 *  page itself prints. Event numbers are not used as a key because the page does not repeat them
 *  in every row; they are reported when present. */
function diffAgainstDataset(rows) {
  const events = JSON.parse(fs.readFileSync(path.join(DATA, "events.json"), "utf8")).events;
  const dataset = new Map();
  for (const e of events) {
    const flight = (e.name.match(/\b(1[A-Z])\b/) || [])[1] || null;
    dataset.set(keyOf(e.date, e.start, e.name), { ...e, flight, taken: false });
  }
  const added = [], removed = [], modified = [], renamed = [];
  for (const r of rows) {
    const k = keyOf(r.date, r.start, r.name);
    let d = dataset.get(k);
    if (!d) {
      // same date and start, different wording: report it as a rename, do not double-count it
      const twin = [...dataset.values()].find((x) => !x.taken && x.date === r.date && x.start === r.start);
      if (twin) {
        twin.taken = true;
        const gA = parseGtd(twin.name), gB = parseGtd(r.name);
        const bA = parseBuyin(twin.name), bB = parseBuyin(r.name);
        const deltas = [];
        if (gA != null && gB != null && gA !== gB) deltas.push(["gtd", gA, gB]);
        if (bA != null && bB != null && bA !== bB) deltas.push(["buy_in", bA, bB]);
        renamed.push({ date: r.date, start: r.start, event_no: twin.event_no, was: twin.name, now: r.name,
          value_deltas: deltas, sheet_url: twin.sheet_url || null,
          note: "same slot, different published wording - re-read the cited sheet before trusting the transcribed name" });
        d = twin;
      } else {
        added.push({ key: k, date: r.date, start: r.start, name: r.name, buy_in: r.buy_in, sheet: r.sheet,
          event_no_in_name: r.event_no_in_name });
        continue;
      }
    }
    d.taken = true;
    const changes = [];
    if (d.buy_in != null && r.buy_in != null && d.buy_in !== r.buy_in) changes.push(["buy_in", d.buy_in, r.buy_in]);
    if (d.sheet && r.sheet && d.sheet !== r.sheet) changes.push(["sheet", d.sheet, r.sheet]);
    const gLive = parseGtd(r.name);
    if (gLive != null && d.gtd != null && Math.abs(gLive - d.gtd) / d.gtd > 0.01) changes.push(["gtd", d.gtd, gLive]);
    if (changes.length) modified.push({ key: k, date: r.date, start: r.start, event_no: d.event_no, name: r.name, changes,
      sheet_url: d.sheet_url || null });
  }
  for (const [k, d] of dataset) if (!d.taken) removed.push({ key: k, date: d.date, start: d.start, name: d.name, event_no: d.event_no,
    note: "in the dataset but not found on the live page - confirm by hand before removing it from the site" });
  return { added, removed, modified, renamed };
}

async function main() {
  const args = process.argv.slice(2);
  if (args.includes("--selftest")) return selftest();
  let html;
  const htmlArg = args.indexOf("--html");
  if (htmlArg !== -1) html = fs.readFileSync(args[htmlArg + 1], "utf8");
  else {
    const res = await fetch(URL_SCHEDULE, {
      headers: { "User-Agent": "Mozilla/5.0 (compatible; Poker2PlannerRefresh/1.0; scheduled schedule scrape)", Accept: "text/html" },
      redirect: "follow", signal: AbortSignal.timeout(60_000),
    });
    if (!res.ok) throw new Error("schedule page returned HTTP " + res.status);
    html = await res.text();
  }
  const rows = parseRows(html);
  if (rows.length < 20) {
    // the page was redesigned or served a bot wall: refuse to conclude "nothing changed"
    const out = { checked: now, url: URL_SCHEDULE, state: "parse_failed", rows_parsed: rows.length,
      note: "Fewer rows than the minimum sanity threshold were parsed. Nothing was compared; read the page by hand before trusting the site's schedule.", added: [], removed: [], modified: [] };
    write(out, rows);
    console.error("PARSE FAILED: " + rows.length + " rows");
    return;
  }
  const d = diffAgainstDataset(rows);
  const state = d.added.length || d.removed.length || d.modified.length ? "changed" : "ok";
  write({
    checked: now, url: URL_SCHEDULE, state, rows_parsed: rows.length,
    rows_expected: JSON.parse(fs.readFileSync(path.join(DATA, "events.json"), "utf8")).events.length,
    counts: { added: d.added.length, removed: d.removed.length, modified: d.modified.length },
    interpretation: "added = published on the official page but absent from the dataset; removed = in the dataset but no longer published; modified = a published field disagrees with the transcribed value. Any of these requires reading the cited structure sheet and re-running scripts/build-events.py.",
    ...d,
  }, rows);
  console.log("schedule scrape: " + rows.length + " rows parsed, state " + state +
    " (+" + d.added.length + " / -" + d.removed.length + " / ~" + d.modified.length + ")");
}

function write(out, rows) {
  fs.mkdirSync(path.join(SNAP_DIR), { recursive: true });
  fs.writeFileSync(path.join(SNAP_DIR, "schedule-live.json"), JSON.stringify({ checked: now, url: URL_SCHEDULE, rows }, null, 1) + "\n");
  fs.writeFileSync(path.join(DATA, "schedule-diff.json"), JSON.stringify(out, null, 1) + "\n");
}
const SNAP_DIR = path.join(DATA, "snapshots");

function selftest() {
  const R = (date, time, name, sheet) =>
    '<tr><td>' + date + '</td><td>' + time + '</td><td>' + name + '</td>' +
    '<td><a href="/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_' + sheet + '.pdf">Structure Sheet</a></td></tr>';
  const fixture = "<table><tbody>" +
    R("Monday, November 16, 2026", "11:10 AM", "$300 No Limit Hold'em 1A $75K GTD", 10) +
    R("Wednesday, November 18, 2026", "11:10 AM", "$300 No Limit Hold'em $10K GTD (1Day)", 6) +
    R("Wednesday, November 18, 2026", "12:00 PM", "$300 No Limit Hold'em Day 2 Restart - field reduced", 10) +
    '<tr><td>totals</td><td colspan="3">More than $3.6 Million in guaranteed tournament prize pools</td></tr>' +
    "</tbody></table>";
  const rows = parseRows(fixture);
  const assert = (cond, msg) => { if (!cond) { console.error("SELFTEST FAIL: " + msg); process.exit(1); } };
  assert(rows.length === 3, "three schedule rows parsed, noise row ignored (got " + rows.length + ")");
  assert(rows[0].date === "2026-11-16", "long-form date to ISO");
  assert(rows[0].start === "11:10", "12h to 24h time");
  assert(rows[2].start === "12:00", "PM noon handling");
  assert(rows[0].sheet === 10 && rows[1].sheet === 6, "relative structure-sheet URL captured");
  assert(rows[0].flight === "1A", "flight suffix captured");
  assert(rows[0].buy_in === 300, "buy-in parsed from the name");
  assert(rows[0].links[0].href === "https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_10.pdf",
    "relative href resolved to the official host");
  const d = diffAgainstDataset(rows);
  assert(d.added.length === 0, "no phantom added rows, got " + JSON.stringify(d.added));
  assert(d.modified.length === 1 && d.modified[0].changes.some((c) => c[0] === "sheet" && c[1] === 5 && c[2] === 6),
    "a changed structure sheet is reported as modified: " + JSON.stringify(d.modified));
  assert(d.renamed.length === 1 && d.renamed[0].event_no === "01", "a wording change in the same slot is a rename, not a new event");
  assert(d.removed.length === 91, "unmatched dataset rows are reported as removed (fixture covers 3 of 94): got " + d.removed.length);
  console.log("selftest ok: parse + diff behaviour verified against the fixture and the real dataset");
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((e) => { console.error(String(e && e.stack || e)); process.exit(1); });
}
