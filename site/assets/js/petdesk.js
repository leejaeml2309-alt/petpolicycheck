/* Pet Desk Starter client. All access checks happen server-side in the Supabase Edge Function
   `petdesk` (Gumroad license verify + HMAC session). This file only renders the UI. */
(function(){
'use strict';
var LOCAL=/^(127\.0\.0\.1|localhost)$/.test(location.hostname);
var API=LOCAL?'/fn/petdesk/':'https://uouccgyeujtmbeeneuwq.supabase.co/functions/v1/petdesk/';
var PUBKEY='sb_publishable_J3NaUoRdx7d5FBDfsFqGFQ__GY9uwYo';
var L=(document.documentElement.getAttribute('data-desk-lang')||'en');
var T=(window.PETDESK_I18N||{})[L]||(window.PETDESK_I18N||{}).en;
var BASE=document.documentElement.getAttribute('data-site-root')||'../../';
var LANG_PATH={en:'',fr:'fr/',es:'es/',de:'de/',it:'it/',ja:'ja/'};
var S={token:null,key:null,acc:null};
function $(s,r){return (r||document).querySelector(s);}
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
function t(k,v){var s=T[k]||(window.PETDESK_I18N.en[k])||k;if(v)Object.keys(v).forEach(function(x){s=s.split('{'+x+'}').join(v[x]);});return s;}
function fmtDate(iso){try{return new Date(iso).toLocaleDateString(L==='en'?'en-US':L,{year:'numeric',month:'long',day:'numeric'});}catch(e){return iso.slice(0,10);}}
function save(){try{localStorage.setItem('petdesk',JSON.stringify({token:S.token,key:S.key}));}catch(e){}}
function load(){try{var j=JSON.parse(localStorage.getItem('petdesk')||'null');if(j){S.token=j.token;S.key=j.key;}}catch(e){}}
function clear(){S.token=S.key=S.acc=null;try{localStorage.removeItem('petdesk');}catch(e){}}
function call(action,body){
  body=body||{};if(action!=='login'){body.token=S.token;body.license_key=S.key;}
  var h={'content-type':'application/json'};if(!LOCAL){h.apikey=PUBKEY;h.authorization='Bearer '+PUBKEY;}
  return fetch(API+action,{method:'POST',headers:h,body:JSON.stringify(body)}).then(function(r){
    return r.json().catch(function(){return {};}).then(function(j){j._status=r.status;return j;});
  }).catch(function(){return {_status:0,error:'network'};});
}
function errMsg(e){return t('err_'+(e||'generic'));}

/* ---------- login ---------- */
function showLogin(msg){
  $('#pd-app').hidden=true;$('#pd-login').hidden=false;
  var m=$('#pd-login-msg');m.textContent=msg||'';m.hidden=!msg;
}
function doLogin(ev){
  if(ev)ev.preventDefault();
  var k=$('#pd-key').value.trim().toUpperCase();
  var b=$('#pd-open');b.disabled=true;b.textContent=t('opening');
  call('login',{license_key:k}).then(function(j){
    b.disabled=false;b.textContent=t('open');
    if(j._status===200&&j.token){S.token=j.token;S.key=k;S.acc=j.account;save();render();}
    else showLogin(errMsg(j.error==='gumroad_unavailable'?'gumroad':j.error==='network'?'gumroad':j.error));
  });
}

/* ---------- desk ---------- */
function statusLine(a){
  var price=a.recurrence==='yearly'?'$468':'$49';
  if(a.status==='trial')return '<span class="pd-badge trial">'+esc(t('b_trial'))+'</span> '+esc(t('st_trial',{price:price,date:fmtDate(a.trial_ends_approx)}));
  if(a.status==='cancelling')return '<span class="pd-badge warn">'+esc(t('b_cancel'))+'</span> '+esc(t('st_cancelling',{date:fmtDate(a.access_until)}));
  return '<span class="pd-badge ok">'+esc(t('b_active'))+'</span> '+esc(t(a.recurrence==='yearly'?'st_active_yr':'st_active_mo'));
}
function render(){
  var a=S.acc;$('#pd-login').hidden=true;$('#pd-app').hidden=false;
  $('#pd-status').innerHTML=statusLine(a);
  $('#pd-who').textContent=t('who',{email:a.email_masked||'—',last4:a.license_last4});
  $('#pd-agency').value=a.agency_name||'';
  var q=a.quota;$('#pd-quota').textContent=t('quota',{used:q.used,limit:q.limit});
  var bar=$('#pd-quota-bar');bar.style.width=Math.min(100,q.used/q.limit*100)+'%';
  var full=q.used>=q.limit;$('#pd-issue').disabled=full;$('#pd-quota-full').hidden=!full;
  var ul=$('#pd-recent');ul.innerHTML='';
  (a.passports||[]).forEach(function(p){
    var li=document.createElement('li');
    li.innerHTML='<code>'+esc(p.ref)+'</code> '+esc(p.route.from+' → '+p.route.to)+(p.client_ref?' · '+esc(p.client_ref):'')+' · '+esc(p.langs.join(' + ').toUpperCase())+' <a href="'+printUrl(p)+'" target="_blank" rel="noopener">'+esc(t('reopen'))+'</a>';
    ul.appendChild(li);
  });
  $('#pd-recent-empty').hidden=!!(a.passports||[]).length;
  renderWatch();
}
function printUrl(p){return 'print.html?ref='+encodeURIComponent(p.ref);}
function readRoute(){
  var r={};['from','to','state','airline','pet','date','ret'].forEach(function(k){var el=$('#pd-'+k);r[k]=el?el.value:'';});
  r.retdate=$('#pd-retdate').value;return r;
}
function doIssue(){
  var l1=$('#pd-l1').value,l2=$('#pd-l2').value,m=$('#pd-issue-msg');
  if(l1===l2){m.textContent=t('err_langs');m.hidden=false;return;}
  var route=readRoute();if(!route.from||!route.to){m.textContent=t('err_route');m.hidden=false;return;}
  var w=window.open('about:blank','_blank');
  call('issue',{route:route,langs:[l1,l2],client_ref:$('#pd-client').value}).then(function(j){
    if(j._status===200){m.hidden=true;
      var p={ref:j.ref,route:route,langs:[l1,l2],client_ref:$('#pd-client').value};
      if(w)w.location=printUrl(p);else location.href=printUrl(p);
      refresh();
    } else { if(w)w.close(); handleErr(j,m); }
  });
}
function handleErr(j,m){
  if(j._status===401){clear();showLogin(errMsg(j.error==='session_replaced'?'session_replaced':'session'));return;}
  if(j._status===403){clear();showLogin(errMsg(j.error));return;}
  m.textContent=errMsg(j.error==='quota_reached'?'quota':j.error);m.hidden=false;
}
function refresh(){call('me').then(function(j){if(j._status===200){S.acc=j.account;render();}else handleErr(j,$('#pd-issue-msg'));});}
function doProfile(){
  var m=$('#pd-profile-msg');
  call('profile',{agency_name:$('#pd-agency').value}).then(function(j){
    if(j._status===200){S.acc=j.account;m.textContent=t('saved');m.hidden=false;setTimeout(function(){m.hidden=true;},2500);}else handleErr(j,m);
  });
}

/* ---------- watchlist ---------- */
var UPD=null;
function airlines(){var sel=$('#pd-airline');return [].slice.call(sel.options).filter(function(o){return o.value;}).map(function(o){return [o.value,o.text];});}
function renderWatch(){
  var box=$('#pd-watch-list');box.innerHTML='';var w=S.acc.watch||[];
  airlines().forEach(function(a){
    var id='pdw-'+a[0];var lab=document.createElement('label');lab.className='pd-chk';
    lab.innerHTML='<input type="checkbox" id="'+id+'" value="'+esc(a[0])+'"'+(w.indexOf(a[0])>=0?' checked':'')+'> '+esc(a[1]);
    box.appendChild(lab);
  });
  box.onchange=function(e){var n=box.querySelectorAll('input:checked').length;if(n>5){e.target.checked=false;var m=$('#pd-watch-msg');m.textContent=t('watch_limit');m.hidden=false;}};
  loadUpdates().then(function(list){
    var hits=list.filter(function(u){return w.indexOf(u.slug)>=0;});
    var ul=$('#pd-watch-hits');ul.innerHTML='';
    hits.forEach(function(u){var li=document.createElement('li');li.innerHTML='<time>'+esc(u.date)+'</time> <b>'+esc(u.name)+'</b>: '+esc(u.text)+(u.src?' <a href="'+esc(u.src)+'" rel="noopener" target="_blank">'+esc(t('source'))+'</a>':'');ul.appendChild(li);});
    $('#pd-watch-none').hidden=!!hits.length||!w.length;$('#pd-watch-pick').hidden=!!w.length;
  });
}
function loadUpdates(){
  if(UPD)return Promise.resolve(UPD);
  return fetch(BASE+LANG_PATH[L]+'updates.html').then(function(r){return r.text();}).then(function(h){
    var d=new DOMParser().parseFromString(h,'text/html');
    UPD=[].slice.call(d.querySelectorAll('ul.changes > li')).map(function(li){
      var a=li.querySelector('a[href*="airlines/"]');var src=[].slice.call(li.querySelectorAll('a')).filter(function(x){return /^https?:/.test(x.getAttribute('href'));})[0];
      var m=a&&a.getAttribute('href').match(/airlines\/([a-z0-9-]+)\.html/);
      var txt=li.textContent.replace(/\s+/g,' ');var time=li.querySelector('time');
      var body=txt.replace(time?time.textContent:'','').replace(a?a.textContent:'','').replace(/^\s*:\s*/,'').replace(/\s*source\s*(unofficial source)?\s*$/i,'').trim();
      return {slug:m?m[1]:'',name:a?a.textContent:'',date:time?time.textContent:'',text:body,src:src?src.getAttribute('href'):''};
    });return UPD;
  }).catch(function(){UPD=[];return UPD;});
}
function doWatch(){
  var slugs=[].slice.call(document.querySelectorAll('#pd-watch-list input:checked')).map(function(i){return i.value;});
  var m=$('#pd-watch-msg');
  call('watch',{slugs:slugs}).then(function(j){if(j._status===200){S.acc.watch=j.watch;m.textContent=t('saved');m.hidden=false;renderWatch();}else handleErr(j,m);});
}

/* ---------- route selects: same options as the public Passport tool ---------- */
/* The hidden passport iframes run the site's language script, which saves their language as the
   visitor's site language (ppc_lang). Put the visitor's own choice back once they have loaded. */
var PPC_LANG_KEPT=(function(){try{return localStorage.getItem('ppc_lang');}catch(e){return null;}})();
function restoreLang(){try{if(PPC_LANG_KEPT===null)localStorage.removeItem('ppc_lang');else localStorage.setItem('ppc_lang',PPC_LANG_KEPT);}catch(e){}}
window.addEventListener('pagehide',restoreLang);
function fillSelects(){
  var fr=document.createElement('iframe');fr.hidden=true;fr.setAttribute('aria-hidden','true');fr.tabIndex=-1;
  fr.src=BASE+LANG_PATH[L]+'passport/?pdesk=1';
  fr.onload=function(){
    restoreLang();var tries=0;(function wait(){
      try{var d=fr.contentDocument;var f=d.getElementById('from');
        if(f&&f.options.length>1){['from','to','state','airline'].forEach(function(k){$('#pd-'+k).innerHTML=d.getElementById(k).innerHTML;});
          $('#pd-to').value='FR';fr.remove();restoreLang();if(S.acc)renderWatch();return;}
      }catch(e){}
      if(++tries<60)setTimeout(wait,100);
    })();
  };
  document.body.appendChild(fr);
}

function init(){
  $('#pd-form').addEventListener('submit',doLogin);
  $('#pd-issue').addEventListener('click',doIssue);
  $('#pd-save-agency').addEventListener('click',doProfile);
  $('#pd-save-watch').addEventListener('click',doWatch);
  $('#pd-logout').addEventListener('click',function(){call('logout').then(function(){clear();showLogin(t('bye'));});});
  fillSelects();
  load();
  if(S.token){call('me').then(function(j){if(j._status===200){S.acc=j.account;render();}else{clear();showLogin(j._status===401&&j.error==='session_replaced'?errMsg('session_replaced'):'');}});}
  else showLogin('');
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
