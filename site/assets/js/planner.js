/* PetPolicyCheck · Pet Travel Planner (wizard + printable plan).
   Data: /assets/data/planner/{airlines,countries}.json (see DATA.md). Crate logic: /assets/js/crate-core.js.
   Nothing is sent to a server; state lives in the URL hash and localStorage. */
(function () {
  'use strict';
  var root = document.getElementById('planner-app');
  if (!root) return;
  var htmlLang = document.documentElement.getAttribute('data-ppc-locale');
  var LANG = htmlLang || ((location.pathname.match(/^\/(it|es)\//) || [])[1]) || 'en';
  var I = window.PPC_PLANNER_I18N || {};
  var S = I[LANG] || I.en;
  var CN = (window.PPC_PLANNER_COUNTRY_NAMES || {})[LANG] || (window.PPC_PLANNER_COUNTRY_NAMES || {}).en || {};
  var C = window.PPCCrate;
  var BASE = '/assets/data/planner/';
  var STORE = 'ppc_planner_v1';
  var LOCAL_TREE = LANG === 'en' ? '' : '/' + LANG;
  /* Airline pages that exist only in English (no /it/ or /es/ version yet). */
  var EN_ONLY_AIRLINES = ['air-transat', 'avelo', 'breeze', 'finnair', 'iberia', 'ita-airways', 'sas', 'sun-country'];
  var REQ_ORDER = ['microchip', 'rabies_vaccine', 'titer_test', 'waiting_period', 'tapeworm_treatment', 'health_certificate', 'endorsement', 'import_permit', 'quarantine'];
  var SPECIES = ['dog', 'cat', 'ferret', 'bird', 'rabbit', 'other'];
  var SPECIES_KEY = { dog: 'dogs', cat: 'cats', ferret: 'ferrets', bird: 'birds', rabbit: 'rabbits' };

  var A = [], K = [], byA = {}, byK = {};
  var st = defaults();

  function defaults() {
    return { step: 1, sp: 'dog', snub: 0, breed: '', wu: 'kg', pw: '', cw: '', lu: 'cm', l: '', w: '', h: '', o: '', d: '', a: '', dt: '' };
  }
  function fmtS(str, o) { return String(str).replace(/\{(\w+)\}/g, function (m, k) { return o[k] != null ? o[k] : m; }); }
  function esc(v) { return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function nullA() { return '<span class="pl-null" role="note"><span aria-hidden="true">◌</span> ' + esc(S.nullAirline) + '</span>'; }
  function nullC() { return '<span class="pl-null" role="note"><span aria-hidden="true">◌</span> ' + esc(S.nullCountry) + '</span>'; }
  function txtA(v) { return v ? '<span class="pl-quote-in" lang="en">' + fullAndExcerpt(v, 240) + '</span>' : nullA(); }
  function n2(v) { var x = C.num(v); return x === null ? null : Math.round(x * 1000) / 1000; }
  function $(id) { return document.getElementById(id); }

  /* ---------- dates ---------- */
  function parseDate(s) { if (!/^\d{4}-\d{2}-\d{2}$/.test(s || '')) return null; var d = new Date(s + 'T12:00:00'); return isNaN(d) || iso(d) !== s ? null : d; }
  function iso(d) { var m = d.getMonth() + 1, dd = d.getDate(); return d.getFullYear() + '-' + (m < 10 ? '0' : '') + m + '-' + (dd < 10 ? '0' : '') + dd; }
  var DF = (function () { try { return new Intl.DateTimeFormat(LANG === 'en' ? 'en-GB' : LANG, { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }); } catch (e) { return null; } })();
  var DFs = (function () { try { return new Intl.DateTimeFormat(LANG === 'en' ? 'en-GB' : LANG, { day: 'numeric', month: 'long', year: 'numeric' }); } catch (e) { return null; } })();
  function fd(d) { return DF ? DF.format(d) : iso(d); }
  function fds(d) { return DFs ? DFs.format(d) : iso(d); }
  function minus(d, v, unit) {
    var x = new Date(d.getTime());
    if (unit === 'days') x.setDate(x.getDate() - v);
    else if (unit === 'weeks') x.setDate(x.getDate() - 7 * v);
    else if (unit === 'months') { var day = x.getDate(); x.setDate(1); x.setMonth(x.getMonth() - v); var last = new Date(x.getFullYear(), x.getMonth() + 1, 0).getDate(); x.setDate(Math.min(day, last)); }
    else if (unit === 'years') x.setFullYear(x.getFullYear() - v);
    else if (unit === 'hours') x = new Date(x.getTime() - v * 3600000);
    else return null;
    return x;
  }
  function today() { var t = new Date(); t.setHours(12, 0, 0, 0); return t; }

  /* ---------- state ---------- */
  function encode() {
    var p = new URLSearchParams();
    Object.keys(st).forEach(function (k) { var v = st[k]; if (v !== '' && v !== null && v !== undefined && !(k === 'snub' && !v)) p.set(k, v); });
    return p.toString();
  }
  function decode(str) {
    var o = defaults(), p = new URLSearchParams(str || '');
    Object.keys(o).forEach(function (k) { if (p.has(k)) o[k] = p.get(k); });
    o.step = Math.min(3, Math.max(1, parseInt(o.step, 10) || 1));
    o.snub = o.snub === '1' || o.snub === 1 ? 1 : 0;
    if (SPECIES.indexOf(o.sp) < 0) o.sp = 'dog';
    if (C.WEIGHT_UNITS.indexOf(o.wu) < 0) o.wu = 'kg';
    if (C.LENGTH_UNITS.indexOf(o.lu) < 0) o.lu = 'cm';
    return o;
  }
  function save() {
    var enc = encode();
    try { localStorage.setItem(STORE, enc); } catch (e) {}
    try { history.replaceState(null, '', location.pathname + location.search + '#' + enc); } catch (e) {}
  }
  function shareUrl() { return location.origin + location.pathname + '#' + encode(); }

  /* ---------- markup helpers ---------- */
  function opt(v, label, sel) { return '<option value="' + esc(v) + '"' + (sel ? ' selected' : '') + '>' + esc(label) + '</option>'; }
  function radio(name, v, label, cur, extra) {
    var id = 'pl-' + name + '-' + v;
    return '<label class="pl-chip' + (extra || '') + '" for="' + id + '"><input type="radio" name="' + name + '" id="' + id + '" value="' + esc(v) + '"' + (String(cur) === String(v) ? ' checked' : '') + '><span>' + esc(label) + '</span></label>';
  }
  function numField(id, key, label, unitLabel) {
    return '<div class="pl-field"><label for="' + id + '">' + esc(label) + ' <span class="pl-unit">(' + esc(unitLabel) + ')</span></label>' +
      '<input id="' + id + '" data-k="' + key + '" type="number" inputmode="decimal" min="0" step="any" value="' + esc(st[key]) + '" aria-describedby="' + id + '-err"><p class="pl-err" id="' + id + '-err" aria-live="polite"></p></div>';
  }
  function excerpt(s, cap) {
    if (!s || s.length <= cap) return esc(s || '');
    var cut = s.lastIndexOf(' ', cap);
    return esc(s.slice(0, cut > cap * .6 ? cut : cap)) + '…';
  }
  function fullAndExcerpt(s, cap) {
    if (!s || s.length <= cap) return esc(s || '');
    return '<span class="pl-full">' + esc(s) + '</span><span class="pl-excerpt"><b lang="' + LANG + '">' + esc(S.excerpt) + '</b> ' + excerpt(s, cap) + '</span>';
  }
  function quoteAround(q, needle, cap) { /* print excerpt keeps the stated timing in view */
    if (!q || q.length <= cap) return esc(q || '');
    var i = needle ? q.indexOf(needle) : -1;
    if (i < 0 || i + needle.length < cap * .8) return fullAndExcerpt(q, cap);
    var a = Math.max(0, i - Math.round(cap * .45)), b = Math.min(q.length, a + cap);
    var sa = q.indexOf(' ', a); if (a > 0 && sa > -1 && sa < i) a = sa + 1;
    var sb = q.lastIndexOf(' ', b); if (b < q.length && sb > i + needle.length) b = sb;
    var ex = (a > 0 ? '…' : '') + esc(q.slice(a, b)) + (b < q.length ? '…' : '');
    return '<span class="pl-full">' + esc(q) + '</span><span class="pl-excerpt"><b lang="' + LANG + '">' + esc(S.excerpt) + '</b> ' + ex + '</span>';
  }
  function countryName(id) { return CN[id] || (byK[id] && byK[id].name) || id; }

  function rail() {
    var h = '<nav class="pl-rail" aria-label="' + esc(S.stepOf.replace('{n}', st.step)) + '"><ol>';
    S.steps.forEach(function (lab, i) {
      var n = i + 1, cls = n === st.step ? 'is-current' : (n < st.step ? 'is-done' : '');
      h += '<li class="' + cls + '"><button type="button" class="pl-rail-btn" data-go="' + n + '"' + (n === st.step ? ' aria-current="step"' : '') + (n > st.step ? ' disabled' : '') + '>' +
        '<span class="pl-medal" aria-hidden="true">' + (n < st.step ? '<svg viewBox="0 0 20 20" width="18" height="18"><path d="M4 10.5l4 4 8-9" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>' : n) + '</span>' +
        '<span class="pl-rail-lab"><span class="pl-rail-n">' + esc(S.stepOf.replace('{n}', n)) + '</span>' + esc(lab) + '</span></button></li>';
    });
    return h + '</ol><svg class="pl-rail-vine" viewBox="0 0 600 24" preserveAspectRatio="none" aria-hidden="true"><path d="M0 12 C 60 2, 90 22, 150 12 S 240 2, 300 12 S 390 22, 450 12 S 540 2, 600 12" fill="none" stroke="currentColor" stroke-width="1.2"/></svg></nav>';
  }

  function step1() {
    var h = '<section class="pl-panel" aria-labelledby="pl-h1"><span class="pl-corner tl" aria-hidden="true"></span><span class="pl-corner tr" aria-hidden="true"></span><span class="pl-corner bl" aria-hidden="true"></span><span class="pl-corner br" aria-hidden="true"></span>' +
      '<h2 id="pl-h1" tabindex="-1">' + esc(S.petH) + '</h2><p class="pl-sub">' + esc(S.petSub) + '</p>' +
      '<fieldset class="pl-fs"><legend>' + esc(S.species) + '</legend><div class="pl-chips pl-chips--species">';
    SPECIES.forEach(function (s) { h += radio('sp', s, S[s], st.sp, ' pl-chip--tile'); });
    h += '</div></fieldset>' +
      '<div class="pl-grid2"><div class="pl-field pl-check"><input type="checkbox" id="pl-snub" data-k="snub"' + (st.snub ? ' checked' : '') + ' aria-describedby="pl-snub-hint"><label for="pl-snub">' + esc(S.snub) + '</label><p class="pl-hint" id="pl-snub-hint">' + esc(S.snubHint) + '</p></div>' +
      '<div class="pl-field"><label for="pl-breed">' + esc(S.breed) + '</label><input id="pl-breed" data-k="breed" type="text" maxlength="60" autocomplete="off" value="' + esc(st.breed) + '" aria-describedby="pl-breed-hint"><p class="pl-hint" id="pl-breed-hint">' + esc(S.breedHint) + '</p></div></div>' +
      '<fieldset class="pl-fs"><legend>' + esc(S.weightUnit) + '</legend><div class="pl-chips">' + radio('wu', 'kg', S.kg, st.wu) + radio('wu', 'lb', S.lb, st.wu) + '</div></fieldset>' +
      '<div class="pl-grid2">' + numField('pl-pw', 'pw', S.petWeight, S[st.wu]) + numField('pl-cw', 'cw', S.carrierWeight, S[st.wu]) + '</div>' +
      '<fieldset class="pl-fs"><legend>' + esc(S.crateH) + '</legend><p class="pl-hint">' + esc(S.crateHint) + '</p>' +
      '<div class="pl-chips" role="group" aria-label="' + esc(S.lenUnit) + '">' + radio('lu', 'cm', S.cm, st.lu) + radio('lu', 'in', S['in'], st.lu) + '</div>' +
      '<div class="pl-grid3">' + numField('pl-l', 'l', S.len, S[st.lu]) + numField('pl-w', 'w', S.wid, S[st.lu]) + numField('pl-h', 'h', S.hei, S[st.lu]) + '</div></fieldset>' +
      '<div class="pl-actions"><button type="button" class="pl-btn" data-act="next">' + esc(S.next) + ' <span aria-hidden="true">→</span></button></div></section>';
    return h;
  }

  function step2() {
    var cs = K.slice().sort(function (x, y) { return countryName(x.id).localeCompare(countryName(y.id), LANG); });
    var as = A.slice().sort(function (x, y) { return x.name.localeCompare(y.name); });
    var h = '<section class="pl-panel" aria-labelledby="pl-h2"><span class="pl-corner tl" aria-hidden="true"></span><span class="pl-corner tr" aria-hidden="true"></span><span class="pl-corner bl" aria-hidden="true"></span><span class="pl-corner br" aria-hidden="true"></span>' +
      '<h2 id="pl-h2" tabindex="-1">' + esc(S.tripH) + '</h2><p class="pl-sub">' + esc(S.tripSub) + '</p><div class="pl-grid2">';
    h += '<div class="pl-field"><label for="pl-o">' + esc(S.origin) + '</label><select id="pl-o" data-k="o">' + opt('', S.choose, !st.o);
    cs.forEach(function (c) { h += opt(c.id, countryName(c.id), st.o === c.id); });
    h += opt('other', S.otherCountry, st.o === 'other') + '</select></div>';
    h += '<div class="pl-field"><label for="pl-d">' + esc(S.destination) + ' <span class="pl-reqmark" aria-hidden="true">*</span></label><select id="pl-d" data-k="d" required aria-describedby="pl-d-err">' + opt('', S.choose, !st.d);
    cs.forEach(function (c) { h += opt(c.id, countryName(c.id), st.d === c.id); });
    h += '</select><p class="pl-err" id="pl-d-err" aria-live="polite"></p></div>';
    h += '<div class="pl-field"><label for="pl-a">' + esc(S.airline) + ' <span class="pl-reqmark" aria-hidden="true">*</span></label><select id="pl-a" data-k="a" required aria-describedby="pl-a-err">' + opt('', S.choose, !st.a);
    as.forEach(function (a) { h += opt(a.id, a.name + (a.iata ? ' (' + a.iata + ')' : ''), st.a === a.id); });
    h += '</select><p class="pl-err" id="pl-a-err" aria-live="polite"></p></div>';
    h += '<div class="pl-field"><label for="pl-dt">' + esc(S.date) + ' <span class="pl-reqmark" aria-hidden="true">*</span></label><input id="pl-dt" data-k="dt" type="date" required value="' + esc(st.dt) + '" min="' + iso(today()) + '" aria-describedby="pl-dt-hint pl-dt-err"><p class="pl-hint" id="pl-dt-hint">' + esc(S.dateHint) + '</p><p class="pl-err" id="pl-dt-err" aria-live="polite"></p></div>';
    h += '</div><div class="pl-actions"><button type="button" class="pl-btn ghost" data-act="back"><span aria-hidden="true">←</span> ' + esc(S.back) + '</button><button type="button" class="pl-btn" data-act="build">' + esc(S.build) + ' <span aria-hidden="true">→</span></button></div></section>';
    return h;
  }

  /* ---------- results ---------- */
  function modeChip(v) {
    if (v === true) return '<span class="pl-st pl-st--yes"><span aria-hidden="true">✓</span> ' + esc(S.yes) + '</span>';
    if (v === false) return '<span class="pl-st pl-st--no"><span aria-hidden="true">✕</span> ' + esc(S.no) + '</span>';
    return '<span class="pl-st pl-st--na"><span aria-hidden="true">?</span> ' + esc(S.unknownMode) + '</span>';
  }
  function statusChip(kind, label) {
    var sym = { ok: '✓', bad: '✕', warn: '!', na: '?' }[kind] || '•';
    return '<span class="pl-st pl-st--' + kind + '"><span aria-hidden="true">' + sym + '</span> ' + esc(label) + '</span>';
  }
  function noCabinBlock(title, a) {
    return '<div class="pl-check-row"><h4>' + esc(title) + '</h4>' + statusChip('na', S.noCabin) + '<p class="pl-as"><span class="pl-as-k">' + esc(S.statedAs) + '</span> ' + txtA(a.cabin_as_stated) + '</p></div>';
  }
  /* Structured fee only when its figures and currency code(s) are all in the official wording; never converted. */
  function feeAmount(f) {
    var t = f.as_stated || '', cs = f.currency ? [f.currency] : (Array.isArray(f.currencies) ? f.currencies : []);
    var sym = typeof f.currency_symbol === 'string' && f.currency_symbol ? f.currency_symbol : '';
    var vals = typeof f.amount === 'number' ? [f.amount] : [f.amount_min, f.amount_max].filter(function (v) { return typeof v === 'number'; });
    if (!t || !vals.length || (!cs.length && !sym)) return null;
    if (sym && t.indexOf(sym) < 0) return null;
    var nums = (t.match(/\d[\d,]*(?:\.\d+)?/g) || []).map(function (x) { return parseFloat(x.replace(/,/g, '')); });
    if (!vals.every(function (v) { return nums.indexOf(v) >= 0; })) return null;
    var cas = f.currency_as_stated || '';
    if (cs.length && !cs.every(function (c) { return t.indexOf(c) >= 0 || cas.indexOf(c) >= 0 || (cas.indexOf('/') >= 0 && cas.split('/').indexOf(c.slice(0, 2)) >= 0); })) return null;
    var amt = typeof f.amount === 'number' ? String(f.amount) : (vals.length === 2 ? f.amount_min + '–' + f.amount_max : String(vals[0]));
    if (!cs.length) return sym + (vals.length === 2 ? f.amount_min + '–' + sym + f.amount_max : amt); /* bare symbol as published, no currency guessed */
    return cs.join('/') + ' ' + amt;
  }
  function sameFeeText(t, fa, scope) {
    var n = function (x) { return String(x).replace(/[\s$]/g, '').replace(/[–—]/g, '-').toLowerCase(); };
    var tt = n(t); if (scope && tt.indexOf(n(scope)) === 0) tt = tt.slice(n(scope).length).replace(/^[:,]/, '');
    return tt === n(fa);
  }
  function weightVerdict(r) {
    var o = { p: n2(r.pet), t: n2(r.total), l: r.limit, u: S[r.unit] }, chip, det = '';
    if (r.status === 'within') { chip = statusChip('ok', S.wWithin); det = fmtS(r.compared === 'pet' ? S.wDetailPet : S.wDetailTotal, o); }
    else if (r.status === 'over') { chip = statusChip('bad', S.wOver); det = fmtS(r.compared === 'total' ? S.wDetailTotal : S.wDetailPet, o); }
    else if (r.status === 'depends') { chip = statusChip('warn', S.wDepends); det = fmtS(r.compared === 'pet-only-entered' ? S.wDependsPet : (r.compared === 'unclear-no-carrier' ? S.wDependsNoCarrier : S.wDependsUnclear), o); }
    else if (r.status === 'other-unit') { chip = statusChip('na', fmtS(S.wOther, { u: S[r.otherUnit.unit] })); det = fmtS(S.wOtherDetail, { v: r.otherUnit.value, ou: S[r.otherUnit.unit] }); }
    else if (r.status === 'no-input') { chip = statusChip('na', S.wNoInput); }
    else { chip = statusChip('na', S.wUnknown); }
    return chip + (det ? '<p class="pl-det">' + esc(det) + '</p>' : '');
  }
  function notesAddText(notes, conds) { /* hide notes that only repeat the conditions' own wording */
    var rest = String(notes || '');
    conds.forEach(function (c) { [c.as_stated, c.condition].forEach(function (t) { if (t) rest = rest.split(t).join(' '); }); });
    return /[A-Za-z0-9]/.test(rest.replace(/\b(and|or|on|the|to|from|flights?|including|carrier)\b/gi, ''));
  }
  function incl(a) { var w = a.cabin_max_weight && a.cabin_max_weight.weight_includes; return w ? ' (' + esc(S.wIncludesShort) + ' <span lang="en">' + esc(w) + '</span>)' : ''; }
  function weightBlock(a) {
    if (a.cabin === false) return noCabinBlock(S.weightRow, a);
    var r = C.checkCabinWeight(a, { petWeight: st.pw, carrierWeight: st.cw, unit: st.wu });
    var h = '<div class="pl-check-row"><h4>' + esc(S.weightRow) + '</h4>';
    if (r.status === 'conditional') {
      var conds = (a.cabin_max_weight && a.cabin_max_weight.conditions) || [];
      h += statusChip('warn', S.wConditional) + '<ul class="pl-conds">' + r.conditions.map(function (c, i) {
        var src = conds[i] || {}, lim = [];
        if (typeof src.kg === 'number') lim.push(src.kg + ' ' + S.kg);
        if (typeof src.lb === 'number') lim.push(src.lb + ' ' + S.lb);
        var hasNamed = r.conditions.some(function (x) { return !!x.condition; });
        return '<li><p class="pl-cond-k"><span lang="en">' + esc(c.condition || '') + '</span>' + (c.condition ? '' : esc(hasNamed ? S.condGeneral : S.condNone)) +
          '</p>' + (lim.length ? '<p class="pl-cond-lim"><span class="pl-as-k">' + esc(S.condLimit) + '</span> ' + esc(lim.join(' / ')) + incl(a) + '</p>' : '') +
          weightVerdict(c) + '<p class="pl-as"><span class="pl-as-k">' + esc(S.statedAs) + '</span> ' + txtA(c.asStated) + '</p></li>';
      }).join('') + '</ul>';
      h += '<p class="pl-as"><span class="pl-as-k">' + esc(S.statedAs) + '</span> ' + txtA(r.asStated) + '</p>';
      if (r.notes && notesAddText(r.notes, conds)) h += '<p class="pl-as"><span class="pl-as-k">' + esc(S.notes) + '</span> ' + txtA(r.notes) + '</p>';
    } else {
      h += weightVerdict(r) + '<p class="pl-as"><span class="pl-as-k">' + esc(S.statedAs) + '</span> ' + (r.asStated ? esc(r.asStated) : nullA()) + '</p>';
      if (a.cabin_max_weight && a.cabin_max_weight.weight_includes) h += '<p class="pl-as"><span class="pl-as-k">' + esc(S.wIncludes) + '</span> <span lang="en">' + esc(a.cabin_max_weight.weight_includes) + '</span></p>';
      if (r.notes) h += '<p class="pl-as"><span class="pl-as-k">' + esc(S.notes) + '</span> ' + txtA(r.notes) + '</p>';
    }
    if (r.scope) h += '<p class="pl-as"><span class="pl-as-k">' + esc(S.scope) + '</span> ' + esc(r.scope) + '</p>';
    return h + '</div>';
  }
  function dimBlock(a) {
    if (a.cabin === false) return noCabinBlock(S.dimRow, a);
    var r = C.checkDimensions(null, { l: st.l, w: st.w, h: st.h, unit: st.lu }, a.carrier_dimensions_as_stated);
    var chip = r.status === 'no-input' ? statusChip('na', S.dNoInput) : (r.status === 'unknown' ? statusChip('na', S.dUnknown) : statusChip('warn', S.dManual));
    var yours = r.entered ? n2(r.crate.l) + ' × ' + n2(r.crate.w) + ' × ' + n2(r.crate.h) + ' ' + S[r.crate.unit] + ' (' + S.len + ' × ' + S.wid + ' × ' + S.hei + ')' : '—';
    return '<div class="pl-check-row"><h4>' + esc(S.dimRow) + '</h4>' + chip +
      '<dl class="pl-dl"><dt>' + esc(S.dYours) + '</dt><dd>' + esc(yours) + '</dd><dt>' + esc(S.dStated) + '</dt><dd>' + txtA(a.carrier_dimensions_as_stated) + '</dd></dl>' +
      (r.entered && a.carrier_dimensions_as_stated ? '<p class="pl-hint">' + esc(S.dNote) + '</p>' : '') + '</div>';
  }
  function speciesBlock(a) {
    var r = C.checkSpecies(a, SPECIES_KEY[st.sp] || st.sp), lab = S[st.sp], chip;
    if (st.sp === 'other') chip = r.status === 'unknown' ? statusChip('na', S.speciesH) : '';
    else if (r.status === 'listed') chip = statusChip('ok', fmtS(S.speciesListed, { s: lab }));
    else if (r.status === 'not-listed') chip = statusChip('bad', fmtS(S.speciesNotListed, { s: lab }));
    else if (r.status === 'none') chip = statusChip('bad', S.speciesNone);
    else chip = statusChip('na', S.unknownMode);
    return '<div class="pl-check-row"><h4>' + esc(S.speciesH) + '</h4>' + chip + '<p class="pl-as"><span class="pl-as-k">' + esc(S.statedAs) + '</span> ' + txtA(a.species_as_stated) + '</p></div>';
  }

  /* Timing → countdown date only when the rule text places the figure before travel / arrival / boarding / export. */
  var AFTER_RE = /^\s*\)?\s*(?:\([^)]*\)\s*)?(?:or more\s+)?(?:before|prior to)\s+(?:the\s+)?(?:export|entry|arrival|arriving|boarding|travel|you arrive|departure|shipment|entering)/i;
  var WITHIN_AFTER_RE = /^\s*(?:of|before)\s+(?:the\s+pet[’']s\s+)?(?:travel|arrival|boarding|departure|entry)/i;
  var WAIT_BEFORE_RE = /(?:wait(?:ing period of)?(?: at least)?|only after)\s*$/i;
  var WAIT_AFTER_RE = /^\s*(?:or more\s+)?(?:after|from)\b/i;
  var AFTER_THEN_BEFORE_RE = /^\s*after\b[^.;|]{0,50}?\bbefore\s+(?:entry|travel|arrival|boarding)/i;
  function countable(t) {
    var ctx = t.context || '', i = ctx.indexOf(t.as_stated);
    if (i < 0) return false;
    var after = ctx.slice(i + t.as_stated.length, i + t.as_stated.length + 64), before = ctx.slice(Math.max(0, i - 28), i);
    if (AFTER_RE.test(after)) return true;                                   /* "10 days before boarding" */
    if (/within\s*$/i.test(before) && WITHIN_AFTER_RE.test(after)) return true; /* "within 30 days of travel" */
    if (WAIT_BEFORE_RE.test(before) && WAIT_AFTER_RE.test(after)) return true;  /* "wait 3 months from the sample date" */
    if (AFTER_THEN_BEFORE_RE.test(after)) return true;                        /* "21 days after the primary vaccination before entry" */
    return false;
  }
  function sentenceFor(req, t) {
    var ctx = t.context || '', i = ctx.indexOf(t.as_stated), src = req.as_stated || '';
    var core = ctx.slice(Math.max(0, i - 18), i + t.as_stated.length + 18);
    var j = src.indexOf(core);
    if (j < 0) { core = ctx.slice(Math.max(0, i), i + t.as_stated.length + 12); j = src.indexOf(core); }
    if (j < 0) return '…' + ctx.trim() + '…';
    var s = j, e = j + core.length;
    function cut(k) { /* sentence boundary at k (index of ". " or " | "), not after an initial like "E." */
      var c = src.charAt(k);
      if (c === '|') return true;
      if (c !== '.' || !/\s|$/.test(src.charAt(k + 1) || ' ')) return false;
      return !/(^|\s)[A-Z]$/.test(src.slice(Math.max(0, k - 2), k));
    }
    while (s > 0 && !(cut(s - 2) && /\s/.test(src.charAt(s - 1)))) s--;
    while (e < src.length && !cut(e)) e++;
    e = Math.min(src.length, e + 1);
    return src.slice(s, e).replace(/^\s*\|\s*/, '').replace(/\s*\|$/, '').trim();
  }
  /* Species-specific requirement view: keep entries for the plan's species (plus dogs_and_cats and unlabelled ones). */
  /* Show an entry when its species is the pet's, dogs_and_cats, or null (= all pets). */
  var ENTRY_SPECIES = { dog: 'dogs', cat: 'cats', ferret: 'ferrets', bird: 'birds', rabbit: 'rabbits' };
  function viewReq(r) {
    if (!r || !Array.isArray(r.entries) || !r.entries.length) return r || {};
    var want = ENTRY_SPECIES[st.sp] || null;
    var keep = r.entries.filter(function (e) { return e.species == null || e.species === 'dogs_and_cats' || (want !== null && e.species === want); });
    var v = {}; for (var k in r) v[k] = r[k];
    var ap = [];
    keep.forEach(function (e) { String(e.applies_to || '').split(/\s*;\s*/).forEach(function (x) { if (x && ap.indexOf(x) < 0) ap.push(x); }); });
    v.as_stated = keep.map(function (e) { return e.as_stated; }).filter(Boolean).join(' | ') || null;
    v.applies_to = ap.join('; ') || null;
    v.timings = [].concat.apply([], keep.map(function (e) { return e.timings || []; }));
    v._hidden = r.entries.length - keep.length;
    v._otherOnly = !keep.length;
    return v;
  }
  function healthBlock(k, travel) {
    var seen = {}, events = [];
    REQ_ORDER.forEach(function (key) {
      var r = k.requirements[key]; if (!r) return;
      r = viewReq(r);
      (r.timings || []).forEach(function (t) {
        var sig = t.value + t.unit + '|' + (t.context || '');
        if (seen[sig] || !countable(t)) return; seen[sig] = 1;
        var d = minus(travel, t.value, t.unit); if (!d) return;
        var dk = key + iso(d); if (seen[dk]) return; seen[dk] = 1;
        var q = sentenceFor(r, t);
        if (/\bonwards?\b|travel on to|then travel|in that country|those destinations/i.test(q + ' ' + (t.context || ''))) return; /* onward-travel rules are not entry steps */
        events.push({ key: key, t: t, d: d, quote: q, applies: r.applies_to });
      });
    });
    events.sort(function (x, y) { return x.d - y.d; });
    var now = today();
    var h = '<section class="pl-sec pl-sec--health" aria-labelledby="pl-hh"><h3 id="pl-hh" class="pl-sec-h"><span>' + esc(S.healthH) + ' · ' + esc(countryName(k.id)) + '</span></h3><p class="pl-sub">' + esc(S.healthSub) + '</p>';
    if (st.o && st.o === st.d) h += '<p class="pl-note">' + esc(S.domestic) + '</p>';
    h += '<ol class="pl-tl">';
    if (!events.length) h += '<li class="pl-tl-item pl-tl-none"><p>' + esc(S.eventsNone) + '</p></li>';
    events.forEach(function (e) {
      var past = e.d < now;
      h += '<li class="pl-tl-item' + (past ? ' is-past' : '') + '"><span class="pl-tl-node" aria-hidden="true"></span><div class="pl-tl-date"><time datetime="' + iso(e.d) + '">' + esc(fd(e.d)) + '</time><span class="pl-tl-delta">' + esc(fmtS(S.countback, { v: e.t.value, u: S.units[e.t.unit] || e.t.unit })) + '</span>' + (past ? statusChip('warn', S.passed) : '') + '</div>' +
        '<div class="pl-tl-body"><p class="pl-tl-k">' + esc(S.req[e.key]) + (e.applies ? ' · <span class="pl-tl-ap">' + fullAndExcerpt(e.applies, 90) + '</span>' : '') + '</p><blockquote lang="en">' + quoteAround(e.quote, e.t.as_stated, 300) + '</blockquote></div></li>';
    });
    h += '<li class="pl-tl-item pl-tl-travel"><span class="pl-tl-node" aria-hidden="true"></span><div class="pl-tl-date"><time datetime="' + iso(travel) + '">' + esc(fd(travel)) + '</time><span class="pl-tl-delta">' + esc(S.travelDay) + '</span></div><div class="pl-tl-body"><p class="pl-tl-k">' + esc(countryName(st.o) && st.o && st.o !== 'other' ? countryName(st.o) + ' → ' + countryName(k.id) : countryName(k.id)) + '</p></div></li></ol>';
    h += '<h4 class="pl-sub-h">' + esc(S.reqDetails) + '</h4><dl class="pl-reqs">';
    var shown = {};
    REQ_ORDER.forEach(function (key) {
      var r = viewReq(k.requirements[key] || {});
      var chip = r._otherOnly ? '' : r.required === true ? statusChip('ok', S.rTrue) : (r.required === false ? statusChip('na', S.rFalse) : (r.as_stated ? statusChip('warn', S.rNull) : ''));
      h += '<div class="pl-req"><dt><span class="pl-req-name">' + esc(S.req[key]) + '</span>' + chip +
        (r.applies_to ? '<span class="pl-req-meta"><span class="pl-as-k">' + esc(S.appliesTo) + '</span> ' + fullAndExcerpt(r.applies_to, 90) + '</span>' : '') +
        (r.standard ? '<span class="pl-req-meta"><span class="pl-as-k">' + esc(S.standard) + '</span> ' + esc(r.standard) + '</span>' : '') +
        '</dt><dd class="pl-req-txt" lang="en">' + (r.as_stated ? (function () {
          var nNew = 0, more = 0, refs = {};
          var out = r.as_stated.split(' | ').map(function (x) {
            var t = x.trim();
            if (shown[t]) {
              if (refs[shown[t]]) return '';
              refs[shown[t]] = 1;
              return '<p class="pl-same" lang="' + LANG + '">' + esc(fmtS(S.sameAs, { r: S.req[shown[t]] })) + '</p>';
            }
            shown[t] = key; nNew++;
            if (nNew > 1) { more++; return '<p class="pl-more">' + fullAndExcerpt(t, 300) + '</p>'; }
            return '<p>' + fullAndExcerpt(t, 300) + '</p>';
          }).join('');
          return out + (more ? '<p class="pl-morenote print-only" lang="' + LANG + '">' + esc(fmtS(S.morePara, { n: more })) + '</p>' : '') +
            (r._hidden ? '<p class="pl-same" lang="' + LANG + '">' + esc(fmtS(S.otherSpecies, { n: r._hidden, s: S[st.sp] || st.sp })) + '</p>' : '');
        })() : (r._otherOnly ? '<p class="pl-same" lang="' + LANG + '">' + esc(fmtS(S.otherSpeciesOnly, { s: S[st.sp] || st.sp })) + '</p>' : nullC())) + '</dd></div>';
    });
    h += '</dl>';
    if (k.cases && k.cases.length) {
      var who = st.sp === 'dog' ? /dog/i : (st.sp === 'cat' ? /cat/i : /./);
      var cs = k.cases.filter(function (c) { return who.test(c.who || ''); });
      if (cs.length) {
        h += '<h4 class="pl-sub-h">' + esc(S.casesH) + '</h4><div class="pl-cases">';
        cs.forEach(function (c) {
          h += '<article class="pl-case"><p class="pl-case-k">' + esc([c.who, c.direction, c['case']].filter(Boolean).join(' · ')) + '</p><p lang="en">' + fullAndExcerpt(c.rule_as_stated, 260) + '</p>' +
            (c.source_urls || []).map(function (u) { return '<a class="pl-src" href="' + esc(u) + '" rel="noopener" target="_blank">' + esc(S.officialSrc) + ' ↗<span class="pl-url">' + esc(u) + '</span></a>'; }).join(' ') + '</article>';
        });
        h += '</div>';
      }
    }
    return h + (LANG === 'en' ? '' : '<p class="pl-hint screen-only">' + esc(S.quotedEn) + '</p>') + '</section>';
  }

  function host(u) { try { var x = new URL(u); return x.hostname.replace(/^www\./, '') + (x.pathname.length > 1 ? x.pathname.replace(/\/$/, '').replace(/^(.{0,34}).*$/, function (m, a) { return a + (m.length > 34 ? '…' : ''); }) : ''); } catch (e) { return u; } }
  function statusLabel(s) { return s === 'verified' ? S.verified : (s === 'checked' ? S.checked : S.notVerified); }
  function srcBlock(kind, rec, localPage) {
    var d = parseDate(rec.verified_date);
    var h = '<div class="pl-srcbox"><p class="pl-srcbox-k">' + esc(kind) + ' · ' + esc(kind === S.airlineSrc ? rec.name + (rec.iata ? ' (' + rec.iata + ')' : '') : countryName(rec.id)) + '</p>' +
      '<p class="pl-verif">' + statusChip(rec.verification_status === 'verified' ? 'ok' : (rec.verification_status === 'checked' ? 'warn' : 'bad'), statusLabel(rec.verification_status)) +
      ' <time datetime="' + esc(rec.verified_date) + '">' + esc(d ? fds(d) : rec.verified_date) + '</time> <span class="pl-iso">(' + esc(rec.verified_date) + ')</span></p>' +
      (rec.verification_as_stated ? '<p class="pl-hint" lang="en">' + esc(rec.verification_as_stated) + '</p>' : '') + '<p class="pl-as-k pl-srch">' + esc(S.officialSrc) + ' (' + (rec.official_source_urls || []).length + ')</p><ul class="pl-srclist">';
    (rec.official_source_urls || []).forEach(function (u) {
      h += '<li><a href="' + esc(u) + '" rel="noopener" target="_blank" title="' + esc(u) + '"><span class="pl-host">' + esc(host(u)) + '</span> <span aria-hidden="true">↗</span></a><span class="pl-url">' + esc(u) + '</span></li>';
    });
    h += '</ul><p class="pl-ppc"><a href="' + esc(localPage.url) + '">' + esc(S.ppcPage) + esc(localPage.suffix || '') + ' →</a><span class="pl-url">' + esc('petpolicycheck.com' + localPage.url) + '</span></p></div>';
    return h;
  }
  function airlinePage(a) {
    if (LANG !== 'en' && EN_ONLY_AIRLINES.indexOf(a.id) < 0) return { url: LOCAL_TREE + '/airlines/' + a.id + '.html' };
    return { url: '/airlines/' + a.id + '.html', suffix: LANG !== 'en' ? S.airlineNoLocal : '' };
  }

  function results() {
    var a = byA[st.a], k = byK[st.d], travel = parseDate(st.dt);
    if (!a || !k || !travel) { st.step = 2; return step2(); }
    var petLine = S[st.sp] + (st.breed ? ' · ' + st.breed : '') + (st.snub ? ' · ' + S.snub : '') + (C.num(st.pw) !== null ? ' · ' + n2(st.pw) + ' ' + S[st.wu] : '');
    var tripLine = (st.o && st.o !== 'other' ? countryName(st.o) : (st.o === 'other' ? S.otherCountry : '—')) + ' → ' + countryName(k.id);
    var r = a.restrictions || {};
    var h = '<article class="pl-plan" aria-labelledby="pl-h3">' +
      '<header class="pl-plan-head"><span class="pl-corner tl" aria-hidden="true"></span><span class="pl-corner tr" aria-hidden="true"></span>' +
      '<p class="pl-kicker">' + esc(S.planKicker) + ' · PetPolicyCheck</p><h2 id="pl-h3" tabindex="-1">' + esc(S.planFor) + ' · ' + esc(tripLine) + '</h2>' +
      '<dl class="pl-sum"><div><dt>' + esc(S.summaryPet) + '</dt><dd>' + esc(petLine) + '</dd></div><div><dt>' + esc(S.summaryTrip) + '</dt><dd>' + esc(tripLine) + '</dd></div><div><dt>' + esc(S.summaryAirline) + '</dt><dd>' + esc(a.name + (a.iata ? ' (' + a.iata + ')' : '')) + '</dd></div><div><dt>' + esc(S.summaryDate) + '</dt><dd><time datetime="' + iso(travel) + '">' + esc(fd(travel)) + '</time></dd></div></dl>' +
      '<p class="pl-gen">' + esc(fmtS(S.generated, { d: fds(today()) })) + '<span class="pl-printurl print-only">' + esc(shareUrl()) + '</span></p>' +
      '<div class="pl-actions no-print"><button type="button" class="pl-btn" data-act="print">' + esc(S.print) + '</button><button type="button" class="pl-btn ghost" data-act="copy">' + esc(S.copy) + '</button><button type="button" class="pl-btn ghost" data-act="edit">' + esc(S.edit) + '</button><button type="button" class="pl-btn ghost" data-act="reset">' + esc(S.reset) + '</button><span class="pl-copied" role="status" aria-live="polite"></span></div></header>';

    h += '<section class="pl-sec" aria-labelledby="pl-mh"><h3 id="pl-mh" class="pl-sec-h"><span>' + esc(S.modesH) + ' · ' + esc(a.name) + '</span></h3><div class="pl-modes">';
    h += '<article class="pl-mode"><h4>' + esc(S.cabin) + '</h4>' + modeChip(a.cabin) + '<p class="pl-as"><span class="pl-as-k">' + esc(S.statedAs) + '</span> ' + txtA(a.cabin_as_stated) + '</p></article>';
    h += '<article class="pl-mode"><h4>' + esc(S.hold) + '</h4>' + modeChip(a.hold) + '<p class="pl-as"><span class="pl-as-k">' + esc(S.statedAs) + '</span> ' + txtA(a.hold_or_cargo_as_stated) + '</p><p class="pl-as"><span class="pl-as-k">' + esc(S.limits) + '</span> ' + txtA(a.hold_limits_as_stated) + '</p></article>';
    h += '<article class="pl-mode"><h4>' + esc(S.cargo) + '</h4>' + modeChip(a.cargo) + '<p class="pl-as"><span class="pl-as-k">' + esc(S.cargoOnly) + '</span> ' + txtA(r.cargo_only_as_stated) + '</p></article>';
    h += '</div></section>';

    h += '<section class="pl-sec" aria-labelledby="pl-ch"><h3 id="pl-ch" class="pl-sec-h"><span>' + esc(S.crateH2) + '</span></h3><div class="pl-checks">' + speciesBlock(a) + weightBlock(a) + dimBlock(a) + '</div></section>';

    h += '<section class="pl-sec pl-sec--two" aria-labelledby="pl-fh"><div><h3 id="pl-fh" class="pl-sec-h"><span>' + esc(S.feesH) + '</span></h3>';
    if (a.fees && a.fees.length) {
      var groups = [];
      a.fees.forEach(function (f) {
        /* group same-scope records only when each one's wording is just its figure (e.g. "EUR 65-85"), so no amount loses its context */
        var g = groups[groups.length - 1], fa = feeAmount(f), bare = !!fa && sameFeeText((f.as_stated || '').trim(), fa, f.scope);
        if (!g || !f.scope || g.scope !== f.scope) { g = { scope: f.scope || '', fees: [], bare: true }; groups.push(g); }
        if (!bare) g.bare = false;
        g.fees.push(f);
      });
      h += '<ul class="pl-fees">' + groups.map(function (g) {
        var shownT = g.fees.filter(function (f) { var fa = feeAmount(f); return !(fa && sameFeeText((f.as_stated || '').trim(), fa, g.scope)); });
        var dupScope = !g.bare && shownT.length === g.fees.length && shownT.every(function (f) { return (f.as_stated || '').trim().indexOf(g.scope) === 0; });
        var head = '<li>' + (g.scope ? '<span class="pl-as-k' + (dupScope ? ' pl-scope-dup' : '') + '">' + esc(g.scope) + '</span> ' : '');
        if (g.bare) /* every record is just its figure: one line of amounts */
          return head + '<span class="pl-fee-amt">' + g.fees.map(function (f) { return esc(feeAmount(f)); }).join(' <span class="pl-fee-sep">·</span> ') + '</span></li>';
        var seenT = [];
        return head + g.fees.map(function (f) {
          var fa = feeAmount(f), t = (f.as_stated || '').trim(), dup = seenT.indexOf(t) >= 0;
          seenT.push(t);
          var txt = t && !dup && !(fa && sameFeeText(t, fa, g.scope));
          return '<span class="pl-fee-row">' + (fa ? '<span class="pl-fee-amt">' + esc(fa) + '</span>' : '') +
            (txt ? '<span class="pl-fee-txt' + (fa ? '' : ' pl-fee-txt--only') + '">' + (fa ? '<span class="pl-as-k">' + esc(S.feeSrcText) + '</span> ' : '') + '<span lang="en">' + fullAndExcerpt(t, 280) + '</span></span>' : '') + '</span>';
        }).join('') + '</li>';
      }).join('') + '</ul>';
    } else h += '<p class="pl-as">' + (a.fees_as_stated ? '<span class="pl-as-k">' + esc(S.statedAs) + '</span> ' + esc(a.fees_as_stated) : nullA()) + '</p>';
    h += '</div><div><h3 class="pl-sec-h"><span>' + esc(S.restrH) + '</span></h3><dl class="pl-dl pl-dl--restr">' +
      '<dt' + (st.snub ? ' class="is-flag"' : '') + '>' + esc(S.brachy) + (st.snub ? ' <span class="pl-flag">' + esc(S.snubFlag) + '</span>' : '') + '</dt><dd>' + txtA(r.brachycephalic_as_stated) + '</dd>' +
      '<dt>' + esc(S.breeds) + '</dt><dd>' + txtA(r.breeds_as_stated) + '</dd>' +
      '<dt>' + esc(S.routes) + '</dt><dd>' + txtA(r.routes_as_stated) + '</dd>' +
      '<dt>' + esc(S.service) + '</dt><dd>' + txtA(a.service_animals_as_stated) + '</dd></dl></div></section>';

    h += healthBlock(k, travel);

    h += '<section class="pl-sec pl-sec--src" aria-labelledby="pl-sh"><h3 id="pl-sh" class="pl-sec-h"><span>' + esc(S.sourcesH) + '</span></h3><div class="pl-srcgrid">' +
      srcBlock(S.airlineSrc, a, airlinePage(a)) + srcBlock(S.countrySrc, k, { url: LOCAL_TREE + '/countries/' + k.id + '.html' }) + '</div>' +
      '<p class="pl-disc">' + esc(S.disclaimer) + ' <span class="pl-print-note print-only">' + (LANG === 'en' ? '' : esc(S.quotedEn) + ' ') + esc(S.printExcerpt) + '</span></p><p class="pl-hint pl-privacy">' + esc(S.privacy) + '</p></section></article>';
    return h;
  }

  /* ---------- render & events ---------- */
  function render(focus) {
    var body = st.step === 1 ? step1() : (st.step === 2 ? step2() : results());
    root.innerHTML = rail() + '<div class="pl-stage">' + body + '</div>';
    root.setAttribute('data-step', st.step);
    save();
    if (focus) { var hh = root.querySelector('h2[tabindex]'); if (hh) hh.focus({ preventScroll: false }); }
  }
  function setErr(id, msg) {
    var el = $(id), e = $(id + '-err');
    if (el) { if (msg) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid'); }
    if (e) e.textContent = msg || '';
    return !msg;
  }
  function valid1() {
    var ok = true;
    [['pl-pw', 'pw'], ['pl-cw', 'cw'], ['pl-l', 'l'], ['pl-w', 'w'], ['pl-h', 'h']].forEach(function (p) {
      var v = st[p[1]]; var bad = v !== '' && C.num(v) === null;
      ok = setErr(p[0], bad ? S.errNum : '') && ok;
    });
    return ok;
  }
  function valid2() {
    var ok = setErr('pl-d', byK[st.d] ? '' : S.errDest);
    ok = setErr('pl-a', byA[st.a] ? '' : S.errAirline) && ok;
    ok = setErr('pl-dt', parseDate(st.dt) ? '' : S.errDate) && ok;
    if (!ok) { var f = root.querySelector('[aria-invalid="true"]'); if (f) f.focus(); }
    return ok;
  }
  function go(n) { st.step = n; render(true); window.scrollTo({ top: Math.max(0, root.getBoundingClientRect().top + window.scrollY - 90), behavior: 'auto' }); }

  root.addEventListener('input', function (e) {
    var el = e.target, k = el.getAttribute('data-k');
    if (el.type === 'radio') { st[el.name] = el.value; save(); if (el.name === 'wu' || el.name === 'lu') { var f = el.id; render(false); var r = $(f); if (r) r.focus(); } return; }
    if (!k) return;
    st[k] = el.type === 'checkbox' ? (el.checked ? 1 : 0) : el.value.trim();
    save();
  });
  root.addEventListener('change', function (e) { var el = e.target; if (el.tagName === 'SELECT' || el.type === 'checkbox' || el.type === 'date') { var k = el.getAttribute('data-k'); if (k) { st[k] = el.type === 'checkbox' ? (el.checked ? 1 : 0) : el.value; save(); } } });
  root.addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    var act = b.getAttribute('data-act'), to = b.getAttribute('data-go');
    if (to) { to = +to; if (to < st.step) go(to); return; }
    if (act === 'next') { if (valid1()) go(2); }
    else if (act === 'back') go(1);
    else if (act === 'build') { if (valid2()) go(3); }
    else if (act === 'edit') go(1);
    else if (act === 'reset') { st = defaults(); try { localStorage.removeItem(STORE); } catch (x) {} go(1); }
    else if (act === 'print') window.print();
    else if (act === 'copy') {
      var url = shareUrl(), out = root.querySelector('.pl-copied');
      var done = function () { if (out) out.textContent = S.copied; };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function () { window.prompt(S.copy, url); });
      else window.prompt(S.copy, url);
    }
  });
  window.addEventListener('hashchange', function () { var n = decode(location.hash.slice(1)); if (encode() !== location.hash.slice(1)) { st = n; render(false); } });

  root.innerHTML = '<p class="pl-loading" role="status">' + esc(S.loading) + '</p>';
  Promise.all([fetch(BASE + 'airlines.json?v=20261118pl4').then(function (r) { if (!r.ok) throw r.status; return r.json(); }), fetch(BASE + 'countries.json?v=20261118pl4').then(function (r) { if (!r.ok) throw r.status; return r.json(); })])
    .then(function (res) {
      A = res[0]; K = res[1];
      A.forEach(function (a) { byA[a.id] = a; }); K.forEach(function (k) { byK[k.id] = k; });
      var hash = location.hash.slice(1), saved = null;
      try { saved = localStorage.getItem(STORE); } catch (e) {}
      st = decode(hash || saved || '');
      if (st.step === 3 && !(byA[st.a] && byK[st.d] && parseDate(st.dt))) st.step = byK[st.d] ? 2 : 1;
      render(false);
    })
    .catch(function () { root.innerHTML = '<p class="pl-err" role="alert">' + esc(S.loadErr) + '</p>'; });
})();
