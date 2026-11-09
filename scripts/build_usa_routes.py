#!/usr/bin/env python3
"""Build 5 USA↔country overview route pages (local preview). EN only."""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path("/workspace/routes-usa-20261109/data/routes.json")
SHELL = ROOT / "site/routes/usa-to-japan.html"
# After first run SHELL may already be updated; prefer the before-backup when present.
BEFORE = Path("/tmp/usa-to-japan-BEFORE.html")

# JSON slug -> live filename (Japan keeps existing live slug)
SLUG_FILE = {
    "usa-canada": "usa-canada.html",
    "usa-mexico": "usa-mexico.html",
    "usa-uk": "usa-uk.html",
    "usa-japan": "usa-to-japan.html",
    "usa-france": "usa-france.html",
}

DEST_LABEL = {
    "usa-canada": "Canada",
    "usa-mexico": "Mexico",
    "usa-uk": "Great Britain",
    "usa-japan": "Japan",
    "usa-france": "France",
}

CRUMB_LABEL = {
    "usa-canada": "USA ↔ Canada",
    "usa-mexico": "USA ↔ Mexico",
    "usa-uk": "USA ↔ United Kingdom",
    "usa-japan": "USA ↔ Japan",
    "usa-france": "USA ↔ France",
}

PAGE_STYLE = """
<style>
.usa-quick{background:var(--sage-l);border:0;border-left:4px solid var(--sage);border-radius:10px;padding:14px 18px}
.usa-quick h2{margin:0 0 .4em}.usa-quick ul{margin:0;padding-left:1.2em}.usa-quick li{margin:.35em 0}
.usa-warn{border:0;border-left:4px solid var(--gold)}
.usa-t .usa-src{white-space:nowrap}
.checklist{background:var(--sage-l,#e7efe9);border-radius:10px;padding:14px 18px;margin:1em 0}
.checklist ul{margin:.4em 0 0;padding-left:1.2em}
.badge-off{display:inline-block;font-size:.72em;font-weight:700;letter-spacing:.02em;text-transform:uppercase;background:var(--sage-l,#e7efe9);color:var(--ink,#0b1719);border:1px solid var(--sage,#6d8f7b);border-radius:6px;padding:1px 6px;margin-right:4px}
.faq details{border:1px solid var(--line,#d9d4c7);border-radius:10px;padding:10px 14px;margin:.5em 0;background:#fff}
.faq summary{cursor:pointer;font-weight:600}
.pv-bar{background:#7a1f1f;color:#fff;font:600 14px/1.4 system-ui,sans-serif;padding:8px 14px;text-align:center;position:sticky;top:0;z-index:9999}
.pv-bar a{color:#fff;text-decoration:underline}
.ppc-links h3{margin:1.1em 0 .35em;font-size:1.02em}
.ppc-links ul{margin:.2em 0 .8em;padding-left:1.2em}
@media (max-width:720px){.usa-t .usa-src{white-space:normal}}
</style>
"""


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def abs_to_rel(url: str) -> str:
    """Map petpolicycheck.com absolute URLs to site-relative from /routes/."""
    prefix = "https://petpolicycheck.com/"
    if url.startswith(prefix):
        path = url[len(prefix) :]
        if path.startswith("routes/"):
            return path[len("routes/") :]  # sibling in routes/
        return "../" + path
    return url


def claim_li(item: dict) -> str:
    src = item.get("source_url") or ""
    title = item.get("source_title") or "Source"
    checked = item.get("checked") or "Nov 9, 2026"
    label = item.get("label") or "Official rule"
    text = item.get("text") or ""
    src_html = ""
    if src:
        src_html = f' <a href="{esc(src)}" rel="noopener" target="_blank">Source</a>'
    return (
        f'<li><span class="badge-off">{esc(label)}</span> {esc(text)}'
        f'{src_html} <span class="small">Checked {esc(checked)}</span></li>'
    )


