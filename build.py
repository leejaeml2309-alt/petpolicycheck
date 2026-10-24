#!/usr/bin/env python3
"""Static site generator for the airline pet policy directory.

Stdlib only. Reads config.json + data/airlines/*.json + data/updates.json,
writes the site to ./site/.  Usage:  python3 build.py
"""
import hashlib
import datetime as dt
import html
import json
import re
import urllib.parse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "forum"))
import forum_pages  # noqa: E402  (forum/forum_pages.py)
DATA = ROOT / "data" / "airlines"
OUT = ROOT / "site"
CHECK = "Check with airline"

FIELDS = [  # (key, label) -- the 9 policy fields counted as confirmed/null
    ("in_cabin_allowed", "Pets in cabin"),
    ("species", "Species accepted"),
    ("max_carrier_dimensions", "Max carrier size"),
    ("max_combined_weight", "Max weight (pet + carrier)"),
    ("fees", "Fees"),
    ("checked_or_cargo", "Checked bag / cargo option"),
    ("banned_breeds", "Breed restrictions"),
    ("banned_routes", "Route restrictions"),
    ("service_animal_note", "Service animals"),
]


def e(s):
    return html.escape("" if s is None else str(s), quote=True)


def load():
    cfg = json.loads((ROOT / "config.json").read_text())
    airlines = [json.loads(p.read_text()) for p in sorted(DATA.glob("*.json"))]
    airlines.sort(key=lambda a: a["name"].lower())
    upd_path = ROOT / "data" / "updates.json"
    updates = json.loads(upd_path.read_text()) if upd_path.exists() else []
    return cfg, airlines, updates


def nice_date(iso):
    if not iso:
        return "not yet verified"
    d = dt.date.fromisoformat(iso[:10])
    return d.strftime("%b %-d, %Y")


def yn(v):
    return CHECK if v is None else ("Yes" if v else "No")


def yn_badge(v):
    cls = "b-check" if v is None else ("b-yes" if v else "b-no")
    return f'<span class="badge {cls}">{e(yn(v))}</span>'


def val(a, key):
    v = a.get(key)
    if key == "in_cabin_allowed":
        return yn_badge(v)
    if v is None or v == []:
        return f'<span class="na">{CHECK}</span>'
    if key == "fees":
        return "<ul class='fees'>" + "".join(
            f"<li><b>{e(f['route'])}:</b> {e(f['amount'])}</li>" for f in v) + "</ul>"
    return e(v)


def plain(a, key):
    v = a.get(key)
    if key == "in_cabin_allowed":
        return yn(v)
    if v is None or v == []:
        return CHECK
    if key == "fees":
        return "; ".join(f"{f['route']}: {f['amount']}" for f in v)
    return str(v)


def short_fee(a):
    f = a.get("fees")
    return CHECK if not f else f[0]["amount"]


def confirmed_count(a):
    return sum(1 for k, _ in FIELDS if a.get(k) not in (None, []))


def affiliate_box(cfg):
    links = [v for v in cfg.get("affiliates", {}).values() if v.get("url")]
    if not links:
        return ""
    items = "".join(f'<li><a href="{e(l["url"])}" rel="sponsored nofollow noopener" target="_blank">{e(l["label"])}</a></li>' for l in links)
    return ('<aside class="reco"><h2>Recommended gear &amp; insurance</h2><ul>' + items +
            '</ul><p class="small">Affiliate links: we may earn a commission at no cost to you. '
            '<a href="{root}about.html#affiliates">Disclosure</a>.</p></aside>')


def site_base(cfg):
    """Absolute site root WITHOUT trailing slash, e.g. https://example.com or
    https://user.github.io/repo. Single source: config.json site_url + base_path."""
    url = cfg.get("site_url")
    if url is None:  # legacy config
        return site_base(cfg)
    bp = cfg.get("base_path", "/").strip("/")
    return url.rstrip("/") + (f"/{bp}" if bp else "")


def custom_domain(cfg):
    """Host for the Pages CNAME file when serving from a custom domain root."""
    from urllib.parse import urlparse
    host = urlparse(cfg.get("site_url", "")).hostname or ""
    if cfg.get("base_path", "/").strip("/") or not host or host.endswith(".github.io"):
        return ""
    return host


ADSENSE = '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7693501377730690" crossorigin="anonymous"></script>'
TP_DRIVE = '<script nowprocket data-noptimize="1" data-cfasync="false" data-wpfc-render="false" seraph-accel-crit="1" data-no-defer="1" data-cmp-ab="2">\n  (function () {\n      var script = document.createElement("script");\n      script.async = 1;\n      script.setAttribute("data-cmp-ab","2");\n      script.src = \'https://emrldtp.cc/NTg4ODAy.js?t=588802\';\n      document.head.appendChild(script);\n  })();\n</script>'


LOGO = ('<svg class="logo" viewBox="0 0 40 40" width="38" height="38" aria-hidden="true" focusable="false">'
        '<circle cx="20" cy="20" r="19" fill="#1d4f55"/><circle cx="20" cy="20" r="16.4" fill="none" stroke="#d9b765" stroke-width=".9"/>'
        '<g fill="#f5efe0"><ellipse cx="12.6" cy="18.6" rx="2.1" ry="2.7" transform="rotate(-18 12.6 18.6)"/><ellipse cx="16.4" cy="14.4" rx="2.1" ry="2.8"/>'
        '<ellipse cx="21.6" cy="14.4" rx="2.1" ry="2.8"/><ellipse cx="25.4" cy="18.6" rx="2.1" ry="2.7" transform="rotate(18 25.4 18.6)"/>'
        '<path d="M19 19.6c-3.4 0-6.2 3.9-6.2 6.4 0 1.8 1.3 2.6 2.9 2.6 1.3 0 2.1-.7 3.3-.7s2 .7 3.3.7c1.6 0 2.9-.8 2.9-2.6 0-2.5-2.8-6.4-6.2-6.4z"/></g>'
        '<path d="M11.2 25.6c-2.4-.5-3 2.4-.9 2.9M10.3 28.5c3.4 5 10.6 6.5 16 3.7 4.2-2.2 6.3-6.1 6.3-10.2" fill="none" stroke="#d9b765" stroke-width="1.2" stroke-linecap="round"/>'
        '<path d="M0-5l1 .6v3l4 2.4v1l-4-1.1v2.5l1.3 1v.8L0 4.8l-2.3.4v-.8l1.3-1V.8l-4 1.1v-1l4-2.4v-3z" fill="#d9b765" transform="translate(29.6 13.4) rotate(32) scale(.62)"/></svg>')
# Main nav: identical to the design-C home header (static/home-c.html). (href, label, i18n key, aria-current path prefixes)
# "#..." hrefs point to sections / panels of the home page ({home}#airlines opens the airline panel on load).
NAV = [("#map", "World map", "site.nav.map", ()), ("book/", "Book", "site.nav.book", ("book/",)), ("#airlines", "Airlines", "site.nav.airlines", ("airlines/",)),
       ("countries/usa.html#federal", "Health certificate", "site.nav.health", ()),  # no dedicated page yet: USA federal rules (CDC/USDA) section, leads to the state CVI table
       ("#compare", "Compare", "site.nav.compare", ()), ("products/", "Products", "site.nav.products", ("products/",)),
       ("#gear", "Guides", "site.nav.guides", ()), ("updates.html", "Updates", "site.nav.updates", ("updates.html",)),
       ("about.html", "About", "site.nav.about", ("about.html",)), ("advertise/", "Advertise", "site.nav.advertise", ("advertise/",))]
LOGO_BADGE = '<span class="lbadge"><img src="{root}assets/img/logo-mark-header.png" width="62" height="48" alt="" aria-hidden="true"></span>'


def brand_word(name):
    """Wordmark: same text, last word tinted (PetPolicy|Check)."""
    if name.endswith("Check"):
        return f'<span class="wm">{e(name[:-5])}<span>Check</span></span>'
    return f'<span class="wm">{e(name)}</span>'


FORUM_NAV = ("forum/", "Forum", ("forum/",))


def ti(key, on):
    """data-i18n attribute for the shared header/footer on forum pages (forum.js translates it client-side)."""
    return f' data-i18n="{key}"' if on else ""
FORUM_ON = False  # set in main() from config.json forum.* (Forum link only when the backend is configured)


def home_url(root):
    """Relative link to the home page root ("./" or "../"), never index.html (canonical is /)."""
    return root or "./"


def nav_links(root, path, i18n=False):
    out = []
    items = NAV[:7] + [(FORUM_NAV[0], FORUM_NAV[1], "nav.forum", FORUM_NAV[2])] + NAV[7:] if FORUM_ON else NAV  # Forum after Guides, before Updates
    for href, label, key, pre in items:
        cur = ' aria-current="page"' if any(path.startswith(x) for x in pre) else ""
        url = home_url(root) + href if href.startswith("#") else root + href
        cta = ' class="cta menu-only"' if href == "advertise/" else (' class="nav-book"' if href == "book/" else "")
        out.append(f'<a{cta} href="{url}"{cur}{ti(key, i18n)}>{label}</a>')
    return "".join(out)


# Header (fix6 v3): logo + horizontal nav (10 links) in the header row; under ~1100px the nav collapses into the "Menu" dropdown
# (which also shows Advertise). A leaderboard ad band sits below the header line, site-wide.
ADSENSE_CLIENT = "ca-pub-7693501377730690"
MENU_BTN = ('<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-menu">'
            '<svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true" focusable="false"><path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>'
            '<span>Menu</span></button>')
MENU_JS = """<script>(function(){function init(){var m=document.getElementById('site-menu');if(!m)return;
var T=[].slice.call(document.querySelectorAll('.top .menu-btn,[data-menu-trigger]')),last=null;if(!T.length)return;
function set(o,f,t){m.classList.toggle('open',o);T.forEach(function(x){x.setAttribute('aria-expanded',o?'true':'false')});if(o){last=t||T[0];if(f){var a=m.querySelector('a');if(a)a.focus({preventScroll:true})}}else if(f&&last)last.focus()}
T.forEach(function(b){b.addEventListener('click',function(e){e.stopPropagation();var o=!m.classList.contains('open');set(o,e.detail===0||!b.classList.contains('menu-btn'),b)})});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&m.classList.contains('open'))set(false,true)});
document.addEventListener('click',function(e){if(m.classList.contains('open')&&!m.contains(e.target))set(false)});
m.addEventListener('click',function(e){if(e.target.closest('a'))set(false)});
m.addEventListener('focusout',function(e){var r=e.relatedTarget;if(m.classList.contains('open')&&r&&!m.contains(r)&&T.indexOf(r)<0)set(false)})}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init()})();</script>"""


def header_ad(cfg, ads=True):
    """Leaderboard ad band below the header line (728x90 desktop and tablet, 320x100 phone; fixed min-height = no layout shift).
    config.json "adsense_header_slot": AdSense ad-unit id for this slot. Empty -> clean placeholder (dashed gold box,
    'Advertisement' label) and the <ins> kept as a commented TODO. Pages built with ads=False always get the placeholder."""
    slot = str(cfg.get("adsense_header_slot") or "").strip()
    if ads and slot:
        return ('<div class="hdr-band"><div class="wrap"><div class="hdr-ad" role="complementary" aria-label="Advertisement"><div class="hdr-box"><span class="adl">Advertisement</span>'
                f'<ins class="adsbygoogle hdr-ins" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="{e(slot)}"></ins>'
                '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div></div></div></div>')
    todo = (f'<!-- TODO header ad: create a 728x90 / responsive display unit in AdSense, put its id in config.json "adsense_header_slot" '
            f'(build.py then renders <ins class="adsbygoogle hdr-ins" data-ad-client="{ADSENSE_CLIENT}" data-ad-slot="REPLACE_WITH_HEADER_AD_SLOT_ID">) -->')
    return f'<div class="hdr-band"><div class="wrap"><div class="hdr-ad empty" role="complementary" aria-label="Advertisement"><div class="hdr-box"><span class="adl">Advertisement</span>{todo}</div></div></div></div>'


def site_footer(cfg, root, fi):
    """Footer identical to the design-C home footer (4 columns), plus the sponsor slot."""
    h = home_url(root)
    li = lambda href, key, label: f'<li><a href="{href}"{ti(key, fi)}>{label}</a></li>'
    forum = (li(f"{root}forum/", "nav.forum", "Forum") + li(f"{root}forum/pet-travel-stories/", "site.foot.stories", "Stories")) if FORUM_ON else ""
    return f"""<footer class="foot">
<div class="wrap">{ad_slot(cfg, "sidebar_or_footer", root, fi)}</div>
<div class="wrap cols">
<div><p class="wm">{e(cfg['site_name'])}</p><p{ti("site.foot.rules", fi)}>Airline pet rules change often. Always confirm with the airline and the destination's official authority before you book. Information here is not legal or veterinary advice.</p></div>
<div><h4{ti("site.foot.explore", fi)}>Explore</h4><ul>{li(h + "#map", "site.nav.map", "World map")}{li(root + "book/", "site.nav.book", "Book your trip")}{li(h + "#airlines", "site.foot.airlines", "Airline policies")}{li(root + "countries/usa.html#federal", "site.nav.health", "Health certificate")}{li(h + "#compare", "site.nav.compare", "Compare")}{li(h + "#gear", "site.nav.guides", "Guides")}{li(root + "updates.html", "site.nav.updates", "Updates")}</ul></div>
<div><h4{ti("site.foot.shop", fi)}>Shop &amp; community</h4><ul>{li(root + "products/", "site.nav.products", "Products")}{forum}{li(root + "advertise/", "site.nav.advertise", "Advertise")}{li(root + "partner-vets/", "site.foot.vets", "Partner vets")}</ul></div>
<div><h4{ti("site.foot.aboutcol", fi)}>About</h4><ul>{li(root + "about.html", "site.foot.about", "About &amp; disclaimer")}{li(root + "privacy.html", "site.foot.privacy", "Privacy")}{li(root + "contact.html", "site.foot.contact", "Contact")}</ul></div>
</div><div class="wrap"><p class="disc"><span{ti("site.foot.aff", fi)}>Some links may be affiliate links; we may earn a commission at no extra cost to you. This never affects our data.</span> &copy; {dt.date.today().year} {e(cfg['site_name'])}</p></div></footer>"""


def css_version():
    import hashlib
    return hashlib.sha1((ROOT / "static" / "style.css").read_bytes() + (ROOT / "static" / "assets" / "css" / "theme.css").read_bytes()).hexdigest()[:8]


CSS_VER = css_version()


OG_IMAGE = "img/og-default.jpg"
OG_SIZE = (1200, 630)


def og_alt(cfg):
    h = (cfg.get("hero_images") or [{}])[0]
    return (h.get("alt") if isinstance(h, dict) else "") or cfg["site_name"]


def verification_meta(cfg):
    """Search-console ownership tags from config.json (empty = omitted)."""
    out = ""
    for key, name in (("google_site_verification", "google-site-verification"), ("bing_site_verification", "msvalidate.01"), ("pinterest_site_verification", "p:domain_verify")):
        v = (cfg.get(key) or "").strip()
        if v:
            out += f'\n<meta name="{name}" content="{e(v)}">'
    return out


def build_og_image(cfg):
    """1200x630 JPEG share image (og:image / twitter:image) from the first hero photo, metadata-free."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("  WARNING: Pillow not installed; og image skipped")
        return
    it = (cfg.get("hero_images") or [None])[0]
    if not it:
        return
    src, crop = (it, None) if isinstance(it, str) else (it.get("src", ""), it.get("crop"))
    rel = src.split("static/", 1)[-1]
    rel = rel if rel.startswith("img/") else "img/" + rel
    im = ImageOps.exif_transpose(Image.open(ROOT / "static" / rel)).convert("RGB")
    W, H = im.size
    if crop:  # keep the configured subject box, widened horizontally toward 1.9:1 if possible
        x0, y0, x1, y1 = crop[0] * W, crop[1] * H, crop[2] * W, crop[3] * H
        cx, ch = (x0 + x1) / 2, y1 - y0
        cw = min(W, ch * OG_SIZE[0] / OG_SIZE[1])
        ch = cw * OG_SIZE[1] / OG_SIZE[0]
        cy = (y0 + y1) / 2
        L = min(max(0, cx - cw / 2), W - cw); T = min(max(0, cy - ch / 2), H - ch)
        im = im.crop((round(L), round(T), round(L + cw), round(T + ch)))
    im = ImageOps.fit(im, OG_SIZE, Image.LANCZOS)
    clean = Image.new("RGB", im.size); clean.paste(im)
    (OUT / "img").mkdir(exist_ok=True)
    clean.save(OUT / OG_IMAGE, "JPEG", quality=82, optimize=True, progressive=True)


def page(cfg, title, desc, body, path, root, jsonld=None, canonical=None, noindex=False, ads=True):
    base = site_base(cfg)
    canon = canonical or f"{base}/{path}"
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    fi = FORUM_ON and path.startswith("forum/")  # forum pages: shared header/footer labels follow the forum language
    return f"""<!doctype html>
<html lang="{e(cfg.get('language','en-US'))}">
<head>
<meta charset="utf-8">
<meta name="impact-site-verification" value="60bdcaa0-2f59-492a-85f2-bf25a93a4644">
{ADSENSE + chr(10) + TP_DRIVE if ads else ''}
<meta name="viewport" content="width=device-width,initial-scale=1">{chr(10) + '<meta name="robots" content="noindex,follow">' if noindex else ''}
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_US">
<meta property="og:site_name" content="{e(cfg['site_name'])}">
<meta property="og:url" content="{e(canon)}">
<meta property="og:image" content="{e(base + '/' + OG_IMAGE)}">
<meta property="og:image:width" content="{OG_SIZE[0]}">
<meta property="og:image:height" content="{OG_SIZE[1]}">
<meta property="og:image:alt" content="{e(og_alt(cfg))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{e(base + '/' + OG_IMAGE)}">{verification_meta(cfg)}
<link rel="icon" href="{root}assets/img/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="{root}assets/img/favicon-32.png"><link rel="apple-touch-icon" sizes="180x180" href="{root}assets/img/apple-touch-icon-180.png">
<link rel="preload" href="{root}assets/fonts/inter-var-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{root}assets/fonts/marcellus-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{root}assets/css/theme.css?v={CSS_VER}">
<link rel="stylesheet" href="{root}style.css?v={CSS_VER}">
<meta name="theme-color" content="#0b1719">
{ld}
</head>
<body class="v-c">
<a class="skip" href="#main"{ti("site.skip", fi)}>Skip to content</a>
<header class="top"><div class="wrap">
<a class="brand" href="{home_url(root)}">{LOGO_BADGE.replace('{root}', root)}{brand_word(cfg['site_name'])}</a>
<nav class="nav menu" id="site-menu" aria-label="Main">{nav_links(root, path, fi)}</nav>{MENU_BTN}
</div></header>{header_ad(cfg, ads)}{MENU_JS}
<main class="wrap" id="main">
{body.replace('{root}', root)}
</main>
{site_footer(cfg, root, fi)}
</body></html>
"""


IMG_MAX_BYTES = 200_000


def pet_img(it, max_w, aspect=None, budget=IMG_MAX_BYTES):
    """Optimize one configured photo (path under static/img/, or {"src","alt","crop"}) to a
    metadata-free WebP in site/img/. crop = [x0,y0,x1,y1] fractions of the (EXIF-rotated) image;
    aspect = w/h centre-trim. Returns (url, w, h, alt) or None."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        print("  WARNING: Pillow not installed; photos skipped (pip install Pillow)")
        return None
    src, alt, crop = (it, "", None) if isinstance(it, str) else (it.get("src", ""), it.get("alt", ""), it.get("crop"))
    rel = src.split("static/", 1)[-1]
    rel = rel if rel.startswith("img/") else "img/" + rel
    path = ROOT / "static" / rel
    if not path.exists():
        print(f"  WARNING: image not found: {path}")
        return None
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if crop:
        W, H = im.size
        im = im.crop((round(crop[0] * W), round(crop[1] * H), round(crop[2] * W), round(crop[3] * H)))
    if aspect:
        W, H = im.size
        if W / H > aspect:
            nw = round(H * aspect); im = im.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
        else:
            nh = round(W / aspect); im = im.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    clean = Image.new("RGB", im.size)  # fresh pixels only: no EXIF/GPS, XMP or ICC carried over
    clean.paste(im)
    (OUT / "img").mkdir(exist_ok=True)
    dest = OUT / "img" / f"{Path(rel).stem}-{max_w}.webp"
    q = 80
    while True:
        clean.save(dest, "WEBP", quality=q, method=6)
        if dest.stat().st_size <= budget or q <= 40:
            break
        q -= 8
    while dest.stat().st_size > budget and clean.width > 480:
        clean = clean.resize((int(clean.width * .85), int(clean.height * .85)), Image.LANCZOS)
        clean.save(dest, "WEBP", quality=q, method=6)
    return (f"img/{dest.name}", clean.width, clean.height, alt)


def img_tag(t, root="", cls="", eager=False):
    u, w, h, alt = t
    return (f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="{root}{e(u)}" width="{w}" height="{h}" alt="{e(alt)}" decoding="async" '
            + ('fetchpriority="high"' if eager else 'loading="lazy"') + ">")


def hero_images(cfg):
    """config.json "hero_images": first = arched frame (3:4), next two = round medallions. [] -> botanical."""
    out = []
    for i, it in enumerate((cfg.get("hero_images") or [])[:3]):
        r = pet_img(it, 720, 3 / 4, 120_000) if i == 0 else pet_img(it, 400, 1, 50_000)
        if r:
            out.append(r)
    return out


def family_strip(cfg):
    """Optional home-page strip from config.json "pet_gallery": {title, text, banner, images[]}."""
    g = cfg.get("pet_gallery") or {}
    imgs = [r for r in (pet_img(it, 600, 3 / 4, 80_000) for it in (g.get("images") or [])[:4]) if r]
    ban = pet_img(g["banner"], 1600, None, 160_000) if g.get("banner") else None
    if not imgs and not ban:
        return ""
    figs = "".join(f'<li>{img_tag(t)}</li>' for t in imgs)
    return (f'<section class="family" aria-labelledby="fam-h"><h2 id="fam-h">{e(g.get("title", ""))}</h2>'
            + (f'<p>{e(g["text"])}</p>' if g.get("text") else "")
            + (f'<div class="pano">{img_tag(ban)}</div>' if ban else "")
            + (f'<ul class="gallery">{figs}</ul>' if figs else "") + "</section>")


def side_photo(cfg, key, root):
    it = cfg.get(key)
    t = pet_img(it, 600, 3 / 4, 80_000) if it else None
    return f'<figure class="side-arch">{img_tag(t, root, eager=True)}</figure>' if t else ""


# Art Nouveau botanical fill for the hero arch when no photos are configured (decorative).
BOTANICAL = ('<svg class="botan" viewBox="0 0 300 400" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">'
    '<defs><linearGradient id="hg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a6066"/><stop offset="1" stop-color="#143a3e"/></linearGradient></defs>'
    '<rect width="300" height="400" fill="url(#hg)"/>'
    '<circle cx="150" cy="150" r="104" fill="#d9b765" fill-opacity=".09"/>'
    '<circle cx="150" cy="150" r="104" fill="none" stroke="#d9b765" stroke-opacity=".6"/>'
    '<circle cx="150" cy="150" r="92" fill="none" stroke="#d9b765" stroke-opacity=".35" stroke-dasharray="2 5"/>'
    '<g fill="#7d8c64"><path d="M150 400C122 342 96 304 62 262c46 30 76 72 88 138z"/><path d="M150 400c26-62 58-98 96-130-32 40-58 76-96 130z" fill="#66754f"/>'
    '<path d="M96 400c-10-50-30-80-64-104 40 12 62 50 64 104z" fill="#5d6c48"/><path d="M206 400c8-46 30-78 66-98-34 26-50 58-66 98z" fill="#5d6c48"/></g>'
    '<g fill="none" stroke="#a9b98a" stroke-width="2.6" stroke-linecap="round">'
    '<path d="M150 400c0-70-28-98-14-158s22-74 14-98"/><path d="M92 400c4-58-30-86-12-138 10-28 26-44 14-64"/><path d="M212 400c-4-54 32-86 12-132-10-26-28-38-16-62"/></g>'
    '<g fill="none" stroke="#d9b765" stroke-width="1.4" stroke-linecap="round">'
    '<path d="M84 262c-40-6-46-50-14-56 20-3 24 22 6 24-9 1-10-10-3-11"/><path d="M220 268c40-8 42-52 10-55-20-2-22 22-4 23 9 0 9-10 2-11"/>'
    '<path d="M140 300c-30-16-56-6-58 14"/><path d="M160 318c30-14 52-2 52 16"/></g>'
    '<g fill="#efe3c2"><path d="M150 146c-16-24-14-50 0-66 14 16 16 42 0 66z"/><path d="M150 146c-24-8-44 4-50 26 20 0 38-8 50-26z"/>'
    '<path d="M150 146c24-8 44 4 50 26-20 0-38-8-50-26z"/><path d="M150 146c-10 12-12 28-4 40 6-12 8-26 4-40z" fill="#d9b765"/>'
    '<ellipse cx="94" cy="190" rx="7" ry="15" transform="rotate(-14 94 190)"/><ellipse cx="208" cy="200" rx="7" ry="15" transform="rotate(16 208 200)"/></g>'
    '<path d="M150 146c-6 6-8 14-6 22M150 146c6 6 8 14 6 22" stroke="#b38a35" fill="none"/></svg>')


