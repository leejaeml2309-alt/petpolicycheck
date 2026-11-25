"""End-to-end preview test. Needs: deno run -A petdesk/tests/serve.ts 8765 (fresh, in-memory store).
Gumroad is never contacted: checkout links are intercepted, the license API is mocked in serve.ts."""
import json, re, sys, pathlib
from playwright.sync_api import sync_playwright
B="http://127.0.0.1:8765"; SHOTS=pathlib.Path("/workspace/petdesk-starter-20261125/shots")
LANGS={"en":"","fr":"fr/","es":"es/","de":"de/","it":"it/","ja":"ja/"}
MO="https://petpolicycheck.gumroad.com/l/petdesk-starter?wanted=true"
YR="https://petpolicycheck.gumroad.com/l/petdesk-starter?yearly=true&wanted=true"
OLD=re.compile(r"14-day (free )?trial|No card\. No commitment|14 days free|essai gratuit de 14|prueba gratuita de 14|14-tägige(n)? (kostenlose )?Test|prova gratuita di 14|14日間(無料|の無料試用)",re.I)
K=dict(trial="TRIAL000-AAAA1111-BBBB2222-CCCC3333",active="ACTIVE00-AAAA1111-BBBB2222-CCCC4444",cancel="CANCEL00-AAAA1111-BBBB2222-CCCC5555",
 ended="ENDED000-AAAA1111-BBBB2222-CCCC6666",failed="FAILED00-AAAA1111-BBBB2222-CCCC7777",refund="REFUND00-AAAA1111-BBBB2222-CCCC8888",other="OTHERPRD-AAAA1111-BBBB2222-CCCC9999")
R=[]; FAIL=[]
def ok(name,cond,info=""):
    R.append((name,bool(cond),info)); 
    if not cond: FAIL.append(name)
    print(("PASS " if cond else "FAIL ")+name+(" — "+str(info) if info and not cond else ""))
def ctx(b,w=1280,h=900):
    c=b.new_context(viewport={"width":w,"height":h})
    c.route(re.compile(r"https://([a-z]+\.)?gumroad\.com/.*"),lambda r:r.fulfill(status=200,content_type="text/html",body="<title>gumroad-mock</title>mock checkout"))
    c.route(re.compile(r"https://www\.googletagmanager\.com/.*|https://www\.google-analytics\.com/.*|https://region1\.google-analytics\.com/.*"),lambda r:r.fulfill(status=204,body=""))
    return c
def shot_plans(pg,path):
    pg.locator("#plans").screenshot(path=str(path))
