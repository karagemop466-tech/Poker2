import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const nodes = Object.fromEntries(['pick','cart','add','entry-count','research-entries','t-hotel','t-book',
  't-checkout','t-nights','t-rate','t-fee','t-tax','t-park','tot-buyin','tot-night','tot-hotel','tot-all'].map(id => [id, {
  value: '', valueAsNumber: NaN, validity: {valid: true}, addEventListener(type, fn) { this[type] = fn; },
}]));
nodes.pick.options = [];
nodes.cart.tBodies = [{}];
const rows = [{dataset: {subtotal: '300'}}];
runInNewContext(readFileSync('2026/assets/site2026.js', 'utf8'), {document: {
  querySelector: key => nodes[key.slice(1)],
  querySelectorAll: key => key === '#cart tbody tr' ? rows : [],
}});
const total = () => nodes['tot-all'].textContent;
function set(id, value) {
  const input = nodes[id];
  input.value = String(value);
  input.valueAsNumber = value === '' ? NaN : value;
  input.validity.valid = value === '' || (value >= 0 && (!id.endsWith('nights') || Number.isInteger(value)));
  input.input();
}
assert.equal(total(), 'Not available');
assert.equal(nodes['tot-buyin'].textContent, '$300.00');
set('t-nights', 3);
assert.equal(total(), 'Not available');
set('t-checkout', 500.51);
assert.equal(total(), '$800.51');
assert.equal(nodes['tot-night'].textContent, '$166.84');
set('t-nights', 1.5);
assert.equal(total(), 'Not available');
set('t-nights', 0);
assert.equal(total(), '$300.00');
set('t-nights', 3);
set('t-rate', 100);
set('t-fee', 55);
set('t-tax', 13.38);
set('t-park', 10);
assert.equal(total(), '$800.51', 'do not double-count fees in checkout mode');
set('t-checkout', '');
assert.equal(nodes['tot-night'].textContent, '$185.74');
assert.equal(total(), '$857.22');
set('t-fee', '');
assert.equal(total(), 'Not available', 'missing resort fee is not a zero fee');
console.log('Checkout-first, scenario arithmetic, missing inputs and entries-only pass.');
