#!/usr/bin/env python3
"""Preview-only transform: remove ad panels and brand-ad offers. Do not run build.py main() (it rmtree site/)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW_BAR = (
    '<div class="ppc-preview-bar" role="status" style="position:sticky;top:0;z-index:9999;'
    'background:#7a1f1f;color:#fff;font:600 13px/1.35 Inter,system-ui,sans-serif;'
    'padding:8px 12px;text-align:center">LOCAL PREVIEW ONLY — ad panels removed · await Marc « publie »</div>'
)
REDIRECT = """<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="robots" content="noindex,nofollow">
<meta http-equiv="refresh" content="0;url=/contact.html#suggest-a-product">
<link rel="canonical" href="https://petpolicycheck.com/contact.html">
<title>Contact · PetPolicyCheck</title>
<script>location.replace('/contact.html#suggest-a-product');</script>
</head>
<body>
<div class="ppc-preview-bar" role="status" style="position:sticky;top:0;z-index:9999;background:#7a1f1f;color:#fff;font:600 13px/1.35 Inter,system-ui,sans-serif;padding:8px 12px;text-align:center">LOCAL PREVIEW ONLY — ad panels removed · await Marc « publie »</div>
<p>This page has moved to <a href="/contact.html#suggest-a-product">Contact — Suggest a product</a>.</p>
</body>
</html>
"""
STATS: dict[str, int] = {}

def bump(k, n=1):
    STATS[k] = STATS.get(k, 0) + n


def patch_build_py():
    p = ROOT / "build.py"
    t = p.read_text()
    orig = t

    if "SHOW_ADS =" not in t:
        t = t.replace(
            'ADSENSE_CLIENT = "ca-pub-7693501377730690"',
            'ADSENSE_CLIENT = "ca-pub-7693501377730690"\n'
            '# Reversible preview switch (2026-11-10). True restores AdSense units,\n'
            '# partner placeholders, and the /advertise/ offer. See docs/paddle-noads-reversible.md.\n'
            'SHOW_ADS = False',
            1,
        )

    t = t.replace(
        '       ("pro/", "For Business", "site.nav.pro", ("pro/", "extension/", "b2b-pet-desk/")),  # briefcase pastille via pastilles.js theme-b2b\n'
        '       ("advertise/", "Advertise", "site.nav.advertise", ("advertise/",))]\n',
        '       ("pro/", "For Business", "site.nav.pro", ("pro/", "extension/", "b2b-pet-desk/")),  # briefcase pastille via pastilles.js theme-b2b\n'
        ']\n'
        'if SHOW_ADS:\n'
        '    NAV.append(("advertise/", "Advertise", "site.nav.advertise", ("advertise/",)))\n',
        1,
    )

    t = t.replace(
        '    if not ads:\n        return ""  # no-AdSense pages (e.g. /pet-travel-checklist/): no ad band at all',
        '    if not SHOW_ADS or not ads:\n        return ""  # no-AdSense pages (e.g. /pet-travel-checklist/): no ad band at all',
        1,
    )
    t = t.replace(
        'def home_footer_ad(cfg):\n    """Homepage bottom band: three 300×250 units. config.json "adsense_home_footer_slot" on each <ins>.\n    Empty -> three dashed Advertise-here cells."""\n',
        'def home_footer_ad(cfg):\n    """Homepage bottom band: three 300×250 units. config.json "adsense_home_footer_slot" on each <ins>.\n    Empty -> three dashed Advertise-here cells."""\n    if not SHOW_ADS:\n        return ""\n',
        1,
    )
    t = t.replace(
        'def site_footer_ad(cfg, root, fi):\n    """Three 300×250 units in the shared site footer',
        'def site_footer_ad(cfg, root, fi):\n    if not SHOW_ADS:\n        return ""\n    """Three 300×250 units in the shared site footer',
        1,
    )
    # docstring after return is ugly; fix by putting guard after docstring instead if we already did it wrong
    # I'll leave if it's valid Python... actually putting if between def and docstring makes the string the body. BAD.
    # Fix that immediately.
    t = t.replace(
        'def site_footer_ad(cfg, root, fi):\n    if not SHOW_ADS:\n        return ""\n    """Three 300×250 units in the shared site footer',
        'def site_footer_ad(cfg, root, fi):\n    """Three 300×250 units in the shared site footer',
        1,
    )
    t = t.replace(
        '    A discreet \'Advertise here\' link stays under the row."""\n    slot = str(((cfg.get("ads") or {}).get("site_footer") or {}).get("adsense_slot") or "").strip()',
        '    A discreet \'Advertise here\' link stays under the row."""\n    if not SHOW_ADS:\n        return ""\n    slot = str(((cfg.get("ads") or {}).get("site_footer") or {}).get("adsense_slot") or "").strip()',
        1,
    )

    t = t.replace(
        '{li(root + "extension/", "site.foot.extension", "Chrome Extension")}{li(root + "advertise/", "site.nav.advertise", "Advertise")}{li(root + "partner-vets/", "site.foot.vets", "Partner vets")}',
        '{li(root + "extension/", "site.foot.extension", "Chrome Extension")}'
        '{(li(root + "advertise/", "site.nav.advertise", "Advertise") if SHOW_ADS else "")}'
        '{li(root + "partner-vets/", "site.foot.vets", "Partner vets")}',
        1,
    )

    t = t.replace(
        '    if sponsor == "auto":\n        sponsor = "frame" if ads else "ph"\n',
        '    if not SHOW_ADS:\n        sponsor = "off"\n    if sponsor == "auto":\n        sponsor = "frame" if ads else "ph"\n',
        1,
    )

    t = t.replace(
        'def partner_banner(root, slot="top-partner"):\n',
        'def partner_banner(root, slot="top-partner"):\n    if not SHOW_ADS:\n        return ""\n',
        1,
    )

    # page(): no AdSense script, no partner-banner.js when SHOW_ADS is False
    t = t.replace(
        '    if ads:\n        ads_head = ga_nl + ADSENSE + "\\n" + TP_DRIVE + "\\n"\n    elif extra_live:\n        ads_head = ga_nl + ADSENSE + "\\n"\n    else:\n        ads_head = ga_nl\n',
        '    if not SHOW_ADS:\n        ads_head = ga_nl + (TP_DRIVE + "\\n" if ads else "")\n    elif ads:\n        ads_head = ga_nl + ADSENSE + "\\n" + TP_DRIVE + "\\n"\n    elif extra_live:\n        ads_head = ga_nl + ADSENSE + "\\n"\n    else:\n        ads_head = ga_nl\n',
        1,
    )
    t = t.replace(
        '{compact_header(root, path)}{partner_banner(root)}{header_ad(cfg, ads)}<script src="{root}assets/js/partner-banner.js" defer data-partner-root="{root}assets/partners/"></script>',
        '{compact_header(root, path)}{partner_banner(root)}{header_ad(cfg, ads)}'
        '{(("" if not SHOW_ADS else \'<script src="\'+root+\'assets/js/partner-banner.js" defer data-partner-root="\'+root+\'assets/partners/"></script>\'))}',
        1,
    )

    t = t.replace(
        '        mid_ad = f\'<div class="wrap home-mid-ad">{ad_grid(cfg, "home_mid", "")}</div>\'\n',
        '        mid_ad = f\'<div class="wrap home-mid-ad">{ad_grid(cfg, "home_mid", "")}</div>\' if SHOW_ADS else ""\n',
        1,
    )

    t = t.replace(
        'def ad_ph(root, i18n=False):\n',
        'def ad_ph(root, i18n=False):\n    if not SHOW_ADS:\n        return ""\n',
        1,
    )
    t = t.replace(
        'def ad_frame(cfg, key, root, i18n=False, attrs=""):\n',
        'def ad_frame(cfg, key, root, i18n=False, attrs=""):\n    if not SHOW_ADS:\n        return ""\n',
        1,
    )
    t = t.replace(
        'def ad_slot(cfg, key, root, i18n=False):\n',
        'def ad_slot(cfg, key, root, i18n=False):\n    if not SHOW_ADS:\n        return ""\n',
        1,
    )
    t = t.replace(
        'def ad_grid(cfg, key, root, i18n=False, n=3):\n',
        'def ad_grid(cfg, key, root, i18n=False, n=3):\n    if not SHOW_ADS:\n        return ""\n',
        1,
    )
    t = t.replace(
        'def medium_rect_grid(slot, key, n=3):\n',
        'def medium_rect_grid(slot, key, n=3):\n    if not SHOW_ADS:\n        return ""\n',
        1,
    )
    t = t.replace(
        'def medium_rect_empty_grid(root, key, i18n=False, todo="", n=3):\n',
        'def medium_rect_empty_grid(root, key, i18n=False, todo="", n=3):\n    if not SHOW_ADS:\n        return ""\n',
        1,
    )

    # advertise page -> redirect
    # Replace build_advertise function body start: we'll swap the whole function via regex
    t2, n = re.subn(
        r"def build_advertise\(cfg\):\n    mail = obf_mail\(cfg\[\"contact_email\"\]\)\n    body = f\"\"\".*?return page\(cfg, f\"Advertise on \{cfg\['site_name'\]\}: reach pet owners planning to fly\",\n                \"Sponsorship and banner placements on PetPolicyCheck for pet carrier brands, pet insurance, pet relocation and pet-friendly travel. Rates on request.\",\n                body, \"advertise/\", \"../\"\)\n",
        '''def build_advertise(cfg):
    """When SHOW_ADS is False, /advertise/ is a noindex redirect to Contact."""
    if not SHOW_ADS:
        return (
            '<!doctype html>\\n<html lang="en-US">\\n<head>\\n<meta charset="utf-8">\\n'
            '<meta name="robots" content="noindex,nofollow">\\n'
            '<meta http-equiv="refresh" content="0;url=/contact.html#suggest-a-product">\\n'
            '<link rel="canonical" href="https://petpolicycheck.com/contact.html">\\n'
            '<title>Contact · PetPolicyCheck</title>\\n'
            "<script>location.replace('/contact.html#suggest-a-product');</script>\\n"
            '</head>\\n<body>\\n<p>This page has moved to '
            '<a href="/contact.html#suggest-a-product">Contact — Suggest a product</a>.</p>\\n'
            '</body></html>\\n'
        )
    mail = obf_mail(cfg["contact_email"])
    body = f"""<h1>Advertise on {e(cfg['site_name'])}</h1>
<p>PetPolicyCheck helps people fly with a dog or cat: airline pet policies checked against the official source and dated, plus carrier and crate guides that compare official product dimensions with airline limits.</p>
<h2>Audience</h2>
<p>Pet owners planning to fly with their pets, in the cabin or in the hold, or to move abroad with them. Readers come to look up a specific airline's pet rules, carrier sizes, weight limits and fees. <b>Traffic stats available on request.</b></p>
<h2>Placements</h2>
<div class="tablewrap"><table class="cmp"><thead><tr><th>Placement</th><th>Where</th><th>Creative size</th></tr></thead><tbody>
<tr><td data-l="Placement">Airline page banner</td><td data-l="Where">Top of every airline pet policy page</td><td data-l="Size">728 &times; 90 px (scales down on mobile)</td></tr>
<tr><td data-l="Placement">Guide sponsor</td><td data-l="Where">Sponsor box in the product guides (carriers, crates, bowls)</td><td data-l="Size">300 &times; 250 px</td></tr>
<tr><td data-l="Placement">Site-wide footer</td><td data-l="Where">Footer of every page</td><td data-l="Size">468 &times; 60 px</td></tr>
</tbody></table></div>
<p class="small">Every placement is clearly labelled "Sponsored" and links with rel="sponsored nofollow". One advertiser per placement at a time. Sponsor creatives are images only (PNG, JPG or WebP); no pop-ups, auto-play or tracking scripts. Separately, the site also shows Google AdSense ads (see our <a href="{root}privacy.html">privacy policy</a>).</p>
<h2>Good fit for</h2>
<ul><li>Pet carrier, crate and travel gear brands</li><li>Pet insurance</li><li>Pet relocation and pet shipping services</li><li>Pet-friendly hotels and travel services</li></ul>
<h2>Editorial independence</h2>
<p>Sponsors never change our airline data, dimensions or fit results, and sponsored products get no special placement in guides (see our <a href="{root}about.html#affiliates">disclosure</a>).</p>
<h2>Rates and booking</h2>
<p><b>Rates on request.</b> Email {mail} with your brand, the placement you're interested in and your dates.</p>"""
    return page(cfg, f"Advertise on {cfg['site_name']}: reach pet owners planning to fly",
                "Sponsorship and banner placements on PetPolicyCheck for pet carrier brands, pet insurance, pet relocation and pet-friendly travel. Rates on request.",
                body, "advertise/", "../")

''',
        t,
        count=1,
        flags=re.S,
    )
    if n != 1:
        print("WARNING: build_advertise replace count", n)

    # about advertising section
    t = t.replace(
        '<h2 id="advertising">Advertising</h2>\n'
        '<p>The site shows ads served by Google AdSense and may load affiliate scripts such as Travelpayouts. Advertisers never change the policy information we publish. See our <a href="privacy.html">privacy policy</a> for how advertising cookies work and how to opt out of personalized ads.</p>\n',
        '<h2 id="affiliates-ads">How the site is funded</h2>\n'
        '<p>We do not currently show Google AdSense units on this site. Affiliate links are disclosed on the pages that use them and never change the policy information we publish. See our <a href="privacy.html">privacy policy</a>.</p>\n',
        1,
    )

    t = t.replace(
        '    services = "advertising, analytics and affiliate" if ga_on else "advertising and affiliate"\n'
        '    cookie_parties = "advertising, analytics and affiliate" if ga_on else "advertising and affiliate"\n'
        '    desc = ("Privacy policy for PetPolicyCheck: Google AdSense advertising cookies and how to opt out, Google Analytics 4, Travelpayouts and affiliate links, and GitHub Pages hosting explained."\n'
        '            if ga_on else\n'
        '            "Privacy policy for PetPolicyCheck: Google AdSense advertising cookies and how to opt out, Travelpayouts and affiliate links, and GitHub Pages hosting explained.")\n',
        '    services = "analytics and affiliate" if ga_on else "affiliate"\n'
        '    cookie_parties = "analytics and affiliate" if ga_on else "affiliate"\n'
        '    desc = ("Privacy policy for PetPolicyCheck: cookies, Google Analytics 4, Travelpayouts and affiliate links, and GitHub Pages hosting explained."\n'
        '            if ga_on else\n'
        '            "Privacy policy for PetPolicyCheck: cookies, Travelpayouts and affiliate links, and GitHub Pages hosting explained.")\n',
        1,
    )
    t = t.replace(
        '<h2>Advertising (Google AdSense)</h2>\n'
        "<p>We use Google AdSense to show ads on this site. Third-party vendors, including Google, use cookies to serve ads based on a user's prior visits to this website or other websites. Google's use of advertising cookies enables it and its partners to serve ads to our users based on their visit to our site and/or other sites on the Internet.</p>\n"
        '<p>You may opt out of personalized advertising by visiting <a href="https://adssettings.google.com" rel="noopener" target="_blank">Google Ads Settings</a>. You can also opt out of some third-party vendors\' use of cookies for personalized advertising by visiting <a href="https://www.aboutads.info" rel="noopener" target="_blank">www.aboutads.info</a>. If you opt out, you may still see ads, but they won\'t be personalized.</p>\n',
        '<h2>Google AdSense</h2>\n'
        '<p>We do not currently load Google AdSense on these pages, so AdSense cookies are not set from this site today. Our publisher account may still appear in ads.txt. If we show AdSense units again, Google and its vendors may use cookies to show ads based on prior visits. You can use <a href="https://adssettings.google.com" rel="noopener" target="_blank">Google Ads Settings</a> and <a href="https://www.aboutads.info" rel="noopener" target="_blank">www.aboutads.info</a>. If you use those controls, any future units would not be personalized.</p>\n',
        1,
    )

    t = t.replace(
        '<h2>Partnerships &amp; sponsorship</h2>\n'
        '<p>Pet travel brands, insurers and travel companies interested in partnerships or sponsorship are welcome to get in touch. Sponsorship never changes the airline policy data we publish (see our <a href="about.html#affiliates">disclosure</a>).</p>\n',
        '<h2 id="suggest-a-product">Suggest a product</h2>\n'
        '<p>If you make a pet-travel product (a carrier, crate, or similar gear) and would like us to consider it for our product guides, email us with the product name, a link to the official page, and the official dimensions. A listing is not guaranteed; we compare official dimensions with airline limits and keep editorial independence (see our <a href="about.html#affiliates">disclosure</a>).</p>\n',
        1,
    )
    t = t.replace(
        '"Contact PetPolicyCheck for corrections to airline pet policy data, partnerships or sponsorship."',
        '"Contact PetPolicyCheck for corrections to airline pet policy data, or to suggest a product for our guides."',
        1,
    )

    t = t.replace('not an advertising cookie', 'not an ad-network cookie')
    t = t.replace(
        'empty until a program accepts the site (then the page shows a sponsored quote link).',
        'empty until a program accepts the site (then the page shows an affiliate quote link).',
    )
    t = t.replace(
        'through links marked &ldquo;sponsored&rdquo; on this page. ',
        'through affiliate links on this page. ',
    )
    t = t.replace(
        'quote links will be marked &ldquo;sponsored&rdquo;; PetPolicyCheck may then earn a fee if you request a quote or buy a policy through them. ',
        'quote links will be marked as affiliate links; PetPolicyCheck may then earn a fee if you request a quote or buy a policy through them. ',
    )
    t = t.replace(
        '{e(alabel)}</a> <span class="small">sponsored</span>',
        '{e(alabel)}</a> <span class="small">affiliate</span>',
    )

    # sitemap: only include /advertise/ when SHOW_ADS
    t = t.replace(
        '(f"{base}/contact.html", newest), (f"{base}/advertise/", newest), (f"{base}/partner-vets/", newest),',
        '(f"{base}/contact.html", newest)] + ([(f"{base}/advertise/", newest)] if SHOW_ADS else []) + [(f"{base}/partner-vets/", newest),',
        1,
    )

    if t != orig:
        p.write_text(t)
        bump("build.py_patched")
        # syntax check later
    else:
        print("WARNING: build.py unchanged")


