# NOTES — USA route pages pack · 2026-11-09

Local only. Nothing published, committed, pushed, emailed or scheduled.

## What Marc already approved
- Rubrique 2: fiches trajets « pays A vers pays B », starting with 5 main routes from the USA (Manager message 15:42 KST).
- Preview only → Web Designer integrates → Marc typed OK before publish.
- Translations later via Traducteur Universel.

## Pack
| Slug | Pair | CDC return risk (dogs) | Live overview page? |
|---|---|---|---|
| usa-canada | USA ↔ Canada | low | No overview; airline-route pages live |
| usa-mexico | USA ↔ Mexico | low (+ screwworm USDA) | No overview; airline-route pages live |
| usa-uk | USA ↔ Great Britain | low | No overview; no UK country page |
| usa-japan | USA ↔ Japan | low | **Yes** `/routes/usa-to-japan.html` |
| usa-france | USA ↔ France (EU) | low | No overview; airline-route pages live |

## Decisions for Marc
1. **Page model:** create new country-pair overview pages (`/routes/usa-canada.html` etc.) that sit above the existing airline-specific corridors, or fold this content into each airline-route page? Recommendation: **new overviews**, linking down to airline pages (same pattern as live `usa-to-japan.html`).
2. **Japan overlap:** live `usa-to-japan.html` was last checked Oct 24, 2026. Publish this Nov 9 refresh as a replacement/update, or keep live text and only add the structured checklist/FAQ blocks?
3. **Missing country pages:** `/countries/uk.html` and `/countries/france.html` and `/countries/japan.html` return **404**. Build them next, or link only to APHIS/destination authorities + airline pages for now?
4. **EU certificates (France):** APHIS requires **new** non-commercial EU health certificates effective **1 Oct 2026** (commercial 17 Oct). Confirm Web Designer shows a clear callout so travellers do not use pre-Oct models.
5. **Mexico NWS (dogs):** NWS inspection certificate since **3 Aug 2026** (no APHIS endorsement outbound). Return needs SENASICA screwworm certificate ≤5 days. OK to keep the red callout in Quick answer?
6. **UK cabin rule:** state clearly that ordinary pets **cannot** fly in cabin on commercial flights **into** GB. OK?
7. **Exit formalities (CA / UK / FR → US):** official pages do **not** clearly mandate a destination exit health certificate solely for US return (unlike Japan AQS export). Text uses “Not stated on the official page” + “confirm with airline/APHA”. Approve that wording, or ask Traducteur/Veilleur for a deeper APHA/CFIA exit dig?
8. **Bot-blocked sources:** APHIS + CDC URLs returned **HTTP 403** to curl from the box; content confirmed via WebFetch/WebSearch Nov 9, 2026. Require a human click-through before publish (same as Expedia hotel links).
9. **Fees:** no invented amounts. Where official pages omit fees → “Not stated on the official page” / Check flag. OK?
10. **Breed bans:** Ontario/Winnipeg, GB Dangerous Dogs/XL Bully, France Catégorie 1/2 included as Official rule with sources. Keep on route pages or only on future country pages?

## Gaps (data)
- Exact OISA / AQS / HARC cargo centre cash fees: not stated on the pages used.
- UK↔USA overview and UK/France/Japan country pages: not live.
- agriculture.gouv.fr often times out to automated tools; France claims cross-checked with service-public.fr, APHIS France, and EU Commission pages.
- Northern Ireland = EU rules (not GB) — mentioned; no full NI checklist in this pack.
- Hawaii/Guam Japan designated-region path included; other US territories not expanded.

## Credit / reuse
Reused without re-fetch where possible:
- `/workspace/hotels-wt/data/routes/usa-japan.json`
- `/workspace/hotels-wt/data/countries/usa.json`
- Vague A Canada / Mexico / UK / France JSON + RECAP (2026-11-06)
Fresh fetches only for APHIS Mexico, APHIS France, GOV.UK taking-pet-abroad, CDC risk confirmation, live PPC URL checks.

## Next after Marc OK
1. Hand `CONTENT-*.md` + `data/routes.json` + preview to **Web Designer** (fast-forward only).
2. Human re-click APHIS/CDC/SENASICA/AQS links.
3. Traducteur Universel for FR/ES/DE/KO/JA after EN publish.
