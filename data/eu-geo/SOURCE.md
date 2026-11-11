# EU map geography source

- **Dataset:** Natural Earth 10m Cultural — Admin 1 states and provinces  
- **License:** Public Domain  
- **URL:** https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/  
- **Build:** `tools/eu-maps/build_eu_geo.py` (shapely + pyproj) → `site/assets/js/*-map-geo.js`

Do not commit the raw Shapefile zip into git if avoidable; regenerate locally from the URL above.

## South Korea & Japan (2026-11-10)
- Same Natural Earth 10m admin-1 source as UK/FR/DE.
- Build: `tools/eu-maps/build_krjp_geo.py` → `site/assets/js/south-korea-map-geo.js` (17) and `japan-map-geo.js` (47). Okinawa inset mirrors USA Hawaii/Alaska offset.
- Hubs on map only when already in repo world decorative hubs: ICN, NRT.
- Japan fit: mainland lon/lat box (Hokkaidō–Kyūshū) excludes Ogasawara / Minamitorishima; Okinawa is a USA-style Hawaii inset.


## South Korea & Japan (2026-11-11 redo)
- Same Natural Earth 10m admin-1 source (public domain).
- Topology-aware simplification via mapshaper (Visvalingam, shared edges preserved), then projected to SVG.
  Build: `tools/eu-maps/build_krjp_geo.py` (needs a venv with pyshp/shapely/pyproj + `npx mapshaper`).
- On-map labels are English names; tiny regions (Seoul, Incheon, Sejong; Tokyo, Kanagawa, Saitama, Osaka, Nara) use USA-style leader lines.
- International airports from official lists (KAC+IIAC; MLIT 2026 winter 002028812.pdf); coordinates from OurAirports (public domain).
- City points: NE 10m populated places, plus Wikidata/Wikipedia summary coordinates for Hongseong and Muan (not in NE places). Sejong has no separate marker (region label).

## UK, France & Germany (2026-11-11 batch 2 preview)
- Same Natural Earth 10m admin-1 source (public domain). Topology-aware mapshaper (Visvalingam, shared edges).
- Build: `tools/eu-maps/build_eu3_geo.py`. Existing region ids kept (UK 12, FR 13 metro, DE 16).
- On-map labels are English names; tiny regions (Greater London; Berlin, Hamburg, Bremen; Île-de-France) use USA-style leader lines.
- Shared label-colour tokens in `country-map.css` (`--lbl-region`, `--lbl-city`, `--lbl-capital`, `--lbl-airport`) plus a label legend under the map.
- Airports from official lists (cited in the builder header): CAA Table 10.1 August 2026; UAF 2025 metro >100k pax (the legal arrêté “open to international traffic” list is much broader and is not plotted); ADV 22 international Verkehrsflughäfen (15 BMV §27d + 7 ADV). Coordinates: OurAirports (public domain).
- Cities: region / Land capitals and a few major cities from Natural Earth 10m populated places (public domain).


## Italy & Spain (2026-11-11 preview)
- Same Natural Earth 10m admin-1 source (public domain). Topology-aware mapshaper (Visvalingam, shared edges).
- Build: `tools/eu-maps/build_itesp_geo.py` → `italy-map-geo.js` (20 regions) and `spain-map-geo.js` (17 autonomous communities + Ceuta + Melilla).
- English names. Canary Islands use a USA-Hawaii / Japan-Okinawa inset; Sicily, Sardinia, Balearics, Ceuta and Melilla stay in geographic place.
- Italy airports: ENAC aeroporti di interesse nazionale (updated 23 June 2026) https://www.enac.gov.it/aeroporti/infrastrutture-aeroportuali/aeroporti-in-italia/
- Spain airports: Aena official network https://www.aena.es/en/passengers/our-airports.html (excludes GA fields and heliports).
- Coordinates: OurAirports (public domain). Cities: Natural Earth 10m populated places.
