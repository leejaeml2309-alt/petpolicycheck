#!/usr/bin/env python3
"""Preview-only: strip travel-booking + non-Amazon affiliate links from site/ HTML."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

PREVIEW_BAR = (
    '<div class="ppc-preview-bar" role="status" style="position:sticky;top:0;z-index:9999;'
    'background:#7a1f1f;color:#fff;font:600 13px/1.35 Inter,system-ui,sans-serif;'
    'padding:8px 12px;text-align:center">LOCAL PREVIEW ONLY — booking platforms and '
    "non-Amazon affiliate links removed · await Marc « publie »</div>"
)

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
""" + PREVIEW_BAR + """
<p><a href="../hotels/">Continue to pet-friendly hotel information</a></p>
</body>
</html>
"""

AFF_HOSTS = {
    "booking.com", "expedia.com", "hotels.com", "agoda.com", "kayak.com",
    "skyscanner.net", "skyscanner.com", "tripadvisor.com", "priceline.com",
    "hopper.com", "airbnb.com", "vrbo.com", "homeaway.com",
    "travelpayouts.com", "tp.media", "kiwi.com", "aviasales.com", "aviasales.ru",
    "tpo.lv", "emrldtp.cc", "orbitz.com", "travelocity.com", "hotwire.com",
    "trivago.com", "hotelscombined.com", "momondo.com", "viator.com",
    "getyourguide.com", "awin1.com", "dwin1.com", "shareasale.com",
    "sjv.io", "pxf.io", "evyy.net", "7eer.net", "prf.hn",
    "anrdoezrs.net", "dpbolvw.net", "jdoqocy.com", "tkqlhce.com",
}

AFF_HOST_SUBSTR = (
    "emrldtp", "travelpayouts", "aviasales", "expedia",
)

AFF_URL_HINTS = (
    "c111.travelpayouts", "expedia.com/affiliate", "tp.media/",
    "aviasales.tpo.lv", "shmarker=", "clickref=",
)


def host_of(url: str) -> str:
    u = url.replace("&amp;", "&").replace("&#38;", "&")
    if u.startswith("//"):
        u = "https:" + u
    try:
        return (urlparse(u).netloc or "").lower().split(":")[0]
    except Exception:
        return ""


def registrable(host: str) -> str:
    h = host.lower().lstrip("www.")
    parts = h.split(".")
    if len(parts) >= 2:
        if parts[-2] in {"co", "com", "ne", "or"} and len(parts) >= 3:
            return ".".join(parts[-3:])
        return ".".join(parts[-2:])
    return h


def is_amazon(url: str) -> bool:
    h = host_of(url)
    r = registrable(h)
    if r.startswith("amazon.") or r in {"amzn.to", "amazon.com", "amazon.co.uk", "amazon.co.jp"}:
        return True
    if "amazon." in h or h.endswith("amzn.to"):
        return True
    if any(x in h for x in ("amazon-adsystem", "images-amazon", "ssl-images-amazon", "media-amazon")):
        return True
    return False


def is_aff_or_booking(url: str) -> bool:
    if not url or url.startswith("#") or url.startswith("mailto:") or url.startswith("tel:"):
        return False
    if is_amazon(url):
        return False
    u = url.lower().replace("&amp;", "&")
    h = host_of(url)
    r = registrable(h)
    if r in AFF_HOSTS:
        return True
    if any(s in h for s in AFF_HOST_SUBSTR):
        return True
    if any(s in u for s in AFF_URL_HINTS):
        return True
    if "/go/" in u.split("?")[0] or "/out/" in u.split("?")[0]:
        if not u.startswith("/") and "petpolicycheck.com" not in u:
            return True
    return False


