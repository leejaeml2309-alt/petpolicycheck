from pathlib import Path
import json,html
from diagrams import render as diagram
import petmap
B=Path(__file__).parent; S=B/'wt/site'; kit=json.loads(Path('/workspace/innov-12-20261106/#8-airport-qr-kit/airports-kit-targets.json').read_text())
D={c:kit[c] for c in ['AUS','BNA','PDX','SAN','BTV','YVR','YUL']}
def config(c,before,after,airlines,sources,note=''):
 D[c].update(before=before,after=after,airlines=airlines,airline_sources=sources,note=note,checked='2026-11-07 KST')
config('AUS',[['Barbara Jordan Terminal','Outside the lower level, at both ends of the parking garage.']],[['Barbara Jordan Terminal','Pet restroom after security near Gate 9.']],['air-canada','alaska','american','british-airways','delta','jetblue','lufthansa','southwest','united'],[['https://www.flyaustin.com/aus-airport-airlines-flights','AUS airline directory']])
D['BNA']['pets_url']='https://bnavisionnashville.com/2021/11/22/the-new-bna-bigger-better-even-friendlier-to-pets-and-service-animals/'
config('BNA',[['Terminal curbside & Garage 1','Curbside relief areas and a dog park on Level P5 of Terminal Garage 1, described in the airport’s November 2021 announcement. Ask airport staff for current access.']],[['Concourse D / satellite gates','The airport announcement lists Concourse D. American’s airport guide additionally lists relief areas across from Gate D2 and next to Gate T1. Ask airport staff to confirm current access from your concourse.']],['american'],[['https://www.aa.com/web/i18n/travelInformation/destinationInformation/bna-airport.html','American’s BNA airport guide']], 'The kit’s newer BNA pet page returned no readable content. The airport announcement is historical (2021); gate details are from American’s airport guide. For other concourses, ask airport staff.')
D['PDX']['pets_url']='https://flypdx.com/Animals'
config('PDX',[['Main terminal · lower level','Outside baggage claim at the south end of the terminal.']],[['Concourses B / C','Just past security near Stumptown Coffee.'],['Concourse D','Across from Gate D5.']],['air-canada','alaska','american','british-airways','delta','hawaiian','jetblue','southwest','united'],[['https://flypdx.com/airlines','PDX airline directory']])
config('SAN',[['Terminal 1 & Terminal 2','Outdoors on the Ground Transportation Plazas at both terminals.']],[['Terminal 1','Across from Gate 117.'],['Terminal 2','Near Gate 46.']],['air-canada','alaska','american','british-airways','delta','hawaiian','southwest','united'],[['https://www.san.org/airlines/','SAN airline directory'],['https://www.san.org/news-articles/who-moved-my-airline-is-it-terminal-1-or-terminal-2-east-or-west/','SAN terminal / airline information']])
config('BTV',[['Terminal','No before-security location confirmed from the amenities page; ask airport staff.']],[['Terminal','The official amenities page confirms indoor post-security relief areas, but does not specify gates or concourses. Ask airport staff for the closest one.']],['american','delta','united'],[['https://btv.aero/where-we-fly/','BTV airline directory']])
D['YVR']['pets_url']='https://www.yvr.ca/en/passengers/accessibility/animal-relief-areas'
config('YVR',[['Main terminal · International Arrivals','Outside International Arrivals at the entrance to Chester Johnson Park.'],['South Terminal','Across from the north entrance.']],[['Domestic A / B Pier','Across from the play area, before Starbucks.'],['Domestic C Pier','Across from Gate C29, in the alcove to the right of the washrooms.'],['International D Pier','Across from Gate D72, and between Gates 58 and 62.'],['International Arrivals · Level 4','In the corridor walkway and in the overflow queuing area.'],['USA E Pier','Near Gates E76 and E77.'],['South Terminal','Gate G1–2, by the vending machines in the corner.']],['air-canada','air-france','alaska','american','british-airways','delta','jetblue','korean-air','lufthansa','united'],[['https://www.yvr.ca/en/passengers/flights/airlines-and-destinations','YVR airline directory']])
D['YUL']['pets_url']='https://yulsatisfaction.admtl.com/hc/en-ca/articles/360001353657-Where-can-I-find-a-relief-area-for-my-pet'
D['YUL']['pets_fr']='https://yulsatisfaction.admtl.com/hc/fr-ca/articles/360001353657'
config('YUL',[['Public area · departures','Near Tracker, at departures level.'],['Public area · parking','At the P4 parking lot.']],[['Domestic pier','In front of Gate 47.'],['International pier','In front of the restrooms near Gate 65.'],['Transborder pier','In front of the restrooms near Gate 73.']],['air-canada','american'],[['https://www.aircanada.com/en-ca/flights-from-montreal','Air Canada’s Montréal service page'],['https://www.aa.com/web/i18n/travelInformation/destinationInformation/yul-airport.html','American’s YUL airport guide']], 'The YUL airline directory could not be read (bot protection). Only the two carriers independently confirmed on their own official pages are listed here.')
# Only clinics already present in site map data; never imply a global nearest ranking.
D['PDX']['vet']=['DoveLewis Emergency Animal Hospital','https://www.dovelewis.org/','site/assets/js/usa-map.js · OR|Portland']
D['YVR']['vet']=['Canada West Veterinary Specialists','https://canadawestvets.com/','site/assets/js/canada-map-data.js · YVR.vet']
D['YUL']['vet']=['CENTREDMVET Montréal','https://centredmvet.com/en/centre/centredmvet-montreal/','site/assets/js/canada-map-data.js · YUL.vet']
D['AUS']['hotels']=['Hotel Van Zandt, Fairmont Austin, The LINE Austin, South Congress Hotel and Hotel Saint Cecilia','hotels/pet-friendly-hotels-austin.html','Austin pet-friendly hotel guide','City hotels, not all airport-adjacent. See existing guide for individual restrictions and policy dates; confirm with the property.']
D['YVR']['hotels']=['Fairmont Hotel Vancouver','countries/canada.html','Canada hotel policy guide','Existing guide listing in Vancouver city, not the airport hotel. Confirm the property’s current pet policy.']
D['YUL']['hotels']=['Alt Hotels (YUL area)','countries/canada.html','Canada hotel policy guide','Existing guide lists Alt in the YUL area under its brand policy. Confirm the specific property and current pet policy.']
from wave_a import extend
extend(D,kit)
(S/'airport').mkdir(exist_ok=True); (S/'assets/css/airport-qr.css').write_text('''
.airport-main{max-width:1100px;padding-top:24px;padding-bottom:30px}.airport-hero{padding:24px 0 28px;border-bottom:1px solid var(--line)}.airport-hero h1{font-size:clamp(2.1rem,4vw,3.5rem);line-height:1.12;max-width:21ch;margin:12px 0}.airport-hero p{max-width:65ch}.airport-code{font:700 .82rem var(--text);letter-spacing:.14em;color:var(--pri);text-transform:uppercase}.airport-sub{font-size:1.08rem;color:var(--mut)}.airport-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px}.airport-layout{display:grid;gap:20px;margin-top:24px}.airport-panel{background:var(--paper);border:1px solid var(--line2);border-radius:var(--r-l);padding:24px;min-width:0}.airport-panel h2{font-size:1.65rem;line-height:1.2;margin-bottom:16px}.airport-panel h3{font:700 1rem var(--text);margin:14px 0 6px}.airport-panel p{margin:8px 0}.airport-zone{padding:15px 0;border-top:1px solid var(--line)}.airport-zone:last-child{padding-bottom:0}.airport-zone strong{display:block;color:var(--head)}.airport-tag{display:inline-block;border:1px solid var(--line2);padding:3px 9px;border-radius:30px;font-size:.75rem;color:var(--pri);margin:0 0 10px}.airport-meta{font-size:.8rem;color:var(--mut);margin-top:18px!important}.airport-note{border-left:3px solid var(--pri);padding:9px 12px;color:var(--mut);font-size:.9rem}.airport-airlines{display:flex;flex-wrap:wrap;gap:9px;list-style:none;padding:0;margin:16px 0}.airport-airlines a{display:block;padding:9px 13px;border:1px solid var(--line2);border-radius:6px;text-decoration:none;min-height:44px}.airport-airlines a:hover{border-color:var(--pri)}.airport-grid{display:grid;gap:18px;margin-top:25px}.airport-grid a{text-decoration:none;padding:24px;background:var(--paper);border:1px solid var(--line2);border-radius:var(--r-l)}.airport-grid strong{display:block;color:var(--pri);font-size:1.8rem}.airport-grid span{display:block;color:var(--ink)}.airport-back{font-size:.88rem}.airport-main a:focus-visible{outline:3px solid var(--pri);outline-offset:4px}.airport-panel a,.airport-meta a{overflow-wrap:anywhere}.airport-disclaimer{margin:28px 0 0;font-size:.9rem;color:var(--mut)}@media(min-width:850px){.airport-layout{grid-template-columns:1.25fr 1fr}.airport-relief{grid-row:span 2}.airport-grid{grid-template-columns:repeat(3,1fr)}}@media(max-width:500px){.airport-panel{padding:20px}.airport-hero{padding-top:14px}.airport-actions .btn{width:100%;justify-content:center}.airport-grid{grid-template-columns:1fr}.airport-hero h1{font-size:2.35rem}}
''')
with (S/'assets/css/airport-qr.css').open('a') as f: f.write('/* Original source-text schematics;'+' no airport floorplan geometry is reproduced. */\n.airport-diagram{margin-top:24px}.diagram-intro{max-width:75ch;margin-bottom:20px}.diagram-intro h2{margin:8px 0}.diagram-layout{display:grid;gap:28px;align-items:start}.airport-diagram-svg{display:block;width:100%;max-width:480px;height:auto;margin:0 auto;font:16px var(--text);color:var(--ink)}.diagram-region{fill:var(--bg);stroke:var(--line2)}.diagram-heading{fill:var(--pri);font:700 15px var(--text);letter-spacing:.04em}.diagram-point rect{fill:var(--paper);stroke:var(--line2)}.diagram-point circle{fill:var(--pri)}.diagram-point text{fill:var(--ink);font-size:16px}.diagram-point .diagram-marker{fill:var(--on-pri);font-weight:700}.diagram-point .diagram-label{fill:var(--head);font-weight:700}.diagram-point .diagram-detail{fill:var(--mut);font-size:15px}.diagram-uncertain rect{stroke:var(--pri);stroke-dasharray:5 4}.diagram-boundary{fill:none;stroke:var(--mut);stroke-dasharray:6 5}.airport-diagram-svg a:hover rect,.airport-diagram-svg a:focus rect{stroke:var(--pri);stroke-width:2}.diagram-legend{display:grid;gap:8px;font-size:.86rem;margin:14px 0}.diagram-legend>span{display:flex;align-items:center;gap:9px}.legend-dot{display:inline-grid;place-items:center;flex:0 0 24px;height:24px;border-radius:50%;background:var(--pri);color:var(--on-pri)}.legend-unknown{background:transparent;color:var(--pri);border:1px dashed var(--pri)}.legend-boundary{display:inline-block;width:24px;border-top:1px dashed var(--mut)}.diagram-sources ol{list-style:none;padding:0;margin:0}.diagram-sources li{margin:0 0 16px;font-size:.9rem}.diagram-sources h3{margin-top:0}.diagram-vet{padding:16px;border:1px solid var(--line2);border-radius:10px;margin-top:20px}.diagram-vet p{font-size:.9rem}.diagram-sources a{overflow-wrap:anywhere}@media(min-width:850px){.diagram-layout{grid-template-columns:minmax(0,1.1fr) minmax(0,1fr)}}@media(max-width:500px){.airport-diagram{padding:14px}.diagram-point text{font-size:16px}.diagram-point .diagram-detail{font-size:15px}}\n')
(S/'assets/js/airport-qr.js').write_text('''/* Airport QR pages: scoped preview-safe nav and UTM-only propagation. */
(function () {
  'use strict';
  function boot() {
    var root = new URL(document.documentElement.dataset.siteRoot, document.baseURI);
    // Shared pastilles builds root-relative navigation from pathname depth.
    // Rebase it to this site's root when previewed below a directory prefix.
    document.querySelectorAll('#site-menu a').forEach(function (a) {
      var href = a.getAttribute('href');
      if (href && !/^(?:[a-z]+:|\/\/)/i.test(href)) {
        a.href = new URL(href.replace(/^(?:\.\.\/)+/, ''), root).href;
      }
    });
    var incoming = new URLSearchParams(location.search);
    function propagate(a) {
      var href = a.getAttribute('href');
      if (!href || href[0] === '#') return;
      var url = new URL(href, document.baseURI);
      if (url.origin !== location.origin || !url.pathname.startsWith(root.pathname)) return;
      incoming.forEach(function (value, key) {
        if (/^utm_[a-z0-9_]+$/i.test(key)) url.searchParams.set(key, value);
      });
      a.href = url.href;
    }
    document.querySelectorAll('a[href]').forEach(propagate);
    document.addEventListener('click', function (event) {
      var a = event.target.closest && event.target.closest('a[href]');
      if (a) propagate(a);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
}());
''')
def e(x):return html.escape(x,quote=True)
def ext(url,label):return f'<a href="{e(url)}" rel="noopener noreferrer" target="_blank">{e(label)} ↗</a>'
def shell(title,body,depth,canonical):
 root='../'*depth
 return f'''<!doctype html><html lang="en" data-site-root="{root}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} | PetPolicyCheck</title><meta name="description" content="Airport pet relief locations, official sources, airline pet policies and existing local resources."><link rel="canonical" href="https://petpolicycheck.com/{canonical}"><link rel="stylesheet" href="{root}assets/css/theme.css"><link rel="stylesheet" href="{root}style.css"><link rel="stylesheet" href="{root}assets/css/airport-qr.css"><script src="{root}assets/js/pastilles.js" defer></script><script src="{root}assets/js/airport-qr.js" defer></script></head><body class="v-c"><a class="skip" href="#main">Skip to content</a><header class="top"><div class="wrap"><a class="brand" href="{root}" aria-label="PetPolicyCheck — Home"><span class="lbadge"><img src="{root}assets/img/logo-mark-header.png" width="62" height="48" alt="PetPolicyCheck"></span></a><nav class="nav menu" id="site-menu" aria-label="Main"></nav><button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-menu">Menu</button></div></header><main class="wrap airport-main" id="main">{body}<p class="airport-disclaimer">Not affiliated with any airline or airport. Locations and access can change; follow airport signage and ask airport staff if unsure.</p><p class="airport-meta scan-counts">Scan counts available on request</p></main><footer class="foot foot-compact"><div class="wrap"><p class="disc"><span data-i18n="site.foot.aff">As an Amazon Associate I earn from qualifying purchases.</span> &copy; 2026 PetPolicyCheck · Paw Passport. All rights reserved. Content, data, design and images may not be copied or reproduced without written permission. See <a href="{root}terms.html" data-i18n="site.foot.terms">Terms</a>.</p><p><a href="{root}terms.html">Terms</a> · <a href="{root}privacy.html">Privacy</a> · <a href="{root}airport/">Airport pet travel guides</a></p></div></footer></body></html>'''
