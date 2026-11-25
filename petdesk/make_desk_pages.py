"""Generate /pro/desk/ (index.html + print.html) for EN, FR, ES, DE, IT, JA from each language's
/pro/ page header and footer (unchanged design), writing to site/ and static/ (kept in sync).
Not part of build.py. Run: python3 petdesk/make_desk_pages.py"""
import json, re, subprocess, pathlib
from urllib.parse import urljoin
R = pathlib.Path(__file__).resolve().parent.parent
LANGS = {"en": "", "fr": "fr/", "es": "es/", "de": "de/", "it": "it/", "ja": "ja/"}
I = json.loads(subprocess.check_output(["node", "-e", "global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.PETDESK_I18N))", str(R / "site/assets/js/petdesk-i18n.js")]))
V = "20261125pd1"

def absolutize(html, base):
    def fix(m):
        attr, q, url = m.group(1), m.group(2), m.group(3)
        if re.match(r"^(https?:|mailto:|tel:|#|/|data:|javascript:)", url): return m.group(0)
        return f'{attr}={q}{urljoin(base, url)}{q}'
    return re.sub(r'\b(href|src)=(["\'])([^"\']*)\2', fix, html)

def parts(lang):
    src = (R / "site" / LANGS[lang] / "pro/index.html").read_text()
    base = "/" + LANGS[lang] + "pro/"
    ga = re.search(r"<script>\s*\(function\(\)\{\s*var skip=false;.*?</script>", src, re.S).group(0)
    hdr = re.search(r'<header class="top">.*?</header><script>.*?</script>', src, re.S).group(0)
    ftr = re.search(r"<footer class=\"foot foot-compact\">.*?</footer>", src, re.S).group(0)
    m = re.search(r'<a [^>]*class="skip"[^>]*>(.*?)</a>', src); skip = m.group(1) if m else 'Skip to content'
    return ga, absolutize(hdr, base), absolutize(ftr, base), skip

HEAD = """<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{title}</title>
<link rel="icon" href="/assets/img/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png"><link rel="apple-touch-icon" sizes="180x180" href="/assets/img/apple-touch-icon-180.png">
<link rel="preload" href="/assets/fonts/inter-var-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/marcellus-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/css/theme.css?v=20261124ja1">
<link rel="stylesheet" href="/style.css?v=20261112footer4">
<script src="/assets/js/pastilles.js?v=20261124ja1" defer></script>
<meta name="theme-color" content="#0b1719">
<link rel="stylesheet" href="/assets/css/pro-palette.css?v=20261118pa1">
<link rel="stylesheet" href="/assets/css/ppc-i18n.css?v=20261113nav1">
<script src="/assets/i18n/ui.js?v=20261124ja1" defer></script>
<script src="/assets/js/ppc-i18n.js?v=20261124ja1" defer></script>
<link rel="stylesheet" href="/assets/site-search.css?v=20261117sb2">
<link rel="stylesheet" href="/assets/css/petdesk.css?v={v}">"""

def opt(v, label, sel=False): return f'<option value="{v}"{" selected" if sel else ""}>{label}</option>'
LN = {"en": "English", "es": "Español", "it": "Italiano"}  # printable passport languages available today

