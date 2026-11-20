#!/usr/bin/env python3
"""Generate /news/ from site/news/_posts/ without running build.py.

Usage:
  python3 news_build.py              # published posts only (empty state if none)
  python3 news_build.py --samples    # include site/news/_samples/ (preview only)
  python3 news_build.py --wire       # one-time sitewide nav, footer, theme, i18n, sprite
  python3 news_build.py --check-reject-test   # confirm missing source fields error out
"""
from __future__ import annotations

import argparse
import calendar
import html
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from email.utils import format_datetime
from pathlib import Path

try:
    import yaml
except ImportError as e:  # pragma: no cover
    raise SystemExit("news_build.py needs PyYAML (pip install pyyaml)") from e
try:
    import markdown
except ImportError as e:  # pragma: no cover
    raise SystemExit("news_build.py needs markdown (pip install markdown)") from e

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"
STATIC = ROOT / "static"
POSTS = SITE / "news" / "_posts"
SAMPLES = SITE / "news" / "_samples"
CACHE = "20261120news1"
ORIGIN = "https://petpolicycheck.com"

CATEGORIES = {
    "cdc-usda": "CDC/USDA",
    "airlines": "Airlines",
    "countries": "Countries & quarantine",
    "adoptions": "Adoptions",
}

NEWS_GLYPH = (
    '<path d="M5 5.6h11.2A1.6 1.6 0 0 1 17.8 7.2v11.6H6.6A1.6 1.6 0 0 1 5 17.2V5.6Z"/>'
    '<path d="M17.8 9.2h1.8A1.4 1.4 0 0 1 21 10.6v7.4a2 2 0 0 1-2 2H6.8"/>'
    '<path d="M7.6 8.8h6.8M7.6 11.6h6.8M7.6 14.4h4.6"/>'
)
NEWS_SYMBOL = (
    '<symbol id="pst-news" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'
    + NEWS_GLYPH + "</symbol>"
)

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
URL_RE = re.compile(r"^https?://", re.I)

I18N_NEWS = {
    "en": "News",
    "fr": "Actualités",
    "es": "Noticias",
    "it": "Notizie",
    "de": "Nachrichten",
    "ko": "뉴스",
    "ja": "ニュース",
}
NAV_LABEL = {"Adoptions": "News", "Adozioni": "Notizie", "Adopciones": "Noticias"}


class NewsBuildError(Exception):
    pass


@dataclass
class Related:
    url: str
    label: str


@dataclass
class Post:
    slug: str
    title: str
    date: date
    category: str
    summary: str
    source_name: str
    source_url: str
    source_date: date
    body_md: str
    updated: date | None = None
    what_this_means: str = ""
    related: list[Related] = field(default_factory=list)
    sample: bool = False
    path: Path | None = None

    @property
    def cat_label(self) -> str:
        return CATEGORIES[self.category]

    @property
    def url(self) -> str:
        return f"{ORIGIN}/news/{self.slug}/"

    @property
    def body_html(self) -> str:
        return markdown.markdown(self.body_md, extensions=["extra", "sane_lists"])

    @property
    def means_html(self) -> str:
        if not self.what_this_means.strip():
            return ""
        return markdown.markdown(self.what_this_means, extensions=["extra", "sane_lists"])


def parse_iso_date(value, field_name: str, src: Path) -> date:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise NewsBuildError(f"{src}: missing required field {field_name}")
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    try:
        return date.fromisoformat(text)
    except ValueError as e:
        raise NewsBuildError(f"{src}: {field_name} must be YYYY-MM-DD, got {value!r}") from e


def parse_related(raw, src: Path) -> list[Related]:
    if not raw:
        return []
    if not isinstance(raw, list):
        raise NewsBuildError(f"{src}: related must be a list")
    out = []
    for item in raw:
        if isinstance(item, str):
            url = item.strip()
            label = url
        elif isinstance(item, dict):
            url = str(item.get("url") or "").strip()
            label = str(item.get("label") or url).strip()
        else:
            raise NewsBuildError(f"{src}: related item must be a URL or {{url, label}}")
        if not url:
            raise NewsBuildError(f"{src}: related item is missing url")
        out.append(Related(url=url, label=label))
    return out


def require_text(meta: dict, key: str, src: Path) -> str:
    val = meta.get(key)
    if val is None or (isinstance(val, str) and not val.strip()):
        raise NewsBuildError(f"{src}: missing required field {key}")
    return str(val).strip()


def post_from_meta(meta: dict, body: str, src: Path, force_sample: bool = False) -> Post:
    missing_source = []
    if not str(meta.get("source_url") or "").strip():
        missing_source.append("source_url")
    if not str(meta.get("source_date") or "").strip() and not isinstance(meta.get("source_date"), date):
        missing_source.append("source_date")
    if missing_source:
        raise NewsBuildError(
            f"{src}: cannot publish without {', '.join(missing_source)}. "
            "Every news item must include source_url and source_date."
        )
    slug = require_text(meta, "slug", src)
    if not SLUG_RE.match(slug):
        raise NewsBuildError(f"{src}: slug must be lowercase letters, numbers and hyphens")
    source_url = require_text(meta, "source_url", src)
    if not URL_RE.match(source_url):
        raise NewsBuildError(f"{src}: source_url must be an http(s) URL")
    category = require_text(meta, "category", src)
    if category not in CATEGORIES:
        raise NewsBuildError(f"{src}: category must be one of {', '.join(CATEGORIES)}")
    body = body.strip()
    if not body:
        raise NewsBuildError(f"{src}: article body is empty")
    sample = force_sample or bool(meta.get("sample"))
    updated = meta.get("updated")
    return Post(
        slug=slug,
        title=require_text(meta, "title", src),
        date=parse_iso_date(meta.get("date"), "date", src),
        category=category,
        summary=require_text(meta, "summary", src),
        source_name=require_text(meta, "source_name", src),
        source_url=source_url,
        source_date=parse_iso_date(meta.get("source_date"), "source_date", src),
        body_md=body,
        updated=parse_iso_date(updated, "updated", src) if updated else None,
        what_this_means=str(meta.get("what_this_means") or "").strip(),
        related=parse_related(meta.get("related"), src),
        sample=sample,
        path=src,
    )


