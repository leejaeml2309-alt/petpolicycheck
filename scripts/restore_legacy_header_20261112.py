#!/usr/bin/env python3
"""fix(nav) 2026-11-12 (Marc): bring back the full pastille header (header.top + nav#site-menu
filled by pastilles.js, Menu button) in place of the 6-link ppc-topbar, on every EN/IT/ES page of
site/ and static/. Order lives in pastilles.js (trip-preparation order). No build.py run."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PST_VER = "20261112nav1"
# (key, EN, IT, ES, i18n key, href relative to the language root)
ITEMS = [
    ("map", "World map", "Mappa del mondo", "Mapa mundial", "site.nav.map", "?view=map"),
    ("law", "Rules", "Norme", "Normas", "site.nav.rules", "countries/usa.html#federal"),
    ("flight", "Airlines", "Compagnie aeree", "Aerolíneas", "site.nav.airlines", "airlines/"),
    ("shop", "Products", "Prodotti", "Productos", "site.nav.products", "products/"),
    ("ground", "Rides", "Trasferimenti", "Traslados", "site.nav.rides", "taxi/"),
    ("hotel", "Hotels", "Hotel", "Hoteles", "site.nav.hotels", "hotels/"),
    ("grooming", "Grooming", "Toelettatura", "Peluquería", "site.nav.grooming", "grooming/"),
    ("forum", "Forum", "Forum", "Foro", "site.nav.forum", "forum/"),
    ("veterans", "Veterans", "Veterani", "Veteranos", "site.nav.veterans", "veterans/"),
    ("b2b", "For Business", "Per le aziende", "Para empresas", "site.nav.pro", "pro/"),
]
SUBS = [("Compare", "Confronta", "Comparar", "#compare"), ("Guides", "Guide", "Guías", "#gear"),
        ("Updates", "Aggiornamenti", "Actualizaciones", "updates.html"), ("About", "Chi siamo", "Acerca de", "about.html")]
LANG = {"en": ("Main", "Menu"), "it": ("Navigazione principale", "Menu"), "es": ("Principal", "Menú")}
SVG = ('<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">'
       '<path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>')
CHROME_RE = re.compile(r'<header class="ppc-topbar top"[^>]*>.*?</header>\s*<div class="ppc-drawer-backdrop"[^>]*></div>\s*'
                       r'<aside\b[^>]*class="ppc-drawer".*?</aside>', re.S)
BRAND_RE = re.compile(r'<a\b[^>]*class="brand"[^>]*>.*?</a>', re.S)

def href(tree, lang, rel, target):
    depth = rel.count('/')
    if lang == "en":
        up = "../" * depth
        return (up or "./") + target if target[0] in "?#" else up + target
    base = f"/{lang}/"
    if target[0] in "?#": return base + target
    bare = target.split('#')[0]
    f = ROOT / tree / lang / bare
    ok = f.is_file() or (f / "index.html").is_file()
    return (base if ok else "/") + target

def header(tree, rel, brand, home):
    lang = rel.split('/')[0] if rel.split('/')[0] in ("it", "es") else "en"
    li = {"en": 1, "it": 2, "es": 3}[lang]
    cur = {"airlines/": "flight", "hotels/": "hotel", "taxi/": "ground", "products/": "shop", "forum/": "forum",
           "grooming/": "grooming", "veterans/": "veterans", "pro/": "b2b"}
    bare = rel[3:] if lang != "en" else rel
    links = []
    for k, en, it, es, key, tgt in ITEMS:
        c = ' aria-current="page"' if any(bare.startswith(p) and v == k for p, v in cur.items()) or (k == "law" and bare == "countries/usa.html") else ""
        cls = ' class="nav-biz"' if k == "b2b" else (' class="nav-vet"' if k == "veterans" else "")
        links.append(f'<a{cls} href="{href(tree, lang, rel, tgt)}"{c} data-i18n="{key}">{(en, it, es)[li-1]}</a>')
    for en, it, es, tgt in SUBS:
        links.append(f'<a class="menu-only sub" href="{href(tree, lang, rel, tgt)}">{(en, it, es)[li-1]}</a>')
    aria, menu = LANG[lang]
    cls = "top map-nav" if home else "top"
    return (f'<header class="{cls}"><div class="wrap">\n{brand}\n'
            f'<nav class="nav menu" id="site-menu" aria-label="{aria}">{"".join(links)}</nav>'
            f'<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-menu">{SVG}'
            f'<span data-i18n="site.nav.menu">{menu}</span></button>\n</div></header>')

touched = 0
for tree in ("site", "static"):
    for f in sorted((ROOT / tree).rglob("*.html")):
        rel = f.relative_to(ROOT / tree).as_posix()
        s0 = s = f.read_text(encoding="utf-8")
        m = CHROME_RE.search(s)
        if m:
            brand = BRAND_RE.search(m.group(0)).group(0)
            home = rel in ("index.html", "it/index.html", "es/index.html")
            s = s[:m.start()] + header(tree, rel, brand, home) + s[m.end():]
            if home:
                s = s.replace("body.intro-home>header.ppc-topbar", "body.intro-home>header.top")
        s = re.sub(r'(pastilles\.js)\?v=[^"]*', r'\1?v=' + PST_VER, s)
        if s != s0:
            f.write_text(s, encoding="utf-8"); touched += 1
print("files touched", touched)
