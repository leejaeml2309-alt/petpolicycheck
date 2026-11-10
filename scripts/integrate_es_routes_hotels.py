#!/usr/bin/env python3
"""Integrate Traducteur ES routes+hotels under site/es/ and static/es/ (preview only)."""
from __future__ import annotations

import re
import shutil
from pathlib import Path
from urllib.parse import urljoin
from datetime import date

ROOT = Path("/workspace/es-routes-hotels-preview-20261110")
SRC = Path("/workspace/traduction/es-routes-hotels-20261110")
LIVE = "https://petpolicycheck.com"
TODAY = date.today().isoformat()
PREVIEW_BAR = (
    '<div class="ppc-preview-bar" role="status" '
    'style="position:sticky;top:0;z-index:9999;background:#7a1f1f;color:#fff;'
    'font:600 13px/1.35 Inter,system-ui,sans-serif;padding:8px 12px;text-align:center">'
    "LOCAL PREVIEW ONLY — /es/routes/ + /es/hotels/ · await Marc « publie »</div>\n"
)
NOINDEX = '<meta name="robots" content="noindex,nofollow">\n'
SNUB_ABS = "/es/airlines/snub-nosed-breeds.html"

# Manifest pages
PAGES: list[str] = []
with (SRC / "manifest.tsv").open(encoding="utf-8") as f:
    next(f)
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3 and parts[2]:
            PAGES.append(parts[2])

# All ES pages that will exist after this integrate (existing + new)
EXISTING_ES = {
    p.relative_to(ROOT / "site" / "es").as_posix()
    for p in (ROOT / "site" / "es").rglob("*.html")
}
ES_SET = set(EXISTING_ES) | set(PAGES)


def es_exists(path: str) -> bool:
    p = path.split("#", 1)[0].split("?", 1)[0].lstrip("/")
    if not p or p == "es" or p.startswith("es/"):
        # already under es
        if p in ("", "es", "es/"):
            return True
        inner = p[3:] if p.startswith("es/") else p
        return es_exists("/" + inner)
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
        p = p[len(LIVE) :]
    if not p.startswith("/"):
        p = "/" + p
    if p in ("", "/"):
        return "/es/"
    if p.startswith("/es/") or p == "/es":
        return p if p.endswith("/") or p.endswith(".html") else p
    return "/es" + p


def is_asset(url: str) -> bool:
    path = url.split("?", 1)[0].split("#", 1)[0]
    if re.search(
        r"\.(css|js|mjs|png|jpe?g|gif|webp|svg|ico|woff2?|ttf|otf|map|json)$",
        path,
        re.I,
    ):
        return True
    if "/assets/" in path or path.startswith("assets/") or path.endswith("style.css") or "/fonts/" in path:
        return True
    if "data-partner" in path or "/partners/" in path:
        return True
    return False


def ensure_asset_depth(url: str, need_prefix: str = "../../") -> str:
    """Normalize relative asset URLs to depth 2 under /es/{routes,hotels}/."""
    if url.startswith(("http://", "https://", "//", "/", "data:", "mailto:")):
        return url
    # Already deep enough
    if url.startswith("../../"):
        return url
    if url.startswith("../"):
        return "../" + url  # ../ -> ../../
    if url.startswith("./"):
        return need_prefix + url[2:]
    return need_prefix + url


def rewrite_assets(html: str) -> str:
    def repl(m: re.Match) -> str:
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if not is_asset(url) and attr.lower() != "data-partner-root":
            return m.group(0)
        if url.startswith(("http://", "https://", "//", "/", "data:")):
            return m.group(0)
        return f"{attr}={q}{ensure_asset_depth(url)}{q}"

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
                bits[0] = ensure_asset_depth(bits[0])
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

        # Force absolute snub
        if "snub-nosed-breeds" in url:
            path, query, frag = split_url(url)
            return SNUB_ABS + query + frag

        if url.startswith(LIVE):
            path, query, frag = split_url(url[len(LIVE) :] or "/")
            if not path.startswith("/"):
                path = "/" + path
            if path.startswith("/es/") or path == "/es":
                return LIVE + path + query + frag
            if es_exists(path):
                return LIVE + to_es_path(path) + query + frag
            return url

        if url.startswith("/"):
            path, query, frag = split_url(url)
            if path.startswith("/es/") or path == "/es":
                return path + query + frag
            if es_exists(path):
                return to_es_path(path) + query + frag
            return url

        path, query, frag = split_url(url)
        resolved = urljoin(base_url, path)
        if resolved.startswith("/es/") or resolved == "/es":
            en = resolved[3:] or "/"
            if not en.startswith("/"):
                en = "/" + en
            if es_exists(en):
                return url
            return en + query + frag
        return url

    def repl(m: re.Match) -> str:
        q, url = m.group(1), m.group(2)
        if is_asset(url):
            return m.group(0)
        new = map_href(url)
        return f"href={q}{new}{q}"

    return re.sub(r'\bhref=(["\'])([^"\']+)\1', repl, html, flags=re.I)


