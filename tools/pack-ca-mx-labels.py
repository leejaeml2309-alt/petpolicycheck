#!/usr/bin/env python3
"""Offline Canada / Mexico label packer (USA option A typography).

Precomputes PPC_LABEL_PLAN tiers. No runtime sampling on the live page.
Fans listed airports off their city dots with dashed leaders (already styled
in CSS). Keeps geometry and fills unchanged.
"""
from __future__ import annotations
import json, time, os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CHROME = '/usr/bin/google-chrome'
BASE = os.environ.get('PPC_PACK_BASE', 'http://127.0.0.1:8877')

FAN_PREF = {
    # away from the city dot; chosen to open space vs neighbours
    'YVR': (-22, 10),   # west of Vancouver, away from Victoria
    'YYC': (20, 12),
    'YWG': (20, 12),
    'YHZ': (16, 18),    # SE of Halifax
    'YQM': (-14, 18),   # S of Moncton / away from YYG+YHZ
    'YYG': (16, -16),   # NE of Charlottetown
    'YYZ': (-20, 10),
    'YUL': (18, -12),
    'YXE': (18, 10),
    'YYT': (18, -10),
    'YZF': (18, 8),
    'YXY': (18, 8),
    'YFB': (18, 10),
    'MEX': (20, -14),
    'CUN': (18, -10),   # east, away from Playa del Carmen
    'GDL': (14, 18),    # south, away from PVR
    'MTY': (18, -12),
    'SJD': (16, 16),
    'PVR': (-20, 8),    # west, away from GDL
}
FAN_MUST = ['YYC','YVR','YWG','MEX','GDL','MTY','CUN','SJD','PVR','YHZ','YQM','YYG']

VIEWS = [
    {'name': 'desk-1280', 'w': 1280, 'h': 800, 'mobile': False, 'vp': 1280},
    {'name': 'desk-1440', 'w': 1440, 'h': 900, 'mobile': False, 'vp': 1440},
    {'name': 'phone-390', 'w': 390, 'h': 844, 'mobile': True, 'vp': 390},
]
K_TIERS = [1.0, 0.625, 0.40]

COUNTRIES = [
    {'code': 'ca', 'path': '/countries/canada-map.html', 'out': 'canada-map-labels.js', 'var': 'CA'},
    {'code': 'mx', 'path': '/countries/mexico-map.html', 'out': 'mexico-map-labels.js', 'var': 'MX'},
]

