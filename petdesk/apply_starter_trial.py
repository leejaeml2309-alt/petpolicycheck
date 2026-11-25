"""Apply the Starter 1-month Gumroad trial copy to /pro/ (6 languages), terms, refund policy and
privacy, in site/ and static/ (kept identical). Idempotent markers: data-pd="starter-trial".
Run: python3 petdesk/apply_starter_trial.py"""
import json, re, pathlib, html, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from copy_pro import PRO
from copy_legal import LEGAL
R = pathlib.Path(__file__).resolve().parent.parent
PRE = {"en": "", "fr": "fr/", "es": "es/", "de": "de/", "it": "it/", "ja": "ja/"}
# Starter membership product on Gumroad (created 25 Nov 2026, product_id Qtlp1phQoytjW-w_I-h0Og==). ?yearly=true is untested: check it in the test purchase.
GUM_MO = "https://petpolicycheck.gumroad.com/l/petdesk-starter?wanted=true"
GUM_YR = "https://petpolicycheck.gumroad.com/l/petdesk-starter?yearly=true&amp;wanted=true"

def must(pat, s, flags=re.S):
    m = re.search(pat, s, flags)
    if not m: raise SystemExit("pattern not found: " + pat[:80])
    return m

def hrefs(l):
    return "/" + PRE[l] + "terms.html", "/" + PRE[l] + "refund-policy.html"

def fmt(s, l):
    T, Rf = hrefs(l); return s.replace("{T}", T).replace("{R}", Rf)

def strip(s): return html.unescape(re.sub(r"<[^>]+>", "", s))

def patch_pro(l):
    p = R / "site" / PRE[l] / "pro/index.html"; t = p.read_text()
    if 'data-pd="starter-trial"' in t: return t
    c = PRO[l]
    def cta_row(tier, inner):
        nonlocal t
        art = must(r'<article class="plan[^"]*" data-tier="%s">.*?</article>' % tier, t).group(0)
        row = must(r'<div class="cta-row">.*?\n\s*</div>', art).group(0)
        onboard = must(r'<a [^>]*data-i="cta_onboard"[^>]*>.*?</a>', row).group(0)
        new_art = art.replace(row, inner(onboard)); t = t.replace(art, new_art)
    cta_row("starter", lambda ob: f'''<div class="cta-row" data-pd="starter-trial">
      <a class="btn-pro pri" href="{GUM_MO}" data-href-mo="{GUM_MO}" data-href-yr="{GUM_YR}" data-i="cta_trial" rel="noopener" target="_blank">{c["cta_trial"]}</a>
      <p class="fine trial-micro" data-i="cta_micro">{c["cta_micro"]}</p>
      {ob}
    </div>''')
    for tier in ("pro", "ent"):
        cta_row(tier, lambda ob: f'''<div class="cta-row">
      {ob.replace('class="btn-pro ghost"', 'class="btn-pro pri"', 1)}
      <p class="fine trial-micro" data-i="po_note">{c["po_note"]}</p>
    </div>''')
    # features: passports languages + watchlist
    for k in ("s2", "s5"):
        t = re.sub(r'(<li data-i="%s">)(.*?)(</li>)' % k, lambda m: m.group(1) + c[k] + m.group(3), t, count=1)
    # notice
    t = re.sub(r'(<div class="notice" data-i="notice">)(.*?)(</div>)', lambda m: m.group(1) + "\n  " + fmt(c["notice"], l) + "\n" + m.group(3), t, count=1, flags=re.S)
    # FAQ: replace every <details> in the pro-faq section
    sec = must(r'<section[^>]*class="pro-faq"[^>]*>.*?</section>', t).group(0)
    first = sec.find("<details"); last = sec.rfind("</details>") + len("</details>")
    items = "\n".join(f'  <details><summary>{q}</summary><p>{fmt(a, l)}</p></details>' for q, a in c["faq"])
    t = t.replace(sec, sec[:first] + items.lstrip() + sec[last:])
    # JSON-LD FAQPage (replace or add)
    ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(fmt(a, l))}} for q, a in c["faq"]]}
    block = '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=2) + "\n</script>"
    done = False
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
        try:
            if json.loads(m.group(1)).get("@type") == "FAQPage":
                t = t[:m.start()] + block + t[m.end():]; done = True; break
        except Exception: pass
    if not done: t = t.replace("</head>", block + "\n</head>", 1)
    # in-page dictionary overrides (used when the page switches language)
    over = {}
    for k in ("en", "fr", "es", "de", "it", "ja", "ko"):
        src = PRO.get(k, PRO["en"]); lk = k if k in PRO else "en"
        over[k] = {"cta_trial": src["cta_trial"], "cta_micro": src["cta_micro"], "s2": src["s2"], "s5": src["s5"],
                   "po_note": src["po_note"], "notice": fmt(src["notice"], lk)}
    js = "(function(O){for(var k in O){if(I[k])for(var j in O[k])I[k][j]=O[k][j];}})(" + json.dumps(over, ensure_ascii=False) + "); /* starter-trial 20261125 */"
    i = t.index("\nvar lang=", t.index("var I={"))
    t = t[:i] + "\n" + js + t[i:]
    return t

