/* Self-test for the site-wide search: run 2026/assets/site2026.js against a minimal DOM stub and
   assert the box actually filters the committed search index and links back to the right page and
   row. Without this, a broken box can still render as a tidy empty panel that looks like a page
   with nothing to say. */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const js = fs.readFileSync(path.join(ROOT, "2026/assets/site2026.js"), "utf8");
const idxSrc = fs.readFileSync(path.join(ROOT, "2026/assets/search-index.js"), "utf8");

function el(id, extra = {}) {
  return Object.assign({
    id, value: "", textContent: "", innerHTML: "", checked: false,
    listeners: {},
    classList: { toggle() {}, remove() {}, add() {}, contains: () => false },
    getAttribute: () => null, setAttribute() {}, appendChild() {}, querySelector: () => null,
    focus() {},
    addEventListener(t, f) { (this.listeners[t] ||= []).push(f); },
    fire(t) { (this.listeners[t] || []).forEach((f) => f()); },
  }, extra);
}

const box = el("gs"), res = el("gs-res"), stat = el("gs-status"), clr = el("gs-clear");
const byId = { gs: box, "gs-res": res, "gs-status": stat, "gs-clear": clr };

global.document = {
  querySelector: (s) => byId[s.replace(/^#/, "")] || null,
  querySelectorAll: () => [],
  createElement: () => ({
    set textContent(v) {
      this._v = String(v).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
    },
    get textContent() { return this._v; },
    get innerHTML() { return this._v; },
  }),
};
global.location = { pathname: "/Poker2/2026/tournaments.html" };
global.window = {};
eval(idxSrc);
eval(js);

const checks = [];
const total = global.window.SEARCH_INDEX.length;
checks.push(["index is committed and non-empty", total > 400]);

box.value = "wynn";
box.fire("input");
checks.push(["finds the Wynn hotel rows", /Wynn/.test(res.innerHTML) && /hotels\.html/.test(res.innerHTML)]);

box.value = "resort fee";
box.fire("input");
checks.push(["multi-word query reports matches", /match/.test(stat.textContent)]);

box.value = "deepstack";
box.fire("input");
checks.push(["top-level page links stay relative", !/href="\.\.\//.test(res.innerHTML)]);

// same script on a venue subpage: every result link must climb one level
global.location = { pathname: "/Poker2/2026/venues/venetian.html" };
box.value = "wynn";
box.fire("input");
const hrefs = [...res.innerHTML.matchAll(/href="([^"]+)"/g)].map((m) => m[1]);
checks.push(["venue subpage links climb to /2026/", hrefs.length > 0 && hrefs.every((h) => h.startsWith("../"))]);
global.location = { pathname: "/Poker2/2026/tournaments.html" };

box.value = "zzzznotathing";
box.fire("input");
checks.push(["no-match reports zero rather than going blank", /^0 rows match/.test(stat.textContent)]);

clr.fire("click");
checks.push(["clear restores the full index", stat.textContent.includes(String(total))]);

// The committed index must describe the committed pages: a stale index silently serves a search
// result whose label does not match the row it links to (this happened: the index still read
// "assets/site2026.css" after the page text became "2026/assets/site2026.css").
const page = fs.readFileSync(path.join(ROOT, "2026/repo-review.html"), "utf8");
const idxRow = global.window.SEARCH_INDEX.find((r) => r.p === "repo-review.html" && /site2026\.css/.test(r.h));
checks.push(["index labels match the rendered page", !!idxRow && page.includes(idxRow.h.split(" | ")[0])]);

let bad = 0;
for (const [name, ok] of checks) {
  console.log((ok ? "ok   " : "FAIL ") + name);
  if (!ok) bad++;
}
process.exit(bad ? 1 : 0);
