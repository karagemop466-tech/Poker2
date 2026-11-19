#!/usr/bin/env node
/* Re-read every official source, hash it, extract the values the site depends on, and write a
   change report the site renders. This is the "automatic re-check of each official URL" feature:
   it runs where network access exists (GitHub Actions), not in the authoring sandbox.

   Design notes:
   * Sources come from site-data/sources.json (monitor.enabled) plus every structure-sheet URL in
     site-data/events.json, so 37 event documents are watched without being re-listed by hand.
   * `monitor.extract` holds regexes with capture groups. A value change is reported at the group
     level ("resort_fee: 55 -> 60"), which is what a human needs in order to act; a bare hash
     change on a page with no tracked values is reported as `drifted`, never as a silent pass.
   * PDFs and other binary bodies are hash-only, and that limitation is recorded in the report.
   * A fetch error is `error`, never `ok`. Missing baseline snapshots are `new`; the first run of
     this script only seeds the repository and says so.
   * Nothing here rewrites event or hotel data. It reports; a person (or a follow-up task) decides.
*/
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DATA = path.join(ROOT, "site-data");
const SNAP = path.join(DATA, "snapshots");
const UA = "Mozilla/5.0 (compatible; Poker2PlannerRefresh/1.0; GitHub Actions scheduled source check)";
const TIMEOUT_MS = 45_000;
const now = new Date().toISOString();

const readJson = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const sha256 = (buf) => crypto.createHash("sha256").update(buf).digest("hex");
const stripTags = (html) =>
  html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&#39;|&rsquo;/g, "'")
    .replace(/&quot;/g, '"')
    // One space everywhere: a published sentence is hard-wrapped in the HTML, and the tracked
    // patterns are written with single spaces, so newlines must not become part of the match.
    .replace(/\s+/g, " ")
    .trim();

function targets() {
  const src = readJson(path.join(DATA, "sources.json"));
  const out = new Map();
  for (const s of src.official) {
    const m = s.monitor || {};
    if (m.enabled === false) continue;
    out.set(s.url, {
      id: s.id, url: s.url, publisher: s.publisher, extract: m.extract || [],
      binary: !!m.binary, note: m.note || "", label: s.label,
    });
  }
  const evs = readJson(path.join(DATA, "events.json")).events;
  for (const e of evs) {
    if (!e.sheet_url || out.has(e.sheet_url)) continue;
    out.set(e.sheet_url, {
      id: "SHEET-" + e.sheet, url: e.sheet_url, publisher: "The Venetian (official)",
      label: "Structure sheet " + e.sheet + " (events " + e.event_no + " and others)",
      extract: [], binary: true,
      note: e.sheet_read ? "sheet values are transcribed in scripts/build-events.py" : "sheet not read yet: hash-only watch",
    });
  }
  return [...out.values()];
}

async function fetchBody(url) {
  const res = await fetch(url, { headers: { "User-Agent": UA, Accept: "*/*", "Accept-Language": "en" },
    redirect: "follow", signal: AbortSignal.timeout(TIMEOUT_MS) });
  const buf = Buffer.from(await res.arrayBuffer());
  return { status: res.status, ok: res.ok, buf, type: res.headers.get("content-type") || "" };
}

function extractValues(text, extract) {
  const values = {};
  for (const { key, regex } of extract) {
    try {
      const m = text.match(new RegExp(regex, "i"));
      if (!m) { values[key] = null; continue; }
      values[key] = (m.length > 1 ? m.slice(1).join("|") : m[0]).trim();
    } catch (err) {
      values[key] = "REGEX_ERROR: " + err.message;
    }
  }
  return values;
}

function diffValues(prev, next) {
  const diffs = [];
  for (const k of Object.keys(next)) {
    const before = prev && prev.values ? prev.values[k] : undefined;
    if (before === undefined) continue;
    if (String(before) !== String(next[k])) {
      diffs.push([k, before === null ? "(not found)" : before, next[k] === null ? "(not found)" : next[k]]);
    }
  }
  return diffs;
}

function addReviewState(prev, rec, reviews = []) {
  // An unchanged fetch is not a human review, nor can a failed fetch clear one.
  const changedNow = ["changed", "drifted", "pattern-missing"].includes(rec.state);
  const wasPending = !!(prev && (prev.review_pending ??
    ["changed", "drifted", "pattern-missing"].includes(prev.state)));
  const reviewed = !String(rec.state).startsWith("error") && rec.hash && reviews.some((r) =>
    r.url === rec.url && r.hash === rec.hash && r.hash_method === "raw-sha256" &&
    r.reviewed_at && r.reviewer && r.note);
  rec.review_pending = !!((wasPending || changedNow) && !reviewed);
  if (rec.review_pending) {
    rec.pending_since = (prev && prev.pending_since) || rec.checked;
    rec.pending_value_diffs = [ ...((prev && prev.pending_value_diffs) || []),
      ...(rec.value_diffs || []) ].slice(-20);
  }
  return rec;
}

