# Paddle no-ads preview — how to restore ad panels

This branch is a **local preview**. Nothing is published until Marc types « publie ».

## Switch

In `build.py`, set `SHOW_ADS = True` and restore the HTML from `origin/main` (or revert this commit). Do **not** run `python3 build.py` without checking: `main()` deletes `site/` first (`shutil.rmtree(OUT)`), which would drop pages that were added outside that generator.

## What this preview removed (to restore later)

1. **Google AdSense units (kept the account and `ads.txt`)**
   - Head script: `https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7693501377730690`
   - Header band: three 300×250 units, slot `4584637408` (`adsense_header_slot`)
   - Homepage mid/bottom bands: slot `9881497431` (`adsense_home_footer_slot`) and `home_mid`
   - Site footer band: slot `2114688057` (`ads.site_footer.adsense_slot`)
   - Empty placeholder cells labelled “Advertisement / Advertise here” (`sidebar_or_footer` and others)
   - Build helpers: `header_ad`, `home_footer_ad`, `site_footer_ad`, `ad_frame`, `ad_slot`, `ad_grid`, `medium_rect_*`, `ad_ph`

2. **Brand-ad offer and every public link to it**
   - `/advertise/` (media kit: placements, audience, rates on request) → noindex redirect to `/contact.html#suggest-a-product`
   - `/field-guides/advertise.html` → same redirect
   - `/forum/partners.html` (free promotional thread in exchange for a backlink) → same redirect
   - Homepage mid-page band “Reach pet parents planning a trip / Advertise here” (and the ES equivalent)
   - Homepage / menu CTA “Advertise” (`pastilles.js` + home nav)
   - Footer “Advertise” / “Anúnciese” and “Advertise here” under footer units
   - Top “Your brand here · Become a PetPolicyCheck partner” placeholder (`partner-banner.js`, `assets/partners/top-partner.json` left in the tree, unused)
   - Field Guides “Sponsor an episode · Become a partner” panel and open-slot CTAs (`ugc.js`)

3. **Copy that sold ads**, reworded on About, Contact, Privacy, insurance disclosures, i18n, and the search index.

## Left untouched

- `site/ads.txt` (Google publisher `pub-7693501377730690`)
- Amazon Associates and other **affiliate** links / disclosures (including `rel="sponsored"` on those links)
- `.lbadge`, and the tokens `--bg`, `--paper`, `--ink`
- Travelpayouts / booking affiliate scripts
