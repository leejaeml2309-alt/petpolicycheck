/* PetPolicyCheck · shared Canada/Mexico pet-travel map engine (Option B).
   Expects window.PPC_MAP = { geo, airports, data, accent, idRoot }
   Loaded after *-map-geo.js and *-map-data.js. English by default. */
(function(){
const CFG = window.PPC_MAP; if(!CFG) return;
const GEO = CFG.geo, AIRPORTS = CFG.airports || [], DATA = CFG.data, ACCENT = CFG.accent || 'maple';
const ROOT = CFG.idRoot || 'country-map';
const SITE = '..';
const $ = s => document.querySelector(s);
const esc = s => String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const enc = encodeURIComponent;
const ABBRS = Object.keys(GEO).sort((a,b)=>GEO[a].name.localeCompare(GEO[b].name));
const PLANE = 'M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5z';
const TAG = {aff:'Affiliate',off:'Official',srch:'Search',stub:'Stub'};
function lk(ic,title,sub,href,tag){
  if(!href) return `<span class="lk stub"><span class="ic" aria-hidden="true">${ic}</span><span class="t">${esc(title)}${sub?`<small>${esc(sub)}</small>`:''}</span><span class="tag stub">${TAG.stub}</span></span>`;
  return `<a class="lk" href="${esc(href)}" target="_blank" rel="${tag==='aff'?'sponsored nofollow noopener':'noopener'}"><span class="ic" aria-hidden="true">${ic}</span><span class="t">${esc(title)}${sub?`<small>${esc(sub)}</small>`:''}</span><span class="tag ${tag}">${TAG[tag]||TAG.off}</span></a>`;
}
const expHotels = q => `https://www.expedia.com/Hotel-Search?destination=${enc(q)}&amenities=PETS`;
const bkgHotels = q => `https://www.booking.com/searchresults.html?ss=${enc(q)}&nflt=hotelfacility%3D4`;
function honest(v, fallback){
  if(v==null || v==='' || v===false) return fallback || 'Not published on official page — confirm directly';
  return v;
}
function el(tag, attrs){
  const n = document.createElementNS('http://www.w3.org/2000/svg', tag);
  for(const k in attrs){ if(attrs[k]!=null) n.setAttribute(k, attrs[k]); }
  return n;
}

/* ---------- map switcher accent tabs ---------- */
function buildSwitcher(){
  const host = document.getElementById('map-switch');
  if(!host) return;
  const tabs = [
    {id:'usa', href:'usa-map.html', label:'USA Map', accent:'usa'},
    {id:'ca', href:'canada-map.html', label:'Canada Map', accent:'maple'},
    {id:'mx', href:'mexico-map.html', label:'Mexico Map', accent:'mxgreen'}
  ];
  const cur = DATA.country === 'CA' ? 'ca' : (DATA.country === 'MX' ? 'mx' : 'usa');
  const back = `<a class="msw-tab world-back" href="../#map" style="touch-action:manipulation;position:relative;z-index:5"><i aria-hidden="true"></i><span>← World Map</span></a>`;
  host.innerHTML = back + tabs.map(t =>
    `<a class="msw-tab accent-${t.accent}${t.id===cur?' is-current':''}" href="${t.href}"${t.id===cur?' aria-current="page"':''} style="touch-action:manipulation;position:relative;z-index:5"><i aria-hidden="true"></i><span>${t.label}</span></a>`
  ).join('');
}

/* ---------- draw ---------- */
function buildMap(){
  const gs = $('#g-st'), gl = $('#g-lb'), gc = $('#g-ct');
  if(!gs) return;
  gs.innerHTML = gl.innerHTML = gc.innerHTML = '';
  const hubCodes = new Set();
  if(DATA.provHub) Object.values(DATA.provHub).forEach(c => hubCodes.add(c));
  if(DATA.stateHub) Object.values(DATA.stateHub).forEach(c => hubCodes.add(c));
  const hubRegions = new Set();
  AIRPORTS.forEach(a => hubRegions.add(a.province || a.state));
  const alertSet = new Set(DATA.alertStates || []);
  const specialSet = new Set(Object.keys(DATA.special || {}));

  for(const a of ABBRS){
    const g = GEO[a];
    const cls = ['st'];
    if(specialSet.has(a) || alertSet.has(a)) cls.push('rule');
    if(hubRegions.has(a)) cls.push('hub');
    const p = el('path', {id:'s-'+a, class:cls.join(' '), d:g.d, role:'button', tabindex:'0', 'aria-label':g.name, 'data-a':a});
    p.addEventListener('click', e => { e.stopPropagation(); selectRegion(a); });
    p.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' '){ e.preventDefault(); selectRegion(a); }});
    gs.appendChild(p);
    if(g.c){
      const t = el('text', {id:'l-'+a, class:'lbl', x:g.c[0], y:g.c[1]});
      t.textContent = a; gl.appendChild(t);
    }
  }
  for(const a of ABBRS){
    for(const c of (GEO[a].cities||[])){
      const g = el('g', {class:'ct'+(c.cap?' cap':'')+(c.sample?' sample':''), role:'button', tabindex:'0', 'data-s':a, 'data-k':a+'|'+c.n, 'aria-label':c.n+', '+GEO[a].name});
      g.appendChild(el('circle', {cx:c.x, cy:c.y, r:c.sample?5:3}));
      if(c.sample) g.appendChild(el('circle', {class:'ring', cx:c.x, cy:c.y, r:8.5}));
      const right = c.x < 880;
      const tx = el('text', {x:c.x+(right?8:-8), y:c.y+3.5, 'text-anchor':right?'start':'end'});
      tx.textContent = c.n; g.appendChild(tx);
      g.addEventListener('click', e => { e.stopPropagation(); selectRegion(a, c.n); });
      gc.appendChild(g);
    }
  }
  buildAirports();
  const pick = $('#pick');
  if(pick){
    pick.innerHTML = `<option value="">Choose a ${DATA.unit}…</option>` +
      ABBRS.map(a => `<option value="${a}">${esc(GEO[a].name)} (${a})</option>`).join('');
    pick.onchange = () => { if(pick.value) selectRegion(pick.value); else resetAll(); };
  }
  buildPortalGrid();
}