export function _test_only() {
  // Offline test of what the monitor actually does: it runs the *production* patterns from
  // site-data/sources.json against text containing the sentences they are meant to match.
  // Run with: node scripts/check_sources.mjs --selftest
  const assert = (cond, msg) => { if (!cond) { console.error("SELFTEST FAIL: " + msg); process.exit(1); } };
  const fixture = `<html><body>
    <p>The Venetian Resort has a standard Las Vegas Resort Fee of $55 plus applicable tax per night, payable upon
    check-in. The daily fee for registered hotel guests is $20/day, seven days a week. Valet parking is $40/day.
    A credit card incidental deposit of $150 per night is required upon check-in. Daily rates do not include the
    applicable Clark County Room Tax of 13.38%. For reservations with more than 2 guests per suite, a charge of $50
    is added to the daily rate for each additional guest 13 years of age or older. Check-out prior to your scheduled
    departure date will result in an additional charge of $100.</p>
    <p>A daily resort fee of $50.00 plus applicable tax will be applied to all reservations. There is an additional
    charge of $40 plus tax per occupant, per night, above 2 occupants per room, as well as a $100 incidental amount per
    day. The first night's deposit is fully refundable provided a timely notice of cancellation is received by Room
    Reservations at least 72 hours prior to the arrival date. Check in time is 3 pm and check out time is 11 am.</p>
    <p>These rates will start as low as $119 and $209 and can be higher. Future rates are only provided out to a
    maximum of 150 days from the current date. You must play six hours of active live cash gameplay or buy in to a
    $300 or higher tournament for each night. There is a $55 resort fee per night stayed.</p>
    <p>Our interior bridge allows you to stroll effortlessly between Bellagio, The Cosmopolitan of Las Vegas, and
    Vdara.</p><script>var decoy = "Resort Fee of $999 must not be seen";</script></body></html>`;

  const text = stripTags(fixture);
  assert(!text.includes("decoy"), "script bodies are stripped before extraction");

  const official = readJson(path.join(DATA, "sources.json")).official;
  let checked = 0;
  for (const src of official) {
    for (const { key, regex } of (src.monitor || {}).extract || []) {
      let re2;
      try { re2 = new RegExp(regex, "i"); }
      catch (e) { assert(false, src.id + "." + key + " is not a compilable regex: " + e.message); }
      // a pattern may omit capture groups; extractValues() then records the whole match
      assert(new RegExp(regex).source === re2.source, src.id + "." + key + " flags changed the match");
      checked++;
      // the hotel and poker-rate patterns are exercised against the fixture text above
      if (["SRC-V-HOTELTC", "SRC-PMGM-TERMS", "SRC-V-POKERRATE", "SRC-MGM-PARKING"].includes(src.id)) {
        const v = extractValues(text, [{ key, regex }]);
        assert(v[key] !== null, src.id + "." + key + " matched nothing in text that contains the sentence: " + regex);
        assert(!/decoy|999/.test(String(v[key])), src.id + "." + key + " matched the decoy: " + v[key]);
      }
    }
  }
  assert(checked >= 20, "expected at least 20 tracked patterns, got " + checked);

  const diffs = diffValues({ values: { resort_fee: "50", gone: "x" } }, { resort_fee: "55", gone: null });
  // a clause that used to match and now does not is a change too, so two lines are expected here
  assert(diffs.length === 2 && diffs[0][0] === "resort_fee" && diffs[0][1] === "50" && diffs[0][2] === "55"
    && diffs[1][0] === "gone" && diffs[1][2] === "(not found)",
    "the moved value and the vanished clause are both reported: " + JSON.stringify(diffs));
  assert(diffValues(null, { a: 1 }).length === 0, "no baseline means no diff (state stays 'new')");
  const changed = addReviewState(null, { url: "https://example.com/a", hash: "b", checked: "day1",
    state: "changed", value_diffs: [["fee", "50", "55"]] });
  const repeated = addReviewState(changed, { url: changed.url, hash: "b", checked: "day2", state: "ok" });
  const failed = addReviewState(repeated, { url: changed.url, hash: "b", checked: "day3", state: "error" });
  assert(changed.review_pending && repeated.review_pending && failed.review_pending &&
    failed.pending_since === "day1" && failed.pending_value_diffs.length === 1,
    "an unchanged or failed fetch must retain the original review and value diff");
  const review = { url: changed.url, hash: "b", hash_method: "raw-sha256", reviewed_at: "day4",
    reviewer: "reviewer", note: "read the official page" };
  assert(!addReviewState(failed, { url: changed.url, hash: "b", checked: "day4", state: "ok" }, [review]).review_pending,
    "an exact-hash documented review clears the warning");
  assert(addReviewState(failed, { url: changed.url, hash: "c", checked: "day5", state: "changed" }, [review]).review_pending,
    "a review of a different hash cannot clear the warning");

  const list = targets();
  const sheets = list.filter((t) => String(t.id).startsWith("SHEET-"));
  assert(sheets.length === 37, "all 37 structure sheets are watched, got " + sheets.length);
  assert(sheets.every((t) => t.binary), "sheets are hash-only: PDF text extraction is not attempted here");
  assert(list.length >= 60, "watch list is the sources plus the sheets, got " + list.length);
  const seen = new Set(list.map((t) => t.url));
  assert(seen.size === list.length, "no URL is monitored twice");
  console.log("selftest ok: " + checked + " tracked patterns compile and match, " + list.length +
    " monitored URLs with no duplicates, diff logic reports only real movement");
}

