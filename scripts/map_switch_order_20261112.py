#!/usr/bin/env python3
"""Map switcher (#map-switch) in US-tourist popularity order (Marc 2026-11-12), only maps that exist
in each language. Rewrites the static switcher on every country map page of site/ and static/
(country-map.js rebuilds it at runtime from the same table)."""
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
# Marc's order; dominican-republic, portugal, greece have no map page yet and are skipped automatically.
ORDER = ["usa", "canada", "mexico", "uk", "italy", "france", "dominican-republic", "spain", "japan", "germany",
         "portugal", "greece", "south-korea"]
ACCENT = {"usa": "usa", "canada": "maple", "mexico": "mxgreen", "uk": "unionjack", "italy": "italy", "france": "tricolore",
          "spain": "rojigualda", "japan": "hinomaru", "germany": "schwarzrotgold", "south-korea": "taegeuk"}
LABEL = {
    "en": {"world": "← World Map", "usa": "USA Map", "canada": "Canada Map", "mexico": "Mexico Map", "uk": "UK Map",
           "italy": "Italy Map", "france": "France Map", "spain": "Spain Map", "japan": "Japan Map",
           "germany": "Germany Map", "south-korea": "Korea Map"},
    "it": {"world": "← Mappa del mondo", "usa": "Mappa USA", "canada": "Mappa del Canada", "mexico": "Mappa del Messico",
           "uk": "Mappa del Regno Unito", "italy": "Mappa dell’Italia", "france": "Mappa della Francia",
           "spain": "Mappa della Spagna", "japan": "Mappa del Giappone", "germany": "Mappa della Germania",
           "south-korea": "Mappa della Corea"},
    "es": {"world": "← Mapa mundial", "usa": "Mapa de EE. UU.", "canada": "Mapa de Canadá", "mexico": "Mapa de México",
           "italy": "Mapa Italia", "spain": "Mapa España"},
}
ST = ' style="touch-action:manipulation;position:relative;z-index:5"'
SW_RE = re.compile(r'(<nav\b[^>]*id="map-switch"[^>]*>)(.*?)(</nav>)', re.S)

def switch_html(tree, lang, cur):
    d = ROOT / tree / ("" if lang == "en" else lang) / "countries"
    pre = "/it/countries/" if lang == "it" else ""
    back = "/it/?view=map" if lang == "it" else "../?view=map"
    out = [f'<a class="msw-tab world-back" href="{back}"{ST}><i aria-hidden="true"></i><span>{LABEL[lang]["world"]}</span></a>']
    for k in ORDER:
        if k not in LABEL[lang] or not (d / f"{k}-map.html").is_file():
            continue
        on = k == cur
        out.append(f'<a class="msw-tab accent-{ACCENT[k]}{" is-current" if on else ""}" href="{pre}{k}-map.html"'
                   f'{" aria-current=" + chr(34) + "page" + chr(34) if on else ""}{ST}><i aria-hidden="true"></i>'
                   f'<span>{LABEL[lang][k]}</span></a>')
    return "".join(out)

n = 0
for tree in ("site", "static"):
    for f in sorted((ROOT / tree).rglob("*-map.html")):
        rel = f.relative_to(ROOT / tree).as_posix()
        parts = rel.split("/")
        lang = parts[0] if parts[0] in ("it", "es") else "en"
        if parts[-2] != "countries":
            continue
        s = f.read_text(encoding="utf-8")
        m = SW_RE.search(s)
        if not m:
            continue
        cur = parts[-1][:-len("-map.html")]
        s2 = s[:m.start(2)] + switch_html(tree, lang, cur) + s[m.end(2):]
        if s2 != s:
            f.write_text(s2, encoding="utf-8"); n += 1
print("map pages touched", n)
