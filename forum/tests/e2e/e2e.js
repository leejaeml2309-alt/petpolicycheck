const puppeteer = require('puppeteer-core');
const { execSync } = require('child_process');
const B = 'http://localhost:8800/forum/';
const jwt = (r, s, e) => execSync(`python3 jwt.py ${r} ${s || ''} ${e || ''}`).toString().trim();
const sess = (id, email) => JSON.stringify({ access_token: jwt('authenticated', id, email), refresh_token: 'x', token_type: 'bearer', expires_in: 2592000,
  expires_at: Math.floor(Date.now() / 1000) + 2592000, user: { id, email, aud: 'authenticated', role: 'authenticated', app_metadata: {}, user_metadata: {} } });
const U1 = ['11111111-1111-1111-1111-111111111111', 'mina@example.com'], AD = ['33333333-3333-3333-3333-333333333333', 'owner@example.com'];
const ok = (c, m) => { console.log((c ? 'PASS ' : 'FAIL ') + m); if (!c) process.exitCode = 1; };
(async () => {
  const br = await puppeteer.launch({ executablePath: '/usr/bin/google-chrome', headless: 'new', args: ['--no-sandbox'] });
  const pg = await br.newPage();
  const errs = [];
  pg.on('pageerror', e => errs.push('pageerror ' + e.message));
  pg.on('console', m => { if (m.type() === 'error' && !/adsbygoogle|googlesyndication|emrldtp|ERR_|Failed to load resource/.test(m.text())) errs.push('console ' + m.text()); });
  pg.on('dialog', d => d.accept(d.type() === 'prompt' ? 'test report' : undefined));
  await pg.setViewport({ width: 1200, height: 900 });
  const txt = async s => pg.$eval(s, e => e.textContent.trim()).catch(() => null);
  const wait = (fn, ...a) => pg.waitForFunction(fn, { timeout: 8000 }, ...a).then(() => true).catch(() => false);

  await pg.goto(B + 'index.html?lang=en', { waitUntil: 'domcontentloaded' });
  ok(await wait(() => /3 experiences/.test(document.getElementById('fstatus').textContent)), 'index live list: ' + await txt('#fstatus'));
  await pg.screenshot({ path: '/tmp/e2e/index.png', fullPage: true });
  await pg.goto(B + 'index.html?transport=train', { waitUntil: 'domcontentloaded' });
  ok(await wait(() => /1 experiences/.test(document.getElementById('fstatus').textContent)), 'filter transport=train: ' + await txt('#fstatus'));
  await pg.goto(B + 'index.html?lang=en&weight=w25_40&q=winter', { waitUntil: 'domcontentloaded' });
  ok(await wait(() => document.querySelectorAll('#flist li').length === 1), 'filter weight+q');
  await pg.click('[data-setlang=ko]');
  ok(await wait(() => document.querySelector('h1').textContent === '반려동물 여행 포럼'), 'lang switch to ko');
  ok(/lang=ko/.test(pg.url()), 'lang in URL');
  await pg.screenshot({ path: '/tmp/e2e/index-ko.png', fullPage: true });
  await pg.goto(B + 'guidelines.html', { waitUntil: 'domcontentloaded' });
  ok(await pg.evaluate(() => localStorage.getItem('ppc_lang')) === 'ko', 'lang persisted');
  await pg.goto(B + 'index.html?lang=en', { waitUntil: 'domcontentloaded' });

  const statics = await pg.evaluate(() => window.FORUM_CFG.static);
  const kpath = Object.values(statics).find(p => /korean-air/.test(p));
  await pg.goto(B + kpath, { waitUntil: 'domcontentloaded' });
  ok(await wait(() => document.querySelector('.fcomments .note a')), 'static post anon: sign-in prompt');
  ok(/Korean Air pet policy/.test(await txt('.fpost')), 'airline link on post');

  // signed in as user 1
  await pg.evaluate(s => localStorage.setItem('sb-localhost-auth-token', s), sess(...U1));
  await pg.goto(B + 'new.html', { waitUntil: 'domcontentloaded' });
  ok(await wait(() => !document.getElementById('newpost').hidden), 'new post form visible when signed in');
  await pg.type('#nf-title', 'Ferry to Ulleungdo with a Jindo');
  await pg.select('#nf-transport', 'ferry'); await pg.select('#nf-species', 'dog'); await pg.select('#nf-weight', 'w15_25');
  await pg.type('#nf-body', 'The ferry had a pet room downstairs; we had to keep her in a crate for the whole three hour crossing.');
  await pg.type('#nf-trip_date', '052026');
  await pg.click('#newpost button[type=submit]');
  ok(await wait(() => !document.getElementById('nf-done').hidden), 'post submitted -> pending notice: ' + await txt('#nf-done p'));
  await pg.evaluate(s => localStorage.setItem('sb-localhost-auth-token', s), sess('22222222-2222-2222-2222-222222222222', 'joon@example.com'));
  await pg.goto(B + 'new.html?lang=ko', { waitUntil: 'domcontentloaded' });
  await wait(() => !document.getElementById('newpost').hidden);
  ok(await pg.$eval('#nf-lang', e => e.value) === 'ko', 'post lang defaults to UI lang');
  await pg.select('#nf-transport', 'subway');
  ok(await pg.$eval('#subway-note', e => !e.hidden), 'subway note shown');
  await pg.type('#nf-title', '지하철 이야기'); await pg.select('#nf-species', 'cat');
  await pg.type('#nf-body', '고양이랑 지하철 탔는데 윤석열 얘기하는 사람들이 많았어요. 이동장은 작은 걸로 준비했어요.');
  await pg.click('#newpost button[type=submit]');
  ok(await wait(() => !document.getElementById('nf-err').hidden), 'political KO post rejected: ' + await txt('#nf-err'));

  await pg.evaluate(s => localStorage.setItem('sb-localhost-auth-token', s), sess(...U1));
  await pg.goto(B + kpath, { waitUntil: 'domcontentloaded' });
  ok(await wait(() => document.getElementById('fc-form')), 'comment form visible');
  await pg.type('#fc-body', 'Thanks, very useful!');
  await pg.click('#fc-form button');
  ok(await wait(() => !document.querySelector('#fc-form .verified').hidden), 'comment pending notice');
  await pg.goto(B + 'account.html', { waitUntil: 'domcontentloaded' });
  ok(await wait(() => !document.getElementById('acc-in').hidden && document.querySelectorAll('#acc-posts li').length >= 5), 'account lists my posts');
  ok(await pg.$eval('#acc-admin', e => e.hidden), 'no admin link for normal user');
  ok(/spam aren|스팸/.test(await txt('#acc-posts')), 'rejection reason shown');
  await pg.screenshot({ path: '/tmp/e2e/account.png', fullPage: true });
  await pg.goto(B + 'admin.html', { waitUntil: 'domcontentloaded' });
  ok(await wait(() => !document.getElementById('adm-only').hidden), 'admin page refuses normal user');

  // admin
  await pg.evaluate(s => localStorage.setItem('sb-localhost-auth-token', s), sess(...AD));
  await pg.goto(B + kpath, { waitUntil: 'domcontentloaded' });
  await wait(() => document.querySelector('.fpost .factions button'));
  await pg.click('.fpost .factions button');
  ok(await wait(() => /Thank you|감사합니다/.test(document.querySelector('.fpost .factions').textContent)), 'report post: ' + await txt('.fpost .factions'));
  await pg.goto(B + 'admin.html', { waitUntil: 'domcontentloaded' });
  ok(await wait(() => document.querySelectorAll('.fadm').length >= 2), 'admin queue: ' + await txt('#adm-count'));
  await pg.screenshot({ path: '/tmp/e2e/admin.png', fullPage: true });
  const n = await pg.$$eval('.fadm', l => l.length);
  for (let i = 0; i < n; i++) {
    const t = await pg.$eval(`.fadm:nth-child(${i + 1})`, e => e.textContent);
    if (/Ferry|Thanks, very useful/.test(t)) await pg.click(`.fadm:nth-child(${i + 1}) .fbtn:not(.alt):not(.warnbtn)`);
  }
  ok(await wait(() => document.querySelectorAll('.fadm.done').length >= 2), 'admin publish');
  await pg.evaluate(() => localStorage.clear());
  await pg.goto(B + kpath, { waitUntil: 'domcontentloaded' });
  ok(await wait(() => document.querySelectorAll('#fclist li').length === 1), 'published comment visible to anon');
  await pg.goto(B + 'post.html?id=' + Object.keys(statics)[0], { waitUntil: 'domcontentloaded' });
  ok(await wait(() => /\/p\//.test(location.href)), 'post.html redirects to static page');
  await pg.goto(B + 'post.html?id=11111111-2222-3333-4444-555555555555', { waitUntil: 'domcontentloaded' });
  ok(await wait(() => /not available/.test(document.getElementById('fpost-static').textContent)), 'missing post notice');
  await pg.setViewport({ width: 390, height: 800 });
  await pg.goto(B + 'index.html?lang=ko', { waitUntil: 'domcontentloaded' });
  await wait(() => /후기 4/.test(document.getElementById('fstatus').textContent));
  await pg.screenshot({ path: '/tmp/e2e/index-mobile.png', fullPage: true });
  await pg.goto(B + 'account.html?lang=en', { waitUntil: 'domcontentloaded' });
  await wait(() => !document.getElementById('acc-out').hidden);
  await pg.screenshot({ path: '/tmp/e2e/signin-mobile.png', fullPage: true });
  ok(errs.length === 0, 'no JS errors ' + JSON.stringify(errs));
  await br.close();
})();
