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
const TAG = {aff:'Affiliate',off:'Official',srch:'Search',stub:'Coming soon'};
function lk(ic,title,sub,href,tag){
  if(!href) return `<span class="lk soon"><span class="ic" aria-hidden="true">${ic}</span><span class="t">${esc(title)}${sub?`<small>${esc(sub)}</small>`:''}</span><span class="tag soon">${TAG.stub}</span></span>`;
  return `<a class="lk" href="${esc(href)}" target="_blank" rel="${tag==='aff'?'sponsored nofollow noopener':'noopener'}"><span class="ic" aria-hidden="true">${ic}</span><span class="t">${esc(title)}${sub?`<small>${esc(sub)}</small>`:''}</span><span class="tag ${tag}">${TAG[tag]||TAG.off}</span></a>`;
}
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
  /* US-tourist popularity order (Marc 2026-11-12); only maps that exist in the page language.
     Dominican Republic (after France), Portugal and Greece (after Germany) join once their pages exist. */
  const path=(location.pathname||'');
  const es = path.indexOf('/es/')===0;
  const it = path.indexOf('/it/')===0;
  const ORDER = ['usa','ca','mx','uk','it','fr','es','jp','de','kr','au'];
  const ACC = {usa:'usa',ca:'maple',mx:'mxgreen',uk:'unionjack',it:'italy',fr:'tricolore',es:'rojigualda',jp:'hinomaru',de:'schwarzrotgold',kr:'taegeuk',au:'ausflag'};
  const FILE = {usa:'usa',ca:'canada',mx:'mexico',uk:'uk',it:'italy',fr:'france',es:'spain',jp:'japan',de:'germany',kr:'south-korea',au:'australia'};
  const LBL = es ? {usa:'Mapa de EE. UU.',ca:'Mapa de Canadá',mx:'Mapa de México',uk:'Mapa del Reino Unido',it:'Mapa Italia',fr:'Mapa de Francia',es:'Mapa de España',jp:'Mapa de Japón',de:'Mapa de Alemania',kr:'Mapa de Corea',au:'Mapa de Australia'}
    : it ? {usa:'Mappa USA',ca:'Mappa del Canada',mx:'Mappa del Messico',uk:'Mappa del Regno Unito',it:'Mappa dell\u2019Italia',fr:'Mappa della Francia',es:'Mappa della Spagna',jp:'Mappa del Giappone',de:'Mappa della Germania',kr:'Mappa della Corea',au:'Mappa dell\u2019Australia'}
    : {usa:'USA Map',ca:'Canada Map',mx:'Mexico Map',uk:'UK Map',it:'Italy Map',fr:'France Map',es:'Spain Map',jp:'Japan Map',de:'Germany Map',kr:'Korea Map',au:'Australia Map'};
  const ES_FALLBACK_EN = {uk:1, de:1};
  const pre = es ? '/es/countries/' : it ? '/it/countries/' : '';
  const tabs = ORDER.filter(id => LBL[id]).map(id => {
    const file = FILE[id] + '-map.html';
    const href = es
      ? (ES_FALLBACK_EN[id] ? '/countries/' + file : '/es/countries/' + file)
      : (pre + file);
    return {id, href, label: LBL[id], accent: ACC[id]};
  });
  const cur = ({CA:'ca',MX:'mx',UK:'uk',FR:'fr',DE:'de',KR:'kr',JP:'jp',IT:'it',ES:'es',AU:'au'}[DATA.country]) || 'usa';
  const backHref = es ? '/es/?view=map' : it ? '/it/?view=map' : '../?view=map';
  const backLabel = es ? '\u2190 Mapa mundial' : it ? '\u2190 Mappa del mondo' : '\u2190 World Map';
  const back = `<a class="msw-tab world-back" href="${backHref}" style="touch-action:manipulation;position:relative;z-index:5"><i aria-hidden="true"></i><span>${backLabel}</span></a>`;
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
    if(DATA.tones && DATA.tones[a]) cls.push(DATA.tones[a]);
    const p = el('path', {id:'s-'+a, class:cls.join(' '), d:g.d, role:'button', tabindex:'0', 'aria-label':g.name, 'data-a':a});
    p.addEventListener('click', e => { e.stopPropagation(); selectRegion(a); if(e.detail){ try{p.blur()}catch(_){ } } });
    p.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' '){ e.preventDefault(); selectRegion(a); }});
    gs.appendChild(p);
    /* KR/JP: English names (USA uses 2-letter codes). Tiny regions get
       USA-style leader lines when geo[a].callout is set by the geo pack. */
    const useNames = !!(DATA && /^(KR|JP|UK|FR|DE|IT|ES|AU)$/.test(DATA.country||''));
    const sameNameCity = /^(JP|KR)$/.test((DATA&&DATA.country)||'') && (g.cities||[]).some(c => c.n===g.name || c.n===g.name+' City' || g.name===(c.n||'').replace(/ City$/,''));
    if(sameNameCity){
      /* City marker already carries this name (Tokyo, Seoul, Osaka…). */
    } else if(g.callout && g.lx!=null && g.ly!=null){
      const ln = el('line', {class:'lbl-lead'+(g.labelZoom?' lbl-zoom':''), x1:g.c[0], y1:g.c[1], x2:g.lx, y2:g.ly, 'data-a':a});
      gl.appendChild(ln);
      const t = el('text', {id:'l-'+a, class:'lbl lbl-callout'+(g.labelZoom?' lbl-zoom':''), x:g.lx, y:g.ly, 'text-anchor': (g.lx < g.c[0] ? 'end' : 'start')});
      t.textContent = useNames ? g.name : a; gl.appendChild(t);
    } else if(g.c){
      const t = el('text', {id:'l-'+a, class:'lbl'+(g.labelZoom?' lbl-zoom':''), x:g.lx||g.c[0], y:g.ly||g.c[1]});
      t.textContent = useNames ? g.name : a; gl.appendChild(t);
    }
  }
  if(DATA && DATA.country==='JP' && Array.isArray(DATA.regionGroups)){
    for(const rg of DATA.regionGroups){
      const t=el('text',{id:'lg-'+(rg.id||rg.name),class:'lbl lbl-group','data-group':rg.name,x:rg.x,y:rg.y,'data-x0':rg.x,'data-y0':rg.y,'text-anchor':rg.anchor||'middle'});
      t.textContent=rg.name;
      gl.appendChild(t);
    }
  }
  for(const a of ABBRS){
    for(const c of (GEO[a].cities||[])){
      const g = el('g', {class:'ct'+(c.cap?' cap':'')+(c.major?' major':'')+(c.sample?' sample':''), role:'button', tabindex:'0', 'data-s':a, 'data-k':a+'|'+c.n, 'aria-label':c.n+', '+GEO[a].name});
      const ctt = el('title',{}); ctt.textContent = c.n+', '+GEO[a].name;
      g.appendChild(el('circle', {cx:c.x, cy:c.y, r:c.cap?3.2:c.sample?5:2.6}));
      if(c.cap) g.appendChild(el('circle', {class:'ring', cx:c.x, cy:c.y, r:6}));
      else if(c.sample) g.appendChild(el('circle', {class:'ring', cx:c.x, cy:c.y, r:8.5}));
      const place = c.place || '';
      const right = c.x < 880;
      const anchor = c.anchor || (place==='above' ? 'middle' : (right?'start':'end'));
      let lx, ly;
      if(c.lx!=null && c.ly!=null){ lx=c.lx; ly=c.ly; }
      else if(place==='above'){ lx=c.x; ly=c.y; }
      else { lx=c.x+(anchor==='end'?-8:anchor==='middle'?0:8); ly=c.y+3.5; }
      const tx = el('text', {x:lx, y:ly, 'text-anchor':anchor});
      const lines = (c.lines && c.lines.length) ? c.lines : [c.n];
      if(lines.length===1 && place!=='above'){ tx.textContent = lines[0]; }
      else {
        lines.forEach((line,i)=>{
          const sp=el('tspan',{x:lx});
          /* Font-relative so the stack stays clear of the city mark at 1280 and 390. */
          if(place==='above') sp.setAttribute('dy', i===0 ? '-1.85em' : '1.15em');
          else sp.setAttribute('dy', i===0 ? '0' : '1.15em');
          sp.textContent=line; tx.appendChild(sp);
        });
      }
      if(c.pinLabel) tx.setAttribute('data-pin','1');
      g.appendChild(tx); g.appendChild(ctt);
      g.addEventListener('click', e => { e.stopPropagation(); selectCity(a, c.n); if(e.detail){ try{g.blur()}catch(_){ } } });
      g.addEventListener('keydown', e => { if(e.key==='Enter'){ selectCity(a, c.n); }});
      gc.appendChild(g);
    }
  }
  buildAirports();
  mountLabelLegend();
  const pick = $('#pick');
  if(pick){
    pick.innerHTML = `<option value="">${mapChoosePlaceholder()}</option>` +
      ABBRS.map(a => `<option value="${a}">${esc(GEO[a].name)} (${a})</option>`).join('');
    pick.onchange = () => { if(pick.value) selectRegion(pick.value); };

  /* Custom mineral-night region picker */
  (function mountCountryPicker(){
    if(!pick || pick.dataset.spMounted) return;
    pick.dataset.spMounted = '1';
    const wrap = document.createElement('div');
    wrap.className = 'state-picker';
    pick.parentNode.insertBefore(wrap, pick);
    wrap.appendChild(pick);
    const unit = (DATA && DATA.unit) ? DATA.unit : 'region';
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'state-picker-btn';
    btn.setAttribute('aria-haspopup', 'listbox');
    btn.setAttribute('aria-expanded', 'false');
    const ph = mapChoosePlaceholder();
    btn.innerHTML = '<span class="sp-label">' + ph + '</span><svg class="sp-chev" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7.4 9.5 12 14.1l4.6-4.6 1.4 1.4-6 6-6-6z"/></svg>';
    const menu = document.createElement('ul');
    menu.className = 'state-picker-menu';
    menu.setAttribute('role', 'listbox');
    const head = ({CA:'Provinces & territories', MX:'States', UK:'Regions', FR:'Regions', DE:'Länder', IT:'Regions', ES:'Communities', JP:'Prefectures', KR:'Provinces & cities'}[DATA && DATA.country]) || 'Regions';
    menu.innerHTML = '<li class="sp-head" aria-hidden="true">' + head + '</li>' +
      ABBRS.map(a => `<li role="option" data-a="${a}" aria-selected="false"><span class="sp-name">${esc(GEO[a].name)}</span><span class="sp-code">${a}</span></li>`).join('');
    wrap.append(btn, menu);
    const label = btn.querySelector('.sp-label');
    function setOpen(o){ wrap.classList.toggle('open', o); btn.setAttribute('aria-expanded', o?'true':'false'); }
    function syncFromPick(){
      const v = pick.value;
      [...menu.querySelectorAll('[role="option"]')].forEach(li => li.setAttribute('aria-selected', String(li.dataset.a === v)));
      label.textContent = v && GEO[v] ? GEO[v].name : ph;
    }
    window.syncCountryStatePicker = syncFromPick;
    btn.addEventListener('click', e => { e.stopPropagation(); setOpen(!wrap.classList.contains('open')); });
    menu.addEventListener('click', e => {
      const li = e.target.closest('[role="option"]'); if(!li) return;
      pick.value = li.dataset.a; selectRegion(li.dataset.a); syncFromPick(); setOpen(false);
    });
    document.addEventListener('click', e => { if(!wrap.contains(e.target)) setOpen(false); });
    document.addEventListener('keydown', e => { if(e.key === 'Escape') setOpen(false); });
    const proto = Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype, 'value');
    if(proto && proto.set){
      Object.defineProperty(pick, 'value', {
        configurable: true,
        get(){ return proto.get.call(this); },
        set(v){ proto.set.call(this, v); syncFromPick(); }
      });
    }
    syncFromPick();
  })();

  }
  buildPortalGrid();
}

