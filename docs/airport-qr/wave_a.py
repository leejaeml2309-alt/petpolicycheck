"""Wave A: facts from official pages checked 7 Nov 2026 KST; no invented locations."""
from copy import deepcopy
AA=lambda c:f'https://www.aa.com/web/i18n/travelInformation/destinationInformation/{c.lower()}-airport.html'
LAXT=lambda t:f'https://www.flylax.com/flight-detail/animal-relief--station/animal-relief-station-{t}'
T4='https://www.jfkt4.nyc/rules-regulations/'
T5='https://www.jfkairport.com/explore-jfk/terminals/terminal-5'
EWRA='https://www.newarkairport.com/explore-ewr/terminals/terminal-a/terminal-a-accessibility-features'
CLOSED5='https://www.lawa.org/news-releases/2025/LAX%20ANNOUNCES%20TERMINAL%205%20CLOSURE%20TO%20MAKE%20WAY%20FOR%20MAJOR%20TRANSFORMATION'
def p(g,label,detail,note='Level: verify on site',src=None,uncertain=False):return (g,label,detail,note,src,uncertain)
WAVE_POINTS={
'JFK':[
 p('before','Terminal 4','Outside · Arrivals Level 1','Exact spot: verify on site',T4),
 p('before','Terminal 8','Outside baggage claim','Follow red parking sign',AA('JFK')),
 p('before','Terminal 8','Outside ticketing Door F','Center island · verify on site',AA('JFK')),
 p('after','Terminal 4 · Concourse B','Between Gates B31 and B33','Level: verify on site',T4),
 p('after','Terminal 5 · Rooftop','Across from Gate 528','Dog walk · verify current hours',T5),
 p('access','Other terminal locations','Airport confirms all terminals','Gate / level: verify on site',None,True)],
'EWR':[
 p('before','Terminal A','Outside Arrivals · Zone 6','Level: verify on site',AA('EWR')),
 p('after','Terminal A','Across Gates A7 / A8','Between food-court restrooms',AA('EWR')),
 p('access','Terminals B / C','Relief confirmed airport-wide','Exact points: verify on site',None,True)],
'MIA':[
 p('before','North Terminal D','Across Door 5 · Level 1','West of Dolphin garage'),
 p('before','Central Terminal F','Across Door 15 · Level 1','West of South short-term lot'),
 p('after','North Terminal D','Near Gate D34'),p('after','Concourse F','Near Gate F7'),p('after','Concourse G','Near Gate G11'),p('after','H–J Connector','Across from InMotion store'),
 p('access','South Terminal J','Door 28 · Level 1','CLOSED: construction',None,True)],
'LAX':[
 p('before','Between Terminals 1 / 2','Outside · Baggage Level 1','Indexed only: verify on site',LAXT('t1'),True),
 p('after','Terminal 1','Near Gate 13 · Level 3','Indexed only: verify on site',LAXT('t1'),True),
 p('after','Terminal 2','Near Gate 21A · Level 3','Indexed only: verify on site',LAXT('t2'),True),
 p('after','Terminal 4','Follow signs near Gate 41','Level: verify on site',AA('LAX')),
 p('access','Terminal 5','Closed for reconstruction','Do not use old relief listing',CLOSED5,True),
 p('access','T3 / T6 / T7 / T8 / TB','No exact point verified here','Gate / level: verify on site',None,True)],
'ORD':[
 p('before','Terminal 1','Lower level · Door 1A','Near United bag claim 15'),
 p('before','Terminal 2','Lower level · Door 2E','Near bag claim 1'),
 p('before','Terminal 5','Lower level · Door 5B','Near bag claim 10'),
 p('before','Multi-Modal Facility','Outside Door 6 · turn right','Rental Cars / Lot F'),
 p('after','Terminal 1 · Concourse C','Just past Gate C10','Hall toward C12'),
 p('after','Terminal 3 · Rotunda','Between Terminals 2 and 3','Hall toward T2 · on left'),
 p('after','Terminal 3 · Gate L26','End of hall · by windows','AA says L27: verify on site'),
 p('after','Terminal 5 · Concourse M','Near Gate M8','Hall toward M7 · on left'),
 p('after','Terminal 5 · Concourse M','Between M25 and M26','Restroom bank · own entrance'),
 p('restricted','Terminal 5','Sterile corridor before CBP','Access: verify on site'),
 p('restricted','Terminal 5','International baggage claim','Access: verify on site'),
 p('access','Terminal 3 · Main Hall','Relief area CLOSED','Construction wall',None,True)],
'MCO':[
 p('before','Terminal A','Level 2 · east end','Outside terminal'),p('before','Terminal B','Level 2 · west end','Outside terminal'),p('before','North Cell Phone Lot','East end of lot','Outdoor relief'),
 p('after','Gates 1–29','Entrance to Gates 20–29'),p('after','Gates 30–59','Entrance to Gates 40–49'),p('after','Gates 70–99','Entrance to Gates 90–99'),p('after','Gates 100–129','Gate 121 / 121–129 wing'),
 p('after','Terminal C','Near C241 and C242','Level 2 (FAQ)'),
 p('restricted','Terminal C','Level 6 · before intl bags','Arrivals access: verify on site'),
 p('access','Terminal C','FAQ differs: C236 vs C238','Exact gate: verify on site',None,True)],
'ATL':[
 p('before','Domestic Terminal South','Outside Doors W1 / W2','Poochie Park · verify access',None,True),
 p('before','International Terminal','Arrivals · outside Door A1','Current access: verify on site',None,True),
 *[p('after','Concourse '+g[0],g,'Current access: verify on site',None,True) for g in ['T7','A10','B33','C19','D Centerpoint','E14','F7']]],
'SEA':[
 p('before','North end · Ticketing','Outside Door 33','Departures level'),p('before','North end · Baggage','Outside Door 26','Arrivals level'),p('before','South end · Baggage','Near Doors 00 / 02','Past Carousel 1'),p('before','Parking garage','Level 1 · blue elevators','Near cruise-lobby exit'),
 p('after','Concourse A','Near Gate A10'),p('after','Concourse C','Restrooms near C3'),p('after','Concourse D','Restrooms near D1'),p('after','S Concourse','S Underground Train Station'),p('after','N Concourse','N Underground Train Station'),
 p('restricted','International Arrivals','Mezzanine · US Customs','Arriving passengers only')],
'DEN':[
 p('before','Jeppesen Terminal','West side · Door 200','Outdoor relief; level 2 per AA'),
 p('after','Concourse A','Center core · US Mail Drop'),p('after','Concourse B','Center core · US Mail Drop'),p('after','Concourse C','Center core · US Mail Drop'),p('after','Outdoor Deck A','Near Gate A15'),p('after','Outdoor Deck B','West side · near B7'),p('after','Outdoor Deck C','East side · near C67')],
'IAH':[
 p('before','Terminal E','Arrivals Level 1 · E-103','Across street / traffic lanes'),
 p('after','Terminal A','Near Gate A12'),p('after','Terminal B','Near B1 · across Fruteria'),p('after','Terminal C','Across Gate C2'),p('after','Terminal D','Across Gate D12'),p('after','Terminal E','Across Gate E12')],
'DTW':[
 p('before','McNamara Terminal','Outside International Arrivals','Lower level'),p('before','Evans Terminal','Both ends of departures curb','Upper level · grassy areas'),p('after','McNamara Terminal','Adjacent to Gate A34'),p('after','Evans Terminal','Across from Gate D16')],
'DFW':[
 p('before','Terminal A','Lower level · outside A8','Outside entry doors'),p('before','Terminal C','Garage near C17','Temporary construction location'),p('before','Terminal D','Lower level · D15 and D29','Outside entry doors'),p('before','Terminal E','Lower level · E2 and E38','Outside entry doors'),
 p('after','Terminal A','Near A29'),p('after','Terminal B','Near B28'),p('after','Terminal D','Near D18'),p('after','Terminal E','Near E31'),
 p('access','Terminal C · after security','No point listed by airport','Verify on site',None,True),p('access','Terminal B · before security','No door listed by airport','Verify on site',None,True)],
'SFO':[
 p('before','Harvey Milk Terminal 1','Outside baggage claim','Follow painted paws',AA('SFO')),
 p('before','Terminal 2','Pre-security area listed','Door / level: verify on site'),p('before','Terminal 3','Pre-security area listed','Door / level: verify on site'),
 p('after','Harvey Milk Terminal 1','Between B3 and B6',src=AA('SFO')),p('after','Harvey Milk Terminal 1','Between B15 and B16',src=AA('SFO')),
 p('after','Terminal 2','Post-security areas listed','Gate / level: verify on site'),p('after','Terminal 3','Post-security area listed','Gate / level: verify on site'),p('after','International A','Post-security area listed','Gate / level: verify on site'),p('after','International G','Post-security area listed','Gate / level: verify on site')]
}
WAVE_MAPS={'JFK':'https://maps.jfkairport.com/su/wgXhsJZQ','EWR':'https://maps.newarkairport.com/su/y6klB5yy','MIA':'https://www.miami-airport.com/map-animal-relief-areas.asp','LAX':'https://www.flylax.com/lax-terminal-maps','ORD':'https://maps.ord.flychicago.com/','MCO':'https://flymco.com/terminal-maps/','ATL':'https://www.atl.com/maps/','SEA':'https://maps.flysea.org/su/8UDxkl61','DEN':'https://maps.flydenver.com/','IAH':'https://iahmaps.fly2houston.com/su/4pwSIzx8','DTW':'https://www.metroairport.com/at-dtw/maps','DFW':'https://www.dfwairport.com/map/','SFO':'https://www.flysfo.com/maps'}
NOTES={
'JFK':'Selected verified locations only, not a complete terminal inventory. Airport confirms relief areas at all terminals; remaining gates, levels, newly changed areas and terminal access: verify on site. Terminal 4 source is its official operator; Terminal 5 rooftop source is the airport itself. Do not infer access between terminals.',
'EWR':'Terminal A is independently located by airport and American sources. The airport confirms relief areas airport-wide, but exact B/C gates and levels were not verified from readable official text; verify on site.',
'LAX':'The kit PDF and terminal relief pages blocked both fetch providers (403). T1/T2 details are from indexed official-page excerpts only, not a successful live page-body read: verify on site. Only T4 near Gate 41 is independently confirmed from a readable American page. LAWA confirms Terminal 5 closed for reconstruction: do not use old T5/Gate 52B relief instructions. Other terminal relief locations remain unverified here. Verification attempts: 7 November 2026 (KST).',
'MIA':'The outdoor South Terminal J / Door 28 area is marked temporarily closed due to construction by the airport. It is not presented as an available stop. Indoor levels and access from your gate: verify on site.',
'ORD':'The airport describes these as service-animal relief areas; pet eligibility and current access: ask airport staff. T3 Main Hall is closed. Airport gives L26 while American gives L27: verify on site. T5 sterile-corridor / international-baggage areas have restricted arrivals access, not a general departures route. Unlisted before-security T3 details: ask airport staff.',
'MCO':'The official FAQ conflicts on the third Terminal C gate: C236 in one answer, C238 in another. That point is not placed as a confirmed location; verify on site. C241/C242 agree. Level 6 is an international-arrivals location; confirm access. Gate-wing labels also differ slightly for 100–129: ask staff.',
'ATL':'The airport source is an announcement describing these relief locations, not an on-site inspection or current opening-status feed. Current access, levels and construction changes at every listed point: verify on site.',
'SEA':'International Arrivals Facility relief is on the Mezzanine in US Customs and only for internationally arriving passengers. Do not treat it as a generally accessible post-security stop. Unspecified concourse levels: verify on site.',
'DEN':'Airport relief-page locations take precedence over broader airline gate descriptions. Concourse levels and outdoor-deck access: verify on site. No walking connection or nearest-stop ranking is implied.',
'IAH':'Terminal E outdoor relief is across traffic lanes from Door E-103; use official signs and safe crossings. Post-security levels and current terminal construction access: verify on site.',
'DTW':'McNamara and Evans are separate terminals; no walking connection is implied. Unspecified post-security levels: verify on site. Follow current terminal names on airport signage.',
'DFW':'Temporary Terminal C outdoor location is in the garage near C17. Airport does not list a C post-security location or B pre-security door: verify on site, not an assertion that none exists. Construction may change access.',
'SFO':'The official page provides terminal/security groupings but not every gate/level. American adds two Terminal 1 gate pairs. Remaining doors, exact points and levels: verify on site. Do not mistake the diagram for complete navigable airport geometry.'}
HOTELS={'JFK':('new-york','The Peninsula New York and 1 Hotel Brooklyn Bridge'),'EWR':('new-york','The Peninsula New York and 1 Hotel Brooklyn Bridge'),'MIA':('miami','Faena Hotel Miami Beach and Kimpton EPIC Hotel'),'LAX':('los-angeles','Hotel Figueroa and Loews Hollywood Hotel'),'ORD':('chicago','Kimpton Gray Hotel and Loews Chicago Hotel'),'MCO':('orlando','The Ritz-Carlton Orlando, Grande Lakes and Waldorf Astoria Orlando'),'IAH':('houston','Hotel ZaZa Houston Museum District and Hotel Granduca Houston'),'DTW':('detroit','Shinola Hotel and Detroit Foundation Hotel')}
def extend(D,kit):
 for c,points in WAVE_POINTS.items():
  d=deepcopy(kit[c]);d.update(checked='2026-11-07 KST',before=[],after=[],airlines=['american'],airline_sources=[[AA(c),f'American’s {c} airport guide']],note=NOTES.get(c,''))
  # Text list and drawing share exactly the same fact records. No separate invented geometry.
  for g,label,detail,note,source,uncertain in points:
   if g in ['before','after']:d[g].append([label,detail+'. '+note+'.'])
  if not d['before']:d['before']=[['No location confirmed','Verify on site; ask airport staff.']]
  if not d['after']:d['after']=[['No location confirmed','Verify on site; ask airport staff.']]
  if c in HOTELS:
   slug,names=HOTELS[c];d['hotels']=[names,'hotels/pet-friendly-hotels-'+slug+'.html','Existing '+slug.replace('-',' ').title()+' hotel guide','City / regional properties already in our guides, not verified airport-adjacent options. For EWR, New York properties require onward travel. Confirm current pet restrictions and availability.']
  if c=='JFK':d['airlines']=['american','delta','jetblue'];d['airline_sources'] += [['https://www.jfkairport.com/explore-jfk/terminals/terminal-4','JFK Terminal 4 / Delta'],[T5,'JFK Terminal 5 / JetBlue']]
  if c=='EWR':d['airlines']+=['air-canada','jetblue'];d['airline_sources'].append([EWRA,'EWR Terminal A airline accessibility information'])
  if c=='LAX':d['airlines']+=['jetblue','delta'];d['airline_sources'].append(['https://www.flylax.com/lax-terminal-maps','LAX Terminal 3 / Delta']);d['airline_sources'].append([CLOSED5,'LAWA terminal relocation announcement']);d['check_label']='Verification attempted'
  D[c]=d
