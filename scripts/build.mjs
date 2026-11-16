// Static site generator for the Poker2 GitHub Pages site.
// Reads data/*.json and writes HTML pages at the repo root (served from main, path /).
// Fails the build if any table row lacks an official source link, or if any
// internal link points to a page that does not exist.
//
// Usage: node scripts/build.mjs

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => JSON.parse(fs.readFileSync(path.join(ROOT, p), "utf8"));

const T = read("data/tournaments.json");
const H = read("data/hotels.json");
const F = read("data/flags.json");
const Q = read("data/questions.json");
const S = read("data/suggestions.json");
const SUM = read("data/summary.json");
const SRC = read("data/sources.json");

const AS_OF = T.as_of;
const OFFICIAL_HOSTS = ["venetianlasvegas.com", "wynnlasvegas.com", "visitwynn.com", "cdn.wynnresorts.com", "api.github.com", "github.com"];
const ALLOWED_PREFIX_NOTE = "Official host required for every table source.";

const VEN_SCHED = "https://www.venetianlasvegas.com/resort/casino/poker/deepstack-extravaganza-poker-tournament/dse-nov-2026.html";
const venStruct = (n) => `https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_${n}.pdf`;
const WPT_SCHED = "https://cdn.wynnresorts.com/image/upload/v1757097329/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Schedule.pdf";
const WPT_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1750864036/visitwynn_pdfs_files/Poker/WPT/WPT_World_Championship_Structures.pdf";
const DAILY_POSTER = "https://cdn.wynnresorts.com/image/upload/v1752011166/visitwynn_pdfs_files/Poker/Daily%20Tournaments/poker-daily-tournament-poster.pdf";
const DAILY_STRUCT = "https://cdn.wynnresorts.com/image/upload/v1752011191/visitwynn_pdfs_files/Poker/Daily%20Tournaments/Poker-All_Daily_Structures.pdf";

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const money = (n) => (n === null || n === undefined || n === "" ? "" : "$" + Number(n).toLocaleString("en-US"));
const hostOf = (u) => new URL(u).hostname.replace(/^www\./, "");
const isOfficial = (u) => OFFICIAL_HOSTS.some((h) => hostOf(u) === h || hostOf(u).endsWith("." + h));