def hero_media(imgs):
    """Mucha-style arched frame with a halo; holds 1-3 pet photos or the botanical fill."""
    if imgs:
        inner = img_tag(imgs[0], cls="main", eager=True)
        extra = "".join(img_tag(t, cls=f"medal m{i}") for i, t in enumerate(imgs[1:], 1))
    else:
        inner, extra = BOTANICAL, ""
    return f'<div class="hero-media n{len(imgs)}"><span class="halo" aria-hidden="true"></span><div class="arch">{inner}</div>{extra}</div>'


def build_index(cfg, airlines):
    rows = []
    for a in airlines:
        rows.append(f"""<tr>
<td data-l="Airline"><a href="airlines/{a['slug']}.html">{e(a['name'])}</a></td>
<td data-l="In cabin">{yn_badge(a.get('in_cabin_allowed'))}</td>
<td data-l="Max carrier">{val(a,'max_carrier_dimensions')}</td>
<td data-l="Max weight">{val(a,'max_combined_weight')}</td>
<td data-l="Fee (from)">{e(short_fee(a)) if a.get('fees') else val(a,'fees')}</td>
<td data-l="Hold / cargo">{val(a,'checked_or_cargo')}</td>
<td data-l="Verified">{f'<time datetime="{e(a["last_verified"])}">{e(nice_date(a["last_verified"]))}</time>' if a.get('last_verified') else 'Not verified'}{' <span class="flag">official page blocked</span>' if a.get('fetch_status')=='blocked' else ''}</td>
</tr>""")
    newest = max(a["last_verified"] for a in airlines if a.get("last_verified"))
    imgs = hero_images(cfg)
    body = f"""
<section class="hero{' hero-photo' if imgs else ''}">
<div class="hero-text">
<h1>Flying with a dog or cat? Airline pet policies, verified.</h1>
<p class="lead">{e(cfg.get('site_tagline',''))} Every airline page shows the date we last checked the <b>official</b> policy page and links to it. If we couldn't confirm a detail, we say so instead of guessing.</p>
<p class="small meta"><span class="dot" aria-hidden="true"></span>Most recent check: <time datetime="{newest}">{nice_date(newest)}</time> &middot; {len(airlines)} airlines</p>
<nav class="chips" aria-label="Airlines">{''.join(f'<a href="airlines/{a["slug"]}.html">{e(a["name"])}</a>' for a in airlines)}</nav>
</div>
{hero_media(imgs)}
</section>
<div class="tools" hidden><label for="q">Filter airlines</label><input id="q" type="search" autocomplete="off" placeholder="e.g. Delta, Air France"></div>
<div class="tablewrap"><table class="cmp" id="cmp">
<thead><tr><th>Airline</th><th>In cabin</th><th>Max carrier</th><th>Max weight</th><th>Fee (from)</th><th>Hold / cargo</th><th>Last verified</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="small">"{CHECK}" means the detail was not stated on, or could not be read from, the airline's official page on the date shown.</p>
{family_strip(cfg)}
{affiliate_box(cfg)}
<script>(function(){{var t=document.querySelector('.tools'),q=document.getElementById('q');if(!t||!q)return;t.hidden=false;var r=document.querySelectorAll('#cmp tbody tr');q.addEventListener('input',function(){{var v=q.value.trim().toLowerCase();r.forEach(function(x){{x.hidden=v&&x.cells[0].textContent.toLowerCase().indexOf(v)<0}})}})}})();</script>
"""
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": cfg["site_name"], "url": site_base(cfg)},
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": f"{a['name']} pet policy",
               "url": f"{site_base(cfg)}/airlines/{a['slug']}.html"} for i, a in enumerate(airlines)]}]
    return page(cfg, f"Airline pet policies compared (in-cabin dogs & cats): verified {nice_date(newest)}",
                "Compare in-cabin pet rules, carrier sizes, weight limits and fees for major airlines, each checked against the official airline page with a last-verified date.",
                body, "index.html", "", ld, canonical=site_base(cfg) + "/")


def faq(a):
    n = a["name"]
    q = [
        (f"Can I bring my pet in the cabin on {n}?", plain(a, "in_cabin_allowed") + (f". Species: {plain(a,'species')}" if a.get("species") else "")),
        (f"What size pet carrier does {n} allow?", plain(a, "max_carrier_dimensions")),
        (f"Is there a weight limit for pets on {n}?", plain(a, "max_combined_weight")),
        (f"How much does it cost to fly with a pet on {n}?", plain(a, "fees")),
        (f"Can my pet fly as checked baggage or cargo on {n}?", plain(a, "checked_or_cargo")),
    ]
    note = f" (Last verified {nice_date(a.get('last_verified'))} against {a['official_url']}; confirm with the airline.)"
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": qq, "acceptedAnswer": {"@type": "Answer", "text": aa + note}} for qq, aa in q]}


def sources_block(a):
    """Optional per-airline source list + related internal pages (only rendered when the data has them)."""
    src = a.get("sources") or []
    rel = a.get("related") or []
    if not src and not rel:
        return ""
    li = "".join(f"<li><a href='{e(x['url'])}' rel='noopener' target='_blank'>{e(x['label'])}</a></li>" for x in src)
    li += "".join(f"<li><a href='{{root}}{e(x['path'])}'>{e(x['label'])}</a></li>" for x in rel)
    return f"<h2>Official sources</h2><ul class='changes'>{li}</ul>"


def build_airline(cfg, a, pd=None, lims=None):
    d = nice_date(a.get("last_verified"))
    rows = "".join(f"<tr><th scope='row'>{e(lbl)}</th><td>{val(a,k)}</td></tr>" for k, lbl in FIELDS)
    changes = a.get("recent_changes") or []
    ch = "".join(
        f"<li><time>{e(nice_date(c.get('date')))}</time> &ndash; {e(c['summary'])} "
        f"<a href='{e(c['source_url'])}' rel='noopener' target='_blank'>source</a>"
        f"{'' if c.get('official') else ' <span class=flag>unofficial source</span>'}</li>" for c in changes)
    status = {"ok": "", "partial": "<p class='warn'>Part of the official page could not be read by our checker; some details come from other official airline sources noted below.</p>",
              "blocked": "<p class='warn'>The airline's official page blocked our checker on the date shown, so no details could be confirmed. Please check the official page directly.</p>"}.get(a.get("fetch_status"), "")
    review = "<p class='warn'>The official page changed at our last check and is awaiting human review. Details below may be out of date.</p>" if a.get("needs_review") else ""
    if a.get("last_verified"):
        verified_line = f"""<p class="verified">&#10003; Last verified <time datetime="{e(a['last_verified'])}">{d}</time> against the <a href="{e(a['official_url'])}" rel="noopener" target="_blank">official {e(a['name'])} pet policy page</a>.</p>"""
        title = f"{a['name']} pet policy (in-cabin dogs & cats): verified {d}"
    else:
        verified_line = f"""<p class="warn">Not yet verified. Last check attempt: {e(nice_date(a.get('last_checked')))}. Official page: <a href="{e(a['official_url'])}" rel="noopener" target="_blank">{e(a['name'])} pet policy</a>.</p>"""
        title = f"{a['name']} pet policy (in-cabin dogs & cats): official page checked {nice_date(a.get('last_checked'))}"
    body = f"""
<nav class="crumbs"><a href="{{root}}index.html">All airlines</a> &rsaquo; {e(a['name'])}</nav>
{ad_slot(cfg, 'airline_top', '{root}')}
<h1>{e(a['name'])} pet policy</h1>
{verified_line}
{status}{review}
<table class="facts"><tbody>{rows}</tbody></table>
{airline_carriers_block(a, pd, lims) if pd else ''}
{airline_gear_box(cfg, a, pd, lims) if pd else ''}
{flight_box(cfg, a)}
{f"<h2>Good to know</h2><p>{e(a['notes'])}</p>" if a.get('notes') else ''}{sources_block(a)}
<h2>Recent changes</h2>
{f"<ul class='changes'>{ch}</ul>" if ch else "<p>No dated changes recorded yet. We log changes here when we detect them.</p>"}
<p class="small">Before you book, re-check the <a href="{e(a['official_url'])}" rel="noopener" target="_blank">official page</a> and call the airline to reserve pet space; space is usually limited per flight.</p>
{forum_pages.airline_link(cfg, a)}
{affiliate_box(cfg)}
"""
    desc = f"{a['name']} pet policy: in-cabin {plain(a,'in_cabin_allowed').lower()}, carrier size, weight limit and fees. {'Verified ' + d if a.get('last_verified') else 'Not yet verified'} against the official airline page."
    return page(cfg, title, desc[:300], body, f"airlines/{a['slug']}.html", "../", [faq(a)] if confirmed_count(a) else [])


def build_updates(cfg, airlines, updates):
    items = []
    for a in airlines:
        for c in a.get("recent_changes") or []:
            items.append({"date": c.get("date"), "airline": a["name"], "slug": a["slug"], **c})
    for u in updates:
        items.append(u)
    items.sort(key=lambda x: x.get("date") or "0000", reverse=True)
    li = "".join(
        f"<li><time>{e(nice_date(i.get('date')))}</time> <a href='airlines/{e(i['slug'])}.html'>{e(i['airline'])}</a>: {e(i['summary'])} "
        f"<a href='{e(i.get('source_url',''))}' rel='noopener' target='_blank'>source</a>"
        f"{'' if i.get('official', True) else ' <span class=flag>unofficial source</span>'}</li>" for i in items)
    body = f"""<h1>Pet policy updates</h1>
<p>Changes we've found on airline pet policy pages, newest first. Changes our nightly checker detects are logged here once reviewed.</p>
<ul class="changes">{li or '<li>No updates yet.</li>'}</ul>"""
    return page(cfg, f"Airline pet policy updates and changes | {cfg['site_name']}",
                "A dated log of airline pet policy changes, each with a link to the source.", body, "updates.html", "")


def build_about(cfg):
    body = f"""<h1>About &amp; disclaimer</h1>
<h2>Why this site exists</h2>
<p>Airline pet policies change often, sometimes without notice, and many pages online are outdated or contradict each other. We check each airline's <b>official</b> pet policy page, record the date we checked, and link to it. If a detail isn't on the official page, or we couldn't read the page, we show "{CHECK}" rather than guessing.</p>
<h2>Disclaimer</h2>
<p>Information may change at any time and may contain errors. It is provided for general guidance only and is not legal, veterinary or travel advice. <b>Always confirm with the airline before booking or travelling</b>, and check the government entry rules (e.g. CDC, USDA APHIS, CFIA, DEFRA) for every country on your route. We are not affiliated with any airline.</p>
<h2 id="affiliates">Affiliate disclosure</h2>
<p>Some pages may contain affiliate links (for example to pet carriers, pet insurance or hotel booking sites such as Expedia). If you buy through them we may earn a commission at no extra cost to you. Affiliate relationships never change the policy information we publish.</p>
<p>{AMAZON_DISCLOSURE} Product pages may link to Amazon.com through the Amazon Associates Program.</p>
<h2 id="advertising">Advertising</h2>
<p>The site shows ads served by Google AdSense and may load affiliate scripts such as Travelpayouts. Advertisers never change the policy information we publish. See our <a href="privacy.html">privacy policy</a> for how advertising cookies work and how to opt out of personalized ads.</p>
<h2>Corrections</h2>
<p>Spotted something out of date? Please tell us via our <a href="contact.html">contact page</a>.</p>"""
    return page(cfg, f"About & disclaimer | {cfg['site_name']}", "How we verify airline pet policies, our disclaimer and affiliate disclosure.", body, "about.html", "")


def obf_mail(addr):
    """Mailto link with every character as an HTML entity: clickable, no JS, hidden from naive scrapers."""
    ent = lambda t: "".join(f"&#{ord(ch)};" for ch in t)
    return f'<a href="{ent("mailto:" + addr)}">{ent(addr)}</a>'


EFFECTIVE = "October 22, 2026"
PRIVACY_UPDATED = "October 22, 2026"


NO_ACCOUNTS = """<h2>No accounts, no forms</h2>
<p>There are no user accounts, logins, comment forms or newsletters on this site. We don't ask for, and don't store, your name, email or any other personal information. If you email us, we only use your message and address to reply.</p>"""


def forum_privacy(cfg):
    fm = obf_mail((cfg.get("forum") or {}).get("contact_email") or cfg["contact_email"])
    return f"""<h2 id="forum">Forum accounts</h2>
<p>Reading the <a href="forum/">forum</a> needs no account. If you create one to post or comment, we store: your <b>email address</b> (to sign you in and for account emails such as confirmation and password reset; never shown publicly), your <b>display name</b> (public, shown next to your posts), a hashed password (if you don't use Google sign-in), and what you post: <b>posts, comments, reports</b>, their categories and dates, and the moderation status and reason. If you choose "Continue with Google", Google shares your email address and basic profile with us for sign-in; we don't use your Google name or photo publicly.</p>
<p><b>Processor:</b> accounts and forum content are stored by <a href="https://supabase.com/privacy" rel="noopener" target="_blank">Supabase</a> (our database and sign-in provider), which processes the data on our behalf; our project is hosted in Supabase's Northeast Asia (Seoul) region. Supabase may log technical data such as IP addresses for security. Sign-in keeps a session token in your browser's local storage (not an advertising cookie); signing out removes it.</p>
<p><b>Moderation:</b> posts and comments are checked before publication by an automatic keyword filter and by a moderator (assisted by an AI tool that reads only the text you submitted). Published posts and comments, with your display name, are public and may be included in search engines.</p>
<p><b>Your choices:</b> you can delete your own posts and comments at any time from <a href="forum/account.html">My account</a>, and change your display name. To delete your account and all its data, or to get a copy of it, email {fm}; we handle requests within 30 days. Your data is kept while your account exists.</p>
<p>Forum pages for signing in and posting don't show ads or load affiliate scripts.</p>
<h3 id="forum-officer">Privacy officer, retention and your rights</h3>
<ul><li><b>Privacy officer:</b> the site owner (operator of {e(cfg['site_name'])}), contact {fm}.</li>
<li><b>Data collected for the forum:</b> email address, display name, password hash (email sign-up only), posts, comments, reports, and their dates and moderation status.</li>
<li><b>Purpose:</b> sign-in, publishing and moderating forum content, account emails.</li>
<li><b>Retention:</b> account data is kept until you ask us to delete it (or delete it yourself); posts and comments you delete, and accounts we delete on request, are removed from the database and from our published pages within 30 days.</li>
<li><b>Processor and storage:</b> Supabase, Inc. (database and authentication) stores the data in its Northeast Asia (Seoul, Republic of Korea) region.</li>
<li><b>Your rights:</b> you can ask to access, correct, delete or stop the processing of your personal data by emailing the privacy officer; we reply within 30 days.</li></ul>
<section lang="ko" id="forum-ko"><h3>포럼 개인정보 처리 안내 (한국어)</h3>
<ul><li><b>개인정보 보호책임자:</b> 사이트 운영자 ({e(cfg['site_name'])} 운영자), 연락처 {fm}</li>
<li><b>수집 항목:</b> 이메일 주소, 닉네임, 비밀번호 해시 (이메일 가입 시), 작성한 글·댓글·신고 내용과 작성일, 검토 상태</li>
<li><b>수집 목적:</b> 로그인, 포럼 글 게시 및 검토, 계정 관련 이메일 발송</li>
<li><b>보유 기간:</b> 계정 정보는 삭제를 요청하실 때까지 (또는 직접 삭제하실 때까지) 보관합니다. 직접 삭제한 글과 댓글, 요청에 따라 삭제한 계정의 정보는 30일 이내에 데이터베이스와 게시된 페이지에서 삭제됩니다.</li>
<li><b>처리 위탁 및 보관 위치:</b> Supabase, Inc. (데이터베이스 및 인증), 노스이스트 아시아 (대한민국 서울) 리전에 저장</li>
<li><b>정보주체의 권리:</b> 개인정보 열람, 정정, 삭제, 처리 정지를 개인정보 보호책임자에게 이메일로 요청할 수 있으며, 30일 이내에 답변드립니다.</li></ul></section>"""


def build_privacy(cfg):
    mail = obf_mail(cfg.get("privacy_email") or cfg["contact_email"])
    body = f"""<h1>Privacy policy</h1>
<p class="small">Effective date: {EFFECTIVE} &middot; Last updated: {PRIVACY_UPDATED}</p>
<p>{e(cfg['site_name'])} is a simple static website. This page explains, in plain English, what data is and isn't collected when you visit, including by the advertising and affiliate services we use.</p>
{forum_privacy(cfg) if forum_pages.enabled(cfg) else NO_ACCOUNTS}
<h2>Hosting (GitHub Pages)</h2>
<p>The site is hosted on GitHub Pages, a service of GitHub, Inc. When you load a page, GitHub's servers may log technical information such as your IP address, browser type and the page requested, for security and operations. We don't receive or control those logs. See the <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener" target="_blank">GitHub Privacy Statement</a>.</p>
<h2>Cookies</h2>
<p>Our own code sets no cookies. The third-party advertising and affiliate services described below may set and read cookies, or use similar technologies such as web beacons and device identifiers, when you visit our pages or click a link. You can block or delete cookies in your browser settings.</p>
<h2>Advertising (Google AdSense)</h2>
<p>We use Google AdSense to show ads on this site. Third-party vendors, including Google, use cookies to serve ads based on a user's prior visits to this website or other websites. Google's use of advertising cookies enables it and its partners to serve ads to our users based on their visit to our site and/or other sites on the Internet.</p>
<p>You may opt out of personalized advertising by visiting <a href="https://adssettings.google.com" rel="noopener" target="_blank">Google Ads Settings</a>. You can also opt out of some third-party vendors' use of cookies for personalized advertising by visiting <a href="https://www.aboutads.info" rel="noopener" target="_blank">www.aboutads.info</a>. If you opt out, you may still see ads, but they won't be personalized.</p>
<p>To learn more, see <a href="https://policies.google.com/technologies/partner-sites" rel="noopener" target="_blank">How Google uses information from sites or apps that use our services</a>.</p>
<h2>Travelpayouts</h2>
<p>Our pages load a script from Travelpayouts, an affiliate network for travel brands. It may turn links to travel partners (such as airlines, hotels or booking sites) into affiliate links, and Travelpayouts or its partners may use cookies or similar technology to record that a visit or booking came from our site, so we can be paid a commission. This is governed by the <a href="https://support.travelpayouts.com/hc/en-us/articles/360004121052-Privacy-Policy" rel="noopener" target="_blank">Travelpayouts privacy policy</a>.</p>
<h2>Affiliate links and partner cookies</h2>
<p>Some pages include affiliate links to partners, for example brands on the Impact network (such as Chewy, Trupanion or Lemonade), Amazon.com, Booking.com and Travelpayouts partners. If you buy through one, we may earn a commission at no extra cost to you. When you click an affiliate link, you leave our site and the partner (or its affiliate network) may set cookies or use similar technology to record that the visit came from us. Those cookies are governed by the partner's own privacy policy, not ours. We don't receive personal information about you from these partners, only aggregated sales or commission reports. Affiliate relationships never change the policy information we publish.</p>
<p>{AMAZON_DISCLOSURE} {e(cfg['site_name'])} participates in the Amazon Services LLC Associates Program; Amazon may use cookies to record that a visit or purchase came from our links, under Amazon's own privacy notice.</p>
<h2>Analytics</h2>
<p>We don't run a separate analytics tool (such as Google Analytics) on this site. If we add one, this page will be updated first to name it, what it collects and how to opt out.</p>
<h2>External links</h2>
<p>We link to airline and government websites. Their privacy practices are their own.</p>
<h2>Children</h2>
<p>This site is not directed at children under 13, and we do not knowingly collect personal information from children.</p>
<h2>Changes</h2>
<p>If this policy changes, we'll update this page and its "last updated" date.</p>
<h2>Contact</h2>
<p>Questions about privacy: {mail}.</p>"""
    return page(cfg, f"Privacy policy | {cfg['site_name']}", "Privacy policy for PetPolicyCheck: Google AdSense advertising cookies and how to opt out, Travelpayouts and affiliate links, and GitHub Pages hosting explained.", body, "privacy.html", "")


def build_contact(cfg):
    mail = obf_mail(cfg["contact_email"])
    body = f"""<h1>Contact</h1>
<p>Email: <b>{mail}</b></p>
<h2>Corrections to airline data</h2>
<p>Found a pet policy detail that's out of date or wrong? Please email us with the airline, what's wrong, and a link to the airline's official page showing the current rule. We check every correction against the official source before updating, and the page's "last verified" date changes when we do.</p>
<h2>Partnerships &amp; sponsorship</h2>
<p>Pet travel brands, insurers and travel companies interested in partnerships or sponsorship are welcome to get in touch. Sponsorship never changes the airline policy data we publish (see our <a href="about.html#affiliates">disclosure</a>).</p>
<p class="small">We can't book flights or answer questions about a specific reservation: please contact your airline for that.</p>"""
    return page(cfg, f"Contact | {cfg['site_name']}", "Contact PetPolicyCheck for corrections to airline pet policy data, partnerships or sponsorship.", body, "contact.html", "")


# ---------------------------------------------------------------- products & ads
CATS = {"soft_carrier": "Soft & under-seat carriers", "backpack": "Carrier backpacks",
        "hard_crate": "Hard crates for the hold / cargo", "bowl": "Travel bowls & water bottles",
        "harness": "Harnesses & leashes (including car harnesses)", "car": "Car seat belts, seat covers & boosters",
        "bed": "Travel beds & mats", "clothing": "Coats, cooling vests, boots & life jackets",
        "calming": "Calming aids", "potty": "Travel litter boxes & pee pads",
        "id_gps": "ID & GPS trackers", "travel_gear": "Other travel accessories"}
# Travel accessories: spec tables only (no airline size comparison); pages say "specs" rather than "dimensions".
GEAR = {"harness", "car", "bed", "clothing", "calming", "potty", "id_gps", "travel_gear"}
GEAR_REL = {"harness": ["dog-road-trip-packing-list"], "car": ["dog-road-trip-packing-list"],
            "bed": ["dog-road-trip-packing-list"], "clothing": ["dog-road-trip-packing-list"],
            "calming": ["dog-road-trip-packing-list", "cat-travel-checklist"], "potty": ["cat-travel-checklist", "dog-road-trip-packing-list"],
            "id_gps": ["dog-road-trip-packing-list", "cat-travel-checklist"], "travel_gear": ["cat-travel-checklist", "dog-road-trip-packing-list"]}


def pets_txt(p):
    ps = p.get("pets") or []
    return " &amp; ".join({"dog": "Dogs", "cat": "Cats"}[x] for x in ps)
EPS = 0.05


def load_products(airlines):
    pd = json.loads((ROOT / "data" / "products.json").read_text())
    by = {a["slug"]: a for a in airlines}
    lims = []
    for l in json.loads((ROOT / "data" / "cabin_limits.json").read_text())["limits"]:
        a = by.get(l["airline"])
        if not a or l["quote"] not in (a.get("max_carrier_dimensions") or ""):
            print(f"  WARNING: cabin limit dropped (airline data changed?): {l['airline']} / {l['label']}")
            continue
        lims.append({**l, "a": a})
    return pd, lims


def ad_slot(cfg, key, root, i18n=False):
    s = (cfg.get("ads") or {}).get(key) or {}
    if s.get("image_url") and s.get("link_url"):
        adv = f'<span class="small"> &middot; {e(s.get("advertiser"))}</span>' if s.get("advertiser") else ""
        return (f'<aside class="ad ad-{e(key)}"><span class="adlabel">Sponsored</span>{adv}'
                f'<a href="{e(s["link_url"])}" rel="sponsored nofollow noopener" target="_blank">'
                f'<img src="{e(s["image_url"])}" alt="{e(s.get("alt") or s.get("advertiser") or "Sponsor")}" loading="lazy"></a></aside>')
    return f'<p class="adph"><a href="{root}advertise/"{ti("site.adhere", i18n)}>Advertise here</a></p>'


def dims(s, unit=None):
    u = s.get("unit", "in")
    L = f'{s["L_min"]:g}&ndash;{s["L"]:g}' if s.get("L_min") else f'{s["L"]:g}'
    t = f'{L} &times; {s["W"]:g} &times; {s["H"]:g} {u}'
    if u == "in":
        cm = lambda v: f"{v * 2.54:.0f}"
        Lc = f'{cm(s["L_min"])}&ndash;{cm(s["L"])}' if s.get("L_min") else cm(s["L"])
        t += f' <span class="small">({Lc} &times; {cm(s["W"])} &times; {cm(s["H"])} cm)</span>'
    return t