PACK_JS = r"""(opts) => {
  const FAN_PREF = Object.assign({}, opts.fanPref || {});
  const FAN_MUST = new Set(opts.fanMust || []);
  const kMark = opts.kMark || 1;
  const forceZoomed = !!opts.forceZoomed;

  const m = document.getElementById('map');
  if (!m) return {error:'no map'};

  if (typeof hoistMapLabels === 'function') hoistMapLabels();
  if (typeof syncLabelScale === 'function') syncLabelScale();

  m.classList.toggle('is-zoomed', forceZoomed);
  m.style.setProperty('--k', String(kMark));
  m.style.setProperty('--kt', String(Math.sqrt(kMark)));
  m.querySelectorAll('#g-ap .ap .ap-mark').forEach(g => {
    g.setAttribute('transform', kMark>0.999 ? '' : 'scale('+kMark.toFixed(4)+')');
  });

  const HIDE = ['lbl-crowd','ct-label-crowd','ap-code-crowd','ap-name-crowd','ct-crowd','ap-crowd','ppc-lbl-hide'];
  function show(el){
    if (!el) return;
    el.classList.remove(...HIDE);
    el.style.removeProperty('display');
    const g = el.closest && el.closest('.ct,.ap');
    if (g) g.classList.remove('ct-crowd','ap-crowd','ap-code-crowd');
  }
  document.querySelectorAll('#g-lb text, #g-ct .ct text, #g-ap .ap text, #g-ap .ap, #g-ct .ct, #g-ap-link line').forEach(show);
  /* Reset is-cap from the city group, not from a previously applied plan. */
  document.querySelectorAll('#g-lb text.ct-label, #g-ct .ct text').forEach(el => {
    el.classList.remove('is-cap');
    if (el.dataset) el.dataset.kind = 'city';
    const owner = el.dataset && el.dataset.owner;
    const g = owner ? document.querySelector('#g-ct .ct[data-k="'+owner+'"]') : (el.closest && el.closest('.ct'));
    if (g && g.classList.contains('cap')) {
      el.classList.add('is-cap');
      if (el.dataset) el.dataset.kind = 'capital';
    }
  });


  function vis(el){
    if (!el) return null;
    const cs = getComputedStyle(el);
    if (cs.display==='none' || cs.visibility==='hidden' || +cs.opacity===0) return null;
    const b = el.getBoundingClientRect();
    if (b.width<1 || b.height<1) return null;
    return b;
  }
  function overlap(a,b,pad){
    return !(a.right+pad<b.left || a.left-pad>b.right || a.bottom+pad<b.top || a.top-pad>b.bottom);
  }
  function area(a,b,pad){
    const x=Math.max(0, Math.min(a.right,b.right)-Math.max(a.left,b.left)+2*pad);
    const y=Math.max(0, Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)+2*pad);
    return (x>0 && y>0) ? x*y : 0;
  }
  const svgRect = m.getBoundingClientRect();
  const vb = (m.viewBox && m.viewBox.baseVal && m.viewBox.baseVal.width) || 975;
  const u = vb / (svgRect.width || 975);
  function inMap(box, slack){
    slack = slack==null ? 4 : slack;
    return box.left>=svgRect.left-slack && box.right<=svgRect.right+slack &&
           box.top>=svgRect.top-slack && box.bottom<=svgRect.bottom+slack;
  }
  function slots(x, y, anchors, maxPx){
    const out=[{x,y,anchor:anchors||null}];
    const rings=[10,16,22,28,36,46,58,72,88,108];
    rings.filter(px=>maxPx==null||px<=maxPx).forEach(px=>{
      const d=px*u;
      [[d,0,'start'],[-d,0,'end'],[0,d,anchors],[0,-d,anchors],
       [d,d,'start'],[-d,d,'end'],[d,-d,'start'],[-d,-d,'end'],
       [d*1.4,0,'start'],[-d*1.4,0,'end'],[0,d*1.4,anchors],[0,-d*1.4,anchors]
      ].forEach(p=> out.push({x:x+p[0], y:y+p[1], anchor:p[2]||anchors||null}));
    });
    return out;
  }
  function applyPos(el, s){
    el.setAttribute('x', (+s.x).toFixed(1));
    el.setAttribute('y', (+s.y).toFixed(1));
    if (s.anchor) el.setAttribute('text-anchor', s.anchor);
    el.querySelectorAll('tspan').forEach(ts => ts.setAttribute('x', (+s.x).toFixed(1)));
  }
  function typOf(el){
    if (el.classList.contains('is-cap') || (el.closest && el.closest('.ct.cap'))) return 'capital';
    if (el.classList.contains('ap-label') || (el.dataset && el.dataset.kind==='airport') || (el.closest && el.closest('.ap'))) return 'airport';
    if (el.classList.contains('ct-label') || (el.dataset && el.dataset.kind==='city') || (el.closest && el.closest('.ct'))) return el.classList.contains('is-cap')?'capital':'city';
    if (el.classList.contains('lbl')) return 'region';
    return 'region';
  }
  function norm(s){ return String(s||'').replace(/\s+/g,' ').trim(); }

  /* ----- fan airports off city dots ----- */
  const icons = [];
  const iconEls = [...m.querySelectorAll('#g-ap .ap')];
  iconEls.forEach(g => {
    const code = g.getAttribute('data-code');
    const tr = g.getAttribute('transform')||'';
    const mm = /translate\(\s*([-+\d.eE]+)\s*[,\s]\s*([-+\d.eE]+)/.exec(tr);
    const ox = mm?+mm[1]:0, oy = mm?+mm[2]:0;
    let fx = ox, fy = oy;
    const pref = FAN_PREF[code];
    const must = FAN_MUST.has(code);
    const link = document.querySelector('#g-ap-link line.ap-link[data-code="'+code+'"]');
    let cx=ox, cy=oy;
    if (link){ cx=+link.getAttribute('x1')||ox; cy=+link.getAttribute('y1')||oy; }
    const dist = Math.hypot(ox-cx, oy-cy);
    if (must || dist < 12 || pref){
      if (pref){ fx = cx + pref[0]; fy = cy + pref[1]; }
      else {
        let vx = ox-cx, vy = oy-cy;
        if (Math.hypot(vx,vy) < 0.8){ vx = 14; vy = 10; }
        const n = Math.hypot(vx,vy) || 1;
        fx = cx + vx/n*20;
        fy = cy + vy/n*20;
      }
    }
    g.setAttribute('transform', 'translate('+fx+' '+fy+')');
    if (link){ link.setAttribute('x2', fx); link.setAttribute('y2', fy); }
    const lab = document.querySelector('#g-lb text.ap-label[data-owner="'+code+'"], #g-ap .ap[data-code="'+code+'"] text');
    if (lab){
      /* keep the label next to the fanned mark (default was +16 y in group space) */
      if (!lab.dataset.hoisted){
        /* not hoisted yet: relative coords stay */
      } else {
        const relx = +(lab.dataset.relx != null ? lab.dataset.relx : (lab.getAttribute('x')||0) - ox);
        const rely = +(lab.dataset.rely != null ? lab.dataset.rely : (lab.getAttribute('y')||0) - oy);
        lab.dataset.relx = relx; lab.dataset.rely = rely;
        applyPos(lab, {x: fx+relx, y: fy+rely, anchor: lab.getAttribute('text-anchor')||'middle'});
      }
    }
    icons.push({code, tx:+(+fx).toFixed(1), ty:+(+fy).toFixed(1), hide:false, origX:ox, origY:oy});
  });

  /* Nudge fans that still sit on a city dot or another icon. */
  function iconBox(g){
    const mark = g.querySelector('.ap-mark') || g.querySelector('.pad') || g;
    return vis(mark);
  }
  const dots = [...m.querySelectorAll('#g-ct .ct circle:not(.ring)')].map(c => ({el:c, box:vis(c)})).filter(d=>d.box);
  function fanCollides(g, selfCode){
    const box = iconBox(g);
    if (!box) return 0;
    let n=0;
    dots.forEach(d => { if (overlap(box,d.box,1)) n++; });
    iconEls.forEach(og => {
      if (og===g) return;
      const b=iconBox(og);
      if (b && overlap(box,b,2)) n++;
    });
    return n;
  }
  iconEls.forEach(g => {
    const code=g.getAttribute('data-code');
    if (fanCollides(g, code)===0) return;
    const ic = icons.find(i=>i.code===code);
    if (!ic) return;
    const link = document.querySelector('#g-ap-link line.ap-link[data-code="'+code+'"]');
    const baseX = link ? +link.getAttribute('x1') : ic.origX;
    const baseY = link ? +link.getAttribute('y1') : ic.origY;
    const tries=[];
    [16,20,24,28,34,42].forEach(r => {
      for (let a=0;a<16;a++){
        const rad=a*Math.PI/8;
        tries.push([baseX+Math.cos(rad)*r, baseY+Math.sin(rad)*r]);
      }
    });
    let best=null, bestN=1e9;
    for (const [x,y] of tries){
      g.setAttribute('transform','translate('+x+' '+y+')');
      const n=fanCollides(g, code);
      if (n<bestN){ bestN=n; best=[x,y]; if (n===0) break; }
    }
    if (best){
      g.setAttribute('transform','translate('+best[0]+' '+best[1]+')');
      ic.tx=+(+best[0]).toFixed(1); ic.ty=+(+best[1]).toFixed(1);
      if (link){ link.setAttribute('x2', ic.tx); link.setAttribute('y2', ic.ty); }
      const lab = document.querySelector('#g-lb text.ap-label[data-owner="'+code+'"], #g-ap .ap[data-code="'+code+'"] text');
      if (lab && lab.dataset.hoisted){
        const relx=+(lab.dataset.relx||0), rely=+(lab.dataset.rely||16);
        applyPos(lab, {x:ic.tx+relx, y:ic.ty+rely, anchor:lab.getAttribute('text-anchor')||'middle'});
      }
    }
  });

  /* ----- collect labels ----- */
  const items=[];
  m.querySelectorAll('#g-lb text.lbl, #g-lb text.ct-label, #g-lb text.ap-label, #g-ct .ct text, #g-ap .ap text').forEach(el => {
    show(el);
    const typ=typOf(el);
    const name=norm(el.textContent);
    const id=el.id||null;
    const owner=el.dataset && el.dataset.owner || '';
    const x=+(el.getAttribute('x')||0);
    const y=+(el.getAttribute('y')||0);
    const anchor=el.getAttribute('text-anchor')||'middle';
    let pri=50;
    if (typ==='capital') pri=10;
    else if (typ==='airport') pri=20;
    else if (typ==='city') pri=30;
    else pri=40;
    if (name==='Québec City' || name==='Fredericton') pri=12;
    items.push({el, typ, name, id, owner, orig:{x,y,anchor}, pri});
  });
  items.sort((a,b)=>a.pri-b.pri);

  const placed=[];
  /* icons and dots as obstacles */
  iconEls.forEach(g => {
    const box=iconBox(g);
    if (box) placed.push({kind:'ap-icon', code:g.getAttribute('data-code'), box, el:g});
  });
  dots.forEach(d => placed.push({kind:'dot', box:d.box, el:d.el}));

  function scoreSlot(box, it){
    let n=0, ar=0;
    for (const p of placed){
      if (it && p.kind==='ap-icon' && p.code && p.code===it.owner) continue;
      const a=area(box,p.box,1);
      if (a){ n++; ar+=a; }
    }
    return {n, area:ar};
  }

  const labels=[];
  for (const it of items){
    const start=slots(it.orig.x, it.orig.y, it.orig.anchor, 108);
    let best=null;
    for (const s of start){
      applyPos(it.el, {x:s.x, y:s.y, anchor:s.anchor||it.orig.anchor});
      const box=vis(it.el);
      if (!box) continue;
      if (!inMap(box, 8)) continue;
      const sc=scoreSlot(box, it);
      if (sc.n===0){ best={s, box, sc}; break; }
      if (!best || sc.n<best.sc.n || (sc.n===best.sc.n && sc.area<best.sc.area)){
        best={s, box, sc};
      }
    }
    if (best){
      applyPos(it.el, {x:best.s.x, y:best.s.y, anchor:best.s.anchor||it.orig.anchor});
      const box=vis(it.el)||best.box;
      placed.push({kind:'label', typ:it.typ, box, el:it.el});
      labels.push({
        id: it.id,
        sel: it.id ? ('#'+it.id) : (it.owner ? null : null),
        name: it.name,
        typ: it.typ,
        x: +(+best.s.x).toFixed(1),
        y: +(+best.s.y).toFixed(1),
        anchor: best.s.anchor||it.orig.anchor,
        hide: false,
        hideClass: null,
        onDark: false,
        isCap: it.typ==='capital',
        tight: false,
        kt: null,
        wrap: null,
        leadSel: null,
        leadHidden: false,
        owner: it.owner||null
      });
    } else {
      applyPos(it.el, it.orig);
      labels.push({
        id: it.id, sel: it.id?('#'+it.id):null, name:it.name, typ:it.typ,
        x:+(+it.orig.x).toFixed(1), y:+(+it.orig.y).toFixed(1),
        anchor:it.orig.anchor, hide:false, hideClass:null, onDark:false,
        isCap: it.typ==='capital', tight:false, kt:null, wrap:null,
        leadSel:null, leadHidden:false, owner:it.owner||null
      });
    }
  }

  /* count leftover overlaps for the report */
  function leftover(){
    const labs = items.map(it => ({it, box:vis(it.el)})).filter(x=>x.box);
    let ll=0, li=0, ii=0, ld=0;
    for (let i=0;i<labs.length;i++){
      for (let j=i+1;j<labs.length;j++){
        if (overlap(labs[i].box, labs[j].box, 0)) ll++;
      }
      iconEls.forEach(g => {
        if (labs[i].it.owner && g.getAttribute('data-code')===labs[i].it.owner) return;
        const b=iconBox(g); if (b && overlap(labs[i].box,b,0)) li++;
      });
      dots.forEach(d => { if (overlap(labs[i].box,d.box,0)) ld++; });
    }
    for (let i=0;i<iconEls.length;i++){
      const a=iconBox(iconEls[i]); if(!a) continue;
      for (let j=i+1;j<iconEls.length;j++){
        const b=iconBox(iconEls[j]); if (b && overlap(a,b,0)) ii++;
      }
    }
    return {ll, li, ii, ld};
  }

  return {
    labels,
    icons: icons.map(i => ({code:i.code, tx:i.tx, ty:i.ty, hide:false})),
    leftover: leftover(),
    count: labels.length
  };
}
"""

