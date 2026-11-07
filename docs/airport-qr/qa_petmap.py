from playwright.sync_api import sync_playwright
import json,sys,requests
from pathlib import Path
B=Path(__file__).parent;S=B/'shots';S.mkdir(exist_ok=True)
BASE='http://127.0.0.1:8782/pet-map/site/'
codes=sys.argv[1].split(',') if len(sys.argv)>1 else json.loads((B/'airports.json').read_text()).keys()
R=[];links=set()
with sync_playwright() as p:
 br=p.chromium.launch(args=['--no-sandbox'])
 for c in list(codes)+['']:
  for w,h in [(390,844),(1440,900)]:
   pg=br.new_page(viewport={'width':w,'height':h});err=[]
   pg.on('pageerror',lambda x:err.append(str(x)));pg.on('console',lambda m:err.append(m.text) if m.type=='error' else None)
   pg.on('response',lambda r:err.append(f'{r.status} {r.url}') if r.status>=400 else None)
   pg.goto(BASE+'airport/'+(c+'/' if c else ''),wait_until='networkidle')
   info=pg.evaluate('''()=>{const s=document.querySelector('.pm-svg');let small=[],out=[];if(s){const k=s.getBoundingClientRect().width/s.viewBox.baseVal.width;s.querySelectorAll('text').forEach(t=>{const fs=parseFloat(getComputedStyle(t).fontSize)*k;if(fs<11)small.push(t.textContent+':'+fs.toFixed(1));const b=t.getBBox();const r=b.x+b.width;if((b.x<180&&b.x>20&&r>190&&!t.classList.contains('pm-tn')&&!t.closest('.pm-extra')&&!t.classList.contains('pm-side')&&!t.classList.contains('pm-zone')&&!t.classList.contains('pm-sect')&&!t.classList.contains('pm-q'))||b.x<0||b.x+b.width>s.viewBox.baseVal.width+0.5)out.push(t.textContent)})}
   const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);return{overflow:document.documentElement.scrollWidth>innerWidth,dup:ids.filter((v,i)=>ids.indexOf(v)!==i),small,out,links:[...document.querySelectorAll('a[href]')].map(a=>a.href).filter(u=>u.startsWith(location.origin)),pm:!!s,firstAfterHero:document.querySelector('.airport-hero')?.nextElementSibling?.id||''}}''')
   links.update(u.split('#')[0].split('?')[0] for u in info.pop('links'))
   ov=None
   if c:
    sec=pg.locator('#pet-map')
    if w==390:
     pg.evaluate("window.scrollTo({top:document.querySelector('#pet-map').getBoundingClientRect().top+scrollY-70,behavior:'instant'})");pg.screenshot(path=str(S/f'{c}-petmap-390x844.png'))
    else:
     pg.evaluate("window.scrollTo({top:document.querySelector('#pet-map').getBoundingClientRect().top+scrollY-80,behavior:'instant'})");pg.screenshot(path=str(S/f'{c}-petmap-1440x900.png'))
    pg.click('.pm-open');o=pg.evaluate("({open:!document.querySelector('.pm-overlay').hidden,focus:document.activeElement.className,role:document.querySelector('.pm-overlay').getAttribute('role')})")
    if w==390:pg.screenshot(path=str(S/f'{c}-petmap-fullscreen-390x844.png'))
    pg.keyboard.press('Escape');esc=pg.evaluate("document.querySelector('.pm-overlay').hidden && document.activeElement.classList.contains('pm-open')")
    pg.click('.pm-open');pg.click('.pm-close');x=pg.evaluate("document.querySelector('.pm-overlay').hidden")
    ov=dict(o,escClose=esc,xClose=x)
   R.append(dict(page=c or 'index',vp=f'{w}x{h}',errors=err,overlay=ov,**info));pg.close()
 br.close()
broken=[u for u in sorted(links) if requests.get(u).status_code!=200]
bad=[r for r in R if r['errors'] or r['overflow'] or r['dup'] or r['small'] or r['out'] or (r['page']!='index' and (not r['pm'] or r['firstAfterHero']!='pet-map' or not all([r['overlay']['open'],r['overlay']['escClose'],r['overlay']['xClose']])))]
json.dump(dict(results=R,internal_links=len(links),broken=broken,failures=len(bad)),open(B/'qa.json','w'),indent=1)
print(len(R),'renders; failures',len(bad),'links',len(links),'broken',broken)
for r in bad:print(r['page'],r['vp'],r['errors'][:2],r['overflow'],r['dup'],r['small'][:3],r['out'][:3])