def fit(size, lim):
    f = 2.54 if lim["unit"] == "cm" and size.get("unit", "in") == "in" else 1
    W, H = size["W"] * f, size["H"] * f
    big, small = max(lim["L"], lim["W"]), min(lim["L"], lim["W"])

    def over(L):
        a, b = max(L, W), min(L, W)
        r = []
        if H > lim["H"] + EPS: r.append(("taller", H - lim["H"]))
        if a > big + EPS: r.append(("longer", a - big))
        if b > small + EPS: r.append(("wider", b - small))
        return r
    full = over(size["L"] * f)
    if not full:
        return "ok", []
    if size.get("L_min"):
        short = over(size["L_min"] * f)
        return ("compressed", []) if not short else ("over", short)
    return "over", full


def fit_cell(size, lim, short=False):
    st, why = fit(size, lim)
    if st == "ok":
        return '<span class="fit-ok">&#10003; Within</span>'
    if st == "compressed":
        return f'<span class="fit-mid">&#10003; Within at {size["L_min"]:g} in length</span>'
    u = lim["unit"]
    return '<span class="fit-no">&#10007; Over</span>' + ("" if short else
        '<br><span class="small">' + ", ".join(f"{k} by {v:.1f} {u}" for k, v in why) + "</span>")


def lim_txt(l):
    return f'{l["L"]:g} &times; {l["W"]:g} &times; {l["H"]:g} {l["unit"]}'


def applicable(p, lims):
    return [l for l in lims if not l.get("hard_only")] if p["category"] in ("soft_carrier", "backpack") else []


def soft_note(p, l):
    if l.get("soft_only") and not p.get("construction"):
        return ' <span class="flag">soft-sided only*</span>'
    return ""


def fit_matrix(p, lims, root):
    ls = applicable(p, lims)
    if not ls:
        return ""
    sz = p["sizes"]
    head = "".join(f"<th>{e(s['name'])}</th>" for s in sz) if len(sz) > 1 else "<th>Fits?</th>"
    rows = "".join(
        f"<tr><td data-l='Airline'><a href='{root}airlines/{l['a']['slug']}.html'>{e(l['a']['name'])}</a>"
        f"<br><span class='small'>{e(l['label'])}</span></td><td data-l='Airline limit'>{lim_txt(l)}{soft_note(p, l)}</td>"
        + "".join(f"<td data-l='{e(s['name'])}'>{fit_cell(s, l)}</td>" for s in sz) + "</tr>" for l in ls)
    return f"""<h2 id="fit">Fits under-seat on which airlines?</h2>
<p class="small">Manufacturer dimensions compared with the cabin carrier limit on each of our airline pages. Length and width may be swapped (the carrier can be turned); height may not. Soft carriers may squash a little, but we only compare published numbers. The gate agent has the final say.</p>
<div class="tablewrap"><table class="cmp fitm"><thead><tr><th>Airline</th><th>Airline limit</th>{head}</tr></thead><tbody>{rows}</tbody></table></div>
{"<p class='small'>* This airline accepts soft-sided carriers only, and " + e(p['brand']) + " doesn&rsquo;t state this product&rsquo;s construction on its page; check before you fly.</p>" if any(l.get("soft_only") for l in ls) and not p.get("construction") else ""}
{"<p class='small'>Over results for an adjustable-length carrier are shown at its shortest length.</p>" if any(s.get("L_min") for s in sz) else ""}
{no_limit_note(lims, root)}"""


def no_limit_note(lims, root):
    return ("<p class='small'>Not compared: airlines with no confirmed cabin carrier size on our pages "
            f"(see <a href='{root}products/under-seat-carrier-size-by-airline.html'>carrier size by airline</a>).</p>")


AMAZON_DISCLOSURE = "As an Amazon Associate I earn from qualifying purchases."


def amazon_tagged(cfg, url):
    """Add or replace the Amazon Associates tag (config `amazon_tag`) on an amazon.com URL; other params kept."""
    tag = cfg.get("amazon_tag")
    if not url or not tag:
        return url
    u = urllib.parse.urlsplit(url)
    host = (u.hostname or "").lower()
    if not (host == "amazon.com" or host.endswith(".amazon.com")):
        return url
    q = [(k, v) for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True) if k != "tag"] + [("tag", tag)]
    return urllib.parse.urlunsplit((u.scheme, u.netloc, u.path, urllib.parse.urlencode(q), u.fragment))


def buy_links(cfg, p):
    slot = (cfg.get("product_links") or {}).get(p["slug"]) or {}
    out = []
    if slot.get("amazon_url"):
        out.append(f'<a class="btn" href="{e(amazon_tagged(cfg, slot["amazon_url"]))}" rel="sponsored nofollow noopener" target="_blank">View at Amazon</a>')
    if slot.get("chewy_url"):
        out.append(f'<a class="btn" href="{e(slot["chewy_url"])}" rel="sponsored nofollow noopener" target="_blank">View at Chewy</a>')
    if not out:
        out.append(f'<a class="btn" href="{e(p["official_url"])}" rel="noopener" target="_blank">View on the official {e(p["brand"])} site</a>')
    return '<p class="buy">' + " ".join(out) + "</p>"


def disclosure(root):
    return (f'<p class="disc small">Affiliate disclosure: some links on this page may be affiliate links; if you buy through them we may earn a commission at no extra cost to you. '
            f'It never changes the dimensions or fit results shown. We have not tested these products ourselves: every figure comes from the linked manufacturer page. '
            f'{AMAZON_DISCLOSURE} <a href="{root}about.html#affiliates">Disclosure</a>.</p>')


def verified_p(p, v, root):
    return (f'<p class="verified">&#10003; {"Specs" if p["category"] in GEAR else "Dimensions"} checked <time datetime="{v}">{nice_date(v)}</time> against the '
            f'<a href="{e(p["official_url"])}" rel="noopener" target="_blank">official {e(p["brand"])} product page</a>. No prices shown: they change too often.</p>')


def crumbs(root, name=None):
    return f'<nav class="crumbs"><a href="{root}index.html">Home</a> &rsaquo; ' + (
        f'<a href="{root}products/">Products</a> &rsaquo; {e(name)}' if name else "Products") + "</nav>"


def bc_ld(cfg, items):
    base = site_base(cfg)
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": f"{base}/{u}"} for i, (n, u) in enumerate(items)]}


def fits_list(p, lims):
    """(within, over) lists of airline-limit labels for the product's sizes."""
    res = []
    for s in p.get("sizes", []):
        ok = [l for l in applicable(p, lims) if fit(s, l)[0] != "over"]
        res.append((s, ok))
    return res


def hold_table(airlines, root):
    rows = "".join(f"<tr><td data-l='Airline'><a href='{root}airlines/{a['slug']}.html'>{e(a['name'])}</a></td>"
                   f"<td data-l='Hold / cargo'>{val(a, 'checked_or_cargo')}</td><td data-l='Weight'>{val(a, 'max_combined_weight')}</td></tr>" for a in airlines)
    return (f"<div class='tablewrap'><table class='cmp'><thead><tr><th>Airline</th><th>Hold / cargo option</th><th>Weight limit</th></tr></thead>"
            f"<tbody>{rows}</tbody></table></div><p class='small'>From our airline pages; each links to the official airline source and its last-verified date.</p>")


def build_product(cfg, p, pd, lims, airlines):
    root, v = "../", pd["verified"]
    if p.get("sizes"):
        hd = "Interior dimensions (L &times; W &times; H)" if p.get("interior") else "Dimensions (L &times; W &times; H)"
        spec = "".join(f"<tr><th scope='row'>{e(s['name'])}</th><td>{dims(s)}</td><td>{e(s.get('pet', ''))}</td></tr>" for s in p["sizes"])
        spec = f"<table class='facts'><thead><tr><th>Size</th><th>{hd}</th><th>Pet size (per maker)</th></tr></thead><tbody>{spec}</tbody></table>"
    else:
        spec = "<table class='facts'><tbody>" + "".join(f"<tr><th scope='row'>{e(a)}</th><td>{e(b)}</td></tr>" for a, b in p["spec_rows"]) + "</tbody></table>"
    says = "".join(f"<li>{e(x)}</li>" for x in p.get("maker_says", []))
    extra, faqs = "", []
    if p["category"] in ("soft_carrier", "backpack"):
        extra = fit_matrix(p, lims, root)
        for a in sorted({l["a"]["slug"]: l["a"] for l in applicable(p, lims)}.values(), key=lambda a: a["name"]):
            al = [l for l in lims if l["a"]["slug"] == a["slug"] and not l.get("hard_only")]
            parts = []
            for s in p["sizes"]:
                ok = [l["label"] for l in al if fit(s, l)[0] != "over"]
                nm = "" if len(p["sizes"]) == 1 else f"{s['name']}: "
                parts.append(nm + (("within the published limit (" + ", ".join(ok) + ")") if ok else "larger than the published limit"))
            faqs.append((f"Does the {p['name']} fit under the seat on {a['name']}?",
                         "Comparing the manufacturer's dimensions with the limit on our " + a["name"] + " page: " + "; ".join(parts) +
                         ". This is a comparison of published numbers, not a test; the airline decides at the gate."))
    elif p["category"] == "hard_crate":
        extra = (f"<h2>Under-seat fit</h2><p>Not applicable: this is a kennel for the hold or cargo, and the maker publishes interior dimensions only, so we don't compare it with cabin limits.</p>"
                 f"<h2>Airlines that take pets in the hold or as cargo</h2>{hold_table(airlines, root)}")
    rel = {"soft_carrier": ["best-airline-approved-soft-carriers", "under-seat-carrier-size-by-airline"],
           "backpack": ["pet-carrier-backpacks-for-flying", "best-airline-approved-soft-carriers"],
           "hard_crate": ["iata-hard-crates-for-cargo"], "bowl": ["travel-water-bowls", "dog-road-trip-packing-list"], **GEAR_REL}[p["category"]]
    gear = p["category"] in GEAR
    if p["slug"] == "petmate-kennel-airline-travel-kit":
        rel = rel + ["iata-hard-crates-for-cargo"]
    rl = "".join(f"<li><a href='{g}.html'>{e(GUIDE_META[g][0])}</a></li>" for g in rel)
    sib = "".join(f"<li><a href='{q['slug']}.html'>{e(q['name'])}</a></li>" for q in pd["products"] if q["category"] == p["category"] and q is not p)
    body = f"""{crumbs("{root}", p['name'])}
<h1>{e(p['name'])}: {'sizes and specs' if gear else 'dimensions'}{' and airline under-seat fit' if p['category'] in ('soft_carrier','backpack') else ''}</h1>
{verified_p(p, v, root)}
{buy_links(cfg, p)}{f'<p>Category: <a href="{{root}}products/#{p["category"]}">{e(CATS[p["category"]])}</a>' + (f' &middot; For: {pets_txt(p)}' if p.get("pets") else '') + '</p>' if gear else ''}
<h2>{'Specs (per maker)' if gear else 'Dimensions'}</h2>
{spec}
<p class="small">{e(p.get('dims_note', ''))}{(' Construction: ' + e(p['construction']) + '.') if p.get('construction') else ''}</p>
{f"<h2>What {e(p['brand'])} says</h2><ul>{says}</ul><p class='small'>Manufacturer claims, not verified by us.</p>" if says else ''}
{extra}
<h2>Related</h2><ul>{rl}{sib}<li><a href="{{root}}products/">All pet travel products</a></li><li><a href="{{root}}index.html">Compare airline pet policies</a></li></ul>
{disclosure("{root}")}
"""
    ld = [bc_ld(cfg, [("Home", ""), ("Products", "products/"), (p["name"], f"products/{p['slug']}.html")])]
    if faqs:
        ld.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]})
    t = f"{p['name']}: {'sizes & specs' if gear else 'dimensions'}" + (" & which airlines it fits under-seat" if faqs else "") + f" | {cfg['site_name']}"
    d = f"{p['name']} dimensions from the official {p['brand']} page" + (", compared with the cabin carrier limits of major airlines." if faqs else ", with links to airline pet rules.")
    if gear:
        d = f"{p['name']}: sizes and specs from the official {p['brand']} page, with what the maker says. For travelling with {pets_txt(p).replace('&amp;', 'and').lower() or 'pets'}."
    return page(cfg, t, d, body, f"products/{p['slug']}.html", root, ld)


GUIDE_META = {
    "best-airline-approved-soft-carriers": ("Best airline-approved soft pet carriers: sizes vs. under-seat limits",
        "Popular soft and under-seat pet carriers, ranked by how many airline cabin carrier limits their published dimensions fit within."),
    "under-seat-carrier-size-by-airline": ("Pet carrier size limits by airline (under-seat) and carriers that fit",
        "Every airline cabin pet carrier limit we've verified, side by side, with the carriers whose official dimensions fit each one."),
    "iata-hard-crates-for-cargo": ("IATA-style hard crates for flying pets in the hold or as cargo",
        "Hard plastic travel kennels for the hold or cargo: interior sizes from the maker, IATA notes, and which airlines carry pets in the hold."),
    "pet-carrier-backpacks-for-flying": ("Pet carrier backpacks for flying: do they fit under the seat?",
        "Do pet backpack carriers fit airline under-seat limits? Official backpack dimensions compared with airline cabin limits."),
    "travel-water-bowls": ("Travel water bowls for dogs and cats: collapsible and nesting options",
        "Travel and collapsible pet bowls for trips and flights, with capacities and sizes from the manufacturers' official pages."),
    "dog-road-trip-packing-list": ("What to pack for a road trip with your dog: a checklist with gear specs",
        "A road trip packing list for dogs: car harnesses and tethers, seat covers, bowls, beds, weather gear, pee pads, calming aids and GPS trackers, with specs from the makers' official pages."),
    "cat-travel-checklist": ("Cat travel checklist: carriers, litter, calming and ID",
        "A checklist for travelling with a cat by car or plane: carriers, travel litter boxes, pads, calming wraps and sprays, GPS trackers and carrier accessories, with specs from official maker pages."),
}

ROADTRIP_LIST = ["Your dog's food for the whole trip, plus a little extra", "Water and a travel bowl", "Leash and a harness with ID tags",
                 "Poop bags", "Any medications, and your vet's phone number", "Vaccination records (some hotels, campgrounds and borders ask for them)",
                 "A recent photo of your dog, in case you get separated", "Bedding or a blanket that smells like home", "Towels and cleanup supplies"]
ROADTRIP_SECS = [
    ("harness", "Restraint: car harness and leash", "Clip a seatbelt tether to a harness rather than a collar. Crash-testing claims differ by maker and size, so read each product page before you rely on one."),
    ("car", "In the car: tethers, booster seats and seat covers", "A tether or booster keeps your dog in one place; a cover protects the seat. Kurgo says its own seatbelt tether is not crash tested."),
    ("bowl", "Water and food on the road", "A collapsible bowl or a bottle with a built-in cup makes rest stops easier."),
    ("bed", "Somewhere to sleep", "A packable bed gives your dog a familiar spot in hotels, at friends' houses or at camp."),
    ("clothing", "Weather gear: coats, cooling vests, boots and life jackets", "Pack for the weather and activities at your destination. Check the maker's size chart: most size by chest girth, boots by paw width."),
    ("potty", "Pee pads", "Handy for long drives, hotel rooms and dogs that are still learning."),
    ("calming", "Calming aids", "If your dog gets anxious in the car, talk to your vet; these are drug-free options the makers recommend for travel."),
    ("id_gps", "ID and GPS trackers", "Update the contact details on your dog's tag and microchip before you leave. GPS trackers need a paid plan and cellular coverage."),
    ("travel_gear", "Other useful extras", ""),
]
CAT_LIST = ["A secure carrier your cat already knows (leave it out at home for a few days before the trip)", "Travel litter box, litter, a scoop and bags",
            "Food, water and a small bowl", "Any medications, and your vet's phone number", "Vaccination and health records (airlines and border authorities may ask for them)",
            "Microchip details and a collar with ID", "A puppy pad or towel to line the carrier", "Something that smells like home"]
CAT_SECS = [
    ("potty", "Travel litter boxes and pads", "A collapsible box can sit in the car footwell or a hotel bathroom."),
    ("calming", "Calming aids", "FELIWAY says to spray the carrier at least 15 minutes before your cat goes in, never with your cat inside."),
    ("id_gps", "ID and GPS trackers", "GPS trackers need a paid plan and cellular coverage. Check the weight range for your cat."),
    ("travel_gear", "Carrier accessories and organizers", "A carrier tether helps during airport security screening, when you may be asked to take your cat out of the carrier."),
]


def gear_table(ps, root=""):
    tr = "".join(f"<tr><td data-l='Product'><a href='{p['slug']}.html'>{e(p['name'])}</a><br><span class='small'>{e(p['brand'])}</span></td>"
                 f"<td data-l='Key specs'>{e(p.get('summary') or '; '.join(f'{a}: {b}' for a, b in p.get('spec_rows', []))[:120])}</td>"
                 f"<td data-l='For'>{pets_txt(p) or '&ndash;'}</td></tr>" for p in ps)
    return (f"<div class='tablewrap'><table class='cmp gear'><colgroup><col class='c-prod'><col><col class='c-for'></colgroup>"
            f"<thead><tr><th>Product</th><th>Key specs (per maker)</th><th>For</th></tr></thead>"
            f"<tbody>{tr}</tbody></table></div>")


def checklist_main(P, items, secs, pet, root):
    out = ("<h2>Quick checklist</h2><ul class='check'>" + "".join(f"<li>{e(x)}</li>" for x in items) + "</ul>") if items else ""
    for cat, h, tip in secs:
        ps = [p for p in P if p["category"] == cat and (cat == "bowl" or pet in (p.get("pets") or []))]
        if not ps:
            continue
        out += f"<h2 id='{cat}'>{e(h)}</h2>" + (f"<p>{e(tip)}</p>" if tip else "") + gear_table(ps, root)
    return out


def build_guide(cfg, g, pd, lims, airlines):
    root, v, slug = "../", pd["verified"], g["slug"]
    title, desc = GUIDE_META[slug]
    P = pd["products"]
    plink = lambda p: f"<a href='{p['slug']}.html'>{e(p['name'])}</a>"
    k = g["kind"]
    if k == "soft":
        rows = []
        for p in [p for p in P if p["category"] == "soft_carrier"]:
            for s, ok in fits_list(p, lims):
                rows.append((len(ok), p, s, ok))
        rows.sort(key=lambda r: (-r[0], r[1]["name"]))
        n = len([l for l in lims if not l.get("hard_only")])
        tr = "".join(f"<tr><td data-l='Carrier'>{plink(p)}{'' if len(p['sizes'])==1 else ' &ndash; ' + e(s['name'])}</td><td data-l='Dimensions'>{dims(s)}</td>"
                     f"<td data-l='Within'>{c} of {n}</td><td data-l='Airlines'>{', '.join(sorted({l['a']['name'] for l in ok})) or '<span class=na>none</span>'}</td></tr>" for c, p, s, ok in rows)
        cards = "".join(f"<h3>{plink(p)}</h3><p>{e(p.get('dims_note',''))} {e(' '.join(p.get('maker_says', [])[:1]))} <a href='{p['slug']}.html#fit'>Full airline fit table</a>.</p>"
                        for p in P if p["category"] == "soft_carrier")
        main = f"""<p>How we rank: by the number of airline cabin carrier limits (out of {n} on our airline pages) that each size fits within on published dimensions alone. It is not a quality rating, and we have not tested these carriers.</p>
<div class="tablewrap"><table class="cmp"><thead><tr><th>Carrier &amp; size</th><th>Dimensions (L &times; W &times; H)</th><th>Limits fitted</th><th>Airlines</th></tr></thead><tbody>{''.join(tr)}</tbody></table></div>
<p class="small">"Within" includes carriers that only fit at their shortest adjustable length (Sleepypod Air). Soft-sided only on our pages: {", ".join(sorted({l["a"]["name"] for l in lims if l.get("soft_only")}))}; check each product page.</p>
<h2>The carriers</h2>{cards}"""
    elif k == "airlines":
        soft = [p for p in P if p["category"] in ("soft_carrier", "backpack")]
        tr = ""
        for l in lims:
            fits = []
            for p in soft:
                if l.get("hard_only"):
                    continue
                for s in p["sizes"]:
                    if fit(s, l)[0] != "over":
                        fits.append(f"<a href='{p['slug']}.html'>{e(p['name'])}{'' if len(p['sizes'])==1 else ' ' + e(s['name'])}</a>")
            typ = "Soft-sided only" if l.get("soft_only") else ("Hard-sided limit" if l.get("hard_only") else ("Soft-sided limit" if l.get("soft_limit") else "Soft or hard"))
            tr += (f"<tr><td data-l='Airline'><a href='{root}airlines/{l['a']['slug']}.html'>{e(l['a']['name'])}</a><br><span class='small'>{e(l['label'])}</span></td>"
                   f"<td data-l='Limit'>{lim_txt(l)}<br><span class='small'>{e(l.get('reading',''))}</span></td><td data-l='Type'>{typ}</td>"
                   f"<td data-l='Carriers within'>{', '.join(fits) if fits else ('<span class=na>none of ours</span>' if not l.get('hard_only') else '<span class=na>no hard-sided carriers listed</span>')}</td></tr>")
        have = {l["a"]["slug"] for l in lims}
        miss = ", ".join(f"<a href='{root}airlines/{a['slug']}.html'>{e(a['name'])}</a>" for a in airlines if a["slug"] not in have)
        main = f"""<p>Each limit comes from the max carrier size on our airline page, which links to the official airline source and shows when we last verified it.</p>
<div class="tablewrap"><table class="cmp"><thead><tr><th>Airline</th><th>Max carrier (L &times; W &times; H)</th><th>Type</th><th>Carriers within the limit</th></tr></thead><tbody>{tr}</tbody></table></div>
<p class="small">Not listed (no confirmed cabin carrier size, or no pets in the cabin): {miss}.</p>"""
    elif k == "crates":
        cr = [p for p in P if p["category"] == "hard_crate"]
        tr = "".join(f"<tr><td data-l='Size'>{plink(p)} {e(s['name'])}</td><td data-l='Interior'>{dims(s)}</td></tr>" for p in cr for s in p["sizes"])
        notes = "".join(f"<li>{plink(p)}: {e(p['maker_says'][0])}</li>" for p in cr)
        main = f"""<p>Pets too big for the cabin usually fly in a hard kennel in the hold or as cargo. Airlines generally refer to the IATA <a href="https://www.iata.org/en/publications/store/live-animals-regulations/" rel="noopener" target="_blank">Live Animals Regulations</a> (see IATA's <a href="https://www.iata.org/en/programs/cargo/live-animals/pets/" rel="noopener" target="_blank">pet travel page</a>); confirm your airline's own crate rules.</p>
<h2>What the makers say</h2><ul>{notes}</ul>
<h2>Interior sizes</h2>
<div class="tablewrap"><table class="cmp"><thead><tr><th>Kennel &amp; size</th><th>Interior (L &times; W &times; H)</th></tr></thead><tbody>{tr}</tbody></table></div>
<p class="small">Petmate publishes interior dimensions only. Airline hold limits (such as Air Canada's 292 cm linear) apply to outside dimensions, so ask the maker or measure before booking.</p>
<h2>Airlines that take pets in the hold or as cargo</h2>{hold_table(airlines, root)}"""
    elif k == "backpacks":
        bp = [p for p in P if p["category"] == "backpack"]
        secs = "".join(f"<h3>{plink(p)}</h3><p>{dims(p['sizes'][0])}. {e(p['maker_says'][0])}</p>{fit_matrix(p, lims, root)}" for p in bp)
        main = f"""<p>Backpack carriers are tall, while airline under-seat limits are usually short (8 to 11 in / 20 to 27 cm high). Below, a backpack's published dimensions against each airline limit we've verified, standing upright.</p>
{secs}
<p>If you need a carrier for the cabin, compare the <a href="best-airline-approved-soft-carriers.html">soft under-seat carriers</a> instead.</p>"""
    elif k == "roadtrip":
        main = (f"""<p>A packing list for car trips with a dog. Products are grouped by need; every spec comes from the maker's official page (linked from each product page), and we have not tested them. Rules on restraining pets in cars vary by state and country, so check the rules where you'll drive.</p>"""
                + checklist_main(P, ROADTRIP_LIST, ROADTRIP_SECS, "dog", root)
                + f"""<h2>Flying instead?</h2><p>See the <a href="best-airline-approved-soft-carriers.html">soft carrier guide</a>, <a href="iata-hard-crates-for-cargo.html">hard crates for the hold</a> and our <a href="{root}index.html">airline pet policy pages</a>.</p>""")
    elif k == "cat":
        soft = ", ".join(plink(p) for p in P if p["category"] == "soft_carrier")
        main = (f"""<p>A checklist for travelling with a cat, by car or by plane. Every product spec below comes from the maker's official page, and we have not tested these products.</p>"""
                + checklist_main(P, CAT_LIST, [], "cat", root)
                + f"""<h2 id="carrier">The carrier</h2><p>For flights, the carrier usually has to fit under the seat in front of you. Compare carrier sizes with each airline's limit in <a href="under-seat-carrier-size-by-airline.html">carrier size by airline</a> and the <a href="best-airline-approved-soft-carriers.html">soft carrier guide</a>. Carriers we list: {soft}.</p>"""
                + checklist_main(P, [], CAT_SECS, "cat", root)
                + f"""<h2>Before you fly</h2><p>Check your airline's cabin pet rules (fees, carrier size, weight limit, breed restrictions) on our <a href="{root}index.html">airline pet policy pages</a>, each linked to the airline's official page and dated.</p>""")
    elif k == "bowls":
        bw = [p for p in P if p["category"] == "bowl"]
        tr = "".join(f"<tr><td data-l='Bowl'>{plink(p)}</td><td data-l='Size'>{e(a)}</td><td data-l='Specs'>{e(b)}</td></tr>" for p in bw for a, b in p["spec_rows"])
        cards = "".join(f"<h3>{plink(p)}</h3><p>{e(p.get('construction') or '')}. {e(' '.join(p.get('maker_says', [])))}</p>" for p in bw)
        main = f"""<p>A collapsible or nesting bowl lets you offer water during layovers. Sizes and capacities below are from each maker's official page.</p>
<div class="tablewrap"><table class="cmp"><thead><tr><th>Bowl</th><th>Size</th><th>Specs (per maker)</th></tr></thead><tbody>{tr}</tbody></table></div>{cards}"""
    else:
        raise ValueError(f"unknown guide kind {k!r}")
    other = "".join(f"<li><a href='{s}.html'>{e(GUIDE_META[s][0])}</a></li>" for s in GUIDE_META if s != slug)
    body = f"""{crumbs("{root}", title.split(':')[0])}
<h1>{e(title)}</h1>
<p class="verified">&#10003; Product {'specs' if k in ('roadtrip', 'cat') else 'dimensions'} checked <time datetime="{v}">{nice_date(v)}</time> against each manufacturer's official page{'' if k in ('roadtrip', 'cat') else '; airline limits from our dated airline pages'}.</p>
{ad_slot(cfg, 'guide_sponsor', '{root}')}
{main}
{forum_pages.guide_link(cfg, slug)}
<h2>More guides</h2><ul>{other}<li><a href="{{root}}products/">All pet travel products</a></li></ul>
{disclosure("{root}")}
"""
    ld = [bc_ld(cfg, [("Home", ""), ("Products", "products/"), (title.split(':')[0], f"products/{slug}.html")])]
    return page(cfg, f"{title} | {cfg['site_name']}", desc, body, f"products/{slug}.html", root, ld)


