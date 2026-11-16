// Click a column header to sort; type in the filter box to narrow rows. No external dependencies.
(function () {
  function sortTable(table, col, dir) {
    var tbody = table.tBodies[0];
    var rows = Array.prototype.slice.call(tbody.rows);
    rows.sort(function (a, b) {
      var x = a.cells[col].getAttribute('data-v') || a.cells[col].textContent;
      var y = b.cells[col].getAttribute('data-v') || b.cells[col].textContent;
      var nx = parseFloat(String(x).replace(/[^0-9.\-]/g, '')), ny = parseFloat(String(y).replace(/[^0-9.\-]/g, ''));
      if (!isNaN(nx) && !isNaN(ny) && /^[\s$\-0-9.,×]*$/.test(String(x) + String(y))) return (nx - ny) * dir;
      return String(x).localeCompare(String(y)) * dir;
    });
    rows.forEach(function (r) { tbody.appendChild(r); });
  }
  document.querySelectorAll('table.sortable').forEach(function (t) {
    t.querySelectorAll('thead th').forEach(function (th) {
      th.addEventListener('click', function () {
        var dir = th.dataset.dir === 'asc' ? -1 : 1;
        t.querySelectorAll('thead th').forEach(function (o) { delete o.dataset.dir; });
        th.dataset.dir = dir === 1 ? 'asc' : 'desc';
        sortTable(t, +th.dataset.i, dir);
      });
    });
  });
  document.querySelectorAll('input.filter').forEach(function (inp) {
    inp.addEventListener('input', function () {
      var t = document.getElementById(inp.dataset.for);
      var q = inp.value.toLowerCase();
      Array.prototype.forEach.call(t.tBodies[0].rows, function (r) {
        r.style.display = r.textContent.toLowerCase().indexOf(q) > -1 ? '' : 'none';
      });
    });
  });
})();
