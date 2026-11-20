# PetPolicyCheck News — how to add an item

This section is built **without** `build.py`. Put one Markdown file per article in `site/news/_posts/`, then run:

```bash
python3 news_build.py
```

The script writes the article HTML, the list page (`/news/`), sitemap entries, and the RSS feed (`/news/feed.xml`), and mirrors everything into `static/`.

Do **not** run `build.py`. Keep `site/` and `static/` in sync by always using `news_build.py`.

## Required fields

Every post must have YAML front matter with all of the following. If `source_url` or `source_date` is missing or empty, **the script exits with an error and writes nothing** — an item cannot be published without an official source.

| Field | Required | Notes |
| --- | --- | --- |
| `slug` | yes | URL path `/news/<slug>/`. Lowercase letters, numbers, hyphens only. |
| `title` | yes | Article headline. |
| `date` | yes | Date we published the item on PetPolicyCheck (`YYYY-MM-DD`). |
| `category` | yes | One of: `cdc-usda`, `airlines`, `countries`, `adoptions`. |
| `summary` | yes | 1–2 lines for the list card and RSS description. |
| `source_name` | yes | Name of the official source (e.g. `CDC`, `USDA APHIS`). |
| `source_url` | yes | Official source URL (`http` or `https`). Script errors out if absent. |
| `source_date` | yes | The **source's own date** (`YYYY-MM-DD`), not today's check date. Script errors out if absent. |
| body (after `---`) | yes | Markdown article body. |

## Optional fields

| Field | Notes |
| --- | --- |
| `updated` | Date we updated the item (`YYYY-MM-DD`). Shown as “Updated …” on the article. |
| `what_this_means` | Markdown for the “What this means for pet travellers” block. Omit the block if empty. |
| `related` | List of on-site links. Each item is a URL, or `{url, label}`. |

Categories (stable ids → label):

- `cdc-usda` → CDC/USDA
- `airlines` → Airlines
- `countries` → Countries & quarantine
- `adoptions` → Adoptions

## Copy-paste example

Save as `site/news/_posts/cdc-dog-import-form.md`:

```markdown
---
slug: cdc-dog-import-form
title: "CDC Dog Import Form: a receipt is required for every dog entering the U.S."
date: 2026-11-20
category: cdc-usda
summary: "CDC requires a Dog Import Form receipt for each dog entering the United States. Always confirm the current rule on the official CDC page before you travel."
source_name: Centers for Disease Control and Prevention (CDC)
source_url: https://www.cdc.gov/importation/dogs/dog-import-form-instructions.html
source_date: 2026-04-28
updated:
what_this_means: |
  Complete the form before you travel. If the dog is flying, show the receipt
  to the airline before boarding, and keep it to show U.S. Customs and Border
  Protection on arrival. Confirm any later change on the official CDC page.
related:
  - url: /countries/usa.html
    label: USA entry rules
  - url: /vet-info/
    label: Vet info
---

Write the article here in Markdown. Quote only what the official source says.
Link back to the official page in the body if it helps the reader, but the
**Official source** box at the top of the article is required and is filled
from `source_name`, `source_url` and `source_date`.
```

You can also use a `.json` file with the same fields (`body` is a Markdown string). Markdown with YAML front matter is the usual format.

## Samples (preview only)

Files in `site/news/_samples/` are **never** published by a default build. They exist so a preview can be generated with:

```bash
python3 news_build.py --samples
```

Sample items are labelled “Sample” on the page. After a `--samples` preview, run `python3 news_build.py` again (no flag) so the committed `/news/` list stays a clean empty state until a real post is added to `_posts/`.

Do not put sample files in `_posts/`.