def build_products_index(cfg, pd, lims):
    root = "../"
    gl = "".join(f"<li><a href='{g['slug']}.html'>{e(GUIDE_META[g['slug']][0])}</a> <span class='small'>{e(GUIDE_META[g['slug']][1])}</span></li>" for g in pd["guides"])
    secs, jump = "", []
    for c, lbl in CATS.items():
        ps = [p for p in pd["products"] if p["category"] == c]
        if not ps:
            continue
        li = ""
        for p in ps:
            if c in ("soft_carrier", "backpack"):
                best = max((len(ok) for _, ok in fits_list(p, lims)), default=0)
                n = len(applicable(p, lims))
                info = (f"within {best} of {n} airline cabin limits (best size)" if best
                        else "Larger than the cabin limits we track; check the hold/cargo options")
            elif c == "hard_crate":
                info = f"{len(p['sizes'])} sizes, interior dimensions"
            elif p.get("summary"):
                info = p["summary"]
            else:
                info = "; ".join(f"{a}: {b}" for a, b in p["spec_rows"])[:90]
            li += f"<li><a href='{p['slug']}.html'>{e(p['name'])}</a> <span class='small'>{e(info)}</span></li>"
        jump.append(f"<a href='#{c}'>{e(lbl)}</a>")
        secs += f"<h2 id='{c}'>{e(lbl)}</h2><ul class='plist cards'>{li}</ul>"
    body = f"""{crumbs("{root}")}
<h1>Pet travel gear: carriers, crates and travel accessories, checked against official specs</h1>
{side_photo(cfg, "products_photo", "{root}")}
<p>Dimensions and specs for each product come from the manufacturer's official page (linked and dated). For carriers, we compare them with the cabin carrier limits on our <a href="{{root}}index.html">airline pet policy pages</a>. No prices, ratings or hands-on test claims: just published numbers you can check.</p>
<p class="small">Jump to: {" &middot; ".join(jump)}</p>
<h2>Guides</h2><ul class="plist cards guides">{gl}</ul>
{secs}
{disclosure("{root}")}
"""
    ld = [bc_ld(cfg, [("Home", ""), ("Products", "products/")]),
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": p["name"], "url": f"{site_base(cfg)}/products/{p['slug']}.html"}
              for i, p in enumerate(pd["products"])]}]
    return page(cfg, f"Pet travel carriers, crates & accessories: official specs and airline under-seat fit | {cfg['site_name']}",
                "Pet carriers, hard crates, car harnesses, seat covers, travel beds, calming aids, litter boxes and GPS trackers, with specs from official manufacturer pages; carriers compared with airline cabin limits.",
                body, "products/", root, ld)


def airline_carriers_block(a, pd, lims):
    al = [l for l in lims if l["a"]["slug"] == a["slug"] and not l.get("hard_only")]
    if not al:
        return (f"<aside class='reco'><h2>Carriers that fit this airline's limits</h2><p class='small'>We can't compare carriers for {e(a['name'])} because no cabin carrier size is confirmed above. "
                f"See <a href='../products/under-seat-carrier-size-by-airline.html'>carrier sizes by airline</a> or <a href='../products/iata-hard-crates-for-cargo.html'>hard crates for the hold</a>.</p></aside>")
    out = ""
    for l in al:
        items = []
        for p in pd["products"]:
            if l not in applicable(p, lims):
                continue
            for s in p["sizes"]:
                st, _ = fit(s, l)
                if st != "over":
                    nm = e(p["name"]) + ("" if len(p["sizes"]) == 1 else " " + e(s["name"]))
                    items.append(f"<a href='../products/{p['slug']}.html'>{nm}</a>" + (f" <span class='small'>(at {s['L_min']:g} in length)</span>" if st == "compressed" else ""))
        out += (f"<li><b>{e(l['label'])}</b> ({lim_txt(l)}): " + (", ".join(items) if items else
                "<span class='na'>none of the carriers we list</span>") + "</li>")
    return (f"<aside class='reco'><h2>Carriers that fit this airline's limits</h2><ul>{out}</ul>"
            f"<p class='small'>Based on manufacturer dimensions vs. the limit above; not a guarantee. <a href='../products/under-seat-carrier-size-by-airline.html'>All airlines</a> &middot; "
            f"<a href='../products/best-airline-approved-soft-carriers.html'>Soft carrier guide</a></p></aside>")


AMAZON_DP = "https://www.amazon.com/dp/{asin}"
# Universal travel items offered on every airline page after the fitting carriers (slug, optional size of the ASIN).
GEAR_FILL = [("kurgo-collaps-a-bowl", "Folds to under 1 in and holds 24 oz (per Kurgo), so it fits in a carrier pocket for water at the gate and after landing."),
             ("ruffwear-front-range-harness", "For dogs: a padded walking harness for the airport before and after the flight (linked: X-Small, girth 17&ndash;22 in; other sizes on the same Amazon page).")]
HOLD_CRATE = ("petmate-sky-kennel", '21"')


def amazon_asin(p, size=None):
    """Verified Amazon ASIN for a product (data/products.json amazon_asins), size-specific when the entry names a size."""
    for x in p.get("amazon_asins") or []:
        if x.get("asin") and (x.get("size") is None or x.get("size") == size):
            return x["asin"]
    return None


def amazon_dp(cfg, asin):
    return amazon_tagged(cfg, AMAZON_DP.format(asin=asin))


def airline_gear(a, pd, lims):
    """[(product, size or None, why_html)] for the airline gear box: up to 2 carriers whose published dimensions fit this
    airline's cabin limits (most limits fitted first, then without length compression, then roomiest), then universal items."""
    by = {p["slug"]: p for p in pd["products"]}
    al = [l for l in lims if l["a"]["slug"] == a["slug"] and not l.get("hard_only")]
    cands = []
    for p in pd["products"]:
        for s in p.get("sizes") or []:
            if not amazon_asin(p, s["name"]):
                continue
            res = [(l, fit(s, l)[0]) for l in al if l in applicable(p, lims)]
            ok = [(l, st) for l, st in res if st != "over"]
            if not ok:
                continue
            flag = any(l.get("soft_only") for l, _ in ok) and not p.get("construction")
            comp = any(st == "compressed" for _, st in ok)
            cands.append((-len(ok), comp, flag, -(s["L"] * s["W"] * s["H"]), p["slug"], s, ok, [l for l, st in res if st == "over"]))
    cands.sort(key=lambda c: c[:5])
    out, used = [], set()
    for *_, slug, s, ok, over in cands:
        if slug in used or len(out) >= 2:
            continue
        used.add(slug)
        p = by[slug]
        why = f"{dims(s)}: within " + " and ".join(
            f"the {e(l['label'])} limit ({lim_txt(l)}){' at its ' + format(s['L_min'], 'g') + ' in shortest length' if st == 'compressed' else ''}" for l, st in ok)
        if over:
            why += "; over the " + ", ".join(f"{e(l['label'])} limit ({lim_txt(l)})" for l in over)
        why += "."
        if any(l.get("soft_only") for l, _ in ok) and not p.get("construction"):
            why += f" {e(a['name'])} accepts soft-sided carriers only and {e(p['brand'])} doesn&rsquo;t state the construction; check before you fly."
        out.append((p, s["name"], why))
    if not al and a.get("in_cabin_allowed") is False and HOLD_CRATE[0] in by and amazon_asin(by[HOLD_CRATE[0]], HOLD_CRATE[1]):
        p = by[HOLD_CRATE[0]]
        s = next(x for x in p["sizes"] if x["name"] == HOLD_CRATE[1])
        out.append((p, s["name"], f"{e(a['name'])} carries no pets in the cabin, so pets fly in the hold in a hard kennel. Petmate says the Sky Kennel meets IATA Live Animals Regulations; "
                                  f"the linked {e(s['name'])} size measures {dims(s)} inside (other sizes on the same Amazon page). Choose the size from your pet&rsquo;s measurements and confirm crate rules with the airline."))
    for slug, why in GEAR_FILL:
        if len(out) >= 3:
            break
        if slug in by and amazon_asin(by[slug]):
            out.append((by[slug], None, why))
    return out[:3]


def airline_gear_box(cfg, a, pd, lims):
    items = airline_gear(a, pd, lims)
    if len(items) < 2:
        return ""
    li = []
    for p, size, why in items:
        nm = e(p["name"]) + (f" ({e(size)})" if size and len(p.get("sizes") or []) > 1 else "")
        li.append(f'<li><p class="gear-name"><a href="../products/{e(p["slug"])}.html">{nm}</a></p><p class="small">{why}</p>'
                  f'<p class="gear-buy"><a class="btn" href="{e(amazon_dp(cfg, amazon_asin(p, size)))}" rel="sponsored nofollow noopener" target="_blank">Check price on Amazon</a></p></li>')
    nofit = "" if any(p["category"] in ("soft_carrier", "backpack") for p, _, _ in items) or a.get("in_cabin_allowed") is False else \
        f"<p class='small'>No cabin carrier size is confirmed for {e(a['name'])} on this page, so we only suggest general travel items here.</p>"
    return (f'<aside class="reco gear"><h2>Gear that fits this airline</h2>{nofit}<ul class="gear-list">{"".join(li)}</ul>'
            f'<p class="small disc">Affiliate links: we may earn a commission at no extra cost to you. {AMAZON_DISCLOSURE} '
            + ('Fit is based on manufacturer dimensions vs. the limits above, not a guarantee. ' if any(p["category"] in ("soft_carrier", "backpack") for p, _, _ in items) else '')
            + f'Prices aren&rsquo;t shown because they change often. '
            f'<a href="../about.html#affiliates">Disclosure</a>.</p></aside>')


def flight_box(cfg, a):
    """'Book this flight' box from config.json flight_affiliates [{label, url_template, note}]; entries with an empty
    url_template are skipped, and the whole box is hidden when none is set. {airline} / {iata} are URL-encoded."""
    btns, notes = [], []
    for f in cfg.get("flight_affiliates") or []:
        t = (f.get("url_template") or "").strip()
        if not t or not f.get("label"):
            continue
        url = t.replace("{airline}", urllib.parse.quote(a["name"])).replace("{iata}", urllib.parse.quote(a.get("iata") or ""))
        btns.append(f'<a class="btn" href="{e(url)}" rel="sponsored nofollow noopener" target="_blank">{e(f["label"])}</a>')
        if f.get("note"):
            notes.append(e(f["note"]))
    if not btns:
        return ""
    return (f'<aside class="reco flights"><h2>Book a pet-friendly flight</h2>'
            f'<p>Compare fares on {e(a["name"])} and other airlines, then arrange your pet&rsquo;s place directly with the airline (see the rules above): pet space is limited per flight.</p>'
            f'<p class="buy">{" ".join(btns)}</p>{"".join(f"<p class=small>{n}</p>" for n in notes)}'
            f'<p class="small disc">Affiliate link: we may earn a commission at no extra cost to you. <a href="../about.html#affiliates">Disclosure</a>.</p></aside>')


def build_advertise(cfg):
    mail = obf_mail(cfg["contact_email"])
    body = f"""<h1>Advertise on {e(cfg['site_name'])}</h1>
<p>{e(cfg['site_name'])} helps people fly with a dog or cat: airline pet policies checked against the official source and dated, plus carrier and crate guides that compare official product dimensions with airline limits.</p>
<h2>Audience</h2>
<p>Pet owners planning to fly with their pets, in the cabin or in the hold, or to move abroad with them. Readers come to look up a specific airline's pet rules, carrier sizes, weight limits and fees. <b>Traffic stats available on request.</b></p>
<h2>Placements</h2>
<div class="tablewrap"><table class="cmp"><thead><tr><th>Placement</th><th>Where</th><th>Creative size</th></tr></thead><tbody>
<tr><td data-l="Placement">Airline page banner</td><td data-l="Where">Top of every airline pet policy page</td><td data-l="Size">728 &times; 90 px (scales down on mobile)</td></tr>
<tr><td data-l="Placement">Guide sponsor</td><td data-l="Where">Sponsor box in the product guides (carriers, crates, bowls)</td><td data-l="Size">300 &times; 250 px</td></tr>
<tr><td data-l="Placement">Site-wide footer</td><td data-l="Where">Footer of every page</td><td data-l="Size">468 &times; 60 px</td></tr>
</tbody></table></div>
<p class="small">Every placement is clearly labelled "Sponsored" and links with rel="sponsored nofollow". One advertiser per placement at a time. Sponsor creatives are images only (PNG, JPG or WebP); no pop-ups, auto-play or tracking scripts. Separately, the site also shows Google AdSense ads (see our <a href="{{root}}privacy.html">privacy policy</a>).</p>
<h2>Good fit for</h2>
<ul><li>Pet carrier, crate and travel gear brands</li><li>Pet insurance</li><li>Pet relocation and pet shipping services</li><li>Pet-friendly hotels and travel services</li></ul>
<h2>Editorial independence</h2>
<p>Sponsors never change our airline data, dimensions or fit results, and sponsored products get no special placement in guides (see our <a href="{{root}}about.html#affiliates">disclosure</a>).</p>
<h2>Rates and booking</h2>
<p><b>Rates on request.</b> Email {mail} with your brand, the placement you're interested in and your dates.</p>"""
    return page(cfg, f"Advertise on {cfg['site_name']}: reach pet owners planning to fly",
                "Sponsorship and banner placements on PetPolicyCheck for pet carrier brands, pet insurance, pet relocation and pet-friendly travel. Rates on request.",
                body, "advertise/", "../")


def build_partner_vets(cfg):
    import json as _j
    mail = obf_mail(cfg["contact_email"])
    clinics = _j.loads((ROOT / "data" / "partner_vets.json").read_text())["clinics"]
    if clinics:
        by = {}
        for c in clinics:
            by.setdefault(c["country"], {}).setdefault(c["city"], []).append(c)
        parts = []
        for country in sorted(by):
            parts.append(f"<h3>{e(country)}</h3>")
            for city in sorted(by[country]):
                rows = []
                for c in by[country][city]:
                    contact = " &middot; ".join(x for x in [
                        f'<a href="tel:{e(c["phone"])}">{e(c["phone"])}</a>' if c.get("phone") else "",
                        f'<a href="mailto:{e(c["email"])}">{e(c["email"])}</a>' if c.get("email") else ""] if x)
                    name = f'<a href="{e(c["url"])}" rel="noopener">{e(c["name"])}</a>' if c.get("url") else e(c["name"])
                    rows.append(f'<tr><td data-l="Clinic">{name}</td><td data-l="City">{e(city)}</td><td data-l="Contact">{contact}</td><td data-l="Travel services">{e(", ".join(c.get("services", [])))}</td></tr>')
                parts.append(f'<h4>{e(city)}</h4><div class="tablewrap"><table class="cmp"><thead><tr><th>Clinic</th><th>City</th><th>Contact</th><th>Travel services</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')
        listing = "".join(parts)
    else:
        listing = """<p><b>First partners coming soon.</b> We are inviting veterinary clinics in the United States first, then in South Korea. Partner clinics will be listed here by country and city, with their website, phone or email, and the travel services they offer, so you can contact them directly.</p>
<div class="tablewrap"><table class="cmp"><thead><tr><th>Clinic</th><th>City</th><th>Contact</th><th>Travel services</th></tr></thead><tbody>
<tr><td data-l="Clinic" colspan="4"><i>No partner clinics listed yet.</i></td></tr></tbody></table></div>"""
    body = f"""<h1>Partner vets: travel-ready clinics</h1>
<p>Flying with a dog or cat usually means a health certificate, up-to-date vaccinations (often a rabies titer test) and country-specific paperwork, all within strict time windows. Our partner veterinary clinics help pet owners prepare these documents ahead of the trip, so nothing is missing at check-in or at the border.</p>
<p class="small">Partner clinics are independent practices. {e(cfg['site_name'])} does not provide veterinary advice and is not paid for referrals; always confirm requirements with the clinic and the destination country's official authority.</p>
<h2>Partner clinics</h2>
{listing}
<h2>Are you a vet? Become a partner</h2>
<p>If your clinic issues pet travel health certificates, vaccinations or export paperwork, we would be glad to list you here free of charge so pet owners planning a trip can contact you directly. Email {mail} with your clinic's name, city, website and the travel services you offer.</p>"""
    return page(cfg, f"Partner vets for pet travel paperwork | {cfg['site_name']}",
                "Veterinary clinics that help pet owners prepare health certificates, vaccinations and travel paperwork before flying with a dog or cat.",
                body, "partner-vets/", "../")


BOOK_CSS = """<style>
.book{margin:20px 0 6px;padding:16px 16px 6px;border:1px solid var(--line2);border-top:3px solid var(--acc);border-radius:var(--r-m);background:var(--chip)}
.book>h2,.book>h3{margin:0 0 4px;font-size:1.2rem;color:var(--head)}
.book .book-lede{margin:0 0 10px;font-size:.9rem;color:var(--mut)}
.book-g{padding:10px 0 12px;border-top:1px solid var(--line)}
.book-g h4,.book-g h3{margin:0 0 8px;font:700 .78rem var(--text);letter-spacing:.1em;text-transform:uppercase;color:var(--acc)}
.book-btns{display:flex;flex-wrap:wrap;gap:8px;margin:0}
.book-btns .btn{padding:10px 14px;font-size:.74rem;letter-spacing:.06em;white-space:normal;text-align:center;border-radius:99px;max-width:100%}
.book-cities{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.book-cities a{display:inline-block;padding:7px 12px;border-radius:99px;border:1px solid var(--line2);color:var(--head);text-decoration:none;font-size:.88rem;background:var(--paper)}
.book-cities a:hover{border-color:var(--acc);color:var(--acc)}
.book-cities a.all{border-style:dashed}
.book-ride{margin:0;padding:0;list-style:none}
.book-ride li{margin:0 0 10px;font-size:.88rem;line-height:1.45;overflow-wrap:anywhere}
.book-ride b{color:var(--head)}
.book .book-disc{font-size:.75rem;color:var(--mut);margin:8px 0 0;line-height:1.4}
.book a{overflow-wrap:anywhere}
.book dl{margin:0 0 10px;display:grid;grid-template-columns:max-content 1fr;gap:4px 12px;font-size:.9rem}
.book dt{font-weight:700;color:var(--head)}.book dd{margin:0}
.book .book-svc{margin:0 0 12px}.book .book-svc h4{margin:0 0 6px;font-size:1rem;color:var(--head);text-transform:none;letter-spacing:0}
@media (max-width:480px){.book{padding:14px 12px 4px}.book dl{grid-template-columns:1fr}.book dt{margin-top:6px}}
</style>"""


BOOK_HOME_CSS = """<style>
.book-home .bh-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;align-items:stretch}
.book-home .book-g{border:1px solid var(--line);border-top:3px solid var(--acc);border-radius:var(--r-m);padding:18px 18px 14px;background:var(--paper);box-shadow:var(--shadow-s);display:flex;flex-direction:column}
.book-home .book-g h3{font-size:.82rem;margin:0 0 10px}
.book-home .book-g>p{font-size:.9rem;color:var(--ink)}
.book-home .bh-p{margin:0 0 10px;font-size:.9rem;line-height:1.45}
.book-home .bh-lux{margin-top:14px}
.book-home .book-btns{flex-direction:column}
.book-home .book-btns .btn{width:100%}
.book-home .book-disc{font-size:.75rem;color:var(--mut);margin:auto 0 0;padding-top:10px;line-height:1.4}
.book-home a{overflow-wrap:anywhere}
@media (max-width:900px){.book-home .bh-grid{grid-template-columns:1fr;gap:14px}}
@media (max-width:480px){.book-home .book-g{padding:14px 14px 12px}}
</style>"""


def flight_aff_buttons(cfg):
    """Sponsored flight search buttons from config.json flight_affiliates (shared by booking_block and /book/)."""
    btns = []
    for f in cfg.get("flight_affiliates") or []:
        u = (f.get("url_template") or "").strip()
        if u and f.get("label") and "{" not in u:
            btns.append(f'<a class="btn" href="{e(u)}" rel="sponsored nofollow noopener" target="_blank">{e(f["label"])}</a>')
    return btns


FLIGHT_DISC = 'Affiliate links: we may earn a commission at no extra cost to you. <a href="{root}about.html#affiliates">Disclosure</a>.'



def home_guides(cfg):
    """Country guides on the home map (static/home-c.html), from data/home_guides.json (one source of truth).
    Returns (guides_js, chips_html). Fails the build if a published guide page (data/routes/*.json,
    data/countries/*.json) has no entry, or an entry has no flag SVG / summary / guide page."""
    d = json.loads((ROOT / "data" / "home_guides.json").read_text())
    gs = d["guides"]
    urls = {g["url"] for g in gs}
    pages = [f"routes/{json.loads(f.read_text())['slug']}.html" for f in sorted((ROOT / "data" / "routes").glob("*.json"))]
    pages += [f"countries/{f.stem}.html" for f in sorted((ROOT / "data" / "countries").glob("*.json"))]
    missing = [u for u in pages if u not in urls]
    assert not missing, f"data/home_guides.json: add a home-map entry for {missing} (see fix4 HANDOFF.md)"
    base = site_base(cfg) + "/"
    out, chips = {}, []
    for g in gs:
        for k in ("id", "flag", "name", "title", "line", "cta", "url", "summary"):
            assert g.get(k), f"data/home_guides.json {g.get('name')}: missing '{k}'"
        assert (ROOT / "static" / "assets" / "img" / "flags" / f"{g['flag']}.svg").exists(), f"missing static/assets/img/flags/{g['flag']}.svg"
        j = {k: v for k, v in g.items() if k not in ("source_page", "chip")}
        j.update(kind="link", url=base + g["url"], flag_src=f"assets/img/flags/{g['flag']}.svg",
                 option=g.get("option") or f"{g['short'] if g.get('short') else g['name']} \u2605 guide")
        out[g["id"]] = j
        chips.append(f'<a class="uschip gchip" href="{e(base + g["url"])}" data-country="{e(g["id"])}">'
                     f'<img class="flag" src="assets/img/flags/{e(g["flag"])}.svg" width="21" height="14" alt="" aria-hidden="true">'
                     f'{e(g.get("chip") or g.get("short") or g["name"])}</a>')
    js = "var GUIDES=" + json.dumps(out, ensure_ascii=False).replace("</", "<\\/") + ";"
    return js, '<span class="gchips" role="group" aria-label="Country guides">' + "".join(chips) + "</span>"

