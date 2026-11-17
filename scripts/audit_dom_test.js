#!/usr/bin/env node
/*
 * DOM test for the /audit/ surface.
 *
 * Renders the built pages in a real DOM (jsdom) and exercises the behaviour that a
 * static HTML diff cannot prove:
 *   - the events page filter bars bind to their own table and actually narrow it,
 *   - the row counter reflects the filtered count,
 *   - the trip-cost calculator does the arithmetic it claims, and refuses to print a
 *     total when a required value is missing.
 *
 * It writes nothing. Run it after `python3 scripts/audit_build.py`:
 *
 *     cd scripts && npm install --no-save jsdom && node audit_dom_test.js
 *
 * Exits 1 on any failed assertion so a workflow can gate on it.
 */
const fs = require('fs');
const path = require('path');

let JSDOM;
try {
  ({ JSDOM } = require('jsdom'));
} catch (err) {
  console.error('jsdom is not installed. Run: npm install --no-save jsdom');
  process.exit(2);
}

const ROOT = path.resolve(__dirname, '..');
const OUT = path.join(ROOT, 'audit');
const EVENTS = path.join(ROOT, 'data', 'audit', 'events.json');

let fails = 0;
let checks = 0;
const ok = (cond, msg) => {
  checks++;
  if (!cond) fails++;
  console.log((cond ? '  ok   ' : '  FAIL ') + msg);
};

// ---------------------------------------------------------------- fixtures
// Expected counts come from the data, not from a number typed into this file, so a
// legitimate data change does not silently turn the test into a no-op.
const events = JSON.parse(fs.readFileSync(EVENTS, 'utf8')).events;
const oneDayRead = events.filter(
  (e) => e.category === 'single' && e.structure_read
);
const wantRows = oneDayRead.length;

const load = (name) =>
  new JSDOM(fs.readFileSync(path.join(OUT, name), 'utf8'), {
    runScripts: 'dangerously',
  });

const visible = (table) =>
  Array.from(table.tBodies[0].rows).filter((r) => r.style.display !== 'none');

// ---------------------------------------------------------------- events page
console.log('\nevents page — search and date filter');
{
  const dom = load('events.html');
  const d = dom.window.document;
  const bars = d.querySelectorAll('.bar');
  ok(bars.length === 3, `events page has 3 filter bars, got ${bars.length}`);

  const tbl = d.getElementById('s-read');
  ok(!!tbl, 'the single-entry sheet-read table is present');
  if (tbl) {
    const total = tbl.tBodies[0].rows.length;
    ok(
      total === wantRows,
      `first table has ${wantRows} rows (one-day, sheet read), got ${total}`
    );

    // a bar must only ever drive the table in its own section
    const bar = bars[0];
    ok(
      bar.parentElement.querySelector('table.data') === tbl,
      'the first filter bar is bound to the first section table'
    );

    const q = bar.querySelector('[data-q]');
    const count = bar.querySelector('[data-count]');

    q.value = 'bounty';
    q.dispatchEvent(new dom.window.Event('input'));
    const hit = visible(tbl).length;
    ok(hit > 0 && hit < total, `search "bounty" narrows ${total} -> ${hit}`);

    q.value = 'zzzznomatch';
    q.dispatchEvent(new dom.window.Event('input'));
    ok(visible(tbl).length === 0, 'nonsense search shows 0 rows');

    q.value = '';
    q.dispatchEvent(new dom.window.Event('input'));
    ok(
      visible(tbl).length === total,
      'clearing the search restores every row'
    );

    const dateSel = bar.querySelector('[data-date]');
    const dates = new Set(events.map((e) => e.date));
    ok(
      dateSel.options.length - 1 === dates.size,
      `date filter offers ${dates.size} distinct dates, got ${dateSel.options.length - 1}`
    );

    // pick the date with the most one-day sheet-read rows, so the assertion is
    // about filtering rather than about a single hard-coded day
    const byDate = {};
    oneDayRead.forEach((e) => {
      byDate[e.date] = (byDate[e.date] || 0) + 1;
    });
    const busiest = Object.keys(byDate).sort((a, b) => byDate[b] - byDate[a])[0];
    dateSel.value = busiest;
    dateSel.dispatchEvent(new dom.window.Event('change'));
    const shown = visible(tbl).length;
    ok(
      shown === byDate[busiest],
      `date filter on ${busiest} shows ${byDate[busiest]} rows, got ${shown}`
    );
    ok(
      count.textContent.indexOf(`${byDate[busiest]} of ${total}`) === 0,
      `row counter updates: "${count.textContent}"`
    );
  }
  dom.window.close();
}

