/* Popup: reads the active tab URL (activeTab permission, only when the user clicks the icon). Preview mode: popup.html?url=…&city=… */
(function(){
var BASE='https://petpolicycheck.com/';
var Q=new URLSearchParams(location.search);
var PAW='<ellipse cx="12" cy="15.6" rx="4.2" ry="3.4"/><circle cx="6.4" cy="10.6" r="1.7"/><circle cx="9.6" cy="6.9" r="1.8"/><circle cx="14.4" cy="6.9" r="1.8"/><circle cx="17.6" cy="10.6" r="1.7"/>';
var G={flight:'<path d="M12 2.9c.85 0 1.45.85 1.45 2.1v4.5l6.8 4v1.9l-6.8-2v4.1l2.1 1.6v1.6L12 19.8l-3.55.9v-1.6l2.1-1.6v-4.1l-6.8 2v-1.9l6.8-4V5c0-1.25.6-2.1 1.45-2.1Z"/>',
 hotel:'<path d="M3.5 6.5v12M20.5 18.5V14a3 3 0 0 0-3-3H11v3.5M3.5 14.5h17M3.5 17.5h17"/><circle cx="7.1" cy="11.6" r="1.7"/>',
 vet:'<path d="M12 20s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 10c0 5.6-7 10-7 10Z"/><path d="M12 9.5v5M9.5 12h5"/>',
 grooming:'<circle cx="6.5" cy="17.5" r="2.5"/><circle cx="12.5" cy="17.5" r="2.5"/><path d="M7.9 15.4 15 5.5M11.1 15.4 8.4 9.6M17.8 3.6v4M15.8 5.6h4"/>',paw:PAW};
function svg(k,s){return '<svg width="'+(s||18)+'" height="'+(s||18)+'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">'+G[k]+'</svg>'}
function pst(k,col){return '<span class="pst" style="--acc:'+col+'">'+svg(k)+'</span>'}
/* Near this hotel: real clinic from PetPolicyCheck USA clinics directory. Groomer row links to live hotels directory until a dedicated groomer dataset ships. */
var NEAR={'new-york':{vet:['The Animal Medical Center (AMC)','24/7 emergency · PPC clinics directory','https://www.amcny.org/'],groomer:['Find pet grooming near your stay','Ask the hotel / city guide · not a verified listing yet','https://petpolicycheck.com/hotels/']}};
function yn(v,txt){return v===true?'<span class="y">✓ '+(txt||'Yes')+'</span>':v===false?'<span class="n">✕ '+(txt||'No')+'</span>':'<span>'+(txt||'Check')+'</span>'}
function sp(s,re){return s?re.test(s):null}
function cm(d){var m=d&&d.match(/^([\d.]+) × ([\d.]+) × ([\d.]+) in/);return m?' <span style="color:#a7b0a2">('+[m[1],m[2],m[3]].map(function(v){return Math.round(v*2.54)}).join('×')+' cm)</span>':''}
function render(url){
 var app=document.getElementById('app'), m=url?PPC_MATCH.match(url):null, host=url?new URL(url).hostname.replace(/^www\./,''):'';
 var head='<div class="hd"><span class="lb"><img src="icons/logo-mark-header.png" alt=""></span><h1>Pets allowed?<small>PetPolicyCheck</small></h1>'+(host?'<span class="dom">'+host+'</span>':'')+'</div>';
 if(!m){app.innerHTML=head+'<div class="none">'+svg('paw',34)+'<h2>No pet rules for this site yet</h2><p>We cover 11 airlines and 10 U.S. hotel brands. Search all rules on PetPolicyCheck.</p><a class="btn pri" target="_blank" href="'+BASE+'">Open PetPolicyCheck</a></div>';return}
 var r=m.rec, col=m.theme==='flight'?'#98c6cc':'#d3a0b1'; document.documentElement.style.setProperty('--acc',col);
 var body='';
 if(m.type==='airline'){
  var dogs=sp(r.species,/dog/i), cats=sp(r.species,/cat/i), hold=/^yes|hold only|cargo via/i.test(r.hold)?true:/^no/i.test(r.hold)?false:null;
  body='<div class="ttl">'+pst('flight',col)+'<div><h2>'+r.name+'</h2><small>'+r.iata+' · verified '+r.verified+' on the official page</small></div></div>'+
   '<div class="verd"><div class="v"><b>Cabin</b>'+(r.cabin?'<span class="y">✓ Dogs '+(dogs===false?'✕':'✓')+' · Cats '+(cats===false?'✕':'✓')+'</span>':'<span class="n">✕ No pets in cabin</span>')+'</div>'+
   '<div class="v"><b>Hold / cargo</b>'+yn(hold,hold===true?'Yes':hold===false?'No':'Limited')+'</div></div>'+
   '<div class="facts"><div class="f"><b>Cabin fee</b><strong>'+r.fee+'</strong></div><div class="f"><b>Max bag</b><span><strong>'+(r.cabin?(r.dims||'Not stated on official page'):'Not applicable')+'</strong>'+cm(r.dims)+'</span></div>'+
   '<div class="f"><b>Max weight</b><span>'+r.weight+'</span></div><div class="f"><b>Hold</b><span>'+r.hold+'</span></div></div>'+
   '<div class="trap">'+svg('paw',14)+'<span>'+r.trap+'</span></div>'+
   '<div class="cta"><a class="btn pri" target="_blank" href="'+BASE+'pet-travel-checklist/">Open Pet Travel Passport checklist</a><a class="btn" target="_blank" href="'+BASE+'updates.html">Get alerted if rule changes</a></div>';
 } else if(m.type==='hotel'){
  var d2=sp(r.species,/dog|pet/i), c2=sp(r.species,/cat|pet/i), near=NEAR[Q.get('city')||''];
  body='<div class="ttl">'+pst('hotel',col)+'<div><h2>'+r.name.replace(/ \(.*\)/,'')+'</h2><small>Brand rules · checked '+r.verified+' on the official page</small></div></div>'+
   '<div class="verd"><div class="v"><b>Dogs</b>'+yn(d2===null?null:d2,d2===null?'Ask hotel':'Accepted')+'</div><div class="v"><b>Cats</b>'+yn(c2===null?null:c2,c2===null?'Ask hotel':'Accepted')+'</div></div>'+
   '<div class="facts"><div class="f"><b>Pet fee</b><strong>'+(r.fee||'Varies / ask the hotel')+'</strong></div><div class="f"><b>Weight limit</b><span>'+(r.weight||'Varies / ask the hotel')+'</span></div><div class="f"><b>Max pets</b><span>'+(r.pets||'Varies / ask the hotel')+'</span></div></div>'+
   (near?'<div class="near"><div class="nr">'+pst('grooming','#c2a8d4')+'<div><b>'+(near.groomer[2]?'<a target="_blank" rel="noopener" href="'+near.groomer[2]+'">'+near.groomer[0]+'</a>':near.groomer[0])+'<span class="tg">ask hotel</span></b><small>'+near.groomer[1]+'</small></div></div>'+
    '<div class="nr">'+pst('vet','#a7b1d3')+'<div><b>24/7 vet · '+near.vet[0]+'</b><small>'+near.vet[1]+'</small></div></div></div>':'')+
   '<div class="cta"><a class="btn pri" target="_blank" href="'+BASE+'hotels/'+(Q.get('city')?'pet-friendly-hotels-'+Q.get('city')+'.html':'')+'">Open our city guide</a><a class="btn" target="_blank" rel="sponsored nofollow" href="'+BASE+'book/">Compare pet-friendly stays</a></div>';
 } else {
  body='<div class="ttl">'+pst('hotel',col)+'<div><h2>'+r.name+'</h2><small>Booking portal · rules differ per property</small></div></div><div class="trap">'+svg('paw',14)+'<span>Open the property’s own pet policy before you pay: “pet-friendly” filters often hide fees and weight limits.</span></div><div class="cta"><a class="btn pri" target="_blank" href="'+BASE+'hotels/">Brand-by-brand pet rules</a></div>';
 }
 app.innerHTML=head+'<div class="bd">'+body+'</div><div class="ft"><span>Verified data · no tracking</span><a target="_blank" href="'+(r.src||BASE)+'">Official source ↗</a></div>';
}
if(Q.get('url')) render(Q.get('url'));
else if(window.chrome&&chrome.tabs&&chrome.tabs.query) chrome.tabs.query({active:true,currentWindow:true},function(t){render(t&&t[0]&&t[0].url)});
else render('');
})();
