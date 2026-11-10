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
