/*! PetPolicyCheck site search — vanilla, no deps. Lazy-loads search-index.<lang>.json on first focus. */
(function (global) {
  "use strict";

  var TYPE_ORDER = ["Routes", "Airlines", "Countries", "Hotels", "Tools", "Guides"];
  var MAX_RESULTS = 8;
  var ICONS = {
    Routes: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M3.5 12a8.5 8.5 0 1 1 15.4 4.9l1.6 1.6-1.4 1.4-1.6-1.6A8.5 8.5 0 0 1 3.5 12zm2 0a6.5 6.5 0 1 0 6.5-6.5A6.5 6.5 0 0 0 5.5 12zm5-4v4.2l3 1.8-.9 1.5-3.6-2.2V8z"/></svg>',
    Airlines: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M21 16v-2l-8-5V3.5A1.5 1.5 0 0 0 11.5 2 1.5 1.5 0 0 0 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>',
    Countries: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 2c1.7 0 3.3.5 4.6 1.4L12 12V4zm0 16a8 8 0 0 1-7.5-5.3L12 12l7.5 2.7A8 8 0 0 1 12 20z"/></svg>',
    Hotels: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 11V3h16v8h2v10h-2v-3H4v3H2V11h2zm2-6v6h4V5H6zm6 0v6h4V5h-4zm6 0v6h2V5h-2z"/></svg>',
    Tools: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M22.7 19.3l-3.1-3.1a7.5 7.5 0 0 0-9.3-9.3L12 8.5l1.5 1.5 1.6-1.6a5.5 5.5 0 0 1 6.5 6.5L20 16.5l1.5 1.5 1.2-1.2zM3.5 13.5L2 15l7 7 1.5-1.5-7-7z"/></svg>',
    Guides: '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M6 2h9l5 5v13a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2zm8 1.5V8h4.5L14 3.5zM8 12h8v2H8v-2zm0 4h8v2H8v-2z"/></svg>'
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
    var max = w.length >= 8 ? 2 : (w.length >= 4 ? 1 : 0);
    if (!max) return false;
    return damerau(q, w) <= max;
  }

  function expandQuery(toks, synonyms) {
    var out = toks.slice();
    var phrases = [];
    var seen = Object.create(null);
    toks.forEach(function (t) { seen[t] = 1; });
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
      syns.forEach(addSynValue);
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
    return out;
  }

  function scorePage(page, qToks, qNorm, expanded) {
    var titleN = norm(page.t);
    var titleToks = tokens(page.t);
    var urlN = norm(page.u);
    var kws = (page.k || []).map(norm);
    var score = 0;
    var exactTitle = false;
    var phrases = expanded._phrases || [];

    if (titleN === qNorm || titleN.indexOf(qNorm) === 0) {
      score += 1200;
      exactTitle = true;
    }
    // slug / path exact-ish ("usa mexico" ↔ usa-mexico)
    var slug = urlN.replace(/^.*\//, "").replace(/\.html$/, "").replace(/-/g, " ");
    var slugCompact = slug.replace(/\s+/g, "");
    var qCompact = qNorm.replace(/\s+/g, "");
    if (slug === qNorm || slugCompact === qCompact) {
      score += 1400;
      exactTitle = true;
    } else if (slugCompact.indexOf(qCompact) !== -1 && qCompact.length >= 5) {
      score += 900;
      exactTitle = true;
    }
    // overview route pages: /routes/usa-mexico.html beats airline-specific children
    if (page.y === "Routes" && /\/routes\/[a-z0-9-]+\.html$/.test(page.u) && page.u.indexOf("-to-") === -1) {
      if (qToks.length >= 2 && qToks.every(function (t) { return slug.indexOf(t) !== -1 || urlN.indexOf(t) !== -1; })) {
        score += 500;
        exactTitle = true;
      }
    }
    phrases.forEach(function (ph) {
      var ph2 = ph.replace(/-/g, " ");
      if (slug === ph2 || slugCompact === ph.replace(/[\s-]/g, "") || urlN.indexOf(ph.replace(/\s+/g, "-")) !== -1) {
        score += 700;
        exactTitle = true;
      }
    });

    qToks.forEach(function (qt) {
      if (!qt) return;
      if (titleToks.indexOf(qt) !== -1) score += 220;
      else if (titleN.indexOf(qt) === 0 || titleToks.some(function (t) { return t.indexOf(qt) === 0; })) score += 140;
      else if (titleToks.some(function (t) { return fuzzyOk(qt, t); })) score += 70;

      if (kws.indexOf(qt) !== -1) score += 160;
      else if (kws.some(function (k) { return k.indexOf(qt) === 0; })) score += 90;
      else if (kws.some(function (k) { return fuzzyOk(qt, k); })) score += 50;

      if (urlN.indexOf(qt) !== -1) score += 40;
      // IATA / short codes in path (norm() strips slashes, so also check raw path)
      if (qt.length === 3) {
        var rawPath = String(page.u || "").toLowerCase();
        if (rawPath.indexOf("/" + qt) !== -1 || rawPath.indexOf("/" + qt + "/") !== -1) score += 800;
        if (kws.indexOf(qt) !== -1) score += 200;
      }
    });

    expanded.forEach(function (et) {
      if (qToks.indexOf(et) !== -1) return;
      if (titleToks.indexOf(et) !== -1 || kws.indexOf(et) !== -1) score += 100;
      else if (kws.some(function (k) { return k.indexOf(et) === 0; }) || titleToks.some(function (t) { return t.indexOf(et) === 0; })) score += 60;
      else if (urlN.indexOf(et.replace(/\s+/g, "-")) !== -1) score += 40;
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

    if (page.y === "Airlines" && qToks.length === 1 && qToks[0].length <= 3) {
      if (kws.indexOf(qToks[0]) !== -1) score += 300;
    }

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
    // boost exact-ish first page already handled; trim
    return scored.slice(0, MAX_RESULTS);
  }

  function group(results) {
    var map = Object.create(null);
    var best = Object.create(null);
    results.forEach(function (r) {
      var y = r.page.y || "Guides";
      if (!map[y]) map[y] = [];
      map[y].push(r);
      if (best[y] == null || r.score > best[y]) best[y] = r.score;
    });
    // Prefer the type that holds the strongest hit (so exact "pug" → Guides before Airlines)
    var order = Object.keys(map);
    order.sort(function (a, b) {
      var db = (best[b] || 0) - (best[a] || 0);
      if (db) return db;
      return TYPE_ORDER.indexOf(a) - TYPE_ORDER.indexOf(b);
    });
    return order.map(function (y) { return { type: y, items: map[y] }; });
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

  function detectLang(root) {
    var lang = (root.getAttribute("data-lang") || document.documentElement.lang || "en").split("-")[0].toLowerCase();
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
    var hero = !!opts.hero || root.classList.contains("ppc-search--hero");
    root.classList.add("ppc-search");
    if (hero) root.classList.add("ppc-search--hero");
    root.innerHTML =
      '<div class="ppc-search__box">' +
        '<span class="ppc-search__ico" aria-hidden="true">' + SEARCH_ICO + "</span>" +
        '<input class="ppc-search__input" type="search" autocomplete="off" spellcheck="false" ' +
          'role="combobox" aria-expanded="false" aria-autocomplete="list" aria-controls="' + root.id + '-list" ' +
          'aria-haspopup="listbox" placeholder="' + (opts.placeholder || "Search airlines, routes, hotels…") + '">' +
        '<button type="button" class="ppc-search__clear" aria-label="Clear search">×</button>' +
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
      results: root.querySelector(".ppc-search__results")
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
    if (!results.length) {
      ui.status.textContent = "No matches for “" + query + "”";
      box.innerHTML = "";
      open(ui, root);
      return;
    }
    ui.status.textContent = results.length + " suggestion" + (results.length > 1 ? "s" : "");
    var groups = group(results);
    groups.forEach(function (g) {
      var sec = document.createElement("div");
      sec.className = "ppc-search__group";
      var lab = document.createElement("p");
      lab.className = "ppc-search__group-label";
      lab.textContent = g.type;
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
        a.querySelector(".ppc-search__meta").textContent = r.page.y;
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
    var ui = buildDom(root, opts || {});
    ui.input.id = root.id + "-input";
    var base = assetBase(root);
    var lang = detectLang(root);
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
        ui.status.textContent = "Search index unavailable";
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
        placeholder: el.getAttribute("data-placeholder") || undefined
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
