/* PetPolicyCheck airline comparator UI — v2 (2026-11-07): search, i18n (6 langs), mobile cards, "Check with airline" for unverified values */
const DATA = window.PPC_COMPARATOR;
let militaryOn = new URLSearchParams(location.search).get('military') === '1';
let militaryData = null, militaryFailed = false;

const A = DATA.airlines, $ = s => document.querySelector(s);
const EN_FALLBACK = (window.PPC_I18N && window.PPC_I18N.strings && window.PPC_I18N.strings.en) || {};
function t(k, vars){
  let v = (window.PPC_LANG && window.PPC_LANG.t(k)) || EN_FALLBACK[k] || k;
  if (vars) Object.keys(vars).forEach(n => { v = v.split('{' + n + '}').join(vars[n]); });
  return v; }
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fold = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const cabinOK = a => !!(a.cabin_dogs || a.cabin_cats);
const NOLIM = ['none_stated', 'explicit_no_limit'];
const REGIONS = [...new Set(A.map(a => a.region))].sort();
function check(){ return `<span class="chk">${esc(t('compare.check'))}</span>`; }
function parseDims(str){ // "18 x 14 x 9 in (..)" → {L,W,H,unit}
  const m = String(str).match(/(\d+(?:\.\d+)?)\s*(?:L\s*)?x\s*(\d+(?:\.\d+)?)\s*(?:W\s*|H\s*)?x\s*(\d+(?:\.\d+)?)\s*(?:H\s*|W\s*)?(cm|in)/i);
  return m ? {L:+m[1], W:+m[2], H:+m[3], unit:m[4].toLowerCase()} : null; }
function fits(a){
  const L = +$('#cL').value, W = +$('#cW').value, H = +$('#cH').value; if(!(L && W && H)) return null;
  const k = $('#cU').value === 'cm' ? 1 : 2.54, mine = [L*k, W*k, H*k];
  const opts = (a.underseat_soft_dims_in_cm || []).map(parseDims).filter(Boolean);
  if(!opts.length) return cabinOK(a) ? 'unknown' : null;
  return opts.some(o => { const f = o.unit === 'cm' ? 1 : 2.54; return mine[0] <= o.L*f && mine[1] <= o.W*f && mine[2] <= o.H*f; }) ? 'ok' : 'ko'; }
function rowsFiltered(useCabin = true){
  const q = fold($('#fQ').value);
  if (militaryOn) return A.filter(a => (!$('#fRegion').value || a.region === $('#fRegion').value)
    && (!q || fold(a.name + ' ' + a.iata + ' ' + a.id).includes(q)))
    .sort((a,b) => militaryRank(b) - militaryRank(a) || a.name.localeCompare(b.name));
  let r = A.filter(a => (!$('#fDog').checked || a.cabin_dogs) && (!$('#fCat').checked || a.cabin_cats)
    && (!useCabin || !$('#fCabin').checked || cabinOK(a))
    && (!$('#fNoLimit').checked || NOLIM.includes(a.weight_limit_type))
    && (!$('#fCargo').checked || a.cargo_or_checked_allowed === true)
    && (!$('#fRegion').value || a.region === $('#fRegion').value)
    && (!q || fold(a.name + ' ' + a.iata + ' ' + a.id).includes(q)));
  const s = $('#fSort').value, key = s === 'long' ? 'fee_usd_long' : 'fee_usd_short';
  r.sort((x, y) => s === 'name' ? x.name.localeCompare(y.name) : ((x[key] ?? 1e9) - (y[key] ?? 1e9)) || x.name.localeCompare(y.name));
  return r; }
