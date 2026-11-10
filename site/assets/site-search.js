/*! PetPolicyCheck site search — vanilla, no deps. Lazy-loads search-index.<lang>.json on first focus. */
(function (global) {
  "use strict";

  var TYPE_ORDER = ["Countries", "Cities", "Airports", "Transport", "Airlines", "Routes", "Guides", "Veterans", "Hotels", "Pro", "Tools", "Legal"];
  var MAX_RESULTS = 10;
  var TYPE_BOOST = {
    Countries: 80, Cities: 90, Airports: 70, Transport: 45,
    Airlines: 35, Routes: 30, Guides: 20, Veterans: 20,
    Hotels: 0, Pro: 8, Tools: 8, Legal: -50
  };
  var TYPE_LABELS = {
    en: {
      Countries: "Countries", Cities: "Cities", Airports: "Airports",
      Transport: "Transport", Airlines: "Airlines", Routes: "Routes",
      Hotels: "Hotels", Guides: "Guides", Veterans: "Veterans",
      Pro: "Pet Desk Pro", Tools: "Tools", Legal: "Legal"
    },
    es: {
      Countries: "Países", Cities: "Ciudades", Airports: "Aeropuertos",
      Transport: "Transporte", Airlines: "Aerolíneas", Routes: "Rutas",
      Hotels: "Hoteles", Guides: "Guías", Veterans: "Veteranos",
      Pro: "Pet Desk Pro", Tools: "Herramientas", Legal: "Legal"
    }
  };
  var ICONS = {
    Routes: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3.5 12a8.5 8.5 0 1 1 15.4 4.9l1.6 1.6-1.4 1.4-1.6-1.6A8.5 8.5 0 0 1 3.5 12zm2 0a6.5 6.5 0 1 0 6.5-6.5A6.5 6.5 0 0 0 5.5 12zm5-4v4.2l3 1.8-.9 1.5-3.6-2.2V8z"/></svg>',
    Airlines: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21 16v-2l-8-5V3.5A1.5 1.5 0 0 0 11.5 2 1.5 1.5 0 0 0 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>',
    Countries: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 2c1.7 0 3.3.5 4.6 1.4L12 12V4zm0 16a8 8 0 0 1-7.5-5.3L12 12l7.5 2.7A8 8 0 0 1 12 20z"/></svg>',
    Cities: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2C8 2 4.5 6 4.5 10.5 4.5 16 12 22 12 22s7.5-6 7.5-11.5C19.5 6 16 2 12 2zm0 8.5A2.5 2.5 0 1 1 14.5 8 2.5 2.5 0 0 1 12 10.5z"/></svg>',
    Airports: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21 16v-2l-8-5V3.5A1.5 1.5 0 0 0 11.5 2 1.5 1.5 0 0 0 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>',
    Transport: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2c-4.5 0-8 1.2-8 4v9c0 1.1.9 2 2 2h1a2 2 0 1 0 4 0h2a2 2 0 1 0 4 0h1c1.1 0 2-.9 2-2V6c0-2.8-3.5-4-8-4zM6.5 17.5A1.5 1.5 0 1 1 8 16a1.5 1.5 0 0 1-1.5 1.5zm11 0A1.5 1.5 0 1 1 19 16a1.5 1.5 0 0 1-1.5 1.5zM6 6h12v5H6z"/></svg>',
    Hotels: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 11V3h16v8h2v10h-2v-3H4v3H2V11h2zm2-6v6h4V5H6zm6 0v6h4V5h-4zm6 0v6h2V5h-2z"/></svg>',
    Tools: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M22.7 19.3l-3.1-3.1a7.5 7.5 0 0 0-9.3-9.3L12 8.5l1.5 1.5 1.6-1.6a5.5 5.5 0 0 1 6.5 6.5L20 16.5l1.5 1.5 1.2-1.2zM3.5 13.5L2 15l7 7 1.5-1.5-7-7z"/></svg>',
    Guides: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm8 1.5V8h4.5L14 3.5zM8 12h8v2H8v-2zm0 4h8v2H8v-2z"/></svg>',
    Veterans: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2l2.4 7.2H22l-6 4.4 2.3 7.2L12 16.8 5.7 20.8 8 13.6 2 9.2h7.6z"/></svg>',
    Pro: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 4h16v4H4zm0 6h16v10H4zm3 3v4h10v-4z"/></svg>',
    Legal: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3 5h18v2H3zm0 6h18v2H3zm0 6h12v2H3z"/></svg>'
  };
  var SEARCH_ICO = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M15.5 14h-.8l-.3-.3A6.5 6.5 0 1 0 14 15.5l.3.3v.8l5 5 1.5-1.5-5-5zm-6 0A4.5 4.5 0 1 1 14 9.5 4.5 4.5 0 0 1 9.5 14z"/></svg>';

  var cache = Object.create(null);

  function norm(s) {
    s = String(s || "").toLowerCase();
    try {
      s = s.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
    } catch (e) {}
    return s.replace(/[^a-z0-9+#.\s-]+/g, " ").replace(/\s+/g, " ").trim();
  }

  function tokens(s) {
    return norm(s).split(" ").filter(function (t) { return t.length > 0; });
  }

  function damerau(a, b) {
    var i, j, la = a.length, lb = b.length;
    if (Math.abs(la - lb) > 2) return 99;
    var m = [];
    for (i = 0; i <= la; i++) {
      m[i] = [i];
    }
    for (j = 0; j <= lb; j++) m[0][j] = j;
    for (i = 1; i <= la; i++) {
      for (j = 1; j <= lb; j++) {
        var cost = a.charCodeAt(i - 1) === b.charCodeAt(j - 1) ? 0 : 1;
        m[i][j] = Math.min(
          m[i - 1][j] + 1,
          m[i][j - 1] + 1,
          m[i - 1][j - 1] + cost
        );
        if (i > 1 && j > 1 && a.charCodeAt(i - 1) === b.charCodeAt(j - 2) && a.charCodeAt(i - 2) === b.charCodeAt(j - 1)) {
          m[i][j] = Math.min(m[i][j], m[i - 2][j - 2] + cost);
        }
      }
    }
    return m[la][lb];
  }

  function fuzzyOk(q, w) {
    if (!q || !w) return false;
    if (q === w) return true;
    // Tight: "paris" must not match "parks". Require length >= 6 and same first letter.
    if (q.charAt(0) !== w.charAt(0)) return false;
    var max = w.length >= 8 ? 2 : (w.length >= 6 ? 1 : 0);
    if (!max) return false;
    return damerau(q, w) <= max;
  }

  function expandQuery(toks, synonyms) {
    var out = toks.slice();
    var phrases = [];
    var seen = Object.create(null);
    var byToken = Object.create(null);
    toks.forEach(function (t) { seen[t] = 1; byToken[t] = []; });
    function addToken(x) {
      if (!x || seen[x]) return;
      // skip ultra-generic expansions that collide with airline names
      if (x === "united" || x === "states" || x === "airlines" || x === "airline") return;
      seen[x] = 1;
      out.push(x);
    }
    function addSynValue(s) {
      var n = norm(s);
      if (!n) return;
      if (n.indexOf(" ") !== -1 || n.indexOf("-") !== -1) phrases.push(n);
      tokens(n).forEach(addToken);
    }
    toks.forEach(function (t) {
      var syns = synonyms[t];
      if (!syns) return;
      syns.forEach(function (s) {
        addSynValue(s);
        var n = norm(s);
        tokens(n).forEach(function (x) {
          if (!x || x === t) return;
          if (!byToken[t]) byToken[t] = [];
          if (byToken[t].indexOf(x) === -1) byToken[t].push(x);
        });
        if (n && n.indexOf(" ") !== -1) {
          if (!byToken[t]) byToken[t] = [];
          if (byToken[t].indexOf(n) === -1) byToken[t].push(n);
        }
      });
    });
    var joined = toks.join(" ");
    Object.keys(synonyms).forEach(function (k) {
      if (k.indexOf(" ") === -1) return;
      if (joined.indexOf(k) !== -1 || k.split(" ").every(function (p) { return seen[p]; })) {
        synonyms[k].forEach(addSynValue);
        phrases.push(k);
      }
    });
    out._phrases = phrases;
    out._byToken = byToken;
    return out;
  }

  function typeLabel(type, lang) {
    var pack = TYPE_LABELS[lang] || TYPE_LABELS.en;
    return pack[type] || type;
  }

  function scorePage(page, qToks, qNorm, expanded) {
    var titleN = norm(page.t);
    var titleToks = tokens(page.t);
    var headN = norm(page.h || "");
    var headToks = tokens(page.h || "");
    var bodyN = norm(page.b || "");
    var urlN = norm(page.u);
    var rawPath = String(page.u || "").toLowerCase();
    var kws = (page.k || []).map(norm);
    var score = 0;
    var exactTitle = false;
    var phrases = expanded._phrases || [];
    var type = page.y || "Guides";

    if (titleN === qNorm || titleN.indexOf(qNorm) === 0) {
      score += 1200;
      exactTitle = true;
    } else if (qNorm.length >= 4 && titleN.indexOf(qNorm) !== -1) {
      score += 900;
      exactTitle = true;
    }
    // Accent / ES aliases: «Londres» matches a title that STARTS with London.
    // Do not treat related places (france, cdg) as a title-exact hit on "Nice — France".
    if (!exactTitle) {
      var aliases = (expanded._phrases || []).concat(expanded.filter ? expanded.filter(function (x) { return x && x !== qNorm; }) : []);
      aliases.forEach(function (al) {
        if (exactTitle || !al || al.length < 4 || /^[a-z]{3}$/.test(al)) return;
        if (titleN === al || titleN.indexOf(al + " ") === 0 || titleN.indexOf(al + "—") === 0 || titleN.indexOf(al + " -") === 0 || titleToks[0] === al) {
          score += 1200;
          exactTitle = true;
        }
      });
    }

    var slug = urlN.replace(/^.*\//, "").replace(/\.html$/, "").replace(/-/g, " ").replace(/#.*$/, "");
    var slugPath = rawPath.split("#")[0];
    if (slug === qNorm) {
      score += 1100;
      exactTitle = true;
    }

    phrases.forEach(function (ph) {
      var ph2 = ph.replace(/-/g, " ");
      if (titleN === ph2 || titleN.indexOf(ph2) === 0) {
        score += 700;
        exactTitle = true;
      }
    });

    function bestField(qt) {
      if (!qt) return null;
      if (titleToks.indexOf(qt) !== -1) return "title";
      if (titleN.indexOf(qt) !== -1 || titleToks.some(function (t) { return t.indexOf(qt) === 0; })) return "title-prefix";
      if (headToks.indexOf(qt) !== -1) return "head";
      if (headN.indexOf(qt) !== -1 || headToks.some(function (t) { return t.indexOf(qt) === 0; })) return "head-prefix";
      if (kws.indexOf(qt) !== -1) return "kw";
      if (kws.some(function (k) { return k.indexOf(qt) === 0; })) return "kw-prefix";
      if (urlN.indexOf(qt) !== -1 || slugPath.indexOf(qt) !== -1) return "url";
      if (bodyN.indexOf(qt) !== -1) return "body";
      if (titleToks.some(function (t) { return fuzzyOk(qt, t); }) ||
          headToks.some(function (t) { return fuzzyOk(qt, t); }) ||
          kws.some(function (k) { return fuzzyOk(qt, k); })) return "fuzzy";
      return null;
    }

    var FIELD_SCORE = {
      title: 280, "title-prefix": 180,
      head: 160, "head-prefix": 100,
      kw: 150, "kw-prefix": 90,
      url: 50, body: 40, fuzzy: 20
    };

    var missing = false;
    qToks.forEach(function (qt) {
      var f = bestField(qt);
      if (!f) {
        // Only synonyms of THIS token (not the whole query) may satisfy AND.
        // Otherwise "new york" → jfk would make any JFK mention satisfy "york".
        var synHit = false;
        var syns = (expanded && expanded._byToken && expanded._byToken[qt]) || [];
        syns.forEach(function (et) {
          if (synHit || et === qt) return;
          if (bestField(et)) synHit = true;
        });
        if (!synHit) missing = true;
        return;
      }
      score += FIELD_SCORE[f] || 0;
      // IATA boost: only real airport codes, never common words like "new"
      var IATA_STOP = {new:1,the:1,and:1,for:1,you:1,all:1,any:1,but:1,not:1,are:1,was:1,usa:1,use:1,our:1,out:1,off:1,can:1,may:1,per:1,pro:1,pet:1,cat:1,dog:1,faq:1};
      if (qt.length === 3 && !IATA_STOP[qt] && (type === "Airports" || /\/airport\//.test(rawPath) || /#[a-z]*hubs/.test(rawPath))) {
        if (rawPath.indexOf("/" + qt) !== -1 || kws.indexOf(qt) !== -1 || titleToks.indexOf(qt) !== -1) score += 400;
      }
    });
    if (missing) return { score: 0, exact: false };

    expanded.forEach(function (et) {
      if (qToks.indexOf(et) !== -1) return;
      var f = bestField(et);
      if (!f) return;
      score += Math.round((FIELD_SCORE[f] || 0) * 0.45);
    });

    // Breed / snub-nosed guide should win for pug/bulldog/brachy queries
    var breedToks = {pug:1, bulldog:1, frenchie:1, persian:1, brachy:1, brachycephalic:1, "snub-nosed":1, "short-nosed":1};
    var wantsBreed = qToks.some(function (t) { return breedToks[t]; }) ||
      (expanded._phrases || []).some(function (ph) { return /snub|brachy|short-nosed/.test(ph); }) ||
      expanded.some(function (t) { return breedToks[t]; });
    if (wantsBreed && String(page.u).indexOf("snub-nosed") !== -1) {
      score += 2000;
      exactTitle = true;
    }

    if (type === "Airlines" && qToks.length === 1 && qToks[0].length <= 3) {
      if (kws.indexOf(qToks[0]) !== -1) score += 300;
    }

    score += (TYPE_BOOST[type] != null ? TYPE_BOOST[type] : 0);
    return { score: score, exact: exactTitle };
  }

  function search(index, query) {
    var qNorm = norm(query);
    if (!qNorm) return [];
    var qToks = tokens(qNorm);
    var expanded = expandQuery(qToks, index.synonyms || {});
    var scored = [];
    (index.pages || []).forEach(function (p) {
      var r = scorePage(p, qToks, qNorm, expanded);
      if (r.score > 0) scored.push({ page: p, score: r.score, exact: r.exact });
    });
    scored.sort(function (a, b) {
      if (b.exact !== a.exact) return b.exact ? 1 : -1;
      if (b.score !== a.score) return b.score - a.score;
      return TYPE_ORDER.indexOf(a.page.y) - TYPE_ORDER.indexOf(b.page.y);
    });
    // Drop only exact URL+title duplicates. CDG and ORY may share #hubs;
    // "Paris — France" may share the country URL.
    var seen = Object.create(null);
    var uniq = [];
    scored.forEach(function (r) {
      var key = r.page.u + "\t" + r.page.t;
      if (seen[key]) return;
      seen[key] = 1;
      uniq.push(r);
    });
    return uniq.slice(0, MAX_RESULTS);
  }

  function group(results) {
    // Keep score order. A type label is shown when the type changes, but
    // weaker same-type hits (Nice/Lyon for « Paris ») must not jump above
    // stronger airports or the country page.
    var out = [];
    results.forEach(function (r) {
      var y = r.page.y || "Guides";
      if (!out.length || out[out.length - 1].type !== y) {
        out.push({ type: y, items: [r] });
      } else {
        out[out.length - 1].items.push(r);
      }
    });
    return out;
  }

  function assetBase(el) {
    var explicit = el.getAttribute("data-index-base");
    if (explicit) return explicit.replace(/\/?$/, "/");
    var scripts = document.querySelectorAll("script[src*='site-search.js']");
    var src = scripts.length ? scripts[scripts.length - 1].getAttribute("src") : "";
    if (src) {
      return src.replace(/site-search\.js.*$/, "");
    }
    return "/assets/";
  }

  var UI = {
    en: {
      clear: "Clear search",
      placeholder: "Search the site…",
      none: "No matches for “{q}”",
      statusOne: "1 suggestion",
      statusMany: "{n} suggestions",
      unavailable: "Search index unavailable"
    },
    es: {
      clear: "Borrar búsqueda",
      placeholder: "Buscar aerolíneas, rutas, hoteles…",
      none: "Sin resultados para “{q}”",
      statusOne: "1 sugerencia",
      statusMany: "{n} sugerencias",
      unavailable: "Índice de búsqueda no disponible"
    }
  };

  function uiFor(lang) {
    return UI[lang] || UI.en;
  }

  function detectLang(root) {
    var fromRoot = root && root.getAttribute("data-lang");
    var fromHtml = document.documentElement.getAttribute("data-ppc-locale") || document.documentElement.lang;
    var lang = (fromRoot || fromHtml || "en").split("-")[0].toLowerCase();
    if (lang === "es" || lang === "en") return lang;
    return lang || "en";
  }

  function loadIndex(base, lang) {
    var key = lang;
    if (cache[key]) return cache[key];
    var url = base + "search-index." + lang + ".json";
    cache[key] = fetch(url, { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("index " + r.status);
        return r.json();
      })
      .catch(function (err) {
        delete cache[key];
        throw err;
      });
    return cache[key];
  }

  function relativeUrl(fromPath, absPath) {
    // Keep absolute-from-root paths; browsers resolve from site root on GH Pages
    return absPath;
  }

  function buildDom(root, opts) {
    opts = opts || {};
    var lang = opts.lang || detectLang(root);
    var uiStr = uiFor(lang);
    var hero = !!opts.hero || root.classList.contains("ppc-search--hero");
    root.classList.add("ppc-search");
    if (hero) root.classList.add("ppc-search--hero");
    root.setAttribute("data-lang", lang);
    root.innerHTML =
      '<div class="ppc-search__box">' +
        '<span class="ppc-search__ico" aria-hidden="true">' + SEARCH_ICO + "</span>" +
        '<input class="ppc-search__input" type="search" autocomplete="off" spellcheck="false" ' +
          'role="combobox" aria-expanded="false" aria-autocomplete="list" aria-controls="' + root.id + '-list" ' +
          'aria-haspopup="listbox" placeholder="' + (opts.placeholder || uiStr.placeholder) + '">' +
        '<button type="button" class="ppc-search__clear" aria-label="' + uiStr.clear + '">×</button>' +
      "</div>" +
      '<div class="ppc-search__panel" id="' + root.id + '-panel" hidden>' +
        '<p class="ppc-search__status" role="status" aria-live="polite"></p>' +
        '<div class="ppc-search__results" id="' + root.id + '-list" role="listbox"></div>' +
      "</div>";
    return {
      input: root.querySelector(".ppc-search__input"),
      clear: root.querySelector(".ppc-search__clear"),
      panel: root.querySelector(".ppc-search__panel"),
      status: root.querySelector(".ppc-search__status"),
      results: root.querySelector(".ppc-search__results"),
      lang: lang,
      uiStr: uiStr
    };
  }

  function render(ui, root, results, query) {
    var box = ui.results;
    box.innerHTML = "";
    if (!query) {
      ui.status.textContent = "";
      close(ui, root);
      return;
    }
    var uiStr = ui.uiStr || uiFor(ui.lang || detectLang(root));
    if (!results.length) {
      ui.status.textContent = uiStr.none.replace("{q}", query);
      box.innerHTML = "";
      open(ui, root);
      return;
    }
    ui.status.textContent = results.length === 1
      ? uiStr.statusOne
      : uiStr.statusMany.replace("{n}", String(results.length));
    var groups = group(results);
    groups.forEach(function (g) {
      var sec = document.createElement("div");
      sec.className = "ppc-search__group";
      var lab = document.createElement("p");
      lab.className = "ppc-search__group-label";
      lab.textContent = typeLabel(g.type, ui.lang || "en");
      sec.appendChild(lab);
      var ul = document.createElement("div");
      ul.className = "ppc-search__list";
      g.items.forEach(function (r) {
        var a = document.createElement("a");
        a.className = "ppc-search__item";
        a.setAttribute("role", "option");
        a.setAttribute("aria-selected", "false");
        a.dataset.type = r.page.y;
        a.href = relativeUrl(location.pathname, r.page.u);
        a.innerHTML =
          '<span class="ppc-search__type">' + (ICONS[r.page.y] || ICONS.Guides) + "</span>" +
          '<span class="ppc-search__title"></span>' +
          '<span class="ppc-search__meta"></span>';
        a.querySelector(".ppc-search__title").textContent = r.page.t;
        a.querySelector(".ppc-search__meta").textContent = typeLabel(r.page.y, ui.lang || "en");
        ul.appendChild(a);
      });
      sec.appendChild(ul);
      box.appendChild(sec);
    });
    open(ui, root);
    setActive(ui, 0);
  }

  function optionsOf(ui) {
    return Array.prototype.slice.call(ui.results.querySelectorAll(".ppc-search__item"));
  }

  function setActive(ui, idx) {
    var opts = optionsOf(ui);
    if (!opts.length) return -1;
    if (idx < 0) idx = opts.length - 1;
    if (idx >= opts.length) idx = 0;
    opts.forEach(function (el, i) {
      el.setAttribute("aria-selected", i === idx ? "true" : "false");
    });
    opts[idx].scrollIntoView({ block: "nearest" });
    ui.input.setAttribute("aria-activedescendant", opts[idx].id || "");
    opts.forEach(function (el, i) {
      if (!el.id) el.id = ui.input.id + "-opt-" + i;
    });
    ui.input.setAttribute("aria-activedescendant", opts[idx].id);
    return idx;
  }

  function open(ui, root) {
    root.classList.add("is-open");
    ui.panel.hidden = false;
    ui.input.setAttribute("aria-expanded", "true");
  }

  function close(ui, root) {
    root.classList.remove("is-open");
    ui.panel.hidden = true;
    ui.input.setAttribute("aria-expanded", "false");
    ui.input.removeAttribute("aria-activedescendant");
  }

  function activeIndex(ui) {
    var opts = optionsOf(ui);
    return opts.findIndex(function (el) { return el.getAttribute("aria-selected") === "true"; });
  }

  function goActive(ui) {
    var opts = optionsOf(ui);
    var i = activeIndex(ui);
    if (i < 0 && opts[0]) i = 0;
    if (i >= 0 && opts[i]) {
      location.href = opts[i].href;
      return true;
    }
    return false;
  }

  function mount(root, opts) {
    if (!root || root.__ppcSearch) return root.__ppcSearch;
    if (!root.id) root.id = "ppc-search-" + Math.random().toString(36).slice(2, 8);
    var lang = (opts && opts.lang) || detectLang(root);
    var ui = buildDom(root, Object.assign({}, opts || {}, { lang: lang }));
    ui.input.id = root.id + "-input";
    var base = assetBase(root);
    var indexPromise = null;
    var lastResults = [];
    var active = 0;
    var debounce = null;

    function ensureIndex() {
      if (!indexPromise) indexPromise = loadIndex(base, lang);
      return indexPromise;
    }

    function run() {
      var q = ui.input.value;
      root.classList.toggle("is-filled", q.length > 0);
      ensureIndex().then(function (index) {
        lastResults = search(index, q);
        render(ui, root, lastResults, norm(q) ? q.trim() : "");
        active = 0;
      }).catch(function () {
        ui.status.textContent = (ui.uiStr || uiFor(lang)).unavailable;
        open(ui, root);
      });
    }

    ui.input.addEventListener("focus", function () { ensureIndex(); if (ui.input.value) run(); });
    ui.input.addEventListener("input", function () {
      clearTimeout(debounce);
      debounce = setTimeout(run, 60);
    });
    ui.clear.addEventListener("click", function () {
      ui.input.value = "";
      root.classList.remove("is-filled");
      close(ui, root);
      ui.input.focus();
    });
    ui.input.addEventListener("keydown", function (e) {
      var opts = optionsOf(ui);
      if (e.key === "ArrowDown") {
        e.preventDefault();
        if (!root.classList.contains("is-open")) run();
        active = setActive(ui, activeIndex(ui) + 1);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        active = setActive(ui, activeIndex(ui) - 1);
      } else if (e.key === "Enter") {
        if (root.classList.contains("is-open") && opts.length) {
          e.preventDefault();
          goActive(ui);
        }
      } else if (e.key === "Escape") {
        if (root.classList.contains("is-open")) {
          e.preventDefault();
          close(ui, root);
        }
      }
    });
    document.addEventListener("click", function (e) {
      if (!root.contains(e.target)) close(ui, root);
    });

    var api = {
      search: function (q) {
        return ensureIndex().then(function (index) { return search(index, q); });
      },
      focus: function () { ui.input.focus(); },
      close: function () { close(ui, root); }
    };
    root.__ppcSearch = api;
    return api;
  }

  function autoMount() {
    document.querySelectorAll("[data-ppc-search]").forEach(function (el) {
      mount(el, {
        hero: el.getAttribute("data-ppc-search") === "hero",
        placeholder: el.getAttribute("data-placeholder") || undefined,
        lang: el.getAttribute("data-lang") || detectLang(el)
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", autoMount);
  } else {
    autoMount();
  }

  global.PPCSearch = {
    mount: mount,
    search: search,
    norm: norm,
    loadIndex: loadIndex,
    _internal: { damerau: damerau, expandQuery: expandQuery, group: group }
  };
})(typeof window !== "undefined" ? window : globalThis);