function buildAirports(){
  let ga = $('#g-ap'); if(!ga){ ga = el('g',{id:'g-ap'}); $('#map').appendChild(ga); }
  ga.innerHTML = '';
  for(const ap of AIRPORTS){
    const region = ap.province || ap.state;
    const city = (GEO[region]&&GEO[region].cities||[]).find(c => c.n === ap.city) || (GEO[region]&&GEO[region].cities||[])[0];
    if(city){
      ga.appendChild(el('line', {class:'ap-link', x1:city.x, y1:city.y, x2:ap.x, y2:ap.y, 'data-region':region, 'data-code':ap.code}));
    }
    const g = el('g', {class:'ap', role:'button', tabindex:'0', 'data-code':ap.code, 'data-region':region, 'aria-label':ap.code+', '+ap.city});
    g.appendChild(el('rect', {class:'pad', x:-8, y:-8, width:16, height:16, rx:2, transform:'rotate(45)'}));
    g.appendChild(el('path', {class:'glyph', d:PLANE, transform:'translate(-6.2,-6.2) scale(.52)'}));
    g.setAttribute('transform', `translate(${ap.x} ${ap.y})`);
    const tx = el('text', {x:0, y:14, 'text-anchor':'middle'}); tx.textContent = ap.code; g.appendChild(tx);
    const tt = el('title',{}); tt.textContent = `${ap.code} — ${ap.city}`; g.appendChild(tt);
    g.addEventListener('click', e => { e.stopPropagation(); selectAirport(ap.code); });
    g.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' '){ e.preventDefault(); selectAirport(ap.code); }});
    ga.appendChild(g);
  }
}

function buildPortalGrid(){
  const grid = $('#grid'); if(!grid) return;
  grid.innerHTML = ABBRS.map(a => {
    const special = DATA.special && DATA.special[a];
    const hub = (DATA.provHub&&DATA.provHub[a]) || (DATA.stateHub&&DATA.stateHub[a]);
    return `<button type="button" data-a="${a}" class="${special?'rule':''}${hub?' hub':''}"><b>${a}</b><span>${esc(GEO[a].name)}</span>${special?'<em>Alert</em>':''}${hub?`<em class="hub">${hub}</em>`:''}</button>`;
  }).join('');
  grid.querySelectorAll('button').forEach(b => b.onclick = () => selectRegion(b.dataset.a));
}