function cell(label, html, cls){ return `<td${cls ? ` class="${cls}"` : ''} data-label="${esc(label)}"><div class="v">${html}</div></td>`; }
function militaryRank(a){
  const d = militaryData && militaryData.airlines[a.id];
  return d ? (d.service.status === 'verified' ? 1 : 0) + (d.military.some(f => f.status === 'verified') ? 2 : 0) : 0;
}
function militaryFact(f){
  if (!f || f.status !== 'verified') return `<p class="mil-unknown">${esc(t('mil.unknown'))}</p>`;
  return `<div class="mil-fact">${f.keys.map(k=>`<p>${esc(t(k))}</p>`).join('')}
    <p class="mil-evidence"><a href="${esc(f.url)}" rel="noopener" target="_blank">${esc(t('mil.source'))} ↗</a>
    <span>${esc(t('mil.checked',{d:f.checked}))}</span></p></div>`;
}
function renderMilitary(){
  const r = rowsFiltered();
  $('#count').textContent = t('compare.count', {n:r.length,t:A.length});
  $('#mil-dot-date').textContent = $('#mil-amc-date').textContent = militaryData ? t('mil.checked',{d:militaryData.meta.checked_date}) : '';
  $('#military-results').innerHTML = !militaryData ? `<p role="status">${esc(t(militaryFailed?'mil.error':'mil.loading'))}</p>` : !r.length ? `<p>${esc(t('compare.count.none'))}</p>` : r.map(a=>{
    const d = militaryData.airlines[a.id];
    return `<article class="mil-card" data-slug="${esc(a.id)}"><header><h3>${esc(a.name)}</h3><small>${esc(a.iata)} · ${esc(t('compare.r.'+a.region))}</small></header>
      <section><h4>${esc(t('mil.service'))}</h4>${militaryFact(d && d.service)}</section>
      <section><h4>${esc(t('mil.military'))}</h4>${(d ? d.military : [null]).map(militaryFact).join('')}</section>
      <p class="mil-policy"><a href="${esc(d ? d.official_policy_url : a.official_policy_url)}" target="_blank" rel="noopener">${esc(t('mil.policy'))} ↗</a></p></article>`;
  }).join('');
}
function setMilitary(on, updateURL){
  militaryOn = on;
  $('#fMilitary').checked = on;
  document.body.classList.toggle('military-mode', on);
  $('#milNote').hidden = $('#military-results').hidden = $('#mil-unknown-note').hidden = !on;
  const meta = document.querySelector('meta[name="theme-color"]');
  meta.content = on ? '#001f3f' : '#0b1719';
  if(updateURL){const u=new URL(location.href);if(on)u.searchParams.set('military','1');else u.searchParams.delete('military');history.replaceState(history.state,'',u);}
  $('#comparator-heading').setAttribute('data-i18n', on ? 'mil.title' : 'compare.h1');
  $('#comparator-heading').textContent = t(on ? 'mil.title' : 'compare.h1');
  render();
}
function render(){
  if (militaryOn) { renderMilitary(); return; }

  const r = rowsFiltered(), all = rowsFiltered(false), hidden = all.length - r.length;
  let c = t('compare.count', {n: r.length, t: A.length});
  if ($('#fCabin').checked && hidden > 0) c += ' · ' + t('compare.count.cabin', {h: hidden});
  $('#count').textContent = c;
  const L = k => t('compare.col.' + k);
  $('#tb').innerHTML = !r.length ? `<tr><td colspan="8" class="empty">${esc(t('compare.count.none'))}</td></tr>` : r.map(a => {
    const f = fits(a), cab = cabinOK(a), rev = /needs_review|needs_recheck|secondary/.test(a.verification_level || '');
    const dims = a.underseat_soft_dims_in_cm && a.underseat_soft_dims_in_cm.length ? a.underseat_soft_dims_in_cm.map(esc).join('<br>') : (cab ? check() : esc(t('compare.na_nocabin')));
    const fee = a.cabin_fee_usd_or_local ? esc(a.cabin_fee_usd_or_local) : (cab ? check() : `<span class="n">${esc(t('compare.nocabin'))}</span>`);
    const wt = a.max_weight_cabin_lb_kg ? esc(a.max_weight_cabin_lb_kg) + (NOLIM.includes(a.weight_limit_type) ? `<br><span class="pill nolimit">${esc(t('compare.nolimit'))}</span>` : '') : check();
    const src = a.official_policy_url ? `<a href="${esc(a.official_policy_url)}" rel="noopener" target="_blank">${esc(t('compare.official'))} ↗</a>` : check();
    const guide = a.ppc_guide_url ? ` · <a href="${esc(a.ppc_guide_url)}">${esc(t('compare.guide'))}</a>` : '';
    const when = a.last_verified ? `<small class="ver">${esc(t('compare.checked', {d: a.last_verified}))}</small>` : `<small class="ver">${check()}</small>`;
    return `<tr data-dept="plane" data-slug="${esc(a.id)}">
    <td class="name" data-label="${esc(L('airline'))}"><b>${esc(a.name)}</b><small>${esc(a.iata)} · ${esc(t('compare.r.' + a.region))}</small>${rev ? `<br><span class="pill rev">${esc(t('compare.rev'))}</span>` : ''}</td>
    ${cell(L('dogscats'), `${a.cabin_dogs ? `<span class="y">${esc(t('compare.dogs.y'))}</span>` : `<span class="n">${esc(t('compare.dogs.n'))}</span>`}<br>${a.cabin_cats ? `<span class="y">${esc(t('compare.cats.y'))}</span>` : `<span class="n">${esc(t('compare.cats.n'))}</span>`}`)}
    ${cell(L('fee'), fee)}
    ${cell(L('weight'), wt)}
    ${cell(L('dims'), dims + (f ? `<br><span class="fit ${f === 'ok' ? 'ok' : 'ko'}">${esc(t(f === 'ok' ? 'compare.fit.ok' : f === 'ko' ? 'compare.fit.ko' : 'compare.fit.unk'))}</span>` : ''))}
    ${cell(L('hold'), a.cargo_fee_note ? esc(a.cargo_fee_note) : check())}
    ${cell(L('snub'), a.snub_nosed_note ? esc(a.snub_nosed_note) : check())}
    ${cell(L('source'), src + guide + '<br>' + when, 'src')}</tr>`; }).join('');
}
function paintStatic(){
  $('#comparator-heading').textContent = t(militaryOn ? 'mil.title' : 'compare.h1');
  $('#ukrule').textContent = t('compare.uk_rule');
  $('#gen').textContent = DATA.meta.generated;
  const sel = $('#fRegion'), cur = sel.value;
  sel.innerHTML = `<option value="">${esc(t('compare.f.allregions'))}</option>` + REGIONS.map(r => `<option value="${esc(r)}">${esc(t('compare.r.' + r))}</option>`).join('');
  sel.value = cur;
  render(); }