def booking_block(cfg, root, full=False, home=False):
    """'Book your trip' block (USA): flights from config.json flight_affiliates, pet-friendly hotel city guides from
    data/hotels/us-cities.json (new cities appear automatically) and Uber/Lyft pet ride rules from data/rideshare/us.json
    (official help pages only). full=True is the longer version for /countries/usa.html; False is the compact home-panel one.
    home=True is the server-rendered three-column homepage section ('Plan and book your whole pet trip in one place')."""
    rs = json.loads((ROOT / "data" / "rideshare" / "us.json").read_text())
    _, ci = hotels_data()
    hx = "h3" if (full or home) else "h4"
    ext = lambda u, t: f'<a href="{e(u)}" rel="noopener" target="_blank">{e(t)} &#8599;</a>'
    # (a) flights
    btns = flight_aff_buttons(cfg)
    fl = ""
    if btns:
        fl = (f'<div class="book-g"><{hx}>&#9992; Flights</{hx}>'
              + ('<p style="margin:0 0 8px;font-size:.9rem">Compare fares, then book your pet&rsquo;s spot directly with the airline: in-cabin pet space is limited per flight. '
                 f'<a href="{root}products/under-seat-carrier-size-by-airline.html">Under-seat carrier sizes</a>.</p>' if (full or home) else "")
              + f'<p class="book-btns">{"".join(btns)}</p>'
              f'<p class="book-disc">{FLIGHT_DISC.replace("{root}", root)}</p></div>')
    # (b) hotels by city
    cities = "".join(f'<li><a href="{root}hotels/pet-friendly-hotels-{e(c["slug"])}.html">{e(c["short"])}</a></li>' for c in ci["cities"])
    if home:
        lux = "".join(f'<li><a href="{root}hotels/pet-friendly-hotels-{e(c["slug"])}.html#luxury">{e(c["short"])}</a></li>' for c in ci["cities"] if c.get("luxury"))
        ho = (f'<div class="book-g"><{hx}>&#127976; Pet-friendly hotels</{hx}>'
              '<p class="bh-p">Chain pet fees, weight limits and number of pets, plus airport pet relief areas and dog parks, from official sources. Pick a city:</p>'
              f'<ul class="book-cities">{cities}<li><a class="all" href="{root}hotels/">All chains: fees &amp; weight limits</a></li></ul>'
              f'<p class="bh-p bh-lux"><b>Luxury hotels</b> set pet rules hotel by hotel:</p>'
              f'<ul class="book-cities">{lux}<li><a class="all" href="{root}hotels/#luxury">Luxury brands</a></li></ul></div>')
    else:
        ho = (f'<div class="book-g"><{hx}>&#127976; Pet-friendly hotels by city</{hx}>'
              + ('<p style="margin:0 0 8px;font-size:.9rem">Each city guide has the chain pet rules (fee, weight, number of pets), luxury hotels&rsquo; own pet policies, airport pet relief areas and dog parks, all from official sources.</p>' if full else "")
              + f'<ul class="book-cities">{cities}<li><a class="all" href="{root}hotels/">All chains: fees &amp; weight limits</a></li></ul></div>')
    # (c) airport to hotel
    chk = f'<time datetime="{rs["checked"]}">{nice_date(rs["checked"])}</time>'
    if full:
        svc = ""
        for s in rs["services"]:
            dl = "".join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v, _ in s["facts"])
            srcs = " &middot; ".join(ext(u, t) for t, u in s["sources"].values())
            svc += f'<div class="book-svc"><h4>{e(s["name"])}</h4><dl>{dl}</dl><p class="book-disc">Source: {srcs}</p></div>'
        rob = "".join(f'<li><b>{e(r["name"])}:</b> {e(r["rule"])} {ext(r["src"][1], r["src"][0])}</li>' for r in rs["robotaxis"])
        ride = (f'<div class="book-g"><h3>&#128661; Airport to hotel with your pet</h3>{svc}'
                f'<p style="font-size:.9rem;margin:0 0 6px"><b>Robotaxis: service animals only.</b></p><ul class="book-ride">{rob}</ul>'
                f'<p class="book-disc">{e(rs["service_animals_note"])} Plain links to the official pages (no affiliate). Checked on the official Uber, Lyft, Waymo, Zoox and Tesla pages on {chk}; fees and availability change, so check the app before you ride.</p></div>')
    else:
        li = "".join(f'<li><b>{e(s["name"])}:</b> {e(s["short"])} {ext(s["sources"]["rider"][1], s["name"].split()[0] + " help")}</li>' for s in rs["services"])
        rnames = ", ".join(r["name"] for r in rs["robotaxis"][:-1]) + " and " + rs["robotaxis"][-1]["name"]
        rlinks = " &middot; ".join(ext(r["src"][1], r["name"]) for r in rs["robotaxis"])
        li += f'<li><b>Robotaxis:</b> {e(rnames)} do not take pets; service animals only. {rlinks}</li>'
        ride = (f'<div class="book-g"><{hx}>&#128661; {"Airport rides with your pet" if home else "Airport to hotel with your pet"}</{hx}><ul class="book-ride">{li}</ul>'
                f'<p class="book-disc">{e(rs["service_animals_note"])} Official pages checked {chk}; no affiliate links. <a href="{root}countries/usa.html#book">Details</a>.</p></div>')
    if home:
        return ('<section class="blk wrap book-home" id="plan-trip" aria-labelledby="plan-trip-h">'
                '<h2 id="plan-trip-h">Plan and book your whole pet trip in one place</h2>'
                '<p class="sub">Flights, pet-friendly hotels and airport rides with your dog or cat: everything ready before you go.</p>'
                f'<div class="bh-grid">{fl}{ho}{ride}</div></section>')
    h = "h2" if full else "h3"
    lede = "Flights, pet-friendly hotels by city, and a ride from the airport with your pet." if full else "Flights, hotels by city and pet-friendly rides."
    return f'<section class="book" id="book" aria-labelledby="book-h"><{h} id="book-h">Book your trip</{h}><p class="book-lede">{lede}</p>{fl}{ho}{ride}</section>'


CHECKLIST_PDF = "downloads/pet-travel-checklist-usa.pdf"
CHECKLIST_CSS = """<style>
.ck-cta{display:flex;align-items:center;gap:16px;background:var(--paper,#11252a);border:1px solid #d9b76555;border-left:4px solid var(--gold,#d9b765);border-radius:10px;padding:12px 16px;margin:18px 0}
.ck-cta img{flex:none;width:64px;height:auto;border-radius:4px;box-shadow:0 2px 10px #0006}
.ck-cta p{margin:0}.ck-cta .ck-t{font-family:var(--disp);color:var(--head);font-size:1.12rem;line-height:1.25}.ck-cta .ck-s{font-size:.9rem;color:var(--mut)}
.ck-cta .btn{margin-left:auto;flex:none}
.ck-cta>div{flex:1 1 200px;min-width:0}
@media (max-width:640px){.ck-cta{flex-wrap:wrap}.ck-cta img{width:48px}.ck-cta .btn{margin-left:0;width:100%;justify-content:center}}
</style>"""


def checklist_cta(root):
    """Compact box linking to /pet-travel-checklist/ (USA rules page and homepage)."""
    return (f'{CHECKLIST_CSS}<aside class="ck-cta" id="free-checklist" aria-label="Free pet travel checklist">'
            f'<img src="{root}assets/img/checklist-thumb.webp" width="64" height="83" alt="" loading="lazy">'
            f'<div><p class="ck-t">Free printable: Pet Travel Checklist USA (PDF)</p>'
            f'<p class="ck-s">Documents, airline cabin vs. hold, Amtrak, hotels and a departure-day list on 2 pages. No sign-up.</p></div>'
            f'<a class="btn" href="{root}pet-travel-checklist/">Get the checklist</a></aside>')


def build_checklist(cfg):
    """/pet-travel-checklist/: landing page for the free PDF (static/downloads/, made by checklist/make_checklist_pdf.py)."""
    root = "../"
    pdf = ROOT / "static" / CHECKLIST_PDF
    kb = round(pdf.stat().st_size / 1024) if pdf.exists() else 0
    css = """<style>
.ck-hero{display:grid;grid-template-columns:minmax(0,1fr) 260px;gap:32px;align-items:start;margin:8px 0 24px}
.ck-hero img{width:100%;height:auto;border-radius:6px;box-shadow:0 0 0 1px #d9b76566,0 12px 32px #0008}
.ck-hero ul{padding-left:1.2em}.ck-hero li{margin:.3em 0}
.ck-dl{margin:18px 0 6px}.ck-note{color:var(--mut);font-size:.92rem;margin:6px 0 0}
@media (max-width:720px){.ck-hero{grid-template-columns:1fr}.ck-hero .ck-img{max-width:240px}}
</style>"""
    body = f"""{css}<nav class="crumbs"><a href="{root}index.html">Home</a> &rsaquo; Pet travel checklist</nav>
<h1>Free Pet Travel Checklist USA (printable PDF)</h1>
<div class="ck-hero"><div>
<p class="lead">A 2-page checklist for traveling in the US with a dog or cat, built from the rules on this site. Every section links back to the page where we cite the official source.</p>
<ul><li><b>Documents:</b> vet health certificate, USDA APHIS endorsement for international trips, rabies certificate, microchip, CDC Dog Import Form</li>
<li><b>Flying:</b> cabin or hold by airline, under-seat carrier sizes</li>
<li><b>Amtrak:</b> weight, carrier, trip length and check-in rules</li>
<li><b>Hotels:</b> what to confirm before you book</li>
<li><b>Departure day:</b> what to pack and when to arrive</li></ul>
<p class="ck-dl"><a class="btn book-cta" href="{root}{CHECKLIST_PDF}" download>Download the free PDF</a></p>
<p class="ck-note">No sign-up needed. Free to share. US Letter, 2 pages{f", {kb} KB" if kb else ""}. Last checked: Oct 2026.{f' Saving ink? <a href="{root}{CHECKLIST_PDF.replace(".pdf", "-print.pdf")}" download>Light print version</a>.' if (ROOT / "static" / CHECKLIST_PDF.replace(".pdf", "-print.pdf")).exists() else ""}</p>
</div><div class="ck-img"><a href="{root}{CHECKLIST_PDF}" download><img src="{root}assets/img/checklist-thumb.webp" width="480" height="621" alt="Page 1 of the Pet Travel Checklist USA: documents and flying sections"></a></div></div>
<p class="warn usa-warn">Rules change; always confirm with the airline and official sources. For the full details see <a href="{root}countries/usa.html">pet travel rules for the USA</a>, the <a href="{root}products/under-seat-carrier-size-by-airline.html">carrier size by airline</a> guide and <a href="{root}hotels/">pet-friendly hotel rules</a>.</p>"""
    return page(cfg, f"Free Pet Travel Checklist USA (printable PDF) | {cfg['site_name']}",
                "A free 2-page printable checklist for US pet travel: documents, airline cabin vs. hold, carrier size, Amtrak, hotels and departure day. No sign-up.",
                body, "pet-travel-checklist/", root,
                jsonld=[bc_ld(cfg, [("Home", ""), ("Pet travel checklist", "pet-travel-checklist/")])], ads=False)


def build_country_usa(cfg, airlines):
    """US pet travel rules page (federal + per-state), from data/countries/usa.json. Every row carries its official source."""
    d = json.loads((ROOT / "data" / "countries" / "usa.json").read_text())
    root, chk = "../", d["checked"]
    src = lambda u, t="Official source": f'<a href="{e(u)}" rel="noopener" target="_blank">{t}</a>'
    checked = f'Last checked <time datetime="{chk}">{nice_date(chk)}</time>'

    def agency(u):
        h = u.split("/")[2]
        return "CDC" if h.endswith("cdc.gov") else "USDA APHIS" if h.endswith("aphis.usda.gov") else "Official source"

    def srcnote(rows):  # rows checked on another date than the page date get it next to their link
        return lambda r: "" if r.get("checked", chk) == chk else f" <span class='small'>checked <time datetime='{r['checked']}'>{nice_date(r['checked'])}</time></span>"
    fed = {f["topic"]: f for f in d["federal"]}
    hi = next(s for s in d["states"] if s["code"] == "HI")
    quick = [
        ("Dogs entering the US", "CDC Dog Import Form receipt for every dog, plus a healthy look, age 6 months or older and a microchip. Dogs from high-risk rabies countries need extra forms (see below).", fed["Dogs entering the US"]["source_url"]),
        ("Cats entering the US", "No federal rabies proof or USDA health requirements for pet cats; they must look healthy. State, airline, Hawaii and Guam rules still apply.", fed["Cats entering the US"]["source_url"]),
        ("Traveling between states", "No federal rule: the destination state decides. Many states want a CVI (health certificate, usually issued within 30 days) and proof of rabies vaccination; airlines often want a certificate within 10 days.", fed["Traveling between states"]["source_url"]),
        ("Hawaii", "Rabies-free with a quarantine program: two rabies vaccinations, a passing FAVN test and a 30-day wait are needed to qualify for direct release; otherwise up to 120 days of quarantine.", hi["source_url"]),
    ]
    qa = "".join(f"<li><b>{e(q)}:</b> {e(a)} {src(u, 'Source')}</li>" for q, a, u in quick)
    fsn = srcnote(d["federal"])
    fr = lambda t, who, way, case: (f"<tr><td data-l='Who'>{who}</td><td data-l='Direction'>{way}</td><td data-l='Case'>{case}</td>"
                                    f"<td data-l='Rule'>{e(fed[t]['rule'])}</td><td class='usa-src' data-l='Source'>{src(fed[t]['source_url'], agency(fed[t]['source_url']))}{fsn(fed[t])}</td></tr>")
    fed_rows = "".join([
        fr("Dogs from rabies-free or low-risk countries", "Dogs", "Entering", "From a rabies-free or low-risk country"),
        fr("US-vaccinated dogs returning from high-risk countries", "Dogs", "Entering", "US-vaccinated, returning from a high-risk country"),
        fr("Foreign-vaccinated dogs from high-risk countries", "Dogs", "Entering", "Foreign-vaccinated, from a high-risk country"),
        fr("Dogs from screwworm or FMD-affected countries (USDA)", "Dogs", "Entering", "From a screwworm- or FMD-affected country (USDA)"),
        fr("Cats entering the US", "Cats", "Entering", "All cats"),
        fr("Leaving the US", "Dogs &amp; cats", "Leaving", "Export to another country"),
        fr("Traveling between states", "Dogs &amp; cats", "Between states", "Moving within the US"),
        fr("Airline health certificate", "Dogs &amp; cats", "Flying", "Airline health certificate"),
    ])
    ssn = srcnote(d["states"])

    def srow(s, in_diff):
        rid = f' id="st-{e(s["code"].lower())}"' if in_diff else ""
        cls = ' class="usa-hl"' if s["differs"] and not in_diff else ""
        badge = f' <a class="flag" href="#st-{e(s["code"].lower())}" title="See States with different rules">Differs</a>' if s["differs"] and not in_diff else ""
        cvi = f'<span class="flag">Check</span> {e(s["cvi"])}' if not s["verified"] else e(s["cvi"])
        return (f"<tr{rid}{cls}><td data-l='State'><b>{e(s['name'])}</b>{badge}</td>"
                f"<td data-l='CVI required?'>{cvi}</td><td data-l='Rabies vaccine'>{e(s['rabies'])}</td>"
                f"<td data-l='Special notes'>{e(s['notes']) or '<span class=na>None stated</span>'}</td>"
                f"<td class='usa-src' data-l='Source'>{src(s['source_url'])}{ssn(s)}</td></tr>")
    head = "<thead><tr><th>State</th><th>CVI required for dogs/cats entering?</th><th>Rabies vaccine rule</th><th>Special notes</th><th>Official source</th></tr></thead>"
    diff = sorted((s for s in d["states"] if s["differs"]), key=lambda s: (s["code"] != "HI", s["name"]))
    nver = sum(s["verified"] for s in d["states"])
    allrows = "".join(srow(s, False) for s in sorted(d["states"], key=lambda s: s["name"]))
    tsn = srcnote(d["territories"])
    terr = "".join(f"<tr><td data-l='Territory'><b>{e(t['name'])}</b></td><td data-l='Rule'>{e(t['rule'])}</td><td class='usa-src' data-l='Source'>{src(t['source_url'])}{tsn(t)}</td></tr>" for t in d["territories"])
    links = "".join(f"<li>{src(u, e(n))}</li>" for n, u in d["links"])
    want = ["american", "delta", "united", "alaska", "hawaiian", "southwest", "jetblue"]
    names = {a["slug"]: a["name"] for a in airlines}
    al = "".join(f"<a href='{root}airlines/{s}.html'>{e(names.get(s, s.title()))}</a>" for s in want if s in names)
    gl = "".join(f"<li><a href='{root}products/{g}.html'>{e(t)}</a></li>" for g, (t, _) in GUIDE_META.items())
    tr = d.get("train")
    train = ""
    if tr:  # 'By train (Amtrak)' section, from data/countries/usa.json "train"
        tli = "".join(f"<li><b>{e(k)}:</b> {e(v)}</li>" for k, v in tr["rules"])
        train = (f'<h2 id="train">{e(tr["heading"])}</h2><div class="usa-quick usa-train"><ul>{tli}</ul></div>'
                 f'<p class="small">{e(tr["service_animals_note"])} Source: {src(tr["source_url"], e(tr["source_name"]) + " &#8599;")}, '
                 f'checked <time datetime="{e(tr["checked"])}">{nice_date(tr["checked"])}</time>.</p>')
    css = """<style>
.usa-quick{background:var(--sage-l);border:0;border-left:4px solid var(--sage);border-radius:10px;padding:14px 18px}
.usa-quick h2{margin:0 0 .4em}.usa-quick ul{margin:0;padding-left:1.2em}.usa-quick li{margin:.35em 0}
.usa-warn{border:0;border-left:4px solid var(--gold)}
.usa-t .usa-src{white-space:nowrap}
.usa-t tbody tr.usa-hl>td{background:rgba(217,183,101,.07)}
.usa-t tbody tr.usa-hl>td:first-child{box-shadow:inset 3px 0 0 var(--gold)}
.usa-t a.flag{text-decoration:none;margin-left:4px;white-space:nowrap}.usa-t a.flag:hover{background:var(--gold);color:#0b1719}
.usa-t tr[id]{scroll-margin-top:calc(var(--hh, 64px) + 16px)}
.usa-t tr[id]:target>td{background:rgba(217,183,101,.14)}
@media (max-width:720px){.usa-t .usa-src{white-space:normal}.usa-t tbody tr.usa-hl>td:first-child{box-shadow:none}.usa-t tbody tr.usa-hl{box-shadow:inset 3px 0 0 var(--gold)}.usa-t tbody tr.usa-hl>td{background:none}}
</style>"""
    css += BOOK_CSS
    body = f"""{css}<nav class="crumbs"><a href="{root}index.html">Home</a> &rsaquo; Countries &rsaquo; United States</nav>
<h1>Pet travel rules for the USA: federal and state requirements</h1>
<p class="lead">What you need to fly a dog or cat into, out of, or around the United States. Federal rules come from the CDC and USDA; each state sets its own entry rules.</p>
<div class="usa-quick"><h2 id="quick">Quick answer</h2><ul>{qa}</ul></div>
<p class="warn usa-warn">Rules change, especially New World screwworm (NWS) restrictions added by many states in 2026. Always confirm with the official source before you travel. {checked}.</p>
{checklist_cta(root)}
{booking_block(cfg, root, full=True)}
<h2 id="federal">Federal rules (CDC and USDA)</h2>
<p class="small">{checked} on the CDC and USDA APHIS pages linked in each row.</p>
<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Who</th><th>Direction</th><th>Case</th><th>Rule</th><th>Source</th></tr></thead><tbody>{fed_rows}</tbody></table></div>
{train}
<h2 id="different">States with different rules</h2>
<p>These {len(diff)} states or territories do not follow the common pattern of "CVI plus rabies vaccination at about 3 months for every pet". Some skip the CVI for pets traveling with their owner; others are stricter. <span class="small">{checked} on each state's official page.</span></p>
<div class="tablewrap"><table class="cmp usa-t">{head}<tbody>{''.join(srow(s, True) for s in diff)}</tbody></table></div>
<h2 id="states">All 50 states, DC and Puerto Rico</h2>
<p class="small">{checked}. {nver} of {len(d['states'])} rows verified on official state pages; rows marked <span class="flag">Check</span> could not be confirmed, so contact that state veterinarian. States marked <span class="flag">Differs</span> are highlighted; the badge jumps to their row in the table above. CVI = Certificate of Veterinary Inspection (health certificate) from an accredited vet.</p>
<div class="tablewrap"><table class="cmp usa-t">{head}<tbody>{allrows}</tbody></table></div>
<h2 id="territories">Guam and other territories</h2>
<p class="small">{checked}.</p>
<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Territory</th><th>Rule</th><th>Source</th></tr></thead><tbody>{terr}</tbody></table></div>
<h2 id="official">Official links</h2>
<ul>{links}</ul>
<p class="note small">{checked}. Rules change; confirm with the official source before you travel. This page is a summary, not legal or veterinary advice. Airlines may require more than the state does.</p>
<h2 id="hotels">Pet-friendly hotels</h2>
<p>Pet fees, weight limits and number of pets at the big US hotel chains, from their official sites: <a href="{root}hotels/">pet-friendly hotel rules</a>. City guides: <a href="{root}hotels/pet-friendly-hotels-orlando.html">Orlando</a>, <a href="{root}hotels/pet-friendly-hotels-new-york.html">New York</a>, <a href="{root}hotels/pet-friendly-hotels-miami.html">Miami</a>.</p>
{insurance_teaser(root, "usa")}
<h2 id="airlines">Airline pet policies</h2>
<div class="chips">{al}</div>
<h2 id="gear">Product guides</h2>
<ul>{gl}</ul>"""
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": qn, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for qn, (_, a, _u) in zip(["What does a dog need to enter the United States?", "What does a cat need to enter the United States?",
                                   "What do I need to take a dog or cat between US states?", "What are the rules for bringing a dog or cat to Hawaii?"], quick)]}
    return page(cfg, f"Pet travel rules for the USA: federal and state requirements | {cfg['site_name']}",
                "CDC and USDA rules for dogs and cats entering or leaving the US, plus a state-by-state table of health certificate (CVI) and rabies rules, with official sources.",
                body, "countries/usa.html", root,
                jsonld=[bc_ld(cfg, [("Home", ""), ("United States pet travel rules", "countries/usa.html")]), faq_ld])


