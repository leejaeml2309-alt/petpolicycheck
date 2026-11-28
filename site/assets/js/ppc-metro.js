/*! PetPolicyCheck metro map: one landmark at the top of every page.
    Lines = major sections, stations = their sub-sections. Current station highlighted,
    "Terminal" always one tap away. English pages only for now (preview). */
(function () {
  "use strict";
  var LINES = [
    { id: "map", n: "1", name: "Destinations", c: "#d9b765", st: [
      ["World map", "/?view=map"], ["Country guides", "/countries/"], ["USA state map", "/countries/usa-map.html"], ["Routes", "/routes/"] ] },
    { id: "law", n: "2", name: "Vet & paperwork", c: "#a7b1d3", st: [
      ["Vet hall", "/vet-paperwork/"], ["Vet prep", "/vet-prep/"], ["Health certificate", "/vet-info/"], ["Titer countdown", "/titer-calculator/"], ["Pet passport", "/passport/"], ["Partner vets", "/partner-vets/"], ["US clinics", "/clinics/usa.html"], ["Insurance", "/insurance/pet-insurance-for-travelers.html"] ] },
    { id: "flight", n: "3", name: "Airlines", c: "#98c6cc", st: [
      ["Airline policies", "/airlines/"], ["Compare", "/airlines/compare/"], ["Under-seat sizes", "/products/under-seat-carrier-size-by-airline.html"], ["Airports", "/airport/"], ["Flight volunteers", "/flight-volunteer/"] ] },
    { id: "shop", n: "4", name: "Gear", c: "#dfa572", st: [
      ["Board now", "/board-now/"], ["Soft carriers", "/products/best-airline-approved-soft-carriers.html"], ["Carriers & crates", "/products/carriers/"], ["All products", "/products/"], ["Gifts", "/products/gifts/"] ] },
    { id: "tools", n: "5", name: "Planning tools", c: "#3e8e8a", st: [
      ["Tools hall", "/planning-tools/"], ["Checklist", "/pet-travel-checklist/"], ["Planner", "/planner/"], ["Fit check", "/fit/"] ] },
    { id: "hotel", n: "6", name: "Stay & ground", c: "#d3a0b1", st: [
      ["Hotels", "/hotels/"], ["Hotel pet rules", "/hotel-pets/"], ["Rides", "/taxi/"] ] },
    { id: "grooming", n: "7", name: "Grooming", c: "#c6a4db", st: [
      ["Groomers", "/grooming/"] ] },
    { id: "forum", n: "8", name: "Community", c: "#9dc2a0", st: [
      ["Forum", "/forum/"], ["Stories", "/forum/pet-travel-stories/"], ["Adoptions", "/adoptions/"], ["News", "/news/"], ["Rule updates", "/updates.html"], ["Field guides", "/field-guides/"] ] },
    { id: "b2b", n: "B", name: "Business", c: "#8b9ce2", st: [
      ["Pet Desk", "/pro/"], ["Free widgets", "/widgets/"] ] },
    { id: "military", n: "M", name: "Military", c: "#0a2e5c", mil: true, st: [
      ["Military gate", "/military/"], ["Veterans", "/veterans/"], ["Service dogs", "/veterans/#service-dog-support"], ["PCS moves", "/military-pcs/"], ["K9", "/k9/"] ] }
  ];
  var SEC = { map: "map", law: "law", vet: "law", tools: "tools", flight: "flight", shop: "shop", hotel: "hotel", ground: "ground", grooming: "grooming", forum: "forum", news: "forum", adoptions: "forum", k9: "military", veterans: "military" };

  function norm(p) { p = (p || "/").replace(/index\.html$/, ""); return p || "/"; }
  function stPath(u) { return norm(u.split("#")[0].split("?")[0]); }

  function locate() {
    var path = norm(location.pathname), q = location.search || "", best = null, bestLen = -1;
    LINES.forEach(function (L, li) {
      L.st.forEach(function (s, si) {
        var sp = stPath(s[1]), hit = false;
        if (s[1] === "/?view=map") hit = path === "/";
        else if (sp === path) hit = true;
        else if (sp.slice(-1) === "/" && sp !== "/" && path.indexOf(sp) === 0) hit = true;
        if (s[1].indexOf("#") > -1) hit = false; // hash stations never steal the page match
        var len = hit ? sp.length + (sp === path ? 1000 : 0) : -1;
        if (len > bestLen) { bestLen = len; best = { li: li, si: si }; }
      });
    });
    if (best) return best;
    var sec = document.documentElement.getAttribute("data-section");
    for (var i = 0; i < LINES.length; i++) if (LINES[i].id === SEC[sec]) return { li: i, si: -1 };
    return { li: 0, si: -1 };
  }

  function esc(t) { return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;"); }
  function bullet(L, tag, extra) {
    return "<" + tag + ' class="ppc-metro__bul' + (L.mil ? " is-mil" : "") + '" style="--c:' + L.c + '"' + (extra || "") + ">" + L.n + "</" + tag + ">";
  }
  function track(L, here) {
    var h = '<ol class="ppc-metro__track' + (L.mil ? " is-mil" : "") + '" style="--c:' + L.c + '">';
    L.st.forEach(function (s, i) {
      var on = i === here;
      h += '<li class="ppc-metro__st' + (on ? " is-here" : "") + '"><a href="' + s[1] + '"' + (on ? ' aria-current="page"' : "") + '><span class="ppc-metro__dot" aria-hidden="true"></span><span class="ppc-metro__lbl">' + esc(s[0]) + "</span></a></li>";
    });
    return h + "</ol>";
  }

  function build() {
    if (document.getElementById("ppc-metro")) return;
    var path = location.pathname;
    if (/^\/(de|es|fr|it|ja|ko)\//.test(path) || /print\.html$/.test(path) || window.top !== window.self) return;
    var hdr = document.querySelector("header.top");
    if (!hdr || hdr.closest(".intro")) return;
    var cur = locate(), isTerminal = norm(path) === "/terminal/";
    var nav = document.createElement("nav");
    nav.id = "ppc-metro"; nav.className = "ppc-metro"; nav.setAttribute("aria-label", "Metro map of the site");
    var L = LINES[cur.li];
    var bul = LINES.map(function (x, i) {
      return bullet(x, "button", ' type="button" data-line="' + i + '" aria-pressed="' + (i === cur.li) + '" aria-label="Line ' + x.n + ": " + x.name + '" title="Line ' + x.n + " · " + x.name + '"');
    }).join("");
    var all = LINES.map(function (x) {
      return '<div class="ppc-metro__row">' + bullet(x, "span", ' aria-hidden="true"') + '<span class="ppc-metro__rowname">' + x.name + "</span>" + track(x, x === L ? cur.si : -1) + "</div>";
    }).join("");
    nav.innerHTML =
      '<div class="ppc-metro__bar">' +
        (isTerminal ? '<a class="ppc-metro__back" href="/"><span aria-hidden="true">&larr;</span> Entrance</a>'
                    : '<a class="ppc-metro__back" href="/terminal/"><span aria-hidden="true">&larr;</span> Terminal</a>') +
        '<p class="ppc-metro__where"><span class="ppc-metro__line">Line ' + L.n + " &middot; " + L.name + "</span>" +
          (cur.si > -1 ? '<span class="ppc-metro__you">You are at <b>' + esc(L.st[cur.si][0]) + "</b></span>" : "") + "</p>" +
        '<div class="ppc-metro__bullets" role="group" aria-label="Lines">' + bul + "</div>" +
        '<button class="ppc-metro__all-btn" type="button" aria-expanded="false" aria-controls="ppc-metro-all">All lines</button>' +
      "</div>" +
      '<div class="ppc-metro__cur">' + track(L, cur.si) + "</div>" +
      '<div class="ppc-metro__all" id="ppc-metro-all" hidden>' + all + "</div>";
    hdr.parentNode.insertBefore(nav, hdr.nextSibling);

    var curBox = nav.querySelector(".ppc-metro__cur"), where = nav.querySelector(".ppc-metro__line");
    function centre() {
      var t = curBox.querySelector(".ppc-metro__track"), h = t && t.querySelector(".is-here");
      if (t && h) t.scrollLeft = Math.max(0, h.offsetLeft - (t.clientWidth - h.offsetWidth) / 2);
    }
    nav.querySelectorAll("[data-line]").forEach(function (b) {
      b.addEventListener("click", function () {
        var i = +b.getAttribute("data-line"), X = LINES[i];
        curBox.innerHTML = track(X, i === cur.li ? cur.si : -1);
        where.innerHTML = "Line " + X.n + " &middot; " + X.name;
        nav.querySelectorAll("[data-line]").forEach(function (o) { o.setAttribute("aria-pressed", String(o === b)); });
        centre();
      });
    });
    var ab = nav.querySelector(".ppc-metro__all-btn"), ap = nav.querySelector(".ppc-metro__all");
    ab.addEventListener("click", function () {
      var open = ap.hidden; ap.hidden = !open; ab.setAttribute("aria-expanded", String(open));
      ab.textContent = open ? "Close map" : "All lines";
    });
    centre();
  }
  window.PPCMetro = { lines: LINES, build: build };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