// ---- source resolution for tournament rows ----
function sourcesFor(r) {
  const out = [];
  if (r.src === "ven") {
    out.push({ label: "Official schedule", url: VEN_SCHED });
    if (typeof r.struct === "number") out.push({ label: `Structure sheet ${r.struct}`, url: venStruct(r.struct) });
  } else if (r.src === "wynn_daily") {
    out.push({ label: "Official poster", url: DAILY_POSTER });
    out.push({ label: "Official structure sheets", url: DAILY_STRUCT });
  } else if (r.src === "wynn_wpt") {
    out.push({ label: "Official schedule", url: WPT_SCHED });
    if (r.struct === "wpt_structures") out.push({ label: "Official structure sheets", url: WPT_STRUCT });
  }
  return out;
}
const srcLinks = (list) => list.map((s) => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a>`).join("<br>");

// ---- value computations (computed from official buy-in and guarantee) ----
const valueX = (r) => (r.gtd && r.buy_in ? Math.round((r.gtd / r.buy_in) * 100) / 100 : null);
const poolAfterFee = (r) => (typeof r.fee === "number" ? r.buy_in - r.fee : null);

// ---- verification checks ----
const problems = [];
function checkRow(list, r, label) {
  const s = sourcesFor(r);
  if (!s.length) problems.push(`${label}: row ${r.id} has no source`);
  s.forEach((x) => { if (!isOfficial(x.url)) problems.push(`${label}: ${r.id} non-official source ${x.url}`); });
}
T.single_entry.forEach((r) => checkRow(T.single_entry, r, "single"));
T.excluded.forEach((r) => checkRow(T.excluded, r, "excluded"));
T.unverified.forEach((r) => checkRow(T.unverified, r, "unverified"));
H.rows.forEach((h) => h.sources.forEach((s) => { if (!isOfficial(s.url)) problems.push(`hotel ${h.id}: non-official ${s.url}`); }));
SRC.items.forEach((s) => { if (!isOfficial(s.url) && s.group !== "Repo" && s.group !== "Coordination") problems.push(`source list: non-official ${s.url}`); });
F.items.forEach((f) => { if (!f.source || !/^https:\/\//.test(f.source)) problems.push(`flag ${f.id}: missing source`); });

// ---- site chrome ----
const NAV = [
  { href: "index.html", label: "Home" },
  { href: "tournaments/single-entry.html", label: "Single-entry" },
  { href: "tournaments/excluded.html", label: "Excluded" },
  { href: "tournaments/unverified.html", label: "Unverified" },
  { href: "schedule/index.html", label: "Venetian schedule" },
  { href: "hotels/index.html", label: "Hotels" },
  { href: "summary/index.html", label: "Summary" },
  { href: "questions/index.html", label: "Questions" },
  { href: "suggestions/index.html", label: "Suggestions" },
  { href: "flagged/index.html", label: "Flagged for Review", flag: true },
  { href: "sources/index.html", label: "Sources" },
];

function layout({ depth, title, active, body }) {
  const pre = "../".repeat(depth);
  const nav = NAV.map((n) => `<a href="${pre}${n.href}" class="${n.href === active ? "on" : ""}${n.flag ? " flagnav" : ""}">${esc(n.label)}</a>`).join("");
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)} · Las Vegas Strip Poker Dashboard</title>
<link rel="stylesheet" href="${pre}assets/style.css">
</head>
<body>
<header class="top">
  <div class="brand"><a href="${pre}index.html">Las Vegas Strip Poker Dashboard</a><span class="asof">Data as of ${AS_OF}</span></div>
  <nav>${nav}</nav>
</header>
<main>
${body}
</main>
<footer>
  <p>Every table row links to an official source. Values that could not be confirmed from an official source are left blank and marked UNVERIFIED. Not a betting or financial product. Confirm with the venue before paying.</p>
  <p>Built from <code>data/*.json</code> by <code>scripts/build.mjs</code>. Repo: <a href="https://github.com/karagemop466-tech/Poker2">karagemop466-tech/Poker2</a>.</p>
</footer>
<script src="${pre}assets/app.js"></script>
</body>
</html>
`;
}

// ---- generic table ----
function table(id, cols, rows) {
  const head = cols.map((c, i) => `<th data-i="${i}" class="${c.num ? "num" : ""}">${esc(c.label)}</th>`).join("");
  const body = rows.map((r) => `<tr>${cols.map((c) => {
    const v = c.get(r);
    const sv = c.sort ? c.sort(r) : "";
    const cls = c.num ? "num" : "";
    const content = c.html ? v : esc(v);
    return `<td class="${cls}" data-v="${esc(sv)}">${content ?? ""}</td>`;
  }).join("")}</tr>`).join("\n");
  return `<div class="tablewrap"><input class="filter" data-for="${id}" placeholder="Filter rows…" type="search" aria-label="Filter rows">
<table id="${id}" class="sortable"><thead><tr>${head}</tr></thead><tbody>
${body}
</tbody></table></div>`;
}

const pct = (v) => (v === null ? "" : (v * 100).toFixed(1) + "%");
const xval = (v) => (v === null ? "" : v.toFixed(2) + "×");

