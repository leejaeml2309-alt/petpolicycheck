#!/usr/bin/env python3
"""Build compact per-language search indexes for PetPolicyCheck (GitHub Pages).

Reads site/sitemap.xml + HTML under site/, merges data/search-synonyms.json,
writes site/assets/search-index.<lang>.json and mirrors to static/assets/.
"""
from __future__ import annotations

import html as htmlmod
import json
import re
import sys
import unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
STATIC = ROOT / "static"
SITEMAP = SITE / "sitemap.xml"
SYNONYMS = ROOT / "data" / "search-synonyms.json"
OUT_DIR = SITE / "assets"
STATIC_OUT = STATIC / "assets"

SKIP_NAMES = {
    "_search-preview.html",
}
SKIP_PREFIXES = (
    "68d2b450",
)
LOCALE_SEGMENTS = {"fr", "es", "de", "ko", "ja", "zh"}

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")
H1_RE = re.compile(r"<h1\b[^>]*>(.*?)</h1>", re.I | re.S)
TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(
    r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',
    re.I | re.S,
)
DESC_RE2 = re.compile(
    r'<meta\s+[^>]*content=["\'](.*?)["\'][^>]*name=["\']description["\']',
    re.I | re.S,
)
H2_RE = re.compile(r"<h2\b[^>]*>(.*?)</h2>", re.I | re.S)
LANG_RE = re.compile(r'<html\b[^>]*\blang=["\']([\w-]+)["\']', re.I)
CANON_RE = re.compile(
    r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\'](.*?)["\']',
    re.I | re.S,
)
IATA_RE = re.compile(r"\b([A-Z]{3})\b")
WORD_RE = re.compile(r"[a-z0-9][a-z0-9'+.-]{1,40}")


def strip_tags(s: str) -> str:
    s = TAG_RE.sub(" ", s or "")
    s = htmlmod.unescape(s)
    return WS_RE.sub(" ", s).strip()


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def tokens(s: str) -> list[str]:
    return WORD_RE.findall(norm(s))


TYPE_LABELS = {
    "en": {
        "Routes": "Routes",
        "Airlines": "Airlines",
        "Countries": "Countries",
        "Hotels": "Hotels",
        "Tools": "Tools",
        "Guides": "Guides",
    },
    "es": {
        "Routes": "Rutas",
        "Airlines": "Aerolíneas",
        "Countries": "Países",
        "Hotels": "Hoteles",
        "Tools": "Herramientas",
        "Guides": "Guías",
    },
}


def infer_type_key(url_path: str) -> str:
    p = url_path.strip("/")
    if not p or p in ("index.html",):
        return "Tools"
    parts = [x for x in p.split("/") if x]
    if parts and parts[0] in LOCALE_SEGMENTS:
        parts = parts[1:]
        if not parts:
            return "Tools"
    top = parts[0]
    rest = "/".join(parts)
    if top == "routes":
        return "Routes"
    if top == "airlines":
        if "compare" in rest:
            return "Tools"
        if "snub-nosed" in rest:
            return "Guides"
        return "Airlines"
    if top == "countries":
        return "Countries"
    if top in ("hotels", "hotel-pets"):
        return "Hotels"
    if top in {
        "passport",
        "fit",
        "titer-calculator",
        "pet-travel-checklist",
        "widgets",
        "extension",
    }:
        return "Tools"
    if top == "airport":
        return "Guides"
    if top in {
        "veterans",
        "military-pcs",
        "field-guides",
        "products",
        "forum",
        "book",
        "insurance",
        "grooming",
        "clinics",
        "partner-vets",
        "flight-volunteer",
        "taxi",
        "pro",
        "b2b-pet-desk",
        "advertise",
    }:
        return "Guides"
    if rest.endswith(".html") and "/" not in rest:
        return "Guides"
    return "Guides"


def infer_type(url_path: str, lang: str = "en") -> str:
    key = infer_type_key(url_path)
    labels = TYPE_LABELS.get(lang) or TYPE_LABELS["en"]
    return labels.get(key, key)


def lang_from_html(text: str, rel: str) -> str:
    m = LANG_RE.search(text)
    if m:
        return m.group(1).split("-")[0].lower()
    parts = Path(rel).parts
    for seg in parts:
        if seg in LOCALE_SEGMENTS:
            return seg
    return "en"


def url_path_from_file(rel: str) -> str:
    rel = rel.replace("\\", "/")
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    if rel == "index.html":
        return "/"
    return "/" + rel