def strip_ad_markup(html: str) -> str:
    before = html
    html = re.sub(r'<script async src="https://pagead2\.googlesyndication\.com/pagead/js/adsbygoogle\.js[^"]*" crossorigin="anonymous"></script>\s*', '', html)
    html = re.sub(r'<script src="[^"]*partner-banner\.js[^"]*" [^>]*></script>\s*', '', html)
    html = re.sub(r'<script src="[^"]*partner-banner\.js[^"]*"></script>\s*', '', html)
    html = re.sub(r'<aside class="partner-slot\b[^>]*>.*?</aside>', '', html, flags=re.S)
    html = re.sub(r'<aside class="adframe\b[^>]*>.*?</aside>', '', html, flags=re.S)
    html = re.sub(r'<div class="adgrid\b[^>]*>\s*</div>', '', html)
    html = re.sub(r'<div class="hdr-band">\s*<div class="wrap">\s*</div>\s*</div>', '', html)
    html = re.sub(r'<div class="wrap sfad-wrap">\s*</div>', '', html)
    html = re.sub(r'<div class="wrap sfad-wrap">.*?</div>', '', html, flags=re.S)
    html = re.sub(r'<p class="sfad-adv">.*?</p>', '', html, flags=re.S)
    html = re.sub(r'<p class="adph">.*?</p>', '', html, flags=re.S)
    html = re.sub(r'<div class="wrap home-mid-ad">\s*</div>', '', html)
    html = re.sub(r'<div class="wrap home-bottom-ad">\s*</div>', '', html)
    html = re.sub(r'<div class="wrap home-mid-ad">.*?</div>', '', html, flags=re.S)
    html = re.sub(r'<div class="wrap home-bottom-ad">.*?</div>', '', html, flags=re.S)
    # homepage / ES mid-page sell band
    html = re.sub(r'<div class="wrap">\s*<div class="advert">.*?</div>\s*</div>', '', html, flags=re.S)
    # footer + misc advertise links (keep affiliate rel=sponsored)
    html = re.sub(r'<li><a href="[^"]*advertise/?"[^>]*>.*?</a></li>', '', html, flags=re.S)
    html = re.sub(r'<a class="cta(?:\s+menu-only)?" href="[^"]*advertise/?"[^>]*>.*?</a>', '', html, flags=re.S)
    html = re.sub(r'<a class="adframe-cta" href="[^"]*advertise/?"[^>]*>.*?</a>', '', html, flags=re.S)
    # leftover "Advertise here" / language variants as standalone links
    html = re.sub(r'<a href="[^"]*advertise/?"[^>]*>\s*(?:Advertise(?: here)?|Anúnciese(?: aquí)?|Anunciarse|Annoncer|Werbung)\s*</a>', '', html, flags=re.I)
    # field-guides footer pattern: · <a>Advertise</a>
    html = re.sub(r'<span>·</span><a href="[^"]*advertise/?">[^<]*</a>', '', html)
    if html != before:
        bump("html_stripped")
    return html