def load_md(path: Path, force_sample: bool = False) -> Post:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise NewsBuildError(f"{path}: expected YAML front matter starting with ---")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise NewsBuildError(f"{path}: front matter is not closed with ---")
    meta = yaml.safe_load(parts[1]) or {}
    if not isinstance(meta, dict):
        raise NewsBuildError(f"{path}: front matter must be a YAML mapping")
    return post_from_meta(meta, parts[2], path, force_sample)


def load_json_post(path: Path, force_sample: bool = False) -> Post:
    meta = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(meta, dict):
        raise NewsBuildError(f"{path}: JSON must be an object")
    body = str(meta.pop("body", "") or "")
    return post_from_meta(meta, body, path, force_sample)


def load_posts(include_samples: bool) -> list[Post]:
    posts: list[Post] = []
    for path in sorted(POSTS.glob("*")):
        if path.name.startswith(".") or path.name == ".gitkeep":
            continue
        if path.suffix.lower() == ".md":
            post = load_md(path)
        elif path.suffix.lower() == ".json":
            post = load_json_post(path)
        else:
            continue
        if post.sample:
            raise NewsBuildError(
                f"{path}: sample items must not live in _posts/. Move this file to site/news/_samples/."
            )
        posts.append(post)
    if include_samples and SAMPLES.is_dir():
        for path in sorted(SAMPLES.glob("*")):
            if path.suffix.lower() == ".md":
                posts.append(load_md(path, force_sample=True))
            elif path.suffix.lower() == ".json":
                posts.append(load_json_post(path, force_sample=True))
    seen = {}
    for p in posts:
        if p.slug in seen:
            raise NewsBuildError(f"duplicate slug {p.slug}: {seen[p.slug]} and {p.path}")
        seen[p.slug] = p.path
    posts.sort(key=lambda p: (p.date, p.slug), reverse=True)
    return posts


def e(text: str) -> str:
    return html.escape(text, quote=True)


def fmt_long(d: date) -> str:
    return f"{d.day} {calendar.month_name[d.month]} {d.year}"


def date_block(d: date) -> str:
    mon = calendar.month_abbr[d.month]
    return (
        f'<div class="news-date" aria-label="{e(fmt_long(d))}">'
        f'<span class="d">{d.day:02d}</span>'
        f'<span class="m">{e(mon)}</span>'
        f'<span class="y">{d.year}</span></div>'
    )


def official_pill() -> str:
    return '<span class="news-official">Official source</span>'


def badge(post: Post) -> str:
    return f'<span class="news-badge cat-{e(post.category)}">{e(post.cat_label)}</span>'

def ga_head() -> str:
    return """<script>
(function(){
  var skip=false;
  try{
    var p=new URLSearchParams(location.search);
    if(p.get('qa')==='0') localStorage.removeItem('ppc_qa');
    else if(p.get('qa')==='1') localStorage.setItem('ppc_qa','1');
    if(p.get('qa')==='1'||localStorage.getItem('ppc_qa')==='1') skip=true;
  }catch(err){}
  if(navigator.webdriver===true) skip=true;
  if(/HeadlessChrome|Headless|PhantomJS|Lighthouse|PageSpeed|GTmetrix|bot|crawler|spider|Playwright|Puppeteer/i.test(navigator.userAgent||'')) skip=true;
  if(skip) return;
  var s=document.createElement('script');
  s.async=true;
  s.src='https://www.googletagmanager.com/gtag/js?id=G-K45B2WNXMC';
  document.head.appendChild(s);
  window.dataLayer=window.dataLayer||[];
  function gtag(){dataLayer.push(arguments);}
  window.gtag=gtag;
  gtag('js',new Date());
  gtag('config','G-K45B2WNXMC');
})();
</script>"""


def menu_script() -> str:
    return """<script>(function(){function init(){var m=document.getElementById('site-menu');if(!m)return;
var T=[].slice.call(document.querySelectorAll('.top .menu-btn,[data-menu-trigger]')),last=null;if(!T.length)return;
function set(o,f,t){m.classList.toggle('open',o);T.forEach(function(x){x.setAttribute('aria-expanded',o?'true':'false')});if(o){last=t||T[0];if(f){var a=m.querySelector('a');if(a)a.focus({preventScroll:true})}}else if(f&&last)last.focus()}
T.forEach(function(b){b.addEventListener('click',function(ev){ev.stopPropagation();var o=!m.classList.contains('open');set(o,ev.detail===0||!b.classList.contains('menu-btn'),b)})});
document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&m.classList.contains('open'))set(false,true)});
document.addEventListener('click',function(ev){if(m.classList.contains('open')&&!m.contains(ev.target))set(false)});
m.addEventListener('click',function(ev){if(ev.target.closest('a'))set(false)});
m.addEventListener('focusout',function(ev){var r=ev.relatedTarget;if(m.classList.contains('open')&&r&&!m.contains(r)&&T.indexOf(r)<0)set(false)})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init()})();</script>"""


