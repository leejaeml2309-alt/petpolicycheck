"""Pet map: original schematic plans (terminal rows, security line, numbered paw pins).
Drawn only from source-listed text points in diagrams.POINTS; no official map is traced or copied."""
import html,textwrap
from diagrams import POINTS,MAPS
e=lambda x:html.escape(str(x),quote=True)
W=360;HALF=(16,184,192,344)  # before x0,x1 | after x0,x1
def key(label):
 k=label.split(' · ')[0].strip()
 return k
def lines(t,n=18):return textwrap.wrap(t,n)[:3] or ['']
def pin(x,y,num,unc):
 cls='pm-pin pm-unc' if unc else 'pm-pin'
 return f'<g class="{cls}"><circle cx="{x}" cy="{y}" r="11"/><text x="{x}" y="{y+4.5}" text-anchor="middle">{num}</text></g>'
def item(x,y,num,p,full=False):
 g,label,detail,note,src,unc=p
 sub=label if full else (label.split(' · ',1)[1] if ' · ' in label else '')
 txt=lines((sub+' · ' if sub else '')+detail)
 out=pin(x+12,y+11,num,p[5]);ty=y+8
 for i,t in enumerate(txt):out+=f'<text class="pm-t" x="{x+28}" y="{ty+i*14}">{e(t)}</text>'
 nl=lines(('? ' if p[5] else '')+note,19)
 for j,t in enumerate(nl):out+=f'<text class="pm-n{" pm-q" if p[5] else ""}" x="{x+28}" y="{ty+(len(txt)+j)*14}">{e(t)}</text>'
 return out,22+(len(txt)+len(nl))*14
