function fmt(n){return n.toLocaleString('en-US',{maximumFractionDigits:2})}
function money(n){return '$'+n.toLocaleString('en-US',{maximumFractionDigits:0})}

/* ---- generic table filter (events page + per-venue pages) ---- */
function applyFilters(tableId){
  var t=document.getElementById(tableId); if(!t) return;
  var q=(document.getElementById('q')||{}).value||'';
  var date=(document.getElementById('fdate')||{}).value||'';
  var venue=(document.getElementById('fvenue')||{}).value||'';
  var se=(document.getElementById('fse')||{}).checked;
  var free=(document.getElementById('ffree')||{}).checked;
  var unread=(document.getElementById('funread')||{}).checked;
  var confirmed=0;
  q=q.toLowerCase().trim(); var shown=0;
  t.querySelectorAll('tbody tr').forEach(function(tr){
    var hay=(tr.dataset.search||'').toLowerCase();
    var ok=true;
    if(q && hay.indexOf(q)===-1) ok=false;
    if(date && tr.dataset.date!==date) ok=false;
    if(venue && tr.dataset.venue!==venue) ok=false;
    /* "Single-entry confirmed" requires a positive statement from an official
       source. No row carries one, so this filter is expected to empty the
       table -- that is the finding, not a bug. */
    if(se && tr.dataset.single!=='1') ok=false;
    /* "Silent on entry limits" = a structure sheet was opened and printed no
       rule either way. Distinct from confirmed, and distinct from unread. */
    if(free && tr.dataset.silent!=='1') ok=false;
    if(unread && tr.dataset.silent==='1') ok=false;
    if(unread && tr.dataset.rule!=='not_stated') ok=false;
    tr.classList.toggle('hidden',!ok);
    if(ok) shown++;
  });
  var out=document.getElementById('shown');
  if(out) out.textContent=shown;
}

/* ---- trip cost calculator ---- */
function calcTrip(){
  var nights=+((document.getElementById('c_nights')||{}).value||0);
  var entries=+((document.getElementById('c_entries')||{}).value||0);
  var buyin=+((document.getElementById('c_buyin')||{}).value||0);
  var rate=+((document.getElementById('c_rate')||{}).value||0);
  var fee=+((document.getElementById('c_fee')||{}).value||0);
  var taxp=+((document.getElementById('c_tax')||{}).value||0);
  var park=+((document.getElementById('c_park')||{}).value||0);
  var parknights=+((document.getElementById('c_parknights')||{}).value||0);
  var other=+((document.getElementById('c_other')||{}).value||0);

  var feeTotal=fee*nights;
  var taxTotal=(rate+ fee)* (taxp/100) * nights;
  var roomTotal=rate*nights;
  var perNight=roomTotal/nights + fee + (rate+fee)*(taxp/100);
  var hotel=roomTotal+feeTotal+taxTotal;
  var parking=park*parknights;
  var tourn=entries*buyin;
  var total=hotel+parking+tourn+other;

  var set=function(id,v){var el=document.getElementById(id); if(el) el.textContent=v;};
  set('o_night','$'+fmt(perNight||0));
  set('o_room','$'+fmt(roomTotal||0));
  set('o_fee','$'+fmt(feeTotal||0));
  set('o_tax','$'+fmt(taxTotal||0));
  set('o_hotel','$'+fmt(hotel||0));
  set('o_park','$'+fmt(parking||0));
  set('o_tourn','$'+fmt(tourn||0));
  set('o_other','$'+fmt(other||0));
  set('o_total','$'+fmt(total||0));
  set('o_perday', nights>0 ? '$'+fmt(total/nights) : '—');
  set('o_perentry', entries>0 ? '$'+fmt(total/entries) : '—');
}
document.addEventListener('DOMContentLoaded',function(){
  var c=document.getElementById('c_nights');
  if(c){['c_nights','c_entries','c_buyin','c_rate','c_fee','c_tax','c_park','c_parknights','c_other']
    .forEach(function(id){var el=document.getElementById(id); if(el) el.addEventListener('input',calcTrip);});
    calcTrip();}
  ['q','fdate','fvenue','fse','ffree','funread'].forEach(function(id){
    var el=document.getElementById(id);
    if(el) el.addEventListener('input',function(){applyFilters('evtable');});
  });
  var reset=document.getElementById('freset');
  if(reset) reset.addEventListener('click',function(){
    ['q','fdate','fvenue'].forEach(function(id){var el=document.getElementById(id); if(el) el.value='';});
    ['fse','ffree','funread'].forEach(function(id){var el=document.getElementById(id); if(el) el.checked=false;});
    applyFilters('evtable');
  });
});
