/* Vegas Poker Trip Planner — client-side filters, tables, calculator */
(function () {
  "use strict";
  var S = window.SITE || {};
  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  };
  var srcLinks = function (ids) {
    return (ids || []).map(function (sid) {
      var s = (S.sources || {})[sid];
      return s ? '<a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(sid) + "</a>" : esc(sid);
    }).join(" ");
  };
  var badge = function (c) {
    var m = { single_entry_confirmed: ["b-se", "single-entry"], flagged_ambiguous: ["b-flag", "flagged"],
              excluded: ["b-excl", "excluded"], unverified: ["b-unv", "unverified"] }[c] || ["b-unv", c];
    return '<span class="badge ' + m[0] + '">' + esc(m[1]) + "</span>";
  };
  var ratio = function (e) {
    return (e.gtd && e.buy_in) ? (e.gtd / e.buy_in) : null;
  };
  var fmtRatio = function (e) {
    var r = ratio(e);
    return r == null ? "" : r.toFixed(1) + "×";
  };

  function eventTable(list) {
    if (!list.length) return '<p class="muted">No rows match the current filters.</p>';
    var h = '<table class="data"><thead><tr><th>Date</th><th>Start</th><th>Event</th><th>Venue</th><th>Buy-in</th>' +
      '<th>House fee</th><th>Guarantee</th><th>Gtd ÷ fee</th><th>Format</th><th>Eligibility</th><th>Class</th>' +
      '<th>Last checked</th><th>Sources</th></tr></thead><tbody>';
    list.forEach(function (e) {
      h += '<tr class="evrow" data-id="' + esc(e.id) + '">' +
        "<td>" + esc(e.date) + "</td><td>" + esc(e.start) + "</td>" +
        '<td><details><summary>' + esc(e.name) + "</summary>" + ruleGrid(e) + "</details></td>" +
        "<td>" + esc(e.venue) + "</td>" +
        "<td>" + (e.buy_in != null ? "$" + e.buy_in : "") + "</td>" +
        "<td>" + (e.house_fee != null ? "$" + e.house_fee : "") + "</td>" +
        "<td>" + (e.gtd != null ? "$" + e.gtd + (e.gtd_includes_bounties ? " (incl. bounties)" : "") : "") + "</td>" +
        "<td>" + fmtRatio(e) + "</td><td>" + esc(e.format) + "</td>" +
        '<td class="tiny">' + esc(e.eligibility) + "</td>" +
        "<td>" + badge(e.classification) + "</td>" +
        "<td>" + esc(e.last_checked) + "</td>" +
        '<td class="tiny">' + srcLinks(e.sources) + "</td></tr>";
    });
    return h + "</tbody></table>";
  }

  function ruleGrid(e) {
    var r = e.rules || {};
    var h = '<div class="rulegrid">';
    ["single_entry", "re_entry", "rebuy", "addon", "house_fee"].forEach(function (k) {
      var v = r[k] || {};
      h += '<div class="k">' + esc(k.replace("_", "-")) + "</div><div>" +
        esc(v.value == null ? "blank — not stated on source (flagged)" : v.value) +
        (v.excerpt ? '<div class="tiny">Excerpt: “' + esc(v.excerpt) + "” [" + srcLinks([v.source]) + " · retrieved " + esc(v.retrieved) + "]</div>" : "") +
        "</div>";
    });
    if (e.exclude_reason) h += '<div class="k">reason</div><div>' + esc(e.exclude_reason) + "</div>";
    return h + "</div>";
  }

  function applyFilters() {
    var q = (($("q") || {}).value || "").toLowerCase();
    var from = ($("dfrom") || {}).value || "";
    var to = ($("dto") || {}).value || "";
    var seOnly = ($("seOnly") || {}).checked;
    var hideGated = ($("hideGated") || {}).checked;
    var sort = (($("sort") || {}).value) || "date";
    var rows = (S.events || []).slice();
    rows = rows.filter(function (e) {
      if (seOnly && e.classification !== "single_entry_confirmed") return false;
      if (hideGated && !(e.eligibility || "").startsWith("21+")) return false;
      if (from && (!e.date || e.date < from)) return false;
      if (to && (!e.date || e.date > to)) return false;
      if (q) {
        var blob = [e.id, e.name, e.venue, e.date, e.format, e.eligibility, e.note].join(" ").toLowerCase();
        if (blob.indexOf(q) === -1) return false;
      }
      return true;
    });
    rows.sort(function (a, b) {
      if (sort === "ratio") return (ratio(b) || -1) - (ratio(a) || -1);
      if (sort === "buyin") return (a.buy_in || 1e9) - (b.buy_in || 1e9);
      return String(a.date).localeCompare(String(b.date)) || String(a.start).localeCompare(String(b.start));
    });
    var groups = { se: [], flag: [], excl: [], unv: [] };
    rows.forEach(function (e) {
      var g = { single_entry_confirmed: "se", flagged_ambiguous: "flag", excluded: "excl", unverified: "unv" }[e.classification] || "unv";
      groups[g].push(e);
    });
    if ($("tbl-se")) $("tbl-se").innerHTML = eventTable(groups.se);
    if ($("tbl-flag")) $("tbl-flag").innerHTML = eventTable(groups.flag);
    if ($("tbl-excl")) $("tbl-excl").innerHTML = eventTable(groups.excl);
    if ($("tbl-unv")) $("tbl-unv").innerHTML = eventTable(groups.unv);
    if ($("count")) $("count").textContent = rows.length + " rows shown (of " + (S.events || []).length + ")";
  }

  function filterWalk() {
    var q = (($("q") || {}).value || "").toLowerCase();
    var only30 = ($("only30") || {}).checked;
    Array.prototype.forEach.call(document.querySelectorAll("#walktbl tr.walkrow"), function (tr) {
      var ok = tr.getAttribute("data-ok") === "yes";
      var blob = (tr.getAttribute("data-hotel") + " " + tr.getAttribute("data-venue")).toLowerCase();
      var show = (!q || blob.indexOf(q) !== -1) && (!only30 || ok);
      tr.classList.toggle("hidden", !show);
    });
  }

  function filterSimple(tableId) {
    var q = (($("q") || {}).value || "").toLowerCase();
    var tbl = $(tableId);
    if (!tbl) return;
    Array.prototype.forEach.call(tbl.querySelectorAll("tbody tr"), function (tr) {
      tr.classList.toggle("hidden", q && tr.textContent.toLowerCase().indexOf(q) === -1);
    });
  }

  function calc() {
    var out = $("cOut");
    if (!out) return;
    var entries = +(($("cEntries") || {}).value) || 0;
    var buyin = +(($("cBuyin") || {}).value) || 0;
    var nights = +(($("cNights") || {}).value) || 0;
    var rate = +(($("cRate") || {}).value) || 0;
    var fee = +(($("cFee") || {}).value) || 0;
    var park = ($("cParking") || {}).checked ? 20 : 0;
    var nightCost = (rate + fee) * 1.1338 + park;
    var total = entries * buyin + nights * nightCost;
    out.innerHTML = "<b>entries × buy-ins</b> = " + entries + " × $" + buyin + " = <b>$" + (entries * buyin).toLocaleString() + "</b><br>" +
      "<b>true hotel cost/night</b> = ($" + rate + " + $" + fee + ") × 1.1338" + (park ? " + $" + park + " parking" : "") + " = <b>$" + nightCost.toFixed(2) + "</b><br>" +
      "<b>nights × true cost</b> = " + nights + " × $" + nightCost.toFixed(2) + " = <b>$" + (nights * nightCost).toFixed(2) + "</b><br>" +
      "<b>estimated cost of a trip</b> = <b>$" + total.toLocaleString(undefined, { maximumFractionDigits: 2 }) + "</b>" +
      (rate === 0 ? '<br><span class="tiny">Enter a logged dated room rate — no quote captured yet (see flagged F10).</span>' : "");
  }

  function fillHotels() {
    var sel = $("cHotel");
    if (!sel || !S.hotels) return;
    (S.hotels.rows || []).forEach(function (h) {
      var o = document.createElement("option");
      o.value = h.id; o.textContent = h.name + (h.resort_fee ? " (fee $" + h.resort_fee + ")" : " (fee blank)");
      sel.appendChild(o);
    });
    sel.addEventListener("change", function () {
      var h = (S.hotels.rows || []).filter(function (x) { return x.id === sel.value; })[0];
      if (h) { $("cFee").value = h.resort_fee != null ? h.resort_fee : ""; calc(); }
    });
  }

  function calendar() {
    var host = $("cal");
    if (!host || !S.trip) return;
    var h = "";
    (S.trip.day_plan || []).forEach(function (d) {
      h += '<div class="daycard"><div class="date">' + esc(d.date) + "</div>";
      if (d.primary) h += '<div class="primary"><b>Primary</b> ' + esc(d.primary.start) + " — " + esc(d.primary.name) + " ($" + d.primary.buy_in + ') <span class="elig">' + esc(d.primary.eligibility) + "</span></div>";
      else h += '<div class="primary muted">No confirmed event.</div>';
      if (d.fallback) h += '<div class="fallback"><b>Conditional fallback</b> ' + esc(d.fallback.start) + " — " + esc(d.fallback.name) + " ($" + d.fallback.buy_in + ")</div>";
      (d.overlap_flags || []).forEach(function (f) { h += '<div class="flagline">⚑ ' + esc(f) + "</div>"; });
      h += "</div>";
    });
    host.innerHTML = h;
  }

  ["q", "dfrom", "dto", "seOnly", "hideGated", "sort"].forEach(function (id) {
    var el = $(id);
    if (el) el.addEventListener("input", applyFilters);
    if (el) el.addEventListener("change", applyFilters);
  });
  if ($("only30")) $("only30").addEventListener("change", filterWalk);
  ["cEntries", "cBuyin", "cNights", "cRate", "cFee", "cParking"].forEach(function (id) {
    var el = $(id);
    if (el) el.addEventListener("input", calc);
    if (el) el.addEventListener("change", calc);
  });

  if ($("tbl-se") || $("tbl-flag") || $("tbl-excl") || $("tbl-unv")) applyFilters();
  if ($("walktbl")) filterWalk();
  if ($("hoteltbl") && $("q")) { $("q").addEventListener("input", function () { filterSimple("hoteltbl"); }); filterSimple("hoteltbl"); }
  if ($("wpttbl") && $("q")) { $("q").addEventListener("input", function () { filterSimple("wpttbl"); }); filterSimple("wpttbl"); }
  fillHotels();
  calc();
  calendar();
})();