document.querySelectorAll('.filters input:not(#fMilitary),.filters select,#fQ').forEach(e => e.addEventListener('input', render));
document.querySelectorAll('th[data-k]').forEach(th => th.addEventListener('click', () => { $('#fSort').value = th.dataset.k; render(); }));
function toast(x){ const e = $('#toast'); e.textContent = x; e.style.display = 'block'; setTimeout(() => e.style.display = 'none', 2200); }
function summary(){
  const r = rowsFiltered().slice(0, 10), tags = [$('#fDog').checked && 'dog', $('#fCat').checked && 'cat', $('#fNoLimit').checked && 'no published weight limit', $('#fRegion').value].filter(Boolean).join(', ');
  return `✈️🐾 Flying with a pet${tags ? ' (' + tags + ')' : ''}: ${r.length} airlines, cheapest first\n` +
    r.map((a, i) => `${i + 1}. ${a.name}: ${a.cabin_fee_usd_or_local ? a.cabin_fee_usd_or_local.split(/[;(]/)[0].trim() : (cabinOK(a) ? 'check with airline' : 'no cabin pets')}`).join('\n') +
    `\n⚠️ UK: no cabin pets on arrival, cargo only.\nFull sourced table: https://petpolicycheck.com/airlines/compare/?utm_source=share`; }
$('#copy').onclick = async () => { const x = summary(); try { await navigator.clipboard.writeText(x); toast(t('compare.copied')); } catch(e){ prompt('Copy:', x); } };
$('#card').onclick = () => { const c = $('#cv'), x = c.getContext('2d'), r = rowsFiltered().filter(a => a.fee_usd_short || a.fee_usd_long).slice(0, 10);
  const tint = getComputedStyle(document.documentElement).getPropertyValue('--dept-plane').trim() || '#d9b765';
  x.fillStyle = '#fff'; x.fillRect(0, 0, 1080, 1350); x.fillStyle = tint; x.fillRect(0, 0, 1080, 230);
  x.fillStyle = '#fff'; x.font = 'bold 64px system-ui'; x.fillText('Pet in cabin: who charges what', 60, 120); x.font = '34px system-ui'; x.fillText('One way, per carrier · official airline pages · ' + DATA.meta.generated.slice(0, 10), 60, 185);
  x.fillStyle = '#14213d'; r.forEach((a, i) => { const y = 320 + i * 92; x.font = 'bold 40px system-ui'; x.fillText(a.name.replace(/ \(.*\)/, ''), 60, y);
    x.font = 'bold 44px system-ui'; const v = a.fee_usd_short ?? a.fee_usd_long; x.textAlign = 'right'; x.fillText('$' + v, 1020, y); x.textAlign = 'left';
    x.fillStyle = '#e6eaf2'; x.fillRect(60, y + 24, 960, 2); x.fillStyle = '#14213d'; });
  x.fillStyle = tint; x.font = 'bold 38px system-ui'; x.fillText('petpolicycheck.com/airlines/compare/', 60, 1300);
  const l = document.createElement('a'); l.download = 'ppc-pet-fee-card.png'; l.href = c.toDataURL('image/png'); l.click(); };
window.addEventListener('ppc:lang', paintStatic);
paintStatic();
setMilitary(militaryOn, false);
$('#fMilitary').addEventListener('change', () => setMilitary($('#fMilitary').checked,true));
window.addEventListener('popstate',()=>setMilitary(new URLSearchParams(location.search).get('military')==='1',false));
fetch('/assets/data/military-airlines.json?v=20261107mil1').then(r=>{if(!r.ok)throw new Error('Military policy data unavailable');return r.json();}).then(d=>{militaryData=d;if(militaryOn)render();}).catch(()=>{militaryFailed=true;if(militaryOn)render();});
