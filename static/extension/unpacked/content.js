/* Pets Allowed? content pill v1.0.1 — local prototype */
/* Floating, collapsible pill (bottom-right) on matched airline/hotel pages. Shadow DOM so it never inherits or breaks the site's CSS.
   Never covers checkout: 1 small pill, collapsible to a 34px paw; state remembered per site in chrome.storage.local. */
(function(){
  if(window.__ppcPill) return; window.__ppcPill=1;
  var url=(window.__PPC_URL__)||location.href, m=PPC_MATCH.match(url); if(!m) return;
  var host=new URL(url).hostname.replace(/^www\./,''), key='ppc-collapsed-'+host;
  var C={flight:'#98c6cc',hotel:'#d3a0b1'}[m.theme];
  var base='https://petpolicycheck.com/';
  var r=m.rec, rows=[];
  if(m.type==='airline'){rows=[['Cabin',r.cabin?'Yes':'No'],['Fee',r.fee||'Check with airline'],['Max bag',r.dims||'Not stated'],['Weight',r.weight]]}
  else if(m.type==='hotel'){rows=[['Fee',r.fee||'Varies / ask hotel'],['Weight',r.weight||'Varies'],['Pets/room',r.pets||'Varies']]}
  else rows=[['Tip','Rules differ per property: open the hotel’s own pet policy']];
  var host$=document.createElement('div'); host$.setAttribute('data-ppc','pill');
  host$.style.cssText='position:fixed;right:16px;bottom:16px;z-index:2147483000';
  var sh=host$.attachShadow({mode:'open'});
  sh.innerHTML='<style>'+
   ':host{all:initial}*{box-sizing:border-box;font-family:Inter,system-ui,-apple-system,Segoe UI,Arial,sans-serif}'+
   '.p{display:flex;align-items:center;gap:8px;height:38px;padding:0 6px 0 6px;border-radius:99px;background:#0b1719;color:#f5ecd6;border:1.5px solid #d9b765;box-shadow:0 8px 24px #0006;cursor:pointer;font:600 13px/1 Inter,system-ui,sans-serif}'+
   '.ic{width:26px;height:26px;border-radius:7px;background:#11252a;display:grid;place-items:center;box-shadow:inset 0 0 0 1px '+C+'99;color:'+C+'}'+
   '.t{white-space:nowrap;padding-right:4px}.x{all:unset;width:22px;height:22px;border-radius:50%;display:grid;place-items:center;color:#a7b0a2;font-size:14px;cursor:pointer}.x:hover{background:#173236}'+
   '.mini{width:38px;height:38px;border-radius:50%;padding:0;justify-content:center}.mini .t,.mini .x{display:none}'+
   '.card{position:absolute;right:0;bottom:48px;width:290px;background:#11252a;border:1px solid #3a5a56;border-top:3px solid '+C+';border-radius:14px;padding:12px 14px;color:#ece4d0;box-shadow:0 18px 40px #0008;display:none}'+
   '.card.on{display:block}.card h4{margin:0 0 2px;font:400 16px Marcellus,Georgia,serif;color:#f5ecd6}.card small{color:#a7b0a2;font-size:11px}'+
   '.r{display:grid;grid-template-columns:72px 1fr;gap:8px;padding:6px 0;border-top:1px solid #23413f;font-size:12px}.r b{color:#a7b0a2;font-weight:600;font-size:10px;letter-spacing:.1em;text-transform:uppercase;padding-top:2px}'+
   '.a{display:block;margin-top:10px;text-align:center;padding:8px;border-radius:99px;background:#d9b765;color:#0b1719;text-decoration:none;font-weight:700;font-size:12px}'+
   '</style>'+
   '<div class="card" id="c"><h4>'+r.name+'</h4><small>PetPolicyCheck · verified '+(r.verified||'')+'</small>'+rows.map(function(x){return '<div class="r"><b>'+x[0]+'</b><span>'+x[1]+'</span></div>'}).join('')+
   '<a class="a" target="_blank" rel="noopener" href="'+base+(r.page||'')+'">Open full sheet on PetPolicyCheck</a></div>'+
   '<div class="p" id="p" role="button" tabindex="0" aria-label="PetPolicyCheck pet rules"><span class="ic"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><ellipse cx="12" cy="15.6" rx="4.2" ry="3.4"/><circle cx="6.4" cy="10.6" r="1.7"/><circle cx="9.6" cy="6.9" r="1.8"/><circle cx="14.4" cy="6.9" r="1.8"/><circle cx="17.6" cy="10.6" r="1.7"/></svg></span><span class="t">'+m.pill+'</span><button class="x" id="x" aria-label="Collapse">×</button></div>';
  var p=sh.getElementById('p'),c=sh.getElementById('c'),x=sh.getElementById('x');
  function setMini(v){p.classList.toggle('mini',v);if(v)c.classList.remove('on');try{chrome.storage.local.set({[key]:v})}catch(e){}}
  p.addEventListener('click',function(e){if(e.target===x) return; if(p.classList.contains('mini')){setMini(false);return} c.classList.toggle('on')});
  x.addEventListener('click',function(e){e.stopPropagation();setMini(true)});
  try{chrome.storage.local.get(key,function(o){if(o&&o[key])setMini(true)})}catch(e){}
  if(window.__PPC_OPEN__) c.classList.add('on');
  (document.body||document.documentElement).appendChild(host$);
})();