/* ---------- panel content ---------- */
let step = 1, cur = null;
function header(a, title, sub){
  const P = window.PPC_PST ? PPC_PST('map','pst-ph') : '';
  return `<div class="ph theme-map accent-head"><div class="mark">${esc(a)}</div><div><div class="ph-eye">${P}<span>${esc(DATA.name)} map · ${esc(DATA.unit)} panel</span></div><h2>${esc(title)}</h2><div class="sub">${sub}</div></div></div>`;
}
function dogsCatsBlock(){
  const d = DATA.dogs||{}, c = DATA.cats||{};
  return `<dl class="kv">
    <dt>Dogs — rabies</dt><dd>${esc(honest(d.rabies_vaccine))}</dd>
    <dt>Dogs — health cert / CVI</dt><dd>${esc(honest(d.health_certificate_cvi))}</dd>
    <dt>Dogs — microchip</dt><dd>${esc(honest(d.microchip))}</dd>
    <dt>Dogs — permit / form</dt><dd>${esc(honest(d.import_permit_or_form))}</dd>
    <dt>Cats — rabies</dt><dd>${esc(honest(c.rabies_vaccine))}</dd>
    <dt>Cats — health cert</dt><dd>${esc(honest(c.health_certificate_cvi))}</dd>
  </dl>` +
  ((d.special_notes||[]).map(n=>`<p class="note">${esc(n)}</p>`).join('')) +
  ((c.special_notes||[]).map(n=>`<p class="note">${esc(n)}</p>`).join(''));
}
function breedBlock(a){
  const b = DATA.breeds||{};
  let s = `<h4>Breed rules</h4><p>${esc(honest(b.national, 'No federal breed ban found.'))}</p>`;
  const sub = (b.subnational||[]).filter(x => !a || (x.jurisdiction||'').toLowerCase().includes((GEO[a]?GEO[a].name:'').toLowerCase().split(' ')[0]) || (a==='ON'&&/ontario/i.test(x.jurisdiction)) || (a==='MB'&&/winnipeg/i.test(x.jurisdiction)));
  const list = a ? sub : (b.subnational||[]);
  if(list.length){
    s += list.map(x => `<div class="stubbox alert"><b>${esc(x.jurisdiction)}</b><p>${esc(x.rule)}</p>${x.source?lk('📜','Official source','',x.source,'off'):''}</div>`).join('');
  } else if(DATA.special && DATA.special[a]){
    const sp = DATA.special[a];
    s += `<div class="stubbox alert"><b>${esc(sp.title)}</b><p>${esc(sp.rule)}</p>${lk('📜','Official source','',sp.src,'off')}</div>`;
  }
  return s;
}
function hubForRegion(a){
  const code = (DATA.provHub&&DATA.provHub[a]) || (DATA.stateHub&&DATA.stateHub[a]);
  const hubs = [];
  if(code && DATA.hubs[code]) hubs.push(DATA.hubs[code]);
  // Jalisco also has PVR
  if(a==='JAL' && DATA.hubs.PVR) hubs.push(DATA.hubs.PVR);
  return hubs;
}
function vetCard(hub){
  const v = hub && hub.vet;
  if(!v || !v.name) return `<div class="stubbox"><b>Vet:</b> Not published on official page — confirm directly. ${hub&&hub.city?esc(hub.city):''}</div>`;
  return `<div class="links">${lk('🩺', v.name, honest(v.note, v.city||''), v.url, v.url?'off':'stub')}</div>`;
}
function lawSection(a){
  const nm = GEO[a]?GEO[a].name:a;
  let s = `<section class="sec" data-sec="1"><h3><span class="n">1</span>Vet + laws</h3>`;
  s += `<h4>${esc(DATA.authority)}</h4>`;
  s += `<div class="links">${lk('🏛', DATA.name+' official pet-entry page', 'Checked '+DATA.lastChecked, DATA.officialUrl, 'off')}</div>`;
  s += dogsCatsBlock();
  s += breedBlock(a);
  s += `<h4>Return to the US</h4><p>${esc(DATA.returnToUs)}</p>`;
  const hubs = hubForRegion(a);
  if(hubs.length){
    s += `<h4>Verified clinic near ${esc(nm)}</h4>` + hubs.map(vetCard).join('');
  } else {
    s += `<h4>Clinic</h4><div class="stubbox">No verified clinic listed for this ${DATA.unit} yet — confirm with a local licensed vet.</div>`;
  }
  s += `<p class="disc">Full reference: <a href="${DATA.guideUrl}">${esc(DATA.name)} pet-travel guide</a>. Not legal or veterinary advice.</p></section>`;
  return s;
}
function roadSection(a){
  let s = `<section class="sec" data-sec="2"><h3><span class="n">2</span>Road / rail</h3>`;
  if(DATA.rail && DATA.rail.via_rail){
    s += `<h4>VIA Rail</h4><p>${esc(DATA.rail.via_rail.rule)}</p><div class="links">${lk('🚆','VIA Rail: travelling with pets','',DATA.rail.via_rail.url,'off')}</div>`;
  }
  if(DATA.rail && DATA.rail.uber_pet){
    s += `<h4>Rides</h4><div class="links">${lk('🚗','Uber Pet (Canada)','',DATA.rail.uber_pet.url,'off')}</div><p>${esc(DATA.rail.uber_pet.rule)}</p>`;
  }
  if(DATA.country==='MX'){
    s += `<h4>Ground transport</h4><p>SENASICA OISA inspection happens on arrival before you leave the airport. Rideshare pet acceptance varies by driver — confirm in the app. Hotel-zone taxis: confirm pets when you book.</p>`;
  }
  const hubs = hubForRegion(a);
  hubs.forEach(h => {
    if(h.transit) s += `<h4>${esc(h.city)} local transit</h4><p>${esc(h.transit)}</p>`;
  });
  if(!hubs.length) s += `<div class="stubbox">Local transit pet rules for this ${DATA.unit} are not published on this map yet — confirm directly.</div>`;
  return s + `</section>`;
}
function planeSection(a, apCode){
  let s = `<section class="sec" data-sec="3"><h3><span class="n">3</span>Plane</h3>`;
  s += `<p>Book your pet&rsquo;s in-cabin or cargo spot directly with the airline. Pet space per flight is limited.</p>`;
  const hubs = apCode ? [DATA.hubs[apCode]].filter(Boolean) : hubForRegion(a);
  const list = apCode ? AIRPORTS.filter(x=>x.code===apCode) : AIRPORTS.filter(x => (x.province||x.state)===a);
  if(list.length){
    s += `<h4>Airports</h4><div class="citylist">${list.map(ap=>`<button type="button" class="apbtn" data-ap="${esc(ap.code)}">${esc(ap.code)} — ${esc(ap.city)}</button>`).join('')}</div>`;
  }
  hubs.forEach(h => {
    s += `<h4>${esc(h.iata)} · ${esc(h.name)}</h4><div class="links">${lk('🛫', h.name+' official site','',h.site,'off')}`;
    if(h.relief_url) s += lk('🐾','Pet relief areas', honest(h.relief_note,''), h.relief_url, 'off');
    s += `</div>`;
    if(!h.relief_url && h.relief_note) s += `<div class="stubbox">${esc(h.relief_note)}</div>`;
  });
  if(!hubs.length) s += `<div class="stubbox">No verified airport hub for this ${DATA.unit} on this map yet.</div>`;
  s += `<div class="links">${lk('🧳','Airline pet policies','Cabin, fees, hold','../#compare','off').replace('Official','Site').replace(' target="_blank"','')}</div></section>`;
  return s;
}
function hotelSection(a){
  let s = `<section class="sec" data-sec="4"><h3><span class="n">4</span>Hotel</h3>`;
  if(DATA.hotels && DATA.hotels.chains){
    s += `<h4>Verified Canadian chains</h4><div class="links">` +
      DATA.hotels.chains.map(c => lk('🏨', c.chain, c.policy, c.url, 'off')).join('') + `</div>`;
  }
  const hubs = hubForRegion(a);
  const q = hubs[0] && hubs[0].hotel_q ? hubs[0].hotel_q : ((GEO[a]?GEO[a].name:a)+' pet friendly hotels');
  s += `<div class="links">${lk('🏨','Pet-friendly hotels on Expedia', q, expHotels(q),'srch')}${lk('🛏','Pet-friendly stays on Booking.com', q, bkgHotels(q),'srch')}</div>`;
  s += `<p class="disc">Search links are plain search URLs. Confirm the property&rsquo;s pet fee and weight limit before you book.</p></section>`;
  return s;
}
function groomSection(a){
  let s = `<section class="sec" data-sec="5"><h3><span class="n">5</span>Grooming</h3>`;
  if(DATA.groomingNote){
    s += `<p>${esc(DATA.groomingNote.culture_note||'')}</p>`;
    if(DATA.groomingNote.international_docs_warning) s += `<div class="stubbox alert"><b>Vaccine docs:</b> ${esc(DATA.groomingNote.international_docs_warning)}</div>`;
  }
  const hubs = hubForRegion(a);
  let any = false;
  hubs.forEach(h => {
    (h.grooming||[]).forEach(g => {
      any = true;
      const bits = [];
      if(g.mobile_hotel) bits.push('Mobile / hotel-friendly');
      if(g.cats) bits.push('Cats accepted');
      if(g.vaccines && g.vaccines.length) bits.push('Vaccines: '+g.vaccines.join('; '));
      if(g.note) bits.push(g.note);
      s += `<div class="links">${lk('✂️', g.name, (bits.join(' · ')||g.city||''), g.url, g.url?'off':'stub')}</div>`;
    });
    if(!(h.grooming||[]).length && h.grooming_q){
      s += `<div class="stubbox">No verified salon listed for ${esc(h.city)} yet. Search: <em>${esc(h.grooming_q)}</em> — and call ahead about vaccine papers.</div>`;
    }
  });
  if(!hubs.length && !any) s += `<div class="stubbox">No verified salon for this ${DATA.unit} on this map yet.</div>`;
  s += `<p class="disc">Also see the <a href="../grooming/">Grooming directory</a>.</p></section>`;
  return s;
}

