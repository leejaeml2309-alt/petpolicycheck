# Status — Japan, South Korea, Australia guides + K9 on UK / France / Germany

Date: 14 November 2026 (Asia/Seoul).

**Published** 14 November 2026 after Marc’s « Publie les guides » (13:05 KST).
Base: `origin/main` was `4fa88957` (Italy/Spain already live; no newer WD commits at fetch).
Branch: `guides-jp-kr-au-k9-20261114`
Worktree: `/workspace/it-es-sections-20261114`
Content commit: `17c919fd`
Publish commit (sitemap + this status): see git log on `main` after push.

Live URLs: `/countries/japan.html`, `/countries/south-korea.html`, `/countries/australia.html`, plus K9 on `/countries/{uk,france,germany}.html` and `/it/countries/{uk,france,germany}.html`.
Sitemap: the three new EN country-guide URLs added with `<lastmod>2026-11-14</lastmod>` in `site/sitemap.xml` and `static/sitemap.xml`. World-map links were not changed.

## Done today

1. **United Kingdom, France, Germany** (existing language versions only)
   - Added a dedicated `K9 and assistance dogs` / `K9 e cani da assistenza` section after Grooming, before FAQ.
   - EN: `site/countries/{uk,france,germany}.html` (synced to `static/`).
   - IT: `site/it/countries/{uk,france,germany}.html` (synced to `static/`). Lei register.
   - No ES versions of these country guides exist on origin/main — none created.

2. **Japan, South Korea, Australia — new EN country guides**
   - These pages did **not** exist on origin/main (only `*-map.html` and route pages). New files created in Italy/Spain format (same header, 3 newlines, site chrome).
   - EN only: `site/countries/japan.html`, `south-korea.html`, `australia.html` (synced to `static/`).
   - No IT/ES country-guide versions existed to update. IT/ES map pages were not edited (map files avoided).

### Sections per new EN page

| Page | Sections added |
|---|---|
| Japan EN | entry-rules, return, taxi, train, airlines, hotels, vets, grooming, k9, related, faq |
| South Korea EN | entry-rules, return, taxi, train, airlines, hotels, vets, grooming, k9, related, faq |
| Australia EN | entry-rules, return, train, airlines, hotels, vets, grooming, k9, related, faq (no national official taxi source opened — taxi section omitted) |

### Sections on UK / FR / DE

Only the missing dedicated K9 section was added. Taxi, bus, train, airlines, hotels, parks, vets and grooming were already present.

## Local preview

```
cd /workspace/it-es-sections-20261114/site && python3 -m http.server 8766 --bind 127.0.0.1
```

(Port 8765 from the earlier Italy/Spain preview is also still serving the same `site/`.)

- http://127.0.0.1:8766/countries/japan.html
- http://127.0.0.1:8766/countries/south-korea.html
- http://127.0.0.1:8766/countries/australia.html
- http://127.0.0.1:8766/countries/uk.html
- http://127.0.0.1:8766/countries/france.html
- http://127.0.0.1:8766/countries/germany.html
- http://127.0.0.1:8766/it/countries/uk.html (IT sample)
- http://127.0.0.1:8766/it/countries/france.html
- http://127.0.0.1:8766/it/countries/germany.html

## Screenshots

Full-page Playwright shots (system Chrome), 1280 and 390, in `/workspace/it-es-sections-20261114/shots/`:

- `en-japan-1280.png`, `en-japan-390.png`
- `en-south-korea-1280.png`, `en-south-korea-390.png`
- `en-australia-1280.png`, `en-australia-390.png`
- `en-uk-1280.png`, `en-uk-390.png`
- `en-france-1280.png`, `en-france-390.png`
- `en-germany-1280.png`, `en-germany-390.png`
- `it-uk-1280.png`, `it-uk-390.png` (non-EN sample)

Italy/Spain shots from the earlier pack remain in the same folder under `en-italy-*`, `en-spain-*`, `it-*`, `es-*`.

## Omissions (no official source opened, or conflict / stale page — not invented)

- **Japan:** no official national duty for ordinary taxis to accept pets; no official national hotel pet tariff or clinic/grooming directory; Tokyo Metro English FAQ dimensions conflict with a Japanese “営業のご案内” PDF and were not used; “quarantine within 12 hours” from the route page was not found on the AQS English import page opened today, so it is omitted; designated-region country names (e.g. Hawaii / Guam) were not re-listed from a fetched AQS list — readers are pointed to the official AQS pages; ANA/JAL ordinary-pet yen fees are not published as a single figure on the pages opened.
- **South Korea:** Korail English pet page is a JavaScript app and did not yield verifiable text today — Korail centimetre/weight figures from the October route page were **not** copied; Seoul Metro official terms page returned HTTP 500; Korean Air official pet page returned 403 and was not opened — no KE weights or fares; Kakao T Pet FAQ did not yield usable text (scripted page) — no Kakao prices; no official national hotel tariff or clinic/grooming directory; APQA rabies-free country list was not readable, so this guide does not name the United States (or any other country) as listed or unlisted; APQA English page still shows an Anyang address.
- **Australia:** no official national (all-states) taxi or public-transport pet rule opened — Victoria PTV only; official Qantas / Virgin fare tables were not successfully opened — no airline dollar amounts; no official national hotel tariff or clinic/grooming directory; published DAFF permit/PEQ dollar fees are on the official fee pages (pack of 12 Nov) and were not re-copied as a full table in this lean pass.
- **Germany K9:** no official national taxi rule for assistance dogs was added (the existing taxi section is still a placeholder).
- **UK K9:** Equality Act s.168 fine is “level 3 on the standard scale”; no pound amount is stated in the official text, so none is given.
- **Languages:** IT/ES country guides for Japan, South Korea and Australia were not created (no existing language versions of those country guides). ES versions of UK/FR/DE country guides do not exist.

## Remaining for Tuesday

1. IT and ES country guides for Japan, South Korea and Australia (same sections, Lei / usted), once EN is approved.
2. Re-open Korail (English pet rules), Seoul Metro terms, Korean Air pets, Kakao T Pet, Qantas/Virgin official pet pages, a Japan official clinic directory (if one exists), Accor or other official hotel-chain lists, and a national Australian taxi / other-state transport source — add only what those official pages actually say.
3. Optional: a Japan “bus” section and an Australia “taxi” section if official sources are found.
4. Sitemap, world-map CTAs and hreflang for the new country URLs — **not done here** (no map files touched; no `build.py`). WD / a later pass after Marc’s publish OK.
5. Re-check APQA English page freshness (address / rabies-free list).

Self-check: `site/` and `static/` byte-identical for all changed files; header still 3 newlines; no Amazon/ebook/affiliate/TODO in public copy; internal live links on existing URLs return 200; new `/countries/{japan,south-korea,australia}.html` are preview-only (404 on the live site until published).
