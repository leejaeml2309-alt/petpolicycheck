# Airport QR preview — 7 November 2026 (KST)

Preview only; no publication authorized. Current base: `b73c540` (original seven-airport work started on `84b4fed`). Branch: `airport-qr` in an isolated worktree. No existing site page, shared theme, logo, price or language selector was modified.

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


## Second pass — original inline SVG diagrams (7 November 2026, KST)

Seven responsive inline SVG drawings, 30 source-list entries (including an explicitly unlocated BTV before-security placeholder). Original abstract grouping geometry only: no official map is copied, traced or reproduced. Separate before/after-security group boxes; no route, cardinal direction, floorplan, distance or proximity implied. Each point links its actual official textual source and its airport map. The text source and official map are distinguished; SAN map link leads to the official page containing the Terminal Map PDF. Legend and required not-to-scale/signage disclaimer are displayed. Readable text checked with SVG getBBox at both viewports. `diagrams.py` retains the drawing definitions; point evidence is in `sources.json`.

YVR and YUL EN relief pages re-read with WebFetch. `contacts-and-drafts.md` was read as supporting source inventory only; none of its drafts, contacts or forms were acted on. Sources containing email drafts do not authorize contact.

Missing levels/gates/current access are explicitly “verify on site”; BTV before-security location not plotted, BTV after-security gate/level unknown, BNA historical curbside/P5/current access uncertain. No nearest-vet ranking invented. Existing PDX/YVR/YUL clinic resources are labelled off-airport and not plotted inside terminals.

Exact wording “Scan counts available on request” is present on all eight pages and seven A4 PDFs; no monthly-report promise. No analytics or tracking implementation was added.

Second QA: 42 JS syntax checks OK; 16 renders without console/resource errors, overflow, duplicate IDs or SVG text overflowing its viewBox; 41 internal destinations/anchors, zero broken. All seven diagrams present; no diagram on index. UTM-only propagation and mobile menu tests pass. Seven regenerated single-page A4 PDFs re-rasterized; 7/7 printed QR codes decode to the exact unchanged kit-convention URLs; text extraction confirms scan-count wording. Copies refreshed in original kit folder.

Seven new official-map URLs checked in `official-map-check.json`: AUS/PDX/BTV HTTP 200; SAN/YVR HTTP 403 to box but readable with WebFetch; YUL 500 WebFetch/403 box (official URL corroborated via indexed official terminal-map page); BNA WebFetch 500 and box TLS issuer validation failure (official map URL corroborated on official airport homepage/announcement). Certificate verification was not bypassed. These map URL errors are reported rather than treated as a reason to invent point details.

Extra requested captures: `shots/AUS-plan-visible-1440x900.png`, `shots/AUS-plan-visible-390x844.png`, `shots/YUL-plan-visible-390x844.png`, plus `*-diagram-full-*.png` and all 16 full-page renders. The original first-pass summary remains above.


## Current Wave A extension — 20 airports / 21 pages

Rebased the two unpublished airport commits locally onto `b73c540` (published /pro/ inclusion change). Rebase finished clean; `site/pro/` is identical to that base, main checkout untouched. No push or publication.

Added JFK, EWR, MIA, LAX, ORD, MCO, ATL, SEA, DEN, IAH, DTW, DFW, SFO to the index, landing-page generator, original diagrams and A4 flyer data. All thirteen primary official relief URLs were checked this turn (7 November 2026 KST). Twelve page bodies were read with WebFetch; LAX kit PDF is blocked HTTP 403 and was NOT represented as successfully read. Official LAX terminal detail pages also block both fetch providers. LAX T1/T2 locations are explicitly labelled indexed-official-excerpt only / verify on site; T4 near Gate 41 is independently read from American. LAWA confirms T5 closed for reconstruction, so the old PDF's T5 point is NOT used. LAX's official terminal-map page is readable and confirms Delta at T3. Map geometry was never copied or traced.

Terminal-specific completeness is not claimed: JFK T4/T5/T8 points are sourced, other current terminal points unknown; EWR exact B/C points unknown. All new airline lists are selected verified subsets, not complete directories: American station pages were individually read for all thirteen hubs, with additional airport/LAWA evidence for JFK Delta/JetBlue, EWR Air Canada/JetBlue, and LAX Delta/JetBlue. Existing airline policy pages and the comparator are linked.

Important source discrepancies / access conditions are visible above the diagrams: MIA J/Door28 temporarily closed; ORD T3 Main Hall closed and airport L26 vs American L27, restricted T5 arrivals areas; MCO source itself differs C236 vs C238, so that point is unresolved rather than silently chosen; ATL announcement locations need current-access confirmation; SEA IAF restricted to international arrivals; DFW C17 is temporary and C post-security/B pre-security details are unlisted. See `verify-on-site.json` for all twenty airports' per-point caveats.

No new emergency vet is invented or advertised as nearest: none of the new hubs' existing map records was established here as a qualifying closest 24/7 emergency option. Existing city hotel guides only are used for JFK/EWR (New York region, explicitly not airport-adjacent), MIA, LAX, ORD, MCO, IAH and DTW; no invented hotel at other hubs.

### Flyer data / visual template separation

The current flyer style is intentionally unchanged while another designer prepares playful variants. Canonical working files in the artifact root:
- `flyer-data.json`: twenty resolved per-airport records, including code/name/city, QR URL, separate UTM values, short URL, headline, intro, bullet headings/bodies, CTA, disclaimer, scan-count wording and preview notice.
- `flyer-template.html`: visual HTML/CSS only, with placeholders; no airport-specific URL/UTM/copy is embedded.
- `flyers.py`: escapes JSON copy, builds QR codes, and renders the template. Run with the artifact-root venv Python; then `qa.py` exports PDFs and `verify_pdfs.py` raster-decodes them and refreshes kit copies.
Reference snapshots of those three files are committed beside this README. Styling changes can reuse the same JSON URLs/UTM/text without rebuilding airline/location research.

### Final Wave A validation

42 JavaScript syntax checks pass. 21 pages × 390/1440 = 42 Chromium renders: zero console/JS/resource errors, horizontal overflow, duplicate IDs, ads, language selectors or SVG-text viewBox overflow; mobile menu and UTM-only propagation pass. 61 internal destinations/anchors checked, zero broken. Initial QA caught long raw-source URLs causing mobile overflow on four pages; removed the redundant raw prose URLs (the clickable per-point source list remains), then all 42 renders passed.

20 single-page A4 PDFs generated from the isolated template/data, 20/20 QR codes decoded from actual PDF rasterizations to exact kit-convention URLs; all 20 include “Scan counts available on request”, no monthly-report promise. PDFs copied to original kit folder. `external-check-wave-a.json` records 72 official destinations and HTTP/TLS conditions; source content read with WebFetch when box GET is blocked. The guessed MCO map host failed TLS and was replaced by the verified official terminal-map page `https://flymco.com/terminal-maps/` (200). BNA's existing official map still fails local certificate-issuer validation; no verification bypass used. No linked source was declared absent just because a provider blocks it.

Requested captures: `shots/JFK-plan-visible-{390x844,1440x900}.png`, `shots/LAX-plan-visible-{390x844,1440x900}.png`; `*-plan-points-*` captures prioritize diagram points, and `*-diagram-full-*` include the complete schematics. All 42 full-page captures are in `shots/`. No publication mode was executed; the airport branch is now stacked on the published Pro commit.
