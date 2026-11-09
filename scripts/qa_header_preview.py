#!/usr/bin/env python3
from __future__ import annotations
import json, threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUT = ROOT / "qa" / "search"
OUT.mkdir(parents=True, exist_ok=True)
PAGES = [
    "/_search-preview.html",
    "/airlines/delta.html",
    "/routes/usa-mexico.html",
    "/hotels/pet-friendly-hotels-boston.html",
]
HUBS = ["/routes/", "/airlines/", "/countries/usa-map.html", "/hotels/", "/passport/"]

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(SITE), **k)
    def log_message(self, *a):
        pass

def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"
    errors = []
    missing = []
    shots = {}
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # link check hubs
        ctx = browser.new_context()
        page = ctx.new_page()
        for hub in HUBS:
            resp = page.goto(base + hub, wait_until="domcontentloaded")
            if not resp or resp.status >= 400:
                missing.append(f"{hub} -> {resp.status if resp else 'none'}")
        ctx.close()

        for width, height, label in [(1280, 800, "desktop"), (390, 844, "mobile")]:
            context = browser.new_context(viewport={"width": width, "height": height})
            page = context.new_page()
            page.on("pageerror", lambda e: errors.append(f"{label}:{e}"))
            page.on("console", lambda m: errors.append(f"{label} console.{m.type}:{m.text}") if m.type == "error" else None)
            # demo
            page.goto(base + "/_search-preview.html", wait_until="networkidle")
            page.wait_for_timeout(200)
            if label == "desktop":
                page.screenshot(path=str(OUT / "header-desktop-demo.png"), full_page=False)
                shots["header-desktop-demo"] = "qa/search/header-desktop-demo.png"
            else:
                page.locator("[data-ppc-burger]").click()
                page.wait_for_selector("[data-ppc-drawer].is-open", timeout=3000)
                page.wait_for_timeout(150)
                page.screenshot(path=str(OUT / "header-mobile-menu-demo.png"), full_page=False)
                shots["header-mobile-menu-demo"] = "qa/search/header-mobile-menu-demo.png"
                page.keyboard.press("Escape")
            # real page sample
            page.goto(base + "/airlines/delta.html", wait_until="networkidle")
            page.wait_for_timeout(250)
            if label == "desktop":
                page.screenshot(path=str(OUT / "header-desktop-delta.png"), full_page=False)
                shots["header-desktop-delta"] = "qa/search/header-desktop-delta.png"
            else:
                page.locator("[data-ppc-burger]").click()
                page.wait_for_selector("[data-ppc-drawer].is-open", timeout=3000)
                page.screenshot(path=str(OUT / "header-mobile-menu-delta.png"), full_page=False)
                shots["header-mobile-menu-delta"] = "qa/search/header-mobile-menu-delta.png"
            context.close()
        browser.close()
    server.shutdown()
    report = {"errors": errors, "missing_hubs": missing, "shots": shots,
              "error_count": len(errors), "missing_count": len(missing)}
    (OUT / "header-qa-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if errors or missing:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
