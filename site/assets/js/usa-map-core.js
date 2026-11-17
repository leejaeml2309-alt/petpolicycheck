/* USA pet-travel map behavior. GEO and USA_RULES are loaded first.
   Eight sample cities have local transport and hotel-guide links; every other city is an explicit placeholder. */
const GEO = window.GEO;
const RULES = window.USA_RULES;
const ON_ES=(location.pathname||'').indexOf('/es/')===0;
const SITE=ON_ES?"":"..";
function siteUrl(path){
  /* path like /clinics/usa.html or /hotels/pet-friendly-….html */
  var p=path.charAt(0)==='/'?path:'/'+path;
  if(!ON_ES) return '..'+p;
  /* Prefer /es/ when an ES page exists; else site-root EN. */
  var ES={
    'countries/usa.html':1,'countries/canada.html':1,'countries/mexico.html':1,
    'countries/usa-map.html':1,'countries/canada-map.html':1,'countries/mexico-map.html':1,
    'grooming/':1,'grooming/index.html':1,'fit/':1,'pet-travel-checklist/':1,
    'routes/usa-canada.html':1,'routes/usa-mexico.html':1,'routes/usa-france.html':1,
    'routes/usa-uk.html':1,'routes/usa-to-japan.html':1,
    'airlines/snub-nosed-breeds.html':1,'airlines/compare/':1,'passport/':1
  };
  var rel=p.replace(/^\/+/, '');
  var key=rel; if(key && key.slice(-1)!=='/' && key.indexOf('.html')<0) key=key+'/';
  if(ES[rel]||ES[key]||ES[rel.replace(/\/$/,'')+'/index.html']) return '/es/'+rel;
  return p;
}

const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const enc=encodeURIComponent;
const ABBRS=Object.keys(GEO).filter(a=>a!=="DC").sort((a,b)=>GEO[a].name.localeCompare(GEO[b].name));
const TINY=["VT","NH","MA","RI","CT","NJ","DE","MD"];
/* ---------- links ---------- */
const TAG={aff:"Affiliate",off:"Official",srch:"Search",stub:"Stub"};
function lk(ic,title,sub,href,tag){return `<a class="lk" href="${esc(href)}" target="_blank" rel="${tag==='aff'?'sponsored nofollow noopener':'noopener'}"><span class="ic" aria-hidden="true">${ic}</span><span class="t">${esc(title)}${sub?`<small>${esc(sub)}</small>`:""}</span><span class="tag ${tag}">${TAG[tag]}</span></a>`}
const FED={
 cdc:["https://www.cdc.gov/importation/dogs/index.html","CDC: Bringing a dog into the US","Dog Import Form + rules for dogs arriving from abroad"],
 aphisIn:["https://www.aphis.usda.gov/pet-travel/another-country-to-us-import","USDA APHIS: Bring a pet into the US","Cats, dogs and other pets entering from another country"],
 aphisSS:["https://www.aphis.usda.gov/pet-travel/state-to-state","USDA APHIS: State-to-state travel","No federal rule between states: the destination state decides"],
 aphisAir:["https://www.aphis.usda.gov/pet-travel/pets-on-planes/preparing-pets-air-travel","USDA APHIS: Preparing pets for air travel","Airlines may want a health certificate within 10 days"],
 aphisOut:["https://www.aphis.usda.gov/pet-travel/us-to-another-country-export","USDA APHIS: Take a pet from the US abroad","Export health certificates (endorsed by APHIS)"],
 dot:["https://www.transportation.gov/individuals/aviation-consumer-protection/service-animals","US DOT: Service animals on flights","Federal rule for service dogs in the cabin"],
};
const fed=(k,ic="🏛")=>lk(ic,FED[k][1],FED[k][2],FED[k][0],"off");
const RIDES=lk("🚗","Uber Pet","One pet per trip, surcharge in the upfront fare","https://help.uber.com/en/riders/article/uber-pet-pet-friendly-rides?nodeId=e4468070-c193-41cf-b792-fa66ecfb1163","off")+
 lk("🚙","Lyft Pet","One well-behaved animal; US only; extra fee","https://help.lyft.com/hc/en-us/all/articles/8559088908-Pet-rides-for-riders","off");
