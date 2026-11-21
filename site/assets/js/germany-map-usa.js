/* Germany map — USA-style Land codes, airport tags, hide clipped names. After country-map.js. */
(function(){
  var GEO=window.DE_GEO||{};
  var LAND_XY=window.PPC_DE_LAND_XY||{};
  var CODES=['SN','BY','RP','SL','SH','NI','NW','BW','BB','MV','HB','HH','HE','TH','ST','BE'];
  var CFG=window.PPC_MAP=window.PPC_MAP||{};

  function applyLandCodes(){
    document.querySelectorAll('#g-lb .lbl-lead, #g-lb line.lbl-lead').forEach(function(n){ n.remove(); });
    CODES.forEach(function(a){
      var t=document.getElementById('l-'+a);
      var g=GEO[a];
      if(!t||!g) return;
      var xy=LAND_XY[a]||g.c;
      if(!xy) return;
      t.textContent=a;
      t.setAttribute('data-abbr', a);
      if(g.name) t.setAttribute('data-full', g.name);
      t.setAttribute('x', xy[0]);
      t.setAttribute('y', xy[1]);
      t.setAttribute('text-anchor','middle');
      t.setAttribute('dominant-baseline','central');
      t.classList.remove('lbl-callout','lbl-zoom','lbl-crowd');
      t.dataset.ox=String(xy[0]);
      t.dataset.oy=String(xy[1]);
      t.dataset.ota='middle';
    });
  }

  function visible(el){
    if(!el) return false;
    var cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden'||Number(cs.opacity)===0) return false;
    if(el.classList.contains('lbl-crowd')||el.classList.contains('ct-label-crowd')||el.classList.contains('ap-code-crowd')||el.classList.contains('ct-crowd')) return false;
    var b=el.getBoundingClientRect();
    return b.width>1 && b.height>1;
  }
  function box(el){ return el.getBoundingClientRect(); }
  function hit(a,b,pad){
    pad=pad==null?1:pad;
    return a.left<b.right-pad && a.right>b.left+pad && a.top<b.bottom-pad && a.bottom>b.top+pad;
  }

  function restoreAirports(){
    var APS=window.DE_GEO_AIRPORTS||[];
    var by={};
    APS.forEach(function(ap){ by[ap.code]=ap; });
    document.querySelectorAll('#g-ap .ap').forEach(function(g){
      var code=g.getAttribute('data-code');
      var ap=by[code];
      var tx=g.querySelector('text.map-label');
      if(!ap||!tx) return;
      var x=ap.ldx||0, y=(ap.ldy==null?16:ap.ldy), ta=ap.anchor||'middle';
      tx.setAttribute('x', x);
      tx.setAttribute('y', y);
      tx.setAttribute('text-anchor', ta);
      tx.dataset.ox=String(x);
      tx.dataset.oy=String(y);
      tx.dataset.ota=ta;
      if(ap.major) tx.setAttribute('data-pin','1');
      tx.classList.remove('ap-code-crowd','lbl-crowd');
    });
  }

  function hideDuplicateCityNames(){
    var tagged={};
    document.querySelectorAll('#g-ap .ap').forEach(function(g){
      if(getComputedStyle(g).display==='none') return;
      var tx=g.querySelector('text.map-label');
      if(!visible(tx)) return;
      var m=(tx.textContent||'').split('·');
      if(m[1]) tagged[m[1].trim().toLowerCase()]=1;
    });
    document.querySelectorAll('#g-ct .ct').forEach(function(el){
      var name=((el.getAttribute('data-k')||'').split('|')[1]||'').trim();
      var tx=el.querySelector('text');
      if(!tx) return;
      if(name && tagged[name.toLowerCase()]){
        tx.classList.add('lbl-crowd','ct-label-crowd');
      } else {
        /* Keep capitals that the overlap pass may have dropped in favour of a Land code. */
        if(el.classList.contains('cap')){
          tx.classList.remove('lbl-crowd','ct-label-crowd','ct-crowd');
          el.classList.remove('ct-crowd');
        }
      }
    });
  }

  function resolveLands(){
    var m=document.querySelector('#country-map svg#map');
    if(!m) return;
    var mapBox=m.getBoundingClientRect();
    function inMap(b){
      return !(b.right<mapBox.left+2 || b.left>mapBox.right-2 || b.bottom<mapBox.top+2 || b.top>mapBox.bottom-2);
    }
    var others=[].slice.call(m.querySelectorAll('#g-ct text, #g-ap text.map-label')).filter(visible);
    var lands=[].slice.call(m.querySelectorAll('#g-lb text.lbl'));
    lands.forEach(function(t){ t.classList.remove('lbl-crowd'); });

    /* If a land still collides, try a tight ring; hide only as a last resort. */
    var u = (function(){
      var w=mapBox.width||460;
      var vb=(m.viewBox&&m.viewBox.baseVal&&m.viewBox.baseVal.width)||460;
      return vb/w;
    })();
    lands.forEach(function(t){
      var a=(t.getAttribute('data-abbr')||t.id.replace(/^l-/,''));
      var xy=LAND_XY[a]||(GEO[a]&&GEO[a].c);
      if(!xy) return;
      var slots=[{x:xy[0], y:xy[1]}];
      [10,18,26,36].forEach(function(px){
        var d=px*u;
        slots.push({x:xy[0]+d,y:xy[1]},{x:xy[0]-d,y:xy[1]},{x:xy[0],y:xy[1]+d},{x:xy[0],y:xy[1]-d},
                   {x:xy[0]+d,y:xy[1]+d},{x:xy[0]-d,y:xy[1]+d},{x:xy[0]+d,y:xy[1]-d},{x:xy[0]-d,y:xy[1]-d});
      });
      var placed=false;
      for(var i=0;i<slots.length;i++){
        t.setAttribute('x', slots[i].x);
        t.setAttribute('y', slots[i].y);
        var b=box(t);
        if(!inMap(b)) continue;
        var collide=others.some(function(o){ return hit(b, box(o), 1); });
        if(!collide){
          collide=lands.some(function(o){
            if(o===t || o.classList.contains('lbl-crowd')) return false;
            return hit(b, box(o), 1);
          });
        }
        if(!collide){
          t.dataset.ox=String(slots[i].x);
          t.dataset.oy=String(slots[i].y);
          t.classList.remove('lbl-crowd');
          placed=true;
          break;
        }
      }
      if(!placed){
        t.setAttribute('x', xy[0]);
        t.setAttribute('y', xy[1]);
        t.classList.add('lbl-crowd');
      }
    });
  }


  function dropZoomOnlyCollisions(){
    var m=document.querySelector('#country-map svg#map');
    if(!m) return;
    var aps=[].slice.call(m.querySelectorAll('#g-ap .ap')).filter(function(g){
      return getComputedStyle(g).display!=='none';
    }).map(function(g){
      var tx=g.querySelector('text.map-label');
      return {g:g, tx:tx, major:g.classList.contains('ap-major'), code:g.getAttribute('data-code')};
    }).filter(function(o){ return visible(o.tx); });
    var caps=[].slice.call(m.querySelectorAll('#g-ct .ct.cap text')).filter(visible);
    // airport vs airport: drop zoom-only when it hits a major or another tag
    aps.forEach(function(a){
      if(a.major) return;
      var ba=box(a.tx);
      var hitAp=aps.some(function(b){
        if(b===a) return false;
        return hit(ba, box(b.tx), 1);
      });
      var hitCap=caps.some(function(c){ return hit(ba, box(c), 1); });
      if(hitAp||hitCap) a.tx.classList.add('ap-code-crowd');
    });
    // remaining airport vs airport (two zoom-only): drop the later one
    var live=aps.filter(function(a){ return visible(a.tx); });
    for(var i=0;i<live.length;i++){
      for(var j=i+1;j<live.length;j++){
        if(!visible(live[i].tx)||!visible(live[j].tx)) continue;
        if(hit(box(live[i].tx), box(live[j].tx), 1)){
          var drop=live[i].major?live[j]:(live[j].major?live[i]:live[j]);
          drop.tx.classList.add('ap-code-crowd');
        }
      }
    }
  }


  function isDe(){
    try{
      var path=location.pathname||'';
      return path==='/de'||path.indexOf('/de/')===0||document.documentElement.getAttribute('data-ppc-locale')==='de';
    }catch(_){ return false; }
  }

  /* USA-style typography key: dark sample chips + plain readable labels. */
  function mountUsaStyleLegend(){
    var root=document.getElementById('country-map');
    var host=root && root.querySelector('.mapcard');
    if(!host) return;
    var de=isDe();
    var L=de
      ? {r:'Regionen', c:'Städte', k:'Hauptstadt', a:'Internationale Flughäfen', aria:'Legende der Beschriftungen'}
      : {r:'Regions', c:'Cities', k:'Capital', a:'International airports', aria:'Label colour legend'};
    var sm={r:'BY', c:de?'Nürnberg':'Nuremberg', k:'Dresden', a:'MUC'};
    var box=host.querySelector('.lbl-legend');
    if(!box){
      box=document.createElement('div');
      box.className='lbl-legend';
      box.setAttribute('role','note');
      host.appendChild(box);
    }
    box.setAttribute('aria-label', L.aria);
    box.innerHTML=
      '<span class="ll-r"><i aria-hidden="true">'+sm.r+'</i>'+L.r+'</span>'+
      '<span class="ll-c"><i aria-hidden="true">'+sm.c+'</i>'+L.c+'</span>'+
      '<span class="ll-k"><i aria-hidden="true">'+sm.k+'</i>'+L.k+'</span>'+
      '<span class="ll-a"><b aria-hidden="true">'+sm.a+'</b>'+L.a+'</span>';
  }


  function svgMidY(el){
    var m=document.querySelector('#country-map svg#map');
    if(!m||!el) return 0;
    var mb=m.getBoundingClientRect();
    var b=el.getBoundingClientRect();
    var vb=m.viewBox && m.viewBox.baseVal;
    var y0=vb?vb.y:0, h=vb?vb.height:590;
    return y0+((b.top+b.bottom)/2-mb.top)*h/mb.height;
  }
  function toneLabelsForBands(){
    var m=document.querySelector('#country-map svg#map');
    if(!m) return;
    var flag=window.PPC_DE_FLAG||{};
    var goldFrom=flag.goldFrom!=null?flag.goldFrom:388;
    var nodes=m.querySelectorAll('#g-lb text.lbl, #g-ct .ct text, #g-ap text.map-label, #g-lb text.ct-label, #g-lb text.ap-label');
    nodes.forEach(function(t){
      var cs=getComputedStyle(t);
      if(cs.display==='none'||cs.visibility==='hidden'){
        t.classList.remove('on-gold');
        return;
      }
      if(svgMidY(t)>=goldFrom) t.classList.add('on-gold');
      else t.classList.remove('on-gold');
    });
  }

  function run(){
    applyLandCodes();
    restoreAirports();
    hideDuplicateCityNames();
    resolveLands();
    dropZoomOnlyCollisions();
    toneLabelsForBands();
  }

  CFG.afterLabels=run;
  run();
  mountUsaStyleLegend();
  if(window.PPC_mapView && typeof window.PPC_mapView.refreshLabels==='function'){
    requestAnimationFrame(function(){ window.PPC_mapView.refreshLabels(); });
  }
})();
