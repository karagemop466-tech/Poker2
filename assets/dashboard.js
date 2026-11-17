/* Poker2 — dashboard interactivity: search, date filter, entry-rule toggle,
   walk filter, trip-cost calculator, hotel true-cost calculator. */
(function () {
  "use strict";

  function norm(s) { return (s || "").toLowerCase(); }

  /* ---------- generic table filters (search / date / category / walk) ---------- */
  function applyFilters(table) {
    var q = norm(table.getAttribute("data-search") || "");
    var date = table.getAttribute("data-date") || "";
    var cat = table.getAttribute("data-cat") || "";
    var walkOnly = table.getAttribute("data-walkonly") === "1";
    var rows = table.querySelectorAll("tbody tr");
    var shown = 0;
    rows.forEach(function (row) {
      var ok = true;
      if (q && norm(row.textContent).indexOf(q) === -1) ok = false;
      if (date && (row.getAttribute("data-date") || "") !== date) ok = false;
      if (cat && (row.getAttribute("data-cat") || "") !== cat) ok = false;
      if (walkOnly) {
        var w = row.getAttribute("data-walk-ok");
        if (w !== "1") ok = false;
      }
      row.classList.toggle("hidden", !ok);
      if (ok) shown++;
    });
    var countEl = document.querySelector('[data-count-for="' + table.id + '"]');
    if (countEl) countEl.textContent = shown + " of " + rows.length + " rows shown";
  }

  function bindTable(id) {
    var table = document.getElementById(id);
    if (!table) return;
    var search = document.querySelector('[data-bind-search="' + id + '"]');
    var dateSel = document.querySelector('[data-bind-date="' + id + '"]');
    var catSel = document.querySelector('[data-bind-cat="' + id + '"]');
    var walkChk = document.querySelector('[data-bind-walk="' + id + '"]');
    if (search) search.addEventListener("input", function () {
      table.setAttribute("data-search", search.value); applyFilters(table);
    });
    if (dateSel) dateSel.addEventListener("change", function () {
      table.setAttribute("data-date", dateSel.value); applyFilters(table);
    });
    if (catSel) catSel.addEventListener("change", function () {
      table.setAttribute("data-cat", catSel.value); applyFilters(table);
    });
    if (walkChk) walkChk.addEventListener("change", function () {
      table.setAttribute("data-walkonly", walkChk.checked ? "1" : ""); applyFilters(table);
    });
    applyFilters(table);
  }

  Array.prototype.forEach.call(document.querySelectorAll("table.data[id]"), function (t) {
    bindTable(t.id);
  });

  /* ---------- site-wide search across every table on the page ---------- */
  var globalBox = document.getElementById("site-search");
  if (globalBox) {
    var allTables = document.querySelectorAll("table.data");
    var statusEl = document.getElementById("site-search-status");
    function runGlobalSearch() {
      var q = norm(globalBox.value).trim();
      var shown = 0, total = 0;
      allTables.forEach(function (table) {
        table.setAttribute("data-search", q);
        applyFilters(table);
        table.querySelectorAll("tbody tr").forEach(function (row) {
          total++;
          if (!row.classList.contains("hidden")) shown++;
        });
      });
      if (statusEl) {
        if (total === 0) {
          // pages without tables (dashboard, summary) should not claim "0 rows"
          statusEl.textContent = "Use the boxes on the tournament, hotel, venue or walking pages to filter.";
        } else if (q === "") {
          statusEl.textContent = total + " rows on this page";
        } else {
          statusEl.textContent = shown + " of " + total + " rows on this page match \u201c" + globalBox.value + "\u201d";
        }
      }
    }
    globalBox.addEventListener("input", runGlobalSearch);
    runGlobalSearch();
  }

  /* ---------- trip cost calculator ---------- */
  var tripForm = document.getElementById("trip-calc");
  if (tripForm) {
    var entrySumEl = document.getElementById("trip-entry-sum");
    var entriesList = tripForm.querySelectorAll("input[data-buyin]");

    function recalcTrip() {
      var entryTotal = 0, picked = 0;
      entriesList.forEach(function (cb) {
        if (cb.checked) { entryTotal += parseFloat(cb.getAttribute("data-buyin")) || 0; picked++; }
      });
      if (entrySumEl) entrySumEl.textContent = picked + " entries, buy-ins total $" + entryTotal.toFixed(2);

      var nights = parseFloat(document.getElementById("trip-nights").value) || 0;
      var nightly = parseFloat(document.getElementById("trip-nightly").value) || 0;
      var fee = parseFloat(document.getElementById("trip-resort-fee").value) || 0;
      var taxPct = parseFloat(document.getElementById("trip-tax").value) || 0;
      var parkingPerNight = parseFloat(document.getElementById("trip-parking").value) || 0;

      // true hotel cost/night = (room rate + resort fee) * (1 + tax) + parking
      var trueNightly = (nightly + fee) * (1 + taxPct / 100) + parkingPerNight;
      var hotelTotal = trueNightly * nights;
      var grand = entryTotal + hotelTotal;

      var t1 = document.getElementById("trip-true-nightly");
      var t2 = document.getElementById("trip-hotel-total");
      var t3 = document.getElementById("trip-grand");
      if (t1) t1.textContent = "$" + trueNightly.toFixed(2);
      if (t2) t2.textContent = "$" + hotelTotal.toFixed(2);
      if (t3) t3.textContent = "$" + grand.toFixed(2);
    }

    tripForm.addEventListener("input", recalcTrip);
    tripForm.addEventListener("change", recalcTrip);
    var presetBtn = document.getElementById("trip-preset-hotel");
    if (presetBtn) presetBtn.addEventListener("change", function () {
      var opt = presetBtn.selectedOptions[0];
      if (opt && opt.dataset.rate !== undefined) {
        document.getElementById("trip-nightly").value = opt.dataset.rate || "";
        document.getElementById("trip-resort-fee").value = opt.dataset.fee || "";
        document.getElementById("trip-tax").value = opt.dataset.tax || "";
        document.getElementById("trip-parking").value = opt.dataset.parking || "";
      }
      recalcTrip();
    });
    recalcTrip();
  }

  /* ---------- per-hotel true cost calculator (hotels page) ---------- */
  document.querySelectorAll("[data-hotel-calc]").forEach(function (wrap) {
    function recalc() {
      var rate = parseFloat(wrap.querySelector(".hc-rate").value) || 0;
      var fee = parseFloat(wrap.getAttribute("data-fee")) || 0;
      var tax = parseFloat(wrap.getAttribute("data-tax")) || 0;
      var parking = parseFloat(wrap.getAttribute("data-parking")) || 0;
      var out = wrap.querySelector(".hc-out");
      if (!out) return;
      var nightly = (rate + fee) * (1 + tax) + parking;
      out.textContent = rate > 0
        ? "True cost per night: $" + nightly.toFixed(2) + "  (room $" + rate.toFixed(2) + " + resort fee $" + fee.toFixed(2) + ", tax " + (tax * 100).toFixed(2) + "%, parking $" + parking.toFixed(2) + ")"
        : "Enter a dated room rate to compute true cost per night.";
    }
    wrap.addEventListener("input", recalc);
    recalc();
  });
})();
