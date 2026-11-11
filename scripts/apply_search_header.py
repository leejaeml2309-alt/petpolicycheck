#!/usr/bin/env python3
"""Apply compact search header to EN HTML pages (not /es/). In-place for site/ + static/."""
from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VER = "20261110search3"
HUBS = [
    ("/vet-info/", "Vet info", ("vet-info/",)),
    ("countries/usa-map.html", "Countries/Maps", ("countries/",)),
    ("airlines/", "Airlines", ("airlines/",)),
    ("routes/", "Routes", ("routes/",)),
    ("hotels/", "Hotels", ("hotels/",)),
    ("passport/", "Tools", ("passport/", "fit/", "titer-calculator/", "widgets/", "pet-travel-checklist/")),
]
SKIP_DIR_PARTS = {"es", "forum"}  # leave /es/ untouched; forum admin pages often special
SKIP_NAMES = {"_search-preview.html"}
HEADER_RE = re.compile(
    r'<header class="(?:top|top map-nav|ppc-topbar top)[^"]*"[^>]*>.*?</header>',
    re.S,
)
# Also remove leftover drawer from prior preview patches before re-inserting
DRAWER_RE = re.compile(
    r'\s*<div class="ppc-drawer-backdrop"[^>]*>.*?</div>\s*'
    r'<aside class="ppc-drawer"[^>]*>.*?</aside>',
    re.S,
)
CSS_LINK_RE = re.compile(r'<link rel="stylesheet" href="[^"]*site-search\.css[^"]*">\s*')
JS_FOOT_RE = re.compile(
    r'\s*<script src="[^"]*site-search\.js[^"]*" defer></script>\s*'
    r'(?:<script src="[^"]*ppc-header\.js[^"]*" defer></script>\s*)?'
)


def rel_root(path: Path, base: Path) -> str:
    depth = len(path.relative_to(base).parts) - 1
    return "" if depth <= 0 else "../" * depth


def page_path_key(path: Path, base: Path) -> str:
    rel = path.relative_to(base).as_posix()
    if rel.endswith("/index.html"):
        return rel[: -len("index.html")]
    return rel


def hub_nav(root: str, key: str, mobile=False) -> str:
    bits = []
    for href, label, pre in HUBS:
        cur = ' aria-current="page"' if any(key.startswith(x) for x in pre) else ""
        url = href if href.startswith("/") else f"{root}{href}"
        bits.append(f'<a href="{url}"{cur}>{label}</a>')
    aria = "Primary mobile" if mobile else "Primary"
    return f'<nav class="ppc-nav" aria-label="{aria}">' + "".join(bits) + "</nav>"


def compact_header(root: str, key: str) -> str:
    ph = "Search airlines, routes, hotels…"
    return (
        f'<header class="ppc-topbar top" data-ppc-topbar>'
        f'<div class="wrap">'
        f'<a class="brand" href="{root or "./"}" aria-label="PetPolicyCheck — Home">'
        f'<span class="lbadge"><img src="{root}assets/img/logo-mark-header.png" width="62" height="48" alt="PetPolicyCheck"></span></a>'
        f'{hub_nav(root, key, False)}'
        f'<div data-ppc-search data-index-base="{root}assets/" data-placeholder="{ph}"></div>'
        f'<button class="ppc-burger" type="button" data-ppc-burger aria-expanded="false" aria-controls="ppc-drawer">'
        f'<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>'
        f'<span>Menu</span></button>'
        f'</div></header>\n'
        f'<div class="ppc-drawer-backdrop" data-ppc-drawer-backdrop></div>\n'
        f'<aside class="ppc-drawer" id="ppc-drawer" data-ppc-drawer aria-label="Site menu">\n'
        f'<div class="ppc-drawer__head"><h2>Menu</h2>\n'
        f'<button type="button" class="ppc-drawer__close" data-ppc-drawer-close aria-label="Close menu">×</button></div>\n'
        f'<div data-ppc-search data-index-base="{root}assets/" data-placeholder="Search…"></div>\n'
        f'{hub_nav(root, key, True)}\n'
        f'</aside>'
    )


