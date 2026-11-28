/* /pro/ Starter CTA (2026-11-25): gumroad_click GA4 event + mobile sticky bar. */
(function(){
  function lang(){var l=(document.documentElement.getAttribute('lang')||'en').slice(0,2).toLowerCase();return l||'en';}
  /* 2026-11-28: params are built from explicit data attributes first (data-tier, data-cta), then the URL and the
     billing toggle, so every event carries tier / billing / lang / cta_position as plain strings.
     Add ?ga_debug=1 to the page URL to send debug_mode and watch the event in GA4 DebugView. */
  var DBG=/[?&]ga_debug=1\b/.test(location.search);
  function billing(a,u){
    var b=a.getAttribute('data-billing');if(b)return b;
    if(/[?&]yearly=true/.test(u))return 'yearly';
    return document.documentElement.getAttribute('data-bill')==='yr'?'yearly':'monthly';
  }
  function track(ev){
    var a=ev.target&&ev.target.closest?ev.target.closest('a[href*="gumroad.com/l/petdesk-"]'):null;
    if(!a||(ev.type==='auxclick'&&ev.button!==1))return;
    var u=a.href||'';
    var p={
      tier:String(a.getAttribute('data-tier')||'starter'),
      billing:String(billing(a,u)),
      lang:String(lang()),
      cta_position:String(a.getAttribute('data-cta')||'plan'),
      link_url:u,
      transport_type:'beacon'
    };
    if(DBG)p.debug_mode=true;
    try{
      if(typeof window.gtag==='function')window.gtag('event','gumroad_click',p);
      window.__ppcLastGumroad=p;
    }catch(e){}
  }
  document.addEventListener('click',track,true);
  document.addEventListener('auxclick',track,true);

  /* Text and URL sync for the hero / sticky CTA (follows the page language and the billing toggle). */
  var TX={
    en:{mo:"$49/mo after your free month",yr:"$468/year after your free month",desk:"Already a member? Open your Pet Desk"},
    fr:{mo:"49 $/mois après le mois gratuit",yr:"468 $/an après le mois gratuit",desk:"Déjà abonné\u00a0? Ouvrez votre Pet Desk"},
    es:{mo:"49 $/mes después del mes gratis",yr:"468 $/año después del mes gratis",desk:"¿Ya es miembro? Abra su Pet Desk"},
    de:{mo:"$49/Monat nach dem Gratismonat",yr:"$468/Jahr nach dem Gratismonat",desk:"Schon Mitglied? Öffnen Sie Ihren Pet Desk"},
    it:{mo:"49 $/mese dopo il mese gratuito",yr:"468 $/anno dopo il mese gratuito",desk:"Già abbonato? Apra il Suo Pet Desk"},
    ja:{mo:"無料期間終了後は月額$49",yr:"無料期間終了後は年額$468",desk:"ご契約済みの方：Pet Deskを開く"}
  };
  function sync(){
    var d=TX[lang()];
    if(d)document.querySelectorAll('[data-pc]').forEach(function(el){var v=d[el.getAttribute('data-pc')];if(v!=null&&el.textContent!==v)el.textContent=v;});
    var main=document.querySelector('[data-pd="starter-trial"] a[data-href-mo]');
    var b=document.querySelector('.bill-sw button[aria-pressed="true"]');
    var yr=b&&b.getAttribute('data-bill')==='yr';
    if(document.documentElement.getAttribute('data-bill')!==(yr?'yr':'mo'))document.documentElement.setAttribute('data-bill',yr?'yr':'mo');
    if(main)document.querySelectorAll('a[data-cta][data-href-mo]').forEach(function(a){
      var u=yr?a.getAttribute('data-href-yr'):a.getAttribute('data-href-mo');
      if(u&&a.getAttribute('href')!==u)a.setAttribute('href',u);
      if(main.innerHTML&&a.innerHTML!==main.innerHTML)a.innerHTML=main.innerHTML;
    });
  }
  function initSync(){
    sync();
    if('MutationObserver' in window){
      new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
      var sw=document.querySelector('.bill-sw');if(sw)new MutationObserver(sync).observe(sw,{attributes:true,subtree:true,attributeFilter:['aria-pressed']});
    }
    window.addEventListener('ppc:lang',function(){setTimeout(sync,0);});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initSync);else initSync();

  function sticky(){
    var bar=document.getElementById('pd-sticky');if(!bar||!('IntersectionObserver' in window))return;
    var watch=[document.querySelector('.pd-hero-cta'),document.querySelector('[data-pd="starter-trial"]'),document.querySelector('footer')].filter(Boolean);
    var seen=new Map();
    var mq=window.matchMedia('(max-width:767px)');
    function upd(){
      var any=false;seen.forEach(function(v){if(v)any=true;});
      var heroGone=true;var h=document.querySelector('.pd-hero-cta');
      if(h){var r=h.getBoundingClientRect();heroGone=r.bottom<0;}
      var on=mq.matches&&!any&&heroGone;
      bar.classList.toggle('on',on);bar.setAttribute('aria-hidden',on?'false':'true');
      bar.querySelectorAll('a').forEach(function(x){x.tabIndex=on?0:-1;});
      document.body.classList.toggle('pd-sticky-pad',mq.matches);
    }
    var io=new IntersectionObserver(function(es){es.forEach(function(e){seen.set(e.target,e.isIntersecting);});upd();},{threshold:0});
    watch.forEach(function(el){seen.set(el,false);io.observe(el);});
    window.addEventListener('scroll',upd,{passive:true});
    if(mq.addEventListener)mq.addEventListener('change',upd);
    upd();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',sticky);else sticky();
})();