def header_nav(root: str, current: str) -> str:
    def cur(name: str) -> str:
        return ' aria-current="page"' if current == name else ""

    return (
        f'<header class="top"><div class="wrap">\n'
        f'<a class="brand" href="{root}" aria-label="PetPolicyCheck — Home"><span class="lbadge"><img src="{root}assets/img/logo-mark-header.png" width="62" height="48" alt="PetPolicyCheck"></span></a>\n'
        f'<nav class="nav menu" id="site-menu" aria-label="Main">'
        f'<a href="{root}?view=map" data-i18n="site.nav.map">World map</a>'
        f'<a href="{root}countries/usa.html#federal">Laws</a>'
        f'<a href="{root}vet-info/">Vet</a>'
        f'<a href="{root}airlines/">Plane</a>'
        f'<a href="{root}hotels/">Hotel</a>'
        f'<a href="{root}grooming/" data-i18n="site.nav.grooming">Grooming</a>'
        f'<a href="{root}products/" data-i18n="site.nav.products">Products</a>'
        f'<a href="{root}taxi/" data-i18n="site.nav.rides">Rides</a>'
        f'<span class="nav-group-sep" aria-hidden="true"></span>'
        f'<a href="{root}forum/" data-i18n="site.nav.forum">Forum</a>'
        f'<a href="{root}k9/">K9</a>'
        f'<a href="{root}veterans/#service-dog-support">Service dogs</a>'
        f'<a class="nav-vet" href="{root}veterans/" data-i18n="site.nav.veterans">Veterans</a>'
        f'<a href="{root}adoptions/" data-i18n="site.nav.adoptions">Adoptions</a>'
        f'<a href="{root}news/" data-i18n="site.nav.news"{cur("news")}>News</a>'
        f'<a class="nav-biz" href="{root}pro/" data-i18n="site.nav.pro">For Business</a>'
        f'<a class="menu-only sub" href="{root}#compare">Compare</a>'
        f'<a class="menu-only sub" href="{root}#gear">Guides</a>'
        f'<a class="menu-only sub" href="{root}updates.html">Updates</a>'
        f'<a class="menu-only sub" href="{root}about.html">About</a></nav>'
        f'<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-menu">'
        f'<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false">'
        f'<path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>'
        f'<span data-i18n="site.nav.menu">Menu</span></button>\n'
        f'</div></header>'
    )


FOOT_RULES = (
    "Airline pet rules change often. Always confirm with the airline and the "
    "destination's official authority before you book. Information here is not "
    "legal or veterinary advice."
)
FB_PATH = "M22 12.07C22 6.48 17.52 2 11.93 2S2 6.48 2 12.07c0 5.02 3.66 9.18 8.44 9.93v-7.03H7.9v-2.9h2.54V9.83c0-2.5 1.49-3.89 3.78-3.89 1.09 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56v1.88h2.78l-.44 2.9h-2.34V22c4.78-.75 8.44-4.91 8.44-9.93z"
X_PATH = "M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.725-8.835L1.254 2.25H8.08l4.253 5.622L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117z"


def footer(root: str) -> str:
    return (
        f'<footer class="foot foot-compact">\n'
        f'<div class="wrap cols">\n'
        f'<div class="fbrand"><p class="wm">PetPolicyCheck</p>'
        f'<p data-i18n="site.foot.rules">{FOOT_RULES}</p>'
        f'<p class="soc"><a href="https://www.facebook.com/profile.php?id=61596615981846" rel="noopener" target="_blank" aria-label="Facebook">'
        f'<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="currentColor"><path d="{FB_PATH}"/></svg></a>'
        f'<a href="https://x.com/PetPolicyCheck" rel="noopener" target="_blank" aria-label="X">'
        f'<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" fill="currentColor"><path d="{X_PATH}"/></svg></a></p></div>\n'
        f'<div><h4><a href="{root}vet-info/" data-i18n="site.foot.vet_info">Vet info</a></h4><ul>'
        f'<li><a href="{root}vet-prep/" data-i18n="site.foot.vet_prep">Vet prep</a></li>'
        f'<li><a href="{root}countries/usa.html#federal" data-i18n="site.nav.health">Health certificate</a></li>'
        f'<li><a href="{root}titer-calculator/" data-i18n="home.tools.titer">Titer countdown</a></li>'
        f'<li><a href="{root}partner-vets/" data-i18n="site.foot.vets">Partner vets</a></li></ul></div>\n'
        f'<div><h4 data-i18n="site.foot.explore">Explore</h4><ul>'
        f'<li><a href="{root}?view=map" data-i18n="site.nav.map">World map</a></li>'
        f'<li><a href="{root}airlines/" data-i18n="site.foot.airlines">Airline policies</a></li>'
        f'<li><a href="{root}airlines/compare/" data-i18n="site.nav.compare">Compare</a></li>'
        f'<li><a href="{root}#gear" data-i18n="site.nav.guides">Guides</a></li>'
        f'<li><a href="{root}updates.html" data-i18n="site.nav.updates">Updates</a></li>'
        f'<li><a href="{root}routes/">Routes</a></li>'
        f'<li><a href="{root}k9/" data-i18n="site.foot.k9">K9</a></li>'
        f'<li><a href="{root}veterans/" data-i18n="site.foot.service_dogs_veterans">Service dogs &amp; Veterans</a></li>'
        f'<li><a href="{root}adoptions/" data-i18n="site.foot.adoptions">Adoptions</a></li>'
        f'<li><a href="{root}news/" data-i18n="site.foot.news">News</a></li>'
        f'<li><a href="{root}fit/">Carrier fit</a></li>'
        f'<li><a href="/planner/">Pet Travel Planner</a></li>'
        f'<li><a href="{root}airport/">Airport pet travel guides</a></li></ul></div>\n'
        f'<div><h4 data-i18n="site.foot.shop">Shop &amp; community</h4><ul>'
        f'<li><a href="{root}products/" data-i18n="site.nav.products">Products</a></li>'
        f'<li><a href="{root}forum/" data-i18n="nav.forum">Forum</a></li>'
        f'<li><a href="{root}forum/pet-travel-stories/" data-i18n="site.foot.stories">Stories</a></li>'
        f'<li><a href="{root}pro/" data-i18n="site.foot.pro">B2B Pet Desk</a></li>'
        f'<li><a href="{root}clinics/usa.html" data-i18n="site.foot.clinics_usa">US clinics</a></li></ul></div>\n'
        f'<div><h4 data-i18n="site.foot.aboutcol">About</h4><ul>'
        f'<li><a href="{root}about.html" data-i18n="site.foot.about">About &amp; disclaimer</a></li>'
        f'<li><a href="{root}terms.html" data-i18n="site.foot.terms">Terms</a></li>'
        f'<li><a href="{root}refund-policy.html" data-i18n="site.foot.refund">Refund policy</a></li>'
        f'<li><a href="{root}privacy.html" data-i18n="site.foot.privacy">Privacy</a></li>'
        f'<li><a href="{root}contact.html" data-i18n="site.foot.contact">Contact</a></li></ul></div>\n'
        f'</div>\n'
        f'<div class="wrap"><p class="disc">© 2026 PetPolicyCheck · Paw Passport. All rights reserved. '
        f'Content, data, design and images may not be copied or reproduced without written permission. '
        f'See <a href="{root}terms.html">Terms</a>.</p></div></footer>\n'
        f'<script src="{root}assets/site-search.js?v=20261117sb2" defer></script>\n'
        f'<script src="{root}assets/ppc-header.js?v=20261110footerk9" defer></script>\n'
        f'</body></html>'
    )