function hilite(a, apCode){
  document.querySelectorAll('.st.sel,.lbl.sel,.ct.sel,.ap.sel').forEach(e=>e.classList.remove('sel'));
  document.querySelectorAll('#grid button.sel').forEach(e=>e.classList.remove('sel'));
  if(a){ $('#s-'+a)?.classList.add('sel'); $('#l-'+a)?.classList.add('sel'); document.querySelector(`#grid button[data-a="${a}"]`)?.classList.add('sel'); }
  document.querySelectorAll('.ap,.ap-link').forEach(el=>{
    const mine = !a || el.dataset.region===a;
    el.classList.toggle('dim', !!a && !mine);
    el.classList.toggle('hot', !!a && mine);
  });
  if(apCode) document.querySelector(`.ap[data-code="${CSS.escape(apCode)}"]`)?.classList.add('sel');
  const pick = $('#pick'); if(pick) pick.value = a||'';
  const reset = $('#reset'); if(reset) reset.hidden = !a;
  zoomTo(a);
}

/* ---------- view box: zoomTo (region select on phones) + free zoom/pan (mirrors usa-map.js) ---------- */
const FULL=[0,0,975,610],MAXZ=8,MINW=975/MAXZ;let vb=FULL.slice(),animId=0;
function clampVB(v){const w=Math.min(975,Math.max(MINW,v[2])),h=w*610/975;
 const cx=v[0]+v[2]/2,cy=v[1]+v[3]/2;let x=cx-w/2,y=cy-h/2;
 x=Math.max(0,Math.min(975-w,x));y=Math.max(0,Math.min(610-h,y));return [x,y,w,h]}