// ---- tournament page columns ----
function singleRows() {
  return T.single_entry.map((r) => ({ ...r, _v: valueX(r) ?? 0 })).sort((a, b) => b._v - a._v || a.date.localeCompare(b.date));
}
const singleTable = () => {
  const rows = singleRows();
  const cols = [
    { label: "Rank", get: (r) => rows.indexOf(r) + 1, num: true, sort: (r) => rows.indexOf(r) + 1 },
    { label: "Date", get: (r) => `${r.date} (${r.day})`, sort: (r) => r.date },
    { label: "Start", get: (r) => r.start, sort: (r) => r.start },
    { label: "Event #", get: (r) => r.event },
    { label: "Event", get: (r) => r.name },
    { label: "Buy-in", get: (r) => money(r.buy_in), num: true, sort: (r) => r.buy_in },
    { label: "Guarantee", get: (r) => money(r.gtd), num: true, sort: (r) => r.gtd },
    { label: "GTD ÷ buy-in (computed)", get: (r) => xval(valueX(r)), num: true, sort: (r) => valueX(r) },
    { label: "House fee (sheet)", get: (r) => money(r.fee), num: true, sort: (r) => r.fee },
    { label: "Prize pool after fee (computed)", get: (r) => money(poolAfterFee(r)), num: true, sort: (r) => poolAfterFee(r) },
    { label: "Note", get: (r) => r.note },
    { label: "Sources", get: (r) => srcLinks(sourcesFor(r)), html: true },
  ];
  return table("single", cols, rows);
};

const excludedCols = [
  { label: "Property", get: (r) => r.property },
  { label: "Date(s)", get: (r) => r.date },
  { label: "Start", get: (r) => r.start },
  { label: "Event #", get: (r) => r.event },
  { label: "Event", get: (r) => r.name },
  { label: "Buy-in", get: (r) => money(r.buy_in), num: true, sort: (r) => r.buy_in ?? 0 },
  { label: "Guarantee", get: (r) => money(r.gtd), num: true, sort: (r) => r.gtd ?? 0 },
  { label: "Why excluded", get: (r) => r.reason },
  { label: "Sources", get: (r) => srcLinks(sourcesFor(r)), html: true },
];
const unverifiedCols = [
  { label: "Property", get: (r) => r.property },
  { label: "Date", get: (r) => `${r.date} (${r.day})` },
  { label: "Start", get: (r) => r.start },
  { label: "Event #", get: (r) => r.event },
  { label: "Event", get: (r) => r.name },
  { label: "Buy-in", get: (r) => money(r.buy_in), num: true, sort: (r) => r.buy_in ?? 0 },
  { label: "Guarantee", get: (r) => money(r.gtd), num: true, sort: (r) => r.gtd ?? 0 },
  { label: "Verification status", get: (r) => r.reason },
  { label: "Sources", get: (r) => srcLinks(sourcesFor(r)), html: true },
];

// ---- pages ----
const pages = {};

