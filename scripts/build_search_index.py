#!/usr/bin/env python3
"""Build compact per-language search indexes for PetPolicyCheck (GitHub Pages).

Indexes INFORMATION pages only (countries, cities, airlines, airports,
transport, guides, rules/policies). Commercial hotel listings, affiliate
product/shop pages, booking cards, and advertise/partner/sponsor pages
are excluded.

Reads HTML under site/, merges data/search-synonyms.json, writes
site/assets/search-index.<lang>.json and mirrors to static/assets/.
Synthetic city / airport / transport entries point only at existing
pages and anchors — no new content pages, no invented facts.
"""
from __future__ import annotations

import gzip
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
REPORT = ROOT / "qa" / "search" / "index-report.json"

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
    r'<meta\b[^>]*\bname=["\']description["\'][^>]*\bcontent=["\']([^"\']*)["\']',
    re.I,
)
DESC_RE2 = re.compile(
    r'<meta\b[^>]*\bcontent=["\']([^"\']*)["\'][^>]*\bname=["\']description["\']',
    re.I,
)
KW_RE = re.compile(
    r'<meta\b[^>]*\bname=["\']keywords["\'][^>]*\bcontent=["\']([^"\']*)["\']',
    re.I,
)
KW_RE2 = re.compile(
    r'<meta\b[^>]*\bcontent=["\']([^"\']*)["\'][^>]*\bname=["\']keywords["\']',
    re.I,
)
HX_RE = re.compile(r"<h([1-3])\b([^>]*)>(.*?)</h\1>", re.I | re.S)
LANG_RE = re.compile(r'<html\b[^>]*\blang=["\']([\w-]+)["\']', re.I)
CANON_RE = re.compile(
    r'<link\s+[^>]*rel=["\']canonical["\'][^>]*href=["\'](.*?)["\']',
    re.I | re.S,
)
MAIN_RE = re.compile(r"<main\b[^>]*>(.*?)</main>", re.I | re.S)
SCRIPT_STYLE_RE = re.compile(r"<(script|style|noscript)\b[^>]*>.*?</\1>", re.I | re.S)
# Airport kicker: "JFK · New York City · Airport pet travel"
KICKER_RE = re.compile(
    r"\b([A-Z]{3})\s*·\s*([^<\n]{2,80}?)\s*·\s*Airport pet travel",
    re.I,
)
WORD_RE = re.compile(r"[a-z0-9][a-z0-9'+.-]{1,40}")

BODY_CAP = 1800
HEADING_CAP = 320
KEYWORD_CAP = 40
TITLE_CAP = 140

# Stable English type keys (UI localizes the label).
TYPE_LABELS = {
    "en": {
        "Countries": "Countries",
        "Cities": "Cities",
        "Airports": "Airports",
        "Transport": "Transport",
        "Airlines": "Airlines",
        "Routes": "Routes",
        "Hotels": "Hotels",
        "Guides": "Guides",
        "Veterans": "Veterans",
        "Pro": "Pet Desk Pro",
        "Tools": "Tools",
        "Legal": "Legal",
    },
    "es": {
        "Countries": "Países",
        "Cities": "Ciudades",
        "Airports": "Aeropuertos",
        "Transport": "Transporte",
        "Airlines": "Aerolíneas",
        "Routes": "Rutas",
        "Hotels": "Hoteles",
        "Guides": "Guías",
        "Veterans": "Veteranos",
        "Pro": "Pet Desk Pro",
        "Tools": "Herramientas",
        "Legal": "Legal",
    },
}

STOP = {
    "width", "device-width", "initial-scale", "viewport", "charset",
    "content", "name", "meta", "http-equiv", "stylesheet", "script",
    "javascript", "petpolicycheck", "html", "css", "index", "menu",
    "skip", "button", "header", "footer", "nav", "main", "div",
    "the", "and", "for", "with", "you", "your", "our", "are", "this",
    "that", "from", "into", "onto", "over", "under", "plus", "more",
    "page", "site", "home", "click", "here", "also", "than", "then",
    "el", "la", "los", "las", "del", "una", "uno", "para", "por",
    "con", "que", "como", "mas", "más",
}

# Forum tools / account pages are not information pages.
FORUM_SKIP = {
    "account.html", "admin.html", "new.html", "post.html", "partners.html",
    "login.html", "signup.html",
}


