/* IT UI strings when on /it/ (EN source text otherwise). */
var PPC_GROOM_I18N=(function(){
 function lang(){try{
  if((document.documentElement.getAttribute('data-ppc-locale')||'')==='it') return 'it';
  if((location.pathname||'').indexOf('/it/')===0) return 'it';
 }catch(e){} return 'en';}
 var IT={"filter.aria":"Filtri i toelettatori","filter.all":"Tutti","filter.travel":"✈️ Viaggio / senza appuntamento e mobile","filter.resident":"🏠 Residenti ed expat","filter.cats":"🐱 Gatti OK","uses.road.title":"✈️ In viaggio","uses.road.p":"Un lavaggio occasionale dopo il volo, vicino al Suo hotel o un furgone che si ferma all’hotel.","uses.settle.title":"🏠 Quando si installa","uses.settle.p":"Un toelettatore di quartiere abituale per residenti e nuovi expat: lingue, gatti senza sedazione, cani grandi.","partner.cta":"Diventi toelettatore verificato / partner","partner.note":"I toelettatori possono candidarsi per essere inseriti; ogni scheda è verificata sul sito ufficiale del toelettatore.","legend.confirmed":"confermato","legend.confirmed_on":"sul sito ufficiale del toelettatore","legend.ask":"chieda al salone","legend.ask_note":"non pubblicato: chiami prima di prenotare (i documenti di vaccino e di importazione variano).","empty":"Nessun toelettatore verificato è ancora elencato qui. I toelettatori verificati sono disponibili per le 8 città degli hotel:","badge.intl_ok":"🌍 Passaporto antirabbico internazionale OK","badge.intl_ask":"🌍 Passaporto antirabbico internazionale · chieda al salone","badge.intl_ask_title":"Non pubblicato dal salone (accettazione del passaporto antirabbico internazionale non confermata)","badge.openview_yes":"👁️ Tavolo a vista · niente gabbie nascoste","badge.openview_na":"👁️ A vista · non applicabile, furgone alla Sua porta","badge.openview_ask":"👁️ Tavolo a vista · chieda al salone","badge.hotel_mobile":"🚐 Mobile in hotel","badge.sedation_free":"🐱 Gatti senza sedazione","badge.cats_ok":"🐱 Gatti OK","badge.large_dogs":"🐕 Cani da 25 kg in su","langs_title":"Lingue indicate","official_site":"Sito ufficiale ↗","section.h3":"Toelettatura"};
 return {lang:lang,it:IT,t:function(k,en){return lang()==='it'&&IT[k]!=null?IT[k]:en;}};
})();
function T(k,en){return PPC_GROOM_I18N.t(k,en);}
/* PetPolicyCheck · Grooming (8e département) · composant partagé carte USA + pages Hôtels. Production.
   Données : window.PPC_GROOMERS (grooming-data.js, généré depuis vague-a-grooming.json).
   Badges en 3 états : yes (confirmé sur le site officiel) · ask (non publié : à confirmer par téléphone) · na. */
