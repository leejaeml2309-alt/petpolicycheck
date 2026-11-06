/* PetPolicyCheck · partner banner runtime fallback (build.py prefers build-time render). */
(function(){
  var slots=document.querySelectorAll('.partner-slot[data-partner-live="0"]');
  if(!slots.length) return;
  var root=document.querySelector('script[data-partner-root]');
  var base=(root&&root.getAttribute('data-partner-root'))||'assets/partners/';
  fetch(base+'top-partner.json',{credentials:'same-origin'}).then(function(r){return r.ok?r.json():null}).then(function(cfg){
    if(!cfg||!cfg.active) return;
    slots.forEach(function(slot){
      var card=slot.querySelector('.partner-card'); if(!card) return;
      if(cfg.html){ card.innerHTML='<span class="partner-label">Partner</span><div class="partner-html">'+cfg.html+'</div>'; return; }
      if(cfg.image&&cfg.link){
        var img=cfg.image_mobile&&window.matchMedia('(max-width:720px)').matches? (cfg.image_mobile||cfg.image):cfg.image;
        card.innerHTML='<span class="partner-label">Partner</span><a class="partner-creative" href="'+cfg.link+'" target="_blank" rel="sponsored noopener"><img src="'+base+img+'" alt="'+(cfg.alt||cfg.partner||'Partner')+'" width="970" height="90" loading="lazy" decoding="async"></a>';
      }
    });
  }).catch(function(){});
})();
