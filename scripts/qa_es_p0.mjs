import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = 'http://127.0.0.1:8795';
const OUT = 'qa/es-p0';
const PAGES = [
  { id: 'home', url: '/es/', shot: true },
  { id: 'mexico', url: '/es/countries/mexico.html' },
  { id: 'mexico-map', url: '/es/countries/mexico-map.html', shot: true, selectState: true },
  { id: 'usa-mexico', url: '/es/routes/usa-mexico.html', shot: true },
  { id: 'usa-to-mexico-alaska', url: '/es/routes/usa-to-mexico-alaska.html' },
  { id: 'usa-to-mexico-american', url: '/es/routes/usa-to-mexico-american.html' },
  { id: 'usa-to-mexico-delta', url: '/es/routes/usa-to-mexico-delta.html' },
  { id: 'usa-to-mexico-united', url: '/es/routes/usa-to-mexico-united.html' },
  { id: 'mexico-to-usa-alaska', url: '/es/routes/mexico-to-usa-alaska.html' },
  { id: 'mexico-to-usa-american', url: '/es/routes/mexico-to-usa-american.html' },
  { id: 'mexico-to-usa-delta', url: '/es/routes/mexico-to-usa-delta.html' },
  { id: 'mexico-to-usa-united', url: '/es/routes/mexico-to-usa-united.html' },
  { id: 'aeromexico', url: '/es/airlines/aeromexico.html', shot: true },
  { id: 'volaris', url: '/es/airlines/volaris.html' },
  { id: 'viva-aerobus', url: '/es/airlines/viva-aerobus.html' },
  { id: 'delta', url: '/es/airlines/delta.html' },
  { id: 'united', url: '/es/airlines/united.html' },
  { id: 'american', url: '/es/airlines/american.html' },
  { id: 'alaska', url: '/es/airlines/alaska.html' },
  { id: 'comparator', url: '/es/airlines/compare/', shot: true },
  { id: 'passport', url: '/es/passport/', shot: true },
];

const EN_SMOKE = ['/', '/airlines/aeromexico.html', '/countries/mexico-map.html', '/passport/', '/airlines/compare/'];

// Common English UI leftovers (ignore brand names, official terms, code)
const EN_PHRASES = [
  'Skip to content', 'World map', 'Last verified', 'Book your trip', 'Coming soon',
  'Check with airline', 'Official source', 'Health certificate', 'Guide available',
  'Request this country', 'Country guides', 'All countries', 'Full USA guide',
  'Become a Route Partner', 'After landing', 'Traps on this route', 'Countdown timeline',
  'Route partners', 'Generate passport', 'Print / Save', 'copied ✓',
  'Airlines', 'Compare', 'Products', 'Guides', 'Updates', 'About', 'Veterans',
  'For Business', 'Advertise', 'Menu', 'Partner with us', 'Your brand here',
];

const ALLOW_EN = new Set([
  'PetPolicyCheck', 'Paw Passport', 'Pet Travel Passport', 'Uber Pet', 'Lyft Pet',
  'Waymo', 'Zoox', 'Tesla', 'Robotaxi', 'Aviasales', 'Expedia', 'Kiwi.com',
  'SENASICA', 'OISA', 'USDA', 'APHIS', 'CDC', 'CFIA', 'GOV.UK', 'IATA', 'FAVN',
  'Delta', 'United', 'American', 'Alaska', 'Hawaiian', 'Aeromexico', 'Volaris', 'Viva',
  'B2B Pet Desk', 'Chrome', 'PCS', 'KOREA', 'OK', 'PDF', 'QR', 'IAG', 'PetEmbark',
  'PetSafe', 'Pet Connect', 'AC Animals', 'DOT', 'NWS', 'CZI', 'VEHCS',
]);

fs.mkdirSync(OUT, { recursive: true });