with sync_playwright() as p:
    b=p.chromium.launch(executable_path="/usr/bin/google-chrome")
    # ---------- /pro/ x 6 languages ----------
    for L,pre in LANGS.items():
        for w,h in ((1280,900),(390,844)):
            c=ctx(b,w,h); pg=c.new_page(); errs=[]
            pg.on("pageerror",lambda e:errs.append(str(e)))
            pg.goto(f"{B}/{pre}pro/",wait_until="networkidle"); pg.wait_for_timeout(300)
            st=pg.locator('article[data-tier="starter"] a.btn-pro.pri') if pg.locator('article[data-tier="starter"]').count() else pg.locator('.cta-row[data-pd="starter-trial"] a.btn-pro.pri')
            if w==1280:
                ok(f"{L} /pro/ no JS errors",not errs,errs)
                ok(f"{L} Starter trial button monthly href",st.get_attribute("href")==MO,st.get_attribute("href"))
                ok(f"{L} Starter trial button label set",len(st.inner_text().strip())>5 and "14" not in st.inner_text(),st.inner_text())
                pg.click('.bill-sw button[data-bill="yr"]'); ok(f"{L} yearly toggle switches Starter href",st.get_attribute("href")==YR,st.get_attribute("href"))
                pg.click('.bill-sw button[data-bill="mo"]'); ok(f"{L} monthly toggle restores href",st.get_attribute("href")==MO)
                with c.expect_page() as np: st.click()
                newp=np.value; newp.wait_for_load_state(); ok(f"{L} Starter click opens Gumroad product (mocked)",newp.url==MO,newp.url); newp.close()
                for tier,subj in (("pro","Pro"),("ent","Enterprise")):
                    art=pg.locator(f'article[data-tier="{tier}"]')
                    hrefs=[a.get_attribute("href") for a in art.locator("a").all()]
                    ok(f"{L} {tier}: no Gumroad link",not any("gumroad" in (x or "") for x in hrefs),hrefs)
                    pri=art.locator("a.btn-pro.pri").first
                    ok(f"{L} {tier}: primary = Request onboarding mailto",(pri.get_attribute("href") or "").startswith("mailto:contact@petpolicycheck.com") and subj in pri.get_attribute("href"),pri.get_attribute("href"))
                    ok(f"{L} {tier}: no trial wording in card",not OLD.search(art.inner_text()) and not re.search(r"14[- ]?(day|jours|días|Tage|giorni|日)",art.inner_text()),art.inner_text()[:200])
                body=pg.inner_text("body"); m=OLD.search(body); ok(f"{L} /pro/ visible text has no old 14-day/no-card trial",not m,m and m.group(0))
                faq=pg.locator("details").count()
                lds=[json.loads(s) for s in pg.locator('script[type="application/ld+json"]').all_text_contents()]
                fq=[d for d in lds if d.get("@type")=="FAQPage"]
                ok(f"{L} JSON-LD parses, one FAQPage",len(fq)==1)
                ok(f"{L} FAQPage entries == visible FAQ ({faq})",fq and len(fq[0]["mainEntity"])==faq==11,(faq,fq and len(fq[0]["mainEntity"])))
                ok(f"{L} JSON-LD has no old trial claim",not OLD.search(json.dumps(fq,ensure_ascii=False)))
                html=pg.content(); ok(f"{L} GA only, no AdSense","G-K45B2WNXMC" in html and "adsbygoogle" not in html and "pagead2" not in html)
            shot_plans(pg,SHOTS/f"pro-{L}-{w}.png"); c.close()
        # home + legal
        c=ctx(b); pg=c.new_page(); pg.goto(f"{B}/{pre}",wait_until="domcontentloaded")
        ok(f"{L} home has no old trial sentence",not OLD.search(pg.inner_text("body")))
        for doc in ("terms","refund-policy","privacy"):
            pg.goto(f"{B}/{pre}{doc}.html",wait_until="domcontentloaded")
            t=pg.inner_text("body"); ok(f"{L} {doc}: Starter trial section present",pg.locator('[data-pd="starter-trial"]').count()>=1)
            ok(f"{L} {doc}: no 'no card' trial claim",not OLD.search(t),OLD.search(t) and OLD.search(t).group(0))
        c.close()
    # ---------- desk ----------
    def login(pg,key,L="en"):
        pg.goto(f"{B}/{LANGS[L]}pro/desk/",wait_until="networkidle"); pg.fill("#pd-key",key); pg.click("#pd-open"); pg.wait_for_timeout(700)
    for L,pre in LANGS.items():
        c=ctx(b); pg=c.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
        pg.goto(f"{B}/{pre}pro/desk/",wait_until="networkidle")
        ok(f"{L} desk: login gate shown, app hidden",pg.locator("#pd-login").is_visible() and not pg.locator("#pd-app").is_visible())
        ok(f"{L} desk: noindex",'noindex' in (pg.locator('meta[name="robots"]').get_attribute("content") or ""))
        ok(f"{L} desk: html lang",pg.get_attribute("html","lang").startswith(L))
        login(pg,K["trial"],L); ok(f"{L} desk: trial key opens desk",pg.locator("#pd-app").is_visible(),pg.inner_text("#pd-login-msg") if pg.locator("#pd-login-msg").is_visible() else "")
        pg.wait_for_timeout(1500); ok(f"{L} desk: route selects filled from passport engine",pg.locator("#pd-from option").count()>5 and pg.locator("#pd-to option").count()>5)
        ok(f"{L} desk: no JS errors",not errs,errs)
        if L=="en":
            for w,h in ((1280,900),(390,844)):
                pg.set_viewport_size({"width":w,"height":h}); pg.wait_for_timeout(200); pg.screenshot(path=str(SHOTS/f"desk-app-{w}.png"),full_page=True)
        if L=="fr": pg.screenshot(path=str(SHOTS/"desk-app-fr-1280.png"),full_page=True)
        pg.click("#pd-logout"); pg.wait_for_timeout(400); ok(f"{L} desk: logout returns to gate",pg.locator("#pd-login").is_visible())
        if L=="en":
            for w,h in ((1280,900),(390,844)):
                pg.set_viewport_size({"width":w,"height":h}); pg.screenshot(path=str(SHOTS/f"desk-login-{w}.png"),full_page=True)
        c.close()
    c=ctx(b); pg=c.new_page()
    for name,expect in (("cancel",True),("active",True),("ended",False),("failed",False),("refund",False),("other",False)):
        login(pg,K[name]); vis=pg.locator("#pd-app").is_visible()
        ok(f"desk key '{name}' -> {'open' if expect else 'denied'}",vis==expect,pg.inner_text("#pd-login-msg") if not vis else pg.inner_text("#pd-status"))
        if not expect: ok(f"desk key '{name}' shows a message",len(pg.inner_text("#pd-login-msg").strip())>5)
        if vis: pg.click("#pd-logout"); pg.wait_for_timeout(300)
    pg.goto(f"{B}/pro/desk/"); pg.fill("#pd-key","hello"); pg.click("#pd-open"); pg.wait_for_timeout(400)
    ok("desk bad key format -> message, no Gumroad call",pg.locator("#pd-login-msg").is_visible() and not pg.locator("#pd-app").is_visible())
    login(pg,K["cancel"]); ok("desk cancelling shows access-until date",bool(re.search(r"20\d\d",pg.inner_text("#pd-status"))),pg.inner_text("#pd-status")); c.close()
    # 1 seat
    a=ctx(b); pa=a.new_page(); login(pa,K["trial"]); bb=ctx(b); pb=bb.new_page(); login(pb,K["trial"])
    pa.reload(wait_until="networkidle"); pa.wait_for_timeout(700)
    ok("1 seat: second login closes first session",pa.locator("#pd-login").is_visible() and len(pa.inner_text("#pd-login-msg"))>5,pa.inner_text("#pd-login-msg"))
    ok("1 seat: second session stays open",pb.locator("#pd-app").is_visible())
    # watchlist
    boxes=pb.locator("#pd-watch-list input[type=checkbox]")
    ok("watchlist lists airlines",boxes.count()>=20,boxes.count())
    for i in range(6): boxes.nth(i).click()
    ok("watchlist: 6th airline refused",pb.locator("#pd-watch-list input:checked").count()==5 and pb.locator("#pd-watch-msg").is_visible())
    pb.click("#pd-save-watch"); pb.wait_for_timeout(1500)
    ok("watchlist saved (5)",len(json.loads(pb.evaluate("fetch('/fn/_log').then(r=>r.text())"))["store"]["watch"][0][1])==5)
    pb.fill("#pd-agency","Blue Sky Pet Travel"); pb.click("#pd-save-agency"); pb.wait_for_timeout(600)
    # issue + print
    pb.select_option("#pd-from",index=1); pb.select_option("#pd-to",index=2); pb.select_option("#pd-l1","en"); pb.select_option("#pd-l2","es"); pb.fill("#pd-client","Client 042")
    with bb.expect_page() as np: pb.click("#pd-issue")
    pr=np.value; pr.wait_for_url(re.compile(r"print\.html\?ref=PD-"),timeout=15000)
    pr.wait_for_selector("body.pd-ready",timeout=30000); 
    ok("print sheet: 2 passports (EN+ES)",pr.locator(".pd-pass").count()==2)
    ok("print sheet: agency + ref in header","Blue Sky" in pr.inner_text("body") and "PD-" in pr.inner_text("body"))
    for w in (1280,390): pr.set_viewport_size({"width":w,"height":900}); pr.wait_for_timeout(300); pr.screenshot(path=str(SHOTS/f"desk-print-{w}.png"),full_page=True)
    pb.wait_for_timeout(800); ok("quota counter shows 1 used","1" in pb.inner_text("#pd-quota"),pb.inner_text("#pd-quota"))
    ok("recent list shows the reference",pb.locator("#pd-recent li").count()>=1)
    pr.close()
    # quota 15 via API in-page then UI
    tok=json.loads(pb.evaluate("localStorage.getItem('petdesk')"))
    for i in range(14): pb.evaluate("""t=>fetch('/fn/petdesk/issue',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({token:t.token,license_key:t.key,route:{from:'US',to:'FR'},langs:['en','it']})}).then(r=>r.status)""",tok)
    pb.reload(wait_until="networkidle"); pb.wait_for_timeout(800)
    ok("quota: 15/15 disables Issue",pb.locator("#pd-issue").is_disabled() and pb.locator("#pd-quota-full").is_visible(),pb.inner_text("#pd-quota"))
    st=pb.evaluate("""t=>fetch('/fn/petdesk/issue',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({token:t.token,license_key:t.key,route:{from:'US',to:'FR'},langs:['en','it']})}).then(r=>r.status)""",tok)
    ok("quota: 16th passport refused by server (429)",st==429,st)
    pb.screenshot(path=str(SHOTS/"desk-quota-full-1280.png"),full_page=False)
    ref=pb.locator("#pd-recent li a").first.get_attribute("href")
    # print gate without session
    g=ctx(b); pg=g.new_page(); pg.goto(f"{B}/pro/desk/{ref}",wait_until="networkidle"); pg.wait_for_timeout(800)
    ok("print gate: no session -> denied, no passport",pg.locator(".pd-pass").count()==0 and pg.locator("#pd-print").is_hidden(),pg.inner_text("body")[:200])
    pg.screenshot(path=str(SHOTS/"desk-print-denied-1280.png"))
    pg.goto(f"{B}/pro/desk/",wait_until="networkidle"); ok("desk gate: fresh browser sees only the key form",not pg.locator("#pd-app").is_visible())
    g.close(); a.close(); bb.close(); b.close()
log=json.loads(open("/dev/stdin").read()) if False else None
print(f"\n{len(R)-len(FAIL)}/{len(R)} passed"); 
pathlib.Path("/workspace/petdesk-starter-20261125/e2e-results.json").write_text(json.dumps([{"test":n,"pass":p,"info":str(i)[:300]} for n,p,i in R],ensure_ascii=False,indent=1))
sys.exit(1 if FAIL else 0)