pages["index.html"] = layout({ depth: 0, title: "Home", active: "index.html", body: `
<section class="hero">
  <h1>Las Vegas Strip poker: single-entry tournaments and hotel costs</h1>
  <p class="lede">A verified dashboard of live poker tournaments at The Venetian and Wynn Las Vegas, with a separate section for re-entry, rebuy, add-on and multi-flight events. Every row links to an official source. Unverified values are blank and flagged.</p>
  <p class="note">Coverage in this release: The Venetian and Wynn Las Vegas only. Other Strip rooms are not yet covered (see Flagged for Review).</p>
</section>
<section class="cards">
  <a class="card" href="tournaments/single-entry.html"><span class="k">${T.single_entry.length}</span><span class="t">Verified single-entry events</span><span class="s">The Venetian, Nov 18 – Dec 23, 2026</span></a>
  <a class="card" href="tournaments/excluded.html"><span class="k">${T.excluded.length}</span><span class="t">Excluded (re-entry, rebuy, multi-flight, satellites)</span><span class="s">Separate section, not ranked</span></a>
  <a class="card" href="tournaments/unverified.html"><span class="k">${T.unverified.length}</span><span class="t">Unverified tournament rows</span><span class="s">Official schedule value; rules not checked</span></a>
  <a class="card" href="schedule/index.html"><span class="k">11:10 AM</span><span class="t">Earliest verified single-entry start</span><span class="s">No verified 8 AM start exists</span></a>
  <a class="card" href="hotels/index.html"><span class="k">$55 + tax</span><span class="t">Resort fee at The Venetian and Wynn</span><span class="s">Official terms; room rates unverified</span></a>
  <a class="card" href="summary/index.html"><span class="k">→</span><span class="t">Executive summary</span><span class="s">Key findings and sources</span></a>
  <a class="card" href="questions/index.html"><span class="k">${Q.items.length}</span><span class="t">Questions to answer</span><span class="s">What is missing before deciding</span></a>
  <a class="card" href="suggestions/index.html"><span class="k">${S.items.length}</span><span class="t">Suggestions (awaiting decision)</span><span class="s">Nothing implemented yet</span></a>
  <a class="card flag" href="flagged/index.html"><span class="k">${F.items.length}</span><span class="t">Flagged for Review</span><span class="s">Irregularities and unverified items, with sources</span></a>
  <a class="card" href="sources/index.html"><span class="k">${SRC.items.length}</span><span class="t">Official sources</span><span class="s">Every link used</span></a>
</section>
<section>
  <h2>How to use this site</h2>
  <ol>
    <li>Start with <a href="tournaments/single-entry.html">Single-entry</a>. Rows are ranked by guarantee divided by buy-in (computed from official figures).</li>
    <li>Check <a href="tournaments/excluded.html">Excluded</a> for events with re-entry, rebuys, add-ons or extra flights. They are kept out of the ranking.</li>
    <li>Use <a href="schedule/index.html">Venetian schedule</a> to plan a day. Start times are official; event length is not verified.</li>
    <li>Answer the open items on <a href="questions/index.html">Questions</a> before booking. Review <a href="flagged/index.html">Flagged for Review</a> for irregularities.</li>
  </ol>
</section>
` });

pages["tournaments/single-entry.html"] = layout({ depth: 1, title: "Single-entry tournaments", active: "tournaments/single-entry.html", body: `
<h1>Single-entry tournaments (verified)</h1>
<p class="note">${esc(T.notes.single_entry)} Ranked by guarantee ÷ buy-in (computed). Bounty and PKO guarantees include bounty money. Venetian DeepStack Extravaganza IV, Nov 16 – Dec 23, 2026.</p>
${singleTable()}
<p class="small">Source of every row: the official Venetian schedule and the structure sheet listed in the row. Click a column header to sort.</p>
` });

pages["tournaments/excluded.html"] = layout({ depth: 1, title: "Excluded tournaments", active: "tournaments/excluded.html", body: `
<h1>Excluded: re-entry, rebuy, add-on, multi-flight and satellites</h1>
<p class="note">${esc(T.notes.excluded)}</p>
<h2>Excluded rows</h2>
${table("excl", excludedCols, T.excluded)}
` });

pages["tournaments/unverified.html"] = layout({ depth: 1, title: "Unverified tournaments", active: "tournaments/unverified.html", body: `
<h1>Unverified tournaments</h1>
<p class="note">${esc(T.notes.unverified)}</p>
<h2>Venetian (structure sheet not reviewed)</h2>
${table("unv-v", unverifiedCols, T.unverified.filter((r) => r.property === "The Venetian"))}
<h2>Wynn Las Vegas — WPT World Championship (structure sheets not reviewed)</h2>
${table("unv-w", unverifiedCols, T.unverified.filter((r) => r.property !== "The Venetian"))}
` });

// schedule (Venetian, verified + unverified, by date/time)
const schedRows = [...T.single_entry.map((r) => ({ ...r, _status: "Verified single-entry" })), ...T.unverified.filter((r) => r.property === "The Venetian").map((r) => ({ ...r, _status: "UNVERIFIED (structure not reviewed)" }))]
  .sort((a, b) => a.date.localeCompare(b.date) || timeKey(a.start) - timeKey(b.start));