// ---------------------------------------------------------------- cost page
console.log('\ntrip cost calculator');
{
  const dom = load('cost.html');
  const d = dom.window.document;
  const text = () => d.body.textContent.replace(/\s+/g, ' ');

  const entries = d.querySelectorAll('#c-ev option');
  const hotels = d.querySelectorAll('#c-hotel option');
  ok(entries.length > 50, `calculator lists ${entries.length} single entries`);
  ok(
    hotels.length === 11,
    `calculator lists ${hotels.length} hotels (11 priced properties)`
  );

  // with no room rate there is no true cost per night, so it must refuse to total
  ok(/INCOMPLETE/.test(text()), 'with no room rate the total says INCOMPLETE');
  ok(
    /not a verified rate/.test(text()),
    'the calculator states that a typed rate is not a verified rate'
  );

  // arithmetic: one entry + 4 nights at (typed rate + that hotel's published fee) x 1.1338.
  // The page builds its option lists at runtime and stores array indices as values, so
  // select through the rendered text rather than assuming an index or a default.
  const evSel = d.getElementById('c-ev');
  const hotelSel = d.getElementById('c-hotel');
  const hot = JSON.parse(
    fs.readFileSync(path.join(ROOT, 'data', 'audit', 'hotels.json'), 'utf8')
  ).hotels;
  // pick a hotel whose resort fee is published, so the hotel side can total
  const priced = hot.find((h) => h.resort_fee !== null && h.resort_fee !== undefined);

  const pick = (sel, needle) => {
    const opt = Array.from(sel.options).find((o) => o.textContent.includes(needle));
    if (!opt) return null;
    opt.selected = true;
    sel.dispatchEvent(new dom.window.Event('change'));
    return opt;
  };

  if (evSel) {
    const opt = Array.from(evSel.options)[0];
    if (opt) {
      opt.selected = true;
      evSel.dispatchEvent(new dom.window.Event('change'));
      ok(evSel.selectedOptions.length === 1, `one entry selected: ${opt.textContent.trim()}`);
    }
  }
  if (hotelSel && priced) {
    const opt = pick(hotelSel, `fee $${priced.resort_fee}`);
    ok(!!opt, `hotel selected with a published fee: ${priced.name}`);
  }

  const rate = d.querySelector('#c-rate');
  const nights = d.querySelector('#c-nights');
  if (nights) {
    nights.value = '4';
    nights.dispatchEvent(new dom.window.Event('input'));
  }
  rate.value = '200';
  rate.dispatchEvent(new dom.window.Event('input'));

  // the buy-in is whatever the selected option's event publishes; read it off the page
  const m = text().match(/Entries × buy-in \(1\)\s*\$([\d,]+(?:\.\d+)?)/);
  const buyin = m ? parseFloat(m[1].replace(/,/g, '')) : null;
  ok(buyin !== null, `entries line reports a buy-in: ${m ? m[1] : 'not found'}`);

  if (buyin !== null && priced) {
    const want = buyin + (200 + priced.resort_fee) * 4 * 1.1338;
    const shown = text().match(/\$([\d,]+\.\d{2})/g) || [];
    const totals = shown.map((v) => parseFloat(v.replace(/[$,]/g, '')));
    ok(
      totals.some((v) => Math.abs(v - want) < 0.01),
      `trip total is ${want.toFixed(2)} = ${buyin} + (200 + ${priced.resort_fee}) x 4 x 1.1338; ` +
        `page shows ${shown.join(' ')}`
    );
  }

  dom.window.close();
}

// ---------------------------------------------------------------- every page
console.log('\nevery page parses and has a title');
{
  const pages = fs
    .readdirSync(OUT)
    .filter((f) => f.endsWith('.html'))
    .sort();
  ok(pages.length === 15, `15 pages built, found ${pages.length}`);
  for (const f of pages) {
    const dom = new JSDOM(fs.readFileSync(path.join(OUT, f), 'utf8'));
    const t = dom.window.document.title;
    ok(!!t && t.length > 3, `${f} has a title: "${t}"`);
    dom.window.close();
  }
}

console.log(
  fails === 0
    ? `\nALL PASS (${checks} checks)`
    : `\nFAILURES: ${fails} of ${checks} checks`
);
process.exit(fails === 0 ? 0 : 1);