const AMTRAK_NOTE="Amtrak: dogs and cats, 20 lb max incl. carrier, trips up to 7 hours, Coach (+Acela Business); reserve the pet spot.";
/* ---------- 8 sample cities ---------- */
const SAMPLE={
 "NY|New York City":{q:"New York, NY",amtrak:["nyp","New York Penn Station (NYP)"],guide:"/hotels/pet-friendly-hotels-new-york.html",
  taxi:[["🚕","NYC Taxi & Limousine Commission","Yellow/green cabs and for-hire rules","https://www.nyc.gov/site/tlc/index.page","off"]],
  transit:[["🚇","MTA: subway, buses, LIRR, Metro-North","Check MTA pet rule before riding","https://new.mta.info/","off"]],
  rail:[["🚆","NJ Transit","Trains to New Jersey / Newark Airport","https://www.njtransit.com/","off"]]},
 "CA|Los Angeles":{q:"Los Angeles, CA",amtrak:["lax","Los Angeles Union Station (LAX)"],
  taxi:[["🚕","LADOT Taxi program","City-licensed taxicabs","https://ladot.lacity.gov/","off"]],
  transit:[["🚌","LA Metro","Buses and Metro Rail","https://www.metro.net/","off"]],
  rail:[["🚆","Metrolink","Southern California commuter rail","https://metrolinktrains.com/","off"]]},
 "IL|Chicago":{q:"Chicago, IL",amtrak:["chi","Chicago Union Station (CHI)"],
  taxi:[["🚕","City of Chicago: Taxis (BACP)","Licensed taxis & rideshare rules","https://www.chicago.gov/city/en/depts/bacp.html","off"]],
  transit:[["🚇","CTA","'L' trains and buses","https://www.transitchicago.com/","off"]],
  rail:[["🚆","Metra","Commuter rail to the suburbs","https://metra.com/","off"]]},
 "FL|Miami":{q:"Miami, FL",amtrak:["mia","Miami station (MIA)"],guide:"/hotels/pet-friendly-hotels-miami.html",
  taxi:[["🚕","Miami-Dade: for-hire vehicles","County-regulated taxis","https://www.miamidade.gov/global/transportation/home.page","off"]],
  transit:[["🚌","Miami-Dade Transit","Metrobus, Metrorail, Metromover","https://www.miamidade.gov/global/transportation/home.page","off"]],
  rail:[["🚄","Brightline","Miami ↔ Orlando (check its pet policy)","https://www.gobrightline.com/","off"],["🚆","Tri-Rail","South Florida commuter rail","https://www.tri-rail.com/","off"]]},
 "TX|Houston":{q:"Houston, TX",amtrak:["hos","Houston station (HOS)"],
  taxi:[["🚕","City of Houston: Regulatory Affairs","Licensed taxis","https://www.houstontx.gov/ara/","off"]],
  transit:[["🚌","METRO Houston","Buses and METRORail","https://www.ridemetro.org/","off"]],rail:[]},
 "WA|Seattle":{q:"Seattle, WA",amtrak:["sea","Seattle King Street (SEA)"],
  taxi:[["🚕","King County: taxi & for-hire licensing","","https://kingcounty.gov/","off"]],
  transit:[["🚌","King County Metro","Buses and water taxi","https://kingcounty.gov/en/dept/metro","off"]],
  rail:[["🚆","Sound Transit","Link light rail (SEA airport) and Sounder","https://www.soundtransit.org/","off"]]},
 "CO|Denver":{q:"Denver, CO",amtrak:["den","Denver Union Station (DEN)"],
  taxi:[],transit:[["🚌","RTD Denver","Buses and rail, incl. A Line to DEN airport","https://www.rtd-denver.com/","off"]],rail:[]},
 "GA|Atlanta":{q:"Atlanta, GA",amtrak:["atl","Atlanta Peachtree (ATL)"],
  taxi:[],transit:[["🚇","MARTA","Rail to ATL airport and buses","https://www.itsmarta.com/","off"]],rail:[]},
};
/* Airports for the 8 sample metros, plus two placeholder hubs (SFO, DFW),
   ANC/HNL, 17 FAA large hubs with named map labels (mapLabel/mapName):
   LAS, MCO, CLT, PHX, BOS, FLL, MSP, DTW, PHL, SLC, BWI, DCA, SAN, IAD, TPA, BNA, AUS,
   and one airport for each state that previously had none (FAA CY2024 busiest,
   or the main international field): BHM, LIT, BDL, ILG, DSM, BOI, IND, ICT, CVG,
   MSY, PWM, STL, JAN, BZN, FAR, OMA, MHT, ABQ, CLE, OKC, PDX, PVD, CHS, FSD,
   BTV, CRW, MKE, JAC. Pins use real GPS in the map's Albers USA projection,
   then a short offset so the mark is not on its city dot.
   metroCity/metroState is the booking panel. placeState is where the dot sits
   (EWR is in New Jersey and still belongs to New York City; DCA and IAD sit in
   Virginia and belong to Washington, DC; CVG sits in Kentucky and belongs to
   Cincinnati, Ohio). pets:null = placeholder. */
const PLANE="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5z";
const AIRPORTS=window.AIRPORTS;

function cityXY(state, name){
 const list=(GEO[state]&&GEO[state].cities)||[];
 const c=list.find(x=>x.n===name);
 if(c) return [c.x,c.y];
 if(GEO[state]) return GEO[state].c;
 return null;
}
function airportsFor(state, city){
 const seen=new Set();
 return AIRPORTS.filter(ap=>{
  const hit=city
    ? (ap.metroCity===city && ap.metroState===state) || (ap.localCity===city && ap.placeState===state)
    : ap.placeState===state || ap.metroState===state;
  if(!hit || seen.has(ap.code)) return false;
  seen.add(ap.code); return true;
 });
}
function airportByCode(code){return AIRPORTS.find(ap=>ap.code===code)}
const HD=`style="font:600 .72rem var(--text);letter-spacing:.1em;text-transform:uppercase;color:var(--gold);margin:8px 0 0"`;
function airportChips(list, heading){
 if(!list.length) return "";
 return `<h4 ${HD}>${esc(heading)}</h4><div class="citylist">${list.map(ap=>`<button type="button" class="apbtn${ap.pets?"":" placeholder"}" data-ap="${esc(ap.code)}" aria-label="${esc(ap.code)}, ${esc(ap.metroCity)}">${esc(ap.code)} — ${esc(ap.metroCity)}</button>`).join("")}</div>`;
}
/* ---------- distinct state marks ---------- */
const GLYPH=[
 "M32 14l4.7 9.6 10.6 1.5-7.7 7.5 1.8 10.5L32 38.1l-9.4 5 1.8-10.5-7.7-7.5 10.6-1.5z",
 "M14 42l11-17 6 8 5-6 14 15z",
 "M13 30c4-5 8-5 12 0s8 5 12 0 8-5 12 0M13 39c4-5 8-5 12 0s8 5 12 0 8-5 12 0",
 "M32 23a8 8 0 1 1 0 16a8 8 0 1 1 0-16M32 14v5M32 43v5M18 31h5M41 31h5M22 21l3 3M39 38l3 3M42 21l-3 3M25 38l-3 3",
 "M32 13l9 12h-5l7 9h-5l7 9H19l7-9h-5l7-9h-5zM30 43h4v5h-4z",
 "M32 30c-6 0-10 6-10 10 0 3 3 4 6 3 2-1 6-1 8 0 3 1 6 0 6-3 0-4-4-10-10-10zM22 27a3.5 4.5 0 1 0 .1 0M42 27a3.5 4.5 0 1 0 .1 0M27 18a3.5 4.5 0 1 0 .1 0M37 18a3.5 4.5 0 1 0 .1 0",
 "M16 46C19 30 30 19 48 16c-2 16-14 27-32 30zM16 46C26 36 33 28 42 22",
 "M32 13l5 18-5 18-5-18zM14 31l18-5 18 5-18 5z",
 "M32 15v32M22 47h20M24 22h16M32 15a3 3 0 1 0 .1 0M20 36c2 7 22 7 24 0",
 "M18 20h28v24H18zM18 28h28M26 20v24M38 20v24",
];
const FILLED=new Set([0,1,4,5,6,7]);
function mark(a,size){
 const i=ABBRS.indexOf(a)<0?50:ABBRS.indexOf(a);
 const h=Math.round((i*137.508)%360), g=i%GLYPH.length, ring=Math.floor(i/GLYPH.length)%3;
 const bg=`hsl(${h} 38% 24%)`, acc=`hsl(${h} 60% 72%)`;
 const dash=ring===1?'stroke-dasharray="2 3"':ring===2?'stroke-dasharray="7 2 1 2"':"";
 const gl=FILLED.has(g)?`<path d="${GLYPH[g]}" fill="${acc}" opacity=".95"/>`:`<path d="${GLYPH[g]}" fill="none" stroke="${acc}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>`;
 return `<svg viewBox="0 0 64 64" ${size?`width="${size}" height="${size}"`:""} aria-hidden="true"><circle cx="32" cy="32" r="30" fill="#0b1719" stroke="#d9b765" stroke-width="2"/><circle cx="32" cy="32" r="25.5" fill="${bg}" stroke="#d9b765" stroke-width="1" ${dash}/><g transform="translate(32 25) scale(.62) translate(-32 -31)">${gl}</g><text x="32" y="50" text-anchor="middle" font-family="Marcellus,serif" font-size="11" fill="#f5ecd6" letter-spacing="1">${a}</text></svg>`;
}
/* ---------- map ---------- */
const NS="http://www.w3.org/2000/svg";
const el=(t,at)=>{const e=document.createElementNS(NS,t);for(const k in at)e.setAttribute(k,at[k]);return e};