(function(){
var D=window.PPC_GROOMERS||{};
function e(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function types(g){return (g.type||[]).join(', ')}
function isTravel(g){return g.traveler_friendly===true&&(g.mobile_hotel===true||(g.type||[]).indexOf('salon')>=0)}
function badge(cls,txt,title){return '<span class="gb gb-'+cls+'"'+(title?' title="'+e(title)+'"':'')+'>'+txt+'</span>'}
function card(g,metro){
 var va=g.vaccines_accepted||{},b='';
 b+= va.accepts_international_rabies_cert===true ? badge('yes',T('badge.intl_ok','🌍 Intl Rabies Passport OK')) : badge('ask',T('badge.intl_ask','🌍 Intl rabies passport · ask salon'),T('badge.intl_ask_title','Not published by the salon (intl_rabies_passport_accepted unconfirmed)'));
 b+= g.open_view_table===true ? badge('yes',T('badge.openview_yes','👁️ Open-View Table · no hidden cages')) : g.open_view_table==='n/a_mobile_van' ? badge('na',T('badge.openview_na','👁️ Open-view · n/a, van at your door')) : badge('ask',T('badge.openview_ask','👁️ Open-view table · ask salon'));
 if(g.mobile_hotel===true) b+=badge('yes',T('badge.hotel_mobile','🚐 Hotel Mobile'));
 if(g.sedation_free===true&&g.cats_accepted===true) b+=badge('yes',T('badge.sedation_free','🐱 Sedation-Free Cats'));
 else if(g.cats_accepted===true) b+=badge('yes',T('badge.cats_ok','🐱 Cats OK'));
 if(g.large_dogs_25kg_plus===true) b+=badge('soft',T('badge.large_dogs','🐕 Dogs 25 kg+'));
 var langs=(g.languages||[]).join(' · ');
 return '<article class="gcard" data-travel="'+(isTravel(g)?1:0)+'" data-resident="'+(g.resident_regular===true?1:0)+'" data-cats="'+(g.cats_accepted===true?1:0)+'">'+
  '<div class="gc-h"><a href="'+e(g.url)+'" target="_blank" rel="noopener">'+e(g.name)+'</a>'+(langs?'<span class="gl" title="'+T('langs_title','Languages listed')+'">🗣 '+e(langs)+'</span>':'')+'</div>'+
  '<p class="gc-m">'+e(g.district||metro)+' · '+e(types(g))+'</p>'+
  '<div class="gbs">'+b+'</div>'+
  '<p class="gc-f"><a href="'+e(g.url)+'" target="_blank" rel="noopener">'+T('official_site','Official site ↗')+'</a>'+(g.phone?' · <span>'+e(g.phone)+'</span>':'')+'</p></article>';
}
function filters(){return '<div class="gfilter" role="group" aria-label="'+T('filter.aria','Filter groomers')+'">'+
 '<button type="button" data-gf="all" aria-pressed="true">'+T('filter.all','All')+'</button>'+
 '<button type="button" data-gf="travel" aria-pressed="false">'+T('filter.travel','✈️ Travel / Walk-in &amp; Mobile')+'</button>'+
 '<button type="button" data-gf="resident" aria-pressed="false">'+T('filter.resident','🏠 Resident &amp; Expat')+'</button>'+
 '<button type="button" data-gf="cats" aria-pressed="false" class="gf-tog">'+T('filter.cats','🐱 Cats OK')+'</button></div>'}
function uses(){return '<div class="guses"><div><b>'+T('uses.road.title','✈️ On the road')+'</b><span>'+T('uses.road.p','One-off wash after the flight, near your hotel or a van that parks at the hotel.')+'</span></div><div><b>'+T('uses.settle.title','🏠 Settling in')+'</b><span>'+T('uses.settle.p','A regular neighbourhood groomer for residents and new expats: languages, cats without sedation, big dogs.')+'</span></div></div>'}
function partner(up){var href=(PPC_GROOM_I18N.lang()==='it'?'/it/contact.html':'/contact.html')+'?topic=groomer';return '<p class="gpartner"><a class="btn ghost" href="'+href+'">'+T('partner.cta','Become a Verified Groomer / Partner')+'</a><span>'+T('partner.note','Groomers can apply to be listed; each listing is checked on the groomer’s official site.')+'</span></p>'}
var legend='<p class="glegend"><span class="gb gb-yes">'+T('legend.confirmed','confirmed')+'</span> '+T('legend.confirmed_on','on the groomer’s official site')+' · <span class="gb gb-ask">'+T('legend.ask','ask salon')+'</span> '+T('legend.ask_note','not published, call before you book (vaccine and import papers vary).')+'</p>';
function list(keys){var h='';keys.forEach(function(k){var c=k.split('|')[1];h+='<div class="gmetro" data-m="'+e(k)+'"><h4>'+e(c)+'</h4><div class="ggrid">'+D[k].map(function(g){return card(g,c)}).join('')+'</div></div>'});return h}
window.PPC_GROOM={
 section:function(cur){
  if(!cur) return '';
  var a=cur.a,n=cur.n,keys=[];
  if(n&&D[a+'|'+n]) keys=[a+'|'+n]; else keys=Object.keys(D).filter(function(k){return k.indexOf(a+'|')===0});
  var h='<section class="sec theme-grooming" data-sec="5" data-dept="grooming"><h3><span class="n">5</span>'+T('section.h3','Grooming')+'</h3>';
  if(!keys.length){
   var all=Object.keys(D).map(function(k){var p=k.split('|');return '<button type="button" data-s="'+p[0]+'" data-city="'+e(p[1])+'">'+e(p[1])+'</button>'}).join('');
   return h+'<p>'+T('empty','No verified groomer listed here yet. Verified groomers are live for the 8 hotel cities:')+'</p><div class="citylist">'+all+'</div>'+partner()+'</section>';
  }
  return h+uses()+filters()+list(keys)+legend+partner()+'</section>';
 },
 block:function(keys,up,first){
  var tabs='<div class="gmtabs" role="tablist">'+keys.map(function(k){return '<button type="button" role="tab" data-gm="'+e(k)+'" aria-selected="'+(k===first)+'">'+e(k.split('|')[1])+'</button>'}).join('')+'</div>';
  return '<div class="gblock theme-grooming" data-first="'+e(first)+'">'+uses()+tabs+filters()+list(keys)+legend+partner(up)+'</div>'},
 initBlocks:function(){document.querySelectorAll('.gblock').forEach(function(b){var f=b.dataset.first;b.querySelectorAll('.gmetro').forEach(function(m){m.hidden=m.dataset.m!==f})})},
 count:function(){var n=0;for(var k in D)n+=D[k].length;return n}
};
document.addEventListener('click',function(ev){
 var t=ev.target.closest&&ev.target.closest('[data-gm]');
 if(t){var b=t.closest('.gblock');b.querySelectorAll('[data-gm]').forEach(function(x){x.setAttribute('aria-selected',x===t)});b.querySelectorAll('.gmetro').forEach(function(m){m.hidden=m.dataset.m!==t.dataset.gm});return}
 var b=ev.target.closest&&ev.target.closest('[data-gf]'); if(!b) return;
 var wrap=b.closest('.sec,.gblock'); var grp=b.parentNode; var f=b.dataset.gf;
 if(f==='cats'){b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')==='true'?'false':'true')}
 else grp.querySelectorAll('[data-gf]:not([data-gf=cats])').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
 var mode=(grp.querySelector('[aria-pressed=true]:not([data-gf=cats])')||{dataset:{gf:'all'}}).dataset.gf, cats=grp.querySelector('[data-gf=cats]').getAttribute('aria-pressed')==='true';
 wrap.querySelectorAll('.gcard').forEach(function(c){var ok=(mode==='all'||c.dataset[mode]==='1')&&(!cats||c.dataset.cats==='1');c.hidden=!ok});
});
})();
