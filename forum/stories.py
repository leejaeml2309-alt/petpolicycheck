"""Pet Travel Stories page (/forum/pet-travel-stories/): summaries of public forum discussions, from the research CSV.

Source: /workspace/animaux-forums/base_forums_animaux.csv (UTF-8 BOM, maintained by another bot; rules in its METHODE.md).
At build time the file is refreshed into data/forum_stories.csv when the source exists and is newer (set
FORUM_STORIES_SRC to override the path). The internal column "Intérêt pour l'activité" is dropped from the repo copy
and is never read or published.

Languages: one translated title/summary per UI language found in forum/i18n/<code>.json, read from the CSV columns
"Titre <CODE>" / "Résumé <CODE>" (EN fallback when empty). Adding fr.json / ja.json later is all it takes for FR / JA.
"""
import csv
import datetime as dt
import os
import shutil
import urllib.parse
from pathlib import Path

DEFAULT_SRC = "/workspace/animaux-forums/base_forums_animaux.csv"
PRIVATE_COLS = ("Intérêt pour l'activité",)
MAX_QUOTE_WORDS = 25
COL_QUOTE = "Citation courte (langue d'origine)"

CATEGORY = {"Voyage en avion": "air", "Papiers et vaccins": "papers", "Quarantaine": "quarantine", "Coûts": "costs",
            "Sociétés de transport": "shippers", "Santé et stress": "health", "Caisse et matériel": "crate",
            "Races interdites": "banned", "Autre": "other"}
SPECIES = {"chien": "dog", "chat": "cat", "les deux": "both"}
SRC_LANG = {"français": "fr", "anglais": "en", "coréen": "ko", "japonais": "ja", "italien": "it", "allemand": "de"}


def refresh_copy(root_dir):
    """Copy the source CSV into data/forum_stories.csv when it is newer (minus private columns). Returns the repo copy path."""
    dst = root_dir / "data" / "forum_stories.csv"
    src = Path(os.environ.get("FORUM_STORIES_SRC", DEFAULT_SRC))
    if src.exists() and (not dst.exists() or src.stat().st_mtime > dst.stat().st_mtime):
        with src.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        cols = [c for c in (rows[0].keys() if rows else []) if c not in PRIVATE_COLS]
        tmp = dst.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        shutil.move(tmp, dst)
        print(f"  stories: refreshed data/forum_stories.csv from {src} ({len(rows)} rows)")
    return dst


def load(root_dir, langs):
    """Validated stories (public fields only) + number skipped."""
    path = refresh_copy(root_dir)
    if not path.exists():
        print("  WARNING: stories: data/forum_stories.csv missing; page will be empty")
        return [], 0
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out, skipped = [], 0
    for r in rows:
        rid = (r.get("ID") or "?").strip()
        link = (r.get("Lien") or "").strip()
        quote = (r.get(COL_QUOTE) or "").strip()
        if urllib.parse.urlsplit(link).scheme not in ("http", "https") or not urllib.parse.urlsplit(link).netloc:
            print(f"  WARNING: stories: row {rid} skipped (no http(s) link)")
            skipped += 1
            continue
        if len(quote.split()) > MAX_QUOTE_WORDS:
            print(f"  WARNING: stories: row {rid} skipped (quote has {len(quote.split())} words > {MAX_QUOTE_WORDS})")
            skipped += 1
            continue
        en_t = (r.get("Titre EN") or "").strip() or (r.get("Titre (langue d'origine)") or "").strip()
        en_s = (r.get("Résumé EN") or "").strip() or (r.get("Résumé (langue d'origine)") or "").strip()
        tr = {}
        for code in langs:
            t = (r.get(f"Titre {code.upper()}") or "").strip()
            s = (r.get(f"Résumé {code.upper()}") or "").strip()
            tr[code] = (t or en_t, s or en_s)
        tr["en"] = (en_t, en_s)
        cat = CATEGORY.get((r.get("Catégorie") or "").strip(), "other")
        date = (r.get("Date du post") or "").strip()[:10]
        try:
            dt.date.fromisoformat(date)
        except ValueError:
            date = ""
        out.append({"id": rid, "tr": tr, "quote": quote, "slang": SRC_LANG.get((r.get("Langue source") or "").strip().lower(), "other"),
                    "cat": cat, "species": SPECIES.get((r.get("Espèce") or "").strip().lower(), ""),
                    "route": (r.get("Pays ou trajet concerné") or "").strip(),
                    "site": urllib.parse.urlsplit(link).netloc.lower().removeprefix("www."),
                    "date": date, "link": link})
    out.sort(key=lambda s: s["date"], reverse=True)
    return out, skipped
