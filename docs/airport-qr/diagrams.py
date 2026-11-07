"""Original non-geographic schematics: source-text groupings, not traced airport plans."""
import html,textwrap
MAPS={
 'AUS':'https://airportmaps.flyaustin.com/',
 'BNA':'https://map.flynashville.com/',
 'PDX':'https://flypdx.com/map/occupant/Pet%20Relief',
 'SAN':'https://www.san.org/airport-authority-guidelines-operations/',
 'BTV':'https://btv.aero/terminal-map/',
 'YVR':'https://www.yvr.ca/en/passengers/navigate-yvr/terminal-maps',
 'YUL':'https://www.admtl.com/en-CA/guide/terminals-map/'
}
# Each entry: security group, short source-derived label, source-derived detail,
# explicit unknowns, optional alternative official source, uncertain placement flag.
POINTS={
'AUS':[
 ('before','Parking garage','Lower level · both ends','Outdoor pet relief',None,False),
 ('after','Barbara Jordan Terminal','Near Gate 9','Level: verify on site',None,False)],
'BNA':[
 ('before','Terminal curbside','Relief areas (2021 source)','Exact spot: verify on site',None,True),
 ('before','Terminal Garage 1','Level P5 · dog park','Current access: verify on site',None,True),
 ('after','Concourse D','Across from Gate D2','Level / access: verify on site','https://www.aa.com/web/i18n/travelInformation/destinationInformation/bna-airport.html',False),
 ('after','Gate T1 area','Next to Gate T1','Level / access: verify on site','https://www.aa.com/web/i18n/travelInformation/destinationInformation/bna-airport.html',False)],
'PDX':[
 ('before','Main terminal','Outside baggage claim','Lower level · south end',None,False),
 ('after','Concourses B / C','Near Stumptown Coffee','Level: verify on site',None,False),
 ('after','Concourse D','Across from Gate D5','Level: verify on site',None,False)],
'SAN':[
 ('before','Terminal 1','Ground Transportation Plaza','Outdoor pet relief',None,False),
 ('before','Terminal 2','Ground Transportation Plaza','Outdoor pet relief',None,False),
 ('after','Terminal 1','Across from Gate 117','Level: verify on site',None,False),
 ('after','Terminal 2','Near Gate 46','Level: verify on site',None,False)],
'BTV':[
 ('before','No location confirmed','No point placed here','Verify on site',None,True),
 ('after','Terminal relief areas','Indoor · exact gate unknown','Gate / level: verify on site',None,True)],
'YVR':[
 ('before','Main terminal','Outside International Arrivals','Chester Johnson Park entrance',None,False),
 ('before','South Terminal','Across from north entrance','Outdoor pet relief',None,False),
 ('after','Domestic A / B Pier','Across from play area','Before Starbucks',None,False),
 ('after','Domestic C Pier','Across from Gate C29','Alcove right of washrooms',None,False),
 ('after','International D Pier','Across from Gate D72','Level: verify on site',None,False),
 ('after','International D Pier','Between Gates 58 and 62','Level: verify on site',None,False),
 ('after','International Arrivals','Level 4 · corridor walkway','Pet relief',None,False),
 ('after','International Arrivals','Level 4 · overflow queuing','Pet relief',None,False),
 ('after','USA E Pier','Near Gates E76 and E77','Level: verify on site',None,False),
 ('after','South Terminal','Gate G1–2 · vending machines','In the corner',None,False)],
'YUL':[
 ('before','Public area','Departures level · near Tracker','Pet relief',None,False),
 ('before','Public area','P4 parking lot','Exact spot: verify on site',None,False),
 ('after','Domestic pier','In front of Gate 47','Level: verify on site',None,False),
 ('after','International pier','Restrooms near Gate 65','Level: verify on site',None,False),
 ('after','Transborder pier','Restrooms near Gate 73','Level: verify on site',None,False)]
}
from wave_a import WAVE_POINTS,WAVE_MAPS
POINTS.update(WAVE_POINTS)
MAPS.update(WAVE_MAPS)

