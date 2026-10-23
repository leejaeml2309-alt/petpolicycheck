(function(){
var W=960,H=500,svg=d3.select('#map'),tip=document.getElementById('tip'),box=document.getElementById('mapbox');
var countries=topojson.feature(ATLAS,ATLAS.objects.countries).features.filter(function(f){return f.id!=='010'&&f.properties.name!=='Antarctica'});
var proj=d3.geoNaturalEarth1().fitExtent([[8,8],[W-8,H-8]],{type:'Sphere'}).rotate([-10,0]);
proj.fitExtent([[8,8],[W-8,H-8]],{type:'Sphere'});
var path=d3.geoPath(proj);
var g=svg.append('g');
g.append('path').attr('class','sphere').attr('d',path({type:'Sphere'}));
g.append('path').attr('class','grat').attr('d',path(d3.geoGraticule10()));
var cg=g.append('g');
cg.selectAll('path').data(countries).join('path')
 .attr('class',function(d){return 'country'+(GUIDES[d.id]?' has':'')}).attr('d',path)
 .attr('tabindex',0).attr('role','button').attr('aria-label',function(d){return d.properties.name+(GUIDES[d.id]?' (guide available)':'')})
 .on('click',function(e,d){openCountry(d.id)})
 .on('keydown',function(e,d){if(e.key==='Enter'||e.key===' '){e.preventDefault();openCountry(d.id)}})
 .on('mousemove',function(e,d){var r=box.getBoundingClientRect();tip.style.left=(e.clientX-r.left)+'px';tip.style.top=(e.clientY-r.top)+'px';tip.textContent=d.properties.name+(GUIDES[d.id]?' \u2022 guide available':'');tip.style.opacity=1})
 .on('mouseleave',function(){tip.style.opacity=0});
// decorative routes between hubs of airlines we cover
var hubs={ICN:[126.45,37.46],CDG:[2.55,49.0],FRA:[8.57,50.03],LHR:[-0.45,51.47],ATL:[-84.43,33.64],YYZ:[-79.6,43.68],JFK:[-73.78,40.64],SEA:[-122.3,47.45],NRT:[140.39,35.77]};
var routes=[['ICN','LHR'],['ICN','SEA'],['JFK','CDG'],['ATL','FRA'],['YYZ','LHR'],['SEA','NRT'],['JFK','LHR'],['ATL','NRT']];
var rg=g.append('g').attr('pointer-events','none');
routes.forEach(function(r){rg.append('path').attr('class','arc').attr('d',path({type:'LineString',coordinates:[hubs[r[0]],hubs[r[1]]]}))});
Object.keys(hubs).forEach(function(k){var p=proj(hubs[k]);rg.append('circle').attr('class','hub').attr('cx',p[0]).attr('cy',p[1]).attr('r',2.2)});
// pins for countries with a guide
Object.keys(GUIDES).forEach(function(id){var f=countries.find(function(c){return c.id===id});if(!f)return;var c=GUIDES[id].pin?proj(GUIDES[id].pin):path.centroid(f);
 var pin=g.append('g').attr('class','pin').attr('transform','translate('+c+')').style('cursor','pointer').on('click',function(){openCountry(id)});
 pin.append('circle').attr('class','ring').attr('r',6);pin.append('circle').attr('class','p').attr('r',5);
 pin.append('text').attr('x',9).attr('y',4).text((GUIDES[id].short||GUIDES[id].name)+' guide')});
// airplane button (Pacific)
var pp=proj([-40,14]);
var pb=g.append('g').attr('class','planebtn').attr('transform','translate('+pp+')').attr('tabindex',0).attr('role','button').attr('aria-label','Open airline pet policies')
 .on('click',function(){openAirlines()}).on('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();openAirlines()}});
pb.append('circle').attr('r',24);
pb.append('g').attr('transform','translate(-14,-14) scale(1.17) rotate(45 12 12)').html(PLANE);
pb.append('text').attr('y',42).attr('text-anchor','middle').text('Airline policies');
// zoom
var zoom=d3.zoom().scaleExtent([1,8]).translateExtent([[0,0],[W,H]]).filter(function(e){return !e.button&&e.type!=='wheel'&&e.type.indexOf('touch')!==0}).on('zoom',function(e){g.attr('transform',e.transform)});
svg.call(zoom).on('wheel.zoom',null);
document.getElementById('zin').onclick=function(){svg.transition().call(zoom.scaleBy,1.6)};
document.getElementById('zout').onclick=function(){svg.transition().call(zoom.scaleBy,1/1.6)};
var ms=document.getElementById('mapscroll');if(ms.scrollWidth>ms.clientWidth)ms.scrollLeft=(ms.scrollWidth-ms.clientWidth)*0.97;
// select list (accessible alternative)
var pick=document.getElementById('pick');
var og=document.createElement('optgroup');og.label='Country guides';pick.appendChild(og);
Object.keys(GUIDES).forEach(function(id){var G=GUIDES[id],o=document.createElement('option');o.value=id;o.textContent=G.flag+' '+(G.option||G.name+'  \u2605 guide');og.appendChild(o)});
var oa=document.createElement('optgroup');oa.label='All countries';pick.appendChild(oa);
countries.slice().sort(function(a,b){return a.properties.name.localeCompare(b.properties.name)}).forEach(function(c){var o=document.createElement('option');o.value=c.id;o.textContent=c.properties.name+(GUIDES[c.id]?'  \u2605 guide':'');oa.appendChild(o)});
pick.onchange=function(){if(pick.value)openCountry(pick.value);pick.value=''};
// panel
var panel=document.getElementById('panel'),scrim=document.getElementById('scrim');
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function show(h){panel.innerHTML=h;panel.classList.add('on');scrim.classList.add('on');panel.scrollTop=0;var x=panel.querySelector('.x');x.onclick=close;x.focus()}
function close(){panel.classList.remove('on');scrim.classList.remove('on');cg.selectAll('.country').classed('sel',false);if(location.hash)history.replaceState(null,'',location.pathname)}
scrim.onclick=close;document.addEventListener('keydown',function(e){if(e.key==='Escape')close()});
function top(k,t){return '<div class="ph-top"><div><div class="k">'+k+'</div><h2 id="ptitle">'+t+'</h2></div><button class="x" type="button" aria-label="Close">\u00d7</button></div>'}
function openCountry(id){
 var f=countries.find(function(c){return c.id===id});if(!f)return;
 cg.selectAll('.country').classed('sel',function(d){return d.id===id});
 var G=GUIDES[id],h;
 if(G&&G.kind==='link'){
  h=top('Pet travel rules \u00b7 dogs &amp; cats',G.flag+' '+esc(G.title||G.name))+'<div class="pbody">'
  +'<p class="lede">'+esc(G.line)+'</p>'
  +(G.summary?'<p>'+esc(G.summary)+'</p>':'')
  +(G.url?'<p><a class="btn big" href="'+G.url+'">'+esc(G.cta)+' \u2192</a></p>':'<p class="lede">Full USA guide coming soon.</p>')
  +'<h3>Flying there?</h3><p><a href="#airlines" data-open="airlines">Compare airline pet policies \u2708</a> \u00b7 <a href="'+LIVE+'products/under-seat-carrier-size-by-airline.html">Under-seat carrier sizes</a></p></div>';
 }else if(G){
  h=top('Pet import rules \u00b7 dogs &amp; cats',G.flag+' '+esc(G.name))+'<div class="pbody">'
  +'<p style="margin-top:0;color:var(--mut);font-size:.9rem">'+esc(G.scope)+'</p>'
  +'<h3>Main health rules &amp; obligations</h3><ul class="rules">'+G.rules.map(function(r){return '<li><b>'+r[0]+'</b><span>'+r[1]+'</span></li>'}).join('')+'</ul>'
  +'<h3>Official procedure</h3><a class="src" href="'+G.source+'" target="_blank" rel="noopener"><strong>'+esc(G.source_name)+' \u2197</strong>'+esc(G.source)+'</a>'
  +'<p class="note">Summary of the official page, checked '+esc(G.checked)+'. Rules change: always follow the official page and contact the Animal Quarantine Service at your arrival airport.</p>'
  +'<h3>Veterinary clinics (Tokyo, English-speaking)</h3>'
  +G.vets.map(function(v){return '<div class="vet"><strong>'+esc(v.name)+'</strong><div>'+esc(v.addr)+'</div><div>Tel: <a href="tel:+81'+v.tel.replace(/^0|-/g,'')+'">'+esc(v.tel)+'</a>'+(v.mail?' \u00b7 <a href="mailto:'+v.mail+'">'+esc(v.mail)+'</a>':'')+'</div>'+(v.hours?'<div>'+esc(v.hours)+'</div>':'')+'<div>'+esc(v.note)+' \u00b7 <a href="'+v.url+'" target="_blank" rel="noopener">Website / source \u2197</a></div></div>'}).join('')
  +'<p class="note">Clinic details copied from each clinic\'s own website (accessed Oct 23, 2026). Listing is not an endorsement; call ahead to confirm hours and services.</p>'
  +'<h3>Flying there?</h3><p><a href="#airlines" data-open="airlines">Compare airline pet policies \u2708</a> \u00b7 <a href="'+LIVE+'products/under-seat-carrier-size-by-airline.html">Under-seat carrier sizes</a></p></div>';
 }else{
  h=top('Pet import rules',esc(f.properties.name))+'<div class="pbody"><p><b>We haven\'t verified '+esc(f.properties.name)+' yet.</b></p>'
  +'<p>Every country guide on PetPolicyCheck is checked against the official government source and dated, so we only publish a country once that is done. Japan is our first guide.</p>'
  +'<p><a class="btn" href="mailto:contact@petpolicycheck.com?subject='+encodeURIComponent('Country guide request: '+f.properties.name)+'">Request this country</a></p>'
  +'<p><a href="'+LIVE+'forum/">Ask the community in the forum</a> \u00b7 <a href="#airlines" data-open="airlines">Airline pet policies \u2708</a></p></div>';
 }
 show(h);history.replaceState(null,'','#country='+encodeURIComponent(G?(G.slug||G.name):f.properties.name));
}
function openAirlines(){
 var na='<span class="na">Check with airline</span>';
 var h=top('\u2708 Dogs &amp; cats on board','Airline pet policies')+'<div class="pbody"><p style="margin-top:0;color:var(--mut);font-size:.9rem">'+AIRLINES.length+' airlines, each checked against its official pet policy page. Tap an airline for carrier sizes, all fees and route bans.</p>'
 +AIRLINES.map(function(a){var b=a.cabin===true?'<span class="badge yes">In cabin: yes</span>':a.cabin===false?'<span class="badge no">In cabin: no</span>':'<span class="badge na">Unconfirmed</span>';
  return '<div class="al"><div class="row"><strong>'+esc(a.name)+'</strong><span class="iata">'+a.iata+'</span>'+b+'</div><dl><dt>Fee from</dt><dd>'+(a.fee?esc(a.fee):na)+'</dd><dt>Max weight</dt><dd>'+(a.weight?esc(a.weight):na)+'</dd><dt>Hold/cargo</dt><dd>'+(a.cargo?esc(a.cargo):na)+'</dd><dt>Verified</dt><dd>'+(a.verified?esc(a.verified):'Official page unreachable on last check')+'</dd></dl>'
  +'<div class="lk"><a href="'+a.url+'">Full policy \u2192</a><a href="'+a.official+'" target="_blank" rel="noopener">Official page \u2197</a></div></div>'}).join('')
 +'<p class="note">"Check with airline" = not stated on, or not readable from, the official page on the date shown.</p></div>';
 show(h);history.replaceState(null,'','#airlines');
}
document.addEventListener('click',function(e){var a=e.target.closest('[data-open="airlines"]');if(a){e.preventDefault();openAirlines()}});
// table filter
var q=document.getElementById('q'),rows=document.querySelectorAll('#cmp tbody tr');
q.addEventListener('input',function(){var v=q.value.trim().toLowerCase();rows.forEach(function(r){r.hidden=v&&r.cells[0].textContent.toLowerCase().indexOf(v)<0})});
// deep links
// #airlines, #country=Japan, #country=USA, #country=United%20States, #country-392 (legacy numeric id)
function findCountry(v){
 v=decodeURIComponent(v||'').replace(/\+/g,' ').trim().toLowerCase();if(!v)return null;
 if(/^\d+$/.test(v)){while(v.length<3)v='0'+v;return countries.some(function(c){return c.id===v})?v:null}
 var ids=Object.keys(GUIDES);
 for(var i=0;i<ids.length;i++){var G=GUIDES[ids[i]];if([G.name,G.slug,G.short].concat(G.aliases||[]).some(function(n){return n&&n.toLowerCase()===v}))return ids[i]}
 var f=countries.find(function(c){return c.properties.name.toLowerCase()===v});return f?f.id:null}
function route(){
 var hs=location.hash||'',m;
 if(hs==='#airlines')openAirlines();
 else if((m=hs.match(/^#country[=\-](.+)$/))){var id=findCountry(m[1]);if(id)openCountry(id)}
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',route);else route();
window.addEventListener('hashchange',route);
window.PPC={openCountry:openCountry,openAirlines:openAirlines};
})();
