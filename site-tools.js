(() => {
  const style = document.createElement('style');
  style.textContent = `
    .site-tools{margin:16px 0;padding:14px 16px;border:1px solid #dce4e9;border-radius:12px;background:#fff;display:flex;gap:12px;align-items:end;flex-wrap:wrap}
    .site-tools label{display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:700;color:#34454e}
    .site-tools input{font:inherit;font-weight:400;padding:9px 11px;border:1px solid #c7d2d8;border-radius:8px;min-width:min(340px,80vw)}
    .site-tools .filter-count{font-size:12px;color:#66777f;margin-left:auto}
    .site-nav-extra{display:flex;gap:14px;flex-wrap:wrap;margin-left:12px}
    .site-nav-extra a{font-size:13px}
    .global-search-results{position:relative;margin:-8px 0 18px;padding:12px 16px;background:#fff;border:1px solid #dce4e9;border-radius:12px;box-shadow:0 8px 24px #142b3710;max-height:360px;overflow:auto}
    .global-search-results ol{margin:6px 0 0;padding-left:24px}.global-search-results li{margin:8px 0}.global-search-results a{font-weight:700}.global-search-results small{display:block;color:#66777f}
    .source-change-flag{display:inline-block;margin:4px 4px 4px 0;padding:3px 7px;border-radius:8px;background:#fff0d8;color:#804300;font-size:11px;font-weight:750}
  `;
  document.head.append(style);

  const tables = [...document.querySelectorAll('main table')];
  if (tables.length) {
    const controls = document.createElement('div');
    controls.className = 'site-tools';
    controls.innerHTML = '<label>Search all tables<input type="search" placeholder="Search events, hotels, status, source…" aria-label="Search all tables across the site"></label><label class="date-filter" hidden>Show event date<input type="date" aria-label="Filter tournament rows by date"></label><label class="freezeout-filter" hidden style="flex-direction:row;align-items:center"><input type="checkbox" aria-label="Show only officially confirmed single-entry freezeouts" style="min-width:auto">Confirmed single-entry / freezeout only</label><label class="walk-filter" hidden style="flex-direction:row;align-items:center"><input type="checkbox" aria-label="Show only hotels with a verified walk of 30 minutes or less" style="min-width:auto">Verified walk ≤30 minutes only</label><span class="filter-count" aria-live="polite"></span>';
    const main = document.querySelector('main');
    const firstTable = tables[0].closest('.tablewrap, .table-wrap') || tables[0];
    let insertionPoint = firstTable;
    while (insertionPoint.parentElement && insertionPoint.parentElement !== main) insertionPoint = insertionPoint.parentElement;
    main.insertBefore(controls, insertionPoint);
    const globalResults = document.createElement('div');
    globalResults.className = 'global-search-results';
    globalResults.hidden = true;
    globalResults.setAttribute('aria-live','polite');
    main.insertBefore(globalResults, insertionPoint);
    const search = controls.querySelector('input[type=search]');
    const date = controls.querySelector('input[type=date]');
    const strict = controls.querySelector('.freezeout-filter input');
    const walk = controls.querySelector('.walk-filter input');
    const count = controls.querySelector('.filter-count');
    const eventPage = /tournaments(?:\.html)?$/i.test(location.pathname);
    if (eventPage && tables[0]) tables[0].classList.add('event-table');
    const eventTables = tables.filter(table => table.classList.contains('event-table'));
    const hotelTables = tables.filter(table => table.classList.contains('hotel-table'));
    if (eventTables.length) {
      controls.querySelector('.date-filter').hidden = false;
      controls.querySelector('.freezeout-filter').hidden = false;
    }
    if (hotelTables.length) controls.querySelector('.walk-filter').hidden = false;

    const rows = tables.flatMap(table => [...table.querySelectorAll('tbody tr')]);
    let searchIndex = [];
    const siteRoot = new URL('.', document.currentScript.src);
    fetch(new URL('data/site-search.json', siteRoot), { cache: 'no-store' }).then(response => response.ok ? response.json() : null).then(doc => { searchIndex = doc?.rows || []; if (search.value.trim()) updateGlobalResults(); }).catch(() => {});
    fetch(new URL('data/source-monitor.json', siteRoot), { cache: 'no-store' }).then(response => response.ok ? response.json() : null).then(report => {
      if (location.pathname.endsWith('/source-monitor.html')) return;
      const changed = new Set((report?.sources || []).filter(source => source.status === 'changed').map(source => new URL(source.url).href));
      if (!changed.size) return;
      for (const table of tables) for (const row of table.querySelectorAll('tbody tr')) {
        const hasChange = [...row.querySelectorAll('a[href]')].some(link => { try { return changed.has(new URL(link.href, location.href).href); } catch { return false; } });
        if (!hasChange || row.querySelector('.source-change-flag')) continue;
        const cell = row.cells[0] || row;
        const badge = document.createElement('span'); badge.className = 'source-change-flag'; badge.textContent = 'Official source changed · review'; badge.title = 'The linked source response differs from its previous successful check. Re-verify values before updating this row.';
        cell.append(document.createElement('br'), badge);
        row.dataset.sourceStatus = 'changed';
      }
    }).catch(() => {});
    const updateGlobalResults = () => {
      const query = search.value.trim().toLocaleLowerCase();
      globalResults.replaceChildren();
      if (query.length < 2) { globalResults.hidden = true; return; }
      const matches = searchIndex.filter(item => `${item.title} ${item.text}`.toLocaleLowerCase().includes(query)).slice(0, 12);
      const heading = document.createElement('strong');
      heading.textContent = searchIndex.length ? `Site-wide table matches${matches.length === 12 ? ' (first 12)' : ''}` : 'Cross-page search index is not available yet';
      globalResults.append(heading);
      if (matches.length) {
        const list = document.createElement('ol');
        for (const item of matches) {
          const li = document.createElement('li');
          const link = document.createElement('a'); link.href = new URL(item.page, siteRoot).href; link.textContent = item.title || item.page; li.append(link);
          const snippet = document.createElement('small'); snippet.textContent = item.text; li.append(snippet); list.append(li);
        }
        globalResults.append(list);
      } else {
        const message = document.createElement('p'); message.textContent = searchIndex.length ? 'No matching table rows.' : 'Search the current page; the cross-page table index has not been generated.'; globalResults.append(message);
      }
      globalResults.hidden = false;
    };
    const refresh = () => {
      const needle = search.value.trim().toLocaleLowerCase();
      const chosenDate = date.value;
      let shown = 0;
      for (const row of rows) {
        const textMatch = !needle || row.innerText.toLocaleLowerCase().includes(needle);
        let dateMatch = true;
        const eventRow = eventTables.some(table => table.contains(row));
        if (chosenDate && eventRow) {
          const explicit = row.dataset.date;
          const start = row.dataset.dateStart || explicit || '';
          const end = row.dataset.dateEnd || explicit || '';
          const cellText = row.cells[0]?.innerText || '';
          let parsed = explicit || '';
          if (!start) {
            const iso = cellText.match(/\b(\d{4}-\d{2}-\d{2})\b/);
            const human = cellText.match(/\b([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})\b/);
            if (iso) parsed = iso[1];
            else if (human) {
              const month = new Date(`${human[1]} 1, 2000`).getMonth() + 1;
              parsed = `${human[3]}-${String(month).padStart(2,'0')}-${String(human[2]).padStart(2,'0')}`;
            }
          }
          const rangeStart = start || parsed;
          const rangeEnd = end || parsed;
          dateMatch = rangeStart && rangeEnd ? chosenDate >= rangeStart && chosenDate <= rangeEnd : false;
        }
        const ruleText = row.innerText.toLocaleLowerCase();
        const hotelRow = hotelTables.some(table => table.contains(row));
        const strictMatch = !strict.checked || !eventRow || row.dataset.singleEntry === 'confirmed' || /confirmed (single-entry|freezeout)/i.test(ruleText);
        const walkMinutes = Number(row.dataset.walkMinutes);
        const walkMatch = !walk.checked || !hotelRow || (row.dataset.walkMinutes !== '' && Number.isFinite(walkMinutes) && walkMinutes <= 30);
        row.hidden = !(textMatch && dateMatch && strictMatch && walkMatch);
        if (!row.hidden) shown++;
      }
      count.textContent = (needle || chosenDate) ? `${shown} of ${rows.length} rows shown on this page` : `${rows.length} rows on this page`;
      updateGlobalResults();
    };
    search.addEventListener('input', refresh);
    date.addEventListener('change', refresh);
    strict.addEventListener('change', refresh);
    walk.addEventListener('change', refresh);
    refresh();
  }
})();