def section_replace(t, h2_pat, new_html):
    m = must(h2_pat, t); start = m.start()
    nxt = t.find("<h2", m.end());
    return t[:start] + new_html + t[nxt:]

def para_replace(t, after_pat, kw, new_inner):
    """Replace the inner HTML of the first <p> after `after_pat` whose text matches kw."""
    m = must(after_pat, t)
    for pm in re.finditer(r"<p>(.*?)</p>", t[m.end():], re.S):
        if re.search(kw, strip(pm.group(1)), re.I):
            a, b = m.end() + pm.start(1), m.end() + pm.end(1)
            return t[:a] + new_inner + t[b:], pm.group(1)
    raise SystemExit("para not found after " + after_pat)

KW = r"trial|essai|prueba|Test|prova|試用"
def patch_terms(l):
    p = R / "site" / PRE[l] / "terms.html"; t = p.read_text(); c = LEGAL[l]
    if 'data-pd="starter-trial"' in t: return t
    t, _ = para_replace(t, r'<h2 id="billing">', KW, c["t_billing"])
    t = section_replace(t, r'<h2 id="trial">', f'<h2 id="trial" data-pd="starter-trial">{c["t_h2"]}</h2>\n' + "\n".join(f"<p>{x}</p>" for x in c["t_p"]) + "\n")
    m = must(r'<h2 id="paid-sub">', t)
    seg_end = t.find("<h2", m.end()); seg = t[m.end():seg_end]
    for pm in re.finditer(r"<p>(.*?)</p>", seg, re.S):
        if re.search(r"14", strip(pm.group(1))) and re.search(KW, strip(pm.group(1)), re.I):
            link = re.search(r"<a [^>]*refund[^>]*>.*?</a>", pm.group(1), re.S)
            new = c["t_sep"].replace("{LINK}", link.group(0) if link else "Refund &amp; Cancellation Policy")
            seg = seg[:pm.start(1)] + new + seg[pm.end(1):]; break
    else: raise SystemExit("terms sep para not found " + l)
    return t[:m.end()] + seg + t[seg_end:]

def patch_refund(l):
    p = R / "site" / PRE[l] / "refund-policy.html"; t = p.read_text(); c = LEGAL[l]
    if 'data-pd="starter-trial"' in t: return t
    t, _ = para_replace(t, r'<main', r"Pet Desk", c["r_intro"])
    t = section_replace(t, r'<h2 id="trial">', f'<h2 id="trial" data-pd="starter-trial">{c["r_h2"]}</h2>\n' + "\n".join(f"<p>{x}</p>" for x in c["r_p"]) + "\n")
    t, _ = para_replace(t, r'<h2 id="guarantee">', KW, c["r_sep"])
    return t

def patch_privacy(l):
    p = R / "site" / PRE[l] / "privacy.html"; t = p.read_text(); c = LEGAL[l]
    if 'data-pd="starter-trial"' in t: return t
    b = t.index('<h2 id="billing">'); a = t.rfind("<h2", 0, b)
    return t[:a] + f'<h2 data-pd="starter-trial">{c["p_h2"]}</h2>\n' + "\n".join(f"<p>{x}</p>" for x in c["p_p"]) + "\n" + t[b:]

for l in PRE:
    for name, fn in (("pro/index.html", patch_pro), ("terms.html", patch_terms), ("refund-policy.html", patch_refund), ("privacy.html", patch_privacy)):
        out = fn(l)
        for root in ("site", "static"):
            f = R / root / PRE[l] / name
            if root == "static" and f.exists() and f.read_text() != (R / "site" / PRE[l] / name).read_text() and 'data-pd="starter-trial"' not in f.read_text():
                print("WARN static differs before patch:", f)
            f.write_text(out)
print("ok")