def strip_tags(s: str) -> str:
    s = TAG_RE.sub(" ", s or "")
    s = htmlmod.unescape(s)
    return WS_RE.sub(" ", s).strip()


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s.lower().strip()


def tokens(s: str) -> list[str]:
    return [t for t in WORD_RE.findall(norm(s)) if t not in STOP and len(t) >= 2]


def url_path_from_file(rel: str) -> str:
    rel = rel.replace("\\", "/")
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    if rel == "index.html":
        return "/"
    return "/" + rel


def lang_from_html(text: str, rel: str) -> str:
    m = LANG_RE.search(text)
    if m:
        return m.group(1).split("-")[0].lower()
    parts = Path(rel).parts
    for seg in parts:
        if seg in LOCALE_SEGMENTS:
            return seg
    return "en"


def classify_exclude(url: str, rel: str) -> str | None:
    """Return a reason string if this URL must not enter the index."""
    p = url.lower()
    rel_l = rel.lower()
    if "/advertise" in p or rel_l.endswith("advertise.html"):
        return "advertise/sponsor page"
    if "/partner-vets" in p or "/partners/" in p or p.endswith("/forum/partners.html"):
        return "partner page"
    if p.rstrip("/").endswith("/book") or "/book/" in p:
        return "booking page"
    if "/extension" in p:
        return "removed extension page"
    if "/products/" in p:
        return "affiliate/product page"
    # Commercial city hotel listings (Expedia/booking cards), not chain policy pages.
    if re.search(r"/hotels/pet-friendly-hotels-[a-z0-9-]+", p):
        return "commercial hotel listing"
    # Forum account / compose / admin tools
    name = Path(p).name
    if "/forum/" in p and (name in FORUM_SKIP or name == "partners.html"):
        return "forum tool or partner page"
    if "/ads/" in f"/{rel_l}" or rel_l.startswith("fonts/"):
        return "asset / ad file"
    return None


def infer_type_key(url_path: str) -> str:
    p = url_path.strip("/")
    if not p or p in ("index.html",):
        return "Tools"
    parts = [x for x in p.split("/") if x]
    if parts and parts[0] in LOCALE_SEGMENTS:
        parts = parts[1:]
        if not parts:
            return "Tools"
    top = parts[0] if parts else ""
    rest = "/".join(parts)
    leaf = parts[-1] if parts else ""
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
    if top == "airport":
        return "Airports"
    if top == "taxi" or leaf in ("taxi.html",) or "/taxi" in f"/{rest}":
        if top == "taxi":
            return "Transport"
    if top in {"veterans", "military-pcs", "k9"}:
        return "Veterans"
    if top in {"pro", "b2b-pet-desk"}:
        return "Pro"
    if leaf in {"privacy.html", "terms.html", "refund-policy.html", "contact.html", "about.html"}:
        return "Legal"
    if top in {
        "passport",
        "fit",
        "titer-calculator",
        "pet-travel-checklist",
        "widgets",
    }:
        return "Tools"
    return "Guides"


def legal_filename(url_path: str) -> bool:
    leaf = url_path.rstrip("/").split("/")[-1]
    return leaf in {"privacy.html", "terms.html", "refund-policy.html", "contact.html", "about.html"}


def extract_headings(text: str) -> list[tuple[int, str, str]]:
    """Return list of (level, id, text)."""
    out = []
    for m in HX_RE.finditer(text):
        level = int(m.group(1))
        attrs = m.group(2) or ""
        body = strip_tags(m.group(3))
        if not body or body.lower() in {"menu"}:
            continue
        idm = re.search(r'\bid=["\']([^"\']+)', attrs, re.I)
        hid = idm.group(1) if idm else ""
        out.append((level, hid, body))
    return out


def extract_body(text: str) -> str:
    chunk = None
    m = MAIN_RE.search(text)
    chunk = m.group(1) if m else text
    chunk = SCRIPT_STYLE_RE.sub(" ", chunk)
    # Drop chrome that inflates the body with nav words
    chunk = re.sub(r"<nav\b[^>]*>.*?</nav>", " ", chunk, flags=re.I | re.S)
    chunk = re.sub(r"<header\b[^>]*>.*?</header>", " ", chunk, flags=re.I | re.S)
    chunk = re.sub(r"<footer\b[^>]*>.*?</footer>", " ", chunk, flags=re.I | re.S)
    chunk = re.sub(r'<aside\b[^>]*class=["\'][^"\']*ppc-pro-banner[^"\']*["\'][^>]*>.*?</aside>', " ", chunk, flags=re.I | re.S)
    plain = strip_tags(chunk)
    # Keep a readable but compact snippet; search JS matches tokens in `b`.
    if len(plain) > BODY_CAP:
        plain = plain[:BODY_CAP].rsplit(" ", 1)[0]
    return plain


