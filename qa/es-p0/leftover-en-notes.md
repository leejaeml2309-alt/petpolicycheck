# Leftover English (visible) — ES P0 preview

## False positives (ignored)
- Airline brand names containing "Airlines" (American Airlines, etc.)
- Spanish imperative "Compare tarifas…" matching scanner word "Compare"
- Official acronyms / product names kept on purpose (SENASICA, USDA, Pet Travel Passport, B2B Pet Desk, Uber Pet…)

## Real leftover English by page
### index (home)
- GUIDES panel summaries still EN for USA/KR/JP/CA/MX (titles/CTAs translated; long `summary` / some `line` fields not)
- Map tip / request-country panel still mixed EN for countries without a guide ("We haven't verified…", forum CTA) — JS partially localized
- AIRLINES table: some `carrier` fields still EN for non-P0 airlines (Air Canada, Air France, Hawaiian, JetBlue, Lufthansa…)

### airlines/* (delta, united, american, alaska especially)
- Occasional English fragments inside policy cells that were not in the translator hand map (brand program names OK; some sentence fragments remain)
- Preview warning on some pages: "Vista previa de trabajo local…" (intentional for local preview)

### airlines/compare/
- Dynamic airline detail cells remain EN as published by airlines (by design / existing note in compare.foot)
- Some chrome already ES via compare-ui.js

### passport/
- Form labels partly ES in HTML; computed trap/timeline **content** from passport-data remains EN (data layer)
- UI chrome of generated card localized in passport-ui.js for /es/

### countries/mexico.html
- Manifest flagged possible SPAINISM for review — not altered

### routes/*
- Mostly clean; official source titles may stay EN

## Div balance
- index.html EN and ES: 90/90 after script strip (translator QA had warned 93/90; current sources balance)
