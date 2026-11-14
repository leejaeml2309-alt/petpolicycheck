#!/usr/bin/env python3
"""Offline Australia label packer. No runtime sampling on the page.
Canberra is always visible. Other city names at rest only if they fit
with 0 overlaps; otherwise they wait for zoom. International airports only
(already filtered in france-map-geo.js).

Slots are screen-scaled: s = (975 / svgWidth) * k  (map units per CSS pixel).
London never falls back onto an icon/dot. Newly visible zoom-only icons can
nudge a locked label to another free slot. Multi-word region names wrap, or
are hidden if they still cross a regional border.
"""
from __future__ import annotations
import json, time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path('/workspace/au-map-20261114')
SITE = ROOT / 'site'
CHROME = '/usr/bin/google-chrome'
BASE = 'http://127.0.0.1:8846'
OUT = [
    SITE / 'assets/js/australia-map-labels.js',
    ROOT / 'static/assets/js/australia-map-labels.js',
]
K_TIERS = [1.0, 0.625, 0.40, 0.25]
VIEWS = [
    {'name': 'desk', 'w': 1280, 'h': 900, 'mobile': False},
    {'name': 'phone', 'w': 390, 'h': 844, 'mobile': True},
]
CITY_NAMES = {'Canberra', 'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Gold Coast', 'Hobart', 'Darwin', 'Cairns', 'Newcastle', 'Wollongong', 'Geelong', 'Townsville', 'Toowoomba', 'Ballarat', 'Bendigo', 'Launceston', 'Alice Springs', 'Sunshine Coast'}
CITY_ZOOM_ONLY = {'Newcastle', 'Wollongong', 'Geelong', 'Townsville', 'Toowoomba', 'Ballarat', 'Bendigo', 'Launceston', 'Alice Springs', 'Sunshine Coast'}
CITY_REST_FIRST = {'Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Gold Coast', 'Hobart', 'Darwin', 'Cairns'}
CITY_REST_LAST = set()
ZOOM_ONLY = set()
MAJOR_AP = {'SYD', 'MEL', 'BNE', 'PER', 'ADL', 'CNS', 'OOL'}
LINK_CITY = {'SYD':'Sydney','MEL':'Melbourne','BNE':'Brisbane','PER':'Perth','ADL':'Adelaide','CNS':'Cairns','OOL':'Gold Coast'}
CAPITAL = 'Canberra'
GEO_NAME = 'AU_GEO'
HIDE_REGIONS_AT_REST = False
GROUP_MEMBERS = {}
WRAP_NAMES = {
    'New South Wales': ['New South', 'Wales'],
    'Western Australia': ['Western', 'Australia'],
    'South Australia': ['South', 'Australia'],
    'Northern Territory': ['Northern', 'Territory'],
    'Australian Capital Territory': ['Australian', 'Capital', 'Territory'],
}

