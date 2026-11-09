# Leftover English (visible) — ES P1 preview

## Complements applied (2026-11-09)
- leftover_strings_es.json: **61/61** (GUIDES 9, AIRLINES carriers 5, passport rules 19 + traps 7 + JP note 1, passport-engine 3, home-c 17 via ppcHS)
- ui_js_es_usted.json: **84** ES keys drop-in on `ui.js` (usted + transportadora)

## Truncated ES strings (mirrored EN DOM cuts — not completed)
### Meta descriptions
- `/es/routes/usa-canada.html` — ends «(más un» (EN: «(plus a»)
- `/es/routes/usa-france.html` — ends «veterinario acreditado USDA» (EN: «USDA-acc»)
- `/es/routes/usa-uk.html` — ends «(endoso en tinta),» (EN: «(ink endorsement),»)
- `/es/routes/usa-to-japan.html` — ends «espera de 180 días» (EN: «180-day wai»)

### Body fragments that look cut off
- `/es/routes/usa-to-japan.html` — «…las direcciones de correo están en la»
- `/es/countries/usa.html` — «…Última veri» ; «…Verificado en la»
- `/es/countries/canada.html` — «…confirmado vía s oficial» ; «…contenid»
- `/es/airlines/snub-nosed-breeds.html` — «…Cada fila es una»

## Remaining EN areas (still English — request translations; not translated here)
- **passport-data `us_states[].notes`**: 52 state notes (49 non-empty) still EN
- **airlines-comparator-data.js** dynamic fee/weight/dims/policy cells (~30 airlines) still EN
- **passport-data airlines** dynamic cabin fee / under-seat dims / warn strings still EN
- Official source titles, brand program names, and acronyms kept on purpose

## False positives
- Airline brand names containing "Airlines"
- Spanish «Compare…» matching scanner word Compare