def find_element_end(html: str, start: int) -> int | None:
    m = re.match(r"<([a-zA-Z][a-zA-Z0-9:-]*)", html[start:])
    if not m:
        return None
    tag = m.group(1)
    i = start + 1
    in_q = None
    while i < len(html):
        ch = html[i]
        if in_q:
            if ch == in_q:
                in_q = None
        elif ch in ('"', "'"):
            in_q = ch
        elif ch == ">":
            i += 1
            break
        i += 1
    else:
        return None
    open_end = i
    raw_open = html[start:open_end]
    if raw_open.rstrip().endswith("/>") or tag.lower() in {
        "br", "img", "hr", "meta", "input", "link", "source", "wbr", "area", "col", "embed", "track", "base"
    }:
        return open_end
    tag_l = tag.lower()
    depth = 1
    pos = open_end
    low = html.lower()
    open_tok = "<" + tag_l
    close_tok = "</" + tag_l + ">"
    while pos < len(html):
        nxt_open = low.find(open_tok, pos)
        nxt_close = low.find(close_tok, pos)

        def real_open(p: int) -> bool:
            if p < 0:
                return False
            after = low[p + len(open_tok): p + len(open_tok) + 1]
            return after in ("", " ", "\n", "\t", "\r", ">", "/")

        if nxt_close < 0:
            return None
        if nxt_open >= 0 and real_open(nxt_open) and nxt_open < nxt_close:
            depth += 1
            pos = nxt_open + 1
        else:
            depth -= 1
            pos = nxt_close + len(close_tok)
            if depth == 0:
                return pos
    return None


def remove_elements(html: str, open_re: re.Pattern, content_pred=None) -> tuple[str, int]:
    n = 0
    pos = 0
    out = []
    while True:
        m = open_re.search(html, pos)
        if not m:
            out.append(html[pos:])
            break
        start = m.start()
        end = find_element_end(html, start)
        if end is None:
            out.append(html[pos:m.end()])
            pos = m.end()
            continue
        chunk = html[start:end]
        if content_pred and not content_pred(chunk):
            out.append(html[pos:end])
            pos = end
            continue
        out.append(html[pos:start])
        n += 1
        pos = end
    return "".join(out), n


def remove_affiliate_anchors(html: str) -> tuple[str, int]:
    n = 0
    pos = 0
    out = []
    for m in re.finditer(r"<a\b", html, re.I):
        start = m.start()
        if start < pos:
            continue
        end = find_element_end(html, start)
        if end is None:
            continue
        chunk = html[start:end]
        hm = re.search(r"""href\s*=\s*(["'])(.*?)\1""", chunk, re.I | re.S)
        if not hm:
            continue
        url = hm.group(2)
        if is_aff_or_booking(url):
            out.append(html[pos:start])
            n += 1
            pos = end
    out.append(html[pos:])
    return "".join(out), n


def clean_empty_wrappers(html: str) -> str:
    # empty or whitespace-only paragraphs that held booking buttons
    html = re.sub(
        r'<p class="(?:buy(?: jp-hs)?|book-btns)"[^>]*>\s*</p>',
        "",
        html,
        flags=re.I,
    )
    html = re.sub(
        r'<p class="(?:small disc|book-disc|disc)"[^>]*>\s*(?:Affiliate links?:|Enlaces de afiliados:)[\s\S]*?</p>',
        "",
        html,
        flags=re.I,
    )
    return html


