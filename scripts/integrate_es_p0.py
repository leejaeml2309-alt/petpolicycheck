#!/usr/bin/env python3
"""Integrate Spanish P0 pages under site/es/ and static/es/ (local preview only)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path("/workspace/es-p0-preview-20261109")
SRC = Path("/workspace/traduction/es-site-p0-20261109")
LIVE = "https://petpolicycheck.com"

PAGES = [
    "index.html",
    "countries/mexico.html",
    "countries/mexico-map.html",
    "routes/usa-mexico.html",
    "routes/usa-to-mexico-alaska.html",
    "routes/usa-to-mexico-american.html",
    "routes/usa-to-mexico-delta.html",
    "routes/usa-to-mexico-united.html",
    "routes/mexico-to-usa-alaska.html",
    "routes/mexico-to-usa-american.html",
    "routes/mexico-to-usa-delta.html",
    "routes/mexico-to-usa-united.html",
    "airlines/aeromexico.html",
    "airlines/volaris.html",
    "airlines/viva-aerobus.html",
    "airlines/delta.html",
    "airlines/united.html",
    "airlines/american.html",
    "airlines/alaska.html",
    "airlines/compare/index.html",
    "passport/index.html",
]

ES_SET = set(PAGES)


def es_exists(path: str) -> bool:
    """path like /, /airlines/delta.html, airlines/compare/, passport/"""
    p = path.split("#", 1)[0].split("?", 1)[0]
    if not p or p == "/":
        return True
    p = p.lstrip("/")
    if p in ES_SET:
        return True
    if p.endswith("/") and (p + "index.html") in ES_SET:
        return True
    if not p.endswith(".html") and (p + ".html") in ES_SET:
        return True
    if not p.endswith(".html") and not p.endswith("/") and (p + "/index.html") in ES_SET:
        return True
    return False


def to_es_path(en_path: str) -> str:
    p = en_path
    if p.startswith(LIVE):
        p = p[len(LIVE):]
    if not p.startswith("/"):
        p = "/" + p
    if p in ("", "/"):
        return "/es/"
    return "/es" + p


def is_asset(url: str) -> bool:
    path = url.split("?", 1)[0].split("#", 1)[0]
    if re.search(r"\.(css|js|mjs|png|jpe?g|gif|webp|svg|ico|woff2?|ttf|otf|map|json)$", path, re.I):
        return True
    if "/assets/" in path or path.startswith("assets/") or path.endswith("style.css") or "/fonts/" in path:
        return True
    if "data-partner" in path or "/partners/" in path:
        return True
    return False


def bump_asset(url: str) -> str:
    if url.startswith(("http://", "https://", "//", "/", "data:", "mailto:")):
        return url
    if url.startswith("./"):
        return "../" + url[2:]
    if url.startswith("../") or not url.startswith("."):
        return "../" + url
    return "../" + url


def rewrite_assets(html: str) -> str:
    def repl(m: re.Match) -> str:
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if not is_asset(url) and attr.lower() != "data-partner-root":
            return m.group(0)
        if url.startswith(("http://", "https://", "//", "/", "data:")):
            return m.group(0)
        return f"{attr}={q}{bump_asset(url)}{q}"

    html = re.sub(
        r'\b(href|src|poster|data-partner-root)=(["\'])([^"\']+)\2',
        repl,
        html,
        flags=re.I,
    )

    def srcset_repl(m: re.Match) -> str:
        attr, q, val = m.group(1), m.group(2), m.group(3)
        out = []
        for chunk in val.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            bits = chunk.split()
            if bits and not bits[0].startswith(("http", "/", "data:")):
                bits[0] = bump_asset(bits[0])
            out.append(" ".join(bits))
        return f"{attr}={q}{', '.join(out)}{q}"

    html = re.sub(r'\b(srcset|imagesrcset)=(["\'])([^"\']+)\2', srcset_repl, html, flags=re.I)
    return html


def split_url(url: str):
    path, frag, query = url, "", ""
    if "#" in path:
        path, frag = path.split("#", 1)
        frag = "#" + frag
    if "?" in path:
        path, query = path.split("?", 1)
        query = "?" + query
    return path, query, frag


def rewrite_nav_links(html: str, rel: str) -> str:
    """Rewrite non-asset hrefs so ES targets stay under /es/, others go to EN absolutes.

    Source HTML was written for EN paths (passport/ → ../book/). Under es/passport/
    the same relative ../book/ correctly reaches EN /book/, and ../airlines/compare/
    correctly reaches /es/airlines/compare/. So relative nav links need NO bump.
    Only absolute https://petpolicycheck.com/... links to ES pages need /es/ prefix.
    Also brand/home links that are '/' or bare should become /es/.
    """

    # Page logical dir under es/, used to resolve relatives for existence checks
    page_url = "/es/" + rel.replace("\\", "/")
    if page_url.endswith("index.html"):
        base_url = page_url[: -len("index.html")]
    else:
        base_url = page_url.rsplit("/", 1)[0] + "/"

    def map_href(url: str) -> str:
        if not url or url.startswith(("mailto:", "tel:", "#", "data:", "javascript:", "?")):
            return url
        if is_asset(url):
            return url

        # Live absolute
        if url.startswith(LIVE):
            path, query, frag = split_url(url[len(LIVE):] or "/")
            if not path.startswith("/"):
                path = "/" + path
            if es_exists(path):
                return LIVE + to_es_path(path) + query + frag
            return url

        # Site-absolute
        if url.startswith("/"):
            path, query, frag = split_url(url)
            if es_exists(path):
                return to_es_path(path) + query + frag
            return url

        # Relative — resolve against /es/<dir>/ to see where it lands
        path, query, frag = split_url(url)
        resolved = urljoin(base_url, path)
        # resolved like /es/book/ or /es/airlines/compare/ or /es/ or /book/ (if ../../)
        if resolved.startswith("/es/") or resolved == "/es":
            en = resolved[3:] or "/"
            if not en.startswith("/"):
                en = "/" + en
            if es_exists(en):
                return url  # keep relative; lands on ES page
            # Missing ES page — jump to EN absolute
            return en + query + frag

        # Resolved outside /es (too many ../) — keep as-is (already EN)
        return url

    def repl(m: re.Match) -> str:
        q, url = m.group(1), m.group(2)
        if is_asset(url):
            return m.group(0)
        new = map_href(url)
        return f"href={q}{new}{q}"

    return re.sub(r'\bhref=(["\'])([^"\']+)\1', repl, html, flags=re.I)


def set_canonical_and_hreflang(html: str, rel: str) -> str:
    en_path = "/" if rel == "index.html" else "/" + rel
    if en_path.endswith("/index.html"):
        en_path = en_path[: -len("index.html")]
    es_path = to_es_path(en_path)
    en_url = LIVE + (en_path if en_path != "/" else "/")
    es_url = LIVE + es_path

    if re.search(r'rel=["\']canonical["\']', html, re.I):
        html = re.sub(
            r'<link[^>]+rel=["\']canonical["\'][^>]*>',
            f'<link href="{es_url}" rel="canonical"/>',
            html,
            count=1,
            flags=re.I,
        )
    else:
        html = re.sub(r"(<head[^>]*>)", r'\1\n<link href="' + es_url + '" rel="canonical"/>', html, count=1, flags=re.I)

    html = re.sub(r'<link[^>]+hreflang=["\'][^"\']+["\'][^>]*>\s*', "", html, flags=re.I)
    block = (
        f'<link rel="alternate" hreflang="en" href="{en_url}"/>\n'
        f'<link rel="alternate" hreflang="es" href="{es_url}"/>\n'
        f'<link rel="alternate" hreflang="x-default" href="{en_url}"/>\n'
    )
    html = re.sub(
        r'(<link[^>]+rel=["\']canonical["\'][^>]*>)',
        r"\1\n" + block,
        html,
        count=1,
        flags=re.I,
    )

    html = re.sub(
        r'(property=["\']og:url["\']\s+content=["\'])([^"\']+)(["\'])',
        r"\1" + es_url + r"\3",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'(content=["\'])([^"\']+)(["\']\s+property=["\']og:url["\'])',
        r"\1" + es_url + r"\3",
        html,
        flags=re.I,
    )

    html = re.sub(r'(<html[^>]*\blang=["\'])[^"\']+(["\'])', r"\1es\2", html, count=1, flags=re.I)
    if not re.search(r"<html[^>]*\blang=", html, re.I):
        html = re.sub(r"<html\b", '<html lang="es"', html, count=1, flags=re.I)
    if "data-ppc-locale=" not in html:
        html = re.sub(r"(<html\b)", r'\1 data-ppc-locale="es"', html, count=1, flags=re.I)
    return html


def add_hreflang_to_en(en_file: Path, rel: str) -> None:
    if not en_file.exists():
        print("WARN missing EN", en_file)
        return
    html = en_file.read_text(encoding="utf-8")
    en_path = "/" if rel == "index.html" else "/" + rel
    if en_path.endswith("/index.html"):
        en_path = en_path[: -len("index.html")]
    es_path = to_es_path(en_path)
    en_url = LIVE + (en_path if en_path != "/" else "/")
    es_url = LIVE + es_path

    html2 = re.sub(
        r'<link[^>]+rel=["\']alternate["\'][^>]+hreflang=["\'](en|es|x-default)["\'][^>]*>\s*',
        "",
        html,
        flags=re.I,
    )
    html2 = re.sub(
        r'<link[^>]+hreflang=["\'](en|es|x-default)["\'][^>]*rel=["\']alternate["\'][^>]*>\s*',
        "",
        html2,
        flags=re.I,
    )
    block = (
        f'<link rel="alternate" hreflang="en" href="{en_url}"/>\n'
        f'<link rel="alternate" hreflang="es" href="{es_url}"/>\n'
        f'<link rel="alternate" hreflang="x-default" href="{en_url}"/>\n'
    )
    if re.search(r'rel=["\']canonical["\']', html2, re.I):
        html2 = re.sub(
            r'(<link[^>]+rel=["\']canonical["\'][^>]*>)',
            r"\1\n" + block,
            html2,
            count=1,
            flags=re.I,
        )
    else:
        html2 = re.sub(r"(<head[^>]*>)", r"\1\n" + block, html2, count=1, flags=re.I)
    if html2 != html:
        en_file.write_text(html2, encoding="utf-8")


def process_page(rel: str) -> None:
    html = (SRC / rel).read_text(encoding="utf-8")
    html = rewrite_assets(html)
    html = rewrite_nav_links(html, rel)
    html = set_canonical_and_hreflang(html, rel)
    for base in (ROOT / "site" / "es", ROOT / "static" / "es"):
        dest = base / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
    print("wrote", rel)


def main() -> None:
    for p in (ROOT / "site" / "es", ROOT / "static" / "es"):
        if p.exists():
            shutil.rmtree(p)
        p.mkdir(parents=True)
    for rel in PAGES:
        process_page(rel)
    for rel in PAGES:
        add_hreflang_to_en(ROOT / "site" / rel, rel)
        st = ROOT / "static" / rel
        if st.exists():
            add_hreflang_to_en(st, rel)
    shutil.copy2(SRC / "ui_strings_es.json", ROOT / "site" / "es" / "ui_strings_es.json")
    print("done", len(PAGES))


if __name__ == "__main__":
    main()