def sitemap_paths() -> set[str]:
    if not SITEMAP.exists():
        return set()
    try:
        root = ET.parse(SITEMAP).getroot()
    except ET.ParseError:
        text = SITEMAP.read_text(encoding="utf-8", errors="ignore")
        return {
            u.replace("https://petpolicycheck.com", "") or "/"
            for u in re.findall(r"<loc>(.*?)</loc>", text)
        }
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    out = set()
    for loc in root.findall(".//sm:loc", ns) or root.findall(".//loc"):
        u = (loc.text or "").strip()
        if not u:
            continue
        path = u.replace("https://petpolicycheck.com", "") or "/"
        out.add(path)
    return out


def flatten_synonyms(raw: dict) -> dict[str, list[str]]:
    flat: dict[str, list[str]] = {}
    for group, mapping in raw.items():
        if group.startswith("_") or not isinstance(mapping, dict):
            continue
        for k, vals in mapping.items():
            key = norm(k)
            bucket = flat.setdefault(key, [])
            for v in vals:
                nv = norm(v)
                if nv and nv not in bucket and nv != key:
                    bucket.append(nv)
    return flat


def load_airline_hints() -> dict[str, list[str]]:
    hints: dict[str, list[str]] = {}
    adir = ROOT / "data" / "airlines"
    if not adir.exists():
        return hints
    for p in adir.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        slug = d.get("slug") or p.stem
        name = d.get("name") or slug
        iata = (d.get("iata") or "").lower()
        keys = {norm(slug), norm(name), *tokens(name)}
        if iata:
            keys.add(iata)
        hints[slug] = sorted(k for k in keys if k)
    return hints


def extract_keywords(text: str, url_path: str, title: str, desc: str) -> list[str]:
    kws: list[str] = []
    seen: set[str] = set()

    def add(x: str):
        x = norm(x)
        if not x or x in seen or len(x) < 2:
            return
        seen.add(x)
        kws.append(x)

    for t in tokens(title):
        add(t)
    for t in tokens(desc)[:24]:
        add(t)
    for h2 in H2_RE.findall(text)[:8]:
        for t in tokens(strip_tags(h2))[:6]:
            add(t)
    # path crumbs
    for part in re.split(r"[/\-_.]+", url_path):
        if part and part not in ("html", "index", "pet", "friendly", "to", "the"):
            add(part)
    # IATA from path segments like /airport/YVR/
    for seg in url_path.strip("/").split("/"):
        if re.fullmatch(r"[A-Za-z]{3}", seg):
            add(seg)
    # known three-letter codes that appear as standalone words in early content
    head = strip_tags(text[:4000])
    for code in IATA_RE.findall(head):
        if code in {
            "USA",
            "CDC",
            "USD",
            "CAD",
            "EUR",
            "FAQ",
            "PDF",
            "GPS",
            "HTML",
            "CSS",
            "API",
            "NWS",
            "ISO",
            "AQS",
            "AND",
            "THE",
            "FOR",
            "WITH",
            "YOU",
            "PET",
            "CAT",
            "DOG",
            "ALL",
            "NEW",
            "OLD",
            "NOT",
            "YES",
            "MAX",
            "MIN",
        }:
            continue
        add(code)
    return kws[:48]


def iter_html_files():
    for p in SITE.rglob("*.html"):
        rel = p.relative_to(SITE).as_posix()
        name = Path(rel).name
        if name in SKIP_NAMES or name.startswith("_"):
            continue
        if any(rel.startswith(x) for x in SKIP_PREFIXES):
            continue
        if "/ads/" in f"/{rel}" or rel.startswith("fonts/"):
            continue
        yield p, rel


