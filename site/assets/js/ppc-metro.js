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


  /* Desktop schematic (>=821px): the lines cross like a real metro map. Interchanges are
     stations shared by two or more lines, drawn as connection rings. Mobile keeps the single track. */
  var POS = {
    "/?view=map":[40,116], "/hotels/":[150,116], "/countries/":[250,116], "/countries/usa-map.html":[330,116], "/routes/":[440,76],
    "/vet-paperwork/":[40,36], "/vet-prep/":[100,36], "/vet-info/":[380,196], "/titer-calculator/":[450,196], "/passport/":[520,196],
    "/partner-vets/":[590,196], "/clinics/usa.html":[660,196], "/insurance/pet-insurance-for-travelers.html":[730,196],
    "/airlines/":[340,36], "/airlines/compare/":[530,76], "/products/under-seat-carrier-size-by-airline.html":[640,76], "/airport/":[760,76], "/flight-volunteer/":[880,76],
    "/board-now/":[640,156], "/products/best-airline-approved-soft-carriers.html":[740,36], "/products/carriers/":[820,36], "/products/":[900,36], "/products/gifts/":[980,36],
    "/planning-tools/":[540,156], "/pet-travel-checklist/":[740,156], "/planner/":[840,156], "/fit/":[940,156], "/widgets/":[1040,156], "/pro/":[1120,196],
    "/hotel-pets/":[150,76], "/taxi/":[150,156], "/veterans/#service-dog-support":[150,196],
    "/grooming/":[250,160],
    "/forum/":[740,116], "/forum/pet-travel-stories/":[800,116], "/adoptions/":[960,116], "/news/":[1030,116], "/updates.html":[1100,116], "/field-guides/":[1170,116],
    "/military/":[30,196], "/veterans/":[90,196], "/military-pcs/":[210,196], "/k9/":[270,196]
  };
  /* Each desktop route: station URLs in order, with [x,y] bend points between them. */
  var ROUTE = {
    map: ["/?view=map", "/hotels/", "/countries/", "/countries/usa-map.html", [400,116], "/routes/"],
    law: ["/vet-paperwork/", "/vet-prep/", [170,36], "/countries/", [330,196], "/vet-info/", "/titer-calculator/", "/passport/", "/partner-vets/", "/clinics/usa.html", "/insurance/pet-insurance-for-travelers.html"],
    flight: ["/airlines/", [400,36], "/routes/", "/airlines/compare/", "/products/under-seat-carrier-size-by-airline.html", "/airport/", "/flight-volunteer/"],
    shop: ["/board-now/", "/products/under-seat-carrier-size-by-airline.html", [680,36], "/products/best-airline-approved-soft-carriers.html", "/products/carriers/", "/products/", "/products/gifts/"],
    tools: ["/planning-tools/", "/board-now/", "/pet-travel-checklist/", "/planner/", "/fit/", "/widgets/"],
    hotel: ["/hotel-pets/", "/hotels/", "/taxi/", "/veterans/#service-dog-support"],
    grooming: ["/countries/", "/grooming/"],
    forum: ["/forum/", "/forum/pet-travel-stories/", [840,116], "/flight-volunteer/", [920,116], "/adoptions/", "/news/", "/updates.html", "/field-guides/"],
    b2b: ["/widgets/", [1080,196], "/pro/"],
    military: ["/military/", "/veterans/", "/veterans/#service-dog-support", "/military-pcs/", "/k9/"]
  };
  var NAMES = {};
  LINES.forEach(function (L) { L.st.forEach(function (s) { NAMES[s[1]] = s[0]; }); });
  NAMES["/hotels/"] = "Hotels"; NAMES["/countries/"] = "Country guides";
  function linesAt(u) { var o = []; LINES.forEach(function (L, i) { if (ROUTE[L.id].indexOf(u) > -1) o.push(i); }); return o; }
  function svgMap(sel, curUrl) {
    var W = 1200, H = 226, h = '<svg class="ppc-mmap__svg" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Metro map: all lines and interchanges">';
    var order = LINES.map(function (L, i) { return i; }).filter(function (i) { return i !== sel; }).concat([sel]);
    order.forEach(function (i) {
      var L = LINES[i], pts = ROUTE[L.id].map(function (p) { return typeof p === "string" ? POS[p] : p; });
      var d = "M" + pts.map(function (p) { return p[0] + " " + p[1]; }).join("L");
      var on = i === sel;
      if (L.mil) h += '<path d="' + d + '" class="ppc-mmap__case' + (on ? " is-on" : "") + '"/>';
      h += '<path d="' + d + '" class="ppc-mmap__ln' + (on ? " is-on" : "") + '" style="stroke:' + L.c + '" data-line="' + i + '"/>';
    });
    var seen = {}, k = 0, selSt = ROUTE[LINES[sel].id].filter(function (p) { return typeof p === "string"; });
    Object.keys(POS).forEach(function (u) {
      var xy = POS[u], ls = linesAt(u), x = xy[0], y = xy[1];
      var onSel = selSt.indexOf(u) > -1, here = u === curUrl, ic = ls.length > 1;
      var cls = "ppc-mmap__st" + (ic ? " is-ic" : "") + (onSel ? " is-on" : "") + (here ? " is-here" : "");
      h += '<a href="' + u + '" class="' + cls + '"' + (here ? ' aria-current="page"' : "") + "><title>" + esc(NAMES[u] || u) + (ic ? " (interchange)" : "") + "</title>";
      if (ic) h += '<circle cx="' + x + '" cy="' + y + '" r="8.5" class="ppc-mmap__ring"/>';
      else h += '<circle cx="' + x + '" cy="' + y + '" r="4.6" class="ppc-mmap__dot" style="stroke:' + LINES[ls[0]].c + '"/>';
      if (here) h += '<circle cx="' + x + '" cy="' + y + '" r="13" class="ppc-mmap__here"/>';
      if (onSel || here) {
        var idx = selSt.indexOf(u), below = (idx > -1 ? idx : k++) % 2 === 0, ty = below ? y + 23 : y - 14;
        var anc = x < 60 ? "start" : x > W - 60 ? "end" : "middle", tx = anc === "start" ? x - 8 : anc === "end" ? x + 8 : x;
        var nb = [selSt[idx - 1], selSt[idx + 1]].filter(Boolean).map(function (v) { return POS[v]; });
        if (idx > -1 && nb.length && nb.every(function (q) { return Math.abs(q[0] - x) < Math.abs(q[1] - y); })) { anc = "start"; tx = x + 17; ty = ic ? y - 9 : y + 4; }
        h += '<text x="' + tx + '" y="' + ty + '" text-anchor="' + anc + '" class="ppc-mmap__lbl' + (here ? " is-here" : "") + '">' + esc(NAMES[u] || u) + "</text>";
      }
      h += "</a>";
    });
    return h + "</svg>";
  }

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
      '<div class="ppc-mmap">' + svgMap(cur.li, cur.si > -1 ? L.st[cur.si][1] : "") + "</div>" +
      '<div class="ppc-metro__all" id="ppc-metro-all" hidden>' + all + "</div>";
    hdr.parentNode.insertBefore(nav, hdr.nextSibling);

    document.documentElement.classList.add("ppc-v2");
    var mapBox = nav.querySelector(".ppc-mmap");
    var curBox = nav.querySelector(".ppc-metro__cur"), where = nav.querySelector(".ppc-metro__line");
    function centre() {
      var t = curBox.querySelector(".ppc-metro__track"), h = t && t.querySelector(".is-here");
      if (t && h && t.clientWidth) { var a = h.getBoundingClientRect(), b = t.getBoundingClientRect(); t.scrollLeft += (a.left + a.width / 2) - (b.left + b.width / 2); }
    }
    nav.querySelectorAll("[data-line]").forEach(function (b) {
      b.addEventListener("click", function () {
        var i = +b.getAttribute("data-line"), X = LINES[i];
        curBox.innerHTML = track(X, i === cur.li ? cur.si : -1);
        mapBox.innerHTML = svgMap(i, cur.si > -1 ? L.st[cur.si][1] : "");
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
    var rz; window.addEventListener("resize", function () { clearTimeout(rz); rz = setTimeout(centre, 120); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(centre);
  }
  window.PPCMetro = { lines: LINES, build: build };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
