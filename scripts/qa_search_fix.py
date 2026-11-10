#!/usr/bin/env python3
"""Playwright QA for the search-fix preview: before (live main :8811) and after (:8810)."""
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

ROOT = Path("/workspace/search-fix-preview-20261110")
OUT = ROOT / "qa" / "search"
BEFORE = "http://127.0.0.1:8811"
AFTER = "http://127.0.0.1:8810"
# Homepage has no search widget; use a country page with the compact header.
PAGE = "/countries/usa.html"
IGNORE = (
    "googlesyndication", "adsbygoogle", "adsense", "doubleclick", "pagead2",
    "emerald", "googletagmanager", "google-analytics", "googleadservices",
    "fundingchoicesmessages", "ep1.adtrafficquality",
)
BLOCK = [
    "googlesyndication.com", "doubleclick.net", "pagead2.googlesyndication.com",
    "emerald.com", "googletagmanager.com", "google-analytics.com",
    "fundingchoicesmessages.google.com", "adtrafficquality.google",
]
QUERIES = ["Paris", "London", "Berlin", "Tokyo", "Seoul", "New York"]
SHOTS = [("Paris", "paris"), ("New York", "newyork"), ("Tokyo", "tokyo")]


def should_ignore(text: str) -> bool:
    t = (text or "").lower()
    return any(x in t for x in IGNORE)


def open_search(page, width: int):
    if width <= 500:
        page.locator("[data-ppc-burger], .ppc-burger").first.click()
        page.wait_for_timeout(300)
        box = page.locator(".ppc-drawer .ppc-search__input")
    else:
        box = page.locator(".ppc-topbar .ppc-search__input")
    box.first.wait_for(state="visible", timeout=15000)
    return box.first


def run_query(page, width: int, query: str):
    box = open_search(page, width)
    box.click()
    box.fill("")
    box.type(query, delay=30)
    # Wait for suggestions or the empty state
    page.wait_for_timeout(200)
    page.wait_for_function(
        """() => {
          const items = document.querySelectorAll('.ppc-search__item');
          const status = document.querySelector('.ppc-search__status');
          return items.length > 0 || (status && status.textContent && status.textContent.length > 0);
        }""",
        timeout=8000,
    )
    page.wait_for_timeout(200)
    items = []
    for el in page.locator(".ppc-search__item").all():
        if not el.is_visible():
            continue
        title = (el.locator(".ppc-search__title").inner_text() or "").strip()
        typ = (el.locator(".ppc-search__meta").inner_text() or "").strip()
        href = el.get_attribute("href") or ""
        items.append({"title": title, "type": typ, "href": href})
    return items


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"console_errors": {"before": [], "after": []}, "link_404s": [], "shots": []}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        def route_handler(route):
            url = route.request.url
            if any(b in url for b in BLOCK):
                return route.abort()
            return route.continue_()

        context.route("**/*", route_handler)

        for label, base in (("before", BEFORE), ("after", AFTER)):
            page = context.new_page()
            errors = []

            def on_console(msg):
                if msg.type != "error":
                    return
                if should_ignore(msg.text):
                    return
                errors.append(msg.text)

            def on_page_error(exc):
                if should_ignore(str(exc)):
                    return
                errors.append(str(exc))

            page.on("console", on_console)
            page.on("pageerror", on_page_error)

            for width, tag in ((1280, "1280"), (390, "390")):
                page.set_viewport_size({"width": width, "height": 900 if width >= 1000 else 844})
                page.goto(base + PAGE, wait_until="domcontentloaded", timeout=30000)
                # At 390 the header search is display:none until the drawer opens.
                page.wait_for_selector("[data-ppc-search], .ppc-search", state="attached", timeout=15000)
                page.wait_for_timeout(400)

                for query, slug in SHOTS:
                    # Reload a clean page per shot so the drawer/header starts closed
                    page.goto(base + PAGE, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(400)
                    items = run_query(page, width, query)
                    name = f"{slug}-{label}-{tag}.png"
                    path = OUT / name
                    page.screenshot(path=str(path), full_page=False)
                    report["shots"].append({"file": str(path), "query": query, "phase": label, "width": width, "items": items})
                    print(f"{name}: {len(items)} items")
                    for it in items[:6]:
                        print(f"   [{it['type']}] {it['title']}  {it['href']}")

                # After-only: type every test query at 1280 and check result links
                if label == "after" and width == 1280:
                    for query in QUERIES:
                        page.goto(base + PAGE, wait_until="domcontentloaded", timeout=30000)
                        page.wait_for_timeout(300)
                        items = run_query(page, width, query)
                        for it in items:
                            href = it["href"]
                            if not href or href.startswith("http") and "127.0.0.1" not in href and "petpolicycheck" not in href:
                                # external — skip
                                if href.startswith("http"):
                                    continue
                            url = urljoin(base + PAGE, href)
                            # only check internal preview links
                            if not url.startswith(AFTER):
                                continue
                            resp = page.request.get(url, timeout=15000)
                            if resp.status == 404:
                                report["link_404s"].append({"query": query, "href": href, "status": resp.status})
                                print("404", query, href)

            report["console_errors"][label] = errors
            page.close()

        browser.close()

    report_path = OUT / "qa-report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("console errors before:", len(report["console_errors"]["before"]))
    for e in report["console_errors"]["before"][:8]:
        print("  BEFORE:", e[:200])
    print("console errors after:", len(report["console_errors"]["after"]))
    for e in report["console_errors"]["after"][:8]:
        print("  AFTER:", e[:200])
    print("internal 404s:", len(report["link_404s"]))
    print("wrote", report_path)
    return 0 if not report["link_404s"] and not report["console_errors"]["after"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
