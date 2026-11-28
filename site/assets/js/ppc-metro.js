/*! PetPolicyCheck metro map: one landmark at the top of every page.
    Lines = major sections, stations = their sub-sections. Current station highlighted,
    "Terminal" always one tap away. English pages only for now (preview). */
(function () {
  "use strict";
  var LINES = [
    { id: "map", n: "1", name: "Destinations", c: "#d9b765", st: [
      ["World map", "/?view=map"], ["Country guides", "/countries/"], ["USA state map", "/countries/usa-map.html"], ["Routes", "/routes/"], ["Philippines", "/countries/philippines.html"], ["India", "/countries/india.html"] ] },
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
    "/?view=map":[40,116], "/hotels/":[150,116], "/countries/":[250,116], "/countries/usa-map.html":[330,116], "/routes/":[440,76], "/countries/philippines.html":[480,36], "/countries/india.html":[580,36],
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
    map: ["/?view=map", "/hotels/", "/countries/", "/countries/usa-map.html", [400,116], "/routes/", "/countries/philippines.html", "/countries/india.html"],
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
  /* v3 compact map (viewBox 1200x138): same topology, 7px extra vertical padding so labels clear the frame by 4px. */
  function Y(y) { return Math.round((19 + (y - 36) * 0.6) * 10) / 10; }
  function svgMap(sel, curUrl) {
    var W = 1200, H = 138, h = '<svg class="ppc-mmap__svg" viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Metro map: all lines and interchanges">';
    var order = LINES.map(function (L, i) { return i; }).filter(function (i) { return i !== sel; }).concat([sel]);
    order.forEach(function (i) {
      var L = LINES[i], pts = ROUTE[L.id].map(function (p) { return typeof p === "string" ? POS[p] : p; });
      var d = "M" + pts.map(function (p) { return p[0] + " " + Y(p[1]); }).join("L");
      var on = i === sel;
      if (L.mil) h += '<path d="' + d + '" class="ppc-mmap__case' + (on ? " is-on" : "") + '"/>';
      h += '<path d="' + d + '" class="ppc-mmap__ln' + (on ? " is-on" : "") + '" style="stroke:' + L.c + '" data-line="' + i + '"/>';
    });
    var selSt = ROUTE[LINES[sel].id].filter(function (p) { return typeof p === "string"; });
    var placed = [], labels = [], stations = Object.keys(POS);
    /* station discs count as obstacles so labels never sit on a ring */
    stations.forEach(function (u) { var x = POS[u][0], y = Y(POS[u][1]); placed.push([x - 7, y - 7, x + 7, y + 7]); });
    function tw(t) { return t.length * 6.1 + 2; }
    function fits(b) {
      if (b[0] < 2 || b[2] > W - 2 || b[1] < 1 || b[3] > H - 1) return false;
      for (var q = 0; q < placed.length; q++) { var o = placed[q]; if (b[0] < o[2] && o[0] < b[2] && b[1] < o[3] && o[1] < b[3]) return false; }
      return true;
    }
    /* who gets a name: the page you are on, then interchanges (all lines), then the selected line */
    var want = stations.filter(function (u) { return u === curUrl; })
      .concat(stations.filter(function (u) { return u !== curUrl && linesAt(u).length > 1; }))
      .concat(selSt.filter(function (u) { return u !== curUrl && linesAt(u).length < 2; }));
    want.forEach(function (u) {
      var x = POS[u][0], y = Y(POS[u][1]), t = NAMES[u] || u, w = tw(t), hh = 11;
      var c = [[x - w / 2, y + 8, "middle", x, y + 17], [x - w / 2, y - 18, "middle", x, y - 9],
               [x + 10, y - 5.5, "start", x + 10, y + 4], [x - 10 - w, y - 5.5, "end", x - 10, y + 4],
               [x + 6, y + 7, "start", x + 6, y + 16], [x - 6 - w, y + 7, "end", x - 6, y + 16],
               [x + 6, y - 17, "start", x + 6, y - 8], [x - 6 - w, y - 17, "end", x - 6, y - 8]];
      for (var n = 0; n < c.length; n++) {
        var b = [c[n][0], c[n][1], c[n][0] + w, c[n][1] + hh];
        if (fits(b)) { placed.push(b); labels.push([u, c[n][3], c[n][4], c[n][2], t]); return; }
      }
    });
    stations.forEach(function (u) {
      var x = POS[u][0], y = Y(POS[u][1]), ls = linesAt(u);
      var onSel = selSt.indexOf(u) > -1, here = u === curUrl, ic = ls.length > 1;
      var cls = "ppc-mmap__st" + (ic ? " is-ic" : "") + (onSel ? " is-on" : "") + (here ? " is-here" : "");
      h += '<a href="' + u + '" class="' + cls + '"' + (here ? ' aria-current="page"' : "") + "><title>" + esc(NAMES[u] || u) + (ic ? " (interchange)" : "") + "</title>";
      if (ic) h += '<circle cx="' + x + '" cy="' + y + '" r="6.5" class="ppc-mmap__ring"/>';
      else h += '<circle cx="' + x + '" cy="' + y + '" r="3.6" class="ppc-mmap__dot" style="stroke:' + LINES[ls[0]].c + '"/>';
      if (here) h += '<circle cx="' + x + '" cy="' + y + '" r="10" class="ppc-mmap__here"/>';
      labels.forEach(function (l) {
        if (l[0] === u) h += '<text x="' + l[1] + '" y="' + l[2] + '" text-anchor="' + l[3] + '" data-pri="' + (here ? 3 : ic ? 2 : 1) + '" class="ppc-mmap__lbl' + (here ? " is-here" : ic ? " is-ic" : "") + '">' + esc(l[4]) + "</text>";
      });
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


  var LABEL_GAP = 4; /* CSS px: no label may sit closer than this to a line, disc, ring, other label or the frame */
  function distPointSeg(px, py, x1, y1, x2, y2) {
    var dx = x2 - x1, dy = y2 - y1, l2 = dx * dx + dy * dy;
    if (!l2) return Math.hypot(px - x1, py - y1);
    var t = Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / l2));
    return Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy));
  }
  function distRectSeg(r, x1, y1, x2, y2) {
    var d = Infinity, pts = [[r.left, r.top], [r.right, r.top], [r.right, r.bottom], [r.left, r.bottom]];
    for (var i = 0; i < 4; i++) d = Math.min(d, distPointSeg(pts[i][0], pts[i][1], x1, y1, x2, y2));
    function dpr(px, py) {
      var cx = Math.max(r.left, Math.min(r.right, px)), cy = Math.max(r.top, Math.min(r.bottom, py));
      return Math.hypot(px - cx, py - cy);
    }
    d = Math.min(d, dpr(x1, y1), dpr(x2, y2));
    for (var i = 1; i < 6; i++) { var t = i / 6; d = Math.min(d, dpr(x1 + t * (x2 - x1), y1 + t * (y2 - y1))); }
    return d;
  }
  function distRectCircle(r, cx, cy, rad) {
    var px = Math.max(r.left, Math.min(r.right, cx)), py = Math.max(r.top, Math.min(r.bottom, cy));
    return Math.hypot(cx - px, cy - py) - rad;
  }
  function gapRects(a, b) {
    var ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
    var oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
    if (ox > 0 && oy > 0) return -Math.min(ox, oy);
    if (ox > 0) return -oy;
    if (oy > 0) return -ox;
    return Math.sqrt(ox * ox + oy * oy);
  }
  function inflate(r, p) { return { left: r.left - p, right: r.right + p, top: r.top - p, bottom: r.bottom + p }; }
  function screenPath(p) {
    var sw = parseFloat(getComputedStyle(p).strokeWidth) || 4;
    var len = p.getTotalLength(), n = Math.max(12, Math.ceil(len / 3)), pts = [], ctm = p.getScreenCTM();
    for (var i = 0; i <= n; i++) {
      var pt = p.getPointAtLength(len * i / n), sp = new DOMPoint(pt.x, pt.y).matrixTransform(ctm);
      pts.push([sp.x, sp.y]);
    }
    return { pts: pts, hw: sw / 2 };
  }
  function labelFits(r, sb, paths, circles, placed, gap) {
    if (r.left < sb.left + gap || r.right > sb.right + 0.01 - gap || r.top < sb.top + gap || r.bottom > sb.bottom + 0.01 - gap) return false;
    var i, j, P;
    for (i = 0; i < placed.length; i++) if (gapRects(r, placed[i]) < gap) return false;
    for (i = 0; i < circles.length; i++) if (distRectCircle(r, circles[i].x, circles[i].y, circles[i].r) < gap) return false;
    for (i = 0; i < paths.length; i++) {
      P = paths[i];
      for (j = 1; j < P.pts.length; j++) if (distRectSeg(r, P.pts[j - 1][0], P.pts[j - 1][1], P.pts[j][0], P.pts[j][1]) - P.hw < gap) return false;
    }
    return true;
  }
  function placeMetroLabels(svg) {
    if (!svg || !svg.getClientRects().length) return { placed: 0 };
    /* Frame is the padded map card, not the raw viewBox, so labels may use the inner margin. */
    var frameEl = svg.closest(".ppc-mmap, .tp-fullmap__scroller") || svg.parentElement || svg;
    var sb = frameEl.getBoundingClientRect();
    var texts = [].slice.call(svg.querySelectorAll("text"));
    var paths = [].map.call(svg.querySelectorAll("path"), screenPath);
    var circles = [].map.call(svg.querySelectorAll("circle"), function (c) {
      var b = c.getBoundingClientRect();
      return { x: (b.left + b.right) / 2, y: (b.top + b.bottom) / 2, r: Math.max(b.width, b.height) / 2 };
    });
    var strokePad = 0, cs = texts[0] && getComputedStyle(texts[0]);
    if (cs) strokePad = (parseFloat(cs.strokeWidth) || 0) / 2;
    texts.sort(function (a, b) { return (+b.getAttribute("data-pri") || 0) - (+a.getAttribute("data-pri") || 0); });
    texts.forEach(function (t) { t.style.visibility = "hidden"; });
    var placed = [], inv = svg.getScreenCTM().inverse();
    function toUser(x, y) { var p = new DOMPoint(x, y).matrixTransform(inv); return [p.x, p.y]; }
    function setPos(t, x, y, anc, lines) {
      t.setAttribute("text-anchor", anc);
      t.textContent = "";
      if (!lines || lines.length < 2) {
        t.textContent = lines ? lines[0] : t.getAttribute("data-name") || "";
        t.setAttribute("x", x.toFixed(1));
        t.setAttribute("y", y.toFixed(1));
        return;
      }
      var lh = 10;
      for (var i = 0; i < lines.length; i++) {
        var ts = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
        ts.setAttribute("x", x.toFixed(1));
        ts.setAttribute("dy", i === 0 ? "0" : String(lh));
        ts.textContent = lines[i];
        t.appendChild(ts);
      }
      t.setAttribute("x", x.toFixed(1));
      t.setAttribute("y", (y - (lines.length - 1) * lh * 0.35).toFixed(1));
    }
    texts.forEach(function (t) {
      var a = t.closest("a"), cir = a && a.querySelector("circle");
      if (!cir) { t.style.visibility = "visible"; return; }
      if (!t.getAttribute("data-name")) t.setAttribute("data-name", t.textContent.trim());
      var name = t.getAttribute("data-name");
      var words = name.split(/\s+/), wraps = [[name]];
      if (words.length > 1) {
        for (var w = 1; w < words.length; w++) wraps.push([words.slice(0, w).join(" "), words.slice(w).join(" ")]);
      }
      var cb = cir.getBoundingClientRect(), sx = (cb.left + cb.right) / 2, sy = (cb.top + cb.bottom) / 2;
      var ic = a.classList.contains("is-ic");
      var cands = [], dists = [11, 14, 17, 20, 24, 28, 34, 42, 52, 64, 76];
      var dirs = ic
        ? [[1, 1, "start"], [-1, 1, "end"], [1, -1, "start"], [-1, -1, "end"], [0, 1, "middle"], [0, -1, "middle"], [1, 0.35, "start"], [-1, 0.35, "end"], [1, -0.35, "start"], [-1, -0.35, "end"]]
        : [[0, 1, "middle"], [0, -1, "middle"], [1, 1, "start"], [-1, 1, "end"], [1, -1, "start"], [-1, -1, "end"], [1, 0.4, "start"], [-1, 0.4, "end"], [1, -0.4, "start"], [-1, -0.4, "end"]];
      dists.forEach(function (d) {
        dirs.forEach(function (an) { cands.push([sx + an[0] * d, sy + an[1] * d, an[2]]); });
      });
      var ok = false, i, u, ux, r;
      for (u = 0; u < wraps.length && !ok; u++) {
        for (i = 0; i < cands.length; i++) {
          ux = toUser(cands[i][0], cands[i][1]);
          setPos(t, ux[0], ux[1], cands[i][2], wraps[u]);
          t.style.visibility = "visible";
          r = inflate(t.getBoundingClientRect(), strokePad);
          if (labelFits(r, sb, paths, circles, placed, LABEL_GAP)) { placed.push(r); ok = true; break; }
          t.style.visibility = "hidden";
        }
      }
      if (!ok) {
        t.style.visibility = "hidden";
        t.setAttribute("data-unplaced", "1");
        t.setAttribute("aria-hidden", "true");
      } else { t.removeAttribute("data-unplaced"); t.removeAttribute("aria-hidden"); }
    });
        return { placed: placed.length };
  }
  function placeAllMetroLabels() {
    document.querySelectorAll("#ppc-metro .ppc-mmap svg").forEach(placeMetroLabels);
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
        placeAllMetroLabels();
      });
    });
    var ab = nav.querySelector(".ppc-metro__all-btn"), ap = nav.querySelector(".ppc-metro__all");
    ab.addEventListener("click", function () {
      var open = ap.hidden; ap.hidden = !open; ab.setAttribute("aria-expanded", String(open));
      ab.textContent = open ? "Close map" : "All lines";
    });
    centre();
    placeAllMetroLabels();
    var rz; window.addEventListener("resize", function () { clearTimeout(rz); rz = setTimeout(function () { centre(); placeAllMetroLabels(); }, 120); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { centre(); placeAllMetroLabels(); });
    window.addEventListener("load", placeAllMetroLabels);
  }
  window.PPCMetro = { lines: LINES, build: build, placeLabels: placeAllMetroLabels };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", build);
  else build();
})();