def add_preview_chrome(html: str) -> str:
    if "<html" not in html.lower():
        return html
    if re.search(r'<meta[^>]+name=["\']robots["\']', html, re.I):
        html = re.sub(
            r'<meta([^>]+)name=["\']robots["\']([^>]*)content=["\'][^"\']*["\']',
            r'<meta\1name="robots"\2content="noindex,nofollow"',
            html,
            count=1,
            flags=re.I,
        )
        # if robots had no content attr
        if 'content="noindex,nofollow"' not in html and 'name="robots"' in html:
            html = re.sub(
                r'<meta([^>]*)name=["\']robots["\']([^>]*)/?>',
                r'<meta\1name="robots"\2 content="noindex,nofollow">',
                html,
                count=1,
                flags=re.I,
            )
    else:
        html = re.sub(r'(<head[^>]*>)', r'\1\n<meta name="robots" content="noindex,nofollow">', html, count=1, flags=re.I)
    if 'class="ppc-preview-bar"' not in html:
        if re.search(r'<body[^>]*>', html, re.I):
            html = re.sub(r'(<body[^>]*>)', r'\1\n' + PREVIEW_BAR, html, count=1, flags=re.I)
    return html


def rewrite_special_html(path: Path, html: str) -> str:
    rel = path.as_posix()
    # about
    html = html.replace(
        '<h2 id="advertising">Advertising</h2>\n'
        '<p>The site shows ads served by Google AdSense and may load affiliate scripts such as Travelpayouts. Advertisers never change the policy information we publish. See our <a href="privacy.html">privacy policy</a> for how advertising cookies work and how to opt out of personalized ads.</p>',
        '<h2 id="affiliates-ads">How the site is funded</h2>\n'
        '<p>We do not currently show Google AdSense units on this site. Affiliate links are disclosed on the pages that use them and never change the policy information we publish. See our <a href="privacy.html">privacy policy</a>.</p>',
    )
    # contact
    html = html.replace(
        'content="Contact PetPolicyCheck for corrections to airline pet policy data, partnerships or sponsorship."',
        'content="Contact PetPolicyCheck for corrections to airline pet policy data, or to suggest a product for our guides."',
    )
    html = html.replace(
        '<h2>Partnerships &amp; sponsorship</h2>\n'
        '<p>Pet travel brands, insurers and travel companies interested in partnerships or sponsorship are welcome to get in touch. Sponsorship never changes the airline policy data we publish (see our <a href="about.html#affiliates">disclosure</a>).</p>',
        '<h2 id="suggest-a-product">Suggest a product</h2>\n'
        '<p>If you make a pet-travel product (a carrier, crate, or similar gear) and would like us to consider it for our product guides, email us with the product name, a link to the official page, and the official dimensions. A listing is not guaranteed; we compare official dimensions with airline limits and keep editorial independence (see our <a href="about.html#affiliates">disclosure</a>).</p>',
    )
    # privacy meta + section
    html = re.sub(
        r'content="Privacy policy for PetPolicyCheck: Google AdSense advertising cookies and how to opt out,([^"]*)"',
        r'content="Privacy policy for PetPolicyCheck: cookies,\1"',
        html,
    )
    html = html.replace(
        '<h2>Advertising (Google AdSense)</h2>\n'
        "<p>We use Google AdSense to show ads on this site. Third-party vendors, including Google, use cookies to serve ads based on a user's prior visits to this website or other websites. Google's use of advertising cookies enables it and its partners to serve ads to our users based on their visit to our site and/or other sites on the Internet.</p>\n"
        '<p>You may opt out of personalized advertising by visiting <a href="https://adssettings.google.com" rel="noopener" target="_blank">Google Ads Settings</a>. You can also opt out of some third-party vendors\' use of cookies for personalized advertising by visiting <a href="https://www.aboutads.info" rel="noopener" target="_blank">www.aboutads.info</a>. If you opt out, you may still see ads, but they won\'t be personalized.</p>',
        '<h2>Google AdSense</h2>\n'
        '<p>We do not currently load Google AdSense on these pages, so AdSense cookies are not set from this site today. Our publisher account may still appear in ads.txt. If we show AdSense units again, Google and its vendors may use cookies to show ads based on prior visits. You can use <a href="https://adssettings.google.com" rel="noopener" target="_blank">Google Ads Settings</a> and <a href="https://www.aboutads.info" rel="noopener" target="_blank">www.aboutads.info</a>. If you use those controls, any future units would not be personalized.</p>',
    )
    html = html.replace(
        'including by the advertising, analytics and affiliate services we use.',
        'including by the analytics and affiliate services we use.',
    )
    html = html.replace(
        'including by the advertising and affiliate services we use.',
        'including by the affiliate services we use.',
    )
    html = html.replace(
        'The third-party advertising, analytics and affiliate services described below',
        'The third-party analytics and affiliate services described below',
    )
    html = html.replace(
        'The third-party advertising and affiliate services described below',
        'The third-party affiliate services described below',
    )
    html = html.replace('not an advertising cookie', 'not an ad-network cookie')
    # insurance
    html = html.replace(
        'quote links will be marked &ldquo;sponsored&rdquo;;',
        'quote links will be marked as affiliate links;',
    )
    html = html.replace(
        'through links marked &ldquo;sponsored&rdquo; on this page.',
        'through affiliate links on this page.',
    )
    html = html.replace(' <span class="small">sponsored</span>', ' <span class="small">affiliate</span>')
    # partner-vets CTA heading
    html = html.replace('<h2>Are you a vet? Become a partner</h2>', '<h2>Are you a vet? List your clinic</h2>')
    # forum partners nav -> Suggest a product (contact)
    html = re.sub(
        r'<a href="[^"]*forum/partners\.html"[^>]*>Partners(?: &amp;| &| and)? Products</a>',
        '<a href="/contact.html#suggest-a-product">Suggest a product</a>',
        html,
    )
    # field-guides brand offer panel
    html = re.sub(
        r'\s*<section class="panel partner">.*?</section>',
        '',
        html,
        flags=re.S,
    )
    html = html.replace(
        'dedicated Paw Passport profile + priority partner perks.',
        'dedicated Paw Passport profile and credit on the guides.',
    )
    html = html.replace(
        'Partner names in seed slots are examples only, not current sponsors. They will be replaced by real human-approved submissions.',
        'Brand names in sample slots are examples only. They will be replaced by real human-approved submissions.',
    )
    return html


