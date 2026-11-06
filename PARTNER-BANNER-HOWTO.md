# Partner banner howto (PetPolicyCheck)

Sitewide slot under every page's top navigation (`aside.partner-slot.partner-top`), reserved height 90px desktop / 100px mobile to avoid CLS.

## One file to edit

`static/assets/partners/top-partner.json` (copied to `site/assets/partners/` on build):

```json
{
  "active": false,
  "image": "",
  "image_mobile": "",
  "link": "",
  "alt": "",
  "partner": "",
  "html": ""
}
```

## Go live with an image

1. Drop creatives in `static/assets/partners/` (e.g. `acme-970x90.webp`, optional `acme-320x100.webp`).
2. Edit `top-partner.json`:

```json
{
  "active": true,
  "image": "acme-970x90.webp",
  "image_mobile": "acme-320x100.webp",
  "link": "https://partner.example/",
  "alt": "Acme — pet travel partner",
  "partner": "Acme",
  "html": ""
}
```

3. Run `python3 build.py`. Rebuild injects the creative on every HTML page.
4. Links use `rel="sponsored noopener"` and `target="_blank"`.

## Or inject partner HTML/JS tag

Set `"active": true` and put the partner snippet in `"html"` (leave `image` empty). Prefer images when possible.

## Turn off

Set `"active": false` (or clear image/link/html). The discreet placeholder returns:
**Your brand here · Become a PetPolicyCheck partner** → `/advertise/`.

## Notes

- Do not put AdSense code in this slot; AdSense keeps its own frames.
- No need to edit `build.py` or page templates for a normal swap.
- Optional future: per-page override files `static/assets/partners/<slot>.json` (not required today; global `top-partner` is the default).
