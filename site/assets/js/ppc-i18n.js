/* PetPolicyCheck · Tier-1 hybrid i18n (EN|FR|ES|IT|DE|KO|JA). Initials only — zero flags.
   Persists ppc_lang + ?lang=. Single global switcher; syncs page-local switchers. */
(function () {
  'use strict';
  var LANGS = ['en', 'es', 'it', 'fr', 'ko', 'ja', 'de'];
  var LANG_LABELS = {en:'EN', es:'ES', it:'IT', fr:'FR', ko:'KR', ja:'JP', de:'DE'};
  var KEY = 'ppc_lang';
  var D = (window.PPC_I18N && window.PPC_I18N.strings) || {};
  var L = 'en';

  function ppcPathLocale() {
    try {
      var p = location.pathname || '/';
      var m = p.match(/^\/(es|it|fr|de|ko|ja)(?=\/|$)/);
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
        /* Dedicated locale trees (/es/, /it/): switching navigates between trees.
           Other langs keep hybrid ?lang= on the current tree. */
        var TREE_LANGS = ['es', 'it'];
        var IT_OK = {"/":1,"/about.html":1,"/advertise/":1,"/advertise/index.html":1,"/airlines/":1,"/airlines/aeromexico.html":1,"/airlines/air-canada.html":1,"/airlines/air-france.html":1,"/airlines/air-premia.html":1,"/airlines/alaska.html":1,"/airlines/american.html":1,"/airlines/ana.html":1,"/airlines/asiana.html":1,"/airlines/british-airways.html":1,"/airlines/compare/":1,"/airlines/compare/index.html":1,"/airlines/delta.html":1,"/airlines/frontier.html":1,"/airlines/hawaiian.html":1,"/airlines/index.html":1,"/airlines/jal.html":1,"/airlines/jeju-air.html":1,"/airlines/jetblue.html":1,"/airlines/korean-air.html":1,"/airlines/lufthansa.html":1,"/airlines/peach.html":1,"/airlines/porter.html":1,"/airlines/snub-nosed-breeds.html":1,"/airlines/southwest.html":1,"/airlines/spirit.html":1,"/airlines/tway.html":1,"/airlines/united.html":1,"/airlines/viva-aerobus.html":1,"/airlines/volaris.html":1,"/airlines/westjet.html":1,"/airlines/zipair.html":1,"/book/":1,"/book/index.html":1,"/clinics/usa.html":1,"/contact.html":1,"/countries/canada-map.html":1,"/countries/canada.html":1,"/countries/france-map.html":1,"/countries/france.html":1,"/countries/germany-map.html":1,"/countries/germany.html":1,"/countries/italy-map.html":1,"/countries/italy.html":1,"/countries/spain-map.html":1,"/countries/uk-map.html":1,"/countries/uk.html":1,"/countries/usa-map.html":1,"/countries/usa.html":1,"/fit/":1,"/fit/index.html":1,"/flight-volunteer/":1,"/flight-volunteer/index.html":1,"/forum/":1,"/forum/account.html":1,"/forum/admin.html":1,"/forum/guidelines.html":1,"/forum/index.html":1,"/forum/new.html":1,"/forum/partners.html":1,"/forum/pet-travel-stories/":1,"/forum/pet-travel-stories/index.html":1,"/forum/post.html":1,"/grooming/":1,"/grooming/index.html":1,"/hotel-pets/":1,"/hotel-pets/index.html":1,"/hotels/":1,"/hotels/index.html":1,"/hotels/pet-friendly-hotels-atlanta.html":1,"/hotels/pet-friendly-hotels-austin.html":1,"/hotels/pet-friendly-hotels-boston.html":1,"/hotels/pet-friendly-hotels-chicago.html":1,"/hotels/pet-friendly-hotels-denver.html":1,"/hotels/pet-friendly-hotels-detroit.html":1,"/hotels/pet-friendly-hotels-houston.html":1,"/hotels/pet-friendly-hotels-los-angeles.html":1,"/hotels/pet-friendly-hotels-miami.html":1,"/hotels/pet-friendly-hotels-new-york.html":1,"/hotels/pet-friendly-hotels-orlando.html":1,"/hotels/pet-friendly-hotels-san-francisco.html":1,"/hotels/pet-friendly-hotels-seattle.html":1,"/index.html":1,"/insurance/pet-insurance-for-travelers.html":1,"/military-pcs/":1,"/military-pcs/index.html":1,"/partner-vets/":1,"/partner-vets/index.html":1,"/passport/":1,"/passport/index.html":1,"/pet-travel-checklist/":1,"/pet-travel-checklist/index.html":1,"/privacy.html":1,"/pro/":1,"/pro/index.html":1,"/products/":1,"/products/best-airline-approved-soft-carriers.html":1,"/products/cat-travel-checklist.html":1,"/products/chuckit-travel-pillow-bed.html":1,"/products/dog-road-trip-packing-list.html":1,"/products/feliway-classic-spray.html":1,"/products/iata-hard-crates-for-cargo.html":1,"/products/index.html":1,"/products/kurgo-collaps-a-bowl.html":1,"/products/kurgo-direct-to-seatbelt-tether.html":1,"/products/kurgo-enhanced-strength-tru-fit-harness.html":1,"/products/kurgo-gourd-water-bottle.html":1,"/products/kurgo-loft-dog-jacket.html":1,"/products/kurgo-loft-wander-bed.html":1,"/products/kurgo-rover-bench-seat-cover.html":1,"/products/kurgo-skybox-booster.html":1,"/products/kurgo-surf-n-turf-life-jacket.html":1,"/products/pet-carrier-backpacks-for-flying.html":1,"/products/pet-evac-pak-collapsible-litter-box.html":1,"/products/petmate-kennel-airline-travel-kit.html":1,"/products/petmate-sky-kennel.html":1,"/products/petmate-ultra-vari-kennel.html":1,"/products/ruffwear-dirtbag-seat-cover.html":1,"/products/ruffwear-float-coat.html":1,"/products/ruffwear-front-range-harness.html":1,"/products/ruffwear-front-range-leash.html":1,"/products/ruffwear-grip-trex-boots.html":1,"/products/ruffwear-highlands-pad.html":1,"/products/ruffwear-load-up-harness.html":1,"/products/ruffwear-quencher.html":1,"/products/ruffwear-swamp-cooler-vest.html":1,"/products/sherpa-elevation-backpack.html":1,"/products/sherpa-original-deluxe.html":1,"/products/sleepypod-air.html":1,"/products/sleepypod-atom.html":1,"/products/sleepypod-clickit-range.html":1,"/products/sleepypod-go-bag.html":1,"/products/sleepypod-mini.html":1,"/products/sleepypod-safety-tether.html":1,"/products/sleepypod-yummy-travel-bowls.html":1,"/products/sturdibag-pro.html":1,"/products/thunderease-dog-calming-spray.html":1,"/products/thundershirt-for-cats.html":1,"/products/thundershirt-for-dogs.html":1,"/products/tractive-gps-cat.html":1,"/products/tractive-gps-dog-6.html":1,"/products/travel-cat-porta-pawty.html":1,"/products/travel-water-bowls.html":1,"/products/under-seat-carrier-size-by-airline.html":1,"/products/wee-wee-cat-pads.html":1,"/products/wee-wee-superior-performance-pads.html":1,"/refund-policy.html":1,"/routes/":1,"/routes/canada-to-usa-air-canada.html":1,"/routes/canada-to-usa-alaska.html":1,"/routes/canada-to-usa-american.html":1,"/routes/canada-to-usa-delta.html":1,"/routes/canada-to-usa-united.html":1,"/routes/france-to-usa-air-france.html":1,"/routes/france-to-usa-delta.html":1,"/routes/france-to-usa-united.html":1,"/routes/index.html":1,"/routes/japan-to-usa-american.html":1,"/routes/japan-to-usa-delta.html":1,"/routes/japan-to-usa-united.html":1,"/routes/mexico-to-usa-alaska.html":1,"/routes/mexico-to-usa-american.html":1,"/routes/mexico-to-usa-delta.html":1,"/routes/mexico-to-usa-united.html":1,"/routes/south-korea-to-usa-delta.html":1,"/routes/south-korea-to-usa-korean-air.html":1,"/routes/south-korea-to-usa-united.html":1,"/routes/uk-to-france-air-france.html":1,"/routes/uk-to-france-british-airways.html":1,"/routes/usa-canada.html":1,"/routes/usa-france.html":1,"/routes/usa-mexico.html":1,"/routes/usa-to-canada-air-canada.html":1,"/routes/usa-to-canada-alaska.html":1,"/routes/usa-to-canada-american.html":1,"/routes/usa-to-canada-delta.html":1,"/routes/usa-to-canada-united.html":1,"/routes/usa-to-france-air-france.html":1,"/routes/usa-to-france-american.html":1,"/routes/usa-to-france-delta.html":1,"/routes/usa-to-france-united.html":1,"/routes/usa-to-germany-delta.html":1,"/routes/usa-to-germany-lufthansa.html":1,"/routes/usa-to-germany-united.html":1,"/routes/usa-to-japan-american.html":1,"/routes/usa-to-japan-delta.html":1,"/routes/usa-to-japan-korean-air.html":1,"/routes/usa-to-japan-united.html":1,"/routes/usa-to-japan.html":1,"/routes/usa-to-mexico-alaska.html":1,"/routes/usa-to-mexico-american.html":1,"/routes/usa-to-mexico-delta.html":1,"/routes/usa-to-mexico-united.html":1,"/routes/usa-to-south-korea-delta.html":1,"/routes/usa-to-south-korea-korean-air.html":1,"/routes/usa-to-south-korea-united.html":1,"/routes/usa-to-south-korea.html":1,"/routes/usa-uk.html":1,"/taxi/":1,"/taxi/index.html":1,"/terms.html":1,"/titer-calculator/":1,"/titer-calculator/index.html":1,"/updates.html":1,"/vet-info/":1,"/vet-info/index.html":1,"/vet-prep/":1,"/vet-prep/checklist.html":1,"/vet-prep/index.html":1,"/widgets/":1,"/widgets/index.html":1,"/airport/":1,"/airport/index.html":1,"/b2b-pet-desk/":1,"/b2b-pet-desk/index.html":1,"/countries/japan-map.html":1,"/countries/mexico-map.html":1,"/countries/mexico.html":1,"/countries/south-korea-map.html":1,"/countries/spain.html":1,"/extension/":1,"/extension/index.html":1,"/field-guides/":1,"/field-guides/index.html":1,"/field-guides/advertise.html":1,"/k9/":1,"/k9/index.html":1,"/veterans/":1,"/veterans/index.html":1,"/airport/ATL/":1,"/airport/AUS/":1,"/airport/BNA/":1,"/airport/BTV/":1,"/airport/DEN/":1,"/airport/DFW/":1,"/airport/DTW/":1,"/airport/EWR/":1,"/airport/HND/":1,"/airport/IAH/":1,"/airport/ICN/":1,"/airport/JFK/":1,"/airport/KIX/":1,"/airport/LAX/":1,"/airport/MCO/":1,"/airport/MIA/":1,"/airport/NRT/":1,"/airport/ORD/":1,"/airport/PDX/":1,"/airport/SAN/":1,"/airport/SEA/":1,"/airport/SFO/":1,"/airport/YUL/":1,"/airport/YVR/":1,"/airport/ATL/index.html":1,"/airport/AUS/index.html":1,"/airport/BNA/index.html":1,"/airport/BTV/index.html":1,"/airport/DEN/index.html":1,"/airport/DFW/index.html":1,"/airport/DTW/index.html":1,"/airport/EWR/index.html":1,"/airport/HND/index.html":1,"/airport/IAH/index.html":1,"/airport/ICN/index.html":1,"/airport/JFK/index.html":1,"/airport/KIX/index.html":1,"/airport/LAX/index.html":1,"/airport/MCO/index.html":1,"/airport/MIA/index.html":1,"/airport/NRT/index.html":1,"/airport/ORD/index.html":1,"/airport/PDX/index.html":1,"/airport/SAN/index.html":1,"/airport/SEA/index.html":1,"/airport/SFO/index.html":1,"/airport/YUL/index.html":1,"/airport/YVR/index.html":1};
        function enOf(p){ return (p || '/').replace(/^\/(es|it)(?=\/|$)/, '') || '/'; }
        function treeHas(lang, enPath){
          var p = enPath || '/';
          if (p === '') p = '/';
          if (lang === 'it') {
            if (IT_OK[p]) return true;
            if (p.slice(-1) !== '/' && IT_OK[p + '/']) return true;
            if (/index\.html$/.test(p) && IT_OK[p.replace(/index\.html$/, '')]) return true;
            return false;
          }
          if (lang === 'es') {
            /* Historic ES behaviour prefixes /es+path, except IT-only guides that would 404. */
            if (/^\/countries\/(italy|italy-map|spain|spain-map)\.html$/.test(p)) return false;
            return true;
          }
          return false;
        }
        function withTree(lang, enPath, search, hash){
          var p = enPath || '/';
          if (p === '/' || p === '/index.html') {
            var dest = '/' + lang + '/' + search + hash;
            if (search.indexOf('view=') < 0 && (hash === '#map' || hash === '#world-map')) dest = '/' + lang + '/?view=map';
            return dest;
          }
          return '/' + lang + p + search + hash;
        }
        if (TREE_LANGS.indexOf(lang) >= 0 && prevPathLang !== lang) {
          var enPath2 = prevPathLang ? enOf(path) : path;
          var dest2;
          if (treeHas(lang, enPath2)) dest2 = withTree(lang, enPath2, search, hash);
          else {
            dest2 = '/' + lang + '/';
            if (search.indexOf('view=') < 0 && (hash === '#map' || hash === '#world-map')) dest2 = '/' + lang + '/?view=map';
            else dest2 = '/' + lang + '/' + search + hash;
          }
          location.assign(dest2);
          return;
        }
        if (lang === 'en' && TREE_LANGS.indexOf(prevPathLang) >= 0) {
          var enPath3 = path.replace(/^\/(es|it)(?=\/|$)/, '') || '/';
          if (enPath3 === '') enPath3 = '/';
          location.assign(enPath3 + search + hash);
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
    /* Footer copyright disc — translate the copyright sentence while keeping affiliate + Terms.
       Also upgrade a bare « © YEAR PetPolicyCheck » paragraph so every footer shows the full mention. */
    function paintFootCopyright(p, fallbackHref) {
      /* Copyright and the See Terms link stay in English on every page and language (Marc 2026-11-12).
         The Amazon Associates sentence still follows the active language. */
      var en = D.en || {};
      var copy = en['site.foot.copyright'] || '© 2026 PetPolicyCheck · Paw Passport. All rights reserved. Content, data, design and images may not be copied or reproduced without written permission.';
      var aff = t('site.foot.aff');
      if (!copy) return;
      var link = p.querySelector('a[href*="terms"]');
      var termsHref = (link && link.getAttribute('href')) || fallbackHref || 'terms.html';
      var affHtml = aff ? '<span data-i18n="site.foot.aff">' + aff + '</span> ' : '';
      var termsHtml = '<a href="' + termsHref + '">Terms</a>';
      p.classList.add('disc');
      p.removeAttribute('style');
      p.innerHTML = affHtml + copy + ' See ' + termsHtml + '.';
    }
    var footTerms = (document.querySelector('footer a[href*="terms"]') || {}).getAttribute && (document.querySelector('footer a[href*="terms"]').getAttribute('href'));
    document.querySelectorAll('footer .disc').forEach(function (p) { paintFootCopyright(p, footTerms); });
    document.querySelectorAll('footer p').forEach(function (p) {
      if (p.classList.contains('disc')) return;
      var text = (p.textContent || '').replace(/\s+/g, ' ').trim();
      if (/^©\s*\d{4}\s*PetPolicyCheck\.?$/.test(text)) paintFootCopyright(p, footTerms);
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
    if (L === 'en' || L === 'it' || !isLongForm()) {
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