def skip_html(path: Path) -> bool:
    posix = path.as_posix()
    if "extension/unpacked" in posix:
        return True
    if path.suffix.lower() != ".html":
        return True
    return False


def process_html_tree(base: Path):
    for path in base.rglob("*.html"):
        if skip_html(path):
            continue
        rel = str(path.relative_to(ROOT))
        # replace offer pages with redirect
        if path.match("*/advertise/index.html") or path.name == "advertise.html" or path.match("*/forum/partners.html"):
            path.write_text(REDIRECT)
            bump("redirect_pages")
            continue
        raw = path.read_text(errors="replace")
        html = strip_ad_markup(raw)
        html = rewrite_special_html(path, html)
        html = add_preview_chrome(html)
        if html != raw:
            path.write_text(html)
            bump("html_written")


def patch_sitemap(path: Path):
    if not path.exists():
        return
    t = path.read_text()
    t2 = re.sub(r'<url><loc>https://petpolicycheck.com/advertise/</loc>.*?</url>', '', t)
    t2 = re.sub(r'<url><loc>https://petpolicycheck.com/forum/partners\.html</loc>.*?</url>', '', t2)
    t2 = re.sub(r'<url><loc>https://petpolicycheck.com/field-guides/advertise\.html</loc>.*?</url>', '', t2)
    if t2 != t:
        path.write_text(t2)
        bump("sitemap")


