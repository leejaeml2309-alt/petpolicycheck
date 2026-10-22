"""Forum pages for build.py (stdlib only).

build.py calls `forum_pages.build(B, cfg, airlines)` where B is the build module (page(), e(), site_base() ...).
- Forum off (forum.enabled false, or supabase_url / supabase_anon_key empty): only /forum/index.html is
  written, a noindex "coming soon" page without ads; nothing in the sitemap or nav.
- Forum on: index (filters + pre-rendered list), post.html (live, noindex), p/<id>.html (pre-rendered
  published posts, indexable), new.html, account.html, admin.html (noindex), guidelines.html,
  forum.js + i18n.js + config.js. Returns sitemap entries.

Pre-render: published posts/comments are read with the public anon key over the Supabase REST API at build
time (same visibility as any visitor). On network failure the last good copy in data/forum_cache.json is used.
Set FORUM_PRERENDER=0 to skip the fetch (cache only).
"""
import datetime as dt
import json
import os
import re
import shutil
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATS = json.loads((HERE / "categories.json").read_text())
FILTERS = ("transport", "weather", "season", "carrier", "species", "weight")
SUPABASE_JS = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.118.0/dist/umd/supabase.js"
POST_COLS = ("id,lang,title,body,transport,weather,season,carrier,species,breed,weight,airline_slug,operator,"
             "route_from,route_to,trip_date,created_at,author:profiles(display_name)")


def dicts():
    out = {}
    for p in sorted((HERE / "i18n").glob("*.json")):
        out[p.stem] = json.loads(p.read_text())
    return out


I18N = dicts()
EN = I18N["en"]


def T(key, **kw):
    s = EN.get(key, key)
    for k, v in kw.items():
        s = s.replace("{" + k + "}", str(v))
    return s


def fcfg(cfg):
    f = cfg.get("forum") or {}
    on = bool(f.get("enabled")) and bool((f.get("supabase_url") or "").strip()) and bool((f.get("supabase_anon_key") or "").strip())
    return f, on


def enabled(cfg):
    return fcfg(cfg)[1]


# ------------------------------------------------------------------ small render helpers
def i(B, key, tag="span", attrs="", **kw):
    """Element whose text is translated client-side (data-i18n); English rendered statically."""
    return f'<{tag} data-i18n="{key}"{attrs}>{B.e(T(key, **kw))}</{tag}>'


def post_path(p):
    """Static path of a pre-rendered post, relative to /forum/: p/<12 hex>[-ascii-slug].html."""
    hid = p["id"].replace("-", "")[:12]
    slug = re.sub(r"[^a-z0-9]+", "-", p.get("title", "").lower()).strip("-")[:60].strip("-")
    return f"p/{hid}{'-' + slug if slug else ''}.html"


def fdate(iso):
    if not iso:
        return ""
    return dt.date.fromisoformat(iso[:10]).strftime("%b %-d, %Y")


def tags(B, p):
    out = []
    for g in ("transport", "species", "weight", "carrier", "weather", "season"):
        if p.get(g):
            out.append(f'<span class="ftag t-{g}" data-i18n="cat.{g}.{p[g]}">{B.e(T(f"cat.{g}.{p[g]}"))}</span>')
    if p.get("breed"):
        out.append(f'<span class="ftag">{B.e(p["breed"])}</span>')
    return '<span class="ftags">' + "".join(out) + "</span>"


def body_html(B, txt):
    paras = [x for x in re.split(r"\n\s*\n", (txt or "").strip()) if x.strip()]
    return "".join("<p>" + B.e(x.strip()).replace("\n", "<br>") + "</p>" for x in paras)


def excerpt(txt, n=220):
    t = re.sub(r"\s+", " ", txt or "").strip()
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0] + "…"


def author(p):
    return ((p.get("author") or {}).get("display_name")) or "Traveller"


def subnav(B, root, cur, show_lang=True):
    items = [("index.html", "f.home"), ("new.html", "f.new"), ("guidelines.html", "f.rules"), ("account.html", "f.account")]
    links = "".join(f'<a href="{root}forum/{h}"{" aria-current=page" if h == cur else ""}'
                    f'{" data-acct" if h == "account.html" else ""} data-i18n="{k}">{B.e(T(k))}</a>' for h, k in items)
    langs = "".join(f'<button type="button" data-setlang="{c}" lang="{c}">{B.e(d.get("_lang_name", c))}</button>'
                    for c, d in I18N.items())
    return (f'<nav class="fnav" aria-label="Forum">{links}'
            + (f'<span class="flang" role="group" aria-label="Language">{langs}</span>' if show_lang else "") + "</nav>")