def build_for_lang(lang: str, syn_flat: dict[str, list[str]], airline_hints: dict) -> dict:
    pages = []
    sm = sitemap_paths()

    for path, rel in iter_html_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        page_lang = lang_from_html(text, rel)
        if page_lang != lang:
            continue
        # Skip localized route copies living under /routes/fr/ etc. when lang=en
        parts = Path(rel).parts
        if lang == "en" and len(parts) >= 2 and parts[0] == "routes" and parts[1] in LOCALE_SEGMENTS:
            continue

        url = url_path_from_file(rel)
        # Prefer canonical path when present
        cm = CANON_RE.search(text)
        if cm:
            cu = cm.group(1).strip()
            if "petpolicycheck.com" in cu:
                url = cu.split("petpolicycheck.com", 1)[1] or "/"
                if not url.startswith("/"):
                    url = "/" + url

        h1 = strip_tags(H1_RE.search(text).group(1)) if H1_RE.search(text) else ""
        title_raw = strip_tags(TITLE_RE.search(text).group(1)) if TITLE_RE.search(text) else ""
        title_meta = title_raw.split("|")[0].strip()
        # Airport marketing H1s are vague; prefer document title when it carries the code/place.
        if url.startswith("/airport/") and title_meta:
            title = title_meta
        else:
            title = h1 or title_meta or url
        dm = DESC_RE.search(text) or DESC_RE2.search(text)
        desc = strip_tags(dm.group(1)) if dm else ""

        ptype = infer_type(url, lang)
        kws = extract_keywords(text, url, title, desc)

        # airline slug hints
        m = re.search(r"/airlines/([a-z0-9-]+)\.html$", url)
        if m and m.group(1) in airline_hints:
            for h in airline_hints[m.group(1)]:
                if h not in kws:
                    kws.append(h)

        # hotel city from filename
        hm = re.search(r"pet-friendly-hotels-([a-z0-9-]+)\.html$", url)
        if hm:
            city = hm.group(1).replace("-", " ")
            if city not in kws:
                kws.append(city)
            if "hotel" not in kws:
                kws.append("hotel")
            if "hotels" not in kws:
                kws.append("hotels")
            if lang == "es":
                for extra in ("hotel", "hoteles", "mascota", "perro", "gato"):
                    if extra not in kws:
                        kws.append(extra)

        # ES topic boosts from path/title
        if lang == "es":
            blob = " ".join([title, desc, url])
            low = norm(blob)
            for term in (
                "perro",
                "gato",
                "mascota",
                "aerolinea",
                "ruta",
                "hotel",
                "veterano",
                "braquicefalo",
                "hocico",
            ):
                if term in low and term not in kws:
                    kws.append(term)

        pages.append(
            {
                "t": title[:120],
                "u": url,
                "y": ptype,
                "k": kws[:40],
            }
        )

    # Prefer sitemap-listed pages first (stable), then extras from disk
    sm_norm = {p if p.endswith("/") or p.endswith(".html") or p == "/" else p + "/" for p in sm}
    def rank(p):
        u = p["u"]
        in_sm = 0 if (u in sm or u in sm_norm or (u.rstrip("/") + "/") in sm) else 1
        return (in_sm, p["y"], p["u"])

    pages.sort(key=rank)

    # Compact synonym map: only entries useful for this language index
    syn_out = {k: v for k, v in sorted(syn_flat.items()) if v}

    return {
        "lang": lang,
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "synonyms": syn_out,
        "pages": pages,
    }


def main() -> int:
    raw = {}
    if SYNONYMS.exists():
        raw = json.loads(SYNONYMS.read_text(encoding="utf-8"))
    syn_flat = flatten_synonyms(raw)
    airline_hints = load_airline_hints()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_OUT.mkdir(parents=True, exist_ok=True)

    # EN now; structure ready for es/fr later
    langs = ["en", "es"]
    for lang in langs:
        data = build_for_lang(lang, syn_flat, airline_hints)
        if lang == "es":
            # No /es/hotels yet — include EN hotel pages so "hotel boston" etc. resolve.
            en_hotels = build_for_lang("en", syn_flat, airline_hints)
            seen = {p["u"] for p in data["pages"]}
            for page in en_hotels["pages"]:
                if not page["u"].startswith("/hotels/"):
                    continue
                if page["u"] in seen:
                    continue
                page = dict(page)
                page["y"] = TYPE_LABELS["es"]["Hotels"]
                # keep EN title (no ES twin); add Spanish query tokens
                k = list(page.get("k") or [])
                for extra_kw in ("hotel", "hoteles", "mascota", "perro", "gato"):
                    if extra_kw not in k:
                        k.append(extra_kw)
                page["k"] = k[:40]
                data["pages"].append(page)
        out = OUT_DIR / f"search-index.{lang}.json"
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        out.write_text(payload + "\n", encoding="utf-8")
        mirror = STATIC_OUT / f"search-index.{lang}.json"
        mirror.write_text(payload + "\n", encoding="utf-8")
        raw_size = len(payload.encode("utf-8"))
        import gzip

        gz = len(gzip.compress(payload.encode("utf-8"), compresslevel=9))
        print(f"{out}: {len(data['pages'])} pages, {raw_size} bytes raw, {gz} bytes gzip")
        if gz > 150_000:
            print(f"WARNING: gzip size {gz} exceeds 150KB target", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