def page_head(*, root: str, title: str, description: str, canonical: str, og_type: str, extra_head: str = "") -> str:
    t, d = e(title), e(description)
    return (
        f'<!doctype html>\n<html lang="en-US" class="theme-news" data-section="news"><head>\n'
        f'<meta charset="utf-8">\n{ga_head()}\n'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        f'<title>{t}</title>\n'
        f'<meta name="description" content="{d}">\n'
        f'<link rel="canonical" href="{e(canonical)}">\n'
        f'<link rel="alternate" hreflang="en" href="{e(canonical)}"/>\n'
        f'<link rel="alternate" hreflang="x-default" href="{e(canonical)}"/>\n'
        f'<link rel="alternate" type="application/rss+xml" title="PetPolicyCheck News" href="{ORIGIN}/news/feed.xml">\n'
        f'<meta property="og:title" content="{t}">\n'
        f'<meta property="og:description" content="{d}">\n'
        f'<meta property="og:type" content="{e(og_type)}">\n'
        f'<meta property="og:locale" content="en_US">\n'
        f'<meta property="og:site_name" content="PetPolicyCheck">\n'
        f'<meta property="og:url" content="{e(canonical)}">\n'
        f'<meta property="og:image" content="{ORIGIN}/img/og-default.jpg">\n'
        f'<meta property="og:image:width" content="1200">\n'
        f'<meta property="og:image:height" content="630">\n'
        f'<meta property="og:image:alt" content="Shih Tzu sitting in a pet stroller carrier in front of a Christmas tree">\n'
        f'<meta name="twitter:card" content="summary_large_image">\n'
        f'<meta name="twitter:title" content="{t}">\n'
        f'<meta name="twitter:description" content="{d}">\n'
        f'<meta name="twitter:image" content="{ORIGIN}/img/og-default.jpg">\n'
        f'<link rel="icon" href="{root}assets/img/favicon.ico" sizes="any">'
        f'<link rel="icon" type="image/png" sizes="32x32" href="{root}assets/img/favicon-32.png">'
        f'<link rel="apple-touch-icon" sizes="180x180" href="{root}assets/img/apple-touch-icon-180.png">\n'
        f'<link rel="preload" href="{root}assets/fonts/inter-var-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
        f'<link rel="preload" href="{root}assets/fonts/marcellus-latin.woff2" as="font" type="font/woff2" crossorigin>\n'
        f'<link rel="stylesheet" href="{root}assets/css/theme.css?v={CACHE}">\n'
        f'<link rel="stylesheet" href="{root}style.css?v=20261112footer4">\n'
        f'<link rel="stylesheet" href="{root}assets/css/ppc-i18n.css?v=20261113nav1">\n'
        f'<link rel="stylesheet" href="{root}assets/css/news.css?v={CACHE}">\n'
        f'<script src="{root}assets/i18n/ui.js?v={CACHE}" defer></script>\n'
        f'<script src="{root}assets/js/ppc-i18n.js?v=20261118es1" defer></script>\n'
        f'<script src="{root}assets/js/pastilles.js?v={CACHE}" defer></script>\n'
        f'<meta name="theme-color" content="#0b1719">\n'
        f'<link rel="stylesheet" href="{root}assets/site-search.css?v=20261117sb2">\n'
        f'{extra_head}\n</head>\n'
        f'<body class="v-c news-page"><a class="skip" href="#main" data-i18n="site.skip">Skip to content</a>\n'
    )


def chips_html() -> str:
    items = [("all", "All")] + list(CATEGORIES.items())
    bits = ['<div class="news-filters" role="toolbar" aria-label="Filter by category">']
    for cid, label in items:
        pressed = "true" if cid == "all" else "false"
        on = " is-on" if cid == "all" else ""
        bits.append(
            f'<button type="button" class="news-chip{on}" data-news-cat="{e(cid)}" '
            f'aria-pressed="{pressed}">{e(label)}</button>'
        )
    bits.append("</div>")
    return "".join(bits)


