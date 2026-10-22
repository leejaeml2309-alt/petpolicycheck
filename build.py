#!/usr/bin/env python3
"""Static site generator for the airline pet policy directory.

Stdlib only. Reads config.json + data/airlines/*.json + data/updates.json,
writes the site to ./site/.  Usage:  python3 build.py
"""
import datetime as dt
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
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


def val(a, key):
    v = a.get(key)
    if key == "in_cabin_allowed":
        return e(yn(v))
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


def page(cfg, title, desc, body, path, root, jsonld=None, canonical=None):
    base = site_base(cfg)
    canon = canonical or f"{base}/{path}"
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    return f"""<!doctype html>
<html lang="{e(cfg.get('language','en'))}">
<head>
<meta charset="utf-8">
<meta name="impact-site-verification" value="60bdcaa0-2f59-492a-85f2-bf25a93a4644">
{ADSENSE}
{TP_DRIVE}
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canon)}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{e(canon)}">
<meta name="twitter:card" content="summary">
<link rel="stylesheet" href="{root}style.css">
{ld}
</head>
<body>
<header class="top"><div class="wrap">
<a class="brand" href="{root}index.html">{e(cfg['site_name'])}</a>
<nav><a href="{root}index.html">Compare</a><a href="{root}products/">Products</a><a href="{root}updates.html">Updates</a><a href="{root}about.html">About</a><a href="{root}advertise/">Advertise</a></nav>
</div></header>
<main class="wrap">
{body.replace('{root}', root)}
</main>
<footer class="foot"><div class="wrap">
{ad_slot(cfg, "sidebar_or_footer", root)}
<p>Airline pet rules change often. Always confirm with the airline before you book. Information here is not legal or veterinary advice.</p>
<p class="disc">Some links may be affiliate links; we may earn a commission at no extra cost to you. This never affects our data.</p>
<p>&copy; {dt.date.today().year} {e(cfg['site_name'])} &middot; <a href="{root}about.html">About &amp; disclaimer</a> &middot; <a href="{root}products/">Products</a> &middot; <a href="{root}updates.html">Updates</a> &middot; <a href="{root}advertise/">Advertise</a> &middot; <a href="{root}privacy.html">Privacy</a> &middot; <a href="{root}contact.html">Contact</a></p>
</div></footer>
</body></html>
"""


def build_index(cfg, airlines):
    rows = []
    for a in airlines:
        rows.append(f"""<tr>
<td data-l="Airline"><a href="airlines/{a['slug']}.html">{e(a['name'])}</a></td>
<td data-l="In cabin">{e(yn(a.get('in_cabin_allowed')))}</td>
<td data-l="Max carrier">{val(a,'max_carrier_dimensions')}</td>
<td data-l="Max weight">{val(a,'max_combined_weight')}</td>
<td data-l="Fee (from)">{e(short_fee(a)) if a.get('fees') else val(a,'fees')}</td>
<td data-l="Hold / cargo">{val(a,'checked_or_cargo')}</td>
<td data-l="Verified">{f'<time datetime="{e(a["last_verified"])}">{e(nice_date(a["last_verified"]))}</time>' if a.get('last_verified') else 'Not verified'}{' <span class="flag">official page blocked</span>' if a.get('fetch_status')=='blocked' else ''}</td>
</tr>""")
    newest = max(a["last_verified"] for a in airlines if a.get("last_verified"))
    body = f"""
<section class="hero">
<h1>Flying with a dog or cat? Airline pet policies, verified.</h1>
<p>{e(cfg.get('site_tagline',''))} Every airline page shows the date we last checked the <b>official</b> policy page and links to it. If we couldn't confirm a detail, we say so instead of guessing.</p>
<p class="small">Most recent check: <time datetime="{newest}">{nice_date(newest)}</time> &middot; {len(airlines)} airlines</p>
</section>
<div class="tablewrap"><table class="cmp">
<thead><tr><th>Airline</th><th>In cabin</th><th>Max carrier</th><th>Max weight</th><th>Fee (from)</th><th>Hold / cargo</th><th>Last verified</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
<p class="small">"{CHECK}" means the detail was not stated on, or could not be read from, the airline's official page on the date shown.</p>
{affiliate_box(cfg)}
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
{f"<h2>Good to know</h2><p>{e(a['notes'])}</p>" if a.get('notes') else ''}
<h2>Recent changes</h2>
{f"<ul class='changes'>{ch}</ul>" if ch else "<p>No dated changes recorded yet. We log changes here when we detect them.</p>"}
<p class="small">Before you book, re-check the <a href="{e(a['official_url'])}" rel="noopener" target="_blank">official page</a> and call the airline to reserve pet space; space is usually limited per flight.</p>
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
<p>Some pages may contain affiliate links (for example to pet carriers or pet insurance). If you buy through them we may earn a commission at no extra cost to you. Affiliate relationships never change the policy information we publish.</p>
<h2>Corrections</h2>
<p>Spotted something out of date? Please tell us via our <a href="contact.html">contact page</a>.</p>"""
    return page(cfg, f"About & disclaimer | {cfg['site_name']}", "How we verify airline pet policies, our disclaimer and affiliate disclosure.", body, "about.html", "")


