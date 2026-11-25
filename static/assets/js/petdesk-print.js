/* Pet Desk Starter: dual-language print sheet. Only opens for a passport issued by the signed-in
   desk (checked server-side: action "passport"). Renders the public Passport engine in two languages
   (same-origin iframes) and stacks both printable passports under one agency header. */
(function(){
'use strict';
var LOCAL=/^(127\.0\.0\.1|localhost)$/.test(location.hostname);
var API=LOCAL?'/fn/petdesk/':'https://uouccgyeujtmbeeneuwq.supabase.co/functions/v1/petdesk/';
var PUBKEY='sb_publishable_J3NaUoRdx7d5FBDfsFqGFQ__GY9uwYo';
var BASE=document.documentElement.getAttribute('data-site-root')||'../../';
var LP={en:'',es:'es/',it:'it/'};
var NAMES={en:'English',es:'Español',it:'Italiano'};
function esc(s){return String(s==null?'':s).replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c];});}
var ref=new URLSearchParams(location.search).get('ref')||'';
var sess={};try{sess=JSON.parse(localStorage.getItem('petdesk')||'{}')||{};}catch(e){}
var h={'content-type':'application/json'};if(!LOCAL){h.apikey=PUBKEY;h.authorization='Bearer '+PUBKEY;}
var head=document.getElementById('pd-head');
function fail(){head.innerHTML='<div><b>Pet Desk</b></div><div>'+esc(document.documentElement.getAttribute('data-msg-denied'))+' <a href="./">Pet Desk</a></div>';document.getElementById('pd-print').hidden=true;}
if(!sess.token){fail();return;}
fetch(API+'passport',{method:'POST',headers:h,body:JSON.stringify({token:sess.token,license_key:sess.key,ref:ref})})
.then(function(r){return r.ok?r.json():Promise.reject(r.status);}).then(function(j){
  var P=j.passport,langs=P.langs.filter(function(l){return LP.hasOwnProperty(l);});
  head.innerHTML='<div><b>'+esc(j.agency_name||'Pet Desk')+'</b>'+(P.client_ref?' · '+esc(P.client_ref):'')+'</div>'+
    '<div>Ref <code>'+esc(P.ref)+'</code> · '+esc(P.created_at.slice(0,10))+' · '+langs.map(function(l){return NAMES[l];}).join(' + ')+'</div>';
  var params=new URLSearchParams();['from','to','state','airline','pet','date','ret','retdate'].forEach(function(k){if(P.route[k])params.set(k,P.route[k]);});
  fetch(BASE+'assets/css/passport.css').then(function(r){return r.text();}).then(function(css){
    css=css.replace(/@media print\{[\s\S]*?\n\}/,'').replace(/#ppc-passport #pass\{display:none\}/g,'').replace(/#pass\{display:none\}/g,'').replace(/#pass/g,'.pd-pass');
    var st=document.createElement('style');st.textContent=css;document.head.appendChild(st);
  });
  var host=document.getElementById('pd-copies'),done=0;
  langs.forEach(function(l,i){
    var sec=document.createElement('section');sec.className='pd-copy';sec.setAttribute('lang',l);
    sec.innerHTML='<p class="pd-lang no-print">'+esc(NAMES[l])+'</p><div class="pd-pass" id="pd-pass-'+i+'"><p class="pd-wait">…</p></div>';
    host.appendChild(sec);
    var fr=document.createElement('iframe');fr.className='pd-src';fr.setAttribute('aria-hidden','true');fr.tabIndex=-1;
    fr.src=BASE+LP[l]+'passport/?'+params.toString();
    fr.onload=function(){var n=0;(function wait(){
      try{var p=fr.contentDocument.getElementById('pass');
        if(p&&p.innerHTML.length>500){
          [].slice.call(p.querySelectorAll('canvas')).forEach(function(c){try{var im=fr.contentDocument.createElement('img');im.src=c.toDataURL();im.width=c.width;im.height=c.height;c.replaceWith(im);}catch(e){}});
          document.getElementById('pd-pass-'+i).innerHTML=p.innerHTML;fr.remove();
          if(++done===langs.length){document.body.classList.add('pd-ready');document.getElementById('pd-print').disabled=false;}
          return;}
      }catch(e){}
      if(++n<80)setTimeout(wait,100);})();};
    document.body.appendChild(fr);
  });
}).catch(fail);
document.getElementById('pd-print').addEventListener('click',function(){window.print();});
})();