PACK_JS = r"""(opts) => {
  const ZOOM_ONLY = new Set(opts.zoomOnly);
  const MAJOR_AP = new Set(opts.majorAp);
  const CITY_NAMES = new Set(opts.cityNames);
  const CITY_ZOOM_ONLY = new Set(opts.cityZoomOnly || []);
  const CITY_REST_FIRST = new Set(opts.cityRestFirst || []);
  const CITY_REST_LAST = new Set(opts.cityRestLast || []);
  const LINK_CITY = Object.assign({}, opts.linkCity || {});
  const CAPITAL = opts.capital;
  const k = opts.k;
  const lock = opts.lock || [];

  const WRAP = Object.assign({}, opts.wrap || {});

  const m = document.getElementById('map');
  if (!m) return {error:'no map'};
  const HIDE = ['lbl-crowd','ct-label-crowd','ap-code-crowd','ap-name-crowd','ct-crowd','ap-crowd','ppc-lbl-hide'];
  function show(el){
    el.classList.remove(...HIDE);
    el.style.removeProperty('display');
    const g = el.closest('.ct,.ap');
    if (g) g.classList.remove('ct-crowd','ap-crowd','ap-code-crowd');
  }
  let accepted = [];
  function hide(el, typ){
    const cls = typ==='airport' ? 'ap-code-crowd' : typ==='region' ? 'lbl-crowd' : typ==='ap-name' ? 'ap-name-crowd' : 'ct-label-crowd';
    el.classList.add(cls, 'ppc-lbl-hide');
    for(let i=accepted.length-1;i>=0;i--){
      if(accepted[i].el===el) accepted.splice(i,1);
    }
  }
  function typOf(el){
    if (el.classList.contains('lbl-group') || (el.dataset && el.dataset.group)) return 'group';
    if (el.classList.contains('map-name')) return 'ap-name';
    if (el.classList.contains('is-cap') || (el.dataset && el.dataset.kind==='capital') || (el.closest && el.closest('.ct.cap'))) return 'capital';
    if (el.classList.contains('ap-label') || (el.dataset && el.dataset.kind==='airport') || (el.closest && el.closest('.ap'))) return el.classList.contains('map-name')?'ap-name':'airport';
    if (el.classList.contains('ct-label') || (el.dataset && el.dataset.kind==='city') || (el.closest && el.closest('.ct'))) return el.classList.contains('is-cap')?'capital':'city';
    if (el.classList.contains('lbl')) return 'region';
    return 'region';
  }
  function ov(a,b,pad){
    pad = pad==null ? 1.5 : pad;
    return !(a.x+a.w+pad<=b.x || b.x+b.w+pad<=a.x || a.y+a.h+pad<=b.y || b.y+b.h+pad<=a.y);
  }
  function boxOf(el){
    const r = el.getBoundingClientRect();
    return {x:r.x, y:r.y, w:r.width, h:r.height};
  }
  function mapToScreen(mx, my){
    const vb = m.viewBox.baseVal;
    const br = m.getBoundingClientRect();
    return {x: br.x + (mx - vb.x) * br.width / vb.width,
            y: br.y + (my - vb.y) * br.height / vb.height};
  }
  function slotScale(){
    const br = m.getBoundingClientRect();
    const vb = m.viewBox.baseVal;
    return vb.width / Math.max(1, br.width);
  }
  const s = slotScale();

  m.querySelectorAll('text, .ct, .ap, line.lbl-lead').forEach(el => {
    el.classList.remove(...HIDE);
    el.style.removeProperty('display');
  });
  m.querySelectorAll('text[data-x0]').forEach(el => {
    el.setAttribute('x', el.getAttribute('data-x0'));
    el.setAttribute('y', el.getAttribute('data-y0'));
  });

  function unwrap(el){
    const ts=[...el.querySelectorAll('tspan')];
    if(!ts.length) return;
    const full = el.getAttribute('data-full') || ts.map(t=>(t.textContent||'').trim()).filter(Boolean).join(' ');
    while(el.firstChild) el.removeChild(el.firstChild);
    el.textContent = full;
    el.removeAttribute('data-wrapped');
  }
  function applyWrap(el, lines){
    if(!lines || !lines.length) return;
    if(!el.getAttribute('data-full')){
      const cur=(el.textContent||'').replace(/\s+/g,' ').trim();
      if(cur) el.setAttribute('data-full', cur);
    }
    const ns=el.namespaceURI;
    const x=el.getAttribute('x')||0;
    while(el.firstChild) el.removeChild(el.firstChild);
    lines.forEach((text,i)=>{
      const ts=document.createElementNS(ns,'tspan');
      ts.setAttribute('x', x);
      ts.setAttribute('dy', i===0 ? '0' : '1.05em');
      ts.textContent=text;
      el.appendChild(ts);
    });
    el.setAttribute('data-wrapped', '1');
  }
  function syncTspans(el){
    const x=el.getAttribute('x')||0;
    el.querySelectorAll('tspan').forEach(ts=>ts.setAttribute('x', x));
  }

  const obstacles = [];
  m.querySelectorAll('#g-ct .ct circle:not(.ring)').forEach(c => {
    const r=c.getBoundingClientRect();
    if(r.width<1) return;
    const nm=(c.closest('.ct') && (c.closest('.ct').getAttribute('aria-label')||'').split(',')[0]) || '';
    obstacles.push({x:r.x-1, y:r.y-1, w:r.width+2, h:r.height+2, kind:'dot', name:nm});
  });
  m.querySelectorAll('#g-ct .ct.cap .ring').forEach(c => {
    const r=c.getBoundingClientRect();
    if(r.width<1) return;
    const nm=(c.closest('.ct') && (c.closest('.ct').getAttribute('aria-label')||'').split(',')[0]) || '';
    obstacles.push({x:r.x-1, y:r.y-1, w:r.width+2, h:r.height+2, kind:'ring', name:nm});
  });
  m.querySelectorAll('#g-ap .ap .ap-mark').forEach(mk => {
    const g=mk.closest('.ap');
    if(!g) return;
    const cs=getComputedStyle(g);
    if(cs.display==='none' || cs.visibility==='hidden') return;
    const r=mk.getBoundingClientRect();
    if(r.width<1 || r.height<1) return;
    obstacles.push({x:r.x-1, y:r.y-1, w:r.width+2, h:r.height+2, kind:'icon', name:g.getAttribute('data-code')});
  });
  m.querySelectorAll('line.lbl-lead').forEach(l => {
    if(getComputedStyle(l).display==='none') return;
    const x1=+l.getAttribute('x1'), y1=+l.getAttribute('y1'), x2=+l.getAttribute('x2'), y2=+l.getAttribute('y2');
    const a=mapToScreen(Math.min(x1,x2), Math.min(y1,y2)-2.5);
    const b=mapToScreen(Math.max(x1,x2), Math.max(y1,y2)+2.5);
    obstacles.push({x:a.x, y:a.y, w:Math.max(1,b.x-a.x), h:Math.max(1,b.y-a.y), kind:'lead', name:l.getAttribute('data-a')||'lead'});
  });
  document.querySelectorAll('#zin,#zout,#zreset,div.zoom').forEach(el => {
    const r=el.getBoundingClientRect();
    if(r.width>0) obstacles.push({x:r.x-2, y:r.y-2, w:r.width+4, h:r.height+4, kind:'ui', name:el.id||'zoom'});
  });

  const texts = [...m.querySelectorAll('#g-lb text, #g-ct .ct text, #g-ap .ap text')]
    .filter(el => (el.textContent||'').trim());
  texts.forEach(unwrap);

  function recOf(el){
    const typ=typOf(el);
    const name=(el.getAttribute('data-full')||el.textContent||'').replace(/\s+/g,' ').trim();
    const g=el.closest('.ct,.ap') || (el.dataset && el.dataset.owner && document.querySelector('#g-ct .ct[data-k="'+el.dataset.owner+'"], #g-ap .ap[data-code="'+el.dataset.owner+'"]'));
    const code=(g && g.getAttribute('data-code')) || (el.dataset && el.dataset.owner) || null;
    const isCapCity = name===CAPITAL && (typ==='city'||typ==='capital');
    const isMustCity = isCapCity || ((typ==='city'||typ==='capital') && CITY_REST_FIRST.has(name));
    let pri=6;
    if(typ==='ap-name') pri=9;
    else if(isCapCity) pri=0;
    else if((typ==='city'||typ==='capital') && CITY_REST_FIRST.has(name)) pri=1;
    else if(typ==='airport' && MAJOR_AP.has(name||code)) pri=2;
    else if(typ==='group') pri=3;
    else if((typ==='city'||typ==='capital') && CITY_NAMES.has(name) && !CITY_REST_LAST.has(name)) pri=4;
    else if((typ==='city'||typ==='capital') && CITY_REST_LAST.has(name)) pri=6;
    else if(typ==='airport') pri=5;
    else if(typ==='region') pri=5;
    const key=(typ==='airport'||typ==='ap-name'?(code||name):name)+'::'+typ;
    return {el, typ, name, code, isCapCity, isMustCity, pri, key, id:el.id||null, sel:el.id?('#'+el.id):null};
  }

  const recs = texts.map(recOf);

  recs.forEach(r => {
    if(r.typ==='ap-name'){ hide(r.el,'ap-name'); r.hide=true; r.hideClass='ap-name-crowd'; }
    else if(r.typ==='airport' && ZOOM_ONLY.has(r.code||r.name) && k>=0.999){ hide(r.el,'airport'); r.hide=true; r.hideClass='ap-code-crowd'; }
    else if((r.typ==='city'||r.typ==='capital') && !r.isCapCity && CITY_ZOOM_ONLY.has(r.name) && k>=0.999){ hide(r.el,'city'); r.hide=true; r.hideClass='ct-label-crowd'; }
    else if(r.typ==='group' && k<0.999){ hide(r.el,'region'); r.hide=true; r.hideClass='lbl-crowd'; }
    else if(r.typ==='region' && opts.hideRegionsAtRest && k>=0.999){ hide(r.el,'region'); r.hide=true; r.hideClass='lbl-crowd'; }
    else { r.hide=false; }
  });

  recs.forEach(r => {
    if(((r.typ==='region'||r.typ==='group')||r.typ==='group') && WRAP[r.name]){
      applyWrap(r.el, WRAP[r.name]);
      r.wrap = WRAP[r.name].map((text,i)=>({text, dy: i? '1.05em':'0'}));
    }
  });

  function citySlots(mx, my, isCapCity, name){
    const slots=[];
    if(isCapCity){
      /* Capital only: stay visibly next to Rome's red dot. Max 15 CSS px. */
      const gaps=[6,9,12,15];
      for(const g0 of gaps){
        const g=g0*s;
        slots.push(
          [mx+g, my-3*s, 'start'],
          [mx+g, my+8*s, 'start'],
          [mx+g, my-g, 'start'],
          [mx+g, my+g, 'start'],
          [mx-g, my-3*s, 'end'],
          [mx-g, my+8*s, 'end'],
          [mx-g, my-g, 'end'],
          [mx-g, my+g, 'end'],
          [mx, my-g, 'middle'],
          [mx, my+g, 'middle'],
          [mx+0.7*g, my-0.75*g, 'start'],
          [mx-0.7*g, my-0.75*g, 'end'],
          [mx+0.7*g, my+0.75*g, 'start'],
          [mx-0.7*g, my+0.75*g, 'end']
        );
      }
      return slots;
    }
    /* Osaka west/south, Kyoto east/north so both fit at 390 rest. */
    if(name==='Osaka' || name==='Kyoto'){
      const west = name==='Osaka';
      for(const g0 of [6,9,13,16]){
        const g=g0*s, dy=3*s, up=6*s, dn=8*s;
        if(west){
          slots.push(
            [mx-g, my+dy, 'end'],
            [mx-g, my+dn, 'end'],
            [mx-g, my-up, 'end'],
            [mx, my+(dn+1*s), 'middle'],
            [mx+g, my+dn, 'start'],
            [mx+g, my+dy, 'start']
          );
        } else {
          slots.push(
            [mx+g, my-up, 'start'],
            [mx+g, my+dy, 'start'],
            [mx, my-(up+2*s), 'middle'],
            [mx+g, my+dn, 'start'],
            [mx-g, my-up, 'end'],
            [mx-g, my+dy, 'end']
          );
        }
      }
      return slots;
    }
    /* Other cities/airports: tight beside the marker only. Max 13 CSS px. Never 22/30. */
    for(const g0 of [6,9,13]){
      const g=g0*s, dy=3*s, up=6*s, dn=8*s;
      slots.push(
        [mx+g, my+dy, 'start'],
        [mx-g, my+dy, 'end'],
        [mx+g, my-up, 'start'],
        [mx-g, my-up, 'end'],
        [mx+g, my+dn, 'start'],
        [mx-g, my+dn, 'end'],
        [mx, my-(up+2*s), 'middle'],
        [mx, my+(dn+1*s), 'middle']
      );
    }
    return slots;
  }
  function apSlots(mx, my){
    const slots=[];
    mx = mx||0; my = my||0;
    for(const g0 of [6,9,13]){
      const g=g0*s;
      slots.push(
        [mx+g, my+3*s, 'start'],
        [mx-g, my+3*s, 'end'],
        [mx, my-g, 'middle'],
        [mx, my+g, 'middle'],
        [mx+g, my-0.75*g, 'start'],
        [mx-g, my-0.75*g, 'end'],
        [mx+g, my+0.75*g, 'start'],
        [mx-g, my+0.75*g, 'end']
      );
    }
    return slots;
  }

  function ownerGroup(r){
    return r.el.closest('.ct,.ap') || (r.code && document.querySelector('#g-ap .ap[data-code="'+r.code+'"]')) || (r.el.dataset && r.el.dataset.owner && document.querySelector('#g-ct .ct[data-k="'+r.el.dataset.owner+'"], #g-ap .ap[data-code="'+r.el.dataset.owner+'"]'));
  }
  function ownerXY(r){
    if(r.typ==='city'||r.typ==='capital'){
      const g=ownerGroup(r);
      const c=g && g.querySelector('circle:not(.ring)');
      if(c) return {x:+c.getAttribute('cx'), y:+c.getAttribute('cy')};
    }
    if(r.typ==='airport'){
      const g=ownerGroup(r);
      if(g){
        const tr=g.getAttribute('transform')||'';
        const m=/translate\(\s*([-+\d.eE]+)\s*[,\s]\s*([-+\d.eE]+)/.exec(tr);
        if(m) return {x:+m[1], y:+m[2]};
      }
    }
    return null;
  }

  accepted = obstacles.map(o => ({...o}));
  const lockMap = new Map(lock.map(L => [L.key, L]));

  function isOwnMarker(a, r){
    if(!a || !r) return false;
    if((r.typ==='city'||r.typ==='capital') && a.kind==='dot' && a.name===r.name) return true;
    if(r.typ==='airport' && a.kind==='icon' && a.name===r.code) return true;
    if(r.typ==='airport' && (a.kind==='dot'||a.kind==='ring') && a.name && LINK_CITY[r.code]===a.name) return true;
    if((r.typ==='city'||r.typ==='capital') && a.kind==='icon' && LINK_CITY[a.name]===r.name) return true;
    if((r.typ==='region'||r.typ==='group') && a.kind==='lead' && r.id && r.id==='l-'+a.name) return true;
    return false;
  }
  function pointIn(px,py,box){
    return px>=box.x && py>=box.y && px<=box.x+box.w && py<=box.y+box.h;
  }
  function segHitsBox(x1,y1,x2,y2,box){
    if(pointIn(x1,y1,box)||pointIn(x2,y2,box)) return true;
    function hit(ax,ay,bx,by,cx,cy,dx,dy){
      const den=(bx-ax)*(dy-cy)-(by-ay)*(dx-cx);
      if(Math.abs(den)<1e-8) return false;
      const u=((cx-ax)*(dy-cy)-(cy-ay)*(dx-cx))/den;
      const v=((cx-ax)*(by-ay)-(cy-ay)*(bx-ax))/den;
      return u>=0 && u<=1 && v>=0 && v<=1;
    }
    const x3=box.x, y3=box.y, x4=box.x+box.w, y4=box.y+box.h;
    return hit(x1,y1,x2,y2,x3,y3,x4,y3)||hit(x1,y1,x2,y2,x3,y4,x4,y4)||hit(x1,y1,x2,y2,x3,y3,x3,y4)||hit(x1,y1,x2,y2,x4,y3,x4,y4);
  }
  const apLinks=[...m.querySelectorAll('#g-ap-link line.ap-link, #g-ap line.ap-link')].filter(l=>getComputedStyle(l).display!=='none');
  function shrinkSeg(a,c, inset){
    const dx=c.x-a.x, dy=c.y-a.y;
    const len=Math.hypot(dx,dy);
    if(len < inset*2+1) return null;
    const ux=dx/len, uy=dy/len;
    return {x1:a.x+ux*inset, y1:a.y+uy*inset, x2:c.x-ux*inset, y2:c.y-uy*inset};
  }
  function linkHits(box, pad, r){
    pad = pad==null ? 1.5 : pad;
    const b={x:box.x-pad,y:box.y-pad,w:box.w+2*pad,h:box.h+2*pad};
    for(const l of apLinks){
      if(l.classList.contains('ppc-lbl-hide')) continue;
      const code=l.getAttribute('data-code');
      /* Own airport label is at the endpoint; ignore that link. */
      if(r && r.typ==='airport' && r.code && r.code===code) continue;
      const a=mapToScreen(+l.getAttribute('x1'), +l.getAttribute('y1'));
      const c=mapToScreen(+l.getAttribute('x2'), +l.getAttribute('y2'));
      const seg=shrinkSeg(a,c, 8);
      if(!seg) continue; /* very short (FUK/OKA); endpoints only */
      if(segHitsBox(seg.x1,seg.y1,seg.x2,seg.y2,b)) return l;
    }
    return null;
  }
  function collisionOf(box, r, kinds){
    for(const a of accepted){
      if(r && a.el===r.el) continue;
      if(isOwnMarker(a, r)) continue;
      if(kinds && kinds.length && kinds.indexOf(a.kind)<0) continue;
      if(ov(box,a)) return a;
    }
    return null;
  }
  function collides(box, r, kinds){ return !!collisionOf(box, r, kinds); }

  function applySlot(el, x, y, anchor){
    el.setAttribute('x', x);
    el.setAttribute('y', y);
    if(anchor) el.setAttribute('text-anchor', anchor);
    syncTspans(el);
    show(el);
  }

  function elNum(el,a){ const v=el.getAttribute(a); return v==null?null:+v; }

  function slotsFor(r){
    if(r.typ==='city'||r.typ==='capital'){
      const o=ownerXY(r);
      if(!o) return null;
      return citySlots(o.x, o.y, r.isCapCity, r.name);
    }
    if(r.typ==='airport'){
      const o=ownerXY(r);
      if(!o) return null;
      return apSlots(o.x, o.y);
    }
    const x=elNum(r.el,'x'), y=elNum(r.el,'y'), anc=r.el.getAttribute('text-anchor')||'middle';
    const nlines = (r.wrap && r.wrap.length) || 1;
    const wrapDy = nlines>1 ? -0.5*(nlines-1)*8*s*1.05 : 0;
    const path0 = regionPath(r);
    const pathArr = !path0 ? [] : (Array.isArray(path0) ? path0 : [path0]);
    const rid = r.id && r.id.startsWith('l-') ? r.id.slice(2) : r.id;
    const geoC = (window[opts.geoName] && rid && window[opts.geoName][rid] && window[opts.geoName][rid].c) || null;
    const centers=[];
    try{
      let minX=Infinity, minY=Infinity, maxX=-Infinity, maxY=-Infinity, any=false;
      for(const pth of pathArr){
        if(!pth || typeof pth.getBBox!=='function') continue;
        const bb=pth.getBBox();
        if(bb && bb.width>0 && bb.height>0){
          any=true;
          minX=Math.min(minX,bb.x); minY=Math.min(minY,bb.y);
          maxX=Math.max(maxX,bb.x+bb.width); maxY=Math.max(maxY,bb.y+bb.height);
          centers.push([bb.x+bb.width/2, bb.y+bb.height/2]);
        }
      }
      if(any) centers.push([(minX+maxX)/2, (minY+maxY)/2]);
    }catch(e){}
    if(geoC && geoC.length>=2) centers.push([+geoC[0], +geoC[1]]);
    if(x!=null && y!=null) centers.push([x, y]);
    /* Map-unit offsets (not CSS-scaled) so narrow phone views still find in-polygon pockets. */
    const offs=[0];
    for(const step of [4,8,12,16,20,24,28,32,40,48]){ offs.push(-step, step); }
    const slots=[];
    const seen=new Set();
    for(const [cx,cy] of centers){
      for(const dx of offs){
        for(const dy of offs){
          const sx=cx+dx, sy=cy+dy+wrapDy;
          const key=sx.toFixed(2)+','+sy.toFixed(2)+',middle';
          if(seen.has(key)) continue;
          seen.add(key);
          slots.push([sx, sy, 'middle']);
        }
      }
    }
    return slots.length ? slots : [[x, y+wrapDy, anc]];
  }

  function regionPath(r){
    if(r.typ==='group'){
      const ids=(opts.groupMembers && opts.groupMembers[r.name]) || [];
      const paths=ids.map(id => m.querySelector('#s-'+id)).filter(Boolean);
      return paths.length ? paths : null;
    }
    if(r.typ!=='region' || !r.id) return null;
    const id=r.id.startsWith('l-') ? r.id.slice(2) : r.id;
    const p=m.querySelector('#s-'+id);
    return p ? [p] : null;
  }
  function boxInRegion(box, pathOrPaths){
    const paths = !pathOrPaths ? [] : (Array.isArray(pathOrPaths) ? pathOrPaths : [pathOrPaths]);
    if(!paths.length) return false;
    const inset=1.5; /* 1.5 CSS px, all 9 points strictly inside */
    if(box.w<=2*inset || box.h<=2*inset) return false;
    const pts=[
      [box.x+box.w/2, box.y+box.h/2],
      [box.x+inset, box.y+inset],
      [box.x+box.w-inset, box.y+inset],
      [box.x+inset, box.y+box.h-inset],
      [box.x+box.w-inset, box.y+box.h-inset],
      [box.x+box.w/2, box.y+inset],
      [box.x+box.w/2, box.y+box.h-inset],
      [box.x+inset, box.y+box.h/2],
      [box.x+box.w-inset, box.y+box.h/2]
    ];
    let inside=0;
    for(const [sx,sy] of pts){
      let ok=false;
      for(const path of paths){
        if(!path || typeof path.isPointInFill!=='function') continue;
        const ctm=path.getScreenCTM();
        if(!ctm) continue;
        const inv=ctm.inverse();
        const p=new DOMPoint(sx,sy).matrixTransform(inv);
        try{ if(path.isPointInFill(p)){ ok=true; break; } }catch(e){}
      }
      if(ok) inside++;
    }
    return inside === 9;
  }

  function tryPlace(r, slots, allowEvict, requireRegion){
    const path = requireRegion ? regionPath(r) : null;
    for(const [x,y,anc] of slots){
      applySlot(r.el, x, y, anc);
      const box=boxOf(r.el);
      if(box.w<1 || box.h<1) continue;
      if(collides(box, r)) continue;
      if(r.typ!=='region' && r.typ!=='group' && linkHits(box, null, r)) continue;
      if(path && !boxInRegion(box, path)) continue;
      r.x=x; r.y=y; r.anchor=anc; r.box=box; r.hide=false;
      accepted.push({...box, kind:'label', el:r.el, typ:r.typ, name:r.name, rec:r});
      return 'ok';
    }
    if(allowEvict && (r.isCapCity||r.isMustCity)){
      for(const [x,y,anc] of slots){
        applySlot(r.el, x, y, anc);
        const box=boxOf(r.el);
        if(box.w<1 || box.h<1) continue;
        if(collides(box, r, ['dot','ring','icon','lead','ui'])) continue;
        if(path && !boxInRegion(box, path)) continue;
        for(let i=accepted.length-1;i>=0;i--){
          const a=accepted[i];
          if(a.kind==='label' && a.el!==r.el && ov(box,a)){
            if(a.rec && (a.rec.isCapCity || a.rec.isMustCity)) continue;
            hide(a.el, a.typ);
            if(a.rec) a.rec.hide=true;
            accepted.splice(i,1);
          }
        }
        r.x=x; r.y=y; r.anchor=anc; r.box=box; r.hide=false;
        accepted.push({...box, kind:'label', el:r.el, typ:r.typ, name:r.name, rec:r});
        return 'evict';
      }
    }
    return 'fail';
  }

  function markerScreen(r){
    const o=ownerXY(r);
    if(!o) return null;
    return mapToScreen(o.x, o.y);
  }
  function boxGap(pt, box){
    if(!pt || !box) return 999;
    const cx=Math.max(box.x, Math.min(pt.x, box.x+box.w));
    const cy=Math.max(box.y, Math.min(pt.y, box.y+box.h));
    return Math.hypot(pt.x-cx, pt.y-cy);
  }
  function lockStillTight(r, L){
    if(L.x==null || L.y==null) return false;
    if(!(r.typ==='city'||r.typ==='capital'||r.typ==='airport')) return true;
    applySlot(r.el, L.x, L.y, L.anchor||'start');
    return boxGap(markerScreen(r), boxOf(r.el)) <= 16;
  }

  recs.sort((a,b)=>a.pri-b.pri || a.name.localeCompare(b.name));
  const lockedOk = [];

  for(const r of recs){
    if(r.hide) continue;
    const L = lockMap.get(r.key);
    if(!L) continue;
    const slots = slotsFor(r) || [];
    const preferred = [];
    if(L.x!=null && L.y!=null && lockStillTight(r, L)){
      preferred.push([L.x, L.y, L.anchor||'start']);
    }
    for(const sl of slots){
      if(!preferred.some(p=>p[0]===sl[0] && p[1]===sl[1] && p[2]===sl[2])) preferred.push(sl);
    }
    const res = tryPlace(r, preferred, !!(r.isCapCity||r.isMustCity), (r.typ==='region'||r.typ==='group'));
    if(res==='ok' || res==='evict'){
      lockedOk.push(r.key);
    }
  }

  for(const r of recs){
    if(r.hide) continue;
    if(lockedOk.includes(r.key)) continue;
    const slots = slotsFor(r);
    if(!slots){ hide(r.el,r.typ); r.hide=true; continue; }
    const res = tryPlace(r, slots, !!(r.isCapCity||r.isMustCity), (r.typ==='region'||r.typ==='group'));
    if(res==='fail'){
      if(r.isCapCity || r.isMustCity){
        const extra = r.isCapCity ? citySlots((ownerXY(r)||{}).x||0, (ownerXY(r)||{}).y||0, true) : slots;
        const res2 = tryPlace(r, extra, true, false);
        if(res2==='fail'){
          const o=ownerXY(r);
          const fb=o ? [o.x, o.y-15*s, 'middle'] : slots[0];
          applySlot(r.el, fb[0], fb[1], fb[2]);
          const box=boxOf(r.el);
          if(!collides(box, r, ['dot','ring','icon'])){
            for(let i=accepted.length-1;i>=0;i--){
              const a=accepted[i];
              if(a.kind==='label' && a.el!==r.el && ov(box,a)){
                hide(a.el, a.typ);
                if(a.rec) a.rec.hide=true;
                accepted.splice(i,1);
              }
            }
            r.x=fb[0]; r.y=fb[1]; r.anchor=fb[2]; r.box=box; r.hide=false;
            accepted.push({...box, kind:'label', el:r.el, typ:r.typ, name:r.name, rec:r});
          } else {
            hide(r.el, r.typ);
            r.hide=true;
          }
        }
      } else {
        hide(r.el, r.typ);
        r.hide=true;
        r.hideClass = r.typ==='airport'?'ap-code-crowd': (r.typ==='region'||r.typ==='group')?'lbl-crowd':'ct-label-crowd';
        r.x=elNum(r.el,'x'); r.y=elNum(r.el,'y'); r.anchor=r.el.getAttribute('text-anchor')||'start';
      }
    }
  }

  m.querySelectorAll('line.lbl-lead').forEach(l => {
    l.classList.add('lbl-crowd','ppc-lbl-hide');
  });
  recs.forEach(r => {
    if((r.typ==='region'||r.typ==='group')){
      r.leadHidden=true;
      if(r.id && r.id.startsWith('l-')){
        const lead=m.querySelector('#g-lb line.lbl-lead[data-a="'+r.id.slice(2)+'"]');
        if(lead) lead.classList.add('lbl-crowd','ppc-lbl-hide');
      }
    }
  });

  recs.forEach(r => {
    if(r.hide || r.typ==='ap-name' || (r.typ==='region'||r.typ==='group')) return;
    if(!(r.typ==='city'||r.typ==='capital'||r.typ==='airport')) return;
    const pt=markerScreen(r);
    const box=boxOf(r.el);
    const gap=boxGap(pt, box);
    r.gap=+gap.toFixed(1);
    const maxGap = r.isCapCity ? 16 : 16;
    if(gap>maxGap){
      if(r.isCapCity) return; /* keep Rome; slots already cap at 15 */
      hide(r.el, r.typ);
      r.hide=true;
      r.hideClass = r.typ==='airport'?'ap-code-crowd':'ct-label-crowd';
    }
  });

  function relocate(rec, extraObstacles){
    const slots = slotsFor(rec) || [];
    const prevX=rec.x, prevY=rec.y, prevA=rec.anchor;
    for(const [x,y,anc] of slots){
      applySlot(rec.el, x, y, anc);
      const box=boxOf(rec.el);
      if(box.w<1 || box.h<1) continue;
      if(extraObstacles && extraObstacles.some(o=>ov(box,o,0.25))) continue;
      if(collides(box, rec)) continue;
      if(rec.typ!=='region' && rec.typ!=='group' && linkHits(box, null, rec)) continue;
      rec.x=x; rec.y=y; rec.anchor=anc; rec.box=box; rec.hide=false;
      hide(rec.el, rec.typ); /* drop old accepted only; show next */
      show(rec.el);
      rec.hide=false;
      accepted.push({...box, kind:'label', el:rec.el, typ:rec.typ, name:rec.name, rec:rec});
      return true;
    }
    if(prevX!=null) applySlot(rec.el, prevX, prevY, prevA||'start');
    return false;
  }

  const AP_RANK = {NRT: 0, HND: 1, KIX: 2, NGO: 3, FUK: 4, CTS: 5, OKA: 6};
  const iconState = [];
  m.querySelectorAll('#g-ap .ap').forEach(g => {
    const code=g.getAttribute('data-code');
    const mk=g.querySelector('.ap-mark')||g;
    const cssHidden = (g.classList.contains('ap-zoomonly') && k>=0.999) || getComputedStyle(g).display==='none';
    iconState.push({g, code, rank: (AP_RANK[code]==null?25:AP_RANK[code]), hide: cssHidden});
  });
  iconState.sort((a,b)=>a.rank-b.rank || (a.code||'').localeCompare(b.code||''));
  const keptIcons = [];
  function iconBoxOf(g){
    const mk=g.querySelector('.ap-mark')||g;
    const r=mk.getBoundingClientRect();
    return {x:r.x-0.5, y:r.y-0.5, w:r.width+1, h:r.height+1};
  }
  for(const ic of iconState){
    if(ic.hide){
      ic.g.classList.add('ppc-lbl-hide');
      const link=m.querySelector('#g-ap-link line.ap-link[data-code="'+ic.code+'"], #g-ap line.ap-link[data-code="'+ic.code+'"]');
      if(link) link.classList.add('ppc-lbl-hide');
      recs.forEach(r => {
        if((r.typ==='airport'||r.typ==='ap-name') && r.code===ic.code && !r.hide){
          hide(r.el, r.typ);
          r.hide=true;
        }
      });
      continue;
    }
    ic.g.classList.remove('ppc-lbl-hide');
    const box=iconBoxOf(ic.g);
    if(box.w<1 || box.h<1){ ic.hide=true; continue; }
    let hit=null;
    for(const a of obstacles){
      if(a.kind==='icon' && a.name===ic.code) continue;
      if(a.kind==='icon' && keptIcons.some(k=>k.code===a.name && !k.hide)===false && a.name!==ic.code){
        /* skip icons already marked hidden */
      }
      if((a.kind==='dot'||a.kind==='ring'||a.kind==='icon'||a.kind==='label') && ov(box,a,0.25)){
        if(a.kind==='icon' && a.name===ic.code) continue;
        if((a.kind==='dot'||a.kind==='ring') && LINK_CITY[ic.code] && a.name===LINK_CITY[ic.code]) continue;
        const alreadyHidden = a.kind==='icon' && iconState.some(s=>s.code===a.name && s.hide);
        if(alreadyHidden) continue;
        const notYetKept = a.kind==='icon' && !keptIcons.some(k=>k.code===a.name);
        if(notYetKept && a.kind==='icon') continue;
        hit=a; break;
      }
    }
    if(!hit){
      for(const kr of recs){
        if(kr.hide || kr.typ==='ap-name') continue;
        if(kr.typ==='airport' && kr.code===ic.code) continue;
        const lb=boxOf(kr.el);
        if(lb.w>=1 && ov(box,lb,0.25)){ hit={kind:'label', name:kr.name, rec:kr, el:kr.el}; break; }
      }
    }
    if(hit && hit.kind==='label' && hit.rec && relocate(hit.rec, [box])){
      hit=null;
    }
    if(hit && MAJOR_AP.has(ic.code) && hit.kind==='label' && hit.rec && !hit.rec.isCapCity && !hit.rec.isMustCity && LINK_CITY[ic.code]!==hit.rec.name && !CITY_NAMES.has(hit.rec.name)){
      hide(hit.el, hit.typ||hit.rec.typ);
      hit.rec.hide=true;
      const ix=accepted.findIndex(a=>a.el===hit.el);
      if(ix>=0) accepted.splice(ix,1);
      hit=null;
    }
    if(hit){
      ic.hide=true;
      ic.g.classList.add('ppc-lbl-hide');
      const link=m.querySelector('#g-ap-link line.ap-link[data-code="'+ic.code+'"], #g-ap line.ap-link[data-code="'+ic.code+'"]');
      if(link) link.classList.add('ppc-lbl-hide');
      recs.forEach(r => {
        if((r.typ==='airport'||r.typ==='ap-name') && r.code===ic.code && !r.hide){
          hide(r.el, r.typ);
          r.hide=true;
        }
      });
    } else {
      keptIcons.push(ic);
      const box2=iconBoxOf(ic.g);
      obstacles.push({...box2, kind:'icon', name:ic.code});
    }
  }

  function audit(){
    const vis=recs.filter(r=>!r.hide && r.typ!=='ap-name');
    const overlaps=[];
    for(let i=0;i<vis.length;i++){
      const A=boxOf(vis[i].el);
      for(let j=i+1;j<vis.length;j++){
        if(ov(A, boxOf(vis[j].el), 0.5)) overlaps.push(['label-label', vis[i].name, vis[j].name]);
      }
      for(const a of obstacles){
        const own = isOwnMarker(a, vis[i]);
        if(own) continue;
        if(a.kind==='icon' && iconState.some(s=>s.code===a.name && s.hide)) continue;
        if(ov(A, a, 0.25)) overlaps.push(['label-'+a.kind, vis[i].name, a.name]);
      }
    }
    const visIcons=iconState.filter(ic=>!ic.hide);
    for(let i=0;i<visIcons.length;i++){
      const A=iconBoxOf(visIcons[i].g);
      for(let j=i+1;j<visIcons.length;j++){
        if(ov(A, iconBoxOf(visIcons[j].g), 0.25)) overlaps.push(['icon-icon', visIcons[i].code, visIcons[j].code]);
      }
      for(const a of obstacles){
        if(a.kind==='icon' && a.name===visIcons[i].code) continue;
        if(a.kind==='icon' && iconState.some(s=>s.code===a.name && s.hide)) continue;
        if((a.kind==='dot'||a.kind==='ring') && LINK_CITY[visIcons[i].code] && a.name===LINK_CITY[visIcons[i].code]) continue;
        if((a.kind==='dot'||a.kind==='ring'||a.kind==='icon') && ov(A,a,0.25)) overlaps.push(['icon-'+a.kind, visIcons[i].code, a.name]);
      }
    }
    return overlaps;
  }

  const labels = recs.map(r => ({
    id: r.id,
    sel: r.sel,
    name: r.name,
    typ: r.isCapCity ? 'capital' : (r.typ==='ap-name'?'airport':r.typ),
    x: r.x!=null ? +(+r.x).toFixed(1) : null,
    y: r.y!=null ? +(+r.y).toFixed(1) : null,
    anchor: r.anchor || 'start',
    hide: !!r.hide,
    hideClass: r.hide ? (r.hideClass || (r.typ==='airport'||r.typ==='ap-name'?'ap-code-crowd': (r.typ==='region'||r.typ==='group')?'lbl-crowd':'ct-label-crowd')) : null,
    onDark: false,
    isCap: !!r.isCapCity,
    tight: false,
    kt: null,
    wrap: r.wrap || null,
    leadSel: (r.id && r.id.startsWith('l-')) ? ('#g-lb line.lbl-lead[data-a="'+r.id.slice(2)+'"]') : null,
    leadHidden: (r.typ==='region'||r.typ==='group') ? true : false,
    owner: r.code || null,
    key: r.key,
  }));
  const vis = labels.filter(l => !l.hide).length;
  const hid = labels.filter(l => l.hide).length;
  const icons = iconState.map(ic => ({code: ic.code, hide: !!ic.hide}));
  const gaps = recs.filter(r => !r.hide && r.gap!=null).map(r => ({name:r.name, typ:r.typ, gap:r.gap}));
  const maxGap = gaps.reduce((m,g)=>Math.max(m,g.gap), 0);
  return {labels, vis, hid, overlaps: audit(), slotScale:+s.toFixed(4), icons, maxGap:+maxGap.toFixed(1), gaps};
}"""