def patch_search_index(path: Path):
    if not path.exists():
        return
    data = json.loads(path.read_text())
    pages = data.get("pages")
    if not isinstance(pages, list):
        return
    new = []
    changed = False
    for item in pages:
        u = str(item.get("u") or "")
        if u.rstrip("/").endswith("/advertise") or "forum/partners" in u or u.endswith("advertise.html"):
            changed = True
            continue
        k = item.get("k")
        if isinstance(k, list):
            k2 = [x for x in k if not re.search(r'advertis|sponsor', str(x), re.I)]
            if k2 != k:
                item = dict(item)
                item["k"] = k2
                changed = True
        new.append(item)
    if changed:
        data["pages"] = new
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
        bump("search_index")


def patch_ui_js(path: Path):
    if not path.exists():
        return
    t = path.read_text()
    m = re.search(r"window\.PPC_I18N=(\{.*\});\s*$", t, re.S)
    if not m:
        print("WARNING: cannot parse", path)
        return
    obj = json.loads(m.group(1))
    drop = {"site.nav.advertise", "site.adhere", "site.partner.label", "site.partner.ph", "site.partner.cta"}
    changed = False
    for lang, strs in obj.get("strings", {}).items():
        for k in list(strs):
            if k in drop:
                del strs[k]
                changed = True
    if changed:
        path.write_text("window.PPC_I18N=" + json.dumps(obj, ensure_ascii=False, separators=(",", ":")) + ";\n")
        bump("ui_js")