def filter_js() -> str:
    return """<script>
(function(){
  var grid=document.getElementById('news-list');
  if(!grid) return;
  var chips=[].slice.call(document.querySelectorAll('[data-news-cat]'));
  var none=document.getElementById('news-filter-empty');
  var CATEGORIES_OK={all:1, 'cdc-usda':1, airlines:1, countries:1, adoptions:1};
  function apply(cat){
    cat=cat||'all';
    if(!CATEGORIES_OK[cat]) cat='all';
    chips.forEach(function(c){
      var on=c.getAttribute('data-news-cat')===cat;
      c.classList.toggle('is-on',on);
      c.setAttribute('aria-pressed',on?'true':'false');
    });
    var n=0, cards=grid.querySelectorAll('.news-card');
    cards.forEach(function(card){
      var show=cat==='all'||card.getAttribute('data-cat')===cat;
      card.hidden=!show;
      if(show) n++;
    });
    if(none) none.hidden=!(cards.length && n===0);
    try{
      var url=new URL(location.href);
      if(cat==='all') url.searchParams.delete('cat'); else url.searchParams.set('cat',cat);
      history.replaceState({},'',url);
    }catch(err){}
  }
  chips.forEach(function(c){ c.addEventListener('click', function(){ apply(c.getAttribute('data-news-cat')); }); });
  var start='all';
  try{ start=new URLSearchParams(location.search).get('cat')||'all'; }catch(err){}
  apply(start);
})();
</script>"""


def card_html(post: Post) -> str:
    sample = (
        '<span class="news-badge" style="border-color:var(--news-gold);color:var(--news-gold-l)">Sample</span>'
        if post.sample
        else ""
    )
    return (
        f'<li><a class="news-card" href="/news/{e(post.slug)}/" data-cat="{e(post.category)}">'
        f"{date_block(post.date)}<div class=\"news-card-body\">"
        f'<div class="news-meta">{badge(post)}{sample}{official_pill()}</div>'
        f"<h2>{e(post.title)}</h2>"
        f'<p class="news-sum">{e(post.summary)}</p>'
        f"</div></a></li>"
    )


def empty_state() -> str:
    return (
        '<div class="news-empty" id="news-empty">'
        "<h2>First updates coming soon</h2>"
        "<p>Official pet-travel rule changes from CDC, USDA, airlines and destination authorities will appear here, each with a dated official source.</p>"
        "</div>"
    )


def list_page(posts: list[Post]) -> str:
    root = "../"
    desc = (
        "Official pet-travel rule updates from CDC, USDA, airlines and destination authorities, "
        "each with a dated official source."
    )
    title = "News | PetPolicyCheck"
    sample_banner = ""
    if any(p.sample for p in posts):
        sample_banner = '<p class="news-sample-banner">Sample items — preview only, not published news</p>'
    if posts:
        listing = f'<ul class="news-list" id="news-list">{"".join(card_html(p) for p in posts)}</ul>'
        listing += '<p class="news-filter-empty" id="news-filter-empty" hidden>No items in this category yet.</p>'
    else:
        listing = empty_state()
    body = sample_banner + f'<p class="news-lede">{e(desc)}</p>' + chips_html() + listing
    return (
        page_head(root=root, title=title, description=desc, canonical=f"{ORIGIN}/news/", og_type="website")
        + header_nav(root, "news")
        + menu_script()
        + '<main class="wrap" id="main">'
        + '<section class="news-hero"><h1>News</h1>'
        + body
        + "</section></main>\n"
        + filter_js()
        + footer(root)
    )


def json_ld(post: Post) -> str:
    data = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": post.title,
        "datePublished": post.date.isoformat(),
        "dateModified": (post.updated or post.date).isoformat(),
        "description": post.summary,
        "articleSection": post.cat_label,
        "mainEntityOfPage": {"@type": "WebPage", "@id": post.url},
        "author": {"@type": "Organization", "name": "PetPolicyCheck", "url": ORIGIN + "/"},
        "publisher": {
            "@type": "Organization",
            "name": "PetPolicyCheck",
            "logo": {"@type": "ImageObject", "url": ORIGIN + "/assets/img/logo-full.png"},
        },
        "citation": {
            "@type": "CreativeWork",
            "name": post.source_name,
            "url": post.source_url,
            "datePublished": post.source_date.isoformat(),
        },
        "image": ORIGIN + "/img/og-default.jpg",
    }
    if post.sample:
        data["creativeWorkStatus"] = "Sample / unpublished preview"
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False) + "</script>"


def article_page(post: Post) -> str:
    root = "../../"
    sample = (
        '<p class="news-sample-banner">Sample — preview only, not a published update</p>'
        if post.sample
        else ""
    )
    updated = (
        f'<span class="news-updated">Updated <time datetime="{post.updated.isoformat()}">{e(fmt_long(post.updated))}</time></span>'
        if post.updated
        else ""
    )
    means = ""
    if post.means_html:
        means = (
            '<section class="news-means" id="what-this-means">'
            "<h2>What this means for pet travellers</h2>"
            + post.means_html
            + "</section>"
        )
    related = ""
    if post.related:
        items = "".join(f'<li><a href="{e(r.url)}">{e(r.label)}</a></li>' for r in post.related)
        related = (
            '<nav class="news-related" aria-label="Related pages">'
            "<h2>Related on PetPolicyCheck</h2>"
            f"<ul>{items}</ul></nav>"
        )
    source = (
        f'<aside class="news-source" aria-label="Official source">'
        f'<p class="k">Official source</p>'
        f'<p class="name"><a href="{e(post.source_url)}" rel="noopener" target="_blank">{e(post.source_name)}</a></p>'
        f'<p class="sdate">Source date <strong><time datetime="{post.source_date.isoformat()}">{e(fmt_long(post.source_date))}</time></strong></p>'
        f"</aside>"
    )
    eyebrow = (
        '<div class="sec-eyebrow theme-news">'
        '<span class="pst theme-news pst-lg" aria-hidden="true">'
        '<svg viewBox="0 0 24 24"><use href="#pst-news"/></svg></span>'
        '<span>News</span></div>'
    )
    return (
        page_head(
            root=root,
            title=f"{post.title} | PetPolicyCheck",
            description=post.summary,
            canonical=post.url,
            og_type="article",
            extra_head=json_ld(post),
        )
        + header_nav(root, "news")
        + menu_script()
        + '<main class="wrap" id="main">'
        + eyebrow
        + '<article class="news-article">'
        + '<p class="news-back"><a href="/news/">← All news</a></p>'
        + sample
        + '<header class="news-article-head">'
        + '<div class="news-article-top">'
        + date_block(post.date)
        + "<div>"
        + f'<div class="news-meta">{badge(post)}{official_pill()}</div>'
        + f"<h1>{e(post.title)}</h1>"
        + f'<p class="news-byline"><span>Published <time datetime="{post.date.isoformat()}">{e(fmt_long(post.date))}</time></span>{updated}</p>'
        + "</div></div></header>"
        + source
        + f'<div class="news-body">{post.body_html}</div>'
        + means
        + related
        + "</article></main>\n"
        + footer(root)
    )


