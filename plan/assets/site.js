/* Client-side behaviour for the poker planner. No dependencies and no network calls:
   every number comes from the generated dataset (assets/data.js), itself built from
   site-data/*.json by scripts/build-site.py. Values never change in the browser. */
(function () {
  var D = window.POKER || {};
  var q = function (sel, root) { return (root || document).querySelector(sel); };
  var qa = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ---------------------------------------------------------------- table filtering */
  function initTable(wrap) {
    var section = wrap.closest('section') || document;
    var controls = qa('[data-f]', section);
    var rows = qa('tbody tr[data-key]', wrap);
    var count = q('.count', section);
    if (!rows.length) return;

    function apply() {
      var s = {};
      controls.forEach(function (c) {
        s[c.dataset.f] = (c.type === 'checkbox') ? c.checked : String(c.value || '').trim().toLowerCase();
      });
      var shown = 0;
      rows.forEach(function (r) {
        var d = r.dataset, ok = true;
        if (s.q) ok = (d.search || '').indexOf(s.q) !== -1;
        if (ok && s.datefrom) ok = (d.date || '9999') >= s.datefrom;
        if (ok && s.dateto) ok = (d.date || '0000') <= s.dateto;
        if (ok && s.venue && s.venue !== 'all') ok = (d.venue || '') === s.venue;
        if (ok && s.cat && s.cat !== 'all') ok = (d.cat || '').split(' ').indexOf(s.cat) !== -1;
        if (ok && s.single) ok = d.single === 'candidate';
        if (ok && s.walk) { var m = parseFloat(d.walk); ok = !isNaN(m) && m <= 30; }
        if (ok && s.flagged) ok = d.flag === 'yes';
        r.hidden = !ok;
        if (ok) shown++;
      });
      if (count) {
        count.textContent = shown + ' of ' + rows.length + ' rows shown';
        if (shown === 0) count.textContent += ' — nothing in the verified data matches; blanks are unverified, not zero';
      }
    }
    controls.forEach(function (c) { c.addEventListener('input', apply); c.addEventListener('change', apply); });

    var params = new URLSearchParams(location.search);
    controls.forEach(function (c) {
      var v = params.get(c.dataset.f);
      if (v !== null) { if (c.type === 'checkbox') c.checked = (v === '1' || v === 'true'); else c.value = v; }
    });
    apply();
  }
  qa('.tablewrap[data-filterable]').forEach(initTable);

  /* ---------------------------------------------------------------- global search */
  var box = q('#global-search'), sug = q('#search-suggest');
  if (box && sug && D.search) {
    var strip = function (s) { var t = document.createElement('textarea'); t.innerHTML = s; return t.value; };
    var render = function () {
      var needle = strip(box.value).trim().toLowerCase();
      if (needle.length < 2) { sug.style.display = 'none'; sug.innerHTML = ''; return; }
      var hits = [];
      for (var i = 0; i < D.search.length && hits.length < 14; i++) {
        var it = D.search[i];
        if (strip(it.label + ' ' + it.group + ' ' + it.page).toLowerCase().indexOf(needle) !== -1) hits.push(it);
      }
      if (!hits.length) {
        sug.innerHTML = '<button disabled type="button">No verified row matches that.</button>';
        sug.style.display = 'block';
        return;
      }
      sug.innerHTML = hits.map(function (h) {
        return '<button type="button" data-href="' + h.page + (h.anchor ? '#' + h.anchor : '') + '">'
          + h.label + ' <span class="tag">· ' + h.group + ' → ' + h.page + '</span></button>';
      }).join('');
      sug.style.display = 'block';
      qa('button[data-href]', sug).forEach(function (b) {
        b.addEventListener('click', function () { location.href = b.dataset.href; });
      });
    };
    box.addEventListener('input', render);
    box.addEventListener('focus', render);
    document.addEventListener('click', function (e) { if (!sug.contains(e.target) && e.target !== box) sug.style.display = 'none'; });
  }

  /* ---------------------------------------------------------------- trip calculator */
  var calc = q('#trip-calc') || (q('#c-out') && q('#c-out').closest('section'));
  if (calc && D.hotels && D.rates && D.events && D.schedule) {
    var TAX = (D.tax && D.tax.rate_pct ? D.tax.rate_pct : 13.38) / 100;
    var money = function (n) { return '$' + Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };
    var byId = {};
    D.events.forEach(function (e) { byId[e.id] = e; });

    var hotelSel = q('#c-hotel'), rateSel = q('#c-rate'), nightsIn = q('#c-nights'),
      occIn = q('#c-occ'), parkIn = q('#c-parking'), addBtn = q('#c-add'),
      pick = q('#c-pick'), out = q('#c-out');

    function hotel(id) {
      var list = D.hotels.hotels;
      for (var i = 0; i < list.length; i++) if (list[i].id === id) return list[i];
      return null;
    }
    function ratesFor(hid) {
      return (D.rates.entries || []).filter(function (r) { return r.hotel_id === hid && r.rate_usd; });
    }
    // A dated quote (it carries a per-night breakdown from the booking engine) is the strongest
    // evidence there is, so it is listed first and labelled as a quote. A "from" rate is a
    // published floor and is labelled as one - see flag FG-05.
    function isQuote(r) { return !!(r && r.nightly && r.nightly.length); }
    function rateLabel(r) {
      var kind = r.rate_kind || 'rate';
      var when = r.applies_to_dates ? (' · ' + r.applies_to_dates) : '';
      return '<option value="' + r.id + '">$' + r.rate_usd + ' · '
        + (isQuote(r) ? 'DATED QUOTE' : 'published floor') + ' · ' + kind + when
        + ' (captured ' + r.date_captured + ')</option>';
    }
    function fillRates() {
      var list = ratesFor(hotelSel.value).slice().sort(function (a, b) {
        return (isQuote(b) ? 1 : 0) - (isQuote(a) ? 1 : 0);
      });
      rateSel.innerHTML = list.length
        ? list.map(rateLabel).join('')
        : '<option value="">no verified nightly rate for this property</option>';
      rateSel.disabled = !list.length;
    }
    function chosen() {
      return qa('input:checked', pick).map(function (i) { return byId[i.value]; }).filter(Boolean);
    }
    function pickedIds() {
      return qa('input:checked', pick).map(function (i) { return i.value; });
    }

    function build() {
      var h = hotel(hotelSel.value);
      if (!h) return;
      var rl = ratesFor(h.id), r = null;
      for (var i = 0; i < rl.length; i++) if (rl[i].id === rateSel.value) r = rl[i];
      var feeObj = h.resort_fee || {};
      var feeKnown = feeObj.status === 'verified_official' && feeObj.amount != null;
      var fee = feeKnown ? feeObj.amount : 0;
      var occObj = h.occupancy || {};
      var extraPer = occObj.extra_guest_charge || 0;
      var occN = parseInt(occIn.value, 10) || 1;
      var extraGuests = Math.max(0, occN - 2);
      var n = parseInt(nightsIn.value, 10) || 0;
      var perNightBase = (r ? r.rate_usd : 0) + fee + extraPer * extraGuests;
      var taxEach = perNightBase * TAX;
      var parkingOn = parkIn.checked;
      var parkingPer = ((h.parking || {}).guest_self_per_day || 0);
      var parking = parkingOn ? parkingPer * n : 0;

      var ids = pickedIds(), entries = 0, gtd = 0, lines = '';
      ids.forEach(function (id) {
        var e = byId[id];
        if (!e) return;
        entries += e.buy_in; gtd += (e.gtd || 0);
        lines += '<div class="line"><span>Event ' + e.event_no + ' · ' + e.date + ' ' + e.start.slice(0, 5)
          + ' · ' + e.name + '</span><b>' + money(e.buy_in) + '</b></div>';
      });
      var lodging = (r || feeKnown) ? n * (perNightBase + taxEach) : 0;
      var total = entries + lodging + parking;

      var warn = [];
      if (!r) warn.push('No verified nightly rate exists for ' + h.property + ', so lodging contributes only fees and tax here. Capture the itemised checkout total to make this a real trip cost.');
      if (r && !isQuote(r)) warn.push('$' + r.rate_usd + ' is a published floor, not your quote (FG-05). The Venetian dated quotes captured 2026-11-17 came out at $568.54–$761.75 per night before tax for the same property — pick one of the dated-quote rows above to see what a real stay costs.');
      if (r && isQuote(r) && r.tax_pct_implied) warn.push('This quote implies ' + r.tax_pct_implied + '% tax, computed from its own tax line (not from the county notice) — the two agree to four decimal places.');
      if (!feeKnown) warn.push('This property’s resort fee is not read from an official page yet, so it is excluded from the nightly cost rather than guessed.');
      var unread = ids.filter(function (id) { return byId[id] && !byId[id].sheet_read; });
      if (unread.length) warn.push(unread.length + ' chosen event(s) have no read structure sheet: fee treatment, stack, levels and entry limits are unverified.');
      if (parkingOn && h.id === 'H-VEN') warn.push('Venetian parking is disputed: hotel terms charge registered guests $20/day, the poker page advertises free self-parking for players (flag FG-07).');
      if (feeKnown && h.id !== 'H-WYN') warn.push('The fee line is taxed in this model (Park MGM’s terms state lodging tax applies to “any resort fee”; the Venetian states “$55 plus applicable tax”). Where a property does not say, that is an interpretation — flag FG-06.');
      var allQualify = ids.length && ids.every(function (id) { return byId[id] && byId[id].buy_in >= 300; });
      if (r && h.room_rate_log_id && !allQualify) warn.push('The Venetian poker suite rate needs a $300+ tournament buy-in (or six hours of live cash) every night; this selection does not, so the $' + (r.rate_usd) + ' rate would revert to the prevailing rate.');
      if (extraGuests && occObj.extra_guest_rule) warn.push('Occupancy surcharge applied: ' + occObj.extra_guest_rule);

      out.innerHTML =
        '<div class="line"><span>Entries (' + ids.length + ')</span><b>' + money(entries) + '</b></div>' + lines +
        '<div class="line"><span>Room rate per night ' + (r ? (isQuote(r) ? '<span class="badge b-ok">dated official quote</span>' : '<span class="badge b-warn">published floor, not a quote</span>') : '<span class="badge b-bad">not verified</span>') + '</span><b>' + (r ? money(r.rate_usd) : '—') + '</b></div>' +
        (r && isQuote(r) && r.checkout_total_usd ? '<div class="line"><span>Cross-check — what the engine actually charged</span><b>' + money(r.checkout_total_usd) + ' over ' + r.nights + ' night(s)</b></div>' : '') +
        '<div class="line"><span>Resort fee per night ' + (feeKnown ? '<span class="badge b-ok">official</span>' : '<span class="badge b-warn">not read</span>') + '</span><b>' + (feeKnown ? money(fee) : '—') + '</b></div>' +
        (extraGuests ? '<div class="line"><span>Extra occupants (' + extraGuests + ' × ' + money(extraPer) + ')</span><b>' + money(extraPer * extraGuests) + '</b></div>' : '') +
        '<div class="line"><span>Room tax at ' + (TAX * 100).toFixed(2) + '%</span><b>' + ((r || feeKnown) ? money(taxEach) : '—') + '</b></div>' +
        '<div class="line"><span>True cost per night</span><b>' + ((r || feeKnown) ? money(perNightBase + taxEach) : '—') + '</b></div>' +
        '<div class="line"><span>Lodging × ' + n + ' night' + (n === 1 ? '' : 's') + '</span><b>' + money(lodging) + '</b></div>' +
        (parking ? '<div class="line"><span>Hotel parking (' + n + ' days)</span><b>' + money(parking) + '</b></div>' : '') +
        '<div class="line total"><span>Estimated trip cost</span><b>' + money(total) + '</b></div>' +
        '<div class="line"><span>Published guarantee in play</span><b>' + money(gtd) + '</b></div>' +
        (gtd && entries ? '<div class="line"><span>Descriptive ratio: guarantee ÷ entry cost</span><b>' + (gtd / entries).toFixed(1) + '×</b></div>' : '') +
        (warn.length ? '<div class="note" style="margin-top:10px"><b>Open items in this estimate</b><ul class="tight">'
          + warn.map(function (w) { return '<li>' + w + '</li>'; }).join('') + '</ul></div>'
          : '<div class="note ok" style="margin-top:10px">Every input in this scenario is backed by a quoted official page; the room rate is a dated “from” capture, so the lodging line is still a floor.</div>');

      q('#c-pernight').textContent = (r || feeKnown) ? money(perNightBase + taxEach) : 'not calculable';
      q('#c-entries').textContent = money(entries);
      q('#c-total').textContent = money(total);
    }

    if (addBtn) addBtn.addEventListener('click', function () {
      var w = (D.schedule.windows.best_poker_rate_compatible || [])[0]
        || (D.schedule.windows.best_size_ratio || [])[0];
      if (!w) return;
      hotelSel.value = 'H-VEN'; fillRates();
      nightsIn.value = w.nights;
      var want = w.days;
      qa('input', pick).forEach(function (i) {
        var d = (byId[i.value] || {}).date;
        i.checked = want.indexOf(d) !== -1;
      });
      build();
    });
    qa('select, input', calc).forEach(function (c) {
      c.addEventListener('change', function () { if (c === hotelSel) fillRates(); build(); });
      c.addEventListener('input', build);
    });
    fillRates();
    build();
  }

  /* ---------------------------------------------------------------- change badges */
  if (D.changes && D.changes.length) {
    var changed = {};
    D.changes.forEach(function (c) { changed[c.url] = true; });
    qa('tr[data-key]').forEach(function (r) {
      var list = (r.dataset.sources || '').split(' ');
      var hit = list.some(function (u) { return changed[u]; });
      if (hit) {
        var cell = q('.change-cell', r);
        if (cell) cell.innerHTML = '<span class="badge b-bad">source changed</span>';
      }
    });
  }
})();