def claim_row(item: dict) -> str:
    src = item.get("source_url") or ""
    short = (item.get("source_title") or "Source").split(":")[0].strip()
    # Prefer short agency name
    for key, name in [
        ("aphis", "USDA APHIS"),
        ("cdc", "CDC"),
        ("cfia", "CFIA"),
        ("cbsa", "CBSA"),
        ("senasica", "SENASICA"),
        ("defra", "DEFRA"),
        ("gov.uk", "GOV.UK"),
        ("maff", "Japan AQS"),
        ("aqs", "Japan AQS"),
        ("europa", "European Commission"),
        ("agriculture.gouv", "France Ministry"),
    ]:
        u = (src or "").lower()
        t = (item.get("source_title") or "").lower()
        if key in u or key in t:
            short = name
            break
    checked = item.get("checked") or "Nov 9, 2026"
    text = item.get("text") or ""
    if src:
        src_cell = (
            f"<a href=\"{esc(src)}\" rel=\"noopener\" target=\"_blank\">{esc(short)}</a>"
            f"<br><span class=\"small\">Checked {esc(checked)}</span>"
        )
    else:
        src_cell = f"<span class=\"small\">Checked {esc(checked)}</span>"
    return (
        f"<tr><td data-l='Rule'>{esc(text)}</td>"
        f"<td class='usa-src' data-l='Source'>{src_cell}</td></tr>"
    )


def timeline_rows(items: list) -> str:
    rows = []
    for it in items:
        when = it.get("when") or it.get("time") or ""
        what = it.get("what") or it.get("text") or ""
        rows.append(
            f"<tr><td data-l='When'><b>{esc(when)}</b></td>"
            f"<td data-l='What'>{esc(what)}</td></tr>"
        )
    return "".join(rows)


def checklist_box(title: str, items: list) -> str:
    lis = "".join(f"<li>{esc(x if isinstance(x, str) else x.get('text',''))}</li>" for x in items)
    return f'<div class="checklist"><h3>{esc(title)}</h3><ul>{lis}</ul></div>'


def faq_block(items: list) -> str:
    parts = []
    for it in items:
        q = it.get("q") or it.get("question") or ""
        a = it.get("a") or it.get("answer") or ""
        parts.append(
            f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>"
        )
    return '<div class="faq">' + "".join(parts) + "</div>"


def ppc_links_block(links: dict) -> str:
    sections = [
        ("country_pages", "Country / overview pages"),
        ("airlines", "Airline pages"),
        ("airline_routes_live", "Related live airline-route pages"),
        ("clinics", "Clinics"),
        ("tools", "Tools"),
    ]
    out = ['<div class="ppc-links"><h2 id="ppc">Links on PetPolicyCheck</h2>']
    for key, heading in sections:
        vals = links.get(key) or []
        if not vals:
            continue
        out.append(f"<h3>{esc(heading)}</h3><ul>")
        for u in vals:
            rel = abs_to_rel(u)
            label = "/" + u.replace("https://petpolicycheck.com/", "")
            out.append(f'<li><a href="{esc(rel)}">{esc(label)}</a></li>')
        out.append("</ul>")
    out.append("</div>")
    return "".join(out)


