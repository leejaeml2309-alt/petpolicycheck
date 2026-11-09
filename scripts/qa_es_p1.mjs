import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const BASE = 'http://127.0.0.1:8795';
const OUT = 'qa/es-p1';
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const AD_RE = /googletagmanager|googlesyndication|adsbygoogle|doubleclick|pagead|emrldtp|amazon-adsystem|googleads|FundingChoices|google-analytics|gtag|csp\.withgoogle|ep1\.adtrafficquality|pagead2/i;

const EN_PHRASES = [
  'Skip to content', 'World map', 'Last verified', 'Book your trip', 'Coming soon',
  'Check with airline', 'Official source', 'Guide available', 'Request this country',
  'Become a Route Partner', 'Traps on this route', 'Countdown timeline',
  'Generate passport', 'Print / Save', 'Your brand here', 'Partner with us',
  'Under-seat carrier sizes', 'Pet travel rules', 'We haven\'t verified',
  'Ask the community in the forum', 'Full guide:', 'Snub-nosed breeds:',
];
const ALLOW = /PetPolicyCheck|Paw Passport|Pet Travel Passport|Uber Pet|Lyft Pet|Waymo|Zoox|Tesla|Aviasales|Expedia|Kiwi\.com|SENASICA|OISA|USDA|APHIS|CDC|CFIA|GOV\.UK|IATA|FAVN|Delta|United|American|Alaska|Hawaiian|Aeromexico|Volaris|Viva|B2B Pet Desk|Chrome|PCS|PDF|QR|NWS|CZI|VEHCS|AQS|CBSA|CVI|ISO|RNATT|DHPP|Bordetella|Field-Verified|PetEmbark|PetSafe|Pet Connect|HTTP 403|curl|robots?/i;

