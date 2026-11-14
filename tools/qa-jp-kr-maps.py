#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8845'
OUT = Path('/workspace/jp-kr-maps-20261114/qa')
CHROME = '/usr/bin/google-chrome'

AUDIT_JS = r'''(opts) => {
  const CAPITAL = opts.capital;
  const m = document.getElementById('map');
  const root = document.getElementById('country-map');
  if (!m || !root) return {error:'no map'};
  function ov(a,b,pad){
    pad = pad==null ? 0.25 : pad;
    return !(a.x+a.w+pad<=b.x || b.x+b.w+pad<=a.x || a.y+a.h+pad<=b.y || b.y+b.h+pad<=a.y);
  }
  function visBox(el){
    const cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0) return null;
    if(el.classList.contains('ppc-lbl-hide')) return null;
    const r=el.getBoundingClientRect();
    if(r.width<1||r.height<1) return null;
    return {x:r.x,y:r.y,w:r.width,h:r.height,el,name:(el.getAttribute('data-code')||el.getAttribute('aria-label')||el.textContent||'').trim().replace(/\s+/g,' ').slice(0,40)};
  }
  function boxGap(pt, box){
    const cx=Math.max(box.x, Math.min(pt.x, box.x+box.w));
    const cy=Math.max(box.y, Math.min(pt.y, box.y+box.h));
    return Math.hypot(pt.x-cx, pt.y-cy);
  }
  function mapToScreen(mx, my){
    const vb = m.viewBox.baseVal;
    const br = m.getBoundingClientRect();
    return {x: br.x + (mx - vb.x) * br.width / vb.width,
            y: br.y + (my - vb.y) * br.height / vb.height};
  }
  const labels=[], icons=[], dots=[];
  m.querySelectorAll('#g-lb text, #g-ct .ct text, #g-ap .ap text').forEach(el=>{
    const b=visBox(el); if(b) labels.push(b);
  });
  m.querySelectorAll('#g-ap .ap').forEach(g=>{
    if(g.classList.contains('ppc-lbl-hide')) return;
    const cs=getComputedStyle(g);
    if(cs.display==='none'||cs.visibility==='hidden') return;
    const mk=g.querySelector('.ap-mark')||g;
    const b=visBox(mk);
    if(b){ b.name=g.getAttribute('data-code'); b.kind='icon'; b.code=g.getAttribute('data-code'); icons.push(b); }
  });
  m.querySelectorAll('#g-ct .ct circle:not(.ring)').forEach(c=>{
    const g=c.closest('.ct');
    const b=visBox(c);
    if(b){ b.name=(g&&(g.getAttribute('aria-label')||'').split(',')[0])||'dot'; b.kind='dot'; b.cx=+c.getAttribute('cx'); b.cy=+c.getAttribute('cy'); dots.push(b); }
  });
  m.querySelectorAll('#g-ct .ct.cap .ring').forEach(c=>{
    const g=c.closest('.ct');
    const b=visBox(c);
    if(b){ b.name=(g&&(g.getAttribute('aria-label')||'').split(',')[0])||'ring'; b.kind='ring'; dots.push(b); }
  });
  const overlaps=[];
  function check(listA, listB, typ, same){
    for(let i=0;i<listA.length;i++){
      const start = same ? i+1 : 0;
      for(let j=start;j<listB.length;j++){
        if(listA[i].el===listB[j].el) continue;
        if(typ.startsWith('label-icon') && listA[i].name.startsWith(listB[j].name||'')) continue;
        if(typ.startsWith('label-dot') && listA[i].name.split(',')[0]===listB[j].name) continue;
        if(ov(listA[i], listB[j])) overlaps.push([typ, listA[i].name, listB[j].name]);
      }
    }
  }
  check(labels, labels, 'label-label', true);
  check(labels, icons, 'label-icon', false);
  check(labels, dots, 'label-dot', false);
  check(icons, icons, 'icon-icon', true);
  const LINK={NRT:'Tokyo',HND:'Tokyo',KIX:'Osaka',NGO:'Nagoya',FUK:'Fukuoka',CTS:'Sapporo',OKA:'Naha',ICN:'Seoul',GMP:'Seoul',PUS:'Busan'};
  check(icons, dots, 'icon-dot', false);
  for(let i=overlaps.length-1;i>=0;i--){
    const o=overlaps[i];
    if(o[0]==='icon-dot' && LINK[o[1]]===o[2]) overlaps.splice(i,1);
    if(o[0]==='label-dot' && LINK[o[1]]===o[2]) overlaps.splice(i,1);
  }

  const gaps=[];
  labels.forEach(l => {
    const typ = l.el.classList.contains('ap-label') || (l.el.dataset && l.el.dataset.kind==='airport') || l.el.closest('.ap') ? 'airport'
      : (l.el.classList.contains('ct-label') || l.el.classList.contains('is-cap') || (l.el.dataset && (l.el.dataset.kind==='city'||l.el.dataset.kind==='capital')) || l.el.closest('.ct')) ? 'city'
      : 'region';
    if(typ==='region') return;
    let pt=null;
    if(typ==='city'){
      const owner=l.el.dataset && l.el.dataset.owner;
      const g=l.el.closest('.ct') || (owner && document.querySelector('#g-ct .ct[data-k="'+owner+'"]'));
      const c=g && g.querySelector('circle:not(.ring)');
      if(c) pt=mapToScreen(+c.getAttribute('cx'), +c.getAttribute('cy'));
    } else {
      const code=(l.el.dataset && l.el.dataset.owner) || l.name;
      const g=document.querySelector('#g-ap .ap[data-code="'+code+'"]');
      if(g){
        const tr=g.getAttribute('transform')||'';
        const mm=/translate\(\s*([-+\d.eE]+)\s*[,\s]\s*([-+\d.eE]+)/.exec(tr);
        if(mm) pt=mapToScreen(+mm[1], +mm[2]);
      }
    }
    if(!pt) return;
    const gap=boxGap(pt, l);
    gaps.push({name:l.name, typ, gap:+gap.toFixed(1)});
  });
  const maxGap = gaps.reduce((m,g)=>Math.max(m,g.gap), 0);
  const far = gaps.filter(g=>g.gap>16);

  const capDot = [...m.querySelectorAll('#g-ct .ct.cap')].some(g=>{
    const cs=getComputedStyle(g);
    if(cs.display==='none'||g.classList.contains('ppc-lbl-hide')) return false;
    return (g.getAttribute('aria-label')||'').split(',')[0]===CAPITAL;
  });
  const nCapDots = m.querySelectorAll('#g-ct .ct.cap').length;
  const capLbl = labels.some(l=>l.name===CAPITAL || l.name.startsWith(CAPITAL+' '));
  const cities = labels.filter(l=>{
    const el=l.el;
    return el.classList.contains('ct-label') || (el.dataset && (el.dataset.kind==='city'||el.dataset.kind==='capital')) || el.classList.contains('is-cap') || !!(el.closest && el.closest('.ct'));
  }).map(l=>l.name.split(',')[0]);
  function regionInside(el){
    const name=(el.getAttribute('data-full')||el.getAttribute('data-group')||el.textContent||'').replace(/\s+/g,' ').trim();
    const GROUP_MEMBERS={'Hokkaido':['01'],'Tohoku':['02','03','04','05','06','07'],'Kanto':['08','09','10','11','12','13','14'],'Chubu':['15','16','17','18','19','20','21','22','23'],'Kansai':['24','25','26','27','28','29','30'],'Chugoku':['31','32','33','34','35'],'Shikoku':['36','37','38','39'],'Kyushu-Okinawa':['40','41','42','43','44','45','46'],'Kyushu':['40','41','42','43','44','45','46']};
    const groupKey=el.getAttribute('data-group') || (el.classList.contains('lbl-group') ? name : null);
    let paths=[];
    if(groupKey && GROUP_MEMBERS[groupKey]){
      paths=GROUP_MEMBERS[groupKey].map(id=>m.querySelector('#s-'+id)).filter(Boolean);
    } else {
      const id=el.id && el.id.startsWith('l-') ? el.id.slice(2) : (el.id && el.id.startsWith('lg-') ? null : el.id);
      const path=id ? m.querySelector('#s-'+id) : null;
      if(path) paths=[path];
    }
    if(!paths.length) return {ok:false, reason:'no-path', name, inside:0};
    const r=el.getBoundingClientRect();
    const inset=1.5;
    const box={x:r.x,y:r.y,w:r.width,h:r.height};
    if(box.w<=2*inset || box.h<=2*inset) return {ok:false, reason:'too-small', name, inside:0};
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
        const pt=new DOMPoint(sx,sy).matrixTransform(ctm.inverse());
        try{ if(path.isPointInFill(pt)){ ok=true; break; } }catch(e){}
      }
      if(ok) inside++;
    }
    return {ok: inside===9, inside, name, group:!!groupKey};
  }
  const regionAudit = labels.filter(l=>l.el.classList.contains('lbl') && !l.el.classList.contains('ct-label') && !l.el.classList.contains('ap-label')).map(l=>regionInside(l.el));
  const regionOutside = regionAudit.filter(a=>!a.ok);
  const leadsVisible = [...m.querySelectorAll('line.lbl-lead')].filter(l=>{
    const cs=getComputedStyle(l);
    return cs.display!=='none' && cs.visibility!=='hidden' && +cs.opacity!==0 && !l.classList.contains('ppc-lbl-hide');
  }).length;
  const airports = icons.map(i=>i.name);
  const regions = labels.filter(l=>l.el.classList.contains('lbl') && !l.el.classList.contains('ct-label') && !l.el.classList.contains('ap-label')).map(l=>l.name);

  const nav = document.querySelector('#site-menu') || document.querySelector('nav.nav.menu');
  let headerRows = null, headerLinkCount=0;
  if(nav){
    const links=[...nav.querySelectorAll('a:not(.menu-only)')].filter(a=>getComputedStyle(a).display!=='none');
    headerLinkCount=links.length;
    if(links.length){
      const tops=links.map(a=>Math.round(a.getBoundingClientRect().top));
      headerRows = new Set(tops).size;
    }
  }
  const longTasks = (window.__ppcLongTasks || []).filter(t => t.startTime >= (window.__ppcNavStart || 0));
  return {
    overlaps, nOverlaps: overlaps.length,
    capDot, capLbl, nCapDots, capital: CAPITAL,
    nCities: cities.length, cities,
    nAirports: airports.length, airports,
    regions,
    nLabels: labels.length, nIcons: icons.length, nDots: dots.length,
    headerRows, headerLinkCount,
    maxGap:+maxGap.toFixed(1), far, gaps,
    nLongTasks: longTasks.length,
    longTasks: longTasks.slice(0,8),
    regionAudit, regionOutside, nRegionOutside: regionOutside.length, leadsVisible
  };
}'''