def obf_mail(addr):
    """Mailto link with every character as an HTML entity: clickable, no JS, hidden from naive scrapers."""
    ent = lambda t: "".join(f"&#{ord(ch)};" for ch in t)
    return f'<a href="{ent("mailto:" + addr)}">{ent(addr)}</a>'


EFFECTIVE = "October 22, 2026"


def build_privacy(cfg):
    mail = obf_mail(cfg["contact_email"])
    body = f"""<h1>Privacy policy</h1>
<p class="small">Effective date: {EFFECTIVE}</p>
<p>{e(cfg['site_name'])} is a simple static website. This page explains, in plain English, what data is and isn't collected when you visit.</p>
<h2>No accounts, no forms</h2>
<p>There are no user accounts, logins, comment forms or newsletters on this site. We don't ask for, and don't store, your name, email or any other personal information. If you email us, we only use your message and address to reply.</p>
<h2>Hosting (GitHub Pages)</h2>
<p>The site is hosted on GitHub Pages, a service of GitHub, Inc. When you load a page, GitHub's servers may log technical information such as your IP address, browser type and the page requested, for security and operations. We don't receive or control those logs. See the <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener" target="_blank">GitHub Privacy Statement</a>.</p>
<h2>Analytics</h2>
<p>We currently use <b>no analytics, tracking pixels or advertising scripts</b>, and the site itself sets no cookies.</p>
<div class="note" id="analytics-update"><b>Update note:</b> if we add an analytics tool in the future, this section will be updated before it goes live to name the tool, what it collects, and how to opt out, and the effective date above will change.</div>
<h2>Affiliate links and partner cookies</h2>
<p>Some pages may include affiliate links to partners, for example brands on the Impact network (such as Chewy, Trupanion or Lemonade) and Booking.com. If you click one, you leave our site and the partner (or its affiliate network) may set cookies or use similar technology to record that the visit came from us, so we can be paid a commission if you buy something. Those cookies are governed by the partner's own privacy policy, not ours. You can block or delete cookies in your browser settings. We don't receive personal information about you from these partners, only aggregated sales or commission reports.</p>
<h2>External links</h2>
<p>We link to airline and government websites. Their privacy practices are their own.</p>
<h2>Children</h2>
<p>This site is not directed at children and does not knowingly collect information from anyone.</p>
<h2>Changes</h2>
<p>If this policy changes, we'll update this page and its effective date.</p>
<h2>Contact</h2>
<p>Questions about privacy: {mail}.</p>"""
    return page(cfg, f"Privacy policy | {cfg['site_name']}", "Privacy policy for PetPolicyCheck: no accounts, no analytics, GitHub Pages hosting and affiliate partner cookies explained.", body, "privacy.html", "")


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
        "hard_crate": "Hard crates for the hold / cargo", "bowl": "Travel bowls"}
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


def ad_slot(cfg, key, root):
    s = (cfg.get("ads") or {}).get(key) or {}
    if s.get("image_url") and s.get("link_url"):
        adv = f'<span class="small"> &middot; {e(s.get("advertiser"))}</span>' if s.get("advertiser") else ""
        return (f'<aside class="ad ad-{e(key)}"><span class="adlabel">Sponsored</span>{adv}'
                f'<a href="{e(s["link_url"])}" rel="sponsored nofollow noopener" target="_blank">'
                f'<img src="{e(s["image_url"])}" alt="{e(s.get("alt") or s.get("advertiser") or "Sponsor")}" loading="lazy"></a></aside>')
    return f'<p class="adph"><a href="{root}advertise/">Advertise here</a></p>'


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


def buy_links(cfg, p):
    slot = (cfg.get("product_links") or {}).get(p["slug"]) or {}
    out = []
    if slot.get("amazon_url"):
        out.append(f'<a class="btn" href="{e(slot["amazon_url"])}" rel="sponsored nofollow noopener" target="_blank">View at Amazon</a>')
    if slot.get("chewy_url"):
        out.append(f'<a class="btn" href="{e(slot["chewy_url"])}" rel="sponsored nofollow noopener" target="_blank">View at Chewy</a>')
    if not out:
        out.append(f'<a class="btn" href="{e(p["official_url"])}" rel="noopener" target="_blank">View on the official {e(p["brand"])} site</a>')
    return '<p class="buy">' + " ".join(out) + "</p>"


