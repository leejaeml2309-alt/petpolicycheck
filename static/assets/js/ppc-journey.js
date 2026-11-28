/* ppc-journey (2026-11-28): GA4 event for the discreet Pet Desk link and the Next step cards.
   pro_link_click {cta_position, link_url, lang}; next_step_click {cta_position, link_url, lang}.
   cta_position reuses the event-scoped custom dimension already declared for gumroad_click. */
(function(){
  function lang(){return ((document.documentElement.getAttribute('lang')||'en').slice(0,2).toLowerCase())||'en';}
  function on(ev){
    var a=ev.target&&ev.target.closest?ev.target.closest('a[data-ppc-ev]'):null;
    if(!a||(ev.type==='auxclick'&&ev.button!==1))return;
    try{
      if(typeof window.gtag==='function')window.gtag('event',a.getAttribute('data-ppc-ev'),{
        cta_position:String(a.getAttribute('data-cta')||'other'),link_url:a.href||'',lang:lang(),transport_type:'beacon'});
    }catch(e){}
  }
  document.addEventListener('click',on,true);
  document.addEventListener('auxclick',on,true);
})();
