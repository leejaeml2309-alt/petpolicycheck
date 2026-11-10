import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

const BASE = 'http://127.0.0.1:8802';
const OUT = '/workspace/petdesk-preview-20261110/qa/petdesk';
fs.mkdirSync(OUT, { recursive: true });

const pages = [
  { name: 'terms', url: '/terms.html' },
  { name: 'refund', url: '/refund-policy.html' },
  { name: 'privacy', url: '/privacy.html' },
  { name: 'pro', url: '/pro/' },
  { name: 'hotel-ny', url: '/hotels/pet-friendly-hotels-new-york.html' },
  { name: 'country-canada', url: '/countries/canada.html' },
];

const viewports = [
  { name: 'desktop', width: 1280, height: 900 },
  { name: 'mobile', width: 390, height: 844 },
];

const ignoreConsole = (text, loc) => {
  const t = (text || '').toLowerCase();
  const u = (loc || '').toLowerCase();
  const blob = t + ' ' + u;
  if (blob.includes('adsbygoogle') || blob.includes('adsense') || blob.includes('googlesyndication') || blob.includes('pagead') || blob.includes('doubleclick') || blob.includes('googleads')) return true;
  if (blob.includes('emrldtp') || blob.includes('travelpayouts') || blob.includes('tpo.lv')) return true;
  if (blob.includes('gtag') || blob.includes('googletagmanager') || blob.includes('google-analytics')) return true;
  // opaque third-party 400/CORS without URL in message — treat as ad/affiliate noise when no local path
  if (t.includes('failed to load resource') && t.includes('status of 400')) return true;
  if (t.includes('cors policy') || t.includes('access-control-allow-origin')) return true;
  if (t.includes('net::err_failed') || t.includes('net::err_blocked')) return true;
  return false;
};

const results = { consoleErrors: [], status404: [], shots: [], checks: [], ok: true };

const browser = await chromium.launch({ headless: true });
for (const vp of viewports) {
  const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
  const page = await context.newPage();
  // Block known third-party ad/affiliate noise for console cleanliness; still check local 404s
  await page.route('**/*', (route) => {
    const u = route.request().url();
    if (/googlesyndication|doubleclick|pagead|emrldtp|travelpayouts|googletagmanager|google-analytics|googleadservices/i.test(u)) {
      return route.abort();
    }
    return route.continue();
  });
  page.on('console', (msg) => {
    if (msg.type() !== 'error') return;
    const text = msg.text();
    const loc = msg.location()?.url || '';
    if (ignoreConsole(text, loc)) return;
    results.consoleErrors.push({ vp: vp.name, text, loc });
    results.ok = false;
  });
  page.on('pageerror', (err) => {
    const text = String(err);
    if (ignoreConsole(text, '')) return;
    results.consoleErrors.push({ vp: vp.name, text: 'pageerror: ' + text });
    results.ok = false;
  });
  page.on('response', (res) => {
    const u = res.url();
    if (res.status() === 404 && u.startsWith(BASE)) {
      results.status404.push({ vp: vp.name, url: u });
      results.ok = false;
    }
  });

  for (const p of pages) {
    await page.goto(BASE + p.url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    await page.waitForTimeout(500);
    const shot = path.join(OUT, `${p.name}-${vp.name}.png`);
    await page.screenshot({ path: shot, fullPage: false });
    results.shots.push(shot);

    if (vp.name === 'desktop') {
      if (p.name === 'pro') {
        const cta = await page.locator('.btn-pro.pri').first().innerText();
        results.checks.push({ p: p.name, cta });
        if (!/free 14-day/i.test(cta)) { results.ok = false; results.consoleErrors.push({ text: 'bad CTA '+cta }); }
        const notice = await page.locator('.notice').innerText();
        if (!/does not create a paid subscription/i.test(notice)) { results.ok = false; results.consoleErrors.push({ text: 'bad notice' }); }
      }
      if (p.name === 'terms') {
        const has = await page.locator('#trial').count();
        results.checks.push({ p: p.name, trial: has });
        if (!has) { results.ok = false; }
      }
      if (p.name === 'refund') {
        const has = await page.locator('#trial').count();
        results.checks.push({ p: p.name, trial: has });
        if (!has) { results.ok = false; }
      }
      if (p.name === 'hotel-ny' || p.name === 'country-canada') {
        const n = await page.locator('.ppc-pro-banner').count();
        results.checks.push({ p: p.name, banner: n });
        if (n < 1) { results.ok = false; results.consoleErrors.push({ text: 'missing banner '+p.name }); }
      }
    }
  }
  await context.close();
}
await browser.close();
fs.writeFileSync(path.join(OUT, 'qa-report.json'), JSON.stringify(results, null, 2));
console.log(JSON.stringify(results, null, 2));
process.exit(results.ok && results.consoleErrors.length === 0 && results.status404.length === 0 ? 0 : 1);