def desk(lang):
    t = I[lang]; ga, hdr, ftr, skip = parts(lang)
    l1 = lang if lang in ("es", "it") else "en"
    l2 = "es" if l1 == "en" else "en"
    lopts = lambda s: "".join(opt(k, v, k == s) for k, v in LN.items())
    body = f"""<main class="wrap pd" id="main">
<section class="pro-sign theme-b2b pd-hero" aria-labelledby="pd-h1">
  <div class="pro-eye"><span>Paw Passport · Pet Desk</span></div>
  <h1 id="pd-h1">{t['h1']}</h1>
</section>

<section id="pd-login" class="pd-card pd-login" aria-labelledby="pd-login-h" hidden>
  <h2 id="pd-login-h" class="pd-h2">{t['open']}</h2>
  <p class="pd-lead">{t['lead']}</p>
  <form id="pd-form" autocomplete="off">
    <label for="pd-key">{t['key_label']}</label>
    <input id="pd-key" name="key" type="text" inputmode="text" spellcheck="false" autocapitalize="characters" placeholder="XXXXXXXX-XXXXXXXX-XXXXXXXX-XXXXXXXX" required maxlength="40">
    <button class="btn-pro pri" id="pd-open" type="submit">{t['open']}</button>
  </form>
  <p class="pd-msg err" id="pd-login-msg" role="alert" hidden></p>
  <p class="fine">{t['key_help']}</p>
  <p class="fine">{t['no_plan']}</p>
</section>

<div id="pd-app" hidden>
  <section class="pd-card pd-statusbar" aria-live="polite">
    <p id="pd-status" class="pd-status"></p>
    <p class="fine" id="pd-who"></p>
    <p class="pd-actions"><a class="btn-pro ghost" href="https://gumroad.com/library" rel="noopener" target="_blank">{t['manage']}</a> <button class="btn-pro ghost" type="button" id="pd-logout">{t['logout']}</button></p>
  </section>

  <section class="pd-card" aria-labelledby="pd-pass-h">
    <h2 class="pd-h2" id="pd-pass-h">{t['sec_pass']}</h2>
    <p class="pd-lead">{t['pass_lead']}</p>
    <div class="pd-quota"><span id="pd-quota"></span><span class="pd-bar"><span id="pd-quota-bar"></span></span></div>
    <div class="pd-grid">
      <label>{t['f_from']}<select id="pd-from"><option value="US">United States</option></select></label>
      <label>{t['f_to']}<select id="pd-to"><option value="FR">France</option></select></label>
      <label>{t['f_state']}<select id="pd-state"><option value="">—</option></select></label>
      <label>{t['f_airline']}<select id="pd-airline"><option value="">—</option></select></label>
      <label>{t['f_pet']}<select id="pd-pet">{opt('dog', t['f_dog'], True)}{opt('cat', t['f_cat'])}</select></label>
      <label>{t['f_ret']}<select id="pd-ret">{opt('0', t['f_oneway'], True)}{opt('1', t['f_round'])}</select></label>
      <label>{t['f_date']}<input type="date" id="pd-date"></label>
      <label>{t['f_retdate']}<input type="date" id="pd-retdate"></label>
      <label class="wide">{t['f_client']}<input type="text" id="pd-client" maxlength="60"></label>
      <label>{t['f_l1']}<select id="pd-l1">{lopts(l1)}</select></label>
      <label>{t['f_l2']}<select id="pd-l2">{lopts(l2)}</select></label>
    </div>
    <p><button class="btn-pro pri" type="button" id="pd-issue">{t['issue']}</button></p>
    <p class="pd-msg warn" id="pd-quota-full" hidden>{t['quota_full']}</p>
    <p class="pd-msg err" id="pd-issue-msg" role="alert" hidden></p>
    <h3 class="pd-h3">{t['recent']}</h3>
    <ul class="pd-list" id="pd-recent"></ul><p class="fine" id="pd-recent-empty">{t['recent_empty']}</p>
  </section>

  <section class="pd-card" aria-labelledby="pd-prof-h">
    <h2 class="pd-h2" id="pd-prof-h">{t['sec_profile']}</h2>
    <p class="pd-row"><input type="text" id="pd-agency" maxlength="80" placeholder="{t['profile_ph']}" aria-labelledby="pd-prof-h"> <button class="btn-pro ghost" type="button" id="pd-save-agency">{t['save']}</button> <span class="pd-msg ok" id="pd-profile-msg" hidden></span></p>
  </section>

  <section class="pd-card" aria-labelledby="pd-watch-h">
    <h2 class="pd-h2" id="pd-watch-h">{t['sec_watch']}</h2>
    <p class="pd-lead">{t['watch_lead']}</p>
    <ul class="pd-list pd-hits" id="pd-watch-hits"></ul>
    <p class="fine" id="pd-watch-none" hidden>{t['watch_none']}</p><p class="fine" id="pd-watch-pick">{t['watch_pick']}</p>
    <div class="pd-chks" id="pd-watch-list"></div>
    <p><button class="btn-pro ghost" type="button" id="pd-save-watch">{t['watch_save']}</button> <span class="pd-msg" id="pd-watch-msg" hidden></span></p>
  </section>

  <section class="pd-card" aria-labelledby="pd-tools-h">
    <h2 class="pd-h2" id="pd-tools-h">{t['sec_tools']}</h2>
    <ul class="pd-tools">
      <li><a href="/{LANGS[lang]}?view=map">{t['t_maps']}</a></li>
      <li><a href="/{LANGS[lang]}airlines/compare/">{t['t_comp']}</a></li>
    </ul>
  </section>
  <p class="fine">{t['note']}</p>
  <p class="fine">{t['help']}</p>
</div>
</main>"""
    return f"""<!doctype html>
<html lang="{lang}" data-ppc-locale="{lang}" data-section="b2b" class="theme-b2b pro-pal" data-desk-lang="{lang}" data-site-root="/">
<head>
<meta charset="utf-8">
{ga}
{HEAD.format(title='Pet Desk · Starter | PetPolicyCheck', v=V)}
</head>
<body class="v-c pd-body"><a class="skip" href="#main">{skip}</a>
{hdr}
{body}
{ftr}
<script src="/assets/js/petdesk-i18n.js?v={V}"></script>
<script src="/assets/js/petdesk.js?v={V}" defer></script>
<script src="/assets/site-search.js?v=20261124ja1" defer></script>
<script src="/assets/ppc-header.js?v=20261110footerk9" defer></script>
</body>
</html>
"""

def printpage(lang):
    t = I[lang]; ga, *_ = parts(lang)
    return f"""<!doctype html>
<html lang="{lang}" data-site-root="/" data-msg-denied="{t['denied']}">
<head>
<meta charset="utf-8">
{ga}
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Pet Desk · Passport | PetPolicyCheck</title>
<link rel="icon" href="/assets/img/favicon.ico" sizes="any">
<link rel="stylesheet" href="/assets/css/theme.css?v=20261124ja1">
<link rel="stylesheet" href="/style.css?v=20261112footer4">
<link rel="stylesheet" href="/assets/css/petdesk.css?v={V}">
</head>
<body class="pd-print-body">
<div class="pd-printbar no-print"><a href="./">← Pet Desk</a> <button class="btn-pro pri" id="pd-print" type="button" disabled>{t['print']}</button></div>
<header class="pd-head" id="pd-head"></header>
<div id="pd-copies"></div>
<p class="pd-foot">PetPolicyCheck · Pet Desk Starter — {t['note']}</p>
<script src="/assets/js/petdesk-print.js?v={V}" defer></script>
</body>
</html>
"""

for lang, pre in LANGS.items():
    for root in ("site", "static"):
        d = R / root / pre / "pro/desk"; d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(desk(lang)); (d / "print.html").write_text(printpage(lang))
print("ok")