function listEsPages() {
  const esRoot = path.join(ROOT, 'site/es');
  const out = [];
  function walk(dir, rel = '') {
    for (const name of fs.readdirSync(dir)) {
      const p = path.join(dir, name);
      const r = rel ? rel + '/' + name : name;
      if (fs.statSync(p).isDirectory()) walk(p, r);
      else if (name.endsWith('.html')) {
        let url = '/es/' + r.replace(/\\/g, '/');
        if (url.endsWith('/index.html')) url = url.slice(0, -'index.html'.length);
        if (url === '/es/index.html') url = '/es/';
        out.push({ id: r.replace(/\.html$/, '').replace(/\//g, '--'), url });
      }
    }
  }
  walk(esRoot);
  return out.sort((a, b) => a.url.localeCompare(b.url));
}

const PAGES = listEsPages();
const EN_SMOKE = ['/', '/airlines/compare/', '/passport/', '/countries/usa-map.html'];
fs.mkdirSync(OUT, { recursive: true });

function cleanConsole(errs) {
  return errs.filter(e => {
    if (AD_RE.test(e)) return false;
    if (/TAGGING|adsbygoogle|gtag|FundingChoices/i.test(e)) return false;
    if (/^Failed to load resource: the server responded with a status of 400/.test(e)) return false;
    if (/^Failed to load resource: net::ERR_FAILED/.test(e)) return false;
    if (/\[Report Only\] Refused to frame/.test(e)) return false;
    return true;
  });
}

async function checkPage(browser, pageMeta, viewport, do404, leftover) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push(String(err)));

  let gotoUrl = BASE + pageMeta.url;
  if (pageMeta.url === '/es/' || pageMeta.url === '/es') gotoUrl = BASE + '/es/?view=map';
  const resp = await page.goto(gotoUrl, { waitUntil: 'networkidle', timeout: 90000 }).catch(() => ({ status: () => 0 }));
  const status = typeof resp.status === 'function' ? resp.status() : 0;

  if ((pageMeta.url || '').includes('-map.html')) {
    try {
      const pick = page.locator('#pick');
      if (await pick.count()) {
        const opts = await pick.locator('option').all();
        if (opts.length > 1) {
          const val = await opts[1].getAttribute('value');
          if (val) { await pick.selectOption(val); await page.waitForTimeout(300); }
        }
      }
    } catch (_) {}
  }

  let brokenInternal = [];
  if (do404) {
    brokenInternal = await page.evaluate(async () => {
      const hrefs = [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(Boolean);
      const seen = new Set(); const bad = [];
      for (const h of hrefs) {
        if (h.startsWith('#') || h.startsWith('mailto:') || h.startsWith('tel:') || h.startsWith('javascript:')) continue;
        let u; try { u = new URL(h, location.href); } catch { continue; }
        if (u.origin !== location.origin) continue;
        const key = u.pathname + u.search; if (seen.has(key)) continue; seen.add(key);
        try { const r = await fetch(key); if (r.status === 404) bad.push(key); } catch { bad.push(key + ' fail'); }
      }
      return bad;
    });
  }

  let leftovers = [];
  if (leftover) {
    leftovers = await page.evaluate((phrases) => {
      function vis(el) {
        if (!el || el.closest('script,style,noscript,template')) return false;
        const st = getComputedStyle(el);
        return !(st && (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0'));
      }
      const found = [];
      const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
      let n;
      while ((n = walker.nextNode())) {
        const t = (n.textContent || '').replace(/\s+/g, ' ').trim();
        if (!t || t.length < 4 || !vis(n.parentElement)) continue;
        for (const ph of phrases) {
          if (t.includes(ph)) found.push(ph + ' :: ' + t.slice(0, 100));
        }
      }
      return found;
    }, EN_PHRASES);
    leftovers = leftovers.filter(x => !ALLOW.test(x));
  }

  const tag = viewport.width >= 1000 ? 'desktop' : 'mobile';
  await page.screenshot({ path: path.join(OUT, `${pageMeta.id}-${tag}.png`), fullPage: false });
  await context.close();
  return { id: pageMeta.id, url: pageMeta.url, viewport: viewport.width, status, consoleErrors: cleanConsole(consoleErrors), brokenInternal, leftovers };
}

const report = { pages: [], enSmoke: [], summary: {} };
const browser = await chromium.launch({ headless: true });
for (const meta of PAGES) {
  for (const vp of [{ width: 1280, height: 800 }, { width: 390, height: 844 }]) {
    const r = await checkPage(browser, meta, vp, vp.width === 1280, vp.width === 1280);
    report.pages.push(r);
    const flag = (r.consoleErrors.length || r.brokenInternal.length) ? ' FAIL' : '';
    console.log(`${r.status} ${vp.width} ${meta.url} console=${r.consoleErrors.length} 404=${r.brokenInternal.length} en=${r.leftovers.length}${flag}`);
    if (r.consoleErrors.length) console.log(' ', r.consoleErrors.slice(0, 3));
    if (r.brokenInternal.length) console.log(' ', r.brokenInternal.slice(0, 5));
    if (r.leftovers.length) console.log('  EN', r.leftovers.slice(0, 5));
  }
}
for (const u of EN_SMOKE) {
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  page.on('pageerror', e => errs.push(String(e)));
  const resp = await page.goto(BASE + u, { waitUntil: 'networkidle', timeout: 90000 });
  const cleaned = cleanConsole(errs);
  report.enSmoke.push({ url: u, status: resp.status(), consoleErrors: cleaned });
  console.log(`EN ${u} status=${resp.status()} console=${cleaned.length}`);
  await ctx.close();
}
await browser.close();
report.summary = {
  pages: PAGES.length,
  checks: report.pages.length,
  consoleErrors: report.pages.reduce((n, p) => n + p.consoleErrors.length, 0),
  brokenInternal: report.pages.reduce((n, p) => n + p.brokenInternal.length, 0),
  leftoverHits: report.pages.reduce((n, p) => n + p.leftovers.length, 0),
  enSmokeErrors: report.enSmoke.reduce((n, p) => n + p.consoleErrors.length, 0),
};
fs.writeFileSync(path.join(OUT, 'qa-report.json'), JSON.stringify(report, null, 2));
console.log('SUMMARY', report.summary);
if (report.summary.consoleErrors || report.summary.brokenInternal || report.summary.enSmokeErrors) process.exitCode = 1;