def disclosure(root):
    return (f'<p class="disc small">Affiliate disclosure: some links on this page may be affiliate links; if you buy through them we may earn a commission at no extra cost to you. '
            f'It never changes the dimensions or fit results shown. We have not tested these products ourselves: every figure comes from the linked manufacturer page. '
            f'<a href="{root}about.html#affiliates">Disclosure</a>.</p>')


def verified_p(p, v, root):
    return (f'<p class="verified">&#10003; Dimensions checked <time datetime="{v}">{nice_date(v)}</time> against the '
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
           "hard_crate": ["iata-hard-crates-for-cargo"], "bowl": ["travel-water-bowls"]}[p["category"]]
    rl = "".join(f"<li><a href='{g}.html'>{e(GUIDE_META[g][0])}</a></li>" for g in rel)
    sib = "".join(f"<li><a href='{q['slug']}.html'>{e(q['name'])}</a></li>" for q in pd["products"] if q["category"] == p["category"] and q is not p)
    body = f"""{crumbs("{root}", p['name'])}
<h1>{e(p['name'])}: dimensions{' and airline under-seat fit' if p['category'] in ('soft_carrier','backpack') else ''}</h1>
{verified_p(p, v, root)}
{buy_links(cfg, p)}
<h2>Dimensions</h2>
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
    t = f"{p['name']}: dimensions" + (" & which airlines it fits under-seat" if faqs else "") + f" | {cfg['site_name']}"
    d = f"{p['name']} dimensions from the official {p['brand']} page" + (", compared with the cabin carrier limits of major airlines." if faqs else ", with links to airline pet rules.")
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
}


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
    else:
        bw = [p for p in P if p["category"] == "bowl"]
        tr = "".join(f"<tr><td data-l='Bowl'>{plink(p)}</td><td data-l='Size'>{e(a)}</td><td data-l='Specs'>{e(b)}</td></tr>" for p in bw for a, b in p["spec_rows"])
        cards = "".join(f"<h3>{plink(p)}</h3><p>{e(p.get('construction') or '')}. {e(' '.join(p.get('maker_says', [])))}</p>" for p in bw)
        main = f"""<p>A collapsible or nesting bowl lets you offer water during layovers. Sizes and capacities below are from each maker's official page.</p>
<div class="tablewrap"><table class="cmp"><thead><tr><th>Bowl</th><th>Size</th><th>Specs (per maker)</th></tr></thead><tbody>{tr}</tbody></table></div>{cards}"""
    other = "".join(f"<li><a href='{s}.html'>{e(GUIDE_META[s][0])}</a></li>" for s in GUIDE_META if s != slug)
    body = f"""{crumbs("{root}", title.split(':')[0])}
<h1>{e(title)}</h1>
<p class="verified">&#10003; Product dimensions checked <time datetime="{v}">{nice_date(v)}</time> against each manufacturer's official page; airline limits from our dated airline pages.</p>
{ad_slot(cfg, 'guide_sponsor', '{root}')}
{main}
<h2>More guides</h2><ul>{other}<li><a href="{{root}}products/">All pet travel products</a></li></ul>
{disclosure("{root}")}
"""
    ld = [bc_ld(cfg, [("Home", ""), ("Products", "products/"), (title.split(':')[0], f"products/{slug}.html")])]
    return page(cfg, f"{title} | {cfg['site_name']}", desc, body, f"products/{slug}.html", root, ld)


def build_products_index(cfg, pd, lims):
    root = "../"
    gl = "".join(f"<li><a href='{g['slug']}.html'>{e(GUIDE_META[g['slug']][0])}</a><br><span class='small'>{e(GUIDE_META[g['slug']][1])}</span></li>" for g in pd["guides"])
    secs = ""
    for c, lbl in CATS.items():
        ps = [p for p in pd["products"] if p["category"] == c]
        if not ps:
            continue
        li = ""
        for p in ps:
            if c in ("soft_carrier", "backpack"):
                best = max((len(ok) for _, ok in fits_list(p, lims)), default=0)
                n = len(applicable(p, lims))
                info = f"within {best} of {n} airline cabin limits (best size)"
            elif c == "hard_crate":
                info = f"{len(p['sizes'])} sizes, interior dimensions"
            else:
                info = "; ".join(f"{a}: {b}" for a, b in p["spec_rows"])[:90]
            li += f"<li><a href='{p['slug']}.html'>{e(p['name'])}</a> <span class='small'>&middot; {e(info)}</span></li>"
        secs += f"<h2>{e(lbl)}</h2><ul class='plist'>{li}</ul>"
    body = f"""{crumbs("{root}")}