def set_canonical_and_hreflang(html: str, rel: str) -> str:
    en_path = "/" + rel
    if en_path.endswith("/index.html"):
        en_path = en_path[: -len("index.html")]
    es_path = to_es_path(en_path)
    # Prefer trailing-slash form for hubs
    en_url = LIVE + en_path
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
        html = re.sub(
            r"(<head[^>]*>)",
            r'\1\n<link href="' + es_url + '" rel="canonical"/>',
            html,
            count=1,
            flags=re.I,
        )

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


def add_preview_markers(html: str) -> str:
    if 'name="robots"' not in html[:2500]:
        html = re.sub(r"(<head[^>]*>)", r"\1\n" + NOINDEX, html, count=1, flags=re.I)
    else:
        html = re.sub(
            r'<meta[^>]+name=["\']robots["\'][^>]*>',
            NOINDEX.strip(),
            html,
            count=1,
            flags=re.I,
        )
    if "ppc-preview-bar" not in html:
        html = re.sub(
            r"(<body[^>]*>)",
            r"\1\n" + PREVIEW_BAR,
            html,
            count=1,
            flags=re.I,
        )
    return html


def add_hreflang_to_en(en_file: Path, rel: str) -> None:
    if not en_file.exists():
        print("WARN missing EN", en_file)
        return
    html = en_file.read_text(encoding="utf-8")
    en_path = "/" + rel
    if en_path.endswith("/index.html"):
        en_path = en_path[: -len("index.html")]
    es_path = to_es_path(en_path)
    en_url = LIVE + en_path
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
    src = SRC / rel
    if not src.exists():
        print("MISSING SRC", rel)
        return
    html = src.read_text(encoding="utf-8")
    html = rewrite_assets(html)
    html = rewrite_nav_links(html, rel)
    html = set_canonical_and_hreflang(html, rel)
    html = add_preview_markers(html)
    for base in (ROOT / "site" / "es", ROOT / "static" / "es"):
        dest = base / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")
    print("wrote", rel)


def update_sitemap() -> None:
    sm = ROOT / "site" / "sitemap.xml"
    text = sm.read_text(encoding="utf-8")
    # collect existing locs
    existing = set(re.findall(r"<loc>([^<]+)</loc>", text))
    additions = []
    for rel in PAGES:
        en_path = "/" + rel
        if en_path.endswith("/index.html"):
            en_path = en_path[: -len("index.html")]
        es_url = LIVE + to_es_path(en_path)
        if es_url not in existing:
            additions.append(
                f"<url><loc>{es_url}</loc><lastmod>{TODAY}</lastmod></url>"
            )
        else:
            # bump lastmod if present as single-line url
            text = re.sub(
                rf"(<url><loc>{re.escape(es_url)}</loc><lastmod>)[^<]+(</lastmod></url>)",
                rf"\g<1>{TODAY}\2",
                text,
            )
    if additions:
        if "</urlset>" not in text:
            raise SystemExit("sitemap missing </urlset>")
        text = text.replace("</urlset>", "".join(additions) + "</urlset>")
    sm.write_text(text, encoding="utf-8")
    # mirror
    (ROOT / "static" / "sitemap.xml").write_text(text, encoding="utf-8")
    print("sitemap +", len(additions), "urls")


def patch_es_home_hub_links() -> None:
    """Point ES home header-adjacent / body hub CTAs to /es/routes/ and /es/hotels/."""
    for base in (ROOT / "site", ROOT / "static"):
        path = base / "es" / "index.html"
        if not path.exists():
            continue
        html = path.read_text(encoding="utf-8")
        # absolute EN hubs used in nav/footer/CTA
        html2 = html.replace('href="/routes/"', 'href="/es/routes/"')
        html2 = html2.replace('href="/hotels/"', 'href="/es/hotels/"')
        html2 = html2.replace(
            'href="https://petpolicycheck.com/hotels/"',
            'href="https://petpolicycheck.com/es/hotels/"',
        )
        html2 = html2.replace(
            'href="https://petpolicycheck.com/routes/"',
            'href="https://petpolicycheck.com/es/routes/"',
        )
        # city hotel links on ES home → ES twins
        for city in [
            "orlando",
            "new-york",
            "miami",
            "los-angeles",
            "chicago",
            "austin",
            "detroit",
            "houston",
            "atlanta",
            "boston",
            "denver",
            "san-francisco",
            "seattle",
        ]:
            en = f"/hotels/pet-friendly-hotels-{city}.html"
            es = f"/es/hotels/pet-friendly-hotels-{city}.html"
            html2 = html2.replace(
                f"https://petpolicycheck.com{en}", f"https://petpolicycheck.com{es}"
            )
            html2 = html2.replace(f'href="{en}"', f'href="{es}"')
        if html2 != html:
            path.write_text(html2, encoding="utf-8")
            print("patched hub links", path)


def main() -> None:
    print("pages", len(PAGES))
    for rel in PAGES:
        process_page(rel)
    for rel in PAGES:
        add_hreflang_to_en(ROOT / "site" / rel, rel)
        st = ROOT / "static" / rel
        if st.exists():
            add_hreflang_to_en(st, rel)
    update_sitemap()
    patch_es_home_hub_links()
    # leave legacy /routes/es/* untouched — never touch those paths
    print("done")


if __name__ == "__main__":
    main()
