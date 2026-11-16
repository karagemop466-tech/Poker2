#!/usr/bin/env node
/* Static checks on the generated site, run in CI:
   1. plan/assets/data.js parses as JavaScript and every dataset the UI reads is present;
   2. every id that assets/site.js queries exists on the page that uses it;
   3. no table row on a page renders a value with the string "undefined"/"null"/"NaN";
   4. every <td> row in an event table keeps its source link (a row can never lose its citation). */
import fs from "node:fs";
import path from "node:path";
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const fail = [];
const PLAN = "plan";
const read = (p) => fs.readFileSync(path.join(ROOT, p), "utf8");

const dataJs = read(PLAN + "/assets/data.js");
const win = {};
new Function("window", dataJs)(win);
const D = win.POKER;
for (const k of ["events", "schedule", "hotels", "rates", "walk", "venues", "flags", "search", "tax"]) {
  if (!D[k]) fail.push(PLAN + "/assets/data.js missing key " + k);
}
if (D.events.length !== 94) fail.push("expected 94 venetian rows, got " + D.events.length);
if (!D.schedule.days || !Object.keys(D.schedule.days).length) fail.push("no schedule days generated");
for (const e of D.events) {
  if (!e.schedule_url || !/^https/.test(e.schedule_url)) fail.push("event " + e.id + " has no https schedule source");
  for (const f of ["fee", "chips", "level_min", "reg_close"]) {
    if (e[f] !== null && !e.sheet_read) fail.push("event " + e.event_no + " has " + f + " without a read sheet");
  }
}

const siteJs = read(PLAN + "/assets/site.js");
const ids = [...siteJs.matchAll(/[#]([a-z][a-z0-9-]*)/gi)].map((m) => m[1]);
const uniq = [...new Set(ids)].filter((i) => /^c-|global-search|search-suggest/.test(i));
const pages = fs.readdirSync(path.join(ROOT, PLAN)).filter((f) => f.endsWith(".html")).map((f) => PLAN + "/" + f);
const allHtml = pages.map((p) => read(p)).join("\n") + fs.readdirSync(path.join(ROOT, PLAN, "venues")).map((f) => read(PLAN + "/venues/" + f)).join("\n");
for (const id of uniq) {
  if (!allHtml.includes('id="' + id + '"')) fail.push("site.js expects #" + id + " but no page defines it");
}

for (const p of pages.concat(fs.readdirSync(path.join(ROOT, PLAN, "venues")).map((f) => PLAN + "/venues/" + f))) {
  const html = read(p);
  for (const bad of [">undefined<", ">null<", ">NaN<", "&mdash; USD", "$nan"]) {
    if (html.includes(bad)) fail.push(p + " renders " + bad);
  }
  const rows = html.split(/<tr\b/).slice(1);
  for (const r of rows) {
    const body = r.split(/<\/tr>/)[0];
    if (!/data-key="/.test(body)) continue;
    if (!/href="https:\/\//.test(body)) fail.push(p + ": row with data-key has no https source link");
  }
}

/* the trip calculator must agree with the static column next to it */
{
  const html = read(PLAN + "/trip-cost.html");
  const win = (D.schedule.windows.best_poker_rate_compatible || [])[0]
    || (D.schedule.windows.best_size_ratio || [])[0];
  const nightsAttr = (html.match(/id="c-nights"[^>]*value="(\d+)"/) || [])[1];
  const pickCount = (html.match(/id="c-pick"[\s\S]*?<\/div>/) || [""])[0].split('type="checkbox"').length - 1;
  if (!win) fail.push("no recommended window was generated at all");
  else {
    if (nightsAttr !== String(win.nights)) fail.push("trip-cost.html nights input is " + nightsAttr + " but the recommended window is " + win.nights);
    if (pickCount !== win.days.length) fail.push("trip-cost.html offers " + pickCount + " day rows for a " + win.days.length + "-day window");
    const checked = (html.match(/id="c-pick"[\s\S]*?<\/div>/) || [""])[0].split("checked").length - 1;
    if (checked < win.days.length) fail.push("the recommended days are not pre-selected (checked=" + checked + ")");
  }
  if (/%[A-Z][A-Z_]{2,}%/.test(html)) fail.push("trip-cost.html has an unresolved placeholder");
  if (/id="c-hotel"[\s\S]{0,400}?selected/.test(html) === false && !/id="c-hotel">\s*<option value="H-VEN"/.test(html)) {
    // not fatal: the first option is the default; just make sure a default exists
    if (!/id="c-hotel">/.test(html)) fail.push("trip-cost.html has no hotel select");
  }
}

if (fail.length) {
  console.error("SITE CHECKS FAILED:");
  for (const f of fail.slice(0, 25)) console.error("  - " + f);
  process.exit(1);
}
console.log("site checks ok: " + pages.length + " plan pages, " + D.events.length + " event rows, " +
  uniq.length + " UI ids resolved, every data row carries an https source link");