<h1>Pet travel gear: carriers, crates and bowls, checked against airline limits</h1>
<p>Dimensions for each product come from the manufacturer's official page (linked and dated), and we compare them with the cabin carrier limits on our <a href="{{root}}index.html">airline pet policy pages</a>. No prices, ratings or hands-on test claims: just published numbers you can check.</p>
<h2>Guides</h2><ul class="plist">{gl}</ul>
{secs}
{disclosure("{root}")}
"""
    ld = [bc_ld(cfg, [("Home", ""), ("Products", "products/")]),
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": p["name"], "url": f"{site_base(cfg)}/products/{p['slug']}.html"}
              for i, p in enumerate(pd["products"])]}]
    return page(cfg, f"Pet travel carriers & crates: which fit airline under-seat limits | {cfg['site_name']}",
                "Pet carriers, hard crates and travel bowls with official manufacturer dimensions, compared with airline cabin carrier limits.",
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
<p class="small">Every placement is clearly labelled "Sponsored" and links with rel="sponsored nofollow". One advertiser per placement at a time. Images only (PNG, JPG or WebP); no pop-ups, auto-play or tracking scripts.</p>
<h2>Good fit for</h2>
<ul><li>Pet carrier, crate and travel gear brands</li><li>Pet insurance</li><li>Pet relocation and pet shipping services</li><li>Pet-friendly hotels and travel services</li></ul>
<h2>Editorial independence</h2>
<p>Sponsors never change our airline data, dimensions or fit results, and sponsored products get no special placement in guides (see our <a href="{{root}}about.html#affiliates">disclosure</a>).</p>
<h2>Rates and booking</h2>
<p><b>Rates on request.</b> Email {mail} with your brand, the placement you're interested in and your dates.</p>"""
    return page(cfg, f"Advertise on {cfg['site_name']}: reach pet owners planning to fly",
                "Sponsorship and banner placements on PetPolicyCheck for pet carrier brands, pet insurance, pet relocation and pet-friendly travel. Rates on request.",
                body, "advertise/", "../")


def main():
    cfg, airlines, updates = load()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "airlines").mkdir(parents=True)
    (OUT / "products").mkdir()
    (OUT / "advertise").mkdir()
    pd, lims = load_products(airlines)
    shutil.copy(ROOT / "static" / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").write_text("")
    if custom_domain(cfg):
        (OUT / "CNAME").write_text(custom_domain(cfg) + "\n")
    (OUT / "index.html").write_text(build_index(cfg, airlines))
    for a in airlines:
        (OUT / "airlines" / f"{a['slug']}.html").write_text(build_airline(cfg, a, pd, lims))
    (OUT / "updates.html").write_text(build_updates(cfg, airlines, updates))
    (OUT / "about.html").write_text(build_about(cfg))
    (OUT / "privacy.html").write_text(build_privacy(cfg))
    (OUT / "contact.html").write_text(build_contact(cfg))
    (OUT / "advertise" / "index.html").write_text(build_advertise(cfg))
    (OUT / "products" / "index.html").write_text(build_products_index(cfg, pd, lims))
    for p in pd["products"]:
        (OUT / "products" / f"{p['slug']}.html").write_text(build_product(cfg, p, pd, lims, airlines))
    for g in pd["guides"]:
        (OUT / "products" / f"{g['slug']}.html").write_text(build_guide(cfg, g, pd, lims, airlines))
    base = site_base(cfg)
    newest = max(a["last_verified"] for a in airlines if a.get("last_verified"))
    urls = [(f"{base}/", newest), (f"{base}/updates.html", newest), (f"{base}/about.html", newest),
            (f"{base}/privacy.html", newest), (f"{base}/contact.html", newest), (f"{base}/advertise/", newest),
            (f"{base}/products/", pd["verified"])]
    urls += [(f"{base}/products/{x['slug']}.html", pd["verified"]) for x in pd["products"] + pd["guides"]]
    urls += [(f"{base}/airlines/{a['slug']}.html", a.get("last_verified") or a.get("last_checked") or newest) for a in airlines]
    sm = "".join(f"<url><loc>{e(u)}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (OUT / "ads.txt").write_text("google.com, pub-7693501377730690, DIRECT, f08c47fec0942fa0\n")
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    print(f"Built {len(airlines)} airline pages, {len(pd['products'])} products, {len(pd['guides'])} guides, {len(lims)} cabin limits -> {OUT}")
    for a in airlines:
        print(f"  {a['slug']:16} confirmed {confirmed_count(a)}/{len(FIELDS)}  status={a.get('fetch_status')}")


if __name__ == "__main__":
    main()