def patch_forum_i18n(path: Path):
    if not path.exists():
        return
    t = path.read_text()
    # remove advertise / adhere keys from JSON-like objects
    t2 = re.sub(r',"site\.nav\.advertise":"[^"]*"', "", t)
    t2 = re.sub(r',"site\.adhere":"[^"]*"', "", t2)
    if t2 != t:
        path.write_text(t2)
        bump("forum_i18n")


def patch_es_ui_strings(path: Path):
    if not path.exists():
        return
    t = path.read_text()
    t2 = re.sub(r'\n\s*"Advertise":\s*"[^"]*",', "\n", t)
    if t2 != t:
        path.write_text(t2)
        bump("es_ui_strings")


def patch_pastilles(path: Path):
    if not path.exists():
        return
    t = path.read_text()
    t2 = t.replace(",Advertise:'Anúnciese'", "")
    t2 = t2.replace(
        "+'<a class=\"cta\" data-i18n=\"site.nav.advertise\" href=\"'+ppcHref('advertise/')+'\">'+plab('Advertise')+'</a>'",
        "",
    )
    if t2 != t:
        path.write_text(t2)
        bump("pastilles")


def patch_ugc(path: Path):
    if not path.exists():
        return
    t = path.read_text()
    orig = t
    # visible offer strings -> neutral or empty
    replacements = {
        "nav_adv:'Annonceurs'": "nav_adv:'Contact'",
        "nav_adv:'Anunciarse'": "nav_adv:'Contacto'",
        "nav_adv:'Werben'": "nav_adv:'Kontakt'",
        "nav_adv:'광고'": "nav_adv:'문의'",
        "nav_adv:'広告'": "nav_adv:'お問い合わせ'",
        "c_pdept:'Pour les marques animales · emplacements natifs relus par un humain'": "c_pdept:''",
        "c_ph:'Sponsoriser un épisode · Devenir partenaire'": "c_ph:''",
        "c_pl2:'Ensuite : sponsoring d’épisode payant, facturé manuellement'": "c_pl2:''",
        "c_pl3:'Toujours balisé « Sponsorisé » ; le contenu réglementaire reste indépendant'": "c_pl3:''",
        "c_pcta:'Sponsoriser un épisode · Devenir partenaire →'": "c_pcta:''",
        "c_disc:'Exemple : les épisodes d’exemple illustrent de vraies règles Vague A ; les @pseudos sont des exemples génériques, pas de vrais comptes. Les marques des emplacements d’exemple ne sont pas des sponsors actuels.'": "c_disc:'Exemple : les épisodes d’exemple illustrent de vraies règles Vague A ; les @pseudos sont des exemples génériques, pas de vrais comptes.'",
        "c_pdept:'Para marcas de mascotas · espacios nativos revisados'": "c_pdept:''",
        "c_ph:'Patrocinar un episodio · Ser socio'": "c_ph:''",
        "c_pl2:'Después: patrocinio de episodio con facturación manual'": "c_pl2:''",
        "c_pl3:'Siempre etiquetado « Patrocinado »; las reglas oficiales se mantienen independientes'": "c_pl3:''",
        "c_pcta:'Patrocinar un episodio · Ser socio →'": "c_pcta:''",
        "c_pdept:'Für Heimtiermarken · native, geprüfte Platzierungen'": "c_pdept:''",
        "c_ph:'Episode sponsern · Partner werden'": "c_ph:''",
        "c_pl2:'Danach: bezahltes Episoden-Sponsoring auf manuelle Rechnung'": "c_pl2:''",
        "c_pl3:'Immer als „Gesponsert“ gekennzeichnet; Regelwerke bleiben unabhängig'": "c_pl3:''",
        "c_pcta:'Episode sponsern · Partner werden →'": "c_pcta:''",
        "c_pdept:'펫 브랜드용 · 네이티브, 사람 검토 플레이스먼트'": "c_pdept:''",
        "c_ph:'에피소드 스폰서 · 파트너 되기'": "c_ph:''",
        "c_pl2:'이후: 유료 에피소드 스폰서십, 수동 청구'": "c_pl2:''",
        "c_pl3:'항상 “Sponsored” 표기; 정책 콘텐츠는 독립 유지'": "c_pl3:''",
        "c_pcta:'에피소드 스폰서 · 파트너 되기 →'": "c_pcta:''",
        "c_pdept:'ペットブランド向け · ネイティブ、人確認の掲載'": "c_pdept:''",
        "c_ph:'エピソードをスポンサー · パートナーになる'": "c_ph:''",
        "c_pl2:'その後：有料エピソードスポンサー、手動請求'": "c_pl2:''",
        "c_pl3:'常に「Sponsored」表示；政策コンテンツは独立'": "c_pl3:''",
        "c_pcta:'エピソードをスポンサー · パートナーになる →'": "c_pcta:''",
        "sponsored:'Sponsored · Example'": "sponsored:''",
        "sponsored:'Sponsorisé · Exemple'": "sponsored:''",
        "sponsored:'Patrocinado · Ejemplo'": "sponsored:''",
        "sponsored:'Gesponsert · Beispiel'": "sponsored:''",
        "sponsored:'스폰서 · 예시'": "sponsored:''",
        "sponsored:'スポンサー · 例'": "sponsored:''",
        "openslot:'Open sponsor slot on this episode.'": "openslot:''",
        "opencta:'Sponsor an episode / Become a partner →'": "opencta:''",
        "openslot:'Emplacement sponsor libre sur cet épisode.'": "openslot:''",
        "opencta:'Sponsoriser un épisode / Devenir partenaire →'": "opencta:''",
        "openslot:'Espacio patrocinador libre en este episodio.'": "openslot:''",
        "opencta:'Patrocinar un episodio / Ser socio →'": "opencta:''",
        "openslot:'Freier Sponsorenplatz in dieser Episode.'": "openslot:''",
        "opencta:'Episode sponsern / Partner werden →'": "opencta:''",
        "openslot:'이 에피소드 스폰서 자리 열림.'": "openslot:''",
        "opencta:'에피소드 스폰서 / 파트너 되기 →'": "opencta:''",
        "openslot:'このエピソードのスポンサースロット空き'": "openslot:''",
        "opencta:'エピソードをスポンサー / パートナーになる →'": "opencta:''",
        "var SPONSOR_LABEL={none:'None · Open slot CTA',winwin:'Win-Win Gear',paid:'Paid Sponsor'};":
            "var SPONSOR_LABEL={none:'None',winwin:'Gear mention',paid:'Product mention'};",
    }
    for a, b in replacements.items():
        if a in t:
            t = t.replace(a, b)
    # hide rendered brand-slot / open CTAs
    t = re.sub(
        r"function sponsorBlock\(it,compact\)\{",
        "function sponsorBlock(it,compact){ return ''; /* brand-slot UI removed for preview */\n  if(false){",
        t,
        count=1,
    )
    # close the if(false) — original function should still be syntactically valid if we wrap... risky.
    # Better: replace the whole function.
    t = re.sub(
        r"function sponsorBlock\(it,compact\)\{ return ''; /\* brand-slot UI removed for preview \*/\n  if\(false\)\{[\s\S]*?\n\}",
        "function sponsorBlock(it,compact){ return ''; }",
        t,
        count=1,
    )
    # if the wrap failed, try replacing original function only
    if "function sponsorBlock(it,compact){ return ''; }" not in t:
        t = re.sub(
            r"function sponsorBlock\(it,compact\)\{\n[\s\S]*?\n\}\n",
            "function sponsorBlock(it,compact){ return ''; }\n",
            t,
            count=1,
        )
    t = t.replace('href="advertise.html"', 'href="../contact.html#suggest-a-product"')
    t = t.replace("href='advertise.html'", "href='../contact.html#suggest-a-product'")
    # drop remaining visible English offer phrases if any
    t = t.replace("Paid Sponsor", "Product mention")
    t = t.replace("Win-Win Gear Partner", "Product mention")
    t = t.replace("Example partner slot", "Example product mention")
    t = t.replace("Open slot CTA", "Contact")
    t = t.replace("Sponsor slot", "Product mention")
    t = t.replace("Sponsor: ", "Mention: ")
    if t != orig:
        path.write_text(t)
        bump("ugc_js")
    else:
        print("WARNING: ugc.js unchanged", path)


