/* IT UI strings when on /it/ (EN source text otherwise). Locale packs also cover es/fr/de/ja for the directory. */
var PPC_GROOM_I18N=(function(){
 function lang(){try{
  var l=(document.documentElement.getAttribute('data-ppc-locale')||'').toLowerCase();
  if(l && (l==='it'||l==='es'||l==='fr'||l==='de'||l==='ja')) return l;
  var p=location.pathname||'';
  if(p.indexOf('/it/')===0) return 'it';
  if(p.indexOf('/es/')===0) return 'es';
  if(p.indexOf('/fr/')===0) return 'fr';
  if(p.indexOf('/de/')===0) return 'de';
  if(p.indexOf('/ja/')===0) return 'ja';
 }catch(e){} return 'en';}
 var IT={"filter.aria":"Filtri i toelettatori","filter.all":"Tutti","filter.travel":"✈️ Viaggio / senza appuntamento e mobile","filter.resident":"🏠 Residenti ed expat","filter.cats":"🐱 Gatti OK","uses.road.title":"✈️ In viaggio","uses.road.p":"Un lavaggio occasionale dopo il volo, vicino al Suo hotel o un furgone che si ferma all’hotel.","uses.settle.title":"🏠 Quando si installa","uses.settle.p":"Un toelettatore di quartiere abituale per residenti e nuovi expat: lingue, gatti senza sedazione, cani grandi.","partner.cta":"Diventi toelettatore verificato / partner","partner.note":"I toelettatori possono candidarsi per essere inseriti; ogni scheda è verificata sul sito ufficiale del toelettatore.","legend.confirmed":"confermato","legend.confirmed_on":"sul sito ufficiale del toelettatore","legend.ask":"chieda al salone","legend.ask_note":"non pubblicato: chiami prima di prenotare (i documenti di vaccino e di importazione variano).","empty":"Nessun toelettatore verificato è ancora elencato qui. I toelettatori verificati sono disponibili in queste città:","badge.intl_ok":"🌍 Passaporto antirabbico internazionale OK","badge.intl_ask":"🌍 Passaporto antirabbico internazionale · chieda al salone","badge.intl_ask_title":"Non pubblicato dal salone (accettazione del passaporto antirabbico internazionale non confermata)","badge.openview_yes":"👁️ Tavolo a vista · niente gabbie nascoste","badge.openview_na":"👁️ A vista · non applicabile, furgone alla Sua porta","badge.openview_ask":"👁️ Tavolo a vista · chieda al salone","badge.hotel_mobile":"🚐 Mobile in hotel","badge.sedation_free":"🐱 Gatti senza sedazione","badge.cats_ok":"🐱 Gatti OK","badge.large_dogs":"🐕 Cani da 25 kg in su","langs_title":"Lingue indicate","official_site":"Sito ufficiale ↗","section.h3":"Toelettatura","dir.h2":"{n} toelettatori verificati in {c} paesi","dir.country":"Paese","dir.city":"Città","dir.species":"Specie","dir.search":"Cerca","dir.search_ph":"Nome, città, paese o note","dir.all_countries":"Tutti i paesi","dir.all_cities":"Tutte le città","dir.sp_all":"Tutti","dir.sp_both":"Cani e gatti","dir.sp_dogs":"Cani","dir.sp_cats":"Gatti","dir.status":"Mostrati {n} di {total}","dir.empty":"Nessun salone corrisponde a questi filtri.","dir.map":"Mappa ↗"};
 var ES={"dir.h2":"{n} peluqueros verificados en {c} países","dir.country":"País","dir.city":"Ciudad","dir.species":"Especie","dir.search":"Buscar","dir.search_ph":"Nombre, ciudad, país o notas","dir.all_countries":"Todos los países","dir.all_cities":"Todas las ciudades","dir.sp_all":"Todos","dir.sp_both":"Perros y gatos","dir.sp_dogs":"Perros","dir.sp_cats":"Gatos","dir.status":"Mostrando {n} de {total}","dir.empty":"Ningún salón coincide con estos filtros.","dir.map":"Mapa ↗","official_site":"Sitio oficial ↗","partner.cta":"Conviértase en peluquero verificado / partner","partner.note":"Los peluqueros pueden solicitar ser incluidos; cada ficha se comprueba en el sitio oficial.","legend.confirmed":"confirmado","legend.confirmed_on":"en el sitio oficial del peluquero","legend.ask":"consulte al salón","legend.ask_note":"no publicado, llame antes de reservar (los papeles de vacunas e importación varían).","empty":"Aún no hay peluqueros verificados aquí. Hay peluqueros verificados en estas ciudades:"};
 var FR={"dir.h2":"{n} toiletteurs vérifiés dans {c} pays","dir.country":"Pays","dir.city":"Ville","dir.species":"Espèce","dir.search":"Rechercher","dir.search_ph":"Nom, ville, pays ou notes","dir.all_countries":"Tous les pays","dir.all_cities":"Toutes les villes","dir.sp_all":"Tous","dir.sp_both":"Chiens et chats","dir.sp_dogs":"Chiens","dir.sp_cats":"Chats","dir.status":"Affichage de {n} sur {total}","dir.empty":"Aucun salon ne correspond à ces filtres.","dir.map":"Carte ↗","official_site":"Site officiel ↗","partner.cta":"Devenez toiletteur vérifié / partenaire","partner.note":"Les toiletteurs peuvent demander à être inscrits ; chaque fiche est vérifiée sur le site officiel.","legend.confirmed":"confirmé","legend.confirmed_on":"sur le site officiel du toiletteur","legend.ask":"demandez au salon","legend.ask_note":"non publié, appelez avant de réserver (les papiers de vaccin et d’importation varient).","empty":"Aucun toiletteur vérifié n’est encore listé ici. Des toiletteurs vérifiés sont disponibles dans ces villes :"};
 var DE={"dir.h2":"{n} geprüfte Salons in {c} Ländern","dir.country":"Land","dir.city":"Stadt","dir.species":"Tierart","dir.search":"Suche","dir.search_ph":"Name, Stadt, Land oder Hinweise","dir.all_countries":"Alle Länder","dir.all_cities":"Alle Städte","dir.sp_all":"Alle","dir.sp_both":"Hunde und Katzen","dir.sp_dogs":"Hunde","dir.sp_cats":"Katzen","dir.status":"{n} von {total} angezeigt","dir.empty":"Kein Salon entspricht diesen Filtern.","dir.map":"Karte ↗","official_site":"Offizielle Website ↗","partner.cta":"Werden Sie geprüfter Groomer / Partner","partner.note":"Salons können sich bewerben; jeder Eintrag wird auf der offiziellen Website geprüft.","legend.confirmed":"bestätigt","legend.confirmed_on":"auf der offiziellen Website des Salons","legend.ask":"im Salon nachfragen","legend.ask_note":"nicht veröffentlicht, vor der Buchung anrufen (Impf- und Einfuhrpapiere variieren).","empty":"Hier ist noch kein geprüfter Salon gelistet. Geprüfte Salons gibt es in diesen Städten:"};
 var JA={"dir.h2":"{c}か国、確認済みグルーマー {n} 件","dir.country":"国","dir.city":"都市","dir.species":"対象","dir.search":"検索","dir.search_ph":"名前・都市・国・メモ","dir.all_countries":"すべての国","dir.all_cities":"すべての都市","dir.sp_all":"すべて","dir.sp_both":"犬と猫","dir.sp_dogs":"犬","dir.sp_cats":"猫","dir.status":"{total} 件中 {n} 件を表示","dir.empty":"この条件に合うサロンはありません。","dir.map":"地図 ↗","official_site":"公式サイト ↗","partner.cta":"確認済みグルーマー／パートナーになる","partner.note":"掲載を希望するグルーマーは申し込めます。各掲載は公式サイトで確認しています。","legend.confirmed":"確認済み","legend.confirmed_on":"グルーマーの公式サイトで","legend.ask":"サロンに確認","legend.ask_note":"未掲載のため、予約前にお電話ください（ワクチンや入国書類はサロンにより異なります）。","empty":"ここに確認済みのグルーマーはまだありません。確認済みのグルーマーがいる都市："};
 var PACK={it:IT,es:ES,fr:FR,de:DE,ja:JA};
 return {lang:lang,it:IT,t:function(k,en){var L=lang(),p=PACK[L];return p&&p[k]!=null?p[k]:en;}};
})();
function T(k,en){return PPC_GROOM_I18N.t(k,en);}
function Tf(k,en,vars){var s=T(k,en);if(vars)Object.keys(vars).forEach(function(v){s=s.split('{'+v+'}').join(vars[v]);});return s;}
/* PetPolicyCheck · Grooming (8e département) · composant partagé carte USA + pages Hôtels. Production.
   Données : window.PPC_GROOMERS (grooming-data.js, généré depuis vague-a-grooming.json, étendu 2026-11-27).
   Badges en 3 états : yes (confirmé sur le site officiel) · ask (non publié : à confirmer par téléphone) · na. */