def rewrite_headings(html: str) -> str:
    reps = [
        ("Plan and book your whole pet trip in one place", "Pet-friendly hotels and airport rides"),
        (
            "Flights, pet-friendly hotels and airport rides with your dog or cat: everything ready before you go.",
            "Hotel pet rules by city, and airport-to-hotel rides with your dog or cat.",
        ),
        ("Book your trip", "Pet-friendly hotels and airport rides"),
        ("Reserve su viaje", "Hoteles y traslados que admiten mascotas"),
        ("Reserva tu viaje", "Hoteles y traslados que admiten mascotas"),
        ("Flights, hotels by city and pet-friendly rides.", "Hotel pet rules by city, and airport-to-hotel rides."),
        (
            "Vuelos, hoteles por ciudad y traslados que admiten mascotas.",
            "Normas para mascotas de hoteles por ciudad, y traslados del aeropuerto al hotel.",
        ),
        (
            "Planifique y reserve todo el viaje de su mascota en un solo lugar",
            "Hoteles y traslados que admiten mascotas",
        ),
        (
            "Vuelos, hoteles que admiten mascotas y traslados desde el aeropuerto con su perro o gato: todo listo antes de irse.",
            "Normas para mascotas de hoteles por ciudad y traslados del aeropuerto al hotel con su perro o gato.",
        ),
    ]
    for a, b in reps:
        html = html.replace(a, b)
    # escaped JS string variants
    html = html.replace("Book your trip<\\/h3>", "Pet-friendly hotels and airport rides<\\/h3>")
    html = html.replace("Reserve su viaje<\\/h3>", "Hoteles y traslados que admiten mascotas<\\/h3>")
    return html


def has_amazon_link(html: str) -> bool:
    for m in re.finditer(r"""href\s*=\s*(["'])(.*?)\1""", html, re.I):
        if is_amazon(m.group(2)):
            return True
    return False


def update_footer_aff(html: str) -> str:
    amazon = has_amazon_link(html)
    # span with or without data-i18n
    pat = re.compile(
        r'<span(?:\s+data-i18n="site\.foot\.aff")?>Some links may be affiliate links; we may earn a commission at no extra cost to you\. This never affects our data\.</span>\s*',
        re.I,
    )
    # also ES hardcoded footer without i18n, other langs
    pat2 = re.compile(
        r'<span(?:\s+data-i18n="site\.foot\.aff")?>[^<]*affiliat[^<]*</span>\s*',
        re.I,
    )
    if amazon:
        html = pat.sub(
            '<span data-i18n="site.foot.aff">As an Amazon Associate I earn from qualifying purchases.</span> ',
            html,
        )
        html = pat2.sub(
            '<span data-i18n="site.foot.aff">As an Amazon Associate I earn from qualifying purchases.</span> ',
            html,
        )
    else:
        html = pat.sub("", html)
        html = pat2.sub("", html)
    return html


def update_page_disclosures(html: str, rel: str) -> str:
    old = (
        "Affiliate disclosure: some links on this page may be affiliate links; if you buy through them we may earn a commission at no extra cost to you. "
        "It never changes the dimensions or fit results shown. We have not tested these products ourselves: every figure comes from the linked manufacturer page. "
        "As an Amazon Associate I earn from qualifying purchases."
    )
    new = (
        "As an Amazon Associate I earn from qualifying purchases. Product links to Amazon.com may earn a commission at no extra cost to you. "
        "That never changes the dimensions or fit results shown. We have not tested these products ourselves: every figure comes from the linked manufacturer page."
    )
    html = html.replace(old, new)

    old_ins = (
        "we have no affiliate relationship with any insurer on this page today, and every link goes to the insurer&rsquo;s own site. "
        "If that changes, quote links will be marked as affiliate links; PetPolicyCheck may then earn a fee if you request a quote or buy a policy through them. "
        "That won&rsquo;t change what you pay or how we describe products. "
        '<a href="../about.html#affiliates">Affiliate disclosure</a>.'
    )
    new_ins = (
        "every link on this page goes to the insurer&rsquo;s own official site. "
        "We have no affiliate relationship with any insurer."
    )
    html = html.replace(old_ins, new_ins)
    return html