def render(c,d):
 e=lambda x:html.escape(str(x),quote=True)
 groups=[];sources=[];y=12;num=0
 for key,heading in [('before','BEFORE SECURITY'),('after','AFTER SECURITY'),('restricted','RESTRICTED ARRIVALS ACCESS'),('access','STATUS / VERIFY ON SITE')]:
  points=[x for x in POINTS[c] if x[0]==key]
  if not points: continue
  height=42+len(points)*106
  groups.append(f'<rect class="diagram-region" x="4" y="{y}" width="352" height="{height}" rx="12"/><text class="diagram-heading" x="18" y="{y+26}">{heading}</text>')
  py=y+42
  for group,label,detail,note,source,uncertain in points:
   num+=1;code=f'{c[0]}{num}';url=source or d['pets_url'];mark=str(num)
   # Rectangles and ordered markers identify source entries only. Their arrangement
   # intentionally encodes no relative direction, distance or walking connection.
   groups.append(f'<a href="{e(url)}" target="_blank" rel="noopener noreferrer" aria-label="{e(code+": "+label+". "+detail+". "+note+". Official source")}"><g class="diagram-point{ " diagram-uncertain" if uncertain else ""}"><rect x="16" y="{py}" width="328" height="96" rx="8"/><circle cx="38" cy="{py+26}" r="14"/><text class="diagram-marker" x="38" y="{py+32}" text-anchor="middle">{mark}</text><text class="diagram-label" x="61" y="{py+25}">{e(label)}</text><text x="61" y="{py+50}">{e(detail)}</text><text class="diagram-detail" x="61" y="{py+74}">{e(note)}</text></g></a>')
   sources.append({'id':code,'group':key,'label':label,'detail':detail,'note':note,'source':url,'official_map':MAPS[c],'verify_on_site':uncertain or 'verify on site' in note.lower()})
   py+=106
  y+=height+18
  if key=='before':
   groups.append(f'<path class="diagram-boundary" d="M12 {y-9}H348"/>')
 d['diagram_points']=sources;d['official_map']=MAPS[c]
 svg=f'<svg class="airport-diagram-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 {y}" role="img" aria-labelledby="diagram-title-{c} diagram-desc-{c}"><title id="diagram-title-{c}">{c} pet relief schematic</title><desc id="diagram-desc-{c}">Original schematic grouping source-listed relief points before and after security. No directions, relative positions, walking routes or distances are implied. Missing details must be verified on site.</desc>'+''.join(groups)+'</svg>'
 sourcehtml=''
 for s in sources:
  sourcehtml+=f'<li><strong>{e(s["id"])} · {e(s["label"])}</strong><br><a href="{e(s["source"])}" target="_blank" rel="noopener noreferrer">Point source ↗</a> · <a href="{e(s["official_map"])}" target="_blank" rel="noopener noreferrer">Official airport map ↗</a></li>'
 vet=''
 if 'vet' in d:
  name,url,_=d['vet'];vet=f'<div class="diagram-vet"><strong>V · Off-airport 24/7 resource</strong><p><a href="{e(url)}" target="_blank" rel="noopener noreferrer">{e(name)} ↗</a></p><p>Already in our map data. Not plotted in the terminal or distance-ranked. Nearest clinic: verify on site.</p></div>'
 else:vet='<p class="airport-note">Nearest 24/7 vet: verify on site. No qualifying local emergency clinic confirmed in our existing map records.</p>'
 caveat=f'<p class="airport-note">{e(d.get("note",""))}</p>' if c in WAVE_POINTS else ''
 return f'''<section class="airport-panel airport-diagram" id="airport-diagram"><div class="diagram-intro"><div class="airport-code">{c} · Practical pet stops</div><h2>Your pet-stop diagram</h2><p>Simplified diagram, not to scale — check official airport signage</p><p class="airport-meta">Original PetPolicyCheck drawing from written official sources. Numbered stops are grouped by security access, not geographic position; no walking route is implied.</p></div>{caveat}<div class="diagram-layout"><div>{svg}<div class="diagram-legend"><span><b class="legend-dot">1</b> Source-listed relief point</span><span><b class="legend-dot legend-unknown">?</b> Dashed outline: verify on site</span><span><i class="legend-boundary"></i> Security grouping only</span></div></div><div class="diagram-sources"><h3>Official maps &amp; point sources</h3><p class="airport-meta">Source check: 7 November 2026 (KST). See caveats below; use the numbered source list to confirm every point. Maps open on the airport’s own website{'; SAN links to the official page containing its terminal-map PDF' if c=='SAN' else ''}.</p><ol>{sourcehtml}</ol><p class="airport-note">Levels or gate details not stated in a source: verify on site. For current access, ask airport staff.</p>{vet}</div></div></section>'''
