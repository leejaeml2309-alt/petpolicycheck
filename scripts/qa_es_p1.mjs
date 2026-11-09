import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const BASE = 'http://127.0.0.1:8795';
const OUT = 'qa/es-p1';
const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const AD_RE = /googletagmanager|googlesyndication|adsbygoogle|doubleclick|pagead|emrldtp|amazon-adsystem|googleads|FundingChoices|google-analytics|gtag/i;

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
        out.push({ id: r.replace(/\.html$/, '').replace(/\//g, '--'), url, shot: true });
      }
    }
  }
  walk(esRoot);
  return out.sort((a, b) => a.url.localeCompare(b.url));
}

const PAGES = listEsPages();
fs.mkdirSync(OUT, { recursive: true });

async function checkPage(browser, pageMeta, viewport, do404) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1 });
  const page = await context.newPage();
  const consoleErrors = [];
  const failed = [];
  page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
  page.on('pageerror', err => consoleErrors.push(String(err)));
  page.on('requestfailed', req => {
    const u = req.url();
    if (AD_RE.test(u)) return;
    failed.push({ url: u, err: req.failure()?.errorText });
  });

  let gotoUrl = BASE + pageMeta.url;
  if (pageMeta.url === '/es/' || pageMeta.url === '/es') gotoUrl = BASE + '/es/?view=map';
  const resp = await page.goto(gotoUrl, { waitUntil: 'networkidle', timeout: 90000 }).catch(e => ({ status: () => 0, _e: String(e) }));
  const status = typeof resp.status === 'function' ? resp.status() : 0;

  if (pageMeta.url.includes('-map.html')) {
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
      const hrefs = [...document.querySelectorAll('a[href]')]
        .map(a => a.getAttribute('href'))
        .filter(h => h && !h.startsWith('mailto:') && !h.startsWith('tel:') && !h.startsWith('javascript:') && !h.startsWith('#'));
      const abs = [];
      for (const h of hrefs) {
        try {
          const u = new URL(h, location.href);
          if (u.origin !== location.origin) continue;
          abs.push(u.pathname + u.search);
        } catch (e) {}
      }
      const uniq = [...new Set(abs)].slice(0, 100);
      const bad = [];
      for (const p of uniq) {
        try {
          const r = await fetch(p, { method: 'GET' });
          if (r.status === 404) bad.push(p);
        } catch (e) { bad.push(p + ' (fetch fail)'); }
      }
      return bad;
    });
  }

  const tag = viewport.width >= 1000 ? 'desktop' : 'mobile';
  await page.screenshot({ path: path.join(OUT, `${pageMeta.id}-${tag}.png`), fullPage: false });

  const cleaned = consoleErrors.filter(e => {
    if (AD_RE.test(e)) return false;
    if (/TAGGING|adsbygoogle|gtag|FundingChoices|ep1\.adtrafficquality/i.test(e)) return false;
    // Chrome omits the URL for many ad failures; treat bare 400 / ERR_FAILED as ads.
    if (/^Failed to load resource: the server responded with a status of 400/.test(e)) return false;
    if (/^Failed to load resource: net::ERR_FAILED/.test(e)) return false;
    if (/\[Report Only\] Refused to frame/.test(e)) return false;
    return true;
  });
  await context.close();
  return { id: pageMeta.id, url: pageMeta.url, viewport: viewport.width, status, consoleErrors: cleaned, failed, brokenInternal };
}

const report = { pages: [], summary: {} };
const browser = await chromium.launch({ headless: true });
for (const meta of PAGES) {
  for (const vp of [{ width: 1280, height: 800 }, { width: 390, height: 844 }]) {
    const r = await checkPage(browser, meta, vp, vp.width === 1280);
    report.pages.push(r);
    const line = `${r.status} ${vp.width} ${meta.url} console=${r.consoleErrors.length} 404=${r.brokenInternal.length}`;
    console.log(line);
    if (r.consoleErrors.length) console.log('  ', r.consoleErrors.slice(0, 4));
    if (r.brokenInternal.length) console.log('  404', r.brokenInternal.slice(0, 8));
  }
}
await browser.close();
report.summary = {
  pages: PAGES.length,
  checks: report.pages.length,
  consoleErrors: report.pages.reduce((n, p) => n + p.consoleErrors.length, 0),
  brokenInternal: report.pages.reduce((n, p) => n + p.brokenInternal.length, 0),
};
fs.writeFileSync(path.join(OUT, 'qa-report.json'), JSON.stringify(report, null, 2));
console.log('SUMMARY', report.summary);
if (report.summary.consoleErrors || report.summary.brokenInternal) process.exitCode = 1;
