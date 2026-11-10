#!/usr/bin/env python3
"""Remove the Chrome extension, strip leftover booking CSS/i18n, clean static/,
drop preview bars, and write noindex redirects. Does not run build.py."""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from apply_notravel import process_html  # noqa: E402

PREVIEW_BAR_RE = re.compile(
    r'<div class="ppc-preview-bar"[^>]*>[\s\S]*?</div>\s*',
    re.I,
)
FOOT_EXT_RE = re.compile(
    r'<li>\s*<a\b[^>]*(?:/extension/?|site\.foot\.extension)[^>]*>[\s\S]*?</a>\s*</li>',
    re.I,
)
# preview-injected robots, including the broken name=\"robots\" form
INJECTED_ROBOTS_RE = re.compile(
    r'\n?<meta\s+name=\\?"robots\\?"\s+content=\\?"noindex,\s*nofollow\\?">\s*',
    re.I,
)
BOOK_BTNS_RULE_RE = re.compile(r'\.book-btns(?:\s+\.btn)?[^{]*\{[^}]*\}')
JP_HS_RULE_RE = re.compile(r'\.jp-hs[^{]*\{[^}]*\}')

REDIRECT_KEEP = {
    "book/index.html",
    "extension/index.html",
}
RESTORE_ROBOTS = {
    "advertise/index.html": '<meta name="robots" content="noindex,nofollow">',
    "field-guides/advertise.html": '<meta name="robots" content="noindex,nofollow">',
    "forum/account.html": '<meta name="robots" content="noindex,follow">',
    "forum/admin.html": '<meta name="robots" content="noindex,follow">',
    "forum/new.html": '<meta name="robots" content="noindex,follow">',
    "forum/post.html": '<meta name="robots" content="noindex,follow">',
    "forum/partners.html": '<meta name="robots" content="noindex,nofollow">',
}

BOOK_REDIRECT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0; url=../hotels/">
<link rel="canonical" href="https://petpolicycheck.com/hotels/">
<title>Redirecting to pet-friendly hotel information</title>
<script>location.replace("../hotels/");</script>
</head>
<body>
<p><a href="../hotels/">Continue to pet-friendly hotel information</a></p>
</body>
</html>
"""

EXT_REDIRECT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex, nofollow">
<meta http-equiv="refresh" content="0; url=../passport/">
<link rel="canonical" href="https://petpolicycheck.com/passport/">
<title>Redirecting to the pet travel passport</title>
<script>location.replace("../passport/");</script>
</head>
<body>
<p><a href="../passport/">Continue to the pet travel passport</a></p>
</body>
</html>
"""


def write_redirect(tree: Path, rel: str, html: str) -> None:
    dest = tree / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")


def fix_style_css(text: str) -> str:
    text = text.replace("p.book-btns,p.buy{", "p.buy{")
    text = text.replace("p.book-btns .btn,p.buy .btn{", "p.buy .btn{")
    text = BOOK_BTNS_RULE_RE.sub("", text)
    text = JP_HS_RULE_RE.sub("", text)
    return text


def strip_preview_and_extension(html: str, rel: str) -> tuple[str, dict]:
    stats = {"preview_bar": 0, "foot_ext": 0, "robots_stripped": 0, "book_btns": 0, "jp_hs": 0}
    html, n = PREVIEW_BAR_RE.subn("", html)
    stats["preview_bar"] += n
    html, n = FOOT_EXT_RE.subn("", html)
    stats["foot_ext"] += n
    html, n = INJECTED_ROBOTS_RE.subn("\n", html)
    stats["robots_stripped"] += n
    if rel in RESTORE_ROBOTS:
        tag = RESTORE_ROBOTS[rel]
        if "name=\"robots\"" not in html and "name='robots'" not in html:
            html = re.sub(r"(<head\b[^>]*>)", r"\1\n" + tag, html, count=1, flags=re.I)
    html, n = BOOK_BTNS_RULE_RE.subn("", html)
    stats["book_btns"] += n
    html, n = JP_HS_RULE_RE.subn("", html)
    stats["jp_hs"] += n
    html = html.replace(' class="book-btns"', "")
    html = html.replace(" class='book-btns'", "")
    html = html.replace("p.book-btns,p.buy{", "p.buy{")
    html = html.replace("p.book-btns .btn,p.buy .btn{", "p.buy .btn{")
    return html, stats


