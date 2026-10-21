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


def page(cfg, title, desc, body, path, root, jsonld=None, canonical=None):
    base = cfg["base_url"].rstrip("/")
    canon = canonical or f"{base}/{path}"
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    return f"""<!doctype html>
<html lang="{e(cfg.get('language','en'))}">
<head>
<meta charset="utf-8">
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
<nav><a href="{root}index.html">Compare</a><a href="{root}updates.html">Updates</a><a href="{root}about.html">About</a></nav>
</div></header>
<main class="wrap">
{body.replace('{root}', root)}
</main>
<footer class="foot"><div class="wrap">
<p>Airline pet rules change often. Always confirm with the airline before you book. Information here is not legal or veterinary advice.</p>
<p>&copy; {dt.date.today().year} {e(cfg['site_name'])} &middot; <a href="{root}about.html">About &amp; disclaimer</a> &middot; <a href="{root}updates.html">Updates</a></p>
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
    ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": cfg["site_name"], "url": cfg["base_url"]},
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "name": f"{a['name']} pet policy",
               "url": f"{cfg['base_url'].rstrip('/')}/airlines/{a['slug']}.html"} for i, a in enumerate(airlines)]}]
    return page(cfg, f"Airline pet policies compared (in-cabin dogs & cats): verified {nice_date(newest)}",
                "Compare in-cabin pet rules, carrier sizes, weight limits and fees for major airlines, each checked against the official airline page with a last-verified date.",
                body, "index.html", "", ld, canonical=cfg["base_url"].rstrip("/") + "/")


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


def build_airline(cfg, a):
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
<h1>{e(a['name'])} pet policy</h1>
{verified_line}
{status}{review}
<table class="facts"><tbody>{rows}</tbody></table>
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
<p>Spotted something out of date? {('Email <a href="mailto:'+e(cfg['contact_email'])+'">'+e(cfg['contact_email'])+'</a>.') if cfg.get('contact_email') else 'A contact address will be added soon.'}</p>"""
    return page(cfg, f"About & disclaimer | {cfg['site_name']}", "How we verify airline pet policies, our disclaimer and affiliate disclosure.", body, "about.html", "")


def main():
    cfg, airlines, updates = load()
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "airlines").mkdir(parents=True)
    shutil.copy(ROOT / "static" / "style.css", OUT / "style.css")
    (OUT / ".nojekyll").write_text("")
    (OUT / "index.html").write_text(build_index(cfg, airlines))
    for a in airlines:
        (OUT / "airlines" / f"{a['slug']}.html").write_text(build_airline(cfg, a))
    (OUT / "updates.html").write_text(build_updates(cfg, airlines, updates))
    (OUT / "about.html").write_text(build_about(cfg))
    base = cfg["base_url"].rstrip("/")
    newest = max(a["last_verified"] for a in airlines if a.get("last_verified"))
    urls = [(f"{base}/", newest), (f"{base}/updates.html", newest), (f"{base}/about.html", newest)]
    urls += [(f"{base}/airlines/{a['slug']}.html", a.get("last_verified") or a.get("last_checked") or newest) for a in airlines]
    sm = "".join(f"<url><loc>{e(u)}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    print(f"Built {len(airlines)} airline pages -> {OUT}")
    for a in airlines:
        print(f"  {a['slug']:16} confirmed {confirmed_count(a)}/{len(FIELDS)}  status={a.get('fetch_status')}")


if __name__ == "__main__":
    main()
