# Leftover English (visible) — ES P1 preview (complements2)

## Truncation root cause
False positives «Última veri» / «Verificado en la» / «están en la» came from the QA text-node walker + `t[:200]` slice splitting on `<time>` / `<a>` — HTML was already complete in P1 source and under `site/es/`.
Real fixes applied from `truncated_fixes_es.json`: full meta descriptions (4 routes), Canada YUL/YVR relief cells (from canada-hubs.json), snub-nosed lede agreement.

## Complements2 applied
- truncated_fixes: 10/10
- dynamic_data_es: 399/399 (52 us_states notes + 185 comparator cells + 162 passport-airlines) via /es/-only runtime overlays (EN data files unchanged at rest)

## cvi / rabies
YES — shown on ES passport timeline when a US state is selected: `passport-engine.js` appends `CVI ${st.cvi}; rabies ${st.rabies}` (values still EN).

## Remaining EN (by design / still EN)
- `us_states[].cvi` and `us_states[].rabies` field values (displayed on passport)
- Comparator `fee_usd_*` numerics / meta.rules (untouched per pack)
- Brand names, airport codes, breed names, `needs_review`
