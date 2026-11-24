/* Country maps, phones only (Marc 2026-11-24): airport buttons, plane marks and
   their code labels keep one fixed on-screen size at every zoom level (pinch,
   wheel or +/- buttons). Desktop is untouched.
   - plane mark: counter-scaled by --k (viewBox width / full width), never under 8px;
   - invisible tap target: 34px circle around each airport;
   - airport code / name labels: fixed px font size and halo.
   Works with country-map.js and usa-map.js (both keep the SVG in #map). */
(function(){
  var MQ=window.matchMedia?window.matchMedia('(max-width: 900px)'):null;
  var NS='http://www.w3.org/2000/svg';
  var MARK_MIN_PX=8, HIT_PX=34, CODE_PX=8, NAME_PX=7.5;
  var obs=null, bound=null;
  function mobile(){ return !!(MQ&&MQ.matches); }
  function geom(m){
    var r=m.getBoundingClientRect(); var W=r.width||m.clientWidth||0;
    var vb=m.viewBox&&m.viewBox.baseVal; if(!W||!vb||!vb.width) return null;
    var k=parseFloat(m.style.getPropertyValue('--k'))||1;
    return {upp:vb.width/W, k:k};
  }
  function clear(m){
    m.classList.remove('mz-fixed');
    m.querySelectorAll('circle.ap-hit').forEach(function(c){ c.parentNode.removeChild(c); });
    m.querySelectorAll('[data-mzfs]').forEach(function(t){ t.style.removeProperty('display'); t.style.removeProperty('font-size'); t.style.removeProperty('stroke-width'); t.removeAttribute('data-mzfs'); t.removeAttribute('data-mzpx'); t.removeAttribute('data-mzsw'); });
  }
  function apply(){
    var m=document.getElementById('map'); if(!m) return;
    if(!mobile()){ if(m.classList.contains('mz-fixed')) clear(m); return; }
    var g0=geom(m); if(!g0) return;
    var upp=g0.upp, k=g0.k, uppFull=upp/k;
    m.classList.add('mz-fixed');
    m.querySelectorAll('#g-ap .ap').forEach(function(g){
      var mk=g.querySelector('.ap-mark');
      if(mk){
        var pad=mk.querySelector('.pad');
        var wu=pad?(+pad.getAttribute('width')||16):16;
        var basePx=wu*1.4142/uppFull;                 /* diamond size at full view */
        var c=basePx<MARK_MIN_PX?MARK_MIN_PX/basePx:1;
        var s=k*c;
        mk.setAttribute('transform', Math.abs(s-1)<0.001?'':'scale('+s.toFixed(4)+')');
      }
      var hit=null;
      for(var i=0;i<g.childNodes.length;i++){ var n=g.childNodes[i]; if(n.nodeType===1&&n.classList&&n.classList.contains('ap-hit')){hit=n;break;} }
      if(!hit){
        hit=document.createElementNS(NS,'circle');
        hit.setAttribute('class','ap-hit'); hit.setAttribute('cx','0'); hit.setAttribute('cy','0');
        hit.setAttribute('fill','transparent'); hit.setAttribute('stroke','none');
        hit.setAttribute('aria-hidden','true');
        hit.style.pointerEvents='all';
        g.insertBefore(hit, g.firstChild);
      }
      hit.setAttribute('r', (HIT_PX/2*upp).toFixed(3));
    });
    m.querySelectorAll('#g-lb text.ap-label, #g-ap .ap text').forEach(function(t){
      t.setAttribute('data-mzfs','1');
      t.style.removeProperty('display');
      size(t,upp);
    });
    queueDeclutter();
  }
  /* On-screen size = the label's own full-view size (so the normal view looks the
     same), or 8px when that full-view size was too small to read. */
  function size(t,upp){
    var px=+t.getAttribute('data-mzpx')||(t.classList.contains('map-name')?NAME_PX:CODE_PX);
    var sw=t.hasAttribute('data-mzsw')?+t.getAttribute('data-mzsw'):px*0.28;
    t.style.setProperty('font-size',(px*upp).toFixed(3)+'px','important');
    t.style.setProperty('stroke-width',(sw*upp).toFixed(3)+'px','important');
  }
  function calibrate(m){
    var g0=geom(m); if(!g0||g0.k<0.999) return false;
    var changed=false;
    m.querySelectorAll('[data-mzfs]').forEach(function(t){
      if(t.hasAttribute('data-mzpx')) return;
      t.style.removeProperty('font-size'); t.style.removeProperty('stroke-width');
      var cs=getComputedStyle(t), fs=parseFloat(cs.fontSize)/g0.upp, sw=parseFloat(cs.strokeWidth)/g0.upp;
      var min=t.classList.contains('map-name')?NAME_PX:CODE_PX;
      if(fs>=6&&fs<=12){ t.setAttribute('data-mzpx',fs.toFixed(2)); if(sw>0&&sw<6) t.setAttribute('data-mzsw',sw.toFixed(2)); }
      else t.setAttribute('data-mzpx',String(min));
      size(t,g0.upp); changed=true;
    });
    return changed;
  }
  /* Fixed-size codes can be larger than before at full view: after the map's own
     label pass, hide any airport label that would still touch another label or
     another airport's mark. It comes back as soon as zoom gives it room. */
  var dq=0;
  function queueDeclutter(){
    if(dq) cancelAnimationFrame(dq);
    dq=requestAnimationFrame(function(){ dq=requestAnimationFrame(function(){ dq=requestAnimationFrame(function(){ dq=0; declutter(); }); }); });
  }
  function shown(el,m){
    var p=el; while(p&&p!==m){ if(p.nodeType===1){ var cs=getComputedStyle(p); if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0) return false; } p=p.parentNode; }
    var b=el.getBoundingClientRect(); return b.width>0&&b.height>0?b:false;
  }
  /* Keep each label's on-screen distance to its airport as in the full view:
     the map places labels in map units, so zooming in would push them away. */
  function anchorOf(t,m){
    var g=t.closest&&t.closest('.ap'); if(g) return {x:0,y:0};
    var code=t.getAttribute('data-owner')||''; if(!code) return null;
    g=m.querySelector('#g-ap .ap[data-code="'+code.replace(/"/g,'')+'"]'); if(!g) return null;
    var r=/translate\(\s*([-+\d.eE]+)\s*[,\s]\s*([-+\d.eE]+)/.exec(g.getAttribute('transform')||'');
    return r?{x:+r[1],y:+r[2]}:null;
  }
  function pull(m){
    var g0=geom(m); if(!g0) return; var f=Math.min(1,g0.k);
    m.querySelectorAll('[data-mzfs]').forEach(function(t){
      var x=t.getAttribute('x'), y=t.getAttribute('y'); if(x==null||y==null) return;
      var hx, hy;
      if(t.getAttribute('data-mzx')===x&&t.getAttribute('data-mzy')===y){ hx=+t.getAttribute('data-mzhx'); hy=+t.getAttribute('data-mzhy'); }
      else { hx=+x; hy=+y; t.setAttribute('data-mzhx',x); t.setAttribute('data-mzhy',y); }
      var a=anchorOf(t,m); if(!a) return;
      var nx=(a.x+(hx-a.x)*f).toFixed(2), ny=(a.y+(hy-a.y)*f).toFixed(2);
      t.setAttribute('x',nx); t.setAttribute('y',ny);
      t.setAttribute('data-mzx',t.getAttribute('x')); t.setAttribute('data-mzy',t.getAttribute('y'));
      t.querySelectorAll('tspan[x]').forEach(function(ts){ ts.setAttribute('x',nx); });
    });
  }
  function hitBox(a,b){ return Math.min(a.right,b.right)-Math.max(a.left,b.left)>1&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>1; }
  function declutter(){
    var m=document.getElementById('map'); if(!m||!m.classList.contains('mz-fixed')) return;
    if(calibrate(m)){ var v=window.PPC_mapView; if(v&&typeof v.refreshLabels==='function') try{ v.refreshLabels(); }catch(e){} queueDeclutter(); return; }
    pull(m);
    var mr=m.getBoundingClientRect();
    var mine=[], others=[], marks=[];
    m.querySelectorAll('text').forEach(function(t){
      var b=shown(t,m); if(!b) return;
      if(b.right<mr.left||b.left>mr.right||b.bottom<mr.top||b.top>mr.bottom) return;
      if(t.hasAttribute('data-mzfs')){
        var code=t.getAttribute('data-owner')||((t.closest&&t.closest('.ap'))||{getAttribute:function(){return ''}}).getAttribute('data-code')||'';
        var g=t.closest&&t.closest('.ap')||(code?m.querySelector('#g-ap .ap[data-code="'+code.replace(/"/g,'')+'"]'):null);
        mine.push({t:t,b:b,code:code,pri:(g&&g.classList.contains('ap-major'))?1:0});
      } else others.push(b);
    });
    m.querySelectorAll('#g-ap .ap .ap-mark').forEach(function(mk){
      var b=shown(mk,m); if(b) marks.push({b:b,code:(mk.parentNode.getAttribute('data-code')||'')});
    });
    mine.sort(function(a,b){ return b.pri-a.pri; });
    var kept=[];
    mine.forEach(function(it){
      var bad=others.some(function(o){ return hitBox(it.b,o); })
        ||kept.some(function(k){ return hitBox(it.b,k.b); })
        ||marks.some(function(k){ return k.code!==it.code&&hitBox(it.b,k.b); });
      if(bad) it.t.style.setProperty('display','none'); else kept.push(it);
    });
  }
  function bind(m){
    if(bound===m) return; bound=m;
    if(obs) obs.disconnect();
    obs=new MutationObserver(function(list){
      for(var i=0;i<list.length;i++){ if(list[i].attributeName==='viewBox'||list[i].attributeName==='style'){ apply(); return; } }
    });
    obs.observe(m,{attributes:true,attributeFilter:['viewBox']});
    apply();
    var v=window.PPC_mapView; if(v&&typeof v.refreshLabels==='function') try{ v.refreshLabels(); }catch(e){}
  }
  function find(){
    var m=document.getElementById('map');
    if(m&&m.querySelector('#g-ap .ap')){ bind(m); return true; }
    return false;
  }
  if(!find()){
    var wait=new MutationObserver(function(){ if(find()) wait.disconnect(); });
    wait.observe(document.documentElement,{childList:true,subtree:true});
    setTimeout(function(){ wait.disconnect(); },20000);
  }
  var rz=0;
  window.addEventListener('resize',function(){ clearTimeout(rz); rz=setTimeout(function(){ find(); apply(); },120); });
  if(MQ&&MQ.addEventListener) MQ.addEventListener('change',function(){ apply(); var v=window.PPC_mapView; if(v&&v.refreshLabels) try{v.refreshLabels();}catch(e){} });
})();
