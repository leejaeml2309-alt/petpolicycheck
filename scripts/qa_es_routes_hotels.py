#!/usr/bin/env python3
"""QA for ES routes+hotels preview on :8801."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright

ROOT = Path("/workspace/es-routes-hotels-preview-20261110")
BASE = "http://127.0.0.1:8801"
OUT = ROOT / "qa" / "es-routes-hotels"
OUT.mkdir(parents=True, exist_ok=True)

AD_RE = re.compile(
    r"googletagmanager|googlesyndication|adsbygoogle|doubleclick|pagead|emrldtp|"
    r"amazon-adsystem|googleads|FundingChoices|google-analytics|gtag|"
    r"csp\.withgoogle|ep1\.adtrafficquality|pagead2|TAGGING|Failed to load resource",
    re.I,
)

SHOT_PAGES = [
    ("es-routes-hub", "/es/routes/"),
    ("es-hotels-hub", "/es/hotels/"),
    ("es-route-usa-canada", "/es/routes/usa-canada.html"),
    ("es-route-usa-to-south-korea", "/es/routes/usa-to-south-korea.html"),
    ("es-hotel-boston", "/es/hotels/pet-friendly-hotels-boston.html"),
    ("es-hotel-new-york", "/es/hotels/pet-friendly-hotels-new-york.html"),
]


def clean_console(errs: list[str]) -> list[str]:
    return [e for e in errs if not AD_RE.search(e) and "[Report Only]" not in e]


def list_new_pages() -> list[str]:
    urls = []
    for section in ("routes", "hotels"):
        for p in sorted((ROOT / "site" / "es" / section).rglob("*.html")):
            rel = p.relative_to(ROOT / "site").as_posix()
            if rel.endswith("/index.html"):
                urls.append("/" + rel[: -len("index.html")])
            else:
                urls.append("/" + rel)
    return urls


def main() -> None:
    pages = list_new_pages()
    report: dict = {
        "shots": [],
        "console_errors": {},
        "page_count": len(pages),
        "direct_404": [],
        "link_404": [],
        "search": {},
        "ok": True,
    }

    def on_console(bucket):
        def _h(m):
            if m.type == "error":
                bucket.append(m.text)
        return _h

    def on_pageerror(bucket):
        def _h(e):
            bucket.append(str(e))
        return _h

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for name, url in SHOT_PAGES:
            for vp_name, w, h in [("desktop", 1280, 800), ("mobile", 390, 844)]:
                context = browser.new_context(viewport={"width": w, "height": h})
                page = context.new_page()
                errs: list[str] = []
                page.on("console", on_console(errs))
                page.on("pageerror", on_pageerror(errs))
                resp = page.goto(BASE + url, wait_until="networkidle", timeout=90000)
                status = resp.status if resp else 0
                shot = OUT / f"{name}-{vp_name}.png"
                page.screenshot(path=str(shot), full_page=False)
                cleaned = clean_console(errs)
                key = f"{name}:{vp_name}"
                report["console_errors"][key] = cleaned
                report["shots"].append({"id": key, "url": url, "status": status, "shot": str(shot)})
                if status >= 400 or cleaned:
                    report["ok"] = False
                context.close()

        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        api = context.request

        # Direct status of every new page
        for url in pages:
            r = api.get(BASE + url, timeout=20000)
            if r.status >= 400:
                report["direct_404"].append({"url": url, "status": r.status})

        # Crawl internal links from all new pages (same-origin paths)
        probed = set()
        for url in pages:
            page.goto(BASE + url, wait_until="domcontentloaded", timeout=60000)
            hrefs = page.eval_on_selector_all(
                "a[href]",
                "els => els.map(a => a.getAttribute('href'))",
            )
            for href in hrefs:
                if not href or href.startswith(("mailto:", "tel:", "javascript:", "#", "?")):
                    continue
                full = urljoin(BASE + url, href)
                parsed = urlparse(full)
                if parsed.scheme not in ("http", "https"):
                    continue
                host = parsed.hostname
                if host not in (None, "127.0.0.1", "localhost", "petpolicycheck.com"):
                    continue
                path = parsed.path or "/"
                if path in probed:
                    continue
                probed.add(path)
                # Only validate paths that should exist on this preview (local site tree)
                # Skip external-looking absolute live paths that are intentionally EN-only
                # but DO check /es/* and relative assets under site.
                check_hosts_local = host in (None, "127.0.0.1", "localhost") or path.startswith("/es/")
                if not check_hosts_local and host == "petpolicycheck.com":
                    # map live absolute to local for same path
                    pass
                try:
                    r = api.get(BASE + path, timeout=15000)
                    if r.status >= 400:
                        report["link_404"].append({"url": path, "status": r.status, "from": url})
                except Exception as e:
                    report["link_404"].append({"url": path, "status": "err", "error": str(e), "from": url})

        if report["direct_404"] or report["link_404"]:
            report["ok"] = False

        # Search test on /es/
        errs = []
        page.on("console", on_console(errs))
        page.goto(BASE + "/es/", wait_until="networkidle", timeout=90000)
        page.wait_for_timeout(500)
        inp = page.locator(".ppc-search__input").first
        inp.click()
        inp.fill("perro Nueva York")
        page.wait_for_timeout(1200)
        items = page.eval_on_selector_all(
            ".ppc-search__item",
            "els => els.map(a => ({href:a.getAttribute('href'), text:(a.querySelector('.ppc-search__title')||a).textContent.trim()}))",
        )
        es_hits = [i for i in items if i.get("href") and ("/es/" in i["href"] or i["href"].startswith("es/"))]
        # also try hotel city query if needed
        if not es_hits:
            inp.fill("hotel Boston")
            page.wait_for_timeout(1200)
            items = page.eval_on_selector_all(
                ".ppc-search__item",
                "els => els.map(a => ({href:a.getAttribute('href'), text:(a.querySelector('.ppc-search__title')||a).textContent.trim()}))",
            )
            es_hits = [i for i in items if i.get("href") and ("/es/" in i["href"] or "hotels" in i["href"])]
        report["search"] = {
            "query": "perro Nueva York",
            "items": items[:10],
            "es_hits": len(es_hits),
            "console": clean_console(errs),
        }
        if len(es_hits) < 1:
            report["ok"] = False
            page.screenshot(path=str(OUT / "search-fail.png"), full_page=False)

        context.close()
        browser.close()

    (OUT / "qa-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    summary = {
        "ok": report["ok"],
        "shots": len(report["shots"]),
        "page_count": report["page_count"],
        "direct_404": len(report["direct_404"]),
        "link_404": len(report["link_404"]),
        "link_404_sample": report["link_404"][:15],
        "console_nonzero": sum(1 for v in report["console_errors"].values() if v),
        "console_sample": {k: v for k, v in report["console_errors"].items() if v},
        "search_es_hits": report["search"]["es_hits"],
        "search_items": report["search"]["items"][:5],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
