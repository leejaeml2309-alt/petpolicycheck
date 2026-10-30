/* USA pet-travel map behavior. GEO and USA_RULES are loaded first.
   Eight sample cities have booking links; every other city is an explicit placeholder. */
const GEO = window.GEO;
const RULES = window.USA_RULES;
const SITE="..";
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const enc=encodeURIComponent;
const ABBRS=Object.keys(GEO).filter(a=>a!=="DC").sort((a,b)=>GEO[a].name.localeCompare(GEO[b].name));
const TINY=["VT","NH","MA","RI","CT","NJ","DE","MD"];
/* ---------- links ---------- */
const TAG={aff:"Affiliate",off:"Official",srch:"Search",stub:"Stub"};
function lk(ic,title,sub,href,tag){return `<a class="lk" href="${esc(href)}" target="_blank" rel="${tag==='aff'?'sponsored nofollow noopener':'noopener'}"><span class="ic" aria-hidden="true">${ic}</span><span class="t">${esc(title)}${sub?`<small>${esc(sub)}</small>`:""}</span><span class="tag ${tag}">${TAG[tag]}</span></a>`}
const expHotels=(q)=>`https://www.expedia.com/Hotel-Search?destination=${enc(q)}&amenities=PETS`;
const bkgHotels=(q)=>`https://www.booking.com/searchresults.html?ss=${enc(q)}&nflt=hotelfacility%3D4`;
const FED={
 cdc:["https://www.cdc.gov/importation/dogs/index.html","CDC: Bringing a dog into the US","Dog Import Form + rules for dogs arriving from abroad"],
 aphisIn:["https://www.aphis.usda.gov/pet-travel/another-country-to-us-import","USDA APHIS: Bring a pet into the US","Cats, dogs and other pets entering from another country"],
 aphisSS:["https://www.aphis.usda.gov/pet-travel/state-to-state","USDA APHIS: State-to-state travel","No federal rule between states: the destination state decides"],
 aphisAir:["https://www.aphis.usda.gov/pet-travel/pets-on-planes/preparing-pets-air-travel","USDA APHIS: Preparing pets for air travel","Airlines may want a health certificate within 10 days"],
 aphisOut:["https://www.aphis.usda.gov/pet-travel/us-to-another-country-export","USDA APHIS: Take a pet from the US abroad","Export health certificates (endorsed by APHIS)"],
 dot:["https://www.transportation.gov/individuals/aviation-consumer-protection/service-animals","US DOT: Service animals on flights","Federal rule for service dogs in the cabin"],
};
const fed=(k,ic="🏛")=>lk(ic,FED[k][1],FED[k][2],FED[k][0],"off");
const RIDES=lk("🚗","Uber Pet","One pet per trip, surcharge in the upfront fare","https://help.uber.com/en/riders/article/pet-friendly-rides?nodeId=e4468070-c193-41cf-b792-fa66ecfb1163","off")+
 lk("🚙","Lyft Pet","One well-behaved animal; US only; extra fee","https://help.lyft.com/hc/en-us/all/articles/8559088908-Pet-rides-for-riders","off");
