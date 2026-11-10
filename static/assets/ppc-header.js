/*! Compact header proposal: burger drawer with focus trap + Esc. */
(function () {
  "use strict";

  function focusables(root) {
    return Array.prototype.slice.call(
      root.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])')
    ).filter(function (el) { return el.offsetParent !== null || el === document.activeElement; });
  }

  function init(root) {
    root = root || document;
    var bar = root.querySelector("[data-ppc-topbar]");
    if (!bar || bar.__ppcHeader) return;
    var btn = bar.querySelector("[data-ppc-burger]");
    var drawer = document.querySelector("[data-ppc-drawer]");
    var backdrop = document.querySelector("[data-ppc-drawer-backdrop]");
    if (!btn || !drawer) return;

    var lastFocus = null;

    function setOpen(open) {
      drawer.classList.toggle("is-open", open);
      if (backdrop) backdrop.classList.toggle("is-open", open);
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      document.documentElement.classList.toggle("ppc-nav-lock", open);
      if (open) {
        lastFocus = document.activeElement;
        var f = focusables(drawer);
        if (f[0]) f[0].focus();
      } else if (lastFocus) {
        lastFocus.focus();
      }
    }

    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      setOpen(!drawer.classList.contains("is-open"));
    });
    var closer = drawer.querySelector("[data-ppc-drawer-close]");
    if (closer) closer.addEventListener("click", function () { setOpen(false); });
    if (backdrop) backdrop.addEventListener("click", function () { setOpen(false); });
    drawer.addEventListener("click", function (e) {
      var a = e.target.closest && e.target.closest("a");
      if (a) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && drawer.classList.contains("is-open")) {
        e.preventDefault();
        setOpen(false);
        return;
      }
      if (e.key !== "Tab" || !drawer.classList.contains("is-open")) return;
      var f = focusables(drawer);
      if (!f.length) return;
      var first = f[0], last = f[f.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });
    bar.__ppcHeader = { open: function () { setOpen(true); }, close: function () { setOpen(false); } };
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { init(); });
  else init();
  window.PPCHeader = { init: init };
})();
