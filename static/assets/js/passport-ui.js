/* ES dynamic strings when on /es/ passport */
(function(){
  var ES={
    copied:'copiado ✓',
    critical:'⛔ Crítico',
    watch:'⚠️ Atención',
    source:'fuente',
    official:'oficial',
    noTrap:'No se detectó ninguna trampa especial para esta ruta. Consulte igual los enlaces oficiales.',
    cabin:'Cabina',
    weight:'Peso',
    carrier:'Transportadora',
    notPub:'sin publicar',
    airOfficial:'Página oficial de la aerolínea',
    checked:'verificado',
    trapsH:'Trampas en esta ruta',
    timelineH:'Cronograma de cuenta atrás',
    partnersH:'Socios de la ruta',
    vetH:'Veterinario patrocinado / socio de certificado de salud',
    vetB:'Clínica acreditada por USDA para esta ruta (certificado D-10). ',
    become:'Conviértase en socio de ruta →',
    carrierH:'Socio verificado de transportadora / seguro',
    carrierB:'Transportista de mascotas o seguro de viaje para este corredor. ',
    arrivalVet:'Veterinario verificado cerca de la llegada',
    featureClinic:'Destacar su clínica →',
    groomerH:'Peluquero verificado (baño post-vuelo)',
    featureSalon:'Destacar su salón →',
    after:'Después de aterrizar:',
    scan:'Escanee: esta misma ruta, siempre al día',
    clinicHere:'Su clínica aquí · Conviértase en socio de ruta: petpolicycheck.com/partners',
    brandHere:'Su marca aquí · Conviértase en socio de ruta: petpolicycheck.com/partners',
    generated:function(d){return 'Generado el '+d+' a partir de fuentes oficiales (CDC, USDA APHIS, CFIA, GOV.UK, UE, SENASICA). Las normas cambian: vuelva a comprobar antes de cada paso. No es asesoría legal ni veterinaria.';},
    back:' de regreso'
  };
  function lang(){
    try{
      if((document.documentElement.getAttribute('data-ppc-locale')||'')==='es') return 'es';
      if((location.pathname||'').indexOf('/es/')===0) return 'es';
      if((document.documentElement.lang||'').toLowerCase().indexOf('es')===0) return 'es';
    }catch(e){}
    return 'en';
  }
  window.PPC_PASS_I18N={lang:lang,es:ES,t:function(k,en){return lang()==='es'&&ES[k]!=null?(typeof ES[k]==='function'?ES[k]:ES[k]):en;}};
})();

/* Pet Travel Passport UI — from innov #1 preview */

