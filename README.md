# Airline pet policy directory (v1)

Static site: airline pet policies, each checked against the airline's official page with a "last verified" date.

- `data/airlines/<slug>.json`: one file per airline. `null` = not confirmed on the official page -> rendered "Check with airline".
- `config.json`: site name (placeholder), base URL, affiliate slots (empty = no box rendered).
- `data/products.json`: pet travel products (dimensions copied from the official maker page, `official_url` = source) + guides + skipped list.
- `data/cabin_limits.json`: numeric under-seat limits parsed from each airline's `max_carrier_dimensions`; each `quote` must still appear in the airline JSON or the limit is dropped at build (warning printed).
- `config.json` `product_links.<slug>.amazon_url|chewy_url`: empty -> buy button goes to the maker's page; filled -> affiliate link with rel="sponsored nofollow".
- `config.json` `ads.<airline_top|guide_sponsor|sidebar_or_footer>`: image_url, link_url, alt, advertiser. Empty -> small "Advertise here" link to /advertise/.
- `python3 build.py`: renders `site/` (index, airline pages, updates, about, sitemap.xml, robots.txt). Stdlib only.
- `python3 refresh.py`: nightly check of the airline checked longest ago (`--slug X`, `--all`, `--dry-run`, `--no-build`).
  Hashes policy-relevant text, sets `needs_review` + an Updates entry on change (values are never auto-edited),
  bumps `last_verified` only when the page is unchanged, rebuilds, writes `reports/YYYY-MM-DD.md`.
  Then commits + pushes (no force) via `publish_hook()`; `--no-publish` to skip.
- Cron: `0 3 * * * cd /workspace/petsite && python3 refresh.py >> reports/cron.log 2>&1`
- Live: https://leejaeml2309-alt.github.io/petpolicycheck/ (GitHub Actions deploys `site/` on every push to main).
