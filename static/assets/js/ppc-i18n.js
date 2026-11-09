/* PetPolicyCheck · Tier-1 hybrid i18n (EN|FR|ES|DE|KO|JA). Initials only — zero flags.
   Persists ppc_lang + ?lang=. Single global switcher; syncs page-local switchers. */
(function () {
  'use strict';
  var LANGS = ['en', 'es', 'fr', 'ko', 'ja', 'de'];
  var LANG_LABELS = {en:'EN', es:'ES', fr:'FR', ko:'KR', ja:'JP', de:'DE'};
  var KEY = 'ppc_lang';
  var D = (window.PPC_I18N && window.PPC_I18N.strings) || {};
  var L = 'en';

  function ppcPathLocale() {
    try {
      var p = location.pathname || '/';
      if (p === '/es' || p.indexOf('/es/') === 0) return 'es';
      /* future: /fr/ /de/ /ko/ /ja/ */
      var m = p.match(/^\/(fr|de|ko|ja)(?=\/|$)/);
      if (m) return m[1];
    } catch (e) {}
    return null;
  }
  function detect() {
    var pathLang = ppcPathLocale();
    if (pathLang) return pathLang;
    try {
      var q = new URLSearchParams(location.search).get('lang');
      if (q) { q = q.toLowerCase().slice(0, 2); if (LANGS.indexOf(q) >= 0) return q; }
    } catch (e) {}
    try {
      var s = localStorage.getItem(KEY);
      if (s && LANGS.indexOf(s) >= 0) return s;
    } catch (e) {}
    try {
      var n = (navigator.language || 'en').slice(0, 2).toLowerCase();
      if (LANGS.indexOf(n) >= 0) return n;
    } catch (e) {}
    return 'en';
  }

  function t(key, lang) {
    lang = lang || L;
    var pack = D[lang] || D.en || {};
    if (pack[key] != null) return pack[key];
    if (D.en && D.en[key] != null) return D.en[key];
    return null;
  }

  function setLang(lang, pushUrl) {
    if (LANGS.indexOf(lang) < 0) lang = 'en';
    var prevPathLang = ppcPathLocale();
    L = lang;
    try { localStorage.setItem(KEY, L); } catch (e) {}
    try {
      if (pushUrl !== false) {
        var path = location.pathname || '/';
        var search = location.search || '';
        var hash = location.hash || '';
        /* Dedicated /es/ tree (P0): switching EN↔ES navigates between trees.
           Other langs keep hybrid ?lang= on the current tree. */
        if (lang === 'es' && prevPathLang !== 'es') {
          /* From EN home → /es/ (preserve ?view=map); from other EN pages → /es/ counterpart if known, else /es/ */
          var dest = '/es/';
          if (path === '/' || path === '/index.html') {
            dest = '/es/' + search + hash;
            if (search.indexOf('view=') < 0 && (hash === '#map' || hash === '#world-map')) dest = '/es/?view=map';
          } else {
            dest = '/es' + path + search + hash;
          }
          location.assign(dest);
          return;
        }
        if (lang === 'en' && prevPathLang === 'es') {
          var enPath = path.replace(/^\/es(?=\/|$)/, '') || '/';
          if (enPath === '') enPath = '/';
          location.assign(enPath + search + hash);
          return;
        }
        var u = new URL(location.href);
        if (L === 'en') u.searchParams.delete('lang');
        else u.searchParams.set('lang', L);
        history.replaceState(null, '', u.pathname + u.search + u.hash);
      }
    } catch (e) {}
    document.documentElement.setAttribute('lang', L === 'en' ? 'en-US' : L);
    document.documentElement.setAttribute('data-ppc-lang', L);
    /* On /es/ dedicated pages, baked usted HTML wins — still apply for chrome pastilles inject */
    apply();
    syncLocalSwitchers();
    try { window.dispatchEvent(new CustomEvent('ppc:lang', { detail: { lang: L } })); } catch (e) {}
  }

  function applyEl(el) {
    var key = el.getAttribute('data-i18n');
    if (!key) return;
    var v = t(key);
    if (v == null) return;
    if (el.hasAttribute('data-i18n-html')) { el.innerHTML = v; return; }
    /* Prefer .lbl inside pastille nav links so SVG icons stay intact */
    var lbl = el.querySelector && el.querySelector(':scope > .lbl, :scope > span.lbl, :scope > span:not(.pst)');
    if (lbl && el.classList && (el.classList.contains('sec') || el.classList.contains('sec-eyebrow') || el.classList.contains('msw-tab'))) {
      lbl.textContent = v; return;
    }
    if (el.children && el.children.length && el.querySelector('.pst, svg, i')) {
      var sp = el.querySelector('span:not(.pst)');
      if (sp) { sp.textContent = v; return; }
    }
    el.textContent = v;
  }

  function apply() {
    document.querySelectorAll('[data-i18n]').forEach(applyEl);
    document.querySelectorAll('[data-i18n-ph]').forEach(function (el) {
      var v = t(el.getAttribute('data-i18n-ph'));
      if (v != null) el.setAttribute('placeholder', v);
    });
    document.querySelectorAll('[data-i18n-aria]').forEach(function (el) {
      var v = t(el.getAttribute('data-i18n-aria'));
      if (v != null) el.setAttribute('aria-label', v);
    });
    /* Pastilles nav labels */
    document.querySelectorAll('#site-menu a.sec[data-i18n-nav], #site-menu a[data-i18n]').forEach(applyEl);
    document.querySelectorAll('.sec-eyebrow [data-i18n], .sec-eyebrow span[data-i18n]').forEach(applyEl);
    /* Menu button */
    var mb = document.querySelector('.menu-btn span');
    if (mb) { var mv = t('site.nav.menu'); if (mv) mb.textContent = mv; }
    /* Partner banner */
    document.querySelectorAll('.partner-label').forEach(function (el) {
      var v = t('site.partner.label'); if (v) el.textContent = v;
    });
    document.querySelectorAll('.partner-ph b').forEach(function (el) {
      /* keep structure: first line bold brand phrase from partner.ph split */
    });
    document.querySelectorAll('.partner-ph p').forEach(function (el) {
      var v = t('site.partner.ph'); if (v) el.innerHTML = '<b>' + v.split(' · ')[0] + '</b> · ' + v.split(' · ').slice(1).join(' · ');
    });
    document.querySelectorAll('.partner-cta').forEach(function (el) {
      var v = t('site.partner.cta'); if (v) el.innerHTML = v.replace('→', '<span aria-hidden="true">→</span>');
    });
    /* Map switcher */
    var mapKeys = {
      'world-back': 'map.switch.world',
      'accent-usa': 'map.switch.usa',
      'accent-maple': 'map.switch.canada',
      'accent-mxgreen': 'map.switch.mexico'
    };
    document.querySelectorAll('#map-switch a.msw-tab').forEach(function (a) {
      var key = null;
      if (a.classList.contains('world-back')) key = 'map.switch.world';
      else if (a.classList.contains('accent-usa')) key = 'map.switch.usa';
      else if (a.classList.contains('accent-maple')) key = 'map.switch.canada';
      else if (a.classList.contains('accent-mxgreen')) key = 'map.switch.mexico';
      if (!key) return;
      var v = t(key); if (!v) return;
      var span = a.querySelector('span'); if (span) span.textContent = v; else a.textContent = v;
    });
    /* Footer copyright disc — translate the copyright sentence while keeping affiliate + Terms */
    document.querySelectorAll('footer .disc').forEach(function (p) {
      var copy = t('site.foot.copyright');
      var aff = t('site.foot.aff');
      var terms = t('site.foot.terms') || 'Terms';
      if (!copy) return;
      var termsHref = (p.querySelector('a[href*="terms"]') || {}).getAttribute?.('href') || 'terms.html';
      var affHtml = aff ? '<span data-i18n="site.foot.aff">' + aff + '</span> ' : '';
      p.innerHTML = affHtml + copy + ' See <a href="' + termsHref + '" data-i18n="site.foot.terms">' + terms + '</a>.';
    });
    /* Global switcher pressed state */
    document.querySelectorAll('.ppc-lang-sw [data-setlang]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(b.getAttribute('data-setlang') === L));
    });
    paintRefNotice();
  }

  function isLongForm() {
    var p = location.pathname || '';
    return /\/(products|hotels|airlines)\/[^/]+\.html$/.test(p)
      || /\/countries\/(usa|canada|mexico|uk|germany|france|dominican)\.html$/.test(p)
      || /\/(privacy|terms|refund-policy|about|contact)\.html$/.test(p)
      || /\/routes\/[^/]+\.html$/.test(p)
      || /\/insurance\//.test(p)
      || /\/clinics\//.test(p);
  }

  function paintRefNotice() {
    var existing = document.getElementById('ppc-ref-notice');
    if (L === 'en' || !isLongForm()) {
      if (existing) existing.remove();
      return;
    }
    var msg = t('site.refnotice');
    var links = t('site.refnotice.links') || '';
    if (!msg) return;
    var root = '/';
    try {
      var segs = (location.pathname || '/').replace(/\/+$/, '').split('/').filter(Boolean);
      if (segs.length && /\.[a-z0-9]+$/i.test(segs[segs.length - 1])) segs = segs.slice(0, -1);
      root = segs.length ? '../'.repeat(segs.length) : '';
    } catch (e) {}
    var html = '<aside id="ppc-ref-notice" class="ppc-ref-notice" role="status">'
      + '<span class="ppc-ref-msg">' + msg + '</span>'
      + '<span class="ppc-ref-links">'
      + '<a href="' + root + 'airlines/compare/">' + (links.split(' · ')[0] || 'Comparator') + '</a>'
      + ' · <a href="' + root + 'passport/">' + (links.split(' · ')[1] || 'Passport') + '</a>'
      + ' · <a href="' + root + '?view=map">' + (links.split(' · ')[2] || 'Maps') + '</a>'
      + '</span></aside>';
    if (existing) { existing.outerHTML = html; return; }
    var main = document.querySelector('main, #main, article') || document.body;
    main.insertAdjacentHTML('afterbegin', html);
  }

  function switcherHTML() {
    var aria = t('lang.aria') || 'Language';
    return '<div class="ppc-lang-sw" role="group" aria-label="' + aria + '">'
      + LANGS.map(function (c) {
        return '<button type="button" data-setlang="' + c + '" lang="' + c + '" aria-pressed="' + (c === L ? 'true' : 'false') + '">' + (LANG_LABELS[c] || c.toUpperCase()) + '</button>';
      }).join('')
      + '</div>';
  }

  function ensureSwitcher() {
    var html = switcherHTML();
    var introLocked = document.documentElement.classList.contains('intro-lock');
    var onHomeIntro = introLocked && !!document.querySelector('section.intro');

    /* Marc 2026-11-07: visible language switcher ONLY on Page 1 intro.
       All other pages keep ui.js + apply() via localStorage — zero switcher UI. */
    function stripAllSwitchers() {
      document.querySelectorAll('.ppc-lang-sw, .ppc-lang-bar, .ppc-lang-fixed, .ppc-lang-intro-wrap, .flang').forEach(function (el) { el.remove(); });
      document.querySelectorAll('.lang-sw, .langsw').forEach(function (sw) {
        if (sw.classList.contains('ppc-lang-sw')) return;
        /* Keep billing switchers; hide language UIs only */
        if (sw.classList.contains('bill-sw')) return;
        sw.setAttribute('hidden', '');
        sw.style.display = 'none';
        sw.setAttribute('aria-hidden', 'true');
      });
    }

    if (!onHomeIntro) {
      stripAllSwitchers();
      return;
    }

    /* Page 1 only: mount stable bar below brandbar */
    document.querySelectorAll('header.top .ppc-lang-sw, header.map-nav .ppc-lang-sw, .ppc-lang-fixed').forEach(function (el) { el.remove(); });
    var brandbar = document.querySelector('section.intro header.brandbar, section.intro .brandbar');
    var existing = document.querySelector('.ppc-lang-bar-intro');
    if (existing) {
      var sw = existing.querySelector('.ppc-lang-sw');
      if (sw) sw.outerHTML = html.replace('class="ppc-lang-sw"', 'class="ppc-lang-sw ppc-lang-intro"');
      else existing.innerHTML = '<div class="wrap">' + html.replace('class="ppc-lang-sw"', 'class="ppc-lang-sw ppc-lang-intro"') + '</div>';
    } else if (brandbar) {
      var bar = document.createElement('div');
      bar.className = 'ppc-lang-bar ppc-lang-bar-intro';
      bar.innerHTML = '<div class="wrap">' + html.replace('class="ppc-lang-sw"', 'class="ppc-lang-sw ppc-lang-intro"') + '</div>';
      brandbar.insertAdjacentElement('afterend', bar);
    } else {
      var intro = document.querySelector('section.intro .wrap, section.intro');
      if (intro) {
        var bar2 = document.createElement('div');
        bar2.className = 'ppc-lang-bar ppc-lang-bar-intro';
        bar2.innerHTML = '<div class="wrap">' + html.replace('class="ppc-lang-sw"', 'class="ppc-lang-sw ppc-lang-intro"') + '</div>';
        intro.insertAdjacentElement('afterbegin', bar2);
      }
    }
    document.querySelectorAll('.ppc-lang-intro-wrap').forEach(function (el) { el.remove(); });
    /* Hide any non-intro page-local switchers that might still be in DOM */
    document.querySelectorAll('.lang-sw, .langsw').forEach(function (sw) {
      if (sw.closest && sw.closest('section.intro')) return;
      if (sw.classList.contains('bill-sw')) return;
      sw.setAttribute('hidden', '');
      sw.style.display = 'none';
    });
  }

  function syncLocalSwitchers() {
    /* Hide all non-intro language UIs (Marc: switcher only on Page 1) */
    if (!document.documentElement.classList.contains('intro-lock')) {
      document.querySelectorAll('.ppc-lang-sw, .ppc-lang-bar, .ppc-lang-fixed, .ppc-lang-intro-wrap, .flang').forEach(function (el) { el.remove(); });
      document.querySelectorAll('.lang-sw, .langsw').forEach(function (sw) {
        if (sw.classList.contains('bill-sw')) return;
        sw.setAttribute('hidden', '');
        sw.style.display = 'none';
      });
    }
    /* pro/ uses data-lang; field-guides uses data-lang; forum uses data-setlang */
    document.querySelectorAll('.lang-sw [data-lang], .langsw [data-lang], [data-lang]').forEach(function (b) {
      if (b.closest && b.closest('.ppc-lang-sw')) return;
      var c = b.getAttribute('data-lang');
      if (!c) return;
      if (b.getAttribute('aria-pressed') != null) b.setAttribute('aria-pressed', String(c === L));
      if (b.parentElement && (b.parentElement.classList.contains('langsw') || b.parentElement.classList.contains('lang-sw'))) {
        b.style.background = c === L ? '' : '';
        b.setAttribute('aria-pressed', String(c === L));
      }
    });
    /* Hide duplicate page-local switchers when global exists — keep them but sync clicks */
    document.querySelectorAll('.lang-sw, .langsw').forEach(function (sw) {
      if (sw.classList.contains('ppc-lang-sw')) return;
      sw.setAttribute('data-ppc-synced', '1');
      /* Ensure KO/JA buttons exist */
      LANGS.forEach(function (c) {
        if (!sw.querySelector('[data-lang="' + c + '"]')) {
          var b = document.createElement('button');
          b.type = 'button';
          b.setAttribute('data-lang', c);
          b.textContent = c.toUpperCase();
          b.setAttribute('aria-pressed', c === L ? 'true' : 'false');
          sw.appendChild(b);
        }
      });
      sw.querySelectorAll('[data-lang]').forEach(function (b) {
        b.setAttribute('aria-pressed', String(b.getAttribute('data-lang') === L));
      });
    });
  }

  function onClick(ev) {
    var b = ev.target && ev.target.closest && (ev.target.closest('.ppc-lang-sw [data-setlang]') || ev.target.closest('.lang-sw [data-lang]') || ev.target.closest('.langsw [data-lang]') || ev.target.closest('[data-setlang]'));
    if (!b) return;
    var lang = b.getAttribute('data-setlang') || b.getAttribute('data-lang');
    if (!lang || LANGS.indexOf(lang) < 0) return;
    ev.preventDefault();
    setLang(lang);
    /* Notify page-local engines */
    if (window.PPC_PRO_SETLANG) try { window.PPC_PRO_SETLANG(lang); } catch (e) {}
  }

  function boot() {
    L = detect();
    ensureSwitcher();
    setLang(L, false);
    document.addEventListener('click', onClick, true);
    /* Re-apply after pastilles rewrites nav */
    setTimeout(function () { ensureSwitcher(); apply(); syncLocalSwitchers(); }, 0);
    setTimeout(function () { apply(); }, 50);
  }

  window.PPC_LANG = {
    get: function () { return L; },
    set: setLang,
    t: t,
    langs: LANGS.slice()
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
