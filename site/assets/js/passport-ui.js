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
  $('#share').href = R.url; $('#share').onclick = e => { e.preventDefault(); navigator.clipboard && navigator.clipboard.writeText(R.url); $('#share').textContent = 'copied ✓'; };
  const traps = R.traps.map(t => `<div class="trap ${t.level}" data-dept="laws"><b>${t.level === 'critical' ? '⛔ Critical' : '⚠️ Watch'}:</b> ${esc(t.text)} <a href="${esc(t.source)}" target="_blank" rel="noopener">source</a></div>`).join('') || '<p>No special trap detected for this route. Still check the official links.</p>';
  const tl = R.timeline.map(t => `<li><div class="when">${t.when}<small>${t.date || ''}</small></div><div><div class="leg">Leg ${t.leg}: ${esc(t.legLabel)}</div>${esc(t.text)}${t.source ? ` <a href="${esc(t.source)}" target="_blank" rel="noopener">official</a>` : ''}</div></li>`).join('');
  const A = R.airline, air = A ? `<div class="card air" data-dept="plane"><h2>✈️ ${esc(A.name)}</h2>
    ${A.cabinOK ? `<p>Cabin: <b>${esc(A.cabin_fee_usd_or_local)}</b><br>Weight: ${esc(A.max_weight_cabin_lb_kg)}<br>Carrier: ${esc((A.underseat_soft_dims_in_cm||['not published']).join(' / '))}</p>` : ''}
    ${A.warn.map(w => `<p class="warn">${esc(w)}</p>`).join('')}<p><a href="${esc(A.official_policy_url)}" target="_blank" rel="noopener">Airline official page</a> · checked ${esc(A.last_verified)}</p></div>` : '';
  const slots = `<div class="partners" data-dept="hotel">
    <div class="slot" data-slot="sponsored_vet"><b>Sponsored Vet / Health Certificate Partner</b>USDA-accredited clinic for this route (D-10 certificate). <a href="${partnerCTA(route)}&slot=vet">Become a Route Partner →</a></div>
    <div class="slot" data-slot="verified_carrier_insurance"><b>Verified Carrier / Insurance Partner</b>Pet shipper or travel insurance for this corridor. <a href="${partnerCTA(route)}&slot=carrier">Become a Route Partner →</a></div></div>`;
  const PA = R.postArrival, post = `<div class="card post" data-dept="hotel"><h2>🛁 ${esc(PA.title)}${PA.city_hint ? ' · ' + esc(PA.city_hint) : ''}</h2><p>${esc(PA.text)}</p>
    <div class="partners"><div class="slot" data-slot="verified_vet_arrival"><b>Verified Vet near arrival</b>PPC Verified · Track 3 <a href="${partnerCTA(route)}&slot=arrival_vet">Feature your clinic →</a></div>
    <div class="slot" data-slot="verified_groomer_arrival"><b>Verified Groomer (post-flight bath)</b>PPC Verified · Track 4, no membership needed <a href="${partnerCTA(route)}&slot=groomer">Feature your salon →</a></div></div></div>`;
  $('#out').innerHTML = `<div class="card" data-dept="laws"><h2>Traps on this route</h2>${traps}</div>${air}
    <div class="card" data-dept="laws"><h2>Countdown timeline</h2><ul class="tl">${tl}</ul></div>${post}
    <div class="card" data-dept="hotel"><h2>Route partners</h2>${slots}</div>`;
  // QR (offline lib, MIT)
  const qr = qrcode(0, 'M'); qr.addData(R.qrUrl); qr.make();
  const name = c => (F.countries[c] || {}).name || c;
  $('#pass').innerHTML = `<div class="bp"><div class="bp-top"><div><div style="font-size:11px;letter-spacing:2px">PET TRAVEL PASSPORT · PETPOLICYCHECK.COM</div>
    <div class="bp-route">${R.legs.map(l => l.from).concat(R.legs.at(-1).to).join(' ✈ ')}</div><div>${esc(name(inp.from))} → ${esc(name(inp.to))}${inp.ret ? ' → back' : ''}${inp.state ? ' · ' + inp.state : ''}</div></div>
    <div style="text-align:right"><div>PET: <b>${inp.pet.toUpperCase()}</b></div><div>AIRLINE: <b>${A ? esc(A.iata) : '—'}</b></div><div>DEP: <b>${inp.date || '—'}</b></div></div></div>
    <div class="bp-body"><div>${R.traps.map(t => `<div class="bp-trap"><b>${t.level.toUpperCase()}</b> ${esc(t.text)}</div>`).join('')}
      <ol>${R.timeline.map(t => `<li><b>${t.when}${t.date ? ' (' + t.date + ')' : ''}</b> · L${t.leg}: ${esc(t.text.length > 190 ? t.text.slice(0, 187) + '…' : t.text)}</li>`).join('')}</ol>
      <p><b>After landing:</b> ${esc(PA.text.slice(0, 200))}</p></div>
      <div class="qr">${qr.createSvgTag({ cellSize: 3, margin: 0, scalable: true })}<div style="font-size:9px">Scan: this exact route, always up to date</div></div></div>
    <div class="bp-foot"><div class="bp-slot"><b>Sponsored Vet / Health Certificate Partner</b><br>Your clinic here · Become a Route Partner: petpolicycheck.com/partners</div>
    <div class="bp-slot"><b>Verified Carrier / Insurance Partner</b><br>Your brand here · Become a Route Partner: petpolicycheck.com/partners</div></div>
    <div style="padding:0 14px 8px;font-size:9px;color:#555">Generated ${new Date().toISOString().slice(0,10)} from official sources (CDC, USDA APHIS, CFIA, GOV.UK, EU, SENASICA). Rules change: rescan before each step. Not legal or veterinary advice.</div></div>`;
}
document.querySelectorAll('#f select,#f input').forEach(e => e.addEventListener('input', render));
$('#print').onclick = () => window.print();
render();