def should_skip(path: Path, base: Path) -> bool:
    rel = path.relative_to(base)
    if path.name in SKIP_NAMES:
        return True
    parts = set(rel.parts)
    if "es" in parts:
        return True
    # leave forum account/admin/new/post alone (noindex tools)
    if "forum" in parts and path.name in {"account.html", "admin.html", "new.html", "post.html"}:
        return True
    return False


def patch_html(text: str, root: str, key: str) -> tuple[str, bool]:
    if "class=\"top map-nav\"" in text or "class='top map-nav'" in text:
        # Home: keep language selector + map nav; inject search assets only beside existing header
        # Do not replace home header (language selector lives here).
        changed = False
        css = f'<link rel="stylesheet" href="{root}assets/site-search.css?v={VER}">'
        if "site-search.css" not in text:
            text = text.replace("</head>", css + "\n</head>", 1)
            changed = True
        else:
            text2 = CSS_LINK_RE.sub(css + "\n", text, count=1)
            if text2 != text:
                text = text2
                changed = True
        foot = (
            f'<script src="{root}assets/site-search.js?v={VER}" defer></script>\n'
            f'<script src="{root}assets/ppc-header.js?v={VER}" defer></script>\n'
        )
        if "site-search.js" not in text:
            text = text.replace("</body>", foot + "</body>", 1)
            changed = True
        else:
            text2 = JS_FOOT_RE.sub("\n" + foot, text, count=1)
            if text2 != text:
                text = text2
                changed = True
        # Insert compact search into home top map-nav wrap if missing
        if "data-ppc-search" not in text and '<header class="top map-nav">' in text:
            # After brand, before nav — add hubs+search soft fail: skip structural change on home
            pass
        return text, changed

    m = HEADER_RE.search(text)
    if not m:
        return text, False
    # strip old drawer if header already converted
    body = text
    body = DRAWER_RE.sub("", body)
    m = HEADER_RE.search(body)
    if not m:
        return text, False
    new_h = compact_header(root, key)
    body = body[: m.start()] + new_h + body[m.end() :]
    css = f'<link rel="stylesheet" href="{root}assets/site-search.css?v={VER}">'
    if "site-search.css" not in body:
        body = body.replace("</head>", css + "\n</head>", 1)
    else:
        body = CSS_LINK_RE.sub(css + "\n", body, count=1)
    foot = (
        f'<script src="{root}assets/site-search.js?v={VER}" defer></script>\n'
        f'<script src="{root}assets/ppc-header.js?v={VER}" defer></script>\n'
    )
    if "site-search.js" not in body:
        body = body.replace("</body>", foot + "</body>", 1)
    else:
        body = JS_FOOT_RE.sub("\n" + foot, body, count=1)
    # Remove obsolete menu-btn only headers leftovers already replaced
    return body, body != text


def apply_tree(base: Path) -> dict:
    stats = {"patched": 0, "skipped": 0, "home_assets": 0, "no_header": 0}
    for path in sorted(base.rglob("*.html")):
        if should_skip(path, base):
            stats["skipped"] += 1
            continue
        root = rel_root(path, base)
        key = page_path_key(path, base)
        raw = path.read_text(encoding="utf-8")
        new, changed = patch_html(raw, root, key)
        if not changed:
            if "map-nav" in raw:
                stats["home_assets"] += 0
            elif not HEADER_RE.search(raw):
                stats["no_header"] += 1
            continue
        path.write_text(new, encoding="utf-8")
        stats["patched"] += 1
        if "map-nav" in raw:
            stats["home_assets"] += 1
    return stats


def main():
    # delete preview page
    for base in (ROOT / "site", ROOT / "static"):
        prev = base / "_search-preview.html"
        if prev.exists():
            prev.unlink()
            print("removed", prev)
    s1 = apply_tree(ROOT / "site")
    s2 = apply_tree(ROOT / "static")
    print("site", s1)
    print("static", s2)


if __name__ == "__main__":
    main()