const D = window.PPC_PASSPORT_DATA, F = D.frame, $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const C = Object.entries(F.countries);
['from','to'].forEach(id => C.forEach(([k, v]) => $('#'+id).insertAdjacentHTML('beforeend', `<option value="${k}">${esc(v.name)}</option>`)));
F.us_states.forEach(s => $('#state').insertAdjacentHTML('beforeend', `<option value="${s.code}">${esc(s.name)}</option>`));
D.airlines.forEach(a => $('#airline').insertAdjacentHTML('beforeend', `<option value="${a.id}">${esc(a.name)}</option>`));
// prefill from URL (?from=US&to=MX&pet=dog&airline=delta&return=1&date=...)
const P = new URLSearchParams(location.search);
$('#from').value = P.get('from') || 'US'; $('#to').value = P.get('to') || 'MX'; $('#state').value = P.get('state') || '';
$('#airline').value = P.get('airline') || 'delta'; $('#pet').value = P.get('pet') || 'dog'; $('#ret').value = P.get('return') || '1';
$('#date').value = P.get('date') || ''; $('#retDate').value = P.get('retdate') || '';
const partnerCTA = route => `https://petpolicycheck.com/partners/route-partner.html?route=${encodeURIComponent(route)}&utm_source=passport`;
function render(){
  const inp = { from: $('#from').value, to: $('#to').value, state: $('#state').value || null, airline: $('#airline').value || null, pet: $('#pet').value, ret: $('#ret').value === '1', date: $('#date').value || null, retDate: $('#retDate').value || null };
  const R = PPCPassport.computePassport(inp, D), route = R.legs.map(l => l.from).concat(R.legs.at(-1).to).join('-');
  $('#share').href = R.url; $('#share').onclick = e => { e.preventDefault(); navigator.clipboard && navigator.clipboard.writeText(R.url); $('#share').textContent = (window.PPC_PASS_I18N?PPC_PASS_I18N.t('copied','copied ✓'):'copied ✓'); };
  const traps = R.traps.map(t => `<div class="trap ${t.level}" data-dept="laws"><b>${t.level === 'critical' ? (window.PPC_PASS_I18N?PPC_PASS_I18N.t('critical','⛔ Critical'):'⛔ Critical') : (window.PPC_PASS_I18N?PPC_PASS_I18N.t('watch','⚠️ Watch'):'⚠️ Watch')}:</b> ${esc(t.text)} <a href="${esc(t.source)}" target="_blank" rel="noopener">${window.PPC_PASS_I18N?PPC_PASS_I18N.t('source','source'):'source'}</a></div>`).join('') || `<p>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('noTrap','No special trap detected for this route. Still check the official links.'):'No special trap detected for this route. Still check the official links.'}</p>`;
  const tl = R.timeline.map(t => `<li><div class="when">${t.when}<small>${t.date || ''}</small></div><div><div class="leg">Leg ${t.leg}: ${esc(t.legLabel)}</div>${esc(t.text)}${t.source ? ` <a href="${esc(t.source)}" target="_blank" rel="noopener">${window.PPC_PASS_I18N?PPC_PASS_I18N.t('official','official'):'official'}</a>` : ''}</div></li>`).join('');
  const A = R.airline, air = A ? `<div class="card air" data-dept="plane"><h2>✈️ ${esc(A.name)}</h2>
    ${A.cabinOK ? `<p>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('cabin','Cabin'):'Cabin'}: <b>${esc(A.cabin_fee_usd_or_local)}</b><br>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('weight','Weight'):'Weight'}: ${esc(A.max_weight_cabin_lb_kg)}<br>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('carrier','Carrier'):'Carrier'}: ${esc((A.underseat_soft_dims_in_cm||[window.PPC_PASS_I18N?PPC_PASS_I18N.t('notPub','not published'):'not published']).join(' / '))}</p>` : ''}
    ${A.warn.map(w => `<p class="warn">${esc(w)}</p>`).join('')}<p><a href="${esc(A.official_policy_url)}" target="_blank" rel="noopener">${window.PPC_PASS_I18N?PPC_PASS_I18N.t('airOfficial','Airline official page'):'Airline official page'}</a> · ${window.PPC_PASS_I18N?PPC_PASS_I18N.t('checked','checked'):'checked'} ${esc(A.last_verified)}</p></div>` : '';
  const slots = `<div class="partners" data-dept="hotel">
    <div class="slot" data-slot="sponsored_vet"><b>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('vetH','Sponsored Vet / Health Certificate Partner'):'Sponsored Vet / Health Certificate Partner'}</b>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('vetB','USDA-accredited clinic for this route (D-10 certificate). '):'USDA-accredited clinic for this route (D-10 certificate). '}<a href="${partnerCTA(route)}&slot=vet">${window.PPC_PASS_I18N?PPC_PASS_I18N.t('become','Become a Route Partner →'):'Become a Route Partner →'}</a></div>
    <div class="slot" data-slot="verified_carrier_insurance"><b>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('carrierH','Verified Carrier / Insurance Partner'):'Verified Carrier / Insurance Partner'}</b>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('carrierB','Pet shipper or travel insurance for this corridor. '):'Pet shipper or travel insurance for this corridor. '}<a href="${partnerCTA(route)}&slot=carrier">${window.PPC_PASS_I18N?PPC_PASS_I18N.t('become','Become a Route Partner →'):'Become a Route Partner →'}</a></div></div>`;
  const PA = R.postArrival, post = `<div class="card post" data-dept="hotel"><h2>🛁 ${esc(PA.title)}${PA.city_hint ? ' · ' + esc(PA.city_hint) : ''}</h2><p>${esc(PA.text)}</p>
    <div class="partners"><div class="slot" data-slot="verified_vet_arrival"><b>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('arrivalVet','Verified Vet near arrival'):'Verified Vet near arrival'}</b>PPC Verified · Track 3 <a href="${partnerCTA(route)}&slot=arrival_vet">${window.PPC_PASS_I18N?PPC_PASS_I18N.t('featureClinic','Feature your clinic →'):'Feature your clinic →'}</a></div>
    <div class="slot" data-slot="verified_groomer_arrival"><b>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('groomerH','Verified Groomer (post-flight bath'):'Verified Groomer (post-flight bath)'}</b>PPC Verified · Track 4, no membership needed <a href="${partnerCTA(route)}&slot=groomer">${window.PPC_PASS_I18N?PPC_PASS_I18N.t('featureSalon','Feature your salon →'):'Feature your salon →'}</a></div></div></div>`;
  $('#out').innerHTML = `<div class="card" data-dept="laws"><h2>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('trapsH','Traps on this route'):'Traps on this route'}</h2>${traps}</div>${air}
    <div class="card" data-dept="laws"><h2>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('timelineH','Countdown timeline'):'Countdown timeline'}</h2><ul class="tl">${tl}</ul></div>${post}
    <div class="card" data-dept="hotel"><h2>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('partnersH','Route partners'):'Route partners'}</h2>${slots}</div>`;
  // QR (offline lib, MIT)
  const qr = qrcode(0, 'M'); qr.addData(R.qrUrl); qr.make();
  const name = c => (F.countries[c] || {}).name || c;
  $('#pass').innerHTML = `<div class="bp"><div class="bp-top"><div><div style="font-size:11px;letter-spacing:2px">PET TRAVEL PASSPORT · PETPOLICYCHECK.COM</div>
    <div class="bp-route">${R.legs.map(l => l.from).concat(R.legs.at(-1).to).join(' ✈ ')}</div><div>${esc(name(inp.from))} → ${esc(name(inp.to))}${inp.ret ? (window.PPC_PASS_I18N&&PPC_PASS_I18N.lang()==='es'?' →'+PPC_PASS_I18N.es.back:' → back') : ''}${inp.state ? ' · ' + inp.state : ''}</div></div>
    <div style="text-align:right"><div>PET: <b>${inp.pet.toUpperCase()}</b></div><div>AIRLINE: <b>${A ? esc(A.iata) : '—'}</b></div><div>DEP: <b>${inp.date || '—'}</b></div></div></div>
    <div class="bp-body"><div>${R.traps.map(t => `<div class="bp-trap"><b>${t.level.toUpperCase()}</b> ${esc(t.text)}</div>`).join('')}
      <ol>${R.timeline.map(t => `<li><b>${t.when}${t.date ? ' (' + t.date + ')' : ''}</b> · L${t.leg}: ${esc(t.text.length > 190 ? t.text.slice(0, 187) + '…' : t.text)}</li>`).join('')}</ol>
      <p><b>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('after','After landing:'):'After landing:'}</b> ${esc(PA.text.slice(0, 200))}</p></div>
      <div class="qr">${qr.createSvgTag({ cellSize: 3, margin: 0, scalable: true })}<div style="font-size:9px">${window.PPC_PASS_I18N?PPC_PASS_I18N.t('scan','Scan: this exact route, always up to date'):'Scan: this exact route, always up to date'}</div></div></div>
    <div class="bp-foot"><div class="bp-slot"><b>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('vetH','Sponsored Vet / Health Certificate Partner'):'Sponsored Vet / Health Certificate Partner'}</b><br>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('clinicHere','Your clinic here · Become a Route Partner: petpolicycheck.com/partners'):'Your clinic here · Become a Route Partner: petpolicycheck.com/partners'}</div>
    <div class="bp-slot"><b>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('carrierH','Verified Carrier / Insurance Partner'):'Verified Carrier / Insurance Partner'}</b><br>${window.PPC_PASS_I18N?PPC_PASS_I18N.t('brandHere','Your brand here · Become a Route Partner: petpolicycheck.com/partners'):'Your brand here · Become a Route Partner: petpolicycheck.com/partners'}</div></div>
    <div style="padding:0 14px 8px;font-size:9px;color:#555">${(window.PPC_PASS_I18N&&PPC_PASS_I18N.lang()==='es')?PPC_PASS_I18N.es.generated(new Date().toISOString().slice(0,10)):('Generated '+new Date().toISOString().slice(0,10)+' from official sources (CDC, USDA APHIS, CFIA, GOV.UK, EU, SENASICA). Rules change: rescan before each step. Not legal or veterinary advice.')}</div></div>`;
}
document.querySelectorAll('#f select,#f input').forEach(e => e.addEventListener('input', render));
$('#print').onclick = () => window.print();
render();