def extract_meta(text: str) -> tuple[str, str]:
    dm = DESC_RE.search(text) or DESC_RE2.search(text)
    desc = strip_tags(dm.group(1)) if dm else ""
    km = KW_RE.search(text) or KW_RE2.search(text)
    kws = strip_tags(km.group(1)) if km else ""
    return desc, kws


def extract_keywords(
    title: str,
    desc: str,
    meta_kw: str,
    headings: list[tuple[int, str, str]],
    url_path: str,
    body: str,
    extra: list[str] | None = None,
) -> list[str]:
    kws: list[str] = []
    seen: set[str] = set()

    def add(x: str):
        x = norm(x)
        if not x or x in seen or x in STOP or len(x) < 2:
            return
        # skip viewport-like tokens
        if x.startswith("device-") or x.endswith("-scale"):
            return
        seen.add(x)
        kws.append(x)

    for t in tokens(title):
        add(t)
    for t in tokens(meta_kw):
        add(t)
    for t in tokens(desc)[:24]:
        add(t)
    for _lvl, _hid, htext in headings[:12]:
        for t in tokens(htext)[:8]:
            add(t)
    for part in re.split(r"[/\-_.]+", url_path):
        if part and part not in ("html", "index", "pet", "friendly", "to", "the", "es", "en"):
            add(part)
    # 3-letter codes that are real path segments (airport hubs)
    for seg in url_path.strip("/").split("/"):
        if re.fullmatch(r"[A-Za-z]{3}", seg):
            add(seg.lower())
    if extra:
        for e in extra:
            if " " in e.strip():
                add(e)
                for t in tokens(e):
                    add(t)
            else:
                add(e)
    # A few distinctive body tokens not already captured (cities, airports)
    for t in tokens(body)[:40]:
        if t not in seen and t not in STOP and len(t) >= 4:
            add(t)
        if len(kws) >= KEYWORD_CAP:
            break
    return kws[:KEYWORD_CAP]


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


def country_label_from_rel(rel: str, title: str, h1: str) -> str:
    slug = Path(rel).stem.replace("-map", "")
    pretty = {
        "usa": "United States",
        "uk": "United Kingdom",
        "south-korea": "South Korea",
        "france": "France",
        "germany": "Germany",
        "japan": "Japan",
        "canada": "Canada",
        "mexico": "Mexico",
    }.get(slug)
    if pretty:
        return pretty
    blob = h1 or title
    m = re.search(r"for (the )?([^:|]+)", blob, re.I)
    if m:
        return m.group(2).strip()
    return slug.replace("-", " ").title()


def parse_hubs_table(html: str) -> list[tuple[str, str]]:
    """Return (IATA, city-cell text) from a country page hubs table, if any."""
    m = re.search(
        r'<section\b[^>]*\bid=["\']hubs["\'][^>]*>(.*?)</section>',
        html,
        re.I | re.S,
    )
    if not m:
        return []
    chunk = m.group(1)
    # ignore thead
    body_only = re.sub(r"<thead\b[^>]*>.*?</thead>", " ", chunk, flags=re.I | re.S)
    rows = []
    for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", body_only, re.I | re.S):
        cells = [strip_tags(c) for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.I | re.S)]
        if len(cells) < 2:
            continue
        code = cells[0].strip()
        city = cells[1].strip()
        if not re.fullmatch(r"[A-Za-z]{3}", code):
            continue
        if code.upper() in {"HUB", "IATA", "COD", "REF"}:
            continue
        if city.lower().startswith("city") or city.lower() in {"hub", "region", "land"}:
            continue
        rows.append((code.upper(), city))
    return rows


def first_city_name(city_cell: str) -> str:
    """'Paris (Roissy) · Île-de-France' -> 'Paris'."""
    head = city_cell.split("·")[0].strip()
    head = re.sub(r"\s*\([^)]*\)\s*", " ", head).strip()
    # 'Lyon Saint-Exupéry' -> keep first token if it's a known short city form
    # but prefer the full leading name before an en-dash airport suffix.
    head = re.sub(r"\s+Saint-Exupéry$", "", head, flags=re.I).strip()
    return head or city_cell.split("·")[0].strip()


