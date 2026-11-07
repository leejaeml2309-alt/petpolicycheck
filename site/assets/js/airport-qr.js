/* Airport QR pages: scoped preview-safe nav and UTM-only propagation. */
(function () {
  'use strict';
  function boot() {
    var root = new URL(document.documentElement.dataset.siteRoot, document.baseURI);
    // Shared pastilles builds root-relative navigation from pathname depth.
    // Rebase it to this site's root when previewed below a directory prefix.
    document.querySelectorAll('#site-menu a').forEach(function (a) {
      var href = a.getAttribute('href');
      if (href && !/^(?:[a-z]+:|\/\/)/i.test(href)) {
        a.href = new URL(href.replace(/^(?:\.\.\/)+/, ''), root).href;
      }
    });
    var incoming = new URLSearchParams(location.search);
    function propagate(a) {
      var href = a.getAttribute('href');
      if (!href || href[0] === '#') return;
      var url = new URL(href, document.baseURI);
      if (url.origin !== location.origin || !url.pathname.startsWith(root.pathname)) return;
      incoming.forEach(function (value, key) {
        if (/^utm_[a-z0-9_]+$/i.test(key)) url.searchParams.set(key, value);
      });
      a.href = url.href;
    }
    document.querySelectorAll('a[href]').forEach(propagate);
    document.addEventListener('click', function (event) {
      var a = event.target.closest && event.target.closest('a[href]');
      if (a) propagate(a);
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
}());