def build_route_usa_japan(cfg, airlines):
    """USA -> Japan route page (preview), from data/routes/usa-japan.json. Every row carries its official source."""
    d = json.loads((ROOT / "data" / "routes" / "usa-japan.json").read_text())
    root, chk, S = "../", d["checked"], d["sources"]
    src = lambda u, t="Official source": f'<a href="{e(u)}" rel="noopener" target="_blank">{t}</a>'
    checked = f'Last checked <time datetime="{chk}">{nice_date(chk)}</time>'

    def agency(k):
        h = S[k].split("/")[2]
        return "Japan AQS" if h.endswith("maff.go.jp") else "CDC" if h.endswith("cdc.gov") else "USDA APHIS" if h.endswith("aphis.usda.gov") else "Official source"
    chkflag = lambda r: '<span class="flag">Check</span> ' if r.get("check") else ""
    qa = "".join(f"<li><b>{e(q)}:</b> {e(a)} {src(S[k], 'Source')}</li>" for q, a, k in d["quick"])
    rows = "".join(f"<tr><td data-l='Who'>{e(r['who'])}</td><td data-l='Direction'>{e(r['way'])}</td><td data-l='Case'>{e(r['case'])}</td>"
                   f"<td data-l='Rule'>{e(r['rule'])}</td><td class='usa-src' data-l='Source'>{src(S[r['src']], agency(r['src']))}</td></tr>" for r in d["rules"])
    fees = "".join(f"<tr><td data-l='Item'>{e(f['item'])}</td><td data-l='Cost (USD)'>{chkflag(f)}{e(f['amount'])}</td>"
                   f"<td class='usa-src' data-l='Source'>{src(S[f['src']], agency(f['src']))}</td></tr>" for f in d["fees"])
    quar = "".join(f"<tr><td data-l='Situation'>{e(q['item'])}</td><td data-l='Quarantine'>{e(q['detail'])}</td>"
                   f"<td class='usa-src' data-l='Source'>{src(S[q['src']], agency(q['src']))}</td></tr>" for q in d["quarantine"])
    offs = "".join(f"<tr><td data-l='Airport'><b>{e(o['airport'])}</b></td><td data-l='AQS office'>{e(o['office'])}</td><td data-l='Phone'>{e(o['phone'])}</td>"
                   f"<td class='usa-src' data-l='Source'>{src(S[o['src']], agency(o['src']))}</td></tr>" for o in d["offices"])
    links = "".join(f"<li>{src(S[k], e(n))}</li>" for n, k in d["links"])
    by = {a["slug"]: a for a in airlines}
    arows = []
    for s in d["airlines"]:
        a = by.get(s)
        if not a:
            continue
        note = (f"<b>Route limits:</b> {e(a.get('banned_routes') or 'none listed.')} "
                f"<b>Hold or cargo:</b> {e(a.get('checked_or_cargo') or CHECK)}")
        arows.append(f"<tr><td data-l='Airline'><a href='{root}airlines/{e(s)}.html'><b>{e(a['name'])}</b></a></td>"
                     f"<td data-l='What our airline page says'>{note}</td>"
                     f"<td data-l='Japan flights'><span class='flag'>Check</span> Confirm with the airline for your Japan flight</td>"
                     f"<td class='usa-src' data-l='Checked'>{src(a['official_url'], 'Airline page')} <span class='small'>checked <time datetime='{e(a.get('last_verified') or '')}'>{nice_date(a.get('last_verified'))}</time></span></td></tr>")
    btns = [f'<a class="btn" href="{e(f["url_template"].strip())}" rel="sponsored nofollow noopener" target="_blank">{e(f["label"])}</a>'
            for f in cfg.get("flight_affiliates") or [] if (f.get("url_template") or "").strip() and f.get("label")]
    fbox = ("" if not btns else
            f'<aside class="reco flights"><h2>Book flights to Japan</h2>'
            f'<p>Compare fares from the US to Tokyo (Narita or Haneda), Osaka (Kansai) and other Japanese airports, then arrange your pet&rsquo;s place directly with the airline before you buy: pet space is limited per flight, and your arrival airport must match your AQS notification.</p>'
            f'<p class="buy">{" ".join(btns)}</p>'
            f'<p class="small disc">Affiliate links: we may earn a commission at no extra cost to you. <a href="{root}about.html#affiliates">Disclosure</a>.</p></aside>')
    gl = "".join(f"<li><a href='{root}products/{g}.html'>{e(t)}</a></li>" for g, (t, _) in GUIDE_META.items() if g != "dog-road-trip-packing-list")
    css = """<style>
.usa-quick{background:var(--sage-l);border:0;border-left:4px solid var(--sage);border-radius:10px;padding:14px 18px}
.usa-quick h2{margin:0 0 .4em}.usa-quick ul{margin:0;padding-left:1.2em}.usa-quick li{margin:.35em 0}
.usa-warn{border:0;border-left:4px solid var(--gold)}
.usa-t .usa-src{white-space:nowrap}
.rj-air td:nth-child(3){min-width:9em}
.tablewrap+.tablewrap{margin-top:16px}
@media (max-width:720px){.usa-t .usa-src{white-space:normal}}
</style>"""
    body = f"""{css}<nav class="crumbs"><a href="{root}index.html">Home</a> &rsaquo; Routes &rsaquo; USA to Japan</nav>
<h1>Flying with a dog or cat from the USA to Japan</h1>
<p class="lead">What your dog or cat needs to fly from the United States to Japan without a long quarantine, and what you need to bring it back. Japan&rsquo;s rules come from the Animal Quarantine Service (AQS) of the Ministry of Agriculture, Forestry and Fisheries (MAFF); USDA APHIS endorses the US health certificate. By our count you need at least about 7 months from the first rabies shot to arrival (30 days between shots, then the 180-day wait), so start early.</p>
<div class="usa-quick"><h2 id="quick">Quick answer</h2><ul>{qa}</ul></div>
<p class="warn usa-warn">Rules change. Always confirm with Japan&rsquo;s AQS and USDA APHIS before you travel; a missing date or signature can mean up to 180 days of quarantine. {checked}.</p>
<h2 id="rules">Rules by case</h2>
<p class="small">{checked} on the Japan AQS, USDA APHIS and CDC pages linked in each row. Where AQS and APHIS word a rule differently, we follow Japan&rsquo;s AQS page.</p>
<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Who</th><th>Direction</th><th>Case</th><th>Rule</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2 id="fees">Fees and quarantine</h2>
<p class="small">{checked}. Prices in US dollars where the source gives them. Rows marked <span class="flag">Check</span> have no official amount we could confirm.</p>
<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Item</th><th>Cost</th><th>Source</th></tr></thead><tbody>{fees}</tbody></table></div>
<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Situation</th><th>Quarantine in Japan</th><th>Source</th></tr></thead><tbody>{quar}</tbody></table></div>
<h2 id="airports">Airports and AQS offices</h2>
<p class="small">{checked}. Send the advance notification to the AQS office at the airport where you will land; email addresses are on the <a href="{e(S['aqs_contact'])}" rel="noopener" target="_blank">AQS contact page</a>.</p>
<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Airport</th><th>AQS office</th><th>Phone</th><th>Source</th></tr></thead><tbody>{offs}</tbody></table></div>
<h2 id="airlines">US airlines to Japan</h2>
<p class="small">From our airline pages, checked on the airline&rsquo;s official site on the date shown. Airline rules are separate from Japan&rsquo;s entry rules; confirm in-cabin or cargo acceptance for your exact flight.</p>
<div class="tablewrap"><table class="cmp usa-t rj-air"><thead><tr><th>Airline</th><th>What our airline page says</th><th>Japan flights</th><th>Source</th></tr></thead><tbody>{''.join(arows)}</tbody></table></div>
{fbox}
{insurance_teaser(root, "japan")}
<h2 id="return">Coming back to the USA</h2>
<p>Japan is not on the CDC list of high-risk countries for dog rabies, so a dog that was only in Japan (or other low-risk countries) in the 6 months before returning needs the free <b>CDC Dog Import Form</b> receipt, a microchip, a healthy look and an age of at least 6 months; the CDC simplified this on August 1, 2024. Cats have no federal rabies proof requirement. State and airline rules still apply. {src(S['cdc_low'], 'CDC')} &middot; {src(S['cdc_high'], 'CDC high-risk list')}</p>
<p>Full US entry and state rules: <a href="{root}countries/usa.html">Pet travel rules for the USA</a>.</p>
<p>Staying in a US city before or after the flight? <a href="{root}hotels/">Pet-friendly hotel rules by chain</a> (fees, weight limits, number of pets), with guides for <a href="{root}hotels/pet-friendly-hotels-new-york.html">New York</a>, <a href="{root}hotels/pet-friendly-hotels-orlando.html">Orlando</a> and <a href="{root}hotels/pet-friendly-hotels-miami.html">Miami</a>.</p>
<h2 id="official">Official links</h2>
<ul>{links}</ul>
<p class="note small">{checked}. Rules change; confirm with the official source before you travel. This page is a summary, not legal or veterinary advice. Airlines may require more than Japan does.</p>
<h2 id="gear">Product guides</h2>
<ul>{gl}</ul>"""
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": qn, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for qn, (_, a, _k) in zip(["What does a dog or cat need to fly from the US mainland to Japan?",
                                   "How far ahead do I need to notify Japan's Animal Quarantine Service?",
                                   "Who endorses the US health certificate for a pet going to Japan?",
                                   "What are the rules for taking a pet from Hawaii or Guam to Japan?",
                                   "What happens if my pet doesn't meet Japan's requirements?",
                                   "What does a dog need to return to the US from Japan?"], d["quick"])]}
    return page(cfg, f"Flying with a dog or cat from the USA to Japan: rules, timeline and fees | {cfg['site_name']}",
               "What a dog or cat needs to fly from the US to Japan: microchip, two rabies shots, titer test, 180-day wait, 40-day AQS notice, USDA APHIS endorsement, fees and how to come back, with official sources.",
               body, "routes/usa-to-japan.html", root,
               jsonld=[bc_ld(cfg, [("Home", ""), ("Flying with a dog or cat from the USA to Japan", "routes/usa-to-japan.html")]), faq_ld])


def build_route_usa_korea(cfg, airlines):
    """USA -> South Korea route page / main Korea guide (preview), from data/routes/usa-korea.json. Every row carries its official source."""
    d = json.loads((ROOT / "data" / "routes" / "usa-korea.json").read_text())
    root, chk, S = "../", d["checked"], d["sources"]
    src = lambda u, t="Official source": f'<a href="{e(u)}" rel="noopener" target="_blank">{t}</a>'
    checked = f'Last checked <time datetime="{chk}">{nice_date(chk)}</time>'

    def agency(k):
        h = S[k].split("/")[2]
        return ("APQA" if h.endswith("qia.go.kr") else "CDC" if h.endswith("cdc.gov") else "USDA APHIS" if h.endswith("aphis.usda.gov")
                else "Incheon Airport" if h.endswith("airport.kr") else "Korail" if h.endswith("korail.com") else "Easy Law (MOLEG)" if h.endswith("easylaw.go.kr") else "Official source")
    chkflag = lambda r: '<span class="flag">Check</span> ' if r.get("check") else ""
    qa = "".join(f"<li><b>{e(q)}:</b> {e(a)} {src(S[k], 'Source')}</li>" for q, a, k in d["quick"])
    rows = "".join(f"<tr><td data-l='Who'>{e(r['who'])}</td><td data-l='Direction'>{e(r['way'])}</td><td data-l='Case'>{e(r['case'])}</td>"
                   f"<td data-l='Rule'>{e(r['rule'])}</td><td class='usa-src' data-l='Source'>{src(S[r['src']], agency(r['src']))}</td></tr>" for r in d["rules"])
    fees = "".join(f"<tr><td data-l='Item'>{e(f['item'])}</td><td data-l='Cost (USD)'>{chkflag(f)}{e(f['amount'])}</td>"
                   f"<td class='usa-src' data-l='Source'>{src(S[f['src']], agency(f['src']))}</td></tr>" for f in d["fees"])
    offs = "".join(f"<tr><td data-l='Airport'><b>{e(o['airport'])}</b></td><td data-l='APQA office'>{e(o['office'])}</td><td data-l='Phone'>{e(o['phone'])}</td>"
                   f"<td class='usa-src' data-l='Source'>{src(S[o['src']], agency(o['src']))}</td></tr>" for o in d["offices"])
    kt = d["transport"]
    tchk = f'<time datetime="{e(kt["checked"])}">{nice_date(kt["checked"])}</time>'
    def tr_card(c):
        trs = "".join(f"<tr><th>{k}</th><td>{e(c[f])}</td></tr>" for k, f in
                      (("Species", "species"), ("Carrier", "carrier"), ("Fee", "fee"), ("Booking", "booking"),
                       ("Rules", "rules"), ("Service dogs", "service"), ("For tourists", "tourist")))
        return (f'<article class="ht-card"><h4>{e(c["mode"])}</h4><p class="ht-sub">{e(c["sub"])}</p><table>{trs}</table>'
                f'<p class="ht-foot"><a href="{e(c["url"])}" rel="noopener" target="_blank">{e(c["link_text"])} &#8599;</a>'
                f' <span class="small">&middot; checked {tchk}</span></p></article>')
    trans = ("".join(f"<p>{e(t)}</p>" for t in kt["intro"])
             + f'<p class="warn usa-warn">Rules checked {tchk} on each operator&rsquo;s official page; confirm with the operator before you travel. Fees in Korean won with approximate US dollars '
             f'({e(kt["usd_rate"])}). &ldquo;Not stated&rdquo; or &ldquo;confirm&rdquo; means the official page doesn&rsquo;t say or we couldn&rsquo;t open it.</p>'
             + f'<div class="kr-ht">{"".join(tr_card(c) for c in kt["cards"])}</div>')
    links = "".join(f"<li>{src(S[k], e(n))}</li>" for n, k in d["links"])
    by = {a["slug"]: a for a in airlines}
    arows = []
    for s in d["airlines"]:
        a = by.get(s)
        if not a:
            continue
        note = (f"<b>Route limits:</b> {e(a.get('banned_routes') or 'none listed.')} "
                f"<b>Hold or cargo:</b> {e(a.get('checked_or_cargo') or CHECK)}")
        arows.append(f"<tr><td data-l='Airline'><a href='{root}airlines/{e(s)}.html'><b>{e(a['name'])}</b></a></td>"
                     f"<td data-l='What our airline page says'>{note}</td>"
                     f"<td data-l='Korea flights'><span class='flag'>Check</span> Confirm the airline flies your route and accepts pets on that flight</td>"
                     f"<td class='usa-src' data-l='Checked'>{src(a['official_url'], 'Airline page')} <span class='small'>checked <time datetime='{e(a.get('last_verified') or '')}'>{nice_date(a.get('last_verified'))}</time></span></td></tr>")
    btns = [f'<a class="btn" href="{e(f["url_template"].strip())}" rel="sponsored nofollow noopener" target="_blank">{e(f["label"])}</a>'
            for f in cfg.get("flight_affiliates") or [] if (f.get("url_template") or "").strip() and f.get("label")]
    fbox = ("" if not btns else
            f'<aside class="reco flights"><h2>Book flights to South Korea</h2>'
            f'<p>Compare fares from the US to Seoul (Incheon) and other Korean airports, then arrange your pet&rsquo;s place directly with the airline before you buy: pet space is limited per flight, and in-cabin and cargo rules differ by airline.</p>'
            f'<p class="buy">{" ".join(btns)}</p>'
            f'<p class="small disc">Affiliate links: we may earn a commission at no extra cost to you. <a href="{root}about.html#affiliates">Disclosure</a>.</p></aside>')
    kh = d["hotels"]
    hchk = f'<time datetime="{e(kh["checked"])}">{nice_date(kh["checked"])}</time>'
    def kr_card(h):
        trs = "".join(f"<tr><th>{k}</th><td>{e(h[f])}</td></tr>" for k, f in
                      (("Species", "species"), ("Weight limit", "weight"), ("Max pets", "pets"), ("Fee", "fee"), ("Conditions", "conditions")))
        return (f'<article class="ht-card"><h4>{e(h["name"])}</h4><p class="ht-sub">{e(h["area"])}</p><table>{trs}</table>'
                f'<p class="ht-foot"><a href="{e(h["url"])}" rel="noopener" target="_blank">Pet policy &amp; booking &#8599;</a></p></article>')
    kr_hotels = (f'<h2 id="hotels">Pet-friendly hotels in South Korea</h2>'
                 + "".join(f"<p>{e(t)}</p>" for t in kh["intro"])
                 + f'<p class="warn usa-warn">Policies checked {hchk}; confirm with the hotel before booking. Fees in Korean won with approximate US dollars '
                 f'({e(kh["usd_rate"])}). Where a card says &ldquo;confirm with hotel&rdquo;, the official page is unclear or sources disagree.</p>'
                 + "".join(f'<h3 id="hotels-{e(c["city"].lower())}">{e(c["city"])}</h3><div class="kr-ht">{"".join(kr_card(h) for h in c["hotels"])}</div>' for c in kh["cities"])
                 + f'<p class="small">Each link goes to the hotel&rsquo;s own pet policy or pet package page. Staying in a US city before or after the flight? See <a href="{root}hotels/">pet-friendly hotel rules by chain</a>.</p>')
    gl = "".join(f"<li><a href='{root}products/{g}.html'>{e(t)}</a></li>" for g, (t, _) in GUIDE_META.items() if g != "dog-road-trip-packing-list")
    css = """<style>
.usa-quick{background:var(--sage-l);border:0;border-left:4px solid var(--sage);border-radius:10px;padding:14px 18px}
.usa-quick h2{margin:0 0 .4em}.usa-quick ul{margin:0;padding-left:1.2em}.usa-quick li{margin:.35em 0}
.usa-warn{border:0;border-left:4px solid var(--gold)}
.usa-t .usa-src{white-space:nowrap}
.rj-air td:nth-child(3){min-width:9em}
.tablewrap+.tablewrap{margin-top:16px}
.kr-ht{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin:.6em 0 1.2em}
.kr-ht .ht-card{border:1px solid var(--line,#d9d4c7);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column}
.kr-ht h4{margin:0 0 .15em;font-size:1.08em}.kr-ht .ht-sub{margin:0 0 .6em;font-size:.9em;opacity:.8}
.kr-ht table{width:100%;border-collapse:collapse;font-size:.92em;margin:0 0 .6em}
.kr-ht th{text-align:left;vertical-align:top;padding:4px 8px 4px 0;width:6.5em;font-weight:600}
.kr-ht .ht-foot .small{font-weight:400;opacity:.8}
.kr-ht td{vertical-align:top;padding:4px 0}.kr-ht tr+tr th,.kr-ht tr+tr td{border-top:1px solid var(--line,#ece8de)}
.kr-ht .ht-foot{margin:auto 0 0;font-size:.92em;font-weight:600}
@media (max-width:720px){.usa-t .usa-src{white-space:normal}}
</style>"""
    body = f"""{css}<nav class="crumbs"><a href="{root}index.html">Home</a> &rsaquo; Routes &rsaquo; USA to South Korea</nav>
<h1>Traveling to South Korea with your dog or cat</h1>
<p class="lead">What your dog or cat needs to fly from the United States to South Korea, how to get around Korea with it, and what you need to bring it back. Korea&rsquo;s import rules come from the Animal and Plant Quarantine Agency (APQA); USDA APHIS endorses the US health certificate. Book the rabies antibody (FAVN) test early: the result has to be on the health certificate.</p>
<div class="usa-quick"><h2 id="quick">Quick answer</h2><ul>{qa}</ul></div>
<p class="warn usa-warn">Rules change. Always confirm with APQA and USDA APHIS before you travel; a missing microchip, test result or endorsement can mean quarantine at your cost, or your pet being sent back. {checked}.</p>
<h2 id="rules">Rules by case</h2>
<p class="small">{checked} on the APQA, USDA APHIS, Incheon Airport and CDC pages linked in each row. Where APQA and APHIS word a rule differently, we follow APQA&rsquo;s page.</p>
<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Who</th><th>Direction</th><th>Case</th><th>Rule</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2 id="fees">Fees</h2>
<p class="small">{checked}. Prices in US dollars where the source gives them. Rows marked <span class="flag">Check</span> have no official amount we could confirm.</p>
<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Item</th><th>Cost</th><th>Source</th></tr></thead><tbody>{fees}</tbody></table></div>
<h2 id="airports">Arrival airports and APQA offices</h2>
<p class="small">{checked}. Phone numbers as listed on APQA&rsquo;s English import page; APQA&rsquo;s <a href="{e(S['qia_contact'])}" rel="noopener" target="_blank">contact page</a> lists all regional offices.</p>
<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Airport</th><th>APQA office</th><th>Phone</th><th>Source</th></tr></thead><tbody>{offs}</tbody></table></div>
<h2 id="airlines">Airlines between the US and Korea</h2>
<p class="small">From our airline pages, checked on the airline&rsquo;s official site on the date shown. Airline rules are separate from Korea&rsquo;s entry rules; confirm in-cabin or cargo acceptance for your exact flight.</p>
<div class="tablewrap"><table class="cmp usa-t rj-air"><thead><tr><th>Airline</th><th>What our airline page says</th><th>Korea flights</th><th>Source</th></tr></thead><tbody>{''.join(arows)}</tbody></table></div>
{fbox}
{insurance_teaser(root, "korea")}
<h2 id="getting-around">Getting around South Korea with your pet</h2>
{trans}
{kr_hotels}
<h2 id="return">Coming back to the USA</h2>
<p>South Korea is not on the CDC list of high-risk countries for dog rabies (North Korea is), so a dog that was only in South Korea (or other low-risk countries) in the 6 months before returning needs the free <b>CDC Dog Import Form</b> receipt, a microchip, a healthy look and an age of at least 6 months. Cats have no federal rabies proof requirement. State and airline rules still apply. {src(S['cdc_low'], 'CDC')} &middot; {src(S['cdc_high'], 'CDC high-risk list')}</p>
<p>Full US entry and state rules: <a href="{root}countries/usa.html">Pet travel rules for the USA</a>.</p>
<h2 id="official">Official links</h2>
<ul>{links}</ul>
<p class="note small">{checked}. Rules change; confirm with the official source before you travel. This page is a summary, not legal or veterinary advice. Airlines may require more than Korea does.</p>
<h2 id="gear">Product guides</h2>
<ul>{gl}</ul>"""
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": qn, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for qn, (_, a, _k) in zip(["What does a dog or cat need to travel from the US to South Korea?",
                                   "Who endorses the US health certificate for a pet going to South Korea?",
                                   "What are the rules for puppies and kittens under 90 days going to South Korea?",
                                   "Do I need to notify Korea's quarantine agency before I arrive with my pet?",
                                   "What happens if my pet doesn't meet South Korea's requirements?",
                                   "What does a dog need to return to the US from South Korea?"], d["quick"])]}
    return page(cfg, f"Traveling to South Korea with your dog or cat: USA to Korea rules | {cfg['site_name']}",
               "What a dog or cat needs to travel from the US to South Korea: ISO microchip, rabies vaccination, FAVN antibody test, USDA APHIS-endorsed health certificate, Incheon arrival, getting around Korea and coming back, with official sources.",
               body, "routes/usa-to-south-korea.html", root,
               jsonld=[bc_ld(cfg, [("Home", ""), ("Traveling to South Korea with your dog or cat", "routes/usa-to-south-korea.html")]), faq_ld])


HOTELS_CSS = """<style>
.usa-quick{background:var(--sage-l);border:0;border-left:4px solid var(--sage);border-radius:10px;padding:14px 18px}
.usa-quick h2{margin:0 0 .4em}.usa-quick ul{margin:0;padding-left:1.2em}.usa-quick li{margin:.35em 0}
.usa-warn{border:0;border-left:4px solid var(--gold)}
.ht-warn{font-size:1.02em;padding:14px 18px}.ht-warn b{display:block;margin-bottom:.2em}
.usa-t .usa-src{white-space:nowrap}
.ht-t td:first-child{min-width:9em}
.ht-ph{border:2px dashed var(--gold);border-radius:10px;padding:12px 16px;margin:.6em 0;font-size:.95em}
.ht-ph code{word-break:break-all;font-size:.85em}
.ht-cities{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin:1em 0}
.ht-cities a{display:block;border:1px solid var(--line,#d9d4c7);border-radius:12px;padding:14px 16px;text-decoration:none}
.ht-cities a b{display:block;font-size:1.1em;margin-bottom:.2em}
.ht-lux{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin:1em 0}
.ht-card{border:1px solid var(--line,#d9d4c7);border-radius:12px;padding:14px 16px;display:flex;flex-direction:column}
.ht-card h3{margin:0 0 .15em;font-size:1.12em}.ht-card .ht-sub{margin:0 0 .6em;font-size:.9em;opacity:.8}
.ht-card table{width:100%;border-collapse:collapse;font-size:.93em;margin:0 0 .6em}
.ht-card th{text-align:left;vertical-align:top;padding:4px 8px 4px 0;width:7.5em;font-weight:600}
.ht-card td{vertical-align:top;padding:4px 0}.ht-card tr+tr th,.ht-card tr+tr td{border-top:1px solid var(--line,#ece8de)}
.ht-card .ht-note{font-size:.9em;border-left:3px solid var(--gold);padding:4px 10px;margin:0 0 .6em}
.ht-card .ht-foot{margin-top:auto;display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;font-size:.9em}
.ht-card .btn{margin:0}
.ht-no{font-size:.95em}
@media (max-width:720px){.usa-t .usa-src{white-space:normal}}
</style>"""


def hotels_data():
    ch = json.loads((ROOT / "data" / "hotels" / "us-chains.json").read_text())
    ci = json.loads((ROOT / "data" / "hotels" / "us-cities.json").read_text())
    return ch, ci


def hotel_chain_table(ch, root):
    """Brand-level pet rules, one row per chain; null -> 'Varies by hotel', check -> 'Check' flag."""
    src = lambda u, t: f'<a href="{e(u)}" rel="noopener" target="_blank">{t}</a>'
    va = '<span class="na">Not stated: varies by hotel</span>'
    rows = []
    for c in ch["chains"]:
        flag = '<span class="flag">Check</span> ' if c.get("check") else ""
        cell = lambda k: e(c[k]) if c.get(k) else va
        s2 = f' &middot; {src(c["source2"], "more")}' if c.get("source2") else ""
        rows.append(f"<tr><td data-l='Chain'><b>{e(c['brand'])}</b></td><td data-l='Pet fee (USD)'>{flag}{cell('fee')}</td>"
                    f"<td data-l='Max weight (lb)'>{cell('weight')}</td><td data-l='Max pets'>{cell('pets')}</td>"
                    f"<td data-l='Notes'>{e(c['notes'])}</td><td class='usa-src' data-l='Source'>{src(c['source'], 'Official page')}{s2}</td></tr>")
    return ("<div class='tablewrap'><table class='cmp usa-t ht-t'><thead><tr><th>Chain</th><th>Pet fee (USD)</th><th>Max weight (lb)</th>"
            "<th>Max pets per room</th><th>Notes</th><th>Source</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")


def hotel_warn(chk):
    return (f'<p class="warn usa-warn ht-warn"><b>Policies change: confirm with the hotel.</b> Pet fees, weight limits and the number of pets '
            f'are set by each brand and often by each hotel, and can change without notice. We read every chain&rsquo;s official page on '
            f'<time datetime="{chk}">{nice_date(chk)}</time>. Call or message the hotel to confirm before you book, and declare your pet at check-in.</p>')


