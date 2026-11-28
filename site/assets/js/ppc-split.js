/*! PetPolicyCheck sub-section split (preview 2026-11-28). Long pages become tabbed sub-sections.
    Without JavaScript every section stays visible; with it, one sub-section shows at a time,
    each with its own #hash so links and the back button still work. */
(function () {
  "use strict";
  function slug(t) { return t.toLowerCase().replace(/&amp;|&/g, "and").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 48); }
  function runSections(root) {
    var stop = ["Sources", "Next step"];
    var secs = [].filter.call(root.querySelectorAll("section[id]"), function (x) {
      var h = x.querySelector(":scope > h2"); return h && !/ppc-src|ppc-next/.test(x.className) && stop.indexOf(h.textContent.trim()) < 0;
    });
    if (secs.length < 2) return;
    var parent = secs[0].parentNode; secs = secs.filter(function (x) { return x.parentNode === parent; });
    if (secs.length < 2) return;
    secs.forEach(function (x) { x.classList.add("ppc-split__panel"); x.setAttribute("role", "tabpanel"); x.setAttribute("aria-labelledby", "t-" + x.id); });
    wire(root, parent, secs);
  }
  function run(root) {
    if (root.getAttribute("data-ppc-split") === "sections") return runSections(root);
    var stop = (root.getAttribute("data-ppc-split-stop") || "Sources|Next step").split("|");
    var h2s = [].slice.call(root.querySelectorAll("h2"));
    if (root.getAttribute("data-ppc-split-in")) h2s = [].slice.call(root.querySelectorAll(root.getAttribute("data-ppc-split-in") + " > h2"));
    if (h2s.length < 2) return;
    var cnt = new Map(), parent = null, best = 0;
    h2s.forEach(function (h) { var c = (cnt.get(h.parentNode) || 0) + 1; cnt.set(h.parentNode, c); if (c > best) { best = c; parent = h.parentNode; } });
    var skip = (root.getAttribute("data-ppc-split-skip") || "For travel pros").split("|");
    h2s = h2s.filter(function (h) { var t = h.textContent.trim(); return h.parentNode === parent && !skip.some(function (k) { return t.indexOf(k) === 0; }); });
    var cut = h2s.length;
    for (var i = 0; i < h2s.length; i++) if (stop.indexOf(h2s[i].textContent.trim()) > -1) { cut = i; break; }
    var endNode = cut < h2s.length ? h2s[cut] : null;
    h2s = h2s.slice(0, cut);
    if (h2s.length < 2) return;
    var panels = [];
    h2s.forEach(function (h, idx) {
      var sec = document.createElement("section");
      sec.className = "ppc-split__panel";
      var id = h.id || ("s-" + slug(h.textContent));
      if (h.id) h.removeAttribute("id");
      sec.id = id; sec.setAttribute("role", "tabpanel"); sec.setAttribute("aria-labelledby", "t-" + id);
      parent.insertBefore(sec, h);
      var n = h, next;
      while (n && n !== endNode && !(n !== h && h2s.indexOf(n) > -1)) { next = n.nextSibling; sec.appendChild(n); n = next; }
      panels.push(sec);
    });
    wire(root, parent, panels);
  }
  function wire(root, parent, panels) {
    var bar = document.createElement("div");
    bar.className = "ppc-split"; bar.setAttribute("role", "tablist"); bar.setAttribute("aria-label", root.getAttribute("data-ppc-split-label") || "Sections of this page");
    panels.forEach(function (p) {
      var b = document.createElement("a");
      b.href = "#" + p.id; b.id = "t-" + p.id; b.setAttribute("role", "tab"); b.className = "ppc-split__tab";
      b.textContent = p.querySelector("h2").textContent.replace(/\s+/g, " ").trim();
      bar.appendChild(b);
    });
    parent.insertBefore(bar, panels[0]);
    function show(id, push) {
      var hit = panels.filter(function (p) { return p.id === id || (id && p.querySelector("#" + CSS.escape(id))); })[0] || panels[0];
      panels.forEach(function (p) { p.hidden = p !== hit; });
      [].forEach.call(bar.children, function (b) { var on = b.id === "t-" + hit.id; b.setAttribute("aria-selected", String(on)); b.tabIndex = on ? 0 : -1; });
      if (push && history.replaceState) history.replaceState(null, "", "#" + hit.id);
      return hit;
    }
    bar.addEventListener("click", function (e) {
      var a = e.target.closest("a.ppc-split__tab"); if (!a) return;
      e.preventDefault(); show(a.getAttribute("href").slice(1), true);
      var top = bar.getBoundingClientRect().top + window.scrollY - 90; if (window.scrollY > top) window.scrollTo(0, top);
      a.scrollIntoView({ block: "nearest", inline: "center" });
    });
    bar.addEventListener("keydown", function (e) {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      var tabs = [].slice.call(bar.children), i = tabs.indexOf(document.activeElement); if (i < 0) return;
      var t = tabs[(i + (e.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length]; t.focus(); t.click();
    });
    window.addEventListener("hashchange", function () { var h = location.hash.slice(1); if (h) show(h, false); });
    show(location.hash.slice(1), false);
    root.classList.add("is-split");
  }
  function init() { [].forEach.call(document.querySelectorAll("[data-ppc-split]"), run); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