/* Pet-travel hub & rule density score → 5-tier red choropleth (Marc 2026-11-07).
   Deterministic from SAMPLE / AIRPORTS / CLINICS / RULES / GEO already on the page. */
const HOTEL_GUIDE_STATES=new Set(["CA","NY","FL","IL","TX","MI","WA","CO","GA"]);
function stateDensityScore(a){
  let s=0;
  const apN=AIRPORTS.filter(ap=>ap.placeState===a||ap.metroState===a).length;
  s+=apN*2;
  const clinicN=Object.keys(CLINICS).filter(k=>k.startsWith(a+"|")).length;
  s+=clinicN*1.5;
  const hasSample=Object.keys(SAMPLE).some(k=>k.startsWith(a+"|"));
  if(hasSample||HOTEL_GUIDE_STATES.has(a)) s+=3;
  if(RULES[a]&&RULES[a].differs) s+=1.5;
  if(RULES[a]&&RULES[a].verified) s+=1;
  const cities=((GEO[a]&&GEO[a].cities)||[]).length;
  s+=cities*0.5;
  return s;
}

/* Frozen choropleth, 17 Nov 2026: adding the missing-state airports must not
   reshape the quantile buckets or change existing state colours. */
const FROZEN_DENSITY_TIERS={AK:3,AL:2,AR:1,AZ:4,CA:5,CO:4,CT:1,DC:4,DE:4,FL:5,GA:5,HI:4,IA:2,ID:1,IL:5,IN:1,KS:1,KY:1,LA:2,MA:4,MD:3,ME:2,MI:4,MN:4,MO:2,MS:1,MT:2,NC:5,ND:2,NE:2,NH:3,NJ:3,NM:2,NV:3,NY:5,OH:4,OK:3,OR:3,PA:4,RI:1,SC:2,SD:3,TN:5,TX:5,UT:4,VA:5,VT:3,WA:5,WI:3,WV:1,WY:1};
function assignDensityTiers(){
  const states=ABBRS.slice();
  const scored=states.map(a=>({a,score:stateDensityScore(a)})).sort((x,y)=>x.score-y.score||x.a.localeCompare(y.a));
  const tiers=Object.assign({}, FROZEN_DENSITY_TIERS);
  if(GEO.DC && tiers.DC==null){ const d=Math.round(((tiers.VA||3)+(tiers.MD||3))/2); tiers.DC=Math.max(1,Math.min(5,d)); }
  window.PPC_USA_DENSITY_TIERS=tiers;
  window.PPC_USA_DENSITY_SCORES=Object.fromEntries(scored.map(r=>[r.a,r.score]));
  return tiers;
}
const TIER_FILL={1:"#d9828b",2:"#be4f5c",3:"#a82c3a",4:"#841c29",5:"#5c111b"};
function tierFill(a){const t=(window.PPC_USA_DENSITY_TIERS||{})[a]||1;return TIER_FILL[t]||TIER_FILL[1]}

