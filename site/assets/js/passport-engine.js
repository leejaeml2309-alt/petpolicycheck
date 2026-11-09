function ppcPassES(){try{var d=document.documentElement;if((d.getAttribute('data-ppc-locale')||'')==='es')return true;if((location.pathname||'').indexOf('/es/')===0)return true;if((d.lang||'').toLowerCase().indexOf('es')===0)return true;}catch(e){}return false;}
/* PetPolicyCheck · Unified Route Engine v1 (#1 Pet Travel Passport)
 * Pure function: computePassport(input, DATA) -> {legs, timeline, traps, airline, url}
 * input = {from:'US', to:'MX', state:'FL'|null, airline:'delta'|null, pet:'dog'|'cat', ret:true|false, date:'YYYY-MM-DD'|null, retDate:...}
 * No network, no storage: works on GitHub Pages and file://. */
(function (g) {
  const OFF = { 'D-180': 180, 'D-30': 30, 'D-21': 21, 'D-10': 10, 'D-5': 5, 'Airport Day': 0 };
  const iso = d => d.toISOString().slice(0, 10);
  function minus(dateStr, n) { if (!dateStr) return null; const d = new Date(dateStr + 'T12:00:00Z'); d.setUTCDate(d.getUTCDate() - n); return iso(d); }
  function match(rule, leg, inp, F) {
    const a = rule.applies || {};
    if (a.always) return true;
    if (leg.from === leg.to) return !!(a.us_state && inp.state && leg.to === 'US');   // domestic trip: state rules only
    if (a.international) return leg.n === 1;                                          // generic prep once

    if (a.dest && !a.dest.includes(leg.to)) return false;
    if (a.origin && !a.origin.includes(leg.from)) return false;
    if (a.species && !a.species.includes(inp.pet)) return false;
    if (a.visited_high_risk && !(F.countries[leg.from] && F.countries[leg.from].cdc_risk === 'HIGH')) return false;
    if (a.from_nws && !(F.nws_affected || []).includes(leg.from)) return false;
    if (a.us_state && !(inp.state && leg.to === 'US')) return false;
    return !!(a.dest || a.us_state);
  }
  function computePassport(inp, DATA) {
    const F = DATA.frame, legs = [{ n: 1, from: inp.from, to: inp.to, date: inp.date || null }];
    if (inp.ret && inp.from !== inp.to) legs.push({ n: 2, from: inp.to, to: inp.from, date: inp.retDate || null });
    const timeline = [];
    legs.forEach(leg => F.rules.forEach(r => {
      if (!match(r, leg, inp, F)) return;
      if (leg.n === 2 && r.applies.always) return;               // generic steps once
      // US high-risk certificate must be done BEFORE the outbound leg leaves the US
      const anchorLeg = (r.id === 'us_hr_cert' && leg.n === 2) ? legs[0] : leg;
      const st = (F.us_states || []).find(s => s.code === inp.state);
      let text = r.text.replace('{state}', st ? st.name : 'your state');
      if (r.id === 'us_state' && st) text += ppcPassES()
        ? ` → ${st.name}: CVI (certificado de inspección veterinaria) ${st.cvi}; rabia ${st.rabies}.${st.verified ? '' : ' (página estatal no verificada: llame al veterinario estatal)'}`
        : ` → ${st.name}: CVI ${st.cvi}; rabies ${st.rabies}.${st.verified ? '' : ' (state page not verified: call the state vet)'}`;
      timeline.push({ leg: anchorLeg.n, legLabel: `${anchorLeg.from} → ${anchorLeg.to}` + (anchorLeg !== leg ? (ppcPassES()?' (necesario para el regreso)':' (needed for the return)') : ''),
        when: r.when, date: minus(anchorLeg.date, OFF[r.when]), text, source: r.source, id: r.id });
    }));
    timeline.sort((a, b) => a.leg - b.leg || OFF[b.when] - OFF[a.when]);
    // traps
    const inRoute = c => legs.some(l => l.from === c || l.to === c), toUS = legs.some(l => l.to === 'US' && l.from !== 'US');
    const T = F.traps, traps = [], add = id => { const t = T.find(x => x.id === id); if (t && !traps.includes(t)) traps.push(t); };
    if (legs.some(l => l.to === 'GB')) add('gb_no_cabin');
    if (inRoute('MX') && inp.pet === 'dog' && toUS) add('mx_return_nws');
    if (inRoute('CA') && toUS && inp.pet === 'dog') add('ca_return_cdc');
    if (inRoute('DO') && inp.pet === 'dog') add('do_high_risk');
    if (['turkish', 'qatar'].includes(inp.airline) && inRoute('US') && inp.pet === 'dog') add('hr_transit');
    if (toUS && inp.pet === 'dog') add('us_age');
    if (inp.state === 'HI') add('hi_quarantine');
    // airline check
    let airline = null;
    if (inp.airline) {
      const a = DATA.airlines.find(x => x.id === inp.airline);
      if (a) {
        const cabinOK = inp.pet === 'dog' ? a.cabin_dogs : a.cabin_cats, warn = [];
        if (!cabinOK) warn.push(`${a.name} does not take ${inp.pet}s in the cabin. ${a.cargo_fee_note || ''}`);
        const names = legs.flatMap(l => [F.countries[l.to] && F.countries[l.to].name, F.countries[l.from] && F.countries[l.from].name]).filter(Boolean);
        const br = (a.banned_routes || '').split(a.name.replace(/ \(.*\)/, '')).join('');
        names.forEach(nm => { const short = nm.replace(/ \(.*\)/, ''); if (short !== 'United States' && br.toLowerCase().includes(short.toLowerCase())) warn.push(`Route restriction on ${a.name}: "${a.banned_routes}"`); });
        if (/needs_review|secondary|recheck/.test(a.verification_level)) warn.push((ppcPassES()?'Al menos una cifra de esta aerolínea proviene de una fuente secundaria: confírmela con la aerolínea antes de pagar.':'At least one number for this airline comes from a secondary source: confirm with the airline before paying.'));
        airline = Object.assign({ cabinOK, warn: [...new Set(warn)] }, a);
        if (cabinOK) timeline.push({ leg: 1, legLabel: `${legs[0].from} → ${legs[0].to}`, when: 'D-30', date: minus(legs[0].date, 30), id: 'airline_specific',
          text: `${a.name}: cabin fee ${a.cabin_fee_usd_or_local || 'n/a'} · weight ${a.max_weight_cabin_lb_kg} · carrier ${(a.underseat_soft_dims_in_cm || ['not published']).join(' / ')}`, source: a.official_policy_url });
        timeline.sort((x, y) => x.leg - y.leg || OFF[y.when] - OFF[x.when]);
      }
    }
    const q = new URLSearchParams({ from: inp.from, to: inp.to, pet: inp.pet }); if (inp.state) q.set('state', inp.state); if (inp.airline) q.set('airline', inp.airline); if (inp.ret) q.set('return', '1'); if (inp.date) q.set('date', inp.date); if (inp.retDate) q.set('retdate', inp.retDate);
    const url = `https://petpolicycheck.com/passport/?${q.toString()}`;
    // Marc 2026-11-06: post-arrival tip slot (#2 Track 3 vets + Track 4 groomers feed it)
    const postArrival = { title: 'Post-Arrival Grooming & Vet Check', city_hint: (F.countries[inp.to] || {}).hubs ? F.countries[inp.to].hubs[0][1] : null,
      text: 'Within 24-72 h of landing: a quick vet check (stress, hydration, ears/paws after the carrier) and, if needed, a one-off post-flight bath at a PPC Verified Groomer (no membership, accepts your international rabies certificate). ' +
        (inRoute('MX') && inp.pet === 'dog' ? 'Mexico: ask the vet to check for screwworm wounds; you will need an official NWS certificate within 5 days of flying back.' : ''),
      slots: ['verified_vet', 'verified_groomer'] };
    return { legs, timeline, traps, airline, url, postArrival, qrUrl: url + '&utm_source=passport_qr&utm_medium=print' };
  }
  g.PPCPassport = { computePassport, buckets: Object.keys(OFF) };
  if (typeof module !== 'undefined') module.exports = g.PPCPassport;
})(typeof window !== 'undefined' ? window : globalThis);
