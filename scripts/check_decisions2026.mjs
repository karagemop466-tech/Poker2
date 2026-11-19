import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {JSDOM} from 'jsdom';
const js = readFileSync('2026/assets/site2026.js','utf8');
function open(page) {
  const dom = new JSDOM(readFileSync(`2026/${page}.html`,'utf8'), {
    runScripts:'outside-only', url:`https://example.test/Poker2/2026/${page}.html`
  });
  const NativeDate = dom.window.Date;
  dom.window.Date = class extends NativeDate {
    constructor(...args) { super(...(args.length ? args : ['2026-11-19T20:00:00Z'])); }
  };
  dom.window.eval(js);
  const $ = id => dom.window.document.getElementById(id);
  function set(id, value) {
    const el=$(id); if(el.type==='checkbox') el.checked=value; else el.value=value;
    el.dispatchEvent(new dom.window.Event('input'));
    el.dispatchEvent(new dom.window.Event('change'));
  }
  return {dom,$,set};
}
{
  const {dom,$,set}=open('tournaments');
  const shown=()=>[...dom.window.document.querySelectorAll('#t tbody tr:not(.hidden)')];
  assert.equal(shown().length,0,'the initial page shows confirmed freezeouts only');
  set('sef',false);
  assert.equal(shown().length,62,'past entry dates hidden, including ended multi-flight event');
  set('sef',true); assert.equal(shown().length,0,'rules silent is not confirmed');
  assert.match($('count').textContent,/No confirmed freezeout matches/);
  set('sef',false); set('datef','2026-11-19'); set('date-to','2026-11-21');
  assert.deepEqual(shown().map(r=>r.id),['ev3','ev4','ev5']);
  set('datef','2026-11-22'); assert.equal(shown().length,0,'reversed range returns no matches');
  $('reset').click(); set('sef',false); set('include-past',true); set('datef','2026-11-18'); set('date-to','2026-11-18');
  assert.deepEqual(shown().map(r=>r.id),['ev2'],'restart is not a new entry');
  $('reset').click(); set('sef',false); dom.window.document.querySelector('.pill[data-g="candidate"]').click();
  assert(shown().every(r=>r.dataset.group==='candidate'));
  dom.window.close();
}
{
  const {dom,$,set}=open('hotels');
  assert.equal($('h-total').textContent,'Not available');
  set('h-hotel','venetian');
  set('h-rate','100'); set('h-nights','2');
  assert.equal($('h-total').textContent,'Not available','unknown parking is not free');
  set('h-park','0');
  assert.equal($('h-night').textContent,'$175.74');
  assert.equal($('h-total').textContent,'$351.48');
  set('h-nights','1.5'); assert.equal($('h-total').textContent,'Not available');
  set('h-nights','2'); set('h-hotel','caesars-palace');
  assert.equal($('h-fee').value,''); assert.equal($('h-tax').value,'');
  assert.equal($('h-total').textContent,'Not available','switch must clear unverified rates');
  set('h-hotel','venetian'); assert.equal($('h-fee').value,'55');
  set('h-rate','-1'); assert.equal($('h-total').textContent,'Not available');
  dom.window.close();
}
{
  const d=JSON.parse(readFileSync('data/verified2026/dataset.json'));
  assert.equal(d.wynn_daily.length,4);
  assert(d.wynn_daily.every(r=>r.single_entry.value===false && r.source && r.last_checked));
  const friday=d.wynn_daily.find(r=>r.days==='Friday');
  assert.equal(friday.reentry.value,false); assert.equal(friday.rebuy.value,200);
  assert.equal(friday.addon.value,100);
  assert(d.events.every(r=>r.last_checked && r.sheet_url && r.single_entry_confirmed===false));
}
console.log('Decision gates pass: strict eligibility, upcoming dates, range/reset, restarts, blank quotes, cents, hotel changes and Wynn rule provenance.');
