/*! PetPolicyCheck boarding-pass frames (preview v4b, 2026-11-28).
    Wraps section cards in the shared .ppc-ticket markup (head band + body + perforated stub).
    Styles: /assets/css/ppc-ticket.css (.ppc-ticket--frame). English pages only.
    Never touches the metro header or any geographic map (world/country SVG, pins, popups, zoom). */
(function () {
  "use strict";
  var EXCL = "#ppc-metro, .ppc-metro, .ppc-mmap, .tp-fullmap, .mapcard, .mapbox, #mapbox, .mapscroll, .map-stage, #world-map, #map, #usa-map, #country-map, .map-switch, .panel, svg";
  var PLANE = '<svg class="ppc-ticket__plane" width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5z"/></svg>';
  var GOLD = "#d9b765";
  /* One entry per card family. o: "p" portrait (stub bottom) | "l" landscape (stub right, bottom on mobile). */
  var CFG = [
    { sel: "a.tp-gate", o: "p", title: "h3", cta: ".tp-gate__go", accent: "sec" },
    { sel: "a.ent-gate", o: "p", title: "b", ctaText: "Board here", accent: function (el) { return el.classList.contains("is-mil") ? "#0a2e5c" : GOLD; } },
    { sel: "a.tp-head", o: "l", title: ".tp-head__cap b", cta: ".tp-head__go", accent: GOLD },
    { sel: "aside.usa-map-tease", o: "l", titleText: function (el) { var t = el.getAttribute("aria-label") || "Country map"; return t.charAt(0).toUpperCase() + t.slice(1); }, cta: "a.btn", accent: GOLD },
    { sel: ".bn .bn-card", o: "p", title: ".pp-name", cta: ".pp-actions a.pp-btn", accent: "#dfa572" },
    { sel: ".cty-grid > .cty", o: "l", title: "b", cta: ".cty__l > a", accent: GOLD },
    { sel: "ul.plist.cards > li", o: "l", title: "a", dupCta: "Read", accent: "#dfa572" },
    { sel: ".ht-cities > a", o: "p", title: "b", ctaText: "City guide", accent: "#d3a0b1" },
    { sel: "li.scard", o: "l", title: ".sh", cta: ".slink a", accent: "#9dc2a0" },
    { sel: ".adopt-grid > a.adopt-card", o: "l", title: "h3", cta: ".ppc-btn", accent: "#9dc2a0" },
    { sel: ".theme-adoptions main > section.gcard", o: "l", title: ":scope > h2", stubLabel: "Line 8 · Community", accent: "#9dc2a0", section: 1 },
    { sel: ".theme-veterans main > section.gcard", o: "l", title: ":scope > h2", stubLabel: "Line M · Veterans", accent: "#0a2e5c", section: 1 },
    { sel: ".gdir-grid > .gcard", o: "l", title: ".gc-h > a", dupCta: "Visit", accent: "#c6a4db" },
    { sel: ".theme-flight .ppc-split > .ppc-split__panel", o: "l", title: ".ppc-split__h", stubLabel: "Line 1 · Routes", accent: GOLD, section: 1 }
  ];
  function mk(cls) { var d = document.createElement("div"); d.className = cls; return d; }
  function arrow(el) {
    if (/→|\u2192/.test(el.textContent)) return;
    var s = document.createElement("span"); s.className = "ppc-ticket__arrow"; s.setAttribute("aria-hidden", "true"); s.textContent = "→"; el.appendChild(s);
  }
  function q(el, s) { try { return el.querySelector(s); } catch (e) { return null; } }
  function build(el, c) {
    if (el.__ppcTicket || el.classList.contains("ppc-ticket")) return;
    if (el.parentElement && el.parentElement.closest(EXCL)) return;
    el.__ppcTicket = 1;
    var head = mk("ppc-ticket__head"), main = mk("ppc-ticket__main"), body = mk("ppc-ticket__body"), stub = mk("ppc-ticket__stub");
    var title = mk("ppc-ticket__title");
    var t = c.title ? q(el, c.title) : null;
    var cta = c.cta ? q(el, c.cta) : null;
    if (t) title.appendChild(t); else title.textContent = c.titleText ? c.titleText(el) : "";
    head.appendChild(title);
    head.insertAdjacentHTML("beforeend", PLANE);
    while (el.firstChild) body.appendChild(el.firstChild);
    if (cta) { cta.classList.add("ppc-ticket__cta"); arrow(cta); stub.appendChild(cta); }
    else if (c.dupCta && t && t.tagName === "A") {
      t.classList.add("ppc-ticket__stretch");
      var a = document.createElement("span"); a.className = "ppc-ticket__cta"; a.setAttribute("aria-hidden", "true");
      a.textContent = c.dupCta; arrow(a); stub.appendChild(a);
    } else if (c.ctaText) {
      var s = document.createElement("span"); s.className = "ppc-ticket__cta"; s.setAttribute("aria-hidden", "true"); s.textContent = c.ctaText; arrow(s); stub.appendChild(s);
    } else if (c.stubLabel) {
      var l = document.createElement("p"); l.className = "ppc-ticket__lbl"; l.textContent = c.stubLabel; stub.appendChild(l);
    }
    main.appendChild(head); main.appendChild(body);
    el.appendChild(main); el.appendChild(stub);
    el.classList.add("ppc-ticket", "ppc-ticket--frame", c.o === "p" ? "ppc-ticket--portrait" : "ppc-ticket--landscape");
    var ac = typeof c.accent === "function" ? c.accent(el) : c.accent === "sec" ? (el.style.getPropertyValue("--sec") || GOLD) : c.accent;
    if (ac) el.style.setProperty("--ticket-accent", ac.trim());
    if (/^#0a2e5c$/i.test((ac || "").trim())) el.classList.add("ppc-ticket--mil");
    if (el.parentElement && !c.section) el.parentElement.classList.add("ppc-ticket-list");
    else el.classList.add("ppc-ticket--section");
  }
  function scan() {
    CFG.forEach(function (c) {
      var list; try { list = document.querySelectorAll(c.sel); } catch (e) { return; }
      for (var i = 0; i < list.length; i++) build(list[i], c);
    });
  }
  /* Grid fr tracks can differ by 1/64 px; pin every ticket of a list to the narrowest one. */
  function equalize() {
    var lists = document.querySelectorAll(".ppc-ticket-list");
    for (var i = 0; i < lists.length; i++) {
      var kids = [], k = lists[i].children;
      for (var j = 0; j < k.length; j++) if (k[j].classList.contains("ppc-ticket--frame")) { k[j].style.width = ""; k[j].style.justifySelf = ""; if (k[j].getClientRects().length) kids.push(k[j]); }
      if (kids.length < 2) continue;
      var min = Infinity;
      kids.forEach(function (e) { min = Math.min(min, e.getBoundingClientRect().width); });
      var w = Math.floor(min * 64) / 64;
      kids.forEach(function (e) { if (e.getBoundingClientRect().width !== w) { e.style.width = w + "px"; e.style.justifySelf = "start"; } });
    }
  }
  var eqT = 0;
  function eqLater() { clearTimeout(eqT); eqT = setTimeout(equalize, 60); }
  var pending = 0;
  function later() { if (pending) return; pending = 1; (window.requestAnimationFrame || setTimeout)(function () { pending = 0; scan(); eqLater(); }); }
  function start() {
    scan(); equalize();
    window.addEventListener("resize", eqLater);
    window.addEventListener("load", eqLater);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(eqLater);
    if (window.MutationObserver) new MutationObserver(later).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
  window.PPCTicketFrames = { scan: scan };
})();
