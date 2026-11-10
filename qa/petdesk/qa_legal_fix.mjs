import { chromium } from 'playwright';
import fs from 'fs';
const BASE='http://127.0.0.1:8802';
const OUT='/workspace/petdesk-preview-20261110/qa/petdesk';
const BLOCK=/googlesyndication|doubleclick|pagead|emrldtp|travelpayouts|googletagmanager|google-analytics|googleadservices/i;
const ignore=t=>{t=(t||'').toLowerCase();return /adsbygoogle|adsense|cors|failed to load resource|net::err|status of 400|emrldtp/.test(t)};
const r={consoleErrors:[],status404:[],ok:true};
const browser=await chromium.launch({headless:true});
for (const [w,h,label] of [[1280,900,'desktop'],[390,844,'mobile']]){
  const ctx=await browser.newContext({viewport:{width:w,height:h}});
  const page=await ctx.newPage();
  await page.route('**/*', route=>{const u=route.request().url(); if(BLOCK.test(u)) return route.abort(); return route.continue();});
  page.on('console', msg=>{if(msg.type()!=='error')return; if(ignore(msg.text()))return; r.consoleErrors.push({vp:label,text:msg.text()}); r.ok=false;});
  page.on('response', res=>{if(res.status()===404 && res.url().startsWith(BASE)){r.status404.push(res.url()); r.ok=false;}});
  for (const [url,name] of [['/privacy.html','privacy'],['/refund-policy.html','refund'],['/terms.html','terms']]){
    await page.goto(BASE+url,{waitUntil:'domcontentloaded',timeout:60000});
    await page.waitForTimeout(400);
    const html=await page.content();
    if(label==='desktop'){
      if(name==='privacy'){
        if(!html.includes('mostly static website')||!html.includes('Pet Desk free trial and B2B contact requests')||html.includes('simple static website')){r.ok=false;r.consoleErrors.push({text:'privacy content fail'});}
        await page.locator('h2',{hasText:'Pet Desk free trial'}).scrollIntoViewIfNeeded();
      } else if(name==='refund'){
        if(html.includes('Separate 14-day refund guarantee')||(html.match(/Free trial: no payment to refund/g)||[]).length!==1){r.ok=false;r.consoleErrors.push({text:'refund content fail'});}
        await page.locator('#trial').scrollIntoViewIfNeeded();
      } else {
        if(!html.includes('Paid subscriptions that you choose and confirm through Paddle')||!html.includes('href="#trial"')){r.ok=false;r.consoleErrors.push({text:'terms content fail'});}
        await page.locator('#paddle').scrollIntoViewIfNeeded();
      }
      await page.waitForTimeout(200);
      await page.screenshot({path:`${OUT}/${name}-desktop.png`});
    }
  }
  await ctx.close();
}
await browser.close();
fs.writeFileSync(`${OUT}/qa-legal-fix.json`, JSON.stringify(r,null,2));
console.log(JSON.stringify(r,null,2));
process.exit(r.ok && !r.consoleErrors.length && !r.status404.length ? 0 : 1);
