
(function(){
  'use strict';
  var $=function(s){return document.querySelector(s)};
  var $$=function(s){return Array.prototype.slice.call(document.querySelectorAll(s))};

  function text(tr){return (tr.getAttribute('data-search')||'')+' '+tr.textContent.toLowerCase();}

  // ---- tournaments table -------------------------------------------------
  var t=$('#t');
  if(t){
    var q=$('#q'), df=$('#datef'), mbi=$('#maxbi'), sef=$('#sef'), ng=$('#nogtd'), cnt=$('#count');
    var pills=$$('#t-pills .pill, .pill[data-g]');
    var activeGroups={};
    function run(){
      var s=(q.value||'').toLowerCase().trim();
      var d=df.value, mb=mbi.value?parseInt(mbi.value,10):null;
      var rows=$$('#t tbody tr'), shown=0;
      rows.forEach(function(tr){
        var ok=true;
        if(s && text(tr).indexOf(s)===-1) ok=false;
        if(ok && d && (tr.getAttribute('data-dates')||'').split(' ').indexOf(d)===-1) ok=false;
        if(ok && mb!==null){var b=parseInt(tr.getAttribute('data-buyin')||'0',10); if(!b||b>mb) ok=false;}
        if(ok && sef.checked && tr.getAttribute('data-group')!=='candidate') ok=false;
        if(ok && ng.checked && !(parseInt(tr.getAttribute('data-gtd')||'0',10)>0)) ok=false;
        if(ok && Object.keys(activeGroups).length && !activeGroups[tr.getAttribute('data-group')]) ok=false;
        tr.classList.toggle('hidden',!ok);
        if(ok) shown++;
      });
      cnt.textContent=shown+' of '+rows.length+' events shown.';
    }
    [q,df,mbi,sef,ng].forEach(function(el){ el.addEventListener('input',run); el.addEventListener('change',run); });
    pills.forEach(function(p){p.addEventListener('click',function(){
      var g=p.getAttribute('data-g');
      if(activeGroups[g]) delete activeGroups[g]; else activeGroups[g]=1;
      p.classList.toggle('on'); run();
    });});
    $('#reset').addEventListener('click',function(){
      q.value=''; df.value=''; mbi.value=''; sef.checked=false; ng.checked=false;
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
        if(ok && ov.checked && !p.querySelector('.t-bad')) ok=false;
        p.style.display=ok?'':'none';
        if(ok) shown++;
      });
      c2.textContent=shown+' of '+panels.length+' days shown.';
    }
    df2.addEventListener('change',run2); ov.addEventListener('change',run2); run2();
  }

  // ---- walking page ------------------------------------------------------
  if($('#v')){
    var v=$('#v'), w30=$('#w30'), w15=$('#w15'), wc=$('#wc');
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
        tr.classList.toggle('hidden',!ok);
        if(ok) shown++;
      });
      wc.textContent=shown+' of '+all.length+' hotel\u2013room pairs shown ('+shownp+' rooms).';
    }
    [v,w30,w15].forEach(function(el){el.addEventListener('change',run3)});
    run3();
  }

  function fmt(n){return '$'+Math.round(n).toLocaleString('en-US')}

  // ---- hotels calculator -------------------------------------------------
  if($('#h-rate')){
    var H={r:$('#h-rate'),f:$('#h-fee'),t:$('#h-tax'),p:$('#h-park'),n:$('#h-nights')};
    var o={s:$('#o-sub'),x:$('#o-tax'),nn:$('#o-night'),tt:$('#o-total')};
    var note=$('#h-note');
    function run4(){
      var r=+H.r.value||0, f=+H.f.value||0, tx=(+H.t.value||0)/100, pk=+H.p.value||0, n=+H.n.value||1;
      var sub=r+f, tax=sub*tx, night=sub+tax+pk, tot=night*n;
      o.s.textContent=fmt(sub); o.x.textContent=fmt(tax);
      o.nn.textContent=fmt(night); o.tt.textContent=fmt(tot);
      note.textContent='Tax is applied to room rate + resort fee because the official Venetian page says '
        +'the resort fee is "$55 plus tax". Parking is not taxable. '
        +'The nightly rate you enter is not verified by this site \u2014 enter the quote you are given.';
    }
    Object.keys(H).forEach(function(k){H[k].addEventListener('input',run4)});
    run4();
  }

  // ---- trip calculator ---------------------------------------------------
  if($('#pick')){
    var pick=$('#pick'), body=$('#cart').tBodies[0];
    var R={r:$('#t-rate'),f:$('#t-fee'),t:$('#t-tax'),p:$('#t-park'),n:$('#t-nights')};
    function recalc(){
      var buyin=0,pool=0;
      $$('#cart tbody tr').forEach(function(tr){
        buyin+=parseFloat(tr.getAttribute('data-buyin'))||0;
        pool+=parseFloat(tr.getAttribute('data-pool'))||0;
      });
      var r=+R.r.value||0, f=+R.f.value||0, tx=(+R.t.value||0)/100, pk=+R.p.value||0, n=+R.n.value||0;
      var night=(r+f)*(1+tx)+pk, hotel=night*n;
      $('#sum-buyin').textContent=fmt(buyin);
      $('#sum-pool').textContent=fmt(pool);
      $('#tot-buyin').textContent=fmt(buyin);
      $('#tot-night').textContent=fmt(night);
      $('#tot-hotel').textContent=fmt(hotel);
      $('#tot-all').textContent=fmt(buyin+hotel);
    }
    $('#add').addEventListener('click',function(){
      var o=pick.options[pick.selectedIndex]; if(!o||!o.value) return;
      var tr=document.createElement('tr');
      tr.setAttribute('data-buyin',o.getAttribute('data-buyin'));
      tr.setAttribute('data-pool',o.getAttribute('data-pool')||'0');
      tr.innerHTML='<td class="num">'+o.value+'</td><td>'+o.textContent+'</td>'
        +'<td class="num">'+fmt(+o.getAttribute('data-buyin'))+'</td>'
        +'<td class="num">'+(o.getAttribute('data-pool')?fmt(+o.getAttribute('data-pool')):'\u2014')+'</td>'
        +'<td><button class="btn del">remove</button></td>';
      tr.querySelector('.del').addEventListener('click',function(){tr.remove();recalc()});
      body.appendChild(tr); recalc();
    });
    Object.keys(R).forEach(function(k){R[k].addEventListener('input',recalc)});
    recalc();
  }
})();
