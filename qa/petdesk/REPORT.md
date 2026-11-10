# Pet Desk preview — trial clauses + For pros banner

**Branch:** `petdesk-trial-banner-20261110` @ `8b4c9bd` (based on `origin/main` `8dd867a`)  
**Worktree:** `/workspace/petdesk-preview-20261110`  
**Server:** `http://127.0.0.1:8802` (site/) — LOCAL ONLY, no push  
**Date:** 2026-11-10 Asia/Seoul

## Preview URLs
- http://127.0.0.1:8802/pro/
- http://127.0.0.1:8802/terms.html
- http://127.0.0.1:8802/refund-policy.html
- http://127.0.0.1:8802/privacy.html *(unchanged — see gaps)*
- http://127.0.0.1:8802/hotels/pet-friendly-hotels-new-york.html
- http://127.0.0.1:8802/countries/canada.html
- Also: all 13 hotel city guides + usa/mexico/uk/france/germany country pages + hotel-pets hub

## Shots (`qa/petdesk/`)
- terms/refund/privacy/pro/hotel-ny/country-canada × desktop 1280 + mobile 390
- Scroll: `pro-plans-desktop.png`, `terms-trial-desktop.png`, `hotel-ny-banner-desktop.png`, `hotel-ny-banner-mobile.png`, `canada-banner-desktop.png`

## QA
Playwright 1280 + 390 on Terms, Refund, Privacy, /pro/, 1 hotel, 1 country: **0 console errors** (AdSense/Travelpayouts blocked), **0 internal 404s**.

## Pages touched
- Legal/product: `terms.html`, `refund-policy.html`, `pro/index.html` (+ static mirrors)
- Banner CSS/include: `assets/css/ppc-pro-banner.css`, `assets/includes/ppc-pro-banner.html`
- Hotels: 13× `pet-friendly-hotels-*.html` + `hotel-pets/index.html`
- Countries: `usa.html`, `canada.html`, `mexico.html`, `uk.html`, `france.html`, `germany.html`
- Privacy: **not modified**

## Gaps / contradictions (quoted)
1. **Privacy — missing text:** Pack has no Privacy draft. trial-check.md: *"Privacy — add Pet Desk trial/account processing before activation (open decision from 7 Nov pack)."* Live still: *"PetPolicyCheck is a simple static website."* → left untouched; no invented legal text.
2. **Refund overlap:** Pack `"Separate 14-day refund guarantee"` overlaps live `"14-Day Refund Guarantee"`. Inserted free-trial section WORD FOR WORD; added pack separation sentence + price table; kept live how-to / Paddle portal bullets.
3. **Pro IPATA CTA:** Pack common label `"Start your free 14-day trial"` replaces live `"Start 14-day IPATA & Relocation Agency trial"` on Pro card (pack: common CTA, no eligibility assumed). Buttons remain `mailto:contact@…` (pack: destination not defined; must not hit paid checkout).
4. **Terms §3 vs new trial sections:** Live §3 still says subscriptions renew automatically / authorize recurring charges; new § trial + paid-sub clarify only confirmed paid plans renew. Mild tension left as-is (did not rewrite §3 beyond inserting pack text).
5. **Banner:** Per proposal, does **not** say “free 14-day trial” (refund-only microcopy) until clauses are *live* — even though they appear in this same preview.
6. **Non-EN /pro/ i18n:** EN notice/FAQ/CTA from pack; other langs CTA set to EN pack string; non-EN notice/FAQ not rewritten (pack is EN-only).

Nothing published. Awaits Marc « publie ».