def render(c,d):
 pts=POINTS[c];nums={id(p):i+1 for i,p in enumerate(pts)}
 rows={};order=[]
 for p in pts:
  if p[0] in('before','after'):
   k=key(p[1]);rows.setdefault(k,[]) or order.append(k);rows[k].append(p)
 extra=[p for p in pts if p[0] not in('before','after')]
 s=[];y=58
 # landside / airside orientation
 s.append(f'<text class="pm-side" x="{HALF[0]}" y="22">◀ CITY / CURBSIDE</text><text class="pm-side" x="{W-16}" y="22" text-anchor="end">GATES / AIRSIDE ▶</text>')
 s.append(f'<text class="pm-zone pm-zb" x="{(HALF[0]+HALF[1])//2}" y="44" text-anchor="middle">BEFORE SECURITY</text><text class="pm-zone pm-za" x="{(HALF[2]+HALF[3])//2}" y="44" text-anchor="middle">AFTER SECURITY</text>')
 top=y;body=[];link_y={}
 for k in order:
  b=[p for p in rows[k] if p[0]=='before'];a=[p for p in rows[k] if p[0]=='after']
  col={'b':[],'a':[]};hb=ha=0;yy=y+30
  for p in b:o,h=item(HALF[0]+4,yy+hb,nums[id(p)],p);col['b'].append(o);hb+=h
  for p in a:o,h=item(HALF[2]+4,yy+ha,nums[id(p)],p);col['a'].append(o);ha+=h
  if not b:col['b'].append(f'<text class="pm-n" x="{HALF[0]+10}" y="{yy+12}">No listed stop</text>');hb=24
  if not a:col['a'].append(f'<text class="pm-n" x="{HALF[2]+10}" y="{yy+12}">No listed stop</text>');ha=24
  h=30+max(hb,ha)+6
  body.append(f'<g class="pm-term"><rect class="pm-tb" x="8" y="{y}" width="{W-16}" height="{h}" rx="18"/><path class="pm-ta" d="M{W/2} {y}H{W-26}a18 18 0 0 1 18 18V{y+h-18}a18 18 0 0 1-18 18H{W/2}Z"/><rect class="pm-chip" x="14" y="{y+6}" width="{min(len(k)*8+16,W-28)}" height="20" rx="10"/><text class="pm-tn" x="22" y="{y+20}">{e(k)}</text>{"".join(col["b"])}{"".join(col["a"])}</g>')
  link_y[k]=(y,y+h);y+=h+(34 if c=='ICN' and k=='T1' else 14)
 s+=body
 bot=y-14
 s.append(f'<path class="pm-sec" d="M{W/2} 32V{bot+6}"/><text class="pm-sect" x="{W/2}" y="{bot+20}" text-anchor="middle">┆ SECURITY CHECKPOINT</text>')
 y=bot+36
 if c=='ICN':
  ks=[k for k in order if k=='T2'];k1=[k for k in order if k=='T1']
  if ks and k1:
   y1=link_y[k1[-1]][1];y2=link_y[ks[0]][0]
   s.append(f'<path class="pm-link" d="M60 {y1}V{y2}"/><text class="pm-q pm-n" x="70" y="{(y1+y2)/2+4}">T1 ⇅ T2 shuttle / AREX · ? verify on site</text>')
 for p in extra:
  o,h=item(18,y+8,nums[id(p)],p,True)
  s.append(f'<g class="pm-extra"><rect x="8" y="{y}" width="{W-16}" height="{h+4}" rx="12"/>{o}</g>');y+=h+14
 # vet: off plan, arrow pointing away
 vy=y+6
 if 'vet' in d:vt=['Nearest 24/7 vet (off airport)',d['vet'][0],'Not ranked · verify']
 else:vt=['Nearest 24/7 vet (off airport)','Not in our data:','ask airport staff']
 vl=textwrap.wrap(vt[1],17)[:2]+[vt[2]] if 'vet' in d else vt[1:]
 bh=30+len(vl)*13
 s.append(f'<path class="pm-arrow" d="M{W/2} {vy-6}V{vy+22}H{W-154}" marker-end="url(#pm-ah-{c})"/><g class="pm-vet"><rect x="{W-148}" y="{vy}" width="140" height="{bh}" rx="10"/><text class="pm-vi" x="{W-78}" y="{vy+19}" text-anchor="middle">✚ VET</text>'+''.join(f'<text class="pm-n" x="{W-78}" y="{vy+35+i*13}" text-anchor="middle">{e(t)}</text>' for i,t in enumerate(vl))+'</g>')
 s.append(f'<text class="pm-n" x="16" y="{vy+30}">Outside the airport</text>')
 H=vy+bh+10
 defs=f'<defs><marker id="pm-ah-{c}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10Z" class="pm-ahd"/></marker></defs>'
 svg=f'<svg class="pm-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="pm-t-{c} pm-d-{c}"><title id="pm-t-{c}">{c} pet map</title><desc id="pm-d-{c}">Simplified original diagram, not to scale: terminals as rows, city side left, gates right, dashed security line, numbered paw pins matching the legend. Dashed pins: verify on site.</desc>{defs}'+''.join(s)+'</svg>'
 leg=''
 for i,p in enumerate(pts,1):
  g,label,detail,note,src,unc=p;url=src or d['pets_url']
  grp={'before':'Before security','after':'After security','restricted':'Arrivals','access':'Status'}[g]
  leg+=f'<li class="{"pm-lu" if unc else ""}"><b class="pm-ln">{i}</b><span><strong>{e(label)}</strong> — {e(detail)} <em>({grp})</em><br><small>{"? " if unc else ""}{e(note)} · <a href="{e(url)}" target="_blank" rel="noopener noreferrer">source ↗</a></small></span></li>'
 caveat=f'<p class="airport-note">{e(d.get("note",""))}</p>' if d.get('note') else ''
 return f'''<section class="airport-panel petmap" id="pet-map" aria-labelledby="pm-h-{c}"><div class="airport-code">{c} · Pet map</div><h2 id="pm-h-{c}">Pet map</h2><p class="pm-disc">Simplified diagram, not to scale — check official airport signage</p><div class="pm-frame"><button type="button" class="pm-open" aria-haspopup="dialog" aria-label="Open the {c} pet map full screen">{svg}<span class="pm-fs">⤢ Full screen</span></button></div><div class="pm-key"><span><b class="pm-ln">1</b> Paw pin: listed pet stop</span><span><b class="pm-ln pm-lq">?</b> Dashed: verify on site</span><span><i class="pm-ks"></i> Security line</span></div><ol class="pm-legend">{leg}</ol>{caveat}<p class="pm-links"><a class="btn ghost" href="{e(MAPS[c])}" target="_blank" rel="noopener noreferrer">Official airport map ↗</a></p><p class="airport-meta">Original PetPolicyCheck drawing from the official written sources listed above, read 7 November 2026 (KST). Not traced from any airport map; positions are schematic.</p></section>'''