def write_plan(country, code, tiers):
    payload = {
        'country': code,
        'mapW': 975,
        'generated': time.strftime('%Y-%m-%dT%H:%M:%S+0900'),
        'tiers': tiers,
    }
    js = 'window.PPC_LABEL_PLAN=' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';\n'
    for dest in [SITE / 'assets/js' / country['out'], ROOT / 'static/assets/js' / country['out']]:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(js)
        print(' wrote', dest, 'bytes', dest.stat().st_size)
    return js


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=['--disable-gpu','--no-sandbox'])
        for country in COUNTRIES:
            print('='*60, country['code'])
            tiers = []
            for view in VIEWS:
                page = browser.new_page(viewport={'width': view['w'], 'height': view['h'], 'device_scale_factor': 1})
                page.goto(BASE + country['path'], wait_until='networkidle', timeout=60000)
                page.wait_for_timeout(400)
                page.evaluate("""() => { if (window.CFG) CFG.afterLabels = null; window.PPC_LABEL_PLAN = null; }""")
                for k in K_TIERS:
                    name = f"{view['name']}-k{k:.3f}".replace('0.000','').rstrip('0').rstrip('.')
                    # pack zoom typography at full viewBox but with is-zoomed + scaled marks
                    result = page.evaluate(PACK_JS, {
                        'fanPref': FAN_PREF,
                        'fanMust': FAN_MUST,
                        'kMark': k,
                        'forceZoomed': k < 0.999,
                    })
                    if result.get('error'):
                        raise SystemExit(f"{country['code']} {name}: {result}")
                    leftover = result.get('leftover') or {}
                    print(f"  {name:24} labels={result.get('count')} leftover={leftover}")
                    tiers.append({
                        'name': name,
                        'k': k,
                        'mobile': view['mobile'],
                        'vp': view['vp'],
                        'viewBox': [0, 0, 975, 610],
                        'labels': result['labels'],
                        'icons': result['icons'],
                    })
                page.close()
            write_plan(country, country['code'], tiers)
        browser.close()
    print('done')

if __name__ == '__main__':
    main()
