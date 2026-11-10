# EU map geography source

- **Dataset:** Natural Earth 10m Cultural — Admin 1 states and provinces  
- **License:** Public Domain  
- **URL:** https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/  
- **Build:** `tools/eu-maps/build_eu_geo.py` (shapely + pyproj) → `site/assets/js/*-map-geo.js`

Do not commit the raw Shapefile zip into git if avoidable; regenerate locally from the URL above.
