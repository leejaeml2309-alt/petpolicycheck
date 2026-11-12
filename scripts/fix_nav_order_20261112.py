#!/usr/bin/env python3
"""fix(nav) 2026-11-12: trip-preparation order for the header hub links, header visible on the
home intro splash (EN, /it/, /es/), and the duplicated /it/ homepage collapsed to one document.
Targeted in-place edit of site/ and static/ (no build.py run)."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
ORDER = ["countries/", "airlines/", "vet-info/", "routes/", "hotels/", "passport/"]
NAV_RE = re.compile(r'(<nav\b[^>]*class="ppc-nav"[^>]*>)(.*?)(</nav>)', re.S)
A_RE = re.compile(r'<a\b[^>]*>.*?</a>', re.S)

def key(a):
    h = re.search(r'href="([^"]*)"', a).group(1)
    h = re.sub(r'^(?:\.\./)+|^/', '', h); h = re.sub(r'^(?:it|es)/', '', h)
    for i, k in enumerate(ORDER):
        if h.startswith(k): return i
    raise ValueError(h)

def reorder(s):
    def sub(m):
        items = A_RE.findall(m.group(2))
        if A_RE.sub('', m.group(2)).strip(): raise ValueError('extra content in nav')
        return m.group(1) + ''.join(sorted(items, key=key)) + m.group(3)
    return NAV_RE.sub(sub, s)

def dedupe_it_home(s):
    if s.count('<!doctype html>') + s.count('<!DOCTYPE html>') < 2: return s
    a = s.index('<!doctype html>')            # second, complete copy (has home-c.css)
    b = s.index('</body></html>', a) + len('</body></html>')
    return s[a:b] + '\n'

HOME_CSS = ('<style id="intro-topbar">html.intro-lock body.intro-home>header.ppc-topbar~section.intro'
            '{top:calc(var(--preview-h,0px) + var(--ppc-top-h,67px)) !important}</style>')
HOME_JS = ('<script>(function(){var h=document.querySelector("body.intro-home>header.ppc-topbar");if(!h)return;'
           'function s(){document.documentElement.style.setProperty("--ppc-top-h",h.offsetHeight+"px")}s();'
           'if(window.ResizeObserver)new ResizeObserver(s).observe(h)})();</script>')
CHROME_RE = re.compile(r'(<header class="ppc-topbar top"[^>]*>.*?</header>\s*<div class="ppc-drawer-backdrop"[^>]*></div>\s*<aside\b[^>]*class="ppc-drawer".*?</aside>)', re.S)

def home_topbar(s):
    if 'id="intro-topbar"' in s: return s
    m = CHROME_RE.search(s); assert m, 'chrome not found'
    chrome = m.group(1)
    s = s[:m.start()] + s[m.end():]
    body = re.search(r'<body class="v-c intro-home">', s); assert body
    s = s[:body.end()] + '\n' + chrome + HOME_JS + '\n' + s[body.end():]
    s = s.replace('</head>', HOME_CSS + '\n</head>', 1)
    return s

touched = 0
for tree in ('site', 'static'):
    for f in sorted((ROOT / tree).rglob('*.html')):
        rel = f.relative_to(ROOT / tree).as_posix()
        s0 = s = f.read_text(encoding='utf-8')
        if rel == 'it/index.html': s = dedupe_it_home(s)
        s = reorder(s)
        if rel in ('index.html', 'it/index.html', 'es/index.html'): s = home_topbar(s)
        if s != s0:
            f.write_text(s, encoding='utf-8'); touched += 1
print('files touched', touched)
