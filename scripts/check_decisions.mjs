import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const js = readFileSync('2026/assets/site2026.js', 'utf8');
function node(value = '') {
  return { value, checked: false, validity: {valid:true}, addEventListener(name, fn) { this[name] = fn; } };
}
function load(els, rows = []) {
  runInNewContext(js, {
    Date: class extends Date { constructor() { super('2026-11-19T03:00:00Z'); } },
    document: {querySelector: key => els[key.slice(1)], querySelectorAll: key => key === '#t tbody tr' ? rows : []},
    location: { hash: '' },
  });
}
function row(dates, confirmed, buyIn) {
  const attrs = {'data-dates': dates.join(' '), 'data-confirmed': confirmed, 'data-buyin': buyIn, 'data-group': 'candidate'};
  const slots = dates.map(date => ({getAttribute: () => date}));
  return {textContent: '', slots, getAttribute: (key) => attrs[key], querySelectorAll: () => slots,
    classList: {toggle: (_, hidden) => {attrs.hidden = hidden;}}, get hidden() {return attrs.hidden;} };
}
const rows = [row(['2026-11-17','2026-11-18'], '0', '1100'), row(['2026-11-20'], '1', '300')];
const filters = Object.fromEntries(['t','q','datef','date-to','include-past','maxbi','sef','nogtd','count','reset'].map(id => [id,node()]));
load(filters, rows);
assert.equal(rows[0].hidden, false, 'Vegas date is still Nov 18');
assert.equal(rows[0].slots[0].hidden, true, 'old flight is hidden while current flight stays');
filters.datef.value = '2026-11-19';
filters['date-to'].value = '2026-11-20';
filters.datef.input();
assert.deepEqual(rows.map(r => r.hidden), [true, false]);
filters.reset.click();
filters.sef.checked = false;
filters.maxbi.value = '1000';
filters.maxbi.input();
assert.deepEqual(rows.map(r => r.hidden), [true, false]);
filters.reset.click();
filters.sef.checked = true;
filters.sef.input();
assert.deepEqual(rows.map(r => r.hidden), [true, false], 'strict filter needs confirmation, not the candidate group');

const hotel = Object.fromEntries(Object.entries({'h-rate':'','h-fee':'55','h-tax':'13.38','h-fee-tax':'13.38','h-park':'20','h-nights':'3',
  'h-hotel':'','h-book':'','h-night':'','h-total':''}).map(([id,value]) => [id,node(value)]));
for (const el of Object.values(hotel)) el.valueAsNumber = el.value === '' ? NaN : Number(el.value);
load(hotel);
assert.equal(hotel['h-total'].textContent, 'Not available', 'missing room price is not zero');
hotel['h-rate'].value = '100';
hotel['h-rate'].valueAsNumber = 100;
hotel['h-rate'].input();
assert.equal(hotel['h-night'].textContent, '$195.74');
assert.equal(hotel['h-total'].textContent, '$587.22');
console.log('Decision checks: Vegas date, flight range, strict freezeout, entry cap and hotel estimates');
