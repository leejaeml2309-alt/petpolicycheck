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