def section_heading(html: str, section_id: str) -> str:
    m = re.search(
        rf'<section\b[^>]*\bid=["\']{re.escape(section_id)}["\'][^>]*>(.*?)</section>',
        html,
        re.I | re.S,
    )
    if not m:
        return ""
    hm = re.search(r"<h2\b[^>]*>(.*?)</h2>", m.group(1), re.I | re.S)
    return strip_tags(hm.group(1)) if hm else ""


def _names_overlap(a: str, b: str) -> bool:
    a, b = norm(a), norm(b)
    if not a or not b:
        return False
    if a == b or a in b or b in a:
        return True
    ta, tb = a.split(), b.split()
    short, long = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return all(tok in long for tok in short)


def find_anchor_for_term(html: str, term: str) -> str:
    """Hash only when a heading *is* the term (e.g. "New York"), not a
    passing mention inside taxi/parks copy or the following section."""
    term_n = norm(term)
    if not term_n:
        return ""
    skip = {"main", "ppc-drawer", "menu", "federal", "origins", "faq", "quick", "free-checklist", "book", "book-h"}
    term_words = len(term_n.split())
    best = ""
    for hx in HX_RE.finditer(html):
        attrs = hx.group(2) or ""
        text = strip_tags(hx.group(3))
        idm = re.search(r'\bid=["\']([^"\']+)', attrs, re.I)
        hid = idm.group(1) if idm else ""
        if not hid or hid in skip:
            # id may sit on a wrapper; look back a little for id=
            pre = html[max(0, hx.start() - 400): hx.start()]
            ids = re.findall(r'\bid=["\']([^"\']+)', pre)
            hid = next((i for i in reversed(ids) if i not in skip), "")
        if not hid or hid in skip:
            continue
        nt = norm(text)
        if not nt:
            continue
        if nt == term_n or nt.startswith(term_n + " ") or term_n.startswith(nt) and _names_overlap(term_n, nt):
            if len(nt.split()) <= term_words + 2:
                return hid
    return ""



def make_page(
    title: str,
    url: str,
    type_key: str,
    keywords: list[str],
    headings: str,
    body: str,
) -> dict:
    return {
        "t": title[:TITLE_CAP],
        "u": url,
        "y": type_key,
        "k": keywords[:KEYWORD_CAP],
        "h": headings[:HEADING_CAP],
        "b": body[:BODY_CAP],
    }