labels={'air-canada':'Air Canada','alaska':'Alaska Airlines','american':'American Airlines','british-airways':'British Airways','delta':'Delta Air Lines','jetblue':'JetBlue','lufthansa':'Lufthansa','southwest':'Southwest','united':'United Airlines','air-france':'Air France','hawaiian':'Hawaiian Airlines','korean-air':'Korean Air'}
for c,d in D.items():
 root='../../'; areas=''; diagram(c,d);diagram_html=petmap.render(c,d)
 for k,label in [('before','Before security'),('after','After security')]:
  areas+=f'<h3><span class="airport-tag">{label}</span></h3>'
  for terminal,where in d[k]:areas+=f'<div class="airport-zone"><strong>{e(terminal)}</strong><p>{e(where)}</p></div>'
 source=ext(d['pets_url'],'Official airport relief information')
 if 'pets_fr' in d:source+=' · '+ext(d['pets_fr'],'Official information in French')
 areas+=f'<p class="airport-meta">{source}<br>{e(d.get("check_label","Source read"))}: <time datetime="2026-11-07">7 November 2026 (KST)</time>. Not an on-site inspection.</p>'
 if d['note']:areas+=f'<p class="airport-note">{e(d["note"])}</p>'
 airline_links=''.join(f'<li><a href="{root}airlines/{a}.html">{labels[a]}</a></li>' for a in d['airlines'])
 airline_sources=' · '.join(ext(*src) for src in d['airline_sources'])
 if 'vet' in d:
  name,url,record=d['vet'];vet=f'<p><strong>{e(name)}</strong></p><p>{ext(url,"24/7 emergency care — official clinic site")}</p><p class="airport-meta">Already listed in our {"Canada" if c.startswith("Y") else "USA"} map data; 24/7 service confirmed on the clinic website on 7 November 2026 (KST).</p><p class="airport-note">This is an existing map listing, not a verified nearest-clinic ranking. Confirm travel time and availability directly. For the closest current option, ask airport staff.</p>'
 else:vet='<p>No local 24/7 emergency vet could be confirmed from our existing map records. For help finding the nearest available clinic, ask airport staff.</p>'
 if 'hotels' in d:
  names,guide,label,note=d['hotels'];hotels=f'<p>{e(names)}.</p><p><a href="{root}{guide}">{e(label)} →</a></p><p class="airport-meta">{e(note)} No live room availability is provided.</p>'
 else:hotels='<p>We do not yet have a city-specific hotel listing in our existing guides for this airport. For local pet-friendly options, ask airport staff and confirm directly with the hotel.</p>'
 body=f'''<a class="airport-back" href="../">← All airport guides</a><section class="airport-hero"><div class="airport-code">{c} · {e(d['city'])} · Airport pet travel</div><h1>A calmer connection,<br>with your pet.</h1><p class="airport-sub">{e(d['name'])}. Find a relief stop, check your airline’s rules, and plan your next step.</p><div class="airport-actions"><a class="btn" href="#pet-map">Open the pet map</a><a class="btn ghost" href="{root}airlines/compare/">Compare airline pet rules</a></div></section>{diagram_html}<div class="airport-layout"><section class="airport-panel airport-relief" id="relief"><h2>Pet relief areas</h2>{areas}</section><section class="airport-panel"><h2>Your airline’s pet rules</h2><p>Selected airlines serving {c} with an existing PetPolicyCheck policy page. This is not a complete airline directory; service may be seasonal.</p><ul class="airport-airlines">{airline_links}</ul><p class="airport-meta">Service sources: {airline_sources}<br>Sources read: 7 November 2026 (KST). Terminal assignments and flight schedules can change.</p></section><section class="airport-panel"><h2>24/7 veterinary help</h2>{vet}</section><section class="airport-panel"><h2>Pet-friendly stays</h2>{hotels}</section></div>'''
 p=S/'airport'/c;p.mkdir(exist_ok=True);(p/'index.html').write_text(shell(f'{c} airport pet travel guide',body,2,f'airport/{c}/'))
links=''.join(f'<a href="{c}/"><strong>{c}</strong><span>{e(d["city"])}</span><small>{e(d["name"])}</small></a>' for c,d in D.items())
(S/'airport/index.html').write_text(shell('Airport pet travel guides',f'<section class="airport-hero"><div class="airport-code">Airport pet travel</div><h1>One airport.<br>A clearer next step.</h1><p class="airport-sub">Pet relief areas, airline pet rules and existing local resources — with official sources and honest gaps.</p></section><div class="airport-grid">{links}</div>',1,'airport/'))
(B/'airports.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
P=B/'wt/docs/airport-qr';P.mkdir(parents=True,exist_ok=True);(P/'sources.json').write_text(json.dumps(D,ensure_ascii=False,indent=2))
with (S/'assets/css/airport-qr.css').open('a') as f:f.write(petmap.CSS)
with (S/'assets/js/airport-qr.js').open('a') as f:f.write(petmap.JS)
print(str(len(D)+1)+' airport pages generated')
