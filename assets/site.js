/* SUPERSEDED - kept for the record, loads on four legacy pages, does nothing there.
 *
 * This file was written for the 2026-11 generation of the root dashboard, which is no longer the
 * one published. It binds #evtable (tournaments), #q / #f-date / #f-class / #f-max / #f-single
 * (filters) and the #c-* trip-calculator inputs. None of those element ids exists on any page the
 * generators now produce, so every feature here is inert: the page loads, no handler attaches, and
 * nothing errors. Verified 2026-11-17 across all 30 root pages.
 *
 * The live root features are in assets/dashboard.js, which the current generators reference:
 * data-search / data-date / data-cat table filters, the #site-search box, and the
 * #trip-calc calculator (true cost/night = (room rate + resort fee) x (1 + tax) + parking).
 *
 * It is left in place rather than deleted because four legacy pages still <script> it, and the
 * pages still render without it. Deleting it is recorded as a suggestion, not done unilaterally.
 *
 * Search, filters and the trip-cost calculator. No dependencies, no network calls. */
(function () {
  "use strict";

  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------------------------------------------------------- filtering --- */
  function initFilters() {
    var table = $("#evtable");
    if (!table) return;
    var q = $("#q"), fd = $("#f-date"), fc = $("#f-class"), fm = $("#f-max"), fs = $("#f-single");
    var count = $("#tcount");
    var rows = $$("#evtable tbody tr");

    function apply() {
      var term = (q && q.value || "").trim().toLowerCase();
      var date = fd && fd.value;
      var cls = fc && fc.value;
      var max = fm && fm.value ? parseFloat(fm.value) : null;
      var singleOnly = fs && fs.checked;
      var shown = 0;

      rows.forEach(function (tr) {
        var ok = true;
        if (term && tr.textContent.toLowerCase().indexOf(term) === -1) ok = false;
        if (ok && date && tr.getAttribute("data-date") !== date) ok = false;
        if (ok && cls && tr.getAttribute("data-class") !== cls) ok = false;
        if (ok && max !== null) {
          var b = parseFloat(tr.getAttribute("data-buyin"));
          if (isNaN(b) || b > max) ok = false;
        }
        if (ok && singleOnly && tr.getAttribute("data-single") !== "yes") ok = false;
        tr.style.display = ok ? "" : "none";
        if (ok) shown++;
      });

      if (count) {
        var msg = shown + " of " + rows.length + " rows";
        if (singleOnly) {
          msg += shown === 0
            ? " — no event has a confirmed one-entry, no-rebuy, no-add-on rule from an official source. See Entry rules."
            : "";
        }
        count.textContent = msg;
      }
    }

    [q, fd, fc, fm, fs].forEach(function (el) {
      if (!el) return;
      el.addEventListener(el.type === "checkbox" ? "change" : "input", apply);
      el.addEventListener("change", apply);
    });
    apply();
  }

  /* --------------------------------------------------------- calculator --- */
  function num(id, fallback) {
    var el = document.getElementById(id);
    if (!el) return fallback;
    var v = parseFloat(el.value);
    return isNaN(v) || v < 0 ? fallback : v;
  }

  function money(n) {
    return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 0 });
  }

  function initCalc() {
    var out = document.getElementById("c-out");
    if (!out) return;

    var inputs = ["c-entries", "c-buyin", "c-nights", "c-rate", "c-fee", "c-tax", "c-park", "c-other"]
      .map(function (id) { return document.getElementById(id); })
      .filter(Boolean);

    function render() {
      var entries = num("c-entries", 0);
      var buyin = num("c-buyin", 0);
      var nights = num("c-nights", 0);
      var rateEl = document.getElementById("c-rate");
      var hasRate = rateEl && rateEl.value.trim() !== "";
      var rate = num("c-rate", 0);
      var fee = num("c-fee", 0);
      var taxPct = num("c-tax", 0);
      var park = num("c-park", 0);
      var other = num("c-other", 0);

      var entryCost = entries * buyin;
      // Published rule: the tax applies to the room rate, the resort fee and other
      // per-night charges. Parking is a per-day fee and is added after tax.
      var nightlyTaxable = rate + fee + other;
      var taxPerNight = nightlyTaxable * (taxPct / 100);
      var trueNightly = nightlyTaxable + taxPerNight;
      var hotelTotal = nights * trueNightly + nights * park;
      var total = entryCost + hotelTotal;

      var html = "";
      html += '<div class="row"><span>Tournament entries (' + entries + " × " + money(buyin) + ")</span><span>" + money(entryCost) + "</span></div>";
      if (hasRate) {
        html += '<div class="row"><span>Room rate, ' + nights + " night(s) × " + money(rate) + "</span><span>" + money(nights * rate) + "</span></div>";
        html += '<div class="row"><span>Resort fee, ' + nights + " night(s) × " + money(fee) + "</span><span>" + money(nights * fee) + "</span></div>";
        if (other > 0) html += '<div class="row"><span>Other per-night fees</span><span>' + money(nights * other) + "</span></div>";
        html += '<div class="row"><span>Room tax at ' + taxPct + "% (on rate + fees)</span><span>" + money(nights * taxPerNight) + "</span></div>";
        if (park > 0) html += '<div class="row"><span>Parking, ' + nights + " day(s) × " + money(park) + "</span><span>" + money(nights * park) + "</span></div>";
        html += '<div class="row"><span><b>True cost per night</b> (rate + fee + tax)</span><span><b>' + money(trueNightly + park) + "</b></span></div>";
      } else {
        html += '<div class="row"><span>Hotel</span><span class="blank">enter a dated rate to calculate</span></div>';
      }
      html += '<div class="row total"><span>Total trip cost</span><span>' + money(total) + "</span></div>";

      if (!hasRate) {
        html += '<p class="warnline">The hotel half is undefined until you enter a nightly rate copied from the ' +
          "property's own booking page for your exact dates. The site will not fill it in for you.</p>";
      } else {
        html += '<p class="warnline">Rate source is whatever you entered. Nothing here is a quote, ' +
          "and the room tax percentage is only published by The Venetian (13.38%).</p>";
      }
      out.innerHTML = html;
    }

    inputs.forEach(function (el) {
      el.addEventListener("input", render);
      el.addEventListener("change", render);
    });
    render();
  }

  /* ------------------------------------------------------------- prices --- */
  document.addEventListener("DOMContentLoaded", function () {
    initFilters();
    initCalc();
  });
})();