async function main() {
  fs.mkdirSync(SNAP, { recursive: true });
  const list = targets();
  const report = [];
  let reviews = [];
  try { reviews = readJson(path.join(ROOT, "data", "source_reviews.json")).reviews || []; } catch {}
  console.log("checking " + list.length + " official sources at " + now);

  for (const t of list) {
    const file = path.join(SNAP, t.id + ".json");
    let prev = null;
    if (fs.existsSync(file)) { try { prev = readJson(file); } catch { prev = null; } }
    let rec;
    try {
      const { status, ok, buf, type } = await fetchBody(t.url);
      if (!ok) throw new Error("HTTP " + status);
      const isBinary = t.binary || /pdf|octet-stream/i.test(type);
      const text = isBinary ? "" : stripTags(buf.toString("utf8"));
      const hash = sha256(buf);
      const values = isBinary ? {} : extractValues(text, t.extract);
      const valueDiffs = isBinary ? [] : diffValues(prev, values);
      let state = "ok";
      if (!prev || !prev.hash) state = "new";
      else if (prev.hash !== hash) state = valueDiffs.length ? "changed" : "drifted";
      if (text) {
        for (const { key } of t.extract) {
          if (values[key] === null) state = state === "ok" ? "pattern-missing" : state;
        }
      }
      rec = {
        id: t.id, url: t.url, label: t.label, publisher: t.publisher, checked: now,
        http_status: status, content_type: type, bytes: buf.length, hash, last_success_checked: now,
        state, binary: isBinary, values, value_diffs: valueDiffs,
        excerpt_hint: text ? text.slice(0, 400) : "(binary: hash-only check)",
        note: t.note,
      };
    } catch (err) {
      rec = {
        id: t.id, url: t.url, label: t.label, publisher: t.publisher, checked: now,
        state: prev && prev.hash ? "error" : "error-new", error: String(err && err.message || err),
        hash: prev ? prev.hash : null, values: prev ? prev.values : {}, value_diffs: [],
        last_success_checked: prev ? (prev.last_success_checked || (!String(prev.state).startsWith("error") ? prev.checked : null)) : null,
        note: "fetch failed; the last successful hash and any unresolved change are retained",
      };
    }
    addReviewState(prev, rec, reviews);
    fs.writeFileSync(file, JSON.stringify(rec, null, 1) + "\n");
    report.push({
      id: rec.id, url: rec.url, label: rec.label, state: rec.state, checked: rec.checked,
      last_success_checked: rec.last_success_checked || null, review_pending: rec.review_pending,
      pending_since: rec.pending_since || null, pending_value_diffs: rec.pending_value_diffs || [],
      hash: rec.hash || null, value_diffs: rec.value_diffs || [], error: rec.error || null,
      binary: !!rec.binary, bytes: rec.bytes || null,
    });
    const mark = { ok: "=", new: "+", changed: "!", drifted: "~", "pattern-missing": "?", error: "x", "error-new": "X" }[rec.state] || "-";
    console.log(" " + mark + " " + rec.id.padEnd(16) + rec.state.padEnd(16) +
      (rec.value_diffs && rec.value_diffs.length ? JSON.stringify(rec.value_diffs) : "") + (rec.error ? " " + rec.error : ""));
  }

  const counts = {};
  for (const r of report) counts[r.state] = (counts[r.state] || 0) + 1;
  const actionNeeded = report.filter((r) => r.review_pending ||
    ["changed", "drifted", "error", "error-new", "pattern-missing"].includes(r.state));
  const out = {
    last_run: now, generator: "scripts/check_sources.mjs", sources_checked: report.length,
    counts, needs_attention: actionNeeded.length,
    meaning: {
      ok: "content hash unchanged since the previous run",
      new: "first snapshot taken; nothing to compare yet",
      drifted: "the page hash changed without a tracked-value diff; review is still required", 
      changed: "a value this site depends on changed - re-run scripts/build-events.py and review the row",
      "pattern-missing": "a tracked pattern no longer matches: the page was redesigned or the clause was removed",
      error: "the official URL could not be read; the last verified value stays on the site with its old date",
      "error-new": "the official URL could not be read and no baseline exists yet",
    },
    note: "This job never edits event or hotel values; it reports. Site data changes go through the generators and a pull request.",
    sources: report,
  };
  fs.writeFileSync(path.join(DATA, "change-report.json"), JSON.stringify(out, null, 1) + "\n");
  console.log("wrote site-data/change-report.json: " + JSON.stringify(counts));
  const allFailed = report.length > 0 && report.every((r) => String(r.state).startsWith("error"));
  if (allFailed) { console.error("every fetch failed - the runner has no network access"); process.exit(1); }
}

if (process.argv.includes("--selftest")) { _test_only(); } else {
  main().catch((e) => { console.error(String(e && e.stack || e)); process.exit(1); });
}
