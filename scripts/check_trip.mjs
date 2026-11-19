import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const nodes = Object.fromEntries(['pick','cart','add','t-checkout','t-nights','sum-buyin',
  'sum-pool','tot-buyin','tot-night','tot-hotel','tot-all'].map(id => [id, {
  valueAsNumber: NaN, validity: {valid: true}, addEventListener(type, fn) { this[type] = fn; },
}]));
nodes.cart.tBodies = [{}];
const rows = [{getAttribute: key => key === 'data-buyin' ? '300' : '242'}];
runInNewContext(readFileSync('2026/assets/site2026.js', 'utf8'), {document: {
  querySelector: key => nodes[key.slice(1)],
  querySelectorAll: key => key === '#cart tbody tr' ? rows : [],
}});
const total = () => nodes['tot-all'].textContent;
const nights = nodes['t-nights'], checkout = nodes['t-checkout'];
assert.equal(total(), 'Not available');
assert.equal(nodes['tot-buyin'].textContent, '$300.00');
nights.valueAsNumber = 3;
nights.input();
assert.equal(total(), 'Not available');
checkout.valueAsNumber = 500.51;
checkout.input();
assert.equal(total(), '$800.51');
assert.equal(nodes['tot-night'].textContent, '$166.84');
nights.valueAsNumber = 1.5;
nights.input();
assert.equal(total(), 'Not available');
nights.valueAsNumber = 0;
nights.input();
assert.equal(total(), '$300.00');