function timeKey(s) { const m = /(\d+):(\d+)\s*(AM|PM)/i.exec(s || ""); if (!m) return 0; let h = +m[1] % 12; if (/PM/i.test(m[3])) h += 12; return h * 60 + +m[2]; }
pages["schedule/index.html"] = layout({ depth: 1, title: "Venetian schedule", active: "schedule/index.html", body: `
<h1>Venetian day planner (official start times)</h1>
<p class="note">Start times and buy-ins come from the official Venetian schedule. Event length is not verified, so the gaps between events cannot be confirmed. The earliest start in this list is ${esc(schedRows.map((r) => r.start).sort((a, b) => timeKey(a) - timeKey(b))[0])}. No option starts at 8:00 AM.</p>
<p class="note">Days with verified single-entry events: ${new Set(T.single_entry.map((r) => r.date)).size}. Rows are sorted by date and then by start time. The Status column separates verified rows from UNVERIFIED rows.</p>
${table("sched", [
  { label: "Date", get: (r) => `${r.date} (${r.day})`, sort: (r) => r.date },
  { label: "Start", get: (r) => r.start, sort: (r) => timeKey(r.start) },
  { label: "Event #", get: (r) => r.event },
  { label: "Event", get: (r) => r.name },
  { label: "Buy-in", get: (r) => money(r.buy_in), num: true, sort: (r) => r.buy_in ?? 0 },
  { label: "Guarantee", get: (r) => money(r.gtd), num: true, sort: (r) => r.gtd ?? 0 },
  { label: "Status", get: (r) => r._status },
  { label: "Sources", get: (r) => srcLinks(sourcesFor(r)), html: true },
], schedRows)}
` });

// hotels
pages["hotels/index.html"] = layout({ depth: 1, title: "Hotels", active: "hotels/index.html", body: `
<h1>Hotels near the tournaments</h1>
<p class="note">Resort fees are verified from official terms. Nightly room rates, walking times and quality ratings are NOT verified and are left blank. The "true cost per night" needs an official nightly rate for the chosen dates.</p>
${table("hot", [
  { label: "Hotel", get: (h) => h.hotel },
  { label: "Tournament venue", get: (h) => h.tournament_site },
  { label: "Walk to tournament venue", get: (h) => h.walk_to_poker_room_status },
  { label: "Nightly room rate", get: (h) => h.nightly_room_rate || "UNVERIFIED", num: false },
  { label: "Resort fee (official)", get: (h) => h.resort_fee_official },
  { label: "Resort fee + 13.38% (computed)", get: (h) => money(h.resort_fee_with_13_38_tax_computed), num: true, sort: (h) => h.resort_fee_with_13_38_tax_computed },
  { label: "Parking / deposit (official)", get: (h) => `${h.parking} ${h.incidental_deposit}` },
  { label: "Quality rating", get: (h) => h.quality_rating || "UNVERIFIED" },
  { label: "True cost per night", get: (h) => h.true_cost_per_night || "UNVERIFIED" },
  { label: "Sources", get: (h) => srcLinks(h.sources), html: true },
], H.rows)}
<h2>Notes</h2>
<ul>
  <li>${esc(H.clark_county_room_tax_note)}</li>
  <li>${esc(H.rows[0].resort_fee_computed_note)}</li>
  <li>${esc(H.rows[1].resort_fee_computed_note)}</li>
  <li>Walking times: ${esc(H.rows[0].walk_to_poker_room_status)} ${esc(H.rows[1].walk_to_poker_room_status)}</li>
</ul>
` });

