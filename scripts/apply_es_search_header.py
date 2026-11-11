#!/usr/bin/env python3
"""Apply compact ES search header to all /es/ HTML pages (site/ + static/).

Hub links prefer /es/ equivalents when they exist; otherwise fall back to EN.
Labels are usted Spanish. Leaves data-ppc-locale / lang and non-header UI alone.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER = "20261110essearch2"

# (href_abs, label, active_prefixes under /es/)
# href_abs is site-root absolute path
HUBS = [
    ("/es/vet-info/", "Info veterinaria", ("es/vet-info/",)),
    ("/es/countries/usa-map.html", "Países/Mapas", ("es/countries/",)),
    ("/es/airlines/compare/", "Aerolíneas", ("es/airlines/",)),
    ("/es/routes/", "Rutas", ("es/routes/",)),
    ("/es/hotels/", "Hoteles", ("es/hotels/",)),
    ("/es/passport/", "Herramientas", ("es/passport/", "es/fit/", "es/pet-travel-checklist/")),
]

HEADER_RE = re.compile(
    r'<header class="(?:top|top map-nav|ppc-topbar top)[^"]*"[^>]*>.*?</header>',
    re.S,
)
DRAWER_RE = re.compile(
    r'\s*<div class="ppc-drawer-backdrop"[^>]*>.*?</div>\s*'
    r'<aside class="ppc-drawer"[^>]*>.*?</aside>',
    re.S,
)
# Legacy inline menu script often right after header on ES pages
LEGACY_MENU_SCRIPT_RE = re.compile(
    r'\s*<script>\(function\(\)\{function init\(\)\{var m=document\.getElementById\(\'site-menu\'\).*?</script>',
    re.S,
)
CSS_LINK_RE = re.compile(r'<link rel="stylesheet" href="[^"]*site-search\.css[^"]*">\s*')
JS_FOOT_RE = re.compile(
    r'\s*<script src="[^"]*site-search\.js[^"]*" defer></script>\s*'
    r'(?:<script src="[^"]*ppc-header\.js[^"]*" defer></script>\s*)?'
)

PH = "Buscar aerolíneas, rutas, hoteles…"
PH_SHORT = "Buscar…"


def rel_root(path: Path, base: Path) -> str:
    depth = len(path.relative_to(base).parts) - 1
    return "" if depth <= 0 else "../" * depth


def page_path_key(path: Path, base: Path) -> str:
    rel = path.relative_to(base).as_posix()
    if rel.endswith("/index.html"):
        return rel[: -len("index.html")]
    return rel


def hub_nav(key: str, mobile: bool = False) -> str:
    bits = []
    for href, label, pre in HUBS:
        cur = ' aria-current="page"' if any(key.startswith(x) for x in pre) else ""
        bits.append(f'<a href="{href}"{cur}>{label}</a>')
    aria = "Navegación principal móvil" if mobile else "Navegación principal"
    return f'<nav class="ppc-nav" aria-label="{aria}">' + "".join(bits) + "</nav>"


def compact_header(asset_root: str, key: str) -> str:
    brand = "/es/"
    return (
        f'<header class="ppc-topbar top" data-ppc-topbar>'
        f'<div class="wrap">'
        f'<a class="brand" href="{brand}" aria-label="PetPolicyCheck — Inicio">'
        f'<span class="lbadge"><img src="{asset_root}assets/img/logo-mark-header.png" width="62" height="48" alt="PetPolicyCheck"></span></a>'
        f'{hub_nav(key, False)}'
        f'<div data-ppc-search data-lang="es" data-index-base="{asset_root}assets/" data-placeholder="{PH}"></div>'
        f'<button class="ppc-burger" type="button" data-ppc-burger aria-expanded="false" aria-controls="ppc-drawer" aria-label="Abrir menú">'
        f'<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>'
        f'<span>Menú</span></button>'
        f'</div></header>\n'
        f'<div class="ppc-drawer-backdrop" data-ppc-drawer-backdrop></div>\n'
        f'<aside class="ppc-drawer" id="ppc-drawer" data-ppc-drawer aria-label="Menú del sitio">\n'
        f'<div class="ppc-drawer__head"><h2>Menú</h2>\n'
        f'<button type="button" class="ppc-drawer__close" data-ppc-drawer-close aria-label="Cerrar menú">×</button></div>\n'
        f'<div data-ppc-search data-lang="es" data-index-base="{asset_root}assets/" data-placeholder="{PH_SHORT}"></div>\n'
        f'{hub_nav(key, True)}\n'
        f'</aside>'
    )


def should_process(path: Path, base: Path) -> bool:
    rel = path.relative_to(base).as_posix()
    return rel == "es/index.html" or rel.startswith("es/")


def patch_html(text: str, asset_root: str, key: str) -> tuple[str, bool]:
    if "data-ppc-locale" not in text and 'lang="es"' not in text[:400]:
        # still process files under /es/
        pass

    body = text
    body = DRAWER_RE.sub("", body)
    m = HEADER_RE.search(body)
    if not m:
        return text, False

    new_h = compact_header(asset_root, key)
    body = body[: m.start()] + new_h + body[m.end() :]
    # Drop legacy burger script tied to #site-menu (now replaced)
    body2 = LEGACY_MENU_SCRIPT_RE.sub("\n", body, count=1)
    body = body2

    css = f'<link rel="stylesheet" href="{asset_root}assets/site-search.css?v={VER}">'
    if "site-search.css" not in body:
        body = body.replace("</head>", css + "\n</head>", 1)
    else:
        body = CSS_LINK_RE.sub(css + "\n", body, count=1)

    foot = (
        f'<script src="{asset_root}assets/site-search.js?v={VER}" defer></script>\n'
        f'<script src="{asset_root}assets/ppc-header.js?v={VER}" defer></script>\n'
    )
    if "site-search.js" not in body:
        body = body.replace("</body>", foot + "</body>", 1)
    else:
        body = JS_FOOT_RE.sub("\n" + foot, body, count=1)

    return body, body != text


def apply_tree(base: Path) -> dict:
    stats = {"patched": 0, "skipped": 0, "no_header": 0}
    for path in sorted(base.rglob("*.html")):
        if not should_process(path, base):
            continue
        asset_root = rel_root(path, base)
        key = page_path_key(path, base)
        raw = path.read_text(encoding="utf-8")
        new, changed = patch_html(raw, asset_root, key)
        if not changed:
            if not HEADER_RE.search(raw):
                stats["no_header"] += 1
            else:
                stats["skipped"] += 1
            continue
        path.write_text(new, encoding="utf-8")
        stats["patched"] += 1
    return stats


def main() -> None:
    s1 = apply_tree(ROOT / "site")
    s2 = apply_tree(ROOT / "static")
    print("site", s1)
    print("static", s2)


if __name__ == "__main__":
    main()