function applyViewBox(v){vb=v.slice();const m=$('#map');if(!m)return;
 const k=vb[2]/975;m.setAttribute('viewBox',vb.map(n=>+n.toFixed(2)).join(' '));m.style.setProperty('--k',k.toFixed(3));m.style.setProperty('--kt',Math.sqrt(k).toFixed(3));
 m.querySelectorAll('#g-ap .ap').forEach(g=>{const b=g.dataset.at||(g.dataset.at=g.getAttribute('transform'));g.setAttribute('transform',k>0.999?b:b+' scale('+k.toFixed(4)+')');});
 syncZoomUI()}
function isFull(){return vb[2]>=974.5}
function syncZoomUI(){const m=$('#map');if(!m)return;const full=isFull();m.classList.toggle('is-zoomed',!full);
 const zi=$('#zin'),zo=$('#zout'),zr=$('#zreset');
 if(zi)zi.disabled=vb[2]<=MINW+0.5;if(zo)zo.disabled=full;if(zr)zr.disabled=full}
function stopAnim(){if(animId){cancelAnimationFrame(animId);animId=0}}
function animateTo(t,ms){stopAnim();t=clampVB(t);const f=vb.slice(),t0=performance.now();ms=ms||350;
 (function an(n){const k=Math.min(1,(n-t0)/ms),e=k*(2-k);applyViewBox(f.map((v,i)=>v+(t[i]-v)*e));animId=k<1?requestAnimationFrame(an):0})(t0)}