function buildAirports(){
  let ga = $('#g-ap'); if(!ga){ ga = el('g',{id:'g-ap'}); $('#map').appendChild(ga); }
  ga.innerHTML = '';
  let glink = $('#g-ap-link');
  if(!glink){
    glink = el('g',{id:'g-ap-link'});
    const gc = $('#g-ct');
    if(gc && gc.parentNode) gc.parentNode.insertBefore(glink, gc);
    else if(ga.parentNode) ga.parentNode.insertBefore(glink, ga);
    else $('#map').appendChild(glink);
  }
  glink.innerHTML = '';
  function findCityByName(name){
    if(!name) return null;
    for(const key of Object.keys(GEO||{})){
      const hit = (GEO[key].cities||[]).find(c => c.n === name);
      if(hit) return hit;
    }
    return null;
  }
  for(const ap of AIRPORTS){
    const region = ap.province || ap.state;
    const linkName = ap.linkCity || ap.city;
    const city = findCityByName(linkName) || (GEO[region]&&GEO[region].cities||[]).find(c => c.n === ap.city) || (GEO[region]&&GEO[region].cities||[])[0];
    if(city){
      glink.appendChild(el('line', {class:'ap-link'+(ap.zoomOnly?' ap-zoomonly':''), x1:city.x, y1:city.y, x2:ap.x, y2:ap.y, 'data-region':region, 'data-citykey':region+'|'+(linkName||ap.city), 'data-code':ap.code, 'data-city':linkName||ap.city}));
    }
    const g = el('g', {class:'ap'+(ap.zoomOnly?' ap-zoomonly':'')+(ap.major?' ap-major':''), role:'button', tabindex:ap.zoomOnly?'-1':'0', 'data-code':ap.code, 'data-region':region, 'data-citykey':region+'|'+ap.city, 'aria-label':ap.code+', '+ap.city});
    const mark=el('g',{class:'ap-mark'});
    const rootAp=document.getElementById('country-map');
    const compactAp=!!(document.documentElement.classList.contains('accent-unionjack')||document.documentElement.classList.contains('accent-italy')||document.documentElement.classList.contains('accent-tricolore')||document.documentElement.classList.contains('accent-rojigualda')||document.documentElement.classList.contains('accent-hinomaru')||document.documentElement.classList.contains('accent-taegeuk')||document.documentElement.classList.contains('accent-ausflag')||(rootAp&&(rootAp.classList.contains('accent-unionjack')||rootAp.classList.contains('accent-italy')||rootAp.classList.contains('accent-tricolore')||rootAp.classList.contains('accent-rojigualda')||rootAp.classList.contains('accent-hinomaru')||rootAp.classList.contains('accent-taegeuk')||rootAp.classList.contains('accent-ausflag'))));
    const aps=compactAp?0.62:1;
    mark.appendChild(el('rect', {class:'pad', x:(-8*aps).toFixed(2), y:(-8*aps).toFixed(2), width:(16*aps).toFixed(2), height:(16*aps).toFixed(2), rx:(2*aps).toFixed(2), transform:'rotate(45)'}));
    mark.appendChild(el('path', {class:'glyph', d:PLANE, transform:`translate(${(-6.2*aps).toFixed(3)},${(-6.2*aps).toFixed(3)}) scale(${(0.52*aps).toFixed(4)})`}));
    g.appendChild(mark);
    g.setAttribute('transform', `translate(${ap.x} ${ap.y})`);
    const ax=ap.ldx||0, ay=ap.ldy==null?16:ap.ldy, ta=ap.anchor||'middle';
    const tx = el('text', {x:ax, y:ay, 'text-anchor':ta, class:ap.mapLabel?'map-label':'map-label'});
    tx.textContent = ap.mapLabel||ap.code;
    if(ap.pinLabel) tx.setAttribute('data-pin','1');
    g.appendChild(tx);
    if(ap.mapName){ const t2=el('text',{x:ax,y:ay+14,'text-anchor':ta,class:'map-name'}); t2.textContent=ap.mapName; g.appendChild(t2); }
    const tt = el('title',{}); tt.textContent = `${ap.code} — ${ap.name||ap.city}`; g.appendChild(tt);
    g.setAttribute('aria-label', `${ap.code}, ${ap.name||''}, ${ap.city}`);
    g.addEventListener('click', e => { e.stopPropagation(); selectAirport(ap.code); if(e.detail){ try{g.blur()}catch(_){ } } });
    g.addEventListener('keydown', e => { if(e.key==='Enter'||e.key===' '){ e.preventDefault(); selectAirport(ap.code); }});
    ga.appendChild(g);
  }
}