def rss_xml(posts: list[Post]) -> str:
    items = []
    for p in posts:
        pub = format_datetime(datetime(p.date.year, p.date.month, p.date.day, 12, 0, tzinfo=timezone.utc))
        desc = e(p.summary) + f" Official source: {e(p.source_name)} ({e(p.source_date.isoformat())})."
        if p.sample:
            desc = "SAMPLE — preview only. " + desc
        items.append(
            "<item>"
            f"<title>{e(p.title)}</title>"
            f"<link>{e(p.url)}</link>"
            f'<guid isPermaLink="true">{e(p.url)}</guid>'
            f"<pubDate>{pub}</pubDate>"
            f"<category>{e(p.cat_label)}</category>"
            f"<description>{desc}</description>"
            "</item>"
        )
    built = format_datetime(datetime.now(timezone.utc))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "<channel>\n"
        "<title>PetPolicyCheck News</title>\n"
        f"<link>{ORIGIN}/news/</link>\n"
        "<description>Official pet-travel rule updates from CDC, USDA, airlines and destination authorities, each with a dated official source.</description>\n"
        "<language>en-us</language>\n"
        f"<lastBuildDate>{built}</lastBuildDate>\n"
        f'<atom:link href="{ORIGIN}/news/feed.xml" rel="self" type="application/rss+xml"/>\n'
        + "\n".join(items)
        + ("\n" if items else "")
        + "</channel>\n</rss>\n"
    )


def update_sitemap(posts: list[Post]) -> None:
    lastmod = max([p.date for p in posts], default=date(2026, 11, 20)).isoformat()
    block = f"<url><loc>{ORIGIN}/news/</loc><lastmod>{lastmod}</lastmod></url>" + "".join(
        f"<url><loc>{p.url}</loc><lastmod>{(p.updated or p.date).isoformat()}</lastmod></url>"
        for p in posts
    )
    for path in (SITE / "sitemap.xml", STATIC / "sitemap.xml"):
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r"<url><loc>https://petpolicycheck\.com/news/[^<]*</loc><lastmod>[^<]*</lastmod></url>",
            "",
            text,
        )
        # origin/main sitemap currently ends with a dangling "<" and no closing urlset.
        # Repair only the close so new /news/ entries can be appended; do not rebuild the full map.
        text = text.rstrip()
        if text.endswith("<"):
            text = text[:-1].rstrip()
        if "</urlset>" not in text:
            if not text.endswith(">"):
                raise NewsBuildError(f"{path} looks truncated and cannot be repaired safely")
            text = text + block + "</urlset>"
        else:
            text = text.replace("</urlset>", block + "</urlset>")
        if not text.endswith("\n"):
            text += "\n"
        path.write_text(text, encoding="utf-8")


def mirror_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def clear_generated_articles(keep: set[str]) -> None:
    for base in (SITE / "news", STATIC / "news"):
        if not base.is_dir():
            continue
        for child in base.iterdir():
            if child.name in {"_posts", "_samples", "index.html", "feed.xml"}:
                continue
            if child.is_dir() and child.name not in keep:
                shutil.rmtree(child)


def write_generated(posts: list[Post]) -> None:
    news_dir = SITE / "news"
    news_dir.mkdir(parents=True, exist_ok=True)
    (news_dir / "index.html").write_text(list_page(posts), encoding="utf-8")
    (news_dir / "feed.xml").write_text(rss_xml(posts), encoding="utf-8")
    keep = {p.slug for p in posts}
    clear_generated_articles(keep)
    for p in posts:
        d = news_dir / p.slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(article_page(p), encoding="utf-8")
    static_news = STATIC / "news"
    static_news.mkdir(parents=True, exist_ok=True)
    (static_news / "index.html").write_text(list_page(posts), encoding="utf-8")
    (static_news / "feed.xml").write_text(rss_xml(posts), encoding="utf-8")
    for p in posts:
        d = static_news / p.slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(article_page(p), encoding="utf-8")
    if POSTS.exists():
        mirror_tree(POSTS, static_news / "_posts")
    if SAMPLES.exists():
        mirror_tree(SAMPLES, static_news / "_samples")
    css = SITE / "assets" / "css" / "news.css"
    if css.exists():
        dst = STATIC / "assets" / "css" / "news.css"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(css, dst)
    update_sitemap(posts)