function buildStates(){
 const gs=$("#g-st"),gl=$("#g-lb"),gc=$("#g-ct");
 const tiers=assignDensityTiers();
 for(const a of Object.keys(GEO)){
  const s=GEO[a];
  const special=!!(RULES[a]&&RULES[a].differs), unver=!!(RULES[a]&&!RULES[a].verified);
  const tier=tiers[a]||1;
  const p=el("path",{d:s.d,class:"st st-t"+tier+(special?" rule":""),id:"s-"+a,"data-tier":String(tier),"data-density":String((window.PPC_USA_DENSITY_SCORES||{})[a]||0),tabindex:a==="DC"?-1:0,role:"button","aria-label":s.name+(special?" (special entry rules)":"")+", density tier "+tier});
  const t=el("title",{});t.textContent=s.name;p.appendChild(t);
  p.addEventListener("click",()=>a==="DC"?selectDC():selectState(a));
  p.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();selectState(a)}});
  gs.appendChild(p);
 }
 // labels; tiny NE states get callouts in the Atlantic
 const tiny=TINY.map(a=>({a,y:GEO[a].c[1],x:GEO[a].c[0]})).sort((p,q)=>p.y-q.y);
 let last=-1e9;for(const t of tiny){t.ly=Math.max(t.y,last+17);last=t.ly}
 const shift=(tiny[0].y+tiny.at(-1).y)/2-(tiny[0].ly+tiny.at(-1).ly)/2;
 for(const a of ABBRS){
  if(TINY.includes(a))continue;
  let [x,y]=GEO[a].c; if(a==="FL")x+=12; if(a==="MI"){x+=12;y+=22} if(a==="LA")x-=10; if(a==="CO")y+=16; if(a==="HI"){x=GEO.HI.c[0]+12;y=GEO.HI.c[1]+14}
  const t=el("text",{x,y,class:"lbl",id:"l-"+a});t.textContent=a;t.dataset.abbr=a;t.dataset.full=(GEO[a]&&GEO[a].name)||a;gl.appendChild(t);
 }
 for(const t of tiny){
  const ly=t.ly+shift, lx=948;
  gl.appendChild(el("line",{class:"lbl-lead",x1:t.x,y1:t.y,x2:lx-14,y2:ly,stroke:"#3a5a56","stroke-width":.8,"data-a":t.a}));
  const g=el("g",{class:"ct",role:"button",tabindex:0,"aria-label":GEO[t.a].name});
  const r=el("rect",{x:lx-13,y:ly-8,width:26,height:16,rx:8,fill:tierFill(t.a),stroke:"#1a0b0e","data-tier":String(tiers[t.a]||1),id:"cb-"+t.a});
  const tx=el("text",{x:lx,y:ly,class:"lbl",id:"l-"+t.a});tx.textContent=t.a;tx.dataset.abbr=t.a;tx.dataset.full=(GEO[t.a]&&GEO[t.a].name)||t.a;
  g.append(r,tx);g.addEventListener("click",()=>selectState(t.a));
  g.addEventListener("keydown",e=>{if(e.key==="Enter"){selectState(t.a)}});gl.appendChild(g);
 }
}
function buildCitiesAndAirports(){
 const gc=$("#g-ct");
 // cities
 for(const a of ABBRS){for(const c of GEO[a].cities){
  const key=a+"|"+c.n, smp=!!SAMPLE[key];
  const g=el("g",{class:"ct"+(c.cap?" cap":"")+(smp?" sample":" hide-lbl"),role:"button",tabindex:smp?0:-1,"aria-label":c.n+", "+a,"data-k":key,"data-s":a});
  if(smp)g.appendChild(el("circle",{class:"ring",cx:c.x,cy:c.y,r:8.5}));
  g.appendChild(el("circle",{cx:c.x,cy:c.y,r:smp?5:3}));
  const right=c.x<880;const tx=el("text",{x:c.x+(right?8:-8),y:c.y+3.5,"text-anchor":right?"start":"end"});tx.textContent=c.n==="New York City"?"NYC":c.n;g.appendChild(tx);
  const tt=el("title",{});tt.textContent=c.n+", "+GEO[a].name;g.appendChild(tt);
  g.addEventListener("click",e=>{e.stopPropagation();selectCity(a,c.n)});
  g.addEventListener("keydown",e=>{if(e.key==="Enter"){selectCity(a,c.n)}});
  gc.appendChild(g);
 }}
 const dc=GEO.DC.city;const g=el("g",{class:"ct cap",role:"button",tabindex:-1,"aria-label":"Washington, DC"});
 g.appendChild(el("circle",{cx:dc.x,cy:dc.y,r:3}));const tt=el("title",{});tt.textContent="Washington, DC (District of Columbia)";g.appendChild(tt);
 g.addEventListener("click",e=>{e.stopPropagation();selectDC()});gc.appendChild(g);
 buildAirports();
}
function buildMap(){ buildStates(); buildCitiesAndAirports(); }
function buildAirports(){
 let ga=$("#g-ap");
 if(!ga){ga=el("g",{id:"g-ap"}); $("#map").appendChild(ga);}
 for(const ap of AIRPORTS){
  const xy=cityXY(ap.metroState, ap.metroCity); if(!xy) continue;
  const states=[ap.metroState, ap.placeState].filter((v,i,a)=>a.indexOf(v)===i).join(" ");
  const citykey=ap.metroState+"|"+ap.metroCity;
  ga.appendChild(el("line",{class:"ap-link"+(ap.pets?"":" placeholder"),x1:xy[0],y1:xy[1],x2:ap.x,y2:ap.y,"data-states":states,"data-citykey":citykey,"data-code":ap.code}));
 }
 for(const ap of AIRPORTS){
  const states=[ap.metroState, ap.placeState].filter((v,i,a)=>a.indexOf(v)===i).join(" ");
  const citykey=ap.metroState+"|"+ap.metroCity;
  const g=el("g",{class:"ap"+(ap.pets?"":" placeholder"),role:"button",tabindex:0,"data-code":ap.code,"data-states":states,"data-citykey":citykey,"aria-label":ap.code+", "+ap.metroCity});
  const mark=el("g",{class:"ap-mark"});
  mark.appendChild(el("rect",{class:"pad",x:-8,y:-8,width:16,height:16,rx:2,transform:"rotate(45)"}));
  mark.appendChild(el("path",{class:"glyph",d:PLANE,transform:"translate(-6.2,-6.2) scale(.52)"}));
  g.appendChild(mark);
  g.setAttribute("transform","translate("+ap.x+" "+ap.y+")");
  const ax=ap.ldx||0, ay=ap.ldy==null?16:ap.ldy, ta=ap.anchor||"middle";
  const chip=el("rect",{class:"ap-chip",x:(ax-10).toFixed(1),y:(ay-9).toFixed(1),width:20,height:12,rx:2.4});
  g.appendChild(chip);
  const tx=el("text",{x:ax,y:ay,"text-anchor":ta,class:"map-label"});
  tx.textContent=ap.code; g.appendChild(tx);
  if(ap.mapName){const t2=el("text",{x:ax,y:ay+14,"text-anchor":ta,class:"map-name"});t2.textContent=ap.mapName;g.appendChild(t2)}
  const tt=el("title",{}); tt.textContent=ap.code+" — "+ap.metroCity+" ("+ap.name+")"; g.appendChild(tt);
  g.setAttribute("aria-label",ap.code+", "+ap.name+", "+ap.metroCity);
  g.addEventListener("click",e=>{e.stopPropagation(); selectAirport(ap.code)});
  g.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault(); selectAirport(ap.code)}});
  ga.appendChild(g);
 }
}
/* One clinic per labeled map city. directory = data/usa_clinics_directory.json. */
const CLINICS={"AL|Birmingham":{"name":"New Kelley Animal Hospital","place":"Birmingham, AL","url":"https://newkelleyah.com/pet-health-certificates-birmingham-tarrant/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"AL|Montgomery":{"name":"Taylor Crossing Animal Hospital","place":"Montgomery, AL","url":"https://www.taylorcrossingvet.com/","tag":"off","source":"Official clinic site"},"AK|Anchorage":{"name":"Anchorage Pet Travel Certificates","place":"Anchorage, AK","url":"https://www.anchoragepettravelcertificates.com/our-services","tag":"off","source":"PetPolicyCheck USA clinics directory"},"AK|Juneau":{"name":"Juneau Veterinary Hospital","place":"Juneau, AK","url":"https://www.juneauvet.com/","tag":"off","source":"Official clinic site"},"AZ|Phoenix":{"name":"Alta Vista Veterinary Hospital","place":"Phoenix, AZ","url":"https://www.altavistavet.com/internationalhealthcertificate","tag":"off","source":"PetPolicyCheck USA clinics directory"},"AZ|Tucson":{"name":"VCA Animal Health Hospital","place":"Tucson, AZ","url":"https://vcahospitals.com/animal-health-hospital","tag":"off","source":"VCA hospital page"},"CO|Denver":{"name":"Denver Animal Hospital","place":"Denver, CO","url":"https://denveranimalhospital.org/","tag":"off","source":"Official clinic site"},"FL|Miami":{"name":"Doral Centre Animal Hospital","place":"Doral, FL (near Miami)","url":"https://doralvet.com/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"FL|Orlando":{"name":"East Orlando Animal Hospital","place":"Orlando, FL","url":"https://www.eastorlandovet.com/","tag":"off","source":"Official clinic site"},"FL|Tampa":{"name":"VCA Carrollwood Cat Hospital","place":"Tampa, FL","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Carrollwood%20Cat%20Hospital%2013305%20Orange%20Grove%20Drive%20Tampa%20FL","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"FL|Tallahassee":{"name":"Novey Animal Hospital","place":"Tallahassee, FL","url":"https://novey.com/","tag":"off","source":"Official clinic site"},"GA|Atlanta":{"name":"Beyond Pets Animal Hospital","place":"Atlanta, GA","url":"https://beyondpets.com/pet-services/usda-travel-certificates/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"GA|Savannah":{"name":"VCA Greater Savannah Animal Hospital","place":"Savannah, GA","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Greater%20Savannah%20Animal%20Hospital%201350%20E%20DeRenne%20Ave%20Savannah%20GA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"IN|Indianapolis":{"name":"VCA Beech Grove Animal Hospital","place":"Indianapolis, IN","url":"https://vcahospitals.com/beech-grove","tag":"off","source":"VCA hospital page"},"KS|Wichita":{"name":"Veterinary Emergency & Specialty Hospital of Wichita","place":"Wichita, KS","url":"https://www.vetwichita.com/","tag":"off","source":"Official clinic site"},"ME|Portland":{"name":"Brackett Street Veterinary Clinic","place":"Portland, ME","url":"https://brackettstveterinaryclinic.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"ME|Augusta":{"name":"Pine Tree Veterinary Hospital","place":"Augusta, ME","url":"https://www.pinetreevet.com/","tag":"off","source":"Official clinic site"},"MA|Boston":{"name":"Angell Animal Medical Center (MSPCA-Angell)","place":"Boston, MA","url":"https://www.mspca.org/veterinarycare/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"MN|Minneapolis":{"name":"VCA Cedar Animal Hospital","place":"Minneapolis, MN","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Cedar%20Animal%20Hospital%203604%20Cedar%20Avenue%20South%20Minneapolis%20MN","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"MN|Saint Paul":{"name":"University of Minnesota Veterinary Medical Center","place":"St. Paul, MN","url":"https://vmc.umn.edu/about/about-us","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NC|Charlotte":{"name":"VCA Stoney Creek Animal Hospital","place":"Charlotte, NC","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Stoney%20Creek%20Animal%20Hospital%20Charlotte%20NC","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"NC|Raleigh":{"name":"NC State Veterinary Hospital","place":"Raleigh, NC","url":"https://hospital.cvm.ncsu.edu/clients/emergency/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"ND|Fargo":{"name":"CareVet of West Fargo","place":"West Fargo, ND (near Fargo)","url":"https://www.carevet.com/west-fargo/health-certificates/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"OK|Oklahoma City":{"name":"Quail Creek Veterinary Clinic","place":"Oklahoma City, OK","url":"https://quailcreekvet.com/international-pet-travel-oklahoma-city-ok/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"OK|Tulsa":{"name":"VCA Woodland Central Animal Hospital","place":"Tulsa, OK","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Woodland%20Central%20Animal%20Hospital%205326%20E%20Skelly%20Drive%20Tulsa%20OK","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"PA|Philadelphia":{"name":"Penn Vet – Ryan Veterinary Hospital","place":"Philadelphia, PA","url":"https://www.vet.upenn.edu/ryan-hospital/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"PA|Pittsburgh":{"name":"Cheyenne Veterinary Wellness & Surgical Center","place":"Pittsburgh, PA","url":"https://www.cheyennevets.com/","tag":"off","source":"Official clinic site"},"PA|Harrisburg":{"name":"Colonial Park Animal Clinic","place":"Harrisburg, PA","url":"https://www.google.com/maps/search/?api=1&query=Colonial%20Park%20Animal%20Clinic%204905%20Jonestown%20Road%20Harrisburg%20PA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"SD|Sioux Falls":{"name":"Heather Ridge Pet Hospital","place":"Sioux Falls, SD","url":"https://www.heatherridgepet.com/services/domestic-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"TX|Houston":{"name":"Gulf Coast Veterinary Specialists (GCVS)","place":"Houston, TX","url":"https://www.gcvs.com/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"TX|Dallas":{"name":"VCA Preston Park Animal Hospital","place":"Dallas, TX","url":"https://vcahospitals.com/preston-park/services/primary-care/health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"TX|San Antonio":{"name":"VCA Becker Animal Hospital","place":"San Antonio, TX","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Becker%20Animal%20Hospital%206515%20I-10%20San%20Antonio%20TX","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"TX|Austin":{"name":"South Park Animal Hospital","place":"Austin, TX","url":"https://www.southparkaustin.com/services/international-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"CT|Hartford":{"name":"VCA Veterinary Specialists of CT","place":"West Hartford, CT (Hartford metro)","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Veterinary%20Specialists%20of%20CT%20993%20North%20Main%20Street%20West%20Hartford%20CT","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"MO|Kansas City":{"name":"VCA Welborn Animal Hospital","place":"Kansas City, KS (Kansas City metro)","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Welborn%20Animal%20Hospital%207860%20Washington%20Avenue%20Kansas%20City%20KS","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"MO|St. Louis":{"name":"Heritage Veterinary Hospital","place":"Creve Coeur (St. Louis), MO (near St. Louis)","url":"https://heritageveterinary.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"IL|Chicago":{"name":"MedVet Chicago","place":"Chicago, IL","url":"https://www.medvet.com/location/chicago/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NM|Albuquerque":{"name":"Manzano Animal Clinic","place":"Albuquerque, NM","url":"https://www.manzanoanimalclinic.com/services/international-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NM|Santa Fe":{"name":"VCA Arrighetti Animal Hospital","place":"Santa Fe, NM","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Arrighetti%20Animal%20Hospital%20Santa%20Fe%20NM","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"AR|Little Rock":{"name":"Hillcrest Animal Hospital","place":"Little Rock, AR","url":"https://www.hillcrestanimalhospital.org/services/international-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"CA|Los Angeles":{"name":"Beverly Robertson Veterinary Clinic","place":"Los Angeles, CA","url":"https://beverlyrobertsonvet.com/travel-and-health-certificate-for-dogs-and-cats/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"CA|San Diego":{"name":"Amici Pet Hospital","place":"San Diego, CA","url":"https://amicipethospital.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"CA|Sacramento":{"name":"VCA Sacramento Veterinary Referral Center","place":"Sacramento, CA","url":"https://vcahospitals.com/sacramento-veterinary-referral-center/hospital","tag":"off","source":"VCA hospital page"},"DE|Wilmington":{"name":"BluePearl Pet Hospital Christiana","place":"Newark, DE (serves Wilmington)","url":"https://bluepearlvet.com/hospital/christiana-de/","tag":"off","source":"Official hospital page; serves Wilmington"},"DE|Dover":{"name":"VCA Dover Animal Hospital","place":"Dover, DE","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Dover%20Animal%20Hospital%20201%20Towne%20Centre%20Drive%20Dover%20DE","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"DC|Washington, DC":{"name":"Friendship Hospital for Animals","place":"Washington, DC","url":"https://friendshiphospital.com/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"HI|Honolulu":{"name":"Ali'i Animal Hospital","place":"Honolulu, HI","url":"https://aliianimal.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"IA|Des Moines":{"name":"VCA Avondale Veterinary Hospital","place":"Des Moines, IA","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Avondale%20Veterinary%20Hospital%204318%20E%20Army%20Post%20Road%20Des%20Moines%20IA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"KY|Louisville":{"name":"Plantation Animal Clinic","place":"Louisville, KY","url":"https://plantationanimalclinic.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"MD|Annapolis":{"name":"Greater Annapolis Veterinary Hospital","place":"Annapolis, MD","url":"https://www.greaterannapolisveterinaryhospital.com/","tag":"off","source":"Official clinic site"},"MI|Lansing":{"name":"MSU Veterinary Medical Center","place":"East Lansing, MI (near Lansing)","url":"https://cvm.msu.edu/hospital","tag":"off","source":"PetPolicyCheck USA clinics directory"},"MT|Billings":{"name":"Caring Hands Veterinary","place":"Billings, MT","url":"https://www.caringhandsbillings.com/pet-travel/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NH|Concord":{"name":"VCA Russell Animal Hospital","place":"Concord, NH","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Russell%20Animal%20Hospital%20286B%20Pleasant%20Street%20Concord%20NH","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"NY|New York City":{"name":"The Animal Medical Center (AMC)","place":"New York, NY","url":"https://www.amcny.org/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NY|Buffalo":{"name":"VCA Sheridan Animal Hospital","place":"Buffalo, NY","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Sheridan%20Animal%20Hospital%202288%20Sheridan%20Drive%20Buffalo%20NY","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"OH|Columbus":{"name":"Ohio State Veterinary Medical Center","place":"Columbus, OH","url":"https://vmc.vet.osu.edu/about","tag":"off","source":"PetPolicyCheck USA clinics directory"},"OH|Cleveland":{"name":"MedVet Cleveland","place":"Cleveland, OH","url":"https://www.medvet.com/location/cleveland/","tag":"off","source":"Official clinic site"},"OH|Cincinnati":{"name":"VCA College Hill Animal Hospital","place":"Cincinnati, OH","url":"https://www.google.com/maps/search/?api=1&query=VCA%20College%20Hill%20Animal%20Hospital%20Cincinnati%20OH","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"OR|Portland":{"name":"DoveLewis Emergency Animal Hospital","place":"Portland, OR","url":"https://www.dovelewis.org/","tag":"off","source":"Official clinic site"},"OR|Salem":{"name":"VCA Salem Animal Hospital","place":"Salem, OR","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Salem%20Animal%20Hospital%204053%20Commercial%20Street%20SE%20Salem%20OR","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"TN|Nashville":{"name":"VCA Murphy Road Animal Hospital","place":"Nashville, TN","url":"https://vcahospitals.com/murphy-road","tag":"off","source":"VCA hospital page"},"TN|Memphis":{"name":"Shelby Center Veterinary","place":"Memphis, TN","url":"https://shelbycentervet.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"UT|Salt Lake City":{"name":"MedVet Northern Utah","place":"Sunset (Salt Lake metro), UT (near Salt Lake City)","url":"https://www.medvet.com/location/northern-utah/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"VA|Virginia Beach":{"name":"BluePearl Pet Hospital Town Center","place":"Virginia Beach, VA","url":"https://bluepearlvet.com/hospital/virginia-beach-va/","tag":"off","source":"Official hospital page"},"VA|Richmond":{"name":"VCA Pets First Animal Hospital","place":"Richmond, VA","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Pets%20First%20Animal%20Hospital%209201%20Staples%20Mill%20Road%20Richmond%20VA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"WA|Seattle":{"name":"The Family Pet","place":"Seattle, WA","url":"https://www.thefamilypet.org/services/health-certificates/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"WA|Spokane":{"name":"VCA Manito Animal Hospital","place":"Spokane, WA","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Manito%20Animal%20Hospital%202304%20E%2057th%20Avenue%20Spokane%20WA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"WI|Milwaukee":{"name":"VCA Milwaukee Emergency Center for Animals","place":"Greenfield, WI (Milwaukee metro)","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Milwaukee%20Emergency%20Center%20for%20Animals%203670%20South%20108th%20Street%20Greenfield%20WI","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"WI|Madison":{"name":"UW Veterinary Care","place":"Madison, WI","url":"https://uwveterinarycare.wisc.edu/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NE|Omaha":{"name":"Omaha Vets Group","place":"Omaha, NE","url":"https://omahavetsgroup.com/services/healthcertificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NE|Lincoln":{"name":"Nebraska Animal Medical Center","place":"Lincoln, NE","url":"https://www.namcvet.com/services/international-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"SC|Columbia":{"name":"Two Notch Road Animal Clinic","place":"Columbia, SC","url":"https://petfriendsvet.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"ID|Boise":{"name":"Foothills Veterinary Hospital","place":"Meridian, ID (near Boise)","url":"https://foothillsveterinary.com/services/health-certificates-usda-certified/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NV|Las Vegas":{"name":"Cheyenne Tonopah Animal Hospital","place":"Las Vegas, NV","url":"https://www.ctanimalhospital.com/services/domestic-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"VT|Burlington":{"name":"Dorset Street Animal Hospital","place":"South Burlington, VT (near Burlington)","url":"https://dorsetstreetanimalhospital.com/south-burlington-vt/international-health-certificates-for-pet-travel/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"LA|New Orleans":{"name":"Prytania Veterinary Hospital","place":"New Orleans, LA","url":"https://prytaniavet.com/service/international-health-certificates-new-orleans-la/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"LA|Baton Rouge":{"name":"LSU Veterinary Teaching Hospital","place":"Baton Rouge, LA","url":"https://www.lsu.edu/vetmed/veterinary_hospital/index.php","tag":"off","source":"PetPolicyCheck USA clinics directory"},"RI|Providence":{"name":"VCA Povar Animal Hospital","place":"East Providence, RI (Providence metro)","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Povar%20Animal%20Hospital%2015%201st%20Street%20East%20Providence%20RI","tag":"srch","source":"Named on an official clinic directory; Google Maps search"}};

/* ---------- panel ---------- */
let step=1,cur=null;
function header(a,title,sub){const P=window.PPC_PST?PPC_PST("map","pst-ph"):"";return `<div class="ph theme-map">${mark(a)}<div><div class="ph-eye">${P}<span>USA map · state panel</span></div><h2>${esc(title)}</h2><div class="sub">${sub}</div></div></div>`}
function ruleKind(a){
 const r=RULES[a];
 if(r&&r.differs) return "<b style='color:#f0d58c'>Special entry rules</b>";
 if(r&&!r.verified) return "";
 return "State entry rules";
}
function clinicCard(state, city){
 const c=CLINICS[state+"|"+city];
 const dir=lk("📋","USA clinics directory","Informational list, not a partnership",siteUrl("/clinics/usa.html"),"off").replace("Official","Site");
 if(!c) return `<h4>Clinic for ${esc(city)}</h4><div class="links">${dir}${lk("🏛","USDA Vet Finder","Search USDA-accredited veterinarians","https://usdavetfinder.com/","off")}</div>`;
 return `<h4>Clinic for ${esc(city)}</h4><div class="links">${lk("🩺",c.name,c.place+" · "+c.source,c.url,c.tag)}${dir}</div><p class="disc">One clinic for this city. Informational only, not a partner. Confirm services, USDA accreditation and fees with the clinic.</p>`;
}
function clinicsForState(a){
 const p=a+"|";
 return Object.keys(CLINICS).filter(k=>k.startsWith(p)).sort((x,y)=>x.localeCompare(y)).map(k=>({city:k.slice(p.length),c:CLINICS[k]}));
}
function stateClinics(a){
 const list=clinicsForState(a);
 const dir=lk("📋","USA clinics directory","Informational list, not a partnership",siteUrl("/clinics/usa.html"),"off").replace("Official","Site");
 const usda=lk("🏛","USDA Vet Finder","Search USDA-accredited veterinarians","https://usdavetfinder.com/","off");
 const hi=a==="HI"?`<p class="disc">Hawaii trips also need the FAVN rabies test and the quarantine steps above.</p>`:"";
 if(!list.length) return `<h4>Clinics in this state</h4><div class="stubbox"><b>No clinic listed for this state yet.</b> Use the directory or the USDA accredited-vet search, then confirm with the clinic.</div>${hi}<div class="links">${dir}${usda}</div>`;
 return `<h4>Clinics in this state (${list.length})</h4>${hi}<div class="links">${list.map(({c})=>lk("🩺",c.name,c.place+" · "+c.source,c.url,c.tag)).join("")}${dir}${usda}</div><p class="disc">One clinic per listed city. Informational only, not a partner. Confirm services, USDA accreditation and fees with the clinic.</p>`;
}
function lawSection(a,compact,cityName,clinicState){
 const r=RULES[a], nm=a==="DC"?"District of Columbia":GEO[a].name;
 let s=`<section class="sec" data-sec="1"><h3><span class="n">1</span>Vet + laws</h3><h4>${esc(nm)} entry rules</h4>`;
 if(r){
  s+=`<dl class="kv"><dt>Health certificate</dt><dd>${esc(r.cvi)}</dd><dt>Rabies</dt><dd>${esc(r.rabies)}</dd></dl><p>${esc(r.notes)}</p>`+lk("📜",nm+": official entry requirements","Checked Oct 23, 2026 (live usa.html table)",r.src,"off");
 }
 s+=`<details class="fd"${compact?"":" open"}><summary>Federal rules (apply in every state)</summary><div class="links">${fed("aphisSS")}${fed("cdc","🐕")}${fed("aphisIn")}${fed("aphisOut")}</div><p class="disc">Same CDC and USDA pages as <a href="usa.html#federal">the USA federal table</a>. State rules still decide travel between states.</p></details>`;
 s+=`<h4>Sanitary / vet visit</h4><p>Airlines may ask for a health and acclimation certificate signed by a licensed vet within 10 days. Book a USDA-accredited vet for the CVI and rabies certificate; keep paper and photo copies.</p>`;
 if(cityName) s+=clinicCard(clinicState||a, cityName);
 else s+=stateClinics(a);
 return s+`</section>`;
}
function roadSection(a,city){
 let s=`<section class="sec" data-sec="2"><h3><span class="n">2</span>Road / rail</h3>`;
 if(!city){s+=`<h4>Rides</h4><div class="links">${RIDES}</div><h4>Rail and bus</h4><p>${AMTRAK_NOTE}</p><div class="links">${lk("🚆","Amtrak: Pets on trains","Rules + pet reservation","https://www.amtrak.com/pets","off")}${lk("🚌","Greyhound / FlixBus","Service animals only, no pets (carrier policy; verify)","https://www.greyhound.com/","off")}</div><p class="disc">Pick a gold city for local taxis, transit and stations.</p>`}
 else s+=city;
 return s+`</section>`;
}
function airFedLinks(){
 return lk("🧳","Airline pet policies","Cabin, fees, hold","../#compare","off").replace("Official","Site").replace(' target="_blank"','')
  +lk("🇺🇸","PetPolicyCheck: USA pet travel guide","Full federal and state table (source for this map)",siteUrl("/countries/usa.html"),"off").replace("Official","Site")
  +fed("aphisAir")+fed("cdc","🐕")+fed("dot","🦮");
}
function planeSection(a, cityName){
 const list=airportsFor(a, cityName||null);
 const nm=cityName||(a==="DC"?"Washington, DC":(GEO[a]?GEO[a].name:a));
 let s=`<section class="sec" data-sec="3"><h3><span class="n">3</span>Plane</h3><p>Book your pet's in-cabin or cargo spot directly with the airline (pet space per flight is limited). Many airlines ask for a health certificate issued within 10 days.</p>`;
 if(list.length){
  s+=`<h4>${cityName?`Airports serving ${esc(cityName)}`:"Airports on this map"}</h4><div class="citylist">${list.map(ap=>`<button type="button" class="apbtn${ap.pets?"":" placeholder"}" data-ap="${esc(ap.code)}" aria-label="${esc(ap.code)}, ${esc(ap.metroCity)}">${esc(ap.code)} — ${esc(ap.metroCity)}</button>`).join("")}</div>`;
  s+=`<p class="disc">Open an airport for its relief page. The dashed line on the map ties it to ${cityName?esc(cityName):"its city"}.</p>`;
 }
 s+=`<div class="links">${airFedLinks()}</div>`;
 if(list.length && !cityName) s+=`<p class="disc">Only mapped airports are listed.</p>`;
 return s+`</section>`;
}
function transconUiLang(){
 const path=location.pathname||'';
 const pm=path.match(/^\/(es|fr|de|it|ja|ko)(\/|$)/);
 if(pm) return pm[1];
 const raw=((document.documentElement.lang||'')+' '+(document.documentElement.getAttribute('data-lang')||'')).toLowerCase();
 const lm=raw.match(/\b(es|fr|de|it|ja|ko)\b/);
 if(lm) return lm[1];
 try{ const stored=localStorage.getItem('ppc_lang')||''; if(/^(es|fr|de|it|ja|ko)$/.test(stored)) return stored; }catch(_){}
 return 'en';
}
/* Partner pet-mover pages for SFO, LAX and JFK only. URLs checked 12 Nov 2026 (KST). No EWR link. */
const TRANSCON={
 SFO:{url:"https://transconpet.com/san-francisco-pet-shipping-services/", title:"Pet mover: Transcon Pet Movers", sub:"San Francisco office"},
 LAX:{url:"https://transconpet.com/los-angeles-pet-shipping/", title:"Pet mover: Transcon Pet Movers", sub:"Los Angeles office"},
 JFK:{url:"https://transconpet.com/new-york-pet-shipping/", title:"Pet mover: Transcon Pet Movers", sub:"New York service"}
};
function transconLink(ap){
 const t=TRANSCON[ap.code];
 if(!t) return "";
 const en=transconUiLang()==='en';
 const title=en?t.title:"Transcon Pet Movers";
 const sub=en?(t.sub||""):"";
 const logoHref="https://transconpet.com/?utm_source=petpolicycheck&utm_medium=referral&utm_campaign=partner_listing&utm_content=logo";
 const src="/assets/partners/transcontinental-pet-movers";
 return `<div class="lk transcon-link" data-partner="transconpet"><a class="transcon-logo-link" href="${esc(logoHref)}" target="_blank" rel="sponsored noopener"><picture><source type="image/webp" srcset="${src}.webp"><img src="${src}.png" width="48" height="48" alt="Transcontinental Pet Movers logo"></picture></a><a class="t" href="${esc(t.url)}" target="_blank" rel="sponsored noopener">${esc(title)}${sub?`<small>${esc(sub)}</small>`:""}</a></div>`;
}
function airportPlane(ap){
 const sibs=airportsFor(ap.metroState, ap.metroCity).filter(x=>x.code!==ap.code);
 let s=`<section class="sec" data-sec="3"><h3><span class="n">3</span>Plane</h3><h4>${esc(ap.code)} · ${esc(ap.name)}</h4><p>${esc(ap.code)} serves ${esc(ap.metroCity)}. Relief areas are the airport’s; the airline still sets cabin and cargo rules.</p><div class="links">`;
 s+=lk("🛫", ap.site[1], ap.name, ap.site[0], "off");
 if(ap.pets) s+=lk("🐾", ap.pets[1], ap.pets[2]||"Official pet or relief page", ap.pets[0], "off");
 s+=transconLink(ap);
 s+=airFedLinks()+`</div>`;
 if(ap.placeState!==ap.metroState) s+=`<p class="disc">${esc(ap.code)} is in ${esc(GEO[ap.placeState].name)}. Taxis and hotels continue on the ${esc(ap.metroCity)} panel.</p>`;
 if(sibs.length) s+=`<h4>Other airports for ${esc(ap.metroCity)}</h4><div class="citylist">${sibs.map(x=>`<button type="button" class="apbtn${x.pets?"":" placeholder"}" data-ap="${esc(x.code)}">${esc(x.code)} — ${esc(x.metroCity)}</button>`).join("")}</div>`;
 return s+`</section>`;
}
function airportRoad(ap){
 return `<section class="sec" data-sec="2"><h3><span class="n">2</span>Road / rail</h3><p>After landing, taxis, trains and hotels continue on the ${esc(ap.metroCity)} city panel.</p><div class="btnrow"><button type="button" class="btn ghost" data-s="${ap.metroState}" data-city="${esc(ap.metroCity)}">Open ${esc(ap.metroCity)}: taxis, rail, hotels</button></div><h4>Rides from the airport</h4><div class="links">${RIDES}</div></section>`;
}
function groomSection(){return window.PPC_GROOM?PPC_GROOM.section(cur):""}
function hotelSection(q,extra){
 return `<section class="sec" data-sec="4"><h3><span class="n">4</span>Hotel</h3><div class="links">${extra||""}${lk("📋","Hotel chains: pet fees & weight limits","PetPolicyCheck",siteUrl("/hotels/"),"off").replace('Official','Site')}</div></section>`;
}
function render(html){const p=$("#panel");p.innerHTML=html;p.scrollTop=0;applyStep(false);
 p.querySelectorAll("[data-city]").forEach(b=>b.onclick=()=>selectCity(b.dataset.s,b.dataset.city));
 p.querySelectorAll("[data-state]").forEach(b=>b.onclick=()=>selectState(b.dataset.state));
 p.querySelectorAll("[data-ap]").forEach(b=>b.onclick=()=>selectAirport(b.dataset.ap));
 if(innerWidth<=900&&cur)p.scrollIntoView({behavior:"smooth",block:"start"});
}
/* ---------- view box: zoomTo (state select on phones) + free zoom/pan (no d3) ---------- */
const FULL=[0,0,975,610],MAXZ=8,MINW=975/MAXZ;let vb=FULL.slice(),animId=0;
/* clamp: never wider than FULL, never closer than 8x, keep the 975:610 ratio, no panning into empty space */