def opts(B, group, codes, blank_key="f.any"):
    o = f'<option value="" data-i18n="{blank_key}">{B.e(T(blank_key))}</option>' if blank_key else ""
    return o + "".join(f'<option value="{c}" data-i18n="cat.{group}.{c}">{B.e(T(f"cat.{group}.{c}"))}</option>' for c in codes)


def scripts(root, page_name, extra=""):
    v = FORUM_VER
    return (f'<script src="{SUPABASE_JS}" defer></script>'
            f'<script src="{root}forum/i18n.js?v={v}" defer></script>'
            f'<script src="{root}forum/config.js?v={v}" defer></script>'
            f'<script src="{root}forum/forum.js?v={v}" defer></script>{extra}')


FORUM_VER = "0"


def app(page_name, inner="", **data):
    da = "".join(f' data-{k.replace("_", "-")}="{v}"' for k, v in data.items())
    return f'<div id="forum" class="forum" data-page="{page_name}"{da}>{inner}</div>'


def noscript(B):
    return '<noscript><p class="warn">Please enable JavaScript to sign in, post or comment. 로그인·글쓰기·댓글에는 자바스크립트가 필요해요.</p></noscript>'


# ------------------------------------------------------------------ data
def fetch_published(cfg, root_dir):
    f, _ = fcfg(cfg)
    cache = root_dir / "data" / "forum_cache.json"
    if os.environ.get("FORUM_PRERENDER", "1") != "0":
        try:
            url = f["supabase_url"].rstrip("/") + "/rest/v1/"
            key = f["supabase_anon_key"]

            def get(path, params):
                req = urllib.request.Request(url + path + "?" + urllib.parse.urlencode(params, safe="(),.*:"))
                req.add_header("apikey", key)
                if not key.startswith("sb_"):
                    req.add_header("Authorization", "Bearer " + key)
                with urllib.request.urlopen(req, timeout=15) as r:
                    return json.loads(r.read().decode())

            posts = get("posts", {"select": POST_COLS, "status": "eq.published", "order": "created_at.desc", "limit": "1000"})
            comments = get("comments", {"select": "id,post_id,body,created_at,author:profiles(display_name)",
                                        "status": "eq.published", "order": "created_at.asc", "limit": "10000"})
            data = {"fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "posts": posts, "comments": comments}
            cache.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
            print(f"  forum: pre-rendering {len(posts)} published posts, {len(comments)} comments")
            return data
        except Exception as ex:  # network / config problem: never break the site build
            print(f"  WARNING: forum pre-render fetch failed ({type(ex).__name__}: {ex}); using cache")
    if cache.exists():
        return json.loads(cache.read_text())
    return {"posts": [], "comments": []}


# ------------------------------------------------------------------ pages
def coming_soon(B, cfg):
    root = "../"
    body = f"""<section class="soon">
<h1>{i(B, "f.soon.h", "span")}</h1>
<p class="lead">{B.e(T("f.soon.p"))}</p>
<p lang="ko" class="small">{B.e(I18N["ko"]["f.soon.p"])}</p>
<p>{B.e(T("f.soon.p2"))}</p>
<p class="fbtns"><a class="fbtn" href="{root}index.html">Compare airline pet policies</a> <a class="fbtn alt" href="{root}products/">Carrier &amp; crate guides</a></p>
</section>"""
    return B.page(cfg, f"Pet travel forum: coming soon | {cfg['site_name']}",
                  "A moderated forum for travelling with dogs and cats is coming soon to PetPolicyCheck.",
                  body, "forum/", root, noindex=True, ads=False)


def card(B, p, root, href):
    al = f' &middot; {B.e(p["operator"])}' if p.get("operator") else ""
    route = " → ".join(x for x in (p.get("route_from"), p.get("route_to")) if x)
    return (f'<li class="fcard" lang="{B.e(p.get("lang", "en"))}"><a href="{href}">{B.e(p["title"])}</a>'
            f'{tags(B, p)}<span class="small fmeta">{B.e(author(p))} &middot; <time datetime="{B.e(p["created_at"][:10])}">{fdate(p["created_at"])}</time>{al}'
            f'{(" &middot; " + B.e(route)) if route else ""}</span>'
            f'<span class="fex">{B.e(excerpt(p["body"]))}</span></li>')


def filter_form(B, airlines):
    sel = "".join(
        f'<label><span data-i18n="f.fld.{g}">{B.e(T("f.fld." + g))}</span><select name="{g}">{opts(B, g, CATS[g])}</select></label>'
        for g in FILTERS)
    al = '<option value="" data-i18n="f.any">Any</option>' + "".join(f'<option value="{a["slug"]}">{B.e(a["name"])}</option>' for a in airlines)
    lang = f'<label><span data-i18n="f.fld.plang">{B.e(T("f.fld.plang"))}</span><select name="plang">{opts(B, "lang", CATS["lang"])}</select></label>'
    return (f'<form class="ffilters" id="ffilters" action="index.html" method="get" role="search">'
            f'<h2 class="fh" data-i18n="f.filters">{B.e(T("f.filters"))}</h2><div class="fgrid">'
            f'<label class="wide"><span data-i18n="f.search">{B.e(T("f.search"))}</span><input type="search" name="q" maxlength="60" data-i18n-ph="f.search_ph" placeholder="{B.e(T("f.search_ph"))}"></label>'
            f'{sel}<label><span data-i18n="f.fld.airline">{B.e(T("f.fld.airline"))}</span><select name="airline">{al}</select></label>{lang}</div>'
            f'<p class="fbtns"><button type="submit" class="fbtn" data-i18n="f.filter_btn">{B.e(T("f.filter_btn"))}</button> <a href="index.html" class="fbtn alt" data-i18n="f.reset">{B.e(T("f.reset"))}</a></p></form>')


def build_index(B, cfg, airlines, posts, paths):
    root = "../"
    cards = "".join(card(B, p, root, paths[p["id"]]) for p in posts[:30])
    lst = f'<ul class="flist" id="flist">{cards}</ul>' if cards else f'<ul class="flist" id="flist"></ul><p class="note" id="fempty">{i(B, "f.empty")}</p>'
    body = f"""<nav class="crumbs"><a href="{{root}}index.html" data-i18n="f.crumb_home">Home</a> &rsaquo; <span data-i18n="nav.forum">Forum</span></nav>
<h1 data-i18n="f.h1">{B.e(T("f.h1"))}</h1>
{subnav(B, root, "index.html")}
<p class="lead" data-i18n="f.lead">{B.e(T("f.lead"))}</p>
{filter_form(B, airlines)}
<p class="small" id="fstatus" aria-live="polite"></p>
{lst}
<p><button type="button" class="fbtn alt" id="fmore" hidden data-i18n="f.load_more">{B.e(T("f.load_more"))}</button></p>
<p class="small">{i(B, "f.disclaimer")} <a href="guidelines.html" data-i18n="f.why.see_rules">{B.e(T("f.why.see_rules"))}</a></p>
{app("index")}{scripts(root, "index")}"""
    ld = [B.bc_ld(cfg, [("Home", ""), ("Forum", "forum/")])]
    return B.page(cfg, f"Pet travel forum: flying and travelling with dogs and cats | {cfg['site_name']}",
                  "Real experiences travelling with dogs and cats by plane (cabin or cargo), train, bus, subway, taxi, car and ferry, in English and Korean. Filter by transport, carrier, season and pet size.",
                  body, "forum/", root, ld)


def post_article(B, p, comments, root, airlines_by):
    meta = []
    if p.get("airline_slug") in airlines_by:
        a = airlines_by[p["airline_slug"]]
        meta.append(f'<a href="{root}airlines/{a["slug"]}.html" data-i18n="f.airline_page" data-i18n-name="{B.e(a["name"])}">{B.e(T("f.airline_page", name=a["name"]))}</a>')
    if p.get("operator"):
        meta.append(B.e(p["operator"]))
    route = " → ".join(x for x in (p.get("route_from"), p.get("route_to")) if x)
    if route:
        meta.append(B.e(route))
    if p.get("trip_date"):
        meta.append(f'<span data-i18n="f.trip">Trip</span>: {B.e(p["trip_date"][:7])}')
    cm = "".join(f'<li id="c-{B.e(c["id"])}"><p class="small fmeta">{B.e(author(c))} &middot; <time datetime="{B.e(c["created_at"][:10])}">{fdate(c["created_at"])}</time></p>{body_html(B, c["body"])}</li>' for c in comments)
    return (f'<article class="fpost" lang="{B.e(p.get("lang", "en"))}"><h1>{B.e(p["title"])}</h1>'
            f'<p class="small fmeta">{B.e(author(p))} &middot; <time datetime="{B.e(p["created_at"][:10])}">{fdate(p["created_at"])}</time></p>'
            f'{tags(B, p)}{"<p class=small>" + " &middot; ".join(meta) + "</p>" if meta else ""}'
            f'<div class="fbody">{body_html(B, p["body"])}</div></article>'
            f'<section class="fcomments" aria-labelledby="fc-h"><h2 id="fc-h" data-i18n="f.comments">{B.e(T("f.comments"))}</h2>'
            f'<ul class="fclist" id="fclist">{cm}</ul>{"" if cm else i(B, "f.no_comments", "p", " class=small id=fcnone")}</section>')


def build_post_static(B, cfg, p, comments, path, airlines_by):
    root = "../../"
    art = post_article(B, p, comments, root, airlines_by)
    body = f"""<nav class="crumbs"><a href="{{root}}index.html" data-i18n="f.crumb_home">Home</a> &rsaquo; <a href="{{root}}forum/" data-i18n="nav.forum">Forum</a> &rsaquo; {B.e(p["title"][:60])}</nav>
{subnav(B, root, "")}
<div id="fpost-static">{art}</div>
{app("post", post_id=p["id"], static="1")}{noscript(B)}{scripts(root, "post")}"""
    base = B.site_base(cfg)
    ld = [B.bc_ld(cfg, [("Home", ""), ("Forum", "forum/"), (p["title"][:80], f"forum/{path}")]),
          {"@context": "https://schema.org", "@type": "DiscussionForumPosting", "headline": p["title"][:110],
           "text": p["body"][:5000], "inLanguage": p.get("lang", "en"), "datePublished": p["created_at"],
           "url": f"{base}/forum/{path}", "author": {"@type": "Person", "name": author(p)},
           "commentCount": len(comments),
           "comment": [{"@type": "Comment", "text": c["body"][:2000], "datePublished": c["created_at"],
                        "author": {"@type": "Person", "name": author(c)}} for c in comments[:50]]}]
    desc = excerpt(p["body"], 155)
    return B.page(cfg, f"{p['title'][:70]} | {cfg['site_name']} forum", desc, body, f"forum/{path}", root, ld)


def build_post_live(B, cfg):
    root = "../"
    body = f"""<nav class="crumbs"><a href="{{root}}index.html" data-i18n="f.crumb_home">Home</a> &rsaquo; <a href="index.html" data-i18n="nav.forum">Forum</a></nav>
{subnav(B, root, "")}
<div id="fpost-static"><p class="small" data-i18n="f.loading">{B.e(T("f.loading"))}</p></div>
{app("post")}{noscript(B)}{scripts(root, "post")}"""
    return B.page(cfg, f"Forum post | {cfg['site_name']}", "A traveller's experience with a dog or cat.", body,
                  "forum/post.html", root, noindex=True, ads=False)


def field(B, key, control, opt=False, hint=None):
    o = f' <span class="small">(<span data-i18n="f.optional">{B.e(T("f.optional"))}</span>)</span>' if opt else ""
    h = f'<span class="small fhint" data-i18n="{hint}">{B.e(T(hint))}</span>' if hint else ""
    return f'<div class="ffield"><label for="nf-{key}"><span data-i18n="f.fld.{key}">{B.e(T("f.fld." + key))}</span>{o}</label>{control}{h}</div>'


def build_new(B, cfg, airlines):
    root = "../"
    sel = lambda g, req=False: (f'<select id="nf-{g}" name="{g}"{" required" if req else ""}><option value="">&mdash;</option>'
                                f'{opts(B, g, CATS[g], None)}</select>')
    al = (f'<select id="nf-airline" name="airline_slug"><option value="" data-i18n="f.airline_other">{B.e(T("f.airline_other"))}</option>'
          + "".join(f'<option value="{a["slug"]}">{B.e(a["name"])}</option>' for a in airlines) + "</select>")
    dl = "".join(f'<datalist id="breeds-{s}">' + "".join(f'<option value="{B.e(b)}">' for b in bs) + "</datalist>" for s, bs in CATS["breeds"].items())
    langsel = f'<select id="nf-lang" name="lang">{opts(B, "lang", CATS["lang"], None)}</select>'
    form = f"""<form class="fform" id="newpost" hidden novalidate>
{field(B, "title", '<input id="nf-title" name="title" required minlength="5" maxlength="140">')}
<div class="frow">{field(B, "transport", sel("transport", True))}{field(B, "species", sel("species", True))}{field(B, "lang", langsel)}</div>
<p class="small note" id="subway-note" hidden data-i18n="f.subway_note">{B.e(T("f.subway_note"))}</p>
{field(B, "body", '<textarea id="nf-body" name="body" required minlength="30" maxlength="8000" rows="10"></textarea>', hint="f.hint.body")}
<div class="frow">{field(B, "breed", '<input id="nf-breed" name="breed" maxlength="60" list="breeds-dog">', True, "f.hint.breed")}{field(B, "weight", sel("weight"), True)}{field(B, "carrier", sel("carrier"), True)}</div>
<div class="frow">{field(B, "weather", sel("weather"), True)}{field(B, "season", sel("season"), True)}{field(B, "trip_date", '<input id="nf-trip_date" name="trip_date" type="month" min="2000-01">', True)}</div>
<div class="frow">{field(B, "airline", al, True)}{field(B, "operator", '<input id="nf-operator" name="operator" maxlength="80">', True, "f.hint.operator")}</div>
<div class="frow">{field(B, "route_from", '<input id="nf-route_from" name="route_from" maxlength="60">', True)}{field(B, "route_to", '<input id="nf-route_to" name="route_to" maxlength="60">', True)}</div>
{dl}
<p class="ferr" id="nf-err" role="alert" hidden></p>
<p class="fbtns"><button type="submit" class="fbtn" data-i18n="f.submit">{B.e(T("f.submit"))}</button></p>
<p class="small">{i(B, "f.agree_pre")} <a href="guidelines.html" data-i18n="f.rules">{B.e(T("f.rules"))}</a>{i(B, "f.agree_post")} {i(B, "f.mod_note")}</p>
</form>"""
    body = f"""<nav class="crumbs"><a href="{{root}}index.html" data-i18n="f.crumb_home">Home</a> &rsaquo; <a href="index.html" data-i18n="nav.forum">Forum</a> &rsaquo; <span data-i18n="f.new">{B.e(T("f.new"))}</span></nav>
<h1 data-i18n="f.new">{B.e(T("f.new"))}</h1>
{subnav(B, root, "new.html")}
<div class="note" id="nf-signin" hidden><p data-i18n="f.need_signin">{B.e(T("f.need_signin"))}</p><p><a class="fbtn" href="account.html?next=new.html" data-i18n="f.signin">{B.e(T("f.signin"))}</a></p></div>
<div class="verified" id="nf-done" hidden role="status"><p data-i18n="f.pending_post">{B.e(T("f.pending_post"))}</p><p><a href="account.html" data-i18n="f.see_status">{B.e(T("f.see_status"))}</a></p></div>
{form}
{app("new")}{noscript(B)}{scripts(root, "new")}"""
    return B.page(cfg, f"Share your pet travel experience | {cfg['site_name']}", "Share a trip with your dog or cat.", body,
                  "forum/new.html", root, noindex=True, ads=False)


def build_account(B, cfg, mail_html):
    root = "../"
    inp = lambda id_, typ, key, extra="": (f'<div class="ffield"><label for="{id_}" data-i18n="{key}">{B.e(T(key))}</label>'
                                           f'<input id="{id_}" type="{typ}" {extra}></div>')
    body = f"""<nav class="crumbs"><a href="{{root}}index.html" data-i18n="f.crumb_home">Home</a> &rsaquo; <a href="index.html" data-i18n="nav.forum">Forum</a> &rsaquo; <span data-i18n="f.account">{B.e(T("f.account"))}</span></nav>
<h1 data-i18n="f.acc.h">{B.e(T("f.acc.h"))}</h1>
{subnav(B, root, "account.html")}
<p class="ferr" id="acc-err" role="alert" hidden></p><p class="verified" id="acc-msg" role="status" hidden></p>
<section id="acc-out" hidden>
 <div class="fauth">
  <form class="fform" id="f-signin"><h2 class="fh" data-i18n="f.auth.signin_h">{B.e(T("f.auth.signin_h"))}</h2>
   {inp("si-email", "email", "f.auth.email", 'autocomplete="email" required')}
   {inp("si-pass", "password", "f.auth.password", 'autocomplete="current-password" required')}
   <p class="fbtns"><button class="fbtn" type="submit" data-i18n="f.auth.signin_btn">{B.e(T("f.auth.signin_btn"))}</button></p>
   <p class="small"><a href="#" data-show="f-reset" data-i18n="f.auth.forgot">{B.e(T("f.auth.forgot"))}</a> &middot; <a href="#" data-show="f-signup" data-i18n="f.auth.to_signup">{B.e(T("f.auth.to_signup"))}</a></p>
  </form>
  <form class="fform" id="f-signup" hidden><h2 class="fh" data-i18n="f.auth.signup_h">{B.e(T("f.auth.signup_h"))}</h2>
   {inp("su-name", "text", "f.auth.display_name", 'minlength="2" maxlength="40" required autocomplete="nickname"')}<p class="small fhint" data-i18n="f.auth.display_hint">{B.e(T("f.auth.display_hint"))}</p>
   {inp("su-email", "email", "f.auth.email", 'autocomplete="email" required')}
   {inp("su-pass", "password", "f.auth.password", 'autocomplete="new-password" minlength="8" required')}<p class="small fhint" data-i18n="f.auth.password_hint">{B.e(T("f.auth.password_hint"))}</p>
   <p class="small"><span data-i18n="f.auth.agree">{B.e(T("f.auth.agree"))}</span> <a href="guidelines.html" data-i18n="f.rules">{B.e(T("f.rules"))}</a> &middot; <a href="{{root}}privacy.html#forum">Privacy</a></p>
   <p class="fbtns"><button class="fbtn" type="submit" data-i18n="f.auth.signup_btn">{B.e(T("f.auth.signup_btn"))}</button></p>
   <p class="small"><a href="#" data-show="f-signin" data-i18n="f.auth.to_signin">{B.e(T("f.auth.to_signin"))}</a></p>
  </form>
  <form class="fform" id="f-reset" hidden><h2 class="fh" data-i18n="f.auth.forgot">{B.e(T("f.auth.forgot"))}</h2>
   {inp("rs-email", "email", "f.auth.email", 'autocomplete="email" required')}
   <p class="fbtns"><button class="fbtn" type="submit" data-i18n="f.auth.reset_btn">{B.e(T("f.auth.reset_btn"))}</button></p>
   <p class="small"><a href="#" data-show="f-signin" data-i18n="f.auth.to_signin">{B.e(T("f.auth.to_signin"))}</a></p>
  </form>
  <div class="fgoogle"><p class="small" data-i18n="f.auth.or">{B.e(T("f.auth.or"))}</p><button type="button" class="fbtn alt" id="g-btn" data-i18n="f.auth.google">{B.e(T("f.auth.google"))}</button></div>
 </div>
</section>
<form class="fform" id="f-newpass" hidden><h2 class="fh" data-i18n="f.auth.new_password">{B.e(T("f.auth.new_password"))}</h2>
 {inp("np-pass", "password", "f.auth.new_password", 'autocomplete="new-password" minlength="8" required')}
 <p class="fbtns"><button class="fbtn" type="submit" data-i18n="f.auth.save_password">{B.e(T("f.auth.save_password"))}</button></p>
</form>
<section id="acc-in" hidden>
 <p><span data-i18n="f.acc.signed_in_as">{B.e(T("f.acc.signed_in_as"))}</span> <b id="acc-email"></b> &middot; <button type="button" class="linkbtn" id="acc-out-btn" data-i18n="f.signout">{B.e(T("f.signout"))}</button></p>
 <p id="acc-admin" hidden><a class="fbtn" href="admin.html" data-i18n="f.acc.admin">{B.e(T("f.acc.admin"))}</a></p>
 <form class="fform inline" id="f-name"><div class="ffield"><label for="acc-name" data-i18n="f.acc.display_name">{B.e(T("f.acc.display_name"))}</label><input id="acc-name" minlength="2" maxlength="40" required></div>
  <button class="fbtn" type="submit" data-i18n="f.acc.save">{B.e(T("f.acc.save"))}</button></form>
 <h2 data-i18n="f.acc.my_posts">{B.e(T("f.acc.my_posts"))}</h2><ul class="fmine" id="acc-posts"></ul>
 <h2 data-i18n="f.acc.my_comments">{B.e(T("f.acc.my_comments"))}</h2><ul class="fmine" id="acc-comments"></ul>
 <p class="small" data-i18n-html="f.acc.delete_info" data-email="{B.e(fcfg(cfg)[0].get("contact_email") or cfg["contact_email"])}">{T("f.acc.delete_info", email=mail_html)}</p>
</section>
{app("account")}{noscript(B)}{scripts(root, "account")}"""
    return B.page(cfg, f"My forum account | {cfg['site_name']}", "Sign in or create an account for the PetPolicyCheck forum.", body,
                  "forum/account.html", root, noindex=True, ads=False)


def build_admin(B, cfg):
    root = "../"
    body = f"""<h1 data-i18n="adm.h">{B.e(T("adm.h"))}</h1>
{subnav(B, root, "")}
<p class="warn" id="adm-only" hidden data-i18n="adm.only">{B.e(T("adm.only"))}</p>
<section id="adm" hidden>
<p class="fbtns"><button type="button" class="fbtn alt" id="adm-refresh" data-i18n="adm.refresh">{B.e(T("adm.refresh"))}</button> <span class="small" id="adm-count"></span></p>
<div id="adm-list"></div>
<p class="small">Normal flow: the moderator bot (forum/moderate.py) reviews the queue about every 30 minutes. This page is the manual fallback.</p>
</section>
{app("admin")}{noscript(B)}{scripts(root, "admin")}"""
    return B.page(cfg, f"Forum moderation | {cfg['site_name']}", "Forum moderation.", body, "forum/admin.html", root, noindex=True, ads=False)


GUIDE_EN = [
    ("What belongs here", ["First-hand experiences travelling with a dog or cat: flights (cabin or hold), trains, buses, subways, taxis, cars and ferries.",
                           "Practical details help others most: the carrier you used, your pet's size, the season and weather, what the staff asked for, what went well and what didn't.",
                           "Questions and kind, helpful replies in the comments."]),
    ("Not allowed", ["Insults, harassment, slurs or hate against anyone, including staff, other travellers or groups of people.",
                     "Violence, threats, cruelty to animals, or encouraging unsafe travel.",
                     "Sexual, adult or shocking content.",
                     "Politics: elections, parties, politicians or political debates, in any country. This forum is about pets and travel only.",
                     "Advertising, spam, affiliate or referral links, and contact details for selling services.",
                     "Personal data of other people (names, photos, booking numbers, phone numbers)."]),
    ("How moderation works", ["Every post and comment is checked before it appears, usually within 30 minutes.",
                              "An automatic filter immediately refuses obvious insults, adult content, political content and spam. Posts with external links are reviewed by a moderator.",
                              "Anyone signed in can report a post or comment. After several reports it is hidden until a moderator looks at it.",
                              "We may refuse or remove content that breaks these rules, and suspend accounts that repeatedly do so."]),
    ("Be kind and accurate", ["Write about your own experience and say when it was: airline and operator rules change often.",
                              "Experiences are not official rules. Always confirm with the airline or operator before you travel; our airline pages link to the official sources.",
                              "Be patient with people asking basic questions: everyone flies with a pet for the first time once."]),
]
GUIDE_KO = [
    ("올릴 수 있는 글", ["강아지·고양이와 함께한 직접 경험: 비행기 (기내 또는 위탁), 기차, 버스, 지하철, 택시, 자동차, 여객선.",
                    "이동장 종류, 반려동물 크기, 계절과 날씨, 직원이 요청한 것, 좋았던 점과 아쉬웠던 점처럼 구체적인 정보가 가장 도움이 돼요.",
                    "댓글로 하는 질문과 친절하고 도움이 되는 답변."]),
    ("허용되지 않는 글", ["직원, 다른 여행객, 특정 집단 등 누구에 대해서든 욕설, 괴롭힘, 비하, 혐오 표현.",
                      "폭력, 위협, 동물 학대 또는 위험한 여행을 부추기는 내용.",
                      "선정적이거나 성인용, 충격적인 내용.",
                      "정치: 어느 나라든 선거, 정당, 정치인, 정치 논쟁. 이 포럼은 반려동물과 여행만 다뤄요.",
                      "광고, 스팸, 제휴·추천 링크, 서비스 판매를 위한 연락처.",
                      "다른 사람의 개인정보 (이름, 사진, 예약 번호, 전화번호)."]),
    ("검토 방식", ["모든 글과 댓글은 게시 전에 검토돼요. 보통 30분 이내에 처리돼요.",
                "자동 필터가 명백한 욕설, 성인물, 정치 관련 내용, 스팸을 즉시 거절해요. 외부 링크가 있는 글은 운영자가 확인해요.",
                "로그인한 사용자는 누구나 글이나 댓글을 신고할 수 있어요. 여러 건 신고되면 운영자가 확인할 때까지 숨겨져요.",
                "규칙을 어긴 글은 거절되거나 삭제될 수 있고, 반복해서 어기는 계정은 정지될 수 있어요."]),
    ("친절하고 정확하게", ["본인의 경험을 언제였는지와 함께 써 주세요. 항공사와 운영사의 규정은 자주 바뀌어요.",
                       "후기는 공식 규정이 아니에요. 여행 전에 항공사나 운영사에 꼭 확인하세요. 사이트의 항공사 페이지에서 공식 출처로 연결돼요.",
                       "기본적인 질문에도 너그럽게 답해 주세요. 누구나 처음은 있으니까요."]),
]


def build_guidelines(B, cfg, mail_html):
    root = "../"
    sec = lambda items: "".join(f"<h2>{B.e(h)}</h2><ul>" + "".join(f"<li>{B.e(x)}</li>" for x in li) + "</ul>" for h, li in items)
    body = f"""<nav class="crumbs"><a href="{{root}}index.html">Home</a> &rsaquo; <a href="index.html">Forum</a> &rsaquo; Community rules</nav>
<h1>Community rules <span class="small" lang="ko">커뮤니티 규칙</span></h1>
{subnav(B, root, "guidelines.html", show_lang=False)}
<p class="small"><a href="#ko" lang="ko">한국어로 보기 ↓</a></p>
<section lang="en"><p class="lead">This forum is for sharing real experiences travelling with dogs and cats. Be kind, be specific, and keep it about pets and travel.</p>
{sec(GUIDE_EN)}
<p>Questions, or a request to remove something: {mail_html}.</p></section>
<section lang="ko" id="ko"><h2 class="fh">커뮤니티 규칙 (한국어)</h2><p class="lead">이 포럼은 강아지·고양이와 함께한 실제 여행 경험을 나누는 곳이에요. 친절하고 구체적으로, 반려동물과 여행 이야기만 나눠 주세요.</p>
{sec(GUIDE_KO)}
<p>문의나 삭제 요청: {mail_html}</p></section>"""
    return B.page(cfg, f"Forum community rules | {cfg['site_name']}",
                  "Community rules for the PetPolicyCheck pet travel forum: be kind, no abuse, violence, adult content, politics or spam; every post is moderated.",
                  body, "forum/guidelines.html", root, [B.bc_ld(cfg, [("Home", ""), ("Forum", "forum/"), ("Community rules", "forum/guidelines.html")])])


# ------------------------------------------------------------------ links from other pages
GUIDE_FILTERS = {"best-airline-approved-soft-carriers": "transport=plane_cabin&carrier=soft_bag",
                 "under-seat-carrier-size-by-airline": "transport=plane_cabin",
                 "pet-carrier-backpacks-for-flying": "transport=plane_cabin",
                 "iata-hard-crates-for-cargo": "transport=plane_hold&carrier=hard_crate",
                 "travel-water-bowls": ""}


def link_box(cfg, root, query, text):
    if not enabled(cfg):
        return ""
    href = f"{root}forum/" + (f"index.html?{query.replace('&', '&amp;')}" if query else "")
    return (f'<aside class="reco fpromo"><h2>From the forum</h2><p>{text} <a href="{href}">Read traveller experiences</a> '
            f'&middot; <a href="{root}forum/new.html">share yours</a>.</p></aside>')


def airline_link(cfg, a, root="../"):
    return link_box(cfg, root, f"airline={a['slug']}", f"How did flying with a pet on {a['name']} actually go?")


def guide_link(cfg, slug, root="../"):
    return link_box(cfg, root, GUIDE_FILTERS.get(slug, ""), "Real trips from pet owners, filtered for this topic.")


# ------------------------------------------------------------------ assets
def write_assets(B, cfg, out, airlines, paths):
    f, _ = fcfg(cfg)
    shutil.copy(HERE / "js" / "forum.js", out / "forum.js")
    (out / "i18n.js").write_text("window.FORUM_I18N=" + json.dumps(I18N, ensure_ascii=False, separators=(",", ":")) + ";\n")
    conf = {"url": f["supabase_url"].strip(), "key": f["supabase_anon_key"].strip(),
            "site": B.site_base(cfg), "cats": {k: v for k, v in CATS.items() if not k.startswith("_")},
            "airlines": {a["slug"]: a["name"] for a in airlines},
            "static": {pid: p for pid, p in paths.items()},
            "contact": f.get("contact_email") or cfg["contact_email"]}
    (out / "config.js").write_text("window.FORUM_CFG=" + json.dumps(conf, ensure_ascii=False, separators=(",", ":")) + ";\n")


class _Safe:
    """Wraps build.py so every escaped string also neutralises "{" (page() substitutes {root} in bodies)."""
    def __init__(self, B):
        self._B = B

    def __getattr__(self, k):
        return getattr(self._B, k)

    def e(self, s):
        return self._B.e(s).replace("{", "&#123;")


def build(B, cfg, airlines, out_root, root_dir):
    """Write site/forum/. Returns [(url, lastmod)] for the sitemap ([] when the forum is off)."""
    global FORUM_VER
    B = _Safe(B)
    import hashlib
    out = out_root / "forum"
    out.mkdir(exist_ok=True)
    if not enabled(cfg):
        (out / "index.html").write_text(coming_soon(B, cfg))
        return []
    FORUM_VER = hashlib.sha1((HERE / "js" / "forum.js").read_bytes() + json.dumps(I18N).encode()).hexdigest()[:8]
    data = fetch_published(cfg, root_dir)
    posts = data.get("posts") or []
    by_post = {}
    for c in data.get("comments") or []:
        by_post.setdefault(c["post_id"], []).append(c)
    paths = {p["id"]: post_path(p) for p in posts}
    airlines_by = {a["slug"]: a for a in airlines}
    f, _ = fcfg(cfg)
    mail_html = B.obf_mail(f.get("contact_email") or cfg["contact_email"])
    write_assets(B, cfg, out, airlines, paths)
    (out / "index.html").write_text(build_index(B, cfg, airlines, posts, paths))
    (out / "post.html").write_text(build_post_live(B, cfg))
    (out / "new.html").write_text(build_new(B, cfg, airlines))
    (out / "account.html").write_text(build_account(B, cfg, mail_html))
    (out / "admin.html").write_text(build_admin(B, cfg))
    (out / "guidelines.html").write_text(build_guidelines(B, cfg, mail_html))
    (out / "p").mkdir(exist_ok=True)
    base = B.site_base(cfg)
    today = dt.date.today().isoformat()
    newest = max([p["created_at"][:10] for p in posts] + [today[:4] + "-01-01"])
    urls = [(f"{base}/forum/", newest), (f"{base}/forum/guidelines.html", "2026-10-22")]
    for p in posts:
        cs = by_post.get(p["id"], [])
        (out / paths[p["id"]]).write_text(build_post_static(B, cfg, p, cs, paths[p["id"]], airlines_by))
        last = max([p["created_at"][:10]] + [c["created_at"][:10] for c in cs])
        urls.append((f"{base}/forum/{paths[p['id']]}", last))
    print(f"  forum: on ({len(posts)} pre-rendered posts)")
    return urls