def write_docs():
    (ROOT / "docs" / "paddle-noads-reversible.md").write_text(
        """# Paddle no-ads preview — how to restore ad panels

This branch is a **local preview**. Nothing is published until Marc types « publie ».

## Switch

In `build.py`, set `SHOW_ADS = True` and restore the HTML from `origin/main` (or revert this commit). Do **not** run `python3 build.py` without checking: `main()` deletes `site/` first (`shutil.rmtree(OUT)`), which would drop pages that were added outside that generator.

## What this preview removed (to restore later)

1. **Google AdSense units (kept the account and `ads.txt`)**
   - Head script: `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7693501377730690`
   - Header band: three 300×250 units, slot `4584637408` (`adsense_header_slot`)
   - Homepage mid/bottom bands: slot `9881497431` (`adsense_home_footer_slot`) and `home_mid`
   - Site footer band: slot `2114688057` (`ads.site_footer.adsense_slot`)
   - Empty placeholder cells labelled “Advertisement / Advertise here” (`sidebar_or_footer` and others)
   - Build helpers: `header_ad`, `home_footer_ad`, `site_footer_ad`, `ad_frame`, `ad_slot`, `ad_grid`, `medium_rect_*`, `ad_ph`

2. **Brand-ad offer and every public link to it**
   - `/advertise/` (media kit: placements, audience, rates on request) → noindex redirect to `/contact.html#suggest-a-product`
   - `/field-guides/advertise.html` → same redirect
   - `/forum/partners.html` (free promotional thread in exchange for a backlink) → same redirect
   - Homepage mid-page band “Reach pet parents planning a trip / Advertise here” (and the ES equivalent)
   - Homepage / menu CTA “Advertise” (`pastilles.js` + home nav)
   - Footer “Advertise” / “Anúnciese” and “Advertise here” under footer units
   - Top “Your brand here · Become a PetPolicyCheck partner” placeholder (`partner-banner.js`, `assets/partners/top-partner.json` left in the tree, unused)
   - Field Guides “Sponsor an episode · Become a partner” panel and open-slot CTAs (`ugc.js`)

3. **Copy that sold ads**, reworded on About, Contact, Privacy, insurance disclosures, i18n, and the search index.

## Left untouched

- `site/ads.txt` (Google publisher `pub-7693501377730690`)
- Amazon Associates and other **affiliate** links / disclosures (including `rel="sponsored"` on those links)
- `.lbadge`, and the tokens `--bg`, `--paper`, `--ink`
- Travelpayouts / booking affiliate scripts
"""
    )


