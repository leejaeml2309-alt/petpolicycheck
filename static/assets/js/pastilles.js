/* PetPolicyCheck · Section pastilles (Version A) · Production.
   1 sprite SVG monoline (viewBox 24, stroke 1.75) + nav 7 sections + badge d'en-tête.
   Injects Version A pastille nav + section eyebrow. */
(function(){
var G={
 map:'<circle cx="12" cy="12" r="8.6"/><path d="M3.4 12h17.2M12 3.4c2.4 2.5 3.6 5.4 3.6 8.6s-1.2 6.1-3.6 8.6M12 3.4C9.6 5.9 8.4 8.8 8.4 12s1.2 6.1 3.6 8.6"/>',
 flight:'<path d="M12 2.9c.85 0 1.45.85 1.45 2.1v4.5l6.8 4v1.9l-6.8-2v4.1l2.1 1.6v1.6L12 19.8l-3.55.9v-1.6l2.1-1.6v-4.1l-6.8 2v-1.9l6.8-4V5c0-1.25.6-2.1 1.45-2.1Z"/>',
 hotel:'<path d="M3.5 6.5v12M20.5 18.5V14a3 3 0 0 0-3-3H11v3.5M3.5 14.5h17M3.5 17.5h17"/><circle cx="7.1" cy="11.6" r="1.7"/>',
 ground:'<path d="M5.2 17.2h13.6a1 1 0 0 0 1-1v-3l-2.1-4.9a1.6 1.6 0 0 0-1.5-1H7.8a1.6 1.6 0 0 0-1.5 1l-2.1 4.9v3a1 1 0 0 0 1 1ZM4.4 12.8h15.2M7 17.2v2.1M17 17.2v2.1"/><path d="M7.4 15h1.2M15.4 15h1.2"/>',
 shop:'<path d="M5.6 8.2h12.8l-.9 11.1a1 1 0 0 1-1 .9H7.5a1 1 0 0 1-1-.9L5.6 8.2Z"/><path d="M9 10.6V7a3 3 0 0 1 6 0v3.6"/>',
 law:'<path d="M12 4.2v15M8.2 19.4h7.6M5.4 7.4h13.2M12 4.2l-.01.01"/><path d="M5.4 7.6 3 13a2.4 2.4 0 0 0 4.8 0L5.4 7.6ZM18.6 7.6 16.2 13a2.4 2.4 0 0 0 4.8 0l-2.4-5.4Z"/>',
 grooming:'<circle cx="6.6" cy="17.4" r="2.6"/><circle cx="17.4" cy="17.4" r="2.6"/><path d="M8.5 15.6 16.4 4.2M15.5 15.6 7.6 4.2M12 11.3v.01"/><path d="M19.6 4.4v2.4M18.4 5.6h2.4"/>',
 forum:'<path d="M5 4.8h14a1.5 1.5 0 0 1 1.5 1.5v8.2A1.5 1.5 0 0 1 19 16h-7.6l-4.6 3.6V16H5a1.5 1.5 0 0 1-1.5-1.5V6.3A1.5 1.5 0 0 1 5 4.8Z"/><path d="M7.8 9.2h8.4M7.8 12h5.4"/>',
 b2b:'<rect x="3.5" y="7" width="17" height="12" rx="1.5"/><path d="M8 7V5.8A2.2 2.2 0 0 1 10.2 3.6h3.6A2.2 2.2 0 0 1 16 5.8V7M3.5 12h17"/>',
 veterans:'<path d="M12 3.2 19 6v5.4c0 4.6-3 7.9-7 9.4-4-1.5-7-4.8-7-9.4V6l7-2.8Z"/><path d="m12 8 1.15 2.35 2.6.38-1.88 1.83.44 2.59L12 13.93l-2.31 1.22.44-2.59-1.88-1.83 2.6-.38L12 8Z"/>'
};
window.PPC_GLYPHS=G;
var sp='<svg xmlns="http://www.w3.org/2000/svg" style="position:absolute;width:0;height:0;overflow:hidden" aria-hidden="true">';
for(var k in G) sp+='<symbol id="pst-'+k+'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'+G[k]+'</symbol>';
sp+='</svg>';
function pst(k,cls){return '<span class="pst theme-'+k+(cls?' '+cls:'')+'" aria-hidden="true"><svg viewBox="0 0 24 24"><use href="#pst-'+k+'"/></svg></span>'}
window.PPC_PST=pst;
function boot(){
 document.body.insertAdjacentHTML('afterbegin',sp);
 var path=location.pathname || '/';
 /* Exact relative root: /countries/usa-map.html → '../'; /airlines/compare/ → '../../' */
 var segs=path.replace(/\/+$/,'').split('/').filter(Boolean);
 /* Drop the file segment when path ends with a filename (*.html) */
 if(segs.length && /\.[a-z0-9]+$/i.test(segs[segs.length-1])) segs=segs.slice(0,-1);
 var up=segs.length ? '../'.repeat(segs.length) : '';
 /* Country sub-maps (usa/canada/mexico-map) must NOT mark World map as current. */
 var onCountryMap=/\/countries\/(?:usa|canada|mexico)-map\.html$/.test(path);
 var cur=document.documentElement.dataset.section||(
  /\/airlines\//.test(path)?'flight':/\/hotels\//.test(path)?'hotel':/\/book\//.test(path)?'ground':
  /\/products\//.test(path)?'shop':/\/countries\/usa\.html/.test(path)?'law':/\/forum\//.test(path)?'forum':/\/grooming\//.test(path)?'grooming':
  /\/veterans\//.test(path)?'veterans':
  /\/(?:pro|extension|b2b-pet-desk)\/?$|\/(?:terms|refund-policy|privacy)\.html/.test(path)?'b2b':
  onCountryMap?'':(/usa-map|\/map/.test(path)?'map':''));
 /* Homepage unlocked world-map view (?view=map) marks World map current */
 try{ if((path==='/'||/\/(index\.html)?$/.test(path)) && new URLSearchParams(location.search).get('view')==='map') cur='map'; }catch(e){}
 var V=(new URLSearchParams(location.search).get('nav'))||document.documentElement.dataset.nav||'8';
 /* '8' = 8 liens (Rides garde sa place) ; '7g' (reco) = Rides fusionne dans Book (hub de réservation), Grooming prend sa place */
 /* World map uses ?view=map (NO #hash) so browsers never native-scroll to an id */
 var S=[['map','World map',up+'?view=map'],['flight','Airlines',up+'airlines/united.html'],['hotel','Hotels',up+'hotels/'],
        ['grooming','Grooming',up+'grooming/'],['ground','Rides',up+'book/#rides'],['shop','Products',up+'products/'],['law','Rules',up+'countries/usa.html#federal'],['forum','Forum',up+'forum/'],['veterans','Veterans',up+'veterans/'],['b2b','For Business',up+'pro/']];
 if(V==='7g') S=S.filter(function(x){return x[0]!=='ground'});
 document.documentElement.classList.add('nav-v'+V);
 var bookCur=false; if(V==='7g'&&cur==='ground'){cur='';bookCur=true}
 if(cur) document.documentElement.classList.add('theme-'+cur);
 if(onCountryMap) document.documentElement.classList.add('theme-map');
 var m=document.getElementById('site-menu')||document.querySelector('.map-nav nav.nav, header.map-nav nav'); if(!m) return;
 var NAV_I18N={map:'site.nav.map',flight:'site.nav.airlines',hotel:'site.nav.hotels',grooming:'site.nav.grooming',ground:'site.nav.rides',shop:'site.nav.products',law:'site.nav.rules',forum:'site.nav.forum',veterans:'site.nav.veterans',b2b:'site.nav.pro'};
 var h=S.map(function(s){var extra=s[0]==='b2b'?' nav-biz':(s[0]==='veterans'?' nav-vet':'');var ik=NAV_I18N[s[0]]||'';return '<a class="sec theme-'+s[0]+extra+'" href="'+s[2]+'"'+(s[0]===cur?' aria-current="page"':'')+(ik?' data-i18n="'+ik+'"':'')+'>'+pst(s[0])+'<span class="lbl">'+s[1]+'</span></a>'}).join('');
 h+='<span class="menu-sep menu-only" aria-hidden="true"></span>'+
    ['Compare|'+up+'#compare','Guides|'+up+'#gear','Updates|'+up+'updates.html','About|'+up+'about.html'].map(function(x){x=x.split('|');return '<a class="menu-only sub" href="'+x[1]+'">'+x[0]+'</a>'}).join('')+
    (V==='7g'?'<a class="nav-book" data-i18n="site.nav.book"'+(bookCur?' aria-current="page"':'')+' href="'+up+'book/" title="Flights, hotels, rides, vets, insurance">Book<span class="bk-sub"> · rides</span></a>':'<a class="nav-book" data-i18n="site.nav.book" href="'+up+'book/">Book</a>')+'<a class="cta" data-i18n="site.nav.advertise" href="'+up+'advertise/">Advertise</a>';
 m.innerHTML=h; m.classList.add('pst-nav');
 /* badge d'en-tête de section, même tampon que la nav (taille page) */
 var h1=document.querySelector('main h1, #main h1, h1');
 /* Country maps: clickable back-link to the homepage World map (never a dead div). */
 if(onCountryMap&&h1&&!document.querySelector('.sec-eyebrow')){
  h1.insertAdjacentHTML('beforebegin','<a class="sec-eyebrow theme-map" href="'+up+'?view=map" style="text-decoration:none;cursor:pointer;pointer-events:auto;touch-action:manipulation">'+pst('map','pst-lg')+'<span data-i18n="site.nav.world_back">\u2190 World map</span></a>');
 }else if(cur&&h1&&!document.querySelector('.sec-eyebrow')){
  var L={map:'World map',flight:'Airlines',hotel:'Hotels',ground:'Rides',shop:'Products',law:'Rules & health certificate',forum:'Forum',grooming:'Care & Grooming (Travel + Expat)',veterans:'Veterans',b2b:'B2B Pet Desk'};
  h1.insertAdjacentHTML('beforebegin','<div class="sec-eyebrow theme-'+cur+'">'+pst(cur,'pst-lg')+'<span>'+L[cur]+'</span></div>');
 }

 /* Logo-only brand: ensure .lbadge, strip wordmark text from aria, hide .wm via CSS */
 var brand=document.querySelector('header.top a.brand, header.map-nav a.brand');
 if(brand){
  brand.setAttribute('aria-label','PetPolicyCheck — Home');
  if(!brand.querySelector('.lbadge')){
   brand.insertAdjacentHTML('afterbegin','<span class="lbadge"><img src="'+up+'assets/img/logo-mark-header.png" width="62" height="48" alt="PetPolicyCheck"></span>');
  } else {
   var img=brand.querySelector('.lbadge img');
   if(img){ img.setAttribute('alt','PetPolicyCheck'); img.removeAttribute('aria-hidden'); }
  }
 }
}

 /* Mobile menu toggle (growth pages may lack MENU_JS) */
 if(!window.__ppcMenuBound){
  window.__ppcMenuBound=1;
  document.addEventListener('click',function(e){
   var b=e.target&&e.target.closest&&e.target.closest('.menu-btn,[data-menu-trigger]');
   var menu=document.getElementById('site-menu');
   if(!menu) return;
   if(b){ e.preventDefault(); e.stopPropagation(); var o=!menu.classList.contains('open'); menu.classList.toggle('open',o); document.querySelectorAll('.menu-btn,[data-menu-trigger]').forEach(function(x){x.setAttribute('aria-expanded',o?'true':'false')}); return; }
   if(menu.classList.contains('open')&&!menu.contains(e.target)){ menu.classList.remove('open'); document.querySelectorAll('.menu-btn,[data-menu-trigger]').forEach(function(x){x.setAttribute('aria-expanded','false')}); }
  });
  document.addEventListener('keydown',function(e){ if(e.key==='Escape'){ var menu=document.getElementById('site-menu'); if(menu){ menu.classList.remove('open'); document.querySelectorAll('.menu-btn').forEach(function(x){x.setAttribute('aria-expanded','false')}); }}});
 }
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
window.addEventListener('ppc:lang',function(){ if(window.PPC_LANG&&window.PPC_LANG.t){ document.querySelectorAll('#site-menu [data-i18n], .sec-eyebrow [data-i18n]').forEach(function(el){var v=window.PPC_LANG.t(el.getAttribute('data-i18n')); if(v){ var lbl=el.querySelector('.lbl'); if(lbl) lbl.textContent=v; else if(el.tagName==='SPAN'||!el.querySelector('svg')) el.textContent=v; }}); }});
})();