/* Phones (<=900): zoom into the selected region. Desktop keeps free-zoom unless clearing selection. */
function zoomTo(a){let t=null;
 if(a&&innerWidth<=900){const node=$('#s-'+a);if(node){const b=node.getBBox();const w=Math.max(b.width*1.5,220),h=Math.max(b.height*1.5,150);const sc=Math.max(w/975,h/610);const W=975*sc,H=610*sc;t=[b.x+b.width/2-W/2,b.y+b.height/2-H/2,W,H];}}
 else if(!cur)t=FULL;
 if(t)animateTo(t,350)}
function zoomAt(px,py,f,ms){const w=Math.min(975,Math.max(MINW,vb[2]/f)),s=w/vb[2];
 const t=[px-(px-vb[0])*s,py-(py-vb[1])*s,w,w*610/975];if(ms)animateTo(t,ms);else{stopAnim();applyViewBox(clampVB(t))}}

function render(html){
  const p=$('#panel'); p.innerHTML=html; p.scrollTop=0; applyStep(false);
  p.querySelectorAll('[data-ap]').forEach(b=>b.onclick=()=>selectAirport(b.dataset.ap));
  if(innerWidth<=900&&cur)p.scrollIntoView({behavior:'smooth',block:'start'});
}
function applyStep(scroll){
  document.querySelectorAll('#steps button').forEach(b=>b.setAttribute('aria-pressed', String(+b.dataset.step===step)));
  const secs=document.querySelectorAll('#panel .sec');
  secs.forEach(s=>{
    s.classList.toggle('focus', +s.dataset.sec===step);
    s.classList.toggle('active', +s.dataset.sec===step);
  });
  if(scroll){
    const t=document.querySelector(`#panel .sec[data-sec="${step}"]`);
    if(t){
      const p=$('#panel');
      if(innerWidth>900 && p){
        p.scrollTo({top:p.scrollTop+t.getBoundingClientRect().top-p.getBoundingClientRect().top-6,behavior:'smooth'});
      } else {
        t.scrollIntoView({behavior:'smooth',block:'start'});
      }
    }
  }
}
function selectRegion(a, city){
  cur={a,city}; hilite(a);
  const s=GEO[a];
  const hubs=hubForRegion(a);
  const hubNote = hubs.length ? ` · hub ${hubs.map(h=>h.iata).join(', ')}` : '';
  render(header(a, s.name, `${a} · ${DATA.unit}${hubNote}`) +
    lawSection(a)+roadSection(a)+planeSection(a)+hotelSection(a)+groomSection(a));
}
function selectAirport(code){
  const ap = AIRPORTS.find(x=>x.code===code); if(!ap) return;
  const a = ap.province || ap.state;
  cur={a,ap:code}; hilite(a, code);
  render(header(code, ap.city+' · '+code, `${GEO[a]?GEO[a].name:a} · airport hub`) +
    lawSection(a)+roadSection(a)+planeSection(a, code)+hotelSection(a)+groomSection(a));
}
function resetAll(){ cur=null; hilite(null); render(welcome()); }
function welcome(){
  return `<div class="ph theme-map accent-head"><div class="mark">${esc(DATA.country)}</div><div><div class="ph-eye"><span>${esc(DATA.name)} pet-travel map</span></div><h2>Pick a ${esc(DATA.unit)}</h2><div class="sub">${esc(DATA.unitPlural)} · verified ${esc(DATA.lastChecked)}</div></div></div>
    <p>Click a region or airport, or use the dropdown. Plan in order: vet and laws, road or rail, plane, hotel, grooming.</p>
    <div class="links">${lk('🏛', DATA.authority, 'Official authority', DATA.officialUrl, 'off')}${lk('📜', 'Full '+DATA.name+' guide', 'Federal rules + hubs', DATA.guideUrl, 'off').replace(' target="_blank"','').replace('Official','Site')}</div>
    <section class="sec active focus" data-sec="1"><h3><span class="n">1</span>Federal snapshot</h3>${dogsCatsBlock()}${breedBlock(null)}<h4>Return to the US</h4><p>${esc(DATA.returnToUs)}</p></section>`;
}