// summary
pages["summary/index.html"] = layout({ depth: 1, title: "Executive summary", active: "summary/index.html", body: `
<h1>${esc(SUM.title)}</h1>
<p class="note">${esc(SUM.scope)}</p>
<section class="cards small-cards">
${SUM.headline_numbers.map((h) => `<div class="card static"><span class="k">${esc(h.value)}</span><span class="t">${esc(h.label)}</span><span class="s">${esc(h.note)}</span></div>`).join("")}
</section>
<h2>Findings</h2>
${SUM.findings.map((f) => `<section class="finding"><h3>${esc(f.title)}</h3><p>${esc(f.text)}</p><p class="small">Sources: ${srcLinksPlain(f.sources)}</p></section>`).join("")}
<h2>Recommendation</h2>
<p>${esc(SUM.recommendation)}</p>
` });

function srcLinksPlain(urls) { return urls.map((u, i) => `<a href="${esc(u)}" target="_blank" rel="noopener">[${i + 1}]</a>`).join(" "); }

// questions
pages["questions/index.html"] = layout({ depth: 1, title: "Questions", active: "questions/index.html", body: `
<h1>Questions to answer before deciding</h1>
<p class="note">${esc(Q.intro)}</p>
${table("qa", [
  { label: "ID", get: (q) => q.id },
  { label: "Question", get: (q) => q.question },
  { label: "Status", get: (q) => q.status },
  { label: "What the data shows", get: (q) => q.answer },
  { label: "Still needed", get: (q) => q.needed },
  { label: "How to find it", get: (q) => q.how_to_find },
  { label: "Sources", get: (q) => (q.sources.length ? q.sources.map((u, i) => `<a href="${esc(u)}" target="_blank" rel="noopener">[${i + 1}]</a>`).join(" ") : "—"), html: true },
], Q.items)}
` });

// suggestions
pages["suggestions/index.html"] = layout({ depth: 1, title: "Suggestions", active: "suggestions/index.html", body: `
<h1>Suggestions (review before any change)</h1>
<p class="note">${esc(S.intro)} Nothing on this page has been implemented.</p>
${S.items.map((s) => `<section class="sugg"><h3>${esc(s.id)} · ${esc(s.title)} <span class="pill">${esc(s.category)}</span></h3>
<ul>${s.options.map((o) => `<li>${esc(o)}</li>`).join("")}</ul>
<p class="small"><b>Trade-off:</b> ${esc(s.tradeoff)} · <b>Status:</b> ${esc(s.status)}</p></section>`).join("")}
` });

// flagged for review
pages["flagged/index.html"] = layout({ depth: 1, title: "Flagged for Review", active: "flagged/index.html", body: `
<h1>Flagged for Review</h1>
<p class="note">${esc(F.intro)} This page is the review list for the owner. Flagged items do not block the site.</p>
${table("flags", [
  { label: "ID", get: (f) => f.id },
  { label: "Area", get: (f) => f.area },
  { label: "Severity", get: (f) => f.severity },
  { label: "Issue", get: (f) => f.title },
  { label: "Detail", get: (f) => f.detail },
  { label: "Source", get: (f) => `<a href="${esc(f.source)}" target="_blank" rel="noopener">${esc(f.source_label)}</a>`, html: true },
], F.items)}
` });

// sources
pages["sources/index.html"] = layout({ depth: 1, title: "Sources", active: "sources/index.html", body: `
<h1>Sources</h1>
<p class="note">${esc(SRC.intro)} Accessed ${SRC.accessed}.</p>
${table("src", [
  { label: "Group", get: (s) => s.group },
  { label: "Source", get: (s) => s.label },
  { label: "Link", get: (s) => `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.url)}</a>`, html: true },
], SRC.items)}
` });

// landing page is at root; subpages in folders
// ---- write files ----
if (problems.length) {
  console.error("VERIFICATION FAILED:\n" + problems.join("\n"));
  process.exit(1);
}

for (const [rel, html] of Object.entries(pages)) {
  const full = path.join(ROOT, rel);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, html);
}
fs.writeFileSync(path.join(ROOT, ".nojekyll"), "");
console.log(`Built ${Object.keys(pages).length} pages. Verification passed: every table source is an official host.`);