def hotel_aff_url(cfg, c):
    """(expedia config, tracked city URL or "") from config.json hotel_affiliates.expedia.links[slug]."""
    ex = (cfg.get("hotel_affiliates") or {}).get("expedia") or {}
    return ex, ((ex.get("links") or {}).get(c["slug"]) or "").strip()


def hotel_aff_box(cfg, c):
    """Expedia box for one city. Tracked URL comes from config.json hotel_affiliates.expedia.links[slug] (dashboard-generated);
    empty -> clearly marked placeholder (never a guessed tracking URL)."""
    ex, url = hotel_aff_url(cfg, c)
    disc = ('<p class="small disc">Affiliate disclosure: this is an affiliate link. If you book through it we may earn a commission at no extra cost to you. '
            'It never changes the pet rules we publish. <a href="{root}about.html#affiliates">Disclosure</a>.</p>')
    head = (f'<aside class="reco flights" id="book"><h2>Find a pet-friendly hotel in {e(c["name"])}</h2>'
            f'<p>Search hotels in {e(c["short"])} with the pet-friendly filter on, then check the hotel&rsquo;s own pet policy (fee, weight, number of pets) before you pay.</p>')
    if url:
        return head + f'<p class="buy"><a class="btn" href="{e(url)}" rel="sponsored nofollow noopener" target="_blank">{e(ex.get("label") or "See pet-friendly hotels on Expedia")}</a></p>' + disc + "</aside>"
    # No tracked link yet: plain Expedia search with the pet-friendly filter (untracked; swapped for a tracked link later).
    print(f"  NOTE: hotels/{c['slug']}: no tracked Expedia link yet -> plain expedia_target link")
    return head + f'<p class="buy"><a class="btn" href="{e(c["expedia_target"])}" rel="nofollow noopener" target="_blank">{e(ex.get("label") or "See pet-friendly hotels on Expedia")}</a></p>' + "</aside>"


def hotel_city_links(ci, root, skip=None):
    return "".join(f'<a href="{root}hotels/pet-friendly-hotels-{e(x["slug"])}.html"><b>{e(x["name"])}</b>Pet-friendly hotel rules and local tips</a>'
                   for x in ci["cities"] if x["slug"] != skip)


def hotel_lux_link(cfg, h):
    """Booking button for one luxury hotel. Tracked URL from config.json hotel_affiliates.expedia.hotel_links[id]
    (made in the Expedia Creator dashboard); empty -> plain untracked link to expedia_target (never a placeholder)."""
    ex = (cfg.get("hotel_affiliates") or {}).get("expedia") or {}
    url = ((ex.get("hotel_links") or {}).get(h["id"]) or "").strip()
    label = "Check rates on Expedia" if h.get("expedia_is_property") else "Search this hotel on Expedia"
    if url:
        return f'<a class="btn" href="{e(url)}" rel="sponsored nofollow noopener" target="_blank">{label}</a>', True
    print(f"  NOTE: luxury {h['id']}: no tracked Expedia link yet -> plain expedia_target link")
    return f'<a class="btn" href="{e(h["expedia_target"])}" rel="nofollow noopener" target="_blank">{label}</a>', False


def hotel_lux_section(cfg, c):
    lux = c.get("luxury") or []
    if not lux:
        return ""
    src = lambda u, t: f'<a href="{e(u)}" rel="noopener" target="_blank">{t}</a>'
    na = '<span class="na">Not stated on the official page</span>'
    chk_flag = '<span class="flag">Check</span> '
    cards, tracked = [], False
    for h in lux:
        flag = chk_flag if h.get("check") else ""
        rows = [("Pet fee", h.get("fee")), ("Deposit", h.get("deposit")), ("Max weight", h.get("weight")),
                ("Pets", h.get("pets")), ("Species", h.get("species")), ("Amenities", h.get("amenities")),
                ("Rules", h.get("restrictions"))]
        trs = []
        for k, v in rows:
            if k == "Deposit" and not v:
                continue  # only shown when the hotel names one
            if k in ("Amenities", "Rules") and not v:
                continue
            trs.append(f"<tr><th>{k}</th><td>{(flag if k == 'Pet fee' else '')}{e(v) if v else na}</td></tr>")
        note = f'<p class="ht-note">{e(h["note"])}</p>' if h.get("note") else ""
        btn, t = hotel_lux_link(cfg, h)
        tracked = tracked or t
        s2 = f' &middot; {src(h["source2"], "more")}' if h.get("source2") else ""
        cards.append(f'<article class="ht-card" id="{e(h["id"])}"><h3>{e(h["name"])}</h3>'
                     f'<p class="ht-sub">{e(h["brand"])} &middot; {e(h["area"])}</p>'
                     f'<table>{"".join(trs)}</table>{note}'
                     f'<p class="ht-foot">{btn}<span>{src(h["source"], "Hotel pet policy")}{s2} &middot; checked <time datetime="{e(h["checked"])}">{nice_date(h["checked"])}</time></span></p></article>')
    no = "".join(f'<li><b>{e(x["name"])}:</b> {e(x["text"])} {src(x["source"], "Official page")}</li>' for x in c.get("luxury_not") or [])
    no = f'<p class="ht-no"><b>Not pet-friendly:</b></p><ul class="ht-no">{no}</ul>' if no else ""
    disc = ('<p class="small disc">Affiliate disclosure: some booking buttons are affiliate links. If you book through them we may earn a commission at no extra cost to you. '
            'It never changes the pet rules we publish. <a href="{root}about.html#affiliates">Disclosure</a>.</p>') if tracked else ""
    return (f'<h2 id="luxury">Luxury pet-friendly hotels in {e(c["name"])}</h2>'
            f'<p>Luxury hotels set their own pet rules, so we read each hotel&rsquo;s official pet policy rather than the brand&rsquo;s. Fees in US dollars, weights in pounds. '
            f'<span class="flag">Check</span> means the official page leaves something unclear or another source disagrees: call the hotel before you book. '
            f'</p>'
            f'<div class="ht-lux">{"".join(cards)}</div>{no}{disc}')


def hotel_lux_brands(ci):
    src = lambda u: f'<a href="{e(u)}" rel="noopener" target="_blank">Official page</a>'
    rows = "".join(f"<tr><td data-l='Brand'><b>{e(b['brand'])}</b></td><td data-l='Pet rules'>{e(b['text'])}</td><td class='usa-src' data-l='Source'>{src(b['source'])}</td></tr>"
                   for b in ci.get("luxury_brands") or [])
    return ("<div class='tablewrap'><table class='cmp usa-t ht-t'><thead><tr><th>Brand</th><th>Pet rules</th><th>Source</th></tr></thead><tbody>"
            + rows + "</tbody></table></div>")


def hotel_lux_faq(c):
    ok = [h for h in c.get("luxury") or [] if not h.get("check") and (h.get("fee") or h.get("weight"))]
    if not ok:
        return None
    parts = []
    for h in ok:
        bits = [x for x in (h.get("fee") and f"pet fee {h['fee']}", h.get("weight") and f"max {h['weight']}", h.get("pets") and f"{h['pets']} pets") if x]
        parts.append(f"{h['name']} ({', '.join(bits)})")
    return (f"Which luxury hotels in {c['name']} accept pets?",
            "From each hotel's official pet policy: " + "; ".join(parts) + ". Confirm with the hotel before you book.")


def build_hotel_city(cfg, c, ch, ci):
    root, chk, S = "../", ci["checked"], ci["sources"]
    path = f"hotels/pet-friendly-hotels-{c['slug']}.html"
    src = lambda u, t="Source": f'<a href="{e(u)}" rel="noopener" target="_blank">{t}</a>'
    by = {x["brand"].split(" (")[0].split(" /")[0]: x for x in ch["chains"]}
    quick = [
        ("No pet fee", f"Kimpton charges no pet fee and sets no size, weight or number limit; Motel 6 lets up to 2 dogs or cats stay free (150 lb combined).", by["Kimpton"]["source"]),
        ("Budget chains", "Red Roof: first pet free, second $15 per night, 80 lb per pet. La Quinta: optional fee up to $25 per night, max $75 per stay, 2 pets.", by["Red Roof Inn"]["source"]),
        ("Higher fees", "Drury charges a daily pet fee of at least $50 (varies by hotel), 2 pets, 80 lb combined.", by["Drury Hotels"]["source"]),
        ("Hilton, Aloft, Four Seasons, Loews", "Their official pages give no single brand-wide pet fee or weight limit (Loews allows 2 pets): each hotel sets its own rules, so check the hotel page.", by["Hilton brands"]["source"]),
        (c["quick_city"][0], c["quick_city"][1], S[c["quick_city"][2]]),
    ]
    qa = "".join(f"<li><b>{e(q)}:</b> {e(a)} {src(u)}</li>" for q, a, u in quick)
    secs = []
    for s in c["sections"]:
        items = []
        for it in s["items"]:
            t, k = (it, None) if isinstance(it, str) else it
            items.append(f"<li>{e(t)}{' ' + src(S[k]) if k else ''}</li>")
        intro = f"<p>{e(s['intro'])} {src(S[s['src']], 'Official source')}</p>" if s["intro"] else ""
        if not s["intro"] and all(not isinstance(i, str) for i in s["items"]):
            intro = ""
        elif not s["intro"]:
            intro = f"<p class='small'>{src(S[s['src']], 'Official source')}</p>"
        secs.append(f"<h2 id='{e(s['id'])}'>{e(s['h'])}</h2>{intro}" + (f"<ul>{''.join(items)}</ul>" if items else ""))
    checked = f'Last checked <time datetime="{chk}">{nice_date(chk)}</time>'
    body = f"""{HOTELS_CSS}<nav class="crumbs"><a href="{root}index.html">Home</a> &rsaquo; <a href="{root}hotels/">Pet-friendly hotels</a> &rsaquo; {e(c['name'])}</nav>
<h1>Pet-friendly hotels in {e(c['name'])}: chain and luxury hotel pet fees, weight limits and local tips</h1>
<p class="lead">{e(c['lead'])}</p>
{hotel_warn(chk)}
<div class="usa-quick"><h2 id="quick">Quick answer</h2><ul>{qa}</ul></div>
{hotel_aff_box(cfg, c)}
<h2 id="chains">Hotel chain pet rules (US, brand-wide)</h2>
<p class="small">{checked} on each chain&rsquo;s official website. Fees in US dollars, weights in pounds. Brand rules are a starting point: a franchised hotel in {e(c['name'])} can differ. Rows marked <span class="flag">Check</span> could not be read on the official site.</p>
{hotel_chain_table(ch, root)}
{hotel_lux_section(cfg, c)}
{''.join(secs)}
<h2 id="tips">Before you book</h2>
<ul><li>Filter for pet-friendly, then open the hotel&rsquo;s own policy: fee per night or per stay, weight limit, number of pets, and whether cats are accepted.</li>
<li>Ask whether your pet may stay alone in the room: Motel 6 and Drury say pets should not be left alone.</li>
<li>Service animals are not pets. Ask the hotel how it handles service animals and emotional support animals rather than assuming a pet fee or limit applies.</li></ul>
<p class="note small">{checked}. Hotel pet policies change and vary by property; confirm with the hotel before you book. This page is a summary, not legal or veterinary advice. We are not affiliated with any hotel chain.</p>
<h2 id="more">More pet travel help</h2>
<p>Flying there? Check the airline: <a href="{root}airlines/american.html">American</a>, <a href="{root}airlines/delta.html">Delta</a>, <a href="{root}airlines/united.html">United</a>, <a href="{root}airlines/southwest.html">Southwest</a>, <a href="{root}airlines/jetblue.html">JetBlue</a>. State entry rules: <a href="{root}countries/usa.html#states">Pet travel rules for the USA</a>.</p>
<div class="ht-cities">{hotel_city_links(ci, root, c['slug'])}</div>"""
    faqs = [("Which hotel chains have no pet fee?", quick[0][1]), ("What do Red Roof and La Quinta charge for pets?", quick[1][1])] + [(q, a) for q, a, _ in c["faq"]]
    lf = hotel_lux_faq(c)
    if lf:
        faqs.append(lf)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    return page(cfg, f"Pet-friendly hotels in {c['name']}: chain pet fees and weight limits | {cfg['site_name']}",
                f"Pet fees, weight limits and pet numbers at chains and at {len(c.get('luxury') or [])} luxury hotels in {c['name']}, each from its official pet policy, plus airport pet relief areas and dog parks.",
                body, path, root,
                jsonld=[bc_ld(cfg, [("Home", ""), ("Pet-friendly hotels", "hotels/"), (f"Pet-friendly hotels in {c['name']}", path)]), faq_ld])


def build_hotels_index(cfg, ch, ci):
    root, chk = "../", ci["checked"]
    body = f"""{HOTELS_CSS}<nav class="crumbs"><a href="{root}index.html">Home</a> &rsaquo; Pet-friendly hotels</nav>
<h1>Pet-friendly hotels in the US: chain pet fees, weight limits and city guides</h1>
<p class="lead">What the big US hotel chains charge for a dog or cat, how heavy a pet they accept and how many per room, read on each chain&rsquo;s official site. Then pick a city for local tips on airport pet relief areas and dog parks.</p>
{hotel_warn(chk)}
<h2 id="cities">City guides</h2>
<div class="ht-cities">{hotel_city_links(ci, root)}</div>
<h2 id="chains">Hotel chain pet rules (US, brand-wide)</h2>
<p class="small">Last checked <time datetime="{chk}">{nice_date(chk)}</time> on each chain&rsquo;s official website. Fees in US dollars, weights in pounds. Rows marked <span class="flag">Check</span> could not be read on the official site.</p>
{hotel_chain_table(ch, root)}
<h2 id="luxury">Luxury hotel brands: pet rules are set per hotel</h2>
<p>At luxury brands there is rarely one brand-wide pet policy: fees, weight limits and even whether pets are allowed change from hotel to hotel. Each city guide lists luxury hotels with their own published pet rules (checked <time datetime="{chk}">{nice_date(chk)}</time>) and a booking link.</p>
{hotel_lux_brands(ci)}
<p class="small disc">City pages may contain affiliate links; if you book through them we may earn a commission at no extra cost to you. It never changes the pet rules we publish. <a href="{root}about.html#affiliates">Disclosure</a>.</p>
<p>Driving or flying between states? See <a href="{root}countries/usa.html">pet travel rules for the USA</a> for each state&rsquo;s health certificate and rabies rules.</p>"""
    return page(cfg, f"Pet-friendly hotels in the US: chain pet fees and weight limits | {cfg['site_name']}",
                "Pet fees, weight limits and number of pets at Kimpton, Motel 6, Red Roof, La Quinta, Drury, Loews, Hilton, Aloft and Four Seasons, from official sites, plus city guides for Orlando, New York and Miami.",
                body, "hotels/", root, jsonld=[bc_ld(cfg, [("Home", ""), ("Pet-friendly hotels", "hotels/")])])



INS_SLUG = "insurance/pet-insurance-for-travelers.html"
INS_NOT_AGENT = ("PetPolicyCheck is not a licensed insurance agent or broker and does not sell, solicit or negotiate insurance. "
                 "We provide general information only, not insurance advice. Coverage, availability and prices vary by state and are set by the insurer. "
                 "Always read the policy documents and confirm details with the insurer.")


def load_insurers():
    return json.loads((ROOT / "data" / "insurance" / "us-pet-insurers.json").read_text())


def ins_affiliate_url(cfg, key):
    """config.json insurance_affiliates.<key>.url; empty until a program accepts the site (then the page shows a sponsored quote link)."""
    v = (cfg.get("insurance_affiliates") or {}).get(key) or {}
    return (v.get("url") or "").strip(), v.get("label") or ""


def ins_disclosure(cfg, root):
    live = any(ins_affiliate_url(cfg, k)[0] for k in (cfg.get("insurance_affiliates") or {}) if not k.startswith("_"))
    ftc = ("<b>Disclosure:</b> PetPolicyCheck may earn a fee if you request a quote or buy a policy through links marked &ldquo;sponsored&rdquo; on this page. "
           "This doesn&rsquo;t change what you pay or how we describe products." if live else
           "<b>Disclosure:</b> we have no affiliate relationship with any insurer on this page today, and every link goes to the insurer&rsquo;s own site. "
           "If that changes, quote links will be marked &ldquo;sponsored&rdquo;; PetPolicyCheck may then earn a fee if you request a quote or buy a policy through them. "
           "That won&rsquo;t change what you pay or how we describe products.")
    return (f'<div class="note ins-disc"><p>{ftc} <a href="{root}about.html#affiliates">Affiliate disclosure</a>.</p>'
            f'<p><b>Not advice:</b> {e(INS_NOT_AGENT)}</p></div>')


def insurance_teaser(root, where):
    """Small linked block for /countries/usa.html ('usa'), /routes/usa-to-japan.html ('japan') and /routes/usa-to-south-korea.html ('korea'), counts taken from the insurer data."""
    d = load_insurers()
    ins = d["insurers"]
    abroad = [i["name"] for i in ins if i["abroad"] == "yes"]
    url = f"{root}{INS_SLUG}"
    chk = f'<time datetime="{d["checked"]}">{nice_date(d["checked"])}</time>'
    if where == "japan":
        h = "Will your US pet insurance work in Japan?"
        p = (f"Often not. Of the {len(ins)} US insurers we checked, most limit coverage to the US and Canada (some add US territories or military bases); "
             f"only {' and '.join(abroad)} say they cover vet care abroad, and terms apply. Policies reimburse you after you pay the vet, so keep itemized invoices and records.")
    elif where == "korea":
        h = "Will your US pet insurance work in South Korea?"
        p = (f"Often not. Of the {len(ins)} US insurers we checked, most limit coverage to the US and Canada (some add US territories or military bases); "
             f"only {' and '.join(abroad)} say they cover vet care abroad, and terms apply. Policies reimburse you after you pay the vet, so keep itemized invoices and records.")
    else:
        h = "Pet insurance while traveling in the US"
        p = (f"Most US pet insurance policies reimburse care at any licensed vet in the US, and many also in Canada, so an emergency vet on a road trip can be covered. "
             f"Waiting periods (up to 30 days for illnesses among the {len(ins)} insurers we checked) mean a policy bought just before a trip may not cover it yet.")
    return (f'<aside class="reco ins-tease"><h2>{h}</h2><p>{p}</p>'
            f'<p><a href="{url}"><b>Compare what {len(ins)} US insurers say about travel coverage</b></a> &rsaquo;</p>'
            f'<p class="small disc">Checked on insurers&rsquo; official sites {chk}. General information, not insurance advice; PetPolicyCheck is not a licensed insurance agent.</p></aside>')


def build_insurance_travel(cfg):
    """Pet Insurance for Travelers (US), from data/insurance/us-pet-insurers.json. Facts only from insurers' own sites; 'Check' where unverified."""
    d = load_insurers()
    root, chk, ins = "../", d["checked"], d["insurers"]
    src = lambda u, t="Official source": f'<a href="{e(u)}" rel="noopener" target="_blank">{t}</a>'
    checked = f'Last checked <time datetime="{chk}">{nice_date(chk)}</time>'
    CHK = '<span class="flag">Check</span>'

    def cell(i, k):
        v = i[k]
        if v.strip() == "Check":
            return f"{CHK} Confirm with the insurer"
        v = re.sub(r"\bCheck\b\.?", CHK, e(v))
        return (CHK + " " + v) if k in i["check"] and CHK not in v else v

    abroad_lbl = {"yes": "<b>Yes</b>, per insurer (terms apply)", "no": "No", "check": f"{CHK} Not stated"}
    rows = []
    for i in ins:
        aurl, alabel = ins_affiliate_url(cfg, i["key"])
        link = (f'<a class="btn" href="{e(aurl)}" rel="sponsored nofollow noopener" target="_blank">{e(alabel)}</a> <span class="small">sponsored</span>' if aurl
                else src(i["official_url"], "Official site"))
        srcs = "<br>".join(src(u, e(t)) for t, u in i["sources"])
        extra = f"<br><span class='small'>{e(i['extra'])}</span>" if i.get("extra") else ""
        rows.append(f"<tr><td data-l='Insurer'><b>{e(i['name'])}</b><br>{link}</td>"
                    f"<td data-l='Outside US &amp; Canada?' style='min-height:2.6rem'>{abroad_lbl[i['abroad']]}</td>"
                    f"<td data-l='Where covered'>{cell(i, 'territory')}{extra}</td>"
                    f"<td data-l='Waiting periods'>{cell(i, 'waiting')}</td>"
                    f"<td data-l='Age limits'>{cell(i, 'age')}</td>"
                    f"<td data-l='Reimbursement'>{cell(i, 'reimb')}</td>"
                    f"<td class='ins-src' data-l='Sources'>{srcs}<br><span class='small'>checked <time datetime='{chk}'>{nice_date(chk)}</time></span></td></tr>")
    n = len(ins)
    yes = [i["name"] for i in ins if i["abroad"] == "yes"]
    us_only = [i["name"] for i in ins if "outside the US is not covered" in i["territory"]]
    nchk = sum(1 for i in ins if i["check"])
    css = """<style>
.usa-quick{background:var(--sage-l);border:0;border-left:4px solid var(--sage);border-radius:10px;padding:14px 18px}
.usa-quick h2{margin:0 0 .4em}.usa-quick ul{margin:0;padding-left:1.2em}.usa-quick li{margin:.35em 0}
.usa-warn{border:0;border-left:4px solid var(--gold)}
.ins-disc p{margin:.3em 0}
.ins-t td{vertical-align:top}.ins-t td:first-child{min-width:8.5em}.ins-t td:nth-child(3),.ins-t td:nth-child(4){min-width:13em}
.ins-t .ins-src{min-width:11em;font-size:.86rem}
.ins-t .btn{margin-top:6px}
@media (max-width:720px){.ins-t td{min-width:0!important}}
</style>"""
    body = f"""{css}<nav class="crumbs"><a href="{root}index.html">Home</a> &rsaquo; Insurance &rsaquo; Pet insurance for travelers</nav>
<h1>Pet insurance for travelers (US): what policies cover away from home</h1>
<p class="lead">If your dog or cat gets sick or hurt on a trip, will your US pet insurance pay? It depends on where you are, how long you&rsquo;ve had the policy and what it excludes. Below: what to check, and what {n} US insurers say on their own websites about travel coverage, waiting periods, age limits and reimbursement.</p>
{ins_disclosure(cfg, root)}
<div class="usa-quick"><h2 id="quick">Quick answer</h2><ul>
<li><b>US and Canada:</b> most policies we checked reimburse care at any licensed vet in the US, and most also in Canada (some only during a temporary stay). {(' and '.join(us_only) + ' covers the US only.') if us_only else ''}</li>
<li><b>Outside the US and Canada:</b> only {' and '.join(yes)} say their policies cover vet care abroad. The rest limit cover to the US (and usually Canada), sometimes adding US territories or military bases, or their sites don&rsquo;t say (marked &ldquo;Check&rdquo; in the table).</li>
<li><b>Waiting periods:</b> illness cover usually starts only after a waiting period of up to 30 days (14 or 15 days at most insurers we checked), so a policy bought the week before a trip may not cover that trip.</li>
<li><b>Pre-existing conditions</b> are generally not covered, and that includes anything that first shows up during a waiting period.</li>
<li><b>You pay first:</b> pet insurance usually reimburses you after you pay the vet, so budget for the full bill on the road.</li>
</ul></div>
<p class="warn usa-warn">Policies differ by state, product and underwriting company, and insurers change their terms. Confirm every detail with the insurer before you buy or travel. {checked}.</p>
<h2 id="why">Why insurance matters when you travel with a pet</h2>
<p>Trips bring new risks: heat, unfamiliar food and water, other animals, car and airport stress. If your pet needs an emergency vet away from home, you usually don&rsquo;t know the clinic, you normally pay the bill yourself first, and it can be large. Abroad, it may come in another currency and language.</p>
<p>Pet insurance doesn&rsquo;t change what the vet charges, but it can pay back part of a covered bill afterwards. Separate travel insurance for people usually doesn&rsquo;t cover pets (Trupanion notes this on its travel FAQ), so check your pet&rsquo;s policy before you go.</p>
<h2 id="where">Where coverage applies: US only, US and Canada, or abroad</h2>
<ul>
<li><b>US only:</b> {', '.join(us_only) or 'none in our table'}. Care in Canada or abroad is not covered.</li>
<li><b>US and Canada:</b> most insurers below. Some limit Canada to a temporary stay (Healthy Paws: &ldquo;temporarily traveling&rdquo;; Odie&rsquo;s sample policy: 90 days or less). Trupanion and Pets Best also name US territories and US military bases abroad.</li>
<li><b>Abroad:</b> {' and '.join(yes)} say coverage applies outside the US and Canada. Embrace says up to 6 consecutive months per trip; Nationwide says any licensed vet anywhere. Confirm the exact policy wording before an international trip.</li>
</ul>
<h2 id="waiting">Waiting periods and pre-existing conditions</h2>
<p>A waiting period is the time after the policy starts before claims are paid. Anything that starts during it is usually treated as pre-existing and never covered. Among the insurers below, accident waiting periods range from none to 15 days, and illness waiting periods from 14 days or less to 30 days. Orthopedic or knee (cruciate ligament) conditions can wait up to 6 months, or 12 months for hip dysplasia at Healthy Paws. Some insurers shorten these after a vet exam. If you&rsquo;re planning a trip, compare start dates early.</p>
<p>Pre-existing conditions are excluded. Some insurers will cover a curable condition again once it has been cured and symptom-free for a set time (Spot: 180 days; Lemonade, in most states: 12 months), but not knee or ligament conditions.</p>
<h2 id="compare">What {n} US pet insurers say about travel coverage</h2>
<p class="small">{checked}, on each insurer&rsquo;s own website or sample policy (linked in each row). Facts only, no prices and no rankings. Cells marked {CHK} could not be confirmed, or the insurer&rsquo;s pages disagree or vary by state or carrier ({nchk} of {n} insurers have at least one). Your actual policy decides.</p>
<div class="tablewrap"><table class="cmp ins-t"><thead><tr><th>Insurer</th><th>Covers care outside the US and Canada?</th><th>Where covered</th><th>Waiting periods</th><th>Age limits</th><th>Reimbursement options</th><th>Sources</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p class="note small">Confirm with the insurer: this table summarizes the insurers&rsquo; public pages as read on <time datetime="{chk}">{nice_date(chk)}</time>. Terms vary by state and can change at any time, and the policy document always decides. Found something out of date? <a href="{root}contact.html">Tell us</a>.</p>
<h2 id="before">Before you travel: a short checklist</h2>
<ul>
<li>Read the <b>territory</b> clause in your policy (often called &ldquo;Territory&rdquo; or &ldquo;Treatment locations&rdquo;) for every country on your route.</li>
<li>Check that your <b>waiting periods</b> will be over before you leave.</li>
<li>Save your policy number and the insurer&rsquo;s claims phone number or app on your phone.</li>
<li>Carry your pet&rsquo;s medical and vaccination records. Insurers usually ask for them with a claim.</li>
<li>Keep <b>itemized invoices</b> and payment receipts from any vet you visit; abroad, ask for an English version if possible.</li>
<li>Look up an emergency vet near where you&rsquo;ll stay.</li>
</ul>
<h2 id="related">Related pages</h2>
<ul><li><a href="{root}countries/usa.html">Pet travel rules for the USA: federal and state requirements</a></li>
<li><a href="{root}routes/usa-to-japan.html">Flying with a dog or cat from the USA to Japan</a></li>
<li><a href="{root}routes/usa-to-south-korea.html">Traveling to South Korea with your dog or cat</a></li></ul>
<p class="note small">{checked}. {e(INS_NOT_AGENT)} Prices are set by insurers in US dollars and are not shown here.</p>"""
    return page(cfg, f"Pet insurance for travelers (US): coverage away from home compared | {cfg['site_name']}",
                f"Does US pet insurance cover your dog or cat while traveling? Where {n} US insurers cover care (US, Canada, abroad), plus waiting periods, age limits and reimbursement, from their official sites.",
                body, INS_SLUG, root,
                jsonld=[bc_ld(cfg, [("Home", ""), ("Pet insurance for travelers (US)", INS_SLUG)])])


