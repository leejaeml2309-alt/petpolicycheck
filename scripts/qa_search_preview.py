#!/usr/bin/env python3
"""Playwright QA for search preview: desktop/mobile shots + console errors."""
from __future__ import annotations

import json
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUT = ROOT / "qa" / "search"
OUT.mkdir(parents=True, exist_ok=True)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(SITE), **k)

    def log_message(self, fmt, *args):
        pass


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    base = f"http://127.0.0.1:{port}"
    errors = []
    results = {}

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width, height, label in [(1280, 800, "desktop"), (390, 844, "mobile")]:
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()
            page.on("pageerror", lambda err: errors.append(f"{label}: {err}"))
            page.on("console", lambda msg: errors.append(f"{label} console.{msg.type}: {msg.text}") if msg.type == "error" else None)
            page.goto(f"{base}/_search-preview.html", wait_until="networkidle")
            page.wait_for_timeout(300)

            for q, slug in [("delta", "delta"), ("usa mexico", "usa-mexico"), ("pug", "pug")]:
                # use hero search
                hero = page.locator('[data-ppc-search="hero"] .ppc-search__input')
                hero.click()
                hero.fill("")
                hero.type(q, delay=20)
                page.wait_for_timeout(350)
                # ensure suggestions open
                page.wait_for_selector('[data-ppc-search="hero"].is-open .ppc-search__item', timeout=5000)
                shot = OUT / f"{label}-{slug}.png"
                page.screenshot(path=str(shot), full_page=False)
                results[f"{label}:{slug}"] = str(shot.relative_to(ROOT))

            if label == "mobile":
                # open burger menu
                page.locator("[data-ppc-burger]").click()
                page.wait_for_timeout(200)
                page.screenshot(path=str(OUT / "mobile-menu-open.png"), full_page=False)
                results["mobile:menu"] = "qa/search/mobile-menu-open.png"
                # Esc closes
                page.keyboard.press("Escape")
                page.wait_for_timeout(150)

            context.close()
        browser.close()

    server.shutdown()
    report = {"errors": errors, "shots": results, "error_count": len(errors)}
    (OUT / "qa-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