/* Default hub region when a journey step is pressed with nothing selected (mirrors USA → NYC). */
function defaultRegion(){
  if(DATA.country==='CA') return 'ON';
  if(DATA.country==='MX') return 'CMX';
  const hubs = DATA.provHub || DATA.stateHub || {};
  return Object.keys(hubs)[0] || ABBRS[0];
}

/* ---------- steps + free zoom/pan + init ---------- */
function initSteps(){
  document.querySelectorAll('#steps button').forEach(b=>{
    b.addEventListener('click',()=>{
      step=+b.dataset.step;
      /* Root-cause fix: without a selection the welcome panel only has sec 1, so steps 2–5
         had nothing to scroll to and felt dead. USA auto-selects NYC; we auto-select the
         primary hub region, then scroll/highlight the matching journey section. */
      if(!cur) selectRegion(defaultRegion());
      applyStep(true);
    });
  });
  const reset=$('#reset'); if(reset) reset.onclick=resetAll;
}

/* Free zoom & pan — same UX as usa-map.js (wheel, drag, pinch, sideways pan, +/−/reset). */
function initFreeZoom(){const m=$('#map');if(!m)return;
 let wrap=m.parentNode;if(!wrap.classList.contains('mapwrap')){wrap=document.createElement('div');wrap.className='mapwrap';m.parentNode.insertBefore(wrap,m);wrap.appendChild(m)}
 /* Country-specific empty-space placement: CA Pacific SW, MX Pacific SW (desktop). Mobile: under map. */
 wrap.classList.add('zoom-pos-'+(DATA.country==='MX'?'mx':'ca'));
 if(!$('#zin')){const z=document.createElement('div');z.className='zoom';z.setAttribute('role','group');z.setAttribute('aria-label','Map zoom');
  z.innerHTML='<button type="button" id="zin" aria-label="Zoom in" title="Zoom in">+</button><button type="button" id="zout" aria-label="Zoom out" title="Zoom out">&minus;</button><button type="button" id="zreset" aria-label="Reset map view" title="Reset map view">&#8634;</button>';
  wrap.appendChild(z)}
 const ctr=()=>[vb[0]+vb[2]/2,vb[1]+vb[3]/2];
 $('#zin').onclick=()=>{const c=ctr();zoomAt(c[0],c[1],1.6,250)};
 $('#zout').onclick=()=>{const c=ctr();zoomAt(c[0],c[1],1/1.6,250)};
 $('#zreset').onclick=()=>animateTo(FULL,300);
 const note=document.querySelector('#country-map .mapnote');
 if(note&&!note.querySelector('.mhint')){note.insertAdjacentHTML('afterbegin','<span class="mhint">Pinch with two fingers to zoom, swipe sideways to move the map. </span><span class="dhint">Scroll over the map to zoom, drag to move. </span>')}
 syncZoomUI();
 const toSVG=(cx,cy)=>{const r=m.getBoundingClientRect();return [vb[0]+(cx-r.left)*vb[2]/r.width,vb[1]+(cy-r.top)*vb[3]/r.height]};
 const perPx=()=>vb[2]/(m.getBoundingClientRect().width||975);
 let eatClick=false;
 m.addEventListener('click',e=>{if(eatClick){eatClick=false;e.stopPropagation();e.preventDefault()}},true);
 const armEat=()=>{eatClick=true;setTimeout(()=>{eatClick=false},350)};
 m.addEventListener('wheel',e=>{if(e.deltaY>0&&isFull()&&!(e.ctrlKey||e.metaKey))return;e.preventDefault();
  const dy=e.deltaY*(e.deltaMode===1?16:e.deltaMode===2?400:1);const p=toSVG(e.clientX,e.clientY);
  zoomAt(p[0],p[1],Math.exp(-Math.max(-300,Math.min(300,dy))*0.0025))},{passive:false});
 let drag=null;const TH=6;
 m.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'||e.button)return;drag={id:e.pointerId,x:e.clientX,y:e.clientY,v:vb.slice(),k:perPx(),on:false}});
 m.addEventListener('pointermove',e=>{if(!drag||e.pointerId!==drag.id)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;
  if(!drag.on){if(Math.hypot(dx,dy)<TH)return;drag.on=true;stopAnim();m.classList.add('is-panning');try{m.setPointerCapture(e.pointerId)}catch(_){}}
  applyViewBox(clampVB([drag.v[0]-dx*drag.k,drag.v[1]-dy*drag.k,drag.v[2],drag.v[3]]))});
 const endDrag=e=>{if(!drag||e.pointerId!==drag.id)return;if(drag.on){armEat();m.classList.remove('is-panning');try{m.releasePointerCapture(e.pointerId)}catch(_){}}drag=null};
 m.addEventListener('pointerup',endDrag);m.addEventListener('pointercancel',endDrag);
 let mode=null,T0,c0,P0;
 const mid=(a,b)=>[(a.clientX+b.clientX)/2,(a.clientY+b.clientY)/2],dist=(a,b)=>Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY)||1;
 function pinch(e){const a=e.touches[0],b=e.touches[1],c=mid(a,b);T0=vb.slice();P0={d:dist(a,b),w:toSVG(c[0],c[1])};mode='pinch';stopAnim()}
 function pan(t){T0=vb.slice();c0=[t.clientX,t.clientY];P0={k:perPx()};mode='pan';stopAnim()}
 m.addEventListener('touchstart',e=>{const n=e.touches.length;if(n>=2)pinch(e);else if(n===1){mode='maybe';c0=[e.touches[0].clientX,e.touches[0].clientY]}},{passive:true});
 m.addEventListener('touchmove',e=>{
  if(mode==='pinch'&&e.touches.length>=2){if(!e.cancelable)return;e.preventDefault();
   const a=e.touches[0],b=e.touches[1],c=mid(a,b),r=m.getBoundingClientRect();
   const w=Math.min(975,Math.max(MINW,T0[2]*P0.d/dist(a,b))),h=w*610/975;
   applyViewBox(clampVB([P0.w[0]-(c[0]-r.left)*w/r.width,P0.w[1]-(c[1]-r.top)*h/r.height,w,h]));return}
  if(mode==='maybe'){const t=e.touches[0],dx=t.clientX-c0[0],dy=t.clientY-c0[1];
   if(Math.abs(dx)<8&&Math.abs(dy)<8)return;
   if(Math.abs(dx)>Math.abs(dy)&&e.cancelable)pan(t);else{mode='scroll';return}}
  if(mode==='pan'){if(!e.cancelable)return;e.preventDefault();const t=e.touches[0];
   applyViewBox(clampVB([T0[0]-(t.clientX-c0[0])*P0.k,T0[1]-(t.clientY-c0[1])*P0.k,T0[2],T0[3]]))}},{passive:false});
 const tend=e=>{const n=e.touches.length;if(mode==='pan'||mode==='pinch')armEat();if(n===0)mode=null;else if(n===1&&mode==='pinch')pan(e.touches[0])};
 m.addEventListener('touchend',tend);m.addEventListener('touchcancel',tend);
 /* Click empty SVG chrome → clear selection (same as USA). */
 m.addEventListener('click',e=>{if(cur&&e.target===e.currentTarget)resetAll()});
}

document.documentElement.classList.add('accent-'+ACCENT);
buildSwitcher(); buildMap(); initSteps(); initFreeZoom(); applyViewBox(FULL); render(welcome());

// deep link #ON or #ON/Toronto or #YYZ
const hash = decodeURIComponent(location.hash.replace(/^#/,''));
if(hash){
  if(AIRPORTS.some(a=>a.code===hash)) selectAirport(hash);
  else {
    const [a,city] = hash.split('/');
    if(GEO[a]) selectRegion(a, city||null);
  }
}
})();