SETUP = """() => {
  window.PPC_LABEL_PLAN = null;
  const cfg = window.PPC_MAP;
  if (cfg) cfg.afterLabels = function(){};
  if (window.PPC_mapView) window.PPC_mapView.refreshLabels = function(){};
  const m = document.getElementById('map');
  if (!m) return false;
  const HIDE = ['lbl-crowd','ct-label-crowd','ap-code-crowd','ap-name-crowd','ct-crowd','ap-crowd','ppc-lbl-hide'];
  m.querySelectorAll('text, .ct, .ap, line.lbl-lead').forEach(el => {
    el.classList.remove(...HIDE);
    el.style.removeProperty('display');
  });
  m.querySelectorAll('text[data-x0]').forEach(el => {
    el.setAttribute('x', el.getAttribute('data-x0'));
    el.setAttribute('y', el.getAttribute('data-y0'));
  });
  return true;
}"""

def apply_zoom(page, k, map_w=975, map_h=610):
    page.evaluate('''(args) => {
      const [k, MAP_W, MAP_H] = args;
      const w = MAP_W * k, h = MAP_H * k;
      const x = (MAP_W - w) / 2, y = (MAP_H - h) / 2;
      if(window.PPC_mapView && window.PPC_mapView.applyViewBox){
        window.PPC_mapView.applyViewBox([x, y, w, h]);
      } else {
        const m=document.getElementById('map');
        if(m) m.setAttribute('viewBox', [x,y,w,h].join(' '));
      }
    }''', [k, map_w, map_h])
    page.wait_for_timeout(160)

