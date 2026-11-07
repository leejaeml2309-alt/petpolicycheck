# Airport QR preview — 7 November 2026 (KST)

Preview only; no publication authorized. Base: `84b4fed`. Branch: `airport-qr` in an isolated worktree. No existing site page, shared theme, logo, price or language selector was modified.

## QR convention

Follow the original kit convention (not the alternate brief example):
`https://petpolicycheck.com/airport/AUS/?utm_source=airport_qr&utm_medium=print&utm_campaign=aus_relief`
Replace airport code and lower-case campaign prefix for each airport. Trailing slash matches the landing directories. Pages forward only incoming `utm_*` parameters to same-site links, preserving target queries and anchors; other incoming parameters are not forwarded.

## Official evidence read this turn

All source reads below occurred on 7 November 2026 (KST), not an on-site inspection. Individual URLs are in `sources.json`.

- AUS travel/security page: outdoor lower-level dog walks at both ends of parking garage; post-security pet restroom near Gate 9. Airline directory read with WebFetch.
- PDX Animals and airline directory: retrieved with curl/requests HTTP 200 (WebFetch provider returned 403); lower-level south-end baggage claim before security; B/C near Stumptown Coffee and D opposite D5 after security. Airline names verified from the directory's image alt text and carrier links.
- SAN services page, airline directory and airport terminal article read with WebFetch. T1 across Gate 117, T2 near Gate 46; ground transportation plazas outside both terminals. Conservative airline subset; no JetBlue inclusion based solely on the older terminal article.
- BTV amenities and airline directory read with WebFetch. Indoor post-security relief confirmed, but no precise concourse/gate. Before-security location unknown: ask airport staff.
- YVR official relief and airline directories read with WebFetch. Main terminal and South Terminal before security; A/B, C, D, E, International Arrivals level 4 and South Terminal after security.
- YUL official relief help article read in EN and FR with WebFetch: gates 47/65/73; public departures near Tracker and P4. French article agrees with English. Main airline directory is blocked (WebFetch 500, curl 403); include only Air Canada and American, independently confirmed on their official Montréal service/airport pages read with WebFetch.
- BNA kit pet page and current accessibility/directory routes return empty bodies or bot-protection notices despite HTTP 200. The airport's readable BNA Vision announcement (22 November 2021) confirms curbside areas, P5 dog park, and Concourse D. Clearly label it historical. American's readable current BNA guide adds D2 and T1; ask airport staff to confirm access. Only American is included as a verified airline; list is explicitly non-exhaustive.
- DoveLewis, Canada West and CENTREDMVET official sites read with WebFetch: 24/7 emergency service confirmed. These clinics already exist in the repo's USA/Canada map data. No new clinic invented. They are NOT advertised as the geographically nearest; distance ranking is unavailable. Ask airport staff for the closest current option.

## Existing guide content only

- AUS: existing Austin hotel guide; named city properties only, not claimed airport-adjacent.
- YVR: existing Canada guide's Fairmont Hotel Vancouver (city hotel, not Fairmont airport).
- YUL: existing Canada guide's Alt Hotels/YUL-area brand listing; confirm specific property.
- BNA, PDX, SAN and BTV: no matching existing guide properties confirmed; ask airport staff.
- AUS, BNA, SAN and BTV: no existing map clinic with confirmed local 24/7 status; ask airport staff. Do not repurpose health-certificate clinics as emergency hospitals.

## QA and reproducibility

Artifacts live at `/workspace/ppc-pastilles-palettes-preview-wd/airport-qr/`:
`build.py`, `flyers.py`, `qa.py`, `verify_pdfs.py`, `qa.json`, `node-check.json`, `external-check.json`, `sources/`, `shots/`, `pdf/qr-manifest.json`.

42 site JavaScript files checked with `node --check`. Eight pages × two viewports (390×844, 1440×900), mobile menu, console/resource errors, overflow, duplicate IDs, absence of ads/language selector, UTM preservation, linked internal pages and fragment targets checked. Seven single-page A4 PDFs rasterized and their actual printed QR decoded with OpenCV, matching exact manifest URLs. PDFs copied to the original kit folder; clearly marked preview / airport approval required before display.

External automated GET: 20 linked official URLs checked; 11 return 403 to box requests, but each of those was readable with WebFetch. Preserve these results in `external-check.json`; do not call them 404s. YUL's blocked airline directory and BNA's unreadable current pages are not used as substantive evidence.

`PUBLISH-WHEN-APPROVED.sh` has an airport-qr mode, prepared but NOT run. It targets this isolated worktree and requires fast-forward. If `/pro/` or any other branch publishes first, stop, restack/rebase this unpublished airport branch, regenerate preview and QA, and obtain Marc's approval for the updated reviewed result. Never overwrite main.