def update_legal(html: str, rel: str) -> str:
    if rel == "about.html":
        html = html.replace(
            "How we verify airline pet policies, our disclaimer and affiliate disclosure.",
            "How we verify airline pet policies, our disclaimer and Amazon Associates disclosure.",
        )
        html = html.replace(
            "Some pages may contain affiliate links (for example to pet carriers, pet insurance or hotel booking sites such as Expedia). If you buy through them we may earn a commission at no extra cost to you. Affiliate relationships never change the policy information we publish.",
            "Some product pages contain Amazon Associates links to items on Amazon.com. As an Amazon Associate I earn from qualifying purchases. We do not use other affiliate programs. That never changes the policy information we publish.",
        )
        html = html.replace(
            "We do not currently show Google AdSense units on this site. Affiliate links are disclosed on the pages that use them and never change the policy information we publish. See our <a href=\"privacy.html\">privacy policy</a>.",
            "We do not currently show Google AdSense units on this site. The only affiliate program we use is Amazon Associates, disclosed on the product pages that link to Amazon.com. See our <a href=\"privacy.html\">privacy policy</a>.",
        )
    if rel == "privacy.html":
        html = html.replace(
            "Privacy policy for PetPolicyCheck: cookies, Google Analytics 4, Travelpayouts and affiliate links, and GitHub Pages hosting explained.",
            "Privacy policy for PetPolicyCheck: cookies, Google Analytics 4, Amazon Associates links, and GitHub Pages hosting explained.",
        )
        html = html.replace(
            "including by the analytics and affiliate services we use.",
            "including by the analytics service we use and, on some product pages, Amazon Associates.",
        )
        html = html.replace(
            "Forum pages for signing in and posting don't show ads or load affiliate scripts.",
            "Forum pages for signing in and posting don't show ads or load affiliate scripts.",
        )
        html = html.replace(
            "The third-party analytics and affiliate services described below may set and read cookies",
            "The third-party analytics service described below, and Amazon Associates on some product pages, may set and read cookies",
        )
        # drop Travelpayouts heading+paragraph
        html = re.sub(
            r"<h2>Travelpayouts</h2>\s*<p>[\s\S]*?</p>\s*",
            "",
            html,
            count=1,
        )
        html = html.replace("<h2>Affiliate links and partner cookies</h2>", "<h2>Amazon Associates</h2>")
        html = html.replace(
            "Some pages include affiliate links to partners, for example brands on the Impact network (such as Chewy, Trupanion or Lemonade), Amazon.com, Booking.com and Travelpayouts partners. If you buy through one, we may earn a commission at no extra cost to you. When you click an affiliate link, you leave our site and the partner (or its affiliate network) may set cookies or use similar technology to record that the visit came from us. Those cookies are governed by the partner's own privacy policy, not ours. We don't receive personal information about you from these partners, only aggregated sales or commission reports. Affiliate relationships never change the policy information we publish.",
            "Some product pages include Amazon Associates links to Amazon.com. If you buy through one, we may earn a commission at no extra cost to you. When you click an Amazon Associates link, you leave our site and Amazon may set cookies or use similar technology to record that the visit came from us, under Amazon's own privacy notice. We don't receive personal information about you from Amazon, only aggregated sales or commission reports. This never changes the policy information we publish. We do not use other affiliate programs.",
        )
    return html


def inject_preview(html: str) -> str:
    if "ppc-preview-bar" not in html:
        html = re.sub(r"(<body\b[^>]*>)", r"\1" + PREVIEW_BAR, html, count=1, flags=re.I)
    if re.search(r'<meta\s+name=["\']robots["\']', html, re.I):
        html = re.sub(
            r'<meta\s+name=["\']robots["\'][^>]*>',
            '<meta name="robots" content="noindex, nofollow">',
            html,
            count=1,
            flags=re.I,
        )
    else:
        html = re.sub(r"(<head\b[^>]*>)", r"\1\n<meta name=\"robots\" content=\"noindex, nofollow\">", html, count=1, flags=re.I)
    return html


