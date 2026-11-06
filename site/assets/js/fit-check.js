/* PetPolicyCheck · /fit/ under-seat carrier fit check · v2 2026-11-07
   Data: window.PPC_COMPARATOR (assets/js/airlines-comparator-data.js — same sourced rows as /airlines/compare/).
   Two views (front L×H, side W×H) drawn to scale per view; airline limit = dashed gold outline, carrier = teal fill,
   overage = red with "+X" delta. No values are invented: anything that does not parse shows "Check with airline". */
(function () {
  'use strict';
  var DATA = window.PPC_COMPARATOR || { airlines: [] };
  var AIR = (DATA.airlines || []).slice().sort(function (a, b) { return a.name.localeCompare(b.name); });
  var EN = (window.PPC_I18N && window.PPC_I18N.strings && window.PPC_I18N.strings.en) || {};
  var NS = 'http://www.w3.org/2000/svg';
  var RE = /(\d+(?:\.\d+)?)\s*(?:L\s*)?x\s*(\d+(?:\.\d+)?)\s*(?:W\s*|H\s*)?x\s*(\d+(?:\.\d+)?)\s*(?:H\s*|W\s*)?(cm|in)/i;
  var C = { gold: '#d9b765', teal: '#8fc9c9', tealFill: 'rgba(143,201,201,.38)', over: '#e07a6e', overFill: 'rgba(224,122,110,.38)', ink: '#ece4d0', mut: '#a9b3a4', bg: '#0b1719', paper: '#11252a' };
  function $(id) { return document.getElementById(id); }
  function t(k, vars) {
    var v = (window.PPC_LANG && window.PPC_LANG.t && window.PPC_LANG.t(k)) || EN[k] || k;
    if (vars) Object.keys(vars).forEach(function (n) { v = v.split('{' + n + '}').join(vars[n]); });
    return v;
  }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fold(s) { return String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }
  function r1(x) { return Math.round(x * 10) / 10; }
  function fmt(x) { var v = r1(x); return (Math.abs(v - Math.round(v)) < 1e-9 ? String(Math.round(v)) : v.toFixed(1)); }
  function cabinOK(a) { return !!(a.cabin_dogs || a.cabin_cats); }

  /* ---------- data → variants ---------- */
  function variantsOf(a) {
    var out = [];
    (a.underseat_soft_dims_in_cm || []).forEach(function (s, i) {
      var m = RE.exec(String(s)); if (!m) return;
      var label = String(s).slice(0, m.index).replace(/[\s:,(–-]+$/, '').trim();
      var low = String(s).toLowerCase(), ll = label.toLowerCase();
      var softOnly = /soft[^,;]*only|soft\/flexible only|soft without solid frame/.test(low);
      var kind = (/hard/.test(ll) && !/soft/.test(ll)) ? 'hard' : (/soft/.test(ll) && !/hard/.test(ll)) ? 'soft' : softOnly ? 'soft' : 'any';
      out.push({ i: i, raw: String(s), label: label, L: +m[1], W: +m[2], H: +m[3], unit: m[4].toLowerCase(), softOnly: softOnly, kind: kind });
    });
    return out;
  }
  function vol(v) { var f = v.unit === 'in' ? 2.54 : 1; return v.L * v.W * v.H * f * f * f; }
  function dimText(v) { return fmt(v.L) + ' × ' + fmt(v.W) + ' × ' + fmt(v.H) + ' ' + v.unit; }

  /* ---------- state ---------- */
  var st = { a: null, vars: [], v: null, auto: true };
  function carrier() {
    return { L: parseFloat($('fL').value), W: parseFloat($('fW').value), H: parseFloat($('fH').value), unit: $('fU').value, soft: $('fSoft').checked };
  }
  function pickAuto(vars, soft) {
    var app = vars.filter(function (v) { return soft ? v.kind !== 'hard' : v.kind !== 'soft'; });
    if (!app.length) app = vars.slice();
    return app.reduce(function (m, v) { return !m || vol(v) < vol(m) ? v : m; }, null);
  }

  /* ---------- comparison (in the airline's published unit, rounded to 0.1) ---------- */
  function compare(v, c) {
    var k = (c.unit === v.unit) ? 1 : (c.unit === 'cm' ? 1 / 2.54 : 2.54);
    var m = { L: r1(c.L * k), W: r1(c.W * k), H: r1(c.H * k) };
    function ex(L, W) { return Math.max(0, L - v.L) + Math.max(0, W - v.W); }
    var rot = ex(m.W, m.L) < ex(m.L, m.W) - 1e-9;
    var cc = rot ? { L: m.W, W: m.L, H: m.H } : m;
    var back = 1 / k, d = {}, over = [];
    ['L', 'W', 'H'].forEach(function (x) { d[x] = r1(cc[x] - v[x]); if (d[x] > 0) over.push(x); });
    var u = c.unit;
    return {
      rot: rot, over: over, unit: u,
      lim: { L: v.L * back, W: v.W * back, H: v.H * back },              // limit in user's unit
      car: { L: (rot ? c.W : c.L), W: (rot ? c.L : c.W), H: c.H },         // carrier (oriented) in user's unit
      delta: { L: d.L * back, W: d.W * back, H: d.H * back }               // + = over, in user's unit
    };
  }

  /* ---------- SVG view ---------- */
  function el(tag, attrs, text) {
    var e = document.createElementNS(NS, tag);
    Object.keys(attrs).forEach(function (k) { e.setAttribute(k, attrs[k]); });
    if (text != null) e.textContent = text;
    return e;
  }
  /* view: horizontal key hx ('L' or 'W'), vertical 'H' */
  function drawView(svg, res, hx, title) {
    while (svg.firstChild) svg.removeChild(svg.firstChild);
    var VW = 360, VH = 262, left = 68, right = 12, top = 12, bottom = 68, fs = 16, u = res.unit;
    var limX = res.lim[hx], limY = res.lim.H, carX = res.car[hx], carY = res.car.H;
    var s = Math.min((VW - left - right) / Math.max(limX, carX), (VH - top - bottom) / Math.max(limY, carY));
    var x0 = left, fl = VH - bottom;
    svg.setAttribute('viewBox', '0 0 ' + VW + ' ' + VH);
    svg.setAttribute('role', 'img');
    var oX = res.delta[hx] > 0, oY = res.delta.H > 0;
    svg.setAttribute('aria-label', title + ': ' + t('fit.leg.limit') + ' ' + fmt(limX) + ' × ' + fmt(limY) + ' ' + u + ', ' + t('fit.leg.carrier') + ' ' + fmt(carX) + ' × ' + fmt(carY) + ' ' + u);
    svg.appendChild(el('rect', { x: 0, y: 0, width: VW, height: VH, fill: C.bg }));
    svg.appendChild(el('line', { x1: x0 - 4, y1: fl, x2: VW - right, y2: fl, stroke: 'rgba(236,228,208,.35)', 'stroke-width': 1 }));
    // carrier (solid, semi-transparent)
    svg.appendChild(el('rect', { x: x0, y: fl - carY * s, width: carX * s, height: carY * s, fill: C.tealFill, stroke: C.teal, 'stroke-width': 2, rx: 3 }));
    // overage areas
    if (oY) svg.appendChild(el('rect', { x: x0, y: fl - carY * s, width: Math.min(carX, limX) * s, height: (carY - limY) * s, fill: C.overFill, stroke: C.over, 'stroke-width': 2 }));
    if (oX) svg.appendChild(el('rect', { x: x0 + limX * s, y: fl - Math.min(carY, limY) * s, width: (carX - limX) * s, height: Math.min(carY, limY) * s, fill: C.overFill, stroke: C.over, 'stroke-width': 2 }));
    if (oX && oY) svg.appendChild(el('rect', { x: x0 + limX * s, y: fl - carY * s, width: (carX - limX) * s, height: (carY - limY) * s, fill: C.overFill, stroke: C.over, 'stroke-width': 2 }));
    // airline limit (dashed gold outline, on top)
    svg.appendChild(el('rect', { x: x0, y: fl - limY * s, width: limX * s, height: limY * s, fill: 'none', stroke: C.gold, 'stroke-width': 2.5, 'stroke-dasharray': '8 5' }));
    // horizontal rails (below floor): limit row then carrier row
    function hRail(y, len, col, label, lcol) {
      svg.appendChild(el('line', { x1: x0, y1: y, x2: x0 + len * s, y2: y, stroke: col, 'stroke-width': 2, 'stroke-dasharray': col === C.gold ? '6 4' : '0' }));
      svg.appendChild(el('line', { x1: x0, y1: y - 5, x2: x0, y2: y + 5, stroke: col, 'stroke-width': 2 }));
      svg.appendChild(el('line', { x1: x0 + len * s, y1: y - 5, x2: x0 + len * s, y2: y + 5, stroke: col, 'stroke-width': 2 }));
      var cx = Math.max(x0 + 64, Math.min(VW - right - 64, x0 + len * s / 2));
      svg.appendChild(el('text', { x: cx, y: y + 19, fill: lcol, 'font-size': fs, 'text-anchor': 'middle', 'font-family': 'system-ui,-apple-system,Segoe UI,Roboto,sans-serif', 'font-weight': lcol === C.over ? 700 : 400 }, label));
    }
    hRail(fl + 10, limX, C.gold, fmt(limX) + ' ' + u, C.gold);
    hRail(fl + 40, carX, C.teal, fmt(carX) + ' ' + u + (oX ? '  +' + fmt(res.delta[hx]) + ' ' + u : ''), oX ? C.over : C.teal);
    // vertical rails (left of shape): limit column then carrier column, labels rotated
    function vRail(x, len, col, label, lcol) {
      svg.appendChild(el('line', { x1: x, y1: fl, x2: x, y2: fl - len * s, stroke: col, 'stroke-width': 2, 'stroke-dasharray': col === C.gold ? '6 4' : '0' }));
      svg.appendChild(el('line', { x1: x - 5, y1: fl - len * s, x2: x + 5, y2: fl - len * s, stroke: col, 'stroke-width': 2 }));
      var cy = Math.max(top + 62, Math.min(fl - 62, fl - len * s / 2)), tx = x - 9;
      svg.appendChild(el('text', { x: tx, y: cy, fill: lcol, 'font-size': fs, 'text-anchor': 'middle', transform: 'rotate(-90 ' + tx + ' ' + cy + ')', 'font-family': 'system-ui,-apple-system,Segoe UI,Roboto,sans-serif', 'font-weight': lcol === C.over ? 700 : 400 }, label));
    }
    vRail(x0 - 10, limY, C.gold, fmt(limY) + ' ' + u, C.gold);
    vRail(x0 - 40, carY, C.teal, fmt(carY) + ' ' + u + (oY ? '  +' + fmt(res.delta.H) + ' ' + u : ''), oY ? C.over : C.teal);
  }

  /* ---------- select (grouped by region, filterable) ---------- */
  function regionLabel(r) { var k = 'fit.r.' + r, v = t(k); return v === k ? r : v; }
  function buildSelect() {
    var sel = $('fAir'), cur = sel.value || (st.a && st.a.id), q = fold($('fQ').value).trim();
    var groups = {};
    AIR.forEach(function (a) {
      if (q && fold(a.name + ' ' + a.iata + ' ' + a.id).indexOf(q) < 0) return;
      (groups[a.region] = groups[a.region] || []).push(a);
    });
    sel.innerHTML = '';
    var regs = Object.keys(groups).sort(function (x, y) { return regionLabel(x).localeCompare(regionLabel(y)); });
    regs.forEach(function (r) {
      var og = document.createElement('optgroup'); og.label = regionLabel(r);
      groups[r].forEach(function (a) {
        var o = document.createElement('option'); o.value = a.id;
        o.textContent = a.name + (a.iata ? ' (' + a.iata + ')' : '') + (cabinOK(a) ? '' : ' — ' + t('fit.nocabin.tag'));
        og.appendChild(o);
      });
      sel.appendChild(og);
    });
    $('fQmsg').hidden = regs.length > 0;
    if (cur && sel.querySelector('option[value="' + cur + '"]')) sel.value = cur;
    else if (sel.options.length) { sel.selectedIndex = 0; }
    return sel.value;
  }
  function buildVariants() {
    var a = st.a, vs = st.vars, wrap = $('fVarWrap'), sel = $('fVar');
    if (!a || vs.length < 2) { wrap.hidden = true; sel.innerHTML = ''; return; }
    wrap.hidden = false;
    var cur = st.auto ? 'auto' : String(st.v && st.v.i);
    sel.innerHTML = '<option value="auto">' + esc(t('fit.variant.strict')) + '</option>' + vs.map(function (v) {
      return '<option value="' + v.i + '">' + esc((v.label || a.name) + ' — ' + dimText(v)) + '</option>';
    }).join('');
    sel.value = cur;
  }

  /* ---------- render ---------- */
  var last = null;
  function render(pushUrl) {
    var a = st.a, c = carrier(), res = $('fitRes'), views = $('fitViews');
    last = { a: a, c: c, kind: null, res: null, v: null };
    if (!a) return;
    st.vars = variantsOf(a);
    if (st.auto || !st.v || st.vars.indexOf(st.v) < 0) {
      var keepI = (!st.auto && st.v) ? st.v.i : null;
      st.v = (keepI != null && st.vars.filter(function (v) { return v.i === keepI; })[0]) || pickAuto(st.vars, c.soft);
      if (keepI == null) st.auto = true;
    }
    buildVariants();
    var raw = (a.underseat_soft_dims_in_cm || []).map(function (s) { return '<li>' + esc(s) + '</li>'; }).join('');
    var src = '<p class="src"><span class="fit-badge">' + esc(t('fit.checked', { d: a.last_verified || '—' })) + '</span><br>'
      + (a.official_policy_url ? '<a href="' + esc(a.official_policy_url) + '" target="_blank" rel="noopener">' + esc(t('fit.source')) + ' ↗</a>' : '')
      + (a.ppc_guide_url ? ' · <a href="' + esc(a.ppc_guide_url) + '">PetPolicyCheck</a>' : '') + '</p>';
    var weight = a.max_weight_cabin_lb_kg ? '<p class="fit-note">' + esc(t('fit.weight')) + ': ' + esc(a.max_weight_cabin_lb_kg) + '</p>' : '';
    var details = '';
    var notes = raw ? '<p class="fit-note" style="border:0;padding:0;margin-bottom:0">' + esc(t('fit.notes')) + ':</p><ul class="raw">' + raw + '</ul>' : '';

    if (!cabinOK(a)) {
      last.kind = 'nocabin';
      views.innerHTML = '<div class="fit-msg"><h3>' + esc(t('fit.v.nocabin')) + '</h3><p>' + esc(a.cargo_or_checked_allowed ? t('fit.v.nocabin.hold') : '') + '</p></div>';
      $('fitLegend').hidden = true;
      res.innerHTML = '<p class="air">' + esc(a.name) + '</p><h2 class="bad">' + esc(t('fit.v.nocabin')) + '</h2>'
        + (a.cargo_fee_note ? '<p class="fit-note">' + esc(a.cargo_fee_note) + '</p>' : '') + src;
      details = notes;
    } else if (!st.v) {
      last.kind = 'check';
      views.innerHTML = '<div class="fit-msg"><h3>' + esc(t('fit.v.check')) + '</h3><p>' + esc(t('fit.v.check.why')) + '</p></div>';
      $('fitLegend').hidden = true;
      res.innerHTML = '<p class="air">' + esc(a.name) + '</p><h2 class="chk-airline">' + esc(t('fit.v.check')) + '</h2><p class="fit-note">' + esc(t('fit.v.check.why')) + '</p>' + src;
      details = weight + notes;
    } else if (!(c.L > 0 && c.W > 0 && c.H > 0)) {
      last.kind = 'enter';
      views.innerHTML = '<div class="fit-msg"><p>' + esc(t('fit.v.enter')) + '</p></div>';
      $('fitLegend').hidden = true;
      res.innerHTML = '<p class="air">' + esc(a.name) + '</p><h2>' + esc(t('fit.v.enter')) + '</h2>' + src;
      details = '';
    } else {
      var r = compare(st.v, c); last.kind = 'dims'; last.res = r; last.v = st.v;
      views.innerHTML = '<figure class="fit-view"><figcaption>' + esc(t('fit.front')) + '</figcaption><svg id="svgFront" xmlns="' + NS + '"></svg></figure>'
        + '<figure class="fit-view"><figcaption>' + esc(t('fit.side')) + '</figcaption><svg id="svgSide" xmlns="' + NS + '"></svg></figure>';
      drawView($('svgFront'), r, 'L', t('fit.front'));
      drawView($('svgSide'), r, 'W', t('fit.side'));
      $('fitLegend').hidden = false;
      var ok = !r.over.length, u = r.unit;
      var head = ok ? t('fit.v.ok') : t('fit.v.ko');
      var sub = ok ? '' : (r.over.length === 1 ? t('fit.v.over1') : t('fit.v.overN', { n: r.over.length }));
      var rows = ['L', 'W', 'H'].map(function (x) {
        var over = r.delta[x] > 0;
        return '<tr><td>' + esc(t('fit.dim' + x)) + '</td><td>' + fmt(r.lim[x]) + '</td><td>' + fmt(r.car[x]) + '</td><td class="' + (over ? 'over' : 'fine') + '">'
          + (over ? '+' + fmt(r.delta[x]) + ' ' + u : '✓') + '</td></tr>';
      }).join('');
      var extra = '';
      if (st.vars.length > 1) extra += '<p class="fit-note">' + esc(t('fit.multi')) + '</p>';
      if (st.v.softOnly && !c.soft) extra += '<p class="fit-note fit-warn">' + esc(t('fit.softonly')) + '</p>';
      if (c.soft) extra += '<p class="fit-note">' + esc(t('fit.softnote')) + '</p>';
      if (r.rot) extra += '<p class="fit-note">' + esc(t('fit.rotated')) + '</p>';
      if (st.v.unit !== c.unit) extra += '<p class="fit-note">' + esc(t('fit.unitnote', { u: st.v.unit })) + '</p>';
      res.innerHTML = '<p class="air">' + esc(a.name) + (st.v.label ? ' · ' + esc(st.v.label) : '') + ' — ' + esc(dimText(st.v)) + '</p>'
        + '<h2 class="' + (ok ? 'ok' : 'bad') + '">' + esc(head) + '</h2>' + (sub ? '<p class="bad" style="margin:0;font-weight:700">' + esc(sub) + '</p>' : '')
        + '<table><thead><tr><th>' + esc(t('fit.r.dim')) + '</th><th>' + esc(t('fit.r.limit')) + ' (' + u + ')</th><th>' + esc(t('fit.r.yours')) + ' (' + u + ')</th><th>' + esc(t('fit.r.delta')) + '</th></tr></thead><tbody>' + rows + '</tbody></table>'
        + extra + src;
      details = weight + '<p class="fit-note">' + esc(t('fit.axis')) + '</p>' + notes;
    }
    $('fitDetails').innerHTML = details;
    if (pushUrl) {
      try {
        var q = new URLSearchParams(location.search);
        q.set('airline', a.id); q.set('L', $('fL').value); q.set('W', $('fW').value); q.set('H', $('fH').value); q.set('u', c.unit); q.set('soft', c.soft ? '1' : '0');
        if (st.auto) q.delete('size'); else q.set('size', String(st.v.i));
        history.replaceState(null, '', location.pathname + '?' + q.toString());
      } catch (e) {}
    }
  }

  /* ---------- PNG export (draws the same SVG views) ---------- */
  function svgImage(svg, w, h) {
    return new Promise(function (ok) {
      var cl = svg.cloneNode(true); cl.setAttribute('width', w); cl.setAttribute('height', h); cl.setAttribute('xmlns', NS);
      var img = new Image();
      img.onload = function () { ok(img); }; img.onerror = function () { ok(null); };
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(new XMLSerializer().serializeToString(cl));
    });
  }
  function wrapText(ctx, text, x, y, maxW, lh) {
    var words = String(text).split(/(\s+)/), line = '';
    if (!/\s/.test(text)) words = Array.from(String(text));
    for (var i = 0; i < words.length; i++) {
      var test = line + words[i];
      if (ctx.measureText(test).width > maxW && line.trim()) { ctx.fillText(line.trim(), x, y); y += lh; line = words[i].trim() ? words[i] : ''; }
      else line = test;
    }
    if (line.trim()) { ctx.fillText(line.trim(), x, y); y += lh; }
    return y;
  }
  function exportPng(W, H, name) {
    var cv = document.createElement('canvas'); cv.width = W; cv.height = H; var ctx = cv.getContext('2d');
    var F = 'system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans","Noto Sans CJK KR","Noto Sans CJK JP",sans-serif', P = 56;
    ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
    ctx.strokeStyle = 'rgba(217,183,101,.45)'; ctx.lineWidth = 3; ctx.strokeRect(24, 24, W - 48, H - 48);
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = C.gold; ctx.font = '700 46px ' + F; ctx.fillText(t('fit.card.title'), P, 104);
    var L = last || {}, a = L.a; var y = 160;
    if (a) { ctx.fillStyle = C.ink; ctx.font = '600 32px ' + F; y = wrapText(ctx, a.name + (L.v && L.v.label ? ' · ' + L.v.label : '') + (L.v ? ' — ' + dimText(L.v) : ''), P, y, W - 2 * P, 42); }
    var c = L.c || carrier();
    var verdict, vcol = C.ink, sub = '';
    if (L.kind === 'dims') { var ok = !L.res.over.length; verdict = ok ? t('fit.v.ok') : t('fit.v.ko'); vcol = ok ? '#7dcea0' : C.over; sub = ok ? '' : (L.res.over.length === 1 ? t('fit.v.over1') : t('fit.v.overN', { n: L.res.over.length })); }
    else if (L.kind === 'nocabin') { verdict = t('fit.v.nocabin'); vcol = C.over; sub = a && a.cargo_or_checked_allowed ? t('fit.v.nocabin.hold') : ''; }
    else if (L.kind === 'check') { verdict = t('fit.v.check'); vcol = C.gold; sub = t('fit.v.check.why'); }
    else verdict = t('fit.v.enter');
    ctx.fillStyle = vcol; ctx.font = '700 44px ' + F; y = wrapText(ctx, verdict, P, y + 18, W - 2 * P, 54);
    if (sub) { ctx.font = '600 28px ' + F; y = wrapText(ctx, sub, P, y + 2, W - 2 * P, 36); }
    if (L.kind === 'dims') { ctx.fillStyle = C.mut; ctx.font = '26px ' + F; y = wrapText(ctx, t('fit.carrier') + ': ' + fmt(c.L) + ' × ' + fmt(c.W) + ' × ' + fmt(c.H) + ' ' + c.unit + ' · ' + (c.soft ? t('fit.soft') : t('fit.hard')), P, y + 6, W - 2 * P, 34); }
    function finish() {
      // legend + footer
      var fy = H - 100;
      if (L.kind === 'dims') {
        var lx = P, ly = fy - 56; ctx.font = '24px ' + F;
        [[C.gold, t('fit.leg.limit'), 'dash'], [C.teal, t('fit.leg.carrier'), 'fill'], [C.over, t('fit.leg.over'), 'line']].forEach(function (it) {
          ctx.save(); ctx.lineWidth = 3; ctx.strokeStyle = it[0];
          if (it[2] === 'dash') { ctx.setLineDash([8, 5]); ctx.strokeRect(lx, ly - 18, 34, 20); }
          else if (it[2] === 'fill') { ctx.fillStyle = C.tealFill; ctx.fillRect(lx, ly - 18, 34, 20); ctx.strokeRect(lx, ly - 18, 34, 20); }
          else { ctx.fillStyle = C.overFill; ctx.fillRect(lx, ly - 18, 34, 20); ctx.strokeRect(lx, ly - 18, 34, 20); }
          ctx.restore(); ctx.fillStyle = C.ink; ctx.fillText(it[1], lx + 46, ly); lx += 46 + ctx.measureText(it[1]).width + 34;
        });
      }
      ctx.fillStyle = C.mut; ctx.font = '22px ' + F;
      ctx.fillText((a && a.last_verified ? t('fit.checked', { d: a.last_verified }) + ' · ' : '') + 'petpolicycheck.com/fit', P, fy);
      ctx.font = '20px ' + F; wrapText(ctx, t('fit.disclaimer'), P, fy + 30, W - 2 * P, 24);
      var link = document.createElement('a'); link.download = name; link.href = cv.toDataURL('image/png');
      document.body.appendChild(link); link.click(); link.remove();
    }
    if (L.kind !== 'dims') {
      ctx.fillStyle = C.mut; ctx.font = '26px ' + F;
      if (a) { var txt = L.kind === 'nocabin' ? (a.cargo_fee_note || (a.underseat_soft_dims_in_cm || []).join(' · ')) : (a.underseat_soft_dims_in_cm || []).join(' · '); if (txt) wrapText(ctx, txt, P, y + 30, W - 2 * P, 36); }
      finish(); return;
    }
    var fr = $('svgFront'), sd = $('svgSide'), area = { x: P, y: y + 24, w: W - 2 * P, h: (H - 196) - (y + 24) };
    var stacked = H / W > 1.3, vw, vh;
    if (stacked) { vh = Math.min(area.w * 262 / 360, (area.h - 76) / 2); vw = vh * 360 / 262; }
    else { vw = (area.w - 24) / 2; vh = vw * 262 / 360; if (vh > area.h - 30) { vh = area.h - 30; vw = vh * 360 / 262; } }
    Promise.all([svgImage(fr, 720, 524), svgImage(sd, 720, 524)]).then(function (im) {
      ctx.font = '600 24px ' + F; ctx.fillStyle = '#c9c2b4';
      var pos = stacked ? [[area.x + (area.w - vw) / 2, area.y + 30], [area.x + (area.w - vw) / 2, area.y + 30 + vh + 46]]
                        : [[area.x, area.y + 30], [area.x + vw + 24, area.y + 30]];
      [t('fit.front'), t('fit.side')].forEach(function (cap, i) {
        ctx.fillStyle = '#c9c2b4'; ctx.fillText(cap, pos[i][0], pos[i][1] - 10);
        if (im[i]) ctx.drawImage(im[i], pos[i][0], pos[i][1], vw, vh);
        ctx.strokeStyle = 'rgba(217,183,101,.25)'; ctx.lineWidth = 2; ctx.strokeRect(pos[i][0], pos[i][1], vw, vh);
      });
      // dimension table in the remaining space (limit / yours / difference)
      var ty = (stacked ? pos[1][1] : pos[0][1]) + vh + 56, r = L.res, u = r.unit, rows = 4, rh = 40;
      if ((H - 196) - ty >= rows * rh) {
        var cols = [P, P + 300, P + 520, P + 740];
        ctx.font = '600 24px ' + F; ctx.fillStyle = '#c9c2b4';
        [t('fit.r.dim'), t('fit.r.limit') + ' (' + u + ')', t('fit.r.yours') + ' (' + u + ')', t('fit.r.delta')].forEach(function (h, i) { ctx.fillText(h, cols[i], ty); });
        ['L', 'W', 'H'].forEach(function (x, j) {
          var yy = ty + (j + 1) * rh, over = r.delta[x] > 0;
          ctx.font = '26px ' + F; ctx.fillStyle = C.ink;
          ctx.fillText(t('fit.dim' + x), cols[0], yy); ctx.fillText(fmt(r.lim[x]), cols[1], yy); ctx.fillText(fmt(r.car[x]), cols[2], yy);
          ctx.font = (over ? '700 ' : '') + '26px ' + F; ctx.fillStyle = over ? C.over : '#7dcea0';
          ctx.fillText(over ? '+' + fmt(r.delta[x]) + ' ' + u : '✓', cols[3], yy);
        });
      } else if ((H - 196) - ty >= 10) {
        // compact one-line summary: "Length 46 → 50 +4 cm"
        var cw = (W - 2 * P) / 3;
        ['L', 'W', 'H'].forEach(function (x, j) {
          var over = r.delta[x] > 0, cx = P + j * cw;
          ctx.font = '600 22px ' + F; ctx.fillStyle = '#c9c2b4'; ctx.fillText(t('fit.dim' + x), cx, ty);
          ctx.font = (over ? '700 ' : '') + '26px ' + F; ctx.fillStyle = over ? C.over : '#7dcea0';
          ctx.fillText(fmt(r.lim[x]) + ' → ' + fmt(r.car[x]) + ' ' + u + '  ' + (over ? '+' + fmt(r.delta[x]) : '✓'), cx, ty + 34);
        });
      }
      finish();
    });
  }

  /* ---------- wiring ---------- */
  function setAirline(id) { st.a = AIR.filter(function (a) { return a.id === id; })[0] || AIR[0] || null; st.v = null; st.auto = true; }
  function init() {
    var q = new URLSearchParams(location.search);
    if (q.get('L')) $('fL').value = q.get('L');
    if (q.get('W')) $('fW').value = q.get('W');
    if (q.get('H')) $('fH').value = q.get('H');
    if (q.get('u') === 'in' || q.get('u') === 'cm') $('fU').value = q.get('u');
    if (q.get('soft') === '0') $('fSoft').checked = false;
    var want = q.get('airline') || 'delta';
    if (!AIR.some(function (a) { return a.id === want; })) want = 'delta';
    $('fAir').value = ''; st.a = null;
    setAirline(want); buildSelect(); $('fAir').value = st.a ? st.a.id : '';
    if (q.get('size') != null && q.get('size') !== 'auto') {
      var vs = variantsOf(st.a), hit = vs.filter(function (v) { return String(v.i) === q.get('size'); })[0];
      if (hit) { st.v = hit; st.auto = false; }
    }
    render(false);
    $('fQ').addEventListener('input', function () { var id = buildSelect(); if (id && (!st.a || id !== st.a.id)) { setAirline(id); } render(true); });
    $('fAir').addEventListener('change', function () { setAirline($('fAir').value); render(true); });
    $('fVar').addEventListener('change', function () {
      var val = $('fVar').value;
      if (val === 'auto') { st.auto = true; st.v = null; } else { st.auto = false; st.v = st.vars.filter(function (v) { return String(v.i) === val; })[0] || null; }
      render(true);
    });
    ['fL', 'fW', 'fH'].forEach(function (id) { $(id).addEventListener('input', function () { render(true); }); });
    $('fU').addEventListener('change', function () {
      var k = $('fU').value === 'in' ? 1 / 2.54 : 2.54;
      ['fL', 'fW', 'fH'].forEach(function (id) { var v = parseFloat($(id).value); if (v > 0) $(id).value = fmt(v * k); });
      render(true);
    });
    $('fSoft').addEventListener('change', function () { if (st.auto) st.v = null; render(true); });
    $('fGo').addEventListener('click', function () { render(true); });
    $('png916').addEventListener('click', function () { exportPng(1080, 1920, 'ppc-fit-story-9x16.png'); });
    $('png11').addEventListener('click', function () { exportPng(1080, 1080, 'ppc-fit-post-1x1.png'); });
    window.addEventListener('ppc:lang', function () { buildSelect(); render(false); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
  window.PPC_FIT = { variantsOf: variantsOf, compare: compare };
})();