CSS='''
/* Pet map: original schematic */
.petmap{margin-top:22px}.petmap h2{margin:6px 0 4px}.pm-disc{font-size:.88rem;color:var(--mut)}.pm-frame{margin:12px auto 0;max-width:560px}.pm-open{all:unset;display:block;position:relative;width:100%;cursor:zoom-in;border-radius:16px;background:var(--bg);border:1px solid var(--line2);padding:6px;box-sizing:border-box}.pm-open:focus-visible{outline:3px solid var(--pri);outline-offset:3px}.pm-fs{display:block;width:max-content;margin:6px auto 4px;background:var(--pri);color:var(--on-pri);font:700 .78rem var(--text);padding:5px 9px;border-radius:20px}
.pm-svg{display:block;width:100%;height:auto;font-family:var(--text)}.pm-side{fill:var(--mut);font-size:12px;font-weight:700;letter-spacing:.04em}.pm-zone{font-size:12px;font-weight:700;letter-spacing:.06em}.pm-zb{fill:#9fd6a0}.pm-za{fill:var(--pri)}
.pm-tb{fill:rgba(159,214,160,.10);stroke:var(--line2);stroke-width:1.5}.pm-ta{fill:rgba(217,183,101,.13)}.pm-chip{fill:#11252a;stroke:var(--line2)}.pm-tn{fill:var(--head);font-size:13px;font-weight:700}.pm-t{fill:var(--ink);font-size:12px}.pm-n{fill:var(--mut);font-size:12px}.pm-q{fill:#f0a3a3}
.pm-pin circle{fill:var(--pri);stroke:#0b1719;stroke-width:1.5}.pm-pin text{fill:#0b1719;font-size:12px;font-weight:800}.pm-unc circle{fill:transparent;stroke:#f0a3a3;stroke-width:2;stroke-dasharray:4 3}.pm-unc text{fill:#f0a3a3}
.pm-sec{stroke:#f0a3a3;stroke-width:3;stroke-dasharray:8 6;fill:none}.pm-sect{fill:#f0a3a3;font-size:12px;font-weight:700}.pm-link{stroke:#f0a3a3;stroke-width:2.5;stroke-dasharray:4 4;fill:none}
.pm-extra rect{fill:none;stroke:#f0a3a3;stroke-dasharray:6 4}.pm-arrow{stroke:var(--mut);stroke-width:2;fill:none;stroke-dasharray:3 3}.pm-ahd{fill:var(--mut)}.pm-vet rect{fill:var(--paper);stroke:#9fd6a0;stroke-width:1.5}.pm-vi{fill:#9fd6a0;font-size:13px;font-weight:800}
.pm-key{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:.84rem;margin:12px 0 6px;color:var(--mut)}.pm-ln{display:inline-grid;place-items:center;min-width:24px;height:24px;border-radius:50%;background:var(--pri);color:var(--on-pri);font-size:.8rem;margin-right:6px;flex:none}.pm-lq,.pm-lu .pm-ln{background:transparent;color:#f0a3a3;border:2px dashed #f0a3a3}.pm-ks{display:inline-block;width:26px;border-top:3px dashed #f0a3a3;vertical-align:middle;margin-right:6px}
.pm-legend{list-style:none;padding:0;margin:8px 0;display:grid;gap:8px}.pm-legend li{display:flex;gap:4px;align-items:flex-start;font-size:.92rem}.pm-legend small{color:var(--mut)}.pm-links{margin-top:14px}@media(min-width:900px){.pm-legend{grid-template-columns:1fr 1fr}}
@media(max-width:500px){.petmap.airport-panel{padding:14px 10px}.pm-open{padding:2px}}
.pm-overlay{position:fixed;inset:0;z-index:1000;background:#071012;display:flex;flex-direction:column}.pm-overlay[hidden]{display:none}.pm-ohead{display:flex;justify-content:space-between;align-items:center;padding:10px 14px;color:var(--head)}.pm-close{font:700 1.6rem var(--text);width:48px;height:48px;border-radius:50%;border:1px solid var(--line2);background:var(--paper);color:var(--head);cursor:pointer}.pm-close:focus-visible{outline:3px solid var(--pri)}.pm-obody{flex:1;overflow:auto;padding:8px;touch-action:pan-x pan-y pinch-zoom;-webkit-overflow-scrolling:touch}.pm-obody svg{width:100%;min-width:340px;max-width:900px;margin:0 auto;display:block;height:auto}.pm-zoom{display:flex;gap:8px}.pm-zoom button{min-width:44px;height:44px;border-radius:10px;border:1px solid var(--line2);background:var(--paper);color:var(--head);font-weight:700;cursor:pointer}
'''
JS=r'''
/* Pet map full-screen overlay */
(function(){function init(){var b=document.querySelector('.pm-open');if(!b)return;var o=document.createElement('div');o.className='pm-overlay';o.hidden=true;o.setAttribute('role','dialog');o.setAttribute('aria-modal','true');o.setAttribute('aria-label','Pet map, full screen');o.innerHTML='<div class="pm-ohead"><strong>Pet map</strong><div class="pm-zoom"><button type="button" data-z="-1" aria-label="Zoom out">−</button><button type="button" data-z="1" aria-label="Zoom in">+</button><button type="button" class="pm-close" aria-label="Close full-screen map">×</button></div></div><div class="pm-obody"></div>';document.body.appendChild(o);var body=o.querySelector('.pm-obody'),close=o.querySelector('.pm-close'),z=1;
var svg=b.querySelector('svg').cloneNode(true);svg.querySelectorAll('[id]').forEach(function(n){n.id='fs-'+n.id});svg.setAttribute('aria-labelledby',svg.getAttribute('aria-labelledby').split(' ').map(function(x){return 'fs-'+x}).join(' '));svg.querySelectorAll('[marker-end]').forEach(function(n){n.setAttribute('marker-end',n.getAttribute('marker-end').replace('#','#fs-'))});body.appendChild(svg);
function setz(){svg.style.width=(100*z)+'%'}o.querySelectorAll('[data-z]').forEach(function(x){x.addEventListener('click',function(){z=Math.min(3,Math.max(1,z+0.5*x.getAttribute('data-z')));setz()})});
function open(){o.hidden=false;document.documentElement.style.overflow='hidden';close.focus()}function shut(){o.hidden=true;document.documentElement.style.overflow='';z=1;setz();b.focus()}
b.addEventListener('click',open);close.addEventListener('click',shut);o.addEventListener('keydown',function(ev){if(ev.key==='Escape'){shut()}if(ev.key==='Tab'){var f=o.querySelectorAll('button'),first=f[0],last=f[f.length-1];if(ev.shiftKey&&document.activeElement===first){ev.preventDefault();last.focus()}else if(!ev.shiftKey&&document.activeElement===last){ev.preventDefault();first.focus()}}})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init()}());
'''
