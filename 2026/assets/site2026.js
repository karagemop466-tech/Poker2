
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
    if(/^#ev\d+$/.test(location.hash)) past.checked=true;  // Index links can cite historical rows.
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
      cnt.textContent=shown+' of '+rows.length+' events shown.'+(sef.checked&&!shown?' No events meet the confirmed freezeout filter.':'');
    }
    [q,df,until,past,mbi,sef,ng].forEach(function(el){ el.addEventListener('input',run); el.addEventListener('change',run); });
    pills.forEach(function(p){p.addEventListener('click',function(){
      var g=p.getAttribute('data-g');
      if(activeGroups[g]) delete activeGroups[g]; else activeGroups[g]=1;
      p.classList.toggle('on'); run();
    });});
    $('#reset').addEventListener('click',function(){
      q.value=''; df.value=''; until.value=''; past.checked=false; mbi.value=''; sef.checked=false; ng.checked=false;
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
    var df2=$('#df'), ov=$('#ov'), c2=$('#c'), panels=$$('.panel[data-date]');
    function run2(){
      var d=df2.value, shown=0;
      panels.forEach(function(p){
        var ok=true;
        if(d && p.getAttribute('data-date')!==d) ok=false;
        if(ok && ov.checked && p.getAttribute('data-multiple')!=='1') ok=false;
        p.style.display=ok?'':'none';
        if(ok) shown++;
      });
      c2.textContent=shown+' of '+panels.length+' days shown.';
    }
    df2.addEventListener('change',run2); ov.addEventListener('change',run2); run2();
  }

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
        if(ok && maps.checked && tr.getAttribute('data-maps')!=='1') ok=false;
        tr.classList.toggle('hidden',!ok);
        if(ok) shown++;
      });
      wc.textContent=shown+' of '+all.length+' hotel\u2013room pairs shown ('+shownp+' rooms).';
    }
    [v,w30,w15,maps].forEach(function(el){el.addEventListener('change',run3)});
    run3();
  }

  function fmt(n){return n==null?'\u2014':n.toLocaleString('en-US',{style:'currency',currency:'USD'});}
  function hotelCost(H){
    function read(el){return el.value!==''&&el.validity.valid ? Number(el.value) : null;}
    var r=read(H.r), f=read(H.f), t=read(H.t), p=read(H.p), n=read(H.n);
    var sub=r!=null&&f!=null?r+f:null;
    var tax=sub!=null&&t!=null?sub*t/100:null;
    var night=tax!=null&&p!=null?sub+tax+p:null;
    return {sub:sub,tax:tax,night:night,total:n===0?0:night!=null&&n!=null?night*n:null};
  }

  // ---- hotels calculator -------------------------------------------------
  if($('#h-rate')){
    var H={r:$('#h-rate'),f:$('#h-fee'),t:$('#h-tax'),p:$('#h-park'),n:$('#h-nights')};
    var o={s:$('#o-sub'),x:$('#o-tax'),nn:$('#o-night'),tt:$('#o-total')};
    var note=$('#h-note');
    function run4(){
      var valid=Object.keys(H).every(function(k){return H[k].value!=='' && Number.isFinite(+H[k].value) && +H[k].value>=0});
      if(!valid || !Number.isInteger(+H.n.value) || +H.n.value<1){
        Object.keys(o).forEach(function(k){o[k].textContent='Not available'});
        note.textContent='No complete quote. Blank rate, tax, fee or parking is unknown, not zero. Dates, occupancy and a final checkout total are still required.';
        return;
      }
      var r=+H.r.value, f=+H.f.value, tx=(+H.t.value)/100, pk=+H.p.value, n=+H.n.value;
      var sub=r+f, tax=sub*tx, night=sub+tax+pk, tot=night*n;
      o.s.textContent=fmt(sub); o.x.textContent=fmt(tax);
      o.nn.textContent=fmt(night); o.tt.textContent=fmt(tot);
      note.textContent='Illustrative formula: (room + resort fee) × (1 + tax rate) + tax-inclusive parking. This assumes the same tax rate on room and resort fee; verify the itemized checkout. Never add fees twice if already included. Not a live quote.';
    }
    if($('#h-hotel')) $('#h-hotel').addEventListener('change',function(){
      var option=this.options[this.selectedIndex];
      H.f.value=option.getAttribute('data-fee'); H.t.value=option.getAttribute('data-tax');
      H.r.value=''; H.p.value=''; run4();
    });
    Object.keys(H).forEach(function(k){H[k].addEventListener('input',run4)});
    run4();
  }

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
    var pick=$('#pick'), body=$('#cart').tBodies[0];
    var checkout=$('#t-checkout'), nights=$('#t-nights');
    function setCost(selector, amount){
      $(selector).textContent=amount===null?'Not available':amount.toLocaleString('en-US',{style:'currency',currency:'USD'});
    }
    function recalc(){
      var buyin=0,pool=0;
      $$('#cart tbody tr').forEach(function(tr){
        buyin+=parseFloat(tr.getAttribute('data-buyin'))||0;
        pool+=parseFloat(tr.getAttribute('data-pool'))||0;
      });
      var n=nights.valueAsNumber, quote=checkout.valueAsNumber;
      var valid=Number.isInteger(n)&&n>0&&Number.isFinite(quote)&&quote>=0&&checkout.validity.valid;
      var hotel=n===0?0:valid?quote:null;
      setCost('#sum-buyin',buyin);
      setCost('#sum-pool',pool);
      setCost('#tot-buyin',buyin);
      setCost('#tot-night',valid?quote/n:null);
      setCost('#tot-hotel',hotel);
      setCost('#tot-all',hotel===null?null:buyin+hotel);
    }
    $('#add').addEventListener('click',function(){
      var o=pick.options[pick.selectedIndex]; if(!o||!o.value) return;
      if(body.querySelector('[data-event="'+o.value+'"]')) return;
      var tr=document.createElement('tr');
      tr.setAttribute('data-event',o.value);
      tr.setAttribute('data-buyin',o.getAttribute('data-buyin'));
      tr.setAttribute('data-pool',o.getAttribute('data-pool')||'0');
      tr.innerHTML='<td class="num">'+o.value+'</td><td>'+o.textContent+'</td>'
        +'<td class="num">'+fmt(+o.getAttribute('data-buyin'))+'</td>'
        +'<td class="num">'+(o.getAttribute('data-pool')?fmt(+o.getAttribute('data-pool')):'\u2014')+'</td>'
        +'<td><button class="btn del">remove</button></td>';
      tr.querySelector('.del').addEventListener('click',function(){tr.remove();recalc()});
      body.appendChild(tr); recalc();
    });
    [checkout,nights].forEach(function(input){input.addEventListener('input',recalc)});
    recalc();
  }
})();
