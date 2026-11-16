(() => {
  const summary = document.getElementById('summary');
  const notice = document.getElementById('notice');
  const tbody = document.querySelector('#source-table tbody');
  const addCell = (row, text, cls) => { const cell=document.createElement('td'); if(cls){const badge=document.createElement('span');badge.className=`status-badge status-${cls}`;badge.textContent=text;cell.append(badge);}else cell.textContent=text ?? ''; row.append(cell); };
  const fmt = value => value ? new Date(value).toLocaleString('en-GB',{timeZone:'UTC',dateStyle:'medium',timeStyle:'short'})+' UTC' : '—';
  fetch('data/source-monitor.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('No report is available yet.');return r.json();}).then(report=>{
    const changed=report.changed_count||0, unavailable=report.unavailable_count||0;
    summary.replaceChildren();
    [[fmt(report.last_checked),'Last checked'],[report.sources?.length||0,'Registered sources'],[changed,'Changed · review'],[unavailable,'Unavailable']].forEach(([value,label])=>{const chip=document.createElement('div');chip.className='monitor-chip';const b=document.createElement('b');b.textContent=value;chip.append(b,document.createTextNode(label));summary.append(chip);});
    notice.textContent=report.last_checked?`Comparison method: ${report.comparison||'response-body SHA-256'}. ${report.first_run_note||''}`:'No scheduled check has run yet. The first scheduled run will create initial source baselines; it cannot identify a change until a later successful check.';
    (report.sources||[]).forEach(source=>{const tr=document.createElement('tr');addCell(tr,source.status,source.status);const title=document.createElement('td');const a=document.createElement('a');a.href=source.url;a.textContent=source.label||source.id;a.target='_blank';a.rel='noopener noreferrer';title.append(a);tr.append(title);addCell(tr,fmt(source.last_checked));addCell(tr,source.http_status||'—');addCell(tr,source.detail||'');tbody.append(tr);});
    if(!report.sources?.length)notice.className='empty';
  }).catch(()=>{notice.textContent='No scheduled monitoring report is available yet. The daily check is configured for 07:00 UTC; after its first successful run this page will show the checked sources and change flags.';});
})();