def collect_records(lang: str, syn_flat: dict, airline_hints: dict) -> tuple[list[dict], list[dict], list[dict]]:
    """Return (pages, exclusions, skipped_locale_copies)."""
    pages: list[dict] = []
    exclusions: list[dict] = []
    # For synthetic entries we keep the raw HTML of country/airport pages.
    country_docs: list[dict] = []
    airport_docs: list[dict] = []

    for path, rel in iter_html_files():
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        page_lang = lang_from_html(text, rel)
        if page_lang != lang:
            continue
        parts = Path(rel).parts
        if len(parts) >= 2 and parts[0] == "routes" and parts[1] in LOCALE_SEGMENTS:
            continue

        url = url_path_from_file(rel)
        cm = CANON_RE.search(text)
        if cm:
            cu = cm.group(1).strip()
            if "petpolicycheck.com" in cu:
                url = cu.split("petpolicycheck.com", 1)[1] or "/"
                if not url.startswith("/"):
                    url = "/" + url

        reason = classify_exclude(url, rel)
        if reason:
            exclusions.append({"u": url, "reason": reason, "file": rel})
            continue

        h1s = [strip_tags(x) for x in H1_RE.findall(text)]
        h1 = next((h for h in h1s if h and h.lower() != "menu"), "")
        title_raw = strip_tags(TITLE_RE.search(text).group(1)) if TITLE_RE.search(text) else ""
        title_meta = title_raw.split("|")[0].strip()
        headings = extract_headings(text)
        desc, meta_kw = extract_meta(text)
        body = extract_body(text)

        # Airport marketing H1s are vague; prefer document title + on-page kicker city.
        kicker_city = ""
        kicker_code = ""
        km = KICKER_RE.search(text)
        if km:
            kicker_code = km.group(1).upper()
            # "Haneda · Tokyo" or "New York City" or "Incheon · Seoul"
            kicker_city = strip_tags(km.group(2))
        if url.startswith("/airport/") and title_meta:
            title = title_meta
            if kicker_city and norm(kicker_city) not in norm(title):
                # Use words already on the page (kicker + title), do not invent a city.
                title = f"{title_meta} — {kicker_city.replace(' · ', ', ')}"
        else:
            title = h1 or title_meta or url

        type_key = infer_type_key(url)
        extra: list[str] = []
        if kicker_city:
            extra.append(kicker_city)
            extra.extend(re.split(r"\s*·\s*", kicker_city))
        if kicker_code:
            extra.append(kicker_code)

        m_air = re.search(r"/airlines/([a-z0-9-]+)\.html$", url)
        if m_air and m_air.group(1) in airline_hints:
            extra.extend(airline_hints[m_air.group(1)])

        kws = extract_keywords(title, desc, meta_kw, headings, url, body, extra)

        # Country hubs: keep city / IATA terms searchable even if they sit
        # late in the page (beyond the body cap).
        if type_key == "Countries":
            hub_bits = []
            for code, cell in parse_hubs_table(text):
                hub_bits.append(code)
                hub_bits.append(cell)
                extra_city = first_city_name(cell)
                if extra_city:
                    hub_bits.append(extra_city)
                for term in (code, cell, extra_city):
                    if term and term not in kws:
                        # extract_keywords will normalize; append raw too
                        pass
            if hub_bits:
                blob = " ".join(hub_bits)
                body = (body + " " + blob).strip()[:BODY_CAP]
                kws = extract_keywords(title, desc, meta_kw, headings, url, body, extra + hub_bits)

        heading_str = " · ".join(h[2] for h in headings[:10])

        rec = make_page(title, url, type_key, kws, heading_str, body)
        pages.append(rec)

        if type_key == "Countries":
            country_docs.append(
                {
                    "url": url,
                    "rel": rel,
                    "text": text,
                    "title": title,
                    "h1": h1 or title,
                    "label": country_label_from_rel(rel, title_meta, h1),
                    "lang": lang,
                }
            )
        if type_key == "Airports" and re.search(r"/airport/[A-Za-z]{3}/?$", url):
            # Longer visible text for country association only (not stored in the index).
            plain_long = extract_body(text)  # uses BODY_CAP; get a wider slice below
            main_m = MAIN_RE.search(SCRIPT_STYLE_RE.sub(" ", text))
            wider = strip_tags(main_m.group(1) if main_m else text)[:8000]
            airport_docs.append(
                {
                    "url": url,
                    "title": title,
                    "code": url.strip("/").split("/")[-1].upper(),
                    "kicker_city": kicker_city,
                    "body": body,
                    "plain": wider,
                }
            )

    synthetics = build_synthetics(country_docs, airport_docs, lang)
    return pages, exclusions, synthetics