def main():
    labels_js = SITE / 'assets/js/australia-map-labels.js'
    backup = labels_js.read_text()
    labels_js.write_text('window.PPC_LABEL_PLAN=null;\n')
    (ROOT/'static'/'assets'/'js'/'japan-map-labels.js').write_text('window.PPC_LABEL_PLAN=null;\n')
    tiers=[]
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=CHROME, args=['--disable-dev-shm-usage','--disable-http-cache'], headless=True)
            for view in VIEWS:
                ctx = browser.new_context(viewport={'width':view['w'],'height':view['h']}, device_scale_factor=1)
                page = ctx.new_page()
                page.goto(BASE+'/countries/australia-map.html?pack=3', wait_until='domcontentloaded', timeout=60000)
                page.wait_for_selector('svg#map', timeout=30000)
                page.wait_for_timeout(400)
                page.evaluate(SETUP)
                page.wait_for_timeout(200)
                lock = []
                for k in K_TIERS:
                    apply_zoom(page, k)
                    page.evaluate(SETUP)
                    page.wait_for_timeout(80)
                    data = page.evaluate(PACK_JS, {
                        'k': k,
                        'zoomOnly': sorted(ZOOM_ONLY),
                        'majorAp': sorted(MAJOR_AP),
                        'cityNames': sorted(CITY_NAMES),
                        'cityZoomOnly': sorted(CITY_ZOOM_ONLY),
                        'cityRestFirst': sorted(CITY_REST_FIRST),
                        'cityRestLast': sorted(CITY_REST_LAST),
                        'linkCity': LINK_CITY,
                        'lock': lock,
                        'capital': CAPITAL,
                        'wrap': WRAP_NAMES,
                        'geoName': GEO_NAME,
                        'hideRegionsAtRest': HIDE_REGIONS_AT_REST,
                        'groupMembers': GROUP_MEMBERS,
                    })
                    if data.get('error'):
                        raise RuntimeError(data)
                    labels = data['labels']
                    cities_on = [l['name'] for l in labels if (not l['hide'] and l['typ'] in ('city','capital'))]
                    cities_hid = [l['name'] for l in labels if (l['hide'] and l['typ'] in ('city','capital'))]
                    ap_on = [l['name'] for l in labels if (not l['hide'] and l['typ']=='airport')]
                    groups_on = [l['name'] for l in labels if (not l['hide'] and l['typ']=='group')]
                    groups_hid = [l['name'] for l in labels if (l['hide'] and l['typ']=='group')]
                    regions_on = [l['name'] for l in labels if (not l['hide'] and l['typ']=='region')]
                    rome = [l for l in labels if l.get('isCap') or (l['name']==CAPITAL and l['typ'] in ('city','capital'))]
                    icons_on = [i['code'] for i in (data.get('icons') or []) if not i.get('hide')]
                    print(f"  {view['name']}-k{k}: vis={data['vis']} hid={data['hid']} s={data.get('slotScale')} maxGap={data.get('maxGap')} cities_on={cities_on} ap_on={ap_on} icons_on={icons_on} groups_on={groups_on} groups_hid={groups_hid} regions_on={regions_on} overlaps={data.get('overlaps')} capital={[ (l['hide'], l['x'], l['y'], l['anchor']) for l in rome ]}", flush=True)
                    lock = [{'key':l['key'],'x':l['x'],'y':l['y'],'anchor':l['anchor'],'typ':l['typ'],'name':l['name'],'id':l['id'],'sel':l['sel']}
                            for l in labels if not l['hide'] and l.get('key')]
                    pub = [{kk:v for kk,v in l.items() if kk!='key'} for l in labels]
                    vb = page.evaluate('''() => {
                      const v=document.getElementById('map').viewBox.baseVal;
                      return [+v.x.toFixed(2),+v.y.toFixed(2),+v.width.toFixed(2),+v.height.toFixed(2)];
                    }''')
                    tiers.append({
                        'name': f"{view['name']}-k{k}",
                        'k': k,
                        'mobile': view['mobile'],
                        'vp': view['w'],
                        'viewBox': vb,
                        'labels': pub,
                        'icons': data.get('icons') or [],
                        'visible': data['vis'],
                        'hidden': data['hid'],
                        'overlaps': data.get('overlaps') or [],
                        'capitals': [{'name':l['name'],'hide':l['hide'],'x':l['x'],'y':l['y'],'isCap':l.get('isCap')} for l in pub if l.get('isCap') or l['name']==CAPITAL],
                    })
                ctx.close()
            browser.close()
    except Exception:
        labels_js.write_text(backup)
        raise

    plan = {
        'country': 'au',
        'mapW': 975,
        'generated': time.strftime('%Y-%m-%dT%H:%M:%S%z'),
        'tiers': tiers,
    }
    body = 'window.PPC_LABEL_PLAN=' + json.dumps(plan, ensure_ascii=False, separators=(',', ':')) + ';\n'
    for dest in OUT:
        dest.write_text(body)
        print('wrote', dest, 'bytes', len(body))
    qa = ROOT/'qa'/'label-plans'
    qa.mkdir(parents=True, exist_ok=True)
    summary = {
        'country': 'au',
        'tiers': [{'name':t['name'],'k':t['k'],'mobile':t['mobile'],'visible':t['visible'],'hidden':t['hidden'],
                   'overlaps':t.get('overlaps') or [],
                   'cities_on':[l['name'] for l in t['labels'] if not l['hide'] and l['typ'] in ('city','capital')],
                   'cities_hid':[l['name'] for l in t['labels'] if l['hide'] and l['typ'] in ('city','capital')],
                   'airports_on':[l['name'] for l in t['labels'] if not l['hide'] and l['typ']=='airport'],
                   'groups_on':[l['name'] for l in t['labels'] if not l['hide'] and l['typ']=='group'],
                   'groups_hid':[l['name'] for l in t['labels'] if l['hide'] and l['typ']=='group'],
                   'regions_on':[l['name'] for l in t['labels'] if not l['hide'] and l['typ']=='region'],
                   'capitals':t['capitals']} for t in tiers]
    }
    (qa/'au-summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