def process_html(html: str, rel: str, preview: bool = False) -> tuple[str, dict]:
    stats = {
        "emrldtp": 0,
        "impact_meta": 0,
        "footer_book": 0,
        "asides": 0,
        "book_g": 0,
        "anchors": 0,
    }
    # emrldtp loader
    new, n = re.subn(
        r'<script\b[^>]*(?:nowprocket|data-cmp-ab)[^>]*>\s*\(function\s*\(\)\s*\{[\s\S]*?emrldtp\.cc[\s\S]*?\}\)\(\);\s*</script>\s*',
        "",
        html,
        flags=re.I,
    )
    if n:
        html = new
        stats["emrldtp"] += n
    else:
        new, n = re.subn(
            r'<script\b[^>]*>\s*\(function\s*\(\)\s*\{[\s\S]*?emrldtp\.cc[\s\S]*?\}\)\(\);\s*</script>\s*',
            "",
            html,
            flags=re.I,
        )
        html = new
        stats["emrldtp"] += n

    new, n = re.subn(
        r'<meta\s+name="impact-site-verification"[^>]*>\s*',
        "",
        html,
        flags=re.I,
    )
    html = new
    stats["impact_meta"] += n

    # footer Book your trip / Reserve su viaje / translations
    new, n = re.subn(
        r'<li><a\b[^>]*href="[^"]*book/?"[^>]*>[\s\S]*?</a></li>',
        "",
        html,
        flags=re.I,
    )
    html = new
    stats["footer_book"] += n

    # reco flights asides (city expedia box + airline/route flight CTAs)
    html, n = remove_elements(
        html,
        re.compile(r'<aside\b[^>]*class="[^"]*\breco\b[^"]*\bflights\b[^"]*"[^>]*>', re.I),
    )
    stats["asides"] += n
    html, n = remove_elements(
        html,
        re.compile(r'<aside\b[^>]*class="[^"]*\bflights\b[^"]*\breco\b[^"]*"[^>]*>', re.I),
    )
    stats["asides"] += n

    # book-g blocks that contain booking-platform URLs (homepage flights column)
    def bookg_is_aff(chunk: str) -> bool:
        return bool(re.search(r"expedia|aviasales|travelpayouts|tp\.media|emrldtp|kiwi\.com/deep", chunk, re.I))

    html, n = remove_elements(
        html,
        re.compile(r'<div\b[^>]*class="[^"]*\bbook-g\b[^"]*"[^>]*>', re.I),
        content_pred=bookg_is_aff,
    )
    stats["book_g"] += n

    html, n = remove_affiliate_anchors(html)
    stats["anchors"] += n

    html = clean_empty_wrappers(html)
    html = rewrite_headings(html)
    html = update_page_disclosures(html, rel)
    html = update_legal(html, rel)

    # collapse homepage 3-col grid now that flights column is gone
    html = html.replace(
        ".book-home .bh-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;align-items:stretch}",
        ".book-home .bh-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px;align-items:stretch}",
    )

    html = update_footer_aff(html)
    if preview:
        html = inject_preview(html)
    return html, stats


def main():
    totals = {}
    changed = 0
    # special-case /book/
    book = SITE / "book" / "index.html"
    if book.exists():
        book.write_text(BOOK_REDIRECT, encoding="utf-8")
        changed += 1
        print("rewrote site/book/index.html -> noindex redirect to /hotels/")

    for fp in sorted(SITE.rglob("*.html")):
        rel = str(fp.relative_to(SITE))
        if rel == "book/index.html":
            continue
        raw = fp.read_text(encoding="utf-8", errors="replace")
        new, stats = process_html(raw, rel)
        if new != raw:
            fp.write_text(new, encoding="utf-8")
            changed += 1
        for k, v in stats.items():
            totals[k] = totals.get(k, 0) + v

    # sitemap
    sm = SITE / "sitemap.xml"
    if sm.exists():
        t = sm.read_text(encoding="utf-8")
        nt, n = re.subn(r"<url>\s*<loc>https://petpolicycheck.com/book/</loc>[\s\S]*?</url>", "", t)
        if n:
            sm.write_text(nt, encoding="utf-8")
            print(f"removed {n} /book/ url(s) from sitemap")

    print("files_changed", changed)
    print("stats", totals)


if __name__ == "__main__":
    main()
