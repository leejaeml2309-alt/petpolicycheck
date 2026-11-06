/* PetPolicyCheck airline comparator UI — sourced from innov #6 */
const DATA = window.PPC_COMPARATOR;
const A = DATA.airlines, $ = s => document.querySelector(s);
$('#ukrule').textContent = DATA.meta.uk_global_rule; $('#gen').textContent = DATA.meta.generated;
[...new Set(A.map(a => a.region))].sort().forEach(r => $('#fRegion').insertAdjacentHTML('beforeend', `<option>${r}</option>`));
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function parseDims(str){ // "18 x 14 x 9 in (..)" → {L,W,H,unit}
  const m = String(str).match(/(\d+(?:\.\d+)?)\s*(?:L\s*)?x\s*(\d+(?:\.\d+)?)\s*(?:W\s*|H\s*)?x\s*(\d+(?:\.\d+)?)\s*(?:H\s*|W\s*)?(cm|in)/i);
  return m ? {L:+m[1], W:+m[2], H:+m[3], unit:m[4].toLowerCase()} : null; }
function fits(a){
  const L = +$('#cL').value, W = +$('#cW').value, H = +$('#cH').value; if(!(L && W && H)) return null;
  const k = $('#cU').value === 'cm' ? 1 : 2.54, mine = [L*k, W*k, H*k];
  const opts = (a.underseat_soft_dims_in_cm || []).map(parseDims).filter(Boolean);
  if(!opts.length) return a.cabin_dogs || a.cabin_cats ? 'unknown' : null;
  // best-case aircraft/label; soft carriers usually compress ~1 in on height, we do NOT assume it.
  return opts.some(o => { const f = o.unit === 'cm' ? 1 : 2.54; return mine[0] <= o.L*f && mine[1] <= o.W*f && mine[2] <= o.H*f; }) ? 'ok' : 'ko'; }
function feeTxt(a){ return a.cabin_fee_usd_or_local ? esc(a.cabin_fee_usd_or_local) : '<span class="n">No cabin pets</span>'; }
function rowsFiltered(){
  let r = A.filter(a => (!$('#fDog').checked || a.cabin_dogs) && (!$('#fCat').checked || a.cabin_cats)
    && (!$('#fCabin').checked || a.cabin_dogs || a.cabin_cats)
    && (!$('#fNoLimit').checked || ['none_stated','explicit_no_limit'].includes(a.weight_limit_type))
    && (!$('#fCargo').checked || a.cargo_or_checked_allowed === true)
    && (!$('#fRegion').value || a.region === $('#fRegion').value));
  const s = $('#fSort').value, key = s === 'long' ? 'fee_usd_long' : 'fee_usd_short';
  r.sort((x, y) => s === 'name' ? x.name.localeCompare(y.name) : ((x[key] ?? 1e9) - (y[key] ?? 1e9)) || x.name.localeCompare(y.name));
  return r; }
function render(){
  const r = rowsFiltered();
  $('#count').textContent = `${r.length} of ${A.length} airlines match`;
  $('#tb').innerHTML = r.map(a => { const f = fits(a); const rev = /needs_review|needs_recheck|secondary/.test(a.verification_level);
    return `<tr data-dept="plane">
    <td class="name"><b>${esc(a.name)}</b><small>${esc(a.iata)} · ${esc(a.region)}</small>${rev ? '<br><span class="pill rev">needs review</span>' : ''}</td>
    <td>${a.cabin_dogs ? '<span class="y">Dogs ✓</span>' : '<span class="n">Dogs ✗</span>'}<br>${a.cabin_cats ? '<span class="y">Cats ✓</span>' : '<span class="n">Cats ✗</span>'}</td>
    <td>${feeTxt(a)}</td>
    <td>${esc(a.max_weight_cabin_lb_kg)}${['none_stated','explicit_no_limit'].includes(a.weight_limit_type) ? '<br><span class="pill nolimit">no published limit</span>' : ''}</td>
    <td>${(a.underseat_soft_dims_in_cm || ['Not published / n.a.']).map(esc).join('<br>')}${f ? `<br><span class="fit ${f === 'ok' ? 'ok' : 'ko'}">${f === 'ok' ? 'Your carrier fits ✓' : f === 'ko' ? 'Too big ✗' : 'Size not published ?'}</span>` : ''}</td>
    <td class="hide-m">${esc(a.cargo_fee_note)}</td><td class="hide-m">${esc(a.snub_nosed_note || '—')}</td>
    <td><a href="${esc(a.official_policy_url)}" rel="noopener" target="_blank">Official</a>${a.ppc_guide_url ? ` · <a href="${esc(a.ppc_guide_url)}">PPC guide</a>` : ''}<br><small>${esc(a.last_verified)}</small></td></tr>`; }).join('');
}
document.querySelectorAll('.filters input,.filters select').forEach(e => e.addEventListener('input', render));
document.querySelectorAll('th[data-k]').forEach(th => th.addEventListener('click', () => { $('#fSort').value = th.dataset.k; render(); }));
function toast(t){ const e = $('#toast'); e.textContent = t; e.style.display = 'block'; setTimeout(() => e.style.display = 'none', 2200); }
function summary(){
  const r = rowsFiltered().slice(0, 10), tags = [$('#fDog').checked && 'dog', $('#fCat').checked && 'cat', $('#fNoLimit').checked && 'no published weight limit', $('#fRegion').value].filter(Boolean).join(', ');
  return `✈️🐾 Flying with a pet${tags ? ' (' + tags + ')' : ''}: ${r.length} airlines, cheapest first\n` +
    r.map((a, i) => `${i + 1}. ${a.name}: ${a.cabin_fee_usd_or_local ? a.cabin_fee_usd_or_local.split(/[;(]/)[0].trim() : 'no cabin pets'}`).join('\n') +
    `\n⚠️ UK: no cabin pets on arrival, cargo only.\nFull sourced table: https://petpolicycheck.com/airlines/compare/?utm_source=share`; }
