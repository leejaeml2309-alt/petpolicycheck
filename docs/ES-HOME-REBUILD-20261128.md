# Spanish homepage rebuild (2026-11-28)

`site/es/index.html` was rebuilt from the CURRENT English `site/index.html` (v4j nav, no story, no album) and is
**edited directly** in the repo, like `site/index.html` itself. `build.py` is stale and crashes at `affiliate_box`,
so it must not be used to regenerate either homepage.

Spanish-only gates added to shared scripts (English behaviour unchanged):
- `assets/js/ppc-metro.js` (key m18es1): `ESHOME` flag (data-ppc-locale="es" on /es/ or /es/index.html) -> Spanish line/station/UI strings, /es/ links where an ES page exists.
- `assets/js/ppc-ticket-frames.js` (key tk8es1): CTA "Embarcar aquí" on the ES home.
- `assets/ppc-header.js` (key es1): metro + ticket-frame loaders now also run on /es/ home.
- `assets/js/home-c.js` (key 20261128cc1es1): Spanish country names / sort / "guía" pin text when locale = es.
- `assets/js/es-country-names.js` (new): ICU Spanish country names for the world map.

Intentionally English: "Paw Passport" (Marc's name), copyright line and "See Terms" (Marc rule 2026-11-12, ppc-i18n.js).