def build_synthetics(country_docs: list[dict], airport_docs: list[dict], lang: str) -> list[dict]:
    """City / airport / transport / hotel-policy entries from existing anchors."""
    out: list[dict] = []
    seen_keys: set[tuple] = set()
    city_seen: set[str] = set()  # norm(city + country)

    def add(rec: dict):
        key = (rec["u"], rec["t"], rec["y"])
        if key in seen_keys:
            return
        seen_keys.add(key)
        out.append(rec)

    # Map country label (norm) -> doc
    def _prefer_country(a, b):
        def is_map(d):
            return "-map.html" in d["url"]
        if a is None:
            return b
        if is_map(a) and not is_map(b):
            return b
        if is_map(b) and not is_map(a):
            return a
        return a if len(a.get("text") or "") >= len(b.get("text") or "") else b

    by_label = {}
    for doc in country_docs:
        keys = {
            norm(doc["label"]),
            norm(doc["label"].replace("United States", "USA")),
            norm(doc["label"].replace("United Kingdom", "UK")),
        }
        if "korea" in norm(doc["label"]):
            keys.update({"south korea", "korea"})
        for k in keys:
            if not k:
                continue
            by_label[k] = _prefer_country(by_label.get(k), doc)

    # 1) Hubs tables + transport / hotels sections on country pages
    for doc in country_docs:
        hubs = parse_hubs_table(doc["text"])
        country = doc["label"]
        base = doc["url"]
        cities_here: list[str] = []
        for code, cell in hubs:
            city = first_city_name(cell)
            if city:
                cities_here.append(city)
            # Airport row — no standalone /airport/CODE page needed; point at #hubs.
            title = f"{code} — {cell}" if cell else code
            extra = [code, city, country, cell, "airport", "aeropuerto", "hub"]
            kws = extract_keywords(title, "", "", [], base + "#hubs", cell, extra)
            add(
                make_page(
                    title[:TITLE_CAP],
                    base + "#hubs",
                    "Airports",
                    kws,
                    f"{code} · {cell}",
                    cell[:BODY_CAP],
                )
            )
        # One city entry per unique city on this country page
        for city in dict.fromkeys(cities_here):
            key = norm(city) + "|" + norm(country)
            if key in city_seen:
                continue
            city_seen.add(key)
            anchor = find_anchor_for_term(doc["text"], city)
            # Prefer a city-specific heading if any; otherwise the country page
            # (hubs / parks often hold the practical city info).
            if not anchor:
                # Paris / London practical info is on the same country page.
                if "id=\"hubs\"" in doc["text"] or "id='hubs'" in doc["text"]:
                    # Keep the country URL without a hash so the city result
                    # is the France/UK/Germany page itself (distinct from #hubs airports).
                    dest = base
                else:
                    dest = base
            else:
                dest = f"{base}#{anchor}"
                # If the only hit is a very generic id, stay on the page root.
                if anchor in {"federal", "origins", "faq", "main"}:
                    dest = base
            title = f"{city} — {country}"
            extra = [city, country, "city", "ciudad", "pet travel"]
            kws = extract_keywords(title, "", "", [], dest, city + " " + country, extra)
            add(
                make_page(
                    title,
                    dest,
                    "Cities",
                    kws,
                    title,
                    "",
                )
            )

        # Transport sections
        for sid, kind, extra_words in (
            ("taxi", "Taxi and private hire", ["taxi", "uber", "vtc", "rideshare"]),
            ("bus", "Bus and local transit", ["bus", "metro", "tram", "transit", "subway"]),
            ("train", "Train", ["train", "rail", "sncf", "eurostar"]),
        ):
            if not re.search(rf'\bid=["\']{sid}["\']', doc["text"]):
                continue
            heading = section_heading(doc["text"], sid) or kind
            title = f"{heading} — {country}"
            dest = f"{base}#{sid}"
            extra = extra_words + [country, "transport", "transporte"]
            # include cities so "Paris taxi" still hits this entry
            extra.extend(dict.fromkeys(cities_here))
            kws = extract_keywords(title, "", "", [], dest, heading, extra)
            add(make_page(title, dest, "Transport", kws, heading, ""))

        # Hotel pet-policy section on the country page (info, not a listing)
        if re.search(r'\bid=["\']hotels["\']', doc["text"]):
            heading = section_heading(doc["text"], "hotels") or "Hotels"
            title = f"{heading} — {country}"
            dest = f"{base}#hotels"
            extra = ["hotel", "hotels", "hoteles", country] + list(dict.fromkeys(cities_here))
            kws = extract_keywords(title, "", "", [], dest, heading, extra)
            add(make_page(title, dest, "Hotels", kws, heading, ""))

    # 2) Cities mentioned on standalone airport pages (Tokyo, Seoul, New York…)
    #    when no hubs-table city entry already exists.
    def country_for_airport(adoc: dict) -> dict | None:
        # Visible text only — never raw HTML (nav hrefs like /countries/usa-map.html
        # would otherwise make every airport look American).
        blob = norm(
            " ".join(
                [
                    adoc.get("plain") or adoc.get("body") or "",
                    adoc.get("title") or "",
                    adoc.get("kicker_city") or "",
                ]
            )
        )
        # Score country labels by whole-word hits so "Korea or France"
        # on a Japan airport page does not beat "Japan".
        best, best_n = None, 0
        seen_docs = set()
        for lab, doc in by_label.items():
            if not lab or id(doc) in seen_docs and lab != norm(doc["label"]):
                # still count every alias, but accumulate per doc
                pass
            aliases = {lab, norm(doc["label"])}
            # short aliases
            pretty = norm(doc["label"])
            if pretty == "united states":
                aliases.update({"usa", "u.s.", "u.s.a.", "united states"})
            elif pretty == "united kingdom":
                aliases.update({"uk", "u.k.", "great britain", "united kingdom"})
            elif "korea" in pretty:
                aliases.update({"south korea", "korea"})
            n = 0
            for alias in aliases:
                if not alias or alias in {"us", "un"}:  # too short / ambiguous
                    continue
                n += len(re.findall(r"\b" + re.escape(alias) + r"\b", blob))
            doc_id = id(doc)
            # We may see the same doc under many aliases; keep a running max
            prev = getattr(doc, "_score", 0)
            # use a side map
            if not hasattr(country_for_airport, "_scores"):
                country_for_airport._scores = {}
            # handled below with a clean map instead
        scores: dict[int, tuple[int, dict]] = {}
        for lab, doc in by_label.items():
            aliases = {lab, norm(doc["label"])}
            pretty = norm(doc["label"])
            if pretty == "united states":
                aliases.update({"usa", "u.s.", "u.s.a.", "united states"})
            elif pretty == "united kingdom":
                aliases.update({"uk", "u.k.", "great britain", "united kingdom"})
            elif "korea" in pretty:
                aliases.update({"south korea", "korea"})
            elif pretty == "japan":
                aliases.update({"japan", "japanese"})
            elif pretty == "canada":
                aliases.update({"canada", "canadian"})
            n = 0
            for alias in {a for a in aliases if a and len(a) >= 3}:
                n += len(re.findall(r"\b" + re.escape(alias) + r"\b", blob))
            did = id(doc)
            if did not in scores or n > scores[did][0]:
                scores[did] = (n, doc)
        ranked = sorted(scores.values(), key=lambda x: x[0], reverse=True)
        if not ranked or ranked[0][0] <= 0:
            return None
        # require a clear winner when two countries are mentioned
        if len(ranked) > 1 and ranked[0][0] == ranked[1][0]:
            return None
        return ranked[0][1]

    for adoc in airport_docs:
        kicker = adoc.get("kicker_city") or ""
        # Split "Narita · Tokyo" / "Incheon · Seoul" / "New York City"
        parts = [p.strip() for p in re.split(r"\s*·\s*", kicker) if p.strip()]
        # The last or only part is usually the city
        city_guess = parts[-1] if parts else ""
        if not city_guess:
            continue
        # Avoid using a bare airport name as a city when it's the first part
        # only (e.g. just "Austin" is fine; "Haneda" should not beat "Tokyo").
        country_doc = country_for_airport(adoc)
        if country_doc is None:
            # Fall back: a country RULES page that already mentions this city
            # (e.g. New York City on /countries/usa.html#st-ny).
            hits = []
            for cdoc in country_docs:
                if "-map.html" in cdoc["url"]:
                    continue
                visible = strip_tags(SCRIPT_STYLE_RE.sub(" ", cdoc["text"]))[:20000]
                if _names_overlap(city_guess, visible) and norm(city_guess) in norm(visible):
                    hits.append(cdoc)
            if len(hits) == 1:
                country_doc = hits[0]
        country_name = country_doc["label"] if country_doc else ""
        key = norm(city_guess) + "|" + norm(country_name or adoc["url"])
        already = any(s.startswith(norm(city_guess) + "|") for s in city_seen)
        if key in city_seen or (already and not country_doc):
            continue
        # Don't attach a second country to a city already claimed from a hubs table
        if already and country_name:
            # only skip if a hubs-derived entry already exists for this city
            continue
        # If this "city" is only an airport short name already used as code, skip
        if re.fullmatch(r"[A-Z]{3}", city_guess):
            continue
        city_seen.add(key)
        dest = adoc["url"]
        if country_doc:
            anchor = find_anchor_for_term(country_doc["text"], city_guess)
            # New York → #st-ny on the USA page when that heading exists
            dest = f"{country_doc['url']}#{anchor}" if anchor and anchor not in {"federal", "origins", "faq", "main", "hubs"} else country_doc["url"]
        title = f"{city_guess} — {country_name}" if country_name else city_guess
        extra = [city_guess, country_name, adoc["code"], "city", "ciudad"]
        kws = extract_keywords(title, "", "", [], dest, city_guess, extra)
        add(make_page(title, dest, "Cities", kws, title, ""))

    return out


