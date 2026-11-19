
(function(){
  'use strict';
  var $=function(s){return document.querySelector(s)};
  var $$=function(s){return Array.prototype.slice.call(document.querySelectorAll(s))};

  function text(tr){return (tr.getAttribute('data-search')||'')+' '+tr.textContent.toLowerCase();}

  function vegasDate(){
    var parts=new Intl.DateTimeFormat('en-US',{timeZone:'America/Los_Angeles',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
    var date={}; parts.forEach(function(part){date[part.type]=part.value;});
    return date.year+'-'+date.month+'-'+date.day;
  }

  // ---- tournaments table -------------------------------------------------
  var t=$('#t');
  if(t){
    var q=$('#q'), df=$('#datef'), mbi=$('#maxbi'), sef=$('#sef'), ng=$('#nogtd'), cnt=$('#count');
    var pills=$$('.pill[data-g]'), until=$('#date-to'), past=$('#include-past');
    var today=vegasDate();
    if(/^#ev\d+$/.test(location.hash)){ past.checked=true; sef.checked=false; } // A source link can cite research.
    var activeGroups={};
    function run(){
      var s=(q.value||'').toLowerCase().trim();
      var d=df.value, mb=mbi.value?parseInt(mbi.value,10):null;
      var rows=$$('#t tbody tr'), shown=0;
      rows.forEach(function(tr){
        var ok=true;
        if(s && text(tr).indexOf(s)===-1) ok=false;
        function matches(date){return (!d||date>=d)&&(!until.value||date<=until.value)&&(past.checked||date>=today);}
        if(!(tr.getAttribute('data-dates')||'').split(' ').some(matches)) ok=false;
        tr.querySelectorAll('.slot').forEach(function(slot){slot.hidden=!matches(slot.getAttribute('data-slot-date'));});
        if(ok && mb!==null){var b=parseInt(tr.getAttribute('data-buyin')||'0',10); if(!b||b>mb) ok=false;}
        if(ok && sef.checked && tr.getAttribute('data-confirmed')!=='1') ok=false;
        if(ok && ng.checked && !(parseInt(tr.getAttribute('data-gtd')||'0',10)>0)) ok=false;
        if(ok && Object.keys(activeGroups).length && !activeGroups[tr.getAttribute('data-group')]) ok=false;
        tr.classList.toggle('hidden',!ok);
        if(ok) shown++;
      });
      cnt.textContent=shown+' of '+rows.length+' events shown.'+(sef.checked&&!shown?' No confirmed freezeout matches. Turn off the filter to see research only.':'');
    }
    [q,df,until,past,mbi,sef,ng].forEach(function(el){ el.addEventListener('input',run); el.addEventListener('change',run); });
    pills.forEach(function(p){p.addEventListener('click',function(){
      var g=p.getAttribute('data-g');
      if(activeGroups[g]) delete activeGroups[g]; else activeGroups[g]=1;
      p.classList.toggle('on'); run();
    });});
    $('#reset').addEventListener('click',function(){
      q.value=''; df.value=''; until.value=''; past.checked=false; mbi.value=''; sef.checked=true; ng.checked=false;
      activeGroups={}; pills.forEach(function(p){p.classList.remove('on')}); run();
    });
    $$('#t th').forEach(function(th,i){
      th.addEventListener('click',function(){
        var body=t.tBodies[0], rows=$$('#t tbody tr');
        var num=th.classList.contains('num');
        rows.sort(function(a,b){
          var x=a.cells[i].textContent.trim(), y=b.cells[i].textContent.trim();
          if(num){x=parseFloat(x.replace(/[^0-9.\-]/g,''))||0;y=parseFloat(y.replace(/[^0-9.\-]/g,''))||0;
                  return x-y;}
          return x.localeCompare(y);
        });
        if(th.getAttribute('data-desc')==='1'){rows.reverse(); th.setAttribute('data-desc','0');}
        else th.setAttribute('data-desc','1');
        rows.forEach(function(r){body.appendChild(r)});
      });
    });
    run();
  }

  // ---- schedule page -----------------------------------------------------
  if($('#df')){
    var df2=$('#df'), ov=$('#ov'), past=$('#past'), c2=$('#c'), panels=$$('.panel[data-date]');
    var today=vegasDate();
    function run2(){
      var d=df2.value, shown=0;
      panels.forEach(function(p){
        var ok=true;
        if(d && p.getAttribute('data-date')!==d) ok=false;
        if(ok && !past.checked && !d && p.getAttribute('data-date')<today) ok=false;
        if(ok && ov.checked && p.getAttribute('data-overlap')!=='1') ok=false;
        p.style.display=ok?'':'none';
        if(ok) shown++;
      });
      c2.textContent=shown+' of '+panels.length+' days shown.';
    }
    df2.addEventListener('change',run2); ov.addEventListener('change',run2); past.addEventListener('change',run2); run2();
  }

  var google30=$('#google30');
  if(google30)google30.addEventListener('change',function(){
    $$('tr[data-google-min]').forEach(function(tr){tr.hidden=google30.checked && Number(tr.dataset.googleMin)>30;});
  });

  // ---- walking page ------------------------------------------------------
  if($('#v')){
    var v=$('#v'), w30=$('#w30'), w15=$('#w15'), wc=$('#wc'), maps=$('#maps-evidence');
    var prs=$$('.panel[data-venue]'), all=$$('.panel[data-venue] tbody tr');
    function run3(){
      var vv=v.value, shown=0, shownp=0;
      prs.forEach(function(p){
        var pok=(!vv||p.getAttribute('data-venue')===vv);
        p.style.display=pok?'':'none';
        if(pok) shownp++;
      });
      all.forEach(function(tr){
        var m=parseFloat(tr.getAttribute('data-min'));
        var ok=(!vv||tr.closest('.panel').getAttribute('data-venue')===vv);
        if(ok && w30.checked && !(m<=30)) ok=false;
        if(ok && w15.checked && !(m<=15)) ok=false;
        if(ok && maps.checked && tr.getAttribute('data-maps')!=='1')ok=false;
        tr.classList.toggle('hidden',!ok);
        if(ok) shown++;
      });
      wc.textContent=shown+' of '+all.length+' hotel\u2013room pairs shown ('+shownp+' rooms).';
    }
    [v,w30,w15,maps].forEach(function(el){el.addEventListener('change',run3)});
    run3();
  }

  function fmt(n){return n===null ? 'Not available' : n.toLocaleString('en-US',{style:'currency',currency:'USD'});}
  function number(input){return input.value!=='' && input.validity.valid && Number.isFinite(input.valueAsNumber)
    ? input.valueAsNumber : null;}

  function setupLodging(p, onTotal){
    var hotel=$('#'+p+'-hotel'), book=$('#'+p+'-book'), checkout=$('#'+p+'-checkout');
    var fields=['rate','fee','tax','fee-tax','park','nights'].map(function(key){return $('#'+p+'-'+key);});
    function update(){
      var v=fields.map(number);
      var nightly=v.slice(0,5).includes(null) ? null : Math.round((v[0]*(1+v[2]/100)+v[1]*(1+v[3]/100)+v[4])*100)/100;
      var n=v[5], total=nightly===null || n===null ? null : nightly*n;
      if(checkout && (checkout.value!=='' || checkout.validity.badInput)){
        total=number(checkout);
        nightly=n>0 && total!==null ? total/n : null;
      }
      if(n===0){total=0; nightly=null;}
      else if(n===null){total=null; nightly=null;}
      $(p==='t'?'#tot-night':'#h-night').textContent=fmt(nightly);
      $(p==='t'?'#tot-hotel':'#h-total').textContent=fmt(total);
      if(onTotal)onTotal(total);
    }
    hotel.addEventListener('change',function(){
      var opt=hotel.options[hotel.selectedIndex];
      fields[0].value=''; fields[1].value=opt.dataset.fee; fields[2].value=opt.dataset.tax;
      fields[3].value=''; fields[4].value='';
      if(checkout)checkout.value='';
      book.href=opt.dataset.book || 'hotels.html#checkout-log';
      book.textContent=opt.dataset.book ? 'Official booking for '+opt.textContent : 'Official booking links and lookup log';
      update();
    });
    if(checkout)checkout.addEventListener('input',update);
    fields.forEach(function(f){f.addEventListener('input',update);}); update();
  }
  if($('#h-rate'))setupLodging('h');

  // ---- single-room walking table (venue pages) --------------------------
  var rw=$('#w30[data-walk-room]');
  if(rw){
    var rt=document.getElementById('wt-'+rw.getAttribute('data-walk-room'));
    var rwc=document.getElementById('wc');
    function runRoom(){
      var rows=rt.tBodies[0].rows, n=0;
      Array.prototype.forEach.call(rows,function(tr){
        var m=parseFloat(tr.getAttribute('data-min'));
        var ok=!rw.checked||(m<=30);
        tr.classList.toggle('hidden',!ok); if(ok)n++;
      });
      rwc.textContent=n+' of '+rows.length+' hotels shown.';
    }
    rw.addEventListener('change',runRoom); runRoom();
  }

  // ---- site-wide search across every table on every page ----------------
  function pagePrefix(){
    // venues/*.html sits one level down
    return location.pathname.indexOf('/venues/') !== -1 ? '../' : '';
  }
  var box=$('#gs'), res=$('#gs-res'), stat=$('#gs-status');
  if(box && window.SEARCH_INDEX){
    var IDX=window.SEARCH_INDEX, LIMIT=40;
    function esc(t){var d=document.createElement('div');d.textContent=t;return d.innerHTML;}
    function runSearch(){
      var q=(box.value||'').toLowerCase().trim();
      if(!q){res.innerHTML='';stat.textContent=IDX.length+' rows indexed across every table on the site.';return;}
      var terms=q.split(/\s+/), hits=[];
      for(var i=0;i<IDX.length;i++){
        // search the table label, the row heading and every cell, not just the caption
        var r=IDX[i], hay=(r.t+' '+r.h+' '+(r.x||'')).toLowerCase(), ok=true;
        for(var j=0;j<terms.length;j++){ if(hay.indexOf(terms[j])===-1){ok=false;break;} }
        if(ok) hits.push(r);
      }
      var byPage={};
      hits.forEach(function(h){ (byPage[h.p]=byPage[h.p]||[]).push(h); });
      var html='';
      Object.keys(byPage).forEach(function(pg){
        html+='<div class="gs-group"><h3><a href="'+pagePrefix()+pg+'">'+esc(byPage[pg][0].pl)+'</a>'
             +' <span class="note">'+byPage[pg].length+' match'+(byPage[pg].length===1?'':'es')+'</span></h3><ul class="tight">';
        byPage[pg].slice(0,LIMIT).forEach(function(h){
          html+='<li><a href="'+pagePrefix()+pg+(h.a?'#'+h.a:'')+'">'+esc(h.h)+'</a>'
               +' <span class="note">'+esc(h.t.slice(0,180))+'</span></li>';
        });
        if(byPage[pg].length>LIMIT) html+='<li class="note">&hellip; '+(byPage[pg].length-LIMIT)+' more in this table</li>';
        html+='</ul></div>';
      });
      res.innerHTML=html;
      stat.textContent=hits.length+' row'+(hits.length===1?'':'s')+' match \u201c'+box.value.trim()+'\u201d'
        +' in '+Object.keys(byPage).length+' table'+(Object.keys(byPage).length===1?'':'s')+'.';
    }
    box.addEventListener('input',runSearch);
    var clr=$('#gs-clear');
    if(clr) clr.addEventListener('click',function(){box.value='';runSearch();box.focus();});
    runSearch();
  }

  // ---- trip calculator ---------------------------------------------------
  if($('#pick')){
    var pick=$('#pick'), body=$('#cart').tBodies[0], add=$('#add');
    var research=$('#research-entries'), hotelTotal=null;
    function alreadyPicked(){return pick.value && Array.from(body.rows).some(function(tr){return tr.dataset.event===pick.value;});}
    function recalc(){
      var buyin=$$('#cart tbody tr').reduce(function(sum,tr){return sum+Number(tr.dataset.subtotal);},0);
      $('#tot-buyin').textContent=fmt(buyin);
      $('#tot-all').textContent=fmt(hotelTotal===null ? null : buyin+hotelTotal);
      add.disabled=!pick.value || alreadyPicked();
    }
    function filterCart(){
      var choice=pick.value;
      Array.from(pick.options).forEach(function(o){if(o.value)o.hidden=o.disabled=!research.checked && o.dataset.confirmed!=='1';});
      if(!research.checked){
        $$('#cart tbody tr[data-research="true"]').forEach(function(tr){tr.remove();});
      }
      if(choice && (!pick.options[pick.selectedIndex] || pick.options[pick.selectedIndex].disabled))pick.value='';
      recalc();
    }
    add.addEventListener('click',function(){
      var o=pick.options[pick.selectedIndex];
      if(!o || !o.value || o.disabled || alreadyPicked())return;
      var tr=body.insertRow(), cost=Number(o.dataset.buyin);
      tr.dataset.event=o.value;
      tr.dataset.subtotal=cost;
      tr.dataset.research=o.dataset.confirmed!=='1';
      var link=document.createElement('a'); link.href='tournaments.html#ev'+o.value; link.textContent=o.textContent;
      tr.insertCell().appendChild(link); tr.insertCell().textContent=1; tr.insertCell().textContent=fmt(cost);
      var del=document.createElement('button'); del.type='button'; del.className='btn'; del.textContent='Remove';
      tr.insertCell().appendChild(del); del.addEventListener('click',function(){tr.remove();recalc();}); recalc();
    });
    pick.addEventListener('change',recalc);
    research.addEventListener('change',filterCart); setupLodging('t',function(total){hotelTotal=total;recalc();}); filterCart();
  }
})();