def main():
    patch_build_py()
    for tree in (ROOT / "site", ROOT / "static"):
        if tree.exists():
            process_html_tree(tree)
    for sm in (ROOT / "site" / "sitemap.xml", ROOT / "static" / "sitemap.xml"):
        patch_sitemap(sm)
    for idx in ROOT.glob("*/assets/search-index*.json"):
        patch_search_index(idx)
    for ui in (ROOT / "site" / "assets" / "i18n" / "ui.js", ROOT / "static" / "assets" / "i18n" / "ui.js"):
        patch_ui_js(ui)
    for fi in (ROOT / "site" / "forum" / "i18n.js", ROOT / "static" / "forum" / "i18n.js"):
        patch_forum_i18n(fi)
    for es in (ROOT / "site" / "es" / "ui_strings_es.json", ROOT / "static" / "es" / "ui_strings_es.json"):
        patch_es_ui_strings(es)
    for pst in (ROOT / "site" / "assets" / "js" / "pastilles.js", ROOT / "static" / "assets" / "js" / "pastilles.js"):
        patch_pastilles(pst)
    for ugc in (ROOT / "site" / "field-guides" / "ugc.js", ROOT / "static" / "field-guides" / "ugc.js"):
        patch_ugc(ugc)
    write_docs()
    print("STATS", json.dumps(STATS, indent=2))


if __name__ == "__main__":
    main()
