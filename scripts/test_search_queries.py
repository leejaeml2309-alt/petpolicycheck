#!/usr/bin/env python3
"""Log top-3 search results for the brief's sample queries (Node-free)."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = json.loads((ROOT / "site/assets/search-index.en.json").read_text(encoding="utf-8"))

QUERIES = [
    "Delta",
    "usa mexico",
    "pug cargo",
    "ESA",
    "rabies titer japan",
    "hotel boston",
    "YVR",
    "aplhis health certificate",
    "emotionnal support",
]

TYPE_ORDER = ["Routes", "Airlines", "Countries", "Hotels", "Tools", "Guides"]


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower()
    s = re.sub(r"[^a-z0-9+#.\s-]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def tokens(s: str) -> list[str]:
    return [t for t in norm(s).split(" ") if t]


def damerau(a: str, b: str) -> int:
    la, lb = len(a), len(b)
    if abs(la - lb) > 2:
        return 99
    m = [[0] * (lb + 1) for _ in range(la + 1)]
    for i in range(la + 1):
        m[i][0] = i
    for j in range(lb + 1):
        m[0][j] = j
    for i in range(1, la + 1):
        for j in range(1, lb + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            m[i][j] = min(m[i - 1][j] + 1, m[i][j - 1] + 1, m[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                m[i][j] = min(m[i][j], m[i - 2][j - 2] + cost)
    return m[la][lb]


def fuzzy_ok(q: str, w: str) -> bool:
    if q == w:
        return True
    maxd = 2 if len(w) >= 8 else (1 if len(w) >= 4 else 0)
    return bool(maxd) and damerau(q, w) <= maxd


def expand(toks: list[str], synonyms: dict) -> list[str]:
    out = list(toks)
    seen = set(toks)
    for t in toks:
        for s in synonyms.get(t, []):
            for x in tokens(s):
                if x not in seen:
                    seen.add(x)
                    out.append(x)
    joined = " ".join(toks)
    for k, vals in synonyms.items():
        if " " not in k:
            continue
        if k in joined or all(p in seen for p in k.split()):
            for s in vals:
                for x in tokens(s):
                    if x not in seen:
                        seen.add(x)
                        out.append(x)
    return out


def score_page(page, q_toks, q_norm, expanded):
    title_n = norm(page["t"])
    title_toks = tokens(page["t"])
    url_n = norm(page["u"])
    kws = [norm(k) for k in page.get("k") or []]
    score = 0
    exact = False
    slug = url_n.rsplit("/", 1)[-1].replace(".html", "").replace("-", " ")
    if title_n == q_norm or title_n.startswith(q_norm):
        score += 1200
        exact = True
    if slug == q_norm or slug.replace(" ", "") == q_norm.replace(" ", ""):
        score += 1100
        exact = True
    for qt in q_toks:
        if qt in title_toks:
            score += 220
        elif any(t.startswith(qt) for t in title_toks) or title_n.startswith(qt):
            score += 140
        elif any(fuzzy_ok(qt, t) for t in title_toks):
            score += 70
        if qt in kws:
            score += 160
        elif any(k.startswith(qt) for k in kws):
            score += 90
        elif any(fuzzy_ok(qt, k) for k in kws):
            score += 50
        if qt in url_n:
            score += 40
    for et in expanded:
        if et in q_toks:
            continue
        if et in title_toks or et in kws:
            score += 100
        elif any(k.startswith(et) for k in kws) or any(t.startswith(et) for t in title_toks):
            score += 60
        elif et.replace(" ", "-") in url_n:
            score += 40
    if page.get("y") == "Airlines" and len(q_toks) == 1 and len(q_toks[0]) <= 3 and q_toks[0] in kws:
        score += 300
    return score, exact


def search(query: str):
    q_norm = norm(query)
    q_toks = tokens(q_norm)
    expanded = expand(q_toks, INDEX.get("synonyms") or {})
    scored = []
    for p in INDEX["pages"]:
        sc, exact = score_page(p, q_toks, q_norm, expanded)
        if sc > 0:
            scored.append((sc, exact, p))
    scored.sort(key=lambda x: (-int(x[1]), -x[0], TYPE_ORDER.index(x[2].get("y", "Guides")) if x[2].get("y") in TYPE_ORDER else 99))
    return scored[:3]


def main():
    print(f"pages={len(INDEX['pages'])} synonyms={len(INDEX.get('synonyms') or {})}")
    for q in QUERIES:
        top = search(q)
        print(f"\nQ: {q}")
        if not top:
            print("  (no results)")
            continue
        for i, (sc, exact, p) in enumerate(top, 1):
            print(f"  {i}. [{p.get('y')}] {p['t']} → {p['u']}  (score={sc}{' exact' if exact else ''})")


if __name__ == "__main__":
    main()