async function checkPage(browser, pageMeta, viewport) {
  const context = await browser.newContext({
    viewport: viewport,
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();
  const consoleErrors = [];
  const failed = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', err => consoleErrors.push(String(err)));
  page.on('requestfailed', req => {
    const u = req.url();
    if (u.includes('googletagmanager') || u.includes('googlesyndication') || u.includes('adsbygoogle') || u.includes('emrldtp') || u.includes('doubleclick') || u.includes('pagead')) return;
    failed.push({ url: u, err: req.failure()?.errorText });
  });

  const url = BASE + pageMeta.url;
  const resp = await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 }).catch(e => ({ ok: () => false, status: () => 0, _e: e }));
  const status = typeof resp.status === 'function' ? resp.status() : 0;

  // Unlock intro on home
  if (pageMeta.id === 'home') {
    await page.goto(BASE + '/es/?view=map', { waitUntil: 'networkidle', timeout: 60000 });
  }

  if (pageMeta.selectState) {
    // Click a Mexican state path if present
    await page.waitForTimeout(800);
    const clicked = await page.evaluate(() => {
      const sel = document.querySelector('#mexico-map path.state, #mx-map path, svg path.state, .mapbox path, #map svg path');
      if (sel) { sel.dispatchEvent(new MouseEvent('click', { bubbles: true })); return true; }
      // try any path in country map
      const paths = document.querySelectorAll('svg path');
      for (const p of paths) {
        if ((p.getAttribute('d') || '').length > 50) { p.dispatchEvent(new MouseEvent('click', { bubbles: true })); return true; }
      }
      return false;
    });
    await page.waitForTimeout(500);
    pageMeta._clicked = clicked;
  }

  // Leftover English in visible text
  const leftovers = await page.evaluate((phrases) => {
    function visible(el) {
      if (!el || el.closest('script,style,noscript,template')) return false;
      const st = window.getComputedStyle(el);
      if (st && (st.display === 'none' || st.visibility === 'hidden' || st.opacity === '0')) return false;
      return true;
    }
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const found = [];
    let n;
    while ((n = walker.nextNode())) {
      const t = (n.textContent || '').replace(/\s+/g, ' ').trim();
      if (!t || t.length < 3) continue;
      if (!visible(n.parentElement)) continue;
      for (const ph of phrases) {
        if (t.includes(ph)) found.push(ph + ' :: ' + t.slice(0, 120));
      }
    }
    return found;
  }, EN_PHRASES);

  // Internal link 404 check (same-origin)
  const broken = await page.evaluate(async (base) => {
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
    const uniq = [...new Set(abs)].slice(0, 80);
    const bad = [];
    for (const p of uniq) {
      try {
        const r = await fetch(p, { method: 'GET' });
        if (r.status === 404) bad.push(p);
      } catch (e) { bad.push(p + ' (fetch fail)'); }
    }
    return bad;
  }, BASE);

  const label = viewport.width + 'x' + viewport.height;
  if (pageMeta.shot) {
    const shotName = `${pageMeta.id}-${viewport.width === 1280 ? 'desktop' : 'mobile'}.png`;
    await page.screenshot({ path: path.join(OUT, shotName), fullPage: false });
  }

  await context.close();
  return {
    id: pageMeta.id,
    url: pageMeta.url,
    viewport: label,
    status,
    consoleErrors: consoleErrors.filter(e => !/adsbygoogle|gtag|TAGGING|Failed to load resource.*ads|net::ERR_FAILED.*goog/.test(e)),
    failedRequests: failed,
    leftovers,
    brokenInternal: broken,
    clickedState: pageMeta._clicked,
  };
}

const report = { pages: [], enSmoke: [], summary: {} };
const browser = await chromium.launch({ headless: true });

for (const meta of PAGES) {
  for (const vp of [{ width: 1280, height: 800 }, { width: 390, height: 844 }]) {
    const r = await checkPage(browser, { ...meta }, vp);
    report.pages.push(r);
    process.stdout.write(`${r.id} ${r.viewport} status=${r.status} err=${r.consoleErrors.length} failReq=${r.failedRequests.length} en=${r.leftovers.length} 404=${r.brokenInternal.length}\n`);
  }
}

for (const u of EN_SMOKE) {
  for (const vp of [{ width: 1280, height: 800 }]) {
    const context = await browser.newContext({ viewport: vp });
    const page = await context.newPage();
    const errs = [];
    page.on('pageerror', e => errs.push(String(e)));
    page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    const resp = await page.goto(BASE + u, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForTimeout(400);
    report.enSmoke.push({ url: u, status: resp.status(), errs: errs.filter(e => !/adsbygoogle|gtag|TAGGING/.test(e)) });
    await context.close();
    process.stdout.write(`EN ${u} status=${resp.status()} err=${errs.length}\n`);
  }
}

await browser.close();

const flat = report.pages;
report.summary = {
  pages: PAGES.length,
  totalRuns: flat.length,
  consoleErrors: flat.reduce((n, p) => n + p.consoleErrors.length, 0),
  failedRequests: flat.reduce((n, p) => n + p.failedRequests.length, 0),
  brokenInternal: flat.reduce((n, p) => n + p.brokenInternal.length, 0),
  leftoverHits: flat.reduce((n, p) => n + p.leftovers.length, 0),
  enSmokeErrors: report.enSmoke.reduce((n, p) => n + p.errs.length, 0),
};
fs.writeFileSync(path.join(OUT, 'report.json'), JSON.stringify(report, null, 2));

// Leftover English by page (deduped)
const byPage = {};
for (const p of flat) {
  if (!byPage[p.id]) byPage[p.id] = new Set();
  p.leftovers.forEach(x => byPage[p.id].add(x.split(' :: ')[0]));
}
const leftoverSummary = Object.fromEntries(Object.entries(byPage).map(([k, v]) => [k, [...v]]));
fs.writeFileSync(path.join(OUT, 'leftover-en.json'), JSON.stringify(leftoverSummary, null, 2));
console.log('SUMMARY', report.summary);
console.log('LEFTOVER', leftoverSummary);