def patch_theme(css: str) -> str:
    if "--theme-news" in css and "data-sec=\"news\"" in css:
        return css
    css = css.replace(
        " --theme-grooming:#c6a4db; /* Lavande savon / iris minéral */\n --theme-accent:var(--pri);",
        " --theme-grooming:#c6a4db; /* Lavande savon / iris minéral */\n"
        " --theme-news:#3e8e8a;    /* Gazette teal — News (unused elsewhere) */\n"
        " --theme-accent:var(--pri);",
    )
    css = css.replace(
        ".theme-forum{--theme-accent:var(--theme-forum)}.theme-grooming{--theme-accent:var(--theme-grooming)}",
        ".theme-forum{--theme-accent:var(--theme-forum)}.theme-grooming{--theme-accent:var(--theme-grooming)}\n"
        ".theme-news{--theme-accent:var(--theme-news)}",
    )
    css = css.replace(
        "  --theme-adoptions: #d1848c; /* Rose foyer / old rose — Adoptions */\n}",
        "  --theme-adoptions: #d1848c; /* Rose foyer / old rose — Adoptions */\n"
        "  --theme-news: #3e8e8a; /* Gazette teal — News */\n}",
    )
    css = css.replace(
        ":root{--theme-vet:#7cc9b5;--theme-k9:#cfa57a;--theme-service:#86aee6;--theme-adoptions:#d1848c}",
        ":root{--theme-vet:#7cc9b5;--theme-k9:#cfa57a;--theme-service:#86aee6;--theme-adoptions:#d1848c;--theme-news:#3e8e8a}",
    )
    css = css.replace(
        ".theme-adoptions{--theme-accent:var(--theme-adoptions)}",
        ".theme-adoptions{--theme-accent:var(--theme-adoptions)}.theme-news{--theme-accent:var(--theme-news)}",
    )
    css = css.replace(
        '.theme-adoptions,[data-sec="adoptions"]{--sec:#d1848c}',
        '.theme-adoptions,[data-sec="adoptions"]{--sec:#d1848c}\n'
        '.theme-news,     [data-sec="news"]{--sec:#3e8e8a}',
    )
    return css


def patch_pastilles(js: str) -> str:
    if "tgt('news/')" in js and "news:'<path" in js:
        return js
    if "news:'<path" not in js:
        js = js.replace(
            " adoptions:'<path d=\"M3.8 11.5 12 4.2l8.2 7.3\"/><path d=\"M5.6 10.6v9.2h12.8v-9.2\"/><path d=\"M10 19.8v-5.4h4v5.4\"/>'\n};",
            " adoptions:'<path d=\"M3.8 11.5 12 4.2l8.2 7.3\"/><path d=\"M5.6 10.6v9.2h12.8v-9.2\"/><path d=\"M10 19.8v-5.4h4v5.4\"/>',\n"
            f" news:'{NEWS_GLYPH}'\n}};",
        )
    js = js.replace(
        "/\\/adoptions\\//.test(path)?'adoptions':",
        "/\\/news\\//.test(path)?'news':/\\/adoptions\\//.test(path)?'adoptions':",
    )
    js = js.replace(
        "adoptions:'Adozioni',b2b:'Per le aziende'",
        "adoptions:'Adozioni',news:'Notizie',b2b:'Per le aziende'",
    )
    js = js.replace(
        "adoptions:'Adopciones',b2b:'Para empresas'",
        "adoptions:'Adopciones',news:'Noticias',b2b:'Para empresas'",
    )
    js = js.replace(
        "adoptions:'Adoptions',b2b:'Pour les pros'",
        "adoptions:'Adoptions',news:'Actualités',b2b:'Pour les pros'",
    )
    js = js.replace(
        "   adoptions:['Adoptions','Adozioni','Adopciones','Adoptions'],\n   b2b:",
        "   adoptions:['Adoptions','Adozioni','Adopciones','Adoptions'],\n"
        "   news:['News','Notizie','Noticias','Actualités'],\n   b2b:",
    )
    js = js.replace(
        "['adoptions',tgt('adoptions/')],['b2b',tgt('pro/')]",
        "['adoptions',tgt('adoptions/')],['news',tgt('news/')],['b2b',tgt('pro/')]",
    )
    js = js.replace(
        "adoptions:'site.nav.adoptions',b2b:'site.nav.pro'",
        "adoptions:'site.nav.adoptions',news:'site.nav.news',b2b:'site.nav.pro'",
    )
    js = js.replace(
        ",adoptions:plab('Adoptions','adoptions')};",
        ",adoptions:plab('Adoptions','adoptions'),news:plab('News','news')};",
    )
    return js


def patch_ui_js(text: str) -> str:
    prefix, json_text = text.split("=", 1)
    payload = json.loads(json_text.rstrip().rstrip(";"))
    for lang, label in I18N_NEWS.items():
        strings = payload["strings"][lang]
        strings["site.nav.news"] = label
        strings["site.foot.news"] = label
    return prefix + "=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"


def patch_ui_json(path: Path) -> None:
    if not path.exists():
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    for lang, label in I18N_NEWS.items():
        if lang in data.get("strings", {}):
            data["strings"][lang]["site.nav.news"] = label
            data["strings"][lang]["site.foot.news"] = label
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def news_href_from_adoptions(href: str) -> str:
    if href.endswith("adoptions/"):
        return href[: -len("adoptions/")] + "news/"
    if href.endswith("/adoptions"):
        return href[: -len("adoptions")] + "news"
    return href.replace("adoptions", "news")


NAV_ADOPT = re.compile(
    r'(<a href="([^"]*)" data-i18n="site\.nav\.adoptions"(?: aria-current="page")?>)([^<]*)(</a>)'
    r'(?!\s*<a[^>]*data-i18n="site\.nav\.news")'
)
FOOT_ADOPT = re.compile(
    r'(<li><a href="([^"]*)" data-i18n="site\.foot\.adoptions">)([^<]*)(</a></li>)'
    r'(?!<li><a[^>]*data-i18n="site\.foot\.news")'
)


