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
    .replace(/[ \t]+/g, " ")
    .replace(/\n{2,}/g, "\n")
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

async function main() {
  fs.mkdirSync(SNAP, { recursive: true });
  const list = targets();
  const report = [];
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
      if (!prev) state = "new";
      else if (prev.hash !== hash) state = valueDiffs.length ? "changed" : "drifted";
      if (text) {
        for (const { key } of t.extract) {
          if (values[key] === null) state = state === "ok" ? "pattern-missing" : state;
        }
      }
      rec = {
        id: t.id, url: t.url, label: t.label, publisher: t.publisher, checked: now,
        http_status: status, content_type: type, bytes: buf.length, hash,
        state, binary: isBinary, values, value_diffs: valueDiffs,
        excerpt_hint: text ? text.slice(0, 400) : "(binary: hash-only check)",
        note: t.note,
      };
    } catch (err) {
      rec = {
        id: t.id, url: t.url, label: t.label, publisher: t.publisher, checked: now,
        state: prev ? "error" : "error-new", error: String(err && err.message || err),
        hash: prev ? prev.hash : null, values: prev ? prev.values : {}, value_diffs: [],
        note: "fetch failed; the previous snapshot is kept so the site still shows the last verified value",
      };
    }
    fs.writeFileSync(file, JSON.stringify(rec, null, 1) + "\n");
    report.push({
      id: rec.id, url: rec.url, label: rec.label, state: rec.state, checked: rec.checked,
      hash: rec.hash || null, value_diffs: rec.value_diffs || [], error: rec.error || null,
      binary: !!rec.binary, bytes: rec.bytes || null,
    });
    const mark = { ok: "=", new: "+", changed: "!", drifted: "~", "pattern-missing": "?", error: "x", "error-new": "X" }[rec.state] || "-";
    console.log(" " + mark + " " + rec.id.padEnd(16) + rec.state.padEnd(16) +
      (rec.value_diffs && rec.value_diffs.length ? JSON.stringify(rec.value_diffs) : "") + (rec.error ? " " + rec.error : ""));
  }

  const counts = {};
  for (const r of report) counts[r.state] = (counts[r.state] || 0) + 1;
  const actionNeeded = report.filter((r) => ["changed", "error", "error-new", "pattern-missing"].includes(r.state));
  const out = {
    last_run: now, generator: "scripts/check_sources.mjs", sources_checked: report.length,
    counts, needs_attention: actionNeeded.length,
    meaning: {
      ok: "content hash unchanged since the previous run",
      new: "first snapshot taken; nothing to compare yet",
      drifted: "the official page changed but none of the values this site depends on changed",
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

main().catch((e) => { console.error(String(e && e.stack || e)); process.exit(1); });