BOOK_PAGE_CSS = """<style>
.bk-lead{max-width:70ch;color:var(--mut)}
.bk-jump{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 8px;padding:0;list-style:none}
.bk-jump a{display:inline-flex;align-items:center;gap:6px;padding:9px 16px;border-radius:99px;border:1px solid var(--line2);background:var(--chip);color:var(--head);text-decoration:none;font-weight:600;font-size:.9rem}
.bk-jump a:hover,.bk-jump a:focus-visible{border-color:var(--acc);color:var(--acc)}
.bk-sec{margin:22px 0;padding:20px 22px 16px;border:1px solid var(--line);border-top:3px solid var(--acc);border-radius:var(--r-m);background:var(--paper);scroll-margin-top:90px}
.bk-sec>h2{font-size:1.55rem;margin:0 0 6px}
.bk-sec>p{max-width:75ch}
.bk-sec h3{font-size:1.15rem;margin:0 0 6px}
.bk-k{display:block;font:700 .72rem var(--text);letter-spacing:.14em;text-transform:uppercase;color:var(--acc);margin:0 0 4px}
.bk-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:12px 0;align-items:start}
.bk-grid.two{grid-template-columns:repeat(2,minmax(0,1fr))}
.bk-card{border:1px solid var(--line2);border-radius:var(--r-m);padding:14px 16px;background:var(--chip);display:flex;flex-direction:column;gap:8px}
.bk-card p{margin:0;font-size:.92rem}
.bk-card .btn{justify-content:center;text-align:center;white-space:normal}
.bk-card ul{margin:0;padding-left:1.1em;font-size:.92rem}.bk-card ul.book-cities{padding:0}
.bk-sec .book-disc{font-size:.8rem;color:var(--mut);line-height:1.45;margin:8px 0 0}.bk-card li{margin:3px 0}
.bk-card .book-disc{margin-top:auto}
.bk-links{margin:8px 0 0;padding-left:1.1em}.bk-links li{margin:5px 0}
.bk-tools{list-style:none;margin:10px 0;padding:0;display:grid;gap:10px}
.bk-tools li{border-left:3px solid var(--acc);padding:6px 12px;background:var(--chip);border-radius:0 var(--r-s) var(--r-s) 0;font-size:.92rem}
.bk-tools a{font-weight:600}
.bk-empty{border:1px dashed var(--line2);border-radius:var(--r-m);padding:12px 14px;background:var(--bg)}
.bk-sec a{overflow-wrap:anywhere}
.bk-ride dl{margin:0;display:grid;grid-template-columns:max-content 1fr;gap:6px 12px;font-size:.9rem}
.bk-ride dt{font-weight:700;color:var(--head)}.bk-ride dd{margin:0}
.bk-disc{font-size:.82rem;color:var(--mut)}
@media (max-width:900px){.bk-grid{grid-template-columns:1fr}}
@media (max-width:720px){.bk-grid.two{grid-template-columns:1fr}.bk-ride dl{grid-template-columns:1fr;gap:2px}.bk-ride dt{margin-top:6px}.bk-sec{padding:16px 14px 12px}.bk-sec>h2{font-size:1.3rem}.bk-jump a{padding:8px 13px;font-size:.86rem}}
</style>"""


def build_book(cfg, airlines):
    """/book/: one page for every booking a pet trip needs (flights, hotels, airport rides, vets, insurance).
    Everything comes from existing data: config.json flight_affiliates / hotel_affiliates, data/hotels/us-cities.json,
    data/rideshare/us.json, data/partner_vets.json (clinics only once they accepted; official tools meanwhile)
    and data/insurance/us-pet-insurers.json. No clinic, ride or booking link is invented here."""
    root = "../"
    ext = lambda u, t: f'<a href="{e(u)}" rel="noopener" target="_blank">{t} &#8599;</a>'
    rs = json.loads((ROOT / "data" / "rideshare" / "us.json").read_text())
    pv = json.loads((ROOT / "data" / "partner_vets.json").read_text())
    _, ci = hotels_data()
    ins = load_insurers()
    # flights
    btns = flight_aff_buttons(cfg)
    al = "".join(f'<li><a href="{root}airlines/{e(a["slug"])}.html">{e(a["name"])}</a></li>' for a in airlines)
    flights = f"""<section class="bk-sec" id="flights" aria-labelledby="flights-h"><span class="bk-k">Step 1</span><h2 id="flights-h">Flights</h2>
<p>Compare fares, then book your pet&rsquo;s spot directly with the airline: in-cabin pet space is limited per flight, so call or add the pet right after you buy the ticket. Check the airline&rsquo;s pet policy and carrier size first.</p>
<div class="bk-grid two"><div class="bk-card"><h3>Search flights</h3>{'<p class="book-btns">' + "".join(btns) + '</p>' if btns else '<p>Flight search links coming soon.</p>'}
<p class="book-disc">{FLIGHT_DISC.replace("{root}", root)}</p></div>
<div class="bk-card"><h3>Airline pet policies</h3><p>Fees, cabin and hold rules, each checked against the airline&rsquo;s official page:</p>
<ul class="book-cities">{al}</ul>
<p><a href="{root}#compare">Compare airlines side by side</a> &middot; <a href="{root}products/under-seat-carrier-size-by-airline.html">Under-seat carrier sizes by airline</a></p></div></div></section>"""
    # hotels
    cards, tracked = [], False
    for c in ci["cities"]:
        ex, url = hotel_aff_url(cfg, c)
        label = e(ex.get("label") or "See pet-friendly hotels on Expedia")
        tracked = tracked or bool(url)
        btn = (f'<a class="btn" href="{e(url)}" rel="sponsored nofollow noopener" target="_blank">{label}</a>' if url
               else f'<a class="btn" href="{e(c["expedia_target"])}" rel="nofollow noopener" target="_blank">{label}</a>')
        nlux = len(c.get("luxury") or [])
        lux = f'<li><a href="{root}hotels/pet-friendly-hotels-{e(c["slug"])}.html#luxury">{nlux} luxury hotels and their own pet rules</a></li>' if nlux else ""
        cards.append(f'<div class="bk-card"><h3>{e(c["name"])}</h3>' + (f'<p class="small">{e(c["short"])}</p>' if c["short"] != c["name"] else "") +
                     f'<ul><li><a href="{root}hotels/pet-friendly-hotels-{e(c["slug"])}.html">City guide: chain pet fees, weight limits, airport relief areas, dog parks</a></li>{lux}</ul>'
                     f'<p class="book-btns">{btn}</p></div>')
    hotels = f"""<section class="bk-sec" id="hotels" aria-labelledby="hotels-h"><span class="bk-k">Step 2</span><h2 id="hotels-h">Pet-friendly hotels</h2>
<p>Pick a city for each chain&rsquo;s pet fee, weight limit and number of pets (read on the official sites), luxury hotels&rsquo; own pet policies and local tips. The Expedia buttons open a search with the pet-friendly filter on: always check the hotel&rsquo;s own pet policy before you pay.</p>
<div class="bk-grid">{''.join(cards)}</div>
<p><a href="{root}hotels/"><b>All US hotel chains: pet fees &amp; weight limits</b></a> &middot; <a href="{root}hotels/#luxury">Luxury brands&rsquo; pet rules</a></p>
<p class="small">More cities are being added gradually. Policies checked <time datetime="{ci["checked"]}">{nice_date(ci["checked"])}</time>.</p></section>"""
    # rides
    chk = f'<time datetime="{rs["checked"]}">{nice_date(rs["checked"])}</time>'
    svc = ""
    for s in rs["services"]:
        dl = "".join(f'<dt>{e(k)}</dt><dd>{e(v)}</dd>' for k, v, _ in s["facts"])
        srcs = " &middot; ".join(ext(u, e(t)) for t, u in s["sources"].values())
        svc += f'<div class="bk-card bk-ride"><h3>{e(s["name"])}</h3><dl>{dl}</dl><p class="book-disc">Official source: {srcs}</p></div>'
    rob = "".join(f'<li><b>{e(r["name"])}:</b> {e(r["rule"])} {ext(r["src"][1], e(r["src"][0]))}</li>' for r in rs["robotaxis"])
    rides = f"""<section class="bk-sec" id="rides" aria-labelledby="rides-h"><span class="bk-k">Step 3</span><h2 id="rides-h">Taxis &amp; airport rides with your pet</h2>
<p>From the airport to your hotel: request a pet ride in the Uber or Lyft app (US). Rules below are from their official help pages; there are no affiliate links in this section.</p>
<div class="bk-grid two">{svc}</div>
<h3>Robotaxis: service animals only</h3><ul class="book-ride">{rob}</ul>
<p class="book-disc">{e(rs["service_animals_note"])} Checked on the official Uber, Lyft, Waymo, Zoox and Tesla pages on {chk}; fees and availability change, so check the app before you ride.</p></section>"""
    # vets
    clinics = pv.get("clinics") or []
    if clinics:
        places = sorted({f'{c["city"]}, {c["country"]}' for c in clinics})
        partner = (f'<p><b>{len(clinics)} partner clinic{"s" if len(clinics) != 1 else ""}</b> ({e("; ".join(places))}) help with travel paperwork. '
                   f'<a href="{root}partner-vets/">See partner clinics and how to contact them</a>.</p>')
    else:
        partner = (f'<div class="bk-empty"><p><b>Partner clinics coming soon.</b> We only list veterinary clinics that have agreed to be listed, '
                   f'and none has confirmed yet. They will appear here and on <a href="{root}partner-vets/">Partner vets</a> by country and city as soon as they confirm. '
                   f'Until then, use the official tools below to find a vet who can sign your pet&rsquo;s health certificate.</p></div>')
    tchk = pv.get("tools_checked")
    tools = "".join(f'<li>{ext(t["url"], e(t["label"]))}<br>{e(t["text"])}</li>' for t in pv.get("official_tools") or [])
    vets = f"""<section class="bk-sec" id="vets" aria-labelledby="vets-h"><span class="bk-k">Before you fly</span><h2 id="vets-h">Vet clinics &amp; health certificates</h2>
<p>Flying abroad, or to some states, usually means a health certificate, up-to-date rabies vaccination and sometimes a microchip, tests or a permit, all within strict time windows. In the US, a <b>USDA-accredited veterinarian</b> issues the certificate and USDA APHIS endorses it for international travel. Book that vet visit early.</p>
{partner}
<h3>Find an accredited vet: official tools</h3><ul class="bk-tools">{tools}</ul>
{f'<p class="book-disc">Official USDA pages checked <time datetime="{tchk}">{nice_date(tchk)}</time>. We do not book vet appointments and are not paid for referrals.</p>' if tchk else ''}
<h3>Paperwork by destination</h3><ul class="bk-links">
<li><a href="{root}countries/usa.html">Pet travel rules for the USA</a>: federal rules and each state&rsquo;s health certificate and rabies rules.</li>
<li><a href="{root}routes/usa-to-japan.html">USA to Japan</a>: the Japan health certificate (Form AC) completed by a USDA-accredited vet, microchip, rabies titer test and the 180-day wait.</li>
<li><a href="{root}routes/usa-to-south-korea.html">USA to South Korea</a>: ISO microchip, rabies vaccination, a rabies antibody (FAVN) test and a health certificate endorsed by USDA APHIS within 30 days of export.</li>
<li><a href="{root}partner-vets/">Are you a vet? Become a partner clinic</a> (free listing).</li></ul></section>"""
    # insurance
    insurance = f"""<section class="bk-sec" id="insurance" aria-labelledby="ins-h"><span class="bk-k">Peace of mind</span><h2 id="ins-h">Pet insurance for the trip</h2>
<div class="bk-card"><p>Will your pet&rsquo;s insurance pay for an emergency vet away from home? We compared what {len(ins["insurers"])} US insurers say about coverage in the US, Canada and abroad, waiting periods and reimbursement.</p>
<p><a href="{root}{INS_SLUG}"><b>Pet insurance for travelers: coverage compared</b></a> &rsaquo;</p></div></section>"""
    body = f"""{BOOK_CSS}{BOOK_PAGE_CSS}<nav class="crumbs"><a href="{root}index.html">Home</a> &rsaquo; Book your trip</nav>
<h1>Book your pet trip: flights, hotels, airport rides &amp; vets</h1>
<p class="lead bk-lead">Everything to book for a trip with your dog or cat, in one place: flights, pet-friendly hotels, a taxi or rideshare from the airport, the vet visit for the health certificate, and travel insurance. Every rule is from the official source and dated.</p>
<nav aria-label="On this page"><ul class="bk-jump"><li><a href="#flights">&#9992; Flights</a></li><li><a href="#hotels">&#127976; Hotels</a></li><li><a href="#rides">&#128661; Rides</a></li><li><a href="#vets">&#129658; Vets</a></li><li><a href="#insurance">&#128737; Insurance</a></li></ul></nav>
{flights}{hotels}{rides}{vets}{insurance}
<p class="note bk-disc"><b>Affiliate disclosure:</b> some links on this page ({"the flight search and Expedia hotel buttons" if tracked else "the flight search buttons"}) are affiliate links. If you book through them we may earn a commission at no extra cost to you. It never changes the pet rules we publish. Ride, vet and insurance links go to the official sites with no affiliate. <a href="{root}about.html#affiliates">Disclosure</a>. Always confirm pet rules with the airline, hotel or service before you book.</p>"""
    return page(cfg, f"Book your pet trip: flights, hotels, airport rides & vets | {cfg['site_name']}",
                "Book a trip with your dog or cat in one place: flights, pet-friendly hotels in Orlando, New York and Miami, Uber Pet and Lyft Pet airport rides, USDA-accredited vets for health certificates, and pet travel insurance.",
                body, "book/", root, jsonld=[bc_ld(cfg, [("Home", ""), ("Book your trip", "book/")])])


def main():
    cfg, airlines, updates = load()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "airlines").mkdir(parents=True)
    (OUT / "products").mkdir()
    (OUT / "advertise").mkdir()
    (OUT / "partner-vets").mkdir()
    (OUT / "countries").mkdir()
    (OUT / "routes").mkdir()
    (OUT / "hotels").mkdir()
    (OUT / "insurance").mkdir()
    (OUT / "book").mkdir()
    (OUT / "pet-travel-checklist").mkdir()
    pd, lims = load_products(airlines)
    global FORUM_ON
    FORUM_ON = forum_pages.enabled(cfg)
    shutil.copy(ROOT / "static" / "style.css", OUT / "style.css")
    shutil.copytree(ROOT / "static" / "fonts", OUT / "fonts")
    if (ROOT / "static" / "downloads").exists():  # free PDFs (checklist/make_checklist_pdf.py)
        shutil.copytree(ROOT / "static" / "downloads", OUT / "downloads")
    (OUT / ".nojekyll").write_text("")
    if custom_domain(cfg):
        (OUT / "CNAME").write_text(custom_domain(cfg) + "\n")
    build_og_image(cfg)
    (OUT / "index.html").write_text(build_index(cfg, airlines))
    # New home page (design C, delivered by Web Designer; frozen airline table verified 2026-10-22)
    if (ROOT / "static" / "home-c.html").exists():
        home = (ROOT / "static" / "home-c.html").read_text()
        # USA side panel: 'Book your trip' block (rendered by assets/js/home-c.js from window.BOOK_USA)
        js_tag = '<script src="assets/js/home-c.js"></script>'
        assert js_tag in home and "</head>" in home
        book = json.dumps(booking_block(cfg, site_base(cfg) + "/")).replace("</", "<\\/")
        # Homepage 'Plan and book your whole pet trip in one place' section (static HTML, right after the map)
        mark = next(l for l in home.splitlines() if l.startswith("<!--BOOK_HOME"))
        home = home.replace(mark, booking_block(cfg, site_base(cfg) + "/", home=True), 1)
        home = home.replace("</head>", BOOK_CSS + BOOK_HOME_CSS + "</head>", 1).replace(js_tag, f"<script>var BOOK_USA={book};</script>" + js_tag.replace("home-c.js", "home-c.js?v=" + hashlib.md5((ROOT / "static" / "assets" / "js" / "home-c.js").read_bytes()).hexdigest()[:8]), 1)
        home = home.replace("<!--CHECKLIST_CTA-->", checklist_cta(""), 1)
        # Country guides (map panel, pins, chips, flags) from data/home_guides.json
        gjs, gchips = home_guides(cfg)
        gmark = "/*GUIDES: generated by build.py from data/home_guides.json*/"
        cmark = next(l for l in home.splitlines() if l.strip().startswith("<!--GUIDE_CHIPS"))
        assert gmark in home
        home = home.replace(gmark, gjs, 1).replace(cmark, "  " + gchips, 1)
        assert "<!--HDR_AD-->" in home and "<!--HDR_MENU_JS-->" in home
        home = home.replace("<!--HDR_AD-->", MENU_BTN, 1).replace("<!--HDR_MENU_JS-->", header_ad(cfg) + MENU_JS, 1)
        home = home.replace('href="assets/css/theme.css"', f'href="assets/css/theme.css?v={CSS_VER}"', 1)  # header CSS changed: bust cache on home too
        (OUT / "index.html").write_text(home)
        shutil.copytree(ROOT / "static" / "assets", OUT / "assets")
        shutil.copy(ROOT / "static" / "assets" / "img" / "favicon.ico", OUT / "favicon.ico")
    (OUT / "img" / "email").mkdir(parents=True, exist_ok=True)
    for f in (ROOT / "static" / "img-email").glob("*"):
        shutil.copy(f, OUT / "img" / "email" / f.name)
    for a in airlines:
        (OUT / "airlines" / f"{a['slug']}.html").write_text(build_airline(cfg, a, pd, lims))
    (OUT / "updates.html").write_text(build_updates(cfg, airlines, updates))
    (OUT / "about.html").write_text(build_about(cfg))
    (OUT / "privacy.html").write_text(build_privacy(cfg))
    (OUT / "contact.html").write_text(build_contact(cfg))
    (OUT / "advertise" / "index.html").write_text(build_advertise(cfg))
    (OUT / "partner-vets" / "index.html").write_text(build_partner_vets(cfg))
    (OUT / "countries" / "usa.html").write_text(build_country_usa(cfg, airlines))
    (OUT / "routes" / "usa-to-japan.html").write_text(build_route_usa_japan(cfg, airlines))
    (OUT / "routes" / "usa-to-south-korea.html").write_text(build_route_usa_korea(cfg, airlines))
    hch, hci = hotels_data()
    (OUT / "hotels" / "index.html").write_text(build_hotels_index(cfg, hch, hci))
    for c in hci["cities"]:
        (OUT / "hotels" / f"pet-friendly-hotels-{c['slug']}.html").write_text(build_hotel_city(cfg, c, hch, hci))
    (OUT / "insurance" / "pet-insurance-for-travelers.html").write_text(build_insurance_travel(cfg))
    (OUT / "book" / "index.html").write_text(build_book(cfg, airlines))
    (OUT / "pet-travel-checklist" / "index.html").write_text(build_checklist(cfg))
    (OUT / "products" / "index.html").write_text(build_products_index(cfg, pd, lims))
    for p in pd["products"]:
        (OUT / "products" / f"{p['slug']}.html").write_text(build_product(cfg, p, pd, lims, airlines))
    for g in pd["guides"]:
        (OUT / "products" / f"{g['slug']}.html").write_text(build_guide(cfg, g, pd, lims, airlines))
    base = site_base(cfg)
    newest = max(a["last_verified"] for a in airlines if a.get("last_verified"))
    urls = [(f"{base}/", newest), (f"{base}/updates.html", newest), (f"{base}/about.html", newest),
            (f"{base}/privacy.html", newest), (f"{base}/contact.html", newest), (f"{base}/advertise/", newest), (f"{base}/partner-vets/", newest),
            (f"{base}/products/", pd["verified"])]
    urls += [(f"{base}/products/{x['slug']}.html", pd["verified"]) for x in pd["products"] + pd["guides"]]
    urls += [(f"{base}/airlines/{a['slug']}.html", a.get("last_verified") or a.get("last_checked") or newest) for a in airlines]
    urls += forum_pages.build(sys.modules[__name__], cfg, airlines, OUT, ROOT)  # [] while the forum is off
    urls.append((f"{base}/countries/usa.html", json.loads((ROOT / "data" / "countries" / "usa.json").read_text())["checked"]))
    urls.append((f"{base}/routes/usa-to-japan.html", json.loads((ROOT / "data" / "routes" / "usa-japan.json").read_text())["checked"]))
    urls.append((f"{base}/routes/usa-to-south-korea.html", json.loads((ROOT / "data" / "routes" / "usa-korea.json").read_text())["checked"]))
    urls.append((f"{base}/hotels/", hci["checked"]))
    urls += [(f"{base}/hotels/pet-friendly-hotels-{c['slug']}.html", hci["checked"]) for c in hci["cities"]]
    urls.append((f"{base}/{INS_SLUG}", load_insurers()["checked"]))
    urls.append((f"{base}/book/", max(hci["checked"], json.loads((ROOT / "data" / "rideshare" / "us.json").read_text())["checked"],
                                      json.loads((ROOT / "data" / "partner_vets.json").read_text()).get("tools_checked") or "", load_insurers()["checked"])))
    urls.append((f"{base}/pet-travel-checklist/", "2026-10-24"))
    sm = "".join(f"<url><loc>{e(u)}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (OUT / "ads.txt").write_text("google.com, pub-7693501377730690, DIRECT, f08c47fec0942fa0\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    for k in (ROOT / "static").glob("*.txt"):  # IndexNow key file(s): static/<32-hex key>.txt -> site root
        if len(k.stem) == 32 and all(c in "0123456789abcdef" for c in k.stem) and k.read_text().strip() == k.stem:
            shutil.copy(k, OUT / k.name)
    print(f"Built {len(airlines)} airline pages, {len(pd['products'])} products, {len(pd['guides'])} guides, {len(lims)} cabin limits -> {OUT}")
    for a in airlines:
        print(f"  {a['slug']:16} confirmed {confirmed_count(a)}/{len(FIELDS)}  status={a.get('fetch_status')}")


if __name__ == "__main__":
    main()