function mapLang(){
  const blob=((document.documentElement.lang||'')+' '+(document.documentElement.getAttribute('data-lang')||'')).toLowerCase();
  let stored='';
  try{ stored=(localStorage.getItem('ppc_lang')||'').toLowerCase(); }catch(_){}
  if(/\bit\b/.test(blob) || stored==='it') return 'it';
  if(/\bes\b/.test(blob) || stored==='es') return 'es';
  return 'en';
}
function mapChoosePlaceholder(){
  const lang=mapLang();
  const unit=(DATA && DATA.unit) || 'region';
  if(lang==='es') return unit==='community' ? 'Elija una comunidad autónoma…' : 'Elija una región…';
  if(lang==='it') return unit==='community' ? 'Scelga una comunità autonoma…' : 'Scelga una regione…';
  return 'Choose a ' + unit + '…';
}
function mapPickTitle(){
  const lang=mapLang();
  const unit=(DATA && DATA.unit) || 'region';
  if(lang==='es') return unit==='community' ? 'Seleccione una comunidad autónoma o ciudad' : 'Seleccione una región o ciudad';
  if(lang==='it') return unit==='community' ? 'Selezioni una comunità autonoma o una città' : 'Selezioni una regione o una città';
  return 'Pick a ' + unit + ' or city';
}
function mapClickLead(){
  const lang=mapLang();
  const unit=(DATA && DATA.unit) || 'region';
  if(lang==='es') return 'Haga clic en cualquier región del mapa (or use the list) to open its panel. Plane marks are the airport hubs:';
  if(lang==='it') return 'Faccia clic su una regione qualsiasi della mappa (or use the list) to open its panel. Plane marks are the airport hubs:';
  return 'Click any ' + unit + ' on the map (or use the list) to open its panel. Plane marks are the airport hubs:';
}
function mapJourneyOrder(){
  const lang=mapLang();
  if(lang==='es') return 'Orden del viaje: 1 veterinario + normativa → 2 carretera/tren → 3 avión → 4 hotel → 5 peluquería.';
  if(lang==='it') return 'Ordine del viaggio: 1 veterinario + normative → 2 strada/treno → 3 aereo → 4 hotel → 5 toelettatura.';
  return 'Journey order: 1 vet + laws → 2 road/rail → 3 plane → 4 hotel → 5 grooming.';
}
function mapPanelVetLaws(){
  const lang=mapLang();
  if(lang==='es') return 'Veterinario + normativa';
  if(lang==='it') return 'Veterinario + normative';
  return 'Vet + laws';
}
function mapPanelAuthority(){
  const lang=mapLang();
  if(lang==='es') return 'AUTORIDAD';
  if(lang==='it') return 'AUTORITÀ';
  return 'Authority';
}
function mapPanelMainCities(){
  const lang=mapLang();
  if(lang==='es') return 'CIUDADES PRINCIPALES';
  if(lang==='it') return 'CITTÀ PRINCIPALI';
  return 'Main cities';
}

function mountLabelLegend(){
  const root = $('#country-map') || document.getElementById('country-map');
  const host = root && root.querySelector('.mapcard');
  if(!host || host.querySelector('.lbl-legend')) return;
  const lang = ((document.documentElement.lang||'') + ' ' + (document.documentElement.getAttribute('data-lang')||'')).toLowerCase();
  let es = /\bes\b/.test(lang);
  try{ es = es || (localStorage.getItem('ppc_lang')||'')==='es'; }catch(_){}
  const L = es
    ? {r:'Regiones', c:'Ciudades', k:'Capital', a:'Aeropuertos internacionales'}
    : {r:'Regions', c:'Cities', k:'Capital', a:'International airports'};
  const box = document.createElement('div');
  box.className = 'lbl-legend';
  box.setAttribute('role','note');
  box.setAttribute('aria-label', es ? 'Leyenda de etiquetas' : 'Label colour legend');
  box.innerHTML =
    '<span class="ll-r"><i aria-hidden="true"></i>'+L.r+'</span>'+
    '<span class="ll-c"><i aria-hidden="true"></i>'+L.c+'</span>'+
    '<span class="ll-k"><i aria-hidden="true"></i>'+L.k+'</span>'+
    '<span class="ll-a"><b aria-hidden="true">✈</b>'+L.a+'</span>';
  host.appendChild(box);
}