def fallback_en_into_es(en_pages: list[dict], es_urls: set[str]) -> list[dict]:
    """When an ES twin is missing, include the EN information page so
    «París» / «Tokio» still resolve (no invented ES pages)."""
    out = []
    for p in en_pages:
        u = p["u"]
        if u in es_urls or u.startswith("/es/"):
            continue
        # Only fill gaps that matter for ES users: country, city, airport,
        # transport, airline, route, veterans, pro, legal, guides — never
        # commercial pages (already excluded from en_pages).
        if p["y"] not in {
            "Countries",
            "Cities",
            "Airports",
            "Transport",
            "Airlines",
            "Routes",
            "Veterans",
            "Pro",
            "Guides",
            "Hotels",
            "Tools",
            "Legal",
        }:
            continue
        # Skip EN pages that already have an obvious /es twin path
        if ("/es" + u) in es_urls:
            continue
        q = dict(p)
        out.append(q)
    return out


def write_index(lang: str, data: dict) -> tuple[int, int, int]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_OUT.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"search-index.{lang}.json"
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    raw = payload.encode("utf-8")
    out.write_text(payload + "\n", encoding="utf-8")
    (STATIC_OUT / f"search-index.{lang}.json").write_text(payload + "\n", encoding="utf-8")
    gz = len(gzip.compress(raw, compresslevel=9))
    print(f"{out}: {len(data['pages'])} pages, {len(raw)} bytes raw ({len(raw)/1024:.1f} KB), {gz} bytes gzip ({gz/1024:.1f} KB)")
    if gz > 180_000:
        print(f"WARNING: gzip size {gz} exceeds 180KB target", file=sys.stderr)
    return len(data["pages"]), len(raw), gz