SETUP_ZOOM = '''(k) => {
  const MAP_W=975, MAP_H=610;
  const w=MAP_W*k, h=MAP_H*k;
  const x=(MAP_W-w)/2, y=(MAP_H-h)/2;
  if(window.PPC_mapView && window.PPC_mapView.applyViewBox){
    window.PPC_mapView.applyViewBox([x,y,w,h]);
  } else {
    const m=document.getElementById('map');
    if(m) m.setAttribute('viewBox',[x,y,w,h].join(' '));
  }
}'''

INIT = '''
window.__ppcLongTasks = [];
window.__ppcNavStart = performance.now();
try {
  const po = new PerformanceObserver((list) => {
    for (const e of list.getEntries()) window.__ppcLongTasks.push({name:e.name,startTime:+e.startTime.toFixed(1),duration:+e.duration.toFixed(1)});
  });
  po.observe({type:'longtask', buffered:true});
} catch (e) {}
'''

def run():
    OUT.mkdir(parents=True, exist_ok=True)
    report={'pages':{}}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=CHROME, args=['--disable-dev-shm-usage','--disable-http-cache'], headless=True)

        def check(path, w, h, name, capital, zooms):
            rec={'path':path,'vp':[w,h],'capital':capital,'views':{}}
            ctx=browser.new_context(viewport={'width':w,'height':h}, device_scale_factor=1)
            page=ctx.new_page()
            page.add_init_script(INIT)
            errors=[]; failed_req=[]
            page.on('pageerror', lambda e: errors.append('page:'+str(e)))
            page.on('console', lambda m: errors.append(f'console:{m.type}:{m.text}') if m.type=='error' else None)
            page.on('requestfailed', lambda r: failed_req.append(f'{r.method} {r.url} {r.failure}'))
            resp=page.goto(BASE+path, wait_until='domcontentloaded', timeout=60000)
            status=resp.status if resp else None
            page.wait_for_selector('svg#map #g-st path, svg#map #g-ct .ct', timeout=30000)
            page.wait_for_timeout(450)
            scroll_ms=page.evaluate('''() => {
              const t0=performance.now();
              window.scrollTo(0, 40);
              const t1=performance.now();
              window.scrollTo(0, 0);
              return +(t1-t0).toFixed(2);
            }''')
            rec['status']=status
            rec['errors']=errors[:]
            rec['failed_req']=[u for u in failed_req if 'favicon' not in u and 'googletagmanager' not in u and 'google-analytics' not in u]
            rec['scroll_ms']=scroll_ms

            for k, shot, scroll in zooms:
                page.evaluate(SETUP_ZOOM, k)
                page.wait_for_timeout(280)
                if scroll=='map':
                    page.evaluate('''() => {
                      const el=document.querySelector('.mapcard') || document.getElementById('map');
                      if(el){ const r=el.getBoundingClientRect(); window.scrollTo(0, Math.max(0, window.scrollY + r.top - 72)); }
                    }''')
                elif scroll=='top':
                    page.evaluate('() => window.scrollTo(0,0)')
                page.wait_for_timeout(140)
                data=page.evaluate(AUDIT_JS, {'k':k, 'capital':capital})
                rec['views'][f'k{k}'] = data
                if shot:
                    page.screenshot(path=str(shot), full_page=False)
            ctx.close()
            report['pages'][name]=rec
            return rec

        check('/countries/japan-map.html', 1280, 800, 'jp-en-1280', 'Tokyo',
              zooms=[(1.0, OUT/'jp-1280-rest.png', 'map'), (0.625, OUT/'jp-1280-zoom.png', 'map')])
        check('/countries/japan-map.html', 390, 844, 'jp-en-390', 'Tokyo',
              zooms=[(1.0, OUT/'jp-390-rest.png', 'map'), (0.625, None, 'map')])
        check('/it/countries/japan-map.html', 1280, 800, 'jp-it-1280', 'Tokyo', zooms=[(1.0, None, 'map')])
        check('/es/countries/japan-map.html', 1280, 800, 'jp-es-1280', 'Tokyo', zooms=[(1.0, None, 'map')])
        check('/countries/south-korea-map.html', 1280, 800, 'kr-en-1280', 'Seoul',
              zooms=[(1.0, OUT/'kr-1280-rest.png', 'map'), (0.625, OUT/'kr-1280-zoom.png', 'map')])
        check('/countries/south-korea-map.html', 390, 844, 'kr-en-390', 'Seoul',
              zooms=[(1.0, OUT/'kr-390-rest.png', 'map'), (0.625, None, 'map')])
        check('/it/countries/south-korea-map.html', 1280, 800, 'kr-it-1280', 'Seoul', zooms=[(1.0, None, 'map')])
        check('/es/countries/south-korea-map.html', 1280, 800, 'kr-es-1280', 'Seoul', zooms=[(1.0, None, 'map')])

        ctx=browser.new_context(viewport={'width':1280,'height':800}, device_scale_factor=1)
        page=ctx.new_page()
        werr=[]; wfail=[]
        page.on('pageerror', lambda e: werr.append('page:'+str(e)))
        page.on('console', lambda m: werr.append(f'console:{m.type}:{m.text}') if m.type=='error' else None)
        page.on('requestfailed', lambda r: wfail.append(f'{r.method} {r.url} {r.failure}'))
        resp=page.goto(BASE+'/?view=map', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_selector('#world-map .pin, #world-map path.country, #world-map path', timeout=30000)
        page.wait_for_timeout(1500)
        bridge=page.evaluate("() => {\n          const svg=document.getElementById('world-map');\n          if(!svg) return {error:'no world-map'};\n          const bridges=[...svg.querySelectorAll('.bridges .bridge, path.bridge')];\n          const pins=[...svg.querySelectorAll('.pin')];\n          const visB=bridges.filter(b=>{const cs=getComputedStyle(b); return cs.display!=='none' && +cs.opacity!==0;});\n          const pe=visB.length>0 && visB.every(b=>{\n            const cs=getComputedStyle(b);\n            const par=b.closest('.bridges');\n            const pcs=par?getComputedStyle(par):null;\n            return cs.pointerEvents==='none' || (pcs && pcs.pointerEvents==='none');\n          });\n          const nav=document.querySelector('header .nav, header nav, header');\n          let headerRows=null;\n          if(nav){ const h=nav.getBoundingClientRect().height; headerRows=h<=48?1:(h<=88?2:Math.round(h/40)); }\n          return {nBridge:visB.length, nPin:pins.length, dash: visB.slice(0,3).map(b=>getComputedStyle(b).strokeDasharray), peNone:pe, headerRows};\n        }")
        page.screenshot(path=str(OUT/'bridges-1280.png'), full_page=False)
        report['pages']['world-bridges-1280']={
            'path':'/?view=map','status': resp.status if resp else None,
            'errors':werr,
            'failed_req':[u for u in wfail if 'favicon' not in u and 'googletagmanager' not in u and 'google-analytics' not in u],
            'scroll_ms':0,
            'views':{'k1.0': dict(bridge, overlaps=[], nOverlaps=0, maxGap=0, capDot=True, capLbl=True, nCapDots=1, nCities=0, cities=[], nAirports=0, airports=[], nRegionOutside=0, leadsVisible=0, nLongTasks=0)}
        }
        ctx.close()
        browser.close()

    (OUT/'jp-kr-qa-report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False))
    all_ok=True
    print('======= JAPAN + SOUTH KOREA MAP QA =======')
    for name, rec in report['pages'].items():
        print(f"\n[{name}] status={rec['status']} scroll={rec['scroll_ms']}ms errors={len(rec['errors'])} failed={len(rec['failed_req'])}")
        if rec['errors']: print('  ERRORS', rec['errors'][:8])
        if rec['failed_req']: print('  FAILED', rec['failed_req'][:8])
        for vk, data in rec['views'].items():
            if data.get('error'):
                print('  VIEW ERROR', vk, data); all_ok=False; continue
            print(f"  {vk}: overlaps={data['nOverlaps']} maxGap={data['maxGap']} capDot={data['capDot']} capLbl={data['capLbl']} nCapDots={data['nCapDots']} cities={data['nCities']} {data['cities']} airports={data['nAirports']} {data['airports']} regions={data.get('regions')} headerRows={data.get('headerRows')} longTasks={data.get('nLongTasks')}")
            if data['overlaps']: print('    OVERLAPS', data['overlaps'][:12])
            if data.get('far'): print('    FAR', data['far'])
            MAJOR_JP={'Tokyo','Osaka','Yokohama','Nagoya','Sapporo','Fukuoka','Kobe','Kyoto','Sendai','Hiroshima','Naha'}
            MAJOR_KR={'Seoul','Busan','Incheon','Daegu','Daejeon','Gwangju','Ulsan','Jeju'}
            if data.get('regionOutside'): print('    REGION OUTSIDE', data['regionOutside'])
            if data.get('leadsVisible'): print('    LEADS VISIBLE', data['leadsVisible'])
            ok = (rec['status']==200 and not rec['errors'] and not rec['failed_req']
                  and data['nOverlaps']==0 and data['capDot'] and data['capLbl'] and data.get('nCapDots')==1
                  and rec['scroll_ms']<25 and data['maxGap']<=16
                  and data.get('nRegionOutside',0)==0 and data.get('leadsVisible',0)==0)
            if name.startswith('jp-') and vk=='k1.0':
                must_missing=[c for c in ('Tokyo','Osaka','Kyoto') if c not in set(data.get('cities') or [])]
                if must_missing:
                    print('    MUST CITY MISSING at rest:', must_missing)
                    ok=False
                missing=sorted(MAJOR_JP - set(data.get('cities') or []))
                if missing:
                    print('    NOTE missing JP cities at this view (packer may hide overlaps):', missing)
            if name.startswith('kr-') and name.endswith('1280') and vk=='k1.0':
                missing=sorted(MAJOR_KR - set(data.get('cities') or []))
                if missing:
                    print('    NOTE missing KR cities at this view (packer may hide overlaps):', missing)
            if name.endswith('1280') and vk=='k1.0':
                ok = ok and data.get('headerRows')==1
            if not ok:
                all_ok=False
                reasons=[]
                if rec['status']!=200: reasons.append('status')
                if rec['errors']: reasons.append('errors')
                if rec['failed_req']: reasons.append('failed_req')
                if data['nOverlaps']: reasons.append('overlaps')
                if not data['capDot'] or not data['capLbl']: reasons.append('capital')
                if data.get('nCapDots')!=1: reasons.append(f"nCapDots={data.get('nCapDots')}")
                if rec['scroll_ms']>=25: reasons.append('scroll')
                if data['maxGap']>16: reasons.append(f"maxGap={data['maxGap']}")
                if data.get('nRegionOutside'): reasons.append('region-outside')
                if data.get('leadsVisible'): reasons.append('leads')
                if name.endswith('1280') and vk=='k1.0' and data.get('headerRows')!=1: reasons.append('headerRows')
                print('    => FAIL', reasons)
            else:
                print('    => PASS')
    print('\nOVERALL', 'PASS' if all_ok else 'FAIL')
    wb=report['pages'].get('world-bridges-1280')
    if wb:
        v=wb['views']['k1.0']
        print("\n[world-bridges-1280] status=%s errors=%s failed=%s nBridge=%s nPin=%s peNone=%s dash=%s" % (wb['status'], len(wb['errors']), len(wb['failed_req']), v.get('nBridge'), v.get('nPin'), v.get('peNone'), v.get('dash')))
        if wb['errors']:
            print('  ERRORS', wb['errors'][:8])
        if v.get('nBridge',0)<2 or not v.get('peNone') or wb['errors'] or wb['status']!=200:
            all_ok=False
            print('    => FAIL bridges')
        else:
            print('    => PASS')
    for fn in ['jp-1280-rest.png','jp-1280-zoom.png','jp-390-rest.png','kr-1280-rest.png','kr-1280-zoom.png','kr-390-rest.png','bridges-1280.png']:
        fp=OUT/fn
        print('shot', fp, 'bytes', fp.stat().st_size if fp.exists() else 'MISSING')
    return 0 if all_ok else 1

if __name__=='__main__':
    raise SystemExit(run())
