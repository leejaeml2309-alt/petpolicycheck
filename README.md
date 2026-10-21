# Airline pet policy directory (v1)

Static site: airline pet policies, each checked against the airline's official page with a "last verified" date.

- `data/airlines/<slug>.json`: one file per airline. `null` = not confirmed on the official page -> rendered "Check with airline".
- `config.json`: site name (placeholder), base URL, affiliate slots (empty = no box rendered).
- `python3 build.py`: renders `site/` (index, airline pages, updates, about, sitemap.xml, robots.txt). Stdlib only.
- `python3 refresh.py`: nightly check of the airline checked longest ago (`--slug X`, `--all`, `--dry-run`, `--no-build`).
  Hashes policy-relevant text, sets `needs_review` + an Updates entry on change (values are never auto-edited),
  bumps `last_verified` only when the page is unchanged, rebuilds, writes `reports/YYYY-MM-DD.md`.
  Git commit/push is intentionally disabled: see `publish_hook()`.
- Cron: `0 3 * * * cd /workspace/petsite && python3 refresh.py >> reports/cron.log 2>&1`
- GitHub Pages (later): publish the `site/` folder (e.g. via an Actions workflow), then set `base_url` in config.json.