function buildPortalGrid(){
  const grid = $('#grid'); if(!grid) return;
  grid.innerHTML = ABBRS.map(a => {
    const special = DATA.special && DATA.special[a];
    const hub = (DATA.provHub&&DATA.provHub[a]) || (DATA.stateHub&&DATA.stateHub[a]);
    return `<button type="button" data-a="${a}" class="${special?'rule':''}${hub?' hub':''}"><b>${a}</b><span>${esc(GEO[a].name)}</span>${special?'<em>Alert</em>':''}${hub?`<em class="hub">${hub}</em>`:''}</button>`;
  }).join('');
  grid.querySelectorAll('button').forEach(b => b.onclick = () => { selectRegion(b.dataset.a); $('#panel').scrollIntoView({behavior:'smooth',block:'nearest'}); });
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
  /* EU data uses `breed`; CA/MX use `breeds`. Never claim a US-style "no federal ban". */
  const b = DATA.breed || DATA.breeds || {};
  const eu = /^(UK|FR|DE|IT|ES)$/.test(DATA.country||'');
  const national = eu
    ? (b.national && String(b.national).trim() ? b.national : 'Policy details coming soon')
    : honest(b.national, 'Policy details coming soon');
  let s = `<h4>Breed rules</h4><p>${esc(national)}</p>`;
  if(eu) return s; /* no inherited US/CA subnational breed claims on EU maps */
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
  let s = `<section class="sec" data-sec="1"><h3><span class="n">1</span>${esc(mapPanelVetLaws())}</h3>`;
  if(DATA.entry_note) s += `<p class="disc">${esc(DATA.entry_note)}</p>`;
  /* Authority is body copy (muted), never a gold uppercase h4 — gold is for map selection + short section labels. */
  s += `<h4>${esc(mapPanelAuthority())}</h4>`;
  if(DATA.authority && DATA.authority !== 'Coming soon'){
    s += `<p class="disc">${esc(DATA.authority)}</p>`;
  } else {
    s += `<p class="disc">Coming soon</p>`;
  }
  if(DATA.officialUrl){
    const checked = DATA.lastChecked ? ('Checked '+DATA.lastChecked) : '';
    s += `<div class="links">${lk('🏛', DATA.name+' official pet-entry page', checked, DATA.officialUrl, 'off')}</div>`;
  }
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
  if(DATA.rail && DATA.rail.train){
    s += `<h4>Train</h4><p>${esc(DATA.rail.train.rule)}</p>`;
    if(DATA.rail.train.url) s += `<div class="links">${lk('🚆','Official train pet rules','',DATA.rail.train.url,'off')}</div>`;
  }
  if(DATA.rail && DATA.rail.bus){
    s += `<h4>Bus / coach</h4><p>${esc(DATA.rail.bus.rule)}</p>`;
    if(DATA.rail.bus.url) s += `<div class="links">${lk('🚌','Official bus pet rules','',DATA.rail.bus.url,'off')}</div>`;
  }
  if(DATA.rail && DATA.rail.uber_pet){
    s += `<h4>Rides</h4><div class="links">${lk('🚗','Uber Pet','',DATA.rail.uber_pet.url,'off')}</div><p>${esc(DATA.rail.uber_pet.rule)}</p>`;
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
function hotelSection(a, qCity){
  let s = `<section class="sec" data-sec="4"><h3><span class="n">4</span>Hotel</h3>`;
  if(DATA.hotels && DATA.hotels.chains){
    s += `<h4>Hotel chains</h4><div class="links">` +
      DATA.hotels.chains.map(c => lk('🏨', c.chain, c.policy, c.url, 'off')).join('') + `</div>`;
  }
  s += `<p class="disc">Confirm the property&rsquo;s pet fee and weight limit with the hotel before you stay.</p></section>`;
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

/* Same steps as usa-map.js hilite(a,key,apCode): city key lights only that city's airports. */
function hilite(a, key, apCode){
  document.querySelectorAll('.st.sel,.lbl.sel,.ct.sel,.ap.sel').forEach(e=>e.classList.remove('sel'));
  document.querySelectorAll('#grid button.sel').forEach(e=>e.classList.remove('sel'));
  if(a){ $('#s-'+a)?.classList.add('sel'); $('#l-'+a)?.classList.add('sel'); document.querySelector(`#grid button[data-a="${a}"]`)?.classList.add('sel'); }
  if(key) document.querySelector(`.ct[data-k="${CSS.escape(key)}"]`)?.classList.add('sel');
  document.querySelectorAll('.ap,.ap-link').forEach(el=>{
    const mine = !a || el.dataset.region===a;
    el.classList.toggle('dim', !!a && !mine);
    const cityHot = !!(key && el.dataset.citykey===key);
    const stateHot = !!a && !key && mine;
    el.classList.toggle('hot', cityHot || stateHot);
  });
  if(apCode) document.querySelector(`.ap[data-code="${CSS.escape(apCode)}"]`)?.classList.add('sel');
  const pick = $('#pick'); if(pick) pick.value = a||'';
  const reset = $('#reset'); if(reset) reset.hidden = !a;
  zoomTo(a);
}

/* ---------- view box: zoomTo (region select on phones) + free zoom/pan (mirrors usa-map.js) ---------- */
const FULL=(CFG.view&&CFG.view.length===4)?CFG.view.slice():[0,0,975,610];
const MAP_W=FULL[2],MAP_H=FULL[3],MAP_X=FULL[0],MAP_Y=FULL[1];
const MAXZ=8,MINW=MAP_W/MAXZ;let vb=FULL.slice(),animId=0;
function clampVB(v){const w=Math.min(MAP_W,Math.max(MINW,v[2])),h=w*MAP_H/MAP_W;
 const cx=v[0]+v[2]/2,cy=v[1]+v[3]/2;let x=cx-w/2,y=cy-h/2;
 x=Math.max(MAP_X,Math.min(MAP_X+MAP_W-w,x));y=Math.max(MAP_Y,Math.min(MAP_Y+MAP_H-h,y));return [x,y,w,h]}

function syncLabelScale(){
  const m=$('#map'); if(!m) return;
  const w=m.getBoundingClientRect().width||MAP_W;
  m.style.setProperty('--map-w-px', Math.max(1,w).toFixed(1));
}
function _box(el){
  const b=el.getBoundingClientRect();
  if(b.width<2||b.height<2||b.bottom<=0||b.right<=0) return null;
  return b;
}
function _overlap(a,b,pad){
  return !(a.right+pad<b.left || a.left-pad>b.right || a.bottom+pad<b.top || a.top-pad>b.bottom);
}
/* Hide secondary labels that collide. Priority (kept first): major airports,
   capitals, large region names, then minor cities, then small region names.
   Secondaries are allowed back when zoom gives them room. */
function _userPerPx(){
  const m=$('#map'); if(!m) return 1;
  const w=m.getBoundingClientRect().width||MAP_W;
  const vb=(m.viewBox&&m.viewBox.baseVal&&m.viewBox.baseVal.width)||MAP_W;
  return vb/w;
}
function _rememberPos(el){
  if(el.dataset.ox==null){
    el.dataset.ox=el.getAttribute('x')||'0';
    el.dataset.oy=el.getAttribute('y')||'0';
    el.dataset.ota=el.getAttribute('text-anchor')||'';
  }
}
function _restorePos(el){
  _rememberPos(el);
  el.setAttribute('x', el.dataset.ox);
  el.setAttribute('y', el.dataset.oy);
  if(el.dataset.ota) el.setAttribute('text-anchor', el.dataset.ota);
  else el.removeAttribute('text-anchor');
}
function _applyPos(el, s){
  el.setAttribute('x', (+s.x).toFixed(1));
  el.setAttribute('y', (+s.y).toFixed(1));
  if(s.anchor) el.setAttribute('text-anchor', s.anchor);
}
function _slotRing(x, y, anchors, maxPx){
  const u=_userPerPx();
  const out=[{x,y,anchor:anchors||null}];
  [16,28,42,58,76].filter(px=>maxPx==null||px<=maxPx).forEach(px=>{
    const d=px*u;
    [[d,0,'start'],[-d,0,'end'],[0,d,anchors],[0,-d,anchors],
     [d,d,'start'],[-d,d,'end'],[d,-d,'start'],[-d,-d,'end']].forEach(p=>{
      out.push({x:x+p[0], y:y+p[1], anchor:p[2]||anchors||null});
    });
  });
  return out;
}
function _overlapArea(a,b,pad){
  const x=Math.max(0, Math.min(a.right,b.right)-Math.max(a.left,b.left)+2*pad);
  const y=Math.max(0, Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)+2*pad);
  return (x>0 && y>0) ? x*y : 0;
}
function _scoreSlot(box, placed, pad, it){
  let n=0, area=0;
  for(const p of placed){
    if(it && p.kind==='ap-icon' && p.code && p.code===it.code) continue;
    const a=_overlapArea(box,p.box,pad);
    if(a){ n++; area+=a; }
  }
  return {n, area};
}
function _airportRank(code){
  const R={ATL:0,LAX:1,ORD:2,DFW:3,DEN:4,JFK:5,SFO:6,LAS:7,SEA:8,MIA:9,CLT:10,PHX:11,EWR:12,MCO:13,IAH:14,BOS:15,MSP:16,DTW:17,FLL:18,PHL:19,LGA:20,BWI:21,DCA:22,IAD:23,SLC:24,SAN:25,TPA:26,PDX:27,HNL:28,
    LHR:0,LGW:1,MAN:2,STN:3,LTN:4,BHX:5,EDI:6,BRS:7,
    CDG:0,ORY:1,NCE:2,MRS:3,LYS:4,BSL:5,TLS:6,NTE:7,BVA:8,BOD:9,
    FRA:0,MUC:1,BER:2,DUS:3,HAM:4,CGN:5,STR:6,
    ICN:0,GMP:1,PUS:2,CJU:3,
    HND:0,NRT:1,KIX:2,ITM:3,FUK:4,CTS:5,NGO:6,OKA:7,
    FCO:0,MXP:1,BGY:2,VCE:3,NAP:4,CTA:5,BLQ:6,LIN:7,CIA:8,PMO:9,
    MAD:0,BCN:1,PMI:2,AGP:3,ALC:4,LPA:5,TFS:6,VLC:7,SVQ:8,BIO:9};
  const n=R[(code||'').toUpperCase()];
  return (n==null)?25:n;
}
function resolveLabelOverlaps(){
  if(window.PPC_LABEL_PLAN) return;
  const m=$('#map'); if(!m) return;
  const _cc0=(typeof DATA!=='undefined' && DATA.country)||'';
  if(/^(FR|UK|DE|IT|ES|JP|KR)$/.test(_cc0)){
    m.querySelectorAll('#g-lb text.lbl').forEach(t=>{
      const ts=t.querySelectorAll('tspan');
      if(!ts.length) return;
      t.textContent=[...ts].map(s=>(s.textContent||'').trim()).filter(Boolean).join(' ');
    });
  }
  m.querySelectorAll('#g-lb line.lbl-lead[data-temp="1"]').forEach(n=>n.remove());
  m.querySelectorAll('.lbl-crowd,.ct-crowd,.ct-label-crowd,.ap-crowd,.ap-name-crowd,.ap-code-crowd').forEach(n=>n.classList.remove('lbl-crowd','ct-crowd','ct-label-crowd','ap-crowd','ap-name-crowd','ap-code-crowd'));
  const vis=el=>{
    const cs=getComputedStyle(el);
    if(cs.display==='none'||cs.visibility==='hidden'||+cs.opacity===0) return null;
    const b=el.getBoundingClientRect();
    return (b.width>2 && b.height>2) ? b : null;
  };
  const mapBox=m.getBoundingClientRect();
  const inMap=box=>!(box.right<mapBox.left+4 || box.left>mapBox.right-4 || box.bottom<mapBox.top+4 || box.top>mapBox.bottom-4);
  const inMapFull=box=>box.left>=mapBox.left+1 && box.right<=mapBox.right-1 && box.top>=mapBox.top+1 && box.bottom<=mapBox.bottom-1;
  const screenToSvg=(x,y)=>{
    const v=(typeof vb!=='undefined' && vb && vb.length===4)?vb:[0,0,975,610];
    return [v[0]+(x-mapBox.left)*v[2]/mapBox.width, v[1]+(y-mapBox.top)*v[3]/mapBox.height];
  };
  const insetBoxes=()=>{
    const boxes=[];
    if(typeof GEO==='undefined'||!GEO) return boxes;
    const keys=(typeof ABBRS!=='undefined'&&ABBRS)?ABBRS:Object.keys(GEO);
    for(const a of keys){
      const g=GEO[a]; if(!g||!g.inset) continue;
      if(g.insetBox&&g.insetBox.length===4){ boxes.push(g.insetBox); continue; }
      const p=document.getElementById('s-'+a);
      if(p&&p.getBBox){ try{ const b=p.getBBox(); boxes.push([b.x,b.y,b.width,b.height]); }catch(_){ } }
    }
    return boxes;
  };
  const underInset=box=>{
    const insets=insetBoxes(); if(!insets.length) return false;
    const p1=screenToSvg(box.left,box.top), p2=screenToSvg(box.right,box.bottom);
    for(const [x,y,w,h] of insets){
      if(p1[1]>=y+h-2 && !(p2[0]<x-8 || p1[0]>x+w+8)) return true;
    }
    return false;
  };
  const full=(typeof isFull==='function')?isFull():true;
  const nCap=m.querySelectorAll('#g-ct .ct.cap').length;
  const nMaj=m.querySelectorAll('#g-ap .ap.ap-major').length;
  const nAp=[...m.querySelectorAll('#g-ap .ap')].filter(g=>getComputedStyle(g).display!=='none').length;
  const cc=(typeof DATA!=='undefined' && DATA.country)||(document.getElementById('usa-map')&&'US')||'';
  /* Marc 09:03 KST: at 390, crowded maps keep capitals + major airports; region names wait for zoom. */
  const crowdedMobile=full && mapBox.width<500 && (/^(FR|UK|DE|US|IT|ES|JP|KR)$/.test(cc));
  const items=[];
  m.querySelectorAll('#g-lb text.lbl').forEach(t=>{
    _restorePos(t);
    const id=(t.id||'').replace(/^l-/,'');
    const path=document.getElementById('s-'+id);
    let area=0;
    if(path && path.getBBox){ try{ const bb=path.getBBox(); area=bb.width*bb.height; }catch(_){ } }
    const lead=m.querySelector('#g-lb line.lbl-lead[data-a="'+id+'"]');
    if(lead && lead.dataset.ox2==null){ lead.dataset.ox2=lead.getAttribute('x2')||''; lead.dataset.oy2=lead.getAttribute('y2')||''; lead.dataset.ox1=lead.getAttribute('x1')||''; lead.dataset.oy1=lead.getAttribute('y1')||''; }
    if(lead && lead.dataset.ox2!=null){ lead.setAttribute('x2', lead.dataset.ox2); lead.setAttribute('y2', lead.dataset.oy2); }
    const c=(typeof GEO!=='undefined' && GEO[id] && GEO[id].c) ? GEO[id].c : null;
    const group=t.classList.contains('lbl-group');
    items.push({el:t, pri: group?(crowdedMobile?36:26): area>12000?34: area>5000?40:48, kind:'region', hide:'lbl-crowd', id, path, lead, keep:false, c,
      defer:crowdedMobile && !group,
      orig:{x:+(t.dataset.ox), y:+(t.dataset.oy), anchor:t.dataset.ota||t.getAttribute('text-anchor')||'middle'}});
  });
  const tight=/^(IT|ES)$/.test(cc);
  const compact=/^(FR|UK|DE|IT|ES|JP|KR)$/.test(cc);
  const jpkr=/^(JP|KR)$/.test(cc);
  function pushCity(t,g){
    if(!t) return;
    _restorePos(t);
    const cap=t.classList.contains('is-cap') || !!(g && g.classList.contains('cap'));
    const major=t.classList.contains('is-major') || !!(g && g.classList.contains('major'));
    const pin=t.getAttribute('data-pin')==='1';
    items.push({el:t, pri: pin?5: cap?(tight?8:20): major?24:54, kind: cap?'cap':'city', hide: (tight||compact)?'ct-label-crowd':'ct-crowd', hideEl: (tight||compact)?t:g, keep:false, pin, labelOnlyHide:tight||compact, defer:crowdedMobile && !cap && !major && !pin,
      orig:{x:+(t.dataset.ox), y:+(t.dataset.oy), anchor:t.dataset.ota||t.getAttribute('text-anchor')||'start'}});
  }
  m.querySelectorAll('#g-ct .ct').forEach(g=>pushCity(g.querySelector('text'), g));
  m.querySelectorAll('#g-lb text.ct-label').forEach(t=>{
    const key=t.dataset.owner||'';
    const g=key?m.querySelector('#g-ct .ct[data-k="'+key.replace(/"/g,'')+'"]'):null;
    pushCity(t,g);
  });
  function pushAirportText(codeEl, name, g, code, major){
    if(codeEl){
      _restorePos(codeEl);
      const apPin=codeEl.getAttribute('data-pin')==='1';
      items.push({el:codeEl, pri: apPin?5: 10+_airportRank(code)*0.4, kind: major?'ap-major':'ap-code', hide:'ap-code-crowd', keep:false, pin:apPin, code,
        orig:{x:+(codeEl.dataset.ox), y:+(codeEl.dataset.oy), anchor:codeEl.dataset.ota||codeEl.getAttribute('text-anchor')||'middle'}});
    }
    if(name){
      _restorePos(name);
      items.push({el:name, pri:90, kind:'ap-name', hide:'ap-name-crowd', keep:false, nameOnly:true, code,
        orig:{x:+(name.dataset.ox), y:+(name.dataset.oy), anchor:name.dataset.ota||name.getAttribute('text-anchor')||'middle'}});
    }
  }
  m.querySelectorAll('#g-ap .ap').forEach(g=>{
    if(getComputedStyle(g).display==='none') return;
    const major=g.classList.contains('ap-major') || !!document.getElementById('usa-map');
    const codeEl=g.querySelector('text.map-label, text:not(.map-name)');
    const name=g.querySelector('text.map-name');
    const code=(g.getAttribute('data-code')||(codeEl&&codeEl.textContent)||'').trim();
    pushAirportText(codeEl, name, g, code, major);
  });
  const grouped={};
  m.querySelectorAll('#g-lb text.ap-label').forEach(t=>{
    const code=(t.dataset.owner||(t.textContent||'').trim());
    const g=code?m.querySelector('#g-ap .ap[data-code="'+code.replace(/"/g,'')+'"]'):null;
    if(g && getComputedStyle(g).display==='none') return;
    if(!grouped[code]) grouped[code]={g, code, major: !!(g && (g.classList.contains('ap-major') || document.getElementById('usa-map')))};
    if(t.classList.contains('map-name')) grouped[code].name=t;
    else grouped[code].codeEl=t;
  });
  Object.values(grouped).forEach(o=>pushAirportText(o.codeEl, o.name, o.g, o.code, o.major));
  function hideItem(it){
    it._hidden=true;
    _applyPos(it.el, it.orig);
    if(it.lead){
      if(it.lead.dataset.ox2!=null){ it.lead.setAttribute('x2', it.lead.dataset.ox2); it.lead.setAttribute('y2', it.lead.dataset.oy2); }
      it.lead.classList.add('lbl-crowd');
    }
    if((it.kind==='cap'||it.kind==='city') && !it.labelOnlyHide){
      const g=it.hideEl||it.el.closest&&it.el.closest('.ct')||it.el;
      g.classList.add('ct-crowd');
    } else {
      (it.hideEl||it.el).classList.add(it.hide||'lbl-crowd');
    }
  }
  function tryPlace(it, slots, placed, opts){
    opts=opts||{};
    let best=null;
    for(const s of slots){
      _applyPos(it.el, {x:s.x, y:s.y, anchor:s.anchor||it.orig.anchor});
      const box=vis(it.el);
      if(!box) continue;
      if(opts.requireInMap && !inMap(box)) continue;
      if(opts.requireInMapFull && !inMapFull(box)) continue;
      if(opts.noUnderInset && underInset(box)) continue;
      if(it.kind==='region'){
        const isOrig=Math.abs(s.x-it.orig.x)<0.2 && Math.abs(s.y-it.orig.y)<0.2;
        if(!isOrig){
          const c=it.c||[it.orig.x,it.orig.y];
          const maxU=(tight?96:52)*_userPerPx();
          const dx=s.x-c[0], dy=s.y-c[1];
          if(dx*dx+dy*dy>maxU*maxU) continue;
        }
      }
      if(opts.requireInPath && it.path && it.path.isPointInFill){
        try{
          const svg=it.path.ownerSVGElement;
          const p=svg.createSVGPoint(); p.x=s.x; p.y=s.y;
          if(!it.path.isPointInFill(p) && (s.x!==it.orig.x || s.y!==it.orig.y)) continue;
        }catch(_){ }
      }
      const sc=_scoreSlot(box, placed, 4, it);
      if(sc.n===0){ return {s, box, sc}; }
      if(!best || sc.n<best.sc.n || (sc.n===best.sc.n && sc.area<best.sc.area)){
        best={s, box, sc};
      }
    }
    return best;
  }
  const placed=[];
  m.querySelectorAll('#g-ap .ap').forEach(g=>{
    if(getComputedStyle(g).display==='none') return;
    const mark=g.querySelector('.ap-mark')||g.querySelector('.pad');
    if(!mark) return;
    const box=vis(mark);
    if(!box) return;
    const pad=jpkr?4:(compact?2:0);
    const ib=pad?{left:box.left-pad,right:box.right+pad,top:box.top-pad,bottom:box.bottom+pad}:box;
    placed.push({box:ib, pri:-5, keep:true, kind:'ap-icon', code:(g.getAttribute('data-code')||'').trim()});
  });
  if(compact){
    m.querySelectorAll('#g-ct .ct').forEach(g=>{
      if(getComputedStyle(g).display==='none' || g.classList.contains('ct-crowd')) return;
      const mark=g.querySelector('circle.ring')||g.querySelector('circle');
      if(!mark) return;
      const box=vis(mark);
      if(!box) return;
      const pad=jpkr?4:2;
      placed.push({box:{left:box.left-pad,right:box.right+pad,top:box.top-pad,bottom:box.bottom+pad}, pri:-6, keep:true, kind:'ct-mark'});
    });
  }
  items.sort((a,b)=>a.pri-b.pri);
  for(const it of items){
    if(it.defer){ hideItem(it); continue; }
    if(it.kind==='ap-name'){
      const code=it.el.parentNode && it.el.parentNode.querySelector('text.map-label, text:not(.map-name)');
      if(code){
        const u=_userPerPx();
        it.orig={x:+(code.getAttribute('x')||it.orig.x), y:+(code.getAttribute('y')||it.orig.y)+14*u, anchor:code.getAttribute('text-anchor')||it.orig.anchor};
      }
      /* Subtitle only in its natural place under the code, otherwise just the IATA. */
      _applyPos(it.el, it.orig);
      const box=vis(it.el);
      const sc=box?_scoreSlot(box, placed, 4, it):{n:1,area:1};
      if(box && ((compact||tight)?(inMapFull(box)&&!underInset(box)):inMap(box)) && sc.n===0){ it.box=box; placed.push(it); }
      else hideItem(it);
      continue;
    }
    if(it.pin){
      _applyPos(it.el, it.orig);
      const box=vis(it.el);
      const fully=box && inMapFull(box) && !underInset(box);
      const sc=box?_scoreSlot(box, placed, 4, it):{n:1,area:1};
      if(box && fully && sc.n===0){ it.box=box; placed.push(it); continue; }
    }
    const maxPx = (tight||compact)
      ? (it.kind==='region'?76 : it.kind==='cap'?48 : (it.kind==='city'||it.kind==='ap-major'||it.kind==='ap-code')?36 : 24)
      : (it.kind==='region'?48:76);
    const slots=_slotRing(it.orig.x, it.orig.y, it.orig.anchor, maxPx);
    const requireInPath=(it.kind==='region' && it.path && (!it.lead || tight));
    const found=tryPlace(it, slots, placed, {requireInPath, requireInMap:true, requireInMapFull:compact||!!it.pin, noUnderInset:compact||!!it.pin});
    if(found && found.sc.n===0){
      _applyPos(it.el, {x:found.s.x, y:found.s.y, anchor:found.s.anchor||it.orig.anchor});
      if(it.lead){ it.lead.setAttribute('x2', (+found.s.x).toFixed(1)); it.lead.setAttribute('y2', (+found.s.y).toFixed(1)); }
      it.box=found.box;
      placed.push(it);
    } else {
      hideItem(it);
    }
  }
  /* Rescue hidden region names on zoom (or on a desktop full view) with a short nearby leader. */
  if(!crowdedMobile){
    items.filter(it=>it.kind==='region' && it._hidden).forEach(it=>{
      const stayInside=tight||compact;
      const slots=_slotRing(it.orig.x, it.orig.y, it.orig.anchor, stayInside?24:48);
      const found=tryPlace(it, slots, placed, {requireInMap:true, requireInMapFull:stayInside, noUnderInset:stayInside, requireInPath:stayInside});
      if(found && found.sc.n===0){
        it.el.classList.remove('lbl-crowd');
        it._hidden=false;
        _applyPos(it.el, {x:found.s.x, y:found.s.y, anchor:found.s.anchor||it.orig.anchor});
        let lead=it.lead;
        const c=it.c||[it.orig.x, it.orig.y];
        if(stayInside){
          /* IT/ES: region names stay inside the shape or remain hidden. */
        } else if(!lead){
          lead=el('line',{class:'lbl-lead', x1:c[0], y1:c[1], x2:found.s.x, y2:found.s.y, 'data-a':it.id, 'data-temp':'1'});
          const gl=$('#g-lb'); if(gl) gl.insertBefore(lead, it.el);
          it.lead=lead;
        } else {
          lead.classList.remove('lbl-crowd');
          lead.setAttribute('x2', (+found.s.x).toFixed(1));
          lead.setAttribute('y2', (+found.s.y).toFixed(1));
        }
        it.box=found.box;
        placed.push(it);
      }
    });
  }
  /* Final sweep: no on-map overlaps. Drop the more disposable of each colliding pair. */
  const pad=4;
  let changed=true;
  while(changed){
    changed=false;
    const live=placed.filter(p=>p.box && !p._hidden);
    for(let i=0;i<live.length;i++){
      for(let j=i+1;j<live.length;j++){
        const a=live[i], b=live[j];
        if(!inMap(a.box) || !inMap(b.box)) continue;
        if(a.kind==='ap-icon' && b.kind==='ap-icon') continue;
        if((a.kind==='ap-icon' && a.code && a.code===b.code) || (b.kind==='ap-icon' && b.code && b.code===a.code)) continue;
        if(!_overlap(a.box,b.box,pad)) continue;
        const drop=(a.keep&&!b.keep)?b:(b.keep&&!a.keep)?a:(a.pri>=b.pri?a:b);
        if(!drop || drop.keep || drop.kind==='ap-icon' || !drop.el) continue;
        hideItem(drop);
        const ix=placed.indexOf(drop);
        if(ix>=0) placed.splice(ix,1);
        changed=true;
        break;
      }
      if(changed) break;
    }
  }
}
/* JP/KR: paint every label in one top layer (g-lb moved after land,
   markers and borders) so type is never hidden by a later region's fill. */
function hoistMapLabels(){
  const cc=(typeof DATA!=='undefined' && DATA.country)||'';
  if(!/^(JP|KR|IT|ES)$/.test(cc)) return;
  const svg=$('#map'); if(!svg) return;
  const top=$('#g-lb'); if(!top) return;
  svg.appendChild(top);
  const gc=$('#g-ct');
  if(gc){
    gc.querySelectorAll('.ct text').forEach(t=>{
      const g=t.closest('.ct');
      t.dataset.kind=(g && g.classList.contains('cap'))?'capital':'city';
      t.classList.add('ct-label');
      if(g){
        if(g.classList.contains('cap')) t.classList.add('is-cap');
        if(g.classList.contains('major')) t.classList.add('is-major');
        t.dataset.owner=g.getAttribute('data-k')||'';
        if(!t.dataset.clickBound){
          t.dataset.clickBound='1';
          t.addEventListener('click', ev=>{ ev.stopPropagation(); g.dispatchEvent(new MouseEvent('click',{bubbles:true})); });
        }
      }
      top.appendChild(t);
    });
  }
  const ga=$('#g-ap');
  if(ga){
    ga.querySelectorAll('.ap text').forEach(t=>{
      const g=t.closest('.ap');
      if(!t.dataset.hoisted){
        let ox=0, oy=0;
        if(g){
          const tr=g.getAttribute('transform')||'';
          const m=/translate\(\s*([-+\d.eE]+)\s*[,\s]\s*([-+\d.eE]+)/.exec(tr);
          if(m){ ox=+m[1]; oy=+m[2]; }
        }
        const nx=+(t.getAttribute('x')||0)+ox;
        const ny=+(t.getAttribute('y')||0)+oy;
        t.setAttribute('x', nx);
        t.setAttribute('y', ny);
        t.querySelectorAll('tspan').forEach(ts=>ts.setAttribute('x', nx));
        if(t.dataset.ox!=null){
          t.dataset.ox=String(+t.dataset.ox+ox);
          t.dataset.oy=String(+t.dataset.oy+oy);
        }
        t.dataset.hoisted='1';
      }
      t.dataset.kind='airport';
      t.classList.add('ap-label');
      if(g && g.classList.contains('ap-zoomonly')) t.classList.add('ap-zoomonly');
      if(g){
        t.dataset.owner=g.getAttribute('data-code')||'';
        if(!t.dataset.clickBound){
          t.dataset.clickBound='1';
          t.addEventListener('click', ev=>{ ev.stopPropagation(); g.dispatchEvent(new MouseEvent('click',{bubbles:true})); });
        }
      }
      top.appendChild(t);
    });
  }
}
let _lblRaf=0;
function refreshLabels(){
  syncLabelScale();
  if(_lblRaf) cancelAnimationFrame(_lblRaf);
  _lblRaf=requestAnimationFrame(function(){
    _lblRaf=requestAnimationFrame(function(){
      _lblRaf=0;
      syncLabelScale();
      hoistMapLabels();
      resolveLabelOverlaps();
      if(typeof CFG.afterLabels==='function') CFG.afterLabels();
    });
  });
}

function applyViewBox(v){vb=v.slice();const m=$('#map');if(!m)return;
 const k=vb[2]/MAP_W;m.setAttribute('viewBox',vb.map(n=>+n.toFixed(2)).join(' '));m.style.setProperty('--k',k.toFixed(3));m.style.setProperty('--kt',Math.sqrt(k).toFixed(3));
 m.querySelectorAll('#g-ap .ap .ap-mark').forEach(g=>{g.setAttribute('transform',k>0.999?'':'scale('+k.toFixed(4)+')');});
 syncZoomUI()}
function isFull(){return vb[2]>=MAP_W-0.5}
function syncZoomUI(){const m=$('#map');if(!m)return;const full=isFull();m.classList.toggle('is-zoomed',!full);
 m.querySelectorAll('#g-ap .ap.ap-zoomonly').forEach(g=>g.setAttribute('tabindex', full?'-1':'0'));
 const zi=$('#zin'),zo=$('#zout'),zr=$('#zreset');
 if(zi)zi.disabled=vb[2]<=MINW+0.5;if(zo)zo.disabled=full;if(zr)zr.disabled=full;
 refreshLabels()}
function stopAnim(){if(animId){cancelAnimationFrame(animId);animId=0}}
function animateTo(t,ms){stopAnim();t=clampVB(t);const f=vb.slice(),t0=performance.now();ms=ms||350;
 (function an(n){const k=Math.min(1,(n-t0)/ms),e=k*(2-k);applyViewBox(f.map((v,i)=>v+(t[i]-v)*e));animId=k<1?requestAnimationFrame(an):0})(t0)}
/* Phones (<=900): zoom into the selected region. Desktop keeps free-zoom unless clearing selection. */
function zoomTo(a){let t=null;
 if(a&&innerWidth<=900){const node=$('#s-'+a);if(node){const b=node.getBBox();const w=Math.max(b.width*1.5,220),h=Math.max(b.height*1.5,150);const sc=Math.max(w/MAP_W,h/MAP_H);const W=MAP_W*sc,H=MAP_H*sc;t=[b.x+b.width/2-W/2,b.y+b.height/2-H/2,W,H];}}
 else if(!cur)t=FULL;
 if(t)animateTo(t,350)}
function zoomAt(px,py,f,ms){const w=Math.min(MAP_W,Math.max(MINW,vb[2]/f)),s=w/vb[2];
 const t=[px-(px-vb[0])*s,py-(py-vb[1])*s,w,w*MAP_H/MAP_W];if(ms)animateTo(t,ms);else{stopAnim();applyViewBox(clampVB(t))}}

function render(html){
  const p=$('#panel'); p.innerHTML=html; p.scrollTop=0; applyStep(false);
  p.querySelectorAll('[data-city]').forEach(b=>b.onclick=()=>selectCity(b.dataset.s,b.dataset.city));
  p.querySelectorAll('[data-state]').forEach(b=>b.onclick=()=>selectRegion(b.dataset.state));
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
/* ---------- selections: same flow as usa-map.js (state → city → airport, hash, crumbs) ---------- */
function setHash(a,n){
  const h=n?a+'/'+encodeURIComponent(n):a;
  if(decodeURIComponent(location.hash.replace(/^#/,''))!==(n?a+'/'+n:a)) history.replaceState(null,'','#'+h);
}
function airportsFor(a, city){ return AIRPORTS.filter(ap => (ap.province||ap.state)===a && (!city || ap.city===city)); }
function airportChips(list, heading){
  if(!list.length) return '';
  return `<h4 class="hd">${esc(heading)}</h4><div class="citylist">${list.map(ap=>`<button type="button" class="apbtn" data-ap="${esc(ap.code)}" aria-label="${esc(ap.code)}, ${esc(ap.city)}">${esc(ap.code)} — ${esc(ap.city)}</button>`).join('')}</div>`;
}
function cityButtons(a){
  const list = GEO[a].cities||[];
  if(!list.length) return '';
  return `<h4 class="hd">${esc(mapPanelMainCities())}</h4><div class="citylist">${list.map(c=>`<button type="button" data-s="${a}" data-city="${esc(c.n)}" class="${c.sample?'sample':''}">${esc(c.n)}${c.cap?' (capital)':''}</button>`).join('')}</div>`;
}
function selectRegion(a){
    document.querySelectorAll('#g-st path.st:focus, #g-st path.st:focus-visible').forEach(function(el){ try{el.blur()}catch(_){ } });
cur={a}; hilite(a); setHash(a);
  const s=GEO[a];
  const hubs=hubForRegion(a);
  const hubNote = hubs.length ? ` · hub ${hubs.map(h=>h.iata).join(', ')}` : '';
  render(header(a, s.name, `${a} · ${DATA.unit}${hubNote}`) + cityButtons(a) +
    lawSection(a)+roadSection(a)+planeSection(a)+hotelSection(a)+groomSection(a));
}
function selectCity(a, n){
  const st=GEO[a]; if(!st) return;
  const key=a+'|'+n; cur={a,n}; hilite(a,key); setHash(a,n);
  const crumbs=`<p class="crumbs"><button type="button" data-state="${a}">← ${esc(st.name)}</button> · ${esc(n)}</p>`;
  const aps=airportsFor(a,n);
  const hub=aps.map(ap=>DATA.hubs[ap.code]).find(h=>h&&h.hotel_q);
  render(crumbs+header(a, n, `${esc(st.name)} · city`)+airportChips(aps, 'Airports serving '+n)+
    lawSection(a)+roadSection(a)+planeSection(a)+hotelSection(a, hub?hub.hotel_q:n+', '+st.name)+groomSection(a));
}
function airHead(ap){
  const a=ap.province||ap.state;
  const title=ap.name?`${esc(ap.code)} — ${esc(ap.name)}`:`${esc(ap.code)} — ${esc(ap.city)}`;
  const page=ap.page?`<div class="links" style="margin-top:6px">${lk('🛫', ap.code+' airport page', ap.name||ap.city, ap.page, 'off').replace('Official','Site')}</div>`:'';
  return `<div class="ph"><div class="ap-badge" aria-hidden="true"><svg viewBox="0 0 24 24" width="28" height="28"><path fill="#d9b765" d="${PLANE}"/></svg><b>${esc(ap.code)}</b></div><div><h2>${title}</h2><div class="sub">${esc(ap.city)} · ${esc(GEO[a]?GEO[a].name:a)}</div>${page}</div></div>`;
}
function selectAirport(code){
  const ap = AIRPORTS.find(x=>x.code===code); if(!ap) return;
  const a = ap.province || ap.state;
  step=3;
  cur={a,n:ap.city,ap:code}; hilite(a, a+'|'+ap.city, code); setHash(a, code);
  const st=GEO[a];
  const crumbs=`<p class="crumbs"><button type="button" data-state="${a}">← ${esc(st.name)}</button> · <button type="button" data-s="${a}" data-city="${esc(ap.city)}">${esc(ap.city)}</button> · ${esc(code)}</p>`;
  const hub=DATA.hubs[code];
  render(crumbs+airHead(ap)+
    `<div class="btnrow" style="margin:0 0 4px"><button type="button" class="btn" data-s="${a}" data-city="${esc(ap.city)}">City panel: ${esc(ap.city)}</button></div>`+
    lawSection(a)+roadSection(a)+planeSection(a, code)+hotelSection(a, hub&&hub.hotel_q)+groomSection(a));
  applyStep(true);
}
/* USA showAllStates(): clear selection, zoom, hash and panel. */
function resetAll(){
  cur=null; hilite(null);
  if(location.hash) try{ history.replaceState(null,'',location.pathname+location.search) }catch(_){ location.hash='' }
  empty(); const r=$('#reset'); if(r) r.hidden=true; const pk=$('#pick'); if(pk) pk.value='';
}
/* USA empty(): "Pick a state or city" + city and airport shortcuts. */
function empty(){
  const cities=[]; for(const a of ABBRS) for(const c of (GEO[a].cities||[])) if(c.sample) cities.push([a,c.n]);
  $('#panel').innerHTML=`<div class="empty"><div class="big">${esc(mapPickTitle())}</div><p>${esc(mapClickLead())}</p>`+
    (cities.length?`<div class="citylist">${cities.map(([a,n])=>`<button type="button" class="sample" data-s="${a}" data-city="${esc(n)}">${esc(n)}</button>`).join('')}</div>`:'')+
    `<div class="citylist">${AIRPORTS.map(ap=>`<button type="button" class="apbtn" data-ap="${esc(ap.code)}">${esc(ap.code)} — ${esc(ap.city)}</button>`).join('')}</div><p class="disc">${esc(mapJourneyOrder())}</p></div>`;
  $('#panel').querySelectorAll('[data-city]').forEach(b=>b.onclick=()=>selectCity(b.dataset.s,b.dataset.city));
  $('#panel').querySelectorAll('[data-ap]').forEach(b=>b.onclick=()=>selectAirport(b.dataset.ap));
}

/* Default hub region when a journey step is pressed with nothing selected (mirrors USA → NYC). */
function defaultRegion(){
  if(DATA.country==='KR' && GEO['11']) return '11'; /* Seoul */
  if(DATA.country==='JP' && GEO['13']) return '13'; /* Tokyo */
  if(DATA.country==='AU' && GEO['VIC']) return 'VIC'; /* Melbourne PEQ arrival */

  if(DATA.country==='CA') return 'ON';
  if(DATA.country==='MX') return 'CMX';
  if(DATA.country==='UK') return 'ENG';
  if(DATA.country==='FR') return 'IDF';
  if(DATA.country==='DE') return 'BY';
  if(DATA.country==='IT') return 'LAZ';
  if(DATA.country==='ES') return 'MD';
  const hubs = DATA.provHub || DATA.stateHub || {};
  return Object.keys(hubs)[0] || ABBRS[0];
}

/* ---------- steps + free zoom/pan + init ---------- */
function initSteps(){
  document.querySelectorAll('#steps button').forEach(b=>{
    b.addEventListener('click',()=>{
      step=+b.dataset.step;
      /* Same as USA (auto-selects NYC): with nothing selected, open the default hub city, then scroll to the step. */
      if(!cur){ const r=defaultRegion(); const c=(GEO[r].cities||[])[0]; c?selectCity(r,c.n):selectRegion(r); }
      applyStep(true);
    });
  });
  const reset=$('#reset'); if(reset){ reset.classList.remove('ghost'); reset.classList.add('reset-all'); reset.onclick=resetAll; }
  /* USA: Escape clears the selection (capture phase, an open site menu keeps Escape) */
  window.addEventListener('keydown',e=>{
    if(e.key!=='Escape'||!cur||e.defaultPrevented) return;
    const sm=document.getElementById('site-menu'); if(sm&&sm.classList.contains('open')) return;
    resetAll();
  },true);
}

/* Free zoom & pan — same UX as usa-map.js (wheel, drag, pinch, sideways pan, +/−/reset). */
function initFreeZoom(){const m=$('#map');if(!m)return;
 let wrap=m.parentNode;if(!wrap.classList.contains('mapwrap')){wrap=document.createElement('div');wrap.className='mapwrap';m.parentNode.insertBefore(wrap,m);wrap.appendChild(m)}
 /* Country-specific empty-space placement: CA Pacific SW, MX Pacific SW (desktop). Mobile: under map. */
 wrap.classList.add('zoom-pos-'+({MX:'mx',CA:'ca',UK:'uk',FR:'fr',DE:'de',KR:'kr',JP:'jp',IT:'it',ES:'es'}[DATA.country]||'ca'));
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
 const perPx=()=>vb[2]/(m.getBoundingClientRect().width||MAP_W);
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
   const w=Math.min(MAP_W,Math.max(MINW,T0[2]*P0.d/dist(a,b))),h=w*MAP_H/MAP_W;
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
buildSwitcher(); buildMap(); initSteps(); initFreeZoom(); applyViewBox(FULL); empty();
 window.PPC_mapView={zoomAt:typeof zoomAt==='function'?zoomAt:null, applyViewBox, refreshLabels, isFull};
 (function(){const m=$('#map'); if(!m||typeof ResizeObserver==='undefined'){window.addEventListener('resize',refreshLabels);return;}
  const ro=new ResizeObserver(()=>refreshLabels()); ro.observe(m);})();

// deep links (USA rules): #ON · #ON/Toronto · #QC/YUL · #YYZ
{
  const raw=decodeURIComponent((location.hash||'').replace(/^#/,'').replace(/\+/g,' '));
  const slash=raw.indexOf('/');
  const isAp=c=>AIRPORTS.some(x=>x.code===c);
  if(slash>0){ const a=raw.slice(0,slash), n=raw.slice(slash+1);
    if(isAp(n)) selectAirport(n);
    else if(GEO[a]&&(GEO[a].cities||[]).some(c=>c.n===n)) selectCity(a,n);
    else if(GEO[a]) selectRegion(a);
  } else if(isAp(raw)) selectAirport(raw);
  else if(GEO[raw]) selectRegion(raw);
}
})();