(function(){
var D=window.PPC_GROOMERS||{};
var COUNTRY_ORDER=['USA','Canada','UK','France','Germany','Japan','South Korea','Australia'];
function e(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function types(g){return (g.type||[]).join(', ')}
function isTravel(g){return g.traveler_friendly===true&&(g.mobile_hotel===true||(g.type||[]).indexOf('salon')>=0)}
function badge(cls,txt,title){return '<span class="gb gb-'+cls+'"'+(title?' title="'+e(title)+'"':'')+'>'+txt+'</span>'}
function metroOf(g,key){return g.city||((key||'').split('|')[1]||'')}
function countryOf(g){return g.country||'USA'}
function card(g,metro,opts){
 var va=g.vaccines_accepted||{},b='';
 b+= va.accepts_international_rabies_cert===true ? badge('yes',T('badge.intl_ok','🌍 Intl Rabies Passport OK')) : badge('ask',T('badge.intl_ask','🌍 Intl rabies passport · ask salon'),T('badge.intl_ask_title','Not published by the salon (intl_rabies_passport_accepted unconfirmed)'));
 b+= g.open_view_table===true ? badge('yes',T('badge.openview_yes','👁️ Open-View Table · no hidden cages')) : g.open_view_table==='n/a_mobile_van' ? badge('na',T('badge.openview_na','👁️ Open-view · n/a, van at your door')) : badge('ask',T('badge.openview_ask','👁️ Open-view table · ask salon'));
 if(g.mobile_hotel===true) b+=badge('yes',T('badge.hotel_mobile','🚐 Hotel Mobile'));
 if(g.sedation_free===true&&g.cats_accepted===true) b+=badge('yes',T('badge.sedation_free','🐱 Sedation-Free Cats'));
 else if(g.cats_accepted===true) b+=badge('yes',T('badge.cats_ok','🐱 Cats OK'));
 if(g.large_dogs_25kg_plus===true) b+=badge('soft',T('badge.large_dogs','🐕 Dogs 25 kg+'));
 var langs=(g.languages||[]).join(' · ');
 var loc=e(g.district||metro);
 if(opts&&opts.showCountry) loc=e((g.city||metro)+', '+countryOf(g));
 var map=g.google_maps_url?' · <a href="'+e(g.google_maps_url)+'" target="_blank" rel="noopener">'+T('dir.map','Map ↗')+'</a>':'';
 var sp=(g.species||[]).slice().sort().join(',');
 return '<article class="gcard" data-id="'+e(g.id)+'" data-country="'+e(countryOf(g))+'" data-city="'+e(g.city||metro)+'" data-species="'+e(sp)+'" data-travel="'+(isTravel(g)?1:0)+'" data-resident="'+(g.resident_regular===true?1:0)+'" data-cats="'+(g.cats_accepted===true?1:0)+'">'+
  '<div class="gc-h"><a href="'+e(g.url)+'" target="_blank" rel="noopener">'+e(g.name)+'</a>'+(langs?'<span class="gl" title="'+T('langs_title','Languages listed')+'">🗣 '+e(langs)+'</span>':'')+'</div>'+
  '<p class="gc-m">'+loc+' · '+e(types(g))+'</p>'+
  '<div class="gbs">'+b+'</div>'+
  '<p class="gc-f"><a href="'+e(g.url)+'" target="_blank" rel="noopener">'+T('official_site','Official site ↗')+'</a>'+(g.phone?' · <span>'+e(g.phone)+'</span>':'')+map+'</p></article>';
}
function filters(){return '<div class="gfilter" role="group" aria-label="'+T('filter.aria','Filter groomers')+'">'+
 '<button type="button" data-gf="all" aria-pressed="true">'+T('filter.all','All')+'</button>'+
 '<button type="button" data-gf="travel" aria-pressed="false">'+T('filter.travel','✈️ Travel / Walk-in &amp; Mobile')+'</button>'+
 '<button type="button" data-gf="resident" aria-pressed="false">'+T('filter.resident','🏠 Resident &amp; Expat')+'</button>'+
 '<button type="button" data-gf="cats" aria-pressed="false" class="gf-tog">'+T('filter.cats','🐱 Cats OK')+'</button></div>'}
function uses(){return '<div class="guses"><div><b>'+T('uses.road.title','✈️ On the road')+'</b><span>'+T('uses.road.p','One-off wash after the flight, near your hotel or a van that parks at the hotel.')+'</span></div><div><b>'+T('uses.settle.title','🏠 Settling in')+'</b><span>'+T('uses.settle.p','A regular neighbourhood groomer for residents and new expats: languages, cats without sedation, big dogs.')+'</span></div></div>'}
function partner(up){var L=PPC_GROOM_I18N.lang();var href=(L&&L!=='en'?'/'+L+'/contact.html':'/contact.html')+'?topic=groomer';return '<p class="gpartner"><a class="btn ghost" href="'+href+'">'+T('partner.cta','Become a Verified Groomer / Partner')+'</a><span>'+T('partner.note','Groomers can apply to be listed; each listing is checked on the groomer’s official site.')+'</span></p>'}
var legend='<p class="glegend"><span class="gb gb-yes">'+T('legend.confirmed','confirmed')+'</span> '+T('legend.confirmed_on','on the groomer’s official site')+' · <span class="gb gb-ask">'+T('legend.ask','ask salon')+'</span> '+T('legend.ask_note','not published, call before you book (vaccine and import papers vary).')+'</p>';
function list(keys){var h='';keys.forEach(function(k){var c=k.split('|')[1];h+='<div class="gmetro" data-m="'+e(k)+'"><h4>'+e(c)+'</h4><div class="ggrid">'+D[k].map(function(g){return card(g,c)}).join('')+'</div></div>'});return h}
function allListings(){
 var out=[];
 Object.keys(D).forEach(function(k){
  (D[k]||[]).forEach(function(g){ out.push({g:g,key:k,city:metroOf(g,k),country:countryOf(g)}); });
 });
 return out;
}
function uniqueCountries(rows){
 var set={};
 rows.forEach(function(r){ set[r.country]=1; });
 return COUNTRY_ORDER.filter(function(c){ return set[c]; }).concat(Object.keys(set).filter(function(c){ return COUNTRY_ORDER.indexOf(c)<0; }).sort());
}
function uniqueCities(rows,country){
 var set={};
 rows.forEach(function(r){ if(!country||r.country===country) set[r.city]=1; });
 return Object.keys(set).sort(function(a,b){ return a.localeCompare(b); });
}
function directoryHtml(){
 var rows=allListings(), total=rows.length, countries=uniqueCountries(rows);
 var h2=Tf('dir.h2','{n} verified groomers across {c} countries',{n:String(total),c:String(countries.length)});
 var countryOpts='<option value="">'+e(T('dir.all_countries','All countries'))+'</option>'+countries.map(function(c){return '<option value="'+e(c)+'">'+e(c)+'</option>';}).join('');
 var cityOpts='<option value="">'+e(T('dir.all_cities','All cities'))+'</option>'+uniqueCities(rows,'').map(function(c){return '<option value="'+e(c)+'">'+e(c)+'</option>';}).join('');
 var bar='<form class="gdir-bar" role="search" aria-label="'+e(T('filter.aria','Filter groomers'))+'" onsubmit="return false">'+
  '<label>'+e(T('dir.country','Country'))+'<select data-gdir="country">'+countryOpts+'</select></label>'+
  '<label>'+e(T('dir.city','City'))+'<select data-gdir="city">'+cityOpts+'</select></label>'+
  '<label>'+e(T('dir.species','Species'))+'<select data-gdir="species">'+
    '<option value="">'+e(T('dir.sp_all','All'))+'</option>'+
    '<option value="dogs,cats">'+e(T('dir.sp_both','Dogs &amp; Cats'))+'</option>'+
    '<option value="dogs">'+e(T('dir.sp_dogs','Dogs'))+'</option>'+
    '<option value="cats">'+e(T('dir.sp_cats','Cats'))+'</option>'+
  '</select></label>'+
  '<label class="gdir-q">'+e(T('dir.search','Search'))+'<input type="search" data-gdir="q" maxlength="80" placeholder="'+e(T('dir.search_ph','Name, city, country or notes'))+'"></label>'+
  '</form>';
 var cards=rows.map(function(r){
  var hay=[r.g.name,r.city,r.country,r.g.region,r.g.notes,r.g.address,r.g.district,(r.g.languages||[]).join(' ')].join(' ').toLowerCase();
  return card(r.g,r.city,{showCountry:true}).replace('<article ','<article data-hay="'+e(hay)+'" ');
 }).join('');
 return '<div class="gdir theme-grooming">'+
  '<h2 id="directory">'+h2+'</h2>'+bar+
  '<p class="gdir-status" data-gdir-status></p>'+
  '<div class="gdir-grid">'+cards+'</div>'+
  '<p class="gdir-empty" data-gdir-empty hidden>'+e(T('dir.empty','No salons match these filters.'))+'</p>'+
  legend+partner()+
  '</div>';
}
function applyDirectory(root){
 var country=(root.querySelector('[data-gdir=country]')||{}).value||'';
 var city=(root.querySelector('[data-gdir=city]')||{}).value||'';
 var species=(root.querySelector('[data-gdir=species]')||{}).value||'';
 var q=((root.querySelector('[data-gdir=q]')||{}).value||'').trim().toLowerCase();
 var cards=root.querySelectorAll('.gdir-grid .gcard');
 var n=0, total=cards.length;
 cards.forEach(function(c){
  var ok=true;
  if(country && c.getAttribute('data-country')!==country) ok=false;
  if(city && c.getAttribute('data-city')!==city) ok=false;
  if(species){
   var sp=(c.getAttribute('data-species')||'');
   if(species==='dogs,cats'){ if(sp!=='cats,dogs' && sp!=='dogs,cats') ok=false; }
   else if(sp.split(',').indexOf(species)<0) ok=false;
  }
  if(q){
   var hay=c.getAttribute('data-hay')||c.textContent.toLowerCase();
   if(hay.indexOf(q)<0) ok=false;
  }
  c.hidden=!ok;
  if(ok) n++;
 });
 var st=root.querySelector('[data-gdir-status]');
 if(st) st.textContent=Tf('dir.status','Showing {n} of {total}',{n:String(n),total:String(total)});
 var empty=root.querySelector('[data-gdir-empty]');
 if(empty) empty.hidden=n!==0;
}
function refillCities(root){
 var country=(root.querySelector('[data-gdir=country]')||{}).value||'';
 var citySel=root.querySelector('[data-gdir=city]');
 if(!citySel) return;
 var prev=citySel.value;
 var cities=[];
 var seen={};
 root.querySelectorAll('.gdir-grid .gcard').forEach(function(c){
  if(country && c.getAttribute('data-country')!==country) return;
  var name=c.getAttribute('data-city');
  if(name && !seen[name]){ seen[name]=1; cities.push(name); }
 });
 cities.sort(function(a,b){ return a.localeCompare(b); });
 citySel.innerHTML='<option value="">'+e(T('dir.all_cities','All cities'))+'</option>'+cities.map(function(c){return '<option value="'+e(c)+'">'+e(c)+'</option>';}).join('');
 if(prev && seen[prev]) citySel.value=prev;
}
window.PPC_GROOM={
 section:function(cur){
  if(!cur) return '';
  var a=cur.a,n=cur.n,keys=[];
  if(n&&D[a+'|'+n]) keys=[a+'|'+n]; else keys=Object.keys(D).filter(function(k){return k.indexOf(a+'|')===0});
  var h='<section class="sec theme-grooming" data-sec="5" data-dept="grooming"><h3><span class="n">5</span>'+T('section.h3','Grooming')+'</h3>';
  if(!keys.length){
   var all=Object.keys(D).filter(function(k){ var g=(D[k]||[])[0]; return !g||countryOf(g)==='USA'; }).map(function(k){var p=k.split('|');return '<button type="button" data-s="'+p[0]+'" data-city="'+e(p[1])+'">'+e(p[1])+'</button>'}).join('');
   return h+'<p>'+T('empty','No verified groomer listed here yet. Verified groomers are listed for these cities:')+'</p><div class="citylist">'+all+'</div>'+partner()+'</section>';
  }
  return h+uses()+filters()+list(keys)+legend+partner()+'</section>';
 },
 block:function(keys,up,first){
  var tabs='<div class="gmtabs" role="tablist">'+keys.map(function(k){return '<button type="button" role="tab" data-gm="'+e(k)+'" aria-selected="'+(k===first)+'">'+e(k.split('|')[1])+'</button>'}).join('')+'</div>';
  return '<div class="gblock theme-grooming" data-first="'+e(first)+'">'+uses()+tabs+filters()+list(keys)+legend+partner(up)+'</div>'},
 initBlocks:function(){document.querySelectorAll('.gblock').forEach(function(b){var f=b.dataset.first;b.querySelectorAll('.gmetro').forEach(function(m){m.hidden=m.dataset.m!==f})})},
 directory:function(){ return directoryHtml(); },
 initDirectory:function(scope){
  var root=(scope||document).querySelector('.gdir');
  if(!root) return;
  function run(){ applyDirectory(root); }
  root.addEventListener('change',function(ev){
   if(!ev.target || !ev.target.getAttribute) return;
   if(ev.target.getAttribute('data-gdir')==='country'){ refillCities(root); }
   run();
  });
  root.addEventListener('input',function(ev){
   if(ev.target && ev.target.getAttribute && ev.target.getAttribute('data-gdir')==='q') run();
  });
  run();
 },
 count:function(){var n=0;for(var k in D)n+=D[k].length;return n},
 countries:function(){return uniqueCountries(allListings())}
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