def process_tree(tree: Path, strip_affiliates: bool) -> dict:
    totals = {}
    changed = 0
    skipped_unpacked = 0
    for fp in sorted(tree.rglob("*.html")):
        rel = fp.relative_to(tree).as_posix()
        if "extension/unpacked" in rel:
            skipped_unpacked += 1
            continue
        if rel == "book/index.html":
            write_redirect(tree, rel, BOOK_REDIRECT)
            changed += 1
            totals["book_redirect"] = totals.get("book_redirect", 0) + 1
            continue
        if rel == "extension/index.html":
            write_redirect(tree, rel, EXT_REDIRECT)
            changed += 1
            totals["ext_redirect"] = totals.get("ext_redirect", 0) + 1
            continue
        raw = fp.read_text(encoding="utf-8", errors="replace")
        html = raw
        if strip_affiliates:
            html, st = process_html(html, rel, preview=False)
            for k, v in st.items():
                totals[k] = totals.get(k, 0) + v
        html, st = strip_preview_and_extension(html, rel)
        for k, v in st.items():
            totals[k] = totals.get(k, 0) + v
        if html != raw:
            fp.write_text(html, encoding="utf-8")
            changed += 1
    totals["files_changed"] = changed
    totals["skipped_unpacked"] = skipped_unpacked
    return totals


def patch_sitemap(path: Path) -> int:
    if not path.exists():
        return 0
    t = path.read_text(encoding="utf-8")
    nt, n1 = re.subn(r"<url>\s*<loc>https://petpolicycheck.com/book/</loc>[\s\S]*?</url>", "", t)
    nt, n2 = re.subn(r"<url>\s*<loc>https://petpolicycheck.com/extension/</loc>[\s\S]*?</url>", "", nt)
    if n1 or n2:
        path.write_text(nt, encoding="utf-8")
    return n1 + n2


def delete_extension_binaries() -> list[str]:
    removed = []
    for rel in [
        "site/extension/unpacked",
        "static/extension/unpacked",
        "site/downloads/pets-allowed-chrome-extension-v1.zip",
        "site/downloads/pets-allowed-chrome-extension-v1.0.1.zip",
        "static/downloads/pets-allowed-chrome-extension-v1.zip",
        "static/downloads/pets-allowed-chrome-extension-v1.0.1.zip",
    ]:
        p = ROOT / rel
        if p.is_dir():
            shutil.rmtree(p)
            removed.append(rel + "/")
        elif p.exists():
            p.unlink()
            removed.append(rel)
    return removed


def drop_i18n_keys() -> None:
    keys = ("site.foot.book", "site.nav.book")

    def scrub_obj(data: dict) -> int:
        n = 0
        strings = data.get("strings", {})
        for lang, blob in strings.items():
            if not isinstance(blob, dict):
                continue
            for k in keys:
                if k in blob:
                    del blob[k]
                    n += 1
        return n

    p = ROOT / "data/i18n/ui.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    n = scrub_obj(data)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ui.json removed {n} keys")

    for js_path in [ROOT / "site/assets/i18n/ui.js", ROOT / "static/assets/i18n/ui.js"]:
        raw = js_path.read_text(encoding="utf-8")
        prefix = "window.PPC_I18N="
        if not raw.startswith(prefix):
            # try to locate
            idx = raw.find("{")
            payload = raw[idx:]
            tail = ""
            if payload.rstrip().endswith(";"):
                payload = payload.rstrip()[:-1]
            data = json.loads(payload)
            n = scrub_obj(data)
            js_path.write_text(prefix + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")
            print(f"{js_path.relative_to(ROOT)} rebuilt, removed {n} keys")
        else:
            payload = raw[len(prefix):]
            if payload.rstrip().endswith(";"):
                payload = payload.rstrip()[:-1]
            data = json.loads(payload)
            n = scrub_obj(data)
            js_path.write_text(prefix + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")
            print(f"{js_path.relative_to(ROOT)} rebuilt, removed {n} keys")


def scrub_ui_strings() -> None:
    for rel in ["site/es/ui_strings_es.json", "static/es/ui_strings_es.json"]:
        p = ROOT / rel
        if not p.exists():
            continue
        data = json.loads(p.read_text(encoding="utf-8"))
        if "Chrome Extension" in data:
            del data["Chrome Extension"]
            p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"removed Chrome Extension key from {rel}")


def patch_css_files() -> None:
    for rel in ["site/style.css", "static/style.css"]:
        p = ROOT / rel
        old = p.read_text(encoding="utf-8")
        new = fix_style_css(old)
        if new != old:
            p.write_text(new, encoding="utf-8")
            print(f"patched {rel}")


def main() -> None:
    print("=== site/ (preview bar + extension + extra CSS; affiliates already stripped) ===")
    print(process_tree(ROOT / "site", strip_affiliates=False))
    print("=== static/ (full affiliate strip + extension + CSS) ===")
    print(process_tree(ROOT / "static", strip_affiliates=True))
    n1 = patch_sitemap(ROOT / "site/sitemap.xml")
    n2 = patch_sitemap(ROOT / "static/sitemap.xml")
    print(f"sitemap urls removed: site={n1} static={n2}")
    removed = delete_extension_binaries()
    print("removed files/dirs:", removed)
    drop_i18n_keys()
    scrub_ui_strings()
    patch_css_files()


if __name__ == "__main__":
    main()