const AMTRAK_NOTE="Amtrak: dogs and cats, 20 lb max incl. carrier, trips up to 7 hours, Coach (+Acela Business); reserve the pet spot.";
/* ---------- 8 sample cities ---------- */
const SAMPLE={
 "NY|New York City":{q:"New York, NY",amtrak:["nyp","New York Penn Station (NYP)"],guide:"/hotels/pet-friendly-hotels-new-york.html",exp:"https://expedia.com/affiliate/XuC5FQA",
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
 "FL|Miami":{q:"Miami, FL",amtrak:["mia","Miami station (MIA)"],guide:"/hotels/pet-friendly-hotels-miami.html",exp:"https://expedia.com/affiliate/g3j20Y7",
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
/* Airports for the 8 sample metros, plus two placeholder hubs (SFO, DFW).
   metroCity/metroState is the booking panel. placeState is where the dot sits
   (EWR is in New Jersey and still belongs to New York City). pets:null = placeholder. */
const PLANE="M21 16v-2l-8-5V3.5a1.5 1.5 0 0 0-3 0V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5z";
const AIRPORTS=[
 {code:"LGA", name:"LaGuardia", metroCity:"New York City", metroState:"NY", placeState:"NY", x:912, y:184, ldx:8, ldy:3, anchor:"start",
  site:["https://www.laguardiaairport.com/","LaGuardia Airport official site"],
  pets:["https://www.laguardiaairport.com/explore-lga/services","LGA pet and service-animal relief","Listed with airport services"]},
 {code:"EWR", name:"Newark Liberty International", metroCity:"New York City", metroState:"NY", placeState:"NJ", localCity:"Newark", x:818, y:188, ldx:-8, ldy:3, anchor:"end",
  site:["https://www.newarkairport.com/","Newark Liberty official site"],
  pets:["https://www.newarkairport.com/explore-ewr/services","EWR pet and service-animal relief","Listed with airport services"]},
 {code:"JFK", name:"John F. Kennedy International", metroCity:"New York City", metroState:"NY", placeState:"NY", x:918, y:252, ldx:8, ldy:3, anchor:"start",
  site:["https://www.jfkairport.com/","JFK Airport official site"],
  pets:["https://www.jfkairport.com/explore-jfk/accessibility-services","JFK pet and service-animal relief","Same page cited on the New York hotel guide"]},
 {code:"LAX", name:"Los Angeles International", metroCity:"Los Angeles", metroState:"CA", placeState:"CA", x:68, y:378, ldx:-8, ldy:3, anchor:"end",
  site:["https://www.flylax.com/","LAX official site"],
  pets:["https://www.flylax.com/sites/lax/files/documents/LAX%20Pet%20Relief%20Locations.pdf","LAX animal relief stations map","Official LAX pet-relief map (PDF)"]},
 {code:"SFO", name:"San Francisco International", metroCity:"San Francisco", metroState:"CA", placeState:"CA", x:22, y:286, ldx:8, ldy:3, anchor:"start",
  site:["https://www.flysfo.com/","SFO official site"], pets:null},
 {code:"ORD", name:"O'Hare International", metroCity:"Chicago", metroState:"IL", placeState:"IL", x:616, y:206, ldx:0, ldy:-12, anchor:"middle",
  site:["https://www.flychicago.com/ohare/home/pages/default.aspx","O'Hare official site"],
  pets:["https://www.flychicago.com/ohare/ServicesAmenities/accessibility/Pages/Terminal-Accessibility.aspx","O'Hare service-animal relief areas","On the O'Hare accessibility page"]},
 {code:"MDW", name:"Midway International", metroCity:"Chicago", metroState:"IL", placeState:"IL", x:622, y:246, ldx:-8, ldy:3, anchor:"end",
  site:["https://www.flychicago.com/midway/home/pages/default.aspx","Midway official site"],
  pets:["https://www.flychicago.com/midway/ServicesAmenities/accessibility/Pages/Terminal-Accessibility.aspx","Midway service-animal relief area","On the Midway accessibility page"]},
 {code:"MIA", name:"Miami International", metroCity:"Miami", metroState:"FL", placeState:"FL", x:798, y:558, ldx:-8, ldy:3, anchor:"end",
  site:["https://www.miami-airport.com/","Miami International official site"],
  pets:["https://www.miami-airport.com/map-animal-relief-areas.asp","MIA animal relief areas","Same page cited on the Miami hotel guide"]},
 {code:"IAH", name:"George Bush Intercontinental", metroCity:"Houston", metroState:"TX", placeState:"TX", x:496, y:486, ldx:0, ldy:-12, anchor:"middle",
  site:["https://www.fly2houston.com/iah/","IAH official site"],
  pets:["https://www.fly2houston.com/iah/accessibility/travelingwithpets/","IAH traveling with pets","Houston Airport System pet-relief page"]},
 {code:"HOU", name:"William P. Hobby", metroCity:"Houston", metroState:"TX", placeState:"TX", x:528, y:526, ldx:8, ldy:3, anchor:"start",
  site:["https://www.fly2houston.com/hou/","Hobby Airport official site"],
  pets:["https://www.fly2houston.com/hou/visitor-information/hou-travel-with-pets/","Hobby traveling with pets","Houston Airport System pet-relief page"]},
 {code:"DFW", name:"Dallas/Fort Worth International", metroCity:"Dallas", metroState:"TX", placeState:"TX", x:464, y:422, ldx:-8, ldy:3, anchor:"end",
  site:["https://www.dfwairport.com/","DFW official site"], pets:null},
 {code:"SEA", name:"Seattle-Tacoma International", metroCity:"Seattle", metroState:"WA", placeState:"WA", x:140, y:92, ldx:8, ldy:3, anchor:"start",
  site:["https://www.flysea.org/","SEA official site"],
  pets:["https://www.portseattle.org/services-amenities/traveling-pets","SEA traveling with pets","Port of Seattle pet-relief page"]},
 {code:"DEN", name:"Denver International", metroCity:"Denver", metroState:"CO", placeState:"CO", x:372, y:262, ldx:8, ldy:3, anchor:"start",
  site:["https://www.flydenver.com/","DEN official site"],
  pets:["https://www.flydenver.com/at-the-airport/services-and-amenities/traveling-with-pets/","DEN traveling with pets","Denver International pet-relief page"]},
 {code:"ATL", name:"Hartsfield-Jackson Atlanta International", metroCity:"Atlanta", metroState:"GA", placeState:"GA", x:706, y:430, ldx:0, ldy:16, anchor:"middle",
  site:["https://www.atl.com/","ATL official site"],
  pets:["https://www.atl.com/atls-relief-areas-provide-haven-for-service-animals-passenger-pets/","ATL pet relief areas","Hartsfield-Jackson official page"]},
];
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
function buildMap(){
 const gs=$("#g-st"),gl=$("#g-lb"),gc=$("#g-ct");
 for(const a of Object.keys(GEO)){
  const s=GEO[a];
  const special=!!(RULES[a]&&RULES[a].differs), unver=!!(RULES[a]&&!RULES[a].verified);
  const p=el("path",{d:s.d,class:"st"+(special?" rule":""),id:"s-"+a,tabindex:a==="DC"?-1:0,role:"button","aria-label":s.name+(special?" (special entry rules)":"")+(unver?" (placeholder, confirm with the state veterinarian)":"")});
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
  const t=el("text",{x,y,class:"lbl",id:"l-"+a});t.textContent=a;gl.appendChild(t);
 }
 for(const t of tiny){
  const ly=t.ly+shift, lx=948;
  gl.appendChild(el("line",{x1:t.x,y1:t.y,x2:lx-14,y2:ly,stroke:"#3a5a56","stroke-width":.8}));
  const g=el("g",{class:"ct",role:"button",tabindex:0,"aria-label":GEO[t.a].name});
  const r=el("rect",{x:lx-13,y:ly-8,width:26,height:16,rx:8,fill:"#16302f",stroke:"#3a5a56",id:"cb-"+t.a});
  const tx=el("text",{x:lx,y:ly,class:"lbl",id:"l-"+t.a});tx.textContent=t.a;
  g.append(r,tx);g.addEventListener("click",()=>selectState(t.a));
  g.addEventListener("keydown",e=>{if(e.key==="Enter"){selectState(t.a)}});gl.appendChild(g);
 }
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
  g.appendChild(el("rect",{class:"pad",x:-8,y:-8,width:16,height:16,rx:2,transform:"rotate(45)"}));
  g.appendChild(el("path",{class:"glyph",d:PLANE,transform:"translate(-6.2,-6.2) scale(.52)"}));
  g.setAttribute("transform","translate("+ap.x+" "+ap.y+")");
  const tx=el("text",{x:ap.ldx||0,y:ap.ldy==null?14:ap.ldy,"text-anchor":ap.anchor||"middle"});
  tx.textContent=ap.code; g.appendChild(tx);
  const tt=el("title",{}); tt.textContent=ap.code+" — "+ap.metroCity+" ("+ap.name+")"; g.appendChild(tt);
  g.addEventListener("click",e=>{e.stopPropagation(); selectAirport(ap.code)});
  g.addEventListener("keydown",e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault(); selectAirport(ap.code)}});
  ga.appendChild(g);
 }
}
/* One clinic per labeled map city. directory = data/usa_clinics_directory.json. */
const CLINICS={"AL|Birmingham":{"name":"New Kelley Animal Hospital","place":"Birmingham, AL","url":"https://newkelleyah.com/pet-health-certificates-birmingham-tarrant/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"AL|Montgomery":{"name":"Taylor Crossing Animal Hospital","place":"Montgomery, AL","url":"https://www.taylorcrossingvet.com/","tag":"off","source":"Official clinic site"},"AK|Anchorage":{"name":"Anchorage Pet Travel Certificates","place":"Anchorage, AK","url":"https://www.anchoragepettravelcertificates.com/our-services","tag":"off","source":"PetPolicyCheck USA clinics directory"},"AK|Juneau":{"name":"Juneau Veterinary Hospital","place":"Juneau, AK","url":"https://www.juneauvet.com/","tag":"off","source":"Official clinic site"},"AZ|Phoenix":{"name":"Alta Vista Veterinary Hospital","place":"Phoenix, AZ","url":"https://www.altavistavet.com/internationalhealthcertificate","tag":"off","source":"PetPolicyCheck USA clinics directory"},"AZ|Tucson":{"name":"VCA Animal Health Hospital","place":"Tucson, AZ","url":"https://vcahospitals.com/animal-health-hospital","tag":"off","source":"VCA hospital page"},"CO|Denver":{"name":"Denver Animal Hospital","place":"Denver, CO","url":"https://denveranimalhospital.org/","tag":"off","source":"Official clinic site"},"FL|Miami":{"name":"Doral Centre Animal Hospital","place":"Doral, FL (near Miami)","url":"https://doralvet.com/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"FL|Orlando":{"name":"East Orlando Animal Hospital","place":"Orlando, FL","url":"https://www.eastorlandovet.com/","tag":"off","source":"Official clinic site"},"FL|Tampa":{"name":"VCA Carrollwood Cat Hospital","place":"Tampa, FL","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Carrollwood%20Cat%20Hospital%2013305%20Orange%20Grove%20Drive%20Tampa%20FL","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"FL|Tallahassee":{"name":"Novey Animal Hospital","place":"Tallahassee, FL","url":"https://novey.com/","tag":"off","source":"Official clinic site"},"GA|Atlanta":{"name":"Beyond Pets Animal Hospital","place":"Atlanta, GA","url":"https://beyondpets.com/pet-services/usda-travel-certificates/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"GA|Savannah":{"name":"VCA Greater Savannah Animal Hospital","place":"Savannah, GA","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Greater%20Savannah%20Animal%20Hospital%201350%20E%20DeRenne%20Ave%20Savannah%20GA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"IN|Indianapolis":{"name":"VCA Beech Grove Animal Hospital","place":"Indianapolis, IN","url":"https://vcahospitals.com/beech-grove","tag":"off","source":"VCA hospital page"},"KS|Wichita":{"name":"Veterinary Emergency & Specialty Hospital of Wichita","place":"Wichita, KS","url":"https://www.vetwichita.com/","tag":"off","source":"Official clinic site"},"ME|Portland":{"name":"Brackett Street Veterinary Clinic","place":"Portland, ME","url":"https://brackettstveterinaryclinic.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"ME|Augusta":{"name":"Pine Tree Veterinary Hospital","place":"Augusta, ME","url":"https://www.pinetreevet.com/","tag":"off","source":"Official clinic site"},"MA|Boston":{"name":"Angell Animal Medical Center (MSPCA-Angell)","place":"Boston, MA","url":"https://www.mspca.org/veterinarycare/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"MN|Minneapolis":{"name":"VCA Cedar Animal Hospital","place":"Minneapolis, MN","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Cedar%20Animal%20Hospital%203604%20Cedar%20Avenue%20South%20Minneapolis%20MN","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"MN|Saint Paul":{"name":"University of Minnesota Veterinary Medical Center","place":"St. Paul, MN","url":"https://vmc.umn.edu/about/about-us","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NC|Charlotte":{"name":"VCA Stoney Creek Animal Hospital","place":"Charlotte, NC","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Stoney%20Creek%20Animal%20Hospital%20Charlotte%20NC","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"NC|Raleigh":{"name":"NC State Veterinary Hospital","place":"Raleigh, NC","url":"https://hospital.cvm.ncsu.edu/clients/emergency/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"ND|Fargo":{"name":"CareVet of West Fargo","place":"West Fargo, ND (near Fargo)","url":"https://www.carevet.com/west-fargo/health-certificates/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"OK|Oklahoma City":{"name":"Quail Creek Veterinary Clinic","place":"Oklahoma City, OK","url":"https://quailcreekvet.com/international-pet-travel-oklahoma-city-ok/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"OK|Tulsa":{"name":"VCA Woodland Central Animal Hospital","place":"Tulsa, OK","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Woodland%20Central%20Animal%20Hospital%205326%20E%20Skelly%20Drive%20Tulsa%20OK","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"PA|Philadelphia":{"name":"Penn Vet – Ryan Veterinary Hospital","place":"Philadelphia, PA","url":"https://www.vet.upenn.edu/ryan-hospital/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"PA|Pittsburgh":{"name":"Cheyenne Veterinary Wellness & Surgical Center","place":"Pittsburgh, PA","url":"https://www.cheyennevets.com/","tag":"off","source":"Official clinic site"},"PA|Harrisburg":{"name":"Colonial Park Animal Clinic","place":"Harrisburg, PA","url":"https://www.google.com/maps/search/?api=1&query=Colonial%20Park%20Animal%20Clinic%204905%20Jonestown%20Road%20Harrisburg%20PA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"SD|Sioux Falls":{"name":"Heather Ridge Pet Hospital","place":"Sioux Falls, SD","url":"https://www.heatherridgepet.com/services/domestic-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"TX|Houston":{"name":"Gulf Coast Veterinary Specialists (GCVS)","place":"Houston, TX","url":"https://www.gcvs.com/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"TX|Dallas":{"name":"VCA Preston Park Animal Hospital","place":"Dallas, TX","url":"https://vcahospitals.com/preston-park/services/primary-care/health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"TX|San Antonio":{"name":"VCA Becker Animal Hospital","place":"San Antonio, TX","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Becker%20Animal%20Hospital%206515%20I-10%20San%20Antonio%20TX","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"TX|Austin":{"name":"South Park Animal Hospital","place":"Austin, TX","url":"https://www.southparkaustin.com/services/international-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"CT|Hartford":{"name":"VCA Veterinary Specialists of CT","place":"West Hartford, CT (Hartford metro)","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Veterinary%20Specialists%20of%20CT%20993%20North%20Main%20Street%20West%20Hartford%20CT","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"MO|Kansas City":{"name":"VCA Welborn Animal Hospital","place":"Kansas City, KS (Kansas City metro)","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Welborn%20Animal%20Hospital%207860%20Washington%20Avenue%20Kansas%20City%20KS","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"MO|St. Louis":{"name":"Heritage Veterinary Hospital","place":"Creve Coeur (St. Louis), MO (near St. Louis)","url":"https://heritageveterinary.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"IL|Chicago":{"name":"MedVet Chicago","place":"Chicago, IL","url":"https://www.medvet.com/location/chicago/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NM|Albuquerque":{"name":"Manzano Animal Clinic","place":"Albuquerque, NM","url":"https://www.manzanoanimalclinic.com/services/international-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NM|Santa Fe":{"name":"VCA Arrighetti Animal Hospital","place":"Santa Fe, NM","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Arrighetti%20Animal%20Hospital%20Santa%20Fe%20NM","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"AR|Little Rock":{"name":"Hillcrest Animal Hospital","place":"Little Rock, AR","url":"https://www.hillcrestanimalhospital.org/services/international-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"CA|Los Angeles":{"name":"Beverly Robertson Veterinary Clinic","place":"Los Angeles, CA","url":"https://beverlyrobertsonvet.com/travel-and-health-certificate-for-dogs-and-cats/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"CA|San Francisco":{"name":"San Francisco SPCA – Veterinary Hospital","place":"San Francisco, CA","url":"https://www.sfspca.org/veterinary-care/hospital/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"CA|San Diego":{"name":"Amici Pet Hospital","place":"San Diego, CA","url":"https://amicipethospital.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"CA|Sacramento":{"name":"VCA Sacramento Veterinary Referral Center","place":"Sacramento, CA","url":"https://vcahospitals.com/sacramento-veterinary-referral-center/hospital","tag":"off","source":"VCA hospital page"},"DE|Wilmington":{"name":"BluePearl Pet Hospital Christiana","place":"Newark, DE (serves Wilmington)","url":"https://bluepearlvet.com/hospital/christiana-de/","tag":"off","source":"Official hospital page; serves Wilmington"},"DE|Dover":{"name":"VCA Dover Animal Hospital","place":"Dover, DE","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Dover%20Animal%20Hospital%20201%20Towne%20Centre%20Drive%20Dover%20DE","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"DC|Washington, DC":{"name":"Friendship Hospital for Animals","place":"Washington, DC","url":"https://friendshiphospital.com/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"HI|Honolulu":{"name":"Ali'i Animal Hospital","place":"Honolulu, HI","url":"https://aliianimal.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"IA|Des Moines":{"name":"VCA Avondale Veterinary Hospital","place":"Des Moines, IA","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Avondale%20Veterinary%20Hospital%204318%20E%20Army%20Post%20Road%20Des%20Moines%20IA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"KY|Louisville":{"name":"Plantation Animal Clinic","place":"Louisville, KY","url":"https://plantationanimalclinic.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"MD|Annapolis":{"name":"Greater Annapolis Veterinary Hospital","place":"Annapolis, MD","url":"https://www.greaterannapolisveterinaryhospital.com/","tag":"off","source":"Official clinic site"},"MI|Lansing":{"name":"MSU Veterinary Medical Center","place":"East Lansing, MI (near Lansing)","url":"https://cvm.msu.edu/hospital","tag":"off","source":"PetPolicyCheck USA clinics directory"},"MT|Billings":{"name":"Caring Hands Veterinary","place":"Billings, MT","url":"https://www.caringhandsbillings.com/pet-travel/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NH|Concord":{"name":"VCA Russell Animal Hospital","place":"Concord, NH","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Russell%20Animal%20Hospital%20286B%20Pleasant%20Street%20Concord%20NH","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"NY|New York City":{"name":"The Animal Medical Center (AMC)","place":"New York, NY","url":"https://www.amcny.org/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NY|Buffalo":{"name":"VCA Sheridan Animal Hospital","place":"Buffalo, NY","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Sheridan%20Animal%20Hospital%202288%20Sheridan%20Drive%20Buffalo%20NY","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"OH|Columbus":{"name":"Ohio State Veterinary Medical Center","place":"Columbus, OH","url":"https://vmc.vet.osu.edu/about","tag":"off","source":"PetPolicyCheck USA clinics directory"},"OH|Cleveland":{"name":"MedVet Cleveland","place":"Cleveland, OH","url":"https://www.medvet.com/location/cleveland/","tag":"off","source":"Official clinic site"},"OH|Cincinnati":{"name":"VCA College Hill Animal Hospital","place":"Cincinnati, OH","url":"https://www.google.com/maps/search/?api=1&query=VCA%20College%20Hill%20Animal%20Hospital%20Cincinnati%20OH","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"OR|Portland":{"name":"DoveLewis Emergency Animal Hospital","place":"Portland, OR","url":"https://www.dovelewis.org/","tag":"off","source":"Official clinic site"},"OR|Salem":{"name":"VCA Salem Animal Hospital","place":"Salem, OR","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Salem%20Animal%20Hospital%204053%20Commercial%20Street%20SE%20Salem%20OR","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"TN|Nashville":{"name":"VCA Murphy Road Animal Hospital","place":"Nashville, TN","url":"https://vcahospitals.com/murphy-road","tag":"off","source":"VCA hospital page"},"TN|Memphis":{"name":"Shelby Center Veterinary","place":"Memphis, TN","url":"https://shelbycentervet.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"UT|Salt Lake City":{"name":"MedVet Northern Utah","place":"Sunset (Salt Lake metro), UT (near Salt Lake City)","url":"https://www.medvet.com/location/northern-utah/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"VA|Virginia Beach":{"name":"BluePearl Pet Hospital Town Center","place":"Virginia Beach, VA","url":"https://bluepearlvet.com/hospital/virginia-beach-va/","tag":"off","source":"Official hospital page"},"VA|Richmond":{"name":"VCA Pets First Animal Hospital","place":"Richmond, VA","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Pets%20First%20Animal%20Hospital%209201%20Staples%20Mill%20Road%20Richmond%20VA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"WA|Seattle":{"name":"The Family Pet","place":"Seattle, WA","url":"https://www.thefamilypet.org/services/health-certificates/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"WA|Spokane":{"name":"VCA Manito Animal Hospital","place":"Spokane, WA","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Manito%20Animal%20Hospital%202304%20E%2057th%20Avenue%20Spokane%20WA","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"WI|Milwaukee":{"name":"VCA Milwaukee Emergency Center for Animals","place":"Greenfield, WI (Milwaukee metro)","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Milwaukee%20Emergency%20Center%20for%20Animals%203670%20South%20108th%20Street%20Greenfield%20WI","tag":"srch","source":"Named on an official clinic directory; Google Maps search"},"WI|Madison":{"name":"UW Veterinary Care","place":"Madison, WI","url":"https://uwveterinarycare.wisc.edu/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NE|Omaha":{"name":"Omaha Vets Group","place":"Omaha, NE","url":"https://omahavetsgroup.com/services/healthcertificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NE|Lincoln":{"name":"Nebraska Animal Medical Center","place":"Lincoln, NE","url":"https://www.namcvet.com/services/international-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"SC|Charleston":{"name":"All Creatures Animal Hospital","place":"Charleston, SC","url":"https://allcreatureschs.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"SC|Columbia":{"name":"Two Notch Road Animal Clinic","place":"Columbia, SC","url":"https://petfriendsvet.com/services/pet-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"ID|Boise":{"name":"Foothills Veterinary Hospital","place":"Meridian, ID (near Boise)","url":"https://foothillsveterinary.com/services/health-certificates-usda-certified/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"NV|Las Vegas":{"name":"Cheyenne Tonopah Animal Hospital","place":"Las Vegas, NV","url":"https://www.ctanimalhospital.com/services/domestic-health-certificates","tag":"off","source":"PetPolicyCheck USA clinics directory"},"VT|Burlington":{"name":"Dorset Street Animal Hospital","place":"South Burlington, VT (near Burlington)","url":"https://dorsetstreetanimalhospital.com/south-burlington-vt/international-health-certificates-for-pet-travel/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"LA|New Orleans":{"name":"Prytania Veterinary Hospital","place":"New Orleans, LA","url":"https://prytaniavet.com/service/international-health-certificates-new-orleans-la/","tag":"off","source":"PetPolicyCheck USA clinics directory"},"LA|Baton Rouge":{"name":"LSU Veterinary Teaching Hospital","place":"Baton Rouge, LA","url":"https://www.lsu.edu/vetmed/veterinary_hospital/index.php","tag":"off","source":"PetPolicyCheck USA clinics directory"},"RI|Providence":{"name":"VCA Povar Animal Hospital","place":"East Providence, RI (Providence metro)","url":"https://www.google.com/maps/search/?api=1&query=VCA%20Povar%20Animal%20Hospital%2015%201st%20Street%20East%20Providence%20RI","tag":"srch","source":"Named on an official clinic directory; Google Maps search"}};

/* ---------- panel ---------- */
let step=1,cur=null;
function header(a,title,sub){return `<div class="ph">${mark(a)}<div><h2>${esc(title)}</h2><div class="sub">${sub}</div></div></div>`}
function ruleKind(a){
 const r=RULES[a];
 if(r&&r.differs) return "<b style='color:#f0d58c'>Special entry rules</b>";
 if(r&&!r.verified) return "<b style='color:#f0a3a3'>Placeholder — confirm with the state vet</b>";
 return "State entry rules";
}
function clinicCard(state, city){
 const c=CLINICS[state+"|"+city];
 const dir=lk("📋","USA clinics directory","Informational list, not a partnership",SITE+"/clinics/usa.html","off").replace("Official","Site");
 if(!c) return `<h4>Clinic for ${esc(city)}</h4><div class="stubbox"><b>Placeholder:</b> no verified clinic for ${esc(city)} on this preview. Use the directory or the USDA accredited-vet search, then confirm with the clinic.</div><div class="links">${dir}${lk("🏛","USDA: find an accredited vet","Search by state and county","https://vsapps.aphis.usda.gov/vsps/public/VetSearch.do","off")}</div>`;
 return `<h4>Clinic for ${esc(city)}</h4><div class="links">${lk("🩺",c.name,c.place+" · "+c.source,c.url,c.tag)}${dir}</div><p class="disc">One clinic for this city. Informational only, not a partner. Confirm services, USDA accreditation and fees with the clinic.</p>`;
}
function lawSection(a,compact,cityName,clinicState){
 const r=RULES[a], nm=a==="DC"?"District of Columbia":GEO[a].name;
 let s=`<section class="sec" data-sec="1"><h3><span class="n">1</span>Vet + laws</h3><h4>${esc(nm)} entry rules</h4>`;
 if(r){
  s+=`<dl class="kv"><dt>Health certificate</dt><dd>${esc(r.cvi)}</dd><dt>Rabies</dt><dd>${esc(r.rabies)}</dd></dl><p>${esc(r.notes)}</p>`+lk("📜",nm+": official entry requirements","Checked Oct 23, 2026 (live usa.html table)",r.src,"off");
  if(!r.verified) s+=`<div class="stubbox"><b>Placeholder:</b> this row could not be confirmed on the official page. It matches the Check row on the live USA table. Confirm with the state veterinarian before you travel.</div>`;
 }else{
  s+=`<div class="stubbox"><b>Placeholder:</b> no published entry rule for ${esc(nm)} on this map yet. See the <a href="usa.html#states">USA rules table</a>.</div>`;
 }
 s+=`<details class="fd"${compact?"":" open"}><summary>Federal rules (apply in every state)</summary><div class="links">${fed("aphisSS")}${fed("cdc","🐕")}${fed("aphisIn")}${fed("aphisOut")}</div><p class="disc">Same CDC and USDA pages as <a href="usa.html#federal">the USA federal table</a>. State rules still decide travel between states.</p></details>`;
 s+=`<h4>Sanitary / vet visit</h4><p>Airlines may ask for a health and acclimation certificate signed by a licensed vet within 10 days. Book a USDA-accredited vet for the CVI and rabies certificate; keep paper and photo copies.</p>`;
 if(cityName) s+=clinicCard(clinicState||a, cityName);
 else s+=`<p class="disc">Open a city for its clinic.${a==="HI"?" Hawaii trips also need the FAVN and quarantine steps above.":""} A full clinic list for every town in the state is still a placeholder.</p><div class="links">${lk("🩺","PetPolicyCheck: USA pet-travel clinics","Directory of clinics that list health-certificate services",SITE+"/clinics/usa.html","off").replace("Official","Site")}${fed("aphisAir")}</div>`;
 return s+`</section>`;
}
function roadSection(a,city){
 let s=`<section class="sec" data-sec="2"><h3><span class="n">2</span>Road / rail</h3>`;
 if(!city){s+=`<h4>Rides</h4><div class="links">${RIDES}</div><h4>Rail and bus</h4><p>${AMTRAK_NOTE}</p><div class="links">${lk("🚆","Amtrak: Pets on trains","Rules + pet reservation","https://www.amtrak.com/pets","off")}${lk("🚌","Greyhound / FlixBus","Service animals only, no pets (carrier policy; verify)","https://www.greyhound.com/","off")}</div><p class="disc">Pick a gold city for local taxis, transit and stations.</p>`}
 else s+=city;
 return s+`</section>`;
}
function airFedLinks(){
 return lk("✈️","Search flights on Expedia","Then add the pet with the airline","https://expedia.com/affiliate/jnsZjjX","aff")
  +lk("🧳","Airline pet policies","Fees, carrier sizes, breed bans","../index.html#airlines","off").replace("Official","Site")
  +lk("🇺🇸","PetPolicyCheck: USA pet travel guide","Full federal and state table (source for this map)",SITE+"/countries/usa.html","off").replace("Official","Site")
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
 if(!list.length) s+=`<div class="stubbox"><b>Placeholder:</b> ${a==="HI"?"Honolulu (HNL) direct-release window and neighbor-island rules; ":""}airports in ${esc(nm)} are not on this preview map yet.</div>`;
 else if(!cityName) s+=`<p class="disc">Only mapped airports are listed. Any other airport in ${esc(nm)} is still a placeholder.</p>`;
 return s+`</section>`;
}
function airportPlane(ap){
 const sibs=airportsFor(ap.metroState, ap.metroCity).filter(x=>x.code!==ap.code);
 let s=`<section class="sec" data-sec="3"><h3><span class="n">3</span>Plane</h3><h4>${esc(ap.code)} · ${esc(ap.name)}</h4><p>${esc(ap.code)} serves ${esc(ap.metroCity)}. Relief areas are the airport’s; the airline still sets cabin and cargo rules.</p><div class="links">`;
 s+=lk("🛫", ap.site[1], ap.name, ap.site[0], "off");
 if(ap.pets) s+=lk("🐾", ap.pets[1], ap.pets[2]||"Official pet or relief page", ap.pets[0], "off");
 else s+=`</div><div class="stubbox"><b>Placeholder:</b> a pet-relief or traveling-with-pets page for ${esc(ap.code)} is not verified on this preview. Use the official airport site and confirm before you fly.</div><div class="links">`;
 s+=airFedLinks()+`</div>`;
 if(ap.placeState!==ap.metroState) s+=`<p class="disc">${esc(ap.code)} is in ${esc(GEO[ap.placeState].name)}. Taxis and hotels continue on the ${esc(ap.metroCity)} panel.</p>`;
 if(sibs.length) s+=`<h4>Other airports for ${esc(ap.metroCity)}</h4><div class="citylist">${sibs.map(x=>`<button type="button" class="apbtn${x.pets?"":" placeholder"}" data-ap="${esc(x.code)}">${esc(x.code)} — ${esc(x.metroCity)}</button>`).join("")}</div>`;
 return s+`</section>`;
}
function airportRoad(ap){
 return `<section class="sec" data-sec="2"><h3><span class="n">2</span>Road / rail</h3><p>After landing, taxis, trains and hotels continue on the ${esc(ap.metroCity)} city panel.</p><div class="btnrow"><button type="button" class="btn ghost" data-s="${ap.metroState}" data-city="${esc(ap.metroCity)}">Open ${esc(ap.metroCity)}: taxis, rail, hotels</button></div><h4>Rides from the airport</h4><div class="links">${RIDES}</div></section>`;
}
function hotelSection(q,extra){
 return `<section class="sec" data-sec="4"><h3><span class="n">4</span>Hotel</h3><div class="links">${extra||""}${lk("🏨","Pet-friendly hotels on Expedia",q+" · pets-allowed filter",expHotels(q),"srch")}${lk("🛏","Pet-friendly stays on Booking.com",q+" · pets-allowed filter",bkgHotels(q),"srch")}${lk("📋","Hotel chains: pet fees & weight limits","PetPolicyCheck",SITE+"/hotels/","off").replace('Official','Site')}</div><p class="disc">“Search” links are plain search URLs: swap for affiliate deep links before publish. “Affiliate” links may earn a commission at no extra cost to you.</p></section>`;
}
function render(html){const p=$("#panel");p.innerHTML=html;p.scrollTop=0;applyStep(false);
 p.querySelectorAll("[data-city]").forEach(b=>b.onclick=()=>selectCity(b.dataset.s,b.dataset.city));
 p.querySelectorAll("[data-state]").forEach(b=>b.onclick=()=>selectState(b.dataset.state));
 p.querySelectorAll("[data-ap]").forEach(b=>b.onclick=()=>selectAirport(b.dataset.ap));
 if(innerWidth<=900&&cur)p.scrollIntoView({behavior:"smooth",block:"start"});
}
const FULL=[0,0,975,610];let vb=FULL.slice();
function zoomTo(a){const m=$("#map");let t=FULL;
 if(a&&innerWidth<=900){const b=$("#s-"+a).getBBox();const w=Math.max(b.width*1.5,220),h=Math.max(b.height*1.5,150);const sc=Math.max(w/975,h/610);const W=975*sc,H=610*sc;t=[b.x+b.width/2-W/2,b.y+b.height/2-H/2,W,H];}
 $("#reset").hidden=t===FULL;const f=vb.slice(),t0=performance.now();
 (function an(n){const k=Math.min(1,(n-t0)/350),e=k*(2-k);vb=f.map((v,i)=>v+(t[i]-v)*e);m.setAttribute("viewBox",vb.join(" "));m.style.setProperty("--k",(vb[2]/975).toFixed(3));if(k<1)requestAnimationFrame(an)})(t0);}
function hilite(a,key,apCode){zoomTo(a&&a!=="DC"?a:null);
 document.querySelectorAll(".st.sel,.lbl.sel,.ct.sel,.ap.sel").forEach(e=>e.classList.remove("sel"));
 document.querySelectorAll("#grid button.sel").forEach(e=>e.classList.remove("sel"));
 document.querySelectorAll(".ct[data-s]").forEach(e=>{if(!e.classList.contains("sample"))e.classList.toggle("hide-lbl",e.dataset.s!==a)});
 TINY.forEach(t=>{const r=$("#cb-"+t);r&&r.setAttribute("fill",t===a?"#6d5a2c":"#16302f")});
 if(a){$("#s-"+a)?.classList.add("sel");$("#l-"+a)?.classList.add("sel");document.querySelector(`#grid button[data-a="${a}"]`)?.classList.add("sel")}
 if(key)document.querySelector(`.ct[data-k="${CSS.escape(key)}"]`)?.classList.add("sel");
 document.querySelectorAll(".ap,.ap-link").forEach(el=>{
  const mine=!a || (el.dataset.states||"").split(" ").includes(a);
  el.classList.toggle("dim", !!a && !mine);
  const cityHot=!!(key && el.dataset.citykey===key);
  const stateHot=!!a && !key && mine;
  el.classList.toggle("hot", cityHot || stateHot);
 });
 if(apCode) document.querySelector(`.ap[data-code="${CSS.escape(apCode)}"]`)?.classList.add("sel");
 $("#pick").value=a&&a!=="DC"?a:"";
}
function cityButtons(a){return `<div class="citylist">${GEO[a].cities.map(c=>`<button data-s="${a}" data-city="${esc(c.n)}" class="${SAMPLE[a+'|'+c.n]?'sample':''}">${esc(c.n)}${c.cap?" ★cap":""}</button>`).join("").replace(/ ★cap/g," (capital)")}</div>`}
function setHash(a,n){
 const h=n?a+"/"+encodeURIComponent(n):a;
 if(decodeURIComponent(location.hash.replace(/^#/,""))!== (n?a+"/"+n:a)) history.replaceState(null,"","#"+h);
}
function selectState(a){
 cur={a};hilite(a);setHash(a);
 const s=GEO[a];
 render(header(a,s.name,`${a} · ${ruleKind(a)} · state law portal`)+
  `<h4 style="font:600 .72rem var(--text);letter-spacing:.1em;text-transform:uppercase;color:var(--gold);margin:4px 0 0">Main cities</h4>${cityButtons(a)}`+
  lawSection(a)+roadSection(a)+planeSection(a)+hotelSection(s.name));
}
function selectDC(){cur={a:"DC"};hilite(null);setHash("DC");
 render(header("DC","Washington, DC","DC · "+ruleKind("DC")+" · state law portal")+lawSection("DC")+roadSection("DC")+planeSection("DC")+hotelSection("Washington, DC"));}
function cityHotelExtra(a,n){
 const S=SAMPLE[a+"|"+n]; if(!S) return "";
 let extra="";
 if(S.guide) extra+=lk("📍","PetPolicyCheck: pet-friendly hotels in "+n,"Chain rules, luxury hotels, dog parks",SITE+S.guide,"off").replace("Official","Site");
 if(S.exp) extra+=lk("🏨","See pet-friendly hotels on Expedia","Live affiliate link from the site",S.exp,"aff");
 extra+=lk("🐕","BringFido: pet-friendly places",S.q,`https://www.bringfido.com/lodging/?q=${enc(S.q)}`,"srch");
 return extra;
}
function selectCity(a,n){
 const key=a+"|"+n, S=SAMPLE[key], st=GEO[a];cur={a,n};hilite(a,key);setHash(a,n);
 const crumbs=`<p class="crumbs"><button data-state="${a}">← ${esc(st.name)}</button> · ${esc(n)}</p>`;
 const chips=airportChips(airportsFor(a,n), "Airports serving "+n);
 if(!S){
  render(crumbs+header(a,n,`${esc(st.name)} · city`)+chips+`<div class="stubbox"><b>Placeholder:</b> the full city booking panel (local taxis, transit, stations, hotels) is built for 8 sample cities in this preview. State-level links shown below.</div>`+lawSection(a,true,n)+roadSection(a)+planeSection(a,n)+hotelSection(n+", "+a));
  return;
 }
 const L=arr=>arr.map(x=>lk(...x)).join("");
 const city=`<h4>Taxis &amp; rideshare</h4><div class="links">${L(S.taxi)}${RIDES}</div>`+
  `<h4>Trains</h4><p>${AMTRAK_NOTE}</p><div class="links">${lk("🚆","Amtrak: "+S.amtrak[1],"Station page · then book on amtrak.com","https://www.amtrak.com/stations/"+S.amtrak[0],"off")}${lk("🐾","Amtrak: Pets on trains","Reserve the pet spot when you book","https://www.amtrak.com/pets","off")}${L(S.rail)}</div>`+
  `<h4>Buses &amp; local transit</h4><div class="links">${L(S.transit)}${lk("🚌","Greyhound","Service animals only, no pets (carrier policy; verify)","https://www.greyhound.com/","off")}</div><div class="stubbox"><b>Placeholder:</b> local transit pet rules (carrier size, fares, rush-hour limits) to be verified per agency.</div>`;
 render(crumbs+header(a,n,`${esc(st.name)} · city booking guide`)+
  `<div class="btnrow" style="margin:0 0 4px"><button class="btn ghost" data-state="${a}">State laws for ${esc(st.name)}</button></div>`+
  chips+lawSection(a,true,n)+roadSection(a,city)+planeSection(a,n)+hotelSection(S.q,cityHotelExtra(a,n)));
}
function airHead(ap){
 const tag=ap.pets?"":` · <b style="color:#f0a3a3">Placeholder hub</b>`;
 return `<div class="ph"><div class="ap-badge" aria-hidden="true"><svg viewBox="0 0 24 24" width="28" height="28"><path fill="#d9b765" d="${PLANE}"/></svg><b>${esc(ap.code)}</b></div><div><h2>${esc(ap.code)} — ${esc(ap.metroCity)}</h2><div class="sub">${esc(ap.name)} · ${esc(GEO[ap.placeState].name)}${tag}</div></div></div>`;
}
function selectAirport(code){
 const ap=airportByCode(code); if(!ap) return;
 step=3;
 const key=ap.metroState+"|"+ap.metroCity;
 cur={a:ap.metroState, n:ap.metroCity, ap:code};
 hilite(ap.metroState, key, code);
 setHash(ap.metroState, code);
 const st=GEO[ap.metroState];
 const crumbs=`<p class="crumbs"><button type="button" data-state="${ap.metroState}">← ${esc(st.name)}</button> · <button type="button" data-s="${ap.metroState}" data-city="${esc(ap.metroCity)}">${esc(ap.metroCity)}</button> · ${esc(ap.code)}</p>`;
 const q=SAMPLE[key]?SAMPLE[key].q:ap.metroCity+", "+ap.placeState;
 render(crumbs+airHead(ap)+
  `<div class="btnrow" style="margin:0 0 4px"><button type="button" class="btn" data-s="${ap.metroState}" data-city="${esc(ap.metroCity)}">City panel: taxis and hotels in ${esc(ap.metroCity)}</button></div>`+
  lawSection(ap.placeState,true,ap.metroCity,ap.metroState)+airportRoad(ap)+airportPlane(ap)+hotelSection(q,cityHotelExtra(ap.metroState, ap.metroCity)));
 applyStep(true);
}
function empty(){
 $("#panel").innerHTML=`<div class="empty"><div class="big">Pick a state or city</div><p>Click any of the 50 states on the map (or use the list) to open its law portal. Gold cities have the full booking guide. Plane marks are that city’s airports:</p><div class="citylist">${Object.keys(SAMPLE).map(k=>{const[a,n]=k.split("|");return `<button class="sample" data-s="${a}" data-city="${esc(n)}">${esc(n)}</button>`}).join("")}</div><div class="citylist">${AIRPORTS.filter(ap=>ap.pets&&SAMPLE[ap.metroState+"|"+ap.metroCity]).map(ap=>`<button type="button" class="apbtn" data-ap="${esc(ap.code)}">${esc(ap.code)} — ${esc(ap.metroCity)}</button>`).join("")}</div><p class="disc">Journey order: 1 vet + laws → 2 road/rail → 3 plane → 4 hotel. Dashed plane marks (SFO, DFW) are placeholder hubs.</p></div>`;
 $("#panel").querySelectorAll("[data-city]").forEach(b=>b.onclick=()=>selectCity(b.dataset.s,b.dataset.city));
 $("#panel").querySelectorAll("[data-ap]").forEach(b=>b.onclick=()=>selectAirport(b.dataset.ap));
}
function applyStep(scroll){
 document.querySelectorAll("#steps button").forEach(b=>b.setAttribute("aria-pressed",+b.dataset.step===step));
 const secs=document.querySelectorAll("#panel .sec");
 secs.forEach(s=>s.classList.toggle("focus",+s.dataset.sec===step));
 if(scroll){const t=document.querySelector(`#panel .sec[data-sec="${step}"]`);if(t){const p=$("#panel");if(innerWidth>900)p.scrollTo({top:p.scrollTop+t.getBoundingClientRect().top-p.getBoundingClientRect().top-6,behavior:"smooth"});else t.scrollIntoView({behavior:"smooth",block:"start"})}}
}
document.querySelectorAll("#steps button").forEach(b=>b.onclick=()=>{step=+b.dataset.step;if(!cur)selectCity("NY","New York City");applyStep(true)});
/* ---------- init ---------- */
$("#reset").onclick=()=>zoomTo(null);
buildMap();
const pick=$("#pick");ABBRS.forEach(a=>pick.add(new Option(GEO[a].name,a)));pick.onchange=()=>pick.value&&selectState(pick.value);
$("#grid").innerHTML=ABBRS.map(a=>`<button data-a="${a}">${mark(a)}<span>${esc(GEO[a].name)}</span></button>`).join("")+`<button data-a="DC">${mark("DC")}<span>Washington, DC</span></button>`;
$("#grid").querySelectorAll("button").forEach(b=>b.onclick=()=>{b.dataset.a==="DC"?selectDC():selectState(b.dataset.a);$("#panel").scrollIntoView({behavior:"smooth",block:"nearest"})});
const raw=decodeURIComponent((location.hash||"").replace(/^#/,"").replace(/\+/g," "));
const slash=raw.indexOf("/");
if(slash>0){const a=raw.slice(0,slash), n=raw.slice(slash+1);
 if(airportByCode(n)) selectAirport(n);
 else if(GEO[a]&&(GEO[a].cities||[]).some(c=>c.n===n)) selectCity(a,n);
 else if(a==="DC") selectDC();
 else if(GEO[a]) selectState(a);
 else empty();
}else if(airportByCode(raw)) selectAirport(raw);
else if(raw==="DC") selectDC();
else if(GEO[raw]) selectState(raw);
else empty();