def inject_nav(html_text: str) -> str:
    def nav_sub(m):
        label = NAV_LABEL.get(m.group(3), "News")
        return (
            f'{m.group(0)}'
            f'<a href="{news_href_from_adoptions(m.group(2))}" data-i18n="site.nav.news">{label}</a>'
        )

    def foot_sub(m):
        label = NAV_LABEL.get(m.group(3), "News")
        return (
            f'{m.group(0)}'
            f'<li><a href="{news_href_from_adoptions(m.group(2))}" data-i18n="site.foot.news">{label}</a></li>'
        )

    html_text = NAV_ADOPT.sub(nav_sub, html_text)
    html_text = FOOT_ADOPT.sub(foot_sub, html_text)
    html_text = re.sub(r"theme\.css\?v=[^\"']+", f"theme.css?v={CACHE}", html_text)
    html_text = re.sub(r"i18n/ui\.js\?v=[^\"']+", f"i18n/ui.js?v={CACHE}", html_text)
    html_text = re.sub(r"pastilles\.js\?v=[^\"']+", f"pastilles.js?v={CACHE}", html_text)
    if 'id="ppc-pst-sprite"' in html_text and 'id="pst-news"' not in html_text:
        if 'id="pst-adoptions"' in html_text:
            html_text = re.sub(
                r'(<symbol id="pst-adoptions"[^>]*>.*?</symbol>)',
                r"\1" + NEWS_SYMBOL,
                html_text,
                count=1,
                flags=re.S,
            )
        else:
            html_text = html_text.replace(
                'id="ppc-pst-sprite">',
                'id="ppc-pst-sprite">' + NEWS_SYMBOL,
                1,
            )
    return html_text


def wire_site() -> None:
    for rel in (
        Path("assets/css/theme.css"),
        Path("assets/js/pastilles.js"),
        Path("assets/i18n/ui.js"),
    ):
        for base in (SITE, STATIC):
            path = base / rel
            text = path.read_text(encoding="utf-8")
            if rel.name == "theme.css":
                new = patch_theme(text)
            elif rel.name == "pastilles.js":
                new = patch_pastilles(text)
            else:
                new = patch_ui_js(text)
            if new != text:
                path.write_text(new, encoding="utf-8")
                print(f"wired {path.relative_to(ROOT)}")
            else:
                print(f"unchanged {path.relative_to(ROOT)}")
    patch_ui_json(ROOT / "data" / "i18n" / "ui.json")
    build_py = ROOT / "build.py"
    bp = build_py.read_text(encoding="utf-8")
    if '("news/", "News", "site.nav.news", "")' not in bp:
        bp = bp.replace(
            '("adoptions/", "Adoptions", "site.nav.adoptions", ""), ("pro/", "For Business", "site.nav.pro", "nav-biz")]',
            '("adoptions/", "Adoptions", "site.nav.adoptions", ""), ("news/", "News", "site.nav.news", ""), ("pro/", "For Business", "site.nav.pro", "nav-biz")]',
        )
        bp = bp.replace(
            '{li(root + "adoptions/", "site.foot.adoptions", "Adoptions")}<li><a href="{root}fit/">Carrier fit</a></li>',
            '{li(root + "adoptions/", "site.foot.adoptions", "Adoptions")}{li(root + "news/", "site.foot.news", "News")}<li><a href="{root}fit/">Carrier fit</a></li>',
        )
        build_py.write_text(bp, encoding="utf-8")
        print("wired build.py (not run)")
    nav_n = foot_n = sprite_n = pages = 0
    for base in (SITE, STATIC):
        for path in base.rglob("*.html"):
            pages += 1
            old = path.read_text(encoding="utf-8")
            new = inject_nav(old)
            if new != old:
                if 'data-i18n="site.nav.news"' in new and 'data-i18n="site.nav.news"' not in old:
                    nav_n += 1
                if 'data-i18n="site.foot.news"' in new and 'data-i18n="site.foot.news"' not in old:
                    foot_n += 1
                if 'id="pst-news"' in new and 'id="pst-news"' not in old:
                    sprite_n += 1
                path.write_text(new, encoding="utf-8")
    print(f"html pages scanned {pages}; nav inserted on {nav_n}; footer on {foot_n}; sprite symbol on {sprite_n}")


def reject_test() -> None:
    tmp = POSTS / ".tmp-reject-test.md"
    POSTS.mkdir(parents=True, exist_ok=True)
    tmp.write_text(
        "---\nslug: reject-test\ntitle: Missing source\ndate: 2026-11-20\n"
        "category: airlines\nsummary: x\nsource_name: Test\n---\nBody.\n",
        encoding="utf-8",
    )
    try:
        try:
            load_md(tmp)
        except NewsBuildError as err:
            msg = str(err)
            if "source_url" in msg and "source_date" in msg:
                print("reject-test OK:", msg)
                return
            raise SystemExit(f"reject-test failed: unexpected error: {msg}")
        raise SystemExit("reject-test failed: missing source fields were accepted")
    finally:
        tmp.unlink(missing_ok=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build PetPolicyCheck /news/ without build.py")
    parser.add_argument("--samples", action="store_true", help="Include _samples/ items (preview only)")
    parser.add_argument("--wire", action="store_true", help="Wire nav, footer, theme, i18n and sprite sitewide")
    parser.add_argument("--check-reject-test", action="store_true")
    args = parser.parse_args(argv)
    if args.check_reject_test:
        reject_test()
        return 0
    if args.wire:
        wire_site()
    POSTS.mkdir(parents=True, exist_ok=True)
    (POSTS / ".gitkeep").write_text("", encoding="utf-8")
    try:
        posts = load_posts(include_samples=args.samples)
    except NewsBuildError as err:
        print(f"ERROR: {err}", file=sys.stderr)
        return 1
    write_generated(posts)
    kind = "with samples" if args.samples else "published only"
    print(f"Built /news/ ({kind}): {len(posts)} item(s). List {'empty state' if not posts else 'has cards'}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