def main() -> int:
    raw = {}
    if SYNONYMS.exists():
        raw = json.loads(SYNONYMS.read_text(encoding="utf-8"))
    syn_flat = flatten_synonyms(raw)
    airline_hints = load_airline_hints()

    report = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "langs": {},
        "excluded": {},
    }

    # Build EN first so ES can borrow missing information pages.
    en_pages, en_excl, en_syn = collect_records("en", syn_flat, airline_hints)
    es_pages, es_excl, es_syn = collect_records("es", syn_flat, airline_hints)

    # Dedup synthetics against real pages (same exact URL keeps the richer record,
    # but #hash airport/city entries are kept beside the country page).
    def merge(real: list[dict], synth: list[dict]) -> list[dict]:
        # Same URL is allowed when the title or type differs (Paris city vs
        # France country; CDG vs ORY both pointing at #hubs).
        have = {(p["u"], p["t"], p["y"]) for p in real}
        out = list(real)
        for s in synth:
            key = (s["u"], s["t"], s["y"])
            if key in have:
                continue
            have.add(key)
            out.append(s)
        return out

    en_all = merge(en_pages, en_syn)
    es_all = merge(es_pages, es_syn)
    es_urls = {p["u"] for p in es_all}
    es_all.extend(fallback_en_into_es(en_all, es_urls))

    # Stable order: sitemap-listed first, then type, then url
    sm = sitemap_paths()
    sm_norm = {p if p.endswith("/") or p.endswith(".html") or p == "/" else p + "/" for p in sm}

    def sort_key(p):
        u = p["u"].split("#")[0]
        in_sm = 0 if (u in sm or u in sm_norm or (u.rstrip("/") + "/") in sm) else 1
        return (in_sm, p["y"], p["u"])

    en_all.sort(key=sort_key)
    es_all.sort(key=sort_key)

    syn_out = {k: v for k, v in sorted(syn_flat.items()) if v}

    sizes = {}
    for lang, pages in (("en", en_all), ("es", es_all)):
        data = {
            "lang": lang,
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "synonyms": syn_out,
            "pages": pages,
        }
        n, raw_b, gz = write_index(lang, data)
        from collections import Counter

        types = Counter(p["y"] for p in pages)
        sizes[lang] = {
            "pages": n,
            "bytes": raw_b,
            "gzip": gz,
            "types": dict(types),
        }

    def summarize_excl(items: list[dict]) -> dict:
        from collections import Counter, defaultdict

        c = Counter(x["reason"] for x in items)
        examples = defaultdict(list)
        for x in items:
            if len(examples[x["reason"]]) < 8:
                examples[x["reason"]].append(x["u"])
        return {"count": len(items), "by_reason": dict(c), "examples": dict(examples)}

    report["langs"] = sizes
    report["excluded"]["en"] = summarize_excl(en_excl)
    report["excluded"]["es"] = summarize_excl(es_excl)
    report["synthetics"] = {"en": len(en_syn), "es": len(es_syn)}
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT}")
    print("Excluded EN:", report["excluded"]["en"]["by_reason"], "n=", report["excluded"]["en"]["count"])
    print("Excluded ES:", report["excluded"]["es"]["by_reason"], "n=", report["excluded"]["es"]["count"])
    print("Synthetics EN/ES:", report["synthetics"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
