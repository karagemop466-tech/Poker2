(() => {
  'use strict';

  const data = window.POKER_RESEARCH;
  if (!data) return;

  const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, ch => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  })[ch]);
  const money = value => value == null ? '—' : `$${Number(value).toLocaleString('en-US')}`;
  const sourceLink = key => {
    const source = data.sources[key];
    if (!source) return '';
    return `<a href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(source.label)} ↗</a>`;
  };
  const sourceLinks = keys => `<div class="source-links">${keys.map(sourceLink).join('')}</div>`;

  const tableBody = document.querySelector('#event-rows');
  const searchInput = document.querySelector('#event-search');
  const statusSelect = document.querySelector('#status-filter');
  const resultCount = document.querySelector('#event-results');
  const totalLabel = document.querySelector('#event-total');

  function renderEvents() {
    const query = searchInput.value.trim().toLowerCase();
    const status = statusSelect.value;
    const visible = data.events.filter(event => {
      const matchesStatus = status === 'all' ||
        (status === 'unconfirmed' && event.group === 'unconfirmed') ||
        (status === 'spend' && event.group === 'spend') ||
        (status === 'unknown' && event.group === 'unknown') ||
        (status === 'inactive' && event.group === 'inactive');
      const haystack = [event.date, event.time, event.venue, event.name, event.detail, event.finding, event.badge].join(' ').toLowerCase();
      return matchesStatus && (!query || haystack.includes(query));
    });

    tableBody.innerHTML = visible.length ? visible.map(event => `
      <tr data-group="${escapeHTML(event.group)}">
        <td>${escapeHTML(event.date)}</td>
        <td>${escapeHTML(event.time)}</td>
        <td>${escapeHTML(event.venue)}</td>
        <td><span class="event-name">${escapeHTML(event.name)}</span><span class="event-detail">${escapeHTML(event.detail)}</span></td>
        <td>${event.buyIn == null ? '—' : money(event.buyIn)}</td>
        <td>${event.guarantee == null ? '—' : money(event.guarantee)}</td>
        <td><span class="entry-badge badge-${escapeHTML(event.group)}">${escapeHTML(event.badge)}</span><span class="event-detail">${escapeHTML(event.finding)}</span></td>
        <td>${sourceLinks(event.sources)}</td>
      </tr>`).join('') : '<tr><td colspan="8" class="empty-state">No matching events. Try another search or status filter.</td></tr>';

    resultCount.textContent = `${visible.length} of ${data.events.length}`;
    totalLabel.textContent = `${data.events.length} source-linked records`;
  }

  function renderTimeline() {
    const target = document.querySelector('#timeline');
    target.innerHTML = data.timeline.map(item => `
      <article class="time-card"><time>${escapeHTML(item.time)}</time><b>${escapeHTML(item.title)}</b><p>${escapeHTML(item.text)}</p><div class="time-sources">${item.sources.map(sourceLink).join('')}</div></article>`).join('');
  }

  function renderHotels() {
    const target = document.querySelector('#hotel-grid');
    target.innerHTML = data.hotels.map(hotel => `
      <article class="hotel-card ${hotel.featured ? 'featured' : ''}">
        <div class="hotel-title-row"><h3>${escapeHTML(hotel.name)}</h3><span class="quality-pill">${escapeHTML(hotel.quality)}</span></div>
        <p class="hotel-relation">${escapeHTML(hotel.relation)}</p>
        <div class="hotel-facts">
          <div class="hotel-fact"><span>Resort fee</span><strong>${escapeHTML(hotel.fee)}</strong></div>
          <div class="hotel-fact"><span>Published starting rate</span><strong>${escapeHTML(hotel.rate)}</strong></div>
          <div class="hotel-fact"><span>True nightly total</span><strong class="unquoted">${escapeHTML(hotel.total)}</strong></div>
          <div class="hotel-fact"><span>Walk time</span><strong>Not measured</strong></div>
        </div>
        <p class="hotel-note">${escapeHTML(hotel.note)}</p>
        <div class="hotel-links">${hotel.sources.map(key => sourceLink(key)).join('')}</div>
      </article>`).join('');
  }

  function renderQuestions() {
    const target = document.querySelector('#question-grid');
    target.innerHTML = data.questions.map((question, index) => `
      <article class="question-card"><span class="question-index">${String(index + 1).padStart(2, '0')}</span><h3>${escapeHTML(question.title)}</h3><p>${escapeHTML(question.text)}</p></article>`).join('');
  }

  function renderSources() {
    const sources = Object.entries(data.sources);
    document.querySelector('#source-total').textContent = `${sources.length} official links`;
    document.querySelector('#source-grid').innerHTML = sources.map(([, source]) => `
      <article class="source-card"><a href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(source.label)} ↗</a><span>${escapeHTML(source.publisher)}</span></article>`).join('');
  }

  searchInput.addEventListener('input', renderEvents);
  statusSelect.addEventListener('change', renderEvents);
  renderEvents();
  renderTimeline();
  renderHotels();
  renderQuestions();
  renderSources();
})();