def build_main(route: dict) -> str:
    slug = route["slug"]
    dest = DEST_LABEL[slug]
    crumb = CRUMB_LABEL[slug]
    h1 = route["h1"]
    lead = route["lead"]
    quick = "".join(claim_li(x) for x in route.get("quick") or [])
    leaving = "".join(claim_row(x) for x in route.get("leaving_usa") or [])
    entering = "".join(claim_row(x) for x in route.get("entering_destination") or [])
    ret = "".join(claim_row(x) for x in route.get("return_usa") or [])
    exit_ = "".join(claim_row(x) for x in route.get("exit_destination") or [])
    tl = timeline_rows(route.get("timeline") or [])

    # Checklist titles: mockup uses "Checklist — USA → Canada"
    arrow_dest = {
        "usa-canada": "Canada",
        "usa-mexico": "Mexico",
        "usa-uk": "Great Britain",
        "usa-japan": "Japan",
        "usa-france": "France",
    }[slug]

    parts = [
        "<main class=\"wrap\" id=\"main\">",
        PAGE_STYLE,
        f'<nav class="crumbs"><a href="./">Routes</a> &rsaquo; {esc(crumb)}</nav>',
        f"<h1>{esc(h1)}</h1>",
        f'<p class="lead">{esc(lead)}</p>',
        f'<div class="usa-quick"><h2 id="quick">Quick answer</h2><ul>{quick}</ul></div>',
        '<p class="warn usa-warn">Rules change. Confirm on the official pages linked in each row before you book. '
        'Last checked <time datetime="2026-11-09">Nov 9, 2026</time>. '
        "This page is a <b>local preview</b> only — not published.</p>",
        checklist_box(f"Checklist — USA → {arrow_dest}", route.get("checklist_out") or []),
        '<h2 id="leaving">Leaving the USA</h2>',
        f'<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Official rule</th><th>Source</th></tr></thead><tbody>{leaving}</tbody></table></div>',
        f'<h2 id="entering">Entering {esc(dest)}</h2>',
        f'<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Official rule</th><th>Source</th></tr></thead><tbody>{entering}</tbody></table></div>',
        '<h2 id="timeline">Timeline</h2>',
        f'<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>When</th><th>What</th></tr></thead><tbody>{tl}</tbody></table></div>',
        '<h2 id="return">Return to the USA</h2>',
        checklist_box("Checklist — return to the USA", route.get("checklist_return") or []),
        f'<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Official rule</th><th>Source</th></tr></thead><tbody>{ret}</tbody></table></div>',
        f'<h2 id="exit">Exit formalities from {esc(dest)}</h2>',
        f'<div class="tablewrap"><table class="cmp usa-t"><thead><tr><th>Official rule</th><th>Source</th></tr></thead><tbody>{exit_}</tbody></table></div>',
        '<h2 id="faq">FAQ</h2>',
        faq_block(route.get("faq") or []),
        ppc_links_block(route.get("ppc_links") or {}),
        '<p class="small">Every claim is labelled <span class="badge-off">Official rule</span>. '
        "Where a fee or duration is unclear: <i>Not stated on the official page</i>. "
        "Translations later via Traducteur Universel. Sources checked Nov 9, 2026.</p>",
        "</main>",
    ]
    return "\n".join(parts)


def patch_head(head: str, route: dict, filename: str) -> str:
    title = f"{route['title']} | PetPolicyCheck"
    desc = route["lead"][:160]
    canon = f"https://petpolicycheck.com/routes/{filename}"
    crumb_name = route["h1"]

    # robots noindex for preview
    if 'name="robots"' not in head:
        head = head.replace(
            '<meta charset="utf-8">',
            '<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">',
            1,
        )
    else:
        head = re.sub(
            r'<meta name="robots"[^>]*>',
            '<meta name="robots" content="noindex,nofollow">',
            head,
            count=1,
        )

    head = re.sub(r"<title>[^<]*</title>", f"<title>{esc(title)}</title>", head, count=1)
    if re.search(r'name="description"', head):
        head = re.sub(
            r'<meta name="description" content="[^"]*">',
            f'<meta name="description" content="{esc(desc)}">',
            head,
            count=1,
        )
    else:
        head = head.replace(
            "</title>",
            f'</title>\n<meta name="description" content="{esc(desc)}">',
            1,
        )

    head = re.sub(
        r'<link rel="canonical" href="[^"]*">',
        f'<link rel="canonical" href="{esc(canon)}">',
        head,
        count=1,
    )
    head = re.sub(
        r'<meta property="og:title" content="[^"]*">',
        f'<meta property="og:title" content="{esc(title)}">',
        head,
        count=1,
    )
    head = re.sub(
        r'<meta property="og:description" content="[^"]*">',
        f'<meta property="og:description" content="{esc(desc)}">',
        head,
        count=1,
    )
    head = re.sub(
        r'<meta property="og:url" content="[^"]*">',
        f'<meta property="og:url" content="{esc(canon)}">',
        head,
        count=1,
    )
    head = re.sub(
        r'<meta name="twitter:title" content="[^"]*">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        head,
        count=1,
    )
    head = re.sub(
        r'<meta name="twitter:description" content="[^"]*">',
        f'<meta name="twitter:description" content="{esc(desc)}">',
        head,
        count=1,
    )

    # Replace JSON-LD blocks with simple BreadcrumbList (drop old FAQPage for Japan)
    ld = (
        '{"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": ['
        '{"@type": "ListItem", "position": 1, "name": "Home", "item": "https://petpolicycheck.com/"}, '
        '{"@type": "ListItem", "position": 2, "name": "Routes", "item": "https://petpolicycheck.com/routes/"}, '
        f'{{"@type": "ListItem", "position": 3, "name": "{esc(crumb_name)}", "item": "{esc(canon)}"}}]}}'
    )
    head = re.sub(
        r'<script type="application/ld\+json">.*?</script>',
        "",
        head,
        flags=re.S,
    )
    head = head.replace(
        "</head>",
        f'<script type="application/ld+json">{ld}</script>\n</head>',
        1,
    )
    return head