$('#copy').onclick = async () => { const t = summary(); try { await navigator.clipboard.writeText(t); toast('Summary copied'); } catch(e){ prompt('Copy:', t); } };
$('#card').onclick = () => { const c = $('#cv'), x = c.getContext('2d'), r = rowsFiltered().filter(a => a.fee_usd_short || a.fee_usd_long).slice(0, 10);
  const tint = getComputedStyle(document.documentElement).getPropertyValue('--dept-plane').trim();
  x.fillStyle = '#fff'; x.fillRect(0, 0, 1080, 1350); x.fillStyle = tint; x.fillRect(0, 0, 1080, 230);
  x.fillStyle = '#fff'; x.font = 'bold 64px system-ui'; x.fillText('Pet in cabin: who charges what', 60, 120); x.font = '34px system-ui'; x.fillText('One way, per carrier · official airline pages · ' + DATA.meta.generated.slice(0, 10), 60, 185);
  x.fillStyle = '#14213d'; r.forEach((a, i) => { const y = 320 + i * 92; x.font = 'bold 40px system-ui'; x.fillText(a.name.replace(/ \(.*\)/, ''), 60, y);
    x.font = 'bold 44px system-ui'; const v = a.fee_usd_short ?? a.fee_usd_long; x.textAlign = 'right'; x.fillText('$' + v, 1020, y); x.textAlign = 'left';
    x.fillStyle = '#e6eaf2'; x.fillRect(60, y + 24, 960, 2); x.fillStyle = '#14213d'; });
  x.fillStyle = tint; x.font = 'bold 38px system-ui'; x.fillText('petpolicycheck.com/airlines/compare/', 60, 1300);
  const l = document.createElement('a'); l.download = 'ppc-pet-fee-card.png'; l.href = c.toDataURL('image/png'); l.click(); };
render();


/* Military & Service Dog filter (Step C V3) */
(function(){
  function bootMil(){
    var filters=document.querySelector('.filters');
    if(!filters || document.getElementById('fMilitary')) return;
    var lab=document.createElement('label');
    lab.innerHTML='<input type="checkbox" id="fMilitary"> <span data-i18n="compare.military">Military & Service Dog</span>';
    filters.insertBefore(lab, filters.firstChild);
    var note=document.createElement('div');
    note.id='milNote'; note.className='gcard'; note.style.cssText='display:none;margin:10px 0;padding:10px 12px;border:1px solid rgba(212,175,55,.35);border-radius:10px;background:linear-gradient(165deg,rgba(0,31,63,.92),rgba(3,40,79,.88));color:#f4f6fa';
    note.innerHTML='<b>Military / Service Dog view</b>: Highlights carriers often used on PCS orders (Delta, United, American, Alaska). DOT service dogs: $0 cabin under 14 CFR Part 382. Canada CTA may require ADI/IGDF school certification. AMC Space-A: leisure pets generally barred — service dogs / Patriot Express PCS slots differ. JTR pet reimbursement overview: up to $550 CONUS / $2,000 OCONUS (confirm on dfas.mil / defense.gov). See <a href="../../veterans/">Veterans hub</a> · <a href="../../military-pcs/">PCS kit</a>.';
    filters.parentNode.insertBefore(note, filters.nextSibling);
    var milSlugs={delta:1,united:1,american:1,alaska:1,'air-canada':1};
    function apply(){
      var on=document.getElementById('fMilitary').checked;
      note.style.display=on?'block':'none';
      document.querySelectorAll('#tb tr').forEach(function(tr){
        var slug=(tr.getAttribute('data-slug')||tr.id||'').toLowerCase();
        if(!slug){ var a=tr.querySelector('a'); slug=(a&&a.href||'').toLowerCase(); }
        var hit=Object.keys(milSlugs).some(function(k){return slug.indexOf(k)>=0 || (tr.textContent||'').toLowerCase().indexOf(k.replace('-',' '))>=0});
        if(on && !hit) tr.style.opacity='0.35'; else tr.style.opacity='';
      });
    }
    document.getElementById('fMilitary').addEventListener('change', apply);
    if(new URLSearchParams(location.search).get('military')==='1'){ document.getElementById('fMilitary').checked=true; apply(); }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', bootMil); else bootMil();
})();
