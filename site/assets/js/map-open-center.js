/* PetPolicyCheck · center the country/region map stage in the opening viewport.
   Shared by every *-map.html page (USA included).

   On the initial load, when there is no explicit #hash and the visitor has
   not already scrolled, scroll so .mapcard (map + its controls) sits in the
   visible band below the sticky header. If the card is taller than that
   band, pin its top just below the header with a little breathing room so
   the top of the map and its tools are never cropped.

   Never overrides an explicit location.hash, never fights back/forward
   scroll restoration, and never interferes with zoom, pan, pinch, or
   region/airport selection. Runs at most once per initial load, after the
   map stage has a real rendered height. */
(function () {
  var PAD = 16;
  var MIN_H = 80;
  var MAX_WAIT = 5000;
  var done = false;
  var userMoved = false;
  var started = false;

  function hasHash() {
    return (location.hash || '').length > 1;
  }

  function isBackForward() {
    try {
      var nav = performance.getEntriesByType && performance.getEntriesByType('navigation')[0];
      if (nav && nav.type === 'back_forward') return true;
    } catch (e) {}
    try {
      if (performance.navigation && performance.navigation.type === 2) return true;
    } catch (e) {}
    return false;
  }

  function headerH() {
    var h = document.querySelector('header.top, header.map-nav, .top');
    if (!h) return 0;
    return Math.max(0, Math.round(h.getBoundingClientRect().height));
  }

  function stage() {
    return document.querySelector('.mapcard') ||
      document.getElementById('map') ||
      document.getElementById('country-map') ||
      document.getElementById('usa-map');
  }

  function report(extra) {
    var el = stage();
    var r = el ? el.getBoundingClientRect() : null;
    var hh = headerH();
    var visH = Math.max(0, window.innerHeight - hh);
    window.__ppcMapOpenCenter = Object.assign({
      done: done,
      userMoved: userMoved,
      hash: location.hash || '',
      headerH: hh,
      visH: visH,
      visCenter: hh + visH / 2,
      scrollY: window.scrollY,
      top: r ? r.top : null,
      bottom: r ? r.bottom : null,
      height: r ? r.height : null,
      centerY: r ? (r.top + r.height / 2) : null
    }, extra || {});
    return window.__ppcMapOpenCenter;
  }


  function allowed(adjusting) {
    if (userMoved || hasHash() || isBackForward()) return false;
    if (done && !adjusting) return false;
    if (!adjusting && window.scrollY >= 10) return false;
    return true;
  }

  function targetY(el) {
    var hh = headerH();
    var visH = Math.max(0, window.innerHeight - hh);
    var r = el.getBoundingClientRect();
    var absTop = r.top + window.scrollY;
    var h = r.height;
    var y;
    if (h >= visH - PAD) {
      y = absTop - hh - PAD;
    } else {
      var visCenter = hh + visH / 2;
      y = absTop + h / 2 - visCenter;
    }
    return Math.max(0, Math.round(y));
  }

  function apply(reason) {
    var adjusting = reason === 'adjust';
    if (!allowed(adjusting)) {
      if (!done) report({ skipped: true, reason: reason || 'blocked' });
      return false;
    }
    var el = stage();
    if (!el || el.getBoundingClientRect().height < MIN_H) return false;
    var y = targetY(el);
    try { document.documentElement.style.scrollBehavior = 'auto'; } catch (e) {}
    window.scrollTo(0, y);
    done = true;
    report({ applied: true, targetY: y, reason: reason || 'center' });
    try { window.dispatchEvent(new Event('ppc:map-centered')); } catch (e) {}
    return true;
  }

  function markMoved() {
    if (!done) userMoved = true;
  }

  function boot() {
    if (started) return;
    started = true;
    if (hasHash() || isBackForward()) {
      done = true;
      report({ skipped: true, reason: hasHash() ? 'hash' : 'back_forward' });
      return;
    }

    window.addEventListener('wheel', markMoved, { passive: true });
    window.addEventListener('touchmove', markMoved, { passive: true });
    window.addEventListener('keydown', function (e) {
      if (['PageDown', 'PageUp', 'Home', 'End', 'ArrowDown', 'ArrowUp', ' '].indexOf(e.key) >= 0) markMoved();
    });

    var lastH = 0, stable = 0, elapsed = 0;
    var ro = null;

    function tryNow(reason) {
      if (apply(reason)) {
        if (ro) { try { ro.disconnect(); } catch (e) {} ro = null; }
        // One short follow-up if fonts/labels still settle the height.
        setTimeout(function () {
          if (userMoved || hasHash()) return;
          apply('adjust');
        }, 280);
        return true;
      }
      return false;
    }

    function pulse() {
      if (done || userMoved || hasHash()) return;
      var el = stage();
      if (el) {
        var h = el.getBoundingClientRect().height;
        if (h >= MIN_H) {
          if (Math.abs(h - lastH) < 1) stable++;
          else { stable = 0; lastH = h; }
          if (stable >= 2 && tryNow('stable')) return;
        }
      }
      elapsed += 50;
      if (elapsed >= MAX_WAIT) { tryNow('timeout'); return; }
      setTimeout(pulse, 50);
    }

    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        if (tryNow('raf')) return;
        var el = stage();
        if (el && typeof ResizeObserver !== 'undefined') {
          ro = new ResizeObserver(function () { tryNow('resize'); });
          ro.observe(el);
        }
        pulse();
      });
    });
  }

  report({ started: false });
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
  window.addEventListener('load', function () { if (!done && started) apply('load'); });
})();