def build_page(route: dict, shell_html: str) -> str:
    i = shell_html.index('<main class="wrap" id="main">')
    j = shell_html.index('<footer class="foot foot-compact">')
    head = patch_head(shell_html[:i], route, SLUG_FILE[route["slug"]])
    foot = shell_html[j:]
    # Preview bar after <body>
    bar = (
        '<div class="pv-bar">LOCAL PREVIEW · not published · awaiting Marc&rsquo;s OK · '
        f'/routes/{SLUG_FILE[route["slug"]]} · <a href="./">All routes</a></div>\n'
    )
    if "<body" in head:
        head = re.sub(
            r"(<body[^>]*>)",
            r"\1\n" + bar,
            head,
            count=1,
        )
    # Footer: keep copyright; ensure preview note doesn't invent data
    main = build_main(route)
    return head + main + "\n" + foot


def update_index(index_path: Path) -> None:
    html_txt = index_path.read_text()
    block = """
<section class="wrap" style="padding:8px 0 8px;max-width:920px;margin:0 auto" id="usa-overviews">
<p class="eyebrow" style="color:var(--gold,#d9b765);letter-spacing:.08em;text-transform:uppercase">Country-pair overviews · preview</p>
<h2 style="font-family:var(--disp,Marcellus,serif);font-weight:400;margin:.2em 0 .4em">USA ↔ country (local preview)</h2>
<p class="sub" style="color:var(--mut,#a9b3a4);max-width:65ch">Five overview pages with both directions, Official-rule sources checked Nov 9, 2026. Not published until Marc&rsquo;s typed OK.</p>
<ul style="line-height:1.7">
<li><a href="usa-canada.html"><b>USA ↔ Canada</b> — rabies certificate / CDC Dog Import Form</a></li>
<li><a href="usa-mexico.html"><b>USA ↔ Mexico</b> — SENASICA / NWS / CDC return</a></li>
<li><a href="usa-uk.html"><b>USA ↔ United Kingdom (Great Britain)</b> — PETS / Defra · NI ≠ GB</a></li>
<li><a href="usa-to-japan.html"><b>USA ↔ Japan</b> — AQS titer + 180-day wait (updated preview)</a></li>
<li><a href="usa-france.html"><b>USA ↔ France (EU)</b> — new EU certificates from Oct 2026</a></li>
</ul>
</section>
"""
    if 'id="usa-overviews"' in html_txt:
        html_txt = re.sub(
            r'<section class="wrap"[^>]*id="usa-overviews">.*?</section>\s*',
            block,
            html_txt,
            count=1,
            flags=re.S,
        )
    else:
        html_txt = html_txt.replace(
            '<main class="wrap" id="main">',
            '<main class="wrap" id="main">\n' + block,
            1,
        )
    # robots noindex while preview
    if 'name="robots"' not in html_txt:
        html_txt = html_txt.replace(
            '<meta charset="utf-8">',
            '<meta charset="utf-8">\n<meta name="robots" content="noindex,nofollow">',
            1,
        )
    index_path.write_text(html_txt)


def main() -> None:
    data = json.loads(SRC.read_text())
    shell_src = BEFORE if BEFORE.exists() else SHELL
    shell = shell_src.read_text()
    # Copy JSON into repo data for reference
    dest_json = ROOT / "data" / "routes" / "usa-overviews-20261109.json"
    dest_json.parent.mkdir(parents=True, exist_ok=True)
    dest_json.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    written = []
    for route in data["routes"]:
        slug = route["slug"]
        fname = SLUG_FILE[slug]
        page = build_page(route, shell)
        for base in (ROOT / "site" / "routes", ROOT / "static" / "routes"):
            base.mkdir(parents=True, exist_ok=True)
            (base / fname).write_text(page)
        written.append(fname)
        print("wrote", fname, "bytes", len(page))

    update_index(ROOT / "site" / "routes" / "index.html")
    # mirror index to static if present or create
    idx = (ROOT / "site" / "routes" / "index.html").read_text()
    (ROOT / "static" / "routes" / "index.html").write_text(idx)
    print("updated routes/index.html")
    print("OK", written)


if __name__ == "__main__":
    main()
